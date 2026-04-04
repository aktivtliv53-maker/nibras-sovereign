# -*- coding: utf-8 -*-
# ==============================================================================
# Nibras Sovereign System - v30.4 Final Stable Edition (سدرة المنتهى)
# ==============================================================================

import streamlit as st
import re
import hashlib
import math
import json
import os
import pandas as pd
import plotly.graph_objects as go
from collections import Counter

# ==============================================================================
# [1] الميثاق الدستوري (GENE STYLE)
# ==============================================================================
GENE_STYLE = {
    "N": {"color": "#FFFFFF", "icon": "🌟", "name": "إشراق مُستحق"},
    "S": {"color": "#FFD700", "icon": "👑", "name": "سيادي علوي"},
    "G": {"color": "#00E676", "icon": "🌱", "name": "نمو أرضي"},
    "B": {"color": "#2979FF", "icon": "💧", "name": "بناء وسيط"},
    "C": {"color": "#CFD8DC", "icon": "🧱", "name": "تأسيس قاعدي"}
}

# ==============================================================================
# [2] النواة الحتمية (Deterministic Core)
# ==============================================================================
def signature_from_root(root_norm):
    if not root_norm:
        return {'x': 0.0, 'y': 0.0, 'n_factor': 0, 'eb': 0.0}
    h = int(hashlib.md5(root_norm.encode('utf-8')).hexdigest(), 16)
    return {
        'x': round(((h % 360) - 180) / 10.0, 3),
        'y': round((((h >> 8) % 360) - 180) / 10.0, 3),
        'n_factor': (h >> 16) % 100,
        'eb': round((((h >> 24) % 81) - 40) / 10.0, 3)
    }

def compute_dynamic_energy(base_w, count, mode, morph_rank, orbit_id, sig):
    base_e = float(base_w) * 100 if float(base_w) < 10 else float(base_w)
    rep_boost = 1.0 + math.log1p(max(0, count - 1)) * 0.35
    mode_f = 1.0 if mode == "direct" else 0.92
    morph_f = 1.0 + (max(2, morph_rank) - 2) * 0.05
    orbit_f = 1.0 + max(0, int(orbit_id or 0) - 4) * 0.03
    return round((base_e * rep_boost * mode_f * morph_f * orbit_f) + sig['eb'], 2)

def resolve_sovereign_gene(orbit_id, morph_rank, sig, energy):
    orb = int(orbit_id or 0)
    base = "S" if orb >= 7 else "G" if orb >= 5 else "B" if orb >= 3 else "C"
    if sig['n_factor'] >= 92 and (orb >= 5 or morph_rank >= 6 or energy >= 85):
        return "N"
    return base

def compute_ascent_vector(bodies):
    if not bodies: return 0.0
    weights = {"N": 2.5, "S": 1.8, "G": 1.0, "B": 0.2, "C": -0.5}
    total = sum((weights[b['gene']] * (b['energy'] / 100)) for b in bodies)
    return round(total / len(bodies), 3)

# ==============================================================================
# [3] التطهير السيادي + محرك الاستخراج
# ==============================================================================
def normalize_sovereign(text):
    if not text: return ""
    text = str(text).strip()
    text = re.sub(r'[\u0617-\u061A\u064B-\u0652]', '', text)
    replacements = {'أ': 'ا', 'إ': 'ا', 'آ': 'ا', 'ى': 'ي', 'ئ': 'ي', 'ؤ': 'و', 'ة': 'ه'}
    for k, v in replacements.items(): text = text.replace(k, v)
    return re.sub(r'[^\w\s\u0600-\u06FF]', ' ', text).strip()

def match_root_from_word(word, r_index):
    w = normalize_sovereign(word)
    if not w: return None, 0
    if w in r_index: return w, 10
    prefixes = ['ال', 'و', 'ف', 'ب', 'ل']
    for p in prefixes:
        if w.startswith(p) and len(w) > len(p) + 2:
            sub = w[len(p):]
            if sub in r_index: return sub, 7
    suffixes = ['ون', 'ين', 'ات', 'ها', 'هم', 'كم', 'نا']
    for s in suffixes:
        if w.endswith(s) and len(w) > len(s) + 2:
            sub = w[:-len(s)]
            if sub in r_index: return sub, 7
    return None, 0

# ==============================================================================
# [4] محمل البيانات السيادي
# ==============================================================================
def load_sovereign_lexicon(path):
    if not os.path.exists(path): return {}
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    r_index = {}
    for item in data:
        root_raw = item.get("root", "")
        if not root_raw: continue
        norm = normalize_sovereign(root_raw)
        r_index[norm] = {
            "root_raw": root_raw,
            "orbit_id": item.get("orbit_id", 0),
            "weight": item.get("weight", 50.0),
            "insight": item.get("insight_radar", item.get("insight", "")),
            "sig": signature_from_root(norm)
        }
    return r_index

# ==============================================================================
# [5] المحرك الموحد
# ==============================================================================
def analyze_text_sovereign(text, r_index):
    clean = normalize_sovereign(text)
    words = clean.split()
    meta = []
    for pos, w in enumerate(words):
        rk, m_rank = match_root_from_word(w, r_index)
        if rk:
            meta.append({"rk": rk, "pos": pos, "m_rank": m_rank})
    if not meta:
        return {"bodies": [], "unique_roots": [], "ascent": 0.0}
    counts = Counter([m['rk'] for m in meta])
    bodies = []
    for m in meta:
        data = r_index[m['rk']]
        energy = compute_dynamic_energy(data['weight'], counts[m['rk']], "direct", m['m_rank'], data['orbit_id'], data['sig'])
        gene = resolve_sovereign_gene(data['orbit_id'], m['m_rank'], data['sig'], energy)
        bodies.append({
            "root_norm": m['rk'],
            "root_raw": data['root_raw'],
            "energy": energy,
            "gene": gene,
            "sig": data['sig'],
            "style": GENE_STYLE[gene],
            "orbit_id": data['orbit_id'],
            "insight": data['insight']
        })
    return {
        "bodies": bodies,
        "unique_roots": list(counts.keys()),
        "ascent": compute_ascent_vector(bodies)
    }

# ==============================================================================
# [6] الواجهة (الرادار + الكروت)
# ==============================================================================
def render_insight_radar(bodies):
    if not bodies: return
    df = pd.DataFrame([{
        'r': b['root_norm'], 'x': b['sig']['x'], 'y': b['sig']['y'],
        'e': b['energy'], 'c': b['style']['color']
    } for b in bodies])
    fig = go.Figure(go.Scatter(
        x=df['x'], y=df['y'], mode='markers+text', text=df['r'],
        textposition="top center",
        marker=dict(size=df['e']/3, color=df['c'], line=dict(width=1, color='white'))
    ))
    fig.update_layout(template="plotly_dark", height=500)
    st.plotly_chart(fig, use_container_width=True)

def render_sovereign_cards(bodies):
    for b in bodies:
        st.markdown(f"""
        <div style='border-right:4px solid {b["style"]["color"]}; padding:15px; margin-bottom:12px; background:#0d0d14; border-radius:0 10px 10px 0;'>
            <h4 style='color:{b["style"]["color"]}; margin:0;'>{b["style"]["icon"]} {b["root_norm"]}</h4>
            <small style='color:#888;'>طاقة: {b["energy"]} | جين: {b["gene"]} | مدار: {b["orbit_id"]}</small>
            <p style='color:#bbb; margin-top:8px; font-size:0.9em;'>{b["insight"]}</p>
        </div>
        """, unsafe_allow_html=True)

# ==============================================================================
# [7] التطبيق
# ==============================================================================
st.set_page_config(page_title="Nibras v30.4", page_icon="🛡️", layout="wide")

r_index = load_sovereign_lexicon("data/nibras_lexicon.json")

st.sidebar.markdown("<h1 style='color:#FFD700;'>🛡️ نِبْرَاس</h1>", unsafe_allow_html=True)
st.sidebar.info(f"📊 الجذور المحملة: {len(r_index)}")

tabs = st.tabs(["🔍 الاستنطاق", "⚖️ المقارن", "🌌 الجذر"])

with tabs[0]:
    st.markdown("### 📍 الاستنطاق")
    txt = st.text_area("أدخل النص:", height=150)
    if st.button("🚀 تحليل"):
        res = analyze_text_sovereign(txt, r_index)
        if res['bodies']:
            st.success(f"🚀 مؤشر الصعود: {res['ascent']}")
            render_insight_radar(res['bodies'])
            render_sovereign_cards(res['bodies'])
        else:
            st.error("لا توجد جذور مطابقة.")

with tabs[1]:
    st.markdown("### ⚖️ المقارنة")
    t1 = st.text_area("النص الأول")
    t2 = st.text_area("النص الثاني")
    if st.button("مقارنة"):
        c1 = analyze_text_sovereign(t1, r_index)
        c2 = analyze_text_sovereign(t2, r_index)
        st.metric("فرق الصعود", round(c1['ascent'] - c2['ascent'], 3))

with tabs[2]:
    st.markdown("### 🌌 استكشاف الجذر")
    root = st.selectbox("اختر جذراً:", sorted(r_index.keys()))
    if root:
        d = r_index[root]
        st.write(d)

st.markdown("<p style='text-align:center; color:#555;'>خِت فِت.</p>", unsafe_allow_html=True)
