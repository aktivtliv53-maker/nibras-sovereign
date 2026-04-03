# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os
import random
import re
from collections import Counter

# ==============================================================================
# [1] إعدادات السيادة
# ==============================================================================
st.set_page_config(page_title="نبراس السيادي v32.0", page_icon="🛡️", layout="wide")

# CSS السيادي - لمنع العبث البصري وضمان الفصاحة
st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background: #050505; color: #e0e0e0; direction: rtl; }
    .insight-card {
        background: rgba(255,255,255,0.04); padding: 20px; border-radius: 10px;
        border-right: 5px solid #4fc3f7; margin-bottom: 15px; line-height: 1.8;
    }
    .summary-box {
        background: linear-gradient(135deg, #0a1a0a 0%, #051005 100%);
        padding: 25px; border-radius: 15px; border-right: 5px solid #FFD700;
        margin-bottom: 30px; border: 1px solid #1a3a1a;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# [2] المحرك الهندسي والجيني
# ==============================================================================
GENE_STYLE = {
    'C': {'name': 'الإبل', 'color': '#4fc3f7', 'icon': '🐪'},
    'B': {'name': 'البقر', 'color': '#FFD700', 'icon': '🐄'},
    'S': {'name': 'الضأن', 'color': '#4CAF50', 'icon': '🐑'},
    'G': {'name': 'المعز', 'color': '#ff5252', 'icon': '🐐'}
}

LETTER_GEOMETRY = {
    'ا': 'امتداد عمودي، صلة بين العلوي والأرضي.', 'ب': 'ظهور أرضي، احتواء أفقي.',
    'ت': 'استقرار فوقي، جمع وتراكم.', 'ج': 'حركة لولبية، طاقة حيوية ممتدة.',
    'ح': 'احتواء حار، طاقة حياة صافية.', 'د': 'رسوخ زاوي، ثبات واتجاه.',
    'ر': 'انطلاق سائل، تكرار طاقي.', 'س': 'تردد تموجي، انتشار أفقي.',
    'ص': 'إحكام صلب، تجميع مركزي.', 'ط': 'سمو مرتفع، طاقة صاعدة.',
    'ع': 'عمق وعين، انفتاح على الباطن.', 'ق': 'قوة دائرية، حسم مداري.',
    'ل': 'اتصال وانسياب، امتداد طولي.', 'م': 'جمع ميمي، طاقة المحيط.',
    'ن': 'احتواء نوني، وعي في قلب الرحم.'
}

def normalize_root(text):
    if not text: return ""
    s = str(text).strip().replace("أ", "ا").replace("إ", "ا").replace("آ", "ا")
    return re.sub(r'[\u064B-\u065F]', '', s)

def ensure_dot(text):
    if not text: return "."
    s = str(text).strip()
    return s if s.endswith('.') else s + "."

def generate_geometric_insight(root):
    if not root: return "بصيرة قيد التكوين."
    parts = [LETTER_GEOMETRY.get(c, f"تفاعل الحرف {c}") for c in root]
    return "الاستنطاق الهندسي: " + " ثم ".join(parts) + "."

@st.cache_data
def load_db():
    path = "data/nibras_lexicon.json"
    if not os.path.exists(path): return {}
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return {normalize_root(item['root']): item for item in data}

db = load_db()

# ==============================================================================
# [3] دالة العرض السيادي
# ==============================================================================
def display_sovereign_results(bodies_list):
    if not bodies_list: return
    
    # البيان الجماعي
    genes_count = Counter(b['gene'] for b in bodies_list)
    dominant_gene = max(genes_count, key=genes_count.get)
    g_info = GENE_STYLE.get(dominant_gene, GENE_STYLE['S'])
    
    st.markdown(f"""
    <div class="summary-box">
        <h3 style='color:#FFD700;'>📜 البيان الختامي الموسع</h3>
        <p>✅ تم استنطاق <b>{len(bodies_list)}</b> جذراً | الهيمنة: <b style='color:{g_info["color"]}'>{g_info['icon']} {g_info['name']}</b></p>
        <p>📚 المسار: <b>{', '.join([b['root'] for b in bodies_list])}</b></p>
    </div>
    """, unsafe_allow_html=True)
    
    for b in bodies_list:
        st.markdown(f"""
        <div class="insight-card" style="border-right-color: {b['color']}">
            <b style="color:{b['color']};">📌 الجذر: {b['root']}</b> | {b['gene_display']}<br>
            <p style="margin-top:10px;">{ensure_dot(b['insight'])}</p>
        </div>
        """, unsafe_allow_html=True)

# ==============================================================================
# [4] الواجهة والزر
# ==============================================================================
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
                    "gene": g_code, "gene_display": f"{GENE_STYLE[g_code]['icon']} {GENE_STYLE[g_code]['name']}",
                    "insight": item.get('insight_radar', item.get('insight', '')) or generate_geometric_insight(norm),
                    "color": GENE_STYLE[g_code]['color']
                })
        
        if bodies:
            st.plotly_chart(px.scatter(pd.DataFrame(bodies), x="root", y="orbit", color="gene_display", size_max=40))
            display_sovereign_results(bodies)
        else: st.error("لم يتم العثور على جذور.")
