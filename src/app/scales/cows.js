/** COWS clinician total and supplied severity bands. */
export function score(values, questions, form) {
    const total = values.reduce((sum, value) => sum + Number(value), 0);
    const severity = total < 5 ? 'Below the supplied withdrawal bands'
        : total <= 12 ? 'Mild' : total <= 24 ? 'Moderate' : total <= 36 ? 'Moderately severe' : 'Severe';
    return [{ name: form.name + ' total', score: total + '/48', severity: severity + '; interpret with clinical assessment', notDiagnostic: true }];
}
