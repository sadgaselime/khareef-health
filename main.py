"""
main.py – Khareef Health v3.3
Fixed gender colour change + age categories + women's health
"""

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import json
import os
from datetime import datetime
from data import Patient, validate_patient_input, normalize_symptoms, log_patient, get_session_log
from triage import assess_patient
from gemini_helper import get_gemini_advice, is_api_key_configured, get_api_key_status, analyze_free_text
from diseases import DISEASES, CATEGORIES, search_diseases, get_by_category

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

def load_json(f):
    if os.path.exists(f):
        try:
            return json.load(open(f,"r"))
        except: return []
    return []

def save_json(f, data):
    json.dump(data, open(f,"w"), indent=2, ensure_ascii=False)

def save_record(r):
    d = load_json(RECORDS_FILE); d.append(r); save_json(RECORDS_FILE, d)

def save_profile(p):
    d = load_json(PROFILES_FILE)
    found = False
    for i,x in enumerate(d):
        if x.get("name","").lower()==p["name"].lower():
            d[i]=p; found=True; break
    if not found: d.append(p)
    save_json(PROFILES_FILE, d)


# ══════════════════════════════════════
# VISITOR TRACKING
# Records every visit automatically
# ══════════════════════════════════════
VISITORS_FILE = "visitors.json"

def log_visitor():
    """Logs every app visit with timestamp."""
    try:
        visitors = load_json(VISITORS_FILE)
        visit = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "date":      datetime.now().strftime("%Y-%m-%d"),
            "time":      datetime.now().strftime("%H:%M"),
        }
        visitors.append(visit)
        save_json(VISITORS_FILE, visitors)
    except Exception:
        pass

def get_visitor_stats():
    visitors = load_json(VISITORS_FILE)
    if not visitors:
        return {"total": 0, "today": 0, "by_date": {}}
    today = datetime.now().strftime("%Y-%m-%d")
    today_visits  = sum(1 for v in visitors if v.get("date") == today)
    by_date = {}
    for v in visitors:
        d = v.get("date", "unknown")
        by_date[d] = by_date.get(d, 0) + 1
    return {"total": len(visitors), "today": today_visits, "by_date": by_date}

# Track this visit (runs every time app loads)
if "visit_logged" not in st.session_state:
    log_visitor()
    st.session_state.visit_logged = True

# ══════════════════════════════════════
# SESSION STATE — gender MUST be set before CSS
# ══════════════════════════════════════
if "gender" not in st.session_state:
    st.session_state.gender = "Not specified"
for k,v in {
    "user_name":"","user_age":40,"user_city":"Salalah",
    "user_conditions":[],"user_medications":"","user_phone":"",
    "user_blood_type":"Unknown","khareef_mode":False,
    "show_arabic":True,"use_gemini":is_api_key_configured(),
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ══════════════════════════════════════
# GENDER SELECTOR — FIRST THING (before CSS)
# This ensures the colour applies immediately
# ══════════════════════════════════════
THEMES = {
    "Male":          {"p":"#1a4a8a","s":"#2d6fba","l":"#dbeafe","a":"#0d2d5c","g":"135deg,#0d2d5c,#1a4a8a,#2d6fba"},
    "Female":        {"p":"#9d174d","s":"#db2777","l":"#fce7f3","a":"#500724","g":"135deg,#500724,#9d174d,#db2777"},
    "Not specified": {"p":"#1a5c45","s":"#2d8a65","l":"#d1fae5","a":"#0d3d29","g":"135deg,#0d3d29,#1a5c45,#2d8a65"},
}
T = THEMES[st.session_state.gender]

# ══════════════════════════════════════
# CSS — uses current theme
# ══════════════════════════════════════
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&family=Poppins:wght@400;600;700&display=swap');
html,body,[class*="css"]{{font-family:'Poppins',sans-serif;}}
.stApp{{background:linear-gradient(150deg,{T['l']} 0%,#f9fafb 60%,{T['l']} 100%) !important;}}
section[data-testid="stSidebar"]{{display:none;}}
.app-header{{background:linear-gradient({T['g']});border-radius:20px;
    padding:28px 36px;margin-bottom:16px;color:white;
    box-shadow:0 8px 32px {T['p']}55;}}
.app-header h1{{font-size:2rem;font-weight:700;margin:0;color:white;}}
.app-header .byline{{font-size:0.75rem;opacity:0.65;margin-top:2px;}}
.app-header .sub{{font-size:0.92rem;opacity:0.85;margin-top:4px;}}
.app-header .ar{{font-family:'Tajawal',sans-serif;font-size:0.88rem;opacity:0.7;direction:rtl;}}
.profile-card{{background:linear-gradient({T['g']});color:white;
    border-radius:16px;padding:24px;text-align:center;
    box-shadow:0 4px 20px {T['p']}44;}}
.step{{background:{T['l']};border-left:4px solid {T['p']};
    border-radius:8px;padding:10px 14px;margin:6px 0;font-size:0.9rem;}}
.step-red{{background:#fff1f2;border-left:4px solid #dc2626;
    border-radius:8px;padding:10px 14px;margin:6px 0;font-size:0.9rem;}}
.step-pink{{background:#fdf2f8;border-left:4px solid #db2777;
    border-radius:8px;padding:10px 14px;margin:6px 0;font-size:0.9rem;}}
.arabic-text{{font-family:'Tajawal',sans-serif;direction:rtl;text-align:right;
    font-size:1.1rem;line-height:2.1;background:#fffbf0;
    border-radius:10px;padding:16px 20px;border:1px solid #fde68a;}}
.nutrition-tip{{background:#f0fdf4;border-left:3px solid #22c55e;
    border-radius:6px;padding:9px 14px;margin:5px 0;font-size:0.88rem;}}
.disclaimer{{background:#fff8e1;border:1px solid #fcd34d;
    border-radius:10px;padding:12px 18px;font-size:0.82rem;color:#78350f;}}
.women-card{{background:linear-gradient(135deg,#fdf2f8,#fce7f3);
    border-radius:14px;padding:20px;border:2px solid #db277733;margin:8px 0;}}
.result-green{{background:linear-gradient(135deg,#dcfce7,#bbf7d0);
    border:3px solid #16a34a;border-radius:16px;padding:24px;text-align:center;}}
.result-yellow{{background:linear-gradient(135deg,#fef9c3,#fde68a);
    border:3px solid #f59e0b;border-radius:16px;padding:24px;text-align:center;}}
.result-red{{background:linear-gradient(135deg,#fee2e2,#fecaca);
    border:3px solid #dc2626;border-radius:16px;padding:24px;text-align:center;
    animation:pulse 2s infinite;}}
@keyframes pulse{{0%,100%{{box-shadow:0 0 0 0 rgba(220,38,38,0.3);}}
    50%{{box-shadow:0 0 0 14px rgba(220,38,38,0);}}}}
.stTabs [data-baseweb="tab-list"]{{gap:4px;background:white;border-radius:14px;
    padding:5px;box-shadow:0 2px 14px rgba(0,0,0,0.07);flex-wrap:wrap;}}
.stTabs [data-baseweb="tab"]{{border-radius:10px;font-weight:600;font-size:0.82rem;padding:7px 12px;}}
.stTabs [aria-selected="true"]{{background:{T['p']} !important;color:white !important;}}
#MainMenu{{visibility:hidden;}}footer{{visibility:hidden;}}header{{visibility:hidden;}}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════
# HEADER
# ══════════════════════════════════════
g_emoji = "👨" if st.session_state.gender=="Male" else "👩" if st.session_state.gender=="Female" else "🌿"
st.markdown(f"""
<div class="app-header">
  <div style="display:flex;align-items:center;gap:20px;flex-wrap:wrap;">
    <div style="font-size:3.5rem;line-height:1">{g_emoji}</div>
    <div style="flex:1;">
      <h1>Khareef Health</h1>
      <div class="byline">by Sadga Selime</div>
      <div class="sub">AI Telemedicine Triage · Salalah, Dhofar, Oman</div>
      <div class="ar">مساعد الفرز الطبي الذكي · صلالة، ظفار، عُمان</div>
    </div>
    <div style="text-align:right;">
      <div style="font-size:0.85rem;opacity:0.8">📞 Emergency</div>
      <div style="font-size:2rem;font-weight:700">999</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════
# SETTINGS BAR
# ══════════════════════════════════════
st.markdown("#### ⚙️ Settings / الإعدادات")
s1,s2,s3,s4,s5 = st.columns([1.3,1,1,1,1.4])

with s1:
    # THIS is the key fix — we update session_state AND rerun
    new_gender = st.selectbox(
        "🎨 Gender Theme / اختر الثيم",
        ["Not specified","Male","Female"],
        index=["Not specified","Male","Female"].index(st.session_state.gender),
        key="gender_select_top"
    )
    if new_gender != st.session_state.gender:
        st.session_state.gender = new_gender
        st.rerun()  # ← This makes the colour change instantly!
    labels = {"Male":"💙 Blue Theme","Female":"💗 Rose Theme","Not specified":"💚 Green Theme"}
    st.caption(labels[st.session_state.gender])

with s2:
    khareef_mode = st.toggle("🌦️ Khareef Mode", value=st.session_state.khareef_mode, key="k_tog")
    st.session_state.khareef_mode = khareef_mode

with s3:
    show_arabic = st.toggle("🌐 Arabic / عربي", value=st.session_state.show_arabic, key="a_tog")
    st.session_state.show_arabic = show_arabic

with s4:
    use_gemini = st.toggle("🤖 AI Advice", value=st.session_state.use_gemini, key="g_tog")
    st.session_state.use_gemini = use_gemini

with s5:
    st.markdown(f"""
    <div style="background:{'#fef3c7' if khareef_mode else T['l']};border-radius:10px;
         padding:8px 14px;font-size:0.82rem;
         border:1px solid {'#f59e0b' if khareef_mode else T['s']}55;">
        {'🌦️ <b>Khareef Mode ON</b>' if khareef_mode else '💚 Normal Mode'}
    </div>""", unsafe_allow_html=True)

if khareef_mode:
    st.warning("🌦️ Khareef Mode Active — Higher respiratory sensitivity")

st.markdown("---")

# ══════════════════════════════════════
# MAIN TABS
# ══════════════════════════════════════
tab_profile, tab_assess, tab_emergency, tab_medicine, tab_women, tab_diseases, tab_about = st.tabs([
    "👤 My Profile",
    "🩺 Health Check",
    "🚨 Emergency",
    "💊 Medicines",
    "👩 Women's Health",
    "🦠 Diseases",
    "ℹ️ About",
])

# ══════════════════════════════════════
# TAB 1 — PROFILE
# ══════════════════════════════════════
with tab_profile:
    st.markdown("### 👤 Your Profile / ملفك الشخصي")
    st.caption("Save your info once — used automatically in every health check")

    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.markdown("#### Personal Information")
        p_name  = st.text_input("Full Name / الاسم",
            value=st.session_state.user_name,
            placeholder="e.g. Ahmed Al-Shanfari", key="p_name")
        p_age   = st.number_input("Age / العمر", min_value=0, max_value=120,
            value=st.session_state.user_age, key="p_age")

        # Age category display
        if p_age <= 1:    st.caption("👶 Infant (0–1 year)")
        elif p_age <= 12: st.caption("🧒 Child (2–12 years)")
        elif p_age <= 17: st.caption("🧑 Teenager (13–17 years)")
        elif p_age <= 59: st.caption("👨 Adult (18–59 years)")
        else:             st.caption("👴 Elderly (60+ years) — Higher risk monitoring")

        p_gender= st.selectbox("Gender / الجنس",
            ["Not specified","Male","Female"],
            index=["Not specified","Male","Female"].index(st.session_state.gender),
            key="p_gender_sel")
        p_phone = st.text_input("Phone / الهاتف",
            value=st.session_state.user_phone,
            placeholder="+968 9X XXX XXXX", key="p_phone")
        p_city  = st.selectbox("City / المدينة",
            ["Salalah","Taqah","Mirbat","Rakhyut","Muscat","Sohar","Other"],
            key="p_city_sel")

        st.markdown("#### Medical Information")
        p_blood = st.selectbox("Blood Type / فصيلة الدم",
            ["Unknown","A+","A-","B+","B-","O+","O-","AB+","AB-"], key="p_blood_sel")
        p_conditions = st.multiselect("Existing Conditions / أمراض",
            ["Diabetes","High Blood Pressure","Asthma","Heart Disease",
             "Kidney Disease","Arthritis","Thyroid","Anaemia","None"],
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
                "saved_at":datetime.now().strftime("%Y-%m-%d %H:%M"),
                "name":p_name,"age":int(p_age),"gender":p_gender,
                "phone":p_phone,"city":p_city,"blood_type":p_blood,
                "conditions":p_conditions,"medications":p_meds,
                "allergies":p_allergy,"emergency_contact":p_emergency,
            }
            save_profile(profile)
            st.success("✅ Profile saved!")
            st.rerun()

    with col_p2:
        st.markdown("#### Your Profile Card")
        if st.session_state.user_name:
            age_v = st.session_state.user_age
            if age_v <= 1:    age_cat = "👶 Infant"
            elif age_v <= 12: age_cat = "🧒 Child"
            elif age_v <= 17: age_cat = "🧑 Teenager"
            elif age_v <= 59: age_cat = "👨 Adult"
            else:             age_cat = "👴 Elderly"
            conds = ", ".join(st.session_state.user_conditions) or "None"
            st.markdown(f"""
            <div class="profile-card">
                <div style="font-size:3rem">{g_emoji}</div>
                <div style="font-size:1.4rem;font-weight:700;margin:10px 0">
                    {st.session_state.user_name}</div>
                <div style="opacity:0.9">🎂 Age: {age_v} · {age_cat}</div>
                <div style="opacity:0.9">⚧ {st.session_state.gender}</div>
                <div style="opacity:0.9">📍 {st.session_state.user_city}</div>
                <div style="opacity:0.9">🩸 {st.session_state.user_blood_type}</div>
                <div style="margin-top:10px;background:rgba(255,255,255,0.2);
                    border-radius:8px;padding:8px;font-size:0.82rem">
                    Conditions: {conds}
                </div>
            </div>""", unsafe_allow_html=True)
        else:
            st.info("Fill your profile on the left → click Save")

        st.markdown("#### Saved Profiles")
        profiles = load_json(PROFILES_FILE)
        if profiles:
            st.dataframe(pd.DataFrame(profiles), use_container_width=True, height=220)
            st.download_button("📥 Download Profiles",
                pd.DataFrame(profiles).to_csv(index=False),
                "profiles.csv","text/csv",key="dl_prof")
        else:
            st.caption("No profiles saved yet")

# ══════════════════════════════════════
# TAB 2 — HEALTH CHECK
# ══════════════════════════════════════
with tab_assess:
    st.markdown("### 👤 Patient Details")
    a1,a2 = st.columns(2)
    with a1:
        name = st.text_input("Name / الاسم",
            value=st.session_state.user_name,
            placeholder="e.g. Ahmed Al-Shanfari", key="assess_name")
    with a2:
        age = st.number_input("Age / العمر", min_value=0, max_value=120,
            value=st.session_state.user_age, key="assess_age")
        # Age category
        if age <= 1:    st.caption("👶 Infant — special care guidelines apply")
        elif age <= 12: st.caption("🧒 Child")
        elif age <= 17: st.caption("🧑 Teenager")
        elif age <= 59: st.caption("👨 Adult")
        else:           st.caption("👴 Elderly — higher risk monitoring")

    st.markdown("---")

    # ── VOICE INPUT ──
    st.markdown("### 🎤 Voice Input / الإدخال الصوتي")
    st.caption("Click mic → speak symptoms → copy text to box below · Chrome only")
    components.html(f"""
    <div style="background:{T['l']};border:2px dashed {T['s']};
         border-radius:14px;padding:18px;text-align:center;">
        <button id="vBtn" onclick="go()" style="
            background:linear-gradient({T['g']});color:white;border:none;
            border-radius:50px;padding:12px 32px;font-size:1rem;
            font-weight:700;cursor:pointer;">
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
            document.getElementById('status').textContent='✅ Done! Copy text to box below.';
        }};
        rec.start();
    }}
    </script>
    """, height=195)

    st.markdown("---")

    # ── VITALS ──
    st.markdown("### 🩺 Vital Signs / العلامات الحيوية")
    know_vitals = st.toggle("I have my BP / Sugar / Temperature readings",
        value=False, key="know_vitals")

    if not know_vitals:
        st.info("No readings? No problem — get symptom-based advice below.")
        bp_systolic=120;bp_diastolic=80;blood_sugar=100;temperature=37.0
    else:
        st.markdown("#### Blood Pressure / ضغط الدم")
        bpc1,bpc2 = st.columns(2)
        with bpc1:
            st.markdown("**Upper Number (Systolic)**")
            st.caption("Normal: 90–120")
            bp_systolic = st.number_input("Systolic", min_value=60,
                max_value=240, value=120, key="bp_sys", label_visibility="collapsed")
            if bp_systolic>=180:   st.error("🔴 Crisis")
            elif bp_systolic<90:   st.error("🔴 Very LOW")
            elif bp_systolic>=140: st.warning("🟡 High")
            else:                   st.success("🟢 Normal")
        with bpc2:
            st.markdown("**Lower Number (Diastolic)**")
            st.caption("Normal: 60–80")
            bp_diastolic = st.number_input("Diastolic", min_value=40,
                max_value=140, value=80, key="bp_dia", label_visibility="collapsed")
            if bp_diastolic>=120:  st.error("🔴 Crisis")
            elif bp_diastolic<60:  st.error("🔴 Very LOW")
            elif bp_diastolic>=90: st.warning("🟡 High")
            else:                   st.success("🟢 Normal")
        st.markdown(f"**Combined: {bp_systolic}/{bp_diastolic} mmHg**")
        st.markdown("---")
        vc1,vc2 = st.columns(2)
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


    st.markdown("---")

    # ── FREE TEXT AI ANALYSIS ──
    st.markdown("### 💬 Describe Your Problem in Your Own Words")
    st.caption("Type anything — AI will analyze it directly. Works in English or Arabic.")

    free_text_input = st.text_area(
        "What is bothering you? / ما الذي يزعجك؟",
        placeholder=(
            "Example: I have had a headache for 2 days, feel dizzy and my neck is stiff...\n"
            "مثال: عندي صداع منذ يومين وأشعر بدوار وتصلب في الرقبة..."
        ),
        height=110,
        key="free_text_health"
    )

    ft_col1, ft_col2 = st.columns([1, 1])
    with ft_col1:
        analyze_en = st.button("🔍 Analyze in English",
            type="primary", use_container_width=True, key="ft_en")
    with ft_col2:
        analyze_ar = st.button("🔍 تحليل بالعربية",
            use_container_width=True, key="ft_ar")

    if (analyze_en or analyze_ar) and free_text_input.strip():
        lang = "ar" if analyze_ar else "en"
        with st.spinner("🤖 AI is analyzing your health concern..."):
            ft_result = analyze_free_text(free_text_input, language=lang)

        if ft_result["success"]:
            urgency = ft_result.get("urgency", "MEDIUM")
            urgency_config = {
                "HIGH":   ("🔴 HIGH — Seek help immediately", "#dc2626", "result-red"),
                "MEDIUM": ("🟡 MEDIUM — See a doctor soon",  "#d97706", "result-yellow"),
                "LOW":    ("🟢 LOW — Monitor at home",       "#16a34a", "result-green"),
            }
            u_label, u_color, u_css = urgency_config.get(urgency, urgency_config["MEDIUM"])

            st.markdown("---")
            st.markdown("### 🤖 AI Health Analysis")

            # Urgency banner
            st.markdown(f"""
            <div class="{u_css}" style="margin-bottom:16px;">
                <div style="font-size:1.5rem;font-weight:700;color:{u_color}">
                    Urgency Level: {u_label}
                </div>
            </div>""", unsafe_allow_html=True)

            # Results in columns
            r1, r2 = st.columns(2)

            with r1:
                if ft_result.get("symptoms"):
                    st.markdown("#### 🤒 Symptoms Identified")
                    for s in ft_result["symptoms"]:
                        st.markdown(f'<div class="step-red">• {s}</div>',
                            unsafe_allow_html=True)

                if ft_result.get("explanation"):
                    st.markdown("#### 💡 Why This Might Be Happening")
                    st.info(ft_result["explanation"])

            with r2:
                if ft_result.get("causes"):
                    st.markdown("#### 🔬 Possible Causes")
                    for c in ft_result["causes"]:
                        st.markdown(f'<div class="step">• {c}</div>',
                            unsafe_allow_html=True)

                if ft_result.get("next_steps"):
                    st.markdown("#### ✅ What To Do Next")
                    for step in ft_result["next_steps"]:
                        st.markdown(f'<div class="step">• {step}</div>',
                            unsafe_allow_html=True)

            # Hospital info if HIGH urgency
            if urgency == "HIGH":
                st.error(
                    "🚨 **Please go to Sultan Qaboos Hospital Salalah NOW**\n\n"
                    "📍 Al Dahariz, Salalah · 📞 Emergency: **999** · +968 23 218 000"
                )
                st.link_button("📍 Open in Google Maps",
                    "https://maps.google.com/?q=Sultan+Qaboos+Hospital+Salalah+Oman")

            st.markdown("""<div class="disclaimer">
                ⚠️ This AI analysis is for general guidance only.
                It does NOT replace a qualified doctor's diagnosis.
                Always consult a licensed medical professional.
            </div>""", unsafe_allow_html=True)

        else:
            st.error(f"AI analysis failed: {ft_result.get('error', 'Unknown error')}")

    elif (analyze_en or analyze_ar) and not free_text_input.strip():
        st.warning("Please describe your health concern before clicking Analyze.")

    st.markdown("---")
    st.markdown("### — OR use the structured form below —")
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

    extra = st.text_area("Other symptoms / أعراض أخرى (or paste voice text):",
        placeholder="e.g. back pain... أو ألم في الظهر", height=65, key="extra")
    if extra.strip():
        extras=[s.strip() for s in extra.replace(",","\n").splitlines() if s.strip()]
        selected_symptoms.extend(normalize_symptoms(extras))
        selected_symptoms = list(set(selected_symptoms))

    if selected_symptoms:
        st.info(f"Selected: {', '.join(selected_symptoms)}")
    if "chest_pain" in selected_symptoms or "breathlessness" in selected_symptoms:
        st.error("🚨 SERIOUS SYMPTOMS — Go to Emergency tab or call 999 now!")

    # Infant warning
    if age <= 1:
        st.error("👶 INFANT PATIENT — Any fever above 38°C in infants under 3 months "
                 "is a medical emergency. Go to hospital immediately.")
    elif age <= 12:
        st.warning("🧒 CHILD PATIENT — Dosing and normal ranges differ from adults. "
                  "Always consult a paediatrician.")

    st.markdown("""<div class="disclaimer">
        ⚠️ Health guide only. NOT a doctor. Emergency: <strong>999</strong>
    </div>""", unsafe_allow_html=True)
    st.markdown("")

    if st.button("🔍 Assess My Health / تقييم صحتي",
            type="primary", use_container_width=True, key="assess_btn"):
        err = validate_patient_input(
            name if name else "Patient", max(int(age),1),
            int(bp_systolic), int(bp_diastolic),
            float(blood_sugar), float(temperature))
        if err:
            st.error(err)
        else:
            patient = Patient(
                name=name.strip() if name else "Patient",
                age=max(int(age),1),
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
                "name":        patient.name, "age": patient.age,
                "gender":      st.session_state.gender,
                "city":        st.session_state.user_city,
                "phone":       st.session_state.user_phone,
                "blood_type":  st.session_state.user_blood_type,
                "conditions":  ", ".join(st.session_state.user_conditions) or "None",
                "bp":          f"{bp_systolic}/{bp_diastolic}" if know_vitals else "Not measured",
                "blood_sugar": blood_sugar if know_vitals else "Not measured",
                "temperature": temperature if know_vitals else "Not measured",
                "symptoms":    ", ".join(selected_symptoms) or "None",
                "triage_level":result["level"],
                "findings":    " | ".join(result["reasons"])[:300],
                "ai_used":     bool(ai_result and ai_result.get("success")),
            }
            save_record(record)
            log_patient(patient, result)

            st.markdown("---")
            st.markdown(f"## Results for **{patient.name}**")
            level = result["level"]
            css_map={"GREEN":"result-green","YELLOW":"result-yellow","RED":"result-red"}
            lmap={
                "GREEN":  ("🟢 ALL CLEAR",             "بصحة جيدة",          "#16a34a"),
                "YELLOW": ("🟡 ATTENTION NEEDED",       "يحتاج انتباهاً",     "#d97706"),
                "RED":    ("🔴 URGENT — SEEK HELP NOW","عاجل — اطلب المساعدة","#dc2626"),
            }
            le,la,col = lmap[level]
            st.markdown(f"""<div class="{css_map[level]}">
                <div style="font-size:1.8rem;font-weight:700;color:{col}">{le}</div>
                <div style="font-family:'Tajawal',sans-serif;font-size:1.1rem;
                     color:{col};opacity:0.8;direction:rtl">{la}</div>
            </div>""", unsafe_allow_html=True)

            if know_vitals:
                m1,m2,m3,m4=st.columns(4)
                m1.metric("🩺 BP",   f"{bp_systolic}/{bp_diastolic}")
                m2.metric("🩸 Sugar",f"{int(blood_sugar)} mg/dL")
                m3.metric("🌡️ Temp", f"{temperature:.1f}°C")
                m4.metric("👤 Age",  f"{int(age)} yrs")

            st.markdown("### 🔍 Findings")
            for r in result["reasons"]: st.markdown(f"- {r}")

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

            if level=="RED":
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
    st.error("🔴 Life in danger? **CALL 999 FIRST** then follow steps below")
    h1,h2,h3=st.columns(3)
    with h1: st.error("**🚑 Emergency**\n📞 **999**\n🕐 24/7")
    with h2: st.info("**🏥 Sultan Qaboos**\n📞 +968 23 218 000\n📍 Al Dahariz, Salalah")
    with h3: st.info("**🏥 Salalah Private**\n📞 +968 23 295 999\n📍 Salalah")
    st.link_button("📍 Open Sultan Qaboos in Maps",
        "https://maps.google.com/?q=Sultan+Qaboos+Hospital+Salalah+Oman")
    st.markdown("---")

    et1,et2,et3,et4,et5,et6=st.tabs([
        "❤️ Heart Attack","💓 CPR","😮‍💨 Choking","😵 Fainting","🌡️ Heat Stroke","👶 Infant Emergency"])

    with et1:
        e1,e2=st.columns(2)
        with e1:
            st.markdown("### Signs")
            for s in ["💔 Chest pain or pressure","😮‍💨 Shortness of breath",
                "💪 Pain in left arm or jaw","😰 Cold sweat","🤢 Nausea","😵 Dizziness"]:
                st.markdown(f'<div class="step-red">{s}</div>',unsafe_allow_html=True)
        with e2:
            st.markdown("### Steps")
            for i,s in enumerate(["📞 Call 999","🪑 Sit patient — do NOT walk",
                "👗 Loosen tight clothing","💊 Aspirin 300mg if available",
                "🧍 Stay — never leave alone","🚫 No food or water"],1):
                st.markdown(f'<div class="step-red"><b>{i}.</b> {s}</div>',unsafe_allow_html=True)

    with et2:
        st.error("Only if person is **unconscious and NOT breathing**")
        c1,c2=st.columns(2)
        with c1:
            for i,s in enumerate(["Check response","Call 999","Lay flat on hard surface",
                "Heel of hand on CENTRE of chest","Push DOWN 5–6cm hard and fast",
                "30 compressions at 100–120/min","Tilt head, give 2 breaths",
                "Repeat until help arrives"],1):
                st.markdown(f'<div class="step-red"><b>{i}.</b> {s}</div>',unsafe_allow_html=True)
        with c2:
            st.warning("🎵 Push to beat of 'Stayin Alive' = 100 bpm\n\n"
                "💪 Press HARD — 5cm deep\n\n🚑 Don't stop until paramedics arrive")

    with et3:
        ch1,ch2=st.columns(2)
        with ch1:
            st.markdown("### Adult")
            for i,s in enumerate(["Ask: Can you speak?","Tell to cough hard",
                "5 back blows between shoulders","5 abdominal thrusts (Heimlich)",
                "Alternate until clear","Call 999 if unconscious"],1):
                st.markdown(f'<div class="step"><b>{i}.</b> {s}</div>',unsafe_allow_html=True)
        with ch2:
            st.info("**Heimlich:** Stand behind, fist above belly button, sharp inward+upward thrusts")
            st.markdown("### Child (1–8 years)")
            for s in ["5 back blows","5 chest thrusts (lighter pressure)","Check mouth","Repeat","Call 999"]:
                st.markdown(f'<div class="step">{s}</div>',unsafe_allow_html=True)

    with et4:
        f1,f2=st.columns(2)
        with f1:
            for i,s in enumerate(["Lay flat","Raise legs above heart level",
                "Loosen clothing","Check breathing","Turn on side if vomiting",
                "No water while unconscious","Call 999 if not waking in 1 min"],1):
                st.markdown(f'<div class="step"><b>{i}.</b> {s}</div>',unsafe_allow_html=True)
        with f2:
            st.success("**Prevention:**\n- Drink water\n- Rise slowly\n- Eat regularly\n- Sit if feeling faint")

    with et5:
        st.error("Heat stroke is a MEDICAL EMERGENCY — call 999")
        hs1,hs2=st.columns(2)
        with hs1:
            for s in ["🌡️ Temp above 40°C","🧠 Confusion","🚫 Hot dry skin","🤢 Nausea"]:
                st.markdown(f'<div class="step-red">{s}</div>',unsafe_allow_html=True)
        with hs2:
            for i,s in enumerate(["Call 999","Move to cool shade",
                "Remove excess clothing","Wet cloths on neck+armpits","Fan continuously",
                "Cool water if conscious","Do NOT give aspirin"],1):
                st.markdown(f'<div class="step"><b>{i}.</b> {s}</div>',unsafe_allow_html=True)

    with et6:
        st.error("👶 Infant emergencies — always call 999 immediately")
        inf1,inf2=st.columns(2)
        with inf1:
            st.markdown("### 🌡️ Infant Fever — When to Rush to Hospital")
            for s in [
                "🚨 Any fever in baby UNDER 3 MONTHS — go immediately",
                "🚨 Fever above 39°C in baby 3–6 months",
                "🚨 Fever above 40°C in any infant",
                "🚨 Infant not feeding for more than 8 hours",
                "🚨 Infant very difficult to wake up",
                "🚨 Rash appearing with fever",
                "🚨 Difficulty breathing or fast breathing",
                "🚨 Crying non-stop for more than 2 hours",
            ]:
                st.markdown(f'<div class="step-red">{s}</div>',unsafe_allow_html=True)
        with inf2:
            st.markdown("### 😮‍💨 Infant Choking")
            for i,s in enumerate([
                "Hold face-DOWN on your forearm, head lower than chest",
                "Give 5 firm back blows with heel of hand",
                "Turn face-UP carefully",
                "Give 5 chest thrusts with 2 fingers on breastbone",
                "Check mouth — remove ONLY visible objects",
                "Repeat back blows and chest thrusts",
                "Call 999 — do NOT do abdominal thrusts on infants",
            ],1):
                st.markdown(f'<div class="step-red"><b>{i}.</b> {s}</div>',unsafe_allow_html=True)

            st.markdown("### 💊 Safe Fever Medicine for Infants")
            st.info("""
**Paracetamol drops (Panadol infant):**
- Under 3 months: DO NOT give — go to hospital
- 3–6 months: 2.5ml (60mg) — only if advised by doctor
- 6–24 months: 2.5–5ml every 4–6 hours
- NEVER give aspirin to infants or children

**Always check weight-based dosing on the bottle**
            """)

# ══════════════════════════════════════
# TAB 4 — MEDICINE GUIDE
# ══════════════════════════════════════
with tab_medicine:
    st.markdown("### 💊 Medicine Information Guide")
    st.markdown("""<div class="disclaimer">
        ⚠️ General info only. Always follow your doctor's prescription.</div>""",
        unsafe_allow_html=True)
    st.markdown("")

    med_cat = st.selectbox("Category:", [
        "Common Medicines", "Children & Infant Medicines", "Elderly Medicines"], key="med_cat")

    if med_cat == "Common Medicines":
        medicines = {
            "Paracetamol (Panadol)":{"e":"💊","for":"Fever, headache, mild pain",
                "dose":"500–1000mg every 4–6 hrs. Max 4g/day.",
                "warn":"Do not exceed 4g/day. Avoid alcohol.",
                "avoid":"Liver disease","tip":"Safest painkiller for all ages"},
            "Ibuprofen (Brufen)":{"e":"💊","for":"Pain, inflammation, fever",
                "dose":"200–400mg every 6–8 hrs WITH food.",
                "warn":"Take with food. Can cause stomach bleeding.",
                "avoid":"Kidney problems, ulcers, pregnancy","tip":"Always eat before taking"},
            "Metformin":{"e":"🔵","for":"Type 2 diabetes",
                "dose":"500–1000mg twice daily with meals.",
                "warn":"Take with food. Stay hydrated.",
                "avoid":"Kidney disease","tip":"Never stop without doctor advice"},
            "Amlodipine":{"e":"❤️","for":"High blood pressure, chest pain",
                "dose":"5–10mg once daily.",
                "warn":"May cause ankle swelling.",
                "avoid":"Severe low BP","tip":"Take at same time each day"},
            "Omeprazole":{"e":"🟡","for":"Heartburn, stomach acid, ulcers",
                "dose":"20mg once daily 30 min before eating.",
                "warn":"Long-term use may reduce magnesium.",
                "avoid":"Long-term without review","tip":"Take before breakfast"},
            "Salbutamol (Ventolin)":{"e":"💨","for":"Asthma, wheezing",
                "dose":"1–2 puffs when needed. Max 4x/day.",
                "warn":"See doctor if using more than 3x/week.",
                "avoid":"Heart rhythm problems","tip":"Always carry in Khareef season"},
        }
    elif med_cat == "Children & Infant Medicines":
        medicines = {
            "Paracetamol Infant Drops":{"e":"👶","for":"Fever and pain in infants",
                "dose":"Based on WEIGHT not age. Usually 15mg/kg every 4–6 hrs. Check bottle.",
                "warn":"Under 3 months — only with doctor advice.",
                "avoid":"Liver problems. Never exceed recommended dose.",
                "tip":"Use the syringe provided — never guess the dose"},
            "Ibuprofen Syrup (Child)":{"e":"🧒","for":"Fever, pain, teething pain",
                "dose":"5–10mg/kg every 6–8 hrs. Only for children over 6 months.",
                "warn":"Do NOT give to infants under 6 months.",
                "avoid":"Under 6 months, kidney problems, dehydration",
                "tip":"Give with food or milk to protect stomach"},
            "ORS (Oral Rehydration Salts)":{"e":"💧","for":"Diarrhoea, vomiting, dehydration in children",
                "dose":"Small sips frequently. 1 sachet in 1 litre clean water.",
                "warn":"Make fresh every 24 hours. Do not add sugar.",
                "avoid":"Nothing — safe for all ages",
                "tip":"Best treatment for child diarrhoea — better than plain water"},
            "Zinc Syrup":{"e":"🟢","for":"Supports recovery from diarrhoea in children",
                "dose":"Under 6 months: 10mg/day. Over 6 months: 20mg/day for 10–14 days.",
                "warn":"Do not exceed recommended dose.",
                "avoid":"Hypersensitivity to zinc",
                "tip":"Give alongside ORS for best results"},
            "Antihistamine Syrup":{"e":"🟣","for":"Allergies, rash, runny nose in children",
                "dose":"As per bottle. Usually once or twice daily.",
                "warn":"May cause drowsiness. Do not drive.",
                "avoid":"Under 2 years — consult doctor first",
                "tip":"Give at bedtime — drowsiness can be helpful"},
        }
    else:  # Elderly
        medicines = {
            "Aspirin 75mg":{"e":"🔴","for":"Prevents heart attack and stroke",
                "dose":"75mg once daily with food.",
                "warn":"Can cause stomach bleeding.",
                "avoid":"Stomach ulcers, bleeding disorders","tip":"Do not stop without doctor"},
            "Atorvastatin":{"e":"🟠","for":"High cholesterol, heart disease",
                "dose":"10–80mg once daily at night.",
                "warn":"Report muscle pain immediately.",
                "avoid":"Liver disease, pregnancy","tip":"Take at night for best effect"},
            "Warfarin":{"e":"🩸","for":"Blood thinner — prevents clots, stroke",
                "dose":"Strictly as prescribed. Dose varies per person.",
                "warn":"MANY drug and food interactions. Do NOT change dose.",
                "avoid":"Bleeding disorders, pregnancy",
                "tip":"Avoid green leafy vegetables in large amounts — they affect warfarin"},
            "Bisoprolol":{"e":"💙","for":"Heart failure, high blood pressure, irregular heartbeat",
                "dose":"As prescribed. Usually 1.25–10mg once daily.",
                "warn":"Do NOT stop suddenly — can cause heart problems.",
                "avoid":"Severe asthma, certain heart conditions",
                "tip":"Always carry a list of your heart medicines"},
            "Calcium + Vitamin D":{"e":"🦴","for":"Bone strength, osteoporosis prevention",
                "dose":"500–1000mg calcium + 400–800 IU Vitamin D daily.",
                "warn":"Take with food. Space doses if taking iron.",
                "avoid":"High calcium levels, kidney stones",
                "tip":"Essential for elderly to prevent falls and fractures"},
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
# TAB 5 — WOMEN'S HEALTH
# ══════════════════════════════════════
with tab_women:
    st.markdown("""
    <div style="background:linear-gradient(135deg,#500724,#9d174d,#db2777);
         border-radius:16px;padding:20px 28px;color:white;text-align:center;margin-bottom:20px;">
        <div style="font-size:2rem">👩</div>
        <div style="font-size:1.4rem;font-weight:700">Women's Health Guide</div>
        <div style="opacity:0.85">دليل صحة المرأة</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("""<div class="disclaimer">
        ⚠️ This is general health information only. Always consult your doctor or gynaecologist.
    </div>""", unsafe_allow_html=True)
    st.markdown("")

    wt1,wt2,wt3,wt4 = st.tabs([
        "🤰 Pregnancy","🩸 Period Care","💊 Women's Medicines","⚠️ When to Seek Help"])

    with wt1:
        st.markdown("## 🤰 Pregnancy Care / رعاية الحمل")
        pr1,pr2 = st.columns(2)
        with pr1:
            st.markdown("### By Trimester / حسب الثلث")
            st.markdown("""
            <div class="women-card">
                <strong>🌱 First Trimester (Weeks 1–12)</strong><br><br>
                ✅ Start folic acid 400mcg daily — prevents birth defects<br>
                ✅ Attend first antenatal appointment<br>
                ✅ Avoid alcohol, smoking, raw fish<br>
                ✅ Normal to feel nausea — eat small frequent meals<br>
                ⚠️ Report heavy bleeding immediately<br>
                💊 Safe: Paracetamol for pain. Avoid ibuprofen.
            </div>""", unsafe_allow_html=True)

            st.markdown("""
            <div class="women-card">
                <strong>🌿 Second Trimester (Weeks 13–26)</strong><br><br>
                ✅ Anomaly scan around week 20<br>
                ✅ Start iron supplements if low<br>
                ✅ Gentle exercise — walking is excellent<br>
                ✅ Sleep on LEFT side — better blood flow to baby<br>
                ⚠️ Report reduced baby movement<br>
                ⚠️ Report severe headache or vision changes
            </div>""", unsafe_allow_html=True)

            st.markdown("""
            <div class="women-card">
                <strong>🌺 Third Trimester (Weeks 27–40)</strong><br><br>
                ✅ Attend all antenatal checks<br>
                ✅ Prepare hospital bag by week 36<br>
                ✅ Count baby movements daily<br>
                ✅ Learn signs of labour<br>
                🚨 Go to hospital: contractions every 5 min<br>
                🚨 Go to hospital: waters breaking<br>
                🚨 Go to hospital: heavy bleeding
            </div>""", unsafe_allow_html=True)

        with pr2:
            st.markdown("### 🚨 Pregnancy Warning Signs")
            st.error("**Go to hospital immediately if:**")
            for s in [
                "🩸 Heavy vaginal bleeding",
                "💧 Sudden gush of fluid (waters breaking early)",
                "🤕 Severe headache that won't go away",
                "👁️ Blurred or double vision",
                "🤢 Severe vomiting — cannot keep any food down",
                "🦵 Severe swelling of face, hands, or feet",
                "👶 Baby not moving for more than 2 hours",
                "🌡️ Fever above 38°C",
                "😣 Severe abdominal pain",
                "🫀 Heart racing or chest pain",
            ]:
                st.markdown(f'<div class="step-red">{s}</div>',unsafe_allow_html=True)

            st.markdown("### ✅ Safe Foods in Pregnancy")
            st.success("""
- 🥦 All cooked vegetables
- 🍌 All fruits (washed well)
- 🥩 Well-cooked meat and chicken
- 🐟 Cooked fish (avoid tuna, shark)
- 🥛 Pasteurised dairy products
- 🌾 Whole grains, lentils, beans
            """)

            st.markdown("### 🚫 Avoid in Pregnancy")
            st.error("""
- 🐟 Raw fish (sushi, sashimi)
- 🧀 Soft unpasteurised cheese
- 🥚 Raw or undercooked eggs
- 🍷 Alcohol — any amount
- ☕ Limit caffeine to 1 cup/day
- 💊 Ibuprofen, aspirin (unless prescribed)
- 🚬 Smoking
            """)

            st.markdown("### 💊 Safe Medicines in Pregnancy")
            st.info("""
**SAFE (with doctor advice):**
- ✅ Paracetamol — pain and fever
- ✅ Folic acid — essential first 12 weeks
- ✅ Iron supplements — if anaemic
- ✅ Vitamin D — bone health
- ✅ ORS — for dehydration

**AVOID:**
- 🚫 Ibuprofen (especially 3rd trimester)
- 🚫 Aspirin (unless prescribed)
- 🚫 Most antibiotics without prescription
- 🚫 Any new medicine without asking doctor
            """)

    with wt2:
        st.markdown("## 🩸 Period Care / رعاية الدورة الشهرية")
        pc1,pc2 = st.columns(2)
        with pc1:
            st.markdown("### Managing Period Pain")
            for tip in [
                "💊 Ibuprofen 400mg with food — best for cramps (start 1 day before if possible)",
                "💊 Paracetamol 500–1000mg — if ibuprofen not suitable",
                "🌡️ Heat pad or hot water bottle on lower abdomen — very effective",
                "🧘 Gentle yoga or stretching reduces cramping",
                "💧 Drink warm water and herbal teas — ginger tea especially helpful",
                "🚶 Light walking improves blood flow and reduces pain",
                "🛁 Warm bath helps relax muscles",
                "🚫 Avoid caffeine and salty foods — they worsen bloating",
            ]:
                st.markdown(f'<div class="step-pink">{tip}</div>',unsafe_allow_html=True)

            st.markdown("### Nutrition During Period")
            st.success("""
**Eat more:**
- 🥬 Iron-rich foods: spinach, red meat, lentils (replenish blood loss)
- 🍌 Bananas — magnesium helps with cramps
- 🐟 Omega-3 fish: salmon, sardines — anti-inflammatory
- 🫐 Berries — antioxidants reduce inflammation
- 🌰 Dark chocolate (70%+) — magnesium

**Avoid:**
- ☕ Caffeine — worsens cramps and bloating
- 🧂 Salty foods — increase bloating
- 🍬 Excess sugar — causes energy crashes
            """)

        with pc2:
            st.markdown("### 🚨 When to See a Doctor")
            st.error("**See a doctor if:**")
            for s in [
                "Period pain is so severe it stops daily activities",
                "Bleeding so heavy you soak more than 1 pad per hour",
                "Periods lasting more than 7 days",
                "No period for 3+ months (and not pregnant)",
                "Periods suddenly becoming very irregular",
                "Bleeding between periods",
                "Severe bloating or pelvic pain outside of period",
                "Fever with period pain",
            ]:
                st.markdown(f'<div class="step-red">{s}</div>',unsafe_allow_html=True)

            st.markdown("### 📅 Normal vs Abnormal")
            st.info("""
**Normal period:**
- 21–35 day cycle
- Lasts 3–7 days
- Mild to moderate cramping
- Some clots are normal

**Not normal — see doctor:**
- Cycle shorter than 21 or longer than 35 days
- Flooding or soaking through every hour
- Clots larger than a 50 baisa coin
- Severe pain needing bed rest
- Pain during sex
            """)

    with wt3:
        st.markdown("## 💊 Women's Medicines Guide")
        st.markdown("""<div class="disclaimer">
            ⚠️ Always consult a doctor before starting any medication.</div>""",
            unsafe_allow_html=True)
        st.markdown("")

        womens_meds = {
            "Folic Acid": {
                "for":"Pregnancy — prevents neural tube defects in baby",
                "dose":"400mcg daily — start BEFORE pregnancy if planning. Continue through first 12 weeks.",
                "warn":"Safe and important. Do not skip.",
                "avoid":"No major contraindications",
                "tip":"Every woman who could become pregnant should take folic acid",
            },
            "Iron Supplements": {
                "for":"Anaemia, pregnancy, heavy periods",
                "dose":"As prescribed. Usually 200mg ferrous sulphate once or twice daily.",
                "warn":"Take on empty stomach for best absorption — but with food if nausea occurs.",
                "avoid":"Haemochromatosis (iron overload condition)",
                "tip":"Take with orange juice — vitamin C helps iron absorption. Causes dark stools — normal.",
            },
            "Calcium + Vitamin D": {
                "for":"Bone health, pregnancy, breastfeeding, menopause",
                "dose":"1000mg calcium + 600–800 IU Vitamin D daily.",
                "warn":"Space doses throughout day. Do not take with iron.",
                "avoid":"High calcium levels",
                "tip":"Essential during pregnancy and after menopause",
            },
            "Oral Contraceptive Pill": {
                "for":"Contraception, period regulation, period pain reduction",
                "dose":"Take at SAME TIME every day. As prescribed by doctor.",
                "warn":"Take at same time daily. Does not protect against STIs.",
                "avoid":"History of blood clots, certain migraines, smokers over 35",
                "tip":"If you miss a pill, take it as soon as you remember",
            },
            "Metronidazole": {
                "for":"Bacterial vaginal infections, certain STIs",
                "dose":"As prescribed. Usually 400–500mg twice daily for 5–7 days.",
                "warn":"Do NOT drink alcohol during treatment or 48 hours after.",
                "avoid":"First trimester of pregnancy (unless essential)",
                "tip":"Complete the full course even if symptoms improve",
            },
            "Mefenamic Acid (Ponstan)": {
                "for":"Period pain, menstrual cramps",
                "dose":"500mg three times daily with food. Start at first sign of period.",
                "warn":"Take with food. Not for long-term use.",
                "avoid":"Stomach ulcers, kidney problems, pregnancy (3rd trimester)",
                "tip":"Most effective if started 1 day before period begins",
            },
        }

        sel_w = st.selectbox("Select:", list(womens_meds.keys()), key="w_med_sel")
        if sel_w:
            m = womens_meds[sel_w]
            st.markdown(f"### 💊 {sel_w}")
            st.info(f"💡 {m['tip']}")
            wm1,wm2 = st.columns(2)
            with wm1:
                st.success(f"**✅ Used for:**\n{m['for']}")
                st.info(f"**💊 Dose:**\n{m['dose']}")
            with wm2:
                st.warning(f"**⚠️ Warning:**\n{m['warn']}")
                st.error(f"**🚫 Avoid if:**\n{m['avoid']}")

    with wt4:
        st.markdown("## ⚠️ When Women Should Seek Urgent Help")
        st.error("**Call 999 or go to hospital immediately:**")
        urgent = [
            "🩸 Heavy vaginal bleeding — soaking more than 1 pad per hour",
            "🤰 Any pregnancy complication — bleeding, severe pain, no fetal movement",
            "🫀 Chest pain or difficulty breathing",
            "🤕 Severe sudden headache (worst of your life)",
            "👁️ Sudden vision changes or loss",
            "😵 Confusion or loss of consciousness",
            "🌡️ High fever with pelvic pain",
            "😣 Severe abdominal pain",
        ]
        for s in urgent:
            st.markdown(f'<div class="step-red">{s}</div>',unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### See Doctor Soon (Within 1–2 Days):")
        soon = [
            "Period pain that stops you doing normal activities",
            "Unusual vaginal discharge or odour",
            "Burning or pain when urinating",
            "Lump in breast or breast changes",
            "Missed period (not pregnant)",
            "Excessive hair loss or unwanted hair growth",
            "Severe mood swings or depression around period",
        ]
        for s in soon:
            st.markdown(f'<div class="step-pink">{s}</div>',unsafe_allow_html=True)

        st.markdown("---")
        st.info("""
**Important contacts for Salalah women:**

🏥 **Sultan Qaboos Hospital Salalah** — Maternity & Gynaecology
📞 +968 23 218 000 · 📍 Al Dahariz, Salalah

🚑 **Emergency:** 999

💚 **Your health matters. Never delay seeking help.**
        """)


# ══════════════════════════════════════
# TAB 6 — DISEASE ENCYCLOPEDIA
# ══════════════════════════════════════
with tab_diseases:
    st.markdown("""
    <div style="background:linear-gradient(135deg,#1e3a5f,#2d6fba);border-radius:16px;
         padding:20px 28px;color:white;text-align:center;margin-bottom:20px;">
        <div style="font-size:2rem">🦠</div>
        <div style="font-size:1.4rem;font-weight:700">Disease Encyclopedia</div>
        <div style="opacity:0.85">موسوعة الأمراض</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("""<div class="disclaimer">
        ⚠️ This is general health education only. Always consult a qualified doctor
        for diagnosis and treatment.</div>""", unsafe_allow_html=True)
    st.markdown("")

    # Search and filter
    d_col1, d_col2 = st.columns([2, 1])
    with d_col1:
        search_q = st.text_input("🔍 Search disease (English or Arabic):",
            placeholder="e.g. diabetes, السكري, COVID...", key="dis_search")
    with d_col2:
        cat_filter = st.selectbox("Filter by category:",
            ["All Categories"] + CATEGORIES, key="dis_cat")

    # Get filtered diseases
    if search_q.strip():
        filtered = search_diseases(search_q)
    elif cat_filter != "All Categories":
        filtered = get_by_category(cat_filter)
    else:
        filtered = DISEASES

    if not filtered:
        st.warning("No diseases found. Try a different search term.")
    else:
        # Show disease count
        st.caption(f"Showing {len(filtered)} disease(s)")

        # Disease selector
        disease_names = list(filtered.keys())
        selected_disease = st.selectbox(
            "Select a disease to view full information:",
            disease_names,
            format_func=lambda x: f"{filtered[x]['emoji']} {x}  —  {filtered[x]['category']}",
            key="dis_select"
        )

        if selected_disease:
            d = filtered[selected_disease]
            st.markdown("---")

            # Disease header
            contagious_badge = "🔴 Contagious" if d["is_contagious"] else "✅ Not contagious"
            genetic_badge    = "🧬 Has genetic component" if d["is_genetic"] else "❌ Not genetic"
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,{T['l']},white);
                 border-radius:16px;padding:24px;border:2px solid {T['p']}33;margin-bottom:16px;">
                <div style="display:flex;align-items:center;gap:16px;flex-wrap:wrap;">
                    <div style="font-size:3.5rem;line-height:1">{d['emoji']}</div>
                    <div style="flex:1;">
                        <div style="font-size:1.6rem;font-weight:700;color:{T['p']}">{selected_disease}</div>
                        <div style="font-size:0.9rem;color:#6b7280;margin-top:4px">
                            Also known as: {d['also_known_as']}</div>
                        <div style="font-family:'Tajawal',sans-serif;font-size:1rem;
                             color:{T['s']};margin-top:4px">{d['arabic_name']}</div>
                    </div>
                    <div style="display:flex;flex-direction:column;gap:6px;text-align:right;">
                        <span style="background:{'#fee2e2' if d['is_contagious'] else '#dcfce7'};
                            color:{'#dc2626' if d['is_contagious'] else '#16a34a'};
                            padding:4px 12px;border-radius:99px;font-size:0.82rem;font-weight:600">
                            {contagious_badge}</span>
                        <span style="background:{'#ede9fe' if d['is_genetic'] else '#f3f4f6'};
                            color:{'#7c3aed' if d['is_genetic'] else '#6b7280'};
                            padding:4px 12px;border-radius:99px;font-size:0.82rem;font-weight:600">
                            {genetic_badge}</span>
                        <span style="background:{T['l']};color:{T['p']};
                            padding:4px 12px;border-radius:99px;font-size:0.82rem;font-weight:600">
                            📂 {d['category']}</span>
                    </div>
                </div>
                <div style="margin-top:14px;font-size:0.95rem;color:#374151;line-height:1.7">
                    {d['overview']}</div>
            </div>""", unsafe_allow_html=True)

            # Recovery time
            st.info(f"⏱️ **Recovery Time:** {d['recovery_time']}")

            # Khareef connection
            if d.get("khareef_connection"):
                st.warning(f"🌦️ **Khareef Season Note:** {d['khareef_connection']}")

            st.markdown("---")

            # Main info in tabs
            dt1, dt2, dt3, dt4, dt5, dt6 = st.tabs([
                "🔬 How It Occurs",
                "🤒 Symptoms",
                "⚠️ High Risk Groups",
                "🛡️ Prevention",
                "💊 Treatment",
                "🚨 When to Seek Help",
            ])

            with dt1:
                st.markdown(f"### 🔬 How Does It Occur?")
                st.info(f"**Type:** {d['how_it_occurs']}")
                for item in d["transmission"]:
                    st.markdown(f'<div class="step">{item}</div>', unsafe_allow_html=True)

            with dt2:
                st.markdown("### 🤒 Symptoms / الأعراض")
                for s in d["symptoms"]:
                    color = "step-red" if "🔴" in s or "Severe" in s else "step"
                    st.markdown(f'<div class="{color}">{s}</div>', unsafe_allow_html=True)

            with dt3:
                st.markdown("### ⚠️ Who Is Most at Risk?")
                for g in d["high_risk_groups"]:
                    st.markdown(f'<div class="step-red">{g}</div>', unsafe_allow_html=True)

            with dt4:
                st.markdown("### 🛡️ Prevention / الوقاية")
                for p in d["prevention"]:
                    st.markdown(f'<div class="step">{p}</div>', unsafe_allow_html=True)

            with dt5:
                st.markdown("### 💊 Treatment / العلاج")
                for t in d["treatment"]:
                    st.markdown(f'<div class="step">{t}</div>', unsafe_allow_html=True)

            with dt6:
                st.markdown("### 🚨 When to Seek Medical Help")
                st.error("**Go to hospital or call 999 if you experience:**")
                for w in d["when_to_seek_help"]:
                    st.markdown(f'<div class="step-red">⚠️ {w}</div>', unsafe_allow_html=True)
                st.markdown("")
                st.info("Sultan Qaboos Hospital Salalah — Emergency: 999 — +968 23 218 000")
                st.link_button("📍 Open in Google Maps",
                    "https://maps.google.com/?q=Sultan+Qaboos+Hospital+Salalah+Oman")

# ══════════════════════════════════════
# TAB 8 — ABOUT
# ══════════════════════════════════════
with tab_about:
    ab1,ab2=st.columns(2)
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
Free AI medical triage for **Salalah, Dhofar, Oman**.
Instant advice in **English and Arabic**.
Named after Salalah's **Khareef** monsoon season.

**Features:**
- 🎤 Voice input · 🤖 Gemini AI
- 👶 Infant & teenager care
- 👩 Women's health & pregnancy
- 🚨 Emergency first aid
- 💊 Medicine guide
- 📊 History tracking
        """)
    st.markdown("---")
    ec1,ec2,ec3=st.columns(3)
    with ec1: st.error("**Emergency**\n📞 999")
    with ec2: st.info("**Sultan Qaboos**\n📞 +968 23 218 000")
    with ec3: st.info("**Salalah Private**\n📞 +968 23 295 999")
    st.markdown("---")
    st.markdown("""<div class="disclaimer">
        ⚠️ For educational purposes only. NOT a substitute for professional medical advice.
        Always consult a licensed doctor. Emergency: <strong>999</strong>
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════
# HIDDEN ADMIN PANEL
# Only visible at: your-app-url/?admin=true
# Then enter password to unlock
# ══════════════════════════════════════

# Check for secret admin URL parameter
query_params = st.query_params
is_admin_url  = query_params.get("admin", "") == "true"

if is_admin_url:
    st.markdown("---")
    st.markdown("""
    <div style="background:linear-gradient(135deg,#0d3d29,#1a5c45);border-radius:16px;
         padding:20px 28px;color:white;text-align:center;margin-bottom:20px;">
        <div style="font-size:2rem">🔐</div>
        <div style="font-size:1.3rem;font-weight:700">Admin Dashboard</div>
        <div style="opacity:0.75;font-size:0.85rem">Private — Sadga Selime only</div>
    </div>""", unsafe_allow_html=True)

    # ── PASSWORD CHECK ──
    if "admin_unlocked" not in st.session_state:
        st.session_state.admin_unlocked = False

    if not st.session_state.admin_unlocked:
        admin_pass = st.text_input("Admin Password:", type="password", key="adm_pass")
        if st.button("🔓 Login", key="adm_login"):
            # ⚠️ CHANGE THIS TO YOUR OWN SECRET PASSWORD
            if admin_pass == "Sadga@Khareef2026":
                st.session_state.admin_unlocked = True
                st.rerun()
            else:
                st.error("❌ Wrong password.")
    else:
        st.success("✅ Welcome, Sadga Selime!")
        if st.button("🔒 Logout", key="adm_logout"):
            st.session_state.admin_unlocked = False
            st.rerun()

        # ── VISITOR STATS ──
        st.markdown("### 👥 Visitor Statistics")
        stats = get_visitor_stats()
        v1, v2 = st.columns(2)
        v1.metric("🌍 Total Visits", stats["total"])
        v2.metric("📅 Today's Visits", stats["today"])

        if stats["by_date"]:
            st.markdown("**Visits by Date:**")
            df_visitors = pd.DataFrame([
                {"Date": d, "Visits": c}
                for d, c in sorted(stats["by_date"].items(), reverse=True)
            ])
            st.dataframe(df_visitors, use_container_width=True, height=250)
            st.download_button("📥 Download Visitor Log",
                pd.DataFrame(load_json(VISITORS_FILE)).to_csv(index=False),
                "visitors.csv", "text/csv", key="dl_vis")

        st.markdown("---")

        # ── USER RECORDS ──
        st.markdown("### 📋 All User Assessment Records")
        records = load_json(RECORDS_FILE)
        if records:
            df_r = pd.DataFrame(records).sort_values("timestamp", ascending=False)
            s1,s2,s3,s4 = st.columns(4)
            s1.metric("Total Checks",  len(df_r))
            s2.metric("🟢 Green",  len(df_r[df_r["triage_level"]=="GREEN"]))
            s3.metric("🟡 Yellow", len(df_r[df_r["triage_level"]=="YELLOW"]))
            s4.metric("🔴 Red",    len(df_r[df_r["triage_level"]=="RED"]))

            search = st.text_input("Search by name:", key="adm_search")
            if search:
                df_r = df_r[df_r["name"].str.contains(search, case=False, na=False)]

            st.dataframe(df_r, use_container_width=True, height=380)
            ac1, ac2 = st.columns(2)
            with ac1:
                st.download_button("📥 Download CSV",
                    df_r.to_csv(index=False), "records.csv", "text/csv", key="adm_csv")
            with ac2:
                st.download_button("📥 Download JSON",
                    json.dumps(records, indent=2, ensure_ascii=False),
                    "records.json", "application/json", key="adm_json")

            if st.button("🗑️ Clear Records", key="adm_clear_r"):
                if os.path.exists(RECORDS_FILE): os.remove(RECORDS_FILE)
                st.success("Records cleared!"); st.rerun()
        else:
            st.info("No assessment records yet.")

        st.markdown("---")

        # ── SAVED PROFILES ──
        st.markdown("### 👤 All Saved Profiles")
        profiles = load_json(PROFILES_FILE)
        if profiles:
            st.dataframe(pd.DataFrame(profiles), use_container_width=True)
            st.download_button("📥 Download Profiles",
                pd.DataFrame(profiles).to_csv(index=False),
                "profiles.csv", "text/csv", key="adm_prof")
            if st.button("🗑️ Clear Profiles", key="adm_clear_p"):
                if os.path.exists(PROFILES_FILE): os.remove(PROFILES_FILE)
                st.success("Profiles cleared!"); st.rerun()
        else:
            st.info("No profiles saved yet.")

st.markdown("---")
st.caption("🌿 Khareef Health v3.3 · by Sadga Selime · Salalah, Oman · Powered by Google Gemini AI · Educational use only")
