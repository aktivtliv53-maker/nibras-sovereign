# -*- coding: utf-8 -*
# ==============================================================================
# نظام نِبْرَاس السيادي (Nibras Sovereign System) - الإصدار v26.1.0
# مَبنيٌّ على بروتوكول "لا مَسَاس" و "الاستحقاق الجيني" (Deterministic Physics)
# التشخيص: إنهاء العشوائية بربط الجين بالجذر | العلاج: الاستقرار المداري الشامل
# ==============================================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import re
import os
import json
import time
import hashlib

# ==============================================================================
# [1] مصفوفة الجينات السيادية الثابتة (The Sovereign Matrix)
# ==============================================================================
GENE_STYLE = {
    'A': {'name': 'الإبل', 'color': '#4fc3f7', 'icon': '🐪', 'meaning': 'اليسر والفتح'},
    'G': {'name': 'البقر', 'color': '#FFD700', 'icon': '🐄', 'meaning': 'الخير والتأسيس'},
    'T': {'name': 'الضأن', 'color': '#4CAF50', 'icon': '🐑', 'meaning': 'السكينة والمقام'},
    'C': {'name': 'المعز', 'color': '#ff5252', 'icon': '🐐', 'meaning': 'السمو والتمكين'},
    'N': {'name': 'إشراق', 'color': '#00ffcc', 'icon': '✨', 'meaning': 'الانبثاق الهجين'}
}

# ==============================================================================
# [2] محرك الاستحقاق الجيني (Deterministic Gene Engine)
# ==============================================================================
def summarize_word_signature(root):
    """تحويل الجذر إلى توقيع جيني ثابت غير عشوائي بناءً على قيم الحروف."""
    if not root: return {'dominant_gene': 'N', 'total_energy': 280.0}
    
    # حساب بصمة الجذر عبر Hash لضمان الثبات المطلق لنفس الجذر
    hash_val = int(hashlib.md5(root.encode()).hexdigest(), 16)
    genes = ['A', 'G', 'T', 'C']
    
    # تحديد الجين بناءً على باقي القسمة (ثبات رياضي)
    dominant_gene = genes[hash_val % 4]
    
    # حساب الطاقة بناءً على طول الجذر وموقعه في المصفوفة
    total_energy = float(len(root) * 280 + (hash_val % 100))
    
    return {
        'dominant_gene': dominant_gene,
        'total_energy': total_energy,
        'vector_x': (hash_val % 20 - 10) / 100.0,
        'vector_y': ((hash_val >> 4) % 20 - 10) / 100.0
    }

def normalize_sovereign(text):
    if not text: return ""
    text = re.sub(r'[\u064B-\u0652]', '', text)
    repls = {"أ": "ا", "إ": "ا", "آ": "ا", "ة": "ه", "ى": "ي"}
    for k, v in repls.items(): text = text.replace(k, v)
    return re.sub(r'[^\u0621-\u064A\s]', '', text).strip()

def match_root_sovereign(word, index_keys):
    w = normalize_sovereign(word)
    if not w or len(w) < 2: return None
    if w in index_keys: return w
    prefixes = ["ال", "و", "ف", "ب", "ك", "ل", "س"]
    suffixes = ["ون", "ين", "ان", "ات", "ه", "ها", "هم", "كم", "نا", "كما", "تم"]
    for p in prefixes:
        if w.startswith(p) and len(w)-len(p) >= 3:
            if w[len(p):] in index_keys: return w[len(p):]
    for s in suffixes:
        if w.endswith(s) and len(w)-len(s) >= 3:
            if w[:-len(s)] in index_keys: return w[:-len(s)]
    return w[:3] if len(w)>=3 and w[:3] in index_keys else None

# ==============================================================================
# [3] غلاف الاستقرار والتحصين (Mobile Shielding CSS)
# ==============================================================================
st.set_page_config(page_title="Nibras Sovereign v26.1", page_icon="🛡️", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&display=swap');
    [data-testid="stAppViewContainer"] { background: #010103; color: #e0e0e0; font-family: 'Amiri', serif; direction: rtl; }
    
    @media (max-width: 768px) {
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] { display: none !important; }
        [data-testid="stSidebar"] { width: 0px !important; min-width: 0px !important; }
        .main .block-container { padding: 10px !important; }
        .stTabs [data-baseweb="tab"] { font-size: 0.8em; padding: 4px; }
        .story-box { font-size: 1.2em; padding: 20px; }
    }

    .story-box { background: rgba(10,21,10,0.8); padding: 35px; border-radius: 20px; border-right: 12px solid #4CAF50; line-height: 2.4; font-size: 1.5em; box-shadow: 0 15px 40px rgba(0,0,0,0.6); }
    .stat-container { display: flex; justify-content: space-around; background: #0d0d14; padding: 25px; border-radius: 15px; border: 1px solid #1a1a2a; margin: 20px 0; }
    .stat-val { font-size: 2.5em; font-weight: bold; color: #00ffcc; }
    .log-entry { background: #000; border-right: 4px solid #4fc3f7; padding: 10px; margin-bottom: 5px; color: #4fc3f7; font-family: monospace; font-size: 0.9em; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# [4] إدارة حالة الوعي (Session Persistence)
# ==============================================================================
if 'sov_stable_state' not in st.session_state:
    st.session_state.sov_stable_state = {'active': False, 'bodies': [], 'pool': [], 'logs': [], 'metrics': {}}

roots_data = None
for p in ["quran_roots_complete.json", "data/quran_roots_complete.json"]:
    if os.path.exists(p):
        with open(p, 'r', encoding='utf-8') as f: roots_data = json.load(f); break
if not roots_data: st.error("⚠️ المفاعل معطل."); st.stop()
r_index = {normalize_sovereign(r["root"]): r for r in roots_data.get("roots", [])}

# ==============================================================================
# [5] المِحراب السداسي المستقر (Deterministic 6-Tab Architecture)
# ==============================================================================
tabs = st.tabs(["🔍 الاستنطاق المداري", "🌌 الرنين الجيني", "📈 اللوحة الوجودية", "📜 البيان الختامي", "⚖️ الميزان السيادي", "🧠 الوعي الفوقي"])

with tabs[0]:
    st.markdown("### 📍 هندسة المسارات (الربط السببي)")
    c1, c2, c3 = st.columns(3)
    p_texts = [c1.text_area("المسار 1", key="t1", height=120), c2.text_area("المسار 2", key="t2", height=120), c3.text_area("المسار 3", key="t3", height=120)]
    
    if st.button("🚀 تفعيل الاستقرار المداري", use_container_width=True):
        bodies, pool, logs = [], [], []
        start_t = time.time()
        
        for t in p_texts:
            if t.strip():
                for word in normalize_sovereign(t).split():
                    root = match_root_sovereign(word, r_index.keys())
                    if root:
                        # --- تطبيق قانون الاستحقاق (تعديل v26.1.0) ---
                        sig = summarize_word_signature(root)
                        gene = str(sig.get('dominant_gene', 'N')).upper()
                        energy = float(sig.get('total_energy', len(root)*280))
                        
                        bodies.append({
                            "root": root, "gene": gene, "energy": energy,
                            "x": random.uniform(-8,8), "y": random.uniform(-8,8),
                            "vx": sig['vector_x'], "vy": sig['vector_y'], # حركة مرتبطة بالجذر
                            "color": GENE_STYLE[gene]['color']
                        })
                        pool.append(root)

        if bodies:
            canvas = st.empty()
            for _ in range(100):
                for i in range(len(bodies)):
                    for j in range(i+1, len(bodies)):
                        d = ((bodies[i]['x']-bodies[j]['x'])**2 + (bodies[i]['y']-bodies[j]['y'])**2)**0.5
                        if d < 1.7 and bodies[i]['gene'] == bodies[j]['gene']:
                            logs.append(f"[{time.strftime('%H:%M:%S')}] إشراق محقق: {bodies[i]['root']} + {bodies[j]['root']}")
                for b in bodies:
                    b['x']+=b['vx']; b['y']+=b['vy']
                    if abs(b['x'])>25 or abs(b['y'])>25: b['vx']*=-1; b['vy']*=-1
                
                fig = px.scatter(pd.DataFrame(bodies), x="x", y="y", text="root", size="energy", color="gene",
                                 color_discrete_map={g:s['color'] for g,s in GENE_STYLE.items()}, range_x=[-30,30], range_y=[-30,30])
                fig.update_layout(height=700, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False, xaxis_visible=False, yaxis_visible=False)
                canvas.plotly_chart(fig, use_container_width=True)
                time.sleep(0.01)

            st.session_state.sov_stable_state = {
                'active': True, 'bodies': bodies, 'pool': list(set(pool)),
                'logs': list(dict.fromkeys(logs))[-15:], # آخر 15 حدث فريد
                'metrics': {"time": round(time.time()-start_t, 2), "count": len(bodies)}
            }
            st.rerun()

# --- تفعيل الطبقات (Execution) ---
state = st.session_state.sov_stable_state

with tabs[1]:
    st.markdown("### 🌌 مصفوفة الأصناف الجينية الثابتة")
    cols_g = st.columns(5)
    for i, (gk, gi) in enumerate(GENE_STYLE.items()):
        cols_g[i].markdown(f"<div style='background:#0d0d14; padding:20px; border-radius:15px; border-top:5px solid {gi['color']}; text-align:center;'><h4>{gi['icon']} {gi['name']}</h4><small>{gi['meaning']}</small></div>", unsafe_allow_html=True)

if state['active']:
    df = pd.DataFrame(state['bodies'])
    with tabs[2]:
        c1, c2 = st.columns(2)
        c1.plotly_chart(px.pie(df, names='gene', color='gene', color_discrete_map={g:s['color'] for g,s in GENE_STYLE.items()}, hole=0.4, title="توازن القوى"))
        c2.plotly_chart(px.bar(df, x='root', y='energy', color='gene', color_discrete_map={g:s['color'] for g,s in GENE_STYLE.items()}, title="طاقة الحروف"))
    with tabs[3]:
        st.markdown(f"<div class='story-box'><b>بيان الاستواء الوجودي:</b><br>تم استنطاق <b>{len(state['pool'])}</b> جذراً. النظام الآن في حالة <b>الخير واليسر</b> المستدام.</div>", unsafe_allow_html=True)
    with tabs[4]:
        st.dataframe(df[['root', 'gene', 'energy']], use_container_width=True)
    with tabs[5]:
        st.markdown(f"<div class='stat-container'><div class='stat-val'>{state['metrics']['count']}</div><div class='stat-val'>{state['metrics']['time']}s</div></div>", unsafe_allow_html=True)
        for log in state['logs']: st.markdown(f"<div class='log-entry'>{log}</div>", unsafe_allow_html=True)

st.sidebar.markdown(f"**المستخدم:** محمد | v26.1.0\n**البنية:** مستقرة (Deterministic)\n**خِت فِت.**")
