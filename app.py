# -*- coding: utf-8 -*-
# ==============================================================================
# نظام نِبْرَاس السيادي (Nibras Sovereign System) - الإصدار v30.1
# المسمى: The Final Stable Engine - المحرك المستقر النهائي
# الميثاق: نواة حتمية + حواس استخراج + رادار بصري + مقارن بنيوي
# المستخدم المهيمن: محمّد | CPU: السجدة (5)
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
# [1] الميثاق الدستوري (Constitutional Standards)
# ==============================================================================
GENE_STYLE = {
    "N": {"color": "#FFFFFF", "icon": "🌟", "name": "إشراق مُستحق"},
    "S": {"color": "#FFD700", "icon": "👑", "name": "سيادي علوي"},
    "G": {"color": "#00E676", "icon": "🌱", "name": "نمو أرضي"},
    "B": {"color": "#2979FF", "icon": "💧", "name": "بناء وسيط"},
    "C": {"color": "#CFD8DC", "icon": "🧱", "name": "تأسيس قاعدي"}
}

# ==============================================================================
# [2] النواة الحتمية (The Deterministic Core) - "ممنوع التعديل"
# ==============================================================================
def signature_from_root(root_norm):
    """
    التوقيع الجذري الحتمي - المصدر الوحيد للإحداثيات والعوامل
    أي تغيير في هذه الدالة يغير الخريطة بأكملها
    """
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
    """
    الطاقة الديناميكية الحتمية
    تعتمد على: الوزن الأساسي + التكرار + ثقة المطابقة + الرتبة الصرفية + المدار + انحياز التوقيع
    """
    base_e = base_w * 100 if base_w < 10 else base_w
    rep_boost = 1.0 + math.log1p(max(0, count - 1)) * 0.35
    mode_f = 1.0 if mode == "direct" else 0.92
    morph_f = 1.0 + (max(2, morph_rank) - 2) * 0.05
    orbit_f = 1.0 + max(0, int(orbit_id or 0) - 4) * 0.03
    return round((base_e * rep_boost * mode_f * morph_f * orbit_f) + sig['eb'], 2)

def resolve_sovereign_gene(orbit_id, morph_rank, sig, energy):
    """
    الاستحقاق الجيني الميثاقي
    القاعدة الذهبية: الإشراق N لا يحدث إلا باستحقاق مركب
    """
    orb = int(orbit_id or 0)
    # التصنيف الأساسي حسب المدار
    if orb >= 7:
        base = "S"
    elif orb >= 5:
        base = "G"
    elif orb >= 3:
        base = "B"
    else:
        base = "C"
    
    # بوابة الإشراق N - لا يدخلها إلا المستحقون
    if sig['n_factor'] >= 92 and (orb >= 5 or morph_rank >= 6 or energy >= 85):
        return "N"
    
    return base

def compute_ascent_vector(bodies):
    """مؤشر الصعود الموزون - يعكس نبرة النص الروحية"""
    if not bodies:
        return 0.0
    weights = {"N": 2.5, "S": 1.8, "G": 1.0, "B": 0.2, "C": -0.5}
    total = sum((weights.get(b['gene'], 0) * (b['energy'] / 100)) for b in bodies)
    return round(total / len(bodies), 3)

# ==============================================================================
# [3] الحواس والإمداد (Senses & Feeding)
# ==============================================================================
def normalize_sovereign(text):
    """
    تطهير النص السيادي - يمرر كل النصوص قبل أي معالجة
    """
    if not text:
        return ""
    text = str(text).strip()
    # إزالة التشكيل
    text = re.sub(r'[\u0617-\u061A\u064B-\u0652]', '', text)
    # توحيد الأحرف المتشابهة
    text = text.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا')
    text = text.replace('ى', 'ي').replace('ئ', 'ي').replace('ؤ', 'و')
    text = text.replace('ة', 'ه')
    # إزالة الرموز غير العربية
    return re.sub(r'[^\w\s\u0600-\u06FF]', ' ', text).strip()

def extract_candidate_root(word, r_index):
    """
    استخراج الجذر المرشح من الكلمة مع الرتبة الصرفية
    """
    w = normalize_sovereign(word)
    if not w:
        return None, 0
    
    # مطابقة مباشرة
    if w in r_index:
        return w, 10
    
    # إزالة الزوائد الصرفية
    prefixes = ['ال', 'و', 'ف', 'ب', 'ل', 'س', 'ك']
    suffixes = ['ون', 'ين', 'ات', 'ان', 'ه', 'ها', 'هم', 'كن', 'نا', 'تم']
    
    temp_w = w
    for p in prefixes:
        if temp_w.startswith(p) and len(temp_w) > 3:
            temp_w = temp_w[len(p):]
            break
    for s in suffixes:
        if temp_w.endswith(s) and len(temp_w) > 3:
            temp_w = temp_w[:-len(s)]
            break
    
    if temp_w in r_index:
        return temp_w, 7
    
    return None, 0

def load_sovereign_lexicon(file_path):
    """
    تحميل الليكسيكون السيادي مع توليد التوقيعات الحتمية مسبقاً
    ملف JSON هو مصفوفة من الكائنات، كل كائن له مفتاح "root"
    """
    if not os.path.exists(file_path):
        st.error(f"❌ ملف الليكسيكون غير موجود: {file_path}")
        return {}
    
    with open(file_path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            st.error(f"❌ خطأ في JSON: {e}")
            return {}
    
    # التأكد من أن البيانات مصفوفة
    if not isinstance(data, list):
        st.error("❌ ملف JSON يجب أن يكون مصفوفة من الجذور")
        return {}
    
    r_index = {}
    for item in data:
        # استخراج الجذر الخام
        raw_root = item.get("root", "")
        if not raw_root:
            continue
        
        # تطبيع الجذر لاستخدامه كمفتاح
        norm_key = normalize_sovereign(raw_root)
        
        # تخزين البيانات مع التوقيع الحتمي
        r_index[norm_key] = {
            "root_raw": raw_root,
            "root": norm_key,
            "orbit_id": item.get("orbit_id", 0),
            "weight": item.get("weight", 50.0),
            "insight": item.get("insight_radar", item.get("insight", "")),
            "energy_type": item.get("energy_type", "مزدوج"),
            "carrier_type": item.get("carrier_type", ""),
            "bio_link": item.get("bio_link", ""),
            "structural_analysis": item.get("structural_analysis", ""),
            "sig": signature_from_root(norm_key)
        }
    
    return r_index

# ==============================================================================
# [4] المحرك الموحد والمقارن (Unified Engine)
# ==============================================================================
def analyze_text_sovereign(full_text, r_index):
    """
    تحليل النص بالكامل وإرجاع النتائج الموحدة
    """
    clean_text = normalize_sovereign(full_text)
    words = clean_text.split()
    
    # المرحلة 1: استخراج الجذور والرتب الصرفية
    matched_meta = []
    for pos, word in enumerate(words):
        rk, m_rank = extract_candidate_root(word, r_index)
        if rk:
            matched_meta.append({
                "rk": rk,
                "pos": pos,
                "m_rank": m_rank
            })
    
    if not matched_meta:
        return {"bodies": [], "unique_roots": [], "ascent": 0.0, "counts": Counter()}
    
    # المرحلة 2: حساب التكرارات الحقيقية
    counts = Counter([m['rk'] for m in matched_meta])
    
    # المرحلة 3: بناء الأجسام الجذرية
    bodies = []
    for m in matched_meta:
        data = r_index.get(m['rk'])
        if not data:
            continue
        
        # حساب الطاقة الديناميكية
        energy = compute_dynamic_energy(
            base_w=data.get('weight', 10),
            count=counts[m['rk']],
            mode="direct",
            morph_rank=m['m_rank'],
            orbit_id=data.get('orbit_id', 0),
            sig=data['sig']
        )
        
        # حسم الجين النهائي
        gene = resolve_sovereign_gene(
            orbit_id=data.get('orbit_id', 0),
            morph_rank=m['m_rank'],
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
            "pos": m['pos']
        })
    
    # المرحلة 4: حساب المؤشرات الإجمالية
    unique_roots = list(counts.keys())
    ascent = compute_ascent_vector(bodies)
    
    return {
        "bodies": bodies,
        "unique_roots": unique_roots,
        "ascent": ascent,
        "counts": counts
    }

def structural_compare(text1, text2, r_index):
    """
    المقارنة البنيوية بين نصين
    """
    res1 = analyze_text_sovereign(text1, r_index)
    res2 = analyze_text_sovereign(text2, r_index)
    
    valid = bool(res1['bodies'] and res2['bodies'])
    
    return {
        "is_valid": valid,
        "ascent_diff": round(res1['ascent'] - res2['ascent'], 3) if valid else None,
        "common": list(set(res1['unique_roots']) & set(res2['unique_roots'])),
        "only_in_1": list(set(res1['unique_roots']) - set(res2['unique_roots'])),
        "only_in_2": list(set(res2['unique_roots']) - set(res1['unique_roots'])),
        "avg_energy_1": round(sum(b['energy'] for b in res1['bodies']) / len(res1['bodies']), 2) if res1['bodies'] else 0,
        "avg_energy_2": round(sum(b['energy'] for b in res2['bodies']) / len(res2['bodies']), 2) if res2['bodies'] else 0
    }

# ==============================================================================
# [5] واجهة التجسيد (The Visual Deck)
# ==============================================================================
def render_insight_radar(bodies):
    """
    رسم رادار الاستنطاق - خريطة حتمية للجذور
    """
    if not bodies:
        st.info("لا توجد بيانات للعرض.")
        return
    
    df = pd.DataFrame([{
        'r': b['root_norm'],
        'x': b['sig']['x'],
        'y': b['sig']['y'],
        'e': b['energy'],
        'c': b['style']['color']
    } for b in bodies])
    
    fig = go.Figure(go.Scatter(
        x=df['x'],
        y=df['y'],
        mode='markers+text',
        text=df['r'],
        textposition="top center",
        textfont=dict(color='white', size=10),
        marker=dict(
            size=df['e'] / 3,
            color=df['c'],
            line=dict(width=1, color='white'),
            sizemode='area'
        )
    ))
    
    fig.update_layout(
        template="plotly_dark",
        height=500,
        margin=dict(l=0, r=0, b=0, t=0),
        xaxis=dict(range=[-20, 20], showgrid=False, zeroline=False, visible=False),
        yaxis=dict(range=[-20, 20], showgrid=False, zeroline=False, visible=False),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_sovereign_cards(bodies, limit=12):
    """
    عرض الكروت السيادية للجذور المستنطقة
    """
    if not bodies:
        st.info("لا توجد بيانات للعرض.")
        return
    
    cols = st.columns(3)
    for i, b in enumerate(bodies[:limit]):
        with cols[i % 3]:
            st.markdown(f"""
            <div style='border:1px solid {b['style']['color']};padding:12px;border-radius:8px;background:#1a1a1a;margin-bottom:8px;'>
                <h4 style='color:{b['style']['color']};margin:0 0 5px 0;'>{b['style']['icon']} {b['root_norm']}</h4>
                <small style='color:#aaa;'>طاقة: {b['energy']:.1f} | جين: {b['gene']}</small>
                <br><small style='color:#666;'>المدار: {b.get('orbit_id', '?')}</small>
            </div>
            """, unsafe_allow_html=True)

# ==============================================================================
# [6] تهيئة التطبيق وإعدادات الصفحة
# ==============================================================================
st.set_page_config(
    page_title="Nibras v30.1 - المحرك المستقر النهائي",
    page_icon="🛡️",
    layout="wide"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&display=swap');
    [data-testid="stAppViewContainer"] {
        background: radial-gradient(circle at center, #0a0a1a 0%, #000000 100%);
        color: #e0e0e0;
        font-family: 'Amiri', serif;
        direction: rtl;
    }
    .stTabs [aria-selected="true"] {
        color: #FFD700 !important;
        border-bottom: 2px solid #FFD700 !important;
    }
    .story-box {
        background: linear-gradient(135deg, rgba(10,21,10,0.85) 0%, rgba(1,1,3,0.95) 100%);
        padding: 30px;
        border-radius: 20px;
        border-right: 5px solid #FFD700;
        line-height: 1.8;
        margin-bottom: 20px;
    }
    .st-emotion-cache-1v0mbdj, .st-emotion-cache-1wivap2 {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# [7] تحميل البيانات وتهيئة الجلسة
# ==============================================================================
@st.cache_data(ttl=3600)
def get_lexicon():
    return load_sovereign_lexicon("data/nibras_lexicon.json")

r_index = get_lexicon()

if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None
if 'compare_result' not in st.session_state:
    st.session_state.compare_result = None

# ==============================================================================
# [8] الشريط الجانبي
# ==============================================================================
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding:10px;'>
        <h1 style='color:#FFD700; margin:0;'>🛡️ نبراس السيادي</h1>
        <p style='color:#888;'>الإصدار v30.1</p>
        <p style='color:#555;'>المستخدم: محمد</p>
    </div>
    ---
    <div style='padding:5px;'>
        <p style='color:#4CAF50;'>📊 إحصائيات القاعدة:</p>
        <p>📚 إجمالي الجذور: <span style='color:#FFD700;'>{len(r_index)}</span></p>
    </div>
    ---
    <div style='text-align:center; padding:10px;'>
        <p style='color:#555;'>خِت فِت.</p>
    </div>
    """, unsafe_allow_html=True)

# ==============================================================================
# [9] التبويبات السيادية
# ==============================================================================
tabs = st.tabs([
    "🔍 الاستنطاق المداري",
    "🌌 الرنين الجيني",
    "📈 اللوحة الوجودية",
    "📜 البيان الختامي",
    "⚖️ الميزان السيادي",
    "🧠 الوعي الفوقي",
    "⚖️ المقارن البنيوي"
])

# ==================== التبويب 0: الاستنطاق ====================
with tabs[0]:
    st.markdown("### 📍 هندسة المسارات المدارية - المحرك المستقر النهائي")
    
    input_text = st.text_area(
        "أدخل النص للاستنطاق:",
        height=150,
        placeholder="مثال: أحد أبى أثر أجد أجل أخذ",
        key="input_area"
    )
    
    if st.button("🚀 تفعيل المفاعل السيادي v30.1", use_container_width=True):
        if input_text.strip():
            with st.spinner("جاري استنطاق النص..."):
                result = analyze_text_sovereign(input_text, r_index)
                st.session_state.analysis_result = result
            
            if result['bodies']:
                # مؤشر الصعود
                ascent = result['ascent']
                if ascent > 0:
                    st.success(f"🚀 مؤشر الصعود: {ascent} - صعود طاقي نحو المعاني العلوية")
                elif ascent < 0:
                    st.warning(f"📌 مؤشر الصعود: {ascent} - تثبيت مادي في الجذور الأرضية")
                else:
                    st.info(f"⚖️ مؤشر الصعود: {ascent} - توازن بين الصعود والثبات")
                
                # رادار الاستنطاق
                render_insight_radar(result['bodies'])
                
                # البيان الختامي
                st.markdown("### 📜 البيان الختامي")
                genes_count = Counter(b['gene'] for b in result['bodies'])
                dom_gene = max(genes_count, key=genes_count.get)
                total_energy = sum(b['energy'] for b in result['bodies'])
                
                st.markdown(f"""
                <div class="story-box">
                    ✅ تم استنطاق <b>{len(result['bodies'])}</b> جسماً جذرياً.<br>
                    🧬 الهيمنة الجينية: <b>{GENE_STYLE[dom_gene]['icon']} {GENE_STYLE[dom_gene]['name']}</b><br>
                    ⚡ مجموع الطاقة: <b>{total_energy:.1f}</b><br>
                    📚 الجذور الفريدة: <b>{', '.join(result['unique_roots'][:10])}</b>
                    {'...' if len(result['unique_roots']) > 10 else ''}
                </div>
                """, unsafe_allow_html=True)
                
                # كروت الاستنطاق
                st.markdown("### 🔍 تفاصيل الاستنطاق")
                render_sovereign_cards(result['bodies'])
                st.success("✅ تم الاستنطاق بنجاح.")
            else:
                st.error("⚠️ لم يتم العثور على جذور مطابقة في قاعدة البيانات.")
        else:
            st.warning("⚠️ الرجاء إدخال نص للاستنطاق.")

# ==================== التبويب 1: الرنين الجيني ====================
with tabs[1]:
    st.markdown("### 🌌 مصفوفة الرنين والاستحقاق الجيني")
    
    cols = st.columns(5)
    for i, (code, info) in enumerate(GENE_STYLE.items()):
        with cols[i]:
            st.markdown(f"""
            <div style='text-align:center; padding:15px; background:#0d0d14; border-radius:15px; border-top:3px solid {info["color"]};'>
                <h2 style='margin:0;'>{info['icon']}</h2>
                <h4 style='margin:5px 0; color:{info["color"]};'>{info['name']}</h4>
                <small style='color:#888;'>{code}</small>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 📖 استنطاق جذر محدد")
    
    if r_index:
        root_options = sorted([k for k in r_index.keys()])
        selected = st.selectbox("اختر جذراً:", options=root_options)
        
        if selected:
            data = r_index.get(selected)
            if data:
                sig = data.get('sig', {})
                st.markdown(f"""
                <div style='border:1px solid #2979FF; padding:20px; border-radius:15px; background:#0d0d14; margin-top:15px;'>
                    <h3 style='color:#FFD700; margin:0;'>📌 {data.get('root_raw', selected)}</h3>
                    <p><b>المدار:</b> {data.get('orbit_id', 'غير محدد')}</p>
                    <p><b>الوزن:</b> {data.get('weight', 1.0)}</p>
                    <p><b>عامل الإشراق (n_factor):</b> {sig.get('n_factor', 0)}</p>
                    <p><b>الإحداثيات:</b> ({sig.get('x', 0)}, {sig.get('y', 0)})</p>
                    <hr>
                    <p><b>🔮 بصيرة الجذر:</b></p>
                    <p>{data.get('insight', 'لا توجد بصيرة مسجلة')}</p>
                </div>
                """, unsafe_allow_html=True)

# ==================== التبويب 2: اللوحة الوجودية ====================
with tabs[2]:
    st.markdown("### 📈 التحليل الكمي للمدار")
    
    if st.session_state.analysis_result and st.session_state.analysis_result['bodies']:
        bodies = st.session_state.analysis_result['bodies']
        df = pd.DataFrame([{
            'الجذر': b['root_norm'],
            'الطاقة': b['energy'],
            'الجين': b['gene'],
            'المدار': b.get('orbit_id', 0)
        } for b in bodies])
        
        col1, col2 = st.columns(2)
        with col1:
            st.dataframe(df, use_container_width=True)
        with col2:
            st.bar_chart(df.set_index('الجذر')['الطاقة'])
        
        st.markdown("---")
        st.markdown("#### 📊 إحصائيات الطاقة")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("متوسط الطاقة", f"{df['الطاقة'].mean():.1f}")
        with col2:
            st.metric("أقصى طاقة", f"{df['الطاقة'].max():.1f}")
        with col3:
            st.metric("أدنى طاقة", f"{df['الطاقة'].min():.1f}")
    else:
        st.info("⚙️ انتظر تفعيل المفاعل في التبويب الأول.")

# ==================== التبويب 3: البيان الختامي ====================
with tabs[3]:
    st.markdown("### 📜 البيان الختامي")
    
    if st.session_state.analysis_result and st.session_state.analysis_result['bodies']:
        result = st.session_state.analysis_result
        total_energy = sum(b['energy'] for b in result['bodies'])
        genes_count = Counter(b['gene'] for b in result['bodies'])
        dom_gene = max(genes_count, key=genes_count.get)
        
        st.markdown(f"""
        <div class="story-box">
            <h3 style='color:#FFD700; margin:0 0 15px 0;'>📜 البيان الختامي الموسع</h3>
            <p><b>عدد الجذور المستنطقة:</b> {len(result['bodies'])}</p>
            <p><b>مجموع الطاقة:</b> {total_energy:.1f}</p>
            <p><b>الهيمنة الجينية:</b> {GENE_STYLE[dom_gene]['icon']} {GENE_STYLE[dom_gene]['name']}</p>
            <p><b>مؤشر الصعود:</b> {result['ascent']}</p>
            <p><b>الجذور الفريدة:</b> {', '.join(result['unique_roots'])}</p>
        </div>
        """, unsafe_allow_html=True)
        
        render_sovereign_cards(result['bodies'])
    else:
        st.info("⚙️ انتظر تفعيل المفاعل في التبويب الأول.")

# ==================== التبويب 4: الميزان السيادي ====================
with tabs[4]:
    st.markdown("### ⚖️ ميزان النزاهة الجذرية")
    
    if st.session_state.analysis_result and st.session_state.analysis_result['bodies']:
        render_sovereign_cards(st.session_state.analysis_result['bodies'])
    else:
        st.info("⚙️ انتظر تفعيل المفاعل في التبويب الأول.")

# ==================== التبويب 5: الوعي الفوقي ====================
with tabs[5]:
    st.markdown("### 🧠 الوعي الفوقي - البيان الجمعي")
    
    if st.session_state.analysis_result and st.session_state.analysis_result['bodies']:
        result = st.session_state.analysis_result
        total_energy = sum(b['energy'] for b in result['bodies'])
        genes_count = Counter(b['gene'] for b in result['bodies'])
        
        st.markdown(f"""
        <div class="story-box">
            <h3 style='color:#FFD700; margin:0 0 15px 0;'>🌌 بيان الوعي الجمعي</h3>
            <p><b>عدد الجذور:</b> {len(result['bodies'])}</p>
            <p><b>مجموع الطاقة:</b> {total_energy:.1f}</p>
            <p><b>مؤشر الصعود:</b> {result['ascent']}</p>
            <p><b>توزيع الجينات:</b></p>
            {''.join([f'<p style="margin-right:20px;">{GENE_STYLE[g]["icon"]} {GENE_STYLE[g]["name"]}: {c}</p>' for g, c in genes_count.items()])}
        </div>
        """, unsafe_allow_html=True)
        
        render_insight_radar(result['bodies'])
    else:
        st.info("⚙️ انتظر تفعيل المفاعل في التبويب الأول.")

# ==================== التبويب 6: المقارن البنيوي ====================
with tabs[6]:
    st.markdown("### ⚖️ المقارن البنيوي - مقارنة بين نصين")
    
    col1, col2 = st.columns(2)
    with col1:
        text1 = st.text_area("النص الأول:", height=120, key="compare_text1", placeholder="أدخل النص الأول هنا...")
    with col2:
        text2 = st.text_area("النص الثاني:", height=120, key="compare_text2", placeholder="أدخل النص الثاني هنا...")
    
    if st.button("🔍 قارن بين النصين", use_container_width=True):
        if text1.strip() and text2.strip():
            with st.spinner("جاري المقارنة..."):
                result = structural_compare(text1, text2, r_index)
                st.session_state.compare_result = result
            
            if result['is_valid']:
                st.markdown(f"""
                <div class="story-box">
                    <h3 style='color:#FFD700; margin:0 0 15px 0;'>📊 نتائج المقارنة</h3>
                    <p><b>فرق مؤشر الصعود:</b> {result['ascent_diff']}</p>
                    <p><b>فرق متوسط الطاقة:</b> {result['avg_energy_1'] - result['avg_energy_2']:.2f}</p>
                    <p><b>الجذور المشتركة:</b> {', '.join(result['common']) if result['common'] else 'لا يوجد'}</p>
                    <p><b>جذور فريدة في النص الأول:</b> {', '.join(result['only_in_1'][:5]) if result['only_in_1'] else 'لا يوجد'}</p>
                    <p><b>جذور فريدة في النص الثاني:</b> {', '.join(result['only_in_2'][:5]) if result['only_in_2'] else 'لا يوجد'}</p>
                </div>
                """, unsafe_allow_html=True)
                
                comp_data = pd.DataFrame({
                    'المقياس': ['متوسط الطاقة', 'مؤشر الصعود'],
                    'النص الأول': [result['avg_energy_1'], result['ascent_diff'] + result['avg_energy_2']],
                    'النص الثاني': [result['avg_energy_2'], result['avg_energy_2']]
                })
                st.dataframe(comp_data, use_container_width=True)
            else:
                st.error("⚠️ أحد النصين أو كليهما لا يحتوي على جذور مطابقة.")
        else:
            st.warning("⚠️ الرجاء إدخال نصين للمقارنة.")
