import streamlit as st

st.set_page_config(
    page_title="Khareef Health",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",
)

import os, json, uuid, urllib.parse
from datetime import datetime
import streamlit.components.v1 as components

# ── Optional imports ──────────────────────────────
try:
    from data import Patient, validate_patient_input, normalize_symptoms, log_patient
    DATA_AVAILABLE = True
except ImportError:
    DATA_AVAILABLE = False

try:
    from triage import assess_patient
    TRIAGE_AVAILABLE = True
except ImportError:
    TRIAGE_AVAILABLE = False

try:
    from gemini_helper import (
        get_gemini_advice, analyze_free_text,
        is_api_key_configured, get_api_key_status, GEMINI_API_KEY
    )
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    def is_api_key_configured(): return False
    def get_gemini_advice(*a, **kw): return "AI not configured."
    def analyze_free_text(*a, **kw): return "AI not configured."
    GEMINI_API_KEY = ""

try:
    from diseases import DISEASES, CATEGORIES, search_diseases, get_by_category
    DISEASES_AVAILABLE = True
except ImportError:
    DISEASES_AVAILABLE = False
    DISEASES, CATEGORIES = [], []
    def search_diseases(q): return []
    def get_by_category(c): return []

try:
    from translations import t, LANGUAGES, get_lang_code, get_tts_code
    from voice_utils import voice_input_component, text_to_speech_component
    VOICE_ENABLED = True
except ImportError:
    VOICE_ENABLED = False
    def t(key, lang="English"): return key.replace("_", " ").title()

# ── Storage ───────────────────────────────────────
RECORDS_FILE  = "user_records.json"
PROFILES_FILE = "user_profiles.json"
VISITORS_FILE = "visitors.json"

def load_json(f):
    if os.path.exists(f):
        try: return json.load(open(f))
        except: return []
    return []

def save_json(f, d):
    json.dump(d, open(f, "w"), indent=2, ensure_ascii=False)

def save_record(r):
    d = load_json(RECORDS_FILE); d.append(r); save_json(RECORDS_FILE, d)

def save_profile(p):
    d = load_json(PROFILES_FILE)
    for i, x in enumerate(d):
        if x.get("name","").lower() == p["name"].lower():
            d[i] = p; save_json(PROFILES_FILE, d); return
    d.append(p); save_json(PROFILES_FILE, d)

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
for k, v in DEFAULTS.items():
    if k not in st.session_state: st.session_state[k] = v

# ── Profile persistence via URL params ────────────
params = st.query_params
if params.get("kn") and not st.session_state.profile_restored:
    st.session_state.user_name        = urllib.parse.unquote(params.get("kn",""))
    st.session_state.user_phone       = urllib.parse.unquote(params.get("kp",""))
    st.session_state.user_city        = urllib.parse.unquote(params.get("kc","Salalah"))
    st.session_state.gender           = urllib.parse.unquote(params.get("kg","Not specified"))
    st.session_state.user_blood_type  = urllib.parse.unquote(params.get("kb","Unknown"))
    st.session_state.user_medications = urllib.parse.unquote(params.get("km",""))
    try: st.session_state.language    = urllib.parse.unquote(params.get("kl","English"))
    except: pass
    try: st.session_state.user_age    = int(params.get("ka", 40))
    except: pass
    try: st.session_state.user_conditions = json.loads(urllib.parse.unquote(params.get("kco","[]")))
    except: pass
    st.session_state.profile_restored = True
    st.session_state.welcomed = True
    st.query_params.clear()

components.html("""
<script>
(function() {
    try {
        if (sessionStorage.getItem('kh_loaded') === '1') return;
        var url = new URL(window.parent.location.href);
        if (url.searchParams.get('kn')) { sessionStorage.setItem('kh_loaded','1'); return; }
        var saved = localStorage.getItem('khareef_profile');
        if (!saved) return;
        var p; try { p = JSON.parse(saved); } catch(e) { return; }
        if (!p || !p.name) return;
        sessionStorage.setItem('kh_loaded','1');
        url.searchParams.set('kn', encodeURIComponent(p.name||''));
        url.searchParams.set('kp', encodeURIComponent(p.phone||''));
        url.searchParams.set('ka', p.age||40);
        url.searchParams.set('kg', encodeURIComponent(p.gender||'Not specified'));
        url.searchParams.set('kc', encodeURIComponent(p.city||'Salalah'));
        url.searchParams.set('kb', encodeURIComponent(p.blood_type||'Unknown'));
        url.searchParams.set('km', encodeURIComponent(p.medications||''));
        url.searchParams.set('kl', encodeURIComponent(p.language||'English'));
        url.searchParams.set('kco', encodeURIComponent(JSON.stringify(p.conditions||[])));
        window.parent.history.replaceState({}, '', url.toString());
        window.parent.location.reload();
    } catch(e) {}
})();
</script>
""", height=0)

def save_to_localstorage():
    profile_json = json.dumps({
        "name":       st.session_state.user_name,
        "phone":      st.session_state.user_phone,
        "age":        st.session_state.user_age,
        "gender":     st.session_state.gender,
        "city":       st.session_state.user_city,
        "blood_type": st.session_state.user_blood_type,
        "medications":st.session_state.user_medications,
        "language":   st.session_state.language,
        "conditions": st.session_state.user_conditions,
    }, ensure_ascii=False)
    components.html(f"""
    <script>
    try {{
        localStorage.setItem('khareef_profile', {json.dumps(profile_json)});
        sessionStorage.setItem('kh_loaded','1');
    }} catch(e) {{}}
    </script>
    """, height=0)

# ── Theme colors ──────────────────────────────────
THEMES = {
    "Male":          {"p":"#1a4a8a","s":"#2d6fba","l":"#dbeafe","dark":"#0d2d5c",
                      "a":"#0d2d5c","g":"135deg,#0d2d5c,#1a4a8a,#2d6fba",
                      "g1":"#0d2d5c","g2":"#1a4a8a","g3":"#2d6fba","accent":"#60a5fa"},
    "Female":        {"p":"#9d174d","s":"#db2777","l":"#fce7f3","dark":"#500724",
                      "a":"#500724","g":"135deg,#500724,#9d174d,#db2777",
                      "g1":"#500724","g2":"#9d174d","g3":"#db2777","accent":"#f9a8d4"},
    "Not specified": {"p":"#1a5c45","s":"#2d8a65","l":"#d1fae5","dark":"#0d3d29",
                      "a":"#0d3d29","g":"135deg,#0d3d29,#1a5c45,#2d8a65",
                      "g1":"#0d3d29","g2":"#1a5c45","g3":"#2d8a65","accent":"#6ee7b7"},
}
T = THEMES[st.session_state.gender]

# ══════════════════════════════════════════════════
# GLOBAL CSS — Full redesign
# ══════════════════════════════════════════════════
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Tajawal:wght@400;500;700&display=swap');

/* ── Reset & Base ── */
*, *::before, *::after {{ box-sizing: border-box; }}
html, body, [class*="css"] {{
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 14px;
    line-height: 1.6;
}}
#MainMenu, footer, header {{ visibility: hidden; }}
section[data-testid="stSidebar"] {{ display: none; }}
.stApp {{ background: #f4f6f4; }}
.block-container {{ padding: 1rem 1.5rem 3rem !important; max-width: 960px !important; }}

/* ── Header ── */
.kh-header {{
    background: linear-gradient(135deg, {T['g1']} 0%, {T['g2']} 45%, {T['g3']} 100%);
    border-radius: 20px;
    padding: 22px 28px 16px;
    color: white;
    margin-bottom: 14px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 8px 32px {T['p']}40;
}}
.kh-header::before {{
    content: '';
    position: absolute;
    top: -40px; right: -40px;
    width: 180px; height: 180px;
    border-radius: 50%;
    background: rgba(255,255,255,0.06);
    pointer-events: none;
}}
.kh-header::after {{
    content: '';
    position: absolute;
    bottom: -30px; left: 20%;
    width: 120px; height: 120px;
    border-radius: 50%;
    background: rgba(255,255,255,0.04);
    pointer-events: none;
}}
.kh-header-inner {{
    display: flex;
    align-items: center;
    gap: 18px;
    position: relative;
    z-index: 1;
    flex-wrap: wrap;
}}
.kh-logo {{
    width: 54px; height: 54px;
    border-radius: 16px;
    background: rgba(255,255,255,0.15);
    backdrop-filter: blur(4px);
    display: flex; align-items: center; justify-content: center;
    font-size: 26px;
    border: 1.5px solid rgba(255,255,255,0.25);
    flex-shrink: 0;
    animation: kh-float 3.5s ease-in-out infinite;
}}
@keyframes kh-float {{
    0%,100% {{ transform: translateY(0); }}
    50% {{ transform: translateY(-5px); }}
}}
.kh-header-text {{ flex: 1; min-width: 0; }}
.kh-header-text h1 {{
    font-size: 22px; font-weight: 800;
    margin: 0 0 3px; letter-spacing: -0.3px;
}}
.kh-header-text .kh-sub {{
    font-size: 11px; opacity: 0.7;
    letter-spacing: 1px; text-transform: uppercase;
    margin: 0;
}}
.kh-header-text .kh-arabic {{
    font-family: 'Tajawal', sans-serif;
    font-size: 12px; opacity: 0.6;
    direction: rtl; margin-top: 2px;
}}
.kh-badge-row {{
    display: flex; gap: 8px; align-items: center;
    flex-wrap: wrap;
}}
.kh-badge {{
    background: rgba(255,255,255,0.15);
    border: 1px solid rgba(255,255,255,0.2);
    border-radius: 8px;
    padding: 4px 10px;
    font-size: 10px; font-weight: 700;
    letter-spacing: 0.8px; text-transform: uppercase;
}}
.kh-emergency {{
    background: rgba(220,38,38,0.75);
    border: 1px solid rgba(255,100,100,0.4);
    border-radius: 12px;
    padding: 10px 16px;
    text-align: center;
    flex-shrink: 0;
    backdrop-filter: blur(4px);
}}
.kh-emergency .em-label {{
    font-size: 9px; letter-spacing: 2px;
    opacity: 0.9; display: block; margin-bottom: 2px;
}}
.kh-emergency .em-num {{
    font-size: 24px; font-weight: 900;
    letter-spacing: 2px; display: block;
}}
.kh-ecg {{
    width: 100%; height: 20px;
    margin-top: 12px; opacity: 0.2;
}}

/* ── Settings strip ── */
.kh-settings {{
    background: white;
    border-radius: 14px;
    padding: 12px 16px;
    margin-bottom: 14px;
    display: flex;
    gap: 10px;
    align-items: center;
    flex-wrap: wrap;
    border: 1px solid #e8ede8;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}}
.kh-settings .stSelectbox, .kh-settings .stToggle {{
    flex: 1;
    min-width: 120px;
}}

/* ── Greeting banner ── */
.kh-greeting {{
    background: linear-gradient(135deg, {T['g2']} 0%, {T['g3']} 100%);
    border-radius: 16px;
    padding: 18px 22px;
    color: white;
    margin-bottom: 14px;
    display: flex;
    align-items: center;
    gap: 16px;
    animation: kh-fadein 0.5s ease;
    box-shadow: 0 4px 18px {T['p']}35;
}}
@keyframes kh-fadein {{
    from {{ opacity: 0; transform: translateY(8px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}
.kh-greeting-avatar {{
    width: 52px; height: 52px;
    border-radius: 50%;
    background: rgba(255,255,255,0.2);
    display: flex; align-items: center; justify-content: center;
    font-size: 26px;
    border: 2px solid rgba(255,255,255,0.3);
    flex-shrink: 0;
}}
.kh-greeting-text h2 {{
    font-size: 17px; font-weight: 700; margin: 0 0 4px;
}}
.kh-greeting-text p {{
    font-size: 12px; opacity: 0.85; margin: 0;
}}

/* ── Stat cards ── */
.kh-stats {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
    margin-bottom: 16px;
}}
.kh-stat {{
    background: white;
    border-radius: 14px;
    padding: 14px 10px;
    text-align: center;
    border: 1px solid #e8ede8;
    cursor: pointer;
    transition: all 0.18s ease;
    box-shadow: 0 2px 6px rgba(0,0,0,0.04);
}}
.kh-stat:hover {{
    transform: translateY(-3px);
    box-shadow: 0 6px 18px rgba(0,0,0,0.10);
    border-color: {T['s']}55;
}}
.kh-stat .st-ico {{ font-size: 22px; margin-bottom: 7px; }}
.kh-stat .st-lbl {{
    font-size: 10px; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.6px;
    margin-bottom: 2px;
}}
.kh-stat .st-sub {{ font-size: 10px; color: #777; }}

/* ── Section label ── */
.kh-section-label {{
    font-size: 10px; font-weight: 700;
    text-transform: uppercase; letter-spacing: 1.2px;
    color: #888; margin: 0 0 8px 2px;
}}

/* ── Khareef banner ── */
.kh-khareef-banner {{
    background: #fffbeb;
    border: 1px solid #fcd34d;
    border-radius: 12px;
    padding: 10px 16px;
    font-size: 12px;
    color: #78350f;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 10px;
    font-weight: 500;
}}

/* ── Form cards ── */
.kh-card {{
    background: white;
    border-radius: 16px;
    padding: 20px;
    border: 1px solid #e8ede8;
    margin-bottom: 14px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}}

/* ── Vitals row ── */
.kh-vitals {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
    margin-bottom: 14px;
}}
.kh-vital {{
    background: white;
    border-radius: 14px;
    padding: 14px;
    text-align: center;
    border: 1px solid #e8ede8;
    box-shadow: 0 2px 6px rgba(0,0,0,0.04);
}}
.kh-vital-label {{
    font-size: 10px; font-weight: 600;
    color: #888; text-transform: uppercase;
    letter-spacing: 0.6px; margin-bottom: 6px;
}}
.kh-vital-value {{
    font-size: 28px; font-weight: 800;
    color: {T['p']}; line-height: 1;
    margin-bottom: 4px;
}}
.kh-vital-unit {{
    font-size: 11px; color: #aaa;
}}
.kh-vital-bar {{
    height: 3px; border-radius: 99px;
    margin-top: 10px;
}}
.kh-vital-bar.normal {{ background: #16a34a; }}
.kh-vital-bar.warning {{ background: #f59e0b; }}
.kh-vital-bar.danger {{ background: #dc2626; }}

/* ── Symptom chips ── */
.kh-chips {{
    display: flex;
    flex-wrap: wrap;
    gap: 7px;
    margin-bottom: 14px;
}}
.kh-chip {{
    padding: 6px 13px;
    border-radius: 99px;
    font-size: 12px;
    font-weight: 500;
    cursor: pointer;
    border: 1.5px solid #e0e7e0;
    color: #555;
    background: white;
    transition: all 0.15s ease;
    user-select: none;
}}
.kh-chip:hover {{
    border-color: {T['s']};
    color: {T['p']};
    background: {T['l']};
}}

/* ── Result cards ── */
.kh-result {{
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 12px;
    animation: kh-fadein 0.4s ease;
}}
.kh-result.green {{
    background: linear-gradient(135deg, #dcfce7, #bbf7d0);
    border: 2px solid #16a34a;
}}
.kh-result.yellow {{
    background: linear-gradient(135deg, #fef9c3, #fde68a);
    border: 2px solid #f59e0b;
}}
.kh-result.red {{
    background: linear-gradient(135deg, #fee2e2, #fecaca);
    border: 2px solid #dc2626;
}}
.kh-result-head {{
    display: flex; align-items: center;
    gap: 10px; margin-bottom: 14px;
}}
.kh-level-badge {{
    padding: 4px 14px;
    border-radius: 99px;
    font-size: 11px; font-weight: 800;
    letter-spacing: 1px;
    color: white;
}}
.kh-level-badge.green {{ background: #16a34a; }}
.kh-level-badge.yellow {{ background: #d97706; }}
.kh-level-badge.red {{ background: #dc2626; }}
.kh-result-title {{
    font-size: 15px; font-weight: 700;
}}
.kh-result.green .kh-result-title {{ color: #065f46; }}
.kh-result.yellow .kh-result-title {{ color: #78350f; }}
.kh-result.red .kh-result-title {{ color: #7f1d1d; }}

/* ── Steps ── */
.kh-steps {{ display: flex; flex-direction: column; gap: 6px; }}
.kh-step {{
    display: flex; gap: 10px; align-items: flex-start;
    padding: 9px 12px;
    border-radius: 10px;
    font-size: 13px;
    line-height: 1.5;
}}
.kh-step.g {{ background: rgba(22,163,74,0.12); color: #065f46; }}
.kh-step.y {{ background: rgba(217,119,6,0.12); color: #78350f; }}
.kh-step.r {{ background: rgba(220,38,38,0.12); color: #7f1d1d; }}
.kh-step-num {{
    width: 20px; height: 20px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 10px; font-weight: 800;
    flex-shrink: 0; margin-top: 1px;
    color: white;
}}
.kh-step.g .kh-step-num {{ background: #16a34a; }}
.kh-step.y .kh-step-num {{ background: #d97706; }}
.kh-step.r .kh-step-num {{ background: #dc2626; }}

/* ── Arabic panel ── */
.kh-arabic-panel {{
    background: #fffbf0;
    border-right: 4px solid {T['p']};
    border-radius: 10px;
    padding: 14px 16px;
    margin-top: 10px;
}}
.kh-arabic-panel .ar-label {{
    font-size: 10px; font-weight: 700;
    letter-spacing: 1px; color: #888;
    text-transform: uppercase; margin-bottom: 7px;
}}
.kh-arabic-panel .ar-text {{
    font-family: 'Tajawal', sans-serif;
    direction: rtl; text-align: right;
    font-size: 14px; line-height: 1.9;
    color: #3d3d3d;
}}

/* ── Emergency tab ── */
.kh-emergency-main {{
    background: linear-gradient(135deg, #fee2e2, #fecaca);
    border: 2px solid #dc2626;
    border-radius: 18px;
    padding: 28px;
    text-align: center;
    margin-bottom: 14px;
}}
.kh-emergency-num {{
    font-size: 64px; font-weight: 900;
    color: #dc2626; line-height: 1;
    letter-spacing: 4px;
}}
.kh-hospital-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
}}
.kh-hospital {{
    background: white;
    border: 1px solid #e8ede8;
    border-radius: 14px;
    padding: 16px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.04);
}}
.kh-hospital .h-name {{
    font-size: 12px; font-weight: 700;
    color: #444; margin-bottom: 6px;
}}
.kh-hospital .h-phone {{
    font-size: 15px; font-weight: 700;
    color: {T['p']}; margin-bottom: 4px;
}}
.kh-hospital .h-addr {{
    font-size: 11px; color: #888;
}}

/* ── Skin/Med upload ── */
.kh-upload-zone {{
    background: white;
    border: 2px dashed #c8d5c8;
    border-radius: 16px;
    padding: 40px 20px;
    text-align: center;
    margin-bottom: 14px;
    transition: all 0.2s ease;
    cursor: pointer;
}}
.kh-upload-zone:hover {{
    border-color: {T['s']};
    background: {T['l']}40;
}}
.kh-upload-icon {{ font-size: 42px; margin-bottom: 12px; }}
.kh-upload-title {{
    font-size: 15px; font-weight: 700;
    color: #333; margin-bottom: 6px;
}}
.kh-upload-sub {{ font-size: 12px; color: #888; }}

/* ── Disclaimer ── */
.kh-disclaimer {{
    background: #fff8e1;
    border: 1px solid #fcd34d;
    border-radius: 12px;
    padding: 11px 16px;
    font-size: 11px;
    color: #78350f;
    margin: 12px 0;
    line-height: 1.6;
}}

/* ── Primary button ── */
div.stButton > button {{
    background: linear-gradient(135deg, {T['g2']}, {T['g3']}) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    font-size: 13px !important;
    padding: 10px 20px !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 14px {T['p']}40 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}}
div.stButton > button:hover {{
    transform: translateY(-2px) !important;
    box-shadow: 0 7px 20px {T['p']}55 !important;
    opacity: 0.95 !important;
}}

/* ── Streamlit inputs ── */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stSelectbox > div > div > div,
.stTextArea textarea {{
    border-radius: 10px !important;
    border: 1.5px solid #dde5dd !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 13px !important;
    transition: border-color 0.15s !important;
}}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus,
.stTextArea textarea:focus {{
    border-color: {T['s']} !important;
    box-shadow: 0 0 0 3px {T['l']} !important;
}}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {{
    background: white !important;
    border-radius: 14px !important;
    padding: 5px !important;
    gap: 3px !important;
    box-shadow: 0 2px 10px rgba(0,0,0,0.06) !important;
    border: 1px solid #e8ede8 !important;
}}
.stTabs [data-baseweb="tab"] {{
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 12px !important;
    padding: 7px 13px !important;
    color: #666 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}}
.stTabs [aria-selected="true"] {{
    background: linear-gradient(135deg, {T['g2']}, {T['g3']}) !important;
    color: white !important;
    box-shadow: 0 3px 10px {T['p']}40 !important;
}}
.stTabs [data-baseweb="tab-highlight"] {{ display: none !important; }}
.stTabs [data-baseweb="tab-border"] {{ display: none !important; }}

/* ── Metrics ── */
[data-testid="stMetricValue"] {{
    color: {T['p']} !important;
    font-weight: 800 !important;
    font-size: 26px !important;
}}
[data-testid="stMetricLabel"] {{
    font-weight: 600 !important;
    font-size: 11px !important;
    text-transform: uppercase !important;
    letter-spacing: 0.8px !important;
    color: #888 !important;
}}

/* ── Expander ── */
.streamlit-expanderHeader {{
    background: white !important;
    border-radius: 12px !important;
    border: 1px solid #e8ede8 !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}}
.streamlit-expanderContent {{
    background: white !important;
    border: 1px solid #e8ede8 !important;
    border-top: none !important;
    border-radius: 0 0 12px 12px !important;
    padding: 16px !important;
}}

/* ── Toggle ── */
.stToggle > label {{
    font-weight: 600 !important;
    font-size: 12px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}}

/* ── Alert/info ── */
.stAlert {{
    border-radius: 12px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 13px !important;
}}

/* ── Welcome screen ── */
.kh-welcome {{
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 20px;
}}
.kh-welcome-card {{
    background: white;
    border-radius: 24px;
    padding: 36px 32px;
    max-width: 440px;
    width: 100%;
    box-shadow: 0 20px 60px rgba(0,0,0,0.12);
    border: 1px solid #e8ede8;
}}
.kh-welcome-hero {{
    background: linear-gradient(135deg, {T['g1']}, {T['g3']});
    border-radius: 16px;
    padding: 28px;
    text-align: center;
    color: white;
    margin-bottom: 24px;
}}
.kh-welcome-hero .hero-icon {{
    font-size: 48px;
    animation: kh-float 3s ease-in-out infinite;
    display: block;
    margin-bottom: 12px;
}}
.kh-welcome-hero h2 {{
    font-size: 24px;
    font-weight: 800;
    margin: 0 0 6px;
}}
.kh-welcome-hero p {{
    font-size: 12px;
    opacity: 0.8;
    margin: 0;
}}

/* ── Divider ── */
hr {{ border: none; border-top: 1px solid #e8ede8; margin: 14px 0; }}

/* ── Disease cards ── */
.kh-disease-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    margin-bottom: 14px;
}}
.kh-disease-card {{
    background: white;
    border: 1px solid #e8ede8;
    border-radius: 14px;
    padding: 16px;
    cursor: pointer;
    transition: all 0.18s ease;
    box-shadow: 0 2px 6px rgba(0,0,0,0.04);
}}
.kh-disease-card:hover {{
    transform: translateY(-2px);
    border-color: {T['s']}66;
    box-shadow: 0 6px 18px rgba(0,0,0,0.09);
}}

/* ── Trends ── */
.kh-trend-history {{
    background: white;
    border-radius: 14px;
    border: 1px solid #e8ede8;
    overflow: hidden;
    box-shadow: 0 2px 6px rgba(0,0,0,0.04);
}}
.kh-trend-row {{
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 16px;
    border-bottom: 1px solid #f0f4f0;
    font-size: 13px;
}}
.kh-trend-row:last-child {{ border-bottom: none; }}
.kh-level-pill {{
    padding: 3px 10px;
    border-radius: 99px;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 0.5px;
    color: white;
    flex-shrink: 0;
}}
.kh-level-pill.green {{ background: #16a34a; }}
.kh-level-pill.yellow {{ background: #d97706; }}
.kh-level-pill.red {{ background: #dc2626; }}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════
# WELCOME SCREEN
# ══════════════════════════════════════
if not st.session_state.welcomed:
    T_cur = THEMES[st.session_state.gender]
    is_returning = bool(st.session_state.user_name)

    if is_returning and st.session_state.profile_restored:
        st.session_state.welcomed = True
        log_visitor(st.session_state.user_name, "auto-login returning user")
        st.rerun()

    elif is_returning:
        wc1, wc2, wc3 = st.columns([1, 2, 1])
        with wc2:
            st.markdown(f"""
            <div class="kh-welcome-hero" style="margin-bottom:20px;border-radius:20px">
                <span class="hero-icon">👋</span>
                <h2>Welcome back!</h2>
                <p style="font-size:16px;margin-top:6px;opacity:1;font-weight:700">{st.session_state.user_name}</p>
                <p>Your profile has been restored</p>
            </div>""", unsafe_allow_html=True)
            if st.button("Continue →", type="primary", use_container_width=True, key="wbtn_ret"):
                st.session_state.welcomed = True
                log_visitor(st.session_state.user_name, "returning user")
                st.rerun()
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            if st.button("Not you? Start fresh", use_container_width=True, key="wfresh"):
                for k in list(DEFAULTS.keys()):
                    st.session_state[k] = DEFAULTS[k]
                st.query_params.clear()
                components.html("""
                <script>
                localStorage.removeItem('khareef_profile');
                sessionStorage.removeItem('kh_loaded');
                </script>""", height=0)
                st.rerun()
    else:
        wc1, wc2, wc3 = st.columns([1, 2, 1])
        with wc2:
            st.markdown(f"""
            <div class="kh-welcome-hero">
                <span class="hero-icon">🌿</span>
                <h2>Khareef Health</h2>
                <p>AI Telemedicine Triage · Salalah, Oman</p>
                <p style="font-family:'Tajawal',sans-serif;direction:rtl;margin-top:6px;font-size:13px">
                    مساعد الفرز الطبي الذكي · صلالة، ظفار، عُمان</p>
            </div>""", unsafe_allow_html=True)

            st.markdown("#### Introduce yourself 👋")

            lang_opts = ["English", "العربية", "বাংলা"]
            lang_labels = {"English":"🇬🇧 English","العربية":"🇴🇲 العربية","বাংলা":"🇧🇩 বাংলা"}
            w_lang = st.selectbox("Language", lang_opts,
                index=lang_opts.index(st.session_state.language) if st.session_state.language in lang_opts else 0,
                format_func=lambda x: lang_labels[x], key="welcome_lang")
            if w_lang != st.session_state.language:
                st.session_state.language = w_lang

            w_name   = st.text_input("Your Name / اسمك", placeholder="e.g. Ahmed Al-Shanfari", key="wn")
            w_phone  = st.text_input("Phone (optional)", placeholder="+968 9X XXX XXXX", key="wp")
            w_gender = st.selectbox("Gender / الجنس", ["Not specified","Male","Female"],
                index=["Not specified","Male","Female"].index(st.session_state.gender), key="wg")

            c1, c2 = st.columns(2)
            if c1.button("Continue →", type="primary", use_container_width=True, key="wbtn"):
                st.session_state.welcomed   = True
                st.session_state.user_name  = w_name.strip()
                st.session_state.user_phone = w_phone.strip()
                st.session_state.gender     = w_gender
                st.session_state.language   = w_lang
                log_visitor(w_name.strip() or "Anonymous", "first visit")
                save_to_localstorage()
                st.rerun()
            if c2.button("Skip", use_container_width=True, key="wskip"):
                st.session_state.welcomed  = True
                st.session_state.language  = w_lang
                st.session_state.gender    = w_gender
                log_visitor("Anonymous (skipped)", "skipped welcome")
                st.rerun()

            st.markdown("""<p style="text-align:center;font-size:11px;color:#888;margin-top:12px">
                🔒 Your data is stored only on your device</p>""", unsafe_allow_html=True)
    st.stop()

# ══════════════════════════════════════
# MAIN APP
# ══════════════════════════════════════

# ── Header ────────────────────────────────────────
T = THEMES[st.session_state.gender]
g_emoji = "👨" if st.session_state.gender=="Male" else "👩" if st.session_state.gender=="Female" else "🌿"

st.markdown(f"""
<div class="kh-header">
  <div class="kh-header-inner">
    <div class="kh-logo">{g_emoji}</div>
    <div class="kh-header-text">
      <h1>Khareef Health</h1>
      <p class="kh-sub">AI · Salalah, Dhofar, Oman</p>
      <p class="kh-arabic">مساعد الفرز الطبي الذكي · صلالة، ظفار، عُمان</p>
      <div class="kh-badge-row" style="margin-top:8px">
        <span class="kh-badge">🤖 AI Powered</span>
        <span class="kh-badge">🩺 Triage</span>
        <span class="kh-badge">📸 Skin AI</span>
        <span class="kh-badge">🦠 Diseases</span>
      </div>
    </div>
    <div class="kh-emergency">
      <span class="em-label">EMERGENCY</span>
      <span class="em-num">999</span>
    </div>
  </div>
  <svg class="kh-ecg" viewBox="0 0 500 20" fill="none">
    <path d="M0 10 L80 10 L95 2 L105 18 L115 5 L125 15 L135 10 L500 10"
          stroke="white" stroke-width="2.5" stroke-linecap="round"/>
  </svg>
</div>
""", unsafe_allow_html=True)

# ── Settings row ──────────────────────────────────
lang_opts = ["English","العربية","বাংলা"]

s1, s2, s3, s4, s5 = st.columns([1.4, 1.4, 0.9, 0.9, 0.9])
with s1:
    new_g = st.selectbox("Theme", ["Not specified","Male","Female"],
        index=["Not specified","Male","Female"].index(st.session_state.gender), key="gs",
        label_visibility="collapsed")
    if new_g != st.session_state.gender:
        st.session_state.gender = new_g
        save_to_localstorage()
        st.rerun()
    icons = {"Male":"💙 Blue theme","Female":"💗 Rose theme","Not specified":"💚 Green theme"}
    st.caption(icons[st.session_state.gender])

with s2:
    curr_idx = lang_opts.index(st.session_state.language) if st.session_state.language in lang_opts else 0
    new_lang = st.selectbox("Language", lang_opts, index=curr_idx, key="lang_sel",
        label_visibility="collapsed")
    if new_lang != st.session_state.language:
        st.session_state.language = new_lang
        save_to_localstorage()
        st.rerun()
    st.caption({"English":"🇬🇧 English","العربية":"🇴🇲 Arabic","বাংলা":"🇧🇩 Bengali"}[st.session_state.language])

with s3:
    st.session_state.khareef = st.toggle("🌦️ Khareef", value=st.session_state.khareef, key="kt")
with s4:
    st.session_state.show_arabic = st.toggle("📖 Arabic", value=st.session_state.show_arabic, key="at")
with s5:
    st.session_state.use_ai = st.toggle("🤖 AI", value=st.session_state.use_ai, key="git")

if st.session_state.khareef:
    st.markdown("""
    <div class="kh-khareef-banner">
        🌦️ <strong>Khareef Mode ON</strong> — Higher respiratory sensitivity. Extra caution for mold, humidity and mosquito-borne diseases.
    </div>""", unsafe_allow_html=True)

# ── Greeting ──────────────────────────────────────
if st.session_state.user_name and st.session_state.profile_restored:
    h = datetime.now().hour
    greeting = "Good morning" if h < 12 else "Good afternoon" if h < 18 else "Good evening"
    if st.session_state.show_arabic:
        ar_greet = "صباح الخير" if h < 12 else "مساء الخير"
        greeting = f"{greeting} · {ar_greet}"
    conds_str = f" · {', '.join(st.session_state.user_conditions[:2])}" if st.session_state.user_conditions else ""
    st.markdown(f"""
    <div class="kh-greeting">
      <div class="kh-greeting-avatar">{g_emoji}</div>
      <div class="kh-greeting-text">
        <h2>{greeting}, {st.session_state.user_name}!</h2>
        <p>Age {st.session_state.user_age} · {st.session_state.user_city} · Blood {st.session_state.user_blood_type}{conds_str}</p>
        <p style="margin-top:4px;font-size:11px;opacity:0.8">Your profile is loaded and ready 🩺</p>
      </div>
    </div>""", unsafe_allow_html=True)

# ── Quick stat cards ───────────────────────────────
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown("""<div class="kh-stat">
        <div class="st-ico">❤️</div>
        <div class="st-lbl" style="color:#dc2626">Emergency</div>
        <div class="st-sub">Call 999</div></div>""", unsafe_allow_html=True)
    if st.button("ℹ️ Info", key="cem", use_container_width=True):
        st.session_state.show_card_info = "emergency" if st.session_state.show_card_info!="emergency" else None

with col2:
    st.markdown(f"""<div class="kh-stat">
        <div class="st-ico">🩺</div>
        <div class="st-lbl" style="color:{T['p']}">AI Triage</div>
        <div class="st-sub">Green · Yellow · Red</div></div>""", unsafe_allow_html=True)
    if st.button("ℹ️ Info", key="ctr", use_container_width=True):
        st.session_state.show_card_info = "triage" if st.session_state.show_card_info!="triage" else None

with col3:
    st.markdown("""<div class="kh-stat">
        <div class="st-ico">🌐</div>
        <div class="st-lbl" style="color:#1e40af">Multilingual</div>
        <div class="st-sub">EN · AR · BN</div></div>""", unsafe_allow_html=True)
    if st.button("ℹ️ Info", key="cla", use_container_width=True):
        st.session_state.show_card_info = "bilingual" if st.session_state.show_card_info!="bilingual" else None

with col4:
    st.markdown("""<div class="kh-stat">
        <div class="st-ico">🌦️</div>
        <div class="st-lbl" style="color:#92400e">Khareef</div>
        <div class="st-sub">Salalah Season</div></div>""", unsafe_allow_html=True)
    if st.button("ℹ️ Info", key="ckh", use_container_width=True):
        st.session_state.show_card_info = "khareef" if st.session_state.show_card_info!="khareef" else None

# Info panels
if st.session_state.show_card_info == "emergency":
    with st.expander("🚨 Emergency Contacts — Salalah", expanded=True):
        c1, c2, c3 = st.columns(3)
        with c1: st.error("**Ambulance / Police**\n\n999\n\n24 hours")
        with c2: st.info("**Sultan Qaboos Hospital**\n\n+968 23 211 555\n\nAl Dahariz, Salalah")
        with c3: st.info("**Badr Al Samaa**\n\n+968 23 219 999\n\n24 hours · Private")
elif st.session_state.show_card_info == "triage":
    with st.expander("🩺 How AI Triage Works", expanded=True):
        st.markdown("""
| Level | Meaning | Action |
|---|---|---|
| 🟢 GREEN | All readings normal | Rest at home |
| 🟡 YELLOW | Mild concern | See doctor soon |
| 🔴 RED | Urgent concern | Go to hospital NOW |

Google Gemini AI gives personalised advice in English and Arabic.""")
elif st.session_state.show_card_info == "bilingual":
    with st.expander("🌐 Multilingual Support", expanded=True):
        st.success("Full English, Arabic, and Bengali support.")
        st.markdown('<div class="kh-arabic-panel"><div class="ar-label">عربي</div><div class="ar-text">تطبيق خريف هيلث متاح باللغتين العربية والإنجليزية بالكامل.</div></div>', unsafe_allow_html=True)
elif st.session_state.show_card_info == "khareef":
    with st.expander("🌦️ About Khareef Mode", expanded=True):
        st.warning("Salalah's monsoon season (June–September) increases humidity, mold, respiratory risks and mosquito-borne diseases. Turn Khareef Mode ON during this period for extra sensitivity in triage.")

st.markdown("<hr>", unsafe_allow_html=True)

# ── Profile context builder ───────────────────────
def build_user_profile_context():
    name        = st.session_state.get("user_name","") or "Unknown"
    age         = st.session_state.get("user_age", 40)
    gender      = st.session_state.get("gender","Not specified")
    city        = st.session_state.get("user_city","Salalah")
    blood_type  = st.session_state.get("user_blood_type","Unknown")
    medications = st.session_state.get("user_medications","").strip()
    conditions  = st.session_state.get("user_conditions",[])
    khareef     = st.session_state.get("khareef", False)
    return f"""PATIENT PROFILE:
- Name: {name}
- Age: {age} years
- Gender: {gender}
- Location: {city}, Oman
- Blood type: {blood_type}
- Known conditions: {', '.join(conditions) if conditions else 'None reported'}
- Current medications: {medications if medications else 'None reported'}
- Khareef mode: {'YES — higher humidity/respiratory sensitivity' if khareef else 'No'}
Always address the patient by name if known. Tailor advice to their profile."""

st.session_state["_profile_context"] = build_user_profile_context()

# ══════════════════════════════════════
# TABS
# ══════════════════════════════════════
tab_labels = ["👤 Profile","🩺 Health Check","🚨 Emergency",
              "💊 Medicines","👩 Women","🦠 Diseases",
              "📸 Skin AI","💊📷 Med Scanner","📊 Trends","ℹ️ About"]

if VOICE_ENABLED:
    lang = st.session_state.language
    tab_labels = [
        t("profile", lang), t("health_check", lang), t("emergency", lang),
        t("medicines", lang), t("women", lang), t("diseases", lang),
        t("skin_ai", lang), t("med_scanner", lang), t("trends", lang), t("about", lang)
    ]

tabs = st.tabs(tab_labels)
(tab_profile, tab_assess, tab_emergency,
 tab_medicine, tab_women, tab_diseases,
 tab_skin, tab_medscan, tab_research, tab_about) = tabs

# ── Tab: Profile ──────────────────────────────────
with tab_profile:
    try:
        from tabs.tab_profile import render
        render(T, g_emoji, save_profile, load_json, PROFILES_FILE)
    except ImportError:
        st.markdown('<div class="kh-card">', unsafe_allow_html=True)
        st.markdown('<p class="kh-section-label">Personal Information</p>', unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            name_val = st.text_input("Full Name / الاسم الكامل",
                value=st.session_state.user_name,
                placeholder="Ahmed Al-Shanfari", key="p_name")
        with c2:
            phone_val = st.text_input("Phone / الهاتف",
                value=st.session_state.user_phone,
                placeholder="+968 9X XXX XXXX", key="p_phone")

        c1, c2 = st.columns(2)
        with c1:
            age_val = st.number_input("Age / العمر", min_value=0, max_value=120,
                value=st.session_state.user_age, key="p_age")
        with c2:
            gender_val = st.selectbox("Gender / الجنس",
                ["Not specified","Male","Female"],
                index=["Not specified","Male","Female"].index(st.session_state.gender),
                key="p_gender")

        c1, c2 = st.columns(2)
        with c1:
            city_val = st.text_input("City / المدينة",
                value=st.session_state.user_city,
                placeholder="Salalah", key="p_city")
        with c2:
            blood_opts = ["Unknown","A+","A-","B+","B-","AB+","AB-","O+","O-"]
            blood_val = st.selectbox("Blood Type / فصيلة الدم", blood_opts,
                index=blood_opts.index(st.session_state.user_blood_type)
                    if st.session_state.user_blood_type in blood_opts else 0,
                key="p_blood")

        meds_val = st.text_input("Current Medications / الأدوية الحالية",
            value=st.session_state.user_medications,
            placeholder="e.g. Metformin 500mg, Lisinopril 10mg", key="p_meds")

        cond_options = ["Diabetes","Hypertension","Heart Disease","Asthma",
                        "COPD","Kidney Disease","Liver Disease","Cancer","Pregnancy"]
        cond_val = st.multiselect("Medical Conditions / الحالات الطبية",
            cond_options,
            default=[c for c in st.session_state.user_conditions if c in cond_options],
            key="p_conds")

        st.markdown('</div>', unsafe_allow_html=True)

        if st.button("💾 Save Profile / حفظ الملف الشخصي", use_container_width=True, key="p_save"):
            st.session_state.user_name        = name_val.strip()
            st.session_state.user_phone       = phone_val.strip()
            st.session_state.user_age         = age_val
            st.session_state.gender           = gender_val
            st.session_state.user_city        = city_val.strip()
            st.session_state.user_blood_type  = blood_val
            st.session_state.user_medications = meds_val.strip()
            st.session_state.user_conditions  = cond_val
            save_profile({
                "name": name_val.strip(), "phone": phone_val.strip(),
                "age": age_val, "gender": gender_val, "city": city_val.strip(),
                "blood_type": blood_val, "medications": meds_val.strip(),
                "conditions": cond_val
            })
            save_to_localstorage()
            st.success("✅ Profile saved successfully!")
            st.rerun()

    save_to_localstorage()

# ── Tab: Health Check ─────────────────────────────
with tab_assess:
    try:
        from tab_assess_full import render as render_assess
        render_assess(T, save_record, log_patient if DATA_AVAILABLE else lambda *a,**kw: None,
                      is_api_key_configured, get_gemini_advice, analyze_free_text, RECORDS_FILE)
    except ImportError:
        try:
            from tabs.tab_assess import render as render_assess
            render_assess(T, save_record, log_patient if DATA_AVAILABLE else lambda *a,**kw: None,
                          is_api_key_configured, get_gemini_advice, analyze_free_text, RECORDS_FILE)
        except ImportError:
            # ── Built-in fallback health check UI ──
            st.markdown('<p class="kh-section-label">Vital Signs</p>', unsafe_allow_html=True)

            # Vitals
            v1, v2, v3 = st.columns(3)
            with v1:
                temp = st.number_input("🌡️ Temperature (°C)", min_value=34.0, max_value=43.0,
                    value=37.0, step=0.1, key="v_temp")
                temp_status = "normal" if 36.1 <= temp <= 37.5 else "warning" if temp <= 38.5 else "danger"
            with v2:
                hr = st.number_input("💓 Heart Rate (bpm)", min_value=30, max_value=220,
                    value=75, key="v_hr")
                hr_status = "normal" if 60 <= hr <= 100 else "warning" if 50 <= hr <= 120 else "danger"
            with v3:
                spo2 = st.number_input("🫁 SpO₂ (%)", min_value=70, max_value=100,
                    value=98, key="v_spo2")
                spo2_status = "normal" if spo2 >= 95 else "warning" if spo2 >= 90 else "danger"

            # Vitals display
            st.markdown(f"""
            <div class="kh-vitals">
              <div class="kh-vital">
                <div class="kh-vital-label">Temperature</div>
                <div class="kh-vital-value">{temp:.1f}</div>
                <div class="kh-vital-unit">°C</div>
                <div class="kh-vital-bar {temp_status}"></div>
              </div>
              <div class="kh-vital">
                <div class="kh-vital-label">Heart Rate</div>
                <div class="kh-vital-value">{hr}</div>
                <div class="kh-vital-unit">bpm</div>
                <div class="kh-vital-bar {hr_status}"></div>
              </div>
              <div class="kh-vital">
                <div class="kh-vital-label">SpO₂</div>
                <div class="kh-vital-value">{spo2}</div>
                <div class="kh-vital-unit">%</div>
                <div class="kh-vital-bar {spo2_status}"></div>
              </div>
            </div>""", unsafe_allow_html=True)

            # Symptoms
            st.markdown('<p class="kh-section-label">Symptoms / الأعراض</p>', unsafe_allow_html=True)
            symptom_options = [
                "Fever","Cough","Headache","Fatigue","Chest pain",
                "Shortness of breath","Nausea","Vomiting","Dizziness",
                "Back pain","Sore throat","Runny nose","Muscle aches",
                "Rash","Abdominal pain","Diarrhea","Joint pain","Confusion"
            ]
            selected_syms = st.multiselect("Select symptoms", symptom_options,
                placeholder="Choose symptoms...", key="v_symptoms")

            free_text = st.text_area("Describe how you feel / صف كيف تشعر",
                placeholder="e.g. I have had a fever for 2 days with body aches...",
                height=90, key="v_freetext")

            col_btn1, col_btn2 = st.columns([3, 1])
            with col_btn1:
                assess_clicked = st.button("🩺 Assess My Health / تقييم صحتي",
                    use_container_width=True, key="v_assess")
            with col_btn2:
                st.button("🔄 Reset", use_container_width=True, key="v_reset")

            if assess_clicked:
                # Simple rule-based triage
                danger_symptoms = {"chest pain","shortness of breath","confusion"}
                warn_symptoms   = {"fever","headache","nausea","vomiting","dizziness"}
                selected_lower  = {s.lower() for s in selected_syms}

                if (temp >= 39.5 or spo2 < 90 or hr > 130 or hr < 45
                        or selected_lower & danger_symptoms):
                    level, cls = "RED", "red"
                    title = "Urgent — Seek immediate medical attention"
                    ar_title = "عاجل — اطلب الرعاية الطبية الفورية"
                    steps = [
                        ("r", "Call 999 or go to the nearest emergency room immediately."),
                        ("r", "Do NOT drive yourself — call for help."),
                        ("r", "Take your medications list with you."),
                    ]
                elif (temp >= 38.0 or spo2 < 95 or hr > 100 or hr < 55
                        or selected_lower & warn_symptoms):
                    level, cls = "YELLOW", "yellow"
                    title = "Moderate concern — See a doctor today"
                    ar_title = "قلق معتدل — زر الطبيب اليوم"
                    steps = [
                        ("y", "Visit a clinic or GP today — do not delay."),
                        ("y", "Stay hydrated and rest."),
                        ("y", "Monitor your temperature every 4 hours."),
                        ("y", "Take paracetamol for fever (500mg every 6h max)."),
                    ]
                else:
                    level, cls = "GREEN", "green"
                    title = "All readings normal — You can manage at home"
                    ar_title = "جميع القراءات طبيعية — يمكنك التعافي في المنزل"
                    steps = [
                        ("g", "Rest well and stay hydrated — drink at least 2L of water."),
                        ("g", "Take paracetamol if needed for mild pain or fever."),
                        ("g", "Monitor your symptoms over the next 24 hours."),
                        ("g", "Visit a clinic if symptoms worsen or do not improve in 48 hours."),
                    ]

                steps_html = "".join(
                    f'<div class="kh-step {c}"><div class="kh-step-num">{i+1}</div><div>{s}</div></div>'
                    for i,(c,s) in enumerate(steps)
                )
                st.markdown(f"""
                <div class="kh-result {cls}">
                  <div class="kh-result-head">
                    <span class="kh-level-badge {cls}">{level}</span>
                    <span class="kh-result-title">{title}</span>
                  </div>
                  <div class="kh-steps">{steps_html}</div>
                </div>""", unsafe_allow_html=True)

                if st.session_state.show_arabic:
                    st.markdown(f"""
                    <div class="kh-arabic-panel">
                      <div class="ar-label">Arabic / العربية</div>
                      <div class="ar-text">{ar_title}</div>
                    </div>""", unsafe_allow_html=True)

                # AI advice
                if st.session_state.use_ai and is_api_key_configured():
                    with st.spinner("🤖 Getting AI advice..."):
                        profile_ctx = st.session_state.get("_profile_context","")
                        symptoms_str = ", ".join(selected_syms) if selected_syms else "none reported"
                        prompt = f"""{profile_ctx}

VITALS: Temp={temp}°C, HR={hr}bpm, SpO2={spo2}%
SYMPTOMS: {symptoms_str}
DESCRIPTION: {free_text or 'none'}
TRIAGE RESULT: {level}

Give concise personalised health advice in English, then Arabic. Keep it practical and safe."""
                        advice = get_gemini_advice(prompt)
                        if advice:
                            with st.expander("🤖 AI Personalised Advice", expanded=True):
                                st.markdown(advice)

                # Save record
                save_record({
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "name": st.session_state.user_name,
                    "age": st.session_state.user_age,
                    "temp": temp, "hr": hr, "spo2": spo2,
                    "symptoms": selected_syms,
                    "level": level,
                    "khareef": st.session_state.khareef,
                })

            st.markdown("""
            <div class="kh-disclaimer">
                ⚠️ This triage tool is for educational guidance only. It does not replace professional 
                medical advice. In an emergency, always call <strong>999</strong>.
            </div>""", unsafe_allow_html=True)

# ── Tab: Emergency ────────────────────────────────
with tab_emergency:
    try:
        from tabs.tab_emergency import render
        render(T)
    except ImportError:
        st.markdown("""
        <div class="kh-emergency-main">
          <div style="font-size:13px;font-weight:700;color:#dc2626;letter-spacing:2px;margin-bottom:10px">
              EMERGENCY — SALALAH, OMAN</div>
          <div class="kh-emergency-num">999</div>
          <div style="font-size:13px;color:#7f1d1d;margin-top:8px">Ambulance & Police · 24 hours · Free</div>
          <div style="font-family:'Tajawal',sans-serif;direction:rtl;font-size:14px;
               color:#7f1d1d;margin-top:6px;opacity:0.8">إسعاف وشرطة · ٢٤ ساعة · مجاناً</div>
        </div>""", unsafe_allow_html=True)

        st.markdown('<p class="kh-section-label">Hospitals & Clinics</p>', unsafe_allow_html=True)
        st.markdown('<div class="kh-hospital-grid">', unsafe_allow_html=True)

        hospitals = [
            ("Sultan Qaboos Hospital", "+968 23 211 555", "Al Dahariz, Salalah", "Government · 24h"),
            ("Badr Al Samaa Salalah", "+968 23 219 999", "Salalah", "Private · 24h"),
            ("Al Nahdha Hospital", "+968 23 218 900", "Salalah", "Government"),
            ("Ibin Sina Medical", "+968 23 294 000", "Salalah", "Private"),
        ]
        cols = st.columns(2)
        for i, (name, phone, addr, note) in enumerate(hospitals):
            with cols[i % 2]:
                st.markdown(f"""
                <div class="kh-hospital">
                  <div class="h-name">{name}</div>
                  <div class="h-phone">{phone}</div>
                  <div class="h-addr">{addr} · {note}</div>
                </div>""", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

        st.markdown('<p class="kh-section-label">Warning Signs — Seek Emergency Care Immediately</p>', unsafe_allow_html=True)
        signs = [
            ("Chest pain or pressure", "ألم أو ضغط في الصدر"),
            ("Difficulty breathing", "صعوبة في التنفس"),
            ("Sudden severe headache", "صداع شديد ومفاجئ"),
            ("Signs of stroke (FAST)", "علامات السكتة الدماغية"),
            ("Uncontrolled bleeding", "نزيف لا يمكن إيقافه"),
            ("Loss of consciousness", "فقدان الوعي"),
            ("Severe allergic reaction", "رد فعل تحسسي شديد"),
            ("SpO₂ below 90%", "مستوى الأكسجين أقل من 90٪"),
        ]
        c1, c2 = st.columns(2)
        for i, (en, ar) in enumerate(signs):
            with (c1 if i % 2 == 0 else c2):
                st.markdown(f"""<div class="kh-step r" style="margin-bottom:5px">
                    <div class="kh-step-num" style="background:#dc2626">!</div>
                    <div><strong>{en}</strong><br>
                    <span style="font-family:'Tajawal',sans-serif;direction:rtl;font-size:12px">{ar}</span></div>
                </div>""", unsafe_allow_html=True)

# ── Tab: Medicines ────────────────────────────────
with tab_medicine:
    try:
        from tabs.tab_medicine import render
        render(T)
    except ImportError:
        st.info("💊 Medicine reference tab — connect your `tabs/tab_medicine.py` module.")

# ── Tab: Women ────────────────────────────────────
with tab_women:
    try:
        from tabs.tab_women import render
        render(T)
    except ImportError:
        st.info("👩 Women's health tab — connect your `tabs/tab_women.py` module.")

# ── Tab: Diseases ─────────────────────────────────
with tab_diseases:
    try:
        from tabs.tab_diseases import render
        render(T, DISEASES, CATEGORIES, search_diseases, get_by_category)
    except ImportError:
        st.markdown('<p class="kh-section-label">Disease Reference Library</p>', unsafe_allow_html=True)
        search_q = st.text_input("🔍 Search diseases", placeholder="e.g. malaria, dengue, respiratory...", key="dis_search")

        diseases_data = [
            ("🦟", "Malaria", "Mosquito-borne parasitic infection — higher risk during Khareef",
             "Fever, chills, headache, muscle aches, fatigue", "#fee2e2", "#7f1d1d"),
            ("🌡️", "Dengue Fever", "Viral infection transmitted by Aedes mosquitoes",
             "High fever, severe headache, rash, joint and muscle pain", "#fef9c3", "#78350f"),
            ("🫁", "Respiratory Infections", "Bacterial or viral lung/airway infections — common in Khareef",
             "Cough, fever, difficulty breathing, chest pain", "#dbeafe", "#1e40af"),
            ("☀️", "Heat Exhaustion", "Overheating due to high temperature and humidity",
             "Heavy sweating, weakness, dizziness, nausea", "#fff7ed", "#9a3412"),
            ("💧", "Gastroenteritis", "Stomach and intestinal infection",
             "Diarrhea, vomiting, abdominal cramps, fever", "#d1fae5", "#065f46"),
            ("🩸", "Typhoid Fever", "Bacterial infection from contaminated food/water",
             "Sustained fever, weakness, abdominal pain, headache", "#fce7f3", "#9d174d"),
        ]

        filtered = [d for d in diseases_data if not search_q or
                    search_q.lower() in d[1].lower() or search_q.lower() in d[2].lower()]

        cols = st.columns(2)
        for i, (icon, name, desc, symptoms, bg, tc) in enumerate(filtered):
            with cols[i % 2]:
                st.markdown(f"""
                <div class="kh-disease-card" style="border-left:4px solid {tc}">
                  <div style="font-size:22px;margin-bottom:8px">{icon}</div>
                  <div style="font-size:14px;font-weight:700;color:{tc};margin-bottom:5px">{name}</div>
                  <div style="font-size:12px;color:#555;margin-bottom:8px">{desc}</div>
                  <div style="font-size:11px;font-weight:600;color:#888;margin-bottom:3px">SYMPTOMS</div>
                  <div style="font-size:12px;color:#444">{symptoms}</div>
                </div>""", unsafe_allow_html=True)

# ── Tab: Skin AI ──────────────────────────────────
with tab_skin:
    try:
        from tabs.tab_skin import render
        render(T, GEMINI_API_KEY, is_api_key_configured)
    except ImportError:
        st.markdown("""
        <div class="kh-upload-zone">
          <div class="kh-upload-icon">📸</div>
          <div class="kh-upload-title">AI Skin Analysis</div>
          <div class="kh-upload-sub">Upload a photo of the affected skin area for AI-powered analysis</div>
        </div>""", unsafe_allow_html=True)

        uploaded = st.file_uploader("Upload skin photo", type=["jpg","jpeg","png"],
            key="skin_upload", label_visibility="collapsed")
        if uploaded:
            st.image(uploaded, caption="Uploaded image", use_column_width=True)
            if st.session_state.use_ai and is_api_key_configured():
                if st.button("🔍 Analyse with AI", use_container_width=True, key="skin_btn"):
                    st.info("🤖 Connecting AI skin analysis module...")
            else:
                st.warning("⚠️ AI not configured. Add your Gemini API key to enable AI analysis.")

        st.markdown("""
        <div class="kh-disclaimer">
            ⚠️ AI skin analysis is for educational purposes only and is not a medical diagnosis.
            Always consult a qualified dermatologist for skin concerns.
        </div>""", unsafe_allow_html=True)

# ── Tab: Med Scanner ──────────────────────────────
with tab_medscan:
    try:
        from tabs.tab_medscan import render
        render(T, GEMINI_API_KEY, is_api_key_configured)
    except ImportError:
        st.markdown("""
        <div class="kh-upload-zone">
          <div class="kh-upload-icon">💊</div>
          <div class="kh-upload-title">Medicine Scanner</div>
          <div class="kh-upload-sub">Take a photo of your medicine packaging — AI will identify and explain it</div>
        </div>""", unsafe_allow_html=True)

        uploaded_med = st.file_uploader("Upload medicine photo", type=["jpg","jpeg","png"],
            key="med_upload", label_visibility="collapsed")
        if uploaded_med:
            st.image(uploaded_med, caption="Medicine photo", use_column_width=True)
            if st.session_state.use_ai and is_api_key_configured():
                if st.button("🔍 Scan & Explain", use_container_width=True, key="med_btn"):
                    st.info("🤖 Connecting AI medicine scanner...")

# ── Tab: Trends ───────────────────────────────────
with tab_research:
    try:
        from tabs.tab_research import render
        render(T, load_json, RECORDS_FILE)
    except ImportError:
        records = load_json(RECORDS_FILE)
        user_records = [r for r in records
                        if r.get("name","") == st.session_state.user_name] if st.session_state.user_name else records
        user_records = sorted(user_records, key=lambda x: x.get("timestamp",""), reverse=True)

        # Metrics
        total = len(user_records)
        green_c  = sum(1 for r in user_records if r.get("level","") == "GREEN")
        yellow_c = sum(1 for r in user_records if r.get("level","") == "YELLOW")
        red_c    = sum(1 for r in user_records if r.get("level","") == "RED")

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Assessments", total)
        m2.metric("🟢 Green", green_c)
        m3.metric("🟡 Yellow", yellow_c)
        m4.metric("🔴 Red", red_c)

        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        st.markdown('<p class="kh-section-label">Assessment History</p>', unsafe_allow_html=True)

        if user_records:
            level_map = {"GREEN":"green","YELLOW":"yellow","RED":"red"}
            rows_html = ""
            for r in user_records[:20]:
                lvl = r.get("level","GREEN")
                cls = level_map.get(lvl,"green")
                syms = ", ".join(r.get("symptoms",[])[:3]) or "No symptoms"
                ts   = r.get("timestamp","")[:10]
                rows_html += f"""
                <div class="kh-trend-row">
                  <span class="kh-level-pill {cls}">{lvl}</span>
                  <span style="flex:1;font-size:13px">{syms}</span>
                  <span style="font-size:11px;color:#999">{ts}</span>
                </div>"""
            st.markdown(f'<div class="kh-trend-history">{rows_html}</div>', unsafe_allow_html=True)
        else:
            st.info("No assessment records yet. Use the Health Check tab to get started.")

# ── Tab: About ────────────────────────────────────
with tab_about:
    try:
        from tabs.tab_about import render
        render(T)
    except ImportError:
        st.markdown(f"""
        <div class="kh-card" style="text-align:center">
          <div style="font-size:48px;margin-bottom:12px">🌿</div>
          <div style="font-size:20px;font-weight:800;color:{T['p']};margin-bottom:4px">Khareef Health</div>
          <div style="font-size:12px;color:#888;margin-bottom:16px">v4.2 · by Sadga Selime · Salalah, Oman</div>
          <div style="font-size:13px;color:#555;line-height:1.8;max-width:500px;margin:0 auto">
            An AI-powered telemedicine triage assistant designed for Salalah, Dhofar, Oman.
            Supports English, Arabic, and Bengali. Powered by Google Gemini AI.
            Built for the Khareef season and year-round health guidance.
          </div>
          <div style="margin-top:16px;padding:14px;background:#f4f6f4;border-radius:12px;
               font-family:'Tajawal',sans-serif;direction:rtl;font-size:14px;color:#444;line-height:2">
            مساعد الفرز الطبي الذكي المصمم لصلالة، ظفار، عُمان.
            يدعم اللغتين العربية والإنجليزية والبنغالية.
          </div>
        </div>""", unsafe_allow_html=True)

        st.markdown("""
        <div class="kh-disclaimer">
            ⚠️ <strong>Disclaimer:</strong> Khareef Health is for educational and informational purposes only.
            It does not constitute medical advice, diagnosis, or treatment.
            Always consult a qualified healthcare professional for medical concerns.
            In emergencies, call <strong>999</strong>.
        </div>""", unsafe_allow_html=True)

# ── Admin Panel ───────────────────────────────────
if st.query_params.get("admin","") == "true":
    try:
        from tabs.tab_admin import render
        render(load_json, save_json, RECORDS_FILE, PROFILES_FILE, VISITORS_FILE)
    except ImportError:
        st.warning("Admin module not found.")

# ── Footer ────────────────────────────────────────
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown(f"""
<div style="text-align:center;padding:8px 0 16px;font-size:11px;color:#aaa">
  🌿 Khareef Health v4.2 · by Sadga Selime · Salalah, Oman<br>
  Powered by Google Gemini AI · Educational use only · Emergency: <strong style="color:#dc2626">999</strong>
</div>""", unsafe_allow_html=True)
