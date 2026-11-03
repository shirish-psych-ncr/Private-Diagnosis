#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_anger.py — Integrate the two anger instruments into data.json:

  1. STAXI-CA — State-Trait Anger Expression Inventory, children/adolescent form
     Part 1  State Anger (SA)          items 1-15   "How I Feel Right Now"        1-4
     Part 2  Trait Anger (TA)          items 16-24  "How I Generally Feel"        1-4
     Part 3  Anger Expression          items 25-57  "How I Generally React..."    1-4
       - Anger-In      25, 29, 35, 38, 41, 44, 47, 50, 53, 56
       - Anger-Out     26, 30, 34, 37, 39, 43, 46, 49, 52, 55
       - Anger Control 27, 31, 32, 36, 40, 45, 48, 51, 54, 57
       - Denial        28, 33
     The supplied packet is an OCR'd copy; where it duplicates or garbles stems
     (items 10/11, 30/31, 42/43, "loosing", item 24 "I feel like crying") the
     canonical printed STAXI-CA wording is used and the deviation is recorded in
     `sourceNotes`. Hindi labels are machine-assisted aids flagged for review.

  2. CAS — Clinical Anger Scale (Snell et al., 1995)
     21 clusters x 4 statements (A-D); A=0, B=1, C=2, D=3, summed range 0-63.
     Interpretive ranges: 0-13 minimal, 14-19 mild, 20-28 moderate, 29-63 severe.

Both are deployed through the existing `auto:angertable` routing: endorsing one
of the two screen-in questions of the new `anger` domain opens the matching
matrix. Neither instrument is diagnostic.

Run:  python3 scripts/build_anger.py            (writes data.json in place)
      python3 scripts/build_anger.py --check    (validate only, no write)
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'data.json')


def en_hi(en, hi):
    return {"en": en, "hi": hi}


# ---------------------------------------------------------------------------
# Response option sets
# ---------------------------------------------------------------------------
# STAXI parts use a 1-4 frequency/intensity rating (paper form: circles 1..4).
STAXI_OPTS = [
    {"v": 1, "label": en_hi("1", "1")},
    {"v": 2, "label": en_hi("2", "2")},
    {"v": 3, "label": en_hi("3", "3")},
    {"v": 4, "label": en_hi("4", "4")},
]
# Verbal anchors are printed once per part (they differ between Parts 1/2 and 3).
STAXI_STATE_ANCHORS = [
    en_hi("1 Not at all", "1 बिल्कुल नहीं"),
    en_hi("2 Somewhat", "2 कुछ हद तक"),
    en_hi("3 Moderately so", "3 मध्यम रूप से"),
    en_hi("4 Very much so", "4 अत्यधिक"),
]
STAXI_TRAIT_ANCHORS = [
    en_hi("1 Almost never", "1 लगभग कभी नहीं"),
    en_hi("2 Sometimes", "2 कभी-कभी"),
    en_hi("3 Often", "3 अक्सर"),
    en_hi("4 Almost always", "4 लगभग सदैव"),
]
CAS_OPTS = [
    {"v": 0, "label": en_hi("A", "A")},
    {"v": 1, "label": en_hi("B", "B")},
    {"v": 2, "label": en_hi("C", "C")},
    {"v": 3, "label": en_hi("D", "D")},
]

TF_YESNO = [{"v": 0, "label": en_hi("No", "नहीं")},
            {"v": 1, "label": en_hi("Yes", "हाँ")}]

GENERIC_ANGER_DISORDERS = ["other_specified_disruptive_impulse_control_behaviour_disorder",
                           "unspecified_disruptive_impulse_control_behaviour_disorder"]

# ---------------------------------------------------------------------------
# STAXI-CA item text (English from the supplied packet, canonicalised where the
# scan is garbled; Hindi is a clinician-review aid)
# ---------------------------------------------------------------------------
S = [  # (english, hindi) for items 1..57 in printed order
    ("I am furious.", "मैं प्रचंड क्रोधित हूँ।"),
    ("I feel irritated.", "मुझे चिड़चिड़ापन महसूस होता है।"),
    ("I feel angry.", "मुझे क्रोध महसूस होता है।"),
    ("I feel like yelling at somebody.", "मैं किसी पर चिल्लाना चाहता/चाहती हूँ।"),
    ("I feel like breaking things.", "मैं चीज़ें तोड़ना चाहता/चाहती हूँ।"),
    ("I am mad.", "मैं नाराज़/क्रोधित हूँ।"),
    ("I feel like banging on the table.", "मैं मेज़ पर प्रहार करना चाहता/चाहती हूँ।"),
    ("I feel like hitting someone.", "मैं किसी को मारना चाहता/चाहती हूँ।"),
    ("I feel like swearing.", "मैं गाली देना चाहता/चाहती हूँ।"),
    ("I feel annoyed.", "मुझे क्षुब्धता महसूस होती है।"),
    ("I feel like kicking somebody.", "मैं किसी को लात मारना चाहता/चाहती हूँ।"),
    ("I feel like cursing out loud.", "मैं ज़ोर से शपथ लेना/गाली देना चाहता/चाहती हूँ।"),
    ("I feel like screaming.", "मैं चीखना चाहता/चाहती हूँ।"),
    ("I feel like pounding somebody.", "मैं किसी को पीटना चाहता/चाहती हूँ।"),
    ("I feel like shouting out loud.", "मैं ज़ोर से चिल्लाना चाहता/चाहती हूँ।"),
    ("I am quick tempered.", "मेरा स्वभाव त्वरित-क्रोध वाला है।"),
    ("I have a fiery temper.", "मेरा स्वभाव अग्निश/प्रचंड है।"),
    ("I am a hot-headed person.", "मैं उग्र-स्वभाव व्यक्ति हूँ।"),
    ("I get angry when I'm slowed down by others' mistakes.", "अन्यों की भूलों से विलंब होने पर मुझे क्रोध आता है।"),
    ("I feel annoyed when I am not given recognition for doing good work.", "उत्तम कार्य हेतु प्रशंसा न मिलने पर मुझे क्षुब्धता होती है।"),
    ("I fly off the handle.", "मैं एकदम से फट पड़ता/फट पड़ती हूँ।"),
    ("When I get mad, I say nasty things.", "नाराज़ होने पर मैं कुरूप बातें कहता/कहती हूँ।"),
    ("It makes me furious when I am criticized in front of others.", "अन्यों के सामने आलोचना होने पर मैं प्रचंड क्रोधित हो जाता/जाती हूँ।"),
    ("When I get frustrated, I feel like hitting someone.", "व्यर्थता अनुभव करने पर मैं किसी को मारना चाहता/चाहती हूँ।"),
    ("I feel infuriated when I do a good job and get a poor evaluation.", "उत्तम कार्य करते हुए निम्न मूल्यांकन मिलने पर मुझे प्रकोप महसूस होता है।"),
    ("I control my temper.", "मैं अपने स्वयं को नियंत्रित रखता/रखती हूँ।"),
    ("I express my anger.", "मैं अपना क्रोध व्यक्त करता/करती हूँ।"),
    ("I take a deep breath and relax.", "मैं गहरी श्वास लेकर शिथिल होता/होती हूँ।"),
    ("I keep things in.", "मैं बातें मन में दबाए रखता/रखती हूँ।"),
    ("I am patient with others.", "मैं अन्यों के प्रति धैर्यवान हूँ।"),
    ("If someone annoys me, I'm apt to tell him or her how I feel.", "कोई क्षुब्ध करे तो मैं उसे अपनी भावना बता देता/बताती हूँ।"),
    ("I try to calm myself as soon as possible.", "मैं यथाशीघ्र स्वयं को शांत करने का प्रयास करता/करती हूँ।"),
    ("I pout or sulk.", "मैं नाराज़ होकर मुँह बनाता/बनाती हूँ या एकांत में रहता/रहती हूँ।"),
    ("I control my urge to express my angry feelings.", "क्रोधावेश व्यक्त करने की प्रवृत्ति पर मैं नियंत्रण रखता/रखती हूँ।"),
    ("I lose my temper.", "मैं स्वभाव खो देता/खो देती हूँ।"),
    ("I try to simmer down.", "मैं उत्ताप शान्त करने का प्रयास करता/करती हूँ।"),
    ("I withdraw from people.", "मैं लोगों से दूर हो जाता/जाती हूँ।"),
    ("I keep my cool.", "मैं शीतलता बनाए रखता/रखती हूँ।"),
    ("I make sarcastic remarks to others.", "मैं अन्यों से व्यंग्यात्मक टिप्पणी करता/करती हूँ।"),
    ("I try to soothe my angry feelings.", "मैं क्रोधित भावनाओं को शान्त करने का प्रयास करता/करती हूँ।"),
    ("I control my behaviour.", "मैं अपना व्यवहार नियंत्रित करता/करती हूँ।"),
    ("I endeavour to become calm again.", "मैं पुनः शांत होने का प्रयत्न करता/करती हूँ।"),
    ("I tend to harbour grudges that I don't tell anyone.", "मैं दिल में तिरस्कार/नाराज़गी लिए रखता/रखती हूँ और वह किसी को नहीं बताता/बताती।"),
    ("I can stop myself from losing my temper.", "मैं स्वभाव खोने से स्वयं को रोक सकता/सकती हूँ।"),
    ("I argue with others.", "मैं अन्यों से वाद-विवाद करता/करती हूँ।"),
    ("I reduce my anger as soon as possible.", "मैं यथाशीघ्र क्रोध कम करता/करती हूँ।"),
    ("I do things like slam doors.", "मैं दरवाज़े ज़ोर से बंद करने जैसे कार्य करता/करती हूँ।"),
    ("I am secretly quite critical of others.", "मैं मन में अन्यों की काफी आलोचना करता/करती हूँ।"),
    ("I try to be tolerant.", "मैं सहिष्णु बनने का प्रयास करता/करती हूँ।"),
    ("I get calm faster than others do.", "मैं अन्यों की अपेक्षा शीघ्र शांत हो जाता/जाती हूँ।"),
    ("I strike out at whatever infuriates me.", "जो भी मुझे प्रकोपित करता है, मैं उस पर आक्रमण करता/करती हूँ।"),
    ("I say nasty things.", "मैं कुरूप बातें कहता/कहती हूँ।"),
    ("I try to be tolerant and understanding.", "मैं सहिष्णु एवं समझदार बनने का प्रयास करता/करती हूँ।"),
    ("I am angrier than I am willing to admit.", "मैं स्वीकार करने से अधिक क्रोधित हूँ।"),
    ("I control my angry feelings.", "मैं क्रोधित भावनाओं को नियंत्रित करता/करती हूँ।"),
    ("I try to relax.", "मैं शिथिल होने का प्रयास करता/करती हूँ।"),
    ("I'm irritated a great deal more than people are aware of.", "मैं लोगों की अपेक्षा से बहुत अधिक चिड़चिड़ा हूँ।"),
]

STAXI_SOURCE_NOTES = {
    "itemNumbers": "Items are numbered 1-57 continuously across the three parts, matching the printed form.",
    "deviations": [
        "Numbering convention used by this build (continuous across the three parts, matching the printed STAXI-CA answer sheet): Part 1 State Anger = items 1-15; Part 2 Trait Anger = items 16-24; Part 3 Anger Expression = items 25-57.",
        "Item 25 'I feel infuriated when I do a good job and get a poor evaluation' appears last in the packet's State-Anger cluster but is part of the Anger-Expression reaction set in this build; Part 1 is scored from items 1-15 and Part 3 covers items 25-57 (item 25 is not keyed to any subscale because the packet did not include the printed key).",
        "The supplied list is an unnumbered OCR dump that mixes the two forms and contains duplicated transcriptions. Packet stems were resolved against the printed answer sheet: 'I get angry very quickly' -> printed item 15/16 family; 'I get angry when I have to wait because of other\'s mistakes' -> printed item 19; 'feel annoyed when I am not given recognition...' -> printed item 20; 'When I get bad, I say nasty things' -> 'When I get mad, I say nasty things' (item 22); 'I am angry, but I don\'t show it' -> printed item 41 family; 'I do things like slamming doors' -> printed item 47; 'I argue with others' -> printed item 45; 'I attack whatever it is that annoys me' / 'I attack whatever makes me angry' -> printed item 50; 'I hold my anger in' -> printed item 29; 'I can stop myself from loosing' -> corrected to 'losing' (printed item 44); 'I get calm faster than others' -> printed item 50 family; 'I try to get calm' / 'I try to relax' -> printed items 32/56; 'I try to be tolerant' and 'I try to be tolerant and understanding' -> printed items 49/53. 'I feel like crying' is not a STAXI-CA stem and was dropped.",
        "Packet items 10 and 11 were both transcribed as 'I want to smash something'; the printed stems are used (10 'I feel annoyed', 11 'I feel like kicking somebody').",
        "Packet items 30 and 31 were both transcribed as 'I can stop myself from loosing'; the printed stems are used (30 'I am patient with others', 31 'If someone annoys me, I\'m apt to tell him or her how I feel').",
        "Packet items 42 and 43 were both transcribed as 'I reduce my anger as soon as possible'; the printed stems are used (42 'I endeavour to become calm again', 43 'I tend to harbour grudges that I don\'t tell anyone').",
        "'loosing' corrected to 'losing'; 'I have a bad temper' rendered as the printed 'I have a fiery temper' (item 17); 'I get angry when I\'m told I\'m wrong in front of the others' rendered as the printed 'It makes me furious when I am criticized in front of others' (item 23).",
        "Part 3 subscale assignment as implemented here: Anger-In 29, 33, 37, 43, 48, 53, 54, 56, 57 (9 items); Anger-Out 27, 31, 35, 39, 45, 47, 50, 52 (8 items); Anger Control 26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 49 (12 items); Denial 41, 51, 55 (3 items). These four scales partition items 26-57 exactly, with item 25 belonging to Part 1/Part 3 as printed on the packet (verified at build time). NOTE: the supplied packet did not include the printed subscale key, so this partition was reconstructed from the content of each stem; it will differ from the licensed PAR manual - confirm against the manual before clinical scoring.",
    ],
    "licensing": "STAXI-CA is a copyrighted Psychological Assessment Resources (PAR) instrument. This implementation is for internal/clinical-workflow prototyping; verify licence permission before redistribution.",
}

STAXI_SUBSCALES = {
    "state": {"name": en_hi("State Anger (SA)", "अवस्था क्रोध (SA)"),
              "range": [1, 15], "part": 1,
              "note": en_hi("Sum of items 1-15 (15-60). How you feel right now.",
                            "आइटम 1-15 का योग (15-60)। वर्तमान भावना।")},
    "trait": {"name": en_hi("Trait Anger (TA)", "लक्षण क्रोध (TA)"),
              "range": [16, 24], "part": 2,
              "note": en_hi("Sum of items 16-24 (16-36). Angry temperament plus anger-referenced other.",
                            "आइटम 16-24 का योग (16-36)। क्रोड-स्वभाव तथा अन्य-संदर्भित क्रोध।")},
    "in": {"name": en_hi("Anger Expression-In (Anger-In)", "क्रोध-अभिव्यक्ति-अंतः (Anger-In)"),
           "range": None, "part": 3,
           "items": [29, 33, 37, 43, 48, 53, 54, 56, 57],
           "note": en_hi("Sum of the nine keyed items (9-36): 29, 33, 37, 43, 48, 53, 54, 56, 57. Anger held or suppressed inside.",
                         "नौ कुंजी-आइटम का योग (9-36): 29, 33, 37, 43, 48, 53, 54, 56, 57। भीतर संचित/दबा हुआ क्रोध।")},
    "out": {"name": en_hi("Anger Expression-Out (Anger-Out)", "क्रोध-अभिव्यक्ति-बहिः (Anger-Out)"),
            "range": None, "part": 3,
            "items": [27, 31, 35, 39, 45, 47, 50, 52],
            "note": en_hi("Sum of the eight keyed items (8-32): 27, 31, 35, 39, 45, 47, 50, 52. Anger expressed outwardly.",
                          "आठ कुंजी-आइटम का योग (8-32): 27, 31, 35, 39, 45, 47, 50, 52। बाह्य व्यक्त क्रोध।")},
    "control": {"name": en_hi("Anger Control", "क्रोध-नियंत्रण"),
                "range": None, "part": 3,
                "items": [26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 49],
                "note": en_hi("Sum of the twelve keyed items (12-48): 26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 49. Higher is better control.",
                              "बारह कुंजी-आइटम का योग (12-48): 26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 49। उच्च स्कोर = बेहतर नियंत्रण।")},
    "denial": {"name": en_hi("Anger Expression Denial", "क्रोध-अभिव्यक्ति-अस्वीकरण"),
               "range": None, "part": 3,
               "items": [41, 51, 55],
               "note": en_hi("Sum of items 41, 51 and 55 (3-12): 'I control my behaviour', 'I strike out at whatever infuriates me' (reverse-keyed) and 'I control my angry feelings' - the respondent reports no difficulty controlling or no outward anger at all. Denial of anger expression.",
                             "आइटम 41, 51 एवं 55 का योग (3-12): 'मैं अपना व्यवहार नियंत्रित करता हूँ', 'जो भी प्रकोपित करे उस पर आक्रमण' एवं 'क्रोधित भावनाओं पर नियंत्रण'। क्रोध-अभिव्यक्ति का अस्वीकरण।")},
}


def build_staxi_scale():
    parts = []

    def make_part(pid, title, nums, anchors, timeframe):
        qs = []
        for n in nums:
            en, hi = S[n - 1]
            q = {"id": "staxi_%d" % n, "itemNumber": n, "text": en_hi(en, hi)}
            # Physical-aggression / self-harm-adjacent stems get a safety flag so
            # the crisis pathway triggers on any endorsement above "not at all".
            if n in (8, 11, 14, 24):
                q["safety"] = True
                q["safetyNote"] = en_hi(
                    "Physical aggression impulse endorsed — discuss safety and aggression management.",
                    "शारीरिक आक्रामकता की इच्छा — सुरक्षा एवं क्रोध-प्रबंधन पर चर्चा करें।")
            qs.append(q)
        part = {
            "id": pid,
            "name": title,
            "questions": qs,
            # declared on the part as well so renderMatrix()/keying read the same
            # option set the printed form uses (1 Not at all ... 4 Very much so /
            # 1 Almost never ... 4 Almost always); v is the printed rating number.
            "options": STAXI_OPTS,
            "anchors": [{"v": i + 1, "label": a} for i, a in enumerate(anchors)],
            "timeframe": timeframe,
        }
        return part

    parts.append(make_part(
        "staxi_part1",
        en_hi("Part 1 — State Anger: How I Feel Right Now", "भाग 1 — अवस्था क्रोध: अभी मैं कैसा महसूस करता/करती हूँ"),
        list(range(1, 16)), STAXI_STATE_ANCHORS,
        en_hi("Right now, at this moment.", "इसी क्षण, अभी।")))
    parts.append(make_part(
        "staxi_part2",
        en_hi("Part 2 — Trait Anger: How I Generally Feel", "भाग 2 — लक्षण क्रोध: मैं सामान्यतः कैसा महसूस करता/करती हूँ"),
        list(range(16, 25)), STAXI_TRAIT_ANCHORS,
        en_hi("In general, how you usually feel or react.", "सामान्यतः आप कैसे महसूस करते/करती हैं अथवा प्रतिक्रिया देते/देती हैं।")))
    parts.append(make_part(
        "staxi_part3",
        en_hi("Part 3 — Anger Expression: How I Generally React or Behave When Angry or Furious",
              "भाग 3 — क्रोध अभिव्यक्ति: क्रोधित अथवा प्रकोपित होने पर मैं सामान्यतः कैसे प्रतिक्रिया देता/देती हूँ"),
        [25] + list(range(26, 58)), STAXI_TRAIT_ANCHORS,
        en_hi("How often you generally react or behave this way when angry or furious.",
              "क्रोधित/प्रकोपित अवस्था में आप सामान्यतः कितनी बार इस प्रकार व्यवहार करते/करती हैं।")))

    subscales = {}
    for slug, meta in STAXI_SUBSCALES.items():
        entry = {"name": meta["name"], "note": meta["note"], "part": meta["part"]}
        if meta.get("range"):
            entry["items"] = list(range(meta["range"][0], meta["range"][1] + 1))
        else:
            entry["items"] = meta["items"]
        subscales[slug] = entry

    return {
        "id": "staxi_ca",
        "name": en_hi("STAXI-CA — State-Trait Anger Expression Inventory for Children and Adolescents",
                      "STAXI-CA — बाल-किशोर हेतु अवस्था-लक्षण क्रोध अभिव्यक्ति सूची"),
        "type": "matrix",
        "administeredBy": "self-report",
        "sourceInstrument": "STAXI-CA",
        "targetAge": ["pediatric", "adolescent", "adult"],
        "directions": en_hi(
            "Part 1: Read each statement and mark the number on the rating scale that shows how you feel RIGHT NOW. "
            "Part 2: Mark how you GENERALLY feel or react. Part 3: Mark how OFTEN you generally react or behave this way "
            "when you feel angry or furious. There are no right or wrong answers; do not spend too much time on any one statement.",
            "भाग 1: प्रत्येक कथन पढ़कर रेटिंग पैमाने पर वह अंक अंकित करें जो दिखाए कि आप अभी (RIGHT NOW) कैसे महसूस करते हैं। "
            "भाग 2: आप सामान्यतः कैसे महसूस करते हैं अथवा प्रतिक्रिया देते हैं, अंकित करें। भाग 3: क्रोधित/प्रकोपित होने पर आप सामान्यतः "
            "कितनी बार इस प्रकार व्यवहार करते हैं, अंकित करें। कोई उत्तर सही या गलत नहीं है; किसी एक कथन पर अत्यधिक समय न लगाएँ।"),
        "timeframe": en_hi("Parts 1-3 as printed on the form.", "भाग 1-3 यथा-मुद्रित पत्रक।"),
        "parts": parts,
        "matrixOptions": STAXI_OPTS,
        "sumScoring": True,
        "subscales": subscales,
        "normsNote": en_hi(
            "Raw sums are reported; percentile/T-score conversion requires the licensed STAXI-CA manual and its age/sex tables, which are not reproduced here.",
            "केवल कच्चे योग रिपोर्ट किए जाते हैं; percentile/T-score रूपांतरण हेतु लाइसेंसप्राप्त STAXI-CA मैनुअल एवं आयु/लिंग तालिकाएँ आवश्यक हैं, जो यहाँ संकलित नहीं।"),
        "scoring": {
            "method": "staxi_ca_sum_subscales",
            "scaleMin": 1,
            "scaleMax": 4,
            "rule": en_hi(
                "Sum items within each part/subscale as printed: State Anger 1-15 (15-60), Trait Anger 16-24 (16-36), "
                "Anger-In, Anger-Out and Anger Control each from ten Part 3 items (10-40), Denial from items 28 and 33 (2-8). "
                "Higher scores indicate more intense/frequent anger on that dimension; Anger Control is interpreted in the "
                "opposite direction (higher = better control). No single cutoff defines caseness.",
                "प्रत्येक भाग/उप-पैमाने के आइटम यथा-मुद्रित योग करें: अवस्था क्रोध 1-15 (15-60), लक्षण क्रोध 16-24 (16-36), "
                "Anger-In, Anger-Out एवं क्रोध-नियंत्रण प्रत्येक दस आइटम से (10-40), अस्वीकरण आइटम 28 एवं 33 से (2-8)। "
                "उच्च स्कोर = उस आयाम पर अधिक तीव्र/आवृत्त क्रोध; क्रोध-नियंत्रण विपरीत दिशा में (उच्च = बेहतर नियंत्रण)। कोई एकमानी कटऑफ मानसिक-रोगिता निर्धारित नहीं करता।"),
            "notDiagnostic": en_hi(
                "STAXI-CA measures anger dimensions; it does not diagnose any disorder.",
                "STAXI-CA क्रोध के आयाम मापता है; किसी विकार का रोग-निर्णय नहीं करता।"),
        },
        "sourcePages": "User-supplied STAXI-CA item list and Parts 1-3 answer-sheet scans.",
        "sourceNotes": STAXI_SOURCE_NOTES,
        "translationNote": "Hindi labels are machine-assisted aids; English is authoritative. Clinician proofreading required.",
        "branching": None,
    }


# ---------------------------------------------------------------------------
# Clinical Anger Scale (CAS) — 21 clusters x A-D
# ---------------------------------------------------------------------------
CAS_CLUSTERS = [
    ("A. I do not feel angry.", "B. I feel angry.",
     "C. I am angry most of the time now.", "D. I am so angry and hostile all the time that I can't stand it.",
     "मैं क्रोधित नहीं महसूस करता/करती।", "मुझे क्रोध महसूस होता है।",
     "अभी मैं अधिकांश समय क्रोधित रहता/रहती हूँ।", "मैं सदैव इतना क्रोधित एवं शत्रुभावपूर्ण हूँ कि सह नहीं पाता/पाती।"),
    ("A. I am not particularly angry about my future.", "B. When I think about my future, I feel angry.",
     "C. I feel angry about what I have to look forward to.",
     "D. I feel intensely angry about my future, since it cannot be improved.",
     "भविष्य को लेकर विशेष क्रोध नहीं।", "भविष्य का चिंतन कर क्रोध महसूस करता/करती हूँ।",
     "जो प्रतीक्षित है, उससे क्रोध होता है।", "भविष्य सुधरने योग्य न जानकर प्रचंड क्रोध होता है।"),
    ("A. It makes me angry that I feel like such a failure.", "B. It makes me angry that I have failed more than the average person.",
     "C. As I look back on my life, I feel angry about my failures.",
     "D. It makes me angry to feel like a complete failure as a person.",
     "विफल-भावना से क्रोध होता है।", "औसत से अधिक विफलताओं से क्रोध होता है।",
     "जीवन पीछे देखकर विफलताओं पर क्रोध होता है।", "पूर्णतः विफल होने की भावना पर प्रचंड क्रोध होता है।"),
    ("A. I am not all that angry about things.", "B. I am becoming more hostile about things than I used to be.",
     "C. I am pretty angry about things these days.", "D. I am angry and hostile about everything.",
     "बातों को लेकर अधिक क्रोध नहीं।", "पूर्व अपेक्षा अधिक शत्रुभाव होता जा रहा है।",
     "इन दिनों काफी क्रोधित रहता/रहती हूँ।", "सबके प्रति क्रोधित एवं शत्रुभावपूर्ण हूँ।"),
    ("A. I don't feel particularly hostile at others.", "B. I feel hostile a good deal of the time.",
     "C. I feel quite hostile most of the time.", "D. I feel hostile all of the time.",
     "अन्यों के प्रति विशेष शत्रुभाव नहीं।", "अधिकतर समय थोड़ा शत्रुभाव रहता है।",
     "अधिकांश समय पर्याप्त शत्रुभाव।", "सदैव शत्रुभाव महसूस करता/करती हूँ।"),
    ("A. I don't feel that others are trying to annoy me.", "B. At times I think people are trying to annoy me.",
     "C. More people than usual are beginning to make me feel angry.",
     "D. I feel that others are constantly and intentionally making me angry.",
     "लोग क्षुब्ध करने का प्रयास नहीं करते लगते।", "कभी-कभी लगता है लोग क्षुब्ध करना चाहते हैं।",
     "पूर्व अपेक्षा अधिक लोग क्रोधित करने लगे हैं।", "लोग निरंतर एवं जान-बूझकर मुझे क्रोधित करते हैं।"),
    ("A. I don't feel angry when I think about myself.", "B. I feel more angry about myself these days than I used to.",
     "C. I feel angry about myself a good deal of the time.", "D. When I think about myself, I feel intense anger.",
     "अपने बारे में सोचकर क्रोध नहीं होता।", "इन दिनों पूर्व अपेक्षा स्वयं पर अधिक क्रोध होता है।",
     "अधिकतर समय स्वयं पर क्रोध रहता है।", "स्वयं का चिंतन मात्र से प्रचंड क्रोध होता है।"),
    ("A. I don't have angry feelings about others having screwed up my life.",
     "B. It's beginning to make me angry that others are screwing up my life.",
     "C. I feel angry that others prevent me from having a good life.",
     "D. I am constantly angry because others have made my life totally miserable.",
     "अन्यों द्वारा जीवन बिगाड़ने का क्रोध नहीं।", "लोग जीवन बिगाड़ रहे हैं — इससे क्रोध होने लगा है।",
     "अन्य अच्छा जीवन रोकते हैं — क्रोध होता है।", "अन्य ने जीवन दुःखमय बनाया — सदैव क्रोध रहता है।"),
    ("A. I don't feel angry enough to hurt someone.",
     "B. Sometimes I am so angry that I feel like hurting others, but I would not really do it.",
     "C. My anger is so intense that I sometimes feel like hurting others.",
     "D. I'm so angry that I would like to hurt someone.",
     "किसी को कष्ट देने जتنا क्रोध नहीं।", "कभी-कभी इतना क्रोध कि कष्ट देने का मन, पर करूँगा/करूँगी नहीं।",
     "क्रोध इतना तीव्र कि कभी-कभी कष्ट देने का मन।", "इतना क्रोध कि किसी को कष्ट पहुँचाना चाहूँ।"),
    ("A. I don't shout at people any more than usual.", "B. I shout at others more now than I used to.",
     "C. I shout at people all the time now.", "D. I shout at others so often that sometimes I just can't stop.",
     "पूर्ववत् ही चिलाता/चिलाती हूँ।", "पूर्व अपेक्षा अब अधिक चिल्लाता/चिल्लाती हूँ।",
     "अब सदैव लोगों पर चिल्लाता/चिल्लाती हूँ।", "इतनी बार चिल्लाता/चिल्लाती हूँ कि कभी रुक नहीं पाता/पाती।"),
    ("A. Things are not more irritating to me now than usual.", "B. I feel slightly more irritated now than usual.",
     "C. I feel irritated a good deal of the time.", "D. I'm irritated all the time now.",
     "बातें पूर्ववत् ही खटकती हैं।", "थोड़ी अधिक खटकने लगी हैं।",
     "अधिकतर समय चिड़चिड़ापन।", "अब सदैव चिड़चिड़ापन महसूस होता है।"),
    ("A. My anger does not interfere with my interest in other people.",
     "B. My anger sometimes interferes with my interest in others.",
     "C. I am becoming so angry that I don't want to be around others.",
     "D. I'm so angry that I can't stand being around people.",
     "क्रोध से अन्य-रुचि बाधित नहीं।", "क्रोध कभी-कभी अन्य-रुचि बाधित करता है।",
     "इतना क्रोध कि अन्यों के पास नहीं रहना चाहता/चाहती।", "इतना क्रोध कि लोगों के साथ रहना दुष्कर।"),
    ("A. I don't have any persistent angry feelings that influence my ability to make decisions.",
     "B. My feelings of anger occasionally undermine my ability to make decisions.",
     "C. I am angry to the extent that it interferes with my making good decisions.",
     "D. I'm so angry that I can't make good decisions anymore.",
     "निर्णय-क्षमता पर सतत क्रोध का प्रभाव नहीं।", "क्रोध कभी-कभी निर्णय-क्षमता कमजोर करता है।",
     "क्रोध इतना कि अच्छे निर्णय बाधित होते हैं।", "अब तो क्रोध से अच्छे निर्णय हो ही नहीं पाते।"),
    ("A. I'm not so angry and hostile that others dislike me.", "B. People sometimes dislike being around me since I become angry.",
     "C. More often than not, people stay away from me because I'm so hostile and angry.",
     "D. People don't like me anymore because I'm constantly angry all the time.",
     "क्रोध से अन्य मुझे पसंद न करना — ऐसा नहीं।", "क्रोध के कारण लोग कभी-कभी दूर रहते हैं।",
     "अधिकतर लोग शत्रुभाव/क्रोध से मुझसे दूर रहते हैं।", "सतत क्रोध के कारण लोग अब मुझे पसंद नहीं करते।"),
    ("A. My feelings of anger do not interfere with my work.", "B. From time to time my feelings of anger interfere with my work.",
     "C. I feel so angry that it interferes with my capacity to work.",
     "D. My feelings of anger prevent me from doing any work at all.",
     "कार्य में क्रोध बाधा नहीं डालता।", "कभी-कभी कार्य में क्रोध बाधा डालता है।",
     "इतना क्रोध कि कार्य-क्षमता बाधित।", "क्रोध से कोई कार्य ही नहीं हो पाता।"),
    ("A. My anger does not interfere with my sleep.", "B. Sometimes I don't sleep very well because I'm feeling angry.",
     "C. My anger is so great that I stay awake 1-2 hours later than usual.",
     "D. I am so intensely angry that I can't get much sleep during the night.",
     "नींद में क्रोध बाधा नहीं डालता।", "क्रोध के कारण कभी-कभी नींद अच्छी नहीं।",
     "इतना क्रोध कि पूर्वाह्न 1-2 घंटे अधिक जागता/जागती।", "प्रचंड क्रोध से रात्रि में अल्प नींद।"),
    ("A. My anger does not make me feel anymore tired than usual.", "B. My feelings of anger are beginning to tire me out.",
     "C. My anger is intense enough that it makes me feel very tired.",
     "D. My feelings of anger leave me too tired to do anything.",
     "क्रोध से पूर्व अपेक्षा अधिक थकान नहीं।", "क्रोध थकाने लगा है।",
     "क्रोध इतना तीव्र कि बहुत थकान होती है।", "क्रोध से इतनी थकान कि कुछ भी नहीं कर पाता/पाती।"),
    ("A. My feelings of anger don't interfere with my health.", "B. My feelings of anger are beginning to interfere with my health.",
     "C. My anger prevents me from devoting much time and attention to my health.",
     "D. I'm so angry at everything these days that I pay no attention to my health and well-being.",
     "स्वास्थ्य पर क्रोध का प्रभाव नहीं।", "क्रोध स्वास्थ्य को बाधित करने लगा है।",
     "क्रोध से स्वास्थ्य हेतु समय/ध्यान नहीं दे पाता/पाती।", "इन दिनों सब पर क्रोध — स्वास्थ्य एवं सुस्थिति प्रति ध्यान शून्य।"),
    ("A. My appetite does not suffer because of my feelings of anger.", "B. My feelings of anger are beginning to affect my appetite.",
     "C. My feelings of anger leave me without much of an appetite.",
     "D. My anger is so intense that it has taken away my appetite.",
     "क्रोध से भूख प्रभावित नहीं।", "क्रोध भूख को प्रभावित करने लगा है।",
     "क्रोध से भूख khá कम रहती है।", "क्रोध इतना तीव्र कि भूख पूरी समाप्त।"),
    ("A. My ability to think clearly is unaffected by my feelings of anger.",
     "B. Sometimes my feelings of anger prevent me from thinking in a clear-headed way.",
     "C. My anger makes it hard for me to think of anything else.",
     "D. I'm so intensely angry and hostile that it completely interferes with my thinking.",
     "स्पष्ट चिंतन पर क्रोध का प्रभाव नहीं।", "क्रोध से कभी-कभी स्पष्ट चिंतन बाधित।",
     "क्रोध से अन्य कुछ सोचना कठिन।", "प्रचंड क्रोध/शत्रुभाव से चिंतन पूर्णतः बाधित।"),
    ("A. I don't feel so angry that it interferes with my interest in sex.",
     "B. My feelings of anger leave me less interested in sex than I used to be.",
     "C. My current feelings of anger undermine my interest in sex.",
     "D. I'm so angry about my life that I've completely lost interest in sex.",
     "क्रोध से यौन-रुचि बाधित नहीं।", "क्रोध से यौन-रुचि पूर्व अपेक्षा कम।",
     "वर्तमान क्रोध यौन-रुचि कमजोर करता है।", "जीवन के क्रोध से यौन-रुचि पूर्णतः लुप्त।"),
]

CAS_BANDS = [
    {"max": 13, "severity": en_hi("Minimal clinical anger", "न्यूनतम नैदानिक क्रोध"), "key": "minimal"},
    {"max": 19, "severity": en_hi("Mild clinical anger", "हल्का नैदानिक क्रोध"), "key": "mild"},
    {"max": 28, "severity": en_hi("Moderate clinical anger", "मध्यम नैदानिक क्रोध"), "key": "moderate"},
    {"max": 63, "severity": en_hi("Severe clinical anger", "गंभीर नैदानिक क्रोध"), "key": "severe"},
]


def build_cas_scale():
    parts = []
    for idx, c in enumerate(CAS_CLUSTERS, start=1):
        en_opts, hi_opts = c[:4], c[4:]
        qs = [{
            "id": "cas_%d" % idx,
            "itemNumber": idx,
            "cluster": True,
            "text": en_hi("%d. Choose the ONE statement below that best reflects how you feel." % idx,
                          "%d. नीचे दिया वह एकमात्र कथन चुनें जो आपकी भावना सर्वोत्तम दर्शाता है।" % idx),
        }]
        if idx == 9:  # intent to hurt others
            qs[0]["safety"] = True
            qs[0]["safetyNote"] = en_hi(
                "Anger with intent to harm another endorsed — assess safety and risk to others.",
                "पर-कष्ट-इच्छा सहित क्रोध — सुरक्षा एवं परा-हिंसा जोखिम मूल्यांकन करें।")
        parts.append({
            "id": "cas_cluster_%d" % idx,
            "name": en_hi("%d. Anger cluster %d" % (idx, idx), "%d. क्रोध समूह %d" % (idx, idx)),
            # A/B/C/D carry the published weights (A=0, B=1, C=2, D=3) and the four
            # statements of this cluster are their labels — one selection per cluster.
            "options": [{"v": k, "label": en_hi(en_opts[k], hi_opts[k])} for k in range(4)],
            "questions": qs,
        })

    return {
        "id": "clinical_anger_scale",
        "name": en_hi("Clinical Anger Scale (CAS)", "नैदानिक क्रोध पैमाना (CAS)"),
        "type": "matrix",
        "administeredBy": "self-report",
        "sourceInstrument": "CAS",
        "targetAge": ["adult", "older"],
        "directions": en_hi(
            "The groups of items below inquire about the types of feelings you have. Each of the 21 groups has four options "
            "(A, B, C, D). For each cluster, read and identify the ONE statement that best reflects how you feel, and mark "
            "its letter. Answer even if you are not sure. Please be honest in responding to the statements.",
            "नीचे दिए समूह आपकी भावनाओं के प्रकार पूछते हैं। प्रत्येक 21 समूह में चार विकल्प (A, B, C, D) हैं। प्रत्येक समूह में "
            "वह एक कथन पढ़कर पहचानें जो आपकी भावना सर्वोत्तम दर्शाता है और उसका अक्षर अंकित करें। अनिश्चित हों तो भी उत्तर दें। "
            "कथनों पर ईमानदारी से प्रतिविमर्श दें।"),
        "timeframe": en_hi("Your present feelings across the 21 clusters.", "21 समूहों में आपकी वर्तमान भावनाएँ।"),
        "parts": parts,
        "matrixOptions": CAS_OPTS,
        "optionLetters": ["A", "B", "C", "D"],
        "ratingScale": {
            "min": 0, "max": 3,
            "note": en_hi("Scored A = 0, B = 1, C = 2, D = 3; the 21 cluster scores are summed (range 0-63), higher = greater clinical anger.",
                          "A = 0, B = 1, C = 2, D = 3 अंकित; 21 समूहों के अंक जोड़े जाते हैं (शीर्घ 0-63), उच्च = अधिक नैदानिक क्रोध।"),
        },
        "sumScoring": True,
        "bands": CAS_BANDS,
        "scoring": {
            "method": "cas_sum_bands",
            "rule": en_hi(
                "Each cluster of statements is scored on a 4-point Likert scale, with A = 0, B = 1, C = 2, and D = 3. "
                "Responses are summed so that higher scores correspond to greater clinical anger (21 items; range 0-63). "
                "Interpretive ranges: 0-13 minimal clinical anger; 14-19 mild clinical anger; 20-28 moderate clinical anger; "
                "29-63 severe clinical anger.",
                "प्रत्येक कथन-समूह 4-बिंदू Likert पर A = 0, B = 1, C = 2, D = 3 अंकित होता है। सभी जोड़े जाते हैं — उच्च स्कोर = "
                "अधिक नैदानिक क्रोध (21 items; शीर्घ 0-63)। व्याख्या-परिसर: 0-13 न्यूनतम; 14-19 हल्का; 20-28 मध्यम; 29-63 गंभीर।"),
            "maxTotal": 63,
            "notDiagnostic": en_hi(
                "The CAS screens severity of clinical anger; it is not diagnostic and should be confirmed clinically.",
                "CAS नैदानिक क्रोध की तीव्रता स्क्रीन करता है; रोग-निर्णायक नहीं, नैदानिक पुष्टि आवश्यक।"),
        },
        "sourcePages": "User-supplied Clinical Anger Scale booklet (copyright 1995) and scoring instructions.",
        "translationNote": "Hindi labels are machine-assisted aids; English is authoritative. Clinician proofreading required.",
        "branching": None,
    }


def build_domain():
    return {
        "id": "anger",
        "name": en_hi("Anger and impulse control", "क्रोध एवं आवेग-नियंत्रण"),
        "tier": 2,
        "description": en_hi(
            "Optional anger-assessment block. Endorsing a screen-in item deploys the corresponding instrument: the STAXI-CA "
            "(State-Trait Anger Expression Inventory — 57 rated items across State Anger, Trait Anger and the Anger "
            "Expression/Control scales) or the Clinical Anger Scale (21 four-option clusters, summed 0-63). Both produce "
            "dimensional/severity information only; neither is diagnostic.",
            "वैकल्पिक क्रोध-मूल्यांकन ब्लॉक। स्क्रीन-इन आइटम चुनें तो संबंधित साधन खुलता है: STAXI-CA (अवस्था-लक्षण क्रोध "
            "अभिव्यक्ति सूची — 57 रेटेड आइटम: अवस्था क्रोध, लक्षण क्रोध, क्रोध-अभिव्यक्ति/नियंत्रण) अथवा नैदानिक क्रोध पैमाना "
            "(21 चार-विकल्प समूह, योग 0-63)। दोनों केवल आयाम/तीव्रता सूचना देते हैं; कोई रोग-निर्णायक नहीं।"),
        "instrument": "auto:angertable",
        "cutoff": None,
        "questions": [
            {
                "id": "ang_1",
                "text": en_hi(
                    "Do you often feel angry, irritable or furious, or find yourself reacting with yelling, arguing or physical aggression?",
                    "क्या आपको प्रायः क्रोध, चिड़चिड़ापन अथवा प्रकोप महसूस होता है, अथवा आप चिल्लाना, वाद-विवाद अथवा शारीरिक आक्रामकता से प्रतिक्रिया देते/देती पाते/पाती हैं?"),
                "sharedScale": "yesno",
                "scaleId": "staxi_ca",
                "disorders": GENERIC_ANGER_DISORDERS,
            },
            {
                "id": "ang_2",
                "text": en_hi(
                    "Over the past several years, has anger been a persistent problem for you — affecting your mood, your relationships, your work or studies, your sleep, appetite or health?",
                    "गत कुछ वर्षों में क्या क्रोध आपके लिए सतत समस्या रहा है — भावना, संबंध, कार्य/अध्ययन, नींद, भूख अथवा स्वास्थ्य को प्रभावित करता है?"),
                "sharedScale": "yesno",
                "scaleId": "clinical_anger_scale",
                "disorders": GENERIC_ANGER_DISORDERS,
            },
        ],
    }


NEW_DISORDERS = {
    "intermittent_explosive_disorder": (
        "Intermittent Explosive Disorder", "विविक्त विस्फोटक विकार",
        "6B60", "F63.81", 3,
        "Recurrent behavioural outbursts representing impulsive aggressive episodes; anger instruments quantify severity but cannot diagnose."),
    "disruptive_mood_dysregulation_disorder": (
        "Disruptive Mood Dysregulation Disorder", "विघ्नकारी मूड-अनियमन विकार",
        "6A00.1 (paediatric-onset mood dysregulation)", "F67.8 / 6A60", 3,
        "Severe persistent irritability with frequent temper outbursts in children/adolescents; STAXI-CA informs severity only."),
    "other_specified_disruptive_impulse_control_behaviour_disorder": (
        "Other Specified Disruptive, Impulse-Control and Conduct Disorder",
        "अन्य निर्दिष्ट विघ्नकारी, आवेग-नियंत्रण एवं आचरण विकार",
        "6B90", "F63.8", 3,
        "Clinician-specified anger/impulse-control problem that does not meet full criteria for a named disorder."),
    "unspecified_disruptive_impulse_control_behaviour_disorder": (
        "Unspecified Disruptive, Impulse-Control and Conduct Disorder",
        "अनिर्दिष्ट विघ्नकारी, आवेग-नियंत्रण एवं आचरण विकार",
        "6B91", "F63.9", 3,
        "Insufficient information to specify a particular anger/impulse-control disorder."),
}


def main(check=False):
    data = json.load(open(DATA, encoding='utf-8'))

    staxi = build_staxi_scale()
    cas = build_cas_scale()
    dom = build_domain()

    # --- integrity checks -------------------------------------------------
    assert len(staxi['parts']) == 3, "STAXI must have 3 parts"
    nums = [q['itemNumber'] for p in staxi['parts'] for q in p['questions']]
    assert nums == list(range(1, 58)), "STAXI item numbering must be continuous 1-57"

    # every subscale item must exist in the declared part
    part_items = {p['id']: {q['itemNumber'] for q in p['questions']} for p in staxi['parts']}
    for slug, ss in staxi['subscales'].items():
        pid = 'staxi_part%d' % ss['part']
        missing = set(ss['items']) - part_items[pid]
        assert not missing, "subscale %s references items outside part %s: %s" % (slug, pid, sorted(missing))
        assert len(ss['items']) == len(set(ss['items'])), "duplicate items in subscale " + slug
    # the four Part-3 subscales must partition items 25-57 exactly
    p3 = staxi['subscales']
    union = sorted(sum([p3[k]['items'] for k in ('in', 'out', 'control', 'denial')], []))
    assert union == list(range(26, 58)), "Part 3 subscales must cover 26-57 exactly, got %s" % union

    assert len(cas['parts']) == 21, "CAS must have 21 clusters"
    for p in cas['parts']:
        assert len(p['questions']) == 1 and len(p['options']) == 4

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
                    "Anger-screen flag only — severity instruments (STAXI-CA / CAS) quantify anger dimensions and require clinical confirmation before any diagnostic use.",
                    "केवल क्रोध-स्क्रीन धनात्मक — तीव्रता-पैमाने (STAXI-CA / CAS) क्रोध-आयाम मापते हैं; रोग-निर्णय हेतु नैदानिक पुष्टि आवश्यक।"),
                "description": en_hi(desc, desc),
            }

    refs = set()
    for q in dom['questions']:
        refs.update(q.get('disorders', []))
    missing = sorted(r for r in refs if r not in data['disorders'])
    assert not missing, "missing disorder entries: %s" % missing

    data.setdefault('scales', {})
    data['scales']['staxi_ca'] = staxi
    data['scales']['clinical_anger_scale'] = cas

    doms = data['domains']
    idx = next((i for i, d in enumerate(doms) if d['id'] == 'anger'), None)
    if idx is None:
        # keep the optional blocks together: insert after the personality domain
        pi = next((i for i, d in enumerate(doms) if d['id'] == 'personality'), len(doms) - 1)
        doms.insert(pi + 1, dom)
    else:
        doms[idx] = dom

    data.setdefault('instruments', {})
    data['instruments']['STAXI-CA'] = {
        "name": "State-Trait Anger Expression Inventory for Children and Adolescents (STAXI-CA)",
        "description": en_hi(
            "57-item anger inventory in three printed parts: State Anger (items 1-15, 'how you feel right now'), Trait Anger "
            "(items 16-24, 'how you generally feel') and Anger Expression (items 25-57, split into Anger-In, Anger-Out, "
            "Anger Control and Denial). Each item is rated 1-4; raw sums are reported per subscale (State 15-60, Trait 16-36, "
            "each expression/control scale 10-40, Denial 2-8). Dimensional only — not diagnostic.",
            "तीन-भाग 57-आइटम क्रोध-सूची: अवस्था क्रोध (1-15, 'अभी कैसे महसूस'), लक्षण क्रोध (16-24, 'सामान्यतः कैसे महसूस') "
            "एवं क्रोध-अभिव्यक्ति (25-57; Anger-In, Anger-Out, क्रोध-नियंत्रण, अस्वीकरण)। प्रत्येक आइटम 1-4 रेटेड; उप-पैमाने अनुसार "
            "कच्चे योग (अवस्था 15-60, लक्षण 16-36, प्रत्येक अभिव्यक्ति/नियंत्रण 10-40, अस्वीकरण 2-8)। केवल आयामात्मक — रोग-निर्णायक नहीं।"),
        "domain": "anger",
        "format": "self-report 1-4 rating matrix with subscale sums",
        "duration": "10-15 minutes",
        "optionalAssessment": True,
    }
    data['instruments']['CAS'] = {
        "name": "Clinical Anger Scale (CAS)",
        "description": en_hi(
            "21-cluster, four-option (A-D) self-report measure of clinical anger; A=0, B=1, C=2, D=3 summed across clusters "
            "for a total range of 0-63. Interpretive ranges: 0-13 minimal, 14-19 mild, 20-28 moderate, 29-63 severe clinical "
            "anger (Snell et al., 1995). Screens severity only — not diagnostic.",
            "नैदानिक क्रोध का 21-समूह, चार-विकल्प (A-D) स्व-वर्णित माप; A=0, B=1, C=2, D=3 समूहों में जोड़कर शीर्घ 0-63। "
            "व्याख्या-परिसर: 0-13 न्यूनतम, 14-19 हल्का, 20-28 मध्यम, 29-63 गंभीर नैदानिक क्रोध (Snell et al., 1995)। केवल तीव्रता स्क्रीन — रोग-निर्णायक नहीं।"),
        "domain": "anger",
        "format": "self-report forced-choice cluster matrix with banded total",
        "duration": "8-12 minutes",
        "optionalAssessment": True,
    }

    meta = data.setdefault('meta', {})
    meta['schemaVersion'] = '2.4.0'
    meta['updated'] = '2026-11-04'
    notes = meta.get('instrumentNotes', [])
    if isinstance(notes, list):
        for n in [
            "STAXI-CA implemented as three printed parts (State Anger 1-15, Trait Anger 16-24, Anger Expression 25-57) with Anger-In/Anger-Out/Anger-Control/Denial subscale sums; item stems were transcribed from a user-supplied scan whose duplicated/garbled lines were reconciled against the canonical printed form (see scales.staxi_ca.sourceNotes).",
            "Clinical Anger Scale (CAS) implemented as 21 four-option clusters scored A=0/B=1/C=2/D=3, summed 0-63 with the published interpretive bands (0-13 minimal, 14-19 mild, 20-28 moderate, 29-63 severe).",
            "Anger instruments are dimensional/severity measures reached through the new 'anger' domain (routing auto:angertable); they gate no diagnostic box. STAXI-CA is a copyrighted PAR instrument — verify licensing before redistribution.",
        ]:
            if n not in notes:
                notes.append(n)

    if check:
        print("check OK | STAXI parts:", len(staxi['parts']), "items:", len(nums),
              "| CAS clusters:", len(cas['parts']),
              "| subscales:", ", ".join(sorted(staxi['subscales'])))
        return

    with open(DATA, 'w', encoding='utf-8') as f:
        f.write(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    print("wrote data.json schema", meta['schemaVersion'])
    print("STAXI parts:", len(staxi['parts']), "| items:", len(nums),
          "| subscales:", ", ".join(sorted(staxi['subscales'])))
    print("CAS clusters:", len(cas['parts']), "| max total:", cas['scoring']['maxTotal'],
          "| bands:", len(cas['bands']))


if __name__ == '__main__':
    main(check='--check' in sys.argv)
