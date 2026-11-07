export function score(values) {
    const symptoms = values.slice(0, 13).reduce((a, b) => a + b, 0);
    const positive = symptoms >= 7 && values[13] === 1 && values[14] >= 2;
    const impairment = ['None', 'Minor', 'Moderate', 'Serious'][values[14]];
    return [
        { name: 'Mood Disorder Questionnaire', score: symptoms + '/13',
            severity: positive ? 'Positive screen · clinician follow-up' : 'Screening criteria not met', aboveCutoff: positive },
        { name: 'MDQ · Symptoms during the same period', score: ['No', 'Yes', 'Not applicable'][values[13]], severity: 'Impact: ' + impairment },
        { name: 'MDQ · History', score: 'Family: ' + (values[15] ? 'Yes' : 'No'),
            severity: 'Previously diagnosed: ' + (values[16] ? 'Yes' : 'No') }
    ];
}
