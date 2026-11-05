def build_pdq_scale():
    items = []
    for num in range(1, 100):
        q = {
            "id": "pdq_%d" % num,
            "text": en_hi(PDQ_ITEMS[num], PDQ_HI.get(num, PDQ_ITEMS[num])),
            "itemNumber": num,
        }
        if num in SAFETY_ITEMS:
            q["safety"] = True
        if num in (98, 99):
            q["isSectionB"] = True
        items.append(q)

    sectionB = [
        {
            "id": "pdq_98_impulsivity",
            "linkedItem": 98,
            "name": en_hi("Item 98 — Impulsive activities (check those that apply)",
                          "आइटम 98 — आवेगी गतिविधियाँ (लागू होने पर चिह्नित करें)"),
            "options": YESNO,
            "questions": [{"id": pid, "text": en_hi(txt, PDQ_SUBITEM_HI.get(pid, txt))} for pid, txt in PDQ_IMULSE_98],
        },
        {
            "id": "pdq_99_conduct",
            "linkedItem": 99,
            "name": en_hi("Item 99 — Juvenile conduct problems before age 15 (check those that apply)",
                          "आइटम 99 — 15 वर्ष से पूर्व किशोरावस्था की आचरण समस्याएँ (लागू होने पर चिह्नित करें)"),
            "options": YESNO,
            "questions": [{"id": cid, "text": en_hi(txt, PDQ_SUBITEM_HI.get(cid, txt))} for cid, txt in PDQ_CD_99],
        },
    ]

    cs_part = {
        "id": "pdq_clinical_significance",
        "name": en_hi("Clinical Significance Evaluation (mandatory follow-up for each flagged scale)",
                     "नैदानिक महत्व मूल्यांकन (चिह्नित प्रत्येक पैमाने हेतु अनिवार्य अनुवर्ती)"),
        "clinicianRated": True,
        "options": YESNO,
        "questions": [{"id": qid, "text": en_hi(q, PDQ_SUBITEM_HI.get(qid, q)), "criterionNote": note}
                      for qid, q, note in PDQ_CS_QUESTIONS],
    }

    scales_meta = []
    for entry in PDQ_SCALES:
        slug, abbr, name_en, thr, keys, dis = entry[:6]
        sm = {"slug": slug, "profileColumn": abbr, "name": en_hi(name_en, name_en),
              "threshold": thr, "items": keys, "disorders": list(dis)}
        if len(entry) > 6:
            sm["requiresSectionB"] = entry[6]
        scales_meta.append(sm)

    return {
        "id": "pdq4_screen",
        "name": en_hi("PDQ-4+ Personality Questionnaire (99 items)",
                      "PDQ-4+ व्यक्तित्व प्रश्नावली (99 आइटम)"),
        "type": "matrix",
        "administeredBy": "self-report",
        "sourceInstrument": "PDQ-4+",
        "targetAge": ["adult"],
        "directions": en_hi(
            "The purpose of this personality questionnaire is for you to describe the kind of person you are. When answering the questions, think about how you have tended to feel, think, and act over the past several years. Please answer either True or False to each item. T (True) means that the statement is generally true for you. F (False) means that the statement is generally false for you. Even if you are not entirely sure about the answer, indicate T or F for every question. There are no correct answers. You may take as much time as you wish.",
            "इस व्यक्तित्व प्रश्नावली का उद्देश्य आप द्वारा स्व वर्णन है। उत्तर देते समय गत कुछ वर्षों में अपनी भावना, विचार एवं व्यवहार पर विचार करें। प्रत्येक कथन हेतु सत्य अथवा मिथ्या चुनें। T अर्थ आप हेतु सामान्यतः सत्य; F अर्थ सामान्यतः मिथ्या। पूर्ण निश्चितता न हो तो भी प्रत्येक प्रश्न का उत्तर अवश्य दीजिए। कोई सही अथवा गलत उत्तर नहीं है।"),
        "timeframe": en_hi(
            "Answer based on long-standing patterns, not temporary states (e.g., mood episodes, substance use).",
            "दीर्घकालिक रूपों पर उत्तर देें, अस्थायी अवस्थाओं पर नहीं (जैसे मूड एपिसोड, पदार्थ सेवन)।"),
        "parts": [{
            "id": "pdq_items",
            "name": en_hi("Personality Questionnaire Items", "व्यक्तित्व प्रश्नावली आइटम"),
            "questions": items,
        }] + sectionB + [cs_part],
        "matrixOptions": TF,
        # Machine-readable markers consumed by app.js (renderMatrix / computeResults)
        "keyedScoring": True,
        "keying": "pdq4",
        "itemNumberPrefix": True,
        "validity": {
            "items": [
                {"id": "pdq_64", "statement": en_hi("A nuclear war may not be such a bad idea.", "परमाणु युद्ध इतना बुरा विचार न हो।"),
                 "pathologicalResponse": "True",
                 "meaning": en_hi("Suggests random, exaggerated, or invalid responding.",
                                  "यादृच्छिक/ अतिरंजित अथवा अमान्य प्रतिविमर्श सूचित।")},
                {"id": "pdq_76", "statement": en_hi("I have lied a lot on this questionnaire.", "इस प्रश्नावली में मैंने बहुत झूठ बोला है।"),
                 "pathologicalResponse": "True",
                 "meaning": en_hi("Indicates response distortion or poor validity.",
                                  "प्रतिविमर्श विकृति अथवा निम्न वैधता सूचित।")},
            ],
            "rule": en_hi(
                "Before scoring, check these infrequency/validity items. If either is True, interpret results with extreme caution or consider the profile invalid.",
                "अंकन से पूर्व ये अवरण/वैधता आइटम जाँचें। यदि कोई एक सत्य हो तो परिणाम अत्यंत सावधानी से व्याख्यायित करें अथवा प्रोफ़ाइल अमान्य मानें।"),
        },
        "scales": scales_meta,
        "scoring": {
            "method": "pdq4_true_count_thresholds_with_section_b",
            "countRule": en_hi(
                "Count only True responses on the keyed items of each scale. Item 60 appears on both Schizoid and Schizotypal — count it once.",
                "प्रत्येक पैमाने के कुंजी-आइटम में केवल सत्य गनें। आइटम 60 Sczoid एवं Schizotypal दोनों में है — एक वार गनें।"),
            "sectionB": {
                "pdq_98_impulsivity": {"minimum": 2, "gateScale": "Borderline"},
                "pdq_99_conduct": {"minimum": 3, "gateScale": "Antisocial"},
            },
            "clinicalSignificance": en_hi(
                "A PD screen is only clinically significant if criteria A-E (accuracy, duration, pervasiveness, impairment, distress) are ALL met after the initial positive screen. If any criterion fails, the screen is not clinically meaningful (e.g., due to state effects, exaggeration, or transient stress).",
                "प्रारंभिक धनात्मक स्क्रीन पश्चात् A-E (यथार्थता, कालावधि, व्यापकता, बाधा, पीड़ा) सभी मानदंड पूर्त हों तो ही स्क्रीन नैदानिक दृष्ट्या महत्वपूर्ण है। कोई एक असफल तो स्क्रीन नैदानिक दृष्ट्या अर्थहीन।"),
            "comorbidityNote": en_hi(
                "High comorbidity is common (e.g., Borderline + Avoidant + Depressive).",
                "सह-रोगिता सामान्य है (जैसे सीमांत+ परिहरण+ अवसाद)।"),
            "notDiagnosticNote": en_hi(
                "The PDQ-4+ is a self-report screening tool; it is not diagnostic but identifies individuals who may warrant a structured clinical interview for a personality disorder.",
                "PDQ-4+ स्व-वर्णित_स्क्रीनिंग_साधन_है;_रोग-निर्णायक_नहीं,_किंतु_संरचित_नैदानिक_साक्षात्कार_के_पात्र_व्यक्तियों_को_चिह्नित_करता_है।"),
        },
        "sourcePages": "PDQ-4+ instructions, profile sheet and Full Assessment Guide (CURE Counseling & Assessment Training Centre packet)",
        "licensingNote": en_hi(
            "PDQ-4+ content transcribed from the provided packet; verify current licensing/warranties before clinical redistribution.",
            "प्रदत्त पैकेट से अभिलिखित; नैदानिक पुनर्वितरण से पूर्व वर्तमान लाइसेंस सत्यापित करें।"),
        "translationNote": en_hi(
            "English item wording was reconstructed from a low-quality scan; obvious OCR artifacts were repaired and the reconstruction is flagged for clinician review against the published PDQ-4+ form.",
            PDQ_HI_HINT),
    }


