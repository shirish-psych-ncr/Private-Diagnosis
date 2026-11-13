import { state } from '../state.js';
import { L } from '../i18n.js';

const domains = [
    { name: 'Cognition', ids: [1, 2, 3, 4, 5, 6] },
    { name: 'Mobility', ids: [7, 8, 9, 10, 11] },
    { name: 'Self-care', ids: [12, 13, 14, 15] },
    { name: 'Getting along', ids: [16, 17, 18, 19, 20] },
    { name: 'Life activities', ids: [21, 22, 23, 24, 25, 26, 27, 28] },
    { name: 'Participation', ids: [29, 30, 31, 32, 33, 34, 35, 36] }
];

function score(values, questions, form) {
    const responses = new Map(questions.map((question, index) => [question.id, values[index]]));
    const employed = responses.get('WH_WORK') === 1;
    const scoredIds = Array.from({ length: 36 }, (_, index) => index + 1)
        .filter(id => employed || id < 25 || id > 28);
    const valueFor = id => responses.get('WH' + id) ?? state.responses[form.id + ':WH' + id];
    const total = scoredIds.reduce((sum, id) => sum + (valueFor(id) || 0), 0);
    const max = scoredIds.length * 4;
    const rows = [{
        name: L(form.name) + ' — Simple total',
        score: total + '/' + max,
        severity: 'Descriptive functioning score; no diagnostic cutoff',
        notDiagnostic: true,
        sourceNote: 'Simple 0-4 summed scoring; the WHO IRT conversion is not applied.'
    }];
    domains.forEach(domain => {
        const ids = domain.ids.filter(id => employed || id < 25 || id > 28);
        if (!ids.length) return;
        const sum = ids.reduce((result, id) => result + (valueFor(id) || 0), 0);
        rows.push({
            name: L(form.name) + ' — ' + domain.name,
            score: sum + '/' + (ids.length * 4),
            severity: 'Domain sum; higher values indicate more difficulty',
            notDiagnostic: true
        });
    });
    for (const id of ['WH37', 'WH38', 'WH39']) {
        const value = responses.get(id);
        const question = questions.find(item => item.id === id);
        if (!Number.isFinite(value) || !question) continue;
        rows.push({
            name: L(question.text),
            score: value + ' days',
            severity: 'Descriptive count; excluded from the 36-item score',
            notDiagnostic: true
        });
    }
    return rows;
}

export { score };
