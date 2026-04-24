import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import datetime
from data import Patient, validate_patient_input, normalize_symptoms
from triage import assess_patient

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

def render(T, save_record, log_patient, is_api_key_configured,
           get_gemini_advice, analyze_free_text, RECORDS_FILE):

    st.markdown("### Patient Details")
    a1,a2 = st.columns(2)
    with a1:
        name = st.text_input("Name / الاسم", value=st.session_state.user_name,
            placeholder="e.g. Ahmed", key="aname")
    with a2:
        age = st.number_input("Age / العمر", 0, 120,
            value=st.session_state.user_age, key="aage")
        if age<=1:    st.caption("👶 Infant")
        elif age<=12: st.caption("🧒 Child")
        elif age<=17: st.caption("🧑 Teenager")
        elif age<=59: st.caption("👨 Adult")
        else:         st.caption("👴 Elderly — higher risk")

    st.markdown("---")
    # ── FREE TEXT AI ──
    st.markdown("### Describe Your Problem in Your Own Words")
    st.caption("Type anything in English or Arabic — AI analyzes directly")
    ft = st.text_area("What is bothering you? / ما الذي يزعجك؟",
        placeholder="e.g. I have had a headache for 2 days and feel dizzy...",
        height=100, key="ft")
    fc1,fc2 = st.columns(2)
    run_en = fc1.button("Analyze English", type="primary", use_container_width=True, key="fen")
    run_ar = fc2.button("تحليل بالعربية", use_container_width=True, key="far")

    if (run_en or run_ar) and ft.strip():
        with st.spinner("AI analyzing..."):
            res = analyze_free_text(ft, "ar" if run_ar else "en")
        if res.get("success"):
            urgency = res.get("urgency","MEDIUM")
            colors  = {"HIGH":"#dc2626","MEDIUM":"#d97706","LOW":"#16a34a"}
            bgs     = {"HIGH":"#fee2e2","MEDIUM":"#fef9c3","LOW":"#dcfce7"}
            uc = colors.get(urgency,"#d97706")
            ub = bgs.get(urgency,"#fef9c3")
            st.markdown(f"""
            <div style="background:{ub};border-left:5px solid {uc};border-radius:12px;padding:16px;">
                <b style="color:{uc};font-size:1.1rem">Urgency: {urgency}</b>
            </div>""", unsafe_allow_html=True)
            c1,c2 = st.columns(2)
            with c1:
                if res.get("symptoms"):
                    st.markdown("**Symptoms Found:**")
                    for s in res["symptoms"]:
                        st.markdown(f'<div class="step-red">• {s}</div>', unsafe_allow_html=True)
                if res.get("explanation"):
                    st.info(res["explanation"])
            with c2:
                if res.get("causes"):
                    st.markdown("**Possible Causes:**")
                    for c in res["causes"]:
                        st.markdown(f'<div class="step">• {c}</div>', unsafe_allow_html=True)
                if res.get("next_steps"):
                    st.markdown("**What To Do:**")
                    for s in res["next_steps"]:
                        st.markdown(f'<div class="step">• {s}</div>', unsafe_allow_html=True)
            if urgency == "HIGH":
                st.error("Sultan Qaboos Hospital Salalah · 999 · +968 23 218 000")
        else:
            st.error(f"AI Error: {res.get('error','Unknown error')}")
    elif (run_en or run_ar):
        st.warning("Please describe your concern first.")

    st.markdown("---")
    st.markdown("### OR use the structured form below")
    st.markdown("---")

    # ── VITALS ──
    st.markdown("### Vital Signs / العلامات الحيوية")
    know = st.toggle("I have my BP / Sugar / Temperature readings", key="know")
    if not know:
        st.info("No readings? That's OK — get symptom-based advice below.")
        bps,bpd,sugar,temp = 120,80,100,37.0
    else:
        b1,b2 = st.columns(2)
        with b1:
            st.markdown("**Upper BP (Systolic)** — Normal: 90-120")
            bps = st.number_input("Systolic",60,240,120,key="bps",label_visibility="collapsed")
            if bps>=180: st.error("CRISIS")
            elif bps<90: st.error("Very LOW")
            elif bps>=140: st.warning("High")
            else: st.success("Normal")
        with b2:
            st.markdown("**Lower BP (Diastolic)** — Normal: 60-80")
            bpd = st.number_input("Diastolic",40,140,80,key="bpd",label_visibility="collapsed")
            if bpd>=120: st.error("CRISIS")
            elif bpd<60: st.error("Very LOW")
            elif bpd>=90: st.warning("High")
            else: st.success("Normal")
        st.markdown(f"Combined: **{bps}/{bpd} mmHg**")
        st.markdown("---")
        v1,v2 = st.columns(2)
        with v1:
            st.markdown("**Blood Sugar** — Normal fasting: 70-99 mg/dL")
            sugar = st.number_input("Sugar mg/dL",30.0,700.0,110.0,key="sug",label_visibility="collapsed")
            if sugar>300: st.error("Critically HIGH")
            elif sugar<60: st.error("Critically LOW")
            elif sugar>180: st.warning("High")
            else: st.success("Normal")
        with v2:
            st.markdown("**Temperature** — Normal: 36.1-37.2°C")
            temp = st.number_input("Temp °C",34.0,43.0,36.8,step=0.1,format="%.1f",key="tmp",label_visibility="collapsed")
            if temp>=39.5: st.error("Very High Fever")
            elif temp>=37.5: st.warning("Fever")
            elif temp<35.5: st.error("Too Low")
            else: st.success("Normal")

    st.markdown("---")
    st.markdown("### Symptoms / الأعراض")
    syms = []
    c1,c2,c3,c4 = st.columns(4)
    if c1.checkbox("Cough / سعال",     key="sy1"): syms.append("cough")
    if c2.checkbox("Breathless / ضيق", key="sy2"): syms.append("breathlessness")
    if c3.checkbox("Chest Pain / صدر", key="sy3"): syms.append("chest_pain")
    if c4.checkbox("Dizziness / دوار", key="sy4"): syms.append("dizziness")
    if c1.checkbox("Fever / حمى",      key="sy5"): syms.append("fever")
    if c2.checkbox("Fatigue / إعياء",  key="sy6"): syms.append("fatigue")
    if c3.checkbox("Headache / صداع",  key="sy7"): syms.append("headache")
    if c4.checkbox("Nausea / غثيان",   key="sy8"): syms.append("nausea")

    extra = st.text_area("Other symptoms:", placeholder="Type in English or Arabic...", height=60, key="exs")
    if extra.strip():
        syms += normalize_symptoms([s.strip() for s in extra.replace(",","\n").splitlines() if s.strip()])
        syms  = list(set(syms))
    if syms: st.info(f"Selected: {', '.join(syms)}")
    if "chest_pain" in syms or "breathlessness" in syms:
        st.error("SERIOUS SYMPTOMS — Call 999 or go to Emergency tab!")

    if age <= 1:
        st.error("INFANT: Any fever over 38°C in babies under 3 months is a medical emergency!")

    st.markdown("""<div class="disclaimer">
        This is a health guide only. NOT a doctor. Emergency: <b>999</b></div>""",
        unsafe_allow_html=True)
    st.markdown("")

    if st.button("Assess My Health / تقييم صحتي", type="primary",
            use_container_width=True, key="assess"):
        err = validate_patient_input(
            name or "Patient", max(int(age),1),
            int(bps),int(bpd),float(sugar),float(temp))
        if err:
            st.error(err)
            return

        patient = Patient(
            name=name.strip() or "Patient",
            age=max(int(age),1),
            blood_pressure_systolic=int(bps),
            blood_pressure_diastolic=int(bpd),
            blood_sugar=float(sugar),
            temperature=float(temp),
            symptoms=syms,
            khareef_mode=st.session_state.khareef,
        )
        result = assess_patient(
            age=patient.age,
            bp_systolic=patient.blood_pressure_systolic,
            bp_diastolic=patient.blood_pressure_diastolic,
            blood_sugar=patient.blood_sugar,
            temperature=patient.temperature,
            symptoms=patient.symptoms,
            khareef_mode=patient.khareef_mode,
        )

        ai_result = None
        if st.session_state.use_ai and is_api_key_configured():
            with st.spinner("Getting AI advice..."):
                ai_result = get_gemini_advice(
                    patient_name=patient.name,
                    patient_age=patient.age,
                    bp_systolic=patient.blood_pressure_systolic,
                    bp_diastolic=patient.blood_pressure_diastolic,
                    blood_sugar=patient.blood_sugar,
                    temperature=patient.temperature,
                    symptoms=patient.symptoms,
                    triage_level=result["level"],
                    triage_reasons=result["reasons"],
                    khareef_mode=patient.khareef_mode,
                )

        # Save record
        rec = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "name":patient.name,"age":patient.age,
            "gender":st.session_state.gender,"city":st.session_state.user_city,
            "phone":st.session_state.user_phone,
            "conditions":", ".join(st.session_state.user_conditions) or "None",
            "bp":f"{bps}/{bpd}" if know else "Not measured",
            "blood_sugar":sugar if know else "Not measured",
            "temperature":temp if know else "Not measured",
            "symptoms":", ".join(syms) or "None",
            "triage_level":result["level"],
            "findings":" | ".join(result["reasons"])[:300],
            "ai_used":bool(ai_result and ai_result.get("success")),
        }
        save_record(rec)
        log_patient(patient, result)

        # Show result
        st.markdown("---")
        st.markdown(f"## Results for **{patient.name}**")
        level = result["level"]
        css   = {"GREEN":"result-green","YELLOW":"result-yellow","RED":"result-red"}[level]
        lbl   = {"GREEN":"ALL CLEAR","YELLOW":"ATTENTION NEEDED","RED":"URGENT"}[level]
        col   = {"GREEN":"#16a34a","YELLOW":"#d97706","RED":"#dc2626"}[level]
        lar   = {"GREEN":"بصحة جيدة","YELLOW":"يحتاج انتباهاً","RED":"عاجل"}[level]
        st.markdown(f"""
        <div class="{css}">
            <div style="font-size:1.8rem;font-weight:700;color:{col}">{lbl}</div>
            <div class="ar" style="color:{col};opacity:0.8">{lar}</div>
        </div>""", unsafe_allow_html=True)

        if know:
            m1,m2,m3,m4 = st.columns(4)
            m1.metric("BP",f"{bps}/{bpd}")
            m2.metric("Sugar",f"{int(sugar)} mg/dL")
            m3.metric("Temp",f"{temp:.1f}°C")
            m4.metric("Age",f"{int(age)} yrs")

        st.markdown("### Findings")
        for r in result["reasons"]: st.markdown(f"- {r}")

        st.markdown("---")
        if ai_result and ai_result.get("success"):
            st.markdown("### AI Medical Advice")
            st.info(ai_result["advice_en"])
            if st.session_state.show_arabic and ai_result.get("advice_ar"):
                st.markdown("### النصيحة الطبية")
                st.markdown(f'<div class="ar" style="background:#fffbf0;border-radius:10px;padding:16px;border:1px solid #fde68a;font-size:1.05rem;line-height:2">{ai_result["advice_ar"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown("### Medical Advice")
            st.info(result["rule_advice_en"])
            if st.session_state.show_arabic:
                st.markdown("### النصيحة الطبية")
                st.markdown(f'<div class="ar" style="background:#fffbf0;border-radius:10px;padding:16px;border:1px solid #fde68a;font-size:1.05rem;line-height:2">{result["rule_advice_ar"]}</div>', unsafe_allow_html=True)

        if level=="RED":
            st.error("Sultan Qaboos Hospital Salalah · Al Dahariz · 999 · +968 23 218 000")
            st.link_button("Open in Maps","https://maps.google.com/?q=Sultan+Qaboos+Hospital+Salalah+Oman")

        if result.get("nutrition"):
            st.markdown("### Nutrition Tips")
            for tip in result["nutrition"]:
                st.markdown(f'<div class="nutrition-tip">{tip}</div>', unsafe_allow_html=True)

        st.markdown("""<div class="disclaimer">
            Educational use only. Not medical advice. Emergency: <b>999</b></div>""",
            unsafe_allow_html=True)
