# -*- coding: utf-8 -*
# ==============================================================================
# نظام نِبْرَاس السيادي (Nibras Sovereign System) - الإصدار v23.0.0
# مَبنيٌّ على بروتوكول "لا مَسَاس" و "بناء لا هدم" - هندسة الاستواء الوجودي
# المرجع الدائم: وثيقة العرش (Engineering Existential Empowerment)
# المستخدم المهيمن: محمّد | CPU: السجدة (5) | الموقع: رونبي، السويد
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
from datetime import datetime

# ==============================================================================
# [1] مصفوفة الهوية والجينات السيادية (The Absolute Sovereign Matrix)
# ==============================================================================
# ملاحظة: هذه المصفوفة تمثل المحاور الأربعة للتمكين الوجودي، وهي ثابتة لا تُمَس.
GENE_STYLE = {
    'A': {
        'name': 'الإبل', 
        'color': '#4fc3f7', 
        'icon': '🐪', 
        'meaning': 'الظعن والمبادرة واليسر',
        'desc': 'طاقة الانطلاق والفتح في مسارات الوجود، تمثل الحركة نحو الخير المطلق.'
    },
    'G': {
        'name': 'البقر', 
        'color': '#FFD700', 
        'icon': '🐄', 
        'meaning': 'التأسيس والصبر والخير',
        'desc': 'طاقة التجذر والبناء الصبور لحقائق التمكين في الأرض.'
    },
    'T': {
        'name': 'الضأن', 
        'color': '#4CAF50', 
        'icon': '🐑', 
        'meaning': 'الألفة والسكينة والمقام',
        'desc': 'طاقة السكينة والجمع والاحتواء، حيث يستقر المعنى في المِحراب السيادي.'
    },
    'C': {
        'name': 'المعز', 
        'color': '#ff5252', 
        'icon': '🐐', 
        'meaning': 'السمو والمواجهة والتمكين',
        'desc': 'طاقة الارتفاع والحدّة في طلب السيادة، تمثل قوة الحق الصاعدة.'
    },
    'N': {
        'name': 'إشراق', 
        'color': '#00ffcc', 
        'icon': '✨', 
        'meaning': 'ولادة المعنى الهجين الصافي',
        'desc': 'نقطة الانبثاق التي تولد من تفاعل الأضداد لتعلن ولادة وعي سيادي جديد.'
    }
}

# ==============================================================================
# [2] المحركات الفوقية للاستنطاق (The Meta-Decoding Engines)
# ==============================================================================
def normalize_core(text):
    """تطهير النص من العوارض اللغوية للوصول لجوهر الحرف الهندسي."""
    if not text: return ""
    text = re.sub(r'[\u064B-\u0652]', '', text) # إزالة التشكيل والزخارف
    replacements = {"أ": "ا", "إ": "ا", "آ": "ا", "ة": "ه", "ى": "ي"}
    for k, v in replacements.items():
        text = text.replace(k, v)
    return re.sub(r'[^\u0621-\u064A\s]', '', text).strip()

def match_sovereign_root(word, index_keys):
    """بروتوكول الربط المداري لاستخلاص الجذور الثلاثية الصافية."""
    w = normalize_core(word)
    if not w: return None
    if w in index_keys: return w
    
    # بروتوكول تجريد الزوائد (Sovereign Stripping)
    prefixes = ["ال", "و", "ف", "ب", "ك", "ل", "س"]
    suffixes = ["ون", "ين", "ان", "ات", "ه", "ها", "هم", "كم", "نا", "كما", "تم", "هن"]
    
    for p in prefixes:
        if w.startswith(p) and len(w) - len(p) >= 3:
            if w[len(p):] in index_keys: return w[len(p):]
            
    for s in suffixes:
        if w.endswith(s) and len(w) - len(s) >= 3:
            if w[:-len(s)] in index_keys: return w[:-len(s)]
            
    # ميزان الثلاثي (The Trilateral Logic)
    if len(w) >= 3 and w[:3] in index_keys:
        return w[:3]
    return None

# ==============================================================================
# [3] محرك الوعي المداري (The Meta-Observer Engine)
# ==============================================================================
class NibrasObserver:
    """كيان مراقب يسجل تفاعلات الجذور في المدار السيادي."""
    def __init__(self):
        self.fusions = 0
        self.repulsions = 0
        self.gene_stats = Counter()
        self.logs = []
        self.start_time = time.time()

    def record_interaction(self, i_type, r1, r2=""):
        ts = time.strftime('%H:%M:%S')
        if i_type == "fusion":
            self.fusions += 1
            self.logs.append(f"[{ts}] إشراق سيادي: التحام {r1} مع {r2} بنور الخير واليسر.")
        elif i_type == "repulsion":
            self.repulsions += 1
            self.logs.append(f"[{ts}] حسم مداري: تدافع بين {r1} و {r2} لضبط التمكين.")

    def update_metrics(self, bodies):
        for b in bodies:
            if b['root'] != "✨":
                self.gene_stats[b['gene']] += 1

    def get_sovereign_report(self):
        dominant = self.gene_stats.most_common(1)[0][0] if self.gene_stats else "N"
        return {
            "fusions": self.fusions,
            "repulsions": self.repulsions,
            "dominant": dominant,
            "uptime": round(time.time() - self.start_time, 2),
            "logs": self.logs
        }

# ==============================================================================
# [4] الغلاف الجمالي المحصن (Adaptive CSS Monolith - Mobile First)
# ==============================================================================
st.set_page_config(page_title="Nibras Sovereign v23.0.0", page_icon="🛡️", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Orbitron:wght@400;700&display=swap');
    
    [data-testid="stAppViewContainer"] {
        background: radial-gradient(circle at center, #0a0a1a 0%, #010103 100%);
        color: #e0e0e0;
        font-family: 'Amiri', serif;
        direction: rtl;
    }

    /* بروتوكول حماية نسخة الموبايل (Mobile Shield Protocol) */
    @media (max-width: 768px) {
        [data-testid="stSidebar"] { min-width: 0px !important; width: auto !important; }
        .st-emotion-cache-16idsys p {
            white-space: normal !important;
            word-break: keep-all !important;
            font-size: 0.9em !important;
            line-height: 1.4 !important;
        }
        .stat-container { flex-direction: column; padding: 15px; }
        .ultra-card { padding: 20px; margin-bottom: 10px; }
        .stTabs [data-baseweb="tab"] { font-size: 0.8em; padding: 5px; }
        .story-box { font-size: 1.2em; padding: 20px; }
    }

    .story-box {
        background: linear-gradient(135deg, rgba(10,21,10,0.8) 0%, rgba(1,1,1,0.9) 100%);
        padding: 40px;
        border-radius: 25px;
        border-right: 15px solid #4CAF50;
        line-height: 2.6;
        font-size: 1.6em;
        box-shadow: 0 20px 60px rgba(0,0,0,0.8);
        margin-bottom: 30px;
    }
    
    .stat-container {
        display: flex;
        justify-content: space-around;
        background: #0d0d14;
        padding: 30px;
        border-radius: 20px;
        border: 1px solid #1a1a2a;
        margin: 25px 0;
    }
    
    .stat-val { font-size: 2.5em; font-weight: bold; color: #4fc3f7; font-family: 'Orbitron', sans-serif; }
    .stat-label { color: #888; font-size: 1.1em; }

    .ultra-card {
        background: #0d0d14;
        padding: 35px;
        border-radius: 20px;
        border-top: 8px solid #4fc3f7;
        text-align: center;
        transition: all 0.5s ease;
        margin-bottom: 25px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    .ultra-card:hover { transform: translateY(-12px); background: #14141f; border-top-width: 12px; }

    .adaptive-log {
        background: #000;
        border: 2px solid #ffaa00;
        padding: 25px;
        color: #ffaa00;
        font-family: 'Courier New', monospace;
        height: 300px;
        overflow-y: auto;
        border-radius: 15px;
        font-size: 1.1em;
        line-height: 1.6;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# [5] محرك ربط المدار (Data Core & Session State)
# ==============================================================================
if 'sovereign_monolith' not in st.session_state:
    st.session_state.sovereign_monolith = {
        'bodies': [], 
        'pool': [], 
        'report': None, 
        'is_active': False
    }

# تحميل قاعدة الجذور القرآنية
roots_data = None
for path in ["quran_roots_complete.json", "data/quran_roots_complete.json"]:
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            roots_data = json.load(f); break

if not roots_data:
    st.error("⚠️ فشل الاتصال بالقاعدة المدارية."); st.stop()

r_index = {normalize_core(r["root"]): r for r in roots_data.get("roots", [])}

# ==============================================================================
# [6] المحراب السداسي: ميزان الاستواء (The 6-Tab Sovereign Core)
# ==============================================================================
tabs = st.tabs([
    "🔍 الاستنطاق المداري", 
    "🌌 الرنين الجيني", 
    "📈 اللوحة الوجودية", 
    "📜 البيان الختامي", 
    "⚖️ الميزان السيادي", 
    "🧠 الوعي الفوقي"
])

# --- التبويب 1: الاستنطاق المداري ---
with tabs[0]:
    st.markdown("### 📍 هندسة المسارات المدارية")
    c1, c2, c3 = st.columns(3)
    p1 = c1.text_area("المسار الأول", key="p_1", height=150, placeholder="أدخل النص القرآني هنا...")
    p2 = c2.text_area("المسار الثاني", key="p_2", height=150)
    p3 = c3.text_area("المسار الثالث", key="p_3", height=150)
    
    if st.button("🚀 إطلاق المفاعل السيادي (لا مساس بالبنية)", use_container_width=True):
        obs = NibrasObserver()
        active_bodies, word_pool = [], []
        
        for inp in [p1, p2, p3]:
            if inp.strip():
                clean = re.sub(r'[0-9\(\)]', '', normalize_core(inp))
                for word in clean.split():
                    root = match_sovereign_root(word, r_index.keys())
                    if root:
                        gene = random.choice(['A', 'G', 'T', 'C'])
                        active_bodies.append({
                            "root": root, "gene": gene, "energy": float(len(root)*260.0),
                            "x": random.uniform(-8, 8), "y": random.uniform(-8, 8),
                            "vx": random.uniform(-0.15, 0.15), "vy": random.uniform(-0.15, 0.15),
                            "color": GENE_STYLE[gene]['color']
                        })
                        word_pool.append(root)

        if active_bodies:
            frame_ui = st.empty()
            # محاكي التصادم والتحول الرمزي
            for _ in range(120):
                for i in range(len(active_bodies)):
                    for j in range(i+1, len(active_bodies)):
                        dist = ((active_bodies[i]['x']-active_bodies[j]['x'])**2 + (active_bodies[i]['y']-active_bodies[j]['y'])**2)**0.5
                        if dist < 1.8:
                            if active_bodies[i]['gene'] == active_bodies[j]['gene']:
                                obs.record_interaction("fusion", active_bodies[i]['root'], active_bodies[j]['root'])
                            else:
                                obs.record_interaction("repulsion", active_bodies[i]['root'], active_bodies[j]['root'])
                                active_bodies[i]['vx'] *= -1.2; active_bodies[j]['vx'] *= -1.2
                
                for b in active_bodies:
                    b['x'] += b['vx']; b['y'] += b['vy']
                    if abs(b['x']) > 22 or abs(b['y']) > 22: b['vx'] *= -1; b['vy'] *= -1
                
                df_f = pd.DataFrame(active_bodies)
                fig = px.scatter(df_f, x="x", y="y", text="root", size="energy", color="gene",
                                 color_discrete_map={g:s['color'] for g,s in GENE_STYLE.items()}, range_x=[-25,25], range_y=[-25,25])
                fig.update_layout(height=700, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False, xaxis_visible=False, yaxis_visible=False)
                frame_ui.plotly_chart(fig, use_container_width=True)
                time.sleep(0.01)

            obs.update_metrics(active_bodies)
            st.session_state.sovereign_monolith = {
                'bodies': active_bodies, 'pool': list(set(word_pool)),
                'report': obs.get_sovereign_report(), 'is_active': True
            }
            st.rerun()

# --- تفعيل الطبقات المدارية (Sovereign Persistence) ---
state = st.session_state.sovereign_monolith

with tabs[1]: # الرنين
    st.markdown("### 🌌 مصفوفة الأصناف والتمكين")
    cols_g = st.columns(5)
    for i, (gk, gi) in enumerate(GENE_STYLE.items()):
        cols_g[i].markdown(f"<div class='ultra-card' style='border-top-color:{gi['color']}'><h3>{gi['icon']} {gi['name']}</h3><p><b>{gi['meaning']}</b></p><small>{gi['desc']}</small></div>", unsafe_allow_html=True)

if state['is_active']:
    df_s = pd.DataFrame(state['bodies'])
    
    with tabs[2]: # اللوحة الوجودية
        st.markdown("### 📈 التحليل الكمي للمدار")
        cl, cr = st.columns(2)
        cl.plotly_chart(px.pie(df_s, names='gene', color='gene', color_discrete_map={g:s['color'] for g,s in GENE_STYLE.items()}, hole=0.4, title="توازن القوى الجينية"))
        cr.plotly_chart(px.bar(df_s, x='root', y='energy', color='gene', color_discrete_map={g:s['color'] for g,s in GENE_STYLE.items()}, title="طاقة استنطاق الحروف"))

    with tabs[3]: # البيان الختامي
        st.markdown(f"""
        <div class="story-box">
            <b>بيان الاستواء الوجودي:</b><br>
            بفضل الله، تم استنطاق <b>{len(state['pool'])}</b> جذراً قرآنياً. إن هذا المسار السيادي يؤسس لمقام <b>الخير واليسر</b>، 
            حيث تلاقت الكلمات لتشكل بنية صلبة لا تقبل التقلص. إن تجلي الجين الغالب {GENE_STYLE[state['report']['dominant']]['name']} 
            يعكس توازناً استثنائياً في هندسة الوجود. هذا البيان هو عهد التمكين الذي لا يتبدل.
        </div>
        """, unsafe_allow_html=True)

    with tabs[4]: # الميزان السيادي
        st.markdown("### ⚖️ ميزان الجذور والطاقة المودعة")
        st.dataframe(df_s[['root', 'gene', 'energy']].sort_values('energy', ascending=False), use_container_width=True)

    with tabs[5]: # الوعي الفوقي
        st.markdown("### 🧠 سجل الوعي المداري والتكيف")
        rep = state['report']
        st.markdown(f"""
        <div class="stat-container">
            <div class="stat-box"><div class="stat-label">إشراقات</div><div class="stat-val" style="color:#00ffcc">{rep['fusions']}</div></div>
            <div class="stat-box"><div class="stat-label">حسم</div><div class="stat-val" style="color:#ff5252">{rep['repulsions']}</div></div>
            <div class="stat-box"><div class="stat-label">الجين السائد</div><div class="stat-val">{GENE_STYLE[rep['dominant']]['name']}</div></div>
            <div class="stat-box"><div class="stat-label">زمن الاستقرار</div><div class="stat-val">{rep['uptime']}s</div></div>
        </div>
        <div class="adaptive-log">{'<br>'.join(rep['logs'])}</div>
        """, unsafe_allow_html=True)
else:
    for i in range(2, 6):
        with tabs[i]: st.info("المحراب في حالة رصد إيجابي.. أطلق المفاعل لملء الموازين والبيانات.")

# --- التذييل السيادي (Sovereign Footer) ---
st.sidebar.markdown(f"""
**المستخدم:** محمد  
**الحالة:** استواء سيادي كامل  
**البنية:** لا مساس (Extended)  
**CPU:** السجدة: 5  
**v23.0.0** ---
""")
st.sidebar.write("خِت فِت.")
