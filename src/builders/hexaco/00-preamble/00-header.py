#!/usr/bin/env python3
"""
Add the HEXACO-PI-R Observer Report Form to the modular data tree.

The HEXACO-PI-R observer form is a 60-item other-report measure of the six
HEXACO personality domains (Honesty-Humility, Emotionality, Extraversion,
Agreeableness, Conscientiousness, Openness to Experience), rated on a 1-5
agree/disagree scale by someone who knows the person being described. Each
domain has four facets; items marked R are reverse-scored. Facet score = mean
of its (reversed where keyed) raw items; domain score = mean of its facet
scores. The form is published freely by the authors (Lee & Ashton) at
hexaco.org, so item wording is reproduced verbatim.

This script is idempotent: it rewrites only the `hexaco_pi_r_observer` scale,
the `personality` domain's attached screen-in item, the instrument-library
entry and the meta notes. Run with --check for a dry run.

    python3 scripts/build_hexaco.py [--check]
"""
import json
import sys
from pathlib import Path

SCHEMA_TARGET = "2.9.0"


def bi(hi, en):
    return {"en": en, "hi": hi}


# --------------------------------------------------------------------------
# Items — verbatim from the printed OBSERVER report form. `n` is the printed
# item number, `rev` marks the items the scoring guide keys as R (reverse).
# --------------------------------------------------------------------------
ITEMS = [
    (1,  "He/she would be quite bored by a visit to an art gallery.",
               "वह/वो कला-दीर्घा देखने से बिल्कुल ऊब जाएगा/जाएगी।"),
    (2, "He/she cleans his/her office or home quite frequently.",
               "वह/वो अपना कार्यालय या घर बहुत अक्सर साफ़ करता/करती है।"),
    (3, "He/she rarely holds a grudge, even against people who have badly wronged him/her.",
               "वह/वो बुरी तरह ठगा गया हो तब भी शिकायत/द्वेष बहुत कम रखता/रखती है।"),
    (4, "He/she feels reasonably satisfied with himself/herself overall.",
               "वह/वो समग्र रूप से स्वयं से यथेष्ट संतुष्ट महसूस करता/करती है।"),
    (5, "He/she would feel afraid if he/she had to travel in bad weather conditions.",
               "वह/वो खराब मौसम में यात्रा करनी हो तो डरेगा/डरेगी।"),
    (6, "If he/she wants something from a person he/she dislikes, he/she will act very nicely toward that person in order to get it.",
               "जिस व्यक्ति को वह/वो पसंद नहीं करता/करती, उससे कुछ चाहिए हो तो पाने हेतु उसके साथ बड़ा मिलनसार व्यवहार करेगा/करेगी।"),
    (7, "He/she is interested in learning about the history and politics of other countries.",
               "वह/वो अन्य देशों के इतिहास एवं राजनीति जानने में रुचि रखता/रखती है।"),
    (8, "When working, he/she often sets ambitious goals for himself/herself.",
               "कार्य करते समय वह/वो अक्सर स्वयं के लिए महत्वाकांक्षी लक्ष्य निर्धारित करता/करती है।"),
    (9,  "People sometimes say that he/she is too critical of others.",
               "लोग कभी-कभी कहते हैं कि वह/वो दूसरों की अधिक आलोचना करता/करती है।"),
    (10,  "He/she rarely expresses his/her opinions in group meetings.",
               "वह/वो सामूहिक बैठकों में अपना मत बहुत कम व्यक्त करता/करती है।"),
    (11, "He/she worries about little things.",
               "वह/वो छोटी-छोटी बातों की चिंता करता/करती है।"),
    (12,  "If he/she knew that he/she could never get caught, he/she would be willing to steal a million dollars.",
               "पकड़े जाने की सम्भावना न हो तो वह/वो दस लाख रुपये चुराने को तैयार होगा/होगी।"),
    (13, "He/she would like a job that requires following a routine rather than being creative.",
               "वह/वो रचनात्मकता के बजाय दिनचर्या-पालन वाली नौकरी पसंद करेगा/करेगी।"),
    (14, "He/she often checks his/her work over repeatedly to find any mistakes.",
               "वह/वो त्रुटियाँ खोजने हेतु अपना कार्य बार-बार जाँचता/जाँचती है।"),
