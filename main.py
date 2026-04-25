import streamlit as st

st.set_page_config(
    page_title="Khareef Health",
    page_icon=":herb:",
    layout="wide",
    initial_sidebar_state="collapsed",
)

import os, json, uuid, urllib.parse
from datetime import datetime
import pandas as pd
import streamlit.components.v1 as components

from data        import Patient, validate_patient_input, normalize_symptoms, log_patient
from triage      import assess_patient
from gemini_helper import (
    get_gemini_advice, analyze_free_text,
    is_api_key_configured, get_api_key_status, GEMINI_API_KEY
)
from diseases import DISEASES, CATEGORIES, search_diseases, get_by_category

# Voice + translations
try:
    from translations import t, LANGUAGES, get_lang_code, get_tts_code
    from voice_utils import voice_input_component, text_to_speech_component
    VOICE_ENABLED = True
except ImportError:
    VOICE_ENABLED = False
    print("Voice features disabled - translations.py or voice_utils.py not found")

# ── Storage ──────────────────────────────────────
RECORDS_FILE  = "user_records.json"
PROFILES_FILE = "user_profiles.json"
VISITORS_FILE = "visitors.json"

def load_json(f):
    if os.path.exists(f):
        try: return json.load(open(f))
        except: return []
    return []

def save_json(f, d):
    json.dump(d, open(f,"w"), indent=2, ensure_ascii=False)

def save_record(r):
    d = load_json(RECORDS_FILE); d.append(r); save_json(RECORDS_FILE, d)

def save_profile(p):
    d = load_json(PROFILES_FILE)
    for i,x in enumerate(d):
        if x.get("name","").lower() == p["name"].lower():
            d[i]=p; save_json(PROFILES_FILE,d); return
    d.append(p); save_json(PROFILES_FILE,d)

def log_visitor(name="Anonymous", action="opened app"):
    try:
        d = load_json(VISITORS_FILE)
        d.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "date":      datetime.now().strftime("%Y-%m-%d"),
            "name":      name or "Anonymous",
            "action":    action,
            "session":   st.session_state.get("sid",""),
        })
        save_json(VISITORS_FILE, d)
    except: pass

# ── Session defaults ──────────────────────────────
DEFAULTS = {
    "gender":"Not specified","user_name":"","user_age":40,
    "user_city":"Salalah","user_conditions":[],"user_medications":"",
    "user_phone":"","user_blood_type":"Unknown",
    "khareef":False,"show_arabic":True,"use_ai":is_api_key_configured(),
    "welcomed":False,"profile_restored":False,"sid":str(uuid.uuid4())[:8],
    "show_card_info":None,"language":"English",
}
for k,v in DEFAULTS.items():
    if k not in st.session_state: st.session_state[k]=v

# ══════════════════════════════════════════════════
# STEP 1 — JS reads localStorage → sets URL params
# Streamlit reads URL params → restores session state
# This is the BRIDGE between JS and Python
# ══════════════════════════════════════════════════
components.html("""
<script>
(function() {
    try {
        var url = new URL(window.parent.location.href);
        // Only inject if not already done
        if (url.searchParams.get('kn')) {
            console.log('Profile already loaded from URL params');
            return;
        }
        
        var saved = localStorage.getItem('khareef_profile');
        if (!saved) {
            console.log('No saved profile found in localStorage');
            return;
        }
        
        var p = JSON.parse(saved);
        if (!p.name) {
            console.log('Profile exists but has no name');
            return;
        }
        
        console.log('Loading profile for:', p.name);
        
        // Set URL parameters
        url.searchParams.set('kn',  encodeURIComponent(p.name  || ''));
        url.searchParams.set('kp',  encodeURIComponent(p.phone || ''));
        url.searchParams.set('ka',  p.age   || 40);
        url.searchParams.set('kg',  encodeURIComponent(p.gender     || 'Not specified'));
        url.searchParams.set('kc',  encodeURIComponent(p.city       || 'Salalah'));
        url.searchParams.set('kb',  encodeURIComponent(p.blood_type || 'Unknown'));
        url.searchParams.set('km',  encodeURIComponent(p.medications|| ''));
        url.searchParams.set('kco', encodeURIComponent(JSON.stringify(p.conditions||[])));
        
        // Update URL and reload
        window.parent.history.replaceState({}, '', url.toString());
        console.log('Profile loaded, reloading page...');
        window.parent.location.reload();
    } catch(e) {
        console.error('Error loading profile from localStorage:', e);
    }
})();
</script>
""", height=0)

# STEP 2 — Read URL params into session state
params = st.query_params
if params.get("kn") and not st.session_state.profile_restored:
    st.session_state.user_name        = urllib.parse.unquote(params.get("kn",""))
    st.session_state.user_phone       = urllib.parse.unquote(params.get("kp",""))
    st.session_state.user_city        = urllib.parse.unquote(params.get("kc","Salalah"))
    st.session_state.gender           = urllib.parse.unquote(params.get("kg","Not specified"))
    st.session_state.user_blood_type  = urllib.parse.unquote(params.get("kb","Unknown"))
    st.session_state.user_medications = urllib.parse.unquote(params.get("km",""))
    try: st.session_state.user_age = int(params.get("ka", 40))
    except: pass
    try: st.session_state.user_conditions = json.loads(urllib.parse.unquote(params.get("kco","[]")))
    except: pass
    st.session_state.profile_restored = True
    st.session_state.welcomed = True  # Auto-skip welcome screen
    # Clear URL params after restoration
    st.query_params.clear()

# ── Theme ─────────────────────────────────────────
THEMES = {
    "Male":          {"p":"#1a4a8a","s":"#2d6fba","l":"#dbeafe","a":"#0d2d5c","g":"135deg,#0d2d5c,#1a4a8a,#2d6fba"},
    "Female":        {"p":"#9d174d","s":"#db2777","l":"#fce7f3","a":"#500724","g":"135deg,#500724,#9d174d,#db2777"},
    "Not specified": {"p":"#1a5c45","s":"#2d8a65","l":"#d1fae5","a":"#0d3d29","g":"135deg,#0d3d29,#1a5c45,#2d8a65"},
}
T = THEMES[st.session_state.gender]

# ── CSS ───────────────────────────────────────────
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&family=Poppins:wght@400;600;700&display=swap');
html,body,[class*="css"]{font-family:'Poppins',sans-serif;}
""" + f"""
.stApp{{background:
    radial-gradient(ellipse at 10% 10%,{T['l']} 0%,transparent 55%),
    radial-gradient(ellipse at 90% 90%,{T['l']}99 0%,transparent 55%),
    linear-gradient(160deg,#f8fafb 0%,#f0f4f2 100%);}}
.header-box{{background:linear-gradient({T['g']});border-radius:20px;
    padding:26px 32px;color:white;box-shadow:0 8px 28px {T['p']}55;
    margin-bottom:16px;position:relative;overflow:hidden;}}
.profile-card{{background:linear-gradient({T['g']});color:white;
    border-radius:16px;padding:24px;text-align:center;
    position:relative;overflow:hidden;}}
.step{{background:{T['l']};border-left:4px solid {T['p']};border-radius:8px;
    padding:10px 14px;margin:6px 0;font-size:0.9rem;line-height:1.6;
    transition:transform 0.15s ease,box-shadow 0.15s ease;}}
.step:hover{{transform:translateX(4px);box-shadow:2px 2px 8px {T['p']}22;}}
.stTabs [data-baseweb="tab-list"]{{background:white;border-radius:12px;
    padding:5px;box-shadow:0 2px 12px rgba(0,0,0,0.06);gap:4px;}}
.stTabs [aria-selected="true"]{{background:{T['p']}!important;color:white!important;}}
.stTabs [data-baseweb="tab"]{{border-radius:8px;font-weight:600;font-size:0.83rem;padding:7px 12px;}}
[data-testid="stMetricValue"]{{color:{T['p']}!important;font-weight:700!important;}}
div.stButton > button{{background:linear-gradient({T['g']});color:white!important;
    border:none;border-radius:10px;font-weight:700;transition:all 0.2s ease;
    box-shadow:0 4px 12px {T['p']}33;}}
div.stButton > button:hover{{transform:translateY(-2px);box-shadow:0 6px 18px {T['p']}44;}}
""" + """
.step-red{background:#fff1f2;border-left:4px solid #dc2626;border-radius:8px;
    padding:10px 14px;margin:6px 0;font-size:0.9rem;line-height:1.6;}
.step-red:hover{transform:translateX(4px);}
.ar{font-family:'Tajawal',sans-serif;direction:rtl;text-align:right;}
.disclaimer{background:#fff8e1;border:1px solid #fcd34d;border-radius:10px;
    padding:12px 18px;font-size:0.82rem;color:#78350f;}
.result-green{background:linear-gradient(135deg,#dcfce7,#bbf7d0);
    border:3px solid #16a34a;border-radius:16px;padding:24px;text-align:center;}
.result-yellow{background:linear-gradient(135deg,#fef9c3,#fde68a);
    border:3px solid #f59e0b;border-radius:16px;padding:24px;text-align:center;}
.result-red{background:linear-gradient(135deg,#fee2e2,#fecaca);
    border:3px solid #dc2626;border-radius:16px;padding:24px;text-align:center;}
.nutrition-tip{background:#f0fdf4;border-left:3px solid #22c55e;border-radius:6px;
    padding:9px 14px;margin:5px 0;font-size:0.88rem;}
@keyframes fadeUp{from{opacity:0;transform:translateY(14px);}to{opacity:1;transform:translateY(0);}}
@keyframes float{0%,100%{transform:translateY(0);}50%{transform:translateY(-6px);}}
@keyframes pulse-ring{0%{transform:scale(1);opacity:0.5;}100%{transform:scale(1.6);opacity:0;}}
.float{display:inline-block;animation:float 3s ease-in-out infinite;}
section[data-testid="stSidebar"]{display:none;}
#MainMenu,footer,header{visibility:hidden;}
</style>""", unsafe_allow_html=True)

# ══════════════════════════════════════
# WELCOME SCREEN
# ══════════════════════════════════════
if not st.session_state.welcomed:
    g = T['g']; p = T['p']
    is_returning = bool(st.session_state.user_name)

    if is_returning and st.session_state.profile_restored:
        # Auto-skip for users with restored profiles
        st.session_state.welcomed = True
        log_visitor(st.session_state.user_name, "auto-login returning user")
        st.rerun()
    
    elif is_returning:
        st.markdown(f"""
        <div style="background:linear-gradient({g});border-radius:20px;padding:32px;
             color:white;text-align:center;margin-bottom:24px;
             box-shadow:0 8px 24px {p}44;">
            <div style="font-size:3.5rem">👋</div>
            <div style="font-size:2rem;font-weight:800;margin:10px 0">Welcome back!</div>
            <div style="font-size:1.3rem;opacity:0.95;margin-bottom:6px">
                {st.session_state.user_name}</div>
            <div style="opacity:0.85;font-size:0.9rem">
                Your profile has been restored automatically</div>
        </div>""", unsafe_allow_html=True)
        wc1,wc2,wc3 = st.columns([1,2,1])
        with wc2:
            if st.button("Continue / متابعة", type="primary",
                    use_container_width=True, key="wbtn_ret"):
                st.session_state.welcomed = True
                log_visitor(st.session_state.user_name, "returning user")
                st.rerun()
            if st.button("Not you? Start fresh", use_container_width=True, key="wfresh"):
                for k in list(DEFAULTS.keys()):
                    st.session_state[k] = DEFAULTS[k]
                st.query_params.clear()
                components.html("<script>localStorage.removeItem('khareef_profile');</script>", height=0)
                st.rerun()
    else:
        st.markdown(f"""
        <div style="background:linear-gradient({g});border-radius:20px;padding:32px;
             color:white;text-align:center;margin-bottom:24px;
             box-shadow:0 8px 24px {p}44;">
            <div class="float" style="font-size:3.5rem">🌿</div>
            <div style="font-size:2rem;font-weight:800;margin:10px 0">Khareef Health</div>
            <div style="opacity:0.9;font-size:0.95rem">
                AI Telemedicine Triage · Salalah, Dhofar, Oman</div>
            <div class="ar" style="opacity:0.75;margin-top:6px;font-size:0.9rem">
                مساعد الفرز الطبي الذكي · صلالة، ظفار، عُمان</div>
        </div>""", unsafe_allow_html=True)
        wc1,wc2,wc3 = st.columns([1,2,1])
        with wc2:
            st.markdown("#### Please introduce yourself 👋")
            w_name  = st.text_input("Your Name / اسمك",
                placeholder="e.g. Ahmed Al-Shanfari", key="wn")
            w_phone = st.text_input("Phone (optional) / الهاتف",
                placeholder="+968 9X XXX XXXX", key="wp")
            c1,c2 = st.columns(2)
            if c1.button("Continue / متابعة", type="primary",
                    use_container_width=True, key="wbtn"):
                st.session_state.welcomed   = True
                st.session_state.user_name  = w_name.strip()
                st.session_state.user_phone = w_phone.strip()
                log_visitor(w_name.strip() or "Anonymous", "first visit")
                st.rerun()
            if c2.button("Skip / تخطي", use_container_width=True, key="wskip"):
                st.session_state.welcomed = True
                log_visitor("Anonymous (skipped)", "skipped welcome")
                st.rerun()
            st.caption("🔒 Your info is private and saved only on your device")
    st.stop()

# ══════════════════════════════════════
# HEADER
# ══════════════════════════════════════
g_emoji = "👨" if st.session_state.gender=="Male" else "👩" if st.session_state.gender=="Female" else "🌿"
p = T['p']
st.markdown(f"""
<div class="header-box">
  <svg style="position:absolute;right:130px;top:6px;opacity:0.06;width:90px;height:90px"
       viewBox="0 0 100 100">
    <rect x="40" y="8" width="20" height="84" rx="10" fill="white"/>
    <rect x="8"  y="40" width="84" height="20" rx="10" fill="white"/>
  </svg>
  <svg style="position:absolute;left:-15px;bottom:-20px;opacity:0.05;width:110px;height:110px"
       viewBox="0 0 100 100">
    <circle cx="50" cy="50" r="44" fill="none" stroke="white" stroke-width="8"/>
    <circle cx="50" cy="50" r="28" fill="none" stroke="white" stroke-width="4"/>
  </svg>
  <div style="display:flex;align-items:center;gap:16px;flex-wrap:wrap;position:relative;z-index:1">
    <div style="position:relative">
      <div class="float" style="font-size:3rem">{g_emoji}</div>
      <div style="position:absolute;inset:-6px;border-radius:50%;
           border:2px solid rgba(255,255,255,0.3);
           animation:pulse-ring 2s ease-out infinite;pointer-events:none"></div>
    </div>
    <div style="flex:1">
      <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap">
        <span style="font-size:1.8rem;font-weight:700">Khareef Health</span>
        <span style="background:rgba(255,255,255,0.2);padding:3px 10px;
               border-radius:99px;font-size:0.7rem;font-weight:700;letter-spacing:1px">
          AI POWERED</span>
      </div>
      <div style="font-size:0.72rem;opacity:0.65">by Sadga Selime &nbsp;·&nbsp; Salalah, Oman</div>
      <div style="font-size:0.83rem;opacity:0.85;margin-top:2px">
        🩺 Triage &nbsp;·&nbsp; 📸 Skin AI &nbsp;·&nbsp; 💊 Med Scanner &nbsp;·&nbsp; 🦠 Diseases</div>
      <div class="ar" style="font-size:0.8rem;opacity:0.7">
        مساعد الفرز الطبي الذكي · صلالة، ظفار، عُمان</div>
    </div>
    <div style="text-align:center;background:rgba(220,38,38,0.3);border-radius:12px;
         padding:10px 18px;border:1px solid rgba(255,255,255,0.2)">
      <div style="font-size:0.7rem;letter-spacing:2px;opacity:0.9">EMERGENCY</div>
      <div style="font-size:2rem;font-weight:900;letter-spacing:2px">999</div>
    </div>
  </div>
  <svg style="width:100%;height:22px;margin-top:10px;opacity:0.18" viewBox="0 0 500 22">
    <path d="M0 11 L80 11 L95 2 L105 20 L115 5 L125 17 L135 11 L500 11"
          stroke="white" stroke-width="2.5" fill="none" stroke-linecap="round"/>
  </svg>
</div>""", unsafe_allow_html=True)

# ── Settings bar ──────────────────────────────────
st.markdown("#### Settings / الإعدادات / সেটিংস")

if VOICE_ENABLED:
    s1,s2,s3,s4,s5 = st.columns([1.2,1.2,1,1,1])
else:
    s1,s3,s4,s5 = st.columns([1.2,1,1,1])

with s1:
    new_g = st.selectbox("Gender Theme",
        ["Not specified","Male","Female"],
        index=["Not specified","Male","Female"].index(st.session_state.gender),
        key="gs")
    if new_g != st.session_state.gender:
        st.session_state.gender = new_g; st.rerun()
    st.caption({"Male":"💙 Blue","Female":"💗 Rose","Not specified":"💚 Green"}[st.session_state.gender])

if VOICE_ENABLED:
    with s2:
        lang_opts = ["English", "العربية", "বাংলা"]
        curr_idx = lang_opts.index(st.session_state.language) if st.session_state.language in lang_opts else 0
        new_lang = st.selectbox("🌐 Language / لغة / ভাষা", lang_opts, index=curr_idx, key="lang_sel")
        if new_lang != st.session_state.language:
            st.session_state.language = new_lang; st.rerun()
        st.caption({"English":"🇬🇧 EN","العربية":"🇸🇦 AR","বাংলা":"🇧🇩 BN"}[st.session_state.language])

with s3:
    st.session_state.khareef = st.toggle("🌦️ Khareef",  value=st.session_state.khareef, key="kt")
with s4:
    st.session_state.show_arabic = st.toggle("📖 Arabic", value=st.session_state.show_arabic, key="at")
with s5:
    st.session_state.use_ai = st.toggle("🤖 AI", value=st.session_state.use_ai, key="git")

if st.session_state.khareef:
    st.warning("🌦️ Khareef Mode ON — Higher respiratory sensitivity")

# ── Welcome returning users ───────────────────────
if st.session_state.user_name and st.session_state.profile_restored:
    welcome_time = datetime.now().hour
    if welcome_time < 12:
        greeting = "Good morning" if not st.session_state.show_arabic else "صباح الخير"
    elif welcome_time < 18:
        greeting = "Good afternoon" if not st.session_state.show_arabic else "مساء الخير"
    else:
        greeting = "Good evening" if not st.session_state.show_arabic else "مساء الخير"
    
    st.markdown(f"""
    <div style="background:linear-gradient({T['g']});color:white;border-radius:16px;
         padding:20px 28px;margin-bottom:16px;box-shadow:0 4px 16px {T['p']}44;
         animation:fadeUp 0.5s ease;">
        <div style="font-size:1.8rem;margin-bottom:4px">{g_emoji}</div>
        <div style="font-size:1.3rem;font-weight:700">{greeting}, {st.session_state.user_name}!</div>
        <div style="font-size:0.9rem;opacity:0.9;margin-top:4px">
            Welcome back · Age: {st.session_state.user_age} · {st.session_state.user_city}</div>
        <div style="font-size:0.8rem;opacity:0.75;margin-top:6px">
            Your profile is loaded and ready to use 🩺</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ── Clickable stat cards ───────────────────────────
col1,col2,col3,col4 = st.columns(4)
with col1:
    st.markdown("""<div style="background:#fee2e2;border:1px solid #fca5a5;border-radius:14px;
         padding:14px;text-align:center;"><div style="font-size:1.8rem">❤️</div>
         <div style="font-weight:700;color:#dc2626;font-size:0.82rem">EMERGENCY</div>
         <div style="font-size:0.75rem;color:#dc2626;opacity:0.8">Call 999</div></div>""",
        unsafe_allow_html=True)
    if st.button("Emergency Info", key="cem", use_container_width=True):
        st.session_state.show_card_info = "emergency" if st.session_state.show_card_info!="emergency" else None

with col2:
    st.markdown("""<div style="background:#d1fae5;border:1px solid #6ee7b7;border-radius:14px;
         padding:14px;text-align:center;"><div style="font-size:1.8rem">🩺</div>
         <div style="font-weight:700;color:#065f46;font-size:0.82rem">AI TRIAGE</div>
         <div style="font-size:0.75rem;color:#065f46;opacity:0.8">GREEN/YELLOW/RED</div></div>""",
        unsafe_allow_html=True)
    if st.button("How It Works", key="ctr", use_container_width=True):
        st.session_state.show_card_info = "triage" if st.session_state.show_card_info!="triage" else None

with col3:
    st.markdown("""<div style="background:#dbeafe;border:1px solid #93c5fd;border-radius:14px;
         padding:14px;text-align:center;"><div style="font-size:1.8rem">🌐</div>
         <div style="font-weight:700;color:#1e40af;font-size:0.82rem">BILINGUAL</div>
         <div style="font-size:0.75rem;color:#1e40af;opacity:0.8">English + Arabic</div></div>""",
        unsafe_allow_html=True)
    if st.button("Languages", key="cla", use_container_width=True):
        st.session_state.show_card_info = "bilingual" if st.session_state.show_card_info!="bilingual" else None

with col4:
    st.markdown("""<div style="background:#fef9c3;border:1px solid #fcd34d;border-radius:14px;
         padding:14px;text-align:center;"><div style="font-size:1.8rem">🌦️</div>
         <div style="font-weight:700;color:#92400e;font-size:0.82rem">KHAREEF</div>
         <div style="font-size:0.75rem;color:#92400e;opacity:0.8">Salalah Season</div></div>""",
        unsafe_allow_html=True)
    if st.button("Khareef Info", key="ckh", use_container_width=True):
        st.session_state.show_card_info = "khareef" if st.session_state.show_card_info!="khareef" else None

if st.session_state.show_card_info == "emergency":
    with st.expander("Emergency Contacts — Salalah", expanded=True):
        c1,c2,c3 = st.columns(3)
        with c1: st.error("Ambulance / Police\n999\n24 hours")
        with c2: st.info("Sultan Qaboos Hospital\n+968 23 211 555\nAl Dahariz, Salalah")
        with c3: st.info("Badr Al Samaa\n+968 23 219 999\n24 hours")

elif st.session_state.show_card_info == "triage":
    with st.expander("How AI Triage Works", expanded=True):
        st.markdown("""
| Level | Meaning | Action |
|---|---|---|
| GREEN | All readings normal | Rest at home |
| YELLOW | Mild concern | See doctor soon |
| RED | Urgent concern | Go to hospital NOW |

Google Gemini AI then gives personalised advice in English and Arabic.
Go to **Health Check tab** to assess your health!""")

elif st.session_state.show_card_info == "bilingual":
    with st.expander("Bilingual Support", expanded=True):
        st.success("Full English and Arabic support. Toggle Arabic in settings above.")
        st.markdown('<div class="ar" style="background:#fffbf0;padding:14px;border-radius:10px;border:1px solid #fde68a;line-height:2;font-size:1rem">تطبيق خريف هيلث متاح باللغتين العربية والإنجليزية بالكامل.</div>', unsafe_allow_html=True)

elif st.session_state.show_card_info == "khareef":
    with st.expander("About Khareef Mode", expanded=True):
        st.warning("Salalah's monsoon season (June-September) increases humidity, mold, respiratory risks and mosquito-borne diseases. Turn Khareef Mode ON during this period for extra sensitivity.")

st.markdown("")
st.markdown("---")

# ══════════════════════════════════════
# TABS
# ══════════════════════════════════════
tabs = st.tabs([
    "👤 Profile","🩺 Health Check","🚨 Emergency",
    "💊 Medicines","👩 Women","🦠 Diseases",
    "📸 Skin AI","💊📷 Med Scanner","📊 Trends","ℹ️ About"
])
(tab_profile, tab_assess, tab_emergency,
 tab_medicine, tab_women, tab_diseases,
 tab_skin, tab_medscan, tab_research, tab_about) = tabs

with tab_profile:
    from tabs.tab_profile import render
    render(T, g_emoji, save_profile, load_json, PROFILES_FILE)

with tab_assess:
    from tabs.tab_assess import render
    render(T, save_record, log_patient, is_api_key_configured,
           get_gemini_advice, analyze_free_text, RECORDS_FILE)

with tab_emergency:
    from tabs.tab_emergency import render
    render(T)

with tab_medicine:
    from tabs.tab_medicine import render
    render(T)

with tab_women:
    from tabs.tab_women import render
    render(T)

with tab_diseases:
    from tabs.tab_diseases import render
    render(T, DISEASES, CATEGORIES, search_diseases, get_by_category)

with tab_skin:
    from tabs.tab_skin import render
    render(T, GEMINI_API_KEY, is_api_key_configured)

with tab_medscan:
    from tabs.tab_medscan import render
    render(T, GEMINI_API_KEY, is_api_key_configured)

with tab_research:
    from tabs.tab_research import render
    render(T, load_json, RECORDS_FILE)

with tab_about:
    from tabs.tab_about import render
    render(T)

# ── Hidden Admin Panel ────────────────────────────
if st.query_params.get("admin","") == "true":
    from tabs.tab_admin import render
    render(load_json, save_json, RECORDS_FILE, PROFILES_FILE, VISITORS_FILE)

st.markdown("---")
st.caption("🌿 Khareef Health v4.1 · by Sadga Selime · Salalah, Oman · Powered by Google Gemini AI · Educational use only")
