أفهمك تماماً يا محمد، من خلال الصور التي أرفقتها، الفجوة واضحة:
 1. **في الصورة الثالثة (v29.0):** كان العرض يتم عبر **جدول (Table)**، وهو ما يسبب "البتر" وظهور النقاط ... في خانة الاستنطاق.
 2. **في الصورة الرابعة:** بدأنا ننتقل إلى **"نظام الكروت"**، لكن الواجهة تفتقر إلى "الهيبة" والبيان الختامي الملون الذي اتفقنا عليه.
أنت تريد **المحتوى الكامل** (بدون بتر) مع **الواجهة السيادية** (الصندوق الذهبي والخطوط الواضحة).
إليك التعديل النهائي لملف app.py ليعيد الواجهة كما كانت في خيالك وبنفس القوة البرمجية، مع التأكد من أن "البيان الختامي" يظهر كقطعة واحدة مهيبة:
### 🛡️ النسخة السيادية (v34.0) - إعادة الواجهة والبيان
```python
# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os
import re
from collections import Counter

# ==============================================================================
# [1] الواجهة السيادية - إعادة الهيبة البصرية
# ==============================================================================
st.set_page_config(page_title="نبراس السيادي", page_icon="🛡️", layout="wide")

st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background: #050505; color: #e0e0e0; direction: rtl; }
    /* صندوق البيان الختامي الموسع - كما في وصفك */
    .summary-box {
        background: linear-gradient(135deg, #0d1a0d 0%, #000000 100%);
        padding: 30px; border-radius: 15px; 
        border: 2px solid #1a3a1a; border-right: 8px solid #FFD700;
        margin-bottom: 40px; box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }
    /* كروت الاستنطاق - تمنع البتر نهائياً */
    .insight-card {
        background: #111; padding: 20px; border-radius: 10px;
        border-right: 5px solid #4fc3f7; margin-bottom: 20px;
        border-bottom: 1px solid #222;
    }
    .root-header { font-size: 1.4em; font-weight: bold; margin-bottom: 10px; }
    .insight-text { font-size: 1.15em; line-height: 1.8; color: #ccc; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# [2] المحرك الهيكلي
# ==============================================================================
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
    if not os.path.exists(path): return {}
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return {normalize_root(item['root']): item for item in data}

db = load_db()

# ==============================================================================
# [3] عرض النتائج (البيان الختامي + الكروت)
# ==============================================================================
def display_nibras_interface(bodies):
    if not bodies: return
    
    # حساب الهيمنة الجينية
    genes = [b['gene'] for b in bodies]
    dominant = max(set(genes), key=genes.count)
    g_info = GENE_STYLE.get(dominant, GENE_STYLE['S'])
    
    # 1. البيان الختامي الموسع (Header)
    st.markdown(f"""
    <div class="summary-box">
        <h2 style='color:#FFD700; margin-top:0;'>📜 البيان الختامي الموسع</h2>
        <div style='display: flex; gap: 40px; margin-top: 15px;'>
            <div>✅ الجذور المستنطقة: <b>{len(bodies)}</b></div>
            <div>🐪 الهيمنة: <b style='color:{g_info["color"]}'>{g_info['icon']} {g_info['name']}</b></div>
            <div>⚡ المسار: <b>{', '.join([b['root'] for b in bodies])}</b></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 2. كروت الاستنطاق الفردية (Content)
    for b in bodies:
        st.markdown(f"""
        <div class="insight-card" style="border-right-color: {b['color']}">
            <div class="root-header" style="color: {b['color']}">📌 الجذر: {b['root']} | {b['gene_display']}</div>
            <div class="insight-text">
                <b>الاستنطاق:</b> {b['insight']}{'.' if not b['insight'].endswith('.') else ''}
            </div>
        </div>
        """, unsafe_allow_html=True)

# ==============================================================================
# [4] التنفيذ الرئيسي
# ==============================================================================
input_text = st.text_area("أدخل النص للاستنطاق:", height=100, placeholder="أدخل كلماتك هنا...")

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
                    "gene_display": f"{GENE_STYLE[g_code]['icon']} {GENE_STYLE[g_code]['name']}",
                    "insight": item.get('insight_radar', item.get('insight', 'بصيرة قيد التكوين.')),
                    "color": GENE_STYLE[g_code]['color']
                })
        
        if bodies:
            # عرض الرسم البياني
            fig = px.scatter(pd.DataFrame(bodies), x="root", y="orbit", color="gene_display", 
                             template="plotly_dark", size_max=30)
            st.plotly_chart(fig, use_container_width=True)
            
            # عرض الواجهة السيادية
            display_nibras_interface(bodies)
        else:
            st.error("لم يتم العثور على جذور مطابقة.")

```
### **ما الذي استعدناه في هذه النسخة؟**
 1. **البيان الختامي:** عاد الصندوق الكبير في الأعلى الذي يلخص "المشهد الوجودي" كاملاً قبل الدخول في التفاصيل.
 2. **بصمة الجذر:** كل كارت استنطاق يظهر بلون "الجين" الخاص به (سماوي، ذهبي، أخضر، أحمر) كما في الصور.
 3. **سلامة النص:** استخدمنا نظام الكروت لضمان أن يظهر النص كاملاً (كما تراه في صورتك الرابعة) ولكن بتنسيق "سيادي" أفضل.
**خِت فِت.** ارفع هذا الكود، وسيعود النظام لأصله وبنيته التي ترضيك. هل الواجهة الآن كما تريد؟
