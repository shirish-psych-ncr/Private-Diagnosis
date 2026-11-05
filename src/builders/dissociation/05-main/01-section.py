        "tier": 5,
        "dsm5": "Other Specified Dissociative Disorder",
        "icd11": "6B6Y",
        "description": en_hi(
            "Clinically significant dissociative symptoms that do not meet criteria for a specific "
            "dissociative disorder (e.g. OSDD-1: identity disruption with less distinct parts, or "
            "without amnesia).",
            "नैदानिक रूप से महत्वपूर्ण वियोजीय लक्षण जो किसी निश्चित वियोजीय विकार के मानदंड पूर्ण नहीं करते "
            "(जैसे OSDD-1: कम भिन्न अंशों के साथ पहचान-विचलन, अथवा क्षतिस्मृति विना)।"),
        "mappingNote": "ICD-11 6B6Y Other specified dissociative disorder; DSM-5-TR OSDD. Screen flags only.",
    })
    disc.setdefault('unspecified_dissociative_disorder', {
        "name": en_hi("Unspecified Dissociative Disorder", "अनिर्दिष्ट वियोजीय विकार"),
        "tier": 5,
        "dsm5": "Unspecified Dissociative Disorder",
        "icd11": "6B6Z",
        "description": en_hi(
            "Dissociative symptoms of clinical significance where criteria are not met or information "
            "is insufficient for a specific diagnosis.",
            "नैदानिक महत्व वाले वियोजीय लक्षण जहाँ मानदंड पूर्ण नहीं हैं अथवा विशिष्ट निदान हेतु सूचना अपर्याप्त है।"),
        "mappingNote": "ICD-11 6B6Z Unspecified dissociative disorder; DSM-5-TR unspecified. Screen flags only.",
    })
    disc.setdefault('dissociative_amnesia', {
        "name": en_hi("Dissociative Amnesia", "वियोजीय क्षतिस्मृति"),
        "tier": 5,
        "dsm5": "Dissociative Amnesia",
        "icd11": "6B60",
        "description": en_hi(
            "Inability to recall important autobiographical information, inconsistent with ordinary "
            "forgetting; may include dissociative fugue.",
            "महत्वपूर्ण आत्मकथात्मक सूचना का स्मरण-असमर्थता, साधारण विस्मरण से असंगत; वियोजीय फ्यूग सम्मिलित हो सकती है।"),
        "mappingNote": "ICD-11 6B60; DSM-5-TR Dissociative Amnesia. Flagged by MID-60 amnesia subscales.",
    })
    disc.setdefault('depersonalisation_derealisation_disorder', {
        "name": en_hi("Depersonalization/Derealization Disorder", "विलगता/वास्तविकता-विचलन विकार"),
        "tier": 5,
        "dsm5": "Depersonalization/Derealization Disorder",
        "icd11": "6B61",
        "description": en_hi(
            "Persistent or recurrent episodes of depersonalization, derealization or both, with intact "
            "reality testing.",
            "विलगता, वास्तविकता-विचलन अथवा दोनों की निरंतर/पुनरावृत्त घटनाएँ, वास्तविकता-परीक्षण सुरक्षित।"),
        "mappingNote": "ICD-11 6B61; DSM-5-TR DDD. Flagged by the MID-60 D/DD subscale.",
    })

    # link the new instruments into the library
    inst = data.setdefault('instruments', {})
    inst['MID-60'] = {
        "name": en_hi("Multidimensional Inventory of Dissociation — MID-60 (short form)",
                      "बहुआयामी वियोजन सूची — MID-60 (लघु संस्करण)"),
        "description": en_hi(
            "60-item dissociative-experience inventory rated 0-10 (never → always) when not intoxicated. "
            "Index = mean of all 60 responses x 10 (0-100) with printed score ranges (0-7 none; 7-14 few; "
            "15-20 mild; 21-30 may have DD/PTSD; 31-40 may have DD such as OSDD-1/DID; 41-64 probably DID "
            "or severe DD; 64+ severe). Twelve subscales carry individual clinical cutoffs (DID amnesia 10; "
            "alter awareness 20; angry intrusions 18; persecutory intrusions 18; D/DD 20; amnesia distress 30; "
            "autobiographical amnesia 34; PTSD flashbacks 16; conversion body symptoms 10; pseudo-seizures 10; "
            "trance 11.7; self-confusion 33.3). Screening/severity only — not diagnostic.",
            "60-आइटम वियोजीय-अनुभव सूची, नशे में न रहते हुए 0-10 (कभी नहीं → सदैव) रेटेड। सूचकांक = सभी 60 उत्तरों का "
            "माध्य × 10 (0-100), मुद्रित स्कोर-परिसर सहित। बारह उप-पैमानों पर पृथक नैदानिक कटऑफ (DID क्षतिस्मृति 10; "
            "अंश-बोध 20; क्रोधित प्रवेश 18; उत्पीड़नकारी प्रवेश 18; D/DD 20; क्षतिस्मृति-कष्ट 30; आत्मकथात्मक क्षतिस्मृति 34; "
            "PTSD फ्लैशबैक 16; परिवर्तन शारीरिक लक्षण 10; छद्म-दौरे 10; ट्रांस 11.7; स्व-विभ्रम 33.3)। केवल स्क्रीनिंग/तीव्रता — "
            "रोग-निर्णायक नहीं।"),
