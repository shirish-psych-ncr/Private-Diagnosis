def build_domain():
    return {
        "id": "personality",
        "name": en_hi("Personality functioning", "व्यक्तित्व कार्यक्षमता"),
        "tier": 2,
        "description": en_hi(
            "Optional personality-disorder screening block. Endorsing a screen-in item deploys the corresponding self-report instrument: the IPDE ICD-10 module screening questionnaire (five-option True/False keyed items across the nine F60 clusters) or the PDQ-4+ (99-item questionnaire with validity items, Section B impulsivity/conduct checklists and the mandatory clinical-significance follow-up). Neither instrument is diagnostic.",
            "वैकल्पिक व्यक्तित्व विकार स्क्रीनिंग ब्लॉक। स्क्रीन-इन आइटम चुनें तो संबंधित साधन खुलता है: IPDE ICD-10 माड्यूल स्क्रीनिंग प्रश्नावली (नौं F60 क्लस्टर पर कुंजी-उत्तर T/F आइटम) अथवा PDQ-4+ (99-आइटम, वैधता आइटम, खंड-B सूचियाँ एवं अनिवार्य नैदानिक महत्व अनुवर्ती)। कोई भी साधन रोग-निर्णायक नहीं है।"),
        "instrument": "auto:pdscreen",
        "cutoff": None,
        "questions": [
            {
                "id": "pd_1",
                "text": en_hi("Over the past several years, have people frequently complained about how you relate to others, or have you repeatedly found yourself in conflict in close relationships?",
                              "गत कुछ वर्षों में क्या लोग आपके संबंधों पर प्रायः शिकायत करते आए हैं अथवा घनिष्ठ संबंधों में आप बार-बार संघर्ष में रहे हैं?"),
                "sharedScale": "yesno",
                "scaleId": "ipde_screen",
                "disorders": GENERIC_PD_DISORDERS,
            },
            {
                "id": "pd_2",
                "text": en_hi("Do you tend to react to other people in ways that have stayed much the same since adolescence — for example being unusually suspicious, withdrawn, demanding, emotionally unstable, or rigid about rules?",
                              "क्या आप किशोरावस्था से लगभग अपरिवर्तित  tarike से लोगों को प्रतिक्रिया देते आए हैं — जैसे असामान्य संदेहशीलता, एकांतवाद, मांगपन, भावनात्मक अस्थिरता अथवा नियमों पर कठोरता?"),
                "sharedScale": "yesno",
                "scaleId": "pdq4_screen",
                "disorders": GENERIC_PD_DISORDERS,
            },
        ],
    }


NEW_DISORDERS = {
    "paranoid_personality_disorder": ("Paranoid Personality Disorder", "संशयात्मक व्यक्तित्व विकार", "6D10", "F60.0", 2,
        "Pattern of pervasive distrust and suspiciousness such that others' motives are interpreted as malevolent."),
    "schizoid_personality_disorder": ("Schizoid Personality Disorder", "स्किज़ॉइड व्यक्तित्व विकार", "6D11", "F60.1", 2,
        "Detachment from social relationships and a restricted range of emotional expression."),
    "schizotypal_personality_disorder": ("Schizotypal Personality Disorder", "स्किज़ोटिपल व्यक्तित्व विकार", "6D12", "F60.2 (ICD-10 schizotypal is F21)", 2,
        "Social deficits with acute discomfort in close relationships, cognitive or perceptual distortions, and eccentricities of behaviour."),
    "borderline_personality_disorder": ("Borderline Personality Disorder", "सीमांत व्यक्तित्व विकार", "6D110", "F60.31", 2,
        "Instability of interpersonal relationships, self-image and affects, and marked impulsivity."),
    "impulsive_control_features": ("Impulsive control features (ICD-10 F60.30 dissocial, impulsive subtype)", "आवेगी नियंत्रण लक्षण (ICD-10 F60.30)", "6D11", "F60.30", 2,
        "Emotional instability and impulsive tendency without the full borderline pattern."),
    "histrionic_personality_disorder": ("Histrionic Personality Disorder", "हिस्ट्रियोनिक व्यक्तित्व विकार", "6D13", "F60.4", 2,
        "Excessive emotionality and attention-seeking."),
    "narcissistic_personality_disorder": ("Narcissistic Personality Disorder", "नार्सिसिस्टिक व्यक्तित्व विकार", "6D14", "F60.6 (ICD-10 has no dedicated category)", 2,
        "Grandiosity, need for admiration and lack of empathy."),
    "avoidant_personality_disorder": ("Avoidant Personality Disorder", "परिहरणकारी व्यक्तित्व विकार", "6D15", "F60.6", 2,
        "Social inhibition, feelings of inadequacy and hypersensitivity to negative evaluation."),
    "dependent_personality_disorder": ("Dependent Personality Disorder", "निर्भर व्यक्तित्व विकार", "6D16", "F60.7", 2,
        "Excessive need to be taken care of leading to submissive and clinging behaviour and fears of separation."),
    "obsessive_compulsive_personality_disorder": ("Obsessive-Compulsive Personality Disorder", "ऑब्सेसिव-कंपल्सिव व्यक्तित्व विकार", "6D17", "F60.5", 2,
        "Preoccupation with orderliness, perfectionism and mental and interpersonal control at the expense of flexibility."),
    "passive_aggressive_personality_disorder": ("Passive-Aggressive (Negativistic) Personality Features", "निष्क्रिय-आक्रामक (नकारात्मकता) व्यक्तित्व लक्षण", "6D1Z", "F60.89", 2,
        "Pessimistic, obstructive handling of tasks and indirect expression of dissatisfaction; DSM-IV provisional category."),
    "depressive_personality_disorder": ("Depressive Personality Features", "अवसादी व्यक्तित्व लक्षण", "6D1Z", "F60.89", 2,
        "Chronic gloomy, self-critical, pessimistic disposition; not an official DSM-5 disorder."),
    "other_specified_personality_disorder": ("Other Specified Personality Disorder", "अन्य निर्दिष्ट व्यक्तित्व विकार", "6D1Z", "F60.8 / F60.9", 2,
        "Clinically significant personality pattern causing distress or impairment that does not meet full criteria for a specific cluster-C/A/B disorder."),
    "unspecified_personality_disorder": ("Unspecified Personality Disorder", "अनिर्दिष्ट व्यक्तित्व विकार", "6D1Z", "F60.9", 2,
        "Screen-positive personality pattern awaiting the structured interview (IPDE/PDQ-4+ screens are hypothesis-generating only)."),
}


