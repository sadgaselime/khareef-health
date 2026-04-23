import streamlit as st

def render(T, GEMINI_API_KEY, is_api_key_configured):
    st.markdown("### Medicine Scanner")
    st.markdown('<div class="disclaimer">Educational purposes only. Always follow your doctors prescription.</div>', unsafe_allow_html=True)
    st.markdown("")

    mode = st.radio("Scan type:", [
        "Scan medicine packet/label",
        "Scan prescription/doctors note",
        "Ask a question about medicine photo",
    ], key="ms_mode")

    method = st.radio("Image source:", ["Take photo","Upload image"], horizontal=True, key="ms_m")
    img = None
    if method == "Take photo":
        cam = st.camera_input("Point at medicine", key="ms_cam")
        if cam: img = cam
    else:
        up = st.file_uploader("Upload image", type=["jpg","jpeg","png","webp"], key="ms_up")
        if up: img = up

    question = st.text_input("Ask a specific question (optional):",
        placeholder="e.g. Can I take this with metformin? Safe in pregnancy?", key="ms_q")

    if img:
        st.image(img, width=350)
        if st.button("Analyze Medicine", type="primary", use_container_width=True, key="ms_btn"):
            if not is_api_key_configured():
                st.error("Gemini API key required.")
            else:
                with st.spinner("Reading medicine..."):
                    try:
                        from google import genai
                        import PIL.Image, io
                        client = genai.Client(api_key=GEMINI_API_KEY)
                        pil    = PIL.Image.open(io.BytesIO(img.getvalue()))

                        if "packet" in mode:
                            prompt = f"""You are a helpful pharmacist AI assistant.
Look at this medicine packaging or label and provide:
MEDICINE NAME: [name + generic name]
WHAT IT IS FOR: [condition it treats]
ACTIVE INGREDIENT: [main drug]
DOSAGE: [dose information]
HOW TO TAKE IT: [instructions]
WARNINGS: [warnings, allergies, side effects]
STORAGE: [how to store]
EXPIRY: [expiry date if visible]
{f"ANSWER THIS: {question}" if question else ""}
End with: Consult your pharmacist or doctor before taking any medication."""
                        elif "prescription" in mode:
                            prompt = f"""You are a helpful medical assistant.
Look at this prescription and provide:
MEDICINES PRESCRIBED: [list each]
WHAT EACH IS FOR: [purpose]
DOSAGE INSTRUCTIONS: [how and when]
IMPORTANT NOTES: [special instructions]
{f"ANSWER THIS: {question}" if question else ""}
Confirm with the prescribing doctor."""
                        else:
                            prompt = f"""You are a knowledgeable pharmacist AI.
Patient question: {question or "What is this medicine and what is it used for?"}
Provide a clear, simple answer based on what you can see.
Include safety information. End with: Please confirm with your pharmacist or doctor."""

                        resp = client.models.generate_content(model="gemini-2.5-flash", contents=[prompt, pil])
                        st.markdown("### Medicine Analysis")
                        st.info(resp.text.strip())
                        st.warning("AI-generated educational information. Always follow your doctors instructions.")
                    except Exception as e:
                        st.error(f"Scan failed: {e}")
    else:
        st.info("Take or upload a photo of any medicine packet, label, or prescription")

    st.markdown("---")
    st.markdown("### Tips for Best Results")
    c1,c2,c3 = st.columns(3)
    with c1: st.markdown('<div class="step">Good lighting — avoid shadows on the label</div>', unsafe_allow_html=True)
    with c2: st.markdown('<div class="step">Focus on text — medicine name and dose must be visible</div>', unsafe_allow_html=True)
    with c3: st.markdown('<div class="step">Flat surface — photograph straight down</div>', unsafe_allow_html=True)
