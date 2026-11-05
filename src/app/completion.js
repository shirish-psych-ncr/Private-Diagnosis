import { OPTIONAL_TABLE_ROUTES } from './routing.js';
import { state, CLINICAL_DATA } from './state.js';

function allAnswered() {
    for (const domain of CLINICAL_DATA.domains) {
        if (!state.selectedDomains.has(domain.id)) continue;
        if (domain.instrument === 'auto:adhd' && ['pediatric', 'adolescent'].includes(state.context.ageGroup)) {
            const vadrs = CLINICAL_DATA.scales.vadrs;
            for (const part of vadrs.parts)
                for (const q of part.questions)
                    if (state.responses['vadrs:' + q.id] === undefined) return false;
            continue;
        }
        for (const q of domain.questions)
            if (state.responses[domain.id + ':' + q.id] === undefined) return false;

        // Every optional instrument attached to a screen-in item of this domain
        // must be fully answered before results are shown — scoring a partially
        // completed printed form would misreport its severity bands. Two
        // exceptions: (a) clinician-rated follow-up parts (PDQ-4+ clinical
        // significance, MINI disability register) are completed after the
        // interview, and (b) performance/observer forms keep their own gates.
        if (OPTIONAL_TABLE_ROUTES.includes(domain.instrument)) {
            for (const q of domain.questions) {
                if (!q.scaleId) continue;
                const s = CLINICAL_DATA.scales[q.scaleId];
                if (!s) continue;
                for (const part of s.parts) {
                    if (part.clinicianRated) continue;
                    for (const item of part.questions) {
                        if (item.nonScored) continue;   // optional clinical tick-box
                        if (state.responses[s.id + ':' + item.id] === undefined) return false;
                    }
                }
            }
        }
    }
    return true;
}

export { allAnswered };
