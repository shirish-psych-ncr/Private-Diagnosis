import { selectedDomainForms, selectedFormsForDomain, state } from './state.js';

/* ------------------------------------------------------------------ *
 * 6. STAGE 3 — ADAPTIVE INSTRUMENT DEPLOYMENT (routing engine)
 * ------------------------------------------------------------------ */

/**
 * Given the selected domains and the declared age group, decide which
 * instruments to deploy. `auto:adhd` routes VADRS for pediatric/adolescent
 * and ASRS-v1.1 (the domain's own item set) for adults, per the whitepaper.
 */
/* Specialized routing for domains that combine explicit scale choices with screen-in tables. */
const OPTIONAL_TABLE_ROUTES = ['auto:minioptional', 'auto:pdscreen', 'auto:angertable', 'auto:dissociationtable', 'auto:somatoptable', 'auto:genderdistress', 'auto:bipolartable'];

function routeInstruments() {
    const deployed = [];
    selectedDomainForms().forEach(domain => {
        const instName = domain.instrument || null;
        if (instName === 'auto:adhd') {
            const peds = ['pediatric', 'schoolage', 'adolescent'].includes(state.context.ageGroup);
            const chosen = domain.selectedForms || [];
            if (chosen.includes('base')) deployed.push(peds
                ? { domain, scaleId: 'vadrs', instrumentLabel: 'VADRS', ratingTable: true }
                : { domain, scaleId: null, instrumentLabel: domain.baseInstrument || 'ASRS-v1.1' });
            chosen.filter(id => (domain.forms || []).includes(id)).forEach(id => deployed.push({
                domain: { ...domain, id, directForm: true },
                scaleId: id,
                instrumentLabel: null
            }));
        } else if (OPTIONAL_TABLE_ROUTES.includes(instName)) {
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
            const chosenForms = (domain.selectedForms || []).filter(id => (domain.forms || []).includes(id));
            chosenForms.forEach(id => {
                if (deployed.some(entry => entry.scaleId === id && entry.domain.id === id)) return;
                deployed.push({ domain: { ...domain, id, directForm: true }, scaleId: id, instrumentLabel: null });
            });
        } else {
            const chosen = domain.selectedForms || [];
            const baseName = domain.baseInstrument || domain.originalLabel;
            if (!chosen.length && domain.forms?.length) return;
            chosen.filter(id => !domain.forms?.includes(id) && domain.questions.some(q => q.scaleId === id))
                .forEach(id => {
                    if (deployed.some(entry => entry.domain === domain && entry.scaleId === id)) return;
                    deployed.push({ domain, scaleId: id, ratingTable: true, instrumentLabel: null });
                });
            if (chosen.includes('base') && baseName) {
                deployed.push({ domain: { ...domain, questions: domain.questions.filter(q => !q.scaleId || chosen.includes(q.scaleId)) }, scaleId: null, instrumentLabel: baseName });
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
