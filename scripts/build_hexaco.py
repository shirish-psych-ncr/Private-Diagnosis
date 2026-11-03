#!/usr/bin/env python3
"""
Add the HEXACO-PI-R Observer Report Form to data.json.

The HEXACO-PI-R observer form is a 60-item other-report measure of the six
HEXACO personality domains (Honesty-Humility, Emotionality, Extraversion,
Agreeableness, Conscientiousness, Openness to Experience), rated on a 1-5
agree/disagree scale by someone who knows the person being described. Each
domain has four facets; items marked R are reverse-scored. Facet score = mean
of its (reversed where keyed) raw items; domain score = mean of its facet
scores. The form is published freely by the authors (Lee & Ashton) at
hexaco.org, so item wording is reproduced verbatim.

This script is idempotent: it rewrites only the `hexaco_pi_r_observer` scale,
the `personality` domain's attached screen-in item, the instrument-library
entry and the meta notes. Run with --check for a dry run.

    python3 scripts/build_hexaco.py [--check]
"""
import json
import sys
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data.json"
SCHEMA_TARGET = "2.9.0"


def bi(hi, en):
    return {"en": en, "hi": hi}


# --------------------------------------------------------------------------
# Items — verbatim from the printed OBSERVER report form. `n` is the printed
# item number, `rev` marks the items the scoring guide keys as R (reverse).
# --------------------------------------------------------------------------
ITEMS = [
    (1,  "He/she would be quite bored by a visit to an art gallery.",
               "वह/वो कला-दीर्घा देखने से बिल्कुल ऊब जाएगा/जाएगी।"),
    (2, "He/she cleans his/her office or home quite frequently.",
               "वह/वो अपना कार्यालय या घर बहुत अक्सर साफ़ करता/करती है।"),
    (3, "He/she rarely holds a grudge, even against people who have badly wronged him/her.",
               "वह/वो बुरी तरह ठगा गया हो तब भी शिकायत/द्वेष बहुत कम रखता/रखती है।"),
    (4, "He/she feels reasonably satisfied with himself/herself overall.",
               "वह/वो समग्र रूप से स्वयं से यथेष्ट संतुष्ट महसूस करता/करती है।"),
    (5, "He/she would feel afraid if he/she had to travel in bad weather conditions.",
               "वह/वो खराब मौसम में यात्रा करनी हो तो डरेगा/डरेगी।"),
    (6, "If he/she wants something from a person he/she dislikes, he/she will act very nicely toward that person in order to get it.",
               "जिस व्यक्ति को वह/वो पसंद नहीं करता/करती, उससे कुछ चाहिए हो तो पाने हेतु उसके साथ बड़ा मिलनसार व्यवहार करेगा/करेगी।"),
    (7, "He/she is interested in learning about the history and politics of other countries.",
               "वह/वो अन्य देशों के इतिहास एवं राजनीति जानने में रुचि रखता/रखती है।"),
    (8, "When working, he/she often sets ambitious goals for himself/herself.",
               "कार्य करते समय वह/वो अक्सर स्वयं के लिए महत्वाकांक्षी लक्ष्य निर्धारित करता/करती है।"),
    (9,  "People sometimes say that he/she is too critical of others.",
               "लोग कभी-कभी कहते हैं कि वह/वो दूसरों की अधिक आलोचना करता/करती है।"),
    (10,  "He/she rarely expresses his/her opinions in group meetings.",
               "वह/वो सामूहिक बैठकों में अपना मत बहुत कम व्यक्त करता/करती है।"),
    (11, "He/she worries about little things.",
               "वह/वो छोटी-छोटी बातों की चिंता करता/करती है।"),
    (12,  "If he/she knew that he/she could never get caught, he/she would be willing to steal a million dollars.",
               "पकड़े जाने की सम्भावना न हो तो वह/वो दस लाख रुपये चुराने को तैयार होगा/होगी।"),
    (13, "He/she would like a job that requires following a routine rather than being creative.",
               "वह/वो रचनात्मकता के बजाय दिनचर्या-पालन वाली नौकरी पसंद करेगा/करेगी।"),
    (14, "He/she often checks his/her work over repeatedly to find any mistakes.",
               "वह/वो त्रुटियाँ खोजने हेतु अपना कार्य बार-बार जाँचता/जाँचती है।"),
    (15,  "People sometimes think that he/she is too stubborn.",
               "लोग कभी-कभी सोचते हैं कि वह/वो अत्यधिक ज़िद्दी है।"),
    (16, "He/she avoids making \"small talk\" with people.",
               "वह/वो लोगों से अनौपचारिक गप्पें (small talk) करने से बचता/बचती है।"),
    (17, "When he/she suffers from a painful experience, he/she needs someone to make him/her feel comfortable.",
               "कष्टदायक अनुभव में वह/वो किसी को स्वयं को सांत्वना देने वाला चाहता/चाहती है।"),
    (18,  "Having a lot of money is not especially important to him/her.",
               "अधिक धन होना उसके/उसके लिए विशेष महत्वपूर्ण नहीं है।"),
    (19,  "He/she thinks that paying attention to radical ideas is a waste of time.",
               "वह/वो उग्र/कट्टर विचारों पर ध्यान देना समय की बर्बादी मानता/मानती है।"),
    (20,  "He/she makes decisions based on the feeling of the moment rather than on careful thought.",
               "वह/वो सूझबूझ के बजाय क्षणिक भावनाओं पर निर्णय लेता/लेती है।"),
    (21,  "People think of him/her as someone who has a quick temper.",
               "लोग उसे/उसे तेज़ गुस्से वाला मानते हैं।"),
    (22, "He/she is energetic nearly all the time.",
               "वह/वो लगभग सदैव ऊर्जावान रहता/रहती है।"),
    (23, "He/she feels like crying when he/she sees other people crying.",
               "दूसरों को रोते देख वह/वो स्वयं भी रोने जैसा महसूस करता/करती है।"),
    (24,  "He/she thinks that he/she is an ordinary person who is no better than others.",
               "वह/वो स्वयं को साधारण और दूसरों से श्रेष्ठ नहीं मानता/मानती।"),
    (25,  "He/she wouldn't spend his/her time reading a book of poetry.",
               "वह/वो काव्य-पुस्तक पढ़ने में समय नहीं बिताएगा/बिताएगी।"),
    (26,  "He/she plans ahead and organizes things, to avoid scrambling at the last minute.",
               "अंतिम क्षण की हड़बड़ी से बचने हेतु वह/वो पूर्व-नियोजन एवं संगठन करता/करती है।"),
    (27, "His/her attitude toward people who have treated him/her badly is \"forgive and forget\".",
               "बुरा करने वालों के प्रति उसका/उसके मनभाव — “क्षमा करो और भूल जाओ”।"),
    (28, "He/she thinks that most people like some aspects of his/her personality.",
               "वह/वो सोचता/सोचती है कि अधिकतर लोग उसकी/उसके व्यक्तित्व के कुछ पहलू पसंद करते हैं।"),
    (29, "He/she doesn't mind doing jobs that involve dangerous work.",
               "वह/वो खतरनाक काम वाली नौकरियों में कोई आपत्ति नहीं करता/करती।"),
    (30,  "He/she wouldn't use flattery to get a raise or promotion at work, even if he/she thought it would succeed.",
               "वेतन-वृद्धि या पदोन्नति हेतु चापलूसी उपयोग नहीं करेगा/करेगी, भले सफलता का विश्वास हो।"),
    (31, "He/she enjoys looking at maps of different places.",
               "वह/वो विभिन्न स्थानों के नक्शे देखने में आनंद लेता/लेती है।"),
    (32,  "He/she often pushes himself/herself very hard when trying to achieve a goal.",
               "लक्ष्य प्राप्ति हेतु वह/वो स्वयं को अक्सर अत्यधिक कठिन परिश्रम के लिए प्रेरित करता/करती है।"),
    (33, "He/she generally accepts people's faults without complaining about them.",
               "वह/वो सामान्यतः लोगों की कमियाँ शिकायत किए बिना स्वीकार करता/करती है।"),
    (34, "In social situations, he/she is usually the one who makes the first move.",
               "सामाजिक परिस्थितियों में अक्सर पहल वह/वो करता/करती है।"),
    (35,  "He/she worries a lot less than most people do.",
               "वह/वो अधिकतर लोगों की तुलना में बहुत कम चिंता करता/करती है।"),
    (36,  "He/she would be tempted to buy stolen property if he/she were financially tight.",
               "आर्थिक तंगी में चोरी का माल खरीदने के लिए प्रलोभित होगा/होगी।"),
    (37, "He/she would enjoy creating a work of art, such as a novel, a song, or a painting.",
               "वह/वो उपन्यास, गीत या चित्रकला जैसे कला-कर्म रचने में आनंद लेगा/लेगी।"),
    (38,  "When working on something, he/she doesn't pay much attention to small details.",
               "कार्य करते समय वह/वो छोटे-छोटे विवरणों पर अधिक ध्यान नहीं देता/देती।"),
    (39, "He/she is usually quite flexible in his/her opinions when people disagree with him/her.",
               "मतभेद होने पर वह/वो सामान्यतः अपने मतों में काफ़ी लचीला रहता/रहती है।"),
    (40, "He/she enjoys having lots of people around to talk with.",
               "वह/वो बातचीत हेतु बहुत से लोगों के बीच रहना पसंद करता/करती है।"),
    (41,  "He/she can handle difficult situations without needing emotional support from anyone else.",
               "कठिन परिस्थितियों का सामना वह/वो अन्य किसी के भावनात्मक सहारे के बिना कर सकता/सकती है।"),
    (42,  "He/she would like to live in a very expensive, high-class neighborhood.",
               "वह/वो अत्यंत महँगे, उच्च-वर्गीय पड़ोस में रहना चाहेगा/चाहेगी।"),
    (43, "He/she likes people who have unconventional views.",
               "वह/वो असम्प्रदायिक/अपरंपरिक विचारों वाले लोगों को पसंद करता/करती है।"),
    (44,  "He/she makes a lot of mistakes because he/she doesn't think before he/she acts.",
               "विचार किए बिना कार्य करने से वह/वो अनेक त्रुटियाँ करता/करती है।"),
    (45, "He/she rarely feels anger, even when people treat him/her quite badly.",
               "लोग बुरा व्यवहार करें तब भी वह/वो क्रोध बहुत कम महसूस करता/करती है।"),
    (46, "On most days, he/she feels cheerful and optimistic.",
               "अधिकतर दिनों वह/वो प्रसन्न एवं आशावादी महसूस करता/करती है।"),
    (47, "When someone he/she knows well is unhappy, he/she can almost feel that person's pain himself/herself.",
               "निकट परिचित दुखी हो तो वह/वो लगभग उसका दर्द स्वयं महसूस कर सकता/सकती है।"),
    (48,  "He/she wouldn't want people to treat him/her as though he/she were superior to them.",
               "लोग उसे/उसे स्वयं से श्रेष्ठ मानकर व्यवहार करें — यह वह/वो नहीं चाहेगा/चाहेगी।"),
    (49, "If he/she had the opportunity, he/she would like to attend a classical music concert.",
               "अवसर मिले तो वह/वो शास्त्रीय संगीत कार्यक्रम में जाना चाहेगा/चाहेगी।"),
    (50,  "People often joke with him/her about the messiness of his/her room or desk.",
               "लोग उसके/उसके कमरे या मेज़ की अव्यवस्था का अक्सर मज़ाक उड़ाते हैं।"),
    (51,  "If someone has cheated him/her once, he/she will always feel suspicious of that person.",
               "एक बार धोखा हुआ हो तो वह/वो उस व्यक्ति के प्रति सदैव संदेहशील रहेगा/रहेगी।"),
    (52,  "He/she feels that he/she is an unpopular person.",
               "वह/वो स्वयं को अप्रिय/अलोकप्रिय व्यक्ति मानता/मानती है।"),
    (53, "When it comes to physical danger, he/she is very fearful.",
               "शारीरिक खतरे के मामले में वह/वो अत्यंत भयाकुल होता/होती है।"),
    (54,  "If he/she wants something from someone, he/she will laugh at that person's worst jokes.",
               "किसी से कुछ चाहिए हो तो उसकी सबसे बुरी चुटकुलों पर भी वह/वो हँसेगा/हँसेगी।"),
    (55,  "He/she would be very bored by a book about the history of science and technology.",
               "विज्ञान एवं तकनीकी के इतिहास की पुस्तक से वह/वो बहुत बोर होगा/होगी।"),
    (56,  "Often when he/she sets a goal, he/she ends up quitting without having reached it.",
               "अक्सर लक्ष्य निर्धारित करने पर उसे पाए बिना ही वह/वो बीच में छोड़ देता/छोड़ देती है।"),
    (57, "He/she tends to be lenient in judging other people.",
               "दूसरों का मूल्यांकन करते समय वह/वो उदार/शिथिल रहने की प्रवृत्ति रखता/रखती है।"),
    (58, "When he/she is in a group of people, he/she is often the one who speaks on behalf of the group.",
               "समूह में वह/वो अक्सर समूह की ओर से बोलता/बोलती है।"),
    (59,  "He/she rarely, if ever, has trouble sleeping due to stress or anxiety.",
               "तनाव या चिंता के कारण नींद में कठिनाई वह/वो बहुत कम, यदि कभी, अनुभव करता/करती है।"),
    (60,  "He/she would never accept a bribe, even if it were very large.",
               "अत्यधिक बड़ा हो तब भी वह/वो कभी रिश्वत स्वीकार नहीं करेगा/करेगी।"),
]

# --------------------------------------------------------------------------
# Facets — exactly as printed in the HEXACO-60 scoring guide. `R` marks the
# reverse-keyed items. Domain score = mean of its facet scores.
# --------------------------------------------------------------------------
FACETS = [
    ("h_h", "sincerity",            "Sincerity",                    "आंतरिकता/निष्ठा", [6, 30, 54]),
    ("h_h", "fairness",             "Fairness",                     "न्यायपरायणता",     [12, 36, 60]),
    ("h_h", "greed_avoidance",      "Greed Avoidance",              "लालच-परिहार",   [18, 42]),
    ("h_h", "modesty",              "Modesty",                      "विनम्रता",       [24, 48]),

    ("e", "fearfulness",            "Fearfulness",                  "भयाकुलता",       [5, 29, 53]),
    ("e", "anxiety",                "Anxiety",                      "चिंता",         [11, 35]),
    ("e", "dependence",             "Dependence",                   "निर्भरता",       [17, 41]),
    ("e", "sentimentality",         "Sentimentality",               "संवेदनशीलता",   [23, 47, 59]),

    ("x", "social_self_esteem",     "Social Self-Esteem",           "सामाजिक आत्मसम्मान", [4, 28, 52]),
    ("x", "social_boldness",        "Social Boldness",              "सामाजिक साहस",   [10, 34, 58]),
    ("x", "sociability",            "Sociability",                  "सामाजिकता",     [16, 40]),
    ("x", "liveliness",             "Liveliness",                   "प्राणोद्वलन",   [22, 46]),

    ("a", "forgiveness",            "Forgiveness",                  "क्षमाशीलता",     [3, 27]),
    ("a", "gentleness",             "Gentleness",                   "कोमलता",        [9, 33, 51]),
    ("a", "flexibility",            "Flexibility",                  "लचीलापन",       [15, 39, 57]),
    ("a", "patience",               "Patience",                     "धैर्य",         [21, 45]),

    ("c", "organization",           "Organization",                 "सुव्यवस्था",    [2, 26]),
    ("c", "diligence",              "Diligence",                    "परिश्रमिता",    [8, 32]),
    ("c", "perfectionism",          "Perfectionism",                "परिपूर्णता",    [14, 38, 50]),
    ("c", "prudence",               "Prudence",                     "सावधानता",      [20, 44, 56]),

    ("o", "aesthetic_appreciation", "Aesthetic Appreciation",       "सौंदर्य-साहाध्यता", [1, 25]),
    ("o", "inquisitiveness",        "Inquisitiveness",              "जिज्ञासा",       [7, 31]),
    ("o", "creativity",             "Creativity",                   "रचनात्मकता",    [13, 37, 49]),
    ("o", "unconventionality",      "Unconventionality",            "अपरंपरिकता",    [19, 43, 55]),
]

# Items keyed "R" (reverse-scored) in the published HEXACO-60 scoring guide.
REVERSE_KEYED = {1, 9, 10, 12, 15, 18, 19, 20, 21, 24, 25, 26, 30, 32, 35, 36,
                 38, 41, 42, 44, 48, 50, 51, 52, 54, 55, 56, 57, 59, 60}

# Reverse-keyed items ("R" in the printed scoring guide), derived from FACETS so
# the item flags and the facet keying can never drift apart.
REV = {num for _d, _f, _en, _hi, items in FACETS for num in items if num in REVERSE_KEYED}

DOMAINS = [
    ("h_h", "Honesty-Humility", "प्रामाणिकता-विनम्रता",
     "Sincerity, Fairness, Greed Avoidance, Modesty"),
    ("e", "Emotionality", "भावनात्मकता",
     "Fearfulness, Anxiety, Dependence, Sentimentality"),
    ("x", "Extraversion", "बहिर्मुखता",
     "Social Self-Esteem, Social Boldness, Sociability, Liveliness"),
    ("a", "Agreeableness", "सहमतिशीलता",
     "Forgiveness, Gentleness, Flexibility, Patience"),
    ("c", "Conscientiousness", "कर्तव्यनिष्ठा",
     "Organization, Diligence, Perfectionism, Prudence"),
    ("o", "Openness to Experience", "अनुभव-के-प्रति-विवृतता",
     "Aesthetic Appreciation, Inquisitiveness, Creativity, Unconventionality"),
]



def build_scale():
    questions = []
    for n, en, hi in ITEMS:
        questions.append({
            "id": "hx_%d" % n,
            "itemNumber": n,
            "reverseScored": bool(n in REV),
            "text": bi(hi, en),
        })

    facets = {}
    for dom_slug, fslug, f_en, f_hi, items in FACETS:
        entries = list(items)
        facets[fslug] = {
            "name": bi(f_hi, f_en),
            "domain": dom_slug,
            "items": entries,
        }

    domains = {}
    for slug, d_en, d_hi, facet_names in DOMAINS:
        fs = [k for k, v in facets.items() if v["domain"] == slug]
        domains[slug] = {
            "name": bi(d_hi, d_en),
            "facets": fs,
            "facetNames": facet_names,
        }

    return {
        "id": "hexaco_pi_r_observer",
        "name": bi("HEXACO-PI-R (पर्यवेक्षक रिपोर्ट फ़ॉर्म)",
                   "HEXACO-PI-R (Observer Report Form)"),
        "type": "matrix",
        "administeredBy": "informant",
        "optionalAssessment": True,
        "sourceInstrument": "HEXACO-PI-R / HEXACO-60",
        "targetAge": ["adolescent", "adult"],
        "directions": bi(
            "निम्न पृष्ठों में उन व्यक्ति के बारे में कथनों की एक श्रृंखला दी गई है जिसे आप अभी रेट कर रहे हैं। प्रत्येक कथन पढ़ें और निर्णय करें कि आप उससे कितना सहमत या असहमत हैं। फिर निम्न पैमाने का उपयोग कर उत्तर दें: 5 = पूर्णतः सहमत, 4 = सहमत, 3 = तटस्थ (न सहमत न असहमत), 2 = असहमत, 1 = पूर्णतः असहमत। प्रत्येक कथन का उत्तर दें, भले ही आप पूर्णतः निश्चित न हों।\n\nमूल्यांकन से पूर्व रेट किए जा रहे व्यक्ति के बारे में ये जानकारी दें: परिचय की संवत्सर-संख्या, लिंग, आयु।",
            "On the following pages you will find a series of statements about the person that you are rating now. Please read each statement and decide how much you agree or disagree with that statement. Then write your response in the space next to the statement using the following scale: 5 = strongly agree, 4 = agree, 3 = neutral (neither agree nor disagree), 2 = disagree, 1 = strongly disagree. Please answer every statement, even if you are not completely sure of your response.\n\nPlease provide the following information about the person that you will be rating: number of years you have been acquainted with this person, sex of the person being rated, and age of the person being rated."),
        "timeframe": bi(
            "सामान्यतः — स्थायी व्यवहार-पैटर्न (अस्थायी अवस्थाएँ नहीं)।",
            "General, long-standing pattern as observed by the informant (not a temporary state)."),
        "informantFields": [
            {"id": "hx_years_acquainted", "label": bi("परिचय की अवधि (वर्ष)",
                                                     "Number of years that you have been acquainted with this person")},
            {"id": "hx_subject_sex", "label": bi("मूल्यांकन-विषय का लिंग",
                                                "Sex of the person that you will be rating"),
             "options": [{"v": "female", "label": bi("स्त्री", "Female")},
                         {"v": "male", "label": bi("पुरुष", "Male")}]},
            {"id": "hx_subject_age", "label": bi("मूल्यांकन-विषय की आयु (वर्ष)",
                                                "Age of the person that you will be rating")},
        ],
        "parts": [{
            "id": "hx_items",
            "partKey": "observer_items",
            "name": bi("पर्यवेक्षक-रेटिंग — 60 कथन (1 = पूर्णतः असहमत … 5 = पूर्णतः सहमत)",
                       "Observer ratings — 60 statements (1 = strongly disagree … 5 = strongly agree)"),
            "questions": questions,
        }],
        "matrixOptions": [
            {"v": 1, "label": bi("1 पूर्णतः असहमत", "1 Strongly disagree")},
            {"v": 2, "label": bi("2 असहमत", "2 Disagree")},
            {"v": 3, "label": bi("3 तटस्थ", "3 Neutral")},
            {"v": 4, "label": bi("4 सहमत", "4 Agree")},
            {"v": 5, "label": bi("5 पूर्णतः सहमत", "5 Strongly agree")},
        ],
        "ratingScale": {
            "min": 1, "max": 5,
            "note": bi(
                "1 = पूर्णतः असहमत · 2 = असहमत · 3 = तटस्थ · 4 = सहमत · 5 = पूर्णतः सहमत। 'R' चिह्नित आइटम व्युक्रम-अंकित होते हैं।",
                "1 = strongly disagree, 2 = disagree, 3 = neutral (neither agree nor disagree), 4 = agree, 5 = strongly agree. Items marked R are reverse-scored."),
        },
        "facets": facets,
        "domains": domains,
        "sumScoring": True,
        "scoring": {
            "method": "hexaco_observer_facet_domain_means",
            "scaleMin": 1,
            "scaleMax": 5,
            "rule": bi(
                "प्रत्येक आइटम 1-5 पर रेट होता है। पहले व्युक्रम-आइटम (R) के लिए 6 − उत्तर निकालें। प्रत्येक फलक (facet) का अंक = उसके (व्युक्रम-अंकित) आइटमों का माध्य; प्रत्येक डोमेन का अंक = अपने चार फलक-अंकों का माध्य। सभी अंक 1-5 पर रिपोर्ट हों।",
                "Rate each item 1-5. For every item marked R in the scoring guide, use 6 minus the response. A facet score is the MEAN of its (reversed where keyed) raw items; a domain score is the MEAN of its four facet scores. Report all scores on the 1-5 metric."),
            "reverseItems": sorted(REV),
            "interpretationNote": bi(
                "HEXACO अंक वर्णनात्मक व्यक्तित्व-प्रोफाइल हैं — कोई नैदानिक कटऑफ नहीं। उच्च H-H = प्रामाणिकता/विनम्रता; उच्च E = भय/चिंता/निर्भरता/संवेदनशीलता; उच्च X = सामाजिक आत्मसम्मान/साहस/सामाजिकता/प्राणोद्वलन; उच्च A = क्षमा/कोमलता/लचीलापन/धैर्य; उच्च C = सुव्यवस्था/परिश्रम/परिपूर्णता/सावधानता; उच्च O = सौंदर्य/जिज्ञासा/रचनात्मकता/अपरंपरिकता। पर्यवेक्षक-रिपोर्ट रोगी-स्व-रिपोर्ट से पृथक सन्दर्भ में व्याख्या करें।",
                "HEXACO scores are descriptive personality profiles, not diagnostic thresholds — the instrument defines no clinical cut-offs. High H-H indicates sincerity, fairness, greed avoidance and modesty; high E indicates fearfulness, anxiety, dependence and sentimentality; high X indicates social self-esteem, social boldness, sociability and liveliness; high A indicates forgiveness, gentleness, flexibility and patience; high C indicates organization, diligence, perfectionism and prudence; high O indicates aesthetic appreciation, inquisitiveness, creativity and unconventionality. Interpret observer ratings alongside — not instead of — the patient's own report, and note the informant's relationship and exposure to the subject."),
            "psychometrics": bi(
                "आंतरिक सुसंगतता .77-.80 (कॉलेज नमूने) एवं .73-.80 (सामुदायिक नमूने); NEO-FFI से अभिसारी वैधता पर्याप्त (Ashton & Lee, 2009)।",
                "Internal-consistency reliabilities ranged .77 to .80 for college samples and .73 to .80 for community samples, with sufficient convergent validity against theoretically related scales such as the NEO Five-Factor Inventory (Ashton & Lee, 2009)."),
            "notDiagnostic": True,
            "disorders": [],
        },
        "licensing": bi(
            "HEXACO-PI-R / HEXACO-60, Kibeom Lee एवं Michael C. Ashton। मूल रूप व स्कोरिंग-कुंजी लेखकों द्वारा शोध/नैदानिक उपयोग हेतु मुक्त प्रकाशित; व्यावसायिक अथवा पुनर्विक्रय उपयोग हेतु उनकी अनुमति आवश्यक। यहाँ का हिन्दी रूपांतर कार्यशील अनुवाद है — नैदानिक प्रयोग से पूर्व समीक्षा कराएँ।",
            "HEXACO-PI-R / HEXACO-60 by Kibeom Lee, Ph.D. & Michael C. Ashton, Ph.D. Item wording and the scoring key are published freely by the authors for research and clinical use; commercial or redistributed use requires their permission. The Hindi rendering here is a working translation and should be reviewed before clinical use."),
        "translationNote": bi(
            "हिन्दी आइटम-रूप कार्यशील अनुवाद हैं; अंग्रेज़ी मूल प्राधिकृत है।",
            "Hindi item wording is a working translation; the English original is authoritative."),
        "branching": None,
    }


def domain_questions():
    """Screen-in item that deploys the observer form from the personality domain."""
    return [
        {
            "id": "per_hexaco_1",
            "text": bi(
                "क्या किसी निकट informants (परिवार/साथी/सहकर्मी) द्वारा व्यक्ति-ता-प्रोफाइल की पर्यवेक्षक-रेटिंग आवश्यक है — आत्म-रिपोर्ट की सीमाओं को आंकने या नैदानिक-सूचना हेतु?",
                "Is an informant-rated personality profile needed — to corroborate or challenge the person's own account, or because self-report alone is insufficient for the referral question?"),
            "scale": [
                {"v": 0, "label": bi("नहीं", "No")},
                {"v": 1, "label": bi("हाँ", "Yes")},
            ],
            "scaleId": "hexaco_pi_r_observer",
            "disorders": [],
        },
    ]


def merge(data):
    changed = False
    data["scales"]["hexaco_pi_r_observer"] = build_scale()

    pers = next((d for d in data["domains"] if d["id"] == "personality"), None)
    assert pers is not None, "personality domain missing - run scripts/build_pd.py first"
    existing_ids = {q["id"] for q in pers["questions"]}
    for q in domain_questions():
        if q["id"] not in existing_ids:
            pers["questions"].append(q)
            changed = True

    inst = data.setdefault("instruments", {})
    if "HEXACO-PI-R (Observer)" not in inst:
        inst["HEXACO-PI-R (Observer)"] = {
            "name": "HEXACO-PI-R Observer Report Form (60 items)",
            "construct": bi("Six-domain personality structure rated by an informant",
                            "पर्यवेक्षक द्वारा रेटित छह-डोमेन व्यक्तित्व-संरचना"),
            "format": bi(
                "60 statements rated 1 (strongly disagree) to 5 (strongly agree) about the person being described; 24 facet scales across 6 domains; R-keyed items reverse-scored; facet = mean of its items, domain = mean of its facets",
                "60 कथन, मूल्यांकन-विषय के विषय में 1 (पूर्णतः असहमत) से 5 (पूर्णतः सहमत) पर रेटित; 6 डोमेनों में 24 फलक-पैमाने; R-कुंजी आइटम व्युक्रम-अंकित; फलक = उसके आइटमों का माध्य, डोमेन = उसके फलकों का माध्य"),
            "duration": "~10-15 min",
            "language": bi("हिन्दी कार्यशील अनुवाद; अंग्रेज़ी मूल प्राधिकृत",
                           "Hindi working translation; English original authoritative"),
            "purpose": bi(
                "Obtain a personality profile from someone who knows the person well, to corroborate or challenge self-report and add observer-level information to the formulation. Descriptive only - it carries no diagnostic cut-offs.",
                "व्यक्ति को अच्छी तरह जानने वाले से व्यक्ति-ता-प्रोफाइल प्राप्त करना — आत्म-रिपोर्ट की पुष्टि/चुनौती एवं रूपरेखा में पर्यवेक्षक-स्तर की सूचना जोड़ना। केवल वर्णनात्मक — कोई नैदानिक कटऑफ नहीं।"),
            "source": "HEXACO-PI-R / HEXACO-60 (Lee & Ashton)",
            "licensing": bi(
                "मूल रूप व स्कोरिंग-कुंजी लेखकों द्वारा मुक्त-उपयोग हेतु प्रकाशित; व्यावसायिक/पुनर्विक्रय उपयोग हेतु अनुमति आवश्यक।",
                "Item wording and scoring key published freely by the authors; commercial or redistributed use requires their permission."),
        }
        changed = True

    ver = data["meta"].get("schemaVersion", "")
    if ver != SCHEMA_TARGET:
        data["meta"]["schemaVersion"] = SCHEMA_TARGET
        notes = data["meta"].setdefault("instrumentNotes", [])
        note = ("HEXACO-PI-R Observer Report Form implemented as scales.hexaco_pi_r_observer "
                "(60 informant-rated items, 1-5 scale, 24 facets across 6 domains, R items "
                "reverse-scored, facet/domain means reported on the 1-5 metric). Descriptive "
                "profile only - no diagnostic cut-offs. Item wording and the scoring key are "
                "those published by Lee & Ashton; confirm licensing terms for the deployment "
                "setting.")
        if note not in notes:
            notes.append(note)
        changed = True
    return changed


def main():
    check = "--check" in sys.argv
    data = json.loads(DATA.read_text(encoding="utf-8"))
    before = json.dumps(data, sort_keys=True, ensure_ascii=False)
    changed = merge(data)
    after = json.dumps(data, sort_keys=True, ensure_ascii=False)

    # integrity assertions
    sc = data["scales"]["hexaco_pi_r_observer"]
    assert len(sc["parts"][0]["questions"]) == 60, "expected 60 observer items"
    assert len(sc["facets"]) == 24, "expected 24 facets"
    assert len(sc["domains"]) == 6, "expected 6 domains"
    used = sorted(n for f in sc["facets"].values() for n in f["items"])
    assert used == list(range(1, 61)), "every item must belong to exactly one facet"
    rev_flagged = sorted(q["itemNumber"] for q in sc["parts"][0]["questions"] if q["reverseScored"])
    assert rev_flagged == sc["scoring"]["reverseItems"], "reverse flags must match the key"
    assert sum(len(v["facets"]) for v in sc["domains"].values()) == 24

    if check:
        print("would write schema %s | HEXACO observer items: 60 | facets: 24 | %s"
              % (data["meta"]["schemaVersion"], "changes pending" if (changed or before != after) else "up to date"))
        return
    DATA.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("wrote data.json schema %s | HEXACO observer items: 60 | facets: 24 | domains: 6"
          % data["meta"]["schemaVersion"])


if __name__ == "__main__":
    main()
