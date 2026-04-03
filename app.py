# -*- coding: utf-8 -*-
# ==============================================================================
# نظام نِبْرَاس السيادي (Nibras Sovereign System) - الإصدار v29.1
# مَبنيٌّ على بروتوكول "الأمانة" و "الاستحقاق الجيني الحتمي"
# الإصدار: الواجهة النقية - استنطاق كامل بلا قَصّ ولا تلوث
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
# [2] قاموس هندسة الحروف
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
# [5] تحميل قاعدة البيانات
# ==============================================================================

@st.cache_data(ttl=3600)
def load_lexicon_db(path):
    """تحميل الليكسيكون بالكامل"""
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
# [6] دالة عرض الجدول المخصص - بدون قص
# ==============================================================================

def display_roots_table(bodies_data):
    """عرض الجذور في جدول مخصص بدون قص النصوص"""
    if not bodies_data:
        st.info("لا توجد بيانات للعرض.")
        return
    
    for idx, body in enumerate(bodies_data):
        insight_text = body.get('insight', '')
        if is_placeholder(insight_text) or not insight_text:
            insight_text = generate_geometric_insight(body.get('root', ''))
        
        st.markdown(f"""
        <div style='border:1px solid #333; border-radius:10px; padding:15px; margin-bottom:15px; background:#0a0a0a;'>
            <table style='width:100%; border-collapse:collapse; direction:rtl;'>
                <tr>
                    <td style='padding:8px; width:100px; color:#888;'>الجذر</td>
                    <td style='padding:8px; color:#4fc3f7; font-weight:bold;'>{body.get('root', '')}</td>
                </tr>
                <tr>
                    <td style='padding:8px; width:100px; color:#888;'>الجين</td>
                    <td style='padding:8px;'><span style='color:{GENE_STYLE.get(body.get('gene', 'S'), GENE_STYLE['S'])["color"]};'>{GENE_STYLE.get(body.get('gene', 'S'), GENE_STYLE['S'])["icon"]} {GENE_STYLE.get(body.get('gene', 'S'), GENE_STYLE['S'])["name"]}</span></td>
                </tr>
                <tr>
                    <td style='padding:8px; width:100px; color:#888;'>الطاقة</td>
                    <td style='padding:8px;'>{body.get('energy', 0):.2f}</td>
                </tr>
                <tr>
                    <td style='padding:8px; width:100px; color:#888; vertical-align:top;'>الاستنطاق</td>
                    <td style='padding:8px; line-height:1.6;'>{ensure_dot(insight_text)}</td>
                </tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

# ==============================================================================
# [7] تهيئة التطبيق
# ==============================================================================

st.set_page_config(page_title="نبراس السيادي v29.1", page_icon="🛡️", layout="wide")

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
        padding: 40px;
        border-radius: 25px;
        border-right: 15px solid #4CAF50;
        line-height: 2;
        font-size: 1.3em;
        margin-bottom: 30px;
    }
    .ultra-card {
        background: #0d0d14;
        padding: 25px;
        border-radius: 20px;
        border-top: 8px solid #4fc3f7;
        text-align: center;
        transition: all 0.3s ease;
        margin-bottom: 20px;
    }
    .stat-val {
        font-size: 2.5em;
        font-weight: bold;
        color: #00ffcc;
    }
    /* إخفاء أي عناصر عائمة غير مرغوب فيها */
    .st-emotion-cache-1v0mbdj, .st-emotion-cache-1wivap2 {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

# تحميل الليكسيكون
ROOTS_PATH = "data/nibras_lexicon.json"
r_index, all_roots = load_lexicon_db(ROOTS_PATH)

# حالة الجلسة
if 'active_bodies' not in st.session_state:
    st.session_state.active_bodies = []
    st.session_state.active_pool = []
    st.session_state.is_active = False
    st.session_state.full_analysis = None

# الشريط الجانبي
with st.sidebar:
    st.markdown(f"""
    **نبراس السيادي v29.1**  
    **المستخدم:** محمد  
    ---
    **📊 قاعدة البيانات:**
    - إجمالي الجذور: {len(r_index)}
    - 🐪 إبل: {len([r for r in r_index.values() if r['gene'] == 'C'])}
    - 🐄 بقر: {len([r for r in r_index.values() if r['gene'] == 'B'])}
    - 🐑 ضأن: {len([r for r in r_index.values() if r['gene'] == 'S'])}
    - 🐐 معز: {len([r for r in r_index.values() if r['gene'] == 'G'])}
    ---
    **خِت فِت.**
    """)

# ==============================================================================
# [8] واجهة التبويبات
# ==============================================================================

tabs = st.tabs(["🔍 الاستنطاق المداري", "🌌 الرنين الجيني", "📈 اللوحة الوجودية", "📜 البيان الختامي", "⚖️ الميزان السيادي", "🧠 الوعي الفوقي"])

# ==================== التبويب 0: الاستنطاق ====================
with tabs[0]:
    st.markdown("### 📍 الاستنطاق المداري - تحليل النصوص")
    
    input_text = st.text_area(
        "أدخل النص للاستنطاق:",
        height=150,
        placeholder="مثال: أحد أبى أثر أجد أجل أخذ أذن أرب أرض أزل أسر أصل أفق",
        key="input_area"
    )
    
    if st.button("🚀 تفعيل المفاعل", use_container_width=True):
        if input_text.strip():
            clean = normalize_input_text(input_text)
            words = clean.split()
            
            bodies = []
            pool = []
            
            for word in words:
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
                            "x": random.uniform(-10, 10),
                            "y": random.uniform(-10, 10),
                            "vx": sig['vector_x'],
                            "vy": sig['vector_y'],
                            "color": GENE_STYLE[data['gene']]['color']
                        })
                        pool.append(data['root_raw'])
            
            if bodies:
                st.session_state.active_bodies = bodies
                st.session_state.active_pool = list(set(pool))
                st.session_state.is_active = True
                
                # عرض الرسم البياني
                fig = px.scatter(pd.DataFrame(bodies), x="x", y="y", text="root", size="energy", color="gene",
                                 color_discrete_map={g: GENE_STYLE[g]['color'] for g in GENE_STYLE},
                                 range_x=[-35, 35], range_y=[-35, 35])
                fig.update_layout(height=500, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                  showlegend=False, xaxis_visible=False, yaxis_visible=False)
                st.plotly_chart(fig, use_container_width=True)
                
                # بيان الوعي الجمعي - يظهر مباشرة
                st.markdown("---")
                st.markdown("### 🌌 بيان الوعي الجمعي")
                
                total_energy = sum(b['energy'] for b in bodies)
                genes_count = Counter(b['gene'] for b in bodies)
                dominant_gene = max(genes_count, key=genes_count.get)
                gene_info = GENE_STYLE[dominant_gene]
                
                st.markdown(f"""
                <div class='story-box'>
                    <p><b>تم استنطاق {len(bodies)} جذراً.</b><br>
                    الهيمنة الجينية: <span style='color:{gene_info["color"]}'>{gene_info['icon']} {gene_info['name']}</span><br>
                    مجموع الطاقة: {total_energy:.1f}<br>
                    الجذور المستنطقة: {', '.join(pool[:10])}{'...' if len(pool) > 10 else ''}</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.success(f"✅ تم الاستنطاق بنجاح.")
            else:
                st.warning("⚠️ لم يتم العثور على جذور مطابقة في الليكسيكون")
        else:
            st.warning("⚠️ الرجاء إدخال نص")

# ==================== التبويب 1: الرنين الجيني ====================
with tabs[1]:
    st.markdown("### 🌌 مصفوفة الرنين الجيني")
    
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
    
    search_root = st.text_input("أدخل جذراً للبحث:", value="أحد", key="search_root")
    
    if search_root:
        normalized = normalize_root(search_root)
        found = r_index.get(normalized)
        
        if found:
            gene_info = GENE_STYLE[found['gene']]
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                <div style='border:1px solid #444; padding:15px; border-radius:15px; background:#111; margin-bottom:15px;'>
                    <p style='color:#888;'>الجذر الأصلي</p>
                    <h3>{found['root_raw']}</h3>
                </div>
                <div style='border:1px solid {gene_info["color"]}; padding:15px; border-radius:15px; background:#111;'>
                    <p style='color:#888;'>الجين الحتمي</p>
                    <h3 style='color:{gene_info["color"]};'>{gene_info['icon']} {gene_info['name']}</h3>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div style='border:1px solid #444; padding:15px; border-radius:15px; background:#111; margin-bottom:15px;'>
                    <p style='color:#888;'>المدار</p>
                    <h3>{found['orbit']}</h3>
                </div>
                <div style='border:1px solid #444; padding:15px; border-radius:15px; background:#111;'>
                    <p style='color:#888;'>نوع الطاقة</p>
                    <h3>{found['energy_type']}</h3>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div style='border:1px solid #4CAF50; padding:15px; border-radius:15px; background:#0a1a0a; margin-top:15px;'>
                <p style='color:#4CAF50;'>🔮 بصيرة الجذر</p>
                <p>{ensure_dot(found['insight'])}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.error(f"❌ الجذر '{search_root}' غير موجود")

# ==================== التبويب 2: اللوحة الوجودية ====================
with tabs[2]:
    st.markdown("### 📈 التحليل الكمي")
    if st.session_state.is_active and st.session_state.active_bodies:
        df = pd.DataFrame(st.session_state.active_bodies)
        col1, col2 = st.columns(2)
        col1.plotly_chart(px.pie(df, names='gene', color='gene', color_discrete_map={g: GENE_STYLE[g]['color'] for g in GENE_STYLE}, hole=0.5, title="توزيع الجينات"))
        col2.plotly_chart(px.bar(df.groupby('gene').size().reset_index(name='count'), x='gene', y='count', color='gene', color_discrete_map={g: GENE_STYLE[g]['color'] for g in GENE_STYLE}, title="التعداد"))
        st.plotly_chart(px.scatter(df, x='root', y='energy', color='gene', size='energy', color_discrete_map={g: GENE_STYLE[g]['color'] for g in GENE_STYLE}, title="خارطة الطاقة"))
    else:
        st.info("⚙️ انتظر تفعيل المفاعل في التبويب الأول")

# ==================== التبويب 3: البيان الختامي ====================
with tabs[3]:
    if st.session_state.is_active and st.session_state.active_bodies:
        df = pd.DataFrame(st.session_state.active_bodies)
        dominant = df['gene'].mode()[0] if not df.empty else 'S'
        st.markdown(f"""
        <div class='story-box'>
            <b>بيان الاستواء الوجودي v29.1:</b><br>
            تم استنطاق <b>{len(st.session_state.active_pool)}</b> جذراً.<br>
            الهيمنة الجينية: <b style='color:{GENE_STYLE[dominant]["color"]}'>{GENE_STYLE[dominant]['icon']} {GENE_STYLE[dominant]['name']}</b><br>
            مجموع الطاقة: <b>{df['energy'].sum():.1f}</b>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("⚙️ انتظر تفعيل المفاعل")

# ==================== التبويب 4: الميزان السيادي ====================
with tabs[4]:
    st.markdown("### ⚖️ ميزان النزاهة الجذرية - استنطاق كامل")
    
    if st.session_state.is_active and st.session_state.active_bodies:
        display_roots_table(st.session_state.active_bodies)
    else:
        st.info("⚙️ انتظر تفعيل المفاعل")

# ==================== التبويب 5: الوعي الفوقي ====================
with tabs[5]:
    st.markdown("### 🧠 الوعي الفوقي")
    
    if st.session_state.is_active and st.session_state.active_bodies:
        total_energy = sum(b['energy'] for b in st.session_state.active_bodies)
        genes_count = Counter(b['gene'] for b in st.session_state.active_bodies)
        dominant_gene = max(genes_count, key=genes_count.get)
        gene_info = GENE_STYLE[dominant_gene]
        
        st.markdown(f"""
        <div class='story-box'>
            <h3 style='margin:0; color:#FFD700;'>🌌 بيان الوعي الجمعي</h3>
            <p><b>عدد الجذور المستنطقة:</b> {len(st.session_state.active_bodies)}<br>
            <b>مجموع الطاقة:</b> {total_energy:.1f}<br>
            <b>الهيمنة الجينية:</b> <span style='color:{gene_info["color"]}'>{gene_info['icon']} {gene_info['name']}</span><br>
            <b>الجذور:</b> {', '.join(st.session_state.active_pool)}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # عرض تفاصيل كل جذر
        st.markdown("#### 📖 تفاصيل الاستنطاق")
        display_roots_table(st.session_state.active_bodies)
    else:
        st.info("⚙️ انتظر تفعيل المفاعل في التبويب الأول")
