import { selectedDomainForms, selectedFormsForDomain, state } from './state.js';

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
            const peds = ['pediatric', 'schoolage', 'adolescent'].includes(state.context.ageGroup);
            deployed.push({
                domain,
                scaleId: peds ? 'vadrs' : null,
                instrumentLabel: peds ? 'VADRS' : 'ASRS-v1.1'
            });
        } else if (OPTIONAL_TABLE_ROUTES.includes(instName)) {
            if (instName === 'auto:bipolartable' && domain.baseInstrument && (domain.selectedForms || []).includes('base')) {
                // The mood domain keeps its own PHQ-9 item set as the primary
                // instrument; the BISS rides along underneath as an optional
                // clinician-rated table.
                deployed.push({ domain, scaleId: null, instrumentLabel: domain.baseInstrument });
            }
            // Several prompts can refer to the same questionnaire.
            domain.questions.forEach(q => {
                if (instName === 'auto:bipolartable' && q.scaleId === 'biss') {
                    if ((domain.selectedForms || []).includes('biss') && !deployed.some(entry => entry.domain === domain && entry.scaleId === q.scaleId))
                        deployed.push({ domain, scaleId: q.scaleId, instrumentLabel: null, ratingTable: true });
                    return;
                }
                if (!selectedFormsForDomain(domain).includes(q.scaleId)) return;
                if (!q.scaleId || deployed.some(entry => entry.domain === domain && entry.scaleId === q.scaleId)) return;
                deployed.push({ domain, scaleId: q.scaleId, instrumentLabel: null, ratingTable: true });
            });
            if (instName === 'auto:bipolartable' && (domain.selectedForms || []).includes('base') && !deployed.some(entry => entry.domain === domain && !entry.scaleId))
                deployed.push({ domain, scaleId: null, instrumentLabel: domain.baseInstrument });
        } else {
            const chosen = domain.selectedForms || [];
            if (!chosen.length && domain.forms?.length) return;
            if (domain.forms?.length && !chosen.includes('base') && domain.baseInstrument) {
                chosen.filter(id => domain.questions.some(q => q.scaleId === id)).forEach(id => {
                    if (deployed.some(entry => entry.domain === domain && entry.scaleId === id)) return;
                    deployed.push({ domain, scaleId: id, ratingTable: true, instrumentLabel: null });
                });
            }
            if (chosen.includes('base') && domain.baseInstrument) {
                deployed.push({ domain: { ...domain, questions: domain.questions.filter(q => !q.scaleId || chosen.includes(q.scaleId)) }, scaleId: null, instrumentLabel: domain.baseInstrument });
            }
            const chosenForms = chosen.filter(id => (domain.forms || []).includes(id));
            if (chosenForms.length) {
                chosenForms.forEach(id => deployed.push({
                    domain: { ...domain, id, directForm: true }, scaleId: id, instrumentLabel: null
                }));
            }
            if (!chosen.includes('base') && !chosenForms.length && !domain.forms?.length) deployed.push({ domain, scaleId: null, instrumentLabel: instName });
        }
    });
    return deployed;
}

export { OPTIONAL_TABLE_ROUTES, routeInstruments };
