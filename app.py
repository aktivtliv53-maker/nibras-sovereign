# -*- coding: utf-8 -*-
# Nibras Sovereign v26.5 – The Unabridged Monolith
# الحالة: بناء تراكمي كامل | لا مساس بالهوية | لا هدم للنوافذ
# المرجع: وثيقة العرش للهندسة الوجودية - محمد (CPU: 32-5)

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import re, random, os, json, time, hashlib
from pathlib import Path

# =========================[ 1. CONFIG & SOVEREIGN IDENTITY ]==================
st.set_page_config(
    page_title="Nibras Sovereign v26.5",
    page_icon="🧿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# قاموس الجينات الوجودية (The Sovereign Genes)
GENE_STYLE = {
    'A': {'name': 'الإبل', 'color': '#4fc3f7', 'icon': '🐪', 'meaning': 'الفتح المداري'},
    'G': {'name': 'البقر', 'color': '#FFD700', 'icon': '🐄', 'meaning': 'التأسيس الراسخ'},
    'T': {'name': 'الضأن', 'color': '#4CAF50', 'icon': '🐑', 'meaning': 'السكينة الآمنة'},
    'C': {'name': 'المعز', 'color': '#ff5252', 'icon': '🐐', 'meaning': 'السمو الصاعد'},
    'N': {'name': 'إشراق', 'color': '#00ffcc', 'icon': '✨', 'meaning': 'الانبثاق الصافي'},
}

# =========================[ 2. SOVEREIGN ENGINE: LOGIC ]========================
def normalize_sovereign(text: str) -> str:
    if not text: return ""
    # إزالة التشكيل (اليسر والخير)
    text = re.sub(r'[\u0617-\u061A\u064B-\u0652\u0670]', '', str(text))
    # توحيد الحروف الوجودية (لا نكس بل مدارات مقلوبة)
    rep = {"أ":"ا","إ":"ا","آ":"ا","ة":"ه","ى":"ي","ؤ":"و","ئ":"ي"}
    for k, v in rep.items(): text = text.replace(k, v)
    text = re.sub(r'[^\u0621-\u064A\s]', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()

def extract_root_candidates(word: str, index_keys):
    """محرك استخراج الجذور السيادي المعتمد على هندسة الحرف العربي"""
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
    
    final_set = set()
    for c in candidates:
        final_set.add(c)
        if len(c) >= 3:
            for i in range(len(c)-2): final_set.add(c[i:i+3]) # المنطق المداري الثلاثي
            
    sorted_cands = sorted(list(final_set), key=lambda x: (-len(x), x))
    for cand in sorted_cands:
        if cand in index_keys:
            return cand, (0.98 if len(cand)==3 else 0.85), sorted_cands
            
    return None, 0.0, sorted_cands

# =========================[ 3. DATABASE: THE QURANIC MATRIX ]==================
@st.cache_data(show_spinner=False)
def load_nibras_matrix():
    # البحث في المسارات المحددة (Root and /data)
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
    .verse-res { background: #000; padding: 15px; border-radius: 8px; border-left: 3px solid #4fc3f7; margin-top: 10px; color: #4fc3f7; font-size: 1.1em; line-height: 1.6; }
</style>
""", unsafe_allow_html=True)

# =========================[ 5. MAIN SANCTUARY (THE INTERFACE) ]================
st.title("🛡️ مِحْرَاب نِبْرَاس السيادي v26.5")
st.write("---")

# منطقة الإدخال الفسيحة (تحرير المساحة من الشريط الجانبي)
main_input = st.text_area("أدخل المسار الوجودي أو الآيات للهندسة الكلية:", height=250, placeholder="اكتب هنا سوراً أو آيات لفك شفراتها الوجودية...")

col_btn1, col_btn2, col_btn3 = st.columns([2, 2, 1])
with col_btn1:
    trace_on = st.checkbox("تفعيل أثر الاستدلال (Trace)", value=True)
with col_btn2:
    run_monolith = st.button("🚀 تفعيل المونوليث السيادي", use_container_width=True)
with col_btn3:
    if st.button("🗑️ تطهير"): st.rerun()

# =========================[ 6. PROCESSING LOGIC ]==============================
if run_monolith and main_input:
    start_time = time.time()
    clean_path = normalize_sovereign(main_input)
    words = clean_path.split()
    
    analyzed_tokens = []
    for w in words:
        root, conf, trace = extract_root_candidates(w, r_index.keys())
        if root:
            # ربط المصفوفة (matrix_data.json)
            resonances = [v for v in matrix_db if root in normalize_sovereign(v.get('text', ''))][:3]
            analyzed_tokens.append({
                "word": w, "root": root, "conf": conf, "trace": trace, "verses": resonances,
                "gene": list(GENE_STYLE.keys())[sum(ord(c) for c in root) % 5]
            })
    
    # النوافذ الخمسة الكبرى (Full Restoration)
    t1, t2, t3, t4, t5 = st.tabs([
        "🪐 المدار البصري", 
        "🧬 الرنين الجيني", 
        "⚖️ التوازن السيادي", 
        "🧠 البيان الوجودي", 
        "🧿 المستشار القرآني"
    ])

    with t1: # المدار البصري (Full Physics)
        st.subheader("🪐 تمثيل المدارات الوجودية")
        if analyzed_tokens:
            plot_df = pd.DataFrame([{
                "x": random.uniform(-10,10), "y": random.uniform(-10,10),
                "root": t['root'], "gene": GENE_STYLE[t['gene']]['name'],
                "size": t['conf']*35, "color": GENE_STYLE[t['gene']]['color']
            } for t in analyzed_tokens])
            
            fig = px.scatter(plot_df, x="x", y="y", text="root", size="size", color="gene",
                             color_discrete_map={v['name']: v['color'] for v in GENE_STYLE.values()})
            fig.update_layout(height=650, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            fig.update_xaxes(visible=False); fig.update_yaxes(visible=False)
            st.plotly_chart(fig, use_container_width=True)

    with t2: # الرنين الجيني (Statistics)
        st.subheader("🧬 الهيمنة الجينية للمسار")
        counts = Counter([t['gene'] for t in analyzed_tokens])
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
        integrity = round((len(analyzed_tokens)/len(words))*100, 1) if words else 0
        duration = round(time.time() - start_time, 3)
        cm1, cm2, cm3 = st.columns(3)
        cm1.metric("درجة الثبات", f"{integrity}%")
        cm2.metric("زمن المفاعل", f"{duration}s")
        cm3.metric("الجذور النشطة", len(analyzed_tokens))
        st.divider()
        st.markdown(f"<div style='text-align:center; padding:30px; background:#051005; border-radius:15px; border:1px solid #1a3a1a;'><h3>القرار: {'مستقر ويقيني' if integrity > 75 else 'استكشافي'}</h3></div>", unsafe_allow_html=True)

    with t4: # البيان الوجودي (Mathematical Path)
        st.subheader("🧠 الهندسة الرمزية والبيان")
        eq = " ➔ ".join([f"<span style='color:{GENE_STYLE[t['gene']]['color']}'>{t['root']}</span>" for t in analyzed_tokens])
        st.markdown(f"<div style='font-size:1.8em; background:#111; padding:40px; border-radius:20px; text-align:center;'>{eq}</div>", unsafe_allow_html=True)

    with t5: # المستشار القرآني (Matrix Link)
        st.subheader("🧿 رنين المصفوفة السيادية (matrix_data.json)")
        for t in analyzed_tokens:
            with st.container():
                st.markdown(f"<div class='advisor-card'><span style='font-size:1.3em; color:#00ffcc;'>{t['word']}</span> ➔ <b>{t['root']}</b></div>", unsafe_allow_html=True)
                if t['verses']:
                    for v in t['verses']:
                        st.markdown(f"<div class='verse-res'>\"{v['text']}\" <br><small>— {v.get('surah')} [{v.get('verse')}]</small></div>", unsafe_allow_html=True)
                if trace_on:
                    st.caption(f"أثر القرار: {', '.join(t['trace'][:6])}...")
else:
    st.info("🧿 المفاعل في وضع الاستعداد. أدخل السور أو الآيات في المحراب أعلاه لتفعيل المونوليث v26.5.")

# =========================[ 8. FOOTER & SOVEREIGNTY ]==========================
st.sidebar.markdown("### 🛡️ نِبْرَاس v26.5")
st.sidebar.caption("Mohamed | Idris-Mohammed Link")
st.sidebar.write("CPU: Surah As-Sajdah [5]")
st.sidebar.write("---")
st.sidebar.write("خِت فِت.")
