/** OCI-R provides both the conventional raw total and subscale distress means. */
export function score(values, questions, form) {
    const groups = form.meanScores.groups;
    const mean = items => items.reduce((sum, index) => sum + Number(values[index - 1]), 0) / items.length;
    const rows = [{ name: form.name + ' raw total', score: values.reduce((sum, value) => sum + Number(value), 0) + '/72',
        severity: '0-72; descriptive self-report, not diagnostic', notDiagnostic: true }];
    for (const [label, items] of Object.entries(groups)) rows.push({
        name: form.name + ' - ' + label, score: mean(items).toFixed(2) + '/4', severity: 'Subscale mean; descriptive, not diagnostic', notDiagnostic: true
    });
    rows.push({ name: form.name + ' overall distress mean', score: (values.reduce((sum, value) => sum + Number(value), 0) / values.length).toFixed(2) + '/4',
        severity: 'Overall mean; descriptive, not diagnostic', notDiagnostic: true });
    return rows;
}
