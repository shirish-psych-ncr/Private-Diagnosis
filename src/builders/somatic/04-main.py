def main():
    check = '--check' in sys.argv
    d = load_clinical_data()
    orig = copy.deepcopy(d)

    d.setdefault('scales', {})
    d['scales']['fac22_sr'] = build_fac22()
    d['scales']['phq15'] = build_phq15()

    ids = [dom['id'] for dom in d['domains']]
    if 'somatic' in ids:
        d['domains'][ids.index('somatic')] = SOMATIC_DOMAIN
    else:
        # keep the tier ordering readable: place after the other tier-2 screens
        pos = len(d['domains'])
        for i, dom in enumerate(d['domains']):
            if dom.get('tier', 1) >= 4:
                pos = i
                break
        d['domains'].insert(pos, SOMATIC_DOMAIN)

    d.setdefault('disorders', {})
    for k, v in DISORDERS.items():
        d['disorders'][k] = v

    d.setdefault('instruments', {})
    d['instruments']['FAC22-SR'] = {
        "name": "FAC22-SR (Factitious Disorder Symptom Scale, self-report)",
        "construct": en_hi("Factitious disorder screening", "छलरोग स्क्रीनिंग"),
        "format": en_hi("22 Yes/No items, keyed; 9-14 possible, 15+ probable",
                        "22 हाँ/नहीं आइटम, keyed; 9-14 संभव, 15+ संभावित"),
        "duration": "~5 min",
        "language": en_hi("English (authoritative), Hindi working translation",
                          "अंग्रेज़ी (प्रामाणिक), हिन्दी कार्य-अनुवाद"),
        "purpose": en_hi(
            "Screen for factitious disorder in patients with medically unexplained symptoms. Not diagnostic; "
            "must be combined with record review and exclusion of malingering.",
            "अस्पष्टीकृत शारीरिक लक्षण वाले रोगियों में छलरोग की स्क्रीनिंग। रोग-निर्णायक नहीं; रिकॉर्ड-समीक्षा एवं मालिंगरिंग-विवर्जन के साथ उपयोग।"),
        "source": "Senthil & Prabhakar, J Evid Based Med Healthc 2019;6(21) Table 7",
        "licensing": en_hi("Published research instrument (open-access journal article); verify reuse terms.",
                           "प्रकाशित अनुसंधान-मापनी (open-access); पुनरुपयोग-शर्ताएँ सत्यापित करें।"),
    }
    d['instruments']['PHQ-15'] = {
        "name": "PHQ-15 (Patient Health Questionnaire — Somatic Symptoms)",
        "construct": en_hi("Somatic symptom severity", "शारीरिक लक्षण तीव्रता"),
        "format": en_hi("15 items scored 0-2 over 4 weeks (0-30)",
                        "15 आइटम, 4 सप्ताह, 0-2 अंकन (0-30)"),
        "duration": "~3 min",
        "language": en_hi("English, Hindi", "अंग्रेज़ी, हिन्दी"),
        "purpose": en_hi(
            "Quantify somatic symptom burden; supplements clinical judgement (cut-points 5 / 10 / 15).",
            "शारीरिक लक्षण-भार का परिमाणीकरण; चिकित्सकीय निर्णय की सहायता (सीमा 5 / 10 / 15)।"),
        "source": "PHQ-15 (Kroenke, Spitzer & Williams); free to use, no permission required",
        "licensing": en_hi("Public-domain PHQ family instrument.", "PHQ परिवार की सार्वजनिक-उपयोग मापनी।"),
    }

    d.setdefault('reference', {})
    d['reference']['malingering'] = REFERENCE

    meta = d.setdefault('meta', {})
    meta['schemaVersion'] = '2.6.0'
    meta['updated'] = '2026-11-04'
    notes = meta.setdefault('instrumentNotes', [])
    fac_note = ("FAC22-SR: added from the published scale table (Senthil & Prabhakar, J Evid Based Med "
                "Healthc 2019;6(21) Table 7). English wording is authoritative and was repaired from the "
                "scan; Hindi labels are a working translation awaiting bilingual-clinician proofreading. "
                "Keying verified at build time: Yes to 5, 8, 10, 11, 14-22 and No to 1-4, 6, 7, 9, 12, 13 "
                "= 22 items. Screening only - never diagnostic; factitious disorder additionally requires "
                "exclusion of malingering (see reference.malingering).")
    phq_note = ("PHQ-15: 15-item somatic symptom severity index (0-2 each, total 0-30) added as a tier-2 "
                "optional screen reached from the `somatic` domain; bands follow the printed cut-points "
                "0-4 / 5-9 / 10-14 / 15+. Severity measure that supplements clinical judgement.")
    if fac_note not in notes:
        notes.append(fac_note)
    if phq_note not in notes:
        notes.append(phq_note)

    if check:
        assert json.dumps(d, sort_keys=True) != json.dumps(orig, sort_keys=True), 'no change applied'
        print('build_somatic: --check OK (would write schema %s)' % meta['schemaVersion'])
        return

    save_clinical_data(d)

    fac = d['scales']['fac22_sr']
    phq = d['scales']['phq15']
    yes_items = sorted(q['itemNumber'] for q in fac['parts'][0]['questions'] if q['keyedAnswer'] == 'T')
    no_items = sorted(q['itemNumber'] for q in fac['parts'][0]['questions'] if q['keyedAnswer'] == 'F')
    print('wrote the modular data tree schema', meta['schemaVersion'],
          '| FAC22 items:', len(fac['parts'][0]['questions']),
          '| Yes-keyed:', yes_items,
          '| No-keyed:', no_items,
          '| PHQ-15 items:', len(phq['parts'][0]['questions']),
          '| domains:', [x['id'] for x in d['domains']],
          '| reference sections:', len(REFERENCE['sections']))


if __name__ == '__main__':
    main()
