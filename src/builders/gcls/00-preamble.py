#!/usr/bin/env python3
"""
Add the Gender Congruence and Life Satisfaction Scale (GCLS) to the modular data tree.

The GCLS is a 38-item self-report measure of gender-related distress, gender
incongruence and life satisfaction, rated NEVER / RARELY / SOMETIMES / OFTEN /
ALWAYS over the past 6 months, plus one non-scored tick-box recording whether
genital surgery has already been carried out.

This script is idempotent: it rewrites only the `gcls` scale, the `gender`
domain, the two GCLS disorder keys, the instrument-library entry and the meta
notes. Run with --check for a dry run.

    python3 scripts/build_gcls.py [--check]
"""
import json
import sys
from pathlib import Path

SCHEMA_TARGET = "2.7.0"

# --------------------------------------------------------------------------
# Item text — verbatim from the printed scale. `key` is the scored direction:
#   'D'  distress/incongruence item (higher = more distress/incongruence)
#   'C'  congruence item (higher = MORE congruent, therefore reverse-scored)
#   'S'  life-satisfaction item (higher = more satisfied; NOT part of the
#        distress subscales — reported as its own satisfaction register)
#   'R'  satisfaction item worded negatively (reverse-scored within satisfaction)
# --------------------------------------------------------------------------
ITEMS = [
    # --- Part 1: functional impact of gender-related distress (items 1-13) ---
    (1,  'D', 'I have avoided social situations and/or social interactions.',
         'मैंने सामाजिक परिस्थितियों और/अथवा सामाजिक संपर्कों से परहेज़ किया है।'),
    (2,  'D', 'I have not gone to school/college/work.',
         'मैं स्कूल/महाविद्यालय/कार्यस्थल नहीं गया/गई हूँ।'),
    (3,  'D', 'I have not been able to have emotional relationships with other people.',
         'मैं दूसरे लोगों के साथ भावनात्मक संबंध नहीं बना पाया/पाई।'),
    (4,  'D', 'I have suffered from anxiety.',
         'मुझे चिंता का सामना करना पड़ा है।'),
    (5,  'D', 'I have not been able to be physically intimate with other people.',
         'मैं दूसरे लोगों के साथ शारीरिक रूप से निकट नहीं हो पाया/पाई।'),
    (6,  'D', 'I have been unable to leave the house.',
         'मैं घर से बाहर नहीं जा पाया/पाई।'),
    (7,  'D', 'I have found it difficult to make friends.',
         'मुझे मित्र बनाने में कठिनाई हुई है।'),
    (8,  'D', 'I have thought about cutting or hurting my chest, genitals, and/or surrounding areas.',
         'मुझे अपने वक्ष, जननांगों और/अथवा आस-पास के अंगों को काटने या क्षति पहुँचाने का विचार आया है।', True),
    (9,  'D', 'I have felt that life is meaningless.',
         'मुझे लगा कि जीवन निरर्थक है।'),
    (10, 'D', 'I have not enjoyed life.',
         'मैं जीवन का आनंद नहीं ले पाया/पाई।'),
    (11, 'D', 'I have not engaged in leisure activities.',
         'मैं अवकाश गतिविधियों में शामिल नहीं हुआ/हुई।'),
    (12, 'D', 'I have suffered from low mood.',
         'मेरा मूद उदासीन रहा है।'),
    (13, 'D', 'I have thought about hurting myself or taking my own life.',
         'मुझे स्वयं को क्षति पहुँचाने या आत्महत्या करने का विचार आया है।', True),
    # --- Part 2: gender incongruence / body distress (items 14-30) ---
    (14, 'D', 'I have felt distressed when touching my genitals as they do not match my gender identity.',
         'जननांगों को स्पर्श करने पर मुझे कष्ट हुआ क्योंकि वे मेरी लिंग-पहचान से मेल नहीं खाते।'),
    (15, 'D', 'I have felt so distressed about my chest that I have not been able to have a fulfilling life.',
         'अपने वक्ष को लेकर इतना कष्ट अनुभव किया कि मैं संतुष्टिपूर्ण जीवन नहीं जी पाया/पाई।'),
    (16, 'C', 'I have felt comfortable with how others have perceived my gender.',
         'मुझे यह सुखद लगा कि दूसरों ने मेरे लिंग को कैसे देखा/पहचाना।'),
    (17, 'D', 'I have felt that my body hair conflicts with my gender identity, either because I have it and do not like it or because I would like to have it.',
         'मुझे लगा कि मेरे शरीर के बाल मेरी लिंग-पहचान से टकराते हैं — चाहे वे हों और अप्रिय हों, या मैं उन्हें चाहता/चाहती हूँ।'),
    (18, 'D', 'I have felt like my chest does not match my gender identity.',
         'मुझे लगा कि मेरा वक्ष मेरी लिंग-पहचान से मेल नहीं खाता।'),
    (19, 'D', 'I have found it distressing that others do not address me according to my gender identity.',
         'मुझे कष्ट हुआ कि दूसरे मुझे मेरी लिंग-पहचान के अनुसार नहीं संबोधित करते।'),
    (20, 'C', 'I have felt satisfied with the pronouns that others use when talking about me.',
         'मुझे उन सर्वनामों से संतुष्टि महसूस हुई जो दूसरे मेरे बारे में बात करते समय प्रयोग करते हैं।'),
    (21, 'D', 'I have felt unhappy about my genitalia since they do not match my gender identity.',
         'मेरे जननांग मेरी लिंग-पहचान से मेल नहीं खाते, इसलिए मैं उनसे असुखी रहा/रही।'),
    (22, 'C', 'I have felt comfortable with how other people perceive my gender based on my physical appearance.',
         'मुझे सुखद लगा कि मेरे बाह्य स्वरूप के आधार पर दूसरे मेरे लिंग को जिस तरह देखते हैं वैसा ठीक है।'),
    (23, 'D', 'I have felt that my voice has affected the way other people have perceived my gender identity which has been distressing for me.',
         'मुझे लगा कि मेरी आवाज़ ने दूसरों की मेरी लिंग-पहचान की धारणा को प्रभावित किया, जिससे कष्ट हुआ।'),
    (24, 'D', 'I have felt that my facial hair conflicts with my gender identity, either because I have it and do not like it or because I would like to have it.',
         'मुझे लगा कि मेरे चेहरे के बाल मेरी लिंग-पहचान से टकराते हैं — चाहे वे हों और अप्रिय हों, या मैं उन्हें चाहता/चाहती हूँ।'),
    (25, 'C', 'I have felt that my genitals do match with my gender identity.',  # congruence -> reverse-scored
         'मुझे लगा कि मेरे जननांग मेरी लिंग-पहचान से मेल खाते हैं।'),
    (26, 'D', 'I have felt that genital surgery will address the unhappiness I experience in relation to my gender.',
         'मुझे लगा कि जननांग-शस्त्रक्रिया मेरे लिंग से जुड़े असुख को दूर कर सकेगी।'),
    (27, 'D', 'I have been unable to have a fulfilling life because of the distress relating to my genitalia.',
         'मेरे जननांगों से जुड़े कष्ट के कारण मैं संतुष्टिपूर्ण जीवन नहीं जी पाया/पाई।'),
    (28, 'D', 'I have felt extremely distressed when looking at my chest.',
         'अपना वक्ष देखकर मुझे अत्यंत कष्ट हुआ।'),
    (29, 'D', 'I have felt extremely distressed when looking at my genitals.',
         'अपने जननांग देखकर मुझे अत्यंत कष्ट हुआ।'),
    (30, 'C', 'I have felt satisfied with my chest.',
         'मुझे अपने वक्ष से संतुष्टि महसूस हुई।'),
    # --- Part 3: life satisfaction (items 31-38) ---
    (31, 'S', 'I have felt satisfied at school/college/work.',
         'मुझे स्कूल/महाविद्यालय/कार्यस्थल में संतुष्टि महसूस हुई।'),
    (32, 'S', 'I have felt satisfied with my emotional relationship(s).',
         'मुझे अपने भावनात्मक संबंधों/संबंध से संतुष्टि महसूस हुई।'),
    (33, 'S', 'I have felt satisfied with my sex life.',
         'मुझे अपने यौन जीवन से संतुष्टि महसूस हुई।'),
    (34, 'S', 'I have felt satisfied in my leisure activities and hobbies.',
         'मुझे अपनी अवकाश गतिविधियों और शौकों से संतुष्टि महसूस हुई।'),
    (35, 'R', 'I have not felt satisfied with my friends.',
         'मुझे अपने मित्रों से संतुष्टि महसूस नहीं हुई।'),
    (36, 'S', 'I have felt satisfied with the support I have received from other significant people.',
         'मुझे अन्य महत्वपूर्ण व्यक्तियों से प्राप्त सहयोग से संतुष्टि महसूस हुई।'),
    (37, 'R', 'I have not felt satisfied with my health.',
         'मुझे अपने स्वास्थ्य से संतुष्टि महसूस नहीं हुई।'),
    (38, 'S', 'I have felt satisfied with life in general.',
         'मुझे सामान्यतः जीवन से संतुष्टि महसूस हुई।'),
]


from clinical_data import load_clinical_data, save_clinical_data, save_interview
