#!/usr/bin/env python3
"""
Add the Gender Congruence and Life Satisfaction Scale (GCLS) to data.json.

The GCLS is a 38-item self-report measure of gender-related distress, gender
incongruence and life satisfaction, rated NEVER / RARELY / SOMETIMES / OFTEN /
ALWAYS over the past 6 months, plus one non-scored tick-box recording whether
genital surgery has already been carried out.

This script is idempotent: it rewrites only the `gcls` scale, the `gender`
domain, the two GCLS disorder keys, the instrument-library entry and the meta
notes. Run with --check for a dry run.

    python3 scripts/build_gcls.py [--check]
"""
import json
import sys
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data.json"
SCHEMA_TARGET = "2.7.0"

# --------------------------------------------------------------------------
# Item text — verbatim from the printed scale. `key` is the scored direction:
#   'D'  distress/incongruence item (higher = more distress/incongruence)
#   'C'  congruence item (higher = MORE congruent, therefore reverse-scored)
#   'S'  life-satisfaction item (higher = more satisfied; NOT part of the
#        distress subscales — reported as its own satisfaction register)
#   'R'  satisfaction item worded negatively (reverse-scored within satisfaction)
# --------------------------------------------------------------------------
ITEMS = [
    # --- Part 1: functional impact of gender-related distress (items 1-13) ---
    (1,  'D', 'I have avoided social situations and/or social interactions.',
         'मैंने सामाजिक परिस्थितियों और/अथवा सामाजिक संपर्कों से परहेज़ किया है।'),
    (2,  'D', 'I have not gone to school/college/work.',
         'मैं स्कूल/महाविद्यालय/कार्यस्थल नहीं गया/गई हूँ।'),
    (3,  'D', 'I have not been able to have emotional relationships with other people.',
         'मैं दूसरे लोगों के साथ भावनात्मक संबंध नहीं बना पाया/पाई।'),
    (4,  'D', 'I have suffered from anxiety.',
         'मुझे चिंता का सामना करना पड़ा है।'),
    (5,  'D', 'I have not been able to be physically intimate with other people.',
         'मैं दूसरे लोगों के साथ शारीरिक रूप से निकट नहीं हो पाया/पाई।'),
    (6,  'D', 'I have been unable to leave the house.',
         'मैं घर से बाहर नहीं जा पाया/पाई।'),
    (7,  'D', 'I have found it difficult to make friends.',
         'मुझे मित्र बनाने में कठिनाई हुई है।'),
    (8,  'D', 'I have thought about cutting or hurting my chest, genitals, and/or surrounding areas.',
         'मुझे अपने वक्ष, जननांगों और/अथवा आस-पास के अंगों को काटने या क्षति पहुँचाने का विचार आया है।', True),
    (9,  'D', 'I have felt that life is meaningless.',
         'मुझे लगा कि जीवन निरर्थक है।'),
    (10, 'D', 'I have not enjoyed life.',
         'मैं जीवन का आनंद नहीं ले पाया/पाई।'),
    (11, 'D', 'I have not engaged in leisure activities.',
         'मैं अवकाश गतिविधियों में शामिल नहीं हुआ/हुई।'),
    (12, 'D', 'I have suffered from low mood.',
         'मेरा मूद उदासीन रहा है।'),
    (13, 'D', 'I have thought about hurting myself or taking my own life.',
         'मुझे स्वयं को क्षति पहुँचाने या आत्महत्या करने का विचार आया है।', True),
    # --- Part 2: gender incongruence / body distress (items 14-30) ---
    (14, 'D', 'I have felt distressed when touching my genitals as they do not match my gender identity.',
         'जननांगों को स्पर्श करने पर मुझे कष्ट हुआ क्योंकि वे मेरी लिंग-पहचान से मेल नहीं खाते।'),
    (15, 'D', 'I have felt so distressed about my chest that I have not been able to have a fulfilling life.',
         'अपने वक्ष को लेकर इतना कष्ट अनुभव किया कि मैं संतुष्टिपूर्ण जीवन नहीं जी पाया/पाई।'),
    (16, 'C', 'I have felt comfortable with how others have perceived my gender.',
         'मुझे यह सुखद लगा कि दूसरों ने मेरे लिंग को कैसे देखा/पहचाना।'),
    (17, 'D', 'I have felt that my body hair conflicts with my gender identity, either because I have it and do not like it or because I would like to have it.',
         'मुझे लगा कि मेरे शरीर के बाल मेरी लिंग-पहचान से टकराते हैं — चाहे वे हों और अप्रिय हों, या मैं उन्हें चाहता/चाहती हूँ।'),
    (18, 'D', 'I have felt like my chest does not match my gender identity.',
         'मुझे लगा कि मेरा वक्ष मेरी लिंग-पहचान से मेल नहीं खाता।'),
    (19, 'D', 'I have found it distressing that others do not address me according to my gender identity.',
         'मुझे कष्ट हुआ कि दूसरे मुझे मेरी लिंग-पहचान के अनुसार नहीं संबोधित करते।'),
    (20, 'C', 'I have felt satisfied with the pronouns that others use when talking about me.',
         'मुझे उन सर्वनामों से संतुष्टि महसूस हुई जो दूसरे मेरे बारे में बात करते समय प्रयोग करते हैं।'),
    (21, 'D', 'I have felt unhappy about my genitalia since they do not match my gender identity.',
         'मेरे जननांग मेरी लिंग-पहचान से मेल नहीं खाते, इसलिए मैं उनसे असुखी रहा/रही।'),
    (22, 'C', 'I have felt comfortable with how other people perceive my gender based on my physical appearance.',
         'मुझे सुखद लगा कि मेरे बाह्य स्वरूप के आधार पर दूसरे मेरे लिंग को जिस तरह देखते हैं वैसा ठीक है।'),
    (23, 'D', 'I have felt that my voice has affected the way other people have perceived my gender identity which has been distressing for me.',
         'मुझे लगा कि मेरी आवाज़ ने दूसरों की मेरी लिंग-पहचान की धारणा को प्रभावित किया, जिससे कष्ट हुआ।'),
    (24, 'D', 'I have felt that my facial hair conflicts with my gender identity, either because I have it and do not like it or because I would like to have it.',
         'मुझे लगा कि मेरे चेहरे के बाल मेरी लिंग-पहचान से टकराते हैं — चाहे वे हों और अप्रिय हों, या मैं उन्हें चाहता/चाहती हूँ।'),
    (25, 'C', 'I have felt that my genitals do match with my gender identity.',  # congruence -> reverse-scored
         'मुझे लगा कि मेरे जननांग मेरी लिंग-पहचान से मेल खाते हैं।'),
    (26, 'D', 'I have felt that genital surgery will address the unhappiness I experience in relation to my gender.',
         'मुझे लगा कि जननांग-शस्त्रक्रिया मेरे लिंग से जुड़े असुख को दूर कर सकेगी।'),
    (27, 'D', 'I have been unable to have a fulfilling life because of the distress relating to my genitalia.',
         'मेरे जननांगों से जुड़े कष्ट के कारण मैं संतुष्टिपूर्ण जीवन नहीं जी पाया/पाई।'),
    (28, 'D', 'I have felt extremely distressed when looking at my chest.',
         'अपना वक्ष देखकर मुझे अत्यंत कष्ट हुआ।'),
    (29, 'D', 'I have felt extremely distressed when looking at my genitals.',
         'अपने जननांग देखकर मुझे अत्यंत कष्ट हुआ।'),
    (30, 'C', 'I have felt satisfied with my chest.',
         'मुझे अपने वक्ष से संतुष्टि महसूस हुई।'),
    # --- Part 3: life satisfaction (items 31-38) ---
    (31, 'S', 'I have felt satisfied at school/college/work.',
         'मुझे स्कूल/महाविद्यालय/कार्यस्थल में संतुष्टि महसूस हुई।'),
    (32, 'S', 'I have felt satisfied with my emotional relationship(s).',
         'मुझे अपने भावनात्मक संबंधों/संबंध से संतुष्टि महसूस हुई।'),
    (33, 'S', 'I have felt satisfied with my sex life.',
         'मुझे अपने यौन जीवन से संतुष्टि महसूस हुई।'),
    (34, 'S', 'I have felt satisfied in my leisure activities and hobbies.',
         'मुझे अपनी अवकाश गतिविधियों और शौकों से संतुष्टि महसूस हुई।'),
    (35, 'R', 'I have not felt satisfied with my friends.',
         'मुझे अपने मित्रों से संतुष्टि महसूस नहीं हुई।'),
    (36, 'S', 'I have felt satisfied with the support I have received from other significant people.',
         'मुझे अन्य महत्वपूर्ण व्यक्तियों से प्राप्त सहयोग से संतुष्टि महसूस हुई।'),
    (37, 'R', 'I have not felt satisfied with my health.',
         'मुझे अपने स्वास्थ्य से संतुष्टि महसूस नहीं हुई।'),
    (38, 'S', 'I have felt satisfied with life in general.',
         'मुझे सामान्यतः जीवन से संतुष्टि महसूस हुई।'),
]

SURGERY_TICK = ("Tick here if you have already had genital surgery "
                "(unless you feel you need more)")
SURGERY_TICK_HI = ("यदि आपका पहले ही जननांग-शस्त्रक्रिया हो चुकी है तो यहाँ चिह्नित करें "
                   "(जब तक कि आपको अधिक की आवश्यकता न लगे)")

FREQUENCY_OPTIONS = [
    {"v": 0, "en": "Never",     "hi": "कभी नहीं"},
    {"v": 1, "en": "Rarely",    "hi": "विरल"},
    {"v": 2, "en": "Sometimes", "hi": "कभी-कभी"},
    {"v": 3, "en": "Often",     "hi": "अक्सर"},
    {"v": 4, "en": "Always",    "hi": "सदैव"},
]

# Subscales exactly as printed on the instrument.
SUBSCALES = {
    "functional_impact": {
        "en": "Functional impact of gender-related distress (items 1-13)",
        "hi": "लिंग-संबंधी कष्ट का कार्यात्मक प्रभाव (आइटम 1-13)",
        "note_en": ("How much gender-related distress has disrupted social, "
                    "occupational, emotional, physical-intimacy and home life, "
                    "and depressed/anxious symptoms."),
        "note_hi": ("लिंग-संबंधी कष्ट ने सामाजिक, व्यावसायिक, भावनात्मक, शारीरिक-नैकट्य "
                    "और गार्हस्थ्य जीवन तथा उदासीन/चिंत लक्षणों को कितना बाधित किया।"),
        "range": (0, 52),
    },
    "body_preoccupation": {
        "en": "Body preoccupation and distress (items 14, 15, 17, 18, 19, 21, 23, 24, 26, 27, 28, 29)",
        "hi": "शारीरिक आसक्ति एवं कष्ट (आइटम 14, 15, 17, 18, 19, 21, 23, 24, 26, 27, 28, 29)",
        "note_en": ("Distress focused on chest, genitals, body/facial hair and "
                    "voice, and belief that genital surgery would relieve the "
                    "unhappiness."),
        "note_hi": ("वक्ष, जननांग, शरीर/मुख्य बाल और स्वर पर केंद्रित कष्ट, तथा यह "
                    "धारणा कि जननांग-शस्त्रक्रिया असुख को हर लेगी।"),
        "range": (0, 48),
    },
    "social_preoccupation": {
        "en": "Social preoccupation and distress (items 16, 20, 22, 25, 30 reversed)",
        "hi": "सामाजिक आसक्ति एवं कष्ट (आइटम 16, 20, 22, 25, 30 — व्युक्रम)",
        "note_en": ("Comfort with how others perceive one's gender, satisfaction "
                    "with the pronouns used, comfort with being perceived from one's "
                    "appearance, feeling that the genitals match, and satisfaction "
                    "with the chest. These five items are worded positively and are "
                    "REVERSE-scored: the subscale rises as comfort falls."),
        "note_hi": ("दूसरों द्वारा लिंग-धारण से सुख, प्रयुक्त सर्वनामों से संतुष्टि, बाह्य "
                    "स्वरूप से धारणा से सुख, जननांगों के मेल का बोध और वक्ष से संतुष्टि। ये पाँच "
                    "कथन सकारात्मक हैं और व्युक्रम-अंकित होते हैं: सुख घटने पर यह उप-पैमाना बढ़ता है।"),
        "range": (0, 20),
    },
    "life_satisfaction": {
        "en": "Life satisfaction (items 31-38, 35 and 37 reversed)",
        "hi": "जीवन-संतुष्टि (आइटम 31-38, 35 एवं 37 — व्युक्रम)",
        "note_en": ("Reported separately from the distress subscales: higher = "
                    "MORE satisfaction. Items 35 and 37 are worded negatively "
                    "and are reverse-scored so that all eight point the same way."),
        "note_hi": ("कष्ट-उप-पैमानों से पृथक् रिपोर्ट: उच्च = अधिक संतुष्टि। आइटम 35 एवं 37 "
                    "नकारात्मक हैं और व्युक्रम-अंकित होते ताकि सभी आठ एक ही दिशा में रहें।"),
        "range": (0, 32),
    },
}

REVERSED_KEYS = {"C", "R"}


def build_scale():
    parts = []
    meta = {}
    groups = [
        ("gcls_part1", "past_6_months_distress",
         {"en": "In the past 6 months, due to the distress about my gender "
                "(i.e., the distress caused as the gender I was assigned at "
                "birth does not match with my gender identity):",
          "hi": "पिछले 6 माह में, मेरे लिंग संबंधी कष्ट के कारण (अर्थात् वह कष्ट जो "
              "जन्म के समय सौंपे गए लिंग और मेरी लिंग-पहचान के मेल न खाने से होता है):"},
         [i for i in ITEMS if i[0] <= 13]),
        ("gcls_part2", "gender_experience",
         {"en": "In the past 6 months:", "hi": "पिछले 6 माह में:"},
         [i for i in ITEMS if 14 <= i[0] <= 30]),
        ("gcls_part3", "life_satisfaction",
         {"en": "Next, we would like to know how satisfied you have been with "
               "your life for the last 6 months:",
          "hi": "इसके बाद, हम जानना चाहते हैं कि पिछले 6 माह में आप अपने जीवन से "
              "कितने संतुष्ट रहे:"},
         [i for i in ITEMS if i[0] >= 31]),
    ]
    for pid, key, name, rows in groups:
        questions = []
        for row in rows:
            num, k, en, hi = row[0], row[1], row[2], row[3]
            safety = bool(row[4]) if len(row) > 4 else False
            q = {
                "id": "gcls_%d" % num,
                "itemNumber": num,
                "text": {"en": en, "hi": hi},
            }
            if safety:
                q["safety"] = True
            if k in REVERSED_KEYS:
                q["reverseScored"] = True
            questions.append(q)
            meta[num] = k
        parts.append({"id": pid, "partKey": key, "name": name, "questions": questions})

    # Non-scored clinical note attached to item 26, exactly as printed.
    parts[1]["questions"].append({
        "id": "gcls_surgery_tick",
        "itemNumber": "□",
        "text": {"en": SURGERY_TICK, "hi": SURGERY_TICK_HI},
        "nonScored": True,
        "tickBox": True,
        "linkedItem": 26,
        "note": {"en": "Clinical note — not scored",
                 "hi": "नैदानिक टिप्पणी — अंकित नहीं"},
    })

    subscales = {slug: dict(spec) for slug, spec in SUBSCALES.items()}
    # Explicit item lists (readable and asserted against the item table).
    subscales["functional_impact"]["items"] = list(range(1, 14))
    subscales["body_preoccupation"]["items"] = [14, 15, 17, 18, 19, 21, 23, 24, 26, 27, 28, 29]
    subscales["social_preoccupation"]["items"] = [16, 20, 22, 25, 30]
    subscales["life_satisfaction"]["items"] = list(range(31, 39))
    for slug, spec in subscales.items():
        spec["reversedItems"] = [n for n in spec["items"] if meta[n] in REVERSED_KEYS]
        # Range is derived from the item lists (0-4 per item), never hand-typed.
        spec["minTotal"] = 0
        spec["maxTotal"] = len(spec["items"]) * 4
        assert tuple(spec["range"]) == (spec["minTotal"], spec["maxTotal"]), \
            (slug, spec["range"], spec["maxTotal"])

    total_scored_items = sum(len(p["questions"]) for p in parts) - 1  # minus tick box
    assert total_scored_items == 38, total_scored_items

    return {
        "id": "gcls",
        "name": {
            "en": "Gender Congruence and Life Satisfaction Scale (GCLS)",
            "hi": "लंग-संगति एवं जीवन-संतुष्टि मापनी (GCLS)",
        },
        "type": "matrix",
        "administeredBy": "self-report",
        "optionalAssessment": True,
        "sourceInstrument": "GCLS",
        "targetAge": ["adolescent", "adult"],
        "directions": {
            "en": ("Below is a range of statements about how you might feel in relation "
                   "to your gender, mental well-being, and life satisfaction. Please "
                   "respond to each statement, thinking about how frequently you have "
                   "felt like this in the past 6 months. "
                   "Please note that when talking about 'gender identity' we mean one's "
                   "internal sense of one's self as a man, a woman, or some other gender. "
                   "Please rate each statement as: NEVER (N), RARELY (R), SOMETIMES (S), "
                   "OFTEN (O), or ALWAYS (A)."),
            "hi": ("नीचे आपके लिंग, मानसिक सुख-समता एवं जीवन-संतुष्टि से संबंधित कथनों की "
                   "एक श्रेणी दी गई है। प्रत्येक कथन का उत्तर दें, यह सोचते हुए कि पिछले 6 माह में "
                   "आपने ऐसा कितनी बार अनुभव किया। "
                   "कृपया ध्यान दें कि जब 'लिंग-पहचान' की बात की जाती है, तब इसका अर्थ है किसी का "
                   "अंतर्गत स्व-बोध — पुरुष, महिला या अन्य कोई लिंग के रूप में। "
                   "प्रत्येक कथन का मूल्यांकन करें: कभी नहीं (N), विरल (R), कभी-कभी (S), अक्सर (O), या सदैव (A)।"),
        },
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
                "hi": ("GCLS लिंग-संबंधी कष्ट एवं जीवन-संतुष्टि का वर्णन करता है; यह लिंग-असंगति/"
                       "डिस्फोरिया का रोग-निर्णय नहीं करता, जो DSM-5-TR / ICD-11 नियमों एवं नैदानिक "
                       "मूल्यांकन पर आधारित है। केवल लिंग-विविधता मानसिक विकार नहीं है। स्कोर उपचार-"
                       "योजना एवं अनुवर्ती हेतु सूचित करते हैं, किसी हस्तक्षेप की पात्रता हेतु नहीं।"),
            },
            "disorders": ["gender_incongruence"],
            "riskItems": {
                "en": ("Items 8 and 13 ask about thoughts of hurting the chest/genitals and "
                       "of suicide. Any non-zero response opens the crisis pathway; these "
                       "responses must be followed by a direct risk assessment."),
                "hi": ("आइटम 8 वक्ष/जननांग को क्षति पहुँचाने तथा आइटम 13 आत्महत्या के विचार पूछते हैं। "
                       "शून्येतर उत्तर पर संकट-पथ खुलता है; ऐसे उत्तरों का सीधा जोखिम-मूल्यांकन आवश्यक।"),
            },
        },
        "sourcePages": ("Gender Congruence and Life Satisfaction Scale (GCLS) — 38 items, "
                        "5-point frequency rating over the past 6 months, plus one non-scored "
                        "genital-surgery tick-box."),
        "translationNote": {
            "en": ("English wording is authoritative and reproduced as supplied. Hindi labels "
                   "are a working translation and must be proofread by a bilingual clinician "
                   "before clinical use."),
            "hi": ("अंग्रेज़ी पाठ प्रामाणिक है तथा यथा-प्रदत्त प्रतिलिपित किया गया है। हिन्दी "
                   "अनुवाद कार्य-प्रगति पर है; नैदानिक प्रयोग से पूर्व द्विभाषी चिकित्सक से "
                   "शुद्धि आवश्यक।"),
        },
        "licensing": {
            "en": ("Instrument text should be used only with permission of the rights holder; "
                   "confirm current GCLS licensing terms before clinical or research deployment."),
            "hi": ("मापनी का पाठ केवल अधिकार-वाहक की अनुमति से प्रयोग करें; नैदानिक या शोध-"
                   "प्रयोग से पूर्व वर्तमान लाइसेंस-शर्तें पुष्टि करें।"),
        },
        "branching": None,
    }


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


INSTRUMENT_ENTRY = {
    "name": "GCLS (Gender Congruence and Life Satisfaction Scale)",
    "construct": {"en": "Gender congruence, gender-related distress & life satisfaction",
                  "hi": "लंग-संगति, लिंग-संबंधी कष्ट एवं जीवन-संतुष्टि"},
    "format": {"en": "38 items rated Never-Rarely-Sometimes-Often-Always (0-4) over 6 months, "
                     "+ 1 non-scored genital-surgery tick-box; 4 subscales",
               "hi": "38 आइटम, कभी नहीं–सदैव (0-4), 6 माह, + 1 अ-अंकित जननांग-शस्त्रक्रिया चिह्न; 4 उप-पैमाने"},
    "duration": "~10 min",
    "language": {"en": "English, Hindi", "hi": "अंग्रेज़ी, हिन्दी"},
    "purpose": {"en": "Quantify gender-related distress, body and social preoccupation and "
                      "life satisfaction; supports assessment and outcome monitoring.",
                "hi": "लिंग-संबंधी कष्ट, शारीरिक व सामाजिक आसक्ति तथा जीवन-संतुष्टि का परिमाणीकरण; "
                      "मूल्यांकन एवं परिणाम-निगरानी में सहायक।"},
    "source": "Gender Congruence and Life Satisfaction Scale (GCLS)",
    "licensing": {"en": "Confirm permission terms with the rights holder before clinical or "
                        "research use.",
                  "hi": "नैदानिक/शोध-प्रयोग से पूर्व अधिकार-वाहक से अनुमति-शर्तें पुष्टि करें।"},
}


def main():
    check = "--check" in sys.argv
    data = json.loads(DATA.read_text(encoding="utf-8"))

    data.setdefault("scales", {})["gcls"] = build_scale()

    domains = data["domains"]
    for i, d in enumerate(domains):
        if d["id"] == "gender":
            domains[i] = build_domain()
            break
    else:
        domains.append(build_domain())

    for k, v in DISORDERS_TO_ADD.items():
        data["disorders"].setdefault(k, v)

    data["instruments"]["GCLS"] = INSTRUMENT_ENTRY

    notes = data["meta"].setdefault("instrumentNotes", [])
    note = ("GCLS implemented as scales.gcls (Gender Congruence and Life Satisfaction Scale; "
            "38 items rated Never=0 to Always=4 over the past 6 months, plus one non-scored "
            "genital-surgery tick-box linked to item 26). Four subscales with reverse-keyed "
            "positively worded items (16, 20, 22, 30 congruence; 35, 37 negative satisfaction): "
            "functional impact 1-13, body preoccupation 14/15/17/18/19/21/23/24/26/27/28/29, "
            "social preoccupation 16/20/22/30, life satisfaction 31-38 reported separately "
            "(higher = more satisfied). Reached through the new 'gender' domain via routing "
            "auto:genderdistress. Items 8 and 13 are safety-flagged (chest/genital self-harm "
            "and suicidal ideation) and open the crisis pathway. Dimensional screen only — it "
            "never diagnoses gender incongruence, and gender diversity alone is not a disorder.")
    if note not in notes:
        notes.append(note)

    data["meta"]["schemaVersion"] = SCHEMA_TARGET
    data["meta"]["updated"] = "2026-11-04"

    # sanity assertions
    s = data["scales"]["gcls"]
    scored = [q for p in s["parts"] for q in p["questions"] if not q.get("nonScored")]
    assert len(scored) == 38, len(scored)
    assert all(("reverseScored" in q) == (q["itemNumber"] in (16, 20, 22, 30, 35, 37))
               for q in scored), "reverse key mismatch"
    covered = set()
    for spec in s["subscales"].values():
        covered.update(spec["items"])
    assert covered == set(range(1, 39)), sorted(set(range(1, 39)) - covered)

    if check:
        print("would write schema %s | gcls items: %d | subscales: %d | domains: %d"
              % (SCHEMA_TARGET, len(scored), len(s["subscales"]), len(data["domains"])))
        return

    DATA.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("wrote data.json schema %s | gcls items: %d | subscales: %d | domains: %d"
          % (SCHEMA_TARGET, len(scored), len(s["subscales"]), len(data["domains"])))


if __name__ == "__main__":
    main()
