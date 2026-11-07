export function score(values) {
    const raw = values.reduce((sum, value) => sum + value, 0);
    return [{ name: 'Panic Disorder Severity Scale — Self-Report (PDSS-SR)',
        score: (raw / values.length).toFixed(2) + '/4',
        severity: 'Mean of seven past-week ratings; raw total ' + raw + '/28. Descriptive, not diagnostic.',
        notDiagnostic: true }];
}
