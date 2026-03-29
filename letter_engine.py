# =========================================================
# letter_engine.py — v20.5
# هندسة الحرف + وعي النقطة + المصفوفة الجينية + كيمياء الحروف
# =========================================================

from collections import Counter
from itertools import pairwise

# =========================================================
# 1) المصفوفة الجينية الموحدة (أزواج الأنعام) - v20.4
# =========================================================
GENETIC_MATRIX = {
    'الإبل (A)': {
        'letters': ['ا', 'أ', 'إ', 'آ', 'ه', 'و', 'ي', 'ر', 'ل'],
        'energy': 'حركة/انتقال/صعود خفيف',
        'function': 'دفع/انطلاق/سفر داخلي',
        'base_gene': 'A'
    },
    'البقر (G)': {
        'letters': ['ق', 'ط', 'ض', 'ص', 'ظ', 'خ'],
        'energy': 'بناء/ثقل/إنتاج',
        'function': 'بناء/كشف/تحمل',
        'base_gene': 'G'
    },
    'الضأن (T)': {
        'letters': ['ن', 'م', 'ب', 'ف', 'ت', 'س'],
        'energy': 'سكون/لين/قرب',
        'function': 'نعومة/استقرار/ألفة',
        'base_gene': 'T'
    },
    'المعز (C)': {
        'letters': ['ك', 'ج', 'د', 'ذ', 'ز', 'ش'],
        'energy': 'صعود/تحدي/ثبات',
        'function': 'قوة/صلابة/مواجهة',
        'base_gene': 'C'
    }
}

# =========================================================
# 2) خريطة وعي النقطة (Point Consciousness Map)
# =========================================================
POINT_MAP = {
    "ب": {"position": "down", "vector": -1},
    "ي": {"position": "down", "vector": -1},
    "ج": {"position": "down-inner", "vector": -0.5},
    "ت": {"position": "up", "vector": +1},
    "ث": {"position": "up", "vector": +1},
    "ن": {"position": "up", "vector": +1},
    "ق": {"position": "inner", "vector": 0},
    "ف": {"position": "inner", "vector": 0},
    "خ": {"position": "inner", "vector": 0},
    "ش": {"position": "crown", "vector": +2},
    "ز": {"position": "mid", "vector": 0.5},
}

# =========================================================
# 3) الحقول والمجالات الوجودية + طاقة الحرف
# =========================================================
LETTER_FIELD = {
    "ا": "fire", "ب": "earth", "ت": "air", "ث": "air", "ج": "water", "ح": "water",
    "خ": "water", "ر": "fire", "د": "fire", "س": "air", "ش": "air", "ص": "earth",
    "ض": "earth", "ط": "fire", "ظ": "fire", "ع": "water", "غ": "water", "ف": "air",
    "ق": "fire", "ك": "earth", "ل": "air", "م": "water", "ن": "air", "ه": "ether",
    "و": "water", "ي": "air"
}

BASE_LETTER_ENERGY = {
    "ا": 10, "ب": 8, "ت": 7, "ث": 7, "ج": 6, "ح": 9, "خ": 9, "د": 6, "ذ": 6,
    "ر": 7, "ز": 7, "س": 5, "ش": 8, "ص": 9, "ض": 10, "ط": 9, "ظ": 10,
    "ع": 9, "غ": 9, "ف": 6, "ق": 8, "ك": 7, "ل": 6, "م": 8, "ن": 7,
    "ه": 5, "و": 7, "ي": 7,
}

# =========================================================
# 4) محركات الأساس: الجين + النقطة
# =========================================================

def get_genetic_data(letter: str):
    """تحديد الانتماء الجيني للحرف بناءً على أزواج الأنعام"""
    for group, data in GENETIC_MATRIX.items():
        if letter in data['letters']:
            return {
                "group": group,
                "gene": data['base_gene'],
                "energy_desc": data['energy'],
                "function": data['function'],
            }
    return {"group": "بناء", "gene": "N", "energy_desc": "neutral", "function": "neutral"}

def get_point_consciousness(letter: str):
    """إرجاع وعي النقطة (الموضع + المتجه)"""
    meta = POINT_MAP.get(letter)
    if not meta:
        return {"position": "none", "vector": 0}
    return meta

# =========================================================
# 5) تحليل الحروف داخل الكلمة
# =========================================================

def analyze_word_letters(word: str):
    """
    تحليل الحرف بدمج:
    - المجال
    - الجين
    - وعي النقطة
    """
    letters = list(word)
    analysis = []
    for letter in letters:
        gen_data = get_genetic_data(letter)
        point_meta = get_point_consciousness(letter)
        field = LETTER_FIELD.get(letter, "neutral")

        analysis.append({
            "letter": letter,
            "field": field,
            "genetic_group": gen_data["group"],
            "gene": gen_data["gene"],
            "point_position": point_meta["position"],
            "point_vector": point_meta["vector"],
        })
    return analysis

# =========================================================
# 6) كيمياء الحروف (Inter-Letter Alchemy) - v20.5
# =========================================================

# خريطة تفاعل الجينات (مبسطة مبدئيًا)
GENE_INTERACTION_MAP = {
    ("A", "G"): {"type": "تثبيت", "factor": 1.1},
    ("G", "A"): {"type": "تثبيت", "factor": 1.1},

    ("A", "C"): {"type": "اندفاع", "factor": 1.2},
    ("C", "A"): {"type": "اندفاع", "factor": 1.2},

    ("G", "T"): {"type": "استقرار", "factor": 1.15},
    ("T", "G"): {"type": "استقرار", "factor": 1.15},

    ("C", "T"): {"type": "توتر", "factor": 1.05},
    ("T", "C"): {"type": "توتر", "factor": 1.05},
}

def get_gene_interaction(g1: str, g2: str):
    """إرجاع نوع التفاعل الجيني بين حرفين"""
    if g1 is None or g2 is None:
        return {"type": "محايد", "factor": 1.0}
    key = (g1, g2)
    return GENE_INTERACTION_MAP.get(key, {"type": "محايد", "factor": 1.0})

def compute_inter_letter_alchemy(word: str):
    """
    يحسب:
    - قائمة التفاعلات بين كل زوج متجاور من الحروف
    - معامل التفاعل الكلي للكلمة
    """
    letters = analyze_word_letters(word)
    if len(letters) < 2:
        return {"interactions": [], "global_factor": 1.0}

    interactions = []
    total_factor = 1.0
    count = 0

    # pairwise متاحة من itertools في بايثون 3.10+
    for a, b in pairwise(letters):
        g1 = a["gene"]
        g2 = b["gene"]
        inter = get_gene_interaction(g1, g2)
        interactions.append({
            "pair": f"{a['letter']}{b['letter']}",
            "genes": f"{g1}-{g2}",
            "type": inter["type"],
            "factor": inter["factor"],
        })
        total_factor *= inter["factor"]
        count += 1

    global_factor = total_factor if count > 0 else 1.0
    return {"interactions": interactions, "global_factor": round(global_factor, 3)}

# =========================================================
# 7) طاقة الحرف/الكلمة (مع كيمياء الحروف)
# =========================================================

def compute_letter_energy(word: str) -> float:
    """
    طاقة الكلمة = مجموع طاقات الحروف
    × معامل وعي النقطة
    × معامل كيمياء الحروف (التفاعل الجيني)
    """
    letters = list(word)
    if not letters:
        return 0.0

    total = 0
    for letter in letters:
        base = BASE_LETTER_ENERGY.get(letter, 5)
        point_meta = get_point_consciousness(letter)
        point_factor = 1 + (point_meta["vector"] * 0.15)
        total += base * point_factor

    # معامل كيمياء الحروف
    inter = compute_inter_letter_alchemy(word)
    total *= inter["global_factor"]

    return round(total, 3)

# =========================================================
# 8) البصمة الجينية–الحرفية للكلمة
# =========================================================

def summarize_word_signature(word: str):
    """
    يعطي:
    - الجين الغالب
    - متوسط متجه النقطة
    - معامل التفاعل الجيني
    - عدد الحروف
    """
    letters = analyze_word_letters(word)
    if not letters:
        return {
            "dominant_gene": "N",
            "avg_point_vector": 0,
            "inter_factor": 1.0,
            "letter_count": 0,
        }

    genes = [l["gene"] for l in letters if l["gene"] != "N"]
    dom_gene = Counter(genes).most_common(1)[0][0] if genes else "N"
    avg_vec = round(sum(l["point_vector"] for l in letters) / len(letters), 3)

    inter = compute_inter_letter_alchemy(word)

    return {
        "dominant_gene": dom_gene,
        "avg_point_vector": avg_vec,
        "inter_factor": inter["global_factor"],
        "letter_count": len(letters),
        "interactions": inter["interactions"],
    }
