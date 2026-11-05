        "timeframe": {
            "en": "Past 6 months.",
            "hi": "पिछले 6 माह।",
        },
        "definition": {
            "en": "Gender identity",
            "text": {
                "en": ("One's internal sense of one's self as a man, a woman, or "
                       "some other gender."),
                "hi": "किसी का अंतर्गत स्व-बोध — पुरुष, महिला या अन्य कोई लिंग के रूप में।",
            },
        },
        "parts": parts,
        "matrixOptions": [
            {"v": o["v"], "label": {"en": o["en"], "hi": o["hi"]}} for o in FREQUENCY_OPTIONS
        ],
        "ratingScale": {
            "min": 0, "max": 4,
            "note": {
                "en": ("Frequency rating per item: Never = 0 · Rarely = 1 · Sometimes = 2 · "
                       "Often = 3 · Always = 4. Positively worded congruence/satisfaction "
                       "items (16, 20, 22, 30, 35, 37) are reverse-scored (4 − response)."),
                "hi": ("प्रत्येक आइटम की आवृत्ति: कभी नहीं = 0 · विरल = 1 · कभी-कभी = 2 · "
                       "अक्सर = 3 · सदैव = 4। सकारात्मक रूप से अभिव्यक्त संगति/संतुष्टि कथनों "
                       "(16, 20, 22, 30, 35, 37) का व्युक्रम-अंकन होता है (4 − उत्तर)।"),
            },
        },
        "subscales": subscales,
        "tickBoxItem": {
            "id": "gcls_surgery_tick",
            "linkedItem": 26,
            "scored": False,
            "purpose": {
                "en": ("Records whether genital surgery has already been carried out, so "
                       "that item 26 ('genital surgery will address the unhappiness') can "
                       "be interpreted correctly. Not included in any subscale total."),
                "hi": ("यह दर्ज करता है कि जननांग-शस्त्रक्रिया पहले हो चुकी है या नहीं, ताकि आइटम 26 "
                       "('जननांग-शस्त्रक्रिया असुख को दूर करेगी') की व्याख्या ठीक से की जा सके। किसी "
                       "उप-पैमाना योग में नहीं जोड़ा जाता।"),
            },
        },
        "sumScoring": True,
        "scoring": {
            "method": "gcls_reverse_keyed_subscales",
            "scaleMin": 0,
            "scaleMax": 4,
            "rule": {
                "en": ("Score each item Never=0, Rarely=1, Sometimes=2, Often=3, Always=4. "
                       "Reverse-score the positively worded items 16, 20, 22, 30 (congruence) "
                       "and 35, 37 (negative satisfaction wording) as 4 minus the response. "
                       "Sum within each subscale: Functional impact 1-13 (0-52), Body "
                       "preoccupation 14,15,17,18,19,21,23,24,26,27,28,29 (0-48), Social "
                       "preoccupation 16,20,22,30 reversed (0-16). Life satisfaction 31-38 "
                       "with 35 and 37 reversed (0-32) is reported separately — higher means "
                       "MORE satisfaction. The □ surgery tick-box is not scored."),
                "hi": ("प्रत्येक आइटम: कभी नहीं=0, विरल=1, कभी-कभी=2, अक्सर=3, सदैव=4। सकारात्मक "
                       "कथनों 16, 20, 22, 30 (संगति) तथा 35, 37 (नकारात्मक संतुष्टि-शब्दावली) का "
                       "व्युक्रम (4 − उत्तर) करें। प्रत्येक उप-पैमाने का योग: कार्यात्मक प्रभाव 1-13 "
                       "(0-52), शारीरिक आसक्ति 14,15,17,18,19,21,23,24,26,27,28,29 (0-48), सामाजिक "
                       "आसक्ति 16,20,22,30 व्युक्रम (0-16)। जीवन-संतुष्टि 31-38 (35 एवं 37 व्युक्रम, "
                       "0-32) पृथक् रिपोर्ट — उच्च अर्थ अधिक संतुष्टि। □ शस्त्रक्रिया-चिह्न अंकित नहीं।"),
            },
            "notDiagnostic": {
                "en": ("The GCLS describes gender-related distress and life satisfaction; it "
                       "does not diagnose gender incongruence/dysphoria, which rests on the "
                       "DSM-5-TR / ICD-11 criteria and a clinical assessment. Gender diversity "
                       "alone is not a mental disorder. Scores also inform treatment planning "
                       "and follow-up rather than eligibility for any intervention."),
