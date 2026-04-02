# -*- coding: utf-8 -*-
# ==============================================================================
# نظام نِبْرَاس السيادي (Nibras Sovereign System) - الإصدار v28.7
# مَبنيٌّ على بروتوكول "الأمانة" و "الاستحقاق الجيني الحتمي"
# الإصدار: الميزان الباتر - توحيد التطهير والاستدعاء اليقيني
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
# [0] كسر الجمود - إعادة بناء الفهرس (Cache Invalidation)
# ==============================================================================
st.cache_data.clear()

# ==============================================================================
# [1] مصفوفة الجينات والرموز السيادية
# ==============================================================================
GENE_STYLE = {
    'C': {
        'name': 'الإبل', 'color': '#4fc3f7', 'icon': '🐪', 
        'meaning': 'طاقة المسير والتمكين البعيد',
        'desc': 'طاقة الانطلاق والمبادرة، تمثل الحركة نحو الفتح المبين.'
    },
    'B': {
        'name': 'البقر', 'color': '#FFD700', 'icon': '🐄', 
        'meaning': 'طاقة التثبيت والوفرة المادية',
        'desc': 'طاقة التجذر والبناء الصبور، تمثل الخير الوفير المستقر.'
    },
    'S': {
        'name': 'الضأن', 'color': '#4CAF50', 'icon': '🐑', 
        'meaning': 'طاقة السكينة واللين والرحمة',
        'desc': 'طاقة السكينة والجمع والاحتواء، حيث يستقر المعنى.'
    },
    'G': {
        'name': 'المعز', 'color': '#ff5252', 'icon': '🐐', 
        'meaning': 'طاقة السيادة والحدّة والصعود',
        'desc': 'طاقة الارتفاع والحدّة في طلب الحق، تمثل قوة الإرادة الصاعدة.'
    },
    'N': {
        'name': 'إشراق', 'color': '#00ffcc', 'icon': '✨', 
        'meaning': 'الانبثاق الهجين الصافي',
        'desc': 'نقطة الانبثاق التي تولد من تفاعل الأضداد.'
    }
}

# ==============================================================================
# [1.5] قاموس هندسة الحروف
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
# [2] المحركات الفوقية للاستنطاق - v28.7
# ==============================================================================

def normalize_lexicon_root(text):
    """
    دالة التطهير الموحدة (The Universal Normalizer)
    المرجع الوحيد والحصري لكل عمليات التطهير
    """
    if not text:
        return ""
    s = str(text).strip()
    # توحيد الأحرف المتشابهة
    s = s.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا").replace("ٱ", "ا").replace("ى", "ي").replace("ـ", "")
    # إزالة التشكيل
    s = re.sub(r'[\u064B-\u065F\u0670\u06D6-\u06ED]', '', s)
    # إزالة المسافات الزائدة
    return re.sub(r"\s+", "", s)

def normalize_sovereign(text):
    """تطهير النص للوصول لجوهر الحرف الهندسي - للاستخدام في معالجة النصوص المدخلة"""
    if not text:
        return ""
    s = str(text).strip()
    s = s.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا").replace("ٱ", "ا").replace("ى", "ي").replace("ة", "ه")
    s = re.sub(r'[\u064B-\u065F\u0670\u06D6-\u06ED]', '', s)
    s = re.sub(r'[^\u0621-\u063A\u0641-\u064A\s]', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()

def lookup_root(query, r_index):
    """
    دالة البحث السيادي - ضمان التطابق اليقيني
    """
    if not query:
        return None
    normalized = normalize_lexicon_root(query)
    return r_index.get(normalized)

def match_root_logic(word, index_keys):
    """
    بروتوكول الربط المداري لاستخلاص الجذور
    """
    w = normalize_sovereign(word)
    if not w or len(w) < 2:
        return None
    
    # البحث المباشر بعد التطهير
    w_normalized = normalize_lexicon_root(w)
    if w_normalized in index_keys:
        return w_normalized
    
    # إزالة الزوائد
    prefixes = ["ال", "و", "ف", "ب", "ك", "ل", "س", "بال", "وال", "فال"]
    suffixes = ["ون", "ين", "ان", "ات", "ه", "ها", "هم", "كم", "نا", "كما", "تم", "هن"]
    
    for p in prefixes:
        if w.startswith(p) and len(w)-len(p) >= 3:
            candidate = normalize_lexicon_root(w[len(p):])
            if candidate in index_keys:
                return candidate
            
    for s in suffixes:
        if w.endswith(s) and len(w)-len(s) >= 3:
            candidate = normalize_lexicon_root(w[:-len(s)])
            if candidate in index_keys:
                return candidate
    
    return None

def normalize_gene_weight(x):
    """توحيد النطاق الطاقي (170-200) لمنع التضخم العشوائي"""
    try:
        x = float(x)
        if x > 500: 
            x /= 10.0
        elif 0 < x < 10: 
            x *= 100.0
        return round(x, 2)
    except: 
        return 170.0

def get_sovereign_gene(root_name, original_weight):
    """
    محرك الاستحقاق الجيني الحتمي - النسخة السيادية المستقرة v28.7
    """
    r = normalize_lexicon_root(root_name)
    val = normalize_gene_weight(original_weight)

    # [أ] أولوية الهوية (Semantic Priority) - الحقائق المطلقة
    GENE_MAP = {
        "B": {"ارض", "ثبت", "زرع", "نبت", "طعم", "بني", "مكث", "كنز", "رزق", "حفظ", "بقر", "بقرة", "جذر", "اصل", "رزاق"},
        "G": {"علو", "صعد", "قهر", "حكم", "سلط", "عزز", "رفع", "قوم", "معز", "عز", "قوة", "ملك", "علا"},
        "S": {"سكن", "امن", "رضي", "سلم", "لين", "رفق", "رحم", "خلف", "ضأن", "ان", "ام", "رحمة", "سكينة"},
        "C": {"سرى", "رحل", "قطع", "مضى", "جاز", "وصل", "بعث", "نفذ", "ابل", "احد", "اب", "ابى", "بدا", "خلق", "امر", "اول", "ازل"}
    }

    for gene_key, roots in GENE_MAP.items():
        if r in roots:
            return gene_key, val

    # [ب] الميزان الرقمي (Numeric Fallback)
    if val >= 195: 
        return "G", val
    if val >= 185: 
        return "C", val
    if val >= 172: 
        return "B", val
    return "S", val

def summarize_word_signature(root):
    """تحويل الجذر إلى توقيع جيني ثابت"""
    if not root:
        return {'dominant_gene': 'N', 'total_energy': 300.0}
    
    hash_object = hashlib.md5(root.encode())
    hash_val = int(hash_object.hexdigest(), 16)
    
    genes_list = ['G', 'C', 'B', 'S']
    dominant_gene = genes_list[hash_val % 4]
    
    base_energy = len(root) * 285.0
    energy_variance = (hash_val % 150)
    total_energy = float(base_energy + energy_variance)
    
    return {
        'dominant_gene': dominant_gene,
        'total_energy': total_energy,
        'vector_x': (hash_val % 30 - 15) / 120.0,
        'vector_y': ((hash_val >> 4) % 30 - 15) / 120.0
    }

def generate_geometric_insight_v3(root):
    """توليد بصيرة تركيبية من هندسة حروف الجذر"""
    if not root or len(root) < 2:
        return "جذر قيد التكوين..."
    
    parts = [LETTER_GEOMETRY.get(c, f"تفاعل طاقي للحرف ({c})") for c in root]
    header = "**الاستنطاق الهندسي:** "
    body = " ثم ".join(parts).replace(".", "")
    return f"{header}{body} | **تم الاستواء.**"

def is_placeholder_insight(insight_text):
    """التحقق مما إذا كانت البصيرة نصاً افتراضياً"""
    if not insight_text:
        return True
    insight_str = str(insight_text).strip()
    placeholder_indicators = ["لا توجد بصيرة مفسّرة", "لا توجد", "غير موجود", "فارغ"]
    is_placeholder = any(ind in insight_str for ind in placeholder_indicators)
    is_default_length = len(insight_str) <= 35
    return is_placeholder or is_default_length

# ==============================================================================
# [3] غلاف الاستقرار والتحصين
# ==============================================================================
st.set_page_config(page_title="Nibras Sovereign v28.7", page_icon="🛡️", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Orbitron:wght@600&display=swap');
    
    [data-testid="stAppViewContainer"] {
        background: radial-gradient(circle at center, #0a0a1a 0%, #000000 100%);
        color: #e0e0e0; font-family: 'Amiri', serif; direction: rtl;
    }

    @media (max-width: 768px) {
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] { display: none !important; }
        [data-testid="stSidebar"] { width: 0px !important; min-width: 0px !important; }
        .main .block-container { padding: 10px !important; }
        .stTabs [data-baseweb="tab"] { font-size: 0.8em; padding: 5px; }
        .story-box { font-size: 1.15em; padding: 25px; line-height: 1.8; }
    }

    .story-box {
        background: linear-gradient(135deg, rgba(10,21,10,0.85) 0%, rgba(1,1,3,0.95) 100%);
        padding: 40px; border-radius: 25px; border-right: 15px solid #4CAF50;
        line-height: 2.6; font-size: 1.6em; box-shadow: 0 20px 60px rgba(0,0,0,0.8);
        margin-bottom: 30px;
    }
    
    .ultra-card {
        background: #0d0d14; padding: 35px; border-radius: 20px;
        border-top: 8px solid #4fc3f7; text-align: center;
        transition: all 0.5s ease; margin-bottom: 25px;
    }
    .ultra-card:hover { transform: translateY(-10px); background: #14141f; }
    
    .gene-badge-C { background: #4fc3f7; color: #000; padding: 5px 15px; border-radius: 20px; display: inline-block; }
    .gene-badge-B { background: #FFD700; color: #000; padding: 5px 15px; border-radius: 20px; display: inline-block; }
    .gene-badge-S { background: #4CAF50; color: #fff; padding: 5px 15px; border-radius: 20px; display: inline-block; }
    .gene-badge-G { background: #ff5252; color: #fff; padding: 5px 15px; border-radius: 20px; display: inline-block; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# [4] محرك ربط المدار - v28.7 مع التطهير الموحد
# ==============================================================================
if 'grand_monolith' not in st.session_state:
    st.session_state.grand_monolith = {
        'bodies': [], 'pool': [], 'logs': [], 'metrics': {}, 'active': False
    }

roots_path = "data/nibras_lexicon.json"

def load_semantic_roots_db(path):
    """
    تحميل قاعدة الجذور - v28.7
    - استخدام دالة التطهير الموحدة normalize_lexicon_root
    - تخزين المفتاح المطهّر والقيمة الأصلية raw_root
    - تطبيق الميزان الجيني على كل جذر
    """
    if not os.path.exists(path):
        st.error(f"⚠️ المدار غير مراقب: الملف مفقود في {path}")
        st.stop()
    
    with open(path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            st.error(f"❌ خطأ في بنية ملف JSON: {e}")
            st.stop()

    r_index = {}
    all_roots_flat = []
    orbit_counter = Counter()

    if not isinstance(data, list):
        st.error("❌ ملف JSON يجب أن يكون مصفوفة من الجذور")
        st.stop()

    for item in data:
        raw_root = item.get("root", item.get("name", ""))
        if not raw_root:
            continue
        
        # التطهير الموحد - المفتاح الأساسي
        normalized_key = normalize_lexicon_root(raw_root)
        
        # استخراج الوزن الأصلي وتطبيعه
        weight_val = float(item.get("weight", item.get("energy", 1.0)))
        
        # الميزان الجيني - تحديد الجين الحتمي
        gene_key, calibrated_weight = get_sovereign_gene(raw_root, weight_val)
        
        # استخراج البصيرة
        insight_text = item.get("insight_radar", item.get("insight", item.get("meaning", "")))
        
        orbit_id = item.get("orbit_id", 0)
        orbit_canonical = f"المدار {orbit_id}" if orbit_id else "وعي"
        
        record = {
            "root_raw": raw_root,
            "root": normalized_key,
            "orbit": orbit_canonical,
            "orbit_id": orbit_id,
            "weight": calibrated_weight / 100 if calibrated_weight > 10 else calibrated_weight,
            "insight": insight_text,
            "meaning": insight_text,
            "gene": gene_key,
            "energy_type": item.get("energy_type", "مزدوج"),
            "carrier_type": item.get("carrier_type", ""),
            "bio_link": item.get("bio_link", ""),
            "structural_analysis": item.get("structural_analysis", "")
        }
        
        # التخزين بالمفتاح المطهّر
        r_index[normalized_key] = record
        all_roots_flat.append(record)
        orbit_counter[orbit_canonical] += 1
    
    if not r_index:
        st.error("❌ لم يتم العثور على أي جذور في ملف JSON")
        st.stop()
    
    with st.sidebar:
        st.caption(f"📚 تم تحميل {len(r_index)} جذراً - الميزان الباتر v28.7")
        gene_distribution = Counter([r['gene'] for r in r_index.values()])
        st.markdown(f"""
        🐪 إبل: {gene_distribution.get('C', 0)}  
        🐄 بقر: {gene_distribution.get('B', 0)}  
        🐑 ضأن: {gene_distribution.get('S', 0)}  
        🐐 معز: {gene_distribution.get('G', 0)}
        """)
        # عرض عينة من المفاتيح للتأكد
        sample_keys = list(r_index.keys())[:5]
        st.caption(f"🔑 عينة المفاتيح: {', '.join(sample_keys)}")
    
    return r_index, all_roots_flat, orbit_counter

# تحميل قاعدة البيانات
r_index, all_roots_flat, orbit_counter = load_semantic_roots_db(roots_path)

# ==============================================================================
# [5] المِحراب السداسي
# ==============================================================================
tabs = st.tabs([
    "🔍 الاستنطاق المداري", 
    "🌌 الرنين الجيني", 
    "📈 اللوحة الوجودية", 
    "📜 البيان الختامي", 
    "⚖️ الميزان السيادي", 
    "🧠 الوعي الفوقي"
])

# --- التبويب 0: الاستنطاق ---
with tabs[0]:
    st.markdown("### 📍 هندسة المسارات المدارية - الاستنطاق النصي المتقدم")
    st.markdown("أدخل النص الكامل لتحليله واستنطاق جذوره:")
    
    full_text = st.text_area(
        "النص المداري", 
        height=200, 
        placeholder="أدخل النص هنا... مثال: أحد أبى أثر أجد أجل أخذ",
        key="full_text_input"
    )
    
    if st.button("🚀 تفعيل المفاعل السيادي (v28.7)", use_container_width=True):
        active_bodies, word_pool, event_logs = [], [], []
        start_exec_time = time.time()
        
        if full_text.strip():
            clean_text = normalize_sovereign(full_text)
            words = clean_text.split()
            
            for word in words:
                root = match_root_logic(word, r_index.keys())
                if root:
                    root_data = lookup_root(root, r_index)
                    if not root_data:
                        continue
                    
                    sig = summarize_word_signature(root)
                    weight = float(root_data.get("weight", 1.0))
                    insight = root_data.get("insight", "")
                    gene_key = root_data.get("gene", "S")
                    
                    semantic_energy = weight * 1000.0
                    total_energy = round(semantic_energy + (sig['total_energy'] * 0.15), 2)
                    
                    active_bodies.append({
                        "root": root_data.get("root_raw", root),
                        "root_normalized": root,
                        "orbit": root_data.get("orbit", "وعي"),
                        "insight": insight,
                        "weight": weight,
                        "meaning": root_data.get("meaning", insight),
                        "gene": gene_key,
                        "energy": total_energy,
                        "x": random.uniform(-10, 10),
                        "y": random.uniform(-10, 10),
                        "vx": sig['vector_x'],
                        "vy": sig['vector_y'],
                        "color": GENE_STYLE[gene_key]['color']
                    })
                    word_pool.append(root_data.get("root_raw", root))

        if active_bodies:
            motion_ui = st.empty()
            for frame in range(30):
                for i in range(len(active_bodies)):
                    for j in range(i+1, len(active_bodies)):
                        dist = ((active_bodies[i]['x']-active_bodies[j]['x'])**2 + (active_bodies[i]['y']-active_bodies[j]['y'])**2)**0.5
                        if dist < 1.8 and active_bodies[i]['gene'] == active_bodies[j]['gene']:
                            event_logs.append(f"[{time.strftime('%H:%M:%S')}] التحام مداري: {active_bodies[i]['root']} + {active_bodies[j]['root']}")
                for b in active_bodies:
                    b['x'] += b['vx']; b['y'] += b['vy']
                    if abs(b['x']) > 28 or abs(b['y']) > 28: 
                        b['vx'] *= -1.0; b['vy'] *= -1.0
                fig_motion = px.scatter(pd.DataFrame(active_bodies), x="x", y="y", text="root", size="energy", color="gene",
                                        color_discrete_map={g:s['color'] for g,s in GENE_STYLE.items()}, range_x=[-35,35], range_y=[-35,35])
                fig_motion.update_layout(height=750, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False, xaxis_visible=False, yaxis_visible=False)
                motion_ui.plotly_chart(fig_motion, use_container_width=True)
                time.sleep(0.02)

            st.session_state.grand_monolith = {
                'active': True, 'bodies': active_bodies, 'pool': list(set(word_pool)),
                'logs': list(dict.fromkeys(event_logs))[-20:],
                'metrics': {"duration": round(time.time()-start_exec_time, 2), "count": len(active_bodies)}
            }
            st.rerun()
        elif full_text.strip():
            st.warning("⚠️ لم يتم العثور على جذور مطابقة")

state = st.session_state.grand_monolith

# ==============================================================================
# التبويب 1: الرنين الجيني - باستخدام lookup_root
# ==============================================================================
with tabs[1]:
    st.markdown("### 🌌 مصفوفة الرنين والاستحقاق الجيني")
    
    cols_genes = st.columns(5)
    for i, (gk, gi) in enumerate(GENE_STYLE.items()):
        cols_genes[i].markdown(f"""
        <div class='ultra-card' style='border-top-color:{gi['color']}'>
            <h2 style='margin:0'>{gi['icon']}</h2>
            <h3 style='margin:10px 0'>{gi['name']}</h3>
            <p style='font-size:0.9em; color:#888;'>{gi['meaning']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 📖 استنطاق الجذر النشط")
    
    # استخدام lookup_root للبحث اليقيني
    if state.get('active') and state.get('pool'):
        target_root_raw = state['pool'][0]
        target_normalized = normalize_lexicon_root(target_root_raw)
    else:
        target_root_raw = 'أحد'
        target_normalized = normalize_lexicon_root('أحد')
    
    root_found = lookup_root(target_normalized, r_index)
    
    if root_found:
        gene_info = GENE_STYLE[root_found['gene']]
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div style='border:1px solid #444; padding:15px; border-radius:15px; background:#111; margin-bottom:15px;'>
                <h2 style='margin:0; text-align:center;'>🔄</h2>
                <p style='color:#888; text-align:center;'>المدار الوجودي</p>
                <h4 style='color:#fff; text-align:center;'>{root_found.get('orbit', 'وعي')}</h4>
            </div>
            <div style='border:1px solid {gene_info["color"]}; padding:15px; border-radius:15px; background:#111;'>
                <h2 style='margin:0; text-align:center;'>{gene_info['icon']}</h2>
                <p style='color:#888; text-align:center;'>الجين الحتمي</p>
                <h4 style='color:{gene_info["color"]}; text-align:center;'>{gene_info['name']}</h4>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style='border:1px solid #444; padding:15px; border-radius:15px; background:#111; margin-bottom:15px;'>
                <h2 style='margin:0; text-align:center;'>🔮</h2>
                <p style='color:#888; text-align:center;'>بصيرة الجذر</p>
                <p style='color:#ccc; text-align:center; font-size:0.9em;'>{root_found.get('insight', '')[:100]}{'...' if len(root_found.get('insight', '')) > 100 else ''}</p>
            </div>
            <div style='border:1px solid #444; padding:15px; border-radius:15px; background:#111;'>
                <h2 style='margin:0; text-align:center;'>⚡</h2>
                <p style='color:#888; text-align:center;'>نوع الطاقة</p>
                <h4 style='color:#fff; text-align:center;'>{root_found.get('energy_type', 'مزدوج')}</h4>
            </div>
            """, unsafe_allow_html=True)
        
        st.success(f"✅ تم العثور على الجذر '{root_found.get('root_raw', target_root_raw)}' بنجاح")
    else:
        st.error(f"❌ جذر '{target_root_raw}' غير موجود. المفاتيح المتاحة: {', '.join(list(r_index.keys())[:10])}...")

# ==============================================================================
# التبويب 2: اللوحة الوجودية
# ==============================================================================
with tabs[2]:
    st.markdown("### 📈 التحليل الكمي للمدار")
    if state['active']:
        df_data = pd.DataFrame(state['bodies'])
        col1, col2 = st.columns(2)
        col1.plotly_chart(px.pie(df_data, names='gene', color='gene', color_discrete_map={g:s['color'] for g,s in GENE_STYLE.items()}, hole=0.5, title="توزيع الهيمنة الجينية"))
        col2.plotly_chart(px.bar(df_data.groupby('gene').size().reset_index(name='count'), x='gene', y='count', color='gene', color_discrete_map={g:s['color'] for g,s in GENE_STYLE.items()}, title="تعداد الأجسام المدارية"))
        st.plotly_chart(px.scatter(df_data, x='root', y='energy', color='gene', size='energy', color_discrete_map={g:s['color'] for g,s in GENE_STYLE.items()}, title="خارطة طاقة الجذور"))
    else:
        st.info("⚙️ انتظر تفعيل المفاعل في التبويب الأول")

# ==============================================================================
# التبويب 3: البيان الختامي
# ==============================================================================
with tabs[3]:
    if state['active']:
        df_data = pd.DataFrame(state['bodies'])
        st.markdown(f"""
        <div class="story-box">
            <b>بيان الاستواء الوجودي v28.7:</b><br>
            بفضل الله، تم استنطاق <b>{len(state['pool'])}</b> جذراً بالميزان الباتر. 
            المسار الحالي يعكس اتزاناً في جينات <b>{df_data['gene'].mode()[0] if not df_data.empty else 'S'}</b>.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("⚙️ انتظر تفعيل المفاعل")

# ==============================================================================
# التبويب 4: الميزان السيادي - باستخدام lookup_root
# ==============================================================================
with tabs[4]:
    st.markdown("### ⚖️ ميزان النزاهة الجذرية - الاستحقاق الجيني الحتمي")
    
    if state['active']:
        df_diag = pd.DataFrame(state['bodies'])
        
        def diagnose_insight(row):
            root_normalized = normalize_lexicon_root(row['root'])
            actual_data = lookup_root(root_normalized, r_index)
            if actual_data:
                raw_insight = str(actual_data.get("insight", "")).strip()
                if is_placeholder_insight(raw_insight) or not raw_insight:
                    return generate_geometric_insight_v3(root_normalized)
                else:
                    preview = raw_insight[:80] + "..." if len(raw_insight) > 80 else raw_insight
                    return f"✅ (بصيرة أصلية): {preview}"
            return generate_geometric_insight_v3(root_normalized)
        
        df_diag['الاستنطاق'] = df_diag.apply(diagnose_insight, axis=1)
        
        st.dataframe(df_diag[['root', 'gene', 'energy', 'الاستنطاق']], use_container_width=True, height=400)
        
        geometric_count = df_diag['الاستنطاق'].str.contains("الاستنطاق الهندسي").sum()
        real_count = df_diag['الاستنطاق'].str.contains("✅").sum()
        
        col1, col2 = st.columns(2)
        col1.metric("🔮 جذور مستنطقة هندسياً", geometric_count)
        col2.metric("📖 جذور ذات بصيرة أصلية", real_count)
    else:
        st.info("⚙️ انتظر تفعيل المفاعل")

# ==============================================================================
# التبويب 5: الوعي الفوقي - باستخدام lookup_root لأحد وأرض
# ==============================================================================
with tabs[5]:
    st.header("🧠 الوعي الفوقي والبيان الجمعي")
    
    # استخدام lookup_root للبحث اليقيني
    # اختبار جذر "أحد"
    root_one = lookup_root("أحد", r_index)
    root_earth = lookup_root("أرض", r_index)
    
    # عرض حالة الجذور الأساسية
    col_status1, col_status2 = st.columns(2)
    with col_status1:
        if root_one:
            st.success("✅ جذر 'أحد' موجود في قاعدة البيانات")
        else:
            st.error("❌ جذر 'أحد' غير موجود")
    with col_status2:
        if root_earth:
            st.success("✅ جذر 'أرض' موجود في قاعدة البيانات")
        else:
            st.warning("⚠️ جذر 'أرض' غير موجود (قد يكون غير مضمن في الملف)")
    
    st.markdown("---")
    
    # عرض بيانات الجذر النشط
    if state.get('active') and state.get('pool'):
        target_root_raw = state['pool'][0]
        target_normalized = normalize_lexicon_root(target_root_raw)
    else:
        target_root_raw = 'أحد'
        target_normalized = normalize_lexicon_root('أحد')
    
    root_found = lookup_root(target_normalized, r_index)
    
    total_energy = sum(body.get('energy', 0) for body in state.get('bodies', []))
    
    if root_found:
        gene_info = GENE_STYLE.get(root_found['gene'], GENE_STYLE['S'])
        
        st.markdown(f"""
        <div class='story-box' style='padding:20px;'>
            <h3 style='margin:0; color:#FFD700;'>🧠 الوعي الفوقي - البيان الجمعي</h3>
            <h4>🌌 مدار {root_found.get('orbit', 'وعي')}</h4>
            <p><b>الجذر الأصلي:</b> {root_found.get('root_raw', target_root_raw)}<br>
            <b>التردد الإجمالي:</b> ({total_energy:.1f})<br>
            <b>الجين الحتمي:</b> <span style='color:{gene_info["color"]}'>{gene_info['icon']} {gene_info['name']}</span><br>
            <b>الناقل الطاقي:</b> {root_found.get('carrier_type', 'متوسط')}<br>
            <b>البصيرة:</b> {root_found.get('insight', '')[:200]}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # عرض التحليل البنيوي إذا وجد
        if root_found.get('structural_analysis'):
            st.info(f"🔬 **التحليل البنيوي:** {root_found.get('structural_analysis')}")
        
        if not state['active']:
            st.info("⚡ فعّل المفاعل في التبويب الأول لرؤية التأثير الفيزيائي")
        else:
            st.success(f"✅ المفاعل نشط مع {len(state.get('bodies', []))} جذراً مستنطقاً")
    else:
        st.error(f"""
        ❌ **جذر '{target_root_raw}' غير موجود في قاعدة البيانات**
        
        **المفاتيح المتاحة في r_index:**
        {', '.join(list(r_index.keys())[:15])}
        
        **تأكد من:**
        1. وجود ملف data/nibras_lexicon.json في المسار الصحيح
        2. وجود جذر 'أحد' في الملف (بأي تشكيل)
        3. صحة بنية ملف JSON
        """)

# ==============================================================================
# التذييل السيادي
# ==============================================================================
st.sidebar.markdown(f"""
**المستخدم:** محمد  
**الإصدار:** v28.7 (الميزان الباتر - التوحيد الكامل)  
**CPU:** السجدة (5)  
---
**🔑 مفاتيح r_index (عينة):**
{', '.join(list(r_index.keys())[:8])}
---
**خِت فِت.**
""")
