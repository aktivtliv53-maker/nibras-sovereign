import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os
import re
from collections import Counter

# 1. إعدادات الصفحة
st.set_page_config(page_title="نبراس السيادي", page_icon="🛡️", layout="wide")

# 2. تحسين العرض لمنع البتر (CSS)
st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background: #050505; color: #e0e0e0; direction: rtl; }
    .summary-box {
        background: linear-gradient(135deg, #0d1a0d 0%, #000000 100%);
        padding: 25px; border-radius: 15px; border-right: 8px solid #FFD700;
        margin-bottom: 30px; border: 1px solid #1a3a1a;
    }
    .insight-card {
        background: #111; padding: 20px; border-radius: 10px;
        border-right: 5px solid #4fc3f7; margin-bottom: 15px;
        line-height: 1.8; font-size: 1.1em;
    }
</style>
""", unsafe_allow_html=True)

# 3. الدوال الأساسية
GENE_STYLE = {
    'C': {'name': 'الإبل', 'color': '#4fc3f7', 'icon': '🐪'},
    'B': {'name': 'البقر', 'color': '#FFD700', 'icon': '🐄'},
    'S': {'name': 'الضأن', 'color': '#4CAF50', 'icon': '🐑'},
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

# 4. واجهة المدخلات
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
                    "root": item['root'], 
                    "orbit": item.get('orbit_id', 1),
                    "gene": g_code,
                    "insight": item.get('insight_radar', item.get('insight', 'بصيرة قيد التكوين.')),
                    "color": GENE_STYLE.get(g_code, GENE_STYLE['S'])['color'],
                    "gene_display": f"{GENE_STYLE.get(g_code, GENE_STYLE['S'])['icon']} {GENE_STYLE.get(g_code, GENE_STYLE['S'])['name']}"
                })
        
        if bodies:
            # عرض الرسم البياني
            fig = px.scatter(pd.DataFrame(bodies), x="root", y="orbit", color="gene_display", template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)
            
            # عرض البيان الختامي الموسع
            genes = [b['gene'] for b in bodies]
            dom = max(set(genes), key=genes.count)
            st.markdown(f"""
            <div class="summary-box">
                <h2 style='color:#FFD700;'>📜 البيان الختامي الموسع</h2>
                <p>✅ تم استنطاق {len(bodies)} جذور | الهيمنة: {GENE_STYLE[dom]['icon']} {GENE_STYLE[dom]['name']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # عرض الكروت (بدون بتر)
            for b in bodies:
                st.markdown(f"""
                <div class="insight-card" style="border-right-color: {b['color']}">
                    <b style="color:{b['color']};">📌 الجذر: {b['root']}</b><br>
                    {b['insight']}
                </div>
                """, unsafe_allow_html=True)
