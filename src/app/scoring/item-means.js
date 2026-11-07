export function scoreMeans(values, form) {
    const { groups, reverse, overall } = form.meanScores;
    const low = form.matrixOptions[0].v;
    const high = form.matrixOptions.at(-1).v;
    const keyed = values.map((v, i) => reverse.includes(i + 1) ? low + high - v : v);
    const mean = numbers => numbers.reduce((sum, v) => sum + v, 0) / numbers.length;
    const means = Object.entries(groups).map(([label, items]) =>
        [label, mean(items.map(n => keyed[n - 1]))]);
    const rows = means.map(([label, value]) => ({
        name: form.name + ' · ' + label, score: value.toFixed(2) + '/' + high, severity: 'Subscale mean'
    }));
    if (overall) {
        const total = mean(overall === 'subscales' ? means.map(([, value]) => value) : keyed);
        rows.unshift({ name: form.name, score: total.toFixed(2) + '/' + high, severity: 'Overall mean' });
    }
    return rows;
}
