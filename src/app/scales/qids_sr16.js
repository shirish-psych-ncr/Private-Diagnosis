export function score(values) {
    // Sleep, appetite/weight, and psychomotor change each contribute one domain.
    const sleep = Math.max(...values.slice(0, 4));
    const appetite = Math.max(...values.slice(5, 9));
    const movement = Math.max(...values.slice(14, 16));
    const total = sleep + values[4] + appetite + values.slice(9, 14).reduce((a, b) => a + b, 0) + movement;
    return [{ name: 'QIDS-SR16', score: total + '/27', severity: 'Nine symptom domains · past week' }];
}
