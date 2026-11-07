/** PID-5-BF adult overall and five trait-domain raw/average scores. */
export function score(values, questions, form) {
    const numbers = values.map(Number);
    const sum = items => items.reduce((total, index) => total + numbers[index - 1], 0);
    const rows = [{ name: form.name + ' raw total', score: sum(numbers.map((_, i) => i + 1)) + '/75',
        severity: 'Average: ' + (sum(numbers.map((_, i) => i + 1)) / 25).toFixed(2) + '/3; dimensional self-report, not diagnostic', notDiagnostic: true }];
    for (const [domain, items] of Object.entries(form.traitGroups)) {
        const raw = sum(items);
        rows.push({ name: form.name + ' - ' + domain, score: raw + '/15',
            severity: 'Average: ' + (raw / items.length).toFixed(2) + '/3; dimensional profile, not diagnostic', notDiagnostic: true });
    }
    return rows;
}
