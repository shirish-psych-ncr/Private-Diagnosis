def build_phq15():
    qs = []
    for num, en, hi in PHQ15_ITEMS:
        q = {"id": "phq15_%d" % num, "itemNumber": num, "text": en_hi(en, hi)}
        if num == 4:
            q["applicability"] = "women_only"
        qs.append(q)
    return {
        "id": "phq15",
        "name": en_hi("PHQ-15 — Somatic Symptom Severity Scale",
                      "PHQ-15 — शारीरिक लक्षण तीव्रता मापनी"),
        "type": "matrix",
        "administeredBy": "self-report",
        "optionalAssessment": True,
        "sourceInstrument": "PHQ-15",
        "targetAge": ["adult"],
        "directions": en_hi(
            "During the past four weeks, how much have you been bothered by any of the following problems?",
            "पिछले चार सप्ताह में, निम्नलिखित समस्याओं से आप कितने परेशान रहे हैं?"),
        "timeframe": en_hi("Past four weeks.", "पिछले चार सप्ताह।"),
        "parts": [{
            "id": "phq15_items",
            "name": en_hi("Somatic symptoms", "शारीरिक लक्षण"),
            "options": PHQ_OPTS,
            "questions": qs,
        }],
        "matrixOptions": PHQ_OPTS,
        "ratingScale": {
            "min": 0, "max": 2,
            "note": en_hi(
                "Not bothered at all = 0 · Bothered a little = 1 · Bothered a lot = 2. Sum all 15 items (range 0-30).",
                "बिल्कुल परेशान नहीं = 0 · थोड़ा परेशान = 1 · बहुत परेशान = 2। सभी 15 आइटम जोड़ें (शीर्घ 0-30)।"),
        },
        "sumScoring": True,
        "scoring": {
            "method": "phq15_sum_bands",
            "scaleMin": 0, "scaleMax": 2,
            "rule": en_hi(
                "0-4 = no somatisation disorder; 5-9 = mild; 10-14 = moderate; 15+ = severe somatisation disorder.",
                "0-4 = कोई सोमटाइज़ेशन रोग नहीं; 5-9 = हल्का; 10-14 = मध्यम; 15+ = गंभीर सोमटाइज़ेशन रोग।"),
            "notDiagnostic": en_hi(
                "The PHQ-15 is intended to supplement clinical acumen and experience for individual patients; it does not diagnose.",
                "PHQ-15 का उद्देश्य चिकित्सकीय बुद्धि एवं अनुभव की सहायता करना है; यह रोग-निर्णय नहीं करता।"),
            "disorders": ["somatic_symptom_disorder"],
        },
        "bands": [
            {"max": 4, "severity": en_hi("No somatisation disorder", "सोमटाइज़ेशन रोग नहीं"), "key": "none"},
            {"max": 9, "severity": en_hi("Mild somatisation disorder", "हल्का सोमटाइज़ेशन रोग"), "key": "mild"},
            {"max": 14, "severity": en_hi("Moderate somatisation disorder", "मध्यम सोमटाइज़ेशन रोग"), "key": "moderate"},
            {"max": 30, "severity": en_hi("Severe somatisation disorder", "गंभीर सोमटाइज़ेशन रोग"), "key": "severe"},
        ],
        "sourcePages": "PHQ-15 (Kroenke et al.) — 15-item somatic symptom severity scale, printed form supplied",
        "branching": None,
    }


SOMATIC_DOMAIN = {
    "id": "somatic",
    "name": en_hi("Somatic symptoms & health-related preoccupation",
                  "शारीरिक लक्षण एवं स्वास्थ्य-संबंधी चिंतन"),
    "tier": 2,
    "optional": True,
    "instrument": "auto:somatoptable",
    "timeframe": en_hi("Past months of physical symptoms and healthcare contact.",
                       "पिछले कई माह के शारीरिक लक्षण एवं चिकित्सा-संपर्क।"),
    "help": en_hi(
        "Endorse either question to open the corresponding rating instrument: the PHQ-15 "
        "somatic severity index and/or the FAC22-SR factitious-disorder screen. Both are "
        "screening/severity measures and never establish a diagnosis by themselves.",
        "किसी भी प्रश्न को स्वीकार करने पर संगत मापनी खुलेगी: PHQ-15 शारीरिक तीव्रता सूचकांक एवं/अथवा FAC22-SR भत्रुण-रोग स्क्रीन। दोनों स्क्रीन/तीव्रता माप हैं; स्वयं रोग-निर्णय नहीं करते।"),
    "questions": [
        {
            "id": "som_1",
            "text": en_hi(
                "Do you have several physical symptoms that bother you or that doctors have not been able to explain clearly?",
                "क्या आपके कई शारीरिक लक्षण हैं जो आपको परेशान करते हैं या जिन्हें चिकित्सक स्पष्ट रूप से समझा नहीं पाए?"),
            "scaleId": "phq15",
            "sharedScale": "yes_no",
            "disorders": ["somatic_symptom_disorder", "conversion_disorder"],
        },
        {
            "id": "som_2",
            "text": en_hi(
                "Do you feel that your illness has been treated differently from what you expected, or that the attention you receive while being ill matters greatly to you?",
                "क्या आपको लगता है कि आपके रोग का प्रबंध अपेक्षा से भिन्न रहा, अथवा बीमारी के दौरान आपको मिलने वाला ध्यान आपके लिए अत्यंत महत्वपूर्ण है?"),
            "scaleId": "fac22_sr",
            "sharedScale": "yes_no",
            "disorders": ["factitious_disorder", "somatic_symptom_disorder"],
        },
    ],
}


DISORDERS = {
    "somatic_symptom_disorder": {
        "name": en_hi("Somatic Symptom Disorder", "सोमेटिक लक्षण विकार"),
        "category": "somatic",
        "dsm5Code": "300.82 (F45.1)",
        "icd11Code": "6B41",
        "notes": en_hi(
            "PHQ-15 ≥ 10 (moderate-severe somatisation) supports the differential; the diagnosis "
            "requires distressing somatic symptoms plus excessive thoughts, feelings or behaviours about them.",
            "PHQ-15 ≥ 10 (मध्यम-गंभीर सोमटाइज़ेशन) विभेदी-सूची का समर्थन करता है; निर्णय के लिए क्लेशजनक शारीरिक लक्षण तथा उनके प्रति अत्यधिक विचार/भाव/व्यवहार आवश्यक।"),
        "instruments": ["PHQ-15"],
    },
    "conversion_disorder": {
        "name": en_hi("Functional Neurological Symptom Disorder (Conversion)",
                      "क्रियात्मक तंत्रिका-लक्षण विकार (कन्वर्ज़न)"),
        "category": "somatic",
        "dsm5Code": "300.11 (F44)",
        "icd11Code": "6B40",
        "notes": en_hi(
            "Neutral symptom description only — do not tell the patient the symptoms are 'not real'. "
            "MID-60 conversion subscales (body symptoms, pseudo-seizures) and PHQ-15 inform the differential.",
            "तटस्थ लक्षण-वर्णन करें — रोगी से कहें नहीं कि लक्षण 'असली' नहीं हैं। MID-60 कन्वर्ज़न उप-पैमाने एवं PHQ-15 विभेदी-सूची में सहायक।"),
        "instruments": ["PHQ-15", "MID-60"],
    },
    "factitious_disorder": {
        "name": en_hi("Factitious Disorder (imposed on self)", "छलरोग (स्व-आरोपित)"),
        "category": "somatic",
        "dsm5Code": "300.19 (F45.81)",
        "icd11Code": "6B42",
        "notes": en_hi(
            "FAC22-SR is a screen only. Diagnosis requires evidence of falsification/induction of symptoms "
            "with an identified deception motive of assuming the patient role, AND exclusion of external "
            "incentives (malingering). Never confront based on a score alone.",
            "FAC22-SR केवल स्क्रीन है। निर्णय हेतु लक्षण-रोपण/छल का प्रमाण एवं रोगी-भूमिका अपनाने की प्रेरणा आवश्यक, साथ ही बाह्य लाभ (मालिंगरिंग) का विवर्जन। केवल अंक के आधार पर कभी अभियुक्त न करें।"),
        "instruments": ["FAC22-SR"],
    },
}


