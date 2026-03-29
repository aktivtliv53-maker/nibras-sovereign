import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import re
import random

# =========================================================
# 0) محرك التحميل والبيانات (Data Core)
# =========================================================
try:
    from core_paths import load_json
except ImportError:
    st.error("❌ ملف core_paths.py مفقود!"); st.stop()

# =========================================================
# 1) الإعدادات والقاموس الدلالي v16.0
# =========================================================
st.set_page_config(page_title="Nibras v16.0 Cosmic Canvas", page_icon="🌌", layout="wide")

SEMANTIC_FIELDS = {
    "امن": "الإيمان", "صدق": "الإيمان", "كفر": "الضلال", "فسد": "الفساد",
    "صلح": "الإصلاح", "هدى": "الهداية", "ضل": "الضلال", "رحم": "الرحمة",
    "غفر": "الرحمة", "قتل": "الصراع", "قاتل": "الصراع", "نصر": "القوة",
    "ملك": "القوة", "نور": "النور", "ظلم": "الظلام", "عدل": "العدل",
    "عمل": "العمل", "قول": "البيان", "ذكر": "الذكر", "بشر": "البشارة",
    "نذر": "التحذير", "يسر": "اليسر", "عسر": "الشدة", "غني": "الغنى", "خلف": "التمكين"
}

st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background-color: #0a0a0a; color: #e0e0e0; }
    .comparison-card { background: #161616; padding: 15px; border-radius: 15px; border: 1px solid #262626; margin-bottom: 10px; text-align: center; }
    .advisor-box { background:#0a1a0a; padding:20px; border-radius:15px; border-left:5px solid #4CAF50; margin-top:20px; border:1px solid #1a331a; }
    .intent-box { background:#111; padding:20px; border-radius:15px; border-left:5px solid #FFD700; margin-bottom:20px; border:1px solid #333; }
    h1, h2, h3, h4 { color: #4CAF50 !important; text-align: center; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 2) المحركات المركزية (v15.1 Core Engines)
# =========================================================

def normalize_arabic(text):
    if not text: return ""
    text = re.sub(r'[\u0617-\u061A\u064B-\u0652\u0670]', '', text)
    replacements = {"أ": "ا", "إ": "ا", "آ": "ا", "ة": "ه", "ى": "ي", "ؤ": "و", "ئ": "ي"}
    for k, v in replacements.items(): text = text.replace(k, v)
    return re.sub(r'\s+', ' ', re.sub(r'[^\u0621-\u064A\s]', ' ', text)).strip()

def deep_morpho_extract(word):
    w = normalize_arabic(word)
    w = re.sub(r"^(وال|فال|بال|ال|يست|يت|تست|نست|است|لل|ب|و|ف|ي|ت|ن|ا)", "", w)
    w = re.sub(r"(كم|هم|نا|ها|وا|ون|ين|ات|كما|هما|ه|ي|ت|تم)$", "", w)
    return w if len(w) <= 3 else w[:3]

def match_sovereign_root(word, root_index):
    word_norm = normalize_arabic(word)
    prefixes = ["وال", "فال", "بال", "ال", "و", "ف", "ب", "ل"]
    candidates = {word_norm}
    for p in prefixes:
        if word_norm.startswith(p) and len(word_norm)-len(p)>=2: candidates.add(word_norm[len(p):])
    for c in list(candidates):
        if c in root_index: return c, root_index[c]
        if len(c)>=3 and c[:3] in root_index: return c[:3], root_index[c[:3]]
    est = deep_morpho_extract(word_norm)
    if est in root_index: return est, root_index[est]
    return None, None

def analyze_path_v15_1(text, l_idx, r_idx):
    norm = normalize_arabic(text)
    res = {"mass": 0.0, "speed": 0.0, "energy": 0.0, "orbit": "بناء", "matched_roots": [], "orbit_counter": Counter()}
    for char in norm.replace(" ", ""):
        m = l_idx.get(char)
        if m: res["mass"] += float(m.get("mass", 0)); res["speed"] += float(m.get("speed", 0))
    for word in norm.split():
        m_root, entry = match_sovereign_root(word, r_idx)
        if m_root:
            res["energy"] += entry["weight"]
            res["orbit_counter"][entry["orbit"]] += entry["weight"]
            res["matched_roots"].append({"word": word, "root": m_root, "orbit": entry["orbit"], "weight": entry["weight"]})
    if res["orbit_counter"]: res["orbit"] = res["orbit_counter"].most_common(1)[0][0]
    res["total"] = round(res["mass"] + res["speed"] + res["energy"], 2)
    return res

# =========================================================
# 3) محركات السيادة (Intent v15.2 & Cosmic v16.0)
# =========================================================

def deep_intent_engine(nodes, global_sem):
    if not nodes: return {"intent": "نية غير مرصودة", "vector": [], "summary": "لا يوجد نص كافٍ."}
    fields = [v["dominant_field"] for v in global_sem.values()]
    intent = Counter(fields).most_common(1)[0][0] if fields else "بناء"
    vector = sorted(global_sem.keys())
    summary = f"النية العميقة للنص تتجه نحو: **{intent}** عبر مسار يبدأ من المسار {vector[0]} وينتهي في المسار {vector[-1]}."
    return {"intent": intent, "vector": vector, "summary": summary}

def cosmic_field(nodes):
    if not nodes: return {"gravity": None, "field_map": None}
    gravity = max(nodes.items(), key=lambda x: x[1]["energy"] + x[1]["count"])[0]
    field_map = Counter([n["orbit"] for n in nodes.values()])
    return {"gravity": gravity, "field_map": field_map}

def build_global_semantic_graph(all_s_results):
    nodes_g, intra_edges, cross_edges = {}, Counter(), Counter()
    for p_idx, s_list in enumerate(all_s_results):
        if not s_list: continue
        for s_res in s_list:
            analysis = s_res["analysis"]
            roots_in_s = [r["root"] for r in analysis["matched_roots"]]
            for r_info in analysis["matched_roots"]:
                r = r_info["root"]
                if r not in nodes_g:
                    nodes_g[r] = {"orbit": r_info["orbit"], "energy": r_info["weight"], "paths": {p_idx+1}, "count": 1}
                else:
                    nodes_g[r]["paths"].add(p_idx+1); nodes_g[r]["count"] += 1
            for i in range(len(roots_in_s)):
                for j in range(i + 1, len(roots_in_s)):
                    intra_edges[tuple(sorted([roots_in_s[i], roots_in_s[j]]))] += 2
    r_list = list(nodes_g.keys())
    for i in range(len(r_list)):
        for j in range(i+1, len(r_list)):
            if nodes_g[r_list[i]]["orbit"] == nodes_g[r_list[j]]["orbit"]:
                cross_edges[tuple(sorted([r_list[i], r_list[j]]))] += 1.5
    return nodes_g, intra_edges, cross_edges

def analyze_semantics_v14(s_res_list):
    fields = [SEMANTIC_FIELDS.get(r["root"], "بناء") for s in s_res_list for r in s["analysis"]["matched_roots"]]
    return {"dominant_field": Counter(fields).most_common(1)[0][0] if fields else "غير مصنف"}

def semantic_advisor_v151(nodes, global_semantics):
    if not nodes: return {"core": "صمت", "flow": "سكون", "judgment": "نص ساكن", "advice": "أدخل نصاً."}
    core_root = max(nodes.items(), key=lambda x: x[1]["count"] + len(x[1]["paths"]) * 5)[0]
    p_present = sorted(list(set().union(*(n["paths"] for n in nodes.values()))))
    unique_fields = list(set(v["dominant_field"] for v in global_semantics.values()))
    return {"core": core_root, "flow": " → ".join([f"المسار {p}" for p in p_present]), "judgment": "ارتقاء من " + " و ".join(unique_fields), "advice": "توازن سيادي مستقر."}

# =========================================================
# 4) واجهة التطبيق والتحكم (The Sovereign UI)
# =========================================================
try:
    l_idx = {normalize_arabic(i["letter"]): i for i in load_json("sovereign_letters_v1.json") if i.get("letter")}
    r_idx = {normalize_arabic(r["root"]): {"root": normalize_arabic(r["root"]), "weight": float(r.get("frequency", 1)), "orbit": r.get("orbit_hint", "بناء")} for r in load_json("quran_roots_complete.json").get("roots", [])}
except: st.error("❌ فشل تحميل القواعد السيادية."); st.stop()

st.title("🛰️ محراب نبراس v16.0 Unified Cosmic Canvas")

# 1) إدخال النصوص (قبل الزر)
cols_in = st.columns(3)
inputs = [cols_in[i].text_area(f"📍 المسار {i+1}", key=f"v{i}") for i in range(3)]

# 2) زر التشغيل
if st.button("🚀 استنطاق الوجود الرقمي", use_container_width=True):
    all_s_results = []
    for t in inputs:
        if t.strip():
            sentences = [s.strip() for s in re.sub(r"[\.!\?؛،]", ".", t).split(".") if s.strip()]
            all_s_results.append([{"sentence": s, "analysis": analyze_path_v15_1(s, l_idx, r_idx)} for s in sentences])
        else: all_s_results.append(None)
    
    if any(all_s_results):
        # [أ] التحليل والمحركات
        nodes_g, intra_g, cross_g = build_global_semantic_graph(all_s_results)
        global_sem = {i+1: analyze_semantics_v14(s_list) for i, s_list in enumerate(all_s_results) if s_list}
        adv = semantic_advisor_v151(nodes_g, global_sem)
        intent = deep_intent_engine(nodes_g, global_sem)
        field = cosmic_field(nodes_g)

        # [ب] إنشاء التبويبات بعد توفر البيانات
        tabs = st.tabs(["🔍 التحليل السيادي", "🌌 اللوحة الكونية الموحّدة"])

        with tabs[0]:
            cols_disp = st.columns(3)
            for i, s_res in enumerate(all_s_results):
                if s_res:
                    with cols_disp[i]:
                        st.markdown(f"<div class='comparison-card'><h3>مسار {i+1}</h3><h1>{round(sum(s['analysis']['total'] for s in s_res),1)}</h1></div>", unsafe_allow_html=True)
                        with st.expander(f"✨ المحراب الرباعي {i+1}", expanded=True):
                            # (الطبقات الأربع)
                            st.markdown("#### 🕸️ شبكة العلاقات")
                            roots_p = Counter([r["root"] for s in s_res for r in s["analysis"]["matched_roots"]])
                            if roots_p:
                                fig_p = go.Figure()
                                pos_p = {r: (random.random(), random.random()) for r in roots_p}
                                fig_p.add_trace(go.Scatter(x=[pos_p[r][0] for r in roots_p], y=[pos_p[r][1] for r in roots_p], mode='markers+text', text=list(roots_p.keys()), marker=dict(size=[15 + v*5 for v in roots_p.values()], color='#4CAF50'), textposition="top center"))
                                fig_p.update_layout(height=200, showlegend=False, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(showgrid=False, showticklabels=False), yaxis=dict(showgrid=False, showticklabels=False))
                                st.plotly_chart(fig_p, use_container_width=True)
                            
                            st.markdown(f"🧠 المجال المهيمن: **{analyze_semantics_v14(s_res)['dominant_field']}**")
            
            st.markdown(f"<div class='advisor-box'><h3>🧭 المستشار v15.1</h3><p><b>🔹 المحور:</b> {adv['core']} | <b>🔹 التدفق:</b> {adv['flow']}</p><p><b>🔹 الحكم:</b> {adv['judgment']}</p></div>", unsafe_allow_html=True)

        with tabs[1]:
            # عرض النية العميقة v15.2
            st.markdown(f"<div class='intent-box'><h3>🔮 النية العميقة (Deep Intent)</h3><p><b>النية المحركة:</b> {intent['intent']}</p><p>{intent['summary']}</p></div>", unsafe_allow_html=True)
            
            # اللوحة الكونية الهجينة v16.0
            st.markdown("### 🌌 الخريطة الكونية الهجينة (Hybrid Cosmic Map)")
            fig_g = go.Figure()
            pos_g = {n: (random.random(), random.random()) for n in nodes_g}
            
            # خطوط التدفق والربط
            for (a, b), w in {**intra_g, **cross_g}.items():
                fig_g.add_trace(go.Scatter(x=[pos_g[a][0], pos_g[b][0]], y=[pos_g[a][1], pos_g[b][1]], mode="lines", line=dict(width=w/2, color="#222"), hoverinfo="none"))
            
            # العقد وموجات الطاقة
            for n, info in nodes_g.items():
                # موجة الطاقة
                fig_g.add_shape(type="circle", xref="x", yref="y", x0=pos_g[n][0]-info["energy"]*0.015, y0=pos_g[n][1]-info["energy"]*0.015, x1=pos_g[n][0]+info["energy"]*0.015, y1=pos_g[n][1]+info["energy"]*0.015, line=dict(color="#4CAF50", width=1, dash="dot"))
                # العقدة السيادية
                fig_g.add_trace(go.Scatter(x=[pos_g[n][0]], y=[pos_g[n][1]], mode="markers+text", text=[n], marker=dict(size=20+info["count"]*6, color="#4CAF50" if n != field["gravity"] else "#FFD700", line=dict(width=2, color="#000")), textposition="top center"))
            
            # هالة مركز الثقل
            g = field["gravity"]
            if g:
                fig_g.add_trace(go.Scatter(x=[pos_g[g][0]], y=[pos_g[g][1]], mode="markers", marker=dict(size=50, color="#FFD700", opacity=0.2), hoverinfo="none"))

            fig_g.update_layout(height=650, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(showgrid=False, zeroline=False, showticklabels=False), yaxis=dict(showgrid=False, zeroline=False, showticklabels=False), showlegend=False)
            st.plotly_chart(fig_g, use_container_width=True)

st.sidebar.write("v16.0 Final | خِت فِت.")
