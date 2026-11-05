#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_pd.py — Integrate the personality-disorder instruments into the modular data tree:

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

Run:  python3 scripts/build_pd.py            (writes the modular data tree in place)
      python3 scripts/build_pd.py --check    (validate only, no write)
"""
import json, sys, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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

from clinical_data import load_clinical_data, save_clinical_data, save_interview
