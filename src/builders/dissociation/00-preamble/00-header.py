#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_dissociation.py — Integrate the two dissociation instruments into the modular data tree:

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

Run:  python3 scripts/build_dissociation.py            (writes the modular data tree in place)
      python3 scripts/build_dissociation.py --check    (validate only, no write)
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


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
