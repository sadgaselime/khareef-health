"""
main.py – Khareef Health v3.2 — No Sidebar Version
All controls inside the app. Clean and simple.
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

st.set_page_config(
    page_title="Khareef Health",
    page_icon=":herb:",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ══════════════════════════════════════
# DATA STORAGE
# ══════════════════════════════════════
RECORDS_FILE  = "user_records.json"
PROFILES_FILE = "user_profiles.json"

def load_json(filename):
    if os.path.exists(filename):
        try:
            with open(filename, "r") as f:
                return json.load(f)
        except:
            return []
    return []

def save_json(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def save_record(record):
    records = load_json(RECORDS_FILE)
    records.append(record)
    save_json(RECORDS_FILE, records)

def save_profile(profile):
    profiles = load_json(PROFILES_FILE)
    found = False
    for i, p in enumerate(profiles):
        if p.get("name","").lower() == profile["name"].lower():
            profiles[i] = profile
            found = True
            break
    if not found:
        profiles.append(profile)
    save_json(PROFILES_FILE, profiles)

# ══════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════
defaults = {
    "gender":          "Not specified",
    "user_name":       "",
    "user_age":        40,
    "user_city":       "Salalah",
    "user_conditions": [],
    "user_medications":"",
    "user_phone":      "",
    "user_blood_type": "Unknown",
    "khareef_mode":    False,
    "show_arabic":     True,
    "use_gemini":      is_api_key_configured(),
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ══════════════════════════════════════
# THEMES
# ══════════════════════════════════════
THEMES = {
    "Male":          {"p":"#1a4a8a","s":"#2d6fba","l":"#dbeafe","a":"#0d2d5c","g":"135deg,#0d2d5c,#1a4a8a,#2d6fba"},
    "Female":        {"p":"#9d174d","s":"#db2777","l":"#fce7f3","a":"#500724","g":"135deg,#500724,#9d174d,#db2777"},
    "Not specified": {"p":"#1a5c45","s":"#2d8a65","l":"#d1fae5","a":"#0d3d29","g":"135deg,#0d3d29,#1a5c45,#2d8a65"},
}
T = THEMES.get(st.session_state.gender, THEMES["Not specified"])

# ══════════════════════════════════════
# CSS
# ══════════════════════════════════════
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&family=Poppins:wght@400;600;700&display=swap');
html,body,[class*="css"]{{font-family:'Poppins',sans-serif;}}
.stApp{{background:linear-gradient(150deg,{T['l']} 0%,#f9fafb 60%,{T['l']} 100%);}}

/* Hide sidebar completely */
section[data-testid="stSidebar"]{{display:none;}}
.st-emotion-cache-1cypcdb{{display:none;}}

/* Header */
.app-header{{
    background:linear-gradient({T['g']});
    border-radius:20px;padding:28px 36px;margin-bottom:16px;
    color:white;box-shadow:0 8px 32px {T['p']}55;
}}
.app-header h1{{font-size:2rem;font-weight:700;margin:0;color:white;}}
.app-header .byline{{font-size:0.75rem;opacity:0.65;margin-top:2px;}}
.app-header .sub{{font-size:0.92rem;opacity:0.85;margin-top:4px;}}
.app-header .ar{{font-family:'Tajawal',sans-serif;font-size:0.88rem;opacity:0.7;direction:rtl;}}

/* Settings bar */
.settings-bar{{
    background:white;border-radius:14px;padding:16px 24px;
    margin-bottom:16px;box-shadow:0 2px 12px rgba(0,0,0,0.06);
    display:flex;align-items:center;gap:12px;flex-wrap:wrap;
}}

/* Cards */
.card{{background:white;border-radius:14px;padding:22px;margin-bottom:14px;
    box-shadow:0 2px 12px rgba(0,0,0,0.06);border-top:4px solid {T['p']};}}

/* Profile card */
.profile-card{{
    background:linear-gradient({T['g']});color:white;
    border-radius:16px;padding:24px;text-align:center;
    box-shadow:0 4px 20px {T['p']}44;
}}

/* Steps */
.step{{background:{T['l']};border-left:4px solid {T['p']};
    border-radius:8px;padding:10px 14px;margin:6px 0;font-size:0.9rem;}}
.step-red{{background:#fff1f2;border-left:4px solid #dc2626;
    border-radius:8px;padding:10px 14px;margin:6px 0;font-size:0.9rem;}}

/* Arabic */
.arabic-text{{
    font-family:'Tajawal',sans-serif;direction:rtl;text-align:right;
    font-size:1.1rem;line-height:2.1;background:#fffbf0;
    border-radius:10px;padding:16px 20px;border:1px solid #fde68a;
}}

/* Nutrition */
.nutrition-tip{{background:#f0fdf4;border-left:3px solid #22c55e;
    border-radius:6px;padding:9px 14px;margin:5px 0;font-size:0.88rem;}}

/* Disclaimer */
.disclaimer{{background:#fff8e1;border:1px solid #fcd34d;
    border-radius:10px;padding:12px 18px;font-size:0.82rem;color:#78350f;}}

/* Results */
.result-green{{background:linear-gradient(135deg,#dcfce7,#bbf7d0);
    border:3px solid #16a34a;border-radius:16px;padding:24px;text-align:center;}}
.result-yellow{{background:linear-gradient(135deg,#fef9c3,#fde68a);
    border:3px solid #f59e0b;border-radius:16px;padding:24px;text-align:center;}}
.result-red{{background:linear-gradient(135deg,#fee2e2,#fecaca);
    border:3px solid #dc2626;border-radius:16px;padding:24px;text-align:center;
    animation:pulse 2s infinite;}}
@keyframes pulse{{
    0%,100%{{box-shadow:0 0 0 0 rgba(220,38,38,0.3);}}
    50%{{box-shadow:0 0 0 14px rgba(220,38,38,0);}}
}}

/* Tabs */
.stTabs [data-baseweb="tab-list"]{{
    gap:6px;background:white;border-radius:14px;
    padding:6px;box-shadow:0 2px 14px rgba(0,0,0,0.07);
}}
.stTabs [data-baseweb="tab"]{{
    border-radius:10px;font-weight:600;font-size:0.88rem;padding:8px 16px;
}}
.stTabs [aria-selected="true"]{{
    background:{T['p']} !important;color:white !important;
}}

#MainMenu{{visibility:hidden;}}
footer{{visibility:hidden;}}
header{{visibility:hidden;}}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════
# HEADER
# ══════════════════════════════════════
g_emoji = "👨" if st.session_state.gender=="Male" else "👩" if st.session_state.gender=="Female" else "🌿"

st.markdown(f"""
<div class="app-header">
  <div style="display:flex;align-items:center;gap:20px;">
    <div style="font-size:3.5rem;line-height:1">{g_emoji}</div>
    <div>
      <h1>Khareef Health</h1>
      <div class="byline">by Sadga Selime</div>
      <div class="sub">AI Telemedicine Triage · Salalah, Dhofar, Oman</div>
      <div class="ar">مساعد الفرز الطبي الذكي · صلالة، ظفار، عُمان</div>
    </div>
    <div style="margin-left:auto;text-align:right;">
      <div style="font-size:0.85rem;opacity:0.8">📞 Emergency</div>
      <div style="font-size:1.8rem;font-weight:700">999</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════
# SETTINGS BAR — replaces sidebar
# ══════════════════════════════════════
st.markdown("#### ⚙️ Settings")
s1, s2, s3, s4, s5 = st.columns([1.2, 1, 1, 1, 1.5])

st.markdown("#### ⚙️ Settings")
s1, s2, s3, s4, s5 = st.columns([1.2, 1, 1, 1, 1.5])

with s1:
    gender = st.selectbox("🎨 Gender Theme / اختر الثيم", ["Not specified","Male","Female"],
        index=["Not specified","Male","Female"].index(st.session_state.gender),
        key="main_gender")

with s2:
    khareef_mode = st.toggle("🌦️ Khareef Mode", value=st.session_state.khareef_mode, key="khareef_toggle")
    st.session_state.khareef_mode = khareef_mode

with s3:
    show_arabic = st.toggle("🌐 Arabic", value=st.session_state.show_arabic, key="arabic_toggle")
    st.session_state.show_arabic = show_arabic

with s4:
    use_gemini = st.toggle("🤖 AI Advice", value=st.session_state.use_gemini, key="gemini_toggle")
    st.session_state.use_gemini = use_gemini

with s5:
    st.markdown(f"""
    <div style="background:{'#fef3c7' if khareef_mode else T['l']};
         border-radius:10px;padding:8px 14px;font-size:0.82rem;
         border:1px solid {'#f59e0b' if khareef_mode else T['s']}55;">
        {'🌦️ <b>Khareef Mode ON</b> — Respiratory sensitivity increased' if khareef_mode else
         '💚 Normal mode — Toggle Khareef during Jun–Sep'}
    </div>
    """, unsafe_allow_html=True)

if khareef_mode:
    st.warning("🌦️ Khareef Mode Active — Higher respiratory sensitivity for monsoon season")

st.markdown("---")

# ══════════════════════════════════════
# MAIN TABS
# ══════════════════════════════════════
tab_profile, tab_assess, tab_emergency, tab_medicine, tab_history, tab_about = st.tabs([
    "👤 My Profile",
    "🩺 Health Check",
    "🚨 Emergency",
    "💊 Medicines",
    "📊 History",
    "ℹ️ About",
])

# ══════════════════════════════════════
# TAB 1 — MY PROFILE
# ══════════════════════════════════════
with tab_profile:
    st.markdown("### 👤 Your Profile / ملفك الشخصي")
    st.caption("Save your info once — used automatically in every health check")

    col_p1, col_p2 = st.columns(2)

    with col_p1:
        st.markdown("#### Personal Information")
        p_name  = st.text_input("Full Name / الاسم",
            value=st.session_state.user_name, placeholder="e.g. Ahmed Al-Shanfari", key="p_name")
        p_age   = st.number_input("Age / العمر", min_value=1, max_value=120,
            value=st.session_state.user_age, key="p_age")
        p_gender= st.selectbox("Gender / الجنس", ["Not specified","Male","Female"],
            index=["Not specified","Male","Female"].index(st.session_state.gender), key="p_gender_sel")
        p_phone = st.text_input("Phone / الهاتف",
            value=st.session_state.user_phone, placeholder="+968 9X XXX XXXX", key="p_phone")
        p_city  = st.selectbox("City / المدينة",
            ["Salalah","Taqah","Mirbat","Rakhyut","Muscat","Sohar","Other"],
            key="p_city_sel")

        st.markdown("#### Medical Information")
        p_blood = st.selectbox("Blood Type / فصيلة الدم",
            ["Unknown","A+","A-","B+","B-","O+","O-","AB+","AB-"], key="p_blood_sel")
        p_conditions = st.multiselect("Existing Conditions / أمراض",
            ["Diabetes","High Blood Pressure","Asthma","Heart Disease",
             "Kidney Disease","Arthritis","Thyroid","None"],
            default=st.session_state.user_conditions, key="p_conds")
        p_meds  = st.text_area("Daily Medications / أدوية يومية",
            value=st.session_state.user_medications,
            placeholder="List daily medications...", height=70, key="p_meds")
        p_allergy = st.text_input("Allergies / الحساسية",
            placeholder="e.g. Penicillin, Aspirin", key="p_allergy")
        p_emergency = st.text_input("Emergency Contact / جهة طوارئ",
            placeholder="Name + Phone number", key="p_emerg")

        if st.button("💾 Save Profile", type="primary",
                use_container_width=True, key="save_btn"):
            st.session_state.user_name        = p_name
            st.session_state.user_age         = int(p_age)
            st.session_state.gender           = p_gender
            st.session_state.user_phone       = p_phone
            st.session_state.user_city        = p_city
            st.session_state.user_blood_type  = p_blood
            st.session_state.user_conditions  = p_conditions
            st.session_state.user_medications = p_meds

            profile = {
                "saved_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "name": p_name, "age": int(p_age), "gender": p_gender,
                "phone": p_phone, "city": p_city, "blood_type": p_blood,
                "conditions": p_conditions, "medications": p_meds,
                "allergies": p_allergy, "emergency_contact": p_emergency,
            }
            save_profile(profile)
            st.success("✅ Profile saved!")
            st.rerun()

    with col_p2:
        st.markdown("#### Your Profile Card")
        if st.session_state.user_name:
            risk = "Higher Risk ⚠️" if st.session_state.user_age >= 60 else "Standard ✅"
            conds = ", ".join(st.session_state.user_conditions) or "None"
            st.markdown(f"""
            <div class="profile-card">
                <div style="font-size:3rem">{g_emoji}</div>
                <div style="font-size:1.4rem;font-weight:700;margin:10px 0">
                    {st.session_state.user_name}</div>
                <div style="opacity:0.9">🎂 Age: {st.session_state.user_age}</div>
                <div style="opacity:0.9">⚧ Gender: {st.session_state.gender}</div>
                <div style="opacity:0.9">📍 {st.session_state.user_city}</div>
                <div style="opacity:0.9">🩸 {st.session_state.user_blood_type}</div>
                <div style="margin-top:10px;background:rgba(255,255,255,0.2);
                    border-radius:8px;padding:8px;font-size:0.85rem">
                    Risk: {risk}
                </div>
                <div style="margin-top:6px;background:rgba(255,255,255,0.15);
                    border-radius:8px;padding:8px;font-size:0.8rem">
                    Conditions: {conds}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Fill your profile on the left → click Save")

        st.markdown("#### Saved Profiles")
        profiles = load_json(PROFILES_FILE)
        if profiles:
            st.dataframe(pd.DataFrame(profiles), use_container_width=True, height=250)
            st.download_button("📥 Download Profiles",
                pd.DataFrame(profiles).to_csv(index=False),
                "profiles.csv", "text/csv", key="dl_prof")
        else:
            st.caption("No profiles saved yet")

# ══════════════════════════════════════
# TAB 2 — HEALTH CHECK
# ══════════════════════════════════════
with tab_assess:

    st.markdown("### 👤 Patient Details")
    a1, a2 = st.columns(2)
    with a1:
        name = st.text_input("Name / الاسم",
            value=st.session_state.user_name,
            placeholder="e.g. Ahmed Al-Shanfari", key="assess_name")
    with a2:
        age = st.number_input("Age / العمر", min_value=1, max_value=120,
            value=st.session_state.user_age, key="assess_age")
        if age >= 60:
            st.caption("👴 Elderly — higher risk monitoring")

    st.markdown("---")

    # ── VOICE INPUT ──
    st.markdown("### 🎤 Voice Input / الإدخال الصوتي")
    st.caption("Click mic → speak symptoms → copy text to box below")

    components.html(f"""
    <div style="background:{T['l']};border:2px dashed {T['s']};
         border-radius:14px;padding:18px;text-align:center;">
        <button id="vBtn" onclick="go()" style="
            background:linear-gradient({T['g']});color:white;border:none;
            border-radius:50px;padding:12px 32px;font-size:1rem;
            font-weight:700;cursor:pointer;font-family:'Poppins',sans-serif;">
            🎤 Tap to Speak / انقر للتحدث
        </button>
        <div id="status" style="margin-top:10px;color:{T['p']};font-weight:600;font-size:0.88rem;"></div>
        <div id="out" style="margin-top:8px;background:white;border-radius:8px;
             padding:10px;min-height:40px;font-size:0.95rem;text-align:left;
             border:1px solid {T['s']}44;color:#111;"></div>
        <div style="margin-top:6px;font-size:0.75rem;color:#6b7280;">
            Works in Chrome · Supports English & Arabic
        </div>
    </div>
    <script>
    let going=false,rec;
    function go(){{
        if(!('webkitSpeechRecognition' in window)&&!('SpeechRecognition' in window)){{
            document.getElementById('status').textContent='❌ Please use Chrome';return;}}
        if(going){{rec.stop();return;}}
        const SR=window.SpeechRecognition||window.webkitSpeechRecognition;
        rec=new SR();rec.lang='ar-OM';rec.interimResults=true;
        rec.onstart=()=>{{going=true;
            document.getElementById('vBtn').textContent='⏹️ Stop';
            document.getElementById('vBtn').style.background='#dc2626';
            document.getElementById('status').textContent='🔴 Listening...';
        }};
        rec.onresult=(e)=>{{
            let f='',t='';
            for(let i=e.resultIndex;i<e.results.length;i++){{
                if(e.results[i].isFinal)f+=e.results[i][0].transcript;
                else t+=e.results[i][0].transcript;}}
            document.getElementById('out').innerHTML=f+'<span style="color:#9ca3af">'+t+'</span>';
        }};
        rec.onerror=(e)=>{{document.getElementById('status').textContent='❌ '+e.error;going=false;}};
        rec.onend=()=>{{going=false;
            document.getElementById('vBtn').textContent='🎤 Tap to Speak / انقر للتحدث';
            document.getElementById('vBtn').style.background='linear-gradient({T["g"]})';
            document.getElementById('status').textContent='✅ Done! Copy text above to box below.';
        }};
        rec.start();
    }}
    </script>
    """, height=200)

    st.markdown("---")

    # ── VITALS ──
    st.markdown("### 🩺 Vital Signs / العلامات الحيوية")
    know_vitals = st.toggle("I have my BP / Sugar / Temperature readings",
        value=False, key="know_vitals")

    if not know_vitals:
        st.info("No readings? No problem — get symptom-based advice below.")
        bp_systolic=120; bp_diastolic=80; blood_sugar=100; temperature=37.0
    else:
        st.markdown("#### Blood Pressure / ضغط الدم")
        bpc1, bpc2 = st.columns(2)
        with bpc1:
            st.markdown("**Upper Number (Systolic)**")
            st.caption("Normal: 90–120")
            bp_systolic = st.number_input("Systolic", min_value=60,
                max_value=240, value=120, key="bp_sys", label_visibility="collapsed")
            if bp_systolic>=180:   st.error("🔴 Crisis — very HIGH")
            elif bp_systolic<90:   st.error("🔴 Very LOW")
            elif bp_systolic>=140: st.warning("🟡 High")
            else:                   st.success("🟢 Normal")
        with bpc2:
            st.markdown("**Lower Number (Diastolic)**")
            st.caption("Normal: 60–80")
            bp_diastolic = st.number_input("Diastolic", min_value=40,
                max_value=140, value=80, key="bp_dia", label_visibility="collapsed")
            if bp_diastolic>=120:  st.error("🔴 Crisis — very HIGH")
            elif bp_diastolic<60:  st.error("🔴 Very LOW")
            elif bp_diastolic>=90: st.warning("🟡 High")
            else:                   st.success("🟢 Normal")
        st.markdown(f"**Combined reading: {bp_systolic}/{bp_diastolic} mmHg**")
        st.markdown("---")

        vc1, vc2 = st.columns(2)
        with vc1:
            st.markdown("#### Blood Sugar / سكر الدم")
            st.caption("Normal fasting: 70–99 mg/dL")
            blood_sugar = st.number_input("mg/dL", min_value=30.0,
                max_value=700.0, value=110.0, step=1.0, key="sugar",
                label_visibility="collapsed")
            if blood_sugar>300:   st.error("🔴 Critically HIGH")
            elif blood_sugar<60:  st.error("🔴 Critically LOW")
            elif blood_sugar>180: st.warning("🟡 High")
            else:                  st.success("🟢 Normal")
        with vc2:
            st.markdown("#### Temperature / الحرارة")
            st.caption("Normal: 36.1°C – 37.2°C")
            temperature = st.number_input("Celsius", min_value=34.0,
                max_value=43.0, value=36.8, step=0.1, format="%.1f",
                key="temp", label_visibility="collapsed")
            if temperature>=39.5:   st.error("🔴 Very High Fever")
            elif temperature>=37.5: st.warning("🟡 Fever")
            elif temperature<35.5:  st.error("🔴 Too Low")
            else:                    st.success("🟢 Normal")

    st.markdown("---")

    # ── SYMPTOMS ──
    st.markdown("### 🤒 Symptoms / الأعراض")
    st.caption("Select all that apply")

    selected_symptoms = []
    sc1,sc2,sc3,sc4 = st.columns(4)
    if sc1.checkbox("Cough / سعال",      key="s1"): selected_symptoms.append("cough")
    if sc2.checkbox("Breathless / ضيق",  key="s2"): selected_symptoms.append("breathlessness")
    if sc3.checkbox("Chest Pain / صدر",  key="s3"): selected_symptoms.append("chest_pain")
    if sc4.checkbox("Dizziness / دوار",  key="s4"): selected_symptoms.append("dizziness")
    if sc1.checkbox("Fever / حمى",       key="s5"): selected_symptoms.append("fever")
    if sc2.checkbox("Fatigue / إعياء",   key="s6"): selected_symptoms.append("fatigue")
    if sc3.checkbox("Headache / صداع",   key="s7"): selected_symptoms.append("headache")
    if sc4.checkbox("Nausea / غثيان",    key="s8"): selected_symptoms.append("nausea")

    extra = st.text_area("Other symptoms / أعراض أخرى (or paste voice text here):",
        placeholder="e.g. back pain... أو ألم في الظهر", height=65, key="extra")
    if extra.strip():
        extras = [s.strip() for s in extra.replace(",","\n").splitlines() if s.strip()]
        selected_symptoms.extend(normalize_symptoms(extras))
        selected_symptoms = list(set(selected_symptoms))

    if selected_symptoms:
        st.info(f"Selected: {', '.join(selected_symptoms)}")
    if "chest_pain" in selected_symptoms or "breathlessness" in selected_symptoms:
        st.error("🚨 SERIOUS SYMPTOMS — Go to Emergency tab or call 999 now!")

    st.markdown("""<div class="disclaimer">
        ⚠️ Health guide only. NOT a doctor. Emergency: <strong>999</strong>
    </div>""", unsafe_allow_html=True)
    st.markdown("")

    if st.button("🔍 Assess My Health / تقييم صحتي",
            type="primary", use_container_width=True, key="assess_btn"):

        err = validate_patient_input(
            name if name else "Patient", int(age),
            int(bp_systolic), int(bp_diastolic),
            float(blood_sugar), float(temperature))
        if err:
            st.error(err)
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

            record = {
                "timestamp":   datetime.now().strftime("%Y-%m-%d %H:%M"),
                "name":        patient.name,
                "age":         patient.age,
                "gender":      st.session_state.gender,
                "city":        st.session_state.user_city,
                "phone":       st.session_state.user_phone,
                "blood_type":  st.session_state.user_blood_type,
                "conditions":  ", ".join(st.session_state.user_conditions) or "None",
                "medications": st.session_state.user_medications,
                "bp":          f"{bp_systolic}/{bp_diastolic}" if know_vitals else "Not measured",
                "blood_sugar": blood_sugar if know_vitals else "Not measured",
                "temperature": temperature if know_vitals else "Not measured",
                "symptoms":    ", ".join(selected_symptoms) or "None",
                "vitals_known":know_vitals,
                "khareef_mode":khareef_mode,
                "triage_level":result["level"],
                "findings":    " | ".join(result["reasons"])[:300],
                "ai_used":     bool(ai_result and ai_result.get("success")),
            }
            save_record(record)
            log_patient(patient, result)

            st.markdown("---")
            st.markdown(f"## Results for **{patient.name}**")

            level = result["level"]
            css_map = {"GREEN":"result-green","YELLOW":"result-yellow","RED":"result-red"}
            lmap = {
                "GREEN":  ("🟢 ALL CLEAR",              "بصحة جيدة",          "#16a34a"),
                "YELLOW": ("🟡 ATTENTION NEEDED",        "يحتاج انتباهاً",     "#d97706"),
                "RED":    ("🔴 URGENT — SEEK HELP NOW",  "عاجل — اطلب المساعدة","#dc2626"),
            }
            le, la, col = lmap[level]
            st.markdown(f"""
            <div class="{css_map[level]}">
                <div style="font-size:1.8rem;font-weight:700;color:{col}">{le}</div>
                <div style="font-family:'Tajawal',sans-serif;font-size:1.1rem;
                     color:{col};opacity:0.8;direction:rtl">{la}</div>
            </div>""", unsafe_allow_html=True)

            if know_vitals:
                m1,m2,m3,m4 = st.columns(4)
                m1.metric("🩺 BP",   f"{bp_systolic}/{bp_diastolic}")
                m2.metric("🩸 Sugar",f"{int(blood_sugar)} mg/dL")
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
                st.error("🚨 **Sultan Qaboos Hospital Salalah**\n\n"
                         "📍 Al Dahariz · 📞 999 · +968 23 218 000")
                st.link_button("📍 Open in Google Maps",
                    "https://maps.google.com/?q=Sultan+Qaboos+Hospital+Salalah+Oman")

            if result["nutrition"]:
                st.markdown("---")
                st.markdown("### 🥗 Nutrition Tips")
                for tip in result["nutrition"]:
                    st.markdown(f'<div class="nutrition-tip">{tip}</div>',
                        unsafe_allow_html=True)

            st.markdown("---")
            st.markdown("""<div class="disclaimer">
                ⚠️ Educational use only. Not medical advice. Emergency: <strong>999</strong>
            </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════
# TAB 3 — EMERGENCY
# ══════════════════════════════════════
with tab_emergency:
    st.markdown("""
    <div style="background:linear-gradient(135deg,#dc2626,#7f1d1d);border-radius:16px;
         padding:20px 28px;color:white;text-align:center;margin-bottom:20px;
         box-shadow:0 4px 20px rgba(220,38,38,0.3)">
        <div style="font-size:2.5rem">🚨</div>
        <div style="font-size:1.5rem;font-weight:700">EMERGENCY FIRST AID GUIDE</div>
        <div style="opacity:0.85;margin-top:4px">دليل الإسعافات الأولية</div>
    </div>""", unsafe_allow_html=True)

    st.error("🔴 Life in danger? **CALL 999 FIRST** then follow steps below")

    h1,h2,h3 = st.columns(3)
    with h1: st.error("**🚑 Emergency**\n📞 **999**\n🕐 24/7")
    with h2: st.info("**🏥 Sultan Qaboos**\n📞 +968 23 218 000\n📍 Al Dahariz, Salalah")
    with h3: st.info("**🏥 Salalah Private**\n📞 +968 23 295 999\n📍 Salalah")
    st.link_button("📍 Open Sultan Qaboos Hospital in Maps",
        "https://maps.google.com/?q=Sultan+Qaboos+Hospital+Salalah+Oman")
    st.markdown("---")

    et1,et2,et3,et4,et5 = st.tabs([
        "❤️ Heart Attack","💓 CPR","😮‍💨 Choking","😵 Fainting","🌡️ Heat Stroke"])

    with et1:
        e1,e2 = st.columns(2)
        with e1:
            st.markdown("### Signs / العلامات")
            for s in ["💔 Chest pain or pressure","😮‍💨 Shortness of breath",
                "💪 Pain in left arm or jaw","😰 Sudden cold sweat",
                "🤢 Nausea","😵 Dizziness"]:
                st.markdown(f'<div class="step-red">{s}</div>',unsafe_allow_html=True)
        with e2:
            st.markdown("### Steps / الخطوات")
            for i,s in enumerate(["📞 Call 999 immediately",
                "🪑 Sit patient down — do NOT let them walk",
                "👗 Loosen tight clothing",
                "💊 Aspirin 300mg if available and not allergic",
                "🧍 Stay with patient — never leave alone",
                "🚫 No food or water","🚫 Do not drive themselves"],1):
                st.markdown(f'<div class="step-red"><b>{i}.</b> {s}</div>',unsafe_allow_html=True)

    with et2:
        st.error("Only do CPR if person is **unconscious and NOT breathing**")
        c1,c2 = st.columns(2)
        with c1:
            for i,s in enumerate(["Tap shoulder — check response",
                "Call 999","Lay flat on hard surface",
                "Heel of hand on CENTRE of chest",
                "Other hand on top, fingers interlocked",
                "Push DOWN 5–6cm hard and fast",
                "30 compressions at 100–120/min",
                "Tilt head back, lift chin",
                "Pinch nose — give 2 breaths",
                "Repeat: 30 compressions + 2 breaths",
                "Continue until help arrives"],1):
                st.markdown(f'<div class="step-red"><b>{i}.</b> {s}</div>',unsafe_allow_html=True)
        with c2:
            st.warning("🎵 **Rhythm:** Push to beat of 'Stayin Alive' = 100 bpm\n\n"
                "💪 Press HARD — at least 5cm\n\n"
                "😮‍💨 No rescue breaths? Compressions only is OK\n\n"
                "🔄 Switch every 2 min if someone can help\n\n"
                "🚑 Don't stop until paramedics arrive")

    with et3:
        ch1,ch2 = st.columns(2)
        with ch1:
            st.markdown("### Signs"); 
            for s in ["Cannot speak","Hands on throat","Weak cough","Skin turning blue"]:
                st.markdown(f'<div class="step-red">{s}</div>',unsafe_allow_html=True)
            st.markdown("### Steps")
            for i,s in enumerate(["Ask: Can you speak?","Tell them to cough hard",
                "Lean forward","5 back blows between shoulders",
                "5 abdominal thrusts","Alternate until clear","Call 999 if unconscious"],1):
                st.markdown(f'<div class="step"><b>{i}.</b> {s}</div>',unsafe_allow_html=True)
        with ch2:
            st.info("**Heimlich Manoeuvre:**\n\n"
                "1. Stand BEHIND the person\n2. Fist above belly button\n"
                "3. Grab fist with other hand\n4. Sharp inward + upward thrusts\n"
                "5. Repeat until object expelled")

    with et4:
        f1,f2 = st.columns(2)
        with f1:
            for i,s in enumerate(["Lay flat on ground",
                "Raise legs above heart level","Loosen clothing",
                "Check breathing","Turn on side if vomiting",
                "No water while unconscious",
                "Call 999 if not waking in 1 min"],1):
                st.markdown(f'<div class="step"><b>{i}.</b> {s}</div>',unsafe_allow_html=True)
        with f2:
            st.success("**Prevention:**\n- Drink water regularly\n"
                "- Rise slowly from sitting\n- Eat regular meals\n"
                "- Sit down if feeling faint")

    with et5:
        st.error("Heat stroke is a MEDICAL EMERGENCY — call 999 immediately")
        hs1,hs2 = st.columns(2)
        with hs1:
            st.markdown("### Signs")
            for s in ["🌡️ Temp above 40°C","🧠 Confusion","🚫 Hot dry skin",
                "🤢 Nausea","💓 Rapid heartbeat","😵 Loss of consciousness"]:
                st.markdown(f'<div class="step-red">{s}</div>',unsafe_allow_html=True)
        with hs2:
            st.markdown("### Steps")
            for i,s in enumerate(["Call 999","Move to shade/cool room",
                "Remove excess clothing","Wet cloths on neck+armpits+groin",
                "Fan continuously","Cool water if conscious",
                "Do NOT give aspirin","Monitor breathing"],1):
                st.markdown(f'<div class="step"><b>{i}.</b> {s}</div>',unsafe_allow_html=True)

# ══════════════════════════════════════
# TAB 4 — MEDICINE GUIDE
# ══════════════════════════════════════
with tab_medicine:
    st.markdown("### 💊 Medicine Information Guide")
    st.markdown("""<div class="disclaimer">
        ⚠️ General info only. Always follow your doctor's prescription.</div>""",
        unsafe_allow_html=True)
    st.markdown("")

    medicines = {
        "Paracetamol (Panadol)": {"e":"💊",
            "for":"Fever, headache, mild pain",
            "dose":"500–1000mg every 4–6 hrs. Max 4g/day.",
            "warn":"Do not exceed 4g/day. Avoid alcohol.",
            "avoid":"Liver disease","tip":"Safest painkiller for elderly"},
        "Ibuprofen (Brufen)": {"e":"💊",
            "for":"Pain, inflammation, fever",
            "dose":"200–400mg every 6–8 hrs WITH food.",
            "warn":"Must take with food. Can cause stomach bleeding.",
            "avoid":"Kidney problems, stomach ulcers, pregnancy","tip":"Always eat before taking"},
        "Metformin": {"e":"🔵",
            "for":"Type 2 diabetes — lowers blood sugar",
            "dose":"500–1000mg twice daily with meals.",
            "warn":"Take with food. Stay hydrated.",
            "avoid":"Kidney disease","tip":"Never stop without doctor advice"},
        "Amlodipine": {"e":"❤️",
            "for":"High blood pressure, chest pain",
            "dose":"5–10mg once daily.",
            "warn":"May cause ankle swelling.",
            "avoid":"Severe low blood pressure","tip":"Take at same time each day"},
        "Omeprazole": {"e":"🟡",
            "for":"Heartburn, stomach acid, ulcers",
            "dose":"20mg once daily 30 min before eating.",
            "warn":"Long-term use may reduce magnesium.",
            "avoid":"Do not use long-term without review","tip":"Take before breakfast"},
        "Salbutamol (Ventolin)": {"e":"💨",
            "for":"Asthma, wheezing, breathlessness",
            "dose":"1–2 puffs when needed. Max 4x/day.",
            "warn":"See doctor if using more than 3x/week.",
            "avoid":"Heart rhythm problems","tip":"Always carry in Khareef season"},
        "Aspirin 75mg": {"e":"🔴",
            "for":"Prevents heart attack and stroke",
            "dose":"75mg once daily with food.",
            "warn":"Can cause stomach bleeding.",
            "avoid":"Under 16, stomach ulcers","tip":"Do not stop without doctor"},
        "Atorvastatin": {"e":"🟠",
            "for":"High cholesterol, heart disease prevention",
            "dose":"10–80mg once daily at night.",
            "warn":"Report muscle pain immediately.",
            "avoid":"Liver disease, pregnancy","tip":"Take at night for best effect"},
    }

    sel = st.selectbox("Select a medicine:", list(medicines.keys()),
        format_func=lambda x:f"{medicines[x]['e']} {x}", key="med_sel")
    if sel:
        m = medicines[sel]
        st.markdown(f"### {m['e']} {sel}")
        st.info(f"💡 **Tip:** {m['tip']}")
        mm1,mm2 = st.columns(2)
        with mm1:
            st.success(f"**✅ Used for:**\n{m['for']}")
            st.info(f"**💊 Dose:**\n{m['dose']}")
        with mm2:
            st.warning(f"**⚠️ Warning:**\n{m['warn']}")
            st.error(f"**🚫 Avoid if:**\n{m['avoid']}")

    st.markdown("---")
    st.markdown("""<div class="disclaimer">
        ⚠️ Always consult a doctor or pharmacist before taking any medication.</div>""",
        unsafe_allow_html=True)

# ══════════════════════════════════════
# TAB 5 — HISTORY
# ══════════════════════════════════════
with tab_history:
    st.markdown("### 📊 All User Records")
    st.caption("Every health check ever performed on this app")

    records = load_json(RECORDS_FILE)
    if records:
        df = pd.DataFrame(records).sort_values("timestamp", ascending=False)

        s1,s2,s3,s4 = st.columns(4)
        s1.metric("Total Checks", len(df))
        s2.metric("🟢 Green",  len(df[df["triage_level"]=="GREEN"]))
        s3.metric("🟡 Yellow", len(df[df["triage_level"]=="YELLOW"]))
        s4.metric("🔴 Red",    len(df[df["triage_level"]=="RED"]))

        st.markdown("---")
        search = st.text_input("Search by name:", key="hist_search")
        if search:
            df = df[df["name"].str.contains(search, case=False, na=False)]

        fltr = st.multiselect("Filter by level:", ["GREEN","YELLOW","RED"],
            default=["GREEN","YELLOW","RED"], key="hist_filter")
        if fltr:
            df = df[df["triage_level"].isin(fltr)]

        st.markdown(f"**{len(df)} records**")
        st.dataframe(df, use_container_width=True, height=400)

        c1,c2 = st.columns(2)
        with c1:
            st.download_button("📥 Download CSV",
                df.to_csv(index=False), "records.csv", "text/csv", key="dl_csv")
        with c2:
            st.download_button("📥 Download JSON",
                json.dumps(records, indent=2, ensure_ascii=False),
                "records.json", "application/json", key="dl_json")

        st.markdown("---")
        if st.button("🗑️ Clear All Records", key="clear_recs"):
            if os.path.exists(RECORDS_FILE): os.remove(RECORDS_FILE)
            st.success("Cleared!"); st.rerun()
    else:
        st.info("No records yet. Complete a Health Check to see data here.")

    st.markdown("---")
    st.markdown("### Saved Profiles")
    profiles = load_json(PROFILES_FILE)
    if profiles:
        st.dataframe(pd.DataFrame(profiles), use_container_width=True)
        st.download_button("📥 Download Profiles",
            pd.DataFrame(profiles).to_csv(index=False),
            "profiles.csv","text/csv", key="dl_prof2")
    else:
        st.caption("No profiles saved yet")

# ══════════════════════════════════════
# TAB 6 — ABOUT
# ══════════════════════════════════════
with tab_about:
    ab1,ab2 = st.columns(2)
    with ab1:
        st.markdown(f"""<div class="profile-card">
            <div style="font-size:3rem">👨‍💻</div>
            <div style="font-size:1.3rem;font-weight:700;margin:8px 0">Sadga Selime</div>
            <div style="opacity:0.85">Developer & Designer</div>
            <div style="opacity:0.85">Salalah, Dhofar, Oman 🇴🇲</div>
            <div style="margin-top:10px;font-size:0.82rem;opacity:0.75">
                Python · Streamlit · Google Gemini AI</div>
        </div>""", unsafe_allow_html=True)
    with ab2:
        st.markdown("""### 🌿 About Khareef Health
**Khareef Health** is a free AI medical triage assistant
built for the community of **Salalah, Dhofar, Oman**.

Get instant health advice in **English and Arabic**
without needing to visit a doctor for every concern.

Named after Salalah's unique **Khareef** monsoon season.
        """)

    st.markdown("---")
    ec1,ec2,ec3 = st.columns(3)
    with ec1: st.error("**Emergency**\n📞 999")
    with ec2: st.info("**Sultan Qaboos**\n📞 +968 23 218 000")
    with ec3: st.info("**Salalah Private**\n📞 +968 23 295 999")

    st.markdown("---")
    st.markdown("""<div class="disclaimer">
        ⚠️ For educational purposes only. NOT a substitute for professional medical advice.
        Always consult a licensed doctor. Emergency: <strong>999</strong>
    </div>""", unsafe_allow_html=True)

# ── FOOTER ──
st.markdown("---")
st.caption("🌿 Khareef Health v3.2 · by Sadga Selime · Salalah, Oman · Powered by Google Gemini AI · Educational use only")
