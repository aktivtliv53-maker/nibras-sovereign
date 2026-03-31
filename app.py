import streamlit as st
import json
import os
import re
import math
from datetime import datetime

# =========================================================
# إعداد الصفحة
# =========================================================
st.set_page_config(
    page_title="Quranic Root Resonance System",
    page_icon="🜂",
    layout="wide"
)

# =========================================================
# إعدادات الملفات
# =========================================================
ROOTS_FILE = "quranic_roots_full.json"
CLEANED_ROOTS_FILE = "quranic_roots_full.cleaned.json"

# =========================================================
# أدوات تنظيف JSON
# =========================================================
def clean_json_text(text: str) -> str:
    """
    تنظيف النص من المشاكل الشائعة في ملفات JSON العربية:
    - إزالة BOM
    - استبدال الفاصلة العربية
    - تحويل الاقتباسات الذكية
    - إزالة الأحرف الخفية
    """
    if not text:
        return text

    # إزالة BOM من البداية
    text = text.lstrip("\ufeff")

    # استبدال الفاصلة العربية بالفاصلة الإنجليزية
    text = text.replace("،", ",")

    # تحويل الاقتباسات الذكية إلى اقتباس عادي
    smart_quotes_map = {
        "“": '"',
        "”": '"',
        "„": '"',
        "‟": '"',
        "‘": "'",
        "’": "'"
    }
    for bad, good in smart_quotes_map.items():
        text = text.replace(bad, good)

    # إزالة أحرف مخفية شائعة (Zero-width + bidi controls)
    hidden_chars = [
        "\u200b",  # zero width space
        "\u200c",  # zero width non-joiner
        "\u200d",  # zero width joiner
        "\u2060",  # word joiner
        "\ufeff",  # BOM
        "\u202a", "\u202b", "\u202c", "\u202d", "\u202e",  # bidi
        "\u2066", "\u2067", "\u2068", "\u2069"
    ]
    for ch in hidden_chars:
        text = text.replace(ch, "")

    return text

def save_cleaned_json_if_valid(cleaned_text: str, output_path: str):
    """
    يحفظ نسخة نظيفة من JSON فقط إذا كانت صالحة
    """
    try:
        parsed = json.loads(cleaned_text)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(parsed, f, ensure_ascii=False, indent=2)
        return True, parsed
    except Exception as e:
        return False, str(e)

def safe_load_json(file_path: str, cleaned_output_path: str = None):
    """
    تحميل JSON بشكل آمن:
    1) محاولة مباشرة
    2) إذا فشلت -> تنظيف تلقائي
    3) إذا نجح التنظيف -> حفظ نسخة نظيفة وإرجاع البيانات
    4) إذا فشل -> إظهار رسالة خطأ واضحة
    """
    if not os.path.exists(file_path):
        return None, f"❌ الملف غير موجود: {file_path}"

    # قراءة خام
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            raw_text = f.read()
    except Exception as e:
        return None, f"⚠️ تعذر فتح الملف: {e}"

    # المحاولة الأولى: قراءة مباشرة
    try:
        data = json.loads(raw_text)
        return data, None
    except json.JSONDecodeError as original_error:
        # المحاولة الثانية: تنظيف النص
        cleaned_text = clean_json_text(raw_text)

        try:
            data = json.loads(cleaned_text)

            # حفظ نسخة منظفة إن طُلب
            if cleaned_output_path:
                try:
                    with open(cleaned_output_path, "w", encoding="utf-8") as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                except Exception:
                    pass

            return data, f"⚠️ تم اكتشاف مشكلة في JSON الأصلي وتم إصلاحها تلقائيًا.\nتم استخدام نسخة منظفة من الملف."

        except json.JSONDecodeError as cleaned_error:
            # تجهيز تقرير واضح
            lines = cleaned_text.splitlines()
            bad_line = ""
            context = []

            if 1 <= cleaned_error.lineno <= len(lines):
                start = max(0, cleaned_error.lineno - 3)
                end = min(len(lines), cleaned_error.lineno + 2)
                context = lines[start:end]
                bad_line = lines[cleaned_error.lineno - 1]

            error_message = (
                f"⚠️ تعذر قراءة ملف الجذور حتى بعد التنظيف التلقائي.\n\n"
                f"الخطأ الأصلي:\n"
                f"- السطر: {original_error.lineno}\n"
                f"- العمود: {original_error.colno}\n"
                f"- الرسالة: {original_error.msg}\n\n"
                f"بعد التنظيف:\n"
                f"- السطر: {cleaned_error.lineno}\n"
                f"- العمود: {cleaned_error.colno}\n"
                f"- الرسالة: {cleaned_error.msg}\n\n"
            )

            if bad_line:
                error_message += f"السطر المشكوك فيه:\n{bad_line}\n\n"

            if context:
                error_message += "سياق قريب من الخطأ:\n"
                start_num = max(1, cleaned_error.lineno - 2)
                for idx, line in enumerate(context, start=start_num):
                    prefix = ">> " if idx == cleaned_error.lineno else "   "
                    error_message += f"{prefix}{idx}: {line}\n"

            return None, error_message

    except Exception as e:
        return None, f"⚠️ خطأ غير متوقع أثناء تحميل JSON: {e}"

# =========================================================
# تحميل بيانات الجذور
# =========================================================
@st.cache_data
def load_roots_data():
    data, msg = safe_load_json(ROOTS_FILE, CLEANED_ROOTS_FILE)
    return data, msg

# =========================================================
# بناء فهرس الجذور
# =========================================================
def build_root_index(roots_data):
    """
    يحول البيانات من صيغة المدارات إلى فهرس سريع:
    {
      "root_name": {
         "orbit": "...",
         "weight": ...,
         "insight": "..."
      }
    }
    """
    root_index = {}

    if not isinstance(roots_data, list):
        return root_index

    for orbit_block in roots_data:
        orbit_name = orbit_block.get("orbit", "غير معروف")
        roots = orbit_block.get("roots", [])

        if not isinstance(roots, list):
            continue

        for root in roots:
            name = str(root.get("name", "")).strip()
            if not name:
                continue

            root_index[name] = {
                "orbit": orbit_name,
                "weight": float(root.get("weight", 1.0)),
                "insight": str(root.get("insight", "لا توجد بصيرة مفسرة لهذا الجذر")).strip()
            }

    return root_index

# =========================================================
# تحويل النص إلى جذور محتملة
# =========================================================
def normalize_arabic(text: str) -> str:
    """
    تبسيط النص العربي للمطابقة المرنة
    """
    if not text:
        return ""

    text = text.strip()

    replacements = {
        "أ": "ا",
        "إ": "ا",
        "آ": "ا",
        "ى": "ي",
        "ة": "ه",
        "ؤ": "و",
        "ئ": "ي"
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    # إزالة التشكيل
    text = re.sub(r"[\u064B-\u065F\u0670]", "", text)

    return text

def find_matching_roots(user_text: str, root_index: dict):
    """
    يحاول استخراج الجذور الموجودة في النص:
    - مطابقة مباشرة
    - مطابقة بعد التطبيع
    - مطابقة احتواء جزئي
    """
    found = []

    user_norm = normalize_arabic(user_text)

    # خريطة مطبعة
    normalized_map = {}
    for root_name in root_index.keys():
        normalized_map[normalize_arabic(root_name)] = root_name

    # 1) مطابقة مباشرة على النص الكامل
    if user_text in root_index:
        found.append(user_text)

    # 2) مطابقة بعد التطبيع على النص الكامل
    if user_norm in normalized_map:
        found.append(normalized_map[user_norm])

    # 3) تقسيم النص لكلمات ومحاولة المطابقة
    words = re.findall(r"[\u0600-\u06FF]+", user_text)
    for w in words:
        w_norm = normalize_arabic(w)

        if w in root_index and w not in found:
            found.append(w)

        if w_norm in normalized_map:
            root_name = normalized_map[w_norm]
            if root_name not in found:
                found.append(root_name)

        # مطابقة احتواء جزئي
        for root_name in root_index.keys():
            rn = normalize_arabic(root_name)

            if len(rn) >= 3:
                if rn in w_norm or w_norm in rn:
                    if root_name not in found:
                        found.append(root_name)

    return found

# =========================================================
# حساب الرنين
# =========================================================
def compute_resonance(found_roots, root_index):
    """
    حساب درجة رنين بسيطة قابلة للتوسعة
    """
    if not found_roots:
        return {
            "score": 0.0,
            "average_weight": 0.0,
            "dominant_orbit": "غير محدد"
        }

    weights = []
    orbit_counter = {}

    for root in found_roots:
        info = root_index.get(root, {})
        weight = info.get("weight", 1.0)
        orbit = info.get("orbit", "غير معروف")

        weights.append(weight)
        orbit_counter[orbit] = orbit_counter.get(orbit, 0) + 1

    avg_weight = sum(weights) / len(weights)
    score = avg_weight * len(found_roots)

    dominant_orbit = max(orbit_counter, key=orbit_counter.get) if orbit_counter else "غير محدد"

    return {
        "score": round(score, 3),
        "average_weight": round(avg_weight, 3),
        "dominant_orbit": dominant_orbit
    }

# =========================================================
# واجهة التطبيق
# =========================================================
st.title("🜂 Quranic Root Resonance System")
st.caption("نظام رنين الجذور القرآنية — نسخة مستقرة مع تنظيف JSON تلقائي")

# تحميل البيانات
roots_data, load_message = load_roots_data()

if load_message:
    if roots_data is not None:
        st.warning(load_message)
    else:
        st.error(load_message)
        st.stop()

root_index = build_root_index(roots_data)

if not root_index:
    st.error("❌ تم تحميل الملف لكن لم يتم استخراج أي جذور صالحة.")
    st.stop()

# =========================================================
# الشريط الجانبي
# =========================================================
with st.sidebar:
    st.header("📊 معلومات النظام")

    total_orbits = len(roots_data) if isinstance(roots_data, list) else 0
    total_roots = len(root_index)

    st.metric("عدد المدارات", total_orbits)
    st.metric("عدد الجذور المفهرسة", total_roots)

    if os.path.exists(CLEANED_ROOTS_FILE):
        st.success(f"تم إنشاء نسخة منظفة:\n{CLEANED_ROOTS_FILE}")

    st.markdown("---")
    st.write("**صيغة الإدخال المقترحة:**")
    st.write("- جذر واحد: `بصير`")
    st.write("- عدة جذور: `نور بصيرة كشف`")
    st.write("- عبارة حرة: `أبحث عن النور الداخلي والبصيرة`")

# =========================================================
# منطقة الإدخال
# =========================================================
st.subheader("🔍 أدخل الجذر أو العبارة")

user_input = st.text_area(
    "أدخل هنا:",
    height=120,
    placeholder="مثال: نور بصيرة كشف"
)

analyze_btn = st.button("تحليل الرنين")

# =========================================================
# التحليل
# =========================================================
if analyze_btn:
    if not user_input.strip():
        st.warning("يرجى إدخال نص للتحليل.")
    else:
        found_roots = find_matching_roots(user_input, root_index)
        resonance = compute_resonance(found_roots, root_index)

        st.subheader("✨ نتائج التحليل")

        c1, c2, c3 = st.columns(3)
        c1.metric("عدد الجذور المطابقة", len(found_roots))
        c2.metric("متوسط الوزن", resonance["average_weight"])
        c3.metric("درجة الرنين", resonance["score"])

        st.markdown(f"**المدار الغالب:** `{resonance['dominant_orbit']}`")

        st.markdown("---")

        if not found_roots:
            st.info("لم يتم العثور على جذور مطابقة واضحة في النص.")
        else:
            st.subheader("📚 الجذور المستخرجة")

            for root in found_roots:
                info = root_index.get(root, {})
                orbit = info.get("orbit", "غير معروف")
                weight = info.get("weight", 1.0)
                insight = info.get("insight", "لا توجد بصيرة مفسرة لهذا الجذر")

                with st.expander(f"{root}  |  الوزن: {weight}"):
                    st.write(f"**المدار:** {orbit}")
                    st.write(f"**البصيرة:** {insight}")

        st.markdown("---")
        st.subheader("🧭 قراءة مختصرة")

        if found_roots:
            insights = []
            for root in found_roots[:5]:
                insights.append(f"- **{root}** → {root_index[root]['insight']}")

            st.markdown("\n".join(insights))
        else:
            st.write("لا توجد قراءة لأن النص لم يُنتج جذورًا قابلة للمطابقة.")

# =========================================================
# قسم استكشاف الجذور
# =========================================================
st.markdown("---")
st.subheader("🗂️ استكشاف الجذور")

search_root = st.text_input("ابحث عن جذر محدد:")

if search_root.strip():
    search_norm = normalize_arabic(search_root)
    matches = []

    for root_name, info in root_index.items():
        rn = normalize_arabic(root_name)
        if search_norm in rn or rn in search_norm:
            matches.append((root_name, info))

    if matches:
        st.success(f"تم العثور على {len(matches)} نتيجة")
        for root_name, info in matches[:30]:
            with st.expander(f"{root_name} | {info['weight']}"):
                st.write(f"**المدار:** {info['orbit']}")
                st.write(f"**البصيرة:** {info['insight']}")
    else:
        st.info("لا توجد نتائج مطابقة.")

# =========================================================
# التذييل
# =========================================================
st.markdown("---")
st.caption(f"آخر تشغيل: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
