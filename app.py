# -*- coding: utf-8 -*-
# ==============================================================================
# نظام نِبْرَاس السيادي (Nibras Sovereign System) - الإصدار v27.8-Final
# مَبنيٌّ على بروتوكول "الأمانة" و "الاستحقاق الجيني الحتمي"
# الإصدار: Precision Calibration - المعايرة الدقيقة لنطاق الأزل (1.7-2.0)
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
    'ج': 'حركة لولبية، طاقة حيوية ممتدة، ذيل طاقي واصل.',
    'ح': 'احتواء حار، طاقة حياة صافية، سكون إيجابي.',
    'خ': 'اختراق علوي، وعي بالنقطة فوق المقام، تميز سيادي.',
    'د': 'رسوخ زاوي، ثبات واتجاه، استناد مادي.',
    'ر': 'انطلاق سائل، تكرار طاقي، ذيل ممتد نحو الغيب.',
    'س': 'تردد تموجي، انتشار أفقي، أسنان القوة الناعمة.',
    'ش': 'انتشار مشع، طاقة ثلاثية الأبعاد، وعي علوي مثلث.',
    'ص': 'إحكام صلب، تجميع مركزي، بروز هوياتي.',
    'ط': 'سمو مرتفع، طاقة صاعدة، هيمنة مقامية.',
    'ع': 'عمق وعين، انفتاح على الباطن، طاقة وعي سحيقة.',
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
# أنماط التطهير المتقدمة
ARABIC_DIACRITICS_PATTERN = re.compile(r'[\u0617-\u061A\u064B-\u0652\u0670\u06D6-\u06ED]')
NON_ARABIC_KEEP_SPACES_PATTERN = re.compile(r'[^\u0621-\u063A\u0641-\u064A\s]')

def normalize_sovereign(text: str):
    """تطهير النص للوصول لجوهر الحرف الهندسي - نسخة متقدمة"""
    if not text: return ""
    text = ARABIC_DIACRITICS_PATTERN.sub('', text)
    text = text.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا").replace("ى", "ي").replace("ة", "ه")
    text = NON_ARABIC_KEEP_SPACES_PATTERN.sub(' ', text)
    return re.sub(r'\s+', ' ', text).strip()

def match_root_logic(word, index_keys):
    """بروتوكول الربط المداري لاستخلاص الجذور الثلاثية - نسخة متقدمة"""
    w = normalize_sovereign(word)
    if not w or len(w) < 2: return None
    if w in index_keys: return w
    
    prefixes = ["ال", "و", "ف", "ب", "ك", "ل", "س", "بال", "وال", "فال"]
    suffixes = ["ون", "ين", "ان", "ات", "ه", "ها", "هم", "كم", "نا", "كما", "تم", "هن"]
    
    for p in prefixes:
        if w.startswith(p) and len(w)-len(p) >= 3:
            candidate = w[len(p):]
            if candidate in index_keys: return candidate
            
    for s in suffixes:
        if w.endswith(s) and len(w)-len(s) >= 3:
            candidate = w[:-len(s)]
            if candidate in index_keys: return candidate
    
    return None

def get_sovereign_gene(root_name, original_weight):
    """
    محرك المعايرة الدقيقة لنطاق الأزل (1.7 - 2.0) - v27.8 Precision Calibration
    إعادة توزيع الأوزان العالية على الأنعام الأربعة وفق عتبات حساسة
    """
    r = normalize_sovereign(root_name).strip()
    w = float(original_weight)

    # 1. نظام الحوكمة بالهوية (الأولوية القصوى)
    cow_roots = ["رزق", "رزاق", "ارض", "ثبت", "زرع", "نبت", "طعم", "بني", "مكث", "كنز"]
    if r in cow_roots:
        return "B", 55.0

    # 2. إعادة معايرة "العتبات الحرجة" (Critical Thresholds)
    # نحول الرقم من (1.84) إلى (184) لسهولة الحساب
    val = w * 100 if w < 10 else w

    # الميزان الجديد المتكيف مع أرقام "الأزل" في معجمك:
    if val >= 190:
        return "G", val  # المعز: للقيم الفائقة (حق، حيي، قدوس)
    if val >= 185:
        return "C", val  # الإبل: للقيم العالية (قدر، ملك، عظم)
    if val >= 180:
        return "B", val  # البقر: للقيم المتوسطة في الأزل (رزاق، غفور، سميع)
    if val >= 170:
        return "S", val  # الضأن: للقيم اللطيفة (شكور، تواب، لطيف)
    
    # للمدارات الأخرى التي قد تحمل أوزاناً طبيعية
    if val > 80:
        return "G", val
    if val > 60:
        return "C", val
    if val > 40:
        return "B", val
    return "S", val

def summarize_word_signature(root):
    """تحويل الجذر إلى توقيع جيني ثابت (Deterministic Signature)."""
    if not root: return {'dominant_gene': 'N', 'total_energy': 300.0}
    
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
    """توليد بصيرة تركيبية من هندسة حروف الجذر - نسخة محكمة الإغلاق"""
    if not root or len(root) < 2:
        return "جذر قيد التكوين..."
    
    parts = [LETTER_GEOMETRY.get(c, f"تفاعل طاقي للحرف ({c})") for c in root]
    header = "**الاستنطاق الهندسي:** "
    body = " ثم ".join(parts).replace(".", "")
    return f"{header}{body} | **تم الاستواء.**"

def generate_collective_insight(bodies):
    """توليد وعي جمعي للمدار بأكمله"""
    if not bodies:
        return "المدار في حالة سكون."
    
    genes = [b['gene'] for b in bodies]
    dom_gene = max(set(genes), key=genes.count)
    total_e = sum(b['energy'] for b in bodies)
    
    header = f"### 🌌 بيان الوعي الجمعي للمدار (v27.8-Final)\n"
    analysis = f"هذا المسار يمثل منظومة طاقية بتردد إجمالي قدره **({total_e:.1f})**. يهيمن عليه جين **{GENE_STYLE[dom_gene]['name']}**، مما يوجه التدفق نحو **{GENE_STYLE[dom_gene]['meaning']}**."
    narrative = f"\n\n**تسلسل التمكين:** يتدفق الوعي عبر محاور {' -> '.join([b['root'] for b in bodies[:5]])} ليخلق استواءً وجودياً."
    
    return f"{header}{analysis}{narrative}"

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
# [3] غلاف الاستقرار والتحصين (Advanced Shielding CSS)
# ==============================================================================
st.set_page_config(page_title="Nibras Sovereign v27.8-Final", page_icon="🛡️", layout="wide")

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

    .adaptive-log {
        background: #000; border: 1px solid #ffaa00; padding: 25px;
        color: #ffaa00; font-family: 'Courier New', monospace;
        height: 300px; overflow-y: auto; border-radius: 15px;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# [4] محرك ربط المدار (Data Core & Session State)
# ==============================================================================
if 'grand_monolith' not in st.session_state:
    st.session_state.grand_monolith = {
        'bodies': [], 'pool': [], 'logs': [], 'metrics': {}, 'active': False
    }

# مسار الملف - هيكل المدارات
roots_path = "data/nibras_lexicon.json"

def load_semantic_roots_db(path):
    """تحميل قاعدة الجذور من هيكل المدارات (Orbit-based Structure)"""
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
    all_roots_flat = {}
    orbit_counter = Counter()

    for batch in data.values():
            if isinstance(batch, list):
                for item in batch:
                    root_name = item.get("الجذر", item.get("root", ""))
                    if root_name: all_roots_flat[root_name] = item
            elif isinstance(batch, dict):
                all_roots_flat.update(batch)

    r_index = list(all_roots_flat.keys())
    orbit_counter = len(all_roots_flat)
    return r_index, all_roots_flat, orbit_counter
    r_index = list(all_roots_flat.keys())
    orbit_counter = len(all_roots_flat)
    return r_index, all_roots_flat, orbit_counter
            
    r_index[root_name] = record
    all_roots_flat.append(record)
    orbit_counter[orbit_canonical] += 1
    
    return r_index, all_roots_flat, orbit_counter

# تحميل قاعدة البيانات
r_index, all_roots_flat, orbit_counter = load_semantic_roots_db(roots_path)

# ==============================================================================
# [5] المِحراب السداسي - صرح البيانات
# ==============================================================================
tabs = st.tabs([
    "🔍 الاستنطاق المداري", 
    "🌌 الرنين الجيني", 
    "📈 اللوحة الوجودية", 
    "📜 البيان الختامي", 
    "⚖️ الميزان السيادي", 
    "🧠 الوعي الفوقي"
])

# --- التبويب 1: الاستنطاق - نسخة مطورة بمربع نص واحد ---
with tabs[0]:
    st.markdown("### 📍 هندسة المسارات المدارية - الاستنطاق النصي المتقدم")
    st.markdown("أدخل النص الكامل لتحليله واستنطاق جذوره:")
    
    full_text = st.text_area(
        "النص المداري", 
        height=200, 
        placeholder="أدخل النص هنا... سيقوم النظام باستخراج الجذور وتحليلها فوراً.",
        key="full_text_input"
    )
    
    if st.button("🚀 تفعيل المفاعل السيادي (v27.8-Final)", use_container_width=True):
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
                    orbit_name = root_data.get("orbit", "وعي")
                    orbit_raw = root_data.get("orbit_raw", orbit_name)
                    weight = float(root_data.get("weight", 1.0))
                    insight = root_data.get("insight", "")
                    gene_key = root_data.get("gene", sig['dominant_gene'])
                    semantic_energy = weight * 1000.0
                    total_energy = round(semantic_energy + (sig['total_energy'] * 0.15), 2)
                    active_bodies.append({
                        "root": root,
                        "orbit": orbit_name,
                        "orbit_raw": orbit_raw,
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
            for _ in range(120):
                for i in range(len(active_bodies)):
                    for j in range(i+1, len(active_bodies)):
                        dist = ((active_bodies[i]['x']-active_bodies[j]['x'])**2 + (active_bodies[i]['y']-active_bodies[j]['y'])**2)**0.5
                        if dist < 1.8 and active_bodies[i]['gene'] == active_bodies[j]['gene']:
                            event_logs.append(f"[{time.strftime('%H:%M:%S')}] التحام مداري محقق: {active_bodies[i]['root']} + {active_bodies[j]['root']}")
                for b in active_bodies:
                    b['x'] += b['vx']; b['y'] += b['vy']
                    if abs(b['x']) > 28 or abs(b['y']) > 28: 
                        b['vx'] *= -1.0; b['vy'] *= -1.0
                fig_motion = px.scatter(pd.DataFrame(active_bodies), x="x", y="y", text="root", size="energy", color="gene",
                                        color_discrete_map={g:s['color'] for g,s in GENE_STYLE.items()}, range_x=[-35,35], range_y=[-35,35])
                fig_motion.update_layout(height=750, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False, xaxis_visible=False, yaxis_visible=False)
                motion_ui.plotly_chart(fig_motion, use_container_width=True)
                time.sleep(0.01)

            st.session_state.grand_monolith = {
                'active': True, 'bodies': active_bodies, 'pool': list(set(word_pool)),
                'logs': list(dict.fromkeys(event_logs))[-20:],
                'metrics': {"duration": round(time.time()-start_exec_time, 2), "count": len(active_bodies)}
            }
            st.rerun()

state = st.session_state.grand_monolith

with tabs[1]:
    st.markdown("### 🌌 مصفوفة الرنين والاستحقاق الجيني")
    cols_genes = st.columns(5)
    for i, (gk, gi) in enumerate(GENE_STYLE.items()):
        cols_genes[i].markdown(f"""
        <div class='ultra-card' style='border-top-color:{gi['color']}'>
            <h2 style='margin:0'>{gi['icon']}</h2>
            <h3 style='margin:10px 0'>{gi['name']}</h3>
            <p style='font-size:0.9em; color:#888;'>{gi['meaning']}</p>
            <small style='display:block; margin-top:10px;'>{gi['desc']}</small>
        </div>
        """, unsafe_allow_html=True)

if state['active']:
    df_data = pd.DataFrame(state['bodies'])
    
    with tabs[2]:
        st.markdown("### 📈 التحليل الكمي للمدار")
        cl, cr = st.columns(2)
        cl.plotly_chart(px.pie(df_data, names='gene', color='gene', color_discrete_map={g:s['color'] for g,s in GENE_STYLE.items()}, hole=0.5, title="توزيع الهيمنة الجينية"))
        cr.plotly_chart(px.bar(df_data.groupby('gene').size().reset_index(name='count'), x='gene', y='count', color='gene', color_discrete_map={g:s['color'] for g,s in GENE_STYLE.items()}, title="تعداد الأجسام المدارية"))
        st.plotly_chart(px.scatter(df_data, x='root', y='energy', color='gene', size='energy', color_discrete_map={g:s['color'] for g,s in GENE_STYLE.items()}, title="خارطة طاقة الجذور"))

    with tabs[3]:
        st.markdown(f"""
        <div class="story-box">
            <b>بيان الاستواء الوجودي v27.8-Final:</b><br>
            بفضل الله، تم استنطاق <b>{len(state['pool'])}</b> جذراً قرآنياً بنظام المعايرة الدقيقة لنطاق الأزل. 
            المسار الحالي يعكس اتزاناً في جينات <b>{GENE_STYLE[df_data['gene'].mode()[0]]['name']}</b>، 
            مما يؤكد مقام <b>الخير واليسر</b> في هذا المدار. كل حرف هنا هو وتدٌ في صرح التمكين.
        </div>
        """, unsafe_allow_html=True)

    with tabs[4]:
        st.markdown("### ⚖️ ميزان النزاهة الجذرية والاستنطاق الهجين")
        
        if state['active']:
            df_diag = pd.DataFrame(state['bodies'])
            
            def diagnose_insight_hybrid(row):
                root = row['root']
                actual_data = r_index.get(root, {})
                raw_insight = str(actual_data.get("insight", "")).strip()
                
                if is_placeholder_insight(raw_insight):
                    return generate_geometric_insight_v3(root)
                else:
                    preview = raw_insight[:80] + "..." if len(raw_insight) > 80 else raw_insight
                    return f"✅ (قاعدة البيانات): {preview}"
            
            df_diag['حالة البيانات'] = df_diag.apply(diagnose_insight_hybrid, axis=1)
            
            st.dataframe(
                df_diag[['root', 'gene', 'energy', 'حالة البيانات']],
                column_config={
                    "root": st.column_config.TextColumn("الجذر", width="small"),
                    "gene": st.column_config.TextColumn("الجين", width="small"),
                    "energy": st.column_config.NumberColumn("الطاقة", format="%.2f", width="small"),
                    "حالة البيانات": st.column_config.TextColumn("الاستنطاق الهندسي / البصيرة", width="large")
                },
                use_container_width=True,
                height=400
            )
            
            geometric_count = df_diag['حالة البيانات'].str.contains("الاستنطاق الهندسي").sum()
            real_insight_count = df_diag['حالة البيانات'].str.contains("✅ \(قاعدة البيانات\)").sum()
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("🔮 جذور مستنطقة هندسياً", f"{geometric_count}")
            with col2:
                st.metric("📖 جذور ذات بصيرة حقيقية", f"{real_insight_count}")
            
            st.markdown("---")
            
            if not df_diag.empty:
                top_root = df_diag.iloc[0]['root']
                top_info = r_index.get(top_root, {})
                file_insight = str(top_info.get("insight", "")).strip()
                
                if is_placeholder_insight(file_insight):
                    geometric_insight = generate_geometric_insight_v3(top_root)
                    st.markdown(f"**🔮 الاستنطاق الهندسي لسيد المدار ({top_root}):**\n\n{geometric_insight}")
                    
                    if file_insight and len(file_insight) > 0:
                        st.caption(f"*ملاحظة: البصيرة الأصلية في القاعدة هي: \"{file_insight[:50]}...\" (نص افتراضي)*")
                else:
                    st.success(f"**📖 بصيرة سيد المدار (من القاعدة) للجذر ({top_root}):**\n\n{file_insight}")
        
        else:
            st.info("بانتظار استنطاق المدار لملء الموازين.")

    with tabs[5]:
        st.header("🧠 الوعي الفوقي والبيان الجمعي")
        
        if state['active']:
            collective_insight = generate_collective_insight(state['bodies'])
            st.markdown(collective_insight)
        else:
            st.info("بانتظار اكتمال المدار لتوليد الوعي الجمعي.")

else:
    for i in range(1, 6):
        with tabs[i]: st.info("المحراب في حالة انتظار... أطلق المفاعل لملء الموازين.")

# --- التذييل السيادي ---
st.sidebar.markdown(f"""
**المستخدم:** محمد  
**الحالة:** استواء سيادي - معايرة دقيقة لنطاق الأزل  
**الإصدار:** v27.8-Final (Precision Calibration)  
**CPU:** السجدة (5)  
---
**خِت فِت.**
""")
