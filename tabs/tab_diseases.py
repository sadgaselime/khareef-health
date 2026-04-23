import streamlit as st

def render(T, DISEASES, CATEGORIES, search_diseases, get_by_category):
    st.markdown("### Disease Encyclopedia / موسوعة الأمراض")
    st.markdown('<div class="disclaimer">General health education only. Always consult a qualified doctor for diagnosis.</div>', unsafe_allow_html=True)
    st.markdown("")

    c1,c2 = st.columns([2,1])
    with c1:
        q = st.text_input("Search / البحث:", placeholder="e.g. diabetes, COVID, السكري...", key="dq")
    with c2:
        cat = st.selectbox("Category:", ["All"] + CATEGORIES, key="dcat")

    if q.strip():
        filtered = search_diseases(q)
    elif cat != "All":
        filtered = get_by_category(cat)
    else:
        filtered = DISEASES

    if not filtered:
        st.warning("No results found. Try a different search term.")
        return

    st.caption(f"{len(filtered)} disease(s) found")
    names = list(filtered.keys())
    sel = st.selectbox("Select disease:", names,
        format_func=lambda x: f"{filtered[x]['emoji']} {x} — {filtered[x]['category']}",
        key="dsel")

    if sel:
        d = filtered[sel]
        p = T['p']
        contagious = "Contagious" if d['is_contagious'] else "Not contagious"
        genetic    = "Has genetic component" if d['is_genetic'] else "Not genetic"
        st.markdown(f"""
        <div style="background:{T['l']};border-radius:14px;padding:20px;border:2px solid {p}33;margin-bottom:12px;">
            <div style="display:flex;align-items:center;gap:14px;flex-wrap:wrap;">
                <div style="font-size:3rem">{d['emoji']}</div>
                <div style="flex:1">
                    <div style="font-size:1.4rem;font-weight:700;color:{p}">{sel}</div>
                    <div style="font-size:0.85rem;color:#6b7280">Also known as: {d['also_known_as']}</div>
                    <div class="ar" style="color:{p};font-size:0.95rem">{d['arabic_name']}</div>
                </div>
                <div style="display:flex;flex-direction:column;gap:4px;font-size:0.8rem;font-weight:600;">
                    <span style="background:{'#fee2e2' if d['is_contagious'] else '#dcfce7'};color:{'#dc2626' if d['is_contagious'] else '#16a34a'};padding:3px 10px;border-radius:99px">{contagious}</span>
                    <span style="background:#ede9fe;color:#7c3aed;padding:3px 10px;border-radius:99px">{genetic}</span>
                    <span style="background:{T['l']};color:{p};padding:3px 10px;border-radius:99px">{d['category']}</span>
                </div>
            </div>
            <div style="margin-top:12px;font-size:0.9rem;color:#374151;line-height:1.7">{d['overview']}</div>
        </div>""", unsafe_allow_html=True)

        st.info(f"Recovery: {d['recovery_time']}")
        if d.get("khareef_connection"):
            st.warning(f"Khareef Note: {d['khareef_connection']}")

        dt1,dt2,dt3,dt4,dt5,dt6 = st.tabs(["How It Occurs","Symptoms","High Risk","Prevention","Treatment","Seek Help"])

        with dt1:
            st.info(f"Type: {d['how_it_occurs']}")
            for item in d["transmission"]:
                st.markdown(f'<div class="step">{item}</div>', unsafe_allow_html=True)
        with dt2:
            for s in d["symptoms"]:
                css = "step-red" if "Severe" in s or "EMERGENCY" in s.upper() else "step"
                st.markdown(f'<div class="{css}">{s}</div>', unsafe_allow_html=True)
        with dt3:
            for g in d["high_risk_groups"]:
                st.markdown(f'<div class="step-red">{g}</div>', unsafe_allow_html=True)
        with dt4:
            for p in d["prevention"]:
                st.markdown(f'<div class="step">{p}</div>', unsafe_allow_html=True)
        with dt5:
            for t in d["treatment"]:
                st.markdown(f'<div class="step">{t}</div>', unsafe_allow_html=True)
        with dt6:
            st.error("Go to hospital or call 999 if:")
            for w in d["when_to_seek_help"]:
                st.markdown(f'<div class="step-red">{w}</div>', unsafe_allow_html=True)
            st.info("Sultan Qaboos Hospital Salalah · 999 · +968 23 218 000")
