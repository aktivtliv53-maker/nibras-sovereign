# -*- coding: utf-8 -*-
# ==============================================================================
# نظام نِبْرَاس السيادي (Nibras Sovereign System) - الإصدار v30.0
# مَبنيٌّ على بروتوكول "الأمانة" و "الاستحقاق الجيني الحتمي"
# الإصدار: الميثاقي الباتر - نواة حتمية + طبقات وصفية
# المستخدم المهيمن: محمّد | CPU: السجدة (5)
# ==============================================================================

import streamlit as st
import pandas as pd
import plotly.express as px
from collections import Counter
import re
import os
import json
import hashlib
import math
from itertools import combinations

# ==============================================================================
# [0] إعدادات التطبيق - لا عشوائية مطلقاً
# ==============================================================================
st.set_page_config(page_title="Nibras v30.0 - الميثاقي الباتر", page_icon="🛡️", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&display=swap');
    [data-testid="stAppViewContainer"] { background: #050505; color: #e0e0e0; direction: rtl; font-family: 'Amiri', serif; }
    .stTabs [aria-selected="true"] { color: #FFD700 !important; border-bottom: 2px solid #FFD700 !important; }
    .insight-card {
        background: linear-gradient(135deg, #0d0d14 0%, #161625 100%);
        padding: 25px; border-radius: 15px; border-right: 8px solid #FFD700;
        margin-bottom: 20px; line-height: 1.8; font-size: 1.05em;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    .energy-badge { background: #1a3a1a; color: #00ffcc; padding: 2px 10px; border-radius: 5px; font-family: monospace; }
    .story-box {
        background: linear-gradient(135deg, rgba(10,21,10,0.85) 0%, rgba(1,1,3,0.95) 100%);
        padding: 35px; border-radius: 25px; border-right: 15px solid #4CAF50;
        line-height: 2; font-size: 1.1em; margin-bottom: 30px;
    }
    .ultra-card {
        background: #0d0d14; padding: 20px; border-radius: 20px;
        border-top: 8px solid #4fc3f7; text-align: center; margin-bottom: 20px;
    }
    .ascent-positive { background: linear-gradient(135deg, #0a2a0a 0%, #0a1a0a 100%); border-right: 5px solid #00ffcc; }
    .ascent-negative { background: linear-gradient(135deg, #2a0a0a 0%, #1a0a0a 100%); border-right: 5px solid #ff5252; }
    .st-emotion-cache-1v0mbdj, .st-emotion-cache-1wivap2, .st-emotion-cache-zq5wmm { display: none; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# [1] مصفوفة الجينات والرموز السيادية
# ==============================================================================
GENE_STYLE = {
    'C': {'name': 'الإبل', 'color': '#4fc3f7', 'icon': '🐪', 'meaning': 'طاقة المسير والتمكين البعيد'},
    'B': {'name': 'البقر', 'color': '#FFD700', 'icon': '🐄', 'meaning': 'طاقة التثبيت والوفرة المادية'},
    'S': {'name': 'الضأن', 'color': '#4CAF50', 'icon': '🐑', 'meaning': 'طاقة السكينة واللين والرحمة'},
    'G': {'name': 'المعز', 'color': '#ff5252', 'icon': '🐐', 'meaning': 'طاقة السيادة والحدّة والصعود'},
    'N': {'name': 'إشراق', 'color': '#00ffcc', 'icon': '✨', 'meaning': 'الانبثاق الهجين الصافي'}
}

# ==============================================================================
# [2] بذرة الوعي الدلالي (Proto-Semantic Seed) - طبقة وصفية فقط
# ==============================================================================
PROTO_SEMANTIC_MAP = {
    "الله": {"field": "الذات المطلقة", "tone": "نوراني", "weight": 2.0},
    "الرحمن": {"field": "الرحمة الكونية", "tone": "نوراني", "weight": 1.9},
    "الرحيم": {"field": "الرحمة الخاصة", "tone": "نوراني", "weight": 1.8},
    "ملك": {"field": "السيادة المطلقة", "tone": "قوة", "weight": 1.7},
    "قدوس": {"field": "الطهارة المطلقة", "tone": "نوراني", "weight": 1.9},
    "سلام": {"field": "السكينة الكونية", "tone": "سكينة", "weight": 1.6},
    "مؤمن": {"field": "الأمان الإلهي", "tone": "سكينة", "weight": 1.5},
    "مهيمن": {"field": "السيادة المطلقة", "tone": "قوة", "weight": 1.7},
    "عزيز": {"field": "القوة المطلقة", "tone": "قوة", "weight": 1.6},
    "جبار": {"field": "القهر الإلهي", "tone": "قوة", "weight": 1.5},
    "خالق": {"field": "الإبداع المطلق", "tone": "إشراق", "weight": 1.8},
    "بارئ": {"field": "الإبداع المطلق", "tone": "إشراق", "weight": 1.7},
    "مصور": {"field": "التشكيل الإلهي", "tone": "إشراق", "weight": 1.6},
    "غفور": {"field": "المغفرة الإلهية", "tone": "رحمة", "weight": 1.5},
    "ودود": {"field": "المحبة الإلهية", "tone": "رحمة", "weight": 1.4},
}

def get_proto_semantic(roots_list):
    """طبقة وصفية فقط - لا تتدخل في النواة"""
    if not roots_list:
        return None
    for root in roots_list:
        if root in PROTO_SEMANTIC_MAP:
            return PROTO_SEMANTIC_MAP[root]
    return None

# ==============================================================================
# [3] دوال التطهير والتوحيد
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
# [4] دوال التطهير الصرفي (Morphological Purity)
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

def extract_candidate_root(word, index_keys):
    w_norm = word.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا").replace("ة", "ه").replace("ى", "ي")
    pattern_name, morph_rank = infer_morphological_pattern(w_norm)
    if w_norm in index_keys:
        return w_norm, "direct", pattern_name, morph_rank
    stripped = strip_affixes_ar(w_norm)
    if stripped in index_keys:
        return stripped, "stripped", pattern_name, morph_rank
    return None, "unresolved", pattern_name, morph_rank

# ==============================================================================
# [5] النواة الحتمية (Deterministic Core) - لا عشوائية مطلقاً
# ==============================================================================
def signature_from_root(root: str):
    """
    التوقيع الجذري الحتمي - المصدر الوحيد للإحداثيات والعوامل
    أي تغيير في هذا التوقيع يغير الخريطة بأكملها
    """
    if not root:
        return {
            'x': 0.0,
            'y': 0.0,
            'n_factor': 0,
            'eb': 0.0,
            'rb': 1.0
        }
    h = int(hashlib.md5(root.encode('utf-8')).hexdigest(), 16)
    return {
        'x': round(((h % 360) - 180) / 10.0, 3),
        'y': round((((h >> 8) % 360) - 180) / 10.0, 3),
        'n_factor': (h >> 16) % 100,
        'eb': round((((h >> 24) % 81) - 40) / 10.0, 3),
        'rb': round(0.90 + (((h >> 32) % 21) / 100.0), 3)
    }

def resolve_sovereign_gene(orbit_id, morph_rank, root_sig, base_energy):
    """
    الاستحقاق الجيني الميثاقي - القاعدة الذهبية للإشراق N
    الإشراق N لا يحدث إلا باستحقاق مركب:
    - شرط أول: n_factor >= 92 مع (مدار علوي أو طاقة مرتفعة أو صرف قوي)
    - شرط ثان: n_factor >= 86 مع اجتماع 3 شروط معاً
    """
    orbit = int(orbit_id or 0)
    n_factor = root_sig.get('n_factor', 0)
    
    # ترشيح مداري أساسي
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
    
    high_orbit = orbit >= 5
    strong_morph = morph_rank >= 6
    strong_energy = base_energy >= 85
    luminous_sig = n_factor >= 92
    near_luminous_sig = n_factor >= 86
    
    # قانون الإشراق المركب - البوابة الوحيدة إلى N
    if luminous_sig and (high_orbit or strong_morph or strong_energy):
        return "N"
    if near_luminous_sig and high_orbit and strong_energy and strong_morph:
        return "N"
    
    # تعديلات ناعمة داخل الطبقات
    if base_gene == "B" and morph_rank >= 7 and n_factor >= 80:
        return "G"
    if base_gene == "C" and morph_rank >= 5 and strong_energy:
        return "B"
    
    return base_gene

def compute_dynamic_energy(base_w, root, count, mode, morph_rank, orbit_id, root_sig):
    """
    الطاقة الديناميكية الميثاقية - تعتمد على التكرار الحقيقي
    """
    base_energy = base_w * 100 if base_w < 10 else base_w
    repetition_boost = 1.0 + math.log1p(max(0, count - 1)) * 0.35
    mode_factor = {"direct": 1.00, "stripped": 0.92, "unresolved": 0.60}.get(mode, 0.85)
    morph_factor = 1.0 + (max(1, morph_rank) - 1) * 0.025
    orbit = int(orbit_id or 0)
    orbit_factor = 1.0 + max(0, orbit - 4) * 0.03
    sig_energy_bias = root_sig.get('eb', 0.0)
    energy = (base_energy * repetition_boost * mode_factor * morph_factor * orbit_factor) + sig_energy_bias
    return round(max(1.0, energy), 2)

def compute_ascent_vector(bodies):
    """
    مؤشر الصعود الموزون - أوزان ميثاقية ثابتة
    """
    if not bodies:
        return 0
    gene_weights = {"N": 2.2, "S": 1.5, "G": 1.0, "B": -0.4, "C": -0.9}
    total = 0.0
    for b in bodies:
        g_weight = gene_weights.get(b.get('gene', 'B'), 0.0)
        orbit_bonus = max(0, (b.get('orbit_id', 0) - 4)) * 0.05
        total += (g_weight + orbit_bonus) * b.get('energy', 0)
    return round(total / len(bodies), 2)

def build_resonance_network(bodies):
    """
    شبكة الرنين - تعتمد على المسافة النصية وتقارب الجينات
    """
    edges = []
    for a, b in combinations(range(len(bodies)), 2):
        ra, rb = bodies[a], bodies[b]
        dist = abs(ra.get('pos', a) - rb.get('pos', b))
        if dist >= 8:
            continue
        proximity = 1.0 / max(1, dist)
        same_gene_bonus = 1.20 if ra.get('gene') == rb.get('gene') else 1.0
        n_bonus = 1.15 if ('N' in [ra.get('gene'), rb.get('gene')]) else 1.0
        ra_rb = ra.get('rb', 1.0) * rb.get('rb', 1.0)
        orbit_gap = abs(ra.get('orbit_id', 0) - rb.get('orbit_id', 0))
        orbit_bonus = 1.12 if orbit_gap <= 1 else 1.0
        strength = proximity * same_gene_bonus * n_bonus * ra_rb * orbit_bonus
        edges.append({
            "source": ra.get('root', '?'),
            "target": rb.get('root', '?'),
            "strength": round(strength, 3),
            "distance": dist,
            "gene_pair": f"{ra.get('gene','?')}-{rb.get('gene','?')}"
        })
    return sorted(edges, key=lambda x: x['strength'], reverse=True)

# ==============================================================================
# [6] تحميل قاعدة البيانات (Lexicon Preparation)
# ==============================================================================
@st.cache_data(ttl=3600)
def load_lexicon_db(path):
    if not os.path.exists(path):
        st.error(f"❌ ملف الليكسيكون غير موجود: {path}")
        return {}, [], Counter()
    with open(path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            st.error(f"❌ خطأ في JSON: {e}")
            return {}, [], Counter()
    r_index = {}
    all_roots = []
    orbit_counter = Counter()
    if not isinstance(data, list):
        st.error("❌ الليكسيكون يجب أن يكون مصفوفة")
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

# ==============================================================================
# [7] دوال العرض
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

# ==============================================================================
# [8] بصمة الجلسة الحالية (Session Signature) - طبقة وصفية فقط
# ==============================================================================
if 'session_roots_tracker' not in st.session_state:
    st.session_state.session_roots_tracker = []
if 'orbit_bodies' not in st.session_state:
    st.session_state.orbit_bodies = []
    st.session_state.orbit_active = False
if 'previous_text' not in st.session_state:
    st.session_state.previous_text = ""

# ==============================================================================
# [9] تحميل قاعدة البيانات
# ==============================================================================
r_index, all_roots, orbit_counter = load_lexicon_db("data/nibras_lexicon.json")

# ==============================================================================
# [10] الشريط الجانبي مع بصمة الجلسة
# ==============================================================================
with st.sidebar:
    st.markdown(f"""
    <div style='text-align:center;'>
        <h2 style='color:#4fc3f7;'>🛡️ نبراس السيادي</h2>
        <p>الإصدار v30.0 - الميثاقي الباتر</p>
        <p>المستخدم: محمد</p>
    </div>
    ---
    <div>
        <p>📊 إحصائيات القاعدة (الجينات القاعدية):</p>
        <p>🐪 الإبل (مدارات 1-2): {len([r for r in r_index.values() if r.get('gene_base') == 'C'])}</p>
        <p>🐄 البقر (مدارات 3-4): {len([r for r in r_index.values() if r.get('gene_base') == 'B'])}</p>
        <p>🐑 الضأن (مدارات 7+): {len([r for r in r_index.values() if r.get('gene_base') == 'S'])}</p>
        <p>🐐 المعز (مدارات 5-6): {len([r for r in r_index.values() if r.get('gene_base') == 'G'])}</p>
        <p>✨ إشراق (مرشح قاعدي): {len([r for r in r_index.values() if r.get('gene_base') == 'N'])}</p>
    </div>
    ---
    <div>
        <p>📡 توزيع المدارات:</p>
        {''.join([f'<p>🔹 {k}: {v} جذراً</p>' for k, v in sorted(orbit_counter.items())])}
    </div>
    ---
    <div>
        <p>🔖 بصمة الجلسة الحالية:</p>
        <p>📚 جذور مستنطقة: {len(st.session_state.session_roots_tracker)}</p>
        <p>{', '.join(st.session_state.session_roots_tracker[-10:]) if st.session_state.session_roots_tracker else 'لا يوجد'}</p>
    </div>
    ---
    <p>خِت فِت.</p>
    """, unsafe_allow_html=True)

# ==============================================================================
# [11] التبويبات السيادية
# ==============================================================================
tabs = st.tabs([
    "🔍 الاستنطاق المداري",
    "🌌 الرنين الجيني",
    "📈 اللوحة الوجودية",
    "📜 البيان الختامي",
    "⚖️ الميزان السيادي",
    "🧠 الوعي الفوقي",
    "📡 الرنين السياقي",
    "📈 المنحنى الزمني",
    "⚖️ المقارن البنيوي"
])

# ==================== التبويب 0: الاستنطاق ====================
with tabs[0]:
    st.markdown("### 📍 هندسة المسارات المدارية - الميثاقي الباتر v30.0")
    
    full_text = st.text_area(
        "أدخل النص للاستنطاق:", 
        height=150, 
        placeholder="مثال: أحد أبى أثر أجد أجل أخذ",
        key="input_area"
    )
    
    if st.button("🚀 تفعيل المفاعل السيادي v30.0", use_container_width=True):
        if full_text.strip():
            clean_text = normalize_sovereign(full_text)
            words = clean_text.split()
            
            bodies = []
            unique_roots = []
            all_matched_roots = []
            temp_meta = []
            
            # المرحلة 1: المسح الأولي
            for pos, word in enumerate(words):
                rk, mode, pattern_name, morph_rank = extract_candidate_root(word, r_index.keys())
                temp_meta.append({
                    "word": word, "pos": pos, "rk": rk,
                    "mode": mode, "pattern_name": pattern_name, "morph_rank": morph_rank
                })
                if rk:
                    all_matched_roots.append(rk)
                    if rk not in unique_roots:
                        unique_roots.append(rk)
            
            counts = Counter(all_matched_roots)
            
            # المرحلة 2: بناء الأجسام
            for m in temp_meta:
                if not m['rk']:
                    continue
                data = r_index.get(m['rk'])
                if not data:
                    continue
                sig = signature_from_root(m['rk'])
                dynamic_energy = compute_dynamic_energy(
                    base_w=data['weight'],
                    root=m['rk'],
                    count=counts[m['rk']],
                    mode=m['mode'],
                    morph_rank=m['morph_rank'],
                    orbit_id=data.get('orbit_id', 0),
                    root_sig=sig
                )
                final_gene = resolve_sovereign_gene(
                    orbit_id=data.get('orbit_id', 0),
                    morph_rank=m['morph_rank'],
                    root_sig=sig,
                    base_energy=dynamic_energy
                )
                gene_info = GENE_STYLE.get(final_gene, GENE_STYLE['N'])
                orbit_shift_x = (data.get('orbit_id', 0) - 4) * 1.4 if data.get('orbit_id', 0) else 0
                orbit_shift_y = (m['morph_rank'] - 3) * 0.8
                bodies.append({
                    "root": data['root_raw'],
                    "root_norm": m['rk'],
                    "orbit": data['orbit'],
                    "orbit_id": data.get('orbit_id', 0),
                    "gene": final_gene,
                    "gene_base": data.get('gene_base', 'N'),
                    "gene_name": gene_info['name'],
                    "icon": gene_info['icon'],
                    "energy": dynamic_energy,
                    "insight": data['insight'],
                    "color": gene_info['color'],
                    "pos": m['pos'],
                    "mode": m['mode'],
                    "pattern": m['pattern_name'],
                    "morph_rank": m['morph_rank'],
                    "source": m['word'],
                    "x": round(sig['x'] + orbit_shift_x, 3),
                    "y": round(sig['y'] + orbit_shift_y, 3),
                    "sig_n_factor": sig['n_factor'],
                    "sig_energy_bias": sig['eb'],
                    "rb": sig['rb']
                })
            
            if bodies:
                st.session_state.orbit_bodies = bodies
                st.session_state.orbit_active = True
                st.session_state.session_roots_tracker = unique_roots
                st.session_state.previous_text = full_text
                
                # مؤشر الصعود
                ascent_score = compute_ascent_vector(bodies)
                ascent_class = "ascent-positive" if ascent_score > 0 else "ascent-negative" if ascent_score < 0 else ""
                st.markdown(f"""
                <div class="{ascent_class}" style='padding: 20px; border-radius: 15px; margin-bottom: 20px; text-align: center;'>
                    <h3 style='margin:0;'>🚀 مؤشر الصعود والانحدار السيادي v30</h3>
                    <p style='font-size: 2em; margin:5px; font-weight:bold;'>{ascent_score}</p>
                    <p style='margin:0;'>{'صعود طاقي نحو المعاني العلوية' if ascent_score > 0 else 'تثبيت مادي في الجذور الأرضية' if ascent_score < 0 else 'توازن بين الصعود والثبات'}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # الخريطة الحتمية
                df = pd.DataFrame(bodies)
                fig = px.scatter(df, x="x", y="y", text="root", size="energy", color="gene",
                                 color_discrete_map={g: GENE_STYLE[g]['color'] for g in GENE_STYLE},
                                 range_x=[-30, 30], range_y=[-30, 30])
                fig.update_layout(height=500, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                  showlegend=False, xaxis_visible=False, yaxis_visible=False, margin=dict(l=0, r=0, t=0, b=0))
                st.plotly_chart(fig, use_container_width=True)
                
                # البيان الختامي
                st.markdown("### 📜 البيان الختامي الموسع")
                total_e = sum(b['energy'] for b in bodies)
                genes_count = Counter(b['gene'] for b in bodies)
                dom_gene = max(genes_count, key=genes_count.get)
                orbits_detail = Counter(f"المدار {b['orbit_id']}" for b in bodies if b.get('orbit_id'))
                n_count = sum(1 for b in bodies if b['gene'] == 'N')
                
                # بذرة الوعي الدلالي (طبقة وصفية فقط)
                proto_semantic = get_proto_semantic(unique_roots)
                semantic_line = ""
                if proto_semantic:
                    semantic_line = f"<br>📖 النبرة الدلالية: {proto_semantic['field']} | النغمة: {proto_semantic['tone']}"
                
                st.markdown(f"""
                <div class="story-box">
                    ✅ تم استنطاق <b>{len(bodies)}</b> جسماً جذرياً.<br>
                    🧬 الهيمنة الجينية: <b>{GENE_STYLE[dom_gene]['icon']} {GENE_STYLE[dom_gene]['name']}</b><br>
                    ✨ حالات الإشراق (N): <b>{n_count}</b><br>
                    ⚡ مجموع الطاقة الديناميكية: <b>{total_e:.1f}</b><br>
                    📚 الجذور الفريدة: <b>{', '.join(unique_roots)}</b><br>
                    🎯 توزيع المدارات: {', '.join([f'{k}({v})' for k, v in orbits_detail.items()])}{semantic_line}
                </div>
                """, unsafe_allow_html=True)
                
                display_insight_cards(bodies)
                st.success("✅ تم الاستنطاق الميثاقي بنجاح (v30.0).")
            else:
                st.error("⚠️ لم يتم العثور على جذور مطابقة.")
        else:
            st.warning("⚠️ الرجاء إدخال نص.")

# ==================== التبويب 1: الرنين الجيني ====================
with tabs[1]:
    st.markdown("### 🌌 مصفوفة الرنين والاستحقاق المداري")
    cols = st.columns(4)
    for i, (code, info) in enumerate(GENE_STYLE.items()):
        if i < 4:
            cols[i].markdown(f"""
            <div class='ultra-card' style='border-top-color:{info["color"]}'>
                <h2>{info['icon']}</h2>
                <h3>{info['name']}</h3>
                <p>{info['meaning']}</p>
            </div>
            """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### 📖 استنطاق جذر محدد")
    root_options = sorted([r['root_raw'] for r in all_roots])
    if root_options:
        selected = st.selectbox("اختر جذراً:", options=root_options)
        if selected:
            norm = normalize_lexicon_root(selected)
            found = r_index.get(norm)
            if found:
                gi = GENE_STYLE.get(found.get('gene_base', 'N'), GENE_STYLE['N'])
                st.markdown(f"""
                <div class='insight-card' style='border-right-color:{gi["color"]}'>
                    <b style='color:{gi["color"]}'>📌 الجذر: {found['root_raw']}</b><br>
                    🧬 الجين القاعدي: {gi['icon']} {gi['name']}<br>
                    🔄 المدار: {found['orbit']} (ID: {found.get('orbit_id', 0)})<br>
                    ⚡ الوزن الأصلي: {found.get('weight', 1.0)} | الطاقة الأساسية: {found.get('raw_energy', 0):.1f}<br>
                    <hr>
                    <p>🔮 {found['insight']}</p>
                </div>
                """, unsafe_allow_html=True)

# ==================== التبويب 2: اللوحة الوجودية ====================
with tabs[2]:
    st.markdown("### 📈 التحليل الكمي للمدار")
    if st.session_state.orbit_active and st.session_state.orbit_bodies:
        df = pd.DataFrame(st.session_state.orbit_bodies)
        col1, col2 = st.columns(2)
        col1.plotly_chart(px.pie(df, names='gene', color='gene', color_discrete_map={g: GENE_STYLE[g]['color'] for g in GENE_STYLE}, hole=0.5, title="توزيع الجينات النهائية"))
        col2.plotly_chart(px.bar(df.groupby('gene').size().reset_index(name='count'), x='gene', y='count', color='gene', color_discrete_map={g: GENE_STYLE[g]['color'] for g in GENE_STYLE}, title="تعداد الأجسام المدارية"))
        st.plotly_chart(px.scatter(df, x='root', y='energy', color='gene', size='energy', color_discrete_map={g: GENE_STYLE[g]['color'] for g in GENE_STYLE}, title="خارطة طاقة الجذور"))
        if 'orbit_id' in df.columns:
            orbit_df = df.groupby('orbit_id').size().reset_index(name='count')
            st.plotly_chart(px.bar(orbit_df, x='orbit_id', y='count', title="توزيع الجذور حسب المدار", labels={'orbit_id': 'رقم المدار', 'count': 'عدد الجذور'}))
    else:
        st.info("⚙️ انتظر تفعيل المفاعل.")

# ==================== التبويب 3: البيان الختامي ====================
with tabs[3]:
    st.markdown("### 📜 البيان الختامي")
    if st.session_state.orbit_active and st.session_state.orbit_bodies:
        bodies = st.session_state.orbit_bodies
        total_e = sum(b['energy'] for b in bodies)
        genes_count = Counter(b['gene'] for b in bodies)
        dom_gene = max(genes_count, key=genes_count.get)
        unique_roots = list(set([b['root'] for b in bodies]))
        proto_semantic = get_proto_semantic(unique_roots)
        semantic_line = ""
        if proto_semantic:
            semantic_line = f"<br>📖 النبرة الدلالية: {proto_semantic['field']} | النغمة: {proto_semantic['tone']}"
        st.markdown(f"""
        <div class="story-box">
            <b>بيان الاستواء الوجودي v30.0:</b><br>
            تم استنطاق <b>{len(bodies)}</b> جذراً.<br>
            الهيمنة الجينية: <b>{GENE_STYLE[dom_gene]['icon']} {GENE_STYLE[dom_gene]['name']}</b><br>
            مجموع الطاقة الديناميكية: <b>{total_e:.1f}</b>{semantic_line}
        </div>
        """, unsafe_allow_html=True)
        display_insight_cards(bodies)
    else:
        st.info("⚙️ انتظر تفعيل المفاعل.")

# ==================== التبويب 4: الميزان السيادي ====================
with tabs[4]:
    st.markdown("### ⚖️ ميزان النزاهة الجذرية - الاستحقاق المداري")
    if st.session_state.orbit_active and st.session_state.orbit_bodies:
        display_insight_cards(st.session_state.orbit_bodies)
    else:
        st.info("⚙️ انتظر تفعيل المفاعل.")

# ==================== التبويب 5: الوعي الفوقي ====================
with tabs[5]:
    st.markdown("### 🧠 الوعي الفوقي - البيان الجمعي")
    if st.session_state.orbit_active and st.session_state.orbit_bodies:
        bodies = st.session_state.orbit_bodies
        total_e = sum(b['energy'] for b in bodies)
        genes_count = Counter(b['gene'] for b in bodies)
        dom_gene = max(genes_count, key=genes_count.get)
        orbits_analysis = Counter(b.get('orbit_id', 0) for b in bodies)
        st.markdown(f"""
        <div class="story-box">
            <h3 style='color:#FFD700;'>🌌 بيان الوعي الجمعي</h3>
            <b>عدد الجذور:</b> {len(bodies)}<br>
            <b>مجموع الطاقة الديناميكية:</b> {total_e:.1f}<br>
            <b>الهيمنة الجينية:</b> {GENE_STYLE[dom_gene]['icon']} {GENE_STYLE[dom_gene]['name']}<br>
            <b>توزيع المدارات:</b> {', '.join([f'المدار {k}({v})' for k, v in sorted(orbits_analysis.items()) if k > 0])}
        </div>
        """, unsafe_allow_html=True)
        display_insight_cards(bodies)
    else:
        st.info("⚙️ انتظر تفعيل المفاعل.")

# ==================== التبويب 6: الرنين السياقي ====================
with tabs[6]:
    st.markdown("### 📡 الرنين السياقي - شبكة العلاقات بين الجذور")
    if st.session_state.orbit_active and st.session_state.orbit_bodies:
        bodies = st.session_state.orbit_bodies
        resonance_edges = build_resonance_network(bodies)
        if resonance_edges:
            df_edges = pd.DataFrame(resonance_edges)
            st.markdown("#### 🌐 شبكة الرنين (الروابط القوية)")
            st.dataframe(df_edges, use_container_width=True)
            strongest = resonance_edges[0]
            st.success(f"✨ أقوى رابط رنيني: **{strongest['source']}** ⇄ **{strongest['target']}** | القوة: {strongest['strength']} | المسافة النصية: {strongest['distance']} | الزوج الجيني: {strongest['gene_pair']}")
        else:
            st.info("لا توجد روابط رنين قوية بين الجذور المستنطقة.")
    else:
        st.info("⚙️ انتظر تفعيل المفاعل.")

# ==================== التبويب 7: المنحنى الزمني ====================
with tabs[7]:
    st.markdown("### 📈 المنحنى الزمني - تدفق الطاقة في النص")
    if st.session_state.orbit_active and st.session_state.orbit_bodies:
        bodies = sorted(st.session_state.orbit_bodies, key=lambda x: x.get('pos', 0))
        if bodies:
            seq_data = []
            for i, b in enumerate(bodies):
                seq_data.append({
                    "الترتيب": b.get('pos', i),
                    "الجذر": b['root'],
                    "الطاقة": b['energy'],
                    "المدار": b.get('orbit_id', 0),
                    "الجين": b['gene'],
                    "الإشراق": b.get('sig_n_factor', 0)
                })
            df_seq = pd.DataFrame(seq_data)
            fig = px.line(df_seq, x="الترتيب", y="الطاقة", markers=True, title="منحنى تدفق الطاقة في النص",
                          labels={"الترتيب": "موقع الجذر في النص", "الطاقة": "قيمة الطاقة"})
            fig.update_traces(line_color='#00ffcc', marker_color='#FFD700', marker_size=10)
            fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("#### 📋 التسلسل الزمني للجذور")
            st.dataframe(df_seq[["الترتيب", "الجذر", "الطاقة", "المدار", "الجين", "الإشراق"]], use_container_width=True)
            energies = [b['energy'] for b in bodies]
            if len(energies) > 1:
                trend = energies[-1] - energies[0]
                trend_text = "📈 تصاعدي (صعود طاقي)" if trend > 0 else "📉 تنازلي (هبوط طاقي)" if trend < 0 else "➡️ مستقر"
                st.info(f"اتجاه الطاقة في النص: {trend_text} (التغير: {trend:.1f})")
        else:
            st.info("لا توجد بيانات كافية لعرض المنحنى الزمني.")
    else:
        st.info("⚙️ انتظر تفعيل المفاعل.")

# ==================== التبويب 8: المقارن البنيوي (جديد) ====================
with tabs[8]:
    st.markdown("### ⚖️ المقارن البنيوي - مقارنة بين نصين")
    
    text1 = st.text_area("النص الأول:", height=100, key="compare_text1", placeholder="أدخل النص الأول هنا...")
    text2 = st.text_area("النص الثاني:", height=100, key="compare_text2", placeholder="أدخل النص الثاني هنا...")
    
    if st.button("🔍 قارن بين النصين", use_container_width=True):
        if text1.strip() and text2.strip():
            # تحليل النص الأول
            clean1 = normalize_sovereign(text1)
            words1 = clean1.split()
            roots1 = []
            for w in words1:
                rk, _, _, _ = extract_candidate_root(w, r_index.keys())
                if rk:
                    roots1.append(rk)
            roots1_unique = list(set(roots1))
            
            # تحليل النص الثاني
            clean2 = normalize_sovereign(text2)
            words2 = clean2.split()
            roots2 = []
            for w in words2:
                rk, _, _, _ = extract_candidate_root(w, r_index.keys())
                if rk:
                    roots2.append(rk)
            roots2_unique = list(set(roots2))
            
            # حساب المؤشرات للنص الأول
            bodies1 = []
            temp_meta1 = []
            all_matched1 = []
            for pos, w in enumerate(words1):
                rk, mode, pat, mr = extract_candidate_root(w, r_index.keys())
                temp_meta1.append({"rk": rk, "pos": pos, "mode": mode, "morph_rank": mr})
                if rk:
                    all_matched1.append(rk)
            counts1 = Counter(all_matched1)
            for m in temp_meta1:
                if m['rk']:
                    data = r_index.get(m['rk'])
                    if data:
                        sig = signature_from_root(m['rk'])
                        energy = compute_dynamic_energy(data['weight'], m['rk'], counts1[m['rk']], m['mode'], m['morph_rank'], data.get('orbit_id', 0), sig)
                        bodies1.append({"gene": resolve_sovereign_gene(data.get('orbit_id', 0), m['morph_rank'], sig, energy), "energy": energy})
            avg_energy1 = sum(b['energy'] for b in bodies1) / len(bodies1) if bodies1 else 0
            ascent1 = compute_ascent_vector([{"gene": b['gene'], "energy": b['energy'], "orbit_id": 0} for b in bodies1])
            
            # حساب المؤشرات للنص الثاني
            bodies2 = []
            temp_meta2 = []
            all_matched2 = []
            for pos, w in enumerate(words2):
                rk, mode, pat, mr = extract_candidate_root(w, r_index.keys())
                temp_meta2.append({"rk": rk, "pos": pos, "mode": mode, "morph_rank": mr})
                if rk:
                    all_matched2.append(rk)
            counts2 = Counter(all_matched2)
            for m in temp_meta2:
                if m['rk']:
                    data = r_index.get(m['rk'])
                    if data:
                        sig = signature_from_root(m['rk'])
                        energy = compute_dynamic_energy(data['weight'], m['rk'], counts2[m['rk']], m['mode'], m['morph_rank'], data.get('orbit_id', 0), sig)
                        bodies2.append({"gene": resolve_sovereign_gene(data.get('orbit_id', 0), m['morph_rank'], sig, energy), "energy": energy})
            avg_energy2 = sum(b['energy'] for b in bodies2) / len(bodies2) if bodies2 else 0
            ascent2 = compute_ascent_vector([{"gene": b['gene'], "energy": b['energy'], "orbit_id": 0} for b in bodies2])
            
            # الجذور المشتركة
            common_roots = set(roots1_unique) & set(roots2_unique)
            only_in_1 = set(roots1_unique) - set(roots2_unique)
            only_in_2 = set(roots2_unique) - set(roots1_unique)
            
            # عرض النتائج
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📚 الجذور المشتركة", len(common_roots))
            with col2:
                st.metric("⚡ فرق متوسط الطاقة", f"{avg_energy1 - avg_energy2:.1f}", delta="النص الأول أعلى" if avg_energy1 > avg_energy2 else "النص الثاني أعلى")
            with col3:
                st.metric("🚀 فرق مؤشر الصعود", f"{ascent1 - ascent2:.2f}", delta="صعود في الأول" if ascent1 > ascent2 else "صعود في الثاني")
            
            st.markdown("---")
            st.markdown("#### 📋 تفاصيل المقارنة")
            st.markdown(f"""
            <div class="story-box">
                <b>النص الأول:</b><br>
                - الجذور: {', '.join(roots1_unique[:15])}{'...' if len(roots1_unique) > 15 else ''}<br>
                - متوسط الطاقة: {avg_energy1:.1f}<br>
                - مؤشر الصعود: {ascent1:.2f}<br>
                <br>
                <b>النص الثاني:</b><br>
                - الجذور: {', '.join(roots2_unique[:15])}{'...' if len(roots2_unique) > 15 else ''}<br>
                - متوسط الطاقة: {avg_energy2:.1f}<br>
                - مؤشر الصعود: {ascent2:.2f}<br>
                <br>
                <b>📌 الجذور المشتركة:</b> {', '.join(common_roots) if common_roots else 'لا يوجد'}<br>
                <b>🔹 جذور فريدة في النص الأول:</b> {', '.join(only_in_1) if only_in_1 else 'لا يوجد'}<br>
                <b>🔸 جذور فريدة في النص الثاني:</b> {', '.join(only_in_2) if only_in_2 else 'لا يوجد'}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("⚠️ الرجاء إدخال نصين للمقارنة.")
