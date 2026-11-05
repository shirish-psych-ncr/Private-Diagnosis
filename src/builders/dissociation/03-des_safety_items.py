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


