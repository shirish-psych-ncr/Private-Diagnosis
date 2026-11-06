export function score(values, questions) {
    const totals = new Map();
    questions.forEach((q, i) => {
        const value = q.reverse ? 7 - values[i] : values[i];
        totals.set(q.dimension, (totals.get(q.dimension) || 0) + value);
    });
    return Array.from(totals, ([dimension, total]) => ({
        name: 'Ryff · ' + dimension, score: total + '/84', severity: 'Subscale total (14–84)'
    }));
}
