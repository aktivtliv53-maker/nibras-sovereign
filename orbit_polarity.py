# orbit_polarity.py — v20.3
ORBIT_POLARITY_MAP = {
    "التمكين": "الابتلاء",
    "الإيمان": "الضلال",
    "النور": "الظلام",
    "الرحمة": "العقاب",
    "العدل": "الظلم",
    "بناء": "هدم",
    "الإصلاح": "الفساد"
}

def get_orbit_meta(orbit: str):
    opposite = ORBIT_POLARITY_MAP.get(orbit)
    relation = "تقابل" if opposite else "توازن"
    return {
        "main": orbit,
        "opposite": opposite if opposite else "توازن وجودي",
        "relation": relation
    }
