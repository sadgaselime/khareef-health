import streamlit as st

def render(T):
    c1,c2 = st.columns(2)
    with c1:
        g = T['g']
        st.markdown(f"""
        <div class="profile-card">
            <div style="font-size:3rem">👨‍💻</div>
            <div style="font-size:1.3rem;font-weight:700;margin:8px 0">Sadga Selime</div>
            <div style="opacity:0.85">Developer and Designer</div>
            <div style="opacity:0.85">Salalah, Dhofar, Oman</div>
            <div style="margin-top:10px;font-size:0.82rem;opacity:0.75">
                Python · Streamlit · Google Gemini AI</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("""
**Khareef Health** is a free AI medical triage assistant built for the community of Salalah, Dhofar, Oman.

Instant health advice in English and Arabic.
Named after Salalah unique Khareef monsoon season.

**Features:**
- AI triage (GREEN / YELLOW / RED)
- Free text symptom analysis
- Skin photo analysis
- Medicine scanner
- Women health guide
- Disease encyclopedia
- Community health trends
- Emergency first aid guide
        """)
    st.markdown("---")
    c1,c2,c3 = st.columns(3)
    with c1: st.error("Emergency\n999")
    with c2: st.info("Sultan Qaboos\n+968 23 218 000")
    with c3: st.info("Salalah Private\n+968 23 295 999")
    st.markdown("---")
    st.markdown('<div class="disclaimer">For educational purposes only. NOT a substitute for professional medical advice. Always consult a licensed doctor. Emergency: 999</div>', unsafe_allow_html=True)
