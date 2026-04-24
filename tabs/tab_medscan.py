import streamlit as st

def section_header(icon, title, subtitle="", color="#1a5c45"):
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:14px;background:white;
         border-radius:14px;padding:16px 20px;margin-bottom:16px;
         box-shadow:0 2px 10px rgba(0,0,0,0.06);border-left:5px solid {color};">
        <div style="font-size:2.4rem">{icon}</div>
        <div>
            <div style="font-size:1.1rem;font-weight:700;color:{color}">{title}</div>
            <div style="font-size:0.82rem;color:#6b7280">{subtitle}</div>
        </div>
        <div style="margin-left:auto;opacity:0.07;font-size:3rem;color:{color}">+</div>
    </div>""", unsafe_allow_html=True)

def render(T, GEMINI_API_KEY, is_api_key_configured):
    section_header("💊📷","Medicine Scanner","Scan any medicine packet, label or prescription","#0369a1")
    st.markdown('<div class="disclaimer">Educational only. Always follow your doctors prescription.</div>',unsafe_allow_html=True)
    st.markdown("")
    mode = st.radio("Scan type:",["Scan medicine packet/label","Scan prescription/doctors note","Ask a question about this medicine"],key="ms_mode")
    method = st.radio("Image source:",["Take photo","Upload image"],horizontal=True,key="ms_m")
    img=None
    if "Take" in method:
        cam=st.camera_input("Point at medicine",key="ms_cam")
        if cam: img=cam
    else:
        up=st.file_uploader("Upload image",type=["jpg","jpeg","png","webp"],key="ms_up")
        if up: img=up
    question=st.text_input("Ask a specific question (optional):",placeholder="e.g. Can I take this with metformin?",key="ms_q")
    if img:
        st.image(img,width=350)
        if st.button("Analyze Medicine",type="primary",use_container_width=True,key="ms_btn"):
            if not is_api_key_configured():
                st.error("Gemini API key required.")
            else:
                with st.spinner("Reading medicine..."):
                    try:
                        from google import genai
                        import PIL.Image,io
                        client=genai.Client(api_key=GEMINI_API_KEY)
                        pil=PIL.Image.open(io.BytesIO(img.getvalue()))
                        if "packet" in mode:
                            prompt=f"""Helpful pharmacist AI. Look at this medicine and provide:
MEDICINE NAME: [name and generic name]
WHAT IT IS FOR: [condition it treats]
DOSAGE: [dose shown on label]
WARNINGS: [any warnings]
STORAGE: [how to store]
EXPIRY: [expiry date if visible]
{f"ANSWER: {question}" if question else ""}
End: Consult your pharmacist or doctor."""
                        elif "prescription" in mode:
                            prompt=f"""Medical assistant AI. Look at this prescription:
MEDICINES PRESCRIBED: [list each]
WHAT EACH IS FOR: [purpose]
DOSAGE: [how and when]
NOTES: [special instructions]
{f"ANSWER: {question}" if question else ""}
Confirm with prescribing doctor."""
                        else:
                            prompt=f"""Pharmacist AI. Patient question: {question or "What is this medicine?"}
Clear simple answer based on what you see. Include safety information.
End: Confirm with your pharmacist or doctor."""
                        resp=client.models.generate_content(model="gemini-2.5-flash",contents=[prompt,pil])
                        st.markdown("### Medicine Analysis")
                        st.info(resp.text.strip())
                        st.warning("Educational only. Always follow your doctors instructions.")
                    except Exception as e:
                        st.error(f"Scan failed: {e}")
    else:
        p=T['p'];l=T['l']
        st.markdown(f'<div style="background:{l};border:2px dashed {p}44;border-radius:14px;padding:28px;text-align:center;"><div style="font-size:3.5rem">💊</div><div style="font-weight:700;color:{p};margin:8px 0">Take or upload a medicine photo</div><div style="color:#6b7280;font-size:0.85rem">Packets, labels, prescriptions, tablets</div></div>',unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### Tips for Best Results")
    c1,c2,c3=st.columns(3)
    with c1: st.markdown('<div class="step">Good lighting — avoid shadows on the label</div>',unsafe_allow_html=True)
    with c2: st.markdown('<div class="step">Focus on text — medicine name must be visible</div>',unsafe_allow_html=True)
    with c3: st.markdown('<div class="step">Flat surface — photograph straight down</div>',unsafe_allow_html=True)
