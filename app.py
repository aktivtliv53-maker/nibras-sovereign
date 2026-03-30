import streamlit as st
import json
from pathlib import Path

st.title("🛡️ نظام الفحص السيادي - v30 Test")

# 1. تحديد المسارات بناءً على أسماء ملفاتك الحالية في GitHub
data_dir = Path("data")
files = {
    "الجذور": data_dir / "nibras_lexicon.json",
    "محرك الحروف": data_dir / "sovereign_letters_v1.json",
    "المصفوفة": data_dir / "matrix_data.json"
}

# 2. فحص الوجود المادي للملفات
st.subheader("🔍 فحص وجود الملفات")
for name, path in files.items():
    if path.exists():
        st.success(f"✅ تم العثور على ملف {name} في: `{path}`")
    else:
        st.error(f"❌ ملف {name} مفقود! بحثنا في: `{path}`")

# 3. فحص القدرة على القراءة (Parsing)
st.subheader("📖 فحص محتوى الجذور")
try:
    with open(files["الجذور"], "r", encoding="utf-8") as f:
        data = json.load(f)
        # تعديل المنطق ليتناسب مع هيكلية ملفك (سواء كانت قائمة أو قاموس)
        if isinstance(data, dict) and "roots" in data:
            roots = data["roots"]
        elif isinstance(data, list):
            roots = data
        else:
            roots = []
            
        st.write(f"📊 عدد الجذور المرصودة: **{len(roots)}**")
        if roots:
            st.write("📝 عينة من أول جذر:")
            st.json(roots[0])
except Exception as e:
    st.error(f"⚠️ خطأ في قراءة ملف الجذور: {e}")

st.info("إذا ظهرت العلامات الخضراء الآن، فنحن جاهزون للإقلاع النهائي بالأسماء التي اخترتها أنت.")
