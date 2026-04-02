# -*- coding: utf-8 -*-
# ==============================================================================
# نظام نِبْرَاس السيادي (Nibras Sovereign System) - الإصدار v28.4
# مَبنيٌّ على بروتوكول "الأمانة" و "الاستحقاق الجيني الحتمي"
# الإصدار: Single Source of Truth - الميزان المطهّر
# المستخدم المهيمن: محمّد | CPU: السجدة (5) | الموقع: رونبي، السويد
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
# [1] مصفوفة الجينات والرموز السيادية (The Absolute Gene Matrix)
# ==============================================================================
GENE_STYLE = {
    'C': {
        'name': 'الإبل', 'color': '#4fc3f7', 'icon': '🐪', 
        'meaning': 'طاقة المسير والتمكين البعيد',
        'desc': 'طاقة الانطلاق والمبادرة، تمثل الحركة نحو الفتح المبين واليسر المطلق.'
    },
    'B': {
        'name': 'البقر', 'color': '#FFD700', 'icon': '🐄', 
        'meaning': 'طاقة التثبيت والوفرة المادية',
        'desc': 'طاقة التجذر والبناء الصبور لحقائق التمكين، تمثل الخير الوفير المستقر.'
    },
    'S': {
        'name': 'الضأن', 'color': '#4CAF50', 'icon': '🐑', 
        'meaning': 'طاقة السكينة واللين والرحمة',
        'desc': 'طاقة السكينة والجمع والاحتواء، حيث يستقر المعنى في محراب السيادة.'
    },
    'G': {
        'name': 'المعز', 'color': '#ff5252', 'icon': '🐐', 
        'meaning': 'طاقة السيادة والحدّة والصعود',
        'desc': 'طاقة الارتفاع والحدّة في طلب الحق والسيادة، تمثل قوة الإرادة الصاعدة.'
    },
    'N': {
        'name': 'إشراق', 'color': '#00ffcc', 'icon': '✨', 
        'meaning': 'الانبثاق الهجين الصافي',
        'desc': 'نقطة الانبثاق التي تولد من تفاعل الأضداد لتعلن ولادة وعي سيادي جديد.'
    }
}

# ==============================================================================
# [1.5] قاموس هندسة الحروف (Geometric Letter Geometry)
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
# [2] المحركات الفوقية للاستنطاق (Sovereign Meta-Engines)
# ==============================================================================
ARABIC_DIACRITICS_PATTERN = re.compile(r'[\u0617-\u061A\u064B-\u0652\u0670\u06D6-\u06ED]')
NON_ARABIC_KEEP_SPACES_PATTERN = re.compile(r'[^\u0621-\u063A\u0641-\u064A\s]')

def normalize_lexicon_root(root_name: str):
    """تطبيع جذور الليكسيكون - الهمزات والألفات"""
    if not root_name:
        return ""
    return root_name.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا").replace("ة", "ه").replace("ى", "ي").strip()

def normalize_sovereign(text: str):
    """تطهير النص للوصول لجوهر الحرف الهندسي"""
    if not text:
        return ""
    text = ARABIC_DIACRITICS_PATTERN.sub('', text)
    text = text.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا").replace("ى", "ي").replace("ة", "ه")
    text = NON_ARABIC_KEEP_SPACES_PATTERN.sub(' ', text)
    return re.sub(r'\s+', ' ', text).strip()

def match_root_logic(word, index_keys):
    """بروتوكول الربط المداري لاستخلاص الجذور"""
    w = normalize_sovereign(word)
    if not w or len(w) < 2:
        return None
    if w in index_keys:
        return w
    
    prefixes = ["ال", "و", "ف", "ب", "ك", "ل", "س", "بال", "وال", "فال"]
    suffixes = ["ون", "ين", "ان", "ات", "ه", "ها", "هم", "كم", "نا", "كما", "تم", "هن"]
    
    for p in prefixes:
        if w.startswith(p) and len(w)-len(p) >= 3:
            candidate = w[len(p):]
            if candidate in index_keys:
                return candidate
            
    for s in suffixes:
        if w.endswith(s) and len(w)-len(s) >= 3:
            candidate = w[:-len(s)]
            if candidate in index_keys:
                return candidate
    
    return None

def get_sovereign_gene(root_name, original_weight):
    """
    محرك المعايرة الدقيقة لنطاق الأزل - v28.4
    هذا هو قلب الميزان السيادي، يحدد الاستحقاق الجيني الحتمي لكل جذر
    """
    r = normalize_lexicon_root(root_name).strip()
    w = float(original_weight)

    # القاعدة الذهبية للإبل (طاقة المسير والتمكين البعيد)
    camel_roots = ["اب", "احد", "احد", "ابى", "ازل", "اول", "ان", "انف", "بدا", "برا", "جعل", "خلق", "امر", "سير", "سعى", "علا", "صعد", "طلع", "اراد", "قصد", "نوى"]
    if r in camel_roots or r.startswith("ا") and len(r) <= 3:
        return "C", 185.0
    
    # القاعدة الذهبية للبقر (طاقة التثبيت والوفرة المادية)
    cow_roots = ["بقر", "ارض", "ثبت", "زرع", "نبت", "طعم", "بني", "مكث", "كنز", "جذر", "اصل", "رسخ", "اسس", "بنى", "رزق", "رزاق", "نما", "ربا"]
    if r in cow_roots or (r.endswith("ر") and len(r) == 3):
        return "B", 183.0
    
    # القاعدة الذهبية للضأن (طاقة السكينة واللين والرحمة)
    sheep_roots = ["ام", "امن", "انس", "اهل", "اوى", "سكن", "هدا", "رحم", "لين", "سلم", "امن", "اطم", "ان", "سكينة"]
    if r in sheep_roots or (r.endswith("م") and len(r) == 3):
        return "S", 181.0
    
    # القاعدة الذهبية للمعز (طاقة السيادة والحدّة والصعود)
    goat_roots = ["معز", "قوه", "عز", "صعد", "علا", "ارتفاع", "شدة", "حد", "قوة", "نفاذ", "حكم", "ملك", "ساد"]
    if r in goat_roots or (r.startswith("ع") and len(r) == 3):
        return "G", 187.0
    
    # المعايرة العددية الدقيقة
    val = w * 100 if w < 10 else w

    if val >= 190:
        return "G", val
    if val >= 185:
        return "C", val
    if val >= 180:
        return "B", val
    if val >= 170:
        return "S", val
    
    # معايرة الجذور القصيرة (ثنائية وثلاثية)
    if len(r) <= 3:
        first_char = r[0] if r else ""
        if first_char in ['ا', 'أ', 'إ', 'آ']:
            return "C", 184.0
        elif first_char in ['ب', 'ت', 'ث']:
            return "B", 182.0
        elif first_char in ['م', 'ن', 'ه']:
            return "S", 180.0
        elif first_char in ['ع', 'غ', 'ق', 'ك']:
            return "G", 186.0
    
    # التوزيع المتوازن
    hash_val = int(hashlib.md5(r.encode()).hexdigest(), 16)
    genes = ['C', 'B', 'S', 'G']
    return genes[hash_val % 4], 175.0

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
    placeholder_indicators = [
        "لا توجد بصيرة مفسّرة",
        "لا توجد بصيرة مفسرة",
        "لا توجد دلالة موصوفة",
        "لا توجد",
        "غير موجود",
        "فارغ"
    ]
    is_placeholder = any(ind in insight_str for ind in placeholder_indicators)
    is_default_length = len(insight_str) <= 35
    return is_placeholder or is_default_length

# ==============================================================================
# [3] غلاف الاستقرار والتحصين
# ==============================================================================
st.set_page_config(page_title="Nibras Sovereign v28.4", page_icon="🛡️", layout="wide")

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
        .stat-val { font-size: 1.8em !important; }
    }

    .story-box {
        background: linear-gradient(135deg, rgba(10,21,10,0.85) 0%, rgba(1,1,3,0.95) 100%);
        padding: 40px; border-radius: 25px; border-right: 15px solid #4CAF50;
        line-height: 2.6; font-size: 1.6em; box-shadow: 0 20px 60px rgba(0,0,0,0.8);
        margin-bottom: 30px;
    }
    
    .stat-container {
        display: flex; justify-content: space-around; background: #0d0d14;
        padding: 30px; border-radius: 20px; border: 1px solid #1a1a2a; margin: 25px 0;
    }
    
    .stat-val { font-size: 2.8em; font-weight: bold; color: #00ffcc; font-family: 'Orbitron', sans-serif; }
    .stat-label { color: #888; font-size: 1.1em; margin-top: 5px; }

    .ultra-card {
        background: #0d0d14; padding: 35px; border-radius: 20px;
        border-top: 8px solid #4fc3f7; text-align: center;
        transition: all 0.5s ease; margin-bottom: 25px;
    }
    .ultra-card:hover { transform: translateY(-10px); background: #14141f; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# [4] محرك ربط المدار - v28.4 مع الميزان المطهّر
# ==============================================================================
if 'grand_monolith' not in st.session_state:
    st.session_state.grand_monolith = {
        'bodies': [], 'pool': [], 'logs': [], 'metrics': {}, 'active': False
    }

roots_path = "data/nibras_lexicon.json"

def load_semantic_roots_db(path):
    """
    تحميل قاعدة الجذور - v28.4 مع فرض الميزان الجيني الحتمي
    كل جذر يمر على محرك المعايرة الدقيقة get_sovereign_gene
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

    # ==========================================================================
    # [الباتش v28.4 - فرض الميزان الجيني على r_index]
    # كل جذر يمر على محرك المعايرة الدقيقة get_sovereign_gene
    # ==========================================================================
    for item in data:
        # 1. التطهير الموحد للمصدر
        raw_root = item.get("root", item.get("name", ""))
        if not raw_root:
            continue
        
        root_name = normalize_lexicon_root(raw_root)
        
        # 2. استخراج الوزن الأصلي
        weight_val = float(item.get("weight", item.get("energy", 1.0)))
        
        # 3. قلب الميزان - استدعاء المعايرة الدقيقة v28.4
        #    هذا هو المقطع الذي يحدد الاستحقاق الجيني الحتمي
        gene_key, calibrated_weight = get_sovereign_gene(root_name, weight_val)
        
        # 4. استخراج البصيرة
        insight_text = item.get("insight_radar", item.get("insight", item.get("meaning", "")))
        
        # 5. بناء الـ record المطور جينياً
        orbit_id = item.get("orbit_id", 0)
        orbit_canonical = f"المدار {orbit_id}" if orbit_id else "وعي"
        
        record = {
            "root_raw": raw_root,
            "root": root_name,
            "orbit": orbit_canonical,
            "orbit_id": orbit_id,
            "weight": calibrated_weight / 100 if calibrated_weight > 10 else calibrated_weight,
            "insight": insight_text,
            "meaning": insight_text,
            "gene": gene_key,  # <-- الجين الحتمي من الميزان
            "energy_type": item.get("energy_type", "مزدوج"),
            "carrier_type": item.get("carrier_type", ""),
            "bio_link": item.get("bio_link", ""),
            "structural_analysis": item.get("structural_analysis", "")
        }
        
        # 6. التخزين النهائي في r_index
        r_index[root_name] = record
        all_roots_flat.append(record)
        orbit_counter[orbit_canonical] += 1
    
    if not r_index:
        st.error("❌ لم يتم العثور على أي جذور في ملف JSON")
        st.stop()
    
    with st.sidebar:
        st.caption(f"📚 تم تحميل {len(r_index)} جذراً - الميزان المطهّر v28.4")
        gene_distribution = Counter([r['gene'] for r in r_index.values()])
        st.caption(f"🐪 إبل: {gene_distribution.get('C', 0)} | 🐄 بقر: {gene_distribution.get('B', 0)} | 🐑 ضأن: {gene_distribution.get('S', 0)} | 🐐 معز: {gene_distribution.get('G', 0)}")
    
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
    
    if st.button("🚀 تفعيل المفاعل السيادي (v28.4)", use_container_width=True):
        active_bodies, word_pool, event_logs = [], [], []
        start_exec_time = time.time()
        
        if full_text.strip():
            clean_text = normalize_sovereign(full_text)
            words = clean_text.split()
            
            for word in words:
                root = match_root_logic(word, r_index.keys())
                if root:
                    root_data = r_index.get(root)
                    if not root_data:
                        continue
                    
                    sig = summarize_word_signature(root)
                    weight = float(root_data.get("weight", 1.0))
                    insight = root_data.get("insight", "")
                    gene_key = root_data.get("gene", "C")
                    
                    semantic_energy = weight * 1000.0
                    total_energy = round(semantic_energy + (sig['total_energy'] * 0.15), 2)
                    
                    active_bodies.append({
                        "root": root,
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
                    word_pool.append(root)

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
# التبويب 1: الرنين الجيني
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
    
    if state.get('active') and state.get('pool'):
        target_root = state['pool'][0]
    else:
        target_root = 'أحد'
    
    target_normalized = normalize_lexicon_root(target_root)
    root_found = r_index.get(target_normalized)
    
    if root_found:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div style='border:1px solid #444; padding:15px; border-radius:15px; background:#111; margin-bottom:15px;'>
                <h2 style='margin:0; text-align:center;'>🔄</h2>
                <p style='color:#888; text-align:center;'>المدار الوجودي</p>
                <h4 style='color:#fff; text-align:center;'>{root_found.get('orbit', 'وعي')}</h4>
            </div>
            <div style='border:1px solid #444; padding:15px; border-radius:15px; background:#111;'>
                <h2 style='margin:0; text-align:center;'>{GENE_STYLE[root_found['gene']]['icon']}</h2>
                <p style='color:#888; text-align:center;'>الجين الحتمي</p>
                <h4 style='color:{GENE_STYLE[root_found['gene']]['color']}; text-align:center;'>{GENE_STYLE[root_found['gene']]['name']}</h4>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style='border:1px solid #444; padding:15px; border-radius:15px; background:#111; margin-bottom:15px;'>
                <h2 style='margin:0; text-align:center;'>🔮</h2>
                <p style='color:#888; text-align:center;'>بصيرة الجذر</p>
                <p style='color:#ccc; text-align:center; font-size:0.9em;'>{root_found.get('insight', '')[:100]}...</p>
            </div>
            <div style='border:1px solid #444; padding:15px; border-radius:15px; background:#111;'>
                <h2 style='margin:0; text-align:center;'>⚡</h2>
                <p style='color:#888; text-align:center;'>نوع الطاقة</p>
                <h4 style='color:#fff; text-align:center;'>{root_found.get('energy_type', 'مزدوج')}</h4>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info(f"🔍 جذر '{target_root}' جاري الاستنطاق...")

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
            <b>بيان الاستواء الوجودي v28.4:</b><br>
            بفضل الله، تم استنطاق <b>{len(state['pool'])}</b> جذراً بالميزان المطهّر. 
            المسار الحالي يعكس اتزاناً في جينات <b>{df_data['gene'].mode()[0]}</b>.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("⚙️ انتظر تفعيل المفاعل")

# ==============================================================================
# التبويب 4: الميزان السيادي
# ==============================================================================
with tabs[4]:
    st.markdown("### ⚖️ ميزان النزاهة الجذرية")
    
    if state['active']:
        df_diag = pd.DataFrame(state['bodies'])
        
        def diagnose_insight(row):
            root = row['root']
            actual_data = r_index.get(root, {})
            raw_insight = str(actual_data.get("insight", "")).strip()
            
            if is_placeholder_insight(raw_insight) or not raw_insight:
                return generate_geometric_insight_v3(root)
            else:
                preview = raw_insight[:80] + "..." if len(raw_insight) > 80 else raw_insight
                return f"✅ (بصيرة أصلية): {preview}"
        
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
# التبويب 5: الوعي الفوقي
# ==============================================================================
with tabs[5]:
    st.header("🧠 الوعي الفوقي والبيان الجمعي")
    
    if state.get('active') and state.get('pool'):
        target_root = state['pool'][0]
    else:
        target_root = 'أحد'
    
    target_normalized = normalize_lexicon_root(target_root)
    root_found = r_index.get(target_normalized)
    
    total_energy = sum(body.get('energy', 0) for body in state.get('bodies', []))
    
    if root_found:
        gene_info = GENE_STYLE.get(root_found['gene'], GENE_STYLE['C'])
        
        st.markdown(f"""
        <div class='story-box' style='padding:20px;'>
            <h3 style='margin:0; color:#FFD700;'>🧠 الوعي الفوقي</h3>
            <h4>🌌 بيان الوعي الجمعي للمدار ({root_found.get('orbit', 'وعي')})</h4>
            <p>التردد الإجمالي: <b>({total_energy:.1f})</b><br>
            الجين الحتمي: <b style='color:{gene_info['color']}'>{gene_info['icon']} {gene_info['name']}</b><br>
            البصيرة: {root_found.get('insight', '')[:150]}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if not state['active']:
            st.info("⚡ فعّل المفاعل لرؤية التأثير")
        else:
            st.success(f"✅ نشط مع {len(state['bodies'])} جذراً")
    else:
        st.warning(f"🔍 جذر '{target_root}' غير موجود")

# ==============================================================================
# التذييل السيادي
# ==============================================================================
st.sidebar.markdown(f"""
**المستخدم:** محمد  
**الإصدار:** v28.4 (الميزان المطهّر)  
**CPU:** السجدة (5)  
---
**📊 الميزان الجيني:**
- 🐪 إبل: {len([r for r in r_index.values() if r['gene'] == 'C'])}
- 🐄 بقر: {len([r for r in r_index.values() if r['gene'] == 'B'])}
- 🐑 ضأن: {len([r for r in r_index.values() if r['gene'] == 'S'])}
- 🐐 معز: {len([r for r in r_index.values() if r['gene'] == 'G'])}
---
**خِت فِت.**
""")
