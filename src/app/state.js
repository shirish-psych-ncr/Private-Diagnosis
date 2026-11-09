
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
    const questionScales = [...new Set((domain.questions || []).map(q => q.scaleId).filter(Boolean))];
    const formScales = (domain.forms || []).filter(id => {
        const scale = CLINICAL_DATA.scales[id];
        const ages = scale?.ageGroups || scale?.targetAge || [];
        return !ages.length || ages.includes(state.context.ageGroup);
    });
    const choices = [];
    if (domain.baseInstrument || domain.originalLabel) choices.push('base');
    choices.push(...questionScales, ...formScales);
    return [...new Set(choices)];
}

export function defaultChoicesForDomain(domain) {
    const available = choicesForDomain(domain);
    if (Array.isArray(domain.defaultScales))
        return domain.defaultScales.filter(id => available.includes(id));
    if (domain.defaultForm && available.includes(domain.defaultForm)) return [domain.defaultForm];
    return available;
}

function filterDomainQuestions(domain, selected) {
    return (domain.questions || []).filter(q => {
        if (q.scaleId) return selected.includes(q.scaleId);
        if (domain.baseInstrument || domain.originalLabel) return selected.includes('base');
        return true;
    });
}

function directFormDomain(id) {
    const form = CLINICAL_DATA.scales[id];
    const questions = form.parts.flatMap(part => part.questions
        .filter(q => !q.requires || state.responses[id + ':' + q.requires] === 1)
        .map((q, i) => ({ ...q, scale: q.scale ?? form.matrixOptions, section: i === 0 ? part.name : null })));
    return { id, directForm: true, name: form.name, timeframe: form.directions,
        contextFields: form.contextFields, durationOptions: form.durationOptions,
        attribution: form.attribution, questions };
}

export function selectedDomainForms() {
    return CLINICAL_DATA.domains.filter(domain => state.selectedDomains.has(domain.id)).map(domain => {
        const hasSavedChoice = state.scaleChoices.has(domain.id);
        const savedChoice = state.scaleChoices.get(domain.id);
        const available = choicesForDomain(domain);
        const defaults = defaultChoicesForDomain(domain);
        const selected = hasSavedChoice && Array.isArray(savedChoice)
            ? savedChoice.filter(id => available.includes(id))
            : hasSavedChoice && savedChoice === 'all' ? available
                : hasSavedChoice && available.includes(savedChoice) ? [savedChoice]
                    : defaults;
        const effectiveSelected = selected;
        if (!hasSavedChoice && effectiveSelected.length === 1 && domain.forms?.includes(effectiveSelected[0]))
            return directFormDomain(effectiveSelected[0]);
        if (!hasSavedChoice && effectiveSelected.length === 1 && !(domain.forms || []).length && !domain.baseInstrument && !domain.originalLabel)
            return { ...domain, questions: filterDomainQuestions(domain, effectiveSelected) };
        if (domain.forms?.length || domain.baseInstrument || domain.originalLabel || hasSavedChoice) {
            const questions = !hasSavedChoice && !effectiveSelected.length && domain.forms?.length
                ? domain.questions.filter(q => !q.scaleId)
                : filterDomainQuestions(domain, effectiveSelected);
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
    if (choice === 'all') return choicesForDomain(domain).filter(id => id !== 'base');
    if (choice) return [choice].filter(id => id !== 'base');
    return defaultChoicesForDomain(domain).filter(id => id !== 'base');
}
