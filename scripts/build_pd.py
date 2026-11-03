#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_pd.py — Integrate the personality-disorder instruments into data.json:

  1. IPDE ICD-10 module screening questionnaire (Loranger, 1999)
     - 59 True/False screen items (numbering 1-59; item 3 is not printed on the
       form and is therefore omitted), keyed to the nine ICD-10 F60 clusters.
     - Screen rule (verbatim from the scoring summary): circle the keyed answer;
       "If three or more items from a disorder are circled, the subject has
       failed the screen for that disorder, and should be interviewed."
     - This app implements the *lower* sensitivity standard noted by the
       authors ("Clinicians and investigators may wish to adopt lower or higher
       screening standards"): any single keyed item flags its cluster.

  2. PDQ-4+ (from the CURE Counseling & Assessment Training Centre packet)
     - 99 True/False items + validity items 64 & 76, 12 DSM-IV cluster scales.
     - Thresholds per the Full Assessment Guide, including the Section B rules:
         Antisocial >=3 keyed AND >=3 checks in item 99 (conduct disorder)
         Borderline >=5 keyed AND >=2 checks in item 98 (impulsivity)
     - Mandatory clinical-significance follow-up questions A-E are attached to
       every positive PDQ-4+ scale as a clinician-rated checklist.

Both instruments are deployed through the existing `auto:pdscreen` routing:
the two screen-in questions of the `personality` domain each open one table.

Run:  python3 scripts/build_pd.py            (writes data.json in place)
      python3 scripts/build_pd.py --check    (validate only, no write)
"""
import json, sys, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'data.json')

def en_hi(en, hi):
    return {"en": en, "hi": hi}

# ---------------------------------------------------------------------------
# Shared T/F response option sets
# ---------------------------------------------------------------------------
TF = [{"v": 1, "label": en_hi("True", "सत्य")},
      {"v": 0, "label": en_hi("False", "मिथ्या")}]
YESNO = [{"v": 0, "label": en_hi("No", "नहीं")},
         {"v": 1, "label": en_hi("Yes", "हाँ")}]

GENERIC_PD_DISORDERS = ["other_specified_personality_disorder",
                        "unspecified_personality_disorder"]

# ---------------------------------------------------------------------------
# IPDE ICD-10 module screening questionnaire
# key: (item number, required answer) -> disorder code
# ---------------------------------------------------------------------------
IPDE_ITEMS_TEXT = {
    1:  "I usually get fun and enjoyment out of life.",
    2:  "I don't react well when someone offends me.",
    4:  "I can't decide what kind of person I want to be.",
    5:  "I show my feelings for everyone to see.",
    6:  "I let others make my big decisions for me.",
    7:  "I usually feel tense or nervous.",
    8:  "I almost never get angry about anything.",
    9:  "I go to extremes to try to keep people from leaving me.",
    10: "I am a very cautious person.",
    11: "I've never been arrested.",
    12: "People think I am cold and detached.",
    13: "I get into very intense relationships that don't last.",
    14: "Most people are fair and honest with me.",
    15: "I find it hard to disagree with people if I depend on them a lot.",
    16: "I feel awkward or out of place in social situations.",
    17: "I am too easily influenced by what goes on around me.",
    18: "I usually feel bad when I hurt or mistreat someone.",
    19: "I argue or fight when people try to stop me from doing what I want.",
    20: "At times I've refused to hold a job, even when I was expected to.",
    21: "When I am praised or criticized I don't show others my reaction.",
    22: "I've held grudges against people for years.",
    23: "I spend too much time trying to do things perfectly.",
    24: "People often make fun of me behind my back.",
    25: "I have never threatened suicide or injured myself on purpose.",
    26: "My feelings are like the weather; they are always changing.",
    27: "I fight for my rights even when it annoys people.",
    28: "I like to dress so I stand out in a crowd.",
    29: "I will lie or con someone if it serves my purpose.",
    30: "I don't stick with a plan if I don't get results right away.",
    31: "I have little or no desire to have sex with anyone.",
    32: "People think I am too strict about rules and regulations.",
    33: "I usually feel uncomfortable or helpless when I am alone.",
    34: "I won't get involved with people until I am certain they like me.",
    35: "I would rather not be the centre of attention.",
    36: "I think my spouse (lover) may be unfaithful to me.",
    37: "Sometimes I get so angry I break or smash things.",
    38: "I've had close friendships that lasted a long time.",
    39: "I worry a lot that people may not like me.",
    40: "I often feel 'empty' inside.",
    41: "I work so hard I don't have time left for anything else.",
    42: "I worry about being left alone and having to care for myself.",
    43: "A lot of things seem dangerous to me that don't bother most people.",
    44: "I have a reputation for being a flirt.",
    45: "I don't ask favors from people I depend on a lot.",
    46: "मुझे वे गतिविधियाँ पसंद हैं जो मैं अकेले कर सकूँ।",
    47: "I lose my temper and get into physical fights.",
    48: "People think I am too stiff or formal.",
    49: "I often seek advice or reassurance about everyday decisions.",
    50: "I keep to myself even when there are other people around.",
    51: "It's hard for me to stay out of trouble.",
    52: "I am convinced there is a conspiracy behind many things in the world.",
    53: "I'm very moody.",
    54: "It's hard for me to get used to a new way of doing things.",
    55: "Most people think I am a strange person.",
    56: "I take chances and do reckless things.",
    57: "Everyone needs a friend or two to be happy.",
    58: "I am more interested in my own thoughts than what goes on around me.",
    59: "I usually try to get people to do things my way.",
}

IPDE_HI_HINT = ("यह पाठ पत्रक के अंग्रेज़ी मूल से लिया गया है; हिन्दी रूपांतरण "
                "केवल संकेतात्मक सहायता हेतु है और इसमें कुछ वाक्य-विन्यास "
                "अस्पष्ट हैं। कृपया सत्यापित अंग्रेज़ी/IPDE संस्करण से पुष्टि करें।")

# rough machine Hindi for the IPDE stems (flagged as non-authoritative below)
IPDE_HI = {
    1: "मैं आमतौर पर जीवन से मज़ा और आनंद प्राप्त करता/करती हूँ।",
    2: "जब कोई मुझे अपमानित करे तो मैं अच्छी तरह प्रतिक्रिया नहीं करता/करती।",
    4: "मैं यह तय नहीं कर सकता/सकती कि मैं कैसा व्यक्ति बनना चाहता/चाहती हूँ।",
    5: "मैं अपने भाव सबको दिखाने देता/दिखाती हूँ।",
    6: "मैं अपने बड़े निर्णय दूसरों को करने देता/करने देती हूँ।",
    7: "मुझे आमतौर पर तनाव या घबराहट महसूस होती है।",
    8: "मैं लगभग किसी भी चीज़ पर कभी क्रोधित नहीं होता/होती।",
    9: "लोगों को खोने से रोकने हेतु मैं अति में जाता/जाती हूँ।",
    10: "मैं अत्यंत सावधान व्यक्ति हूँ।",
    11: "मुझे कभी गिरफ्तार नहीं किया गया।",
    12: "लोग मुझे ठंडा और विरक्त मानते हैं।",
    13: "मैं बहुत तीव्र संबंधों में उलझता/उलझती हूँ जो टिकते नहीं।",
    14: "अधिकतर लोग मेरे साथ न्यायपूर्ण और ईमानदार होते हैं।",
    15: "जिन पर मैं बहुत निर्भर हूँ उनसे असहमत होना मुझे कठिन लगता है।",
    16: "सामाजिक परिस्थितियों में मैं अजीब या बेढंगा महसूस करता/करती हूँ।",
    17: "मैं चारों ओर होने वाली बातों से बहुत सहजता से प्रभावित हो जाता/जाती हूँ।",
    18: "जब मैं किसी को ठेस पहुँचाता/पहुँचाती हूँ तो आमतौर पर बुरा महसूस करता/करती हूँ।",
    19: "जब लोग मेरी मनचाही चीज़ रोकने की कोशिश करते हैं तो मैं बहस या लड़ाई करता/करती हूँ।",
    20: "कभी-कभी मैंने नौकरी पकड़ने से इनकार किया है, भले अपेक्षा थी।",
    21: "प्रशंसा या आलोचना होने पर मैं अपनी प्रतिक्रिया दूसरों को नहीं दिखाता/दिखाती।",
    22: "मैं वर्षों तक लोगों के प्रति द्বেष रखता/रखती हूँ।",
    23: "चीज़ें पूर्ण करने के लिए मैं बहुत अधिक समय लगाता/लगाती हूँ।",
    24: "लोग अक्सर पीठ पीछे मेरा मज़ाक उड़ाते हैं।",
    25: "मैंने कभी आत्महत्या की धमकी नहीं दी या जान-बूझकर स्वयं को क्षति नहीं पहुँचाई।",
    26: "मेरी भावनाएँ मौसम की तरह हैं; ये सदैव बदलती रहती हैं।",
    27: "मैं अपने अधिकारों हेतु लड़ता/लड़ती हूँ भले लोगों को बुरा लगे।",
    28: "मुझे ऐसा पोशाक पहनना पसंद है जिससे भीड़ में मैं दिखूँ।",
    29: "अपने काम निकालने हेतु मैं झूठ बोल सकता/सकती हूँ या किसी को ठगा सकता/सकती हूँ।",
    30: "जल्दी परिणाम न मिले तो मैं योजना पर टिकता/टिकती नहीं।",
    31: "किसी के साथ यौन संबंध की मेरी इच्छा कम या शून्य है।",
    32: "लोग मानते हैं कि मैं नियम-कानूनों के बारे में बहुत कठोर हूँ।",
    33: "अकेले होने पर मुझे सहज नहीं या असहाय महसूस होता है।",
    34: "लोगों से जुड़ने से पहले निश्चित होना चाहता/चाहती हूँ कि वे मुझे पसंद करते हैं।",
    35: "मैं ध्यान का केंद्र नहीं बनना चाहता/चाहती।",
    36: "मुझे लगता है कि मेरे जीवनसाथी (प्रेमी/प्रेमिका) ने मेरे साथ विश्वासघात किया होगा।",
    37: "कभी-कभी इतना क्रोध आता है कि मैं चीज़ें तोड़ता/तोड़ती या फेंकता/फेंकती हूँ।",
    38: "मेरे पास दीर्घकालिक घनिष्ठ मित्रता रही हैं।",
    39: "लोग मुझे पसंद न करें, इसका बहुत चिंता करता/करती हूँ।",
    40: "अक्सर भीतर से खालीपन महसूस करता/करती हूँ।",
    41: "इतना कार्य करता/करती हूँ कि अन्य किसी चीज़ हेतु समय नहीं बचता।",
    42: "अकेले रह जाने और स्वयं की देखभाल करने की चिंता सताती है।",
    43: "कई चीज़ें मुझे खतरनाक लगती हैं जिनसे सामान्य लोग प्रभावित नहीं होते।",
    44: "मुछल्लद होने की मेरी साख है।",
    45: "जिन पर बहुत निर्भर हूँ उनसे मैं सहायता नहीं माँगता/माँगती।",
    46: "मुझे वे गतिविधियाँ पसंद हैं जो मैं अकेले कर सकूँ।",
    47: "मैं आत्म-नियंत्रण खोकर शारीरिक झगड़ों में उलझ जाता/जाती हूँ।",
    48: "लोग मुझे बहुत रूढ़/कठोर मानते हैं।",
    49: "रोज़मर्रा के निर्णय हेतु मैं प्रायः सलाह या आश्वासन माँगता/माँगती हूँ।",
    50: "आसपास लोग होने पर भी मैं स्वयं को अलग रखता/रखती हूँ।",
    51: "मुसीबत से दूर रहना मेरे लिए कठिन है।",
    52: "मुझे विश्वास है कि संसार की कई घटनाओं के पीछे षड्यंत्र है।",
    53: "मैं बहुत मिजाज़-परिवर्ती हूँ।",
    54: "किसी नए तरीके से कार्य करने का अभ्यस्त होना मेरे लिए कठिन है।",
    55: "अधिकतर लोग मुझे अजीब व्यक्ति मानते हैं।",
    56: "मैं जोखिम उठाता/उठाती और बेपरवाह कार्य करता/करती हूँ।",
    57: "सुखी रहने हेतु प्रत्येक को एक-दो मित्रों की आवश्यकता होती है।",
    58: "चारों ओर घटित होने वाली बातों की तुलना में मैं स्वयं के विचारों में अधिक रुचि रखता/रखती हूँ।",
    59: "मैं आमतौर पर लोगों को अपनी बात मनवाने का प्रयत्न करता/करती हूँ।",
}

# (module code, ICD-10 label, dsm label, items [(num,'T'|'F')], disorder key(s))
IPDE_MODULES = [
    ("F60.0", "Paranoid", "Paranoid Personality Disorder",
     [(2, 'F'), (14, 'F'), (24, 'F'), (36, 'T'), (52, 'T')], ["paranoid_personality_disorder"]),
    ("F60.1", "Schizoid", "Schizoid Personality Disorder",
     [(1, 'F'), (8, 'T'), (12, 'T'), (31, 'T'), (46, 'T'), (58, 'T')], ["schizoid_personality_disorder"]),
    ("F60.2", "Dissocial", "Antisocial Personality Disorder",
     [(11, 'F'), (18, 'F'), (20, 'T'), (27, 'T'), (29, 'T'), (51, 'T'), (56, 'T'), (59, 'T')],
     ["antisocial_personality_disorder"]),
    ("F60.30", "Impulsive", "Impulsive subtype / intermittent explosive features",
     [(19, 'T'), (30, 'T'), (37, 'T'), (47, 'T')], ["impulsive_control_features"]),
    ("F60.31", "Borderline", "Borderline Personality Disorder",
     [(4, 'T'), (9, 'T'), (13, 'T'), (25, 'F'), (26, 'T'), (40, 'T'), (53, 'T')],
     ["borderline_personality_disorder"]),
    ("F60.4", "Histrionic", "Histrionic Personality Disorder",
     [(5, 'T'), (17, 'T'), (28, 'T'), (35, 'F'), (44, 'T')], ["histrionic_personality_disorder"]),
    ("F60.5", "Anankastic", "Obsessive-Compulsive Personality Disorder",
     [(3, None), (10, 'T'), (23, 'T'), (32, 'T'), (41, 'T'), (48, 'T'), (54, 'T')],
     ["obsessive_compulsive_personality_disorder"]),
    ("F60.6", "Anxious (Avoidant)", "Avoidant Personality Disorder",
     [(7, 'T'), (16, 'T'), (34, 'T'), (39, 'T'), (43, 'T'), (50, 'T')],
     ["avoidant_personality_disorder"]),
    ("F60.7", "Dependent", "Dependent Personality Disorder",
     [(6, 'T'), (15, 'T'), (22, 'T'), (33, 'T'), (42, 'T'), (45, 'F'), (49, 'T'), (57, 'T')],
     ["dependent_personality_disorder"]),
]

# ---------------------------------------------------------------------------
# PDQ-4+ item text (cleaned from the scanned packet; numbering 1-99)
# ---------------------------------------------------------------------------
PDQ_ITEMS = {
    1:  "I avoid working with others who may criticize me.",
    2:  "I can't make decisions without the advice, or reassurance, of others.",
    3:  "I often get lost in details and lose sight of the \"big picture\".",
    4:  "I need to be the center of attention.",
    5:  "I have accomplished far more than others give me credit.",
    6:  "I'll go to extremes to prevent those whom I love from ever leaving me.",
    7:  "Others have complained that I do not keep up with my work or commitments.",
    8:  "I've been in trouble with the law several times (or would have been if I had been caught).",
    9:  "Spending time with family or friends just doesn't interest me.",
    10: "I get special messages from things happening around me.",
    11: "I know that people will take advantage of me, or try to cheat me, if I let them.",
    12: "Sometimes I get upset.",
    13: "I make friends with people only when I am sure they like me.",
    14: "I am usually depressed.",
    15: "I prefer that other people assume responsibility for me.",
    16: "I waste time trying to make things too perfect.",
    17: "I am \"sexier\" than most people.",
    18: "I often find myself thinking about how great a person I am, or will be.",
    19: "I either love someone or hate them, with nothing in between.",
    20: "I get into a lot of physical fights.",
    21: "I feel that others don't understand or appreciate me.",
    22: "I would rather do things by myself than with other people.",
    23: "I have the ability to know that some things will happen before they actually do.",
    24: "I often wonder whether the people I know can really be trusted.",
    25: "Occasionally I talk about people behind their backs.",
    26: "I am inhibited in my intimate relationships because I am afraid of being ridiculed.",
    27: "I fear losing the support of others if I disagree with them.",
    28: "I have many shortcomings.",
    29: "I put my work ahead of being with my family or friends or having fun.",
    30: "I show my emotions easily.",
    31: "Only certain special people can really appreciate and understand me.",
    32: "I often wonder who I really am.",
    33: "I have difficulty paying bills because I don't stay at any one job for very long.",
    34: "Sex just doesn't interest me.",
    35: "Others consider me moody and \"hot tempered\".",
    36: "I can often sense, or feel things, that others can't.",
    37: "Others will use what I tell them against me.",
    38: "There are some people I don't like.",
    39: "I am more sensitive to criticism or rejection than most people.",
    40: "I find it difficult to start something if I have to do it by myself.",
    41: "I have a higher sense of morality than other people.",
    42: "I am my own worst critic.",
    43: "I use my \"looks\" to get the attention that I need.",
    44: "I very much need other people to take notice or compliment me.",
    45: "I have tried to hurt or kill myself.",
    46: "I do a lot of things without considering the consequences.",
    47: "There are few activities that I have any interest.",
    48: "People often have difficulty understanding what I say.",
    49: "I object to supervisors telling me how I should do my job.",
    50: "I keep alert to figure out the real meaning of what people are saying.",
    51: "I have never told a lie.",
    52: "I am afraid to meet new people because I feel inadequate.",
    53: "I want people to like me so much that I volunteer to do things that I'd rather not do.",
    54: "I have accumulated lots of things that I don't need but I can't bear to throw out.",
    55: "Even though I talk a lot, people say that I have trouble getting to the point.",
    56: "I worry a lot.",
    57: "I expect other people to do favors for me even though I do not usually do favors for them.",
    58: "I am a very moody person.",
    59: "Lying comes easily to me and I often do it.",
    60: "I am not interested in having close friends.",
    61: "I am often on guard against being taken advantage of.",
    62: "I never forget, or forgive, those who do me wrong.",
    63: "I resent those who have more \"luck\" than I.",
    64: "A nuclear war may not be such a bad idea.",
    65: "When alone, I feel helpless and unable to care for myself.",
    66: "If others can't do things correctly, I would prefer to do them myself.",
    67: "I have a flair for the dramatic.",
    68: "Some people think that I take advantage of others.",
    69: "I feel that my life is dull and meaningless.",
    70: "I am critical of others.",
    71: "I don't care what others have to say about me.",
    72: "I have difficulties relating to others in a one-to-one situation.",
    73: "People have often complained that I did not realize that they were upset.",
    74: "By looking at me, people might think that I'm pretty odd, eccentric or weird.",
    75: "I enjoy doing risky things.",
    76: "I have lied a lot on this questionnaire.",
    77: "I complain a lot about my hardships.",
    78: "I have difficulty controlling my anger or temper.",
    79: "Some people are jealous of me.",
    80: "I am easily influenced by others.",
    81: "I see myself as thrifty, but others see me as being cheap.",
    82: "I am terrified of being left to care for myself.",
    83: "I suffer from low self-esteem.",
    84: "I am a pessimist.",
    85: "I waste no time in getting back at people who insult me.",
    86: "Being around other people makes me nervous.",
    87: "In new situations, I fear being embarrassed.",
    88: "I take relationships more seriously than do those who I'm involved with.",
    89: "People complain that I'm \"stubborn as a mule\".",
    90: "When a close relationship ends, I need to get involved with someone else immediately.",
    91: "I can be nasty with someone one minute, then find myself apologizing to them the next minute.",
    92: "Others consider me to be stuck up.",
    93: "When stressed, things happen, like I get paranoid or just \"black out\".",
    94: "I don't care if others get hurt so long as I get what I want.",
    95: "I keep my distance from others.",
    96: "I often wonder whether my wife (husband, girlfriend or boyfriend) has been unfaithful to me.",
    97: "I often feel guilty.",
    98: "When I was an adult, I have done things on impulse that could have gotten me into trouble.",
    99: "When I was a kid (before age 15), I was somewhat of a juvenile delinquent, doing some of the things below.",
}

PDQ_HI_HINT = ("यह पाठ CURE पैकेट के स्कैन किए गए अंग्रेज़ी पत्रक से लिया गया है; "
               "हिन्दी रूपांतरण केवल संकेतात्मक सहायता हेतु है और इसमें कुछ "
               "वाक्य-विन्यास अस्पष्ट हैं। कृपया सत्यापित PDQ-4+ संस्करण से पुष्टि करें।")

PDQ_SCALES = [
    # slug, code(abbrev), name-en, threshold, keyed-true items, disorders
    ("Paranoid",   "Par", "Paranoid",                 4,
     [11, 24, 37, 50, 62, 85, 96], ["paranoid_personality_disorder"]),
    ("Schizoid",   "Szid", "Schizoid",                4,
     [9, 22, 34, 47, 60, 71, 95], ["schizoid_personality_disorder"]),
    ("Schizotypal", "Sztp", "Schizotypal",            5,
     [1, 10, 23, 31, 36, 48, 61, 72, 74, 86], ["schizotypal_personality_disorder"]),
    ("Antisocial", "Ant", "Antisocial",               3,
     [8, 20, 33, 46, 59, 75, 94], ["antisocial_personality_disorder"],
     "sectionB_99"),
    ("Borderline", "Bor", "Borderline",               5,
     [6, 19, 32, 45, 58, 69, 78, 93], ["borderline_personality_disorder"],
     "sectionB_98"),
    ("Histrionic", "His", "Histrionic",               4,
     [4, 17, 30, 43, 55, 67, 80, 90], ["histrionic_personality_disorder"]),
    ("Narcissistic", "Nar", "Narcissistic",           5,
     [5, 18, 31, 44, 57, 68, 73, 79, 92], ["narcissistic_personality_disorder"]),
    ("Avoidant",   "Av", "Avoidant",                  4,
     [1, 13, 26, 39, 52, 83, 87], ["avoidant_personality_disorder"]),
    ("Dependent",  "Dep", "Dependent",                5,
     [2, 15, 27, 40, 53, 65, 82], ["dependent_personality_disorder"]),
    ("OC",         "OC", "Obsessive-Compulsive",      4,
     [3, 16, 29, 41, 54, 66, 81, 89], ["obsessive_compulsive_personality_disorder"]),
    ("Negativistic", "Neg", "Passive-Aggressive (Negativistic)", 4,
     [7, 21, 35, 49, 63, 77, 91], ["passive_aggressive_personality_disorder"]),
    ("Depressive", "Dpt", "Depressive",               5,
     [14, 28, 42, 56, 70, 84, 97], ["depressive_personality_disorder"]),
]

PDQ_IMULSE_98 = [
    ("i98_spend", "Spend more money than I have."),
    ("i98_sex", "Having sex with people I hardly know."),
    ("i98_drink", "Drinking too much."),
    ("i98_drugs", "Taking drugs."),
    ("i98_binge", "Eating binges."),
    ("i98_drive", "Reckless driving."),
]

PDQ_CD_99 = [
    ("cd99_bully", "I was considered a bully."),
    ("cd99_fights", "I used to start fights with other kids."),
    ("cd99_weapon", "I used a weapon in fights that I had."),
    ("cd99_rob", "I robbed or mugged other people."),
    ("cd99_cruel_people", "I was physically cruel to other people."),
    ("cd99_cruel_animals", "I was physically cruel to animals."),
    ("cd99_sex", "I forced someone to have sex with me."),
    ("cd99_lie", "I lied a lot."),
    ("cd99_stay_out", "I stayed out at night without permission."),
    ("cd99_steal", "I stole things from others."),
    ("cd99_fire", "I set fires."),
    ("cd99_property", "I broke windows or destroyed property."),
    ("cd99_runaway", "I ran away from home overnight more than once."),
    ("cd99_truancy", "I began skipping school a lot before age 13."),
    ("cd99_break_in", "I broke into someone's house, building, or car."),
]

PDQ_CS_QUESTIONS = [
    ("cs_a", "Are all these items totally true for you?",
     "Accuracy — client must confirm (or remove false positives)"),
    ("cs_b", "How long have these traits been part of your personality?",
     "Duration — most of life / since before age 18"),
    ("cs_c", "Are these traits present even when you're NOT depressed, anxious, using substances, or physically ill?",
     "Pervasiveness — not limited to transient states"),
    ("cs_d", "Have these traits caused problems in work, relationships, or home life?",
     "Impairment — yes in at least one area"),
    ("cs_e", "Do these traits bother you or cause you distress?",
     "Distress — yes"),
]

SAFETY_ITEMS = {45, 64, 76}   # 45 suicidal behaviour; 64/76 validity infrequency

# Curated Hindi rendering of the PDQ-4+ stems. The English wording is the
# authoritative item text (transcribed from the packet); these labels are a
# clinician-reviewable aid, never a replacement.
PDQ_HI = {
    1: "मैं उन लोगों के साथ काम करने से परहेज करता/करती हूँ जो मुझे आलोचित कर सकते हैं।",
    2: "दूसरों की सलाह या आश्वासन के बिना मैं निर्णय नहीं ले सकता/सकती।",
    3: "मैं प्रायः विवरणों में खो जाता/जाती हूँ और 'पूरी तस्वीर' देखना भूल जाता/जाती हूँ।",
    4: "मुझे ध्यान का केंद्र बनने की आवश्यकता होती है।",
    5: "मैंने इतनी अधिक सफलता अर्जित की है जितना लोग मुझे श्रेय देते हैं।",
    6: "प्रियजनों को मुझसे दूर जाने से रोकने हेतु मैं अति में जाता/जाती हूँ।",
    7: "लोग शिकायत करते हैं कि मैं अपना कार्य या प्रतिबद्धताएँ पूरी नहीं करता/करती।",
    8: "कानून से मेरे कई बार झंझट रहे हैं (अथवा होते यदि पकड़ा जाता)।",
    9: "परिवार या मित्रों के साथ समय बिताने में मुझे रुचि नहीं है।",
    10: "चारों ओर घटित होने वाली बातों से मुझे विशेष संदेश मिलते हैं।",
    11: "मुझे ज्ञात है कि लोग मुझे ठगा करेंगे अथवा दोहन करेंगे यदि मैं अनुमति दूँ।",
    12: "कभी-कभी मैं परेशान हो जाता/जाती हूँ।",
    13: "मैं लोगों से मित्रता तभी करता/करती हूँ जब निश्चित होऊँ कि वे मुझे पसंद करते हैं।",
    14: "मैं प्रायः अवसादग्रस्त रहता/रहती हूँ।",
    15: "मैं चाहता/चाहती हूँ कि अन्य लोग मेरे लिए उत्तरदायित्व लें।",
    16: "चीज़ों को अत्यंत पूर्ण बनाने के प्रयास में मैं समय बर्बाद करता/करती हूँ।",
    17: "मैं अधिकतर लोगों की तुलना में अधिक आकर्षक/आकर्षी हूँ।",
    18: "मैं प्रायः स्वयं को यह सोचते पाता/पाती हूँ कि मैं कितना महान व्यक्ति हूँ अथवा हूँगा।",
    19: "मैं किसी से या तो प्रेम करता/करती हूँ या घृणा, बीच का कुछ नहीं।",
    20: "मेरे कई शारीरिक झगड़े होते हैं।",
    21: "मुझे लगता है कि अन्य लोग मुझे समझते नहीं या सराहते नहीं।",
    22: "मैं अन्य लोगों के साथ करने की बजाय कार्य स्वयं करना पसंद करता/करती हूँ।",
    23: "कुछ घटनाएँ घटने से पूर्व ही जानने की क्षमता मुझमें है।",
    24: "मैं प्रायः सोचता/सोचती हूँ कि क्या मेरे परिचित सच में विश्वसनीय हैं।",
    25: "कभी-कभी मैं पीठ पीछे लोगों की बात करता/करती हूँ।",
    26: "उपहास के भय से मैं अपने घनिष्ठ संबंधों में संकोची रहता/रहती हूँ।",
    27: "उनसे असहमत होने पर दूसरों का समर्थन खोने का भय सताता है।",
    28: "मुझे अनेक कमियाँ हैं।",
    29: "मैं परिवार, मित्रों या आनंद से पहले अपना कार्य रखता/रखती हूँ।",
    30: "मैं सहजता से अपनी भावनाएँ प्रकट करता/करती हूँ।",
    31: "केवल कुछ विशेष व्यक्ति ही वास्तव में मुझे सराह व समझ सकते हैं।",
    32: "मैं प्रायः सोचता/सोचती हूँ कि वास्तव में मैं कौन हूँ।",
    33: "बिल चुकाने में कठिनाई होती है क्योंकि मैं कोई नौकरी अधिक काल तक नहीं करता/करती।",
    34: "यौन विषय में मुझे रुचि नहीं है।",
    35: "लोग मुझे मिजाज़ी व 'गर्म स्वभाव' का मानते हैं।",
    36: "मैं प्रायः ऐसी बातें अनुभव कर सकता/सकती हूँ जो अन्य नहीं कर सकते।",
    37: "लोग मेरी कही बात मेरे विरुद्ध प्रयोग करेंगे।",
    38: "कुछ लोग ऐसे हैं जिन्हें मैं पसंद नहीं करता/करती।",
    39: "आलोचना या अस्वीकृति प्रति अधिकतर लोगों की अपेक्षा मैं अधिक संवेदनशील हूँ।",
    40: "स्वयं से करना पड़े तो आरंभ करने में कठिनाई होती है।",
    41: "अन्य लोगों की तुलना में मेरा नैतिक बोध उच्चतर है।",
    42: "मैं स्वयं का सबसे कठोर आलोचक हूँ।",
    43: "मुझे चाहिए वाला ध्यान पाने हेतु मैं अपना 'रूप' प्रयोग करता/करती हूँ।",
    44: "मुझे अत्यंत आवश्यकता है कि लोग मुझे ध्यान दें या प्रशंसा करें।",
    45: "मैंने स्वयं को क्षति पहुँचाने अथवा आत्महत्या के प्रयास किए हैं।",
    46: "मैं परिणामों को विचारे बिना अनेक कार्य करता/करती हूँ।",
    47: "ऐसी गतिविधियाँ कम हैं जिनमें मुझे रुचि है।",
    48: "लोगों को मेरी बात समझने में कठिनाई होती है।",
    49: "अधिकारी द्वारा कार्य-विधि बताने का मैं विरोध करता/करती हूँ।",
    50: "लोगों की बात का वास्तविक अर्थ जानने हेतु मैं सतर्क रहता/रहती हूँ।",
    51: "मैंने कभी झूठ नहीं बोला।",
    52: "नए लोगों से मिलने से भय लगता है क्योंकि मैं अपर्याप्त अनुभव करता/करती हूँ।",
    53: "लोग मुझे पसंद करें, इसकी इतनी इच्छा है कि अनचाहे कार्य भी स्वैच्छिक करता/करती हूँ।",
    54: "अनेक अनावश्यक वस्तुएँ जमा कर चुका हूँ पर फेंकने की सहनशक्ति नहीं।",
    55: "अधिक बोलने के बावजूद लोग कहते हैं कि मैं मुख्य बात तक नहीं पहुँच पाता/पहुँचती।",
    56: "मैं बहुत चिंता करता/करती हूँ।",
    57: "मुझे आशा है कि अन्य मेरे उपकार करेंगे यद्यपि मैं प्रायः उनके नहीं करता/करती।",
    58: "मैं अत्यंत मिजाज़-परिवर्ती व्यक्ति हूँ।",
    59: "झूठ बोलना मुझे सहज है और मैं प्रायः बोलता/बोलती हूँ।",
    60: "घनिष्ठ मित्रता रखने में मेरी रुचि नहीं है।",
    61: "दोहन हुए जाय, इससे बचने हेतु मैं प्रायः सतर्क रहता/रहती हूँ।",
    62: "मुझे अन्याय करने वालों को न भूलता/भूलती हूँ, न क्षमा करता/करती हूँ।",
    63: "जिनका भाग्य मुझसे अच्छा है उनपर मुझे कड़वाहट होती है।",
    64: "परमाणु युद्ध इतना बुरा विचार न हो।",
    65: "अकेले होने पर असहाय व स्वयं की देखभाल में असमर्थ अनुभव करता/करती हूँ।",
    66: "अन्य सही ढंग से न करें तो मैं कार्य स्वयं करना पसंद करता/करती हूँ।",
    67: "मुझे नाटकीयता की सहज शैली है।",
    68: "कुछ लोग सोचते हैं कि मैं दूसरों का दोहन करता/करती हूँ।",
    69: "मुझे लगता है मेरा जीवन रसहीन व निरर्थक है।",
    70: "मैं दूसरों की आलोचना करता/करती हूँ।",
    71: "लोग मेरे विषय क्या कहते हैं, इससे मुझे फर्क नहीं पड़ता।",
    72: "एक-से-एक परिस्थिति में संबंध बनाने में कठिनाई होती है।",
    73: "लोग शिकायत करते रहे कि मैं उनकी उद्विग्नाता पहचान नहीं पाता/पाती।",
    74: "मुझे देखकर लोग सोच सकते हैं कि मैं बहुत अजीब, विचित्र हूँ।",
    75: "जोखिम वाले कार्य करने में मुझे आनंद मिलता है।",
    76: "इस प्रश्नावली में मैंने बहुत झूठ बोला है।",
    77: "मैं अपनी कठिनाइयों की बहुत शिकायत करता/करती हूँ।",
    78: "क्रोध या प्रकोप पर नियंत्रण में कठिनाई होती है।",
    79: "कुछ लोग मुझसे ईर्ष्या करते हैं।",
    80: "मैं दूसरों से सहजता से प्रभावित हो जाता/जाती हूँ।",
    81: "मैं स्वयं को मितव्ययी मानता/मानती हूँ पर लोग कंजूस मानते हैं।",
    82: "स्वयं की देखभाल हेतु अकेले छोड़े जाने का भय सताता है।",
    83: "मैं निम्न आत्म-सम्मान से पीड़ित हूँ।",
    84: "मैं निराशावादी हूँ।",
    85: "अपमान करने वालों से बदला लेने में देर नहीं लगाता/लगाती।",
    86: "लोगों के बीच रहने पर घबराहट होती है।",
    87: "नई परिस्थितियों में अपमानित होने का भय लगता है।",
    88: "मैं संबंधों को अपने सहभागियों की अपेक्षा अधिक गंभीरता से लेता/लेती हूँ।",
    89: "लोग शिकायत करते हैं कि मैं अत्यंत ज़िद्दी हूँ।",
    90: "घनिष्ठ संबंध समाप्त होते ही तुरंत किसी अन्य से जुड़ना आवश्यक लगता है।",
    91: "एक पल किसी पर नाराज़, अगले पल क्षमायाचना — ऐसा होता है।",
    92: "लोग मुझे घमंडी मानते हैं।",
    93: "तनाव में ऐसी बातें होती हैं जैसे अत्यधिक संदेहवाद अथवा स्मृति-छाया (black out)।",
    94: "अपना काम निकलने तक दूसरों को क्षति हो तो मुझे परवाह नहीं।",
    95: "मैं दूसरों से दूरी बनाए रखता/रखती हूँ।",
    96: "मैं प्रायः सोचता/सोचती हूँ कि क्या मेरे जीवनसाथी ने विश्वासघात किया।",
    97: "मुझे प्रायः अपराधबोध होता है।",
    98: "वयस्क होने पर आवेगी कार्य किए जो मुझे मुसीबत में डाल सकते थे।",
    99: "15 वर्ष से पूर्व बचपन में मैं कुछ हद तक किशोर-अपराधी था; नीचे दी गई कुछ बातें करता था।",
}

# Hindi for the Section-B sub-items and the clinical-significance follow-ups
PDQ_SUBITEM_HI = {
    "i98_spend": "मेरे पास से अधिक धन व्यय करना।",
    "i98_sex": "परिचित न लोगों के साथ यौन संबंध।",
    "i98_drink": "अधिक शराब सेवन।",
    "i98_drugs": "मादक द्रव्य लेना।",
    "i98_binge": "अतिभोजन के एपिसोड।",
    "i98_drive": "बेपरवाह ड्राइविंग।",
    "cd99_bully": "मुझे दुर्व्यवहारकारी माना जाता था।",
    "cd99_fights": "मैं अन्य बच्चों से झगड़े आरंभ करता था।",
    "cd99_weapon": "झगड़ों में मैंने अस्त्र प्रयोग किया।",
    "cd99_rob": "मैं लोगों को लूटता था।",
    "cd99_cruel_people": "मैं लोगों के प्रति शारीरिक रूप से क्रूर था।",
    "cd99_cruel_animals": "मैं पशुओं के प्रति शारीरिक रूप से क्रूर था।",
    "cd99_sex": "मैंने किसी को बलपूर्वक संबंध बनाने को बाध्य किया।",
    "cd99_lie": "मैं बहुत झूठ बोलता था।",
    "cd99_stay_out": "अनुमति बिना रात भर बाहर रहता था।",
    "cd99_steal": "मैं दूसरों की वस्तुएँ चुराता था।",
    "cd99_fire": "मैं आग लगाता था।",
    "cd99_property": "मैं खिड़कियाँ तोड़ता या संपत्ति नष्ट करता था।",
    "cd99_runaway": "एक से अधिक बार घर से रात भर गायब हुआ।",
    "cd99_truancy": "13 वर्ष से पूर्व मैं विद्यालय प्रायः छूटता था।",
    "cd99_break_in": "मैं किसी के घर, भवन या वाहन में सेंध लगाता था।",
    "cs_a": "क्या ये सभी आइटम आपके लिए पूर्णतः सत्य हैं?",
    "cs_b": "ये लक्षण कब से आपके व्यक्तित्व का अंग हैं?",
    "cs_c": "क्या ये लक्षण तब भी विद्यमान हैं जब आप अवसादग्रस्त, चिंतित, पदार्थाधीन अथवा शारीरिक रूप से रोगी नहीं हैं?",
    "cs_d": "क्या इन लक्षणों ने कार्य, संबंध या गृह-जीवन में समस्याएँ उत्पन्न की हैं?",
    "cs_e": "क्या ये लक्षण आपको परेशान करते हैं अथवा पीड़ा देते हैं?",
}


# ---------------------------------------------------------------------------
# Build the two scale definitions
# ---------------------------------------------------------------------------
def build_ipde_scale():
    parts = []
    for code, name_en, dsm_name, keys, dis in IPDE_MODULES:
        qs = []
        for num, ans in keys:
            if ans is None:   # IPDE item 3: not printed on the form
                continue
            q = {
                "id": "ipde_%d" % num,
                "text": en_hi(IPDE_ITEMS_TEXT[num], IPDE_HI.get(num, IPDE_ITEMS_TEXT[num])),
                "keyedAnswer": ans,          # 'T' or 'F' counts toward the screen
                "screenItems": code,
                "disorders": list(dis),
            }
            if num == 25:                    # suicidal-threat stem -> safety flag
                q["safety"] = True
            qs.append(q)
        parts.append({
            "id": "ipde_" + code.replace(".", "_"),
            "name": en_hi("%s %s" % (code, name_en), "%s %s" % (code, name_en)),
            "icd10Module": code,
            "disorderName": en_hi(dsm_name, dsm_name),
            "disorders": list(dis),
            "questions": qs,
        })
    return {
        "id": "ipde_screen",
        "name": en_hi("IPDE ICD-10 Module Screening Questionnaire",
                      "IPDE ICD-10 माड्यूल स्क्रीनिंग प्रश्नावली"),
        "type": "matrix",
        "administeredBy": "self-or-clinician",
        "sourceInstrument": "IPDE",
        "targetAge": ["adult"],
        "directions": en_hi(
            "Please do not skip any item. If you are not sure of an answer, select the one TRUE or FALSE which is more likely to be correct. There is no time limit, but do not spend too much time thinking about the answer to any single statement. When the answer is TRUE, mark T. When the answer is FALSE, mark F.",
            "कृपया किसी भी item को छोड़ें नहीं। उत्तर में निश्चित न हों तो सत्य अथवा मिथ्या में से अधिक संभावित सही चुनें। समय की सीमा नहीं है, किंतु किसी एक कथन पर अत्यधिक चिंतन न करें। उत्तर सत्य हो तो T और मिथ्या हो तो F अंकित करें।"),
        "timeframe": en_hi(
            "Rate how you generally are, not how you feel at this moment.",
            "सामान्य स्व का मूल्यांकन करें, इस क्षण की भावना का नहीं।"),
        "parts": parts,
        "matrixOptions": TF,
        "scoring": {
            "method": "ipde_keyed_answer_screen",
            "rule": en_hi(
                "Circle the item numbers not followed by F, if they were answered True. Circle the remaining item numbers (those followed by F), if they were answered False. If three or more items from a disorder are circled, the subject has failed the screen for that disorder, and should be interviewed.",
                "जिन आइटम संख्याओं के पास F नहीं है उनको सत्य उत्तर पर वृत्त करें। शेष (F वाले) को मिथ्या उत्तर पर वृत्त करें। यदि किसी विकार के तीन अथवा अधिक आइटम वृत्त हुए तो उस विकार की स्क्रीन असफल हुई और साक्षात्कार आवश्यक है।"),
            "failThreshold": 3,
            "appStandard": en_hi(
                "This application applies the LOWER screening standard permitted by the instrument's authors ('clinicians and investigators may wish to adopt lower or higher screening standards'): ONE or more keyed items flags the ICD-10 F60 cluster for the full IPDE interview. The screen is not diagnostic and yields no dimensional score.",
                "यह एप्लिकेशन लेखकों द्वारा अनुमत निम्नतर स्क्रीनिंग मानदंड लागू करता है: एक अथवा अधिक कुंजी-उत्तर आइटम ICD-10 F60 क्लस्टर को पूर्ण IPDE साक्षात्कार हेतु चिह्नित करता है। यह स्क्रीन रोग-निर्णायक नहीं है और कोई विमानी अंक नहीं देती।"),
            "positiveThreshold": 1,
            "note": en_hi(
                "The screen should not be used to make a diagnosis or to calculate a dimensional score for a personality disorder.",
                "व्यक्तित्व विकार का रोग-निर्णय अथवा विमानी अंक हेतु स्क्रीन का प्रयोग न करें।"),
        },
        "sourcePages": "IPDE International Personality Disorder Examination — ICD-10 module screening questionnaire & scoring summary",
        "licensingNote": en_hi(
            "IPDE screening form reproduced for local clinical/research use; verify current licensing with the instrument publisher before redistribution.",
            "स्थानीय नैदानिक /शोध प्रयोग हेतु अभिलिखित; पुनर्वितरण से पूर्व प्रकाशक लाइसेंस सत्यापित करें।"),
        "translationNote": en_hi(
            "Item wording is transcribed verbatim from the English screening form. Hindi labels are a machine-assisted aid flagged for clinician review; the printed form omits item 3.",
            IPDE_HI_HINT),
    }


def build_pdq_scale():
    items = []
    for num in range(1, 100):
        q = {
            "id": "pdq_%d" % num,
            "text": en_hi(PDQ_ITEMS[num], PDQ_HI.get(num, PDQ_ITEMS[num])),
            "itemNumber": num,
        }
        if num in SAFETY_ITEMS:
            q["safety"] = True
        if num in (98, 99):
            q["isSectionB"] = True
        items.append(q)

    sectionB = [
        {
            "id": "pdq_98_impulsivity",
            "linkedItem": 98,
            "name": en_hi("Item 98 — Impulsive activities (check those that apply)",
                          "आइटम 98 — आवेगी गतिविधियाँ (लागू होने पर चिह्नित करें)"),
            "options": YESNO,
            "questions": [{"id": pid, "text": en_hi(txt, PDQ_SUBITEM_HI.get(pid, txt))} for pid, txt in PDQ_IMULSE_98],
        },
        {
            "id": "pdq_99_conduct",
            "linkedItem": 99,
            "name": en_hi("Item 99 — Juvenile conduct problems before age 15 (check those that apply)",
                          "आइटम 99 — 15 वर्ष से पूर्व किशोरावस्था की आचरण समस्याएँ (लागू होने पर चिह्नित करें)"),
            "options": YESNO,
            "questions": [{"id": cid, "text": en_hi(txt, PDQ_SUBITEM_HI.get(cid, txt))} for cid, txt in PDQ_CD_99],
        },
    ]

    cs_part = {
        "id": "pdq_clinical_significance",
        "name": en_hi("Clinical Significance Evaluation (mandatory follow-up for each flagged scale)",
                     "नैदानिक महत्व मूल्यांकन (चिह्नित प्रत्येक पैमाने हेतु अनिवार्य अनुवर्ती)"),
        "clinicianRated": True,
        "options": YESNO,
        "questions": [{"id": qid, "text": en_hi(q, PDQ_SUBITEM_HI.get(qid, q)), "criterionNote": note}
                      for qid, q, note in PDQ_CS_QUESTIONS],
    }

    scales_meta = []
    for entry in PDQ_SCALES:
        slug, abbr, name_en, thr, keys, dis = entry[:6]
        sm = {"slug": slug, "profileColumn": abbr, "name": en_hi(name_en, name_en),
              "threshold": thr, "items": keys, "disorders": list(dis)}
        if len(entry) > 6:
            sm["requiresSectionB"] = entry[6]
        scales_meta.append(sm)

    return {
        "id": "pdq4_screen",
        "name": en_hi("PDQ-4+ Personality Questionnaire (99 items)",
                      "PDQ-4+ व्यक्तित्व प्रश्नावली (99 आइटम)"),
        "type": "matrix",
        "administeredBy": "self-report",
        "sourceInstrument": "PDQ-4+",
        "targetAge": ["adult"],
        "directions": en_hi(
            "The purpose of this personality questionnaire is for you to describe the kind of person you are. When answering the questions, think about how you have tended to feel, think, and act over the past several years. Please answer either True or False to each item. T (True) means that the statement is generally true for you. F (False) means that the statement is generally false for you. Even if you are not entirely sure about the answer, indicate T or F for every question. There are no correct answers. You may take as much time as you wish.",
            "इस व्यक्तित्व प्रश्नावली का उद्देश्य आप द्वारा स्व वर्णन है। उत्तर देते समय गत कुछ वर्षों में अपनी भावना, विचार एवं व्यवहार पर विचार करें। प्रत्येक कथन हेतु सत्य अथवा मिथ्या चुनें। T अर्थ आप हेतु सामान्यतः सत्य; F अर्थ सामान्यतः मिथ्या। पूर्ण निश्चितता न हो तoby प्रत्येक प्रश्न का उत्तर अवश्य दीजिए। कोई सही अथवा गलत उत्तर नहीं है।"),
        "timeframe": en_hi(
            "Answer based on long-standing patterns, not temporary states (e.g., mood episodes, substance use).",
            "दीर्घकालिक रूपों पर उत्तर देें, अस्थायी अवस्थाओं पर नहीं (जैसे मूड एपिसोड, पदार्थ सेवन)।"),
        "parts": [{
            "id": "pdq_items",
            "name": en_hi("Personality Questionnaire Items", "व्यक्तित्व प्रश्नावली आइटम"),
            "questions": items,
        }] + sectionB + [cs_part],
        "matrixOptions": TF,
        "validity": {
            "items": [
                {"id": "pdq_64", "statement": en_hi("A nuclear war may not be such a bad idea.", "परमाणु युद्ध इतना बुरा विचार न हो।"),
                 "pathologicalResponse": "True",
                 "meaning": en_hi("Suggests random, exaggerated, or invalid responding.",
                                  "यादृच्छिक/ अतिरंजित अथवा अमान्य प्रतिविमर्श सूचित।")},
                {"id": "pdq_76", "statement": en_hi("I have lied a lot on this questionnaire.", "इस प्रश्नावली में मैंने बहुत झूठ बोला है।"),
                 "pathologicalResponse": "True",
                 "meaning": en_hi("Indicates response distortion or poor validity.",
                                  "प्रतिविमर्श विकृति अथवा निम्न वैधता सूचित।")},
            ],
            "rule": en_hi(
                "Before scoring, check these infrequency/validity items. If either is True, interpret results with extreme caution or consider the profile invalid.",
                "अंकन से पूर्व ये अवरण/वैधता आइटम जाँचें। यदि कोई एक सत्य हो तो परिणाम अत्यंत सावधानी से व्याख्यायित करें अथवा प्रोफ़ाइल अमान्य मानें।"),
        },
        "scales": scales_meta,
        "scoring": {
            "method": "pdq4_true_count_thresholds_with_section_b",
            "countRule": en_hi(
                "Count only True responses on the keyed items of each scale. Item 60 appears on both Schizoid and Schizotypal — count it once.",
                "प्रत्येक पैमाने के कुंजी-आइटम में केवल सत्य गनें। आइटम 60 Sczoid एवं Schizotypal दोनों में है — एक वार गनें।"),
            "sectionB": {
                "pdq_98_impulsivity": {"minimum": 2, "gateScale": "Borderline"},
                "pdq_99_conduct": {"minimum": 3, "gateScale": "Antisocial"},
            },
            "clinicalSignificance": en_hi(
                "A PD screen is only clinically significant if criteria A-E (accuracy, duration, pervasiveness, impairment, distress) are ALL met after the initial positive screen. If any criterion fails, the screen is not clinically meaningful (e.g., due to state effects, exaggeration, or transient stress).",
                "प्रारंभिक धनात्मक स्क्रीन पश्चात् A-E (यथार्थता, कालावधि, व्यापकता, बाधा, पीड़ा) सभी मानदंड पूर्त हों तो ही स्क्रीन नैदानिक दृष्ट्या महत्वपूर्ण है। कोई एक असफल तो स्क्रीन नैदानिक दृष्ट्या अर्थहीन।"),
            "comorbidityNote": en_hi(
                "High comorbidity is common (e.g., Borderline + Avoidant + Depressive).",
                "सह-रोगिता सामान्य है (जैसे सीमांत+ परिहरण+ अवसाद)।"),
            "notDiagnosticNote": en_hi(
                "The PDQ-4+ is a self-report screening tool; it is not diagnostic but identifies individuals who may warrant a structured clinical interview for a personality disorder.",
                "PDQ-4+ स्व-वर्णित_स्क्रीनिंग_साधन_है;_रोग-निर्णायक_नहीं,_किंतु_संरचित_नैदानिक_साक्षात्कार_के_पात्र_व्यक्तियों_को_चिह्नित_करता_है।"),
        },
        "sourcePages": "PDQ-4+ instructions, profile sheet and Full Assessment Guide (CURE Counseling & Assessment Training Centre packet)",
        "licensingNote": en_hi(
            "PDQ-4+ content transcribed from the provided packet; verify current licensing/warranties before clinical redistribution.",
            "प्रदत्त पैकेट से अभिलिखित; नैदानिक पुनर्वितरण से पूर्व वर्तमान लाइसेंस सत्यापित करें।"),
        "translationNote": en_hi(
            "English item wording was reconstructed from a low-quality scan; obvious OCR artifacts were repaired and the reconstruction is flagged for clinician review against the published PDQ-4+ form.",
            PDQ_HI_HINT),
    }


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


def main(check=False):
    data = json.load(open(DATA, encoding='utf-8'))

    ipde = build_ipde_scale()
    pdq = build_pdq_scale()
    dom = build_domain()

    # sanity: every referenced disorder exists (existing + newly added)
    data.setdefault('disorders', {})
    for key, (name_en, name_hi, icd11, icd10, tier, desc) in NEW_DISORDERS.items():
        if key not in data['disorders']:
            data['disorders'][key] = {
                "name": en_hi(name_en, name_hi),
                "tier": tier,
                "dsm5": name_en,
                "icd11": icd11,
                "icd10": icd10,
                "mappingNote": en_hi(
                    "Personality-disorder screen flag only — requires confirmation with the full IPDE/PDQ-4+ interview before any diagnostic use.",
                    "केवल व्यक्तित्व स्क्रीन धनात्मक — रोग-निर्णय हेतु पूर्ण साक्षात्कार आवश्यक।"),
                "description": en_hi(desc, desc),
            }

    refs = set()
    for p in ipde['parts']:
        refs.update(p['disorders'])
    for s in pdq['scales']:
        refs.update(s['disorders'])
    for q in dom['questions']:
        refs.update(q.get('disorders', []))
    missing = sorted(r for r in refs if r not in data['disorders'])
    assert not missing, "missing disorder entries: %s" % missing

    data.setdefault('scales', {})
    data['scales']['ipde_screen'] = ipde
    data['scales']['pdq4_screen'] = pdq

    # replace-or-append the personality domain
    doms = data['domains']
    idx = next((i for i, d in enumerate(doms) if d['id'] == 'personality'), None)
    if idx is None:
        doms.append(dom)
    else:
        doms[idx] = dom

    data.setdefault('instruments', {})
    data['instruments']['IPDE'] = {
        "name": "International Personality Disorder Examination (IPDE) — ICD-10 module screening questionnaire",
        "description": en_hi(
            "Loranger's structured interview; the brief screening form covers the nine ICD-10 F60 personality categories (paranoid, schizoid, dissocial, impulsive, borderline, histrionic, anankastic, anxious, dependent) with keyed True/False items. Three or more keyed items fail the screen for that disorder (this app flags at one, per the authors' lower-standard option); the screen is never diagnostic.",
            "loranger_का_संरचित_साक्षात्कार;_संक्षिप्त_स्क्रीनिंग_पत्रक_ICD-10 की_nौं_F60 श्रेणियों_को_कुंजी-उत्तर T/F आइटम_से_कवर_करता_है। तीन_अथवा_अधिक_कुंजी_आइटम_उस_विकार_की_स्क्रीन_असफल_करते_हैं (यह_ऐप_लेखकों_के_निम्नतर_मानदंड_अनुसार_एक_पर_धनात्मक_करता_है);_स्क्रीन_कभी_रोग-निर्णायक_नहीं।"),
        "domain": "personality",
        "format": "clinician/self-administered keyed True-False screen",
        "optionalAssessment": True,
    }
    data['instruments']['PDQ-4+'] = {
        "name": "Personality Diagnostic Questionnaire-4+ (PDQ-4+)",
        "description": en_hi(
            "99-item True/False self-report screen for 12 DSM personality disorders, with two validity items (64, 76), Section B impulsivity (item 98) and conduct-disorder (item 99) checklists gating Borderline and Antisocial respectively, and a mandatory five-part clinical-significance follow-up (accuracy, duration, pervasiveness, impairment, distress). Not diagnostic.",
            "12 DSM व्यक्तित्व_विकार_हेतु 99-आइटम T/F स्व-वर्णित_स्क्रीन;_दो_वैधता_आइटम (64, 76),_खंड-B आवेगी_आइटम 98 एवं_आचरण-विकार_आइटम 99 क्रमशः सीमांत_एवं_विरोधी_समाजवादी_द्वार_रूप, तथा_पाँच-भाग_नैदानिक_महत्व_अनुवर्ती_अनिवार्य। रोग-निर्णायक_नहीं।"),
        "domain": "personality",
        "format": "self-report True/False questionnaire with thresholds",
        "optionalAssessment": True,
    }

    meta = data.setdefault('meta', {})
    meta['schemaVersion'] = '2.3.0'
    meta['updated'] = '2026-11-04'
    notes = meta.setdefault('instrumentNotes', []) if isinstance(meta.get('instrumentNotes', []), list) else []
    if isinstance(notes, list):
        for n in [
            "IPDE ICD-10 screening questionnaire implemented with keyed True/False items; app uses the single-item positive standard explicitly permitted by the instrument authors (printed standard: >=3 keyed items per disorder).",
            "PDQ-4+ implemented with validity items 64/76, Section B item 98 (>=2 impulsivity checks gates Borderline) and item 99 (>=3 conduct checks gates Antisocial), plus the mandatory clinical-significance A-E follow-up checklist.",
            "Personality instrument item text was transcribed from user-supplied scans; Hindi labels are machine-assisted aids flagged for clinician review. Verify licensing before redistribution."]:
            if n not in notes:
                notes.append(n)

    out = json.dumps(data, ensure_ascii=False, indent=2)
    if check:
        print("check OK:", len(ipde['parts']), "IPDE modules,",
              len(pdq['parts'][0]['questions']), "PDQ items,",
              len(pdq['scales']), "PDQ scales")
        return

    with open(DATA, 'w', encoding='utf-8') as f:
        f.write(out + "\n")
    print("wrote data.json schema", meta['schemaVersion'])
    print("IPDE modules:", len(ipde['parts']), "| IPDE items:",
          sum(len(p['questions']) for p in ipde['parts']))
    print("PDQ items:", len(pdq['parts'][0]['questions']),
          "| scales:", len(pdq['scales']),
          "| 98 options:", len(pdq['parts'][1]['questions']),
          "| 99 options:", len(pdq['parts'][2]['questions']),
          "| CS items:", len(pdq['parts'][3]['questions']))


if __name__ == '__main__':
    main(check='--check' in sys.argv)
