"""
main.py – Khareef Health Triage App
Run with: streamlit run main.py
"""

import streamlit as st
import pandas as pd
from data import Patient, validate_patient_input, normalize_symptoms, log_patient, get_session_log
from triage import assess_patient
from gemini_helper import get_gemini_advice, is_api_key_configured, get_api_key_status

st.set_page_config(
    page_title="Khareef Health",
    page_icon="🌿",
    layout="wide",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&family=Inter:wght@400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: linear-gradient(135deg, #e8f5ef 0%, #f0f9f4 50%, #e8f0f5 100%);
}

/* ── Header ── */
.app-header {
    background: linear-gradient(135deg, #0d3d29, #1a5c45);
    border-radius: 16px;
    padding: 24px 32px;
    margin-bottom: 24px;
    color: white;
    box-shadow: 0 4px 20px rgba(13,61,41,0.25);
}
.app-header h1 {
    font-size: 2rem;
    font-weight: 700;
    margin: 0;
    color: white;
}
.app-header .byline {
    font-size: 0.85rem;
    opacity: 0.7;
    margin-top: 4px;
}
.app-header .subtitle {
    font-size: 1rem;
    opacity: 0.85;
    margin-top: 4px;
}
.app-header .arabic {
    font-family: 'Tajawal', sans-serif;
    font-size: 0.95rem;
    opacity: 0.75;
    direction: rtl;
}

/* ── Cards ── */
.card {
    background: white;
    border-radius: 14px;
    padding: 24px;
    margin-bottom: 18px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    border-top: 4px solid #1a5c45;
}

/* ── Emergency Button ── */
.emergency-section {
    background: linear-gradient(135deg, #dc2626, #991b1b);
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 24px;
    text-align: center;
    color: white;
    box-shadow: 0 4px 20px rgba(220,38,38,0.3);
}

/* ── Steps ── */
.step {
    background: #f8fffe;
    border-left: 4px solid #1a5c45;
    border-radius: 8px;
    padding: 12px 16px;
    margin: 8px 0;
    font-size: 0.95rem;
}
.step-red {
    background: #fff5f5;
    border-left: 4px solid #dc2626;
    border-radius: 8px;
    padding: 12px 16px;
    margin: 8px 0;
    font-size: 0.95rem;
}

/* ── Arabic ── */
.arabic-text {
    font-family: 'Tajawal', sans-serif;
    direction: rtl;
    text-align: right;
    font-size: 1.1rem;
    line-height: 2;
    background: #fffbf0;
    border-radius: 10px;
    padding: 16px 20px;
    border: 1px solid #fde68a;
}

/* ── Disclaimer ── */
.disclaimer {
    background: #fff8e1;
    border: 1px solid #fcd34d;
    border-radius: 10px;
    padding: 12px 18px;
    font-size: 0.85rem;
    color: #78350f;
}

/* ── Nutrition ── */
.nutrition-tip {
    background: #f0fdf4;
    border-left: 3px solid #22c55e;
    border-radius: 6px;
    padding: 10px 14px;
    margin: 6px 0;
    font-size: 0.9rem;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: white;
    border-radius: 10px;
    padding: 4px;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    font-weight: 600;
    font-size: 0.95rem;
}

/* Hide streamlit menu */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════
with st.sidebar:
    st.markdown("## 🌿 Khareef Health")
    st.caption("by Sadga Selime")
    st.markdown("---")

    khareef_mode = st.toggle("🌦️ Khareef Mode", value=False,
        help="Turn ON during June-September monsoon season")
    if khareef_mode:
        st.success("Khareef Mode ON")

    st.markdown("---")
    show_arabic = st.toggle("🌐 Arabic / عربي", value=True)

    st.markdown("---")
    st.markdown("### 🤖 AI Status")
    st.caption(get_api_key_status())
    use_gemini = st.toggle("Use AI Advice", value=is_api_key_configured())

    st.markdown("---")
    st.markdown("### 🏥 Emergency")
    st.error("📞 **999**")
    st.markdown("**Sultan Qaboos Hospital**")
    st.markdown("📞 +968 23 218 000")
    st.markdown("📍 Al Dahariz, Salalah")

    st.markdown("---")
    show_log = st.toggle("📋 Session Log", value=False)

# ══════════════════════════════════════
# HEADER
# ══════════════════════════════════════
st.markdown("""
<div class="app-header">
    <h1>🌿 Khareef Health</h1>
    <div class="byline">by Sadga Selime</div>
    <div class="subtitle">AI Telemedicine Triage · Salalah, Dhofar, Oman</div>
    <div class="arabic">مساعد الفرز الطبي الذكي · صلالة، ظفار، عُمان</div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════
# EMERGENCY BUTTON — TOP OF PAGE
# ══════════════════════════════════════
st.markdown("""
<div class="emergency-section">
    <div style="font-size:2.5rem">🚨</div>
    <div style="font-size:1.4rem; font-weight:700; margin:8px 0">EMERGENCY GUIDE</div>
    <div style="opacity:0.85; font-size:0.95rem">CPR · Heart Attack · Choking · Fainting</div>
</div>
""", unsafe_allow_html=True)

show_emergency = st.toggle("🚨 Open Emergency First Aid Guide", value=False)

if show_emergency:
    st.error("⚠️ If life is in danger — call 999 FIRST, then follow these steps")

    em1, em2 = st.columns(2)

    with em1:
        st.markdown("#### ❤️ Heart Attack Signs")
        for step in [
            "1. Call 999 immediately",
            "2. Ask patient to sit down and rest",
            "3. Loosen tight clothing around neck and chest",
            "4. Give aspirin 300mg if available and not allergic",
            "5. Stay with patient until ambulance arrives",
            "6. Do NOT give food or water",
        ]:
            st.markdown(f'<div class="step-red">{step}</div>', unsafe_allow_html=True)

        st.markdown("#### 😮‍💨 Choking — Adult")
        for step in [
            "1. Ask: Are you choking? Can you speak?",
            "2. Tell them to cough hard",
            "3. Give 5 firm back blows between shoulder blades",
            "4. Give 5 abdominal thrusts (Heimlich manoeuvre)",
            "5. Repeat until object comes out",
            "6. Call 999 if unconscious",
        ]:
            st.markdown(f'<div class="step">{step}</div>', unsafe_allow_html=True)

    with em2:
        st.markdown("#### 💓 CPR Steps")
        for step in [
            "1. Check the person is unresponsive — tap shoulder",
            "2. Call 999 immediately",
            "3. Lay person flat on their back",
            "4. Place heel of hand on centre of chest",
            "5. Push down hard and fast — 30 times",
            "6. Tilt head back, lift chin, give 2 breaths",
            "7. Repeat 30 compressions + 2 breaths",
            "8. Continue until help arrives",
        ]:
            st.markdown(f'<div class="step-red">{step}</div>', unsafe_allow_html=True)

        st.markdown("#### 😵 Fainting")
        for step in [
            "1. Lay person flat on the ground",
            "2. Raise their legs above heart level",
            "3. Loosen tight clothing",
            "4. Do NOT give water while unconscious",
            "5. Turn on side if vomiting",
            "6. Call 999 if not waking up within 1 minute",
        ]:
            st.markdown(f'<div class="step">{step}</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 🏥 Nearest Hospitals in Salalah")
    col_h1, col_h2, col_h3 = st.columns(3)
    with col_h1:
        st.info("**Sultan Qaboos Hospital**\n📞 +968 23 218 000\n📍 Al Dahariz")
    with col_h2:
        st.info("**Salalah Private Hospital**\n📞 +968 23 295 999\n📍 Salalah")
    with col_h3:
        st.info("**Emergency**\n📞 **999**\n🕐 24 hours")

    st.link_button("📍 Sultan Qaboos Hospital on Google Maps",
        "https://maps.google.com/?q=Sultan+Qaboos+Hospital+Salalah+Oman")

st.markdown("---")

# ══════════════════════════════════════
# TABS — SEPARATE PAGES
# ══════════════════════════════════════
tab1, tab2, tab3 = st.tabs(["🩺 Patient Assessment", "💊 Medicine Guide", "ℹ️ About"])

# ══════════════════════════════════════
# TAB 1 — PATIENT ASSESSMENT
# ══════════════════════════════════════
with tab1:

    if khareef_mode:
        st.warning("🌦️ Khareef Mode Active — Higher respiratory sensitivity")
    if not is_api_key_configured():
        st.info("ℹ️ Using rule-based advice — add Gemini key to enable AI.")

    # ── PATIENT INFO ──
    st.markdown("### 👤 Patient Information")
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Full Name / الاسم الكامل",
            placeholder="e.g. Ahmed Al-Shanfari")
    with col2:
        age = st.number_input("Age / العمر", min_value=1, max_value=120, value=65)
        if age >= 60:
            st.caption("👴 Elderly — higher risk monitoring active")

    st.markdown("---")

    # ── BLOOD PRESSURE — SEPARATE ──
    st.markdown("### 🩺 Blood Pressure / ضغط الدم")
    st.caption("Enter the two numbers from your blood pressure reading")

    bp_col1, bp_col2 = st.columns(2)

    with bp_col1:
        st.markdown("#### Upper Number (Systolic) / الانقباضي")
        st.caption("Normal: between 90 and 120")
        bp_systolic = st.number_input("Systolic",
            min_value=60, max_value=240, value=120, label_visibility="collapsed")
        if bp_systolic >= 180:
            st.error("🔴 Dangerously HIGH")
        elif bp_systolic < 90:
            st.error("🔴 Dangerously LOW")
        elif bp_systolic >= 140:
            st.warning("🟡 High — monitor")
        else:
            st.success("🟢 Normal")

    with bp_col2:
        st.markdown("#### Lower Number (Diastolic) / الانبساطي")
        st.caption("Normal: between 60 and 80")
        bp_diastolic = st.number_input("Diastolic",
            min_value=40, max_value=140, value=80, label_visibility="collapsed")
        if bp_diastolic >= 120:
            st.error("🔴 Dangerously HIGH")
        elif bp_diastolic < 60:
            st.error("🔴 Dangerously LOW")
        elif bp_diastolic >= 90:
            st.warning("🟡 High — monitor")
        else:
            st.success("🟢 Normal")

    st.markdown(f"**Combined reading: {bp_systolic}/{bp_diastolic} mmHg**")
    st.markdown("---")

    # ── BLOOD SUGAR & TEMP ──
    st.markdown("### 🩸 Blood Sugar & 🌡️ Temperature")
    col3, col4 = st.columns(2)

    with col3:
        st.markdown("#### Blood Sugar / سكر الدم")
        st.caption("Normal fasting: 70–99 mg/dL")
        blood_sugar = st.number_input("Blood Sugar (mg/dL)",
            min_value=30.0, max_value=700.0, value=110.0, step=1.0,
            label_visibility="collapsed")
        if blood_sugar > 300:
            st.error("🔴 Critically HIGH")
        elif blood_sugar < 60:
            st.error("🔴 Critically LOW")
        elif blood_sugar > 180:
            st.warning("🟡 High")
        else:
            st.success("🟢 Normal")

    with col4:
        st.markdown("#### Temperature / الحرارة")
        st.caption("Normal: 36.1°C – 37.2°C")
        temperature = st.number_input("Temperature (°C)",
            min_value=34.0, max_value=43.0, value=36.8,
            step=0.1, format="%.1f", label_visibility="collapsed")
        if temperature >= 39.5:
            st.error("🔴 Very High Fever")
        elif temperature >= 37.5:
            st.warning("🟡 Fever")
        elif temperature < 35.5:
            st.error("🔴 Too Low")
        else:
            st.success("🟢 Normal")

    st.markdown("---")

    # ── SYMPTOMS ──
    st.markdown("### 🤒 Symptoms / الأعراض")
    st.caption("Select all that apply")

    selected_symptoms = []
    c1, c2, c3, c4 = st.columns(4)
    if c1.checkbox("Cough / سعال"):             selected_symptoms.append("cough")
    if c2.checkbox("Breathlessness / ضيق"):     selected_symptoms.append("breathlessness")
    if c3.checkbox("Chest Pain / الم الصدر"):  selected_symptoms.append("chest_pain")
    if c4.checkbox("Dizziness / دوار"):         selected_symptoms.append("dizziness")
    if c1.checkbox("Fever / حمى"):              selected_symptoms.append("fever")
    if c2.checkbox("Fatigue / اعياء"):          selected_symptoms.append("fatigue")
    if c3.checkbox("Headache / صداع"):          selected_symptoms.append("headache")
    if c4.checkbox("Nausea / غثيان"):           selected_symptoms.append("nausea")

    extra = st.text_area("Other symptoms / أعراض أخرى:",
        placeholder="Type in English or Arabic...", height=60)
    if extra.strip():
        extras = [s.strip() for s in extra.replace(",", "\n").splitlines() if s.strip()]
        selected_symptoms.extend(normalize_symptoms(extras))
        selected_symptoms = list(set(selected_symptoms))

    if selected_symptoms:
        st.info(f"Selected: {', '.join(selected_symptoms)}")

    st.markdown("---")

    # ── TRUST & SAFETY ──
    st.markdown("""
    <div class="disclaimer">
        ⚠️ <strong>Important:</strong> This app is a health guide only.
        It is NOT a doctor. Always consult a qualified medical professional.
        For emergencies call <strong>999</strong> immediately.
    </div>
    """, unsafe_allow_html=True)
    st.markdown("")

    # ── ASSESS BUTTON ──
    if st.button("🔍 Assess My Health / تقييم صحتي",
            type="primary", use_container_width=True):

        # Force emergency for serious symptoms
        if "chest_pain" in selected_symptoms or "breathlessness" in selected_symptoms:
            st.error("🚨 SERIOUS SYMPTOMS DETECTED — Please call 999 now or go to Sultan Qaboos Hospital immediately!")

        error = validate_patient_input(
            name, int(age), int(bp_systolic), int(bp_diastolic),
            float(blood_sugar), float(temperature)
        )

        if error:
            st.error(error)
        else:
            patient = Patient(
                name=name.strip(),
                age=int(age),
                blood_pressure_systolic=int(bp_systolic),
                blood_pressure_diastolic=int(bp_diastolic),
                blood_sugar=float(blood_sugar),
                temperature=float(temperature),
                symptoms=selected_symptoms,
                khareef_mode=khareef_mode,
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
            if use_gemini and is_api_key_configured():
                with st.spinner("🤖 Getting AI advice..."):
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

            log_patient(patient, result)

            st.markdown("---")
            st.markdown(f"## Results for **{patient.name}**")

            level = result["level"]
            if level == "GREEN":
                st.success("## 🟢 GREEN — All Clear")
            elif level == "YELLOW":
                st.warning("## 🟡 YELLOW — Attention Needed")
            else:
                st.error("## 🔴 RED — URGENT: Go to Hospital Now")

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("🩺 BP", f"{bp_systolic}/{bp_diastolic}")
            m2.metric("🩸 Sugar", f"{int(blood_sugar)} mg/dL")
            m3.metric("🌡️ Temp", f"{temperature:.1f}°C")
            m4.metric("👤 Age", f"{int(age)} yrs")

            st.markdown("### 🔍 Findings")
            for r in result["reasons"]:
                st.markdown(f"- {r}")

            st.markdown("---")
            if ai_result and ai_result["success"]:
                st.markdown("### 💬 AI Medical Advice ✨")
                st.info(ai_result["advice_en"])
                if show_arabic and ai_result["advice_ar"]:
                    st.markdown("### النصيحة الطبية")
                    st.markdown(
                        f'<div class="arabic-text">{ai_result["advice_ar"]}</div>',
                        unsafe_allow_html=True)
            else:
                st.markdown("### 💬 Medical Advice")
                st.info(result["rule_advice_en"])
                if show_arabic:
                    st.markdown("### النصيحة الطبية")
                    st.markdown(
                        f'<div class="arabic-text">{result["rule_advice_ar"]}</div>',
                        unsafe_allow_html=True)

            if level == "RED":
                st.markdown("---")
                st.error(
                    "🚨 **Go to Sultan Qaboos Hospital NOW**\n\n"
                    "📍 Al Dahariz, Salalah · 📞 999 · +968 23 218 000"
                )
                st.link_button("📍 Open in Google Maps",
                    "https://maps.google.com/?q=Sultan+Qaboos+Hospital+Salalah+Oman")

            if result["nutrition"]:
                st.markdown("---")
                st.markdown("### 🥗 Nutrition Tips")
                for tip in result["nutrition"]:
                    st.markdown(
                        f'<div class="nutrition-tip">{tip}</div>',
                        unsafe_allow_html=True)

            st.markdown("---")
            st.markdown("""
            <div class="disclaimer">
                ⚠️ This tool is for educational purposes only.
                It is NOT a substitute for professional medical advice.
                Always consult a licensed doctor. Emergency: <strong>999</strong>
            </div>
            """, unsafe_allow_html=True)

# ══════════════════════════════════════
# TAB 2 — MEDICINE GUIDE
# ══════════════════════════════════════
with tab2:
    st.markdown("### 💊 Basic Medicine Information Guide")
    st.markdown("""
    <div class="disclaimer">
        ⚠️ This is general information only. Always follow your doctor's prescription.
        Never change your dose without consulting a doctor.
    </div>
    """, unsafe_allow_html=True)
    st.markdown("")

    medicines = {
        "Paracetamol (Panadol)": {
            "for": "Fever, headache, mild pain",
            "dose": "500mg–1000mg every 4–6 hours. Max 4 doses per day.",
            "warning": "Do not exceed 4g per day. Avoid alcohol. Be careful with liver problems.",
            "avoid": "Liver disease, heavy alcohol use",
        },
        "Ibuprofen (Brufen)": {
            "for": "Pain, inflammation, fever",
            "dose": "200mg–400mg every 6–8 hours with food.",
            "warning": "Take with food. Avoid on empty stomach.",
            "avoid": "Kidney problems, stomach ulcers, pregnancy (3rd trimester)",
        },
        "Metformin": {
            "for": "Type 2 diabetes — lowers blood sugar",
            "dose": "As prescribed by doctor. Usually with meals.",
            "warning": "Take with food to reduce nausea. Stay hydrated.",
            "avoid": "Kidney problems. Stop before surgery or CT scans.",
        },
        "Amlodipine": {
            "for": "High blood pressure, chest pain (angina)",
            "dose": "5mg–10mg once daily. As prescribed.",
            "warning": "May cause ankle swelling. Do not stop suddenly.",
            "avoid": "Low blood pressure",
        },
        "Omeprazole": {
            "for": "Stomach acid, heartburn, ulcers",
            "dose": "20mg once daily before eating.",
            "warning": "Take 30 minutes before meals for best effect.",
            "avoid": "Long-term use without doctor advice",
        },
        "Salbutamol (Ventolin)": {
            "for": "Asthma, wheezing, breathlessness",
            "dose": "1–2 puffs when needed. Max 4 times daily.",
            "warning": "If needed more than 3 times per week — see a doctor.",
            "avoid": "Heart rhythm problems",
        },
    }

    selected_med = st.selectbox("Select a medicine to learn about:",
        list(medicines.keys()))

    if selected_med:
        med = medicines[selected_med]
        st.markdown(f"### 💊 {selected_med}")

        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.success(f"**✅ Used for:**\n{med['for']}")
            st.info(f"**💊 Usual Dose:**\n{med['dose']}")
        with col_m2:
            st.warning(f"**⚠️ Warning:**\n{med['warning']}")
            st.error(f"**🚫 Avoid if:**\n{med['avoid']}")

    st.markdown("---")
    st.markdown("""
    <div class="disclaimer">
        ⚠️ <strong>Disclaimer:</strong> This medicine information is for general knowledge only.
        It does not replace a doctor's prescription or pharmacist's advice.
        Always consult a qualified healthcare professional before taking any medication.
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════
# TAB 3 — ABOUT
# ══════════════════════════════════════
with tab3:
    st.markdown("### 🌿 About Khareef Health")
    st.markdown("""
    **Khareef Health** is an AI-powered medical triage assistant built for
    the community of Salalah, Dhofar, Oman.

    It helps patients understand their health readings and decide whether
    they need urgent care, monitoring, or simply reassurance.
    """)

    st.markdown("### 👨‍💻 Developer")
    st.info("**Sadga Selime**\nSalalah, Dhofar, Oman\nBuilt with Python, Streamlit & Google Gemini AI")

    st.markdown("### 🏥 Emergency Contacts — Salalah")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.error("**Emergency**\n📞 999")
    with c2:
        st.info("**Sultan Qaboos Hospital**\n📞 +968 23 218 000")
    with c3:
        st.info("**Salalah Private Hospital**\n📞 +968 23 295 999")

    st.markdown("### ⚠️ Medical Disclaimer")
    st.markdown("""
    <div class="disclaimer">
        This application is for <strong>educational and informational purposes only</strong>.
        It does NOT replace a qualified medical professional, licensed doctor, or pharmacist.
        Always consult a healthcare provider for diagnosis and treatment.
        In any medical emergency, call <strong>999</strong> immediately.
        The developer is not liable for any medical decisions made based on this app.
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════
# SESSION LOG
# ══════════════════════════════════════
if show_log:
    st.markdown("---")
    st.markdown("## 📋 Session Log")
    log = get_session_log()
    if log:
        st.dataframe(pd.DataFrame(log), use_container_width=True)
    else:
        st.info("No assessments yet.")

# ── FOOTER ──
st.markdown("---")
st.caption("🌿 Khareef Health · by Sadga Selime · Salalah, Oman · Powered by Google Gemini AI · Educational use only")
