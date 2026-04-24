import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta

def section_header(icon, title, subtitle="", color="#1a5c45"):
    """Reusable section header with medical graphic."""
    import streamlit as st
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:14px;
         background:white;border-radius:14px;padding:16px 20px;
         margin-bottom:16px;box-shadow:0 2px 10px rgba(0,0,0,0.06);
         border-left:5px solid {color};">
        <div style="font-size:2.4rem;line-height:1">{icon}</div>
        <div>
            <div style="font-size:1.1rem;font-weight:700;color:{color}">{title}</div>
            <div style="font-size:0.82rem;color:#6b7280">{subtitle}</div>
        </div>
        <div style="margin-left:auto;opacity:0.08;font-size:3rem;font-weight:900;color:{color}">✚</div>
    </div>""", unsafe_allow_html=True)

def render(T, load_json, RECORDS_FILE):
    st.markdown("### Community Health Trends — Salalah, Dhofar")
    st.caption("Real-time health analytics for public health research")

    records = load_json(RECORDS_FILE)
    use_mock = len(records) < 3

    if use_mock:
        st.info("Showing sample data — grows automatically as users submit health checks")
        random.seed(42)
        syms_pool = ["cough","fever","dizziness","fatigue","headache","breathlessness","nausea","chest_pain"]
        records = []
        for i in range(120):
            d = (datetime.now() - timedelta(days=random.randint(0,29))).strftime("%Y-%m-%d")
            records.append({
                "timestamp":d+" "+f"{random.randint(7,22):02d}:{random.randint(0,59):02d}",
                "date":d,"age":random.randint(18,85),
                "gender":random.choice(["Male","Female","Not specified"]),
                "city":random.choice(["Salalah"]*7+["Taqah","Mirbat","Rakhyut"]),
                "symptoms":", ".join(random.sample(syms_pool,random.randint(1,3))),
                "triage_level":random.choices(["GREEN","YELLOW","RED"],weights=[55,35,10])[0],
                "khareef_mode":random.random()>0.5,
            })
    else:
        st.success(f"Live data from {len(records)} real assessments")

    df = pd.DataFrame(records)

    k1,k2,k3,k4,k5 = st.columns(5)
    k1.metric("Total",   len(df))
    k2.metric("GREEN",   len(df[df["triage_level"]=="GREEN"]))
    k3.metric("YELLOW",  len(df[df["triage_level"]=="YELLOW"]))
    k4.metric("RED",     len(df[df["triage_level"]=="RED"]))
    if "age" in df.columns:
        try: k5.metric("Avg Age", round(df["age"].astype(float).mean(),1))
        except: pass

    st.markdown("---")
    c1,c2 = st.columns(2)
    with c1:
        st.markdown("**Most Common Symptoms**")
        sym_counts = {}
        for _,row in df.iterrows():
            for s in str(row.get("symptoms","")).split(", "):
                s = s.strip()
                if s and s not in ("None","nan",""):
                    sym_counts[s] = sym_counts.get(s,0)+1
        if sym_counts:
            sd = pd.DataFrame([{"Symptom":k.replace("_"," ").title(),"Count":v}
                for k,v in sorted(sym_counts.items(),key=lambda x:-x[1])[:10]])
            st.bar_chart(sd.set_index("Symptom"), color=T['p'], height=280)
    with c2:
        st.markdown("**Triage Distribution**")
        tc = df["triage_level"].value_counts().reset_index()
        tc.columns = ["Level","Count"]
        st.bar_chart(tc.set_index("Level"), height=280)

    if "date" in df.columns or "timestamp" in df.columns:
        st.markdown("**Daily Volume (Last 30 Days)**")
        try:
            df["d"] = pd.to_datetime(df.get("date",df["timestamp"].str[:10])).dt.strftime("%Y-%m-%d")
            daily = df.groupby("d").size().reset_index(name="Assessments").sort_values("d").tail(30)
            st.line_chart(daily.set_index("d"), color=T['p'], height=220)
        except: pass

    st.markdown("---")
    st.markdown("### Current Disease Alerts 2025-2026")
    at1,at2,at3,at4 = st.tabs(["Global Alerts","Oman & Gulf","New Treatments","Research"])

    with at1:
        alerts = [
            ("HMPV Respiratory Virus","ELEVATED","#d97706","#fef9c3",
             "Human Metapneumovirus surge globally. Flu-like illness. No specific treatment — supportive care. Affects elderly and children most severely."),
            ("COVID-19 New Variants","ACTIVE","#d97706","#fef9c3",
             "New subvariants circulating globally. Vaccines still protective against severe disease. Boosters recommended for high-risk groups."),
            ("Mpox (Monkeypox)","WATCH","#ea580c","#fff7ed",
             "WHO declared health emergency. Travel-related cases in Middle East. Monitor returnees from affected regions."),
        ]
        for name,status,color,bg,detail in alerts:
            st.markdown(f"""
            <div style="background:{bg};border-left:5px solid {color};border-radius:10px;padding:14px 18px;margin:8px 0;">
                <div style="display:flex;justify-content:space-between;flex-wrap:wrap;gap:6px;">
                    <b style="color:{color}">{name}</b>
                    <span style="background:{color};color:white;padding:2px 10px;border-radius:99px;font-size:0.8rem">{status}</span>
                </div>
                <div style="font-size:0.88rem;color:#374151;margin-top:6px;line-height:1.6">{detail}</div>
            </div>""", unsafe_allow_html=True)

    with at2:
        oman = [
            ("Dengue Fever","SEASONAL","#ea580c","Khareef creates mosquito breeding conditions. Eliminate standing water. Use repellent outdoors."),
            ("Heat Stroke","HIGH RISK MAY-SEP","#dc2626","Extreme temperatures + Khareef humidity = high risk. Stay hydrated, avoid midday sun."),
            ("Diabetes — Oman","CHRONIC HIGH BURDEN","#dc2626","Oman has one of the world's highest diabetes rates. Regular screening critical."),
            ("Respiratory Infections","SEASONAL KHAREEF","#d97706","Fungal spores and humidity during Khareef trigger asthma and respiratory infections."),
        ]
        for name,status,color,detail in oman:
            st.markdown(f"""
            <div style="background:#fff7f0;border-left:5px solid {color};border-radius:10px;padding:12px 16px;margin:6px 0;">
                <div style="display:flex;justify-content:space-between;flex-wrap:wrap;">
                    <b style="color:{color}">{name}</b>
                    <span style="font-size:0.8rem;color:{color};font-weight:700">{status}</span>
                </div>
                <div style="font-size:0.88rem;color:#374151;margin-top:6px">{detail}</div>
            </div>""", unsafe_allow_html=True)

    with at3:
        st.success("""
New developments in healthcare 2025-2026:

GLP-1 Medications (Ozempic/Wegovy) — Now proven to reduce heart attack risk by 20%

RSV Vaccines — First adult RSV vaccine approved. Recommended for adults 60+

Alzheimer's drug (Lecanemab) — First drug to slow Alzheimer's progression

mRNA Vaccines — Being applied to cancer, RSV, HIV, and influenza

AI Diagnostics — Matching specialist accuracy in skin cancer, chest X-rays, ECG

Affordable Insulin — Generic insulin now at much lower cost in many countries
        """)

    with at4:
        st.markdown("""
        <div style="background:#eff6ff;border-radius:12px;padding:18px 22px;border-left:5px solid #2563eb;">
            <b style="color:#1e40af">Research Partnership — Khareef Health</b>
            <div style="color:#1e3a8a;font-size:0.9rem;margin-top:10px;line-height:1.8">
                Real-time symptom surveillance across Salalah and Dhofar<br>
                Seasonal health pattern analysis — Khareef vs normal season<br>
                Elderly health monitoring — priority population in Dhofar<br>
                AI-assisted triage data for clinical decision support research<br>
                Multilingual health equity — Arabic and English accessibility<br><br>
                <i>Contact: sadgaselime for research collaboration enquiries</i>
            </div>
        </div>""", unsafe_allow_html=True)
