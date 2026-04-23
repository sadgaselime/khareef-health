"""
main.py – Khareef Health v3.1
Fixed duplicate element IDs + full user data storage
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
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════
# USER DATA STORAGE
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
    # Update existing or add new
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
    "gender": "Not specified",
    "user_name": "",
    "user_age": 40,
    "user_city": "Salalah",
    "user_conditions": [],
    "user_medications": "",
    "user_phone": "",
    "user_blood_type": "Unknown",
    "profile_saved": False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ══════════════════════════════════════
# THEMES
# ══════════════════════════════════════
THEMES = {
    "Male":          {"p":"#1a4a8a","s":"#2d6fba","l":"#e8f0fb","a":"#0d2d5c","g":"135deg,#0d2d5c,#1a4a8a,#2d6fba"},
    "Female":        {"p":"#8a1a5c","s":"#c44d8a","l":"#fbe8f3","a":"#5c0d3a","g":"135deg,#5c0d3a,#8a1a5c,#c44d8a"},
    "Not specified": {"p":"#1a5c45","s":"#2d8a65","l":"#e8f5ef","a":"#0d3d29","g":"135deg,#0d3d29,#1a5c45,#2d8a65"},
}
T = THEMES.get(st.session_state.gender, THEMES["Not specified"])

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&family=Poppins:wght@300;400;600;700&display=swap');
html,body,[class*="css"]{{font-family:'Poppins',sans-serif;}}
.stApp{{background:linear-gradient(160deg,{T['l']} 0%,#f8f9fa 50%,{T['l']} 100%);}}
.app-header{{background:linear-gradient({T['g']});border-radius:20px;padding:24px 32px;
    margin-bottom:20px;color:white;box-shadow:0 8px 32px {T['p']}44;}}
.app-header h1{{font-size:1.9rem;font-weight:700;margin:0;color:white;}}
.app-header .byline{{font-size:0.75rem;opacity:0.6;}}
.app-header .sub{{font-size:0.9rem;opacity:0.82;}}
.app-header .ar{{font-family:'Tajawal',sans-serif;font-size:0.85rem;opacity:0.7;direction:rtl;}}
.profile-card{{background:linear-gradient({T['g']});color:white;border-radius:16px;
    padding:24px;text-align:center;box-shadow:0 4px 20px {T['p']}44;}}
.step{{background:{T['l']};border-left:4px solid {T['p']};border-radius:8px;
    padding:10px 14px;margin:6px 0;font-size:0.9rem;line-height:1.6;}}
.step-red{{background:#fff5f5;border-left:4px solid #dc2626;border-radius:8px;
    padding:10px 14px;margin:6px 0;font-size:0.9rem;line-height:1.6;}}
.arabic-text{{font-family:'Tajawal',sans-serif;direction:rtl;text-align:right;
    font-size:1.1rem;line-height:2.1;background:#fffbf0;border-radius:10px;
    padding:16px 20px;border:1px solid #fde68a;}}
.nutrition-tip{{background:#f0fdf4;border-left:3px solid #22c55e;border-radius:6px;
    padding:9px 14px;margin:5px 0;font-size:0.88rem;}}
.disclaimer{{background:#fff8e1;border:1px solid #fcd34d;border-radius:10px;
    padding:12px 18px;font-size:0.82rem;color:#78350f;line-height:1.6;}}
.result-green{{background:linear-gradient(135deg,#dcfce7,#bbf7d0);border:3px solid #16a34a;
    border-radius:16px;padding:24px;text-align:center;}}
.result-yellow{{background:linear-gradient(135deg,#fef9c3,#fde68a);border:3px solid #f59e0b;
    border-radius:16px;padding:24px;text-align:center;}}
.result-red{{background:linear-gradient(135deg,#fee2e2,#fecaca);border:3px solid #dc2626;
    border-radius:16px;padding:24px;text-align:center;
    animation:pulse 2s infinite;}}
@keyframes pulse{{0%,100%{{box-shadow:0 0 0 0 rgba(220,38,38,0.3);}}50%{{box-shadow:0 0 0 12px rgba(220,38,38,0);}}}}
.stTabs [data-baseweb="tab-list"]{{gap:6px;background:white;border-radius:12px;
    padding:5px;box-shadow:0 2px 12px rgba(0,0,0,0.06);}}
.stTabs [data-baseweb="tab"]{{border-radius:8px;font-weight:600;font-size:0.85rem;padding:7px 14px;}}
.stTabs [aria-selected="true"]{{background:{T['p']} !important;color:white !important;}}
section[data-testid="stSidebar"]{{background:linear-gradient(180deg,{T['a']} 0%,{T['p']} 100%);}}
section[data-testid="stSidebar"] *{{color:white !important;}}
#MainMenu{{visibility:hidden;}}footer{{visibility:hidden;}}header{{visibility:hidden;}}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════
with st.sidebar:
    st.markdown("## 🌿 Khareef Health")
    st.caption("by Sadga Selime")
    st.markdown("---")
    st.markdown("### Gender / الجنس")
    g = st.radio("Gender", ["Not specified","Male","Female"],
        index=["Not specified","Male","Female"].index(st.session_state.gender),
        horizontal=True, label_visibility="collapsed", key="sidebar_gender")
    if g != st.session_state.gender:
        st.session_state.gender = g
        st.rerun()
    emoji_map = {"Male":"💙 Blue","Female":"💗 Rose","Not specified":"💚 Green"}
    st.caption(f"{emoji_map[st.session_state.gender]} theme active")
    st.markdown("---")
    khareef_mode = st.toggle("🌦️ Khareef Mode", value=False, key="khareef")
    show_arabic  = st.toggle("🌐 Arabic / عربي",  value=True,  key="arabic")
    use_gemini   = st.toggle("🤖 AI Advice",       value=is_api_key_configured(), key="gemini")
    st.markdown("---")
    st.markdown("### 🏥 Emergency")
    st.error("📞 **999**")
    st.markdown("Sultan Qaboos Hospital")
    st.caption("+968 23 218 000")
    st.markdown("---")
    st.caption(get_api_key_status())

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
  </div>
</div>
""", unsafe_allow_html=True)

if khareef_mode:
    st.warning("🌦️ Khareef Mode Active — Higher respiratory sensitivity")

# ══════════════════════════════════════
# TABS
# ══════════════════════════════════════
tabs = st.tabs(["👤 My Profile","🩺 Health Check","🚨 Emergency","💊 Medicines","📊 History","ℹ️ About"])
tab_profile, tab_assess, tab_emergency, tab_medicine, tab_history, tab_about = tabs

# ══════════════════════════════════════
# TAB 1 — PROFILE
# ══════════════════════════════════════
with tab_profile:
    st.markdown("### 👤 Your Profile / ملفك الشخصي")
    st.caption("Save your information once — it will be used automatically in health checks")

    col_p1, col_p2 = st.columns([1,1])

    with col_p1:
        st.markdown("#### Personal Information")
        p_name   = st.text_input("Full Name / الاسم الكامل",
            value=st.session_state.user_name,
            placeholder="e.g. Ahmed Al-Shanfari", key="p_name")
        p_age    = st.number_input("Age / العمر", min_value=1, max_value=120,
            value=st.session_state.user_age, key="p_age")
        p_gender = st.selectbox("Gender / الجنس",
            ["Not specified","Male","Female"],
            index=["Not specified","Male","Female"].index(st.session_state.gender),
            key="p_gender")
        p_phone  = st.text_input("Phone Number / رقم الهاتف",
            value=st.session_state.user_phone,
            placeholder="+968 9X XXX XXXX", key="p_phone")
        p_city   = st.selectbox("City / المدينة",
            ["Salalah","Taqah","Mirbat","Rakhyut","Muscat","Sohar","Other"],
            index=["Salalah","Taqah","Mirbat","Rakhyut","Muscat","Sohar","Other"].index(
                st.session_state.user_city) if st.session_state.user_city in
                ["Salalah","Taqah","Mirbat","Rakhyut","Muscat","Sohar","Other"] else 0,
            key="p_city")

        st.markdown("#### Medical Information")
        p_blood  = st.selectbox("Blood Type / فصيلة الدم",
            ["Unknown","A+","A-","B+","B-","O+","O-","AB+","AB-"],
            index=["Unknown","A+","A-","B+","B-","O+","O-","AB+","AB-"].index(
                st.session_state.user_blood_type)
                if st.session_state.user_blood_type in
                ["Unknown","A+","A-","B+","B-","O+","O-","AB+","AB-"] else 0,
            key="p_blood")
        p_conditions = st.multiselect("Existing Conditions / أمراض معروفة",
            ["Diabetes","High Blood Pressure","Asthma","Heart Disease",
             "Kidney Disease","Arthritis","Thyroid","Anaemia","None"],
            default=st.session_state.user_conditions, key="p_conditions")
        p_meds   = st.text_area("Daily Medications / الأدوية اليومية",
            value=st.session_state.user_medications,
            placeholder="List your daily medications...", height=80, key="p_meds")
        p_allergy = st.text_input("Allergies / الحساسية",
            placeholder="e.g. Penicillin, Aspirin...", key="p_allergy")
        p_emergency_contact = st.text_input(
            "Emergency Contact Name & Number / جهة اتصال طارئة",
            placeholder="e.g. Mohammed +968 9X XXX XXXX", key="p_emergency")

        if st.button("💾 Save Profile", type="primary",
                use_container_width=True, key="save_profile_btn"):
            st.session_state.user_name        = p_name
            st.session_state.user_age         = p_age
            st.session_state.gender           = p_gender
            st.session_state.user_phone       = p_phone
            st.session_state.user_city        = p_city
            st.session_state.user_blood_type  = p_blood
            st.session_state.user_conditions  = p_conditions
            st.session_state.user_medications = p_meds
            st.session_state.profile_saved    = True

            profile_data = {
                "saved_at":        datetime.now().strftime("%Y-%m-%d %H:%M"),
                "name":            p_name,
                "age":             p_age,
                "gender":          p_gender,
                "phone":           p_phone,
                "city":            p_city,
                "blood_type":      p_blood,
                "conditions":      p_conditions,
                "medications":     p_meds,
                "allergies":       p_allergy,
                "emergency_contact": p_emergency_contact,
            }
            save_profile(profile_data)
            st.success("✅ Profile saved! Your information is stored.")
            st.rerun()

    with col_p2:
        st.markdown("#### Your Profile Card")
        if st.session_state.user_name:
            risk = "Higher Risk ⚠️" if st.session_state.user_age >= 60 else "Standard Risk ✅"
            conds = ", ".join(st.session_state.user_conditions) if st.session_state.user_conditions else "None"
            st.markdown(f"""
            <div class="profile-card">
                <div style="font-size:3rem">{g_emoji}</div>
                <div style="font-size:1.4rem;font-weight:700;margin:10px 0">
                    {st.session_state.user_name}</div>
                <div style="opacity:0.9;margin:4px 0">🎂 Age: {st.session_state.user_age}</div>
                <div style="opacity:0.9;margin:4px 0">⚧ Gender: {st.session_state.gender}</div>
                <div style="opacity:0.9;margin:4px 0">📍 City: {st.session_state.user_city}</div>
                <div style="opacity:0.9;margin:4px 0">🩸 Blood: {st.session_state.user_blood_type}</div>
                <div style="margin-top:12px;background:rgba(255,255,255,0.15);
                    border-radius:8px;padding:8px;font-size:0.85rem">
                    Risk Level: {risk}
                </div>
                <div style="margin-top:8px;background:rgba(255,255,255,0.15);
                    border-radius:8px;padding:8px;font-size:0.82rem;text-align:left">
                    Conditions: {conds}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("👈 Fill in your profile and click Save\nYour profile card will appear here")

        st.markdown("#### All Saved Profiles")
        profiles = load_json(PROFILES_FILE)
        if profiles:
            st.dataframe(pd.DataFrame(profiles), use_container_width=True)
            csv_p = pd.DataFrame(profiles).to_csv(index=False)
            st.download_button("📥 Download Profiles CSV", csv_p,
                "profiles.csv", "text/csv", key="dl_profiles")
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
    st.caption("Click the mic and speak your symptoms — works best in Chrome")

    components.html(f"""
    <div style="background:{T['l']};border:2px dashed {T['s']};
         border-radius:14px;padding:20px;text-align:center;margin:8px 0;">
        <button id="voiceBtn" onclick="startVoice()" style="
            background:linear-gradient({T['g']});color:white;border:none;
            border-radius:50px;padding:14px 36px;font-size:1.1rem;
            font-weight:700;cursor:pointer;font-family:'Poppins',sans-serif;
            box-shadow:0 4px 16px {T['p']}55;">
            🎤 Tap to Speak / انقر للتحدث
        </button>
        <div id="status" style="margin-top:12px;color:{T['p']};font-weight:600;font-size:0.9rem;"></div>
        <div id="transcript" style="margin-top:10px;background:white;border-radius:10px;
             padding:12px;min-height:44px;font-size:1rem;color:#1a3a2a;
             text-align:left;border:1px solid {T['s']}55;"></div>
        <div style="margin-top:8px;font-size:0.78rem;color:#6b7280;">
            Supports English & Arabic · Copy result to symptoms box below
        </div>
    </div>
    <script>
    let recognizing=false,recognition;
    function startVoice(){{
        if(!('webkitSpeechRecognition' in window)&&!('SpeechRecognition' in window)){{
            document.getElementById('status').innerHTML='❌ Use Chrome browser for voice input';return;
        }}
        if(recognizing){{recognition.stop();return;}}
        const SR=window.SpeechRecognition||window.webkitSpeechRecognition;
        recognition=new SR();recognition.lang='ar-OM';
        recognition.interimResults=true;recognition.maxAlternatives=1;
        recognition.onstart=function(){{
            recognizing=true;
            document.getElementById('voiceBtn').innerHTML='⏹️ Stop / وقف';
            document.getElementById('voiceBtn').style.background='#dc2626';
            document.getElementById('status').innerHTML='🔴 Listening... / جاري الاستماع...';
        }};
        recognition.onresult=function(e){{
            let f='',interim='';
            for(let i=e.resultIndex;i<e.results.length;i++){{
                if(e.results[i].isFinal)f+=e.results[i][0].transcript;
                else interim+=e.results[i][0].transcript;
            }}
            document.getElementById('transcript').innerHTML=
                f+'<span style="color:#9ca3af">'+interim+'</span>';
        }};
        recognition.onerror=function(e){{
            document.getElementById('status').innerHTML='❌ Error: '+e.error;
            recognizing=false;
        }};
        recognition.onend=function(){{
            recognizing=false;
            document.getElementById('voiceBtn').innerHTML='🎤 Tap to Speak / انقر للتحدث';
            document.getElementById('voiceBtn').style.background='linear-gradient({T["g"]})';
            document.getElementById('status').innerHTML='✅ Done! Copy text above to symptoms box below';
        }};
        recognition.start();
    }}
    </script>
    """, height=215)

    st.markdown("---")

    # ── VITALS ──
    st.markdown("### 🩺 Vital Signs / العلامات الحيوية")
    know_vitals = st.toggle("I have my readings (BP / Sugar / Temperature)",
        value=False, key="know_vitals",
        help="Turn ON if you have a blood pressure monitor or thermometer")

    if not know_vitals:
        st.info("No problem! You can still get symptom-based advice.\n\n"
                "For best accuracy, use a BP monitor and thermometer.")
        bp_systolic=120; bp_diastolic=80; blood_sugar=100; temperature=37.0
    else:
        st.markdown("#### Blood Pressure / ضغط الدم")
        st.caption("The two numbers from your BP monitor")
        bpc1, bpc2 = st.columns(2)
        with bpc1:
            st.markdown("**Upper Number (Systolic)**")
            st.caption("Normal: 90–120")
            bp_systolic = st.number_input("Systolic mmHg", min_value=60,
                max_value=240, value=120, key="bp_sys", label_visibility="collapsed")
            if bp_systolic>=180:   st.error("🔴 Dangerously HIGH")
            elif bp_systolic<90:   st.error("🔴 Dangerously LOW")
            elif bp_systolic>=140: st.warning("🟡 High")
            else:                   st.success("🟢 Normal")
        with bpc2:
            st.markdown("**Lower Number (Diastolic)**")
            st.caption("Normal: 60–80")
            bp_diastolic = st.number_input("Diastolic mmHg", min_value=40,
                max_value=140, value=80, key="bp_dia", label_visibility="collapsed")
            if bp_diastolic>=120:   st.error("🔴 Dangerously HIGH")
            elif bp_diastolic<60:   st.error("🔴 Dangerously LOW")
            elif bp_diastolic>=90:  st.warning("🟡 High")
            else:                    st.success("🟢 Normal")
        st.markdown(f"**Combined: {bp_systolic}/{bp_diastolic} mmHg**")
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
    st.caption("Select all that apply, or paste from voice input above")

    selected_symptoms = []
    sc1,sc2,sc3,sc4 = st.columns(4)
    if sc1.checkbox("Cough / سعال",       key="s_cough"):     selected_symptoms.append("cough")
    if sc2.checkbox("Breathless / ضيق",   key="s_breath"):    selected_symptoms.append("breathlessness")
    if sc3.checkbox("Chest Pain / صدر",   key="s_chest"):     selected_symptoms.append("chest_pain")
    if sc4.checkbox("Dizziness / دوار",   key="s_dizzy"):     selected_symptoms.append("dizziness")
    if sc1.checkbox("Fever / حمى",        key="s_fever"):     selected_symptoms.append("fever")
    if sc2.checkbox("Fatigue / إعياء",    key="s_fatigue"):   selected_symptoms.append("fatigue")
    if sc3.checkbox("Headache / صداع",    key="s_headache"):  selected_symptoms.append("headache")
    if sc4.checkbox("Nausea / غثيان",     key="s_nausea"):    selected_symptoms.append("nausea")

    extra = st.text_area("Other symptoms / أعراض أخرى:",
        placeholder="Type or paste voice text here...", height=65, key="extra_symp")
    if extra.strip():
        extras = [s.strip() for s in extra.replace(",","\n").splitlines() if s.strip()]
        selected_symptoms.extend(normalize_symptoms(extras))
        selected_symptoms = list(set(selected_symptoms))

    if selected_symptoms:
        st.info(f"Selected: {', '.join(selected_symptoms)}")

    if "chest_pain" in selected_symptoms or "breathlessness" in selected_symptoms:
        st.error("🚨 SERIOUS SYMPTOMS — Go to Emergency tab or call 999 now!")

    st.markdown("""<div class="disclaimer">
        ⚠️ This is a health guide only. NOT a doctor.
        Emergency: <strong>999</strong></div>""", unsafe_allow_html=True)
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

            # Save complete record
            record = {
                "timestamp":    datetime.now().strftime("%Y-%m-%d %H:%M"),
                "name":         patient.name,
                "age":          patient.age,
                "gender":       st.session_state.gender,
                "city":         st.session_state.user_city,
                "blood_type":   st.session_state.user_blood_type,
                "phone":        st.session_state.user_phone,
                "conditions":   ", ".join(st.session_state.user_conditions) if st.session_state.user_conditions else "None",
                "medications":  st.session_state.user_medications,
                "bp":           f"{bp_systolic}/{bp_diastolic}" if know_vitals else "Not measured",
                "blood_sugar":  blood_sugar if know_vitals else "Not measured",
                "temperature":  temperature if know_vitals else "Not measured",
                "symptoms":     ", ".join(selected_symptoms) if selected_symptoms else "None",
                "vitals_known": know_vitals,
                "khareef_mode": khareef_mode,
                "triage_level": result["level"],
                "findings":     " | ".join(result["reasons"]),
                "ai_used":      bool(ai_result and ai_result.get("success")),
            }
            save_record(record)
            log_patient(patient, result)

            # ── RESULTS ──
            st.markdown("---")
            st.markdown(f"## Results for **{patient.name}**")

            level = result["level"]
            css_map = {"GREEN":"result-green","YELLOW":"result-yellow","RED":"result-red"}
            lmap = {
                "GREEN":  ("🟢 ALL CLEAR",             "بصحة جيدة",         "#16a34a"),
                "YELLOW": ("🟡 ATTENTION NEEDED",       "يحتاج انتباهاً",    "#d97706"),
                "RED":    ("🔴 URGENT — SEEK HELP NOW","عاجل — اطلب المساعدة","#dc2626"),
            }
            le, la, col = lmap[level]
            st.markdown(f"""
            <div class="{css_map[level]}">
              <div style="font-size:1.8rem;font-weight:700;color:{col}">{le}</div>
              <div style="font-family:'Tajawal',sans-serif;font-size:1.2rem;
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
    st.markdown("""<div style="background:linear-gradient(135deg,#dc2626,#7f1d1d);
        border-radius:16px;padding:20px 28px;color:white;text-align:center;
        margin-bottom:20px;box-shadow:0 4px 20px rgba(220,38,38,0.3)">
        <div style="font-size:2.5rem">🚨</div>
        <div style="font-size:1.5rem;font-weight:700">EMERGENCY FIRST AID GUIDE</div>
        <div style="opacity:0.85">دليل الإسعافات الأولية</div>
    </div>""", unsafe_allow_html=True)

    st.error("🔴 Life in danger? **CALL 999 FIRST**, then follow steps below")

    h1,h2,h3 = st.columns(3)
    with h1: st.error("**🚑 Emergency**\n📞 **999**\n🕐 24/7")
    with h2: st.info("**🏥 Sultan Qaboos**\n📞 +968 23 218 000\n📍 Al Dahariz, Salalah")
    with h3: st.info("**🏥 Salalah Private**\n📞 +968 23 295 999\n📍 Salalah")
    st.link_button("📍 Sultan Qaboos Hospital Maps",
        "https://maps.google.com/?q=Sultan+Qaboos+Hospital+Salalah+Oman")
    st.markdown("---")

    et1,et2,et3,et4,et5 = st.tabs([
        "❤️ Heart Attack","💓 CPR","😮‍💨 Choking","😵 Fainting","🌡️ Heat Stroke"])

    with et1:
        st.markdown("## ❤️ Heart Attack")
        e1,e2 = st.columns(2)
        with e1:
            st.markdown("### Signs")
            for s in ["💔 Chest pain or pressure","😮‍💨 Shortness of breath",
                "💪 Pain in left arm, jaw or neck","😰 Sudden sweating",
                "🤢 Nausea or vomiting","😵 Dizziness or fainting"]:
                st.markdown(f'<div class="step-red">{s}</div>',unsafe_allow_html=True)
        with e2:
            st.markdown("### Steps")
            for i,s in enumerate(["📞 Call 999 immediately",
                "🪑 Sit patient down — do NOT let them walk or exert",
                "👗 Loosen collar and clothing",
                "💊 Give 300mg aspirin if available (not allergic)",
                "🧍 Stay with patient — never leave alone",
                "🚫 No food or water","🚫 Do not let them drive"],1):
                st.markdown(f'<div class="step-red"><strong>{i}.</strong> {s}</div>',
                    unsafe_allow_html=True)

    with et2:
        st.markdown("## 💓 CPR")
        st.error("Only do CPR if person is **unconscious and not breathing**")
        c1,c2 = st.columns(2)
        with c1:
            for i,s in enumerate(["Check response — tap shoulder, shout",
                "Call 999","Lay flat on back on hard surface",
                "Place heel of hand on CENTRE of chest",
                "Other hand on top, fingers interlocked",
                "Push DOWN 5–6cm — hard and fast",
                "30 compressions at 100–120 per minute",
                "Tilt head back, lift chin",
                "Pinch nose, seal mouth, give 2 breaths",
                "Watch chest rise with each breath",
                "Repeat: 30 compressions + 2 breaths",
                "Continue until help arrives"],1):
                st.markdown(f'<div class="step-red"><strong>{i}.</strong> {s}</div>',
                    unsafe_allow_html=True)
        with c2:
            st.warning("""
🎵 **Rhythm:** Push to beat of 'Stayin Alive' = 100 bpm

💪 **Press HARD** — at least 5cm deep

😮‍💨 **No rescue breaths?** Chest compressions only is OK

🔄 **Switch** every 2 min if someone can help

🚑 **Don't stop** until paramedics arrive
            """)

    with et3:
        st.markdown("## 😮‍💨 Choking")
        ch1,ch2 = st.columns(2)
        with ch1:
            st.markdown("### Signs")
            for s in ["Cannot speak or cry","Hands clutching throat",
                "Weak cough","Skin turning blue","Cannot breathe"]:
                st.markdown(f'<div class="step-red">{s}</div>',unsafe_allow_html=True)
            st.markdown("### Steps — Conscious Adult")
            for i,s in enumerate(["Ask: Can you speak? Are you choking?",
                "Tell them to cough hard","Lean them forward",
                "5 firm back blows between shoulder blades",
                "5 abdominal thrusts (Heimlich)",
                "Alternate back blows and thrusts",
                "Call 999 if object won't come out"],1):
                st.markdown(f'<div class="step"><strong>{i}.</strong> {s}</div>',
                    unsafe_allow_html=True)
        with ch2:
            st.info("""**Heimlich Manoeuvre:**
1. Stand BEHIND the person
2. One foot forward for balance
3. Make a fist — place above belly button
4. Grab fist with other hand
5. Sharp inward AND upward thrusts
6. Repeat until object is expelled""")
            st.markdown("### For Infant under 1 year")
            for s in ["Hold face-down on your forearm",
                "5 back blows with heel of hand",
                "Turn face-up — 5 chest thrusts with 2 fingers",
                "Check mouth — remove visible object only",
                "Call 999 immediately"]:
                st.markdown(f'<div class="step-red">{s}</div>',unsafe_allow_html=True)

    with et4:
        st.markdown("## 😵 Fainting")
        f1,f2 = st.columns(2)
        with f1:
            st.markdown("### Steps")
            for i,s in enumerate(["Lay person flat on the ground",
                "Raise legs 30cm above heart level",
                "Loosen clothing — collar, belt",
                "Check they are breathing",
                "Turn on side if vomiting",
                "No food or water while unconscious",
                "Call 999 if not waking in 1 minute",
                "Stay with them as they recover"],1):
                st.markdown(f'<div class="step"><strong>{i}.</strong> {s}</div>',
                    unsafe_allow_html=True)
        with f2:
            st.markdown("### Common Causes")
            for s in ["🌡️ Heat or standing too long","💧 Dehydration",
                "😟 Shock or emotional stress","🩸 Low blood sugar",
                "💊 Medication side effects","🩺 Low blood pressure"]:
                st.markdown(f'<div class="step">{s}</div>',unsafe_allow_html=True)
            st.success("**Prevention:**\n- Drink water regularly\n- Rise slowly from sitting\n"
                "- Eat regular meals\n- Sit down if feeling faint")

    with et5:
        st.markdown("## 🌡️ Heat Stroke — Common in Salalah")
        st.error("Heat stroke is a MEDICAL EMERGENCY — call 999 immediately")
        hs1,hs2 = st.columns(2)
        with hs1:
            st.markdown("### Signs")
            for s in ["🌡️ Body temp above 40°C","🧠 Confusion or slurred speech",
                "🚫 Hot dry skin — stopped sweating","🤢 Nausea or vomiting",
                "💓 Rapid heartbeat","😵 Loss of consciousness","🤕 Severe headache"]:
                st.markdown(f'<div class="step-red">{s}</div>',unsafe_allow_html=True)
        with hs2:
            st.markdown("### Steps")
            for i,s in enumerate(["Call 999 immediately",
                "Move to shade or cool room",
                "Remove excess clothing",
                "Wet cloths on neck, armpits, groin",
                "Fan them continuously",
                "Cool (not cold) water if conscious",
                "Ice packs on neck, armpits, groin",
                "Do NOT give aspirin or paracetamol",
                "Monitor breathing until help arrives"],1):
                st.markdown(f'<div class="step"><strong>{i}.</strong> {s}</div>',
                    unsafe_allow_html=True)

# ══════════════════════════════════════
# TAB 4 — MEDICINE GUIDE
# ══════════════════════════════════════
with tab_medicine:
    st.markdown("### 💊 Medicine Information Guide")
    st.markdown("""<div class="disclaimer">
        ⚠️ General info only. Always follow your doctor's prescription.
        Never change dose without medical advice.</div>""", unsafe_allow_html=True)
    st.markdown("")

    medicines = {
        "Paracetamol (Panadol)": {"e":"💊","for":"Fever, headache, mild pain",
            "dose":"500–1000mg every 4–6 hrs. Max 4g/day.",
            "warn":"Do not exceed 4g/day. Avoid alcohol.",
            "avoid":"Liver disease, heavy alcohol use","tip":"Safest painkiller for elderly"},
        "Ibuprofen (Brufen)": {"e":"💊","for":"Pain, inflammation, fever",
            "dose":"200–400mg every 6–8 hrs WITH food.",
            "warn":"Must take with food. Can cause stomach bleeding.",
            "avoid":"Kidney problems, ulcers, pregnancy (3rd trimester)","tip":"Always eat before taking"},
        "Metformin": {"e":"🔵","for":"Type 2 diabetes — lowers blood sugar",
            "dose":"500–1000mg twice daily with meals.",
            "warn":"Take with food. Stay hydrated. Stop before CT scan.",
            "avoid":"Kidney disease","tip":"Never stop without doctor advice"},
        "Amlodipine": {"e":"❤️","for":"High blood pressure, angina",
            "dose":"5–10mg once daily at same time each day.",
            "warn":"May cause ankle swelling. Do not stop suddenly.",
            "avoid":"Severe low blood pressure","tip":"Take in the morning"},
        "Omeprazole": {"e":"🟡","for":"Heartburn, stomach acid, ulcers",
            "dose":"20mg once daily 30 min BEFORE eating.",
            "warn":"Long-term use may reduce magnesium and B12.",
            "avoid":"Do not use long-term without review","tip":"Take before breakfast"},
        "Salbutamol (Ventolin)": {"e":"💨","for":"Asthma, wheezing, breathlessness",
            "dose":"1–2 puffs when needed. Max 4 times/day.",
            "warn":"See doctor if using more than 3x/week.",
            "avoid":"Heart rhythm problems","tip":"Keep with you in Khareef season"},
        "Aspirin 75mg": {"e":"🔴","for":"Blood thinner — prevents heart attack/stroke",
            "dose":"75–100mg once daily with food.",
            "warn":"Can cause stomach bleeding. Do not use with ibuprofen.",
            "avoid":"Under 16s, stomach ulcers, bleeding disorders","tip":"Do not stop without doctor"},
        "Atorvastatin": {"e":"🟠","for":"High cholesterol, heart disease prevention",
            "dose":"10–80mg once daily at night.",
            "warn":"Report muscle pain immediately.",
            "avoid":"Liver disease, pregnancy, grapefruit juice","tip":"Take at night"},
    }

    sel = st.selectbox("Select a medicine:", list(medicines.keys()),
        format_func=lambda x:f"{medicines[x]['e']} {x}", key="med_select")
    if sel:
        m = medicines[sel]
        st.markdown(f"### {m['e']} {sel}")
        st.info(f"💡 **Tip:** {m['tip']}")
        mm1,mm2 = st.columns(2)
        with mm1:
            st.success(f"**✅ Used for:**\n{m['for']}")
            st.info(f"**💊 Usual Dose:**\n{m['dose']}")
        with mm2:
            st.warning(f"**⚠️ Warning:**\n{m['warn']}")
            st.error(f"**🚫 Avoid if:**\n{m['avoid']}")

    st.markdown("---")
    st.markdown("""<div class="disclaimer">
        ⚠️ This is general knowledge only. Always consult a doctor or pharmacist.</div>""",
        unsafe_allow_html=True)

# ══════════════════════════════════════
# TAB 5 — HISTORY
# ══════════════════════════════════════
with tab_history:
    st.markdown("### 📊 All User Assessment Records")
    st.caption("Complete data from every health check performed")

    records = load_json(RECORDS_FILE)
    if records:
        df = pd.DataFrame(records)
        df = df.sort_values("timestamp", ascending=False)

        total = len(df)
        g_count = len(df[df["triage_level"]=="GREEN"])
        y_count = len(df[df["triage_level"]=="YELLOW"])
        r_count = len(df[df["triage_level"]=="RED"])

        s1,s2,s3,s4 = st.columns(4)
        s1.metric("Total Checks",  total)
        s2.metric("🟢 Green",  g_count)
        s3.metric("🟡 Yellow", y_count)
        s4.metric("🔴 Red",    r_count)

        st.markdown("---")

        # Search/filter
        search = st.text_input("Search by name:", placeholder="Type a name...",
            key="history_search")
        if search:
            df = df[df["name"].str.contains(search, case=False, na=False)]

        level_filter = st.multiselect("Filter by triage level:",
            ["GREEN","YELLOW","RED"], default=["GREEN","YELLOW","RED"],
            key="level_filter")
        if level_filter:
            df = df[df["triage_level"].isin(level_filter)]

        st.markdown(f"**Showing {len(df)} records**")
        st.dataframe(df, use_container_width=True, height=400)

        csv_data = df.to_csv(index=False)
        st.download_button("📥 Download as CSV", csv_data,
            "khareef_health_records.csv", "text/csv", key="dl_records")

        json_data = json.dumps(records, indent=2, ensure_ascii=False)
        st.download_button("📥 Download as JSON", json_data,
            "khareef_health_records.json", "application/json", key="dl_json")

        st.markdown("---")
        if st.button("🗑️ Clear All Records", type="secondary", key="clear_records"):
            if os.path.exists(RECORDS_FILE): os.remove(RECORDS_FILE)
            st.success("All records cleared!")
            st.rerun()
    else:
        st.info("No assessments yet. Complete a Health Check to see records here.")

    st.markdown("---")
    st.markdown("### All Saved Profiles")
    profiles = load_json(PROFILES_FILE)
    if profiles:
        st.dataframe(pd.DataFrame(profiles), use_container_width=True)
        csv_p = pd.DataFrame(profiles).to_csv(index=False)
        st.download_button("📥 Download Profiles", csv_p,
            "profiles.csv","text/csv", key="dl_prof_hist")
    else:
        st.caption("No profiles saved yet")

# ══════════════════════════════════════
# TAB 6 — ABOUT
# ══════════════════════════════════════
with tab_about:
    st.markdown("### 🌿 About Khareef Health")
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
        st.markdown("""
**Khareef Health** is a free AI medical triage assistant
built for the community of **Salalah, Dhofar, Oman**.

Helps patients understand health readings, identify
warning signs, and get instant advice in **English and Arabic**.

Named after Salalah's unique **Khareef** monsoon season
(June–September) when health risks increase significantly.
        """)

    st.markdown("---")
    ec1,ec2,ec3 = st.columns(3)
    with ec1: st.error("**Emergency**\n📞 999")
    with ec2: st.info("**Sultan Qaboos**\n📞 +968 23 218 000")
    with ec3: st.info("**Salalah Private**\n📞 +968 23 295 999")

    st.markdown("---")
    st.markdown("""<div class="disclaimer">
        ⚠️ <strong>Disclaimer:</strong> For educational purposes only.
        NOT a substitute for professional medical advice.
        Always consult a licensed doctor. Emergency: <strong>999</strong>
    </div>""", unsafe_allow_html=True)

# ── FOOTER ──
st.markdown("---")
st.caption("🌿 Khareef Health v3.1 · by Sadga Selime · Salalah, Oman · Powered by Google Gemini AI · Educational use only")
