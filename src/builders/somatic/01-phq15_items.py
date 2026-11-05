PHQ15_ITEMS = [
    (1,  "Stomach pain", "पेट में दर्द"),
    (2,  "Back pain", "पीठ में दर्द"),
    (3,  "Pain in your arms or legs or other joints", "बाँहों या टाँगों या अन्य जोड़ों में दर्द"),
    (4,  "Menstrual cramps or other problems with your periods (women only)", "मासिक धर्म में ऐंठन या अन्य समस्याएँ (केवल महिलाएँ)"),
    (5,  "Headaches", "सिरदर्द"),
    (6,  "Chest pain", "छाती में दर्द"),
    (7,  "Dizziness", "चक्कर आना"),
    (8,  "Fainting spells", "बेहोशी के दौर"),
    (9,  "Feeling your heart pound or race", "दिल जोर से या तेज़ धड़कना"),
    (10, "Shortness of breath", "साँस कम पड़ना"),
    (11, "Pain or problems during sexual intercourse", "सहवास के दौरान दर्द या समस्या"),
    (12, "Constipation, loose bowels, or diarrhoea", "कब्ज़, ढीली दस्त या पतले मल"),
    (13, "Nausea, gas, or indigestion", "जी मचलाना, गैस या अपच"),
    (14, "Feeling tired, or having low energy", "थकान या ऊर्जा का अभाव"),
    (15, "Trouble sleeping", "नींद में समस्या"),
]

YESNO = [
    {"v": 1, "label": en_hi("Yes", "हाँ")},
    {"v": 0, "label": en_hi("No", "नहीं")},
]
TF = [
    {"v": 1, "label": en_hi("True", "सत्य")},
    {"v": 0, "label": en_hi("False", "मिथ्या")},
]
PHQ_OPTS = [
    {"v": 0, "label": en_hi("Not bothered at all", "बिल्कुल परेशान नहीं")},
    {"v": 1, "label": en_hi("Bothered a little", "थोड़ा परेशान")},
    {"v": 2, "label": en_hi("Bothered a lot", "बहुत परेशान")},
]


def build_fac22():
    qs = []
    for num, en, key in FAC22_ITEMS:
        q = {
            "id": "fac_%d" % num,
            "itemNumber": num,
            "text": en_hi(en, FAC22_HI.get(num, en)),
            "keyedAnswer": key,
        }
        if num == 22 or num == 8:
            q["criterionNote"] = en_hi(
                "self-prepared / heroic patient-role item", "स्व-तैयारी / नायक-रोगी-भूमिका आइटम")
        qs.append(q)
    return {
        "id": "fac22_sr",
        "name": en_hi("FAC22-SR — Factitious Disorder Symptom Scale (Self-Report)",
                      "FAC22-SR — छलरोग लक्षण मापनी (स्व-रिपोर्ट)"),
        "type": "matrix",
        "administeredBy": "self-report",
        "optionalAssessment": True,
        "sourceInstrument": "FAC22-SR",
        "targetAge": ["adult"],
        "directions": en_hi(
            "Please answer Yes or No to each statement. Do not skip any item. "
            "If you are not sure, choose the answer that is more likely to be correct. "
            "There is no time limit, but do not spend too long on any single statement.",
            "प्रत्येक कथन का हाँ या नहीं में उत्तर दें। कोई आइटम छोड़ें नहीं। यदि निश्चित नहीं हैं तो अधिक संभावित उत्तर चुनें। "
            "समय-सीमा नहीं है, किंतु किसी एक कथन पर अधिक समय व्यर्थ न करें।"),
        "timeframe": en_hi("Present pattern over recent illness experience.",
                           "वर्तमान रोग-अनुभव की समसामयिक पैटर्न।"),
        "parts": [{
            "id": "fac22_items",
            "name": en_hi("FAC22-SR items 1-22", "FAC22-SR आइटम 1-22"),
            "options": TF,
            "questions": qs,
        }],
        "matrixOptions": TF,
        "keyedScoring": True,
        "scoring": {
            "method": "fac22_sr_keyed_sum",
            "possibleThreshold": 9,
            "probableThreshold": 15,
            "maxKeyed": 22,
            "rule": en_hi(
                "Score 1 each for Yes to items 5, 8, 10, 11, 14-22, and No to items 1-4, 6, 7, 9, 12 and 13. "
                "A score of 9-14: possible factitious disorder; 15 or more: probable factitious disorder.",
                "आइटम 5, 8, 10, 11, 14-22 के 'हाँ' तथा आइटम 1-4, 6, 7, 9, 12, 13 के 'नहीं' उत्तर पर क्रमशः 1 अंक। "
                "9-14 अंक: संभव भत्रुण रोग (factitious); 15 या अधिक: संभावित भत्रुण रोग।"),
            "notDiagnostic": en_hi(
                "A screen only. Factitious disorder requires that deception for external gain (malingering) be excluded "
                "and that the presentation be established over time; this scale cannot make the diagnosis.",
                "यह केवल स्क्रीन है। भत्रुण रोग के लिए बाह्य लाभ हेतु छल (मालिंगरिंग) का विवर्जन आवश्यक है तथा प्रस्तुति कालक्रम में स्थापित हो; यह मापनी रोग-निर्णय नहीं कर सकती।"),
            "disorders": ["factitious_disorder", "somatic_symptom_disorder"],
        },
        "bands": [
            {"max": 8, "severity": en_hi("Below screen threshold", "स्क्रीन-सीमा से नीचे"), "key": "negative"},
            {"max": 14, "severity": en_hi("Possible factitious disorder", "संभव भत्रुण रोग"), "key": "possible"},
            {"max": 22, "severity": en_hi("Probable factitious disorder", "संभावित भत्रुण रोग"), "key": "probable"},
        ],
        "sourcePages": "Senthil & Prabhakar, J Evid Based Med Healthc 2019;6(21) — Table 7 (FAC22-SR scale) and scoring note",
        "translationNote": en_hi(
            "English wording is authoritative (repaired from the scanned table). Hindi labels are a working "
            "translation and must be proofread by a bilingual clinician before clinical use.",
            "अंग्रेज़ी पाठ प्रामाणिक है (स्कैन की गई तालिका से संशोधित)। हिन्दी अनुवाद कार्य-प्रगति पर है; नैदानिक प्रयोग से पूर्व द्विभाषी चिकित्सक से शुद्धि आवश्यक।"),
        "branching": None,
    }


