import streamlit as st

def section_header(icon, title, subtitle="", color="#1a5c45"):
    """Reusable section header with medical graphic."""
    import streamlit as st
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:14px;
         background:white;border-radius:14px;padding:16px 20px;
         margin-bottom:16px;box-shadow:0 2px 10px rgba(0,0,0,0.06);
         border-left:5px solid {color};">
        <div style="font-size:2.4rem;line-height:1">{icon}</div>
        <div>
            <div style="font-size:1.1rem;font-weight:700;color:{color}">{title}</div>
            <div style="font-size:0.82rem;color:#6b7280">{subtitle}</div>
        </div>
        <div style="margin-left:auto;opacity:0.08;font-size:3rem;font-weight:900;color:{color}">✚</div>
    </div>""", unsafe_allow_html=True)

def render(T):
    st.markdown("### Womens Health Guide / دليل صحة المرأة")
    st.markdown('<div class="disclaimer">General health information only. Always consult your doctor or gynaecologist.</div>', unsafe_allow_html=True)
    st.markdown("")

    wt1,wt2,wt3,wt4 = st.tabs(["Pregnancy","Period Care","Womens Medicines","When to Seek Help"])

    with wt1:
        c1,c2 = st.columns(2)
        with c1:
            for title, items in [
                ("First Trimester (Weeks 1-12)", ["Start folic acid 400mcg daily","Attend first antenatal appointment","Avoid alcohol, smoking, raw fish","Normal to feel nausea — eat small meals","Report heavy bleeding immediately","Safe: Paracetamol. Avoid ibuprofen."]),
                ("Second Trimester (Weeks 13-26)", ["Anomaly scan around week 20","Start iron supplements if low","Gentle walking is excellent","Sleep on LEFT side — better blood flow","Report reduced baby movement"]),
                ("Third Trimester (Weeks 27-40)", ["Attend all antenatal checks","Prepare hospital bag by week 36","Count baby movements daily","Go to hospital: contractions every 5 min","Go to hospital: waters breaking"]),
            ]:
                st.markdown(f"**{title}**")
                for item in items:
                    st.markdown(f'<div class="step">{item}</div>', unsafe_allow_html=True)
        with c2:
            st.error("Go to hospital immediately if:")
            for s in ["Heavy vaginal bleeding","Sudden gush of fluid","Severe headache","Blurred or double vision","Severe vomiting","Baby not moving for 2+ hours","Fever above 38C","Severe abdominal pain"]:
                st.markdown(f'<div class="step-red">{s}</div>', unsafe_allow_html=True)
            st.success("Safe foods: Cooked vegetables, fruits, well-cooked meat, pasteurised dairy, whole grains")
            st.error("Avoid: Raw fish, soft cheese, raw eggs, alcohol, excess caffeine")

    with wt2:
        c1,c2 = st.columns(2)
        with c1:
            st.markdown("**Managing Period Pain:**")
            for tip in ["Ibuprofen 400mg with food — best for cramps","Paracetamol if ibuprofen not suitable","Heat pad on lower abdomen — very effective","Ginger tea is especially helpful","Light walking improves blood flow","Warm bath relaxes muscles"]:
                st.markdown(f'<div class="step">{tip}</div>', unsafe_allow_html=True)
            st.success("Eat more: Iron-rich foods (spinach, red meat, lentils), bananas, omega-3 fish\nAvoid: Caffeine, salty foods, excess sugar")
        with c2:
            st.error("See a doctor if:")
            for s in ["Pain stops daily activities","Soaking more than 1 pad per hour","Periods lasting more than 7 days","No period for 3+ months (not pregnant)","Bleeding between periods","Fever with period pain"]:
                st.markdown(f'<div class="step-red">{s}</div>', unsafe_allow_html=True)

    with wt3:
        meds = {
            "Folic Acid":"400mcg daily. Start BEFORE pregnancy if planning. Continue through first 12 weeks.",
            "Iron Supplements":"As prescribed. Take with orange juice — vitamin C helps absorption. Causes dark stools (normal).",
            "Calcium + Vitamin D":"1000mg calcium + 600-800 IU Vitamin D daily. Essential in pregnancy and after menopause.",
            "Mefenamic Acid (Ponstan)":"500mg three times daily WITH food. Best for period pain — start 1 day before period begins.",
            "Oral Contraceptive Pill":"Take at SAME TIME every day. Does not protect against STIs.",
        }
        sel = st.selectbox("Select medicine:", list(meds.keys()), key="wmsel")
        if sel: st.info(meds[sel])

    with wt4:
        st.error("Call 999 or go to hospital immediately:")
        for s in ["Heavy vaginal bleeding","Any pregnancy complication","Chest pain or difficulty breathing","Sudden severe headache","Sudden vision changes","Confusion or loss of consciousness","High fever with pelvic pain"]:
            st.markdown(f'<div class="step-red">{s}</div>', unsafe_allow_html=True)
        st.markdown("**See doctor soon (1-2 days):**")
        for s in ["Period pain stopping daily activities","Unusual vaginal discharge","Burning when urinating","Lump in breast","Missed period (not pregnant)"]:
            st.markdown(f'<div class="step">{s}</div>', unsafe_allow_html=True)
        st.info("Sultan Qaboos Hospital Salalah — Maternity and Gynaecology\n+968 23 218 000 · Al Dahariz, Salalah")
