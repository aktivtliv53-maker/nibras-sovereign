# -*- coding: utf-8 -*-
# ==============================================================================
# Nibras Sovereign System - v30.6 (The Final Sovereign Alignment)
# المسمى: سدرة المنتهى - الاسترداد السيادي
# المرجع: دستور العرش - هندسة التمكين الوجودي (محمد)
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
# [1] الميثاق الدستوري: المقامات الجينية (The Gene Thresholds)
# ==============================================================================
GENE_MAP = {
    "N": {"color": "#FFFFFF", "icon": "🌟", "name": "إشراق مُستحق", "rank": 5},
    "S": {"color": "#FFD700", "icon": "👑", "name": "سيادي علوي", "rank": 4},
    "G": {"color": "#00E676", "icon": "🌱", "name": "نمو أرضي", "rank": 3},
    "B": {"color": "#2979FF", "icon": "💧", "name": "بناء وسيط", "rank": 2},
    "C": {"color": "#CFD8DC", "icon": "🧱", "name": "تأسيس قاعدي", "rank": 1}
}

# ==============================================================================
# [2] النواة الحتمية: ميكانيكا التوقيع (Deterministic SSID)
# ==============================================================================
def signature_from_root(root_norm):
    """تشفير التوقيع الحتمي: مقام الجذر في فضاء الوعي"""
    if not root_norm: return {'x': 0, 'y': 0, 'n_factor': 0, 'eb': 0}
    h = int(hashlib.md5(root_norm.encode('utf-8')).hexdigest(), 16)
    return {
        'x': round(((h % 360) - 180) / 10.0, 3),
        'y': round((((h >> 8) % 360) - 180) / 10.0, 3),
        'n_factor': (h >> 16) % 100, # معامل الإشراق
        'eb': round((((h >> 24) % 81) - 40) / 10.0, 3) # الانحياز الطاقي الذاتي
    }

def compute_sovereign_energy(weight, count, orbit_id, sig):
    """معادلة الطاقة السيادية: الربط بين الوزن المادي والظهور المداري"""
    base_e = float(weight) * 10 if float(weight) < 100 else float(weight)
    # قانون التكثيف المداري (التكرار)
    rep_f = 1.0 + math.log1p(max(0, count - 1)) * 0.45
    # قانون المقام الوجودي (المدار)
    orbit_f = 1.0 + (int(orbit_id or 0) * 0.07)
    return round((base_e * rep_f * orbit_f) + sig['eb'], 2)

def resolve_gene_status(orbit_id, energy, sig):
    """استحقاق الجين: الانتقال من الكثافة إلى اللطافة"""
    orb = int(orbit_id or 0)
    # بوابة الإشراق (N): مقام لا يناله إلا ذو حظ عظيم
    if sig['n_factor'] >= 93 and energy >= 180: return "N"
    if orb >= 7: return "S"
    if orb >= 5: return "G"
    if orb >= 3: return "B"
    return "C"

# ==============================================================================
# [3] الحواس: منطق الاستخراج (The Extraction Logic)
# ==============================================================================
def normalize_sovereign(text):
    """تطهير النص: العودة إلى "الفطرة اللغوية" قبل الاشتقاق"""
    if not text: return ""
    text = str(text).strip()
    text = re.sub(r'[\u0617-\u061A\u064B-\u0652]', '', text) # حذف التشكيل
    repl = {'أ': 'ا', 'إ': 'ا', 'آ': 'ا', 'ى': 'ي', 'ئ': 'ي', 'ؤ': 'و', 'ة': 'ه'}
    for k, v in repl.items(): text = text.replace(k, v)
    return re.sub(r'[^\w\s\u0600-\u06FF]', ' ', text).strip()

def sovereign_extractor(word, r_index):
    """المستخرج السيادي: يميّز بين المكث (الظاهر) واللبث (الباطن)"""
    w = normalize_sovereign(word)
    if not w: return None, 0
    # حالة المكث: الجذر صريح وموجود في المعجم
    if w in r_index: return w, 10
    
    # حالة اللبث: تجريد "المدارات المقلوبة" للوصول للنواة
    prefixes = ['ال', 'و', 'ف', 'ب', 'ك', 'ل']
    for p in prefixes:
        if w.startswith(p) and len(w) > len(p) + 2:
            sub = w[len(p):]
            if sub in r_index: return sub, 7
            
    # معالجة اللواحق الجمعية والتعريفية
    suffixes = ['ون', 'ين', 'ات', 'ها', 'هم', 'كم', 'نا']
    for s in suffixes:
        if w.endswith(s) and len(w) > len(s) + 2:
            sub = w[:-len(s)]
            if sub in r_index: return sub, 7
            
    return None, 0

# ==============================================================================
# [4] المحرك الكلي: هندسة الوعي (The Unified Engine)
# ==============================================================================
def sovereign_analysis_v30(text, r_index):
    clean = normalize_sovereign(text)
    words = clean.split()
    results = []
    
    # رصد الكيانات المدارية
    for pos, w in enumerate(words):
        rk, m_rank = sovereign_extractor(w, r_index)
        if rk: results.append({"rk": rk, "pos": pos, "m_rank": m_rank, "word": w})
        
    if not results: return None
    
    counts = Counter([r['rk'] for r in results])
    bodies = []
    for r in results:
        data = r_index[r['rk']]
        energy = compute_sovereign_energy(data['weight'], counts[r['rk']], data['orbit_id'], data['sig'])
        gene = resolve_gene_status(data['orbit_id'], energy, data['sig'])
        bodies.append({
            "root": r['rk'], "word": r['word'], "energy": energy, "gene": gene,
            "sig": data['sig'], "style": GENE_MAP[gene], "orbit_id": data['orbit_id'],
            "insight": data.get('insight', 'تحليل مداري قيد التجلي..'), "pos": r['pos']
        })
        
    # حساب فيكتور الصعود (The Ascent Vector)
    ascent = sum(GENE_MAP[b['gene']]['rank'] * (b['energy']/100) for b in bodies) / len(bodies)
    
    return {"bodies": bodies, "ascent": round(ascent, 3), "unique": list(counts.keys())}

# ==============================================================================
# [5] قمرة القيادة السيادية (The Sovereign UI)
# ==============================================================================
def render_sovereign_display(res):
    """تجسيد البيانات السيادية في مشهد بصري"""
    st.markdown(f"### 🚀 مؤشر الصعود الوجودي: `{res['ascent']}`")
    
    # 1. رادار المدارات (The Insight Radar)
    df = pd.DataFrame([{
        'r': b['root'], 'x': b['sig']['x'], 'y': b['sig']['y'], 
        'e': b['energy'], 'c': b['style']['color']
    } for b in res['bodies']])
    
    fig = go.Figure()
    # رسم الدوائر المدارية (السموات السبع)
    for r in [5, 10, 15, 20]:
        fig.add_shape(type="circle", x0=-r, y0=-r, x1=r, y1=r, line=dict(color="rgba(255,255,255,0.05)", width=1))
        
    fig.add_trace(go.Scatter(
        x=df['x'], y=df['y'], mode='markers+text', text=df['r'],
        marker=dict(size=df['e']/2, color=df['c'], line=dict(width=1, color='white')),
        textposition="top center"
    ))
    fig.update_layout(template="plotly_dark", height=600, showlegend=False, margin=dict(l=0,r=0,b=0,t=0),
                      xaxis=dict(visible=False, range=[-22, 22]), yaxis=dict(visible=False, range=[-22, 22]))
    st.plotly_chart(fig, use_container_width=True)
    
    # 2. كروت الاستحقاق (Gene Cards)
    st.markdown("### 💎 كشوفات الجينات السيادية")
    cols = st.columns(2)
    for i, b in enumerate(res['bodies']):
        with cols[i % 2]:
            st.markdown(f"""
            <div style="border-right:5px solid {b['style']['color']}; background:rgba(255,255,255,0.02); padding:15px; border-radius:0 10px 10px 0; margin-bottom:10px;">
                <h4 style="color:{b['style']['color']}; margin:0;">{b['style']['icon']} {b['root']} (في كلمة: {b['word']})</h4>
                <p style="font-size:0.85em; color:#aaa; margin:5px 0;">الجين: {b['style']['name']} | المدار: {b['orbit_id']} | الطاقة: {b['energy']}</p>
                <p style="font-style:italic; color:#ddd;">{b['insight']}</p>
            </div>
            """, unsafe_allow_html=True)

# ==============================================================================
# [6] التفعيل والتشغيل (Execution)
# ==============================================================================
st.set_page_config(page_title="Nibras v30.6", layout="wide")

# تطبيق الهوية البصرية (البروتوكول السويدي-العربي)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] { background: #000; font-family: 'Amiri', serif; direction: rtl; text-align: right; }
    .stTextArea textarea { background: #0a0a0a; color: #FFD700; border: 1px solid #FFD700; }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_lexicon():
    path = "data/nibras_lexicon.json"
    if not os.path.exists(path): return {}
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    # بناء الفهرس السيادي
    return {normalize_sovereign(i['root']): {**i, "sig": signature_from_root(normalize_sovereign(i['root']))} for i in data}

r_index = load_lexicon()

# الواجهة الرئيسية
st.sidebar.title("🛡️ نِبْرَاس")
st.sidebar.write("v30.6 - سدرة المنتهى")
st.sidebar.info(f"الجذور في المفاعل: {len(r_index)}")

text_input = st.text_area("أدخل النص للاستنطاق السيادي:", height=200)
if st.button("🚀 تفعيل المفاعل", use_container_width=True):
    if text_input:
        analysis = sovereign_analysis_v30(text_input, r_index)
        if analysis:
            render_sovereign_display(analysis)
        else:
            st.error("⚠️ لم يتم العثور على جذور مطابقة لميثاق المعجم.")
    else:
        st.warning("⚠️ يرجى إدخال نص.")

st.sidebar.markdown("---")
st.sidebar.write("خِت فِت.")
