
/* ------------------------------------------------------------------ *
 * 1. EPHEMERAL STATE — lives only in volatile memory. Never persisted.
 * ------------------------------------------------------------------ */
const state = {
    lang: 'en',
    stage: 0,
    consent: false,
    context: { ageGroup: '', reason: '', medications: '', priorDiagnoses: '' },
    selectedDomains: new Set(),
    scaleChoices: new Map(),
    responses: {},            // key: `${domainId}:${questionId}` or `vadrs:${id}` -> number
    formContext: {},
    safetyFlags: [],          // [{ questionId, domainId }]
    selectedICD11Codes: new Set(), // optional clinician-reviewed reference choices
    icd11BoundaryOptions: [],
    touchedQuestions: new Set(),
    results: null             // computed at finish
};

let CLINICAL_DATA = null;     // populated from the modular data tree
let I18N = null;              // populated from the modular data tree


let addFlagGlobal = () => {};
function setFlagSink(sink) { addFlagGlobal = sink; }
function setClinicalData(payload) {
    const { icd11BoundaryOptions = [], ...clinical } = payload;
    CLINICAL_DATA = clinical;
    state.icd11BoundaryOptions = icd11BoundaryOptions;
    I18N = clinical.i18n || {};
}

export { state, CLINICAL_DATA, I18N, addFlagGlobal, setFlagSink, setClinicalData };

export function choicesForDomain(domain) {
    const ageAvailable = id => {
        const scale = CLINICAL_DATA.scales[id];
        const ages = scale?.ageGroups || scale?.targetAge || [];
        return !ages.length || ages.includes(state.context.ageGroup) ||
            (['youngadult', 'midlife'].includes(state.context.ageGroup) && ages.includes('adult'));
    };
    const questionScales = [...new Set((domain.questions || []).map(q => q.scaleId).filter(Boolean))].filter(ageAvailable);
    const formScales = (domain.forms || []).filter(ageAvailable);
    const choices = [];
    if (domain.baseInstrument || domain.originalLabel) choices.push('base');
    choices.push(...questionScales, ...formScales);
    return [...new Set(choices)];
}

export function defaultChoicesForDomain(domain) {
    // Selecting a topic is a routing choice only. Instruments are always
    // opted into explicitly, even when the domain offers a single scale.
    return [];
}

export function requiredQuestionId(question, scaleId) {
    if (!question.requires) return null;
    const required = String(question.requires);
    const ids = CLINICAL_DATA?.scales?.[scaleId]?.parts?.flatMap(part => part.questions.map(item => item.id)) || [];
    return ids.includes(required) ? required : scaleId + '_' + required;
}

export function questionIsApplicable(question, scaleId) {
    const parentId = requiredQuestionId(question, scaleId);
    if (!parentId) return true;
    const value = state.responses[scaleId + ':' + parentId];
    return question.requiresPositive ? Number.isFinite(value) && value > 0 : value === 1;
}

function filterDomainQuestions(domain, selected) {
    return (domain.questions || []).filter(q => {
        if (q.scaleId) return selected.includes(q.scaleId);
        if (domain.baseInstrument || domain.originalLabel) return selected.includes('base');
        return true;
    });
}

export function selectedDomainForms() {
    return CLINICAL_DATA.domains.filter(domain => state.selectedDomains.has(domain.id)).map(domain => {
        const hasSavedChoice = state.scaleChoices.has(domain.id);
        const savedChoice = state.scaleChoices.get(domain.id);
        const available = choicesForDomain(domain);
        const defaults = defaultChoicesForDomain(domain);
        const selected = hasSavedChoice && Array.isArray(savedChoice)
            ? savedChoice.filter(id => available.includes(id))
            : hasSavedChoice && available.includes(savedChoice) ? [savedChoice]
                : defaults;
        const effectiveSelected = selected;
        if (available.length || domain.forms?.length || domain.baseInstrument || domain.originalLabel || hasSavedChoice) {
            const questions = filterDomainQuestions(domain, effectiveSelected);
            return { ...domain, selectedForms: effectiveSelected, questions };
        }
        if (!effectiveSelected.length) return domain;
        return { ...domain, questions: filterDomainQuestions(domain, effectiveSelected) };
    });
}

export function selectedFormsForDomain(domain) {
    if (Array.isArray(domain.selectedForms)) return domain.selectedForms.filter(id => id !== 'base');
    const choice = state.scaleChoices.get(domain.id);
    if (Array.isArray(choice)) return choice.filter(id => id !== 'base');
    if (choice === 'all') return [];
    if (choice) return [choice].filter(id => id !== 'base');
    return defaultChoicesForDomain(domain).filter(id => id !== 'base');
}
