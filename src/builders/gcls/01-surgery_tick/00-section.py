SURGERY_TICK = ("Tick here if you have already had genital surgery "
                "(unless you feel you need more)")
SURGERY_TICK_HI = ("यदि आपका पहले ही जननांग-शस्त्रक्रिया हो चुकी है तो यहाँ चिह्नित करें "
                   "(जब तक कि आपको अधिक की आवश्यकता न लगे)")

FREQUENCY_OPTIONS = [
    {"v": 0, "en": "Never",     "hi": "कभी नहीं"},
    {"v": 1, "en": "Rarely",    "hi": "विरल"},
    {"v": 2, "en": "Sometimes", "hi": "कभी-कभी"},
    {"v": 3, "en": "Often",     "hi": "अक्सर"},
    {"v": 4, "en": "Always",    "hi": "सदैव"},
]

# Subscales exactly as printed on the instrument.
SUBSCALES = {
    "functional_impact": {
        "en": "Functional impact of gender-related distress (items 1-13)",
        "hi": "लिंग-संबंधी कष्ट का कार्यात्मक प्रभाव (आइटम 1-13)",
        "note_en": ("How much gender-related distress has disrupted social, "
                    "occupational, emotional, physical-intimacy and home life, "
                    "and depressed/anxious symptoms."),
        "note_hi": ("लिंग-संबंधी कष्ट ने सामाजिक, व्यावसायिक, भावनात्मक, शारीरिक-नैकट्य "
                    "और गार्हस्थ्य जीवन तथा उदासीन/चिंत लक्षणों को कितना बाधित किया।"),
        "range": (0, 52),
    },
    "body_preoccupation": {
        "en": "Body preoccupation and distress (items 14, 15, 17, 18, 19, 21, 23, 24, 26, 27, 28, 29)",
        "hi": "शारीरिक आसक्ति एवं कष्ट (आइटम 14, 15, 17, 18, 19, 21, 23, 24, 26, 27, 28, 29)",
        "note_en": ("Distress focused on chest, genitals, body/facial hair and "
                    "voice, and belief that genital surgery would relieve the "
                    "unhappiness."),
        "note_hi": ("वक्ष, जननांग, शरीर/मुख्य बाल और स्वर पर केंद्रित कष्ट, तथा यह "
                    "धारणा कि जननांग-शस्त्रक्रिया असुख को हर लेगी।"),
        "range": (0, 48),
    },
    "social_preoccupation": {
        "en": "Social preoccupation and distress (items 16, 20, 22, 25, 30 reversed)",
        "hi": "सामाजिक आसक्ति एवं कष्ट (आइटम 16, 20, 22, 25, 30 — व्युक्रम)",
        "note_en": ("Comfort with how others perceive one's gender, satisfaction "
                    "with the pronouns used, comfort with being perceived from one's "
                    "appearance, feeling that the genitals match, and satisfaction "
                    "with the chest. These five items are worded positively and are "
                    "REVERSE-scored: the subscale rises as comfort falls."),
        "note_hi": ("दूसरों द्वारा लिंग-धारण से सुख, प्रयुक्त सर्वनामों से संतुष्टि, बाह्य "
                    "स्वरूप से धारणा से सुख, जननांगों के मेल का बोध और वक्ष से संतुष्टि। ये पाँच "
                    "कथन सकारात्मक हैं और व्युक्रम-अंकित होते हैं: सुख घटने पर यह उप-पैमाना बढ़ता है।"),
        "range": (0, 20),
    },
    "life_satisfaction": {
        "en": "Life satisfaction (items 31-38, 35 and 37 reversed)",
        "hi": "जीवन-संतुष्टि (आइटम 31-38, 35 एवं 37 — व्युक्रम)",
        "note_en": ("Reported separately from the distress subscales: higher = "
                    "MORE satisfaction. Items 35 and 37 are worded negatively "
                    "and are reverse-scored so that all eight point the same way."),
        "note_hi": ("कष्ट-उप-पैमानों से पृथक् रिपोर्ट: उच्च = अधिक संतुष्टि। आइटम 35 एवं 37 "
                    "नकारात्मक हैं और व्युक्रम-अंकित होते ताकि सभी आठ एक ही दिशा में रहें।"),
        "range": (0, 32),
    },
}

REVERSED_KEYS = {"C", "R"}


def build_scale():
    parts = []
    meta = {}
    groups = [
        ("gcls_part1", "past_6_months_distress",
         {"en": "In the past 6 months, due to the distress about my gender "
                "(i.e., the distress caused as the gender I was assigned at "
                "birth does not match with my gender identity):",
