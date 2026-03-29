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
    st.error("❌ ملف core_paths.py مفقود!"); st.stop()

# =========================================================
# 1) الإعدادات والقاموس الدلالي v16.0
# =========================================================
st.set_page_config(page_title="Nibras v16.0 Absolute Canvas", page_icon="🌌", layout="wide")

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
    .advisor-box { background:#0a1a0a; padding:20px; border-radius:15px; border-left:5px solid #4CAF50; margin-top:20px; border:1px solid #1a331a; }
    .intent-box { background:#111; padding:20px; border-radius:15px; border-left:5px solid #FFD700; margin-bottom:20px; border:1px solid #333; }
    h1, h2, h3, h4 { color: #4CAF50 !important; text-align: center; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 2) المحركات الجوهرية (Core Logic)
# =========================================================

def normalize_arabic(text):
    if not text: return ""
    text = re.sub(r'[\u0617-\u061A\u064B-\u0652\u0670]', '', text)
    replacements = {"أ": "ا", "إ": "ا", "آ": "ا", "ة": "ه", "ى": "ي", "ؤ": "و", "ئ": "ي"}
    for k, v in replacements.items(): text = text.replace(k, v)
    return re.sub(r'\s+', ' ', re.sub(r'[^\u0621-\u064A\s]', ' ', text)).strip()

def match_sovereign_root(word, root_index):
    word_norm = normalize_arabic(word)
    prefixes = ["وال", "فال", "بال", "ال", "و", "ف", "ب", "ل"]
    candidates = {word_norm}
    for p in prefixes:
        if word_norm.startswith(p) and len(word_norm)-len(p)>=2: candidates.add(word_norm[len(p):])
    for c in list(candidates):
        if c in root_index: return c, root_index[c]
        if len(c)>=3 and c[:3] in root_index: return c[:3], root_index[c[:3]]
    return None, None

def analyze_path_v15_1(text, l_idx, r_idx):
    norm = normalize_arabic(text)
    res = {"mass": 0.0, "speed": 0.0, "energy": 0.0, "orbit": "بناء", "matched_roots": [], "orbit_counter": Counter()}
    for char in norm.replace(" ", ""):
        m = l_idx.get(char); 
        if m: res["mass"] += float(m.get("mass", 0)); res["speed"] += float(m.get("speed", 0))
    for word in norm.split():
        m_root, entry = match_sovereign_root(word, r_idx)
        if m_root:
            res["energy"] += entry["weight"]
            res["orbit_counter"][entry["orbit"]] += entry["weight"]
            res["matched_roots"].append({"word": word, "root": m_root, "orbit": entry["orbit"], "weight": entry["weight"]})
    if res["orbit_counter"]: res["orbit"] = res["orbit_counter"].most_common(1)[0][0]
    res["total"] = round(res["mass"] + res["speed"] + res["energy"], 2)
    return res

def build_global_semantic_graph(all_s_results):
    nodes_g, intra_edges, cross_edges = {}, Counter(), Counter()
    for p_idx, s_list in enumerate(all_s_results):
        if not s_list: continue
        for s_res in s_list:
            analysis = s_res["analysis"]
            roots_in_s = [r["root"] for r in analysis["matched_roots"]]
            for r_info in analysis["matched_roots"]:
                r = r_info["root"]
                if r not in nodes_g:
                    nodes_g[r] = {"orbit": r_info["orbit"], "energy": r_info["weight"], "paths": {p_idx+1}, "count": 1}
                else:
                    nodes_g[r]["paths"].add(p_idx+1); nodes_g[r]["count"] += 1
            for i in range(len(roots_in_s)):
                for j in range(i+1, len(roots_in_s)):
                    intra_edges[tuple(sorted([roots_in_s[i], roots_in_s[j]]))] += 2
    return nodes_g, intra_edges, cross_edges

# =========================================================
# 3) الواجهة السيادية (The Unified Layout)
# =========================================================

try:
    l_idx = {normalize_arabic(i["letter"]): i for i in load_json("sovereign_letters_v1.json") if i.get("letter")}
    r_idx = {normalize_arabic(r["root"]): {"root": normalize_arabic(r["root"]), "weight": float(r.get("frequency", 1)), "orbit": r.get("orbit_hint", "بناء")} for r in load_json("quran_roots_complete.json").get("roots", [])}
except: st.error("❌ فشل تحميل القواعد."); st.stop()

st.title("🛰️ محراب نبراس v16.0 Absolute Canvas")

# إنشاء التبويبات أولاً لتكون الحاويات جاهزة
tabs = st.tabs(["🔍 التحليل السيادي", "🌌 اللوحة الكونية الموحّدة"])

with tabs[0]:
    cols_in = st.columns(3)
    inputs = [cols_in[i].text_area(f"📍 المسار {i+1}", key=f"in_{i}", height=150) for i in range(3)]
    
    # الزر داخل التبويب الأول لضمان بقاء الحالة
    run_btn = st.button("🚀 استنطاق الوجود الرقمي", use_container_width=True)

if run_btn:
    all_s_results = []
    for t in inputs:
        if t.strip():
            sentences = [s.strip() for s in re.sub(r"[\.!\?؛،]", ".", t).split(".") if s.strip()]
            all_s_results.append([{"sentence": s, "analysis": analyze_path_v15_1(s, l_idx, r_idx)} for s in sentences])
        else: all_s_results.append(None)

    if any(all_s_results):
        # محركات التحليل
        nodes_g, intra_g, cross_g = build_global_semantic_graph(all_s_results)
        global_sem = {i+1: Counter([SEMANTIC_FIELDS.get(r["root"], "بناء") for s in s_list for r in s["analysis"]["matched_roots"]]).most_common(1)[0][0] if s_list else "صمت" for i, s_list in enumerate(all_s_results)}

        # --- عرض التبويب الأول (التحليل التفصيلي) ---
        with tabs[0]:
            st.divider()
            cols_res = st.columns(3)
            for i, s_res in enumerate(all_s_results):
                if s_res:
                    with cols_res[i]:
                        total_en = sum(s["analysis"]["total"] for s in s_res)
                        st.markdown(f"<div class='comparison-card'><h3>مسار {i+1}</h3><h1>{round(total_en, 1)}</h1></div>", unsafe_allow_html=True)
                        with st.expander(f"✨ المحراب الرباعي {i+1}", expanded=True):
                            st.markdown(f"🧠 المجال: **{global_sem.get(i+1, 'بناء')}**")
                            # الرسم المجهري للمسار
                            roots_p = Counter([r["root"] for s in s_res for r in s["analysis"]["matched_roots"]])
                            if roots_p:
                                fig_p = go.Figure(go.Scatter(x=[random.random() for _ in roots_p], y=[random.random() for _ in roots_p], mode='markers+text', text=list(roots_p.keys()), marker=dict(size=20, color='#4CAF50')))
                                fig_p.update_layout(height=200, showlegend=False, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(visible=False), yaxis=dict(visible=False))
                                st.plotly_chart(fig_p, use_container_width=True)

            # المستشار v15.1
            core_root = max(nodes_g.items(), key=lambda x: x[1]["count"])[0] if nodes_g else "صمت"
            st.markdown(f"<div class='advisor-box'><h3>🧭 المستشار السيادي</h3><p><b>المحور المركزي:</b> {core_root} | <b>التدفق الدلالي:</b> {' ➔ '.join(set(global_sem.values()))}</p></div>", unsafe_allow_html=True)

        # --- عرض التبويب الثاني (اللوحة الكونية v16.0) ---
        with tabs[1]:
            st.markdown(f"<div class='intent-box'><h3>🔮 النية العميقة (Deep Intent)</h3><p>المجال المهيمن عبر الأبعاد: <b>{Counter(global_sem.values()).most_common(1)[0][0]}</b></p></div>", unsafe_allow_html=True)
            
            st.markdown("### 🌌 الخريطة الكونية الهجينة (Hybrid Cosmic Map)")
            if nodes_g:
                fig_g = go.Figure()
                pos_g = {n: (random.random(), random.random()) for n in nodes_g}
                
                # خطوط الربط
                for (a, b), w in {**intra_g, **cross_g}.items():
                    fig_g.add_trace(go.Scatter(x=[pos_g[a][0], pos_g[b][0]], y=[pos_g[a][1], pos_g[b][1]], mode="lines", line=dict(width=w/2, color="#333"), hoverinfo="none"))
                
                # العقد وموجات الطاقة
                gravity_node = max(nodes_g.items(), key=lambda x: x[1]["energy"])[0]
                for n, info in nodes_g.items():
                    fig_g.add_shape(type="circle", xref="x", yref="y", x0=pos_g[n][0]-0.02, y0=pos_g[n][1]-0.02, x1=pos_g[n][0]+0.02, y1=pos_g[n][1]+0.02, line=dict(color="#4CAF50", width=0.5))
                    fig_g.add_trace(go.Scatter(x=[pos_g[n][0]], y=[pos_g[n][1]], mode="markers+text", text=[n], marker=dict(size=25+info["count"]*5, color="#4CAF50" if n != gravity_node else "#FFD700", line=dict(width=2, color="#000")), textposition="top center"))

                fig_g.update_layout(height=650, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(visible=False), yaxis=dict(visible=False), showlegend=False)
                st.plotly_chart(fig_g, use_container_width=True)

st.sidebar.write("v16.0 Sovereign | خِت فِت.")
