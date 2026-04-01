# ==============================================================================
# التبويب 1: الرنين الجيني - نسخة ديناميكية تقرأ من ملف JSON
# ==============================================================================
with tabs[1]:
    st.markdown("### 🌌 مصفوفة الرنين والاستحقاق الجيني")
    
    # عرض بطاقات الأنعام الأربعة
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
    
    st.markdown("---")
    st.markdown("### 📖 استنطاق الجذر النشط")
    
    # البحث عن الجذر والمدار التابع له في all_roots
    target_root = st.session_state.get('active_root', '').strip()
    root_data = None
    orbit_name = "جين المعز"  # القيمة الافتراضية في حال عدم المطابقة
    
    if target_root and 'all_roots' in globals():
        for orbit_item in all_roots:
            # تأكد من أننا نبحث داخل قائمة roots داخل كل مدار
            current_roots = orbit_item.get('roots', [])
            for r in current_roots:
                if r.get('name', '').strip() == target_root:
                    root_data = r
                    orbit_name = orbit_item.get('orbit', 'مدار غير مسمى')
                    break
            if root_data:
                break
    
    if root_data:
        display_items = [
            {"icon": "🌌", "label": "المدار الوجودي", "val": root_data.get('meaning', 'جاري الرصد')},
            {"icon": "⚖️", "label": "المقام السيادي", "val": root_data.get('insight', 'جاري الضبط')}
        ]
        c1, c2 = st.columns(2)
        for i, item in enumerate(display_items):
            with [c1, c2][i]:
                st.markdown(f"""
                    <div style='border:1px solid #444; padding:15px; border-radius:15px; text-align:center; background:#111; min-height:150px;'>
                        <h2 style='margin:0;'>{item['icon']}</h2>
                        <p style='color:#888; font-size:0.8em; margin:5px 0;'>{item['label']}</p>
                        <h4 style='color:#fff; margin:0;'>{item['val']}</h4>
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.info(f"🔍 لم يتم العثور على بيانات للجذر '{target_root}' في قاعدة البيانات. تأكد من وجوده في ملف nibras_lexicon.json")
