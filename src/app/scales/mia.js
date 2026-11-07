export function score(values, questions) {
    const rows = [];
    for (const dimension of ['accompanied', 'alone']) {
        const ratings = values.filter((value, index) => questions[index].subscale === dimension && value > 0);
        const mean = ratings.length ? ratings.reduce((sum, value) => sum + value, 0) / ratings.length : 0;
        rows.push({ name: 'MIA — Avoidance ' + dimension, score: mean.toFixed(2) + '/5',
            severity: ratings.length ? 'Descriptive mean across ' + ratings.length + ' applicable situations; not diagnostic' : 'No applicable situations rated', notDiagnostic: true });
    }
    return rows;
}
