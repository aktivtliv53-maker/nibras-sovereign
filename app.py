import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import re
import os
import random

# =========================================================
# 0) محرك المسارات السيادي (core_paths)
# =========================================================
try:
    from core_paths import load_json
except ImportError:
    st.error("❌ ملف core_paths.py مفقود!")
    st.stop()

# =========================================================
# 1) إعداد الواجهة v13.0 الإمبراطورية
# =========================================================
st.set_page_config(page_title="Nibras v13.0 Quad-Sovereign", page_icon="🏛️", layout="wide")

SEMANTIC_FIELDS = {
    "امن": "الإيمان", "صدق": "الإيمان", "كفر": "الضلال", "فسد": "الفساد",
    "صلح": "الإصلاح", "هدى": "الهداية", "ضل": "الضلال", "رحم": "الرحمة",
    "غفر": "الرحمة", "قتل": "الصراع", "قاتل": "الصراع", "نصر": "القوة",
    "ملك": "القوة", "نور": "النور", "ظلم": "الظلام", "عدل": "العدل",
    "عمل": "العمل", "قول": "البيان", "ذكر": "الذكر", "بشر": "البشارة",
    "نذر": "التحذير", "يسر": "اليسر", "عسر": "الشدة"
}

st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background-color: #0a0a0a; color: #e0e0e0; }
    .comparison-card { background: #161616; padding: 15px; border-radius: 15px; border: 1px solid #262626; margin-bottom: 10px; text-align: center; }
    .coherence-box { background:#001f24; padding:10px; border-radius:10px; border-left:4px solid #00afcc; margin-bottom:10px; font-size: 0.9em; }
    h1, h2, h3, h4 { color: #4CAF50 !important; text-align: center; margin-bottom: 5px; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 2) محركات التحليل (تطبيع، جذور، مدارات)
# =========================================================
try:
    letters_raw = load_json("sovereign_letters_v1.json")
    roots_data = load_json("quran_roots_complete.json")
except Exception as e:
    st.error(f"⚠️ فشل الرصد: {e}"); st.stop()

def normalize_arabic(text):
    if not text: return ""
    text = re.sub(r'[\u0617-\u061A\u064B-\u0652\u0670]', '', text)
    replacements = {"أ": "ا", "إ": "ا", "آ": "ا", "ة": "ه", "ى": "ي", "ؤ": "و", "ئ": "ي"}
    for k, v in replacements.items(): text = text.replace(k, v)
    return re.sub(r'\s+', ' ', re.sub(r'[^\u0621-\u064A\s]', ' ', text)).strip()

letters_idx = {normalize_arabic(i.get("letter", "")): i for i in letters_raw if i.get("letter")} if isinstance(letters_raw, list) else {}
quranic_root_index = {normalize_arabic(r["root"]): {"root": normalize_arabic(r["root"]), "weight": float(r.get("frequency", 1)), "orbit": r.get("orbit_hint", "مدار مجهول")} for r in roots_data.get("roots", [])} if roots_data else {}

def match_quranic_root(word, root_index):
    word = normalize_arabic(word)
    prefixes = ["وال", "فال", "بال", "ال", "و", "ف", "ب"]
    candidates = {word}
    for p in prefixes: 
        if word.startswith(p) and len(word)-len(p)>=2: candidates.add(word[len(p):])
    for c in list(candidates):
        if c in root_index: return c, root_index[c]
        if len(c)>=3 and c[:3] in root_index: return c[:3], root_index[c[:3]]
    return None, None

def analyze_path(text, l_idx, r_idx):
    norm = normalize_arabic(text)
    res = {"mass": 0.0, "speed": 0.0, "energy": 0.0, "orbit": "غير_مرصود", "matched_roots": [], "orbit_counter": Counter()}
    for char in norm.replace(" ", ""):
        m = l_idx.get(char); 
        if m: res["mass"] += float(m.get("mass", 0)); res["speed"] += float(m.get("speed", 0))
    for word in norm.split():
        m_root, entry = match_quranic_root(word, r_idx)
        if m_root:
            res["energy"] += entry["weight"]; res["orbit_counter"][entry["orbit"]] += entry["weight"]
            res["matched_roots"].append({"word": word, "root": m_root, "orbit": entry["orbit"], "weight": entry["weight"]})
    if res["orbit_counter"]: res["orbit"] = res["orbit_counter"].most_common(1)[0][0]
    res["total"] = round(res["mass"] + res["speed"] + res["energy"], 2)
    return res

# =========================================================
# 3) محركات العرض والرسوم (الطبقات المدمجة)
# =========================================================
def build_root_network(sentence_results):
    nodes, edges = {}, Counter()
    for item in sentence_results:
        roots_info = item["analysis"]["matched_roots"]
        roots = [r["root"] for r in roots_info]
        for r in roots_info:
            if r["root"] not in nodes: nodes[r["root"]] = {"orbit": r["orbit"], "energy": r["weight"]}
        for i in range(len(roots)):
            for j in range(i + 1, len(roots)):
                edges[tuple(sorted([roots[i], roots[j]]))] += 1
    return nodes, edges

def render_root_network(nodes, edges, title):
    if not nodes or not edges:
        st.info(f"ℹ️ {title}: لا توجد علاقات كافية للشبكة."); return
    st.markdown(f"#### 🕸️ شبكة الجذور")
    pos = {r: (random.uniform(0, 1), random.uniform(0, 1)) for r in nodes}
    edge_x, edge_y = [], []
    for (a, b) in edges:
        x0, y0 = pos[a]; x1, y1 = pos[b]
        edge_x += [x0, x1, None]; edge_y += [y0, y1, None]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=edge_x, y=edge_y, mode='lines', line=dict(width=1, color='#444'), hoverinfo='none'))
    fig.add_trace(go.Scatter(x=[pos[r][0] for r in nodes], y=[pos[r][1] for r in nodes], mode='markers+text', text=list(nodes.keys()),
                             marker=dict(size=[20+(nodes[r]['energy']/15) for r in nodes], color=[nodes[r]['energy'] for r in nodes], colorscale='Viridis'),
                             textposition="top center"))
    fig.update_layout(showlegend=False, height=300, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                      xaxis=dict(showgrid=False, zeroline=False, showticklabels=False), yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
    st.plotly_chart(fig, use_container_width=True)

def analyze_coherence(sentence_results):
    if not sentence_results: return {}
    orbits = [s["analysis"]["orbit"] for s in sentence_results if s["analysis"]["orbit"] != "غير_مرصود"]
    if not orbits: return {"ratio": 0, "dominant_orbit": "غير_مرصود"}
    dom = Counter(orbits).most_common(1)[0][0]
    coherent = [s for s in sentence_results if s["analysis"]["orbit"] == dom]
    return {"dominant_orbit": dom, "ratio": len(coherent)/len(sentence_results), "coherent": coherent}

def analyze_semantics(sentence_results):
    fields, detailed = [], []
    for s in sentence_results:
        roots = s["analysis"]["matched_roots"]
        f = Counter([SEMANTIC_FIELDS.get(r["root"], "بناء") for r in roots]).most_common(1)[0][0] if roots else "صمت"
        fields.append(f); detailed.append({"sentence": s["sentence"], "field": f})
    return {"dominant_field": Counter(fields).most_common(1)[0][0] if fields else "غير مصنف", "detailed": detailed}

def render_semantic_map(sem, title):
    if not sem: return
    st.markdown(f"#### 🧠 خريطة المعنى")
    df = pd.DataFrame(sem["detailed"])
    fig = px.scatter(df, x=df.index + 1, y="field", color="field", hover_data=["sentence"], height=300)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown(f"<div class='coherence-box'><b>🧠 المجال المهيمن:</b> {sem['dominant_field']}</div>", unsafe_allow_html=True)

def render_cross_path_coherence(results):
    valid = [r for r in results if r]
    if len(valid) < 2: return
    st.markdown("---")
    st.subheader("🌐 الانسجام الكوني بين المسارات")
    df = pd.DataFrame([{"path": f"مسار {i+1}", "orbit": r["orbit"], "energy": r["energy"]} for i, r in enumerate(results) if r])
    st.plotly_chart(px.scatter(df, x="path", y="orbit", size="energy", color="orbit", title="خريطة الانسجام البيني"), use_container_width=True)

# =========================================================
# 4) واجهة التشغيل الرئيسية v13.0
# =========================================================
st.title("🛰️ محراب نبراس v13.0 Quad-Sovereign")
c1, c2, c3 = st.columns(3)
inputs = [c1.text_area("📍 المسار 1", key="v1"), c2.text_area("📍 المسار 2", key="v2"), c3.text_area("📍 المسار 3", key="v3")]

if st.button("🚀 إطلاق الرصد الإمبراطوري v13.0", use_container_width=True):
    results = [analyze_path(t, letters_idx, quranic_root_index) if t.strip() else None for t in inputs]
    all_s_results = []

    if any(results):
        score_cols = st.columns(3)
        for i, r in enumerate(results):
            if r:
                with score_cols[i]: st.markdown(f"<div class='comparison-card'><h3>مسار {i+1}</h3><h1>{r['total']}</h1><p>{r['orbit']}</p></div>", unsafe_allow_html=True)
                with st.expander(f"✨ المحراب الهندسي للمسار {i+1}", expanded=True):
                    sentences = [s.strip() for s in re.sub(r"[\.!\?؛،]", ".", inputs[i]).split(".") if s.strip()]
                    s_results = [{"sentence": s, "analysis": analyze_path(s, letters_idx, quranic_root_index)} for s in sentences]
                    all_s_results.append(s_results)

                    col_net, col_heat, col_coh, col_sem = st.columns([1.2, 1.2, 1, 1.2])
                    # العمود 1: الشبكة
                    with col_net:
                        nodes, edges = build_root_network(s_results)
                        render_root_network(nodes, edges, f"المسار {i+1}")
                    # العمود 2: الحرارة
                    with col_heat:
                        if nodes:
                            df_energy = pd.DataFrame([{"جذر": r, "طاقة": d["energy"], "مدار": d["orbit"]} for r, d in nodes.items()])
                            st.markdown("#### 🔥 الخريطة الحرارية")
                            st.plotly_chart(px.density_heatmap(df_energy, x="جذر", y="مدار", z="طاقة", color_continuous_scale="Inferno", height=300), use_container_width=True)
                    # العمود 3: الانسجام والزمن
                    with col_coh:
                        coh = analyze_coherence(s_results)
                        st.markdown(f"<div class='coherence-box'>🔹 انسجام المدار: {round(coh.get('ratio',0)*100, 2)}%</div>", unsafe_allow_html=True)
                        st.markdown("#### ⏳ الانحراف الزمني")
                        df_drift = pd.DataFrame([{"index": k+1, "orbit": s["analysis"]["orbit"]} for k, s in enumerate(s_results)])
                        st.plotly_chart(px.line(df_drift, x="index", y="orbit", markers=True, height=250), use_container_width=True)
                    # العمود 4: المعنى
                    with col_sem:
                        sem = analyze_semantics(s_results)
                        render_semantic_map(sem, f"المسار {i+1}")
            else: all_s_results.append(None)

        # الطبقات الكونية الختامية
        render_cross_path_coherence(results)
        
        # تحليل المجال الدلالي الكوني
        all_semantic_fields = []
        for s_res in all_s_results:
            if s_res:
                sem_data = analyze_semantics(s_res)
                all_semantic_fields.append(sem_data["dominant_field"])
        
        if all_semantic_fields:
            st.markdown("### 🧠 المجال الدلالي الكوني")
            df_sem_global = pd.DataFrame({"مسار": [f"مسار {idx+1}" for idx in range(len(results)) if results[idx]], "مجال": all_semantic_fields})
            st.plotly_chart(px.bar(df_sem_global, x="مسار", y="مجال", color="مجال", title="توزيع المجالات الدلالية الكبرى"), use_container_width=True)

st.sidebar.write("v13.0 Quad-Sovereign | خِت فِت.")
