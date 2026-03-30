import streamlit as st
import json
from pathlib import Path

st.title("🛡️ نظام الفحص السيادي - v30 Test")

# 1. تحديد المسارات
data_dir = Path("data")
files = {
    "الجذور": data_dir / "nibras_lexicon.json",
    "محرك الحروف": data_dir / "letter_engine.py",
    "المصفوفة": data_dir / "matrix_resonance.json"
}

# 2. فحص الوجود المادي للملفات
st.subheader("🔍 فحص وجود الملفات")
for name, path in files.items():
    if path.exists():
        st.success(f"✅ تم العثور على ملف {name} في: `{path}`")
    else:
        st.error(f"❌ ملف {name} مفقود! بحثنا في: `{path.absolute()}`")

# 3. فحص القدرة على القراءة (Parsing)
st.subheader("📖 فحص محتوى الجذور")
try:
    with open(files["الجذور"], "r", encoding="utf-8") as f:
        data = json.load(f)
        roots = data.get("roots", [])
        st.write(f"📊 عدد الجذور المرصودة: **{len(roots)}**")
        st.write("📝 عينة من أول جذر:")
        st.json(roots[0] if roots else "الملف فارغ")
except Exception as e:
    st.warning(f"⚠️ خطأ في قراءة ملف الجذور: {e}")

st.info("إذا ظهرت العلامات الخضراء أعلاه، فنحن جاهزون للإقلاع النهائي.")
