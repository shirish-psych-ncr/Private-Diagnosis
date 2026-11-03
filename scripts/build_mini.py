#!/usr/bin/env python3
"""Assemble /tmp/mini.json — MINI 7.0.2 (DSM-5) Modules A-P, bilingual EN/HI.

Module B is loaded verbatim from scripts/modB.json; the other modules are
defined here with the official screening logic:
  - Module A: screen-in (A1a/A2a) -> current followups (A1b/A2b) -> symptom
    gate -> timeframe-explored A3 symptoms -> A4 impairment -> diagnostic box
    (>=5 of A1-A3 Yes + A4 Yes + organic ruled out), A5 recurrence flag, A6a.
  - Module C: family-history vigilance probe, C1/C2 screen-ins (terminate if
    both No), C3a-g criteria (3+ w/ elation incl. C3f, 4+ w/ irritability),
    C4 duration buckets a/b/c, C5 hospitalization, C6 impairment, C7 change of
    function, Manic / Hypomanic / Hypomanic-Symptoms diagnostic boxes with the
    mutual-exclusion rules, C8a-c bipolar follow-ups.
  - Module D: panic attacks screen-in (D1a/D1b/D2), D3 anticipatory anxiety,
    D4a-m 13 somatic/cognitive symptoms (4+ gate), D5 lifetime box, D6 current
    follow-up.
  - Module E: agoraphobia situation list (2+ gate), E2-E6 fear/avoidance/
    persistence/impairment chain -> Current Agoraphobia box.
  - Module F: social anxiety screen-in F1 (past month), F2-F6 chain ->
    Current Social Anxiety box with performance-restricted specifier.
  - Module G: obsessions (G1a/G1b/G2) and compulsions (G3a/G3b) -> OR-gate,
    G4 impact -> Current OCD box with insight specifiers + tic-related.
  - Module H: trauma exposure H1, re-experiencing H2, past-month avoidance
    H3 (1+), negative cognitions/mood H4 (2+), arousal H5 (2+), H6 onset &
    duration, H7 impact -> Current PTSD box with depersonalization/
    derealization/delayed-expression specifiers.
  - Module I: alcohol screen-in I1, criteria I2a-k (k1 withdrawal checklist
    2+/8, k2 relief drinking, k summary counts as one criterion), 2+ gate ->
    Alcohol Use Disorder box with severity/remission specifiers.
  - Module J: drug-class list J1a, criteria J2a-k mirroring Module I with
    class-specific withdrawal checklists (sedatives 2+, opiates 3+,
    stimulants 2+, cannabis 3+), 2+ gate -> Substance Use Disorder box with
    specifiers.
  - Module K: psychotic screen K1-K7a/b (persecutory, mind reading, thought
    insertion/possession, delusions of reference, other odd beliefs, auditory
    and visual hallucinations) plus clinician-judged K8-K10 (disorganized
    speech, disorganized/catatonic behavior, negative symptoms) -> Mood
    Disorder With Psychotic Features lifetime (K11a + K11b) and current (K12)
    boxes with the mood-vs-psychotic duration rules, then Psychotic Disorder
    current (K13) and lifetime (K14) boxes requiring 1+ "b" (or "a") symptom
    of K1-K8, 2+ of K1-K10, two symptoms in the same 1-month period, and
    organic cause ruled out (O2 summary).
  - Module L: anorexia nervosa — height/weight entry with BMI-17 threshold
    table, L2 restriction, L3 fear of gaining weight, L4 body-image items
    (1+ gate -> L5), diagnostic box.
  - Module M: bulimia nervosa — binge screen M1/M2 (gate), weekly frequency
    M3, compensatory behaviours M4 (+M4a flag), self-evaluation M5, episode/
    day counts M6, anorexia-criteria check M7, M8 gate -> Bulimia Nervosa
    Current box; downstream Anorexia Binge-Eating/Purging and Restricting
    Type boxes (shared eating-disorder severity specifiers).
  - Module MB: binge eating disorder — exclusion of anorexia/bulimia (MB1/
    MB2), M2/M3/M4 linkage gates, MB6a-e binging behaviours (3+ gate), MB7
    distress, MB8 binge counts -> Binge-Eating Disorder Current box with
    severity specifiers.
  - Module N: GAD — excessive worry N1a most days N1b, not-better-explained
    gate, uncontrollable worry N2, six associated symptoms N3a-f (3+ gate),
    N4 impact + organic rule-out -> Current GAD box.
  - Module O: rule out medical/organic/drug causes — O1a substances, O1b
    medical illness, O2 clinician judgment, O2 SUMMARY (inverse of O2;
    feeds every organic-exclusion gate above).
  - Module P: antisocial personality disorder — conduct-disorder items P1a-f
    before age 15 (2+ gate), adult criteria P2a-g (3+ gate; politically or
    religiously motivated behaviours excluded) -> ASPD Lifetime box.
  - Mood Disorders Diagnostic Algorithm (after Module P): derived boxes for
    Major Depressive Disorder, Bipolar I, Bipolar II and Other Specified
    Bipolar and Related Disorder from Modules A/C/K plus the O2 summary,
    with psychotic-feature, mixed-features, anxious-distress, severity and
    most-recent-episode specifiers.
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
                            "hi": "जीवनभर में आपको कितने अवसादी एपिसोड हुए? (प्रत्येक एपिसोड के बीच कम से कम 2 माह बिना महत्वपूर्ण अवसाद के होने चाहिए।)"}},
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
                            "hi": "उत्फुल्लता/विस्तारवादिता हेतु C3 (C3f सहित) के 3+ लक्षण आवश्यक; केवल चिड़चिड़े मूड हेतु 4+ लक्षण आवश्यक। सभी लक्षण एक ही समय-अवधि में घटित होने चाहिए।"},
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

modD = {
  "id": "D",
  "name": {"en": "Module D — Panic Disorder",
           "hi": "माड्यूल D — पैैनिक विकार"},
  "screen": {"intro": {"en": "Screen-in questions", "hi": "स्क्रीन-इन प्रश्न"},
             "questions": [
      q("D1a", "Have you, on more than one occasion, had spells or attacks when you suddenly felt anxious, very frightened, uncomfortable or uneasy, even in situations where most people would not feel that way?",
        "क्या एक से अधिक बार आपको ऐसे दौरे/आक्रमण आए जब आप अचानक बेचैन, बहुत भयभीत, असहज या व्याकुल महसूस करने लगे — ऐसी भी स्थितियों में जहाँ अधिकांश लोग ऐसा नहीं महसूस करते?"),
      q("D1b", "Did the spells surge to a peak within 10 minutes of starting?",
        "क्या ये दौरे शुरुआत के 10 मिनट के भीतर अपने चरम पर पहुँचे?"),
      q("D2", "At any time in the past, did any of those spells or attacks come on unexpectedly or occur in an unpredictable or unprovoked manner?",
        "क्या अतीत में कभी इनमें से कोई दौरा अप्रत्याशित रूप से या अनिश्चित/बे-कारण ढंग से आया?")],
             "gateRule": "IF ANY OF D1a/D1b/D2 coded No -> GO TO DIAGNOSTIC BOX, CIRCLE NO AND MOVE TO THE NEXT MODULE.",
             "gateNote": {"en": "All three screen-ins must be Yes to continue; otherwise Panic Disorder is coded No.",
                          "hi": "जारी रखने हेतु तीनों स्क्रीन-इन 'हाँ' होने चाहिए; अन्यथा पैैनिक विकार 'नहीं' कोड होता है।"}},
  "d3": q("D3", "Have you ever had one such attack followed by a month or more of persistent concern about having another attack, or worries about the consequences of the attack — or did you make any significant change in your behavior because of the attacks (e.g., avoiding unfamiliar situations, or avoiding leaving your house or shopping alone, or doing things to avoid having a panic attack or visiting your doctor or the emergency room more frequently)?",
          "क्या किसी ऐसे दौरे के बाद एक माह या अधिक तक दूसरे दौरे की लगातार चिंता रही, या परिणामों की फ़िक्र हुई — या दौरे के कारण व्यवहार में महत्वपूर्ण परिवर्तन किया (जैसे अपरिचित स्थितियाँ/अकेला घर से निकलना/अकेला खरीदारी करना टालना, या दौरा टालने के उपाय, या बार-बार डॉक्टर/इमरजेंसी रूम जाना)?"),
  "symptomsIntro": {"en": "During the worst attack that you can remember:",
                    "hi": "जिस सबसे बुरे दौरे को आप याद कर सकते हैं, उस दौरान:"},
  "symptoms": [
      q("D4a", "Did you have skipping, racing or pounding of your heart?", "क्या दिल ज़ोर से/तेज़/दौड़ता हुआ धड़का?"),
      q("D4b", "Did you have sweating or clammy hands?", "क्या पसीना आया या हाथ ठंडे/नम हो गए?"),
      q("D4c", "Were you trembling or shaking?", "क्या कांपना या कंपन हुआ?"),
      q("D4d", "Did you have shortness of breath or difficulty breathing or a smothering sensation?", "क्या सांस लेने में कठिनाई या घुटन जैसा अनुभव हुआ?"),
      q("D4e", "Did you have a choking sensation or a lump in your throat?", "क्या गला घुटने जैसा या गले में गोलठनुमा अहसास हुआ?"),
      q("D4f", "Did you have chest pain, pressure or discomfort?", "क्या छाती में दर्द, दबाव या बेचैनी हुई?"),
      q("D4g", "Did you have nausea, stomach problems or sudden diarrhea?", "क्या जी मिचलाना, पेट की तकलीफ़ या अचानक दस्त हुआ?"),
      q("D4h", "Did you feel dizzy, unsteady, lightheaded or feel faint?", "क्या चक्कर, लखलखाहट, हल्कापन या बेहोशी जैसा लगा?"),
      q("D4i", "Did you have hot flushes or chills?", "क्या गर्मी की लहरें या ठंड लगना (chills) जैसा हुआ?"),
      q("D4j", "Did you have tingling or numbness in parts of your body?", "क्या शरीर के कुछ हिस्सों में झनझनाहट या सुन्नपन हुआ?"),
      q("D4k", "Did things around you feel strange, unreal, detached or unfamiliar, or did you feel outside of or detached from part or all of your body?",
        "क्या आसपास की चीज़ें अजीब/अवास्तविक/विपृक्त/अपरिचित लगीं, या शरीर के किसी भाग/समूचे शरीर से बाहर/टूटे हुए जैसा लगा?"),
      q("D4l", "Did you fear that you were losing control or going crazy?", "क्या यह डर लगा कि आप नियंत्रण खो रहे हैं या पागल हो रहे हैं?"),
      q("D4m", "Did you fear that you were dying?", "क्या यह डर लगा कि आप मर रहे हैं?")],
  "d5Gate": {"rule": "IF D3 Yes AND >=4 of D4 answers Yes -> D5 YES (Lifetime Panic Disorder). Otherwise D5 NO.",
             "text": {"en": "Are both D3, and 4 or more D4 answers, coded Yes?",
                      "hi": "क्या D3 और D4 के 4 या अधिक उत्तर, दोनों 'हाँ' कोडित हैं?"}},
  "diagnosticBoxes": [
    {"id": "D_diag_lifetime", "label": {"en": "Panic Disorder — Lifetime", "hi": "पैैनिक विकार — जीवनभर"},
     "rule": "D5 Yes AND organic cause ruled out (O2 summary).",
     "flags": ["LIFETIME"], "disordersOnPositive": ["panic_disorder"]}],
  "d6": {"id": "D6", "visibleWhen": "D5 == 1",
         "text": {"en": "In the past month did you have persistent concern about having another attack, or worry about the consequences of the attacks, or did you change your behavior in any way because of the attacks?",
                  "hi": "पिछले माह में क्या दूसरे दौरे की लगातार चिंता थी, या परिणामों की फ़िक्र रही, या दौरे के कारण किसी तरह व्यवहार बदला?"}},
  "currentBox": {"id": "D_diag_current", "label": {"en": "Panic Disorder — Current", "hi": "पैैनिक विकार — वर्तमान"},
     "rule": "(D5 OR D6) Yes AND organic cause ruled out (O2 summary). Specify CURRENT and/or LIFETIME.",
     "flags": ["CURRENT", "LIFETIME"], "disordersOnPositive": ["panic_disorder"]}
}

modE = {
  "id": "E",
  "name": {"en": "Module E — Agoraphobia",
           "hi": "माड्यूल E — एगोराफोबिया (खुले स्थान का भय)"},
  "situationsIntro": {"en": "Do you feel anxious or uneasy in places or situations where help might not be available or escape might be difficult if you had a panic attack or panic-like or embarrassing symptoms, like:",
                      "hi": "क्या ऐसी जगहों/स्थितियों में आप बेचैन या असहज महसूस करते हैं जहाँ मदद उपलब्ध न हो सके या भागना कठिन हो यदि पैैनिक/पैैनिक-जैसे या शर्मनाक लक्षण आ जाएँ, जैसे:"},
  "situations": [
      {"id": "E1a", "label": {"en": "Being in a crowd, or standing in a line (queue)", "hi": "भीड़ में होना या क़तार में खड़ा होना"}},
      {"id": "E1b", "label": {"en": "Being in an open space or when crossing a bridge", "hi": "खुले स्थान में होना या पुल पार करना"}},
      {"id": "E1c", "label": {"en": "Being in an enclosed space", "hi": "बंद स्थान में होना"}},
      {"id": "E1d", "label": {"en": "When you are alone away from home, or alone at home", "hi": "घर से बाहर अकेले होना, या घर पर अकेले होना"}},
      {"id": "E1e", "label": {"en": "Traveling in a bus, train or car or using public transportation", "hi": "बस, ट्रेन या कार से यात्रा करना या सार्वजनिक परिवहन उपयोग करना"}}],
  "situationGate": {"rule": "IF <2 of the E1 situations coded Yes -> GO TO DIAGNOSTIC BOX, CIRCLE NO AND MOVE TO THE NEXT MODULE.",
                    "text": {"en": "Are 2 or more of the above situations in E1 coded Yes?",
                             "hi": "क्या E1 की उपरोक्त स्थितियों में से 2 या अधिक 'हाँ' कोडित हैं?"}},
  "questions": [
      q("E2", "Do these situations almost always bring on fear or anxiety?", "क्या ये स्थितियाँ लगभग सदा भय या चिंता उत्पन्न करती हैं?"),
      q("E3", "Do you fear these situations so much that you avoid them, or suffer through them, or need a companion to face them?",
        "क्या आप इतना डरते हैं कि इनसे बचते हैं, या झेलते हैं, या इनका सामना हेतु साथी चाहिए?"),
      q("E4", "Is this fear or anxiety excessive or out of proportion to the real danger in the situation?",
        "क्या यह भय/चिंता अत्यधिक है या स्थिति की वास्तविक ख़तरे से असंतुलित?"),
      q("E5", "Did this avoidance, fear or anxiety persist for at least 6 months?", "क्या यह परहेज़/भय/चिंता कम से कम 6 माह जारी रही?"),
      q("E6", "Did these symptoms cause significant distress or problems at home, at work, socially, at school or in some other important way?",
        "क्या इन लक्षणों से घर, कार्य, सामाजिक, विद्यालय या अन्य महत्वपूर्ण क्षेत्र में महत्वपूर्ण परेशानी/समस्या हुई?")],
  "terminateRules": {"en": "Each of E2-E6: if No, go to the diagnostic box, circle No and move to the next module.",
                     "hi": "E2-E6 में से प्रत्येक: यदि 'नहीं', तो नैदानिक बॉक्स पर जाएँ, 'नहीं' घेरें और अगले माड्यूल पर बढ़ें।"},
  "diagnosticBoxes": [
    {"id": "E_diag", "label": {"en": "Agoraphobia — Current", "hi": "एगोराफोबिया — वर्तमान"},
     "rule": ">=2 E1 situations AND E2 AND E3 AND E4 AND E5 AND E6 all Yes.",
     "flags": ["CURRENT"], "disordersOnPositive": ["agoraphobia"]}]
}

modF = {
  "id": "F",
  "name": {"en": "Module F — Social Anxiety Disorder (Social Phobia)",
           "hi": "माड्यूल F — सामाजिक आतंक विकार (सोशल फ़ोबिया)"},
  "screen": {"intro": {"en": "Screen-in question (past month)", "hi": "स्क्रीन-इन प्रश्न (पिछले माह)"},
             "examples": {"en": "Examples of such social situations typically include: initiating or maintaining a conversation, participating in small groups, dating, speaking to authority figures, attending parties, public speaking, eating in front of others, performing in front of others, urinating in a public washroom, etc.",
                          "hi": "ऐसी सामाजिक स्थितियों के उदाहरण: बातचीत शुरू/जारी रखना, छोटे समूहों में भाग लेना, डेटिंग, अधिकार-स्थान व्यक्तियों से बोलना, पार्टियों में जाना, सार्वजनिक भाषण, दूसरों के सामने खाना, मंच पर प्रदर्शन, सार्वजनिक शौचालय में पेशाब करना आदि।"},
             "questions": [
      q("F1", "In the past month, did you have persistent fear and significant anxiety at being watched, being the focus of attention, or of being humiliated or embarrassed or rejected? This includes things like speaking in public, eating in public or with others, writing while someone watches, performing in front of others or being in social situations.",
        "पिछले माह में क्या देखा जाने, ध्यान का केंद्र बनने, या अपमानित/शर्मिंदा/अस्वीकृत होने का लगातार भय और महत्वपूर्ण आतंक रहा? इसमें सार्वजनिक भाषण, सार्वजनिक रूप से/दूसरों संग खाना, किसी के देखते हुए लिखना, दूसरों के सामने प्रदर्शन या सामाजिक स्थितियाँ शामिल हैं।")],
             "gateRule": "IF F1 No -> GO TO THE DIAGNOSTIC BOX, CIRCLE NO AND MOVE TO THE NEXT MODULE.",
             "gateNote": {"en": "If F1 is No, Module F terminates (Social Anxiety Disorder coded No).",
                          "hi": "यदि F1 'नहीं' है, माड्यूल F समाप्त (सामाजिक आतंक विकार 'नहीं' कोड)।"}},
  "questions": [
      q("F2", "Do these social situations almost always bring on fear or anxiety?", "क्या ये सामाजिक स्थितियाँ लगभग सदा भय या आतंक उत्पन्न करती हैं?"),
      q("F3", "Do you fear these social situations so much that you avoid them, or suffer through them, or need a companion to face them?",
        "क्या आप इतना डरते हैं कि इन स्थितियों से बचते हैं, झेलते हैं, या सामना हेतु साथी चाहते हैं?"),
      q("F4", "Is this social fear or anxiety excessive or unreasonable in these social situations?", "क्या यह सामाजिक भय/आतंक अत्यधिक या अनुचित है?"),
      q("F5", "Did this social avoidance, fear or anxiety persist for at least 6 months?", "क्या यह सामाजिक परहेज़/भय/आतंक कम से कम 6 माह जारी रहा?"),
      q("F6", "Did these social fears cause significant distress or interfere with your ability to function at work, at school or socially or in your relationships or in some other important way?",
        "क्या इन सामाजिक भयों से महत्वपूर्ण कष्ट हुआ या कार्य/विद्यालय/सामाजिक/संबंध/अन्य महत्वपूर्ण क्षेत्रों में कार्यक्षमता बाधित हुई?")],
  "terminateRules": {"en": "Each of F2-F6: if No, go to the diagnostic box, circle No and move to the next module.",
                     "hi": "F2-F6 में से प्रत्येक: यदि 'नहीं', तो नैदानिक बॉक्स पर जाएँ, 'नहीं' घेरें और अगले माड्यूल पर बढ़ें।"},
  "clinicianNote": {"en": "Note to clinician: please specify if the subject's fears are restricted to speaking or performing in public.",
                    "hi": "चिकित्सक हेतु सूचना: यदि भय केवल सार्वजनिक बोलने/प्रदर्शन तक सीमित हो तो निर्दिष्ट करें।"},
  "diagnosticBoxes": [
    {"id": "F_diag", "label": {"en": "Social Anxiety Disorder (Social Phobia) — Current", "hi": "सामाजिक आतंक विकार — वर्तमान"},
     "rule": "F1-F6 all Yes AND organic cause ruled out (O2 summary). Specifier: RESTRICTED TO PERFORMANCE (social) only.",
     "flags": ["CURRENT", "RESTRICTED TO PERFORMANCE"], "disordersOnPositive": ["social_anxiety"]}]
}

modG = {
  "id": "G",
  "name": {"en": "Module G — Obsessive-Compulsive Disorder",
           "hi": "माड्यूल G — ऑब्सेसिव-कम्पल्सिव विकार"},
  "obsessionsIntro": {"en": "Obsessions", "hi": "ओब्सेशन (अवधारणाएँ)"},
  "obsessionQuestions": [
      q("G1a", "In the past month, have you been bothered by recurrent thoughts, impulses, or images that were unwanted, distasteful, inappropriate, intrusive, or distressing? (For example, the idea that you were dirty, contaminated or had germs, or fear of contaminating others, or fear of harming someone even though it disturbs or distresses you, or fear you would act on some impulse, or fear or superstitions that you would be responsible for things going wrong, or obsessions with sexual thoughts, images or impulses, or religious obsessions.)",
        "पिछले माह में क्या आप बार-बार आने वाले विचारों/आवेगों/छवियों से परेशान रहे जो अवांछित, अप्रिय, अनुचित, हस्तक्षेपी या पीड़ादायक थे? (जैसे गंदे/संक्रमित/कीटाणुमय होने का विचार, दूसरों को संक्रमित करने का डर, किसी को नुकसान पहुँचाने का डर — भले ही वह सताए —, किसी आवेग पर कार्य करने का भय, गलत होने का दोषी पाए जाने का डर/अंधविश्वास, यौन विचार/छवियों/आवेगों के ओब्सेशन, या धार्मिक ओब्सेशन।)"),
      q("G1b", "In the past month, did you try to suppress these thoughts, impulses, or images or to neutralize or to reduce them with some other thought or action? (Do not include simply excessive worries about real life problems. Do not include obsessions directly related to hoarding, hair pulling, skin picking, body dysmorphic disorder, eating disorders, sexual deviations, pathological gambling, or alcohol or drug abuse.)",
        "पिछले माह में क्या आप इन विचारों/आवेगों/छवियों को दबाने, निष्क्रिय करने या किसी अन्य विचार/कार्य से कम करने का प्रयास करते थे? (वास्तविक जीवन समस्याओं की अत्यधिक चिंता शामिल न करें; hoarding, बाल नोचना, त्वचा चुभोना, शैलिक-छवि विकार, आहार विकार, यौन विकृतियाँ, जुआ, शराब/नशा संबंधी ओब्सेशन शामिल न करें।)"),
      q("G2", "Did they keep coming back into your mind even when you tried to ignore or get rid of them?",
        "क्या उपेक्षा/छोड़ने के प्रयास के बाद भी वे बार-बार मन में लौटते थे?")],
  "compulsionsIntro": {"en": "Compulsions", "hi": "कम्पल्शन (विवशता-कृत्य)"},
  "compulsionQuestions": [
      q("G3a", "In the past month, did you feel driven to do something repeatedly in response to an obsession or in response to a rigid rule, like washing or cleaning excessively, counting or checking things over and over, or repeating or arranging things, or other superstitious rituals?",
        "पिछले माह में क्या किसी ओब्सेशन या कठोर नियम के उत्तर में बार-बार कुछ करने की वेग-प्रेरणा होती थी — जैसे अत्यधिक धुलाई/सफ़ाई, बार-बार गिनना/जाँचना, दोहराना/क्रमबद्ध करना, या अन्य अंधविश्वासी अनुष्ठान?"),
      q("G3b", "Are these rituals done to prevent or reduce anxiety or distress or to prevent something bad from happening and are they excessive or unreasonable?",
        "क्या ये अनुष्ठान आतंक/कष्ट रोकने-कम करने या बुरा होने से बचाने हेतु हैं और क्या ये अत्यधिक/अनुचित हैं?")],
  "skipNotes": {"en": "If G1a is No, skip to G3a. If G1b is No, skip to G3a.",
                "hi": "यदि G1a 'नहीं' तो G3a पर जाएँ। यदि G1b 'नहीं' तो G3a पर जाएँ।"},
  "gate": {"rule": "IF NOT ((G1a AND G1b AND G2) OR (G3a AND G3b)) -> GO TO THE DIAGNOSTIC BOX, CIRCLE NO AND MOVE TO THE NEXT MODULE.",
           "text": {"en": "Are (G1a AND G1b AND G2) OR (G3a AND G3b) coded Yes?",
                    "hi": "क्या (G1a तथा G1b तथा G2) या (G3a तथा G3b) 'हाँ' कोडित हैं?"}},
  "g4": q("G4", "In the past month, did these obsessive thoughts and/or compulsive behaviors cause significant distress, or interfere with your ability to function at home, at work, at school or socially or in your relationships or in some other important way, or did they take more than one hour a day?",
          "पिछले माह में क्या ये ओब्सेसिव विचार/कम्पल्सिव व्यवहार ने महत्वपूर्ण कष्ट दिया, या घर/कार्य/विद्यालय/सामाजिक/संबंध/अन्य महत्वपूर्ण क्षेत्रों में कार्यक्षमता बाधित की, या दिन में एक घंटे से अधिक समय लिया?"),
  "insightNote": {"en": "Check for any obsessive-compulsive symptoms starting within 3 weeks of an infection. Specify the level of insight and if the episode is tic-related.",
                  "hi": "किसी संक्रमण के 3 सप्ताह के भीतर शुरू हुए O-C लक्षणों की जाँच करें। अंतर्दृष्टि का स्तर और टिक-संबंधिता निर्दिष्ट करें।"},
  "diagnosticBoxes": [
    {"id": "G_diag", "label": {"en": "O.C.D. — Current", "hi": "O.C.D. — वर्तमान"},
     "rule": "((G1a AND G1b AND G2) OR (G3a AND G3b)) AND G4 Yes AND organic cause ruled out (O2 summary). Insight specifiers: GOOD OR FAIR / POOR / ABSENT / DELUSIONAL; TIC-RELATED.",
     "flags": ["CURRENT", "INSIGHT: GOOD OR FAIR", "INSIGHT: POOR", "INSIGHT: ABSENT", "INSIGHT: DELUSIONAL", "TIC-RELATED"],
     "disordersOnPositive": ["ocd"]}]
}

modH = {
  "id": "H",
  "name": {"en": "Module H — Posttraumatic Stress Disorder",
           "hi": "माड्यूल H — आघात-ोत्तर तनाव विकार (PTSD)"},
  "screen": {"intro": {"en": "Criterion A — trauma exposure", "hi": "मानदंड A — आघात-संपर्क"},
             "examples": {"en": "Examples of traumatic events include: serious accidents, sexual or physical assault, a terrorist attack, being held hostage, kidnapping, fire, discovering a body, war, or natural disaster, witnessing the violent or sudden death of someone close to you, or a life threatening illness.",
                          "hi": "आघातजनक घटनाओं के उदाहरण: गंभीर दुर्घटनाएँ, यौन/शारीरिक हमला, आतंकी हमला, बंधक बनना, अपहरण, आग, मृतदेह देखना, युद्ध, प्राकृतिक आपदा, निकट के किसी की हिंसक/अचानक मृत्यु का साक्षी होना, या जीवन-घातक बीमारी।"},
             "questions": [
      q("H1", "Have you ever experienced or witnessed or had to deal with an extremely traumatic event that included actual or threatened death or serious injury or sexual violence to you or someone else?",
        "क्या आपने कभी अत्यंत आघातजनक घटना का अनुभव/साक्ष्य/प्रबंध किया जिसमें आपके या किसी और की वास्तविक/उपद्रुत मृत्यु, गंभीर चोट या यौन हिंसा शामिल थी?")],
             "gateRule": "IF H1 No -> GO TO THE DIAGNOSTIC BOX, CIRCLE NO, AND MOVE TO THE NEXT MODULE.",
             "gateNote": {"en": "If H1 is No, Module H terminates (PTSD coded No).",
                          "hi": "यदि H1 'नहीं', माड्यूल H समाप्त (PTSD 'नहीं' कोड)।"}},
  "h2": q("H2", "Starting after the traumatic event, did you repeatedly re-experience the event in an unwanted mentally distressing way (such as in recurrent dreams related to the event, intense recollections or memories, or flashbacks or as if the event was recurring) or did you have intense physical or psychological reactions when you were reminded about the event or exposed to a similar event?",
          "आघात के बाद क्या आपने घटना को बार-बार अवांछित, मानसिक रूप से पीड़ादायक ढंग से पुनः-अनुभव किया (जैसे घटना-संबंधी बार-बार सपने, तीव्र स्मृतियाँ, फ्लैशबैक, या जैसे घटना दोहराई जा रही हो), या घटना की याद दिलाने पर/समान घटना में तीव्र शारीरिक/मानसिक प्रतिक्रियाएँ हुईं?"),
  "h3Intro": {"en": "In the past month (persistent avoidance):", "hi": "पिछले माह (लगातार परहेज़):"},
  "h3": [
      q("H3a", "Did you persistently try to avoid thinking about or remembering distressing details or feelings related to the event?",
        "क्या आप लगातार घटना से जुड़े कष्टदायी विवरण/भावनाओं के बारे में सोचने या याद करने से बचते रहे?"),
      q("H3b", "Did you persistently try to avoid people, conversations, places, situations, activities or things that bring back distressing recollections of the event?",
        "क्या आप लगातार उन लोगों/बातचीत/स्थानों/स्थितियों/गतिविधियों/वस्तुओं से बचते रहे जो घटना की कष्टदायी स्मृतियाँ लौटाएँ?")],
  "h3Gate": {"rule": "IF 0 of H3 answers Yes -> GO TO THE DIAGNOSTIC BOX, CIRCLE NO, AND MOVE TO THE NEXT MODULE.",
             "text": {"en": "Are 1 or more H3 answers coded Yes?", "hi": "क्या H3 के 1 या अधिक उत्तर 'हाँ' कोडित हैं?"}},
  "h4Intro": {"en": "In the past month (negative alterations in cognitions and mood):",
              "hi": "पिछले माह (संज्ञाना एवं मूड में नकारात्मक परिवर्तन):"},
  "h4": [
      q("H4a", "Did you have trouble recalling some important part of the trauma? (but not because of or related to head trauma, alcohol or drugs).",
        "क्या आघात के किसी महत्वपूर्ण भाग को याद करने में कठिनाई हुई? (शिर-आघात/शराब/नशे से संबंधित कारण नहीं)।"),
      q("H4b", "Were you constantly and unreasonably negative about yourself or others or the world?", "क्या आप सतत और अनुचित रूप से स्वयं/दूसरों/संसार के प्रति नकारात्मक रहे?"),
      q("H4c", "Did you constantly blame yourself or others in unreasonable ways for the trauma?", "क्या आप सतत अनुचित ढंग से आघात हेतु स्वयं/दूसरों को दोष देते रहे?"),
      q("H4d", "Were your feelings always negative (such as fear, horror, anger, guilt or shame)?", "क्या भावनाएँ सदैव नकारात्मक रहीं (भय, आतंक, क्रोध, अपराधबोध, शर्म)?"),
      q("H4e", "Have you become much less interested in participating in activities that were meaningful to you before?", "क्या पहले अर्थपूर्ण रही गतिविधियों में भाग लेने की रुचि बहुत कम हो गई?"),
      q("H4f", "Did you feel detached or estranged from others?", "क्या दूसरों से विपृक्त/परभासित महसूस किया?"),
      q("H4g", "Were you unable to experience any good feelings (such as happiness, satisfaction or loving feelings)?", "क्या कोई सकारात्मक भावनाएँ (सुख, संतोष, प्रेम) अनुभव करना संभव नहीं रहा?")],
  "h4Gate": {"rule": "IF <2 of H4 answers Yes -> GO TO THE DIAGNOSTIC BOX, CIRCLE NO, AND MOVE TO THE NEXT MODULE.",
             "text": {"en": "Are 2 or more H4 answers coded Yes?", "hi": "क्या H4 के 2 या अधिक उत्तर 'हाँ' कोडित हैं?"}},
  "h5Intro": {"en": "In the past month (marked alterations in arousal and reactivity):",
              "hi": "पिछले माह (उत्तेजना एवं अभिक्रिया में स्पष्ट परिवर्तन):"},
  "h5": [
      q("H5a", "Were you especially irritable or did you have outbursts of anger with little or no provocation?", "क्या आप विशेष चिड़चिड़े रहे या अल्प/अनुत्तेजक क्रोध-विस्फोट हुए?"),
      q("H5b", "Were you more reckless or more self-destructive?", "क्या आप अधिक लापरवाह या आत्मविनाशी हुए?"),
      q("H5c", "Were you more nervous or constantly on your guard?", "क्या अधिक घबराहट या सतत सतर्कता रही?"),
      q("H5d", "Were you more easily startled?", "क्या आप अधिक आसानी से चौंकते/हड़बड़ाते थे?"),
      q("H5e", "Did you have more difficulty concentrating?", "क्या ध्यान केंद्रित करने में अधिक कठिनाई हुई?"),
      q("H5f", "Did you have more difficulty sleeping?", "क्या नींद में अधिक कठिनाई हुई?")],
  "h5Gate": {"rule": "IF <2 of H5 answers Yes -> GO TO THE DIAGNOSTIC BOX, CIRCLE NO, AND MOVE TO THE NEXT MODULE.",
             "text": {"en": "Are 2 or more H5 answers coded Yes?", "hi": "क्या H5 के 2 या अधिक उत्तर 'हाँ' कोडित हैं?"}},
  "h6": q("H6", "Did all these problems start after the traumatic event and last for more than one month?",
          "क्या ये सभी समस्याएँ आघात-ोत्तर शुरू हुईं और एक माह से अधिक जारी रहीं?"),
  "h7": q("H7", "During the past month, did these problems cause significant distress, or interfere with your ability to function at home, at work, at school or socially or in your relationships or in some other important way?",
          "पिछले माह में क्या इन समस्याओं ने महत्वपूर्ण कष्ट दिया, या घर/कार्य/विद्यालय/सामाजिक/संबंध/अन्य महत्वपूर्ण क्षेत्रों में कार्यक्षमता बाधित की?"),
  "specifierNote": {"en": "Specify if the condition is associated with depersonalization, derealization or with delayed expression.",
                    "hi": "निर्दिष्ट करें: क्या यह विपृक्त-आत्मता (depersonalization), यथार्थ-विपृक्तता (derealization) या विलंबित-अभिव्यक्ति (delayed expression) से संबंधित है।"},
  "diagnosticBoxes": [
    {"id": "H_diag", "label": {"en": "Posttraumatic Stress Disorder — Current", "hi": "आघात-ोत्तर तनाव विकार — वर्तमान"},
     "rule": "H1 AND H2 AND H3-gate AND H4-gate AND H5-gate AND H6 AND H7 all Yes AND organic cause ruled out (O2 summary). Specifiers: WITH DEPERSONALIZATION / DEREALIZATION / DELAYED EXPRESSION.",
     "flags": ["CURRENT", "WITH DEPERSONALIZATION", "DEREALIZATION", "DELAYED EXPRESSION"],
     "disordersOnPositive": ["ptsd"]}]
}

# Shared I2/J2 criteria builder (alcohol vs substance wording)
def _use_criteria(prefix, what_en, what_hi):
    """Return the ten lettered criteria questions (a-j) shared by Modules I and J."""
    return [
      q(prefix + "a", "During the times when you used " + what_en + ", did you end up using more than you planned when you started?",
        "जब भी आप " + what_hi + " का सेवन करते, क्या शुरू में योजना से अधिक का सेवन हो जाता?"),
      q(prefix + "b", "Did you repeatedly want to reduce or control your use? Did you try to cut down or control your use, but failed? (If yes to either, code Yes.)",
        "क्या बार-बार कम करने/नियंत्रण की इच्छा हुई? क्या घटाने/नियंत्रण का प्रयास कर विफल रहे? (किसी भी पर 'हाँ' कोड करें।)"),
      q(prefix + "c", "On the days that you used " + what_en + ", did you spend substantial time obtaining it, using it, or recovering from its effects?",
        "जिन दिनों " + what_hi + " का सेवन किया, क्या पर्याप्त समय इसे प्राप्त करने/सेवन/प्रभाव से उबरने में लगा?"),
      q(prefix + "d", "Did you crave or have a strong desire or urge to use " + what_en + "?",
        "क्या " + what_hi + " के लिए लालसा/तीव्र इच्छा/वेग हुआ?"),
      q(prefix + "e", "Did you spend less time meeting your responsibilities at work, at school, or at home, because of your repeated use?",
        "क्या बार-बार सेवन के कारण कार्य/विद्यालय/घर की ज़िम्मेदारियों में कम समय देने लगे?"),
      q(prefix + "f", "If your use caused problems with your family or other people, did you still keep on using?",
        "यदि सेवन से परिवार/अन्य लोगों में समस्या हुई, तब भी सेवन जारी रखा?"),
      q(prefix + "g", "Did you use more than once in any situation where you or others were physically at risk, for example, driving a car, riding a motorbike, using machinery, boating, etc.?",
        "क्या एक से अधिक बार ऐसी स्थिति में सेवन किया जहाँ आप/दूसरे शारीरिक रूप से जोखिम में थे — जैसे कार/बाइक चलाना, मशीनरी, नाव आदि?"),
      q(prefix + "h", "Did you continue to use, even though it was clear that it had caused or worsened psychological or physical problems?",
        "क्या सेवन जारी रखा, यद्यपि स्पष्ट था कि इससे मानसिक/शारीरिक समस्याएँ उत्पन्न/बढ़ी हैं?"),
      q(prefix + "i", "Did you reduce or give up important work, social or recreational activities because of your use?",
        "क्या सेवन के कारण महत्वपूर्ण कार्य/सामाजिक/मनोरंजन गतिविधियाँ घटाईं/छोड़ीं?"),
      q(prefix + "j", "Did you need to use a lot more in order to get the same effect that you got when you first started using, or did you get much less effect with continued use of the same amount?",
        "क्या प्रारंभिक-समान असर हेतु बहुत अधिक सेवन आवश्यक हुआ, या समान मात्रा से असर बहुत कम होने लगा?")]

WITHDRAWAL_ALCOHOL = [
    {"v": "w1", "label": {"en": "Increased sweating or increased heart rate", "hi": "अधिक पसीना या बढ़ी हृदय-गति"}},
    {"v": "w2", "label": {"en": "Hand tremor or 'the shakes'", "hi": "हाथों का कंपन"}},
    {"v": "w3", "label": {"en": "Trouble sleeping", "hi": "नींद में कठिनाई"}},
    {"v": "w4", "label": {"en": "Nausea or vomiting", "hi": "जी मिचलाना/उल्टी"}},
    {"v": "w5", "label": {"en": "Hearing or seeing things other people could not see or hear, or having sensations in your skin for no apparent reason",
                          "hi": "दूसरों को न दिखने/सुनने वाली चीज़ें देखना/सुनना, या बिना कारण त्वचा में अनुभूति"}},
    {"v": "w6", "label": {"en": "Agitation", "hi": "अधि-चंचलता (एजिटेशन)"}},
    {"v": "w7", "label": {"en": "Anxiety", "hi": "आतंक/चिंता"}},
    {"v": "w8", "label": {"en": "Seizures", "hi": "आपात (मिर्गी-जैसे दौरे)"}}]

USE_DISORDER_SPECIFIERS = ["MILD", "MODERATE", "SEVERE", "IN EARLY REMISSION", "IN SUSTAINED REMISSION", "IN A CONTROLLED ENVIRONMENT"]

modI = {
  "id": "I",
  "name": {"en": "Module I — Alcohol Use Disorder",
           "hi": "माड्यूल I — मद्य-सेवन विकार"},
  "screen": {"intro": {"en": "Screen-in question (past 12 months)", "hi": "स्क्रीन-इन प्रश्न (पिछले 12 माह)"},
             "questions": [
      q("I1", "In the past 12 months, have you had 3 or more alcoholic drinks, within a 3-hour period, on 3 or more occasions?",
        "पिछले 12 माह में, क्या 3-घंटे की अवधि में 3 या अधिक पेय, 3 या अधिक अवसरों पर लिए?")],
             "gateRule": "IF I1 No -> GO TO DIAGNOSTIC BOX, CIRCLE NO AND MOVE TO THE NEXT MODULE.",
             "gateNote": {"en": "If I1 is No, Module I terminates (Alcohol Use Disorder coded No).",
                          "hi": "यदि I1 'नहीं', माड्यूल I समाप्त (मद्य-सेवन विकार 'नहीं' कोड)।"}},
  "criteriaIntro": {"en": "In the past 12 months:", "hi": "पिछले 12 माह में:"},
  "criteria": _use_criteria("I2", "alcohol", "शराब"),
  "k1": {"id": "I2k1",
         "text": {"en": "When you cut down on heavy or prolonged drinking did you have any of the following: (If yes to 2 or more of the 8, code k1 as Yes.)",
                  "hi": "अत्यधिक/दीर्घ सेवन घटाने पर निम्नलिखित में से कोई हुआ: (8 में से 2+ 'हाँ' हो तो k1 'हाँ' कोड करें।)"},
         "checklist": WITHDRAWAL_ALCOHOL, "minChecks": 2},
  "k2": q("I2k2", "Did you drink alcohol to reduce or avoid withdrawal symptoms or to avoid being hung-over?",
          "क्या विषमुक्ति-लक्षण घटाने/टालने या हैंगओवर बचने हेतु शराब पी?"),
  "kSummary": {"id": "I2k_summary",
               "rule": "IF YES TO I2k1 OR I2k2, CODE YES. (I2k1 and I2k2 together count as one among the I2 criteria.)",
               "text": {"en": "I2k SUMMARY: If yes to I2k1 or I2k2, code Yes.",
                        "hi": "I2k सारांश: यदि I2k1 या I2k2 'हाँ' तो 'हाँ' कोड।"}},
  "gate": {"rule": "IF <2 of I2a-I2k SUMMARY coded Yes -> Alcohol Use Disorder NO.",
           "text": {"en": "Are 2 or more I2 answers from I2a through I2k SUMMARY coded Yes? (I2k1 and I2k2 together count as one among these choices.)",
                    "hi": "क्या I2a से I2k सारांश तक के 2 या अधिक उत्तर 'हाँ' कोडित हैं? (I2k1 व I2k2 संयुक्त रूप से एक गिने जाते हैं।)"}},
  "specifierNote": {"en": "Specifiers: MILD = 2-3 of the I2 symptoms; MODERATE = 4-5; SEVERE = 6 or more. IN EARLY REMISSION = criteria not met for between 3 & 12 months; IN SUSTAINED REMISSION = criteria not met for 12 months or more (both with the exception of criterion d [craving]); IN A CONTROLLED ENVIRONMENT = where alcohol access is restricted.",
                    "hi": "विशेषण: मृदु = I2 के 2-3 लक्षण; मध्यम = 4-5; गंभीर = 6+। प्रारंभिक-मिटी = 3-12 माह मानदंड पूरे नहीं; दीर्घ-मिटी = 12+ माह मानदंड पूरे नहीं (दोनों में मानदंड d [लालसा] अपवाद); नियंत्रित-वातावरण = जहाँ शराब-प्राप्ति सीमित हो।"},
  "diagnosticBoxes": [
    {"id": "I_diag", "label": {"en": "Alcohol Use Disorder — Past 12 Months", "hi": "मद्य-सेवन विकार — पिछले 12 माह"},
     "rule": "I1 Yes AND >=2 of I2a-I2k SUMMARY Yes. Severity by symptom count (2-3 mild, 4-5 moderate, 6+ severe).",
     "flags": USE_DISORDER_SPECIFIERS, "disordersOnPositive": ["alcohol_use_disorder"]}]
}

J_DRUG_CLASSES = [
  {"label": {"en": "Stimulants: amphetamines, 'speed', crystal meth, 'crank', Dexedrine, Ritalin, diet pills",
             "hi": "उत्तेजक: एम्फ़ैटामाइन, स्पीड, क्रिस्टल मेथ, डेक्सेड्रीन, रिटालिन, डाइट पिल्स"}},
  {"label": {"en": "Cocaine: snorting, IV, freebase, crack, 'speedball'", "hi": "कोकीन: नाक से, IV, फ्रीबेस, क्रैक, स्पीडबॉल"}},
  {"label": {"en": "Opiates: heroin, morphine, Dilaudid, opium, Demerol, methadone, Darvon, codeine, Percodan, Vicodin, OxyContin",
             "hi": "ओपिएट: हेरोइन, मॉर्फीन, ओपियम, डीमेरॉल, मेथैडोन, कोडीन, Percodan, Vicodin, OxyContin"}},
  {"label": {"en": "Hallucinogens: LSD ('acid'), mescaline, peyote, psilocybin, STP, 'mushrooms', 'ecstasy', MDA, MDMA",
             "hi": "मूत्र्छाकारक: LSD (एसिड), मेस्कालीन, पेयोटे, साइलोसाइबिन, STP, मशरूम, ایکस्टसी, MDA, MDMA"}},
  {"label": {"en": "Dissociative drugs: PCP ('Angel Dust', 'Peace Pill', 'Hog'), ketamine ('Special K')",
             "hi": "वियोजक द्रव्य: PCP (एंजेल डस्ट, पीस पिल), केटामाइन (स्पेशल के)"}},
  {"label": {"en": "Inhalants: 'glue', ethyl chloride, 'rush', nitrous oxide ('laughing gas'), amyl or butyl nitrate ('poppers')",
             "hi": "श्वसन-द्रव्य: गोंद, एथिल क्लोराइड, rush, नाइट्रस ऑक्साइड (हँसी गैस), poppers"}},
  {"label": {"en": "Cannabis: marijuana, hashish ('hash'), THC, 'pot', 'grass', 'weed', 'reefer'",
             "hi": "कैंनाबिस: गाँजा, चरस, THC, pot, grass, weed"}},
  {"label": {"en": "Sedatives, hypnotics or anxiolytics: Quaalude, Seconal ('reds'), Valium, Xanax, Librium, Ativan, Dalmane, Halcion, barbiturates, Miltown, GHB, Roofinol, 'Roofies'",
             "hi": "शांतक/निद्राकारक/आतंक-नाशक: वैलियम, ज़ैनैक्स, लिब्रियम, एटिवैन, डालमैन, हाल्शियन, बारबिट्यूरेट, GHB, 'रूफीज़'"}},
  {"label": {"en": "Miscellaneous: steroids, nonprescription sleep or diet pills, cough medicine, any others",
             "hi": "विविध: स्टेरॉइड, बिना-पर्चे नींद/डाइट गोलियाँ, खाँसी की दवा, अन्य"}},
  {"label": {"en": "Prescription medications taken to get high (not as prescribed)",
             "hi": "पर्चे-विरोधी उद्देश्य से ली गई पर्ची-दवाइयाँ"}}]

modJ = {
  "id": "J",
  "name": {"en": "Module J — Substance Use Disorder (Non-alcohol)",
           "hi": "माड्यूल J — पदार्थ-सेवन विकार (गैर-मद्य)"},
  "intro": {"en": "Now I am going to show you / read to you a list of street drugs or medicines.",
             "hi": "अब मैं आपको सड़क-दवाइयों/औषधियों की सूची दिखाता/पढ़ता हूँ।"},
  "screen": {"intro": {"en": "Screen-in question (past 12 months)", "hi": "स्क्रीन-इन प्रश्न (पिछले 12 माह)"},
             "questions": [
      q("J1a", "In the past 12 months, did you take any of these drugs more than once, to get high, to feel elated, to get 'a buzz' or to change your mood?",
        "पिछले 12 माह में क्या इनमें से कोई दवा एक से अधिक बार — नशा/उन्माद/मूड-परिवर्तन हेतु — ली?")],
             "gateRule": "IF J1a No -> GO TO THE DIAGNOSTIC BOX, CIRCLE NO AND MOVE TO THE NEXT MODULE.",
             "gateNote": {"en": "If J1a is No, Module J terminates (Substance Use Disorder coded No). Circle each drug taken; specify the most used drug(s) and which drug(s) cause the biggest problems. First explore the criteria for the drug class causing the biggest problems.",
                          "hi": "यदि J1a 'नहीं', माड्यूल J समाप्त (पदार्थ-सेवन विकार 'नहीं' कोड)। ली गई प्रत्येक दवा घेरें; सर्वाधिक-उपयोग एवं सर्वाधिक-समस्याजनक दवा निर्दिष्ट करें। प्रथम सर्वाधिक-समस्याजनक वर्ग के मानदंड जाँचें।"}},
  "drugClasses": J_DRUG_CLASSES,
  "mostUsed": {"id": "J_most_used", "nonScoring": True, "freeText": True,
               "text": {"en": "Specify the most used drug(s):", "hi": "सर्वाधिक प्रयुक्त दवा निर्दिष्ट करें:"}},
  "biggestProblems": {"id": "J_biggest_problems", "nonScoring": True, "freeText": True,
               "text": {"en": "Which drug(s) cause the biggest problems?", "hi": "कौन-सी दवा सर्वाधिक समस्या जनती है?"}},
  "criteriaIntro": {"en": "Considering your use of the selected drug/drug class, in the past 12 months:",
                    "hi": "चयनित दवा/दवा-वर्ग के सेवन के संदर्भ में, पिछले 12 माह में:"},
  "criteria": _use_criteria("J2", "the drug", "दवा"),
  "k1": {"id": "J2k1",
         "text": {"en": "When you cut down on heavy or prolonged use of the drug did you have any of the following withdrawal symptoms? (If yes to the required number for the class, code J2k1 as Yes. This criterion is coded No if the medication is prescribed and used under appropriate medical supervision.)",
                  "hi": "अत्यधिक/दीर्घ सेवन घटाने पर निम्न विषमुक्ति-लक्षण हुए? (वर्ग हेतु अपेक्षित संख्या पर 'हाँ' हो तो J2k1 'हाँ' कोड। यदि दवा उचित चिकित्सीय निगरानी में पर्ची-अनुसार है तो यह 'नहीं' कोड होता है।)"},
         "classChecklists": [
    {"class": {"en": "Sedatives, hypnotics or anxiolytics (2 or more withdrawal symptoms)",
               "hi": "शांतक/निद्राकारक/आतंक-नाशक (2+ लक्षण)"}, "minChecks": 2,
     "items": [l["label"] for l in WITHDRAWAL_ALCOHOL]},
    {"class": {"en": "Opiates (3 or more withdrawal symptoms)", "hi": "ओपिएट (3+ लक्षण)"}, "minChecks": 3,
     "items": [{"en": "Feeling depressed", "hi": "उदासी"},
               {"en": "Nausea or vomiting", "hi": "जी मिचलाना/उल्टी"},
               {"en": "Muscle aches", "hi": "मांसपेशियों में दर्द"},
               {"en": "Runny nose or teary eyes", "hi": "बहती नाक/आँसू"},
               {"en": "Dilated pupils, goose bumps or hair standing on end or sweating", "hi": "पुतली फैलना, रोमांच, पसीना"},
               {"en": "Diarrhea", "hi": "दस्त"},
               {"en": "Yawning", "hi": "जांबई"},
               {"en": "Hot flashes", "hi": "गर्मी की लहरें"},
               {"en": "Trouble sleeping", "hi": "नींद में कठिनाई"}]},
    {"class": {"en": "Stimulants and cocaine (2 or more withdrawal symptoms)", "hi": "उत्तेजक/कोकीन (2+ लक्षण)"}, "minChecks": 2,
     "items": [{"en": "Fatigue", "hi": "थकान"},
               {"en": "Vivid or unpleasant dreams", "hi": "तीव्र/अप्रिय सपने"},
               {"en": "Difficulty sleeping or sleeping too much", "hi": "अनिद्रा/अति-निद्रा"},
               {"en": "Increased appetite", "hi": "बढ़ी भूख"},
               {"en": "Feeling or looking physically or mentally slowed down", "hi": "शारीरिक/मानसिक मंदता"}]},
    {"class": {"en": "Cannabis (3 or more withdrawal symptoms)", "hi": "कैंनाबिस (3+ लक्षण)"}, "minChecks": 3,
     "items": [{"en": "Irritability, anger or aggression", "hi": "चिड़चिड़ापन/क्रोध/आक्रामकता"},
               {"en": "Nervousness or anxiety", "hi": "घबराहट/आतंक"},
               {"en": "Trouble sleeping", "hi": "नींद में कठिनाई"},
               {"en": "Appetite or weight loss", "hi": "भूख/वज़न हानि"},
               {"en": "Restlessness", "hi": "अस्थिरता"},
               {"en": "Feeling depressed", "hi": "उदासी"},
               {"en": "Significant discomfort from: stomach pain, tremors or 'shakes', sweating, hot flashes, chills, headaches",
                "hi": "पेट दर्द, कंपन, पसीना, गर्मी/ठंड की लहरें, सिरदर्द से महत्वपूर्ण कष्ट"}]}]},
  "k2": q("J2k2", "Did you use the drug to reduce or avoid withdrawal symptoms?",
          "क्या विषमुक्ति-लक्षण घटाने/टालने हेतु दवा ली?"),
  "kSummary": {"id": "J2k_summary",
               "rule": "IF YES TO J2k1 OR J2k2, CODE YES. (J2k1 and J2k2 together count as one among the J2 criteria.)",
               "text": {"en": "J2k SUMMARY: If yes to J2k1 or J2k2, code Yes.",
                        "hi": "J2k सारांश: यदि J2k1 या J2k2 'हाँ' तो 'हाँ' कोड।"}},
  "gate": {"rule": "IF <2 of J2a-J2k SUMMARY coded Yes -> Substance Use Disorder NO.",
           "text": {"en": "Are 2 or more J2 answers from J2a through J2k SUMMARY coded Yes? (J2k1 and J2k2 together count as one among these choices.)",
                    "hi": "क्या J2a से J2k सारांश तक के 2 या अधिक उत्तर 'हाँ' कोडित हैं? (J2k1 व J2k2 संयुक्त रूप से एक गिने जाते हैं।)"}},
  "specifierNote": {"en": "Specifiers: MILD = 2-3 of the J2 symptoms; MODERATE = 4-5; SEVERE = 6 or more. IN EARLY REMISSION = criteria not met for between 3 & 12 months; IN SUSTAINED REMISSION = criteria not met for 12 months or more (both with the exception of criterion d [craving]); IN A CONTROLLED ENVIRONMENT = where substance/drug access is restricted.",
                    "hi": "विशेषण: मृदु = J2 के 2-3 लक्षण; मध्यम = 4-5; गंभीर = 6+। प्रारंभिक-मिटी = 3-12 माह मानदंड पूरे नहीं; दीर्घ-मिटी = 12+ माह मानदंड पूरे नहीं (दोनों में मानदंड d [लालसा] अपवाद); नियंत्रित-वातावरण = जहाँ पदार्थ-प्राप्ति सीमित हो।"},
  "diagnosticBoxes": [
    {"id": "J_diag", "label": {"en": "Substance (Drug or Drug Class Name) Use Disorder — Past 12 Months",
                               "hi": "पदार्थ (दवा/दवा-वर्ग) सेवन विकार — पिछले 12 माह"},
     "rule": "J1a Yes AND >=2 of J2a-J2k SUMMARY Yes. Severity by symptom count (2-3 mild, 4-5 moderate, 6+ severe). Record the drug/drug-class name.",
     "flags": USE_DISORDER_SPECIFIERS, "disordersOnPositive": ["substance_use_disorder"]}]
}

# Module K — Psychotic Disorders and Mood Disorder With Psychotic Features.
# Each screening item is an "a" (lifetime) question with a linked "b" (current)
# follow-up coded only if the "a" answer was Yes; K8-K10 are clinician-
# judgment observations. Ask for an example of every positively answered item.
K_SYMPTOMS = [
  {"id": "K1", "role": {"en": "Persecutory delusions", "hi": "अतासी भ्रम"},
   "note": {"en": "NOTE: Ask for examples to rule out actual stalking.",
            "hi": "सूचना: वास्तविक पीछा-करी (stalking) को खारिज करने हेतु उदाहरण पूछें।"},
   "a": q("K1a", "Have you ever believed that people were spying on you, or that someone was plotting against you, or trying to hurt you?",
          "क्या आपको कभी विश्वास हुआ कि लोग आपकी जासूसी कर रहे हैं, या कोई आपके विरुद्ध षड्यंत्र रच रहा है, या आपको नुकसान पहुँचाने का प्रयास कर रहा है?"),
   "b": q("K1b", "If Yes: do you currently believe these things?",
          "यदि 'हाँ': क्या आप वर्तमान में भी इन बातों में विश्वास करते हैं?")},
  {"id": "K2", "role": {"en": "Mind reading / hearing others' thoughts",
                        "hi": "मन-पठन / अन्य के विचार सुनना"},
   "a": q("K2a", "Have you ever believed that someone was reading your mind or could hear your thoughts, or that you could actually read someone's mind or hear what another person was thinking?",
          "क्या आपको कभी विश्वास हुआ कि कोई आपका मन पढ़ रहा है या आपके विचार सुन सकता है, या कि आप वास्तव में किसी का मन पढ़ सकते हैं या दूसरे व्यक्ति के विचार सुन सकते हैं?"),
   "b": q("K2b", "If Yes: do you currently believe these things?",
          "यदि 'हाँ': क्या आप वर्तमान में भी इन बातों में विश्वास करते हैं?")},
  {"id": "K3", "role": {"en": "Thought insertion / possession",
                        "hi": "विचार-आरोपण / ग्रस्त-भाव"},
   "note": {"en": "CLINICIAN: Ask for examples and discount any that are not psychotic.",
            "hi": "चिकित्सक: उदाहरण पूछें और अमनर्विकार वृत्तांतों को खारिज करें।"},
   "a": q("K3a", "Have you ever believed that someone or some force outside of yourself put thoughts in your mind that were not your own, or made you act in a way that was not your usual self? Have you ever felt that you were possessed?",
          "क्या आपको कभी विश्वास हुआ कि किसी बाहरी व्यक्ति/शक्ति ने आपके मन में आपके स्वयं के न हो वाले विचार रखे, या आपको ऐसे व्यवहार पर विवश किया जो आपका स्वाभाविक स्वभाव नहीं? क्या कभी लगा कि आप ग्रस्त (possessed) हैं?"),
   "b": q("K3b", "If Yes: do you currently believe these things?",
          "यदि 'हाँ': क्या आप वर्तमान में भी इन बातों में विश्वास करते हैं?")},
  {"id": "K4", "role": {"en": "Delusions of reference", "hi": "संदर्भ-भ्रम"},
   "a": q("K4a", "Have you ever believed that you were being sent special messages through the TV, radio, internet, newspapers, books, or magazines, or that a person you did not personally know was particularly interested in you?",
          "क्या आपको कभी विश्वास हुआ कि टीवी, रेडियो, इंटरनेट, समाचार-पत्र, पुस्तकों या पत्रिकाओं के माध्यम से आपको विशेष संदेश भेजे जा रहे हैं, या कि कोई व्यक्ति जिसे आप व्यक्तिगत रूप से नहीं जानते विशेष रूप से आपमें रुचि रखता है?"),
   "b": q("K4b", "If Yes: do you currently believe these things?",
          "यदि 'हाँ': क्या आप वर्तमान में भी इन बातों में विश्वास करते हैं?")},
  {"id": "K5", "role": {"en": "Other odd / delusional beliefs reported by others",
                        "hi": "अन्य विषम/भ्रामक मान्यताएँ (परजनों द्वारा)"},
   "note": {"en": "CLINICIAN: Ask for examples. Only code Yes if the examples are clearly delusional ideas not explored in questions K1 to K4 — for example, religious, death, disease or somatic delusions, delusions of grandiosity, jealousy or guilt, or of failure, inadequacy, ruin, or destitution, or nihilistic delusions.",
            "hi": "चिकित्सक: उदाहरण पूछें। केवल तभी 'हाँ' कोड करें जब उदाहरण स्पष्टतः भ्रामक विचार हों जो K1–K4 में नहीं पूछे गए — यथा धर्म/मृत्यु/रोग/कायिक भ्रम; वैभव, ईर्ष्या या अपराध के भ्रम; असफलता, अक्षमता, बर्बादी या दरिद्रता के भ्रम; शून्यतावादी भ्रम।"},
   "a": q("K5a", "Have your relatives or friends ever considered any of your beliefs odd or unusual?",
          "क्या आपके आत्मीय/मित्रों ने कभी आपकी कोई मान्यता विषम या असामान्य मानी?"),
   "b": q("K5b", "If Yes: do they currently consider your beliefs strange or unusual?",
          "यदि 'हाँ': क्या वे वर्तमान में भी आपकी मान्यताएँ विचित्र/असामान्य मानते हैं?")},
  {"id": "K6", "role": {"en": "Auditory hallucinations", "hi": "श्रवण-छलात्मक अनुभव"},
   "voiceNote": {"en": "If yes to voice hallucination: Was the voice commenting on your thoughts or behavior, or did you hear two or more voices talking to each other?",
                 "hi": "यदि स्वर-छलाहन 'हाँ': क्या स्वर आपके विचार/व्यवहार पर टिप्पणी कर रहा था, या दो या अधिक स्वर एक-दूसरे से बात कर रहे थे?"},
   "a": q("K6a", "Have you ever heard things other people couldn't hear, such as voices?",
          "क्या आपने कभी ऐसी चीज़ें सुनी जो दूसरों को नहीं सुनाई दीं, जैसे स्वर/आवाज़ें?"),
   "b": q("K6b", "If Yes to K6a: have you heard sounds/voices in the past month?",
          "यदि K6a 'हाँ': क्या पिछले माह में आपको स्वर/आवाज़ें सुनाई दीं?")},
  {"id": "K7", "role": {"en": "Visual hallucinations", "hi": "दृश्य-छलात्मक अनुभव"},
   "note": {"en": "CLINICIAN: Check to see if these are culturally inappropriate.",
            "hi": "चिकित्सक: जाँचें कि ये सांस्कृतिक दृष्टि से अनुचित तो नहीं हैं।"},
   "a": q("K7a", "Have you ever had visions when you were awake, or have you ever seen things other people couldn't see?",
          "क्या आपको कभी जागती अवस्था में दृश्य-आभास (visions) हुए, या कभी ऐसी चीज़ें दिखाई दीं जो दूसरों को नहीं दिखीं?"),
   "b": q("K7b", "If Yes: have you seen these things in the past month?",
          "यदि 'हाँ': क्या पिछले माह में आपको ऐसी चीज़ें दिखाई दीं?")},
  {"id": "K8", "clinicianJudgment": True,
   "role": {"en": "Disorganized / incoherent speech", "hi": "विशृंखल/असंगत वाक्"},
   "a": q("K8a", "Clinician's judgment: Did the patient ever in the past exhibit disorganized, incoherent or derailed speech, or marked loosening of associations?",
          "चिकित्सकीय निर्णय: क्या रोगी ने अतीत में कभी विशृंखल, असंगत या भ्रष्ट वाक् प्रदर्शित की, या सह-संबंधों का सुस्पष्ट शिथिलन (loosening of associations) देखा गया?"),
   "b": q("K8b", "Clinician's judgment: Is the patient currently exhibiting incoherence, disorganized or derailed speech, or marked loosening of associations?",
          "चिकित्सकीय निर्णय: क्या रोगी वर्तमान में असंगति, विशृंखल/भ्रष्ट वाक् या सह-संबंधों का सुस्पष्ट शिथिलन प्रदर्शित कर रहा है?")},
  {"id": "K9", "clinicianJudgment": True,
   "role": {"en": "Disorganized or catatonic behavior", "hi": "विशृंखल या कटाटोनिक व्यवहार"},
   "a": q("K9a", "Clinician's judgment: Did the patient ever in the past exhibit disorganized or catatonic behavior?",
          "चिकित्सकीय निर्णय: क्या रोगी ने अतीत में कभी विशृंखल या कटाटोनिक व्यवहार प्रदर्शित किया?"),
   "b": q("K9b", "Clinician's judgment: Is the patient currently exhibiting disorganized or catatonic behavior?",
          "चिकित्सकीय निर्णय: क्या रोगी वर्तमान में विशृंखल या कटाटोनिक व्यवहार प्रदर्शित कर रहा है?")},
  {"id": "K10", "clinicianJudgment": True,
   "role": {"en": "Negative symptoms", "hi": "नकारात्मक लक्षण"},
   "a": q("K10a", "Clinician's judgment: Did the patient ever in the past have negative symptoms, e.g. significant reduction of emotional expression or affective flattening, poverty of speech (alogia) or an inability to initiate or persist in goal-directed activities (avolition)?",
          "चिकित्सकीय निर्णय: क्या रोगी को अतीत में कभी नकारात्मक लक्षण रहे — यथा भावनात्मक अभिव्यक्ति का महत्वपूर्ण ह्रास/भाव-फ्लैटनेस, वाक्-दारिद्र्य (alogia), या लक्ष्य-संचालित गतिविधियाँ आरंभ करने/निर्vah करने में अक्षमता (avolition)?"),
   "b": q("K10b", "Clinician's judgment: Are negative symptoms of schizophrenia, e.g. significant reduction of emotional expression or affective flattening, poverty of speech (alogia) or an inability to initiate or persist in goal-directed activities (avolition), prominent during the interview?",
          "चिकित्सकीय निर्णय: क्या साक्षात्कार के दौरान स्क़िज़ोफ्रेनिया के नकारात्मक लक्षण — भावनात्मक अभिव्यक्ति का महत्वपूर्ण ह्रास/भाव-फ्लैटनेस, वाक्-दारिद्र्य (alogia), या लक्ष्य-संचालित गतिविधियों में अक्षमता (avolition) — सुस्पष्ट हैं?")},
]

modK = {
  "id": "K",
  "name": {"en": "Module K — Psychotic Disorders and Mood Disorder With Psychotic Features",
           "hi": "माड्यूल K — मनर्विकार विकार एवं मनर्विकारी लक्षणों सहित मूड विकार"},
  "moduleNote": {"en": "Ask for an example of each question answered positively. Code Yes only if the examples clearly show a distortion of thought or of perception or if they are not culturally appropriate. The purpose of this module is to exclude patients with psychotic disorders. This module needs experience.",
                  "hi": "प्रत्येक सकारात्मक उत्तर का उदाहरण पूछें। केवल तभी 'हाँ' कोड करें जब उदाहरण स्पष्ट रूप से चिंतन या प्रत्यक्ष-ज्ञान का विरूपण दर्शाते हों, या वे सांस्कृतिक दृष्टि से अनुचित हों। इस माड्यूल का उद्देश्य मनर्विकार रोगियों को बहिर्गत करना है। इसके लिए अनुभव आवश्यक है।"},
  "intro": {"en": "Now I am going to ask you about unusual experiences that some people have.",
             "hi": "अब मैं कुछ असामान्य अनुभवों के बारे में पूछूँगा जो कुछ लोगों को होते हैं।"},
  "symptoms": K_SYMPTOMS,
  "k11Intro": {"en": "K11a — Lifetime mood disorder with psychotic features",
               "hi": "K11a — जीवनभर का मनर्विकारी लक्षणों सहित मूड विकार"},
  "k11a": {"id": "K11a",
           "text": {"en": "Are 1 or more \"a\" questions from K1a to K7a coded Yes? AND is either MAJOR DEPRESSIVE EPISODE (current, recurrent or past) or MANIC OR HYPOMANIC EPISODE (current or past) coded Yes? AND how long has the mood episode lasted / how long has the psychotic episode lasted? If such a mood episode is present, code Yes to K11a ONLY IF the mood disturbance is present for the majority of the total duration of the active and residual periods of the psychotic symptoms. Otherwise code No.",
                    "hi": "क्या K1a से K7a तक के 1 या अधिक «a» प्रश्न 'हाँ' कोडित हैं? और क्या प्रमुख अवसादी एपिसोड (वर्तमान/पुनरावर्ती/अतीत) या मैैनिक/हाइपोमैैनिक एपिसोड (वर्तमान/अतीत) 'हाँ' कोडित है? साथ ही मूड एपिसोड कब तक रहा / मनर्विकारी एपिसोड कब तक रहा? यदि ऐसा मूड एपिसोड उपस्थित है तो K11a पर 'हाँ' केवल तभी कोड करें जब मूड-विकृति मनर्विकारी लक्षणों की सक्रिय एवं शेषकालीन अवधियों की कुल अवधि के अधिकांश भाग में विद्यमान रही हो। अन्यथा 'नहीं' कोड करें।"},
           "durationFields": [{"id": "K11_mood_duration", "label": {"en": "How long has the mood episode lasted?", "hi": "मूड एपिसोड कब तक रहा?"}},
                              {"id": "K11_psych_duration", "label": {"en": "How long has the psychotic episode lasted?", "hi": "मनर्विकारी एपिसोड कब तक रहा?"}}],
           "skipRule": {"en": "If No to K11a and the total duration of the mood episode is LESS than the total duration of the psychotic episode, then circle No in both 'MOOD DISORDER WITH PSYCHOTIC FEATURES' diagnostic boxes and move to K13.",
                        "hi": "यदि K11a 'नहीं' और मूड एपिसोड की कुल अवधि मनर्विकारी एपिसोड की कुल अवधि से कम है, तो दोनों 'मनर्विकारी लक्षणों सहित मूड विकार' निदान-बक्ses में 'नहीं' घेरें और K13 पर जाएँ।"}},
  "k11b": {"id": "K11b",
           "text": {"en": "You told me earlier that you had period(s) when you felt (depressed/high/persistently irritable). Were the beliefs and experiences you just described (symptoms coded Yes from K1a to K7a) restricted exclusively to times when you were feeling depressed/high/irritable? If the patient ever had a period of at least 2 weeks of having these beliefs or experiences (psychotic symptoms) when they were NOT depressed/high/irritable, code NO to this disorder. If the answer is No to this disorder grouping, also circle No to K12 and move to K13.",
                    "hi": "आपने पहले बताया कि आपको ऐसी अवधियाँ आईं जब आप (उदास/उन्मुक्त/सतत चिड़चिड़े) महसूस करते थे। क्या अभी वर्णित मान्यताएँ/अनुभव (K1a–K7a में 'हाँ' कोडित लक्षण) केवल उन्हीं समयों तक सीमित थे जब आप उदास/उन्मुक्त/चिड़चिड़े थे? यदि रोगी को कभी कम से कम 2 सप्ताह तक ऐसी मान्यताएँ/अनुभव (मनर्विकारी लक्षण) उन समयों में हुए जब वे उदास/उन्मुक्त/चिड़चिड़े नहीं थे, तो इस विकार पर 'नहीं' कोड करें। यदि इस समूह पर उत्तर 'नहीं' है तो K12 पर भी 'नहीं' घेरें और K13 पर जाएँ।"}},
  "k12": {"id": "K12",
          "text": {"en": "Are 1 or more \"b\" questions from K1b to K7b coded Yes? AND is either MAJOR DEPRESSIVE EPISODE (current) or MANIC OR HYPOMANIC EPISODE (current) coded Yes? If the answer is Yes to this disorder (lifetime or current), circle No to K13 and K14 and move to the next module.",
                   "hi": "क्या K1b से K7b तक के 1 या अधिक «b» प्रश्न 'हाँ' कोडित हैं? और क्या प्रमुख अवसादी एपिसोड (वर्तमान) या मैैनिक/हाइपोमैैनिक एपिसोड (वर्तमान) 'हाँ' कोडित है? यदि इस विकार पर उत्तर 'हाँ' (जीवनभर या वर्तमान) है तो K13 व K14 पर 'नहीं' घेरें और अगले माड्यूल पर जाएँ।"}},
  "k13": {"id": "K13",
          "text": {"en": "Are 1 or more \"b\" questions from K1b to K8b coded Yes? AND are 2 or more \"b\" questions from K1b to K10b coded Yes? AND did at least two of the psychotic symptoms occur during the same 1-month period? AND is \"RULE OUT ORGANIC CAUSE (O2 SUMMARY)\" coded Yes?",
                   "hi": "क्या K1b से K8b तक के 1 या अधिक «b» प्रश्न 'हाँ' कोडित हैं? और क्या K1b से K10b तक के 2 या अधिक «b» प्रश्न 'हाँ' कोडित हैं? और क्या कम से कम दो मनर्विकारी लक्षण उसी 1-माह की अवधि में हुए? और क्या «जैविक कारण का बहिर्गमन (O2 सारांश)» 'हाँ' कोडित है?"}},
  "k14": {"id": "K14",
          "text": {"en": "Is K13 coded Yes? OR [are 1 or more \"a\" questions from K1a to K8a coded Yes? AND are 2 or more \"a\" questions from K1a to K10a coded Yes? AND did at least 2 of the psychotic symptoms occur during the same 1-month period?] AND is \"RULE OUT ORGANIC CAUSE (O2 SUMMARY)\" coded Yes?",
                   "hi": "क्या K13 'हाँ' कोडित है? या [K1a से K8a तक के 1 या अधिक «a» प्रश्न 'हाँ' कोडित हैं? और K1a से K10a तक के 2 या अधिक «a» प्रश्न 'हाँ' कोडित हैं? और कम से कम 2 मनर्विकारी लक्षण उसी 1-माह की अवधि में हुए?] और «जैविक कारण का बहिर्गमन (O2 सारांश)» 'हाँ' कोडित है?"}},
  "diagnosticBoxes": [
    {"id": "K11_diag", "label": {"en": "Mood Disorder With Psychotic Features — Lifetime",
                                 "hi": "मनर्विकारी लक्षणों सहित मूड विकार — जीवनभर"},
     "rule": "K11a Yes AND K11b Yes (psychotic symptoms confined to the mood episodes). If Yes here or in K12, circle No to K13 and K14.",
     "flags": ["LIFETIME"], "disordersOnPositive": ["mood_disorder_with_psychotic_features"]},
    {"id": "K12_diag", "label": {"en": "Mood Disorder With Psychotic Features — Current",
                                 "hi": "मनर्विकारी लक्षणों सहित मूड विकार — वर्तमान"},
     "rule": "1+ of K1b-K7b Yes AND a CURRENT major depressive or manic/hypomanic episode Yes AND K11b logic (psychosis restricted to mood episodes).",
     "flags": ["CURRENT"], "disordersOnPositive": ["mood_disorder_with_psychotic_features"]},
    {"id": "K13_diag", "label": {"en": "Psychotic Disorder — Current", "hi": "मनर्विकार विकार — वर्तमान"},
     "rule": "1+ of K1b-K8b Yes AND 2+ of K1b-K10b Yes AND >=2 symptoms within the same 1-month period AND organic cause ruled out (O2 summary). Not applicable if a Mood Disorder With Psychotic Features box was coded Yes.",
     "flags": ["CURRENT"], "disordersOnPositive": ["psychotic_disorder"]},
    {"id": "K14_diag", "label": {"en": "Psychotic Disorder — Lifetime", "hi": "मनर्विकार विकार — जीवनभर"},
     "rule": "K13 Yes, OR [1+ of K1a-K8a Yes AND 2+ of K1a-K10a Yes AND >=2 symptoms within the same 1-month period] AND organic cause ruled out (O2 summary).",
     "flags": ["LIFETIME"], "disordersOnPositive": ["psychotic_disorder"]}]
}

# Height/weight table corresponding to a BMI threshold of 17.0 kg/m2 (Module L).
HEIGHT_WEIGHT_TABLE = {
  "bmiThreshold": 17.0,
  "columns": [
    {"ftin": "4'9\"",  "cm": 145, "lb": 79,  "kg": 36},
    {"ftin": "4'10\"", "cm": 147, "lb": 82,  "kg": 37},
    {"ftin": "4'11\"", "cm": 150, "lb": 84,  "kg": 38.5},
    {"ftin": "5'0\"",  "cm": 152, "lb": 87,  "kg": 39.5},
    {"ftin": "5'1\"",  "cm": 155, "lb": 90,  "kg": 41},
    {"ftin": "5'2\"",  "cm": 158, "lb": 93,  "kg": 42.5},
    {"ftin": "5'3\"",  "cm": 160, "lb": 96,  "kg": 43.5},
    {"ftin": "5'4\"",  "cm": 163, "lb": 99,  "kg": 45.5},
    {"ftin": "5'5\"",  "cm": 165, "lb": 102, "kg": 46.5},
    {"ftin": "5'6\"",  "cm": 168, "lb": 106, "kg": 48},
    {"ftin": "5'7\"",  "cm": 170, "lb": 109, "kg": 49},
    {"ftin": "5'8\"",  "cm": 173, "lb": 112, "kg": 51},
    {"ftin": "5'9\"",  "cm": 175, "lb": 115, "kg": 52},
    {"ftin": "5'10\"", "cm": 178, "lb": 119, "kg": 54},
    {"ftin": "5'11\"", "cm": 180, "lb": 122, "kg": 55},
    {"ftin": "6'0\"",  "cm": 183, "lb": 125, "kg": 57},
    {"ftin": "6'1\"",  "cm": 185, "lb": 129, "kg": 58.5},
    {"ftin": "6'2\"",  "cm": 188, "lb": 133, "kg": 60},
    {"ftin": "6'3\"",  "cm": 191, "lb": 136, "kg": 62}],
  "note": {"en": "The weight thresholds above are calculated using a body mass index (BMI) equal to or below 17.0 kg/m2 for the patient's height using the Center of Disease Control & Prevention BMI Calculator. This is the threshold guideline below which a person is deemed underweight by the DSM-5 for Anorexia Nervosa.",
            "hi": "उपरोक्त भार-सीमाएँ रोगी की ऊँचाई हेतु CDC BMI कैलकुलेटर का उपयोग कर BMI 17.0 किग्रा/मी² या उससे कम पर गणना की गई हैं। यह वह सीमा-निर्देश है जिसके नीचे व्यक्ति को DSM-5 द्वारा एनोरेक्सिया नर्वोसा हेतु अल्पभारी माना जाता है।"}}

modL = {
  "id": "L",
  "name": {"en": "Module L — Anorexia Nervosa",
           "hi": "माड्यूल L — एनोरेक्सिया नर्वोसा"},
  "screen": {"intro": {"en": "L1 — Height and lowest weight in the past 3 months",
                        "hi": "L1 — ऊँचाई और पिछले 3 माह का न्यूनतम वज़न"},
             "questions": [
      q("L1a", "How tall are you? (feet/inches or centimetres)",
        "आपकी ऊँचाई कितनी है? (फ़ीट/इंच या सेंटीमीटर)", nonScoring=True, measurement="height"),
      q("L1b", "What was your lowest weight in the past 3 months? (pounds or kilograms)",
        "पिछले 3 माह में आपका सबसे कम वज़न क्या था? (पाउंड या किलोग्राम)", nonScoring=True, measurement="weight")],
             "gateRule": "IF L1c No -> GO TO THE DIAGNOSTIC BOX, CIRCLE NO, AND MOVE TO THE NEXT MODULE.",
             "gateNote": {"en": "If the patient's weight is above the threshold for his/her height, Module L terminates (Anorexia Nervosa coded No).",
                          "hi": "यदि रोगी का वज़न उसकी ऊँचाई की सीमा से अधिक है, तो माड्यूल L समाप्त (एनोरेक्सिया नर्वोसा 'नहीं' कोड)।"}},
  "l1c": {"id": "L1c",
          "text": {"en": "Is patient's weight equal to or below the threshold corresponding to his/her height? (See the height/weight table below.)",
                   "hi": "क्या रोगी का वज़न उसकी ऊँचाई संगत सीमा के बराबर या उससे कम है? (नीचे ऊँचाई/वज़न सारणी देखें।)"},
          "thresholdTable": HEIGHT_WEIGHT_TABLE},
  "pastThreeMonthsIntro": {"en": "In the past 3 months:", "hi": "पिछले 3 माह में:"},
  "l2": q("L2", "In spite of this low weight, have you tried not to gain weight or to restrict your food intake?",
          "इतने कम वज़न के बावजूद, क्या आपने वज़न बढ़ने से रोकने या भोजन-सेवन सीमित करने का प्रयास किया?"),
  "l3": q("L3", "Have you intensely feared gaining weight or becoming fat, even though you were underweight?",
          "क्या आपको अल्पभारी होने के बावजूद वज़न बढ़ने या मोटे होने का तीव्र भय रहा?"),
  "l4": [
      q("L4a", "Have you considered yourself too big/fat or that part of your body was too big/fat?",
        "क्या आपने स्वयं को अधिक बड़ा/मोटा या शरीर का कोई भाग अधिक बड़ा/मोटा समझा?"),
      q("L4b", "Has your body weight or shape greatly influenced how you felt about yourself?",
        "क्या आपके शारीरिक वज़न/आकार ने स्वयं के प्रति आपकी भावना को बहुत प्रभावित किया?"),
      q("L4c", "Have you thought that your current low body weight was normal or excessive?",
        "क्या आपने वर्तमान कम शारीरिक वज़न को सामान्य या अधिक माना?")],
  "l5Gate": {"rule": "IF 0 of L4 answers Yes -> GO TO THE DIAGNOSTIC BOX, CIRCLE NO, AND MOVE TO THE NEXT MODULE.",
             "text": {"en": "L5: Are 1 or more items from L4 coded Yes?",
                      "hi": "L5: क्या L4 के 1 या अधिक मद 'हाँ' कोडित हैं?"}},
  "diagnosticBoxes": [
    {"id": "L_diag", "label": {"en": "Anorexia Nervosa — Current", "hi": "एनोरेक्सिया नर्वोसा — वर्तमान"},
     "rule": "L1c Yes AND L2 Yes AND L3 Yes AND L5 Yes (1+ of L4). Restricting vs Binge-Eating/Purging type is decided in Module M (M7/M8).",
     "flags": ["CURRENT"], "disordersOnPositive": ["eating_anorexia"]}]
}

# Shared severity specifiers for eating disorders (Modules M / MB).
EATING_SEVERITY_SPECIFIERS = ["MILD", "MODERATE", "SEVERE", "EXTREME"]

modM = {
  "id": "M",
  "name": {"en": "Module M — Bulimia Nervosa",
           "hi": "माड्यूल M — बुलिमिया नर्वोसा"},
  "screen": {"intro": {"en": "Screen-in question (past three months)", "hi": "स्क्रीन-इन प्रश्न (पिछले तीन माह)"},
             "questions": [
      q("M1", "In the past three months, did you have eating binges or times when you ate a very large amount of food within a 2-hour period?",
        "पिछले तीन माह में, क्या आपको भोजन-प्रपात (binge) हुए या ऐसे समय जब आपने 2-घंटे की अवधि में बहुत अधिक मात्रा में भोजन किया?")],
             "gateRule": "IF M1 No -> GO TO THE DIAGNOSTIC BOXES, CIRCLE NO IN THE BULIMIA NERVOSA AND IN THE ANOREXIA NERVOSA BINGE EATING/PURGING TYPE DIAGNOSTIC BOXES. BUT IF ANOREXIA NERVOSA (MODULE L) IS CODED YES, CONTINUE WITH THE QUESTIONS TO BE ABLE TO PROPERLY CODE ANOREXIA NERVOSA RESTRICTING TYPE.",
             "gateNote": {"en": "If M1 is No, circle No in both the Bulimia Nervosa box and the Anorexia Nervosa Binge-Eating/Purging Type box; if Anorexia Nervosa (Module L) was coded Yes, continue with the questions to properly code Anorexia Nervosa Restricting Type.",
                          "hi": "यदि M1 'नहीं', तो बुलिमिया नर्वोसा एवं एनोरेक्सिया नर्वोसा बिंज-ईटिंग/पर्जिंग-टाइप दोनों बक्सेस में 'नहीं' घेरें; यदि एनोरेक्सिया नर्वोसा (माड्यूल L) 'हाँ' कोडित है, तो रेस्ट्रिक्टिंग-टाइप सही ढंग से कोड करने हेतु प्रश्न जारी रखें।"}},
  "m2": q("M2", "During these binges, did you feel that your eating was out of control?",
          "इन प्रपातों के दौरान, क्या आपको लगा कि आपका भोजन नियंत्रण से बाहर था?"),
  "pastThreeMonthsIntro": {"en": "In the past 3 months:", "hi": "पिछले 3 माह में:"},
  "m3": q("M3", "Did you have eating binges as often as once a week?",
          "क्या आपको सप्ताह में कम से कम एक बार भोजन-प्रपात हुए?"),
  "m4": q("M4", "Did you do anything to compensate for, or to prevent a weight gain, like vomiting, fasting, exercising or taking laxatives, enemas, diuretics (fluid pills), or other medications? Did you do this as often as once a week?",
          "क्या आपने वज़न बढ़ने से रोकने/क्षतिपूर्ति हेतु कुछ किया — जैसे उल्टी, उपवास, व्यायाम, या लैक्सेटिव, एनिमा, डाययूरेटिक (फ्लुइड पिल्स) अथवा अन्य दवाएँ लेना? क्या यह सप्ताह में कम से कम एक बार किया?"),
  "m4a": {"id": "M4a", "numeric": True, "max": 99,
          "text": {"en": "M4a — number recorded here refers to the frequency of inappropriate compensatory behaviours (episodes per week); see M6.",
                   "hi": "M4a — यहाँ अंकित संख्या अनुचित क्षतिपूर्ति-व्यवहारों की आवृत्ति (सप्ताह में एपिसोड) दर्शाती है; M6 देखें।"}},
  "m5": q("M5", "Did your body weight or shape greatly influence how you felt about yourself?",
          "क्या आपके शारीरिक वज़न/आकार ने स्वयं के प्रति आपकी भावना को बहुत प्रभावित किया?"),
  "m6Episodes": {"id": "M6a", "numeric": True, "max": 99,
                  "text": {"en": "Number of episodes of inappropriate compensatory behaviors per week?",
                           "hi": "प्रति सप्ताह अनुचित क्षतिपूर्ति-व्यवहारों के एपिसोड की संख्या?"}},
  "m6Days": {"id": "M6b", "numeric": True, "max": 7,
             "text": {"en": "Number of days of inappropriate compensatory behaviors per week?",
                      "hi": "प्रति सप्ताह अनुचित क्षतिपूर्ति-व्यवहारों वाले दिनों की संख्या?"}},
  "m7": q("M7", "Did these binges occur only when you were under the threshold weight (write in the threshold weight for this patient's height from the height/weight table in the Anorexia Nervosa module)?",
          "क्या ये प्रपात केवल तभी हुए जब आप सीमा-वज़न (माड्यूल L की ऊँचाई/वज़न सारणी से इस रोगी की ऊँचाई हेतु सीमा-वज़न यहाँ लिखें) से कम पर थे?"),
  "m8Gate": {"rule": "IF NOT (M5 Yes AND (M6 No OR M7 No)) -> Bulimia Nervosa NO.",
             "text": {"en": "Is M5 coded Yes AND is either M6 or M7 coded No?",
                      "hi": "क्या M5 'हाँ' कोडित है और क्या M6 या M7 में से कोई भी 'नहीं' कोडित है?"}},
  "specifierNote": {"en": "Specifiers of eating disorder: MILD = 1-3 episodes of inappropriate compensatory behaviors; MODERATE = 4-7; SEVERE = 8-13; EXTREME = 14 or more.",
                    "hi": "भोजन-विकार विशेषण: मृदु = अनुचित क्षतिपूर्ति-व्यवहारों के 1-3 एपिसोड; मध्यम = 4-7; गंभीर = 8-13; अत्यंत गंभीर = 14 या अधिक।"},
  "diagnosticBoxes": [
    {"id": "M_diag", "label": {"en": "Bulimia Nervosa — Current", "hi": "बुलिमिया नर्वोसा — वर्तमान"},
     "rule": "M1 Yes AND M2 Yes AND M8 gate Yes (M5 Yes AND either M6 or M7 No). Severity by weekly episodes of inappropriate compensatory behaviors (1-3 mild, 4-7 moderate, 8-13 severe, 14+ extreme).",
     "flags": ["CURRENT"] + EATING_SEVERITY_SPECIFIERS, "disordersOnPositive": ["eating_bulimia"]},
    {"id": "M_an_bept_diag", "label": {"en": "Anorexia Nervosa, Binge Eating/Purging Type — Current",
                                       "hi": "एनोरेक्सिया नर्वोसा, बिंज-ईटिंग/पर्जिंग प्रकार — वर्तमान"},
     "rule": "Asked only if Module L (Anorexia Nervosa) was coded Yes: M7 Yes (binges occurred only while underweight) -> Binge-Eating/Purging Type; otherwise continue to code Restricting Type.",
     "flags": ["CURRENT"], "disordersOnPositive": ["eating_anorexia"]},
    {"id": "M_an_restrict_diag", "label": {"en": "Anorexia Nervosa, Restricting Type — Current",
                                            "hi": "एनोरेक्सिया नर्वोसा, रेस्ट्रिक्टिंग प्रकार — वर्तमान"},
     "rule": "Do the patient's symptoms meet criteria for Anorexia Nervosa? AND is M2 or M4 coded No? (Patient has not been regularly bingeing or purging.)",
     "flags": ["CURRENT"], "disordersOnPositive": ["eating_anorexia"]}]}

modMB = {
  "id": "MB",
  "name": {"en": "Module MB — Binge Eating Disorder",
           "hi": "माड्यूल MB — बिंज-ईटिंग (अतिभक्षण) विकार"},
  "gateRules": [
    {"rule": "IF MB1 Yes -> GO TO THE DIAGNOSTIC BOX, CIRCLE NO, AND MOVE TO THE NEXT MODULE.",
     "id": "MB1", "text": {"en": "Do the patient's symptoms meet criteria for Anorexia Nervosa?",
                            "hi": "क्या रोगी के लक्षण एनोरेक्सिया नर्वोसा के मानदंड पूरे करते हैं?"}},
    {"rule": "IF MB2 Yes -> GO TO THE DIAGNOSTIC BOX, CIRCLE NO, AND MOVE TO THE NEXT MODULE.",
     "id": "MB2", "text": {"en": "Do the patient's symptoms meet criteria for Bulimia Nervosa?",
                            "hi": "क्या रोगी के लक्षण बुलिमिया नर्वोसा के मानदंड पूरे करते हैं?"}},
    {"rule": "IF MB3 No -> GO TO THE DIAGNOSTIC BOX, CIRCLE NO, AND MOVE TO THE NEXT MODULE.",
     "id": "MB3", "text": {"en": "Is M2 coded Yes? (During binges, eating felt out of control.)",
                            "hi": "क्या M2 'हाँ' कोडित है? (प्रपात के दौरान भोजन नियंत्रण-बाहर लगा।)"}},
    {"rule": "IF MB4 No -> GO TO THE DIAGNOSTIC BOX, CIRCLE NO, AND MOVE TO THE NEXT MODULE.",
     "id": "MB4", "text": {"en": "Is M3 coded Yes? (Binges at least once a week.)",
                            "hi": "क्या M3 'हाँ' कोडित है? (सप्ताह में कम से कम एक बार प्रपात।)"}},
    {"rule": "IF MB5 No -> GO TO THE DIAGNOSTIC BOX, CIRCLE NO, AND MOVE TO THE NEXT MODULE.",
     "id": "MB5", "text": {"en": "Is M4 coded Yes? If M4 was bypassed in Module M (Bulimia Nervosa), ask M4 now to code MB5.",
                            "hi": "क्या M4 'हाँ' कोडित है? यदि माड्यूल M (बुलिमिया नर्वोसा) में M4 छोड़ा गया था, तो MB5 कोड हेतु अब M4 पूछें।"}}],
  "mb6Intro": {"en": "In the last 3 months during the binging did you:", "hi": "पिछले 3 माह में प्रपात के दौरान क्या आप:"},
  "mb6": [
      q("MB6a", "Eat more rapidly than normal?", "क्या सामान्य से तेज़ खाते थे?"),
      q("MB6b", "Eat until you felt uncomfortably full?", "क्या अप्रिय ढंग से भरपूर महसूस करने तक खाते थे?"),
      q("MB6c", "Eat large amounts of food when you were not hungry?", "क्या भूख न होने पर भी अधिक भोजन खाते थे?"),
      q("MB6d", "Eat alone because you felt embarrassed about how much you were eating?", "क्या खाने की मात्रा से शर्मिंदगी के कारण अकेले खाते थे?"),
      q("MB6e", "Feel guilty, depressed or disgusted with yourself after binging?", "क्या प्रपात के बाद स्वयं के प्रति अपराधबोध, उदासी या घृणा महसूस हुई?")],
  "mb6Gate": {"rule": "IF <3 of MB6 answers Yes -> GO TO THE DIAGNOSTIC BOX, CIRCLE NO, AND MOVE TO THE NEXT MODULE.",
              "text": {"en": "Are 3 or more MB6 questions coded Yes?",
                        "hi": "क्या MB6 के 3 या अधिक प्रश्न 'हाँ' कोडित हैं?"}},
  "mb7": q("MB7", "Does your binging distress you a lot?",
           "क्या आपका प्रपात आपको बहुत कष्ट देता है?"),
  "mb8Episodes": {"id": "MB8a", "numeric": True, "max": 99,
                  "text": {"en": "Number of binge eating episodes per week?",
                            "hi": "प्रति सप्ताह अतिभक्षण एपिसोड की संख्या?"}},
  "mb8Days": {"id": "MB8b", "numeric": True, "max": 7,
              "text": {"en": "Number of binge eating days per week?",
                       "hi": "प्रति सप्ताह अतिभक्षण दिनों की संख्या?"}},
  "specifierNote": {"en": "Specifiers of eating disorder: MILD = 1-3 episodes of binge eating per week; MODERATE = 4-7; SEVERE = 8-13; EXTREME = 14 or more.",
                    "hi": "भोजन-विकार विशेषण: मृदु = प्रति सप्ताह 1-3 प्रपात एपिसोड; मध्यम = 4-7; गंभीर = 8-13; अत्यंत गंभीर = 14 या अधिक।"},
  "diagnosticBoxes": [
    {"id": "MB_diag", "label": {"en": "Binge-Eating Disorder — Current", "hi": "बिंज-ईटिंग (अतिभक्षण) विकार — वर्तमान"},
     "rule": "MB1 No AND MB2 No AND MB3 Yes AND MB4 Yes AND MB5 No AND >=3 of MB6 Yes AND MB7 Yes. Severity by weekly binge-eating episodes (1-3 mild, 4-7 moderate, 8-13 severe, 14+ extreme).",
     "flags": ["CURRENT"] + EATING_SEVERITY_SPECIFIERS, "disordersOnPositive": ["eating_binge_eating"]}]}

modN = {
  "id": "N",
  "name": {"en": "Module N — Generalized Anxiety Disorder",
           "hi": "माड्यूल N — सामान्यीकृत चिंता विकार"},
  "screen": {"intro": {"en": "Screen-in questions (past 6 months)", "hi": "स्क्रीन-इन प्रश्न (पिछले 6 माह)"},
             "probe": {"en": "IN ENGLISH, if the patient is unclear about what you mean, probe by asking (Do others think that you are a worrier or a 'worry wart'?) and get examples.",
                        "hi": "यदि रोगी को प्रश्न का अर्थ स्पष्ट न हो तो पूछकर जाँचें (क्या दूसरे लोग आपको चिंता-प्रवण व्यक्ति समझते हैं?) और उदाहरण प्राप्त करें।"},
             "questions": [
      q("N1a", "Were you excessively anxious or worried about several routine things, over the past 6 months?",
        "पिछले 6 माह में क्या आप अत्यधिक चिंतित/चिंताग्रस्त रहे — कई सामान्य/रोज़मर्रा की बातों को लेकर?"),
      q("N1b", "Are these anxieties and worries present most days?",
        "क्या ये आतंक/चिंताएँ अधिकतर दिनों में विद्यमान रहीं?")],
             "gateRule": "IF N1a OR N1b No -> GO TO THE DIAGNOSTIC BOX, CIRCLE NO, AND MOVE TO THE NEXT MODULE.",
             "gateNote": {"en": "If either screen-in is No, Module N terminates (Generalized Anxiety Disorder coded No).",
                          "hi": "यदि कोई भी स्क्रीन-इन 'नहीं', माड्यूल N समाप्त (सामान्यीकृत चिंता विकार 'नहीं' कोड)।"}},
  "notBetterExplainedGate": {"rule": "IF Yes (anxieties restricted to / better explained by a prior disorder) -> GO TO THE DIAGNOSTIC BOX, CIRCLE NO, AND MOVE TO THE NEXT MODULE.",
                             "text": {"en": "Are the patient's anxiety and worries restricted exclusively to, or better explained by, any disorder prior to this point?",
                                      "hi": "क्या रोगी की चिंता/आतंक अनन्य रूप से यहाँ तक के किसी पूर्व विकार तक सीमित हैं, या उससे बेहतर ढंग से व्याख्यायित होती हैं?"}},
  "n2": q("N2", "Do you find it difficult to control the worries?",
          "क्या आपको चिंताओं को नियंत्रित करना कठिन लगता है?"),
  "n3Intro": {"en": "When you were anxious over the past 6 months, did you, most of the time: (Code No if the symptoms are confined to features of any disorder explored prior to this point.)",
              "hi": "पिछले 6 माह में जब आप चिंतित थे, तब अधिकतर समय क्या आप: (यदि लक्षण यहाँ तक जाँचे गए किसी विकार की विशेषताओं तक सीमित हों तो 'नहीं' कोड करें।)"},
  "n3": [
      q("N3a", "Feel restless, keyed up or on edge?", "बेचैन, उत्तेजित या सतर्क भाव?"),
      q("N3b", "Have muscle tension?", "मांसपेशियों में तनाव?"),
      q("N3c", "Feel tired, weak or exhausted easily?", "जल्दी थकान, दुर्बलता या शून्यता?"),
      q("N3d", "Have difficulty concentrating or find your mind going blank?", "ध्यान केंद्रित करने में कठिनाई या मन खाली हो जाना?"),
      q("N3e", "Feel irritable?", "चिड़चिड़ापन?"),
      q("N3f", "Have difficulty sleeping (difficulty falling asleep, waking up in the middle of the night, early morning wakening or sleeping excessively)?",
        "नींद में कठिनाई (सोने में कठिनाई, बीच में उठना, सुबह जल्द उठना या अधिक सोना)?")],
  "n3Gate": {"rule": "IF <3 of N3 answers Yes -> GO TO THE DIAGNOSTIC BOX, CIRCLE NO, AND MOVE TO THE NEXT MODULE.",
             "text": {"en": "Are 3 or more N3 answers coded Yes?", "hi": "क्या N3 के 3 या अधिक उत्तर 'हाँ' कोडित हैं?"}},
  "n4": q("N4", "Do these anxieties and worries significantly disrupt your ability to work, to function socially or in your relationships or in other important areas of your life or cause you significant distress?",
          "क्या ये आतंक/चिंताएँ कार्य, सामाजिक/संबंध-कार्यक्षमता या जीवन के अन्य महत्वपूर्ण क्षेत्रों को महत्वपूर्ण रूप से बाधित करती हैं, या आपको महत्वपूर्ण कष्ट देती हैं?"),
  "diagnosticBoxes": [
    {"id": "N_diag", "label": {"en": "Generalized Anxiety Disorder — Current", "hi": "सामान्यीकृत चिंता विकार — वर्तमान"},
     "rule": "N1a AND N1b AND not-better-explained gate No AND N2 AND N3-gate (>=3) AND N4 all Yes AND organic cause ruled out (O2 summary).",
     "flags": ["CURRENT"], "disordersOnPositive": ["gad"]}]}

NYU_OPTIONS = [{"v": "no", "label": YN_NO}, {"v": "yes", "label": YN_YES},
               {"v": "uncertain", "label": {"en": "Uncertain", "hi": "अनिश्चित"}}]

modO = {
  "id": "O",
  "name": {"en": "Module O — Rule Out Medical, Organic or Drug Causes For All Disorders",
           "hi": "माड्यूल O — सभी विकारों हेतु चिकित्सकीय/जैविक/दवा-जन्य कारणों का बहिर्गमन"},
  "applicabilityNote": {"en": "If the patient codes positive for any current disorder or a major depressive episode or a manic or a hypomanic episode, ask the following about the period just before these symptoms began.",
                         "hi": "यदि रोगी किसी वर्तमान विकार या प्रमुख अवसादी एपिसोड या मैैनिक/हाइपोमैैनिक एपिसोड पर सकारात्मक कोडित होता है, तो इन लक्षणों के ठीक पूर्व काल के बारे में निम्न पूछें।"},
  "intro": {"en": "Just before these symptoms began:", "hi": "इन लक्षणों के शुरू होने से ठीक पहले:"},
  "questions": [
    q("O1a", "Were you taking any drugs or medicines or in withdrawal from any of these?",
      "क्या आप कोई नशा/दवा ले रहे थे या उनसे विषमुक्ति-अवस्था में थे?", options=NYU_OPTIONS),
    q("O1b", "Did you have any medical illness?", "क्या आपको कोई चिकित्सकीय रोग था?", options=NYU_OPTIONS),
    q("O2", "If O1a or O1b is coded Yes: in the clinician's judgment, is either likely to be a direct cause of the patient's disorder? If necessary, ask additional open-ended questions.",
      "यदि O1a या O1b 'हाँ' कोडित हो: चिकित्सक के निर्णय अनुसार, क्या इनमें से कोई रोगी के विकार का प्रत्यक्ष कारण होने की संभावना है? आवश्यकतानुसार अतिरिक्त खुले प्रश्न पूछें।",
      options=NYU_OPTIONS, clinicianJudgment=True)],
  "o2Summary": {"id": "O2_summary", "derived": True,
                "rule": "Has an 'organic'/medical/drug related cause been ruled out? If O2 is Yes, then O2 SUMMARY is No. If O2 is No, then O2 SUMMARY is Yes. Otherwise it is Uncertain.",
                "text": {"en": "O2 SUMMARY: Has an 'organic'/medical/drug related cause been ruled out?",
                          "hi": "O2 सारांश: क्या 'जैविक'/चिकित्सकीय/दवा-संबंधित कारण बहिर्गत किया गया है?"},
                "options": NYU_OPTIONS}}

modP = {
  "id": "P",
  "name": {"en": "Module P — Antisocial Personality Disorder",
           "hi": "माड्यूल P — प्रतिसामाजिक व्यक्तित्व विकार"},
  "p1Intro": {"en": "Before you were 15 years old, did you:", "hi": "15 वर्ष की आयु से पूर्व, क्या आप:"},
  "p1": [
      q("P1a", "Repeatedly skip school or run away from home overnight or stayed out at night against your parent's rules?",
        "बार-बार विद्यालय छोड़ना, रात को घर से भागना, या माता-पिता के नियमों के विरुद्ध रात बाहर रहना?"),
      q("P1b", "Repeatedly lie, cheat, 'con' others, or steal or break into someone's house or car?",
        "बार-बार झूठ, छल, दूसरों को ठगना, चोरी, या किसी के घर/गाड़ी में जबरन प्रवेश?"),
      q("P1c", "Start fights or bully, threaten, or intimidate others?",
        "झगड़े शुरू करना, या दूसरों को बुलिंग, धमकी या भयभीत करना?"),
      q("P1d", "Deliberately destroy things or start fires?", "जानबूझकर चीज़ें नष्ट करना या आग लगाना?"),
      q("P1e", "Deliberately hurt animals or people?", "जानबूझकर पशुओं या लोगों को कष्ट पहुँचाना?"),
      q("P1f", "Force someone into sexual activity?", "किसी को यौन क्रिया हेतु विवश करना?")],
  "p1Gate": {"rule": "IF <2 of P1 answers Yes -> SKIP ALL THE P2 QUESTIONS, GO TO THE DIAGNOSTIC BOX AND CIRCLE NO.",
             "text": {"en": "Are 2 or more P1 answers coded Yes?", "hi": "क्या P1 के 2 या अधिक उत्तर 'हाँ' कोडित हैं?"}},
  "p2Note": {"en": "Do not code Yes to the behaviors below if they are exclusively politically or religiously motivated.",
             "hi": "निम्न व्यवहारों पर 'हाँ' कोड न करें यदि वे अनन्य रूप से राजनीतिक या धार्मिक प्रेरित हैं।"},
  "p2Intro": {"en": "Since you were 15 years old, have you:", "hi": "15 वर्ष की आयु के बाद से, क्या आप:"},
  "p2": [
      q("P2a", "Done things that are illegal or would be grounds to get arrested, even if you didn't get caught (for example destroying property, shoplifting, stealing, selling drugs, or committing a felony)?",
        "ऐसे कार्य किए जो अवैध हैं या गिरफ़्तारी का आधार बन सकते, चाहे पकड़े गए या नहीं (जैसे संपत्ति नष्ट, दुकान-चोरी, चोरी, दवा-बेचना, गंभीर अपराध)?"),
      q("P2b", "Often lied or 'conned' other people to get money or pleasure, or lied just for fun?",
        "धन/सुख हेतु बार-बार झूठ बोला या लोगों को ठगा, या केवल मनोरंजन हेतु झूठ बोला?"),
      q("P2c", "Been impulsive and didn't care about planning ahead?", "अववेगी रहे और पूर्व-योजना की चिंता नहीं की?"),
      q("P2d", "Been in physical fights repeatedly or assaulted others (including physical fights with your spouse or children)?",
        "बार-बार शारीरिक झगड़े या दूसरों पर हमला (पत्नी/संतान से शारीरिक झगड़े सहित)?"),
      q("P2e", "Exposed others or yourself to danger without caring?", "बेपरवाही से दूसरों/स्वयं को खतरे में डाला?"),
      q("P2f", "Repeatedly behaved in a way that others would consider irresponsible, like failing to pay for things you owed, deliberately being impulsive or deliberately not working to support yourself?",
        "बार-बार ऐसी व्यवहार जो दूसरे लापरवाही मानें — जैसे उधार चुकाना नहीं, जानबूझकर अववेगता, या स्वयं को पोषण हेतु काम न करना?"),
      q("P2g", "Felt no guilt after hurting, mistreating, lying to, or stealing from others, or after damaging property?",
        "दूसरों को कष्ट/दुरुपयोग/झूठ/चोरी के बाद या संपत्ति नष्ट करने के बाद कोई अपराधबोध न हुआ?")],
  "p2Gate": {"rule": "IF <3 of P2 answers Yes -> Antisocial Personality Disorder NO.",
             "text": {"en": "Are 3 or more P2 questions coded Yes?", "hi": "क्या P2 के 3 या अधिक प्रश्न 'हाँ' कोडित हैं?"}},
  "diagnosticBoxes": [
    {"id": "P_diag", "label": {"en": "Antisocial Personality Disorder — Lifetime", "hi": "प्रतिसामाजिक व्यक्तित्व विकार — जीवनभर"},
     "rule": ">=2 of P1a-P1f Yes AND >=3 of P2a-P2g Yes (behaviors not exclusively politically or religiously motivated).",
     "flags": ["LIFETIME"], "disordersOnPositive": ["antisocial_personality_disorder"]}]}

# ---------------------------------------------------------------------------
# Additional optional interview assessments (pages 36-37 of the MINI
# user-scripted version):
#   A - Cross-Cutting Measures: severity of symptom (0-10 clinician rating
#       scale across 13 symptom domains)
#   B - Disability / Functional Impairment: severity of disability (0-10
#       clinician rating scale across 12 functioning domains)
# These are self-contained rating tables; they add no branching logic and do
# not feed any diagnostic box.
# ---------------------------------------------------------------------------

ccSymptoms = [
    ("CCS1", "Depression", "अवसाद"),
    ("CCS2", "Anger", "क्रोध"),
    ("CCS3", "Mania (feeling up or high or hyper or full of energy with racing thoughts)",
     "मैैनिया (उत्फुल्ल/हाई/अति-सक्रिय, दौड़ते विचारों के साथ)"),
    ("CCS4", "Anxiety", "आतंक/चिंता"),
    ("CCS5", "Physical (somatic) symptoms", "शारीरिक (देहज) लक्षण"),
    ("CCS6", "Suicidal thoughts, impulses, plans, intent, (ANY thoughts of killing yourself), or any preparations to kill yourself or ANY attempt to kill yourself",
     "आत्मघाती विचार, प्रेरणाएँ, योजनाएँ, अभिप्राय (स्वयं को मारने का कोई भी विचार), या आत्महत्या की कोई तैयारी अथवा कोई प्रयास"),
    ("CCS7", "Hearing sounds or voices others can't hear or fearing someone can hear or read your thoughts or believing things others don't accept as true e.g. that people are spying on you or plotting against you or talking about you (Psychosis)",
     "ऐसी ध्वनियाँ/आवाज़ें सुनना जो अन्य नहीं सुन सकते, भय कि कोई आपके विचार सुन/पढ़ सकता है, या ऐसी बातें मानना जिन्हें अन्य सत्य नहीं मानते — जैसे लोग आपकी जासूसी/साज़िश कर रहे हैं या आपके बारे में बात करते हैं (मनर्विकार)"),
    ("CCS8", "Sleep problems", "नींद की समस्याएँ"),
    ("CCS9", "Memory problems", "स्मृति समस्याएँ"),
    ("CCS10", "Repetitive or obsessive thoughts or compulsive behaviors",
     "पुनरावृत्त या विचारग्रस्त (obsessive) विचार या विवशतापूर्ण (compulsive) व्यवहार"),
    ("CCS11", "Feeling things around you are strange, unreal, detached or unfamiliar, or feeling outside or detached from part or all of your body (Dissociation)",
     "आसपास की चीज़ें अजीब/अवास्तविक/परिचित-नहीं लगना, या शरीर के कुछ/सभी भाग से विलग/बाहर महसूस करना (वियोजन/Dissociation)"),
    ("CCS12", "Ability to function at work, at home, in your life, or in your relationships",
     "कार्य, घर, जीवन या संबंधों में कार्य करने की क्षमता"),
    ("CCS13", "Overusing alcohol or drugs", "शराब या दवाओं का अत्यधिक सेवन"),
]

crossCuttingMeasures = {
  "id": "OPT-A",
  "optionalAssessment": True,
  "name": {"en": "Additional Optional Assessment A — Cross-Cutting Measures: Severity of Symptom",
           "hi": "अतिरिक्त वैकल्पिक मूल्यांकन A — क्रॉस-कटिंग माप: लक्षणों की तीव्रता"},
  "intro": {"en": "Use this scale to rate the severity of your symptom in the score column in the table below: Assessment of Symptoms That Cut Across Disorders.",
            "hi": "इस पैमाने का उपयोग नीचे दी गई तालिका के स्कोर कॉलम में अपने लक्षण की तीव्रता रेट करने हेतु करें: विकारों-पार लक्षणों का मूल्यांकन।"},
  "tableHeading": {"en": "Symptom Name / Score", "hi": "लक्षण का नाम / स्कोर"},
  "items": [{"id": sid, "text": {"en": sen, "hi": shi}} for sid, sen, shi in ccSymptoms],
  "ratingScale": {"min": 0, "max": 10, "type": "clinician_rating",
                  "anchors": [{"v": 0, "label": {"en": "Not present", "hi": "उपस्थित नहीं"}},
                              {"v": 1, "label": {"en": "Mild", "hi": "हल्का"}},
                              {"v": 3, "label": {"en": "Moderate", "hi": "मध्यम"}},
                              {"v": 6, "label": {"en": "Severe", "hi": "गंभीर"}},
                              {"v": 10, "label": {"en": "Extreme", "hi": "अत्यधिक"}}]},
  "note": {"en": "Clinician-rated 0-10 severity for each cross-cutting symptom domain; independent of the Module A-P branching logic and does not gate any diagnostic box.",
           "hi": "प्रत्येक क्रॉस-कटिंग लक्षण-क्षेत्र हेतु चिकित्सक-रेटित 0-10 तीव्रता; माड्यूल A-P की शाखा-विभाजन पद्धति से स्वतंत्र तथा किसी निदान-बक्से को नियंत्रित नहीं करता।"}}

disabilityItems = [
    ("DIS1", "Work or school work", "कार्य या विद्यालय-कार्य"),
    ("DIS2", "Social life or leisure activities (like hobbies or things you do for enjoyment)",
     "सामाजिक जीवन या अवकाश गतिविधियाँ (शौक या मनोरंजन हेतु की जाने वाली चीज़ें)"),
    ("DIS3", "Family life and/or home responsibilities", "पारिवारिक जीवन और/या घरेलू ज़िम्मेदारियाँ"),
    ("DIS4", "Ability to get along with people", "लोगों के साथ मिलकर चलने की क्षमता"),
    ("DIS5", "Personal and social relationships", "व्यक्तिगत एवं सामाजिक संबंध"),
    ("DIS6", "Ability to understand and to communicate with others", "अन्य को समझने एवं उनसे संवाद करने की क्षमता"),
    ("DIS7", "Ability to take care of yourself (washing, showering, bathing, dressing properly, brushing teeth, laundry, combing/brushing hair, eating regularly)",
     "स्वयं की देखभाल की क्षमता (धुलाई, स्नान, उचित वस्त्र, दाँत साफ करना, कपड़े धोना, बाल सुलझाना, नियमित भोजन)"),
    ("DIS8", "Made you disruptive or aggressive towards others", "आपको दूसरों प्रति अव्यवस्थाकारी या आक्रामक बनाना"),
    ("DIS9", "Financially (ability to manage your money)", "आर्थिक (धन प्रबंधन की क्षमता)"),
    ("DIS10", "Ability to get around physically", "भौतिक रूप से इधर-उधर चलने की क्षमता"),
    ("DIS11", "Spiritual or religious life", "आध्यात्मिक या धार्मिक जीवन"),
    ("DIS12", "How much did your condition have an impact on other people in your family?",
     "आपकी स्थिति का आपके परिवार के अन्य लोगों पर कितना प्रभाव पड़ा?"),
]

disabilityImpairment = {
  "id": "OPT-B",
  "optionalAssessment": True,
  "name": {"en": "Additional Optional Assessment B — Disability / Functional Impairment: Severity of Disability / Impairment",
           "hi": "अतिरिक्त वैकल्पिक मूल्यांकन B — अक्षमता/कार्यात्मक हानि: अक्षमता/हानि की तीव्रता"},
  "intro": {"en": "Use this scale to rate in the score column of the table below, how much your symptoms have disrupted your ability to function in the following areas of your life: Assessment of Impairment of Functioning/Disability.",
            "hi": "इस पैमाने का उपयोग नीचे दी गई तालिका के स्कोर कॉलम में रेट करने हेतु करें कि आपके लक्षणों ने आपके जीवन के निम्न क्षेत्रों में कार्य करने की क्षमता को कितना बाधित किया है: कार्यात्मक हानि/अक्षमता का मूल्यांकन।"},
  "tableHeading": {"en": "Domain Name / Score", "hi": "क्षेत्र का नाम / स्कोर"},
  "items": [{"id": did, "text": {"en": den, "hi": dhi}} for did, den, dhi in disabilityItems],
  "ratingScale": {"min": 0, "max": 10, "type": "clinician_rating",
                  "anchors": [{"v": 0, "label": {"en": "Not present", "hi": "उपस्थित नहीं"}},
                              {"v": 1, "label": {"en": "Mild", "hi": "हल्का"}},
                              {"v": 3, "label": {"en": "Moderate", "hi": "मध्यम"}},
                              {"v": 6, "label": {"en": "Severe", "hi": "गंभीर"}},
                              {"v": 10, "label": {"en": "Extreme", "hi": "अत्यधिक"}}]},
  "note": {"en": "Clinician-rated 0-10 disruption for each functional domain; independent of the Module A-P branching logic and does not gate any diagnostic box.",
           "hi": "प्रत्येक कार्यात्मक क्षेत्र हेतु चिकित्सक-रेटित 0-10 बाधा; माड्यूल A-P की शाखा-विभाजन पद्धति से स्वतंत्र तथा किसी निदान-बक्से को नियंत्रित नहीं करता।"}}

# ---------------------------------------------------------------------------
# Additional optional interview assessment: Mood Disorders Diagnostic Algorithm
# (consult Modules A - Major Depressive Episode, C - (Hypo)manic Episode,
#  K - Psychotic Disorders). Derived boxes; no new interview items.
# ---------------------------------------------------------------------------
moodAlgorithm = {
  "id": "ALG-MOOD",
  "optionalAssessment": True,
  "name": {"en": "Mood Disorders: Diagnostic Algorithm",
            "hi": "मूड विकार: निदान एल्गोरिद्म"},
  "consultModules": ["A - Major Depressive Episode", "C - (Hypo)manic Episode", "K - Psychotic Disorders"],
  "steps": [
    {"id": "1a", "text": {"en": "Module K: Is K11b coded Yes?",
                           "hi": "माड्यूल K: क्या K11b 'हाँ' कोडित है?"}},
    {"id": "1b", "text": {"en": "Module K: Is K12a coded Yes?",
                           "hi": "माड्यूल K: क्या K12a 'हाँ' कोडित है?"}},
    {"id": "2a", "perTimeframe": ["current", "past"],
     "text": {"en": "Circle Yes if a delusional idea is identified in A3e or in any psychotic feature in K1 through K7.",
               "hi": "'हाँ' घेरें यदि A3e में या K1–K7 की किसी मनर्विकारी विशेषता में भ्रामक विचार चिह्नित हो।"}},
    {"id": "2b", "perTimeframe": ["current", "past"],
     "text": {"en": "Circle Yes if a delusional idea is identified in C3a or in any psychotic feature in K1 through K7.",
               "hi": "'हाँ' घेरें यदि C3a में या K1–K7 की किसी मनर्विकारी विशेषता में भ्रामक विचार चिह्नित हो।"}}],
  "specifierNotes": [
    {"en": "Mixed features: hypo/manic with mixed features = hypo/manic + at least 3 symptoms from A3; depressed with mixed features = major depressive episode + at least 3 symptoms from C3.",
     "hi": "मिश्र-लक्षण: हाइपो/मैैनिक मिश्र-लक्षणों सहित = हाइपो/मैैनिक + A3 के कम से कम 3 लक्षण; अवसादित मिश्र-लक्षणों सहित = प्रमुख अवसादी एपिसोड + C3 के कम से कम 3 लक्षण।"},
    {"en": "With anxious distress = with at least 3 symptoms from N3.",
     "hi": "आतंक-पीड़ा सहित = N3 के कम से कम 3 लक्षण।"}],
  "diagnosticBoxes": [
    {"id": "ALG_MDD", "label": {"en": "Major Depressive Disorder — Current / Past",
                                 "hi": "प्रमुख अवसादी विकार — वर्तमान / अतीत"},
     "rule": "MAJOR DEPRESSIVE EPISODE coded Yes (current or past) AND MANIC EPISODE No (current and past) AND HYPOMANIC EPISODE No (current and past) AND organic cause ruled out (O2 summary). Specify if the depressive episode is current or past or both. With psychotic features, CURRENT: if 1b OR 2a (current) = Yes; PAST: if 1a OR 2a (past) = Yes.",
     "flags": ["MDD CURRENT", "MDD PAST", "WITH PSYCHOTIC FEATURES CURRENT", "WITH PSYCHOTIC FEATURES PAST"],
     "disordersOnPositive": ["depression_mdd"]},
    {"id": "ALG_BPI", "label": {"en": "Bipolar I Disorder — Current / Past",
                                 "hi": "बाइपोलर I विकार — वर्तमान / अतीत"},
     "rule": "MANIC EPISODE coded Yes (current or past) AND organic cause ruled out (O2 summary). Single manic episode: if manic episode (current or past) Yes AND major depressive episode (current and past) No. With psychotic features, CURRENT: if 1b OR 2a (current) OR 2b (current) = Yes; PAST: if 1a OR 2a (past) OR 2b (past) = Yes. Specify most recent episode (manic/depressed/hypomanic, mutually exclusive) and whether it had mixed, anxious or psychotic features, and severity (mild/moderate/severe).",
     "flags": ["BIPOLAR I CURRENT", "BIPOLAR I PAST", "SINGLE MANIC EPISODE", "WITH PSYCHOTIC FEATURES CURRENT", "WITH PSYCHOTIC FEATURES PAST",
               "MOST RECENT: MANIC", "MOST RECENT: DEPRESSED", "MOST RECENT: HYPOMANIC",
               "MOST RECENT WITH MIXED FEATURES", "MOST RECENT WITH ANXIOUS DISTRESS",
               "MOST RECENT MILD", "MOST RECENT MODERATE", "MOST RECENT SEVERE"],
     "disordersOnPositive": ["bipolar_i_disorder"]},
    {"id": "ALG_BPII", "label": {"en": "Bipolar II Disorder — Current / Past",
                                  "hi": "बाइपोलर II विकार — वर्तमान / अतीत"},
     "rule": "MAJOR DEPRESSIVE EPISODE Yes (current or past) AND HYPOMANIC EPISODE Yes (current or past) AND MANIC EPISODE No (current and past) AND organic cause ruled out (O2 summary). Specify if bipolar disorder is current or past or both; most recent mood episode hypomanic or depressed (mutually exclusive); most recent episode with mixed/anxious/psychotic features; severity mild/moderate/severe.",
     "flags": ["BIPOLAR II CURRENT", "BIPOLAR II PAST",
               "MOST RECENT: HYPOMANIC", "MOST RECENT: DEPRESSED",
               "MOST RECENT WITH MIXED FEATURES", "MOST RECENT WITH ANXIOUS DISTRESS",
               "MOST RECENT MILD", "MOST RECENT MODERATE", "MOST RECENT SEVERE"],
     "disordersOnPositive": ["bipolar_ii_disorder"]},
    {"id": "ALG_OSBR", "label": {"en": "Other Specified Bipolar and Related Disorder — Current / Past",
                                  "hi": "अन्य निर्दिष्ट बाइपोलर एवं संबंधित विकार — वर्तमान / अतीत"},
     "rule": "Either: MAJOR DEPRESSIVE EPISODE No (current and past) AND MANIC EPISODE No (current and past) AND C4b Yes for the appropriate timeframe AND C8b Yes; OR: MANIC EPISODE No (current and past) AND HYPOMANIC EPISODE No (current and past) AND C4a Yes for the appropriate timeframe AND C8c Yes. Specify if current or past or both.",
     "flags": ["CURRENT", "PAST"], "disordersOnPositive": ["other_specified_bipolar"]}],
  "note": {"en": "Additional optional interview assessments (pages 36 & 37 of the MINI user-scripted version): this algorithm derives its diagnostic boxes from Modules A, C and K plus the O2 summary; it adds no new interview questions.",
            "hi": "अतिरिक्त वैकल्पिक साक्षात्कार मूल्यांकन (MINI उपयोगकर्ता-स्क्रिप्टेड संस्करण के पृष्ठ 36 एवं 37): यह एल्गोरिद्म माड्यूल A, C, K तथा O2 सारांश से निदान-बक्से व्युत्पन्न करता है; कोई नया साक्षात्कार-प्रश्न नहीं जोड़ता।"}}

with open(os.path.join(HERE, "modB.json"), encoding="utf-8") as f:
    modB = json.load(f)

mini = {
  "id": "mini",
  "name": {"en": "Mini International Neuropsychiatric Interview (MINI), English Version 7.0.2, for DSM-5",
           "hi": "मिनी इंटरनैशनल न्यूरोसाइकिएट्रिक इंटरव्यू (MINI), अंग्रेज़ी संस्करण 7.0.2, DSM-5 हेतु"},
  "type": "mini_branching",
  "source": {"framework": "DSM-5", "version": "7.0.2", "date": "August 8, 2016",
             "modulesImplemented": ["A - Major Depressive Episode", "B - Suicidality", "C - Manic and Hypomanic Episodes",
                                    "D - Panic Disorder", "E - Agoraphobia", "F - Social Anxiety Disorder",
                                    "G - Obsessive-Compulsive Disorder", "H - Posttraumatic Stress Disorder",
                                    "I - Alcohol Use Disorder", "J - Substance Use Disorder (Non-alcohol)",
                                    "K - Psychotic Disorders and Mood Disorder With Psychotic Features",
                                    "L - Anorexia Nervosa", "M - Bulimia Nervosa", "MB - Binge Eating Disorder",
                                    "N - Generalized Anxiety Disorder",
                                    "O - Rule Out Medical, Organic or Drug Causes For All Disorders",
                                    "P - Antisocial Personality Disorder",
                                    "Additional optional interview assessments (pages 36-37): A - Cross-Cutting Measures (Severity of Symptom), B - Disability/Functional Impairment (Severity of Disability/Impairment)",
                                    "Mood Disorders Diagnostic Algorithm"],
             "note": {"en": "Structured interview modules adapted from the MINI 7.0.2 user-scripted version. This web implementation captures the screening logic only; it is not a substitute for trained interviewer administration. The organic-cause exclusion (Module O) is captured as an explicit clinician-rated No/Yes/Uncertain summary that gates every current-disorder diagnostic box.",
                      "hi": "MINI 7.0.2 के उपयोगकर्ता-स्क्रिप्टेड संस्करण से अनुकूलित संरचित साक्षात्कार माड्यूल। यह वेब कार्यान्वयन केवल स्क्रीनिंग तर्क ग्रहण करता है; प्रशिक्षित इंटरव्यूटर के प्रशासन का विकल्प नहीं है। जैविक-कारण बहिर्गमन (माड्यूल O) को चिकित्सक-रेटित नहीं/हाँ/अनिश्चित सारांश के रूप में ग्रहण किया गया है जो प्रत्येक वर्तमान-विकार निदान-बक्से को नियंत्रित करता है।"}},
  "responseScale": [{"v": 0, "label": YN_NO}, {"v": 1, "label": YN_YES}],
  "directions": {"en": "These questions follow the MINI 7.0.2 branching logic (Modules A-P plus the additional optional interview assessments: Cross-Cutting Measures, Disability/Functional Impairment, and the Mood Disorders Diagnostic Algorithm: Major Depressive Episode; Suicidality; Manic/Hypomanic Episodes; Panic Disorder; Agoraphobia; Social Anxiety; Obsessive-Compulsive Disorder; Posttraumatic Stress Disorder; Alcohol Use Disorder; Substance Use Disorder; Psychotic Disorders and Mood Disorder With Psychotic Features; Anorexia Nervosa; Bulimia Nervosa; Binge Eating Disorder; Generalized Anxiety Disorder; Rule Out Medical/Organic/Drug Causes; Antisocial Personality Disorder). Answer honestly; sections that do not apply are skipped automatically.",
                 "hi": "ये प्रश्न MINI 7.0.2 की शाखा-विभाजन पद्धति का पालन करते हैं (माड्यूल A-P एवं अतिरिक्त वैकल्पिक मूल्यांकन: क्रॉस-कटिंग माप, अक्षमता/कार्यात्मक हानि, तथा मूड-विकार निदान-एल्गोरिद्म: प्रमुख अवसादी एपिसोड; आत्मघातिता; मैैनिक/हाइपोमैैनिक एपिसोड; पैैनिक विकार; एगोराफोबिया; सामाजिक आतंक; O.C.D.; PTSD; मद्य-सेवन विकार; पदार्थ-सेवन विकार; मनर्विकार विकार एवं मनर्विकारी लक्षणों सहित मूड विकार; एनोरेक्सिया नर्वोसा; बुलिमिया नर्वोसा; बिंज-ईटिंग विकार; सामान्यीकृत चिंता विकार; चिकित्सकीय/जैविक/दवा-कारणों का बहिर्गमन; प्रतिसामाजिक व्यक्तित्व विकार)। ईमानदारी से उत्तर दें; लागू न होने वाले भाग स्वतः छोड़े जाएँगे।"},
  "modules": [modA, modB, modC, modD, modE, modF, modG, modH, modI, modJ, modK,
              modL, modM, modMB, modN, modO, modP,
              crossCuttingMeasures, disabilityImpairment, moodAlgorithm]
}

out = "/tmp/mini.json"
with open(out, "w", encoding="utf-8") as f:
    json.dump(mini, f, ensure_ascii=False, indent=2)
json.load(open(out))
print("WROTE", out, "| modules:", [m["id"] for m in mini["modules"]], "| JSON VALID")
