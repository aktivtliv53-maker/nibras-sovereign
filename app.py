import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import re
import random

# =========================================================
# 0) محرك التحميل والبيانات (Data Core)
# =========================================================
try:
    from core_paths import load_json
except ImportError:
    st.error("❌ ملف core_paths.py مفقود!")
    st.stop()

# =========================================================
# 1) إعداد الواجهة والقاموس الدلالي
# =========================================================
st.set_page_config(page_title="Nibras v14.1 Refined Sovereign", page_icon="🏛️", layout="wide")

SEMANTIC_FIELDS = {
    "امن": "الإيمان", "صدق": "الإيمان", "كفر": "الضلال", "فسد": "الفساد",
    "صلح": "الإصلاح", "هدى": "الهداية", "ضل": "الضلال", "رحم": "الرحمة",
    "غفر": "الرحمة", "قتل": "الصراع", "قاتل": "الصراع", "نصر": "القوة",
    "ملك": "القوة", "نور": "النور", "ظلم": "الظلام", "عدل": "العدل",
    "عمل": "العمل", "قول": "البيان", "ذكر": "الذكر", "بشر": "البشارة",
    "نذر": "التحذير", "يسر": "اليسر", "عسر": "الشدة", "غني": "الغنى", "خلف": "التمكين"
}

st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background-color: #0a0a0a; color: #e0e0e0; }
    .comparison-card { background: #161616; padding: 15px; border-radius: 15px; border: 1px solid #262626; margin-bottom: 10px; text-align: center; }
    .coherence-box { background:#001f24; padding:10px; border-radius:10px; border-left:4px solid #00afcc; margin-bottom:10px; font-size: 0.85em; }
    .tension-alert { background:#420000; padding:10px; border-radius:10px; border-right:4px solid #ff4444; margin-top:5px; font-size: 0.8em; }
    h1, h2, h3, h4 { color: #4CAF50 !important; text-align: center; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 2) محركات التحليل المركزية (The Core Engines)
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

def deep_morpho_extract(word):
    w = normalize_arabic(word)
    w = re.sub(r"^(وال|فال|بال|ال|يست|يت|تست|نست|است|لل|ب|و|ف|ي|ت|ن|ا)", "", w)
    w = re.sub(r"(كم|هم|نا|ها|وا|ون|ين|ات|كما|هما|ه|ي|ت|تم)$", "", w)
    return w if len(w) <= 3 else w[:3]

def match_sovereign_root(word, root_index):
    word_norm = normalize_arabic(word)
    prefixes = ["وال", "فال", "بال", "ال", "و", "ف", "ب", "ل"]
    for p in [""] + prefixes:
        candidate = word_norm[len(p):] if word_norm.startswith(p) else word_norm
        if candidate in root_index: return candidate, root_index[candidate]
        if len(candidate) >= 3 and candidate[:3] in root_index: return candidate[:3], root_index[candidate[:3]]
    est = deep_morpho_extract(word_norm)
    if est in root_index: return est, root_index[est]
    return None, None

def analyze_path_v14_1(text, l_idx, r_idx):
    norm = normalize_arabic(text)
    res = {"mass": 0.0, "speed": 0.0, "energy": 0.0, "orbit": "غير_مرصود", "matched_roots": [], "orbit_counter": Counter()}
    for char in norm.replace(" ", ""):
        m = l_idx.get(char)
        if m: res["mass"] += float(m.get("mass", 0)); res["speed"] += float(m.get("speed", 0))
    for word in norm.split():
        m_root, entry = match_sovereign_root(word, r_idx)
        if m_root:
            res["energy"] += entry["weight"]; res["orbit_counter"][entry["orbit"]] += entry["weight"]
            res["matched_roots"].append({"word": word, "root": m_root, "orbit": entry["orbit"], "weight": entry["weight"]})
    if res["orbit_counter"]: res["orbit"] = res["orbit_counter"].most_common(1)[0][0]
    res["total"] = round(res["mass"] + res["speed"] + res["energy"], 2)
    return res

# =========================================================
# 3) محرك الشبكة الهجين والتوتر (Hybrid Nexus & Tension)
# =========================================================
def build_hybrid_network(s_results):
    nodes = {}
    real_edges = Counter()
    for item in s_results:
        roots_info = item["analysis"]["matched_roots"]
        roots_list = [r["root"] for r in roots_info]
        for r in roots_info:
            if r["root"] not in nodes: nodes[r["root"]] = {"orbit": r["orbit"], "energy": r["weight"]}
        for i in range(len(roots_list)):
            for j in range(i + 1, len(roots_list)):
                real_edges[tuple(sorted([roots_list[i], roots_list[j]]))] += 5
    
    node_list = list(nodes.keys())
    hybrid_edges = real_edges.copy()
    for i in range(len(node_list)):
        for j in range(i + 1, len(node_list)):
            pair = tuple(sorted([node_list[i], node_list[j]]))
            if pair not in hybrid_edges:
                weight = 1.5 if nodes[pair[0]]['orbit'] == nodes[pair[1]]['orbit'] else 0.5
                hybrid_edges[pair] = weight
    return nodes, hybrid_edges

def analyze_semantics_v14(s_res):
    fields, detailed = [], []
    for s in s_res:
        roots = s["analysis"]["matched_roots"]
        f = Counter([SEMANTIC_FIELDS.get(r["root"], "بناء") for r in roots]).most_common(1)[0][0] if roots else "صمت"
        fields.append(f); detailed.append({"sentence": s["sentence"], "field": f})
    return {"dominant_field": Counter(fields).most_common(1)[0][0] if fields else "غير مصنف", "detailed": detailed}

def detect_tension(sem_detailed):
    fields = [d['field'] for d in sem_detailed if d['field'] not in ['صمت', 'بناء']]
    unique_f = set(fields)
    tensions = {tuple(sorted(["الرحمة", "الصراع"])): "⚡ تدافع (الرحمة والقوة)",
                tuple(sorted(["العمل", "الجزاء"])): "🤝 انسجام (تحقق الثمرة)"}
    for f1 in unique_f:
        for f2 in unique_f:
            pair = tuple(sorted([f1, f2]))
            if pair in tensions: return tensions[pair]
    return "✅ تناغم دلالي"

# =========================================================
# 4) واجهة التشغيل v14.1 المستقرة
# =========================================================
st.title("🛰️ محراب نبراس v14.1 Unified Refined")
c1, c2, c3 = st.columns(3)
inputs = [c1.text_area("📍 المسار 1", key="v1"), c2.text_area("📍 المسار 2", key="v2"), c3.text_area("📍 المسار 3", key="v3")]

if st.button("🚀 إطلاق المحرك الإمبراطوري v14.1", use_container_width=True):
    results = [analyze_path_v14_1(t, letters_idx, quranic_root_index) if t.strip() else None for t in inputs]
    
    if any(results):
        score_cols = st.columns(3)
        for i, r in enumerate(results):
            if r:
                with score_cols[i]: st.markdown(f"<div class='comparison-card'><h3>مسار {i+1}</h3><h1>{r['total']}</h1><p>{r['orbit']}</p></div>", unsafe_allow_html=True)
                with st.expander(f"✨ المحراب الرباعي v14.1", expanded=True):
                    sentences = [s.strip() for s in re.sub(r"[\.!\?؛،]", ".", inputs[i]).split(".") if s.strip()]
                    s_results = [{"sentence": s, "analysis": analyze_path_v14_1(s, letters_idx, quranic_root_index)} for s in sentences]
                    
                    col_net, col_heat, col_coh, col_sem = st.columns([1.2, 1, 1, 1.2])
                    nodes, hybrid_edges = build_hybrid_network(s_results)

                    with col_net:
                        st.markdown("#### 🕸️ شبكة العلاقات")
                        if nodes:
                            pos = {root: (random.uniform(0, 1), random.uniform(0, 1)) for root in nodes}
                            edge_x, edge_y = [], []
                            for (a, b), w in hybrid_edges.items():
                                x0, y0 = pos[a]; x1, y1 = pos[b]
                                edge_x += [x0, x1, None]; edge_y += [y0, y1, None]
                            fig = go.Figure()
                            fig.add_trace(go.Scatter(x=edge_x, y=edge_y, mode='lines', line=dict(width=1, color='#333'), hoverinfo='none'))
                            fig.add_trace(go.Scatter(x=[pos[r][0] for r in nodes], y=[pos[r][1] for r in nodes], mode='markers+text', text=list(nodes.keys()),
                                                     marker=dict(size=[20 + (v['energy']/10) for v in nodes.values()], color='#4CAF50'), textposition="top center"))
                            fig.update_layout(showlegend=False, height=250, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(showgrid=False, zeroline=False, showticklabels=False), yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                            st.plotly_chart(fig, use_container_width=True)

                    with col_heat:
                        st.markdown("#### 🌀 طيف الطاقة")
                        if nodes:
                            df_p = pd.DataFrame([{"root": k, "energy": v["energy"], "orbit": v["orbit"]} for k, v in nodes.items()])
                            fig_p = px.bar_polar(df_p, r="energy", theta="root", color="orbit", template="plotly_dark")
                            fig_p.update_layout(height=250, margin=dict(l=0,r=0,t=20,b=0), showlegend=False)
                            st.plotly_chart(fig_p, use_container_width=True)

                    with col_coh:
                        st.markdown("#### ⏳ الانحراف")
                        df_drift = pd.DataFrame([{"index": k+1, "orbit": s["analysis"]["orbit"]} for k, s in enumerate(s_results)])
                        st.plotly_chart(px.line(df_drift, x="index", y="orbit", markers=True, height=250), use_container_width=True)

                    with col_sem:
                        st.markdown("#### 🧠 المعنى")
                        sem = analyze_semantics_v14(s_results)
                        st.markdown(f"<div class='coherence-box'><b>المجال:</b> {sem['dominant_field']}</div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='tension-alert'>{detect_tension(sem['detailed'])}</div>", unsafe_allow_html=True)

st.sidebar.write("v14.1 Unified | خِت فِت.")
