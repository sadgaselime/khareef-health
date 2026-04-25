import streamlit as st
import streamlit.components.v1 as components

def voice_input_component(lang_code="en-US", key="voice_input"):
    """
    Voice input component using Web Speech API.
    Returns recognized text via session state.
    """
    
    html_code = f"""
    <div style="font-family:Poppins,sans-serif">
        <button id="voiceBtn" style="
            background:linear-gradient(135deg,#059669,#10b981);
            color:white;border:none;border-radius:10px;
            padding:12px 24px;font-size:1rem;font-weight:600;
            cursor:pointer;box-shadow:0 4px 12px rgba(5,150,105,0.3);
            transition:all 0.2s;">
            🎤 <span id="btnText">Start Speaking</span>
        </button>
        <div id="transcript" style="
            margin-top:12px;padding:12px;background:#f0fdf4;
            border-radius:8px;min-height:60px;font-size:0.9rem;
            color:#166534;display:none;"></div>
        <div id="status" style="margin-top:8px;font-size:0.85rem;color:#6b7280;"></div>
    </div>
    
    <script>
    (function() {{
        const btn = document.getElementById('voiceBtn');
        const btnText = document.getElementById('btnText');
        const transcript = document.getElementById('transcript');
        const status = document.getElementById('status');
        
        let recognition = null;
        let isRecording = false;
        
        // Check browser support
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {{
            status.textContent = '❌ Voice input not supported in this browser';
            status.style.color = '#dc2626';
            btn.disabled = true;
            return;
        }}
        
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();
        recognition.lang = '{lang_code}';
        recognition.continuous = false;
        recognition.interimResults = true;
        
        recognition.onstart = function() {{
            isRecording = true;
            btn.style.background = 'linear-gradient(135deg,#dc2626,#ef4444)';
            btnText.textContent = 'Recording... (Click to stop)';
            transcript.style.display = 'block';
            transcript.textContent = 'Listening...';
            status.textContent = '🎙️ Speak now';
            status.style.color = '#059669';
        }};
        
        recognition.onresult = function(event) {{
            let interimTranscript = '';
            let finalTranscript = '';
            
            for (let i = event.resultIndex; i < event.results.length; i++) {{
                const result = event.results[i];
                if (result.isFinal) {{
                    finalTranscript += result[0].transcript;
                }} else {{
                    interimTranscript += result[0].transcript;
                }}
            }}
            
            transcript.textContent = finalTranscript || interimTranscript;
            
            if (finalTranscript) {{
                // Send to Streamlit
                window.parent.postMessage({{
                    type: 'voice_input',
                    key: '{key}',
                    text: finalTranscript
                }}, '*');
            }}
        }};
        
        recognition.onerror = function(event) {{
            status.textContent = '❌ Error: ' + event.error;
            status.style.color = '#dc2626';
            resetButton();
        }};
        
        recognition.onend = function() {{
            resetButton();
            status.textContent = '✓ Done';
        }};
        
        function resetButton() {{
            isRecording = false;
            btn.style.background = 'linear-gradient(135deg,#059669,#10b981)';
            btnText.textContent = 'Start Speaking';
        }}
        
        btn.onclick = function() {{
            if (isRecording) {{
                recognition.stop();
            }} else {{
                transcript.style.display = 'block';
                recognition.start();
            }}
        }};
    }})();
    </script>
    """
    
    components.html(html_code, height=180)


def text_to_speech_component(text, lang_code="en-US", auto_play=False):
    """
    Text-to-speech component using Web Speech API.
    Reads text aloud in specified language.
    """
    
    # Escape text for JavaScript
    safe_text = text.replace("'", "\\'").replace('"', '\\"').replace("\n", " ")
    auto = "true" if auto_play else "false"
    
    html_code = f"""
    <div style="font-family:Poppins,sans-serif">
        <button id="ttsBtn" style="
            background:linear-gradient(135deg,#2563eb,#3b82f6);
            color:white;border:none;border-radius:10px;
            padding:10px 20px;font-size:0.95rem;font-weight:600;
            cursor:pointer;box-shadow:0 4px 12px rgba(37,99,235,0.3);
            transition:all 0.2s;">
            🔊 <span id="ttsText">Read Aloud</span>
        </button>
        <div id="ttsStatus" style="margin-top:8px;font-size:0.85rem;color:#6b7280;"></div>
    </div>
    
    <script>
    (function() {{
        const btn = document.getElementById('ttsBtn');
        const btnText = document.getElementById('ttsText');
        const status = document.getElementById('ttsStatus');
        
        // Check browser support
        if (!('speechSynthesis' in window)) {{
            status.textContent = '❌ Text-to-speech not supported';
            status.style.color = '#dc2626';
            btn.disabled = true;
            return;
        }}
        
        const text = `{safe_text}`;
        const langCode = '{lang_code}';
        let isSpeaking = false;
        
        function speak() {{
            if (isSpeaking) {{
                window.speechSynthesis.cancel();
                return;
            }}
            
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = langCode;
            utterance.rate = 0.9;
            utterance.pitch = 1.0;
            
            utterance.onstart = function() {{
                isSpeaking = true;
                btn.style.background = 'linear-gradient(135deg,#dc2626,#ef4444)';
                btnText.textContent = 'Stop Reading';
                status.textContent = '🔊 Speaking...';
                status.style.color = '#2563eb';
            }};
            
            utterance.onend = function() {{
                isSpeaking = false;
                btn.style.background = 'linear-gradient(135deg,#2563eb,#3b82f6)';
                btnText.textContent = 'Read Aloud';
                status.textContent = '';
            }};
            
            utterance.onerror = function(event) {{
                status.textContent = '❌ Error: ' + event.error;
                status.style.color = '#dc2626';
                isSpeaking = false;
            }};
            
            window.speechSynthesis.speak(utterance);
        }}
        
        btn.onclick = speak;
        
        // Auto-play if enabled
        if ({auto}) {{
            setTimeout(speak, 500);
        }}
    }})();
    </script>
    """
    
    components.html(html_code, height=80)


def get_voice_input_value(key="voice_input"):
    """
    Retrieve voice input from JavaScript postMessage.
    Store in session state.
    """
    
    # JavaScript listener (runs once per session)
    if f"voice_listener_{key}" not in st.session_state:
        components.html(f"""
        <script>
        window.addEventListener('message', function(event) {{
            if (event.data.type === 'voice_input' && event.data.key === '{key}') {{
                // Store in URL params (Streamlit can read this)
                const url = new URL(window.parent.location.href);
                url.searchParams.set('voice_{key}', event.data.text);
                window.parent.history.replaceState({{}}, '', url.toString());
                
                // Trigger rerun
                window.parent.location.reload();
            }}
        }});
        </script>
        """, height=0)
        st.session_state[f"voice_listener_{key}"] = True
    
    # Read from URL params
    voice_text = st.query_params.get(f"voice_{key}", "")
    if voice_text:
        st.query_params.pop(f"voice_{key}")  # Clear after reading
        return voice_text
    
    return st.session_state.get(f"voice_text_{key}", "")
