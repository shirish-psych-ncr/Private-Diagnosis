import { state } from '../state.js';
import { L } from '../i18n.js';

function scoreSuppliedProfile(form) {
    const config = form.scoringProfile;
    if (!config) return [];
    const items = new Map(form.parts.flatMap(part => part.questions).map(q => [q.id, q]));
    const valueFor = id => Number(state.responses[form.id + ':' + id]);
    const rows = [];
    const note = form.interpretationNote || form.attribution;

    if (config.itemRegister) {
        for (const id of config.itemRegister) {
            const value = state.responses[form.id + ':' + id];
            if (Number.isFinite(value)) rows.push({ name: L(items.get(id)?.text || id), score: value,
                severity: 'Item-level monitoring', notDiagnostic: true, sourceNote: note });
        }
    }
    if (config.contextRegister) {
        for (const id of config.contextRegister) {
            const value = state.responses[form.id + ':' + id];
            if (value == null || value === '') continue;
            rows.push({ name: L(items.get(id)?.text || id), score: String(value),
                severity: 'Recorded context — not scored', notDiagnostic: true, sourceNote: note });
        }
    }
    for (const group of config.groups || []) {
        const present = group.ids.filter(id => Number.isFinite(valueFor(id)));
        if (!present.length) continue;
        const values = present.map(id => {
            const item = items.get(id);
            const value = valueFor(id);
            return item?.reverse || group.reverse?.includes(id)
                ? (item?.max ?? form.responseMax) + (item?.min ?? form.responseMin) - value
                : value;
        });
        const sum = values.reduce((a, b) => a + b, 0);
        const raw = group.average ? sum / values.length : sum;
        const max = group.average ? (group.max ?? form.responseMax) :
            (group.max ?? (group.ids.length * (form.responseMax - form.responseMin) +
                (group.average ? 0 : form.responseMin * group.ids.length)));
        let severity = group.severity || (group.average ? 'Subscale mean' : 'Dimensional profile — not diagnostic');
        if (group.cutoff != null) severity = raw >= group.cutoff
            ? (group.positiveLabel || 'Further assessment indicated')
            : (group.negativeLabel || 'Below screening threshold');
        rows.push({ name: group.name || L(form.name),
            score: (group.average ? raw.toFixed(2) : raw) + '/' + max,
            severity, aboveCutoff: group.cutoff != null ? raw >= group.cutoff : undefined,
            notDiagnostic: true, sourceNote: note });
    }
    if (config.screening) {
        const s = config.screening;
        const recognized = s.recognizedAny.some(id => valueFor(id) === 1);
        const consequence = s.consequenceAny.some(id => valueFor(id) === 1);
        const positive = recognized && consequence;
        rows.push({ name: s.name, score: positive ? 'Possible concern flagged' : 'Rule not met',
            severity: positive ? 'Follow up with a clinical assessment; this is not a diagnosis.' : 'No flag from this rule',
            aboveCutoff: positive, notDiagnostic: true, sourceNote: note });
    }
    return rows;
}

export { scoreSuppliedProfile };
