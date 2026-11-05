DEP_IDS = ["biss_%d" % i["n"] for i in ITEMS if i["sec"] == "D"]
MAN_IDS = ["biss_%d" % i["n"] for i in ITEMS if i["sec"] == "M"]


def build_scale():
    parts = []
    for sec, pid, pname in (("D", "biss_sec_d", "I. Depression (items 1-20)"),
                            ("M", "biss_sec_m", "II. Mania (items 21-44)")):
        qs = []
        for it in ITEMS:
            if it["sec"] != sec:
                continue
            q = {
                "id": "biss_%d" % it["n"],
                "itemNumber": it["n"],
                "text": bi(None, "%s: %s" % (it["name"], it["defn"])),
                "itemName": bi(None, it["name"]),
                "definition": bi(None, it["defn"]),
                "probes": [bi(None, p) for p in it["probes"]],
                "anchors": [bi(None, a["en"]) for a in ANCHORS[it["n"]]],
            }
            if it.get("safety"):
                q["safety"] = True
            qs.append(q)
        parts.append({"id": pid, "partKey": sec,
                      "name": bi(None, pname), "questions": qs})

    return {
        "id": "biss",
        "name": bi(None, "Bipolar Inventory of Signs and Symptoms Scale (BISS)",
                   "बाइपोलर लक्षण एवं रोगलक्षण मापनी (BISS)"),
        "type": "matrix",
        "administeredBy": "clinician",
        "optionalAssessment": True,
        "sourceInstrument": "BISS",
        "targetAge": ["adult", "adolescent"],
        "directions": bi(None,
            "Items are scored from 0 to 4, based on the most recent 7 day period, utilizing information from self report, and family and clinician observation both outside and during the interview. The anchor statements are examples of behaviors, proportions of time experiencing disturbance, severity of disturbance, and functional impairment that would qualify for a specific score, but do not exclude similar behaviors and internal feelings that would qualify for that score. Items are scored both on the basis of frequency and severity. A score of 3, in most cases, also entails behavior that is observable to others. A score of 0 means the symptom is completely absent. When in doubt between 2 ratings, assign the higher score. Some items in the mania section, e.g. No. 26, Hyperactive, rate behavior that may not have associated impairment of function or adverse consequences. For each defined item, please ask the bolded questions as they are written, or nearly so, for purposes of increasing the consistency of patient responses. The questions in italics are to be asked only if the patient indicates some symptomatology on the bolded general question(s) for the item. Additional questions to those in italics may be needed to establish item severity for individual patients. Rate each item independently. For example, a patient could have both psychomotor slowing (9) and agitation (22) if the behaviors occurred at different times over the rating period. When asking the questions for the item at the top of each page, start with the phrase, \"Over the past week have...\" The Scale lists depressive symptoms first. If the patient is known, or the primary problem area already identified, we recommend commencing the interview with the area of prominent symptomatology and concern to the patient, then completing all remaining sections.",
            None),
        "timeframe": bi(None, "Most recent 7 days.", "अंतिम 7 दिन।"),
        "ratingScale": {"min": 0, "max": 4, "note": bi(None,
            "Each item is rated 0 (absent) to 4 (severe) on the printed anchor set shown beside it; anchors are examples, not an exhaustive list, and when in doubt between two ratings the higher score is assigned.",
            "प्रत्येक आइटम छपाए हुए एंकर-समुच्चय के अनुसार 0 (अनुपस्थित) से 4 (गंभीर) तक रेट किया जाता है; एंकर उदाहरण हैं, पूर्ण सूची नहीं — दो रेटिंगों में संदेह हो तो उच्चतर अंक दें।")},
        "matrixOptions": [
            {"v": 0, "label": bi(None, "0 Absent", "0 अनुपस्थित")},
            {"v": 1, "label": bi(None, "1 Slight", "1 हल्का")},
            {"v": 2, "label": bi(None, "2 Mild", "2 मंद")},
            {"v": 3, "label": bi(None, "3 Moderate", "3 मध्यम")},
            {"v": 4, "label": bi(None, "4 Severe", "4 गंभीर")},
        ],
        "parts": parts,
        "sumScoring": True,
        "scoring": {
            "method": "biss_sectional_severity",
            "scaleMin": 0, "scaleMax": 4,
            "sections": {
                "depression": {"ids": DEP_IDS, "count": len(DEP_IDS), "maxTotal": len(DEP_IDS) * 4},
                "mania": {"ids": MAN_IDS, "count": len(MAN_IDS), "maxTotal": len(MAN_IDS) * 4},
            },
            "positiveItemValue": 2,
            "rule": bi(None,
                "Section totals are the sum of the item scores: Depression items 1-20 (0-80) and Mania items 21-44 (0-96). An item counts as symptomatic at score >= 2 (mild or worse). The published use of the BISS is dimensional - severity of bipolar signs and symptoms over 7 days and change over time - it has no diagnostic cutoff, so no total converts into a diagnosis. Item 4 (suicidality) >= 1 and items 25/39/43 >= 2 require immediate clinical review.",
                "विभाग-योग इतना है: अवसाद आइटम 1-20 (0-80) तथा उन्माद आइटम 21-44 (0-96)। स्कोर >= 2 पर आइटम लक्षणमान्य होता है। BISS का प्रकाशित प्रयोग विमात्मक (7 दिनों में द्विध्रुवी लक्षणों की तीव्रता एवं समय के साथ परिवर्तन) है — इसका कोई नैदानिक कटऑफ नहीं, अतः कुल अंक रोग-निर्णय नहीं बनाता। आइटम 4 >= 1 तथा 25/39/43 >= 2 पर तत्काल चिकित्सकीय समीक्षा आवश्यक।"),
            "disordersOnPositive": [],
            "interpretationNote": bi(None,
                "The BISS was designed to capture the full range of bipolar signs and symptoms rather than to generate a categorical diagnosis; interpret the depression and mania profiles together with the longitudinal course, collateral report and DSM-5/ICD criteria.",
                "BISS वर्गीकृत रोग-निर्णय हेतु नहीं, द्विध्रुवी लक्षणों की सम्पूर्ण श्रेणी पकड़ने हेतु निर्मित है; अवसाद एवं उन्माद प्रोफाइल को दीर्घानुक्रमिक पाठ्यक्रम, सह-सूचना एवं DSM-5/ICD मानदंडों संग पढ़ें।"),
        },
        "safetyItems": ["biss_4", "biss_25", "biss_39", "biss_43"],
        "sourcePages": "BISS (Bowden) version 1.5, 4/1/08, pages 1-7 of 7",
        "translationNote": bi(None,
            "Item text, probes and verbal anchors are the English original. Hindi is provided for the scale title only; the printed instrument is English-language and must be administered in English until a validated translation exists.",
            "आइटम-पाठ, प्रश्न एवं एंकर अंग्रेज़ी मूल से हैं। हिन्दी केवल शीर्षक हेतु; छपा मापनी अंग्रेज़ी में ही प्रयोज्य जब तक मान्यताप्त अनुवाद उपलब्ध न हो।"),
        "licensing": bi(None,
            "Copyright 2005 Charles L. Bowden, MD. Reproduction requires written permission; researchers and clinicians working in nonprofit or publicly owned settings (universities, nonprofit hospitals, government institutions) may make single copies of the BISS for their own use. Confirm the deployment setting qualifies before clinical or research use.",
            "प्रतिलिप्याधिकार 2005, चार्ल्स एल. बोडेन। पुनरुत्पादन हेतु लिखित अनुमति आवश्यक; गैर-लाभकारी/सार्वजनिक संस्थाओं के शोधकर्ता-चिकित्सक स्व-उपयोग हेतु एक प्रति बना सकते हैं। प्रयोग से पूर्व संस्था की पात्रता सुनिश्चित करें।"),
        "disorderKeys": BIPOLAR_DISORDERS,
    }


