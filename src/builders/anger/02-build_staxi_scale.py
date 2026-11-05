def build_staxi_scale():
    parts = []

    def make_part(pid, title, nums, anchors, timeframe):
        qs = []
        for n in nums:
            en, hi = S[n - 1]
            q = {"id": "staxi_%d" % n, "itemNumber": n, "text": en_hi(en, hi)}
            # Physical-aggression / self-harm-adjacent stems get a safety flag so
            # the crisis pathway triggers on any endorsement above "not at all".
            if n in (8, 11, 14, 24):
                q["safety"] = True
                q["safetyNote"] = en_hi(
                    "Physical aggression impulse endorsed — discuss safety and aggression management.",
                    "शारीरिक आक्रामकता की इच्छा — सुरक्षा एवं क्रोध-प्रबंधन पर चर्चा करें।")
            qs.append(q)
        part = {
            "id": pid,
            "name": title,
            "questions": qs,
            # declared on the part as well so renderMatrix()/keying read the same
            # option set the printed form uses (1 Not at all ... 4 Very much so /
            # 1 Almost never ... 4 Almost always); v is the printed rating number.
            "options": STAXI_OPTS,
            "anchors": [{"v": i + 1, "label": a} for i, a in enumerate(anchors)],
            "timeframe": timeframe,
        }
        return part

    parts.append(make_part(
        "staxi_part1",
        en_hi("Part 1 — State Anger: How I Feel Right Now", "भाग 1 — अवस्था क्रोध: अभी मैं कैसा महसूस करता/करती हूँ"),
        list(range(1, 16)), STAXI_STATE_ANCHORS,
        en_hi("Right now, at this moment.", "इसी क्षण, अभी।")))
    parts.append(make_part(
        "staxi_part2",
        en_hi("Part 2 — Trait Anger: How I Generally Feel", "भाग 2 — लक्षण क्रोध: मैं सामान्यतः कैसा महसूस करता/करती हूँ"),
        list(range(16, 25)), STAXI_TRAIT_ANCHORS,
        en_hi("In general, how you usually feel or react.", "सामान्यतः आप कैसे महसूस करते/करती हैं अथवा प्रतिक्रिया देते/देती हैं।")))
    parts.append(make_part(
        "staxi_part3",
        en_hi("Part 3 — Anger Expression: How I Generally React or Behave When Angry or Furious",
              "भाग 3 — क्रोध अभिव्यक्ति: क्रोधित अथवा प्रकोपित होने पर मैं सामान्यतः कैसे प्रतिक्रिया देता/देती हूँ"),
        [25] + list(range(26, 58)), STAXI_TRAIT_ANCHORS,
        en_hi("How often you generally react or behave this way when angry or furious.",
              "क्रोधित/प्रकोपित अवस्था में आप सामान्यतः कितनी बार इस प्रकार व्यवहार करते/करती हैं।")))

    subscales = {}
    for slug, meta in STAXI_SUBSCALES.items():
        entry = {"name": meta["name"], "note": meta["note"], "part": meta["part"]}
        if meta.get("range"):
            entry["items"] = list(range(meta["range"][0], meta["range"][1] + 1))
        else:
            entry["items"] = meta["items"]
        subscales[slug] = entry

    return {
        "id": "staxi_ca",
        "name": en_hi("STAXI-CA — State-Trait Anger Expression Inventory for Children and Adolescents",
                      "STAXI-CA — बाल-किशोर हेतु अवस्था-लक्षण क्रोध अभिव्यक्ति सूची"),
        "type": "matrix",
        "administeredBy": "self-report",
        "sourceInstrument": "STAXI-CA",
        "targetAge": ["pediatric", "adolescent", "adult"],
        "directions": en_hi(
            "Part 1: Read each statement and mark the number on the rating scale that shows how you feel RIGHT NOW. "
            "Part 2: Mark how you GENERALLY feel or react. Part 3: Mark how OFTEN you generally react or behave this way "
            "when you feel angry or furious. There are no right or wrong answers; do not spend too much time on any one statement.",
            "भाग 1: प्रत्येक कथन पढ़कर रेटिंग पैमाने पर वह अंक अंकित करें जो दिखाए कि आप अभी (RIGHT NOW) कैसे महसूस करते हैं। "
            "भाग 2: आप सामान्यतः कैसे महसूस करते हैं अथवा प्रतिक्रिया देते हैं, अंकित करें। भाग 3: क्रोधित/प्रकोपित होने पर आप सामान्यतः "
            "कितनी बार इस प्रकार व्यवहार करते हैं, अंकित करें। कोई उत्तर सही या गलत नहीं है; किसी एक कथन पर अत्यधिक समय न लगाएँ।"),
        "timeframe": en_hi("Parts 1-3 as printed on the form.", "भाग 1-3 यथा-मुद्रित पत्रक।"),
        "parts": parts,
        "matrixOptions": STAXI_OPTS,
        "sumScoring": True,
        "subscales": subscales,
        "normsNote": en_hi(
            "Raw sums are reported; percentile/T-score conversion requires the licensed STAXI-CA manual and its age/sex tables, which are not reproduced here.",
            "केवल कच्चे योग रिपोर्ट किए जाते हैं; percentile/T-score रूपांतरण हेतु लाइसेंसप्राप्त STAXI-CA मैनुअल एवं आयु/लिंग तालिकाएँ आवश्यक हैं, जो यहाँ संकलित नहीं।"),
        "scoring": {
            "method": "staxi_ca_sum_subscales",
            "scaleMin": 1,
            "scaleMax": 4,
            "rule": en_hi(
                "Sum items within each part/subscale as printed: State Anger 1-15 (15-60), Trait Anger 16-24 (16-36), "
                "Anger-In, Anger-Out and Anger Control each from ten Part 3 items (10-40), Denial from items 28 and 33 (2-8). "
                "Higher scores indicate more intense/frequent anger on that dimension; Anger Control is interpreted in the "
                "opposite direction (higher = better control). No single cutoff defines caseness.",
                "प्रत्येक भाग/उप-पैमाने के आइटम यथा-मुद्रित योग करें: अवस्था क्रोध 1-15 (15-60), लक्षण क्रोध 16-24 (16-36), "
                "Anger-In, Anger-Out एवं क्रोध-नियंत्रण प्रत्येक दस आइटम से (10-40), अस्वीकरण आइटम 28 एवं 33 से (2-8)। "
                "उच्च स्कोर = उस आयाम पर अधिक तीव्र/आवृत्त क्रोध; क्रोध-नियंत्रण विपरीत दिशा में (उच्च = बेहतर नियंत्रण)। कोई एकमानी कटऑफ मानसिक-रोगिता निर्धारित नहीं करता।"),
            "notDiagnostic": en_hi(
                "STAXI-CA measures anger dimensions; it does not diagnose any disorder.",
                "STAXI-CA क्रोध के आयाम मापता है; किसी विकार का रोग-निर्णय नहीं करता।"),
        },
        "sourcePages": "User-supplied STAXI-CA item list and Parts 1-3 answer-sheet scans.",
        "sourceNotes": STAXI_SOURCE_NOTES,
        "translationNote": "Hindi labels are machine-assisted aids; English is authoritative. Clinician proofreading required.",
        "branching": None,
    }


# ---------------------------------------------------------------------------
# Clinical Anger Scale (CAS) — 21 clusters x A-D
# ---------------------------------------------------------------------------
