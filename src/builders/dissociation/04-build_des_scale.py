def build_des_scale():
    qs = []
    for n, (en, hi) in enumerate(D, start=1):
        q = {"id": "desii_%d" % n, "itemNumber": n, "text": en_hi(en, hi)}
        if n in DES_SAFETY_ITEMS:
            q["safety"] = True
            q["safetyNote"] = DES_SAFETY_ITEMS[n]
        qs.append(q)
    assert len(qs) == 28, len(qs)
    return {
        "id": "desii",
        "name": en_hi("Dissociative Experiences Scale — DES-II",
                      "वियोजीय अनुभव पैमाना — DES-II"),
        "type": "matrix",
        "administeredBy": "self-report",
        "optionalAssessment": True,
        "sourceInstrument": "DES-II",
        "targetAge": ["adult", "adolescent"],
        "directions": en_hi(
            "This questionnaire consists of twenty-eight questions about experiences that you may have "
            "in your daily life. We are interested in how often you have these experiences. Your answers "
            "must show how often these experiences happen to you when you are NOT under the influence of "
            "alcohol or drugs. For each item, determine to what degree the described experience applies "
            "to you and mark the number showing the percentage of the time you have the experience "
            "(0% = never, 100% = always).",
            "यह प्रश्नावनी आपके दैनिक जीवन के संभाव्य अनुभवों से संबंधित अट्ठाईस प्रश्नों की है। हमें यह जानना है कि "
            "ये अनुभव आपको कितनी बार होते हैं। उत्तर यह दर्शाएँ कि ये अनुभव शराब या नशे के प्रभाव में न रहते हुए "
            "कितनी बार होते हैं। प्रत्येक प्रश्न हेतु निर्धारित करें कि वर्णित अनुभव आपको किस सीमा तक लागू होता है और "
            "वह प्रतिशत अंकित करें (0% = कभी नहीं, 100% = सदैव)।"),
        "timeframe": en_hi(
            "How often the experiences occur in daily life (not under the influence of alcohol or drugs).",
            "दैनिक जीवन में अनुभव कितनी बार होते हैं (शराब/नशे के प्रभाव में नहीं)।"),
        "parts": [{
            "id": "desii_part1",
            "name": en_hi("Percentage of time the experience happens (0% Never to 100% Always)",
                          "अनुभव कितने प्रतिशत समय होता है (0% कभी नहीं से 100% सदैव तक)"),
            "options": DES_OPTS,
            "anchors": [{"v": 0, "label": en_hi("0% (Never)", "0% (कभी नहीं)")},
                        {"v": 100, "label": en_hi("100% (Always)", "100% (सदैव)")}],
            "questions": qs,
        }],
        "matrixOptions": DES_OPTS,
        "ratingScale": {
            "min": 0, "max": 100,
            "note": en_hi("Each item is answered with the percentage of time the experience happens: "
                          "0% 10 20 30 40 50 60 70 80 90 100% (Never → Always).",
                          "प्रत्येक प्रश्न का उत्तर अनुभव के प्रतिशत समय से: 0% 10 20 30 40 50 60 70 80 90 100% "
                          "(कभी नहीं → सदैव)।"),
        },
        "sumScoring": True,
        "scoring": {
            "method": "desii_mean_percent",
            "indexFormula": en_hi(
                "DES-II total = the mean of the twenty-eight item percentages (0-100).",
                "DES-II कुल = अट्ठाईस आइटम प्रतिशतों का माध्य (0-100)।"),
            "scaleMin": 0,
            "scaleMax": 100,
            "cutoff": 30,
            "rule": en_hi(
                "Sum the twenty-eight item percentages and divide by 28. A mean DES-II score of 30 or "
                "above is the commonly used clinical comparison point and warrants a structured "
                "dissociative-disorder interview; higher means indicate greater dissociative severity. "
                "The DES-II is a screening measure and is not diagnostic on its own.",
                "अट्ठाईस आइटम प्रतिशतों को जोड़कर 28 से भाग दें। 30 या उससे अधिक का माध्य DES-II स्कोर सामान्यतः "
                "प्रयुक्त नैदानिक-तुलना बिंदु है और संरचित वियोजीय-विकार साक्षात्कार हेतु निर्देशित करता है; उच्च माध्य "
                "अधिक वियोजन-तीव्रता दर्शाता है। DES-II स्क्रीनिंग माप है, स्वयं में रोग-निर्णायक नहीं।"),
        },
        "bands": [
            {"max": 9, "severity": en_hi("Low dissociative experiences", "अल्प वियोजीय अनुभव")},
            {"max": 29, "severity": en_hi("Moderate dissociative experiences", "मध्यम वियोजीय अनुभव")},
            {"max": 44, "severity": en_hi("High dissociative experiences (>= 30: clinical comparison point)",
                                          "उच्च वियोजीय अनुभव (≥30: नैदानिक-तुलना बिंदु)")},
            {"max": 100, "severity": en_hi("Very high dissociative experiences", "अत्यंत उच्च वियोजीय अनुभव")},
        ],
        "normsNote": en_hi(
            "No population norms are reproduced here. The >= 30 mean is the widely used clinical "
            "comparison point from the DES-II literature (Carlson & Putnam); interpret alongside the "
            "MID-60 subscale pattern, trauma history and the structured interview.",
            "यहाँ कोई जनसंख्या-नॉर्म पुनःउत्पादित नहीं किए गए। ≥30 माध्य DES-II साहित्य (Carlson & Putnam) का "
            "व्यापक रूप से प्रयुक्त नैदानिक-तुलना बिंदु है; MID-60 उप-पैमाना प्रतिरूप, आघात-इतिहास एवं संरचित "
            "साक्षात्कार के साथ व्याख्या करें।"),
        "sourcePages": "DES-II directions + items 1-28 (supplied packet)",
        "translationNote": en_hi(
            "English item stems are authoritative; Hindi labels are machine-assisted translations for "
            "clinician review and must be proofread by a qualified translator before clinical use.",
            "अंग्रेज़ी कथन प्राधिकृत हैं; हिंदी लेबल चिकित्सक-समीक्षा हेतु यंत्र-सहायित अनुवाद हैं और नैदानिक प्रयोग से "
            "पूर्व योग्य अनुवादक से शुद्धि आवश्यक।"),
        "branching": None,
    }


