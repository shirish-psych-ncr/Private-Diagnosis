export function score(values) {
    const answered = values.filter(Number.isFinite).length;
    const total = values.reduce((sum, value) => sum + (Number.isFinite(value) ? value : 0), 0);
    return [{
        name: 'Kessler Psychological Distress Scale (K10)',
        score: total + '/50',
        severity: 'Nonspecific psychological distress - past 30 days',
        notDiagnostic: true,
        answered,
        total: 10,
    }];
}
