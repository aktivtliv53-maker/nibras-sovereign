# -*- coding: utf-8 -*-
"""
🜂 نبراس الطير v13.0 — Sovereign Core for Streamlit Cloud
البروتوكول: Idris-Mohammed | الختم السيادي النهائي
"""

import streamlit as st
import json
import re
import os
import sys
from pathlib import Path
from collections import Counter
from datetime import datetime
import plotly.graph_objects as go
import pandas as pd

# =========================================================
# 1. إعدادات الصفحة
# =========================================================
st.set_page_config(
    page_title="Nibras Sovereign v13.0",
    page_icon="🜂",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# 2. نظام فحص المسارات الذكي (Path Debugger)
# =========================================================
def debug_file_system():
    """يطبع هيكل الملفات الحالي للمساعدة في التشخيص"""
    debug_info = {
        "current_directory": os.getcwd(),
        "python_path": sys.path,
        "files_in_root": [],
        "files_in_data": [],
        "files_in_qroot": [],
        "json_files": []
    }
    
    # فحص المجلد الحالي
    try:
        debug_info["files_in_root"] = os.listdir(".") if os.path.exists(".") else []
    except:
        debug_info["files_in_root"] = ["لا يمكن القراءة"]
    
    # فحص مجلد data
    data_path = Path("data")
    if data_path.exists():
        try:
            debug_info["files_in_data"] = [f.name for f in data_path.iterdir() if f.is_file()]
        except:
            debug_info["files_in_data"] = ["لا يمكن القراءة"]
    
    # فحص مجلد qroot
    qroot_path = Path("qroot")
    if qroot_path.exists():
        try:
            debug_info["files_in_qroot"] = [f.name for f in qroot_path.iterdir() if f.is_file()]
        except:
            debug_info["files_in_qroot"] = ["لا يمكن القراءة"]
    
    # البحث عن جميع ملفات JSON
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(".json"):
                rel_path = os.path.relpath(os.path.join(root, file), ".")
                debug_info["json_files"].append(rel_path)
    
    return debug_info

# =========================================================
# 3. محرك البحث عن الملفات متعدد المستويات
# =========================================================
def find_file(filename, search_dirs=None):
    """
    البحث عن ملف في عدة مجلدات مع نظام تشخيص واضح
    
    Args:
        filename: اسم الملف (مثل "quran_roots_complete.json")
        search_dirs: قائمة المجلدات للبحث (افتراضي: [".", "data", "qroot", "assets"])
    
    Returns:
        (Path, str): (مسار الملف, رسالة تشخيص) أو (None, رسالة خطأ)
    """
    if search_dirs is None:
        search_dirs = [".", "data", "qroot", "assets", "./data", "./qroot"]
    
    # إضافة المسارات المطلقة والنسبية
    expanded_dirs = []
    for d in search_dirs:
        expanded_dirs.append(d)
        expanded_dirs.append(Path(d))
        expanded_dirs.append(Path.cwd() / d)
    
    # إزالة التكرار وتحويل إلى سلاسل نصية
    expanded_dirs = list(set([str(p) for p in expanded_dirs]))
    
    for search_dir in expanded_dirs:
        file_path = Path(search_dir) / filename
        if file_path.exists() and file_path.is_file():
            return file_path, f"✅ تم العثور على {filename} في: {file_path}"
    
    # البحث في جميع المجلدات الفرعية
    for root, dirs, files in os.walk("."):
        if filename in files:
            file_path = Path(root) / filename
            return file_path, f"✅ تم العثور على {filename} في: {file_path}"
    
    return None, f"❌ لم يتم العثور على {filename} في أي من المسارات: {search_dirs}"

# =========================================================
# 4. تحميل JSON مع تشخيص كامل
# =========================================================
@st.cache_data(ttl=3600, show_spinner=False)
def load_json_with_debug(filename, default=None):
    """
    تحميل ملف JSON مع تشخيص كامل للأخطاء
    
    Returns:
        (data, path, message): (المحتوى, المسار, رسالة الحالة)
    """
    if default is None:
        default = []
    
    file_path, message = find_file(filename)
    
    if not file_path:
        return default, None, message
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data, str(file_path), f"✅ تم تحميل {filename} بنجاح ({len(data) if isinstance(data, list) else 'dict'} عنصر)"
    except json.JSONDecodeError as e:
        return default, str(file_path), f"❌ خطأ في تنسيق JSON في {filename}: {e}"
    except Exception as e:
        return default, str(file_path), f"❌ خطأ غير متوقع في {filename}: {e}"

# =========================================================
# 5. تحميل جميع الملفات مع التشخيص
# =========================================================
@st.cache_data(ttl=3600)
def load_all_data():
    """تحميل جميع ملفات البيانات مع نظام تشخيص كامل"""
    
    # تشخيص نظام الملفات
    debug_info = debug_file_system()
    
    # تحميل الملفات
    letters_raw, letters_path, letters_msg = load_json_with_debug("sovereign_letters_v1.json", [])
    lexicon_raw, lexicon_path, lexicon_msg = load_json_with_debug("nibras_lexicon.json", [])
    quran_raw, quran_path, quran_msg = load_json_with_debug("quran_roots_complete.json", {})
    
    # تحميل ملفات إضافية إن وجدت
    patterns_raw, patterns_path, patterns_msg = load_json_with_debug("patterns.json", {})
    weights_raw, weights_path, weights_msg = load_json_with_debug("weights.json", {})
    
    # بناء رسالة الحالة
    status_messages = [
        letters_msg,
        lexicon_msg,
        quran_msg,
        patterns_msg if patterns_raw else "ℹ️ patterns.json غير مطلوب",
        weights_msg if weights_raw else "ℹ️ weights.json غير مطلوب"
    ]
    
    return {
        "letters": letters_raw,
        "lexicon": lexicon_raw,
        "quran_roots": quran_raw,
        "patterns": patterns_raw,
        "weights": weights_raw,
        "paths": {
            "letters": letters_path,
            "lexicon": lexicon_path,
            "quran": quran_path,
            "patterns": patterns_path,
            "weights": weights_path
        },
        "debug_info": debug_info,
        "status_messages": status_messages
    }

# =========================================================
# 6. التطبيع العربي
# =========================================================
def normalize_arabic(text):
    if not text:
        return ""
    text = re.sub(r'[\u0617-\u061A\u064B-\u0652\u0670]', '', text)
    replacements = {
        "أ": "ا", "إ": "ا", "آ": "ا",
        "ة": "ه", "ى": "ي", "ؤ": "و", "ئ": "ي"
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    text = re.sub(r"[^\u0621-\u063A\u0641-\u064A0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

# =========================================================
# 7. بناء فهارس الحروف
# =========================================================
def build_letters_index(letters_data):
    letters_idx = {}
    if isinstance(letters_data, list):
        for item in letters_data:
            char = item.get("letter")
            if char:
                letters_idx[normalize_arabic(char)] = item
    return letters_idx

# =========================================================
# 8. مولّد أشكال الكلمات
# =========================================================
PREFIXES = ["و", "ف", "ب", "ك", "ل", "س"]
DOUBLE_PREFIXES = ["ال", "لل", "بال", "وال", "فال", "كال", "ولل", "فلل"]
SUFFIXES = ["ه", "ها", "هم", "هن", "كما", "كم", "كن", "نا", "ي", "ك", "ا", "ان", "ون", "ين", "ات"]

def generate_word_forms(word):
    w = normalize_arabic(word)
    forms = set()
    if not w:
        return []
    
    forms.add(w)
    if len(w) >= 3:
        forms.add(w[:3])
    
    for p in PREFIXES:
        if w.startswith(p) and len(w) > len(p) + 2:
            forms.add(w[len(p):])
    for p in DOUBLE_PREFIXES:
        if w.startswith(p) and len(w) > len(p) + 2:
            forms.add(w[len(p):])
    
    current = list(forms)
    for f in current:
        for s in SUFFIXES:
            if f.endswith(s) and len(f) > len(s) + 2:
                forms.add(f[:-len(s)])
    
    current = list(forms)
    for f in current:
        if f.startswith("ال") and len(f) > 4:
            forms.add(f[2:])
    
    if len(w) >= 4:
        forms.add(w[:3])
        forms.add(w[1:4])
    if len(w) >= 5:
        forms.add(w[2:5])
    
    return [x for x in forms if len(x) >= 2]

# =========================================================
# 9. التحليل السيادي
# =========================================================
ORBIT_COLORS = {
    "أزل": "#ffd700",
    "سيادة": "#00ccff",
    "تمكين": "#4caf50",
    "وعي": "#9c27b0",
    "فطرة": "#ff9800",
    "يسر": "#00bcd4"
}

def analyze_path(text, letters_idx, lexicon_data):
    norm = normalize_arabic(text)
    
    res = {
        "mass": 0.0,
        "speed": 0.0,
        "orbit": "غير_مرصود",
        "energy": 0.0,
        "insight": "لا توجد بصيرة رصدية لهذا المسار.",
        "direction": "غير محدد",
        "count": 0,
        "matched_roots": [],
        "debug_forms": {},
        "orbit_weights": {}
    }
    
    # التحليل الحرفي
    direction_counter = Counter()
    clean_text = norm.replace(" ", "")
    for char in clean_text:
        meta = letters_idx.get(char)
        if meta:
            res["mass"] += float(meta.get("mass", 0))
            res["speed"] += float(meta.get("speed", 0))
            res["count"] += 1
            direction_counter[meta.get("direction", "غير محدد")] += 1
    
    if direction_counter:
        res["direction"] = direction_counter.most_common(1)[0][0]
    
    # التحليل المداري
    orbit_counter = Counter()
    orbit_best_match = {}
    
    if isinstance(lexicon_data, list):
        words = norm.split()
        for word in words:
            forms = generate_word_forms(word)
            res["debug_forms"][word] = forms[:10]
            
            for block in lexicon_data:
                orbit_name = block.get("orbit", "مدار مجهول")
                roots = block.get("roots", [])
                for r in roots:
                    r_name = normalize_arabic(r.get("name", ""))
                    weight = float(r.get("weight", 0))
                    insight = r.get("insight", "")
                    
                    if r_name in forms:
                        orbit_counter[orbit_name] += weight
                        res["energy"] += weight
                        res["matched_roots"].append({
                            "word": word,
                            "root": r_name,
                            "orbit": orbit_name,
                            "weight": weight,
                            "insight": insight
                        })
                        
                        if orbit_name not in orbit_best_match or weight > orbit_best_match[orbit_name]["weight"]:
                            orbit_best_match[orbit_name] = {"root": r_name, "weight": weight, "insight": insight}
                        break
    
    if orbit_counter:
        best_orbit = orbit_counter.most_common(1)[0][0]
        res["orbit"] = best_orbit
        res["orbit_weights"] = dict(orbit_counter)
        if best_orbit in orbit_best_match:
            res["insight"] = orbit_best_match[best_orbit]["insight"]
    
    # الطاقة النهائية
    orbit_weights_map = {"أزل": 1.6, "سيادة": 1.55, "تمكين": 1.5, "وعي": 1.35, "فطرة": 1.4, "يسر": 1.3}
    orbit_factor = orbit_weights_map.get(res["orbit"], 1.0)
    res["total"] = round((res["mass"] + res["speed"]) * 0.7 + res["energy"] * orbit_factor, 2)
    
    return res

# =========================================================
# 10. مخطط الرادار
# =========================================================
def create_radar_chart(results, labels):
    fig = go.Figure()
    categories = ["الكتلة", "السرعة", "طاقة المدار", "الجذور", "التوازن"]
    
    for i, res in enumerate(results):
        if res:
            values = [
                min(res["mass"] / 50, 10),
                min(res["speed"] / 50, 10),
                min(res["energy"] / 15, 10),
                min(len(res["matched_roots"]) / 20, 10),
                min(abs(res["total"]) / 100, 10)
            ]
            color = ORBIT_COLORS.get(res["orbit"], "#888")
            fig.add_trace(go.Scatterpolar(
                r=values, theta=categories, fill='toself',
                name=f"{labels[i]} ({res['orbit']})",
                line=dict(color=color, width=2),
                fillcolor=f"rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},0.3)"
            ))
    
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 10]), angularaxis=dict(gridcolor="#333")),
        showlegend=True, paper_bgcolor="#0a0a0a", plot_bgcolor="#0a0a0a",
        font=dict(color="#e0e0e0"), height=500
    )
    return fig

# =========================================================
# 11. الواجهة الرئيسية
# =========================================================
def main():
    st.title("🜂 نبراس الطير v13.0 — Sovereign Core for Cloud")
    
    # ========== تحميل البيانات مع التشخيص ==========
    with st.spinner("جاري تحميل الملفات..."):
        data = load_all_data()
    
    # ========== عرض حالة التحميل في الشريط الجانبي ==========
    with st.sidebar:
        st.markdown("### 🔍 فحص المسارات")
        
        # عرض حالة الملفات
        for msg in data["status_messages"]:
            if "✅" in msg:
                st.success(msg)
            elif "❌" in msg:
                st.error(msg)
            else:
                st.info(msg)
        
        # عرض هيكل الملفات
        with st.expander("📁 هيكل الملفات على السيرفر", expanded=False):
            st.write(f"**المجلد الحالي:** `{data['debug_info']['current_directory']}`")
            st.write("**الملفات في الجذر:**")
            for f in data['debug_info']['files_in_root'][:20]:
                st.write(f"- {f}")
            
            if data['debug_info']['files_in_data']:
                st.write("**الملفات في مجلد data:**")
                for f in data['debug_info']['files_in_data']:
                    st.write(f"- {f}")
            
            if data['debug_info']['files_in_qroot']:
                st.write("**الملفات في مجلد qroot:**")
                for f in data['debug_info']['files_in_qroot']:
                    st.write(f"- {f}")
            
            st.write("**جميع ملفات JSON:**")
            for f in data['debug_info']['json_files'][:30]:
                st.write(f"- {f}")
        
        # عرض المسارات المحملة
        with st.expander("📍 مسارات الملفات المحملة", expanded=False):
            for key, path in data["paths"].items():
                if path:
                    st.write(f"**{key}:** `{path}`")
                else:
                    st.write(f"**{key}:** ❌ غير موجود")
        
        st.markdown("---")
        st.markdown("*رونبي، السويد | 58-58*")
    
    # ========== بناء الفهارس ==========
    letters_idx = build_letters_index(data["letters"])
    lexicon_data = data["lexicon"]
    
    # ========== التحقق من تحميل الملفات ==========
    if not lexicon_data:
        st.error("⚠️ لم يتم تحميل ملف nibras_lexicon.json. الرجاء التأكد من وجوده في المجلد data/ أو qroot/")
        st.stop()
    
    st.success(f"✅ تم تحميل {len(letters_idx)} حرفاً و {len(lexicon_data)} مداراً")
    
    # ========== إدخال النصوص ==========
    col1, col2, col3 = st.columns(3)
    with col1:
        t1 = st.text_area("📍 المسار الأول", placeholder="الفتح\nنصر\nحق", height=150)
    with col2:
        t2 = st.text_area("📍 المسار الثاني", placeholder="بالحق\nالمستقيم\nالرحمن", height=150)
    with col3:
        t3 = st.text_area("📍 المسار الثالث", placeholder="استقم\nوالفتح\nمحمد", height=150)
    
    # ========== زر التحليل ==========
    if st.button("🚀 إطلاق الرصد السيادي", use_container_width=True, type="primary"):
        inputs = [t1, t2, t3]
        results = []
        labels = ["الأول", "الثاني", "الثالث"]
        
        for i, txt in enumerate(inputs):
            if txt.strip():
                with st.spinner(f"تحليل المسار {labels[i]}..."):
                    res = analyze_path(txt, letters_idx, lexicon_data)
                    results.append(res)
            else:
                results.append(None)
        
        # عرض النتائج
        st.markdown("---")
        st.markdown("## 📊 نتائج الرصد السيادي")
        
        valid_results = [r for r in results if r is not None]
        
        if not valid_results:
            st.warning("الرجاء إدخال نص في أحد المسارات")
        else:
            # عرض الكروت
            cols = st.columns(len(valid_results))
            for i, res in enumerate(valid_results):
                with cols[i]:
                    orbit = res["orbit"]
                    color = ORBIT_COLORS.get(orbit, "#888")
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #1a1a1a, #0a0a0a); 
                                border-right: 5px solid {color}; 
                                border-radius: 15px; 
                                padding: 20px; 
                                margin: 10px 0;
                                text-align: center;">
                        <h3 style="margin:0;">المسار {labels[i]}</h3>
                        <div style="font-size: 48px; font-weight: bold; color: {color};">{res['total']}</div>
                        <p><span style="background: {color}; padding: 4px 12px; border-radius: 20px; color: black; font-weight: bold;">{orbit}</span></p>
                        <p><b>الاتجاه:</b> {res['direction']}</p>
                        <p><b>الطاقة:</b> {res['energy']:.2f}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.progress(min(res["mass"] / 100, 1.0), text="🌊 الكتلة")
                    st.progress(min(res["speed"] / 100, 1.0), text="⚡ السرعة")
                    st.progress(min(res["energy"] / 20, 1.0), text="🟢 طاقة المدار")
            
            # الرادار
            fig = create_radar_chart(valid_results, [labels[i] for i, r in enumerate(results) if r])
            st.plotly_chart(fig, use_container_width=True)
            
            # تفصيل الجذور
            st.markdown("---")
            st.markdown("### 📖 تفصيل الجذور المطابقة")
            tabs = st.tabs([f"المسار {labels[i]}" for i, r in enumerate(results) if r])
            tab_idx = 0
            for i, res in enumerate(results):
                if res:
                    with tabs[tab_idx]:
                        if res["matched_roots"]:
                            for m in res["matched_roots"][:15]:
                                orbit_color = ORBIT_COLORS.get(m["orbit"], "#888")
                                st.markdown(f"""
                                <div style="background: #1a1a1a; padding: 10px; border-radius: 10px; margin: 5px 0; border-right: 3px solid {orbit_color};">
                                    <b>{m['word']}</b> → <code>{m['root']}</code><br>
                                    <span style="color: {orbit_color};">{m['orbit']}</span> | الوزن: {m['weight']}<br>
                                    <small>{m['insight'][:100]}</small>
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.info("لا توجد جذور مطابقة")
                    tab_idx += 1
            
            # المستشار
            st.markdown("---")
            best = max(valid_results, key=lambda x: x["total"])
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #001f24, #001a1a); 
                        border-right: 5px solid {ORBIT_COLORS.get(best['orbit'], '#00afcc')}; 
                        border-radius: 20px; 
                        padding: 25px; 
                        margin-top: 20px;">
                <h3>🧠 المستشار السيادي</h3>
                <p><b>المسار الأقوى:</b> {best['orbit']} بقوة {best['total']}</p>
                <p><b>البصيرة:</b> {best['insight']}</p>
                <p><b>التوجيه:</b> الاتجاه {best['direction']} يشير إلى أن هذه الطاقة {best['direction'] == 'inward' and 'تتركز داخلياً قبل الظهور' or 'تندفع نحو التحقق الخارجي'}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.balloons()

# =========================================================
# 12. التشغيل
# =========================================================
if __name__ == "__main__":
    main()
