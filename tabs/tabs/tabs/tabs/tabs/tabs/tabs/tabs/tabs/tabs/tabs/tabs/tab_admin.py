import streamlit as st
import pandas as pd
import json, os

ADMIN_PASSWORD = "Sadga@Khareef2026"

def render(load_json, save_json, RECORDS_FILE, PROFILES_FILE, VISITORS_FILE):
    st.markdown("---")
    st.markdown("### Admin Dashboard — Private")

    if "admin_ok" not in st.session_state:
        st.session_state.admin_ok = False

    if not st.session_state.admin_ok:
        pw = st.text_input("Admin Password:", type="password", key="admpw")
        if st.button("Login", key="admlogin"):
            if pw == ADMIN_PASSWORD:
                st.session_state.admin_ok = True
                st.rerun()
            else:
                st.error("Wrong password.")
        return

    st.success("Welcome, Sadga Selime!")
    if st.button("Logout", key="admout"):
        st.session_state.admin_ok = False
        st.rerun()

    # Visitor stats
    visitors = load_json(VISITORS_FILE)
    st.markdown("### Visitor Log")
    if visitors:
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        st.metric("Total Visits", len(visitors))
        st.metric("Today", sum(1 for v in visitors if v.get("date")==today))
        df_v = pd.DataFrame(visitors).sort_values("timestamp",ascending=False)
        search_v = st.text_input("Search visitors:", key="vsrch")
        if search_v:
            df_v = df_v[df_v["name"].str.contains(search_v,case=False,na=False)]
        st.dataframe(df_v, use_container_width=True, height=300)
        st.download_button("Download Visitors CSV", df_v.to_csv(index=False),
            "visitors.csv","text/csv",key="dlv")
    else:
        st.info("No visitors yet.")

    st.markdown("---")

    # Health records
    records = load_json(RECORDS_FILE)
    st.markdown("### Health Check Records")
    if records:
        df_r = pd.DataFrame(records).sort_values("timestamp",ascending=False)
        r1,r2,r3,r4 = st.columns(4)
        r1.metric("Total",  len(df_r))
        r2.metric("Green",  len(df_r[df_r["triage_level"]=="GREEN"]))
        r3.metric("Yellow", len(df_r[df_r["triage_level"]=="YELLOW"]))
        r4.metric("Red",    len(df_r[df_r["triage_level"]=="RED"]))

        # Individual viewer
        names = [f"{df_r.iloc[i]['timestamp']} — {df_r.iloc[i]['name']} — {df_r.iloc[i]['triage_level']}"
                 for i in range(len(df_r))]
        sel = st.selectbox("View record:", range(len(names)),
            format_func=lambda i: names[i], key="rsel")
        rec = df_r.iloc[sel]
        col = {"GREEN":"#16a34a","YELLOW":"#d97706","RED":"#dc2626"}.get(rec.get("triage_level",""),"#6b7280")
        st.markdown(f"""
        <div style="background:#f8f9fa;border-left:5px solid {col};border-radius:10px;padding:16px;margin:10px 0;">
            <b style="color:{col}">{rec.get('name','')} — {rec.get('triage_level','')}</b>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-top:8px;font-size:0.88rem;">
                <div>Time: {rec.get('timestamp','')}</div>
                <div>Age: {rec.get('age','')}</div>
                <div>Gender: {rec.get('gender','')}</div>
                <div>City: {rec.get('city','')}</div>
                <div>Phone: {rec.get('phone','')}</div>
                <div>BP: {rec.get('bp','')}</div>
                <div>Sugar: {rec.get('blood_sugar','')}</div>
                <div>Temp: {rec.get('temperature','')}</div>
                <div style="grid-column:1/-1">Symptoms: {rec.get('symptoms','')}</div>
                <div style="grid-column:1/-1">Findings: {rec.get('findings','')[:200]}</div>
            </div>
        </div>""", unsafe_allow_html=True)

        srch = st.text_input("Search records:", key="rsrch")
        if srch: df_r = df_r[df_r["name"].str.contains(srch,case=False,na=False)]
        st.dataframe(df_r, use_container_width=True, height=320)
        c1,c2 = st.columns(2)
        c1.download_button("Download CSV", df_r.to_csv(index=False),"records.csv","text/csv",key="dlr")
        c2.download_button("Download JSON", json.dumps(records,indent=2,ensure_ascii=False),"records.json","application/json",key="dlrj")
        if st.button("Clear Records", key="clrr"):
            if os.path.exists(RECORDS_FILE): os.remove(RECORDS_FILE)
            st.success("Cleared!"); st.rerun()
    else:
        st.info("No health check records yet.")

    st.markdown("---")

    # Profiles
    profiles = load_json(PROFILES_FILE)
    st.markdown("### Saved Profiles")
    if profiles:
        st.dataframe(pd.DataFrame(profiles), use_container_width=True)
        st.download_button("Download Profiles", pd.DataFrame(profiles).to_csv(index=False),
            "profiles.csv","text/csv",key="dlp")
    else:
        st.info("No profiles saved yet.")
