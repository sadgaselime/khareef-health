# tabs/tab_assess.py  — PATCHED VERSION
# Changes:
#   1. Removed allergy field
#   2. Injects user profile context into every AI/Gemini call
#   3. Voice input responses now use profile for personalised answers
#   4. Free-text symptom analysis uses profile

import streamlit as st

def render(T, save_record, log_patient, is_api_key_configured,
           get_gemini_advice, analyze_free_text, RECORDS_FILE):

    lang = st.session_state.get("language", "English")
    g    = T['g']; p = T['p']; l = T['l']

    # ── Pull profile from session ──────────────────────────────
    user_name   = st.session_state.get("user_name", "")
    user_age    = st.session_state.get("user_age", 40)
    gender      = st.session_state.get("gender", "Not specified")
    city        = st.session_state.get("user_city", "Salalah")
    conditions  = st.session_state.get("user_conditions", [])
    medications = st.session_state.get("user_medications", "").strip()
    blood_type  = st.session_state.get("user_blood_type", "Unknown")
    khareef     = st.session_state.get("khareef", False)
    use_ai      = st.session_state.get("use_ai", False)

    # Profile context string for AI calls
    profile_ctx = st.session_state.get("_profile_context", "")

    st.markdown(f"""
    <div style="background:linear-gradient({g});border-radius:16px;padding:20px 28px;
         color:white;margin-bottom:16px;">
        <h2 style="margin:0;font-size:1.4rem">🩺 Health Check / فحص الصحة</h2>
        <p style="margin:4px 0 0;opacity:0.85;font-size:0.88rem">
            Enter your vitals and symptoms for AI-powered triage</p>
    </div>""", unsafe_allow_html=True)

    # ── Show profile summary if available ─────────────────────
    if user_name:
        st.info(f"👤 Checking for **{user_name}** · Age {user_age} · {gender} · {city}"
                + (f" · Conditions: {', '.join(conditions)}" if conditions else "")
                + (f" · Meds: {medications}" if medications else ""))

    st.markdown("### 📊 Vital Signs")
    c1, c2, c3 = st.columns(3)
    with c1:
        temp = st.number_input("🌡️ Temperature (°C)", 35.0, 42.0, 37.0, 0.1)
    with c2:
        hr   = st.number_input("💓 Heart Rate (bpm)", 40, 200, 80)
    with c3:
        spo2 = st.number_input("🫁 SpO2 (%)", 70, 100, 98)

    c4, c5 = st.columns(2)
    with c4:
        sbp = st.number_input("🩸 Systolic BP (mmHg)", 70, 220, 120)
    with c5:
        dbp = st.number_input("🩸 Diastolic BP (mmHg)", 40, 140, 80)

    st.markdown("### 🤒 Symptoms")

    # Symptom checkboxes — no allergy field
    sym_cols = st.columns(3)
    symptom_list = [
        ("fever",        "🌡️ Fever"),
        ("headache",     "🤕 Headache"),
        ("cough",        "😮‍💨 Cough"),
        ("sob",          "😮 Shortness of Breath"),
        ("chest_pain",   "💔 Chest Pain"),
        ("nausea",       "🤢 Nausea / Vomiting"),
        ("diarrhea",     "🚽 Diarrhea"),
        ("fatigue",      "😴 Fatigue"),
        ("dizziness",    "😵 Dizziness"),
        ("joint_pain",   "🦴 Joint / Muscle Pain"),
        ("rash",         "🔴 Skin Rash"),
        ("sore_throat",  "😣 Sore Throat"),
    ]
    selected_symptoms = []
    for i, (key, label) in enumerate(symptom_list):
        with sym_cols[i % 3]:
            if st.checkbox(label, key=f"sym_{key}"):
                selected_symptoms.append(label.split(" ", 1)[1])  # strip emoji

    # Free-text / voice input
    st.markdown("### 💬 Describe your problem")
    st.caption("Type or speak — be specific. The AI will use your saved profile.")

    free_text = st.text_area(
        "Describe symptoms in detail (the more specific, the better):",
        placeholder="e.g. I have had a throbbing headache behind my eyes for 2 days with mild fever...",
        height=100, key="assess_free_text"
    )

    duration = st.selectbox("⏱️ How long have you had these symptoms?",
        ["< 1 day", "1–2 days", "3–5 days", "1–2 weeks", "> 2 weeks"])

    pain_level = st.slider("😣 Pain / Discomfort Level", 0, 10, 3,
        help="0 = no pain, 10 = worst imaginable")

    # ── Assess button ──────────────────────────────────────────
    st.markdown("---")
    if st.button("🔍 Assess My Health / تقييم صحتي", type="primary",
                 use_container_width=True, key="assess_btn"):

        # Build vitals dict
        vitals = {
            "temperature": temp, "heart_rate": hr, "spo2": spo2,
            "systolic_bp": sbp, "diastolic_bp": dbp,
        }

        # Triage logic
        flags = []
        level = "GREEN"

        if temp >= 39.0:     flags.append("High fever"); level = "YELLOW"
        if temp >= 40.0:     level = "RED"
        if spo2 < 94:        flags.append("Low oxygen"); level = "RED"
        if spo2 < 96:        flags.append("Borderline SpO2"); level = max(level, "YELLOW") if level != "RED" else level
        if hr > 120 or hr < 50: flags.append("Abnormal heart rate"); level = "YELLOW"
        if sbp > 180 or sbp < 80: flags.append("Abnormal BP"); level = "RED"
        if "Chest Pain" in selected_symptoms: flags.append("Chest pain"); level = "RED"
        if "Shortness of Breath" in selected_symptoms: flags.append("Shortness of breath"); level = "RED" if spo2 < 96 else max(level, "YELLOW")
        if pain_level >= 8: flags.append(f"Severe pain ({pain_level}/10)"); level = max(level, "YELLOW") if level != "RED" else level
        if khareef and "Cough" in selected_symptoms: flags.append("Khareef respiratory risk")

        # Upgrade YELLOW to RED if multiple RED triggers
        red_count = sum(1 for f in flags if any(w in f for w in ["oxygen","BP","Chest","fever"]))
        if red_count >= 2: level = "RED"

        # Display result
        color_map = {"GREEN": "result-green", "YELLOW": "result-yellow", "RED": "result-red"}
        emoji_map = {"GREEN": "✅", "YELLOW": "⚠️", "RED": "🚨"}
        msg_map   = {
            "GREEN":  "Your readings look normal. Rest and monitor.",
            "YELLOW": "Some concerns noted. See a doctor soon.",
            "RED":    "URGENT — Please go to the hospital NOW or call 999.",
        }

        st.markdown(f"""
        <div class="{color_map[level]}" style="margin:16px 0">
            <div style="font-size:3rem">{emoji_map[level]}</div>
            <div style="font-size:2rem;font-weight:800">{level}</div>
            <div style="font-size:1rem;margin-top:8px">{msg_map[level]}</div>
            {"<div style='margin-top:10px;font-size:0.85rem'><b>Concerns:</b> " + " · ".join(flags) + "</div>" if flags else ""}
        </div>""", unsafe_allow_html=True)

        if level == "RED":
            st.error("📞 **Call 999** or go to Sultan Qaboos Hospital, Al Dahariz, Salalah immediately.")

        # ── AI advice with profile context ────────────────────
        if use_ai and is_api_key_configured():
            with st.spinner("🤖 Getting personalised AI advice..."):
                try:
                    # Build a rich prompt that includes the user profile
                    symptom_str = ", ".join(selected_symptoms) if selected_symptoms else "none selected"
                    
                    prompt_with_profile = f"""{profile_ctx}

CURRENT ASSESSMENT:
- Triage level: {level}
- Vitals: Temp {temp}°C, HR {hr} bpm, SpO2 {spo2}%, BP {sbp}/{dbp} mmHg
- Symptoms reported: {symptom_str}
- Duration: {duration}
- Pain level: {pain_level}/10
- Patient's own description: {free_text if free_text.strip() else 'Not provided'}
- Flags identified: {', '.join(flags) if flags else 'None'}

Please provide:
1. A brief personalised assessment addressing {user_name if user_name else 'the patient'} by name
2. Most likely cause(s) given their age ({user_age}), gender ({gender}), and conditions ({', '.join(conditions) if conditions else 'none'})
3. Specific home care steps if GREEN/YELLOW, or urgent steps if RED
4. Any medication interactions to watch (they take: {medications if medications else 'nothing listed'})
5. When to seek immediate help
6. A brief Arabic summary (النصيحة بالعربية)

Be specific and human. Do NOT give generic disclaimers. This is a triage assistant."""

                    advice = get_gemini_advice(prompt_with_profile)
                    
                    st.markdown("### 🤖 AI Health Advice")
                    st.markdown(advice)

                except Exception as e:
                    st.warning(f"AI advice unavailable: {e}")

        elif free_text.strip() and use_ai and is_api_key_configured():
            # Free-text only analysis
            with st.spinner("Analysing your description..."):
                try:
                    enriched = f"{profile_ctx}\n\nPatient describes: {free_text}"
                    result = analyze_free_text(enriched)
                    st.markdown("### 📝 Symptom Analysis")
                    st.markdown(result)
                except Exception as e:
                    st.warning(f"Analysis unavailable: {e}")

        # ── Save record ───────────────────────────────────────
        record = {
            "timestamp":   str(st.session_state.get("sid","")) + "_" + 
                           __import__("datetime").datetime.now().strftime("%Y%m%d_%H%M%S"),
            "date":        __import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M"),
            "name":        user_name or "Anonymous",
            "age":         user_age,
            "gender":      gender,
            "triage":      level,
            "vitals":      vitals,
            "symptoms":    selected_symptoms,
            "free_text":   free_text,
            "pain":        pain_level,
            "duration":    duration,
            "flags":       flags,
        }
        try:
            save_record(record)
        except Exception:
            pass

    # ── Disclaimer ─────────────────────────────────────────────
    st.markdown("""
    <div class="disclaimer">
    ⚕️ <b>Medical Disclaimer:</b> This tool provides educational triage guidance only.
    It is NOT a substitute for professional medical diagnosis or treatment.
    Always consult a qualified healthcare provider for medical advice.
    In emergencies, call <b>999</b> immediately.
    </div>""", unsafe_allow_html=True)
