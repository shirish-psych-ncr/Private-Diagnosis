const DOMAIN_GROUPS = [
    { id: 'mood_energy', label: 'domain-group.mood_energy', domains: [
        'mood', 'bipolar', 'sleep', 'fatigue', 'perinatal_wellbeing', 'perimenopause'
    ] },
    { id: 'anxiety_trauma', label: 'domain-group.anxiety_trauma', domains: [
        'anxiety', 'worry', 'panic', 'social_anxiety', 'trauma', 'dissociation'
    ] },
    { id: 'development', label: 'domain-group.development', domains: [
        'neurodevelopmental', 'autistic_traits', 'demand_avoidance', 'child_anxiety'
    ] },
    { id: 'thoughts_behavior', label: 'domain-group.thoughts_behavior', domains: [
        'psychosis', 'ocd', 'rumination', 'anger', 'body_dysmorphic',
        'body_focused_repetitive_behaviors', 'hoarding', 'gambling'
    ] },
    { id: 'substance_safety', label: 'domain-group.substance_safety', domains: [
        'substance', 'youth_substance', 'substance_recovery', 'withdrawal',
        'self_injury', 'suicide_followup'
    ] },
    { id: 'eating_body', label: 'domain-group.eating_body', domains: [
        'eating', 'feeding', 'gender', 'sexual_motivation'
    ] },
    { id: 'personality_relationships', label: 'domain-group.personality_relationships', domains: [
        'personality', 'personality_traits', 'maladaptive_personality_traits',
        'borderline_features', 'attachment_patterns', 'emotion_regulation',
        'emotional_intelligence'
    ] },
    { id: 'health_function', label: 'domain-group.health_function', domains: [
        'somatic', 'functional_impairment', 'movement', 'cognitive_screening',
        'quality_of_life'
    ] },
    { id: 'wellbeing_coping', label: 'domain-group.wellbeing_coping', domains: [
        'wellbeing', 'coping_strategies', 'mindfulness', 'psychological_flexibility',
        'values_based_living', 'self_efficacy'
    ] },
    { id: 'broad_screening', label: 'domain-group.broad_screening', domains: [
        'general_distress', 'cross_cutting_symptoms', 'multidomain_symptoms', 'mini_screen'
    ] }
];

export { DOMAIN_GROUPS };
