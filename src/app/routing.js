import { selectedDomainForms, state } from './state.js';

/* ------------------------------------------------------------------ *
 * 6. STAGE 3 — ADAPTIVE INSTRUMENT DEPLOYMENT (routing engine)
 * ------------------------------------------------------------------ */

/**
 * Given the selected domains and the declared age group, decide which
 * instruments to deploy. `auto:adhd` routes VADRS for pediatric/adolescent
 * and ASRS-v1.1 (the domain's own item set) for adults, per the whitepaper.
 */
/* Routes whose optional instruments are always shown once the domain is picked. */
const OPTIONAL_TABLE_ROUTES = ['auto:minioptional', 'auto:pdscreen', 'auto:angertable', 'auto:dissociationtable', 'auto:somatoptable', 'auto:genderdistress', 'auto:bipolartable'];

function routeInstruments() {
    const deployed = [];
    selectedDomainForms().forEach(domain => {
        const instName = domain.instrument || null;
        if (instName === 'auto:adhd') {
            const peds = ['pediatric', 'adolescent'].includes(state.context.ageGroup);
            deployed.push({
                domain,
                scaleId: peds ? 'vadrs' : null,
                instrumentLabel: peds ? 'VADRS' : 'ASRS-v1.1'
            });
        } else if (OPTIONAL_TABLE_ROUTES.includes(instName)) {
            if (instName === 'auto:bipolartable' && domain.baseInstrument) {
                // The mood domain keeps its own PHQ-9 item set as the primary
                // instrument; the BISS rides along underneath as an optional
                // clinician-rated table.
                deployed.push({ domain, scaleId: null, instrumentLabel: domain.baseInstrument });
            }
            // Several prompts can refer to the same questionnaire.
            domain.questions.forEach(q => {
                if (!q.scaleId || deployed.some(entry => entry.domain === domain && entry.scaleId === q.scaleId)) return;
                deployed.push({ domain, scaleId: q.scaleId, instrumentLabel: null, ratingTable: true });
            });
        } else {
            deployed.push({ domain, scaleId: null, instrumentLabel: instName });
        }
    });
    return deployed;
}

export { OPTIONAL_TABLE_ROUTES, routeInstruments };
