# -*- coding: utf-8 -*-
# Nibras Sovereign v26.4 – Root-Stable Edition (Main app.py)

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import re, random, os, json, time, hashlib
from pathlib import Path

# =========================[ 1. PAGE CONFIG ]===================================
st.set_page_config(
    page_title="Nibras Sovereign v26.4",
    page_icon="🛡️",
    layout="wide"
)

# =========================[ 2. GENES ]=========================================
GENE_STYLE = {
    'A': {'name': 'الإبل', 'color': '#4fc3f7', 'icon': '🐪',
          'meaning': 'اليسر والفتح المداري'},
    'G': {'name': 'البقر', 'color': '#FFD700', 'icon': '🐄',
          'meaning': 'الخير والتأسيس الراسخ'},
    'T': {'name': 'الضأن', 'color': '#4CAF50', 'icon': '🐑',
          'meaning': 'السكينة والمقام الآمن'},
    'C': {'name': 'المعز', 'color': '#ff5252', 'icon': '🐐',
          'meaning': 'السمو والتمكين الصاعد'},
    'N': {'name': 'إشراق', 'color': '#00ffcc', 'icon': '✨',
          'meaning': 'الانبثاق الهجين الصافي'},
}

# =========================[ 3. ENGINE: NORMALIZATION ]=========================
def normalize_sovereign(text: str) -> str:
    if not text:
        return ""
    text = str(text)

    # إزالة التشكيل الأشمل
    text = re.sub(r'[\u0617-\u061A\u064B-\u0652\u0670]', '', text)

    # توحيد الحروف
    rep = {
        "أ": "ا", "إ": "ا", "آ": "ا",
        "ة": "ه",
        "ى": "ي",
        "ؤ": "و",
        "ئ": "ي"
    }
    for k, v in rep.items():
        text = text.replace(k, v)

    # الإبقاء على العربية + المسافة
    text = re.sub(r'[^\u0621-\u064A\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# =========================[ 4. ENGINE: ROOT CANDIDATES ]=======================
PREFIXES = ["وال", "فال", "بال", "كال", "لل", "ال", "و", "ف", "ب", "ك", "ل", "س"]
SUFFIXES = ["هما", "كما", "كم", "كن", "هم", "هن", "نا", "ها", "ه", "ات", "ان", "ون", "ين", "يه", "ية", "ي", "ة", "ا"]

def strip_prefixes(word: str):
    candidates = {word}
    for p in PREFIXES:
        if word.startswith(p) and len(word) - len(p) >= 2:
            candidates.add(word[len(p):])
    return candidates

def strip_suffixes(word: str):
    candidates = {word}
    for s in SUFFIXES:
        if word.endswith(s) and len(word) - len(s) >= 2:
            candidates.add(word[:-len(s)])
    return candidates

def generate_root_candidates(word: str):
    """
    توليد مرشحات جذرية أقوى من القصّ الأعمى w[:3]
    """
    w = normalize_sovereign(word)
    if not w:
        return []

    candidates = {w}

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

    # إزالة سوابق + لواحق
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

    # أخذ جميع الثلاثيات الممكنة (بدل أول ثلاثي فقط)
    tri_forms = set()
    for form in list(candidates):
        if len(form) >= 3:
            for i in range(len(form) - 2):
                tri_forms.add(form[i:i+3])
    candidates.update(tri_forms)

    # فلترة نهائية
    final = []
    for c in candidates:
        c = normalize_sovereign(c)
        if 2 <= len(c) <= 6:
            final.append(c)

    # الأطول أولًا ثم أبجديًا
    final = sorted(set(final), key=lambda x: (-len(x), x))
    return final

def match_root_logic(word: str, index_keys):
    """
    مطابقة جذرية أكثر استقرارًا:
    1) مطابقة كاملة
    2) مطابقة ثلاثية ضمن المرشحات
    """
    candidates = generate_root_candidates(word)

    # مطابقة كاملة أولًا
    for c in candidates:
        if c in index_keys:
            return c

    # ثم ثلاثي فقط
    for c in candidates:
        if len(c) == 3 and c in index_keys:
            return c

    return None

# =========================[ 5. ENGINE: SIGNATURE ]=============================
def summarize_word_signature(root: str):
    """
    توقيع رمزي ثابت Stable Hash Signature
    """
    if not root:
        return {'dominant_gene': 'N', 'total_energy': 200.0, 'vx': 0.0, 'vy': 0.0}

    h = int(hashlib.md5(root.encode("utf-8")).hexdigest(), 16)
    genes = ['A', 'G', 'T', 'C']
    g = genes[h % 4]

    base = len(root) * 220.0
    var = (h % 120)
    energy = float(base + var)

    vx = (h % 30 - 15) / 120.0
    vy = ((h >> 4) % 30 - 15) / 120.0

    return {
        'dominant_gene': g,
        'total_energy': energy,
        'vx': vx,
        'vy': vy
    }

# =========================[ 6. LOAD ROOTS SAFELY ]=============================
@st.cache_data(show_spinner=False)
def load_roots_db():
    search_paths = [
        Path("quran_roots_complete.json"),
        Path("data") / "quran_roots_complete.json",
        Path(".") / "quran_roots_complete.json"
    ]

    roots_path = None
    for p in search_paths:
        if p.exists():
            roots_path = p
            break

    if roots_path is None:
        return None, None, None

    try:
        with open(roots_path, 'r', encoding='utf-8') as f:
            roots_db = json.load(f)
    except Exception as e:
        return None, None, f"تعذر قراءة ملف الجذور: {e}"

    r_index = {}
    roots_list = roots_db.get("roots", [])

    if not isinstance(roots_list, list):
        return None, None, "بنية ملف الجذور غير صحيحة: المفتاح roots ليس قائمة."

    for r in roots_list:
        if not isinstance(r, dict):
            continue
        raw_root = r.get("root", "")
        nr = normalize_sovereign(raw_root)
        if nr:
            r_index[nr] = r

    return roots_db, r_index, str(roots_path)

roots_db, r_index, roots_info = load_roots_db()

if roots_db is None or r_index is None:
    st.error(f"⚠️ ملف الجذور quran_roots_complete.json غير متاح أو تالف.\n\n{roots_info if roots_info else ''}")
    st.stop()

# =========================[ 7. CSS ]===========================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Orbitron:wght@600&display=swap');

[data-testid="stAppViewContainer"]{
  background:radial-gradient(circle at center,#050510 0%,#000000 100%);
  color:#e0e0e0;
  font-family:'Amiri',serif;
  direction:rtl;
}

.main .block-container{padding-top:1.5rem;}

.story-box{
  background:linear-gradient(135deg,rgba(10,21,10,0.9),rgba(1,1,3,0.98));
  padding:32px;
  border-radius:22px;
  border-right:10px solid #4CAF50;
  line-height:2.2;
  font-size:1.3em;
  box-shadow:0 18px 45px rgba(0,0,0,0.8);
}

.stat-container{
  display:flex;
  justify-content:space-around;
  background:#05050b;
  padding:22px;
  border-radius:18px;
  border:1px solid #1a1a2a;
  margin:18px 0;
}

.stat-box{text-align:center;}

.stat-val{
  font-size:2.4em;
  font-weight:bold;
  color:#00ffcc;
  font-family:'Orbitron',sans-serif;
}

.stat-label{
  color:#aaa;
  font-size:0.95em;
  margin-top:4px;
}

.ultra-card{
  background:#05050b;
  padding:20px;
  border-radius:16px;
  border-top:6px solid #4fc3f7;
  text-align:center;
  transition:all .3s;
  margin-bottom:16px;
}

.ultra-card:hover{
  transform:translateY(-4px);
  background:#0c0c16;
}

.adaptive-log{
  background:#000;
  border:1px solid #ffaa00;
  padding:16px;
  color:#ffaa00;
  font-family:'Courier New',monospace;
  height:260px;
  overflow-y:auto;
  border-radius:14px;
  font-size:0.85em;
}

.status-box{
  background:#08120d;
  border:1px solid #183c25;
  padding:12px;
  border-radius:12px;
  margin:10px 0;
}

@media (max-width:768px){
  .story-box{font-size:1.1em;padding:22px;}
  .stat-val{font-size:1.8em;}
}
</style>
""", unsafe_allow_html=True)

# =========================[ 8. STATE ]=========================================
if 'grand_monolith' not in st.session_state:
    st.session_state.grand_monolith = {
        'bodies': [],
        'pool': [],
        'logs': [],
        'metrics': {},
        'timeline': [],
        'gene_counts_seq': [],
        'active': False,
        'roots_path': roots_info
    }

state = st.session_state.grand_monolith

# =========================[ 9. HEADER STATUS ]=================================
st.markdown("## 🛡️ Nibras Sovereign v26.4 – Root-Stable Edition")
st.markdown(
    f"""
    <div class="status-box">
        <b>ملف الجذور المحمّل:</b> {roots_info}<br>
        <b>عدد الجذور المفهرسة:</b> {len(r_index)}
    </div>
    """,
    unsafe_allow_html=True
)

# =========================[ 10. TABS ]=========================================
tabs = st.tabs([
    "🔍 الاستنطاق المداري",
    "🌌 الرنين الجيني",
    "📈 اللوحة الوجودية",
    "📜 البيان الختامي",
    "⚖️ الميزان السيادي",
    "🧠 الوعي الفوقي"
])

# =========================[ 11. ORBITAL INFERENCE ]============================
with tabs[0]:
    st.markdown("### 🔍 الاستنطاق المداري – تشغيل المفاعل السيادي")

    c1, c2, c3 = st.columns(3)
    t1 = c1.text_area("المسار الوجودي (أ)", height=150, key="p_a",
                      placeholder="أدخل نصًا عربيًا متنوعًا…")
    t2 = c2.text_area("المسار الوجودي (ب)", height=150, key="p_b")
    t3 = c3.text_area("المسار الوجودي (ج)", height=150, key="p_c")

    opt1, opt2, opt3 = st.columns(3)
    with opt1:
        animate = st.checkbox("🎞️ تفعيل الحركة الحية", value=False)
    with opt2:
        max_frames = st.slider("عدد الإطارات", min_value=20, max_value=90, value=45, step=5)
    with opt3:
        frame_delay = st.slider("زمن الإطار", min_value=0.0, max_value=0.05, value=0.0, step=0.01)

    if st.button("🚀 تفعيل المفاعل (v26.4 – Root-Stable)", use_container_width=True):
        texts = [t1, t2, t3]
        active_bodies = []
        pool = []
        logs = []
        timeline = []
        gene_counts_seq = []
        start_time = time.time()

        # استخراج الجذور
        for txt in texts:
            if not txt or not txt.strip():
                continue

            clean = normalize_sovereign(txt)
            for w in clean.split():
                root = match_root_logic(w, r_index.keys())
                if not root:
                    continue

                sig = summarize_word_signature(root)
                g = sig['dominant_gene']

                body = {
                    "root": root,
                    "gene": g,
                    "energy": sig['total_energy'],
                    "x": random.uniform(-10, 10),
                    "y": random.uniform(-10, 10),
                    "vx": sig['vx'],
                    "vy": sig['vy'],
                    "color": GENE_STYLE[g]['color'],
                    "life": max_frames + 40,
                }

                active_bodies.append(body)
                pool.append(root)

        # لا توجد أجسام
        if not active_bodies:
            state.update({
                'bodies': [],
                'pool': [],
                'logs': ["[SYSTEM] لم يتم التقاط أي جذور من النص المدخل."],
                'metrics': {
                    "duration": round(time.time() - start_time, 2),
                    "count": 0
                },
                'timeline': [],
                'gene_counts_seq': [],
                'active': True,
                'roots_path': roots_info
            })
            st.warning("لم يتم التقاط أي جذور من النص. جرّب نصًا قرآنيًا أو عربيًا أكثر تنوعًا.")
            st.stop()

        # نحتفظ بلقطة أولية
        snapshot_initial = [b.copy() for b in active_bodies]

        motion_placeholder = st.empty()

        # إذا كانت الحركة غير مفعلة، سننفذ المحاكاة بصمت ثم نعرض النتيجة النهائية فقط
        frames_to_run = max_frames if animate else min(18, max_frames)

        for frame in range(frames_to_run):
            # تصادمات بسيطة + تسجيل أحداث
            for i in range(len(active_bodies)):
                for j in range(i + 1, len(active_bodies)):
                    dx = active_bodies[i]['x'] - active_bodies[j]['x']
                    dy = active_bodies[i]['y'] - active_bodies[j]['y']
                    dist2 = dx * dx + dy * dy

                    if dist2 < 4.0 and active_bodies[i]['gene'] == active_bodies[j]['gene']:
                        logs.append(
                            f"[{time.strftime('%H:%M:%S')}] التحام مداري: "
                            f"{active_bodies[i]['root']} + {active_bodies[j]['root']}"
                        )

            # تحديث الفيزياء
            for b in active_bodies:
                # جاذبية نحو المركز
                b['vx'] += -b['x'] * 0.004
                b['vy'] += -b['y'] * 0.004

                # احتكاك
                b['vx'] *= 0.987
                b['vy'] *= 0.987

                # تحديث الموقع
                b['x'] += b['vx']
                b['y'] += b['vy']

                # منطقة استقرار
                if abs(b['x']) < 3 and abs(b['y']) < 3:
                    b['vx'] *= 0.9
                    b['vy'] *= 0.9

                # حدود المدار
                if abs(b['x']) > 32 or abs(b['y']) > 32:
                    b['vx'] *= -0.7
                    b['vy'] *= -0.7

                # عمر
                b['life'] -= 1

            active_bodies = [b for b in active_bodies if b['life'] > 0]

            # تسجيل الرنين
            gene_counter = Counter([b['gene'] for b in active_bodies])
            gene_counts_seq.append(gene_counter)
            timeline.append(frame)

            # الرسم فقط إذا الحركة مفعلة
            if animate:
                df_frame = pd.DataFrame(active_bodies)
                fig = go.Figure()

                if not df_frame.empty:
                    fig.add_trace(go.Scatter(
                        x=df_frame['x'],
                        y=df_frame['y'],
                        mode='markers',
                        marker=dict(
                            size=(df_frame['energy'] / df_frame['energy'].max() * 38).clip(8, 38),
                            color=df_frame['color'],
                            opacity=0.9
                        ),
                        hoverinfo='none'
                    ))

                    for _, row in df_frame.iterrows():
                        fig.add_annotation(
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

                fig.update_layout(
                    height=650,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    xaxis=dict(visible=False, range=[-35, 35]),
                    yaxis=dict(visible=False, range=[-35, 35]),
                    showlegend=False,
                    font=dict(family="Amiri, Arial, sans-serif")
                )

                motion_placeholder.plotly_chart(fig, use_container_width=True)

                if frame_delay > 0:
                    time.sleep(frame_delay)

            if not active_bodies:
                break

        # إذا الحركة غير مفعلة، اعرض الشكل النهائي مرة واحدة فقط
        if not animate:
            final_preview = active_bodies if active_bodies else snapshot_initial
            df_frame = pd.DataFrame(final_preview)
            fig = go.Figure()

            if not df_frame.empty:
                fig.add_trace(go.Scatter(
                    x=df_frame['x'],
                    y=df_frame['y'],
                    mode='markers',
                    marker=dict(
                        size=(df_frame['energy'] / df_frame['energy'].max() * 38).clip(8, 38),
                        color=df_frame['color'],
                        opacity=0.9
                    ),
                    hoverinfo='none'
                ))

                for _, row in df_frame.iterrows():
                    fig.add_annotation(
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

            fig.update_layout(
                height=650,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(visible=False, range=[-35, 35]),
                yaxis=dict(visible=False, range=[-35, 35]),
                showlegend=False,
                font=dict(family="Amiri, Arial, sans-serif")
            )

            motion_placeholder.plotly_chart(fig, use_container_width=True)

        # النتيجة النهائية
        final_bodies = active_bodies if active_bodies else snapshot_initial

        # تنظيف السجلات
        logs = list(dict.fromkeys(logs))[-40:]
        if not logs:
            logs = ["[SYSTEM] مدار مستقر، لم تُسجّل التحامات حادة."]

        state.update({
            'bodies': final_bodies,
            'pool': sorted(set(pool)),
            'logs': logs,
            'metrics': {
                "duration": round(time.time() - start_time, 2),
                "count": len(final_bodies),
                "animate": animate,
                "frames": len(timeline)
            },
            'timeline': timeline,
            'gene_counts_seq': gene_counts_seq,
            'active': True,
            'roots_path': roots_info
        })

        st.success("تم تفعيل المفاعل وتسجيل المدار بنجاح.")
        st.rerun()

# =========================[ 12. GENE RESONANCE ]===============================
with tabs[1]:
    st.markdown("### 🌌 الرنين الجيني الحي")

    cols = st.columns(5)
    for i, (gk, gi) in enumerate(GENE_STYLE.items()):
        cols[i].markdown(
            f"<div class='ultra-card' style='border-top-color:{gi['color']}'>"
            f"<div style='font-size:1.8em'>{gi['icon']}</div>"
            f"<div style='font-weight:bold;margin-top:4px'>{gi['name']}</div>"
            f"<div style='font-size:0.85em;color:#aaa;margin-top:6px'>{gi['meaning']}</div>"
            f"</div>",
            unsafe_allow_html=True
        )

    if state['active'] and state['timeline'] and state['gene_counts_seq']:
        rows = []
        for t, gc in zip(state['timeline'], state['gene_counts_seq']):
            for g in ['A', 'G', 'T', 'C']:
                rows.append({'frame': t, 'gene': g, 'count': gc.get(g, 0)})

        df_gt = pd.DataFrame(rows)

        if not df_gt.empty:
            fig_gt = px.line(
                df_gt,
                x='frame',
                y='count',
                color='gene',
                color_discrete_map={g: GENE_STYLE[g]['color'] for g in ['A', 'G', 'T', 'C']},
                labels={'frame': 'الإطار الزمني', 'count': 'عدد الأجسام'},
                title="تطور قوة كل جين أثناء المدار"
            )
            fig_gt.update_layout(font=dict(family="Amiri, Arial, sans-serif"))
            st.plotly_chart(fig_gt, use_container_width=True)
        else:
            st.info("لا توجد بيانات كافية للرنين الزمني بعد.")
    else:
        st.info("فعّل الاستنطاق المداري أولًا لتظهر موجة الرنين.")

# =========================[ 13. EXISTENTIAL PANEL ]============================
with tabs[2]:
    st.markdown("### 📈 اللوحة الوجودية")

    if state['active'] and state['bodies']:
        df = pd.DataFrame(state['bodies'])
        c1, c2 = st.columns(2)

        # Pie
        c1.plotly_chart(
            px.pie(
                df,
                names='gene',
                color='gene',
                color_discrete_map={g: GENE_STYLE[g]['color'] for g in ['A', 'G', 'T', 'C']},
                hole=0.5,
                title="توزيع الهيمنة الجينية"
            ).update_layout(font=dict(family="Amiri, Arial, sans-serif")),
            use_container_width=True
        )

        # Bar
        gene_counts_df = df.groupby('gene').size().reset_index(name='count')
        c2.plotly_chart(
            px.bar(
                gene_counts_df,
                x='gene',
                y='count',
                color='gene',
                color_discrete_map={g: GENE_STYLE[g]['color'] for g in ['A', 'G', 'T', 'C']},
                title="عدد الأجسام لكل جين"
            ).update_layout(font=dict(family="Amiri, Arial, sans-serif")),
            use_container_width=True
        )

        # Energy map
        st.plotly_chart(
            px.scatter(
                df,
                x='root',
                y='energy',
                color='gene',
                size='energy',
                color_discrete_map={g: GENE_STYLE[g]['color'] for g in ['A', 'G', 'T', 'C']},
                title="خارطة طاقة الجذور"
            ).update_layout(font=dict(family="Amiri, Arial, sans-serif")),
            use_container_width=True
        )
    else:
        st.info("اللوحة الوجودية تنتظر مدارًا واحدًا على الأقل من الاستنطاق.")

# =========================[ 14. FINAL STATEMENT ]==============================
with tabs[3]:
    st.markdown("### 📜 البيان الختامي")

    if state['active']:
        df = pd.DataFrame(state['bodies']) if state['bodies'] else pd.DataFrame(columns=['gene'])

        if not df.empty:
            dom_gene = df['gene'].mode()[0]
            dom_name = GENE_STYLE[dom_gene]['name']
        else:
            dom_gene, dom_name = None, "غير محدد"

        st.markdown(f"""
        <div class="story-box">
        بفضل الله، تم استنطاق <b>{len(state['pool'])}</b> جذراً قرآنياً/لغوياً
        ضمن مدار سيادي مستقر في هذه الجلسة.<br><br>

        يشير الميزان الجيني إلى غلبة مقام <b>{dom_name}</b>،
        بما يعكس طيفًا خاصًا من الاستحقاق في هذا النص.<br><br>

        زمن الاستقرار المداري المسجّل: <b>{state['metrics'].get('duration', 0)} ثانية</b>،
        بعدد أجسام نهائية قدره <b>{state['metrics'].get('count', 0)}</b> جسمًا مداريًا.<br><br>

        وضع الحركة: <b>{"مفعّل" if state['metrics'].get('animate') else "هادئ / ثابت"}</b> —
        عدد الإطارات المسجّلة: <b>{state['metrics'].get('frames', 0)}</b>.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("لا يوجد بيان ختامي قبل تشغيل الاستنطاق المداري.")

# =========================[ 15. BALANCE ]======================================
with tabs[4]:
    st.markdown("### ⚖️ الميزان السيادي")

    if state['active'] and state['bodies']:
        df = pd.DataFrame(state['bodies'])

        st.dataframe(
            df[['root', 'gene', 'energy', 'vx', 'vy']].sort_values('energy', ascending=False),
            use_container_width=True
        )
    else:
        st.info("الميزان السيادي ينتظر بيانات من الاستنطاق المداري.")

# =========================[ 16. META AWARENESS ]===============================
with tabs[5]:
    st.markdown("### 🧠 الوعي الفوقي النابض")

    if state['active']:
        st.markdown(f"""
        <div class="stat-container">
          <div class="stat-box">
            <div class="stat-val">{state['metrics'].get('count', 0)}</div>
            <div class="stat-label">عدد الأجسام النهائية</div>
          </div>
          <div class="stat-box">
            <div class="stat-val" style="color:#ffaa00">{state['metrics'].get('duration', 0)}s</div>
            <div class="stat-label">زمن المدار</div>
          </div>
          <div class="stat-box">
            <div class="stat-val" style="color:#4fc3f7">{len(state['logs'])}</div>
            <div class="stat-label">نبضات الوعي المسجلة</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # نبض الوعي الكلي
        if state['timeline'] and state['gene_counts_seq']:
            rows_aw = []
            for t, gc in zip(state['timeline'], state['gene_counts_seq']):
                rows_aw.append({'frame': t, 'total': sum(gc.values())})

            df_aw = pd.DataFrame(rows_aw)

            if not df_aw.empty:
                fig_aw = px.line(
                    df_aw,
                    x='frame',
                    y='total',
                    labels={'frame': 'الإطار الزمني', 'total': 'شدة الوعي'},
                    title="نبض الوعي المداري عبر الزمن"
                )
                fig_aw.update_layout(font=dict(family="Amiri, Arial, sans-serif"))
                st.plotly_chart(fig_aw, use_container_width=True)

        st.markdown("#### آخر نبضات الوعي:")
        st.markdown(
            "<div class='adaptive-log'>" +
            "<br>".join(state['logs']) +
            "</div>",
            unsafe_allow_html=True
        )
    else:
        st.info("الوعي الفوقي ينتظر أول تشغيل للاستنطاق المداري.")

# =========================[ 17. SIDEBAR ]======================================
st.sidebar.markdown(f"""
**المستخدم:** محمد  
**الإصدار:** v26.4 – Root-Stable Edition  
**الحالة:** مدار سيادي قابل للإطلاق العام  
**ملف الجذور:** {roots_info}  
**عدد الجذور:** {len(r_index)}  
---
خِت فِت.
""")
