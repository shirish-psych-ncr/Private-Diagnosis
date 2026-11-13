import { CLINICAL_DATA } from './state.js';

// Direction of the keyed score. A scale midpoint is descriptive, not a clinical threshold.
const meaning = {
    aaq2: 'greater difficulty making room for uncomfortable thoughts and feelings',
    aase_confidence: 'more confidence in avoiding alcohol in these situations',
    aase_temptation: 'a stronger temptation to drink in these situations',
    adnm20: 'more difficulties following the stressful event',
    asi: 'more fear of anxiety-related sensations',
    asrm: 'more self-reported symptoms of elevated mood or activation',
    cfi: 'greater perceived flexibility in thinking about difficult situations',
    dass21: 'more symptoms on this dimension during the past week',
    ders: 'more difficulty regulating emotions in the area measured',
    dmqr: 'more frequent drinking for this reason',
    dts: 'greater perceived ability to tolerate distress',
    ees: 'more outward expression of emotion',
    ffoci_sf: 'stronger endorsement of the named personality trait',
    flourishing: 'greater perceived well-being',
    ipip120: 'stronger endorsement of the named personality trait',
    ius: 'greater difficulty tolerating uncertainty',
    mcq30: 'stronger endorsement of the thoughts or beliefs measured here',
    msibpd: 'more endorsed features on the borderline personality screener',
    rgpts: 'more frequent or strongly endorsed paranoid thoughts',
    scared_child: 'more anxiety symptoms reported by the child',
    scared_parent: 'more anxiety symptoms observed by the parent',
    spin: 'more social fear, avoidance or discomfort',
    sseit: 'greater self-rated emotional intelligence',
    tcq: 'more frequent use of this thought-control strategy',
    vq: 'more of the named pattern in daily life'
};

function position(score, low, high) {
    const middle = (low + high) / 2;
    if (score === low) return 'At the lowest possible score.';
    if (score === high) return 'At the highest possible score.';
    if (score === middle) return 'At the scale midpoint.';
    return score < middle ? 'Below the scale midpoint.' : 'Above the scale midpoint.';
}

export function scoreReading(row) {
    const { name, score, severity } = row;
    if (name === 'Kessler Psychological Distress Scale (K10)')
        return 'Higher totals indicate more nonspecific psychological distress. This screening result is not a diagnosis; interpretation and any thresholds depend on the setting and population.';
    if (name === 'Hypomania Checklist (HCL-32-R1)')
        return 'This is a self-report checklist of experiences during higher-energy periods. The total is descriptive and does not establish a bipolar-spectrum diagnosis.';
    if (/^(Hamilton Depression Rating Scale|Montgomery–Åsberg Depression Rating Scale|Young Mania Rating Scale|Bipolar Depression Rating Scale|Beck Depression Inventory)/.test(name))
        return 'This total supports symptom description and monitoring. It is not a diagnosis; interpret it with the correct version, administration method and clinical context.';
    if (/^(Hamilton Anxiety Rating Scale|Penn State Worry Questionnaire|Beck Anxiety Inventory|Panic Disorder Severity Scale|MIA —|LSAS —|Liebowitz Social Anxiety Scale|Brief Fear of Negative Evaluation|HADS)/.test(name))
        return 'This score describes the symptoms or experiences covered by the selected form. It is not a diagnosis; interpret with the correct administration method and clinical context.';
    if (name === 'QIDS-SR16') {
        // https://ids-qids.org/interpretation.html
        const n = parseInt(score, 10);
        const band = ['minimal', 'mild', 'moderate', 'severe', 'very severe'][[5,10,15,20,27].findIndex(max => n <= max)];
        return 'Past-week depressive symptoms fall in the ' + band + ' range.';
    }
    const fraction = /^(\d+(?:\.\d+)?)\/(\d+(?:\.\d+)?)$/.exec(score);
    if (fraction) {
        const value = Number(fraction[1]), max = Number(fraction[2]);
        let direction, min;
        for (const [id, description] of Object.entries(meaning)) {
            const form = CLINICAL_DATA.scales[id];
            if (!form || !(name === form.name || name.startsWith(form.name + ' · ') || name.startsWith(id.toUpperCase() + ' · '))) continue;
            direction = description;
            min = form.meanScores ? form.matrixOptions[0].v : Number(/^Range (\d+)/.exec(severity)?.[1]);
            if (id === 'mcq30' && name.endsWith('Cognitive confidence')) direction = 'less confidence in memory';
            if (id === 'vq') direction = name.endsWith('Progress') ? 'more action in line with personal values' : 'more interference with living by personal values';
            break;
        }
        if (name.startsWith('Ryff · ')) { direction = 'greater well-being in this area'; min = 14; }
        if (name === 'MAAS') { direction = 'more attention to the present moment'; min = 1; }
        if (name.startsWith('UGDS-GS · ')) {
            direction = name.endsWith('affirmation') ? 'stronger affirmation of one’s gender' : 'more reported gender-related distress';
            min = 1;
        }
        if (direction && Number.isFinite(min)) return position(value, min, max) + ' Higher scores indicate ' + direction + '.';
    }
    if (name.startsWith('C-SSRS')) return row.aboveCutoff ? 'A yes response needs direct review with the interviewing clinician.' : 'No administered question was endorsed. Review current safety with the clinician.';
    if (name === 'Mood Disorder Questionnaire') return row.aboveCutoff ? 'The combination of symptoms, timing and impact meets the screening criteria for bipolar disorder. Discuss a diagnostic assessment.' : 'The reported symptoms, timing and impact do not meet the combined screening criteria for bipolar disorder.';
    if (name.startsWith('ITQ · ') && fraction) return severity + '. Higher totals indicate more symptoms in this area. The screening pattern also depends on impairment.';
    if (row.ratingRegister) return severity + '. The maximum is the highest individual rating. See the entries below for the affected areas.';
    if (row.eventRegister) return 'Event history only. No diagnostic score is produced; review the recorded history with the clinician.';
    if (row.notDiagnostic && row.answered < row.total) return 'Incomplete. Interpret the answered items individually.';
    if (row.pdRegister) return severity + '. See the profile below for individual dimensions and their interpretation.';
    if (name === 'VADRS') return severity + '. The ADHD screen considers both symptom counts and difficulty functioning.';
    if (fraction && typeof row.aboveCutoff === 'boolean' && !row.notDiagnostic) {
        return severity + '. ' + (row.aboveCutoff ? 'The score reaches the screening threshold for follow-up.' : 'The score falls below the screening threshold.');
    }
    if (row.notDiagnostic) {
        if (score.includes('%')) return severity + '. The percentage summarizes how often dissociative experiences were reported.';
        if (name === CLINICAL_DATA.scales.phq15?.name?.en || name === CLINICAL_DATA.scales.phq15?.name?.hi)
            return severity + '. Higher scores reflect greater reported burden from physical symptoms.';
        if (name === CLINICAL_DATA.scales.clinical_anger_scale?.name?.en || name === CLINICAL_DATA.scales.clinical_anger_scale?.name?.hi)
            return severity + '. Higher scores reflect more difficulties related to anger.';
    }
    return severity;
}
