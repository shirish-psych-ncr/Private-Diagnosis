  "mb6Gate": {"rule": "IF <3 of MB6 answers Yes -> GO TO THE DIAGNOSTIC BOX, CIRCLE NO, AND MOVE TO THE NEXT MODULE.",
              "text": {"en": "Are 3 or more MB6 questions coded Yes?",
                        "hi": "क्या MB6 के 3 या अधिक प्रश्न 'हाँ' कोडित हैं?"}},
  "mb7": q("MB7", "Does your binging distress you a lot?",
           "क्या आपका प्रपात आपको बहुत कष्ट देता है?"),
  "mb8Episodes": {"id": "MB8a", "numeric": True, "max": 99,
                  "text": {"en": "Number of binge eating episodes per week?",
                            "hi": "प्रति सप्ताह अतिभक्षण एपिसोड की संख्या?"}},
  "mb8Days": {"id": "MB8b", "numeric": True, "max": 7,
              "text": {"en": "Number of binge eating days per week?",
                       "hi": "प्रति सप्ताह अतिभक्षण दिनों की संख्या?"}},
  "specifierNote": {"en": "Specifiers of eating disorder: MILD = 1-3 episodes of binge eating per week; MODERATE = 4-7; SEVERE = 8-13; EXTREME = 14 or more.",
                    "hi": "भोजन-विकार विशेषण: मृदु = प्रति सप्ताह 1-3 प्रपात एपिसोड; मध्यम = 4-7; गंभीर = 8-13; अत्यंत गंभीर = 14 या अधिक।"},
  "diagnosticBoxes": [
    {"id": "MB_diag", "label": {"en": "Binge-Eating Disorder — Current", "hi": "बिंज-ईटिंग (अतिभक्षण) विकार — वर्तमान"},
     "rule": "MB1 No AND MB2 No AND MB3 Yes AND MB4 Yes AND MB5 No AND >=3 of MB6 Yes AND MB7 Yes. Severity by weekly binge-eating episodes (1-3 mild, 4-7 moderate, 8-13 severe, 14+ extreme).",
     "flags": ["CURRENT"] + EATING_SEVERITY_SPECIFIERS, "disordersOnPositive": ["eating_binge_eating"]}]}

