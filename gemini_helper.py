"""
gemini_helper.py – Google Gemini AI Connection
Works both locally (.env) and on Streamlit Cloud (st.secrets)
"""

import os

# Try to load streamlit secrets first (for cloud deployment)
GEMINI_API_KEY = ""

try:
    import streamlit as st
    GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")
except Exception:
    pass

# If not found in streamlit secrets, try .env file (for local use)
if not GEMINI_API_KEY:
    try:
        from dotenv import load_dotenv
        load_dotenv()
        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    except Exception:
        pass

# Load Gemini library
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

# Configure Gemini if available
if GENAI_AVAILABLE and GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


def is_api_key_configured():
    """Returns True if API key is set."""
    return bool(GEMINI_API_KEY and len(GEMINI_API_KEY) > 20)


def get_api_key_status():
    """Returns status message about API key."""
    if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_GEMINI_API_KEY_HERE":
        return "No API key found. Add to .env file or Streamlit secrets."
    elif not GENAI_AVAILABLE:
        return "google-generativeai not installed."
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
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)
        full_text = response.text.strip()

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


# ══════════════════════════════════════
# FREE TEXT HEALTH ANALYSIS
# Uses the structured medical AI prompt
# ══════════════════════════════════════

def analyze_free_text(user_input: str, language: str = "en") -> dict:
    """
    Analyzes a user's free-text health concern using a structured medical prompt.
    Works for ANY health problem the user types — not just predefined symptoms.

    Parameters:
    -----------
    user_input : The user's description of their health problem
    language   : "en" for English, "ar" for Arabic response

    Returns:
    --------
    dict with: success, symptoms, causes, explanation,
               urgency, next_steps, full_text, error
    """

    if not is_api_key_configured() or not GENAI_AVAILABLE:
        return {
            "success": False,
            "error": "Gemini AI not available. Please check API key.",
        }

    if not user_input or not user_input.strip():
        return {
            "success": False,
            "error": "Please describe your health concern.",
        }

    arabic_instruction = (
        "Respond ENTIRELY in Arabic (العربية). Use simple, clear Arabic."
        if language == "ar" else
        "Respond in English."
    )

    prompt = f"""
You are an AI medical assistant. Your job is to analyze a user's health concern
and respond like a cautious, helpful doctor.

{arabic_instruction}

User input:
"{user_input}"

Tasks:
1. Extract all symptoms clearly from the text.
2. Identify 2–3 most likely causes (not too many).
3. Explain in simple language WHY these symptoms may be happening.
4. Assign an urgency level: "low", "medium", or "high".
5. Give clear, practical next steps for the user.

Rules:
- NEVER say "all clear" if any symptom is mentioned.
- Be cautious and realistic — do not guarantee any diagnosis.
- If symptoms could be serious (chest pain, breathing issues, loss of consciousness),
  mark urgency as HIGH and advise going to hospital immediately.
- Keep the response short, structured, and easy to read.
- Do NOT use complex medical jargon.
- Always prioritize user safety.
- This is for patients in Salalah, Oman — mention Sultan Qaboos Hospital
  Salalah (phone: +968 23 218 000) if urgency is HIGH.

Output EXACTLY in this format — do not add anything else:

SYMPTOMS:
- [symptom 1]
- [symptom 2]

POSSIBLE CAUSES:
- [cause 1]
- [cause 2]

WHY THIS MIGHT BE HAPPENING:
[simple 2-3 sentence explanation]

URGENCY: [LOW / MEDIUM / HIGH]

WHAT TO DO NEXT:
- [step 1]
- [step 2]
- [step 3]
"""

    try:
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            generation_config=genai.GenerationConfig(
                temperature=0.3,
                max_output_tokens=800,
            ),
        )
        response = model.generate_content(prompt)
        full_text = response.text.strip()

        # Parse the structured response
        parsed = _parse_structured_response(full_text)
        parsed["success"]   = True
        parsed["full_text"] = full_text
        parsed["error"]     = None
        return parsed

    except Exception as e:
        return {
            "success":   False,
            "full_text": "",
            "error":     str(e),
        }


def _parse_structured_response(text: str) -> dict:
    """
    Parses the structured AI response into a clean dictionary.
    Handles slight variations in formatting.
    """
    result = {
        "symptoms":    [],
        "causes":      [],
        "explanation": "",
        "urgency":     "MEDIUM",
        "next_steps":  [],
    }

    lines = text.split("\n")
    current_section = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Detect sections
        upper = line.upper()
        if "SYMPTOMS:" in upper or upper.startswith("SYMPTOMS"):
            current_section = "symptoms"
            continue
        elif "POSSIBLE CAUSES:" in upper or upper.startswith("POSSIBLE CAUSES"):
            current_section = "causes"
            continue
        elif "WHY THIS" in upper:
            current_section = "explanation"
            continue
        elif "URGENCY:" in upper or upper.startswith("URGENCY"):
            current_section = "urgency"
            # Extract urgency level from same line
            for level in ["HIGH", "MEDIUM", "LOW"]:
                if level in upper:
                    result["urgency"] = level
                    break
            continue
        elif "WHAT TO DO" in upper or "NEXT STEPS" in upper:
            current_section = "next_steps"
            continue

        # Collect content per section
        if current_section == "symptoms" and line.startswith("-"):
            result["symptoms"].append(line[1:].strip())
        elif current_section == "causes" and line.startswith("-"):
            result["causes"].append(line[1:].strip())
        elif current_section == "explanation":
            result["explanation"] += line + " "
        elif current_section == "urgency":
            for level in ["HIGH", "MEDIUM", "LOW"]:
                if level in line.upper():
                    result["urgency"] = level
                    break
        elif current_section == "next_steps" and line.startswith("-"):
            result["next_steps"].append(line[1:].strip())

    result["explanation"] = result["explanation"].strip()
    return result
