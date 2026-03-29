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

# --- استدعاء محركات الإدراك (بروتوكول v20.3.1 الصارم) ---
try:
    from letter_engine import analyze_word_letters
    from orbit_polarity import get_orbit_meta
    from state_engine import detect_state
    from tone_engine import purify_text
    from orbit_letter_engine import build_path_orbit_letter_profile
except ImportError as e:
    st.error(f"⚠️ نقص في ملفات المحركات: {e}")

# =========================================================
# 1) التهيئة والقاموس الوجودي (The Sovereign Core)
# =========================================================
st.set_page_config(page_title="Nibras v20.3.1 Sovereign Fusion", page_icon="🎙️", layout="wide")

Q_ARCHETYPES = {
    "رحم": "الرحمة", "عدل": "العدل", "نور": "النور", "نصر": "القوة", 
    "ملك": "القوة", "هدى": "الهداية", "خلف": "التمكين", "امن": "اليقين", "كفر": "الصد"
}

UNIVERSAL_ARCHETYPES = {
    "الرحمة": "The Healer", "العدل": "The Judge", "النور": "The Sage",
    "القوة": "The Warrior", "الهداية": "The Guide", "التمكين": "The Creator",
    "اليقين": "The Believer", "الصد": "The Shadow"
}

ARCHE_COLORS = {"الرحمة": "#4fc3f7", "القوة": "#ff5252", "الهداية": "#4CAF50", "العدل": "#FFD700", "النور": "#bb86fc"}

st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background-color: #030305; color: #e0e0e0; }
    .eloquence-box { 
        background: linear-gradient(145deg, #0a150a, #020202); 
        padding: 30px; border-radius: 20px; border: 1px solid #1e3a1e; 
        border-right: 5px solid #4CAF50; line-height: 1.8; font-size: 1.1em;
    }
    .ultra-card { background: #0a0a0f; padding: 25px; border-radius: 15px; border: 1px solid #1a1a2a; border-top: 4px solid #4fc3f7; margin-bottom: 20px; }
    .path-state-tag { color: #4fc3f7; font-size: 0.75em; font-weight: bold; background: #1a1a2a; padding: 2px 8px; border-radius: 5px; }
    .fusion-sig { color: #4CAF50; font-family: monospace; font-size: 0.9em; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 2) محركات التحليل الهيكلي (Data & Logic)
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
# 3) الواجهة والتنفيذ السيادي (The Final Execution)
# =========================================================
roots_data = load_data("quran_roots_complete.json")

if roots_data:
    r_idx = {normalize_arabic(r["root"]): {"weight": float(r.get("frequency", 1)), "orbit": r.get("orbit_hint", "بناء")} for r in roots_data.get("roots", [])}

    st.title("🎙️ محراب نبراس v20.3.1 - الاندماج المعزز")
    
    tab1, tab2, tab3 = st.tabs(["🔍 المحراب والتحليل", "🌌 اللوحة الكونية", "📝 البيان الموحد"])

    with tab1:
        c1, c2, c3 = st.columns(3)
        p1 = c1.text_area("📍 المسار 1", height=120, key="txt_p1")
        p2 = c2.text_area("📍 المسار 2", height=120, key="txt_p2")
        p3 = c3.text_area("📍 المسار 3", height=120, key="txt_p3")
        run = st.button("🚀 استنطاق الاندماج السيادي", use_container_width=True)

    if run:
        all_res = []
        for inp in [p1, p2, p3]:
            if inp.strip():
                sents = [s.strip() for s in re.split(r'[.!?؛،]', inp) if s.strip()]
                all_res.append([{"sentence": s, "analysis": {
                    "roots": [{"root": match_root(w, r_idx)[0], "orbit": match_root(w, r_idx)[1]["orbit"], "weight": match_root(w, r_idx)[1]["weight"]} for w in normalize_arabic(s).split() if match_root(w, r_idx)[0]]
                }} for s in sents])
            else: all_res.append(None)

        if any(all_res):
            nodes_g = {}
            for idx, s_list in enumerate(all_res):
                if not s_list: continue
                for s in s_list:
                    for r_info in s["analysis"]["roots"]:
                        r = r_info["root"]
                        nodes_g[r] = nodes_g.get(r, {"orbit": r_info["orbit"], "energy": r_info["weight"], "paths": set(), "count": 0})
                        nodes_g[r]["paths"].add(idx+1); nodes_g[r]["count"] += 1
            
            res_map = {r: (len(info["paths"]) * info["energy"]) for r, info in nodes_g.items()}
            dom_root = max(res_map.items(), key=lambda x: x[1])[0] if res_map else "صمت"

            with tab1:
                st.divider()
                cols = st.columns(3)
                for i, s_list in enumerate(all_res):
                    if s_list:
                        with cols[i]:
                            # --- طبقة v20.3.1: الدمج العميق ---
                            words = [r["root"] for s in s_list for r in s["analysis"]["roots"]]
                            orbits = [r["orbit"] for s in s_list for r in s["analysis"]["roots"]]
                            energies = [r["weight"] for s in s_list for r in s["analysis"]["roots"]]

                            fusion = build_path_orbit_letter_profile(words, orbits, energies)
                            path_state = detect_state(words)

                            st.markdown(f"""
                            <div class='ultra-card'>
                                <span class='path-state-tag'>{path_state}</span>
                                <h3 style='margin-top:10px;'>مسار {i+1}</h3>
                                <h1>{round(fusion['total_energy'], 1)}</h1>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            with st.expander("🧬 بصمة الحرف والمدار المعززة"):
                                st.write(f"🔋 طاقة الاندماج: **{round(fusion['total_energy'], 2)}**")
                                st.divider()
                                for item in fusion["profile"]:
                                    st.markdown(f"**{item['word']}**")
                                    st.markdown(f"<span class='fusion-sig'>مدار: {item['orbit']} | طاقة: {round(item['fused_energy'], 2)}</span>", unsafe_allow_html=True)
                                    # إضافة بيانات signature_strength (التي أشرت إليها يا محمد)
                                    st.caption(f"قوة البصمة المدارية: {round(item.get('fused_energy', 0) / (fusion['avg_energy'] or 1), 2)}")

            with tab3:
                # البيان الوجودي الموحد (v18 Logic with v20.3 state)
                global_state = detect_state([dom_root])
                u_arc = UNIVERSAL_ARCHETYPES.get(Q_ARCHETYPES.get(dom_root, "بناء"), "The Architect")
                
                field_stmt = f"المحور المركزي: **'{dom_root}'**. النمط الحاكم: **{u_arc}**."
                state_stmt = f"الحالة السيادية المسيطرة: **{global_state}**."
                
                st.markdown(f"""
                <div class='eloquence-box'>
                    {purify_text(field_stmt)}<br><br>
                    {purify_text(state_stmt)}<br><br>
                    <b>الخلاصة:</b> النظام يتحرك الآن في مقام '{u_arc}' تحت تأثير '{global_state}'.
                </div>
                """, unsafe_allow_html=True)
                
            with tab2:
                # اللوحة الكونية (v18 Independent Map)
                fig = go.Figure()
                pos = {n: (random.random(), random.random()) for n in nodes_g}
                for n, info in nodes_g.items():
                    q = Q_ARCHETYPES.get(n, "بناء")
                    fig.add_trace(go.Scatter(x=[pos[n][0]], y=[pos[n][1]], mode="markers+text", text=[f"<b>{n}</b>"], marker=dict(size=30+(info['count']*10), color=ARCHE_COLORS.get(q, "#4CAF50"))))
                fig.update_layout(height=600, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False)
                st.plotly_chart(fig, use_container_width=True, key="cosmic_v20_3")

st.sidebar.write("v20.3.1 Sovereign Fusion | خِت فِت.")
