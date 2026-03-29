import streamlit as st
import pandas as pd
import plotly.express as px
from collections import Counter
import re
import os

# =========================================================
# 0) استدعاء المحرك السيادي للمسارات
# =========================================================
try:
    from core_paths import load_json, debug_paths
except ImportError:
    st.error("❌ ملف core_paths.py مفقود! يرجى رفعه بجانب app.py")
    st.stop()

# =========================================================
# 1) إعداد الصفحة والواجهة السيادية
# =========================================================
st.set_page_config(
    page_title="Nibras Sovereign Quranic v9.0 Imperial",
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
    .deviation-card {
        background:#1a1a1a; padding:15px; border-radius:10px; 
        margin-bottom:10px; border-right:4px solid #00afcc;
    }
    .sentence-box {
        background: #111; padding: 15px; border-radius: 10px; 
        margin-bottom: 10px; border-left: 4px solid #8bc34a;
    }
    h1, h2, h3 { color: #4CAF50 !important; text-align: center; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 2) تحميل الملفات السيادية (عبر المحرك الجديد)
# =========================================================
try:
    letters_raw = load_json("sovereign_letters_v1.json")
    roots_data = load_json("quran_roots_complete.json")
except Exception as e:
    st.error(f"⚠️ عذراً محمد، حدث خطأ في الرصد: {e}")
    with st.expander("🔍 رادار تشخيص المسارات"):
        st.write(debug_paths())
    st.stop()

# =========================================================
# 3) محرك التطبيع وفهارس البيانات
# =========================================================
def normalize_arabic(text):
    if not text: return ""
    text = re.sub(r'[\u0617-\u061A\u064B-\u0652\u0670]', '', text)
    replacements = {"أ": "ا", "إ": "ا", "آ": "ا", "ة": "ه", "ى": "ي", "ؤ": "و", "ئ": "ي"}
    for k, v in replacements.items(): text = text.replace(k, v)
    text = re.sub(r'[^\u0621-\u064A\s]', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()

letters_idx = {}
if isinstance(letters_raw, list):
    for item in letters_raw:
        char = normalize_arabic(item.get("letter", ""))
        if char: letters_idx[char] = item

quranic_root_index = {}
if roots_data and "roots" in roots_data:
    for r in roots_data["roots"]:
        norm_r = normalize_arabic(r["root"])
        quranic_root_index[norm_r] = {
            "root": norm_r,
            "weight": float(r.get("frequency", 1)),
            "orbit": r.get("orbit_hint", "مدار مجهول"),
            "insight": f"بصيرة سيادية: الجذر {norm_r} في مدار {r.get('orbit_hint')}"
        }

# =========================================================
# 4) محركات التجريد والتحليل الأساسية
# =========================================================
PREFIXES = ["وال", "فال", "بال", "كال", "لل", "ال", "و", "ف", "ب", "ك", "ل", "س"]
SUFFIXES = ["هما", "كما", "كم", "كن", "هم", "هن", "نا", "ها", "ه", "ات", "ان", "ون", "ين", "يه", "ية", "ي", "ة", "ا"]

def generate_root_candidates(word):
    word = normalize_arabic(word)
    if not word: return []
    temp_forms = {word}
    for p in PREFIXES:
        if word.startswith(p) and len(word) - len(p) >= 2: temp_forms.add(word[len(p):])
    for form in list(temp_forms):
        for s in SUFFIXES:
            if form.endswith(s) and len(form) - len(s) >= 2: temp_forms.add(form[:-len(s)])
    final_candidates = set()
    for c in temp_forms:
        final_candidates.add(c)
        if len(c) >= 3:
            final_candidates.add(c[:3]); final_candidates.add(c[-3:])
    return sorted(set(final_candidates), key=lambda x: (-len(x), x))

def match_quranic_root(word, root_index):
    for c in generate_root_candidates(word):
        if c in root_index: return c, root_index[c]
    return None, None

def analyze_path(text, l_idx, root_index):
    norm = normalize_arabic(text)
    res = {"mass": 0.0, "speed": 0.0, "energy": 0.0, "orbit": "غير_مرصود", "insight": "لا توجد بصيرة.", "direction": "غير محدد", "matched_roots": [], "orbit_counter": Counter()}
    clean_text = norm.replace(" ", "")
    dir_counter = Counter()
    for char in clean_text:
        meta = l_idx.get(char)
        if meta:
            res["mass"] += float(meta.get("mass", 0)); res["speed"] += float(meta.get("speed", 0))
            dir_counter[meta.get("direction", "unknown")] += 1
    if dir_counter: res["direction"] = dir_counter.most_common(1)[0][0]
    for word in norm.split():
        m_root, entry = match_quranic_root(word, root_index)
        if m_root:
            res["energy"] += entry["weight"]; res["orbit_counter"][entry["orbit"]] += entry["weight"]
            res["matched_roots"].append({"word": word, "root": m_root, "orbit": entry["orbit"], "weight": entry["weight"], "insight": entry["insight"]})
    if res["orbit_counter"]:
        res["orbit"] = res["orbit_counter"].most_common(1)[0][0]
        for m in res["matched_roots"]:
            if m["orbit"] == res["orbit"]: res["insight"] = m["insight"]; break
    res["total"] = round(res["mass"] + res["speed"] + res["energy"], 2)
    return res

# =========================================================
# 5) طبقات العرض البصري (المراحل 2, 3, 4, 5)
# =========================================================

# --- المرحلة 2: الرسوم البيانية ---
def render_visual_layers(results):
    st.markdown("---")
    colA, colB = st.columns(2)
    
    with colA:
        data_orbit = [{"path": f"مسار {i+1}", "orbit": r["orbit"], "energy": r["energy"]} for i, r in enumerate(results) if r]
        if data_orbit:
            st.subheader("🌀 خريطة المدار")
            st.plotly_chart(px.sunburst(pd.DataFrame(data_orbit), path=["orbit", "path"], values="energy", color="orbit"), use_container_width=True)

    with colB:
        rows_wave = []
        for i, r in enumerate(results):
            if r:
                for m in ["mass", "speed", "energy"]: rows_wave.append({"path": f"مسار {i+1}", "metric": m, "value": r[m]})
        if rows_wave:
            st.subheader("📈 موجة الطاقة")
            st.plotly_chart(px.line(pd.DataFrame(rows_wave), x="metric", y="value", color="path", markers=True), use_container_width=True)

    rows_radar = [{"path": f"مسار {i+1}", "Mass": r["mass"], "Speed": r["speed"], "Energy": r["energy"]} for i, r in enumerate(results) if r]
    if rows_radar:
        st.subheader("🕸️ رادار المسارات")
        st.plotly_chart(px.line_polar(pd.DataFrame(rows_radar).melt(id_vars="path"), r="value", theta="variable", color="path", line_close=True), use_container_width=True)

# --- المرحلة 3: المقارنة و Venn ---
def render_comparison_layer(results):
    root_sets = [set([m["root"] for m in r["matched_roots"]]) if r else set() for r in results]
    s1, s2, s3 = root_sets if len(root_sets) == 3 else (set(), set(), set())
    comp = {
        "common_all": s1 & s2 & s3, "common_1_2": (s1 & s2) - s3, "common_1_3": (s1 & s3) - s2, "common_2_3": (s2 & s3) - s1,
        "unique_1": s1 - s2 - s3, "unique_2": s2 - s1 - s3, "unique_3": s3 - s1 - s2
    }
    st.subheader("🔍 الوعي المقارن للجذور")
    st.success(f"🌐 الجذور المشتركة للكل: {', '.join(comp['common_all']) if comp['common_all'] else '—'}")
    c1, c2, c3 = st.columns(3)
    c1.info(f"🔵 مشتركة (1-2): {', '.join(comp['common_1_2']) if comp['common_1_2'] else '—'}")
    c2.info(f"🟢 مشتركة (1-3): {', '.join(comp['common_1_3']) if comp['common_1_3'] else '—'}")
    c3.info(f"🔴 مشتركة (2-3): {', '.join(comp['common_2_3']) if comp['common_2_3'] else '—'}")

# --- المرحلة 4: الانحراف ---
def render_deviation_layer(results):
    st.subheader("⚠️ تحليل الانحراف السيادي")
    for i, r in enumerate(results):
        if not r or not r["matched_roots"]: continue
        exp_orbit = max(r["orbit_counter"], key=r["orbit_counter"].get)
        dev = 0 if exp_orbit == r["orbit"] else abs(r["orbit_counter"][exp_orbit] - r["orbit_counter"][r["orbit"]])
        st.markdown(f"<div class='deviation-card'><h4>مسار {i+1}</h4><b>المتوقع:</b> {exp_orbit} | <b>الناتج:</b> {r['orbit']}<br><b>الانحراف:</b> {round(dev, 2)}</div>", unsafe_allow_html=True)

# --- المرحلة 5: الجمل ---
def render_sentence_layer(inputs, l_idx, r_idx):
    st.subheader("🟣 تفكيك جمل المسارات")
    for i, txt in enumerate(inputs):
        if txt.strip():
            st.markdown(f"### ✨ مسار {i+1}")
            sentences = [s.strip() for s in re.sub(r"[\.!\?؛،]", ".", txt).split(".") if s.strip()]
            for s in sentences:
                a = analyze_path(s, l_idx, r_idx)
                st.markdown(f"<div class='sentence-box'><b>{s}</b><br>مدار: {a['orbit']} | طاقة: {a['energy']}</div>", unsafe_allow_html=True)

# =========================================================
# 6) الواجهة التشغيلية النهائية
# =========================================================
st.title("🛰️ محراب نبراس السيادي v9.0 Imperial")

col1, col2, col3 = st.columns(3)
t1 = col1.text_area("📍 المسار 1", height=140, key="v1")
t2 = col2.text_area("📍 المسار 2", height=140, key="v2")
t3 = col3.text_area("📍 المسار 3", height=140, key="v3")

if st.button("🚀 إطلاق الرصد القرآني المقارن", use_container_width=True):
    inputs = [t1, t2, t3]
    results = [analyze_path(t, letters_idx, quranic_root_index) if t.strip() else None for t in inputs]
    
    valid_res = [r for r in results if r]
    if valid_res:
        # عرض بطاقات النتائج العلوية
        display_cols = st.columns(3)
        for i, res in enumerate(results):
            if res:
                with display_cols[i]:
                    st.markdown(f"<div class='comparison-card'><h3>مسار {i+1}</h3><h1>{res['total']}</h1><p>المدار: {res['orbit']}</p></div>", unsafe_allow_True=True)
        
        # المستشار
        best = max(valid_res, key=lambda x: x["total"])
        st.markdown(f"<div class='mentor-box'><h3>🧠 المستشار السيادي</h3>{best['insight']}</div>", unsafe_allow_html=True)
        
        # استدعاء الطبقات المتتالية
        render_visual_layers(results)
        render_comparison_layer(results)
        render_deviation_layer(results)
        st.markdown("---")
        render_sentence_layer(inputs, letters_idx, quranic_root_index)

st.sidebar.write("Blekinge, Sweden | Imperial Sovereign v9.0")
st.sidebar.write("خِت فِت.")
