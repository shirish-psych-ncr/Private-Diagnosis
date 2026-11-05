def domain_questions():
    """Screen-in items that deploy the BISS from the mood domain."""
    return [
        {
            "id": "mood_biss_1",
            "text": bi(None,
                "Has the person had a distinct period of abnormally elevated, expansive or irritable mood, or a clear history of hypomanic/manic episodes?",
                "क्या व्यक्ति का कोई सुस्पष्ट काल अत्युच्च/प्रसारित/कोपमय मूड का रहा है, या हाइपोमैनिक/मैनिक अवस्था का स्पष्ट इतिहास है?"),
            "sharedScale": "yesno",
            "scaleId": "biss",
            "disorders": ["bipolar_i_disorder", "bipolar_ii_disorder", "other_specified_bipolar"],
        },
        {
            "id": "mood_biss_2",
            "text": bi(None,
                "Is a 7-day severity profile of depressive AND manic symptoms needed to monitor the current episode or treatment response?",
                "क्या वर्तमान अवस्था या चिकित्सा-प्रतिक्रिया की निगरानी हेतु अवसादी एवं उन्मादी लक्षणों का 7-दिवसीय तीव्रता-प्रोफाइल आवश्यक है?"),
            "sharedScale": "yesno",
            "scaleId": "biss",
            "disorders": ["bipolar_depressive", "other_specified_bipolar"],
        },
    ]


def merge(data):
    changed = False
    data["scales"]["biss"] = build_scale()

    mood = next(d for d in data["domains"] if d["id"] == "mood")
    existing_ids = {q["id"] for q in mood["questions"]}
    for q in domain_questions():
        if q["id"] not in existing_ids:
            mood["questions"].append(q)
    # The mood domain keeps its PHQ-9 item scoring, so the BISS screen-ins must
    # not be summed with it: mark the domain as carrying an optional table route.
    if "auto:bipolartable" not in str(mood.get("instrument", "")):
        mood["optionalInstruments"] = (mood.get("optionalInstruments") or []) + \
            [x for x in ["auto:bipolartable"] if x not in (mood.get("optionalInstruments") or [])]

    data["instruments"]["BISS"] = {
        "name": "BISS (Bipolar Inventory of Signs and Symptoms Scale)",
        "construct": bi(None, "Bipolar signs and symptoms - dimensional severity over 7 days",
                        "द्विध्रुवी लक्षण — 7 दिनों की विमात्मक तीव्रता"),
        "format": bi(None, "44 items rated 0-4 by the clinician from self-report, family and interview observation; two sections (Depression 1-20, Mania 21-44)",
                     "44 आइटम, चिकित्सक द्वारा 0-4; दो विभाग (अवसाद 1-20, उन्माद 21-44)"),
        "duration": "~20 min interview",
        "language": {"en": "English", "hi": "अंग्रेज़ी (हिन्दी शीर्षक)"},
        "purpose": bi(None, "Quantify severity of bipolar signs and symptoms and track change; supports staging of an episode and treatment monitoring. Not diagnostic.",
                      "द्विध्रुवी लक्षणों की तीव्रता मापना एवं परिवर्तन-निगरानी; अवस्था-प्रबंधन व चिकित्सा-निगरानी में सहायक। रोग-निर्णायक नहीं।"),
        "source": "BISS, version 1.5 (4/1/08), Charles L. Bowden et al.",
        "licensing": bi(None,
            "Copyright 2005 Charles L. Bowden, MD. Single copies permitted for researchers/clinicians in nonprofit or publicly owned settings; otherwise written permission required.",
            "प्रतिलिप्याधिकार 2005 चार्ल्स एल. बोडेन; गैर-लाभकारी/सार्वजनिक संस्थाओं हेतु एक-प्रति छूट, अन्यथा लिखित अनुमति आवश्यक।"),
    }

    note = ("BISS implemented as scales.biss (Bipolar Inventory of Signs and Symptoms Scale, "
            "Bowden v1.5 4/1/08): 44 clinician-rated items scored 0-4 over the most recent 7 days, "
            "each with its own printed verbal anchors, item definition and probe questions. "
            "Depression section items 1-20 (0-80), Mania section items 21-44 (0-96); an item counts "
            "as symptomatic at >= 2. Dimensional severity measure with no diagnostic cutoff - the "
            "score never produces a bipolar diagnosis, it describes severity and change. Reached "
            "through the mood domain via routing auto:bipolartable. Items 4 (suicidality), 25 "
            "(aggression), 39 (risky behaviour) and 43 (hallucinations) are safety-flagged.")
    notes = data["meta"].setdefault("instrumentNotes", [])
    if note not in notes:
        notes.append(note)

    ver = data["meta"].get("schemaVersion", "")
    if ver == "2.7.0":
        data["meta"]["schemaVersion"] = "2.8.0"
    return data


def main():
    check = "--check" in sys.argv
    data = load_clinical_data()
    before = json.dumps(data, sort_keys=True, ensure_ascii=False)
    data = merge(data)
    after = json.dumps(data, sort_keys=True, ensure_ascii=False)

    assert len(data["scales"]["biss"]["parts"][0]["questions"]) == 20
    assert len(data["scales"]["biss"]["parts"][1]["questions"]) == 24
    for p in data["scales"]["biss"]["parts"]:
        for q in p["questions"]:
            assert len(q["anchors"]) == 5, q["id"]
            assert q["probes"], q["id"]
    for k in BIPOLAR_DISORDERS:
        assert k in data["disorders"], k

    if check:
        print("would write schema %s | BISS items: %d | changed: %s"
              % (data["meta"]["schemaVersion"], 44, before != after))
        return 0
    if before == after:
        print("the modular data tree already up to date (schema %s)" % data["meta"]["schemaVersion"])
        return 0
    save_clinical_data(data)
    print("wrote the modular data tree schema %s | BISS items: 44 (D 20 / M 24)"
          % data["meta"]["schemaVersion"])
    return 0


