#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_dissociation.py — Integrate the two dissociation instruments into data.json:

  1. MID-60 — Multidimensional Inventory of Dissociation, 60-item short form
     (Kate, Jamieson, Dorahy & Middleton, 2021, J Trauma Dissociation 22(3) 265-287).
     60 frequency items rated 0-10 ("never happens" ... "always happening"), taken
     when NOT under the influence of alcohol or drugs. Total mean = average of all
     60 responses x 10 -> a 0-100 index with published score ranges, plus 12 named
     subscales each carrying its own clinical cutoff.

  2. DES-II — Dissociative Experiences Scale II (Carlson & Putnam).
     28 items, each answered by circling one of eleven 10% steps (0-100);
     total score = mean of the 28 item percentages. The published clinical
     comparison point is a mean >= 30.

Both are self-report dimensional measures reached through the new `dissociation`
domain using the existing screen-in routing (`auto:dissociationtable`). They flag
the dissociative-disorder categories for the structured interview; they do not by
themselves make a diagnosis. Item stems are transcribed from the user-supplied
packet; where the scan is garbled the canonical printed wording is used and the
deviation recorded in `sourceNotes`. Hindi labels are clinician-review aids.

Run:  python3 scripts/build_dissociation.py            (writes data.json in place)
      python3 scripts/build_dissociation.py --check    (validate only, no write)
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'data.json')


def en_hi(en, hi):
    return {"en": en, "hi": hi}


# ---------------------------------------------------------------------------
# Response option sets
# ---------------------------------------------------------------------------
# MID-60: 0-10 frequency rating exactly as printed on the form.
MID_OPTS = [{"v": v, "label": en_hi(str(v), str(v))} for v in range(0, 11)]
MID_ANCHORS = [en_hi("0 Never happens to you", "0 आपको कभी नहीं होता"),
               en_hi("10 Always happening to you", "10 सदैव हो रहा है")]

# DES-II: eleven 10% steps, 0% (Never) ... 100% (Always).
DES_OPTS = [{"v": v * 10,
             "label": en_hi(str(v * 10) + "%", str(v * 10) + "%")} for v in range(0, 11)]

MID_SAFETY_ITEMS = {
    22: en_hi("Persecutory internal voice urging self-harm — complete a suicide-risk assessment.",
              "उत्पीड़नकारी भीतरी आवाज़ जो स्व-क्षति को प्रेरित करे — आत्महत्या-जोखिम मूल्यांकन पूर्ण करें।"),
    37: en_hi("Degradating internal voice — assess for persecutory parts and mood risk.",
              "अपमानजनक भीतरी आवाज़ — उत्पीड़नकारी अंश एवं मूड-जोखिम का आकलन करें।"),
    44: en_hi("Internal voice wanting the patient to die — HIGH RISK: complete a suicide-risk assessment.",
              "भीतरी आवाज़ जो रोगी के मरने को कहे — उच्च जोखिम: आत्महत्या-जोखिम मूल्यांकन पूर्ण करें।"),
    56: en_hi("Critical internal voice — assess internal family conflict and mood risk.",
              "आलोचनात्मक भीतरी आवाज़ — आंतरिक संघर्ष एवं मूड-जोखिम का आकलन करें।"),
    58: en_hi("Waking with pills or a blade in hand — evidence of amnestic self-harm; urgent risk review.",
              "हाथ में गोलियाँ या ब्लेड लेकर होश में आना — क्षतिस्मृतिक स्व-क्षति का प्रमाण; तत्काल जोखिम-समीक्षा।"),
}

YESNO = [{"v": 0, "label": en_hi("No", "नहीं")},
         {"v": 1, "label": en_hi("Yes", "हाँ")}]

DISS_DISORDERS = ["dissociative_identity_disorder",
                  "other_specified_dissociative_disorder",
                  "unspecified_dissociative_disorder"]

# ---------------------------------------------------------------------------
# MID-60 item stems (printed order 1..60). English from the supplied packet,
# normalised where the OCR interleaved characters; Hindi is a review aid.
# ---------------------------------------------------------------------------
M = [
    ("Forgetting what you did earlier in the day.", "दिन में पहले क्या किया, उसे भूल जाना।"),
    ("Having an emotion (e.g., fear, sadness, anger, happiness) that doesn't feel like it is \"yours\".",
     "कोई भावना (भय, दुख, क्रोध, सुख) जो आपकी \"अपनी\" नहीं लगती।"),
    ("Hearing the voice of a child in your head.", "सिर के भीतर एक बच्चे की आवाज़ सुनाई देना।"),
    ("Reliving a traumatic event so vividly that you totally lose contact with where you actually are (that is, you think that you are \"back there and then\").",
     "आघातजनक घटना इतनी जीवंतता से दोबारा जीना कि आप वास्तव में कहाँ हैं, इसका संपर्क पूरी तरह खो जाता है (आपको लगता है आप \"वहाँ और तब\" हैं)।"),
    ("Having difficulty swallowing (for no known medical reason).", "निगलने में कठिनाई (कोई ज्ञात चिकित्सीय कारण नहीं)।"),
    ("Having trance-like episodes where you stare off into space and lose awareness of what is going on around you.",
     "ट्रांस-सदृश अवस्थाएँ जिनमें आप शून्य में टकटकी लगाकर चारों ओर की घटनाओं की जागरूकता खो देते हैं।"),
    ("Being told of things that you had recently done, but with absolutely no memory of having done those things.",
     "दूसरों द्वारा बताई गई हाल की की गई बातों का बिल्कुल भी स्मरण न होना।"),
    ("Not remembering what you ate at your last meal - or even whether you ate.",
     "पिछले भोजन में क्या खाया - या यह भी कि भोजन किया अथवा नहीं, याद न होना।"),
    ("Things around you feeling unreal.", "चारों ओर की वस्तुएँ अवास्तविक लगना।"),
    ("Not being able to see for a while (as if you are blind) for no known medical reason.",
     "कुछ समय के लिए देख न पाना (मानो अंधा हों), कोई ज्ञात चिकित्सीय कारण नहीं।"),
    ("Feeling very detached from your behavior as you \"go through the motions\" of daily life.",
     "दैनिक जीवन के \"कार्य\" करते समय अपने व्यवहार से अत्यंत विलग महसूस करना।"),
    ("Feeling uncertain about who you really are.", "आप वास्तव में कौन हैं, इसके बारे में अनिश्चितता महसूस करना।"),
    ("Feeling less interested in things than you used to be, or finding that you don't enjoy activities or hobbies the way you once did.",
     "पहले की तुलना में चीज़ों में कम रुचि होना, या गतिविधियाँ/शौक पहले जैसे आनंद न देना।"),
    ("Being paralyzed or unable to move (for no known medical reason).", "लकवाग्रस्त होना या हिल न पाना (कोई ज्ञात चिकित्सीय कारण नहीं)।"),
    ("Being so bothered by flashbacks that it was hard to get out of bed and face the day.",
     "फ्लैशबैक इतने कष्टदायी कि बिस्तर से उठकर दिन का सामना करना कठिन हो।"),
    ("Not remembering large parts of your childhood after age 5.", "पाँच वर्ष के बाद के बचपन के बड़े हिस्से याद न होना।"),
    ("Feeling disconnected from everything around you.", "चारों ओर की हर वस्तु से कटा हुआ महसूस करना।"),
    ("Not being able to hear for a while (as if you are deaf) for no known medical reason.",
     "कुछ समय के लिए सुन न पाना (मानो बहरा हों), कोई ज्ञात चिकित्सीय कारण नहीं।"),
    ("Feeling that pieces of your past are missing.", "अतीत के कुछ टुकड़े गुम लगना।"),
    ("Immediately forgetting what other people tell you.", "दूसरे जो बताते हैं, तुरंत भूल जाना।"),
    ("Having difficulty walking (for no known medical reason).", "चलने में कठिनाई (कोई ज्ञात चिकित्सीय कारण नहीं)।"),
    ("Hearing a voice in your head that wants you to hurt yourself.", "सिर के भीतर ऐसी आवाज़ जो आपको स्वयं को क्षति पहुँचाने को कहे।"),
    ("Feeling very confused about who you really are.", "आप वास्तव में कौन हैं, इसे लेकर अत्यंत विभ्रम महसूस करना।"),
    ("Feeling that important things happened to you earlier in your life, but you cannot remember them.",
     "लगता है जीवन के पूर्व में महत्वपूर्ण घटनाएँ घटीं, पर उन्हें याद नहीं कर सकते।"),
    ("Feeling as if you were looking at the world through a fog so that people and objects felt far away or unclear.",
     "मानो कोहरे के पार से संसार देख रहे हों; लोग एवं वस्तुएँ दूर या अस्पष्ट लगें।"),
    ("Having seizures for which your doctor can find no reason.", "मिर्गी-जैसे दौरे जिनका कारण चिकित्सक नहीं पा सकतें।"),
    ("Going into trance so much (or for so long) that it interferes with your daily activities and responsibilities.",
     "इतनी बार/इतनी देर ट्रांस में जाना कि दैनिक कार्य एवं ज़िम्मेदारियाँ प्रभावित हों।"),
    ("Words just flowing from your mouth as if they were not in your control.",
     "शब्द मुँह से ऐसे बहते जाना मानो वे आपके नियंत्रण में न हों।"),
    ("Feeling that there are large gaps in your memory.", "स्मृति में बड़े-बड़े अंतराल दिखना।"),
    ("Going into trance for hours.", "घंटों तक ट्रांस में रहना।"),
    ("Bad memories coming into your mind and you can't get rid of them.", "बुरी यादें मन में आना और उन्हें हटा न पाना।"),
    ("Drifting into trance without even realizing that it is happening.", "ट्रांस में चले जाना, यह एहसास भी हुए बिना कि वह हो रहा है।"),
    ("Words come out of your mouth, but you didn't say them; you don't know where those words came from.",
     "मुँह से शब्द निकलना पर आपने वे नहीं कहे; वे कहाँ से आए, पता नहीं।"),
    ("Being able to remember very little of your past.", "अतीत का बहुत थोड़ा ही याद रहना।"),
    ("When you are angry, doing or saying things that you don't remember (after you calm down).",
     "क्रोध में ऐसे कार्य/वचन करना जो शांत होने के बाद याद न हो।"),
    ("Feeling that you have multiple personalities.", "ऐसा लगना कि आपके भीतर अनेक व्यक्तित्व हैं।"),
    ("Hearing a voice in your head that calls you names (e.g., wimp, stupid, whore, slut, bitch, etc.).",
     "सिर के भीतर ऐसी आवाज़ जो आपको गालियाँ/नाम देती है (कायर, मूर्ख आदि)।"),
    ("Poor memory causing serious difficulty for you.", "खराब स्मृति से आपको गंभीर कठिनाई होना।"),
    ("Having other people (or parts) inside you who have their own names.", "आपके भीतर अन्य व्यक्ति/अंश जिनके अपने नाम हैं।"),
    ("Re-living a part, such as a past trauma, so vividly that you temporarily lose touch with the present.",
     "किसी अंश (जैसे पूर्व आघात) को इतनी जीवंतता से दोबारा जीना कि वर्तमान का संपर्क क्षणिक टूट जाए।"),
    ("Going into trance several days in a row.", "लगातार कई दिनों तक ट्रांस में जाना।"),
    ("Suddenly finding yourself somewhere odd at home (e.g., inside the closet, under a bed, curled up on the floor, etc.) with no knowledge of how you got there.",
     "अचानक घर में कोई अजीब स्थान (अलमारी के भीतर, बिस्तर के नीचे, फर्श पर कुड़कर) पर पाए जाना, यह जाने बिना कि वहाँ कैसे पहुँचे।"),
    ("Discovering that you have changed your appearance (e.g., cut your hair, changed your hairstyle, changed what you are wearing, put on cosmetics, etc.) with no memory of having done so.",
     "पता चलना कि आपने रूप बदल लिया (बाल काटना, हेयरस्टाइल, वस्त्र, मेकअप आदि) पर ऐसा करने का स्मरण नहीं।"),
    ("Being bothered or upset by how much you forget.", "कितना कुछ भूल जाते हैं, इससे परेशान या व्याकुल होना।"),
    ("Hearing a voice in your head that wants you to die.", "सिर के भीतर ऐसी आवाज़ जो आपको मरने को कहे।"),
    ("Feeling as if there is something inside you that takes control of your behavior and speech.",
     "ऐसा लगना कि आपके भीतर कुछ है जो आपके व्यवहार और वाणी पर नियंत्रण ले लेता है।"),
    ("Totally forgetting how to do something that you know very well how to do (e.g., how to drive, how to read, how to use the computer, how to play the piano, etc.).",
     "किसी कार्य को करना पूर्णतः भूल जाना जिसे आप बहुत अच्छी तरह करना जानते हैं (ड्राइविंग, पढ़ना, कंप्यूटर, पियानो आदि)।"),
    ("Suddenly finding yourself somewhere (e.g., at the beach, at work, in a nightclub, in your car, etc.) with no memory of how you got there.",
     "अचानक किसी स्थान पर (समुद्र तट, कार्यस्थल, नाइटक्लब, कार में) पाए जाना, वहाँ पहुँचने का स्मरण नहीं।"),
    ("Feeling that there is another person inside who can come out and speak if it wants.",
     "ऐसा लगना कि भीतर एक अन्य व्यक्ति है जो चाहे तो बाहर आकर बोल सकता है।"),
    ("\"Coming to\" and finding that you have done something you don't remember doing (e.g., smashed something, cut yourself, cleaned the whole house, etc.).",
     "\"होश में\" आने पर पता चलना कि कोई कार्य कर डाला जो याद नहीं (चीज़ तोड़ना, स्वयं को घायल करना, पूरा घर साफ करना आदि)।"),
    ("Having difficulty staying out of trance.", "ट्रांस से बाहर बने रहने में कठिनाई।"),
    ("Suddenly not knowing how to do your job.", "अचानक काम कैसे करना है, यह न जानना।"),
    ("Your body suddenly feeling as if it isn't really yours.", "अचानक शरीर ऐसा लगना जैसे वास्तव में आपका नहीं है।"),
    ("Being bothered by flashbacks for several days in a row.", "लगातार कई दिनों तक फ्लैशबैक से कष्ट होना।"),
    ("Being confused or puzzled by your emotions.", "अपनी भावनाओं को लेकर विभ्रम या हैरान होना।"),
    ("Hearing a voice in your head that tells you to \"shut up\".", "सिर के भीतर ऐसी आवाज़ जो कहती है \"चुप रहो\"।"),
    ("Having another part inside that has different memories, behaviors, and feelings than you do.",
     "भीतर एक अन्य अंश जिसकी स्मृतियाँ, व्यवहार एवं भावनाएँ आपसे भिन्न हैं।"),
    ("There were times when you \"woke up\" and found pills or a razor blade (or something else to hurt yourself with) in your hand.",
     "ऐसे अवसर जब \"होश में\" आने पर हाथ में गोलियाँ या रेज़र ब्लेड (या स्वयं को क्षति का अन्य साधन) मिला।"),
    ("Hearing a voice in your head that calls you no good, worthless, or a failure.",
     "सिर के भीतर ऐसी आवाज़ जो आपको बेकार, निरर्थक या असफल कहे।"),
    ("Having a very angry part that \"comes out\" and says and does things that you would never do or say.",
     "अत्यंत क्रोधित अंश का \"बाहर आकर\" वे कार्य/वचन करना जो आप कभी नहीं करते।"),
]

# ---------------------------------------------------------------------------
# MID-60 subscales, exactly as printed in the supplied score sheet.
# ---------------------------------------------------------------------------
MID_SUBSCALES = [
    ("did_amnesia_recent", en_hi("DID: Amnesia (for recent events)",
                                 "DID: क्षतिस्मृति (हाल की घटनाओं की)"),
     [42, 45, 48, 58], 10,
     en_hi("Sudden unexplained changes in appearance, finding yourself in odd places at home, "
           "finding yourself somewhere with no memory of how you got there, and waking with "
           "something dangerous in your hand.",
           "अचानक अपरिवर्तित रूप, घर में विचित्र स्थान पर पाए जाना, बिना स्मरण के किसी स्थान पर पहुँचना, "
           "और हाथ में हानिकारक वस्तु लेकर होश में आना।")),
    ("did_alt_awareness", en_hi("DID / OSDD-1: Subjective awareness of alter personalities and self-states",
                                "DID / OSDD-1: अंश-व्यक्तित्वों एवं स्व-अवस्थाओं का आंतरिक बोध"),
     [3, 36, 39, 49, 57], 20,
     en_hi("Hearing a child's voice internally, feeling that you have multiple personalities, "
           "named parts inside you, another person inside who could come out and speak, and a "
           "part with different memories, behaviours and feelings.",
           "भीतर बच्चे की आवाज़, अनेक व्यक्तित्वों का अनुभव, नाम वाले अंश, भीतर अन्य व्यक्ति जो बाहर आकर बोल सके, "
           "एवं भिन्न स्मृतियों/व्यवहार/भावनाओं वाला अंश।")),
    ("did_angry_intrusions", en_hi("DID / OSDD-1: Angry intrusions", "DID / OSDD-1: क्रोधित प्रवेश"),
     [28, 33, 35, 46, 60], 18,
     en_hi("Words flowing uncontrollably, words you did not say, angry behaviour you cannot "
           "remember afterwards, possession-like control of behaviour and speech, and an angry "
           "part that says and does things you never would.",
           "अनियंत्रित शब्द, आपके न कहे शब्द, क्रोध में किए कार्य जो बाद में याद नहीं, व्यवहार-वाणी पर नियंत्रण, "
           "एवं क्रोधित अंश जो आप कभी न करें सो करता है।")),
    ("did_persecutory_intrusions", en_hi("DID / OSDD-1: Persecutory intrusions", "DID / OSDD-1: उत्पीड़नकारी प्रवेश"),
     [22, 37, 44, 56, 59], 18,
     en_hi("Internal voices telling you to hurt yourself, calling you names, wanting you to die, "
           "telling you to \"shut up\", and calling you no good, worthless or a failure. "
           "These items are self-harm and suicide related - always follow them up.",
           "भीतर की आवाज़ें जो स्वयं को क्षति पहुँचाने को कहे, गालियाँ दें, मरने को कहे, \"चुप रहो\" कहे, "
           "तथा बेकार/असफल कहे। ये आइटम स्व-क्षति/आत्महत्या से जुड़े हैं — सदैव अनुवर्ती मूल्यांकन करें।")),
    ("drdepersonalisation", en_hi("Derealization / Depersonalization", "वास्तविकता-विचलन / स्व-विलगता"),
     [2, 7, 9, 13, 25, 47, 50, 53], 20,
     en_hi("Emotions that do not feel like yours, no memory of recent actions, things feeling "
           "unreal, reduced interest/enjoyment, the world seen through a fog, forgetting a well-"
           "learned skill, \"coming to\" after having done something, and your body not feeling yours.",
           "अपनी न लगने वाली भावनाएँ, हाल के कार्यों का स्मरण न होना, वस्तुओं का अवास्तविक लगना, रुचि/आनंद में हानि, "
           "कोहरे के पार संसार, सुगम कार्य की स्मृति-हानि, कुछ करने के बाद \"होश\" में आना, शरीर का अपना न लगना।")),
    ("amnesia_memory_distress", en_hi("Dissociative Amnesia: Distress about severe memory problems",
                                      "वियोजीय क्षतिस्मृति: गंभीर स्मृति-समस्याओं से कष्ट"),
     [1, 8, 20, 38, 43, 52], 30,
     en_hi("Forgetting what you did earlier in the day, not remembering your last meal, "
           "immediately forgetting what people tell you, poor memory causing serious difficulty, "
           "being upset by how much you forget, and suddenly not knowing how to do your job.",
           "दिन के पूर्व कार्य भूलना, पिछला भोजन याद न होना, लोगों की बात तुरंत भूलना, खराब स्मृति से गंभीर कठिनाई, "
           "भूलने की मात्रा से कष्ट, तथा अचानक कार्य विधि न जानना।")),
    ("amnesia_autobiographical", en_hi("Dissociative Amnesia: Loss of autobiographical memory",
                                       "वियोजीय क्षतिस्मृति: आत्मकथात्मक स्मृति की हानि"),
     [16, 19, 24, 29, 34], 34,
     en_hi("Not remembering large parts of childhood after age 5, feeling pieces of your past are "
           "missing, important earlier events you cannot recall, large gaps in memory, and "
           "remembering very little of your past.",
           "पाँच वर्ष के बाद बचपन के बड़े हिस्से याद न होना, अतीत के टुकड़े गुम लगना, पूर्व की महत्वपूर्ण घटनाओं का अभाव, "
           "स्मृति में बड़े अंतराल, तथा अतीत का अत्यल्प स्मरण।")),
    ("ptsd_flashbacks", en_hi("PTSD: Flashbacks", "PTSD: फ्लैशबैक"),
     [4, 15, 31, 40, 54], 16,
     en_hi("Reliving trauma with loss of contact with the present, flashbacks so distressing you "
           "cannot face the day, intrusive bad memories, re-living a part such as a past trauma, "
           "and flashbacks for several days in a row.",
           "वर्तमान संपर्क खोकर आघात को दोबारा जीना, इतने कष्टदायी फ्लैशबैक कि दिन भरना कठिन, अवांछित बुरी यादें, "
           "पूर्व आघात जैसे अंश को पुनर्जीवित करना, तथा कई दिनों तक लगातार फ्लैशबैक।")),
    ("conversion_body", en_hi("Conversion Disorder: Body symptoms", "परिवर्तन विकार: शारीरिक लक्षण"),
     [5, 10, 14, 18], 10,
     en_hi("Difficulty swallowing, temporary blindness (as if blind), paralysis or inability to move "
           "and temporary deafness (as if deaf), all for no known medical reason. Items exactly as "
           "printed on the supplied score sheet.",
           "निगलने में कठिनाई, क्षणिक अंधता (मानो अंधा हों), लकवा/हिलने में असमर्थता तथा क्षणिक बहरापन (मानो बहरा हों), "
           "सब कोई ज्ञात चिकित्सीय कारण विना। आइटम यथावत् मुद्रित स्कोर-शीट के अनुसार।")),
    ("conversion_seizures", en_hi("Conversion Disorder: Pseudo-seizures (psychogenic non-epileptic seizures)",
                                  "परिवर्तन विकार: छद्म-दौरे (मनोजन्य गैर-मिर्गी दौरे)"),
     [26], 10,
     en_hi("Seizures for which your doctor can find no reason. Single-item subscale; requires medical "
           "evaluation before any interpretation.",
           "दौरे जिनका कारण चिकित्सक नहीं पा सकतें। एकल-आइटम उप-पैमाना; किसी व्याख्या से पूर्व चिकित्सीय मूल्यांकन आवश्यक।")),
    ("general_trance", en_hi("General subscale: Trance", "सामान्य उप-पैमाना: ट्रांस"),
     [21, 27, 30, 32, 41, 51], 11.7,
     en_hi("Difficulty walking, trance that interferes with daily activities and responsibilities, "
           "trance for hours, drifting into trance unawares, trance several days in a row, and "
           "difficulty staying out of trance. Items exactly as printed on the supplied score sheet "
           "(item 21 also carries the functional-body-symptom stem - see sourceNotes).",
           "चलने में कठिनाई, दैनिक कार्य एवं ज़िम्मेदारियों को प्रभावित करने वाला ट्रांस, घंटों ट्रांस, बिना जानें ट्रांस में "
           "जाना, लगातार कई दिनों तक ट्रांस, तथा ट्रांस से बाहर रहने में कठिनाई। आइटम यथावत् मुद्रित स्कोर-शीट के अनुसार "
           "(आइटम 21 शारीरिक-लक्षण कथन भी वहन करता है — sourceNotes देखें।"),),
    ("general_self_confusion", en_hi("General subscale: Self-confusion", "सामान्य उप-पैमाना: स्व-विभ्रम"),
     [6, 11, 12, 17, 23, 55], 33.3,
     en_hi("Trance-like episodes with loss of awareness, feeling detached from your behaviour, "
           "uncertainty about who you really are, disconnection from everything around you, strong "
           "confusion about identity, and being puzzled by your own emotions.",
           "ट्रांस-सदृश अवस्थाएँ, अपने व्यवहार से विलगता, वास्तविक पहचान के बारे में अनिश्चितता, चारों ओर की हर वस्तु से "
           "कटाव, पहचान में गहरा विभ्रम, तथा अपनी भावनाओं से हैरानी।")),
]

MID_SCORE_RANGES = [
    {"max": 7, "label": en_hi("Does not have dissociative experiences",
                              "वियोजीय अनुभव नहीं हैं")},
    {"max": 14, "label": en_hi("Has few diagnostically significant dissociative experiences",
                               "नैदानिक रूप से महत्वपूर्ण वियोजीय अनुभव अल्प हैं")},
    {"max": 20, "label": en_hi("Mild dissociative symptoms and experiences. PTSD or a mild dissociative disorder "
                               "(such as dissociative amnesia, depersonalization/derealization disorder) are possible.",
                               "हल्के वियोजीय लक्षण एवं अनुभव। PTSD या हल्का वियोजीय विकार (जैसे वियोजीय क्षतिस्मृति, "
                               "विलगता/वास्तविकता-विचलन विकार) संभव।")},
    {"max": 30, "label": en_hi("May have dissociative disorder and/or PTSD.",
                               "वियोजीय विकार एवं/अथवा PTSD संभव।")},
    {"max": 40, "label": en_hi("May have a dissociative disorder (such as OSDD-1 or DID) and PTSD.",
                               "वियोजीय विकार (जैसे OSDD-1 या DID) एवं PTSD संभव।")},
    {"max": 64, "label": en_hi("Probably has DID or a severe dissociative disorder and PTSD.",
                               "संभवतः DID अथवा गंभीर वियोजीय विकार एवं PTSD।")},
    {"max": 100, "label": en_hi("Severe dissociative and post-traumatic symptoms. High scores may also reflect "
                                "neuroticism, attention-seeking behaviour, exaggeration or malingering of "
                                "symptoms, or psychosis.",
                                "गंभीर वियोजीय एवं आघात-पश्चात् लक्षण। उच्च स्कोर न्यूरोटिसिज़्म, ध्यान-आकर्षण "
                                "व्यवहार, लक्षणों का अधिक-प्रदर्शन अथवा अभिनय, या मनोविकृति भी दर्शा सकते हैं।")},
]

MID_SOURCE_NOTES = {
    "provenance": en_hi(
        "MID-60 short form reference: Kate, M.-A., Jamieson, G., Dorahy, M. J., & Middleton, W. (2021). "
        "Measuring dissociative symptoms and experiences in an Australian college sample using a short "
        "version of the Multidimensional Inventory of Dissociation. Journal of Trauma & Dissociation, "
        "22(3), 265-287. https://doi.org/10.1080/15299732.2020.1792024",
        "MID-60 लघु-संस्करण संदर्भ: Kate, Jamieson, Dorahy & Middleton (2021), Journal of Trauma & "
        "Dissociation, 22(3), 265-287।"),
    "transcription": en_hi(
        "Items and subscale keys were transcribed from the user-supplied packet exactly as printed. "
        "Two features of the printed keys are recorded rather than silently changed: (a) item 21 "
        "('Having difficulty walking, for no known medical reason') is listed by the score sheet in "
        "BOTH the Trance key (21, 27, 30, 32, 41, 51) and the functional-body-symptom group, although "
        "its stem reads as a body symptom; (b) because item 21 sits in the Trance key, the printed "
        "'Conversion Disorder: Body symptoms' key covers items 5, 10, 14, 18 only, leaving difficulty "
        "walking outside it. Both keys are implemented verbatim so scores match the paper form; check "
        "against the published MID manual before clinical use. The full MID is a 253-item copyrighted "
        "instrument; this implementation is the 60-item short form only and reproduces no normative "
        "data - verify licensing before redistribution.",
        "आइटम एवं उप-पैमाना-कुंजियाँ उपयोगकर्ता-प्रदत्त पत्रक से अंकित की गईं। दो मुद्रित असंगतियाँ "
        "चुपचाप सुधारने के बजाय दर्ज की गई हैं: (a) 'शारीरिक लक्षण' कुंजी में 5, 10, 14, 18 हैं जबकि आइटम 21 "
        "(चलने में कठिनाई) पाँचवाँ कार्यात्मक-तंत्रिका कथन है और यहाँ सम्मिलित है; (b) 'ट्रांस' कुंजी में आइटम 21 "
        "है जो उसी शारीरिक लक्षण को दोहराता है, अतः उसके स्थान पर आइटम 6 लिया गया है। पूर्ण MID 253-आइटम "
        "coppyrighted उपकरण है; यह कार्यान्वयन केवल 60-आइटम लघु-संस्करण है और कोई normativ डेटा पुनःउत्पादित नहीं करता — "
        "पुनर्वितरण से पूर्व लाइसेंस सत्यापित करें।"
    ),
}

# ---------------------------------------------------------------------------
# DES-II item stems (printed order 1..28)
# ---------------------------------------------------------------------------
D = [
    ("Driving or riding in a car, bus or subway and suddenly realizing that you don't remember what has happened during all or part of the trip.",
     "कार/बस/मेट्रो में यात्रा करते समय अचानक एहसास कि यात्रा के सभी/कुछ भाग की घटनाएँ याद नहीं।"),
    ("Listening to someone talk and suddenly realizing that you did not hear part or all of what was said.",
     "किसी की बात सुनते हुए अचानक एहसास कि कही गई बात का कुछ/पूरा भाग सुनाई ही नहीं दिया।"),
    ("Finding yourself in a place and having no idea how you got there.",
     "किसी स्थान पर स्वयं को पाकर भी यह न जानना कि वहाँ कैसे पहुँचे।"),
    ("Finding yourself dressed in clothes that you don't remember putting on.",
     "ऐसे वस्त्र पहने पाए जाना जो पहने का स्मरण नहीं।"),
    ("Finding new things among your belongings that you do not remember buying.",
     "अपने सामान में नई वस्तुएँ मिलना जिनके खरीदने का स्मरण नहीं।"),
    ("Being approached by people you do not know, who call you by another name or insist that you have met them before.",
     "अपरिचित लोग आपको अन्य नाम से बुलाना या पूर्व-मुलाकात पर जोर देना।"),
    ("Feeling as though you are standing next to yourself or watching yourself do something, seeing yourself as if looking at another person.",
     "ऐसा लगना जैसे स्वयं के पास खड़े होकर अपना कार्य देख रहे हों, मानो अन्य व्यक्ति देख रहे हों।"),
    ("Being told that you sometimes do not recognize friends or family members.",
     "दूसरों द्वारा बताया जाना कि कभी-कभी आप मित्रों या परिवार वालों को नहीं पहचान पाते।"),
    ("Having no memory for some important events in your lives (for example, a wedding or graduation).",
     "जीवन की कुछ महत्वपूर्ण घटनाओं (जैसे विवाह, स्नातक समारोह) की स्मृति का अभाव।"),
    ("Being accused of lying when you do not think that you have lied.",
     "झूठ बोलने का आरोप लगना जब आपको लगता है कि आपने झूठ नहीं बोला।"),
    ("Looking in a mirror and not recognizing yourself.", "दर्पण में स्वयं को देखकर न पहचान पाना।"),
    ("Feeling that other people, objects, and the world around you are not real.",
     "लोगों, वस्तुओं एवं चारों ओर के संसार को अवास्तविक अनुभव करना।"),
    ("Feeling that your body does not seem to belong to you.", "शरीर का आपको नहीं लगना।"),
    ("Remembering a past event so vividly that you feel as if you were reliving that event.",
     "पूर्व घटना इतनी जीवंतता से याद करना मानो उसे पुनः जी रहे हों।"),
    ("Not being sure whether things you remember happening really did happen or whether you just dreamed them.",
     "यह निश्चित न होना कि याद आ रही घटनाएँ वास्तव में घटीं अथवा केवल स्वप्न थीं।"),
    ("Being in a familiar place but finding it strange and unfamiliar.",
     "परिचित स्थान पर होते हुए उसे विचित्र एवं अपरिचित लगना।"),
    ("Watching television or a movie and becoming so absorbed in the story that you are unaware of other events happening around you.",
     "टीवी/फिल्म में इतना लीन होना कि चारों ओर घटित अन्य घटनाओं का पता न चले।"),
    ("Becoming so involved in a fantasy or daydream that it feels as though it were really happening to you.",
     "कल्पना/दिवास्वप्न में इतना लीन होना मानो वह वास्तव में घट रहा हो।",),
    ("Being able to ignore pain.", "दर्द को उपेक्षित कर पाना।"),
    ("Sitting staring off into space, thinking of nothing, and not aware of the passage of time.",
     "शून्य में टकटकी लगाकर बैठना, कुछ न सोचना, समय बीतने का पता न चलना।"),
    ("When alone, talking out loud to yourself.", "एकांत में स्वयं से ऊँची आवाज़ में बात करना।"),
    ("Acting so differently in one situation compared with another that you feel almost as if you were two different people.",
     "एक परिस्थिति में दूसरी की तुलना में इतना भिन्न व्यवहार कि लगें दो भिन्न व्यक्ति।"),
    ("In certain situations being able to do things with amazing ease and spontaneity that would usually be difficult for you (for example, sports, work, social situations).",
     "कुछ परिस्थितियों में आश्चर्यजनक सहजता से कार्य कर पाना जो सामान्यतः कठिन हों (खेल, कार्य, सामाजिक)।"),
    ("Not being able to remember whether you have done something or have just thought about doing that thing (for example, not knowing whether you have just mailed a letter or have just thought about mailing it).",
     "यह स्मरण न होना कि कोई कार्य किया अथवा केवल करने का विचार किया (जैसे पत्र डाक भेजना)।"),
    ("Finding evidence that you have done things that you do not remember doing.",
     "ऐसे प्रमाण मिलना कि आपने कार्य किए पर उनका स्मरण नहीं।"),
    ("Finding writings, drawings, or notes among your belongings that you must have done but cannot remember doing.",
     "सामान में लिखावट/चित्र/नोट मिलना जो आपके ही हों पर करने का स्मरण न हो।"),
    ("Hearing voices inside your head that tell you to do things or comment on things that you are doing.",
     "सिर के भीतर ऐसी आवाज़ें जो कार्य करने को कहें या आपके कार्य पर टिप्पणी करें।"),
    ("Feeling as if you are looking at the world through a fog, so that people and objects appear far away or unclear.",
     "ऐसा लगना जैसे कोहरे के पार से संसार देख रहे हों; लोग एवं वस्तुएँ दूर या अस्पष्ट।"),
]

DES_SAFETY_ITEMS = {27: en_hi(
    "Command/commentary internal voices endorsed — assess for psychosis, DID persecutory parts and "
    "risk to self or others.",
    "आदेश/टिप्पणी करने वाली भीतरी आवाज़ें — मनोविकृति, DID के उत्पीड़नकारी अंश तथा स्व/पर-जोखिम का मूल्यांकन करें।")}


def build_mid_scale():
    qs = []
    for n, (en, hi) in enumerate(M, start=1):
        q = {"id": "mid_%d" % n, "itemNumber": n, "text": en_hi(en, hi)}
        if n in MID_SAFETY_ITEMS:
            q["safety"] = True
            q["safetyNote"] = en_hi(
                "Self-harm or suicide-related internal voice / finding means of self-harm — "
                "complete a suicide-risk assessment.",
                "स्व-क्षति/आत्महत्या से जुड़ी भीतरी आवाज़ या हथियार-साधन मिलना — आत्महत्या-जोखिम मूल्यांकन पूर्ण करें।")
        qs.append(q)
    assert len(qs) == 60, len(qs)

    subscales = {}
    for slug, name, items, cutoff, note in MID_SUBSCALES:
        subscales[slug] = {
            "name": name,
            "items": items,
            "cutoff": cutoff,
            "note": note,
        }
    covered = set()
    for s in subscales.values():
        covered.update(s["items"])
    assert len(covered) == 60 and covered == set(range(1, 61)), \
        sorted(set(range(1, 61)) - covered) + sorted(covered - set(range(1, 61)))

    return {
        "id": "mid60",
        "name": en_hi("Multidimensional Inventory of Dissociation — MID-60 (short form)",
                      "बहुआयामी वियोजन सूची — MID-60 (लघु संस्करण)"),
        "type": "matrix",
        "administeredBy": "self-report",
        "optionalAssessment": True,
        "sourceInstrument": "MID-60",
        "targetAge": ["adult", "adolescent"],
        "directions": en_hi(
            "How often do you have the following experiences when you are NOT under the influence of "
            "alcohol or drugs? Select the number that best describes you: choose 0 if the experience "
            "never happens to you, 10 if it is always happening to you, and a number between 1 and 9 "
            "if it happens sometimes but not all the time.",
            "जब आप शराब या नशे के प्रभाव में न हों, तब नीचे दिए अनुभव कितनी बार होते हैं? वह अंक चुनें जो "
            "आपका सर्वोत्तम वर्णन करे: अनुभव कभी न हो तो 0, सदैव होता हो तो 10, बीच में कभी-कभी हो तो 1 से 9 के "
            "बीच का अंक।"),
        "timeframe": en_hi(
            "Frequency of experiences when not under the influence of alcohol or drugs.",
            "शराब/नशा के प्रभाव में न रहते हुए अनुभवों की आवृत्ति।"),
        "parts": [{
            "id": "mid_part1",
            "name": en_hi("Experiences (rate 0 = never to 10 = always)",
                          "अनुभव (0 = कभी नहीं से 10 = सदैव तक अंकित करें)"),
            "options": MID_OPTS,
            "anchors": [{"v": 0, "label": MID_ANCHORS[0]}, {"v": 10, "label": MID_ANCHORS[1]}],
            "questions": qs,
        }],
        "matrixOptions": MID_OPTS,
        "ratingScale": {
            "min": 0, "max": 10,
            "note": en_hi("0 = never happens to you ... 10 = always happening to you.",
                          "0 = आपको कभी नहीं होता ... 10 = सदैव हो रहा है।"),
        },
        "sumScoring": True,
        "scoring": {
            "method": "mid60_mean_index",
            "indexFormula": en_hi(
                "Total mean score = (average of all 60 responses) x 10, expressed as a percentage 0-100.",
                "कुल माध्य स्कोर = (सभी 60 उत्तरों का औसत) × 10, प्रतिशत के रूप में 0-100।"),
            "scaleMin": 0,
            "scaleMax": 10,
            "rule": en_hi(
                "Compute the mean of the 60 item ratings and multiply by 10 to obtain the MID-60 index "
                "(0-100). Compare the index against the printed score ranges, and compare each subscale "
                "mean (also x10) against its own clinical cutoff. A subscale above cutoff indicates the "
                "need for the full diagnostic interview (SCID-5-D / MID) — it is not itself a diagnosis.",
                "60 आइटम रेटिंग का माध्य निकालकर 10 से गुणा करें — MID-60 सूचकांक (0-100)। सूचकांक की तुलना मुद्रित "
                "स्कोर-परिसर से करें, तथा प्रत्येक उप-पैमाने के माध्य (×10) की तुलना उसके नैदानिक कटऑफ से करें। "
                "कटऑफ से ऊपर उप-पैमाना पूर्ण नैदानिक साक्षात्कार (SCID-5-D / MID) की आवश्यकता दर्शाता है — स्वयं "
                "रोग-निर्णय नहीं।"),
            "subscaleAggregation": "mean_x10",
        },
        "scoreRanges": MID_SCORE_RANGES,
        "subscales": subscales,
        "normsNote": en_hi(
            "Score ranges and subscale cutoffs are reproduced from the supplied MID-60 score sheet. The "
            "MID-60 is a screening/severity measure: elevated subscales indicate which dissociative "
            "disorder (DID, OSDD-1, dissociative amnesia, DDD, PTSD, functional neurological symptoms) "
            "needs a full structured interview. Very high scores may also reflect neuroticism, "
            "exaggeration, malingering or psychosis.",
            "स्कोर-परिसर एवं उप-पैमाना कटऑफ प्रदत्त MID-60 स्कोर-शीट से अंकित हैं। MID-60 स्क्रीनिंग/तीव्रता माप है: "
            "उच्च उप-पैमाने दर्शाते हैं कि कौन-सा वियोजीय विकार (DID, OSDD-1, वियोजीय क्षतिस्मृति, DDD, PTSD, "
            "कार्यात्मक न्यूरोलॉजिकल लक्षण) पूर्ण संरचित साक्षात्कार माँगता है। अत्यधिक उच्च स्कोर न्यूरोटिसिज़्म, "
            "अधिक-प्रदर्शन, अभिनय या मनोविकृति भी हो सकते हैं।"),
        "sourcePages": "MID-60 patient form + score sheet (supplied packet)",
        "sourceNotes": MID_SOURCE_NOTES,
        "translationNote": en_hi(
            "English item stems are authoritative; Hindi labels are machine-assisted translations for "
            "clinician review and must be proofread by a qualified translator before clinical use.",
            "अंग्रेज़ी कथन प्राधिकृत हैं; हिंदी लेबल चिकित्सक-समीक्षा हेतु यंत्र-सहायित अनुवाद हैं औरclinical प्रयोग से "
            "पूर्व योग्य अनुवादक से शुद्धि आवश्यक।"),
        "branching": None,
    }


def build_des_scale():
    qs = []
    for n, (en, hi) in enumerate(D, start=1):
        q = {"id": "desii_%d" % n, "itemNumber": n, "text": en_hi(en, hi)}
        if n in DES_SAFETY_ITEMS:
            q["safety"] = True
            q["safetyNote"] = DES_SAFETY_ITEMS[n]
        qs.append(q)
    assert len(qs) == 28, len(qs)
    return {
        "id": "desii",
        "name": en_hi("Dissociative Experiences Scale — DES-II",
                      "वियोजीय अनुभव पैमाना — DES-II"),
        "type": "matrix",
        "administeredBy": "self-report",
        "optionalAssessment": True,
        "sourceInstrument": "DES-II",
        "targetAge": ["adult", "adolescent"],
        "directions": en_hi(
            "This questionnaire consists of twenty-eight questions about experiences that you may have "
            "in your daily life. We are interested in how often you have these experiences. Your answers "
            "must show how often these experiences happen to you when you are NOT under the influence of "
            "alcohol or drugs. For each item, determine to what degree the described experience applies "
            "to you and mark the number showing the percentage of the time you have the experience "
            "(0% = never, 100% = always).",
            "यह प्रश्नावनी आपके दैनिक जीवन के संभाव्य अनुभवों से संबंधित अट्ठाईस प्रश्नों की है। हमें यह जानना है कि "
            "ये अनुभव आपको कितनी बार होते हैं। उत्तर यह दर्शाएँ कि ये अनुभव शराब या नशे के प्रभाव में न रहते हुए "
            "कितनी बार होते हैं। प्रत्येक प्रश्न हेतु निर्धारित करें कि वर्णित अनुभव आपको किस सीमा तक लागू होता है और "
            "वह प्रतिशत अंकित करें (0% = कभी नहीं, 100% = सदैव)।"),
        "timeframe": en_hi(
            "How often the experiences occur in daily life (not under the influence of alcohol or drugs).",
            "दैनिक जीवन में अनुभव कितनी बार होते हैं (शराब/नशे के प्रभाव में नहीं)।"),
        "parts": [{
            "id": "desii_part1",
            "name": en_hi("Percentage of time the experience happens (0% Never to 100% Always)",
                          "अनुभव कितने प्रतिशत समय होता है (0% कभी नहीं से 100% सदैव तक)"),
            "options": DES_OPTS,
            "anchors": [{"v": 0, "label": en_hi("0% (Never)", "0% (कभी नहीं)")},
                        {"v": 100, "label": en_hi("100% (Always)", "100% (सदैव)")}],
            "questions": qs,
        }],
        "matrixOptions": DES_OPTS,
        "ratingScale": {
            "min": 0, "max": 100,
            "note": en_hi("Each item is answered with the percentage of time the experience happens: "
                          "0% 10 20 30 40 50 60 70 80 90 100% (Never → Always).",
                          "प्रत्येक प्रश्न का उत्तर अनुभव के प्रतिशत समय से: 0% 10 20 30 40 50 60 70 80 90 100% "
                          "(कभी नहीं → सदैव)।"),
        },
        "sumScoring": True,
        "scoring": {
            "method": "desii_mean_percent",
            "indexFormula": en_hi(
                "DES-II total = the mean of the twenty-eight item percentages (0-100).",
                "DES-II कुल = अट्ठाईस आइटम प्रतिशतों का माध्य (0-100)।"),
            "scaleMin": 0,
            "scaleMax": 100,
            "cutoff": 30,
            "rule": en_hi(
                "Sum the twenty-eight item percentages and divide by 28. A mean DES-II score of 30 or "
                "above is the commonly used clinical comparison point and warrants a structured "
                "dissociative-disorder interview; higher means indicate greater dissociative severity. "
                "The DES-II is a screening measure and is not diagnostic on its own.",
                "अट्ठाईस आइटम प्रतिशतों को जोड़कर 28 से भाग दें। 30 या उससे अधिक का माध्य DES-II स्कोर सामान्यतः "
                "प्रयुक्त नैदानिक-तुलना बिंदु है और संरचित वियोजीय-विकार साक्षात्कार हेतु निर्देशित करता है; उच्च माध्य "
                "अधिक वियोजन-तीव्रता दर्शाता है। DES-II स्क्रीनिंग माप है, स्वयं में रोग-निर्णायक नहीं।"),
        },
        "bands": [
            {"max": 9, "severity": en_hi("Low dissociative experiences", "अल्प वियोजीय अनुभव")},
            {"max": 29, "severity": en_hi("Moderate dissociative experiences", "मध्यम वियोजीय अनुभव")},
            {"max": 44, "severity": en_hi("High dissociative experiences (>= 30: clinical comparison point)",
                                          "उच्च वियोजीय अनुभव (≥30: नैदानिक-तुलना बिंदु)")},
            {"max": 100, "severity": en_hi("Very high dissociative experiences", "अत्यंत उच्च वियोजीय अनुभव")},
        ],
        "normsNote": en_hi(
            "No population norms are reproduced here. The >= 30 mean is the widely used clinical "
            "comparison point from the DES-II literature (Carlson & Putnam); interpret alongside the "
            "MID-60 subscale pattern, trauma history and the structured interview.",
            "यहाँ कोई जनसंख्या-नॉर्म पुनःउत्पादित नहीं किए गए। ≥30 माध्य DES-II साहित्य (Carlson & Putnam) का "
            "व्यापक रूप से प्रयुक्त नैदानिक-तुलना बिंदु है; MID-60 उप-पैमाना प्रतिरूप, आघात-इतिहास एवं संरचित "
            "साक्षात्कार के साथ व्याख्या करें।"),
        "sourcePages": "DES-II directions + items 1-28 (supplied packet)",
        "translationNote": en_hi(
            "English item stems are authoritative; Hindi labels are machine-assisted translations for "
            "clinician review and must be proofread by a qualified translator before clinical use.",
            "अंग्रेज़ी कथन प्राधिकृत हैं; हिंदी लेबल चिकित्सक-समीक्षा हेतु यंत्र-सहायित अनुवाद हैं और नैदानिक प्रयोग से "
            "पूर्व योग्य अनुवादक से शुद्धि आवश्यक।"),
        "branching": None,
    }


def main(check=False):
    with open(DATA, encoding='utf-8') as f:
        data = json.load(f)

    scales = data.setdefault('scales', {})
    scales['mid60'] = build_mid_scale()
    scales['desii'] = build_des_scale()

    # ---- domain ----------------------------------------------------------
    domains = data.setdefault('domains', [])
    dom = {
        "id": "dissociation",
        "name": en_hi("Dissociation", "वियोजन"),
        "tier": 2,
        "instrument": "auto:dissociationtable",
        "timeframe": en_hi(
            "Screen-in items refer to the past month and to experiences had when you are not under the "
            "influence of alcohol or drugs; the deployed instruments then rate lifetime/current "
            "dissociative experiences.",
            "स्क्रीन-इन प्रश्न गत माह को एवं उन अनुभवों को संदर्भित करते हैं जो शराब/नशे के प्रभाव में न रहते हुए हों; "
            "तत्पश्चात् संलग्न उपकरण जीवन-भर/वर्तमान वियोजीय अनुभव रेट करते हैं।"),
        "questions": [
            {
                "id": "dis_1",
                "text": en_hi(
                    "Do you often have experiences such as losing track of time or part of the day, "
                    "finding things you don't remember buying or doing, feeling detached from your body "
                    "or from surroundings, or hearing voices inside your head — when you are not under "
                    "the influence of alcohol or drugs?",
                    "क्या आपको प्रायः ऐसे अनुभव होते हैं — समय/दिन का कुछ भाग खो जाना, बिना खरीदे-किए वस्तुएँ मिलना, "
                    "शरीर या चारों ओर से विलगता, सिर के भीतर आवाज़ें सुनना — जब आप शराब/नशे के प्रभाव में न हों?"),
                "sharedScale": "yesno",
                "scaleId": "mid60",
                "disorders": DISS_DISORDERS,
            },
            {
                "id": "dis_2",
                "text": en_hi(
                    "Have other people told you that you sometimes seem to go blank, forget conversations "
                    "or events, act unlike yourself, or that you describe more than one 'part' of you?",
                    "क्या दूसरों ने बताया है कि कभी-कभी आप खाली-से लगते हैं, बातचीत/घटनाएँ भूल जाते हैं, अपने से भिन्न "
                    "व्यवहार करते हैं, अथवा आप अपने भीतर एक से अधिक \"अंश\" का वर्णन करते हैं?"),
                "sharedScale": "yesno",
                "scaleId": "desii",
                "disorders": DISS_DISORDERS,
            },
        ],
    }
    existing = next((i for i, x in enumerate(domains) if x['id'] == 'dissociation'), None)
    if existing is None:
        # keep trauma and dissociation adjacent
        ti = next((i for i, x in enumerate(domains) if x['id'] == 'trauma'), len(domains) - 1)
        domains.insert(ti + 1, dom)
    else:
        domains[existing] = dom

    # ---- disorders -------------------------------------------------------
    disc = data.setdefault('disorders', {})
    disc.setdefault('dissociative_identity_disorder', {
        "name": en_hi("Dissociative Identity Disorder", "वियोजीय पहचान विकार"),
        "tier": 5,
        "dsm5": "Dissociative Identity Disorder",
        "icd11": "6B64",
        "description": en_hi(
            "Two or more distinct personality states with recurrent amnesia; disruption of identity "
            "characterized by marked discontinuity of sense of self and sense of agency.",
            "दो या अधिक भिन्न व्यक्तित्व-अवस्थाएँ एवं बार-बार क्षतिस्मृति; स्व-बोध एवं कर्तृत्व-बोध में स्पष्ट असंततता।"),
        "mappingNote": (
            "ICD-11 6B64 corresponds to DSM-5-TR Dissociative Identity Disorder; the pre-existing "
            "'dissociative' key holds the same label and is retained for backward compatibility. "
            "Flagged by MID-60/DES-II screens only — diagnosis requires the full structured interview."),
    })
    disc.setdefault('other_specified_dissociative_disorder', {
        "name": en_hi("Other Specified Dissociative Disorder", "अन्य निर्दिष्ट वियोजीय विकार"),
        "tier": 5,
        "dsm5": "Other Specified Dissociative Disorder",
        "icd11": "6B6Y",
        "description": en_hi(
            "Clinically significant dissociative symptoms that do not meet criteria for a specific "
            "dissociative disorder (e.g. OSDD-1: identity disruption with less distinct parts, or "
            "without amnesia).",
            "नैदानिक रूप से महत्वपूर्ण वियोजीय लक्षण जो किसी निश्चित वियोजीय विकार के मानदंड पूर्ण नहीं करते "
            "(जैसे OSDD-1: कम भिन्न अंशों के साथ पहचान-विचलन, अथवा क्षतिस्मृति विना)।"),
        "mappingNote": "ICD-11 6B6Y Other specified dissociative disorder; DSM-5-TR OSDD. Screen flags only.",
    })
    disc.setdefault('unspecified_dissociative_disorder', {
        "name": en_hi("Unspecified Dissociative Disorder", "अनिर्दिष्ट वियोजीय विकार"),
        "tier": 5,
        "dsm5": "Unspecified Dissociative Disorder",
        "icd11": "6B6Z",
        "description": en_hi(
            "Dissociative symptoms of clinical significance where criteria are not met or information "
            "is insufficient for a specific diagnosis.",
            "नैदानिक महत्व वाले वियोजीय लक्षण जहाँ मानदंड पूर्ण नहीं हैं अथवा विशिष्ट निदान हेतु सूचना अपर्याप्त है।"),
        "mappingNote": "ICD-11 6B6Z Unspecified dissociative disorder; DSM-5-TR unspecified. Screen flags only.",
    })
    disc.setdefault('dissociative_amnesia', {
        "name": en_hi("Dissociative Amnesia", "वियोजीय क्षतिस्मृति"),
        "tier": 5,
        "dsm5": "Dissociative Amnesia",
        "icd11": "6B60",
        "description": en_hi(
            "Inability to recall important autobiographical information, inconsistent with ordinary "
            "forgetting; may include dissociative fugue.",
            "महत्वपूर्ण आत्मकथात्मक सूचना का स्मरण-असमर्थता, साधारण विस्मरण से असंगत; वियोजीय फ्यूग सम्मिलित हो सकती है।"),
        "mappingNote": "ICD-11 6B60; DSM-5-TR Dissociative Amnesia. Flagged by MID-60 amnesia subscales.",
    })
    disc.setdefault('depersonalisation_derealisation_disorder', {
        "name": en_hi("Depersonalization/Derealization Disorder", "विलगता/वास्तविकता-विचलन विकार"),
        "tier": 5,
        "dsm5": "Depersonalization/Derealization Disorder",
        "icd11": "6B61",
        "description": en_hi(
            "Persistent or recurrent episodes of depersonalization, derealization or both, with intact "
            "reality testing.",
            "विलगता, वास्तविकता-विचलन अथवा दोनों की निरंतर/पुनरावृत्त घटनाएँ, वास्तविकता-परीक्षण सुरक्षित।"),
        "mappingNote": "ICD-11 6B61; DSM-5-TR DDD. Flagged by the MID-60 D/DD subscale.",
    })

    # link the new instruments into the library
    inst = data.setdefault('instruments', {})
    inst['MID-60'] = {
        "name": en_hi("Multidimensional Inventory of Dissociation — MID-60 (short form)",
                      "बहुआयामी वियोजन सूची — MID-60 (लघु संस्करण)"),
        "description": en_hi(
            "60-item dissociative-experience inventory rated 0-10 (never → always) when not intoxicated. "
            "Index = mean of all 60 responses x 10 (0-100) with printed score ranges (0-7 none; 7-14 few; "
            "15-20 mild; 21-30 may have DD/PTSD; 31-40 may have DD such as OSDD-1/DID; 41-64 probably DID "
            "or severe DD; 64+ severe). Twelve subscales carry individual clinical cutoffs (DID amnesia 10; "
            "alter awareness 20; angry intrusions 18; persecutory intrusions 18; D/DD 20; amnesia distress 30; "
            "autobiographical amnesia 34; PTSD flashbacks 16; conversion body symptoms 10; pseudo-seizures 10; "
            "trance 11.7; self-confusion 33.3). Screening/severity only — not diagnostic.",
            "60-आइटम वियोजीय-अनुभव सूची, नशे में न रहते हुए 0-10 (कभी नहीं → सदैव) रेटेड। सूचकांक = सभी 60 उत्तरों का "
            "माध्य × 10 (0-100), मुद्रित स्कोर-परिसर सहित। बारह उप-पैमानों पर पृथक नैदानिक कटऑफ (DID क्षतिस्मृति 10; "
            "अंश-बोध 20; क्रोधित प्रवेश 18; उत्पीड़नकारी प्रवेश 18; D/DD 20; क्षतिस्मृति-कष्ट 30; आत्मकथात्मक क्षतिस्मृति 34; "
            "PTSD फ्लैशबैक 16; परिवर्तन शारीरिक लक्षण 10; छद्म-दौरे 10; ट्रांस 11.7; स्व-विभ्रम 33.3)। केवल स्क्रीनिंग/तीव्रता — "
            "रोग-निर्णायक नहीं।"),
        "domain": "dissociation",
        "format": "self-report 0-10 frequency matrix with index and subscale cutoffs",
        "duration": "10-15 minutes",
        "optionalAssessment": True,
    }
    inst['DES-II'] = {
        "name": en_hi("Dissociative Experiences Scale (DES-II)",
                      "वियोजीय अनुभव पैमाना (DES-II)"),
        "description": en_hi(
            "28-item self-report measure; each item is scored as the percentage of time the experience "
            "occurs (0-100%) and the total is the mean of the 28 percentages. A mean of 30 or higher is "
            "the clinical comparison point indicating a need for a structured dissociative interview "
            "(Eve Bernstein Carlson, Ph.D. & Frank W. Putnam, M.D.). Not diagnostic on its own.",
            "28-आइटम स्व-वर्णित माप; प्रत्येक आइटम अनुभव के प्रतिशत समय (0-100%) से अंकित और कुल 28 प्रतिशतों का माध्य है। "
            "30 या अधिक का माध्य नैदानिक-तुलना बिंदु है जो संरचित वियोजीय साक्षात्कार हेतु निर्देशित करता है (Carlson & "
            "Putnam)। स्वयं में रोग-निर्णायक नहीं।"),
        "domain": "dissociation",
        "format": "self-report percentage matrix with mean total",
        "duration": "5-10 minutes",
        "optionalAssessment": True,
    }

    meta = data.setdefault('meta', {})
    meta['schemaVersion'] = '2.5.0'
    meta['updated'] = '2026-11-04'
    notes = meta.get('instrumentNotes', [])
    if isinstance(notes, list):
        for n in [
            "Dissociation instruments implemented as scales.mid60 (Multidimensional Inventory of "
            "Dissociation 60-item short form; index = mean of 60 ratings x 10 with printed score ranges "
            "and 12 subscale clinical cutoffs) and scales.desii (Dissociative Experiences Scale II; 28 "
            "percentage items, total = mean, clinical comparison point >= 30). Reached through the new "
            "'dissociation' domain via routing auto:dissociationtable; both are self-report dimensional "
            "screening measures and gate no diagnostic box.",
            "MID-60 short-form reference: Kate, Jamieson, Dorahy & Middleton (2021), Journal of Trauma & "
            "Dissociation 22(3), 265-287. Two printed subscale-key anomalies (body-symptom item 21 vs "
            "trance item 21 duplication) are documented in scales.mid60.sourceNotes instead of being "
            "silently corrected. The full 253-item MID is copyrighted — verify licensing before "
            "redistribution.",
            "MID-60 items 22, 37, 44, 56 and 58 (persecutory/degrading voices, waking with means of "
            "self-harm) and DES-II item 27 (command/commentary voices) carry safety flags that open "
            "the crisis pathway when rated above zero.",
        ]:
            if n not in notes:
                notes.append(n)

    # sanity: every disorder referenced from the domain exists
    all_disc = set(disc.keys())
    for q in dom['questions']:
        missing = [x for x in q['disorders'] if x not in all_disc]
        assert not missing, missing

    if check:
        mid = scales['mid60']
        des = scales['desii']
        print("check OK | MID items:", len(mid['parts'][0]['questions']),
              "| subscales:", len(mid['subscales']),
              "| score ranges:", len(mid['scoreRanges']),
              "| DES items:", len(des['parts'][0]['questions']),
              "| schema", meta['schemaVersion'])
        return

    with open(DATA, 'w', encoding='utf-8') as f:
        f.write(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    print("wrote data.json schema", meta['schemaVersion'])
    print("MID-60 items:", len(scales['mid60']['parts'][0]['questions']),
          "| subscales:", len(scales['mid60']['subscales']))
    print("DES-II items:", len(scales['desii']['parts'][0]['questions']),
          "| cutoff:", scales['desii']['scoring']['cutoff'])


if __name__ == '__main__':
    main(check='--check' in sys.argv)
