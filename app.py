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
ENGINES_OK = True
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
except Exception as e:
    ENGINES_OK = False
    st.error(f"⚠️ فشل سيادي في تحميل المحركات: {e}")

# =========================================================
# 2) القاموس الوجودي والأنماط العليا (Universal Schematics)
# =========================================================
st.set_page_config(page_title="Nibras v20.5.3 Herd Balance", page_icon="⚖️", layout="wide")

Q_ARCHETYPES = {
    "رحم": "الرحمة", "عدل": "العدل", "نور": "النور", "نصر": "القوة", 
    "ملك": "القوة", "هدى": "الهداية", "خلف": "التمكين", "امن": "اليقين", "كفر": "الصد"
}

UNIVERSAL_ARCHETYPES = {
    "الرحمة": "The Healer", "العدل": "The Judge", "النور": "The Sage",
    "القوة": "The Warrior", "الهداية": "The Guide", "التمكين": "The Creator",
    "اليقين": "The Believer", "الصد": "The Shadow"
}

GENE_STYLE = {
    'A': {'name': 'الإبل (الحركة)', 'color': '#4fc3f7', 'icon': '🐪', 'desc': 'طاقة اندفاع وسفر داخلي'},
    'G': {'name': 'البقر (البناء)', 'color': '#FFD700', 'icon': '🐄', 'desc': 'طاقة إنتاج وتحمل وثقل'},
    'T': {'name': 'الضأن (السكون)', 'color': '#4CAF50', 'icon': '🐑', 'desc': 'طاقة ألفة وهدوء واستقرار'},
    'C': {'name': 'المعز (الصعود)', 'color': '#ff5252', 'icon': '🐐', 'desc': 'طاقة تحدي وإرادة وثبات'},
    'N': {'name': 'محايد', 'color': '#9e9e9e', 'icon': '⚪', 'desc': 'طاقة متوازنة'}
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
        border-right: 8px solid #4CAF50; line-height: 2.2; font-size: 1.25em;
    }
    .ultra-card { 
        background: #0a0a0f; padding: 30px; border-radius: 20px; border: 1px solid #1a1a2a; 
        border-top: 5px solid #4fc3f7; margin-bottom: 25px;
    }
    .gene-pill { padding: 4px 12px; border-radius: 15px; font-weight: bold; font-size: 0.85em; margin: 2px; display: inline-block; }
    .interaction-badge { font-size: 0.75em; background: #1a1a2a; padding: 2px 8px; border-radius: 10px; color: #4fc3f7; border: 1px solid #4fc3f7; margin: 2px; display: inline-block; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 4) المحركات المساعدة (Helper Engines)
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
    for suf in ["ون", "ين", "ان", "ات", "ه", "ها", "هم", "كم", "نا"]:
        if w.endswith(suf) and len(w) - len(suf) >= 3: w = w[:-len(suf)]; break
    for p in ["وال", "فال", "بال", "كال", "ال", "و", "ف", "ب", "ل"]:
        if w.startswith(p) and len(w) - len(p) >= 3: w = w[len(p):]; break
    if w in root_index: return w, root_index[w]
    if len(w) >= 3 and w[:3] in root_index: return w[:3], root_index[w[:3]]
    if len(w) >= 2 and w[:2] in root_index: return w[:2], root_index[w[:2]]
    return None, None

def generate_global_eloquence(dom_root):
    global_sig = summarize_word_signature(dom_root)
    u_arc = UNIVERSAL_ARCHETYPES.get(Q_ARCHETYPES.get(dom_root, "بناء"), "The Architect")
    analysis_text = f"تم رصد تقاطع كوني في مقام <b>'{dom_root}'</b> بصبغة جينية <b>({global_sig['dominant_gene']})</b>.<br>"
    analysis_text += f"نمط الاندماج: <b>{u_arc}</b> | الكيمياء البينية: <b>{global_sig['inter_factor']}</b>.<br><br>"
    analysis_text += "<b>الخلاصة:</b> النظام يسجل حالة من الاتزان واليسر في تدفق المعنى."
    return purify_text(analysis_text)

# =========================================================
# 5) التنفيذ والواجهة (The Protected Temple)
# =========================================================
roots_data = load_data("quran_roots_complete.json")

if ENGINES_OK and roots_data:
    r_idx = {normalize_arabic(r["root"]): {"weight": float(r.get("frequency", 1)), "orbit": r.get("orbit_hint", "بناء")} for r in roots_data.get("roots", [])}

    st.title("🎙️ محراب نبراس v20.5.3 - ميزان الأنعام")
    
    tab1, tab2, tab3, tab4 = st.tabs(["🔍 استنطاق المسارات", "🌌 الرنين الجيني", "📈 اللوحة الوجودية", "📜 البيان الختامي"])

    with tab1:
        c1, c2, c3 = st.columns(3)
        p1 = c1.text_area("📍 المسار الأول", height=150, key="txt_p1")
        p2 = c2.text_area("📍 المسار الثاني", height=150, key="txt_p2")
        p3 = c3.text_area("📍 المسار الثالث", height=150, key="txt_p3")
        run = st.button("🚀 تفعيل رادار الميزان", use_container_width=True)

    if run:
        all_res = []
        full_word_pool = []
        for inp in [p1, p2, p3]:
            if inp.strip():
                sents = [s.strip() for s in re.split(r'[.!?؛،]', inp) if s.strip()]
                path_analysis = []
                for s in sents:
                    roots_found = []
                    for w in normalize_arabic(s).split():
                        root, meta = match_root(w, r_idx)
                        if root:
                            roots_found.append({"root": root, "orbit": meta["orbit"], "weight": meta["weight"]})
                            full_word_pool.append(root)
                    path_analysis.append({"sentence": s, "roots": roots_found})
                all_res.append(path_analysis)
            else: all_res.append(None)

        if full_word_pool:
            dom_root = max(full_word_pool, key=full_word_pool.count)
            
            with tab1:
                cols = st.columns(3)
                for i, path_data in enumerate(all_res):
                    if path_data:
                        with cols[i]:
                            p_roots = [r["root"] for s in path_data for r in s["roots"]]
                            p_orbits = [r["orbit"] for s in path_data for r in s["roots"]]
                            p_weights = [r["weight"] for s in path_data for r in s["roots"]]
                            fusion = build_path_orbit_letter_profile(p_roots, p_orbits, p_weights)
                            state = detect_state(p_roots)
                            st.markdown(f"<div class='ultra-card'><small>{state}</small><h3>المسار {i+1}</h3><h1 style='color:#4fc3f7;'>{round(fusion['total_energy'], 2)}</h1></div>", unsafe_allow_html=True)
                            with st.expander("🧬 تفكيك الكيمياء"):
                                for r in p_roots:
                                    sig = summarize_word_signature(r)
                                    g_info = GENE_STYLE.get(sig['dominant_gene'], GENE_STYLE['N'])
                                    st.markdown(f"**{r}** | <span class='gene-pill' style='background:{g_info['color']}; color:#000;'>{g_info['icon']} {sig['dominant_gene']}</span>", unsafe_allow_html=True)

            with tab2:
                st.markdown("### 🧬 مصفوفة توزيع الأنعام (DNA Profile)")
                all_genes = [summarize_word_signature(w)['dominant_gene'] for w in full_word_pool]
                g_counts = Counter(all_genes)
                
                c_pie, c_list = st.columns([2, 1])
                with c_pie:
                    fig_pie = go.Figure(data=[go.Pie(labels=[GENE_STYLE[g]['name'] for g in g_counts.keys()], values=list(g_counts.values()), hole=.4, marker_colors=[GENE_STYLE[g]['color'] for g in g_counts.keys()])])
                    fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="#fff")
                    st.plotly_chart(fig_pie, use_container_width=True)
                with c_list:
                    st.markdown("#### التكرار الجيني")
                    for g, count in g_counts.items():
                        st.write(f"{GENE_STYLE[g]['icon']} **{GENE_STYLE[g]['name']}**: {count}")

                st.divider()
                st.markdown("### ⚖️ ميزان الأنعام السيادي (Sovereign Herd Balance)")
                
                path_balances = []
                for idx, p_data in enumerate(all_res):
                    if p_data:
                        p_roots = [r["root"] for s in p_data for r in s["roots"]]
                        p_genes = [summarize_word_signature(w)['dominant_gene'] for w in p_roots]
                        if p_genes:
                            dom_g = Counter(p_genes).most_common(1)[0][0]
                            path_balances.append({"المسار": f"المسار {idx+1}", "الجين الغالب": dom_g})

                if path_balances:
                    balance_data = []
                    for item in path_balances:
                        info = GENE_STYLE.get(item["الجين الغالب"], GENE_STYLE['N'])
                        balance_data.append({
                            "المسار": item["المسار"],
                            "الجين الغالب": f"{info['icon']} {info['name']}",
                            "التفسير الوجودي": info['desc']
                        })
                    st.table(balance_data)

            with tab3:
                st.markdown("### 🌌 هندسة المدارات المتقاطعة")
                nodes = list(set(full_word_pool))
                fig_net = go.Figure()
                for n in nodes:
                    fig_net.add_trace(go.Scatter(x=[random.random()], y=[random.random()], mode='markers+text', text=[n], marker=dict(size=full_word_pool.count(n)*10+20, color='#4fc3f7')))
                fig_net.update_layout(showlegend=False, height=500, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_net, use_container_width=True)

            with tab4:
                st.markdown("### 📜 البيان الوجودي الموحد")
                st.markdown(f"<div class='eloquence-box'>{generate_global_eloquence(dom_root)}</div>", unsafe_allow_html=True)

elif not ENGINES_OK:
    st.warning("⚠️ نظام نبراس في وضع الانتظار: تم اكتشاف خلل في المحركات الرديفة.")
else:
    st.info("📦 بانتظار تحميل قاعدة بيانات الجذور (JSON) لتفعيل المحراب.")

st.sidebar.write("v20.5.3 Herd Balance | خِت فِت.")
