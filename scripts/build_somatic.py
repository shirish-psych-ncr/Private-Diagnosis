#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integrate the somatic-symptom / factitious-disorder material into data.json.

Adds, idempotently:

  scales.fac22_sr   FAC22-SR (Senthil & Prabhakar, 2019) — 22-item Yes/No
                    self-report screen for factitious disorder, keyed exactly
                    as printed ("Score 1 each for Yes to items 5, 8, 10, 11,
                    14-22, and No to items 1-4, 6, 7, 9, 12 and 13"; 9-14
                    possible FD, 15+ probable FD).
  scales.phq15      PHQ-15 — 15-item somatic symptom severity index (0/1/2),
                    cut-points 0-4 / 5-9 / 10-14 / 15+.
  domains.somatic   Tier-2 domain with two screen-in items that deploy the two
                    instruments through `instrument: "auto:somatoptable"`.
  disorders         somatic_symptom_disorder, factitious_disorder,
                    conversion_disorder (if absent).
  instruments       FAC22-SR and PHQ-15 library entries.
  reference.malingering   Non-scored clinical reference notes drawn from the
                    supplied forensic handbook extract (definitions, FD, Ganser,
                    malingered depression / hallucinations / delusions / amnesia,
                    and the pathway-to-violence table).

Run:  python3 scripts/build_somatic.py [--check]
"""
import json, sys, copy, io, os

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data.json')


def en_hi(en, hi):
    return {"en": en, "hi": hi}


# ---------------------------------------------------------------------------
# FAC22-SR item text (verbatim from Table 7; OCR artifacts repaired)
# keying: 'T' = a YES answer scores 1, 'F' = a NO answer scores 1
# ---------------------------------------------------------------------------
FAC22_ITEMS = [
    # (number, English stem, key)
    (1,  "With my physical symptoms, I affirm being referred for psychiatric counselling today.", 'F'),
    (2,  "I do agree that others find my symptoms atypical and unusually recurring.", 'F'),
    (3,  "I do think that because my symptoms are so mild/trivial, physicians often miss their significance and seriousness.", 'F'),
    (4,  "I would be happy if I can suddenly find myself sprightly healthy and strong.", 'F'),
    (5,  "I would be anxious if I find my family members had left for their work as/if I appear healthy to them.", 'T'),
    (6,  "It is just chance that people fail to notice or weren't around, every time when I experienced these symptoms.", 'F'),
    (7,  "I would pull myself up to help (with errands or earning) a family member more sick than me.", 'F'),
    (8,  "(If I had to play in a video game or a stage play) I would prefer portraying an injured warrior dying in bed, than one left unattended in battle.", 'T'),
    (9,  "I usually feel timid and offended when a stranger offers to help me.", 'F'),
    (10, "I am eager and brave enough to undergo painful bodily investigations.", 'T'),
    (11, "I would prefer crying or lamenting to a close friend, than crying alone.", 'T'),
    (12, "I feel giddy or immobilised often when I get emotional when alone.", 'F'),
    (13, "I would feel ashamed if people find about my physical illness.", 'F'),
    (14, "I often get gloomy, unsatisfied or irritable on the day of my discharge from hospital.", 'T'),
    (15, "I might not have accessed the physician but for the erratic concern shown by my family members/friend(s).", 'T'),
    (16, "I find my clinical tests and lab investigations done too casually to get any positive result.", 'T'),
    (17, "I feel unsatisfied and deprived when the health professionals show lesser than usual interest in talking with me.", 'T'),
    (18, "I understand that people with my symptoms may or may not be hearing voices when alone, either transiently or regularly. I hear such voices too.", 'T'),
    (19, "I understand that people with my symptoms may or may not have visual loss, either momentarily or regularly. I have had visual loss too.", 'T'),
    (20, "I understand that people with my symptoms may or may not have weakness/abnormal movements of one or more limbs, either momentarily or continuously. I have had such weakness/abnormal movements too.", 'T'),
    (21, "I have encountered interesting adventures that had been brilliant and wonderful, and/or a series of heartbreaking tragic events including multiple personal crises - many times victimizing me.", 'T'),
    (22, "Wherever I go, many a time I have had the pleasure of playing a hero/heroine of those circumstances and had been wondered at and hailed as a saviour by the people there.", 'T'),
]

# Hindi renderings are working translations pending proofreading by a
# bilingual clinician (flagged in translationNote).
FAC22_HI = {
    1: "अपने शारीरिक लक्षणों के साथ, आज मुझे मनोचिकित्सकीय परामर्श हेतु भेजे जाने में मैं सहमत हूँ।",
    2: "मैं स्वीकार करता/करती हूँ कि अन्य लोगों को मेरे लक्षण असामान्य एवं बारम्बार लगते हैं।",
    3: "मुझे लगता है कि मेरे लक्षण अत्यंत तुच्छ होने के कारण चिकित्सक अक्सर उनके महत्व एवं गंभीरता को उपेक्षित कर देते हैं।",
    4: "यदि मैं अचानक पूर्णतः स्वस्थ व बलिष्ठ पाऊँ तो मुझे प्रसन्नता होगी।",
    5: "यदि मुझे दिखने में स्वस्थ पाकर मेरे परिवारजन कार्य हेतु चले जाएँ तो मुझे चिंता होगी।",
    6: "यह केवल संयोग है कि हर बार इन लक्षणों के अनुभव के समय लोग मौजूद नहीं थे या उन्होंने ध्यान नहीं दिया।",
    7: "मुझसे अधिक बीमार परिवार-सदस्य की सहायता (कार्यों या कमाई में) के लिए मैं खुद को उठा लाऊँगा/उठा लाऊँगी।",
    8: "(यदि मुझे किसी वीडियो गेम या रंगमंच में भाग लेना हो) तो मैं शয्ये पर मरता हुआ घायल योद्धा की भूमिका करने को मैं युद्धभूमि में अनदेखा किए गए सैनिक के रूप निभाने से अधिक प्रिय मानूँगा/मानूँगी।",
    9: "जब कोई अपरिचित व्यक्ति सहायता की पेशकश करता है तो मैं सामान्यतः संकोची एवं आहत महसूस करता/करती हूँ।",
    10: "पीड़ादायक शारीरिक जाँचों से गुज़रने के लिए मैं उत्सुक एवं साहसी हूँ।",
    11: "अकेले रोने के बजाय किसी निकट मित्र से रोना या विलाप करना मुझे अधिक अधिक प्रिय लगता है।",
    12: "अकेले भावुक होते ही प्रायः मुझे चक्कर आता है या मैं स्तब्ध हो जाता/जाती हूँ।",
    13: "यदि लोग मेरी शारीरिक बीमारी के बारे में जान लें तो मुझे लज्जा आएगी।",
    14: "अस्पताल से छुट्टी के दिन मैं प्रायः विषण्ण, असंतुष्ट या चिड़चिड़ा हो जाता/हो जाती हूँ।",
    15: "परिवारजनों/मित्रों द्वारा दिखाई गई उलटी-सीधी चिंता न होती तो शायद मैं चिकित्सक के पास न जाता/जाती।",
    16: "मुझे लगता है कि मेरे नैदानिक परीक्षण एवं जाँचें इतनी सावधानी-विहीन ढंग से की जाती हैं कि उनसे सकारात्मक परिणाम नहीं मिलता।",
    17: "स्वास्थ्य-विशेषज्ञों द्वारा मेरी बातचीत में अपेक्षाकृत कम रुचि दिखाने पर मैं असंतुष्ट एवं वंचित महसूस करता/करती हूँ।",
    18: "मुझे ज्ञात है कि मेरे जैसे लक्षण वाले लोग एकान्त में आवाज़ें सुन सकते हैं या नहीं, क्षणिक या नियमित। मुझे भी ऐसी आवाज़ें सुनाई देती हैं।",
    19: "मुझे ज्ञात है कि मेरे जैसे लक्षण वाले लोगों को क्षणिक या नियमित दृष्टि-हानि हो सकती है। मुझे भी दृष्टि-हानि हुई है।",
    20: "मुझे ज्ञात है कि मेरे जैसे लक्षण वाले एक या अधिक अंगों में क्षणिक या सतत दुर्बलता/असामान्य गतियाँ हो सकती हैं। मुझे भी ऐसी दुर्बलता/असामान्य गतियाँ हुई हैं।",
    21: "मेरे जीवन में रोमांचक, दिव्य अनुभव भी रहे हैं और हृदयविदारक श्रृंखलाबद्ध दुर्घटनाएँ भी — जिनमें अनेक बार मैं पीड़ित बना।",
    22: "जहाँ-जहाँ मैं गया/गई, अनेक बार मैं उन परिस्थितियों का नायक/नायिका बनकर सबका ध्यान आकर्षित करता/करती रहा/रही और लोगों ने मुझे तारीफ़ की।",
}

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


REFERENCE = {
    "id": "malingering_reference",
    "name": en_hi("Forensic reference: malingering, feigning & suspect effort",
                  "फॉरेंसिक संदर्भ: मालिंगरिंग, छल-अभिनय एवं संदेहजनक प्रयास"),
    "nonScored": True,
    "clinicianOnly": True,
    "source": "Supplied forensic-handbook extract (res ipsa / malingering evaluation notes)",
    "sections": [
        {
            "id": "definitions",
            "title": en_hi("Key definitions", "मुख्य परिभाषाएँ"),
            "items": [
                en_hi("Malingering (DSM-5): intentional production of false or grossly exaggerated physical or "
                      "psychological symptoms motivated by external incentives — avoiding military duty, avoiding "
                      "work, obtaining financial compensation, evading criminal prosecution, obtaining drugs.",
                      "मालिंगरिंग (DSM-5): बाह्य प्रलोभन (सैनिक सेवा से बचाव, कार्य से बचाव, आर्थिक क्षतिपूर्ति, दंड से बचाव, मादक द्रव्य प्राप्ति) हेतु शारीरिक/मानसिक लक्षणों का जानबूझकर मिथ्या या अत्यधिक वर्धन।"),
                en_hi("Feigning: deliberate fabrication or gross exaggeration of symptoms without assumptions about its goals (Rogers & Bender, 2003).",
                      "छल-अभिनय: लक्ष्य संबंधी पूर्वधारणा के बिना लक्षणों का जानबूझकर निर्माण या अत्यधिक वर्धन (Rogers & Bender, 2003)।"),
                en_hi("Suspect effort: effort-test performance suggesting the examinee is not applying best effort; may be intentional or non-intentional (also suboptimal/incomplete/submaximal effort).",
                      "संदेहजनक प्रयास: परीक्षार्थी द्वारा सर्वोत्तम प्रयास न लगाने का संकेत; सचेत या असचेत हो सकता है (उप-इष्टतम/अपूर्ण/उप-अधिकतम प्रयास)।"),
                en_hi("Factitious disorder: voluntary production of symptoms to assume the patient role, with no other obvious secondary gain.",
                      "छलरोग: रोगी-भूमिका अपनाने हेतु लक्षणों की स्वेच्छा-उत्पत्ति,अन्य कोई सुगम्य द्वितीयक लाभ के बिना।"),
                en_hi("Ganser syndrome: approximate answers (2+2=5), clouding of consciousness, somatic conversion (especially sensory), hallucinations.",
                      "गैंसर सिंड्रोम: अनुमानोत्तर (2+2=5), चेतना की मंदता, शारीरिक कन्वर्ज़न (विशेषतः संवेदी), एवं Hallucination।"),
            ],
        },
        {
            "id": "depression",
            "title": en_hi("Evaluating possible malingered depression", "संभावित वर्धित अवसाद का मूल्यांकन"),
            "items": [
                en_hi("Gervais et al. (2001): 25-30% of civil-litigation claimants of major depression probably malingered on forced-choice testing.",
                      "Gervais आदि (2001): दीवानी वादों में प्रस्तावित प्रमुख अवसाद के 25-30% दाता संभवतः फोर्सड-चॉइस परीक्षण पर मालिंगरिंग कर रहे थे।"),
                en_hi("Review DSM-5 criteria first; then weigh inconsistency between reported state and observed behaviour: full range of facial expression, normal motor activity, laughing/joking, enjoyment of activities, no verifiable weight change, indiscriminate endorsement of unrelated symptoms, laudatory self-presentation, blame of others, poor performance on very easy personal questions, sudden worsening once told they will be 'tested', mood change when observed vs unobserved.",
                      "प्रथम DSM-5 मानदंड देखें; फिर वर्णित अवस्था एवं प्रत्यक्ष व्यवहार की विसंगति पर विचार: भाव-अभिव्यक्ति का पूर्ण विस्तार, सामान्य मोटर क्रिया, हँसी-मज़ाक, कार्यों में रूचि, वजन-परिवर्तन का अप्रमाणित, असंबंधित लक्षणों का अंधाधुंध समर्थन, स्व-प्रशंसा, दूसरों पर दोषारोपण, अत्यंत सरल व्यक्तिगत प्रश्नों पर खराब प्रदर्शन, 'परीक्षण' बताते ही स्मरण/एकाग्रता का आकस्मिक अवमदन, प्रेक्षित अप्रत्यक्ष अवस्था में अंतर।"),
            ],
        },
        {
            "id": "hallucinations",
            "title": en_hi("Malingered versus true hallucinations", "छल-अभिनयित एवं वास्तविक Hallucination"),
            "items": [
                en_hi("Start open-ended ('Describe what you are hearing. Is there anything else you can describe?'); avoid educating the evaluee about expected signs — 'clinician assisted deception'.",
                      "प्रथम खुले प्रश्न ('जो सुनाई दे उसका वर्णन करें। और कुछ?'); अपेक्षित लक्षणों की शिक्षा न दें — इसे 'चिकित्सक-सहायताप्राप्त छल' कहते हैं।"),
                en_hi("Phenomenology to document: content, clarity, loudness, vividness, duration, frequency, continuous/intermittent, single/multiple voices, gender, inside/outside the head, tone, person addressed, insight, belief others can hear, relationship to speaker, other sensory modalities, alone/with others, conversing back, ability to dismiss, mood, relation to delusions, confusion, reaction, commands, consequences of disobeying, effort not to obey, alternative motives, what worsens/improves, number of voices.",
                      "अभिलिखित घटना-विज्ञान: विषय, स्पष्टता, प्रबलता, व्यक्तता, काल, आवृत्ति, सतत/विविक्त, एक/अनेक स्वर, लिंग, मस्तिष्क के अंतः/बहिः, ध्वनि-स्वर, संबोधन, अंतर्दृष्टि, अन्यको श्रवण-विश्वास, वक्ता-संबंध, अन्य इंद्रिय-द्वारा, एकांत/समूह, उत्तर-दान, निवारण-समर्थता, भाव, भ्रम-संबंध, विषमता, प्रतिक्रिया, आदेश, अवमान्यता के परिणाम, अवमान्य इच्छा, वैकल्पिक प्रेरणा, वर्धन-हेतु, संख्या।"),
                en_hi("In genuine psychosis voices are usually intermittent; Nayani & David (1996): 49% external, 38% internal, 12% both; abuse the commonest content; 76% identify at least one coping strategy (working, posture change, interpersonal contact, medication); being alone worsens voices in 80%, radio/TV worsen them.",
                      "वास्तविक मनोविकृति में स्वर प्रायः विविक्त; Nayani और David (1996): 49% बाह्य, 38% आंतरिक, 12% उभय; गाली सबसे सामान्य; 76% कम-से-कम एक सामना-रणनीति बताते हैं (कार्य, मुद्रा-परिवर्तन, संपर्क, औषधि); 80% में एकांत से वृद्धि, रेडियो/टीवी से भी वर्धन।"),
                en_hi("Suspect auditory hallucinations: continuous rather than intermittent, vague/inaudible, not associated with delusions, stilted language, no strategies to diminish voices, claim that all commands are obeyed.",
                      "संदेहजनक श्रवण-भ्रम: सतत बजाय विविक्त, अस्पष्ट/अश्रव्य, भ्रम से असंबद्ध, कृत्रिम भाषा, स्वर-निवारण की कोई रणनीति नहीं, समस्त आदेश-पालन का दावा।"),
                en_hi("Suspect visual hallucinations: visual alone in schizophrenia, black-and-white, dramatic/atypical, changing with eyes closed, miniature or giant figures, visions unrelated to delusions or auditory hallucinations. (Visual hallucinations were found in 46% of malingerers vs 4% of genuinely psychotic individuals; drug-induced visual phenomena are typically formed with eyes closed.)",
                      "संदेहजनक दृष्टि-भ्रम: स्किज़ोफ्रेनिया में केवल दृष्टि, श्वेत-श्याम, नाटकीय/असामान्य, नेत्र-बंद करने पर परिवर्तन, लीलिपुटियन/विराट आकृतियाँ, भ्रम-असंबद्ध दर्शन। (मालिंगरेटर्स में 46% बनाम वास्तविक मनोविकृतों में 4% दृष्टि-भ्रम; मादक-प्रेरित दृष्टि-घटनाएँ प्रायः नेत्र-बंद अवस्था में।)"),
            ],
        },
        {
            "id": "delusions",
            "title": en_hi("Malingered versus true delusions", "छल-अभिनयित एवं वास्तविक भ्रम"),
            "items": [
                en_hi("Delusion: a fixed false belief held in an inappropriate context with inappropriate justification.",
                      "भ्रम: अपोचित संदर्भ एवं अपोचित उचितकरण के साथ स्थिर मिथ्या विश्वास।"),
                en_hi("Common themes: disease, nihilism/poverty/sin/guilt, grandiosity, jealousy, erotomania, persecution, reference, religion, poisoning, possession, royal descent, delusional parasitosis, Capgras syndrome.",
                      "सामान्य विषय: रोग, शून्यता/दरिद्रता/पाप/अपराध-भाव, वैभवंशा, ईर्ष्या, प्रणय-भ्रम, उत्पीड़न, संदर्भ, धर्म, विष-प्रयोग, ग्रहण, राजवंश-वंशज, भ्रामक परजीविता, कैपग्रस।"),
                en_hi("Clues to malingered delusions: abrupt onset or termination, eagerness to call attention to the delusion, conduct inconsistent with the delusion, bizarre content without disordered thought, delusions paired with exaggerated cognitive deficit.",
                      "छल-संकेत: आकस्मिक आरंभ/अंत, भ्रम पर ध्यान खींचने की उत्सुकता, भ्रम-असंगत व्यवहार, विचार-विकृति के बिना विचित्र विषय, अतिरंजित संज्ञान-क्षति के साथ भ्रम।"),
            ],
        },
        {
            "id": "amnesia",
            "title": en_hi("Claimed amnesia: forensic review", "दावा-कृत स्मृतिलोप: फॉरेंसिक समीक्षा"),
            "items": [
                en_hi("First clarify that the complaint is amnesia rather than dementia/delirium/developmental memory difficulty; a memory evaluation covers orientation, recall of prose, rote learning, visuospatial retention, remote memory/fund of information and autobiographical memory, with medical work-up (labs, neuro exam, imaging) as indicated.",
                      "प्रथम स्पष्ट करें कि शिकायत स्मृतिलोप है, मूर्छा/डीमेंशिया/विकास-जनित स्मरण-कठिनाई नहीं; मूल्यांकन में दिशा-काल ज्ञान, गद्य-स्मरण, रट-अध्ययन, दृश्य-स्थानिक धारणा, सुदूर स्मरण/सूचना-भंडार एवं आत्मकथात्मक स्मरण, तथा आवश्यक चिकित्सीय जाँच।"),
                en_hi("Organic causes to consider: substance use, anterior communicating artery aneurysm rupture, anoxia, brain disease/injury, cerebrovascular accident, delirium, dementia, ECT, encephalitis, hypoglycaemia, somnambulism, transient epileptic amnesia, Wernicke-Korsakoff syndrome.",
                      "कारणात्मक जैविक कारण: मादक द्रव्य, ACoA एनेवरिज्म भंग, अनॉक्सिया, मस्तिष्क रोग/आघात, CVA, delirium, डीमेंशिया, ECT, एन्सेफलाइटिस, हाइपोग्लाइसीमिया, स्लीप-वॉकिंग, क्षणिक मृगवानीय स्मृतिलोप, Wernicke-Korsakoff।"),
                en_hi("Ribot's law: after head trauma older memories return before recent ones, with the gap limited to the event and seconds beforehand; recovery that does not follow this pattern warrants screening for malingering.",
                      "राइबोट-नियम: मस्तिष्क-आघात पश्चात् पुरानी स्मृतियाँ नवीन से पूर्व लौटती हैं, अंतराल घटना एवं उसके कुछ क्षण पूर्व तक सीमित; इस पैटर्न से हटने वाली पुनर्प्राप्ति पर मालिंगरिंग-स्क्रीन आवश्यक।"),
                en_hi("Patterns consistent with malingered amnesia: circumscribed loss for the offence with recall before and after; sharp sudden onset and offset; complete loss for a circumscribed period (complete amnesia for a criminal act is very rare); dogmatic belief that nothing could aid recovery; overly dramatic presentation; implausibly precise time window; attributing amnesia to intoxication contrary to available evidence.",
                      "मालिंगरिंग-संगत पैटर्न: केवल अपराध-काल की सीमित हानि, पूर्व-पश्चात् स्मरण; आकस्मिक आरंभ-अंत; सीमित काल का पूर्ण लोप (अपराध का पूर्ण अमांसिया अत्यंत दुर्लभ); किसी सहायता से स्मरण-पुनर्प्राप्ति का अडंबरहीन अविश्वास; अत्यंत नाटकीय प्रस्तुति; अविश्वसनीय रूप से सटीक समय-सीमा; प्रमाण-विरुद्ध मतवैषम्य को हेतु बताना।"),
                en_hi("Alcohol/substance claims: over half (and in some studies >85%) of offenders claiming amnesia were intoxicated near the offence, but intoxication sufficient to produce genuine amnesia is uncommon — do not accept the claim without corroborating levels/evidence.",
                      "मदिरा/मादक दावे: अमांसिया-दाता अपराधियों में अर्धे से अधिक (कुछ अध्ययनों में >85%) नशे में थे, किंतु वास्तविक अमांसिया उत्पन्न करने योग्य मात्रा दुर्लभ — प्रमाण-राशि के बिना दावा स्वीकार न करें।"),
                en_hi("Planning matters: instrumental (planned) offences involve elaborative encoding and rehearsal, which improve memory, so genuine amnesia for planned violence is unexpected; impulsive/reactive offences may be followed by partial retrograde gaps.",
                      "योजना-प्रसंग: सयोजित (योजनाबद्ध) अपराधों में विस्तृत एनकोडिंग-अभ्यास स्मरण बढ़ाता है, अतः योजनाबद्ध हिंसा का वास्तविक अमांसिया अप्रत्याशित; आवेगजनित अपराधों में आंशिक पश्चगामी अंतराल संभव।"),
                en_hi("Self-report dissociation instruments (DES/DES-II, MID) rely entirely on self-report: a high score does not prove claimed memory loss is genuine (McLeod 2004; Woodworth 2009 — DES tendency correlated with perceived, not objective, memory impairment).",
                      "स्व-रिपोर्ट वियोजन मापनियाँ (DES/DES-II, MID) पूर्णतः स्व-रिपोर्ट पर निर्भर: उच्च अंक दावा-कृत स्मृतिलोप की प्रामाणिकता सिद्ध नहीं करता (McLeod 2004; Woodworth 2009)।"),
            ],
        },
        {
            "id": "pathway",
            "title": en_hi("Pathway to homicidal violence (Calhoun & Weston 2003; steps 7-8 per Christianson et al. 2007)",
                          "हत्याकांड-हेतु हिंसा की पथ-रेखा (Calhoun और Weston 2003; चरण 7-8 Christianson आदि 2007)"),
            "items": [
                en_hi("Step 1 Grievance — anger, revenge, feeling wronged.", "चरण 1 शिकायत — क्रोध, प्रतिशोध, अन्याय-भाव।"),
                en_hi("Step 2 Ideation — accepting violence to right the wrong or fulfil violent/sexual fantasies; identifying with other assailants.", "चरण 2 विचारधारा — अन्याय-सुधार या हिंसक/यौन कल्पना हेतु हिंसा स्वीकार; अन्य आक्रमणकारियों से तादात्म्य।"),
                en_hi("Step 3 Research and planning — gathering information, inquiring about the target, surveillance.", "चरण 3 अनुसंधान-योजना — सूचना-संग्रह, लक्ष्य-पूछताछ, निगरानी।"),
                en_hi("Step 4 Preparations — assembling equipment, practising, choosing clothing, writing messages, making a will.", "चरण 4 पूर्वतैयारी — उपकरण-संग्रह, अभ्यास, वस्त्र-चयन, संदेश-लेखन, वसीयत।"),
                en_hi("Step 5 Breach — positioning oneself close to the potential victim.", "चरण 5 प्रवेश — संभावित शिकार के निकट स्थितिग्रहण।"),
                en_hi("Step 6 Attack — enacting the plan, requiring commitment and resolve.", "चरण 6 आक्रमण — योजना-क्रियान्वयन, संकल्प-आवश्यकता।"),
                en_hi("Step 7 Realisation — actions upon the victim's body, additional violence or sexual acts.", "चरण 7 साक्षात्कार — शरीर पर क्रियाएँ, अतिरिक्त हिंसा/यौन कृत्य।"),
                en_hi("Step 8 Post-crime behaviour — behaviours aimed at avoiding discovery or staging the scene.", "चरण 8 अपराधोत्तर व्यवहार — पकड़े जाने से बचाव अथवा घटना-स्थल की रचना।"),
            ],
        },
    ],
}


def main():
    check = '--check' in sys.argv
    with io.open(DATA, encoding='utf-8') as fh:
        d = json.load(fh)
    orig = copy.deepcopy(d)

    d.setdefault('scales', {})
    d['scales']['fac22_sr'] = build_fac22()
    d['scales']['phq15'] = build_phq15()

    ids = [dom['id'] for dom in d['domains']]
    if 'somatic' in ids:
        d['domains'][ids.index('somatic')] = SOMATIC_DOMAIN
    else:
        # keep the tier ordering readable: place after the other tier-2 screens
        pos = len(d['domains'])
        for i, dom in enumerate(d['domains']):
            if dom.get('tier', 1) >= 4:
                pos = i
                break
        d['domains'].insert(pos, SOMATIC_DOMAIN)

    d.setdefault('disorders', {})
    for k, v in DISORDERS.items():
        d['disorders'][k] = v

    d.setdefault('instruments', {})
    d['instruments']['FAC22-SR'] = {
        "name": "FAC22-SR (Factitious Disorder Symptom Scale, self-report)",
        "construct": en_hi("Factitious disorder screening", "छलरोग स्क्रीनिंग"),
        "format": en_hi("22 Yes/No items, keyed; 9-14 possible, 15+ probable",
                        "22 हाँ/नहीं आइटम, keyed; 9-14 संभव, 15+ संभावित"),
        "duration": "~5 min",
        "language": en_hi("English (authoritative), Hindi working translation",
                          "अंग्रेज़ी (प्रामाणिक), हिन्दी कार्य-अनुवाद"),
        "purpose": en_hi(
            "Screen for factitious disorder in patients with medically unexplained symptoms. Not diagnostic; "
            "must be combined with record review and exclusion of malingering.",
            "अस्पष्टीकृत शारीरिक लक्षण वाले रोगियों में छलरोग की स्क्रीनिंग। रोग-निर्णायक नहीं; रिकॉर्ड-समीक्षा एवं मालिंगरिंग-विवर्जन के साथ उपयोग।"),
        "source": "Senthil & Prabhakar, J Evid Based Med Healthc 2019;6(21) Table 7",
        "licensing": en_hi("Published research instrument (open-access journal article); verify reuse terms.",
                           "प्रकाशित अनुसंधान-मापनी (open-access); पुनरुपयोग-शर्ताएँ सत्यापित करें।"),
    }
    d['instruments']['PHQ-15'] = {
        "name": "PHQ-15 (Patient Health Questionnaire — Somatic Symptoms)",
        "construct": en_hi("Somatic symptom severity", "शारीरिक लक्षण तीव्रता"),
        "format": en_hi("15 items scored 0-2 over 4 weeks (0-30)",
                        "15 आइटम, 4 सप्ताह, 0-2 अंकन (0-30)"),
        "duration": "~3 min",
        "language": en_hi("English, Hindi", "अंग्रेज़ी, हिन्दी"),
        "purpose": en_hi(
            "Quantify somatic symptom burden; supplements clinical judgement (cut-points 5 / 10 / 15).",
            "शारीरिक लक्षण-भार का परिमाणीकरण; चिकित्सकीय निर्णय की सहायता (सीमा 5 / 10 / 15)।"),
        "source": "PHQ-15 (Kroenke, Spitzer & Williams); free to use, no permission required",
        "licensing": en_hi("Public-domain PHQ family instrument.", "PHQ परिवार की सार्वजनिक-उपयोग मापनी।"),
    }

    d.setdefault('reference', {})
    d['reference']['malingering'] = REFERENCE

    meta = d.setdefault('meta', {})
    meta['schemaVersion'] = '2.6.0'
    meta['updated'] = '2026-11-04'
    notes = meta.setdefault('instrumentNotes', [])
    fac_note = ("FAC22-SR: added from the published scale table (Senthil & Prabhakar, J Evid Based Med "
                "Healthc 2019;6(21) Table 7). English wording is authoritative and was repaired from the "
                "scan; Hindi labels are a working translation awaiting bilingual-clinician proofreading. "
                "Keying verified at build time: Yes to 5, 8, 10, 11, 14-22 and No to 1-4, 6, 7, 9, 12, 13 "
                "= 22 items. Screening only - never diagnostic; factitious disorder additionally requires "
                "exclusion of malingering (see reference.malingering).")
    phq_note = ("PHQ-15: 15-item somatic symptom severity index (0-2 each, total 0-30) added as a tier-2 "
                "optional screen reached from the `somatic` domain; bands follow the printed cut-points "
                "0-4 / 5-9 / 10-14 / 15+. Severity measure that supplements clinical judgement.")
    if fac_note not in notes:
        notes.append(fac_note)
    if phq_note not in notes:
        notes.append(phq_note)

    if check:
        assert json.dumps(d, sort_keys=True) != json.dumps(orig, sort_keys=True), 'no change applied'
        print('build_somatic: --check OK (would write schema %s)' % meta['schemaVersion'])
        return

    with io.open(DATA, 'w', encoding='utf-8') as fh:
        json.dump(d, fh, ensure_ascii=False, indent=2)
        fh.write('\n')

    fac = d['scales']['fac22_sr']
    phq = d['scales']['phq15']
    yes_items = sorted(q['itemNumber'] for q in fac['parts'][0]['questions'] if q['keyedAnswer'] == 'T')
    no_items = sorted(q['itemNumber'] for q in fac['parts'][0]['questions'] if q['keyedAnswer'] == 'F')
    print('wrote data.json schema', meta['schemaVersion'],
          '| FAC22 items:', len(fac['parts'][0]['questions']),
          '| Yes-keyed:', yes_items,
          '| No-keyed:', no_items,
          '| PHQ-15 items:', len(phq['parts'][0]['questions']),
          '| domains:', [x['id'] for x in d['domains']],
          '| reference sections:', len(REFERENCE['sections']))


if __name__ == '__main__':
    main()
