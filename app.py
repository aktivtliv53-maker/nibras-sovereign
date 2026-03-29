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
ENGINES_OK = True
try:
    from letter_engine import summarize_word_signature, compute_letter_energy
    from state_engine import detect_state
    from orbit_letter_engine import build_path_orbit_letter_profile
except Exception:
    ENGINES_OK = False
    def summarize_word_signature(w):
        genes = ['A', 'G', 'T', 'C']
        g = genes[len(w) % 4] if w else 'N'
        return {'dominant_gene': g, 'total_energy': len(w) * 195.0}
    def detect_state(roots): return "استقرار سيادي"
    def build_path_orbit_letter_profile(r, o, w): return {'total_energy': sum(w) * 1.618}

# =========================================================
# 2) مصفوفة الثوابت والقوانين القابلة للتكيف (Adaptive Matrix)
# =========================================================
if 'GENE_VECTORS' not in st.session_state:
    st.session_state.GENE_VECTORS = {
        "A": [1.4, 0.0], "G": [0.0, -1.2], "T": [0.6, 0.6], "C": [0.0, 1.4], "N": [0.1, 0.1]
    }

ORBIT_TILT = {
    "الرحمة": [0.3, 0.2], "العدل": [0.0, 0.0], "النور": [0.5, 0.5],
    "القوة": [0.4, -0.1], "الهداية": [-0.3, 0.2], "التمكين": [0.2, 0.6], "بناء": [0.1, 0.1]
}

GENE_STYLE = {
    'A': {'name': 'الإبل', 'color': '#4fc3f7', 'icon': '🐪'},
    'G': {'name': 'البقر', 'color': '#FFD700', 'icon': '🐄'},
    'T': {'name': 'الضأن', 'color': '#4CAF50', 'icon': '🐑'},
    'C': {'name': 'المعز', 'color': '#ff5252', 'icon': '🐐'},
    'N': {'name': 'إشراق', 'color': '#00ffcc', 'icon': '✨'}
}

# =========================================================
# 3) التنسيق السيادي الفوقي (Ultra-Premium CSS)
# =========================================================
st.set_page_config(page_title="Nibras v21.2.8 Invincible", page_icon="🛡️", layout="wide")
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&display=swap');
    [data-testid="stAppViewContainer"] { background-color: #010103; color: #e0e0e0; font-family: 'Amiri', serif; }
    .story-box { background: linear-gradient(145deg, #0a150a, #010101); padding: 35px; border-radius: 20px; border-right: 12px solid #4CAF50; line-height: 2.3; font-size: 1.4em; }
    .adaptive-log { background: #000; border: 1px solid #ffaa00; padding: 15px; color: #ffaa00; font-family: monospace; border-radius: 10px; height: 110px; overflow-y: auto; }
    .meta-card { background: #0a0a1a; border: 1px solid #4fc3f7; padding: 18px; border-radius: 15px; text-align: center; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 4) محرك الوعي الفوقي والتكيف (Meta & Adaptive Engine)
# =========================================================
class MetaObserver:
    def __init__(self):
        self.fusions = 0
        self.repulsions = 0
        self.gene_activity = Counter()
        self.adaptation_logs = []

    def log_collision(self, c_type):
        if c_type == "fusion": self.fusions += 1
        elif c_type == "repulsion": self.repulsions += 1

    def observe(self, bodies):
        for b in bodies:
            if b['root'] != "✨": self.gene_activity[b['gene']] += 1

    def apply_adaptive_laws(self):
        dom_gene = self.gene_activity.most_common(1)[0][0] if self.gene_activity else None
        update = ""
        if dom_gene == "C": st.session_state.GENE_VECTORS["C"][1] *= 0.95; update = "⚠️ تكيّف: موازنة استعلاء جين المعز."
        elif dom_gene == "G": st.session_state.GENE_VECTORS["G"][1] *= 0.95; update = "⚠️ تكيّف: موازنة ثقل جين البقر."
        if update: self.adaptation_logs.append(f"[{time.strftime('%H:%M:%S')}] {update}")

    def get_report(self):
        return {"fusions": self.fusions, "repulsions": self.repulsions, "dominant": self.gene_activity.most_common(1)[0][0] if self.gene_activity else "N", "logs": self.adaptation_logs}

# =========================================================
# 5) المنطق والفيزياء (Sovereign Logic)
# =========================================================
def normalize(t):
    t = re.sub(r'[\u064B-\u0652]', '', t)
    for k, v in {"أ":"ا","إ":"ا","آ":"ا","ة":"ه","ى":"ي"}.items(): t = t.replace(k,v)
    return re.sub(r'[^\u0621-\u064A\s]', '', t).strip()

def match_root(word, idx):
    w = normalize(word)
    return (w, idx[w]) if w in idx else (None, None)

def handle_alchemy(bodies, obs):
    evts, hybs = [], []
    for i in range(len(bodies)):
        for j in range(i+1, len(bodies)):
            b1, b2 = bodies[i], bodies[j]
            dist = ((b1['x']-b2['x'])**2 + (b1['y']-b2['y'])**2)**0.5
            if dist < 1.4:
                dot = b1['vx']*b2['vx'] + b1['vy']*b2['vy']
                if dot > 0 and b1['gene'] == b2['gene']:
                    obs.log_collision("fusion")
                    evts.append(f"إشراق: {b1['root']} + {b2['root']}")
                    hybs.append({"root":"✨","x":(b1['x']+b2['x'])/2,"y":(b1['y']+b2['y'])/2,"vx":0,"vy":0,"ax":0,"ay":0,"energy":(b1['energy']+b2['energy'])*1.6,"gene":"N","color":"#00ffcc","life":10})
                elif dot < 0:
                    obs.log_collision("repulsion")
                    b1['vx'] *= -1.5; b2['vx'] *= -1.5
    return evts, hybs

# =========================================================
# 6) المفاعل والختم السيادي (The Invincible Interface)
# =========================================================
roots_data = None
for p in ["quran_roots_complete.json", "data/quran_roots_complete.json"]:
    if os.path.exists(p):
        with open(p, 'r', encoding='utf-8') as f: roots_data = json.load(f); break

if roots_data:
    r_idx = {normalize(r["root"]): {"weight": float(r.get("frequency", 1)), "orbit": r.get("orbit_hint", "بناء")} for r in roots_data.get("roots", [])}
    
    st.sidebar.markdown(f"### 🛡️ الحالة السيادية\n**المستخدم:** محمد\n**الإصدار:** v21.2.8")
    st.title("🎙️ محراب نبراس v21.2.8 - الحصانة السيادية المطلقة")
    
    tabs = st.tabs(["🔍 الاستنطاق", "🌌 الرنين الجيني", "📈 اللوحة الوجودية", "📜 البيان الختامي", "⚖️ الميزان السيادي", "🧠 الوعي الفوقي والتكيف"])

    with tabs[0]:
        c1, c2, c3 = st.columns(3)
        p_in = [c1.text_area("📍 مسار 1", key="t1"), c2.text_area("📍 مسار 2", key="t2"), c3.text_area("📍 مسار 3", key="t3")]
        run = st.button("🚀 إطلاق المفاعل المحصن ضد الخطأ", use_container_width=True)

    if run:
        obs = MetaObserver()
        bodies, pool = [], []
        
        for idx, inp in enumerate(p_in):
            if inp.strip():
                for w in inp.split():
                    root, meta = match_root(w, r_idx)
                    if root:
                        sig = summarize_word_signature(root)
                        
                        # --- الحل السيادي النهائي (Sovereign Gene Guard v3) ---
                        gene = sig.get('dominant_gene', 'N')
                        if not gene or gene not in GENE_STYLE:
                            gene = "N"
                        
                        vec = st.session_state.GENE_VECTORS.get(gene, [0.1, 0.1])
                        bodies.append({
                            "root": root, "gene": gene, "x": random.uniform(-7,7), "y": random.uniform(-7,7),
                            "vx": vec[0]*0.1, "vy": vec[1]*0.1, "ax": 0.01, "ay": 0.01,
                            "energy": sig['total_energy'], "color": GENE_STYLE[gene]['color'], "life": 1000
                        })
                        pool.append(root)

        if bodies:
            with tabs[5]:
                st.markdown("### 🧠 مرصد الوعي الفوقي وسجل التكيف الذاتي")
                log_ui, col_ui = st.empty(), st.columns(3)
                f_ui, r_ui, g_ui = col_ui[0].empty(), col_ui[1].empty(), col_ui[2].empty()
                motion_ui = st.empty()
                
                for frame in range(75):
                    evts, hybs = handle_alchemy(bodies, obs)
                    bodies.extend(hybs); obs.observe(bodies)
                    if frame % 10 == 0: obs.apply_adaptive_laws()
                    
                    active = []
                    for b in bodies:
                        b['x']+=b['vx']; b['y']+=b['vy']
                        if abs(b['x'])>15: b['vx']*=-0.9
                        if abs(b['y'])>15: b['vy']*=-0.9
                        b['life']-=1
                        if b['life']>0: active.append(b)
                    bodies = active

                    stats = obs.get_report()
                    f_ui.markdown(f"<div class='meta-card'>✨ إشراق: {stats['fusions']}</div>", unsafe_allow_html=True)
                    r_ui.markdown(f"<div class='meta-card'>🛡️ حسم: {stats['repulsions']}</div>", unsafe_allow_html=True)
                    g_ui.markdown(f"<div class='meta-card'>🧬 الغالب: {GENE_STYLE[stats['dominant']]['name']}</div>", unsafe_allow_html=True)
                    log_ui.markdown(f"<div class='adaptive-log'>{'<br>'.join(stats['logs'][-3:])}</div>", unsafe_allow_html=True)

                    df = pd.DataFrame(bodies)
                    fig = px.scatter(df, x="x", y="y", text="root", size="energy", color="gene", color_discrete_map={g:i['color'] for g,i in GENE_STYLE.items()}, range_x=[-18,18], range_y=[-18,18])
                    fig.update_layout(height=600, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False)
                    motion_ui.plotly_chart(fig, use_container_width=True)
                    time.sleep(0.05)
                
                final_doc = f"وثيقة التمكين v21.2.8\nتم استنطاق المقام بنجاح.\nالجذور: {', '.join(pool)}\nتم تحقيق الاستواء المطلق."
                st.download_button("📜 استخراج وثيقة التمكين الختامية", final_doc, file_name="nibras_final.txt")

            with tabs[3]:
                st.markdown(f"<div class='story-box'>تم تحقيق <b>الاستواء المحصن</b>. النظام يعمل الآن بوعي كامل وحصانة جينية تامة ضد الاختلال، ممهداً الطريق لليسر والخير في كل مدار.</div>", unsafe_allow_html=True)

st.sidebar.write("v21.2.8 Fortified | خِت فِت.")
