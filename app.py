import streamlit as st
import json
import re
import os
import time
from datetime import datetime
from collections import defaultdict, Counter

# =========================================================
# NIBRAS SOVEREIGN v30.0 — ORBIT-LOCKED EDITION
# =========================================================

st.set_page_config(
    page_title="NIBRAS SOVEREIGN v30.0 — ORBIT LOCKED",
    page_icon="🜂",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================================
# CONFIG
# =========================================================

APP_VERSION = "30.0"
APP_NAME = "NIBRAS SOVEREIGN"
APP_TITLE = f"{APP_NAME} v{APP_VERSION} — ORBIT-LOCKED EDITION"

LEXICON_PATH = "quranic_1800_roots.json"
LETTERS_PATH = "letters_values.json"
MATRIX_PATH = "matrix_resonance.json"

# ---------------------------------------------------------
# ORBIT LOCK (CRITICAL)
# ---------------------------------------------------------
# هذه هي المدارات الرسمية المعتمدة داخل النظام.
# إن كانت ملفاتك تستخدم أسماء مختلفة، أضفها في ORBIT_ALIASES.
KNOWN_ORBITS = {
    "وعي",
    "نور",
    "رحمة",
    "حق",
    "ميزان",
    "صبر",
    "هداية",
    "قوة",
    "بصيرة",
    "توحيد",
}

# خريطة أسماء بديلة -> الاسم الرسمي
# عدّلها حسب ملفك الحقيقي إن لزم.
ORBIT_ALIASES = {
    "نورانية": "نور",
    "رحماني": "رحمة",
    "الرحمة": "رحمة",
    "الحق": "حق",
    "الميزان": "ميزان",
    "الصبر": "صبر",
    "الهداية": "هداية",
    "القوة": "قوة",
    "البصيرة": "بصيرة",
    "التوحيد": "توحيد",
    "وعي_وجودي": "وعي",
    "وعي وجودي": "وعي",
}

STRICT_ORBIT_MODE = True  # لا fallback صامت إلى "وعي"
UNKNOWN_ORBIT_LABEL = "غير_معروف"

MAX_HISTORY = 5
MAX_COMPARE = 3

# =========================================================
# CSS
# =========================================================

st.markdown("""
<style>
html, body, [class*="css"]  {
    direction: rtl;
    text-align: right;
    font-family: "Segoe UI", Tahoma, sans-serif;
}
.block-container {
    padding-top: 1rem;
    padding-bottom: 2rem;
}
.nibras-title {
    font-size: 2rem;
    font-weight: 800;
    margin-bottom: 0.25rem;
    color: #f8fafc;
}
.nibras-sub {
    color: #94a3b8;
    margin-bottom: 1rem;
}
.card {
    background: #111827;
    border: 1px solid #1f2937;
    border-radius: 16px;
    padding: 14px 16px;
    margin-bottom: 12px;
}
.metric-card {
    background: #0f172a;
    border: 1px solid #1e293b;
    border-radius: 14px;
    padding: 12px;
    margin-bottom: 8px;
}
.status-ok {
    background: #0f2a1d;
    border: 1px solid #10b981;
    padding: 10px;
    border-radius: 10px;
    margin-bottom: 8px;
}
.status-error {
    background: #2a1111;
    border: 1px solid #ef4444;
    padding: 10px;
    border-radius: 10px;
    margin-bottom: 8px;
}
.status-warn {
    background: #2a2110;
    border: 1px solid #f59e0b;
    padding: 10px;
    border-radius: 10px;
    margin-bottom: 8px;
}
.root-chip {
    display: inline-block;
    background: #1e293b;
    color: #e2e8f0;
    border: 1px solid #334155;
    padding: 6px 10px;
    border-radius: 999px;
    margin: 4px 4px 0 0;
    font-size: 0.9rem;
}
.small-note {
    color: #94a3b8;
    font-size: 0.85rem;
}
.orbit-chip {
    display: inline-block;
    background: #172554;
    color: #dbeafe;
    border: 1px solid #1d4ed8;
    padding: 5px 10px;
    border-radius: 999px;
    margin: 4px 4px 0 0;
    font-size: 0.85rem;
}
.unknown-orbit {
    background: #3f1d0b;
    color: #fed7aa;
    border: 1px solid #f97316;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# SESSION STATE
# =========================================================

if "nibras_state" not in st.session_state:
    st.session_state.nibras_state = {
        "history": [],
        "compare": [],
        "silent_mode": False,
        "ambiguity_buffer": [],
        "last_analysis": None,
    }

def S():
    return st.session_state.nibras_state

# =========================================================
# UTILITIES
# =========================================================

def now_iso():
    return datetime.utcnow().isoformat()

def safe_read_json(path):
    if not os.path.exists(path):
        return None, f"الملف غير موجود: {path}"
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data, None
    except Exception as e:
        return None, f"فشل قراءة JSON من {path}: {e}"

def file_stats(path):
    if not os.path.exists(path):
        return {"exists": False}
    try:
        size = os.path.getsize(path)
        with open(path, "r", encoding="utf-8") as f:
            lines = sum(1 for _ in f)
        return {
            "exists": True,
            "size_bytes": size,
            "size_kb": round(size / 1024, 2),
            "lines": lines,
        }
    except Exception:
        return {"exists": True, "size_bytes": None, "size_kb": None, "lines": None}

def push_history(item):
    hist = S()["history"]
    hist.insert(0, item)
    S()["history"] = hist[:MAX_HISTORY]

def add_compare(item):
    comp = S()["compare"]
    comp.insert(0, item)
    dedup = []
    seen = set()
    for x in comp:
        key = x.get("id")
        if key not in seen:
            dedup.append(x)
            seen.add(key)
    S()["compare"] = dedup[:MAX_COMPARE]

# =========================================================
# NORMALIZATION
# =========================================================

ARABIC_DIACRITICS = re.compile(r'[\u0617-\u061A\u064B-\u0652\u0670\u06D6-\u06ED]')
NON_ARABIC_KEEP_SPACE = re.compile(r'[^\u0621-\u063A\u0641-\u064A\s]')

PREFIXES = [
    "وال", "بال", "كال", "فال", "لل", "ال",
    "و", "ف", "ب", "ك", "ل", "س"
]

SUFFIXES = [
    "يات", "يون", "هما", "كما", "كم", "كن", "نا", "ها", "هم", "هن",
    "ية", "ات", "ون", "ين", "ان", "ة", "ه", "ي", "ك", "ت", "ا", "ن"
]

def normalize_arabic(text, taa_mode="preserve"):
    """
    taa_mode:
      - preserve: تبقي ة كما هي
      - variant_heh: لا تغيّر الأصل، لكن يمكن لاحقًا توليد variant
    """
    if not text:
        return ""
    t = str(text).strip()
    t = ARABIC_DIACRITICS.sub("", t)
    t = t.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا")
    t = t.replace("ؤ", "و").replace("ئ", "ي")
    t = t.replace("ى", "ي")
    # لا نحول ة إلى ه بشكل قسري في v30
    t = NON_ARABIC_KEEP_SPACE.sub(" ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t

def normalize_token(token):
    return normalize_arabic(token).replace(" ", "")

def arabic_tokens(text):
    t = normalize_arabic(text)
    return [x for x in t.split() if x.strip()]

def maybe_taa_variants(token):
    """إن انتهت بـ ة، نعطي variant إضافي بـ ه دون تدمير الأصل."""
    variants = [token]
    if token.endswith("ة"):
        variants.append(token[:-1] + "ه")
    return list(dict.fromkeys(variants))

def strip_prefixes(word):
    outs = []
    for p in PREFIXES:
        if word.startswith(p) and len(word) - len(p) >= 2:
            outs.append(word[len(p):])
    return outs

def strip_suffixes(word):
    outs = []
    for s in SUFFIXES:
        if word.endswith(s) and len(word) - len(s) >= 2:
            outs.append(word[:-len(s)])
    return outs

def reduce_doubles_soft(word):
    """
    تقليل ناعم جدًا، فقط عند تكرار 3 أحرف متتالية أو أكثر.
    لا نكسر التضعيف الطبيعي.
    """
    if len(word) < 4:
        return word
    return re.sub(r'(.)\1{2,}', r'\1\1', word)

def sliding_triples(word):
    if len(word) < 3:
        return []
    out = []
    for i in range(len(word) - 2):
        out.append(word[i:i+3])
    return out

# =========================================================
# MORPHOLOGICAL PATTERN FILTERS (LIGHT)
# =========================================================

def pattern_candidates(word):
    """
    مرشحات صرفية خفيفة وليست محللًا صرفيًا كاملاً.
    """
    cands = set()
    w = word

    # استفعل / استفعال
    if w.startswith("است") and len(w) >= 5:
        core = w[3:]
        if len(core) >= 3:
            cands.add(core[:3])

    # مفعول / مفاعل / مفعلة تقريبية
    if w.startswith("م") and len(w) >= 4:
        core = w[1:]
        if len(core) >= 3:
            cands.add(core[:3])

    # تفعيل / تفعّل / تفاعل
    if w.startswith("ت") and len(w) >= 4:
        core = w[1:]
        if len(core) >= 3:
            cands.add(core[:3])

    # انفعل
    if w.startswith("ان") and len(w) >= 5:
        core = w[2:]
        if len(core) >= 3:
            cands.add(core[:3])

    # افتعل
    if w.startswith("افت") and len(w) >= 5:
        core = w[3:]
        if len(core) >= 3:
            cands.add(core[:3])

    return list(cands)

def generate_root_candidates(token):
    """
    توليد مرشحين منظم مع أوزان مصادر.
    """
    candidates = []

    def add(form, source, weight):
        form = normalize_token(form)
        if len(form) >= 2:
            candidates.append({"form": form, "source": source, "weight": weight})

    base = normalize_token(token)
    if not base:
        return []

    # الأصل + variants للـ ة
    base_variants = []
    for v in maybe_taa_variants(base):
        base_variants.append(v)

    for v in base_variants:
        add(v, "normalized", 1.00)

        # pattern candidates
        for pc in pattern_candidates(v):
            add(pc, "pattern_filter", 0.86)

        # prefix strip
        for x in strip_prefixes(v):
            add(x, "prefix_strip", 0.82)
            for pc in pattern_candidates(x):
                add(pc, "pattern_filter_after_prefix", 0.80)

        # suffix strip
        for x in strip_suffixes(v):
            add(x, "suffix_strip", 0.80)
            for pc in pattern_candidates(x):
                add(pc, "pattern_filter_after_suffix", 0.78)

        # prefix + suffix
        for p in strip_prefixes(v):
            for ps in strip_suffixes(p):
                add(ps, "prefix_suffix_strip", 0.72)

        # soft double reduce
        rd = reduce_doubles_soft(v)
        if rd != v:
            add(rd, "soft_reduce_doubles", 0.60)

        # sliding triples = fallback only
        for tri in sliding_triples(v):
            add(tri, "sliding_triple", 0.45)

    # dedup مع أعلى وزن لكل (form, source)
    best = {}
    for c in candidates:
        key = (c["form"], c["source"])
        if key not in best or c["weight"] > best[key]["weight"]:
            best[key] = c

    return list(best.values())

# =========================================================
# LETTERS / VALUES
# =========================================================

@st.cache_data(show_spinner=False)
def load_letters_index():
    data, err = safe_read_json(LETTERS_PATH)
    default_map = {}

    if err or data is None:
        # fallback minimal safe
        for ch in "ابتثجحخدذرزسشصضطظعغفقكلمنهوي":
            default_map[ch] = {"mass": 1.0, "speed": 1.0}
        return default_map, {"loaded": False, "error": err or "no data"}

    idx = {}
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, dict):
                idx[normalize_token(k)] = {
                    "mass": float(v.get("mass", 1.0)),
                    "speed": float(v.get("speed", 1.0)),
                }
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                letter = normalize_token(item.get("letter", ""))
                if letter:
                    idx[letter] = {
                        "mass": float(item.get("mass", 1.0)),
                        "speed": float(item.get("speed", 1.0)),
                    }

    if not idx:
        for ch in "ابتثجحخدذرزسشصضطظعغفقكلمنهوي":
            idx[ch] = {"mass": 1.0, "speed": 1.0}

    return idx, {"loaded": True, "error": None, "count": len(idx)}

def compute_mass_speed(root, letters_idx):
    mass = 0.0
    speed = 0.0
    for ch in normalize_token(root):
        vals = letters_idx.get(ch, {"mass": 1.0, "speed": 1.0})
        mass += float(vals.get("mass", 1.0))
        speed += float(vals.get("speed", 1.0))
    return round(mass, 3), round(speed, 3)

# =========================================================
# ORBIT NORMALIZATION (CRITICAL)
# =========================================================

def canonicalize_orbit(raw_orbit):
    """
    لا fallback صامت إلى "وعي".
    """
    if raw_orbit is None:
        return UNKNOWN_ORBIT_LABEL, {
            "raw": None,
            "canonical": UNKNOWN_ORBIT_LABEL,
            "known": False,
            "aliased": False,
        }

    raw = str(raw_orbit).strip()
    raw_norm = normalize_arabic(raw)

    if raw in KNOWN_ORBITS:
        return raw, {
            "raw": raw,
            "canonical": raw,
            "known": True,
            "aliased": False,
        }

    if raw_norm in KNOWN_ORBITS:
        return raw_norm, {
            "raw": raw,
            "canonical": raw_norm,
            "known": True,
            "aliased": False,
        }

    # alias exact
    if raw in ORBIT_ALIASES:
        mapped = ORBIT_ALIASES[raw]
        return mapped, {
            "raw": raw,
            "canonical": mapped,
            "known": True,
            "aliased": True,
        }

    # alias normalized
    if raw_norm in ORBIT_ALIASES:
        mapped = ORBIT_ALIASES[raw_norm]
        return mapped, {
            "raw": raw,
            "canonical": mapped,
            "known": True,
            "aliased": True,
        }

    if STRICT_ORBIT_MODE:
        return UNKNOWN_ORBIT_LABEL, {
            "raw": raw,
            "canonical": UNKNOWN_ORBIT_LABEL,
            "known": False,
            "aliased": False,
        }

    # لو أوقفت الوضع الصارم فقط
    return "وعي", {
        "raw": raw,
        "canonical": "وعي",
        "known": False,
        "aliased": False,
    }

# =========================================================
# LEXICON LOADING (STRICT)
# =========================================================

@st.cache_data(show_spinner=False)
def load_flat_lexicon():
    data, err = safe_read_json(LEXICON_PATH)

    diagnostics = {
        "loaded": False,
        "error": err,
        "file_stats": file_stats(LEXICON_PATH),
        "entries_total": 0,
        "entries_valid": 0,
        "roots_unique": 0,
        "duplicates": 0,
        "invalid_entries": 0,
        "missing_root": 0,
        "non_arabic_roots": 0,
        "unknown_orbits_count": 0,
        "unknown_orbits": Counter(),
        "aliased_orbits_count": 0,
        "aliased_orbits": Counter(),
        "orbit_distribution": Counter(),
    }

    if err or data is None:
        return {}, diagnostics

    # يدعم list أو dict
    raw_entries = []
    if isinstance(data, list):
        raw_entries = data
    elif isinstance(data, dict):
        # إذا كان dict من root -> metadata
        for k, v in data.items():
            if isinstance(v, dict):
                item = dict(v)
                item["root"] = item.get("root", k)
                raw_entries.append(item)
            else:
                raw_entries.append({"root": k})
    else:
        diagnostics["error"] = "بنية ملف الجذور غير مدعومة (يجب list أو dict)."
        return {}, diagnostics

    diagnostics["entries_total"] = len(raw_entries)

    lex = {}
    seen_roots = set()

    for item in raw_entries:
        if not isinstance(item, dict):
            diagnostics["invalid_entries"] += 1
            continue

        root_raw = item.get("root", "")
        root = normalize_token(root_raw)

        if not root:
            diagnostics["missing_root"] += 1
            continue

        # تحقق عربي تقريبي
        if not re.fullmatch(r'[\u0621-\u063A\u0641-\u064A]+', root):
            diagnostics["non_arabic_roots"] += 1
            continue

        raw_orbit = item.get("orbit", None)
        orbit, orbit_meta = canonicalize_orbit(raw_orbit)

        if not orbit_meta["known"]:
            diagnostics["unknown_orbits_count"] += 1
            diagnostics["unknown_orbits"][str(orbit_meta["raw"])] += 1
        elif orbit_meta["aliased"]:
            diagnostics["aliased_orbits_count"] += 1
            diagnostics["aliased_orbits"][str(orbit_meta["raw"])] += 1

        diagnostics["orbit_distribution"][orbit] += 1

        weight = item.get("weight", 1.0)
        try:
            weight = float(weight)
        except Exception:
            weight = 1.0

        entry = {
            "root": root,
            "orbit": orbit,
            "raw_orbit": raw_orbit,
            "weight": weight,
            "gloss": item.get("gloss", ""),
            "meta": item.get("meta", {}),
        }

        if root in seen_roots:
            diagnostics["duplicates"] += 1
            # نحتفظ بالأعلى وزناً
            if weight > lex[root]["weight"]:
                lex[root] = entry
        else:
            lex[root] = entry
            seen_roots.add(root)

        diagnostics["entries_valid"] += 1

    diagnostics["roots_unique"] = len(lex)
    diagnostics["loaded"] = True
    diagnostics["error"] = None

    return lex, diagnostics

# =========================================================
# ROOT MATCHING
# =========================================================

def score_root_match(candidate_form, root):
    """
    scoring بسيط لكن أكثر انضباطاً من قبل.
    """
    if candidate_form == root:
        return 1.00

    # احتواء مباشر
    if len(candidate_form) >= 3 and root in candidate_form:
        return 0.78

    # تطابق حرفين من 3 بترتيب
    if len(root) == 3 and len(candidate_form) >= 3:
        matched = 0
        idx = 0
        for ch in candidate_form:
            if idx < len(root) and ch == root[idx]:
                matched += 1
                idx += 1
        if matched == 3:
            return 0.85
        elif matched == 2:
            return 0.62

    # تشابه مجموعة أحرف
    inter = len(set(candidate_form) & set(root))
    union = max(1, len(set(candidate_form) | set(root)))
    j = inter / union
    if j >= 0.75:
        return 0.55
    if j >= 0.5:
        return 0.35

    return 0.0

def match_quranic_root(token, quranic_root_index):
    candidates = generate_root_candidates(token)
    if not candidates:
        return {
            "root": None,
            "confidence": 0.0,
            "orbit": None,
            "source": None,
            "alternatives": [],
            "debug": [],
        }

    source_bonus = {
        "normalized": 0.22,
        "pattern_filter": 0.20,
        "prefix_strip": 0.18,
        "suffix_strip": 0.17,
        "pattern_filter_after_prefix": 0.17,
        "pattern_filter_after_suffix": 0.16,
        "prefix_suffix_strip": 0.14,
        "soft_reduce_doubles": 0.10,
        "sliding_triple": 0.04,
    }

    scored = []

    for cand in candidates:
        cform = cand["form"]
        csource = cand["source"]
        cweight = cand["weight"]

        # exact سريع
        if cform in quranic_root_index:
            meta = quranic_root_index[cform]
            total_score = min(1.0, 0.74 + source_bonus.get(csource, 0.0) + (cweight * 0.06))
            scored.append({
                "root": cform,
                "orbit": meta["orbit"],
                "weight": meta["weight"],
                "source": csource,
                "candidate": cform,
                "score": round(total_score, 4),
                "match_type": "exact_candidate",
            })
            continue

        # فحص على الجذور
        for root, meta in quranic_root_index.items():
            s = score_root_match(cform, root)
            if s > 0:
                total_score = min(1.0, s + source_bonus.get(csource, 0.0) + (cweight * 0.04))
                if csource == "sliding_triple" and total_score > 0.72:
                    total_score = 0.72  # سقف لمنع الوهم
                scored.append({
                    "root": root,
                    "orbit": meta["orbit"],
                    "weight": meta["weight"],
                    "source": csource,
                    "candidate": cform,
                    "score": round(total_score, 4),
                    "match_type": "heuristic",
                })

    if not scored:
        return {
            "root": None,
            "confidence": 0.0,
            "orbit": None,
            "source": None,
            "alternatives": [],
            "debug": candidates[:8],
        }

    # تجميع أعلى score لكل root
    best_per_root = {}
    for x in scored:
        r = x["root"]
        if r not in best_per_root or x["score"] > best_per_root[r]["score"]:
            best_per_root[r] = x

    final = sorted(best_per_root.values(), key=lambda x: (-x["score"], -x["weight"], x["root"]))

    best = final[0]
    alternatives = final[1:4]

    # Ambiguity shield (مرحلة أولى)
    ambiguous = False
    if len(final) > 1:
        if abs(final[0]["score"] - final[1]["score"]) <= 0.06:
            ambiguous = True

    return {
        "root": best["root"],
        "confidence": best["score"],
        "orbit": best["orbit"],
        "source": best["source"],
        "candidate": best["candidate"],
        "match_type": best["match_type"],
        "alternatives": alternatives,
        "ambiguous": ambiguous,
        "debug": candidates[:8],
    }

# =========================================================
# MATRIX RESONANCE
# =========================================================

@st.cache_data(show_spinner=False)
def load_matrix_resonance(quranic_root_index):
    data, err = safe_read_json(MATRIX_PATH)

    diagnostics = {
        "loaded": False,
        "error": err,
        "file_stats": file_stats(MATRIX_PATH),
        "verses_total": 0,
        "verses_indexed": 0,
    }

    if err or data is None:
        return {}, diagnostics

    matrix_idx = defaultdict(list)

    # متوقع: list of verses or dict
    verses = []
    if isinstance(data, list):
        verses = data
    elif isinstance(data, dict):
        # ربما dict من id -> verse data
        for k, v in data.items():
            if isinstance(v, dict):
                vv = dict(v)
                vv["id"] = vv.get("id", k)
                verses.append(vv)
    else:
        diagnostics["error"] = "بنية ملف المصفوفة غير مدعومة."
        return {}, diagnostics

    diagnostics["verses_total"] = len(verses)

    for verse in verses:
        if not isinstance(verse, dict):
            continue

        text = verse.get("text", "") or verse.get("verse", "") or ""
        verse_id = verse.get("id", verse.get("ref", ""))

        if not text:
            continue

        roots_in_verse = set()
        for token in arabic_tokens(text):
            m = match_quranic_root(token, quranic_root_index)
            if m["root"]:
                roots_in_verse.add(m["root"])

        for r in roots_in_verse:
            matrix_idx[r].append({
                "id": verse_id,
                "text": text,
            })

        diagnostics["verses_indexed"] += 1

    diagnostics["loaded"] = True
    diagnostics["error"] = None
    return dict(matrix_idx), diagnostics

# =========================================================
# SCORING
# =========================================================

def normalize_metric(x, max_x=30.0):
    x = max(0.0, float(x))
    return min(1.0, x / max_x)

def calculate_absolute_total(mass, speed, energy):
    # الآن مؤشر سيادي مُطبّع لا جمع خام
    nm = normalize_metric(mass, 30.0)
    ns = normalize_metric(speed, 30.0)
    ne = normalize_metric(energy, 5.0)
    total = (nm * 0.33 + ns * 0.27 + ne * 0.40) * 100
    return round(total, 2)

def contextual_harmony(roots, quranic_root_index):
    if not roots:
        return {
            "score": 0.0,
            "label": "فراغ",
            "dominant_orbit": None,
            "distribution": {},
        }

    orbits = []
    for r in roots:
        if r in quranic_root_index:
            orbits.append(quranic_root_index[r]["orbit"])

    if not orbits:
        return {
            "score": 0.0,
            "label": "منخفض",
            "dominant_orbit": None,
            "distribution": {},
        }

    cnt = Counter(orbits)
    dominant_orbit, dominant_count = cnt.most_common(1)[0]
    total = len(orbits)
    ratio = dominant_count / total

    if ratio >= 0.75:
        label = "وحدة طاقية عالية"
    elif ratio >= 0.50:
        label = "تناغم واضح"
    elif ratio >= 0.34:
        label = "تناغم متوسط"
    else:
        label = "تعدد مداري"

    return {
        "score": round(ratio, 4),
        "label": label,
        "dominant_orbit": dominant_orbit,
        "distribution": dict(cnt),
    }

# =========================================================
# ANALYSIS ENGINE
# =========================================================

def analyze_text(text, quranic_root_index, letters_idx, matrix_idx):
    started = time.time()
    tokens = arabic_tokens(text)

    roots_found = []
    detailed = []
    ambiguity_buffer = []

    for token in tokens:
        m = match_quranic_root(token, quranic_root_index)

        if m["root"]:
            root = m["root"]
            meta = quranic_root_index[root]
            mass, speed = compute_mass_speed(root, letters_idx)
            energy = float(meta.get("weight", 1.0))
            total = calculate_absolute_total(mass, speed, energy)

            verse_hits = matrix_idx.get(root, [])[:3]

            item = {
                "token": token,
                "root": root,
                "orbit": meta["orbit"],
                "confidence": round(m["confidence"], 4),
                "source": m["source"],
                "candidate": m.get("candidate"),
                "match_type": m.get("match_type"),
                "mass": mass,
                "speed": speed,
                "energy": round(energy, 3),
                "absolute_total": total,
                "matrix_hits": verse_hits,
                "alternatives": m.get("alternatives", []),
                "ambiguous": m.get("ambiguous", False),
            }

            roots_found.append(root)
            detailed.append(item)

            if item["ambiguous"]:
                ambiguity_buffer.append({
                    "token": token,
                    "chosen": root,
                    "alternatives": m.get("alternatives", []),
                })
        else:
            detailed.append({
                "token": token,
                "root": None,
                "orbit": None,
                "confidence": 0.0,
                "source": None,
                "candidate": None,
                "match_type": None,
                "mass": 0.0,
                "speed": 0.0,
                "energy": 0.0,
                "absolute_total": 0.0,
                "matrix_hits": [],
                "alternatives": [],
                "ambiguous": False,
            })

    harmony = contextual_harmony(roots_found, quranic_root_index)

    duration = round(time.time() - started, 4)

    analysis = {
        "id": f"A-{int(time.time() * 1000)}",
        "timestamp": now_iso(),
        "input_text": text,
        "tokens": tokens,
        "roots_found": roots_found,
        "roots_unique": list(dict.fromkeys(roots_found)),
        "details": detailed,
        "harmony": harmony,
        "ambiguity_buffer": ambiguity_buffer,
        "duration_sec": duration,
        "summary": {
            "tokens_count": len(tokens),
            "matched_count": len([d for d in detailed if d["root"]]),
            "unique_roots_count": len(set(roots_found)),
            "avg_confidence": round(
                sum(d["confidence"] for d in detailed if d["root"]) / max(1, len([d for d in detailed if d["root"]])),
                4
            ),
        }
    }

    return analysis

# =========================================================
# EXPORT
# =========================================================

def build_export_payload(analysis):
    return {
        "app": APP_TITLE,
        "version": APP_VERSION,
        "generated_at": now_iso(),
        "analysis": analysis,
    }

# =========================================================
# LOAD DATA
# =========================================================

quranic_root_index, lex_diag = load_flat_lexicon()
letters_idx, letters_diag = load_letters_index()
matrix_idx, matrix_diag = load_matrix_resonance(quranic_root_index) if quranic_root_index else ({}, {
    "loaded": False, "error": "تعذر تحميل matrix بسبب غياب lexicon", "file_stats": file_stats(MATRIX_PATH),
    "verses_total": 0, "verses_indexed": 0
})

# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:
    st.markdown(f"## 🜂 {APP_NAME}")
    st.markdown(f"**الإصدار:** v{APP_VERSION}")

    S()["silent_mode"] = st.toggle("وضع الرصد الصامت", value=S()["silent_mode"])

    st.markdown("---")
    st.markdown("### تشخيص الملف الجذري (1800+)")

    if lex_diag["loaded"]:
        if lex_diag["roots_unique"] >= 1800:
            st.markdown('<div class="status-ok">✅ تم تحميل الملف الجذري بنجاح (1800+)</div>', unsafe_allow_html=True)
        else:
            st.markdown(
                f'<div class="status-warn">⚠️ تم التحميل لكن عدد الجذور الفريد أقل من 1800: {lex_diag["roots_unique"]}</div>',
                unsafe_allow_html=True
            )
    else:
        st.markdown(
            f'<div class="status-error">❌ فشل تحميل ملف الجذور: {lex_diag.get("error", "خطأ غير معروف")}</div>',
            unsafe_allow_html=True
        )

    fs = lex_diag["file_stats"]
    st.write(f"**المسار:** `{LEXICON_PATH}`")
    st.write(f"**الحجم:** {fs.get('size_kb', '—')} KB")
    st.write(f"**الأسطر:** {fs.get('lines', '—')}")
    st.write(f"**إجمالي المداخل:** {lex_diag['entries_total']}")
    st.write(f"**المداخل الصالحة:** {lex_diag['entries_valid']}")
    st.write(f"**الجذور الفريدة:** {lex_diag['roots_unique']}")
    st.write(f"**المكررات:** {lex_diag['duplicates']}")
    st.write(f"**مداخل غير صالحة:** {lex_diag['invalid_entries']}")
    st.write(f"**جذور مفقودة:** {lex_diag['missing_root']}")
    st.write(f"**جذور غير عربية:** {lex_diag['non_arabic_roots']}")

    st.markdown("---")
    st.markdown("### قفل المدارات (Orbit Lock)")
    st.write(f"**عدد المدارات الرسمية:** {len(KNOWN_ORBITS)}")
    st.write(f"**وضع صارم:** {'نعم' if STRICT_ORBIT_MODE else 'لا'}")
    st.write(f"**مدارات مجهولة:** {lex_diag['unknown_orbits_count']}")
    st.write(f"**مدارات معاد تعيينها Alias:** {lex_diag['aliased_orbits_count']}")

    if lex_diag["unknown_orbits_count"] > 0:
        st.markdown('<div class="status-warn">⚠️ توجد مدارات غير معروفة داخل ملف الجذور.</div>', unsafe_allow_html=True)
        with st.expander("عرض المدارات المجهولة"):
            for k, v in lex_diag["unknown_orbits"].most_common(20):
                st.write(f"- `{k}` × {v}")

    if lex_diag["aliased_orbits_count"] > 0:
        with st.expander("عرض المدارات التي تم تصحيحها عبر Alias"):
            for k, v in lex_diag["aliased_orbits"].most_common(20):
                mapped = ORBIT_ALIASES.get(k, ORBIT_ALIASES.get(normalize_arabic(k), "?"))
                st.write(f"- `{k}` → `{mapped}` × {v}")

    with st.expander("المدارات الرسمية المعتمدة"):
        st.write(sorted(KNOWN_ORBITS))

    st.markdown("---")
    st.markdown("### تشخيص المصفوفة")
    if matrix_diag["loaded"]:
        st.markdown('<div class="status-ok">✅ تم تحميل وفهرسة المصفوفة</div>', unsafe_allow_html=True)
    else:
        st.markdown(
            f'<div class="status-warn">⚠️ {matrix_diag.get("error", "المصفوفة غير متاحة")}</div>',
            unsafe_allow_html=True
        )

    mfs = matrix_diag["file_stats"]
    st.write(f"**المسار:** `{MATRIX_PATH}`")
    st.write(f"**الحجم:** {mfs.get('size_kb', '—')} KB")
    st.write(f"**الأسطر:** {mfs.get('lines', '—')}")
    st.write(f"**إجمالي الآيات/المداخل:** {matrix_diag.get('verses_total', 0)}")
    st.write(f"**المفهرس فعليًا:** {matrix_diag.get('verses_indexed', 0)}")

    st.markdown("---")
    st.markdown("### سجل آخر التحليلات")
    if S()["history"]:
        for h in S()["history"]:
            st.markdown(f"- **{h['id']}** — {h['summary']['unique_roots_count']} جذور")
    else:
        st.caption("لا يوجد سجل بعد.")

# =========================================================
# MAIN UI
# =========================================================

st.markdown(f'<div class="nibras-title">{APP_TITLE}</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="nibras-sub">نسخة v30 تغلق ثغرة المدارات نهائيًا: لا fallback صامت إلى "وعي"، بل تشخيص صريح وتحكّم سيادي.</div>',
    unsafe_allow_html=True
)

with st.container():
    input_text = st.text_area(
        "أدخل النص للتحليل الجذري السيادي",
        height=140,
        placeholder="اكتب آية، عبارة، أو مقطعًا عربيًا...",
    )

    c1, c2, c3 = st.columns([1,1,1])
    with c1:
        run_btn = st.button("🜂 تحليل سيادي", use_container_width=True)
    with c2:
        clear_compare_btn = st.button("مسح المقارنة", use_container_width=True)
    with c3:
        clear_history_btn = st.button("مسح السجل", use_container_width=True)

    if clear_compare_btn:
        S()["compare"] = []
        st.success("تم مسح المقارنة.")

    if clear_history_btn:
        S()["history"] = []
        st.success("تم مسح السجل.")

# =========================================================
# RUN ANALYSIS
# =========================================================

if run_btn:
    if not input_text.strip():
        st.markdown('<div class="status-warn">⚠️ الرجاء إدخال نص أولاً.</div>', unsafe_allow_html=True)
    elif not quranic_root_index:
        st.markdown('<div class="status-error">❌ لا يمكن التحليل لأن ملف الجذور غير محمّل.</div>', unsafe_allow_html=True)
    else:
        analysis = analyze_text(input_text, quranic_root_index, letters_idx, matrix_idx)
        S()["last_analysis"] = analysis
        S()["ambiguity_buffer"] = analysis["ambiguity_buffer"]
        push_history(analysis)
        add_compare(analysis)

# =========================================================
# RENDER LAST ANALYSIS
# =========================================================

analysis = S()["last_analysis"]

if analysis:
    st.markdown("---")
    st.subheader("النتيجة السيادية")

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("عدد الكلمات", analysis["summary"]["tokens_count"])
    with m2:
        st.metric("عدد المطابقات", analysis["summary"]["matched_count"])
    with m3:
        st.metric("الجذور الفريدة", analysis["summary"]["unique_roots_count"])
    with m4:
        st.metric("متوسط الثقة", analysis["summary"]["avg_confidence"])

    harmony = analysis["harmony"]

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### محرك التناغم السياقي")
    st.write(f"**التقييم:** {harmony['label']}")
    st.write(f"**درجة التناغم:** {round(harmony['score'] * 100, 2)}%")
    if harmony["dominant_orbit"]:
        st.write(f"**المدار الغالب:** `{harmony['dominant_orbit']}`")
    if harmony["distribution"]:
        st.write("**توزيع المدارات:**")
        for orb, cnt in harmony["distribution"].items():
            css = "orbit-chip"
            if orb == UNKNOWN_ORBIT_LABEL:
                css += " unknown-orbit"
            st.markdown(f'<span class="{css}">{orb} × {cnt}</span>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if analysis["summary"]["matched_count"] == 0:
        st.markdown('<div class="status-warn">⚠️ لم يتم العثور على جذور مطابقة.</div>', unsafe_allow_html=True)

    st.markdown("### الجذور المستنبطة")
    if analysis["roots_unique"]:
        for r in analysis["roots_unique"]:
            meta = quranic_root_index.get(r, {})
            orb = meta.get("orbit", UNKNOWN_ORBIT_LABEL)
            css = "root-chip"
            st.markdown(f'<span class="{css}">{r} ← {orb}</span>', unsafe_allow_html=True)
    else:
        st.caption("لا توجد جذور مستنبطة.")

    st.markdown("---")
    st.markdown("### تفصيل الكلمات")

    for d in analysis["details"]:
        st.markdown('<div class="card">', unsafe_allow_html=True)

        c1, c2 = st.columns([2,1])
        with c1:
            st.write(f"**الكلمة:** `{d['token']}`")
            if d["root"]:
                st.write(f"**الجذر:** `{d['root']}`")
                st.write(f"**المدار:** `{d['orbit']}`")
                st.write(f"**المصدر:** `{d['source']}` | **النوع:** `{d['match_type']}`")
            else:
                st.write("**الجذر:** —")

        with c2:
            st.metric("الثقة", d["confidence"])
            st.metric("Absolute Total", d["absolute_total"])

        if d["root"]:
            cc1, cc2, cc3 = st.columns(3)
            with cc1:
                st.metric("Mass", d["mass"])
            with cc2:
                st.metric("Speed", d["speed"])
            with cc3:
                st.metric("Energy", d["energy"])

            if d["ambiguous"]:
                st.markdown(
                    '<div class="status-warn">⚠️ تنبيه سيادي: هذه الكلمة تحمل احتمالات متقاربة. راجع البدائل.</div>',
                    unsafe_allow_html=True
                )

            if d["alternatives"]:
                with st.expander("بدائل محتملة"):
                    for alt in d["alternatives"]:
                        st.write(
                            f"- `{alt['root']}` | مدار: `{alt['orbit']}` | score: `{alt['score']}` | source: `{alt['source']}`"
                        )

            if d["matrix_hits"]:
                with st.expander("رنين المصفوفة (أمثلة آيات)"):
                    for hit in d["matrix_hits"]:
                        st.write(f"**{hit['id']}** — {hit['text']}")

        st.markdown('</div>', unsafe_allow_html=True)

    # Ambiguity buffer summary
    if analysis["ambiguity_buffer"]:
        st.markdown("---")
        st.markdown("### نظام التحصين من الالتباس — المرحلة الأولى")
        st.markdown(
            '<div class="status-warn">⚠️ توجد كلمات ذات جذور متقاربة. النسخة v30 تعرضها، وv31 يمكن أن يحوّلها إلى اختيار يدوي تفاعلي.</div>',
            unsafe_allow_html=True
        )
        for amb in analysis["ambiguity_buffer"]:
            st.write(f"- الكلمة: `{amb['token']}` | المختار حاليًا: `{amb['chosen']}`")

    # Export
    st.markdown("---")
    st.markdown("### التصدير السيادي")
    export_payload = build_export_payload(analysis)
    export_json = json.dumps(export_payload, ensure_ascii=False, indent=2)

    st.download_button(
        label="تحميل JSON السيادي",
        data=export_json.encode("utf-8"),
        file_name=f"nibras_v{APP_VERSION}_{analysis['id']}.json",
        mime="application/json",
        use_container_width=True
    )

# =========================================================
# COMPARE PANEL
# =========================================================

if S()["compare"]:
    st.markdown("---")
    st.subheader("مقارنة آخر المسارات")

    cols = st.columns(min(MAX_COMPARE, len(S()["compare"])))
    for i, item in enumerate(S()["compare"][:MAX_COMPARE]):
        with cols[i]:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.write(f"**{item['id']}**")
            st.write(f"جذور فريدة: {item['summary']['unique_roots_count']}")
            st.write(f"متوسط الثقة: {item['summary']['avg_confidence']}")
            st.write(f"تناغم: {item['harmony']['label']}")
            st.markdown('</div>', unsafe_allow_html=True)
