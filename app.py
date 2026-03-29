import streamlit as st
import plotly.graph_objects as go
import json
import os

# إعدادات الصفحة لتكون احترافية مثل صورة DeepSeek
st.set_page_config(page_title="Nibras Sovereign", layout="wide")

# دالة آمنة لقراءة الألوان
def get_safe_color(res, index):
    colors = ['#00E6FF', '#FF3D00', '#7C4DFF', '#00E676', '#FFC400']
    color = res.get('color', colors[index % len(colors)])
    if not color or not str(color).startswith('#'):
        return colors[index % len(colors)]
    return color

# دالة بناء الرادار (تم إصلاح خطأ الألوان فيها)
def create_radar_chart(results, labels):
    fig = go.Figure()
    for i, res in enumerate(results):
        color = get_safe_color(res, i)
        # تحويل الهكس إلى RGBA بأمان
        try:
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
            fill_rgba = f"rgba({r},{g},{b},0.3)"
        except:
            fill_rgba = "rgba(0, 230, 255, 0.3)"

        fig.add_trace(go.Scatterpolar(
            r=[res.get('mass', 5), res.get('velocity', 5), res.get('energy', 5), 
               res.get('awareness', 5), res.get('impact', 5), res.get('mass', 5)],
            theta=['الكتلة', 'السرعة', 'الطاقة', 'الوعي', 'الأثر', 'الكتلة'],
            fill='toself',
            name=labels[i],
            line=dict(color=color),
            fillcolor=fill_rgba
        ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white")
    )
    return fig

def main():
    st.markdown("<h1 style='text-align: center; color: #00E6FF;'>نبراس الرصد السيادي</h1>", unsafe_allow_html=True)
    
    # محاكاة البطاقات التي ظهرت في DeepSeek
    col1, col2, col3 = st.columns(3)
    
    # هنا نضع نتائج الرصد (مثال توضيحي للواجهة)
    with col1:
        st.markdown("<div style='background: #1E1E1E; padding: 20px; border-radius: 10px; border-top: 5px solid #00E6FF;'><h3>المسار الأول</h3><h2 style='color: #00E6FF;'>54.11</h2></div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div style='background: #1E1E1E; padding: 20px; border-radius: 10px; border-top: 5px solid #FF3D00;'><h3>المسار الثاني</h3><h2 style='color: #FF3D00;'>53.97</h2></div>", unsafe_allow_html=True)
        
    with col3:
        st.markdown("<div style='background: #1E1E1E; padding: 20px; border-radius: 10px; border-top: 5px solid #7C4DFF;'><h3>المسار الثالث</h3><h2 style='color: #7C4DFF;'>35.14</h2></div>", unsafe_allow_html=True)

    # الرادار الهندسي (الذي يميزنا عن DeepSeek)
    st.markdown("---")
    st.subheader("📊 هندسة الوعي (الرادار السيادي)")
    # (هنا يتم استدعاء بياناتك الحقيقية من JSON)
    # مثال لعرض الرادار
    sample_res = [{'mass': 8, 'velocity': 7, 'energy': 9, 'awareness': 6, 'impact': 8}]
    st.plotly_chart(create_radar_chart(sample_res, ["رصد الكلمة"]), use_container_width=True)

if __name__ == "__main__":
    main()
