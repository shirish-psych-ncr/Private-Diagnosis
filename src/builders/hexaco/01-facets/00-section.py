FACETS = [
    ("h_h", "sincerity",            "Sincerity",                    "आंतरिकता/निष्ठा", [6, 30, 54]),
    ("h_h", "fairness",             "Fairness",                     "न्यायपरायणता",     [12, 36, 60]),
    ("h_h", "greed_avoidance",      "Greed Avoidance",              "लालच-परिहार",   [18, 42]),
    ("h_h", "modesty",              "Modesty",                      "विनम्रता",       [24, 48]),

    ("e", "fearfulness",            "Fearfulness",                  "भयाकुलता",       [5, 29, 53]),
    ("e", "anxiety",                "Anxiety",                      "चिंता",         [11, 35]),
    ("e", "dependence",             "Dependence",                   "निर्भरता",       [17, 41]),
    ("e", "sentimentality",         "Sentimentality",               "संवेदनशीलता",   [23, 47, 59]),

    ("x", "social_self_esteem",     "Social Self-Esteem",           "सामाजिक आत्मसम्मान", [4, 28, 52]),
    ("x", "social_boldness",        "Social Boldness",              "सामाजिक साहस",   [10, 34, 58]),
    ("x", "sociability",            "Sociability",                  "सामाजिकता",     [16, 40]),
    ("x", "liveliness",             "Liveliness",                   "प्राणोद्वलन",   [22, 46]),

    ("a", "forgiveness",            "Forgiveness",                  "क्षमाशीलता",     [3, 27]),
    ("a", "gentleness",             "Gentleness",                   "कोमलता",        [9, 33, 51]),
    ("a", "flexibility",            "Flexibility",                  "लचीलापन",       [15, 39, 57]),
    ("a", "patience",               "Patience",                     "धैर्य",         [21, 45]),

    ("c", "organization",           "Organization",                 "सुव्यवस्था",    [2, 26]),
    ("c", "diligence",              "Diligence",                    "परिश्रमिता",    [8, 32]),
    ("c", "perfectionism",          "Perfectionism",                "परिपूर्णता",    [14, 38, 50]),
    ("c", "prudence",               "Prudence",                     "सावधानता",      [20, 44, 56]),

    ("o", "aesthetic_appreciation", "Aesthetic Appreciation",       "सौंदर्य-साहाध्यता", [1, 25]),
    ("o", "inquisitiveness",        "Inquisitiveness",              "जिज्ञासा",       [7, 31]),
    ("o", "creativity",             "Creativity",                   "रचनात्मकता",    [13, 37, 49]),
    ("o", "unconventionality",      "Unconventionality",            "अपरंपरिकता",    [19, 43, 55]),
]

# Items keyed "R" (reverse-scored) in the published HEXACO-60 scoring guide.
REVERSE_KEYED = {1, 9, 10, 12, 15, 18, 19, 20, 21, 24, 25, 26, 30, 32, 35, 36,
                 38, 41, 42, 44, 48, 50, 51, 52, 54, 55, 56, 57, 59, 60}

# Reverse-keyed items ("R" in the printed scoring guide), derived from FACETS so
# the item flags and the facet keying can never drift apart.
REV = {num for _d, _f, _en, _hi, items in FACETS for num in items if num in REVERSE_KEYED}

DOMAINS = [
    ("h_h", "Honesty-Humility", "प्रामाणिकता-विनम्रता",
     "Sincerity, Fairness, Greed Avoidance, Modesty"),
    ("e", "Emotionality", "भावनात्मकता",
     "Fearfulness, Anxiety, Dependence, Sentimentality"),
    ("x", "Extraversion", "बहिर्मुखता",
     "Social Self-Esteem, Social Boldness, Sociability, Liveliness"),
    ("a", "Agreeableness", "सहमतिशीलता",
     "Forgiveness, Gentleness, Flexibility, Patience"),
    ("c", "Conscientiousness", "कर्तव्यनिष्ठा",
     "Organization, Diligence, Perfectionism, Prudence"),
    ("o", "Openness to Experience", "अनुभव-के-प्रति-विवृतता",
     "Aesthetic Appreciation, Inquisitiveness, Creativity, Unconventionality"),
]



def build_scale():
    questions = []
    for n, en, hi in ITEMS:
        questions.append({
            "id": "hx_%d" % n,
            "itemNumber": n,
            "reverseScored": bool(n in REV),
            "text": bi(hi, en),
        })

    facets = {}
    for dom_slug, fslug, f_en, f_hi, items in FACETS:
        entries = list(items)
        facets[fslug] = {
            "name": bi(f_hi, f_en),
            "domain": dom_slug,
            "items": entries,
        }

    domains = {}
    for slug, d_en, d_hi, facet_names in DOMAINS:
        fs = [k for k, v in facets.items() if v["domain"] == slug]
        domains[slug] = {
            "name": bi(d_hi, d_en),
            "facets": fs,
            "facetNames": facet_names,
        }

    return {
        "id": "hexaco_pi_r_observer",
        "name": bi("HEXACO-PI-R (पर्यवेक्षक रिपोर्ट फ़ॉर्म)",
                   "HEXACO-PI-R (Observer Report Form)"),
