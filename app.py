# -*- coding: utf-8 -*-
# Nibras Sovereign v26.5 – The Quranic Matrix Restoration
# البروتوكول: استعادة نظام المقارنات الكلي | لا مساس بالنوافذ | الربط بالمصفوفة
# المرجع: وثيقة العرش - محمد (CPU: 32-5)

import streamlit as st
import pandas as pd
import plotly.express as px
import re, random, json, time
from pathlib import Path
from collections import Counter

# =========================[ 1. CONFIG & IDENTITY ]=============================
st.set_page_config(page_title="Nibras Sovereign v26.5", page_icon="🧿", layout="wide")

GENE_STYLE = {
    'A': {'name': 'الإبل', 'color': '#4fc3f7', 'icon': '🐪'},
    'G': {'name': 'البقر', 'color': '#FFD700', 'icon': '🐄'},
    'T': {'name': 'الضأن', 'color': '#4CAF50', 'icon': '🐑'},
    'C': {'name': 'المعز', 'color': '#ff5252', 'icon': '🐐'},
    'N': {'name': 'إشراق', 'color': '#00ffcc', 'icon': '✨'},
}

# =========================[ 2. SOVEREIGN ENGINE: COMPARISON LOGIC ]============
def normalize_sovereign(text: str) -> str:
    if not text: return ""
    text = re.sub(r'[\u0617-\u061A\u064B-\u0652\u0670]', '', str(text))
    rep = {"أ":"ا","إ":"ا","آ":"ا","ة":"ه","ى":"ي","ؤ":"و","ئ":"ي"}
    for k, v in rep.items(): text = text.replace(k, v)
    return re.sub(r'[^\u0621-\u064A\s]', ' ', text).strip()

@st.cache_data(show_spinner=False)
def load_databases():
    # المسارات السيادية للملفات
    r_p = Path("data/quran_roots_complete.json") if Path("data/quran_roots_complete.json").exists() else Path("quran_roots_complete.json")
    m_p = Path("data/matrix_data.json") if Path("data/matrix_data.json").exists() else Path("matrix_data.json")
    
    r_idx, m_db = {}, []
    if r_p.exists():
        with open(r_p, 'r', encoding='utf-8') as f:
            d = json.load(f)
            r_idx = {normalize_sovereign(r['root']): r for r in d.get("roots", []) if r.get('root')}
    if m_p.exists():
        with open(m_p, 'r', encoding='utf-8') as f: m_db = json.load(f)
    return r_idx, m_db

r_index, matrix_db = load_databases()

# =========================[ 3. UI STYLING ]====================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri&family=Orbitron&display=swap');
    [data-testid="stAppViewContainer"] { background: #050510; color: #e0e0e0; font-family: 'Amiri', serif; direction: rtl; }
    .stTabs [data-baseweb="tab-list"] { background: #111; padding: 12px; border-radius: 12px; border: 1px solid #222; }
    .stTabs [data-baseweb="tab"] { color: #777; font-size: 1.2em; padding: 10px 25px; }
    .stTabs [aria-selected="true"] { color: #00ffcc !important; border-bottom: 3px solid #00ffcc !important; }
    .comparison-card { background: rgba(0,255,204,0.02); border-right: 4px solid #00ffcc; padding: 20px; border-radius: 10px; margin-bottom: 15px; border-bottom: 1px solid #1a1a2e; }
    .verse-found { color: #4fc3f7; font-style: italic; margin-top: 10px; display: block; }
</style>
""", unsafe_allow_html=True)

# =========================[ 4. MAIN INTERFACE ]================================
st.title("🛡️ مِحْرَاب نِبْرَاس السيادي v26.5")

# منطقة الإدخال الفسيحة
input_text = st.text_area("أدخل الآيات أو المسار الوجودي للمقارنة والتحليل:", height=200, placeholder="اكتب هنا...")

if st.button("🚀 تفعيل المفاعل الكلي وإجراء المقارنات المصفوفية", use_container_width=True):
    if input_text:
        st.session_state.processed = True
        clean = normalize_sovereign(input_text)
        words = clean.split()
        
        results = []
        for w in words:
            # محرك الاستنباط (الدقة المزدوجة)
            root = None
            if w in r_index: root = w
            elif len(w) > 3 and w[1:] in r_index: root = w[1:]
            elif len(w) > 3 and w[2:] in r_index: root = w[2:]
            
            if root:
                # المقارنة بالمصفوفة القرآنية (matrix_data.json)
                matches = [v for v in matrix_db if root in normalize_sovereign(v.get('text',''))]
                results.append({
                    "word": w, "root": root, "matches": matches,
                    "gene": list(GENE_STYLE.keys())[sum(ord(c) for c in root) % 5]
                })
        st.session_state.results = results

# =========================[ 5. THE 5 SOVEREIGN TABS ]==========================
t1, t2, t3, t4, t5 = st.tabs(["🪐 المدار البصري", "🧬 الرنين الجيني", "⚖️ التوازن", "🧠 البيان الوجودي", "🧿 المستشار المقارن"])

if st.session_state.get('processed') and st.session_state.get('results'):
    res = st.session_state.results
    
    with t1: # المدار
        df = pd.DataFrame([{"x": random.uniform(-10,10), "y": random.uniform(-10,10), "root": r['root'], "gene": GENE_STYLE[r['gene']]['name']} for r in res])
        fig = px.scatter(df, x="x", y="y", text="root", color="gene", size_max=40, color_discrete_map={v['name']: v['color'] for v in GENE_STYLE.values()})
        fig.update_layout(height=600, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

    with t2: # الرنين
        counts = Counter([r['gene'] for r in res])
        cols = st.columns(5)
        for i, (gk, gv) in enumerate(GENE_STYLE.items()):
            cols[i].metric(f"{gv['icon']} {gv['name']}", counts.get(gk, 0))

    with t3: # التوازن
        st.subheader("⚖️ ميزان الاستقرار")
        st.write(f"تم ربط {len(res)} جذراً بالمصفوفة بنجاح.")
        st.progress(len(res)/len(input_text.split()) if input_text else 0)

    with t4: # الوجودي
        path = " ➔ ".join([f"[{r['root']}]" for r in res])
        st.success(path)

    with t5: # المستشار (نظام المقارنة الكلي)
        st.subheader("🧿 رنين المصفوفة القرآنية والمقارنات")
        for r in res:
            with st.container():
                st.markdown(f"""
                <div class="comparison-card">
                    <b style="color:#00ffcc; font-size:1.3em;">الكلمة: {r['word']}</b> ➔ <b>الجذر: {r['root']}</b>
                    <div style="margin-top:10px;"><b>عدد المقارنات المكتشفة: {len(r['matches'])}</b></div>
                </div>
                """, unsafe_allow_html=True)
                if r['matches']:
                    for v in r['matches'][:5]: # عرض أول 5 مقارنات لكل كلمة
                        st.markdown(f"<span class='verse-found'>• \"{v['text']}\" — {v.get('surah')} [{v.get('verse')}]</span>", unsafe_allow_html=True)
                st.divider()
else:
    st.info("🧿 المفاعل في وضع الاستعداد. أدخل النص واضغط تفعيل لإظهار المقارنات المدوية.")

st.sidebar.write("Mohamed | As-Sajdah [5]")
st.sidebar.write("خِت فِت.")
