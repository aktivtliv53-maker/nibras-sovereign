# -*- coding: utf-8 -*-
# ==============================================================================
# نظام نِبْرَاس السيادي (Nibras Sovereign System) - الإصدار v29.5 الشامل
# مَبنيٌّ على بروتوكول "الأمانة" و "الاستحقاق الجيني الحتمي"
# دمج: الذكاء الصرفي، الرنين السياقي، الوعي الزمني، والطاقة الديناميكية
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
# [1] إعدادات الهوية والجمالية السيادية
# ==============================================================================
st.set_page_config(page_title="Nibras v29.5 Sovereign", page_icon="🛡️", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&display=swap');
    [data-testid="stAppViewContainer"] { background: #050505; color: #e0e0e0; direction: rtl; font-family: 'Amiri', serif; }
    .stTabs [aria-selected="true"] { color: #FFD700 !important; border-bottom: 2px solid #FFD700 !important; }
    
    .insight-card {
        background: linear-gradient(135deg, #0d0d14 0%, #161625 100%);
        padding: 20px; border-radius: 15px; border-right: 8px solid #FFD700;
        margin-bottom: 15px; line-height: 1.6; font-size: 1.05em;
        box-shadow: 0 5px 15px rgba(0,0,0,0.5);
    }
    .energy-badge { background: #1a3a1a; color: #00ffcc; padding: 2px 8px; border-radius: 5px; font-family: monospace; }
    .story-box {
        background: linear-gradient(135deg, rgba(10,21,10,0.85) 0%, rgba(1,1,3,0.95) 100%);
        padding: 25px; border-radius: 20px; border-right: 12px solid #4CAF50;
        line-height: 1.8; font-size: 1.1em; margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# [2] مصفوفة الجينات والرموز
# ==============================================================================
GENE_STYLE = {
    'C': {'name': 'الإبل', 'color': '#4fc3f7', 'icon': '🐪', 'meaning': 'طاقة المسير والتمكين'},
    'B': {'name': 'البقر', 'color': '#FFD700', 'icon': '🐄', 'meaning': 'طاقة التثبيت والوفرة'},
    'S': {'name': 'الضأن', 'color': '#4CAF50', 'icon': '🐑', 'meaning': 'طاقة السكينة والرحمة'},
    'G': {'name': 'المعز', 'color': '#ff5252', 'icon': '🐐', 'meaning': 'طاقة السيادة والصعود'},
    'N': {'name': 'إشراق', 'color': '#00ffcc', 'icon': '✨', 'meaning': 'الانبثاق الصافي'}
}

# ==============================================================================
# [3] دوال التطهير والذكاء الصرفي
# ==============================================================================
ARABIC_DIACRITICS_PATTERN = re.compile(r'[\u0617-\u061A\u064B-\u0652\u0670\u06D6-\u06ED]')
COMMON_PREFIXES = ["وال", "بال", "كال", "فال", "لل", "ال", "و", "ف", "ب", "ك", "ل", "س"]
COMMON_SUFFIXES = ["يات", "ات", "ون", "ين", "ان", "وا", "نا", "ها", "هم", "هن", "كم", "ني", "ة", "ه", "ي"]

def normalize_sovereign(text: str):
    if not text: return ""
    text = ARABIC_DIACRITICS_PATTERN.sub('', text)
    text = text.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا").replace("ى", "ي").replace("ة", "ه")
    return re.sub(r'[^\u0621-\u063A\u0641-\u064A\s]', ' ', text).strip()

def normalize_lexicon_root(root_name: str):
    if not root_name: return ""
    return root_name.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا").replace("ة", "ه").replace("ى", "ي").strip()

def strip_affixes_ar(word: str):
    w = normalize_sovereign(word)
    for p in sorted(COMMON_PREFIXES, key=len, reverse=True):
        if w.startswith(p) and len(w) - len(p) >= 3: w = w[len(p):]; break
    for s in sorted(COMMON_SUFFIXES, key=len, reverse=True):
        if w.endswith(s) and len(w) - len(s) >= 3: w = w[:-len(s)]; break
    return w

def infer_pattern(word: str):
    w = normalize_sovereign(word)
    if w.startswith("است"): return "استفعال", 8
    if w.startswith("افت"): return "افتعال", 5
    if len(w) == 3: return "فعل ثلاثي", 1
    return "مزيد/مركب", 3

# ==============================================================================
# [4] محرك الاستحقاق والطاقة v29.5
# ==============================================================================
def get_sovereign_gene(orbit_id):
    oid = int(orbit_id)
    if oid in [1, 2]: return "C"
    if oid in [3, 4]: return "B"
    if oid in [5, 6]: return "G"
    if oid >= 7: return "S"
    return "N"

def signature_from_root(root):
    h = int(hashlib.md5(root.encode()).hexdigest(), 16)
    return {
        'total_energy': len(root) * 285.0 + (h % 150),
        'vx': (h % 30 - 15) / 120.0,
        'vy': ((h >> 4) % 30 - 15) / 120.0
    }

def compute_dynamic_energy(base_w, root, count, mode, pattern_hint):
    sig = signature_from_root(root)
    boost = 1.0 + math.log1p(max(0, count - 1)) * 0.35
    mode_factor = {"direct": 1.0, "stripped": 0.9, "segment": 0.8}.get(mode, 0.7)
    energy = (base_w * 100 * boost * mode_factor) + sig['total_energy'] * 0.12
    return round(energy, 2)

# ==============================================================================
# [5] تحميل وتحليل البيانات
# ==============================================================================
@st.cache_data(ttl=3600)
def load_lexicon_db(path):
    if not os.path.exists(path): return {}, [], Counter()
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    r_index = {}
    all_roots = []
    orbit_counter = Counter()
    for item in data:
        raw_root = item.get("root", "")
        if not raw_root: continue
        norm = normalize_lexicon_root(raw_root)
        oid = item.get("orbit_id", 0)
        gene = get_sovereign_gene(oid)
        r_index[norm] = {
            "root_raw": raw_root, "root": norm, "orbit_id": oid,
            "weight": float(item.get("weight", 1.0)), "gene": gene,
            "insight": item.get("insight_radar", item.get("insight", ""))
        }
        all_roots.append(r_index[norm])
        orbit_counter[f"المدار {oid}"] += 1
    return r_index, all_roots, orbit_counter

def match_root_logic(word, index_keys):
    w = normalize_sovereign(word)
    if not w: return None, "none", "none", 0
    # 1. مباشر
    norm = normalize_lexicon_root(w)
    if norm in index_keys: return norm, "direct", infer_pattern(w)[0], infer_pattern(w)[1]
    # 2. نزع لواصق
    stripped = strip_affixes_ar(w)
    if stripped in index_keys: return stripped, "stripped", infer_pattern(w)[0], infer_pattern(w)[1]
    return None, "unresolved", "none", 0

# ==============================================================================
# [6] طبقات الرنين والزمن
# ==============================================================================
def build_resonance(bodies):
    edges = []
    for a, b in combinations(range(len(bodies)), 2):
        ra, rb = bodies[a], bodies[b]
        dist = max(1, abs(ra['pos'] - rb['pos']))
        strength = (1.0 / dist) * (1.2 if ra['gene'] == rb['gene'] else 1.0)
        if strength > 0.2:
            edges.append({"source": ra['root'], "target": rb['root'], "strength": round(strength, 3)})
    return sorted(edges, key=lambda x: x['strength'], reverse=True)

def build_temporal(bodies):
    if not bodies: return pd.DataFrame()
    df = pd.DataFrame(bodies)
    df['step'] = range(1, len(df) + 1)
    df['cumulative'] = df['energy'].cumsum()
    return df

# ==============================================================================
# [7] واجهة المستخدم والتبويبات
# ==============================================================================
r_index, all_roots, orbit_counter = load_lexicon_db("data/nibras_lexicon.json")

if 'orbit_bodies' not in st.session_state:
    st.session_state.update({'orbit_bodies': [], 'orbit_active': False, 'res_edges': [], 'temp_df': pd.DataFrame()})

with st.sidebar:
    st.markdown("<h2 style='color:#4fc3f7; text-align:center;'>🛡️ نبراس v29.5</h2>", unsafe_allow_html=True)
    st.write(f"📚 الجذور: {len(r_index)}")
    st.write("خِت فِت.")

tabs = st.tabs(["🔍 المفاعل المداري", "📈 اللوحة الوجودية", "🕸️ الرنين السياقي", "⏳ الوعي الزمني", "⚖️ الميزان السيادي"])

# --- التبويب 0: المفاعل ---
with tabs[0]:
    input_text = st.text_area("أدخل النص للاستنطاق السيادي:", height=150)
    if st.button("🚀 تفعيل المفاعل v29.5", use_container_width=True):
        words = normalize_sovereign(input_text).split()
        bodies, resolved_roots = [], []
        
        # المرحلة 1: الحل
        for pos, w in enumerate(words):
            rk, mode, pat, p_oid = match_root_logic(w, r_index.keys())
            if rk: 
                resolved_roots.append(rk)
                data = r_index[rk]
                bodies.append({
                    "root": data['root_raw'], "pos": pos, "mode": mode, "pattern": pat,
                    "gene": data['gene'], "orbit_id": data['orbit_id'], "source": w,
                    "base_w": data['weight'], "insight": data['insight']
                })
        
        # المرحلة 2: تفعيل الطاقة
        counts = Counter(resolved_roots)
        for b in bodies:
            b['energy'] = compute_dynamic_energy(b['base_w'], b['root'], counts[b['root']], b['mode'], 0)
            gi = GENE_STYLE.get(b['gene'], GENE_STYLE['N'])
            b.update({"color": gi['color'], "icon": gi['icon'], "g_name": gi['name']})
            sig = signature_from_root(b['root'])
            b.update({"x": random.uniform(-20, 20), "y": random.uniform(-20, 20)})

        if bodies:
            st.session_state.update({
                'orbit_bodies': bodies, 'orbit_active': True,
                'res_edges': build_resonance(bodies), 'temp_df': build_temporal(bodies)
            })
            
            # رسم الخريطة
            fig = px.scatter(pd.DataFrame(bodies), x="x", y="y", text="root", size="energy", color="gene",
                             color_discrete_map={k: v['color'] for k, v in GENE_STYLE.items()}, range_x=[-40,40], range_y=[-40,40])
            fig.update_layout(height=500, showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
            
            # كروت الاستنطاق
            for b in bodies:
                st.markdown(f"""
                <div class="insight-card" style="border-right-color: {b['color']}">
                    <b style="color:{b['color']}">📌 {b['root']}</b> (من: {b['source']}) | 🧬 {b['icon']} {b['g_name']}<br>
                    🔄 المدار: {b['orbit_id']} | 🧪 الوزن: {b['pattern']} | ⚡ الطاقة: <span class="energy-badge">{b['energy']}</span>
                    <p style="margin-top:10px;">🔮 {b['insight']}</p>
                </div>
                """, unsafe_allow_html=True)

# --- التبويب 2: الرنين السياقي ---
with tabs[2]:
    if st.session_state.orbit_active:
        st.markdown("### 🕸️ شبكة الرنين بين الجذور")
        if st.session_state.res_edges:
            st.table(pd.DataFrame(st.session_state.res_edges).head(10))
        else: st.info("لا يوجد رنين كافٍ.")

# --- التبويب 3: الوعي الزمني ---
with tabs[3]:
    if st.session_state.orbit_active and not st.session_state.temp_df.empty:
        st.plotly_chart(px.line(st.session_state.temp_df, x="step", y="energy", markers=True, title="منحنى الطاقة الزمني"))
        st.plotly_chart(px.area(st.session_state.temp_df, x="step", y="cumulative", title="تراكم الرنين السيادي"))

# التبويبات الأخرى (اللوحة والميزان) يمكن عرض بيانات session_state.orbit_bodies فيها ببساطة.
