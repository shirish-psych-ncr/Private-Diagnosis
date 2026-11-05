import { state, CLINICAL_DATA } from '../state.js';
import { optionsForQuestion } from '../screen-in.js';
import { severityBand } from './bands.js';

export function scoreRawSum(domain, addFlag) {
    // Domain raw-sum scoring against cutoff (PHQ-9/GAD-7/PCL-5/ISI/AUDIT-C/ASRS/CAARS-style)
    let sum = 0, answered = 0;
    domain.questions.forEach(q => {
        if (q.scaleId) return;   // screen-in gates are not scored items
        const v = state.responses[domain.id + ':' + q.id];
        if (v !== undefined) { sum += v; answered++; }
    });
    const maxPossible = domain.questions.filter(q => !q.scaleId).reduce((m, q) =>
        m + Math.max(...optionsForQuestion(q).map(o => o.v)), 0);
    const cutoff = domain.cutoff != null ? domain.cutoff : Math.round(maxPossible * 0.4);
    const bands = domain.bands || [
        { max: Math.floor(cutoff * 0.5), severity: state.lang === 'hi' ? 'हल्का' : 'Mild' },
        { max: Math.floor(cutoff * 0.75), severity: state.lang === 'hi' ? 'मध्यम' : 'Moderate' },
        { max: cutoff, severity: state.lang === 'hi' ? 'गंभीर' : 'Moderately severe' },
        { max: Infinity, severity: state.lang === 'hi' ? 'अत्यंत गंभीर' : 'Severe' }
    ];
    const aboveCutoff = sum >= cutoff;
    const severity = severityBand(sum, bands);
    if (aboveCutoff) {
        domain.questions.forEach(q => {
            if (q.scaleId) return;   // screen-in gates flag via their own route
            const v = state.responses[domain.id + ':' + q.id];
            if ((v || 0) >= 2 && q.disorders) q.disorders.forEach(d => addFlag(d, domain.baseInstrument || domain.instrument || domain.id));
        });
    }
    // Resolve the deployed instrument's canonical name from the library
    // (the clinical data instruments map), falling back to the domain id.
    let instrumentName = (domain.baseInstrument || domain.instrument || domain.id);
    if (CLINICAL_DATA.instruments) {
        const slug = instrumentName.toLowerCase().replace(/[^a-z0-9]/g, '');
        const matchKey = Object.keys(CLINICAL_DATA.instruments)
            .find(k => k.toLowerCase().replace(/[^a-z0-9]/g, '') === slug);
        if (matchKey) instrumentName = matchKey;
    }
    return {
        name: instrumentName,
        score: sum + '/' + maxPossible,
        severity,
        aboveCutoff,
        answered, total: domain.questions.length,
        disorders: aboveCutoff ? collectDomainDisorders(domain) : []
    };
}

function collectDomainDisorders(domain) {
    const set = new Set();
    domain.questions.forEach(q => (q.disorders || []).forEach(d => set.add(d)));
    return [...set];
}
