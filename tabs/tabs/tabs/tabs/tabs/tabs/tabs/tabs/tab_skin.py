import streamlit as st

def render(T, GEMINI_API_KEY, is_api_key_configured):
    st.markdown("### AI Skin Analysis")
    st.markdown('<div class="disclaimer">Educational purposes only. NOT a dermatological diagnosis. Always consult a doctor.</div>', unsafe_allow_html=True)
    st.markdown("")

    method = st.radio("Image source:", ["Take photo","Upload image"], horizontal=True, key="sk_m")
    img = None
    if method == "Take photo":
        cam = st.camera_input("Point at skin area", key="sk_cam")
        if cam: img = cam
    else:
        up = st.file_uploader("Upload photo", type=["jpg","jpeg","png","webp"], key="sk_up")
        if up: img = up

    if img:
        st.image(img, width=350)
        if st.button("Analyze with AI", type="primary", use_container_width=True, key="sk_btn"):
            if not is_api_key_configured():
                st.error("Gemini API key required.")
            else:
                with st.spinner("AI analyzing image..."):
                    try:
                        from google import genai
                        import PIL.Image, io
                        client = genai.Client(api_key=GEMINI_API_KEY)
                        pil    = PIL.Image.open(io.BytesIO(img.getvalue()))
                        prompt = """You are a helpful AI providing general educational information about visible skin conditions.
Look at this image and provide:
1. WHAT YOU SEE: Visual description
2. POSSIBLE CONDITIONS: 2-3 common conditions that may look similar (educational only)
3. CHARACTERISTICS: Notable features
4. WHEN TO SEE A DOCTOR: Warning signs
5. GENERAL CARE: Basic skincare advice
Always end with: Please consult a qualified dermatologist or doctor for proper diagnosis."""
                        resp = client.models.generate_content(model="gemini-2.5-flash", contents=[prompt, pil])
                        st.markdown("### AI Analysis")
                        st.info(resp.text.strip())
                        st.warning("AI-generated educational information only. NOT a medical diagnosis. Consult a doctor.")
                    except Exception as e:
                        st.error(f"Analysis failed: {e}")
    else:
        st.info("Take or upload a photo to begin skin analysis")

    st.markdown("---")
    st.markdown("### Common Skin Conditions in Salalah")
    c1,c2,c3 = st.columns(3)
    with c1:
        st.markdown('<div class="step"><b>Heat Rash</b><br>Small red bumps from blocked sweat glands. Common in Khareef humidity.<br><i>Treatment: Cool shower, loose clothing</i></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="step"><b>Insect Bites</b><br>Red, itchy bumps. Watch for spreading redness.<br><i>Treatment: Antihistamine cream</i></div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="step-red"><b>See Doctor Urgently:</b><br>Rash spreading rapidly, fever with rash, difficulty breathing, rash after medication</div>', unsafe_allow_html=True)
