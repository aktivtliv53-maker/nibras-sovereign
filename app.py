# -*- coding: utf-8 -*-
# =========================================================
# NIBRAS SOVEREIGN v27.0 — THE 1800 ROOTS AWAKENING
# =========================================================
# نسخة سيادية مغلقة معماريًا لتحليل النصوص عبر:
# - محرك جذور (1800 جذر مباشر من nibras_lexicon.json)
# - مستشار قرار | درع الالتباس | تناغم سياقي
# - ذاكرة موضعية | تصدير موثق | الربط بالمصفوفة الكلية
# - نظام الأنعام مع Memory Pruning
# - الميزان الثلاثي (الكتلة + السرعة + الطاقة) بدون عشوائية
# المرجع: وثيقة العرش - محمد (CPU: As-Sajdah 5)
# =========================================================

import streamlit as st
import json
import re
import math
import time
import hashlib
import io
import os
from datetime import datetime
from collections import Counter, defaultdict
from pathlib import Path

# =========================================================
# 0) FORCE CACHE CLEAR (كسر جمود الرصد)
# =========================================================
st.cache_data.clear()
st.cache_resource.clear()

# =========================================================
# 1) PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Nibras Sovereign v27.0 — 1800 ROOTS AWAKENING",
    page_icon="🧿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# 2) GLOBAL STYLE
# =========================================================
GLOBAL_CSS = """
<style>
:root {
    --bg-main: #070b14;
    --bg-card: rgba(18, 26, 42, 0.82);
    --bg-soft: rgba(25, 35, 55, 0.55);
    --text-main: #f4f8ff;
    --text-soft: #b8c7e6;
    --accent: #7dd3fc;
    --accent-2: #a78bfa;
    --good: #34d399;
    --warn: #fbbf24;
    --bad: #f87171;
    --line: rgba(125, 211, 252, 0.18);
    --glow: 0 0 24px rgba(125, 211, 252, 0.12);
}

html, body, [data-testid="stAppViewContainer"] {
    background:
      radial-gradient(circle at 20% 20%, rgba(125,211,252,0.06), transparent 28%),
      radial-gradient(circle at 80% 10%, rgba(167,139,250,0.05), transparent 30%),
      linear-gradient(180deg, #05070d 0%, #0b1120 100%);
    color: var(--text-main);
}

[data-testid="stHeader"] { background: rgba(0,0,0,0); }
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(9,14,24,0.98), rgba(12,18,30,0.98));
    border-right: 1px solid rgba(125,211,252,0.08);
}

.block-container {
    padding-top: 1.2rem;
    padding-bottom: 2rem;
}

.sov-card {
    background: var(--bg-card);
    border: 1px solid var(--line);
    border-radius: 18px;
    padding: 1rem 1rem;
    box-shadow: var(--glow);
    backdrop-filter: blur(10px);
    margin-bottom: 1rem;
}

.sov-big {
    font-size: 1.45rem;
    font-weight: 800;
}

.sov-good { color: var(--good); }
.sov-warn { color: var(--warn); }
.sov-bad  { color: var(--bad); }

.comparison-card {
    background: #161616; padding: 15px; border-radius: 15px;
    border: 1px solid #262626; margin-bottom: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);
}
.mentor-box {
    background: #001f24; border-right: 5px solid #00afcc;
    padding: 20px; border-radius: 12px; margin-top: 20px;
}
.detail-box {
    background: #111; padding: 12px; border-radius: 10px; margin-bottom: 8px; border: 1px solid #222;
}
.status-warn {
    background: #2a1f0f; border: 1px solid #a67c00; padding: 10px; border-radius: 10px; margin: 8px 0;
}
.an3am-expander {
    background: rgba(18, 26, 42, 0.6);
    border-radius: 12px;
    margin-bottom: 8px;
}
</style>
"""
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# =========================================================
# 3) CONSTANTS & RULES
# =========================================================
APP_VERSION = "27.0 1800 ROOTS AWAKENING"

NORMALIZATION_POLICY = {
    "strip_diacritics": True,
    "normalize_hamza": True,
    "convert_alef_maqsura": True,
    "convert_ta_marbuta": True
}

PREFIXES = ["وال", "فال", "بال", "كال", "لل", "ال", "و", "ف", "ب", "ك", "ل", "س"]
SUFFIXES = ["كما", "كم", "كن", "هم", "هن", "نا", "ها", "ه", "ية", "ات", "ون", "ين", "ان", "ة", "ي", "ك", "ت", "ا", "ن"]

CONFIDENCE_LABELS = [
    (0.90, "حاسم"),
    (0.75, "راجح قوي"),
    (0.60, "راجح"),
    (0.40, "استكشافي"),
    (0.00, "ضعيف"),
]

# =========================================================
# 4) ROOT REGISTRY (Extended)
# =========================================================
ROOT_REGISTRY = {
    "رحم": {"family": "mercy", "domain": "divine_softness", "rank": "central", "tags": ["رحمة", "لطف"]},
    "نور": {"family": "light", "domain": "guidance", "rank": "central", "tags": ["نور", "هداية"]},
    "علم": {"family": "knowledge", "domain": "cognition", "rank": "central", "tags": ["علم", "فهم"]},
    "هدي": {"family": "guidance", "domain": "direction", "rank": "central", "tags": ["هداية"]},
    "ذكر": {"family": "remembrance", "domain": "presence", "rank": "high", "tags": ["ذكر"]},
    "امن": {"family": "safety", "domain": "stability", "rank": "high", "tags": ["أمن"]},
    "قلب": {"family": "inner_core", "domain": "inner_perception", "rank": "high", "tags": ["قلب"]},
    "صبر": {"family": "fortitude", "domain": "endurance", "rank": "high", "tags": ["صبر"]},
}

# =========================================================
# 5) SESSION STATE INIT
# =========================================================
def init_sovereign_state():
    if "sovereign_monolith" not in st.session_state:
        st.session_state.sovereign_monolith = {
            "active": False,
            "mode": "sovereign",
            "current_text": "",
            "current_record": None,
            "analysis_history": [],
            "visible_history_limit": 5,
            "pending_ambiguities": [],
            "resolved_ambiguities": {},
            "metrics": {},
            "ui": {
                "silent_mode": False,
                "animate": True,
                "show_ritual": True,
                "show_advisor_trace": False,
                "show_debug": False,
                "show_ambiguity_warnings": True
            },
            "version": APP_VERSION
        }
    if "session_history" not in st.session_state:
        st.session_state.session_history = []
    if "ambiguity_choices" not in st.session_state:
        st.session_state.ambiguity_choices = {}

init_sovereign_state()

def S():
    return st.session_state.sovereign_monolith

# =========================================================
# 6) UTILITIES
# =========================================================
def now_iso():
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

def analysis_id():
    return "analysis_" + datetime.utcnow().strftime("%Y%m%d_%H%M%S")

def confidence_label(score: float):
    for th, label in CONFIDENCE_LABELS:
        if score >= th:
            return label
    return "ضعيف"

def clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))

def sha256_text(text: str):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def arabic_word_tokenize(text: str):
    return re.findall(r"[\u0621-\u064A\u0660-\u0669]+", text)

def get_file_size_mb(path):
    """إرجاع حجم الملف بالميجابايت"""
    try:
        if path and os.path.exists(path):
            return round(os.path.getsize(path) / (1024 * 1024), 2)
    except:
        pass
    return 0.0

# =========================================================
# 7) NORMALIZATION ENGINE
# =========================================================
ARABIC_DIACRITICS = re.compile(r"[\u0617-\u061A\u064B-\u0652\u0670\u0640]")

def normalize_arabic(text: str, policy=None):
    if policy is None:
        policy = NORMALIZATION_POLICY

    t = str(text or "").strip()

    if policy.get("strip_diacritics", True):
        t = ARABIC_DIACRITICS.sub("", t)

    if policy.get("normalize_hamza", True):
        t = re.sub(r"[أإآٱ]", "ا", t)
        t = t.replace("ؤ", "و").replace("ئ", "ي")

    if policy.get("convert_alef_maqsura", True):
        t = t.replace("ى", "ي")

    if policy.get("convert_ta_marbuta", True):
        t = t.replace("ة", "ه")

    t = re.sub(r"[^\u0621-\u064A0-9\s]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t

# =========================================================
# 8) ROOT CANDIDATE ENGINE
# =========================================================
def strip_prefixes(word):
    out = set()
    for p in PREFIXES:
        if word.startswith(p) and len(word) - len(p) >= 2:
            out.add(word[len(p):])
    return out

def strip_suffixes(word):
    out = set()
    for s in SUFFIXES:
        if word.endswith(s) and len(word) - len(s) >= 2:
            out.add(word[:-len(s)])
    return out

def reduce_doubles(word):
    if len(word) < 2:
        return word
    out = [word[0]]
    for ch in word[1:]:
        if ch != out[-1]:
            out.append(ch)
    reduced = "".join(out)
    return reduced if len(reduced) >= 2 else word

def sliding_triples(word):
    triples = set()
    if len(word) >= 3:
        for i in range(len(word) - 2):
            triples.add(word[i:i+3])
    return triples

def generate_root_candidates(word: str):
    w = normalize_arabic(word)
    if not w:
        return []

    candidates = []
    seen = set()

    def add(form, source, weight):
        form = normalize_arabic(form)
        if not form or len(form) < 2:
            return
        key = (form, source)
        if key in seen:
            return
        seen.add(key)
        candidates.append({
            "form": form,
            "source": source,
            "weight": float(weight)
        })

    add(w, "normalized", 1.00)

    p_stripped = strip_prefixes(w)
    for f in p_stripped:
        add(f, "prefix_strip", 0.92)

    s_stripped = strip_suffixes(w)
    for f in s_stripped:
        add(f, "suffix_strip", 0.90)

    both = set()
    for p in p_stripped:
        both.update(strip_suffixes(p))
    for s in s_stripped:
        both.update(strip_prefixes(s))
    for f in both:
        add(f, "prefix_suffix_strip", 0.88)

    for item in list(candidates):
        red = reduce_doubles(item["form"])
        if red != item["form"]:
            add(red, "double_reduce", item["weight"] * 0.86)

    for item in list(candidates):
        if 3 <= len(item["form"]) <= 6:
            for tri in sliding_triples(item["form"]):
                add(tri, "sliding_triple", item["weight"] * 0.78)

    candidates = sorted(
        candidates,
        key=lambda x: (-x["weight"], -len(x["form"]), x["form"])
    )
    return candidates

# =========================================================
# 9) DATA LOADING (FLAT LIST - 1800 ROOTS DIRECT)
# =========================================================
def safe_load_json_file(filename):
    search_paths = [Path("."), Path("./data"), Path("./qroot")]
    for folder in search_paths:
        file_path = folder / filename
        if file_path.exists():
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    return json.load(f), str(file_path)
            except Exception as e:
                st.error(f"خطأ في قراءة {filename}: {e}")
    return None, None

# تحميل ملف الحروف
letters_raw, path_l = safe_load_json_file("sovereign_letters_v1.json")

# =========================================================
# 10) BUILD LETTERS INDEX
# =========================================================
letters_idx = {}
if isinstance(letters_raw, list):
    for item in letters_raw:
        char = item.get("letter")
        if char:
            letters_idx[normalize_arabic(char)] = item

# =========================================================
# 11) LOAD FLAT LEXICON (1800 ROOTS - NO CACHE BLOCK)
# =========================================================
@st.cache_data(ttl=0, show_spinner=False)  # ttl=0 لمنع التخزين المؤقت الطويل
def load_flat_lexicon():
    """تحميل المعجم المسطح (Flat List) مباشرة بدون فلترة"""
    lexicon_raw, path_x = safe_load_json_file("nibras_lexicon.json")
    
    root_index = defaultdict(list)
    roots_list = []
    
    if isinstance(lexicon_raw, list):
        for item in lexicon_raw:
            if isinstance(item, dict):
                # استخراج الجذر مباشرة
                root = item.get("root") or item.get("name") or item.get("lemma") or ""
                root = normalize_arabic(str(root).strip())
                
                if not root or len(root) < 2:
                    continue
                
                # استخراج الوزن (frequency أو weight)
                weight = item.get("frequency") or item.get("weight") or 1.0
                try:
                    weight = float(weight)
                except:
                    weight = 1.0
                
                # المدار (إذا لم يوجد، نستخدم مدار افتراضي حسب طاقة الحروف)
                orbit = item.get("orbit") or item.get("orbit_hint") or "وعي"
                if orbit not in ["سيادة", "فطرة", "تمكين", "يسر", "وعي", "هداية", "تزكية", "أزل"]:
                    # توزيع تلقائي حسب أول حرف في الجذر
                    first_char = root[0] if root else ""
                    if first_char in ["ا", "ع", "ق", "ه", "و", "ل"]:
                        orbit = "سيادة"
                    elif first_char in ["ر", "ح", "م", "ن"]:
                        orbit = "فطرة"
                    elif first_char in ["ف", "ت", "ك", "س"]:
                        orbit = "تمكين"
                    elif first_char in ["ي", "ب", "د"]:
                        orbit = "يسر"
                    else:
                        orbit = "وعي"
                
                # البصيرة
                insight = item.get("insight") or item.get("description") or f"الجذر {root} يحمل طاقة مدار {orbit}"
                
                entry = {
                    "root": root,
                    "weight": weight,
                    "orbit": orbit,
                    "insight": insight
                }
                
                root_index[root].append(entry)
                roots_list.append(root)
    
    # إحصاءات
    total_roots = len(root_index)
    total_entries = sum(len(v) for v in root_index.values())
    
    return dict(root_index), roots_list, total_roots, total_entries, path_x

# تحميل المعجم المسطح
quranic_root_index, roots_list, total_roots, total_entries, path_x = load_flat_lexicon()

# =========================================================
# 12) LOAD MATRIX RESONANCE
# =========================================================
@st.cache_data(ttl=0, show_spinner=False)
def load_matrix_resonance():
    """تحميل مصفوفة الرنين القرآني"""
    matrix_idx = defaultdict(list)
    matrix_path = None
    total_verses = 0
    indexed_verses = 0
    
    for path in [Path("."), Path("./data"), Path("./qroot")]:
        m_path = path / "matrix_data.json"
        if m_path.exists():
            matrix_path = str(m_path)
            try:
                with open(m_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                if isinstance(data, list):
                    total_verses = len(data)
                    
                    for entry in data:
                        verse_text = entry.get('text', '')
                        if not verse_text:
                            continue
                        
                        if len(verse_text) > 150:
                            verse_text = verse_text[:150] + "..."
                        
                        # استخراج الجذور المحتملة من النص
                        words = arabic_word_tokenize(verse_text)
                        roots_in_verse = set()
                        
                        for word in words:
                            norm_word = normalize_arabic(word)
                            if len(norm_word) >= 2:
                                if norm_word in quranic_root_index:
                                    roots_in_verse.add(norm_word)
                                else:
                                    for root_cand in generate_root_candidates(norm_word):
                                        if root_cand["form"] in quranic_root_index:
                                            roots_in_verse.add(root_cand["form"])
                        
                        for root in roots_in_verse:
                            if len(matrix_idx[root]) < 5:
                                matrix_idx[root].append({
                                    "surah": entry.get('surah', entry.get('surah_name', '?')),
                                    "verse": entry.get('verse', entry.get('verse_number', '?')),
                                    "text": verse_text
                                })
                                indexed_verses += 1
                    
                    for root in matrix_idx:
                        matrix_idx[root] = sorted(matrix_idx[root], key=lambda x: x.get('surah', ''))
                        
            except Exception as e:
                st.error(f"خطأ في تحميل المصفوفة: {e}")
                return {}, None, 0, 0
            break
    
    return matrix_idx, matrix_path, total_verses, indexed_verses

matrix_idx, matrix_path, total_verses, indexed_verses = load_matrix_resonance()

# =========================================================
# 13) ROOT LOOKUP HELPERS
# =========================================================
def get_root_meta(root):
    r = normalize_arabic(root)
    if r in ROOT_REGISTRY:
        return ROOT_REGISTRY[r]
    return {
        "family": "unknown",
        "domain": "unknown",
        "rank": "normal",
        "tags": []
    }

def lookup_root_candidates(form: str):
    f = normalize_arabic(form)
    found = set()

    if isinstance(quranic_root_index, dict):
        if f in quranic_root_index:
            found.add(f)

    return sorted(x for x in found if x)

def match_quranic_root(word: str):
    candidates = generate_root_candidates(word)
    scored_hits = []

    source_bonus = {
        "normalized": 0.22,
        "prefix_strip": 0.18,
        "suffix_strip": 0.16,
        "prefix_suffix_strip": 0.14,
        "double_reduce": 0.08,
        "sliding_triple": 0.04
    }

    for c in candidates:
        roots = lookup_root_candidates(c["form"])
        if not roots:
            continue

        for root in roots:
            exact_bonus = 0.12 if normalize_arabic(c["form"]) == normalize_arabic(root) else 0.0
            len_bonus = 0.08 if len(c["form"]) == 3 else 0.0
            score = clamp(c["weight"] + source_bonus.get(c["source"], 0.0) + exact_bonus + len_bonus)
            scored_hits.append({
                "root": normalize_arabic(root),
                "score": score,
                "candidate_form": c["form"],
                "source": c["source"],
                "weight": c["weight"]
            })

    if not scored_hits:
        return {
            "root": None,
            "confidence": 0.0,
            "confidence_label": "غير مطابق",
            "method": "no_match",
            "alternatives": [],
            "ambiguous": False,
            "requires_human": False,
            "trace": candidates,
            "advisor_note": "لم يتم العثور على جذر مطابق ضمن الجذور الـ 1800."
        }

    best_by_root = {}
    for hit in scored_hits:
        r = hit["root"]
        if r not in best_by_root or hit["score"] > best_by_root[r]["score"]:
            best_by_root[r] = hit

    ranked = sorted(best_by_root.values(), key=lambda x: (-x["score"], x["root"]))
    best = ranked[0]
    alternatives = [x["root"] for x in ranked[1:4]]

    ambiguous = False
    requires_human = False

    if len(ranked) > 1:
        gap = best["score"] - ranked[1]["score"]
        if gap <= 0.06:
            ambiguous = True
            requires_human = True
        elif gap <= 0.12:
            ambiguous = True
            requires_human = False

    note = f"تمت المطابقة عبر {best['source']} باستخدام الشكل '{best['candidate_form']}'."
    if ambiguous:
        note += " توجد احتمالات قريبة تستحق الانتباه."

    return {
        "root": best["root"],
        "confidence": round(best["score"], 4),
        "confidence_label": confidence_label(best["score"]),
        "method": best["source"],
        "alternatives": alternatives,
        "ambiguous": ambiguous,
        "requires_human": requires_human,
        "trace": candidates,
        "advisor_note": note
    }

# =========================================================
# 14) AMBIGUITY SHIELD
# =========================================================
def ambiguity_shield(token_index, word, match_result):
    if not match_result["root"]:
        return {
            "ambiguous": False,
            "mode": "auto",
            "candidates": [],
            "message": ""
        }

    if not match_result["ambiguous"]:
        return {
            "ambiguous": False,
            "mode": "auto",
            "candidates": [{"root": match_result["root"], "confidence": match_result["confidence"]}],
            "message": "مطابقة مستقرة."
        }

    candidates = [{"root": match_result["root"], "confidence": match_result["confidence"]}]
    for alt in match_result["alternatives"]:
        candidates.append({"root": alt, "confidence": round(max(0.0, match_result["confidence"] - 0.04), 4)})

    mode = "human" if match_result["requires_human"] else "warning"
    message = (
        "الكلمة تحتمل أكثر من جذر، يُستحسن تدخل بشري."
        if mode == "human"
        else "يوجد تقارب بين جذور محتملة، لكن النظام رجّح أحدها."
    )

    return {
        "ambiguous": True,
        "mode": mode,
        "candidates": candidates,
        "message": message
    }

def token_key(token_index, word):
    return f"token_{token_index}_{normalize_arabic(word)}"

# =========================================================
# 15) CONTEXTUAL HARMONY ENGINE
# =========================================================
def contextual_harmony(tokens):
    matched_roots = [t["match"]["root"] for t in tokens if t["match"]["root"]]
    if not matched_roots:
        return {
            "score": 0.0,
            "label": "لا تناغم مرصود",
            "medal": "⚪",
            "dominant_families": [],
            "repeated_roots": [],
            "cluster_strength": 0.0,
            "centrality_bonus": 0.0
        }

    root_counts = Counter(matched_roots)
    repeated_roots = [r for r, c in root_counts.items() if c > 1]

    families = []
    domains = []
    central_bonus = 0.0

    for r in matched_roots:
        meta = get_root_meta(r)
        fam = meta.get("family", "unknown")
        dom = meta.get("domain", "unknown")
        rank = meta.get("rank", "normal")
        families.append(fam)
        domains.append(dom)
        if rank == "central":
            central_bonus += 0.02
        elif rank == "high":
            central_bonus += 0.01

    fam_counts = Counter(families)
    dom_counts = Counter(domains)

    dominant_families = [f for f, c in fam_counts.items() if c >= 2 and f != "unknown"]

    total = len(matched_roots)
    root_repeat_ratio = sum(c for c in root_counts.values() if c > 1) / total
    family_concentration = max(fam_counts.values()) / total if fam_counts else 0.0
    domain_concentration = max(dom_counts.values()) / total if dom_counts else 0.0

    cluster_strength = clamp((family_concentration * 0.45) + (domain_concentration * 0.35) + (root_repeat_ratio * 0.20))
    centrality_bonus = clamp(central_bonus, 0.0, 0.12)

    score = clamp(cluster_strength + centrality_bonus)

    if score >= 0.85:
        label, medal = "تناغم سيادي عالٍ", "🟢"
    elif score >= 0.70:
        label, medal = "تناغم راجح", "🟢"
    elif score >= 0.50:
        label, medal = "تناغم متوسط", "🟡"
    elif score > 0:
        label, medal = "تناغم ضعيف", "🟠"
    else:
        label, medal = "لا تناغم مرصود", "⚪"

    return {
        "score": round(score, 4),
        "label": label,
        "medal": medal,
        "dominant_families": dominant_families,
        "repeated_roots": repeated_roots,
        "cluster_strength": round(cluster_strength, 4),
        "centrality_bonus": round(centrality_bonus, 4)
    }

def contextual_harmony_engine(matched_roots):
    if not matched_roots:
        return {
            "harmony_score": 0,
            "harmony_label": "لا يوجد تناغم",
            "dominant_family": None,
            "family_counter": {}
        }

    orbit_counts = Counter([m["orbit"] for m in matched_roots])
    root_counts = Counter([m["root"] for m in matched_roots])

    total = len(matched_roots)
    top_orbit, top_orbit_count = orbit_counts.most_common(1)[0]
    top_root, top_root_count = root_counts.most_common(1)[0]

    orbit_ratio = top_orbit_count / total
    root_ratio = top_root_count / total

    harmony_score = round((orbit_ratio * 0.7 + root_ratio * 0.3) * 100, 2)

    if harmony_score >= 80:
        label = "وسام التناغم المطلق"
    elif harmony_score >= 60:
        label = "وحدة طاقية عالية"
    elif harmony_score >= 40:
        label = "تناغم متوسط"
    else:
        label = "تناثر دلالي"

    return {
        "harmony_score": harmony_score,
        "harmony_label": label,
        "dominant_family": top_orbit,
        "family_counter": dict(orbit_counts)
    }

# =========================================================
# 16) RITUAL / REPRESENTATIONAL LAYER
# =========================================================
GENE_MAP = {
    "ا": "alpha", "ب": "beta", "ت": "theta", "ث": "theta",
    "ج": "gamma", "ح": "eta", "خ": "kappa", "د": "delta",
    "ذ": "delta", "ر": "rho", "ز": "zeta", "س": "sigma",
    "ش": "sigma", "ص": "sigma+", "ض": "sigma+", "ط": "tau",
    "ظ": "tau+", "ع": "ayn", "غ": "ghayn", "ف": "phi",
    "ق": "qaf", "ك": "kappa2", "ل": "lambda", "م": "mu",
    "ن": "nu", "ه": "eta2", "و": "omega", "ي": "iota"
}

def ritual_layer(tokens):
    all_text = "".join([t["normalized"] for t in tokens])
    gene_counts = Counter(GENE_MAP.get(ch, "void") for ch in all_text if ch.strip())

    total_chars = max(1, sum(gene_counts.values()))
    dominant_gene_ratio = max(gene_counts.values()) / total_chars if gene_counts else 0.0

    matched_ratio = sum(1 for t in tokens if t["match"]["root"]) / max(1, len(tokens))
    resonance_score = clamp((dominant_gene_ratio * 0.35) + (matched_ratio * 0.65))

    left = sum(v for i, v in enumerate(gene_counts.values()) if i % 2 == 0)
    right = sum(v for i, v in enumerate(gene_counts.values()) if i % 2 == 1)
    balance_score = clamp(1 - abs(left - right) / max(1, left + right))

    return {
        "gene_counts": dict(gene_counts),
        "resonance_score": round(resonance_score, 4),
        "balance_score": round(balance_score, 4)
    }

# =========================================================
# 17) FINAL VERDICT ENGINE
# =========================================================
def final_verdict(summary, harmony, ritual, human_interventions=0):
    matched_count = summary["matched_count"]
    total = summary["matched_count"] + summary["unmatched_count"]
    matched_ratio = matched_count / max(1, total)
    avg_conf = summary["avg_confidence"]
    ambiguous_count = summary["ambiguous_count"]

    overall = clamp(
        (avg_conf * 0.45) +
        (matched_ratio * 0.25) +
        (harmony["score"] * 0.20) +
        (ritual["resonance_score"] * 0.10)
    )

    coherence = clamp(
        (harmony["score"] * 0.60) +
        (summary["strong_matches"] / max(1, total) * 0.40)
    )

    review_penalty = (ambiguous_count * 0.03) + (0.02 if human_interventions > 0 else 0.0)
    overall = clamp(overall - review_penalty)

    requires_review = ambiguous_count > 0 or overall < 0.75
    review_items = ambiguous_count

    if overall >= 0.88 and coherence >= 0.80 and ambiguous_count == 0:
        status = "قابل للاعتماد بثقة عالية"
    elif overall >= 0.78:
        status = "قابل للاعتماد البحثي"
    elif overall >= 0.65:
        status = "راجح مع مراجعة محدودة"
    elif overall >= 0.45:
        status = "استكشافي فقط"
    else:
        status = "غير كافٍ للاعتماد"

    statement = (
        f"التحليل بلغ درجة {status} "
        f"بثقة كلية {overall:.2f} وتماسك سياقي {coherence:.2f}. "
        f"عدد مواضع الالتباس: {ambiguous_count}."
    )

    return {
        "overall_confidence": round(overall, 4),
        "coherence_score": round(coherence, 4),
        "requires_review": requires_review,
        "review_items": review_items,
        "human_interventions": human_interventions,
        "status": status,
        "statement": statement
    }

# =========================================================
# 18) ANALYSIS PIPELINE
# =========================================================
def analyze_text(text: str):
    original_text = str(text or "").strip()
    normalized_text = normalize_arabic(original_text)
    words = arabic_word_tokenize(normalized_text)

    tokens = []
    human_interventions = 0

    for idx, w in enumerate(words):
        m = match_quranic_root(w)
        shield = ambiguity_shield(idx, w, m)

        t_key = token_key(idx, w)
        resolved = S()["resolved_ambiguities"].get(t_key)

        final_root = m["root"]
        if resolved and resolved.get("chosen_root"):
            final_root = normalize_arabic(resolved["chosen_root"])
            human_interventions += 1

        token_record = {
            "index": idx,
            "word": w,
            "normalized": normalize_arabic(w),
            "candidates": [c["form"] for c in generate_root_candidates(w)],
            "match": {
                "root": final_root,
                "confidence": m["confidence"],
                "confidence_label": m["confidence_label"],
                "method": m["method"],
                "alternatives": m["alternatives"],
                "ambiguous": m["ambiguous"],
                "requires_human": m["requires_human"]
            },
            "shield": shield,
            "root_meta": get_root_meta(final_root) if final_root else {
                "family": "unknown", "domain": "unknown", "rank": "normal", "tags": []
            },
            "advisor_note": m["advisor_note"]
        }
        tokens.append(token_record)

    matched = [t for t in tokens if t["match"]["root"]]
    unmatched = [t for t in tokens if not t["match"]["root"]]
    strong_matches = [t for t in matched if t["match"]["confidence"] >= 0.75]
    ambiguous = [t for t in tokens if t["match"]["ambiguous"]]

    avg_conf = sum(t["match"]["confidence"] for t in matched) / max(1, len(matched))

    summary = {
        "matched_count": len(matched),
        "unmatched_count": len(unmatched),
        "avg_confidence": round(avg_conf, 4),
        "strong_matches": len(strong_matches),
        "ambiguous_count": len(ambiguous)
    }

    harmony = contextual_harmony(tokens)
    ritual = ritual_layer(tokens)
    verdict = final_verdict(summary, harmony, ritual, human_interventions=human_interventions)

    record = {
        "id": analysis_id(),
        "timestamp": now_iso(),
        "version": APP_VERSION,
        "mode": S()["mode"],
        "input": {
            "original_text": original_text,
            "normalized_text": normalized_text,
            "word_count": len(words)
        },
        "tokens": tokens,
        "summary": summary,
        "harmony": harmony,
        "ritual": ritual,
        "final_verdict": verdict
    }

    fp_material = json.dumps({
        "text": original_text,
        "roots": [t["match"]["root"] for t in tokens if t["match"]["root"]],
        "avg_conf": summary["avg_confidence"],
        "verdict": verdict["status"],
        "version": APP_VERSION
    }, ensure_ascii=False, sort_keys=True)

    record["fingerprint"] = sha256_text(fp_material)
    return record

# =========================================================
# 19) MEMORY LEDGER
# =========================================================
def push_history(record):
    preview = record["input"]["original_text"][:60]
    item = {
        "id": record["id"],
        "timestamp": record["timestamp"],
        "preview": preview + ("..." if len(record["input"]["original_text"]) > 60 else ""),
        "avg_confidence": record["summary"]["avg_confidence"],
        "harmony": record["harmony"]["score"],
        "status": record["final_verdict"]["status"],
        "fingerprint": record["fingerprint"],
        "record": record
    }

    history = S()["analysis_history"]
    history.insert(0, item)
    S()["analysis_history"] = history[:20]

def set_current_record(record):
    S()["current_record"] = record
    S()["active"] = True
    S()["current_text"] = record["input"]["original_text"]
    push_history(record)

# =========================================================
# 20) QURANIC ANALYSIS FUNCTION
# =========================================================
def calculate_absolute_total(mass, speed, energy):
    return round(float(mass) + float(speed) + float(energy), 2)

def show_resonance_waves(analysis):
    st.markdown("### 🌊 موجات الميزان السيادي")
    col_w1, col_w2, col_w3 = st.columns(3)
    with col_w1:
        st.metric("الكتلة", f"{analysis['mass']:.2f}")
        st.progress(min(analysis["mass"] / 250, 1.0))
    with col_w2:
        st.metric("السرعة", f"{analysis['speed']:.2f}")
        st.progress(min(analysis["speed"] / 250, 1.0))
    with col_w3:
        st.metric("الطاقة الجذرية", f"{analysis['energy']:.2f}")
        st.progress(min(analysis["energy"] / 250, 1.0))

def render_sovereign_insight(match_item):
    root_name = match_item['root']
    with st.expander(f"🔮 أنعام الجذر: [{root_name}] - المدار: {match_item['orbit']}"):
        st.markdown(f"**البصيرة:** {match_item['insight']}")
        st.markdown(f"**الوزن الطاقي:** {match_item['weight']}")
        
        resonance = matrix_idx.get(root_name, [])
        if resonance:
            st.markdown("---")
            st.markdown(f"**🪐 الرنين الموضعي ({len(resonance)} موضع):**")
            for occ in resonance[:5]:
                st.info(f"📖 {occ['text']}\n\n**[{occ.get('surah', '?')}:{occ.get('verse', '?')}]**")
        else:
            st.caption("لم يتم رصد رنين إضافي لهذا الجذر في المصفوفة الحالية.")

def analyze_path(text, l_idx, root_index, use_manual_resolution=True):
    norm = normalize_arabic(text)
    res = {
        "original_text": text,
        "normalized_text": norm,
        "mass": 0.0,
        "speed": 0.0,
        "energy": 0.0,
        "orbit": "غير_مرصود",
        "insight": "لا توجد بصيرة رصدية لهذا المسار.",
        "direction": "غير محدد",
        "count": 0,
        "matched_roots": [],
        "orbit_counter": Counter(),
        "ambiguities": [],
        "confidence": 0.0
    }

    clean_text = norm.replace(" ", "")
    dir_counter = Counter()
    energy_types = Counter()

    for char in clean_text:
        meta = l_idx.get(char)
        if meta:
            res["mass"] += float(meta.get("mass", 0))
            res["speed"] += float(meta.get("speed", 0))
            res["count"] += 1
            d = meta.get("direction", "unknown")
            dir_counter[d] += 1
            et = meta.get("energy_type", "unknown")
            energy_types[et] += 1

    if dir_counter:
        res["direction"] = dir_counter.most_common(1)[0][0]

    if energy_types:
        res["dominant_energy_type"] = energy_types.most_common(1)[0][0]
    else:
        res["dominant_energy_type"] = "غير محدد"

    words = norm.split()
    for word in words:
        matched_root, entries, ambiguous = resolve_root_with_ambiguity(
            word, root_index, use_manual_resolution=use_manual_resolution
        )

        if ambiguous:
            all_matches = get_all_matching_roots(word, root_index)
            res["ambiguities"].append({
                "word": word,
                "options": [
                    {
                        "root": m["candidate"],
                        "orbit": m["best_entry"]["orbit"],
                        "weight": m["best_entry"]["weight"]
                    }
                    for m in all_matches
                ]
            })

        if matched_root and entries:
            best_entry = max(entries, key=lambda x: x["weight"])
            res["energy"] += best_entry["weight"]
            res["orbit_counter"][best_entry["orbit"]] += best_entry["weight"]
            res["matched_roots"].append({
                "word": word,
                "root": matched_root,
                "orbit": best_entry["orbit"],
                "weight": best_entry["weight"],
                "insight": best_entry["insight"]
            })

    if res["orbit_counter"]:
        best_orbit, _ = res["orbit_counter"].most_common(1)[0]
        res["orbit"] = best_orbit
        for m in res["matched_roots"]:
            if m["orbit"] == best_orbit:
                res["insight"] = m["insight"]
                break

    harmony = contextual_harmony_engine(res["matched_roots"])
    res.update(harmony)

    word_count = max(len(words), 1)
    root_match_ratio = len(res["matched_roots"]) / word_count
    ambiguity_penalty = min(len(res["ambiguities"]) * 0.08, 0.32)
    confidence = max(0.0, min(1.0, (root_match_ratio * 0.7 + (res["harmony_score"] / 100) * 0.3) - ambiguity_penalty))
    res["confidence"] = round(confidence * 100, 2)

    res["total"] = calculate_absolute_total(res["mass"], res["speed"], res["energy"])
    
    return res

# =========================================================
# 21) AMBIGUITY RESOLUTION HELPERS
# =========================================================
def get_all_matching_roots(word, root_index):
    candidates = generate_root_candidates(word)
    all_matches = []

    for c in candidates:
        if c["form"] in root_index:
            entries = root_index[c["form"]]
            best_entry = max(entries, key=lambda x: x["weight"])
            all_matches.append({
                "candidate": c["form"],
                "entries": entries,
                "best_entry": best_entry
            })

    seen = set()
    unique = []
    for m in all_matches:
        if m["candidate"] not in seen:
            unique.append(m)
            seen.add(m["candidate"])

    unique = sorted(unique, key=lambda x: x["best_entry"]["weight"], reverse=True)
    return unique

def resolve_root_with_ambiguity(word, root_index, use_manual_resolution=True):
    matches = get_all_matching_roots(word, root_index)

    if not matches:
        return None, [], False

    word_key = normalize_arabic(word)
    if word_key in st.session_state.ambiguity_choices:
        chosen_root = st.session_state.ambiguity_choices[word_key]
        for m in matches:
            if m["candidate"] == chosen_root:
                return chosen_root, m["entries"], len(matches) > 1

    if not use_manual_resolution or len(matches) == 1:
        return matches[0]["candidate"], matches[0]["entries"], len(matches) > 1

    return matches[0]["candidate"], matches[0]["entries"], True

# =========================================================
# 22) EXPORT HELPERS
# =========================================================
def build_export_payload(result, label="مسار"):
    return {
        "label": label,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "original_text": result.get("original_text", ""),
        "normalized_text": result.get("normalized_text", ""),
        "orbit": result.get("orbit", ""),
        "insight": result.get("insight", ""),
        "direction": result.get("direction", ""),
        "dominant_energy_type": result.get("dominant_energy_type", ""),
        "mass": result.get("mass", 0),
        "speed": result.get("speed", 0),
        "energy": result.get("energy", 0),
        "total": result.get("total", 0),
        "confidence": result.get("confidence", 0),
        "harmony_score": result.get("harmony_score", 0),
        "harmony_label": result.get("harmony_label", ""),
        "matched_roots": result.get("matched_roots", []),
        "ambiguities": result.get("ambiguities", [])
    }

def build_export_text(result, label="مسار"):
    lines = []
    lines.append(f"=== الوثيقة الوجودية | {label} ===")
    lines.append(f"التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    lines.append("النص الأصلي:")
    lines.append(result.get("original_text", ""))
    lines.append("")
    lines.append("النص المطبع:")
    lines.append(result.get("normalized_text", ""))
    lines.append("")
    lines.append(f"المدار النهائي: {result.get('orbit', '')}")
    lines.append(f"البصيرة: {result.get('insight', '')}")
    lines.append(f"الاتجاه الغالب: {result.get('direction', '')}")
    lines.append(f"نوع الطاقة الغالب: {result.get('dominant_energy_type', '')}")
    lines.append(f"الكتلة: {result.get('mass', 0)}")
    lines.append(f"السرعة: {result.get('speed', 0)}")
    lines.append(f"الطاقة الجذرية: {result.get('energy', 0)}")
    lines.append(f"الإجمالي السيادي: {result.get('total', 0)}")
    lines.append(f"درجة الثقة: {result.get('confidence', 0)}%")
    lines.append(f"التناغم السياقي: {result.get('harmony_score', 0)}% | {result.get('harmony_label', '')}")
    lines.append("")
    lines.append("الجذور المرصودة:")
    for m in result.get("matched_roots", []):
        lines.append(f"- الكلمة: {m['word']} | الجذر: {m['root']} | المدار: {m['orbit']} | الوزن: {m['weight']}")
    lines.append("")
    lines.append("الالتباسات:")
    for amb in result.get("ambiguities", []):
        opts = " | ".join([f"{o['root']} ({o['orbit']}, {o['weight']})" for o in amb["options"]])
        lines.append(f"- الكلمة: {amb['word']} => {opts}")
    return "\n".join(lines)

def metric_card(label, value, subtitle=None, tone="normal"):
    cls = ""
    if tone == "good":
        cls = "sov-good"
    elif tone == "warn":
        cls = "sov-warn"
    elif tone == "bad":
        cls = "sov-bad"

    html = f"""
    <div class="sov-card">
        <div class="sov-label">{label}</div>
        <div class="sov-big {cls}">{value}</div>
        <div class="sov-label">{subtitle or ""}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def chips(items):
    if not items:
        st.caption("—")
        return
    html = "".join([f'<span class="sov-chip">{x}</span>' for x in items])
    st.markdown(html, unsafe_allow_html=True)

# =========================================================
# 23) UI TITLE
# =========================================================
st.title("🛰️ محراب نبراس السيادي v27.0 — 1800 جذر (كسر جمود الرصد)")
st.write("تحليل حرفي + جذري قرآني (1800 جذر) + ذاكرة + تناغم سياقي + تصدير + تحصين من الالتباس + أنعام المصفوفة")

# =========================================================
# 24) SIDEBAR - DIAGNOSTICS
# =========================================================
with st.sidebar:
    st.markdown("## ⚙️ التحكم السيادي")
    silent_mode = st.toggle("🧪 وضع الرصد الصامت (Silent Observatory)", value=False)

    st.markdown("### 🛠️ لوحة التشخيص السيادي")
    st.write(f"📁 **ملف الحروف:** {path_l if path_l else '❌ مفقود'}")
    st.write(f"📁 **ملف المعجم (1800 جذر):** {path_x if path_x else '❌ مفقود'}")
    st.write(f"📚 **عدد الجذور المحملة:** **{total_roots}** جذراً")
    st.write(f"📖 **إجمالي المداخل:** {total_entries}")
    
    # عرض أول 20 جذراً للتحقق
    if roots_list:
        st.markdown("---")
        st.markdown("**🔍 عينة من الجذور (أول 20):**")
        sample_roots = roots_list[:20]
        st.write(", ".join(sample_roots))
    
    st.markdown("---")
    
    matrix_size_mb = get_file_size_mb(matrix_path)
    st.write(f"📁 **ملف المصفوفة:** {matrix_path if matrix_path else '❌ مفقود'}")
    if matrix_path:
        st.write(f"   - **حجم الملف:** {matrix_size_mb} MB")
        st.write(f"   - **عدد الآيات:** {total_verses}")
        st.write(f"   - **الآيات المفهرسة:** {indexed_verses}")
    
    st.write(f"🔤 **عدد الحروف المفهرسة:** {len(letters_idx)}")
    st.write(f"🪐 **عدد الجذور في المصفوفة:** {len(matrix_idx)}")

    if matrix_path:
        st.success("✅ المصفوفة القرآنية متصلة")
    else:
        st.warning("⚠️ لم يتم العثور على matrix_data.json")

    st.markdown("---")
    st.markdown("### 🧠 الذاكرة السيادية الموضعية (آخر 5)")
    if st.session_state.session_history:
        for idx, item in enumerate(reversed(st.session_state.session_history[-5:]), 1):
            st.markdown(f"**{idx}. {item['label']}**")
            st.caption(f"المدار: {item['orbit']} | الإجمالي: {item['total']} | الثقة: {item['confidence']}%")
            st.text(item["preview"])
            st.markdown("---")
    else:
        st.caption("لا توجد تحليلات محفوظة بعد.")

    st.markdown("---")
    st.markdown("### 🧪 بروتوكول الختام")
    st.write("**Mohamed | As-Sajdah [5]**")
    st.write("**خِت فِت.**")

# =========================================================
# 25) LEXICON TOOLS
# =========================================================
tool_col1, tool_col2 = st.columns(2)

with tool_col1:
    if st.button("📦 عرض عينة من الجذور (أول 50)", use_container_width=True):
        if roots_list:
            st.subheader("📘 عينة من الجذور الـ 1800")
            st.write(", ".join(roots_list[:50]))
            st.caption(f"إجمالي الجذور المحملة: {total_roots}")
        else:
            st.warning("لا توجد جذور متاحة.")

with tool_col2:
    if roots_list:
        # عرض أول 100 جذر كنص قابل للتنزيل
        roots_text = "\n".join(roots_list)
        st.download_button(
            label="📥 تنزيل قائمة الجذور (TXT)",
            data=roots_text,
            file_name="nibras_roots_list.txt",
            mime="text/plain",
            use_container_width=True
        )

st.markdown("---")

# =========================================================
# 26) THREE TEXT INPUTS
# =========================================================
col1, col2, col3 = st.columns(3)
with col1:
    t1 = st.text_area("📍 المسار 1", placeholder="أدخل الآية أو النص...", height=140, key="v1")
with col2:
    t2 = st.text_area("📍 المسار 2", placeholder="أدخل الآية أو النص...", height=140, key="v2")
with col3:
    t3 = st.text_area("📍 المسار 3", placeholder="أدخل الآية أو النص...", height=140, key="v3")

# =========================================================
# 27) MAIN ANALYSIS BUTTON
# =========================================================
if st.button("🚀 إطلاق الرصد القرآني المقارن", use_container_width=True):
    inputs = [t1, t2, t3]
    results = []
    display_cols = st.columns(3)

    for i, txt in enumerate(inputs):
        if txt.strip():
            res = analyze_path(txt, letters_idx, quranic_root_index, use_manual_resolution=True)
            results.append(res)

            st.session_state.session_history.append({
                "label": f"المسار {i+1}",
                "orbit": res["orbit"],
                "total": res["total"],
                "confidence": res["confidence"],
                "preview": txt[:60] + ("..." if len(txt) > 60 else ""),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            st.session_state.session_history = st.session_state.session_history[-5:]

            with display_cols[i]:
                if not silent_mode:
                    st.markdown(f"""
                    <div class="comparison-card">
                        <h3 style='margin:0;'>المسار {i+1}</h3>
                        <h1 style='color:#8bc34a; font-size:40px;'>{res['total']}</h1>
                        <p style='text-align:center;'><b>المدار:</b> {res['orbit']}</p>
                        <p style='text-align:center;'><b>الجذور المطابقة:</b> {len(res['matched_roots'])}</p>
                        <p style='text-align:center;'><b>الثقة:</b> {res['confidence']}%</p>
                    </div>
                    """, unsafe_allow_html=True)

                    show_resonance_waves(res)
                else:
                    st.subheader(f"المسار {i+1}")
                    st.metric("الإجمالي السيادي", res["total"])
                    st.metric("درجة الثقة", f"{res['confidence']}%")

                st.markdown(f"""
                <div class="detail-box">
                    <b>الاتجاه الغالب:</b> {res['direction']}<br>
                    <b>نوع الطاقة الغالب:</b> {res.get('dominant_energy_type', 'غير محدد')}<br>
                    <b>عدد الحروف المرصودة:</b> {res['count']}<br>
                    <b>التناغم:</b> {res['harmony_score']}% — {res['harmony_label']}
                </div>
                """, unsafe_allow_html=True)

                if res["ambiguities"]:
                    st.markdown("### 🛡️ تنبيهات الالتباس")
                    for amb_idx, amb in enumerate(res["ambiguities"]):
                        st.warning(f"الكلمة **{amb['word']}** تحتمل أكثر من جذر.")
                        options = [f"{o['root']} | {o['orbit']} | وزن {o['weight']}" for o in amb["options"]]
                        selected = st.selectbox(
                            f"اختر الجذر الأنسب للكلمة: {amb['word']}",
                            options,
                            key=f"amb_{i}_{amb_idx}_{amb['word']}"
                        )
                        chosen_root = selected.split(" | ")[0].strip()
                        st.session_state.ambiguity_choices[normalize_arabic(amb["word"])] = chosen_root

                if res["matched_roots"]:
                    st.markdown("### 🔍 الجذور المرصودة")
                    for m in res["matched_roots"]:
                        render_sovereign_insight(m)
                else:
                    st.markdown("""
                    <div class="status-warn">
                        ⚠️ لم يتم العثور على جذور مطابقة في هذا المسار.
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("### 📤 التصدير السيادي")
                payload = build_export_payload(res, label=f"المسار {i+1}")
                payload_json = json.dumps(payload, ensure_ascii=False, indent=2)
                payload_txt = build_export_text(res, label=f"المسار {i+1}")

                exp_col1, exp_col2 = st.columns(2)
                with exp_col1:
                    st.download_button(
                        label=f"⬇️ JSON المسار {i+1}",
                        data=payload_json,
                        file_name=f"nibras_path_{i+1}.json",
                        mime="application/json",
                        use_container_width=True
                    )
                with exp_col2:
                    st.download_button(
                        label=f"⬇️ TXT الوثيقة الوجودية {i+1}",
                        data=payload_txt,
                        file_name=f"nibras_path_{i+1}_existential_report.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
        else:
            results.append(None)

    # =========================================================
    # 28) FINAL ADVISOR
    # =========================================================
    valid_results = [r for r in results if r is not None]
    if valid_results:
        st.markdown("<div class='mentor-box'>", unsafe_allow_html=True)
        st.markdown("### 🧠 المستشار الشخصي السيادي — الإصدار الختامي")

        best = max(valid_results, key=lambda x: x["total"])
        most_confident = max(valid_results, key=lambda x: x["confidence"])
        most_harmonic = max(valid_results, key=lambda x: x["harmony_score"])

        with st.chat_message("assistant", avatar="🕌"):
            st.write(f"**أعلى مسار طاقيًا:** المدار **({best['orbit']})** بإجمالي **{best['total']}**")
            st.write(f"**أعلى مسار ثقة:** المدار **({most_confident['orbit']})** بدرجة **{most_confident['confidence']}%**")
            st.write(f"**أعلى مسار تناغمًا:** **{most_harmonic['harmony_label']}** ({most_harmonic['harmony_score']}%)")

            st.info(f"**البصيرة الحاكمة:** {best['insight']}")
            st.success(f"**الاتجاه الغالب:** {best['direction']}")
            st.write(f"**نوع الطاقة الغالب:** {best.get('dominant_energy_type', 'غير محدد')}")
            st.write(f"**عدد الجذور المطابقة:** {len(best['matched_roots'])}")
            st.write(f"**عدد حالات الالتباس:** {len(best['ambiguities'])}")
            
            all_roots = [m['root'] for m in best['matched_roots']]
            matrix_roots = [r for r in all_roots if r in matrix_idx]
            if matrix_roots:
                st.markdown("---")
                st.markdown("#### 🪐 رنين المصفوفة الكلية (من واقع المصحف):")
                for root in matrix_roots[:2]:
                    for occ in matrix_idx[root][:2]:
                        st.write(f"📖 **{occ.get('surah', '?')}:{occ.get('verse', '?')}** — {occ['text'][:100]}...")

            if best["confidence"] >= 80:
                st.success("🟢 البيان الختامي: هذا المسار ذو ثقة سيادية مرتفعة ويمكن اعتماده كمرجع تحليلي قوي.")
            elif best["confidence"] >= 55:
                st.warning("🟡 البيان الختامي: هذا المسار واعد، لكنه يستفيد من مراجعة الالتباسات لتحسين الدقة.")
            else:
                st.error("🔴 البيان الختامي: هذا المسار يحتاج تدقيقًا سياقيًا إضافيًا قبل اعتماده.")

        st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# 29) FOOTER
# =========================================================
st.sidebar.markdown("---")
st.sidebar.markdown("**Blekinge, Sweden | Nibras Sovereign v27.0**")
st.sidebar.markdown("*Mohamed | As-Sajdah [5]*")
st.sidebar.markdown("*خِت فِت.*")
