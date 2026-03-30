# -*- coding: utf-8 -*-
# =========================================================
# NIBRAS SOVEREIGN v30.0 — COMPLETE MONOLITH
# =========================================================
# نظام سيادي متكامل لتحليل الجذور القرآنية والرنين السياقي
# يعمل على Streamlit Cloud مع دعم كامل للملفات الخارجية
# =========================================================

import streamlit as st
import json
import re
import math
import os
from pathlib import Path
from datetime import datetime
from collections import Counter, defaultdict
from typing import Dict, List, Any, Tuple, Optional, Set

# =========================================================
# ===================== 1) IMPORTS & CONFIG =====================
# =========================================================

# PAGE CONFIG
st.set_page_config(
    page_title="NIBRAS SOVEREIGN v30.0",
    page_icon="🜂",
    layout="wide",
)

APP_VERSION = "NIBRAS SOVEREIGN v30.0 COMPLETE"

# =========================================================
# ===================== 2) CONSTANTS =====================
# =========================================================

# STRICT orbit whitelist
KNOWN_ORBITS: Set[str] = {
    "وعي", "نور", "رحمة", "حق", "ميزان", "صبر", "هداية", "قوة", "بصيرة", "توحيد"
}
DEFAULT_ORBIT = "وعي"

# Paths for data files
DATA_DIR = Path("data")
QROOT_DIR = Path("qroot")
DEFAULT_ROOTS_PATH = DATA_DIR / "quranic_roots_1800.json"
DEFAULT_LETTERS_PATH = DATA_DIR / "letters_28_compact.json"
DEFAULT_MATRIX_PATH = DATA_DIR / "matrix_resonance.json"

# Conservative affixes (heuristic only)
PREFIXES = [
    "وال", "بال", "كال", "فال", "لل",
    "ال",
    "و", "ف", "ب", "ك", "ل", "س",
    "ي", "ت", "ن", "ا",
    "است", "مست", "ان", "مت",
]

SUFFIXES = [
    "يات", "ات", "ون", "ين", "ان",
    "هما", "كما", "كم", "كن", "هم", "هن", "ها", "نا",
    "ية", "ه", "ة", "ي", "ك", "ت", "ا", "و", "ن", "م",
]

# Weights for candidate sources
SOURCE_BONUS = {
    "normalized": 0.22,
    "teh_marbuta_variant": 0.16,
    "prefix_strip": 0.18,
    "suffix_strip": 0.18,
    "prefix_suffix_strip": 0.20,
    "double_reduce": 0.08,
    "sliding_triple": 0.52,
    "pattern_extract": 0.30,
}

# Simple morphological patterns
PATTERN_RULES = [
    ("است", 3),
    ("م", 3),
    ("ت", 3),
    ("ان", 3),
    ("ا", 3),
]

# Arabic regex patterns
ARABIC_DIACRITICS_RE = re.compile(r"[\u0617-\u061A\u064B-\u0652\u0670\u0640]")
NON_ARABIC_KEEP_SPACE_RE = re.compile(r"[^\u0621-\u063A\u0641-\u064A\s]")
MULTISPACE_RE = re.compile(r"\s+")
ARABIC_ONLY_RE = re.compile(r"^[\u0621-\u063A\u0641-\u064A]+$")

# Normalization policy
NORMALIZATION_POLICY = {
    "strip_diacritics": True,
    "normalize_hamza": True,
    "convert_alef_maqsura": True,
    "convert_ta_marbuta": True
}

# =========================================================
# ===================== 3) UTILITIES =====================
# =========================================================

def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))

def now_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

def analysis_id() -> str:
    return "analysis_" + datetime.utcnow().strftime("%Y%m%d_%H%M%S")

def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default

def is_arabic_word(text: str) -> bool:
    return bool(text) and bool(ARABIC_ONLY_RE.fullmatch(text))

def dedupe_keep_order(items: List[str]) -> List[str]:
    seen = set()
    out = []
    for x in items:
        if x and x not in seen:
            seen.add(x)
            out.append(x)
    return out

def get_file_info(path: str) -> Tuple[float, int]:
    """إرجاع حجم الملف (MB) وعدد الأسطر"""
    try:
        if path and os.path.exists(path):
            size_mb = round(os.path.getsize(path) / (1024 * 1024), 2)
            with open(path, "r", encoding="utf-8") as f:
                lines = sum(1 for _ in f)
            return size_mb, lines
    except Exception:
        pass
    return 0, 0

def safe_read_json(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(f"Missing JSON file: {path}")
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def search_file_path(filename: str) -> Optional[Path]:
    """البحث عن ملف في المسارات المتعددة"""
    search_paths = [Path("."), DATA_DIR, QROOT_DIR]
    for folder in search_paths:
        file_path = folder / filename
        if file_path.exists():
            return file_path
    return None

# =========================================================
# ===================== 4) NORMALIZATION =====================
# =========================================================

def normalize_arabic(text: str, force_teh_marbuta_to_ha: bool = False) -> str:
    """
    Conservative normalization:
    - Remove diacritics
    - Normalize hamzas/alef variants
    - Normalize yaa maqsura
    - Keep spaces
    - Optionally convert ة -> ه
    """
    if not isinstance(text, str):
        text = str(text)

    t = text.strip()
    t = ARABIC_DIACRITICS_RE.sub("", t)

    # Normalize hamza/alef variants
    t = (
        t.replace("أ", "ا")
         .replace("إ", "ا")
         .replace("آ", "ا")
         .replace("ٱ", "ا")
         .replace("ؤ", "و")
         .replace("ئ", "ي")
         .replace("ى", "ي")
    )

    if force_teh_marbuta_to_ha:
        t = t.replace("ة", "ه")

    t = NON_ARABIC_KEEP_SPACE_RE.sub(" ", t)
    t = MULTISPACE_RE.sub(" ", t).strip()
    return t

def teh_marbuta_variant(word: str) -> Optional[str]:
    if "ة" in word:
        return word.replace("ة", "ه")
    return None

def tokenize_arabic(text: str) -> List[str]:
    """استخراج الكلمات العربية من نص"""
    t = normalize_arabic(text, force_teh_marbuta_to_ha=False)
    if not t:
        return []
    return [w for w in t.split() if len(w) >= 2]

def arabic_word_tokenize(text: str) -> List[str]:
    """Alias for tokenize_arabic"""
    return tokenize_arabic(text)

# =========================================================
# ===================== 5) WORD SHAPING =====================
# =========================================================

def reduce_doubles(word: str) -> str:
    """Conservative duplicate reduction"""
    if len(word) <= 3:
        return word
    out = []
    prev = None
    repeat_count = 0
    for ch in word:
        if ch == prev:
            repeat_count += 1
            if repeat_count >= 2:
                continue
        else:
            repeat_count = 0
        out.append(ch)
        prev = ch
    return "".join(out)

def strip_prefixes(word: str) -> List[str]:
    results = []
    for p in sorted(PREFIXES, key=len, reverse=True):
        if word.startswith(p) and len(word) - len(p) >= 3:
            results.append(word[len(p):])
    return dedupe_keep_order(results)

def strip_suffixes(word: str) -> List[str]:
    results = []
    for s in sorted(SUFFIXES, key=len, reverse=True):
        if word.endswith(s) and len(word) - len(s) >= 3:
            results.append(word[:-len(s)])
    return dedupe_keep_order(results)

def strip_prefix_suffix(word: str) -> List[str]:
    results = []
    for p in sorted(PREFIXES, key=len, reverse=True):
        if word.startswith(p) and len(word) - len(p) >= 3:
            base = word[len(p):]
            for s in sorted(SUFFIXES, key=len, reverse=True):
                if base.endswith(s) and len(base) - len(s) >= 3:
                    results.append(base[:-len(s)])
    return dedupe_keep_order(results)

def sliding_triples(word: str) -> List[str]:
    if len(word) < 3:
        return []
    triples = []
    for i in range(len(word) - 2):
        tri = word[i:i+3]
        if len(tri) == 3 and is_arabic_word(tri):
            triples.append(tri)
    return dedupe_keep_order(triples)

def pattern_extract_roots(word: str) -> List[str]:
    """Very conservative heuristic pattern extraction"""
    out = []

    if len(word) == 3 and is_arabic_word(word):
        out.append(word)

    if len(word) == 4:
        out.extend([word[:3], word[1:4]])

    for pref, _ in PATTERN_RULES:
        if word.startswith(pref) and len(word) - len(pref) >= 3:
            core = word[len(pref):]
            out.append(core[:3])
            if len(core) >= 4:
                out.append(core[0] + core[1] + core[-1])

    if word.startswith("م") and len(word) >= 5:
        core = word[1:]
        out.append(core[0] + core[1] + core[-1])

    if word.startswith("ت") and len(word) >= 4:
        core = word[1:]
        out.append(core[:3])

    cleaned = []
    for c in out:
        c = c.strip()
        if len(c) == 3 and is_arabic_word(c):
            cleaned.append(c)

    return dedupe_keep_order(cleaned)

def generate_root_candidates(word: str) -> List[Dict[str, Any]]:
    """Generate candidate root-like forms with source labels and weights"""
    base = normalize_arabic(word, force_teh_marbuta_to_ha=False).replace(" ", "")
    if not base or len(base) < 2:
        return []

    out: List[Dict[str, Any]] = []

    def add(form: str, source: str, weight: float):
        form = normalize_arabic(form, force_teh_marbuta_to_ha=False).replace(" ", "")
        if not form or len(form) < 2 or not is_arabic_word(form):
            return
        out.append({
            "form": form,
            "source": source,
            "weight": weight,
        })

    add(base, "normalized", 1.00)

    tmv = teh_marbuta_variant(base)
    if tmv and tmv != base:
        add(tmv, "teh_marbuta_variant", 0.92)

    for w in strip_prefixes(base):
        add(w, "prefix_strip", 0.88)

    for w in strip_suffixes(base):
        add(w, "suffix_strip", 0.88)

    for w in strip_prefix_suffix(base):
        add(w, "prefix_suffix_strip", 0.93)

    reduced = reduce_doubles(base)
    if reduced != base:
        add(reduced, "double_reduce", 0.74)

    for p in pattern_extract_roots(base):
        add(p, "pattern_extract", 0.86)

    for tri in sliding_triples(base):
        add(tri, "sliding_triple", 0.58)

    best = {}
    for item in out:
        key = (item["form"], item["source"])
        if key not in best or item["weight"] > best[key]["weight"]:
            best[key] = item

    return list(best.values())

def calculate_normalized_total(mass: float, speed: float, energy: float) -> float:
    """Internal sovereign index"""
    nm = math.log1p(max(0.0, mass))
    ns = math.log1p(max(0.0, speed))
    ne = math.log1p(max(0.0, energy))
    total = (nm * 0.33) + (ns * 0.27) + (ne * 0.40)
    return round(total * 10.0, 4)

def estimate_word_mass_speed(word: str, letters_index: Dict[str, Dict[str, float]]) -> Tuple[float, float]:
    mass = 0.0
    speed = 0.0
    for ch in word:
        entry = letters_index.get(ch)
        if entry:
            mass += safe_float(entry.get("mass", 1.0), 1.0)
            speed += safe_float(entry.get("speed", 1.0), 1.0)
        else:
            mass += 1.0
            speed += 1.0
    return round(mass, 4), round(speed, 4)

# =========================================================
# ===================== 6) DATA LOADING =====================
# =========================================================

def normalize_orbit(orbit_value: Any) -> str:
    orbit = str(orbit_value).strip() if orbit_value is not None else ""
    if orbit in KNOWN_ORBITS:
        return orbit
    return DEFAULT_ORBIT

def validate_and_load_roots(roots_path: Path = DEFAULT_ROOTS_PATH) -> Dict[str, Any]:
    """Loads the 1800+ root lexicon with strict diagnostics"""
    raw = safe_read_json(roots_path)

    if not isinstance(raw, list):
        raise ValueError("quranic_roots_1800.json must be a JSON array (list).")

    index: Dict[str, Dict[str, Any]] = {}
    diagnostics = {
        "path": str(roots_path),
        "entries_total": len(raw),
        "entries_valid": 0,
        "entries_invalid": 0,
        "duplicate_roots": 0,
        "missing_root": 0,
        "non_arabic_roots": 0,
        "unknown_orbit_count": 0,
        "unknown_orbits_seen": Counter(),
        "roots_final": 0,
    }

    for item in raw:
        if not isinstance(item, dict):
            diagnostics["entries_invalid"] += 1
            continue

        root_raw = item.get("root", "")
        root = normalize_arabic(str(root_raw), force_teh_marbuta_to_ha=False).replace(" ", "")

        if not root:
            diagnostics["entries_invalid"] += 1
            diagnostics["missing_root"] += 1
            continue

        if len(root) < 3 or not is_arabic_word(root):
            diagnostics["entries_invalid"] += 1
            diagnostics["non_arabic_roots"] += 1
            continue

        orbit_original = str(item.get("orbit", "")).strip()
        orbit = normalize_orbit(orbit_original)
        if orbit_original and orbit_original not in KNOWN_ORBITS:
            diagnostics["unknown_orbit_count"] += 1
            diagnostics["unknown_orbits_seen"][orbit_original] += 1

        energy = safe_float(item.get("energy", item.get("weight", 1.0)), 1.0)
        mass = safe_float(item.get("mass", 1.0), 1.0)
        speed = safe_float(item.get("speed", 1.0), 1.0)

        forms = item.get("forms", [])
        if isinstance(forms, str):
            forms = [forms]
        if not isinstance(forms, list):
            forms = []

        norm_forms = []
        for f in forms:
            nf = normalize_arabic(str(f), force_teh_marbuta_to_ha=False).replace(" ", "")
            if nf and is_arabic_word(nf):
                norm_forms.append(nf)

        total = calculate_normalized_total(mass, speed, energy)

        if root in index:
            diagnostics["duplicate_roots"] += 1
            existing = index[root]
            existing["energy"] = max(existing["energy"], energy)
            existing["mass"] = max(existing["mass"], mass)
            existing["speed"] = max(existing["speed"], speed)
            existing["total"] = max(existing["total"], total)
            existing["forms"] = dedupe_keep_order(existing["forms"] + norm_forms)
            if existing["orbit"] == DEFAULT_ORBIT and orbit in KNOWN_ORBITS:
                existing["orbit"] = orbit
            diagnostics["entries_valid"] += 1
            continue

        index[root] = {
            "root": root,
            "orbit": orbit,
            "energy": round(energy, 4),
            "mass": round(mass, 4),
            "speed": round(speed, 4),
            "total": round(total, 4),
            "forms": dedupe_keep_order([root] + norm_forms),
        }
        diagnostics["entries_valid"] += 1

    diagnostics["roots_final"] = len(index)
    return {"index": index, "diagnostics": diagnostics}

def validate_and_load_letters(letters_path: Path = DEFAULT_LETTERS_PATH) -> Dict[str, Any]:
    """Loads compact 28-letter metrics"""
    raw = safe_read_json(letters_path)

    if not isinstance(raw, dict):
        raise ValueError("letters_28_compact.json must be a JSON object.")

    index = {}
    valid_count = 0

    for k, v in raw.items():
        key = normalize_arabic(str(k), force_teh_marbuta_to_ha=False).replace(" ", "")
        if len(key) != 1 or not is_arabic_word(key):
            continue
        if not isinstance(v, dict):
            continue

        mass = safe_float(v.get("mass", 1.0), 1.0)
        speed = safe_float(v.get("speed", 1.0), 1.0)
        index[key] = {"mass": mass, "speed": speed}
        valid_count += 1

    diagnostics = {"path": str(letters_path), "letters_valid": valid_count}
    return {"index": index, "diagnostics": diagnostics}

def validate_and_load_matrix(matrix_path: Path = DEFAULT_MATRIX_PATH) -> Dict[str, Any]:
    """Flexible matrix file loader"""
    raw = safe_read_json(matrix_path)

    verses = None
    if isinstance(raw, list):
        verses = raw
    elif isinstance(raw, dict) and isinstance(raw.get("verses"), list):
        verses = raw["verses"]
    else:
        raise ValueError("matrix_resonance.json must be a list or {'verses': [...]}")

    cleaned = []
    invalid = 0

    for i, item in enumerate(verses):
        if not isinstance(item, dict):
            invalid += 1
            continue
        verse_id = str(item.get("verse_id", item.get("id", f"verse_{i+1}"))).strip()
        text = str(item.get("text", "")).strip()
        if not text:
            invalid += 1
            continue
        cleaned.append({"verse_id": verse_id, "text": text})

    diagnostics = {
        "path": str(matrix_path),
        "verses_total": len(verses),
        "verses_valid": len(cleaned),
        "verses_invalid": invalid,
    }

    return {"verses": cleaned, "diagnostics": diagnostics}

# =========================================================
# ===================== 7) MATRIX INDEXING =====================
# =========================================================

def build_matrix_root_index(
    verses: List[Dict[str, Any]],
    roots_index: Dict[str, Dict[str, Any]]
) -> Dict[str, Any]:
    """Build root -> verses mapping using actual root matcher"""
    from collections import defaultdict

    root_to_verses = defaultdict(list)
    verse_to_roots = {}
    processed_words = 0

    for verse in verses:
        verse_id = verse["verse_id"]
        text = verse["text"]
        words = tokenize_arabic(text)
        found_roots = set()

        for w in words:
            processed_words += 1
            m = match_quranic_root(w, roots_index)
            if m["root"]:
                found_roots.add(m["root"])

        verse_to_roots[verse_id] = sorted(found_roots)
        for r in found_roots:
            root_to_verses[r].append({"verse_id": verse_id, "text": text})

    diagnostics = {
        "verses_indexed": len(verses),
        "processed_words": processed_words,
        "roots_with_verses": len(root_to_verses),
    }

    return {
        "root_to_verses": dict(root_to_verses),
        "verse_to_roots": verse_to_roots,
        "diagnostics": diagnostics,
    }

# =========================================================
# ===================== 8) ROOT MATCHING ENGINE =====================
# =========================================================

def match_quranic_root(word: str, roots_index: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Heuristic root matcher against the 1800+ lexicon"""
    candidates = generate_root_candidates(word)
    if not candidates:
        return {
            "input": word,
            "root": None,
            "confidence": 0.0,
            "orbit": None,
            "method": None,
            "candidates_considered": 0,
            "alternatives": [],
        }

    scored = []

    for item in candidates:
        form = item["form"]
        source = item["source"]
        weight = item["weight"]
        source_bonus = SOURCE_BONUS.get(source, 0.0)

        if form in roots_index:
            root_entry = roots_index[form]
            score = (weight * 0.70) + source_bonus + min(root_entry["energy"] * 0.03, 0.18)
            scored.append({
                "root": form,
                "score": score,
                "method": source,
                "entry": root_entry,
            })

        if len(form) > 3:
            for sub in pattern_extract_roots(form):
                if sub in roots_index:
                    root_entry = roots_index[sub]
                    score = (weight * 0.62) + source_bonus + 0.06 + min(root_entry["energy"] * 0.03, 0.18)
                    scored.append({
                        "root": sub,
                        "score": score,
                        "method": f"{source}->pattern_extract",
                        "entry": root_entry,
                    })

    if not scored:
        return {
            "input": word,
            "root": None,
            "confidence": 0.0,
            "orbit": None,
            "method": None,
            "candidates_considered": len(candidates),
            "alternatives": [],
        }

    best_per_root = {}
    for s in scored:
        r = s["root"]
        if r not in best_per_root or s["score"] > best_per_root[r]["score"]:
            best_per_root[r] = s

    ranked = sorted(best_per_root.values(), key=lambda x: x["score"], reverse=True)

    top = ranked[0]
    second = ranked[1] if len(ranked) > 1 else None

    raw_conf = top["score"]
    confidence = clamp(raw_conf / 1.25, 0.0, 1.0)

    ambiguous = False
    ambiguity_gap = None
    if second:
        ambiguity_gap = top["score"] - second["score"]
        if ambiguity_gap < 0.08:
            ambiguous = True
            confidence = min(confidence, 0.72)

    return {
        "input": word,
        "root": top["root"],
        "confidence": round(confidence, 4),
        "orbit": top["entry"]["orbit"],
        "method": top["method"],
        "candidates_considered": len(candidates),
        "ambiguous": ambiguous,
        "ambiguity_gap": round(ambiguity_gap, 4) if ambiguity_gap is not None else None,
        "alternatives": [
            {
                "root": x["root"],
                "score": round(x["score"], 4),
                "orbit": x["entry"]["orbit"],
                "method": x["method"],
            }
            for x in ranked[:5]
        ],
    }

# =========================================================
# ===================== 9) CONTEXTUAL HARMONY =====================
# =========================================================

def contextual_harmony(roots_found: List[str], roots_index: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Contextual harmony based on orbit cohesion"""
    if not roots_found:
        return {
            "score": 0.0,
            "label": "صمت",
            "dominant_orbit": None,
            "orbit_distribution": {},
        }

    orbit_counts = Counter()
    for r in roots_found:
        orbit = roots_index.get(r, {}).get("orbit", DEFAULT_ORBIT)
        orbit_counts[orbit] += 1

    total = sum(orbit_counts.values())
    dominant_orbit, dominant_count = orbit_counts.most_common(1)[0]
    concentration = dominant_count / max(1, total)

    unique_ratio = len(set(roots_found)) / max(1, len(roots_found))
    harmony = (concentration * 0.7) + ((1 - abs(unique_ratio - 0.75)) * 0.3)
    harmony = clamp(harmony, 0.0, 1.0)

    if harmony >= 0.85:
        label = "وسام التناغم"
    elif harmony >= 0.65:
        label = "وحدة عالية"
    elif harmony >= 0.45:
        label = "تماسك متوسط"
    else:
        label = "تناثر"

    return {
        "score": round(harmony, 4),
        "label": label,
        "dominant_orbit": dominant_orbit,
        "orbit_distribution": dict(orbit_counts),
    }

def generate_closing_statement(
    roots_found: List[str],
    orbit_counts: Counter,
    harmony: Dict[str, Any],
    avg_conf: float,
) -> str:
    if not roots_found:
        return "لم يظهر جذر قرآني حاسم في هذا النص ضمن المعجم الحالي، والنتيجة تميل إلى الصمت التحليلي."

    dom = None
    if orbit_counts:
        dom = orbit_counts.most_common(1)[0][0]

    if harmony["score"] >= 0.85:
        return f"النص يُظهر وحدة طاقية عالية جدًا، ومداره الغالب هو «{dom}»، مع تناغم سياقي سيادي وثقة تحليلية مرتفعة."
    if harmony["score"] >= 0.65:
        return f"النص متماسك دلاليًا، ومداره الغالب هو «{dom}»، مع مؤشرات انسجام واضحة وثقة متوازنة."
    if avg_conf >= 0.70:
        return f"النص يحمل جذورًا معتبرة ضمن مدار «{dom}»، لكن بنيته أقل تماسكًا من حالة التناغم الكامل."
    return "ظهرت جذور محتملة، لكن البنية لا تزال بحاجة إلى قراءة بشرية أدق لتثبيت المسار النهائي."

# =========================================================
# ===================== 10) MAIN ANALYSIS ENGINE =====================
# =========================================================

def analyze_text(
    text: str,
    roots_index: Dict[str, Dict[str, Any]],
    letters_index: Dict[str, Dict[str, float]],
    matrix_root_index: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    words = tokenize_arabic(text)

    word_results = []
    roots_found = []
    ambiguity_flags = []

    total_mass = 0.0
    total_speed = 0.0
    total_energy = 0.0

    for w in words:
        mass, speed = estimate_word_mass_speed(w, letters_index)
        match = match_quranic_root(w, roots_index)

        energy = 0.0
        orbit = None
        root = None

        if match["root"]:
            root = match["root"]
            entry = roots_index[root]
            energy = entry["energy"]
            orbit = entry["orbit"]
            roots_found.append(root)

        total_mass += mass
        total_speed += speed
        total_energy += energy

        word_results.append({
            "word": w,
            "mass": round(mass, 4),
            "speed": round(speed, 4),
            "energy": round(energy, 4),
            "root": root,
            "orbit": orbit,
            "confidence": match["confidence"],
            "method": match["method"],
            "ambiguous": match.get("ambiguous", False),
            "alternatives": match.get("alternatives", []),
        })

        if match.get("ambiguous"):
            ambiguity_flags.append({
                "word": w,
                "best_root": match["root"],
                "alternatives": match.get("alternatives", [])[:3],
            })

    harmony = contextual_harmony(roots_found, roots_index)
    total_index = calculate_normalized_total(total_mass, total_speed, total_energy)

    resonance_refs = []
    if matrix_root_index and roots_found:
        root_to_verses = matrix_root_index.get("root_to_verses", {})
        seen_verse_ids = set()
        for r in sorted(set(roots_found)):
            for verse in root_to_verses.get(r, [])[:3]:
                if verse["verse_id"] not in seen_verse_ids:
                    resonance_refs.append({
                        "root": r,
                        "verse_id": verse["verse_id"],
                        "text": verse["text"],
                    })
                    seen_verse_ids.add(verse["verse_id"])
                if len(resonance_refs) >= 9:
                    break
            if len(resonance_refs) >= 9:
                break

    orbit_counts = Counter(roots_index[r]["orbit"] for r in roots_found if r in roots_index)

    confidence_values = [wr["confidence"] for wr in word_results if wr["root"]]
    avg_conf = round(sum(confidence_values) / max(1, len(confidence_values)), 4)

    statement = generate_closing_statement(
        roots_found=roots_found,
        orbit_counts=orbit_counts,
        harmony=harmony,
        avg_conf=avg_conf,
    )

    return {
        "input_text": text,
        "normalized_words": words,
        "word_results": word_results,
        "roots_found": roots_found,
        "unique_roots": sorted(set(roots_found)),
        "orbit_counts": dict(orbit_counts),
        "ambiguity_flags": ambiguity_flags,
        "summary": {
            "words_count": len(words),
            "roots_count": len(roots_found),
            "unique_roots_count": len(set(roots_found)),
            "avg_confidence": avg_conf,
            "total_mass": round(total_mass, 4),
            "total_speed": round(total_speed, 4),
            "total_energy": round(total_energy, 4),
            "total_index": round(total_index, 4),
        },
        "harmony": harmony,
        "resonance_refs": resonance_refs,
        "closing_statement": statement,
    }

def export_analysis_json_payload(analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Clean JSON-safe export payload"""
    return {
        "version": APP_VERSION,
        "input_text": analysis.get("input_text"),
        "summary": analysis.get("summary"),
        "unique_roots": analysis.get("unique_roots"),
        "orbit_counts": analysis.get("orbit_counts"),
        "harmony": analysis.get("harmony"),
        "ambiguity_flags": analysis.get("ambiguity_flags"),
        "closing_statement": analysis.get("closing_statement"),
        "word_results": analysis.get("word_results"),
        "resonance_refs": analysis.get("resonance_refs"),
    }

# =========================================================
# ===================== 11) BOOTSTRAP =====================
# =========================================================

@st.cache_resource(show_spinner=True)
def bootstrap_project() -> Dict[str, Any]:
    """Full project bootstrap with strict diagnostics"""
    # Find data files
    roots_path = search_file_path("quranic_roots_1800.json") or DEFAULT_ROOTS_PATH
    letters_path = search_file_path("letters_28_compact.json") or DEFAULT_LETTERS_PATH
    matrix_path = search_file_path("matrix_resonance.json") or DEFAULT_MATRIX_PATH

    roots_bundle = validate_and_load_roots(roots_path)
    letters_bundle = validate_and_load_letters(letters_path)
    matrix_bundle = validate_and_load_matrix(matrix_path)

    matrix_index = build_matrix_root_index(
        verses=matrix_bundle["verses"],
        roots_index=roots_bundle["index"],
    )

    return {
        "version": APP_VERSION,
        "roots": roots_bundle,
        "letters": letters_bundle,
        "matrix": matrix_bundle,
        "matrix_index": matrix_index,
    }

# =========================================================
# ===================== 12) UI PANELS =====================
# =========================================================

def inject_global_css():
    st.markdown("""
    <style>
    .main {
        direction: rtl;
    }

    .nibras-title {
        font-size: 2rem;
        font-weight: 800;
        margin-bottom: 0.25rem;
    }

    .nibras-sub {
        opacity: 0.85;
        margin-bottom: 1rem;
    }

    .glass-card {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.08);
        padding: 14px;
        border-radius: 14px;
        margin-bottom: 12px;
    }

    .status-ok {
        background: rgba(16, 185, 129, 0.10);
        border: 1px solid rgba(16, 185, 129, 0.45);
        padding: 10px;
        border-radius: 10px;
        margin: 8px 0;
    }

    .status-error {
        background: rgba(239, 68, 68, 0.10);
        border: 1px solid rgba(239, 68, 68, 0.45);
        padding: 10px;
        border-radius: 10px;
        margin: 8px 0;
    }

    .status-warn {
        background: rgba(245, 158, 11, 0.10);
        border: 1px solid rgba(245, 158, 11, 0.45);
        padding: 10px;
        border-radius: 10px;
        margin: 8px 0;
    }

    .tiny {
        font-size: 0.85rem;
        opacity: 0.85;
    }

    .root-chip {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 999px;
        margin: 2px 4px 2px 0;
        border: 1px solid rgba(255,255,255,0.10);
        background: rgba(255,255,255,0.03);
        font-size: 0.9rem;
    }

    .verse-box {
        border-right: 3px solid rgba(255,255,255,0.18);
        padding: 10px 12px;
        margin: 8px 0;
        background: rgba(255,255,255,0.02);
        border-radius: 8px;
    }

    .mono {
        font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
        direction: ltr;
        text-align: left;
    }
    </style>
    """, unsafe_allow_html=True)

def render_header(version: str):
    st.markdown(f'<div class="nibras-title">نبراس السيادي — {version}</div>', unsafe_allow_html=True)
    st.markdown('<div class="nibras-sub">محرك رنين الجذور القرآنية + التناغم السياقي + التشخيص السيادي</div>', unsafe_allow_html=True)

def render_sidebar_diagnostics(bootstrap: Dict[str, Any]):
    st.sidebar.markdown("## التشخيص السيادي")

    roots_diag = bootstrap["roots"]["diagnostics"]
    letters_diag = bootstrap["letters"]["diagnostics"]
    matrix_diag = bootstrap["matrix"]["diagnostics"]
    matrix_index_diag = bootstrap["matrix_index"]["diagnostics"] if bootstrap.get("matrix_index") else None

    st.sidebar.markdown("### ملف الجذور")
    st.sidebar.write(f"**المسار:** `{roots_diag['path']}`")
    st.sidebar.write(f"**إجمالي الإدخالات:** {roots_diag['entries_total']}")
    st.sidebar.write(f"**الصالحة:** {roots_diag['entries_valid']}")
    st.sidebar.write(f"**غير الصالحة:** {roots_diag['entries_invalid']}")
    st.sidebar.write(f"**الجذور النهائية:** {roots_diag['roots_final']}")
    st.sidebar.write(f"**التكرارات:** {roots_diag['duplicate_roots']}")
    st.sidebar.write(f"**مدارات غريبة → وعي:** {roots_diag['unknown_orbit_count']}")

    unknown_seen = roots_diag.get("unknown_orbits_seen", {})
    if unknown_seen:
        with st.sidebar.expander("المدارات الغريبة المرصودة"):
            for k, v in unknown_seen.items():
                st.write(f"- {k}: {v}")

    if roots_diag["roots_final"] >= 1800:
        st.sidebar.markdown('<div class="status-ok">✅ ملف الجذور تجاوز/حقق 1800+</div>', unsafe_allow_html=True)
    else:
        st.sidebar.markdown('<div class="status-warn">⚠️ ملف الجذور أقل من 1800 جذر</div>', unsafe_allow_html=True)

    st.sidebar.markdown("### ملف الحروف")
    st.sidebar.write(f"**المسار:** `{letters_diag['path']}`")
    st.sidebar.write(f"**الحروف الصالحة:** {letters_diag['letters_valid']}")

    st.sidebar.markdown("### ملف المصفوفة")
    st.sidebar.write(f"**المسار:** `{matrix_diag['path']}`")
    st.sidebar.write(f"**الآيات الكلية:** {matrix_diag['verses_total']}")
    st.sidebar.write(f"**الآيات الصالحة:** {matrix_diag['verses_valid']}")
    st.sidebar.write(f"**الآيات غير الصالحة:** {matrix_diag['verses_invalid']}")

    if matrix_index_diag:
        st.sidebar.markdown("### فهرسة المصفوفة")
        st.sidebar.write(f"**الآيات المفهرسة:** {matrix_index_diag['verses_indexed']}")
        st.sidebar.write(f"**الكلمات المعالجة:** {matrix_index_diag['processed_words']}")
        st.sidebar.write(f"**جذور مرتبطة بآيات:** {matrix_index_diag['roots_with_verses']}")

def render_sidebar_controls() -> Dict[str, Any]:
    st.sidebar.markdown("## وضع التشغيل")
    silent_mode = st.sidebar.toggle("الرصد الصامت (مختبري)", value=False)
    show_word_table = st.sidebar.toggle("إظهار جدول الكلمات", value=True)
    show_resonance = st.sidebar.toggle("إظهار مراجع الرنين", value=True)
    show_json_preview = st.sidebar.toggle("معاينة JSON", value=False)
    max_history = st.sidebar.slider("سجل الجلسة", min_value=1, max_value=10, value=5)
    return {
        "silent_mode": silent_mode,
        "show_word_table": show_word_table,
        "show_resonance": show_resonance,
        "show_json_preview": show_json_preview,
        "max_history": max_history,
    }

def render_summary(analysis: Dict[str, Any]):
    s = analysis["summary"]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("الكلمات", s["words_count"])
    c2.metric("الجذور", s["roots_count"])
    c3.metric("الفريدة", s["unique_roots_count"])
    c4.metric("الثقة", f"{round(s['avg_confidence'] * 100, 1)}%")

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("الكتلة", s["total_mass"])
    c6.metric("السرعة", s["total_speed"])
    c7.metric("الطاقة", s["total_energy"])
    c8.metric("المؤشر السيادي", s["total_index"])

def render_harmony(analysis: Dict[str, Any]):
    harmony = analysis["harmony"]
    st.markdown("### التناغم السياقي")
    st.progress(float(harmony["score"]))
    st.write(f"**الحكم:** {harmony['label']}")
    if harmony["dominant_orbit"]:
        st.write(f"**المدار الغالب:** {harmony['dominant_orbit']}")

    dist = harmony.get("orbit_distribution", {})
    if dist:
        st.write("**توزيع المدارات:**")
        st.json(dist)

def render_roots(analysis: Dict[str, Any]):
    st.markdown("### الجذور الفريدة")
    roots = analysis["unique_roots"]
    if not roots:
        st.markdown('<div class="status-warn">⚠️ لم يتم العثور على جذور مطابقة.</div>', unsafe_allow_html=True)
        return

    chips = "".join([f'<span class="root-chip">{r}</span>' for r in roots])
    st.markdown(chips, unsafe_allow_html=True)

def render_word_results(analysis: Dict[str, Any], show_table: bool = True):
    st.markdown("### نتائج الكلمات")

    if not show_table:
        for wr in analysis["word_results"]:
            root = wr["root"] if wr["root"] else "—"
            orbit = wr["orbit"] if wr["orbit"] else "—"
            conf = f"{round(wr['confidence'] * 100, 1)}%"
            st.markdown(
                f"**{wr['word']}** → جذر: **{root}** | مدار: **{orbit}** | ثقة: **{conf}** | طريقة: `{wr['method']}`"
            )
        return

    rows = []
    for wr in analysis["word_results"]:
        rows.append({
            "الكلمة": wr["word"],
            "الجذر": wr["root"] or "",
            "المدار": wr["orbit"] or "",
            "الثقة": round(wr["confidence"] * 100, 1),
            "الطريقة": wr["method"] or "",
            "الكتلة": wr["mass"],
            "السرعة": wr["speed"],
            "الطاقة": wr["energy"],
            "ملتبس؟": "نعم" if wr["ambiguous"] else "لا",
        })

    st.dataframe(rows, use_container_width=True)

def render_ambiguity_flags(analysis: Dict[str, Any]):
    flags = analysis.get("ambiguity_flags", [])
    st.markdown("### التحصين من الالتباس")
    if not flags:
        st.markdown('<div class="status-ok">✅ لا توجد حالات التباس حرجة في هذه القراءة.</div>', unsafe_allow_html=True)
        return

    st.markdown('<div class="status-warn">⚠️ توجد كلمات تحتمل أكثر من جذر محتمل. القراءة البشرية مرجّحة هنا.</div>', unsafe_allow_html=True)

    for item in flags:
        with st.expander(f"الكلمة الملتبسة: {item['word']}"):
            st.write(f"**أفضل جذر حاليًا:** {item['best_root']}")
            st.write("**بدائل محتملة:**")
            for alt in item["alternatives"]:
                st.write(f"- {alt['root']} | المدار: {alt['orbit']} | score: {alt['score']} | via: {alt['method']}")

def render_resonance_refs(analysis: Dict[str, Any]):
    refs = analysis.get("resonance_refs", [])
    st.markdown("### مراجع الرنين من المصفوفة")
    if not refs:
        st.markdown('<div class="status-warn">⚠️ لا توجد مراجع رنين مسترجعة من المصفوفة لهذه القراءة.</div>', unsafe_allow_html=True)
        return

    for ref in refs:
        st.markdown(
            f'<div class="verse-box"><b>{ref["verse_id"]}</b> — جذر: <b>{ref["root"]}</b><br>{ref["text"]}</div>',
            unsafe_allow_html=True
        )

def render_closing_statement(analysis: Dict[str, Any]):
    st.markdown("### البيان الختامي")
    st.markdown(f'<div class="glass-card">{analysis["closing_statement"]}</div>', unsafe_allow_html=True)

def render_history(history: List[Dict[str, Any]]):
    st.markdown("### سجل الجلسة")
    if not history:
        st.markdown('<div class="status-warn">⚠️ لا توجد تحليلات محفوظة بعد.</div>', unsafe_allow_html=True)
        return

    for i, item in enumerate(reversed(history), start=1):
        with st.expander(f"سجل #{i} — {item.get('input_text', '')[:60]}"):
            st.write(f"**النص:** {item.get('input_text', '')}")
            st.write(f"**الجذور الفريدة:** {', '.join(item.get('unique_roots', [])) if item.get('unique_roots') else '—'}")
            st.write(f"**البيان:** {item.get('closing_statement', '—')}")

def render_export_buttons(export_payload: Dict[str, Any]) -> str:
    json_text = json.dumps(export_payload, ensure_ascii=False, indent=2)

    st.download_button(
        label="تحميل الوثيقة الوجودية (JSON)",
        data=json_text.encode("utf-8"),
        file_name="nibras_analysis.json",
        mime="application/json",
        use_container_width=True,
    )

    return json_text

# =========================================================
# ===================== 13) MAIN APP =====================
# =========================================================

def main():
    inject_global_css()
    render_header(APP_VERSION)

    # Load data
    try:
        bootstrap = bootstrap_project()
    except Exception as e:
        st.error(f"فشل الإقلاع السيادي: {e}")
        st.stop()

    render_sidebar_diagnostics(bootstrap)
    controls = render_sidebar_controls()

    # Session state
    if "nibras_history" not in st.session_state:
        st.session_state.nibras_history = []

    if len(st.session_state.nibras_history) > controls["max_history"]:
        st.session_state.nibras_history = st.session_state.nibras_history[-controls["max_history"]:]

    # Main input
    default_text = "إن مع العسر يسرا"
    text = st.text_area(
        "أدخل النص المراد تحليله",
        value=default_text,
        height=120,
        placeholder="اكتب آية أو نصًا عربيًا...",
    )

    analyze_btn = st.button("ابدأ التحليل السيادي", use_container_width=True)

    if analyze_btn:
        with st.spinner("جاري استنطاق الجذور والمدارات..."):
            analysis = analyze_text(
                text=text,
                roots_index=bootstrap["roots"]["index"],
                letters_index=bootstrap["letters"]["index"],
                matrix_root_index=bootstrap["matrix_index"],
            )

        # Save history
        st.session_state.nibras_history.append({
            "input_text": analysis["input_text"],
            "unique_roots": analysis["unique_roots"],
            "closing_statement": analysis["closing_statement"],
        })

        if len(st.session_state.nibras_history) > controls["max_history"]:
            st.session_state.nibras_history = st.session_state.nibras_history[-controls["max_history"]:]

        if controls["silent_mode"]:
            st.markdown("## الوضع المختبري")
        else:
            st.markdown("## القراءة السيادية")

        render_summary(analysis)
        render_harmony(analysis)
        render_roots(analysis)
        render_word_results(analysis, show_table=controls["show_word_table"])
        render_ambiguity_flags(analysis)

        if controls["show_resonance"]:
            render_resonance_refs(analysis)

        render_closing_statement(analysis)

        st.markdown("### التصدير السيادي")
        export_payload = export_analysis_json_payload(analysis)
        json_preview = render_export_buttons(export_payload)

        if controls["show_json_preview"]:
            st.code(json_preview, language="json")

    # History
    render_history(st.session_state.nibras_history)

    # Footer in sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Blekinge, Sweden | Nibras Sovereign v30.0**")
    st.sidebar.markdown("*Mohamed | As-Sajdah [5]*")
    st.sidebar.markdown("*خِت فِت.*")

if __name__ == "__main__":
    main()
