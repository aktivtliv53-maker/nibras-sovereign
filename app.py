import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os
import re
from collections import Counter

# 1. إعدادات الهوية البصرية (مطابقة للصورة 8)
st.set_page_config(page_title="نبراس السيادي", page_icon="🛡️", layout="wide")

st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background: #050505; color: #e0e0e0; direction: rtl; }
    /* صندوق البيان الختامي الموسع الأخضر الداكن */
    .summary-box {
        background: #0d1a0d; padding: 25px; border-radius: 12px; 
        border-right: 8px solid #FFD700; margin-bottom: 30px;
    }
    /* كروت الاستنطاق السوداء الأنيقة */
    .insight-card {
        background: #111; padding: 20px; border-radius: 10px;
        border-left: 4px solid #4fc3f7; margin-bottom: 15px;
        line-height: 1.8; font-size: 1.15em;
    }
    .root-label { color: #81c784; font-weight: bold; font-size: 1.2em; }
</style>
""", unsafe_allow_html=True)

# 2. الدوال والمحرك
GENE_STYLE = {
    'C': {'name': 'الإبل', 'color': '#4fc3f7', 'icon': '🐪'},
    'B': {'name': 'البقر', 'color': '#FFD700', 'icon': '🐄'},
    'S': {'name': 'الضأن', 'color': '#81c784', 'icon': '🐑'},
    'G': {'name': 'المعز', 'color': '#ff5252', 'icon': '🐐'}
}

def normalize_root(text):
    if not text: return ""
    return re.sub(r'[\u064B-\u065F]', '', str(text).strip().replace("أ", "ا").replace("إ", "ا").replace("آ", "ا"))

@st.cache_data
def load_db():
    path = "data/nibras_lexicon.json"
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return {normalize_root(item['root']): item for item in data}
    return {}

db = load_db()

# 3. واجهة المدخلات
input_text = st.text_area("أدخل النص للاستنطاق:", height=100)

if st.button("🚀 تفعيل المفاعل السيادي", use_container_width=True):
    if input_text.strip():
        words = input_text.split()
        bodies = []
        for w in words:
            norm = normalize_root(w)
            if norm in db:
                item = db[norm]
                g_code = item.get('gene', 'S')
                bodies.append({
                    "root": item['root'], "orbit": item.get('orbit_id', 1),
                    "gene": g_code, "insight": item.get('insight_radar', item.get('insight', 'بصيرة قيد التكوين.')),
                    "color": GENE_STYLE.get(g_code, GENE_STYLE['S'])['color'],
                    "gene_display": f"{GENE_STYLE.get(g_code, GENE_STYLE['S'])['icon']} {GENE_STYLE.get(g_code, GENE_STYLE['S'])['name']}"
                })
        
        if bodies:
            # عرض الرسم البياني (كما في الصورة 7)
            fig = px.scatter(pd.DataFrame(bodies), x="root", y="orbit", color="gene_display", 
                             template="plotly_dark", size_max=20)
            st.plotly_chart(fig, use_container_width=True)
            
            # عرض البيان الختامي الموسع (كما في الصورة 8)
            genes = [b['gene'] for b in bodies]
            dom = max(set(genes), key=genes.count)
            st.markdown(f"""
            <div class="summary-box">
                <h2 style='color:#FFD700; margin:0;'>📜 البيان الختامي الموسع</h2>
                <p style='font-size:1.1em; margin-top:10px;'>✅ تم استنطاق {len(bodies)} جذور | الهيمنة: {GENE_STYLE[dom]['icon']} {GENE_STYLE[dom]['name']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # عرض تفاصيل الاستنطاق (بدون بتر)
            for b in bodies:
                st.markdown(f"""
                <div class="insight-card">
                    <span class="root-label">📌 الجذر: {b['root']} | {b['gene_display']}</span>
                    <p style='margin-top:10px;'>{b['insight']}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.error("لم يتم العثور على جذور مطابقة.")
