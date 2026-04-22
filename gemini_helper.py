"""
gemini_helper.py – Google Gemini AI Connection
Save in: khareef_health/ folder
"""

import os

# Load .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Load Gemini library
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

# Get API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Configure Gemini if available
if GENAI_AVAILABLE and GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


def is_api_key_configured():
    """Returns True if API key is set."""
    return bool(GEMINI_API_KEY and len(GEMINI_API_KEY) > 20)


def get_api_key_status():
    """Returns status message about API key."""
    if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_GEMINI_API_KEY_HERE":
        return "No API key found. Add to .env file."
    elif not GENAI_AVAILABLE:
        return "google-generativeai not installed. Run: pip install google-generativeai"
    else:
        preview = GEMINI_API_KEY[:8] + "..." + GEMINI_API_KEY[-4:]
        return f"API key loaded: {preview}"


def get_gemini_advice(
    patient_name,
    patient_age,
    bp_systolic,
    bp_diastolic,
    blood_sugar,
    temperature,
    symptoms,
    triage_level,
    triage_reasons,
    khareef_mode=False,
):
    """
    Sends patient data to Gemini and gets advice back.
    Returns dict with: success, advice_en, advice_ar, error
    """

    if not is_api_key_configured() or not GENAI_AVAILABLE:
        return {
            "success": False,
            "advice_en": "",
            "advice_ar": "",
            "error": "Gemini not available.",
        }

    symptoms_text = ", ".join(symptoms) if symptoms else "none"
    findings_text = "\n".join([f"- {r}" for r in triage_reasons])
    khareef_note = (
        "IMPORTANT: Khareef monsoon season is active in Salalah. High humidity increases respiratory risks."
        if khareef_mode else ""
    )

    prompt = f"""
You are a caring telemedicine doctor assistant for elderly patients in Salalah, Oman.
{khareef_note}

PATIENT:
- Name: {patient_name}, Age: {patient_age}
- Blood Pressure: {bp_systolic}/{bp_diastolic} mmHg
- Blood Sugar: {blood_sugar} mg/dL
- Temperature: {temperature}C
- Symptoms: {symptoms_text}
- Triage Level: {triage_level}

FINDINGS:
{findings_text}

Write a warm, simple, personalised health message. Use the patient's first name.
Use very simple words — no medical jargon.

Respond in EXACTLY this format:

ENGLISH:
[3-4 short paragraphs. Simple English. Warm tone. Max 120 words.
If RED: include Sultan Qaboos Hospital Salalah, Emergency 999.]

ARABIC:
[Arabic translation of the above. Simple Modern Arabic. Max 120 words.]
"""

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        full_text = response.text.strip()

        # Parse English and Arabic
        advice_en = ""
        advice_ar = ""

        if "ARABIC:" in full_text:
            parts = full_text.split("ARABIC:", 1)
            advice_ar = parts[1].strip()
            english_part = parts[0]
            if "ENGLISH:" in english_part:
                advice_en = english_part.split("ENGLISH:", 1)[1].strip()
            else:
                advice_en = english_part.strip()
        elif "ENGLISH:" in full_text:
            advice_en = full_text.split("ENGLISH:", 1)[1].strip()
        else:
            advice_en = full_text

        return {
            "success": True,
            "advice_en": advice_en,
            "advice_ar": advice_ar,
            "error": None,
        }

    except Exception as e:
        return {
            "success": False,
            "advice_en": "",
            "advice_ar": "",
            "error": str(e),
        }
