import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import re
import random

# =========================================================
# 0) محرك التحميل والبيانات (Sovereign Data Core)
# =========================================================
try:
    from core_paths import load_json
except ImportError:
    st.error("❌ ملف core_paths.py مفقود!"); st.stop()

# =========================================================
# 1) القواميس السيادية الشاملة (v15 -> v17)
# =========================================================
st.set_page_config(page_title="Nibras v17.0 Unified", page_icon="🔱", layout="wide")

SEMANTIC_FIELDS = {
    "امن": "الإيمان", "صدق": "الإيمان", "كفر": "الضلال", "فسد": "الفساد",
    "صلح": "الإصلاح", "هدى": "الهداية", "ضل": "الضلال", "رحم": "الرحمة",
    "غفر": "الرحمة", "قتل": "الصراع", "قاتل": "الصراع", "نصر": "القوة",
    "ملك": "القوة", "نور": "النور", "ظلم": "الظلام", "عدل": "العدل",
    "عمل": "العمل", "قول": "البيان", "ذكر": "الذكر", "بشر": "البشارة",
    "نذر": "التحذير", "يسر": "اليسر", "عسر": "الشدة", "خلف": "التمكين"
}

Q_ARCHETYPES = {
    "رحم": "الرحمة", "غفر": "الرحمة", "عدل": "العدل", "نور": "النور",
    "نصر": "القوة", "ملك": "القوة", "هدى": "الهداية", "بشر": "البشارة",
    "نذر": "التحذير", "قتل": "الصراع", "ظلم": "الظلام", "خلف": "التمكين",
    "امن": "اليقين", "صدق": "الصدق", "علم": "العلم", "ذكر": "الذكر"
}

UNIVERSAL_ARCHETYPES = {
    "الرحمة": "The Healer", "العدل": "The Judge", "النور": "The Sage",
    "القوة": "The Warrior", "الهداية": "The Guide", "البشارة": "The Nurturer",
    "التحذير": "The Rebel", "الصراع": "The Destroyer", "الظلام": "The Shadow",
    "التمكين": "The Creator", "اليقين": "The Believer", "الصدق": "The Pure",
    "العلم": "The Scholar", "الذكر": "The Reminder"
}

ARCHE_COLORS = {
    "الرحمة": "#4fc3f7", "القوة": "#ff5252", "الهداية": "#4CAF50", "العدل": "#FFD700",
    "النور": "#bb86fc", "الصراع": "#ff1744", "الظلام": "#212121", "التمكين": "#00e676",
    "اليقين": "#03a9f4", "الصدق": "#ffffff", "العلم": "#ffeb3b", "الذكر": "#00bcd4"
}

HALO_COLORS = {
    "The Healer": "rgba(79,195,247,0.3)", "The Judge": "rgba(255,215,0,0.3)",
    "The Warrior": "rgba(255,82,82,0.3)", "The Guide": "rgba(76,175,80,0.3)",
    "The Sage": "rgba(187,134,252,0.3)", "The Nurturer": "rgba(255,171,64,0.3)",
    "The Rebel": "rgba(255,23,68,0.3)", "The Shadow": "rgba(33,33,33,0.3)",
    "The Creator": "rgba(0,230,118,0.3)", "The Believer": "rgba(3,169,244,0.3)",
    "The Destroyer": "rgba(255,23,68,0.3)"
}

st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background-color: #050505; color: #e0e0e0; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .comparison-card { background: #111; padding: 20px; border-radius: 15px; border: 1px solid #222; text-align: center; }
    .advisor-box { background: linear-gradient(145deg, #0a150a, #020202); padding:25px; border-radius:15px; border-left:5px solid #4CAF50; border:1px solid #1a331a; margin-top:20px; }
    .intent-box { background: #0a0a0a; padding:25px; border-radius:15px; border-left:5px solid #FFD700; border:1px solid #222; margin-bottom:20px; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 2) المحركات الموحدة (Unified Engines)
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
    for p in prefixes:
        if word_norm.startswith(p) and len(word_norm)-len(p)>=2: word_norm = word_norm[len(p):]; break
    if word_norm in root_index: return word_norm, root_index[word_norm]
    if len(word_norm)>=3 and word_norm[:3] in root_index: return word_norm[:3], root_index[word_norm[:3]]
    return None, None

def analyze_path_v17_unified(text, l_idx, r_idx):
    norm = normalize_arabic(text)
    res = {"mass": 0.0, "speed": 0.0, "energy": 0.0, "orbit": "بناء", "matched_roots": [], "orbit_counter": Counter()}
    # طبقة الحروف (v15)
    for char in norm.replace(" ", ""):
        m = l_idx.get(char)
        if m: res["mass"] += float(m.get("mass", 0)); res["speed"] += float(m.get("speed", 0))
    # طبقة الجذور (v16)
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
            roots_in_s = [r["root"] for r in s_res["analysis"]["matched_roots"]]
            for r_info in s_res["analysis"]["matched_roots"]:
                r = r_info["root"]
                if r not in nodes_g:
                    nodes_g[r] = {"orbit": r_info["orbit"], "energy": r_info["weight"], "paths": {p_idx+1}, "count": 1}
                else:
                    nodes_g[r]["paths"].add(p_idx+1); nodes_g[r]["count"] += 1
            for i in range(len(roots_in_s)):
                for j in range(i+1, len(roots_in_s)):
                    intra_edges[tuple(sorted([roots_in_s[i], roots_in_s[j]]))] += 2
    # العلاقات العابرة (v16.5)
    r_list = list(nodes_g.keys())
    for i in range(len(r_list)):
        for j in range(i+1, len(r_list)):
            if nodes_g[r_list[i]]["orbit"] == nodes_g[r_list[j]]["orbit"]:
                cross_edges[tuple(sorted([r_list[i], r_list[j]]))] += 1.5
    return nodes_g, intra_edges, cross_edges

# =========================================================
# 3) المحراب والواجهة السيادية
# =========================================================
try:
    l_idx = {normalize_arabic(i["letter"]): i for i in load_json("sovereign_letters_v1.json") if i.get("letter")}
    r_idx = {normalize_arabic(r["root"]): {"root": normalize_arabic(r["root"]), "weight": float(r.get("frequency", 1)), "orbit": r.get("orbit_hint", "بناء")} for r in load_json("quran_roots_complete.json").get("roots", [])}
except: st.error("❌ فشل تحميل القواعد السيادية."); st.stop()

st.title("🛰️ محراب نبراس v17.0 Unified Sovereign")

tabs = st.tabs(["🔍 المحراب الرباعي والتحليل", "🌌 اللوحة الكونية والأنماط الوجودية"])

with tabs[0]:
    cols_in = st.columns(3)
    inputs = [cols_in[i].text_area(f"📍 المسار {i+1}", key=f"unified_in_{i}", height=120) for i in range(3)]
    run_btn = st.button("🚀 استنطاق الوجود الشامل", use_container_width=True)

if run_btn:
    all_s_results = []
    for t in inputs:
        if t.strip():
            sentences = [s.strip() for s in re.sub(r"[\.!\?؛،]", ".", t).split(".") if s.strip()]
            all_s_results.append([{"sentence": s, "analysis": analyze_path_v17_unified(s, l_idx, r_idx)} for s in sentences])
        else: all_s_results.append(None)

    if any(all_s_results):
        nodes_g, intra_g, cross_g = build_global_semantic_graph(all_s_results)
        # محرك الرنين (v16.5)
        res_map = {r: round((len(info["paths"]) * info["energy"]) * 0.5, 2) for r, info in nodes_g.items()}
        # محرك الأنماط (v17)
        arche_map = {r: {"q": Q_ARCHETYPES.get(r, "بناء"), "u": UNIVERSAL_ARCHETYPES.get(Q_ARCHETYPES.get(r, "بناء"), "The Architect")} for r in nodes_g}
        global_sem = {i+1: Counter([SEMANTIC_FIELDS.get(r["root"], "بناء") for s in s_list for r in s["analysis"]["matched_roots"]]).most_common(1)[0][0] if s_list else "صمت" for i, s_list in enumerate(all_s_results)}

        with tabs[0]:
            st.divider()
            cols_res = st.columns(3)
            for i, s_res in enumerate(all_s_results):
                if s_res:
                    with cols_res[i]:
                        st.markdown(f"<div class='comparison-card'><h3>مسار {i+1}</h3><h1>{round(sum(s['analysis']['total'] for s in s_res), 1)}</h1></div>", unsafe_allow_html=True)
                        with st.expander(f"✨ المحراب الرباعي {i+1}", expanded=True):
                            st.markdown(f"🧠 المجال: **{global_sem[i+1]}**")
                            # طيف الطاقة (v16)
                            df_e = pd.DataFrame([{"root": r["root"], "energy": r["weight"]} for s in s_res for r in s["analysis"]["matched_roots"]])
                            if not df_e.empty:
                                st.plotly_chart(px.bar_polar(df_e, r="energy", theta="root", template="plotly_dark", height=200).update_layout(showlegend=False, margin=dict(l=10,r=10,t=10,b=10)), use_container_width=True)
                            # الانحراف (v16.5)
                            st.markdown("#### ⏳ الانحراف")
                            df_d = pd.DataFrame([{"index": idx+1, "orbit": s["analysis"]["orbit"]} for idx, s in enumerate(s_res)])
                            st.plotly_chart(px.line(df_d, x="index", y="orbit", markers=True, height=200).update_layout(margin=dict(l=0,r=0,t=0,b=0)), use_container_width=True)

            # المستشار الموحد
            finals = [f"{v['u']} of {v['q']}" for v in arche_map.values()]
            dominant = Counter(finals).most_common(1)[0][0] if finals else "The Silent"
            st.markdown(f"<div class='advisor-box'><h3>🧭 المستشار السيادي الموحد (v17)</h3><p><b>النمط الوجودي الحاكم:</b> {dominant}</p><p><b>الرنين الكلي للمجال:</b> {round(sum(res_map.values()), 1)}</p></div>", unsafe_allow_html=True)

        with tabs[1]:
            st.markdown(f"<div class='intent-box'><h3>🔮 حقل الأنماط واللوحة الكونية</h3><p>النية الوجودية: <b>{dominant}</b></p></div>", unsafe_allow_html=True)
            
            if nodes_g:
                fig_g = go.Figure()
                pos_g = {n: (random.random(), random.random()) for n in nodes_g}
                # رسم العلاقات (v16.5)
                for (a, b), w in {**intra_g, **cross_g}.items():
                    fig_g.add_trace(go.Scatter(x=[pos_g[a][0], pos_g[b][0]], y=[pos_g[a][1], pos_g[b][1]], mode="lines", line=dict(width=w/2, color="#222"), hoverinfo="none"))
                # رسم الأنماط والهالات (v17)
                for n, info in nodes_g.items():
                    a_info = arche_map[n]
                    color = ARCHE_COLORS.get(a_info['q'], "#4CAF50")
                    halo = HALO_COLORS.get(a_info['u'], "rgba(255,255,255,0.1)")
                    r_val = res_map.get(n, 1)
                    
                    # الهالة (Universal Archetype + Resonance)
                    fig_g.add_shape(type="circle", xref="x", yref="y", x0=pos_g[n][0]-(r_val*0.015), y0=pos_g[n][1]-(r_val*0.015), x1=pos_g[n][0]+(r_val*0.015), y1=pos_g[n][1]+(r_val*0.015), fillcolor=halo, line=dict(width=0))
                    # العقدة (Q-Archetype + Count)
                    fig_g.add_trace(go.Scatter(x=[pos_g[n][0]], y=[pos_g[n][1]], mode="markers+text", text=[f"{n}<br><span style='font-size:10px;'>{a_info['u']}</span>"], marker=dict(size=22+(info['count']*6), color=color, line=dict(width=2, color="#000")), textposition="top center"))

                fig_g.update_layout(height=750, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(visible=False), yaxis=dict(visible=False), showlegend=False)
                st.plotly_chart(fig_g, use_container_width=True)

st.sidebar.write("v17.0 Unified | خِت فِت.")
