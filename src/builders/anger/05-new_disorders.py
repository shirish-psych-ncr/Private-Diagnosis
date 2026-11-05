NEW_DISORDERS = {
    "intermittent_explosive_disorder": (
        "Intermittent Explosive Disorder", "विविक्त विस्फोटक विकार",
        "6B60", "F63.81", 3,
        "Recurrent behavioural outbursts representing impulsive aggressive episodes; anger instruments quantify severity but cannot diagnose."),
    "disruptive_mood_dysregulation_disorder": (
        "Disruptive Mood Dysregulation Disorder", "विघ्नकारी मूड-अनियमन विकार",
        "6A00.1 (paediatric-onset mood dysregulation)", "F67.8 / 6A60", 3,
        "Severe persistent irritability with frequent temper outbursts in children/adolescents; STAXI-CA informs severity only."),
    "other_specified_disruptive_impulse_control_behaviour_disorder": (
        "Other Specified Disruptive, Impulse-Control and Conduct Disorder",
        "अन्य निर्दिष्ट विघ्नकारी, आवेग-नियंत्रण एवं आचरण विकार",
        "6B90", "F63.8", 3,
        "Clinician-specified anger/impulse-control problem that does not meet full criteria for a named disorder."),
    "unspecified_disruptive_impulse_control_behaviour_disorder": (
        "Unspecified Disruptive, Impulse-Control and Conduct Disorder",
        "अनिर्दिष्ट विघ्नकारी, आवेग-नियंत्रण एवं आचरण विकार",
        "6B91", "F63.9", 3,
        "Insufficient information to specify a particular anger/impulse-control disorder."),
}


def main(check=False):
    data = load_clinical_data()

    staxi = build_staxi_scale()
    cas = build_cas_scale()
    dom = build_domain()

    # --- integrity checks -------------------------------------------------
    assert len(staxi['parts']) == 3, "STAXI must have 3 parts"
    nums = [q['itemNumber'] for p in staxi['parts'] for q in p['questions']]
    assert nums == list(range(1, 58)), "STAXI item numbering must be continuous 1-57"

    # every subscale item must exist in the declared part
    part_items = {p['id']: {q['itemNumber'] for q in p['questions']} for p in staxi['parts']}
    for slug, ss in staxi['subscales'].items():
        pid = 'staxi_part%d' % ss['part']
        missing = set(ss['items']) - part_items[pid]
        assert not missing, "subscale %s references items outside part %s: %s" % (slug, pid, sorted(missing))
        assert len(ss['items']) == len(set(ss['items'])), "duplicate items in subscale " + slug
    # the four Part-3 subscales must partition items 25-57 exactly
    p3 = staxi['subscales']
    union = sorted(sum([p3[k]['items'] for k in ('in', 'out', 'control', 'denial')], []))
    assert union == list(range(26, 58)), "Part 3 subscales must cover 26-57 exactly, got %s" % union

    assert len(cas['parts']) == 21, "CAS must have 21 clusters"
    for p in cas['parts']:
        assert len(p['questions']) == 1 and len(p['options']) == 4

    data.setdefault('disorders', {})
    for key, (name_en, name_hi, icd11, icd10, tier, desc) in NEW_DISORDERS.items():
        if key not in data['disorders']:
            data['disorders'][key] = {
                "name": en_hi(name_en, name_hi),
                "tier": tier,
                "dsm5": name_en,
                "icd11": icd11,
                "icd10": icd10,
                "mappingNote": en_hi(
                    "Anger-screen flag only — severity instruments (STAXI-CA / CAS) quantify anger dimensions and require clinical confirmation before any diagnostic use.",
                    "केवल क्रोध-स्क्रीन धनात्मक — तीव्रता-पैमाने (STAXI-CA / CAS) क्रोध-आयाम मापते हैं; रोग-निर्णय हेतु नैदानिक पुष्टि आवश्यक।"),
                "description": en_hi(desc, desc),
            }

    refs = set()
    for q in dom['questions']:
        refs.update(q.get('disorders', []))
    missing = sorted(r for r in refs if r not in data['disorders'])
    assert not missing, "missing disorder entries: %s" % missing

    data.setdefault('scales', {})
    data['scales']['staxi_ca'] = staxi
    data['scales']['clinical_anger_scale'] = cas

    doms = data['domains']
    idx = next((i for i, d in enumerate(doms) if d['id'] == 'anger'), None)
    if idx is None:
        # keep the optional blocks together: insert after the personality domain
        pi = next((i for i, d in enumerate(doms) if d['id'] == 'personality'), len(doms) - 1)
        doms.insert(pi + 1, dom)
    else:
        doms[idx] = dom

    data.setdefault('instruments', {})
    data['instruments']['STAXI-CA'] = {
        "name": "State-Trait Anger Expression Inventory for Children and Adolescents (STAXI-CA)",
        "description": en_hi(
            "57-item anger inventory in three printed parts: State Anger (items 1-15, 'how you feel right now'), Trait Anger "
            "(items 16-24, 'how you generally feel') and Anger Expression (items 25-57, split into Anger-In, Anger-Out, "
            "Anger Control and Denial). Each item is rated 1-4; raw sums are reported per subscale (State 15-60, Trait 16-36, "
            "each expression/control scale 10-40, Denial 2-8). Dimensional only — not diagnostic.",
            "तीन-भाग 57-आइटम क्रोध-सूची: अवस्था क्रोध (1-15, 'अभी कैसे महसूस'), लक्षण क्रोध (16-24, 'सामान्यतः कैसे महसूस') "
            "एवं क्रोध-अभिव्यक्ति (25-57; Anger-In, Anger-Out, क्रोध-नियंत्रण, अस्वीकरण)। प्रत्येक आइटम 1-4 रेटेड; उप-पैमाने अनुसार "
            "कच्चे योग (अवस्था 15-60, लक्षण 16-36, प्रत्येक अभिव्यक्ति/नियंत्रण 10-40, अस्वीकरण 2-8)। केवल आयामात्मक — रोग-निर्णायक नहीं।"),
        "domain": "anger",
        "format": "self-report 1-4 rating matrix with subscale sums",
        "duration": "10-15 minutes",
        "optionalAssessment": True,
    }
    data['instruments']['CAS'] = {
        "name": "Clinical Anger Scale (CAS)",
        "description": en_hi(
            "21-cluster, four-option (A-D) self-report measure of clinical anger; A=0, B=1, C=2, D=3 summed across clusters "
            "for a total range of 0-63. Interpretive ranges: 0-13 minimal, 14-19 mild, 20-28 moderate, 29-63 severe clinical "
            "anger (Snell et al., 1995). Screens severity only — not diagnostic.",
            "नैदानिक क्रोध का 21-समूह, चार-विकल्प (A-D) स्व-वर्णित माप; A=0, B=1, C=2, D=3 समूहों में जोड़कर शीर्घ 0-63। "
            "व्याख्या-परिसर: 0-13 न्यूनतम, 14-19 हल्का, 20-28 मध्यम, 29-63 गंभीर नैदानिक क्रोध (Snell et al., 1995)। केवल तीव्रता स्क्रीन — रोग-निर्णायक नहीं।"),
        "domain": "anger",
        "format": "self-report forced-choice cluster matrix with banded total",
        "duration": "8-12 minutes",
        "optionalAssessment": True,
    }

    meta = data.setdefault('meta', {})
    meta['schemaVersion'] = '2.4.0'
    meta['updated'] = '2026-11-04'
    notes = meta.get('instrumentNotes', [])
    if isinstance(notes, list):
        for n in [
            "STAXI-CA implemented as three printed parts (State Anger 1-15, Trait Anger 16-24, Anger Expression 25-57) with Anger-In/Anger-Out/Anger-Control/Denial subscale sums; item stems were transcribed from a user-supplied scan whose duplicated/garbled lines were reconciled against the canonical printed form (see scales.staxi_ca.sourceNotes).",
            "Clinical Anger Scale (CAS) implemented as 21 four-option clusters scored A=0/B=1/C=2/D=3, summed 0-63 with the published interpretive bands (0-13 minimal, 14-19 mild, 20-28 moderate, 29-63 severe).",
            "Anger instruments are dimensional/severity measures reached through the new 'anger' domain (routing auto:angertable); they gate no diagnostic box. STAXI-CA is a copyrighted PAR instrument — verify licensing before redistribution.",
        ]:
            if n not in notes:
                notes.append(n)

    if check:
        print("check OK | STAXI parts:", len(staxi['parts']), "items:", len(nums),
              "| CAS clusters:", len(cas['parts']),
              "| subscales:", ", ".join(sorted(staxi['subscales'])))
        return

    save_clinical_data(data)
    print("wrote the modular data tree schema", meta['schemaVersion'])
    print("STAXI parts:", len(staxi['parts']), "| items:", len(nums),
          "| subscales:", ", ".join(sorted(staxi['subscales'])))
    print("CAS clusters:", len(cas['parts']), "| max total:", cas['scoring']['maxTotal'],
          "| bands:", len(cas['bands']))


