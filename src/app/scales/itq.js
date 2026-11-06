import { state } from '../state.js';

export function score(values) {
    function profile(items) {
        const endorsed = items.map(v => v >= 2);
        const clusters = [0, 2, 4].every(i => endorsed[i] || endorsed[i + 1]);
        return {
            meets: clusters && endorsed.slice(6).some(Boolean),
            sum: items.slice(0, 6).reduce((a, b) => a + b, 0)
        };
    }
    const ptsd = profile(values.slice(0, 9));
    const dso = profile(values.slice(9));
    const pattern = ptsd.meets
        ? (dso.meets ? 'CPTSD screening pattern' : 'PTSD screening pattern')
        : 'PTSD/CPTSD screening criteria not met';
    const results = [
        { name: 'ITQ · PTSD symptoms', score: ptsd.sum + '/24', severity: pattern, aboveCutoff: ptsd.meets },
        { name: 'ITQ · Disturbances in self-organization', score: dso.sum + '/24', severity: 'Symptom total' }
    ];
    for (const [key, name] of [['experience', 'Index experience'], ['timing', 'Time since experience']]) {
        const value = state.formContext['itq:' + key]?.trim();
        if (value) results.push({ name: 'ITQ · ' + name, score: '—', severity: value });
    }
    return results;
}
