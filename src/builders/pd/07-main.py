def main(check=False):
    data = load_clinical_data()

    ipde = build_ipde_scale()
    pdq = build_pdq_scale()
    dom = build_domain()

    # sanity: every referenced disorder exists (existing + newly added)
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
                    "Personality-disorder screen flag only — requires confirmation with the full IPDE/PDQ-4+ interview before any diagnostic use.",
                    "केवल व्यक्तित्व स्क्रीन धनात्मक — रोग-निर्णय हेतु पूर्ण साक्षात्कार आवश्यक।"),
                "description": en_hi(desc, desc),
            }

    refs = set()
    for p in ipde['parts']:
        refs.update(p['disorders'])
    for s in pdq['scales']:
        refs.update(s['disorders'])
    for q in dom['questions']:
        refs.update(q.get('disorders', []))
    missing = sorted(r for r in refs if r not in data['disorders'])
    assert not missing, "missing disorder entries: %s" % missing

    data.setdefault('scales', {})
    data['scales']['ipde_screen'] = ipde
    data['scales']['pdq4_screen'] = pdq

    # replace-or-append the personality domain
    doms = data['domains']
    idx = next((i for i, d in enumerate(doms) if d['id'] == 'personality'), None)
    if idx is None:
        doms.append(dom)
    else:
        doms[idx] = dom

    data.setdefault('instruments', {})
    data['instruments']['IPDE'] = {
        "name": "International Personality Disorder Examination (IPDE) — ICD-10 module screening questionnaire",
        "description": en_hi(
            "Loranger's structured interview; the brief screening form covers the nine ICD-10 F60 personality categories (paranoid, schizoid, dissocial, impulsive, borderline, histrionic, anankastic, anxious, dependent) with keyed True/False items. Three or more keyed items fail the screen for that disorder (this app flags at one, per the authors' lower-standard option); the screen is never diagnostic.",
            "loranger_का_संरचित_साक्षात्कार;_संक्षिप्त_स्क्रीनिंग_पत्रक_ICD-10 की_nौं_F60 श्रेणियों_को_कुंजी-उत्तर T/F आइटम_से_कवर_करता_है। तीन_अथवा_अधिक_कुंजी_आइटम_उस_विकार_की_स्क्रीन_असफल_करते_हैं (यह_ऐप_लेखकों_के_निम्नतर_मानदंड_अनुसार_एक_पर_धनात्मक_करता_है);_स्क्रीन_कभी_रोग-निर्णायक_नहीं।"),
        "domain": "personality",
        "format": "clinician/self-administered keyed True-False screen",
        "optionalAssessment": True,
    }
    data['instruments']['PDQ-4+'] = {
        "name": "Personality Diagnostic Questionnaire-4+ (PDQ-4+)",
        "description": en_hi(
            "99-item True/False self-report screen for 12 DSM personality disorders, with two validity items (64, 76), Section B impulsivity (item 98) and conduct-disorder (item 99) checklists gating Borderline and Antisocial respectively, and a mandatory five-part clinical-significance follow-up (accuracy, duration, pervasiveness, impairment, distress). Not diagnostic.",
            "12 DSM व्यक्तित्व_विकार_हेतु 99-आइटम T/F स्व-वर्णित_स्क्रीन;_दो_वैधता_आइटम (64, 76),_खंड-B आवेगी_आइटम 98 एवं_आचरण-विकार_आइटम 99 क्रमशः सीमांत_एवं_विरोधी_समाजवादी_द्वार_रूप, तथा_पाँच-भाग_नैदानिक_महत्व_अनुवर्ती_अनिवार्य। रोग-निर्णायक_नहीं।"),
        "domain": "personality",
        "format": "self-report True/False questionnaire with thresholds",
        "optionalAssessment": True,
    }

    meta = data.setdefault('meta', {})
    meta['schemaVersion'] = '2.3.0'
    meta['updated'] = '2026-11-04'
    notes = meta.setdefault('instrumentNotes', []) if isinstance(meta.get('instrumentNotes', []), list) else []
    if isinstance(notes, list):
        for n in [
            "IPDE ICD-10 screening questionnaire implemented with keyed True/False items; app uses the single-item positive standard explicitly permitted by the instrument authors (printed standard: >=3 keyed items per disorder).",
            "PDQ-4+ implemented with validity items 64/76, Section B item 98 (>=2 impulsivity checks gates Borderline) and item 99 (>=3 conduct checks gates Antisocial), plus the mandatory clinical-significance A-E follow-up checklist.",
            "Personality instrument item text was transcribed from user-supplied scans; Hindi labels are machine-assisted aids flagged for clinician review. Verify licensing before redistribution."]:
            if n not in notes:
                notes.append(n)

    out = json.dumps(data, ensure_ascii=False, indent=2)
    if check:
        print("check OK:", len(ipde['parts']), "IPDE modules,",
              len(pdq['parts'][0]['questions']), "PDQ items,",
              len(pdq['scales']), "PDQ scales")
        return

    save_clinical_data(data)
    print("wrote the modular data tree schema", meta['schemaVersion'])
    print("IPDE modules:", len(ipde['parts']), "| IPDE items:",
          sum(len(p['questions']) for p in ipde['parts']))
    print("PDQ items:", len(pdq['parts'][0]['questions']),
          "| scales:", len(pdq['scales']),
          "| 98 options:", len(pdq['parts'][1]['questions']),
          "| 99 options:", len(pdq['parts'][2]['questions']),
          "| CS items:", len(pdq['parts'][3]['questions']))


if __name__ == '__main__':
    main(check='--check' in sys.argv)
