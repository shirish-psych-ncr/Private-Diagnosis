#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_anger.py — Integrate the two anger instruments into the modular data tree:

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

Run:  python3 scripts/build_anger.py            (writes the modular data tree in place)
      python3 scripts/build_anger.py --check    (validate only, no write)
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


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
