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
# [1] إعدادات السيادة ومنع القص
# ==============================================================================
st.set_page_config(page_title="نبراس السيادي v31.0", page_icon="🛡️", layout="wide")

# منع قص النصوص في الجداول (احتياطي)
pd.set_option('display.max_colwidth', None)

# CSS السيادي - إزالة كل الفراغات والعبث البصري
st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background: #050505; color: #e0e0e0; direction: rtl; font-family: 'Amiri', serif; }
    .insight-card {
        background: rgba(255,255,255,0.04); padding: 20px; border-radius: 10px;
        border-right: 5px solid #4fc3f7; margin-bottom: 15px; line-height: 1.8;
    }
    .summary-box {
        background: linear-gradient(135deg, #0a1a0a 0%, #051005 100%);
        padding: 25px; border-radius: 15px; border-right: 5px solid #FFD700;
        margin-bottom: 30px; border: 1px solid #1a3a1a;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { 
        background-color: #1a1a2a; border-radius: 10px 10px 0 0; padding: 10px 20px; color: white;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# [2] المحرك الداخلي والبيانات
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
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return {normalize_root(item['root']): item for item in data}
    except: return {}

db = load_db()

# ==============================================================================
# [3] دوال العرض السيادية (تمنع القص وتظهر البيان)
# ==============================================================================
def display_sovereign_results(bodies_list):
    if not bodies_list:
        st.info("لم يتم العثور على جذور مستنطقة.")
        return
    
    # 1. البيان الختامي الجماعي
    total_energy = sum(b.get('energy', 0) for b in bodies_list)
    genes_count = Counter(b.get('gene', 'S') for b in bodies_list)
    dominant_gene = max(genes_count, key=genes_count.get)
    gene_info = GENE_STYLE.get(dominant_gene, GENE_STYLE['S'])
    
    st.markdown(f"""
    <div class="summary-box">
        <h3 style='margin:0 0 15px 0; color:#FFD700;'>📜 البيان الختامي الموسع</h3>
        <p style='margin:8px 0;'>✅ تم رصد <b>{len(bodies_list)}</b> كائناً وجودياً.</p>
        <p style='margin:8px 0;'>🐪 الهيمنة الجينية: <b style='color:{gene_info["color"]};'>{gene_info['icon']} {gene_info['name']}</b></p>
        <p style='margin:8px 0;'>⚡ مجموع الطاقة الاستنطاقية: <b>{total_energy:.1f}</b></p>
        <p style='margin:8px 0;'>📚 المسار المكتشف: <b>{', '.join([b.get('root', '—') for b in bodies_list])}</b></p>
    </div>
    """, unsafe_allow_html=True)
    
    # 2. تفاصيل الاستنطاق الفردي
    st.markdown("### 🔍 تفاصيل المدارات المستنطقة")
    for b in bodies_list:
        color = b.get('color', '#4fc3f7')
        st.markdown(f"""
        <div class="insight-card" style="border-right-color: {color}">
            <b style="color:{color}; font-size: 1.2em;">📌 الجذر: {b['root']}</b> | {b['gene_display']}<br>
            <p style="margin-top:10px; color:#ddd;">🔮 <b>الاستنطاق:</b> {ensure_dot(b['insight'])}</p>
        </div>
        """, unsafe_allow_html=True)

# ==============================================================================
# [4] واجهة المستخدم الرئيسية
# ==============================================================================
tabs = st.tabs(["🔍 الاستنطاق المداري", "🌌 الرنين الجيني", "📈 اللوحة الوجودية"])

with tabs[0]:
    st.markdown("### 📍 مفاعل الاستنطاق الفوري")
    input_text = st.text_area("أدخل النص المراد استنطاقه:", height=100, placeholder="مثال: أحد، أرض، أب...")
    
    if st.button("🚀 تفعيل المفاعل السيادي", use_container_width=True):
        if input_text.strip():
            words = input_text.split()
            bodies = []
            
            for w in words:
                norm = normalize_root(w)
                if norm in db:
                    item = db[norm]
                    gene_code = item.get('gene', 'S')
                    g_style = GENE_STYLE.get(gene_code, GENE_STYLE['S'])
                    bodies.append({
                        "root": item['root'],
                        "orbit": item.get('orbit_id', 1),
                        "gene": gene_code,
                        "gene_display": f"{g_style['icon']} {g_style['name']}",
                        "insight": item.get('insight_radar', item.get('insight', 'بصيرة قيد التكوين.')),
                        "energy": float(item.get('weight', 1.0)) * 100,
                        "color": g_style['color']
                    })
            
            if bodies:
                st.session_state.active_bodies = bodies
                # عرض الرسم البياني
                df = pd.DataFrame(bodies)
                fig = px.scatter(df, x="root", y="orbit", size="energy", color="gene_display", 
                                 title="توزيع الأجسام في المدارات", color_discrete_sequence=px.colors.qualitative.Pastel)
                st.plotly_chart(fig, use_container_width=True)
                
                # عرض البيان الختامي
                display_sovereign_results(bodies)
            else:
                st.warning("⚠️ لم يتم العثور على جذور مطابقة في قاعدة البيانات.")

with tabs[1]:
    if 'active_bodies' in st.session_state:
        display_sovereign_results(st.session_state.active_bodies)
    else:
        st.info("قم بتفعيل المفاعل في التبويب الأول أولاً.")

with tabs[2]:
    st.markdown("### 📈 إحصائيات الميزان")
    if 'active_bodies' in st.session_state:
        df = pd.DataFrame(st.session_state.active_bodies)
        st.bar_chart(df['gene'].value_counts())
    else:
        st.info("لا توجد بيانات إحصائية حالياً.")
