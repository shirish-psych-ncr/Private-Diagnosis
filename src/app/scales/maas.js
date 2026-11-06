export function score(values) {
    const mean = values.reduce((sum, v) => sum + v, 0) / values.length;
    return [{ name: 'MAAS', score: mean.toFixed(2) + '/6', severity: 'Mean attention and awareness rating' }];
}
