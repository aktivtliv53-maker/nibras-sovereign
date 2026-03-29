# =========================================================
# orbit_letter_engine.py — v20.3.2 Sovereign Fusion Layer
# =========================================================

from letter_engine import analyze_word_letters, compute_letter_energy
from orbit_polarity import get_orbit_meta

# ---------------------------------------------------------
# 1) بصمة الحرف + المدار (Signature Engine)
# ---------------------------------------------------------
def compute_orbit_letter_signature(word: str, orbit: str):
    """
    يدمج:
    - طاقة الحرف
    - اتجاه الحرف
    - حركة الحرف
    - مجال الحرف
    - قطبية المدار
    - المدار المقابل
    """
    letter_meta = analyze_word_letters(word)
    if not letter_meta:
        return None

    orbit_meta = get_orbit_meta(orbit)
    letter_energy = compute_letter_energy(word)

    return {
        "word": word,
        "orbit": orbit,
        "orbit_opposite": orbit_meta["opposite"],
        "orbit_relation": orbit_meta["relation"],
        "letter_energy": letter_energy,
        "dominant_vector": letter_meta["dominant_vector"],
        "dominant_motion": letter_meta["dominant_motion"],
        "dominant_field": letter_meta["dominant_field"],
        "signature_strength": round(letter_energy * 0.35, 3)
    }

# ---------------------------------------------------------
# 2) دمج الطاقة (Root + Letter + Orbit)
# ---------------------------------------------------------
def fuse_orbit_letter_energy(root_energy: float, word: str, orbit: str):
    """
    الجذر = الأساس
    الحرف = تعديل دقيق
    المدار = انحراف أو تعزيز
    """
    letter_e = compute_letter_energy(word)
    orbit_meta = get_orbit_meta(orbit)

    # المدار ذو علاقة "تقابل" يزيد التأثير
    orbit_factor = 1.15 if orbit_meta["relation"] == "تقابل" else 1.0

    total = root_energy + (letter_e * 0.25 * orbit_factor)
    return round(total, 4)

# ---------------------------------------------------------
# 3) بناء بصمة المسار الكاملة
# ---------------------------------------------------------
def build_path_orbit_letter_profile(words, orbits, root_energies):
    """
    يعطي:
    - طاقة كل كلمة بعد الدمج
    - البصمة الحرفية–المدارية
    - متوسط الطاقة
    """
    profile = []
    total_energy = 0

    for w, o, r_e in zip(words, orbits, root_energies):
        fused = fuse_orbit_letter_energy(r_e, w, o)
        sig = compute_orbit_letter_signature(w, o)

        profile.append({
            "word": w,
            "orbit": o,
            "root_energy": r_e,
            "letter_energy": sig["letter_energy"] if sig else 0,
            "fused_energy": fused,
            "signature": sig
        })

        total_energy += fused

    avg_energy = round(total_energy / len(words), 4) if words else 0

    return {
        "profile": profile,
        "total_energy": round(total_energy, 4),
        "avg_energy": avg_energy
    }
