/** CY-BOCS severity total and supplied pediatric score bands. */
export function score(values, questions, form) {
    const nums = values.map(Number);
    const obs = nums.slice(0, 5).reduce((sum, value) => sum + value, 0);
    const comp = nums.slice(5).reduce((sum, value) => sum + value, 0);
    const total = obs + comp;
    const band = total <= 7 ? 'Subclinical' : total <= 15 ? 'Mild' : total <= 23 ? 'Moderate' : total <= 31 ? 'Severe' : 'Extreme';
    return [
        { name: form.name + ' total', score: total + '/40', severity: band + ' source score band; clinician review, not diagnosis', notDiagnostic: true },
        { name: 'CY-BOCS obsessions subtotal', score: obs + '/20', severity: 'Items 1–5', notDiagnostic: true },
        { name: 'CY-BOCS compulsions subtotal', score: comp + '/20', severity: 'Items 6–10', notDiagnostic: true }
    ];
}
