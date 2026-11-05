#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Add the Bipolar Inventory of Signs and Symptoms Scale (BISS, Bowden v1.5 4/1/08)
to the modular data tree.

Idempotent: re-running replaces the BISS structures in place. Supports --check
(dry run, prints what would be written and exits non-zero if a write is needed).

Provenance / licensing
----------------------
BISS is copyright 2005 Charles L. Bowden, MD. The printed form states that no
part may be reproduced without written permission, BUT that "researchers and
clinicians working in nonprofit or publicly owned settings (including
universities, nonprofit hospitals, and government institutions) may make single
copies of a BISS instrument for their own use." That permission is recorded on
the scale object so the deployment context can be checked before use.

Scoring rules encoded here (verbatim from the manual):
  * every item 0-4 over the most recent 7 days, using self-report plus family
    and clinician observation;
  * anchor statements are examples of behaviour / proportion of time / severity
    / functional impairment, not an exhaustive list;
  * items are rated on frequency AND severity; a score of 3 usually entails
    behaviour observable to others; 0 = symptom completely absent;
  * when in doubt between two ratings, assign the HIGHER score;
  * rate each item independently (e.g. 9 psychomotor slowing and 22 agitation
    can both be positive if they occurred at different times);
  * section I Depression = items 1-20, section II Mania = items 21-44.
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

BIPOLAR_DISORDERS = ["bipolar_i_disorder", "bipolar_ii_disorder",
                     "bipolar_depressive", "other_specified_bipolar"]


def bi(name, en, hi=None):
    d = {"en": en}
    if hi:
        d["hi"] = hi
    return d


# ---------------------------------------------------------------- anchors ----
# Verbal anchors transcribed from the printed form (page N of 7). Each item
# carries its OWN anchor list because the wording differs per item.
A = lambda *xs: [{"v": i, "en": x} for i, x in enumerate(xs)]

ANCHORS = {
    1: A("Not at all",
         'Slight; e.g., only occasionally feels "sad" or "down"',
         'Mild; e.g., often feels somewhat "depressed," "blue" or "downhearted," and/or appears sad and is less responsive to positive stimulus',
         'Moderate; e.g., most of the time feels "depressed," and/or several manifestations of sadness with limited ability to brighten up',
         'Severe; e.g., most of the time feels "wretched," sustained gloomy appearance'),
    2: A("Not at all",
         "Slight; e.g., looks dispirited, but brightens up easily",
         "Mild; e.g., more physical manifestations of sadness, and less response to positive stimulus",
         "Moderate; e.g., often appears sad and unhappy",
         "Severe; e.g., extreme and continuous gloom and despondency"),
    3: A("Not at all",
         "Slight; e.g., occasional feelings of discouragement about future",
         "Mild; e.g., often somewhat discouraged",
         "Moderate; e.g., very often feels quite pessimistic about the future",
         "Severe; e.g., pervasive feelings of intense pessimism"),
    4: A("Not at all",
         'Slight; e.g., occasional thoughts of death (without suicidal thoughts), "I would be better off dead" or "I wish I were dead."',
         "Mild; e.g., frequent thoughts of being better off dead or occasional thoughts of suicide but has no plan or intent",
         "Moderate; e.g. often thinks of suicide or has thought of a specific method",
         "Severe; e.g. often thinks of suicide and has thought of a specific plan or has made a suicidal gesture or attempt"),
    5: A("Not at all",
         "Slight; e.g., occasionally worries about some realistic or trivial problem",
         "Mild; e.g., often worries excessively about a problem",
         "Moderate; e.g., very often worries excessively about a realistic or trivial problem",
         "Severe; e.g., most of the time is spent in worrying or brooding about problems which he/she cannot dispel"),
    6: A("Not at all",
         "Slight; e.g., occasional feelings of mild self-blame",
         "Mild; e.g., often feels somewhat guilty about past actions, the significance of which are exaggerated, such as consequences of the illness",
         "Moderate; e.g., often feels quite guilty about past actions or feelings of guilt that cannot be explained",
         "Severe; e.g., pervasive feelings of intense guilt, self-reproach or generalizes feelings of self-blame"),
    7: A("Not at all",
         "Slight; e.g., occasional feelings of inadequacy",
         "Mild; e.g., often feels somewhat inadequate",
         "Moderate; e.g., often feels like a failure",
         "Severe; e.g., pervasive feelings of worthlessness"),
    8: A("Not at all",
         "Slight; e.g., occasional less energy than usual",
         "Mild; e.g., at times definitely more tired, or less energy than usual",
         "Moderate; e.g., most of time is very tired, lacking energy",
         "Severe; e.g., spends most of time resting, nearly always feels fatigued"),
