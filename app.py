# -*- coding: utf-8 -*-
# Nibras Sovereign v26.5 – The Iron Monolith
# البروتوكول: بناء تراكمي صلب | لا مساس بالهوية | النوافذ مفتوحة دائماً
# المرجع: وثيقة العرش (32-5) - المستخدم: محمد

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import re, random, os, json, time, hashlib
from pathlib import Path

# =========================[ 1. CONFIG & SOVEREIGN IDENTITY ]==================
st.set_page_config(page_title="Nibras Sovereign v26.5", page_icon="🧿", layout="wide")

GENE_STYLE = {
    'A': {'name': 'الإبل', 'color': '#4fc3f7', 'icon': '🐪'},
    'G': {'name': 'البقر', 'color': '#FFD700', 'icon': '🐄'},
    'T': {'name': 'الضأن', 'color': '#4CAF50', 'icon': '🐑'},
    'C': {'name': 'المعز', 'color': '#ff5252', 'icon': '🐐'},
    'N': {'name': 'إشراق', 'color': '#00ffcc', 'icon': '✨'},
}

# =========================[ 2. SOVEREIGN ENGINE: LOGIC ]========================
def normalize_sovereign(text: str) -> str:
    if not text: return ""
    text = re.sub(r'[\u0617-\u061A\u064B-\u0652\u0670]', '', str(text))
    rep = {"أ":"ا","إ":"ا","آ":"ا","ة":"ه","ى":"ي","ؤ":"و","ئ":"ي"}
    for k, v in rep.items(): text = text.replace(k, v)
    return re.sub(r'[^\u0621-\u064A\s]', ' ', text).strip()

def extract_roots(word: str, index_keys):
    w = normalize_sovereign(word)
    if not w or len(w) < 2: return None
    prefixes = ["وال", "فال", "بال", "ال", "و", "ف", "ب", "ل"]
    cands = [w]
    for p in prefixes:
        if w.startswith(p) and len(w) > 3: cands.append(w[len(p):])
    for c in cands:
        if c in index_keys: return c
        if len(c) > 3 and c[:3] in index_keys: return c[:3]
    return None

# =========================[ 3. DATABASE: LOADING ]=============================
@st.cache_data(show_spinner=False)
def load_system():
    r_p = Path("data/quran_roots_complete.json") if Path("data/quran_roots_complete.json").exists() else Path("quran_roots_complete.json")
    m_p = Path("data/matrix_data.json") if Path("data/matrix_data.json").exists() else Path("matrix_data.json")
    
    r_idx = {}
    if r_p.exists():
        with open(r_p, 'r', encoding='utf-8') as f:
            d = json.load(f)
            r_idx = {normalize_sovereign(r['root']): r for r in d.get("roots", []) if r.get('root')}
    
    m_db = []
    if m_p.exists():
        with open(m_p, 'r', encoding='utf-8') as f: m_db = json.load(f)
    return r_idx, m_db

r_index, matrix_db = load_system()

# =========================[ 4. UI STYLING ]====================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri&family=Orbitron&display=swap');
    [data-testid="stAppViewContainer"] { background: #000; color: #e0e0e0; font-family: 'Amiri', serif; direction: rtl; }
    .stTabs [data-baseweb="tab-list"] { background: #111; padding: 12px; border-radius: 12px; border: 1px solid #222; width: 100%; }
    .stTabs [data-baseweb="tab"] { color: #888; font-size: 1.2em; padding: 10px 25px; }
    .stTabs [aria-selected="true"] { color: #00ffcc !important; border-bottom: 3px solid #00ffcc !important; }
    .advisor-box { background: rgba(0,255,204,0.03); border-right: 4px solid #00ffcc; padding: 15px; margin: 10px 0; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# =========================[ 5. MAIN INTERFACE ]================================
st.title("🛡️ مِحْرَاب نِبْرَاس السيادي v26.5")

# منطقة الإدخال الفسيحة دائماً في الأعلى
main_input = st.text_area("أدخل المسار الوجودي (الآيات أو السور):", height=200)
active_btn = st.button("🚀 تفعيل المفاعل الكلي واستخراج المدارات", use_container_width=True)

# =========================[ 6. PERSISTENT TABS ]===============================
# النوافذ مفتوحة دائماً، المحتوى هو الذي يتغير بناءً على الإدخال
t1, t2, t3, t4, t5 = st.tabs(["🪐 المدار البصري", "🧬 الرنين الجيني", "⚖️ التوازن", "🧠 البيان الوجودي", "🧿 المستشار"])

if active_btn and main_input:
    clean_text = normalize_sovereign(main_input)
    words = clean_text.split()
    results = []
    
    for w in words:
        root = extract_roots(w, r_index.keys())
        if root:
            # الربط بملف matrix_data.json
            resonances = [v for v in matrix_db if root in normalize_sovereign(v.get('text', ''))][:3]
            results.append({
                "word": w, "root": root, "verses": resonances,
                "gene": list(GENE_STYLE.keys())[sum(ord(c) for c in root) % 5]
            })

    with t1: # المدار
        df = pd.DataFrame([{"x": random.uniform(-10,10), "y": random.uniform(-10,10), "root": r['root'], "gene": GENE_STYLE[r['gene']]['name']} for r in results])
        if not df.empty:
            fig = px.scatter(df, x="x", y="y", text="root", color="gene", size_max=40, color_discrete_map={v['name']: v['color'] for v in GENE_STYLE.values()})
            fig.update_layout(height=600, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)

    with t2: # الرنين
        counts = Counter([r['gene'] for r in results])
        cols = st.columns(5)
        for i, (gk, gv) in enumerate(GENE_STYLE.items()):
            cols[i].metric(f"{gv['icon']} {gv['name']}", counts.get(gk, 0))

    with t3: # التوازن
        st.metric("الجذور المكتشفة", len(results), f"من أصل {len(words)} كلمة")
        st.progress(len(results)/len(words) if words else 0)

    with t4: # الوجودي
        st.success(" ➔ ".join([f"[{r['root']}]" for r in results]))

    with t5: # المستشار
        for r in results:
            if r['verses']:
                with st.expander(f"الجذر: {r['root']} | {r['word']}"):
                    for v in r['verses']:
                        st.markdown(f"<div class='advisor-box'>{v['text']}<br><small>{v.get('surah')} [{v.get('verse')}]</small></div>", unsafe_allow_html=True)
else:
    with t1: st.info("بانتظار تفعيل المفاعل...")
    with t2: st.info("بانتظار تفعيل المفاعل...")
    with t3: st.info("بانتظار تفعيل المفاعل...")
    with t4: st.info("بانتظار تفعيل المفاعل...")
    with t5: st.info("بانتظار تفعيل المفاعل...")

st.sidebar.write("Mohamed | As-Sajdah [5]")
st.sidebar.write("خِت فِت.")
