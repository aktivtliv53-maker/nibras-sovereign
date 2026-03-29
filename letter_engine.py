# letter_engine.py
LETTER_MAP = {
    "ا": {"symbol": "استقامة", "vector": "صعود", "note": "أمر / توجيه علوي"},
    "ن": {"symbol": "نقطة الوعي", "vector": "احتواء", "note": "وعاء باطني / لبث"},
    "ب": {"symbol": "سطح المادة", "vector": "تجسد", "note": "ظهور أرضي / مكث"},
    "ت": {"symbol": "مسار مغلق", "vector": "ثبات", "note": "اكتداس طاقي"},
    "ج": {"symbol": "مركز الجاذبية", "vector": "تجمع", "note": "حركة لولبية للداخل"},
    "ح": {"symbol": "حيز حيوي", "vector": "إحاطة", "note": "طاقة حياة محصورة"},
    "خ": {"symbol": "اختراق", "vector": "خروج", "note": "تجاوز الحدود"},
    "د": {"symbol": "زاوية الدفع", "vector": "استناد", "note": "تأسيس حركي"},
    "ر": {"symbol": "تكرار ترددي", "vector": "ارتقاء", "note": "اهتزاز مستمر"},
    "س": {"symbol": "تدفق سيال", "vector": "انتشار", "note": "سريان في المدار"},
    "ص": {"symbol": "صلابة الصد", "vector": "تركيز", "note": "مقاومة واحتفاظ"},
    "ع": {"symbol": "منبع العين", "vector": "انبثاق", "note": "رؤية من الداخل"},
    "ق": {"symbol": "قوة القطع", "vector": "استعلاء", "note": "تحكم مركزي"},
    "ل": {"symbol": "وصل طولي", "vector": "ارتباط", "note": "توصيل بين الأقطار"},
    "م": {"symbol": "دائرة التمام", "vector": "إغلاق", "note": "تجميع نهائي"},
    "و": {"symbol": "ربط كوني", "vector": "انسياب", "note": "صلة بين الوجودين"},
    "ي": {"symbol": "امتداد ذاتي", "vector": "تحول", "note": "مرونة التمكين"},
}

def analyze_word_letters(word: str):
    letters = [ch for ch in word if ch in LETTER_MAP]
    if not letters: return None
    details = [LETTER_MAP[l] for l in letters]
    vectors = [d["vector"] for d in details]
    return {
        "dominant_vector": max(set(vectors), key=vectors.count) if vectors else "محايد",
        "details": details
    }
