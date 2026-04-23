# tabs/tab_medicine.py
import streamlit as st

MEDICINES = {
    "Paracetamol (Panadol)":{"for":"Fever, headache, mild pain","dose":"500-1000mg every 4-6 hrs. Max 4g/day.","warn":"Do not exceed 4g/day. Avoid alcohol.","avoid":"Liver disease","tip":"Safest painkiller for all ages"},
    "Ibuprofen (Brufen)":{"for":"Pain, inflammation, fever","dose":"200-400mg every 6-8 hrs WITH food.","warn":"Take with food. Can cause stomach bleeding.","avoid":"Kidney problems, ulcers, pregnancy","tip":"Always eat before taking"},
    "Metformin":{"for":"Type 2 diabetes","dose":"500-1000mg twice daily with meals.","warn":"Take with food. Stay hydrated.","avoid":"Kidney disease","tip":"Never stop without doctor advice"},
    "Amlodipine":{"for":"High blood pressure","dose":"5-10mg once daily.","warn":"May cause ankle swelling.","avoid":"Severe low BP","tip":"Take at same time each day"},
    "Omeprazole":{"for":"Heartburn, stomach acid","dose":"20mg once daily 30 min before eating.","warn":"Long-term use may reduce magnesium.","avoid":"Long-term without review","tip":"Take before breakfast"},
    "Salbutamol (Ventolin)":{"for":"Asthma, wheezing","dose":"1-2 puffs when needed. Max 4x/day.","warn":"See doctor if using more than 3x/week.","avoid":"Heart rhythm problems","tip":"Always carry in Khareef season"},
    "Aspirin 75mg":{"for":"Prevents heart attack/stroke","dose":"75mg once daily with food.","warn":"Can cause stomach bleeding.","avoid":"Under 16, stomach ulcers","tip":"Do not stop without doctor"},
    "Atorvastatin":{"for":"High cholesterol","dose":"10-80mg once daily at night.","warn":"Report muscle pain immediately.","avoid":"Liver disease, pregnancy","tip":"Take at night"},
}

def render(T):
    st.markdown("### Medicine Information Guide")
    st.markdown('<div class="disclaimer">General info only. Always follow your doctors prescription.</div>', unsafe_allow_html=True)
    st.markdown("")
    sel = st.selectbox("Select a medicine:", list(MEDICINES.keys()), key="msel")
    if sel:
        m = MEDICINES[sel]
        st.info(f"Tip: {m['tip']}")
        c1,c2 = st.columns(2)
        with c1:
            st.success(f"Used for: {m['for']}")
            st.info(f"Dose: {m['dose']}")
        with c2:
            st.warning(f"Warning: {m['warn']}")
            st.error(f"Avoid if: {m['avoid']}")
    st.markdown('<div class="disclaimer">Always consult a doctor or pharmacist before taking any medication.</div>', unsafe_allow_html=True)
