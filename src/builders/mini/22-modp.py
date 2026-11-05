modP = {
  "id": "P",
  "name": {"en": "Module P — Antisocial Personality Disorder",
           "hi": "माड्यूल P — प्रतिसामाजिक व्यक्तित्व विकार"},
  "p1Intro": {"en": "Before you were 15 years old, did you:", "hi": "15 वर्ष की आयु से पूर्व, क्या आप:"},
  "p1": [
      q("P1a", "Repeatedly skip school or run away from home overnight or stayed out at night against your parent's rules?",
        "बार-बार विद्यालय छोड़ना, रात को घर से भागना, या माता-पिता के नियमों के विरुद्ध रात बाहर रहना?"),
      q("P1b", "Repeatedly lie, cheat, 'con' others, or steal or break into someone's house or car?",
        "बार-बार झूठ, छल, दूसरों को ठगना, चोरी, या किसी के घर/गाड़ी में जबरन प्रवेश?"),
      q("P1c", "Start fights or bully, threaten, or intimidate others?",
        "झगड़े शुरू करना, या दूसरों को बुलिंग, धमकी या भयभीत करना?"),
      q("P1d", "Deliberately destroy things or start fires?", "जानबूझकर चीज़ें नष्ट करना या आग लगाना?"),
      q("P1e", "Deliberately hurt animals or people?", "जानबूझकर पशुओं या लोगों को कष्ट पहुँचाना?"),
      q("P1f", "Force someone into sexual activity?", "किसी को यौन क्रिया हेतु विवश करना?")],
  "p1Gate": {"rule": "IF <2 of P1 answers Yes -> SKIP ALL THE P2 QUESTIONS, GO TO THE DIAGNOSTIC BOX AND CIRCLE NO.",
             "text": {"en": "Are 2 or more P1 answers coded Yes?", "hi": "क्या P1 के 2 या अधिक उत्तर 'हाँ' कोडित हैं?"}},
  "p2Note": {"en": "Do not code Yes to the behaviors below if they are exclusively politically or religiously motivated.",
             "hi": "निम्न व्यवहारों पर 'हाँ' कोड न करें यदि वे अनन्य रूप से राजनीतिक या धार्मिक प्रेरित हैं।"},
  "p2Intro": {"en": "Since you were 15 years old, have you:", "hi": "15 वर्ष की आयु के बाद से, क्या आप:"},
  "p2": [
      q("P2a", "Done things that are illegal or would be grounds to get arrested, even if you didn't get caught (for example destroying property, shoplifting, stealing, selling drugs, or committing a felony)?",
        "ऐसे कार्य किए जो अवैध हैं या गिरफ़्तारी का आधार बन सकते, चाहे पकड़े गए या नहीं (जैसे संपत्ति नष्ट, दुकान-चोरी, चोरी, दवा-बेचना, गंभीर अपराध)?"),
      q("P2b", "Often lied or 'conned' other people to get money or pleasure, or lied just for fun?",
        "धन/सुख हेतु बार-बार झूठ बोला या लोगों को ठगा, या केवल मनोरंजन हेतु झूठ बोला?"),
      q("P2c", "Been impulsive and didn't care about planning ahead?", "अववेगी रहे और पूर्व-योजना की चिंता नहीं की?"),
      q("P2d", "Been in physical fights repeatedly or assaulted others (including physical fights with your spouse or children)?",
        "बार-बार शारीरिक झगड़े या दूसरों पर हमला (पत्नी/संतान से शारीरिक झगड़े सहित)?"),
      q("P2e", "Exposed others or yourself to danger without caring?", "बेपरवाही से दूसरों/स्वयं को खतरे में डाला?"),
      q("P2f", "Repeatedly behaved in a way that others would consider irresponsible, like failing to pay for things you owed, deliberately being impulsive or deliberately not working to support yourself?",
        "बार-बार ऐसी व्यवहार जो दूसरे लापरवाही मानें — जैसे उधार चुकाना नहीं, जानबूझकर अववेगता, या स्वयं को पोषण हेतु काम न करना?"),
      q("P2g", "Felt no guilt after hurting, mistreating, lying to, or stealing from others, or after damaging property?",
        "दूसरों को कष्ट/दुरुपयोग/झूठ/चोरी के बाद या संपत्ति नष्ट करने के बाद कोई अपराधबोध न हुआ?")],
  "p2Gate": {"rule": "IF <3 of P2 answers Yes -> Antisocial Personality Disorder NO.",
             "text": {"en": "Are 3 or more P2 questions coded Yes?", "hi": "क्या P2 के 3 या अधिक प्रश्न 'हाँ' कोडित हैं?"}},
  "diagnosticBoxes": [
    {"id": "P_diag", "label": {"en": "Antisocial Personality Disorder — Lifetime", "hi": "प्रतिसामाजिक व्यक्तित्व विकार — जीवनभर"},
     "rule": ">=2 of P1a-P1f Yes AND >=3 of P2a-P2g Yes (behaviors not exclusively politically or religiously motivated).",
     "flags": ["LIFETIME"], "disordersOnPositive": ["antisocial_personality_disorder"]}]}

# ---------------------------------------------------------------------------
# Additional optional interview assessments (pages 36-37 of the MINI
# user-scripted version):
#   A - Cross-Cutting Measures: severity of symptom (0-10 clinician rating
#       scale across 13 symptom domains)
#   B - Disability / Functional Impairment: severity of disability (0-10
#       clinician rating scale across 12 functioning domains)
# These are self-contained rating tables; they add no branching logic and do
# not feed any diagnostic box.
# ---------------------------------------------------------------------------

