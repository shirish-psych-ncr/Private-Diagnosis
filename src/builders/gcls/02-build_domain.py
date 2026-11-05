def build_domain(scale_id="gcls"):
    return {
        "id": "gender",
        "name": {
            "en": "Gender identity, incongruence & related distress",
            "hi": "लिंग-पहचान, असंगति एवं संबंधी कष्ट",
        },
        "tier": 2,
        "optional": True,
        "instrument": "auto:genderdistress",
        "timeframe": {
            "en": "Past 6 months.",
            "hi": "पिछले 6 माह।",
        },
        "help": {
            "en": ("Endorsing either question deploys the Gender Congruence and Life "
                   "Satisfaction Scale (GCLS), a 38-item self-report of gender-related "
                   "distress, body and social preoccupation, and life satisfaction over "
                   "the past 6 months. It describes distress and functioning; it does not "
                   "diagnose gender incongruence, and gender diversity alone is not a "
                   "mental disorder."),
            "hi": ("किसी भी प्रश्न को स्वीकार करने पर लंग-संगति एवं जीवन-संतुष्टि मापनी (GCLS) "
                   "खुलेगी — 38 आइटम की स्व-रिपोर्ट जो पिछले 6 माह के लिंग-संबंधी कष्ट, शारीरिक व "
                   "सामाजिक आसक्ति तथा जीवन-संतुष्टि को वर्णित करती है। यह कष्ट एवं कार्य-क्षमता का "
                   "वर्णन करता है; लिंग-असंगति का रोग-निर्णय नहीं करता, और केवल लिंग-विविधता मानसिक "
                   "विकार नहीं है।"),
        },
        "questions": [
            {
                "id": "gen_1",
                "text": {
                    "en": ("Do you feel distress because the gender you were assigned at "
                           "birth does not match the gender you know yourself to be?"),
                    "hi": ("क्या आपको कष्ट होता है क्योंकि जन्म के समय सौंपा गया लिंग उस लिंग से "
                           "मेल नहीं खाता जिसे आप स्वयं के रूप में जानते हैं?"),
                },
                "scaleId": scale_id,
                "sharedScale": "yes_no",
                "disorders": ["gender_incongruence"],
            },
            {
                "id": "gen_2",
                "text": {
                    "en": ("Has distress about your gender interfered with your social life, "
                           "education or work, relationships, or enjoyment of life in the "
                           "past 6 months?"),
                    "hi": ("पिछले 6 माह में आपके लिंग संबंधी कष्ट ने आपके सामाजिक जीवन, शिक्षा या "
                           "कार्य, संबंधों, या जीवन के आनंद में बाधा डाली है?"),
                },
                "scaleId": scale_id,
                "sharedScale": "yes_no",
                "disorders": ["gender_incongruence"],
            },
        ],
    }


DISORDERS_TO_ADD = {
    "gender_incongruence_distress": {
        "name": {"en": "Gender-related distress (GCLS screen)",
                 "hi": "लिंग-संबंधी कष्ट (GCLS स्क्रीन)"},
        "tier": 2,
        "dsm5": "Gender Dysphoria (severity specifier)",
        "icd11": "HA60",
        "description": {
            "en": ("Elevated gender-related distress and/or reduced life satisfaction on "
                   "the GCLS, recorded as a screening finding that needs the diagnostic "
                   "assessment of gender incongruence/dysphoria."),
            "hi": ("GCLS पर उच्च लिंग-संबंधी कष्ट अथवा कम जीवन-संतुष्टि — एक स्क्रीनिंग प्राप्ति "
                   "के रूप में अंकित, जिसके लिए लिंग-असंगति/डिस्फोरिया का नैदानिक मूल्यांकन आवश्यक।"),
        },
        "icd11Chapter": "Chapter 17: Conditions related to sexual health",
        "mappingNote": ("Screen flag only. GCLS subscale scores describe distress and "
                        "functioning; the diagnosis of gender incongruence (ICD-11 HA60/HA61/HA6Z) "
                        "or DSM-5-TR gender dysphoria requires the published criteria met over at "
                        "least six months, established by clinical assessment. Never record a "
                        "GCLS score as a diagnosis, and never treat gender diversity itself as "
                        "disorder."),
    },
    "gender_dysphoria_with_functional_impairment": {
        "name": {"en": "Gender-related functional impairment & low life satisfaction",
                 "hi": "लिंग-संबंधी कार्य-बाधा एवं निम्न जीवन-संतुष्टि"},
        "tier": 2,
        "dsm5": "Contextual specifier (functioning)",
        "icd11": "QA2x / contextual",
        "description": {
            "en": ("High functional-impact and low life-satisfaction scores on the GCLS — a "
                   "treatment-planning and follow-up marker rather than a diagnosis."),
            "hi": ("GCLS पर उच्च कार्यात्मक-प्रभाव एवं निम्न जीवन-संतुष्टि स्कोर — रोग-निर्णय नहीं, "
                   "वرن उपचार-योजना एवं अनुवर्ती का सूचक।"),
        },
        "icd11Chapter": "Contextual codes (not a Chapter 06 mental disorder)",
        "mappingNote": ("Contextual modifier only; never a primary diagnosis. Use it to record "
                        "that distress about gender is disrupting school/work, relationships, "
                        "intimacy or home life, and to justify psychosocial support, referral to "
                        "a gender service and repeat measurement of satisfaction over time."),
    },
}


