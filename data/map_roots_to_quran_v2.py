import json
import re
from collections import Counter, defaultdict

INPUT_FILE = "quran_roots_complete.json"
QURAN_FILE = "quran.json"
OUTPUT_FILE = "quran_roots_mapped.json"

# -----------------------------
# 1) تنظيف العربية
# -----------------------------
def normalize_arabic(w):
    if not w:
        return ""
    w = w.strip()
    w = w.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا")
    w = w.replace("ة", "ه").replace("ى", "ي")
    w = re.sub(r"[ًٌٍَُِّْـ]", "", w)
    return re.sub(r"[^ء-ي]", "", w)

# -----------------------------
# 2) استخراج الجذر الخام من LEM:
# -----------------------------
def extract_raw_root(raw):
    if not raw.startswith("LEM:"):
        return None
    raw = raw.split("LEM:")[1]
    return normalize_arabic(raw)

# -----------------------------
# 3) استخراج الجذر الثلاثي
# -----------------------------
def extract_triliteral(root):
    root = re.sub(r"(.)\1", r"\1", root)
    cleaned = re.sub(r"[اوي]", "", root)
    if len(cleaned) == 3:
        return cleaned
    return cleaned[:3] if len(cleaned) > 3 else root[:3]

# -----------------------------
# 4) المعاني الأساسية (نواة قابلة للتوسعة)
# -----------------------------
ROOT_MEANINGS = {
    "ابو": "الأصل والنسب",
    "اخر": "التأخير",
    "ازر": "القوة والدعم",
    "الو": "النعمة",
    "انف": "البداية",
    "برك": "البركة",
    "غفر": "الستر",
    "رحم": "الرحمة",
    "نصر": "الدعم والقوة",
    "كتب": "الكتابة والتقدير"
}

def get_root_meaning(root):
    return ROOT_MEANINGS.get(root, "—")

# -----------------------------
# 5) استخراج المشتقات من القرآن
# -----------------------------
def extract_derivatives(root, quran):
    derivatives = set()
    for ayah in quran:
        words = normalize_arabic(ayah["text"]).split()
        for w in words:
            if root in w:
                derivatives.add(w)
    return sorted(list(derivatives))

# -----------------------------
# 6) الوزن الصرفي (تقريبي)
# -----------------------------
def detect_pattern(word, root):
    if re.match(r"م..و.", word):
        return "مفعول"
    if re.match(r"م..ا.", word):
        return "مفعال"
    if re.match(r"..ا..", word):
        return "فعال"
    if re.match(r"..ي..", word):
        return "فعيل"
    if re.match(r"ا..", word):
        return "أفعل"
    if re.match(r"ت..", word):
        return "تفعّل"
    return "—"

# -----------------------------
# 7) نوع الفعل
# -----------------------------
def detect_verb_type(word):
    if word.startswith("ي"):
        return "فعل مضارع"
    if word.startswith("ت"):
        return "فعل مضارع أو أمر"
    if word.endswith("وا"):
        return "فعل ماضٍ جمع"
    if word.endswith("ت"):
        return "فعل ماضٍ"
    if word.startswith("ا"):
        return "فعل أمر"
    return "—"

# -----------------------------
# 8) باب الفعل (placeholder للتوسعة)
# -----------------------------
def detect_verb_bab(word):
    return "—"

# -----------------------------
# 9) الوزن الدلالي + المجال الدلالي
# -----------------------------
def get_semantic_weight(root):
    if root in ["نصر", "ازر", "قوي", "غلب"]:
        return "قوة"
    if root in ["مشي", "سير", "ذهب", "رجع"]:
        return "حركة"
    if root in ["ثبت", "قرار", "ركن"]:
        return "ثبات"
    if root in ["خرج", "دخل", "عبر"]:
        return "انتقال"
    if root in ["علم", "فهم", "عقل", "ذكر"]:
        return "إدراك"
    if root in ["الو", "رزق", "برك", "فضل"]:
        return "نعمة"
    return "—"

def get_semantic_domain(root):
    if root in ["يوم", "دهر", "حين", "وقت"]:
        return "زمن"
    if root in ["ارض", "سماء", "بلد", "دار"]:
        return "مكان"
    if root in ["واحد", "اثن", "ثلاث", "كثر"]:
        return "عدد"
    if root in ["مشي", "سير", "ركض", "جري"]:
        return "حركة"
    if root in ["علم", "فهم", "عرف", "ذكر"]:
        return "إدراك"
    if root in ["ابو", "ام", "اخ", "قوم"]:
        return "علاقة"
    if root in ["رزق", "مال", "ملك", "برك"]:
        return "رزق"
    return "—"

# -----------------------------
# 10) البحث داخل القرآن
# -----------------------------
def find_in_quran(root, quran):
    matches = []
    for ayah in quran:
        text_norm = normalize_arabic(ayah["text"])
        if root in text_norm:
            matches.append(ayah)
    return matches

# -----------------------------
# 11) السكربت الرئيسي + تقرير متقدّم
# -----------------------------
def map_roots():
    print("🚀 بدأ التشغيل…")
    print("📂 قراءة الملفات…")

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    with open(QURAN_FILE, "r", encoding="utf-8") as f:
        quran = json.load(f)

    print(f"✅ عدد عناصر ملف الجذور الخام: {len(data)}")
    print(f"✅ عدد آيات القرآن: {len(quran)}")
    print("🔎 بدء معالجة الجذور العربية (LEM فقط)…")

    final = []
    roots_counter = Counter()
    domain_counter = Counter()
    weight_counter = Counter()
    surah_counter = Counter()

    processed = 0
    skipped = 0

    for entry in data:
        raw = entry.get("root", "")
        freq = entry.get("frequency", 0)
        hint = entry.get("orbit_hint", None)

        root = extract_raw_root(raw)
        if not root:
            skipped += 1
            continue

        triliteral = extract_triliteral(root)

        matches = find_in_quran(triliteral, quran)
        derivatives = extract_derivatives(triliteral, quran)

        if matches:
            first = matches[0]
            surah = first["surah_name"]
            verse = first["text"]
            surah_counter[surah] += 1
        else:
            surah = None
            verse = None

        if derivatives:
            sample = derivatives[0]
            pattern = detect_pattern(sample, triliteral)
            verb_type = detect_verb_type(sample)
            bab = detect_verb_bab(sample)
        else:
            pattern = "—"
            verb_type = "—"
            bab = "—"

        semantic_weight = get_semantic_weight(triliteral)
        semantic_domain = get_semantic_domain(triliteral)

        roots_counter[triliteral] += 1
        if semantic_domain != "—":
            domain_counter[semantic_domain] += 1
        if semantic_weight != "—":
            weight_counter[semantic_weight] += 1

        final.append({
            "root": triliteral,
            "raw_root": root,
            "derivatives": derivatives,
            "occurrences": len(matches),
            "pattern": pattern,
            "verb_type": verb_type,
            "verb_bab": bab,
            "semantic_weight": semantic_weight,
            "semantic_domain": semantic_domain,
            "surah": surah,
            "verse": verse,
            "frequency": freq,
            "orbit_hint": hint
        })

        processed += 1

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(final, f, ensure_ascii=False, indent=4)

    print("\n✅ تم إنشاء الملف:", OUTPUT_FILE)
    print(f"📌 عدد الجذور المعالجة فعليًا: {processed}")
    print(f"📌 عدد العناصر المتجاوزة (غير عربية / بدون LEM): {skipped}")
    print(f"📌 عدد الجذور في الملف الناتج: {len(final)}")

    # -------------------------
    # تقرير تحليلي سريع
    # -------------------------
    print("\n📊 إحصائيات سريعة:")

    if roots_counter:
        print("\n🔹 أكثر 10 جذور تكرارًا في ملف الجذور الخام (بعد LEM):")
        for r, c in roots_counter.most_common(10):
            print(f"  - {r}: {c} مرة في ملف الجذور")

    if domain_counter:
        print("\n🔹 توزيع المجالات الدلالية:")
        for d, c in domain_counter.most_common():
            print(f"  - {d}: {c} جذر")

    if weight_counter:
        print("\n🔹 توزيع الأوزان الدلالية:")
        for w, c in weight_counter.most_common():
            print(f"  - {w}: {c} جذر")

    if surah_counter:
        print("\n🔹 أكثر السور التي ظهرت فيها الجذور (أول ظهور):")
        for s, c in surah_counter.most_common(10):
            print(f"  - {s}: {c} جذر")

    # -------------------------
    # عينات للمعاينة
    # -------------------------
    print("\n👁‍🗨 عينة من 5 جذور من الملف الناتج:")
    for item in final[:5]:
        print("\n-----------------------------")
        print(f"🔤 الجذر الثلاثي: {item['root']}")
        print(f"📎 الجذر الخام: {item['raw_root']}")
        print(f"📖 أول سورة: {item['surah']}")
        print(f"🧩 أول آية: {item['verse']}")
        print(f"🧬 عدد المشتقات: {len(item['derivatives'])}")
        print(f"🎯 الوزن الصرفي: {item['pattern']}")
        print(f"⚙ نوع الفعل: {item['verb_type']}")
        print(f"🌌 الوزن الدلالي: {item['semantic_weight']}")
        print(f"🗺 المجال الدلالي: {item['semantic_domain']}")
        print(f"🛰 orbit_hint: {item['orbit_hint']}")
        print(f"📊 frequency: {item['frequency']}")

    print("\n✅ انتهى التنفيذ بنجاح.\n")

if __name__ == "__main__":
    map_roots()