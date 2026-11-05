def _use_criteria(prefix, what_en, what_hi):
    """Return the ten lettered criteria questions (a-j) shared by Modules I and J."""
    return [
      q(prefix + "a", "During the times when you used " + what_en + ", did you end up using more than you planned when you started?",
        "जब भी आप " + what_hi + " का सेवन करते, क्या शुरू में योजना से अधिक का सेवन हो जाता?"),
      q(prefix + "b", "Did you repeatedly want to reduce or control your use? Did you try to cut down or control your use, but failed? (If yes to either, code Yes.)",
        "क्या बार-बार कम करने/नियंत्रण की इच्छा हुई? क्या घटाने/नियंत्रण का प्रयास कर विफल रहे? (किसी भी पर 'हाँ' कोड करें।)"),
      q(prefix + "c", "On the days that you used " + what_en + ", did you spend substantial time obtaining it, using it, or recovering from its effects?",
        "जिन दिनों " + what_hi + " का सेवन किया, क्या पर्याप्त समय इसे प्राप्त करने/सेवन/प्रभाव से उबरने में लगा?"),
      q(prefix + "d", "Did you crave or have a strong desire or urge to use " + what_en + "?",
        "क्या " + what_hi + " के लिए लालसा/तीव्र इच्छा/वेग हुआ?"),
      q(prefix + "e", "Did you spend less time meeting your responsibilities at work, at school, or at home, because of your repeated use?",
        "क्या बार-बार सेवन के कारण कार्य/विद्यालय/घर की ज़िम्मेदारियों में कम समय देने लगे?"),
      q(prefix + "f", "If your use caused problems with your family or other people, did you still keep on using?",
        "यदि सेवन से परिवार/अन्य लोगों में समस्या हुई, तब भी सेवन जारी रखा?"),
      q(prefix + "g", "Did you use more than once in any situation where you or others were physically at risk, for example, driving a car, riding a motorbike, using machinery, boating, etc.?",
        "क्या एक से अधिक बार ऐसी स्थिति में सेवन किया जहाँ आप/दूसरे शारीरिक रूप से जोखिम में थे — जैसे कार/बाइक चलाना, मशीनरी, नाव आदि?"),
      q(prefix + "h", "Did you continue to use, even though it was clear that it had caused or worsened psychological or physical problems?",
        "क्या सेवन जारी रखा, यद्यपि स्पष्ट था कि इससे मानसिक/शारीरिक समस्याएँ उत्पन्न/बढ़ी हैं?"),
      q(prefix + "i", "Did you reduce or give up important work, social or recreational activities because of your use?",
        "क्या सेवन के कारण महत्वपूर्ण कार्य/सामाजिक/मनोरंजन गतिविधियाँ घटाईं/छोड़ीं?"),
      q(prefix + "j", "Did you need to use a lot more in order to get the same effect that you got when you first started using, or did you get much less effect with continued use of the same amount?",
        "क्या प्रारंभिक-समान असर हेतु बहुत अधिक सेवन आवश्यक हुआ, या समान मात्रा से असर बहुत कम होने लगा?")]

