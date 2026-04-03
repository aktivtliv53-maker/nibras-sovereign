import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os
import re
from collections import Counter

# 1. تثبيت الهوية البصرية (التبويبات الثلاثة والواجهة الذهبية)
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

# 2. المحرك السيادي لاستخلاص الجذور
GENE_STYLE = {
    'C': {'name': 'الإبل', 'color': '#4fc3f7', 'icon': '🐪'},
    'B': {'name': 'البقر', 'color': '#FFD700', 'icon': '🐄'},
    'S': {'name': 'الضأن', 'color': '#81c784', 'icon': '🐑'},
    'G': {'name': 'المعز', 'color': '#ff5252', 'icon': '🐐'}
}

def clean_text(text):
    if not text: return ""
    # إزالة التشكيل وكل ما ليس حرفاً عربياً
    text = re.sub(r'[\u064B-\u065F]', '', text)
    return text.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا").strip()

@st.cache_data
def load_db():
    path = "data/nibras_lexicon.json"
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # تخزين القاعدة بنسخة مطهرة للمقارنة
        return {clean_text(item['root']): item for item in data}
    return {}

db = load_db()

# 3. الهيكل الثلاثي (كما في الصورة 9)
tab1, tab2, tab3 = st.tabs(["🔍 مفاعل الاستنطاق", "📜 البيان الختامي", "📈 الخريطة الوجودية"])

with tab1:
    input_text = st.text_area("أدخل الآية أو الجذور:", height=150, placeholder="ضع النص هنا ليقوم النظام باستخلاص الجذور...")
    
    if st.button("🚀 تفعيل المفاعل السيادي", use_container_width=True):
        if input_text.strip():
            # تقطيع النص إلى كلمات وتنظيفها
            raw_words = re.findall(r'\w+', input_text)
            bodies = []
            seen_roots = set()

            for word in raw_words:
                norm_word = clean_text(word)
                # البحث عن أي جذر موجود داخل الكلمة أو يطابقها
                for root_key in db:
                    if root_key in norm_word and root_key not in seen_roots:
                        item = db[root_key]
                        g_code = item.get('gene', 'S')
                        bodies.append({
                            "root": item['root'],
                            "orbit": item.get('orbit_id', 1),
                            "gene": g_code,
                            "insight": item.get('insight_radar', item.get('insight', '...')),
                            "color": GENE_STYLE.get(g_code, GENE_STYLE['S'])['color'],
                            "gene_display": f"{GENE_STYLE.get(g_code, GENE_STYLE['S'])['icon']} {GENE_STYLE.get(g_code, GENE_STYLE['S'])['name']}"
                        })
                        seen_roots.add(root_key)
            
            if bodies:
                st.session_state.active_bodies = bodies
                st.success(f"✅ تم استخلاص {len(bodies)} جذراً من النص بنجاح.")
            else:
                st.error("⚠️ لم يتم العثور على جذور معروفة في هذا النص.")

with tab2:
    if 'active_bodies' in st.session_state:
        bodies = st.session_state.active_bodies
        dom = max([b['gene'] for b in bodies], key=[b['gene'] for b in bodies].count)
        
        st.markdown(f"""
        <div class="summary-box">
            <h2 style='color:#FFD700; margin:0;'>📜 البيان الختامي الموسع</h2>
            <p style='font-size:1.2em;'>الهيمنة الجينية: {GENE_STYLE[dom]['icon']} {GENE_STYLE[dom]['name']}</p>
            <p>الجذور المكتشفة: {', '.join([b['root'] for b in bodies])}</p>
        </div>
        """, unsafe_allow_html=True)
        
        for b in bodies:
            st.markdown(f"""
            <div class="insight-card" style="border-right-color:{b['color']}">
                <b style="color:{b['color']}">📌 الجذر: {b['root']}</b> | {b['gene_display']}
                <p style='margin-top:10px;'>{b['insight']}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("بانتظار الاستنطاق في التبويب الأول.")

with tab3:
    if 'active_bodies' in st.session_state:
        df = pd.DataFrame(st.session_state.active_bodies)
        fig = px.scatter(df, x="root", y="orbit", color="gene_display", size_max=20, template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
