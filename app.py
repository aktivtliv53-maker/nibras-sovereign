# -*- coding: utf-8 -*-
# ==============================================================================
# نظام نِبْرَاس السيادي (Nibras Sovereign System) - الإصدار v30.3
# المسمى: The Final Stable Engine - المحرك المستقر النهائي
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
# [1] الميثاق الدستوري
# ==============================================================================
GENE_STYLE = {
    "N": {"color": "#FFFFFF", "icon": "🌟", "name": "إشراق مُستحق"},
    "S": {"color": "#FFD700", "icon": "👑", "name": "سيادي علوي"},
    "G": {"color": "#00E676", "icon": "🌱", "name": "نمو أرضي"},
    "B": {"color": "#2979FF", "icon": "💧", "name": "بناء وسيط"},
    "C": {"color": "#CFD8DC", "icon": "🧱", "name": "تأسيس قاعدي"}
}

# ==============================================================================
# [2] النواة الحتمية
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
    base_e = base_w * 100 if base_w < 10 else base_w
    rep_boost = 1.0 + math.log1p(max(0, count - 1)) * 0.35
    mode_f = 1.0 if mode == "direct" else 0.92
    morph_f = 1.0 + (max(2, morph_rank) - 2) * 0.05
    orbit_f = 1.0 + max(0, int(orbit_id or 0) - 4) * 0.03
    return round((base_e * rep_boost * mode_f * morph_f * orbit_f) + sig['eb'], 2)

def resolve_sovereign_gene(orbit_id, morph_rank, sig, energy):
    orb = int(orbit_id or 0)
    if orb >= 7:
        base = "S"
    elif orb >= 5:
        base = "G"
    elif orb >= 3:
        base = "B"
    else:
        base = "C"
    if sig['n_factor'] >= 92 and (orb >= 5 or morph_rank >= 6 or energy >= 85):
        return "N"
    return base

def compute_ascent_vector(bodies):
    if not bodies:
        return 0.0
    weights = {"N": 2.5, "S": 1.8, "G": 1.0, "B": 0.2, "C": -0.5}
    total = sum((weights.get(b['gene'], 0) * (b['energy'] / 100)) for b in bodies)
    return round(total / len(bodies), 3)

# ==============================================================================
# [3] الحواس والإمداد
# ==============================================================================
def normalize_sovereign(text):
    if not text:
        return ""
    text = str(text).strip()
    text = re.sub(r'[\u0617-\u061A\u064B-\u0652]', '', text)
    text = text.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا')
    text = text.replace('ى', 'ي').replace('ئ', 'ي').replace('ؤ', 'و')
    text = text.replace('ة', 'ه')
    return re.sub(r'[^\w\s\u0600-\u06FF]', ' ', text).strip()

def match_root_from_word(word, r_index):
    w = normalize_sovereign(word)
    if not w:
        return None
    if w in r_index:
        return w
    if w.startswith('ال') and len(w) > 4:
        w2 = w[2:]
        if w2 in r_index:
            return w2
    for prefix in ['و', 'ف', 'ب', 'ك', 'ل', 'س']:
        if w.startswith(prefix) and len(w) > len(prefix) + 2:
            w2 = w[len(prefix):]
            if w2 in r_index:
                return w2
    for suffix in ['ة', 'ه', 'ي', 'ا', 'ت', 'ن', 'و']:
        if w.endswith(suffix) and len(w) > 3:
            w2 = w[:-len(suffix)]
            if w2 in r_index:
                return w2
    return None

def load_sovereign_lexicon(file_path):
    if not os.path.exists(file_path):
        st.error(f"❌ ملف الليكسيكون غير موجود: {file_path}")
        return {}
    with open(file_path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            st.error(f"❌ خطأ في JSON: {e}")
            return {}
    if not isinstance(data, list):
        st.error("❌ ملف JSON يجب أن يكون مصفوفة")
        return {}
    r_index = {}
    for item in data:
        raw_root = item.get("root", "")
        if not raw_root:
            continue
        norm_key = normalize_sovereign(raw_root)
        r_index[norm_key] = {
            "root_raw": raw_root,
            "root": norm_key,
            "orbit_id": item.get("orbit_id", 0),
            "weight": item.get("weight", 50.0),
            "insight": item.get("insight_radar", item.get("insight", "")),
            "sig": signature_from_root(norm_key)
        }
    return r_index

# ==============================================================================
# [4] المحرك الموحد
# ==============================================================================
def analyze_text_sovereign(full_text, r_index):
    clean_text = normalize_sovereign(full_text)
    words = clean_text.split()
    matched_details = []
    for pos, word in enumerate(words):
        root_key = match_root_from_word(word, r_index)
        if root_key:
            matched_details.append({"rk": root_key, "pos": pos, "word": word})
    if not matched_details:
        return {"bodies": [], "unique_roots": [], "ascent": 0.0}
    counts = Counter([m['rk'] for m in matched_details])
    bodies = []
    for m in matched_details:
        data = r_index.get(m['rk'])
        if not data:
            continue
        energy = compute_dynamic_energy(
            base_w=data.get('weight', 10),
            count=counts[m['rk']],
            mode="direct",
            morph_rank=5,
            orbit_id=data.get('orbit_id', 0),
            sig=data['sig']
        )
        gene = resolve_sovereign_gene(
            orbit_id=data.get('orbit_id', 0),
            morph_rank=5,
            sig=data['sig'],
            energy=energy
        )
        bodies.append({
            "root_norm": m['rk'],
            "root_raw": data.get('root_raw', m['rk']),
            "energy": energy,
            "gene": gene,
            "sig": data['sig'],
            "style": GENE_STYLE.get(gene, GENE_STYLE['C']),
            "orbit_id": data.get('orbit_id', 0),
            "pos": m['pos'],
            "insight": data.get('insight', '')
        })
    unique_roots = list(set([b['root_norm'] for b in bodies]))
    ascent = compute_ascent_vector(bodies)
    return {
        "bodies": bodies,
        "unique_roots": unique_roots,
        "ascent": ascent,
        "total_words": len(words),
        "matched_count": len(matched_details)
    }

def structural_compare(text1, text2, r_index):
    res1 = analyze_text_sovereign(text1, r_index)
    res2 = analyze_text_sovereign(text2, r_index)
    valid = bool(res1['bodies'] and res2['bodies'])
    return {
        "is_valid": valid,
        "ascent_diff": round(res1['ascent'] - res2['ascent'], 3) if valid else None,
        "common": list(set(res1['unique_roots']) & set(res2['unique_roots'])),
        "avg_energy_1": round(sum(b['energy'] for b in res1['bodies']) / len(res1['bodies']), 2) if res1['bodies'] else 0,
        "avg_energy_2": round(sum(b['energy'] for b in res2['bodies']) / len(res2['bodies']), 2) if res2['bodies'] else 0
    }

# ==============================================================================
# [5] واجهة التجسيد
# ==============================================================================
def render_insight_radar(bodies):
    if not bodies:
        return
    df = pd.DataFrame([{
        'r': b['root_norm'],
        'x': b['sig']['x'],
        'y': b['sig']['y'],
        'e': b['energy'],
        'c': b['style']['color']
    } for b in bodies])
    fig = go.Figure(go.Scatter(
        x=df['x'], y=df['y'],
        mode='markers+text',
        text=df['r'],
        textposition="top center",
        marker=dict(size=df['e']/3, color=df['c'], line=dict(width=1, color='white'))
    ))
    fig.update_layout(
        template="plotly_dark", height=500,
        margin=dict(l=0, r=0, b=0, t=0),
        xaxis=dict(range=[-20,20], visible=False),
        yaxis=dict(range=[-20,20], visible=False)
    )
    st.plotly_chart(fig, use_container_width=True)

def render_sovereign_cards(bodies, limit=12):
    if not bodies:
        return
    for b in bodies[:limit]:
        st.markdown(f"""
        <div style='border-right:4px solid {b["style"]["color"]}; padding:12px; margin-bottom:12px; background:#0d0d14; border-radius:0 8px 8px 0;'>
            <h4 style='color:{b["style"]["color"]}; margin:0;'>{b["style"]["icon"]} {b["root_norm"]}</h4>
            <small>طاقة: {b["energy"]:.1f} | جين: {b["gene"]} | مدار: {b.get("orbit_id", "?")}</small>
            <p style='color:#ddd; margin-top:8px;'>{b.get("insight", "")[:150]}...</p>
        </div>
        """, unsafe_allow_html=True)

# ==============================================================================
# [6] تهيئة التطبيق
# ==============================================================================
st.set_page_config(page_title="Nibras v30.3", page_icon="🛡️", layout="wide")

st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background: radial-gradient(circle at center, #0a0a1a 0%, #000000 100%); color: #e0e0e0; font-family: 'Amiri', serif; direction: rtl; }
    .stTabs [aria-selected="true"] { color: #FFD700 !important; border-bottom: 2px solid #FFD700 !important; }
    .story-box { background: linear-gradient(135deg, rgba(10,21,10,0.85) 0%, rgba(1,1,3,0.95) 100%); padding: 25px; border-radius: 20px; border-right: 5px solid #FFD700; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=3600)
def get_lexicon():
    return load_sovereign_lexicon("data/nibras_lexicon.json")

r_index = get_lexicon()

if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None

with st.sidebar:
    st.markdown(f"""
    <div style='text-align:center;'><h1 style='color:#FFD700;'>🛡️ نبراس</h1><p>v30.3</p></div>
    ---
    📊 إجمالي الجذور: **{len(r_index)}**
    """, unsafe_allow_html=True)
    if r_index:
        st.markdown(f"🔍 عينة: {', '.join(list(r_index.keys())[:8])}")
    st.markdown("---\nخِت فِت.")

tabs = st.tabs(["🔍 الاستنطاق", "🌌 الرنين", "📈 اللوحة", "📜 البيان", "⚖️ الميزان", "🧠 الوعي", "⚖️ المقارن"])

with tabs[0]:
    st.markdown("### 📍 الاستنطاق المداري")
    input_text = st.text_area("أدخل النص:", height=120, placeholder="مثال: أحد أبى أثر")
    if st.button("🚀 تفعيل المفاعل", use_container_width=True):
        if input_text.strip():
            result = analyze_text_sovereign(input_text, r_index)
            st.session_state.analysis_result = result
            if result['bodies']:
                ascent = result['ascent']
                if ascent > 0:
                    st.success(f"🚀 مؤشر الصعود: {ascent}")
                elif ascent < 0:
                    st.warning(f"📌 مؤشر الصعود: {ascent}")
                else:
                    st.info(f"⚖️ مؤشر الصعود: {ascent}")
                st.info(f"📊 {result['total_words']} كلمة → {result['matched_count']} جذر")
                render_insight_radar(result['bodies'])
                st.markdown("### 📜 البيان الختامي")
                genes_count = Counter(b['gene'] for b in result['bodies'])
                dom_gene = max(genes_count, key=genes_count.get)
                st.markdown(f"""
                <div class="story-box">
                    ✅ {len(result['bodies'])} جذر<br>
                    🧬 الهيمنة: {GENE_STYLE[dom_gene]['icon']} {GENE_STYLE[dom_gene]['name']}<br>
                    📚 الجذور: {', '.join(result['unique_roots'][:8])}
                </div>
                """, unsafe_allow_html=True)
                render_sovereign_cards(result['bodies'])
                st.success("✅ تم الاستنطاق")
            else:
                st.error("⚠️ لم يتم العثور على جذور")
                st.info(f"الجذور المتاحة: {', '.join(list(r_index.keys())[:15])}")
        else:
            st.warning("⚠️ أدخل نصاً")

with tabs[1]:
    st.markdown("### 🌌 الرنين الجيني")
    cols = st.columns(5)
    for i, (code, info) in enumerate(GENE_STYLE.items()):
        with cols[i]:
            st.markdown(f"<div style='text-align:center;'><h2>{info['icon']}</h2><h4 style='color:{info['color']};'>{info['name']}</h4></div>", unsafe_allow_html=True)
    if r_index:
        selected = st.selectbox("اختر جذراً:", options=sorted(r_index.keys()))
        if selected:
            d = r_index[selected]
            st.markdown(f"""
            <div style='border:1px solid #2979FF; padding:20px; border-radius:15px;'>
                <h3 style='color:#FFD700;'>📌 {d['root_raw']}</h3>
                <p>المدار: {d.get('orbit_id', '?')} | الوزن: {d.get('weight', 1.0)}</p>
                <p>{d.get('insight', '')}</p>
            </div>
            """, unsafe_allow_html=True)

with tabs[2]:
    if st.session_state.analysis_result and st.session_state.analysis_result['bodies']:
        df = pd.DataFrame([{'الجذر': b['root_norm'], 'الطاقة': b['energy'], 'الجين': b['gene']} for b in st.session_state.analysis_result['bodies']])
        st.dataframe(df, use_container_width=True)
        st.bar_chart(df.set_index('الجذر')['الطاقة'])
    else:
        st.info("⚙️ انتظر تفعيل المفاعل")

with tabs[3]:
    if st.session_state.analysis_result and st.session_state.analysis_result['bodies']:
        result = st.session_state.analysis_result
        st.markdown(f"""
        <div class="story-box">
            <h3 style='color:#FFD700;'>📜 البيان الختامي</h3>
            <p>عدد الجذور: {len(result['bodies'])}</p>
            <p>مجموع الطاقة: {sum(b['energy'] for b in result['bodies']):.1f}</p>
            <p>مؤشر الصعود: {result['ascent']}</p>
            <p>الجذور: {', '.join(result['unique_roots'])}</p>
        </div>
        """, unsafe_allow_html=True)
        render_sovereign_cards(result['bodies'])
    else:
        st.info("⚙️ انتظر تفعيل المفاعل")

with tabs[4]:
    if st.session_state.analysis_result and st.session_state.analysis_result['bodies']:
        render_sovereign_cards(st.session_state.analysis_result['bodies'])
    else:
        st.info("⚙️ انتظر تفعيل المفاعل")

with tabs[5]:
    if st.session_state.analysis_result and st.session_state.analysis_result['bodies']:
        result = st.session_state.analysis_result
        genes_count = Counter(b['gene'] for b in result['bodies'])
        st.markdown(f"""
        <div class="story-box">
            <h3 style='color:#FFD700;'>🌌 بيان الوعي الجمعي</h3>
            <p>عدد الجذور: {len(result['bodies'])}</p>
            <p>مؤشر الصعود: {result['ascent']}</p>
            {''.join([f'<p>{GENE_STYLE[g]["icon"]} {GENE_STYLE[g]["name"]}: {c}</p>' for g, c in genes_count.items()])}
        </div>
        """, unsafe_allow_html=True)
        render_insight_radar(result['bodies'])
    else:
        st.info("⚙️ انتظر تفعيل المفاعل")

with tabs[6]:
    st.markdown("### ⚖️ المقارن البنيوي")
    col1, col2 = st.columns(2)
    with col1:
        t1 = st.text_area("النص الأول:", height=100)
    with col2:
        t2 = st.text_area("النص الثاني:", height=100)
    if st.button("🔍 قارن"):
        if t1.strip() and t2.strip():
            res = structural_compare(t1, t2, r_index)
            if res['is_valid']:
                st.markdown(f"""
                <div class="story-box">
                    <h3 style='color:#FFD700;'>📊 نتائج المقارنة</h3>
                    <p>فرق مؤشر الصعود: {res['ascent_diff']}</p>
                    <p>الجذور المشتركة: {', '.join(res['common']) if res['common'] else 'لا يوجد'}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error("أحد النصين لا يحتوي على جذور")
        else:
            st.warning("أدخل نصين")

st.markdown("---\n<p style='text-align:center;'>خِت فِت.</p>", unsafe_allow_html=True)
