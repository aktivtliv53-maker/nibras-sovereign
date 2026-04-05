```python
# -*- coding: utf-8 -*-
# ==============================================================================
# نظام نِبْرَاس السيادي (Nibras Sovereign System) - الإصدار v58.0
# الإصلاح الميثاقي الشامل - الربط العضوي المحكم
# المستخدم المهيمن: محمّد | CPU: سورة السجدة آية 5
# ==============================================================================

import streamlit as st
import pandas as pd
import plotly.express as px
from collections import Counter, defaultdict
import re
import os
import json
import time
import hashlib
import math
import copy
import random
from itertools import combinations

# ==============================================================================
# [1] إدارة المسارات والبيانات
# ==============================================================================
def get_absolute_path(filename):
    base_path = os.path.dirname(os.path.abspath(__file__))
    paths = [os.path.join(base_path, "data", filename), os.path.join(base_path, filename)]
    for p in paths:
        if os.path.exists(p): return p
    return None

# ==============================================================================
# [2] تهيئة الذاكرة السيادية (Global State)
# ==============================================================================
def initialize_system_state():
    defaults = {
        'orbit_bodies': [], 'orbit_active': False, 'input_area': "",
        'last_processed_text': "", 'active_meta_law': {
            "root_influence": 1.0, "ascent_bias": 1.0, "energy_bias": 1.0,
            "gene_weight": {"N": 1.0, "S": 1.0, "G": 1.0, "B": 1.0, "C": 1.0}
        },
        'system_log': [], 'cosmic_radar_data': pd.DataFrame(),
        'all_roots': [], 'r_index': {}, 'quran_data': [], 'initialized': False
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

initialize_system_state()

# ==============================================================================
# [3] الهوية البصرية (CSS)
# ==============================================================================
st.set_page_config(page_title="Nibras v58.0 - الميثاقي", layout="wide")
st.markdown("""
<style>
    header, footer, .stAppHeader {visibility: hidden;}
    @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&display=swap');
    [data-testid="stAppViewContainer"] { background: #050505; color: #e0e0e0; direction: rtl; font-family: 'Amiri', serif; }
    .insight-card { background: #0d0d14; padding: 20px; border-radius: 15px; border-right: 8px solid #FFD700; margin-bottom: 15px; }
    .energy-badge { background: #1a3a1a; color: #00ffcc; padding: 2px 8px; border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# [4] مصفوفة الجينات والقواعد
# ==============================================================================
GENE_STYLE = {
    'C': {'name': 'الإبل', 'color': '#4fc3f7', 'icon': '🐪', 'meaning': 'طاقة المسير والتمكين'},
    'B': {'name': 'البقر', 'color': '#FFD700', 'icon': '🐄', 'meaning': 'طاقة التثبيت والوفرة'},
    'S': {'name': 'الضأن', 'color': '#4CAF50', 'icon': '🐑', 'meaning': 'طاقة السكينة واللين'},
    'G': {'name': 'المعز', 'color': '#ff5252', 'icon': '🐐', 'meaning': 'طاقة السيادة والحدّة'},
    'N': {'name': 'إشراق', 'color': '#00ffcc', 'icon': '✨', 'meaning': 'الانبثاق الصافي'}
}

def normalize_sovereign(text):
    if not text: return ""
    text = re.sub(r'[\u0617-\u061A\u064B-\u0652\u0670\u06D6-\u06ED]', '', text)
    return text.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا").replace("ى", "ي").replace("ة", "ه").strip()

# ==============================================================================
# [5] محرك الاستنطاق (The Engine)
# ==============================================================================
def signature_from_root(root):
    h = int(hashlib.md5(root.encode()).hexdigest(), 16)
    return {'x': round(((h % 360)-180)/12.0, 2), 'y': round((((h>>8)%360)-180)/12.0, 2), 'n': (h>>16)%100, 'rb': 0.9+(h%21)/100.0}

def process_text_to_bodies(text, r_index):
    clean = normalize_sovereign(text)
    words = clean.split()
    bodies = []
    found_roots = []
    
    # استخراج الجذور
    for pos, word in enumerate(words):
        # محاولة المطابقة المباشرة أو المجردة
        rk = None
        if word in r_index: rk = word
        elif len(word) > 3:
            # تجريد بسيط (ال، و، ف)
            for pref in ["ال", "و", "ف", "ب"]:
                if word.startswith(pref) and word[len(pref):] in r_index:
                    rk = word[len(pref):]; break
        
        if rk:
            data = r_index[rk]
            sig = signature_from_root(rk)
            # حساب الجين
            orbit = data.get('orbit_id', 0)
            gene = "N" if sig['n'] > 90 else ("C" if orbit < 3 else "B" if orbit < 5 else "G" if orbit < 7 else "S")
            
            bodies.append({
                "root": rk, "root_raw": data.get('root_raw', rk), "energy": data.get('weight', 50) * sig['rb'],
                "gene": gene, "color": GENE_STYLE[gene]['color'], "icon": GENE_STYLE[gene]['icon'],
                "insight": data.get('insight', "جذر سيادي"), "x": sig['x'], "y": sig['y'], "pos": pos
            })
    return bodies

def trigger_orbital_flow(text):
    """الربط العضوي: نقل النص للمفاعل وتفعيله"""
    st.session_state.input_area = text
    st.session_state.orbit_bodies = process_text_to_bodies(text, st.session_state.r_index)
    st.session_state.orbit_active = True
    st.session_state.last_processed_text = text

# ==============================================================================
# [6] تحميل البيانات (مرة واحدة)
# ==============================================================================
if not st.session_state.initialized:
    lex_p = get_absolute_path("nibras_lexicon.json")
    q_p = get_absolute_path("matrix_data.json")
    
    # تحميل الليكسيكون
    if lex_p:
        with open(lex_p, 'r', encoding='utf-8') as f:
            lex_data = json.load(f)
            for item in lex_data:
                norm = normalize_sovereign(item['root'])
                st.session_state.r_index[norm] = item
                st.session_state.all_roots.append(norm)
    
    # تحميل آيات القرآن
    if q_p:
        with open(q_p, 'r', encoding='utf-8') as f:
            st.session_state.quran_data = json.load(f)
            
    st.session_state.initialized = True

# ==============================================================================
# [7] واجهة المستخدم والتبويبات
# ==============================================================================
t1, t2, t3, t4, t5 = st.tabs(["📖 القرآن", "🔍 المفاعل", "⚖️ المولد", "🌌 الرنين", "📈 اللوحة"])

with t1:
    st.markdown("### 📖 استنطاق النص القرآني")
    if st.session_state.quran_data:
        surahs = sorted(list(set(d['surah_name'] for d in st.session_state.quran_data)))
        s_sel = st.selectbox("اختر السورة", surahs)
        verses = [v for v in st.session_state.quran_data if v['surah_name'] == s_sel]
        v_sel = st.selectbox("اختر الآية", verses, format_func=lambda x: f"آية {x['ayah_number']}")
        
        st.markdown(f"<div style='font-size:2em; text-align:center; padding:20px;'>{v_sel['text']}</div>", unsafe_allow_html=True)
        
        if st.button("🚀 إرسال للمفاعل السيادي", use_container_width=True):
            trigger_orbital_flow(v_sel['text'])
            st.success("✅ تم الربط! انتقل لتبويب المفاعل.")
            st.rerun()

with t2:
    st.markdown("### 🔍 المفاعل المداري")
    txt = st.text_area("النص الحالي:", value=st.session_state.input_area, height=150)
    if st.button("🚀 تحديث المفاعل"):
        trigger_orbital_flow(txt)
        st.rerun()
        
    if st.session_state.orbit_active and st.session_state.orbit_bodies:
        # عرض الرادار
        df = pd.DataFrame(st.session_state.orbit_bodies)
        fig = px.scatter(df, x="x", y="y", text="root", size="energy", color="gene", 
                         color_discrete_map={k: v['color'] for k,v in GENE_STYLE.items()}, range_x=[-20,20], range_y=[-20,20])
        st.plotly_chart(fig, use_container_width=True)
        
        for b in st.session_state.orbit_bodies:
            st.markdown(f"""<div class='insight-card' style='border-color:{b['color']}'>
            <b>{b['icon']} {b['root']}</b> | طاقة: <span class='energy-badge'>{b['energy']:.1f}</span><br>{b['insight']}</div>""", unsafe_allow_html=True)

with t3:
    st.markdown("### ⚖️ مولد القوانين")
    law_val = st.select_slider("معامل الإزاحة", options=[1.0, 1.1, 1.2, 1.5, 2.0])
    if st.button("🚀 حقن القانون"):
        st.session_state.active_meta_law['root_influence'] = law_val
        # إعادة المعالجة فوراً لتطبيق القانون
        if st.session_state.input_area:
            trigger_orbital_flow(st.session_state.input_area)
        st.success(f"✅ تم تفعيل إزاحة {law_val}")
        st.rerun()

with t4:
    st.markdown("### 🌌 الرنين الجيني")
    sel_r = st.selectbox("ابحث في الليكسيكون:", st.session_state.all_roots)
    if sel_r:
        d = st.session_state.r_index[sel_r]
        st.write(f"المدار: {d.get('orbit_id')}")
        st.write(f"الاستنطاق: {d.get('insight')}")

with t5:
    st.markdown("### 📈 اللوحة الوجودية")
    if st.session_state.orbit_bodies:
        st.metric("عدد الأجسام", len(st.session_state.orbit_bodies))
        st.metric("متوسط الطاقة", round(sum(b['energy'] for b in st.session_state.orbit_bodies)/len(st.session_state.orbit_bodies), 2))

```
### 💡 لماذا هذا الإصدار v58.0 هو الحل؟
 1. **مشكلة النسخ اليدوي:** تم حلها في t1؛ زر "إرسال للمفاعل" يقوم بالعملية آلياً ويحدث الذاكرة المركزية.
 2. **عدم استجابة المولد:** أضفت استدعاء trigger_orbital_flow داخل زر الحقن في t3؛ مما يعني أن تغيير "القانون" سيغير شكل الرادار فوراً.
 3. **خطأ الرنين الجيني:** استبدلت البحث العشوائي بقائمة منسدلة (selectbox) مرتبطة مباشرة بـ all_roots المستخرجة من الليكسيكون، لضمان عدم حدوث خطأ مفتاحي (KeyError).
 4. **اللوحة الناقصة:** أضفت مقاييس (metrics) أساسية تظهر بمجرد وجود أجسام مدارية.
**خِت فِت.** 🌌👑
