"""
main.py – Khareef Health v3.0
Complete redesign with gender themes, voice input,
tabbed layout, user storage, emergency images, and more.
Run with: streamlit run main.py
"""

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import json
import os
from datetime import datetime
from data import Patient, validate_patient_input, normalize_symptoms, log_patient, get_session_log
from triage import assess_patient
from gemini_helper import get_gemini_advice, is_api_key_configured, get_api_key_status

# ══════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════
st.set_page_config(
    page_title="Khareef Health",
    page_icon=":herb:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════
# USER DATA STORAGE
# ══════════════════════════════════════
DATA_FILE = "user_records.json"

def load_records():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except:
            return []
    return []

def save_record(record):
    records = load_records()
    records.append(record)
    with open(DATA_FILE, "w") as f:
        json.dump(records, f, indent=2)

# ══════════════════════════════════════
# SESSION STATE INIT
# ══════════════════════════════════════
if "gender" not in st.session_state:
    st.session_state.gender = "Not specified"
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "user_age" not in st.session_state:
    st.session_state.user_age = 40
if "voice_text" not in st.session_state:
    st.session_state.voice_text = ""
if "profile_saved" not in st.session_state:
    st.session_state.profile_saved = False

# ══════════════════════════════════════
# GENDER-BASED COLOUR THEME
# ══════════════════════════════════════
THEMES = {
    "Male":          {"primary": "#1a4a8a", "secondary": "#2d6fba", "light": "#e8f0fb", "accent": "#0d2d5c", "gradient": "135deg, #0d2d5c, #1a4a8a, #2d6fba"},
    "Female":        {"primary": "#8a1a5c", "secondary": "#c44d8a", "light": "#fbe8f3", "accent": "#5c0d3a", "gradient": "135deg, #5c0d3a, #8a1a5c, #c44d8a"},
    "Not specified": {"primary": "#1a5c45", "secondary": "#2d8a65", "light": "#e8f5ef", "accent": "#0d3d29", "gradient": "135deg, #0d3d29, #1a5c45, #2d8a65"},
}

def get_theme():
    return THEMES.get(st.session_state.gender, THEMES["Not specified"])

theme = get_theme()

# ══════════════════════════════════════
# CSS — DYNAMIC THEME
# ══════════════════════════════════════
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&family=Poppins:wght@300;400;600;700&display=swap');

:root {{
    --primary:   {theme['primary']};
    --secondary: {theme['secondary']};
    --light:     {theme['light']};
    --accent:    {theme['accent']};
    --gradient:  {theme['gradient']};
}}

html, body, [class*="css"] {{
    font-family: 'Poppins', sans-serif;
}}

.stApp {{
    background: linear-gradient(160deg, {theme['light']} 0%, #f8f9fa 50%, {theme['light']} 100%);
}}

/* Header */
.app-header {{
    background: linear-gradient({theme['gradient']});
    border-radius: 20px;
    padding: 28px 36px;
    margin-bottom: 20px;
    color: white;
    box-shadow: 0 8px 32px {theme['primary']}44;
    display: flex;
    align-items: center;
    gap: 20px;
}}
.header-text h1 {{
    font-size: 2rem;
    font-weight: 700;
    margin: 0;
    color: white;
}}
.header-text .byline {{
    font-size: 0.78rem;
    opacity: 0.65;
    margin: 2px 0;
}}
.header-text .subtitle {{
    font-size: 0.92rem;
    opacity: 0.82;
}}
.header-text .arabic {{
    font-family: 'Tajawal', sans-serif;
    font-size: 0.88rem;
    opacity: 0.7;
    direction: rtl;
}}
.header-logo {{
    font-size: 4rem;
    line-height: 1;
}}

/* Cards */
.card {{
    background: white;
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 16px;
    box-shadow: 0 2px 16px rgba(0,0,0,0.06);
    border-top: 4px solid {theme['primary']};
}}

/* Emergency */
.emergency-header {{
    background: linear-gradient(135deg, #dc2626, #7f1d1d);
    border-radius: 16px;
    padding: 20px 28px;
    color: white;
    text-align: center;
    margin-bottom: 20px;
    box-shadow: 0 4px 20px rgba(220,38,38,0.3);
}}

/* Step boxes */
.step {{
    background: {theme['light']};
    border-left: 4px solid {theme['primary']};
    border-radius: 8px;
    padding: 11px 16px;
    margin: 7px 0;
    font-size: 0.92rem;
    line-height: 1.6;
}}
.step-red {{
    background: #fff5f5;
    border-left: 4px solid #dc2626;
    border-radius: 8px;
    padding: 11px 16px;
    margin: 7px 0;
    font-size: 0.92rem;
    line-height: 1.6;
}}

/* Arabic */
.arabic-text {{
    font-family: 'Tajawal', sans-serif;
    direction: rtl;
    text-align: right;
    font-size: 1.1rem;
    line-height: 2.1;
    background: #fffbf0;
    border-radius: 10px;
    padding: 18px 22px;
    border: 1px solid #fde68a;
}}

/* Nutrition */
.nutrition-tip {{
    background: #f0fdf4;
    border-left: 3px solid #22c55e;
    border-radius: 6px;
    padding: 9px 14px;
    margin: 5px 0;
    font-size: 0.88rem;
}}

/* Disclaimer */
.disclaimer {{
    background: #fff8e1;
    border: 1px solid #fcd34d;
    border-radius: 10px;
    padding: 12px 18px;
    font-size: 0.82rem;
    color: #78350f;
    line-height: 1.6;
}}

/* Profile card */
.profile-card {{
    background: linear-gradient({theme['gradient']});
    color: white;
    border-radius: 16px;
    padding: 24px 28px;
    text-align: center;
    box-shadow: 0 4px 20px {theme['primary']}44;
}}

/* Voice button */
.voice-area {{
    background: {theme['light']};
    border: 2px dashed {theme['secondary']};
    border-radius: 14px;
    padding: 20px;
    text-align: center;
    margin: 12px 0;
}}

/* Gender buttons */
.gender-btn {{
    border-radius: 50px;
    font-weight: 600;
    padding: 8px 24px;
}}

/* Result boxes */
.result-green {{
    background: linear-gradient(135deg, #dcfce7, #bbf7d0);
    border: 3px solid #16a34a;
    border-radius: 16px;
    padding: 28px;
    text-align: center;
}}
.result-yellow {{
    background: linear-gradient(135deg, #fef9c3, #fde68a);
    border: 3px solid #f59e0b;
    border-radius: 16px;
    padding: 28px;
    text-align: center;
}}
.result-red {{
    background: linear-gradient(135deg, #fee2e2, #fecaca);
    border: 3px solid #dc2626;
    border-radius: 16px;
    padding: 28px;
    text-align: center;
    animation: pulse 2s infinite;
}}
@keyframes pulse {{
    0%,100% {{ box-shadow: 0 0 0 0 rgba(220,38,38,0.3); }}
    50%      {{ box-shadow: 0 0 0 12px rgba(220,38,38,0); }}
}}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {{
    gap: 8px;
    background: white;
    border-radius: 12px;
    padding: 6px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}}
.stTabs [data-baseweb="tab"] {{
    border-radius: 8px;
    font-weight: 600;
    font-size: 0.88rem;
    padding: 8px 16px;
}}
.stTabs [aria-selected="true"] {{
    background: {theme['primary']} !important;
    color: white !important;
}}

/* Hide streamlit default */
#MainMenu {{ visibility: hidden; }}
footer    {{ visibility: hidden; }}
header    {{ visibility: hidden; }}

/* Sidebar */
section[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, {theme['accent']} 0%, {theme['primary']} 100%);
}}
section[data-testid="stSidebar"] * {{
    color: white !important;
}}
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stToggle label {{
    color: white !important;
}}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════
with st.sidebar:
    st.markdown(f"## 🌿 Khareef Health")
    st.caption("by Sadga Selime")
    st.markdown("---")

    # Gender selector in sidebar
    st.markdown("### Choose Gender / الجنس")
    gender_choice = st.radio(
        "Gender",
        ["Not specified", "Male", "Female"],
        index=["Not specified","Male","Female"].index(st.session_state.gender),
        horizontal=True,
        label_visibility="collapsed",
    )
    if gender_choice != st.session_state.gender:
        st.session_state.gender = gender_choice
        st.rerun()

    if st.session_state.gender == "Male":
        st.info("💙 Blue theme active")
    elif st.session_state.gender == "Female":
        st.markdown('<p style="color:#ffb3d9">💗 Rose theme active</p>', unsafe_allow_html=True)
    else:
        st.success("💚 Green theme active")

    st.markdown("---")
    khareef_mode = st.toggle("🌦️ Khareef Mode", value=False)
    show_arabic  = st.toggle("🌐 Arabic / عربي", value=True)
    use_gemini   = st.toggle("🤖 AI Advice", value=is_api_key_configured())

    st.markdown("---")
    st.markdown("### 🏥 Emergency")
    st.error("📞 Call **999** now")
    st.markdown("**Sultan Qaboos Hospital**")
    st.caption("+968 23 218 000 · Al Dahariz")

    st.markdown("---")
    st.caption(get_api_key_status())

# ══════════════════════════════════════
# HEADER
# ══════════════════════════════════════
gender_emoji = "👨" if st.session_state.gender == "Male" else "👩" if st.session_state.gender == "Female" else "🌿"

st.markdown(f"""
<div class="app-header">
    <div class="header-logo">{gender_emoji}</div>
    <div class="header-text">
        <h1>Khareef Health</h1>
        <div class="byline">by Sadga Selime</div>
        <div class="subtitle">AI Telemedicine Triage · Salalah, Dhofar, Oman</div>
        <div class="arabic">مساعد الفرز الطبي الذكي · صلالة، ظفار، عُمان</div>
    </div>
</div>
""", unsafe_allow_html=True)

if khareef_mode:
    st.warning("🌦️ Khareef Mode Active — Higher respiratory sensitivity for monsoon season")

# ══════════════════════════════════════
# MAIN TABS
# ══════════════════════════════════════
tab_profile, tab_assess, tab_emergency, tab_medicine, tab_history, tab_about = st.tabs([
    "👤 My Profile",
    "🩺 Health Check",
    "🚨 Emergency",
    "💊 Medicines",
    "📊 My History",
    "ℹ️ About",
])

# ══════════════════════════════════════
# TAB 1 — MY PROFILE
# ══════════════════════════════════════
with tab_profile:
    st.markdown("### 👤 Your Profile / ملفك الشخصي")
    st.caption("Your information is saved and used to personalise your health assessment")

    col_p1, col_p2 = st.columns([1, 1])

    with col_p1:
        p_name = st.text_input("Full Name / الاسم الكامل",
            value=st.session_state.user_name,
            placeholder="e.g. Ahmed Al-Shanfari")
        p_age = st.number_input("Age / العمر", min_value=1, max_value=120,
            value=st.session_state.user_age)
        p_gender = st.selectbox("Gender / الجنس",
            ["Not specified", "Male", "Female"],
            index=["Not specified","Male","Female"].index(st.session_state.gender))

        p_city = st.selectbox("City / المدينة",
            ["Salalah", "Muscat", "Sohar", "Nizwa", "Sur", "Other"])
        p_conditions = st.multiselect("Existing Conditions / أمراض معروفة",
            ["Diabetes", "High Blood Pressure", "Asthma", "Heart Disease",
             "Kidney Disease", "Arthritis", "None"])
        p_medications = st.text_area("Current Medications / الأدوية الحالية",
            placeholder="List your daily medications here...", height=80)

        if st.button("💾 Save Profile", type="primary", use_container_width=True):
            st.session_state.user_name   = p_name
            st.session_state.user_age    = p_age
            st.session_state.gender      = p_gender
            st.session_state.profile_saved = True
            st.success("✅ Profile saved! Your information will be used in assessments.")
            st.rerun()

    with col_p2:
        if st.session_state.user_name:
            age_val = st.session_state.user_age
            risk = "Higher Risk" if age_val >= 60 else "Standard"
            st.markdown(f"""
            <div class="profile-card">
                <div style="font-size:3rem">{gender_emoji}</div>
                <div style="font-size:1.4rem; font-weight:700; margin:8px 0">
                    {st.session_state.user_name}
                </div>
                <div style="opacity:0.85">Age: {age_val} years</div>
                <div style="opacity:0.85">Gender: {st.session_state.gender}</div>
                <div style="opacity:0.85">City: {p_city if 'p_city' in dir() else 'Salalah'}</div>
                <div style="margin-top:12px; background:rgba(255,255,255,0.2);
                    border-radius:8px; padding:8px; font-size:0.85rem">
                    Risk Level: {risk}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Fill in your profile on the left and click Save")

        st.markdown("### 🔒 Privacy")
        st.markdown("""
        - Your data is stored **only on this device**
        - Nothing is sent to external servers except the AI request
        - You can clear your history anytime in the History tab
        """)

# ══════════════════════════════════════
# TAB 2 — HEALTH CHECK
# ══════════════════════════════════════
with tab_assess:

    # Pre-fill from profile
    default_name = st.session_state.user_name
    default_age  = st.session_state.user_age

    st.markdown("### 👤 Patient Details")
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Name / الاسم", value=default_name,
            placeholder="e.g. Ahmed Al-Shanfari")
    with col2:
        age = st.number_input("Age / العمر", min_value=1, max_value=120,
            value=default_age)
        if age >= 60:
            st.caption("👴 Elderly — higher risk monitoring active")

    st.markdown("---")

    # ── VOICE INPUT ──
    st.markdown("### 🎤 Voice Input / الإدخال الصوتي")
    st.caption("Click the button and speak your symptoms in English or Arabic")

    voice_html = f"""
    <div style="background:{theme['light']}; border:2px dashed {theme['secondary']};
         border-radius:14px; padding:20px; text-align:center; margin:8px 0;">
        <button id="voiceBtn" onclick="startVoice()" style="
            background: linear-gradient({theme['gradient']});
            color: white; border: none; border-radius: 50px;
            padding: 14px 36px; font-size: 1.1rem; font-weight: 700;
            cursor: pointer; box-shadow: 0 4px 16px {theme['primary']}55;
            font-family: 'Poppins', sans-serif;">
            🎤 Tap to Speak
        </button>
        <div id="status" style="margin-top:12px; color:{theme['primary']};
             font-weight:600; font-size:0.95rem;"></div>
        <div id="transcript" style="margin-top:10px; background:white;
             border-radius:10px; padding:12px; min-height:40px;
             font-size:1rem; color:#1a3a2a; text-align:left;
             border:1px solid {theme['secondary']}55;"></div>
        <div style="margin-top:8px; font-size:0.8rem; color:#6b7280;">
            Supported: English, Arabic | Works best in Chrome browser
        </div>
    </div>

    <script>
    let recognizing = false;
    let recognition;

    function startVoice() {{
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {{
            document.getElementById('status').innerHTML =
                '❌ Voice not supported. Please use Chrome browser.';
            return;
        }}
        if (recognizing) {{
            recognition.stop();
            return;
        }}
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();
        recognition.lang = 'ar-OM';
        recognition.interimResults = true;
        recognition.maxAlternatives = 1;

        recognition.onstart = function() {{
            recognizing = true;
            document.getElementById('voiceBtn').innerHTML = '⏹️ Stop Recording';
            document.getElementById('voiceBtn').style.background = '#dc2626';
            document.getElementById('status').innerHTML = '🔴 Listening... speak now';
        }};

        recognition.onresult = function(event) {{
            let final = '';
            let interim = '';
            for (let i = event.resultIndex; i < event.results.length; i++) {{
                if (event.results[i].isFinal) {{
                    final += event.results[i][0].transcript;
                }} else {{
                    interim += event.results[i][0].transcript;
                }}
            }}
            document.getElementById('transcript').innerHTML =
                final + '<span style="color:#9ca3af">' + interim + '</span>';
        }};

        recognition.onerror = function(event) {{
            document.getElementById('status').innerHTML = '❌ Error: ' + event.error;
            recognizing = false;
        }};

        recognition.onend = function() {{
            recognizing = false;
            document.getElementById('voiceBtn').innerHTML = '🎤 Tap to Speak';
            document.getElementById('voiceBtn').style.background =
                'linear-gradient({theme["gradient"]})';
            document.getElementById('status').innerHTML =
                '✅ Done! Copy the text above into the symptoms box below.';
        }};

        recognition.start();
    }}
    </script>
    """

    components.html(voice_html, height=220)

    st.markdown("---")

    # ── VITALS TOGGLE ──
    st.markdown("### 🩺 Vital Signs / العلامات الحيوية")
    know_vitals = st.toggle(
        "I have my BP / Sugar / Temperature readings available",
        value=False,
        help="Turn ON if you have a blood pressure monitor or glucometer"
    )

    if not know_vitals:
        st.info(
            "No problem! You can still get advice based on your symptoms.\n\n"
            "For a more accurate assessment, use a BP monitor and thermometer."
        )
        bp_systolic  = 120
        bp_diastolic = 80
        blood_sugar  = 100
        temperature  = 37.0
    else:
        st.markdown("#### Blood Pressure / ضغط الدم")
        st.caption("Enter the two numbers from your blood pressure reading")

        bp_col1, bp_col2 = st.columns(2)
        with bp_col1:
            st.markdown("**Upper Number (Systolic) الانقباضي**")
            st.caption("Normal: 90–120")
            bp_systolic = st.number_input("Systolic",
                min_value=60, max_value=240, value=120,
                label_visibility="collapsed")
            if bp_systolic >= 180:   st.error("🔴 Dangerously HIGH")
            elif bp_systolic < 90:   st.error("🔴 Dangerously LOW")
            elif bp_systolic >= 140: st.warning("🟡 High — monitor")
            else:                     st.success("🟢 Normal")

        with bp_col2:
            st.markdown("**Lower Number (Diastolic) الانبساطي**")
            st.caption("Normal: 60–80")
            bp_diastolic = st.number_input("Diastolic",
                min_value=40, max_value=140, value=80,
                label_visibility="collapsed")
            if bp_diastolic >= 120:   st.error("🔴 Dangerously HIGH")
            elif bp_diastolic < 60:   st.error("🔴 Dangerously LOW")
            elif bp_diastolic >= 90:  st.warning("🟡 High — monitor")
            else:                      st.success("🟢 Normal")

        st.markdown(f"**Combined: {bp_systolic}/{bp_diastolic} mmHg**")
        st.markdown("---")

        col3, col4 = st.columns(2)
        with col3:
            st.markdown("#### Blood Sugar / سكر الدم")
            st.caption("Normal fasting: 70–99 mg/dL")
            blood_sugar = st.number_input("Blood Sugar (mg/dL)",
                min_value=30.0, max_value=700.0, value=110.0, step=1.0,
                label_visibility="collapsed")
            if blood_sugar > 300:    st.error("🔴 Critically HIGH")
            elif blood_sugar < 60:   st.error("🔴 Critically LOW")
            elif blood_sugar > 180:  st.warning("🟡 High")
            else:                     st.success("🟢 Normal")

        with col4:
            st.markdown("#### Temperature / درجة الحرارة")
            st.caption("Normal: 36.1°C – 37.2°C")
            temperature = st.number_input("Temperature (°C)",
                min_value=34.0, max_value=43.0, value=36.8,
                step=0.1, format="%.1f",
                label_visibility="collapsed")
            if temperature >= 39.5:  st.error("🔴 Very High Fever")
            elif temperature >= 37.5: st.warning("🟡 Fever")
            elif temperature < 35.5:  st.error("🔴 Too Low")
            else:                      st.success("🟢 Normal")

    st.markdown("---")

    # ── SYMPTOMS ──
    st.markdown("### 🤒 Symptoms / الأعراض")
    st.caption("Select all that apply — or use voice input above then type below")

    selected_symptoms = []
    c1, c2, c3, c4 = st.columns(4)
    if c1.checkbox("😮‍💨 Cough / سعال"):          selected_symptoms.append("cough")
    if c2.checkbox("😤 Breathless / ضيق"):        selected_symptoms.append("breathlessness")
    if c3.checkbox("💔 Chest Pain / الصدر"):      selected_symptoms.append("chest_pain")
    if c4.checkbox("😵 Dizziness / دوار"):         selected_symptoms.append("dizziness")
    if c1.checkbox("🤒 Fever / حمى"):              selected_symptoms.append("fever")
    if c2.checkbox("😴 Fatigue / إعياء"):          selected_symptoms.append("fatigue")
    if c3.checkbox("🤕 Headache / صداع"):          selected_symptoms.append("headache")
    if c4.checkbox("🤢 Nausea / غثيان"):           selected_symptoms.append("nausea")

    extra = st.text_area(
        "Other symptoms / أعراض أخرى (type or paste from voice input above):",
        placeholder="e.g. back pain, rash ... أو: ألم في الظهر",
        height=70,
        key="extra_symptoms"
    )
    if extra.strip():
        extras = [s.strip() for s in extra.replace(",", "\n").splitlines() if s.strip()]
        selected_symptoms.extend(normalize_symptoms(extras))
        selected_symptoms = list(set(selected_symptoms))

    if selected_symptoms:
        st.info(f"Selected symptoms: {', '.join(selected_symptoms)}")

    # Force emergency warning
    if "chest_pain" in selected_symptoms or "breathlessness" in selected_symptoms:
        st.error("🚨 SERIOUS SYMPTOMS — Go to Emergency tab or call 999 immediately!")

    st.markdown("---")
    st.markdown("""
    <div class="disclaimer">
        ⚠️ This app is a health guide only. It is NOT a doctor.
        Always consult a qualified medical professional.
        Emergency: <strong>999</strong>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("")

    # ── ASSESS BUTTON ──
    if st.button("🔍 Assess My Health / تقييم صحتي",
            type="primary", use_container_width=True):

        error = validate_patient_input(
            name if name else "Patient",
            int(age), int(bp_systolic), int(bp_diastolic),
            float(blood_sugar), float(temperature)
        )

        if error:
            st.error(error)
        else:
            patient = Patient(
                name=name.strip() if name else "Patient",
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

            # Save to records
            record = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "name": patient.name,
                "age": patient.age,
                "gender": st.session_state.gender,
                "bp": f"{bp_systolic}/{bp_diastolic}",
                "sugar": blood_sugar,
                "temp": temperature,
                "symptoms": ", ".join(selected_symptoms) if selected_symptoms else "None",
                "triage": result["level"],
                "vitals_known": know_vitals,
            }
            save_record(record)
            log_patient(patient, result)

            # ── SHOW RESULTS ──
            st.markdown("---")
            st.markdown(f"## Results for **{patient.name}**")

            level = result["level"]
            css_map = {"GREEN":"result-green","YELLOW":"result-yellow","RED":"result-red"}
            label_map = {
                "GREEN":  ("🟢 ALL CLEAR",              "بصحة جيدة",          "#16a34a"),
                "YELLOW": ("🟡 ATTENTION NEEDED",        "يحتاج انتباهاً",     "#d97706"),
                "RED":    ("🔴 URGENT — SEEK HELP NOW",  "عاجل — اطلب المساعدة","#dc2626"),
            }
            label_en, label_ar, color = label_map[level]

            st.markdown(f"""
            <div class="{css_map[level]}">
                <div style="font-size:1.8rem;font-weight:700;color:{color}">{label_en}</div>
                <div style="font-family:'Tajawal',sans-serif;font-size:1.2rem;
                     color:{color};opacity:0.8;direction:rtl">{label_ar}</div>
            </div>
            """, unsafe_allow_html=True)

            if know_vitals:
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("🩺 BP",   f"{bp_systolic}/{bp_diastolic}")
                m2.metric("🩸 Sugar", f"{int(blood_sugar)}")
                m3.metric("🌡️ Temp", f"{temperature:.1f}°C")
                m4.metric("👤 Age",  f"{int(age)} yrs")

            st.markdown("### 🔍 Findings")
            for r in result["reasons"]:
                st.markdown(f"- {r}")

            st.markdown("---")
            if ai_result and ai_result["success"]:
                st.markdown("### 💬 AI Medical Advice ✨")
                st.info(ai_result["advice_en"])
                if show_arabic and ai_result["advice_ar"]:
                    st.markdown("### النصيحة الطبية")
                    st.markdown(f'<div class="arabic-text">{ai_result["advice_ar"]}</div>',
                        unsafe_allow_html=True)
            else:
                st.markdown("### 💬 Medical Advice")
                st.info(result["rule_advice_en"])
                if show_arabic:
                    st.markdown("### النصيحة الطبية")
                    st.markdown(f'<div class="arabic-text">{result["rule_advice_ar"]}</div>',
                        unsafe_allow_html=True)

            if level == "RED":
                st.markdown("---")
                st.error("🚨 **Sultan Qaboos Hospital Salalah**\n\n📍 Al Dahariz · 📞 999 · +968 23 218 000")
                st.link_button("📍 Open in Google Maps",
                    "https://maps.google.com/?q=Sultan+Qaboos+Hospital+Salalah+Oman")

            if result["nutrition"]:
                st.markdown("---")
                st.markdown("### 🥗 Nutrition Tips")
                for tip in result["nutrition"]:
                    st.markdown(f'<div class="nutrition-tip">{tip}</div>',
                        unsafe_allow_html=True)

            st.markdown("---")
            st.markdown("""
            <div class="disclaimer">
                ⚠️ Educational purposes only. Not a substitute for medical advice. Emergency: <strong>999</strong>
            </div>
            """, unsafe_allow_html=True)

# ══════════════════════════════════════
# TAB 3 — EMERGENCY
# ══════════════════════════════════════
with tab_emergency:
    st.markdown("""
    <div class="emergency-header">
        <div style="font-size:2.5rem">🚨</div>
        <div style="font-size:1.5rem;font-weight:700">EMERGENCY FIRST AID GUIDE</div>
        <div style="opacity:0.85;margin-top:4px">دليل الإسعافات الأولية</div>
    </div>
    """, unsafe_allow_html=True)

    st.error("🔴 If life is in danger — **CALL 999 FIRST**, then follow steps below")

    st.markdown("### 🏥 Salalah Emergency Contacts")
    h1, h2, h3 = st.columns(3)
    with h1:
        st.error("**🚑 Emergency**\n📞 **999**\n🕐 24/7")
    with h2:
        st.info("**🏥 Sultan Qaboos Hospital**\n📞 +968 23 218 000\n📍 Al Dahariz, Salalah")
    with h3:
        st.info("**🏥 Salalah Private Hospital**\n📞 +968 23 295 999\n📍 Salalah")

    st.link_button("📍 Sultan Qaboos Hospital on Maps",
        "https://maps.google.com/?q=Sultan+Qaboos+Hospital+Salalah+Oman")

    st.markdown("---")

    # Emergency guide sections
    em_tab1, em_tab2, em_tab3, em_tab4, em_tab5 = st.tabs([
        "❤️ Heart Attack",
        "💓 CPR",
        "😮‍💨 Choking",
        "😵 Fainting",
        "🌡️ Heat Stroke",
    ])

    with em_tab1:
        st.markdown("## ❤️ Heart Attack / نوبة قلبية")
        col_e1, col_e2 = st.columns([1, 1])
        with col_e1:
            st.markdown("### Signs / العلامات")
            for sign in [
                "💔 Chest pain or pressure",
                "😮‍💨 Shortness of breath",
                "💪 Pain in left arm or jaw",
                "😰 Sweating suddenly",
                "🤢 Nausea or vomiting",
                "😵 Feeling dizzy or faint",
            ]:
                st.markdown(f'<div class="step-red">{sign}</div>', unsafe_allow_html=True)

        with col_e2:
            st.markdown("### What To Do / ماذا تفعل")
            for i, step in enumerate([
                "📞 Call 999 immediately",
                "🪑 Ask patient to sit and rest — do NOT let them walk",
                "👗 Loosen tight clothing on neck and chest",
                "💊 Give aspirin 300mg if available and not allergic",
                "🧍 Stay with patient — do NOT leave them alone",
                "🚫 Do NOT give food or water",
                "🚫 Do NOT let patient drive themselves",
            ], 1):
                st.markdown(f'<div class="step-red"><strong>Step {i}:</strong> {step}</div>',
                    unsafe_allow_html=True)

    with em_tab2:
        st.markdown("## 💓 CPR — Cardiopulmonary Resuscitation")
        st.error("Only do CPR if the person is **unconscious and not breathing**")
        col_c1, col_c2 = st.columns([1, 1])
        with col_c1:
            st.markdown("### Steps / الخطوات")
            for i, step in enumerate([
                "Tap shoulder and shout — check if responsive",
                "Call 999 immediately",
                "Lay person flat on their back on hard surface",
                "Kneel beside them",
                "Place heel of hand on CENTRE of chest",
                "Place other hand on top and interlock fingers",
                "Push DOWN hard and fast — 5–6 cm deep",
                "Do 30 compressions — rate: 100–120 per minute",
                "Tilt head back gently, lift chin up",
                "Pinch nose, seal your mouth over theirs",
                "Give 2 slow breaths — watch chest rise",
                "Repeat: 30 compressions + 2 breaths",
                "Continue until help arrives or person wakes",
            ], 1):
                st.markdown(f'<div class="step-red"><strong>{i}.</strong> {step}</div>',
                    unsafe_allow_html=True)

        with col_c2:
            st.markdown("### Remember / تذكر")
            st.warning("""
            🎵 **Rhythm tip:** Push to the beat of 'Stayin Alive' by Bee Gees
            — that's exactly 100 beats per minute!

            💪 **Press hard** — you need to compress the chest at least 5cm

            😮‍💨 **Rescue breaths** — if you're not trained, do chest compressions only

            🔄 **Switch** with someone else every 2 minutes if possible — CPR is tiring

            🚑 **Don't stop** until paramedics arrive
            """)

    with em_tab3:
        st.markdown("## 😮‍💨 Choking / الاختناق")
        col_ch1, col_ch2 = st.columns(2)
        with col_ch1:
            st.markdown("### Signs / العلامات")
            for sign in [
                "Cannot speak or cry out",
                "Hands clutching throat",
                "Weak, ineffective cough",
                "Skin turning blue or purple",
                "Cannot breathe properly",
            ]:
                st.markdown(f'<div class="step-red">{sign}</div>', unsafe_allow_html=True)

            st.markdown("### For Conscious Adult")
            for i, step in enumerate([
                "Ask: Are you choking? Can you speak?",
                "Tell them to cough HARD",
                "Lean them forward",
                "Give 5 firm back blows between shoulder blades",
                "Give 5 abdominal thrusts (Heimlich manoeuvre)",
                "Alternate back blows and abdominal thrusts",
                "Call 999 if object doesn't come out",
            ], 1):
                st.markdown(f'<div class="step"><strong>{i}.</strong> {step}</div>',
                    unsafe_allow_html=True)

        with col_ch2:
            st.markdown("### Heimlich Manoeuvre")
            st.info("""
            **How to do abdominal thrusts:**

            1. Stand BEHIND the choking person
            2. Put one foot forward for balance
            3. Make a fist with one hand
            4. Place thumb side against their abdomen
               — just above belly button, below breastbone
            5. Grab your fist with your other hand
            6. Give sharp inward AND upward thrusts
            7. Repeat until object is expelled
            """)

            st.markdown("### For Infant (under 1 year)")
            for step in [
                "Hold face-down on your forearm",
                "Give 5 back blows with heel of hand",
                "Turn face-up, give 5 chest thrusts with 2 fingers",
                "Check mouth — remove visible object only",
                "Repeat until breathing or help arrives",
                "Call 999 immediately",
            ]:
                st.markdown(f'<div class="step-red">{step}</div>', unsafe_allow_html=True)

    with em_tab4:
        st.markdown("## 😵 Fainting / الإغماء")
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            st.markdown("### If Someone Faints")
            for i, step in enumerate([
                "Lay person FLAT on the ground",
                "Raise their legs 30cm above heart level",
                "Loosen tight clothing — collar, belt",
                "Check if they are breathing normally",
                "Turn on side if they are vomiting",
                "Do NOT put anything in their mouth",
                "Do NOT give water while unconscious",
                "Call 999 if not waking within 1 minute",
                "Stay with them as they recover",
            ], 1):
                st.markdown(f'<div class="step"><strong>{i}.</strong> {step}</div>',
                    unsafe_allow_html=True)

        with col_f2:
            st.markdown("### Common Causes")
            for cause in [
                "🌡️ Standing too long in heat",
                "💧 Dehydration",
                "😟 Sudden shock or emotional stress",
                "🩸 Low blood sugar",
                "💊 Medication side effects",
                "🩺 Low blood pressure",
                "🏃 Overexertion",
            ]:
                st.markdown(f'<div class="step">{cause}</div>', unsafe_allow_html=True)

            st.markdown("### Prevention")
            st.success("""
            - Drink enough water daily
            - Sit before standing up slowly
            - Avoid standing for long periods
            - Eat regular meals — don't skip
            - Sit or lie if feeling faint
            """)

    with em_tab5:
        st.markdown("## 🌡️ Heat Stroke — Very Important in Salalah")
        st.error("Heat stroke is a MEDICAL EMERGENCY — call 999 immediately")

        col_h1, col_h2 = st.columns(2)
        with col_h1:
            st.markdown("### Signs / العلامات")
            for sign in [
                "🌡️ Body temperature above 40°C",
                "🧠 Confusion, slurred speech",
                "🚫 Stopped sweating (skin is hot and dry)",
                "🤢 Nausea or vomiting",
                "💓 Rapid heartbeat",
                "😵 Loss of consciousness",
                "🤕 Severe headache",
            ]:
                st.markdown(f'<div class="step-red">{sign}</div>', unsafe_allow_html=True)

        with col_h2:
            st.markdown("### What To Do")
            for i, step in enumerate([
                "Call 999 IMMEDIATELY",
                "Move person to shade or cool room",
                "Remove excess clothing",
                "Cool them with wet cloths on neck, armpits, groin",
                "Fan them continuously",
                "Give cool (not cold) water if conscious and can swallow",
                "Apply ice packs to neck, armpits, groin",
                "Do NOT give aspirin or paracetamol",
                "Monitor until help arrives",
            ], 1):
                st.markdown(f'<div class="step"><strong>{i}.</strong> {step}</div>',
                    unsafe_allow_html=True)

# ══════════════════════════════════════
# TAB 4 — MEDICINE GUIDE
# ══════════════════════════════════════
with tab_medicine:
    st.markdown("### 💊 Medicine Information Guide")
    st.markdown("""
    <div class="disclaimer">
        ⚠️ General information only. Always follow your doctor's prescription.
        Never change your dose without consulting a doctor or pharmacist.
    </div>
    """, unsafe_allow_html=True)
    st.markdown("")

    medicines = {
        "Paracetamol (Panadol)": {
            "emoji": "💊", "for": "Fever, headache, mild to moderate pain",
            "dose": "500mg–1000mg every 4–6 hours. Maximum 4g (4000mg) per day.",
            "warning": "Do not exceed 4g per day. Avoid with alcohol.",
            "avoid": "Liver disease, heavy alcohol use, taking other paracetamol products",
            "tip": "Most common and safest painkiller for elderly patients",
        },
        "Ibuprofen (Brufen)": {
            "emoji": "💊", "for": "Pain, inflammation, fever, joint pain",
            "dose": "200mg–400mg every 6–8 hours. Always take WITH food.",
            "warning": "Must take with food. Can cause stomach bleeding.",
            "avoid": "Kidney problems, stomach ulcers, pregnancy (3rd trimester), heart failure",
            "tip": "Always eat something before taking this medicine",
        },
        "Metformin": {
            "emoji": "🔵", "for": "Type 2 diabetes — lowers blood sugar levels",
            "dose": "As prescribed. Usually 500mg–1000mg twice daily with meals.",
            "warning": "Take with food to reduce nausea. Stay well hydrated.",
            "avoid": "Kidney problems. Stop before surgery, CT scans, or MRI with contrast.",
            "tip": "Do not stop without doctor's advice even if sugar normalises",
        },
        "Amlodipine": {
            "emoji": "❤️", "for": "High blood pressure, angina (chest pain)",
            "dose": "5mg–10mg once daily. Take at the same time each day.",
            "warning": "May cause ankle swelling. Do not stop suddenly.",
            "avoid": "Severe low blood pressure, certain heart conditions",
            "tip": "Take in the morning. Blood pressure may take weeks to normalise",
        },
        "Omeprazole": {
            "emoji": "🟡", "for": "Stomach acid, heartburn, ulcers, acid reflux",
            "dose": "20mg once daily, 30 minutes BEFORE eating.",
            "warning": "Long-term use may reduce magnesium and B12 levels.",
            "avoid": "Do not use long-term without doctor review",
            "tip": "Take 30 minutes before breakfast for best effect",
        },
        "Salbutamol (Ventolin)": {
            "emoji": "💨", "for": "Asthma, wheezing, breathlessness, COPD",
            "dose": "1–2 puffs when needed. Maximum 4 times per day.",
            "warning": "If using more than 3 times per week — see a doctor urgently.",
            "avoid": "Heart rhythm problems. Discuss with doctor if heart condition exists.",
            "tip": "Keep with you always during Khareef season",
        },
        "Atorvastatin (Lipitor)": {
            "emoji": "🟠", "for": "High cholesterol, heart disease prevention",
            "dose": "10mg–80mg once daily. Usually taken at night.",
            "warning": "Report muscle pain or weakness to doctor immediately.",
            "avoid": "Liver disease, pregnancy, grapefruit juice (reduces effectiveness)",
            "tip": "Take at night — cholesterol production is highest during sleep",
        },
        "Aspirin (low dose)": {
            "emoji": "🔴", "for": "Blood thinner — prevents heart attack and stroke",
            "dose": "75mg–100mg once daily with food.",
            "warning": "Can cause stomach bleeding. Do not use with ibuprofen.",
            "avoid": "Children under 16, stomach ulcers, bleeding disorders",
            "tip": "Often prescribed for elderly with heart risk — do not stop without doctor advice",
        },
    }

    selected_med = st.selectbox("Select a medicine:",
        list(medicines.keys()), format_func=lambda x: f"{medicines[x]['emoji']} {x}")

    if selected_med:
        med = medicines[selected_med]
        st.markdown(f"### {med['emoji']} {selected_med}")
        st.info(f"💡 **Tip:** {med['tip']}")

        m1, m2 = st.columns(2)
        with m1:
            st.success(f"**✅ Used for:**\n{med['for']}")
            st.info(f"**💊 Usual Dose:**\n{med['dose']}")
        with m2:
            st.warning(f"**⚠️ Warning:**\n{med['warning']}")
            st.error(f"**🚫 Avoid if:**\n{med['avoid']}")

    st.markdown("---")
    st.markdown("""
    <div class="disclaimer">
        ⚠️ This medicine information is for general knowledge only.
        It does not replace a doctor's prescription or pharmacist's advice.
        Always consult a qualified healthcare professional before taking any medication.
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════
# TAB 5 — MY HISTORY
# ══════════════════════════════════════
with tab_history:
    st.markdown("### 📊 Your Assessment History")
    st.caption("All your health checks are stored here")

    records = load_records()

    if records:
        df = pd.DataFrame(records)
        df = df.sort_values("timestamp", ascending=False)

        # Summary stats
        total = len(df)
        greens  = len(df[df["triage"] == "GREEN"])
        yellows = len(df[df["triage"] == "YELLOW"])
        reds    = len(df[df["triage"] == "RED"])

        s1, s2, s3, s4 = st.columns(4)
        s1.metric("Total Checks", total)
        s2.metric("🟢 Green",  greens)
        s3.metric("🟡 Yellow", yellows)
        s4.metric("🔴 Red",    reds)

        st.markdown("---")
        st.markdown("### Full History")
        st.dataframe(df, use_container_width=True, height=400)

        # Download button
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download History as CSV",
            data=csv,
            file_name=f"khareef_health_history.csv",
            mime="text/csv",
        )

        st.markdown("---")
        if st.button("🗑️ Clear All History", type="secondary"):
            if os.path.exists(DATA_FILE):
                os.remove(DATA_FILE)
            st.success("History cleared!")
            st.rerun()
    else:
        st.info("No assessments yet. Complete a Health Check to see your history here.")

# ══════════════════════════════════════
# TAB 6 — ABOUT
# ══════════════════════════════════════
with tab_about:
    st.markdown("### 🌿 About Khareef Health")

    col_a1, col_a2 = st.columns(2)
    with col_a1:
        st.markdown(f"""
        <div class="profile-card">
            <div style="font-size:3rem">👨‍💻</div>
            <div style="font-size:1.3rem;font-weight:700;margin:8px 0">Sadga Selime</div>
            <div style="opacity:0.85">Developer & Designer</div>
            <div style="opacity:0.85">Salalah, Dhofar, Oman 🇴🇲</div>
            <div style="margin-top:10px;font-size:0.85rem;opacity:0.75">
                Built with Python · Streamlit · Google Gemini AI
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_a2:
        st.markdown("### What is Khareef Health?")
        st.markdown("""
        **Khareef Health** is a free AI-powered medical triage assistant
        built specifically for the community of **Salalah, Dhofar, Oman**.

        It helps people understand their health readings, identify warning
        signs, and decide whether they need urgent care — in both
        **English and Arabic**.

        The name comes from **Khareef** — Salalah's unique monsoon season
        (June–September) when health risks increase significantly.
        """)

    st.markdown("---")
    st.markdown("### 🏥 Emergency Contacts — Salalah")
    ec1, ec2, ec3 = st.columns(3)
    with ec1: st.error("**Emergency**\n📞 999")
    with ec2: st.info("**Sultan Qaboos Hospital**\n📞 +968 23 218 000")
    with ec3: st.info("**Salalah Private**\n📞 +968 23 295 999")

    st.markdown("---")
    st.markdown("### 📱 Features")
    feats = [
        ("🎤", "Voice Input",       "Speak your symptoms in English or Arabic"),
        ("🤖", "Gemini AI",         "Personalised advice powered by Google AI"),
        ("🌦️", "Khareef Mode",      "Extra sensitivity during monsoon season"),
        ("🎨", "Gender Themes",     "Personalised colour theme based on gender"),
        ("🚨", "Emergency Guide",   "CPR, Heart Attack, Choking, Fainting steps"),
        ("💊", "Medicine Guide",    "Common medicines explained simply"),
        ("📊", "History Tracking",  "All your checks saved and downloadable"),
        ("🌐", "Bilingual",         "Full English and Arabic support"),
    ]
    f1, f2 = st.columns(2)
    for i, (emoji, name, desc) in enumerate(feats):
        col = f1 if i % 2 == 0 else f2
        col.markdown(f'<div class="step"><strong>{emoji} {name}</strong><br>{desc}</div>',
            unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div class="disclaimer">
        ⚠️ <strong>Medical Disclaimer:</strong>
        This application is for educational and informational purposes only.
        It does NOT replace a qualified medical professional, licensed doctor, or pharmacist.
        Always consult a healthcare provider for diagnosis and treatment.
        In any medical emergency, call <strong>999</strong> immediately.
        The developer is not liable for any medical decisions made based on this app.
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════
# FOOTER
# ══════════════════════════════════════
st.markdown("---")
st.caption(f"🌿 Khareef Health · by Sadga Selime · Salalah, Oman · Powered by Google Gemini AI · Educational use only · v3.0")
