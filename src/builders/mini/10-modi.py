modI = {
  "id": "I",
  "name": {"en": "Module I — Alcohol Use Disorder",
           "hi": "माड्यूल I — मद्य-सेवन विकार"},
  "screen": {"intro": {"en": "Screen-in question (past 12 months)", "hi": "स्क्रीन-इन प्रश्न (पिछले 12 माह)"},
             "questions": [
      q("I1", "In the past 12 months, have you had 3 or more alcoholic drinks, within a 3-hour period, on 3 or more occasions?",
        "पिछले 12 माह में, क्या 3-घंटे की अवधि में 3 या अधिक पेय, 3 या अधिक अवसरों पर लिए?")],
             "gateRule": "IF I1 No -> GO TO DIAGNOSTIC BOX, CIRCLE NO AND MOVE TO THE NEXT MODULE.",
             "gateNote": {"en": "If I1 is No, Module I terminates (Alcohol Use Disorder coded No).",
                          "hi": "यदि I1 'नहीं', माड्यूल I समाप्त (मद्य-सेवन विकार 'नहीं' कोड)।"}},
  "criteriaIntro": {"en": "In the past 12 months:", "hi": "पिछले 12 माह में:"},
  "criteria": _use_criteria("I2", "alcohol", "शराब"),
  "k1": {"id": "I2k1",
         "text": {"en": "When you cut down on heavy or prolonged drinking did you have any of the following: (If yes to 2 or more of the 8, code k1 as Yes.)",
                  "hi": "अत्यधिक/दीर्घ सेवन घटाने पर निम्नलिखित में से कोई हुआ: (8 में से 2+ 'हाँ' हो तो k1 'हाँ' कोड करें।)"},
         "checklist": WITHDRAWAL_ALCOHOL, "minChecks": 2},
  "k2": q("I2k2", "Did you drink alcohol to reduce or avoid withdrawal symptoms or to avoid being hung-over?",
          "क्या विषमुक्ति-लक्षण घटाने/टालने या हैंगओवर बचने हेतु शराब पी?"),
  "kSummary": {"id": "I2k_summary",
               "rule": "IF YES TO I2k1 OR I2k2, CODE YES. (I2k1 and I2k2 together count as one among the I2 criteria.)",
               "text": {"en": "I2k SUMMARY: If yes to I2k1 or I2k2, code Yes.",
                        "hi": "I2k सारांश: यदि I2k1 या I2k2 'हाँ' तो 'हाँ' कोड।"}},
  "gate": {"rule": "IF <2 of I2a-I2k SUMMARY coded Yes -> Alcohol Use Disorder NO.",
           "text": {"en": "Are 2 or more I2 answers from I2a through I2k SUMMARY coded Yes? (I2k1 and I2k2 together count as one among these choices.)",
                    "hi": "क्या I2a से I2k सारांश तक के 2 या अधिक उत्तर 'हाँ' कोडित हैं? (I2k1 व I2k2 संयुक्त रूप से एक गिने जाते हैं।)"}},
  "specifierNote": {"en": "Specifiers: MILD = 2-3 of the I2 symptoms; MODERATE = 4-5; SEVERE = 6 or more. IN EARLY REMISSION = criteria not met for between 3 & 12 months; IN SUSTAINED REMISSION = criteria not met for 12 months or more (both with the exception of criterion d [craving]); IN A CONTROLLED ENVIRONMENT = where alcohol access is restricted.",
                    "hi": "विशेषण: मृदु = I2 के 2-3 लक्षण; मध्यम = 4-5; गंभीर = 6+। प्रारंभिक-मिटी = 3-12 माह मानदंड पूरे नहीं; दीर्घ-मिटी = 12+ माह मानदंड पूरे नहीं (दोनों में मानदंड d [लालसा] अपवाद); नियंत्रित-वातावरण = जहाँ शराब-प्राप्ति सीमित हो।"},
  "diagnosticBoxes": [
    {"id": "I_diag", "label": {"en": "Alcohol Use Disorder — Past 12 Months", "hi": "मद्य-सेवन विकार — पिछले 12 माह"},
     "rule": "I1 Yes AND >=2 of I2a-I2k SUMMARY Yes. Severity by symptom count (2-3 mild, 4-5 moderate, 6+ severe).",
     "flags": USE_DISORDER_SPECIFIERS, "disordersOnPositive": ["alcohol_use_disorder"]}]
}

