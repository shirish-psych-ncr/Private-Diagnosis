disabilityImpairment = {
  "id": "OPT-B",
  "optionalAssessment": True,
  "name": {"en": "Additional Optional Assessment B — Disability / Functional Impairment: Severity of Disability / Impairment",
           "hi": "अतिरिक्त वैकल्पिक मूल्यांकन B — अक्षमता/कार्यात्मक हानि: अक्षमता/हानि की तीव्रता"},
  "intro": {"en": "Use this scale to rate in the score column of the table below, how much your symptoms have disrupted your ability to function in the following areas of your life: Assessment of Impairment of Functioning/Disability.",
            "hi": "इस पैमाने का उपयोग नीचे दी गई तालिका के स्कोर कॉलम में रेट करने हेतु करें कि आपके लक्षणों ने आपके जीवन के निम्न क्षेत्रों में कार्य करने की क्षमता को कितना बाधित किया है: कार्यात्मक हानि/अक्षमता का मूल्यांकन।"},
  "tableHeading": {"en": "Domain Name / Score", "hi": "क्षेत्र का नाम / स्कोर"},
  "items": [{"id": did, "text": {"en": den, "hi": dhi}} for did, den, dhi in disabilityItems],
  "ratingScale": {"min": 0, "max": 10, "type": "clinician_rating",
                  "anchors": [{"v": 0, "label": {"en": "Not present", "hi": "उपस्थित नहीं"}},
                              {"v": 1, "label": {"en": "Mild", "hi": "हल्का"}},
                              {"v": 3, "label": {"en": "Moderate", "hi": "मध्यम"}},
                              {"v": 6, "label": {"en": "Severe", "hi": "गंभीर"}},
                              {"v": 10, "label": {"en": "Extreme", "hi": "अत्यधिक"}}]},
  "note": {"en": "Clinician-rated 0-10 disruption for each functional domain; independent of the Module A-P branching logic and does not gate any diagnostic box.",
           "hi": "प्रत्येक कार्यात्मक क्षेत्र हेतु चिकित्सक-रेटित 0-10 बाधा; माड्यूल A-P की शाखा-विभाजन पद्धति से स्वतंत्र तथा किसी निदान-बक्से को नियंत्रित नहीं करता।"}}

# ---------------------------------------------------------------------------
# Additional optional interview assessment: Mood Disorders Diagnostic Algorithm
# (consult Modules A - Major Depressive Episode, C - (Hypo)manic Episode,
#  K - Psychotic Disorders). Derived boxes; no new interview items.
# ---------------------------------------------------------------------------
