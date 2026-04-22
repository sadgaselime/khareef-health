# ============================================================
# FILE: data.py
# SAVE IN: khareef_health/ folder
# PURPOSE: Stores patient data, validates it, maps symptoms
# ============================================================

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


# ────────────────────────────────────────────
# PATIENT DATA STRUCTURE
# A "dataclass" is just a neat way to store
# related information together.
# ────────────────────────────────────────────

@dataclass
class Patient:
    """
    Holds all information about one patient.
    When you create a Patient, you pass in all these values.

    Example:
        p = Patient(name="Ahmed", age=70, ...)
    """
    name: str                           # Patient's full name
    age: int                            # Age in years
    blood_pressure_systolic: int        # Upper BP number  (e.g., 120)
    blood_pressure_diastolic: int       # Lower BP number  (e.g., 80)
    blood_sugar: float                  # Blood sugar in mg/dL
    temperature: float                  # Body temperature in Celsius
    symptoms: List[str]                 # e.g., ["cough", "dizziness"]
    khareef_mode: bool = False          # True during monsoon season
    timestamp: str = field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M")
    )

    def summary(self) -> dict:
        """
        Returns a simple dictionary of patient vitals.
        Used for displaying in tables and sending to Gemini AI.
        """
        return {
            "Name": self.name,
            "Age": self.age,
            "BP": f"{self.blood_pressure_systolic}/{self.blood_pressure_diastolic} mmHg",
            "Blood Sugar": f"{self.blood_sugar} mg/dL",
            "Temperature": f"{self.temperature} °C",
            "Symptoms": ", ".join(self.symptoms) if self.symptoms else "None reported",
            "Khareef Mode": "ON" if self.khareef_mode else "OFF",
            "Recorded At": self.timestamp,
        }


# ────────────────────────────────────────────
# SYMPTOM ALIASES
# Maps many different ways of saying the same
# symptom (including Arabic) to one standard key.
# ────────────────────────────────────────────

SYMPTOM_ALIASES = {
    # ── COUGH ──
    "cough": "cough",
    "coughing": "cough",
    "dry cough": "cough",
    "سعال": "cough",                    # Arabic: cough
    "كحة": "cough",                    # Arabic: cough (colloquial)

    # ── BREATHLESSNESS ──
    "breathless": "breathlessness",
    "breathlessness": "breathlessness",
    "short of breath": "breathlessness",
    "difficulty breathing": "breathlessness",
    "can't breathe": "breathlessness",
    "ضيق التنفس": "breathlessness",     # Arabic: shortness of breath
    "صعوبة التنفس": "breathlessness",   # Arabic: difficulty breathing

    # ── CHEST PAIN ──
    "chest pain": "chest_pain",
    "chest ache": "chest_pain",
    "chest pressure": "chest_pain",
    "ألم في الصدر": "chest_pain",       # Arabic: chest pain
    "وجع الصدر": "chest_pain",          # Arabic: chest ache (colloquial)

    # ── DIZZINESS ──
    "dizzy": "dizziness",
    "dizziness": "dizziness",
    "lightheaded": "dizziness",
    "vertigo": "dizziness",
    "دوار": "dizziness",               # Arabic: dizziness
    "دوخة": "dizziness",               # Arabic: dizziness (colloquial)

    # ── FEVER ──
    "fever": "fever",
    "high temperature": "fever",
    "hot": "fever",
    "حمى": "fever",                    # Arabic: fever
    "سخونة": "fever",                  # Arabic: fever (colloquial)

    # ── FATIGUE ──
    "fatigue": "fatigue",
    "tired": "fatigue",
    "weakness": "fatigue",
    "exhausted": "fatigue",
    "إعياء": "fatigue",                # Arabic: fatigue
    "تعب": "fatigue",                  # Arabic: tiredness

    # ── HEADACHE ──
    "headache": "headache",
    "head pain": "headache",
    "migraine": "headache",
    "صداع": "headache",               # Arabic: headache

    # ── NAUSEA ──
    "nausea": "nausea",
    "vomiting": "nausea",
    "nauseous": "nausea",
    "غثيان": "nausea",                # Arabic: nausea
    "قيء": "nausea",                  # Arabic: vomiting
}


def normalize_symptoms(raw_symptoms: List[str]) -> List[str]:
    """
    Takes a list of symptom strings (in any language/format)
    and returns standardized symptom keys.

    Example:
        Input:  ["سعال", "dizzy", "chest pain"]
        Output: ["cough", "dizziness", "chest_pain"]
    """
    normalized = set()  # Using a set removes duplicates automatically
    for symptom in raw_symptoms:
        cleaned = symptom.strip().lower()
        if cleaned in SYMPTOM_ALIASES:
            # Known symptom — use the standard key
            normalized.add(SYMPTOM_ALIASES[cleaned])
        elif cleaned:
            # Unknown symptom — keep it as-is
            normalized.add(cleaned)
    return list(normalized)


# ────────────────────────────────────────────
# INPUT VALIDATION
# Checks that the numbers entered are realistic.
# Returns an error message, or None if all is fine.
# ────────────────────────────────────────────

def validate_patient_input(
    name: str,
    age: int,
    bp_sys: int,
    bp_dia: int,
    sugar: float,
    temp: float,
) -> Optional[str]:
    """
    Validates all patient inputs before running triage.

    Returns:
        str  → An error message if something is wrong
        None → Everything is valid, proceed
    """
    if not name or not name.strip():
        return "⚠️ Please enter the patient's name."

    if not (1 <= age <= 120):
        return "⚠️ Please enter a realistic age (1–120 years)."

    if not (60 <= bp_sys <= 240):
        return "⚠️ Systolic (upper) BP must be between 60 and 240 mmHg."

    if not (40 <= bp_dia <= 140):
        return "⚠️ Diastolic (lower) BP must be between 40 and 140 mmHg."

    if bp_dia >= bp_sys:
        return "⚠️ Diastolic BP cannot be higher than Systolic BP."

    if not (30.0 <= sugar <= 700.0):
        return "⚠️ Blood sugar must be between 30 and 700 mg/dL."

    if not (34.0 <= temp <= 43.0):
        return "⚠️ Temperature must be between 34.0°C and 43.0°C."

    return None  # ← All valid!


# ────────────────────────────────────────────
# SESSION LOG
# Keeps a list of all patients assessed during
# this app session (disappears when app closes).
# ────────────────────────────────────────────

# This list stores all assessments for this session
SESSION_LOG: List[dict] = []


def log_patient(patient: Patient, triage_result: dict) -> None:
    """
    Saves one patient assessment to the session log.
    Called after every successful triage.
    """
    entry = {
        **patient.summary(),                                      # All vitals
        "Triage Level":   triage_result.get("level", "UNKNOWN"), # GREEN/YELLOW/RED
        "Primary Advice": triage_result.get("rule_advice_en", "")[:80] + "...",
    }
    SESSION_LOG.append(entry)


def get_session_log() -> List[dict]:
    """Returns all patient assessments from this session."""
    return SESSION_LOG