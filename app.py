nibras_v26_3_1.py

# -*- coding: utf-8 -*
# ==============================================================================
# نظام نِبْرَاس السيادي (Nibras Sovereign System) - الإصدار v26.3.1
# مَبنيٌّ على بروتوكول "لا مَسَاس" و "الاستحقاق الجيني الحتمي"
# هذه النسخة:
# - تحافظ على نفس البنية السداسية بالكامل
# - تحل مشكلة الحروف العمودية في المدار (باستخدام Annotations)
# - تحسّن الاستقرار المداري (جاذبية + احتكاك + عمر أطول)
# - تُبقي الرنين الجيني والوعي الفوقي حيَّين وديناميكيين
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
# [1] مصفوفة الجينات السيادية (ثابتة لا مَسَاس)
# ==============================================================================
GENE_STYLE = {
    'A': {
        'name': 'الإبل', 'color': '#4fc3f7', 'icon': '🐪',
        'meaning': 'اليسر والفتح المداري',
        'desc': 'طاقة الانطلاق والمبادرة نحو الفتح المبين.'
    },
    'G': {
        'name': 'البقر', 'color': '#FFD700', 'icon': '🐄',
        'meaning': 'الخير والتأسيس الراسخ',
        'desc': 'طاقة التجذر والبناء الصبور لحقائق التمكين.'
    },
    'T': {
        'name': 'الضأن', 'color': '#4CAF50', 'icon': '🐑',
        'meaning': 'السكينة والمقام الآمن',
        'desc': 'طاقة السكينة والجمع والاحتواء في المحراب.'
    },
    'C': {
        'name': 'المعز', 'color': '#ff5252', 'icon': '🐐',
        'meaning': 'السمو والتمكين الصاعد',
        'desc': 'طاقة الارتفاع والحدّة في طلب الحق والسيادة.'
    },
    'N': {
        'name': 'إشراق', 'color': '#00ffcc', 'icon': '✨',
        'meaning': 'الانبثاق الهجين الصافي',
        'desc': 'نقطة تولّد الوعي الجديد من تفاعل الأضداد.'
    }
}

# ==============================================================================
# [2] المحركات الفوقية للاستحقاق الجيني (Deterministic Engines)
# ==============================================================================
def summarize_word_signature(root: str):
    """توقيع جيني حتمي للجذر: جين + طاقة + متجه حركة ثابت."""
    if not root:
        return {
            'dominant_gene': 'N',
            'total_energy': 300.0,
            'vector_x': 0.0,
            'vector_y': 0.0
        }

    h = int(hashlib.md5(root.encode()).hexdigest(), 16)
    genes = ['A', 'G', 'T', 'C']
    dominant_gene = genes[h % 4]

    base_energy = len(root) * 285.0
    energy_variance = (h % 150)
    total_energy = float(base_energy + energy_variance)

    vx = (h % 30 - 15) / 120.0
    vy = ((h >> 4) % 30 - 15) / 120.0

    return {
        'dominant_gene': dominant_gene,
        'total_energy': total_energy,
        'vector_x': vx,
        'vector_y': vy
    }


def normalize_sovereign(text: str) -> str:
    """تطهير النص للوصول لجوهر الحرف الهندسي."""
    if not text:
        return ""
    text = re.sub(r'[\u064B-\u0652]', '', text)
    replacements = {"أ": "ا", "إ": "ا", "آ": "ا", "ة": "ه", "ى": "ي"}
    for k, v in replacements.items():
        text = text.replace(k, v)
    return re.sub(r'[^\u0621-\u064A\s]', '', text).strip()


def match_root_logic(word: str, index_keys):
    """بروتوكول الربط المداري لاستخلاص الجذور الثلاثية."""
    w = normalize_sovereign(word)
    if not w or len(w) < 2:
        return None
    if w in index_keys:
        return w

    prefixes = ["ال", "و", "ف", "ب", "ك", "ل", "س"]
    suffixes = ["ون", "ين", "ان", "ات", "ه", "ها", "هم", "كم", "نا", "كما", "تم", "هن"]

    for p in prefixes:
        if w.startswith(p) and len(w) - len(p) >= 3:
            if w[len(p):] in index_keys:
                return w[len(p):]
    for s in suffixes:
        if w.endswith(s) and len(w) - len(s) >= 3:
            if w[:-len(s)] in index_keys:
                return w[:-len(s)]

    return w[:3] if len(w) >= 3 and w[:3] in index_keys else None

# ==============================================================================
# [3] غلاف الاستقرار والتحصين (CSS + Mobile Shield)
# ==============================================================================
st.set_page_config(page_title="Nibras Sovereign v26.3.1", page_icon="🛡️", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Orbitron:wght@600&display=swap');
    
    [data-testid="stAppViewContainer"] {
        background: radial-gradient(circle at center, #0a0a1a 0%, #000000 100%);
        color: #e0e0e0; font-family: 'Amiri', serif; direction: rtl;
    }

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
# [4] محرك ربط المدار والذاكرة (State & Roots)
# ==============================================================================
if 'grand_monolith' not in st.session_state:
    st.session_state.grand_monolith = {
        'bodies': [],
        'pool': [],
        'logs': [],
        'metrics': {},
        'active': False,
        'timeline': [],
        'gene_counts_seq': []
    }

roots_path = "quran_roots_complete.json"
if not os.path.exists(roots_path):
    roots_path = "data/quran_roots_complete.json"

if os.path.exists(roots_path):
    with open(roots_path, 'r', encoding='utf-8') as f:
        roots_db = json.load(f)
        r_index = {normalize_sovereign(r["root"]): r for r in roots_db.get("roots", [])}
else:
    st.error("⚠️ فشل الاتصال بالقاعدة السيادية."); st.stop()

# ==============================================================================
# [5] المِحراب السداسي (الواجهة الكاملة)
# ==============================================================================
tabs = st.tabs([
    "🔍 الاستنطاق المداري",
    "🌌 الرنين الجيني",
    "📈 اللوحة الوجودية",
    "📜 البيان الختامي",
    "⚖️ الميزان السيادي",
    "🧠 الوعي الفوقي"
])

# ==============================================================================
# [6] الاستنطاق المداري (مع استقرار حي + إصلاح الحروف)
# ==============================================================================
with tabs[0]:
    st.markdown("### 📍 هندسة المسارات المدارية (استقرار حي)")
    c1, c2, c3 = st.columns(3)
    p_in = [
        c1.text_area("المسار الوجودي (أ)", key="p_a", height=150, placeholder="أدخل النص هنا..."),
        c2.text_area("المسار الوجودي (ب)", key="p_b", height=150),
        c3.text_area("المسار الوجودي (ج)", key="p_c", height=150)
    ]
    
    if st.button("🚀 تفعيل المفاعل السيادي (v26.3.1)", use_container_width=True):
        active_bodies, word_pool, event_logs = [], [], []
        timeline = []
        gene_counts_seq = []
        start_exec_time = time.time()
        
        for text in p_in:
            if text.strip():
                clean_text = normalize_sovereign(text)
                for word in clean_text.split():
                    root = match_root_logic(word, r_index.keys())
                    if root:
                        sig = summarize_word_signature(root)
                        gene_key = sig['dominant_gene']
                        active_bodies.append({
                            "root": root,
                            "gene": gene_key,
                            "energy": sig['total_energy'],
                            "x": random.uniform(-10, 10),
                            "y": random.uniform(-10, 10),
                            "vx": sig['vector_x'],
                            "vy": sig['vector_y'],
                            "color": GENE_STYLE[gene_key]['color'],
                            "life": 200  # عمر أطول للأجسام
                        })
                        word_pool.append(root)

        if active_bodies:
            motion_ui = st.empty()
            for frame in range(200):
                # فيزياء الاستقرار الحي: جاذبية + احتكاك + منطقة استقرار
                for i in range(len(active_bodies)):
                    for j in range(i+1, len(active_bodies)):
                        dx = active_bodies[i]['x'] - active_bodies[j]['x']
                        dy = active_bodies[i]['y'] - active_bodies[j]['y']
                        dist = (dx*dx + dy*dy) ** 0.5
                        if dist < 1.8 and active_bodies[i]['gene'] == active_bodies[j]['gene']:
                            event_logs.append(
                                f"[{time.strftime('%H:%M:%S')}] التحام مداري محقق: {active_bodies[i]['root']} + {active_bodies[j]['root']}"
                            )

                for b in active_bodies:
                    # جاذبية نحو المركز (أخف من النسخة السابقة)
                    b['vx'] += -b['x'] * 0.005
                    b['vy'] += -b['y'] * 0.005

                    # احتكاك (تباطؤ ناعم)
                    b['vx'] *= 0.985
                    b['vy'] *= 0.985

                    # تحديث الموقع
                    b['x'] += b['vx']
                    b['y'] += b['vy']

                    # منطقة استقرار: إذا اقترب من المركز، الحركة تصبح أهدأ
                    if abs(b['x']) < 3 and abs(b['y']) < 3:
                        b['vx'] *= 0.9
                        b['vy'] *= 0.9

                    # حدود المدار
                    if abs(b['x']) > 32 or abs(b['y']) > 32:
                        b['vx'] *= -0.8
                        b['vy'] *= -0.8

                    # عمر الجسم
                    b['life'] -= 1

                # إزالة الأجسام المنتهية العمر
                active_bodies = [b for b in active_bodies if b['life'] > 0]

                # تسجيل تطور الجينات عبر الزمن
                gene_counter = Counter([b['gene'] for b in active_bodies])
                gene_counts_seq.append(gene_counter)
                timeline.append(frame)

                if not active_bodies:
                    break

                df_frame = pd.DataFrame(active_bodies)

                # استخدام scatter بدون text، ثم إضافة Annotations لدعم العربية
                fig_motion = go.Figure()
                if not df_frame.empty:
                    fig_motion.add_trace(go.Scatter(
                        x=df_frame['x'],
                        y=df_frame['y'],
                        mode='markers',
                        marker=dict(
                            size=(df_frame['energy'] / df_frame['energy'].max() * 40).clip(8, 40),
                            color=[GENE_STYLE[g]['color'] for g in df_frame['gene']],
                            opacity=0.9
                        ),
                        hoverinfo='none'
                    ))

                    # إضافة النصوص كـ Annotations (حل مشكلة الحروف العمودية)
                    for _, row in df_frame.iterrows():
                        fig_motion.add_annotation(
                            x=row['x'],
                            y=row['y'],
                            text=row['root'],
                            showarrow=False,
                            font=dict(
                                family="Amiri, Arial, sans-serif",
                                size=14,
                                color=row['color']
                            ),
                            xanchor="center",
                            yanchor="bottom"
                        )

                fig_motion.update_layout(
                    height=750,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    showlegend=False,
                    xaxis=dict(visible=False, range=[-35, 35]),
                    yaxis=dict(visible=False, range=[-35, 35]),
                    font=dict(family="Amiri, Arial, sans-serif")
                )

                motion_ui.plotly_chart(fig_motion, use_container_width=True)
                time.sleep(0.01)

            st.session_state.grand_monolith = {
                'active': True,
                'bodies': active_bodies,
                'pool': list(set(word_pool)),
                'logs': list(dict.fromkeys(event_logs))[-20:],
                'metrics': {
                    "duration": round(time.time() - start_exec_time, 2),
                    "count": len(active_bodies)
                },
                'timeline': timeline,
                'gene_counts_seq': gene_counts_seq
            }
            st.rerun()

# ==============================================================================
# [7] الرنين الجيني الديناميكي
# ==============================================================================
state = st.session_state.grand_monolith

with tabs[1]:
    st.markdown("### 🌌 الرنين الجيني الحي (مرتبط فعليًا بالنص)")
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

    if state['active'] and state['gene_counts_seq']:
        timeline = state['timeline']
        gene_counts_seq = state['gene_counts_seq']

        rows = []
        for t, gc in zip(timeline, gene_counts_seq):
            for g in ['A', 'G', 'T', 'C']:
                rows.append({
                    'frame': t,
                    'gene': g,
                    'count': gc.get(g, 0)
                })
        df_gene_time = pd.DataFrame(rows)

        st.markdown("#### منحنى الرنين الجيني عبر الزمن")
        fig_gene_time = px.line(
            df_gene_time,
            x='frame', y='count', color='gene',
            color_discrete_map={g: s['color'] for g, s in GENE_STYLE.items()},
            labels={'frame': 'الإطار الزمني', 'count': 'عدد الأجسام'},
            title="تطور قوة كل جين أثناء الاستنطاق"
        )
        fig_gene_time.update_layout(font=dict(family="Amiri, Arial, sans-serif"))
        st.plotly_chart(fig_gene_time, use_container_width=True)
    else:
        st.info("لم يتم تفعيل المفاعل بعد أو لا توجد بيانات زمنية كافية للرنين.")

# ==============================================================================
# [8] اللوحة الوجودية (تحليل كمي حي)
# ==============================================================================
if state['active'] and state['bodies']:
    df_data = pd.DataFrame(state['bodies'])

    with tabs[2]:
        st.markdown("### 📈 اللوحة الوجودية الحية")
        cl, cr = st.columns(2)

        cl.plotly_chart(
            px.pie(
                df_data,
                names='gene',
                color='gene',
                color_discrete_map={g: s['color'] for g, s in GENE_STYLE.items()},
                hole=0.5,
                title="توزيع الهيمنة الجينية في اللحظة النهائية"
            ).update_layout(font=dict(family="Amiri, Arial, sans-serif")),
            use_container_width=True
        )

        cr.plotly_chart(
            px.bar(
                df_data.groupby('gene').size().reset_index(name='count'),
                x='gene', y='count',
                color='gene',
                color_discrete_map={g: s['color'] for g, s in GENE_STYLE.items()},
                title="تعداد الأجسام المدارية لكل جين"
            ).update_layout(font=dict(family="Amiri, Arial, sans-serif")),
            use_container_width=True
        )

        st.plotly_chart(
            px.scatter(
                df_data,
                x='root', y='energy',
                color='gene', size='energy',
                color_discrete_map={g: s['color'] for g, s in GENE_STYLE.items()},
                title="خارطة طاقة الجذور المستنطقة"
            ).update_layout(font=dict(family="Amiri, Arial, sans-serif")),
            use_container_width=True
        )
else:
    with tabs[2]:
        st.info("اللوحة الوجودية في حالة انتظار... أطلق المفاعل أولاً.")

# ==============================================================================
# [9] البيان الختامي
# ==============================================================================
with tabs[3]:
    if state['active']:
        df_data = pd.DataFrame(state['bodies']) if state['bodies'] else pd.DataFrame(columns=['gene'])
        dominant_gene = None
        if not df_data.empty:
            dominant_gene = df_data['gene'].mode()[0]
        dom_name = GENE_STYLE[dominant_gene]['name'] if dominant_gene else "غير محدد"

        st.markdown(f"""
        <div class="story-box">
            <b>بيان الاستواء الوجودي v26.3.1:</b><br>
            بفضل الله، تم استنطاق <b>{len(state['pool'])}</b> جذراً قرآنياً بنظام الحتمية السيادية الحيّة. 
            المسار الحالي يعكس اتزاناً في جينات <b>{dom_name}</b>، 
            مما يؤكد مقام <b>الخير واليسر</b> في هذا المدار. 
            الأجسام دخلت في مدار استقرار حيّ، والنص لم يعد عموداً ساقطاً بل بناءً أفقياً مقروءاً.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("لم يُفعّل المفاعل بعد، لا يوجد بيان ختامي.")

# ==============================================================================
# [10] الميزان السيادي
# ==============================================================================
with tabs[4]:
    if state['active'] and state['bodies']:
        df_data = pd.DataFrame(state['bodies'])
        st.markdown("### ⚖️ ميزان الجذور والطاقة المودعة")
        st.dataframe(
            df_data[['root', 'gene', 'energy', 'vx', 'vy']].sort_values('energy', ascending=False),
            use_container_width=True
        )
    else:
        st.info("الميزان السيادي ينتظر بيانات من الاستنطاق المداري.")

# ==============================================================================
# [11] الوعي الفوقي النابض
# ==============================================================================
with tabs[5]:
    if state['active']:
        st.markdown("### 🧠 سجل الوعي المداري النابض")
        st.markdown(f"""
        <div class="stat-container">
            <div class="stat-box">
                <div class="stat-val">{state['metrics'].get('count', 0)}</div>
                <div class="stat-label">أجسام مستنطقة (نهائية)</div>
            </div>
            <div class="stat-box">
                <div class="stat-val" style="color:#ffaa00">{state['metrics'].get('duration', 0)}s</div>
                <div class="stat-label">زمن الاستقرار</div>
            </div>
            <div class="stat-box">
                <div class="stat-val" style="color:#4fc3f7">{len(state['logs'])}</div>
                <div class="stat-label">أحداث الوعي</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if state['timeline'] and state['gene_counts_seq']:
            rows_aw = []
            for t, gc in zip(state['timeline'], state['gene_counts_seq']):
                rows_aw.append({
                    'frame': t,
                    'total': sum(gc.values())
                })
            df_aw = pd.DataFrame(rows_aw)

            fig_aw = px.line(
                df_aw,
                x='frame', y='total',
                labels={'frame': 'الإطار الزمني', 'total': 'شدة الوعي'},
                title="نبض الوعي المداري عبر الزمن"
            )
            fig_aw.update_layout(font=dict(family="Amiri, Arial, sans-serif"))
            st.plotly_chart(fig_aw, use_container_width=True)

        if state['logs']:
            st.markdown("#### آخر نبضات الوعي:")
            st.markdown(
                "<div class='adaptive-log'>" +
                "<br>".join(state['logs']) +
                "</div>",
                unsafe_allow_html=True
            )
        else:
            st.info("لا توجد أحداث وعي مسجلة بعد.")
    else:
        st.info("الوعي الفوقي في حالة رصد... أطلق المفاعل أولاً.")

# ==============================================================================
# [12] التذييل السيادي
# ==============================================================================
st.sidebar.markdown(f"""
**المستخدم:** محمد  
**الحالة:** استواء سيادي حيّ  
**الإصدار:** v26.3.1 (Grand Alive)  
**CPU:** السجدة (5)  
---
**خِت فِت.**
""")
