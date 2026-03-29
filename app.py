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

# --- استدعاء طبقات الإدراك الجديدة (تأكد من وجود الملفات الـ 5 في المجلد) ---
try:
    from letter_engine import analyze_word_letters
    from orbit_polarity import get_orbit_meta
    from state_engine import detect_state
    from tone_engine import purify_text
    from swedish_layer import translate_meta
except ImportError:
    st.error("⚠️ ملفات المحركات المساعدة غير موجودة. تأكد من رفع letter_engine.py والبقية.")

# =========================================================
# 1) التهيئة والقاموس الوجودي (The Sovereign Core) - لا مساس
# =========================================================
st.set_page_config(page_title="Nibras v20.1 Eloquence Sovereign", page_icon="🎙️", layout="wide")

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

ARCHE_COLORS = {"الرحمة": "#4fc3f7", "القوة": "#ff5252", "الهداية": "#4CAF50", "العدل": "#FFD700", "النور": "#bb86fc"}

st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background-color: #030305; color: #e0e0e0; }
    .eloquence-box { 
        background: linear-gradient(145deg, #0a150a, #020202); 
        padding: 30px; border-radius: 20px; border: 1px solid #1e3a1e; 
        border-right: 5px solid #4CAF50; line-height: 1.8; font-size: 1.1em;
    }
    .ultra-card { background: #0a0a0f; padding: 25px; border-radius: 15px; border: 1px solid #1a1a2a; border-top: 4px solid #4fc3f7; margin-bottom: 20px; }
    .sovereign-tag { color: #4fc3f7; font-weight: bold; border-bottom: 1px solid #1e3a1e; padding-bottom: 5px; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 2) محرك البيان الوجودي (Eloquence Engine v18) - لا مساس
# =========================================================
def collect_global_semantics(all_res, semantic_fields, res_map, gravity, cross_g):
    paths_fields = []
    for s_list in all_res:
        if not s_list:
            paths_fields.append("صمت")
            continue
        roots_in_p = [r["root"] for s in s_list for r in s["analysis"]["roots"]]
        fields = [semantic_fields.get(r, "بناء") for r in roots_in_p]
        dom_field = Counter(fields).most_common(1)[0][0] if fields else "بناء"
        paths_fields.append(dom_field)
    
    global_field_dist = Counter(paths_fields)
    dom_root = max(res_map.items(), key=lambda x: x[1])[0] if res_map else "صمت"
    
    return {
        "paths_fields": paths_fields,
        "global_field_dist": global_field_dist,
        "dom_root": dom_root,
        "dom_res": res_map.get(dom_root, 0),
        "dom_grav": gravity.get(dom_root, {}).get("force", 0),
        "cross_edges": cross_g
    }

def collective_eloquence(global_info, semantic_fields, q_archetypes, universal_archetypes):
    p_fields = global_info["paths_fields"]
    g_dist = global_info["global_field_dist"]
    dom_root = global_info["dom_root"]
    cross_edges = global_info["cross_edges"]
    
    dom_global_field = g_dist.most_common(1)[0][0] if g_dist else "بناء"
    u_arc = universal_archetypes.get(q_archetypes.get(dom_root, "بناء"), "The Architect")
    
    txt_paths = " | ".join([f"المسار {i+1}: {f}" for i, f in enumerate(p_fields)])
    
    # صياغة البيان السيادي (تطبيق فلتر اليسر)
    field_stmt = f"تم رصد توزيع الحقول الدلالية كالآتي: ({txt_paths}). والمجال الغالب الذي يوحد هذه الترددات هو مجال **{dom_global_field}**."
    root_stmt = f"المحور الدلالي المركزي الذي يحني نسيج النص هو الجذر **'{dom_root}'**، برنين كوني مقداره {round(global_info['dom_res'], 1)}."
    arche_stmt = f"النمط الوجودي الحاكم هو **{u_arc}**."
    
    # طبقة التحديث v20: إضافة لبث/مكث والسويدية للبيان العام
    state = detect_state([dom_root])
    sv_summary = translate_meta(dom_global_field, state)
    
    final_text = f"""
    <div class='sovereign-tag'>🇸🇪 {sv_summary}</div>
    {purify_text(field_stmt)}<br><br>
    {purify_text(root_stmt)}<br><br>
    {arche_stmt}<br><br>
    <b>الحالة السيادية المسيطرة:</b> {state}<br><br>
    <b>الخلاصة:</b> شبكة واحدة تتحرك في مدار الـ '{dom_global_field}' تحت سيادة النمط '{u_arc}'.
    """
    return final_text

# =========================================================
# 3) محركات التحليل الهيكلي (Data Processing) - لا مساس
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
    for p in ["وال", "فال", "بال", "ال", "و", "ف", "ب", "ل"]:
        if w.startswith(p) and len(w)-len(p)>=2: w = w[len(p):]; break
    if w in root_index: return w, root_index[w]
    if len(w)>=3 and w[:3] in root_index: return w[:3], root_index[w[:3]]
    return None, None

# =========================================================
# 4) الواجهة والتشغيل (Execution) - التطعيم v20.1
# =========================================================
letters_data = load_data("sovereign_letters_v1.json")
roots_data = load_data("quran_roots_complete.json")

if letters_data and roots_data:
    l_idx = {normalize_arabic(i["letter"]): i for i in letters_data if "letter" in i}
    r_idx = {normalize_arabic(r["root"]): {"weight": float(r.get("frequency", 1)), "orbit": r.get("orbit_hint", "بناء")} for r in roots_data.get("roots", [])}

    st.title("🎙️ محراب نبراس v20.1 - السيادة الهندسية")
    
    tab1, tab2, tab3 = st.tabs(["🔍 المحراب والتحليل", "🌌 اللوحة الكونية", "📝 البيان الوجودي الموحد"])

    with tab1:
        c1, c2, c3 = st.columns(3)
        p1 = c1.text_area("📍 المسار 1", height=120, key="txt_p1")
        p2 = c2.text_area("📍 المسار 2", height=120, key="txt_p2")
        p3 = c3.text_area("📍 المسار 3", height=120, key="txt_p3")
        run = st.button("🚀 استنطاق البيان السيادي", use_container_width=True)

    if run:
        all_res = []
        for idx, inp in enumerate([p1, p2, p3]):
            if inp.strip():
                sents = [s.strip() for s in re.split(r'[.!?؛،]', inp) if s.strip()]
                all_res.append([{"sentence": s, "analysis": {
                    "energy": sum(match_root(w, r_idx)[1]["weight"] for w in normalize_arabic(s).split() if match_root(w, r_idx)[0]),
                    "roots": [{"root": match_root(w, r_idx)[0], "orbit": match_root(w, r_idx)[1]["orbit"], "weight": match_root(w, r_idx)[1]["weight"]} for w in normalize_arabic(s).split() if match_root(w, r_idx)[0]]
                }} for s in sents])
            else: all_res.append(None)

        if any(all_res):
            nodes_g, intra_g, cross_g = {}, Counter(), Counter()
            for idx, s_list in enumerate(all_res):
                if not s_list: continue
                for s in s_list:
                    r_list = [r["root"] for r in s["analysis"]["roots"]]
                    for r_info in s["analysis"]["roots"]:
                        r = r_info["root"]
                        nodes_g[r] = nodes_g.get(r, {"orbit": r_info["orbit"], "energy": r_info["weight"], "paths": set(), "count": 0})
                        nodes_g[r]["paths"].add(idx+1); nodes_g[r]["count"] += 1
            
            res_map = {r: (len(info["paths"]) * info["energy"]) for r, info in nodes_g.items()}
            gravity = {r: {"force": (info["energy"] * res_map[r]) / info["count"], "radius": np.log1p(info["energy"]*res_map[r])*0.05} for r, info in nodes_g.items()}
            
            # --- توليد البيان الوجودي الموحد ---
            global_info = collect_global_semantics(all_res, SEMANTIC_FIELDS, res_map, gravity, cross_g)
            collective_text = collective_eloquence(global_info, SEMANTIC_FIELDS, Q_ARCHETYPES, UNIVERSAL_ARCHETYPES)

            with tab1:
                st.divider()
                cols = st.columns(3)
                for i, s_list in enumerate(all_res):
                    if s_list:
                        with cols[i]:
                            total_e = sum(s["analysis"]["energy"] for s in s_list)
                            st.markdown(f"<div class='ultra-card'><h3>مسار {i+1}</h3><h1>{round(total_e, 1)}</h1></div>", unsafe_allow_html=True)
                            
                            # إضافة الهندسة الحرفية لكل مسار (التحديث v20)
                            roots_in_p = [r["root"] for s in s_list for r in s["analysis"]["roots"]]
                            if roots_in_p:
                                char_analysis = analyze_word_letters(roots_in_p[0])
                                if char_analysis:
                                    st.caption(f"🧬 المحرك الحرفي: {char_analysis['dominant_vector']}")

            with tab3:
                st.markdown("### 🧬 البيان الوجودي الموحد (النسخة السيادية)")
                st.markdown(f"<div class='eloquence-box'>{collective_text}</div>", unsafe_allow_html=True)
                
            with tab2:
                # اللوحة الكونية - لا مساس
                fig = go.Figure()
                pos = {n: (random.random(), random.random()) for n in nodes_g}
                for n, info in nodes_g.items():
                    q = Q_ARCHETYPES.get(n, "بناء"); u = UNIVERSAL_ARCHETYPES.get(q, "The Architect")
                    fig.add_trace(go.Scatter(x=[pos[n][0]], y=[pos[n][1]], mode="markers+text", text=[f"<b>{n}</b><br>{u}"], marker=dict(size=25+(info['count']*10), color=ARCHE_COLORS.get(q, "#4CAF50"))))
                fig.update_layout(height=600, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False)
                st.plotly_chart(fig, use_container_width=True, key="cosmic_v20")

st.sidebar.write("v20.1 Eloquence Sovereign | خِت فِت.")
