import streamlit as st
import json
import re
from pathlib import Path
from collections import Counter, defaultdict

# =========================================================
# 1) إعداد الصفحة
# =========================================================
st.set_page_config(
    page_title="Nibras Sovereign Quranic v8.0 FINAL",
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
# 2) تحميل الملفات السيادية (المعدل للربط بالجذور الصافية)
# =========================================================
def safe_load_json(filename):
    search_paths = [Path("."), Path("./qroot"), Path("./nibras mobail"), Path("./data")]
    for folder in search_paths:
        file_path = folder / filename
        if file_path.exists():
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    return json.load(f), str(file_path)
            except Exception as e:
                st.error(f"خطأ في قراءة {filename}: {e}")
    return None, None

letters_raw, path_l = safe_load_json("sovereign_letters_v1.json")
# الربط بملف الجذور القرآنية الصافية الذي أرسلته يا محمد
roots_data, path_x = safe_load_json("quran_roots_complete.json")

# =========================================================
# 3) التطبيع العربي
# =========================================================
def normalize_arabic(text):
    if not text: return ""
    text = re.sub(r'[\u0617-\u061A\u064B-\u0652\u0670]', '', text)
    replacements = {"أ": "ا", "إ": "ا", "آ": "ا", "ة": "ه", "ى": "ي", "ؤ": "و", "ئ": "ي"}
    for k, v in replacements.items(): text = text.replace(k, v)
    text = re.sub(r'[^\u0621-\u064A\s]', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()

# =========================================================
# 4) بناء الفهارس (الحروف والجذور)
# =========================================================
letters_idx = {}
if isinstance(letters_raw, list):
    for item in letters_raw:
        char = item.get("letter")
        if char: letters_idx[normalize_arabic(char)] = item

# بناء فهرس الجذور من ملفك الجديد مباشرة
quranic_root_index = {}
if roots_data and "roots" in roots_data:
    for r in roots_data["roots"]:
        norm_r = normalize_arabic(r["root"])
        quranic_root_index[norm_r] = {
            "root": norm_r,
            "weight": float(r.get("frequency", 1)),
            "orbit": r.get("orbit_hint", "مدار مجهول"),
            "insight": f"هذا الجذر ينتمي لمدار {r.get('orbit_hint')}"
        }

# =========================================================
# 5) تجريد صرفي ذكي
# =========================================================
PREFIXES = ["وال", "فال", "بال", "كال", "لل", "ال", "و", "ف", "ب", "ك", "ل", "س"]
SUFFIXES = ["هما", "كما", "كم", "كن", "هم", "هن", "نا", "ها", "ه", "ات", "ان", "ون", "ين", "يه", "ية", "ي", "ة", "ا"]

def generate_root_candidates(word):
    word = normalize_arabic(word)
    if not word: return []
    candidates = {word}
    for p in PREFIXES:
        if word.startswith(p) and len(word)-len(p)>=2: candidates.add(word[len(p):])
    for s in SUFFIXES:
        for c in list(candidates):
            if c.endswith(s) and len(c)-len(s)>=2: candidates.add(c[:-len(s)])
    
    # احتمالات الثلاثي
    tri_forms = {c[:3] for c in candidates if len(c) >= 3}
    candidates.update(tri_forms)
    return sorted(set(candidates), key=lambda x: (-len(x), x))

def match_quranic_root(word, root_index):
    for c in generate_root_candidates(word):
        if c in root_index: return c, root_index[c]
    return None, None

# =========================================================
# 6) التحليل الكامل (المسارات)
# =========================================================
def analyze_path(text, l_idx, root_index):
    norm = normalize_arabic(text)
    res = {
        "mass": 0.0, "speed": 0.0, "energy": 0.0, "orbit": "غير_مرصود",
        "insight": "لا توجد بصيرة رصدية لهذا المسار.", "direction": "غير محدد",
        "count": 0, "matched_roots": [], "orbit_counter": Counter()
    }
    
    # أ) الحروف
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

    # ب) الجذور
    for word in norm.split():
        m_root, entry = match_quranic_root(word, root_index)
        if m_root:
            res["energy"] += entry["weight"]
            res["orbit_counter"][entry["orbit"]] += entry["weight"]
            res["matched_roots"].append({
                "word": word, "root": m_root, "orbit": entry["orbit"],
                "weight": entry["weight"], "insight": entry["insight"]
            })

    if res["orbit_counter"]:
        res["orbit"] = res["orbit_counter"].most_common(1)[0][0]
        for m in res["matched_roots"]:
            if m["orbit"] == res["orbit"]:
                res["insight"] = m["insight"]
                break
    res["total"] = round(res["mass"] + res["speed"] + res["energy"], 2)
    return res

# =========================================================
# 7) الواجهة والعرض (نفس هيكلك تماماً)
# =========================================================
st.title("🛰️ محراب نبراس السيادي القرآني v8.0 FINAL")

with st.sidebar.expander("🛠️ لوحة التشخيص السيادي", expanded=True):
    st.write(f"ملف الحروف: {path_l if path_l else '❌ مفقود'}")
    st.write(f"ملف الجذور: {path_x if path_x else '❌ مفقود'}")
    st.write(f"عدد الجذور القرآنية: {len(quranic_root_index)}")

st.markdown("---")
col1, col2, col3 = st.columns(3)
t1 = col1.text_area("📍 المسار 1", height=140, key="v1")
t2 = col2.text_area("📍 المسار 2", height=140, key="v2")
t3 = col3.text_area("📍 المسار 3", height=140, key="v3")

if st.button("🚀 إطلاق الرصد القرآني المقارن", use_container_width=True):
    inputs = [t1, t2, t3]
    results = []
    display_cols = st.columns(3)

    for i, txt in enumerate(inputs):
        if txt.strip():
            res = analyze_path(txt, letters_idx, quranic_root_index)
            results.append(res)
            with display_cols[i]:
                st.markdown(f"""
                <div class="comparison-card">
                    <h3 style='margin:0;'>المسار {i+1}</h3>
                    <h1 style='color:#8bc34a; font-size:40px;'>{res['total']}</h1>
                    <p style='text-align:center;'><b>المدار:</b> {res['orbit']}</p>
                </div>
                """, unsafe_allow_html=True)
                st.caption("🌀 موجة الطاقة الكلية")
                st.progress(min(res["total"] / 1000, 1.0))
                
                if res["matched_roots"]:
                    for m in res["matched_roots"][:3]:
                        st.markdown(f"<div class='detail-box'><b>جذر:</b> {m['root']} | {m['orbit']}</div>", unsafe_allow_html=True)
        else: results.append(None)

    valid_res = [r for r in results if r]
    if valid_res:
        best = max(valid_res, key=lambda x: x["total"])
        st.markdown(f"<div class='mentor-box'><h3>🧠 المستشار السيادي</h3><b>البصيرة:</b> {best['insight']}<br><b>المدار الغالب:</b> {best['orbit']}</div>", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.write("خِت فِت.")
