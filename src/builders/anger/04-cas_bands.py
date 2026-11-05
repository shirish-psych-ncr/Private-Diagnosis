CAS_BANDS = [
    {"max": 13, "severity": en_hi("Minimal clinical anger", "न्यूनतम नैदानिक क्रोध"), "key": "minimal"},
    {"max": 19, "severity": en_hi("Mild clinical anger", "हल्का नैदानिक क्रोध"), "key": "mild"},
    {"max": 28, "severity": en_hi("Moderate clinical anger", "मध्यम नैदानिक क्रोध"), "key": "moderate"},
    {"max": 63, "severity": en_hi("Severe clinical anger", "गंभीर नैदानिक क्रोध"), "key": "severe"},
]


def build_cas_scale():
    parts = []
    for idx, c in enumerate(CAS_CLUSTERS, start=1):
        en_opts, hi_opts = c[:4], c[4:]
        qs = [{
            "id": "cas_%d" % idx,
            "itemNumber": idx,
            "cluster": True,
            "text": en_hi("%d. Choose the ONE statement below that best reflects how you feel." % idx,
                          "%d. नीचे दिया वह एकमात्र कथन चुनें जो आपकी भावना सर्वोत्तम दर्शाता है।" % idx),
        }]
        if idx == 9:  # intent to hurt others
            qs[0]["safety"] = True
            qs[0]["safetyNote"] = en_hi(
                "Anger with intent to harm another endorsed — assess safety and risk to others.",
                "पर-कष्ट-इच्छा सहित क्रोध — सुरक्षा एवं परा-हिंसा जोखिम मूल्यांकन करें।")
        parts.append({
            "id": "cas_cluster_%d" % idx,
            "name": en_hi("%d. Anger cluster %d" % (idx, idx), "%d. क्रोध समूह %d" % (idx, idx)),
            # A/B/C/D carry the published weights (A=0, B=1, C=2, D=3) and the four
            # statements of this cluster are their labels — one selection per cluster.
            "options": [{"v": k, "label": en_hi(en_opts[k], hi_opts[k])} for k in range(4)],
            "questions": qs,
        })

    return {
        "id": "clinical_anger_scale",
        "name": en_hi("Clinical Anger Scale (CAS)", "नैदानिक क्रोध पैमाना (CAS)"),
        "type": "matrix",
        "administeredBy": "self-report",
        "sourceInstrument": "CAS",
        "targetAge": ["adult", "older"],
        "directions": en_hi(
            "The groups of items below inquire about the types of feelings you have. Each of the 21 groups has four options "
            "(A, B, C, D). For each cluster, read and identify the ONE statement that best reflects how you feel, and mark "
            "its letter. Answer even if you are not sure. Please be honest in responding to the statements.",
            "नीचे दिए समूह आपकी भावनाओं के प्रकार पूछते हैं। प्रत्येक 21 समूह में चार विकल्प (A, B, C, D) हैं। प्रत्येक समूह में "
            "वह एक कथन पढ़कर पहचानें जो आपकी भावना सर्वोत्तम दर्शाता है और उसका अक्षर अंकित करें। अनिश्चित हों तो भी उत्तर दें। "
            "कथनों पर ईमानदारी से प्रतिविमर्श दें।"),
        "timeframe": en_hi("Your present feelings across the 21 clusters.", "21 समूहों में आपकी वर्तमान भावनाएँ।"),
        "parts": parts,
        "matrixOptions": CAS_OPTS,
        "optionLetters": ["A", "B", "C", "D"],
        "ratingScale": {
            "min": 0, "max": 3,
            "note": en_hi("Scored A = 0, B = 1, C = 2, D = 3; the 21 cluster scores are summed (range 0-63), higher = greater clinical anger.",
                          "A = 0, B = 1, C = 2, D = 3 अंकित; 21 समूहों के अंक जोड़े जाते हैं (शीर्घ 0-63), उच्च = अधिक नैदानिक क्रोध।"),
        },
        "sumScoring": True,
        "bands": CAS_BANDS,
        "scoring": {
            "method": "cas_sum_bands",
            "rule": en_hi(
                "Each cluster of statements is scored on a 4-point Likert scale, with A = 0, B = 1, C = 2, and D = 3. "
                "Responses are summed so that higher scores correspond to greater clinical anger (21 items; range 0-63). "
                "Interpretive ranges: 0-13 minimal clinical anger; 14-19 mild clinical anger; 20-28 moderate clinical anger; "
                "29-63 severe clinical anger.",
                "प्रत्येक कथन-समूह 4-बिंदू Likert पर A = 0, B = 1, C = 2, D = 3 अंकित होता है। सभी जोड़े जाते हैं — उच्च स्कोर = "
                "अधिक नैदानिक क्रोध (21 items; शीर्घ 0-63)। व्याख्या-परिसर: 0-13 न्यूनतम; 14-19 हल्का; 20-28 मध्यम; 29-63 गंभीर।"),
            "maxTotal": 63,
            "notDiagnostic": en_hi(
                "The CAS screens severity of clinical anger; it is not diagnostic and should be confirmed clinically.",
                "CAS नैदानिक क्रोध की तीव्रता स्क्रीन करता है; रोग-निर्णायक नहीं, नैदानिक पुष्टि आवश्यक।"),
        },
        "sourcePages": "User-supplied Clinical Anger Scale booklet (copyright 1995) and scoring instructions.",
        "translationNote": "Hindi labels are machine-assisted aids; English is authoritative. Clinician proofreading required.",
        "branching": None,
    }


def build_domain():
    return {
        "id": "anger",
        "name": en_hi("Anger and impulse control", "क्रोध एवं आवेग-नियंत्रण"),
        "tier": 2,
        "description": en_hi(
            "Optional anger-assessment block. Endorsing a screen-in item deploys the corresponding instrument: the STAXI-CA "
            "(State-Trait Anger Expression Inventory — 57 rated items across State Anger, Trait Anger and the Anger "
            "Expression/Control scales) or the Clinical Anger Scale (21 four-option clusters, summed 0-63). Both produce "
            "dimensional/severity information only; neither is diagnostic.",
            "वैकल्पिक क्रोध-मूल्यांकन ब्लॉक। स्क्रीन-इन आइटम चुनें तो संबंधित साधन खुलता है: STAXI-CA (अवस्था-लक्षण क्रोध "
            "अभिव्यक्ति सूची — 57 रेटेड आइटम: अवस्था क्रोध, लक्षण क्रोध, क्रोध-अभिव्यक्ति/नियंत्रण) अथवा नैदानिक क्रोध पैमाना "
            "(21 चार-विकल्प समूह, योग 0-63)। दोनों केवल आयाम/तीव्रता सूचना देते हैं; कोई रोग-निर्णायक नहीं।"),
        "instrument": "auto:angertable",
        "cutoff": None,
        "questions": [
            {
                "id": "ang_1",
                "text": en_hi(
                    "Do you often feel angry, irritable or furious, or find yourself reacting with yelling, arguing or physical aggression?",
                    "क्या आपको प्रायः क्रोध, चिड़चिड़ापन अथवा प्रकोप महसूस होता है, अथवा आप चिल्लाना, वाद-विवाद अथवा शारीरिक आक्रामकता से प्रतिक्रिया देते/देती पाते/पाती हैं?"),
                "sharedScale": "yesno",
                "scaleId": "staxi_ca",
                "disorders": GENERIC_ANGER_DISORDERS,
            },
            {
                "id": "ang_2",
                "text": en_hi(
                    "Over the past several years, has anger been a persistent problem for you — affecting your mood, your relationships, your work or studies, your sleep, appetite or health?",
                    "गत कुछ वर्षों में क्या क्रोध आपके लिए सतत समस्या रहा है — भावना, संबंध, कार्य/अध्ययन, नींद, भूख अथवा स्वास्थ्य को प्रभावित करता है?"),
                "sharedScale": "yesno",
                "scaleId": "clinical_anger_scale",
                "disorders": GENERIC_ANGER_DISORDERS,
            },
        ],
    }


