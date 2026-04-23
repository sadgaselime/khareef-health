import streamlit as st

def render(T):
    st.error("Life in danger? CALL 999 FIRST, then follow steps below")
    h1,h2,h3 = st.columns(3)
    with h1: st.error("Emergency\n999\n24/7")
    with h2: st.info("Sultan Qaboos Hospital\n+968 23 218 000\nAl Dahariz, Salalah")
    with h3: st.info("Salalah Private Hospital\n+968 23 295 999\nSalalah")
    st.link_button("Open Sultan Qaboos in Maps","https://maps.google.com/?q=Sultan+Qaboos+Hospital+Salalah+Oman")
    st.markdown("---")

    def steps(items, red=True):
        css = "step-red" if red else "step"
        for i,s in enumerate(items,1):
            st.markdown(f'<div class="{css}"><b>{i}.</b> {s}</div>', unsafe_allow_html=True)

    et1,et2,et3,et4,et5,et6 = st.tabs(["Heart Attack","CPR","Choking","Fainting","Heat Stroke","Infant"])

    with et1:
        c1,c2 = st.columns(2)
        with c1:
            st.markdown("**Signs:**")
            for s in ["Chest pain or pressure","Shortness of breath","Pain in left arm or jaw","Cold sweats","Nausea","Dizziness"]:
                st.markdown(f'<div class="step-red">{s}</div>', unsafe_allow_html=True)
        with c2:
            st.markdown("**Steps:**")
            steps(["Call 999","Sit patient down — do NOT walk","Loosen clothing","Aspirin 300mg if available","Stay — never leave alone","No food or water"])

    with et2:
        st.error("Only if person is unconscious and NOT breathing")
        c1,c2 = st.columns(2)
        with c1:
            steps(["Check response","Call 999","Lay flat on hard surface","Heel of hand on CENTRE of chest","Push DOWN 5-6cm hard and fast","30 compressions at 100-120/min","Tilt head, give 2 breaths","Repeat until help arrives"])
        with c2:
            st.warning("Push to beat of Stayin Alive = 100 bpm\n\nPress HARD — 5cm deep\n\nDont stop until paramedics arrive")

    with et3:
        c1,c2 = st.columns(2)
        with c1:
            steps(["Ask can you speak?","Tell to cough hard","5 back blows between shoulders","5 abdominal thrusts (Heimlich)","Alternate until clear","Call 999 if unconscious"])
        with c2:
            st.info("Heimlich: Stand behind, fist above belly button, sharp inward+upward thrusts")

    with et4:
        c1,c2 = st.columns(2)
        with c1:
            steps(["Lay flat","Raise legs above heart","Loosen clothing","Check breathing","Turn on side if vomiting","Call 999 if not waking in 1 min"], red=False)
        with c2:
            st.success("Prevention:\n- Drink water\n- Rise slowly\n- Eat regularly\n- Sit if feeling faint")

    with et5:
        st.error("Heat stroke is a MEDICAL EMERGENCY — call 999")
        c1,c2 = st.columns(2)
        with c1:
            for s in ["Temp above 40C","Confusion","Hot dry skin","Nausea","Rapid heartbeat"]:
                st.markdown(f'<div class="step-red">{s}</div>', unsafe_allow_html=True)
        with c2:
            steps(["Call 999","Move to cool shade","Remove excess clothing","Wet cloths on neck+armpits","Fan continuously","Cool water if conscious","Do NOT give aspirin"], red=False)

    with et6:
        st.error("Infant emergencies — ALWAYS call 999 immediately")
        c1,c2 = st.columns(2)
        with c1:
            st.markdown("**Fever Emergencies:**")
            for s in ["Any fever in baby UNDER 3 MONTHS","Fever above 39C in 3-6 month baby","Infant not feeding for 8+ hours","Baby very hard to wake up","Rash with fever","Difficulty breathing"]:
                st.markdown(f'<div class="step-red">{s}</div>', unsafe_allow_html=True)
        with c2:
            st.markdown("**Infant Choking:**")
            steps(["Hold face-down on forearm","5 back blows with heel","Turn face-up carefully","5 chest thrusts with 2 fingers","Check mouth for visible object","DO NOT do abdominal thrusts on infants","Call 999 immediately"])
