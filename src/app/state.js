
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
    results: null             // computed at finish
};

let CLINICAL_DATA = null;     // populated from the modular data tree
let I18N = null;              // populated from the modular data tree


let addFlagGlobal = () => {};
function setFlagSink(sink) { addFlagGlobal = sink; }
function setClinicalData(payload) {
    CLINICAL_DATA = payload.clinical || payload;
    I18N = payload.i18n || {};
}

export { state, CLINICAL_DATA, I18N, addFlagGlobal, setFlagSink, setClinicalData };

export function selectedDomainForms() {
    return CLINICAL_DATA.domains.filter(domain => state.selectedDomains.has(domain.id)).map(domain => {
        const choice = state.scaleChoices.get(domain.id) || domain.defaultForm;
        if (domain.forms?.includes(choice)) {
            const form = CLINICAL_DATA.scales[choice];
            const questions = form.parts.flatMap(part => part.questions
                .filter(q => !q.requires || state.responses[choice + ':' + q.requires] === 1)
                .map((q, i) => ({ ...q, scale: q.scale ?? form.matrixOptions, section: i === 0 ? part.name : null })));
            return { id: choice, directForm: true, name: form.name, timeframe: form.directions, contextFields: form.contextFields, durationOptions: form.durationOptions, questions };
        }
        if (!choice || choice === 'all') return domain;
        return { ...domain, questions: domain.questions.filter(q => !q.scaleId || q.scaleId === choice) };
    });
}
