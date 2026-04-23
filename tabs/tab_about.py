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
            <div style="opacity:0.85">Salalah, Dhofar, Oman 🇴🇲</div>
            <div style="margin-top:10px;font-size:0.82rem;opacity:0.75">
                Python · Streamlit · Google Gemini AI</div>
        </div>""", unsafe_allow_html=True)

    with c2:
        st.markdown("""
**Khareef Health** is a free AI medical triage assistant
built for the community of Salalah, Dhofar, Oman.

Instant health advice in **English and Arabic**.
Named after Salalah's unique **Khareef** monsoon season.

**Features:**
- AI triage (GREEN / YELLOW / RED)
- Free text symptom analysis
- Skin photo analysis
- Medicine scanner
- Womens health guide
- Disease encyclopedia
- Community health trends
- Emergency first aid guide
        """)

    st.markdown("---")

    # ── INSTALL AS APP ──────────────────────────────
    st.markdown("### 📲 Add to Your Phone Home Screen")
    st.caption("Use Khareef Health like a real app — no App Store needed!")

    i1, i2 = st.columns(2)

    with i1:
        p = T['p']
        st.markdown(f"""
        <div style="background:#f0fdf4;border-radius:14px;padding:20px;
             border:2px solid {p}33;height:100%;">
            <div style="font-size:2rem;text-align:center">🍎</div>
            <div style="font-weight:700;color:{p};font-size:1.05rem;
                 text-align:center;margin:8px 0">iPhone / iPad</div>
            <div style="font-size:0.88rem;color:#374151;line-height:2;">
                <b>Step 1:</b> Open this app in <b>Safari</b><br>
                <b>Step 2:</b> Tap the Share button ⬆️ at the bottom<br>
                <b>Step 3:</b> Scroll down → tap <b>Add to Home Screen</b><br>
                <b>Step 4:</b> Tap <b>Add</b> — done! ✅
            </div>
            <div style="margin-top:12px;background:#fef9c3;border-radius:8px;
                 padding:8px 12px;font-size:0.8rem;color:#92400e;">
                ⚠️ Must use Safari — does not work in Chrome on iPhone
            </div>
        </div>""", unsafe_allow_html=True)

    with i2:
        st.markdown(f"""
        <div style="background:#eff6ff;border-radius:14px;padding:20px;
             border:2px solid #2563eb33;height:100%;">
            <div style="font-size:2rem;text-align:center">🤖</div>
            <div style="font-weight:700;color:#1e40af;font-size:1.05rem;
                 text-align:center;margin:8px 0">Android Phone</div>
            <div style="font-size:0.88rem;color:#374151;line-height:2;">
                <b>Step 1:</b> Open this app in <b>Chrome</b><br>
                <b>Step 2:</b> Tap the three dots <b>⋮</b> at the top right<br>
                <b>Step 3:</b> Tap <b>Add to Home screen</b><br>
                <b>Step 4:</b> Tap <b>Add</b> — done! ✅
            </div>
            <div style="margin-top:12px;background:#dbeafe;border-radius:8px;
                 padding:8px 12px;font-size:0.8rem;color:#1e40af;">
                ✅ Works best in Chrome browser on Android
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("")

    # App link to copy
    p = T['p']
    st.markdown(f"""
    <div style="background:linear-gradient({T['g']});border-radius:12px;
         padding:16px 20px;color:white;text-align:center;margin-top:8px;">
        <div style="font-size:0.85rem;opacity:0.85;margin-bottom:6px">
            📋 Share this link with anyone:</div>
        <div style="background:rgba(255,255,255,0.2);border-radius:8px;
             padding:10px 16px;font-size:0.9rem;font-weight:600;
             letter-spacing:0.3px;word-break:break-all;">
            khareef-health-6ni9nxypihjhpwsq4nohmw.streamlit.app
        </div>
    </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # Emergency contacts
    c1,c2,c3 = st.columns(3)
    with c1: st.error("Emergency\n📞 999")
    with c2: st.info("Sultan Qaboos\n📞 +968 23 218 000")
    with c3: st.info("Salalah Private\n📞 +968 23 295 999")

    st.markdown("---")
    st.markdown("""<div class="disclaimer">
        For educational purposes only. NOT a substitute for professional medical advice.
        Always consult a licensed doctor. Emergency: <b>999</b></div>""",
        unsafe_allow_html=True)
