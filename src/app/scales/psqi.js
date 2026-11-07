function category(value, bounds) {
    for (const [limit, score] of bounds) if (value <= limit) return score;
    return bounds.at(-1)[1];
}

/** Reconstruct the seven PSQI component scores from the supplied scoring key. */
export function score(values, questions, form) {
    const a = Object.fromEntries(questions.map((question, i) => [question.id, Number(values[i])]));
    const latency = category(a.psqi_2, [[15, 0], [30, 1], [60, 2], [Infinity, 3]]);
    const c2raw = latency + a.psqi_5a;
    const c2 = category(c2raw, [[0, 0], [2, 1], [4, 2], [6, 3]]);
    const c3 = a.psqi_4 >= 7 ? 0 : a.psqi_4 >= 6 ? 1 : a.psqi_4 >= 5 ? 2 : 3;
    const bedtime = a.psqi_1;
    const wake = a.psqi_3;
    const inBedHours = ((wake - bedtime + 1440) % 1440) / 60;
    const efficiency = inBedHours > 0 ? a.psqi_4 / inBedHours * 100 : 0;
    const c4 = efficiency >= 85 ? 0 : efficiency >= 75 ? 1 : efficiency >= 65 ? 2 : 3;
    const disturbance = ['b','c','d','e','f','g','h','i','j'].reduce((sum, letter) => sum + a['psqi_5' + letter], 0);
    const c5 = disturbance === 0 ? 0 : disturbance <= 9 ? 1 : disturbance <= 18 ? 2 : 3;
    const c7raw = a.psqi_7 + a.psqi_8;
    const c7 = category(c7raw, [[0, 0], [2, 1], [4, 2], [6, 3]]);
    const components = [a.psqi_9, c2, c3, c4, c5, a.psqi_6, c7];
    const total = components.reduce((sum, value) => sum + value, 0);
    const labels = ['Subjective sleep quality','Sleep latency','Sleep duration','Habitual sleep efficiency','Sleep disturbances','Use of sleep medication','Daytime dysfunction'];
    const rows = components.map((value, i) => ({ name: 'PSQI - ' + labels[i], score: value + '/3',
        severity: i === 3 ? `Component score; calculated efficiency ${efficiency.toFixed(1)}%` : 'Component score; descriptive, not diagnostic', notDiagnostic: true }));
    rows.unshift({ name: form.name + ' global score', score: total + '/21',
        severity: total > 5 ? 'Above the supplied >5 poor-sleep-quality threshold; not diagnostic' : 'At or below the supplied threshold; not diagnostic', notDiagnostic: true });
    return rows;
}
