import os
import json
from pathlib import Path

# =========================================================
# 1) تحديد المسار الأساسي للتطبيق
# =========================================================
BASE_DIR = Path(os.path.abspath(os.path.dirname(__file__)))

# =========================================================
# 2) جميع المسارات المحتملة للبحث عن الملفات
# =========================================================
SEARCH_DIRS = [
    BASE_DIR,
    BASE_DIR / "data",
    BASE_DIR / "qroot",
    BASE_DIR / "resources",
    BASE_DIR / "assets",
    BASE_DIR.parent,            # في حال كان app.py داخل مجلد فرعي
]

# =========================================================
# 3) دالة تحميل JSON السيادية
# =========================================================
def load_json(relative_path):
    """
    يبحث عن الملف في جميع المسارات المحتملة.
    إذا لم يجده → يرفع خطأ واضحًا.
    """
    for folder in SEARCH_DIRS:
        full_path = folder / relative_path
        if full_path.exists():
            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                raise RuntimeError(f"⚠️ فشل في قراءة الملف: {full_path}\nالسبب: {e}")

    # إذا لم يتم العثور على الملف في أي مكان
    search_list = "\n".join([str(p) for p in SEARCH_DIRS])
    raise FileNotFoundError(
        f"❌ الملف غير موجود: {relative_path}\n"
        f"🔍 تم البحث في المسارات التالية:\n{search_list}"
    )

# =========================================================
# 4) دالة رصد المسارات (للوحة التشخيص)
# =========================================================
def debug_paths():
    """
    تعرض جميع الملفات التي يمكن للنظام رؤيتها.
    مفيدة جدًا في Streamlit Cloud.
    """
    paths = []
    try:
        for root, dirs, files in os.walk(BASE_DIR, topdown=True):
            for f in files:
                paths.append(str(Path(root) / f))
    except:
        paths.append("❌ فشل نظام رصد المسارات")

    return paths
