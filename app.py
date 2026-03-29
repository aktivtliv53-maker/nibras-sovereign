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
# 1) التهيئة والقاموس الوجودي المطلق (The Sovereign Core)
# =========================================================
st.set_page_config(page_title="Nibras v17.5 Ultra Final", page_icon="🔱", layout="wide")

SEMANTIC_FIELDS = {
    "امن": "الإيمان", "صدق": "الإيمان", "كفر": "الضلال", "فسد": "الفساد",
    "صلح": "الإصلاح", "هدى": "الهداية", "ضل": "الضلال", "رحم": "الرحمة",
    "غفر": "الرحمة", "قتل": "الصراع", "نصر": "القوة", "ملك": "القوة",
    "نور": "النور", "ظلم": "الظلام", "عدل": "العدل", "خلف": "التمكين", "ذكر": "الذكر"
}

Q_ARCHETYPES = {
    "رحم": "الرحمة", "عدل": "العدل", "نور": "النور", "نصر": "القوة", 
    "ملك": "القوة", "هدى": "الهداية", "خلف": "التمكين", "امن": "اليقين", "كفر": "الصد"
}

UNIVERSAL_ARCHETYPES = {
    "الرحمة": "The Healer", "العدل": "The Judge", "النور": "The Sage",
    "القوة": "The Warrior", "الهداية": "The Guide", "التمكين": "The Creator",
    "اليقين": "The Believer", "الصد": "The Shadow"
}

ARCHE_COLORS = {"الرحمة": "#4fc3f7", "القوة": "#ff5252", "الهداية": "#4CAF50", "العدل": "#FFD700", "النور": "#bb86fc", "الضلال": "#757575", "اليقين": "#03a9f4"}

st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background-color: #030305; color: #e0e0e0; }
    .ultra-card { background: #0a0a0f; padding: 25px; border-radius: 15px; border: 1px solid #1a1a2a; border-top: 4px solid #4fc3f7; margin-bottom: 20px; }
    .resonance-tag { background: rgba(79, 195, 247, 0.1); color: #4fc3f7; padding: 2px 8px; border-radius: 4px; font-size: 0.8em; border: 1px solid #4fc3f7; }
    .intent-engine-box { background: linear-gradient(90deg, #0a1a0a, #000); padding: 15px; border-radius: 10px; border-right: 4px solid #FFD700; margin-top: 10px; }
    .advisor-final { background: linear-gradient(145deg, #051005, #000); padding:30px; border-radius:20px; border: 1px solid #1e3a1e; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 2) محركات التحليل المتقدمة (v15 -> v17.5)
# =========================================================
def load_data(file_name):
    paths = [file_name, os.path.join("data", file_name)]
    for p in paths:
        if os.path.exists(p):
            with open(p, 'r', encoding='utf-8') as f: return json.load(f)
    return None

def normalize_arabic(text):
    if not text: return ""
    text = re.sub(r'[\u0617-\u061A\u064B-\u0652\u0670]', '', text)
    replacements = {"أ": "ا", "إ": "ا", "آ": "ا", "ة": "ه", "ى": "ي", "ؤ": "و", "ئ": "ي"}
    for k, v in replacements.items(): text = text.replace(k, v)
    return re.sub(r'\s+', ' ', re.sub(r'[^\u0621-\u064A\s]', ' ', text)).strip()

def match_root(word, root_index):
    w = normalize_arabic(word)
    for p in ["وال", "فال", "بال", "ال", "و", "ف", "ب", "ل"]:
        if w.startswith(p) and len(w)-len(p)>=2: w = w[len(p):]; break
    if w in root_index: return w, root_index[w]
    if len(w)>=3 and w[:3] in root_index: return w[:3], root_index[w[:3]]
    return None, None

# =========================================================
# 3) المعمار النهائي (The Final Construction)
# =========================================================
letters_data = load_data("sovereign_letters_v1.json")
roots_data = load_data("quran_roots_complete.json")

if letters_data and roots_data:
    l_idx = {normalize_arabic(i["letter"]): i for i in letters_data if "letter" in i}
    r_idx = {normalize_arabic(r["root"]): {"weight": float(r.get("frequency", 1)), "orbit": r.get("orbit_hint", "بناء")} for r in roots_data.get("roots", [])}

    st.title("🛰️ محراب نبراس v17.5 Ultra Unified Final")
    
    tab1, tab2, tab3 = st.tabs(["🔍 المحراب والنية", "🌌 اللوحة الكونية (Gravity & Cross)", "🧭 المستشار والمركز"])

    with tab1:
        c1, c2, c3 = st.columns(3)
        p1 = c1.text_area("📍 المسار 1", height=120, key="up1")
        p2 = c2.text_area("📍 المسار 2", height=120, key="up2")
        p3 = c3.text_area("📍 المسار 3", height=120, key="up3")
        run = st.button("🚀 استنطاق التمام السيادي", use_container_width=True)

    if run:
        all_res = []
        for idx, inp in enumerate([p1, p2, p3]):
            if inp.strip():
                sents = [s.strip() for s in re.split(r'[.!?؛،]', inp) if s.strip()]
                all_res.append([{"sentence": s, "analysis": {
                    "mass": sum(float(l_idx.get(c, {"mass":0})["mass"]) for c in normalize_arabic(s).replace(" ","")),
                    "speed": sum(float(l_idx.get(c, {"speed":0})["speed"]) for c in normalize_arabic(s).replace(" ","")),
                    "energy": sum(match_root(w, r_idx)[1]["weight"] for w in normalize_arabic(s).split() if match_root(w, r_idx)[0]),
                    "roots": [{"root": match_root(w, r_idx)[0], "orbit": match_root(w, r_idx)[1]["orbit"], "weight": match_root(w, r_idx)[1]["weight"]} for w in normalize_arabic(s).split() if match_root(w, r_idx)[0]]
                }} for s in sents])
            else: all_res.append(None)

        if any(all_res):
            # 1) محركات الترابط (Recovered: Cross Edges)
            nodes_g, intra_g, cross_g = {}, Counter(), Counter()
            for idx, s_list in enumerate(all_res):
                if not s_list: continue
                path_roots = []
                for s in s_list:
                    r_list = [r["root"] for r in s["analysis"]["roots"]]
                    path_roots.extend(r_list)
                    for r_info in s["analysis"]["roots"]:
                        r = r_info["root"]
                        nodes_g[r] = nodes_g.get(r, {"orbit": r_info["orbit"], "energy": r_info["weight"], "paths": set(), "count": 0})
                        nodes_g[r]["paths"].add(idx+1); nodes_g[r]["count"] += 1
                    for i in range(len(r_list)):
                        for j in range(i+1, len(r_list)): intra_g[tuple(sorted([r_list[i], r_list[j]]))] += 1
                
                # حساب العلاقات العابرة (Cross Edges) v16.5
                for r_name, info in nodes_g.items():
                    for other_r, other_info in nodes_g.items():
                        if r_name != other_r and info["orbit"] == other_info["orbit"] and (info["paths"] != other_info["paths"]):
                            cross_g[tuple(sorted([r_name, other_r]))] += 0.5

            # 2) محرك الرنين والجاذبية (Visible Layers)
            res_map = {r: (len(info["paths"]) * info["energy"]) for r, info in nodes_g.items()}
            gravity = {r: {"force": (info["energy"] * res_map[r]) / info["count"], "radius": np.log1p(info["energy"]*res_map[r])*0.05} for r, info in nodes_g.items()}
            
            with tab1:
                st.divider()
                cols = st.columns(3)
                for i, s_list in enumerate(all_res):
                    if s_list:
                        with cols[i]:
                            # المحراب الرباعي
                            total_energy = sum(s["analysis"]["energy"] for s in s_list)
                            st.markdown(f"<div class='ultra-card'><h3>مسار {i+1}</h3><h1>{round(total_energy, 1)}</h1><span class='resonance-tag'>رنين المسار: {round(total_energy * 0.12, 2)}</span></div>", unsafe_allow_html=True)
                            
                            # محرك النية العميقة (Deep Intent Engine v15.2)
                            roots_in_p = [r["root"] for s in s_list for r in s["analysis"]["roots"]]
                            fields = [SEMANTIC_FIELDS.get(r, "بناء") for r in roots_in_p]
                            dom_field = Counter(fields).most_common(1)[0][0] if fields else "بناء"
                            st.markdown(f"""<div class='intent-engine-box'><b>النية العميقة:</b> تتجه نحو <b>{dom_field}</b><br>
                                        <small>المجال المهيمن: {dom_field}</small></div>""", unsafe_allow_html=True)
                            
                            with st.expander("✨ طيف الرنين والانحراف (Visible Layers)"):
                                df_res = pd.DataFrame([{"root": r, "res": v} for r, v in res_map.items() if r in roots_in_p])
                                if not df_res.empty: st.plotly_chart(px.line_polar(df_res, r="res", theta="root", line_close=True, template="plotly_dark", height=200), use_container_width=True)

            with tab2:
                # اللوحة الكونية الكاملة (v17.5 Ultra: Gravity + Intra + Cross)
                fig = go.Figure()
                pos = {n: (random.random(), random.random()) for n in nodes_g}
                # رسم العلاقات العابرة (Cross Edges)
                for (a, b), weight in cross_g.items():
                    fig.add_trace(go.Scatter(x=[pos[a][0], pos[b][0]], y=[pos[a][1], pos[b][1]], mode="lines", line=dict(width=weight*2, color="rgba(79,195,247,0.4)", dash="dot"), hoverinfo="none"))
                # رسم الجاذبية والعلاقات الداخلية
                for n, w in gravity.items():
                    for step in [1, 2]:
                        fig.add_shape(type="circle", xref="x", yref="y", x0=pos[n][0]-w["radius"]*step, y0=pos[n][1]-w["radius"]*step, x1=pos[n][0]+w["radius"]*step, y1=pos[n][1]+w["radius"]*step, fillcolor="rgba(79,195,247,0.05)", line=dict(width=0))
                for (a, b), weight in intra_g.items():
                    fig.add_trace(go.Scatter(x=[pos[a][0], pos[b][0]], y=[pos[a][1], pos[b][1]], mode="lines", line=dict(width=weight/2, color="rgba(150,150,150,0.2)"), hoverinfo="none"))
                # العقد
                for n, info in nodes_g.items():
                    q = Q_ARCHETYPES.get(n, "بناء"); u = UNIVERSAL_ARCHETYPES.get(q, "The Architect")
                    fig.add_trace(go.Scatter(x=[pos[n][0]], y=[pos[n][1]], mode="markers+text", text=[f"<b>{n}</b><br>{u}"], marker=dict(size=25+(info['count']*10), color=ARCHE_COLORS.get(q, "#4CAF50"), line=dict(width=2, color="#fff")), textposition="top center"))
                fig.update_layout(height=800, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(visible=False), yaxis=dict(visible=False), showlegend=False)
                st.plotly_chart(fig, use_container_width=True)

            with tab3:
                # المستشار والمركز الدلالي (v16 + v17 + v17.5)
                dom_root = max(res_map.items(), key=lambda x: x[1])[0] if res_map else "صمت"
                st.markdown(f"""
                <div class='advisor-final'>
                    <h2>🧭 المستشار السيادي v17.5 Ultra Final</h2>
                    <hr style='opacity: 0.2;'>
                    <p>🎯 <b>المحور الدلالي المركزي (v16):</b> <span style='color:#FFD700; font-size:1.2em;'>{dom_root}</span></p>
                    <p>🌊 <b>طيف الرنين الكوني (v16.5):</b> أعلى رنين مسجل في جذر <b>{dom_root}</b> بقيمة {round(res_map[dom_root], 1)}</p>
                    <p>🔮 <b>النمط الوجودي الحاكم (v17):</b> {UNIVERSAL_ARCHETYPES.get(Q_ARCHETYPES.get(dom_root, "بناء"), "The Architect")}</p>
                    <p>🕳️ <b>بئر الجاذبية الأعظم (v17.5):</b> {max(gravity.items(), key=lambda x: x[1]["force"])[0]}</p>
                    <hr style='opacity: 0.2;'>
                    <p>✅ <b>التوجيه النهائي:</b> المنظومة مكتملة الترابط. العلاقات العابرة (Cross Edges) تشير إلى وحدة الموضوع عبر المسارات الثلاثة، مع سيادة مطلقة لنمط {UNIVERSAL_ARCHETYPES.get(Q_ARCHETYPES.get(dom_root, "بناء"), "The Architect")}.</p>
                </div>
                """, unsafe_allow_html=True)

st.sidebar.write("v17.5 Ultra Unified Final | خِت فِت.")
