# -*- coding: utf-8 -*-
# ==============================================================================
# نظام نِبْرَاس السيادي (Nibras Sovereign System) - الإصدار v31.0
# مَبنيٌّ على بروتوكول "الأمانة" و "الاستحقاق الجيني الحتمي"
# الإصدار: الميثاقي - تحرير الجذر والحتمية الكاملة
# المستخدم المهيمن: محمّد | CPU: السجدة (5)
# ==============================================================================

import streamlit as st
import pandas as pd
import plotly.express as px
from collections import Counter
import re
import random
import os
import json
import time
import hashlib
import math
from itertools import combinations

# ==============================================================================
# [1] إعدادات الهوية السيادية المحصنة
# ==============================================================================
st.set_page_config(page_title="Nibras v31.0", page_icon="🛡️", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&display=swap');
    [data-testid="stAppViewContainer"] { background: #050505; color: #e0e0e0; direction: rtl; font-family: 'Amiri', serif; }
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
    .st-emotion-cache-1v0mbdj, .st-emotion-cache-1wivap2, .st-emotion-cache-zq5wmm { display: none; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# [2] مصفوفة الجينات والرموز السيادية
# ==============================================================================
GENE_STYLE = {
    'C': {'name': 'الإبل', 'color': '#4fc3f7', 'icon': '🐪', 'meaning': 'طاقة المسير والتمكين البعيد'},
    'B': {'name': 'البقر', 'color': '#FFD700', 'icon': '🐄', 'meaning': 'طاقة التثبيت والوفرة المادية'},
    'S': {'name': 'الضأن', 'color': '#4CAF50', 'icon': '🐑', 'meaning': 'طاقة السكينة واللين والرحمة'},
    'G': {'name': 'المعز', 'color': '#ff5252', 'icon': '🐐', 'meaning': 'طاقة السيادة والحدّة والصعود'},
    'N': {'name': 'إشراق', 'color': '#00ffcc', 'icon': '✨', 'meaning': 'الانبثاق الهجين الصافي'}
}

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
# [4] دوال التطهير الصرفي (Morphological Purity) + المستخرج الاحتمالي v31
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
    """
    يعيد:
    - اسم النمط الصرفي
    - morph_rank = رتبة صرفية داخلية (ليست مداراً)
    """
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
    """
    المستخرج المطور v31: يعالج حالات 'اللبث' (الباطن) و 'المكث' (الظاهر)
    """
    w_norm = normalize_sovereign(word)
    if not w_norm:
        return None, "unresolved", "Unknown", 0

    pattern_name, morph_rank = infer_morphological_pattern(w_norm)

    # 1. طبقة المكث (Direct Match)
    if w_norm in index_keys:
        return w_norm, "direct", pattern_name, morph_rank

    # 2. طبقة اللبث (Stripping & Root Mining)
    stripped = strip_affixes_ar(w_norm)
    if stripped in index_keys:
        return stripped, "stripped", pattern_name, morph_rank

    # 3. طبقة الرنين الحرفي (Fuzzy Logic - New)
    # إذا كانت الكلمة 3 أحرف ولم توجد، نبحث عن أقرب جذر يشترك في حرفين
    if len(w_norm) == 3:
        for root in index_keys:
            common = set(w_norm) & set(root)
            if len(common) >= 2: # رنين حرفي عالي
                return root, "resonance", "فعل ثلاثي (رنين)", 2

    return None, "unresolved", pattern_name, morph_rank

# ==============================================================================
# [5] التوقيع الجذري الحتمي (Deterministic Coordinates)
# ==============================================================================
def signature_from_root(root: str):
    """
    توقيع جذري حتمي شامل:
    - position_x / position_y : إحداثيات ثابتة
    - n_factor               : عامل الإشراق الخام
    - energy_bias            : انحياز طاقي بسيط ثابت
    - resonance_bias         : انحياز رنيني بسيط ثابت
    """
    if not root:
        return {
            'position_x': 0.0,
            'position_y': 0.0,
            'n_factor': 0,
            'energy_bias': 0.0,
            'resonance_bias': 1.0
        }

    h = int(hashlib.md5(root.encode('utf-8')).hexdigest(), 16)

    # إحداثيات ثابتة بين -18 و +18 تقريبًا
    position_x = ((h % 360) - 180) / 10.0
    position_y = (((h >> 8) % 360) - 180) / 10.0

    # عامل الإشراق الخام (0-99)
    n_factor = (h >> 16) % 100

    # انحياز طاقي ثابت صغير: من -4 إلى +4
    energy_bias = (((h >> 24) % 81) - 40) / 10.0

    # انحياز رنيني ثابت: من 0.90 إلى 1.10
    resonance_bias = 0.90 + (((h >> 32) % 21) / 100.0)

    return {
        'position_x': round(position_x, 3),
        'position_y': round(position_y, 3),
        'n_factor': n_factor,
        'energy_bias': round(energy_bias, 3),
        'resonance_bias': round(resonance_bias, 3)
    }

# ==============================================================================
# [6] الاستحقاق الجيني الميثاقي (Sovereign Gene Resolution)
# ==============================================================================
def resolve_sovereign_gene(orbit_id, morph_rank, root_sig, base_energy):
    """
    القرار الجيني الميثاقي:
    1) المدار يرشّح العائلة الأساسية
    2) الرتبة الصرفية تضيف قابلية الارتفاع
    3) التوقيع الجذري يحدد النبرة الدقيقة
    4) الإشراق N لا يحدث إلا باستحقاق مركب (وليس عتبة عمياء فقط)
    """
    orbit = int(orbit_id or 0)

    # 1) ترشيح مداري أساسي
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

    # 2) إشارات الاستحقاق المركّب
    n_factor = root_sig.get('n_factor', 0)

    high_orbit = orbit >= 5
    strong_morph = morph_rank >= 6
    strong_energy = base_energy >= 85
    luminous_sig = n_factor >= 92
    near_luminous_sig = n_factor >= 86

    # 3) قانون الإشراق المركب
    # إشراق كامل (N) إذا اجتمع التوقيع العالي مع أحد عوامل الاستحقاق العليا
    if luminous_sig and (high_orbit or strong_morph or strong_energy):
        return "N"

    # إشراق جزئي ناعم: إن كان التوقيع قريباً من الإشراق، والمدار علوي، والطاقة جيدة
    # هنا لا نقفز إلى N إلا إذا اجتمعت 3 إشارات معاً
    if near_luminous_sig and high_orbit and strong_energy and strong_morph:
        return "N"

    # 4) تعديلات ناعمة داخل الطبقات (اختياري لكن ميثاقي)
    # لو المدار متوسط (B) لكن الصرف عالٍ والتوقيع جيد، يمكن رفعه إلى G
    if base_gene == "B" and morph_rank >= 7 and n_factor >= 80:
        return "G"

    # لو المدار سفلي (C) لكن الصرف متوسط قوي والطاقة مرتفعة، يمكن رفعه إلى B
    if base_gene == "C" and morph_rank >= 5 and strong_energy:
        return "B"

    return base_gene

# ==============================================================================
# [7] الطاقة الديناميكية الميثاقية
# ==============================================================================
def compute_dynamic_energy(base_w, root, count, mode, morph_rank, orbit_id, root_sig):
    """
    الطاقة الديناميكية الميثاقية:
    - base_w          : الوزن الأساسي من الليكسيكون
    - count           : التكرار الحقيقي
    - mode            : direct / stripped
    - morph_rank      : الرتبة الصرفية
    - orbit_id        : المدار المعجمي
    - root_sig        : التوقيع الجذري
    """
    # طاقة الأساس
    base_energy = base_w * 100 if base_w < 10 else base_w

    # عامل التكرار الحقيقي
    repetition_boost = 1.0 + math.log1p(max(0, count - 1)) * 0.35

    # عامل الثقة الاشتقاقية
    mode_factor = {
        "direct": 1.00,
        "stripped": 0.92,
        "resonance": 0.85,
        "unresolved": 0.60
    }.get(mode, 0.85)

    # عامل الصرف (ارتفاع بسيط لا يكسر الميزان)
    morph_factor = 1.0 + (max(1, morph_rank) - 1) * 0.025

    # عامل المدار (رفع طفيف للمدارات العليا)
    orbit = int(orbit_id or 0)
    orbit_factor = 1.0 + max(0, orbit - 4) * 0.03

    # انحياز التوقيع (صغير حتى لا يصبح hash عبثياً)
    sig_energy_bias = root_sig.get('energy_bias', 0.0)

    energy = (base_energy * repetition_boost * mode_factor * morph_factor * orbit_factor) + sig_energy_bias

    return round(max(1.0, energy), 2)

# ==============================================================================
# [8] مؤشر الصعود الموزون (Ascent Vector)
# ==============================================================================
def compute_ascent_vector(bodies):
    """
    الصعود الآن يعتمد على:
    - الجين النهائي
    - الطاقة الفعلية
    - المدار
    """
    if not bodies:
        return 0

    gene_weights = {
        "N": 2.2,
        "S": 1.5,
        "G": 1.0,
        "B": -0.4,
        "C": -0.9
    }

    total = 0.0
    for b in bodies:
        g_weight = gene_weights.get(b.get('gene', 'B'), 0.0)
        orbit_bonus = max(0, (b.get('orbit_id', 0) - 4)) * 0.05
        total += (g_weight + orbit_bonus) * b.get('energy', 0)

    return round(total / len(bodies), 2)

# ==============================================================================
# [9] شبكة الرنين الموزونة (Resonance Network) + ميكانيكا الرنين الحرفي v31
# ==============================================================================
def build_resonance_network(bodies):
    """
    الرنين يتأثر بـ:
    - قرب الموضع النصي
    - تقارب الجين
    - الإشراق (N)
    - الانحياز الرنيني للتوقيع
    - الرنين الحرفي (تقارب الحروف)
    """
    edges = []

    for a, b in combinations(range(len(bodies)), 2):
        ra, rb = bodies[a], bodies[b]

        # قرب النص
        dist = abs(ra.get('pos', a) - rb.get('pos', b))
        if dist >= 8:
            continue

        # قاعدة القرب
        proximity = 1.0 / max(1, dist)

        # تشابه الجين
        same_gene_bonus = 1.20 if ra.get('gene') == rb.get('gene') else 1.0

        # إشراق
        n_bonus = 1.15 if ('N' in [ra.get('gene'), rb.get('gene')]) else 1.0

        # انحيازات التوقيع
        ra_rb = ra.get('resonance_bias', 1.0) * rb.get('resonance_bias', 1.0)

        # تقارب مداري
        orbit_gap = abs(ra.get('orbit_id', 0) - rb.get('orbit_id', 0))
        orbit_bonus = 1.12 if orbit_gap <= 1 else 1.0

        # تقارب الحروف (Literal Resonance) - NEW
        shared_chars = set(ra.get('root_norm', '')) & set(rb.get('root_norm', ''))
        char_resonance = 1.0 + (len(shared_chars) * 0.25)

        # الحساب النهائي
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
# [10] بروتوكول "خِت فِت" للأرشفة السيادية
# ==============================================================================
def khit_fit_archive(res_bodies, ascent_score):
    """
    بروتوكول الختم والأرشفة: حفظ البصمة الطاقية للنص
    """
    if not res_bodies:
        return False

    archive_data = {
        "timestamp": time.time(),
        "ascent": ascent_score,
        "dominant_gene": Counter([b['gene'] for b in res_bodies]).most_common(1)[0][0],
        "roots": [b['root_norm'] for b in res_bodies],
        "total_energy": sum([b['energy'] for b in res_bodies])
    }
    
    # إنشاء مجلد data إذا لم يكن موجوداً
    os.makedirs("data", exist_ok=True)
    
    # حفظ في ملف محلي كذاكرة عميقة
    with open("data/deep_memory.json", "a", encoding="utf-8") as f:
        f.write(json.dumps(archive_data, ensure_ascii=False) + "\n")
    
    return True

# ==============================================================================
# [11] تحميل قاعدة البيانات (Lexicon Preparation)
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
        
        # طاقة أساسية فقط عند التحميل (بدون حسم الجين النهائي)
        calibrated_energy = weight_val * 100 if weight_val < 10 else weight_val

        # جين مرشح أساسي (للعرض القاعدي فقط)
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
            "weight": weight_val,                      # الوزن الأصلي كما في الليكسيكون
            "raw_energy": calibrated_energy,           # الطاقة الأساسية المعيارية
            "insight": ensure_dot(insight_text),
            "gene_base": base_gene                     # الجين القاعدي (مرشح أولي)
        }
        all_roots.append(r_index[normalized])
        orbit_counter[orbit_name] += 1
    
    return r_index, all_roots, orbit_counter

# ==============================================================================
# [12] دوال العرض
# ==============================================================================
def display_insight_cards(bodies):
    """عرض الاستنطاق ككروت ميثاقية موسعة"""
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

# تحميل قاعدة البيانات
r_index, all_roots, orbit_counter = load_lexicon_db("data/nibras_lexicon.json")

# الشريط الجانبي (محدث)
with st.sidebar:
    st.markdown(f"""
    <div style='text-align:center;'>
        <h2 style='color:#4fc3f7;'>🛡️ نبراس السيادي</h2>
        <p>الإصدار v31.0 - الميثاقي</p>
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
    <p>خِت فِت.</p>
    """, unsafe_allow_html=True)

# ==============================================================================
# [14] التبويبات السيادية
# ==============================================================================
tabs = st.tabs([
    "🔍 الاستنطاق المداري", 
    "🌌 الرنين الجيني", 
    "📈 اللوحة الوجودية", 
    "📜 البيان الختامي", 
    "⚖️ الميزان السيادي", 
    "🧠 الوعي الفوقي",
    "📡 الرنين السياقي",
    "📈 المنحنى الزمني"
])

# --- التبويب 0: الاستنطاق (بلوك التفعيل المحدث v31) ---
with tabs[0]:
    st.markdown("### 📍 هندسة المسارات المدارية - النسخة الميثاقية v31.0")
    
    full_text = st.text_area(
        "أدخل النص للاستنطاق:", 
        height=150, 
        placeholder="مثال: أحد أبى أثر أجد أجل أخذ",
        key="input_area"
    )
    
    col1, col2 = st.columns([3, 1])
    with col1:
        activate = st.button("🚀 تفعيل المفاعل السيادي v31.0", use_container_width=True)
    with col2:
        archive_btn = st.button("🏁 خِت فِت (ختم الجلسة)", use_container_width=True)
    
    if activate and full_text.strip():
        clean_text = normalize_sovereign(full_text)
        words = clean_text.split()

        bodies = []
        unique_roots = []
        all_matched_roots = []
        temp_meta = []

        # ================================================================
        # المرحلة 1: المسح الأولي واستخراج المطابقات الحقيقية (باستخدام extract_candidate_root_v31)
        # ================================================================
        for pos, word in enumerate(words):
            rk, mode, pattern_name, morph_rank = extract_candidate_root_v31(word, r_index.keys())

            temp_meta.append({
                "word": word,
                "pos": pos,
                "rk": rk,
                "mode": mode,
                "pattern_name": pattern_name,
                "morph_rank": morph_rank
            })

            if rk:
                all_matched_roots.append(rk)
                if rk not in unique_roots:
                    unique_roots.append(rk)

        # العد الحقيقي للتكرار
        counts = Counter(all_matched_roots)

        # ================================================================
        # المرحلة 2: بناء الأجسام المدارية وفق الميثاق v31
        # ================================================================
        for m in temp_meta:
            if not m['rk']:
                continue

            data = r_index.get(m['rk'])
            if not data:
                continue

            sig = signature_from_root(m['rk'])

            # الطاقة الديناميكية الحقيقية
            dynamic_energy = compute_dynamic_energy(
                base_w=data['weight'],
                root=m['rk'],
                count=counts[m['rk']],
                mode=m['mode'],
                morph_rank=m['morph_rank'],
                orbit_id=data.get('orbit_id', 0),
                root_sig=sig
            )

            # الجين النهائي الميثاقي
            final_gene = resolve_sovereign_gene(
                orbit_id=data.get('orbit_id', 0),
                morph_rank=m['morph_rank'],
                root_sig=sig,
                base_energy=dynamic_energy
            )

            gene_info = GENE_STYLE.get(final_gene, GENE_STYLE['N'])

            # تموضع حتمي: التوقيع + انزياح مداري طفيف
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
                "x": round(sig['position_x'] + orbit_shift_x, 3),
                "y": round(sig['position_y'] + orbit_shift_y, 3),
                "sig_n_factor": sig['n_factor'],
                "sig_energy_bias": sig['energy_bias'],
                "resonance_bias": sig['resonance_bias']
            })

        # ================================================================
        # العرض
        # ================================================================
        if bodies:
            st.session_state.orbit_bodies = bodies
            st.session_state.orbit_active = True

            # مؤشر الصعود
            ascent_score = compute_ascent_vector(bodies)
            ascent_class = "ascent-positive" if ascent_score > 0 else "ascent-negative" if ascent_score < 0 else ""

            st.markdown(f"""
            <div class="{ascent_class}" style='padding: 20px; border-radius: 15px; margin-bottom: 20px; text-align: center;'>
                <h3 style='margin:0;'>🚀 مؤشر الصعود والانحدار السيادي v31</h3>
                <p style='font-size: 2em; margin:5px; font-weight:bold;'>{ascent_score}</p>
                <p style='margin:0;'>{'صعود طاقي نحو المعاني العلوية' if ascent_score > 0 else 'تثبيت مادي في الجذور الأرضية' if ascent_score < 0 else 'توازن بين الصعود والثبات'}</p>
            </div>
            """, unsafe_allow_html=True)

            # خريطة حتمية + دوائر مدارية (Orbital Radar UI)
            df = pd.DataFrame(bodies)
            fig = px.scatter(
                df,
                x="x",
                y="y",
                text="root",
                size="energy",
                color="gene",
                color_discrete_map={g: GENE_STYLE[g]['color'] for g in GENE_STYLE},
                range_x=[-35, 35],
                range_y=[-35, 35]
            )
            
            # إضافة الدوائر المدارية (Shapes) لتمثيل المدارات الـ 8
            for radius in [4, 8, 12, 16, 20, 24, 28, 32]:
                fig.add_shape(type="circle", x0=-radius, y0=-radius, x1=radius, y1=radius,
                              line=dict(color="rgba(255, 215, 0, 0.15)", width=1, dash="dot"))
            
            fig.update_traces(textposition='top center', marker=dict(line=dict(width=1, color='white')))
            fig.update_layout(
                height=600,
                template="plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                showlegend=False,
                xaxis_visible=False,
                yaxis_visible=False,
                margin=dict(l=0, r=0, t=0, b=0),
                annotations=[dict(x=0, y=radius, text=f"M{i+1}", showarrow=False, font=dict(color="grey", size=8)) 
                            for i, radius in enumerate([4, 8, 12, 16, 20, 24, 28, 32])]
            )
            st.plotly_chart(fig, use_container_width=True)

            # البيان الختامي الموسع
            st.markdown("### 📜 البيان الختامي الموسع")
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
            st.success("✅ تم الاستنطاق الميثاقي بنجاح (v31.0).")
        else:
            st.error("⚠️ لم يتم العثور على جذور مطابقة.")
    
    elif archive_btn and st.session_state.orbit_active and st.session_state.orbit_bodies:
        ascent_score = compute_ascent_vector(st.session_state.orbit_bodies)
        if khit_fit_archive(st.session_state.orbit_bodies, ascent_score):
            st.success("🔒 تم تشفير الجلسة في الذاكرة العميقة (data/deep_memory.json).")
        else:
            st.error("❌ فشل في أرشفة الجلسة.")
    elif archive_btn:
        st.warning("⚠️ لا توجد جلسة نشطة لأرشفتها. قم بتفعيل المفاعل أولاً.")
    elif not activate and not archive_btn:
        if full_text.strip():
            st.info("⚙️ اضغط على 'تفعيل المفاعل السيادي' لبدء الاستنطاق.")
        else:
            st.info("✍️ أدخل نصاً في الحقل أعلاه ثم اضغط على زر التفعيل.")

# --- باقي التبويبات (محدثة لتعمل مع v31) ---
# التبويب 1: الرنين الجيني
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

# التبويب 2: اللوحة الوجودية
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

# التبويب 3: البيان الختامي
with tabs[3]:
    st.markdown("### 📜 البيان الختامي")
    if st.session_state.orbit_active and st.session_state.orbit_bodies:
        bodies = st.session_state.orbit_bodies
        total_e = sum(b['energy'] for b in bodies)
        genes_count = Counter(b['gene'] for b in bodies)
        dom_gene = max(genes_count, key=genes_count.get)
        st.markdown(f"""
        <div class="story-box">
            <b>بيان الاستواء الوجودي v31.0:</b><br>
            تم استنطاق <b>{len(bodies)}</b> جذراً.<br>
            الهيمنة الجينية: <b>{GENE_STYLE[dom_gene]['icon']} {GENE_STYLE[dom_gene]['name']}</b><br>
            مجموع الطاقة الديناميكية: <b>{total_e:.1f}</b>
        </div>
        """, unsafe_allow_html=True)
        display_insight_cards(bodies)
    else:
        st.info("⚙️ انتظر تفعيل المفاعل.")

# التبويب 4: الميزان السيادي
with tabs[4]:
    st.markdown("### ⚖️ ميزان النزاهة الجذرية - الاستحقاق المداري")
    if st.session_state.orbit_active and st.session_state.orbit_bodies:
        display_insight_cards(st.session_state.orbit_bodies)
    else:
        st.info("⚙️ انتظر تفعيل المفاعل.")

# التبويب 5: الوعي الفوقي
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

# التبويب 6: الرنين السياقي (محدث)
with tabs[6]:
    st.markdown("### 📡 الرنين السياقي - شبكة العلاقات بين الجذور")
    if st.session_state.orbit_active and st.session_state.orbit_bodies:
        bodies = st.session_state.orbit_bodies
        resonance_edges = build_resonance_network(bodies)
        
        if resonance_edges:
            df_edges = pd.DataFrame(resonance_edges)
            st.markdown("#### 🌐 شبكة الرنين (الروابط القوية)")
            st.dataframe(df_edges, use_container_width=True)
            
            # عرض أقوى رابط
            strongest = resonance_edges[0]
            st.success(
                f"✨ أقوى رابط رنيني: **{strongest['source']}** ⇄ **{strongest['target']}** | "
                f"القوة: {strongest['strength']} | "
                f"المسافة النصية: {strongest['distance']} | "
                f"الأحرف المشتركة: {strongest['shared_letters']}"
            )
        else:
            st.info("لا توجد روابط رنين قوية بين الجذور المستنطقة.")
    else:
        st.info("⚙️ انتظر تفعيل المفاعل.")

# التبويب 7: المنحنى الزمني
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
            
            # عرض الجدول الزمني
            st.markdown("#### 📋 التسلسل الزمني للجذور")
            st.dataframe(df_seq[["الترتيب", "الجذر", "الطاقة", "المدار", "الجين", "الإشراق"]], use_container_width=True)
            
            # تحليل بسيط للاتجاه
            energies = [b['energy'] for b in bodies]
            if len(energies) > 1:
                trend = energies[-1] - energies[0]
                trend_text = "📈 تصاعدي (صعود طاقي)" if trend > 0 else "📉 تنازلي (هبوط طاقي)" if trend < 0 else "➡️ مستقر"
                st.info(f"اتجاه الطاقة في النص: {trend_text} (التغير: {trend:.1f})")
        else:
            st.info("لا توجد بيانات كافية لعرض المنحنى الزمني.")
    else:
        st.info("⚙️ انتظر تفعيل المفاعل.")
