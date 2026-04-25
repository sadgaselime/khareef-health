# Voice-enabled health assessment tab example

import streamlit as st
from voice_utils import voice_input_component, text_to_speech_component, get_voice_input_value
from translations import t, get_lang_code, get_tts_code

def render_voice_assessment():
    """
    Health assessment with voice input/output.
    Works for users who can't read/write.
    """
    
    lang = st.session_state.get("language", "English")
    lang_code = get_lang_code(lang)
    tts_code = get_tts_code(lang)
    
    st.markdown(f"### {t('health_check', lang)}")
    
    # Instructions
    instructions = {
        "English": "Describe your symptoms below. You can type OR speak.",
        "العربية": "صف أعراضك أدناه. يمكنك الكتابة أو التحدث.",
        "বাংলা": "নীচে আপনার লক্ষণ বর্ণনা করুন। আপনি টাইপ করতে বা বলতে পারেন।"
    }
    st.info(instructions[lang])
    
    # Voice input
    st.markdown(f"#### {t('speak_symptoms', lang)}")
    voice_input_component(lang_code=lang_code, key="symptoms_voice")
    
    # Get voice text
    voice_text = get_voice_input_value("symptoms_voice")
    
    # Text input (fallback)
    st.markdown(f"#### {t('describe_symptoms', lang)}")
    symptoms_text = st.text_area(
        label="",
        value=voice_text,
        height=100,
        placeholder={
            "English": "e.g., I have fever and headache for 2 days...",
            "العربية": "مثال: لدي حمى وصداع منذ يومين...",
            "বাংলা": "উদাহরণ: আমার ২ দিন ধরে জ্বর এবং মাথাব্যথা আছে..."
        }[lang],
        key="symptoms_text"
    )
    
    # Assess button
    if st.button(f"✓ {t('continue', lang)}", type="primary", use_container_width=True):
        if symptoms_text.strip():
            st.session_state.assessment_result = assess_symptoms(symptoms_text, lang)
            st.rerun()
        else:
            st.warning({
                "English": "Please describe your symptoms",
                "العربية": "الرجاء وصف أعراضك",
                "বাংলা": "দয়া করে আপনার লক্ষণ বর্ণনা করুন"
            }[lang])
    
    # Show result
    if "assessment_result" in st.session_state and st.session_state.assessment_result:
        result = st.session_state.assessment_result
        
        st.markdown("---")
        st.markdown(f"### {t('result', lang)}")
        
        # Color based on severity
        if result["level"] == "GREEN":
            st.success(result["message"])
        elif result["level"] == "YELLOW":
            st.warning(result["message"])
        else:
            st.error(result["message"])
        
        # Recommendation
        st.markdown(f"#### {t('recommendation', lang)}")
        st.write(result["recommendation"])
        
        # Text-to-speech button
        st.markdown("---")
        full_text = f"{result['message']}. {result['recommendation']}"
        text_to_speech_component(full_text, tts_code, auto_play=False)
        
        st.caption({
            "English": "👆 Click to hear the result in your language",
            "العربية": "👆 انقر لسماع النتيجة بلغتك",
            "বাংলা": "👆 আপনার ভাষায় ফলাফল শুনতে ক্লিক করুন"
        }[lang])


def assess_symptoms(symptoms, lang):
    """
    Simple symptom assessment.
    In real app, use AI/medical logic.
    """
    
    symptoms_lower = symptoms.lower()
    
    # Check for emergency keywords
    emergency_words = ["chest pain", "difficulty breathing", "unconscious", "bleeding heavily",
                       "ألم في الصدر", "صعوبة في التنفس", "فاقد الوعي", "نزيف شديد",
                       "বুকে ব্যথা", "শ্বাসকষ্ট", "অজ্ঞান", "ভারী রক্তপাত"]
    
    if any(word in symptoms_lower for word in emergency_words):
        return {
            "level": "RED",
            "message": {
                "English": "🚨 URGENT: This requires immediate medical attention!",
                "العربية": "🚨 عاجل: هذا يتطلب عناية طبية فورية!",
                "বাংলা": "🚨 জরুরী: এর জন্য তাৎক্ষণিক চিকিৎসা প্রয়োজন!"
            }[lang],
            "recommendation": {
                "English": "Call 999 or go to emergency room NOW.",
                "العربية": "اتصل بـ 999 أو اذهب إلى غرفة الطوارئ الآن.",
                "বাংলা": "এখনই ৯৯৯ এ কল করুন বা জরুরী কক্ষে যান।"
            }[lang]
        }
    
    # Check for moderate symptoms
    moderate_words = ["fever", "vomit", "pain", "حمى", "قيء", "ألم", "জ্বর", "বমি", "ব্যথা"]
    
    if any(word in symptoms_lower for word in moderate_words):
        return {
            "level": "YELLOW",
            "message": {
                "English": "⚠️ MODERATE: You should see a doctor soon.",
                "العربية": "⚠️ متوسط: يجب أن ترى طبيبًا قريبًا.",
                "বাংলা": "⚠️ মাঝারি: আপনার শীঘ্রই একজন ডাক্তার দেখা উচিত।"
            }[lang],
            "recommendation": {
                "English": "Book an appointment within 24-48 hours. Rest and stay hydrated.",
                "العربية": "احجز موعدًا خلال 24-48 ساعة. استرح واشرب الماء.",
                "বাংলা": "২৪-৪৮ ঘন্টার মধ্যে একটি অ্যাপয়েন্টমেন্ট করুন। বিশ্রাম নিন এবং হাইড্রেটেড থাকুন।"
            }[lang]
        }
    
    # Mild symptoms
    return {
        "level": "GREEN",
        "message": {
            "English": "✓ MILD: Your symptoms appear mild.",
            "العربية": "✓ خفيف: تبدو أعراضك خفيفة.",
            "বাংলা": "✓ হালকা: আপনার লক্ষণগুলি হালকা বলে মনে হয়।"
        }[lang],
        "recommendation": {
            "English": "Rest at home, drink fluids. See doctor if symptoms worsen.",
            "العربية": "استرح في المنزل، اشرب السوائل. راجع الطبيب إذا ساءت الأعراض.",
            "বাংলা": "বাড়িতে বিশ্রাম নিন, তরল পান করুন। লক্ষণ খারাপ হলে ডাক্তার দেখান।"
        }[lang]
    }
