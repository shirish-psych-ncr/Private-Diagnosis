import { L } from '../i18n.js';
import { bandLabel } from '../scoring/bands.js';
import { dissDisorder } from '../scoring/shared.js';
import { state, addFlagGlobal } from '../state.js';

/**
 * DES-II scoring: total = mean of the 28 item percentages (0-100). A mean of
 * 30 or above is the clinical comparison point that warrants a structured
 * dissociative-disorder interview. Dimensional screening only.
 */
function scoreDesII(scale) {
    const hi = state.lang === 'hi';
    const ids = [];
    (scale.parts || []).forEach(part => part.questions.forEach(q => ids.push(q.id)));
    const got = ids.filter(id => state.responses[scale.id + ':' + id] !== undefined)
        .map(id => Number(state.responses[scale.id + ':' + id]));
    const complete = got.length === ids.length;
    const mean = got.length ? got.reduce((a, b) => a + b, 0) / got.length : null;
    const cutoff = (scale.scoring || {}).cutoff || 30;
    const above = mean !== null && complete && mean >= cutoff;
    const disorders = [];
    if (above) {
        [dissDisorder(['other_specified_dissociative_disorder']),
         dissDisorder(['dissociative_amnesia']),
         dissDisorder(['depersonalisation_derealisation_disorder'])]
            .forEach(k => { if (!disorders.includes(k)) disorders.push(k); });
        disorders.forEach(d => addFlagGlobal(d, 'DES-II'));
    }
    return {
        name: L(scale.name),
        score: mean === null ? '—'
            : (Math.round(mean * 10) / 10 + '% (' + got.length + '/' + ids.length + ')'),
        severity: (mean === null ? (hi ? 'अपूर्ण' : 'Incomplete') : bandLabel(mean, scale.bands)) +
            (above ? (hi ? ' · नैदानिक-तुलना बिंदु ≥' + cutoff + ' पार' : ' · above the ≥' + cutoff + ' clinical comparison point') : ''),
        aboveCutoff: above,
        notDiagnostic: true,
        answered: got.length, total: ids.length,
        disorders: disorders
    };
}

export { scoreDesII };
