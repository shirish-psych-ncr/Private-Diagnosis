import { state } from '../state.js';
import { L } from '../i18n.js';

const groups = [
    { label: 'Clutter', ids: [1, 3, 5, 8, 10, 12, 15, 20, 22], reference: 15 },
    { label: 'Difficulty discarding / saving', ids: [4, 6, 7, 13, 17, 19, 23], reference: 13 },
    { label: 'Acquisition', ids: [2, 9, 11, 14, 16, 18, 21], reference: 13 }
];

function score(_values, questions, form) {
    const responses = new Map(questions.map(question => [Number(question.id.slice(3)), state.responses[form.id + ':' + question.id]]));
    const valueFor = id => {
        const raw = responses.get(id);
        return Number.isFinite(raw) ? (id === 2 || id === 4 ? 4 - raw : raw) : null;
    };
    const rows = [];
    groups.forEach(group => {
        const values = group.ids.map(valueFor);
        const total = values.reduce((sum, value) => sum + (value ?? 0), 0);
        const positive = total > group.reference;
        rows.push({
            name: L(form.name) + ' — ' + group.label,
            score: total + '/' + (group.ids.length * 4),
            severity: positive ? 'Above supplied typical-score reference; not diagnostic' : 'At or below supplied typical-score reference',
            aboveCutoff: positive,
            notDiagnostic: true
        });
    });
    const total = groups.reduce((sum, group) => sum + group.ids.map(valueFor).reduce((part, value) => part + (value ?? 0), 0), 0);
    const positive = total > 40;
    rows.unshift({
        name: L(form.name) + ' — Total',
        score: total + '/92',
        severity: positive ? 'Above supplied typical-score reference; not diagnostic' : 'At or below supplied typical-score reference',
        aboveCutoff: positive,
        notDiagnostic: true,
        sourceNote: L(form.interpretationNote)
    });
    return rows;
}

export { score };
