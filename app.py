# -*- coding: utf-8 -*-
# ==============================================================================
# نظام نِبْرَاس السيادي (Nibras Sovereign System) - الإصدار v32.0
# الإصدار: الميثاقي - مع وحدة الاستنطاق القرآني (Q-Mode)
# المستخدم المهيمن: محمّد
# ==============================================================================

import streamlit as st
import pandas as pd
import plotly.express as px
from collections import Counter
import re
import os
import json
import time
import hashlib
import math
from itertools import combinations

# ==============================================================================
# [1] إعدادات الهوية السيادية
# ==============================================================================
st.set_page_config(page_title="Nibras v32.0", page_icon="🛡️", layout="wide")

st.markdown("""
<style>
    /* إخفاء جميع عناصر Streamlit العلوية والسفلية */
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
    
    /* منع تمدد الحروف العمودي */
    h1, h2, h3, .stMarkdown, .st-emotion-cache-1v0mbdj, .st-emotion-cache-1wivap2 {
        word-break: normal !important;
        overflow-wrap: normal !important;
        white-space: nowrap !important;
    }
    
    /* إخفاء أي نصوص زائدة */
    [data-testid="stSidebar"] div, [data-testid="stAppViewContainer"] {
        overflow: hidden !important;
    }
    
    /* إصلاح العناوين الجانبية */
    .sidebar-title, [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        display: block;
        width: 100%;
        text-align: center;
        white-space: nowrap;
    }
    
    /* تخصيص الخلفية والخط */
    @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&display=swap');
    [data-testid="stAppViewContainer"] { 
        background: #050505; 
        color: #e0e0e0; 
        direction: rtl; 
        font-family: 'Amiri', serif; 
    }
    .stTabs [aria-selected="true"] { color: #FFD700 !important; border-bottom: 2px solid #FFD700 !important; }
    
    /* كروت الاستنطاق */
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
# [2] مصفوفة الجينات
# ==============================================================================
GENE_STYLE = {
    'C': {'name': 'الإبل', 'color': '#4fc3f7', 'icon': '🐪', 'meaning': 'طاقة المسير والتمكين البعيد'},
    'B': {'name': 'البقر', 'color': '#FFD700', 'icon': '🐄', 'meaning': 'طاقة التثبيت والوفرة المادية'},
    'S': {'name': 'الضأن', 'color': '#4CAF50', 'icon': '🐑', 'meaning': 'طاقة السكينة واللين والرحمة'},
    'G': {'name': 'المعز', 'color': '#ff5252', 'icon': '🐐', 'meaning': 'طاقة السيادة والحدّة والصعود'},
    'N': {'name': 'إشراق', 'color': '#00ffcc', 'icon': '✨', 'meaning': 'الانبثاق الهجين الصافي'}
}

# ==============================================================================
# [3] دوال التطهير
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
# [4] المستخرج الاحتمالي v31
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
# [5] التوقيع الجذري
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
# [6] الاستحقاق الجيني
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
# [7] الطاقة الديناميكية
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
# [8] مؤشر الصعود
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
# [9] شبكة الرنين
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
# [10] بروتوكول خِت فِت للأرشفة
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
    return True

# ==============================================================================
# [11] تحميل قواعد البيانات
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

@st.cache_data(ttl=3600)
def load_quran_matrix(path="data/quran_matrix.json"):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

@st.cache_data(ttl=3600)
def load_quran_roots(path="data/quran_roots.json"):
    if not os.path.exists(path): 
        return {}
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    roots_map = {}
    for item in data.get("roots", []):
        raw_root = item.get("root", "")
        if not raw_root: 
            continue
        norm = normalize_sovereign(raw_root)
        roots_map[norm] = {
            "root_raw": raw_root,
            "orbit_id": 0,
            "orbit": item.get("orbit_hint", "قرآن"),
            "weight": float(item.get("frequency", 10)),
            "insight": f"جذر قرآني (مصدر: {data.get('metadata', {}).get('source', 'Quran DB')})",
            "gene_base": "N"
        }
    return roots_map

# ==============================================================================
# [12] دوال العرض
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
# [13] تهيئة حالة الجلسة
# ==============================================================================
if 'orbit_bodies' not in st.session_state:
    st.session_state.orbit_bodies = []
    st.session_state.orbit_active = False

# تحميل البيانات والدمج الإضافي
r_index, all_roots, orbit_counter = load_lexicon_db("data/nibras_lexicon.json")
quran_data = load_quran_matrix()
quran_roots_index = load_quran_roots()

# الدمج الإضافي: إضافة جذور القرآن التي لا توجد في الليكسيكون الأصلي
for k, v in quran_roots_index.items():
    if k not in r_index:
        r_index[k] = v

# الشريط الجانبي
with st.sidebar:
    st.markdown("""
    <div style="width: 100%; text-align: center; overflow: hidden; white-space: nowrap;">
        <h2 style="color:#4fc3f7; margin:0; padding:0;">🛡️ نبراس السيادي</h2>
        <p style="margin:0; padding:0;">الإصدار v32.0 - الميثاقي</p>
        <p style="margin:0; padding:0;">المستخدم: محمد</p>
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
    <p>خِت فِت.</p>
    """, unsafe_allow_html=True)

# ==============================================================================
# [14] التبويبات
# ==============================================================================
tabs = st.tabs([
    "🔍 الاستنطاق المداري", "🌌 الرنين الجيني", "📈 اللوحة الوجودية",
    "📜 البيان الختامي", "⚖️ الميزان السيادي", "🧠 الوعي الفوقي",
    "📡 الرنين السياقي", "📈 المنحنى الزمني", "📖 النسخة القرآنية"
])

# --- تبويب 0: الاستنطاق المداري (مثل v31.0 تماماً) ---
with tabs[0]:
    st.markdown("### 📍 هندسة المسارات المدارية - النسخة الميثاقية v32.0")
    full_text = st.text_area("أدخل النص للاستنطاق:", height=150, placeholder="مثال: أحد أبى أثر أجد أجل أخذ", key="input_area")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        activate = st.button("🚀 تفعيل المفاعل السيادي", use_container_width=True)
    with col2:
        archive_btn = st.button("🏁 خِت فِت (ختم الجلسة)", use_container_width=True)
    
    if activate and full_text.strip():
        clean_text = normalize_sovereign(full_text)
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
        
        if bodies:
            st.session_state.orbit_bodies = bodies
            st.session_state.orbit_active = True
            ascent_score = compute_ascent_vector(bodies)
            ascent_class = "ascent-positive" if ascent_score > 0 else "ascent-negative" if ascent_score < 0 else ""
            st.markdown(f"""
            <div class="{ascent_class}" style='padding:20px;border-radius:15px;margin-bottom:20px;text-align:center;'>
                <h3 style='margin:0;'>🚀 مؤشر الصعود والانحدار السيادي v32</h3>
                <p style='font-size:2em;margin:5px;font-weight:bold;'>{ascent_score}</p>
                <p style='margin:0;'>{'صعود طاقي نحو المعاني العلوية' if ascent_score > 0 else 'تثبيت مادي في الجذور الأرضية' if ascent_score < 0 else 'توازن بين الصعود والثبات'}</p>
            </div>
            """, unsafe_allow_html=True)
            
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
            
            total_e = sum(b['energy'] for b in bodies)
            genes_count = Counter(b['gene'] for b in bodies)
            dom_gene = max(genes_count, key=genes_count.get)
            orbits_detail = Counter(f"المدار {b['orbit_id']}" for b in bodies if b.get('orbit_id'))
            n_count = sum(1 for b in bodies if b['gene'] == 'N')
            st.markdown(f"""
            <div class="story-box">
                ✅ تم استنطاق <b>{len(bodies)}</b> جسماً جذرياً.<br>
                🧬 الهيمنة الجينية: <b>{GENE_STYLE[dom_gene]['icon']} {GENE_STYLE[dom_gene]['name']}</b><br>
                ✨ حالات الإشراق (N): <b>{n_count}</b><br>
                ⚡ مجموع الطاقة الديناميكية: <b>{total_e:.1f}</b><br>
                📚 الجذور الفريدة: <b>{', '.join(unique_roots)}</b><br>
                🎯 توزيع المدارات: {', '.join([f'{k}({v})' for k, v in orbits_detail.items()])}
            </div>
            """, unsafe_allow_html=True)
            display_insight_cards(bodies)
            st.success("✅ تم الاستنطاق الميثاقي بنجاح (v32.0).")
        else:
            st.error("⚠️ لم يتم العثور على جذور مطابقة.")
    
    elif archive_btn and st.session_state.orbit_active and st.session_state.orbit_bodies:
        ascent_score = compute_ascent_vector(st.session_state.orbit_bodies)
        if khit_fit_archive(st.session_state.orbit_bodies, ascent_score):
            st.success("🔒 تم تشفير الجلسة في الذاكرة العميقة (data/deep_memory.json).")
        else:
            st.error("❌ فشل في أرشفة الجلسة.")
    elif archive_btn:
        st.warning("⚠️ لا توجد جلسة نشطة لأرشفتها.")

# --- التبويبات 1-7 (مختصرة) ---
with tabs[1]:
    st.markdown("### 🌌 مصفوفة الرنين والاستحقاق المداري")
    cols = st.columns(4)
    for i, (code, info) in enumerate(GENE_STYLE.items()):
        if i < 4:
            cols[i].markdown(f"<div class='ultra-card' style='border-top-color:{info['color']}'><h2>{info['icon']}</h2><h3>{info['name']}</h3><p>{info['meaning']}</p></div>", unsafe_allow_html=True)
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
                st.markdown(f"<div class='insight-card' style='border-right-color:{gi['color']}'><b style='color:{gi['color']}'>📌 الجذر: {found['root_raw']}</b><br>🧬 الجين القاعدي: {gi['icon']} {gi['name']}<br>🔄 المدار: {found['orbit']} (ID: {found.get('orbit_id', 0)})<br>⚡ الوزن الأصلي: {found.get('weight', 1.0)} | الطاقة الأساسية: {found.get('raw_energy', 0):.1f}<br><hr><p>🔮 {found['insight']}</p></div>", unsafe_allow_html=True)

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
            st.plotly_chart(px.bar(orbit_df, x='orbit_id', y='count', title="توزيع الجذور حسب المدار"))
    else:
        st.info("⚙️ انتظر تفعيل المفاعل.")

with tabs[3]:
    st.markdown("### 📜 البيان الختامي")
    if st.session_state.orbit_active and st.session_state.orbit_bodies:
        bodies = st.session_state.orbit_bodies
        total_e = sum(b['energy'] for b in bodies)
        genes_count = Counter(b['gene'] for b in bodies)
        dom_gene = max(genes_count, key=genes_count.get)
        st.markdown(f"<div class='story-box'><b>بيان الاستواء الوجودي v32.0:</b><br>تم استنطاق <b>{len(bodies)}</b> جذراً.<br>الهيمنة الجينية: <b>{GENE_STYLE[dom_gene]['icon']} {GENE_STYLE[dom_gene]['name']}</b><br>مجموع الطاقة الديناميكية: <b>{total_e:.1f}</b></div>", unsafe_allow_html=True)
        display_insight_cards(bodies)
    else:
        st.info("⚙️ انتظر تفعيل المفاعل.")

with tabs[4]:
    st.markdown("### ⚖️ ميزان النزاهة الجذرية")
    if st.session_state.orbit_active and st.session_state.orbit_bodies:
        display_insight_cards(st.session_state.orbit_bodies)
    else:
        st.info("⚙️ انتظر تفعيل المفاعل.")

with tabs[5]:
    st.markdown("### 🧠 الوعي الفوقي")
    if st.session_state.orbit_active and st.session_state.orbit_bodies:
        bodies = st.session_state.orbit_bodies
        total_e = sum(b['energy'] for b in bodies)
        genes_count = Counter(b['gene'] for b in bodies)
        dom_gene = max(genes_count, key=genes_count.get)
        orbits_analysis = Counter(b.get('orbit_id', 0) for b in bodies)
        st.markdown(f"<div class='story-box'><h3 style='color:#FFD700;'>🌌 بيان الوعي الجمعي</h3><b>عدد الجذور:</b> {len(bodies)}<br><b>مجموع الطاقة الديناميكية:</b> {total_e:.1f}<br><b>الهيمنة الجينية:</b> {GENE_STYLE[dom_gene]['icon']} {GENE_STYLE[dom_gene]['name']}<br><b>توزيع المدارات:</b> {', '.join([f'المدار {k}({v})' for k, v in sorted(orbits_analysis.items()) if k > 0])}</div>", unsafe_allow_html=True)
        display_insight_cards(bodies)
    else:
        st.info("⚙️ انتظر تفعيل المفاعل.")

with tabs[6]:
    st.markdown("### 📡 الرنين السياقي")
    if st.session_state.orbit_active and st.session_state.orbit_bodies:
        resonance_edges = build_resonance_network(st.session_state.orbit_bodies)
        if resonance_edges:
            st.dataframe(pd.DataFrame(resonance_edges), use_container_width=True)
            strongest = resonance_edges[0]
            st.success(f"✨ أقوى رابط رنيني: **{strongest['source']}** ⇄ **{strongest['target']}** | القوة: {strongest['strength']} | المسافة: {strongest['distance']} | الأحرف المشتركة: {strongest['shared_letters']}")
        else:
            st.info("لا توجد روابط رنين قوية.")
    else:
        st.info("⚙️ انتظر تفعيل المفاعل.")

with tabs[7]:
    st.markdown("### 📈 المنحنى الزمني")
    if st.session_state.orbit_active and st.session_state.orbit_bodies:
        bodies = sorted(st.session_state.orbit_bodies, key=lambda x: x.get('pos', 0))
        if bodies:
            seq_data = [{"الترتيب": b.get('pos', i), "الجذر": b['root'], "الطاقة": b['energy'], "المدار": b.get('orbit_id', 0), "الجين": b['gene'], "الإشراق": b.get('sig_n_factor', 0)} for i, b in enumerate(bodies)]
            df_seq = pd.DataFrame(seq_data)
            fig = px.line(df_seq, x="الترتيب", y="الطاقة", markers=True, title="منحنى تدفق الطاقة في النص")
            fig.update_traces(line_color='#00ffcc', marker_color='#FFD700', marker_size=10)
            fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df_seq[["الترتيب", "الجذر", "الطاقة", "المدار", "الجين", "الإشراق"]], use_container_width=True)
            energies = [b['energy'] for b in bodies]
            if len(energies) > 1:
                trend = energies[-1] - energies[0]
                trend_text = "📈 تصاعدي" if trend > 0 else "📉 تنازلي" if trend < 0 else "➡️ مستقر"
                st.info(f"اتجاه الطاقة: {trend_text} (التغير: {trend:.1f})")
        else:
            st.info("لا توجد بيانات كافية.")
    else:
        st.info("⚙️ انتظر تفعيل المفاعل.")

# ==============================================================================
# [15] التبويب 8: النسخة القرآنية (Q-Mode)
# ==============================================================================
with tabs[8]:
    st.markdown("### 📖 استنطاق الآيات القرآنية (Q-Mode)")
    
    if not quran_data:
        st.error("⚠️ ملف quran_matrix.json غير موجود. يرجى التأكد من وجوده في مجلد data/")
    else:
        # اختيار السورة
        surahs = sorted(set(r["surah_number"] for r in quran_data))
        col_a, col_b = st.columns(2)
        with col_a:
            sel_sura = st.selectbox("📌 اختر السورة", surahs, format_func=lambda x: f"{x} - {next((r['surah_name'] for r in quran_data if r['surah_number'] == x), '')}")
        
        # تصفية الآيات حسب السورة المختارة
        ayat = [r for r in quran_data if r["surah_number"] == sel_sura]
        ayah_labels = [f"{r['ayah_number']} - {r['surah_name']}" for r in ayat]
        
        with col_b:
            sel_label = st.selectbox("📜 اختر الآية", ayah_labels)
        
        # عرض نص الآية
        selected_ayah = ayat[ayah_labels.index(sel_label)]
        st.markdown(f"""
        <div style="background: #0d0d14; padding: 20px; border-radius: 15px; border-right: 5px solid #4fc3f7; margin-bottom: 20px; text-align: center;">
            <p style="font-size: 1.3em; line-height: 1.8;">{selected_ayah['text']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 تفعيل المفاعل القرآني", use_container_width=True):
            text = selected_ayah['text']
            clean_text = normalize_sovereign(text)
            words = clean_text.split()
            bodies = []
            all_matched_roots = []
            temp_meta = []
            
            for pos, word in enumerate(words):
                # استخراج الجذر (Fallback في حال عدم وجود المطور)
                rk = word if word in r_index else None
                mode = "direct" if rk else "none"
                pattern_name = "direct_match" if rk else "none"
                morph_rank = 3 if rk else 0
                
                temp_meta.append({"word": word, "pos": pos, "rk": rk, "mode": mode, "pattern_name": pattern_name, "morph_rank": morph_rank})
                if rk:
                    all_matched_roots.append(rk)
            
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
                    "root": data.get("root_raw", m['rk']),
                    "root_norm": m['rk'],
                    "orbit": data.get("orbit", "قرآن"),
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
                    "resonance_bias": sig['rb']
                })
            
            if bodies:
                st.session_state.orbit_bodies = bodies
                st.session_state.orbit_active = True
                
                ascent_score = compute_ascent_vector(bodies)
                ascent_class = "ascent-positive" if ascent_score > 0 else "ascent-negative" if ascent_score < 0 else ""
                st.markdown(f"""
                <div class="{ascent_class}" style='padding:20px;border-radius:15px;margin-bottom:20px;text-align:center;'>
                    <h3 style='margin:0;'>🚀 مؤشر الصعود القرآني</h3>
                    <p style='font-size:2em;margin:5px;font-weight:bold;'>{ascent_score}</p>
                    <p style='margin:0;'>{'صعود طاقي نحو المعاني العلوية' if ascent_score > 0 else 'تثبيت مادي في الجذور الأرضية' if ascent_score < 0 else 'توازن بين الصعود والثبات'}</p>
                </div>
                """, unsafe_allow_html=True)
                
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
                
                total_e = sum(b['energy'] for b in bodies)
                genes_count = Counter(b['gene'] for b in bodies)
                dom_gene = max(genes_count, key=genes_count.get)
                orbits_detail = Counter(f"المدار {b['orbit_id']}" for b in bodies if b.get('orbit_id'))
                n_count = sum(1 for b in bodies if b['gene'] == 'N')
                st.markdown(f"""
                <div class="story-box">
                    ✅ تم استنطاق <b>{len(bodies)}</b> جسماً جذرياً من الآية القرآنية.<br>
                    🧬 الهيمنة الجينية: <b>{GENE_STYLE[dom_gene]['icon']} {GENE_STYLE[dom_gene]['name']}</b><br>
                    ✨ حالات الإشراق (N): <b>{n_count}</b><br>
                    ⚡ مجموع الطاقة الديناميكية: <b>{total_e:.1f}</b><br>
                    🎯 توزيع المدارات: {', '.join([f'{k}({v})' for k, v in orbits_detail.items()])}
                </div>
                """, unsafe_allow_html=True)
                
                display_insight_cards(bodies)
                st.success("✅ تم الاستنطاق القرآني بنجاح (Q-Mode).")
            else:
                st.warning("⚠️ لم يتم العثور على جذور مطابقة في هذه الآية.")
