# -*- coding: utf-8 -*-
# Nibras Sovereign v26.5 – The Full Existential Matrix
# البروتوكول: استعادة الهيبة الكاملة | لا مساس بالبنية | بناء تراكمي سيادي
# المرجع: وثيقة العرش للهندسة الوجودية - محمد (CPU: 32-5)

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import re, random, os, json, time, hashlib
from pathlib import Path

# =========================[ 1. CONFIG & VISUAL IDENTITY ]======================
st.set_page_config(
    page_title="Nibras Sovereign v26.5",
    page_icon="🧿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# قاموس الجينات الوجودية (The Sovereign Genes)
GENE_STYLE = {
    'A': {'name': 'الإبل', 'color': '#4fc3f7', 'icon': '🐪', 'meaning': 'الفتح المداري - السمو'},
    'G': {'name': 'البقر', 'color': '#FFD700', 'icon': '🐄', 'meaning': 'التأسيس الراسخ - المادة'},
    'T': {'name': 'الضأن', 'color': '#4CAF50', 'icon': '🐑', 'meaning': 'السكينة الآمنة - الروح'},
    'C': {'name': 'المعز', 'color': '#ff5252', 'icon': '🐐', 'meaning': 'السمو الصاعد - القوة'},
    'N': {'name': 'إشراق', 'color': '#00ffcc', 'icon': '✨', 'meaning': 'الانبثاق الصافي - النور'},
}

# =========================[ 2. SOVEREIGN ENGINE: LOGIC ]========================
def normalize_sovereign(text: str) -> str:
    if not text: return ""
    # إزالة التشكيل والرموز (حفظاً للبنية)
    text = re.sub(r'[\u0617-\u061A\u064B-\u0652\u0670]', '', str(text))
    # توحيد الحروف الوجودية (الهمزات والياءات)
    rep = {"أ":"ا","إ":"ا","آ":"ا","ة":"ه","ى":"ي","ؤ":"و","ئ":"ي"}
    for k, v in rep.items(): text = text.replace(k, v)
    text = re.sub(r'[^\u0621-\u064A\s]', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()

def extract_root_candidates(word: str, index_keys):
    """محرك استخراج الجذور السيادي دون هدم المعنى"""
    w = normalize_sovereign(word)
    if not w or len(w) < 2: return None, 0.0, []
    
    prefixes = ["وال", "فال", "بال", "كال", "لل", "ال", "و", "ف", "ب", "ك", "ل", "س"]
    suffixes = ["هما", "كما", "كم", "كن", "هم", "هن", "نا", "ها", "ه", "ات", "ان", "ون", "ين", "يه", "ية", "ي", "ة", "ا"]
    
    candidates = {w}
    for p in prefixes:
        if w.startswith(p) and len(w)-len(p) >= 2: candidates.add(w[len(p):])
    for s in suffixes:
        for c in list(candidates):
            if c.endswith(s) and len(c)-len(s) >= 2: candidates.add(c[:-len(s)])
    
    # فلترة نهائية وتوليد الثلاثيات
    final_set = set()
    for c in candidates:
        final_set.add(c)
        if len(c) >= 3:
            for i in range(len(c)-2): final_set.add(c[i:i+3])
    
    sorted_cands = sorted(list(final_set), key=lambda x: (-len(x), x))
    
    for cand in sorted_cands:
        if cand in index_keys:
            conf = 0.98 if len(cand) == 3 else 0.85
            return cand, conf, sorted_cands
            
    return None, 0.0, sorted_cands

# =========================[ 3. DATABASE: THE MATRIX ]==========================
@st.cache_data(show_spinner=False)
def load_nibras_matrix():
    # البحث عن ملف الجذور وملف المصفوفة matrix_data.json
    r_path = Path("data/quran_roots_complete.json") if Path("data/quran_roots_complete.json").exists() else Path("quran_roots_complete.json")
    m_path = Path("data/matrix_data.json") if Path("data/matrix_data.json").exists() else Path("matrix_data.json")
    
    roots_idx = {}
    if r_path.exists():
        with open(r_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            roots_idx = {normalize_sovereign(r['root']): r for r in data.get("roots", []) if r.get('root')}
    
    matrix_list = []
    if m_path.exists():
        with open(m_path, 'r', encoding='utf-8') as f:
            matrix_list = json.load(f)
            
    return roots_idx, matrix_list

r_index, matrix_db = load_nibras_matrix()

# =========================[ 4. UI: THE SOVEREIGN STYLE ]=======================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Orbitron:wght@500&display=swap');
    [data-testid="stAppViewContainer"] { background: radial-gradient(circle, #050510 0%, #000 100%); color: #e0e0e0; font-family: 'Amiri', serif; direction: rtl; }
    .stTabs [data-baseweb="tab-list"] { background: rgba(20, 20, 40, 0.6); padding: 15px; border-radius: 15px; border: 1px solid #1a1a3a; gap: 10px; }
    .stTabs [data-baseweb="tab"] { border-radius: 8px; border: 1px solid #1a1a3a; color: #888; font-size: 1.2em; transition: 0.3s; padding: 10px 20px; }
    .stTabs [aria-selected="true"] { background: #00ffcc10 !important; border-color: #00ffcc !important; color: #fff !important; box-shadow: 0 0 15px #00ffcc22; }
    .advisor-card { background: rgba(0, 255, 204, 0.05); border-right: 5px solid #00ffcc; padding: 20px; border-radius: 12px; margin: 15px 0; border-bottom: 1px solid #1a1a2e; }
    .stat-box { background: #0a0a1a; padding: 20px; border-radius: 15px; text-align: center; border: 1px solid #1a1a3a; }
    .verse-text { background: #000; padding: 15px; border-radius: 8px; border-left: 3px solid #4fc3f7; margin-top: 10px; color: #4fc3f7; font-size: 1.1em; }
</style>
""", unsafe_allow_html=True)

# =========================[ 5. SIDEBAR & INPUT ]===============================
with st.sidebar:
    st.title("🛡️ مِحْرَاب نِبْرَاس")
    st.divider()
    input_text = st.text_area("أدخل المسار الوجودي الكامل:", height=250, placeholder="أدخل آيات سورة السجدة أو أي مسار استبصاري...")
    
    col_a, col_b = st.columns(2)
    with col_a: op_mode = st.selectbox("وضع المفاعل:", ["Sovereign", "Ritual", "Lab"])
    with col_b: trace_on = st.checkbox("أثر الاستدلال", value=True)
    
    run_btn = st.button("🚀 تفعيل المونوليث v26.5", use_container_width=True)
    st.divider()
    st.caption("Mohamed CPU: Surah As-Sajdah [5]")
    st.write("خِت فِت.")

# =========================[ 6. PROCESSING LOGIC ]==============================
if run_btn and input_text:
    start_time = time.time()
    clean_path = normalize_sovereign(input_text)
    words = clean_path.split()
    
    analyzed_tokens = []
    for w in words:
        root, conf, trace = extract_root_candidates(w, r_index.keys())
        if root:
            # ربط المصفوفة (Matrix Linking)
            resonances = [v for v in matrix_db if root in normalize_sovereign(v.get('text', ''))][:3]
            analyzed_tokens.append({
                "word": w, "root": root, "conf": conf, "trace": trace, "verses": resonances,
                "gene": list(GENE_STYLE.keys())[sum(ord(c) for c in root) % 5]
            })
    
    st.session_state.current_analysis = {
        "tokens": analyzed_tokens,
        "input": input_text,
        "duration": round(time.time() - start_time, 3),
        "integrity": round((len(analyzed_tokens)/len(words))*100, 1) if words else 0
    }

# =========================[ 7. THE 5 SOVEREIGN TABS ]==========================
t1, t2, t3, t4, t5 = st.tabs([
    "🪐 المدار البصري", 
    "🧬 الرنين الجيني", 
    "⚖️ التوازن السيادي", 
    "🧠 البيان الوجودي", 
    "🧿 المستشار القرآني"
])

if 'current_analysis' in st.session_state:
    data = st.session_state.current_analysis
    
    with t1: # المدار البصري (Full Physics)
        st.subheader("🪐 تمثيل المدارات الوجودية")
        if data['tokens']:
            plot_df = pd.DataFrame([{
                "x": random.uniform(-10,10), "y": random.uniform(-10,10),
                "root": t['root'], "gene": GENE_STYLE[t['gene']]['name'],
                "size": t['conf']*30, "color": GENE_STYLE[t['gene']]['color']
            } for t in data['tokens']])
            
            fig = px.scatter(plot_df, x="x", y="y", text="root", size="size", color="gene",
                             color_discrete_map={v['name']: v['color'] for v in GENE_STYLE.values()})
            fig.update_layout(height=650, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            fig.update_xaxes(visible=False); fig.update_yaxes(visible=False)
            st.plotly_chart(fig, use_container_width=True)

    with t2: # الرنين الجيني (Statistics)
        st.subheader("🧬 الهيمنة الجينية للمسار")
        counts = Counter([t['gene'] for t in data['tokens']])
        cols = st.columns(5)
        for i, (gk, gv) in enumerate(GENE_STYLE.items()):
            with cols[i]:
                st.markdown(f"""
                <div class="stat-box" style="border-top: 4px solid {gv['color']};">
                    <div style="font-size:2.5em;">{gv['icon']}</div>
                    <div style="color:{gv['color']}; font-weight:bold;">{gv['name']}</div>
                    <div style="font-size:2em; font-family:'Orbitron';">{counts.get(gk, 0)}</div>
                </div>
                """, unsafe_allow_html=True)

    with t3: # التوازن السيادي (Metrics)
        st.subheader("⚖️ ميزان الاستقرار المعرفي")
        cm1, cm2, cm3 = st.columns(3)
        cm1.metric("درجة الثبات", f"{data['integrity']}%")
        cm2.metric("زمن المفاعل", f"{data['duration']}s")
        cm3.metric("الجذور النشطة", len(data['tokens']))
        st.divider()
        st.markdown(f"""
        <div style="text-align:center; padding:40px; border:1px solid #1a3a1a; background:#051005; border-radius:20px;">
            <h3>القرار السيادي النهائي</h3>
            <p style="font-size:1.4em;">المسار {'مستقر ويقيني' if data['integrity'] > 75 else 'استكشافي ومرن'}</p>
        </div>
        """, unsafe_allow_html=True)

    with t4: # البيان الوجودي (Mathematical Path)
        st.subheader("🧠 هندسة الحرف والبيان الوجودي")
        eq = " ➔ ".join([f"<span style='color:{GENE_STYLE[t['gene']]['color']}'>{t['root']}</span>" for t in data['tokens']])
        st.markdown(f"<div style='font-size:2em; background:#111; padding:40px; border-radius:20px; text-align:center;'>{eq}</div>", unsafe_allow_html=True)

    with t5: # المستشار القرآني (Matrix Link)
        st.subheader("🧿 رنين المصفوفة السيادية")
        for t in data['tokens']:
            with st.container():
                st.markdown(f"""
                <div class="advisor-card">
                    <span style="font-size:1.4em; color:#00ffcc;">{t['word']}</span> ➔ 
                    <b>الجذر الوجودي: {t['root']}</b>
                </div>
                """, unsafe_allow_html=True)
                if t['verses']:
                    for v in t['verses']:
                        st.markdown(f"<div class='verse-text'>\"{v['text']}\" <br><small>— {v.get('surah')} [{v.get('verse')}]</small></div>", unsafe_allow_html=True)
                if trace_on:
                    st.caption(f"مسار الاستدلال: {', '.join(t['trace'][:6])}...")
else:
    st.info("🧿 المفاعل في وضع الاستعداد. أدخل النص في القائمة الجانبية لتنشيط المونوليث v26.5.")

# =========================[ 8. FINAL FOOTER ]==================================
st.divider()
st.write("خِت فِت. | نِبْرَاس v26.5 - النسخة الكاملة")
