"""
tab_reminders.py — Medicine Reminders + Health Alerts
Sends WhatsApp messages via Twilio
"""
import streamlit as st
import json, os
from datetime import datetime, time

REMINDERS_FILE = "reminders.json"

def load_reminders():
    if os.path.exists(REMINDERS_FILE):
        try: return json.load(open(REMINDERS_FILE))
        except: return []
    return []

def save_reminders(data):
    json.dump(data, open(REMINDERS_FILE,"w"), indent=2, ensure_ascii=False)

def send_whatsapp(to_number, message, account_sid, auth_token):
    """Send WhatsApp message via Twilio"""
    try:
        from twilio.rest import Client
        client = Client(account_sid, auth_token)
        msg = client.messages.create(
            from_="whatsapp:+14155238886",  # Twilio sandbox number
            body=message,
            to=f"whatsapp:+{to_number}"
        )
        return True, msg.sid
    except ImportError:
        return False, "Twilio not installed"
    except Exception as e:
        return False, str(e)

def render(T):
    st.markdown("### Medicine Reminders & Health Alerts")
    st.markdown("""
    <div style="background:linear-gradient(135deg,#065f46,#047857);border-radius:14px;
         padding:20px 26px;color:white;margin-bottom:16px;">
        <div style="font-size:1.3rem;font-weight:700">💊 WhatsApp Reminders</div>
        <div style="opacity:0.85;font-size:0.9rem;margin-top:4px">
            Get medicine reminders and health alerts sent directly to your WhatsApp
        </div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="disclaimer">You need a free Twilio account to send WhatsApp messages. Go to twilio.com to sign up.</div>', unsafe_allow_html=True)
    st.markdown("")

    rt1, rt2, rt3 = st.tabs(["💊 Medicine Reminders", "🚨 Health Alerts", "⚙️ Setup"])

    # ── TAB 1: MEDICINE REMINDERS ──
    with rt1:
        st.markdown("### Add Medicine Reminder")
        r1,r2 = st.columns(2)
        with r1:
            med_name = st.text_input("Medicine Name:", placeholder="e.g. Metformin 500mg", key="rem_name")
            med_dose = st.text_input("Dose:", placeholder="e.g. 1 tablet", key="rem_dose")
            med_phone = st.text_input("WhatsApp Number (with country code):",
                placeholder="96891234567", key="rem_phone")
        with r2:
            med_times = st.multiselect("Reminder times:",
                ["6:00 AM","7:00 AM","8:00 AM","12:00 PM",
                 "1:00 PM","6:00 PM","8:00 PM","10:00 PM"],
                key="rem_times")
            med_food = st.selectbox("Take with:",
                ["With food","Before food","After food","Any time"],
                key="rem_food")
            med_notes = st.text_input("Notes:", placeholder="e.g. Take with water", key="rem_notes")

        if st.button("💊 Save Reminder", type="primary", use_container_width=True, key="save_rem"):
            if med_name and med_phone and med_times:
                reminders = load_reminders()
                reminders.append({
                    "type": "medicine",
                    "name": med_name,
                    "dose": med_dose,
                    "phone": med_phone,
                    "times": med_times,
                    "food": med_food,
                    "notes": med_notes,
                    "active": True,
                    "created": datetime.now().strftime("%Y-%m-%d %H:%M"),
                })
                save_reminders(reminders)
                st.success(f"Reminder saved for {med_name}!")

                # Send confirmation WhatsApp
                try:
                    import streamlit as st2
                    sid   = st.secrets.get("TWILIO_SID","")
                    token = st.secrets.get("TWILIO_TOKEN","")
                    if sid and token:
                        msg = f"""*Khareef Health - Reminder Set!*

Your medicine reminder has been set:

💊 *Medicine:* {med_name}
📋 *Dose:* {med_dose}
🍽️ *Take:* {med_food}
⏰ *Times:* {', '.join(med_times)}
📝 *Notes:* {med_notes or 'None'}

You will receive reminders at the set times.
_Khareef Health - Salalah, Oman_"""
                        ok, result = send_whatsapp(med_phone, msg, sid, token)
                        if ok:
                            st.info("Confirmation sent to WhatsApp!")
                except: pass
            else:
                st.warning("Please fill in medicine name, phone number, and at least one time.")

        # Show existing reminders
        reminders = load_reminders()
        medicine_rems = [r for r in reminders if r.get("type")=="medicine"]
        if medicine_rems:
            st.markdown("---")
            st.markdown("### Your Medicine Reminders")
            for i, rem in enumerate(medicine_rems):
                p = T['p']
                active_color = "#16a34a" if rem.get("active") else "#6b7280"
                st.markdown(f"""
                <div style="background:{T['l']};border-left:4px solid {active_color};
                     border-radius:10px;padding:14px 18px;margin:8px 0;">
                    <div style="display:flex;justify-content:space-between;flex-wrap:wrap;">
                        <b style="color:{p}">💊 {rem['name']} — {rem.get('dose','')}</b>
                        <span style="color:{active_color};font-size:0.82rem;font-weight:600">
                            {'ACTIVE' if rem.get('active') else 'PAUSED'}</span>
                    </div>
                    <div style="font-size:0.85rem;color:#374151;margin-top:6px">
                        ⏰ {', '.join(rem.get('times',[]))} &nbsp;|&nbsp;
                        🍽️ {rem.get('food','')} &nbsp;|&nbsp;
                        📞 +{rem.get('phone','')}
                    </div>
                </div>""", unsafe_allow_html=True)

            if st.button("Clear All Reminders", key="clear_rems"):
                save_reminders([r for r in reminders if r.get("type")!="medicine"])
                st.rerun()

        # Manual test send
        st.markdown("---")
        st.markdown("### Test Send a Reminder Now")
        test_phone = st.text_input("Phone number to test:", placeholder="96891234567", key="test_ph")
        test_med   = st.text_input("Medicine name:", placeholder="e.g. Paracetamol", key="test_med")
        if st.button("Send Test WhatsApp", key="test_send"):
            try:
                sid   = st.secrets.get("TWILIO_SID","")
                token = st.secrets.get("TWILIO_TOKEN","")
                if not sid or not token:
                    st.warning("Add TWILIO_SID and TWILIO_TOKEN to Streamlit secrets first.")
                else:
                    msg = f"""*Khareef Health - Medicine Reminder*

Time to take your medicine!

💊 *{test_med}*

Stay healthy!
_Khareef Health · Salalah, Oman_"""
                    ok, result = send_whatsapp(test_phone, msg, sid, token)
                    if ok: st.success("WhatsApp sent successfully!")
                    else:  st.error(f"Failed: {result}")
            except Exception as e:
                st.error(f"Error: {e}")

    # ── TAB 2: HEALTH ALERTS ──
    with rt2:
        st.markdown("### Health Alert Settings")
        st.markdown("Get automatic WhatsApp alerts when your health check shows RED or YELLOW")

        alert_phone = st.text_input("Your WhatsApp number:",
            value=st.session_state.get("user_phone",""),
            placeholder="96891234567", key="alert_phone")

        st.markdown("**Send alert when:**")
        alert_red    = st.checkbox("RED — Urgent health concern", value=True, key="alrt_r")
        alert_yellow = st.checkbox("YELLOW — Attention needed",   value=True, key="alrt_y")
        alert_emerg  = st.checkbox("Emergency symptoms detected", value=True, key="alrt_e")

        st.markdown("**Alert language:**")
        alert_lang = st.radio("", ["English","Arabic","Both"], horizontal=True, key="alrt_lang")

        if st.button("Save Alert Settings", type="primary", key="save_alerts"):
            st.session_state["alert_phone"]  = alert_phone
            st.session_state["alert_red"]    = alert_red
            st.session_state["alert_yellow"] = alert_yellow
            st.session_state["alert_lang"]   = alert_lang
            st.success("Alert settings saved!")

        st.markdown("---")
        st.markdown("### Weekly Health Summary")
        st.info("""
Every Sunday morning you will receive a WhatsApp summary:

Your health check history for the week
Average readings
Any concerning trends
Reminder to check BP/sugar

This feature activates automatically once you save your alert settings.
        """)

    # ── TAB 3: SETUP ──
    with rt3:
        st.markdown("### Setup WhatsApp Reminders")
        st.markdown("Follow these steps to enable WhatsApp notifications:")

        steps = [
            ("Go to twilio.com", "Click Sign up free and create an account"),
            ("Verify your phone", "Twilio will call or text you to verify"),
            ("Get your credentials", "Find Account SID and Auth Token on your dashboard"),
            ("Join WhatsApp sandbox", "Send 'join [your-code]' to +1 415 523 8886 on WhatsApp"),
            ("Add to Streamlit secrets", "Go to share.streamlit.io → your app → Settings → Secrets"),
            ("Paste these secrets", "Add TWILIO_SID and TWILIO_TOKEN"),
        ]
        for i, (title, detail) in enumerate(steps, 1):
            p = T['p']
            st.markdown(f"""
            <div style="background:{T['l']};border-left:4px solid {p};
                 border-radius:8px;padding:12px 16px;margin:8px 0;">
                <b style="color:{p}">Step {i}: {title}</b>
                <div style="font-size:0.88rem;color:#374151;margin-top:4px">{detail}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("### Add to Streamlit Secrets")
        st.code("""GEMINI_API_KEY = "your_key"
TWILIO_SID = "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
TWILIO_TOKEN = "your_auth_token"
TWILIO_PHONE = "whatsapp:+14155238886"
""")
        st.markdown("### Current Status")
        try:
            sid   = st.secrets.get("TWILIO_SID","")
            token = st.secrets.get("TWILIO_TOKEN","")
            if sid and token:
                st.success("Twilio configured!")
            else:
                st.warning("Twilio not configured yet. Add to Streamlit secrets.")
        except:
            st.warning("Add Twilio credentials to Streamlit secrets.")
