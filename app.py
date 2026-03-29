import streamlit as st
import plotly.graph_objects as go
import json
import os

# 1. الإعدادات الأساسية
st.set_page_config(page_title="Nibras Sovereign", layout="wide")

# 2. وظيفة جلب البيانات (الصياد الماهر)
def load_data():
    files = {
        "roots": "data/quran_roots_complete.json",
        "lexicon": "data/nibras_lexicon.json",
        "letters": "data/sovereign_letters_v1.json"
    }
    loaded_data = {}
    for key, path in files.items():
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                loaded_data[key] = json.load(f)
            st.sidebar.success(f"✅ {key} محمل")
        else:
            st.sidebar.error(f"❌ {key} مفقود")
    return loaded_data

# 3. دالة رسم الرادار المحصنة (منع الخطأ السابق)
def draw_radar(data_list, labels):
    fig = go.Figure()
    colors = ['#00e6ff', '#ff3d00', '#7c4dff']
    
    for i, item in enumerate(data_list):
        color = colors[i % len(colors)]
        fig.add_trace(go.Scatterpolar(
            r=[item.get('mass', 5), item.get('velocity', 5), item.get('energy', 5), 
               item.get('awareness', 5), item.get('impact', 5), item.get('mass', 5)],
            theta=['الكتلة', 'السرعة', 'الطاقة', 'الوعي', 'الأثر', 'الكتلة'],
            fill='toself',
            name=labels[i],
            line=dict(color=color)
        ))
    
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 10])), showlegend=True)
    return fig

# 4. الواجهة البرمجية (الإدخال والرصد)
def main():
    st.title("🛡️ نبراس الرصد السيادي")
    db = load_data()
    
    st.subheader("إدخال المسارات")
    c1, c2, c3 = st.columns(3)
    with c1: p1 = st.text_area("المسار 1", height=150)
    with c2: p2 = st.text_area("المسار 2", height=150)
    with c3: p3 = st.text_area("المسار 3", height=150)
    
    if st.button("🚀 إطلاق الرصد"):
        results = []
        labels = []
        # هنا تتم عملية المعالجة بناءً على ملفات الـ JSON الخاصة بك
        for i, text in enumerate([p1, p2, p3]):
            if text:
                # محاكاة للحسابات لضمان عمل الواجهة (استبدلها بمعادلاتك)
                results.append({'mass': 7, 'velocity': 8, 'energy': 6, 'awareness': 9, 'impact': 7})
                labels.append(f"مسار {i+1}")
        
        if results:
            st.plotly_chart(draw_radar(results, labels), use_container_width=True)
        else:
            st.warning("أدخل نصاً لتبدأ")

if __name__ == "__main__":
    main()
