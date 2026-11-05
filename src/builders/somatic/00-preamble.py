#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integrate the somatic-symptom / factitious-disorder material into the modular data tree.

Adds, idempotently:

  scales.fac22_sr   FAC22-SR (Senthil & Prabhakar, 2019) — 22-item Yes/No
                    self-report screen for factitious disorder, keyed exactly
                    as printed ("Score 1 each for Yes to items 5, 8, 10, 11,
                    14-22, and No to items 1-4, 6, 7, 9, 12 and 13"; 9-14
                    possible FD, 15+ probable FD).
  scales.phq15      PHQ-15 — 15-item somatic symptom severity index (0/1/2),
                    cut-points 0-4 / 5-9 / 10-14 / 15+.
  domains.somatic   Tier-2 domain with two screen-in items that deploy the two
                    instruments through `instrument: "auto:somatoptable"`.
  disorders         somatic_symptom_disorder, factitious_disorder,
                    conversion_disorder (if absent).
  instruments       FAC22-SR and PHQ-15 library entries.
  reference.malingering   Non-scored clinical reference notes drawn from the
                    supplied forensic handbook extract (definitions, FD, Ganser,
                    malingered depression / hallucinations / delusions / amnesia,
                    and the pathway-to-violence table).

Run:  python3 scripts/build_somatic.py [--check]
"""
import json, sys, copy, io, os



def en_hi(en, hi):
    return {"en": en, "hi": hi}


# ---------------------------------------------------------------------------
# FAC22-SR item text (verbatim from Table 7; OCR artifacts repaired)
# keying: 'T' = a YES answer scores 1, 'F' = a NO answer scores 1
# ---------------------------------------------------------------------------
FAC22_ITEMS = [
    # (number, English stem, key)
    (1,  "With my physical symptoms, I affirm being referred for psychiatric counselling today.", 'F'),
    (2,  "I do agree that others find my symptoms atypical and unusually recurring.", 'F'),
    (3,  "I do think that because my symptoms are so mild/trivial, physicians often miss their significance and seriousness.", 'F'),
    (4,  "I would be happy if I can suddenly find myself sprightly healthy and strong.", 'F'),
    (5,  "I would be anxious if I find my family members had left for their work as/if I appear healthy to them.", 'T'),
    (6,  "It is just chance that people fail to notice or weren't around, every time when I experienced these symptoms.", 'F'),
    (7,  "I would pull myself up to help (with errands or earning) a family member more sick than me.", 'F'),
    (8,  "(If I had to play in a video game or a stage play) I would prefer portraying an injured warrior dying in bed, than one left unattended in battle.", 'T'),
    (9,  "I usually feel timid and offended when a stranger offers to help me.", 'F'),
    (10, "I am eager and brave enough to undergo painful bodily investigations.", 'T'),
    (11, "I would prefer crying or lamenting to a close friend, than crying alone.", 'T'),
    (12, "I feel giddy or immobilised often when I get emotional when alone.", 'F'),
    (13, "I would feel ashamed if people find about my physical illness.", 'F'),
    (14, "I often get gloomy, unsatisfied or irritable on the day of my discharge from hospital.", 'T'),
    (15, "I might not have accessed the physician but for the erratic concern shown by my family members/friend(s).", 'T'),
    (16, "I find my clinical tests and lab investigations done too casually to get any positive result.", 'T'),
    (17, "I feel unsatisfied and deprived when the health professionals show lesser than usual interest in talking with me.", 'T'),
    (18, "I understand that people with my symptoms may or may not be hearing voices when alone, either transiently or regularly. I hear such voices too.", 'T'),
    (19, "I understand that people with my symptoms may or may not have visual loss, either momentarily or regularly. I have had visual loss too.", 'T'),
    (20, "I understand that people with my symptoms may or may not have weakness/abnormal movements of one or more limbs, either momentarily or continuously. I have had such weakness/abnormal movements too.", 'T'),
    (21, "I have encountered interesting adventures that had been brilliant and wonderful, and/or a series of heartbreaking tragic events including multiple personal crises - many times victimizing me.", 'T'),
    (22, "Wherever I go, many a time I have had the pleasure of playing a hero/heroine of those circumstances and had been wondered at and hailed as a saviour by the people there.", 'T'),
]

# Hindi renderings are working translations pending proofreading by a
# bilingual clinician (flagged in translationNote).
FAC22_HI = {
    1: "अपने शारीरिक लक्षणों के साथ, आज मुझे मनोचिकित्सकीय परामर्श हेतु भेजे जाने में मैं सहमत हूँ।",
    2: "मैं स्वीकार करता/करती हूँ कि अन्य लोगों को मेरे लक्षण असामान्य एवं बारम्बार लगते हैं।",
    3: "मुझे लगता है कि मेरे लक्षण अत्यंत तुच्छ होने के कारण चिकित्सक अक्सर उनके महत्व एवं गंभीरता को उपेक्षित कर देते हैं।",
    4: "यदि मैं अचानक पूर्णतः स्वस्थ व बलिष्ठ पाऊँ तो मुझे प्रसन्नता होगी।",
    5: "यदि मुझे दिखने में स्वस्थ पाकर मेरे परिवारजन कार्य हेतु चले जाएँ तो मुझे चिंता होगी।",
    6: "यह केवल संयोग है कि हर बार इन लक्षणों के अनुभव के समय लोग मौजूद नहीं थे या उन्होंने ध्यान नहीं दिया।",
    7: "मुझसे अधिक बीमार परिवार-सदस्य की सहायता (कार्यों या कमाई में) के लिए मैं खुद को उठा लाऊँगा/उठा लाऊँगी।",
    8: "(यदि मुझे किसी वीडियो गेम या रंगमंच में भाग लेना हो) तो मैं शয्ये पर मरता हुआ घायल योद्धा की भूमिका करने को मैं युद्धभूमि में अनदेखा किए गए सैनिक के रूप निभाने से अधिक प्रिय मानूँगा/मानूँगी।",
    9: "जब कोई अपरिचित व्यक्ति सहायता की पेशकश करता है तो मैं सामान्यतः संकोची एवं आहत महसूस करता/करती हूँ।",
    10: "पीड़ादायक शारीरिक जाँचों से गुज़रने के लिए मैं उत्सुक एवं साहसी हूँ।",
    11: "अकेले रोने के बजाय किसी निकट मित्र से रोना या विलाप करना मुझे अधिक अधिक प्रिय लगता है।",
    12: "अकेले भावुक होते ही प्रायः मुझे चक्कर आता है या मैं स्तब्ध हो जाता/जाती हूँ।",
    13: "यदि लोग मेरी शारीरिक बीमारी के बारे में जान लें तो मुझे लज्जा आएगी।",
    14: "अस्पताल से छुट्टी के दिन मैं प्रायः विषण्ण, असंतुष्ट या चिड़चिड़ा हो जाता/हो जाती हूँ।",
    15: "परिवारजनों/मित्रों द्वारा दिखाई गई उलटी-सीधी चिंता न होती तो शायद मैं चिकित्सक के पास न जाता/जाती।",
    16: "मुझे लगता है कि मेरे नैदानिक परीक्षण एवं जाँचें इतनी सावधानी-विहीन ढंग से की जाती हैं कि उनसे सकारात्मक परिणाम नहीं मिलता।",
    17: "स्वास्थ्य-विशेषज्ञों द्वारा मेरी बातचीत में अपेक्षाकृत कम रुचि दिखाने पर मैं असंतुष्ट एवं वंचित महसूस करता/करती हूँ।",
    18: "मुझे ज्ञात है कि मेरे जैसे लक्षण वाले लोग एकान्त में आवाज़ें सुन सकते हैं या नहीं, क्षणिक या नियमित। मुझे भी ऐसी आवाज़ें सुनाई देती हैं।",
    19: "मुझे ज्ञात है कि मेरे जैसे लक्षण वाले लोगों को क्षणिक या नियमित दृष्टि-हानि हो सकती है। मुझे भी दृष्टि-हानि हुई है।",
    20: "मुझे ज्ञात है कि मेरे जैसे लक्षण वाले एक या अधिक अंगों में क्षणिक या सतत दुर्बलता/असामान्य गतियाँ हो सकती हैं। मुझे भी ऐसी दुर्बलता/असामान्य गतियाँ हुई हैं।",
    21: "मेरे जीवन में रोमांचक, दिव्य अनुभव भी रहे हैं और हृदयविदारक श्रृंखलाबद्ध दुर्घटनाएँ भी — जिनमें अनेक बार मैं पीड़ित बना।",
    22: "जहाँ-जहाँ मैं गया/गई, अनेक बार मैं उन परिस्थितियों का नायक/नायिका बनकर सबका ध्यान आकर्षित करता/करती रहा/रही और लोगों ने मुझे तारीफ़ की।",
}


from clinical_data import load_clinical_data, save_clinical_data, save_interview
