modL = {
  "id": "L",
  "name": {"en": "Module L — Anorexia Nervosa",
           "hi": "माड्यूल L — एनोरेक्सिया नर्वोसा"},
  "screen": {"intro": {"en": "L1 — Height and lowest weight in the past 3 months",
                        "hi": "L1 — ऊँचाई और पिछले 3 माह का न्यूनतम वज़न"},
             "questions": [
      q("L1a", "How tall are you? (feet/inches or centimetres)",
        "आपकी ऊँचाई कितनी है? (फ़ीट/इंच या सेंटीमीटर)", nonScoring=True, measurement="height"),
      q("L1b", "What was your lowest weight in the past 3 months? (pounds or kilograms)",
        "पिछले 3 माह में आपका सबसे कम वज़न क्या था? (पाउंड या किलोग्राम)", nonScoring=True, measurement="weight")],
             "gateRule": "IF L1c No -> GO TO THE DIAGNOSTIC BOX, CIRCLE NO, AND MOVE TO THE NEXT MODULE.",
             "gateNote": {"en": "If the patient's weight is above the threshold for his/her height, Module L terminates (Anorexia Nervosa coded No).",
                          "hi": "यदि रोगी का वज़न उसकी ऊँचाई की सीमा से अधिक है, तो माड्यूल L समाप्त (एनोरेक्सिया नर्वोसा 'नहीं' कोड)।"}},
  "l1c": {"id": "L1c",
          "text": {"en": "Is patient's weight equal to or below the threshold corresponding to his/her height? (See the height/weight table below.)",
                   "hi": "क्या रोगी का वज़न उसकी ऊँचाई संगत सीमा के बराबर या उससे कम है? (नीचे ऊँचाई/वज़न सारणी देखें।)"},
          "thresholdTable": HEIGHT_WEIGHT_TABLE},
  "pastThreeMonthsIntro": {"en": "In the past 3 months:", "hi": "पिछले 3 माह में:"},
  "l2": q("L2", "In spite of this low weight, have you tried not to gain weight or to restrict your food intake?",
          "इतने कम वज़न के बावजूद, क्या आपने वज़न बढ़ने से रोकने या भोजन-सेवन सीमित करने का प्रयास किया?"),
  "l3": q("L3", "Have you intensely feared gaining weight or becoming fat, even though you were underweight?",
          "क्या आपको अल्पभारी होने के बावजूद वज़न बढ़ने या मोटे होने का तीव्र भय रहा?"),
  "l4": [
      q("L4a", "Have you considered yourself too big/fat or that part of your body was too big/fat?",
        "क्या आपने स्वयं को अधिक बड़ा/मोटा या शरीर का कोई भाग अधिक बड़ा/मोटा समझा?"),
      q("L4b", "Has your body weight or shape greatly influenced how you felt about yourself?",
        "क्या आपके शारीरिक वज़न/आकार ने स्वयं के प्रति आपकी भावना को बहुत प्रभावित किया?"),
      q("L4c", "Have you thought that your current low body weight was normal or excessive?",
        "क्या आपने वर्तमान कम शारीरिक वज़न को सामान्य या अधिक माना?")],
  "l5Gate": {"rule": "IF 0 of L4 answers Yes -> GO TO THE DIAGNOSTIC BOX, CIRCLE NO, AND MOVE TO THE NEXT MODULE.",
             "text": {"en": "L5: Are 1 or more items from L4 coded Yes?",
                      "hi": "L5: क्या L4 के 1 या अधिक मद 'हाँ' कोडित हैं?"}},
  "diagnosticBoxes": [
    {"id": "L_diag", "label": {"en": "Anorexia Nervosa — Current", "hi": "एनोरेक्सिया नर्वोसा — वर्तमान"},
     "rule": "L1c Yes AND L2 Yes AND L3 Yes AND L5 Yes (1+ of L4). Restricting vs Binge-Eating/Purging type is decided in Module M (M7/M8).",
     "flags": ["CURRENT"], "disordersOnPositive": ["eating_anorexia"]}]
}

# Shared severity specifiers for eating disorders (Modules M / MB).
