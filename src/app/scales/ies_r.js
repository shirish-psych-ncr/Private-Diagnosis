const groups = {
    Intrusion: [1, 2, 3, 6, 9, 14, 16, 20],
    Avoidance: [5, 7, 8, 11, 12, 13, 17, 22],
    Hyperarousal: [4, 10, 15, 18, 19, 21]
};

export function score(values) {
    const rows = [{ name: 'Impact of Event Scale–Revised (IES-R) — Total',
        score: values.reduce((sum, value) => sum + value, 0) + '/88',
        severity: 'Past-week event-related distress; not diagnostic', notDiagnostic: true }];
    for (const [label, numbers] of Object.entries(groups)) {
        const mean = numbers.reduce((sum, number) => sum + values[number - 1], 0) / numbers.length;
        rows.push({ name: 'IES-R — ' + label, score: mean.toFixed(2) + '/4',
            severity: 'Descriptive subscale mean; not diagnostic', notDiagnostic: true });
    }
    return rows;
}
