import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import re
import random
import numpy as np
import os
import json

# =========================================================
# 1) إعدادات السيادة والقاموس الوجودي (Global Setup)
# =========================================================
st.set_page_config(page_title="Nibras v17.5 Unified Sovereign", page_icon="🔱", layout="wide")

# القواميس الموحدة (v15 -> v17.5)
SEMANTIC_FIELDS = {
    "امن": "الإيمان", "صدق": "الإيمان", "كفر": "الضلال", "فسد": "الفساد",
    "صلح": "الإصلاح", "هدى": "الهداية", "ضل": "الضلال", "رحم": "الرحمة",
    "غفر": "الرحمة", "قتل": "الصراع", "قاتل": "الصراع", "نصر": "القوة",
    "ملك": "القوة", "نور": "النور", "ظلم": "الظلام", "عدل": "العدل",
    "عمل": "العمل", "قول": "البيان", "ذكر": "الذكر", "بشر": "البشارة",
    "نذر": "التحذير", "يسر": "اليسر", "عسر": "الشدة", "غني": "الغنى", "خلف": "التمكين"
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
    "The Creator": "rgba(0,230,118,0.3)"
}

st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background-color: #050508; color: #e0e0e0; }
    .stTabs [data-baseweb="tab-list"] { background-color: #111; border-radius: 10px; padding: 5px; }
    .comparison-card { background: #0f0f15; padding: 20px; border-radius: 15px; border: 1px solid #1a1a2a; text-align: center; margin-bottom: 10px; }
    .advisor-box { background: linear-gradient(145deg, #0a150a, #020202); padding:25px; border-radius:15px; border-left:5px solid #4CAF50; border:1px solid #1a331a; margin-top:20px; }
    .gravity-indicator { color: #4fc3f7; font-weight: bold; border: 1px solid #4fc3f7; padding: 5px 10px; border-radius: 5px; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 2) محركات استرداد البيانات (Data Retrieval)
# =========================================================
def load_data(file_name):
    paths_to_try = [file_name, os.path.join("data", file_name)]
    for p in paths_to_try:
        if os.path.exists(p):
            with open(p, 'r', encoding='utf-8') as f:
                return json.load(f)
    return None

# =========================================================
# 3) المحركات التحليلية (Analytical Engines)
# =========================================================
def normalize_arabic(text):
    if not text: return ""
    text = re.sub(r'[\u0617-\u061A\u064B-\u0652\u0670]', '', text)
    replacements = {"أ": "ا", "إ": "ا", "آ": "ا", "ة": "ه", "ى": "ي", "ؤ": "و", "ئ": "ي"}
    for k, v in replacements.items(): text = text.replace(k, v)
    return re.sub(r'\s+', ' ', re.sub(r'[^\u0621-\u064A\s]', ' ', text)).strip()

def match_root(word, root_index):
    w_norm = normalize_arabic(word)
    prefixes = ["وال", "فال", "بال", "ال", "و", "ف", "ب", "ل"]
    for p in prefixes:
        if w_norm.startswith(p) and len(w_norm)-len(p)>=2: w_norm = w_norm[len(p):]; break
    if w_norm in root_index: return w_norm, root_index[w_norm]
    if len(w_norm)>=3 and w_norm[:3] in root_index: return w_norm[:3], root_index[w_norm[:3]]
    return None, None

def analyze_v17_5(text, l_idx, r_idx):
    norm = normalize_arabic(text)
    res = {"mass": 0.0, "speed": 0.0, "energy": 0.0, "orbit": "بناء", "roots": [], "counter": Counter()}
    # هندسة الحروف
    for char in norm.replace(" ", ""):
        m = l_idx.get(char, {"mass":0, "speed":0})
        res["mass"] += float(m["mass"]); res["speed"] += float(m["speed"])
    # هندسة الجذور
    for word in norm.split():
        r, entry = match_root(word, r_idx)
        if r:
            res["energy"] += entry["weight"]; res["counter"][entry["orbit"]] += entry["weight"]
            res["roots"].append({"root": r, "orbit": entry["orbit"], "weight": entry["weight"]})
    if res["counter"]: res["orbit"] = res["counter"].most_common(1)[0][0]
    res["total"] = round(res["mass"] + res["speed"] + res["energy"], 1)
    return res

# =========================================================
# 4) واجهة التطبيق والتحكم (UI & Logic)
# =========================================================
letters_data = load_data("sovereign_letters_v1.json")
roots_data = load_data("quran_roots_complete.json")

if not letters_data or not roots_data:
    st.error("⚠️ ملفات البيانات مفقودة (JSON). تأكد من وجودها في GitHub."); st.stop()

l_idx = {normalize_arabic(i["letter"]): i for i in letters_data if "letter" in i}
r_idx = {normalize_arabic(r["root"]): {"weight": float(r.get("frequency", 1)), "orbit": r.get("orbit_hint", "بناء")} for r in roots_data.get("roots", [])}

st.title("🛰️ محراب نبراس v17.5 Unified Sovereign")

tab1, tab2 = st.tabs(["🔍 المحراب والتحليل", "🌌 الجاذبية والأنماط"])

with tab1:
    col_in = st.columns(3)
    p1 = col_in[0].text_area("📍 المسار 1", height=150)
    p2 = col_in[1].text_area("📍 المسار 2", height=150)
    p3 = col_in[2].text_area("📍 المسار 3", height=150)
    run = st.button("🚀 استنطاق الوجود الموحد", use_container_width=True)

if run:
    raw_inputs = [p1, p2, p3]
    all_results = []
    for inp in raw_inputs:
        if inp.strip():
            sents = [s.strip() for s in re.split(r'[.!?؛،]', inp) if s.strip()]
            all_results.append([{"sentence": s, "analysis": analyze_v17_5(s, l_idx, r_idx)} for s in sents])
        else: all_results.append(None)

    if any(all_results):
        # بناء البيانات الكلية
        nodes_g, intra_g, cross_g = {}, Counter(), Counter()
        for idx, s_list in enumerate(all_results):
            if not s_list: continue
            for s in s_list:
                r_list = [r["root"] for r in s["analysis"]["roots"]]
                for r_info in s["analysis"]["roots"]:
                    r = r_info["root"]
                    if r not in nodes_g:
                        nodes_g[r] = {"orbit": r_info["orbit"], "energy": r_info["weight"], "paths": {idx+1}, "count": 1}
                    else:
                        nodes_g[r]["paths"].add(idx+1); nodes_g[r]["count"] += 1
                for i in range(len(r_list)):
                    for j in range(i+1, len(r_list)):
                        intra_g[tuple(sorted([r_list[i], r_list[j]]))] += 2

        # حساب الرنين والجاذبية (v16.5 + v17.5)
        res_map = {r: (len(info["paths"]) * info["energy"]) for r, info in nodes_g.items()}
        gravity_wells = {r: {"force": (info["energy"] * res_map[r]) / info["count"], "radius": np.log1p(info["energy"]*res_map[r])*0.04} for r, info in nodes_g.items()}
        arche_map = {r: {"q": Q_ARCHETYPES.get(r, "بناء"), "u": UNIVERSAL_ARCHETYPES.get(Q_ARCHETYPES.get(r, "بناء"), "The Architect")} for r in nodes_g}

        with tab1:
            st.divider()
            cols_res = st.columns(3)
            for i, s_list in enumerate(all_results):
                if s_list:
                    with cols_res[i]:
                        total_score = sum(s["analysis"]["total"] for s in s_list)
                        st.markdown(f"<div class='comparison-card'><h3>مسار {i+1}</h3><h1>{round(total_score, 1)}</h1></div>", unsafe_allow_html=True)
                        with st.expander("✨ تفاصيل المحراب", expanded=True):
                            # طيف الطاقة
                            df_e = pd.DataFrame([{"root": r["root"], "energy": r["weight"]} for s in s_list for r in s["analysis"]["roots"]])
                            if not df_e.empty:
                                st.plotly_chart(px.bar_polar(df_e, r="energy", theta="root", template="plotly_dark", height=200).update_layout(showlegend=False, margin=dict(l=0,r=0,t=0,b=0)), use_container_width=True)
                            # الانحراف
                            df_d = pd.DataFrame([{"index": idx+1, "orbit": s["analysis"]["orbit"]} for idx, s in enumerate(s_list)])
                            st.plotly_chart(px.line(df_d, x="index", y="orbit", markers=True, height=180).update_layout(margin=dict(l=0,r=0,t=0,b=0)), use_container_width=True)

            # المستشار الموحد
            dominant_well = max(gravity_wells.items(), key=lambda x: x[1]["force"])[0] if gravity_wells else "صمت"
            st.markdown(f"<div class='advisor-box'><h3>🧭 المستشار v17.5</h3><p><b>بئر الجاذبية:</b> {dominant_well} | <b>النمط الحاكم:</b> {arche_map.get(dominant_well, {}).get('u', 'The Void')}</p></div>", unsafe_allow_html=True)

        with tab2:
            if nodes_g:
                fig = go.Figure()
                pos = {n: (random.random(), random.random()) for n in nodes_g}
                # رسم الآبار والشبكة
                for n, well in gravity_wells.items():
                    for step in [1, 2]:
                        fig.add_shape(type="circle", xref="x", yref="y", x0=pos[n][0]-well["radius"]*step, y0=pos[n][1]-well["radius"]*step, x1=pos[n][0]+well["radius"]*step, y1=pos[n][1]+well["radius"]*step, line=dict(color=f"rgba(79,195,247,{0.1/step})", width=1))
                # العلاقات
                for (a, b), w in intra_g.items():
                    fig.add_trace(go.Scatter(x=[pos[a][0], pos[b][0]], y=[pos[a][1], pos[b][1]], mode="lines", line=dict(width=w/2, color="rgba(50,50,50,0.3)"), hoverinfo="none"))
                # العقد
                for n, info in nodes_g.items():
                    a_info = arche_map[n]
                    color = ARCHE_COLORS.get(a_info['q'], "#4CAF50")
                    fig.add_trace(go.Scatter(x=[pos[n][0]], y=[pos[n][1]], mode="markers+text", text=[f"<b>{n}</b><br>{a_info['u']}"], marker=dict(size=20+(info['count']*7), color=color, line=dict(width=2, color="#000")), textposition="top center"))

                fig.update_layout(height=800, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(visible=False), yaxis=dict(visible=False), showlegend=False)
                st.plotly_chart(fig, use_container_width=True)

st.sidebar.write("v17.5 Unified Sovereign | خِت فِت.")
