# -*- coding: utf-8 -*
# ==============================================================================
# نظام نِبْرَاس السيادي (Nibras Sovereign System) - الإصدار v24.0.0
# مَبنيٌّ على بروتوكول "لا مَسَاس" و "بناء لا هدم" - هندسة الاستواء الوجودي
# المرجع: وثيقة العرش | المستخدم: محمّد | CPU: السجدة (5)
# ==============================================================================

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
import time

# ==============================================================================
# [1] مصفوفة الهوية والجينات (لا مَسَاس)
# ==============================================================================
GENE_STYLE = {
    'A': {'name': 'الإبل', 'color': '#4fc3f7', 'icon': '🐪', 'meaning': 'الظعن والمبادرة واليسر', 'desc': 'طاقة الانطلاق والفتح.'},
    'G': {'name': 'البقر', 'color': '#FFD700', 'icon': '🐄', 'meaning': 'التأسيس والصبر والخير', 'desc': 'طاقة التجذر والبناء.'},
    'T': {'name': 'الضأن', 'color': '#4CAF50', 'icon': '🐑', 'meaning': 'الألفة والسكينة والمقام', 'desc': 'طاقة السكينة والجمع.'},
    'C': {'name': 'المعز', 'color': '#ff5252', 'icon': '🐐', 'meaning': 'السمو والمواجهة والتمكين', 'desc': 'طاقة الارتفاع والسيادة.'},
    'N': {'name': 'إشراق', 'color': '#00ffcc', 'icon': '✨', 'meaning': 'ولادة المعنى الهجين الصافي', 'desc': 'نقطة الانبثاق الكبرى.'}
}

# ==============================================================================
# [2] المحركات الفوقية للاستنطاق (Meta-Decoding)
# ==============================================================================
def normalize_sovereign(text):
    if not text: return ""
    text = re.sub(r'[\u064B-\u0652]', '', text)
    repls = {"أ": "ا", "إ": "ا", "آ": "ا", "ة": "ه", "ى": "ي"}
    for k, v in repls.items(): text = text.replace(k, v)
    return re.sub(r'[^\u0621-\u064A\s]', '', text).strip()

def match_root_logic(word, keys):
    w = normalize_sovereign(word)
    if not w or len(w) < 2: return None
    if w in keys: return w
    prefixes = ["ال", "و", "ف", "ب", "ك", "ل", "س"]
    suffixes = ["ون", "ين", "ان", "ات", "ه", "ها", "هم", "كم", "نا", "كما", "تم"]
    for p in prefixes:
        if w.startswith(p) and len(w)-len(p) >= 3:
            if w[len(p):] in keys: return w[len(p):]
    for s in suffixes:
        if w.endswith(s) and len(w)-len(s) >= 3:
            if w[:-len(s)] in keys: return w[:-len(s)]
    return w[:3] if len(w)>=3 and w[:3] in keys else None

# ==============================================================================
# [3] الغلاف الجمالي المحصن - بروتوكول الاستقرار (Shielded CSS)
# ==============================================================================
st.set_page_config(page_title="Nibras v24.0.0 Stable", page_icon="🛡️", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&display=swap');
    
    [data-testid="stAppViewContainer"] {
        background: radial-gradient(circle at center, #0a0a1a 0%, #010103 100%);
        color: #e0e0e0; font-family: 'Amiri', serif; direction: rtl;
    }

    /* بروتوكول الاستقرار النهائي للموبايل - حذف شبح الحروف */
    @media (max-width: 768px) {
        /* إخفاء نصوص الشريط الجانبي تماماً لمنع الانزلاق العمودي */
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
            display: none !important;
        }
        [data-testid="stSidebar"] {
            background-color: transparent !important;
            width: 0px !important;
            min-width: 0px !important;
        }
        /* توسيع المحتوى الرئيسي */
        .main .block-container {
            padding: 10px !important;
            max-width: 100% !important;
        }
        .stat-container { flex-direction: column; gap: 10px; }
        .ultra-card { padding: 15px; }
        .story-box { font-size: 1.1em; padding: 20px; line-height: 1.8; }
    }

    .story-box {
        background: linear-gradient(135deg, rgba(10,21,10,0.8) 0%, rgba(1,1,1,0.9) 100%);
        padding: 35px; border-radius: 20px; border-right: 12px solid #4CAF50;
        line-height: 2.3; font-size: 1.5em; box-shadow: 0 15px 50px rgba(0,0,0,0.7);
    }
    
    .stat-container {
        display: flex; justify-content: space-around; background: #0d0d14;
        padding: 25px; border-radius: 15px; border: 1px solid #1a1a2a; margin: 20px 0;
    }
    
    .stat-val { font-size: 2.2em; font-weight: bold; color: #4fc3f7; }
    
    .ultra-card {
        background: #0d0d14; padding: 30px; border-radius: 18px;
        border-top: 6px solid #4fc3f7; text-align: center; margin-bottom: 20px;
        transition: 0.4s;
    }
    .ultra-card:hover { transform: translateY(-10px); background: #11111a; }

    .adaptive-log {
        background: #000; border: 1px solid #ffaa00; padding: 20px;
        color: #ffaa00; font-family: monospace; height: 250px; overflow-y: auto;
        border-radius: 12px;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# [4] ربط المدار والذاكرة (Sovereign Persistence)
# ==============================================================================
if 'sov_monolith' not in st.session_state:
    st.session_state.sov_monolith = {'bodies': [], 'pool': [], 'report': None, 'active': False}

roots_data = None
for p in ["quran_roots_complete.json", "data/quran_roots_complete.json"]:
    if os.path.exists(p):
        with open(p, 'r', encoding='utf-8') as f: roots_data = json.load(f); break

if not roots_data: st.error("⚠️ المفاعل معطل."); st.stop()
r_idx = {normalize_sovereign(r["root"]): r for r in roots_data.get("roots", [])}

# ==============================================================================
# [5] المحراب السداسي (The 6 Pillars)
# ==============================================================================
tabs = st.tabs(["🔍 الاستنطاق", "🌌 الرنين", "📈 اللوحة", "📜 البيان", "⚖️ الميزان", "🧠 الوعي"])

with tabs[0]:
    st.markdown("### 📍 هندسة المسارات المدارية")
    cols = st.columns(3)
    p_in = [cols[i].text_area(f"المسار {i+1}", key=f"p_{i}", height=120) for i in range(3)]
    
    if st.button("🚀 تفعيل المفاعل السيادي الكلي", use_container_width=True):
        fusions, logs = 0, []
        active_bodies, pool = [], []
        start_t = time.time()
        
        for text in p_in:
            if text.strip():
                for word in re.sub(r'[0-9\(\)]', '', normalize_sovereign(text)).split():
                    root = match_root_logic(word, r_idx.keys())
                    if root:
                        gene = random.choice(['A', 'G', 'T', 'C'])
                        active_bodies.append({
                            "root": root, "gene": gene, "energy": float(len(root)*250),
                            "x": random.uniform(-7,7), "y": random.uniform(-7,7),
                            "vx": random.uniform(-0.12, 0.12), "vy": random.uniform(-0.12, 0.12),
                            "color": GENE_STYLE[gene]['color']
                        })
                        pool.append(root)

        if active_bodies:
            motion = st.empty()
            for _ in range(100):
                for i in range(len(active_bodies)):
                    for j in range(i+1, len(active_bodies)):
                        dist = ((active_bodies[i]['x']-active_bodies[j]['x'])**2 + (active_bodies[i]['y']-active_bodies[j]['y'])**2)**0.5
                        if dist < 1.6 and active_bodies[i]['gene'] == active_bodies[j]['gene']:
                            fusions += 1
                            logs.append(f"[{time.strftime('%H:%M:%S')}] التحام: {active_bodies[i]['root']} + {active_bodies[j]['root']}")
                
                for b in active_bodies:
                    b['x']+=b['vx']; b['y']+=b['vy']
                    if abs(b['x'])>22 or abs(b['y'])>22: b['vx']*=-1; b['vy']*=-1
                
                fig = px.scatter(pd.DataFrame(active_bodies), x="x", y="y", text="root", size="energy", color="gene",
                                 color_discrete_map={g:s['color'] for g,s in GENE_STYLE.items()}, range_x=[-25,25], range_y=[-25,25])
                fig.update_layout(height=650, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False, xaxis_visible=False, yaxis_visible=False)
                motion.plotly_chart(fig, use_container_width=True)
                time.sleep(0.01)

            st.session_state.sov_monolith = {
                'bodies': active_bodies, 'pool': list(set(pool)), 'active': True,
                'report': {"f": fusions, "u": round(time.time()-start_t, 2), "l": logs}
            }
            st.rerun()

# --- تفعيل الطبقات (الاستقرار) ---
state = st.session_state.sov_monolith

with tabs[1]:
    st.markdown("### 🌌 مصفوفة الأصناف")
    cols_g = st.columns(5)
    for i, (gk, gi) in enumerate(GENE_STYLE.items()):
        cols_g[i].markdown(f"<div class='ultra-card' style='border-top-color:{gi['color']}'><h3>{gi['icon']} {gi['name']}</h3><p>{gi['meaning']}</p></div>", unsafe_allow_html=True)

if state['active']:
    df = pd.DataFrame(state['bodies'])
    with tabs[2]:
        c1, c2 = st.columns(2)
        c1.plotly_chart(px.pie(df, names='gene', color='gene', color_discrete_map={g:s['color'] for g,s in GENE_STYLE.items()}, title="توازن الجينات"))
        c2.plotly_chart(px.bar(df, x='root', y='energy', color='gene', color_discrete_map={g:s['color'] for g,s in GENE_STYLE.items()}, title="طاقة الحروف"))
    with tabs[3]:
        st.markdown(f"<div class='story-box'><b>بيان الاستواء:</b> تم استنطاق {len(state['pool'])} جذراً. المقام مقام <b>خير ويسر</b> وتمكين.</div>", unsafe_allow_html=True)
    with tabs[4]:
        st.dataframe(df[['root', 'gene', 'energy']].sort_values('energy', ascending=False), use_container_width=True)
    with tabs[5]:
        st.markdown(f"<div class='stat-container'><div class='stat-val'>{state['report']['f']}</div><div class='stat-val'>{state['report']['u']}s</div></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='adaptive-log'>{'<br>'.join(state['report']['l'])}</div>", unsafe_allow_html=True)

# التذييل الجانبي (يختفي في الموبايل لحمايتك)
st.sidebar.markdown(f"**المستخدم:** محمد\n**v24.0.0**\n**البنية:** لا مساس")
st.sidebar.write("خِت فِت.")
