import { t, L } from '../i18n.js';
import { bandLabel } from '../scoring/bands.js';
import { state } from '../state.js';

/**
 * Clinical Anger Scale scoring: sum of the 21 cluster choices (A=0..D=3,
 * range 0-63) mapped onto the printed interpretive ranges. Severity band
 * only - the CAS is dimensional and does not itself raise a disorder flag.
 */
function scoreCas(scale) {
    const hi = state.lang === 'hi';
    const ids = [];
    (scale.parts || []).forEach(part => part.questions.forEach(q => ids.push(q.id)));
    const got = ids.filter(id => state.responses[scale.id + ':' + id] !== undefined);
    const sum = got.reduce((t, id) => t + Number(state.responses[scale.id + ':' + id]), 0);
    const complete = got.length === ids.length;
    // Printed interpretive ranges are inclusive of their lower bound:
    // 0-13 minimal · 14-19 mild · 20-28 moderate · 29-63 severe.
    const bandIdx = (() => {
        const bands = scale.bands || [];
        for (let i = 0; i < bands.length; i++) if (sum <= bands[i].max) return i;
        return bands.length - 1;
    })();
    const maxTotal = ((scale.ratingScale || {}).max || 3) * ids.length;
    return {
        name: L(scale.name),
        score: sum + '/' + maxTotal + ' (' + got.length + '/' + ids.length + ')',
        severity: (bandLabel(sum, scale.bands) || (hi ? 'अपूर्ण' : 'Incomplete')) +
            (hi ? ' · रोग-निर्णायक नहीं' : ' · not diagnostic'),
        aboveCutoff: complete && bandIdx >= 2,
        notDiagnostic: true,
        answered: got.length, total: ids.length,
        disorders: []
    };
}

export { scoreCas };
