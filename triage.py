# ============================================================
# FILE: triage.py
# SAVE IN: khareef_health/ folder
# PURPOSE: All the medical decision-making rules.
#          Decides GREEN / YELLOW / RED for each patient.
#
# DISCLAIMER: Educational use only. Not medical advice.
# ============================================================

from typing import List, Dict, Any


# ────────────────────────────────────────────
# TRIAGE LEVEL NAMES
# Using constants avoids typos like "green" vs "Green"
# ────────────────────────────────────────────

LEVEL_GREEN  = "GREEN"
LEVEL_YELLOW = "YELLOW"
LEVEL_RED    = "RED"


# ────────────────────────────────────────────
# NUTRITION SUGGESTIONS
# Shown to patients based on their condition.
# Organised by condition type.
# ────────────────────────────────────────────

NUTRITION_TIPS = {

    "high_bp": [
        "🥗 Reduce salt in ALL meals — avoid pickles, chips, and canned food",
        "🍌 Eat potassium-rich foods: bananas, sweet potatoes, spinach",
        "🧄 Add garlic and olive oil to your daily cooking",
        "💧 Drink 8–10 glasses of water every day",
        "🚫 Avoid coffee, energy drinks, and fatty red meat",
        "🏃 A 20-minute gentle walk daily helps lower blood pressure",
    ],

    "low_bp": [
        "🧂 Add a small amount of extra salt to food — ask your doctor first",
        "💧 Drink water frequently — dehydration worsens low BP",
        "🍳 Eat 5–6 small meals per day instead of 2–3 large ones",
        "☕ One cup of tea or coffee in the morning may help temporarily",
        "🚫 Get up slowly from bed or chair — sudden standing causes falls",
        "🧦 Compression stockings can help blood flow in the legs",
    ],

    "high_sugar": [
        "🥦 Eat more vegetables: okra, bitter melon, spinach, broccoli",
        "🌾 Replace white rice and bread with whole grain options",
        "🍎 Choose lower-sugar fruits: guava, green apple, berries",
        "💧 Water only — avoid juices, sodas, and sweet drinks",
        "🚫 No sweets, large amounts of dates, or fried snacks",
        "⏰ Eat at regular times every day — skipping meals raises sugar",
    ],

    "fever_respiratory": [
        "💧 Drink warm fluids: ginger tea, honey-lemon water, chicken broth",
        "🍋 Eat Vitamin C foods: oranges, guava, kiwi — boost immunity",
        "🍲 Light warm soups are best — easy to digest when unwell",
        "🚫 Avoid cold drinks, ice water, ice cream, and dairy when congested",
        "🛏️ Rest in a cool, ventilated room — sleep is the best healer",
        "💊 Take paracetamol for fever — avoid aspirin unless prescribed",
    ],

    "general_elderly": [
        "🥩 Eat enough protein every day: fish, eggs, lentils, chicken",
        "🦴 Calcium for bones: low-fat milk, yoghurt, sesame, almonds",
        "🌞 15 minutes of morning sun helps your body make Vitamin D",
        "💧 Elderly people feel less thirsty — set reminders to drink water",
        "🚫 Reduce fried, processed foods — prefer grilled or boiled",
        "🚶 Light daily walking improves heart health and balance",
    ],
}


# ────────────────────────────────────────────
# MAIN TRIAGE FUNCTION
# This is the heart of the medical logic.
# Call this with patient vitals → get a result.
# ────────────────────────────────────────────

def assess_patient(
    age: int,
    bp_systolic: int,
    bp_diastolic: int,
    blood_sugar: float,
    temperature: float,
    symptoms: List[str],
    khareef_mode: bool = False,
) -> Dict[str, Any]:
    """
    Runs the full triage assessment on a patient.

    HOW IT WORKS:
    1. Starts at GREEN (assume the patient is fine)
    2. Checks each vital sign against danger thresholds
    3. If a threshold is crossed, upgrades to YELLOW or RED
    4. Severity only goes UP, never DOWN (RED stays RED)
    5. Returns a full result dictionary

    Parameters:
    -----------
    age            : Patient age (years)
    bp_systolic    : Upper blood pressure (mmHg)
    bp_diastolic   : Lower blood pressure (mmHg)
    blood_sugar    : Blood glucose (mg/dL)
    temperature    : Body temperature (Celsius)
    symptoms       : List of standardized symptom keys
    khareef_mode   : If True, respiratory rules are stricter

    Returns:
    --------
    dict with: level, reasons, rule_advice_en, rule_advice_ar,
               nutrition, emoji, color
    """

    # ── STARTING STATE ────────────────────
    level = LEVEL_GREEN      # Begin as GREEN
    reasons = []             # Why we flagged this level
    nutrition_keys = []      # Which nutrition tips to show


    # ══════════════════════════════════════
    # CHECK 1: BLOOD PRESSURE
    # ══════════════════════════════════════

    if bp_systolic >= 180 or bp_diastolic >= 120:
        # Hypertensive crisis — emergency
        level = LEVEL_RED
        reasons.append(
            f"⚠️ Blood pressure is dangerously HIGH "
            f"({bp_systolic}/{bp_diastolic} mmHg). "
            f"This is a hypertensive crisis."
        )
        nutrition_keys.append("high_bp")

    elif bp_systolic < 90 or bp_diastolic < 60:
        # Severe hypotension — emergency
        level = LEVEL_RED
        reasons.append(
            f"⚠️ Blood pressure is dangerously LOW "
            f"({bp_systolic}/{bp_diastolic} mmHg). "
            f"Risk of shock or fainting."
        )
        nutrition_keys.append("low_bp")

    elif bp_systolic >= 160 or bp_diastolic >= 100:
        # Stage 2 hypertension
        level = _escalate(level, LEVEL_YELLOW)
        reasons.append(
            f"🔶 Blood pressure is significantly elevated "
            f"({bp_systolic}/{bp_diastolic} mmHg). "
            f"Needs doctor attention soon."
        )
        nutrition_keys.append("high_bp")

    elif bp_systolic >= 140 or bp_diastolic >= 90:
        # Stage 1 hypertension
        level = _escalate(level, LEVEL_YELLOW)
        reasons.append(
            f"🔶 Blood pressure is above normal "
            f"({bp_systolic}/{bp_diastolic} mmHg). Monitor closely."
        )
        nutrition_keys.append("high_bp")


    # ══════════════════════════════════════
    # CHECK 2: BLOOD SUGAR
    # ══════════════════════════════════════

    if blood_sugar > 400:
        # Severe hyperglycemia
        level = LEVEL_RED
        reasons.append(
            f"⚠️ Blood sugar is critically HIGH ({blood_sugar} mg/dL). "
            f"Risk of diabetic ketoacidosis — urgent care needed."
        )
        nutrition_keys.append("high_sugar")

    elif blood_sugar > 300:
        # High hyperglycemia
        level = LEVEL_RED
        reasons.append(
            f"⚠️ Blood sugar is very HIGH ({blood_sugar} mg/dL). "
            f"Risk of diabetic emergency."
        )
        nutrition_keys.append("high_sugar")

    elif blood_sugar < 50:
        # Severe hypoglycemia
        level = LEVEL_RED
        reasons.append(
            f"⚠️ Blood sugar is critically LOW ({blood_sugar} mg/dL). "
            f"Severe hypoglycemia — give sugar immediately."
        )

    elif blood_sugar < 70:
        # Mild hypoglycemia
        level = _escalate(level, LEVEL_YELLOW)
        reasons.append(
            f"🔶 Blood sugar is LOW ({blood_sugar} mg/dL). "
            f"Risk of hypoglycemia — take a sweet drink or snack."
        )

    elif blood_sugar > 250:
        # Moderately high
        level = _escalate(level, LEVEL_YELLOW)
        reasons.append(
            f"🔶 Blood sugar is high ({blood_sugar} mg/dL). "
            f"Consider adjusting diet or medication."
        )
        nutrition_keys.append("high_sugar")

    elif blood_sugar > 180:
        # Post-meal range, but worth noting
        level = _escalate(level, LEVEL_YELLOW)
        reasons.append(
            f"🔶 Blood sugar is slightly elevated ({blood_sugar} mg/dL). "
            f"Monitor and reduce sugar intake."
        )
        nutrition_keys.append("high_sugar")


    # ══════════════════════════════════════
    # CHECK 3: BODY TEMPERATURE
    # ══════════════════════════════════════

    if temperature >= 40.5:
        # Extreme fever — medical emergency
        level = LEVEL_RED
        reasons.append(
            f"⚠️ Temperature is dangerously HIGH ({temperature}°C). "
            f"Risk of febrile seizure or organ damage."
        )
        nutrition_keys.append("fever_respiratory")

    elif temperature >= 39.5:
        # High fever — serious, especially with other symptoms
        level = LEVEL_RED
        reasons.append(
            f"⚠️ Very high fever ({temperature}°C). Needs urgent attention."
        )
        nutrition_keys.append("fever_respiratory")

    elif temperature >= 39.0:
        # High fever — escalate if respiratory symptoms present
        if _has_respiratory_symptoms(symptoms) or "chest_pain" in symptoms:
            level = LEVEL_RED
            reasons.append(
                f"⚠️ High fever ({temperature}°C) combined with "
                f"respiratory/chest symptoms — serious concern."
            )
        else:
            level = _escalate(level, LEVEL_YELLOW)
            reasons.append(
                f"🔶 Significant fever ({temperature}°C). "
                f"Monitor closely and increase fluids."
            )
        nutrition_keys.append("fever_respiratory")

    elif temperature >= 37.5:
        # Mild fever
        level = _escalate(level, LEVEL_YELLOW)
        reasons.append(
            f"🔶 Mild fever ({temperature}°C). Rest and drink warm fluids."
        )
        nutrition_keys.append("fever_respiratory")

    elif temperature < 35.5:
        # Hypothermia
        level = LEVEL_RED
        reasons.append(
            f"⚠️ Temperature is too LOW ({temperature}°C). "
            f"Risk of hypothermia — warm the patient immediately."
        )


    # ══════════════════════════════════════
    # CHECK 4: SYMPTOMS
    # ══════════════════════════════════════

    # Chest Pain → always RED (possible cardiac event)
    if "chest_pain" in symptoms:
        level = LEVEL_RED
        reasons.append(
            "⚠️ Chest pain reported. This could indicate a cardiac event. "
            "Immediate medical attention is essential."
        )

    # Breathlessness → RED
    if "breathlessness" in symptoms:
        level = LEVEL_RED
        if khareef_mode:
            reasons.append(
                "⚠️ Breathlessness during Khareef season is very serious. "
                "High humidity worsens respiratory conditions for elderly patients."
            )
        else:
            reasons.append(
                "⚠️ Severe breathlessness reported. "
                "Urgent medical assessment is required immediately."
            )
        nutrition_keys.append("fever_respiratory")

    # Cough — Khareef + elderly = higher risk
    if "cough" in symptoms:
        if khareef_mode and age >= 60:
            level = _escalate(level, LEVEL_YELLOW)
            reasons.append(
                "🔶 Cough in an elderly patient during Khareef season. "
                "Monsoon humidity increases respiratory infection risk."
            )
        elif level == LEVEL_GREEN:
            # Only note cough if everything else is fine
            reasons.append(
                "ℹ️ Cough noted. Keep warm, drink warm fluids, and monitor."
            )

    # Dizziness → YELLOW (can indicate BP issues, dehydration)
    if "dizziness" in symptoms:
        level = _escalate(level, LEVEL_YELLOW)
        reasons.append(
            "🔶 Dizziness may be related to blood pressure changes, "
            "dehydration, or medication side effects."
        )

    # Fatigue in elderly → YELLOW
    if "fatigue" in symptoms and age >= 60:
        level = _escalate(level, LEVEL_YELLOW)
        reasons.append(
            "🔶 Fatigue in an elderly patient may indicate an underlying "
            "condition. Further assessment recommended."
        )

    # Headache with high BP → more serious
    if "headache" in symptoms and bp_systolic >= 160:
        level = _escalate(level, LEVEL_YELLOW)
        reasons.append(
            "🔶 Headache combined with elevated blood pressure — "
            "can indicate hypertensive urgency."
        )


    # ══════════════════════════════════════
    # CHECK 5: AGE-BASED ESCALATION
    # ══════════════════════════════════════

    if age >= 75 and level == LEVEL_YELLOW:
        reasons.append(
            "🔶 Age 75+ — elderly patients need earlier medical attention. "
            "Do not wait; consult a doctor today."
        )


    # ══════════════════════════════════════
    # DEFAULT GREEN MESSAGE
    # If nothing was flagged, show reassurance
    # ══════════════════════════════════════

    if level == LEVEL_GREEN and not reasons:
        reasons.append(
            "✅ All vitals are within normal range and no serious "
            "symptoms were reported. Well done!"
        )


    # ══════════════════════════════════════
    # ADD GENERAL ELDERLY NUTRITION
    # Always show for patients 60+
    # ══════════════════════════════════════

    if age >= 60 and "general_elderly" not in nutrition_keys:
        nutrition_keys.append("general_elderly")


    # ══════════════════════════════════════
    # BUILD STATIC FALLBACK ADVICE
    # This is used if Gemini AI is unavailable
    # ══════════════════════════════════════

    rule_advice_en, rule_advice_ar = _build_fallback_advice(level, age, khareef_mode)


    # ══════════════════════════════════════
    # COLLECT NUTRITION TIPS
    # ══════════════════════════════════════

    nutrition = _gather_nutrition(nutrition_keys)


    # ══════════════════════════════════════
    # RETURN THE COMPLETE RESULT
    # ══════════════════════════════════════

    return {
        "level":           level,
        "reasons":         reasons,
        "rule_advice_en":  rule_advice_en,   # Fallback: rule-based English advice
        "rule_advice_ar":  rule_advice_ar,   # Fallback: rule-based Arabic advice
        "nutrition":       nutrition,
        "emoji":           _level_emoji(level),
        "color":           _level_color(level),
    }


# ────────────────────────────────────────────
# HELPER FUNCTIONS
# Small utilities used inside assess_patient()
# ────────────────────────────────────────────

def _escalate(current: str, new_level: str) -> str:
    """
    Upgrades the triage level if the new one is more severe.
    RED > YELLOW > GREEN — severity never goes back down.
    """
    priority = {LEVEL_GREEN: 0, LEVEL_YELLOW: 1, LEVEL_RED: 2}
    return new_level if priority[new_level] > priority[current] else current


def _has_respiratory_symptoms(symptoms: List[str]) -> bool:
    """Checks if any breathing-related symptoms are present."""
    respiratory = {"cough", "breathlessness"}
    return bool(respiratory.intersection(set(symptoms)))


def _level_emoji(level: str) -> str:
    """Returns a coloured circle emoji for the triage level."""
    return {LEVEL_GREEN: "🟢", LEVEL_YELLOW: "🟡", LEVEL_RED: "🔴"}.get(level, "⚪")


def _level_color(level: str) -> str:
    """Returns a hex color for styling."""
    return {LEVEL_GREEN: "#16a34a", LEVEL_YELLOW: "#d97706", LEVEL_RED: "#dc2626"}.get(level, "#6b7280")


def _build_fallback_advice(level: str, age: int, khareef_mode: bool) -> tuple:
    """
    Returns simple (English, Arabic) advice text.
    Used when Gemini AI is not available.
    """
    elderly = " Because you are older, please do not delay — see a doctor soon." if age >= 65 else ""
    khareef = " Note: Khareef season humidity can worsen respiratory symptoms." if khareef_mode else ""

    if level == LEVEL_GREEN:
        en = (
            "✅ Good news! Your health readings look normal today.\n\n"
            "Continue your regular medications, drink plenty of water, "
            "eat balanced meals, and rest properly.\n\n"
            "Check again daily and come back if anything changes."
            + khareef
        )
        ar = (
            "✅ أخبار سارة! قراءات صحتك تبدو طبيعية اليوم.\n\n"
            "واصل تناول أدويتك المعتادة، واشرب الماء بكثرة، "
            "وتناول وجبات متوازنة وارتح جيداً.\n\n"
            "تحقق يومياً وعد إذا تغير أي شيء."
        )
    elif level == LEVEL_YELLOW:
        en = (
            "🔶 Some of your readings need attention.\n\n"
            "Please contact your family doctor or visit the nearest health centre soon.\n\n"
            "Take all medications on time, rest well, and avoid physical strain."
            + elderly + khareef
        )
        ar = (
            "🔶 بعض قراءاتك تحتاج إلى انتباه.\n\n"
            "يرجى التواصل مع طبيبك الأسري أو زيارة أقرب مركز صحي قريباً.\n\n"
            "تناول جميع أدويتك في الوقت المحدد، وارتح جيداً، وتجنب المجهود الجسدي."
        )
    else:  # RED
        en = (
            "🚨 URGENT — Please seek medical help NOW.\n\n"
            "Your readings indicate a potentially serious condition.\n\n"
            "Go immediately to:\n"
            "🏥 Sultan Qaboos Hospital – Salalah\n"
            "📍 Al Dahariz, Salalah, Dhofar\n"
            "📞 Emergency: 999  |  Hospital: +968 23 218 000\n\n"
            "Do NOT drive yourself. Call a family member or ambulance."
            + elderly
        )
        ar = (
            "🚨 عاجل — يرجى طلب المساعدة الطبية الآن.\n\n"
            "تشير قراءاتك إلى حالة قد تكون خطيرة.\n\n"
            "توجه فوراً إلى:\n"
            "🏥 مستشفى السلطان قابوس – صلالة\n"
            "📍 الدهاريز، صلالة، ظفار\n"
            "📞 الطوارئ: 999  |  المستشفى: 23218000 968+\n\n"
            "لا تقُد السيارة بنفسك. اتصل بأحد أفراد الأسرة أو سيارة الإسعاف."
        )
    return en, ar


def _gather_nutrition(keys: List[str]) -> List[str]:
    """Collects all unique nutrition tips for the given condition keys."""
    tips = []
    seen = set()
    for key in keys:
        for tip in NUTRITION_TIPS.get(key, []):
            if tip not in seen:
                tips.append(tip)
                seen.add(tip)
    return tips