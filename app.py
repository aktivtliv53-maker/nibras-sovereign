import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os
import re

# 1. إعدادات الهوية السيادية (التبويبات الثلاثة الأصلية)
st.set_page_config(page_title="نبراس السيادي", page_icon="🛡️", layout="wide")

st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background: #050505; color: #e0e0e0; direction: rtl; }
    .summary-box {
        background: #0d1a0d; padding: 25px; border-radius: 12px; 
        border-right: 8px solid #FFD700; margin-bottom: 30px; border: 1px solid #1a3a1a;
    }
    .insight-card {
        background: #111; padding: 20px; border-radius: 10px;
        border-right: 5px solid #4fc3f7; margin-bottom: 15px;
        line-height: 1.8; font-size: 1.15em;
    }
    .stTabs [aria-selected="true"] { color: #FFD700 !important; border-bottom: 2px solid #FFD700 !important; }
</style>
""", unsafe_allow_html=True)

# 2. المحرك الأصلي (تطهير وبحث مباشر)
GENE_STYLE = {
    'C': {'name': 'الإبل', 'color': '#4fc3f7', 'icon': '🐪'},
    'B': {'name': 'البقر', 'color': '#FFD700', 'icon': '🐄'},
    'S': {'name': 'الضأن', 'color': '#81c784', 'icon': '🐑'},
    'G': {'name': 'المعز', 'color': '#ff5252', 'icon': '🐐'}
}

def normalize_root(text):
    if not text: return ""
    # العودة للتطهير البسيط الذي نجح سابقاً
    t = str(text).strip().replace("أ", "ا").replace("إ", "ا").replace("آ", "ا")
    return re.sub(r'[\u064B-\u065F]', '', t)

@st.cache_data
def load_db():
    path = "data/nibras_lexicon.json"
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return {normalize_root(item['root']): item for item in data}
    return {}

db = load_db()

# 3. الهيكل الثلاثي الأصلي
tab1, tab2, tab3 = st.tabs(["🔍 مفاعل الاستنطاق", "📜 البيان الختامي", "📈 الخريطة الوجودية"])

with tab1:
    input_text = st.text_area("أدخل المسار (الجذور مفصولة بمسافة):", height=100)
    if st.button("🚀 تفعيل المفاعل السيادي", use_container_width=True):
        if input_text.strip():
            # استخراج الكلمات وتنظيفها للبحث
            words = input_text.split()
            bodies = []
            for w in words:
                norm = normalize_root(w)
                if norm in db:
                    item = db[norm]
                    g_code = item.get('gene', 'S')
                    bodies.append({
                        "root": item['root'], "orbit": item.get('orbit_id', 1),
                        "gene": g_code, "insight": item.get('insight_radar', item.get('insight', '...')),
                        "color": GENE_STYLE.get(g_code, GENE_STYLE['S'])['color'],
                        "gene_display": f"{GENE_STYLE.get(g_code, GENE_STYLE['S'])['icon']} {GENE_STYLE.get(g_code, GENE_STYLE['S'])['name']}"
                    })
            if bodies:
                st.session_state.active_bodies = bodies
                st.success(f"✅ تم رصد {len(bodies)} جذور بنجاح.")
            else:
                st.error("لم يتم العثور على جذور مطابقة. تأكد من إدخال الجذر الصافي.")

with tab2:
    if 'active_bodies' in st.session_state:
        bodies = st.session_state.active_bodies
        dom = max([b['gene'] for b in bodies], key=[b['gene'] for b in bodies].count)
        
        # البيان الختامي الموسع (Header)
        st.markdown(f"""
        <div class="summary-box">
            <h2 style='color:#FFD700; margin:0;'>📜 البيان الختامي الموسع</h2>
            <p style='font-size:1.2em; margin-top:10px;'>الهيمنة الجينية المستنبطة: {GENE_STYLE[dom]['icon']} {GENE_STYLE[dom]['name']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # تفاصيل الاستنطاق الكاملة (بدون بتر)
        for b in bodies:
            st.markdown(f"""
            <div class="insight-card" style="border-right-color:{b['color']}">
                <b style="color:{b['color']}; font-size:1.2em;">📌 الجذر: {b['root']}</b> | {b['gene_display']}
                <p style='margin-top:10px;'>{b['insight']}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("بانتظار تفعيل المفاعل...")

with tab3:
    if 'active_bodies' in st.session_state:
        df = pd.DataFrame(st.session_state.active_bodies)
        fig = px.scatter(df, x="root", y="orbit", color="gene_display", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
