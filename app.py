# -*- coding: utf-8 -*-
# ==============================================================================
# نظام نِبْرَاس السيادي (Nibras Sovereign System) - الإصدار v30.1
# مَبنيٌّ على بروتوكول "الأمانة" و "الاستحقاق الجيني الحتمي"
# الإصدار: مرحلة الاستواء الكامل - البيان الختامي الموسع
# المستخدم المهيمن: محمّد | CPU: السجدة (5)
# ==============================================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import re
import random
import os
import json
import time
import hashlib
import numpy as np

# ==============================================================================
# [0] إعدادات العرض - منع القص (Truncation)
# ==============================================================================
pd.set_option('display.max_colwidth', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

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
# [1.5] لوحة ألوان سيادية — تدرّجات جاهزة
# ==============================================================================
GENE_COLORS = [
    "#4fc3f7", "#ffb74d", "#81c784", "#ba68c8",
    "#e57373", "#64b5f6", "#ffd54f", "#4db6ac"
]

def pick_color(index):
    return GENE_COLORS[index % len(GENE_COLORS)]

# ==============================================================================
# [2] قاموس هندسة الحروف (للاستنطاق الهندسي)
# ==============================================================================
LETTER_GEOMETRY = {
    'ا': 'امتداد عمودي، صلة بين العلوي والأرضي، تدفق طاقي مستقيم.',
    'ب': 'ظهور أرضي، احتواء أفقي، نقطة الوعي تحت المسار.',
    'ت': 'استقرار فوقي، جمع وتراكم، وعي مزدوج بالقمة.',
    'ث': 'ثبات، وعي بالاستمرارية، حسم في المسار.',
    'ج': 'حركة لولبية، طاقة حيوية ممتدة، ذيل طاقي واصل.',
    'ح': 'احتواء حار، طاقة حياة صافية، سكون إيجابي.',
    'خ': 'اختراق علوي، وعي بالنقطة فوق المقام، تميز سيادي.',
    'د': 'رسوخ زاوي، ثبات واتجاه، استناد مادي.',
    'ذ': 'تميز، وعي بالتفرد، نقطة الانفراد.',
    'ر': 'انطلاق سائل، تكرار طاقي، ذيل ممتد نحو الغيب.',
    'ز': 'زخم، حركة دائرية، وعي بالدوران.',
    'س': 'تردد تموجي، انتشار أفقي، أسنان القوة الناعمة.',
    'ش': 'انتشار مشع، طاقة ثلاثية الأبعاد، وعي علوي مثلث.',
    'ص': 'إحكام صلب، تجميع مركزي، بروز هوياتي.',
    'ض': 'احاطة، وعي شامل، حصر مطلق.',
    'ط': 'سمو مرتفع، طاقة صاعدة، هيمنة مقامية.',
    'ظ': 'ظهور، وعي بالغيب، انبثاق من الخفاء.',
    'ع': 'عمق وعين، انفتاح على الباطن، طاقة وعي سحيقة.',
    'غ': 'غيب، وعي بالمجهول، طاقة خفية.',
    'ف': 'فصل، تمييز، قطع ووصل.',
    'ق': 'قوة دائرية، وعي فوقي بنقطتين، حسم مداري.',
    'ك': 'احتواء عالي، كنف الحماية، انحناء الوعي الشامل.',
    'ل': 'اتصال وانسياب، تعلق بالعلوي، امتداد طولي واصل.',
    'م': 'جمع ميمي، انغلاق البداية والنهاية، طاقة المحيط.',
    'ن': 'احتواء نوني، نقطة الوعي في قلب الرحم الطاقي.',
    'ه': 'هوية لطيفة، تدفق هوائي، وعي مركزي مفتوح.',
    'و': 'وصل مداري، دوران طاقي، ربط بين الأبعاد.',
    'ي': 'امتداد أخير، رجوع للمركز، وعي بالخاتمة.'
}

# ==============================================================================
# [3] دوال التطهير والتوحيد
# ==============================================================================

def normalize_root(text):
    """دالة التطهير المطلقة - تحول أي جذر إلى مفتاح موحد للبحث"""
    if not text:
        return ""
    s = str(text).strip()
    s = s.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا").replace("ٱ", "ا")
    s = s.replace("ى", "ي").replace("ة", "ه")
    s = s.replace("ـ", "")
    s = re.sub(r'[\u064B-\u065F\u0670\u06D6-\u06ED]', '', s)
    return s

def normalize_input_text(text):
    """تطهير النص المدخل للاستنطاق"""
    if not text:
        return ""
    s = str(text).strip()
    s = s.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا").replace("ٱ", "ا")
    s = s.replace("ى", "ي").replace("ة", "ه")
    s = re.sub(r'[\u064B-\u065F\u0670\u06D6-\u06ED]', '', s)
    s = re.sub(r'[^\u0621-\u063A\u0641-\u064A\s]', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()

def ensure_dot(text):
    """ضمان انتهاء النص بنقطة"""
    if not text:
        return ""
    s = str(text).strip()
    if not s.endswith('.'):
        s = s + '.'
    return s

# ==============================================================================
# [4] الميزان الجيني الحتمي
# ==============================================================================

def normalize_gene_weight(x):
    """توحيد النطاق الطاقي (170-200)"""
    try:
        x = float(x)
        if x > 500:
            x /= 10.0
        elif 0 < x < 10:
            x *= 100.0
        return round(x, 2)
    except:
        return 175.0

def get_sovereign_gene(root_name, original_weight):
    """محرك الاستحقاق الجيني الحتمي"""
    r = normalize_root(root_name)
    val = normalize_gene_weight(original_weight)

    GENE_MAP = {
        "B": {"ارض", "ثبت", "زرع", "نبت", "طعم", "بني", "مكث", "كنز", "رزق", "حفظ", "بقر", "بقرة", "جذر", "اصل", "رزاق", "ترب", "حجر", "حصد", "جثث", "جذر", "جير", "حمل"},
        "G": {"علو", "صعد", "قهر", "حكم", "سلط", "عزز", "رفع", "قوم", "معز", "عز", "قوة", "ملك", "علا", "جحد", "جرى", "جند", "جهد", "جور", "جوز", "جول", "حيد", "حمر", "حمس", "تعب"},
        "S": {"سكن", "امن", "رضي", "سلم", "لين", "رفق", "رحم", "خلف", "ضأن", "ان", "ام", "رحمة", "سكينة", "اذن", "انس", "اهل", "اوى", "بشر", "بطن", "جسم", "جمع", "جمل", "جود", "جوف", "حبل", "حبب", "حرم", "حشر", "حضر", "حفظ", "حلم"},
        "C": {"سرى", "رحل", "قطع", "مضى", "جاز", "وصل", "بعث", "نفذ", "ابل", "احد", "اب", "ابى", "بدا", "خلق", "امر", "اول", "ازل", "اب", "ابى", "اجل", "اخذ", "اربع", "اسر", "اف", "اق", "ال", "الم", "ان", "انف", "اول", "برا", "بصر", "بعد", "تاب", "توب", "تقى", "جبل", "جوب", "جوه", "حسب", "حمد", "حول", "خبر", "ختم", "خلف"}
    }

    for gene_key, roots in GENE_MAP.items():
        if r in roots:
            return gene_key, val

    if val >= 195:
        return "G", val
    if val >= 185:
        return "C", val
    if val >= 172:
        return "B", val
    return "S", val

def extract_root_from_word(word, index_keys):
    """استخراج الجذر من كلمة مدخلة - بحث شامل"""
    w = normalize_input_text(word)
    if not w or len(w) < 2:
        return None
    
    w_norm = normalize_root(w)
    if w_norm in index_keys:
        return w_norm
    
    prefixes = ["ال", "و", "ف", "ب", "ك", "ل", "س", "بال", "وال", "فال", "لل", "للا"]
    for p in prefixes:
        if w.startswith(p) and len(w) - len(p) >= 2:
            candidate = normalize_root(w[len(p):])
            if candidate in index_keys:
                return candidate
    
    suffixes = ["ون", "ين", "ان", "ات", "ه", "ها", "هم", "كم", "نا", "كما", "تم", "هن", "ي", "ة"]
    for s in suffixes:
        if w.endswith(s) and len(w) - len(s) >= 2:
            candidate = normalize_root(w[:-len(s)])
            if candidate in index_keys:
                return candidate
    
    return None

def generate_geometric_insight(root):
    """توليد بصيرة هندسية من حروف الجذر"""
    if not root or len(root) < 2:
        return "جذر قيد التكوين."
    parts = [LETTER_GEOMETRY.get(c, f"تفاعل طاقي للحرف ({c})") for c in root]
    result = "الاستنطاق الهندسي: " + " ثم ".join(parts) + ". تم الاستواء."
    return ensure_dot(result)

def is_placeholder(insight):
    """التحقق من كون البصيرة نصاً افتراضياً"""
    if not insight:
        return True
    s = str(insight).strip()
    indicators = ["لا توجد", "غير موجود", "فارغ", "قيد التكوين"]
    return any(i in s for i in indicators) or len(s) <= 35

def signature_from_root(root):
    """توقيع جيني ثابت لكل جذر"""
    if not root:
        return {'dominant_gene': 'N', 'total_energy': 300.0, 'vector_x': 0, 'vector_y': 0}
    h = int(hashlib.md5(root.encode()).hexdigest(), 16)
    genes = ['G', 'C', 'B', 'S']
    return {
        'dominant_gene': genes[h % 4],
        'total_energy': len(root) * 285.0 + (h % 150),
        'vector_x': (h % 30 - 15) / 120.0,
        'vector_y': ((h >> 4) % 30 - 15) / 120.0
    }

# ==============================================================================
# [5] تحميل قاعدة البيانات من nibras_lexicon.json
# ==============================================================================

@st.cache_data(ttl=3600)
def load_lexicon_db(path):
    """تحميل الليكسيكون بالكامل وربطه بقاعدة البيانات"""
    if not os.path.exists(path):
        st.error(f"❌ ملف الليكسيكون غير موجود: {path}")
        st.stop()
    
    with open(path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            st.error(f"❌ خطأ في JSON: {e}")
            st.stop()
    
    if not isinstance(data, list):
        st.error("❌ الليكسيكون يجب أن يكون مصفوفة")
        st.stop()
    
    r_index = {}
    all_roots = []
    
    for item in data:
        raw_root = item.get("root", "")
        if not raw_root:
            continue
        
        normalized_key = normalize_root(raw_root)
        carrier = item.get("carrier_type", "")
        weight_val = item.get("weight", 50.0)
        
        if weight_val == 1.0 and carrier:
            weight_map = {"إبل": 185, "بقر": 180, "ضأن": 175, "معز": 190}
            weight_val = weight_map.get(carrier, 175)
        
        gene_key, cal_weight = get_sovereign_gene(raw_root, weight_val)
        insight_text = item.get("insight_radar", item.get("insight", ""))
        
        record = {
            "root_raw": raw_root,
            "root": normalized_key,
            "orbit_id": item.get("orbit_id", 0),
            "orbit": f"المدار {item.get('orbit_id', 0)}" if item.get('orbit_id') else "وعي",
            "energy_type": item.get("energy_type", "مزدوج"),
            "carrier_type": carrier,
            "bio_link": item.get("bio_link", ""),
            "structural_analysis": item.get("structural_analysis", ""),
            "insight": ensure_dot(insight_text),
            "meaning": ensure_dot(insight_text),
            "gene": gene_key,
            "weight": cal_weight / 100 if cal_weight > 10 else cal_weight
        }
        
        r_index[normalized_key] = record
        all_roots.append(record)
    
    if not r_index:
        st.error("❌ لم يتم العثور على أي جذور في الليكسيكون")
        st.stop()
    
    return r_index, all_roots

# ==============================================================================
# [6] دالة عرض الاستنطاق الكامل + البيان الختامي
# ==============================================================================

def display_sovereign_results(bodies_list):
    """عرض الجذور والاستنطاق ككتل نصية كاملة مع البيان الختامي في الأعلى"""
    if not bodies_list:
        st.info("لا توجد بيانات حالياً.")
        return
    
    # ========== البيان الختامي الجماعي ==========
    total_energy = sum(b.get('energy', 0) for b in bodies_list)
    genes_count = Counter(b.get('gene', 'S') for b in bodies_list)
    dominant_gene = max(genes_count, key=genes_count.get)
    gene_info = GENE_STYLE.get(dominant_gene, GENE_STYLE['S'])
    
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #0a1a0a 0%, #051005 100%); padding: 25px; border-radius: 20px; border-right: 5px solid {gene_info["color"]}; margin-bottom: 30px;'>
        <h3 style='margin:0 0 15px 0; color:#FFD700;'>📜 البيان الختامي الموسع</h3>
        <p style='margin:8px 0;'>✅ تم استنطاق <b>{len(bodies_list)}</b> جذراً.</p>
        <p style='margin:8px 0;'>🐪 الهيمنة الجينية: <b style='color:{gene_info["color"]};'>{gene_info['icon']} {gene_info['name']}</b></p>
        <p style='margin:8px 0;'>⚡ مجموع الطاقة: <b>{total_energy:.1f}</b></p>
        <p style='margin:8px 0;'>📚 الجذور المستنطقة: <b>{', '.join([b.get('root', '—') for b in bodies_list])}</b></p>
    </div>
    """, unsafe_allow_html=True)
    
    # ========== تفاصيل كل جذر على حدة ==========
    st.markdown("### 🔍 تفاصيل الاستنطاق")

    for i, res in enumerate(bodies_list):
        root_name = res.get("root", "—")
        insight_content = res.get("insight") or res.get("meaning") or ""

        # معالجة النصوص الناقصة أو المقصوصة
        if not insight_content or "..." in str(insight_content):
            insight_content = generate_geometric_insight(root_name)

        final_text = ensure_dot(insight_content)

        # اختيار اللون: إمّا من البيانات أو من اللوحة
        gene_color = res.get("color") or pick_color(i)

        block = f"""
        <div style="
            border-right: 4px solid {gene_color};
            padding: 12px 18px;
            margin-bottom: 18px;
            background: rgba(255,255,255,0.04);
            border-radius: 6px;
        ">
            <div style="color:{gene_color}; font-weight:bold; font-size:1.15em;">
                📌 الجذر: {root_name}
            </div>
            <div style="color:#ddd; line-height:1.8; margin-top:6px;">
                🔮 <b>الاستنطاق:</b> {final_text}
            </div>
        </div>
        """

        st.markdown(block, unsafe_allow_html=True)

# ==============================================================================
# [7] تهيئة التطبيق
# ==============================================================================

st.set_page_config(page_title="نبراس السيادي v30.1", page_icon="🛡️", layout="wide")

# CSS النظيف - بدون عناصر عائمة أو أعمدة رأسية
st.markdown("""
<style>
    [data-testid="stAppViewContainer"] {
        background: radial-gradient(circle at center, #0a0a1a 0%, #000000 100%);
        color: #e0e0e0;
        font-family: 'Amiri', serif;
        direction: rtl;
    }
    .story-box {
        background: linear-gradient(135deg, rgba(10,21,10,0.85) 0%, rgba(1,1,3,0.95) 100%);
        padding: 35px;
        border-radius: 25px;
        border-right: 15px solid #4CAF50;
        line-height: 2;
        font-size: 1.2em;
        margin-bottom: 30px;
    }
    .ultra-card {
        background: #0d0d14;
        padding: 20px;
        border-radius: 20px;
        border-top: 8px solid #4fc3f7;
        text-align: center;
        margin-bottom: 20px;
    }
    /* إخفاء أي عناصر عائمة غير مرغوب فيها */
    .st-emotion-cache-1v0mbdj, .st-emotion-cache-1wivap2, .st-emotion-cache-zq5wmm {
        display: none;
    }
    /* تحسين شكل حقل الإدخال */
    .stTextArea textarea {
        background: #0d0d14;
        color: #e0e0e0;
        border: 1px solid #2a2a3a;
        border-radius: 10px;
        font-family: 'Amiri', serif;
        font-size: 1.1em;
    }
    /* تحسين شكل الأزرار */
    .stButton button {
        background: linear-gradient(135deg, #1a472a 0%, #0d2a1a 100%);
        color: #e0e0e0;
        border: 1px solid #4CAF50;
        border-radius: 10px;
        font-family: 'Amiri', serif;
        font-size: 1.1em;
        padding: 10px 25px;
    }
    .stButton button:hover {
        background: linear-gradient(135deg, #2a573a 0%, #1a3a2a 100%);
        border-color: #6fbf6f;
    }
</style>
""", unsafe_allow_html=True)

# تحميل الليكسيكون من قاعدة البيانات
ROOTS_PATH = "data/nibras_lexicon.json"
r_index, all_roots = load_lexicon_db(ROOTS_PATH)

# حالة الجلسة
if 'active_bodies' not in st.session_state:
    st.session_state.active_bodies = []
    st.session_state.active_pool = []
    st.session_state.is_active = False

# الشريط الجانبي النظيف
with st.sidebar:
    st.markdown(f"""
    <div style='text-align:center; padding:10px;'>
        <h2 style='color:#4fc3f7; margin:0;'>🛡️ نبراس السيادي</h2>
        <p style='color:#888; margin:5px 0;'>الإصدار v30.1</p>
        <p style='color:#555; margin:0;'>المستخدم: محمد</p>
    </div>
    ---
    <div style='padding:5px;'>
        <p style='color:#4CAF50; margin:0 0 10px 0;'>📊 إحصائيات القاعدة:</p>
        <p style='margin:3px 0;'>📚 إجمالي الجذور: <span style='color:#4fc3f7;'>{len(r_index)}</span></p>
        <p style='margin:3px 0;'>🐪 الإبل: <span style='color:#4fc3f7;'>{len([r for r in r_index.values() if r['gene'] == 'C'])}</span></p>
        <p style='margin:3px 0;'>🐄 البقر: <span style='color:#FFD700;'>{len([r for r in r_index.values() if r['gene'] == 'B'])}</span></p>
        <p style='margin:3px 0;'>🐑 الضأن: <span style='color:#4CAF50;'>{len([r for r in r_index.values() if r['gene'] == 'S'])}</span></p>
        <p style='margin:3px 0;'>🐐 المعز: <span style='color:#ff5252;'>{len([r for r in r_index.values() if r['gene'] == 'G'])}</span></p>
    </div>
    ---
    <div style='text-align:center; padding:10px;'>
        <p style='color:#555; margin:0;'>خِت فِت.</p>
    </div>
    """, unsafe_allow_html=True)

# ==============================================================================
# [8] الواجهة الرئيسية - التبويبات
# ==============================================================================

tabs = st.tabs(["🔍 الاستنطاق المداري", "🌌 الرنين الجيني", "📈 اللوحة الوجودية", "📜 البيان الختامي", "⚖️ الميزان السيادي", "🧠 الوعي الفوقي"])

# ==================== التبويب 0: الاستنطاق ====================
with tabs[0]:
    st.markdown("### 📍 الاستنطاق المداري - تحليل النصوص")
    
    input_text = st.text_area(
        "أدخل النص للاستنطاق:",
        height=120,
        placeholder="مثال: أحد أبى أثر أجد أجل أخذ أذن أرب أرض أزل أسر أصل أفق",
        key="input_area"
    )
    
    if st.button("🚀 تفعيل المفاعل السيادي", use_container_width=True):
        if input_text.strip():
            clean = normalize_input_text(input_text)
            words = clean.split()
            
            bodies = []
            pool = []
            
            for idx, word in enumerate(words):
                root_key = extract_root_from_word(word, r_index.keys())
                if root_key:
                    data = r_index.get(root_key)
                    if data:
                        sig = signature_from_root(root_key)
                        energy = data['weight'] * 1000 + sig['total_energy'] * 0.15
                        bodies.append({
                            "root": data['root_raw'],
                            "orbit": data['orbit'],
                            "gene": data['gene'],
                            "energy": round(energy, 2),
                            "insight": data['insight'],
                            "meaning": data['meaning'],
                            "color": pick_color(idx),
                            "x": random.uniform(-10, 10),
                            "y": random.uniform(-10, 10),
                            "vx": sig['vector_x'],
                            "vy": sig['vector_y']
                        })
                        pool.append(data['root_raw'])
            
            if bodies:
                st.session_state.active_bodies = bodies
                st.session_state.active_pool = list(set(pool))
                st.session_state.is_active = True
                
                # رسم بياني للحركة المدارية
                fig = px.scatter(pd.DataFrame(bodies), x="x", y="y", text="root", size="energy", color="gene",
                                 color_discrete_map={g: GENE_STYLE[g]['color'] for g in GENE_STYLE},
                                 range_x=[-35, 35], range_y=[-35, 35])
                fig.update_layout(height=450, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                  showlegend=False, xaxis_visible=False, yaxis_visible=False)
                st.plotly_chart(fig, use_container_width=True)
                
                # عرض البيان الختامي الموسع + تفاصيل الاستنطاق
                display_sovereign_results(bodies)
                
            else:
                st.error("⚠️ لم يتم العثور على جذور. تأكد من إدخال كلمات صحيحة.")
        else:
            st.warning("⚠️ الرجاء إدخال نص للاستنطاق.")

# ==================== التبويب 1: الرنين الجيني ====================
with tabs[1]:
    st.markdown("### 🌌 مصفوفة الرنين الجيني")
    
    cols = st.columns(4)
    for i, (code, info) in enumerate(GENE_STYLE.items()):
        if i < 4:
            cols[i].markdown(f"""
            <div class='ultra-card' style='border-top-color:{info["color"]}'>
                <h2 style='margin:0;'>{info['icon']}</h2>
                <h3 style='margin:10px 0 5px 0;'>{info['name']}</h3>
                <p style='margin:0; font-size:0.9em; color:#aaa;'>{info['meaning']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 📖 استنطاق جذر محدد")
    
    # قائمة منسدلة بكل الجذور المتاحة
    root_options = sorted([r['root_raw'] for r in all_roots])
    selected_root_display = st.selectbox("اختر جذراً:", options=root_options, index=0 if root_options else None)
    
    if selected_root_display:
        normalized = normalize_root(selected_root_display)
        found = r_index.get(normalized)
        
        if found:
            gene_info = GENE_STYLE[found['gene']]
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                <div style='border:1px solid #2a2a3a; padding:15px; border-radius:15px; background:#0d0d14; margin-bottom:15px;'>
                    <p style='color:#888; margin:0;'>📌 الجذر الأصلي</p>
                    <h3 style='margin:5px 0 0 0; color:#4fc3f7;'>{found['root_raw']}</h3>
                </div>
                <div style='border:1px solid {gene_info["color"]}; padding:15px; border-radius:15px; background:#0d0d14;'>
                    <p style='color:#888; margin:0;'>🧬 الجين الحتمي</p>
                    <h3 style='margin:5px 0 0 0; color:{gene_info["color"]};'>{gene_info['icon']} {gene_info['name']}</h3>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div style='border:1px solid #2a2a3a; padding:15px; border-radius:15px; background:#0d0d14; margin-bottom:15px;'>
                    <p style='color:#888; margin:0;'>🔄 المدار الوجودي</p>
                    <h3 style='margin:5px 0 0 0;'>{found['orbit']}</h3>
                </div>
                <div style='border:1px solid #2a2a3a; padding:15px; border-radius:15px; background:#0d0d14;'>
                    <p style='color:#888; margin:0;'>⚡ نوع الطاقة</p>
                    <h3 style='margin:5px 0 0 0;'>{found['energy_type']}</h3>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div style='border:1px solid #4CAF50; padding:20px; border-radius:15px; background:#0a1a0a; margin-top:15px;'>
                <p style='color:#4CAF50; margin:0 0 10px 0; font-weight:bold;'>🔮 بصيرة الجذر</p>
                <p style='margin:0; line-height:1.7; color:#ddd;'>{ensure_dot(found['insight'])}</p>
            </div>
            """, unsafe_allow_html=True)

# ==================== التبويب 2: اللوحة الوجودية ====================
with tabs[2]:
    st.markdown("### 📈 التحليل الكمي للمدار")
    if st.session_state.is_active and st.session_state.active_bodies:
        df = pd.DataFrame(st.session_state.active_bodies)
        col1, col2 = st.columns(2)
        col1.plotly_chart(px.pie(df, names='gene', color='gene', color_discrete_map={g: GENE_STYLE[g]['color'] for g in GENE_STYLE}, hole=0.5, title="توزيع الجينات"))
        col2.plotly_chart(px.bar(df.groupby('gene').size().reset_index(name='count'), x='gene', y='count', color='gene', color_discrete_map={g: GENE_STYLE[g]['color'] for g in GENE_STYLE}, title="تعداد الأجسام المدارية"))
        st.plotly_chart(px.scatter(df, x='root', y='energy', color='gene', size='energy', color_discrete_map={g: GENE_STYLE[g]['color'] for g in GENE_STYLE}, title="خارطة طاقة الجذور"))
    else:
        st.info("⚙️ انتظر تفعيل المفاعل في التبويب الأول.")

# ==================== التبويب 3: البيان الختامي ====================
with tabs[3]:
    st.markdown("### 📜 البيان الختامي")
    if st.session_state.is_active and st.session_state.active_bodies:
        display_sovereign_results(st.session_state.active_bodies)
    else:
        st.info("⚙️ انتظر تفعيل المفاعل في التبويب الأول.")

# ==================== التبويب 4: الميزان السيادي ====================
with tabs[4]:
    st.markdown("### ⚖️ ميزان النزاهة الجذرية")
    if st.session_state.is_active and st.session_state.active_bodies:
        display_sovereign_results(st.session_state.active_bodies)
    else:
        st.info("⚙️ انتظر تفعيل المفاعل في التبويب الأول.")

# ==================== التبويب 5: الوعي الفوقي ====================
with tabs[5]:
    st.markdown("### 🧠 الوعي الفوقي - البيان الجمعي")
    
    if st.session_state.is_active and st.session_state.active_bodies:
        display_sovereign_results(st.session_state.active_bodies)
    else:
        st.info("⚙️ انتظر تفعيل المفاعل في التبويب الأول.")
