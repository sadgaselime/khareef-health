import streamlit as st
import streamlit.components.v1 as components

def render(T, save_record, log_patient, is_api_configured, 
           get_gemini_advice, analyze_free_text, RECORDS_FILE):
    """
    Full multilingual voice-enabled health assessment
    """
    
    # Get language
    lang = st.session_state.get("language", "English")
    
    # Check if voice enabled
    try:
        from translations import t, get_lang_code, get_tts_code
        from voice_utils import voice_input_component, text_to_speech_component
        VOICE_ENABLED = True
        lang_code = get_lang_code(lang)
        tts_code = get_tts_code(lang)
    except:
        VOICE_ENABLED = False
        t = lambda k, l: k  # Fallback
    
    # UI Text
    UI = {
        "English": {
            "title": "🩺 AI Health Assessment",
            "subtitle": "Describe your symptoms - Type OR Speak",
            "speak_btn": "🎤 Speak Your Symptoms",
            "stop_btn": "⏹️ Stop Recording",
            "recording": "🔴 Recording... speak now",
            "type_placeholder": "Example: I have fever and headache for 2 days, body pain, feeling weak...",
            "assess_btn": "Assess My Health",
            "assessing": "🔄 Analyzing your symptoms...",
            "result_title": "📋 Assessment Result",
            "listen_btn": "🔊 Listen to Result",
            "recommendation": "💡 Recommendation",
            "emergency_warning": "⚠️ EMERGENCY",
            "emergency_text": "This requires IMMEDIATE medical attention!",
            "emergency_action": "📞 Call 999 NOW or go to nearest hospital",
            "moderate_warning": "⚠️ MEDICAL ATTENTION NEEDED",
            "moderate_text": "You should see a doctor soon",
            "moderate_action": "📅 Book appointment within 24-48 hours",
            "mild_text": "Your symptoms appear mild",
            "mild_action": "🏠 Rest at home, monitor symptoms",
            "when_emergency": "When to call 999",
            "emergency_signs": "• Chest pain\n• Difficulty breathing\n• Heavy bleeding\n• Loss of consciousness\n• Severe allergic reaction",
        },
        "العربية": {
            "title": "🩺 تقييم الصحة بالذكاء الاصطناعي",
            "subtitle": "صف أعراضك - اكتب أو تحدث",
            "speak_btn": "🎤 تحدث عن أعراضك",
            "stop_btn": "⏹️ إيقاف التسجيل",
            "recording": "🔴 جاري التسجيل... تحدث الآن",
            "type_placeholder": "مثال: لدي حمى وصداع منذ يومين، ألم في الجسم، أشعر بالضعف...",
            "assess_btn": "تقييم صحتي",
            "assessing": "🔄 تحليل الأعراض...",
            "result_title": "📋 نتيجة التقييم",
            "listen_btn": "🔊 استمع للنتيجة",
            "recommendation": "💡 التوصية",
            "emergency_warning": "⚠️ طوارئ",
            "emergency_text": "هذا يتطلب عناية طبية فورية!",
            "emergency_action": "📞 اتصل بـ 999 الآن أو اذهب لأقرب مستشفى",
            "moderate_warning": "⚠️ عناية طبية مطلوبة",
            "moderate_text": "يجب أن ترى طبيباً قريباً",
            "moderate_action": "📅 احجز موعداً خلال 24-48 ساعة",
            "mild_text": "أعراضك تبدو خفيفة",
            "mild_action": "🏠 استرح في المنزل، راقب الأعراض",
            "when_emergency": "متى تتصل بـ 999",
            "emergency_signs": "• ألم في الصدر\n• صعوبة في التنفس\n• نزيف شديد\n• فقدان الوعي\n• رد فعل تحسسي شديد",
        },
        "বাংলা": {
            "title": "🩺 এআই স্বাস্থ্য মূল্যায়ন",
            "subtitle": "আপনার লক্ষণ বর্ণনা করুন - টাইপ বা বলুন",
            "speak_btn": "🎤 আপনার লক্ষণ বলুন",
            "stop_btn": "⏹️ রেকর্ডিং বন্ধ করুন",
            "recording": "🔴 রেকর্ডিং... এখন বলুন",
            "type_placeholder": "উদাহরণ: আমার ২ দিন ধরে জ্বর এবং মাথাব্যথা আছে, শরীর ব্যথা, দুর্বল লাগছে...",
            "assess_btn": "আমার স্বাস্থ্য মূল্যায়ন করুন",
            "assessing": "🔄 আপনার লক্ষণ বিশ্লেষণ করা হচ্ছে...",
            "result_title": "📋 মূল্যায়ন ফলাফল",
            "listen_btn": "🔊 ফলাফল শুনুন",
            "recommendation": "💡 সুপারিশ",
            "emergency_warning": "⚠️ জরুরী",
            "emergency_text": "এর জন্য তাৎক্ষণিক চিকিৎসা প্রয়োজন!",
            "emergency_action": "📞 এখনই ৯৯৯ এ কল করুন বা নিকটতম হাসপাতালে যান",
            "moderate_warning": "⚠️ চিকিৎসা প্রয়োজন",
            "moderate_text": "আপনার শীঘ্রই একজন ডাক্তার দেখা উচিত",
            "moderate_action": "📅 ২৪-৪৮ ঘন্টার মধ্যে অ্যাপয়েন্টমেন্ট করুন",
            "mild_text": "আপনার লক্ষণগুলি হালকা বলে মনে হয়",
            "mild_action": "🏠 বাড়িতে বিশ্রাম নিন, লক্ষণ পর্যবেক্ষণ করুন",
            "when_emergency": "কখন ৯৯৯ এ কল করবেন",
            "emergency_signs": "• বুকে ব্যথা\n• শ্বাসকষ্ট\n• ভারী রক্তপাত\n• অজ্ঞান\n• গুরুতর অ্যালার্জি প্রতিক্রিয়া",
        }
    }
    
    txt = UI[lang]
    
    # Header
    st.markdown(f"### {txt['title']}")
    st.info(txt['subtitle'])
    
    # Voice Input Section
    if VOICE_ENABLED:
        st.markdown("---")
        
        # Voice recording component
        voice_html = f"""
        <div style="background:linear-gradient(135deg,{T['p']},{T['s']});padding:20px;border-radius:12px;margin:10px 0">
            <button id="voiceBtn" style="
                background:white;color:{T['p']};border:none;border-radius:10px;
                padding:14px 28px;font-size:1.1rem;font-weight:700;cursor:pointer;
                box-shadow:0 4px 12px rgba(0,0,0,0.2);width:100%;
                transition:all 0.2s;">
                <span id="btnText">{txt['speak_btn']}</span>
            </button>
            <div id="transcript" style="
                margin-top:16px;padding:14px;background:rgba(255,255,255,0.95);
                border-radius:8px;min-height:80px;font-size:1rem;
                color:#1f2937;display:none;font-family:Poppins,sans-serif;"></div>
            <div id="status" style="margin-top:10px;color:white;font-size:0.9rem;text-align:center;"></div>
        </div>
        
        <script>
        (function() {{
            const btn = document.getElementById('voiceBtn');
            const btnText = document.getElementById('btnText');
            const transcript = document.getElementById('transcript');
            const status = document.getElementById('status');
            
            let recognition = null;
            let isRecording = false;
            let finalText = '';
            
            if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {{
                status.textContent = '❌ Voice not supported in this browser';
                btn.disabled = true;
                return;
            }}
            
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            recognition = new SpeechRecognition();
            recognition.lang = '{lang_code}';
            recognition.continuous = true;
            recognition.interimResults = true;
            
            recognition.onstart = function() {{
                isRecording = true;
                btn.style.background = '#ef4444';
                btnText.textContent = '{txt['stop_btn']}';
                transcript.style.display = 'block';
                status.textContent = '{txt['recording']}';
            }};
            
            recognition.onresult = function(event) {{
                let interimTranscript = '';
                finalText = '';
                
                for (let i = 0; i < event.results.length; i++) {{
                    const result = event.results[i];
                    if (result.isFinal) {{
                        finalText += result[0].transcript + ' ';
                    }} else {{
                        interimTranscript += result[0].transcript;
                    }}
                }}
                
                transcript.textContent = finalText + interimTranscript;
            }};
            
            recognition.onerror = function(event) {{
                status.textContent = '❌ Error: ' + event.error;
                resetButton();
            }};
            
            recognition.onend = function() {{
                if (finalText.trim()) {{
                    const url = new URL(window.parent.location.href);
                    url.searchParams.set('voice_input', encodeURIComponent(finalText.trim()));
                    window.parent.history.replaceState({{}}, '', url.toString());
                    window.parent.location.reload();
                }}
                resetButton();
            }};
            
            function resetButton() {{
                isRecording = false;
                btn.style.background = 'white';
                btnText.textContent = '{txt['speak_btn']}';
                status.textContent = '';
            }}
            
            btn.onclick = function() {{
                if (isRecording) {{
                    recognition.stop();
                }} else {{
                    transcript.style.display = 'block';
                    transcript.textContent = '';
                    finalText = '';
                    recognition.start();
                }}
            }};
        }})();
        </script>
        """
        
        components.html(voice_html, height=220)
        
        # Get voice input from URL
        voice_input = st.query_params.get('voice_input', '')
        if voice_input:
            st.query_params.clear()
            st.session_state.symptoms_input = voice_input
            st.rerun()
    
    # Text Input (always available)
    st.markdown("---")
    symptoms = st.text_area(
        "",
        value=st.session_state.get('symptoms_input', ''),
        height=120,
        placeholder=txt['type_placeholder'],
        key='symptoms_text'
    )
    
    # Assess Button
    if st.button(f"✓ {txt['assess_btn']}", type="primary", use_container_width=True, key='assess_btn'):
        if symptoms.strip():
            with st.spinner(txt['assessing']):
                result = assess_symptoms(symptoms, lang)
                st.session_state.assessment_result = result
                st.session_state.symptoms_input = symptoms
                st.rerun()
        else:
            st.warning("Please describe symptoms" if lang == "English" 
                      else "الرجاء وصف الأعراض" if lang == "العربية"
                      else "দয়া করে লক্ষণ বর্ণনা করুন")
    
    # Show Result
    if 'assessment_result' in st.session_state and st.session_state.assessment_result:
        result = st.session_state.assessment_result
        
        st.markdown("---")
        st.markdown(f"### {txt['result_title']}")
        
        # Result display based on severity
        if result['level'] == 'RED':
            st.markdown(f"""
            <div style="background:#fee2e2;border:3px solid #dc2626;border-radius:16px;
                 padding:24px;text-align:center;">
                <div style="font-size:3rem">🚨</div>
                <div style="color:#dc2626;font-size:1.5rem;font-weight:800;margin:10px 0">
                    {txt['emergency_warning']}</div>
                <div style="color:#991b1b;font-size:1.1rem;line-height:1.6">
                    {txt['emergency_text']}</div>
                <div style="background:#dc2626;color:white;padding:12px;border-radius:8px;
                     margin-top:16px;font-size:1rem;font-weight:700">
                    {txt['emergency_action']}</div>
            </div>
            """, unsafe_allow_html=True)
            
        elif result['level'] == 'YELLOW':
            st.markdown(f"""
            <div style="background:#fef9c3;border:3px solid #f59e0b;border-radius:16px;
                 padding:24px;text-align:center;">
                <div style="font-size:3rem">⚠️</div>
                <div style="color:#f59e0b;font-size:1.5rem;font-weight:800;margin:10px 0">
                    {txt['moderate_warning']}</div>
                <div style="color:#92400e;font-size:1.1rem;line-height:1.6">
                    {txt['moderate_text']}</div>
                <div style="background:#f59e0b;color:white;padding:12px;border-radius:8px;
                     margin-top:16px;font-size:1rem;font-weight:700">
                    {txt['moderate_action']}</div>
            </div>
            """, unsafe_allow_html=True)
            
        else:  # GREEN
            st.markdown(f"""
            <div style="background:#dcfce7;border:3px solid #16a34a;border-radius:16px;
                 padding:24px;text-align:center;">
                <div style="font-size:3rem">✅</div>
                <div style="color:#16a34a;font-size:1.5rem;font-weight:800;margin:10px 0">
                    {txt['mild_text']}</div>
                <div style="background:#16a34a;color:white;padding:12px;border-radius:8px;
                     margin-top:16px;font-size:1rem;font-weight:700">
                    {txt['mild_action']}</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Recommendation
        st.markdown(f"#### {txt['recommendation']}")
        st.write(result['recommendation'])
        
        # Voice Output
        if VOICE_ENABLED:
            st.markdown("---")
            full_result = f"{result['message']}. {result['recommendation']}"
            
            tts_html = f"""
            <button id="ttsBtn" style="
                background:linear-gradient(135deg,{T['p']},{T['s']});
                color:white;border:none;border-radius:10px;
                padding:14px 28px;font-size:1.1rem;font-weight:700;
                cursor:pointer;box-shadow:0 4px 12px {T['p']}44;
                width:100%;transition:all 0.2s;">
                🔊 <span id="ttsText">{txt['listen_btn']}</span>
            </button>
            <div id="ttsStatus" style="margin-top:10px;text-align:center;
                 font-size:0.9rem;color:#6b7280;"></div>
            
            <script>
            (function() {{
                const btn = document.getElementById('ttsBtn');
                const btnText = document.getElementById('ttsText');
                const status = document.getElementById('ttsStatus');
                
                if (!('speechSynthesis' in window)) {{
                    status.textContent = '❌ Text-to-speech not supported';
                    btn.disabled = true;
                    return;
                }}
                
                const text = `{full_result.replace("'", "\\'").replace('"', '\\"').replace("\n", " ")}`;
                let isSpeaking = false;
                
                function speak() {{
                    if (isSpeaking) {{
                        window.speechSynthesis.cancel();
                        return;
                    }}
                    
                    const utterance = new SpeechSynthesisUtterance(text);
                    utterance.lang = '{tts_code}';
                    utterance.rate = 0.85;
                    utterance.pitch = 1.0;
                    
                    utterance.onstart = function() {{
                        isSpeaking = true;
                        btn.style.background = 'linear-gradient(135deg,#dc2626,#ef4444)';
                        btnText.textContent = '⏹️ ' + ('Stop' if '{lang}' == 'English' 
                                                       else 'إيقاف' if '{lang}' == 'العربية'
                                                       else 'বন্ধ করুন');
                        status.textContent = '🔊 ' + ('Speaking...' if '{lang}' == 'English'
                                                      else 'يتحدث...' if '{lang}' == 'العربية'
                                                      else 'বলছে...');
                    }};
                    
                    utterance.onend = function() {{
                        isSpeaking = false;
                        btn.style.background = 'linear-gradient(135deg,{T['p']},{T['s']})';
                        btnText.textContent = '{txt['listen_btn']}';
                        status.textContent = '';
                    }};
                    
                    utterance.onerror = function(e) {{
                        status.textContent = '❌ Error';
                        isSpeaking = false;
                    }};
                    
                    window.speechSynthesis.speak(utterance);
                }}
                
                btn.onclick = speak;
            }})();
            </script>
            """
            
            components.html(tts_html, height=100)
        
        # Emergency info
        st.markdown("---")
        with st.expander(txt['when_emergency']):
            st.error(txt['emergency_signs'])


def assess_symptoms(symptoms, lang):
    """Assess severity - returns level + message"""
    
    s = symptoms.lower()
    
    # Emergency keywords
    emergency = {
        'en': ['chest pain', 'cant breathe', 'difficulty breathing', 'unconscious', 
               'heavy bleeding', 'severe allergic', 'stroke', 'heart attack'],
        'ar': ['ألم في الصدر', 'صعوبة في التنفس', 'فاقد الوعي', 'نزيف شديد', 
               'حساسية شديدة', 'سكتة', 'نوبة قلبية'],
        'bn': ['বুকে ব্যথা', 'শ্বাস নিতে পারছি না', 'শ্বাসকষ্ট', 'অজ্ঞান',
               'ভারী রক্তপাত', 'গুরুতর এলার্জি', 'স্ট্রোক', 'হার্ট অ্যাটাক']
    }
    
    for words in emergency.values():
        if any(w in s for w in words):
            return {
                'level': 'RED',
                'message': {
                    'English': 'EMERGENCY: Immediate medical attention required!',
                    'العربية': 'طوارئ: عناية طبية فورية مطلوبة!',
                    'বাংলা': 'জরুরী: তাৎক্ষণিক চিকিৎসা প্রয়োজন!'
                }[lang],
                'recommendation': {
                    'English': 'Call 999 immediately or go to the nearest emergency room. Do not wait.',
                    'العربية': 'اتصل بـ 999 فوراً أو اذهب لأقرب غرفة طوارئ. لا تنتظر.',
                    'বাংলা': 'অবিলম্বে ৯৯৯ এ কল করুন বা নিকটতম জরুরী কক্ষে যান। অপেক্ষা করবেন না।'
                }[lang]
            }
    
    # Moderate keywords
    moderate = {
        'en': ['fever', 'vomit', 'severe pain', 'swelling', 'rash', 'dizzy'],
        'ar': ['حمى', 'قيء', 'ألم شديد', 'تورم', 'طفح', 'دوخة'],
        'bn': ['জ্বর', 'বমি', 'তীব্র ব্যথা', 'ফোলা', 'ফুসকুড়ি', 'মাথা ঘোরা']
    }
    
    for words in moderate.values():
        if any(w in s for w in words):
            return {
                'level': 'YELLOW',
                'message': {
                    'English': 'MODERATE: Medical attention recommended',
                    'العربية': 'متوسط: عناية طبية موصى بها',
                    'বাংলা': 'মাঝারি: চিকিৎসা সুপারিশকৃত'
                }[lang],
                'recommendation': {
                    'English': 'See a doctor within 24-48 hours. Rest, drink fluids, monitor symptoms. If worsening, seek care sooner.',
                    'العربية': 'راجع طبيباً خلال 24-48 ساعة. استرح، اشرب السوائل، راقب الأعراض. إذا ساءت، اطلب الرعاية في وقت أقرب.',
                    'বাংলা': '২৪-৪৮ ঘন্টার মধ্যে একজন ডাক্তার দেখান। বিশ্রাম নিন, তরল পান করুন, লক্ষণ পর্যবেক্ষণ করুন। খারাপ হলে তাড়াতাড়ি চিকিৎসা নিন।'
                }[lang]
            }
    
    # Mild
    return {
        'level': 'GREEN',
        'message': {
            'English': 'MILD: Symptoms appear manageable',
            'العربية': 'خفيف: الأعراض تبدو قابلة للإدارة',
            'বাংলা': 'হালকা: লক্ষণগুলি পরিচালনাযোগ্য বলে মনে হয়'
        }[lang],
        'recommendation': {
            'English': 'Rest at home, stay hydrated, monitor symptoms. See a doctor if symptoms persist beyond 3-5 days or worsen.',
            'العربية': 'استرح في المنزل، حافظ على رطوبتك، راقب الأعراض. راجع طبيباً إذا استمرت الأعراض لأكثر من 3-5 أيام أو ساءت.',
            'বাংলা': 'বাড়িতে বিশ্রাম নিন, হাইড্রেটেড থাকুন, লক্ষণ পর্যবেক্ষণ করুন। লক্ষণ ৩-৫ দিনের বেশি থাকলে বা খারাপ হলে ডাক্তার দেখান।'
        }[lang]
    }
