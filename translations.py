# Language translations for Khareef Health

LANGUAGES = {
    "English": {
        "code": "en-US",
        "flag": "🇬🇧",
        "tts_code": "en-US",
    },
    "العربية": {
        "code": "ar-SA",
        "flag": "🇸🇦",
        "tts_code": "ar-SA",
    },
    "বাংলা": {
        "code": "bn-BD",
        "flag": "🇧🇩",
        "tts_code": "bn-BD",
    }
}

TRANSLATIONS = {
    # Navigation
    "profile": {"English": "Profile", "العربية": "الملف الشخصي", "বাংলা": "প্রোফাইল"},
    "health_check": {"English": "Health Check", "العربية": "الفحص الصحي", "বাংলা": "স্বাস্থ্য পরীক্ষা"},
    "emergency": {"English": "Emergency", "العربية": "طوارئ", "বাংলা": "জরুরী"},
    "medicines": {"English": "Medicines", "العربية": "أدوية", "বাংলা": "ওষুধ"},
    "women": {"English": "Women", "العربية": "النساء", "বাংলা": "মহিলা"},
    "diseases": {"English": "Diseases", "العربية": "أمراض", "বাংলা": "রোগ"},
    "about": {"English": "About", "العربية": "معلومات", "বাংলা": "সম্পর্কে"},
    
    # Welcome screen
    "welcome": {"English": "Welcome", "العربية": "مرحبا", "বাংলা": "স্বাগতম"},
    "welcome_back": {"English": "Welcome back", "العربية": "مرحبا بعودتك", "বাংলা": "ফিরে আসার জন্য স্বাগতম"},
    "introduce_yourself": {"English": "Please introduce yourself", "العربية": "من فضلك عرّف بنفسك", "বাংলা": "দয়া করে নিজের পরিচয় দিন"},
    "your_name": {"English": "Your Name", "العربية": "اسمك", "বাংলা": "আপনার নাম"},
    "phone_optional": {"English": "Phone (optional)", "العربية": "الهاتف (اختياري)", "বাংলা": "ফোন (ঐচ্ছিক)"},
    "continue": {"English": "Continue", "العربية": "متابعة", "বাংলা": "চালিয়ে যান"},
    "skip": {"English": "Skip", "العربية": "تخطي", "বাংলা": "এড়িয়ে যান"},
    
    # Profile
    "full_name": {"English": "Full Name", "العربية": "الاسم الكامل", "বাংলা": "পুরো নাম"},
    "age": {"English": "Age", "العربية": "العمر", "বাংলা": "বয়স"},
    "gender": {"English": "Gender", "العربية": "الجنس", "বাংলা": "লিঙ্গ"},
    "male": {"English": "Male", "العربية": "ذكر", "বাংলা": "পুরুষ"},
    "female": {"English": "Female", "العربية": "أنثى", "বাংলা": "মহিলা"},
    "not_specified": {"English": "Not specified", "العربية": "غير محدد", "বাংলা": "নির্দিষ্ট নয়"},
    "city": {"English": "City", "العربية": "المدينة", "বাংলা": "শহর"},
    "blood_type": {"English": "Blood Type", "العربية": "فصيلة الدم", "বাংলা": "রক্তের গ্রুপ"},
    "save_profile": {"English": "Save Profile", "العربية": "حفظ الملف", "বাংলা": "প্রোফাইল সংরক্ষণ করুন"},
    
    # Health assessment
    "describe_symptoms": {"English": "Describe your symptoms", "العربية": "صف أعراضك", "বাংলা": "আপনার লক্ষণ বর্ণনা করুন"},
    "speak_symptoms": {"English": "🎤 Speak your symptoms", "العربية": "🎤 تحدث عن أعراضك", "বাংলা": "🎤 আপনার লক্ষণ বলুন"},
    "stop_recording": {"English": "⏹️ Stop recording", "العربية": "⏹️ إيقاف التسجيل", "বাংলা": "⏹️ রেকর্ডিং বন্ধ করুন"},
    "recording": {"English": "Recording...", "العربية": "جاري التسجيل...", "বাংলা": "রেকর্ডিং..."},
    "assessing": {"English": "Assessing your condition...", "العربية": "تقييم حالتك...", "বাংলা": "আপনার অবস্থা মূল্যায়ন করা হচ্ছে..."},
    
    # Results
    "result": {"English": "Result", "العربية": "النتيجة", "বাংলা": "ফলাফল"},
    "read_aloud": {"English": "🔊 Read result aloud", "العربية": "🔊 اقرأ النتيجة بصوت عالٍ", "বাংলা": "🔊 ফলাফল জোরে পড়ুন"},
    "recommendation": {"English": "Recommendation", "العربية": "التوصية", "বাংলা": "সুপারিশ"},
    
    # Common
    "loading": {"English": "Loading...", "العربية": "جاري التحميل...", "বাংলা": "লোড হচ্ছে..."},
    "error": {"English": "Error", "العربية": "خطأ", "বাংলা": "ত্রুটি"},
    "success": {"English": "Success", "العربية": "نجاح", "বাংলা": "সফল"},
    "close": {"English": "Close", "العربية": "إغلاق", "বাংলা": "বন্ধ করুন"},
}

def t(key, lang="English"):
    """Get translation. Returns key if not found."""
    return TRANSLATIONS.get(key, {}).get(lang, key)

def get_lang_code(lang):
    """Get speech recognition code for language."""
    return LANGUAGES.get(lang, {}).get("code", "en-US")

def get_tts_code(lang):
    """Get text-to-speech code for language."""
    return LANGUAGES.get(lang, {}).get("tts_code", "en-US")
