export function score(values) {
    const affirmation = new Set([1, 3, 4, 5]);
    return [['Gender affirmation', true], ['Gender dysphoria', false]].map(([label, included]) => {
        const items = values.filter((v, i) => affirmation.has(i + 1) === included);
        const mean = items.reduce((sum, v) => sum + v, 0) / items.length;
        return { name: 'UGDS-GS · ' + label, score: mean.toFixed(2) + '/5', severity: 'Subscale mean' };
    });
}
