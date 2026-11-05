
import { t, L } from '../i18n.js';
import { bandLabel } from '../scoring/bands.js';
import { state } from '../state.js';

/**
 * PHQ-15 somatic symptom severity index: sum of 15 items scored 0-2 over
 * the past four weeks. Printed cut-points 0-4 no somatisation, 5-9 mild,
 * 10-14 moderate, 15+ severe. Severity measure only — it supplements
 * clinical judgement and does not by itself establish a diagnosis.
 */
function scorePhq15(scale) {
    const hi = state.lang === 'hi';
    const ids = [];
    (scale.parts || []).forEach(part => (part.questions || []).forEach(q => ids.push(q.id)));
    const got = ids.filter(id => state.responses[scale.id + ':' + id] !== undefined);
    const complete = got.length === ids.length;
    const sum = got.reduce((t, id) => t + Number(state.responses[scale.id + ':' + id]), 0);
    const maxTotal = ((scale.ratingScale || {}).max || 2) * ids.length;
    // Band list is ordered ascending by `max`; treat "no somatisation" as
    // non-clinical so the differential is only nudged from 5 upwards.
    const bandIdx = (() => {
        const bands = scale.bands || [];
        for (let i = 0; i < bands.length; i++) if (sum <= bands[i].max) return i;
        return bands.length - 1;
    })();
    return {
        name: L(scale.name),
        score: sum + '/' + maxTotal + ' (' + got.length + '/' + ids.length + ')',
        severity: (bandLabel(sum, scale.bands) || (hi ? 'अपूर्ण' : 'Incomplete')) +
            (hi ? ' · रोग-निर्णायक नहीं' : ' · not diagnostic'),
        aboveCutoff: complete && bandIdx >= 1,
        notDiagnostic: true,
        answered: got.length, total: ids.length,
        disorders: []
    };
}

export { scorePhq15 };
