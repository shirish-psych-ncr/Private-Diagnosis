// Synthetic parity cases protect the structural refactor; they are not clinical validation.
function casesFor(domain) {
    return ['en', 'hi'].flatMap(lang => ['adult', 'pediatric'].flatMap(ageGroup =>
        ['empty', 'zero', 'one', 'two', 'mixed'].map(pattern => ({ domain: domain.id, lang, ageGroup, pattern }))));
}

function setCase(state, data, scenario) {
    state.lang = scenario.lang;
    state.context.ageGroup = scenario.ageGroup;
    state.selectedDomains.clear();
    state.selectedDomains.add(scenario.domain);
    state.safetyFlags = [];
    state.responses = {};
    state.results = null;
    if (scenario.pattern === 'empty') return;
    let index = 0;
    function fill(key) {
        index++;
        if (scenario.pattern === 'mixed' && index % 5 === 0) return;
        state.responses[key] = scenario.pattern === 'zero' ? 0 : scenario.pattern === 'one' ? 1
            : scenario.pattern === 'two' ? 2 : index % 3;
    }
    for (const domain of data.domains) for (const question of domain.questions) fill(domain.id + ':' + question.id);
    for (const [id, scale] of Object.entries(data.scales)) {
        for (const part of scale.parts || []) for (const question of part.questions || []) fill(id + ':' + question.id);
    }
}

module.exports = { casesFor, setCase };
