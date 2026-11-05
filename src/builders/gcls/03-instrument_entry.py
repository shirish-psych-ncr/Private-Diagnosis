INSTRUMENT_ENTRY = {
    "name": "GCLS (Gender Congruence and Life Satisfaction Scale)",
    "construct": {"en": "Gender congruence, gender-related distress & life satisfaction",
                  "hi": "लंग-संगति, लिंग-संबंधी कष्ट एवं जीवन-संतुष्टि"},
    "format": {"en": "38 items rated Never-Rarely-Sometimes-Often-Always (0-4) over 6 months, "
                     "+ 1 non-scored genital-surgery tick-box; 4 subscales",
               "hi": "38 आइटम, कभी नहीं–सदैव (0-4), 6 माह, + 1 अ-अंकित जननांग-शस्त्रक्रिया चिह्न; 4 उप-पैमाने"},
    "duration": "~10 min",
    "language": {"en": "English, Hindi", "hi": "अंग्रेज़ी, हिन्दी"},
    "purpose": {"en": "Quantify gender-related distress, body and social preoccupation and "
                      "life satisfaction; supports assessment and outcome monitoring.",
                "hi": "लिंग-संबंधी कष्ट, शारीरिक व सामाजिक आसक्ति तथा जीवन-संतुष्टि का परिमाणीकरण; "
                      "मूल्यांकन एवं परिणाम-निगरानी में सहायक।"},
    "source": "Gender Congruence and Life Satisfaction Scale (GCLS)",
    "licensing": {"en": "Confirm permission terms with the rights holder before clinical or "
                        "research use.",
                  "hi": "नैदानिक/शोध-प्रयोग से पूर्व अधिकार-वाहक से अनुमति-शर्तें पुष्टि करें।"},
}


def main():
    check = "--check" in sys.argv
    data = load_clinical_data()

    data.setdefault("scales", {})["gcls"] = build_scale()

    domains = data["domains"]
    for i, d in enumerate(domains):
        if d["id"] == "gender":
            domains[i] = build_domain()
            break
    else:
        domains.append(build_domain())

    for k, v in DISORDERS_TO_ADD.items():
        data["disorders"].setdefault(k, v)

    data["instruments"]["GCLS"] = INSTRUMENT_ENTRY

    notes = data["meta"].setdefault("instrumentNotes", [])
    note = ("GCLS implemented as scales.gcls (Gender Congruence and Life Satisfaction Scale; "
            "38 items rated Never=0 to Always=4 over the past 6 months, plus one non-scored "
            "genital-surgery tick-box linked to item 26). Four subscales with reverse-keyed "
            "positively worded items (16, 20, 22, 30 congruence; 35, 37 negative satisfaction): "
            "functional impact 1-13, body preoccupation 14/15/17/18/19/21/23/24/26/27/28/29, "
            "social preoccupation 16/20/22/30, life satisfaction 31-38 reported separately "
            "(higher = more satisfied). Reached through the new 'gender' domain via routing "
            "auto:genderdistress. Items 8 and 13 are safety-flagged (chest/genital self-harm "
            "and suicidal ideation) and open the crisis pathway. Dimensional screen only — it "
            "never diagnoses gender incongruence, and gender diversity alone is not a disorder.")
    if note not in notes:
        notes.append(note)

    data["meta"]["schemaVersion"] = SCHEMA_TARGET
    data["meta"]["updated"] = "2026-11-04"

    # sanity assertions
    s = data["scales"]["gcls"]
    scored = [q for p in s["parts"] for q in p["questions"] if not q.get("nonScored")]
    assert len(scored) == 38, len(scored)
    # Item 25 ("I have felt that my genitals DO match with my gender identity") is
    # positively worded like 16/20/22/30 and is reverse-keyed too; items 35/37 are the
    # negatively worded satisfaction stems ("I have NOT felt satisfied...").
    REVERSED_ITEMS = (16, 20, 22, 25, 30, 35, 37)
    assert all(("reverseScored" in q) == (q["itemNumber"] in REVERSED_ITEMS)
               for q in scored), "reverse key mismatch: %s" % [
                   q["itemNumber"] for q in scored
                   if ("reverseScored" in q) != (q["itemNumber"] in REVERSED_ITEMS)]
    covered = set()
    for spec in s["subscales"].values():
        covered.update(spec["items"])
    assert covered == set(range(1, 39)), sorted(set(range(1, 39)) - covered)

    if check:
        print("would write schema %s | gcls items: %d | subscales: %d | domains: %d"
              % (SCHEMA_TARGET, len(scored), len(s["subscales"]), len(data["domains"])))
        return

    save_clinical_data(data)
    print("wrote the modular data tree schema %s | gcls items: %d | subscales: %d | domains: %d"
          % (SCHEMA_TARGET, len(scored), len(s["subscales"]), len(data["domains"])))


if __name__ == "__main__":
    main()
