Import streamlit as st
import json
import re
from pathlib import Path
from collections import Counter, defaultdict

# =========================================================
# 1) إعداد الصفحة
# =========================================================
st.set_page_config(
    page_title="Nibras Sovereign Quranic v8.0 FINAL",
    page_icon="🛰️",
    layout="wide"
)

st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background-color: #0a0a0a; color: #e0e0e0; }
    .stProgress > div > div > div > div { background-image: linear-gradient(to right, #2e7d32, #aed581); }
    .comparison-card { 
        background: #161616; padding: 15px; border-radius: 15px; 
        border: 1px solid #262626; margin-bottom: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .mentor-box { 
        background: #001f24; border-right: 5px solid #00afcc; 
        padding: 20px; border-radius: 12px; margin-top: 20px;
    }
    .detail-box {
        background: #111; padding: 12px; border-radius: 10px; margin-bottom: 8px; border: 1px solid #222;
    }
    .status-ok {
        background: #0f2a12; border: 1px solid #2e7d32; padding: 10px; border-radius: 10px; margin: 8px 0;
    }
    .status-warn {
        background: #2a1f0f; border: 1px solid #a67c00; padding: 10px; border-radius: 10px; margin: 8px 0;
    }
    h1, h2, h3 { color: #4CAF50 !important; text-align: center; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 2) تحميل الملفات
# =========================================================
def safe_load_json(filename):
    search_paths = [
        Path("."),
        Path("./qroot"),
        Path("./nibras mobail"),
        Path("./data")
    ]
    for folder in search_paths:
        file_path = folder / filename
        if file_path.exists():
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    return json.load(f), str(file_path)
            except Exception as e:
                st.error(f"خطأ في قراءة {filename}: {e}")
    return None, None

letters_raw, path_l = safe_load_json("sovereign_letters_v1.json")
lexicon_raw, path_x = safe_load_json("nibras_lexicon.json")

# =========================================================
# 3) التطبيع العربي
# =========================================================
def normalize_arabic(text):
    if not text:
        return ""
    # إزالة التشكيل
    text = re.sub(r'[\u0617-\u061A\u064B-\u0652\u0670]', '', text)
    # توحيد الحروف
    replacements = {
        "أ": "ا", "إ": "ا", "آ": "ا",
        "ة": "ه",
        "ى": "ي",
        "ؤ": "و",
        "ئ": "ي"
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    # حذف الرموز غير العربية مع الإبقاء على المسافة
    text = re.sub(r'[^\u0621-\u064A\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# =========================================================
# 4) فلترة الجذور الحقيقية (استبعاد الوسوم الصرفية)
# =========================================================
MORPH_TAG_PATTERN = re.compile(
    r'^(?:'
    r'[123](?:MS|FS|MP|FP|D|P|S)|'
    r'ACC|GEN|NOM|IMPF|IMPV|PERF|'
    r'ACT_PCPL|PASS_PCPL|'
    r'FS|MS|FP|MP|FD|MD|'
    r'INDEF|DEF|NEG|COND|'
    r'PRON|REL|DEM|PREP|CONJ|PART|'
    r'VN|N|V|ADJ'
    r')$'
)

def is_valid_arabic_root(root_text):
    """
    يقبل فقط الجذور/اللمّات العربية الحقيقية
    ويرفض الوسوم الصرفية والرموز التقنية.
    """
    if not root_text:
        return False

    root_text = str(root_text).strip()

    # رفض LEM:
    if root_text.startswith("LEM:"):
        return False

    # رفض الوسوم الصرفية
    if MORPH_TAG_PATTERN.match(root_text):
        return False

    # يجب أن يكون عربيًا فقط
    pure = normalize_arabic(root_text)
    if not pure:
        return False

    # بدون مسافات داخلية
    if " " in pure:
        return False

    # طول منطقي
    if not (2 <= len(pure) <= 6):
        return False

    return True

# =========================================================
# 5) بناء فهرس الحروف
# =========================================================
letters_idx = {}
if isinstance(letters_raw, list):
    for item in letters_raw:
        char = item.get("letter")
        if char:
            letters_idx[normalize_arabic(char)] = item

# =========================================================
# 6) تنظيف المعجم وبناء ملف نظيف تلقائيًا
# =========================================================
def clean_lexicon_and_build_index(lexicon_raw):
    """
    - ينظف المعجم الحالي
    - يستبعد الوسوم الصرفية
    - يبني root_index للاستعمال المباشر
    - ويُنتج نسخة clean يمكن حفظها كملف
    """
    root_index = defaultdict(list)
    clean_blocks_map = {}

    if not isinstance(lexicon_raw, list):
        return dict(root_index), []

    for block in lexicon_raw:
        orbit_name = block.get("orbit", "مدار مجهول")
        block_insight = block.get("insight", f"هذا الجذر ينتسب إلى مدار {orbit_name}")
        roots = block.get("roots", [])

        if not isinstance(roots, list):
            continue

        if orbit_name not in clean_blocks_map:
            clean_blocks_map[orbit_name] = {
                "orbit": orbit_name,
                "insight": block_insight,
                "roots": []
            }

        seen_in_orbit = set()

        for r in roots:
            raw_root = r.get("name") or r.get("root") or r.get("lemma") or ""
            raw_root = str(raw_root).strip()

            if not is_valid_arabic_root(raw_root):
                continue

            norm_root = normalize_arabic(raw_root)

            weight = (
                r.get("weight")
                or r.get("frequency")
                or block.get("weight")
                or 1
            )

            insight = (
                r.get("insight")
                or block.get("insight")
                or f"هذا الجذر ينتسب إلى مدار {orbit_name}"
            )

            entry = {
                "root": norm_root,
                "weight": float(weight),
                "orbit": orbit_name,
                "insight": insight
            }

            root_index[norm_root].append({
                "orbit": orbit_name,
                "weight": float(weight),
                "insight": insight
            })

            # منع التكرار داخل نفس المدار في الملف النظيف
            if norm_root not in seen_in_orbit:
                clean_blocks_map[orbit_name]["roots"].append({
                    "root": norm_root,
                    "weight": float(weight),
                    "insight": insight
                })
                seen_in_orbit.add(norm_root)

    clean_lexicon = list(clean_blocks_map.values())
    return dict(root_index), clean_lexicon

quranic_root_index, clean_lexicon = clean_lexicon_and_build_index(lexicon_raw)

# حفظ الملف النظيف تلقائيًا
clean_saved_path = None
if clean_lexicon:
    try:
        clean_file = Path("nibras_lexicon_clean.json")
        with open(clean_file, "w", encoding="utf-8") as f:
            json.dump(clean_lexicon, f, ensure_ascii=False, indent=2)
        clean_saved_path = str(clean_file.resolve())
    except Exception:
        clean_saved_path = None

# =========================================================
# 7) تجريد صرفي ذكي بديل عن w[:3]
# =========================================================
PREFIXES = ["وال", "فال", "بال", "كال", "لل", "ال", "و", "ف", "ب", "ك", "ل", "س"]
SUFFIXES = ["هما", "كما", "كم", "كن", "هم", "هن", "نا", "ها", "ه", "ات", "ان", "ون", "ين", "يه", "ية", "ي", "ة", "ا"]

def strip_prefixes(word):
    candidates = {word}
    for p in PREFIXES:
        if word.startswith(p) and len(word) - len(p) >= 2:
            candidates.add(word[len(p):])
    return candidates

def strip_suffixes(word):
    candidates = {word}
    for s in SUFFIXES:
        if word.endswith(s) and len(word) - len(s) >= 2:
            candidates.add(word[:-len(s)])
    return candidates

def generate_root_candidates(word):
    """
    بديل ذكي عن القصّ الأعمى w[:3]
    """
    word = normalize_arabic(word)
    if not word:
        return []

    candidates = set()
    candidates.add(word)

    # إزالة السوابق
    pref_forms = set()
    for form in list(candidates):
        pref_forms.update(strip_prefixes(form))
    candidates.update(pref_forms)

    # إزالة اللواحق
    suff_forms = set()
    for form in list(candidates):
        suff_forms.update(strip_suffixes(form))
    candidates.update(suff_forms)

    # إزالة سوابق + لواحق معًا
    combo_forms = set()
    for form in list(candidates):
        for p_form in strip_prefixes(form):
            combo_forms.update(strip_suffixes(p_form))
    candidates.update(combo_forms)

    # تقليل التضعيف البسيط
    reduced = set()
    for form in candidates:
        reduced.add(re.sub(r'(.)\1+', r'\1', form))
    candidates.update(reduced)

    # أخذ احتمالات ثلاثية لكن بعد التجريد فقط
    tri_forms = set()
    for form in list(candidates):
        if 3 <= len(form) <= 5:
            tri_forms.add(form[:3])
    candidates.update(tri_forms)

    # فلترة نهائية
    final = []
    for c in candidates:
        c = normalize_arabic(c)
        if 2 <= len(c) <= 6:
            final.append(c)

    # ترتيب: الأطول أولاً
    final = sorted(set(final), key=lambda x: (-len(x), x))
    return final

# =========================================================
# 8) مطابقة الجذر القرآني
# =========================================================
def match_quranic_root(word, root_index):
    candidates = generate_root_candidates(word)

    # مطابقة كاملة أولاً
    for c in candidates:
        if c in root_index:
            return c, root_index[c]

    # ثم ثلاثي
    for c in candidates:
        if len(c) == 3 and c in root_index:
            return c, root_index[c]

    return None, []

# =========================================================
# 9) التحليل الكامل
# =========================================================
def analyze_path(text, l_idx, root_index):
    norm = normalize_arabic(text)
    res = {
        "mass": 0.0,
        "speed": 0.0,
        "energy": 0.0,
        "orbit": "غير_مرصود",
        "insight": "لا توجد بصيرة رصدية لهذا المسار.",
        "direction": "غير محدد",
        "count": 0,
        "matched_roots": [],
        "orbit_counter": Counter()
    }

    # -----------------------------
    # أ) التحليل الحرفي
    # -----------------------------
    clean_text = norm.replace(" ", "")
    dir_counter = Counter()
    energy_types = Counter()

    for char in clean_text:
        meta = l_idx.get(char)
        if meta:
            res["mass"] += float(meta.get("mass", 0))
            res["speed"] += float(meta.get("speed", 0))
            res["count"] += 1

            d = meta.get("direction", "unknown")
            dir_counter[d] += 1

            et = meta.get("energy_type", "unknown")
            energy_types[et] += 1

    if dir_counter:
        res["direction"] = dir_counter.most_common(1)[0][0]

    if energy_types:
        res["dominant_energy_type"] = energy_types.most_common(1)[0][0]
    else:
        res["dominant_energy_type"] = "غير محدد"

    # -----------------------------
    # ب) التحليل القرآني الجذري
    # -----------------------------
    words = norm.split()
    for word in words:
        matched_root, entries = match_quranic_root(word, root_index)
        if matched_root and entries:
            best_entry = max(entries, key=lambda x: x["weight"])
            res["energy"] += best_entry["weight"]
            res["orbit_counter"][best_entry["orbit"]] += best_entry["weight"]
            res["matched_roots"].append({
                "word": word,
                "root": matched_root,
                "orbit": best_entry["orbit"],
                "weight": best_entry["weight"],
                "insight": best_entry["insight"]
            })

    # المدار النهائي
    if res["orbit_counter"]:
        best_orbit, _ = res["orbit_counter"].most_common(1)[0]
        res["orbit"] = best_orbit

        for m in res["matched_roots"]:
            if m["orbit"] == best_orbit:
                res["insight"] = m["insight"]
                break

    res["total"] = round(res["mass"] + res["speed"] + res["energy"], 2)
    return res

# =========================================================
# 10) الواجهة الرئيسية
# =========================================================
st.title("🛰️ محراب نبراس السيادي القرآني v8.0 FINAL")
st.write("تحليل حرفي + جذري قرآني حقيقي + تنظيف تلقائي للمعجم + مهيأ للجوال")

# =========================================================
# 11) لوحة التشخيص
# =========================================================
with st.sidebar.expander("🛠️ لوحة التشخيص السيادي", expanded=True):
    st.write(f"ملف الحروف: {path_l if path_l else '❌ مفقود'}")
    st.write(f"ملف المعجم الخام: {path_x if path_x else '❌ مفقود'}")
    st.write(f"عدد الحروف المفهرسة: {len(letters_idx)}")
    st.write(f"عدد الجذور القرآنية المقبولة: {len(quranic_root_index)}")
    st.write(f"عدد كتل المعجم النظيف: {len(clean_lexicon)}")

    if clean_saved_path:
        st.success("✅ تم إنشاء nibras_lexicon_clean.json تلقائيًا")
    else:
        st.warning("⚠️ تعذر حفظ الملف النظيف تلقائيًا (لكن التحليل يعمل)")

# =========================================================
# 12) أزرار الأدوات
# =========================================================
tool_col1, tool_col2 = st.columns(2)

with tool_col1:
    if st.button("📦 عرض المعجم النظيف (أول 5 كتل)", use_container_width=True):
        if clean_lexicon:
            st.subheader("📘 معاينة nibras_lexicon_clean.json")
            st.json(clean_lexicon[:5])
        else:
            st.warning("لا يوجد معجم نظيف متاح.")

with tool_col2:
    if st.button("📥 تحميل المعجم النظيف كنص JSON", use_container_width=True):
        if clean_lexicon:
            clean_json_str = json.dumps(clean_lexicon, ensure_ascii=False, indent=2)
            st.download_button(
                label="⬇️ اضغط هنا لتنزيل nibras_lexicon_clean.json",
                data=clean_json_str,
                file_name="nibras_lexicon_clean.json",
                mime="application/json"
            )
        else:
            st.warning("لا يوجد معجم نظيف للتنزيل.")

st.markdown("---")

# =========================================================
# 13) الإدخال الثلاثي
# =========================================================
col1, col2, col3 = st.columns(3)
with col1:
    t1 = st.text_area("📍 المسار 1", placeholder="أدخل الآية أو النص...", height=140, key="v1")
with col2:
    t2 = st.text_area("📍 المسار 2", placeholder="أدخل الآية أو النص...", height=140, key="v2")
with col3:
    t3 = st.text_area("📍 المسار 3", placeholder="أدخل الآية أو النص...", height=140, key="v3")

# =========================================================
# 14) التحليل المقارن
# =========================================================
if st.button("🚀 إطلاق الرصد القرآني المقارن", use_container_width=True):
    inputs = [t1, t2, t3]
    results = []
    display_cols = st.columns(3)

    for i, txt in enumerate(inputs):
        if txt.strip():
            res = analyze_path(txt, letters_idx, quranic_root_index)
            results.append(res)

            with display_cols[i]:
                st.markdown(f"""
                <div class="comparison-card">
                    <h3 style='margin:0;'>المسار {i+1}</h3>
                    <h1 style='color:#8bc34a; font-size:40px;'>{res['total']}</h1>
                    <p style='text-align:center;'><b>المدار:</b> {res['orbit']}</p>
                    <p style='text-align:center;'><b>الجذور المطابقة:</b> {len(res['matched_roots'])}</p>
                </div>
                """, unsafe_allow_html=True)

                st.caption("🌊 موجة الكتلة")
                st.progress(min(res["mass"] / 250, 1.0))

                st.caption("⚡ موجة السرعة")
                st.progress(min(res["speed"] / 250, 1.0))

                st.caption("🌀 موجة الجذر القرآني")
                st.progress(min(res["energy"] / 250, 1.0))

                st.markdown(f"""
                <div class="detail-box">
                    <b>الاتجاه الغالب:</b> {res['direction']}<br>
                    <b>نوع الطاقة الغالب:</b> {res.get('dominant_energy_type', 'غير محدد')}<br>
                    <b>عدد الحروف المرصودة:</b> {res['count']}
                </div>
                """, unsafe_allow_html=True)

                if res["matched_roots"]:
                    st.markdown("### 🔍 الجذور المرصودة")
                    for m in res["matched_roots"][:6]:
                        st.markdown(f"""
                        <div class="detail-box">
                            <b>الكلمة:</b> {m['word']}<br>
                            <b>الجذر:</b> {m['root']}<br>
                            <b>المدار:</b> {m['orbit']}<br>
                            <b>الوزن:</b> {m['weight']}
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="status-warn">
                        ⚠️ لم يتم العثور على جذور قرآنية مطابقة في هذا المسار.
                    </div>
                    """, unsafe_allow_html=True)

        else:
            results.append(None)

    # =====================================================
    # 15) المستشار السيادي
    # =====================================================
    valid_results = [r for r in results if r is not None]
    if valid_results:
        st.markdown("<div class='mentor-box'>", unsafe_allow_html=True)
        st.markdown("### 🧠 المستشار الشخصي السيادي")

        best = max(valid_results, key=lambda x: x["total"])

        with st.chat_message("assistant", avatar="🕌"):
            st.write(f"أعلى مسار رصدي حاليًا هو المدار **({best['orbit']})**.")
            st.info(f"**البصيرة:** {best['insight']}")
            st.success(f"**الاتجاه الغالب:** {best['direction']}")
            st.write(f"**نوع الطاقة الحرفية الغالب:** {best.get('dominant_energy_type', 'غير محدد')}")
            st.write(f"**عدد الجذور القرآنية المطابقة:** {len(best['matched_roots'])}")
            st.write(f"**إجمالي الطاقة السيادية:** {best['total']}")

        st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# 16) تذييل
# =========================================================
st.sidebar.markdown("---")
st.sidebar.write("Blekinge, Sweden | Nibras Mobile Final")
st.sidebar.write("خِت فِت.")
