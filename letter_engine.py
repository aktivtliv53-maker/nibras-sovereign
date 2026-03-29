# =========================================================
# letter_engine.py — v20.3 Structural Letter Dynamics
# =========================================================

# ---------------------------------------------------------
# 1) القاموس الهندسي الكامل للحروف (28 حرفًا)
# ---------------------------------------------------------
LETTER_MAP = {
    "ا": {"symbol": "استقامة", "vector": "صعود", "motion": "خط مستقيم", "field": "اتصال", "polarity": "موجب", "intensity": 3, "weight": 1.0},
    "ب": {"symbol": "سطح", "vector": "تجسد", "motion": "هبوط", "field": "مادة", "polarity": "محايد", "intensity": 2, "weight": 0.8},
    "ت": {"symbol": "نقطة مزدوجة", "vector": "تعدد", "motion": "تكرار", "field": "تنويع", "polarity": "موجب", "intensity": 3, "weight": 0.9},
    "ث": {"symbol": "نقاط ثلاث", "vector": "توسع", "motion": "انتشار", "field": "تفرع", "polarity": "موجب", "intensity": 4, "weight": 1.1},
    "ج": {"symbol": "قوس سفلي", "vector": "احتواء", "motion": "التفاف", "field": "عمق", "polarity": "محايد", "intensity": 3, "weight": 1.0},
    "ح": {"symbol": "بوابة", "vector": "انفتاح", "motion": "فتح", "field": "تحرر", "polarity": "موجب", "intensity": 4, "weight": 1.2},
    "خ": {"symbol": "بوابة علوية", "vector": "ارتفاع", "motion": "صعود", "field": "تحول", "polarity": "موجب", "intensity": 4, "weight": 1.3},
    "د": {"symbol": "زاوية", "vector": "قطع", "motion": "حسم", "field": "حد", "polarity": "سالب", "intensity": 3, "weight": 1.0},
    "ذ": {"symbol": "زاوية مضيئة", "vector": "إشارة", "motion": "وميض", "field": "تنبيه", "polarity": "موجب", "intensity": 3, "weight": 1.1},
    "ر": {"symbol": "قمة", "vector": "ارتفاع", "motion": "صعود", "field": "قوة", "polarity": "موجب", "intensity": 4, "weight": 1.2},
    "ز": {"symbol": "قمة مشرقة", "vector": "وميض", "motion": "اهتزاز", "field": "نور", "polarity": "موجب", "intensity": 4, "weight": 1.3},
    "س": {"symbol": "مسار", "vector": "انسياب", "motion": "جريان", "field": "حركة", "polarity": "محايد", "intensity": 3, "weight": 1.0},
    "ش": {"symbol": "مسار متشعب", "vector": "تفرع", "motion": "تشتت", "field": "تنويع", "polarity": "محايد", "intensity": 4, "weight": 1.1},
    "ص": {"symbol": "ضغط", "vector": "تكثيف", "motion": "انضغاط", "field": "قوة", "polarity": "سالب", "intensity": 5, "weight": 1.4},
    "ض": {"symbol": "ضغط مظلم", "vector": "تكثيف", "motion": "انضغاط", "field": "ظل", "polarity": "سالب", "intensity": 5, "weight": 1.5},
    "ط": {"symbol": "قوة", "vector": "اندفاع", "motion": "دفع", "field": "قوة", "polarity": "موجب", "intensity": 5, "weight": 1.6},
    "ظ": {"symbol": "قوة مظلمة", "vector": "اندفاع", "motion": "دفع", "field": "ظل", "polarity": "سالب", "intensity": 5, "weight": 1.7},
    "ع": {"symbol": "عمق", "vector": "غور", "motion": "نزول", "field": "باطن", "polarity": "محايد", "intensity": 4, "weight": 1.3},
    "غ": {"symbol": "عمق مضيء", "vector": "غور", "motion": "نزول", "field": "نور", "polarity": "موجب", "intensity": 4, "weight": 1.4},
    "ف": {"symbol": "انفراج", "vector": "انتشار", "motion": "فتح", "field": "تحرر", "polarity": "موجب", "intensity": 3, "weight": 1.1},
    "ق": {"symbol": "قيد", "vector": "انضباط", "motion": "تقييد", "field": "حد", "polarity": "سالب", "intensity": 4, "weight": 1.3},
    "ك": {"symbol": "زاوية", "vector": "قطع", "motion": "حسم", "field": "حد", "polarity": "سالب", "intensity": 3, "weight": 1.0},
    "ل": {"symbol": "قوس", "vector": "اتصال", "motion": "ربط", "field": "وصل", "polarity": "موجب", "intensity": 3, "weight": 1.0},
    "م": {"symbol": "موج", "vector": "تدفق", "motion": "جريان", "field": "حركة", "polarity": "محايد", "intensity": 4, "weight": 1.2},
    "ن": {"symbol": "نقطة", "vector": "احتواء", "motion": "ثبات", "field": "مركز", "polarity": "محايد", "intensity": 3, "weight": 1.0},
    "ه": {"symbol": "تنفس", "vector": "تحرر", "motion": "زفير", "field": "هواء", "polarity": "موجب", "intensity": 2, "weight": 0.9},
    "و": {"symbol": "حلقة", "vector": "دوران", "motion": "التفاف", "field": "دورة", "polarity": "محايد", "intensity": 3, "weight": 1.0},
    "ي": {"symbol": "امتداد", "vector": "نزول", "motion": "سحب", "field": "امتداد", "polarity": "محايد", "intensity": 3, "weight": 1.0}
}

# ---------------------------------------------------------
# 2) تحليل الحرف داخل الكلمة
# ---------------------------------------------------------
def analyze_word_letters(word: str):
    letters = [ch for ch in word if ch in LETTER_MAP]
    if not letters:
        return None
    
    details = [LETTER_MAP[l] for l in letters]
    vectors = [d["vector"] for d in details]
    motions = [d["motion"] for d in details]
    fields = [d["field"] for d in details]

    return {
        "letters": letters,
        "dominant_vector": max(set(vectors), key=vectors.count),
        "dominant_motion": max(set(motions), key=motions.count),
        "dominant_field": max(set(fields), key=fields.count),
        "details": details
    }

# ---------------------------------------------------------
# 3) حساب طاقة الحرف داخل الكلمة
# ---------------------------------------------------------
def compute_letter_energy(word: str):
    letters = [ch for ch in word if ch in LETTER_MAP]
    if not letters:
        return 0.0
    return sum(
        LETTER_MAP[ch]["weight"] * LETTER_MAP[ch]["intensity"]
        for ch in letters
    )
