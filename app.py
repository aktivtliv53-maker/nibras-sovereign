import streamlit as st
import pandas as pd

st.set_page_config(page_title="Nibras Sovereign v26.2.1", layout="wide")

# ---------------------------------------------------------
# 0. إعداد الحالة العامة
# ---------------------------------------------------------
if "active" not in st.session_state:
    st.session_state.active = False

state = st.session_state

# ---------------------------------------------------------
# 1. تعريف GENE_STYLE السيادي
# ---------------------------------------------------------
GENE_STYLE = {
    "A": {"icon": "🜂", "meaning": "قوة اليسر والانفتاح"},
    "B": {"icon": "🜁", "meaning": "قوة الانضباط والاتساق"},
    "C": {"icon": "🜄", "meaning": "قوة الاحتواء والرحمة"},
    "D": {"icon": "🜃", "meaning": "قوة الجذور والرسوخ"},
}

# ---------------------------------------------------------
# 2. واجهة الإدخال
# ---------------------------------------------------------
st.title("🧭 Nibras Sovereign v26.2.1")

uploaded_file = st.file_uploader("ارفع ملف الجذور (CSV)", type=["csv"])

if uploaded_file:
    df_data = pd.read_csv(uploaded_file)
    state.active = True
else:
    df_data = pd.DataFrame()

# ---------------------------------------------------------
# 3. التبويبات
# ---------------------------------------------------------
tabs = st.tabs([
    "📥 الإدخال",
    "🧬 الجينات",
    "🌌 المدار",
    "📊 التحليل",
    "⚖️ الميزان السيادي",
    "🧠 الوعي الفوقي"
])

# ---------------------------------------------------------
# 4. تبويب الإدخال
# ---------------------------------------------------------
with tabs[0]:
    st.header("📥 الإدخال")
    st.write("ارفع ملف CSV يحتوي الأعمدة: root, gene, energy, vx, vy")

# ---------------------------------------------------------
# 5. تبويب الجينات
# ---------------------------------------------------------
with tabs[1]:
    st.header("🧬 الجينات")
    if not df_data.empty:
        st.dataframe(df_data, use_container_width=True)
    else:
        st.info("بانتظار رفع البيانات.")

# ---------------------------------------------------------
# 6. تبويب المدار
# ---------------------------------------------------------
with tabs[2]:
    st.header("🌌 المدار")
    if not df_data.empty:
        st.dataframe(df_data[['root', 'energy', 'vx', 'vy']], use_container_width=True)
    else:
        st.info("بانتظار البيانات.")

# ---------------------------------------------------------
# 7. تبويب التحليل
# ---------------------------------------------------------
with tabs[3]:
    st.header("📊 التحليل")
    if not df_data.empty:
        st.dataframe(df_data.describe(), use_container_width=True)
    else:
        st.info("بانتظار البيانات.")

# ---------------------------------------------------------
# 8. تبويب الميزان السيادي v26.2.1
# ---------------------------------------------------------
with tabs[4]:  # ⚖️ الميزان السيادي v26.2.1 - طبقة النطق والقراءة
    st.markdown("### ⚖️ ميزان الجذور والقراءة السيادية")

    if not df_data.empty:

        # 1. تثبيت وترتيب البيانات
        df_speech = df_data.copy().sort_values('energy', ascending=False).reset_index(drop=True)

        # 2. محركات الترجمة
        def get_energy_level(e):
            if e >= 1200: return "🔝 هيمنة تأسيسية"
            if e >= 1000: return "🔥 حضور قوي جداً"
            if e >= 900:  return "✨ حضور قوي"
            if e >= 750:  return "⚡ حضور متوسط راجح"
            return "🌱 حضور تأسيسي"

        def get_motion_sense(vx, vy):
            h = "اتساع خارجي" if vx > 0.05 else ("انكماش مركزي" if vx < -0.05 else "اتزان أفقي")
            v = "صعود وانكشاف" if vy > 0.05 else ("تجذير وترسيب" if vy < -0.05 else "ثبات مقامي")
            return f"{h} | {v}"

        # 3. الأعمدة السيادية
        df_speech['القطب الوظيفي'] = df_speech['gene'].apply(
            lambda x: f"{GENE_STYLE.get(x, {}).get('icon', '🧬')} {GENE_STYLE.get(x, {}).get('meaning', 'قطب غير معرّف')}"
        )
        df_speech['رتبة الحضور'] = df_speech['energy'].apply(get_energy_level)
        df_speech['الأثر المداري'] = df_speech.apply(
            lambda r: get_motion_sense(r['vx'], r['vy']), axis=1
        )

        # 4. عرض الجدول الناطق
        st.dataframe(
            df_speech[['root', 'القطب الوظيفي', 'energy', 'رتبة الحضور', 'الأثر المداري']],
            column_config={
                "root": "الجذر المستنطق",
                "energy": "الكثافة الخام",
                "القطب الوظيفي": "الجوهر السيادي",
                "رتبة الحضور": "مستوى التجلي",
                "الأثر المداري": "الانحياز الحركي"
            },
            use_container_width=True,
            hide_index=True
        )

        # 5. استخراج سيد المدار
        top_root = df_speech.iloc[0]['root']
        top_gene = df_speech.iloc[0]['gene']
        top_energy = df_speech.iloc[0]['energy']
        top_vx = df_speech.iloc[0]['vx']
        top_vy = df_speech.iloc[0]['vy']

        top_pole = GENE_STYLE.get(top_gene, {}).get('meaning', 'غير معرّف')
        top_icon = GENE_STYLE.get(top_gene, {}).get('icon', '🧬')
        top_rank = get_energy_level(top_energy)
        top_motion = get_motion_sense(top_vx, top_vy)

        # 6. البطاقة السيادية الضخمة (Hero Card – Dark Frame)
        card_css = """
        <style>
        .hero-card {
            background: #0d0d14;
            border-radius: 20px;
            padding: 30px;
            margin-top: 25px;
            border: 2px solid rgba(120, 200, 255, 0.45);
            box-shadow: 0 0 25px rgba(120, 200, 255, 0.35);
        }
        .hero-title {
            font-size: 38px;
            font-weight: 800;
            color: #e8f1ff;
            text-align: center;
            margin-bottom: 10px;
        }
        .hero-icon {
            font-size: 60px;
            text-align: center;
            margin-bottom: 15px;
        }
        .hero-line {
            font-size: 22px;
            color: #d0d8e8;
            text-align: center;
            margin: 6px 0;
        }
        </style>
        """

        st.markdown(card_css, unsafe_allow_html=True)

        hero_html = f"""
        <div class="hero-card">
            <div class="hero-icon">{top_icon}</div>
            <div class="hero-title">سيد المدار: {top_root}</div>
            <div class="hero-line">القطب السيادي: {top_pole}</div>
            <div class="hero-line">رتبة الحضور: {top_rank}</div>
            <div class="hero-line">الأثر المداري: {top_motion}</div>
            <div class="hero-line">الطاقة: {top_energy}</div>
        </div>
        """

        st.markdown(hero_html, unsafe_allow_html=True)

    else:
        st.info("بانتظار استنطاق المدار لملء الموازين.")

# ---------------------------------------------------------
# 9. تبويب الوعي الفوقي
# ---------------------------------------------------------
with tabs[5]:
    st.header("🧠 الوعي الفوقي")
    st.write("طبقة الوعي الفوقي ستُفعّل في الإصدارات القادمة.")
