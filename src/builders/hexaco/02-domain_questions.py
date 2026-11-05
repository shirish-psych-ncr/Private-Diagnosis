def domain_questions():
    """Screen-in item that deploys the observer form from the personality domain."""
    return [
        {
            "id": "per_hexaco_1",
            "text": bi(
                "क्या किसी निकट informants (परिवार/साथी/सहकर्मी) द्वारा व्यक्ति-ता-प्रोफाइल की पर्यवेक्षक-रेटिंग आवश्यक है — आत्म-रिपोर्ट की सीमाओं को आंकने या नैदानिक-सूचना हेतु?",
                "Is an informant-rated personality profile needed — to corroborate or challenge the person's own account, or because self-report alone is insufficient for the referral question?"),
            "scale": [
                {"v": 0, "label": bi("नहीं", "No")},
                {"v": 1, "label": bi("हाँ", "Yes")},
            ],
            "scaleId": "hexaco_pi_r_observer",
            "disorders": [],
        },
    ]


def merge(data):
    changed = False
    data["scales"]["hexaco_pi_r_observer"] = build_scale()

    pers = next((d for d in data["domains"] if d["id"] == "personality"), None)
    assert pers is not None, "personality domain missing - run scripts/build_pd.py first"
    existing_ids = {q["id"] for q in pers["questions"]}
    for q in domain_questions():
        if q["id"] not in existing_ids:
            pers["questions"].append(q)
            changed = True

    inst = data.setdefault("instruments", {})
    if "HEXACO-PI-R (Observer)" not in inst:
        inst["HEXACO-PI-R (Observer)"] = {
            "name": "HEXACO-PI-R Observer Report Form (60 items)",
            "construct": bi("Six-domain personality structure rated by an informant",
                            "पर्यवेक्षक द्वारा रेटित छह-डोमेन व्यक्तित्व-संरचना"),
            "format": bi(
                "60 statements rated 1 (strongly disagree) to 5 (strongly agree) about the person being described; 24 facet scales across 6 domains; R-keyed items reverse-scored; facet = mean of its items, domain = mean of its facets",
                "60 कथन, मूल्यांकन-विषय के विषय में 1 (पूर्णतः असहमत) से 5 (पूर्णतः सहमत) पर रेटित; 6 डोमेनों में 24 फलक-पैमाने; R-कुंजी आइटम व्युक्रम-अंकित; फलक = उसके आइटमों का माध्य, डोमेन = उसके फलकों का माध्य"),
            "duration": "~10-15 min",
            "language": bi("हिन्दी कार्यशील अनुवाद; अंग्रेज़ी मूल प्राधिकृत",
                           "Hindi working translation; English original authoritative"),
            "purpose": bi(
                "Obtain a personality profile from someone who knows the person well, to corroborate or challenge self-report and add observer-level information to the formulation. Descriptive only - it carries no diagnostic cut-offs.",
                "व्यक्ति को अच्छी तरह जानने वाले से व्यक्ति-ता-प्रोफाइल प्राप्त करना — आत्म-रिपोर्ट की पुष्टि/चुनौती एवं रूपरेखा में पर्यवेक्षक-स्तर की सूचना जोड़ना। केवल वर्णनात्मक — कोई नैदानिक कटऑफ नहीं।"),
            "source": "HEXACO-PI-R / HEXACO-60 (Lee & Ashton)",
            "licensing": bi(
                "मूल रूप व स्कोरिंग-कुंजी लेखकों द्वारा मुक्त-उपयोग हेतु प्रकाशित; व्यावसायिक/पुनर्विक्रय उपयोग हेतु अनुमति आवश्यक।",
                "Item wording and scoring key published freely by the authors; commercial or redistributed use requires their permission."),
        }
        changed = True

    ver = data["meta"].get("schemaVersion", "")
    if ver != SCHEMA_TARGET:
        data["meta"]["schemaVersion"] = SCHEMA_TARGET
        notes = data["meta"].setdefault("instrumentNotes", [])
        note = ("HEXACO-PI-R Observer Report Form implemented as scales.hexaco_pi_r_observer "
                "(60 informant-rated items, 1-5 scale, 24 facets across 6 domains, R items "
                "reverse-scored, facet/domain means reported on the 1-5 metric). Descriptive "
                "profile only - no diagnostic cut-offs. Item wording and the scoring key are "
                "those published by Lee & Ashton; confirm licensing terms for the deployment "
                "setting.")
        if note not in notes:
            notes.append(note)
        changed = True
    return changed


def main():
    check = "--check" in sys.argv
    data = load_clinical_data()
    before = json.dumps(data, sort_keys=True, ensure_ascii=False)
    changed = merge(data)
    after = json.dumps(data, sort_keys=True, ensure_ascii=False)

    # integrity assertions
    sc = data["scales"]["hexaco_pi_r_observer"]
    assert len(sc["parts"][0]["questions"]) == 60, "expected 60 observer items"
    assert len(sc["facets"]) == 24, "expected 24 facets"
    assert len(sc["domains"]) == 6, "expected 6 domains"
    used = sorted(n for f in sc["facets"].values() for n in f["items"])
    assert used == list(range(1, 61)), "every item must belong to exactly one facet"
    rev_flagged = sorted(q["itemNumber"] for q in sc["parts"][0]["questions"] if q["reverseScored"])
    assert rev_flagged == sc["scoring"]["reverseItems"], "reverse flags must match the key"
    assert sum(len(v["facets"]) for v in sc["domains"].values()) == 24

    if check:
        print("would write schema %s | HEXACO observer items: 60 | facets: 24 | %s"
              % (data["meta"]["schemaVersion"], "changes pending" if (changed or before != after) else "up to date"))
        return
    save_clinical_data(data)
    print("wrote the modular data tree schema %s | HEXACO observer items: 60 | facets: 24 | domains: 6"
          % data["meta"]["schemaVersion"])


