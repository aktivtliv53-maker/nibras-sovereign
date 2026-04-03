# -*- coding: utf-8 -*-
# ==============================================================================
# نظام نِبْرَاس السيادي (Nibras Sovereign System) - الإصدار v28.0
# مَبنيٌّ على بروتوكول "الأمانة" و "الاستحقاق الجيني الحتمي"
# الإصدار: الربط المداري الحتمي - الجين انعكاس للمقام
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

# ==============================================================================
# [1] إعدادات الهوية السيادية المحصنة
# ==============================================================================
st.set_page_config(page_title="Nibras v28.0", page_icon="🛡️", layout="wide")

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
# [4] محرك الاستحقاق الجيني v28.0 - الربط المداري الحتمي
# ==============================================================================
def get_sovereign_gene(root_name, original_weight, orbit_id=0):
    """
    محرك الاستحقاق الجيني v28.0 - الربط المداري الحتمي
    يتم تحديد الجين بناءً على المدار (المقام) وليس فقط الوزن الرقمي
    
    تصنيف المدارات:
    - المدارات 1-2: طاقة المسير والبدايات (إبل - C)
    - المدارات 3-4: طاقة التثبيت والوفرة (بقر - B)
    - المدارات 5-6: طاقة السيادة والصعود (معز - G)
    - المدارات 7-8 وما فوق: طاقة السكينة والجمع (ضأن - S)
    """
    r = normalize_lexicon_root(root_name).strip()
    orbit = int(orbit_id)
    w = float(original_weight)
    
    # 1. تحديد الجين بناءً على تصنيف المدارات (هندسة المقام)
    if orbit in [1, 2]:
        gene_key = "C"      # إبل: طاقة المسير والبدايات
    elif orbit in [3, 4]:
        gene_key = "B"      # بقر: طاقة التثبيت والوفرة
    elif orbit in [5, 6]:
        gene_key = "G"      # معز: طاقة السيادة والصعود
    elif orbit >= 7:
        gene_key = "S"      # ضأن: طاقة السكينة والجمع
    else:
        gene_key = "N"      # إشراق: للجذور المستقلة

    # 2. حساب الطاقة (Energy) بناءً على الوزن الأصلي
    # الطاقة تعبر عن كثافة الجذر داخل مداره (نطاق 100-900)
    calibrated_energy = w * 100 if w < 10 else w
    
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
# [5] تحميل قاعدة البيانات مع الربط المداري
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
        
        # استخدام المحرك الجديد مع تمرير orbit_id
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
# [6] دوال البحث والعرض
# ==============================================================================
def match_root_logic(word, index_keys):
    w = normalize_sovereign(word)
    if not w or len(w) < 2:
        return None
    w_norm = normalize_lexicon_root(w)
    if w_norm in index_keys:
        return w_norm
    
    prefixes = ["ال", "و", "ف", "ب", "ك", "ل", "س", "بال", "وال", "فال"]
    for p in prefixes:
        if w.startswith(p) and len(w)-len(p) >= 3:
            candidate = normalize_lexicon_root(w[len(p):])
            if candidate in index_keys:
                return candidate
    return None

def display_insight_cards(bodies):
    """عرض الاستنطاق ككروت"""
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

# تحميل قاعدة البيانات
r_index, all_roots, orbit_counter = load_lexicon_db("data/nibras_lexicon.json")

# الشريط الجانبي
with st.sidebar:
    st.markdown(f"""
    <div style='text-align:center;'>
        <h2 style='color:#4fc3f7;'>🛡️ نبراس السيادي</h2>
        <p>الإصدار v28.0 - الربط المداري</p>
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
# [8] التبويبات السيادية
# ==============================================================================
tabs = st.tabs(["🔍 الاستنطاق المداري", "🌌 الرنين الجيني", "📈 اللوحة الوجودية", "📜 البيان الختامي", "⚖️ الميزان السيادي", "🧠 الوعي الفوقي"])

# --- التبويب 0: الاستنطاق ---
with tabs[0]:
    st.markdown("### 📍 هندسة المسارات المدارية - الربط المداري الحتمي")
    
    full_text = st.text_area(
        "أدخل النص للاستنطاق:", 
        height=150, 
        placeholder="مثال: أحد أبى أثر أجد أجل أخذ",
        key="input_area"
    )
    
    if st.button("🚀 تفعيل المفاعل السيادي v28.0", use_container_width=True):
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
                        # استخدام الطاقة من قاعدة البيانات
                        base_energy = data.get('raw_energy', data['weight'] * 100)
                        energy = base_energy + sig['total_energy'] * 0.15
                        gene_info = GENE_STYLE.get(data['gene'], GENE_STYLE['S'])
                        bodies.append({
                            "root": data['root_raw'],
                            "orbit": data['orbit'],
                            "orbit_id": data.get('orbit_id', 0),
                            "gene": data['gene'],
                            "gene_name": gene_info['name'],
                            "gene_icon": gene_info['icon'],
                            "energy": round(energy, 2),
                            "insight": data['insight'],
                            "color": gene_info['color'],
                            "x": random.uniform(-10, 10),
                            "y": random.uniform(-10, 10),
                            "vx": sig['vector_x'],
                            "vy": sig['vector_y']
                        })
                        word_pool.append(data['root_raw'])
            
            if bodies:
                st.session_state.orbit_bodies = bodies
                st.session_state.orbit_active = True
                
                # رسم بياني للحركة
                df = pd.DataFrame(bodies)
                fig = px.scatter(df, x="x", y="y", text="root", size="energy", color="gene",
                                 color_discrete_map={g: GENE_STYLE[g]['color'] for g in GENE_STYLE},
                                 range_x=[-35, 35], range_y=[-35, 35])
                fig.update_layout(height=500, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                  showlegend=False, xaxis_visible=False, yaxis_visible=False)
                st.plotly_chart(fig, use_container_width=True)
                
                # البيان الختامي الموسع
                st.markdown("### 📜 البيان الختامي الموسع")
                total_e = sum(b['energy'] for b in bodies)
                genes_count = Counter(b['gene'] for b in bodies)
                dom_gene = max(genes_count, key=genes_count.get)
                
                # عرض تفصيل المدارات
                orbits_detail = Counter(f"المدار {b['orbit_id']}" for b in bodies if b.get('orbit_id'))
                
                st.markdown(f"""
                <div class="story-box">
                    ✅ تم استنطاق <b>{len(bodies)}</b> جذراً.<br>
                    🐪 الهيمنة الجينية: <b>{GENE_STYLE[dom_gene]['icon']} {GENE_STYLE[dom_gene]['name']}</b><br>
                    ⚡ مجموع الطاقة: <b>{total_e:.1f}</b><br>
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
        
        # إضافة رسم بياني للمدارات
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
            <b>بيان الاستواء الوجودي v28.0:</b><br>
            تم استنطاق <b>{len(bodies)}</b> جذراً.<br>
            الهيمنة الجينية: <b>{GENE_STYLE[dom_gene]['icon']} {GENE_STYLE[dom_gene]['name']}</b><br>
            مجموع الطاقة: <b>{total_e:.1f}</b>
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
        
        # تحليل المدارات
        orbits_analysis = Counter(b.get('orbit_id', 0) for b in bodies)
        
        st.markdown(f"""
        <div class="story-box">
            <h3 style='color:#FFD700;'>🌌 بيان الوعي الجمعي</h3>
            <b>عدد الجذور:</b> {len(bodies)}<br>
            <b>مجموع الطاقة:</b> {total_e:.1f}<br>
            <b>الهيمنة الجينية:</b> {GENE_STYLE[dom_gene]['icon']} {GENE_STYLE[dom_gene]['name']}<br>
            <b>توزيع المدارات:</b> {', '.join([f'المدار {k}({v})' for k, v in sorted(orbits_analysis.items()) if k > 0])}
        </div>
        """, unsafe_allow_html=True)
        display_insight_cards(bodies)
    else:
        st.info("⚙️ انتظر تفعيل المفاعل.")
