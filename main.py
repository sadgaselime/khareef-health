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
.stApp{{background:linear-gradient(150deg,{T['l']} 0%,#f9fafb 60%,{T['l']} 100%)!important;}}
.header-box{{background:linear-gradient({T['g']});border-radius:20px;padding:26px 32px;
    color:white;box-shadow:0 8px 28px {T['p']}55;margin-bottom:16px;}}
.profile-card{{background:linear-gradient({T['g']});color:white;border-radius:14px;
    padding:22px;text-align:center;}}
.step{{background:{T['l']};border-left:4px solid {T['p']};border-radius:8px;
    padding:10px 14px;margin:6px 0;font-size:0.9rem;line-height:1.6;}}
.stTabs [data-baseweb="tab-list"]{{background:white;border-radius:12px;padding:5px;
    box-shadow:0 2px 12px rgba(0,0,0,0.06);gap:4px;}}
.stTabs [aria-selected="true"]{{background:{T['p']}!important;color:white!important;}}
.stTabs [data-baseweb="tab"]{{border-radius:8px;font-weight:600;font-size:0.83rem;padding:7px 12px;}}
""" + """
.step-red{background:#fff1f2;border-left:4px solid #dc2626;border-radius:8px;
    padding:10px 14px;margin:6px 0;font-size:0.9rem;line-height:1.6;}
.ar{font-family:'Tajawal',sans-serif;direction:rtl;text-align:right;}
.disclaimer{background:#fff8e1;border:1px solid #fcd34d;border-radius:10px;
    padding:12px 18px;font-size:0.82rem;color:#78350f;}
.result-green{background:linear-gradient(135deg,#dcfce7,#bbf7d0);border:3px solid #16a34a;
    border-radius:14px;padding:22px;text-align:center;}
.result-yellow{background:linear-gradient(135deg,#fef9c3,#fde68a);border:3px solid #f59e0b;
    border-radius:14px;padding:22px;text-align:center;}
.result-red{background:linear-gradient(135deg,#fee2e2,#fecaca);border:3px solid #dc2626;
    border-radius:14px;padding:22px;text-align:center;}
.nutrition-tip{background:#f0fdf4;border-left:3px solid #22c55e;border-radius:6px;
    padding:9px 14px;margin:5px 0;font-size:0.88rem;}
@keyframes fadeUp{from{opacity:0;transform:translateY(16px);}to{opacity:1;transform:translateY(0);}}
@keyframes float{0%,100%{transform:translateY(0);}50%{transform:translateY(-6px);}}
.float{display:inline-block;animation:float 3s ease-in-out infinite;}
section[data-testid="stSidebar"]{display:none;}
#MainMenu,footer,header{visibility:hidden;}

/* ── Mobile Responsive ── */
@media (max-width: 768px) {
    .header-box{padding:16px 18px!important;}
    .header-box h1, .header-box div[style*="1.8rem"]{font-size:1.3rem!important;}
    .stTabs [data-baseweb="tab"]{font-size:0.72rem!important;padding:5px 7px!important;}
    .step, .step-red{font-size:0.82rem!important;padding:8px 10px!important;}
    div.stButton > button{font-size:1rem!important;padding:12px!important;}
    [data-testid="column"]{min-width:100%!important;}
}
@media (max-width: 480px) {
    .header-box{padding:12px 14px!important;}
    .stTabs [data-baseweb="tab"]{font-size:0.68rem!important;padding:4px 6px!important;}
}

/* ── Install Banner ── */
.install-banner{
    background:linear-gradient(135deg,#065f46,#047857);
    border-radius:12px;padding:14px 20px;color:white;
    display:flex;align-items:center;gap:14px;margin-bottom:12px;
    box-shadow:0 4px 14px rgba(6,95,70,0.3);
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════
# WELCOME SCREEN
# ══════════════════════════════════════
if not st.session_state.welcomed:
    g = T['g']
    st.markdown(f"""
    <div style="background:linear-gradient({g});border-radius:20px;padding:32px;
         color:white;text-align:center;margin-bottom:24px;">
        <div class="float" style="font-size:3rem">🌿</div>
        <div style="font-size:1.8rem;font-weight:700;margin:8px 0">Khareef Health</div>
        <div style="opacity:0.85">AI Telemedicine Triage · Salalah, Dhofar, Oman</div>
        <div class="ar" style="opacity:0.7;margin-top:4px;font-size:0.95rem">
            مساعد الفرز الطبي الذكي · صلالة، ظفار، عُمان</div>
    </div>""", unsafe_allow_html=True)

    wc1, wc2, wc3 = st.columns([1,2,1])
    with wc2:
        st.markdown("#### Please introduce yourself")
        w_name  = st.text_input("Your Name / اسمك", placeholder="e.g. Ahmed Al-Shanfari", key="wn")
        w_phone = st.text_input("Phone (optional) / الهاتف", placeholder="+968 9X XXX XXXX", key="wp")
        c1,c2 = st.columns(2)
        if c1.button("Continue / متابعة", type="primary", use_container_width=True):
            st.session_state.welcomed   = True
            st.session_state.user_name  = w_name.strip()
            st.session_state.user_phone = w_phone.strip()
            log_visitor(w_name.strip() or "Anonymous", "entered welcome")
            st.rerun()
        if c2.button("Skip / تخطي", use_container_width=True):
            st.session_state.welcomed = True
            log_visitor("Anonymous (skipped)", "skipped welcome")
            st.rerun()
    st.stop()

# ══════════════════════════════════════
# HEADER
# ══════════════════════════════════════
g_emoji = "👨" if st.session_state.gender=="Male" else "👩" if st.session_state.gender=="Female" else "🌿"
p = T['p']
st.markdown(f"""
<div class="header-box">
<div style="display:flex;align-items:center;gap:16px;flex-wrap:wrap;">
  <div class="float" style="font-size:3rem">{g_emoji}</div>
  <div style="flex:1">
    <div style="font-size:1.8rem;font-weight:700">Khareef Health</div>
    <div style="font-size:0.75rem;opacity:0.65">by Sadga Selime</div>
    <div style="font-size:0.88rem;opacity:0.82">AI Telemedicine Triage · Salalah, Dhofar, Oman</div>
    <div class="ar" style="font-size:0.85rem;opacity:0.7">مساعد الفرز الطبي الذكي · صلالة، ظفار، عُمان</div>
  </div>
  <div style="text-align:center;background:rgba(220,38,38,0.3);border-radius:12px;padding:10px 18px;">
    <div style="font-size:0.75rem;opacity:0.9">EMERGENCY</div>
    <div style="font-size:2rem;font-weight:800">999</div>
  </div>
</div>
</div>""", unsafe_allow_html=True)

# ── Install as App Banner ────────────────────────
import streamlit.components.v1 as components
components.html("""
<div id="installBanner" style="background:linear-gradient(135deg,#065f46,#047857);
     border-radius:12px;padding:14px 20px;color:white;margin-bottom:12px;
     display:flex;align-items:center;gap:14px;cursor:pointer;position:relative;"
     onclick="showInstructions()">
    <span style="font-size:1.5rem">📲</span>
    <div style="flex:1">
        <div style="font-weight:700;font-size:1rem">Install Khareef Health</div>
        <div style="font-size:0.82rem;opacity:0.85">Tap here — Add to your home screen</div>
    </div>
    <span style="font-size:1.2rem">›</span>
</div>

<!-- Instructions popup -->
<div id="popup" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,0.6);
     z-index:9999;align-items:center;justify-content:center;">
    <div style="background:white;border-radius:20px;padding:28px;max-width:340px;
         margin:20px;box-shadow:0 20px 60px rgba(0,0,0,0.3);">

        <div style="text-align:center;margin-bottom:20px;">
            <div style="font-size:2.5rem">📲</div>
            <div style="font-size:1.2rem;font-weight:700;color:#1a5c45;margin-top:8px">
                Install Khareef Health</div>
            <div style="font-size:0.85rem;color:#6b7280;margin-top:4px">
                Follow steps for your device below</div>
        </div>

        <!-- iPhone instructions -->
        <div id="iphoneSteps" style="display:none;">
            <div style="background:#f0fdf4;border-radius:12px;padding:16px;margin-bottom:12px;">
                <div style="font-weight:700;color:#1a5c45;margin-bottom:10px">
                    🍎 iPhone / iPad Steps:</div>
                <div style="font-size:0.9rem;line-height:2;color:#374151;">
                    1. Tap the <b>Share button</b> ⬆️ at the bottom of Safari<br>
                    2. Scroll down and tap <b>"Add to Home Screen"</b><br>
                    3. Tap <b>"Add"</b> in the top right corner<br>
                    4. Done! Khareef Health icon appears on home screen ✅
                </div>
            </div>
            <div style="font-size:0.8rem;color:#9ca3af;text-align:center">
                ⚠️ Must use Safari browser on iPhone</div>
        </div>

        <!-- Android instructions -->
        <div id="androidSteps" style="display:none;">
            <div style="background:#f0fdf4;border-radius:12px;padding:16px;margin-bottom:12px;">
                <div style="font-weight:700;color:#1a5c45;margin-bottom:10px">
                    🤖 Android Steps:</div>
                <div style="font-size:0.9rem;line-height:2;color:#374151;">
                    1. Tap the <b>three dots ⋮</b> menu in Chrome<br>
                    2. Tap <b>"Add to Home screen"</b><br>
                    3. Tap <b>"Add"</b> to confirm<br>
                    4. Done! Icon appears on your home screen ✅
                </div>
            </div>
        </div>

        <!-- Desktop instructions -->
        <div id="desktopSteps" style="display:none;">
            <div style="background:#f0fdf4;border-radius:12px;padding:16px;margin-bottom:12px;">
                <div style="font-weight:700;color:#1a5c45;margin-bottom:10px">
                    💻 Desktop (Chrome) Steps:</div>
                <div style="font-size:0.9rem;line-height:2;color:#374151;">
                    1. Look for the <b>install icon ⊕</b> in the address bar<br>
                    2. Click it and select <b>"Install"</b><br>
                    3. Or click three dots ⋮ → <b>"Install Khareef Health"</b><br>
                    4. Done! App opens like a desktop application ✅
                </div>
            </div>
        </div>

        <!-- Share link -->
        <div style="background:#eff6ff;border-radius:12px;padding:14px;margin-bottom:16px;">
            <div style="font-size:0.82rem;font-weight:600;color:#1e40af;margin-bottom:6px">
                📋 App Link — Copy and Share:</div>
            <div id="appUrl" style="background:white;border-radius:8px;padding:8px 12px;
                 font-size:0.75rem;color:#374151;word-break:break-all;
                 border:1px solid #bfdbfe;cursor:pointer;"
                 onclick="copyLink()">
                khareef-health-6ni9nxypihjhpwsq4nohmw.streamlit.app
            </div>
            <div id="copiedMsg" style="display:none;color:#16a34a;font-size:0.8rem;
                 margin-top:4px;text-align:center">✅ Copied!</div>
        </div>

        <button onclick="closePopup()" style="width:100%;background:#1a5c45;color:white;
            border:none;border-radius:10px;padding:12px;font-size:1rem;
            font-weight:700;cursor:pointer;">
            Got it! ✓
        </button>
    </div>
</div>

<script>
function showInstructions() {
    document.getElementById('popup').style.display = 'flex';
    var ua = navigator.userAgent.toLowerCase();
    if (/iphone|ipad|ipod/.test(ua)) {
        document.getElementById('iphoneSteps').style.display = 'block';
    } else if (/android/.test(ua)) {
        document.getElementById('androidSteps').style.display = 'block';
    } else {
        document.getElementById('desktopSteps').style.display = 'block';
    }
    // Try native install prompt (Chrome Android/Desktop)
    if (window.deferredPrompt) {
        window.deferredPrompt.prompt();
        window.deferredPrompt.userChoice.then(function() {
            window.deferredPrompt = null;
        });
    }
}
function closePopup() {
    document.getElementById('popup').style.display = 'none';
}
function copyLink() {
    var url = 'khareef-health-6ni9nxypihjhpwsq4nohmw.streamlit.app';
    navigator.clipboard.writeText(url).then(function() {
        document.getElementById('copiedMsg').style.display = 'block';
        setTimeout(function() {
            document.getElementById('copiedMsg').style.display = 'none';
        }, 2000);
    });
}
// Listen for native install prompt
window.addEventListener('beforeinstallprompt', function(e) {
    e.preventDefault();
    window.deferredPrompt = e;
});
</script>
""", height=80)

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
