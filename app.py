# -*- coding: utf-8 -*-
# ==============================================================================
# نظام نِبْرَاس السيادي (Nibras Sovereign System) - الإصدار v30.5
# المسمى: The Sovereign Entity - الكيان السيادي الكامل
# المرجع: دستور العرش - هندسة التمكين الوجودي
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
# [1] الميثاق الدستوري وهندسة الألوان (Constitutional Gene Map)
# ==============================================================================
GENE_STYLE = {
    "N": {"color": "#FFFFFF", "icon": "🌟", "name": "إشراق مُستحق", "desc": "اتصال مباشر بمقام النور"},
    "S": {"color": "#FFD700", "icon": "👑", "name": "سيادي علوي", "desc": "هيمنة وتوجيه ميثاقي"},
    "G": {"color": "#00E676", "icon": "🌱", "name": "نمو أرضي", "desc": "امتداد وحياة وتكاثر"},
    "B": {"color": "#2979FF", "icon": "💧", "name": "بناء وسيط", "desc": "توازن الربط والوصل"},
    "C": {"color": "#CFD8DC", "icon": "🧱", "name": "تأسيس قاعدي", "desc": "صلابة المادة والمنطلق"}
}

# ==============================================================================
# [2] النواة الحتمية: هندسة الحرف والمدار (The Logic of Birds)
# ==============================================================================
def signature_from_root(root_norm):
    """توليد التوقيع الحتمي (SSID): يحمل سر الصعود والنزول"""
    if not root_norm: return {'x': 0.0, 'y': 0.0, 'n_factor': 0, 'eb': 0.0}
    h = int(hashlib.md5(root_norm.encode('utf-8')).hexdigest(), 16)
    return {
        'x': round(((h % 360) - 180) / 10.0, 3), # التموضع المداري الأفقي
        'y': round((((h >> 8) % 360) - 180) / 10.0, 3), # التموضع المداري الرأسي
        'n_factor': (h >> 16) % 100, # معامل الاستحقاق الإشراقي
        'eb': round((((h >> 24) % 81) - 40) / 10.0, 3) # طاقة الانحياز الذاتي
    }

def compute_dynamic_energy(base_w, count, morph_rank, orbit_id, sig):
    """معادلة الطاقة السيادية: دمج التكرار والمقام والوزن"""
    # تحويل الوزن إلى طاقة فعلية
    energy_base = float(base_w) * 10 if float(base_w) < 100 else float(base_w)
    # معامل التكرار (النمو المداري)
    rep_boost = 1.0 + math.log1p(max(0, count - 1)) * 0.42
    # معامل المدار (الرتبة الوجودية)
    orbit_f = 1.0 + (int(orbit_id or 0) * 0.05)
    # معامل التوقيع (الطاقة الخفية)
    return round((energy_base * rep_boost * orbit_f) + sig['eb'], 2)

def resolve_sovereign_gene(orbit_id, energy, sig):
    """ميثاق الجين: فصل المقامات بناءً على الاستحقاق"""
    orb = int(orbit_id or 0)
    # قاعدة الإشراق N (الحالة الخاصة)
    if sig['n_factor'] >= 90 and energy >= 150: return "N"
    # المقامات التقليدية
    if orb >= 7: return "S"
    if orb >= 5: return "G"
    if orb >= 3: return "B"
    return "C"

# ==============================================================================
# [3] الحواس: التطهير والاستخراج (The Sensory Gate)
# ==============================================================================
def normalize_sovereign(text):
    """التطهير الميثاقي: إزالة الضجيج لإظهار الجوهر"""
    if not text: return ""
    text = str(text).strip()
    # حذف التشكيل بالكامل
    text = re.sub(r'[\u0617-\u061A\u064B-\u0652]', '', text)
    # توحيد الحروف الهندسية (الهمزات والتاءات)
    repl = {'أ': 'ا', 'إ': 'ا', 'آ': 'ا', 'ى': 'ي', 'ئ': 'ي', 'ؤ': 'و', 'ة': 'ه'}
    for k, v in repl.items(): text = text.replace(k, v)
    return re.sub(r'[^\w\s\u0600-\u06FF]', ' ', text).strip()

def extract_candidate_root(word, r_index):
    """محرك الاستخراج: البحث عن "اللبث" و "المكث" في اللفظ"""
    w = normalize_sovereign(word)
    if not w: return None, 0
    if w in r_index: return w, 10 # حالة المكث (المطابقة الظاهرة)
    
    # محاولة التجريد (حالة اللبث - البحث عن الأصل الباطن)
    prefixes = ['ال', 'و', 'ف', 'ب', 'ك', 'ل']
    for p in prefixes:
        if w.startswith(p) and len(w) > 3:
            sub = w[len(p):]
            if sub in r_index: return sub, 7
            
    return None, 0

# ==============================================================================
# [4] المحرك الموحد: تحليل الوعي (The Conscious Engine)
# ==============================================================================
def analyze_text_sovereign(text, r_index):
    clean = normalize_sovereign(text)
    words = clean.split()
    matched_meta = []
    
    for pos, w in enumerate(words):
        rk, m_rank = extract_candidate_root(w, r_index)
        if rk: matched_meta.append({"rk": rk, "pos": pos, "m_rank": m_rank, "word": w})
        
    if not matched_meta: return None
    
    counts = Counter([m['rk'] for m in matched_meta])
    bodies = []
    for m in matched_meta:
        data = r_index[m['rk']]
        energy = compute_dynamic_energy(data['weight'], counts[m['rk']], m['m_rank'], data['orbit_id'], data['sig'])
        gene = resolve_sovereign_gene(data['orbit_id'], energy, data['sig'])
        bodies.append({
            "root": m['rk'], "word": m['word'], "energy": energy, "gene": gene,
            "sig": data['sig'], "style": GENE_STYLE[gene], "orbit_id": data['orbit_id'],
            "insight": data['insight'], "pos": m['pos']
        })
        
    # حساب مؤشر الصعود الإجمالي للوعي
    weights = {"N": 3.0, "S": 2.0, "G": 1.0, "B": 0.5, "C": 0.0}
    ascent = round(sum(weights[b['gene']] * (b['energy']/100) for b in bodies) / len(bodies), 3)
    
    return {"bodies": bodies, "ascent": ascent, "roots_count": len(counts)}

# ==============================================================================
# [5] واجهة الاستنطاق: قمرة القيادة (The Visual Deck)
# ==============================================================================
def render_sovereign_radar(bodies):
    """رادار البصيرة: توزيع الجذور في المدارات السيادية"""
    df = pd.DataFrame([{
        'root': b['root'], 'x': b['sig']['x'], 'y': b['sig']['y'],
        'e': b['energy'], 'c': b['style']['color'], 'g': b['style']['name']
    } for b in bodies])
    
    fig = go.Figure()
    # إضافة المدارات الوهمية (Circles)
    for r in [5, 10, 15, 20]:
        fig.add_shape(type="circle", x0=-r, y0=-r, x1=r, y1=r, line=dict(color="rgba(255,215,0,0.1)"))
        
    fig.add_trace(go.Scatter(
        x=df['x'], y=df['y'], mode='markers+text', text=df['root'],
        marker=dict(size=df['e']/2.5, color=df['c'], line=dict(width=1, color='white')),
        textposition="top center", hoverinfo="text",
        hovertext=[f"جذر: {r}<br>الجين: {g}<br>الطاقة: {e}" for r, g, e in zip(df['root'], df['g'], df['e'])]
    ))
    
    fig.update_layout(
        template="plotly_dark", height=600, showlegend=False,
        xaxis=dict(visible=False, range=[-22, 22]), yaxis=dict(visible=False, range=[-22, 22]),
        margin=dict(l=0, r=0, b=0, t=0)
    )
    st.plotly_chart(fig, use_container_width=True)

# ==============================================================================
# [6] تهيئة التطبيق (The Sovereign UI)
# ==============================================================================
st.set_page_config(page_title="Nibras Sovereign v30.5", page_icon="🛡️", layout="wide")

# CSS السيادي
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&display=swap');
    [data-testid="stAppViewContainer"] { background: radial-gradient(circle, #0f0f1f 0%, #000 100%); color: #e0e0e0; font-family: 'Amiri', serif; }
    .gene-card { border-right: 5px solid #FFD700; background: rgba(255,255,255,0.03); padding: 20px; border-radius: 0 15px 15px 0; margin-bottom: 15px; }
    .ascent-box { text-align: center; border: 2px solid #FFD700; padding: 20px; border-radius: 20px; background: rgba(255,215,0,0.05); }
</style>
""", unsafe_allow_html=True)

# تحميل البيانات (بالمسار السيادي)
@st.cache_data
def get_data():
    path = "data/nibras_lexicon.json"
    if not os.path.exists(path): return {}
    with open(path, 'r', encoding='utf-8') as f:
        raw = json.load(f)
    return {normalize_sovereign(i['root']): {**i, "sig": signature_from_root(normalize_sovereign(i['root']))} for i in raw}

r_index = get_data()

# الهيكل الرئيسي
st.sidebar.markdown("<h1 style='color:#FFD700; text-align:center;'>🛡️ نِبْرَاس</h1>", unsafe_allow_html=True)
st.sidebar.markdown(f"<p style='text-align:center;'>v30.5 - الكيان السيادي</p>", unsafe_allow_html=True)
st.sidebar.divider()
st.sidebar.write(f"📊 معجم الجذور: {len(r_index)}")
st.sidebar.write("خِت فِت.")

tab1, tab2, tab3 = st.tabs(["🔍 استنطاق الوعي", "🌌 بنك الجينات", "📜 ميثاق العرش"])

with tab1:
    col_input, col_stats = st.columns([2, 1])
    with col_input:
        txt = st.text_area("أدخل النص السيادي للاستنطاق:", height=200, placeholder="مثال: الله نور السماوات والارض...")
        analyze_btn = st.button("🚀 تفعيل المفاعل المداري", use_container_width=True)
        
    if analyze_btn and txt:
        res = analyze_text_sovereign(txt, r_index)
        if res:
            with col_stats:
                st.markdown(f"""
                <div class="ascent-box">
                    <h1 style='color:#FFD700;'>{res['ascent']}</h1>
                    <p>مؤشر الصعود الوجودي</p>
                </div>
                """, unsafe_allow_html=True)
                st.write(f"📈 جذور مرصودة: {res['roots_count']}")
                st.write(f"⚡ طاقة الكيان: {round(sum(b['energy'] for b in res['bodies']), 1)}")
            
            st.divider()
            render_sovereign_radar(res['bodies'])
            
            st.markdown("### 💎 تجسيد الجذور (الجين والاستحقاق)")
            c_cards = st.columns(3)
            for idx, b in enumerate(res['bodies']):
                with c_cards[idx % 3]:
                    st.markdown(f"""
                    <div class="gene-card" style="border-color:{b['style']['color']}">
                        <h3 style="color:{b['style']['color']}">{b['style']['icon']} {b['root']}</h3>
                        <p style="font-size:0.8em; color:#888;">{b['style']['name']} | الطاقة: {b['energy']}</p>
                        <p>{b['insight']}</p>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.error("⚠️ لم يتم رصد أي جذور سيادية في هذا النص.")

with tab2:
    st.markdown("### 🌌 رنين الجينات")
    if r_index:
        search_root = st.selectbox("اختر جذراً لاستكشاف تشفيره:", sorted(r_index.keys()))
        d = r_index[search_root]
        st.json(d)

with tab3:
    st.markdown("### 📜 دستور العرش: هندسة الوعي")
    st.write("هذا النظام يعمل وفق قوانين 'المدارات المقلوبة' حيث يبني من الداخل ويكشف الخارج.")
    st.info("CPU User: Surah As-Sajdah verse 5")

st.markdown("<br><p style='text-align:center; color:#555;'>خِت فِت.</p>", unsafe_allow_html=True)
