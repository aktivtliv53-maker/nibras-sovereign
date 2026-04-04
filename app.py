# -*- coding: utf-8 -*-
# ==============================================================================
# نظام نِبْرَاس السيادي (Nibras Sovereign System) - الإصدار v29.5
# مَبنيٌّ على بروتوكول "الأمانة" و "الاستحقاق الجيني الحتمي"
# الإصدار: الطبقات المتقدمة - الصرف والطاقة الديناميكية ومؤشر الصعود
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
st.set_page_config(page_title="Nibras v29.5", page_icon="🛡️", layout="wide")

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
# [4] الطبقة الصرفية والمؤشر (Morphological Layer & Ascent Vector)
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
    w = word.replace("أ", "ا").replace("إ", "ا")
    if w.startswith("است"):
        return "استفعال", 8
    if w.startswith("افت"):
        return "افتعال", 5
    if len(w) == 3:
        return "فعل ثلاثي", 1
    return "مزيد/مركب", 3

def extract_candidate_root(word, index_keys):
    w_norm = word.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا").replace("ة", "ه").replace("ى", "ي")
    if w_norm in index_keys:
        return w_norm, "direct", *infer_morphological_pattern(w_norm)
    stripped = strip_affixes_ar(w_norm)
    if stripped in index_keys:
        return stripped, "stripped", *infer_morphological_pattern(w_norm)
    return None, "unresolved", *infer_morphological_pattern(w_norm)

def compute_ascent_vector(bodies):
    """حساب مؤشر الصعود والانحدار: المدارات 5-8 صعود، 1-4 انحدار/تثبيت"""
    if not bodies:
        return 0
    scores = [(b.get('orbit_id', 4) - 4.5) * b.get('energy', 100) for b in bodies]
    return round(sum(scores) / len(bodies), 2)

# ==============================================================================
# [5] محرك الطاقة الديناميكية والرنين (Dynamic Energy & Resonance)
# ==============================================================================
def compute_dynamic_energy(base_w, root, count, mode, orbit_hint):
    """حساب الطاقة الديناميكية مع عوامل التكرار والنمط الصرفي"""
    h = int(hashlib.md5(root.encode()).hexdigest(), 16) if root else 0
    sig_boost = (h % 100) * 0.1
    repetition_boost = 1.0 + math.log1p(max(0, count - 1)) * 0.35
    mode_factor = {"direct": 1.0, "stripped": 0.9, "unresolved": 0.6}.get(mode, 0.7)
    energy = (base_w * 100 * repetition_boost * mode_factor) + sig_boost
    return round(energy, 2)

def build_resonance_network(bodies):
    """بناء شبكة الرنين بين الجذور المستنطقة"""
    edges = []
    for a, b in combinations(range(len(bodies)), 2):
        ra, rb = bodies[a], bodies[b]
        dist = abs(ra.get('pos', a) - rb.get('pos', b))
        if dist < 6:
            strength = (1.0 / max(1, dist)) * (1.2 if ra.get('gene') == rb.get('gene') else 1.0)
            edges.append({
                "source": ra.get('root', '?'),
                "target": rb.get('root', '?'),
                "strength": round(strength, 3)
            })
    return sorted(edges, key=lambda x: x['strength'], reverse=True)

# ==============================================================================
# [6] محرك الاستحقاق الجيني - الربط المداري الحتمي
# ==============================================================================
def get_sovereign_gene(root_name, original_weight, orbit_id=0):
    """
    محرك الاستحقاق الجيني - الربط المداري الحتمي
    تصنيف المدارات:
    - المدارات 1-2: طاقة المسير والبدايات (إبل - C)
    - المدارات 3-4: طاقة التثبيت والوفرة (بقر - B)
    - المدارات 5-6: طاقة السيادة والصعود (معز - G)
    - المدارات 7-8 وما فوق: طاقة السكينة والجمع (ضأن - S)
    """
    orbit = int(orbit_id)
    
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
    
    calibrated_energy = original_weight * 100 if original_weight < 10 else original_weight
    return gene_key, calibrated_energy

def signature_from_root(root):
    """توقيع جيني ثابت لكل جذر للحركة المدارية"""
    if not root: 
        return {'total_energy': 300.0, 'vector_x': 0, 'vector_y': 0}
    h = int(hashlib.md5(root.encode()).hexdigest(), 16)
    return {
        'total_energy': len(root) * 285.0 + (h % 150),
        'vector_x': (h % 30 - 15) / 120.0,
        'vector_y': ((h >> 4) % 30 - 15) / 120.0
    }

# ==============================================================================
# [7] تحميل قاعدة البيانات
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
# [8] دوال العرض
# ==============================================================================
def display_insight_cards(bodies):
    """عرض الاستنطاق ككروت"""
    if not bodies:
        return
    for res in bodies:
        st.markdown(f"""
        <div class="insight-card" style="border-right-color: {res['color']}">
            <b style="color:{res['color']}; font-size:1.2em;">📌 الجذر: {res['root']}</b> | 
            🧬 الجين: {res['icon']} {res['gene_name']} | 
            ⚡ الطاقة: <span class="energy-badge">{res['energy']:.1f}</span> |
            🔄 المصدر: {res.get('source', res['root'])} | 
            📐 النمط: {res.get('pattern', 'مباشر')}
            <hr style="border:0.5px solid #333; margin:10px 0;">
            <p>🔮 {res['insight']}</p>
        </div>
        """, unsafe_allow_html=True)

# ==============================================================================
# [9] تهيئة حالة الجلسة
# ==============================================================================
if 'orbit_bodies' not in st.session_state:
    st.session_state.orbit_bodies = []
    st.session_state.orbit_active = False

# تحميل قاعدة البيانات
r_index, all_roots, orbit_counter = load_lexicon_db("data/nibras_lexicon.json")

# الشريط الجانبي
with st.sidebar:
    st.markdown(f"""
    <div style='text-align:center;'>
        <h2 style='color:#4fc3f7;'>🛡️ نبراس السيادي</h2>
        <p>الإصدار v29.5 - الطبقات المتقدمة</p>
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
# [10] التبويبات السيادية
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

# --- التبويب 0: الاستنطاق (المعالجة المطورة v29.5) ---
with tabs[0]:
    st.markdown("### 📍 هندسة المسارات المدارية - الطبقات المتقدمة v29.5")
    
    full_text = st.text_area(
        "أدخل النص للاستنطاق:", 
        height=150, 
        placeholder="مثال: أحد أبى أثر أجد أجل أخذ",
        key="input_area"
    )
    
    if st.button("🚀 تفعيل المفاعل السيادي v29.5", use_container_width=True):
        if full_text.strip():
            clean_text = normalize_sovereign(full_text)
            words = clean_text.split()
            
            bodies = []
            word_pool = []
            temp_meta = []
            
            # ================================================================
            # مفاعل المعالجة المطور v29.5 - مع الطبقة الصرفية
            # ================================================================
            for pos, word in enumerate(words):
                rk, mode, pat, p_oid = extract_candidate_root(word, r_index.keys())
                temp_meta.append({
                    "word": word, "pos": pos, "rk": rk, 
                    "mode": mode, "pat": pat, "p_oid": p_oid
                })
                if rk and rk not in word_pool:
                    word_pool.append(rk)
            
            counts = Counter(word_pool)
            
            for m in temp_meta:
                if m['rk']:
                    data = r_index.get(m['rk'])
                    if data:
                        # حساب الطاقة الديناميكية
                        dynamic_energy = compute_dynamic_energy(
                            data['weight'], m['rk'], 
                            counts[m['rk']], m['mode'], m['p_oid']
                        )
                        gene_info = GENE_STYLE.get(data['gene'], GENE_STYLE['S'])
                        
                        bodies.append({
                            "root": data['root_raw'],
                            "orbit": data['orbit'],
                            "orbit_id": data.get('orbit_id', 0),
                            "gene": data['gene'],
                            "gene_name": gene_info['name'],
                            "icon": gene_info['icon'],
                            "energy": dynamic_energy,
                            "insight": data['insight'],
                            "color": gene_info['color'],
                            "pos": m['pos'],
                            "mode": m['mode'],
                            "pattern": m['pat'],
                            "source": m['word'],
                            "x": random.uniform(-10, 10),
                            "y": random.uniform(-10, 10),
                            "vx": 0,
                            "vy": 0
                        })
            
            if bodies:
                st.session_state.orbit_bodies = bodies
                st.session_state.orbit_active = True
                
                # مؤشر الصعود والانحدار السيادي
                ascent_score = compute_ascent_vector(bodies)
                ascent_class = "ascent-positive" if ascent_score > 0 else "ascent-negative" if ascent_score < 0 else ""
                st.markdown(f"""
                <div class="{ascent_class}" style='padding: 20px; border-radius: 15px; margin-bottom: 20px; text-align: center;'>
                    <h3 style='margin:0;'>🚀 مؤشر الصعود والانحدار السيادي</h3>
                    <p style='font-size: 2em; margin:5px; font-weight:bold;'>{ascent_score}</p>
                    <p style='margin:0;'>{'صعود طاقي نحو المعاني العلوية' if ascent_score > 0 else 'تثبيت مادي في الجذور الأرضية' if ascent_score < 0 else 'توازن بين الصعود والثبات'}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # رسم بياني ثابت
                df = pd.DataFrame(bodies)
                fig = px.scatter(df, x="x", y="y", text="root", size="energy", color="gene",
                                 color_discrete_map={g: GENE_STYLE[g]['color'] for g in GENE_STYLE},
                                 range_x=[-35, 35], range_y=[-35, 35])
                fig.update_layout(
                    height=450, 
                    paper_bgcolor='rgba(0,0,0,0)', 
                    plot_bgcolor='rgba(0,0,0,0)',
                    showlegend=False, 
                    xaxis_visible=False, 
                    yaxis_visible=False,
                    margin=dict(l=0, r=0, t=0, b=0)
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # البيان الختامي الموسع
                st.markdown("### 📜 البيان الختامي الموسع")
                total_e = sum(b['energy'] for b in bodies)
                genes_count = Counter(b['gene'] for b in bodies)
                dom_gene = max(genes_count, key=genes_count.get)
                
                orbits_detail = Counter(f"المدار {b['orbit_id']}" for b in bodies if b.get('orbit_id'))
                
                st.markdown(f"""
                <div class="story-box">
                    ✅ تم استنطاق <b>{len(bodies)}</b> جذراً.<br>
                    🐪 الهيمنة الجينية: <b>{GENE_STYLE[dom_gene]['icon']} {GENE_STYLE[dom_gene]['name']}</b><br>
                    ⚡ مجموع الطاقة الديناميكية: <b>{total_e:.1f}</b><br>
                    📚 الجذور: <b>{', '.join(word_pool)}</b><br>
                    🎯 توزيع المدارات: {', '.join([f'{k}({v})' for k, v in orbits_detail.items()])}
                </div>
                """, unsafe_allow_html=True)
                
                # عرض كروت الاستنطاق
                display_insight_cards(bodies)
                st.success("✅ تم الاستنطاق بنجاح.")
            else:
                st.error("⚠️ لم يتم العثور على جذور مطابقة.")
        else:
            st.warning("⚠️ الرجاء إدخال نص.")

# --- التبويب 1: الرنين الجيني ---
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
                st.markdown(f"""
                <div class='insight-card' style='border-right-color:{gi["color"]}'>
                    <b style='color:{gi["color"]}'>📌 الجذر: {found['root_raw']}</b><br>
                    🧬 الجين: {gi['icon']} {gi['name']}<br>
                    🔄 المدار: {found['orbit']} (ID: {found.get('orbit_id', 0)})<br>
                    ⚡ الطاقة الأساسية: {found.get('raw_energy', found['weight']*100):.1f}<br>
                    <hr>
                    <p>🔮 {found['insight']}</p>
                </div>
                """, unsafe_allow_html=True)

# --- التبويب 2: اللوحة الوجودية ---
with tabs[2]:
    st.markdown("### 📈 التحليل الكمي للمدار")
    if st.session_state.orbit_active and st.session_state.orbit_bodies:
        df = pd.DataFrame(st.session_state.orbit_bodies)
        col1, col2 = st.columns(2)
        col1.plotly_chart(px.pie(df, names='gene', color='gene', color_discrete_map={g: GENE_STYLE[g]['color'] for g in GENE_STYLE}, hole=0.5, title="توزيع الجينات"))
        col2.plotly_chart(px.bar(df.groupby('gene').size().reset_index(name='count'), x='gene', y='count', color='gene', color_discrete_map={g: GENE_STYLE[g]['color'] for g in GENE_STYLE}, title="تعداد الأجسام المدارية"))
        st.plotly_chart(px.scatter(df, x='root', y='energy', color='gene', size='energy', color_discrete_map={g: GENE_STYLE[g]['color'] for g in GENE_STYLE}, title="خارطة طاقة الجذور"))
        
        if 'orbit_id' in df.columns:
            orbit_df = df.groupby('orbit_id').size().reset_index(name='count')
            st.plotly_chart(px.bar(orbit_df, x='orbit_id', y='count', title="توزيع الجذور حسب المدار", labels={'orbit_id': 'رقم المدار', 'count': 'عدد الجذور'}))
    else:
        st.info("⚙️ انتظر تفعيل المفاعل.")

# --- التبويب 3: البيان الختامي ---
with tabs[3]:
    st.markdown("### 📜 البيان الختامي")
    if st.session_state.orbit_active and st.session_state.orbit_bodies:
        bodies = st.session_state.orbit_bodies
        total_e = sum(b['energy'] for b in bodies)
        genes_count = Counter(b['gene'] for b in bodies)
        dom_gene = max(genes_count, key=genes_count.get)
        st.markdown(f"""
        <div class="story-box">
            <b>بيان الاستواء الوجودي v29.5:</b><br>
            تم استنطاق <b>{len(bodies)}</b> جذراً.<br>
            الهيمنة الجينية: <b>{GENE_STYLE[dom_gene]['icon']} {GENE_STYLE[dom_gene]['name']}</b><br>
            مجموع الطاقة الديناميكية: <b>{total_e:.1f}</b>
        </div>
        """, unsafe_allow_html=True)
        display_insight_cards(bodies)
    else:
        st.info("⚙️ انتظر تفعيل المفاعل.")

# --- التبويب 4: الميزان السيادي ---
with tabs[4]:
    st.markdown("### ⚖️ ميزان النزاهة الجذرية - الاستحقاق المداري")
    if st.session_state.orbit_active and st.session_state.orbit_bodies:
        display_insight_cards(st.session_state.orbit_bodies)
    else:
        st.info("⚙️ انتظر تفعيل المفاعل.")

# --- التبويب 5: الوعي الفوقي ---
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

# --- التبويب 6: الرنين السياقي (جديد) ---
with tabs[6]:
    st.markdown("### 📡 الرنين السياقي - شبكة العلاقات بين الجذور")
    if st.session_state.orbit_active and st.session_state.orbit_bodies:
        bodies = st.session_state.orbit_bodies
        resonance_edges = build_resonance_network(bodies)
        
        if resonance_edges:
            df_edges = pd.DataFrame(resonance_edges)
            st.markdown("#### 🌐 شبكة الرنين (الروابط القوية)")
            st.dataframe(df_edges, use_container_width=True)
            
            # عرض أقوى 5 روابط
            st.markdown("#### 💫 أقوى 5 روابط طاقية")
            for edge in resonance_edges[:5]:
                st.markdown(f"""
                <div style='background: rgba(255,255,255,0.05); padding: 10px; border-radius: 10px; margin-bottom: 5px;'>
                    🔗 <b>{edge['source']}</b> ⇄ <b>{edge['target']}</b> : قوة الرنين <b>{edge['strength']}</b>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("لا توجد روابط رنين قوية بين الجذور المستنطقة.")
    else:
        st.info("⚙️ انتظر تفعيل المفاعل.")

# --- التبويب 7: المنحنى الزمني (جديد) ---
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
                    "الجين": b['gene']
                })
            
            df_seq = pd.DataFrame(seq_data)
            
            fig = px.line(df_seq, x="الترتيب", y="الطاقة", markers=True, title="منحنى تدفق الطاقة في النص",
                          labels={"الترتيب": "موقع الجذر في النص", "الطاقة": "قيمة الطاقة"})
            fig.update_traces(line_color='#00ffcc', marker_color='#FFD700', marker_size=10)
            fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
            
            # عرض الجدول الزمني
            st.markdown("#### 📋 التسلسل الزمني للجذور")
            st.dataframe(df_seq[["الترتيب", "الجذر", "الطاقة", "المدار", "الجين"]], use_container_width=True)
            
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
