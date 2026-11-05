crossCuttingMeasures = {
  "id": "OPT-A",
  "optionalAssessment": True,
  "name": {"en": "Additional Optional Assessment A — Cross-Cutting Measures: Severity of Symptom",
           "hi": "अतिरिक्त वैकल्पिक मूल्यांकन A — क्रॉस-कटिंग माप: लक्षणों की तीव्रता"},
  "intro": {"en": "Use this scale to rate the severity of your symptom in the score column in the table below: Assessment of Symptoms That Cut Across Disorders.",
            "hi": "इस पैमाने का उपयोग नीचे दी गई तालिका के स्कोर कॉलम में अपने लक्षण की तीव्रता रेट करने हेतु करें: विकारों-पार लक्षणों का मूल्यांकन।"},
  "tableHeading": {"en": "Symptom Name / Score", "hi": "लक्षण का नाम / स्कोर"},
  "items": [{"id": sid, "text": {"en": sen, "hi": shi}} for sid, sen, shi in ccSymptoms],
  "ratingScale": {"min": 0, "max": 10, "type": "clinician_rating",
                  "anchors": [{"v": 0, "label": {"en": "Not present", "hi": "उपस्थित नहीं"}},
                              {"v": 1, "label": {"en": "Mild", "hi": "हल्का"}},
                              {"v": 3, "label": {"en": "Moderate", "hi": "मध्यम"}},
                              {"v": 6, "label": {"en": "Severe", "hi": "गंभीर"}},
                              {"v": 10, "label": {"en": "Extreme", "hi": "अत्यधिक"}}]},
  "note": {"en": "Clinician-rated 0-10 severity for each cross-cutting symptom domain; independent of the Module A-P branching logic and does not gate any diagnostic box.",
           "hi": "प्रत्येक क्रॉस-कटिंग लक्षण-क्षेत्र हेतु चिकित्सक-रेटित 0-10 तीव्रता; माड्यूल A-P की शाखा-विभाजन पद्धति से स्वतंत्र तथा किसी निदान-बक्से को नियंत्रित नहीं करता।"}}

