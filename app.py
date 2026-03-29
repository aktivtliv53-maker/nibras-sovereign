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
# 1) الإعدادات والقاموس الدلالي الشامل
# =========================================================
st.set_page_config(page_title="Nibras v16.0 Sovereign Final", page_icon="🌌", layout="wide")

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
    .comparison-card { background: #161616; padding: 20px; border-radius: 15px; border: 1px solid #262626; margin-bottom: 10px; text-align: center; }
    .advisor-box { background:#0a1a0a; padding:25px; border-radius:15px; border-left:5px solid #4CAF50; margin-top:20px; border:1px solid #1a331a; }
    .intent-box { background:#111; padding:25px; border-radius:15px; border-left:5px solid #FFD700; margin-bottom:20px; border:1px solid #333; }
    h1, h2, h3, h4 { color: #4CAF50 !important; text-align: center; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 2) محركات الاستخراج والتحليل (The Core Engines)
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

def analyze_path_v16(text, l_idx, r_idx):
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
# 3) محركات اللوحة الكونية (Cosmic Engines)
# =========================================================

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
                for j in range(i+1, len(roots_in_s)):
                    intra_edges[tuple(sorted([roots_in_s[i], roots_in_s[j]]))] += 2
    
    r_list = list(nodes_g.keys())
    for i in range(len(r_list)):
        for j in range(i+1, len(r_list)):
            if nodes_g[r_list[i]]["orbit"] == nodes_g[r_list[j]]["orbit"]:
                cross_edges[tuple(sorted([r_list[i], r_list[j]]))] += 1.5
    return nodes_g, intra_edges, cross_edges

def analyze_semantics_v16(s_res_list):
    if not s_res_list: return {"dominant_field": "صمت"}
    fields = [SEMANTIC_FIELDS.get(r["root"], "بناء") for s in s_res_list for r in s["analysis"]["matched_roots"]]
    return {"dominant_field": Counter(fields).most_common(1)[0][0] if fields else "بناء"}

def semantic_advisor_v16(nodes, global_sem):
    if not nodes: return {"core": "سكون", "flow": "صمت", "judgment": "نص فارغ", "advice": "أدخل نصاً للتفعيل."}
    core_root = max(nodes.items(), key=lambda x: x[1]["energy"] + x[1]["count"])[0]
    fields = list(set(v["dominant_field"] for v in global_sem.values()))
    advice = f"توازن سيادي عبر حقول {' و '.join(fields)}. "
    if "التمكين" in fields: advice += "المسار يتجه نحو الاستخلاف."
    return {"core": core_root, "flow": " ➔ ".join(fields), "judgment": "ارتقاء دلالي مستقر", "advice": advice}

def deep_intent_engine(nodes, global_sem):
    fields = [v["dominant_field"] for v in global_sem.values()]
    intent = Counter(fields).most_common(1)[0][0] if fields else "بناء"
    return {"intent": intent, "summary": f"النية العميقة للنص تتجه نحو مركزية **{intent}**."}

# =========================================================
# 4) الواجهة السيادية الكبرى (The Absolute UI)
# =========================================================
try:
    l_idx = {normalize_arabic(i["letter"]): i for i in load_json("sovereign_letters_v1.json") if i.get("letter")}
    r_idx = {normalize_arabic(r["root"]): {"root": normalize_arabic(r["root"]), "weight": float(r.get("frequency", 1)), "orbit": r.get("orbit_hint", "بناء")} for r in load_json("quran_roots_complete.json").get("roots", [])}
except: st.error("❌ فشل تحميل القواعد السيادية."); st.stop()

st.title("🛰️ محراب نبراس v16.0 Sovereign Final")

tabs = st.tabs(["🔍 التحليل السيادي المطلق", "🌌 اللوحة الكونية الموحّدة"])

with tabs[0]:
    cols_in = st.columns(3)
    inputs = [cols_in[i].text_area(f"📍 المسار {i+1}", key=f"v_in_{i}", height=150) for i in range(3)]
    run_btn = st.button("🚀 استنطاق الوجود الرقمي الكامل", use_container_width=True)

if run_btn:
    all_s_results = []
    for t in inputs:
        if t.strip():
            sentences = [s.strip() for s in re.sub(r"[\.!\?؛،]", ".", t).split(".") if s.strip()]
            all_s_results.append([{"sentence": s, "analysis": analyze_path_v16(s, l_idx, r_idx)} for s in sentences])
        else: all_s_results.append(None)

    if any(all_s_results):
        # تفعيل المحركات الكبرى
        nodes_g, intra_g, cross_g = build_global_semantic_graph(all_s_results)
        global_sem = {i+1: analyze_semantics_v16(s_list) for i, s_list in enumerate(all_s_results) if s_list}
        adv = semantic_advisor_v16(nodes_g, global_sem)
        intent_res = deep_intent_engine(nodes_g, global_sem)
        gravity_node = max(nodes_g.items(), key=lambda x: x[1]["energy"])[0] if nodes_g else None

        # --- [1] عرض التحليل التفصيلي والطبقات الأربع ---
        with tabs[0]:
            st.divider()
            cols_disp = st.columns(3)
            for i, s_res in enumerate(all_s_results):
                if s_res:
                    with cols_disp[i]:
                        total_en = sum(s["analysis"]["total"] for s in s_res)
                        st.markdown(f"<div class='comparison-card'><h3>مسار {i+1}</h3><h1>{round(total_en, 1)}</h1></div>", unsafe_allow_html=True)
                        
                        with st.expander(f"✨ المحراب الرباعي للمسار {i+1}", expanded=True):
                            # الطبقة 1: شبكة العلاقات
                            st.markdown("#### 🕸️ شبكة العلاقات")
                            roots_p = Counter([r["root"] for s in s_res for r in s["analysis"]["matched_roots"]])
                            if roots_p:
                                fig_net = go.Figure(go.Scatter(x=[random.random() for _ in roots_p], y=[random.random() for _ in roots_p], mode='markers+text', text=list(roots_p.keys()), marker=dict(size=[15 + v*5 for v in roots_p.values()], color='#4CAF50')))
                                fig_net.update_layout(height=200, showlegend=False, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(visible=False), yaxis=dict(visible=False))
                                st.plotly_chart(fig_net, use_container_width=True)
                            
                            # الطبقة 2: طيف الطاقة (Bar Polar)
                            st.markdown("#### 🌀 طيف الطاقة")
                            df_e = pd.DataFrame([{"root": r["root"], "energy": r["weight"], "orbit": r["orbit"]} for s in s_res for r in s["analysis"]["matched_roots"]])
                            if not df_e.empty:
                                fig_e = px.bar_polar(df_e, r="energy", theta="root", color="orbit", template="plotly_dark")
                                fig_e.update_layout(height=250, showlegend=False, margin=dict(l=20,r=20,t=20,b=20))
                                st.plotly_chart(fig_e, use_container_width=True)
                            
                            # الطبقة 3: الانحراف (Line Chart)
                            st.markdown("#### ⏳ الانحراف")
                            df_d = pd.DataFrame([{"index": idx+1, "orbit": s["analysis"]["orbit"]} for idx, s in enumerate(s_res)])
                            fig_d = px.line(df_d, x="index", y="orbit", markers=True, height=200)
                            fig_d.update_layout(margin=dict(l=0,r=0,t=0,b=0))
                            st.plotly_chart(fig_d, use_container_width=True)
                            
                            # الطبقة 4: المعنى (المجال)
                            st.markdown(f"🧠 **المجال المهيمن:** {global_sem[i+1]['dominant_field']}")

            # المستشار السيادي الكامل
            st.markdown(f"<div class='advisor-box'><h3>🧭 المستشار v16.0 Sovereign</h3><p><b>🔹 المحور المركزي:</b> {adv['core']}</p><p><b>🔹 اتجاه التدفق:</b> {adv['flow']}</p><p><b>🔹 التوصية:</b> {adv['advice']}</p></div>", unsafe_allow_html=True)

        # --- [2] عرض اللوحة الكونية الموحدة (Cosmic Canvas) ---
        with tabs[1]:
            st.markdown(f"<div class='intent-box'><h3>🔮 النية العميقة (Deep Intent)</h3><p><b>النية:</b> {intent_res['intent']}</p><p>{intent_res['summary']}</p></div>", unsafe_allow_html=True)
            
            st.markdown("### 🌌 الخريطة الكونية الهجينة (Unified Canvas)")
            if nodes_g:
                fig_g = go.Figure()
                pos_g = {n: (random.random(), random.random()) for n in nodes_g}
                
                # خطوط التدفق
                for (a, b), w in {**intra_g, **cross_g}.items():
                    fig_g.add_trace(go.Scatter(x=[pos_g[a][0], pos_g[b][0]], y=[pos_g[a][1], pos_g[b][1]], mode="lines", line=dict(width=w/2, color="#222"), hoverinfo="none"))
                
                # العقد وموجات الطاقة
                for n, info in nodes_g.items():
                    # موجة الطاقة
                    fig_g.add_shape(type="circle", xref="x", yref="y", x0=pos_g[n][0]-0.02, y0=pos_g[n][1]-0.02, x1=pos_g[n][0]+0.02, y1=pos_g[n][1]+0.02, line=dict(color="#4CAF50", width=0.5, dash="dot"))
                    # العقدة
                    fig_g.add_trace(go.Scatter(x=[pos_g[n][0]], y=[pos_g[n][1]], mode="markers+text", text=[n], marker=dict(size=20+info["count"]*7, color="#4CAF50" if n != gravity_node else "#FFD700", line=dict(width=2, color="#000")), textposition="top center"))
                
                # مركز الثقل
                if gravity_node:
                    fig_g.add_trace(go.Scatter(x=[pos_g[gravity_node][0]], y=[pos_g[gravity_node][1]], mode="markers", marker=dict(size=50, color="#FFD700", opacity=0.2), hoverinfo="none"))

                fig_g.update_layout(height=700, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(visible=False), yaxis=dict(visible=False), showlegend=False)
                st.plotly_chart(fig_g, use_container_width=True)

st.sidebar.write("v16.0 Final Sovereign | خِت فِت.")
