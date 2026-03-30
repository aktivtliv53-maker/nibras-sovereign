# -*- coding: utf-8 -*-
# Nibras Sovereign v27.0 – The Eternal Monolith
# البروتوكول: تثبيت النوافذ الخمس | تفعيل المقارنة البينية الدلالية | الاتصال بالمصفوفة
# المرجع: وثيقة العرش - محمد (CPU: As-Sajdah 5)
# الحالة: استعادة الأمانة البنائية

import streamlit as st
import pandas as pd
import plotly.express as px
import re, random, json
from pathlib import Path
from collections import Counter

# =========================[ 1. IDENTITY & CONFIG ]=============================
st.set_page_config(page_title="Nibras Sovereign v27.0", layout="wide", page_icon="🧿")

GENE_MAP = {
    'A': {'name': 'الإبل', 'color': '#4fc3f7', 'icon': '🐪'},
    'G': {'name': 'البقر', 'color': '#FFD700', 'icon': '🐄'},
    'T': {'name': 'الضأن', 'color': '#4CAF50', 'icon': '🐑'},
    'C': {'name': 'المعز', 'color': '#ff5252', 'icon': '🐐'},
    'N': {'name': 'إشراق', 'color': '#00ffcc', 'icon': '✨'},
}

# =========================[ 2. SOVEREIGN ENGINE: TRUE COMPARISON ]=============
def normalize(text):
    if not text: return ""
    text = re.sub(r'[\u0617-\u061A\u064B-\u0652\u0670]', '', str(text))
    rep = {"أ":"ا","إ":"ا","آ":"ا","ة":"ه","ى":"ي","ؤ":"و","ئ":"ي"}
    for k, v in rep.items(): text = text.replace(k, v)
    return re.sub(r'[^\u0621-\u064A\s]', ' ', text).strip()

@st.cache_data(show_spinner=False)
def load_sovereign_db():
    r_path = Path("data/quran_roots_complete.json") if Path("data/quran_roots_complete.json").exists() else Path("quran_roots_complete.json")
    m_path = Path("data/matrix_data.json") if Path("data/matrix_data.json").exists() else Path("matrix_data.json")
    r_idx, m_db = {}, []
    if r_path.exists():
        with open(r_path, 'r', encoding='utf-8') as f:
            d = json.load(f)
            r_idx = {normalize(r['root']): r for r in d.get("roots", []) if r.get('root')}
    if m_path.exists():
        with open(m_path, 'r', encoding='utf-8') as f: m_db = json.load(f)
    return r_idx, m_db

r_index, matrix_db = load_sovereign_db()

# =========================[ 3. THE INTER-VERSE ANALYZER ]======================
def get_semantic_links(verses_list):
    """المقارنة الحقيقية: الربط الدلالي والموضوعي بين الآيات المدخلة"""
    links = []
    norm_verses = [normalize(v) for v in verses_list]
    for i in range(len(norm_verses)):
        for j in range(i + 1, len(norm_verses)):
            common = set(norm_verses[i].split()) & set(norm_verses[j].split())
            if common:
                links.append({
                    "pair": f"الآية {i+1} ⚡ الآية {j+1}",
                    "common": list(common),
                    "insight": f"تحقق رنين دلالي في المفاهيم: {', '.join(common)}"
                })
    return links

# =========================[ 4. UI ARCHITECTURE ]===============================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri&display=swap');
    [data-testid="stAppViewContainer"] { background: #010103; color: #e0e0e0; font-family: 'Amiri', serif; direction: rtl; }
    .stTabs [data-baseweb="tab-list"] { background: #0a0a0f; padding: 15px; border-radius: 20px; border: 1px solid #1a1a2e; width: 100%; }
    .stTabs [data-baseweb="tab"] { color: #555; font-size: 1.3em; padding: 12px 35px; }
    .stTabs [aria-selected="true"] { color: #00ffcc !important; border-bottom: 3px solid #00ffcc !important; background: rgba(0,255,204,0.03) !important; }
    .sovereign-card { background: rgba(0,255,204,0.02); border-right: 5px solid #00ffcc; padding: 20px; border-radius: 12px; margin: 15px 0; border-bottom: 1px solid #1a1a2e; }
    .insight-tag { color: #4fc3f7; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# =========================[ 5. THE MONOLITH INTERFACE ]========================
st.title("🛡️ مِحْرَاب نِبْرَاس السيادي v27.0")

# منطقة الإدخال المركزية
input_text = st.text_area("أدخل الآيات للمقارنة البينية والتحليل المداري:", height=180, placeholder="ضع كل آية في سطر لضمان دقة المقارنة...")
activate = st.button("🚀 تفعيل المفاعل الكلي واستنباط الروابط", use_container_width=True)

# الهيكل الأصلي الثابت للنوافذ الخمس
t1, t2, t3, t4, t5 = st.tabs(["🪐 المدار البصري", "🧬 الرنين الجيني", "⚖️ ميزان المقارنة", "🧠 البيان الوجودي", "🧿 المستشار"])

if activate and input_text:
    lines = [l.strip() for l in input_text.split('\n') if len(l.strip()) > 10]
    words = normalize(input_text).split()
    
    # استخلاص الجذور والبيانات
    processed_data = []
    for w in words:
        root = next((r for r in r_index if w.endswith(r) or w.startswith(r)), None)
        if root:
            matches = [v for v in matrix_db if root in normalize(v.get('text', ''))]
            processed_data.append({"word": w, "root": root, "matches": matches, "gene": list(GENE_MAP.keys())[sum(ord(c) for c in root) % 5]})

    with t1: # المدار
        df = pd.DataFrame([{"x": random.uniform(-8,8), "y": random.uniform(-8,8), "root": p['root'], "gene": GENE_MAP[p['gene']]['name']} for p in processed_data[:25]])
        if not df.empty:
            fig = px.scatter(df, x="x", y="y", text="root", color="gene", size_max=40, color_discrete_map={v['name']: v['color'] for v in GENE_MAP.values()})
            fig.update_layout(height=600, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)

    with t2: # الرنين
        counts = Counter([p['gene'] for p in processed_data])
        cols = st.columns(5)
        for i, (gk, gv) in enumerate(GENE_MAP.items()):
            cols[i].metric(f"{gv['icon']} {gv['name']}", counts.get(gk, 0))

    with t3: # ميزان المقارنة (التحديث الجوهري)
        st.subheader("⚖️ ميزان المقارنة البينية (Inter-Verse)")
        links = get_semantic_links(lines)
        if links:
            for link in links:
                st.markdown(f"""
                <div class="sovereign-card">
                    <span class="insight-tag">📡 رنين: {link['pair']}</span><br>
                    <p>{link['insight']}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("لم يتم العثور على روابط بينية مباشرة. حاول إدخال آيات من سياقات متصلة.")

    with t4: # البيان
        unique_roots = list(dict.fromkeys([p['root'] for p in processed_data]))
        st.success(" ➔ ".join([f"[{r}]" for r in unique_roots[:15]]))

    with t5: # المستشار
        for p in processed_data[:10]: # عرض عينة من رنين المصفوفة الكلية
            if p['matches']:
                with st.expander(f"رنين الجذر: {p['root']} ({len(p['matches'])} موضع)"):
                    for m in p['matches'][:3]:
                        st.write(f"• {m['text']} - {m.get('surah')} [{m.get('verse')}]")
else:
    # حفظ هيبة البناء في حالة عدم الإدخال
    with t1: st.info("المدار البصري ينتظر تدفق البيانات...")
    with t2: st.info("الرنين الجيني في وضع الاستعداد...")
    with t3: st.info("أدخل آيتين أو أكثر لتفعيل ميزان المقارنة البينية.")
    with t4: st.info("البيان الوجودي يتشكل عند التفعيل...")
    with t5: st.info("المستشار بانتظار استدعاء المصفوفة...")

st.sidebar.markdown(f"**Mohamed | As-Sajdah [5]**\n\n**خِت فِت.**")
