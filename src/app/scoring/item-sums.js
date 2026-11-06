/** Sum the published item keys. Subscales may overlap and remain separate. */
export function scoreItemSums(values, form) {
    const { groups, total, multiplier } = form.sumScores;
    const min = form.matrixOptions[0].v;
    const max = form.matrixOptions.at(-1).v;
    const questions = form.parts.flatMap(part => part.questions);
    const keyed = values.map((value, i) => questions[i].reverse ? min + max - value : value);
    function row(name, items) {
        const score = items.reduce((sum, n) => sum + keyed[n - 1], 0) * multiplier;
        return { name, score: score + '/' + (items.length * max * multiplier), severity: 'Range ' +
            (items.length * min * multiplier) + '–' + (items.length * max * multiplier) };
    }
    const results = total ? [row(form.name, keyed.map((_, i) => i + 1))] : [];
    for (const [group, items] of Object.entries(groups)) {
        results.push(row(form.id.toUpperCase() + ' · ' + group, items));
    }
    return results;
}
