import streamlit as st

CROSS_SVG = """<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}"><defs><linearGradient id="cg" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#60a5fa"/><stop offset="100%" stop-color="#1d4ed8"/></linearGradient></defs><rect x="42" y="20" width="16" height="60" rx="8" fill="url(#cg)"/><rect x="20" y="42" width="60" height="16" rx="8" fill="url(#cg)"/></svg>"""

HEART_SVG = """<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}"><defs><radialGradient id="hg" cx="50%" cy="40%" r="60%"><stop offset="0%" stop-color="#ff6b8a"/><stop offset="100%" stop-color="#dc2626"/></radialGradient></defs><path d="M50 80 C50 80 15 55 15 32 C15 20 25 12 35 12 C41 12 47 15 50 20 C53 15 59 12 65 12 C75 12 85 20 85 32 C85 55 50 80 50 80Z" fill="url(#hg)"/><path d="M25 42 L35 42 L40 32 L45 52 L50 36 L55 42 L70 42" stroke="white" stroke-width="3.5" fill="none" stroke-linecap="round"/></svg>"""

PULSE_SVG = """<svg viewBox="0 0 100 40" xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}"><path d="M0 20 L18 20 L24 5 L30 35 L36 12 L42 28 L48 20 L100 20" stroke="#dc2626" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>"""

SHIELD_SVG = """<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}"><defs><linearGradient id="shg" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#10b981"/><stop offset="100%" stop-color="#065f46"/></linearGradient></defs><path d="M50 8 L85 22 L85 52 C85 70 68 85 50 92 C32 85 15 70 15 52 L15 22 Z" fill="url(#shg)" opacity="0.9"/><path d="M35 50 L45 60 L65 40" stroke="white" stroke-width="6" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>"""

def svg(t, w=60, h=60): return t.format(w=w, h=h)

HOSPITALS = [
    {
        "type":"Government — Main Hospital",
        "color":"#dc2626","bg":"#fff1f2",
        "places":[{
            "name":"Sultan Qaboos Hospital",
            "arabic":"مستشفى السلطان قابوس",
            "phone":"+968 23 211 555",
            "emergency":"999",
            "location":"Al Dahariz, Salalah",
            "hours":"24 Hours — 7 Days",
            "services":"Emergency, Surgery, Maternity, Paediatrics, ICU, All Specialties",
            "badge":"Main Referral · 450 Beds",
            "maps":"https://maps.google.com/?q=Sultan+Qaboos+Hospital+Salalah+Oman",
        }]
    },
    {
        "type":"Private Hospitals",
        "color":"#1d4ed8","bg":"#eff6ff",
        "places":[
            {
                "name":"Badr Al Samaa Hospital",
                "arabic":"مستشفى بدر السماء",
                "phone":"+968 23 219 999",
                "emergency":"+968 23 219 999",
                "location":"Salalah",
                "hours":"24 Hours",
                "services":"All Specialties, ICU, Maternity, Dialysis, Eye Centre, Lab",
                "badge":"25+ Specialists",
                "maps":"https://maps.google.com/?q=Badr+Al+Samaa+Hospital+Salalah",
            },
            {
                "name":"Lifeline Hospital",
                "arabic":"مستشفى لايف لاين",
                "phone":"+968 23 295 999",
                "emergency":"+968 23 295 999",
                "location":"Opp Lulu Hypermarket, Al Wadi, Salalah",
                "hours":"24 Hours",
                "services":"General Medicine, Surgery, Paediatrics, Maternity, Emergency",
                "badge":"Multi-Specialty",
                "maps":"https://maps.google.com/?q=Lifeline+Hospital+Salalah+Oman",
            },
            {
                "name":"Salalah Best Medical Complex",
                "arabic":"مجمع صلالة الطبي",
                "phone":"+968 23 200 000",
                "emergency":"+968 23 200 000",
                "location":"Salalah City",
                "hours":"Sat-Thu 8AM-10PM, Fri 4PM-10PM",
                "services":"General Practice, Dental, Pharmacy, Lab",
                "badge":"GP + Dental",
                "maps":"https://maps.google.com/?q=Salalah+Best+Medical+Complex+Oman",
            },
        ]
    },
    {
        "type":"Government Health Centres (Free)",
        "color":"#065f46","bg":"#f0fdf4",
        "places":[
            {
                "name":"Salalah Al Jadidah Health Centre",
                "arabic":"مركز صحي صلالة الجديدة",
                "phone":"+968 23 295 000",
                "emergency":"999",
                "location":"New Salalah, near Government Offices",
                "hours":"Sun-Thu 7:30AM-2:30PM",
                "services":"GP, Vaccinations, Maternal Health, Chronic Disease Management",
                "badge":"Free — Government",
                "maps":"https://maps.google.com/?q=Salalah+Jadidah+Health+Center+Oman",
            },
            {
                "name":"Salalah Al Gharbiah Health Centre",
                "arabic":"مركز صحي صلالة الغربية",
                "phone":"+968 23 290 000",
                "emergency":"999",
                "location":"West Salalah, in front of Directorate of Housing",
                "hours":"Sun-Thu 7:30AM-2:30PM",
                "services":"GP, Vaccinations, Child Health, Chronic Disease",
                "badge":"Free — Government",
                "maps":"https://maps.google.com/?q=Salalah+Gharbiah+Health+Center+Oman",
            },
        ]
    },
    {
        "type":"Specialist Clinics",
        "color":"#7c3aed","bg":"#f5f3ff",
        "places":[
            {
                "name":"Badr Al Samaa Eye Centre",
                "arabic":"مركز العيون — بدر السماء",
                "phone":"+968 23 219 999",
                "emergency":"+968 23 219 999",
                "location":"Salalah",
                "hours":"Daily 8AM-10PM",
                "services":"Ophthalmology, Vision Testing, Eye Surgery. First private eye centre in Oman.",
                "badge":"Eye Specialist",
                "maps":"https://maps.google.com/?q=Badr+Al+Samaa+Hospital+Salalah",
            },
            {
                "name":"Ministry of Health Dental Clinic",
                "arabic":"عيادة الأسنان — وزارة الصحة",
                "phone":"+968 23 211 555",
                "emergency":"999",
                "location":"Sultan Qaboos Hospital Campus, Salalah",
                "hours":"Sun-Thu 7:30AM-2:30PM",
                "services":"Dental Surgery, Orthodontics, Extractions, Fillings",
                "badge":"Dental",
                "maps":"https://maps.google.com/?q=Sultan+Qaboos+Hospital+Salalah+Oman",
            },
        ]
    },
]

def render(T):
    p = T['p']; l = T['l']; g = T['g']

    # Hero
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#7f1d1d,#dc2626);border-radius:20px;
         padding:26px 30px;color:white;margin-bottom:20px;
         box-shadow:0 8px 28px rgba(220,38,38,0.3);">
        <div style="display:flex;align-items:center;gap:18px;flex-wrap:wrap;">
            <div style="font-size:3rem">🚨</div>
            <div style="flex:1">
                <div style="font-size:1.5rem;font-weight:800">EMERGENCY GUIDE</div>
                <div style="font-family:'Tajawal',sans-serif;font-size:0.95rem;opacity:0.85;
                     direction:rtl">دليل الإسعافات الأولية · صلالة، ظفار</div>
                <div style="margin-top:6px;font-size:0.85rem;opacity:0.85">
                    CPR · Heart Attack · Choking · Fainting · Heat Stroke · Infant</div>
            </div>
            <div style="text-align:center;background:rgba(0,0,0,0.25);border-radius:12px;
                 padding:10px 18px;border:2px solid rgba(255,255,255,0.3);">
                <div style="font-size:0.75rem;letter-spacing:2px">EMERGENCY</div>
                <div style="font-size:2.5rem;font-weight:900;letter-spacing:2px">999</div>
            </div>
        </div>
        <div style="margin-top:14px;opacity:0.3">{svg(PULSE_SVG,300,30)}</div>
    </div>""", unsafe_allow_html=True)

    # Hospitals
    st.markdown("### All Hospitals in Salalah / جميع المستشفيات")

    for grp in HOSPITALS:
        c = grp['color']; b = grp['bg']
        st.markdown(f"""
        <div style="background:{b};border-left:5px solid {c};border-radius:14px;
             padding:14px 18px;margin:10px 0;">
            <div style="font-weight:700;color:{c};font-size:1rem;margin-bottom:10px">
                {grp['type']}</div>""", unsafe_allow_html=True)

        cols = st.columns(min(len(grp['places']),2))
        for i, h in enumerate(grp['places']):
            with cols[i%2]:
                st.markdown(f"""
                <div style="background:white;border-radius:12px;padding:14px;
                     border:1px solid {c}22;margin-bottom:8px;
                     box-shadow:0 2px 8px rgba(0,0,0,0.04);">
                    <div style="display:flex;align-items:flex-start;gap:8px;margin-bottom:8px">
                        <div>{svg(CROSS_SVG,32,32)}</div>
                        <div>
                            <div style="font-weight:700;color:{c};font-size:0.9rem">
                                {h['name']}</div>
                            <div style="font-family:'Tajawal',sans-serif;font-size:0.82rem;
                                 color:#6b7280;direction:rtl">{h['arabic']}</div>
                            <span style="background:{c};color:white;padding:1px 8px;
                                 border-radius:99px;font-size:0.7rem;font-weight:600">
                                {h['badge']}</span>
                        </div>
                    </div>
                    <div style="font-size:0.8rem;color:#374151;line-height:1.9">
                        📞 <b>{h['phone']}</b><br>
                        🚨 Emergency: <b>{h['emergency']}</b><br>
                        📍 {h['location']}<br>
                        🕐 {h['hours']}<br>
                        🏥 {h['services']}
                    </div>
                </div>""", unsafe_allow_html=True)
                st.link_button(f"Open in Maps", h['maps'])

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")

    # First aid guide
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:12px;margin-bottom:14px;">
        {svg(SHIELD_SVG,46,46)}
        <div>
            <div style="font-size:1.15rem;font-weight:700;color:{p}">
                First Aid Guide / دليل الإسعافات</div>
            <div style="font-size:0.82rem;color:#6b7280">
                Step by step emergency instructions</div>
        </div>
    </div>""", unsafe_allow_html=True)

    def steps(items, red=True):
        css = "step-red" if red else "step"
        for i,s in enumerate(items,1):
            st.markdown(f'<div class="{css}"><b>{i}.</b> {s}</div>',
                        unsafe_allow_html=True)

    et1,et2,et3,et4,et5,et6 = st.tabs([
        "Heart Attack","CPR","Choking","Fainting","Heat Stroke","Infant"])

    with et1:
        c1,c2 = st.columns(2)
        with c1:
            st.markdown(f'<div style="text-align:center">{svg(HEART_SVG,70,70)}</div>',
                        unsafe_allow_html=True)
            for s in ["Chest pain or pressure","Shortness of breath",
                      "Pain in left arm or jaw","Cold sweats","Nausea","Dizziness"]:
                st.markdown(f'<div class="step-red">{s}</div>',unsafe_allow_html=True)
        with c2:
            steps(["Call 999 immediately",
                   "Sit down — do NOT walk",
                   "Loosen tight clothing",
                   "Aspirin 300mg if available",
                   "Stay — never leave alone",
                   "No food or water"])

    with et2:
        st.error("Only if unconscious and NOT breathing")
        c1,c2 = st.columns(2)
        with c1:
            steps(["Check response — tap shoulder",
                   "Call 999",
                   "Lay flat on hard surface",
                   "Heel of hand on CENTRE of chest",
                   "Push 5-6cm hard and fast",
                   "30 compressions at 100-120/min",
                   "Tilt head, give 2 breaths",
                   "Repeat until help arrives"])
        with c2:
            st.warning("Push to beat of Stayin Alive = 100 bpm\n\nPress HARD — 5cm deep\n\nDo not stop until paramedics arrive")

    with et3:
        c1,c2 = st.columns(2)
        with c1:
            steps(["Ask: Can you speak?",
                   "Tell to cough hard",
                   "5 back blows between shoulders",
                   "5 abdominal thrusts (Heimlich)",
                   "Alternate until clear",
                   "Call 999 if unconscious"])
        with c2:
            st.info("Heimlich: Stand behind, fist above belly button, sharp inward + upward thrusts")

    with et4:
        c1,c2 = st.columns(2)
        with c1:
            steps(["Lay flat","Raise legs above heart",
                   "Loosen clothing","Check breathing",
                   "Turn on side if vomiting",
                   "Call 999 if not waking in 1 min"], red=False)
        with c2:
            st.success("Drink water regularly\nRise slowly from sitting\nEat regular meals")

    with et5:
        st.error("Heat stroke — MEDICAL EMERGENCY — call 999")
        c1,c2 = st.columns(2)
        with c1:
            for s in ["Temp above 40C","Confusion","Hot dry skin","Nausea"]:
                st.markdown(f'<div class="step-red">{s}</div>',unsafe_allow_html=True)
        with c2:
            steps(["Call 999","Move to cool shade",
                   "Remove excess clothing",
                   "Wet cloths on neck and armpits",
                   "Fan continuously",
                   "Cool water if conscious",
                   "Do NOT give aspirin"], red=False)

    with et6:
        st.error("Infant emergencies — ALWAYS call 999 immediately")
        c1,c2 = st.columns(2)
        with c1:
            for s in ["Any fever in baby UNDER 3 MONTHS",
                      "Fever above 39C in 3-6 month baby",
                      "Not feeding for 8+ hours",
                      "Hard to wake up","Rash with fever"]:
                st.markdown(f'<div class="step-red">{s}</div>',unsafe_allow_html=True)
        with c2:
            steps(["Hold face-down on forearm",
                   "5 back blows with heel",
                   "Turn face-up — 5 chest thrusts",
                   "Call 999 immediately"])
