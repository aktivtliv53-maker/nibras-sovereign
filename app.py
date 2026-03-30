# -*- coding: utf-8 -*-
# ==============================================================================
# نظام نِبْرَاس السيادي (Nibras Sovereign System) - الإصدار v26.2.2
# مَبنيٌّ على بروتوكول "لا مَسَاس" و "الاستحقاق الجيني الحتمي"
# الإصدار: Root Integrity & Insight Diagnostics - كشف أسباب سقوط الجذور
# المستخدم المهيمن: محمّد | CPU: السجدة (5) | الموقع: رونبي، السويد
# ==============================================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import re
import random
import os
import json
import time
import hashlib
import numpy as np

# ==============================================================================
# [1] مصفوفة الجينات والرموز السيادية (The Absolute Gene Matrix)
# ==============================================================================
# هذه المصفوفة تمثل المحاور الأربعة للتمكين الوجودي كما صاغها "نبراس".
GENE_STYLE = {
    'A': {
        'name': 'الإبل', 'color': '#4fc3f7', 'icon': '🐪', 
        'meaning': 'اليسر والفتح المداري',
        'desc': 'طاقة الانطلاق والمبادرة، تمثل الحركة نحو الفتح المبين واليسر المطلق.'
    },
    'G': {
        'name': 'البقر', 'color': '#FFD700', 'icon': '🐄', 
        'meaning': 'الخير والتأسيس الراسخ',
        'desc': 'طاقة التجذر والبناء الصبور لحقائق التمكين، تمثل الخير الوفير المستقر.'
    },
    'T': {
        'name': 'الضأن', 'color': '#4CAF50', 'icon': '🐑', 
        'meaning': 'السكينة والمقام الآمن',
        'desc': 'طاقة السكينة والجمع والاحتواء، حيث يستقر المعنى في محراب السيادة.'
    },
    'C': {
        'name': 'المعز', 'color': '#ff5252', 'icon': '🐐', 
        'meaning': 'السمو والتمكين الصاعد',
        'desc': 'طاقة الارتفاع والحدّة في طلب الحق والسيادة، تمثل قوة الإرادة الصاعدة.'
    },
    'N': {
        'name': 'إشراق', 'color': '#00ffcc', 'icon': '✨', 
        'meaning': 'الانبثاق الهجين الصافي',
        'desc': 'نقطة الانبثاق التي تولد من تفاعل الأضداد لتعلن ولادة وعي سيادي جديد.'
    }
}

# ==============================================================================
# [2] المحركات الفوقية للاستنطاق (Sovereign Meta-Engines)
# ==============================================================================
def summarize_word_signature(root):
    """تحويل الجذر إلى توقيع جيني ثابت (Deterministic Signature)."""
    if not root: return {'dominant_gene': 'N', 'total_energy': 300.0}
    
    # بصمة رياضية ثابتة للجذر لضمان عدم العشوائية
    hash_object = hashlib.md5(root.encode())
    hash_val = int(hash_object.hexdigest(), 16)
    
    genes_list = ['A', 'G', 'T', 'C']
    dominant_gene = genes_list[hash_val % 4]
    
    # حساب الطاقة بناءً على طول الجذر (نظام v12_final)
    base_energy = len(root) * 285.0
    energy_variance = (hash_val % 150)
    total_energy = float(base_energy + energy_variance)
    
    return {
        'dominant_gene': dominant_gene,
        'total_energy': total_energy,
        'vector_x': (hash_val % 30 - 15) / 120.0,
        'vector_y': ((hash_val >> 4) % 30 - 15) / 120.0
    }

def normalize_sovereign(text):
    """تطهير النص للوصول لجوهر الحرف الهندسي."""
    if not text: return ""
    text = re.sub(r'[\u064B-\u0652]', '', text)
    replacements = {"أ": "ا", "إ": "ا", "آ": "ا", "ة": "ه", "ى": "ي"}
    for k, v in replacements.items():
        text = text.replace(k, v)
    return re.sub(r'[^\u0621-\u064A\s]', '', text).strip()

def match_root_logic(word, index_keys):
    """بروتوكول الربط المداري لاستخلاص الجذور الثلاثية - النسخة التشخيصية v26.2.2"""
    w = normalize_sovereign(word)
    if not w or len(w) < 2: return None
    if w in index_keys: return w  # مطابقة تامة
    
    # بروتوكول الزوائد الصارم
    prefixes = ["ال", "و", "ف", "ب", "ك", "ل", "س"]
    suffixes = ["ون", "ين", "ان", "ات", "ه", "ها", "هم", "كم", "نا", "كما", "تم", "هن"]
    
    for p in prefixes:
        if w.startswith(p) and len(w)-len(p) >= 3:
            candidate = w[len(p):]
            if candidate in index_keys: return candidate
            
    for s in suffixes:
        if w.endswith(s) and len(w)-len(s) >= 3:
            candidate = w[:-len(s)]
            if candidate in index_keys: return candidate
    
    # منع w[:3] العشوائي - لا نقبل إلا بمطابقة حقيقية من الفهرس
    return w if w in index_keys else None

# ==============================================================================
# [3] غلاف الاستقرار والتحصين (Advanced Shielding CSS)
# ==============================================================================
st.set_page_config(page_title="Nibras Sovereign v26.2.2", page_icon="🛡️", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Orbitron:wght@600&display=swap');
    
    [data-testid="stAppViewContainer"] {
        background: radial-gradient(circle at center, #0a0a1a 0%, #000000 100%);
        color: #e0e0e0; font-family: 'Amiri', serif; direction: rtl;
    }

    /* بروتوكول حماية نسخة الموبايل (Final Mobile Shield) */
    @media (max-width: 768px) {
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] { display: none !important; }
        [data-testid="stSidebar"] { width: 0px !important; min-width: 0px !important; }
        .main .block-container { padding: 10px !important; }
        .stTabs [data-baseweb="tab"] { font-size: 0.8em; padding: 5px; }
        .story-box { font-size: 1.15em; padding: 25px; line-height: 1.8; }
        .stat-val { font-size: 1.8em !important; }
    }

    .story-box {
        background: linear-gradient(135deg, rgba(10,21,10,0.85) 0%, rgba(1,1,3,0.95) 100%);
        padding: 40px; border-radius: 25px; border-right: 15px solid #4CAF50;
        line-height: 2.6; font-size: 1.6em; box-shadow: 0 20px 60px rgba(0,0,0,0.8);
        margin-bottom: 30px;
    }
    
    .stat-container {
        display: flex; justify-content: space-around; background: #0d0d14;
        padding: 30px; border-radius: 20px; border: 1px solid #1a1a2a; margin: 25px 0;
    }
    
    .stat-val { font-size: 2.8em; font-weight: bold; color: #00ffcc; font-family: 'Orbitron', sans-serif; }
    .stat-label { color: #888; font-size: 1.1em; margin-top: 5px; }

    .ultra-card {
        background: #0d0d14; padding: 35px; border-radius: 20px;
        border-top: 8px solid #4fc3f7; text-align: center;
        transition: all 0.5s ease; margin-bottom: 25px;
    }
    .ultra-card:hover { transform: translateY(-10px); background: #14141f; }

    .adaptive-log {
        background: #000; border: 1px solid #ffaa00; padding: 25px;
        color: #ffaa00; font-family: 'Courier New', monospace;
        height: 300px; overflow-y: auto; border-radius: 15px;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# [4] محرك ربط المدار (Data Core & Session State) - Semantic Activation Patch
# ==============================================================================
if 'grand_monolith' not in st.session_state:
    st.session_state.grand_monolith = {
        'bodies': [], 'pool': [], 'logs': [], 'metrics': {}, 'active': False
    }

roots_path = "quran_roots_complete.json"
if not os.path.exists(roots_path):
    roots_path = "data/quran_roots_complete.json"

# --- المدارات القياسية المعتمدة ---
KNOWN_ORBITS = {"وعي", "نور", "رحمة", "حق", "ميزان", "صبر", "هداية", "قوة", "بصيرة", "توحيد"}

# --- خرائط التطبيع ---
ORBIT_ALIAS = {
    "الأزل": "حق",
    "الازل": "حق",
    "Sovereign Origin": "حق",
    "sovereign origin": "حق",
    "الاصل": "حق",
    "الأصل": "حق"
}

ORBIT_TO_GENE = {
    "وعي": "N",
    "نور": "A",
    "رحمة": "T",
    "حق": "C",
    "ميزان": "G",
    "صبر": "T",
    "هداية": "A",
    "قوة": "C",
    "بصيرة": "N",
    "توحيد": "G"
}

def canonical_orbit(orbit_name: str) -> str:
    """تطبيع اسم المدار إلى المدارات المعروفة فقط."""
    if not orbit_name:
        return "وعي"

    raw = str(orbit_name).strip()

    # إزالة النص الإنجليزي بين الأقواس
    if "(" in raw:
        raw = raw.split("(")[0].strip()

    # تطبيع عربي
    raw_norm = normalize_sovereign(raw)

    # مباشر
    if raw_norm in KNOWN_ORBITS:
        return raw_norm

    # من alias
    if raw in ORBIT_ALIAS:
        return ORBIT_ALIAS[raw]
    if raw_norm in ORBIT_ALIAS:
        return ORBIT_ALIAS[raw_norm]

    return "وعي"

def load_semantic_roots_db(path):
    """تحميل قاعدة الجذور بصيغ متعددة وتحويلها إلى فهرس جذري ناطق."""
    if not os.path.exists(path):
        st.error("⚠️ فشل الاتصال بالقاعدة السيادية.")
        st.stop()

    with open(path, 'r', encoding='utf-8') as f:
        raw_db = json.load(f)

    r_index = {}
    all_roots_flat = []
    orbit_counter = Counter()

    # -------------------------------------------------
    # الصيغة (A): قائمة مدارات
    # [
    #   { "orbit": "...", "roots": [ {"name":"حق","weight":1.9,"insight":"..."} ] }
    # ]
    # -------------------------------------------------
    if isinstance(raw_db, list):
        for orbit_block in raw_db:
            orbit_raw = orbit_block.get("orbit", "وعي")
            orbit_canonical = canonical_orbit(orbit_raw)

            for item in orbit_block.get("roots", []):
                root_name = normalize_sovereign(item.get("name", item.get("root", "")))
                if not root_name:
                    continue

                record = {
                    "root": root_name,
                    "orbit": orbit_canonical,
                    "orbit_raw": orbit_raw,
                    "weight": float(item.get("weight", 1.0)),
                    "insight": item.get("insight", item.get("meaning", "لا توجد بصيرة مفسّرة لهذا الجذر.")),
                    "meaning": item.get("meaning", item.get("insight", "لا توجد دلالة موصوفة.")),
                }

                if root_name not in r_index or record["weight"] > r_index[root_name]["weight"]:
                    r_index[root_name] = record

                all_roots_flat.append(record)
                orbit_counter[orbit_canonical] += 1

    # -------------------------------------------------
    # الصيغة (B): dict يحتوي roots بشكل root-centric
    # { "roots": [ {"root":"...", "orbit":"...", ...} ] }
    # -------------------------------------------------
    elif isinstance(raw_db, dict) and "roots" in raw_db:
        for item in raw_db.get("roots", []):
            root_name = normalize_sovereign(item.get("root", item.get("name", "")))
            if not root_name:
                continue

            orbit_raw = item.get("orbit", "وعي")
            orbit_canonical = canonical_orbit(orbit_raw)

            record = {
                "root": root_name,
                "orbit": orbit_canonical,
                "orbit_raw": orbit_raw,
                "weight": float(item.get("weight", 1.0)),
                "insight": item.get("insight", item.get("meaning", "لا توجد بصيرة مفسّرة لهذا الجذر.")),
                "meaning": item.get("meaning", item.get("insight", "لا توجد دلالة موصوفة.")),
            }

            if root_name not in r_index or record["weight"] > r_index[root_name]["weight"]:
                r_index[root_name] = record

            all_roots_flat.append(record)
            orbit_counter[orbit_canonical] += 1
    else:
        st.error("⚠️ بنية ملف الجذور غير مدعومة.")
        st.stop()

    return r_index, all_roots_flat, orbit_counter

r_index, all_roots_flat, orbit_counter = load_semantic_roots_db(roots_path)

# ==============================================================================
# [5] المِحراب السداسي - صرح البيانات (The Grand 6-Tab Architecture)
# ==============================================================================
tabs = st.tabs([
    "🔍 الاستنطاق المداري", 
    "🌌 الرنين الجيني", 
    "📈 اللوحة الوجودية", 
    "📜 البيان الختامي", 
    "⚖️ الميزان السيادي", 
    "🧠 الوعي الفوقي"
])

# --- التبويب 1: الاستنطاق ---
with tabs[0]:
    st.markdown("### 📍 هندسة المسارات المدارية")
    c1, c2, c3 = st.columns(3)
    p_in = [
        c1.text_area("المسار الوجودي (أ)", key="p_a", height=150, placeholder="أدخل النص هنا..."),
        c2.text_area("المسار الوجودي (ب)", key="p_b", height=150),
        c3.text_area("المسار الوجودي (ج)", key="p_c", height=150)
    ]
    
    if st.button("🚀 تفعيل المفاعل السيادي (v26.2.2)", use_container_width=True):
        active_bodies, word_pool, event_logs = [], [], []
        start_exec_time = time.time()
        
        for idx, text in enumerate(p_in):
            if text.strip():
                clean_text = normalize_sovereign(text)
                for word in clean_text.split():
                    root = match_root_logic(word, r_index.keys())
                    if root:
                        root_data = r_index.get(root)
                        if not root_data:
                            continue

                        # البصمة الرياضية تبقى مساعدة فقط، وليست الحاكم الأعلى
                        sig = summarize_word_signature(root)

                        orbit_name = root_data.get("orbit", "وعي")
                        orbit_raw = root_data.get("orbit_raw", orbit_name)
                        weight = float(root_data.get("weight", 1.0))
                        insight = root_data.get("insight", "لا توجد بصيرة مفسّرة لهذا الجذر.")

                        # الجين الآن مشتق من المدار الحقيقي
                        gene_key = ORBIT_TO_GENE.get(orbit_name, sig['dominant_gene'])

                        # الطاقة الحقيقية = الوزن الدلالي + لمسة رياضية ثانوية
                        semantic_energy = weight * 1000.0
                        total_energy = round(semantic_energy + (sig['total_energy'] * 0.15), 2)

                        active_bodies.append({
                            "root": root,
                            "orbit": orbit_name,
                            "orbit_raw": orbit_raw,
                            "insight": insight,
                            "weight": weight,
                            "meaning": root_data.get("meaning", insight),
                            "gene": gene_key,
                            "energy": total_energy,
                            "x": random.uniform(-10, 10),
                            "y": random.uniform(-10, 10),
                            "vx": sig['vector_x'],
                            "vy": sig['vector_y'],
                            "color": GENE_STYLE[gene_key]['color']
                        })

                        word_pool.append(root)

        if active_bodies:
            motion_ui = st.empty()
            # محاكي الفيزياء المدارية الموسع
            for _ in range(120):
                for i in range(len(active_bodies)):
                    for j in range(i+1, len(active_bodies)):
                        dist = ((active_bodies[i]['x']-active_bodies[j]['x'])**2 + (active_bodies[i]['y']-active_bodies[j]['y'])**2)**0.5
                        if dist < 1.8 and active_bodies[i]['gene'] == active_bodies[j]['gene']:
                            event_logs.append(f"[{time.strftime('%H:%M:%S')}] التحام مداري محقق: {active_bodies[i]['root']} + {active_bodies[j]['root']}")
                
                for b in active_bodies:
                    b['x'] += b['vx']; b['y'] += b['vy']
                    if abs(b['x']) > 28 or abs(b['y']) > 28: 
                        b['vx'] *= -1.0; b['vy'] *= -1.0
                
                fig_motion = px.scatter(pd.DataFrame(active_bodies), x="x", y="y", text="root", size="energy", color="gene",
                                        color_discrete_map={g:s['color'] for g,s in GENE_STYLE.items()}, range_x=[-35,35], range_y=[-35,35])
                fig_motion.update_layout(height=750, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False, xaxis_visible=False, yaxis_visible=False)
                motion_ui.plotly_chart(fig_motion, use_container_width=True)
                time.sleep(0.01)

            st.session_state.grand_monolith = {
                'active': True, 'bodies': active_bodies, 'pool': list(set(word_pool)),
                'logs': list(dict.fromkeys(event_logs))[-20:], # تصفية التكرار
                'metrics': {"duration": round(time.time()-start_exec_time, 2), "count": len(active_bodies)}
            }
            st.rerun()

# --- تفعيل الطبقات (Execution Layers) ---
state = st.session_state.grand_monolith

with tabs[1]:
    st.markdown("### 🌌 مصفوفة الرنين والاستحقاق الجيني")
    cols_genes = st.columns(5)
    for i, (gk, gi) in enumerate(GENE_STYLE.items()):
        cols_genes[i].markdown(f"""
        <div class='ultra-card' style='border-top-color:{gi['color']}'>
            <h2 style='margin:0'>{gi['icon']}</h2>
            <h3 style='margin:10px 0'>{gi['name']}</h3>
            <p style='font-size:0.9em; color:#888;'>{gi['meaning']}</p>
            <small style='display:block; margin-top:10px;'>{gi['desc']}</small>
        </div>
        """, unsafe_allow_html=True)

if state['active']:
    df_data = pd.DataFrame(state['bodies'])
    
    with tabs[2]: # اللوحة الوجودية
        st.markdown("### 📈 التحليل الكمي للمدار")
        cl, cr = st.columns(2)
        cl.plotly_chart(px.pie(df_data, names='gene', color='gene', color_discrete_map={g:s['color'] for g,s in GENE_STYLE.items()}, hole=0.5, title="توزيع الهيمنة الجينية"))
        cr.plotly_chart(px.bar(df_data.groupby('gene').size().reset_index(name='count'), x='gene', y='count', color='gene', color_discrete_map={g:s['color'] for g,s in GENE_STYLE.items()}, title="تعداد الأجسام المدارية"))
        st.plotly_chart(px.scatter(df_data, x='root', y='energy', color='gene', size='energy', color_discrete_map={g:s['color'] for g,s in GENE_STYLE.items()}, title="خارطة طاقة الجذور"))

    with tabs[3]: # البيان الختامي
        st.markdown(f"""
        <div class="story-box">
            <b>بيان الاستواء الوجودي v26.2.2:</b><br>
            بفضل الله، تم استنطاق <b>{len(state['pool'])}</b> جذراً قرآنياً بنظام القراءة الناطقة. 
            المسار الحالي يعكس اتزاناً في جينات <b>{GENE_STYLE[df_data['gene'].mode()[0]]['name']}</b>، 
            مما يؤكد مقام <b>الخير واليسر</b> في هذا المدار. كل حرف هنا هو وتدٌ في صرح التمكين.
        </div>
        """, unsafe_allow_html=True)

    with tabs[4]:  # ⚖️ الميزان السيادي v26.2.2 - Root Integrity & Insight Diagnostics
        st.markdown("### ⚖️ ميزان النزاهة الجذرية وتدقيق البصيرة")
        
        if state['active']:
            df_diag = pd.DataFrame(state['bodies'])
            
            # محرك كشف حالة البصيرة
            def diagnose_insight(row):
                root = row['root']
                # محاولة جلب البيانات الحقيقية من الفهرس
                actual_data = r_index.get(root, {})
                raw_insight = actual_data.get("insight", "")
                
                if not actual_data:
                    return "❌ جذر غير موجود في القاعدة (خارج المدار)"
                if not raw_insight or len(str(raw_insight)).strip() < 5:
                    return "⚠️ الجذر موجود ولكن حقل (insight) فارغ أو مفقود"
                return "✅ بصيرة مكتملة"
            
            df_diag['حالة البيانات'] = df_diag.apply(diagnose_insight, axis=1)
            
            # عرض جدول التشخيص
            st.dataframe(
                df_diag[['root', 'gene', 'energy', 'حالة البيانات']],
                column_config={
                    "root": "الجذر",
                    "gene": "الجين",
                    "energy": "الطاقة",
                    "حالة البيانات": "تقرير النزاهة التشخيصي"
                },
                use_container_width=True
            )
            
            # إحصائية النزاهة
            match_rate = (df_diag['حالة البيانات'] == "✅ بصيرة مكتملة").mean() * 100
            st.metric("معدل اكتمال البصيرة المدارية", f"{match_rate:.1f}%")
            
            if match_rate < 50:
                st.warning("⚠️ تنبيه: أكثر من نصف الجذور تفتقر للبصيرة. راجع مطابقة الأسماء بين النص وقاعدة البيانات.")
            
            # بصيرة سيد المدار
            top_root = df_diag.iloc[0]['root']
            top_info = r_index.get(top_root, {})
            final_insight = top_info.get("insight", "لا توجد بصيرة مفسرة مسجلة لهذا الجذر في ملفك.")
            
            st.info(f"**بصيرة سيد المدار ({top_root}):**\n\n{final_insight}")
        
        else:
            st.info("بانتظار استنطاق المدار لملء الموازين.")

    with tabs[5]: # الوعي الفوقي
        st.markdown("### 🧠 سجل الوعي المداري المستقر")
        st.markdown(f"""
        <div class="stat-container">
            <div class="stat-box"><div class="stat-val">{state['metrics']['count']}</div><div class="stat-label">أجسام مستنطقة</div></div>
            <div class="stat-box"><div class="stat-val" style="color:#ffaa00">{state['metrics']['duration']}s</div><div class="stat-label">زمن الاستقرار</div></div>
            <div class="stat-box"><div class="stat-val" style="color:#4fc3f7">{len(state['logs'])}</div><div class="stat-label">أحداث الوعي</div></div>
        </div>
        <div class="adaptive-log">{'<br>'.join(state['logs'])}</div>
        """, unsafe_allow_html=True)
else:
    for i in range(1, 6):
        with tabs[i]: st.info("المحراب في حالة انتظار... أطلق المفاعل لملء الموازين.")

# --- التذييل السيادي (Sovereign Footer) ---
st.sidebar.markdown(f"""
**المستخدم:** محمد  
**الحالة:** استواء سيادي ناطق  
**الإصدار:** v26.2.2 (Root Integrity)  
**CPU:** السجدة (5)  
---
**خِت فِت.**
""")
