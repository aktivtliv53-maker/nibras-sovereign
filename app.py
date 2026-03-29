import streamlit as st
import json
import re
from pathlib import Path
from collections import Counter, defaultdict

# =========================================================
# 1) إعداد الصفحة
# =========================================================
st.set_page_config(
    page_title="Nibras Sovereign Quranic v8.1 FINAL",
    page_icon="🛰️",
    layout="wide"
)

st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background-color: #0a0a0a; color: #e0e0e0; }
    .stProgress > div > div > div > div { background-image: linear-gradient(to right, #2e7d32, #aed581); }
    .comparison-card { 
        background: #161616; padding: 15px; border-radius: 15px; 
        border: 1px solid #262626; margin-bottom: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .mentor-box { 
        background: #001f24; border-right: 5px solid #00afcc; 
        padding: 20px; border-radius: 12px; margin-top: 20px;
    }
    .detail-box {
        background: #111; padding: 12px; border-radius: 10px; margin-bottom: 8px; border: 1px solid #222;
    }
    .status-ok {
        background: #0f2a12; border: 1px solid #2e7d32; padding: 10px; border-radius: 10px; margin: 8px 0;
    }
    .status-warn {
        background: #2a1f0f; border: 1px solid #a67c00; padding: 10px; border-radius: 10px; margin: 8px 0;
    }
    h1, h2, h3 { color: #4CAF50 !important; text-align: center; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 2) تحميل الملفات (نسخة "صياد الملفات" الذكية)
# =========================================================
def safe_load_json(filename):
    # مسارات البحث الشاملة لضمان الرصد
    search_paths = [
        Path("."),
        Path("data"),
        Path("qroot"),
        Path("nibras mobail"),
        Path(__file__).parent
    ]
    for folder in search_paths:
        file_path = folder / filename
        if file_path.exists():
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    return json.load(f), str(file_path)
            except Exception as e:
                st.error(f"خطأ في قراءة {filename}: {e}")
    return None, None

# تحميل البيانات السيادية
letters_raw, path_l = safe_load_json("sovereign_letters_v1.json")
lexicon_raw, path_x = safe_load_json("nibras_lexicon.json")

# =========================================================
# 3) التطبيع العربي
# =========================================================
def normalize_arabic(text):
    if not text: return ""
    text = re.sub(r'[\u0617-\u061A\u064B-\u0652\u0670]', '', text)
    replacements = {"أ":"ا","إ":"ا","آ":"ا","ة":"ه","ى":"ي","ؤ":"و","ئ":"ي"}
    for k, v in replacements.items(): text = text.replace(k, v)
    text = re.sub(r'[^\u0621-\u064A\s]', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()

# =========================================================
# 4) فلترة الجذور
# =========================================================
MORPH_TAG_PATTERN = re.compile(r'^(?:[123](?:MS|FS|MP|FP|D|P|S)|ACC|GEN|NOM|IMPF|IMPV|PERF|ACT_PCPL|PASS_PCPL|FS|MS|FP|MP|FD|MD|INDEF|DEF|NEG|COND|PRON|REL|DEM|PREP|CONJ|PART|VN|N|V|ADJ)$')

def is_valid_arabic_root(root_text):
    if not root_text: return False
    root_text = str(root_text).strip()
    if root_text.startswith("LEM:") or MORPH_TAG_PATTERN.match(root_text): return False
    pure = normalize_arabic(root_text)
    return bool(pure and " " not in pure and 2 <= len(pure) <= 6)

# =========================================================
# 5) بناء الفهارس
# =========================================================
letters_idx = {}
if isinstance(letters_raw, list):
    for item in letters_raw:
        char = item.get("letter")
        if char: letters_idx[normalize_arabic(char)] = item

def clean_lexicon_and_build_index(lexicon_raw):
    root_index = defaultdict(list)
    clean_blocks = []
    if not isinstance(lexicon_raw, list): return {}, []
    
    for block in lexicon_raw:
        orbit = block.get("orbit", "مدار مجهول")
        roots = block.get("roots", [])
        clean_roots = []
        for r in roots:
            raw = r.get("name") or r.get("root") or r.get("lemma") or ""
            if is_valid_arabic_root(raw):
                norm = normalize_arabic(raw)
                weight = float(r.get("weight") or r.get("frequency") or 1)
                insight = r.get("insight") or block.get("insight") or f"مدار {orbit}"
                entry = {"orbit": orbit, "weight": weight, "insight": insight}
                root_index[norm].append(entry)
                clean_roots.append({"root": norm, "weight": weight, "insight": insight})
        if clean_roots:
            clean_blocks.append({"orbit": orbit, "roots": clean_roots})
    return dict(root_index), clean_blocks

quranic_root_index, clean_lexicon = clean_lexicon_and_build_index(lexicon_raw)

# =========================================================
# 6) التجريد الصرفي
# =========================================================
PREFIXES = ["وال", "فال", "بال", "كال", "لل", "ال", "و", "ف", "ب", "ك", "ل", "س"]
SUFFIXES = ["هما", "كما", "كم", "كن", "هم", "هن", "نا", "ها", "ه", "ات", "ان", "ون", "ين", "يه", "ية", "ي", "ة", "ا"]

def generate_root_candidates(word):
    word = normalize_arabic(word)
    if not word: return []
    cands = {word}
    for p in PREFIXES:
        if word.startswith(p) and len(word)-len(p)>=2: cands.add(word[len(p):])
    for s in SUFFIXES:
        temp = list(cands)
        for c in temp:
            if c.endswith(s) and len(c)-len(s)>=2: cands.add(c[:-len(s)])
    final = []
    for c in cands:
        final.append(c)
        if len(c) >= 3: final.append(c[:3])
    return sorted(list(set(final)), key=lambda x: (-len(x), x))

def analyze_path(text, l_idx, root_idx):
    norm = normalize_arabic(text)
    res = {"mass":0.0, "speed":0.0, "energy":0.0, "orbit":"غير_مرصود", "insight":"لا توجد بصيرة.", "direction":"غير محدد", "count":0, "matched_roots":[], "orbit_counter":Counter()}
    clean_text = norm.replace(" ", "")
    dir_counter = Counter()
    for char in clean_text:
        meta = l_idx.get(char)
        if meta:
            res["mass"] += float(meta.get("mass", 0))
            res["speed"] += float(meta.get("speed", 0))
            res["count"] += 1
            dir_counter[meta.get("direction", "unknown")] += 1
    if dir_counter: res["direction"] = dir_counter.most_common(1)[0][0]
    
    for word in norm.split():
        cands = generate_root_candidates(word)
        for c in cands:
            if c in root_idx:
                best = max(root_idx[c], key=lambda x: x["weight"])
                res["energy"] += best["weight"]
                res["orbit_counter"][best["orbit"]] += best["weight"]
                res["matched_roots"].append({"word":word, "root":c, "orbit":best["orbit"], "weight":best["weight"], "insight":best["insight"]})
                break
    if res["orbit_counter"]:
        res["orbit"] = res["orbit_counter"].most_common(1)[0][0]
        for m in res["matched_roots"]:
            if m["orbit"] == res["orbit"]: res["insight"] = m["insight"]; break
    res["total"] = round(res["mass"] + res["speed"] + res["energy"], 2)
    return res

# =========================================================
# 7) الواجهة الرئيسية
# =========================================================
st.title("🛰️ محراب نبراس v8.1 FINAL")
with st.sidebar:
    st.header("🛠️ لوحة الرصد")
    if not letters_raw: st.error("❌ ملف الحروف مفقود!")
    if not lexicon_raw: st.error("❌ ملف المعجم مفقود!")
    st.write(f"الجذور المفهرسة: {len(quranic_root_index)}")

col1, col2, col3 = st.columns(3)
with col1: t1 = st.text_area("📍 المسار 1", height=140, key="v1")
with col2: t2 = st.text_area("📍 المسار 2", height=140, key="v2")
with col3: t3 = st.text_area("📍 المسار 3", height=140, key="v3")

if st.button("🚀 إطلاق الرصد", use_container_width=True):
    inputs = [t1, t2, t3]
    display_cols = st.columns(3)
    valid_res = []
    for i, txt in enumerate(inputs):
        if txt.strip():
            res = analyze_path(txt, letters_idx, quranic_root_index)
            valid_res.append(res)
            with display_cols[i]:
                st.markdown(f'<div class="comparison-card"><h3 style="margin:0;">المسار {i+1}</h3><h1 style="color:#8bc34a;">{res["total"]}</h1><p>المدار: {res["orbit"]}</p></div>', unsafe_allow_html=True)
                if res["matched_roots"]:
                    for m in res["matched_roots"][:3]:
                        st.write(f"🔍 {m['word']} -> {m['root']} ({m['orbit']})")
    if valid_res:
        best = max(valid_res, key=lambda x: x["total"])
        st.markdown(f'<div class="mentor-box"><h3>🧠 المستشار السيادي</h3><p>المدار الغالب: <b>{best["orbit"]}</b></p><p>البصيرة: {best["insight"]}</p></div>', unsafe_allow_html=True)

st.sidebar.write("رونبي، السويد | خِت فِت.")
