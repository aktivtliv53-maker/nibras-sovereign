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
    from core_paths import load_json, debug_paths
except ImportError:
    st.error("❌ ملف core_paths.py مفقود!")
    st.stop()

# =========================================================
# 1) إعداد الواجهة الإمبراطورية v13.0
# =========================================================
st.set_page_config(page_title="Nibras v13.0 Sovereign Semantic", page_icon="🧠", layout="wide")

# جدول الحقول الدلالية السيادي (نواة المعنى)
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
    .sentence-box { background: #111; padding: 12px; border-radius: 10px; margin-bottom: 10px; border-left: 4px solid #8bc34a; }
    .coherence-box { background:#001f24; padding:15px; border-radius:10px; border-left:4px solid #00afcc; margin-bottom:10px; }
    .semantic-tag { background: #2e7d32; color: white; padding: 2px 8px; border-radius: 5px; font-size: 0.8em; }
    h1, h2, h3 { color: #4CAF50 !important; text-align: center; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 2) محركات التحليل والتطبيع
# =========================================================
try:
    letters_raw = load_json("sovereign_letters_v1.json")
    roots_data = load_json("quran_roots_complete.json")
except Exception as e:
    st.error(f"⚠️ فشل الرصد: {e}")
    st.stop()

def normalize_arabic(text):
    if not text: return ""
    text = re.sub(r'[\u0617-\u061A\u064B-\u0652\u0670]', '', text)
    replacements = {"أ": "ا", "إ": "ا", "آ": "ا", "ة": "ه", "ى": "ي", "ؤ": "و", "ئ": "ي"}
    for k, v in replacements.items(): text = text.replace(k, v)
    return re.sub(r'\s+', ' ', re.sub(r'[^\u0621-\u064A\s]', ' ', text)).strip()

letters_idx = {normalize_arabic(i.get("letter", "")): i for i in letters_raw if i.get("letter")} if isinstance(letters_raw, list) else {}
quranic_root_index = {normalize_arabic(r["root"]): {"root": normalize_arabic(r["root"]), "weight": float(r.get("frequency", 1)), "orbit": r.get("orbit_hint", "مدار مجهول"), "insight": f"الجذر {r['root']} في مدار {r.get('orbit_hint')}"} for r in roots_data.get("roots", [])} if roots_data else {}

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
        m = l_idx.get(char)
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
# 3) محركات المعنى السيادي (v13.0)
# =========================================================
def get_semantic_field(root):
    return SEMANTIC_FIELDS.get(root, "بناء")

def analyze_semantics(sentence_results):
    if not sentence_results: return {}
    fields, detailed = [], []
    for s in sentence_results:
        roots = s["analysis"]["matched_roots"]
        if not roots:
            detailed.append({"sentence": s["sentence"], "field": "صمت"})
            continue
        f = Counter([get_semantic_field(r["root"]) for r in roots]).most_common(1)[0][0]
        fields.append(f); detailed.append({"sentence": s["sentence"], "field": f})
    if not fields: return {}
    return {"dominant_field": Counter(fields).most_common(1)[0][0], "detailed": detailed}

def render_semantic_map(sem, title):
    if not sem: return
    st.markdown(f"#### 🧠 خريطة المعنى السيادي — {title}")
    df = pd.DataFrame(sem["detailed"])
    fig = px.scatter(df, x=df.index + 1, y="field", color="field", hover_data=["sentence"], title=f"توزيع الحقول الدلالية")
    st.plotly_chart(fig, use_container_width=True)
    st.markdown(f"<div class='coherence-box'><b>🧠 المجال المهيمن:</b> {sem['dominant_field']}</div>", unsafe_allow_html=True)

# =========================================================
# 4) محركات الانسجام والشبكة (v12.5 Core)
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

def analyze_coherence(sentence_results):
    if not sentence_results: return {}
    orbits = [s["analysis"]["orbit"] for s in sentence_results if s["analysis"]["orbit"] != "غير_مرصود"]
    if not orbits: return {}
    dom = Counter(orbits).most_common(1)[0][0]
    coherent = [s for s in sentence_results if s["analysis"]["orbit"] == dom]
    return {"dominant_orbit": dom, "coherent": coherent, "ratio": len(coherent)/len(sentence_results)}

# =========================================================
# 5) أدوات العرض البصري
# =========================================================
def render_root_network(nodes, edges, title):
    if not nodes or not edges:
        st.info(f"ℹ️ {title}: لا توجد علاقات كافية لبناء شبكة.")
        return
    st.markdown(f"#### 🕸️ هندسة جذور {title}")
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
    fig.update_layout(showlegend=False, height=400, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                      xaxis=dict(showgrid=False, zeroline=False, showticklabels=False), yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
    st.plotly_chart(fig, use_container_width=True)

# =========================================================
# 6) واجهة التشغيل v13.0
# =========================================================
st.title("🛰️ محراب نبراس v13.0 Sovereign Meaning")
c1, c2, c3 = st.columns(3)
inputs = [c1.text_area("📍 المسار 1", key="v1"), c2.text_area("📍 المسار 2", key="v2"), c3.text_area("📍 المسار 3", key="v3")]

if st.button("🚀 إطلاق الرصد السيادي v13.0", use_container_width=True):
    results = [analyze_path(t, letters_idx, quranic_root_index) if t.strip() else None for t in inputs]
    
    if any(results):
        cols = st.columns(3)
        for i, r in enumerate(results):
            if r:
                with cols[i]: st.markdown(f"<div class='comparison-card'><h3>مسار {i+1}</h3><h1>{r['total']}</h1><p>{r['orbit']}</p></div>", unsafe_allow_html=True)
                with st.expander(f"✨ تحليل المعنى والانسجام للمسار {i+1}", expanded=True):
                    sentences = [s.strip() for s in re.sub(r"[\.!\?؛،]", ".", inputs[i]).split(".") if s.strip()]
                    s_results = [{"sentence": s, "analysis": analyze_path(s, letters_idx, quranic_root_index)} for s in sentences]
                    
                    net_col, sem_col = st.columns([1, 1.2])
                    with net_col:
                        nodes, edges = build_root_network(s_results)
                        render_root_network(nodes, edges, f"المسار {i+1}")
                        coh = analyze_coherence(s_results)
                        if coh: st.markdown(f"<div class='coherence-box'>🔹 انسجام المدار: {round(coh['ratio']*100, 2)}%</div>", unsafe_allow_html=True)
                    with sem_col:
                        sem = analyze_semantics(s_results)
                        render_semantic_map(sem, f"المسار {i+1}")

st.sidebar.write("v13.0 Sovereign | خِت فِت.")
