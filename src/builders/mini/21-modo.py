modO = {
  "id": "O",
  "name": {"en": "Module O — Rule Out Medical, Organic or Drug Causes For All Disorders",
           "hi": "माड्यूल O — सभी विकारों हेतु चिकित्सकीय/जैविक/दवा-जन्य कारणों का बहिर्गमन"},
  "applicabilityNote": {"en": "If the patient codes positive for any current disorder or a major depressive episode or a manic or a hypomanic episode, ask the following about the period just before these symptoms began.",
                         "hi": "यदि रोगी किसी वर्तमान विकार या प्रमुख अवसादी एपिसोड या मैैनिक/हाइपोमैैनिक एपिसोड पर सकारात्मक कोडित होता है, तो इन लक्षणों के ठीक पूर्व काल के बारे में निम्न पूछें।"},
  "intro": {"en": "Just before these symptoms began:", "hi": "इन लक्षणों के शुरू होने से ठीक पहले:"},
  "questions": [
    q("O1a", "Were you taking any drugs or medicines or in withdrawal from any of these?",
      "क्या आप कोई नशा/दवा ले रहे थे या उनसे विषमुक्ति-अवस्था में थे?", options=NYU_OPTIONS),
    q("O1b", "Did you have any medical illness?", "क्या आपको कोई चिकित्सकीय रोग था?", options=NYU_OPTIONS),
    q("O2", "If O1a or O1b is coded Yes: in the clinician's judgment, is either likely to be a direct cause of the patient's disorder? If necessary, ask additional open-ended questions.",
      "यदि O1a या O1b 'हाँ' कोडित हो: चिकित्सक के निर्णय अनुसार, क्या इनमें से कोई रोगी के विकार का प्रत्यक्ष कारण होने की संभावना है? आवश्यकतानुसार अतिरिक्त खुले प्रश्न पूछें।",
      options=NYU_OPTIONS, clinicianJudgment=True)],
  "o2Summary": {"id": "O2_summary", "derived": True,
                "rule": "Has an 'organic'/medical/drug related cause been ruled out? If O2 is Yes, then O2 SUMMARY is No. If O2 is No, then O2 SUMMARY is Yes. Otherwise it is Uncertain.",
                "text": {"en": "O2 SUMMARY: Has an 'organic'/medical/drug related cause been ruled out?",
                          "hi": "O2 सारांश: क्या 'जैविक'/चिकित्सकीय/दवा-संबंधित कारण बहिर्गत किया गया है?"},
                "options": NYU_OPTIONS}}

