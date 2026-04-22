"""
main.py – Khareef Health Triage App
Run with: streamlit run main.py
"""

import streamlit as st
import pandas as pd
from data import Patient, validate_patient_input, normalize_symptoms, log_patient, get_session_log
from triage import assess_patient
from gemini_helper import get_gemini_advice, is_api_key_configured, get_api_key_status

# ── Page config (MUST be first Streamlit command) ──
st.set_page_config(
    page_title="Khareef Health",
    page_icon="🌿",
    layout="wide",
)

# ── Simple CSS ──
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
.stApp { background: #f0f9f4; }
.arabic { font-family: 'Tajawal', sans-serif; direction: rtl; text-align: right; font-size: 1.1rem; line-height: 2; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════
with st.sidebar:
    st.markdown("## 🌿 Khareef Health")
    st.markdown("AI Triage Assistant — Salalah, Oman")
    st.markdown("---")

    khareef_mode = st.toggle("🌦️ Khareef Mode", value=False,
        help="Turn ON during June-September monsoon season")
    if khareef_mode:
        st.success("Khareef Mode ON — Higher respiratory sensitivity")

    st.markdown("---")
    show_arabic = st.toggle("🌐 Show Arabic / عرض العربية", value=True)

    st.markdown("---")
    st.markdown("### 🤖 Gemini AI Status")
    st.write(get_api_key_status())
    use_gemini = st.toggle("Use AI Advice", value=is_api_key_configured())

    st.markdown("---")
    st.markdown("### 🏥 Emergency")
    st.markdown("**Sultan Qaboos Hospital**")
    st.markdown("📞 Emergency: **999**")
    st.markdown("📞 +968 23 218 000")

    st.markdown("---")
    show_log = st.toggle("📋 Session Log", value=False)

# ══════════════════════════════════════
# HEADER
# ══════════════════════════════════════
st.title("🌿 Khareef Health  |  by Sadga Selime")
st.subheader("AI Telemedicine Triage · Salalah, Dhofar, Oman")
st.markdown("**مساعد الفرز الطبي الذكي · صلالة، ظفار، عُمان**")
st.caption("👨‍💻 Designed & Built by Sadga Selime")
if khareef_mode:
    st.warning("🌦️ Khareef Mode Active — Respiratory symptoms monitored with higher sensitivity")

if not is_api_key_configured():
    st.info("ℹ️ No Gemini API key found — using rule-based advice. Add key to .env to enable AI.")

st.markdown("---")

# ══════════════════════════════════════
# PATIENT INFO
# ══════════════════════════════════════
st.markdown("### 👤 Patient Information / معلومات المريض")

col1, col2 = st.columns(2)
with col1:
    name = st.text_input("Full Name / الاسم الكامل", placeholder="e.g. Ahmed Al-Shanfari")
with col2:
    age = st.number_input("Age / العمر", min_value=1, max_value=120, value=65)
    if age >= 60:
        st.caption("👴 Elderly patient — higher risk monitoring active")

st.markdown("---")

# ══════════════════════════════════════
# VITAL SIGNS
# ══════════════════════════════════════
st.markdown("### 🩺 Vital Signs / العلامات الحيوية")

st.markdown("**Blood Pressure / ضغط الدم**")
bp1, bp2, bp3 = st.columns(3)
with bp1:
    bp_systolic = st.number_input("Systolic (upper) / الانقباضي", min_value=60, max_value=240, value=120)
with bp2:
    bp_diastolic = st.number_input("Diastolic (lower) / الانبساطي", min_value=40, max_value=140, value=80)
with bp3:
    st.markdown("**BP Status:**")
    if bp_systolic >= 180 or bp_diastolic >= 120:
        st.error(f"🔴 CRISIS: {bp_systolic}/{bp_diastolic}")
    elif bp_systolic < 90 or bp_diastolic < 60:
        st.error(f"🔴 LOW: {bp_systolic}/{bp_diastolic}")
    elif bp_systolic >= 140 or bp_diastolic >= 90:
        st.warning(f"🟡 HIGH: {bp_systolic}/{bp_diastolic}")
    else:
        st.success(f"🟢 NORMAL: {bp_systolic}/{bp_diastolic}")

st.markdown("")

col3, col4 = st.columns(2)
with col3:
    blood_sugar = st.number_input("🩸 Blood Sugar / سكر الدم (mg/dL)",
        min_value=30.0, max_value=700.0, value=110.0, step=1.0)
    if blood_sugar > 300:
        st.error("🔴 Critically HIGH")
    elif blood_sugar < 60:
        st.error("🔴 Critically LOW")
    elif blood_sugar > 180:
        st.warning("🟡 High")
    else:
        st.success("🟢 Normal")

with col4:
    temperature = st.number_input("🌡️ Temperature / درجة الحرارة (°C)",
        min_value=34.0, max_value=43.0, value=36.8, step=0.1, format="%.1f")
    if temperature >= 39.5:
        st.error("🔴 Very High Fever")
    elif temperature >= 37.5:
        st.warning("🟡 Fever")
    elif temperature < 35.5:
        st.error("🔴 Too Low")
    else:
        st.success("🟢 Normal")

st.markdown("---")

# ══════════════════════════════════════
# SYMPTOMS
# ══════════════════════════════════════
st.markdown("### 🤒 Symptoms / الأعراض")
st.caption("Select all that apply / اختر جميع ما ينطبق")

selected_symptoms = []
c1, c2, c3, c4 = st.columns(4)

if c1.checkbox("Cough / سعال"):              selected_symptoms.append("cough")
if c2.checkbox("Breathlessness / ضيق"):      selected_symptoms.append("breathlessness")
if c3.checkbox("Chest Pain / الم الصدر"):   selected_symptoms.append("chest_pain")
if c4.checkbox("Dizziness / دوار"):          selected_symptoms.append("dizziness")
if c1.checkbox("Fever / حمى"):               selected_symptoms.append("fever")
if c2.checkbox("Fatigue / اعياء"):           selected_symptoms.append("fatigue")
if c3.checkbox("Headache / صداع"):           selected_symptoms.append("headache")
if c4.checkbox("Nausea / غثيان"):            selected_symptoms.append("nausea")

extra = st.text_area("Other symptoms / أعراض أخرى:",
    placeholder="Type here in English or Arabic...", height=70)
if extra.strip():
    extras = [s.strip() for s in extra.replace(",", "\n").splitlines() if s.strip()]
    selected_symptoms.extend(normalize_symptoms(extras))
    selected_symptoms = list(set(selected_symptoms))

if selected_symptoms:
    st.info(f"Selected: {', '.join(selected_symptoms)}")

st.markdown("---")

# ══════════════════════════════════════
# ASSESS BUTTON
# ══════════════════════════════════════
if st.button("🔍 Assess My Health / تقييم صحتي", type="primary", use_container_width=True):

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
            with st.spinner("🤖 Getting AI advice from Gemini..."):
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
            st.error("## 🔴 RED — URGENT: Seek Help Now")

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("🩺 Blood Pressure", f"{bp_systolic}/{bp_diastolic} mmHg")
        m2.metric("🩸 Blood Sugar", f"{int(blood_sugar)} mg/dL")
        m3.metric("🌡️ Temperature", f"{temperature:.1f} C")
        m4.metric("👤 Age", f"{int(age)} years")

        st.markdown("### 🔍 Findings")
        for r in result["reasons"]:
            st.markdown(f"- {r}")

        st.markdown("---")
        if ai_result and ai_result["success"]:
            st.markdown("### 💬 Medical Advice (AI)")
            st.info(ai_result["advice_en"])
            if show_arabic and ai_result["advice_ar"]:
                st.markdown("### النصيحة الطبية")
                st.markdown(f'<div class="arabic">{ai_result["advice_ar"]}</div>',
                    unsafe_allow_html=True)
        else:
            st.markdown("### 💬 Medical Advice")
            st.info(result["rule_advice_en"])
            if show_arabic:
                st.markdown("### النصيحة الطبية")
                st.markdown(f'<div class="arabic">{result["rule_advice_ar"]}</div>',
                    unsafe_allow_html=True)

        if level == "RED":
            st.markdown("---")
            st.error(
                "🚨 Go to Sultan Qaboos Hospital Salalah NOW\n\n"
                "Al Dahariz, Salalah · Emergency: 999 · +968 23 218 000"
            )
            st.link_button("📍 Open in Google Maps",
                "https://maps.google.com/?q=Sultan+Qaboos+Hospital+Salalah+Oman")

        if result["nutrition"]:
            st.markdown("---")
            st.markdown("### 🥗 Nutrition Tips")
            for tip in result["nutrition"]:
                st.markdown(f"- {tip}")

        st.markdown("---")
        st.caption("This tool is for educational purposes only. Not medical advice. Emergency: 999")

if show_log:
    st.markdown("---")
    st.markdown("## 📋 Session Log")
    log = get_session_log()
    if log:
        st.dataframe(pd.DataFrame(log), use_container_width=True)
    else:
        st.info("No assessments yet.")

st.markdown("---")
st.caption("🌿 Khareef Health · Designed by Sadga Selime · Salalah, Oman · Powered by Google Gemini AI")
