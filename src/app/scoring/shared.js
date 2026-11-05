import { t } from '../i18n.js';
import { computeResults } from '../results-computation.js';
import { OPTIONAL_TABLE_ROUTES, routeInstruments } from '../routing.js';
import { scoreCas } from '../scales/clinical_anger_scale.js';
import { scoreStaxi } from '../scales/staxi_ca.js';
import { state, CLINICAL_DATA } from '../state.js';

/* ------------------------------------------------------------------ *
 * 7a. Personality-disorder screens (IPDE / PDQ-4+) — shared helpers   *
 * ------------------------------------------------------------------ */

/** Screen-in questions whose endorsement deploys a keyed T/F instrument. */
function deployedPdScreens(domain) {
    return deployedScreenInstruments(domain, s => !!s.keyedScoring);
}

/**
 * Generic screen-in deployment: returns the scales attached to a domain's
 * yes/no screen items that the respondent endorsed. `accept` selects which
 * kind of instrument qualifies (keyed personality screens, summed anger
 * instruments, ...).
 */
function deployedScreenInstruments(domain, accept) {
    const out = [];
    if (!domain || !domain.questions) return out;
    // Tables are shown as soon as the domain is selected (see routeInstruments),
    // so scoring must follow the same rule — otherwise an instrument can be on
    // screen yet silently skipped because its screen-in item was answered "No".
    // Optional rating-table routes therefore score every attached instrument;
    // other routes keep the original endorse-first behaviour.
    const alwaysDeployed = OPTIONAL_TABLE_ROUTES.includes(domain.instrument) &&
        // A hybrid route (mood / auto:bipolartable) still sums its own primary
        // item set, so the usual endorse-first rule keeps applying there.
        !(domain.instrument === 'auto:bipolartable' && domain.baseInstrument);
    domain.questions.forEach(q => {
        if (!q.scaleId) return;
        if (!alwaysDeployed && (state.responses[domain.id + ':' + q.id] || 0) < 1) return;
        const s = CLINICAL_DATA.scales[q.scaleId];
        if (s && accept(s)) out.push({ question: q, scale: s });
    });
    return out;
}

/**
 * Keyed-answer count for one IPDE module or PDQ-4+ scale.
 * IPDE items carry `keyedAnswer` ('T' counts when answered True, 'F' when
 * answered False); PDQ-4+ scales list plain item numbers counted when True.
 */
function keyedCount(scaleId, qids, keyed) {
    let n = 0;
    qids.forEach(id => {
        const v = state.responses[scaleId + ':' + id];
        if (v === undefined) return;
        if (keyed) { if ((keyed[id] === 'T') === (v === 1)) n++; }
        else if (v === 1) n++;
    });
    return n;
}

/** Checklists rendered as Yes/No columns inside a PDQ-4+ deployment. */
function pdqChecklistParts(scale) {
    return (scale.parts || []).filter(p => p.options && !p.clinicianRated);
}

/** Number of keyed items endorsed on one IPDE module (part). */
function ipdeKeyedHits(part, scaleId) {
    const hits = [];
    part.questions.forEach(q => {
        const v = state.responses[scaleId + ':' + q.id];
        if (v === undefined) return;
        if ((q.keyedAnswer === 'T') === (v === 1)) hits.push(q.itemNumber || q.id);
    });
    return hits;
}

/* ------------------------------------------------------------------ *
 * 7c. Somatic-symptom instruments (FAC22-SR / PHQ-15)                *
 * ------------------------------------------------------------------ */

/**
 * Count keyed answers across an instrument's item parts.
 *  - keyed T/F instruments (IPDE, FAC22-SR): each question carries
 *    `keyedAnswer` 'T' (counts when answered True) or 'F' (counts when
 *    answered False);
 *  - plain True-count instruments (PDQ-4+ scales): any answer of 1 counts.
 * `skip` lets a caller exclude follow-up/clinician-rated parts.
 */
function keyedHitsOfParts(scale, skip) {
    const hits = [];
    // Option value that represents the affirmative answer ("True" / "Yes").
    // PDQ-4+ and IPDE use True=1; FAC22-SR lists Yes first so Yes=1 as well.
    const affirm = (() => {
        const opts = scale.matrixOptions || [];
        const t = opts.find(o => /^(true|yes)$/i.test((o.label || {}).en || ''));
        return t ? t.v : 1;
    })();
    (scale.parts || []).forEach(part => {
        if (skip && skip(part)) return;
        (part.questions || []).forEach(q => {
            const v = state.responses[scale.id + ':' + q.id];
            if (v === undefined) return;
            if (q.keyedAnswer !== undefined) {
                if ((q.keyedAnswer === 'T') === (v === affirm)) {
                    hits.push(q.itemNumber != null ? q.itemNumber : q.id);
                }
            } else if (v === affirm) {
                hits.push(q.itemNumber != null ? q.itemNumber : q.id);
            }
        });
    });
    return hits;
}

/* ------------------------------------------------------------------ *
 * 7d. Dissociation instruments (MID-60 short form / DES-II)          *
 * ------------------------------------------------------------------ */

/** Resolve an instrument disorder key, falling back to the legacy
 *  'dissociative' category if a newer key is absent from the clinical data. */
function dissDisorder(keys) {
    for (const k of keys) if (CLINICAL_DATA.disorders[k]) return k;
    return CLINICAL_DATA.disorders.dissociative ? 'dissociative' : keys[0];
}

/**
 * Transient flag sink used by the standalone scorers (MID-60 / DES-II).
 * `computeResults` installs its own accumulator before deploying any
 * instrument and restores the no-op afterwards, so a scorer can raise a
 * differential-disorder flag without taking the addFlag closure as an
 * argument (keeps the signature aligned with scoreCas / scoreStaxi).
 */


/** Resolve the GCLS differential key, falling back gracefully if a newer
 *  the clinical data does not yet carry it (same pattern as dissDisorder). */
function genderDisorder(keys) {
    const list = keys || ['gender_incongruence_distress', 'gender_incongruence'];
    for (const k of list) if (CLINICAL_DATA.disorders[k]) return k;
    return null;
}

export { deployedPdScreens, deployedScreenInstruments, keyedCount, pdqChecklistParts, ipdeKeyedHits, keyedHitsOfParts, dissDisorder, genderDisorder };
