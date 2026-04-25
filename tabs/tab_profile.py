from streamlit_local_storage import LocalStorage
localS = LocalStorage()
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import json
from datetime import datetime

def render(T, g_emoji, save_profile, load_json, PROFILES_FILE):
    st.markdown("### Your Profile / ملفك الشخصي")
    st.caption("Your profile is saved on YOUR device — it will be here every time you return")
# 🔹 Load profile from browser storage into session_state
saved = localS.getItem("khareef_profile")

if saved:
    st.session_state.user_name        = saved.get("name", "")
    st.session_state.user_age         = saved.get("age", 0)
    st.session_state.gender           = saved.get("gender", "Not specified")
    st.session_state.user_phone       = saved.get("phone", "")
    st.session_state.user_city        = saved.get("city", "Salalah")
    st.session_state.user_blood_type  = saved.get("blood_type", "Unknown")
    st.session_state.user_conditions  = saved.get("conditions", [])
    st.session_state.user_medications = saved.get("medications", "")
    # ── LOAD FROM BROWSER STORAGE ──────────────────
    # This JavaScript reads saved profile from browser localStorage
    # and passes it back to Streamlit via a hidden input
    components.html("""
    <script>
    // Load saved profile from localStorage
    function loadProfile() {
        var saved = localStorage.getItem('khareef_profile');
        if (saved) {
            var profile = JSON.parse(saved);
            // Send to Streamlit via URL params
            var params = new URLSearchParams(window.parent.location.search);
            window.parent.postMessage({
                type: 'khareef_profile',
                data: profile
            }, '*');
        }
    }

    // Save profile to localStorage
    function saveProfile(data) {
        localStorage.setItem('khareef_profile', JSON.stringify(data));
        document.getElementById('saveStatus').textContent = 'Saved to your device!';
        document.getElementById('saveStatus').style.color = '#16a34a';
        setTimeout(function() {
            document.getElementById('saveStatus').textContent = '';
        }, 3000);
    }

    // Check if profile exists
    window.onload = function() {
        var saved = localStorage.getItem('khareef_profile');
        if (saved) {
            var p = JSON.parse(saved);
            document.getElementById('profileStatus').innerHTML =
                '<span style="color:#16a34a">&#10003; Profile found: ' + p.name + '</span>';
        } else {
            document.getElementById('profileStatus').innerHTML =
                '<span style="color:#d97706">No saved profile found on this device</span>';
        }
    };
    </script>
    <div id="profileStatus" style="font-family:Poppins,sans-serif;font-size:0.85rem;
         padding:8px 0;"></div>
    <div id="saveStatus" style="font-family:Poppins,sans-serif;font-size:0.85rem;"></div>
    """, height=50)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Personal Information")
        p_name  = st.text_input("Full Name / الاسم",
            value=st.session_state.user_name, key="pn")
        p_age   = st.number_input("Age / العمر", 0, 120,
            value=st.session_state.user_age, key="pa")
        p_gender= st.selectbox("Gender / الجنس",
            ["Not specified","Male","Female"],
            index=["Not specified","Male","Female"].index(
                st.session_state.gender), key="pg")
        p_phone = st.text_input("Phone / الهاتف",
            value=st.session_state.user_phone,
            placeholder="+968 9X XXX XXXX", key="pp")
        p_city  = st.selectbox("City / المدينة",
            ["Salalah","Taqah","Mirbat","Rakhyut","Muscat","Sohar","Other"],
            key="pc")

        st.markdown("#### Medical Information")
        p_blood = st.selectbox("Blood Type / فصيلة الدم",
            ["Unknown","A+","A-","B+","B-","O+","O-","AB+","AB-"], key="pb")
        p_conds = st.multiselect("Existing Conditions / أمراض",
            ["Diabetes","High Blood Pressure","Asthma","Heart Disease",
             "Kidney Disease","Arthritis","Thyroid","None"],
            default=st.session_state.user_conditions, key="pco")
        p_meds  = st.text_area("Daily Medications / أدوية",
            value=st.session_state.user_medications,
            height=70, key="pm")
        p_allergy  = st.text_input("Allergies / الحساسية",
            placeholder="e.g. Penicillin", key="pal")
        p_emerg    = st.text_input("Emergency Contact / طوارئ",
            placeholder="Name + Phone", key="pem")

        if st.button("💾 Save Profile", type="primary",
                use_container_width=True, key="psave"):
            # Save to session state
            st.session_state.user_name        = p_name
            st.session_state.user_age         = int(p_age)
            st.session_state.gender           = p_gender
            st.session_state.user_phone       = p_phone
            st.session_state.user_city        = p_city
            st.session_state.user_blood_type  = p_blood
            st.session_state.user_conditions  = p_conds
            st.session_state.user_medications = p_meds

            profile = {
                "saved_at":        datetime.now().strftime("%Y-%m-%d %H:%M"),
                "name":            p_name,
                "age":             int(p_age),
                "gender":          p_gender,
                "phone":           p_phone,
                "city":            p_city,
                "blood_type":      p_blood,
                "conditions":      p_conds,
                "medications":     p_meds,
                "allergies":       p_allergy,
                "emergency_contact": p_emerg,
            }

            # Save to server file (for admin records)
            save_profile(profile)

            # Save to browser localStorage (persists for user)
            localS.setItem("khareef_profile", profile)
            <script>
            localStorage.setItem('khareef_profile', '{profile_json}');
            document.getElementById('localStatus').innerHTML =
                '<span style="color:#16a34a;font-weight:600">&#10003; Profile saved to your device permanently!</span>';
            setTimeout(function() {{
                document.getElementById('localStatus').innerHTML = '';
            }}, 4000);
            </script>
            <div id="localStatus" style="font-family:Poppins,sans-serif;font-size:0.9rem;
                 padding:8px 0;"></div>
            """, height=40)

            st.success("Profile saved! It will be here next time you visit.")
            st.rerun()

        # ── LOAD FROM DEVICE button ──────────────────
        st.markdown("---")
        st.markdown("#### Already saved on this device?")
        if st.button("Load My Saved Profile", use_container_width=True, key="load_btn"):
            components.html("""
            <script>
            var saved = localStorage.getItem('khareef_profile');
            if (saved) {
                var p = JSON.parse(saved);
                document.getElementById('loadedData').innerHTML =
                    '<div style="background:#f0fdf4;border-radius:8px;padding:12px;' +
                    'font-family:Poppins,sans-serif;font-size:0.85rem;color:#374151;">' +
                    '<b style="color:#16a34a">Profile found on your device:</b><br><br>' +
                    'Name: ' + p.name + '<br>' +
                    'Age: ' + p.age + '<br>' +
                    'City: ' + p.city + '<br>' +
                    'Phone: ' + p.phone + '<br>' +
                    'Blood Type: ' + p.blood_type + '<br><br>' +
                    '<span style="color:#6b7280;font-size:0.8rem">Fill in the form above with this info and click Save Profile</span>' +
                    '</div>';
            } else {
                document.getElementById('loadedData').innerHTML =
                    '<div style="color:#d97706;font-family:Poppins,sans-serif;font-size:0.85rem;">' +
                    'No profile saved on this device yet. Fill in the form above and click Save Profile.</div>';
            }
            </script>
            <div id="loadedData"></div>
            """, height=180)

    with col2:
        st.markdown("#### Your Profile Card")
        if st.session_state.user_name:
            av   = st.session_state.user_age
            cats = {0:"👶",2:"🧒",13:"🧑",18:"👨",60:"👴"}
            cat  = next((v for k,v in sorted(cats.items(),reverse=True) if av>=k),"👤")
            conds = ", ".join(st.session_state.user_conditions) or "None"
            g    = T["g"]
            p    = T["p"]
            st.markdown(f"""
            <div class="profile-card">
                <div style="font-size:3rem">{g_emoji}</div>
                <div style="font-size:1.3rem;font-weight:700;margin:8px 0">
                    {st.session_state.user_name}</div>
                <div>Age: {av} {cat}</div>
                <div>{st.session_state.gender} · {st.session_state.user_city}</div>
                <div>Blood: {st.session_state.user_blood_type}</div>
                <div style="margin-top:10px;background:rgba(255,255,255,0.2);
                    border-radius:8px;padding:8px;font-size:0.82rem">
                    Conditions: {conds}</div>
                <div style="margin-top:6px;font-size:0.75rem;opacity:0.75">
                    🔒 Private — only visible to you</div>
            </div>""", unsafe_allow_html=True)

            # Show storage info
            st.markdown(f"""
            <div style="background:{T["l"]};border-radius:10px;padding:12px 16px;
                 margin-top:10px;font-size:0.82rem;color:{T["p"]};
                 border:1px solid {T["p"]}33;">
                <b>How your profile is saved:</b><br>
                💾 On this device — stays even after browser closes<br>
                ☁️ On our server — for your health records<br>
                🔒 Never shared with anyone else
            </div>""", unsafe_allow_html=True)

        else:
            st.info("Fill in your profile and click Save. It will be saved permanently on your device.")

        st.markdown("---")

        # Clear profile option
        with st.expander("Clear my profile from this device"):
            st.warning("This will remove your profile from this device only.")
            if st.button("Clear Profile from Device", key="clear_local"):
                components.html("""
                <script>
                localStorage.removeItem('khareef_profile');
                alert('Profile cleared from this device.');
                </script>
                """, height=0)
                st.session_state.user_name        = ""
                st.session_state.user_age         = 40
                st.session_state.user_phone       = ""
                st.session_state.user_conditions  = []
                st.session_state.user_medications = ""
                st.success("Profile cleared from this device.")
                st.rerun()
