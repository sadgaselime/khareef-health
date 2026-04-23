import streamlit as st
import pandas as pd
from datetime import datetime

def render(T, g_emoji, save_profile, load_json, PROFILES_FILE):
    st.markdown("### Your Profile / ملفك الشخصي")
    st.caption("Save your info once — used automatically in every health check")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Personal Information")
        p_name  = st.text_input("Full Name / الاسم", value=st.session_state.user_name, key="pn")
        p_age   = st.number_input("Age / العمر", 0, 120, st.session_state.user_age, key="pa")
        p_gender= st.selectbox("Gender / الجنس", ["Not specified","Male","Female"],
            index=["Not specified","Male","Female"].index(st.session_state.gender), key="pg")
        p_phone = st.text_input("Phone / الهاتف", value=st.session_state.user_phone,
            placeholder="+968 9X XXX XXXX", key="pp")
        p_city  = st.selectbox("City / المدينة",
            ["Salalah","Taqah","Mirbat","Rakhyut","Muscat","Sohar","Other"], key="pc")
        st.markdown("#### Medical Information")
        p_blood = st.selectbox("Blood Type / فصيلة الدم",
            ["Unknown","A+","A-","B+","B-","O+","O-","AB+","AB-"], key="pb")
        p_conds = st.multiselect("Existing Conditions / أمراض",
            ["Diabetes","High Blood Pressure","Asthma","Heart Disease",
             "Kidney Disease","Arthritis","Thyroid","None"],
            default=st.session_state.user_conditions, key="pco")
        p_meds  = st.text_area("Daily Medications / أدوية",
            value=st.session_state.user_medications, height=70, key="pm")
        p_allergy  = st.text_input("Allergies / الحساسية", placeholder="e.g. Penicillin", key="pal")
        p_emerg    = st.text_input("Emergency Contact / طوارئ", placeholder="Name + Phone", key="pem")

        if st.button("Save Profile / حفظ الملف", type="primary", use_container_width=True, key="psave"):
            st.session_state.user_name        = p_name
            st.session_state.user_age         = int(p_age)
            st.session_state.gender           = p_gender
            st.session_state.user_phone       = p_phone
            st.session_state.user_city        = p_city
            st.session_state.user_blood_type  = p_blood
            st.session_state.user_conditions  = p_conds
            st.session_state.user_medications = p_meds
            save_profile({
                "saved_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "name":p_name,"age":int(p_age),"gender":p_gender,
                "phone":p_phone,"city":p_city,"blood_type":p_blood,
                "conditions":p_conds,"medications":p_meds,
                "allergies":p_allergy,"emergency_contact":p_emerg,
            })
            st.success("Profile saved!")
            st.rerun()

    with col2:
        st.markdown("#### Your Profile Card")
        if st.session_state.user_name:
            av = st.session_state.user_age
            cats = {0:"👶",2:"🧒",13:"🧑",18:"👨",60:"👴"}
            cat  = next((v for k,v in sorted(cats.items(),reverse=True) if av>=k), "👤")
            conds = ", ".join(st.session_state.user_conditions) or "None"
            g = T['g']
            st.markdown(f"""
            <div class="profile-card">
                <div style="font-size:3rem">{g_emoji}</div>
                <div style="font-size:1.3rem;font-weight:700;margin:8px 0">{st.session_state.user_name}</div>
                <div>Age: {av} {cat}</div>
                <div>{st.session_state.gender} · {st.session_state.user_city}</div>
                <div>Blood: {st.session_state.user_blood_type}</div>
                <div style="margin-top:10px;background:rgba(255,255,255,0.2);border-radius:8px;padding:8px;font-size:0.82rem">
                    Conditions: {conds}</div>
                <div style="margin-top:6px;font-size:0.75rem;opacity:0.75">
                    🔒 Private — only visible to you</div>
            </div>""", unsafe_allow_html=True)
        else:
            st.info("Fill in your profile and click Save")

        st.markdown("""
        <div style="background:#f0fdf4;border-radius:10px;padding:12px;
             font-size:0.85rem;color:#16a34a;border:1px solid #bbf7d0;margin-top:8px;">
            🔒 Your profile is private. Other users cannot see it.
        </div>""", unsafe_allow_html=True)
