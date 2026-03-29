import streamlit as st
import json
import re
import os
import pandas as pd
import plotly.express as px
from pathlib import Path
from collections import Counter

# =========================================================
# 0) نظام استدعاء العمود الفقري (الضبط السيادي النهائي)
# =========================================================
try:
    from core_paths import load_json, debug_paths
except ImportError:
    def load_json(filename):
        search_paths = [Path("."), Path("./data"), Path("./qroot")]
        for folder in search_paths:
            file_path = folder / filename
            if file_path.exists():
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        return json.load(f)
                except: pass
        return None

    def debug_paths():
        paths = ["⚠️ وضع الطوارئ نشط: رصد الملفات المتاحة:"]
        try:
            for root, dirs, files in os.walk(".", topdown=True):
                for f in files:
                    paths.append(str(Path(root) / f))
        except:
            paths.append("❌ فشل نظام رصد المسارات")
        return paths

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
# 2) تحميل الملفات السيادية
# =========================================================
letters_raw = load_json("sovereign_letters_v1.json")
roots_data = load_json("quran_roots_complete.json")

if letters_raw is None: st.sidebar.error("❌ ملف الحروف مفقود")
if roots_data is None: st.sidebar.error("❌ ملف الجذور مفقود")

# =========================================================
# 3) محرك التطبيع العربي
# =========================================================
def normalize_arabic(text):
    if not text: return ""
    text = re.sub(r'[\u0617-\u061A\u064B-\u0652\u0670]', '', text)
    replacements = {"أ": "ا", "إ": "ا", "آ": "ا", "ة": "ه", "ى": "ي", "ؤ": "و", "ئ": "ي"}
    for k, v in replacements.items(): text = text.replace(k, v)
    text = re.sub(r'[^\u0621-\u064A\s]', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()

# =========================================================
# 4) بناء الفهارس السيادية
# =========================================================
letters_idx = {}
if isinstance(letters_raw, list):
    for item in letters_raw:
        char = item.get("letter")
        if char: letters_idx[normalize_arabic(char)] = item

quranic_root_index = {}
if roots_data and "roots" in roots_data:
    for r in roots_data["roots"]:
        norm_r = normalize_arabic(r["root"])
        quranic_root_index[norm_r] = {
            "root": norm_r,
            "weight": float(r.get("frequency", 1)),
            "orbit": r.get("orbit_hint", "مدار مجهول"),
            "insight": f"بصيرة سيادية: الجذر {norm_r} يتحرك في مدار {r.get('orbit_hint')}"
        }

# =========================================================
# 5) محركات التجريد والتحليل
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
    res = {"mass": 0.0, "speed": 0.0, "energy": 0.0, "orbit": "غير_مرصود", "insight": "لا توجد بصيرة رصدية.", "direction": "غير محدد", "count": 0, "matched_roots": [], "orbit_counter": Counter()}
    clean_text = norm.replace(" ", "")
    dir_counter = Counter()
    for char in clean_text:
        meta = l_idx.get(char)
        if meta:
            res["mass"] += float(meta.get("mass", 0)); res["speed"] += float(meta.get("speed", 0)); res["count"] += 1
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
# 5.1) دوال العرض البصري (المرحلة 2)
# =========================================================
def render_orbit_map(results):
    data = []
    for i, r in enumerate(results, start=1):
        if r: data.append({"path": f"مسار {i}", "orbit": r["orbit"], "energy": r["energy"]})
    if data:
        df = pd.DataFrame(data)
        st.subheader("🌀 خريطة المدار")
        st.plotly_chart(px.sunburst(df, path=["orbit", "path"], values="energy", color="orbit"), use_container_width=True)

def render_energy_wave(results):
    rows = []
    for i, r in enumerate(results, start=1):
        if r:
            rows.append({"path": f"مسار {i}", "metric": "Mass", "value": r["mass"]})
            rows.append({"path": f"مسار {i}", "metric": "Speed", "value": r["speed"]})
            rows.append({"path": f"مسار {i}", "metric": "Energy", "value": r["energy"]})
    if rows:
        st.subheader("📈 موجة الطاقة")
        st.plotly_chart(px.line(pd.DataFrame(rows), x="metric", y="value", color="path", markers=True), use_container_width=True)

def render_radar(results):
    rows = []
    for i, r in enumerate(results, start=1):
        if r: rows.append({"path": f"مسار {i}", "Mass": r["mass"], "Speed": r["speed"], "Energy": r["energy"]})
    if rows:
        st.subheader("🕸️ رادار المسارات")
        st.plotly_chart(px.line_polar(pd.DataFrame(rows).melt(id_vars="path"), r="value", theta="variable", color="path", line_close=True), use_container_width=True)

# =========================================================
# 5.2) دوال الوعي المقارن (المرحلة 3)
# =========================================================
def compare_roots(results):
    root_sets = []
    for r in results:
        root_sets.append(set([m["root"] for m in r["matched_roots"]]) if r else set())
    s1, s2, s3 = root_sets if len(root_sets) == 3 else (set(), set(), set())
    return {
        "common_all": s1 & s2 & s3,
        "common_1_2": (s1 & s2) - s3, "common_1_3": (s1 & s3) - s2, "common_2_3": (s2 & s3) - s1,
        "unique_1": s1 - s2 - s3, "unique_2": s2 - s1 - s3, "unique_3": s3 - s1 - s2
    }

def render_root_comparison(comp):
    st.subheader("🔍 مقارنة الجذور بين المسارات")
    st.markdown("### 🌐 الجذور المشتركة بين المسارات الثلاثة")
    st.success(", ".join(comp["common_all"]) if comp["common_all"] else "لا توجد جذور مشتركة للكل")
    c1, c2, c3 = st.columns(3)
    c1.markdown("### 🔵 مشتركة (1 و 2)"); c1.write(", ".join(comp["common_1_2"]) if comp["common_1_2"] else "—")
    c2.markdown("### 🟢 مشتركة (1 و 3)"); c2.write(", ".join(comp["common_1_3"]) if comp["common_1_3"] else "—")
    c3.markdown("### 🔴 مشتركة (2 و 3)"); c3.write(", ".join(comp["common_2_3"]) if comp["common_2_3"] else "—")
    st.markdown("---")
    u1, u2, u3 = st.columns(3)
    u1.markdown("### 🔷 فريدة لـ 1"); u1.info(", ".join(comp["unique_1"]) if comp["unique_1"] else "—")
    u2.markdown("### 🔶 فريدة لـ 2"); u2.info(", ".join(comp["unique_2"]) if comp["unique_2"] else "—")
    u3.markdown("### 🟣 فريدة لـ 3"); u3.info(", ".join(comp["unique_3"]) if comp["unique_3"] else "—")

def render_venn(comp):
    st.subheader("🟠 مخطط الوعي المقارن (Venn)")
    df = pd.DataFrame([
        {"Group": "الكل", "Count": len(comp["common_all"])},
        {"Group": "1∩2", "Count": len(comp["common_1_2"])}, {"Group": "1∩3", "Count": len(comp["common_1_3"])}, {"Group": "2∩3", "Count": len(comp["common_2_3"])},
        {"Group": "فريدة 1", "Count": len(comp["unique_1"])}, {"Group": "فريدة 2", "Count": len(comp["unique_2"])}, {"Group": "فريدة 3", "Count": len(comp["unique_3"])}
    ])
    st.plotly_chart(px.bar(df, x="Group", y="Count", color="Group"), use_container_width=True)

# =========================================================
# 5.3) محرك تحليل الانحراف (المرحلة 4)
# =========================================================
def analyze_deviation(results):
    deviations = []
    for i, r in enumerate(results, start=1):
        if not r or not r["matched_roots"]:
            deviations.append({"path": f"مسار {i}", "expected": "غير متاح", "actual": r["orbit"] if r else "غير متاح", "deviation": 0, "root_cause": "—", "insight": "لا توجد بيانات كافية."})
            continue
        orbit_weights = r["orbit_counter"]
        expected_orbit = max(orbit_weights, key=orbit_weights.get)
        actual_orbit = r["orbit"]
        deviation = 0 if expected_orbit == actual_orbit else abs(orbit_weights.get(expected_orbit, 0) - orbit_weights.get(actual_orbit, 0))
        root_cause = "—"
        for m in r["matched_roots"]:
            if m["orbit"] == expected_orbit: root_cause = m["root"]; break
        insight = "المسار مستقر ومداره مطابق للتوقع." if deviation == 0 else f"هناك انحراف لأن الجذر {root_cause} يشير إلى مدار {expected_orbit} بينما النتيجة كانت {actual_orbit}."
        deviations.append({"path": f"مسار {i}", "expected": expected_orbit, "actual": actual_orbit, "deviation": round(deviation, 2), "root_cause": root_cause, "insight": insight})
    return deviations

def render_deviation(deviations):
    st.subheader("⚠️ تحليل الانحراف السيادي")
    for d in deviations:
        st.markdown(f"""<div class='deviation-card'><h4>{d['path']}</h4><b>المدار المتوقع:</b> {d['expected']} | <b>المدار الناتج:</b> {d['actual']}<br><b>مقدار الانحراف:</b> {d['deviation']} | <b>الجذر المسؤول:</b> {d['root_cause']}<br><i>{d['insight']}</i></div>""", unsafe_allow_html=True)

# =========================================================
# 5.4) تحليل الجملة (المرحلة 5)
# =========================================================
def split_into_sentences(text):
    if not text: return []
    text = re.sub(r"[\.!\?؛،]", ".", text)
    return [s.strip() for s in text.split(".") if s.strip()]

def analyze_sentences(text, l_idx, root_index):
    sentences = split_into_sentences(text)
    return [{"sentence": s, "analysis": analyze_path(s, l_idx, root_index)} for s in sentences]

def render_sentence_analysis(sentence_results):
    for item in sentence_results:
        s, a = item["sentence"], item["analysis"]
        st.markdown(f"""<div class='sentence-box'><b>الجملة:</b> {s}<br><b>المدار:</b> {a['orbit']} | <b>الطاقة:</b> {a['energy']} | <b>الاتجاه:</b> {a['direction']}<br><i>{a['insight']}</i></div>""", unsafe_allow_html=True)

# =========================================================
# 7) عرض الواجهة السيادية
# =========================================================
st.title("🛰️ محراب نبراس السيادي v9.0 Imperial Edition")

with st.sidebar.expander("🔍 رادار المسارات السيادي", expanded=True):
    for path_info in debug_paths(): st.write(path_info)
    st.write(f"📊 إجمالي الجذور النشطة: {len(quranic_root_index)}")

st.markdown("---")
col1, col2, col3 = st.columns(3)
t1 = col1.text_area("📍 المسار 1", height=140, key="v1")
t2 = col2.text_area("📍 المسار 2", height=140, key="v2")
t3 = col3.text_area("📍 المسار 3", height=140, key="v3")

if st.button("🚀 إطلاق الرصد القرآني المقارن", use_container_width=True):
    inputs = [t1, t2, t3]; results = []; display_cols = st.columns(3)
    for i, txt in enumerate(inputs):
        if txt.strip():
            res = analyze_path(txt, letters_idx, quranic_root_index); results.append(res)
            with display_cols[i]:
                st.markdown(f"<div class='comparison-card'><h3 style='margin:0;'>المسار {i+1}</h3><h1 style='color:#8bc34a; font-size:40px;'>{res['total']}</h1><p style='text-align:center;'><b>المدار:</b> {res['orbit']}</p></div>", unsafe_allow_html=True)
                st.progress(min(res["total"] / 1000, 1.0))
                if res["matched_roots"]:
                    for m in res["matched_roots"][:3]: st.markdown(f"<div class='detail-box'><b>جذر:</b> {m['root']} | {m['orbit']}</div>", unsafe_allow_html=True)
        else: results.append(None)
    
    valid_res = [r for r in results if r]
    if valid_res:
        best = max(valid_res, key=lambda x: x["total"])
        st.markdown(f"<div class='mentor-box'><h3>🧠 المستشار السيادي</h3><b>البصيرة:</b> {best['insight']}<br><b>المدار الغالب:</b> {best['orbit']}</div>", unsafe_allow_html=True)
        st.markdown("---")
        render_orbit_map(valid_res); render_energy_wave(valid_res); render_radar(valid_res)
        st.markdown("---")
        comp = compare_roots(valid_res); render_root_comparison(comp); render_venn(comp)
        st.markdown("---")
        render_deviation(analyze_deviation(valid_res))
        st.markdown("---")
        st.subheader("🟣 تحليل الجمل لكل مسار")
        for i, txt in enumerate(inputs, start=1):
            if txt.strip():
                st.markdown(f"### ✨ مسار {i}")
                render_sentence_analysis(analyze_sentences(txt, letters_idx, quranic_root_index))

st.sidebar.markdown("---")
st.sidebar.write("Blekinge, Sweden | Imperial Sovereign v9.0")
st.sidebar.write("خِت فِت.")
