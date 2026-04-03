# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os
import re
from collections import Counter

# ==============================================================================
# [1] إعدادات الهوية البصرية - منع القص نهائياً
# ==============================================================================
st.set_page_config(page_title="نبراس السيادي v33.0", page_icon="🛡️", layout="wide")

st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background: #050505; color: #e0e0e0; direction: rtl; }
    /* صندوق البيان الختامي الموسع */
    .summary-box {
        background: linear-gradient(135deg, #0a1a0a 0%, #051005 100%);
        padding: 30px; border-radius: 20px; border-right: 6px solid #FFD700;
        margin-bottom: 35px; border: 1px solid #1a3a1a;
    }
    /* كروت الاستنطاق الفردي */
    .insight-card {
        background: rgba(255,255,255,0.03); padding: 25px; border-radius: 12px;
        border-right: 5px solid #4fc3f7; margin-bottom: 20px; 
        line-height: 1.8; font-size: 1.1em;
    }
    h3 { color: #FFD700; }
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

def normalize_root(text):
    if not text: return ""
    s = str(text).strip().replace("أ", "ا").replace("إ", "ا").replace("آ", "ا")
    return re.sub(r'[\u064B-\u065F]', '', s)

def ensure_dot(text):
    if not text: return "."
    s = str(text).strip()
    return s if s.endswith('.') else s + "."

@st.cache_data
def load_db():
    path = "data/nibras_lexicon.json"
    if not os.path.exists(path): return {}
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return {normalize_root(item['root']): item for item in data}

db = load_db()

# ==============================================================================
# [3] دالة العرض السيادية - (هنا يكمن الحل)
# ==============================================================================
def display_sovereign_results(bodies_list):
    if not bodies_list: return
    
    # 1. الجزء العلوي: البيان الختامي الموسع (الإحصائيات والجين المهيمن)
    genes_count = Counter(b['gene'] for b in bodies_list)
    dominant_gene = max(genes_count, key=genes_count.get)
    g_info = GENE_STYLE.get(dominant_gene, GENE_STYLE['S'])
    
    st.markdown(f"""
    <div class="summary-box">
        <h2 style='margin-top:0; color:#FFD700;'>📜 البيان الختامي الموسع</h2>
        <p style='font-size:1.2em;'>✅ تم استنطاق <b>{len(bodies_list)}</b> جذراً في هذا المدار.</p>
        <p style='font-size:1.2em;'>🐪 الهيمنة الجينية الحالية: <b style='color:{g_info["color"]}'>{g_info['icon']} {g_info['name']}</b></p>
        <p style='font-size:1.2em;'>📚 المسار المكتشف: <b>{', '.join([b['root'] for b in bodies_list])}</b></p>
    </div>
    """, unsafe_allow_html=True)
    
    # 2. الجزء السفلي: تفاصيل الاستنطاق الكاملة (بدون قص)
    st.markdown("### 🔍 تفاصيل الاستنطاق المداري")
    for b in bodies_list:
        st.markdown(f"""
        <div class="insight-card" style="border-right-color: {b['color']}">
            <b style="color:{b['color']}; font-size:1.3em;">📌 الجذر: {b['root']}</b> 
            <span style="color:#888; margin-right:10px;">| {b['gene_display']}</span>
            <hr style="border:0; border-top:1px solid rgba(255,255,255,0.1); margin:15px 0;">
            <div style="color:#eee; font-size:1.1em;">
                <b>الاستنطاق:</b> {ensure_dot(b['insight'])}
            </div>
        </div>
        """, unsafe_allow_html=True)

# ==============================================================================
# [4] الواجهة والتنفيذ
# ==============================================================================
input_text = st.text_area("أدخل النص للاستنطاق:", height=120, placeholder="أدخل الجذور هنا...")

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
                    "insight": item.get('insight_radar', item.get('insight', 'بصيرة قيد التكوين.')),
                    "color": GENE_STYLE[g_code]['color']
                })
        
        if bodies:
            # عرض الرسم البياني أولاً
            fig = px.scatter(pd.DataFrame(bodies), x="root", y="orbit", color="gene_display", 
                             size_max=40, template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)
            
            # ثم عرض البيان الختامي والتفاصيل
            display_sovereign_results(bodies)
        else:
            st.error("⚠️ لم يتم العثور على أي جذور مطابقة.")
