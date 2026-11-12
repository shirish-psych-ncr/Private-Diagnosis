import { OPTIONAL_TABLE_ROUTES } from './routing.js';
import { selectedDomainForms, selectedFormsForDomain, state, CLINICAL_DATA, questionIsApplicable } from './state.js';

function firstUnanswered() {
    for (const domain of selectedDomainForms()) {
        const chosen = domain.selectedForms || [];
        const pedsAdhd = domain.instrument === 'auto:adhd' &&
            ['pediatric', 'schoolage', 'adolescent'].includes(state.context.ageGroup);

        if (domain.forms?.length) {
            if (domain.instrument === 'auto:adhd' && chosen.includes('base')) {
                if (pedsAdhd) {
                    for (const part of CLINICAL_DATA.scales.vadrs.parts)
                        for (const q of part.questions)
                            if (state.responses['vadrs:' + q.id] === undefined) return 'vadrs:' + q.id;
                } else {
                    for (const q of domain.questions.filter(q => !q.scaleId))
                        if (state.responses[domain.id + ':' + q.id] === undefined) return domain.id + ':' + q.id;
                }
            } else if ((domain.baseInstrument || domain.originalLabel) && chosen.includes('base')) {
                for (const q of domain.questions.filter(q => !q.scaleId))
                    if (state.responses[domain.id + ':' + q.id] === undefined) return domain.id + ':' + q.id;
            }

            for (const id of chosen.filter(id => domain.forms.includes(id))) {
                const form = CLINICAL_DATA.scales[id];
                for (const part of form.parts) {
                    if (part.clinicianRated) continue;
                    for (const q of part.questions) {
                        if (!questionIsApplicable(q, id) || q.nonScored || q.tickBox) continue;
                        if (state.responses[id + ':' + q.id] === undefined) return id + ':' + q.id;
                    }
                }
            }

            if (OPTIONAL_TABLE_ROUTES.includes(domain.instrument) ||
                domain.questions.some(q => q.scaleId && chosen.includes(q.scaleId))) {
                const selectedIds = new Set(chosen.filter(id => id !== 'base'));
                for (const q of domain.questions) {
                    if (q.scaleId && selectedIds.has(q.scaleId) &&
                        state.responses[domain.id + ':' + q.id] === undefined)
                        return domain.id + ':' + q.id;
                }
                const checked = new Set();
                for (const q of domain.questions) {
                    if (!q.scaleId || !selectedIds.has(q.scaleId) || checked.has(q.scaleId)) continue;
                    checked.add(q.scaleId);
                    const form = CLINICAL_DATA.scales[q.scaleId];
                    if (!form) continue;
                    for (const part of form.parts) {
                        if (part.clinicianRated) continue;
                        for (const item of part.questions) {
                            if (!questionIsApplicable(item, form.id) || item.nonScored || item.tickBox) continue;
                            if (state.responses[form.id + ':' + item.id] === undefined)
                                return form.id + ':' + item.id;
                        }
                    }
                }
            }
            continue;
        }

        if (pedsAdhd) {
            for (const part of CLINICAL_DATA.scales.vadrs.parts)
                for (const q of part.questions)
                    if (state.responses['vadrs:' + q.id] === undefined) return 'vadrs:' + q.id;
            continue;
        }

        for (const q of domain.questions)
            if (state.responses[domain.id + ':' + q.id] === undefined) return domain.id + ':' + q.id;

        if (OPTIONAL_TABLE_ROUTES.includes(domain.instrument)) {
            for (const q of domain.questions) {
                if (!q.scaleId) continue;
                const form = CLINICAL_DATA.scales[q.scaleId];
                if (!form) continue;
                for (const part of form.parts) {
                    if (part.clinicianRated) continue;
                    for (const item of part.questions) {
                        if (!questionIsApplicable(item, form.id) || item.nonScored || item.tickBox) continue;
                        if (state.responses[form.id + ':' + item.id] === undefined) return form.id + ':' + item.id;
                    }
                }
            }
        }
    }
    return null;
}

function allAnswered() { return firstUnanswered() === null; }

export { allAnswered, firstUnanswered };

