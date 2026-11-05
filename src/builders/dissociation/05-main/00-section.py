def main(check=False):
    data = load_clinical_data()

    scales = data.setdefault('scales', {})
    scales['mid60'] = build_mid_scale()
    scales['desii'] = build_des_scale()

    # ---- domain ----------------------------------------------------------
    domains = data.setdefault('domains', [])
    dom = {
        "id": "dissociation",
        "name": en_hi("Dissociation", "वियोजन"),
        "tier": 2,
        "instrument": "auto:dissociationtable",
        "timeframe": en_hi(
            "Screen-in items refer to the past month and to experiences had when you are not under the "
            "influence of alcohol or drugs; the deployed instruments then rate lifetime/current "
            "dissociative experiences.",
            "स्क्रीन-इन प्रश्न गत माह को एवं उन अनुभवों को संदर्भित करते हैं जो शराब/नशे के प्रभाव में न रहते हुए हों; "
            "तत्पश्चात् संलग्न उपकरण जीवन-भर/वर्तमान वियोजीय अनुभव रेट करते हैं।"),
        "questions": [
            {
                "id": "dis_1",
                "text": en_hi(
                    "Do you often have experiences such as losing track of time or part of the day, "
                    "finding things you don't remember buying or doing, feeling detached from your body "
                    "or from surroundings, or hearing voices inside your head — when you are not under "
                    "the influence of alcohol or drugs?",
                    "क्या आपको प्रायः ऐसे अनुभव होते हैं — समय/दिन का कुछ भाग खो जाना, बिना खरीदे-किए वस्तुएँ मिलना, "
                    "शरीर या चारों ओर से विलगता, सिर के भीतर आवाज़ें सुनना — जब आप शराब/नशे के प्रभाव में न हों?"),
                "sharedScale": "yesno",
                "scaleId": "mid60",
                "disorders": DISS_DISORDERS,
            },
            {
                "id": "dis_2",
                "text": en_hi(
                    "Have other people told you that you sometimes seem to go blank, forget conversations "
                    "or events, act unlike yourself, or that you describe more than one 'part' of you?",
                    "क्या दूसरों ने बताया है कि कभी-कभी आप खाली-से लगते हैं, बातचीत/घटनाएँ भूल जाते हैं, अपने से भिन्न "
                    "व्यवहार करते हैं, अथवा आप अपने भीतर एक से अधिक \"अंश\" का वर्णन करते हैं?"),
                "sharedScale": "yesno",
                "scaleId": "desii",
                "disorders": DISS_DISORDERS,
            },
        ],
    }
    existing = next((i for i, x in enumerate(domains) if x['id'] == 'dissociation'), None)
    if existing is None:
        # keep trauma and dissociation adjacent
        ti = next((i for i, x in enumerate(domains) if x['id'] == 'trauma'), len(domains) - 1)
        domains.insert(ti + 1, dom)
    else:
        domains[existing] = dom

    # ---- disorders -------------------------------------------------------
    disc = data.setdefault('disorders', {})
    disc.setdefault('dissociative_identity_disorder', {
        "name": en_hi("Dissociative Identity Disorder", "वियोजीय पहचान विकार"),
        "tier": 5,
        "dsm5": "Dissociative Identity Disorder",
        "icd11": "6B64",
        "description": en_hi(
            "Two or more distinct personality states with recurrent amnesia; disruption of identity "
            "characterized by marked discontinuity of sense of self and sense of agency.",
            "दो या अधिक भिन्न व्यक्तित्व-अवस्थाएँ एवं बार-बार क्षतिस्मृति; स्व-बोध एवं कर्तृत्व-बोध में स्पष्ट असंततता।"),
        "mappingNote": (
            "ICD-11 6B64 corresponds to DSM-5-TR Dissociative Identity Disorder; the pre-existing "
            "'dissociative' key holds the same label and is retained for backward compatibility. "
            "Flagged by MID-60/DES-II screens only — diagnosis requires the full structured interview."),
    })
    disc.setdefault('other_specified_dissociative_disorder', {
        "name": en_hi("Other Specified Dissociative Disorder", "अन्य निर्दिष्ट वियोजीय विकार"),
