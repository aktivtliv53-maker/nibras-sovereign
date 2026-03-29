import streamlit as st
import json
import re
from pathlib import Path
from collections import Counter, defaultdict

# =========================================================
# 1) إعداد الصفحة (الهوية السيادية)
# =========================================================
st.set_page_config(
    page_title="Nibras Sovereign v8.2 FINAL",
    page_icon="🛰️",
    layout="wide"
)

st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background-color: #0a0a0a; color: #e0e0e0; }
    .stProgress > div > div > div > div { background-image: linear-gradient(to right, #2e7d32, #aed581); }
    .comparison-card { 
        background: #161616; padding: 20px; border-radius: 15px; 
        border: 1px solid #262626; margin-bottom: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.5);
        text-align: center;
    }
    .mentor-box { 
        background: #001f24; border-right: 5px solid #00afcc; 
        padding: 25px; border-radius: 12px; margin-top: 25px;
    }
    .root-tag {
        background: #222; border: 1px solid #444; padding: 5px 10px; 
        border-radius: 8px; font-size: 0.9em; margin: 3px; display: inline-block;
    }
    h1, h2, h3 { color: #4CAF50 !important; }
    .stTextArea textarea { background-color: #111; color: #fff; border: 1px solid #333; font-size: 1.1em; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 2) محرك جلب البيانات (صياد المسارات)
# =========================================================
def safe_load_json(filename):
    search_paths = [Path("."), Path("data"), Path("qroot"), Path("nibras mobail"), Path(__file__).parent]
    for folder in search_paths:
        file_path = folder / filename
        if file_path.exists():
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    return json.load(f), str(file_path)
            except: continue
    return None, None

letters_raw, path_l = safe_load_json("sovereign_letters_v1.json")
lexicon_raw, path_x = safe_load_json("nibras_lexicon.json")

# =========================================================
# 3) منطق التطبيع والتجذير
# =========================================================
def normalize_arabic(text):
    if not text: return ""
    text = re.sub(r'[\u0617-\u061A\u064B-\u0652\u0670]', '', text)
    repl = {"أ":"ا","إ":"ا","آ":"ا","ة":"ه","ى":"ي","ؤ":"و","ئ":"ي"}
    for k, v in repl.items(): text = text.replace(k, v)
    return re.sub(r'[^\u0621-\u064A\s]', ' ', text).strip()

def build_indices(lex_raw, let_raw):
    root_idx = defaultdict(list)
    if isinstance(lex_raw, list):
        for block in lex_raw:
            orbit = block.get("orbit", "مدار مجهول")
            for r in block.get("roots", []):
                # البحث في كل الحقول الممكنة للجذر
                name = normalize_arabic(r.get("name") or r.get("root") or r.get("lemma") or "")
                if name:
                    root_idx[name].append({
                        "orbit": orbit, 
                        "weight": float(r.get("weight") or 1),
                        "insight": r.get("insight") or block.get("insight", "بصيرة مدارية")
                    })
    
    let_idx = {}
    if isinstance(let_raw, list):
        for it in let_raw:
            char = normalize_arabic(it.get("letter", ""))
            if char: let_idx[char] = it
    return root_idx, let_idx

root_index, letters_index = build_indices(lexicon_raw, letters_raw)

def analyze_path(text):
    norm = normalize_arabic(text)
    res = {"total":0.0, "mass":0.0, "speed":0.0, "energy":0.0, "orbit":"غير مرصود", "insight":"لا توجد بصيرة رصدية لهذا المسار.", "matched":[]}
    if not norm: return res
    
    # حساب الطاقة الحرفية
    for char in norm.replace(" ",""):
        meta = letters_index.get(char)
        if meta:
            res["mass"] += float(meta.get("mass", 0))
            res["speed"] += float(meta.get("speed", 0))
    
    # حساب الطاقة الجذرية (البحث عن الجذور في الكلمات)
    words = norm.split()
    orbit_counts = Counter()
    for w in words:
        found_root = None
        # تجربة الكلمة كاملة، ثم تجربة أول 3 حروف (تجريد بسيط)
        for cand in [w, w[:3]]:
            if cand in root_index:
                best = max(root_index[cand], key=lambda x: x["weight"])
                res["energy"] += best["weight"]
                orbit_counts[best["orbit"]] += best["weight"]
                res["matched"].append({"word": w, "root": cand, "orbit": best["orbit"], "insight": best["insight"]})
                found_root = True
                break
            
    if orbit_counts:
        res["orbit"], _ = orbit_counts.most_common(1)[0]
        # استخراج البصيرة من أول جذر يطابق المدار الغالب
        for m in res["matched"]:
            if m["orbit"] == res["orbit"]:
                res["insight"] = m["insight"]
                break
                
    res["total"] = round(res["mass"] + res["speed"] + res["energy"], 2)
    return res

# =========================================================
# 4) الواجهة السيادية الكبرى
# =========================================================
st.title("🛰️ محراب نبراس السيادي v8.2")

with st.sidebar:
    st.header("📊 مصفوفة الرصد")
    st.markdown(f"**حالة الحروف:** {'✅ متصل' if letters_raw else '❌ مفقود'}")
    st.markdown(f"**حالة المعجم:** {'✅ متصل' if lexicon_raw else '❌ مفقود'}")
    st.markdown("---")
    st.caption("رونبي، السويد | Nibras Final")

col1, col2, col3 = st.columns(3)
t1 = col1.text_area("📍 المسار الأول", height=150, placeholder="أدخل النص هنا...")
t2 = col2.text_area("📍 المسار الثاني", height=150, placeholder="أدخل النص هنا...")
t3 = col3.text_area("📍 المسار الثالث", height=150, placeholder="أدخل النص هنا...")

if st.button("🚀 إطلاق الرصد القرآني المقارن", use_container_width=True):
    results = []
    display_cols = st.columns(3)
    
    for i, txt in enumerate([t1, t2, t3]):
        if txt.strip():
            ans = analyze_path(txt)
            results.append(ans)
            with display_cols[i]:
                st.markdown(f"""
                <div class="comparison-card">
                    <h3 style="margin:0;">المسار {i+1}</h3>
                    <h1 style="color:#8bc34a; font-size:50px;">{ans['total']}</h1>
                    <p><b>المدار:</b> {ans['orbit']}</p>
                    <hr style="border:0.5px solid #333">
                    <div style="text-align:right;">
                """, unsafe_allow_html=True)
                for m in ans["matched"][:5]:
                    st.markdown(f'<span class="root-tag">{m["word"]} → {m["root"]}</span>', unsafe_allow_html=True)
                st.markdown("</div></div>", unsafe_allow_html=True)
        else:
            results.append(None)

    # المستشار السيادي (البصيرة)
    valid = [r for r in results if r and r["orbit"] != "غير مرصود"]
    if valid:
        best = max(valid, key=lambda x: x["total"])
        st.markdown(f"""
        <div class="mentor-box">
            <h2 style="text-align:right;">🧠 المستشار الشخصي السيادي</h2>
            <p style="font-size:1.2em; text-align:right;">المدار المهيمن هو <b>({best['orbit']})</b>.</p>
            <div style="background:#003138; padding:15px; border-radius:10px; border-right:4px solid #4CAF50;">
                <b>البصيرة الوجودية:</b><br>{best['insight']}
            </div>
            <p style="text-align:left; margin-top:10px; color:#aaa;">إجمالي الطاقة: {best['total']}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("⚠️ الرادار لم يرصد مدارات قرآنية محددة. تأكد من صحة الكلمات أو وجود ملف nibras_lexicon.json")

st.sidebar.markdown("---")
st.sidebar.write("خِت فِت.")
