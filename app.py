# -*- coding: utf-8 -*-
# ==============================================================================
# نظام نِبْرَاس السيادي (Nibras Sovereign System) - الإصدار v65.0
# الإصدار: الميثاقي - الدمج الكامل بين v63.2 و v40.2
# الحوكمة الاستراتيجية + الاستنطاق القرآني + التثبيت الفائق
# المستخدم المهيمن: محمّد
# ==============================================================================

import streamlit as st
import pandas as pd
import plotly.express as px
from collections import Counter, defaultdict
import re
import os
import json
import time
import hashlib
import math
import copy
import random
from itertools import combinations

# ==============================================================================
# [1] دوال المسار السيادية
# ==============================================================================
def get_absolute_path(filename):
    base_path = os.path.dirname(os.path.abspath(__file__))
    paths_to_check = [
        os.path.join(base_path, "data", filename),
        os.path.join(base_path, filename),
        os.path.join(os.getcwd(), "data", filename)
    ]
    for p in paths_to_check:
        if os.path.exists(p):
            return p
    return None

# ==============================================================================
# [2] دوال التطهير الأساسية
# ==============================================================================
ARABIC_DIACRITICS_PATTERN = re.compile(r'[\u0617-\u061A\u064B-\u0652\u0670\u06D6-\u06ED]')

def normalize_lexicon_root(root_name: str):
    if not root_name:
        return ""
    return root_name.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا").replace("ة", "ه").replace("ى", "ي").strip()

def normalize_sovereign(text: str):
    if not text: 
        return ""
    text = ARABIC_DIACRITICS_PATTERN.sub('', text)
    text = text.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا").replace("ى", "ي").replace("ة", "ه")
    return re.sub(r'[^\u0621-\u063A\u0641-\u064A\s]', ' ', text).strip()

def ensure_dot(text):
    if not text:
        return ""
    s = str(text).strip()
    if not s.endswith('.'):
        s = s + '.'
    return s

# ==============================================================================
# [3] تهيئة الذاكرة المركزية وحماية الفساد (v63.2 Self-Healing)
# ==============================================================================
def sanitize_session_state():
    """تنقية وتصحيح حالة الجلسة عند التحميل"""
    if "active_meta_law" not in st.session_state or not isinstance(st.session_state.active_meta_law, dict):
        st.session_state.active_meta_law = {"root_influence": 1.0, "energy_bias": 1.0, "gene_weight": {"N": 1.0, "S": 1.0, "G": 1.0, "B": 1.0, "C": 1.0}}
    else:
        law = st.session_state.active_meta_law
        if not isinstance(law.get("root_influence"), (int, float)) or math.isnan(law.get("root_influence", 0)):
            law["root_influence"] = 1.0
        if not isinstance(law.get("energy_bias"), (int, float)) or math.isnan(law.get("energy_bias", 0)):
            law["energy_bias"] = 1.0
        law["root_influence"] = min(max(law["root_influence"], 0.85), 1.80)
        law["energy_bias"] = min(max(law["energy_bias"], 0.80), 2.50)
    
    if "system_log" not in st.session_state or not isinstance(st.session_state.system_log, list):
        st.session_state.system_log = []
    
    if "orbit_active" not in st.session_state:
        st.session_state.orbit_active = False
    if "orbit_bodies" not in st.session_state:
        st.session_state.orbit_bodies = []
    if "input_area" not in st.session_state:
        st.session_state.input_area = ""
    if "current_text" not in st.session_state:
        st.session_state.current_text = ""
    if "trigger_analysis" not in st.session_state:
        st.session_state.trigger_analysis = False
    if "last_processed_text" not in st.session_state:
        st.session_state.last_processed_text = ""
    if "widget_key" not in st.session_state:
        st.session_state.widget_key = "orbital_init_v1"
    
    if "current_strategy" not in st.session_state:
        st.session_state.current_strategy = "STANDARD"
    if "last_correction_cycle" not in st.session_state:
        st.session_state.last_correction_cycle = -9999
    if "last_correction_snapshot" not in st.session_state:
        st.session_state.last_correction_snapshot = {
            "root_influence": None,
            "energy_bias": None,
            "strategy": None
        }
    if "correction_cooldown" not in st.session_state:
        st.session_state.correction_cooldown = 2
    
    if "r_index" not in st.session_state:
        st.session_state.r_index = {}
    if "all_roots" not in st.session_state:
        st.session_state.all_roots = []
    if "quran_data" not in st.session_state:
        st.session_state.quran_data = []
    if "orbit_counter" not in st.session_state:
        st.session_state.orbit_counter = Counter()
    if "cosmic_radar_data" not in st.session_state:
        st.session_state.cosmic_radar_data = pd.DataFrame()
    if "root_frequency_data" not in st.session_state:
        st.session_state.root_frequency_data = Counter()
    if "initialized" not in st.session_state:
        st.session_state.initialized = False

# ==============================================================================
# [4] إعدادات الهوية السيادية
# ==============================================================================
sanitize_session_state()
st.set_page_config(page_title="Nibras v65.0 - السيادة المطلقة", layout="wide")

st.markdown("""
<style>
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stAppHeader {display: none;}
    .st-emotion-cache-1v0mbdj {display: none;}
    .st-emotion-cache-1wivap2 {display: none;}
    .st-emotion-cache-zq5wmm {display: none;}
    .st-emotion-cache-18ni7ap {display: none;}
    .st-emotion-cache-1dp5vir {display: none;}
    #MainMenu {visibility: hidden;}
    .stDeployButton {display: none;}
    [data-testid="stToolbar"] {display: none;}
    [data-testid="stDecoration"] {display: none;}
    
    h1, h2, h3, .stMarkdown { word-break: normal !important; white-space: nowrap !important; }
    [data-testid="stSidebar"] div { overflow: hidden !important; }
    
    @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&display=swap');
    [data-testid="stAppViewContainer"] { background: #050505; color: #e0e0e0; direction: rtl; font-family: 'Amiri', serif; }
    .stTabs [aria-selected="true"] { color: #FFD700 !important; border-bottom: 2px solid #FFD700 !important; }
    
    .insight-card {
        background: linear-gradient(135deg, #0d0d14 0%, #161625 100%);
        padding: 25px; border-radius: 15px; border-right: 8px solid #FFD700;
        margin-bottom: 20px; line-height: 1.8; font-size: 1.1em;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    .energy-badge { background: #1a3a1a; color: #00ffcc; padding: 2px 10px; border-radius: 5px; font-family: monospace; }
    .story-box {
        background: linear-gradient(135deg, rgba(10,21,10,0.85) 0%, rgba(1,1,3,0.95) 100%);
        padding: 35px; border-radius: 25px; border-right: 15px solid #4CAF50;
        line-height: 2; font-size: 1.2em; margin-bottom: 30px;
    }
    .ultra-card {
        background: #0d0d14; padding: 20px; border-radius: 20px;
        border-top: 8px solid #4fc3f7; text-align: center; margin-bottom: 20px;
    }
    .ascent-positive { background: linear-gradient(135deg, #0a2a0a 0%, #0a1a0a 100%); border-right: 5px solid #00ffcc; }
    .ascent-negative { background: linear-gradient(135deg, #2a0a0a 0%, #1a0a0a 100%); border-right: 5px solid #ff5252; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# [5] مصفوفة الجينات
# ==============================================================================
GENE_STYLE = {
    'C': {'name': 'الإبل', 'color': '#4fc3f7', 'icon': '🐪', 'meaning': 'طاقة المسير والتمكين البعيد'},
    'B': {'name': 'البقر', 'color': '#FFD700', 'icon': '🐄', 'meaning': 'طاقة التثبيت والوفرة المادية'},
    'S': {'name': 'الضأن', 'color': '#4CAF50', 'icon': '🐑', 'meaning': 'طاقة السكينة واللين والرحمة'},
    'G': {'name': 'المعز', 'color': '#ff5252', 'icon': '🐐', 'meaning': 'طاقة السيادة والحدّة والصعود'},
    'N': {'name': 'إشراق', 'color': '#00ffcc', 'icon': '✨', 'meaning': 'الانبثاق الهجين الصافي'}
}

# ==============================================================================
# [6] المستخرج الاحتمالي v31
# ==============================================================================
COMMON_PREFIXES = ["وال", "بال", "كال", "فال", "لل", "ال", "و", "ف", "ب", "ك", "ل", "س"]
COMMON_SUFFIXES = ["يات", "ات", "ون", "ين", "ان", "وا", "نا", "ها", "هم", "هن", "كم", "ني", "ة", "ه", "ي"]

def strip_affixes_ar(word: str):
    w = word
    for p in sorted(COMMON_PREFIXES, key=len, reverse=True):
        if w.startswith(p) and len(w) - len(p) >= 3:
            w = w[len(p):]
            break
    for s in sorted(COMMON_SUFFIXES, key=len, reverse=True):
        if w.endswith(s) and len(w) - len(s) >= 3:
            w = w[:-len(s)]
            break
    return w

def infer_morphological_pattern(word: str):
    w = word.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا")
    if w.startswith("است"):
        return "استفعال", 8
    if w.startswith("افت"):
        return "افتعال", 6
    if w.startswith("ان"):
        return "انفعال", 5
    if w.startswith("ت"):
        return "تفعيل/تفعل", 4
    if len(w) == 3:
        return "فعل ثلاثي", 2
    if len(w) == 4:
        return "رباعي/مزيد خفيف", 3
    return "مزيد/مركب", 3

def extract_candidate_root_v31(word, index_keys):
    w_norm = normalize_sovereign(word)
    if not w_norm:
        return None, "unresolved", "Unknown", 0

    pattern_name, morph_rank = infer_morphological_pattern(w_norm)

    if w_norm in index_keys:
        return w_norm, "direct", pattern_name, morph_rank

    stripped = strip_affixes_ar(w_norm)
    if stripped in index_keys:
        return stripped, "stripped", pattern_name, morph_rank

    if len(w_norm) == 3:
        for root in index_keys:
            common = set(w_norm) & set(root)
            if len(common) >= 2:
                return root, "resonance", "فعل ثلاثي (رنين)", 2

    return None, "unresolved", pattern_name, morph_rank

# ==============================================================================
# [7] التوقيع الجذري
# ==============================================================================
def signature_from_root(root: str):
    if not root:
        return {'x': 0.0, 'y': 0.0, 'n_factor': 0, 'eb': 0.0, 'rb': 1.0}
    h = int(hashlib.md5(root.encode('utf-8')).hexdigest(), 16)
    return {
        'x': round(((h % 360) - 180) / 10.0, 3),
        'y': round((((h >> 8) % 360) - 180) / 10.0, 3),
        'n_factor': (h >> 16) % 100,
        'eb': round((((h >> 24) % 81) - 40) / 10.0, 3),
        'rb': round(0.90 + (((h >> 32) % 21) / 100.0), 3)
    }

# ==============================================================================
# [8] الاستحقاق الجيني
# ==============================================================================
def resolve_sovereign_gene(orbit_id, morph_rank, root_sig, base_energy):
    orbit = int(orbit_id or 0)
    if orbit in [1, 2]:
        base_gene = "C"
    elif orbit in [3, 4]:
        base_gene = "B"
    elif orbit in [5, 6]:
        base_gene = "G"
    elif orbit >= 7:
        base_gene = "S"
    else:
        base_gene = "N"

    n_factor = root_sig.get('n_factor', 0)
    high_orbit = orbit >= 5
    strong_morph = morph_rank >= 6
    strong_energy = base_energy >= 85
    luminous_sig = n_factor >= 92
    near_luminous_sig = n_factor >= 86

    if luminous_sig and (high_orbit or strong_morph or strong_energy):
        return "N"
    if near_luminous_sig and high_orbit and strong_energy and strong_morph:
        return "N"
    if base_gene == "B" and morph_rank >= 7 and n_factor >= 80:
        return "G"
    if base_gene == "C" and morph_rank >= 5 and strong_energy:
        return "B"
    return base_gene

# ==============================================================================
# [9] الطاقة الديناميكية
# ==============================================================================
def compute_dynamic_energy(base_w, count, mode, morph_rank, orbit_id, root_sig):
    base_energy = base_w * 100 if base_w < 10 else base_w
    repetition_boost = 1.0 + math.log1p(max(0, count - 1)) * 0.35
    mode_factor = {"direct": 1.00, "stripped": 0.92, "resonance": 0.85, "unresolved": 0.60}.get(mode, 0.85)
    morph_factor = 1.0 + (max(1, morph_rank) - 1) * 0.025
    orbit_factor = 1.0 + max(0, int(orbit_id or 0) - 4) * 0.03
    sig_energy_bias = root_sig.get('eb', 0.0)
    energy = (base_energy * repetition_boost * mode_factor * morph_factor * orbit_factor) + sig_energy_bias
    return round(max(1.0, energy), 2)

# ==============================================================================
# [10] مؤشر الصعود
# ==============================================================================
def compute_ascent_vector(bodies):
    if not bodies:
        return 0
    gene_weights = {"N": 2.2, "S": 1.5, "G": 1.0, "B": -0.4, "C": -0.9}
    total = 0.0
    for b in bodies:
        g_weight = gene_weights.get(b.get('gene', 'B'), 0.0)
        orbit_bonus = max(0, (b.get('orbit_id', 0) - 4)) * 0.05
        total += (g_weight + orbit_bonus) * b.get('energy', 0)
    return round(total / len(bodies), 2)

# ==============================================================================
# [11] شبكة الرنين
# ==============================================================================
def build_resonance_network(bodies):
    edges = []
    for a, b in combinations(range(len(bodies)), 2):
        ra, rb = bodies[a], bodies[b]
        dist = abs(ra.get('pos', a) - rb.get('pos', b))
        if dist >= 8:
            continue
        proximity = 1.0 / max(1, dist)
        same_gene_bonus = 1.20 if ra.get('gene') == rb.get('gene') else 1.0
        n_bonus = 1.15 if ('N' in [ra.get('gene'), rb.get('gene')]) else 1.0
        ra_rb = ra.get('resonance_bias', 1.0) * rb.get('resonance_bias', 1.0)
        orbit_gap = abs(ra.get('orbit_id', 0) - rb.get('orbit_id', 0))
        orbit_bonus = 1.12 if orbit_gap <= 1 else 1.0
        shared_chars = set(ra.get('root_norm', '')) & set(rb.get('root_norm', ''))
        char_resonance = 1.0 + (len(shared_chars) * 0.25)
        strength = proximity * same_gene_bonus * n_bonus * ra_rb * orbit_bonus * char_resonance
        edges.append({
            "source": ra.get('root', '?'),
            "target": rb.get('root', '?'),
            "strength": round(strength, 3),
            "distance": dist,
            "gene_pair": f"{ra.get('gene','?')}-{rb.get('gene','?')}",
            "shared_letters": len(shared_chars)
        })
    return sorted(edges, key=lambda x: x['strength'], reverse=True)

# ==============================================================================
# [12] بروتوكول خِت فِت للأرشفة
# ==============================================================================
def khit_fit_archive(res_bodies, ascent_score):
    if not res_bodies:
        return False
    archive_data = {
        "timestamp": time.time(),
        "ascent": ascent_score,
        "dominant_gene": Counter([b['gene'] for b in res_bodies]).most_common(1)[0][0],
        "roots": [b['root_norm'] for b in res_bodies],
        "total_energy": sum([b['energy'] for b in res_bodies])
    }
    os.makedirs("data", exist_ok=True)
    with open("data/deep_memory.json", "a", encoding="utf-8") as f:
        f.write(json.dumps(archive_data, ensure_ascii=False) + "\n")
    
    log_entry = copy.deepcopy(archive_data)
    log_entry["step"] = len(st.session_state.system_log) + 1
    log_entry["shift_value"] = st.session_state.active_meta_law.get("root_influence", 1.0)
    log_entry["new_influence"] = archive_data["total_energy"] / 100 if archive_data["total_energy"] > 0 else 0
    log_entry["top_root"] = archive_data["roots"][0] if archive_data["roots"] else "none"
    st.session_state.system_log.append(log_entry)
    if len(st.session_state.system_log) > 50:
        st.session_state.system_log = st.session_state.system_log[-50:]
    
    return True

# ==============================================================================
# [13] تحميل قواعد البيانات
# ==============================================================================
@st.cache_data(ttl=3600)
def load_lexicon_db(path):
    if not path or not os.path.exists(path):
        return {}, [], Counter()
    with open(path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            return {}, [], Counter()
    r_index = {}
    all_roots = []
    orbit_counter = Counter()
    if not isinstance(data, list):
        return {}, [], Counter()
    for item in data:
        raw_root = item.get("root", "")
        if not raw_root:
            continue
        normalized = normalize_lexicon_root(raw_root)
        orbit_id = item.get("orbit_id", 0)
        weight_val = float(item.get("weight", 50.0))
        calibrated_energy = weight_val * 100 if weight_val < 10 else weight_val
        if orbit_id in [1, 2]:
            base_gene = "C"
        elif orbit_id in [3, 4]:
            base_gene = "B"
        elif orbit_id in [5, 6]:
            base_gene = "G"
        elif orbit_id >= 7:
            base_gene = "S"
        else:
            base_gene = "N"
        orbit_name = f"المدار {orbit_id}" if orbit_id else "وعي"
        insight_text = item.get("insight_radar", item.get("insight", ""))
        r_index[normalized] = {
            "root_raw": raw_root,
            "root": normalized,
            "orbit_id": orbit_id,
            "orbit": orbit_name,
            "weight": weight_val,
            "raw_energy": calibrated_energy,
            "insight": ensure_dot(insight_text),
            "gene_base": base_gene
        }
        all_roots.append(r_index[normalized])
        orbit_counter[orbit_name] += 1
    return r_index, all_roots, orbit_counter

@st.cache_data(ttl=3600)
def load_quran_matrix():
    path = get_absolute_path("matrix_data.json")
    if path:
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for item in data:
                    if "roots" not in item:
                        item["roots"] = []
                    if "index" not in item:
                        item["index"] = 0
                return data
        except Exception:
            return []
    return []

@st.cache_data(ttl=3600)
def load_quran_roots():
    path = get_absolute_path("quran_roots_complete.json")
    if not path:
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return {}
    
    roots_map = {}
    roots_list = data.get("roots", []) if isinstance(data, dict) else data
    for item in roots_list:
        raw_root = item.get("root", "")
        if not raw_root: 
            continue
        norm = normalize_sovereign(raw_root)
        roots_map[norm] = {
            "root_raw": raw_root,
            "orbit_id": 0,
            "orbit": item.get("orbit_hint", "آيات_الكون"),
            "weight": float(item.get("frequency", 10)),
            "insight": f"جذر قرآني سيادي (التكرار: {item.get('frequency', 'غير محدد')})",
            "gene_base": "N"
        }
    return roots_map

# ==============================================================================
# [14] دوال المحرك المداري
# ==============================================================================
def display_insight_cards(bodies):
    if not bodies:
        return
    for res in bodies:
        gene_base = res.get('gene_base', res.get('gene', 'N'))
        base_info = GENE_STYLE.get(gene_base, GENE_STYLE['N'])
        st.markdown(f"""
        <div class="insight-card" style="border-right-color: {res['color']}">
            <b style="color:{res['color']}; font-size:1.2em;">📌 الجذر: {res['root']}</b> |
            🧬 الجين النهائي: {res['icon']} {res['gene_name']} |
            🧱 الجين القاعدي: {base_info['icon']} {base_info['name']} |
            ⚡ الطاقة: <span class="energy-badge">{res['energy']:.1f}</span><br>
            🔄 المصدر: {res.get('source', res['root'])} |
            📐 النمط: {res.get('pattern', 'مباشر')} |
            🪜 الرتبة الصرفية: {res.get('morph_rank', '-')} |
            ✨ عامل الإشراق: {res.get('sig_n_factor', '-')}<br>
            🛰️ المدار: {res.get('orbit', 'وعي')} |
            📍 الموضع: ({res.get('x', 0)}, {res.get('y', 0)})
            <hr style="border:0.5px solid #333; margin:10px 0;">
            <p>🔮 {res['insight']}</p>
        </div>
        """, unsafe_allow_html=True)

def process_text_and_generate_bodies(input_text, r_index):
    clean_text = normalize_sovereign(input_text)
    words = clean_text.split()
    bodies = []
    unique_roots = []
    all_matched_roots = []
    temp_meta = []
    
    for pos, word in enumerate(words):
        rk, mode, pattern_name, morph_rank = extract_candidate_root_v31(word, r_index.keys())
        temp_meta.append({"word": word, "pos": pos, "rk": rk, "mode": mode, "pattern_name": pattern_name, "morph_rank": morph_rank})
        if rk:
            all_matched_roots.append(rk)
            if rk not in unique_roots:
                unique_roots.append(rk)
    
    counts = Counter(all_matched_roots)
    
    for m in temp_meta:
        if not m['rk']:
            continue
        data = r_index.get(m['rk'])
        if not data:
            continue
        sig = signature_from_root(m['rk'])
        dynamic_energy = compute_dynamic_energy(
            base_w=data['weight'], count=counts[m['rk']], mode=m['mode'],
            morph_rank=m['morph_rank'], orbit_id=data.get('orbit_id', 0), root_sig=sig
        )
        final_gene = resolve_sovereign_gene(
            orbit_id=data.get('orbit_id', 0), morph_rank=m['morph_rank'],
            root_sig=sig, base_energy=dynamic_energy
        )
        gene_info = GENE_STYLE.get(final_gene, GENE_STYLE['N'])
        orbit_shift_x = (data.get('orbit_id', 0) - 4) * 1.4 if data.get('orbit_id', 0) else 0
        orbit_shift_y = (m['morph_rank'] - 3) * 0.8
        bodies.append({
            "root": data['root_raw'], "root_norm": m['rk'],
            "orbit": data['orbit'], "orbit_id": data.get('orbit_id', 0),
            "gene": final_gene, "gene_base": data.get('gene_base', 'N'),
            "gene_name": gene_info['name'], "icon": gene_info['icon'],
            "energy": dynamic_energy, "insight": data['insight'],
            "color": gene_info['color'], "pos": m['pos'],
            "mode": m['mode'], "pattern": m['pattern_name'],
            "morph_rank": m['morph_rank'], "source": m['word'],
            "x": round(sig['x'] + orbit_shift_x, 3),
            "y": round(sig['y'] + orbit_shift_y, 3),
            "sig_n_factor": sig['n_factor'], "resonance_bias": sig['rb']
        })
    
    return bodies, unique_roots

def display_orbital_radar(bodies):
    if not bodies:
        return
    df = pd.DataFrame(bodies)
    fig = px.scatter(df, x="x", y="y", text="root", size="energy", color="gene",
                     color_discrete_map={g: GENE_STYLE[g]['color'] for g in GENE_STYLE},
                     range_x=[-35, 35], range_y=[-35, 35])
    for radius in [4, 8, 12, 16, 20, 24, 28, 32]:
        fig.add_shape(type="circle", x0=-radius, y0=-radius, x1=radius, y1=radius,
                      line=dict(color="rgba(255, 215, 0, 0.15)", width=1, dash="dot"))
    fig.update_traces(textposition='top center', marker=dict(line=dict(width=1, color='white')))
    fig.update_layout(height=600, template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)',
                      plot_bgcolor='rgba(0,0,0,0)', showlegend=False, xaxis_visible=False,
                      yaxis_visible=False, margin=dict(l=0, r=0, t=0, b=0),
                      annotations=[dict(x=0, y=radius, text=f"M{i+1}", showarrow=False,
                                        font=dict(color="grey", size=8))
                                  for i, radius in enumerate([4, 8, 12, 16, 20, 24, 28, 32])])
    st.plotly_chart(fig, use_container_width=True)

def calculate_orbits(text, r_index):
    if not text:
        return []
    bodies, _ = process_text_and_generate_bodies(text, r_index)
    return bodies

def display_orbital_results():
    if st.session_state.orbit_active and st.session_state.orbit_bodies:
        bodies = st.session_state.orbit_bodies
        ascent_score = compute_ascent_vector(bodies)
        ascent_class = "ascent-positive" if ascent_score > 0 else "ascent-negative" if ascent_score < 0 else ""
        st.markdown(f"""
        <div class="{ascent_class}" style='padding:20px;border-radius:15px;margin-bottom:20px;text-align:center;'>
            <h3 style='margin:0;'>🚀 مؤشر الصعود والانحدار السيادي v65.0</h3>
            <p style='font-size:2em;margin:5px;font-weight:bold;'>{ascent_score}</p>
        </div>
        """, unsafe_allow_html=True)
        display_orbital_radar(bodies)
        total_e = sum(b['energy'] for b in bodies)
        genes_count = Counter(b['gene'] for b in bodies)
        dom_gene = max(genes_count, key=genes_count.get)
        st.markdown(f"""
        <div class="story-box">
            ✅ تم استنطاق <b>{len(bodies)}</b> جسماً جذرياً.<br>
            🧬 الهيمنة الجينية: <b>{GENE_STYLE[dom_gene]['icon']} {GENE_STYLE[dom_gene]['name']}</b><br>
            ⚡ مجموع الطاقة: <b>{total_e:.1f}</b>
        </div>
        """, unsafe_allow_html=True)
        display_insight_cards(bodies)
        return True
    return False

# ==============================================================================
# [15] دوال v63 - الحوكمة الاستراتيجية
# ==============================================================================
def get_current_cycle_index():
    return len(st.session_state.get("system_log", []))

def determine_correction_strategy():
    log = st.session_state.get("system_log", [])
    valid_log = [entry for entry in log if isinstance(entry, dict) and "new_influence" in entry]
    if len(valid_log) < 20:
        return "STANDARD"
    recent = valid_log[-20:]
    spans = []
    for i in range(1, len(recent)):
        try:
            prev_val = float(recent[i - 1]["new_influence"])
            curr_val = float(recent[i]["new_influence"])
            spans.append(abs(curr_val - prev_val))
        except Exception:
            continue
    if not spans:
        return "STANDARD"
    avg_volatility = sum(spans) / len(spans)
    if avg_volatility > 0.10:
        return "AGGRESSIVE"
    elif avg_volatility < 0.01:
        return "EXPANSIVE"
    return "STANDARD"

def is_redundant_correction(new_law, strategy):
    snap = st.session_state.get("last_correction_snapshot", {})
    prev_root = snap.get("root_influence")
    prev_energy = snap.get("energy_bias")
    prev_strategy = snap.get("strategy")
    try:
        new_root = float(new_law.get("root_influence", 1.0))
        new_energy = float(new_law.get("energy_bias", 1.0))
    except Exception:
        return False
    if prev_root is None or prev_energy is None:
        return False
    root_delta = abs(new_root - float(prev_root))
    energy_delta = abs(new_energy - float(prev_energy))
    if root_delta < 0.005 and energy_delta < 0.01 and strategy == prev_strategy:
        return True
    return False

def evaluate_system_drift(window=12):
    log = st.session_state.get("system_log", [])
    valid_rows = []
    for entry in log[-window:]:
        if not isinstance(entry, dict):
            continue
        try:
            inf_val = None
            if "new_influence" in entry:
                inf_val = float(entry["new_influence"])
            elif "influence" in entry:
                inf_val = float(entry["influence"])
            else:
                continue
            eng_val = None
            if "energy_score" in entry:
                eng_val = float(entry["energy_score"])
            elif "energy" in entry:
                eng_val = float(entry["energy"])
            elif "total_energy" in entry:
                eng_val = float(entry["total_energy"])
            else:
                continue
            valid_rows.append({"influence": inf_val, "energy": eng_val})
        except Exception:
            continue
    if len(valid_rows) < 3:
        return {"influence_span": 0.0, "energy_avg": 100.0}
    influences = [r["influence"] for r in valid_rows]
    energies = [r["energy"] for r in valid_rows]
    return {
        "influence_span": max(influences) - min(influences),
        "energy_avg": sum(energies) / len(energies)
    }

def corrective_consciousness():
    drift = evaluate_system_drift(window=10)
    if not drift or not isinstance(drift, dict):
        st.session_state.current_strategy = "STANDARD"
        return
    current_cycle = get_current_cycle_index()
    cooldown = int(st.session_state.get("correction_cooldown", 2))
    last_cycle = int(st.session_state.get("last_correction_cycle", -9999))
    if (current_cycle - last_cycle) < cooldown:
        st.session_state.current_strategy = st.session_state.get("current_strategy", "STANDARD")
        return
    strategy = determine_correction_strategy()
    law = copy.deepcopy(st.session_state.active_meta_law)
    brake_force_map = {"AGGRESSIVE": 0.70, "STANDARD": 0.85, "EXPANSIVE": 0.95}
    brake_force = brake_force_map.get(strategy, 0.85)
    influence_span = float(drift.get("influence_span", 0.0))
    energy_avg = float(drift.get("energy_avg", 0.0))
    if influence_span > 0.30:
        law["root_influence"] = round((law["root_influence"] * brake_force) + (1 - brake_force), 4)
    if energy_avg < 35:
        boost = 1.10 if strategy == "EXPANSIVE" else 1.05
        law["energy_bias"] = round(law.get("energy_bias", 1.0) * boost, 4)
    if energy_avg > 200:
        law["root_influence"] = 1.0
    law["root_influence"] = round(min(max(law.get("root_influence", 1.0), 0.85), 1.80), 4)
    law["energy_bias"] = round(min(max(law.get("energy_bias", 1.0), 0.80), 2.50), 4)
    if is_redundant_correction(law, strategy):
        st.session_state.current_strategy = strategy
        return
    st.session_state.active_meta_law = law
    st.session_state.current_strategy = strategy
    st.session_state.last_correction_cycle = current_cycle
    st.session_state.last_correction_snapshot = {
        "root_influence": law.get("root_influence", 1.0),
        "energy_bias": law.get("energy_bias", 1.0),
        "strategy": strategy
    }

def autonomous_law_evolution():
    log = st.session_state.get("system_log", [])
    current_cycle = len(log)
    old_influence = st.session_state.active_meta_law.get("root_influence", 1.0)
    new_law = copy.deepcopy(st.session_state.active_meta_law)
    if current_cycle > 0 and current_cycle % 5 == 0:
        new_law["root_influence"] = round(min(new_law.get("root_influence", 1.0) * 1.02, 1.80), 4)
    if current_cycle > 0 and current_cycle % 7 == 0:
        new_law["energy_bias"] = round(min(new_law.get("energy_bias", 1.0) * 1.01, 2.50), 4)
    st.session_state.active_meta_law = new_law
    log_entry = {
        "cycle": current_cycle,
        "old_influence": old_influence,
        "new_influence": new_law.get("root_influence", 1.0),
        "energy_score": new_law.get("energy_bias", 1.0) * 50,
        "root_influence": new_law.get("root_influence", 1.0),
        "energy_bias": new_law.get("energy_bias", 1.0),
        "timestamp": time.time()
    }
    st.session_state.system_log.append(log_entry)
    if len(st.session_state.system_log) > 200:
        st.session_state.system_log = st.session_state.system_log[-200:]

def normalize_system_log_for_df():
    log = st.session_state.get("system_log", [])
    valid_rows = []
    for entry in log:
        if not isinstance(entry, dict):
            continue
        row = {}
        self_healed = False
        for field in ["cycle", "old_influence", "new_influence", "energy_score", "root_influence", "energy_bias", "strategy", "corrected_root_influence", "corrected_energy_bias"]:
            if field in entry:
                try:
                    val = entry[field]
                    if isinstance(val, (int, float)):
                        row[field] = val
                    elif isinstance(val, str) and val.replace('.', '').isdigit():
                        row[field] = float(val)
                        self_healed = True
                    else:
                        row[field] = None
                        self_healed = True
                except Exception:
                    row[field] = None
                    self_healed = True
            else:
                row[field] = None
                if field in ["new_influence", "energy_score"]:
                    self_healed = True
        if "energy_score" not in entry and "energy_bias" in entry:
            try:
                row["energy_score"] = float(entry["energy_bias"]) * 50
                self_healed = True
            except Exception:
                row["energy_score"] = 100.0
        row["self_healed"] = self_healed
        valid_rows.append(row)
    return pd.DataFrame(valid_rows)

def sovereign_autonomous_cycle():
    autonomous_law_evolution()
    corrective_consciousness()
    if st.session_state.system_log:
        st.session_state.system_log[-1]["strategy"] = st.session_state.get("current_strategy", "STANDARD")
        snap = st.session_state.get("last_correction_snapshot", {})
        st.session_state.system_log[-1]["corrected_root_influence"] = snap.get("root_influence")
        st.session_state.system_log[-1]["corrected_energy_bias"] = snap.get("energy_bias")

def reset_nibras_system():
    st.session_state.system_log = []
    st.session_state.active_meta_law = {"root_influence": 1.0, "energy_bias": 1.0, "gene_weight": {"N": 1.0, "S": 1.0, "G": 1.0, "B": 1.0, "C": 1.0}}
    st.session_state.current_strategy = "STANDARD"
    st.session_state.last_correction_cycle = -9999
    st.session_state.last_correction_snapshot = {"root_influence": None, "energy_bias": None, "strategy": None}
    st.session_state.correction_cooldown = 2
    st.session_state.orbit_active = False
    st.session_state.orbit_bodies = []
    st.session_state.input_area = ""
    st.session_state.current_text = ""

# ==============================================================================
# [16] دوال الرادار
# ==============================================================================
def generate_sample_radar_data():
    sample_data = pd.DataFrame({
        "surah": list(range(1, 115)),
        "name": [f"سورة {i}" for i in range(1, 115)],
        "energy": [abs(math.sin(i * 0.3) * 100 + math.cos(i * 0.7) * 50) for i in range(1, 115)],
        "ascent": [abs(math.cos(i * 0.5) * 100 + math.sin(i * 0.2) * 50) for i in range(1, 115)]
    })
    return sample_data

def generate_sample_root_frequency():
    sample_roots = ["رب", "علم", "نور", "حق", "عدل", "رحم", "حكمة", "قدر", "خلق", "سبح"]
    return Counter({root: random.randint(1, 100) for root in sample_roots})

def update_cosmic_radar(quran_data, r_index, meta_law):
    if not quran_data:
        st.session_state.cosmic_radar_data = generate_sample_radar_data()
        st.session_state.root_frequency_data = generate_sample_root_frequency()
        return
    try:
        root_freq = Counter()
        surah_stats = defaultdict(lambda: {"energy": 0, "ascent": 0, "name": ""})
        for ayah in quran_data[:100]:
            roots = ayah.get("roots", [])
            if not roots:
                text = ayah.get("text", "")
                words = normalize_sovereign(text).split()
                for word in words[:5]:
                    if word in r_index:
                        roots.append(word)
            for root in roots:
                if root in r_index:
                    e = r_index[root]
                    g_mult = meta_law["gene_weight"].get(e.get("gene_base", "N"), 1.0)
                    energy = e.get("weight", 1.0) * meta_law["energy_bias"]
                    resonance = e.get("resonance_bias", 1.0) * meta_law["root_influence"] * g_mult
                    ascent = energy * resonance * meta_law["ascent_bias"]
                    s_num = ayah.get("surah_number", 0)
                    surah_stats[s_num]["energy"] += energy
                    surah_stats[s_num]["ascent"] += ascent
                    surah_stats[s_num]["name"] = ayah.get("surah_name", f"سورة {s_num}")
                    root_freq[root] += 1
        radar_df = pd.DataFrame([
            {"surah": k, "name": v["name"], "energy": round(v["energy"], 2), "ascent": round(v["ascent"], 2)}
            for k, v in surah_stats.items() if k > 0
        ])
        if radar_df.empty:
            radar_df = generate_sample_radar_data()
        if not root_freq:
            root_freq = generate_sample_root_frequency()
        st.session_state.cosmic_radar_data = radar_df
        st.session_state.root_frequency_data = root_freq
    except Exception:
        st.session_state.cosmic_radar_data = generate_sample_radar_data()
        st.session_state.root_frequency_data = generate_sample_root_frequency()

# ==============================================================================
# [17] محرك الحقن السيادي
# ==============================================================================
def initialize_sovereign_memory():
    lex_path = get_absolute_path("nibras_lexicon.json")
    r_idx, roots_list, orbit_cnt = load_lexicon_db(lex_path)
    q_data = load_quran_matrix()
    q_roots = load_quran_roots()
    if q_roots:
        for k, v in q_roots.items():
            if k not in r_idx:
                r_idx[k] = v
                roots_list.append(v)
    st.session_state.r_index = r_idx
    st.session_state.all_roots = roots_list
    st.session_state.quran_data = q_data
    st.session_state.orbit_counter = orbit_cnt
    for i, entry in enumerate(st.session_state.quran_data):
        entry['index'] = i
    if q_data:
        update_cosmic_radar(q_data, r_idx, st.session_state.active_meta_law)
    st.session_state.initialized = True

if not st.session_state.initialized or not st.session_state.all_roots:
    initialize_sovereign_memory()

# الشريط الجانبي
with st.sidebar:
    st.markdown("""
    <div style="width: 100%; text-align: center;">
        <h2 style="color:#4fc3f7;">🛡️ نبراس السيادي</h2>
        <p>الإصدار v65.0 - الميثاقي</p>
        <p>المستخدم: محمد</p>
    </div>
    ---
    """, unsafe_allow_html=True)
    st.sidebar.metric("قوة الإزاحة", round(st.session_state.active_meta_law.get("root_influence", 1.0), 3))
    if st.sidebar.button("♻️ إعادة الضبط الجذري"):
        reset_nibras_system()
        st.rerun()
    st.sidebar.markdown("---")
    st.sidebar.markdown("<p>خِت فِت.</p>", unsafe_allow_html=True)

# ==============================================================================
# [18] التبويبات الرئيسية (9 تبويبات كاملة)
# ==============================================================================
tab_titles = [
    "📖 النسخة القرآنية", "🔍 الاستنطاق المداري", "🛰️ الرادار السيادي",
    "⚖️ مولّد القوانين", "🌐 الواقع الفوقي", "🌌 الرنين الجيني",
    "📈 اللوحة الوجودية", "📜 البيان الختامي", "📡 الرنين السياقي"
]
tabs = st.tabs(tab_titles)

# ==============================================================================
# تبويب 0: النسخة القرآنية
# ==============================================================================
with tabs[0]:
    st.markdown("### 📖 استنطاق الآيات القرآنية (Q-Mode)")
    if not st.session_state.quran_data:
        st.error("🚨 ملف matrix_data.json غير موجود أو فارغ.")
    else:
        surah_map = {}
        for entry in st.session_state.quran_data:
            if entry['surah_number'] not in surah_map:
                surah_map[entry['surah_number']] = entry['surah_name']
        s_list = sorted(surah_map.keys())
        col1, col2 = st.columns(2)
        with col1:
            s_num = st.selectbox("📌 اختر السورة", s_list, format_func=lambda x: f"{x} - {surah_map[x]}", key="q_s_num")
        current_v = [d for d in st.session_state.quran_data if d['surah_number'] == s_num]
        with col2:
            v_obj = st.selectbox("📑 اختر الآية", current_v, format_func=lambda x: f"آية {x['ayah_number']}", key=f"q_v_sel_{s_num}")
        if v_obj:
            st.markdown(f"""
            <div style="text-align:center; padding:20px; border-right:5px solid #FFD700; background:rgba(255,255,255,0.05); font-size:1.8em; font-family:'Amiri'; margin-bottom:20px;">
                {v_obj["text"]}
            </div>
            """, unsafe_allow_html=True)
            if st.button("🚀 تحليل هذه الآية مباشرة", use_container_width=True, key=f"q_btn_{v_obj.get('index', hash(v_obj['text']))}"):
                st.session_state.current_text = v_obj['text']
                st.session_state.input_area = v_obj['text']
                bodies = calculate_orbits(v_obj['text'], st.session_state.r_index)
                if bodies:
                    st.session_state.orbit_bodies = bodies
                    st.session_state.orbit_active = True
                    st.session_state.last_processed_text = v_obj['text']
                    update_cosmic_radar(st.session_state.quran_data, st.session_state.r_index, st.session_state.active_meta_law)
                    st.success(f"✅ تم تحليل الآية بنجاح! ({len(bodies)} جذر)")
                    st.rerun()
                else:
                    st.error("⚠️ لم يتم العثور على جذور مطابقة.")

# ==============================================================================
# تبويب 1: الاستنطاق المداري
# ==============================================================================
with tabs[1]:
    st.markdown("### 🔍 المفاعل السيادي للاستنطاق المداري")
    current_display = st.session_state.get('input_area', '')
    if current_display:
        st.info(f"📝 النص الحالي: {current_display[:100]}..." if len(current_display) > 100 else f"📝 النص الحالي: {current_display}")
    input_text = st.text_area("النص محل الاستنطاق:", value=current_display, height=180, key="main_orbital_input")
    if input_text != st.session_state.input_area:
        st.session_state.input_area = input_text
        st.session_state.current_text = input_text
    col1, col2 = st.columns([3, 1])
    with col1:
        manual_btn = st.button("🚀 تفعيل المفاعل يدوياً", use_container_width=True)
    with col2:
        archive_btn = st.button("🏁 خِت فِت (ختم الجلسة)", use_container_width=True)
    if manual_btn:
        if input_text:
            bodies = calculate_orbits(input_text, st.session_state.r_index)
            if bodies:
                st.session_state.orbit_bodies = bodies
                st.session_state.orbit_active = True
                st.session_state.last_processed_text = input_text
                st.session_state.current_text = input_text
                update_cosmic_radar(st.session_state.quran_data, st.session_state.r_index, st.session_state.active_meta_law)
                st.success(f"✅ تم تحليل النص بنجاح! ({len(bodies)} جذر)")
                st.rerun()
            else:
                st.error("⚠️ لم يتم العثور على جذور مطابقة.")
        else:
            st.warning("⚠️ الرجاء إدخال نص للتحليل.")
    if st.session_state.orbit_active and st.session_state.orbit_bodies:
        display_orbital_results()
    elif not st.session_state.orbit_bodies:
        st.warning("⚠️ المفاعل بانتظار إشارة البدء من التبويب القرآني")
        if st.button("🔄 تنشيط يدوي للمفاعل", use_container_width=True):
            if st.session_state.input_area:
                bodies = calculate_orbits(st.session_state.input_area, st.session_state.r_index)
                if bodies:
                    st.session_state.orbit_bodies = bodies
                    st.session_state.orbit_active = True
                    st.rerun()
    if archive_btn:
        if st.session_state.orbit_active and st.session_state.orbit_bodies:
            ascent_score = compute_ascent_vector(st.session_state.orbit_bodies)
            if khit_fit_archive(st.session_state.orbit_bodies, ascent_score):
                st.success("🔒 تم تشفير الجلسة.")
                st.rerun()
        else:
            st.warning("⚠️ لا توجد بيانات لأرشفتها.")

# ==============================================================================
# تبويب 2: الرادار السيادي
# ==============================================================================
with tabs[2]:
    st.markdown("### 🛰️ رادار التموضع الوجودي")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("تأثير الجذر", f"{st.session_state.active_meta_law.get('root_influence', 1.0):.3f}")
    c2.metric("انحياز الطاقة", f"{st.session_state.active_meta_law.get('energy_bias', 1.0):.3f}")
    c3.metric("الاستراتيجية", st.session_state.get("current_strategy", "STANDARD"))
    c4.metric("عدد الدورات", len(st.session_state.system_log))
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        if st.button("🔁 تشغيل دورة واحدة", use_container_width=True):
            sovereign_autonomous_cycle()
            st.rerun()
    with col_b:
        if st.button("🔁🔁 تشغيل 5 دورات", use_container_width=True):
            for _ in range(5):
                sovereign_autonomous_cycle()
            st.rerun()
    with col_c:
        if st.button("🔁🔁🔁 تشغيل 10 دورات", use_container_width=True):
            for _ in range(10):
                sovereign_autonomous_cycle()
            st.rerun()
    df_log = normalize_system_log_for_df()
    if not df_log.empty and "cycle" in df_log.columns:
        df_valid = df_log.dropna(subset=["cycle", "new_influence"]).copy()
        if not df_valid.empty:
            fig = px.line(df_valid, x="cycle", y="new_influence", title="تطور تأثير الجذر", markers=True)
            fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("📊 لا توجد بيانات كافية لعرض الرسم البياني")
    else:
        st.info("📊 لا توجد دورات بعد. قم بتشغيل دورة واحدة لبدء الرصد")
    if st.session_state.cosmic_radar_data.empty:
        st.warning("⚠️ الرادار بانتظار نبض البيانات. قم بتحليل آية أولاً.")
    else:
        fig = px.scatter(st.session_state.cosmic_radar_data, x="energy", y="ascent", text="name", color="ascent", size="energy", hover_data=["surah"], height=500, color_continuous_scale="Tealrose")
        st.plotly_chart(fig, use_container_width=True)

# ==============================================================================
# تبويب 3: مولّد القوانين
# ==============================================================================
with tabs[3]:
    st.markdown("### ⚖️ محرك حقن القوانين")
    st.info(f"⚙️ القانون الحالي: قوة الإزاحة = {st.session_state.active_meta_law.get('root_influence', 1.0):.3f}")
    shift = st.select_slider("اختر معامل الإزاحة:", options=[1.02, 1.05, 1.10, 1.15, 1.20], value=1.05)
    if st.button("🚀 تفعيل القانون الجديد", key="activate_law_btn", use_container_width=True):
        new_influence = st.session_state.active_meta_law["root_influence"] * shift
        st.session_state.active_meta_law["root_influence"] = new_influence
        st.session_state.system_log.append({
            "step": len(st.session_state.system_log) + 1,
            "shift_value": shift,
            "new_influence": new_influence,
            "timestamp": pd.Timestamp.now().strftime("%H:%M:%S")
        })
        if st.session_state.get('current_text'):
            st.session_state.orbit_bodies = calculate_orbits(st.session_state.current_text, st.session_state.r_index)
            if st.session_state.orbit_bodies:
                st.session_state.orbit_active = True
                update_cosmic_radar(st.session_state.quran_data, st.session_state.r_index, st.session_state.active_meta_law)
        st.success(f"✅ تم حقن الإزاحة {shift}x وتحديث المدارات")
        st.rerun()
    st.markdown("#### التحكم اليدوي")
    new_root = st.number_input("تأثير الجذر", value=float(st.session_state.active_meta_law.get("root_influence", 1.0)), min_value=0.85, max_value=1.80, step=0.01)
    new_energy = st.number_input("انحياز الطاقة", value=float(st.session_state.active_meta_law.get("energy_bias", 1.0)), min_value=0.80, max_value=2.50, step=0.01)
    if st.button("تطبيق التغييرات", use_container_width=True):
        st.session_state.active_meta_law["root_influence"] = round(new_root, 4)
        st.session_state.active_meta_law["energy_bias"] = round(new_energy, 4)
        if st.session_state.get('current_text'):
            st.session_state.orbit_bodies = calculate_orbits(st.session_state.current_text, st.session_state.r_index)
            st.session_state.orbit_active = True
        st.rerun()
    with st.expander("📜 سجل القوانين"):
        if st.session_state.system_log:
            st.table(st.session_state.system_log[-10:])
        else:
            st.info("لا توجد سجلات بعد.")

# ==============================================================================
# تبويب 4: الواقع الفوقي
# ==============================================================================
with tabs[4]:
    st.markdown("## 🌐 محرك الواقع الفوقي")
    with st.expander("🧠 الوعي المصحح الاستراتيجي", expanded=False):
        current_strat = st.session_state.get("current_strategy", "STANDARD")
        st.markdown(f"**📍 نمط الاستراتيجية الحالي:** `{current_strat}`")
        if current_strat == "AGGRESSIVE":
            st.error("⚠️ النظام في حالة كبح شديد نتيجة تذبذب مرتفع.")
        elif current_strat == "EXPANSIVE":
            st.success("✨ النظام في حالة تمدد استراتيجي نتيجة استقرار مرتفع.")
        else:
            st.info("⚖️ النظام يعمل في الوضع القياسي المتوازن.")
    with st.expander("🛡️ حالة التثبيت الفائق (v65.0)", expanded=False):
        st.markdown(f"**Cooldown الحالي:** `{st.session_state.get('correction_cooldown', 2)}` دورة")
        st.markdown(f"**آخر دورة تصحيح:** `{st.session_state.get('last_correction_cycle', -9999)}`")
        snap = st.session_state.get("last_correction_snapshot", {})
        st.json({"root_influence": snap.get("root_influence"), "energy_bias": snap.get("energy_bias"), "strategy": snap.get("strategy")})
    st.markdown("---")
    st.markdown("### 📜 السجل التفصيلي للنظام")
    df_display = normalize_system_log_for_df()
    if not df_display.empty:
        cols_to_show = ["cycle", "old_influence", "new_influence", "energy_score", "strategy", "self_healed"]
        available_cols = [c for c in cols_to_show if c in df_display.columns]
        st.dataframe(df_display[available_cols], use_container_width=True)
    else:
        st.info("لا توجد سجلات بعد. قم بتشغيل دورات من تبويب الرادار.")
    if st.session_state.cosmic_radar_data.empty:
        st.warning("⚠️ الرادار بانتظار نبض البيانات.")
    else:
        top_surah = st.session_state.cosmic_radar_data.nlargest(1, "ascent").iloc[0] if not st.session_state.cosmic_radar_data.empty else None
        top_root = st.session_state.root_frequency_data.most_common(1)[0] if st.session_state.root_frequency_data else ("لا يوجد", 0)
        c1, c2, c3 = st.columns(3)
        c1.metric("السورة القائدة", top_surah["name"] if top_surah is not None else "—")
        c2.metric("الجذر المهيمن", f"{top_root[0]} ({top_root[1]})")
        c3.metric("مستوى الوعي", len(st.session_state.system_log))

# ==============================================================================
# تبويب 5: الرنين الجيني
# ==============================================================================
with tabs[5]:
    st.markdown("### 🌌 مصفوفة الرنين والاستحقاق المداري")
    cols = st.columns(4)
    for i, (code, info) in enumerate(GENE_STYLE.items()):
        if i < 4:
            cols[i].markdown(f"<div class='ultra-card' style='border-top-color:{info['color']}'><h2>{info['icon']}</h2><h3>{info['name']}</h3><p>{info['meaning']}</p></div>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### 📖 استنطاق جذر محدد")
    if st.session_state.r_index:
        root_keys = sorted(st.session_state.r_index.keys())
        selected_root = st.selectbox("اختر جذراً للاستنطاق:", options=root_keys)
        if st.button("🔍 استنطاق الجذر", use_container_width=True):
            target_data = st.session_state.r_index[selected_root]
            sig = signature_from_root(selected_root)
            dynamic_energy = compute_dynamic_energy(base_w=target_data.get('weight', 1.0), count=1, mode="direct", morph_rank=3, orbit_id=target_data.get('orbit_id', 0), root_sig=sig)
            final_gene = resolve_sovereign_gene(orbit_id=target_data.get('orbit_id', 0), morph_rank=3, root_sig=sig, base_energy=dynamic_energy)
            gene_info = GENE_STYLE.get(final_gene, GENE_STYLE['N'])
            base_info = GENE_STYLE.get(target_data.get('gene_base', 'N'), GENE_STYLE['N'])
            st.markdown(f"""
            <div class="insight-card">
                <b style="font-size:1.2em;">📌 الجذر: {target_data['root_raw']}</b><br>
                🧬 الجين القاعدي: {base_info['icon']} {base_info['name']}<br>
                🧬 الجين النهائي: {gene_info['icon']} {gene_info['name']}<br>
                🔄 المدار: {target_data['orbit']} (ID: {target_data.get('orbit_id', 0)})<br>
                ⚡ الوزن الأصلي: {target_data.get('weight', 1.0)}<br>
                ⚡ الطاقة الديناميكية: {dynamic_energy:.1f}<br>
                ✨ عامل الإشراق: {sig['n_factor']}<br>
                📍 التموضع: ({sig['x']}, {sig['y']})<br>
                <hr><p>🔮 {target_data['insight']}</p>
            </div>
            """, unsafe_allow_html=True)

# ==============================================================================
# تبويب 6: اللوحة الوجودية
# ==============================================================================
with tabs[6]:
    st.markdown("### 📈 التحليل الكمي للمدار")
    if st.session_state.orbit_active and st.session_state.orbit_bodies:
        df = pd.DataFrame(st.session_state.orbit_bodies)
        col1, col2 = st.columns(2)
        col1.plotly_chart(px.pie(df, names='gene', color='gene', color_discrete_map={g: GENE_STYLE[g]['color'] for g in GENE_STYLE}, hole=0.5, title="توزيع الجينات"))
        col2.plotly_chart(px.bar(df.groupby('gene').size().reset_index(name='count'), x='gene', y='count', color='gene', color_discrete_map={g: GENE_STYLE[g]['color'] for g in GENE_STYLE}, title="تعداد الأجسام"))
        st.plotly_chart(px.scatter(df, x='root', y='energy', color='gene', size='energy', color_discrete_map={g: GENE_STYLE[g]['color'] for g in GENE_STYLE}, title="خارطة الطاقة"))
    else:
        st.info("⚙️ انتظر تفعيل المفاعل.")

# ==============================================================================
# تبويب 7: البيان الختامي
# ==============================================================================
with tabs[7]:
    st.markdown("### 📜 البيان الختامي")
    if st.session_state.orbit_active and st.session_state.orbit_bodies:
        display_orbital_results()
    else:
        st.info("⚙️ انتظر تفعيل المفاعل.")

# ==============================================================================
# تبويب 8: الرنين السياقي
# ==============================================================================
with tabs[8]:
    st.markdown("### 📡 الرنين السياقي")
    if st.session_state.orbit_active and st.session_state.orbit_bodies:
        resonance_edges = build_resonance_network(st.session_state.orbit_bodies)
        if resonance_edges:
            st.dataframe(pd.DataFrame(resonance_edges), use_container_width=True)
            strongest = resonance_edges[0]
            st.success(f"✨ أقوى رابط: **{strongest['source']}** ⇄ **{strongest['target']}** | القوة: {strongest['strength']}")
        else:
            st.info("لا توجد روابط قوية.")
    else:
        st.info("⚙️ انتظر تفعيل المفاعل.")

# ==============================================================================
# نهاية الكود - الإصدار v65.0 النهائي
# ==============================================================================
