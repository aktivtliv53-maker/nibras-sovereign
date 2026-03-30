# -*- coding: utf-8 -*-
# Nibras Sovereign v26.5 – The Quranic Monolith (The Final Edition)
# Designed by Mohamed & Al-Tair (Gemini)

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import re, random, os, json, time, hashlib
from pathlib import Path

# =========================[ 1. CONFIG & THEME ]================================
st.set_page_config(page_title="Nibras Sovereign v26.5", page_icon="🧿", layout="wide")

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
        'mode': 'Sovereign', # Ritual | Sovereign | Lab
        'current_record': None,
        'history': [],
        'resolved_ambiguities': {},
        'logs': [],
        'metrics': {}
    }

m = st.session_state.monolith

# =========================[ 3. ENGINE: NORMALIZATION ]=========================
def normalize_sovereign(text: str) -> str:
    if not text: return ""
    text = re.sub(r'[\u0617-\u061A\u064B-\u0652\u0670]', '', str(text)) # إزالة التشكيل
    rep = {"أ":"ا","إ":"ا","آ":"ا","ة":"ه","ى":"ي","ؤ":"و","ئ":"ي"}
    for k, v in rep.items(): text = text.replace(k, v)
    text = re.sub(r'[^\u0621-\u064A\s]', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()

# =========================[ 4. ENGINE: ROOT CANDIDATES ]=======================
PREFIXES = ["وال", "فال", "بال", "كال", "لل", "ال", "و", "ف", "ب", "ك", "ل", "س"]
SUFFIXES = ["هما", "كما", "كم", "كن", "هم", "هن", "نا", "ها", "ه", "ات", "ان", "ون", "ين", "يه", "ية", "ي", "ة", "ا"]

def generate_candidates(word: str):
    w = normalize_sovereign(word)
    if not w: return []
    cands = {w}
    for p in PREFIXES: 
        if w.startswith(p) and len(w)-len(p)>=2: cands.add(w[len(p):])
    for s in SUFFIXES:
        for c in list(cands):
            if c.endswith(s) and len(c)-len(s)>=2: cands.add(c[:-len(s)])
    # تقليل التضعيف وإضافة الثلاثيات
    final = set()
    for c in cands:
        final.add(c)
        final.add(re.sub(r'(.)\1+', r'\1', c))
        if len(c) >= 3:
            for i in range(len(c)-2): final.add(c[i:i+3])
    return sorted([x for x in final if 2<=len(x)<=6], key=lambda x: (-len(x), x))

# =========================[ 5. ENGINE: SOVEREIGN MATCH ]=======================
def sovereign_match(word: str, index_keys):
    cands = generate_candidates(word)
    trace = []
    for c in cands:
        if c in index_keys:
            conf = 0.95 if len(c)==3 else 0.85
            return {"root": c, "conf": conf, "method": "Direct Candidate", "trace": cands}
    return {"root": None, "conf": 0.0, "method": "No Match", "trace": cands}

# =========================[ 6. LOAD DATABASES ]================================
@st.cache_data
def load_all_dbs():
    # 1. ملف الجذور
    roots_data = {"roots": []}
    if Path("quran_roots_complete.json").exists():
        with open("quran_roots_complete.json", 'r', encoding='utf-8') as f:
            roots_data = json.load(f)
    
    # 2. ملف القرآن (ربط الآيات)
    quran_text = []
    if Path("quran_text.json").exists(): # نفترض وجوده بجانب التطبيق
        with open("quran_text.json", 'r', encoding='utf-8') as f:
            quran_text = json.load(f)
            
    r_index = {normalize_sovereign(r['root']): r for r in roots_data.get("roots", []) if r.get('root')}
    return r_index, quran_text

r_index, quran_db = load_all_dbs()

# =========================[ 7. UI CSS ]========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Orbitron:wght@500&display=swap');
    [data-testid="stAppViewContainer"] { background: radial-gradient(circle, #0a0a15 0%, #000 100%); color: #e0e0e0; font-family: 'Amiri', serif; direction: rtl; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { background: #111; border-radius: 8px 8px 0 0; padding: 10px 20px; border: 1px solid #222; }
    .advisor-card { background: rgba(0, 255, 204, 0.05); border-right: 5px solid #00ffcc; padding: 20px; border-radius: 12px; margin: 10px 0; }
    .verdict-box { background: #051005; border: 1px solid #1a3a1a; padding: 25px; border-radius: 15px; text-align: center; border-top: 4px solid #4CAF50; }
    .stat-val { font-family: 'Orbitron', sans-serif; color: #00ffcc; font-size: 2em; }
</style>
""", unsafe_allow_html=True)

# =========================[ 8. SIDEBAR ]=======================================
with st.sidebar:
    st.title("🛡️ ميزان نِبْرَاس")
    input_text = st.text_area("أدخل المسار الوجودي للتحليل:", height=200, placeholder="آية قرآنية أو نص سيادي...")
    op_mode = st.selectbox("وضع التشغيل:", ["Sovereign (متزن)", "Ritual (جمال شعائري)", "Lab (سرعة قصوى)"])
    st.divider()
    show_trace = st.checkbox("إظهار مسار المستشار (Trace)", value=True)
    if st.button("🚀 تفعيل المفاعل v26.5", use_container_width=True):
        if input_text:
            start_t = time.time()
            clean = normalize_sovereign(input_text)
            tokens = []
            matched_roots = []
            
            for w in clean.split():
                res = sovereign_match(w, r_index.keys())
                if res['root']:
                    # ربط الآيات (البحث في القرآن)
                    related_verses = []
                    if quran_db:
                        # منطق بحث بسيط: الآيات التي تحتوي على الكلمة
                        related_verses = [v for v in quran_db if res['root'] in normalize_sovereign(v['text'])][:3]
                    
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
                    matched_roots.append(res['root'])

            # الذاكرة السيادية
            record = {
                "id": f"SR-{int(time.time())}",
                "timestamp": time.ctime(),
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

# =========================[ 9. TABS SYSTEM ]===================================
t1, t2, t3, t4, t5 = st.tabs(["🧿 المستشار السيادي", "🪐 المدار القرآني", "🧬 الرنين", "📊 الميزان", "💾 الذاكرة & التصدير"])

if m['active'] and m['current_record']:
    rec = m['current_record']
    
    with t1: # المستشار السيادي
        st.subheader("🧿 تقرير المستشار السيادي")
        col1, col2, col3 = st.columns(3)
        col1.metric("درجة الصدق (Integrity)", f"{rec['metrics']['integrity']}%")
        col2.metric("الجذور المكتشفة", len(rec['tokens']))
        col3.metric("زمن الاستجابة", f"{rec['metrics']['duration']}s")
        
        for tok in rec['tokens']:
            with st.expander(f"الكلمة: {tok['word']} ← الجذر: {tok['root']} ({'حاسم' if tok['conf']>0.9 else 'راجح'})"):
                st.write(f"**المنطق:** {tok['method']}")
                if show_trace: st.caption(f"المرشحات التي فحصها المستشار: {', '.join(tok['trace'])}")
                if tok['verses']:
                    st.info(f"**من الرنين القرآني:** {tok['verses'][0].get('text', '')} ({tok['verses'][0].get('surah', '')})")

    with t2: # المدار القرآني
        st.subheader("🪐 الاستدلال المداري البصري")
        # فيزياء مبسطة للعرض
        df = pd.DataFrame([{"x": random.uniform(-10,10), "y": random.uniform(-10,10), 
                            "root": t['root'], "gene": t['gene'], "size": t['conf']*20} for t in rec['tokens']])
        fig = px.scatter(df, x="x", y="y", text="root", color="gene", 
                         color_discrete_map={k: v['color'] for k, v in GENE_STYLE.items()},
                         size="size")
        fig.update_layout(showlegend=False, height=600, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        fig.update_xaxes(visible=False); fig.update_yaxes(visible=False)
        st.plotly_chart(fig, use_container_width=True)

    with t3: # الرنين
        st.subheader("🧬 تحليل الرنين والجينات")
        gene_counts = Counter([t['gene'] for t in rec['tokens']])
        cols = st.columns(5)
        for i, (gk, gv) in enumerate(GENE_STYLE.items()):
            cols[i].markdown(f"""
            <div style="text-align:center; border:1px solid {gv['color']}; padding:10px; border-radius:10px;">
                <div style="font-size:1.5em">{gv['icon']}</div>
                <div style="color:{gv['color']}">{gv['name']}</div>
                <div class="stat-val">{gene_counts.get(gk, 0)}</div>
            </div>
            """, unsafe_allow_html=True)

    with t4: # الميزان (القرار النهائي)
        st.subheader("⚖️ الميزان السيادي والحكم النهائي")
        st.markdown(f"""
        <div class="verdict-box">
            <h3>القرار السيادي النهائي</h3>
            <p style="font-size:1.2em">بناءً على تحليل {len(rec['tokens'])} جذراً، يجد المستشار أن النص ذو 
            <b>ثبات معرفي بنسبة {rec['metrics']['integrity']}%</b>.</p>
            <p>التوصية: {"قابل للاعتماد البحثي" if rec['metrics']['integrity']>70 else "يحتاج مراجعة يدوية للالتباس"}</p>
            <hr style="border-color:#1a3a1a">
            <small>بصمة الوثيقة: {hashlib.sha256(rec['input'].encode()).hexdigest()[:16]}</small>
        </div>
        """, unsafe_allow_html=True)

    with t5: # الذاكرة والتصدير
        st.subheader("💾 ذاكرة الجلسة والتصدير")
        col_ex1, col_ex2 = st.columns(2)
        with col_ex1:
            st.download_button("📤 تصدير بصيغة JSON", data=json.dumps(rec, ensure_ascii=False), file_name=f"{rec['id']}.json")
        with col_ex2:
            st.download_button("📄 تصدير تقرير نصي", data=str(rec), file_name=f"{rec['id']}.txt")
        
        st.write("---")
        st.write("**السجلات السابقة:**")
        for h in m['history'][:5]:
            st.text(f"🕒 {h['timestamp']} | {h['input'][:50]}...")

else:
    st.info("المفاعل في وضع الاستعداد. أدخل نصاً في القائمة الجانبية لتفعيل المونوليث v26.5.")

# =========================[ 10. FOOTER ]=======================================
st.sidebar.caption(f"Mohamed CPU: Surah As-Sajdah [5] | v26.5")
st.sidebar.markdown("---")
st.sidebar.write("خِت فِت.")
