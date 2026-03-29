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

# =========================================================
# 1) المحركات السيادية (The Sovereign Core Engines)
# =========================================================
try:
    from letter_engine import summarize_word_signature, compute_letter_energy
    from state_engine import detect_state
except Exception:
    def summarize_word_signature(w):
        genes = ['A', 'G', 'T', 'C']
        g = genes[len(w) % 4] if w else 'N'
        return {'dominant_gene': g, 'total_energy': float(len(w) * 195)}
    def detect_state(roots): return "استقرار سيادي"

# =========================================================
# 2) مصفوفة الثوابت الجينية (The Adaptive Matrix)
# =========================================================
if 'GENE_VECTORS' not in st.session_state:
    st.session_state.GENE_VECTORS = {
        "A": [1.4, 0.0], "G": [0.0, -1.2], "T": [0.6, 0.6], "C": [0.0, 1.4], "N": [0.1, 0.1]
    }

GENE_STYLE = {
    'A': {'name': 'الإبل', 'color': '#4fc3f7', 'icon': '🐪', 'meaning': 'الظعن والمبادرة واليسر'},
    'G': {'name': 'البقر', 'color': '#FFD700', 'icon': '🐄', 'meaning': 'التأسيس والصبر والخير'},
    'T': {'name': 'الضأن', 'color': '#4CAF50', 'icon': '🐑', 'meaning': 'الألفة والسكينة والمقام'},
    'C': {'name': 'المعز', 'color': '#ff5252', 'icon': '🐐', 'meaning': 'السمو والمواجهة والتمكين'},
    'N': {'name': 'إشراق', 'color': '#00ffcc', 'icon': '✨', 'meaning': 'ولادة المعنى الهجين الصافي'}
}

# =========================================================
# 3) التنسيق السيادي الفوقي (Ultra-Premium CSS)
# =========================================================
st.set_page_config(page_title="Nibras v21.3.5 Full Synthesis", page_icon="🛡️", layout="wide")
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&display=swap');
    [data-testid="stAppViewContainer"] { background-color: #010103; color: #e0e0e0; font-family: 'Amiri', serif; }
    .story-box { background: linear-gradient(145deg, #0a150a, #010101); padding: 40px; border-radius: 20px; border-right: 15px solid #4CAF50; line-height: 2.3; font-size: 1.4em; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
    .adaptive-log { background: #000; border: 1px solid #ffaa00; padding: 15px; color: #ffaa00; font-family: monospace; border-radius: 10px; height: 120px; overflow-y: auto; }
    .stat-container { display: flex; justify-content: space-around; background: #0a0a0f; padding: 15px; border-radius: 12px; border: 1px solid #1a1a2a; margin-top: 10px; }
    .stat-box { text-align: center; }
    .stat-val { font-size: 1.6em; font-weight: bold; display: block; }
    .ultra-card { background: #0a0a0f; padding: 25px; border-radius: 15px; border-top: 5px solid #4fc3f7; margin-bottom: 20px; text-align: center; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 4) محرك الوعي الفوقي (Meta Observer Engine)
# =========================================================
class MetaObserver:
    def __init__(self):
        self.fusions = 0
        self.repulsions = 0
        self.gene_activity = Counter()
        self.adaptation_logs = []
        self.start_time = time.time()

    def log_collision(self, c_type):
        if c_type == "fusion": self.fusions += 1
        elif c_type == "repulsion": self.repulsions += 1

    def observe(self, bodies):
        for b in bodies:
            if b['root'] != "✨": self.gene_activity[b['gene']] += 1

    def apply_adaptive_laws(self):
        dom_gene = self.gene_activity.most_common(1)[0][0] if self.gene_activity else "N"
        update = ""
        if dom_gene == "C": st.session_state.GENE_VECTORS["C"][1] *= 0.95; update = "موازنة استعلاء المعز."
        elif dom_gene == "G": st.session_state.GENE_VECTORS["G"][1] *= 0.95; update = "موازنة ثقل البقر."
        if update: self.adaptation_logs.append(f"[{time.strftime('%H:%M:%S')}] {update}")

    def get_report(self):
        return {
            "fusions": self.fusions, "repulsions": self.repulsions, 
            "dominant": self.gene_activity.most_common(1)[0][0] if self.gene_activity else "N", 
            "logs": self.adaptation_logs, "uptime": round(time.time() - self.start_time, 2)
        }

# =========================================================
# 5) المنطق والفيزياء السيادية (Sovereign Logic)
# =========================================================
def normalize(t):
    t = re.sub(r'[\u064B-\u0652]', '', t)
    for k, v in {"أ":"ا","إ":"ا","آ":"ا","ة":"ه","ى":"ي"}.items(): t = t.replace(k,v)
    return re.sub(r'[^\u0621-\u064A\s]', '', t).strip()

def handle_alchemy(bodies, obs):
    hybs = []
    for i in range(len(bodies)):
        for j in range(i+1, len(bodies)):
            b1, b2 = bodies[i], bodies[j]
            dist = ((b1['x']-b2['x'])**2 + (b1['y']-b2['y'])**2)**0.5
            if dist < 1.5:
                if b1['gene'] == b2['gene']:
                    obs.log_collision("fusion")
                    hybs.append({"root":"✨","x":(b1['x']+b2['x'])/2,"y":(b1['y']+b2['y'])/2,"vx":0,"vy":0,"energy":(b1['energy']+b2['energy'])*1.6,"gene":"N","color":"#00ffcc","life":15})
                else:
                    obs.log_collision("repulsion")
                    b1['vx'] *= -1.5; b2['vx'] *= -1.5
    return hybs

# =========================================================
# 6) رادار المسارات المطور (The Path Finder Core)
# =========================================================
roots_data = None
target_filename = "quran_roots_complete.json"
search_paths = [target_filename, f"data/{target_filename}", f"../{target_filename}"]

found_path = None
for path in search_paths:
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                roots_data = json.load(f)
                found_path = path
                break
        except: continue

# التحقق السيادي قبل التشغيل
if not roots_data:
    st.error(f"⚠️ عطل سيادي: لم يتم العثور على {target_filename} في المسارات المحددة.")
    with st.expander("🔍 فحص ملفات السيرفر الحالية"):
        st.write("المسار النشط:", os.getcwd())
        st.write("قائمة الملفات:", os.listdir("."))
    st.stop()
else:
    r_idx = {normalize(r["root"]): r.get("orbit_hint", "بناء") for r in roots_data.get("roots", [])}
    st.sidebar.success(f"✅ تم الاتصال بالقاعدة: {found_path}")

# =========================================================
# 7) المحراب السيادي الشامل (The Sovereign Tabbed Interface)
# =========================================================
st.title("🎙️ محراب نبراس - الاستواء المداري الشامل v21.3.5")
tabs = st.tabs(["🔍 الاستنطاق", "🌌 الرنين الجيني", "📈 اللوحة الوجودية", "📜 البيان الختامي", "⚖️ الميزان السيادي", "🧠 الوعي الفوقي"])

with tabs[0]:
    c1, c2, c3 = st.columns(3)
    p_in = [c1.text_area("📍 مسار 1", key="t1"), c2.text_area("📍 مسار 2", key="t2"), c3.text_area("📍 مسار 3", key="t3")]
    run = st.button("🚀 إطلاق المفاعل السيادي الشامل", use_container_width=True)
    
    # حاويات العرض الموحد
    motion_ui = st.empty()
    stats_ui = st.empty()

if run:
    obs = MetaObserver()
    bodies, pool = [], []
    
    for inp in p_in:
        if inp.strip():
            # تنظيف النص واستخراج الكلمات
            clean_text = re.sub(r'[0-9\(\)]', '', normalize(inp))
            for word in clean_text.split():
                if word in r_idx:
                    sig = summarize_word_signature(word)
                    gene = sig.get('dominant_gene', 'N').upper()
                    if gene not in GENE_STYLE: gene = "N"
                    
                    vec = st.session_state.GENE_VECTORS.get(gene, [0.1, 0.1])
                    bodies.append({
                        "root": word, "gene": gene, "x": random.uniform(-6,6), "y": random.uniform(-6,6),
                        "vx": vec[0]*0.12, "vy": vec[1]*0.12, "energy": sig['total_energy'],
                        "color": GENE_STYLE[gene]['color'], "life": 1000
                    })
                    pool.append(word)

    if not bodies:
        st.warning("⚠️ لم يتم استنطاق أي جذور. يرجى التأكد من كتابة الكلمات بشكل فصيح.")
    else:
        # حلقة المفاعل (120 إطاراً لضمان السيولة)
        for frame in range(120):
            hybs = handle_alchemy(bodies, obs)
            bodies.extend(hybs); obs.observe(bodies)
            if frame % 15 == 0: obs.apply_adaptive_laws()
            
            active = []
            for b in bodies:
                b['x']+=b['vx']; b['y']+=b['vy']
                if abs(b['x'])>17: b['vx']*=-0.9
                if abs(b['y'])>17: b['vy']*=-0.9
                b['life']-=1
                if b['life']>0: active.append(b)
            bodies = active

            # التحديث البصري
            df = pd.DataFrame(bodies)
            fig = px.scatter(df, x="x", y="y", text="root", size="energy", color="gene", 
                             color_discrete_map={g:i['color'] for g,i in GENE_STYLE.items()}, 
                             range_x=[-22,22], range_y=[-22,22])
            fig.update_layout(height=650, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False, xaxis={'visible':False}, yaxis={'visible':False})
            motion_ui.plotly_chart(fig, use_container_width=True)
            
            # تحديث العدادات الموحدة
            report = obs.get_report()
            stats_ui.markdown(f"""
            <div class="stat-container">
                <div class="stat-box">✨ إشراق<br><span class="stat-val" style="color:#00ffcc">{report['fusions']}</span></div>
                <div class="stat-box">🛡️ حسم<br><span class="stat-val" style="color:#ff5252">{report['repulsions']}</span></div>
                <div class="stat-box">🧬 الغالب<br><span class="stat-val" style="color:#FFD700">{GENE_STYLE[report['dominant']]['name']}</span></div>
                <div class="stat-box">⏳ الزمن<br><span class="stat-val" style="color:#4fc3f7">{report['uptime']}s</span></div>
            </div>
            """, unsafe_allow_html=True)
            time.sleep(0.01)

        # ملء التبويبات الختامية
        with tabs[3]:
            st.markdown(f"<div class='story-box'>تحقق الاستواء باليسر والخير. الجذور المستنطقة: {', '.join(set(pool))}.</div>", unsafe_allow_html=True)
        with tabs[1]:
            st.markdown("### 🌌 تحليل الرنين الجيني النشط")
            cols = st.columns(len(GENE_STYLE))
            for i, (g, info) in enumerate(GENE_STYLE.items()):
                cols[i].markdown(f"<div class='ultra-card' style='border-top-color:{info['color']}'>{info['icon']} {info['name']}<br><small>{info['meaning']}</small></div>", unsafe_allow_html=True)
        with tabs[5]:
            st.markdown("### 🧠 سجل الوعي الفوقي والتكيف الذاتي")
            st.markdown(f"<div class='adaptive-log'>{'<br>'.join(report['logs'])}</div>", unsafe_allow_html=True)

st.sidebar.markdown(f"**المستخدم:** محمد\n**CPU:** السجدة: 5\n**v21.3.5**")
st.sidebar.write("خِت فِت.")
