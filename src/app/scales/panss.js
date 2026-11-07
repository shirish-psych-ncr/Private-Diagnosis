const groups = [
    ['Positive', 'positive', 7],
    ['Negative', 'negative', 7],
    ['General psychopathology', 'general', 16]
];

export function score(values, questions) {
    const rows = groups.map(([label, key, size]) => {
        const total = values.reduce((sum, value, index) => sum + (questions[index].subscale === key ? value : 0), 0);
        return { name: 'PANSS — ' + label, score: total + '/' + (size * 7),
            severity: 'Clinician-rated symptom severity; not diagnostic', notDiagnostic: true };
    });
    const total = values.reduce((sum, value) => sum + value, 0);
    rows.push({ name: 'PANSS — Total', score: total + '/210',
        severity: 'Sum of 30 clinician ratings; interpret using the authorized manual', notDiagnostic: true });
    return rows;
}
