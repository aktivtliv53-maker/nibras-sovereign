# -*- coding: utf-8 -*-
# ==============================================================================
# نظام نِبْرَاس السيادي (Nibras Sovereign System) - الإصدار v29.1
# "ثلاثية الصعود + الطيف الجيني"
# ==============================================================================

import streamlit as st
import pandas as pd
import plotly.express as px
from collections import Counter
import re, random, os, json, hashlib

# ==============================================================================
# [0] أعلام التحكم
# ==============================================================================
ENABLE_SMART_ROOT = True
ENABLE_CONTEXT_ORBIT = True
ENABLE_DYNAMIC_ENERGY = True
ENABLE_COLLECTIVE_LAYER = True
ENABLE_HEATMAP_LAYER = True
ENABLE_ASCENT_VECTOR = True
ENABLE_MAKIN_LAYER = True

# ==============================================================================
# [1] إعدادات الواجهة
# ==============================================================================
st.set_page_config(page_title="Nibras v29.1", page_icon="🛡️", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&display=swap');
    [data-testid="stAppViewContainer"] {
        background: #050505; color: #e0e0e0; direction: rtl; font-family: 'Amiri', serif;
    }
    .insight-card {
        background: linear-gradient(135deg,#0d0d14,#161625);
        padding:20px;border-radius:15px;border-right:6px solid #FFD700;
        margin-bottom:15px;line-height:1.8;
    }
    .story-box {
        background: linear-gradient(135deg,rgba(10,21,10,0.85),rgba(1,1,3,0.95));
        padding:30px;border-radius:20px;border-right:10px solid #4CAF50;
        margin-bottom:25px;line-height:2;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# [2] الجينات
# ==============================================================================
GENE_STYLE = {
    'C': {'name':'الإبل','color':'#4fc3f7','icon':'🐪'},
    'B': {'name':'البقر','color':'#FFD700','icon':'🐄'},
    'S': {'name':'الضأن','color':'#4CAF50','icon':'🐑'},
    'G': {'name':'المعز','color':'#ff5252','icon':'🐐'},
    'N': {'name':'إشراق','color':'#00ffcc','icon':'✨'}
}

# ==============================================================================
# [3] التطهير
# ==============================================================================
ARABIC_DIACRITICS_PATTERN = re.compile(r'[\u0617-\u061A\u064B-\u0652]')

def normalize_lexicon_root(r):
    return r.replace("أ","ا").replace("إ","ا").replace("آ","ا").replace("ة","ه").replace("ى","ي").strip()

def normalize_sovereign(text):
    text = ARABIC_DIACRITICS_PATTERN.sub('', text)
    text = text.replace("أ","ا").replace("إ","ا").replace("آ","ا").replace("ى","ي").replace("ة","ه")
    return re.sub(r'[^\u0621-\u063A\u064B-\u0652\s]', ' ', text).strip()

def ensure_dot(t):
    return t if t.endswith('.') else t+'.'

# ==============================================================================
# [4] محرك الجين
# ==============================================================================
def get_sovereign_gene(root, weight, orbit):
    if orbit in [1,2]: g="C"
    elif orbit in [3,4]: g="B"
    elif orbit in [5,6]: g="G"
    elif orbit>=7: g="S"
    else: g="N"
    return g, (weight*100 if weight<10 else weight)

def signature_from_root(root):
    if not root: return {'total_energy':300,'vector_x':0,'vector_y':0}
    h=int(hashlib.md5(root.encode()).hexdigest(),16)
    return {
        'total_energy':len(root)*285+(h%150),
        'vector_x':(h%30-15)/120,
        'vector_y':((h>>4)%30-15)/120
    }

# ==============================================================================
# [5] تحميل قاعدة البيانات
# ==============================================================================
@st.cache_data(ttl=3600)
def load_lexicon_db(path):
    if not os.path.exists(path): return {},[],Counter()
    data=json.load(open(path,'r',encoding='utf-8'))
    r_index={}; all_roots=[]; orbit_counter=Counter()

    for item in data:
        raw=item.get("root",""); 
        if not raw: continue
        norm=normalize_lexicon_root(raw)
        orbit=item.get("orbit_id",0)
        weight=float(item.get("weight",50))
        gene,cal=get_sovereign_gene(raw,weight,orbit)
        insight=item.get("insight_radar",item.get("insight",""))

        r_index[norm]={
            "root_raw":raw,"root":norm,
            "orbit_id":orbit,"orbit":f"المدار {orbit}",
            "weight":weight,"raw_energy":cal,
            "insight":ensure_dot(insight),"gene":gene
        }
        all_roots.append(r_index[norm])
        orbit_counter[f"المدار {orbit}"]+=1

    return r_index,all_roots,orbit_counter

# ==============================================================================
# [6] التحليل الجذري
# ==============================================================================
def smart_extract_root(w):
    w=normalize_sovereign(w)
    if len(w)<=3: return w
    for p in ["ال","وال","بال","كال","فال","س","و","ف","ل","ب","ك"]:
        if w.startswith(p) and len(w)-len(p)>=3: w=w[len(p):]; break
    for s in ["هما","كما","كم","كن","نا","ها","هم","هن","ان","ون","ين","ات","ة","ه","ي","ا"]:
        if w.endswith(s) and len(w)-len(s)>=3: w=w[:-len(s)]; break
    return w

def match_root_logic(word,keys):
    w=normalize_sovereign(word)
    if len(w)<2: return None
    n=normalize_lexicon_root(w)
    if n in keys: return n
    for p in ["ال","و","ف","ب","ك","ل","س"]:
        if w.startswith(p) and len(w)-len(p)>=3:
            c=normalize_lexicon_root(w[len(p):])
            if c in keys: return c
    s=normalize_lexicon_root(smart_extract_root(word))
    return s if s in keys else None

def display_insight_cards(bodies):
    for b in bodies:
        st.markdown(f"""
        <div class="insight-card" style="border-right-color:{b['color']}">
            <b style="color:{b['color']}">📌 {b['root']}</b> |
            🧬 {b['gene_icon']} {b['gene_name']} |
            ⚡ {b['energy']:.1f}
            <hr>{b['insight']}
        </div>
        """,unsafe_allow_html=True)

# ==============================================================================
# [7] حالة الجلسة
# ==============================================================================
if 'orbit_bodies' not in st.session_state:
    st.session_state.orbit_bodies=[]
    st.session_state.orbit_active=False

r_index,all_roots,orbit_counter=load_lexicon_db("data/nibras_lexicon.json")

# ==============================================================================
# [8] الشريط الجانبي
# ==============================================================================
with st.sidebar:
    st.markdown("<h2 style='text-align:center;color:#4fc3f7'>🛡️ نبراس السيادي</h2>",unsafe_allow_html=True)
    st.markdown("الإصدار v29.1 — ثلاثية الصعود + الطيف الجيني")
    st.markdown("المستخدم: محمد")
    st.markdown("---")
    st.markdown(f"📚 إجمالي الجذور: {len(r_index)}")
    for k,v in orbit_counter.items(): st.markdown(f"🔹 {k}: {v}")
    st.markdown("---")
    st.markdown("خِت فِت.")

# ==============================================================================
# [9] التبويبات
# ==============================================================================
tabs=st.tabs([
    "🔍 الاستنطاق المداري",
    "🌌 الرنين الجيني",
    "📈 اللوحة الوجودية الحرارية",
    "📜 البيان الختامي",
    "⚖️ الميزان السيادي",
    "🧠 الوعي الفوقي"
])

# ==============================================================================
# [10] الطبقات الديناميكية
# ==============================================================================
def apply_context_orbit_adjustment(bodies):
    freq=Counter(b['root'] for b in bodies)
    maxf=max(freq.values()) if freq else 1
    for b in bodies:
        f=freq[b['root']]
        b['orbit_id_context']=b['orbit_id']+(1 if f>=maxf and b['orbit_id']>0 else 0)
    return bodies

def apply_dynamic_energy(bodies,text_len):
    freq=Counter(b['root'] for b in bodies)
    factor=max(1,min(3,text_len/50))
    for b in bodies:
        sig=signature_from_root(b['root'])
        base=b['base_energy']
        f=freq[b['root']]
        dyn=base*(1+0.05*(f-1))*factor + sig['total_energy']*0.05
        b['energy']=round(dyn,2)
    return bodies

def compute_collective_consciousness(bodies):
    genes=Counter(b['gene'] for b in bodies)
    total=sum(b['energy'] for b in bodies)
    uniq=len(set(b['root'] for b in bodies))
    ascent=genes.get('G',0)+genes.get('C',0)
    calm=genes.get('S',0)
    material=genes.get('B',0)
    tension=ascent*1.2 + material*0.8 - calm
    harmony=calm*1.3 + uniq*0.2
    return {
        "total_energy":total,
        "genes_count":genes,
        "unique_roots":uniq,
        "tension_level":round(tension,2),
        "harmony_level":round(harmony,2)
    }

def compute_ascent_vector(bodies):
    vals=[b.get('orbit_id_context',b['orbit_id']) for b in bodies if b['orbit_id']]
    if not vals: return 0.0
    return round(sum(vals)/len(vals)-5,2)

def compute_gene_spectrum(bodies,window=4):
    spec=[]
    for i in range(0,len(bodies),window):
        chunk=bodies[i:i+window]
        genes=[b['gene'] for b in chunk]
        if genes: spec.append(Counter(genes).most_common(1)[0][0])
    return spec

# ==============================================================================
# [11] التبويب 0: الاستنطاق المداري
# ==============================================================================
with tabs[0]:
    st.markdown("### 📍 هندسة المسارات المدارية — v29.1")
    full_text=st.text_area("أدخل النص للاستنطاق:",height=150)

    if st.button("🚀 تفعيل المفاعل السيادي",use_container_width=True):
        if full_text.strip():
            clean=normalize_sovereign(full_text)
            words=clean.split()
            bodies=[]

            for w in words:
                key=match_root_logic(w,r_index.keys())
                if key:
                    d=r_index[key]
                    sig=signature_from_root(key)
                    base=d['raw_energy']
                    gene_info=GENE_STYLE[d['gene']]
                    energy=base + sig['total_energy']*0.15

                    bodies.append({
                        "root":d['root_raw'],
                        "orbit":d['orbit'],
                        "orbit_id":d['orbit_id'],
                        "gene":d['gene'],
                        "gene_name":gene_info['name'],
                        "gene_icon":gene_info['icon'],
                        "energy":round(energy,2),
                        "base_energy":round(energy,2),
                        "insight":d['insight'],
                        "color":gene_info['color'],
                        "x":random.uniform(-10,10),
                        "y":random.uniform(-10,10)
                    })

            if bodies:
                bodies=apply_context_orbit_adjustment(bodies)
                bodies=apply_dynamic_energy(bodies,len(full_text))

                st.session_state.orbit_bodies=bodies
                st.session_state.orbit_active=True

                df=pd.DataFrame(bodies)
                fig=px.scatter(
                    df,x="x",y="y",text="root",size="energy",color="gene",
                    color_discrete_map={g:GENE_STYLE[g]['color'] for g in GENE_STYLE},
                    range_x=[-35,35],range_y=[-35,35]
                )
                fig.update_layout(height=500,paper_bgcolor='rgba(0,0,0,0)',
                                  plot_bgcolor='rgba(0,0,0,0)',showlegend=False,
                                  xaxis_visible=False,yaxis_visible=False)
                st.plotly_chart(fig,use_container_width=True)

                total=sum(b['energy'] for b in bodies)
                genes=Counter(b['gene'] for b in bodies)
                dom=max(genes,key=genes.get)
                cc=compute_collective_consciousness(bodies)
                asc=compute_ascent_vector(bodies)

                st.markdown(f"""
                <div class="story-box">
                    تم استنطاق <b>{len(bodies)}</b> جذراً.<br>
                    الهيمنة الجينية: <b>{GENE_STYLE[dom]['icon']} {GENE_STYLE[dom]['name']}</b><br>
                    مجموع الطاقة: <b>{total:.1f}</b><br>
                    الانسجام: <b>{cc['harmony_level']}</b> |
                    التوتر: <b>{cc['tension_level']}</b><br>
                    متجه الصعود: <b>{asc}</b>
                </div>
                """,unsafe_allow_html=True)

                display_insight_cards(bodies)
            else:
                st.error("⚠️ لم يتم العثور على جذور.")

# ==============================================================================
# [12] التبويب 1: الرنين الجيني
# ==============================================================================
with tabs[1]:
    st.markdown("### 🌌 الرنين الجيني")
    roots_sorted=sorted([r['root_raw'] for r in all_roots])
    sel=st.selectbox("اختر جذراً:",roots_sorted)

    if sel:
        norm=normalize_lexicon_root(sel)
        d=r_index.get(norm)
        if d:
            gi=GENE_STYLE[d['gene']]
            st.markdown(f"""
            <div class="insight-card" style="border-right-color:{gi['color']}">
                <b style="color:{gi['color']}">📌 {d['root_raw']}</b><br>
                🧬 {gi['icon']} {gi['name']}<br>
                المدار: {d['orbit']}<br>
                الطاقة: {d['raw_energy']:.1f}<br>
                <hr>{d['insight']}
            </div>
            """,unsafe_allow_html=True)

# ==============================================================================
# [13] التبويب 2: اللوحة الوجودية الحرارية
# ==============================================================================
with tabs[2]:
    st.markdown("### 📈 خريطة الوعي الحراري")
    if st.session_state.orbit_active:
        df=pd.DataFrame(st.session_state.orbit_bodies)
        df['orbit_plot']=df.get('orbit_id_context',df['orbit_id'])
        df['gene_label']=df['gene'].map(lambda g:f"{GENE_STYLE[g]['icon']} {GENE_STYLE[g]['name']}")

        heat=df.groupby(['orbit_plot','gene_label'])['energy'].sum().reset_index()
        if not heat.empty:
            pivot=heat.pivot(index='gene_label',columns='orbit_plot',values='energy').fillna(0)

            fig_h=px.imshow(
                pivot.values,
                labels=dict(x="المدار",y="الجين",color="الطاقة"),
                x=list(range(len(pivot.columns))),
                y=list(range(len(pivot.index))),
                color_continuous_scale="RdBu_r"
            )

            fig_h.update_xaxes(
                tickmode='array',
                tickvals=list(range(len(pivot.columns))),
                ticktext=pivot.columns
            )
            fig_h.update_yaxes(
                tickmode='array',
                tickvals=list(range(len(pivot.index))),
                ticktext=pivot.index
            )

            fig_h.update_layout(height=500,paper_bgcolor='rgba(0,0,0,0)',
                                plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_h,use_container_width=True)
            # ==============================================================================
# [14] التبويب 3: البيان الختامي
# ==============================================================================
with tabs[3]:
    st.markdown("### 📜 البيان الختامي")

    if st.session_state.orbit_active and st.session_state.orbit_bodies:
        bodies = st.session_state.orbit_bodies

        total_e = sum(b['energy'] for b in bodies)
        genes_count = Counter(b['gene'] for b in bodies)
        dom_gene = max(genes_count, key=genes_count.get)
        cc = compute_collective_consciousness(bodies)
        ascent_vec = compute_ascent_vector(bodies)

        st.markdown(f"""
        <div class="story-box">
            <b>بيان الاستواء الوجودي v29.1:</b><br>
            عدد الجذور: <b>{len(bodies)}</b><br>
            الهيمنة الجينية: <b>{GENE_STYLE[dom_gene]['icon']} {GENE_STYLE[dom_gene]['name']}</b><br>
            مجموع الطاقة: <b>{total_e:.1f}</b><br>
            مستوى الانسجام: <b>{cc['harmony_level']}</b> |
            مستوى التوتر: <b>{cc['tension_level']}</b><br>
            متجه الصعود: <b>{ascent_vec}</b>
        </div>
        """, unsafe_allow_html=True)

        display_insight_cards(bodies)

    else:
        st.info("⚙️ انتظر تفعيل المفاعل.")

# ==============================================================================
# [15] التبويب 4: الميزان السيادي
# ==============================================================================
with tabs[4]:
    st.markdown("### ⚖️ ميزان النزاهة الجذرية")

    if st.session_state.orbit_active and st.session_state.orbit_bodies:
        display_insight_cards(st.session_state.orbit_bodies)
    else:
        st.info("⚙️ انتظر تفعيل المفاعل.")

# ==============================================================================
# [16] التبويب 5: الوعي الفوقي + الطيف الجيني
# ==============================================================================
with tabs[5]:
    st.markdown("### 🧠 الوعي الفوقي — البيان الجمعي + الطيف الجيني")

    if st.session_state.orbit_active and st.session_state.orbit_bodies:
        bodies = st.session_state.orbit_bodies

        total_e = sum(b['energy'] for b in bodies)
        genes_count = Counter(b['gene'] for b in bodies)
        dom_gene = max(genes_count, key=genes_count.get)
        orbits_analysis = Counter(b.get('orbit_id_context', b['orbit_id']) for b in bodies)
        cc = compute_collective_consciousness(bodies)
        ascent_vec = compute_ascent_vector(bodies)

        st.markdown(f"""
        <div class="story-box">
            <h3 style='color:#FFD700;'>🌌 بيان الوعي الجمعي</h3>
            عدد الجذور: <b>{len(bodies)}</b><br>
            مجموع الطاقة: <b>{total_e:.1f}</b><br>
            الهيمنة الجينية: <b>{GENE_STYLE[dom_gene]['icon']} {GENE_STYLE[dom_gene]['name']}</b><br>
            توزيع المدارات: {', '.join([f'{k}({v})' for k,v in sorted(orbits_analysis.items())])}<br>
            مستوى الانسجام: <b>{cc['harmony_level']}</b> |
            مستوى التوتر: <b>{cc['tension_level']}</b><br>
            متجه الصعود: <b>{ascent_vec}</b>
        </div>
        """, unsafe_allow_html=True)

        # 🌈 الطيف الجيني
        spectrum = compute_gene_spectrum(bodies, window=4)

        if spectrum:
            st.markdown("### 🌈 الطيف الجيني — Gene Spectrum")

            gene_to_num = {"S":1, "B":2, "C":3, "G":4, "N":5}
            numeric = [gene_to_num[g] for g in spectrum]

            fig_spec = px.line(
                x=list(range(1, len(numeric)+1)),
                y=numeric,
                markers=True,
                labels={"x":"المقطع", "y":"الجين"},
                title="الطيف الجيني عبر النص"
            )

            fig_spec.update_yaxes(
                tickmode='array',
                tickvals=[1,2,3,4,5],
                ticktext=[
                    "🐑 الضأن (S)",
                    "🐄 البقر (B)",
                    "🐪 الإبل (C)",
                    "🐐 المعز (G)",
                    "✨ إشراق (N)"
                ]
            )

            fig_spec.update_layout(
                height=350,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )

            st.plotly_chart(fig_spec, use_container_width=True)

            st.markdown(f"""
            <div class="story-box">
                🔭 <b>قراءة الطيف الجيني:</b><br>
                عدد الموجات: <b>{len(spectrum)}</b><br>
                البداية: <b>{GENE_STYLE[spectrum[0]]['name']}</b><br>
                النهاية: <b>{GENE_STYLE[spectrum[-1]]['name']}</b>
            </div>
            """, unsafe_allow_html=True)

        display_insight_cards(bodies)

    else:
        st.info("⚙️ انتظر تفعيل المفاعل.")

# ==============================================================================
# نهاية الملف
# ==============================================================================
