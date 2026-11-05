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
