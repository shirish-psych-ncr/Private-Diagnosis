PDQ_SUBITEM_HI = {
    "i98_spend": "मेरे पास से अधिक धन व्यय करना।",
    "i98_sex": "परिचित न लोगों के साथ यौन संबंध।",
    "i98_drink": "अधिक शराब सेवन।",
    "i98_drugs": "मादक द्रव्य लेना।",
    "i98_binge": "अतिभोजन के एपिसोड।",
    "i98_drive": "बेपरवाह ड्राइविंग।",
    "cd99_bully": "मुझे दुर्व्यवहारकारी माना जाता था।",
    "cd99_fights": "मैं अन्य बच्चों से झगड़े आरंभ करता था।",
    "cd99_weapon": "झगड़ों में मैंने अस्त्र प्रयोग किया।",
    "cd99_rob": "मैं लोगों को लूटता था।",
    "cd99_cruel_people": "मैं लोगों के प्रति शारीरिक रूप से क्रूर था।",
    "cd99_cruel_animals": "मैं पशुओं के प्रति शारीरिक रूप से क्रूर था।",
    "cd99_sex": "मैंने किसी को बलपूर्वक संबंध बनाने को बाध्य किया।",
    "cd99_lie": "मैं बहुत झूठ बोलता था।",
    "cd99_stay_out": "अनुमति बिना रात भर बाहर रहता था।",
    "cd99_steal": "मैं दूसरों की वस्तुएँ चुराता था।",
    "cd99_fire": "मैं आग लगाता था।",
    "cd99_property": "मैं खिड़कियाँ तोड़ता या संपत्ति नष्ट करता था।",
    "cd99_runaway": "एक से अधिक बार घर से रात भर गायब हुआ।",
    "cd99_truancy": "13 वर्ष से पूर्व मैं विद्यालय प्रायः छूटता था।",
    "cd99_break_in": "मैं किसी के घर, भवन या वाहन में सेंध लगाता था।",
    "cs_a": "क्या ये सभी आइटम आपके लिए पूर्णतः सत्य हैं?",
    "cs_b": "ये लक्षण कब से आपके व्यक्तित्व का अंग हैं?",
    "cs_c": "क्या ये लक्षण तब भी विद्यमान हैं जब आप अवसादग्रस्त, चिंतित, पदार्थाधीन अथवा शारीरिक रूप से रोगी नहीं हैं?",
    "cs_d": "क्या इन लक्षणों ने कार्य, संबंध या गृह-जीवन में समस्याएँ उत्पन्न की हैं?",
    "cs_e": "क्या ये लक्षण आपको परेशान करते हैं अथवा पीड़ा देते हैं?",
}


# ---------------------------------------------------------------------------
# Build the two scale definitions
# ---------------------------------------------------------------------------
def build_ipde_scale():
    parts = []
    for code, name_en, dsm_name, keys, dis in IPDE_MODULES:
        qs = []
        for num, ans in keys:
            if ans is None:   # IPDE item 3: not printed on the form
                continue
            q = {
                "id": "ipde_%d" % num,
                "itemNumber": num,
                "text": en_hi(IPDE_ITEMS_TEXT[num], IPDE_HI.get(num, IPDE_ITEMS_TEXT[num])),
                "keyedAnswer": ans,          # 'T' or 'F' counts toward the screen
                "screenItems": code,
                "disorders": list(dis),
            }
            if num == 25:                    # suicidal-threat stem -> safety flag
                q["safety"] = True
            qs.append(q)
        parts.append({
            "id": "ipde_" + code.replace(".", "_"),
            "name": en_hi("%s %s" % (code, name_en), "%s %s" % (code, name_en)),
            "icd10Module": code,
            "disorderName": en_hi(dsm_name, dsm_name),
            "disorders": list(dis),
            "questions": qs,
        })
    return {
        "id": "ipde_screen",
        "name": en_hi("IPDE ICD-10 Module Screening Questionnaire",
                      "IPDE ICD-10 माड्यूल स्क्रीनिंग प्रश्नावली"),
        "type": "matrix",
        "administeredBy": "self-or-clinician",
        "sourceInstrument": "IPDE",
        "targetAge": ["adult"],
        "directions": en_hi(
            "Please do not skip any item. If you are not sure of an answer, select the one TRUE or FALSE which is more likely to be correct. There is no time limit, but do not spend too much time thinking about the answer to any single statement. When the answer is TRUE, mark T. When the answer is FALSE, mark F.",
            "कृपया किसी भी item को छोड़ें नहीं। उत्तर में निश्चित न हों तो सत्य अथवा मिथ्या में से अधिक संभावित सही चुनें। समय की सीमा नहीं है, किंतु किसी एक कथन पर अत्यधिक चिंतन न करें। उत्तर सत्य हो तो T और मिथ्या हो तो F अंकित करें।"),
        "timeframe": en_hi(
            "Rate how you generally are, not how you feel at this moment.",
            "सामान्य स्व का मूल्यांकन करें, इस क्षण की भावना का नहीं।"),
        "parts": parts,
        "matrixOptions": TF,
        # Machine-readable markers consumed by app.js (renderMatrix / computeResults)
        "keyedScoring": True,
        "keying": "ipde",
        "scoring": {
            "method": "ipde_keyed_answer_screen",
            "rule": en_hi(
                "Circle the item numbers not followed by F, if they were answered True. Circle the remaining item numbers (those followed by F), if they were answered False. If three or more items from a disorder are circled, the subject has failed the screen for that disorder, and should be interviewed.",
                "जिन आइटम संख्याओं के पास F नहीं है उनको सत्य उत्तर पर वृत्त करें। शेष (F वाले) को मिथ्या उत्तर पर वृत्त करें। यदि किसी विकार के तीन अथवा अधिक आइटम वृत्त हुए तो उस विकार की स्क्रीन असफल हुई और साक्षात्कार आवश्यक है।"),
            "failThreshold": 3,
            "appStandard": en_hi(
                "This application applies the LOWER screening standard permitted by the instrument's authors ('clinicians and investigators may wish to adopt lower or higher screening standards'): ONE or more keyed items flags the ICD-10 F60 cluster for the full IPDE interview. The screen is not diagnostic and yields no dimensional score.",
                "यह एप्लिकेशन लेखकों द्वारा अनुमत निम्नतर स्क्रीनिंग मानदंड लागू करता है: एक अथवा अधिक कुंजी-उत्तर आइटम ICD-10 F60 क्लस्टर को पूर्ण IPDE साक्षात्कार हेतु चिह्नित करता है। यह स्क्रीन रोग-निर्णायक नहीं है और कोई विमानी अंक नहीं देती।"),
            "positiveThreshold": 1,
            "note": en_hi(
                "The screen should not be used to make a diagnosis or to calculate a dimensional score for a personality disorder.",
                "व्यक्तित्व विकार का रोग-निर्णय अथवा विमानी अंक हेतु स्क्रीन का प्रयोग न करें।"),
        },
        "sourcePages": "IPDE International Personality Disorder Examination — ICD-10 module screening questionnaire & scoring summary",
        "licensingNote": en_hi(
            "IPDE screening form reproduced for local clinical/research use; verify current licensing with the instrument publisher before redistribution.",
            "स्थानीय नैदानिक /शोध प्रयोग हेतु अभिलिखित; पुनर्वितरण से पूर्व प्रकाशक लाइसेंस सत्यापित करें।"),
        "translationNote": en_hi(
            "Item wording is transcribed verbatim from the English screening form. Hindi labels are a machine-assisted aid flagged for clinician review; the printed form omits item 3.",
            IPDE_HI_HINT),
    }


