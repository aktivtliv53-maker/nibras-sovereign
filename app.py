# -*- coding: utf-8 -*-
# Nibras Sovereign v26.5 – The Quranic Monolith (The Final Edition)
# Author: Mohamed & Al-Tair (Gemini)
# Status: Architectural Lockdown (No Modification Beyond This Point)

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import re, random, os, json, time, hashlib
from pathlib import Path

# =========================[ 1. CONFIG & THEME ]================================
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

# =========================[ 2. STATE INITIALIZATION ]==========================
if 'monolith' not in st.session_state:
    st.session_state.monolith = {
        'active': False,
        'mode': 'Sovereign', 
        'current_record': None,
        'history': [],
        'resolved_ambiguities': {},
        'logs': [],
        'metrics': {},
        'version': '26.5'
    }

m = st.session_state.monolith

# =========================[ 3. ENGINE: NORMALIZATION ]=========================
def normalize_sovereign(text: str) -> str:
    if not text: return ""
    # إزالة التشكيل الشامل
    text = re.sub(r'[\u0617-\u061A\u064B-\u0652\u0670]', '', str(text))
    # توحيد الحروف الوجودية
    rep = {"أ":"ا","إ":"ا","آ":"ا","ة":"ه","ى":"ي","ؤ":"و","ئ":"ي"}
    for k, v in rep.items(): text = text.replace(k, v)
    # تنظيف الرموز
    text = re.sub(r'[^\u0621-\u064A\s]', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()

# =========================[ 4. ENGINE: ROOT CANDIDATES ]=======================
PREFIXES = ["وال", "فال", "بال", "كال", "لل", "ال", "و", "ف", "ب", "ك", "ل", "س"]
SUFFIXES = ["هما", "كما", "كم", "كن", "هم", "هن", "نا", "ها", "ه", "ات", "ان", "ون", "ين", "يه", "ية", "ي", "ة", "ا"]

def generate_candidates(word: str):
    w = normalize_sovereign(word)
    if not w: return []
    cands = {w}
    # إزالة الزوائد المركبة
    for p in PREFIXES: 
        if w.startswith(p) and len(w)-len(p)>=2: cands.add(w[len(p):])
    for s in SUFFIXES:
        for c in list(cands):
            if c.endswith(s) and len(c)-len(s)>=2: cands.add(c[:-len(s)])
    # الفلترة النهائية والثلاثيات المنزلقة
    final = set()
    for c in cands:
        final.add(c)
        final.add(re.sub(r'(.)\1+', r'\1', c)) # إزالة التضعيف
        if len(c) >= 3:
            for i in range(len(c)-2): final.add(c[i:i+3])
    return sorted([x for x in final if 2<=len(x)<=6], key=lambda x: (-len(x), x))

# =========================[ 5. ENGINE: SOVEREIGN MATCH ]=======================
def sovereign_match(word: str, index_keys):
    cands = generate_candidates(word)
    for c in cands:
        if c in index_keys:
            conf = 0.96 if len(c) == 3 else 0.88
            return {"root": c, "conf": conf, "method": f"Match via {c}", "trace": cands}
    return {"root": None, "conf": 0.0, "method": "No Match", "trace": cands}

# =========================[ 6. LOAD DATABASES (ROOTS & MATRIX) ]===============
@st.cache_data(show_spinner=False)
def load_all_dbs():
    # 1. تحميل ملف الجذور
    roots_path = Path("data/quran_roots_complete.json") if Path("data/quran_roots_complete.json").exists() else Path("quran_roots_complete.json")
    roots_data = {"roots": []}
    if roots_path.exists():
        with open(roots_path, 'r', encoding='utf-8') as f:
            roots_data = json.load(f)
    
    # 2. تحميل ملف المصفوفة القرآنية (matrix_data.json)
    matrix_path = Path("data/matrix_data.json") if Path("data/matrix_data.json").exists() else Path("matrix_data.json")
    matrix_text = []
    if matrix_path.exists():
        with open(matrix_path, 'r', encoding='utf-8') as f:
            matrix_text = json.load(f)
            
    r_index = {normalize_sovereign(r['root']): r for r in roots_data.get("roots", []) if r.get('root')}
    return r_index, matrix_text, str(matrix_path)

r_index, quran_db, matrix_info = load_all_dbs()

# =========================[ 7. UI CSS ]========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Orbitron:wght@500&display=swap');
    [data-testid="stAppViewContainer"] { background: radial-gradient(circle, #050510 0%, #000 100%); color: #e0e0e0; font-family: 'Amiri', serif; direction: rtl; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; background: rgba(255,255,255,0.03); padding: 10px; border-radius: 12px; }
    .stTabs [data-baseweb="tab"] { border-radius: 8px; border: 1px solid #1a1a2a; color: #aaa; transition: 0.3s; }
    .stTabs [aria-selected="true"] { background: #00ffcc22 !important; border-color: #00ffcc !important; color: #fff !important; }
    .advisor-card { background: rgba(0, 255, 204, 0.05); border-right: 4px solid #00ffcc; padding: 15px; border-radius: 10px; margin: 8px 0; }
    .verdict-box { background: linear-gradient(135deg, #051005, #000); border: 1px solid #183c25; padding: 25px; border-radius: 15px; text-align: center; border-top: 5px solid #4CAF50; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
    .stat-val { font-family: 'Orbitron', sans-serif; color: #00ffcc; font-size: 1.8em; font-weight: bold; }
    .verse-box { background: #0a0a1a; padding: 15px; border-radius: 8px; border-left: 3px solid #4fc3f7; margin-top: 10px; font-style: italic; font-size: 1.1em; }
</style>
""", unsafe_allow_html=True)

# =========================[ 8. SIDEBAR CONTROLS ]==============================
with st.sidebar:
    st.markdown("### 🛡️ مفاعل نِبْرَاس v26.5")
    input_text = st.text_area("أدخل النص السيادي للتحليل:", height=180, placeholder="آية قرآنية أو جملة وجودية...")
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        op_mode = st.selectbox("الوضع:", ["Sovereign", "Ritual", "Lab"])
    with col_s2:
        show_trace = st.checkbox("أثر القرار", value=True)
    
    if st.button("🚀 تفعيل المونوليث", use_container_width=True):
        if input_text:
            start_t = time.time()
            clean = normalize_sovereign(input_text)
            tokens = []
            
            for w in clean.split():
                res = sovereign_match(w, r_index.keys())
                if res['root']:
                    # محرك الربط بالمصفوفة القرآنية
                    related_verses = []
                    if quran_db:
                        # البحث عن الجذر داخل آيات المصفوفة
                        related_verses = [v for v in quran_db if res['root'] in normalize_sovereign(v.get('text', ''))][:3]
                    
                    token_data = {
                        "word": w,
                        "root": res['root'],
                        "conf": res['conf'],
                        "method": res['method'],
                        "trace": res['trace'],
                        "verses": related_verses,
                        "gene": list(GENE_STYLE.keys())[int(hashlib.md5(res['root'].encode()).hexdigest(), 16) % 4]
                    }
                    tokens.append(token_data)

            # تسجيل السجل السيادي
            record = {
                "id": f"SOV-{int(time.time())}",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "input": input_text,
                "tokens": tokens,
                "metrics": {
                    "duration": round(time.time() - start_t, 3),
                    "integrity": round((len(tokens)/len(clean.split()))*100 if clean.split() else 0, 1)
                }
            }
            m['current_record'] = record
            m['history'].insert(0, record)
            m['active'] = True
            st.rerun()

    st.divider()
    st.caption(f"ملف المصفوفة: {matrix_info if quran_db else 'غير محمل'}")
    st.caption(f"المستخدم: محمد | CPU: As-Sajdah [5]")

# =========================[ 9. MAIN INTERFACE (TABS) ]=========================
t1, t2, t3, t4, t5 = st.tabs(["🧿 المستشار", "🪐 المدار", "🧬 الرنين", "⚖️ الميزان", "💾 الذاكرة"])

if m['active'] and m['current_record']:
    rec = m['current_record']
    
    with t1: # المستشار السيادي والربط القرآني
        st.subheader("🧿 تقارير المستشار والربط القرآني")
        for tok in rec['tokens']:
            with st.container():
                st.markdown(f"""
                <div class="advisor-card">
                    <span style="color:#00ffcc; font-weight:bold;">{tok['word']}</span> ← 
                    <span style="color:#4fc3f7;">جذر: {tok['root']}</span> 
                    <span style="float:left; font-size:0.8em; color:#aaa;">الثقة: {tok['conf']}</span>
                </div>
                """, unsafe_allow_html=True)
                
                if tok['verses']:
                    st.markdown(f"**الرنين من المصفوفة القرآنية ({len(tok['verses'])} آيات):**")
                    for v in tok['verses']:
                        st.markdown(f"""<div class="verse-box">"{v['text']}" <br> <small>— {v.get('surah', 'سورة')} [آية {v.get('verse', '0')}]</small></div>""", unsafe_allow_html=True)
                else:
                    st.caption("لم يتم العثور على رنين مباشر في المصفوفة لهذا الجذر.")
                
                if show_trace:
                    st.caption(f"مسار التتبع: {', '.join(tok['trace'][:10])}...")

    with t2: # المدار البصري
        st.subheader("🪐 تمثيل المدار الوجودي")
        if rec['tokens']:
            df = pd.DataFrame([{
                "x": random.uniform(-10,10), 
                "y": random.uniform(-10,10), 
                "root": t['root'], 
                "gene": GENE_STYLE[t['gene']]['name'], 
                "energy": t['conf']*30,
                "color": GENE_STYLE[t['gene']]['color']
            } for t in rec['tokens']])
            
            fig = px.scatter(df, x="x", y="y", text="root", size="energy", color="gene",
                             color_discrete_map={v['name']: v['color'] for v in GENE_STYLE.values()})
            fig.update_layout(height=600, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=True)
            fig.update_xaxes(visible=False); fig.update_yaxes(visible=False)
            st.plotly_chart(fig, use_container_width=True)

    with t3: # الرنين الجيني
        st.subheader("🧬 الهيمنة الجينية")
        gene_counts = Counter([t['gene'] for t in rec['tokens']])
        cols = st.columns(5)
        for i, (gk, gv) in enumerate(GENE_STYLE.items()):
            with cols[i]:
                st.markdown(f"""
                <div style="text-align:center; border:1px solid {gv['color']}; padding:15px; border-radius:12px; background:rgba(255,255,255,0.02);">
                    <div style="font-size:2em;">{gv['icon']}</div>
                    <div style="color:{gv['color']}; font-weight:bold;">{gv['name']}</div>
                    <div class="stat-val">{gene_counts.get(gk, 0)}</div>
                </div>
                """, unsafe_allow_html=True)

    with t4: # الميزان السيادي (Verdict)
        st.subheader("⚖️ الحكم السيادي الختامي")
        integrity = rec['metrics']['integrity']
        status = "حاسم ومستقر" if integrity > 85 else "راجح للاستبصار" if integrity > 60 else "يحتاج مراجعة لغوية"
        
        st.markdown(f"""
        <div class="verdict-box">
            <h2 style="color:#4CAF50;">القرار السيادي: {status}</h2>
            <p style="font-size:1.3em;">تمت مطابقة <b>{len(rec['tokens'])}</b> جذور من أصل <b>{len(rec['input'].split())}</b> كلمات.</p>
            <div style="display:flex; justify-content:space-around; margin:20px 0;">
                <div><small>نسبة الثبات</small><br><span class="stat-val">{integrity}%</span></div>
                <div><small>زمن المفاعل</small><br><span class="stat-val" style="color:#4fc3f7;">{rec['metrics']['duration']}s</span></div>
            </div>
            <small style="color:#555;">بصمة التوثيق: {hashlib.md5(rec['input'].encode()).hexdigest()}</small>
        </div>
        """, unsafe_allow_html=True)

    with t5: # الذاكرة والتصدير
        st.subheader("💾 ذاكرة الجلسة والتصدير السيادي")
        c_ex1, c_ex2 = st.columns(2)
        with c_ex1:
            st.download_button("📤 تصدير بصيغة JSON", data=json.dumps(rec, ensure_ascii=False, indent=2), file_name=f"nibras_{rec['id']}.json")
        with c_ex2:
            st.download_button("📄 تقرير نصي (TXT)", data=str(rec), file_name=f"nibras_{rec['id']}.txt")
        
        st.write("---")
        st.markdown("**آخر 5 تحليلات في الذاكرة الموضعية:**")
        for h in m['history'][:5]:
            st.info(f"🆔 {h['id']} | 🕒 {h['timestamp']} | النص: {h['input'][:40]}...")

else:
    st.info("🧿 المفاعل في وضع الاستعداد السيادي. أدخل نصاً في القائمة الجانبية لبدء الاستنباط.")

# =========================[ 10. FOOTER ]=======================================
st.sidebar.markdown("---")
st.sidebar.write("خِت فِت.")
