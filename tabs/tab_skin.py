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
    section_header("📸","AI Skin Analysis","Photo analysis for educational purposes","#0891b2")
    st.markdown('<div class="disclaimer">Educational only. NOT a diagnosis. Always consult a doctor.</div>',unsafe_allow_html=True)
    st.markdown("")
    method = st.radio("Image source:",["Take photo","Upload image"],horizontal=True,key="sk_m")
    img = None
    if "Take" in method:
        cam = st.camera_input("Point at skin area",key="sk_cam")
        if cam: img=cam
    else:
        up = st.file_uploader("Upload photo",type=["jpg","jpeg","png","webp"],key="sk_up")
        if up: img=up
    if img:
        st.image(img,width=350)
        if st.button("Analyze with AI",type="primary",use_container_width=True,key="sk_btn"):
            if not is_api_key_configured():
                st.error("Gemini API key required.")
            else:
                with st.spinner("AI analyzing..."):
                    try:
                        from google import genai
                        import PIL.Image,io
                        client=genai.Client(api_key=GEMINI_API_KEY)
                        pil=PIL.Image.open(io.BytesIO(img.getvalue()))
                        prompt="""Helpful AI for general educational skin information. Provide:
1. WHAT YOU SEE: Visual description
2. POSSIBLE CONDITIONS: 2-3 similar conditions (educational)
3. WARNING SIGNS: Anything needing urgent care
4. GENERAL CARE: Basic advice
End with: Consult a dermatologist for proper diagnosis."""
                        resp=client.models.generate_content(model="gemini-2.5-flash",contents=[prompt,pil])
                        st.markdown("### AI Analysis")
                        st.info(resp.text.strip())
                        st.warning("Educational only. NOT a diagnosis. Consult a doctor.")
                    except Exception as e:
                        st.error(f"Failed: {e}")
    else:
        p=T['p'];l=T['l']
        st.markdown(f'<div style="background:{l};border:2px dashed {p}44;border-radius:14px;padding:28px;text-align:center;"><div style="font-size:3.5rem">📸</div><div style="font-weight:700;color:{p};margin:8px 0">Take or upload a photo to begin</div><div style="color:#6b7280;font-size:0.85rem">Rashes, spots, skin changes, wound healing</div></div>',unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### Common Skin Conditions in Salalah")
    c1,c2,c3=st.columns(3)
    with c1:
        st.markdown('<div class="step"><b>Heat Rash</b><br>Common in Khareef humidity. Cool shower, loose clothing.</div>',unsafe_allow_html=True)
        st.markdown('<div class="step"><b>Sunburn</b><br>Aloe vera, cool compress, hydrate.</div>',unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="step"><b>Insect Bites</b><br>Antihistamine cream, avoid scratching.</div>',unsafe_allow_html=True)
        st.markdown('<div class="step"><b>Eczema</b><br>Moisturiser daily, steroid cream if prescribed.</div>',unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="step"><b>Fungal Infection</b><br>Common in humidity. Antifungal cream, keep dry.</div>',unsafe_allow_html=True)
        st.markdown('<div class="step-red"><b>See Doctor If:</b><br>Rash spreading fast, fever with rash, rash after medication.</div>',unsafe_allow_html=True)
