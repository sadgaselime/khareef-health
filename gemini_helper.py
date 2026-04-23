"""
gemini_helper.py – Google Gemini AI Connection
Uses the NEW google-genai SDK (2025+)
Model: gemini-2.5-flash (free tier)
"""

import os

# ── Load API key ──────────────────────────────
# Try Streamlit secrets first (cloud), then .env (local)
GEMINI_API_KEY = ""

try:
    import streamlit as st
    GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")
except Exception:
    pass

if not GEMINI_API_KEY:
    try:
        from dotenv import load_dotenv
        load_dotenv()
        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    except Exception:
        pass

# ── Load new Gemini SDK ───────────────────────
try:
    from google import genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

# Current free-tier model (April 2026)
MODEL = "gemini-2.5-flash"


def is_api_key_configured() -> bool:
    return bool(GEMINI_API_KEY and len(GEMINI_API_KEY) > 20)


def get_api_key_status() -> str:
    if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_GEMINI_API_KEY_HERE":
        return "No API key found. Add to Streamlit secrets."
    elif not GENAI_AVAILABLE:
        return "google-genai not installed. Check requirements.txt"
    else:
        preview = GEMINI_API_KEY[:8] + "..." + GEMINI_API_KEY[-4:]
        return f"API key loaded: {preview}"


def _get_client():
    """Creates and returns a Gemini client."""
    return genai.Client(api_key=GEMINI_API_KEY)


# ══════════════════════════════════════
# STRUCTURED PATIENT ADVICE
# ══════════════════════════════════════

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
    Sends patient vitals to Gemini and returns personalised advice
    in English and Arabic.
    """
    if not is_api_key_configured() or not GENAI_AVAILABLE:
        return {"success": False, "advice_en": "", "advice_ar": "", "error": "Gemini not available."}

    symptoms_text  = ", ".join(symptoms) if symptoms else "none"
    findings_text  = "\n".join([f"- {r}" for r in triage_reasons])
    khareef_note   = (
        "IMPORTANT: Khareef monsoon season is active in Salalah. "
        "High humidity increases respiratory risks for elderly patients."
        if khareef_mode else ""
    )

    prompt = f"""
You are a caring telemedicine doctor assistant for patients in Salalah, Oman.
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

Write a warm, simple, personalised health message using the patient's first name.
Use very simple words — no medical jargon.

Respond in EXACTLY this format:

ENGLISH:
[3-4 short paragraphs. Warm tone. Max 120 words.
If RED: include Sultan Qaboos Hospital Salalah, Emergency 999.]

ARABIC:
[Arabic translation. Simple Modern Arabic. Max 120 words.]
"""

    try:
        client   = _get_client()
        response = client.models.generate_content(model=MODEL, contents=prompt)
        text     = response.text.strip()

        advice_en, advice_ar = "", ""
        if "ARABIC:" in text:
            parts     = text.split("ARABIC:", 1)
            advice_ar = parts[1].strip()
            ep        = parts[0]
            advice_en = ep.split("ENGLISH:", 1)[1].strip() if "ENGLISH:" in ep else ep.strip()
        elif "ENGLISH:" in text:
            advice_en = text.split("ENGLISH:", 1)[1].strip()
        else:
            advice_en = text

        return {"success": True, "advice_en": advice_en, "advice_ar": advice_ar, "error": None}

    except Exception as e:
        return {"success": False, "advice_en": "", "advice_ar": "", "error": str(e)}


# ══════════════════════════════════════
# FREE TEXT HEALTH ANALYSIS
# ══════════════════════════════════════

def analyze_free_text(user_input: str, language: str = "en") -> dict:
    """
    Analyzes any health concern typed by the user.
    Returns structured: symptoms, causes, explanation, urgency, next_steps.
    """
    if not is_api_key_configured() or not GENAI_AVAILABLE:
        return {"success": False, "error": "Gemini AI not available. Please check API key."}

    if not user_input or not user_input.strip():
        return {"success": False, "error": "Please describe your health concern."}

    arabic_instruction = (
        "Respond ENTIRELY in Arabic (العربية). Use simple, clear Arabic."
        if language == "ar" else
        "Respond in English."
    )

    prompt = f"""
You are an AI medical assistant. Analyze the user's health concern like a cautious, helpful doctor.

{arabic_instruction}

User input: "{user_input}"

Tasks:
1. Extract all symptoms clearly from the text.
2. Identify 2-3 most likely causes (not too many).
3. Explain in simple language WHY these symptoms may be happening.
4. Assign an urgency level: "low", "medium", or "high".
5. Give clear, practical next steps for the user.

Rules:
- NEVER say "all clear" if any symptom is mentioned.
- Be cautious and realistic - do not guarantee any diagnosis.
- If symptoms could be serious (chest pain, breathing issues, loss of consciousness),
  mark urgency as HIGH and advise going to hospital immediately.
- Keep the response short, structured, and easy to read.
- Do NOT use complex medical jargon.
- This is for patients in Salalah, Oman.
- If urgency is HIGH, mention Sultan Qaboos Hospital Salalah (+968 23 218 000).

Output EXACTLY in this format - nothing else:

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
        client   = _get_client()
        response = client.models.generate_content(model=MODEL, contents=prompt)
        text     = response.text.strip()

        parsed            = _parse_structured_response(text)
        parsed["success"] = True
        parsed["full_text"] = text
        parsed["error"]   = None
        return parsed

    except Exception as e:
        return {"success": False, "full_text": "", "error": str(e)}


def _parse_structured_response(text: str) -> dict:
    """Parses the structured AI response into a clean dictionary."""
    result = {
        "symptoms":    [],
        "causes":      [],
        "explanation": "",
        "urgency":     "MEDIUM",
        "next_steps":  [],
    }

    current_section = None
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue

        upper = line.upper()
        if "SYMPTOMS:" in upper:
            current_section = "symptoms"; continue
        elif "POSSIBLE CAUSES:" in upper:
            current_section = "causes"; continue
        elif "WHY THIS" in upper:
            current_section = "explanation"; continue
        elif "URGENCY:" in upper:
            current_section = "urgency"
            for lvl in ["HIGH", "MEDIUM", "LOW"]:
                if lvl in upper:
                    result["urgency"] = lvl; break
            continue
        elif "WHAT TO DO" in upper or "NEXT STEPS" in upper:
            current_section = "next_steps"; continue

        if current_section == "symptoms" and line.startswith("-"):
            result["symptoms"].append(line[1:].strip())
        elif current_section == "causes" and line.startswith("-"):
            result["causes"].append(line[1:].strip())
        elif current_section == "explanation":
            result["explanation"] += line + " "
        elif current_section == "urgency":
            for lvl in ["HIGH", "MEDIUM", "LOW"]:
                if lvl in line.upper():
                    result["urgency"] = lvl; break
        elif current_section == "next_steps" and line.startswith("-"):
            result["next_steps"].append(line[1:].strip())

    result["explanation"] = result["explanation"].strip()
    return result
