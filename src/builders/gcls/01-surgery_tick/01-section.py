          "hi": "पिछले 6 माह में, मेरे लिंग संबंधी कष्ट के कारण (अर्थात् वह कष्ट जो "
              "जन्म के समय सौंपे गए लिंग और मेरी लिंग-पहचान के मेल न खाने से होता है):"},
         [i for i in ITEMS if i[0] <= 13]),
        ("gcls_part2", "gender_experience",
         {"en": "In the past 6 months:", "hi": "पिछले 6 माह में:"},
         [i for i in ITEMS if 14 <= i[0] <= 30]),
        ("gcls_part3", "life_satisfaction",
         {"en": "Next, we would like to know how satisfied you have been with "
               "your life for the last 6 months:",
          "hi": "इसके बाद, हम जानना चाहते हैं कि पिछले 6 माह में आप अपने जीवन से "
              "कितने संतुष्ट रहे:"},
         [i for i in ITEMS if i[0] >= 31]),
    ]
    for pid, key, name, rows in groups:
        questions = []
        for row in rows:
            num, k, en, hi = row[0], row[1], row[2], row[3]
            safety = bool(row[4]) if len(row) > 4 else False
            q = {
                "id": "gcls_%d" % num,
                "itemNumber": num,
                "text": {"en": en, "hi": hi},
            }
            if safety:
                q["safety"] = True
            if k in REVERSED_KEYS:
                q["reverseScored"] = True
            questions.append(q)
            meta[num] = k
        parts.append({"id": pid, "partKey": key, "name": name, "questions": questions})

    # Non-scored clinical note attached to item 26, exactly as printed.
    parts[1]["questions"].append({
        "id": "gcls_surgery_tick",
        "itemNumber": "□",
        "text": {"en": SURGERY_TICK, "hi": SURGERY_TICK_HI},
        "nonScored": True,
        "tickBox": True,
        "linkedItem": 26,
        "note": {"en": "Clinical note — not scored",
                 "hi": "नैदानिक टिप्पणी — अंकित नहीं"},
    })

    subscales = {slug: dict(spec) for slug, spec in SUBSCALES.items()}
    # Explicit item lists (readable and asserted against the item table).
    subscales["functional_impact"]["items"] = list(range(1, 14))
    subscales["body_preoccupation"]["items"] = [14, 15, 17, 18, 19, 21, 23, 24, 26, 27, 28, 29]
    subscales["social_preoccupation"]["items"] = [16, 20, 22, 25, 30]
    subscales["life_satisfaction"]["items"] = list(range(31, 39))
    for slug, spec in subscales.items():
        spec["reversedItems"] = [n for n in spec["items"] if meta[n] in REVERSED_KEYS]
        # Range is derived from the item lists (0-4 per item), never hand-typed.
        spec["minTotal"] = 0
        spec["maxTotal"] = len(spec["items"]) * 4
        assert tuple(spec["range"]) == (spec["minTotal"], spec["maxTotal"]), \
            (slug, spec["range"], spec["maxTotal"])

    total_scored_items = sum(len(p["questions"]) for p in parts) - 1  # minus tick box
    assert total_scored_items == 38, total_scored_items

    return {
        "id": "gcls",
        "name": {
            "en": "Gender Congruence and Life Satisfaction Scale (GCLS)",
            "hi": "लंग-संगति एवं जीवन-संतुष्टि मापनी (GCLS)",
        },
        "type": "matrix",
        "administeredBy": "self-report",
        "optionalAssessment": True,
        "sourceInstrument": "GCLS",
        "targetAge": ["adolescent", "adult"],
        "directions": {
            "en": ("Below is a range of statements about how you might feel in relation "
                   "to your gender, mental well-being, and life satisfaction. Please "
                   "respond to each statement, thinking about how frequently you have "
                   "felt like this in the past 6 months. "
                   "Please note that when talking about 'gender identity' we mean one's "
                   "internal sense of one's self as a man, a woman, or some other gender. "
                   "Please rate each statement as: NEVER (N), RARELY (R), SOMETIMES (S), "
                   "OFTEN (O), or ALWAYS (A)."),
            "hi": ("नीचे आपके लिंग, मानसिक सुख-समता एवं जीवन-संतुष्टि से संबंधित कथनों की "
                   "एक श्रेणी दी गई है। प्रत्येक कथन का उत्तर दें, यह सोचते हुए कि पिछले 6 माह में "
                   "आपने ऐसा कितनी बार अनुभव किया। "
                   "कृपया ध्यान दें कि जब 'लिंग-पहचान' की बात की जाती है, तब इसका अर्थ है किसी का "
                   "अंतर्गत स्व-बोध — पुरुष, महिला या अन्य कोई लिंग के रूप में। "
                   "प्रत्येक कथन का मूल्यांकन करें: कभी नहीं (N), विरल (R), कभी-कभी (S), अक्सर (O), या सदैव (A)।"),
        },
