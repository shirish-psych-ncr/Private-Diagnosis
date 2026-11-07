export function score(values, questions) {
    const fear = values.reduce((sum, value, index) => sum + (questions[index].subscale === 'fear' ? value : 0), 0);
    const avoidance = values.reduce((sum, value, index) => sum + (questions[index].subscale === 'avoidance' ? value : 0), 0);
    return [
        { name: 'LSAS — Fear', score: fear + '/72', severity: 'Self-report subscale; not diagnostic', notDiagnostic: true },
        { name: 'LSAS — Avoidance', score: avoidance + '/72', severity: 'Self-report subscale; not diagnostic', notDiagnostic: true },
        { name: 'Liebowitz Social Anxiety Scale (LSAS) — Total', score: (fear + avoidance) + '/144', severity: 'Fear plus avoidance; interpret in context, not diagnostic', notDiagnostic: true }
    ];
}
