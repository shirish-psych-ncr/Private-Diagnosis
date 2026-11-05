import { state } from '../state.js';
import { L } from '../i18n.js';

export function scoreRatingRegister(s) {
    const rows = s.parts[0].questions;
    const rated = rows.map(r => state.responses[s.id + ':' + r.id])
        .filter(v => v !== undefined);
    const anchorName = v => {
        const anchors = ((s.ratingScale || {}).anchors || []).slice().sort((a, b) => b.v - a.v);
        const hit = anchors.find(a => v >= a.v);
        return hit ? L(hit.label) : String(v);
    };
    return {
        name: L(s.name),
        score: rated.length + '/' + rows.length + ' rated' +
            (rated.length ? ' | max ' + Math.max(...rated) + '/10 (' + anchorName(Math.max(...rated)) + ')' : ''),
        severity: rated.length
            ? (state.lang === 'hi' ? 'चिकित्सक-रेटित' : 'Clinician-rated')
            : (state.lang === 'hi' ? 'अपूर्ण' : 'Incomplete'),
        aboveCutoff: false,
        answered: rated.length, total: rows.length,
        disorders: [],
        ratingRegister: rows.map(r => ({ id: r.id, label: L(r.text), value: state.responses[s.id + ':' + r.id] }))
    };
}
