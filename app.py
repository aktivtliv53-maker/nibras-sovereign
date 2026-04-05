# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px
from collections import Counter, defaultdict
import re
import os
import json
import hashlib
import math
import copy

# --- [1] النظام الأساسي وإدارة الذاكرة ---
def initialize_engine():
    """تهيئة مخازن البيانات المركزية لمنع أخطاء AttributeError"""
    state_keys = {
        'active_text': "",
        'processed_bodies': [],
        'is_active': False,
        'lexicon_index': {},
        'quran_matrix': [],
        'meta_law': {"influence": 1.0, "ascent": 1.0, "energy": 1.0},
        'radar_data': pd.DataFrame()
    }
    for key, val in state_keys.items():
        if key not in st.session_state:
            st.session_state[key] = val

initialize_engine()

# --- [2] محركات المعالجة الفنية ---
def normalize_text(text):
    if not text: return ""
    text = re.sub(r'[\u0617-\u061A\u064B-\u0652\u0670\u06D6-\u06ED]', '', text)
    return text.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا").replace("ى", "ي").replace("ة", "ه").strip()

def get_root_signature(root):
    h = int(hashlib.md5(root.encode()).hexdigest(), 16)
    return {
        'x': round(((h % 360)-180)/12.0, 2),
        'y': round((((h>>8)%360)-180)/12.0, 2),
        'energy_mod': 0.9 + (h % 21) / 100.0
    }

def run_analysis_flow(text):
    """المحرك المركزي: يحول النص إلى بيانات مدارية ويحدث الذاكرة"""
    st.session_state.active_text = text
    clean = normalize_text(text)
    words = clean.split()
    bodies = []
    
    index = st.session_state.lexicon_index
    for pos, word in enumerate(words):
        root_key = None
        if word in index: root_key = word
        elif len(word) > 3: # تجريد بسيط للزوائد
            for p in ["ال", "و", "ف", "ب"]:
                if word.startswith(p) and word[len(p):] in index:
                    root_key = word[len(p):]; break
        
        if root_key:
            data = index[root_key]
            sig = get_root_signature(root_key)
            bodies.append({
                "root": root_key,
                "energy": data.get('weight', 50) * sig['energy_mod'] * st.session_state.meta_law['influence'],
                "insight": data.get('insight', ""),
                "x": sig['x'], "y": sig['y'], "pos": pos
            })
    
    st.session_state.processed_bodies = bodies
    st.session_state.is_active = True

# --- [3] واجهة المستخدم والتبويبات ---
t1, t2, t3, t4 = st.tabs(["المصدر القرآني", "مفاعل الاستنطاق", "محرك القوانين", "اللوحة التحليلية"])

with t1:
    st.subheader("قاعدة بيانات المصدر")
    if st.session_state.quran_matrix:
        # عرض واختيار الآية
        verses = st.session_state.quran_matrix
        v_sel = st.selectbox("اختر النص المستهدف", verses, format_func=lambda x: f"سورة {x.get('surah_name')} - آية {x.get('ayah_number')}")
        
        if v_sel:
            st.info(v_sel['text'])
            if st.button("تفعيل الربط المباشر مع المفاعل"):
                run_analysis_flow(v_sel['text'])
                st.success("تم نقل البيانات وتحديث المفاعل")
                st.rerun()

with t2:
    st.subheader("نتائج الاستنطاق المداري")
    input_text = st.text_area("النص قيد المعالجة:", value=st.session_state.active_text)
    if st.button("تحديث يدوي للمفاعل"):
        run_analysis_flow(input_text)
        st.rerun()
    
    if st.session_state.is_active and st.session_state.processed_bodies:
        df = pd.DataFrame(st.session_state.processed_bodies)
        fig = px.scatter(df, x="x", y="y", text="root", size="energy", range_x=[-25,25], range_y=[-25,25])
        st.plotly_chart(fig, use_container_width=True)
        
        for b in st.session_state.processed_bodies:
            with st.expander(f"الجذر: {b['root']}"):
                st.write(b['insight'])

with t3:
    st.subheader("إدارة القوانين الرياضية")
    influence = st.slider("معامل الإزاحة (Influence)", 0.5, 2.0, st.session_state.meta_law['influence'])
    if st.button("تطبيق القانون الجديد"):
        st.session_state.meta_law['influence'] = influence
        if st.session_state.active_text:
            run_analysis_flow(st.session_state.active_text)
        st.rerun()

with t4:
    st.subheader("البيانات الاحصائية")
    if st.session_state.processed_bodies:
        st.write(pd.DataFrame(st.session_state.processed_bodies))
    else:
        st.info("بانتظار تفعيل المفاعل")
