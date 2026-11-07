/** EDE-Q global and subscale means, plus separate behavioral-frequency counts. */
export function score(values, questions, form) {
    const { groups } = form.meanScores;
    const mean = items => items.reduce((sum, index) => sum + Number(values[index - 1]), 0) / items.length;
    const means = Object.entries(groups).map(([label, items]) => [label, mean(items)]);
    const rows = means.map(([label, value]) => ({ name: form.name + ' - ' + label, score: value.toFixed(2) + '/6',
        severity: 'Subscale mean; descriptive, not diagnostic', notDiagnostic: true }));
    rows.unshift({ name: form.name + ' global score', score: (means.reduce((sum, [, value]) => sum + value, 0) / means.length).toFixed(2) + '/6',
        severity: 'Global mean of four subscales; descriptive, not diagnostic', notDiagnostic: true });
    for (const index of form.frequencyItems || []) rows.push({ name: form.name + ' - ' + questions[index - 1].text,
        score: String(values[index - 1]), severity: index === 15 ? 'Days in past 28 days' : 'Reported number of times in past 28 days', notDiagnostic: true });
    return rows;
}
