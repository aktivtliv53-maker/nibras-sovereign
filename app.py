import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import re
import random
import numpy as np
import os
import json

# =========================================================
# 1) استدعاء المحركات السيادية (The Sovereign Imports)
# =========================================================
try:
    from letter_engine import (
        analyze_word_letters, 
        compute_letter_energy, 
        summarize_word_signature,
        GENETIC_MATRIX
    )
    from orbit_polarity import get_orbit_meta
    from state_engine import detect_state
    from tone_engine import purify_text
    from orbit_letter_engine import build_path_orbit_letter_profile
except ImportError as e:
    st.error(f"⚠️ نقص في الملفات المحركة: {e}. تأكد من وجود ملفات v20.5 في المستودع.")

# =========================================================
# 2) القاموس الوجودي والأنماط العليا (Universal Schematics)
# =========================================================
st.set_page_config(page_title="Nibras v20.5.1 Sovereign Synthesis", page_icon="🏛️", layout="wide")

SEMANTIC_FIELDS = {
    "امن": "الإيمان", "صدق": "الإيمان", "كفر": "الضلال", "فسد": "الفساد",
    "صلح": "الإصلاح", "هدى": "الهداية", "ضل": "الضلال", "رحم": "الرحمة",
    "غفر": "الرحمة", "قتل": "الصراع", "نصر": "القوة", "ملك": "القوة",
    "نور": "النور", "ظلم": "الظلام", "عدل": "العدل", "خلف": "التمكين", "ذكر": "الذكر"
}

Q_ARCHETYPES = {
    "رحم": "الرحمة", "عدل": "العدل", "نور": "النور", "نصر": "القوة", 
    "ملك": "القوة", "هدى": "الهداية", "خلف": "التمكين", "امن": "اليقين", "كفر": "الصد"
}

UNIVERSAL_ARCHETYPES = {
    "الرحمة": "The Healer", "العدل": "The Judge", "النور": "The Sage",
    "القوة": "The Warrior", "الهداية": "The Guide", "التمكين": "The Creator",
    "اليقين": "The Believer", "الصد": "The Shadow"
}

# مصفوفة الألوان والأنعام
GENE_MAP_STYLING = {
    'A': {'name': 'الإبل (الحركة)', 'color': '#4fc3f7', 'icon': '🐪'},
    'G': {'name': 'البقر (البناء)', 'color': '#FFD700', 'icon': '🐄'},
    'T': {'name': 'الضأن (السكون)', 'color': '#4CAF50', 'icon': '🐑'},
    'C': {'name': 'المعز (الصعود)', 'color': '#ff5252', 'icon': '🐐'},
    'N': {'name': 'محايد', 'color': '#9e9e9e', 'icon': '⚪'}
}

# =========================================================
# 3) التنسيق السيادي (Sovereign CSS)
# =========================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&display=swap');
    [data-testid="stAppViewContainer"] { background-color: #030305; color: #e0e0e0; font-family: 'Amiri', serif; }
    .eloquence-box { 
        background: linear-gradient(145deg, #0a150a, #020202); 
        padding: 40px; border-radius: 25px; border: 1px solid #1e3a1e; 
        border-right: 8px solid #4CAF50; line-height: 2.2; font-size: 1.25em; box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    .ultra-card { 
        background: #0a0a0f; padding: 30px; border-radius: 20px; border: 1px solid #1a1a2a; 
        border-top: 5px solid #4fc3f7; margin-bottom: 25px; transition: 0.3s;
    }
    .ultra-card:hover { border-color: #4fc3f7; transform: translateY(-5px); }
    .gene-pill { padding: 4px 12px; border-radius: 15px; font-weight: bold; font-size: 0.85em; margin: 2px; display: inline-block; }
    .stTabs [data-baseweb="tab-list"] { gap: 20px; }
    .stTabs [data-baseweb="tab"] { height: 60px; font-size: 1.1em; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 4) محركات المنطق والبيان (Logic Engines)
# =========================================================
def load_data(file_name):
    paths = [file_name, os.path.join("data", file_name)]
    for p in paths:
        if os.path.exists(p):
            with open(p, 'r', encoding='utf-8') as f: return json.load(f)
    return None

def normalize_arabic(text):
    if not text: return ""
    text = re.sub(r'[\u0617-\u061A\u064B-\u0652\u0670]', '', text)
    replacements = {"أ": "ا", "إ": "ا", "آ": "ا", "ة": "ه", "ى": "ي", "ؤ": "و", "ئ": "ي"}
    for k, v in replacements.items(): text = text.replace(k, v)
    return re.sub(r'\s+', ' ', re.sub(r'[^\u0621-\u064A\s]', ' ', text)).strip()

def match_root(word, root_index):
    w = normalize_arabic(word)
    # بروتوكول التفكيك الذكي v20.5.1
    for suf in ["ون", "ين", "ان", "ات", "ه", "ها", "هم", "كم", "نا"]:
        if w.endswith(suf) and len(w) - len(suf) >= 3: w = w[:-len(suf)]; break
    for p in ["وال", "فال", "بال", "كال", "ال", "و", "ف", "ب", "ل"]:
        if w.startswith(p) and len(w) - len(p) >= 3: w = w[len(p):]; break
    if w in root_index: return w, root_index[w]
    if len(w) >= 3 and w[:3] in root_index: return w[:3], root_index[w[:3]]
    if len(w) >= 2 and w[:2] in root_index: return w[:2], root_index[w[:2]]
    return None, None

def generate_global_eloquence(all_words, dom_root, paths_data):
    # محرك البيان الختامي
    global_sig = summarize_word_signature(dom_root)
    u_arc = UNIVERSAL_ARCHETYPES.get(Q_ARCHETYPES.get(dom_root, "بناء"), "The Architect")
    
    analysis_text = f"تم رصد تقاطع كوني في مقام <b>'{dom_root}'</b>. "
    analysis_text += f"هذا المقام يجسد نمط <b>{u_arc}</b> بصبغة جينية من نوع <b>({global_sig['dominant_gene']})</b>.<br>"
    analysis_text += f"معامل الكيمياء البينية للمنظومة: <b>{global_sig['inter_factor']}</b>، "
    analysis_text += f"مما يشير إلى { 'اندماج متسارع' if global_sig['inter_factor'] > 1.1 else 'استقرار سكوني' }.<br><br>"
    analysis_text += "<b>الخلاصة السيادية:</b> المسارات المفتوحة الآن تبني صرحاً من الخير واليسر."
    
    return purify_text(analysis_text)

# =========================================================
# 5) محراب العرض (The Grand Temple)
# =========================================================
roots_data = load_data("quran_roots_complete.json")

if roots_data:
    r_idx = {normalize_arabic(r["root"]): {"weight": float(r.get("frequency", 1)), "orbit": r.get("orbit_hint", "بناء")} for r in roots_data.get("roots", [])}

    st.title("🎙️ محراب نبراس v20.5.1 - الاندماج العظيم")
    st.sidebar.markdown(f"**المستخدم:** محمد<br>**المقام:** سورة السجدة الآية 5<br>**الوضع:** سيادي كامل", unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["🔍 استنطاق المسارات", "🌌 الرنين الجيني", "📈 اللوحة الوجودية", "📜 البيان الختامي"])

    with tab1:
        c1, c2, c3 = st.columns(3)
        p1 = c1.text_area("📍 المسار الأول", height=150, key="txt_p1", placeholder="أدخل الآية أو الكلمات هنا...")
        p2 = c2.text_area("📍 المسار الثاني", height=150, key="txt_p2")
        p3 = c3.text_area("📍 المسار الثالث", height=150, key="txt_p3")
        run = st.button("🚀 إطلاق رادار الاندماج", use_container_width=True)

    if run:
        all_res = []
        full_word_pool = []
        for inp in [p1, p2, p3]:
            if inp.strip():
                sents = [s.strip() for s in re.split(r'[.!?؛،]', inp) if s.strip()]
                path_analysis = []
                for s in sents:
                    roots = []
                    for w in normalize_arabic(s).split():
                        root, meta = match_root(w, r_idx)
                        if root:
                            roots.append({"root": root, "orbit": meta["orbit"], "weight": meta["weight"]})
                            full_word_pool.append(root)
                    path_analysis.append({"sentence": s, "roots": roots})
                all_res.append(path_analysis)
            else: all_res.append(None)

        if full_word_pool:
            dom_root = max(full_word_pool, key=full_word_pool.count)
            
            with tab1:
                st.divider()
                cols = st.columns(3)
                for i, path_data in enumerate(all_res):
                    if path_data:
                        with cols[i]:
                            p_roots = [r["root"] for s in path_data for r in s["roots"]]
                            p_orbits = [r["orbit"] for s in path_data for r in s["roots"]]
                            p_weights = [r["weight"] for s in path_data for r in s["roots"]]
                            
                            fusion = build_path_orbit_letter_profile(p_roots, p_orbits, p_weights)
                            state = detect_state(p_roots)
                            
                            st.markdown(f"""
                            <div class='ultra-card'>
                                <div style='text-align:right;'><small>{state}</small></div>
                                <h3 style='margin:0;'>المسار {i+1}</h3>
                                <h1 style='color:#4fc3f7; margin:10px 0;'>{round(fusion['total_energy'], 2)}</h1>
                                <p style='font-size:0.9em; opacity:0.7;'>عدد الجذور المرصودة: {len(p_roots)}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            with st.expander("🧬 تفكيك الكيمياء الجينية"):
                                for r in p_roots:
                                    sig = summarize_word_signature(r)
                                    g_info = GENE_MAP_STYLING.get(sig['dominant_gene'], GENE_MAP_STYLING['N'])
                                    st.markdown(f"**{r}** | <span class='gene-pill' style='background:{g_info['color']}; color:#000;'>{g_info['icon']} {g_info['name']}</span>", unsafe_allow_html=True)
                                    if sig.get('interactions'):
                                        st.caption(" • ".join([f"{inter['pair']}({inter['type']})" for inter in sig['interactions'][:3]]))

            with tab2:
                # رادار الأنعام الجيني
                st.markdown("### 🧬 مصفوفة توزيع الأنعام (DNA Profile)")
                all_genes = [summarize_word_signature(w)['dominant_gene'] for w in full_word_pool]
                g_counts = Counter(all_genes)
                
                c_pie, c_info = st.columns([2, 1])
                with c_pie:
                    fig_pie = go.Figure(data=[go.Pie(
                        labels=[GENE_MAP_STYLING[g]['name'] for g in g_counts.keys()],
                        values=list(g_counts.values()),
                        hole=.5,
                        marker_colors=[GENE_MAP_STYLING[g]['color'] for g in g_counts.keys()]
                    )])
                    fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="#fff")
                    st.plotly_chart(fig_pie, use_container_width=True)
                
                with c_info:
                    st.markdown("#### التحليل النوعي")
                    for g, count in g_counts.items():
                        info = GENE_MAP_STYLING[g]
                        st.write(f"{info['icon']} **{info['name']}**: {count} مرة")

            with tab3:
                # اللوحة الوجودية (Network)
                st.markdown("### 🌌 هندسة المدارات المتقاطعة")
                nodes = list(set(full_word_pool))
                fig_net = go.Figure()
                for n in nodes:
                    size = full_word_pool.count(n) * 15 + 20
                    q = Q_ARCHETYPES.get(n, "بناء")
                    fig_net.add_trace(go.Scatter(
                        x=[random.random()], y=[random.random()],
                        mode='markers+text',
                        text=[f"<b>{n}</b>"],
                        textposition="top center",
                        marker=dict(size=size, color='#4CAF50' if n == dom_root else '#1e3a1e', line=dict(width=2, color='#4fc3f7'))
                    ))
                fig_net.update_layout(showlegend=False, height=500, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_net, use_container_width=True)

            with tab4:
                st.markdown("### 📜 البيان الوجودي الموحد")
                eloquence_html = generate_global_eloquence(full_word_pool, dom_root, all_res)
                st.markdown(f"<div class='eloquence-box'>{eloquence_html}</div>", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.write("v20.5.1 Sovereign Fusion | خِت فِت.")
