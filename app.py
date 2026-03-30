# -*- coding: utf-8 -*-
# Nibras Sovereign v26.5 – The Absolute Monolith
# البروتوكول: بناء تراكمي سيادي | لا مساس بالهوية | لا هدم للنوافذ
# المرجع الأساسي: وثيقة العرش للهندسة الوجودية

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import re, random, os, json, time, hashlib
from pathlib import Path

# =========================[ 1. CONFIG & SOVEREIGN THEME ]======================
st.set_page_config(
    page_title="Nibras Sovereign v26.5",
    page_icon="🧿",
    layout="wide",
    initial_sidebar_state="expanded"
)

GENE_STYLE = {
    'A': {'name': 'الإبل', 'color': '#4fc3f7', 'icon': '🐪', 'meaning': 'الفتح المداري'},
    'G': {'name': 'البقر', 'color': '#FFD700', 'icon': '🐄', 'meaning': 'التأسيس الراسخ'},
    'T': {'name': 'الضأن', 'color': '#4CAF50', 'icon': '🐑', 'meaning': 'السكينة الآمنة'},
    'C': {'name': 'المعز', 'color': '#ff5252', 'icon': '🐐', 'meaning': 'السمو الصاعد'},
    'N': {'name': 'إشراق', 'color': '#00ffcc', 'icon': '✨', 'meaning': 'الانبثاق الصافي'},
}

# =========================[ 2. SESSION STATE MANAGEMENT ]======================
if 'monolith' not in st.session_state:
    st.session_state.monolith = {
        'active': False,
        'current_record': None,
        'history': [],
        'version': '26.5'
    }

m = st.session_state.monolith

# =========================[ 3. CORE ENGINES (NO DESTRUCTION) ]=================
def normalize_sovereign(text: str) -> str:
    if not text: return ""
    text = re.sub(r'[\u0617-\u061A\u064B-\u0652\u0670]', '', str(text)) # إزالة التشكيل
    rep = {"أ":"ا","إ":"ا","آ":"ا","ة":"ه","ى":"ي","ؤ":"و","ئ":"ي"}
    for k, v in rep.items(): text = text.replace(k, v)
    text = re.sub(r'[^\u0621-\u064A\s]', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()

def sovereign_match(word: str, index_keys):
    w = normalize_sovereign(word)
    if not w: return None, 0.0, []
    
    # محرك المرشحات السيادي (Root Candidate Engine)
    prefixes = ["وال", "فال", "بال", "كال", "لل", "ال", "و", "ف", "ب", "ك", "ل", "س"]
    suffixes = ["هما", "كما", "كم", "كن", "هم", "هن", "نا", "ها", "ه", "ات", "ان", "ون", "ين", "يه", "ية", "ي", "ة", "ا"]
    
    cands = {w}
    for p in prefixes:
        if w.startswith(p) and len(w)-len(p)>=2: cands.add(w[len(p):])
    for s in suffixes:
        for c in list(cands):
            if c.endswith(s) and len(c)-len(s)>=2: cands.add(c[:-len(s)])
    
    final_cands = set()
    for c in cands:
        final_cands.add(c)
        final_cands.add(re.sub(r'(.)\1+', r'\1', c)) # إزالة التضعيف
        if len(c) >= 3:
            for i in range(len(c)-2): final_cands.add(c[i:i+3]) # الثلاثيات المنزلقة
            
    sorted_cands = sorted(list(final_cands), key=lambda x: (-len(x), x))
    
    for cand in sorted_cands:
        if cand in index_keys:
            conf = 0.96 if len(cand) == 3 else 0.88
            return cand, conf, sorted_cands
            
    return None, 0.0, sorted_cands

# =========================[ 4. DATABASE LOADERS ]==============================
@st.cache_data(show_spinner=False)
def load_databases():
    # البحث عن ملف الجذور وملف المصفوفة matrix_data.json
    root_file = Path("data/quran_roots_complete.json") if Path("data/quran_roots_complete.json").exists() else Path("quran_roots_complete.json")
    matrix_file = Path("data/matrix_data.json") if Path("data/matrix_data.json").exists() else Path("matrix_data.json")
    
    r_data = {"roots": []}
    if root_file.exists():
        with open(root_file, 'r', encoding='utf-8') as f: r_data = json.load(f)
    
    m_data = []
    if matrix_file.exists():
        with open(matrix_file, 'r', encoding='utf-8') as f: m_data = json.load(f)
            
    r_index = {normalize_sovereign(r['root']): r for r in r_data.get("roots", []) if r.get('root')}
    return r_index, m_data

r_index, matrix_db = load_databases()

# =========================[ 5. UI STYLING ]====================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Orbitron:wght@500&display=swap');
    [data-testid="stAppViewContainer"] { background: radial-gradient(circle, #050512 0%, #000 100%); color: #e0e0e0; font-family: 'Amiri', serif; direction: rtl; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; background: rgba(255,255,255,0.03); padding: 12px; border-radius: 15px; border: 1px solid #1a1a2e; }
    .stTabs [data-baseweb="tab"] { border-radius: 10px; border: 1px solid #1a1a2e; color: #888; padding: 10px 20px; transition: 0.4s; font-size: 1.1em; }
    .stTabs [aria-selected="true"] { background: #00ffcc15 !important; border-color: #00ffcc !important; color: #fff !important; box-shadow: 0 0 15px #00ffcc33; }
    .advisor-card { background: rgba(0, 255, 204, 0.03); border-right: 5px solid #00ffcc; padding: 20px; border-radius: 12px; margin: 15px 0; border-bottom: 1px solid #1a1a2e; }
    .stat-val { font-family: 'Orbitron', sans-serif; color: #00ffcc; font-size: 2em; text-shadow: 0 0 10px #00ffcc55; }
    .verse-box { background: #08081a; padding: 15px; border-radius: 10px; border-left: 4px solid #4fc3f7; margin-top: 10px; font-style: italic; line-height: 1.6; }
    .verdict-container { background: #051005; border: 1px solid #1a3a1a; padding: 30px; border-radius: 20px; text-align: center; border-top: 6px solid #4CAF50; }
</style>
""", unsafe_allow_html=True)

# =========================[ 6. SIDEBAR CONTROLS ]==============================
with st.sidebar:
    st.markdown("## 🛡️ نِبْرَاس السيادي v26.5")
    st.divider()
    input_text = st.text_area("أدخل المسار الوجودي للتحليل:", height=200, placeholder="آية قرآنية أو نص سيادي...")
    
    c1, c2 = st.columns(2)
    with c1: op_mode = st.selectbox("الوضع:", ["Sovereign", "Ritual", "Lab"])
    with c2: show_trace = st.checkbox("أثر القرار", value=True)
    
    if st.button("🚀 تفعيل المفاعل v26.5", use_container_width=True):
        if input_text:
            start_t = time.time()
            clean = normalize_sovereign(input_text)
            tokens = []
            
            for w in clean.split():
                root, conf, trace = sovereign_match(w, r_index.keys())
                if root:
                    # الربط بالمصفوفة القرآنية (matrix_data.json)
                    hits = [v for v in matrix_db if root in normalize_sovereign(v.get('text',''))][:3]
                    
                    tokens.append({
                        "word": w, "root": root, "conf": conf, "trace": trace, "verses": hits,
                        "gene": list(GENE_STYLE.keys())[sum(ord(c) for c in root) % 4]
                    })

            # حفظ السجل المونوليثي
            record = {
                "id": f"SOV-{int(time.time())}",
                "timestamp": time.strftime("%H:%M:%S"),
                "input": input_text,
                "tokens": tokens,
                "metrics": {
                    "duration": round(time.time() - start_t, 3),
                    "integrity": round((len(tokens)/len(clean.split()))*100 if clean.split() else 0, 1)
                }
            }
            st.session_state.monolith['current_record'] = record
            st.session_state.monolith['active'] = True
            st.rerun()

    st.divider()
    st.caption("Mohamed CPU: As-Sajdah [5] | Idris-Mohammed Link")
    st.write("خِت فِت.")

# =========================[ 7. THE 5 SOVEREIGN TABS ]==========================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🪐 الاستدلال المداري", 
    "🧬 الرنين الجيني", 
    "⚖️ التوازن السيادي", 
    "🧠 البيان الوجودي", 
    "🧿 المستشار السيادي"
])

if st.session_state.monolith['active'] and st.session_state.monolith['current_record']:
    rec = st.session_state.monolith['current_record']
    
    with tab1: # المدار (البنية الأصلية المعززة)
        st.subheader("🪐 المدار الوجودي للجذور")
        if rec['tokens']:
            df = pd.DataFrame([{
                "x": random.uniform(-10,10), "y": random.uniform(-10,10),
                "root": t['root'], "gene": GENE_STYLE[t['gene']]['name'],
                "size": t['conf']*25, "color": GENE_STYLE[t['gene']]['color']
            } for t in rec['tokens']])
            
            fig = px.scatter(df, x="x", y="y", text="root", size="size", color="gene",
                             color_discrete_map={v['name']: v['color'] for v in GENE_STYLE.values()})
            fig.update_layout(height=600, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=True)
            fig.update_xaxes(visible=False); fig.update_yaxes(visible=False)
            st.plotly_chart(fig, use_container_width=True)

    with tab2: # الرنين (البنية الأصلية المعززة)
        st.subheader("🧬 الرنين الجيني للمسار")
        counts = Counter([t['gene'] for t in rec['tokens']])
        cols = st.columns(5)
        for i, (gk, gv) in enumerate(GENE_STYLE.items()):
            with cols[i]:
                st.markdown(f"""
                <div style="text-align:center; border:1px solid {gv['color']}; padding:20px; border-radius:15px; background:rgba(255,255,255,0.02);">
                    <div style="font-size:2.5em;">{gv['icon']}</div>
                    <div style="color:{gv['color']}; font-weight:bold; font-size:1.2em;">{gv['name']}</div>
                    <div class="stat-val">{counts.get(gk, 0)}</div>
                </div>
                """, unsafe_allow_html=True)

    with tab3: # التوازن (البنية الأصلية المعززة)
        st.subheader("⚖️ ميزان الاستقرار المعرفي")
        integrity = rec['metrics']['integrity']
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("ثبات المسار", f"{integrity}%")
        col_m2.metric("زمن المفاعل", f"{rec['metrics']['duration']}s")
        col_m3.metric("كلمات المعالجة", len(rec['input'].split()))
        
        st.markdown(f"""
        <div class="verdict-container">
            <h2 style="color:#4CAF50;">القرار: {'قابل للاعتماد البحثي' if integrity > 70 else 'استكشافي'}</h2>
            <p>تم استنباط {len(rec['tokens'])} جذراً سيادياً من المصفوفة بنجاح.</p>
        </div>
        """, unsafe_allow_html=True)

    with tab4: # الوجودي (البيان الكلي)
        st.subheader("🧠 الهندسة الرمزية والبيان الوجودي")
        st.write("المعادلة الوجودية المتشكلة لهذا المسار:")
        equation = " ➔ ".join([f"<span style='color:{GENE_STYLE[t['gene']]['color']}'>{t['root']}</span>" for t in rec['tokens']])
        st.markdown(f"<div style='font-size:1.8em; background:#111; padding:30px; border-radius:15px; text-align:center;'>{equation}</div>", unsafe_allow_html=True)

    with tab5: # المستشار السيادي (الإضافة التراكمية - الربط بالمصفوفة)
        st.subheader("🧿 المستشار السيادي ورنين المصفوفة")
        for t in rec['tokens']:
            with st.container():
                st.markdown(f"""
                <div class="advisor-card">
                    <span style="font-size:1.3em; color:#00ffcc;">{t['word']}</span> ➔ 
                    <b>جذر {t['root']}</b> | <small>الثقة: {t['conf']}</small>
                </div>
                """, unsafe_allow_html=True)
                
                if t['verses']:
                    for v in t['verses']:
                        st.markdown(f"""<div class="verse-box">"{v['text']}" <br> <small>— {v.get('surah')} [آية {v.get('verse')}]</small></div>""", unsafe_allow_html=True)
                
                if show_trace:
                    st.caption(f"مسار التتبع: {', '.join(t['trace'][:8])}...")
else:
    st.info("🧿 المفاعل في وضع الاستعداد السيادي. أدخل المسار في القائمة الجانبية لتنشيط المونوليث v26.5.")

# =========================[ 8. FOOTER ]========================================
st.sidebar.markdown("---")
st.sidebar.write("خِت فِت.")
