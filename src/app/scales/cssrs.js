export function score(values, questions) {
    // Record the interview responses without assigning an automated risk category.
    const responses = questions.map((q, i) => q.id.slice(1) + ': ' + (values[i] ? 'Yes' : 'No'));
    return [{
        name: 'C-SSRS · Since last contact', score: responses.join(', '),
        severity: 'Review with interviewing clinician', aboveCutoff: values.some(v => v === 1)
    }];
}
