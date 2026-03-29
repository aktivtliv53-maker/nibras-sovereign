# -*- coding: utf-8 -*
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
# [1] مصفوفة الثوابت الجينية والجمالية (The Absolute Sovereign Matrix)
# ==============================================================================
# ملاحظة: هذه المصفوفة تمثل المحاور الأربعة للتمكين الوجودي.
GENE_STYLE = {
    'A': {
        'name': 'الإبل', 
        'color': '#4fc3f7', 
        'icon': '🐪', 
        'meaning': 'الظعن والمبادرة واليسر',
        'desc': 'طاقة الانطلاق والفتح في مسارات الوجود.'
    },
    'G': {
        'name': 'البقر', 
        'color': '#FFD700', 
        'icon': '🐄', 
        'meaning': 'التأسيس والصبر والخير',
        'desc': 'طاقة التجذر والبناء الصبور لحقائق التمكين.'
    },
    'T': {
        'name': 'الضأن', 
        'color': '#4CAF50', 
        'icon': '🐑', 
        'meaning': 'الألفة والسكينة والمقام',
        'desc': 'طاقة السكينة والجمع والاحتواء في المحراب.'
    },
    'C': {
        'name': 'المعز', 
        'color': '#ff5252', 
        'icon': '🐐', 
        'meaning': 'السمو والمواجهة والتمكين',
        'desc': 'طاقة الارتفاع والحدّة في طلب السيادة.'
    },
    'N': {
        'name': 'إشراق', 
        'color': '#00ffcc', 
        'icon': '✨', 
        'meaning': 'ولادة المعنى الهجين الصافي',
        'desc': 'نقطة الانبثاق التي تولد من تفاعل الأضداد.'
    }
}

# ==============================================================================
# [2] المحركات الفوقية للاستنطاق (The Meta-Decoding Engines)
# ==============================================================================
def normalize(text):
    """تطهير النص من العوارض اللغوية للوصول لجوهر الحرف."""
    if not text: return ""
    # إزالة التشكيل
    text = re.sub(r'[\u064B-\u0652]', '', text)
    # توحيد الرموز الهندسية للحرف
    replacements = {"أ": "ا", "إ": "ا", "آ": "ا", "ة": "ه", "ى": "ي"}
    for k, v in replacements.items():
        text = text.replace(k, v)
    # تنقية المسافات والرموز غير العربية
    return re.sub(r'[^\u0621-\u064A\s]', '', text).strip()

def match_root(word, index_keys):
    """بروتوكول الربط المداري بين الكلمة وجذرها الأصيل."""
    w = normalize(word)
    if not w: return None
    
    # 1. المطابقة المباشرة
    if w in index_keys: return w
    
    # 2. بروتوكول تجريد السوابق (Prefix Stripping)
    prefixes = ["ال", "و", "ف", "ب", "ك", "ل", "س"]
    for p in prefixes:
        if w.startswith(p) and len(w) - len(p) >= 3:
            w_sub = w[len(p):]
            if w_sub in index_keys: return w_sub
            
    # 3. بروتوكول تجريد اللواحق (Suffix Stripping)
    suffixes = ["ون", "ين", "ان", "ات", "ه", "ها", "هم", "كم", "نا", "كما", "تم"]
    for s in suffixes:
        if w.endswith(s) and len(w) - len(s) >= 3:
            w_sub = w[:-len(s)]
            if w_sub in index_keys: return w_sub
            
    # 4. ميزان الثلاثي الهندسي (Trilateral Extraction)
    if len(w) >= 3:
        tri = w[:3]
        if tri in index_keys: return tri
        
    return None

# ==============================================================================
# [3] الوعي المداري والتكيف (The Orbital Meta-Observer)
# ==============================================================================
class SovereignObserver:
    def __init__(self):
        self.fusions = 0
        self.repulsions = 0
        self.gene_activity = Counter()
        self.logs = []
        self.start_time = time.time()

    def record_collision(self, type, r1, r2):
        if type == "fusion":
            self.fusions += 1
            self.logs.append(f"[{time.strftime('%H:%M:%S')}] إشراق سيادي: التحام {r1} مع {r2} بالخير واليسر.")
        else:
            self.repulsions += 1

    def track_genes(self, bodies):
        for b in bodies:
            if b['root'] != "✨":
                self.gene_activity[b['gene']] += 1

    def generate_report(self):
        dom_gene = self.gene_activity.most_common(1)[0][0] if self.gene_activity else "N"
        return {
            "fusions": self.fusions,
            "repulsions": self.repulsions,
            "dominant": dom_gene,
            "uptime": round(time.time() - self.start_time, 2),
            "logs": self.logs
        }

# ==============================================================================
# [4] الغلاف الجمالي السيادي (Hardened CSS Framework)
# ==============================================================================
st.set_page_config(page_title="Nibras v21.8.0 Monolith", page_icon="🛡️", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Orbitron:wght@400;700&display=swap');
    
    [data-testid="stAppViewContainer"] {
        background: radial-gradient(circle at center, #0a0a1a 0%, #010103 100%);
        color: #e0e0e0;
        font-family: 'Amiri', serif;
        direction: rtl;
    }
    
    .story-box {
        background: linear-gradient(135deg, rgba(10,21,10,0.8) 0%, rgba(1,1,1,0.9) 100%);
        padding: 45px;
        border-radius: 25px;
        border-right: 15px solid #4CAF50;
        line-height: 2.6;
        font-size: 1.6em;
        box-shadow: 0 20px 60px rgba(0,0,0,0.8);
        margin: 20px 0;
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
    
    .stat-box { text-align: center; }
    .stat-label { font-size: 1em; color: #888; margin-bottom: 5px; }
    .stat-val { font-size: 2.2em; font-weight: bold; color: #4fc3f7; font-family: 'Orbitron', sans-serif; }
    
    .ultra-card {
        background: #0d0d14;
        padding: 35px;
        border-radius: 20px;
        border-top: 8px solid #4fc3f7;
        text-align: center;
        transition: all 0.5s ease;
        margin-bottom: 25px;
    }
    .ultra-card:hover { transform: scale(1.05); background: #14141f; }
    
    .adaptive-log {
        background: #000;
        border: 2px solid #ffaa00;
        padding: 25px;
        color: #ffaa00;
        font-family: 'Courier New', monospace;
        height: 250px;
        overflow-y: auto;
        border-radius: 15px;
        font-size: 1.1em;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# [5] ربط المدار (Data Initialization)
# ==============================================================================
roots_data = None
potential_paths = [
    "quran_roots_complete.json",
    "data/quran_roots_complete.json",
    "/mount/src/nibras-sovereign/quran_roots_complete.json"
]

for path in potential_paths:
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                roots_data = json.load(f)
                break
        except: continue

if not roots_data:
    st.error("⚠️ المفاعل معطل: ملف الجذور غائب عن الرادار السيادي.")
    st.stop()

# بناء الفهرس السيادي
r_index = {normalize(r["root"]): r for r in roots_data.get("roots", [])}
st.sidebar.success(f"✅ تم الاتصال المداري")

# ==============================================================================
# [6] محراب نبراس: المحرك السداسي (The 6-Tab Core)
# ==============================================================================
if 'sovereign_state' not in st.session_state:
    st.session_state.sovereign_state = {'bodies': [], 'pool': [], 'report': None, 'active': False}

tabs = st.tabs([
    "🔍 الاستنطاق المداري", 
    "🌌 الرنين الجيني", 
    "📈 اللوحة الوجودية", 
    "📜 البيان الختامي", 
    "⚖️ الميزان السيادي", 
    "🧠 الوعي الفوقي"
])

# --- التبويب 1: الاستنطاق (The Deciphering Tab) ---
with tabs[0]:
    st.markdown("### 📍 هندسة المسارات المدارية")
    col1, col2, col3 = st.columns(3)
    p1 = col1.text_area("المسار السيادي (أ)", key="path_a", height=150, placeholder="أدخل الآيات...")
    p2 = col2.text_area("المسار السيادي (ب)", key="path_b", height=150)
    p3 = col3.text_area("المسار السيادي (ج)", key="path_c", height=150)
    
    if st.button("🚀 إطلاق المفاعل السيادي الكلي", use_container_width=True):
        observer = SovereignObserver()
        active_bodies, word_pool = [], []
        
        all_inputs = [p1, p2, p3]
        for input_text in all_inputs:
            if input_text.strip():
                # إزالة الأرقام والأقواس
                clean_text = re.sub(r'[0-9\(\)]', '', normalize(input_text))
                for word in clean_text.split():
                    root_found = match_root(word, r_index.keys())
                    if root_found:
                        gene = random.choice(['A', 'G', 'T', 'C'])
                        energy_val = float(len(root_found) * 240.0)
                        active_bodies.append({
                            "root": root_found,
                            "gene": gene,
                            "energy": energy_val,
                            "x": random.uniform(-8, 8),
                            "y": random.uniform(-8, 8),
                            "vx": random.uniform(-0.15, 0.15),
                            "vy": random.uniform(-0.15, 0.15),
                            "color": GENE_STYLE[gene]['color'],
                            "life": 100
                        })
                        word_pool.append(root_found)

        if active_bodies:
            motion_ui = st.empty()
            # حلقة المحاكاة الوجودية
            for frame in range(110):
                # فيزياء التصادم والتحول الرمزي
                for i in range(len(active_bodies)):
                    for j in range(i+1, len(active_bodies)):
                        dist = ((active_bodies[i]['x'] - active_bodies[j]['x'])**2 + 
                                (active_bodies[i]['y'] - active_bodies[j]['y'])**2)**0.5
                        if dist < 1.6:
                            if active_bodies[i]['gene'] == active_bodies[j]['gene']:
                                observer.record_collision("fusion", active_bodies[i]['root'], active_bodies[j]['root'])
                            else:
                                active_bodies[i]['vx'] *= -1.2; active_bodies[j]['vx'] *= -1.2
                
                for b in active_bodies:
                    b['x'] += b['vx']; b['y'] += b['vy']
                    if abs(b['x']) > 22 or abs(b['y']) > 22: b['vx'] *= -1; b['vy'] *= -1
                
                # الرسم المداري
                df_frame = pd.DataFrame(active_bodies)
                fig_orb = px.scatter(
                    df_frame, x="x", y="y", text="root", size="energy", color="gene",
                    color_discrete_map={g:s['color'] for g,s in GENE_STYLE.items()},
                    range_x=[-25,25], range_y=[-25,25]
                )
                fig_orb.update_layout(
                    height=700, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                    showlegend=False, xaxis_visible=False, yaxis_visible=False
                )
                motion_ui.plotly_chart(fig_orb, use_container_width=True)
                time.sleep(0.01)

            observer.track_genes(active_bodies)
            st.session_state.sovereign_state = {
                'bodies': active_bodies,
                'pool': list(set(word_pool)),
                'report': observer.generate_report(),
                'active': True
            }
            st.rerun()

# --- تعبئة الطبقات السيادية من الذاكرة (Persistence Protocol) ---
state = st.session_state.sovereign_state

with tabs[1]: # الرنين الجيني
    st.markdown("### 🌌 مصفوفة الأصناف والتمكين")
    cols_gene = st.columns(5)
    for idx, (g_key, g_info) in enumerate(GENE_STYLE.items()):
        cols_gene[idx].markdown(f"""
        <div class="ultra-card" style="border-top-color:{g_info['color']}">
            <div style="font-size:3em;">{g_info['icon']}</div>
            <h3>{g_info['name']}</h3>
            <p><b>{g_info['meaning']}</b></p>
            <p><small>{g_info['desc']}</small></p>
        </div>
        """, unsafe_allow_html=True)

if state['active']:
    df_final = pd.DataFrame(state['bodies'])
    
    with tabs[2]: # اللوحة الوجودية
        st.markdown("### 📈 التحليل الكمي للمسارات")
        c1, c2 = st.columns(2)
        pie = px.pie(df_final, names='gene', color='gene', color_discrete_map={g:s['color'] for g,s in GENE_STYLE.items()}, hole=0.4, title="توازن الجينات في المدار")
        c1.plotly_chart(pie, use_container_width=True)
        bar = px.bar(df_final, x='root', y='energy', color='gene', color_discrete_map={g:s['color'] for g,s in GENE_STYLE.items()}, title="طاقة استنطاق الحروف")
        c2.plotly_chart(bar, use_container_width=True)

    with tabs[3]: # البيان الختامي
        st.markdown(f"""
        <div class="story-box">
            <b>بيان الاستواء الوجودي:</b><br>
            بفضل من الله ومنّة، تم استنطاق <b>{len(state['pool'])}</b> جذراً قرآنياً في هذا المحراب. 
            إن المسار الذي رسمته الآن يحقق توازناً سيادياً يميل نحو <b>اليسر والخير</b> المطلق. 
            الجذور المتفاعلة تشكل بنية عصية على الهدم، وتنبئ بتمكين في مسارات الفعل والوعي. 
            هذا البيان هو وجه الحق الذي تجلى من خلال تفاعل الحروف والجينات.
        </div>
        """, unsafe_allow_html=True)

    with tabs[4]: # الميزان السيادي
        st.markdown("### ⚖️ ميزان الجذور المستخلصة")
        st.table(df_final[['root', 'gene', 'energy']].sort_values('energy', ascending=False))

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
        <div class="adaptive-log">
            {'<br>'.join(rep['logs']) if rep['logs'] else "المدار في حالة سكون إيجابي.."}
        </div>
        """, unsafe_allow_html=True)
else:
    for i in range(2, 6):
        with tabs[i]: st.info("المحراب في حالة انتظار.. أطلق المفاعل لملء الموازين والبيانات.")

# ==============================================================================
# [7] التذييل السيادي (Sovereign Footer)
# ==============================================================================
st.sidebar.markdown(f"""
**المستخدم:** محمد  
**الحالة:** استواء سيادي  
**البنية:** لا مساس (Extended)  
**الإصدار:** v21.8.0  
---
""")
st.sidebar.write("خِت فِت.")
