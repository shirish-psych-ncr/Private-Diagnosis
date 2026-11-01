const CLINICAL_DATA = {
    domains: [
        {
            id: 'mood',
            name: { en: 'Mood', hi: 'मूड' },
            tier: 1,
            questions: [
                {
                    id: 'mood_1',
                    text: { en: 'Little interest or pleasure in doing things', hi: 'चीजों को करने में थोड़ी रुचि या आनंद' },
                    scale: [
                        { value: 0, label: { en: 'Not at all', hi: 'बिल्कुल नहीं' } },
                        { value: 1, label: { en: 'Several days', hi: 'कई दिन' } },
                        { value: 2, label: { en: 'More than half the days', hi: 'आधे से अधिक दिन' } },
                        { value: 3, label: { en: 'Nearly every day', hi: 'लगभग हर दिन' } }
                    ],
                    disorders: ['depression_mdd', 'depression_persistent', 'bipolar_depressive']
                },
                {
                    id: 'mood_2',
                    text: { en: 'Feeling down, depressed, or hopeless', hi: 'उदास, अवसादग्रस्त, या निराश महसूस करना' },
                    scale: [
                        { value: 0, label: { en: 'Not at all', hi: 'बिल्कुल नहीं' } },
                        { value: 1, label: { en: 'Several days', hi: 'कई दिन' } },
                        { value: 2, label: { en: 'More than half the days', hi: 'आधे से अधिक दिन' } },
                        { value: 3, label: { en: 'Nearly every day', hi: 'लगभग हर दिन' } }
                    ],
                    disorders: ['depression_mdd', 'depression_persistent', 'bipolar_depressive']
                },
                {
                    id: 'mood_3',
                    text: { en: 'Thoughts that you would be better off dead, or of hurting yourself', hi: 'विचार कि आप मर जाएं तो बेहतर होगा, या खुद को नुकसान पहुंचाने के' },
                    scale: [
                        { value: 0, label: { en: 'Not at all', hi: 'बिल्कुल नहीं' } },
                        { value: 1, label: { en: 'Several days', hi: 'कई दिन' } },
                        { value: 2, label: { en: 'More than half the days', hi: 'आधे से अधिक दिन' } },
                        { value: 3, label: { en: 'Nearly every day', hi: 'लगभग हर दिन' } }
                    ],
                    disorders: ['depression_mdd', 'bipolar_depressive'],
                    safety: true
                }
            ],
            cutoff: 10,
            instruments: ['PHQ-9', 'MDQ', 'BDI-II']
        },
        {
            id: 'anxiety',
            name: { en: 'Anxiety', hi: 'चिंता' },
            tier: 1,
            questions: [
                {
                    id: 'anxiety_1',
                    text: { en: 'Feeling nervous, anxious, or on edge', hi: 'घबराहट, चिंता, या बेचैन महसूस करना' },
                    scale: [
                        { value: 0, label: { en: 'Not at all', hi: 'बिल्कुल नहीं' } },
                        { value: 1, label: { en: 'Several days', hi: 'कई दिन' } },
                        { value: 2, label: { en: 'More than half the days', hi: 'आधे से अधिक दिन' } },
                        { value: 3, label: { en: 'Nearly every day', hi: 'लगभग हर दिन' } }
                    ],
                    disorders: ['gad', 'panic_disorder', 'social_anxiety']
                },
                {
                    id: 'anxiety_2',
                    text: { en: 'Not being able to stop or control worrying', hi: 'चिंता को रोकने या नियंत्रित करने में असमर्थ' },
                    scale: [
                        { value: 0, label: { en: 'Not at all', hi: 'बिल्कुल नहीं' } },
                        { value: 1, label: { en: 'Several days', hi: 'कई दिन' } },
                        { value: 2, label: { en: 'More than half the days', hi: 'आधे से अधिक दिन' } },
                        { value: 3, label: { en: 'Nearly every day', hi: 'लगभग हर दिन' } }
                    ],
                    disorders: ['gad', 'panic_disorder']
                },
                {
                    id: 'anxiety_3',
                    text: { en: 'Worrying too much about different things', hi: 'विभिन्न चीजों के बारे में बहुत अधिक चिंता करना' },
                    scale: [
                        { value: 0, label: { en: 'Not at all', hi: 'बिल्कुल नहीं' } },
                        { value: 1, label: { en: 'Several days', hi: 'कई दिन' } },
                        { value: 2, label: { en: 'More than half the days', hi: 'आधे से अधिक दिन' } },
                        { value: 3, label: { en: 'Nearly every day', hi: 'लगभग हर दिन' } }
                    ],
                    disorders: ['gad']
                }
            ],
            cutoff: 10,
            instruments: ['GAD-7', 'BAI', 'STAI']
        },
        {
            id: 'trauma',
            name: { en: 'Trauma', hi: 'आघात' },
            tier: 2,
            questions: [
                {
                    id: 'trauma_1',
                    text: { en: 'In the past month, have you had nightmares or unwanted thoughts about a stressful experience?', hi: 'क्या पिछले महीने में आपको किसी तनावपूर्ण अनुभव के बारे में बुरे सपने या अवांछित विचार आए हैं?' },
                    scale: [
                        { value: 0, label: { en: 'Not at all', hi: 'बिल्कुल नहीं' } },
                        { value: 1, label: { en: 'A little bit', hi: 'थोड़ा सा' } },
                        { value: 2, label: { en: 'Moderately', hi: 'मध्यम रूप से' } },
                        { value: 3, label: { en: 'Quite a bit', hi: 'काफी हद तक' } },
                        { value: 4, label: { en: 'Extremely', hi: 'बहुत अधिक' } }
                    ],
                    disorders: ['ptsd', 'complex_ptsd', 'adjustment_disorder']
                },
                {
                    id: 'trauma_2',
                    text: { en: 'Have you avoided activities or situations that remind you of the stressful experience?', hi: 'क्या आपने उन गतिविधियों या स्थितियों से बचाव किया है जो आपको तनावपूर्ण अनुभव की याद दिलाती हैं?' },
                    scale: [
                        { value: 0, label: { en: 'Not at all', hi: 'बिल्कुल नहीं' } },
                        { value: 1, label: { en: 'A little bit', hi: 'थोड़ा सा' } },
                        { value: 2, label: { en: 'Moderately', hi: 'मध्यम रूप से' } },
                        { value: 3, label: { en: 'Quite a bit', hi: 'काफी हद तक' } },
                        { value: 4, label: { en: 'Extremely', hi: 'बहुत अधिक' } }
                    ],
                    disorders: ['ptsd', 'complex_ptsd']
                }
            ],
            cutoff: 33,
            instruments: ['PCL-5', 'IES-R', 'CAPS-5']
        },
        {
            id: 'sleep',
            name: { en: 'Sleep', hi: 'नींद' },
            tier: 2,
            questions: [
                {
                    id: 'sleep_1',
                    text: { en: 'How satisfied are you with your sleep?', hi: 'आप अपनी नींद से कितने संतुष्ट हैं?' },
                    scale: [
                        { value: 0, label: { en: 'Very satisfied', hi: 'बहुत संतुष्ट' } },
                        { value: 1, label: { en: 'Satisfied', hi: 'संतुष्ट' } },
                        { value: 2, label: { en: 'Neutral', hi: 'तटस्थ' } },
                        { value: 3, label: { en: 'Dissatisfied', hi: 'असंतुष्ट' } },
                        { value: 4, label: { en: 'Very dissatisfied', hi: 'बहुत असंतुष्ट' } }
                    ],
                    disorders: ['insomnia', 'hypersomnolence', 'sleep_apnea']
                },
                {
                    id: 'sleep_2',
                    text: { en: 'How much difficulty do you have falling asleep?', hi: 'आपको नींद आने में कितनी कठिनाई होती है?' },
                    scale: [
                        { value: 0, label: { en: 'No difficulty', hi: 'कोई कठिनाई नहीं' } },
                        { value: 1, label: { en: 'Mild', hi: 'हल्की' } },
                        { value: 2, label: { en: 'Moderate', hi: 'मध्यम' } },
                        { value: 3, label: { en: 'Severe', hi: 'गंभीर' } },
                        { value: 4, label: { en: 'Very severe', hi: 'बहुत गंभीर' } }
                    ],
                    disorders: ['insomnia', 'circadian_rhythm']
                }
            ],
            cutoff: 15,
            instruments: ['ISI', 'PSQI', 'ESS']
        },
        {
            id: 'substance',
            name: { en: 'Substance Use', hi: 'पदार्थ उपयोग' },
            tier: 1,
            questions: [
                {
                    id: 'substance_1',
                    text: { en: 'How often do you have a drink containing alcohol?', hi: 'आप कितनी बार शराब पीते हैं?' },
                    scale: [
                        { value: 0, label: { en: 'Never', hi: 'कभी नहीं' } },
                        { value: 1, label: { en: 'Monthly or less', hi: 'महीने में एक बार या कम' } },
                        { value: 2, label: { en: '2-4 times a month', hi: 'महीने में 2-4 बार' } },
                        { value: 3, label: { en: '2-3 times a week', hi: 'हफ्ते में 2-3 बार' } },
                        { value: 4, label: { en: '4 or more times a week', hi: 'हफ्ते में 4 या अधिक बार' } }
                    ],
                    disorders: ['alcohol_use_disorder']
                },
                {
                    id: 'substance_2',
                    text: { en: 'Have you used drugs other than those required for medical reasons?', hi: 'क्या आपने चिकित्सा कारणों के अलावा अन्य ड्रग्स का उपयोग किया है?' },
                    scale: [
                        { value: 0, label: { en: 'No', hi: 'नहीं' } },
                        { value: 1, label: { en: 'Yes, but not in the past year', hi: 'हां, लेकिन पिछले साल नहीं' } },
                        { value: 2, label: { en: 'Yes, in the past year', hi: 'हां, पिछले साल' } },
                        { value: 3, label: { en: 'Yes, in the past month', hi: 'हां, पिछले महीने' } }
                    ],
                    disorders: ['substance_use_disorder']
                }
            ],
            cutoff: 8,
            instruments: ['AUDIT-C', 'DAST-10', 'CAGE-AID']
        },
        {
            id: 'neurodevelopmental',
            name: { en: 'Attention & Development', hi: 'ध्यान और विकास' },
            tier: 2,
            questions: [
                {
                    id: 'neuro_1',
                    text: { en: 'How often do you have trouble wrapping up the final details of a project?', hi: 'आपको कितनी बार किसी परियोजना के अंतिम विवरण को पूरा करने में परेशानी होती है?' },
                    scale: [
                        { value: 0, label: { en: 'Never', hi: 'कभी नहीं' } },
                        { value: 1, label: { en: 'Rarely', hi: 'शायद ही कभी' } },
                        { value: 2, label: { en: 'Sometimes', hi: 'कभी-कभी' } },
                        { value: 3, label: { en: 'Often', hi: 'अक्सर' } },
                        { value: 4, label: { en: 'Very often', hi: 'बहुत अक्सर' } }
                    ],
                    disorders: ['adhd']
                },
                {
                    id: 'neuro_2',
                    text: { en: 'Do you find it difficult to sit still for long periods?', hi: 'क्या आपको लंबे समय तक शांत बैठना मुश्किल लगता है?' },
                    scale: [
                        { value: 0, label: { en: 'Never', hi: 'कभी नहीं' } },
                        { value: 1, label: { en: 'Rarely', hi: 'शायद ही कभी' } },
                        { value: 2, label: { en: 'Sometimes', hi: 'कभी-कभी' } },
                        { value: 3, label: { en: 'Often', hi: 'अक्सर' } },
                        { value: 4, label: { en: 'Very often', hi: 'बहुत अक्सर' } }
                    ],
                    disorders: ['adhd']
                }
            ],
            cutoff: 14,
            instruments: ['ASRS-v1.1', 'AQ-10', 'Conners-3']
        },
        {
            id: 'psychosis',
            name: { en: 'Thoughts & Perceptions', hi: 'विचार और धारणाएं' },
            tier: 4,
            questions: [
                {
                    id: 'psychosis_1',
                    text: { en: 'Do you ever hear voices that other people cannot hear?', hi: 'क्या आप कभी ऐसी आवाज़ें सुनते हैं जो अन्य लोग नहीं सुन सकते?' },
                    scale: [
                        { value: 0, label: { en: 'No', hi: 'नहीं' } },
                        { value: 1, label: { en: 'Yes', hi: 'हां' } }
                    ],
                    disorders: ['schizophrenia', 'schizoaffective', 'brief_psychotic'],
                    safety: true
                },
                {
                    id: 'psychosis_2',
                    text: { en: 'Do you ever feel like people are watching you or following you?', hi: 'क्या आपको कभी ऐसा लगता है कि लोग आपको देख रहे हैं या आपका पीछा कर रहे हैं?' },
                    scale: [
                        { value: 0, label: { en: 'No', hi: 'नहीं' } },
                        { value: 1, label: { en: 'Yes', hi: 'हां' } }
                    ],
                    disorders: ['schizophrenia', 'delusional_disorder'],
                    safety: true
                }
            ],
            cutoff: 1,
            instruments: ['PANSS', 'BPRS', 'CAARMS']
        }
    ],
    
    disorders: {
        depression_mdd: {
            name: { en: 'Major Depressive Disorder', hi: 'प्रमुख अवसादग्रस्तता विकार' },
            tier: 1,
            dsm5: 'Major Depressive Disorder',
            icd11: '6A70',
            description: { 
                en: 'Persistent sadness, loss of interest, and functional impairment lasting at least 2 weeks',
                hi: 'कम से कम 2 सप्ताह तक चलने वाली लगातार उदासी, रुचि की हानि, और कार्यात्मक हानि'
            }
        },
        depression_persistent: {
            name: { en: 'Persistent Depressive Disorder', hi: 'लगातार अवसादग्रस्तता विकार' },
            tier: 1,
            dsm5: 'Persistent Depressive Disorder (Dysthymia)',
            icd11: '6A80.1',
            description: {
                en: 'Chronic depressed mood lasting at least 2 years',
                hi: 'कम से कम 2 साल तक चलने वाला पुराना अवसादग्रस्त मूड'
            }
        },
        gad: {
            name: { en: 'Generalized Anxiety Disorder', hi: 'सामान्यीकृत चिंता विकार' },
            tier: 1,
            dsm5: 'Generalized Anxiety Disorder',
            icd11: '6B02',
            description: {
                en: 'Excessive worry about multiple things for at least 6 months',
                hi: 'कम से कम 6 महीने तक कई चीजों के बारे में अत्यधिक चिंता'
            }
        },
        panic_disorder: {
            name: { en: 'Panic Disorder', hi: 'घबराहट विकार' },
            tier: 1,
            dsm5: 'Panic Disorder',
            icd11: '6B00',
            description: {
                en: 'Recurrent unexpected panic attacks',
                hi: 'बार-बार अप्रत्याशित घबराहट के दौरे'
            }
        },
        social_anxiety: {
            name: { en: 'Social Anxiety Disorder', hi: 'सामाजिक चिंता विकार' },
            tier: 1,
            dsm5: 'Social Anxiety Disorder',
            icd11: '6B00.1',
            description: {
                en: 'Intense fear of social situations and being judged',
                hi: 'सामाजिक स्थितियों और आंके जाने का तीव्र डर'
            }
        },
        ptsd: {
            name: { en: 'Posttraumatic Stress Disorder', hi: 'आघात के बाद तनाव विकार' },
            tier: 2,
            dsm5: 'Posttraumatic Stress Disorder',
            icd11: '6B40',
            description: {
                en: 'Symptoms following exposure to traumatic event',
                hi: 'आघातजनक घटना के संपर्क में आने के बाद लक्षण'
            }
        },
        complex_ptsd: {
            name: { en: 'Complex PTSD', hi: 'जटिल आघात के बाद तनाव विकार' },
            tier: 2,
            dsm5: 'PTSD with dissociative symptoms',
            icd11: '6B41',
            description: {
                en: 'PTSD with additional emotional regulation and self-concept disturbances',
                hi: 'अतिरिक्त भावनात्मक नियमन और आत्म-अवधारणा गड़बड़ी के साथ PTSD'
            }
        },
        insomnia: {
            name: { en: 'Insomnia Disorder', hi: 'अनिद्रा विकार' },
            tier: 2,
            dsm5: 'Insomnia Disorder',
            icd11: '7A00',
            description: {
                en: 'Difficulty initiating or maintaining sleep',
                hi: 'नींद शुरू करने या बनाए रखने में कठिनाई'
            }
        },
        adhd: {
            name: { en: 'Attention-Deficit/Hyperactivity Disorder', hi: 'ध्यान-घाता/अतिसक्रियता विकार' },
            tier: 2,
            dsm5: 'Attention-Deficit/Hyperactivity Disorder',
            icd11: '6A05',
            description: {
                en: 'Persistent pattern of inattention and/or hyperactivity-impulsivity',
                hi: 'ध्यान की कमी और/या अतिसक्रियता-आवेगशीलता का लगातार पैटर्न'
            }
        },
        alcohol_use_disorder: {
            name: { en: 'Alcohol Use Disorder', hi: 'शराब उपयोग विकार' },
            tier: 1,
            dsm5: 'Alcohol Use Disorder',
            icd11: '6C40',
            description: {
                en: 'Problematic pattern of alcohol use leading to impairment',
                hi: 'शराब के उपयोग की समस्याग्रस्त पैटर्न जिससे हानि होती है'
            }
        },
        schizophrenia: {
            name: { en: 'Schizophrenia', hi: 'सिज़ोफ्रेनिया' },
            tier: 4,
            dsm5: 'Schizophrenia',
            icd11: '6A20',
            description: {
                en: 'Persistent psychotic symptoms including delusions and hallucinations',
                hi: 'भ्रम और मतिभ्रम सहित लगातार मनोवैज्ञानिक लक्षण'
            }
        }
    },
    
    instruments: {
        'PHQ-9': {
            name: 'Patient Health Questionnaire-9',
            description: {
                en: 'Depression severity screening',
                hi: 'अवसाद गंभीरता स्क्रीनिंग'
            },
            domains: ['mood'],
            duration: '3-5 minutes'
        },
        'GAD-7': {
            name: 'Generalized Anxiety Disorder-7',
            description: {
                en: 'Anxiety severity screening',
                hi: 'चिंता गंभीरता स्क्रीनिंग'
            },
            domains: ['anxiety'],
            duration: '2-3 minutes'
        },
        'PCL-5': {
            name: 'PTSD Checklist for DSM-5',
            description: {
                en: 'PTSD symptom screening',
                hi: 'PTSD लक्षण स्क्रीनिंग'
            },
            domains: ['trauma'],
            duration: '5-10 minutes'
        },
        'ISI': {
            name: 'Insomnia Severity Index',
            description: {
                en: 'Sleep difficulty assessment',
                hi: 'नींद कठिनाई मूल्यांकन'
            },
            domains: ['sleep'],
            duration: '2-3 minutes'
        },
        'AUDIT-C': {
            name: 'Alcohol Use Disorders Identification Test',
            description: {
                en: 'Alcohol use screening',
                hi: 'शराब उपयोग स्क्रीनिंग'
            },
            domains: ['substance'],
            duration: '1-2 minutes'
        },
        'ASRS-v1.1': {
            name: 'Adult ADHD Self-Report Scale',
            description: {
                en: 'ADHD symptom screening',
                hi: 'ADHD लक्षण स्क्रीनिंग'
            },
            domains: ['neurodevelopmental'],
            duration: '5 minutes'
        },
        'MDQ': {
            name: 'Mood Disorder Questionnaire',
            description: {
                en: 'Bipolar disorder screening',
                hi: 'द्विध्रुवीय विकार स्क्रीनिंग'
            },
            domains: ['mood'],
            duration: '5 minutes'
        },
        'BDI-II': {
            name: 'Beck Depression Inventory-II',
            description: {
                en: 'Depression severity assessment',
                hi: 'अवसाद गंभीरता मूल्यांकन'
            },
            domains: ['mood'],
            duration: '5-10 minutes'
        },
        'BAI': {
            name: 'Beck Anxiety Inventory',
            description: {
                en: 'Anxiety severity assessment',
                hi: 'चिंता गंभीरता मूल्यांकन'
            },
            domains: ['anxiety'],
            duration: '5-10 minutes'
        },
        'STAI': {
            name: 'State-Trait Anxiety Inventory',
            description: {
                en: 'State and trait anxiety measurement',
                hi: 'अवस्था और लक्षण चिंता माप'
            },
            domains: ['anxiety'],
            duration: '10 minutes'
        },
        'IES-R': {
            name: 'Impact of Event Scale-Revised',
            description: {
                en: 'Trauma impact assessment',
                hi: 'आघात प्रभाव मूल्यांकन'
            },
            domains: ['trauma'],
            duration: '5 minutes'
        },
        'CAPS-5': {
            name: 'Clinician-Administered PTSD Scale',
            description: {
                en: 'Comprehensive PTSD assessment',
                hi: 'व्यापक PTSD मूल्यांकन'
            },
            domains: ['trauma'],
            duration: '15-20 minutes'
        },
        'PSQI': {
            name: 'Pittsburgh Sleep Quality Index',
            description: {
                en: 'Sleep quality assessment',
                hi: 'नींद गुणवत्ता मूल्यांकन'
            },
            domains: ['sleep'],
            duration: '5-10 minutes'
        },
        'ESS': {
            name: 'Epworth Sleepiness Scale',
            description: {
                en: 'Daytime sleepiness assessment',
                hi: 'दिन की नींद मूल्यांकन'
            },
            domains: ['sleep'],
            duration: '2-3 minutes'
        },
        'DAST-10': {
            name: 'Drug Abuse Screening Test-10',
            description: {
                en: 'Drug use screening',
                hi: 'ड्रग उपयोग स्क्रीनिंग'
            },
            domains: ['substance'],
            duration: '5 minutes'
        },
        'CAGE-AID': {
            name: 'CAGE-AID',
            description: {
                en: 'Substance use screening',
                hi: 'पदार्थ उपयोग स्क्रीनिंग'
            },
            domains: ['substance'],
            duration: '2 minutes'
        },
        'AQ-10': {
            name: 'Autism Spectrum Quotient-10',
            description: {
                en: 'Autism screening',
                hi: 'ऑटिज्म स्क्रीनिंग'
            },
            domains: ['neurodevelopmental'],
            duration: '5 minutes'
        },
        'Conners-3': {
            name: 'Conners 3 Rating Scales',
            description: {
                en: 'ADHD and behavior assessment',
                hi: 'ADHD और व्यवहार मूल्यांकन'
            },
            domains: ['neurodevelopmental'],
            duration: '10-15 minutes'
        },
        'PANSS': {
            name: 'Positive and Negative Syndrome Scale',
            description: {
                en: 'Psychotic symptom assessment',
                hi: 'मनोवैज्ञानिक लक्षण मूल्यांकन'
            },
            domains: ['psychosis'],
            duration: '30-45 minutes'
        },
        'BPRS': {
            name: 'Brief Psychiatric Rating Scale',
            description: {
                en: 'Psychiatric symptom severity',
                hi: 'मनोचिकित्सा लक्षण गंभीरता'
            },
            domains: ['psychosis'],
            duration: '15-20 minutes'
        },
        'CAARMS': {
            name: 'Comprehensive Assessment of At-Risk Mental States',
            description: {
                en: 'Psychosis risk assessment',
                hi: 'मनोवैज्ञानिक जोखिम मूल्यांकन'
            },
            domains: ['psychosis'],
            duration: '30-60 minutes'
        }
    }
};

const I18N = {
    en: {
        "app.title": "Clinical Pre-Consultation Screening",
        "app.disclaimer": "This tool does not provide a diagnosis. Results are for clinician review only. All data is cleared when you close this page.",
        "stage.consent": "Consent", "stage.context": "Context", "stage.domains": "Domains", "stage.scales": "Scales", "stage.results": "Results",
        "consent.title": "Welcome", "consent.purpose": "This screening tool helps prepare for your clinical consultation by collecting information about your symptoms.",
        "consent.privacy": "Your responses are stored only in your browser's temporary memory. Nothing is sent to any server. Data is destroyed when you close this tab.",
        "consent.agree": "I understand and agree to proceed", "consent.continue": "Continue",
        "context.title": "Patient Information", "context.age": "Age Group", "context.select": "Select...",
        "context.age.pediatric": "Child (under 12)", "context.age.adolescent": "Adolescent (12-17)", "context.age.adult": "Adult (18-64)", "context.age.older": "Older Adult (65+)",
        "context.reason": "Reason for Visit", "context.continue": "Continue",
        "domains.title": "Symptom Domains", "domains.subtitle": "Select the areas you would like to screen.", "domains.continue": "Continue to Assessments",
        "scales.title": "Clinical Assessments", "scales.finish": "Finish & View Results",
        "results.title": "Summary Report", "results.print": "Download PDF Report", "results.clear": "Clear All Data & Restart",
        "safety.title": "Important Safety Information", "safety.message": "Based on your responses, we recommend seeking immediate support.",
        "safety.emergency": "Emergency:", "safety.emergency_num": "Call local emergency services (e.g., 112)",
        "safety.helpline": "Helpline:", "safety.helpline_num": "Kirane (Mental Health): 1800-599-0019", "safety.close": "I Understand",
        "footer.text": "Session-only screening tool. No data is stored or transmitted."
    },
    hi: {
        "app.title": "नैदानिक पूर्व-परामर्श स्क्रीनिंग",
        "app.disclaimer": "यह उपकरण निदान प्रदान नहीं करता है। परिणाम केवल चिकित्सक समीक्षा के लिए हैं। इस पृष्ठ को बंद करने पर सभी डेटा साफ़ हो जाता है।",
        "stage.consent": "सहमति", "stage.context": "संदर्भ", "stage.domains": "डोमेन", "stage.scales": "पैमाने", "stage.results": "परिणाम",
        "consent.title": "स्वागत है", "consent.purpose": "यह स्क्रीनिंग उपकरण आपके लक्षणों के बारे में जानकारी एकत्र करके नैदानिक परामर्श की तैयारी में मदद करता है।",
        "consent.privacy": "आपकी प्रतिक्रियाएं केवल आपके ब्राउज़र की अस्थायी मेमोरी में संग्रहीत होती हैं। कुछ भी किसी सर्वर पर नहीं भेजा जाता है। इस टैब को बंद करने पर डेटा नष्ट हो जाता है।",
        "consent.agree": "मैं समझता हूं और आगे बढ़ने के लिए सहमत हूं", "consent.continue": "जारी रखें",
        "context.title": "रोगी जानकारी", "context.age": "आयु वर्ग", "context.select": "चुनें...",
        "context.age.pediatric": "बच्चा (12 वर्ष से कम)", "context.age.adolescent": "किशोर (12-17)", "context.age.adult": "वयस्क (18-64)", "context.age.older": "वृद्ध वयस्क (65+)",
        "context.reason": "आगमन का कारण", "context.continue": "जारी रखें",
        "domains.title": "लक्षण डोमेन", "domains.subtitle": "उन क्षेत्रों का चयन करें जिनकी आप स्क्रीनिंग करना चाहते हैं।", "domains.continue": "मूल्यांकन पर जाएं",
        "scales.title": "नैदानिक मूल्यांकन", "scales.finish": "समाप्त करें और परिणाम देखें",
        "results.title": "सारांश रिपोर्ट", "results.print": "PDF रिपोर्ट डाउनलोड करें", "results.clear": "सभी डेटा साफ़ करें और पुनः आरंभ करें",
        "safety.title": "महत्वपूर्ण सुरक्षा जानकारी", "safety.message": "आपकी प्रतिक्रियाओं के आधार पर, हम तुरंत सहायता लेने की सलाह देते हैं।",
        "safety.emergency": "आपातकालीन:", "safety.emergency_num": "स्थानीय आपातकालीन सेवाओं पर कॉल करें (उदा. 112)",
        "safety.helpline": "हेल्पलाइन:", "safety.helpline_num": "किरणे (मानसिक स्वास्थ्य): 1800-599-0019", "safety.close": "मैं समझता हूं",
        "footer.text": "केवल सत्र-आधारित स्क्रीनिंग उपकरण। कोई डेटा संग्रहीत या प्रसारित नहीं होता है।"
    }
};

const CLINICAL_DATA = {
    domains: [
        { id: 'mood', name: { en: 'Mood & Depression', hi: 'मूड और अवसाद' }, tier: 1, scales: ['phq9'] },
        { id: 'anxiety', name: { en: 'Anxiety', hi: 'चिंता' }, tier: 1, scales: ['gad7'] },
        { id: 'neurodevelopmental', name: { en: 'Attention & Behavior (Pediatric/Adolescent)', hi: 'ध्यान और व्यवहार (बाल/किशोर)' }, tier: 2, scales: ['vadrs'] }
    ],
    scales: {
        phq9: {
            id: 'phq9', name: { en: 'Patient Health Questionnaire-9', hi: 'पेशेंट हेल्थ क्वेश्चनnaire-9' },
            type: 'list', targetAge: ['adult', 'adolescent', 'older'],
            questions: [
                { id: 'p1', text: { en: 'Little interest or pleasure in doing things', hi: 'चीजों को करने में थोड़ी रुचि या आनंद' }, options: [{v:0, en:'Not at all', hi:'बिल्कुल नहीं'}, {v:1, en:'Several days', hi:'कई दिन'}, {v:2, en:'More than half the days', hi:'आधे से अधिक दिन'}, {v:3, en:'Nearly every day', hi:'लगभग हर दिन'}] },
                { id: 'p2', text: { en: 'Feeling down, depressed, or hopeless', hi: 'उदास, अवसादग्रस्त, या निराश महसूस करना' }, options: [{v:0, en:'Not at all', hi:'बिल्कुल नहीं'}, {v:1, en:'Several days', hi:'कई दिन'}, {v:2, en:'More than half the days', hi:'आधे से अधिक दिन'}, {v:3, en:'Nearly every day', hi:'लगभग हर दिन'}] },
                { id: 'p9', text: { en: 'Thoughts that you would be better off dead, or of hurting yourself', hi: 'विचार कि आप मर जाएं तो बेहतर होगा, या खुद को नुकसान पहुंचाने के' }, options: [{v:0, en:'Not at all', hi:'बिल्कुल नहीं'}, {v:1, en:'Several days', hi:'कई दिन'}, {v:2, en:'More than half the days', hi:'आधे से अधिक दिन'}, {v:3, en:'Nearly every day', hi:'लगभग हर दिन'}], safety: true }
            ]
        },
        gad7: {
            id: 'gad7', name: { en: 'Generalized Anxiety Disorder-7', hi: 'सामान्यीकृत चिंता विकार-7' },
            type: 'list', targetAge: ['adult', 'adolescent', 'older'],
            questions: [
                { id: 'g1', text: { en: 'Feeling nervous, anxious, or on edge', hi: 'घबराहट, चिंता, या बेचैन महसूस करना' }, options: [{v:0, en:'Not at all', hi:'बिल्कुल नहीं'}, {v:1, en:'Several days', hi:'कई दिन'}, {v:2, en:'More than half the days', hi:'आधे से अधिक दिन'}, {v:3, en:'Nearly every day', hi:'लगभग हर दिन'}] },
                { id: 'g2', text: { en: 'Not being able to stop or control worrying', hi: 'चिंता को रोकने या नियंत्रित करने में असमर्थ' }, options: [{v:0, en:'Not at all', hi:'बिल्कुल नहीं'}, {v:1, en:'Several days', hi:'कई दिन'}, {v:2, en:'More than half the days', hi:'आधे से अधिक दिन'}, {v:3, en:'Nearly every day', hi:'लगभग हर दिन'}] }
            ]
        },
        vadrs: {
            id: 'vadrs', name: { en: 'Vanderbilt ADHD Diagnostic Rating Scale (VADRS)', hi: 'वैंडरबिल्ट एडीएचडी डायग्नोस्टिक रेटिंग स्केल' },
            type: 'matrix', targetAge: ['pediatric', 'adolescent'],
            parts: [
                {
                    id: 'symptoms', name: { en: 'Part 1: Symptoms', hi: 'भाग 1: लक्षण' },
                    questions: [
                        // INATTENTION SUBSCALE (Representative subset)
                        { id: 'v1', text: { en: 'Does not pay attention to details or makes careless mistakes', hi: 'विवरणों पर ध्यान नहीं देता या लापरवाही से गलतियां करता है' } },
                        { id: 'v2', text: { en: 'Has difficulty keeping attention to what needs to be done', hi: 'जो करने की आवश्यकता है उस पर ध्यान रखने में कठिनाई होती है' } },
                        { id: 'v3', text: { en: 'Does not seem to listen when spoken to directly', hi: 'सीधे बात करने पर सुनता नहीं प्रतीत होता' } },
                        { id: 'v4', text: { en: 'Does not follow through on instructions and fails to finish activities', hi: 'निर्देशों का पालन नहीं करता और गतिविधियों को पूरा करने में विफल रहता है' } },
                        { id: 'v5', text: { en: 'Has difficulty organizing tasks and activities', hi: 'कार्यों और गतिविधियों को व्यवस्थित करने में कठिनाई होती है' } },
                        { id: 'v6', text: { en: 'Avoids tasks that require ongoing mental effort', hi: 'ऐसे कार्यों से बचता है जिनमें निरंतर मानसिक प्रयास की आवश्यकता होती है' } },
                        { id: 'v7', text: { en: 'Loses things necessary for tasks or activities', hi: 'कार्यों या गतिविधियों के लिए आवश्यक चीजें खो देता है' } },
                        { id: 'v8', text: { en: 'Is easily distracted by extraneous stimuli', hi: 'बाहरी उत्तेजनाओं से आसानी से विचलित हो जाता है' } },
                        { id: 'v9', text: { en: 'Is forgetful in daily activities', hi: 'दैनिक गतिविधियों में भूलक्कड़ है' } },
                        // PERFORMANCE SUBSCALE (Representative subset)
                        { id: 'v48', text: { en: 'Overall school performance', hi: 'समग्र स्कूल प्रदर्शन' }, isPerformance: true },
                        { id: 'v49', text: { en: 'Reading', hi: 'पठन' }, isPerformance: true },
                        { id: 'v50', text: { en: 'Relationship with parents', hi: 'माता-पिता के साथ संबंध' }, isPerformance: true }
                        // NOTE: Paste remaining VADRS questions (10-47, 51-55) here following the exact same {id, text} structure.
                    ]
                }
            ],
            matrixOptions: [
                { v: 0, en: 'Never', hi: 'कभी नहीं' },
                { v: 1, en: 'Occasionally', hi: 'कभी-कभी' },
                { v: 2, en: 'Often', hi: 'अक्सर' },
                { v: 3, en: 'Very Often', hi: 'बहुत अक्सर' }
            ],
            performanceOptions: [
                { v: 1, en: 'Excellent', hi: 'उत्कृष्ट' },
                { v: 2, en: 'Above Average', hi: 'औसत से ऊपर' },
                { v: 3, en: 'Average', hi: 'औसत' },
                { v: 4, en: 'Somewhat of a Problem', hi: 'थोड़ी समस्या' },
                { v: 5, en: 'Problematic', hi: 'समस्याग्रस्त' }
            ]
        }
    },
    disorders: {
        depression_mdd: { name: { en: 'Major Depressive Disorder', hi: 'प्रमुख अवसादग्रस्तता विकार' }, tier: 1, dsm5: 'Major Depressive Disorder', icd11: '6A70' },
        anxiety_gad: { name: { en: 'Generalized Anxiety Disorder', hi: 'सामान्यीकृत चिंता विकार' }, tier: 1, dsm5: 'Generalized Anxiety Disorder', icd11: '6B02' },
        neuro_adhd: { name: { en: 'Attention-Deficit/Hyperactivity Disorder', hi: 'ध्यान-घाटा/अतिसक्रियता विकार' }, tier: 2, dsm5: 'ADHD', icd11: '6A05' }
    }
};
