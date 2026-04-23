"""
diseases.py – Disease Encyclopedia
Complete information for each disease in a structured format.
Used by the Disease Encyclopedia tab in main.py
"""

DISEASES = {

    # ══════════════════════════════════════
    # INFECTIOUS DISEASES
    # ══════════════════════════════════════

    "COVID-19": {
        "emoji": "🦠",
        "category": "Infectious",
        "also_known_as": "Coronavirus, SARS-CoV-2",
        "arabic_name": "كوفيد-19 / فيروس كورونا",
        "overview": (
            "COVID-19 is an infectious disease caused by the SARS-CoV-2 coronavirus. "
            "It was first identified in Wuhan, China in December 2019 and became a "
            "global pandemic in 2020. It primarily affects the respiratory system."
        ),
        "how_it_occurs": "Viral infection — NOT genetic",
        "transmission": [
            "🌬️ Airborne droplets when an infected person coughs, sneezes, or speaks",
            "👋 Touching contaminated surfaces then touching face",
            "👥 Close contact with infected person (within 1–2 metres)",
            "🏠 Poorly ventilated indoor spaces are highest risk",
        ],
        "symptoms": [
            "🌡️ Fever or chills",
            "😮‍💨 Shortness of breath or difficulty breathing",
            "😮 Dry cough",
            "😴 Fatigue and body aches",
            "🤧 Loss of taste or smell",
            "🤕 Headache",
            "🤢 Nausea, vomiting, diarrhoea",
            "🔴 Severe: breathing difficulty, chest pain, confusion",
        ],
        "high_risk_groups": [
            "👴 Elderly — especially 65+",
            "🫀 Heart disease or high blood pressure",
            "🫁 Asthma or COPD",
            "🩸 Diabetes",
            "⚖️ Obesity",
            "🛡️ Weakened immune system",
            "🤰 Pregnant women",
        ],
        "prevention": [
            "💉 Vaccination — most effective prevention",
            "😷 Wear mask in crowded indoor spaces",
            "🧼 Wash hands frequently for 20 seconds",
            "📏 Maintain 2-metre distance from sick people",
            "🌬️ Open windows — improve ventilation",
            "🏠 Stay home if you feel unwell",
            "🤧 Cover cough and sneezes with elbow",
        ],
        "treatment": [
            "🛏️ Rest and stay hydrated",
            "💊 Paracetamol for fever and pain",
            "🏥 Antivirals (Paxlovid) for high-risk patients — prescribed by doctor",
            "💧 Drink plenty of fluids",
            "🚨 Seek emergency care if: breathing difficulty, chest pain, confusion",
        ],
        "when_to_seek_help": [
            "Difficulty breathing or shortness of breath",
            "Persistent chest pain or pressure",
            "Confusion or inability to stay awake",
            "Bluish lips or face",
            "Oxygen level below 94%",
        ],
        "is_genetic": False,
        "is_contagious": True,
        "recovery_time": "Mild: 1–2 weeks. Severe: several weeks or more.",
        "khareef_connection": "During Khareef season, humidity and fog can worsen respiratory COVID symptoms.",
    },

    "Influenza (Flu)": {
        "emoji": "🤧",
        "category": "Infectious",
        "also_known_as": "Flu, Seasonal Influenza",
        "arabic_name": "الإنفلونزا / النزلة الوافدة",
        "overview": (
            "Influenza is a contagious respiratory illness caused by influenza viruses. "
            "It can cause mild to severe illness and sometimes leads to death. "
            "Seasonal flu affects millions every year, especially in winter."
        ),
        "how_it_occurs": "Viral infection — NOT genetic",
        "transmission": [
            "🌬️ Respiratory droplets when infected person coughs or sneezes",
            "👋 Touching contaminated surfaces then touching eyes, nose, or mouth",
            "👥 Close contact with infected people",
        ],
        "symptoms": [
            "🌡️ Sudden high fever (38–40°C)",
            "🤕 Severe headache",
            "💪 Body aches and muscle pain",
            "😴 Extreme fatigue",
            "😮 Dry cough",
            "🤧 Runny or stuffy nose",
            "🤢 Nausea and vomiting (more common in children)",
        ],
        "high_risk_groups": [
            "👶 Children under 5",
            "👴 Adults over 65",
            "🤰 Pregnant women",
            "🛡️ People with weak immune systems",
            "🫀 Heart disease patients",
            "🫁 Asthma patients",
            "🩸 Diabetics",
        ],
        "prevention": [
            "💉 Annual flu vaccine — most effective",
            "🧼 Frequent handwashing",
            "😷 Wear mask when sick",
            "🏠 Stay home when unwell",
            "🤧 Cover cough with elbow",
            "💪 Boost immunity: sleep well, eat well, exercise",
        ],
        "treatment": [
            "🛏️ Rest at home",
            "💊 Paracetamol for fever and aches",
            "💧 Drink plenty of fluids",
            "🧄 Warm soups, ginger tea, honey-lemon",
            "💊 Antivirals (oseltamivir/Tamiflu) if high risk — needs prescription",
            "🚨 Hospital if: breathing difficulty, very high fever, confusion",
        ],
        "when_to_seek_help": [
            "Difficulty breathing",
            "Fever above 40°C",
            "Severe chest pain",
            "Confusion or altered consciousness",
            "Symptoms improving then suddenly worsening",
        ],
        "is_genetic": False,
        "is_contagious": True,
        "recovery_time": "5–7 days. Fatigue may last 2 weeks.",
        "khareef_connection": "Khareef humidity can trigger flu-like respiratory symptoms.",
    },

    "Pneumonia": {
        "emoji": "🫁",
        "category": "Infectious",
        "also_known_as": "Lung infection, Chest infection",
        "arabic_name": "الالتهاب الرئوي",
        "overview": (
            "Pneumonia is an infection that inflames the air sacs in one or both lungs. "
            "The air sacs may fill with fluid or pus, causing cough, fever, chills, and "
            "difficulty breathing. It can range from mild to life-threatening."
        ),
        "how_it_occurs": "Bacterial, viral, or fungal infection — NOT genetic",
        "transmission": [
            "🌬️ Breathing in bacteria or viruses in the air",
            "👥 Close contact with infected persons",
            "🦠 Can develop as a complication of flu or COVID-19",
            "💧 Aspiration (inhaling food or liquids into lungs)",
        ],
        "symptoms": [
            "😮 Cough with phlegm (yellow, green, or bloody)",
            "😤 Shortness of breath",
            "🌡️ High fever with sweating and chills",
            "💔 Chest pain when breathing or coughing",
            "😴 Fatigue and weakness",
            "🤢 Nausea, vomiting, diarrhoea",
            "🔵 Bluish lips or fingernails (severe — emergency)",
        ],
        "high_risk_groups": [
            "👶 Infants under 2 years",
            "👴 Adults over 65",
            "🛡️ Weakened immune system",
            "🫁 Asthma or COPD",
            "🩸 Diabetes",
            "🚬 Smokers",
            "🏥 Recently hospitalised patients",
        ],
        "prevention": [
            "💉 Pneumococcal vaccine — recommended for elderly and high risk",
            "💉 Flu vaccine — prevents flu-related pneumonia",
            "🚭 Stop smoking",
            "🧼 Regular handwashing",
            "😷 Mask in crowded places",
            "💪 Maintain good overall health",
        ],
        "treatment": [
            "💊 Antibiotics for bacterial pneumonia — prescribed by doctor",
            "🛏️ Rest",
            "💧 Plenty of fluids",
            "💊 Paracetamol for fever",
            "🏥 Hospital needed if: severe breathing difficulty, low oxygen, confusion",
        ],
        "when_to_seek_help": [
            "Difficulty breathing or rapid breathing",
            "Chest pain",
            "High fever above 39.5°C",
            "Blue or grey lips/fingernails",
            "Confusion",
            "Coughing blood",
        ],
        "is_genetic": False,
        "is_contagious": True,
        "recovery_time": "Mild: 1–3 weeks. Severe: several weeks.",
        "khareef_connection": "High risk during Khareef — humidity promotes bacterial growth. Elderly especially vulnerable.",
    },

    # ══════════════════════════════════════
    # CHRONIC / LIFESTYLE DISEASES
    # ══════════════════════════════════════

    "Type 2 Diabetes": {
        "emoji": "🩸",
        "category": "Chronic / Lifestyle",
        "also_known_as": "Diabetes mellitus, Sugar disease",
        "arabic_name": "السكري من النوع الثاني / مرض السكر",
        "overview": (
            "Type 2 diabetes is a chronic condition affecting how the body processes "
            "blood sugar (glucose). The body either doesn't produce enough insulin or "
            "doesn't use it effectively. It is one of the most common diseases in Oman."
        ),
        "how_it_occurs": "Combination of genetic and lifestyle factors",
        "transmission": [
            "❌ Not contagious — cannot spread from person to person",
            "🧬 Genetic: family history increases risk",
            "🍔 Lifestyle: poor diet, physical inactivity, obesity are major causes",
        ],
        "symptoms": [
            "💧 Excessive thirst and frequent urination",
            "😴 Extreme fatigue",
            "👁️ Blurred vision",
            "🩹 Slow-healing wounds",
            "🦶 Tingling or numbness in hands/feet",
            "⚖️ Unexplained weight loss",
            "🔁 Frequent infections",
        ],
        "high_risk_groups": [
            "⚖️ Overweight or obese",
            "👴 Age 45+",
            "👨‍👩‍👧 Family history of diabetes",
            "🏃 Physically inactive",
            "🤰 History of gestational diabetes",
            "🩸 Prediabetes",
            "🫀 High blood pressure",
        ],
        "prevention": [
            "🥗 Healthy diet — reduce sugar, white rice, processed foods",
            "🏃 Exercise 30 minutes daily — walking is excellent",
            "⚖️ Maintain healthy weight",
            "💧 Drink water instead of sugary drinks",
            "🔬 Regular blood sugar checks",
            "🚭 Stop smoking",
            "😴 Get adequate sleep",
        ],
        "treatment": [
            "💊 Metformin — first-line medication",
            "💉 Insulin injections — if tablets not enough",
            "🥗 Strict dietary changes",
            "🏃 Regular physical exercise",
            "🔬 Daily blood sugar monitoring",
            "👁️ Regular eye, kidney, and foot checks",
            "👨‍⚕️ Regular doctor appointments",
        ],
        "when_to_seek_help": [
            "Blood sugar above 300 mg/dL",
            "Blood sugar below 70 mg/dL with symptoms",
            "Sudden confusion or loss of consciousness",
            "Fruity smell on breath (diabetic ketoacidosis)",
            "Non-healing wound or infection",
            "Chest pain with diabetes",
        ],
        "is_genetic": True,
        "is_contagious": False,
        "recovery_time": "Chronic — managed with lifestyle and medication, not cured.",
        "khareef_connection": "Dehydration during Khareef can affect blood sugar levels. Monitor more frequently.",
    },

    "High Blood Pressure": {
        "emoji": "🫀",
        "category": "Chronic / Lifestyle",
        "also_known_as": "Hypertension, Silent killer",
        "arabic_name": "ارتفاع ضغط الدم",
        "overview": (
            "High blood pressure (hypertension) is a condition where blood pushes against "
            "artery walls with too much force. It often has no symptoms but can lead to "
            "heart attack, stroke, and kidney damage if untreated. Extremely common in Oman."
        ),
        "how_it_occurs": "Combination of genetic and lifestyle factors",
        "transmission": [
            "❌ Not contagious",
            "🧬 Genetic: runs strongly in families",
            "🍔 Lifestyle: high salt diet, obesity, stress, smoking, alcohol",
            "🕐 Age: risk increases significantly after 40",
        ],
        "symptoms": [
            "😶 Usually NO symptoms — that's why it's called 'silent killer'",
            "🤕 Severe headache (in very high BP)",
            "😵 Dizziness",
            "👁️ Blurred vision",
            "🫀 Chest pain",
            "😤 Shortness of breath",
            "🩸 Nosebleed (rare, with very high BP)",
        ],
        "high_risk_groups": [
            "👴 Age 60+",
            "👨‍👩‍👧 Family history of hypertension",
            "⚖️ Overweight or obese",
            "🍔 High salt diet",
            "🚬 Smokers",
            "🩸 Diabetics",
            "😤 Chronic stress",
            "🏃 Sedentary lifestyle",
        ],
        "prevention": [
            "🧂 Reduce salt — less than 5g (1 teaspoon) per day",
            "🥗 DASH diet: fruits, vegetables, whole grains, low-fat dairy",
            "🏃 Exercise 30 minutes most days",
            "⚖️ Maintain healthy weight",
            "🚭 Stop smoking",
            "🍺 Limit or avoid alcohol",
            "😌 Manage stress — meditation, relaxation",
            "🔬 Regular BP checks",
        ],
        "treatment": [
            "💊 Amlodipine, lisinopril, or other prescribed medications",
            "🧂 Low-salt diet",
            "🏃 Regular exercise",
            "🔬 Daily home BP monitoring",
            "😴 Adequate sleep",
            "⚖️ Weight loss if overweight",
        ],
        "when_to_seek_help": [
            "BP above 180/120 — hypertensive crisis",
            "Severe headache with high BP",
            "Chest pain or heart pounding",
            "Difficulty breathing",
            "Vision problems",
            "Numbness in face or arms",
        ],
        "is_genetic": True,
        "is_contagious": False,
        "recovery_time": "Chronic — controlled with medication and lifestyle, not cured.",
        "khareef_connection": "Physical exertion in Khareef heat and humidity can cause BP spikes.",
    },

    "Asthma": {
        "emoji": "😤",
        "category": "Chronic / Respiratory",
        "also_known_as": "Bronchial asthma",
        "arabic_name": "الربو / الأزيز",
        "overview": (
            "Asthma is a chronic disease where the airways narrow and swell, producing "
            "extra mucus. This makes breathing difficult and triggers coughing, wheezing, "
            "and shortness of breath. Salalah's Khareef season is a major trigger."
        ),
        "how_it_occurs": "Genetic + environmental triggers",
        "transmission": [
            "❌ Not contagious",
            "🧬 Genetic: strong family tendency",
            "🌿 Triggered by: dust, pollen, mold, animal fur",
            "🌫️ Triggered by: air pollution, smoke, Khareef fog",
            "🦠 Triggered by: respiratory infections, cold air",
            "💊 Triggered by: aspirin, ibuprofen in some people",
        ],
        "symptoms": [
            "😤 Shortness of breath",
            "😮 Wheezing (whistling sound when breathing)",
            "😮 Cough — especially at night or early morning",
            "💔 Chest tightness",
            "🔴 Severe attack: cannot speak, lips turning blue",
        ],
        "high_risk_groups": [
            "👶 Children — asthma is most common in children",
            "👨‍👩‍👧 Family history of asthma or allergies",
            "🚬 Smokers or exposed to secondhand smoke",
            "⚖️ Obese individuals",
            "🌿 Allergy sufferers",
            "🌫️ People in polluted or humid environments",
        ],
        "prevention": [
            "🏠 Keep home dust-free — vacuum regularly",
            "🐾 Avoid pets if allergic",
            "🚭 Avoid smoke — active and passive",
            "😷 Wear mask during Khareef fog",
            "💊 Take preventer inhaler daily as prescribed",
            "🌡️ Use air conditioning — filter air",
            "🤧 Treat respiratory infections early",
        ],
        "treatment": [
            "💨 Salbutamol (Ventolin) reliever inhaler — for immediate relief",
            "💊 Steroid preventer inhaler — daily to prevent attacks",
            "💊 Montelukast tablets — for allergy-triggered asthma",
            "😤 Breathing exercises (Buteyko method)",
            "🏥 Nebuliser for severe attacks",
            "🚨 Emergency steroids for severe attacks",
        ],
        "when_to_seek_help": [
            "Reliever inhaler not working",
            "Cannot speak full sentences",
            "Lips or fingernails turning blue",
            "Breathing very fast with neck muscles straining",
            "Oxygen level below 92%",
        ],
        "is_genetic": True,
        "is_contagious": False,
        "recovery_time": "Chronic — managed well with inhalers. Can worsen in Khareef.",
        "khareef_connection": "🌦️ HIGH RISK — Khareef humidity and mold spores are major asthma triggers in Salalah.",
    },

    "Heart Disease": {
        "emoji": "❤️",
        "category": "Chronic / Cardiovascular",
        "also_known_as": "Coronary artery disease, Ischaemic heart disease",
        "arabic_name": "أمراض القلب / مرض الشريان التاجي",
        "overview": (
            "Heart disease refers to conditions affecting the heart's structure and function. "
            "The most common type is coronary artery disease — where arteries supplying the "
            "heart become narrowed or blocked, potentially causing a heart attack."
        ),
        "how_it_occurs": "Combination of genetic and lifestyle factors",
        "transmission": [
            "❌ Not contagious",
            "🧬 Genetic: family history is a major risk factor",
            "🍔 Lifestyle: fatty diet, smoking, physical inactivity",
            "🩸 Associated conditions: diabetes, hypertension, high cholesterol",
        ],
        "symptoms": [
            "💔 Chest pain or pressure (angina)",
            "💪 Pain radiating to left arm, jaw, or shoulder",
            "😤 Shortness of breath",
            "😵 Dizziness or light-headedness",
            "😰 Cold sweats",
            "💓 Irregular heartbeat (palpitations)",
            "😴 Unusual fatigue",
        ],
        "high_risk_groups": [
            "👴 Men over 45, women over 55",
            "👨‍👩‍👧 Family history of heart disease",
            "🚬 Smokers",
            "🩸 Diabetics",
            "🫀 High blood pressure",
            "🧈 High cholesterol",
            "⚖️ Obesity",
            "😤 Chronic stress",
        ],
        "prevention": [
            "🚭 Stop smoking — single most important change",
            "🥗 Heart-healthy diet: less fat, more vegetables",
            "🏃 Exercise 150 minutes per week",
            "⚖️ Maintain healthy weight",
            "🔬 Control blood pressure, sugar, cholesterol",
            "😌 Manage stress",
            "💊 Take prescribed medications consistently",
        ],
        "treatment": [
            "💊 Aspirin — prevents blood clots",
            "💊 Statins — lower cholesterol",
            "💊 Beta-blockers — reduce heart workload",
            "💊 ACE inhibitors — lower blood pressure",
            "🏥 Angioplasty or stent — open blocked arteries",
            "🏥 Bypass surgery — severe cases",
        ],
        "when_to_seek_help": [
            "Chest pain lasting more than 15 minutes",
            "Pain spreading to arm, jaw, or shoulder",
            "Sudden shortness of breath",
            "Loss of consciousness",
            "Heart pounding or very irregular heartbeat",
        ],
        "is_genetic": True,
        "is_contagious": False,
        "recovery_time": "Chronic — managed with medication and lifestyle changes.",
        "khareef_connection": "Physical exertion in Khareef heat stresses the heart. Stay cool and avoid overexertion.",
    },

    "Stroke": {
        "emoji": "🧠",
        "category": "Neurological / Emergency",
        "also_known_as": "Brain attack, CVA (Cerebrovascular accident)",
        "arabic_name": "السكتة الدماغية",
        "overview": (
            "A stroke occurs when blood supply to part of the brain is cut off. "
            "Brain cells begin dying within minutes. Stroke is a medical emergency. "
            "Fast treatment can prevent death and disability. Remember FAST: "
            "Face drooping, Arm weakness, Speech difficulty, Time to call 999."
        ),
        "how_it_occurs": "Blocked or ruptured blood vessel in the brain",
        "transmission": [
            "❌ Not contagious",
            "🧬 Genetic: family history increases risk",
            "🩸 Main causes: blood clot, burst blood vessel, high blood pressure",
        ],
        "symptoms": [
            "😐 Face drooping — one side of face droops or is numb",
            "💪 Arm weakness — one arm is weak or numb, drifts downward",
            "🗣️ Speech difficulty — slurred, strange, or unable to speak",
            "👁️ Sudden vision problems",
            "🤕 Sudden severe headache with no known cause",
            "😵 Sudden confusion",
            "🦶 Sudden trouble walking or loss of balance",
        ],
        "high_risk_groups": [
            "👴 Age 55+",
            "🫀 High blood pressure — biggest risk factor",
            "🚬 Smokers",
            "🩸 Diabetics",
            "🧈 High cholesterol",
            "💓 Atrial fibrillation (irregular heart rhythm)",
            "👨‍👩‍👧 Family history of stroke",
        ],
        "prevention": [
            "🩺 Control blood pressure — most important",
            "🚭 Stop smoking",
            "🏃 Regular exercise",
            "🥗 Healthy diet — less salt, more vegetables",
            "💊 Take blood pressure and diabetes medications",
            "🍺 Limit alcohol",
            "🔬 Treat atrial fibrillation if diagnosed",
        ],
        "treatment": [
            "🚨 CALL 999 IMMEDIATELY — every minute counts",
            "🏥 Clot-dissolving drugs (tPA) within 4.5 hours",
            "🏥 Mechanical thrombectomy to remove clot",
            "🏥 Surgery for bleeding stroke",
            "🔄 Rehabilitation: speech, physiotherapy, occupational therapy",
        ],
        "when_to_seek_help": [
            "ANY of the FAST symptoms — call 999 immediately",
            "Sudden severe headache unlike any before",
            "Sudden loss of vision",
            "Sudden confusion or difficulty understanding speech",
            "Do NOT wait — every minute brain cells die",
        ],
        "is_genetic": True,
        "is_contagious": False,
        "recovery_time": "Varies from weeks to years depending on severity. Some permanent disability possible.",
        "khareef_connection": "Dehydration in Khareef heat thickens blood, increasing clot risk.",
    },

    "Kidney Disease": {
        "emoji": "🫘",
        "category": "Chronic",
        "also_known_as": "Chronic Kidney Disease (CKD), Renal failure",
        "arabic_name": "مرض الكلى المزمن / الفشل الكلوي",
        "overview": (
            "Chronic kidney disease involves gradual loss of kidney function. The kidneys "
            "filter waste and excess fluids from blood. When kidneys fail, dangerous levels "
            "of fluid, electrolytes, and wastes build up. Very common in diabetics and "
            "people with high blood pressure in Oman."
        ),
        "how_it_occurs": "Usually caused by diabetes or high blood pressure over many years",
        "transmission": [
            "❌ Not contagious",
            "🧬 Genetic forms exist (polycystic kidney disease)",
            "🩸 Main causes: uncontrolled diabetes, high blood pressure",
            "💊 Overuse of certain painkillers (NSAIDs)",
        ],
        "symptoms": [
            "😴 Fatigue and weakness",
            "💧 Decreased urine output or changes in urine",
            "🦵 Swollen ankles and feet",
            "😤 Shortness of breath",
            "🤢 Nausea and vomiting",
            "🤕 Headaches",
            "😮 Difficulty concentrating",
            "😮 Itchy skin",
        ],
        "high_risk_groups": [
            "🩸 Diabetics — most common cause",
            "🫀 High blood pressure patients",
            "👨‍👩‍👧 Family history of kidney disease",
            "👴 Adults over 60",
            "⚖️ Obese individuals",
            "🚬 Smokers",
        ],
        "prevention": [
            "🩸 Control blood sugar strictly",
            "🫀 Control blood pressure strictly",
            "💧 Drink adequate water daily",
            "🧂 Low-salt diet",
            "💊 Avoid excess painkillers (ibuprofen, diclofenac)",
            "🔬 Regular kidney function blood tests",
            "🚭 Stop smoking",
        ],
        "treatment": [
            "💊 Medications to control BP and sugar",
            "🥗 Special kidney diet — low potassium, low phosphate",
            "💧 Careful fluid management",
            "🏥 Dialysis — when kidneys fail significantly",
            "🏥 Kidney transplant — for end-stage kidney disease",
        ],
        "when_to_seek_help": [
            "Sudden decrease in urination",
            "Severe swelling in legs or face",
            "Difficulty breathing",
            "Confusion or extreme fatigue",
            "Blood in urine",
        ],
        "is_genetic": True,
        "is_contagious": False,
        "recovery_time": "Chronic — progressive if untreated. Can be slowed with treatment.",
        "khareef_connection": "Dehydration in Khareef worsens kidney disease. Increase water intake.",
    },

    "Arthritis": {
        "emoji": "🦴",
        "category": "Chronic / Musculoskeletal",
        "also_known_as": "Joint disease, Rheumatoid arthritis, Osteoarthritis",
        "arabic_name": "التهاب المفاصل",
        "overview": (
            "Arthritis refers to inflammation of the joints. There are over 100 types. "
            "The most common are osteoarthritis (wear and tear) and rheumatoid arthritis "
            "(autoimmune). Both cause joint pain, stiffness, and reduced mobility. "
            "More common in elderly and women."
        ),
        "how_it_occurs": "Genetic, autoimmune, and mechanical wear",
        "transmission": [
            "❌ Not contagious",
            "🧬 Genetic: rheumatoid arthritis has strong genetic component",
            "⏳ Osteoarthritis: wear and tear over years",
            "🤕 Previous joint injury increases risk",
        ],
        "symptoms": [
            "🦴 Joint pain — constant or intermittent",
            "🦴 Joint stiffness — especially in morning",
            "🔴 Swollen, red, warm joints",
            "🏃 Reduced range of motion",
            "😴 Fatigue",
            "⚖️ Unintended weight loss (rheumatoid type)",
        ],
        "high_risk_groups": [
            "👴 Adults over 50",
            "👩 Women — especially for rheumatoid arthritis",
            "👨‍👩‍👧 Family history of arthritis",
            "⚖️ Overweight — extra strain on joints",
            "🤕 Previous joint injuries",
            "🏭 Jobs involving repetitive movements",
        ],
        "prevention": [
            "⚖️ Maintain healthy weight — reduces knee and hip strain",
            "🏃 Regular low-impact exercise: swimming, cycling, walking",
            "🥗 Anti-inflammatory diet: fish, olive oil, berries",
            "🤕 Protect joints during exercise and work",
            "🔬 Early diagnosis and treatment",
        ],
        "treatment": [
            "💊 Paracetamol or NSAIDs for pain",
            "💊 Disease-modifying drugs for rheumatoid (methotrexate)",
            "💉 Corticosteroid injections",
            "🏃 Physiotherapy and exercise",
            "🏥 Joint replacement surgery for severe cases",
            "🌡️ Hot and cold compresses",
        ],
        "when_to_seek_help": [
            "Joint pain that does not improve with rest",
            "Severe swelling or redness of joint",
            "Sudden inability to move joint",
            "Fever with joint pain",
            "Joints affecting ability to work or walk",
        ],
        "is_genetic": True,
        "is_contagious": False,
        "recovery_time": "Chronic — managed with treatment. Symptoms can be significantly reduced.",
        "khareef_connection": "Khareef humidity and cold fog can worsen joint stiffness and pain.",
    },

    "Thyroid Disease": {
        "emoji": "🦋",
        "category": "Hormonal / Endocrine",
        "also_known_as": "Hypothyroidism, Hyperthyroidism, Thyroid disorder",
        "arabic_name": "أمراض الغدة الدرقية",
        "overview": (
            "The thyroid is a butterfly-shaped gland in the neck that produces hormones "
            "controlling metabolism. When it produces too little (hypothyroidism) or too "
            "much (hyperthyroidism), it affects almost every organ system. More common in women."
        ),
        "how_it_occurs": "Autoimmune, genetic, or iodine deficiency",
        "transmission": [
            "❌ Not contagious",
            "🧬 Genetic: strong family tendency",
            "🛡️ Autoimmune: immune system attacks thyroid",
            "🧂 Iodine: too little or too much iodine in diet",
        ],
        "symptoms": [
            "🥶 Hypothyroid (underactive): fatigue, weight gain, feeling cold, dry skin, constipation",
            "🥵 Hyperthyroid (overactive): weight loss, rapid heartbeat, anxiety, tremors, heat intolerance",
            "🦋 Enlarged thyroid gland (goitre) — visible swelling in neck",
            "💇 Hair loss",
            "😴 Fatigue (both types)",
        ],
        "high_risk_groups": [
            "👩 Women — 5–8x more common than men",
            "👴 Adults over 60",
            "👨‍👩‍👧 Family history of thyroid disease",
            "🛡️ History of autoimmune disease",
            "🤰 Pregnancy and postpartum period",
        ],
        "prevention": [
            "🧂 Adequate iodine: use iodised salt, eat seafood",
            "🔬 Regular thyroid screening for women over 35",
            "🔬 Test during and after pregnancy",
            "💊 Take thyroid medication consistently if prescribed",
        ],
        "treatment": [
            "💊 Levothyroxine (Synthroid) — for underactive thyroid",
            "💊 Anti-thyroid drugs (methimazole) — for overactive",
            "☢️ Radioactive iodine — treats overactive thyroid",
            "🏥 Surgery — for large goitre or cancer",
            "🔬 Regular TSH blood test monitoring",
        ],
        "when_to_seek_help": [
            "Racing heartbeat or palpitations",
            "Sudden unexplained weight change",
            "Visible swelling in neck",
            "Severe fatigue affecting daily life",
            "Extreme sensitivity to cold or heat",
        ],
        "is_genetic": True,
        "is_contagious": False,
        "recovery_time": "Chronic — well managed with daily medication.",
        "khareef_connection": "Temperature sensitivity from thyroid disease is worsened by Khareef humidity changes.",
    },

    "Anaemia": {
        "emoji": "💉",
        "category": "Blood / Haematological",
        "also_known_as": "Low haemoglobin, Iron deficiency anaemia",
        "arabic_name": "فقر الدم / الأنيميا",
        "overview": (
            "Anaemia is a condition where you don't have enough healthy red blood cells "
            "to carry adequate oxygen to your body's tissues. Iron deficiency is the most "
            "common cause. Very common in women, children, and pregnant women in Oman."
        ),
        "how_it_occurs": "Iron deficiency, vitamin deficiency, or inherited blood disorders",
        "transmission": [
            "❌ Not contagious",
            "🥩 Most common cause: lack of iron in diet",
            "🩸 Blood loss: heavy periods, internal bleeding",
            "🧬 Genetic forms: sickle cell, thalassaemia",
            "🛡️ Chronic disease: kidney disease, cancer can cause anaemia",
        ],
        "symptoms": [
            "😴 Extreme fatigue and weakness",
            "😶 Pale skin, lips, and inside eyelids",
            "💓 Fast or irregular heartbeat",
            "😤 Shortness of breath",
            "🤕 Dizziness or light-headedness",
            "❄️ Cold hands and feet",
            "🤕 Headaches",
            "🧊 Craving ice or unusual substances (pica)",
        ],
        "high_risk_groups": [
            "👩 Women of childbearing age",
            "🤰 Pregnant women",
            "👶 Infants and young children",
            "🌱 Vegetarians and vegans",
            "👴 Elderly adults",
            "🩸 People with heavy periods",
        ],
        "prevention": [
            "🥩 Eat iron-rich foods: red meat, chicken, lentils, spinach",
            "🍊 Vitamin C with iron: improves absorption (orange juice with food)",
            "🚫 Avoid tea/coffee with meals: reduces iron absorption",
            "💊 Iron supplements during pregnancy",
            "🔬 Regular blood count checks",
        ],
        "treatment": [
            "💊 Iron supplements: ferrous sulphate tablets",
            "🥩 Iron-rich diet",
            "💉 Iron infusions for severe cases",
            "🩸 Blood transfusion for very severe anaemia",
            "💊 Vitamin B12 or folate supplements if deficient",
        ],
        "when_to_seek_help": [
            "Extreme fatigue preventing daily activities",
            "Heart pounding or chest pain",
            "Difficulty breathing at rest",
            "Very pale appearance",
            "Fainting or near-fainting",
        ],
        "is_genetic": True,
        "is_contagious": False,
        "recovery_time": "Iron deficiency: 2–3 months of supplements. Genetic forms: lifelong management.",
        "khareef_connection": "Anaemia worsens exercise tolerance — take extra care during outdoor Khareef activities.",
    },

    "Dengue Fever": {
        "emoji": "🦟",
        "category": "Infectious / Vector-borne",
        "also_known_as": "Dengue, Breakbone fever",
        "arabic_name": "حمى الضنك",
        "overview": (
            "Dengue fever is a mosquito-borne viral disease common in tropical and "
            "subtropical regions including parts of Oman. It is transmitted by the "
            "Aedes mosquito. Severe dengue can be life-threatening."
        ),
        "how_it_occurs": "Viral infection spread by mosquito bite — NOT person to person",
        "transmission": [
            "🦟 Bite from infected Aedes mosquito",
            "❌ Does NOT spread person to person",
            "🦟 Mosquitoes breed in standing water",
            "🌅 Aedes mosquitoes bite mainly during daytime",
        ],
        "symptoms": [
            "🌡️ Sudden high fever (40°C)",
            "🤕 Severe headache",
            "👁️ Pain behind the eyes",
            "💪 Severe muscle and joint pain",
            "🤢 Nausea and vomiting",
            "🔴 Skin rash appearing 2–5 days after fever",
            "🩸 Severe dengue: bleeding, low blood pressure, organ failure",
        ],
        "high_risk_groups": [
            "🌍 People in tropical/subtropical areas",
            "🔁 People with previous dengue infection (higher risk of severe dengue)",
            "👶 Infants and young children",
            "👴 Elderly adults",
            "🛡️ People with weakened immunity",
        ],
        "prevention": [
            "🦟 Use mosquito repellent (DEET-based)",
            "🪟 Sleep under mosquito nets",
            "👕 Wear long sleeves and trousers",
            "💧 Eliminate standing water around home (flowerpots, tyres, containers)",
            "🪟 Install window and door screens",
            "🌅 Be extra careful during daytime (peak mosquito biting time)",
        ],
        "treatment": [
            "❌ No specific antiviral — treatment is supportive",
            "💧 Drink plenty of fluids — very important",
            "💊 Paracetamol for fever and pain",
            "🚫 NEVER take ibuprofen or aspirin — increases bleeding risk",
            "🏥 Hospital for severe dengue",
            "🩸 Platelet transfusion if severe",
        ],
        "when_to_seek_help": [
            "Severe abdominal pain",
            "Persistent vomiting",
            "Bleeding from nose or gums",
            "Blood in urine or vomit",
            "Rapid breathing",
            "Sudden drop in fever with severe weakness",
        ],
        "is_genetic": False,
        "is_contagious": False,
        "recovery_time": "Mild: 1–2 weeks. Severe dengue: weeks in hospital.",
        "khareef_connection": "🌦️ Khareef standing water creates breeding grounds for dengue mosquitoes. High alert during monsoon.",
    },

    "Depression": {
        "emoji": "🧠",
        "category": "Mental Health",
        "also_known_as": "Major depressive disorder, Clinical depression",
        "arabic_name": "الاكتئاب",
        "overview": (
            "Depression is a common and serious medical illness that negatively affects "
            "how you feel, think, and act. It is not weakness or laziness — it is a "
            "real medical condition that requires treatment. It is highly treatable."
        ),
        "how_it_occurs": "Combination of biological, genetic, and environmental factors",
        "transmission": [
            "❌ Not contagious",
            "🧬 Genetic: runs in families",
            "🧪 Brain chemistry: imbalance in neurotransmitters",
            "😔 Life events: trauma, loss, chronic stress",
            "💊 Can be side effect of certain medications",
        ],
        "symptoms": [
            "😔 Persistent sad or empty mood",
            "😶 Loss of interest in activities once enjoyed",
            "😴 Changes in sleep — too much or too little",
            "⚖️ Weight loss or gain",
            "😴 Fatigue and loss of energy",
            "😕 Difficulty thinking or concentrating",
            "😶 Feelings of worthlessness or guilt",
            "🚨 Thoughts of death or suicide",
        ],
        "high_risk_groups": [
            "👩 Women — twice as common in women",
            "👨‍👩‍👧 Family history of depression",
            "😔 History of trauma or abuse",
            "🩸 Chronic illness — diabetes, heart disease",
            "🧪 Substance abuse",
            "😶 Social isolation",
            "👴 Elderly living alone",
        ],
        "prevention": [
            "🏃 Regular exercise — proven to reduce depression",
            "😴 Good sleep routine",
            "🤝 Maintain social connections",
            "🧘 Mindfulness and stress management",
            "🍎 Healthy diet",
            "🚭 Avoid alcohol and drugs",
            "💬 Talk to someone when struggling",
        ],
        "treatment": [
            "💬 Psychotherapy (talking therapy) — very effective",
            "💊 Antidepressants — prescribed by doctor",
            "🏃 Exercise — as effective as medication for mild depression",
            "😴 Sleep hygiene improvement",
            "🤝 Support groups",
            "🏥 Hospitalisation for severe cases with suicidal thoughts",
        ],
        "when_to_seek_help": [
            "Thoughts of harming yourself or others",
            "Unable to perform daily activities",
            "Symptoms lasting more than 2 weeks",
            "Using alcohol or drugs to cope",
            "Withdrawing completely from friends and family",
        ],
        "is_genetic": True,
        "is_contagious": False,
        "recovery_time": "Treatable — many fully recover with treatment in weeks to months.",
        "khareef_connection": "Social isolation during Khareef season can worsen depression symptoms.",
    },
}

# ── Category list for filtering ──
CATEGORIES = sorted(set(d["category"] for d in DISEASES.values()))

# ── Get diseases by category ──
def get_by_category(category: str) -> dict:
    return {k: v for k, v in DISEASES.items() if v["category"] == category}

# ── Search diseases ──
def search_diseases(query: str) -> dict:
    query = query.lower()
    return {
        k: v for k, v in DISEASES.items()
        if (query in k.lower() or
            query in v.get("also_known_as","").lower() or
            query in v.get("arabic_name","").lower() or
            query in v.get("overview","").lower())
    }
