export function score(values) {
    const anxiety = [0, 2, 4, 6, 8, 10, 12].reduce((sum, index) => sum + values[index], 0);
    const depression = [1, 3, 5, 7, 9, 11, 13].reduce((sum, index) => sum + values[index], 0);
    return [
        { name: 'HADS — Anxiety', score: anxiety + '/21', severity: 'Self-report subscale; not diagnostic', notDiagnostic: true },
        { name: 'HADS — Depression', score: depression + '/21', severity: 'Self-report subscale; not diagnostic', notDiagnostic: true }
    ];
}
