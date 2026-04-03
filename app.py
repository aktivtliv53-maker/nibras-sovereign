import streamlit as st
import pandas as pd
import json
import os
import re

# 1. الإعدادات البصرية السيادية
st.set_page_config(page_title="نبراس السيادي", page_icon="🛡️", layout="wide")

st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background: #050505; color: #e0e0e0; direction: rtl; }
    .summary-box { background: #0d1a0d; padding: 25px; border-radius: 12px; border-right: 8px solid #FFD700; margin-bottom: 30px; }
    .insight-card { background: #111; padding: 20px; border-radius: 10px; border-right: 5px solid #4fc3f7; margin-bottom: 15px; line-height: 1.8; }
</style>
""", unsafe_allow_html=True)

GENE_STYLE = {
    'C': {'name': 'الإبل', 'color': '#4fc3f7', 'icon': '🐪'},
    'B': {'name': 'البقر', 'color': '#FFD700', 'icon': '🐄'},
    'S': {'name': 'الضأن', 'color': '#81c784', 'icon': '🐑'},
    'G': {'name': 'المعز', 'color': '#ff5252', 'icon': '🐐'}
}

# دالة التطهير الأساسية (بدون أي تعقيد)
def simple_normalize(text):
    if not text: return ""
    t = str(text).strip().replace("أ", "ا").replace("إ", "ا").replace("آ", "ا")
    return re.sub(r'[\u064B-\u065F]', '', t)

# تحميل البيانات مع فحص الأخطاء
@st.cache_data
def load_db():
    # البحث في المجلد الرئيسي وفي مجلد data
    potential_paths = ["nibras_lexicon.json", "data/nibras_lexicon.json"]
    for p in potential_paths:
        if os.path.exists(p):
            try:
                with open(p, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                # بناء القاموس بالمطابقة الصافية
                return {simple_normalize(item['root']): item for item in data}
            except: continue
    return None

db = load_db()

# --- واجهة الاستخدام ---
tab1, tab2, tab3 = st.tabs(["🔍 الاستنطاق", "📜 البيان", "📈 المدارات"])

with tab1:
    if db is None:
        st.error("❌ الرادار معطل: لم يتم العثور على ملف nibras_lexicon.json في المستودع.")
    else:
        st.success(f"✅ الرادار متصل: تم تحميل {len(db)} جذراً بنجاح.")
        
    input_text = st.text_area("أدخل الجذور (افصل بينها بمسافة):", height=100)
    
    if st.button("🚀 تفعيل المفاعل"):
        if input_text.strip() and db:
            # تقطيع النص المدخل إلى كلمات بسيطة
            words = input_text.split()
            bodies = []
            for w in words:
                norm_w = simple_normalize(w)
                if norm_w in db:
                    item = db[norm_w]
                    g_code = item.get('gene', 'S')
                    bodies.append({
                        "root": item['root'],
                        "orbit": item.get('orbit_id', 1),
                        "gene": g_code,
                        "insight": item.get('insight_radar', item.get('insight', '...')),
                        "color": GENE_STYLE.get(g_code, GENE_STYLE['S'])['color'],
                        "gene_display": f"{GENE_STYLE.get(g_code, GENE_STYLE['S'])['icon']} {GENE_STYLE.get(g_code, GENE_STYLE['S'])['name']}"
                    })
            
            if bodies:
                st.session_state.active_bodies = bodies
                st.rerun() # إعادة التشغيل لإظهار النتائج في التبويبات
            else:
                st.warning("⚠️ لم يتم العثور على هذه الجذور. تأكد من كتابة 'الجذر' مجرداً (مثل: احد، صمد، ارض).")

with tab2:
    if 'active_bodies' in st.session_state:
        bodies = st.session_state.active_bodies
        st.markdown(f'<div class="summary-box"><h2 style="color:#FFD700;">📜 البيان الختامي الموسع</h2><p>تم استنطاق {len(bodies)} جذراً.</p></div>', unsafe_allow_html=True)
        for b in bodies:
            st.markdown(f'<div class="insight-card" style="border-right-color:{b["color"]}"><b>📌 {b["root"]}</b> | {b["gene_display"]}<br>{b["insight"]}</div>', unsafe_allow_html=True)
    else:
        st.info("لا توجد بيانات.")

with tab3:
    if 'active_bodies' in st.session_state:
        df = pd.DataFrame(st.session_state.active_bodies)
        import plotly.express as px
        st.plotly_chart(px.scatter(df, x="root", y="orbit", color="gene_display", template="plotly_dark"))
