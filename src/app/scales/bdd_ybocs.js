/** BDD-YBOCS total with obsession, activity, insight and avoidance components. */
export function score(values, questions, form) {
    const n = values.map(Number);
    const obs = n.slice(0, 5).reduce((sum, value) => sum + value, 0);
    const acts = n.slice(5, 10).reduce((sum, value) => sum + value, 0);
    const total = n.reduce((sum, value) => sum + value, 0);
    return [
        { name: form.name + ' total', score: total + '/48', severity: 'Past-week clinician rating; descriptive only', notDiagnostic: true },
        { name: 'BDD-YBOCS thoughts subtotal', score: obs + '/20', severity: 'Items 1–5', notDiagnostic: true },
        { name: 'BDD-YBOCS activities subtotal', score: acts + '/20', severity: 'Items 6–10', notDiagnostic: true },
        { name: 'BDD-YBOCS insight', score: n[10] + '/4', severity: 'Item 11', notDiagnostic: true },
        { name: 'BDD-YBOCS avoidance', score: n[11] + '/4', severity: 'Item 12', notDiagnostic: true }
    ];
}
