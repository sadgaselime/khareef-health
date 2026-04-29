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
    from translations import t as _t, LANGUAGES, get_lang_code, get_tts_code
    from voice_utils import voice_input_component, text_to_speech_component
    VOICE_ENABLED = True
except ImportError:
    VOICE_ENABLED = False
    def _t(key, lang="English"): return key.replace("_"," ").title()
    def voice_input_component(*a, **kw): return None
    def text_to_speech_component(*a, **kw): pass
    def get_tts_code(lang): return "en-US"
    def get_lang_code(lang): return "en"

# ══════════════════════════════════════════════════
# BUILT-IN TRANSLATIONS
# ══════════════════════════════════════════════════
TX = {
    "English": {
        "tab_profile":"👤 Profile","tab_health":"🩺 Health Check","tab_emergency":"🚨 Emergency",
        "tab_medicines":"💊 Medicines","tab_women":"👩 Women","tab_diseases":"🦠 Diseases",
        "tab_skin":"📸 Skin AI","tab_medscan":"💊📷 Med Scanner","tab_trends":"📊 Trends","tab_about":"ℹ️ About",
        "theme":"Gender Theme","language":"Language","khareef_toggle":"🌦️ Khareef",
        "ai_toggle":"🤖 AI","voice_toggle":"🎤 Voice",
        "blue_theme":"💙 Blue theme","rose_theme":"💗 Rose theme","green_theme":"💚 Green theme",
        "app_subtitle":"AI Telemedicine Triage · Salalah, Dhofar, Oman",
        "emergency_label":"EMERGENCY","ai_powered":"AI POWERED",
        "introduce":"Introduce yourself 👋","your_name":"Your Name",
        "phone_optional":"Phone (optional)","gender":"Gender",
        "continue_btn":"Continue →","skip_btn":"Skip",
        "privacy_note":"🔒 Your data is stored only on your device",
        "welcome_back":"Welcome back!","profile_restored":"Your profile has been restored",
        "not_you":"Not you? Start fresh",
        "good_morning":"Good morning","good_afternoon":"Good afternoon","good_evening":"Good evening",
        "profile_ready":"Your profile is loaded and ready 🩺",
        "card_emergency":"Emergency","card_call999":"Call 999",
        "card_triage":"AI Triage","card_triagesub":"Green · Yellow · Red",
        "card_multilang":"Multilingual","card_3lang":"3 Languages",
        "card_khareef":"Khareef","card_season":"Salalah Season","info_btn":"ℹ️ Info",
        "khareef_on":"Khareef Mode ON — Higher respiratory sensitivity. Extra caution for mold, humidity and mosquito-borne diseases.",
        "personal_info":"Personal Information","full_name":"Full Name","phone":"Phone",
        "age":"Age","city":"City","blood_type":"Blood Type","medications":"Current Medications",
        "meds_placeholder":"e.g. Metformin 500mg, Lisinopril 10mg",
        "conditions":"Medical Conditions","save_profile":"💾 Save Profile",
        "profile_saved":"✅ Profile saved successfully!",
        "vital_signs":"Vital Signs","temperature":"Temperature","heart_rate":"Heart Rate","spo2":"SpO₂",
        "symptoms_label":"Symptoms","select_symptoms":"Select your symptoms",
        "describe_feel":"Describe how you feel",
        "describe_placeholder":"e.g. I have had a fever for 2 days with body aches...",
        "voice_input_label":"🎤 Tap to speak your symptoms",
        "stop_recording":"⏹ Stop Recording","listening":"Listening...",
        "recorded":"✅ Recorded — edit below if needed",
        "assess_btn":"🩺 Assess My Health","reset_btn":"🔄 Reset",
        "getting_ai":"🤖 Getting AI advice...","ai_advice_title":"🤖 AI Personalised Advice",
        "result_red_title":"Urgent — Seek immediate medical attention",
        "result_yellow_title":"Moderate concern — See a doctor today",
        "result_green_title":"All readings normal — You can manage at home",
        "step_r1":"Call 999 or go to the nearest emergency room immediately.",
        "step_r2":"Do NOT drive yourself — call for help.",
        "step_r3":"Take your medications list with you.",
        "step_y1":"Visit a clinic or GP today — do not delay.",
        "step_y2":"Stay hydrated and rest.",
        "step_y3":"Monitor your temperature every 4 hours.",
        "step_y4":"Take paracetamol for fever (500mg every 6h max).",
        "step_g1":"Rest well and stay hydrated — drink at least 2L of water.",
        "step_g2":"Take paracetamol if needed for mild pain or fever.",
        "step_g3":"Monitor your symptoms over the next 24 hours.",
        "step_g4":"Visit a clinic if symptoms worsen or do not improve in 48 hours.",
        "disclaimer":"⚠️ This triage tool is for educational guidance only. It does not replace professional medical advice. In an emergency, always call 999.",
        "emergency_title":"EMERGENCY — SALALAH, OMAN","ambulance_note":"Ambulance & Police · 24 hours · Free",
        "hospitals_label":"Hospitals & Clinics","warning_signs":"Warning Signs — Seek Emergency Care Immediately",
        "search_diseases":"Search diseases","search_placeholder":"e.g. malaria, dengue, respiratory...",
        "symptoms_col":"SYMPTOMS",
        "skin_title":"AI Skin Analysis","skin_sub":"Upload a photo of the affected skin area for AI-powered analysis",
        "skin_upload":"Upload skin photo","analyse_btn":"🔍 Analyse with AI",
        "med_title":"Medicine Scanner","med_sub":"Take a photo of your medicine packaging — AI will identify and explain it",
        "med_upload":"Upload medicine photo","scan_btn":"🔍 Scan & Explain",
        "ai_not_conf":"⚠️ AI not configured. Add your Gemini API key to enable AI analysis.",
        "total_assess":"Total Assessments","green_results":"🟢 Green","yellow_red":"🟡🔴 Yellow/Red",
        "recent_assess":"Assessment History","no_records":"No assessment records yet. Use the Health Check tab to get started.",
        "about_desc":"An AI-powered telemedicine triage assistant designed for Salalah, Dhofar, Oman. Powered by Google Gemini AI.",
        "disclaimer_full":"⚠️ Disclaimer: Khareef Health is for educational and informational purposes only. It does not constitute medical advice. In emergencies, call 999.",
        "sym_fever":"Fever","sym_cough":"Cough","sym_headache":"Headache","sym_fatigue":"Fatigue",
        "sym_chest":"Chest pain","sym_breath":"Shortness of breath","sym_nausea":"Nausea",
        "sym_vomiting":"Vomiting","sym_dizziness":"Dizziness","sym_backpain":"Back pain",
        "sym_throat":"Sore throat","sym_runny":"Runny nose","sym_muscle":"Muscle aches",
        "sym_rash":"Rash","sym_abdominal":"Abdominal pain","sym_diarrhea":"Diarrhea",
        "sym_joint":"Joint pain","sym_confusion":"Confusion",
        "ai_lang_instruction":"Respond entirely in English only.",
        "tts_lang":"en-US","speech_lang":"en-US",
    },
    "العربية": {
        "tab_profile":"👤 الملف الشخصي","tab_health":"🩺 الفحص الصحي","tab_emergency":"🚨 الطوارئ",
        "tab_medicines":"💊 الأدوية","tab_women":"👩 صحة المرأة","tab_diseases":"🦠 الأمراض",
        "tab_skin":"📸 فحص الجلد","tab_medscan":"💊📷 ماسح الدواء","tab_trends":"📊 الإحصاءات","tab_about":"ℹ️ حول التطبيق",
        "theme":"المظهر","language":"اللغة","khareef_toggle":"🌦️ الخريف",
        "ai_toggle":"🤖 الذكاء الاصطناعي","voice_toggle":"🎤 الصوت",
        "blue_theme":"💙 مظهر أزرق","rose_theme":"💗 مظهر وردي","green_theme":"💚 مظهر أخضر",
        "app_subtitle":"مساعد الفرز الطبي الذكي · صلالة، ظفار، عُمان",
        "emergency_label":"طوارئ","ai_powered":"مدعوم بالذكاء الاصطناعي",
        "introduce":"عرّف بنفسك 👋","your_name":"اسمك",
        "phone_optional":"الهاتف (اختياري)","gender":"الجنس",
        "continue_btn":"متابعة →","skip_btn":"تخطي",
        "privacy_note":"🔒 بياناتك محفوظة على جهازك فقط",
        "welcome_back":"مرحباً بعودتك!","profile_restored":"تم استعادة ملفك الشخصي",
        "not_you":"لست أنت؟ ابدأ من جديد",
        "good_morning":"صباح الخير","good_afternoon":"مساء الخير","good_evening":"مساء الخير",
        "profile_ready":"ملفك الشخصي جاهز 🩺",
        "card_emergency":"طوارئ","card_call999":"اتصل بـ 999",
        "card_triage":"الفرز الذكي","card_triagesub":"أخضر · أصفر · أحمر",
        "card_multilang":"متعدد اللغات","card_3lang":"٣ لغات",
        "card_khareef":"الخريف","card_season":"موسم صلالة","info_btn":"ℹ️ معلومات",
        "khareef_on":"وضع الخريف مفعّل — حساسية تنفسية أعلى. توخَّ الحذر من العفن والرطوبة والأمراض التي تنقلها البعوض.",
        "personal_info":"المعلومات الشخصية","full_name":"الاسم الكامل","phone":"الهاتف",
        "age":"العمر","city":"المدينة","blood_type":"فصيلة الدم","medications":"الأدوية الحالية",
        "meds_placeholder":"مثال: ميتفورمين ٥٠٠ ملغ",
        "conditions":"الحالات الطبية","save_profile":"💾 حفظ الملف الشخصي",
        "profile_saved":"✅ تم حفظ الملف الشخصي بنجاح!",
        "vital_signs":"العلامات الحيوية","temperature":"درجة الحرارة","heart_rate":"معدل ضربات القلب","spo2":"تشبع الأكسجين",
        "symptoms_label":"الأعراض","select_symptoms":"اختر الأعراض",
        "describe_feel":"صف كيف تشعر",
        "describe_placeholder":"مثال: لدي حمى منذ يومين مع آلام في الجسم...",
        "voice_input_label":"🎤 اضغط للتحدث عن أعراضك",
        "stop_recording":"⏹ إيقاف التسجيل","listening":"جارٍ الاستماع...",
        "recorded":"✅ تم التسجيل — عدّل أدناه إذا لزم",
        "assess_btn":"🩺 تقييم صحتي","reset_btn":"🔄 إعادة تعيين",
        "getting_ai":"🤖 جارٍ الحصول على نصيحة الذكاء الاصطناعي...","ai_advice_title":"🤖 نصيحة الذكاء الاصطناعي الشخصية",
        "result_red_title":"عاجل — اطلب الرعاية الطبية الفورية",
        "result_yellow_title":"قلق معتدل — زر الطبيب اليوم",
        "result_green_title":"جميع القراءات طبيعية — يمكنك التعافي في المنزل",
        "step_r1":"اتصل بـ 999 أو اذهب إلى أقرب غرفة طوارئ فوراً.",
        "step_r2":"لا تقد بنفسك — اطلب المساعدة.",
        "step_r3":"خذ معك قائمة أدويتك.",
        "step_y1":"زر عيادة أو طبيباً عاماً اليوم — لا تتأخر.",
        "step_y2":"حافظ على الترطيب والراحة.",
        "step_y3":"راقب درجة حرارتك كل ٤ ساعات.",
        "step_y4":"تناول باراسيتامول للحمى (٥٠٠ ملغ كل ٦ ساعات كحد أقصى).",
        "step_g1":"استرح جيداً واشرب الكثير من الماء — على الأقل ٢ لتر.",
        "step_g2":"تناول باراسيتامول عند الحاجة لتخفيف الألم الخفيف.",
        "step_g3":"راقب أعراضك خلال الـ٢٤ ساعة القادمة.",
        "step_g4":"زر عيادة إذا ساءت الأعراض أو لم تتحسن خلال ٤٨ ساعة.",
        "disclaimer":"⚠️ هذه الأداة للتوجيه التعليمي فقط ولا تُغني عن الرأي الطبي المهني. في حالات الطوارئ اتصل بـ 999.",
        "emergency_title":"طوارئ — صلالة، عُمان","ambulance_note":"إسعاف وشرطة · ٢٤ ساعة · مجاناً",
        "hospitals_label":"المستشفيات والعيادات","warning_signs":"علامات التحذير — اطلب الرعاية الطارئة فوراً",
        "search_diseases":"البحث عن الأمراض","search_placeholder":"مثال: ملاريا، حمى الضنك...",
        "symptoms_col":"الأعراض",
        "skin_title":"تحليل الجلد بالذكاء الاصطناعي","skin_sub":"ارفع صورة لمنطقة الجلد المصابة للتحليل",
        "skin_upload":"ارفع صورة الجلد","analyse_btn":"🔍 التحليل بالذكاء الاصطناعي",
        "med_title":"ماسح الأدوية","med_sub":"التقط صورة لعبوة دوائك — سيتعرف عليها الذكاء الاصطناعي",
        "med_upload":"ارفع صورة الدواء","scan_btn":"🔍 مسح وشرح",
        "ai_not_conf":"⚠️ الذكاء الاصطناعي غير مُهيأ. أضف مفتاح Gemini API لتفعيل التحليل.",
        "total_assess":"إجمالي التقييمات","green_results":"🟢 أخضر","yellow_red":"🟡🔴 أصفر/أحمر",
        "recent_assess":"سجل التقييمات","no_records":"لا توجد سجلات بعد. استخدم تبويب الفحص الصحي للبدء.",
        "about_desc":"مساعد ذكي للفرز الطبي مصمم لصلالة، ظفار، عُمان. مدعوم بـ Google Gemini AI.",
        "disclaimer_full":"⚠️ إخلاء المسؤولية: خريف هيلث للأغراض التعليمية فقط. في حالات الطوارئ اتصل بـ 999.",
        "sym_fever":"حمى","sym_cough":"سعال","sym_headache":"صداع","sym_fatigue":"إرهاق",
        "sym_chest":"ألم في الصدر","sym_breath":"ضيق في التنفس","sym_nausea":"غثيان",
        "sym_vomiting":"قيء","sym_dizziness":"دوخة","sym_backpain":"ألم في الظهر",
        "sym_throat":"التهاب الحلق","sym_runny":"سيلان الأنف","sym_muscle":"آلام عضلية",
        "sym_rash":"طفح جلدي","sym_abdominal":"ألم في البطن","sym_diarrhea":"إسهال",
        "sym_joint":"ألم المفاصل","sym_confusion":"ارتباك",
        "ai_lang_instruction":"أجب بالكامل باللغة العربية فقط. لا تستخدم أي لغة أخرى.",
        "tts_lang":"ar-SA","speech_lang":"ar-SA",
    },
    "বাংলা": {
        "tab_profile":"👤 প্রোফাইল","tab_health":"🩺 স্বাস্থ্য পরীক্ষা","tab_emergency":"🚨 জরুরি",
        "tab_medicines":"💊 ওষুধ","tab_women":"👩 নারী স্বাস্থ্য","tab_diseases":"🦠 রোগসমূহ",
        "tab_skin":"📸 ত্বক AI","tab_medscan":"💊📷 ওষুধ স্ক্যানার","tab_trends":"📊 পরিসংখ্যান","tab_about":"ℹ️ সম্পর্কে",
        "theme":"থিম","language":"ভাষা","khareef_toggle":"🌦️ খারিফ",
        "ai_toggle":"🤖 AI","voice_toggle":"🎤 ভয়েস",
        "blue_theme":"💙 নীল থিম","rose_theme":"💗 গোলাপি থিম","green_theme":"💚 সবুজ থিম",
        "app_subtitle":"AI টেলিমেডিসিন ট্রিয়াজ · সালালাহ, ধোফার, ওমান",
        "emergency_label":"জরুরি","ai_powered":"AI চালিত",
        "introduce":"নিজেকে পরিচয় করিয়ে দিন 👋","your_name":"আপনার নাম",
        "phone_optional":"ফোন (ঐচ্ছিক)","gender":"লিঙ্গ",
        "continue_btn":"চালিয়ে যান →","skip_btn":"এড়িয়ে যান",
        "privacy_note":"🔒 আপনার তথ্য শুধুমাত্র আপনার ডিভাইসে সংরক্ষিত",
        "welcome_back":"আবার স্বাগতম!","profile_restored":"আপনার প্রোফাইল পুনরুদ্ধার করা হয়েছে",
        "not_you":"আপনি নন? নতুন করে শুরু করুন",
        "good_morning":"সুপ্রভাত","good_afternoon":"শুভ অপরাহ্ন","good_evening":"শুভ সন্ধ্যা",
        "profile_ready":"আপনার প্রোফাইল প্রস্তুত 🩺",
        "card_emergency":"জরুরি","card_call999":"999 কল করুন",
        "card_triage":"AI ট্রিয়াজ","card_triagesub":"সবুজ · হলুদ · লাল",
        "card_multilang":"বহুভাষিক","card_3lang":"৩ ভাষা",
        "card_khareef":"খারিফ","card_season":"সালালাহ মৌসুম","info_btn":"ℹ️ তথ্য",
        "khareef_on":"খারিফ মোড চালু — উচ্চ শ্বাসযন্ত্রের সংবেদনশীলতা। ছাঁচ, আর্দ্রতা এবং মশাবাহিত রোগ থেকে সতর্ক থাকুন।",
        "personal_info":"ব্যক্তিগত তথ্য","full_name":"পূর্ণ নাম","phone":"ফোন",
        "age":"বয়স","city":"শহর","blood_type":"রক্তের গ্রুপ","medications":"বর্তমান ওষুধ",
        "meds_placeholder":"যেমন: মেটফর্মিন ৫০০mg",
        "conditions":"চিকিৎসা অবস্থা","save_profile":"💾 প্রোফাইল সংরক্ষণ করুন",
        "profile_saved":"✅ প্রোফাইল সফলভাবে সংরক্ষিত!",
        "vital_signs":"গুরুত্বপূর্ণ লক্ষণ","temperature":"তাপমাত্রা","heart_rate":"হৃদস্পন্দন","spo2":"SpO₂",
        "symptoms_label":"লক্ষণ","select_symptoms":"আপনার লক্ষণ নির্বাচন করুন",
        "describe_feel":"আপনি কেমন অনুভব করছেন বলুন",
        "describe_placeholder":"যেমন: দুই দিন ধরে জ্বর এবং শরীরে ব্যথা...",
        "voice_input_label":"🎤 ট্যাপ করে লক্ষণ বলুন",
        "stop_recording":"⏹ রেকর্ডিং বন্ধ করুন","listening":"শুনছি...",
        "recorded":"✅ রেকর্ড হয়েছে — প্রয়োজনে নিচে সম্পাদনা করুন",
        "assess_btn":"🩺 আমার স্বাস্থ্য মূল্যায়ন করুন","reset_btn":"🔄 রিসেট",
        "getting_ai":"🤖 AI পরামর্শ পাচ্ছি...","ai_advice_title":"🤖 AI ব্যক্তিগত পরামর্শ",
        "result_red_title":"জরুরি — অবিলম্বে চিকিৎসা নিন",
        "result_yellow_title":"মাঝারি উদ্বেগ — আজই ডাক্তার দেখান",
        "result_green_title":"সব রিডিং স্বাভাবিক — বাড়িতে সামলাতে পারবেন",
        "step_r1":"এখনই 999 কল করুন বা নিকটতম জরুরি বিভাগে যান।",
        "step_r2":"নিজে গাড়ি চালাবেন না — সাহায্য চান।",
        "step_r3":"আপনার ওষুধের তালিকা সাথে নিন।",
        "step_y1":"আজই একটি ক্লিনিক বা জিপি পরিদর্শন করুন — দেরি করবেন না।",
        "step_y2":"হাইড্রেটেড থাকুন এবং বিশ্রাম নিন।",
        "step_y3":"প্রতি ৪ ঘন্টায় তাপমাত্রা পর্যবেক্ষণ করুন।",
        "step_y4":"জ্বরের জন্য প্যারাসিটামল নিন (৫০০mg প্রতি ৬ ঘন্টায় সর্বোচ্চ)।",
        "step_g1":"ভালো বিশ্রাম নিন এবং পর্যাপ্ত পানি পান করুন — কমপক্ষে ২ লিটার।",
        "step_g2":"প্রয়োজনে হালকা ব্যথার জন্য প্যারাসিটামল নিন।",
        "step_g3":"পরবর্তী ২৪ ঘন্টা আপনার লক্ষণ পর্যবেক্ষণ করুন।",
        "step_g4":"লক্ষণ খারাপ হলে বা ৪৮ ঘন্টায় উন্নতি না হলে ক্লিনিকে যান।",
        "disclaimer":"⚠️ এই টুলটি শুধুমাত্র শিক্ষামূলক নির্দেশনার জন্য। পেশাদার চিকিৎসা পরামর্শের বিকল্প নয়। জরুরি অবস্থায় 999 কল করুন।",
        "emergency_title":"জরুরি — সালালাহ, ওমান","ambulance_note":"অ্যাম্বুলেন্স ও পুলিশ · ২৪ ঘন্টা · বিনামূল্যে",
        "hospitals_label":"হাসপাতাল ও ক্লিনিক","warning_signs":"সতর্কতার লক্ষণ — অবিলম্বে জরুরি চিকিৎসা নিন",
        "search_diseases":"রোগ খুঁজুন","search_placeholder":"যেমন: ম্যালেরিয়া, ডেঙ্গু...",
        "symptoms_col":"লক্ষণ",
        "skin_title":"AI ত্বক বিশ্লেষণ","skin_sub":"AI বিশ্লেষণের জন্য আক্রান্ত ত্বকের ছবি আপলোড করুন",
        "skin_upload":"ত্বকের ছবি আপলোড করুন","analyse_btn":"🔍 AI দিয়ে বিশ্লেষণ করুন",
        "med_title":"ওষুধ স্ক্যানার","med_sub":"আপনার ওষুধের প্যাকেজিংয়ের ছবি তুলুন",
        "med_upload":"ওষুধের ছবি আপলোড করুন","scan_btn":"🔍 স্ক্যান করুন",
        "ai_not_conf":"⚠️ AI কনফিগার করা নেই। বিশ্লেষণ সক্ষম করতে Gemini API কী যোগ করুন।",
        "total_assess":"মোট মূল্যায়ন","green_results":"🟢 সবুজ","yellow_red":"🟡🔴 হলুদ/লাল",
        "recent_assess":"মূল্যায়নের ইতিহাস","no_records":"এখনও কোনো রেকর্ড নেই। স্বাস্থ্য পরীক্ষা ব্যবহার করুন।",
        "about_desc":"সালালাহ, ধোফার, ওমানের জন্য ডিজাইন করা AI-চালিত টেলিমেডিসিন ট্রিয়াজ সহকারী।",
        "disclaimer_full":"⚠️ দাবিত্যাগ: খারিফ হেলথ শুধুমাত্র শিক্ষামূলক উদ্দেশ্যে। জরুরি অবস্থায় 999 কল করুন।",
        "sym_fever":"জ্বর","sym_cough":"কাশি","sym_headache":"মাথাব্যথা","sym_fatigue":"ক্লান্তি",
        "sym_chest":"বুকে ব্যথা","sym_breath":"শ্বাসকষ্ট","sym_nausea":"বমি বমি ভাব",
        "sym_vomiting":"বমি","sym_dizziness":"মাথা ঘোরা","sym_backpain":"পিঠে ব্যথা",
        "sym_throat":"গলা ব্যথা","sym_runny":"নাক দিয়ে পানি পড়া","sym_muscle":"পেশিতে ব্যথা",
        "sym_rash":"ত্বকে ফুসকুড়ি","sym_abdominal":"পেটে ব্যথা","sym_diarrhea":"ডায়রিয়া",
        "sym_joint":"জয়েন্টে ব্যথা","sym_confusion":"বিভ্রান্তি",
        "ai_lang_instruction":"সম্পূর্ণ বাংলায় উত্তর দিন। অন্য কোনো ভাষা ব্যবহার করবেন না।",
        "tts_lang":"bn-BD","speech_lang":"bn-BD",
    }
}

def L(key):
    lang = st.session_state.get("language","English")
    d = TX.get(lang, TX["English"])
    return d.get(key, TX["English"].get(key, key))

def is_rtl():
    return st.session_state.get("language","English") == "العربية"

def body_font():
    lang = st.session_state.get("language","English")
    if lang == "العربية": return "'Tajawal', sans-serif"
    if lang == "বাংলা":   return "'Hind Siliguri', sans-serif"
    return "'Plus Jakarta Sans', sans-serif"

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
        d.append({"timestamp":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                  "date":datetime.now().strftime("%Y-%m-%d"),
                  "name":name or "Anonymous","action":action,
                  "session":st.session_state.get("sid","")})
        save_json(VISITORS_FILE,d)
    except: pass

# ── Session defaults ──────────────────────────────
DEFAULTS = {
    "gender":"Not specified","user_name":"","user_age":40,
    "user_city":"Salalah","user_conditions":[],"user_medications":"",
    "user_phone":"","user_blood_type":"Unknown",
    "khareef":False,"use_ai":is_api_key_configured(),"voice_on":True,
    "welcomed":False,"profile_restored":False,"sid":str(uuid.uuid4())[:8],
    "show_card_info":None,"language":"English","voice_transcript":"",
}
for k,v in DEFAULTS.items():
    if k not in st.session_state: st.session_state[k]=v

# ── URL param profile restore ─────────────────────
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
    try: st.session_state.user_age    = int(params.get("ka",40))
    except: pass
    try: st.session_state.user_conditions = json.loads(urllib.parse.unquote(params.get("kco","[]")))
    except: pass
    st.session_state.profile_restored = True
    st.session_state.welcomed = True
    st.query_params.clear()

components.html("""<script>
(function(){
  try{
    if(sessionStorage.getItem('kh_loaded')==='1') return;
    var url=new URL(window.parent.location.href);
    if(url.searchParams.get('kn')){sessionStorage.setItem('kh_loaded','1');return;}
    var saved=localStorage.getItem('khareef_profile');
    if(!saved) return;
    var p;try{p=JSON.parse(saved);}catch(e){return;}
    if(!p||!p.name) return;
    sessionStorage.setItem('kh_loaded','1');
    url.searchParams.set('kn',encodeURIComponent(p.name||''));
    url.searchParams.set('kp',encodeURIComponent(p.phone||''));
    url.searchParams.set('ka',p.age||40);
    url.searchParams.set('kg',encodeURIComponent(p.gender||'Not specified'));
    url.searchParams.set('kc',encodeURIComponent(p.city||'Salalah'));
    url.searchParams.set('kb',encodeURIComponent(p.blood_type||'Unknown'));
    url.searchParams.set('km',encodeURIComponent(p.medications||''));
    url.searchParams.set('kl',encodeURIComponent(p.language||'English'));
    url.searchParams.set('kco',encodeURIComponent(JSON.stringify(p.conditions||[])));
    window.parent.history.replaceState({},'',url.toString());
    window.parent.location.reload();
  }catch(e){}
})();
</script>""", height=0)

def save_to_localstorage():
    pj = json.dumps({"name":st.session_state.user_name,"phone":st.session_state.user_phone,
        "age":st.session_state.user_age,"gender":st.session_state.gender,
        "city":st.session_state.user_city,"blood_type":st.session_state.user_blood_type,
        "medications":st.session_state.user_medications,"language":st.session_state.language,
        "conditions":st.session_state.user_conditions},ensure_ascii=False)
    components.html(f"""<script>
    try{{localStorage.setItem('khareef_profile',{json.dumps(pj)});
    sessionStorage.setItem('kh_loaded','1');}}catch(e){{}}
    </script>""",height=0)

# ── Theme ─────────────────────────────────────────
THEMES = {
    "Male":          {"p":"#1a4a8a","s":"#2d6fba","l":"#dbeafe","a":"#0d2d5c",
                      "g":"135deg,#0d2d5c,#1a4a8a,#2d6fba",
                      "g1":"#0d2d5c","g2":"#1a4a8a","g3":"#2d6fba"},
    "Female":        {"p":"#9d174d","s":"#db2777","l":"#fce7f3","a":"#500724",
                      "g":"135deg,#500724,#9d174d,#db2777",
                      "g1":"#500724","g2":"#9d174d","g3":"#db2777"},
    "Not specified": {"p":"#1a5c45","s":"#2d8a65","l":"#d1fae5","a":"#0d3d29",
                      "g":"135deg,#0d3d29,#1a5c45,#2d8a65",
                      "g1":"#0d3d29","g2":"#1a5c45","g3":"#2d8a65"},
}
T = THEMES[st.session_state.gender]
RTL = is_rtl()
FONT = body_font()

# ══════════════════════════════════════════════════
# GLOBAL CSS
# ══════════════════════════════════════════════════
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Tajawal:wght@400;500;700&family=Hind+Siliguri:wght@400;500;600;700&display=swap');
*,*::before,*::after{{box-sizing:border-box;}}
html,body,[class*="css"]{{font-family:{FONT};font-size:14px;line-height:1.6;}}
{"body,.stApp{direction:rtl;}" if RTL else ""}
#MainMenu,footer,header{{visibility:hidden;}}
section[data-testid="stSidebar"]{{display:none;}}
.stApp{{background:#f4f6f4;}}
.block-container{{padding:1rem 1.5rem 3rem !important;max-width:960px !important;}}

.kh-header{{background:linear-gradient(135deg,{T['g1']} 0%,{T['g2']} 45%,{T['g3']} 100%);
  border-radius:20px;padding:22px 28px 16px;color:white;margin-bottom:14px;
  position:relative;overflow:hidden;box-shadow:0 8px 32px {T['p']}40;}}
.kh-header::before{{content:'';position:absolute;top:-40px;right:-40px;width:180px;height:180px;
  border-radius:50%;background:rgba(255,255,255,0.06);pointer-events:none;}}
.kh-header-inner{{display:flex;align-items:center;gap:18px;position:relative;z-index:1;flex-wrap:wrap;
  {"flex-direction:row-reverse;" if RTL else ""}}}
.kh-logo{{width:54px;height:54px;border-radius:16px;background:rgba(255,255,255,0.15);
  display:flex;align-items:center;justify-content:center;font-size:26px;
  border:1.5px solid rgba(255,255,255,0.25);flex-shrink:0;
  animation:kh-float 3.5s ease-in-out infinite;}}
@keyframes kh-float{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-5px)}}}}
.kh-header-text{{flex:1;min-width:0;{"text-align:right;" if RTL else ""}}}
.kh-header-text h1{{font-size:22px;font-weight:800;margin:0 0 3px;letter-spacing:-0.3px;}}
.kh-header-text .kh-sub{{font-size:11px;opacity:0.7;letter-spacing:1px;text-transform:uppercase;margin:0;}}
.kh-badge-row{{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-top:8px;
  {"justify-content:flex-end;" if RTL else ""}}}
.kh-badge{{background:rgba(255,255,255,0.15);border:1px solid rgba(255,255,255,0.2);
  border-radius:8px;padding:4px 10px;font-size:10px;font-weight:700;letter-spacing:0.8px;}}
.kh-emergency{{background:rgba(220,38,38,0.75);border:1px solid rgba(255,100,100,0.4);
  border-radius:12px;padding:10px 16px;text-align:center;flex-shrink:0;}}
.kh-emergency .em-label{{font-size:9px;letter-spacing:2px;opacity:0.9;display:block;margin-bottom:2px;}}
.kh-emergency .em-num{{font-size:24px;font-weight:900;letter-spacing:2px;display:block;}}
.kh-ecg{{width:100%;height:20px;margin-top:12px;opacity:0.2;}}

.kh-greeting{{background:linear-gradient(135deg,{T['g2']} 0%,{T['g3']} 100%);
  border-radius:16px;padding:18px 22px;color:white;margin-bottom:14px;
  display:flex;align-items:center;gap:16px;animation:kh-fadein 0.5s ease;
  box-shadow:0 4px 18px {T['p']}35;{"flex-direction:row-reverse;" if RTL else ""}}}
@keyframes kh-fadein{{from{{opacity:0;transform:translateY(8px)}}to{{opacity:1;transform:translateY(0)}}}}
.kh-greeting-avatar{{width:52px;height:52px;border-radius:50%;background:rgba(255,255,255,0.2);
  display:flex;align-items:center;justify-content:center;font-size:26px;
  border:2px solid rgba(255,255,255,0.3);flex-shrink:0;}}
.kh-greeting-text h2{{font-size:17px;font-weight:700;margin:0 0 4px;{"text-align:right;" if RTL else ""}}}
.kh-greeting-text p{{font-size:12px;opacity:0.85;margin:0;{"text-align:right;" if RTL else ""}}}

.kh-stat{{background:white;border-radius:14px;padding:14px 10px;text-align:center;
  border:1px solid #e8ede8;cursor:pointer;transition:all 0.18s ease;
  box-shadow:0 2px 6px rgba(0,0,0,0.04);}}
.kh-stat:hover{{transform:translateY(-3px);box-shadow:0 6px 18px rgba(0,0,0,0.10);border-color:{T['s']}55;}}
.kh-stat .st-ico{{font-size:22px;margin-bottom:7px;}}
.kh-stat .st-lbl{{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:0.6px;margin-bottom:2px;}}
.kh-stat .st-sub{{font-size:10px;color:#777;}}

.kh-section-label{{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:1.2px;
  color:#888;margin:0 0 8px 2px;{"text-align:right;" if RTL else ""}}}
.kh-khareef-banner{{background:#fffbeb;border:1px solid #fcd34d;border-radius:12px;
  padding:10px 16px;font-size:12px;color:#78350f;margin-bottom:12px;
  display:flex;align-items:center;gap:10px;font-weight:500;
  {"flex-direction:row-reverse;" if RTL else ""}}}
.kh-card{{background:white;border-radius:16px;padding:20px;border:1px solid #e8ede8;
  margin-bottom:14px;box-shadow:0 2px 8px rgba(0,0,0,0.04);}}
.kh-vitals{{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:14px;}}
.kh-vital{{background:white;border-radius:14px;padding:14px;text-align:center;
  border:1px solid #e8ede8;box-shadow:0 2px 6px rgba(0,0,0,0.04);}}
.kh-vital-label{{font-size:10px;font-weight:600;color:#888;text-transform:uppercase;letter-spacing:0.6px;margin-bottom:6px;}}
.kh-vital-value{{font-size:28px;font-weight:800;color:{T['p']};line-height:1;margin-bottom:4px;}}
.kh-vital-unit{{font-size:11px;color:#aaa;}}
.kh-vital-bar{{height:3px;border-radius:99px;margin-top:10px;}}
.kh-vital-bar.normal{{background:#16a34a;}}
.kh-vital-bar.warning{{background:#f59e0b;}}
.kh-vital-bar.danger{{background:#dc2626;}}

/* VOICE MIC */
.kh-mic-wrap{{margin-bottom:10px;}}
.kh-mic-btn{{
  display:flex;align-items:center;justify-content:center;gap:10px;width:100%;
  background:linear-gradient(135deg,{T['g2']},{T['g3']});
  color:white;border:none;border-radius:12px;padding:13px 20px;
  font-size:14px;font-weight:700;cursor:pointer;
  box-shadow:0 4px 14px {T['p']}40;transition:all 0.2s ease;
  font-family:{FONT};
}}
.kh-mic-btn:hover{{transform:translateY(-2px);opacity:0.92;}}
.kh-mic-btn.recording{{background:linear-gradient(135deg,#dc2626,#ef4444);
  box-shadow:0 4px 14px #dc262640;}}
.kh-mic-pulse{{width:11px;height:11px;border-radius:50%;background:white;
  animation:kh-mpulse 1s ease-in-out infinite;}}
@keyframes kh-mpulse{{0%,100%{{transform:scale(1);opacity:1}}50%{{transform:scale(1.6);opacity:0.4}}}}
.kh-transcript{{
  margin-top:8px;padding:12px 16px;border-radius:12px;
  background:{T['l']};border:1.5px solid {T['s']}55;
  font-size:13px;min-height:42px;color:#333;line-height:1.6;
  {"direction:rtl;text-align:right;" if RTL else ""}
  display:none;
}}
.kh-mic-status{{font-size:11px;color:#888;text-align:center;margin-top:5px;min-height:18px;}}

.kh-result{{border-radius:16px;padding:20px;margin-bottom:12px;animation:kh-fadein 0.4s ease;}}
.kh-result.green{{background:linear-gradient(135deg,#dcfce7,#bbf7d0);border:2px solid #16a34a;}}
.kh-result.yellow{{background:linear-gradient(135deg,#fef9c3,#fde68a);border:2px solid #f59e0b;}}
.kh-result.red{{background:linear-gradient(135deg,#fee2e2,#fecaca);border:2px solid #dc2626;}}
.kh-result-head{{display:flex;align-items:center;gap:10px;margin-bottom:14px;
  {"flex-direction:row-reverse;" if RTL else ""}}}
.kh-level-badge{{padding:4px 14px;border-radius:99px;font-size:11px;font-weight:800;letter-spacing:1px;color:white;}}
.kh-level-badge.green{{background:#16a34a;}}
.kh-level-badge.yellow{{background:#d97706;}}
.kh-level-badge.red{{background:#dc2626;}}
.kh-result-title{{font-size:15px;font-weight:700;{"text-align:right;" if RTL else ""}}}
.kh-result.green .kh-result-title{{color:#065f46;}}
.kh-result.yellow .kh-result-title{{color:#78350f;}}
.kh-result.red .kh-result-title{{color:#7f1d1d;}}
.kh-steps{{display:flex;flex-direction:column;gap:6px;}}
.kh-step{{display:flex;gap:10px;align-items:flex-start;padding:9px 12px;border-radius:10px;
  font-size:13px;line-height:1.5;{"flex-direction:row-reverse;text-align:right;" if RTL else ""}}}
.kh-step.g{{background:rgba(22,163,74,0.12);color:#065f46;}}
.kh-step.y{{background:rgba(217,119,6,0.12);color:#78350f;}}
.kh-step.r{{background:rgba(220,38,38,0.12);color:#7f1d1d;}}
.kh-step-num{{width:20px;height:20px;border-radius:50%;display:flex;align-items:center;
  justify-content:center;font-size:10px;font-weight:800;flex-shrink:0;margin-top:1px;color:white;}}
.kh-step.g .kh-step-num{{background:#16a34a;}}
.kh-step.y .kh-step-num{{background:#d97706;}}
.kh-step.r .kh-step-num{{background:#dc2626;}}

.kh-disclaimer{{background:#fff8e1;border:1px solid #fcd34d;border-radius:12px;
  padding:11px 16px;font-size:11px;color:#78350f;margin:12px 0;line-height:1.6;
  {"text-align:right;" if RTL else ""}}}
.kh-emergency-main{{background:linear-gradient(135deg,#fee2e2,#fecaca);border:2px solid #dc2626;
  border-radius:18px;padding:28px;text-align:center;margin-bottom:14px;}}
.kh-emergency-num{{font-size:64px;font-weight:900;color:#dc2626;line-height:1;letter-spacing:4px;}}
.kh-hospital{{background:white;border:1px solid #e8ede8;border-radius:14px;padding:16px;
  box-shadow:0 2px 6px rgba(0,0,0,0.04);margin-bottom:10px;{"text-align:right;" if RTL else ""}}}
.kh-hospital .h-name{{font-size:12px;font-weight:700;color:#444;margin-bottom:6px;}}
.kh-hospital .h-phone{{font-size:15px;font-weight:700;color:{T['p']};margin-bottom:4px;}}
.kh-hospital .h-addr{{font-size:11px;color:#888;}}
.kh-upload-zone{{background:white;border:2px dashed #c8d5c8;border-radius:16px;
  padding:40px 20px;text-align:center;margin-bottom:14px;transition:all 0.2s ease;cursor:pointer;}}
.kh-upload-zone:hover{{border-color:{T['s']};background:{T['l']}40;}}
.kh-upload-icon{{font-size:42px;margin-bottom:12px;}}
.kh-upload-title{{font-size:15px;font-weight:700;color:#333;margin-bottom:6px;}}
.kh-upload-sub{{font-size:12px;color:#888;}}
.kh-disease-card{{background:white;border:1px solid #e8ede8;border-radius:14px;padding:16px;
  cursor:pointer;transition:all 0.18s ease;box-shadow:0 2px 6px rgba(0,0,0,0.04);margin-bottom:10px;
  {"text-align:right;" if RTL else ""}}}
.kh-disease-card:hover{{transform:translateY(-2px);border-color:{T['s']}66;box-shadow:0 6px 18px rgba(0,0,0,0.09);}}
.kh-trend-row{{display:flex;align-items:center;gap:12px;padding:12px 16px;
  border-bottom:1px solid #f0f4f0;font-size:13px;{"flex-direction:row-reverse;" if RTL else ""}}}
.kh-trend-row:last-child{{border-bottom:none;}}
.kh-level-pill{{padding:3px 10px;border-radius:99px;font-size:10px;font-weight:800;
  letter-spacing:0.5px;color:white;flex-shrink:0;}}
.kh-level-pill.green{{background:#16a34a;}}
.kh-level-pill.yellow{{background:#d97706;}}
.kh-level-pill.red{{background:#dc2626;}}
.kh-welcome-hero{{background:linear-gradient(135deg,{T['g1']},{T['g3']});
  border-radius:16px;padding:28px;text-align:center;color:white;margin-bottom:24px;}}
.kh-welcome-hero .hero-icon{{font-size:48px;animation:kh-float 3s ease-in-out infinite;display:block;margin-bottom:12px;}}
.kh-welcome-hero h2{{font-size:24px;font-weight:800;margin:0 0 6px;}}
.kh-welcome-hero p{{font-size:12px;opacity:0.8;margin:0;}}

div.stButton>button{{
  background:linear-gradient(135deg,{T['g2']},{T['g3']}) !important;
  color:white !important;border:none !important;border-radius:12px !important;
  font-weight:700 !important;font-size:13px !important;padding:10px 20px !important;
  transition:all 0.2s ease !important;box-shadow:0 4px 14px {T['p']}40 !important;
  font-family:{FONT} !important;
}}
div.stButton>button:hover{{transform:translateY(-2px) !important;box-shadow:0 7px 20px {T['p']}55 !important;opacity:0.95 !important;}}
.stTextInput>div>div>input,.stNumberInput>div>div>input,.stSelectbox>div>div>div,.stTextArea textarea{{
  border-radius:10px !important;border:1.5px solid #dde5dd !important;
  font-size:13px !important;transition:border-color 0.15s !important;
  {"direction:rtl;text-align:right;" if RTL else ""}
}}
.stTextInput>div>div>input:focus,.stNumberInput>div>div>input:focus,.stTextArea textarea:focus{{
  border-color:{T['s']} !important;box-shadow:0 0 0 3px {T['l']} !important;
}}
.stTabs [data-baseweb="tab-list"]{{background:white !important;border-radius:14px !important;
  padding:5px !important;gap:3px !important;box-shadow:0 2px 10px rgba(0,0,0,0.06) !important;
  border:1px solid #e8ede8 !important;}}
.stTabs [data-baseweb="tab"]{{border-radius:10px !important;font-weight:600 !important;
  font-size:12px !important;padding:7px 13px !important;color:#666 !important;font-family:{FONT} !important;}}
.stTabs [aria-selected="true"]{{background:linear-gradient(135deg,{T['g2']},{T['g3']}) !important;
  color:white !important;box-shadow:0 3px 10px {T['p']}40 !important;}}
.stTabs [data-baseweb="tab-highlight"],.stTabs [data-baseweb="tab-border"]{{display:none !important;}}
[data-testid="stMetricValue"]{{color:{T['p']} !important;font-weight:800 !important;font-size:26px !important;}}
[data-testid="stMetricLabel"]{{font-weight:600 !important;font-size:11px !important;
  text-transform:uppercase !important;letter-spacing:0.8px !important;color:#888 !important;}}
.stAlert{{border-radius:12px !important;font-size:13px !important;}}
hr{{border:none;border-top:1px solid #e8ede8;margin:14px 0;}}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════
# WELCOME SCREEN
# ══════════════════════════════════════
if not st.session_state.welcomed:
    is_returning = bool(st.session_state.user_name)

    if is_returning and st.session_state.profile_restored:
        st.session_state.welcomed = True
        log_visitor(st.session_state.user_name,"auto-login returning user")
        st.rerun()
    elif is_returning:
        wc1,wc2,wc3 = st.columns([1,2,1])
        with wc2:
            st.markdown(f"""
            <div class="kh-welcome-hero" style="margin-bottom:20px;border-radius:20px">
                <span class="hero-icon">👋</span>
                <h2>{L('welcome_back')}</h2>
                <p style="font-size:16px;margin-top:6px;opacity:1;font-weight:700">{st.session_state.user_name}</p>
                <p>{L('profile_restored')}</p>
            </div>""", unsafe_allow_html=True)
            if st.button(L("continue_btn"),type="primary",use_container_width=True,key="wbtn_ret"):
                st.session_state.welcomed=True
                log_visitor(st.session_state.user_name,"returning user"); st.rerun()
            st.markdown("<div style='height:8px'></div>",unsafe_allow_html=True)
            if st.button(L("not_you"),use_container_width=True,key="wfresh"):
                for k in list(DEFAULTS.keys()): st.session_state[k]=DEFAULTS[k]
                st.query_params.clear()
                components.html("<script>localStorage.removeItem('khareef_profile');sessionStorage.removeItem('kh_loaded');</script>",height=0)
                st.rerun()
    else:
        wc1,wc2,wc3 = st.columns([1,2,1])
        with wc2:
            lang_opts = ["English","العربية","বাংলা"]
            lang_labels = {"English":"🇬🇧 English","العربية":"🇴🇲 العربية","বাংলা":"🇧🇩 বাংলা"}
            w_lang = st.selectbox("🌐",lang_opts,
                index=lang_opts.index(st.session_state.language) if st.session_state.language in lang_opts else 0,
                format_func=lambda x:lang_labels[x],key="welcome_lang")
            if w_lang != st.session_state.language:
                st.session_state.language = w_lang; st.rerun()

            st.markdown(f"""
            <div class="kh-welcome-hero">
                <span class="hero-icon">🌿</span>
                <h2>Khareef Health</h2>
                <p>{L('app_subtitle')}</p>
            </div>""", unsafe_allow_html=True)

            st.markdown(f"#### {L('introduce')}")
            w_name  = st.text_input(L("your_name"),placeholder="Ahmed Al-Shanfari",key="wn")
            w_phone = st.text_input(L("phone_optional"),placeholder="+968 9X XXX XXXX",key="wp")
            _g_tx = {"English":["Not specified","Male","Female"],
                      "العربية":["غير محدد","ذكر","أنثى"],
                      "বাংলা":["অনির্দিষ্ট","পুরুষ","মহিলা"]}
            _g_labels = _g_tx.get(w_lang, _g_tx["English"])
            _g_to_en  = dict(zip(_g_labels, ["Not specified","Male","Female"]))
            _g_cur    = dict(zip(["Not specified","Male","Female"], _g_labels)).get(st.session_state.gender, _g_labels[0])
            _g_sel    = st.selectbox(L("gender"), _g_labels,
                index=_g_labels.index(_g_cur) if _g_cur in _g_labels else 0, key="wg")
            w_gender  = _g_to_en.get(_g_sel, "Not specified")

            c1,c2 = st.columns(2)
            if c1.button(L("continue_btn"),type="primary",use_container_width=True,key="wbtn"):
                st.session_state.welcomed=True; st.session_state.user_name=w_name.strip()
                st.session_state.user_phone=w_phone.strip(); st.session_state.gender=w_gender
                st.session_state.language=w_lang
                log_visitor(w_name.strip() or "Anonymous","first visit")
                save_to_localstorage(); st.rerun()
            if c2.button(L("skip_btn"),use_container_width=True,key="wskip"):
                st.session_state.welcomed=True; st.session_state.language=w_lang
                st.session_state.gender=w_gender
                log_visitor("Anonymous (skipped)","skipped welcome"); st.rerun()
            st.markdown(f"""<p style="text-align:center;font-size:11px;color:#888;margin-top:12px">{L('privacy_note')}</p>""",unsafe_allow_html=True)
    st.stop()

# ══════════════════════════════════════
# MAIN APP
# ══════════════════════════════════════
T = THEMES[st.session_state.gender]
g_emoji = "👨" if st.session_state.gender=="Male" else "👩" if st.session_state.gender=="Female" else "🌿"

# ── Header ────────────────────────────────────────
st.markdown(f"""
<div class="kh-header">
  <div class="kh-header-inner">
    <div class="kh-logo">{g_emoji}</div>
    <div class="kh-header-text">
      <h1>Khareef Health</h1>
      <p class="kh-sub">{L('app_subtitle')}</p>
      <div class="kh-badge-row">
        <span class="kh-badge">{L('ai_powered')}</span>
        <span class="kh-badge">🩺 Triage</span>
        <span class="kh-badge">📸 Skin AI</span>
        <span class="kh-badge">🎤 Voice</span>
      </div>
    </div>
    <div class="kh-emergency">
      <span class="em-label">{L('emergency_label')}</span>
      <span class="em-num">999</span>
    </div>
  </div>
  <svg class="kh-ecg" viewBox="0 0 500 20" fill="none">
    <path d="M0 10 L80 10 L95 2 L105 18 L115 5 L125 15 L135 10 L500 10"
          stroke="white" stroke-width="2.5" stroke-linecap="round"/>
  </svg>
</div>""", unsafe_allow_html=True)

# ── Settings ──────────────────────────────────────
lang_opts   = ["English","العربية","বাংলা"]
lang_labels = {"English":"🇬🇧 English","العربية":"🇴🇲 العربية","বাংলা":"🇧🇩 বাংলা"}

s1,s2,s3,s4,s5 = st.columns([1.4,1.4,0.9,0.9,0.9])
with s1:
    _gs_tx = {"English":["Not specified","Male","Female"],
               "العربية":["غير محدد","ذكر","أنثى"],
               "বাংলা":["অনির্দিষ্ট","পুরুষ","মহিলা"]}
    _gs_labels = _gs_tx.get(st.session_state.language, _gs_tx["English"])
    _gs_to_en  = dict(zip(_gs_labels, ["Not specified","Male","Female"]))
    _gs_cur    = dict(zip(["Not specified","Male","Female"], _gs_labels)).get(st.session_state.gender, _gs_labels[0])
    new_g_lbl  = st.selectbox(L("theme"), _gs_labels,
        index=_gs_labels.index(_gs_cur) if _gs_cur in _gs_labels else 0,
        key="gs", label_visibility="collapsed")
    new_g = _gs_to_en.get(new_g_lbl, "Not specified")
    if new_g != st.session_state.gender:
        st.session_state.gender=new_g; save_to_localstorage(); st.rerun()
    st.caption({"Male":L("blue_theme"),"Female":L("rose_theme"),"Not specified":L("green_theme")}[st.session_state.gender])
with s2:
    curr_idx = lang_opts.index(st.session_state.language) if st.session_state.language in lang_opts else 0
    new_lang = st.selectbox(L("language"),lang_opts,index=curr_idx,
        format_func=lambda x:lang_labels[x],key="lang_sel",label_visibility="collapsed")
    if new_lang != st.session_state.language:
        st.session_state.language=new_lang; save_to_localstorage(); st.rerun()
    st.caption(lang_labels[st.session_state.language])
with s3:
    st.session_state.khareef = st.toggle(L("khareef_toggle"),value=st.session_state.khareef,key="kt")
with s4:
    st.session_state.use_ai  = st.toggle(L("ai_toggle"),value=st.session_state.use_ai,key="git")
with s5:
    st.session_state.voice_on= st.toggle(L("voice_toggle"),value=st.session_state.voice_on,key="vt")

if st.session_state.khareef:
    st.markdown(f'<div class="kh-khareef-banner">🌦️ {L("khareef_on")}</div>',unsafe_allow_html=True)

# ── Greeting ──────────────────────────────────────
if st.session_state.user_name and st.session_state.profile_restored:
    h = datetime.now().hour
    greeting = L("good_morning") if h<12 else L("good_afternoon") if h<18 else L("good_evening")
    conds_str = f" · {', '.join(st.session_state.user_conditions[:2])}" if st.session_state.user_conditions else ""
    st.markdown(f"""
    <div class="kh-greeting">
      <div class="kh-greeting-avatar">{g_emoji}</div>
      <div class="kh-greeting-text">
        <h2>{greeting}, {st.session_state.user_name}!</h2>
        <p>{L('age')} {st.session_state.user_age} · {st.session_state.user_city} · {st.session_state.user_blood_type}{conds_str}</p>
        <p style="margin-top:4px;font-size:11px;opacity:0.8">{L('profile_ready')}</p>
      </div>
    </div>""", unsafe_allow_html=True)

# ── Stat cards ────────────────────────────────────
col1,col2,col3,col4 = st.columns(4)
with col1:
    st.markdown(f"""<div class="kh-stat"><div class="st-ico">❤️</div>
    <div class="st-lbl" style="color:#dc2626">{L('card_emergency')}</div>
    <div class="st-sub">{L('card_call999')}</div></div>""",unsafe_allow_html=True)
    if st.button(L("info_btn"),key="cem",use_container_width=True):
        st.session_state.show_card_info="emergency" if st.session_state.show_card_info!="emergency" else None
with col2:
    st.markdown(f"""<div class="kh-stat"><div class="st-ico">🩺</div>
    <div class="st-lbl" style="color:{T['p']}">{L('card_triage')}</div>
    <div class="st-sub">{L('card_triagesub')}</div></div>""",unsafe_allow_html=True)
    if st.button(L("info_btn"),key="ctr",use_container_width=True):
        st.session_state.show_card_info="triage" if st.session_state.show_card_info!="triage" else None
with col3:
    st.markdown(f"""<div class="kh-stat"><div class="st-ico">🌐</div>
    <div class="st-lbl" style="color:#1e40af">{L('card_multilang')}</div>
    <div class="st-sub">{L('card_3lang')}</div></div>""",unsafe_allow_html=True)
    if st.button(L("info_btn"),key="cla",use_container_width=True):
        st.session_state.show_card_info="bilingual" if st.session_state.show_card_info!="bilingual" else None
with col4:
    st.markdown(f"""<div class="kh-stat"><div class="st-ico">🌦️</div>
    <div class="st-lbl" style="color:#92400e">{L('card_khareef')}</div>
    <div class="st-sub">{L('card_season')}</div></div>""",unsafe_allow_html=True)
    if st.button(L("info_btn"),key="ckh",use_container_width=True):
        st.session_state.show_card_info="khareef" if st.session_state.show_card_info!="khareef" else None

if st.session_state.show_card_info=="emergency":
    with st.expander(f"🚨 {L('emergency_title')}",expanded=True):
        c1,c2,c3 = st.columns(3)
        with c1: st.error(f"**999**\n\n{L('ambulance_note')}")
        with c2: st.info("**Sultan Qaboos Hospital**\n\n+968 23 211 555")
        with c3: st.info("**Badr Al Samaa**\n\n+968 23 219 999")
elif st.session_state.show_card_info=="triage":
    with st.expander(f"🩺 {L('card_triage')}",expanded=True):
        st.markdown(f"🟢 {L('step_g1')}\n\n🟡 {L('step_y1')}\n\n🔴 {L('step_r1')}")
elif st.session_state.show_card_info=="bilingual":
    with st.expander(f"🌐 {L('card_multilang')}",expanded=True):
        st.success("English · العربية · বাংলা")
elif st.session_state.show_card_info=="khareef":
    with st.expander(f"🌦️ {L('card_khareef')}",expanded=True):
        st.warning(L("khareef_on"))

st.markdown("<hr>",unsafe_allow_html=True)

# ── Profile context ───────────────────────────────
def build_context():
    return f"""PATIENT PROFILE:
- Name: {st.session_state.get('user_name','Unknown')}
- Age: {st.session_state.get('user_age',40)} years
- Gender: {st.session_state.get('gender','Not specified')}
- Location: {st.session_state.get('user_city','Salalah')}, Oman
- Blood type: {st.session_state.get('user_blood_type','Unknown')}
- Known conditions: {', '.join(st.session_state.get('user_conditions',[])) or 'None reported'}
- Current medications: {st.session_state.get('user_medications','').strip() or 'None reported'}
- Khareef mode: {'YES' if st.session_state.get('khareef') else 'No'}
LANGUAGE INSTRUCTION: {L('ai_lang_instruction')}
Address the patient by name. Do NOT mix languages — respond ONLY in the language stated above."""

st.session_state["_profile_context"] = build_context()

# ══════════════════════════════════════
# TABS
# ══════════════════════════════════════
tabs = st.tabs([L("tab_profile"),L("tab_health"),L("tab_emergency"),
                L("tab_medicines"),L("tab_women"),L("tab_diseases"),
                L("tab_skin"),L("tab_medscan"),L("tab_trends"),L("tab_about")])
(tab_profile,tab_assess,tab_emergency,tab_medicine,tab_women,
 tab_diseases,tab_skin,tab_medscan,tab_research,tab_about) = tabs

# ── Profile tab ── fully translated, bypasses external tab_profile.py ──────────
with tab_profile:
    # Translated options
    cond_en = ["Diabetes","Hypertension","Heart Disease","Asthma","COPD",
               "Kidney Disease","Liver Disease","Cancer","Pregnancy"]
    cond_tx = {
        "English": cond_en,
        "العربية": ["السكري","ارتفاع ضغط الدم","أمراض القلب","الربو","مرض الانسداد الرئوي",
                    "أمراض الكلى","أمراض الكبد","السرطان","الحمل"],
        "বাংলা":  ["ডায়াবেটিস","উচ্চ রক্তচাপ","হৃদরোগ","হাঁপানি","সিওপিডি",
                   "কিডনি রোগ","যকৃতের রোগ","ক্যান্সার","গর্ভাবস্থা"],
    }
    gender_tx = {
        "English": ["Not specified","Male","Female"],
        "العربية": ["غير محدد","ذكر","أنثى"],
        "বাংলা":  ["অনির্দিষ্ট","পুরুষ","মহিলা"],
    }
    lang_now     = st.session_state.language
    cond_labels  = cond_tx.get(lang_now, cond_en)
    gender_labels= gender_tx.get(lang_now, gender_tx["English"])
    gender_to_en = dict(zip(gender_labels, ["Not specified","Male","Female"]))
    en_to_gender = dict(zip(["Not specified","Male","Female"], gender_labels))
    cond_to_en   = dict(zip(cond_labels, cond_en))
    en_to_cond   = dict(zip(cond_en, cond_labels))

    if st.session_state.user_name:
        st.markdown(f"""<div style="background:#d1fae5;border:1px solid #6ee7b7;border-radius:12px;
            padding:10px 16px;font-size:13px;color:#065f46;margin-bottom:14px;font-weight:600">
            ✓ {st.session_state.user_name}</div>""", unsafe_allow_html=True)

    st.markdown(f'<p class="kh-section-label">{L("personal_info")}</p>', unsafe_allow_html=True)
    c1,c2 = st.columns(2)
    with c1:
        name_val = st.text_input(L("full_name"), value=st.session_state.user_name,
            placeholder="Ahmed Al-Shanfari", key="p_name")
    with c2:
        age_val = st.number_input(L("age"), min_value=0, max_value=120,
            value=st.session_state.user_age, key="p_age")
    c1,c2 = st.columns(2)
    with c1:
        phone_val = st.text_input(L("phone"), value=st.session_state.user_phone,
            placeholder="+968 9X XXX XXXX", key="p_phone")
    with c2:
        cur_g_lbl = en_to_gender.get(st.session_state.gender, gender_labels[0])
        gender_sel = st.selectbox(L("gender"), gender_labels,
            index=gender_labels.index(cur_g_lbl) if cur_g_lbl in gender_labels else 0, key="p_gender")
        gender_val = gender_to_en.get(gender_sel, "Not specified")
    c1,c2 = st.columns(2)
    with c1:
        city_val = st.text_input(L("city"), value=st.session_state.user_city,
            placeholder="Salalah", key="p_city")
    with c2:
        bo = ["Unknown","A+","A-","B+","B-","AB+","AB-","O+","O-"]
        blood_val = st.selectbox(L("blood_type"), bo,
            index=bo.index(st.session_state.user_blood_type)
                if st.session_state.user_blood_type in bo else 0, key="p_blood")
    meds_val = st.text_input(L("medications"), value=st.session_state.user_medications,
        placeholder=L("meds_placeholder"), key="p_meds")
    cur_cond_labels = [en_to_cond.get(c,c) for c in st.session_state.user_conditions if c in cond_en]
    cond_sel = st.multiselect(L("conditions"), cond_labels, default=cur_cond_labels, key="p_conds")
    cond_val = [cond_to_en.get(c,c) for c in cond_sel]
    if st.button(L("save_profile"), use_container_width=True, key="p_save"):
        st.session_state.user_name=name_val.strip(); st.session_state.user_phone=phone_val.strip()
        st.session_state.user_age=age_val; st.session_state.gender=gender_val
        st.session_state.user_city=city_val.strip(); st.session_state.user_blood_type=blood_val
        st.session_state.user_medications=meds_val.strip(); st.session_state.user_conditions=cond_val
        save_profile({"name":name_val.strip(),"phone":phone_val.strip(),"age":age_val,
            "gender":gender_val,"city":city_val.strip(),"blood_type":blood_val,
            "medications":meds_val.strip(),"conditions":cond_val})
        save_to_localstorage(); st.success(L("profile_saved")); st.rerun()
    save_to_localstorage()

# ── Health Check tab ──────────────────────────────
with tab_assess:
    try:
        from tab_assess_full import render as ra
        ra(T,save_record,log_patient if DATA_AVAILABLE else lambda *a,**kw:None,
           is_api_key_configured,get_gemini_advice,analyze_free_text,RECORDS_FILE)
    except ImportError:
        try:
            from tabs.tab_assess import render as ra
            ra(T,save_record,log_patient if DATA_AVAILABLE else lambda *a,**kw:None,
               is_api_key_configured,get_gemini_advice,analyze_free_text,RECORDS_FILE)
        except ImportError:

            # ── Vitals ──
            st.markdown(f'<p class="kh-section-label">{L("vital_signs")}</p>',unsafe_allow_html=True)
            v1,v2,v3 = st.columns(3)
            with v1:
                temp=st.number_input(f"🌡️ {L('temperature')} (°C)",min_value=34.0,max_value=43.0,value=37.0,step=0.1,key="v_temp")
                ts="normal" if 36.1<=temp<=37.5 else "warning" if temp<=38.5 else "danger"
            with v2:
                hr=st.number_input(f"💓 {L('heart_rate')} (bpm)",min_value=30,max_value=220,value=75,key="v_hr")
                hs="normal" if 60<=hr<=100 else "warning" if 50<=hr<=120 else "danger"
            with v3:
                spo2=st.number_input(f"🫁 {L('spo2')} (%)",min_value=70,max_value=100,value=98,key="v_spo2")
                ss="normal" if spo2>=95 else "warning" if spo2>=90 else "danger"

            st.markdown(f"""
            <div class="kh-vitals">
              <div class="kh-vital"><div class="kh-vital-label">{L('temperature')}</div>
                <div class="kh-vital-value">{temp:.1f}</div><div class="kh-vital-unit">°C</div>
                <div class="kh-vital-bar {ts}"></div></div>
              <div class="kh-vital"><div class="kh-vital-label">{L('heart_rate')}</div>
                <div class="kh-vital-value">{hr}</div><div class="kh-vital-unit">bpm</div>
                <div class="kh-vital-bar {hs}"></div></div>
              <div class="kh-vital"><div class="kh-vital-label">{L('spo2')}</div>
                <div class="kh-vital-value">{spo2}</div><div class="kh-vital-unit">%</div>
                <div class="kh-vital-bar {ss}"></div></div>
            </div>""",unsafe_allow_html=True)

            # ── Symptoms ──
            st.markdown(f'<p class="kh-section-label">{L("symptoms_label")}</p>',unsafe_allow_html=True)
            sym_keys=["sym_fever","sym_cough","sym_headache","sym_fatigue","sym_chest","sym_breath",
                      "sym_nausea","sym_vomiting","sym_dizziness","sym_backpain","sym_throat",
                      "sym_runny","sym_muscle","sym_rash","sym_abdominal","sym_diarrhea","sym_joint","sym_confusion"]
            sym_en=["Fever","Cough","Headache","Fatigue","Chest pain","Shortness of breath",
                    "Nausea","Vomiting","Dizziness","Back pain","Sore throat","Runny nose",
                    "Muscle aches","Rash","Abdominal pain","Diarrhea","Joint pain","Confusion"]
            sym_labels=[L(k) for k in sym_keys]
            lbl_to_en=dict(zip(sym_labels,sym_en))

            selected_display=st.multiselect(L("select_symptoms"),sym_labels,
                placeholder=L("select_symptoms"),key="v_symptoms")
            selected_syms=[lbl_to_en.get(s,s) for s in selected_display]

            # ── Voice input ──
            st.markdown(f'<p class="kh-section-label">{L("voice_input_label")}</p>',unsafe_allow_html=True)
            speech_lang = L("speech_lang")

            if VOICE_ENABLED and st.session_state.voice_on:
                lang_code = get_lang_code(st.session_state.language)
                transcript = voice_input_component(key="voice_health",lang=lang_code,
                    placeholder=L("describe_placeholder"))
                if transcript:
                    st.session_state.voice_transcript = transcript
            elif st.session_state.voice_on:
                # Browser Web Speech API
                stop_txt  = L("stop_recording")
                listen_txt= L("listening")
                done_txt  = L("recorded")
                mic_txt   = L("voice_input_label")
                components.html(f"""
<style>
.kh-mic-btn{{display:flex;align-items:center;justify-content:center;gap:10px;width:100%;
  background:linear-gradient(135deg,{T['g2']},{T['g3']});color:white;border:none;
  border-radius:12px;padding:13px 20px;font-size:14px;font-weight:700;cursor:pointer;
  box-shadow:0 4px 14px {T['p']}40;transition:all 0.2s ease;font-family:sans-serif;}}
.kh-mic-btn:hover{{transform:translateY(-2px);opacity:0.92;}}
.kh-mic-btn.recording{{background:linear-gradient(135deg,#dc2626,#ef4444);box-shadow:0 4px 14px #dc262640;}}
.kh-mic-pulse{{width:11px;height:11px;border-radius:50%;background:white;
  animation:kmpulse 1s ease-in-out infinite;}}
@keyframes kmpulse{{0%,100%{{transform:scale(1);opacity:1}}50%{{transform:scale(1.6);opacity:0.4}}}}
.kh-transcript{{margin-top:8px;padding:12px 16px;border-radius:12px;
  background:{T['l']};border:1.5px solid {T['s']}55;font-size:13px;min-height:42px;
  color:#333;line-height:1.6;{"direction:rtl;text-align:right;" if RTL else ""}display:none;}}
.kh-mic-status{{font-size:11px;color:#888;text-align:center;margin-top:5px;min-height:18px;}}
</style>
<button class="kh-mic-btn" id="micBtn" onclick="toggleMic()">
  🎤 {mic_txt}
</button>
<div class="kh-transcript" id="transcript"></div>
<div class="kh-mic-status" id="micStatus"></div>
<script>
var recog, isRec=false;
var SR=window.SpeechRecognition||window.webkitSpeechRecognition;
function toggleMic(){{
  if(!SR){{document.getElementById('micStatus').innerText='Use Chrome for voice input.';return;}}
  if(isRec){{recog.stop();return;}}
  recog=new SR();
  recog.lang='{speech_lang}';
  recog.continuous=false;
  recog.interimResults=true;
  var btn=document.getElementById('micBtn');
  var box=document.getElementById('transcript');
  var st=document.getElementById('micStatus');
  recog.onstart=function(){{
    isRec=true;btn.classList.add('recording');
    btn.innerHTML='<div class="kh-mic-pulse"></div> {stop_txt}';
    st.innerText='{listen_txt}';box.style.display='block';
  }};
  recog.onresult=function(e){{
    var t=Array.from(e.results).map(r=>r[0].transcript).join('');
    box.innerText=t;
  }};
  recog.onend=function(){{
    isRec=false;btn.classList.remove('recording');
    btn.innerHTML='🎤 {mic_txt}';
    if(box.innerText){{st.innerText='{done_txt}';}}else{{st.innerText='';}}
  }};
  recog.onerror=function(e){{
    isRec=false;btn.classList.remove('recording');
    btn.innerHTML='🎤 {mic_txt}';
    st.innerText='Error: '+e.error+'. Try typing below.';
  }};
  recog.start();
}}
</script>""",height=130)
            else:
                st.caption("🎤 " + L("voice_toggle") + " is OFF")

            # Text area — prefilled with voice transcript if available
            free_text = st.text_area(L("describe_feel"),
                value=st.session_state.get("voice_transcript",""),
                placeholder=L("describe_placeholder"),height=90,key="v_freetext")

            # ── Buttons ──
            cb1,cb2 = st.columns([3,1])
            with cb1: assess_clicked=st.button(L("assess_btn"),use_container_width=True,key="v_assess")
            with cb2:
                if st.button(L("reset_btn"),use_container_width=True,key="v_reset"):
                    st.session_state.voice_transcript=""
                    st.rerun()

            if assess_clicked:
                danger_s={"chest pain","shortness of breath","confusion"}
                warn_s  ={"fever","headache","nausea","vomiting","dizziness"}
                sel_low ={s.lower() for s in selected_syms}

                if temp>=39.5 or spo2<90 or hr>130 or hr<45 or sel_low&danger_s:
                    level,cls="RED","red"
                    title=L("result_red_title")
                    steps=[("r",L("step_r1")),("r",L("step_r2")),("r",L("step_r3"))]
                elif temp>=38.0 or spo2<95 or hr>100 or hr<55 or sel_low&warn_s:
                    level,cls="YELLOW","yellow"
                    title=L("result_yellow_title")
                    steps=[("y",L("step_y1")),("y",L("step_y2")),("y",L("step_y3")),("y",L("step_y4"))]
                else:
                    level,cls="GREEN","green"
                    title=L("result_green_title")
                    steps=[("g",L("step_g1")),("g",L("step_g2")),("g",L("step_g3")),("g",L("step_g4"))]

                steps_html="".join(f'<div class="kh-step {c}"><div class="kh-step-num">{i+1}</div><div>{s}</div></div>'
                    for i,(c,s) in enumerate(steps))

                st.markdown(f"""
                <div class="kh-result {cls}">
                  <div class="kh-result-head">
                    <span class="kh-level-badge {cls}">{level}</span>
                    <span class="kh-result-title">{title}</span>
                  </div>
                  <div class="kh-steps">{steps_html}</div>
                </div>""",unsafe_allow_html=True)

                # ── TTS: speak result in user's language ──
                tts_text = f"{level}. {title}. " + " ".join(s for _,s in steps)
                tts_lang = L("tts_lang")

                if st.session_state.voice_on:
                    if VOICE_ENABLED:
                        text_to_speech_component(tts_text,lang=get_tts_code(st.session_state.language))
                    else:
                        safe=tts_text.replace("'","").replace('"','').replace('\n',' ')
                        components.html(f"""<script>
(function(){{try{{
  window.speechSynthesis.cancel();
  var u=new SpeechSynthesisUtterance({json.dumps(safe)});
  u.lang='{tts_lang}';u.rate=0.9;
  window.speechSynthesis.speak(u);
}}catch(e){{console.error('TTS:',e);}}
}})();</script>""",height=0)

                # ── AI advice ──
                if st.session_state.use_ai and is_api_key_configured():
                    with st.spinner(L("getting_ai")):
                        syms_str=", ".join(selected_syms) if selected_syms else "none"
                        prompt=f"""{st.session_state.get('_profile_context','')}

VITALS: Temp={temp}°C, HR={hr}bpm, SpO2={spo2}%
SYMPTOMS: {syms_str}
DESCRIPTION: {free_text or 'none'}
TRIAGE RESULT: {level}

Give concise personalised health advice: what to do next, any warnings, when to seek emergency care.
CRITICAL: {L('ai_lang_instruction')} Do NOT use any other language."""
                        advice=get_gemini_advice(prompt)
                        if advice:
                            with st.expander(L("ai_advice_title"),expanded=True):
                                st.markdown(advice)
                            # TTS for AI advice
                            if st.session_state.voice_on:
                                clean=advice.replace("*","").replace("#","").replace("`","")[:600]
                                if VOICE_ENABLED:
                                    text_to_speech_component(clean,lang=get_tts_code(st.session_state.language))
                                else:
                                    safe2=clean.replace("'","").replace('"','').replace('\n',' ')
                                    components.html(f"""<script>
setTimeout(function(){{try{{
  window.speechSynthesis.cancel();
  var u=new SpeechSynthesisUtterance({json.dumps(safe2)});
  u.lang='{tts_lang}';u.rate=0.9;
  window.speechSynthesis.speak(u);
}}catch(e){{}}
}},2500);</script>""",height=0)

                save_record({"timestamp":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "name":st.session_state.user_name,"age":st.session_state.user_age,
                    "temp":temp,"hr":hr,"spo2":spo2,"symptoms":selected_syms,"level":level,
                    "khareef":st.session_state.khareef,"language":st.session_state.language})

            st.markdown(f'<div class="kh-disclaimer">{L("disclaimer")}</div>',unsafe_allow_html=True)

# ── Emergency tab ─────────────────────────────────
with tab_emergency:
    try:
        from tabs.tab_emergency import render; render(T)
    except ImportError:
        st.markdown(f"""
        <div class="kh-emergency-main">
          <div style="font-size:13px;font-weight:700;color:#dc2626;letter-spacing:2px;margin-bottom:10px">{L('emergency_title')}</div>
          <div class="kh-emergency-num">999</div>
          <div style="font-size:13px;color:#7f1d1d;margin-top:8px">{L('ambulance_note')}</div>
        </div>""",unsafe_allow_html=True)
        st.markdown(f'<p class="kh-section-label">{L("hospitals_label")}</p>',unsafe_allow_html=True)
        hosps=[("Sultan Qaboos Hospital","+968 23 211 555","Al Dahariz, Salalah","Government · 24h"),
               ("Badr Al Samaa Salalah","+968 23 219 999","Salalah","Private · 24h"),
               ("Al Nahdha Hospital","+968 23 218 900","Salalah","Government"),
               ("Ibin Sina Medical","+968 23 294 000","Salalah","Private")]
        cols=st.columns(2)
        for i,(nm,ph,ad,nt) in enumerate(hosps):
            with cols[i%2]:
                st.markdown(f'<div class="kh-hospital"><div class="h-name">{nm}</div>'
                    f'<div class="h-phone">{ph}</div><div class="h-addr">{ad} · {nt}</div></div>',unsafe_allow_html=True)
        st.markdown(f'<p class="kh-section-label">{L("warning_signs")}</p>',unsafe_allow_html=True)
        lang=st.session_state.language
        signs={"العربية":["ألم أو ضغط في الصدر","صعوبة في التنفس","صداع شديد ومفاجئ",
                           "علامات السكتة الدماغية","نزيف لا يمكن إيقافه","فقدان الوعي",
                           "رد فعل تحسسي شديد","SpO₂ أقل من 90٪"],
               "বাংলা":["বুকে ব্যথা","শ্বাসকষ্ট","হঠাৎ তীব্র মাথাব্যথা","স্ট্রোকের লক্ষণ",
                         "অনিয়ন্ত্রিত রক্তপাত","জ্ঞান হারানো","তীব্র অ্যালার্জি","SpO₂ ৯০% এর নিচে"],
               "English":["Chest pain or pressure","Difficulty breathing","Sudden severe headache",
                          "Signs of stroke (FAST)","Uncontrolled bleeding","Loss of consciousness",
                          "Severe allergic reaction","SpO₂ below 90%"]}
        sl=signs.get(lang,signs["English"])
        c1,c2=st.columns(2)
        for i,s in enumerate(sl):
            with(c1 if i%2==0 else c2):
                st.markdown(f'<div class="kh-step r" style="margin-bottom:5px">'
                    f'<div class="kh-step-num" style="background:#dc2626">!</div>'
                    f'<div><strong>{s}</strong></div></div>',unsafe_allow_html=True)

# ── Medicines tab ─────────────────────────────────
with tab_medicine:
    try:
        from tabs.tab_medicine import render; render(T)
    except ImportError:
        st.info(f"💊 {L('tab_medicines')}")

# ── Women tab ─────────────────────────────────────
with tab_women:
    try:
        from tabs.tab_women import render; render(T)
    except ImportError:
        st.info(f"👩 {L('tab_women')}")

# ── Diseases tab ──────────────────────────────────
with tab_diseases:
    try:
        from tabs.tab_diseases import render
        render(T,DISEASES,CATEGORIES,search_diseases,get_by_category)
    except ImportError:
        st.markdown(f'<p class="kh-section-label">{L("tab_diseases")}</p>',unsafe_allow_html=True)
        search_q=st.text_input(L("search_diseases"),placeholder=L("search_placeholder"),key="dis_s")
        lang=st.session_state.language
        DIS=[
            ("🦟",{"English":"Malaria","العربية":"ملاريا","বাংলা":"ম্যালেরিয়া"},
             {"English":"Mosquito-borne parasitic infection — higher risk during Khareef",
              "العربية":"عدوى طفيلية تنقلها البعوض — خطر أعلى في موسم الخريف",
              "বাংলা":"মশাবাহিত পরজীবী সংক্রমণ — খারিফ মৌসুমে বেশি ঝুঁকি"},
             "Fever, chills, headache, muscle aches","#fee2e2","#7f1d1d"),
            ("🌡️",{"English":"Dengue Fever","العربية":"حمى الضنك","বাংলা":"ডেঙ্গু জ্বর"},
             {"English":"Viral infection transmitted by Aedes mosquitoes",
              "العربية":"عدوى فيروسية تنقلها بعوضة الأيدس",
              "বাংলা":"Aedes মশার মাধ্যমে ছড়ানো ভাইরাল সংক্রমণ"},
             "High fever, severe headache, rash, joint pain","#fef9c3","#78350f"),
            ("🫁",{"English":"Respiratory Infections","العربية":"التهابات الجهاز التنفسي","বাংলা":"শ্বাসযন্ত্রের সংক্রমণ"},
             {"English":"Common in Khareef due to humidity and mold",
              "العربية":"شائعة في موسم الخريف بسبب الرطوبة والعفن",
              "বাংলা":"খারিফ মৌসুমে আর্দ্রতা ও ছাঁচের কারণে সাধারণ"},
             "Cough, fever, difficulty breathing","#dbeafe","#1e40af"),
            ("☀️",{"English":"Heat Exhaustion","العربية":"الإجهاد الحراري","বাংলা":"তাপ বিকার"},
             {"English":"Overheating due to high temperature and humidity",
              "العربية":"ارتفاع الحرارة بسبب الرطوبة العالية",
              "বাংলা":"উচ্চ তাপমাত্রা ও আর্দ্রতার কারণে"},
             "Sweating, weakness, dizziness, nausea","#fff7ed","#9a3412"),
            ("💧",{"English":"Gastroenteritis","العربية":"التهاب المعدة والأمعاء","বাংলা":"গ্যাস্ট্রোএন্টেরাইটিস"},
             {"English":"Stomach and intestinal infection",
              "العربية":"عدوى في المعدة والأمعاء",
              "বাংলা":"পাকস্থলী ও অন্ত্রের সংক্রমণ"},
             "Diarrhea, vomiting, abdominal cramps","#d1fae5","#065f46"),
        ]
        for icon,names,descs,syms,bg,tc in DIS:
            name=names.get(lang,names["English"])
            desc=descs.get(lang,descs["English"])
            if search_q and search_q.lower() not in name.lower() and search_q.lower() not in names["English"].lower():
                continue
            st.markdown(f'<div class="kh-disease-card" style="border-left:4px solid {tc}">'
                f'<div style="font-size:22px;margin-bottom:8px">{icon}</div>'
                f'<div style="font-size:14px;font-weight:700;color:{tc};margin-bottom:5px">{name}</div>'
                f'<div style="font-size:12px;color:#555;margin-bottom:8px">{desc}</div>'
                f'<div style="font-size:11px;font-weight:600;color:#888;margin-bottom:3px">{L("symptoms_col")}</div>'
                f'<div style="font-size:12px;color:#444">{syms}</div></div>',unsafe_allow_html=True)

# ── Skin AI tab ───────────────────────────────────
with tab_skin:
    try:
        from tabs.tab_skin import render; render(T,GEMINI_API_KEY,is_api_key_configured)
    except ImportError:
        st.markdown(f'<div class="kh-upload-zone"><div class="kh-upload-icon">📸</div>'
            f'<div class="kh-upload-title">{L("skin_title")}</div>'
            f'<div class="kh-upload-sub">{L("skin_sub")}</div></div>',unsafe_allow_html=True)
        upl=st.file_uploader(L("skin_upload"),type=["jpg","jpeg","png"],key="skin_upl",label_visibility="collapsed")
        if upl:
            st.image(upl,use_column_width=True)
            if st.session_state.use_ai and is_api_key_configured():
                if st.button(L("analyse_btn"),use_container_width=True,key="skin_btn"):
                    st.info("🤖 Connecting AI skin analysis...")
            else:
                st.warning(L("ai_not_conf"))
        st.markdown(f'<div class="kh-disclaimer">{L("disclaimer")}</div>',unsafe_allow_html=True)

# ── Med Scanner tab ───────────────────────────────
with tab_medscan:
    try:
        from tabs.tab_medscan import render; render(T,GEMINI_API_KEY,is_api_key_configured)
    except ImportError:
        st.markdown(f'<div class="kh-upload-zone"><div class="kh-upload-icon">💊</div>'
            f'<div class="kh-upload-title">{L("med_title")}</div>'
            f'<div class="kh-upload-sub">{L("med_sub")}</div></div>',unsafe_allow_html=True)
        upm=st.file_uploader(L("med_upload"),type=["jpg","jpeg","png"],key="med_upl",label_visibility="collapsed")
        if upm:
            st.image(upm,use_column_width=True)
            if st.session_state.use_ai and is_api_key_configured():
                if st.button(L("scan_btn"),use_container_width=True,key="med_btn"):
                    st.info("🤖 Connecting AI medicine scanner...")

# ── Trends tab ────────────────────────────────────
with tab_research:
    try:
        from tabs.tab_research import render; render(T,load_json,RECORDS_FILE)
    except ImportError:
        recs=load_json(RECORDS_FILE)
        urecs=[r for r in recs if r.get("name","")==st.session_state.user_name] if st.session_state.user_name else recs
        urecs=sorted(urecs,key=lambda x:x.get("timestamp",""),reverse=True)
        tot=len(urecs); gc=sum(1 for r in urecs if r.get("level","")=="GREEN"); oc=tot-gc
        m1,m2,m3=st.columns(3)
        m1.metric(L("total_assess"),tot); m2.metric(L("green_results"),gc); m3.metric(L("yellow_red"),oc)
        st.markdown(f'<p class="kh-section-label">{L("recent_assess")}</p>',unsafe_allow_html=True)
        if urecs:
            lm={"GREEN":"green","YELLOW":"yellow","RED":"red"}
            rows="".join(f'<div class="kh-trend-row"><span class="kh-level-pill {lm.get(r.get("level","GREEN"),"green")}">{r.get("level","GREEN")}</span>'
                f'<span style="flex:1;font-size:13px">{", ".join(r.get("symptoms",[])[:3]) or "—"}</span>'
                f'<span style="font-size:11px;color:#999">{r.get("timestamp","")[:10]}</span></div>'
                for r in urecs[:20])
            st.markdown(f'<div style="background:white;border-radius:14px;border:1px solid #e8ede8;overflow:hidden">{rows}</div>',unsafe_allow_html=True)
        else:
            st.info(L("no_records"))

# ── About tab ─────────────────────────────────────
with tab_about:
    try:
        from tabs.tab_about import render; render(T)
    except ImportError:
        st.markdown(f"""<div class="kh-card" style="text-align:center">
          <div style="font-size:48px;margin-bottom:12px">🌿</div>
          <div style="font-size:20px;font-weight:800;color:{T['p']};margin-bottom:4px">Khareef Health</div>
          <div style="font-size:12px;color:#888;margin-bottom:16px">v4.2 · by Sadga Selime · Salalah, Oman</div>
          <div style="font-size:13px;color:#555;line-height:1.8;max-width:500px;margin:0 auto">{L('about_desc')}</div>
        </div>""",unsafe_allow_html=True)
        st.markdown(f'<div class="kh-disclaimer">{L("disclaimer_full")}</div>',unsafe_allow_html=True)

# ── Admin ─────────────────────────────────────────
if st.query_params.get("admin","")=="true":
    try:
        from tabs.tab_admin import render
        render(load_json,save_json,RECORDS_FILE,PROFILES_FILE,VISITORS_FILE)
    except ImportError:
        st.warning("Admin module not found.")

# ── Footer ────────────────────────────────────────
st.markdown("<hr>",unsafe_allow_html=True)
st.markdown(f"""<div style="text-align:center;padding:8px 0 16px;font-size:11px;color:#aaa">
  🌿 Khareef Health v4.2 · by Sadga Selime · Salalah, Oman<br>
  Powered by Google Gemini AI · Educational use only
  · <strong style="color:#dc2626">999</strong>
</div>""",unsafe_allow_html=True)
