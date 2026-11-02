#!/usr/bin/env python3
"""Assemble /tmp/mini.json — MINI 7.0.2 (DSM-5) Modules A, B, C, bilingual EN/HI.

Module B is loaded verbatim from scripts/modB.json; Modules A and C are defined
here with the official screening logic:
  - Module A: screen-in (A1a/A2a) -> current followups (A1b/A2b) -> symptom
    gate -> timeframe-explored A3 symptoms -> A4 impairment -> diagnostic box
    (>=5 of A1-A3 Yes + A4 Yes + organic ruled out), A5 recurrence flag, A6a.
  - Module C: family-history vigilance probe, C1/C2 screen-ins (terminate if
    both No), C3a-g criteria (3+ w/ elation incl. C3f, 4+ w/ irritability),
    C4 duration buckets a/b/c, C5 hospitalization, C6 impairment, C7 change of
    function, Manic / Hypomanic / Hypomanic-Symptoms diagnostic boxes with the
    mutual-exclusion rules, C8a-c bipolar follow-ups.
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))

def q(qid, en, hi, **kw):
    d = {"id": qid, "text": {"en": en, "hi": hi}}
    d.update(kw)
    return d

YN_NO = {"en": "No", "hi": "नहीं"}
YN_YES = {"en": "Yes", "hi": "हाँ"}

modA = {
  "id": "A",
  "name": {"en": "Module A — Major Depressive Episode",
           "hi": "माड्यूल A — प्रमुख अवसादी एपिसोड"},
  "screen": {"intro": {"en": "Screen-in questions (ever in your life)",
                       "hi": "स्क्रीन-इन प्रश्न (जीवनभर में कभी)"},
             "questions": [
      q("A1a", "Were you ever depressed or down, or did you feel sad, empty or hopeless, most of the day, nearly every day, for two weeks?",
        "क्या आप कभी उदास या विषण्ण रहे, या दो सप्ताह तक दिन के अधिकतर समय, लगभग हर दिन, दुख, खालीपन या निराशा महसूस किए?"),
      q("A2a", "Were you ever much less interested in most things or much less able to enjoy the things you used to enjoy most of the time, for two weeks?",
        "क्या आप कभी दो सप्ताह तक अधिकतर चीज़ों में बहुत कम रुचि रखते थे, या जिन चीज़ों का पहले आनंद लेते थे उनसे बहुत कम आनंद ले पाते थे?")],
             "gateNote": {"en": "If A1a is No, A1b is coded No automatically. If A2a is No, A2b is coded No automatically.",
                          "hi": "यदि A1a 'नहीं' है, तो A1b स्वतः 'नहीं' माना जाएगा। यदि A2a 'नहीं' है, तो A2b स्वतः 'नहीं' माना जाएगा।"}},
  "followups": {"intro": {"en": "In the past two weeks...", "hi": "पिछले दो सप्ताह में..."},
                "visibleWhen": "A1a == 1 OR A2a == 1",
                "questions": [
      q("A1b", "For the past two weeks, were you depressed or down, or did you feel sad, empty or hopeless, most of the day, nearly every day?",
        "पिछले दो सप्ताह में, क्या आप उदास या विषण्ण रहे, या दिन के अधिकतर समय, लगभग हर दिन दुख, खालीपन या निराशा महसूस किए?"),
      q("A2b", "In the past two weeks, were you much less interested in most things or much less able to enjoy the things you used to enjoy, most of the time?",
        "पिछले दो सप्ताह में, क्या आप अधिकतर चीज़ों में बहुत कम रुचि रखते थे, या अधिकतर समय बहुत कम आनंद ले पाते थे?")]},
  "symptomGate": {"rule": "A1b OR A2b must be Yes to explore symptoms",
                  "note": {"en": "If either current question is Yes, both the current (past 2 weeks) and the most symptomatic past episode are explored; otherwise only the most symptomatic past episode.",
                           "hi": "यदि कोई भी वर्तमान प्रश्न 'हाँ' है, तो वर्तमान (पिछले 2 सप्ताह) और सबसे लक्षण-प्रधान अतीत दोनों की जाँच होती है; अन्यथा केवल सबसे लक्षण-प्रधान अतीत की।"}},
  "timeframes": [{"id": "current", "label": {"en": "Past 2 Weeks", "hi": "पिछले 2 सप्ताह"}},
                 {"id": "past", "label": {"en": "Past Episode", "hi": "अतीत का एपिसोड"}}],
  "symptomsIntro": {"en": "Over that two-week period, when you felt depressed or uninterested:",
                    "hi": "उस दो-सप्ताह की अवधि में, जब आप उदास या बेरुचि महसूस करते थे:"},
  "symptoms": [
      q("A3a", "Was your appetite decreased or increased nearly every day? Did your weight decrease or increase without trying intentionally (i.e., by ±5% of body weight, or ±8 lb / ±3.5 kg for a 160 lb / 70 kg person, in a month)?",
        "क्या आपकी भूख लगभग हर दिन कम या अधिक हो गई? क्या बिना जानबूझकर वज़न कम या अधिक हुआ (माह में शरीर भार का ±5%, या 70 किग्रा व्यक्ति में ±3.5 किग्रा)?"),
      q("A3b", "Did you have trouble sleeping nearly every night (difficulty falling asleep, waking up in the middle of the night, early morning wakening or sleeping excessively)?",
        "क्या लगभग हर रात सोने में कठिनाई हुई (सोने में कठिनाई, बीच में उठना, सुबह जल्द उठना या अधिक सोना)?"),
      q("A3c", "Did you talk or move more slowly than normal or were you fidgety, restless or having trouble sitting still almost every day? Did anyone notice this?",
        "क्या आप सामान्य से धीमे बोले या चले, या लगभग हर दिन बेचैन, अस्थिर या स्थिर बैठने में कठिनाई थी? क्या किसी ने यह देखा?"),
      q("A3d", "Did you feel tired or without energy almost every day?",
        "क्या आपको लगभग हर दिन थकान या ऊर्जा की कमी महसूस हुई?"),
      q("A3e", "Did you feel worthless or guilty almost every day?",
        "क्या आप लगभग हर दिन बेकार या अपराधी महसूस किए?",
        delusionProbe={"en": "Look for delusions of failure, inadequacy, ruin or guilt, or of needing punishment, or delusions of disease or death or nihilistic/somatic delusions.",
                       "hi": "असफलता, अक्षमता, बर्बादी या अपराध के भ्रम, दंड पाने की आवश्यकता, या रोग/मृत्यु के भ्रम या शून्यतावादी/कायिक भ्रम पर ध्यान दें।"}),
      q("A3f", "Did you have difficulty concentrating, thinking or making decisions almost every day?",
        "क्या लगभग हर दिन ध्यान केंद्रित करने, सोचने या निर्णय लेने में कठिनाई हुई?"),
      q("A3g", "Did you repeatedly think about death (fear of dying does not count here), or have any thoughts of killing yourself, or any intent or plan to kill yourself? Did you attempt suicide?",
        "क्या आप बार-बार मृत्यु के बारे में सोचे (मरने का डर यहाँ नहीं गिना जाएगा), या आत्महत्या के विचार, इरादे या योजना आए? क्या आपने आत्महत्या का प्रयास किया?",
        safety=True)],
  "impairment": {"id": "A4", "perTimeframe": True,
                 "text": {"en": "Did these symptoms cause significant distress or problems at home, at work, at school, socially, in your relationships, or in some other important way, and are they a change from your previous functioning?",
                          "hi": "क्या इन लक्षणों से घर, कार्य, विद्यालय, सामाजिक, संबंधों या अन्य महत्वपूर्ण क्षेत्र में महत्वपूर्ण परेशानी हुई, और क्या यह पूर्व कार्यशैली से परिवर्तन है?"}},
  "recurrence": {"id": "A5",
                 "text": {"en": "In between 2 episodes of depression, did you ever have an interval of at least 2 months, without any significant depression or any significant loss of interest?",
                          "hi": "दो अवसादी एपिसोड के बीच, क्या आपको कम से कम 2 माह का अंतराल कभी मिला जब कोई महत्वपूर्ण अवसाद या रुचि की हानि नहीं थी?"},
                 "options": [{"v": "na", "label": {"en": "N/A", "hi": "लागू नहीं"}},
                             {"v": "no", "label": YN_NO},
                             {"v": "yes", "label": YN_YES}]},
  "episodeCount": {"id": "A6a", "numeric": True, "max": 99,
                   "text": {"en": "How many episodes of depression did you have in your lifetime? (Between each episode there must be at least 2 months without any significant depression.)",
                            "hi": "Jeevanbhar mein aapko kitne avasadi episode hue? (Pratyek episode ke beech kam se kam 2 mah bina mahatvapurn avasad ke hone chahiye.)"},
  "diagnosticBox": {"id": "A_diag",
                    "label": {"en": "Major Depressive Episode", "hi": "प्रमुख अवसादी एपिसोड"},
                    "rule": "(>=5 of A1-A3 coded Yes within a timeframe) AND A4 Yes for that timeframe AND organic cause ruled out (O2 summary). A5 Yes => RECURRENT.",
                    "flags": ["CURRENT", "PAST", "RECURRENT"],
                    "disordersOnPositive": ["depression_mdd"]}
}

modC = {
  "id": "C",
  "name": {"en": "Module C — Manic and Hypomanic Episodes",
           "hi": "माड्यूल C — मैैनिक और हाइपोमैैनिक एपिसोड"},
  "familyHistoryProbe": {"id": "C0", "nonScoring": True,
    "text": {"en": "Do you have any family history of manic-depressive illness or bipolar disorder, or any family member who had mood swings treated with a medication like lithium, sodium valproate (Depakote) or lamotrigine (Lamictal)? (Not a criterion; asked to increase vigilance.)",
             "hi": "क्या परिवार में मैैनिक-डिप्रेसिव बीमारी या बाइपोलर विकार का इतिहास है, या कोई सदस्य जिसके मूड स्विंग लिथियम, सोडियम वैप्रोएट या लैामोट्रिजिन से उपचारित हुए? (यह मानदंड नहीं; सतर्कता हेतु।)"}},
  "screen": {"intro": {"en": "Screen-in questions", "hi": "स्क्रीन-इन प्रश्न"},
             "clarification": {"en": "By 'up'/'high'/'hyper' I mean: elated mood; increased energy or activity; needing less sleep; rapid thoughts; full of ideas; increased productivity, motivation, creativity or impulsive behavior; phoning or working excessively or spending more money.",
                               "hi": "'अच्छा/हाई/हाइपर' का अर्थ: उन्मुक्त मूड; ऊर्जा/गतिविधि में वृद्धि; कम नींद; तेज़ विचार; विचारों से भरा; उत्पादकता/ेरक/सृजनशीलता/अववेगी व्यवहार में वृद्धि; अत्यधिक फ़ोन/कार्य/खर्च।"},
             "questions": [
      q("C1a", "Have you ever had a period of time when you were feeling 'up' or 'high' or 'hyper' and so active or full of energy or full of yourself that you got into trouble, or that other people thought you were not your usual self? (Do not consider times when you were intoxicated on drugs or alcohol.)",
        "क्या कभी कोई अवधि रही जब आप 'अच्छा', 'हाई' या 'हाइपर' महसूस कर रहे थे, इतने सक्रिय/ऊर्जावान कि मुसीबत हुई, या लोगों ने महसूस किया कि आप हमेशा जैसे नहीं हैं? (नशे की स्थितियाँ छोड़ें।)"),
      q("C1b", "Are you currently feeling 'up' or 'high' or 'hyper' or full of energy?",
        "क्या आप वर्तमान में 'अच्छा', 'हाई', 'हाइपर' या ऊर्जा से भरपूर महसूस कर रहे हैं?"),
      q("C2a", "Have you ever been persistently irritable, for several days, so that you had arguments or verbal or physical fights, or shouted at people outside your family? Have you or others noticed that you have been more irritable or overreacted, compared to other people, even in situations that you felt were justified?",
        "क्या कई दिनों तक लगातार चिड़चिड़े रहे, जिससे बहस/झगड़े हुए, या परिवार बाहर लोगों पर चिल्लाए? क्या आपको या दूसरों ने देखा कि आप दूसरों से अधिक चिड़चिड़े/अतिप्रतिक्रियाशील थे?"),
      q("C2b", "Are you currently feeling persistently irritable?",
        "क्या वर्तमान में लगातार चिड़चिड़े महसूस कर रहे हैं?")],
             "gateRule": "IF C1a AND C2a BOTH coded No -> MODULE C TERMINATES (all diagnostic boxes coded No).",
             "gateNote": {"en": "If both ever screen-ins are No, Module C terminates. Current positives (C1b/C2b) only affect which timeframe is explored.",
                          "hi": "यदि दोनों 'कभी' स्क्रीन-इन 'नहीं' हैं, तो माड्यूल C समाप्त। वर्तमान सकारात्मक (C1b/C2b) केवल समय-सीमा चयन प्रभावित करते हैं।"}},
  "exploreNote": {"en": "If C1b or C2b = Yes: explore the CURRENT episode first, then the most symptomatic PAST episode. Otherwise explore only the most symptomatic PAST episode.",
                  "hi": "यदि C1b या C2b = हाँ: पहले वर्तमान, फिर सबसे लक्षण-प्रधान अतीत की जाँच करें। अन्यथा केवल सबसे लक्षण-प्रधान अतीत की।"},
  "timeframes": [{"id": "current", "label": {"en": "Current Episode", "hi": "वर्तमान एपिसोड"}},
                 {"id": "past", "label": {"en": "Past Episode", "hi": "अतीत का एपिसोड"}}],
  "symptomsIntro": {"en": "During that period, when you felt high and full of energy or irritable, did you:",
                    "hi": "उस अवधि में, जब आप हाई, ऊर्जावान या चिड़चिड़े थे, क्या आप:"},
  "criteria": [
      q("C3a", "Feel that you could do things others couldn't do, or that you were an especially important person? (If yes, ask for examples; look for delusional ideas.)",
        "क्या लगा कि दूसरों वाले काम आप कर सकते हैं, या आप विशेष रूप से महत्वपूर्ण व्यक्ति हैं? (हाँ पर उदाहरण पूछें; भ्रामक विचार खोजें।)"),
      q("C3b", "Need less sleep (for example, feel rested after only a few hours sleep)?",
        "सामान्य से कम नींद चाहिए थी (जैसे कुछ घंटे सोने पर भी सुस्तापन)?"),
      q("C3c", "Talk too much without stopping, or felt a pressure to keep talking?",
        "बिना रुके अधिक बोलते थे, या बोलने का दबाव महसूस किया?"),
      q("C3d", "Notice your thoughts going very fast or running together or racing or moving very quickly from one subject to another?",
        "विचार बहुत तेज़, एक-दूसरे में मिलते, दौड़ते, या विषय से विषय को तेज़ी से बदलते दिखे?"),
      q("C3e", "Become easily distracted so that any little interruption could distract you?",
        "थोड़ी सी रुकावट से भी ध्यान भटक जाता था?"),
      q("C3f", "Have a significant increase in your activity or drive, at work, at school, socially or sexually, or did you become physically or mentally restless? This increase in activity may be with or without a purpose.",
        "कार्य, विद्यालय, सामाजिक या यौन गतिविधि में महत्वपूर्ण वृद्धि, या शारीरिक/मानसिक बेचैनी? यह वृद्धि उद्देश्य के साथ या बिना हो सकती है।"),
      q("C3g", "Want so much to engage in pleasurable activities that you ignored the risks or consequences (for example, spending sprees, reckless driving, or sexual indiscretions)?",
        "सुखद कार्यों में इतना संलग्न होना चाहा कि जोखिम/परिणाम नज़रअंदाज़ हुए (अत्यधिक खर्च, लापरवाह ड्राइविंग, यौन अनुचित व्यवहार)?")],
  "summaryRule": {"en": "Elation/expansiveness requires 3+ of C3 (including C3f); irritable mood alone requires 4+ of C3 (including C3f). Symptoms must occur during the same time period.",
                            "hi": "Jeevanbhar mein aapko kitne avasadi episode hue? (Pratyek episode ke beech kam se kam 2 mah bina mahatvapurn avasad ke hone chahiye.)"},
  "duration": {"id": "C4", "perTimeframe": True,
               "text": {"en": "What is the longest time these symptoms lasted (most of the day, nearly every day)? Assess from the very start to the very end of symptoms, not just the peak.",
                        "hi": "ये लक्षण अधिकतम कितने समय तक रहे (दिन के अधिकतर समय, लगभग हर दिन)? शुरुआत से अंत तक मापें, केवल चरम नहीं।"},
               "options": [{"v": "a", "label": {"en": "3 consecutive days or less", "hi": "3 लगातार दिन या कम"}},
                           {"v": "b", "label": {"en": "4, 5 or 6 consecutive days", "hi": "4, 5 या 6 लगातार दिन"}},
                           {"v": "c", "label": {"en": "7 consecutive days or more", "hi": "7 लगातार दिन या अधिक"}}]},
  "hospitalized": {"id": "C5", "perTimeframe": True,
                   "text": {"en": "Were you hospitalized for these problems? (If Yes, code MANIC EPISODE Yes for that timeframe and go to C7.)",
                            "hi": "क्या इन्हीं समस्याओं हेतु अस्पताल में भर्ती होना पड़ा? (हाँ पर उस समय-सीमा हेतु मैैनिक एपिसोड 'हाँ' कोड करें और C7 पर जाएँ।)"}},
  "impairment": {"id": "C6", "perTimeframe": True,
                 "text": {"en": "Did these symptoms cause significant problems at home, at work, socially, in your relationships, at school or in some other important way?",
                          "hi": "क्या इन लक्षणों से घर, कार्य, सामाजिक, संबंधों, विद्यालय या अन्य महत्वपूर्ण क्षेत्र में महत्वपूर्ण समस्याएं हुईं?"}},
  "changeOfFunction": {"id": "C7", "perTimeframe": True,
                 "text": {"en": "Were these symptoms associated with a clear change in the way that you previously functioned and that was different from the way that you usually are?",
                          "hi": "क्या इन लक्षणों से पूर्व कार्यशैली में स्पष्ट परिवर्तन हुआ जो आपकी सामान्य प्रकृति से भिन्न था?"}},
  "psychoticFeaturesRef": {"en": "Any psychotic features in Module K (K1-K8) also satisfy the Manic Episode alternatives.",
                           "hi": "माड्यूल K (K1-K8) के किसी भ्रामक लक्षण भी मैैनिक एपिसोड के विकल्प पूर्ण करते हैं।"},
  "diagnosticBoxes": [
    {"id": "C_diag_manic", "label": {"en": "Manic Episode", "hi": "मैैनिक एपिसोड"},
     "rule": "C3 SUMMARY AND C7 AND (C4c OR C5 OR C6 OR any psychotic feature K1-K8) coded Yes; AND organic cause ruled out (O2 summary). Specify CURRENT and/or PAST.",
     "flags": ["CURRENT", "PAST"], "disordersOnPositive": ["bipolar_depressive"]},
    {"id": "C_diag_hypomanic", "label": {"en": "Hypomanic Episode", "hi": "हाइपोमैैनिक एपिसोड"},
     "rule": "C3 SUMMARY Yes AND C5 No AND C6 No AND C7 Yes AND (C4b OR C4c) Yes; AND organic cause ruled out; AND all psychotic features K1-K8 No. If CURRENT Manic Yes -> CURRENT Hypomanic No; if PAST Manic Yes -> PAST Hypomanic Not Explored.",
     "flags": ["CURRENT", "PAST", "NOT EXPLORED"], "disordersOnPositive": ["bipolar_depressive"]},
    {"id": "C_diag_hypomanic_symptoms", "label": {"en": "Hypomanic Symptoms", "hi": "हाइपोमैैनिक लक्षण"},
     "rule": "C3 SUMMARY Yes AND C4a Yes AND C5 No. If current Manic/Hypomanic Yes -> current Hypomanic Symptoms No; if past Manic/Hypomanic Yes -> past Not Explored.",
     "flags": ["CURRENT", "PAST", "NOT EXPLORED"]}],
  "bipolarFollowUps": [
    {"id": "C8a", "visibleWhen": "MANIC EPISODE positive (current or past)",
     "text": {"en": "Did you have 2 or more of these (manic) episodes lasting 7 days or more (C4c) in your lifetime (including the current episode if present)?",
              "hi": "क्या जीवनभर में ऐसे 2+ मैैनिक एपिसोड हुए जो 7+ दिन रहे (C4c) (वर्तमान सहित)?"}},
    {"id": "C8b", "visibleWhen": "MANIC or HYPOMANIC EPISODE positive (current or past)",
     "text": {"en": "Did you have 2 or more of these (hypomanic) episodes lasting 4 days or more (C4b) in your lifetime (including the current episode)?",
              "hi": "क्या जीवनभर में ऐसे 2+ हाइपोमैैनिक एपिसोड हुए जो 4+ दिन रहे (C4b) (वर्तमान सहित)?"}},
    {"id": "C8c", "visibleWhen": "past HYPOMANIC SYMPTOMS positive",
     "text": {"en": "Did you have these hypomanic symptoms lasting only 1 to 3 days (C4a) 2 or more times in your lifetime (including the current episode if present)?",
              "hi": "क्या ये हाइपोमैैनिक लक्षण केवल 1–3 दिन (C4a) रहकर जीवनभर में 2+ बार हुए (वर्तमान सहित)?"}}]
}

with open(os.path.join(HERE, "modB.json"), encoding="utf-8") as f:
    modB = json.load(f)

mini = {
  "id": "mini",
  "name": {"en": "Mini International Neuropsychiatric Interview (MINI), English Version 7.0.2, for DSM-5",
           "hi": "मिनी इंटरनैशनल न्यूरोसाइकिएट्रिक इंटरव्यू (MINI), अंग्रेज़ी संस्करण 7.0.2, DSM-5 हेतु"},
  "type": "mini_branching",
  "source": {"framework": "DSM-5", "version": "7.0.2", "date": "August 8, 2016",
             "modulesImplemented": ["A - Major Depressive Episode", "B - Suicidality", "C - Manic and Hypomanic Episodes"],
             "note": {"en": "Structured interview modules adapted from the MINI 7.0.2 user-scripted version. This web implementation captures the screening logic only; it is not a substitute for trained interviewer administration. The organic-cause exclusion (Module O) is approximated by the prior-diagnoses and medications context fields.",
                      "hi": "MINI 7.0.2 के उपयोगकर्ता-स्क्रिप्टेड संस्करण से अनुकूलित संरचित साक्षात्कार माड्यूल। यह वेब कार्यान्वयन केवल स्क्रीनिंग तर्क ग्रहण करता है; प्रशिक्षित इंटरव्यूटर के प्रशासन का विकल्प नहीं है। जैविक-कारण बहिर्ागमन (माड्यूल O) को पूर्व-निदान एवं दवा संदर्भ फ़ील्ड द्वारा अनुमानित किया गया है।"}},
  "responseScale": [{"v": 0, "label": YN_NO}, {"v": 1, "label": YN_YES}],
  "directions": {"en": "These questions follow the MINI 7.0.2 branching logic (Module A: Major Depressive Episode; Module B: Suicidality; Module C: Manic and Hypomanic Episodes). Answer honestly; sections that do not apply are skipped automatically.",
                 "hi": "ये प्रश्न MINI 7.0.2 की शाखा-विभाजन पद्धति का पालन करते हैं (माड्यूल A: प्रमुख अवसादी एपिसोड; B: आत्मघातिता; C: मैैनिक एवं हाइपोमैैनिक एपिसोड)। ईमानदारी से उत्तर दें; लागू न होने वाले भाग स्वतः छोड़े जाएँगे।"},
  "modules": [modA, modB, modC]
}

out = "/tmp/mini.json"
with open(out, "w", encoding="utf-8") as f:
    json.dump(mini, f, ensure_ascii=False, indent=2)
json.load(open(out))
print("WROTE", out, "| modules:", [m["id"] for m in mini["modules"]], "| JSON VALID")
