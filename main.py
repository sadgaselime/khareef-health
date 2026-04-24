"""
Khareef Health v4.0 — main.py
Streamlit entry point. Kept small and clean.
Run: streamlit run main.py
"""
import streamlit as st

st.set_page_config(
    page_title="Khareef Health",
    page_icon=":herb:",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Full PWA Override ────────────────────────────
ICON_512 = "https://raw.githubusercontent.com/sadgaselime/khareef-health/main/icon-512.png"
ICON_192 = "https://raw.githubusercontent.com/sadgaselime/khareef-health/main/icon-192.png"
ICON_180 = "https://raw.githubusercontent.com/sadgaselime/khareef-health/main/apple-touch-icon.png"

st.markdown(f"""
<head>
<!-- Viewport -->
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">

<!-- PWA name and theme -->
<meta name="application-name" content="Khareef Health">
<meta name="theme-color" content="#1a5c45">

<!-- iOS specific — MUST have these for iPhone home screen -->
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Khareef Health">
<link rel="apple-touch-icon" href="{ICON_180}">
<link rel="apple-touch-icon" sizes="152x152" href="{ICON_192}">
<link rel="apple-touch-icon" sizes="180x180" href="{ICON_180}">
<link rel="apple-touch-icon" sizes="167x167" href="{ICON_192}">

<!-- Android / Chrome PWA manifest (inline) -->
<link rel="manifest" href="data:application/manifest+json,{{
  &quot;name&quot;: &quot;Khareef Health&quot;,
  &quot;short_name&quot;: &quot;Khareef&quot;,
  &quot;description&quot;: &quot;AI Telemedicine Triage - Salalah, Oman&quot;,
  &quot;start_url&quot;: &quot;/&quot;,
  &quot;display&quot;: &quot;standalone&quot;,
  &quot;background_color&quot;: &quot;#1a5c45&quot;,
  &quot;theme_color&quot;: &quot;#1a5c45&quot;,
  &quot;orientation&quot;: &quot;portrait&quot;,
  &quot;icons&quot;: [
    {{&quot;src&quot;: &quot;{ICON_192}&quot;, &quot;sizes&quot;: &quot;192x192&quot;, &quot;type&quot;: &quot;image/png&quot;, &quot;purpose&quot;: &quot;any maskable&quot;}},
    {{&quot;src&quot;: &quot;{ICON_512}&quot;, &quot;sizes&quot;: &quot;512x512&quot;, &quot;type&quot;: &quot;image/png&quot;, &quot;purpose&quot;: &quot;any maskable&quot;}}
  ]
}}">

<!-- Override favicon -->
<link rel="icon" type="image/png" sizes="512x512" href="{ICON_512}">
<link rel="icon" type="image/png" sizes="192x192" href="{ICON_192}">
<link rel="shortcut icon" href="{ICON_512}">

<!-- Override page title -->
<title>Khareef Health</title>

<script>
// Override document title to prevent Streamlit from changing it
Object.defineProperty(document, 'title', {{
    get: function() {{ return 'Khareef Health'; }},
    set: function() {{ document.getElementsByTagName('title')[0].textContent = 'Khareef Health'; }}
}});
document.title = 'Khareef Health';
// Keep overriding every second
setInterval(function() {{
    if(document.title !== 'Khareef Health') {{
        document.title = 'Khareef Health';
    }}
}}, 500);
</script>
</head>
""", unsafe_allow_html=True)

# ── imports ──────────────────────────────────────
import os, json, uuid
from datetime import datetime
import pandas as pd

from data        import Patient, validate_patient_input, normalize_symptoms, log_patient
from triage      import assess_patient
from gemini_helper import (
    get_gemini_advice, analyze_free_text,
    is_api_key_configured, get_api_key_status, GEMINI_API_KEY
)
from diseases import DISEASES, CATEGORIES, search_diseases, get_by_category

# ── storage helpers ──────────────────────────────
RECORDS_FILE  = "user_records.json"
PROFILES_FILE = "user_profiles.json"
VISITORS_FILE = "visitors.json"

def load_json(f):
    if os.path.exists(f):
        try:
            return json.load(open(f))
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

# ── session state ────────────────────────────────
DEFAULTS = {
    "gender":"Not specified","user_name":"","user_age":40,
    "user_city":"Salalah","user_conditions":[],"user_medications":"",
    "user_phone":"","user_blood_type":"Unknown",
    "khareef":False,"show_arabic":True,"use_ai":is_api_key_configured(),
    "welcomed":False,
}
for k,v in DEFAULTS.items():
    if k not in st.session_state: st.session_state[k]=v

if "sid" not in st.session_state:
    st.session_state.sid = str(uuid.uuid4())[:8]
    log_visitor("Anonymous","opened app")

# ── theme ────────────────────────────────────────
THEMES = {
    "Male":          {"p":"#1a4a8a","s":"#2d6fba","l":"#dbeafe","a":"#0d2d5c","g":"135deg,#0d2d5c,#1a4a8a,#2d6fba"},
    "Female":        {"p":"#9d174d","s":"#db2777","l":"#fce7f3","a":"#500724","g":"135deg,#500724,#9d174d,#db2777"},
    "Not specified": {"p":"#1a5c45","s":"#2d8a65","l":"#d1fae5","a":"#0d3d29","g":"135deg,#0d3d29,#1a5c45,#2d8a65"},
}
T = THEMES[st.session_state.gender]

# ── CSS ──────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&family=Poppins:wght@400;600;700&display=swap');
html,body,[class*="css"]{font-family:'Poppins',sans-serif;}
""" + f"""
.stApp{{background:
    radial-gradient(ellipse at 10% 10%, {T['l']} 0%,transparent 55%),
    radial-gradient(ellipse at 90% 90%, {T['l']}99 0%,transparent 55%),
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
.stSelectbox>div>div,.stTextInput input,.stNumberInput input,.stTextArea textarea{{
    border-radius:10px!important;border-color:{T['p']}44!important;}}
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
.stat-card{border-radius:14px;padding:16px;text-align:center;transition:transform 0.2s;}
.stat-card:hover{transform:translateY(-3px);}
@keyframes fadeUp{from{opacity:0;transform:translateY(14px);}to{opacity:1;transform:translateY(0);}}
@keyframes float{0%,100%{transform:translateY(0);}50%{transform:translateY(-6px);}}
@keyframes pulse-ring{0%{transform:scale(1);opacity:0.6;}100%{transform:scale(1.5);opacity:0;}}
@keyframes ecg{0%{stroke-dashoffset:400;}100%{stroke-dashoffset:0;}}
.float{display:inline-block;animation:float 3s ease-in-out infinite;}
section[data-testid="stSidebar"]{display:none;}
#MainMenu,footer,header{visibility:hidden;}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════
# WELCOME SCREEN — Smart returning user detection
# ══════════════════════════════════════
if not st.session_state.welcomed:
    g  = T['g']
    p  = T['p']

    # Read localStorage to check if returning user
    import streamlit.components.v1 as stc_comp

    st.markdown(f"""
    <div style="background:linear-gradient({g});border-radius:20px;padding:32px;
         color:white;text-align:center;margin-bottom:24px;
         box-shadow:0 8px 24px {p}44;position:relative;overflow:hidden;">
        <svg style="position:absolute;right:20px;top:10px;opacity:0.08;width:80px;height:80px"
             viewBox="0 0 100 100">
            <rect x="40" y="8" width="20" height="84" rx="10" fill="white"/>
            <rect x="8" y="40" width="84" height="20" rx="10" fill="white"/>
        </svg>
        <div class="float" style="font-size:3.5rem">🌿</div>
        <div style="font-size:2rem;font-weight:800;margin:10px 0">Khareef Health</div>
        <div style="opacity:0.9;font-size:0.95rem">
            AI Telemedicine Triage · Salalah, Dhofar, Oman</div>
        <div class="ar" style="opacity:0.75;margin-top:6px;font-size:0.9rem">
            مساعد الفرز الطبي الذكي · صلالة، ظفار، عُمان</div>
    </div>""", unsafe_allow_html=True)

    # Check localStorage for returning user
    stc_comp.html("""
    <script>
    var saved = localStorage.getItem('khareef_profile');
    if (saved) {
        var p = JSON.parse(saved);
        var nameEl = window.parent.document.querySelector('[data-testid="stTextInput"] input');
        var phoneEl = window.parent.document.querySelectorAll('[data-testid="stTextInput"] input')[1];
        if (nameEl && p.name)  { nameEl.value  = p.name;  nameEl.dispatchEvent(new Event('input',{bubbles:true})); }
        if (phoneEl && p.phone){ phoneEl.value = p.phone; phoneEl.dispatchEvent(new Event('input',{bubbles:true})); }
        document.getElementById('returning').style.display = 'block';
    }
    </script>
    <div id="returning" style="display:none;background:rgba(255,255,255,0.15);
         border-radius:10px;padding:10px 16px;margin:8px 0;font-size:0.9rem;
         font-family:Poppins,sans-serif;color:#065f46;background:#d1fae5;
         border:1px solid #6ee7b7;">
        ✅ Welcome back! Your profile was found on this device.
    </div>
    """, height=50)

    wc1, wc2, wc3 = st.columns([1,2,1])
    with wc2:
        st.markdown("#### Welcome / أهلاً وسهلاً 👋")
        w_name  = st.text_input("Your Name / اسمك",
            value=st.session_state.user_name,
            placeholder="e.g. Ahmed Al-Shanfari", key="wn")
        w_phone = st.text_input("Phone (optional) / الهاتف",
            value=st.session_state.user_phone,
            placeholder="+968 9X XXX XXXX", key="wp")

        c1,c2 = st.columns(2)
        if c1.button("Continue / متابعة", type="primary", use_container_width=True, key="wbtn"):
            st.session_state.welcomed   = True
            st.session_state.user_name  = w_name.strip()
            st.session_state.user_phone = w_phone.strip()
            log_visitor(w_name.strip() or "Anonymous", "entered welcome")
            st.rerun()
        if c2.button("Skip / تخطي", use_container_width=True, key="wskip"):
            st.session_state.welcomed = True
            log_visitor("Anonymous (skipped)", "skipped welcome")
            st.rerun()

        st.markdown("""
        <div style="text-align:center;font-size:0.78rem;color:#9ca3af;margin-top:10px;">
            🔒 Your information is private and saved only on this device
        </div>""", unsafe_allow_html=True)
    st.stop()

# ══════════════════════════════════════
# AUTO-LOAD PROFILE FROM BROWSER STORAGE
# ══════════════════════════════════════
import streamlit.components.v1 as components

# Read localStorage profile and restore to session state via URL trick
if not st.session_state.get("profile_loaded_from_storage"):
    components.html("""
    <script>
    (function() {
        var saved = localStorage.getItem('khareef_profile');
        if (saved) {
            try {
                var p = JSON.parse(saved);
                document.title = 'Khareef Health';
                // Show welcome back toast
                setTimeout(function() {
                    var note = document.createElement('div');
                    note.style.cssText =
                        'position:fixed;bottom:70px;right:16px;z-index:9999;' +
                        'background:#1a5c45;color:white;padding:12px 18px;' +
                        'border-radius:12px;font-size:0.85rem;font-weight:600;' +
                        'font-family:Poppins,sans-serif;' +
                        'box-shadow:0 4px 18px rgba(0,0,0,0.25);' +
                        'animation:fadeIn 0.4s ease;';
                    note.innerHTML = '<span style="margin-right:6px">✅</span> Welcome back, '
                        + (p.name || 'User') + '!';
                    document.body.appendChild(note);
                    setTimeout(function() {
                        note.style.opacity='0';
                        note.style.transition='opacity 0.5s';
                        setTimeout(function(){ note.remove(); }, 600);
                    }, 3000);
                }, 800);
            } catch(e) {}
        }
    })();
    </script>
    """, height=0)
    st.session_state.profile_loaded_from_storage = True

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
           border:2px solid rgba(255,255,255,0.35);animation:pulse-ring 2s ease-out infinite;
           pointer-events:none"></div>
    </div>
    <div style="flex:1">
      <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap">
        <span style="font-size:1.8rem;font-weight:700">Khareef Health</span>
        <span style="background:rgba(255,255,255,0.2);padding:3px 10px;
               border-radius:99px;font-size:0.7rem;font-weight:700;letter-spacing:1px">
          AI POWERED</span>
      </div>
      <div style="font-size:0.72rem;opacity:0.65">by Sadga Selime &nbsp;·&nbsp; Salalah, Oman 🇴🇲</div>
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
          stroke="white" stroke-width="2.5" fill="none" stroke-linecap="round"
          stroke-dasharray="400" style="animation:ecg 2s ease forwards"/>
  </svg>

</div>""", unsafe_allow_html=True)



# ══════════════════════════════════════
# SETTINGS BAR
# ══════════════════════════════════════
st.markdown("#### Settings / الإعدادات")
s1,s2,s3,s4 = st.columns([1.2,1,1,1])

with s1:
    new_g = st.selectbox("Gender Theme / الثيم",
        ["Not specified","Male","Female"],
        index=["Not specified","Male","Female"].index(st.session_state.gender),
        key="gs")
    if new_g != st.session_state.gender:
        st.session_state.gender = new_g; st.rerun()
    st.caption({"Male":"💙 Blue","Female":"💗 Rose","Not specified":"💚 Green"}[st.session_state.gender])
with s2:
    st.session_state.khareef    = st.toggle("🌦️ Khareef Mode",  value=st.session_state.khareef,    key="kt")
with s3:
    st.session_state.show_arabic = st.toggle("🌐 Arabic / عربي", value=st.session_state.show_arabic, key="at")
with s4:
    st.session_state.use_ai      = st.toggle("🤖 AI Advice",     value=st.session_state.use_ai,      key="git")

if st.session_state.khareef:
    st.warning("🌦️ Khareef Mode ON — Higher respiratory sensitivity")

st.markdown("---")

# ── Clickable stat cards ───────────────────────────
if "show_card_info" not in st.session_state:
    st.session_state.show_card_info = None

col1,col2,col3,col4 = st.columns(4)

with col1:
    st.markdown("""
    <div style="background:#fee2e2;border:1px solid #fca5a5;border-radius:14px;
         padding:14px;text-align:center;box-shadow:0 2px 8px #dc262618;cursor:pointer;">
        <div style="font-size:1.8rem;margin-bottom:4px">❤️</div>
        <div style="font-weight:700;color:#dc2626;font-size:0.82rem">EMERGENCY</div>
        <div style="font-size:0.75rem;color:#dc2626;opacity:0.8">Call 999</div>
    </div>""", unsafe_allow_html=True)
    if st.button("Emergency Info", key="card_em", use_container_width=True):
        st.session_state.show_card_info = "emergency"

with col2:
    st.markdown("""
    <div style="background:#d1fae5;border:1px solid #6ee7b7;border-radius:14px;
         padding:14px;text-align:center;box-shadow:0 2px 8px #065f4618;cursor:pointer;">
        <div style="font-size:1.8rem;margin-bottom:4px">🩺</div>
        <div style="font-weight:700;color:#065f46;font-size:0.82rem">AI TRIAGE</div>
        <div style="font-size:0.75rem;color:#065f46;opacity:0.8">GREEN/YELLOW/RED</div>
    </div>""", unsafe_allow_html=True)
    if st.button("How Triage Works", key="card_tr", use_container_width=True):
        st.session_state.show_card_info = "triage"

with col3:
    st.markdown("""
    <div style="background:#dbeafe;border:1px solid #93c5fd;border-radius:14px;
         padding:14px;text-align:center;box-shadow:0 2px 8px #1e40af18;cursor:pointer;">
        <div style="font-size:1.8rem;margin-bottom:4px">🌐</div>
        <div style="font-weight:700;color:#1e40af;font-size:0.82rem">BILINGUAL</div>
        <div style="font-size:0.75rem;color:#1e40af;opacity:0.8">English + Arabic</div>
    </div>""", unsafe_allow_html=True)
    if st.button("About Languages", key="card_la", use_container_width=True):
        st.session_state.show_card_info = "bilingual"

with col4:
    st.markdown("""
    <div style="background:#fef9c3;border:1px solid #fcd34d;border-radius:14px;
         padding:14px;text-align:center;box-shadow:0 2px 8px #92400e18;cursor:pointer;">
        <div style="font-size:1.8rem;margin-bottom:4px">🌦️</div>
        <div style="font-weight:700;color:#92400e;font-size:0.82rem">KHAREEF</div>
        <div style="font-size:0.75rem;color:#92400e;opacity:0.8">Salalah Season</div>
    </div>""", unsafe_allow_html=True)
    if st.button("Khareef Mode Info", key="card_kh", use_container_width=True):
        st.session_state.show_card_info = "khareef"

# Show card info when clicked
if st.session_state.show_card_info == "emergency":
    with st.expander("Emergency Contacts — Salalah", expanded=True):
        ec1,ec2,ec3 = st.columns(3)
        with ec1: st.error("Ambulance / Police\n📞 **999**\n24 hours")
        with ec2: st.info("Sultan Qaboos Hospital\n📞 +968 23 211 555\nAl Dahariz, Salalah")
        with ec3: st.info("Badr Al Samaa Hospital\n📞 +968 23 219 999\n24 hours")
        st.link_button("Open Emergency Tab for Full Guide →", "#")

elif st.session_state.show_card_info == "triage":
    with st.expander("How AI Triage Works", expanded=True):
        st.markdown("""
        The app uses a **medical rules engine** to assess your readings:

        | Level | What it means | Action |
        |---|---|---|
        | 🟢 **GREEN** | All readings normal | Rest at home, monitor |
        | 🟡 **YELLOW** | Mild concern | See a doctor soon |
        | 🔴 **RED** | Urgent concern | Go to hospital NOW |

        After triage, **Google Gemini AI** generates personalised advice in English and Arabic.
        Go to the **Health Check tab** to assess your health!
        """)

elif st.session_state.show_card_info == "bilingual":
    with st.expander("Bilingual Support", expanded=True):
        st.success("""
        **Khareef Health works in both English and Arabic**

        - All advice given in both languages simultaneously
        - Arabic text displayed right-to-left correctly
        - Voice input supports Arabic (ar-OM dialect)
        - Disease encyclopedia searchable in Arabic
        - Toggle Arabic on/off in settings above
        """)
        st.markdown('<div class="ar" style="background:#fffbf0;padding:14px;border-radius:10px;font-size:1rem;border:1px solid #fde68a;line-height:2">تطبيق خريف هيلث متاح باللغتين العربية والإنجليزية. يمكنك الحصول على النصائح الطبية بكلتا اللغتين في آنٍ واحد.</div>', unsafe_allow_html=True)

elif st.session_state.show_card_info == "khareef":
    with st.expander("About Khareef Mode", expanded=True):
        st.warning("""
        **What is Khareef?**

        Salalah experiences a unique **monsoon season (June–September)** called Khareef.
        During this time:
        - 🌫️ Humidity rises dramatically
        - 🍄 Mold and fungal spores increase
        - 😤 Asthma and respiratory problems worsen
        - 🦟 Mosquito-borne diseases increase
        - 🌡️ Heat stroke risk remains high

        **Khareef Mode** adjusts the app to be more sensitive to respiratory symptoms
        and gives extra warnings for elderly patients during this season.

        Toggle it ON above from **June to September** every year.
        """)

st.markdown("")

# ══════════════════════════════════════
# TABS
# ══════════════════════════════════════
tabs = st.tabs([
    "👤 Profile","🩺 Health Check","🚨 Emergency",
    "💊 Medicines","👩 Women","🦠 Diseases",
    "📸 Skin AI","💊📷 Med Scanner","📊 Trends",
    "💊🔔 Reminders","ℹ️ About"
])
(tab_profile, tab_assess, tab_emergency,
 tab_medicine, tab_women, tab_diseases,
 tab_skin, tab_medscan, tab_research,
 tab_reminders, tab_about) = tabs

# ══════════════════════════════════════
# PROFILE TAB
# ══════════════════════════════════════
with tab_profile:
    from tabs.tab_profile import render
    render(T, g_emoji, save_profile, load_json, PROFILES_FILE)

# ══════════════════════════════════════
# HEALTH CHECK TAB
# ══════════════════════════════════════
with tab_assess:
    from tabs.tab_assess import render
    render(T, save_record, log_patient, is_api_key_configured,
           get_gemini_advice, analyze_free_text, RECORDS_FILE)

# ══════════════════════════════════════
# EMERGENCY TAB
# ══════════════════════════════════════
with tab_emergency:
    from tabs.tab_emergency import render
    render(T)

# ══════════════════════════════════════
# MEDICINES TAB
# ══════════════════════════════════════
with tab_medicine:
    from tabs.tab_medicine import render
    render(T)

# ══════════════════════════════════════
# WOMEN'S HEALTH TAB
# ══════════════════════════════════════
with tab_women:
    from tabs.tab_women import render
    render(T)

# ══════════════════════════════════════
# DISEASES TAB
# ══════════════════════════════════════
with tab_diseases:
    from tabs.tab_diseases import render
    render(T, DISEASES, CATEGORIES, search_diseases, get_by_category)

# ══════════════════════════════════════
# SKIN AI TAB
# ══════════════════════════════════════
with tab_skin:
    from tabs.tab_skin import render
    render(T, GEMINI_API_KEY, is_api_key_configured)

# ══════════════════════════════════════
# MEDICINE SCANNER TAB
# ══════════════════════════════════════
with tab_medscan:
    from tabs.tab_medscan import render
    render(T, GEMINI_API_KEY, is_api_key_configured)

# ══════════════════════════════════════
# RESEARCH / TRENDS TAB
# ══════════════════════════════════════
with tab_research:
    from tabs.tab_research import render
    render(T, load_json, RECORDS_FILE)

# ══════════════════════════════════════
# REMINDERS TAB
# ══════════════════════════════════════
with tab_reminders:
    from tabs.tab_reminders import render
    render(T)

# ══════════════════════════════════════
# ABOUT TAB
# ══════════════════════════════════════
with tab_about:
    from tabs.tab_about import render
    render(T)

# ══════════════════════════════════════
# HIDDEN ADMIN PANEL
# Access: yourapp.streamlit.app/?admin=true
# ══════════════════════════════════════
if st.query_params.get("admin","") == "true":
    from tabs.tab_admin import render
    render(load_json, save_json, RECORDS_FILE, PROFILES_FILE, VISITORS_FILE)

st.markdown("---")
st.caption("🌿 Khareef Health v4.0 · by Sadga Selime · Salalah, Oman · Powered by Google Gemini AI · Educational use only")
