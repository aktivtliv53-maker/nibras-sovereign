# orbit_polarity.py
ORBIT_POLARITY_MAP = {
    "التمكين": "الابتلاء", "الإيمان": "الضلال", "النور": "الظلام",
    "الرحمة": "العقاب", "العدل": "الظلم", "بناء": "هدم", "الإصلاح": "الفساد"
}
def get_orbit_meta(orbit: str):
    return {"main": orbit, "opposite": ORBIT_POLARITY_MAP.get(orbit, "توازن وجودي")}
