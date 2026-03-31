import streamlit as st
import json
import os
import re
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from collections import Counter

# =========================================================
# Nibras Sovereign v27.2.0 — Sovereign Text Ingestion
# =========================================================

st.set_page_config(layout="wide", page_title="Nibras Sovereign v27.2.0")

# ---------------------------------------------------------
# 1) الثوابت السيادية
# ---------------------------------------------------------
GENE_STYLE = {
    "A": {"icon": "🐪", "label": "التأسيس", "meaning": "اليسر والفتح المداري"},
    "G": {"icon": "🐮", "label": "التمكين الصبور", "meaning": "الخير والتأسيس الراسخ"},
    "T": {"icon": "🐏", "label": "السكينة", "meaning": "السكينة والمقام الآمن"},
    "C": {"icon": "🐐", "label": "الوعي الفوقي", "meaning": "السمو والتمكين الصاعد"},
}

DEFAULT_ORBIT_ORDER = [
    "الأزل (Sovereign Origin)",
    "الأمر (Command)",
    "الخلق (Creation)",
    "الإنسان (Human)",
    "الامتحان (Trial)",
    "المصير (Destiny)",
    "الوعي (Consciousness)",
]

ARABIC_DIACRITICS_PATTERN = re.compile(r'[\u0617-\u061A\u064B-\u0652\u0670\u06D6-\u06ED]')
NON_ARABIC_KEEP_SPACES_PATTERN = re.compile(r'[^\u0621-\u063A\u0641-\u064A\s]')

# ---------------------------------------------------------
# 2) أدوات مساعدة
# ---------------------------------------------------------
def safe_text(val, fallback=""):
    if val is None:
        return fallback
    return str(val).strip()

def safe_float(val, fallback=0.0):
    try:
        return float(val)
    except Exception:
        return fallback

def assign_gene(weight: float):
    if weight >= 1.90:
        return "A"
    elif weight >= 1.85:
        return "G"
    elif weight >= 1.80:
        return "T"
    else:
        return "C"

def classify_weight(weight: float):
    if weight >= 1.95:
        return "🔝 هيمنة عليا"
    elif weight >= 1.90:
        return "🔥 حضور قوي جداً"
    elif weight >= 1.85:
        return "✨ حضور قوي"
    elif weight >= 1.80:
        return "⚡ حضور راجح"
    else:
        return "🌱 حضور تأسيسي"

def get_orbit_index(orbit_name: str):
    if orbit_name in DEFAULT_ORBIT_ORDER:
        return DEFAULT_ORBIT_ORDER.index(orbit_name) + 1
    return len(DEFAULT_ORBIT_ORDER) + 1

def normalize_arabic(text: str):
    """
    تنظيف النص العربي:
    - إزالة التشكيل
    - توحيد الألف
    - توحيد الياء/الألف المقصورة
    - إزالة الرموز غير العربية
    """
    if not text:
        return ""

    text = ARABIC_DIACRITICS_PATTERN.sub('', text)
    text = text.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا")
    text = text.replace("ى", "ي")
    text = text.replace("ة", "ه")  # تبسيط أولي
    text = NON_ARABIC_KEEP_SPACES_PATTERN.sub(' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def tokenize_arabic(text: str):
    text = normalize_arabic(text)
    if not text:
        return []
    return [w.strip() for w in text.split() if w.strip()]

def build_prefix_index(root_names):
    """
    فهرس حسب أول 3 أحرف لتسريع المطابقة الجزئية.
    """
    prefix_map = {}
    for name in root_names:
        key = name[:3] if len(name) >= 3 else name
        prefix_map.setdefault(key, []).append(name)
    return prefix_map

def match_root_logic(word, root_index, prefix_index):
    """
    طبقة مطابقة أولية:
    1) مطابقة مباشرة
    2) إزالة 'ال'
    3) إزالة بعض اللواصق البسيطة
    4) مطابقة أول 3 أحرف إن وجدت بشكل مباشر
    """
    candidates = []

    # 1) الكلمة نفسها
    candidates.append(word)

    # 2) إزالة ال التعريف
    if word.startswith("ال") and len(word) > 3:
        candidates.append(word[2:])

    # 3) إزالة لواصق بسيطة جداً
    simple_prefixes = ["و", "ف", "ب", "ك", "ل", "س"]
    for p in simple_prefixes:
        if word.startswith(p) and len(word) > 3:
            candidates.append(word[1:])

    # 4) إزالة لاصق + ال
    for p in simple_prefixes:
        if word.startswith(p + "ال") and len(word) > 4:
            candidates.append(word[3:])

    # إزالة التكرار مع الحفاظ على الترتيب
    seen = set()
    unique_candidates = []
    for c in candidates:
        if c not in seen:
            seen.add(c)
            unique_candidates.append(c)

    # أ) مطابقة مباشرة
    for c in unique_candidates:
        if c in root_index:
            return c, "direct"

    # ب) مطابقة prefix exact against root names
    for c in unique_candidates:
        if len(c) >= 3:
            pref = c[:3]
            # إذا كان أول 3 أحرف نفسها جذرًا موجودًا
            if pref in root_index:
                return pref, "prefix_root"

            # أو إذا وجد مرشح واحد واضح في فهرس البادئة
            pref_candidates = prefix_index.get(pref, [])
            if len(pref_candidates) == 1:
                return pref_candidates[0], "prefix_unique"

    return None, "unmatched"

def summarize_path(path_roots):
    if not path_roots:
        return None

    path_df = pd.DataFrame(path_roots)

    total = len(path_df)
    avg_weight = path_df["weight"].mean()
    max_idx = path_df["weight"].idxmax()
    top_root = path_df.loc[max_idx, "name"]
    top_weight = path_df.loc[max_idx, "weight"]

    orbit_mode = path_df["orbit"].mode()
    dominant_orbit = orbit_mode.iloc[0] if not orbit_mode.empty else "غير محدد"

    gene_mode = path_df["gene"].mode()
    dominant_gene = gene_mode.iloc[0] if not gene_mode.empty else "C"
    gene_style = GENE_STYLE.get(dominant_gene, GENE_STYLE["C"])

    orbit_counts = Counter(path_df["orbit"])
    gene_counts = Counter(path_df["gene"])

    verdict = (
        f"الخلاصة السيادية الناطقة: "
        f"المسار الحالي يتكون من {total} جذراً، "
        f"ومتوسط الثقل فيه {avg_weight:.2f}. "
        f"الجذر القائد هو ({top_root}) بوزن {top_weight:.2f}. "
        f"المدار الغالب هو ({dominant_orbit})، "
        f"والجين الغالب هو {gene_style['icon']} {dominant_gene} — {gene_style['meaning']}."
    )

    return {
        "total": total,
        "avg_weight": avg_weight,
        "top_root": top_root,
        "top_weight": top_weight,
        "dominant_orbit": dominant_orbit,
        "dominant_gene": dominant_gene,
        "dominant_gene_style": gene_style,
        "orbit_counts": dict(orbit_counts),
        "gene_counts": dict(gene_counts),
        "verdict": verdict,
    }

def summarize_text_analysis(matched_roots):
    """
    خلاصة النص المُدخل بعد استخراج الجذور المطابقة.
    """
    if not matched_roots:
        return None

    df = pd.DataFrame(matched_roots)

    total = len(df)
    unique_count = df["name"].nunique()
    avg_weight = df["weight"].mean()

    max_idx = df["weight"].idxmax()
    top_root = df.loc[max_idx, "name"]
    top_weight = df.loc[max_idx, "weight"]

    orbit_mode = df["orbit"].mode()
    dominant_orbit = orbit_mode.iloc[0] if not orbit_mode.empty else "غير محدد"

    gene_mode = df["gene"].mode()
    dominant_gene = gene_mode.iloc[0] if not gene_mode.empty else "C"
    gene_style = GENE_STYLE.get(dominant_gene, GENE_STYLE["C"])

    orbit_counts = Counter(df["orbit"])
    gene_counts = Counter(df["gene"])

    verdict = (
        f"الخلاصة السيادية الناطقة للنص: "
        f"تم استنطاق {total} جذراً مطابقاً ({unique_count} فريداً). "
        f"متوسط الثقل {avg_weight:.2f}. "
        f"الجذر المهيمن الآن هو ({top_root}) بوزن {top_weight:.2f}. "
        f"المدار الغالب هو ({dominant_orbit})، "
        f"والجين الغالب هو {gene_style['icon']} {dominant_gene} — {gene_style['meaning']}."
    )

    return {
        "total": total,
        "unique_count": unique_count,
        "avg_weight": avg_weight,
        "top_root": top_root,
        "top_weight": top_weight,
        "dominant_orbit": dominant_orbit,
        "dominant_gene": dominant_gene,
        "dominant_gene_style": gene_style,
        "orbit_counts": dict(orbit_counts),
        "gene_counts": dict(gene_counts),
        "verdict": verdict,
    }

# ---------------------------------------------------------
# 3) تحميل البيانات + التحقق + الإثراء
# ---------------------------------------------------------
@st.cache_data
def hunt_nibras_core():
    base_path = os.path.dirname(__file__)
    file_path = os.path.join(base_path, "data", "nibras_lexicon.json")

    if not os.path.exists(file_path):
        return {
            "ok": False,
            "error": "⚠️ المدار غير مراقب: ملف الجذور مفقود في المسار الأساسي.",
            "roots": [],
            "root_index": {},
            "prefix_index": {},
            "stats": {},
        }

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        return {
            "ok": False,
            "error": f"⚠️ تعذر قراءة ملف الجذور: {e}",
            "roots": [],
            "root_index": {},
            "prefix_index": {},
            "stats": {},
        }

    if not isinstance(data, list):
        return {
            "ok": False,
            "error": "⚠️ بنية الملف غير صحيحة: يجب أن يكون JSON قائمة مدارات.",
            "roots": [],
            "root_index": {},
            "prefix_index": {},
            "stats": {},
        }

    all_roots_raw = []
    invalid_count = 0
    missing_insight_count = 0

    for orbit_data in data:
        orbit_name = safe_text(orbit_data.get("orbit"), "مدار غير مصنف")
        roots_list = orbit_data.get("roots", [])

        if not isinstance(roots_list, list):
            continue

        for root in roots_list:
            if not isinstance(root, dict):
                invalid_count += 1
                continue

            name = safe_text(root.get("name"))
            if not name:
                invalid_count += 1
                continue

            weight = safe_float(root.get("weight"), 0.0)
            insight = safe_text(root.get("insight"))

            if not insight:
                missing_insight_count += 1
                insight = f"⚠️ الجذر ({name}) موجود لكن لا يحمل بصيرة مفسّرة داخل القاعدة الحالية."

            gene = assign_gene(weight)
            gene_style = GENE_STYLE[gene]

            enriched_root = {
                "name": name,
                "weight": weight,
                "insight": insight,
                "orbit": orbit_name,
                "orbit_index": get_orbit_index(orbit_name),
                "gene": gene,
                "gene_icon": gene_style["icon"],
                "gene_label": gene_style["label"],
                "gene_meaning": gene_style["meaning"],
                "weight_class": classify_weight(weight),
            }

            all_roots_raw.append(enriched_root)

    # إزالة التكرار
    dedup_map = {}
    duplicate_count = 0

    for root in all_roots_raw:
        name = root["name"]
        if name in dedup_map:
            duplicate_count += 1
            if root["weight"] > dedup_map[name]["weight"]:
                dedup_map[name] = root
        else:
            dedup_map[name] = root

    all_roots = list(dedup_map.values())
    all_roots.sort(key=lambda r: (r["orbit_index"], -r["weight"], r["name"]))

    root_index = {r["name"]: r for r in all_roots}
    prefix_index = build_prefix_index(root_index.keys())

    stats = {
        "loaded_raw": len(all_roots_raw),
        "loaded_final": len(all_roots),
        "invalid_count": invalid_count,
        "duplicate_count": duplicate_count,
        "missing_insight_count": missing_insight_count,
    }

    return {
        "ok": True,
        "error": None,
        "roots": all_roots,
        "root_index": root_index,
        "prefix_index": prefix_index,
        "stats": stats,
    }

# ---------------------------------------------------------
# 4) تهيئة الحالة
# ---------------------------------------------------------
if "core_bundle" not in st.session_state:
    st.session_state.core_bundle = hunt_nibras_core()

if "user_path" not in st.session_state:
    st.session_state.user_path = []

if "last_text_analysis" not in st.session_state:
    st.session_state.last_text_analysis = None

bundle = st.session_state.core_bundle
core_roots = bundle["roots"]
root_index = bundle["root_index"]
prefix_index = bundle["prefix_index"]
stats = bundle["stats"]

if not bundle["ok"]:
    st.error(bundle["error"])
    st.stop()

# ---------------------------------------------------------
# 5) تخطيط الواجهة
# ---------------------------------------------------------
left_col, right_col = st.columns([1, 2])

# =========================================================
# العمود الأيسر: النظام والاستنطاق اليدوي
# =========================================================
with left_col:
    st.title("🌿 نبراس السيادي")
    st.subheader("رادار البصيرة الوجودية — طبقة الإدخال النصي")

    st.success(
        f"✅ تم تحميل الروح الكلية: {stats['loaded_final']} جذراً "
        f"(خام: {stats['loaded_raw']} | مكررات مستبعدة: {stats['duplicate_count']} | "
        f"ناقصة البصيرة: {stats['missing_insight_count']} | سجلات معطوبة: {stats['invalid_count']})"
    )

    # --- مصفوفة الجينات ---
    st.write("---")
    st.write("### 🧬 مصفوفة الاستحقاق الطاقي")

    gene_cols = st.columns(4)
    with gene_cols[0]:
        st.button("🐪 A", help=GENE_STYLE["A"]["meaning"])
    with gene_cols[1]:
        st.button("🐮 G", help=GENE_STYLE["G"]["meaning"])
    with gene_cols[2]:
        st.button("🐏 T", help=GENE_STYLE["T"]["meaning"])
    with gene_cols[3]:
        st.button("🐐 C", help=GENE_STYLE["C"]["meaning"])

    # --- فلاتر الاستنطاق اليدوي ---
    st.write("---")
    st.write("### 🧭 مرشحات الاستنطاق اليدوي")

    all_orbits = ["الكل"] + sorted(list({r["orbit"] for r in core_roots}), key=lambda x: get_orbit_index(x))
    all_genes = ["الكل", "A", "G", "T", "C"]

    selected_orbit = st.selectbox("تصفية حسب المدار", all_orbits)
    selected_gene = st.selectbox("تصفية حسب الجين", all_genes)

    filtered_roots = core_roots.copy()

    if selected_orbit != "الكل":
        filtered_roots = [r for r in filtered_roots if r["orbit"] == selected_orbit]

    if selected_gene != "الكل":
        filtered_roots = [r for r in filtered_roots if r["gene"] == selected_gene]

    filtered_names = [r["name"] for r in filtered_roots]

    st.write("---")
    st.write("### 🪞 استنطاق جذر يدوي")

    if filtered_names:
        selected_root_name = st.selectbox("اختر الجذر", filtered_names)
        selected_root = root_index.get(selected_root_name)

        if selected_root:
            st.markdown(
                f"""
                **الجذر:** `{selected_root['name']}`  
                **المدار:** `{selected_root['orbit']}`  
                **الجين:** {selected_root['gene_icon']} `{selected_root['gene']}` — {selected_root['gene_label']}  
                **الرتبة:** {selected_root['weight_class']}
                """
            )

            st.info(f"✨ البصيرة الوجودية:\n\n{selected_root['insight']}")
            st.metric("📊 الوزن السيادي", f"{selected_root['weight']:.2f}")

            if st.button(f"🌀 إضافة {selected_root['name']} إلى المسار"):
                already_exists = any(r["name"] == selected_root["name"] for r in st.session_state.user_path)
                if already_exists:
                    st.warning("⚠️ هذا الجذر موجود بالفعل في المسار.")
                else:
                    st.session_state.user_path.append(selected_root)
                    st.success(f"تمت إضافة ({selected_root['name']}) إلى المسار.")
    else:
        st.warning("⚠️ لا توجد جذور مطابقة لهذه المرشحات.")

    # --- أدوات المسار ---
    st.write("---")
    st.write("### 🧰 أدوات المسار")

    tool_cols = st.columns(2)
    with tool_cols[0]:
        if st.button("↩️ تراجع"):
            if st.session_state.user_path:
                removed = st.session_state.user_path.pop()
                st.info(f"تمت إزالة ({removed['name']})")
            else:
                st.warning("المسار فارغ.")

    with tool_cols[1]:
        if st.button("🧹 مسح المسار"):
            st.session_state.user_path = []
            st.success("تم مسح المسار بالكامل.")

# =========================================================
# العمود الأيمن: الإدخال النصي والتحليل
# =========================================================
with right_col:
    # -----------------------------------------------------
    # 1) الخريطة المدارية
    # -----------------------------------------------------
    st.write("### 🌌 الخريطة المدارية النجمية")

    df_all = pd.DataFrame(core_roots)

    fig = px.scatter(
        df_all,
        x="orbit_index",
        y="weight",
        color="orbit",
        text="name",
        hover_name="name",
        hover_data={
            "orbit": True,
            "gene": True,
            "gene_label": True,
            "weight": ':.2f',
            "orbit_index": False
        },
        labels={"orbit_index": "ترتيب المدار", "weight": "الوزن السيادي"},
        title="فضاء الجذور المحكمة حسب المدار والثقل"
    )

    fig.update_traces(
        marker=dict(size=10, line=dict(width=1.2, color="DarkSlateGrey")),
        textposition="top center"
    )

    orbit_tick_list = sorted(list({r["orbit"] for r in core_roots}), key=lambda x: get_orbit_index(x))

    fig.update_layout(
        template="plotly_dark",
        xaxis=dict(
            tickmode="array",
            tickvals=[get_orbit_index(o) for o in orbit_tick_list],
            ticktext=orbit_tick_list
        ),
        height=580
    )

    st.plotly_chart(fig, use_container_width=True)

    # -----------------------------------------------------
    # 2) طبقة الإدخال النصي
    # -----------------------------------------------------
    st.write("---")
    st.write("## 📝 طبقة الإدخال النصي السيادي")

    text_input = st.text_area(
        "أدخل نصًا عربيًا لاستنطاق جذوره",
        height=180,
        placeholder="مثال: إن مع العسر يسرا إن مع العسر يسرا"
    )

    analyze_cols = st.columns([1, 1, 2])

    analyze_now = False
    clear_text_analysis = False
    add_matched_to_path = False

    with analyze_cols[0]:
        if st.button("🔍 حلّل النص الآن"):
            analyze_now = True

    with analyze_cols[1]:
        if st.button("🧹 مسح نتائج التحليل"):
            clear_text_analysis = True

    if clear_text_analysis:
        st.session_state.last_text_analysis = None
        st.success("تم مسح نتائج التحليل النصي.")

    # تنفيذ التحليل
    if analyze_now:
        tokens = tokenize_arabic(text_input)

        matched_rows = []
        unmatched_words = []
        debug_rows = []

        for word in tokens:
            matched_name, match_type = match_root_logic(word, root_index, prefix_index)

            if matched_name:
                root_obj = root_index[matched_name]
                matched_rows.append({
                    "word": word,
                    "matched_root": root_obj["name"],
                    "match_type": match_type,
                    "orbit": root_obj["orbit"],
                    "gene": root_obj["gene"],
                    "gene_icon": root_obj["gene_icon"],
                    "gene_label": root_obj["gene_label"],
                    "weight": root_obj["weight"],
                    "weight_class": root_obj["weight_class"],
                    "insight": root_obj["insight"],
                })
            else:
                unmatched_words.append(word)

            debug_rows.append({
                "word": word,
                "matched_root": matched_name if matched_name else "—",
                "match_type": match_type
            })

        total_words = len(tokens)
        matched_count = len(matched_rows)
        unmatched_count = len(unmatched_words)
        match_rate = (matched_count / total_words * 100) if total_words > 0 else 0.0

        text_summary = summarize_text_analysis([
            root_index[row["matched_root"]] for row in matched_rows
        ]) if matched_rows else None

        st.session_state.last_text_analysis = {
            "raw_text": text_input,
            "normalized_text": normalize_arabic(text_input),
            "tokens": tokens,
            "matched_rows": matched_rows,
            "unmatched_words": unmatched_words,
            "debug_rows": debug_rows,
            "stats": {
                "total_words": total_words,
                "matched_count": matched_count,
                "unmatched_count": unmatched_count,
                "match_rate": match_rate,
            },
            "summary": text_summary,
        }

    # عرض النتائج الأخيرة إن وجدت
    analysis = st.session_state.last_text_analysis

    if analysis:
        st.write("### 📡 نتائج الاستنطاق النصي")

        stat_cols = st.columns(4)
        with stat_cols[0]:
            st.metric("عدد الكلمات", analysis["stats"]["total_words"])
        with stat_cols[1]:
            st.metric("الجذور المطابقة", analysis["stats"]["matched_count"])
        with stat_cols[2]:
            st.metric("غير المطابق", analysis["stats"]["unmatched_count"])
        with stat_cols[3]:
            st.metric("نسبة المطابقة", f"{analysis['stats']['match_rate']:.1f}%")

        st.caption(f"النص المنظّف: {analysis['normalized_text']}")

        if analysis["summary"]:
            st.success(analysis["summary"]["verdict"])

            # بطاقات عليا
            sum_cols = st.columns(4)
            with sum_cols[0]:
                st.metric("الجذور الفريدة", analysis["summary"]["unique_count"])
            with sum_cols[1]:
                st.metric("متوسط الثقل", f"{analysis['summary']['avg_weight']:.2f}")
            with sum_cols[2]:
                st.metric("المدار الغالب", analysis["summary"]["dominant_orbit"])
            with sum_cols[3]:
                dg = analysis["summary"]["dominant_gene_style"]
                st.metric("الجين الغالب", f"{dg['icon']} {analysis['summary']['dominant_gene']}")

            # زر إضافة الجذور المطابقة إلى المسار
            if st.button("🌀 أضف الجذور المطابقة إلى المسار"):
                existing_names = {r["name"] for r in st.session_state.user_path}
                added = 0

                for row in analysis["matched_rows"]:
                    root_obj = root_index[row["matched_root"]]
                    if root_obj["name"] not in existing_names:
                        st.session_state.user_path.append(root_obj)
                        existing_names.add(root_obj["name"])
                        added += 1

                st.success(f"تمت إضافة {added} جذراً جديداً إلى المسار.")

            # توزيع المدارات
            orbit_counts = analysis["summary"]["orbit_counts"]
            if orbit_counts:
                orbit_df = pd.DataFrame({
                    "المدار": list(orbit_counts.keys()),
                    "العدد": list(orbit_counts.values())
                })
                orbit_bar = px.bar(
                    orbit_df,
                    x="المدار",
                    y="العدد",
                    title="توزيع الجذور المطابقة حسب المدار"
                )
                orbit_bar.update_layout(template="plotly_dark", height=350)
                st.plotly_chart(orbit_bar, use_container_width=True)

            # جدول الجذور المطابقة
            st.write("### ⚖️ الجدول الناطق للجذور المطابقة")

            matched_df = pd.DataFrame(analysis["matched_rows"])

            if not matched_df.empty:
                display_df = matched_df.rename(columns={
                    "word": "الكلمة الأصلية",
                    "matched_root": "الجذر المطابق",
                    "match_type": "نوع المطابقة",
                    "orbit": "المدار",
                    "gene": "الجين",
                    "gene_label": "العائلة الجينية",
                    "weight": "الوزن",
                    "weight_class": "رتبة الحضور",
                    "insight": "البصيرة"
                })[
                    ["الكلمة الأصلية", "الجذر المطابق", "نوع المطابقة", "المدار", "الجين", "العائلة الجينية", "الوزن", "رتبة الحضور", "البصيرة"]
                ]

                st.dataframe(display_df, use_container_width=True, hide_index=True)

            # الكلمات غير المطابقة
            st.write("### 🚫 الكلمات غير المطابقة")
            if analysis["unmatched_words"]:
                st.code(" | ".join(analysis["unmatched_words"]), language="text")
            else:
                st.success("كل الكلمات المطروحة تم ربطها بطبقة جذرية أولية.")

            # جدول التشخيص
            st.write("### 🛠️ جدول التشخيص")
            debug_df = pd.DataFrame(analysis["debug_rows"]).rename(columns={
                "word": "الكلمة",
                "matched_root": "الجذر الناتج",
                "match_type": "آلية المطابقة"
            })
            st.dataframe(debug_df, use_container_width=True, hide_index=True)

            # تصدير تقرير النص
            st.write("---")
            st.write("### 📥 تصدير تقرير النص")

            if st.button("📜 جهّز تقرير النص النهائي"):
                now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                txt_lines = []
                txt_lines.append(f"Nibras Sovereign v27.2.0 — تقرير النص السيادي")
                txt_lines.append(f"التاريخ: {now_str}")
                txt_lines.append("")
                txt_lines.append("النص الأصلي:")
                txt_lines.append(analysis["raw_text"])
                txt_lines.append("")
                txt_lines.append("النص المنظف:")
                txt_lines.append(analysis["normalized_text"])
                txt_lines.append("")
                txt_lines.append("إحصاءات:")
                txt_lines.append(f"- عدد الكلمات: {analysis['stats']['total_words']}")
                txt_lines.append(f"- الجذور المطابقة: {analysis['stats']['matched_count']}")
                txt_lines.append(f"- غير المطابق: {analysis['stats']['unmatched_count']}")
                txt_lines.append(f"- نسبة المطابقة: {analysis['stats']['match_rate']:.1f}%")
                txt_lines.append("")

                if analysis["summary"]:
                    txt_lines.append("الخلاصة السيادية:")
                    txt_lines.append(analysis["summary"]["verdict"])
                    txt_lines.append("")

                txt_lines.append("الكلمات غير المطابقة:")
                if analysis["unmatched_words"]:
                    txt_lines.append(" | ".join(analysis["unmatched_words"]))
                else:
                    txt_lines.append("لا توجد كلمات غير مطابقة.")

                report_txt = "\n".join(txt_lines)

                report_json = {
                    "version": "27.2.0",
                    "generated_at": now_str,
                    "analysis": analysis,
                }

                dl_cols = st.columns(2)
                with dl_cols[0]:
                    st.download_button(
                        "📥 تحميل التقرير (TXT)",
                        data=report_txt,
                        file_name="nibras_text_report_v27_2_0.txt",
                        mime="text/plain"
                    )

                with dl_cols[1]:
                    st.download_button(
                        "📥 تحميل التقرير (JSON)",
                        data=json.dumps(report_json, ensure_ascii=False, indent=2),
                        file_name="nibras_text_report_v27_2_0.json",
                        mime="application/json"
                    )
        else:
            st.warning("⚠️ لم يتم العثور على جذور مطابقة كافية لإنتاج خلاصة ناطقة.")

    # -----------------------------------------------------
    # 3) مسار الوعي المبني
    # -----------------------------------------------------
    st.write("---")
    st.write("## 🌀 مسار الوعي المبني")

    if st.session_state.user_path:
        path_str = " -> ".join([root["name"] for root in st.session_state.user_path])
        st.code(path_str, language="text")

        path_summary = summarize_path(st.session_state.user_path)

        if path_summary:
            st.success(path_summary["verdict"])

            metric_cols = st.columns(4)
            with metric_cols[0]:
                st.metric("عدد الجذور", path_summary["total"])
            with metric_cols[1]:
                st.metric("متوسط الثقل", f"{path_summary['avg_weight']:.2f}")
            with metric_cols[2]:
                st.metric("الجذر القائد", path_summary["top_root"])
            with metric_cols[3]:
                dg = path_summary["dominant_gene_style"]
                st.metric("الجين الغالب", f"{dg['icon']} {path_summary['dominant_gene']}")

            if len(st.session_state.user_path) > 1:
                path_df = pd.DataFrame(st.session_state.user_path).reset_index(drop=True)

                line_fig = go.Figure(
                    data=go.Scatter(
                        x=path_df.index + 1,
                        y=path_df["weight"],
                        mode="lines+markers+text",
                        text=path_df["name"],
                        textposition="top center",
                        line=dict(color="#00FF00", width=4),
                        marker=dict(size=10)
                    )
                )

                line_fig.update_layout(
                    template="plotly_dark",
                    title_text="هندسة مسار الوعي الحالي",
                    xaxis_title="تسلسل الجذور",
                    yaxis_title="الوزن السيادي",
                    height=420
                )

                st.plotly_chart(line_fig, use_container_width=True)

            path_display_df = pd.DataFrame(st.session_state.user_path)[
                ["name", "orbit", "gene", "gene_label", "weight", "weight_class", "insight"]
            ].rename(columns={
                "name": "الجذر",
                "orbit": "المدار",
                "gene": "الجين",
                "gene_label": "العائلة الجينية",
                "weight": "الوزن",
                "weight_class": "رتبة الحضور",
                "insight": "البصيرة"
            })

            st.dataframe(path_display_df, use_container_width=True, hide_index=True)

            st.write("### 🏆 بروتوكول الختام")
            if st.button("🏆 خِت فِت (اعتماد المسار السيادي)"):
                now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                final_report = []
                final_report.append(f"المسار السيادي المعتمد للمستخدم محمد — {now_str}")
                final_report.append("")
                final_report.append(f"المسار: {path_str}")
                final_report.append("")
                final_report.append("الخلاصة السيادية:")
                final_report.append(path_summary["verdict"])
                final_report.append("")
                final_report.append("تفصيل المدارات:")
                for orbit_name, count in path_summary["orbit_counts"].items():
                    final_report.append(f"- {orbit_name}: {count}")
                final_report.append("")
                final_report.append("تفصيل الجينات:")
                for gene_code, count in path_summary["gene_counts"].items():
                    gs = GENE_STYLE.get(gene_code, GENE_STYLE["C"])
                    final_report.append(f"- {gs['icon']} {gene_code} ({gs['label']}): {count}")

                final_report_txt = "\n".join(final_report)

                final_report_json = {
                    "version": "27.2.0",
                    "user": "Mohamed",
                    "generated_at": now_str,
                    "path": [r["name"] for r in st.session_state.user_path],
                    "path_objects": st.session_state.user_path,
                    "summary": path_summary,
                }

                dl_cols = st.columns(2)
                with dl_cols[0]:
                    st.download_button(
                        label="📥 تحميل البيان النهائي (TXT)",
                        data=final_report_txt,
                        file_name="nibras_path_mohamed_v27_2_0.txt",
                        mime="text/plain"
                    )

                with dl_cols[1]:
                    st.download_button(
                        label="📥 تحميل البيان النهائي (JSON)",
                        data=json.dumps(final_report_json, ensure_ascii=False, indent=2),
                        file_name="nibras_path_mohamed_v27_2_0.json",
                        mime="application/json"
                    )

                st.balloons()
    else:
        st.info("✨ المسار فارغ حاليًا. أضف جذورًا يدويًا أو من تحليل النص.")

# ---------------------------------------------------------
# 6) تذييل
# ---------------------------------------------------------
st.write("---")
st.caption("Nibras Sovereign v27.2.0 — Sovereign Text Ingestion | طبقة الإدخال النصي الأولى")
