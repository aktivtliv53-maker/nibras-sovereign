# -*- coding: utf-8 -*-
# ==============================================================================
# نظام نِبْرَاس السيادي (Nibras Sovereign System) - الإصدار v29.0
# "ثلاثية الصعود" — خريطة الوعي الحراري + متجه الصعود + طبقة مكين بلاغية خفيفة
# مبني على v28.0 مع الحفاظ الكامل على الاستقرار
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
import hashlib
import numpy as np

# ==============================================================================
# [0] أعلام التحكم بالطبقات (يمكن تعطيل أي طبقة بدون كسر النظام)
# ==============================================================================
ENABLE_SMART_ROOT = True          # طبقة التحليل الجذري التقريبي
ENABLE_CONTEXT_ORBIT = True       # طبقة المدار السياقي
ENABLE_DYNAMIC_ENERGY = True      # طبقة الطاقة الديناميكية
ENABLE_COLLECTIVE_LAYER = True    # طبقة الوعي الجمعي
ENABLE_HEATMAP_LAYER = True       # خريطة الوعي الحراري
ENABLE_ASCENT_VECTOR = True       # متجه الصعود
ENABLE_MAKIN_LAYER = True         # طبقة بلاغية مكين خفيفة

# ==============================================================================
# [1] إعدادات الهوية السيادية المحصنة
# ==============================================================================
st.set_page_config(page_title="Nibras v29.0", page_icon="🛡️", layout="wide")

st.markdown("""
<style>
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
# [4] محرك الاستحقاق الجيني v28.0 (الربط المداري الحتمي) — أساس v29.0
# ==============================================================================
def get_sovereign_gene(root_name, original_weight, orbit_id=0):
    orbit = int(orbit_id)
    w = float(original_weight)
    
    if orbit in [1, 2]:
        gene_key = "C"
    elif orbit in [3, 4]:
        gene_key = "B"
    elif orbit in [5, 6]:
        gene_key = "G"
    elif orbit >= 7:
        gene_key = "S"
    else:
        gene_key = "N"

    calibrated_energy = w * 100 if w < 10 else w
    return gene_key, calibrated_energy

def signature_from_root(root):
    if not root: 
        return {'total_energy': 300.0, 'vector_x': 0, 'vector_y': 0}
    h = int(hashlib.md5(root.encode()).hexdigest(), 16)
    return {
        'total_energy': len(root) * 285.0 + (h % 150),
        'vector_x': (h % 30 - 15) / 120.0,
        'vector_y': ((h >> 4) % 30 - 15) / 120.0
    }

# ==============================================================================
# [5] تحميل قاعدة البيانات
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
        
        gene_key, calibrated_energy = get_sovereign_gene(raw_root, weight_val, orbit_id)
        
        orbit_name = f"المدار {orbit_id}" if orbit_id else "وعي"
        insight_text = item.get("insight_radar", item.get("insight", ""))
        
        r_index[normalized] = {
            "root_raw": raw_root,
            "root": normalized,
            "orbit_id": orbit_id,
            "orbit": orbit_name,
            "weight": calibrated_energy / 100 if calibrated_energy > 100 else calibrated_energy,
            "raw_energy": calibrated_energy,
            "insight": ensure_dot(insight_text),
            "gene": gene_key
        }
        all_roots.append(r_index[normalized])
        orbit_counter[orbit_name] += 1
    
    return r_index, all_roots, orbit_counter

# ==============================================================================
# [6] طبقة التحليل الجذري التقريبي + دوال البحث
# ==============================================================================
def smart_extract_root(word: str):
    if not ENABLE_SMART_ROOT:
        return word
    if not word:
        return word
    
    w = normalize_sovereign(word)
    if len(w) <= 3:
        return w

    prefixes = ["ال", "وال", "فال", "بال", "كال", "ولل", "فلل", "س", "و", "ف", "ل", "ب", "ك"]
    for p in sorted(prefixes, key=len, reverse=True):
        if w.startswith(p) and len(w) - len(p) >= 3:
            w = w[len(p):]
            break

    suffixes = ["هما", "كما", "كم", "كن", "نا", "ها", "هم", "هن", "ان", "ون", "ين", "ات", "ة", "ه", "ي", "ا", "ت"]
    for s in sorted(suffixes, key=len, reverse=True):
        if w.endswith(s) and len(w) - len(s) >= 3:
            w = w[:-len(s)]
            break

    for p in ["است", "ت", "ان", "افت"]:
        if w.startswith(p) and len(w) - len(p) >= 3:
            w = w[len(p):]
            break

    return w if len(w) >= 3 else w

def match_root_logic(word, index_keys):
    w = normalize_sovereign(word)
    if not w or len(w) < 2:
        return None

    w_norm = normalize_lexicon_root(w)
    if w_norm in index_keys:
        return w_norm
    
    prefixes = ["ال", "و", "ف", "ب", "ك", "ل", "س", "بال", "وال", "فال"]
    for p in prefixes:
        if w.startswith(p) and len(w) - len(p) >= 3:
            candidate = normalize_lexicon_root(w[len(p):])
            if candidate in index_keys:
                return candidate

    if ENABLE_SMART_ROOT:
        smart_candidate = smart_extract_root(word)
        smart_norm = normalize_lexicon_root(smart_candidate)
        if smart_norm in index_keys:
            return smart_norm

    return None

def display_insight_cards(bodies):
    if not bodies:
        return
    for res in bodies:
        st.markdown(f"""
        <div class="insight-card" style="border-right-color: {res['color']}">
            <b style="color:{res['color']}; font-size:1.2em;">📌 الجذر: {res['root']}</b> | 
            🧬 الجين: {res['gene_icon']} {res['gene_name']} | 
            ⚡ الطاقة: <span class="energy-badge">{res['energy']:.1f}</span>
            <hr style="border:0.5px solid #333; margin:10px 0;">
            <p>🔮 {res['insight']}</p>
        </div>
        """, unsafe_allow_html=True)

# ==============================================================================
# [7] تهيئة حالة الجلسة
# ==============================================================================
if 'orbit_bodies' not in st.session_state:
    st.session_state.orbit_bodies = []
    st.session_state.orbit_active = False

r_index, all_roots, orbit_counter = load_lexicon_db("data/nibras_lexicon.json")

# ==============================================================================
# [8] الشريط الجانبي
# ==============================================================================
with st.sidebar:
    st.markdown(f"""
    <div style='text-align:center;'>
        <h2 style='color:#4fc3f7;'>🛡️ نبراس السيادي</h2>
        <p>الإصدار v29.0 - ثلاثية الصعود</p>
        <p>المستخدم: محمد</p>
    </div>
    ---
    <div>
        <p>📊 إحصائيات القاعدة:</p>
        <p>📚 إجمالي الجذور: {len(r_index)}</p>
        <p>🐪 الإبل (مدارات 1-2): {len([r for r in r_index.values() if r['gene'] == 'C'])}</p>
        <p>🐄 البقر (مدارات 3-4): {len([r for r in r_index.values() if r['gene'] == 'B'])}</p>
        <p>🐑 الضأن (مدارات 7+): {len([r for r in r_index.values() if r['gene'] == 'S'])}</p>
        <p>🐐 المعز (مدارات 5-6): {len([r for r in r_index.values() if r['gene'] == 'G'])}</p>
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
# [9] التبويبات السيادية
# ==============================================================================
tabs = st.tabs([
    "🔍 الاستنطاق المداري",
    "🌌 الرنين الجيني",
    "📈 اللوحة الوجودية الحرارية",
    "📜 البيان الختامي",
    "⚖️ الميزان السيادي",
    "🧠 الوعي الفوقي"
])

# ==============================================================================
# [10] طبقات المدار السياقي + الطاقة الديناميكية + الوعي الجمعي + البلاغة
# ==============================================================================
def apply_context_orbit_adjustment(bodies):
    if not ENABLE_CONTEXT_ORBIT or not bodies:
        return bodies
    freq = Counter(b['root'] for b in bodies)
    max_freq = max(freq.values()) if freq else 1
    for b in bodies:
        f = freq[b['root']]
        if f > 1 and isinstance(b.get('orbit_id'), int) and b['orbit_id'] > 0:
            delta = 1 if f >= max_freq else 0
            new_orbit = b['orbit_id'] + delta
            b['orbit_id_context'] = new_orbit
            b['orbit'] = f"المدار {new_orbit}"
        else:
            b['orbit_id_context'] = b.get('orbit_id', 0)
    return bodies

def apply_dynamic_energy(bodies, text_length):
    if not ENABLE_DYNAMIC_ENERGY or not bodies:
        return bodies
    freq = Counter(b['root'] for b in bodies)
    base_len_factor = max(1, min(3, text_length / 50))
    for b in bodies:
        f = freq[b['root']]
        sig = signature_from_root(b['root'])
        base_energy = b.get('base_energy', b['energy'])
        dynamic = base_energy * (1 + 0.05 * (f - 1)) * base_len_factor
        dynamic += sig['total_energy'] * 0.05
        b['energy'] = round(dynamic, 2)
    return bodies

def compute_collective_consciousness(bodies):
    if not ENABLE_COLLECTIVE_LAYER or not bodies:
        return {}
    genes_count = Counter(b['gene'] for b in bodies)
    total_e = sum(b['energy'] for b in bodies)
    unique_roots = len(set(b['root'] for b in bodies))
    ascent = genes_count.get('G', 0) + genes_count.get('C', 0)
    calm = genes_count.get('S', 0)
    material = genes_count.get('B', 0)
    tension_level = ascent * 1.2 + material * 0.8 - calm * 1.0
    harmony_level = calm * 1.3 + unique_roots * 0.2
    return {
        "total_energy": total_e,
        "genes_count": genes_count,
        "unique_roots": unique_roots,
        "tension_level": round(tension_level, 2),
        "harmony_level": round(harmony_level, 2),
    }

def makin_letter_profile(root_text: str):
    """
    طبقة بلاغية مكين خفيفة: تقسيم الحروف إلى:
    - حروف صعود (ق، ط، ظ، خ، ص، ض، غ)
    - حروف احتواء/لين (م، ن، ل، ر، و، ي، ه)
    - حروف قطع/حدّة (ح، ج، ك، س، ش، ت، ث، ف، ب، د، ذ، ز)
    """
    if not ENABLE_MAKIN_LAYER or not root_text:
        return {}
    asc_letters = set("قظطخصضغ")
    soft_letters = set("منلرويها")
    sharp_letters = set("حجكسشتثفبدذز")
    r = normalize_sovereign(root_text)
    asc = sum(1 for ch in r if ch in asc_letters)
    soft = sum(1 for ch in r if ch in soft_letters)
    sharp = sum(1 for ch in r if ch in sharp_letters)
    total = max(1, len(r))
    return {
        "asc": asc,
        "soft": soft,
        "sharp": sharp,
        "asc_ratio": round(asc / total, 2),
        "soft_ratio": round(soft / total, 2),
        "sharp_ratio": round(sharp / total, 2),
    }

def compute_ascent_vector(bodies):
    """
    متجه الصعود: رقم واحد يلخص اتجاه النص:
    - قيم موجبة عالية → صعود نحو المدارات العليا
    - قيم سالبة → هبوط/ثقل مادي
    """
    if not ENABLE_ASCENT_VECTOR or not bodies:
        return 0.0
    orbit_vals = []
    for b in bodies:
        oid = b.get('orbit_id_context', b.get('orbit_id', 0))
        if oid:
            orbit_vals.append(oid)
    if not orbit_vals:
        return 0.0
    avg_orbit = sum(orbit_vals) / len(orbit_vals)
    # نطبع المتجه حول محور 5 (تحت/فوق)
    ascent_vector = avg_orbit - 5.0
    return round(ascent_vector, 2)

# ==============================================================================
# [11] التبويب 0: الاستنطاق المداري
# ==============================================================================
with tabs[0]:
    st.markdown("### 📍 هندسة المسارات المدارية — v29.0 ثلاثية الصعود")
    
    full_text = st.text_area(
        "أدخل النص للاستنطاق:", 
        height=150, 
        placeholder="مثال: أحد أبى أثر أجد أجل أخذ",
        key="input_area"
    )
    
    if st.button("🚀 تفعيل المفاعل السيادي v29.0", use_container_width=True):
        if full_text.strip():
            clean = normalize_sovereign(full_text)
            words = clean.split()
            
            bodies = []
            word_pool = []
            
            for word in words:
                root_key = match_root_logic(word, r_index.keys())
                if root_key:
                    data = r_index.get(root_key)
                    if data:
                        sig = signature_from_root(root_key)
                        base_energy = data.get('raw_energy', data['weight'] * 100)
                        gene_info = GENE_STYLE.get(data['gene'], GENE_STYLE['S'])
                        energy = base_energy + sig['total_energy'] * 0.15
                        bodies.append({
                            "root": data['root_raw'],
                            "orbit": data['orbit'],
                            "orbit_id": data.get('orbit_id', 0),
                            "gene": data['gene'],
                            "gene_name": gene_info['name'],
                            "gene_icon": gene_info['icon'],
                            "energy": round(energy, 2),
                            "base_energy": round(energy, 2),
                            "insight": data['insight'],
                            "color": gene_info['color'],
                            "x": random.uniform(-10, 10),
                            "y": random.uniform(-10, 10),
                            "vx": sig['vector_x'],
                            "vy": sig['vector_y']
                        })
                        word_pool.append(data['root_raw'])
            
            if bodies:
                bodies = apply_context_orbit_adjustment(bodies)
                bodies = apply_dynamic_energy(bodies, len(full_text))

                st.session_state.orbit_bodies = bodies
                st.session_state.orbit_active = True
                
                df = pd.DataFrame(bodies)
                fig = px.scatter(
                    df, x="x", y="y", text="root", size="energy", color="gene",
                    color_discrete_map={g: GENE_STYLE[g]['color'] for g in GENE_STYLE},
                    range_x=[-35, 35], range_y=[-35, 35]
                )
                fig.update_layout(
                    height=500,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    showlegend=False,
                    xaxis_visible=False,
                    yaxis_visible=False
                )
                st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("### 📜 البيان الختامي الموسع")
                total_e = sum(b['energy'] for b in bodies)
                genes_count = Counter(b['gene'] for b in bodies)
                dom_gene = max(genes_count, key=genes_count.get)
                orbits_detail = Counter(
                    f"المدار {b.get('orbit_id_context', b.get('orbit_id', 0))}"
                    for b in bodies if b.get('orbit_id')
                )
                
                cc = compute_collective_consciousness(bodies) if ENABLE_COLLECTIVE_LAYER else None
                ascent_vec = compute_ascent_vector(bodies) if ENABLE_ASCENT_VECTOR else 0.0

                extra_line = ""
                if cc:
                    extra_line = (
                        f"<br>🧠 مستوى الانسجام: <b>{cc['harmony_level']}</b> | "
                        f"مستوى التوتر: <b>{cc['tension_level']}</b>"
                    )
                ascent_line = ""
                if ENABLE_ASCENT_VECTOR:
                    direction = "صعود" if ascent_vec > 0 else ("ثبات" if ascent_vec == 0 else "انحدار")
                    ascent_line = f"<br>📈 متجه الصعود: <b>{ascent_vec}</b> ({direction})"

                st.markdown(f"""
                <div class="story-box">
                    ✅ تم استنطاق <b>{len(bodies)}</b> جذراً.<br>
                    🐪 الهيمنة الجينية: <b>{GENE_STYLE[dom_gene]['icon']} {GENE_STYLE[dom_gene]['name']}</b><br>
                    ⚡ مجموع الطاقة: <b>{total_e:.1f}</b><br>
                    📚 الجذور: <b>{', '.join(word_pool)}</b><br>
                    🎯 توزيع المدارات: {', '.join([f'{k}({v})' for k, v in orbits_detail.items()])}
                    {extra_line}
                    {ascent_line}
                </div>
                """, unsafe_allow_html=True)
                
                display_insight_cards(bodies)
                st.success("✅ تم الاستنطاق بنجاح.")
            else:
                st.error("⚠️ لم يتم العثور على جذور مطابقة.")
        else:
            st.warning("⚠️ الرجاء إدخال نص.")

# ==============================================================================
# [12] التبويب 1: الرنين الجيني
# ==============================================================================
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
                gi = GENE_STYLE[found['gene']]
                profile = makin_letter_profile(found['root_raw']) if ENABLE_MAKIN_LAYER else {}
                extra_line = ""
                if profile:
                    extra_line = (
                        f"<br>🔤 حروف الصعود: {profile['asc']} "
                        f"(نسبة: {profile['asc_ratio']}) | "
                        f"حروف اللين: {profile['soft']} "
                        f"(نسبة: {profile['soft_ratio']}) | "
                        f"حروف الحدّة: {profile['sharp']} "
                        f"(نسبة: {profile['sharp_ratio']})"
                    )
                st.markdown(f"""
                <div class='insight-card' style='border-right-color:{gi["color"]}'>
                    <b style='color:{gi["color"]}'>📌 الجذر: {found['root_raw']}</b><br>
                    🧬 الجين: {gi['icon']} {gi['name']}<br>
                    🔄 المدار: {found['orbit']} (ID: {found.get('orbit_id', 0)})<br>
                    ⚡ الطاقة الأساسية: {found.get('raw_energy', found['weight']*100):.1f}
                    {extra_line}
                    <hr>
                    <p>🔮 {found['insight']}</p>
                </div>
                """, unsafe_allow_html=True)

# ==============================================================================
# [13] التبويب 2: اللوحة الوجودية الحرارية (Heatmap Consciousness)
# ==============================================================================
with tabs[2]:
    st.markdown("### 📈 خريطة الوعي الحراري — Heatmap Consciousness")
    if st.session_state.orbit_active and st.session_state.orbit_bodies and ENABLE_HEATMAP_LAYER:
        df = pd.DataFrame(st.session_state.orbit_bodies)
        # نبني شبكة حرارية بسيطة: المحور X = المدار، المحور Y = الجين، القيمة = مجموع الطاقة
        if 'orbit_id_context' in df.columns:
            df['orbit_plot'] = df['orbit_id_context']
        else:
            df['orbit_plot'] = df['orbit_id']
        df['gene_label'] = df['gene'].map(lambda g: f"{GENE_STYLE[g]['icon']} {GENE_STYLE[g]['name']}" if g in GENE_STYLE else g)

        heat_df = df.groupby(['orbit_plot', 'gene_label'])['energy'].sum().reset_index()
        if not heat_df.empty:
            pivot = heat_df.pivot(index='gene_label', columns='orbit_plot', values='energy').fillna(0)
            fig_h = px.imshow(
                pivot.values,
                labels=dict(x="المدار", y="الجين", color="الطاقة"),
                x=pivot.columns,
                y=pivot.index,
                color_continuous_scale="RdBu_r"
            )
            fig_h.update_layout(
                height=500,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_h, use_container_width=True)
        else:
            st.info("لا توجد بيانات كافية لبناء خريطة حرارية.")

        col1, col2 = st.columns(2)
        col1.plotly_chart(
            px.pie(
                df, names='gene', color='gene',
                color_discrete_map={g: GENE_STYLE[g]['color'] for g in GENE_STYLE},
                hole=0.5, title="توزيع الجينات"
            ),
            use_container_width=True
        )
        col2.plotly_chart(
            px.bar(
                df.groupby('gene').size().reset_index(name='count'),
                x='gene', y='count', color='gene',
                color_discrete_map={g: GENE_STYLE[g]['color'] for g in GENE_STYLE},
                title="تعداد الأجسام المدارية"
            ),
            use_container_width=True
        )
    else:
        st.info("⚙️ انتظر تفعيل المفاعل، أو تأكد أن طبقة الخريطة الحرارية مفعّلة.")

# ==============================================================================
# [14] التبويب 3: البيان الختامي
# ==============================================================================
with tabs[3]:
    st.markdown("### 📜 البيان الختامي")
    if st.session_state.orbit_active and st.session_state.orbit_bodies:
        bodies = st.session_state.orbit_bodies
        total_e = sum(b['energy'] for b in bodies)
        genes_count = Counter(b['gene'] for b in bodies)
        dom_gene = max(genes_count, key=genes_count.get)
        cc = compute_collective_consciousness(bodies) if ENABLE_COLLECTIVE_LAYER else None
        ascent_vec = compute_ascent_vector(bodies) if ENABLE_ASCENT_VECTOR else 0.0

        extra_line = ""
        if cc:
            extra_line = (
                f"<br>🧠 مستوى الانسجام: <b>{cc['harmony_level']}</b> | "
                f"مستوى التوتر: <b>{cc['tension_level']}</b>"
            )
        ascent_line = ""
        if ENABLE_ASCENT_VECTOR:
            direction = "صعود" if ascent_vec > 0 else ("ثبات" if ascent_vec == 0 else "انحدار")
            ascent_line = f"<br>📈 متجه الصعود: <b>{ascent_vec}</b> ({direction})"

        st.markdown(f"""
        <div class="story-box">
            <b>بيان الاستواء الوجودي v29.0:</b><br>
            تم استنطاق <b>{len(bodies)}</b> جذراً.<br>
            الهيمنة الجينية: <b>{GENE_STYLE[dom_gene]['icon']} {GENE_STYLE[dom_gene]['name']}</b><br>
            مجموع الطاقة: <b>{total_e:.1f}</b>
            {extra_line}
            {ascent_line}
        </div>
        """, unsafe_allow_html=True)
        display_insight_cards(bodies)
    else:
        st.info("⚙️ انتظر تفعيل المفاعل.")

# ==============================================================================
# [15] التبويب 4: الميزان السيادي
# ==============================================================================
with tabs[4]:
    st.markdown("### ⚖️ ميزان النزاهة الجذرية - الاستحقاق المداري")
    if st.session_state.orbit_active and st.session_state.orbit_bodies:
        display_insight_cards(st.session_state.orbit_bodies)
    else:
        st.info("⚙️ انتظر تفعيل المفاعل.")

# ==============================================================================
# [16] التبويب 5: الوعي الفوقي
# ==============================================================================
with tabs[5]:
    st.markdown("### 🧠 الوعي الفوقي - البيان الجمعي الحراري")
    if st.session_state.orbit_active and st.session_state.orbit_bodies:
        bodies = st.session_state.orbit_bodies
        total_e = sum(b['energy'] for b in bodies)
        genes_count = Counter(b['gene'] for b in bodies)
        dom_gene = max(genes_count, key=genes_count.get)
        orbits_analysis = Counter(b.get('orbit_id_context', b.get('orbit_id', 0)) for b in bodies)
        cc = compute_collective_consciousness(bodies) if ENABLE_COLLECTIVE_LAYER else None
        ascent_vec = compute_ascent_vector(bodies) if ENABLE_ASCENT_VECTOR else 0.0

        extra_line = ""
        if cc:
            extra_line = (
                f"<br>🧠 مستوى الانسجام: <b>{cc['harmony_level']}</b> | "
                f"مستوى التوتر: <b>{cc['tension_level']}</b>"
            )
        ascent_line = ""
        if ENABLE_ASCENT_VECTOR:
            direction = "صعود" if ascent_vec > 0 else ("ثبات" if ascent_vec == 0 else "انحدار")
            ascent_line = f"<br>📈 متجه الصعود: <b>{ascent_vec}</b> ({direction})"

        st.markdown(f"""
        <div class="story-box">
            <h3 style='color:#FFD700;'>🌌 بيان الوعي الجمعي الحراري</h3>
            <b>عدد الجذور:</b> {len(bodies)}<br>
            <b>مجموع الطاقة:</b> {total_e:.1f}<br>
            <b>الهيمنة الجينية:</b> {GENE_STYLE[dom_gene]['icon']} {GENE_STYLE[dom_gene]['name']}<br>
            <b>توزيع المدارات:</b> {', '.join([f'المدار {k}({v})' for k, v in sorted(orbits_analysis.items()) if k > 0])}
            {extra_line}
            {ascent_line}
        </div>
        """, unsafe_allow_html=True)
        display_insight_cards(bodies)
    else:
        st.info("⚙️ انتظر تفعيل المفاعل.")
