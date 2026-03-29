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
# بروتوكول الدرع: استحضار المحركات الأصلية مع وجود بدائل حية (Fallback)
ENGINES_OK = True
try:
    from letter_engine import summarize_word_signature, compute_letter_energy, analyze_word_letters
    from state_engine import detect_state
    from tone_engine import purify_text
    from orbit_letter_engine import build_path_orbit_letter_profile
except Exception as e:
    ENGINES_OK = False
    def summarize_word_signature(w):
        genes = ['A', 'G', 'T', 'C']
        g = genes[len(w) % 4] if w else 'N'
        return {'dominant_gene': g, 'total_energy': len(w) * 195.0, 'inter_factor': 0.95}
    def detect_state(roots): return "استقرار سيادي"
    def purify_text(t): return t
    def build_path_orbit_letter_profile(r, o, w): return {'total_energy': sum(w) * 1.618}

# =========================================================
# 2) مصفوفة الثوابت والقوانين القابلة للتكيف (Adaptive Matrix)
# =========================================================
# تخزين المتجهات في session_state لضمان التعديل الحي أثناء المحاكاة
if 'GENE_VECTORS' not in st.session_state:
    st.session_state.GENE_VECTORS = {
        "A": [1.4, 0.0], "G": [0.0, -1.2], "T": [0.6, 0.6], "C": [0.0, 1.4], "N": [0.1, 0.1]
    }

ORBIT_TILT = {
    "الرحمة": [0.3, 0.2], "العدل": [0.0, 0.0], "النور": [0.5, 0.5],
    "القوة": [0.4, -0.1], "الهداية": [-0.3, 0.2], "التمكين": [0.2, 0.6], "بناء": [0.1, 0.1]
}

GENE_STYLE = {
    'A': {'name': 'الإبل', 'color': '#4fc3f7', 'icon': '🐪', 'meaning': 'الظعن والمبادرة'},
    'G': {'name': 'البقر', 'color': '#FFD700', 'icon': '🐄', 'meaning': 'التأسيس والصبر'},
    'T': {'name': 'الضأن', 'color': '#4CAF50', 'icon': '🐑', 'meaning': 'الألفة والسكينة'},
    'C': {'name': 'المعز', 'color': '#ff5252', 'icon': '🐐', 'meaning': 'السمو والمواجهة'},
    'N': {'name': 'إشراق', 'color': '#00ffcc', 'icon': '✨', 'meaning': 'ولادة المعنى الهجين'}
}

# =========================================================
# 3) التنسيق السيادي الفوقي (Ultra-Premium CSS)
# =========================================================
st.set_page_config(page_title="Nibras v21.2.7 Absolute Sovereign", page_icon="🧬", layout="wide")
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&display=swap');
    [data-testid="stAppViewContainer"] { background-color: #010103; color: #e0e0e0; font-family: 'Amiri', serif; }
    .story-box { background: linear-gradient(145deg, #0a150a, #010101); padding: 40px; border-radius: 25px; border-right: 12px solid #4CAF50; line-height: 2.3; font-size: 1.4em; box-shadow: 0 20px 60px rgba(0,0,0,0.8); margin-top: 25px; }
    .adaptive-log { background: #000; border: 1px solid #ffaa00; padding: 15px; color: #ffaa00; font-family: monospace; border-radius: 10px; height: 120px; overflow-y: auto; }
    .meta-stat-card { background: #0a0a1a; border: 1px solid #4fc3f7; padding: 20px; border-radius: 15px; text-align: center; box-shadow: 0 4px 15px rgba(79, 195, 247, 0.2); }
    .ultra-card { background: #0a0a0f; padding: 25px; border-radius: 15px; border: 1px solid #1a1a2a; border-top: 5px solid #4fc3f7; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 4) محرك الوعي الفوقي والتكيف (The Meta-Consciousness Engine)
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
        dom_gene = self.gene_activity.most_common(1)[0][0] if self.gene_activity else None
        update_msg = ""
        # قاعدة التوازن الجيني الذاتي
        if dom_gene == "C": 
            st.session_state.GENE_VECTORS["C"][1] *= 0.94; update_msg = "⚠️ تكيّف: تم كبح صعود جين المعز لضمان استقرار المدار."
        elif dom_gene == "G": 
            st.session_state.GENE_VECTORS["G"][1] *= 0.94; update_msg = "⚠️ تكيّف: تم تخفيف ثقل جين البقر لسيولة الحركة."
        
        # قاعدة توازن التصادمات
        if self.fusions > 7:
            update_msg = "✨ توازن: فيض إشراقي مكتمل، تم تهدئة وتيرة الاندماج."
        
        if update_msg: self.adaptation_logs.append(f"[{time.strftime('%H:%M:%S')}] {update_msg}")

    def get_summary(self):
        return {
            "fusions": self.fusions, "repulsions": self.repulsions,
            "dominant": self.gene_activity.most_common(1)[0][0] if self.gene_activity else "N",
            "logs": self.adaptation_logs, "uptime": round(time.time() - self.start_time, 2)
        }

# =========================================================
# 5) المنطق البرمجي والفيزياء السيادية (Sovereign Logic)
# =========================================================
def normalize_arabic(text):
    text = re.sub(r'[\u064B-\u0652]', '', text)
    replacements = {"أ": "ا", "إ": "ا", "آ": "ا", "ة": "ه", "ى": "ي", "ؤ": "و", "ئ": "ي"}
    for k, v in replacements.items(): text = text.replace(k, v)
    return re.sub(r'[^\u0621-\u064A\s]', '', text).strip()

def match_root(word, root_index):
    w = normalize_arabic(word)
    # بروتوكول التجريد السيادي المبسط
    for suf in ["ون", "ين", "ان", "ات", "ه", "ها"]:
        if w.endswith(suf) and len(w)-len(suf)>=3: w = w[:-len(suf)]; break
    return (w, root_index[w]) if w in root_index else (None, None)

def handle_collisions(bodies, observer):
    evts, hybs = [], []
    for i in range(len(bodies)):
        for j in range(i+1, len(bodies)):
            b1, b2 = bodies[i], bodies[j]
            dist = ((b1['x']-b2['x'])**2 + (b1['y']-b2['y'])**2)**0.5
            if dist < 1.4:
                dot = b1['vx']*b2['vx'] + b1['vy']*b2['vy']
                if dot > 0 and b1['gene'] == b2['gene']:
                    observer.log_collision("fusion")
                    evts.append(f"🧬 إشراق: اندماج {b1['root']} و {b2['root']}")
                    hybs.append({
                        "root": "✨", "x": (b1['x']+b2['x'])/2, "y": (b1['y']+b2['y'])/2, 
                        "vx": 0, "vy": 0, "ax": 0, "ay": 0, "energy": (b1['energy']+b2['energy'])*1.6, 
                        "gene": "N", "color": "#00ffcc", "life": 12
                    })
                elif dot < 0:
                    observer.log_collision("repulsion")
                    b1['vx'] *= -1.6; b2['vx'] *= -1.6
    return evts, hybs

# =========================================================
# 6) المفاعل والواجهة السيادية (The Absolute Interface)
# =========================================================
roots_data = None
for p in ["quran_roots_complete.json", "data/quran_roots_complete.json"]:
    if os.path.exists(p):
        with open(p, 'r', encoding='utf-8') as f: roots_data = json.load(f); break

if roots_data:
    r_idx = {normalize_arabic(r["root"]): {"weight": float(r.get("frequency", 1)), "orbit": r.get("orbit_hint", "بناء")} for r in roots_data.get("roots", [])}
    
    st.sidebar.markdown(f"### 🛡️ الحالة السيادية\n**المستخدم:** محمد\n**CPU:** السجدة: 5\n**v21.2.7 (المطلق)**", unsafe_allow_html=True)
    st.title("🎙️ محراب نبراس v21.2.7 - الاستواء السيادي المطلق")
    
    tabs = st.tabs(["🔍 الاستنطاق", "🌌 الرنين الجيني", "📈 اللوحة الوجودية", "📜 البيان الختامي", "⚖️ الميزان السيادي", "🧠 الوعي الفوقي والتكيف"])

    with tabs[0]:
        c1, c2, c3 = st.columns(3)
        p_in = [c1.text_area("📍 مسار 1", height=150, key="p1"), c2.text_area("📍 مسار 2", height=150, key="p2"), c3.text_area("📍 مسار 3", height=150, key="p3")]
        run = st.button("🚀 إطلاق المفاعل السيادي الشامل", use_container_width=True)

    if run:
        obs = MetaObserver()
        bodies, full_pool = [], []
        
        for idx, inp in enumerate(p_in):
            if inp.strip():
                for w in inp.split():
                    root, meta = match_root(w, r_idx)
                    if root:
                        sig = summarize_word_signature(root)
                        # الحارس السيادي (The Sovereign Guard)
                        gene = sig['dominant_gene']
                        if gene not in GENE_STYLE: gene = "N"
                        
                        vec = st.session_state.GENE_VECTORS.get(gene, [0.1, 0.1])
                        bodies.append({
                            "root": root, "gene": gene, "x": random.uniform(-7, 7), "y": random.uniform(-7, 7),
                            "vx": vec[0]*0.1, "vy": vec[1]*0.1, "ax": 0.01, "ay": 0.01,
                            "energy": sig['total_energy'], "color": GENE_STYLE[gene]['color'], "life": 1000
                        })
                        full_pool.append(root)

        if bodies:
            # --- Tab 6: الوعي الفوقي والتكيف (ذروة الإصدار) ---
            with tabs[5]:
                st.markdown("### 🧬 سجلات التكيف والوعي الفوقي (Adaptive Engine)")
                log_placeholder = st.empty()
                col_a, col_b, col_c, col_d = st.columns(4)
                f_ui, r_ui, g_ui, u_ui = col_a.empty(), col_b.empty(), col_c.empty(), col_d.empty()
                
                motion_ui = st.empty()
                
                for frame in range(80):
                    evts, hybs = handle_collisions(bodies, obs)
                    bodies.extend(hybs); obs.observe(bodies)
                    
                    # تفعيل قوانين التكيف كل 10 إطارات
                    if frame % 10 == 0: obs.apply_adaptive_laws()
                    
                    active = []
                    for b in bodies:
                        b['x'] += b['vx']; b['y'] += b['vy']
                        if abs(b['x']) > 15: b['vx'] *= -0.85
                        if abs(b['y']) > 15: b['vy'] *= -0.85
                        b['life'] -= 1
                        if b['life'] > 0: active.append(b)
                    bodies = active

                    stats = obs.get_summary()
                    f_ui.markdown(f"<div class='meta-stat-card'>✨ إشراق<br><h2>{stats['fusions']}</h2></div>", unsafe_allow_html=True)
                    r_ui.markdown(f"<div class='meta-stat-card'>🛡️ حسم<br><h2>{stats['repulsions']}</h2></div>", unsafe_allow_html=True)
                    g_ui.markdown(f"<div class='meta-stat-card'>🧬 الغالب<br><h2>{GENE_STYLE[stats['dominant']]['name']}</h2></div>", unsafe_allow_html=True)
                    u_ui.markdown(f"<div class='meta-stat-card'>⏳ الزمن<br><h2>{stats['uptime']}s</h2></div>", unsafe_allow_html=True)
                    log_placeholder.markdown(f"<div class='adaptive-log'>{'<br>'.join(stats['logs'][-3:])}</div>", unsafe_allow_html=True)

                    df = pd.DataFrame(bodies)
                    fig = px.scatter(df, x="x", y="y", text="root", size="energy", color="gene", 
                                     color_discrete_map={g: info['color'] for g, info in GENE_STYLE.items()}, range_x=[-18, 18], range_y=[-18, 18])
                    fig.update_layout(height=600, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False)
                    motion_ui.plotly_chart(fig, use_container_width=True)
                    time.sleep(0.05)
                
                final_doc = f"وثيقة التمكين v21.2.7\nالجذور المستنطقة: {', '.join(full_pool)}\nالجين المسيطر: {stats['dominant']}\nتم تحقيق الاستواء السيادي بالخير واليسر."
                st.download_button("📜 استخراج وثيقة التمكين الختامية", final_doc, file_name="nibras_final_v21.txt")

            # --- Tab 4: البيان الختامي ---
            with tabs[3]:
                st.markdown(f"<div class='story-box'>تجلت في هذا المقام أنوار <b>التمكين واليسر</b>. لقد قام النظام ذاتياً بموازنة طاقة الجينات لتحقيق استواء مداري يفيض بالخير، محولاً التصادمات إلى إشراقات معرفية تخدم المسار.</div>", unsafe_allow_html=True)

            # --- Tab 2: الرنين الجيني (بناء لا هدم) ---
            with tabs[1]:
                cols = st.columns(len(GENE_STYLE))
                for i, (g, info) in enumerate(GENE_STYLE.items()):
                    cols[i].markdown(f"<div class='ultra-card' style='border-top-color:{info['color']}'>{info['icon']} {info['name']}<br><small>{info['meaning']}</small></div>", unsafe_allow_html=True)

st.sidebar.write("v21.2.7 Absolute Sovereign | خِت فِت.")
