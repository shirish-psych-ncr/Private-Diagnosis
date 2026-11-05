        "domain": "dissociation",
        "format": "self-report 0-10 frequency matrix with index and subscale cutoffs",
        "duration": "10-15 minutes",
        "optionalAssessment": True,
    }
    inst['DES-II'] = {
        "name": en_hi("Dissociative Experiences Scale (DES-II)",
                      "वियोजीय अनुभव पैमाना (DES-II)"),
        "description": en_hi(
            "28-item self-report measure; each item is scored as the percentage of time the experience "
            "occurs (0-100%) and the total is the mean of the 28 percentages. A mean of 30 or higher is "
            "the clinical comparison point indicating a need for a structured dissociative interview "
            "(Eve Bernstein Carlson, Ph.D. & Frank W. Putnam, M.D.). Not diagnostic on its own.",
            "28-आइटम स्व-वर्णित माप; प्रत्येक आइटम अनुभव के प्रतिशत समय (0-100%) से अंकित और कुल 28 प्रतिशतों का माध्य है। "
            "30 या अधिक का माध्य नैदानिक-तुलना बिंदु है जो संरचित वियोजीय साक्षात्कार हेतु निर्देशित करता है (Carlson & "
            "Putnam)। स्वयं में रोग-निर्णायक नहीं।"),
        "domain": "dissociation",
        "format": "self-report percentage matrix with mean total",
        "duration": "5-10 minutes",
        "optionalAssessment": True,
    }

    meta = data.setdefault('meta', {})
    meta['schemaVersion'] = '2.5.0'
    meta['updated'] = '2026-11-04'
    notes = meta.get('instrumentNotes', [])
    if isinstance(notes, list):
        for n in [
            "Dissociation instruments implemented as scales.mid60 (Multidimensional Inventory of "
            "Dissociation 60-item short form; index = mean of 60 ratings x 10 with printed score ranges "
            "and 12 subscale clinical cutoffs) and scales.desii (Dissociative Experiences Scale II; 28 "
            "percentage items, total = mean, clinical comparison point >= 30). Reached through the new "
            "'dissociation' domain via routing auto:dissociationtable; both are self-report dimensional "
            "screening measures and gate no diagnostic box.",
            "MID-60 short-form reference: Kate, Jamieson, Dorahy & Middleton (2021), Journal of Trauma & "
            "Dissociation 22(3), 265-287. Two printed subscale-key anomalies (body-symptom item 21 vs "
            "trance item 21 duplication) are documented in scales.mid60.sourceNotes instead of being "
            "silently corrected. The full 253-item MID is copyrighted — verify licensing before "
            "redistribution.",
            "MID-60 items 22, 37, 44, 56 and 58 (persecutory/degrading voices, waking with means of "
            "self-harm) and DES-II item 27 (command/commentary voices) carry safety flags that open "
            "the crisis pathway when rated above zero.",
        ]:
            if n not in notes:
                notes.append(n)

    # sanity: every disorder referenced from the domain exists
    all_disc = set(disc.keys())
    for q in dom['questions']:
        missing = [x for x in q['disorders'] if x not in all_disc]
        assert not missing, missing

    if check:
        mid = scales['mid60']
        des = scales['desii']
        print("check OK | MID items:", len(mid['parts'][0]['questions']),
              "| subscales:", len(mid['subscales']),
              "| score ranges:", len(mid['scoreRanges']),
              "| DES items:", len(des['parts'][0]['questions']),
              "| schema", meta['schemaVersion'])
        return

    save_clinical_data(data)
    print("wrote the modular data tree schema", meta['schemaVersion'])
    print("MID-60 items:", len(scales['mid60']['parts'][0]['questions']),
          "| subscales:", len(scales['mid60']['subscales']))
    print("DES-II items:", len(scales['desii']['parts'][0]['questions']),
          "| cutoff:", scales['desii']['scoring']['cutoff'])


