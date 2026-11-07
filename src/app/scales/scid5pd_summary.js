/** Scoring for the SCID-5-PD summary sheet; records clinician tallies only. */
export function score(values, questions) {
    const a = Object.fromEntries(questions.map((question, i) => [question.id, Number(values[i])]));
    const specs = [
        ['avoidant', 'Avoidant', 7, 4, false], ['dependent', 'Dependent', 8, 5, false],
        ['ocpd', 'Obsessive-compulsive', 8, 4, false], ['paranoid', 'Paranoid', 7, 4, true],
        ['schizotypal', 'Schizotypal', 9, 5, true], ['schizoid', 'Schizoid', 7, 4, true],
        ['histrionic', 'Histrionic', 9, 5, false], ['narcissistic', 'Narcissistic', 9, 5, false],
        ['borderline', 'Borderline', 9, 5, false], ['antisocial', 'Antisocial', 7, 3, false]
    ];
    const rows = [];
    for (const [id, name, max, threshold, hasB] of specs) {
        const count = a['scid_' + id + '_count'];
        const qualifying = count >= threshold && (!hasB || a['scid_' + id + '_b'] === 1);
        if (id === 'antisocial') {
            const conduct = a.scid_antisocial_conduct >= 2;
            const general = a.scid_antisocial_general === 1;
            rows.push({ name: name + ' threshold-criterion count', score: count + '/' + max,
                severity: `${count} threshold criteria; threshold ${threshold}; clinician review required`, notDiagnostic: true });
            rows.push({ name: name + ' childhood conduct criterion', score: a.scid_antisocial_conduct + '/15',
                severity: 'At least 2 threshold conduct symptoms are required by the supplied score sheet', notDiagnostic: true });
            rows.push({ name: name + ' summary tally', score: qualifying && conduct && general ? 'All entered thresholds met' : 'Not all entered thresholds met',
                severity: 'Also verify all SCID general criteria and exclusions; not a diagnosis' });
        } else {
            rows.push({ name: name + ' threshold-criterion count', score: count + '/' + max,
                severity: count + ' rated threshold; threshold ' + threshold + (hasB ? (a['scid_' + id + '_b'] === 1 ? '; Criterion B clear' : '; Criterion B exclusion applies') : ''), notDiagnostic: true });
            rows.push({ name: name + ' summary tally', score: qualifying ? 'Item threshold met' : 'Item threshold not met',
                severity: 'Clinician must apply general criteria, exclusions, and clinical judgment; not a diagnosis' });
        }
        rows.push({ name: name + ' dimensional profile', score: a['scid_' + id + '_sum'] + '/' + (max * 2),
            severity: 'Sum of 0–2 item ratings; descriptive profile', notDiagnostic: true });
        rows.push({ name: name + ' clinically significant features', score: !qualifying && a['scid_' + id + '_features'] === 1 ? 'Present' : 'Not reported / not applicable',
            severity: 'Summary-sheet feature flag; clinician judgment required' });
    }
    rows.push({ name: 'Other specified personality disorder distress / impairment', score: a.scid_other_specified ? 'Present' : 'Not present',
        severity: 'Clinician-entered summary-sheet item' });
    rows.push({ name: 'Interview information quality', score: String(a.scid_quality), severity: '1 poor to 4 excellent' });
    rows.push({ name: 'Interview duration', score: String(a.scid_duration) + ' minutes', severity: 'Recorded from interview' });
    return rows;
}
