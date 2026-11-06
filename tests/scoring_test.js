const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const crypto = require('node:crypto');
const { loadModule, localFetch } = require('./module_loader');
const { casesFor, setCase } = require('./scoring_cases');

(async () => {
    const context = vm.createContext({ fetch: localFetch });
    const { main, modules } = await loadModule(context, 'src/app/results-computation.js');
    const stateModule = modules.get(path.resolve(__dirname, '../src/app/state.js')).namespace;
    const { main: loader } = await loadModule(context, 'src/app/data.js');
    const data = await loader.namespace.loadClinicalData();
    stateModule.setClinicalData(data);
    let count = 0;
    for (const domain of data.domains) {
        const expected = JSON.parse(fs.readFileSync(path.join(__dirname, 'scoring-baselines', domain.id + '.json'), 'utf8'));
        for (const scenario of casesFor(domain)) {
            setCase(stateModule.state, data, scenario);
            const result = main.namespace.computeResults();
            const hash = crypto.createHash('sha256').update(JSON.stringify(result)).digest('hex');
            const key = [scenario.lang, scenario.ageGroup, scenario.pattern].join('/');
            assert.equal(hash, expected[key], domain.id + '/' + key + ' changed from the pre-refactor output');
            count++;
        }
    }
    // Exercise alternatives through the same selected-domain path as the browser.
    const state = stateModule.state;
    function report(topic, form, valueFor) {
        state.selectedDomains.clear();
        state.selectedDomains.add(topic);
        state.scaleChoices.set(topic, form);
        state.responses = {};
        for (const part of data.scales[form].parts) {
            for (const q of part.questions) state.responses[form + ':' + q.id] = valueFor(q);
        }
        return main.namespace.computeResults().instrumentResults;
    }
    assert.deepEqual(Array.from(report('gender', 'ugds_gs', q =>
        ['u1', 'u3', 'u4', 'u5'].includes(q.id) ? 5 : 1), r => r.score), ['5.00/5', '1.00/5']);
    assert.equal(report('trauma', 'itq', () => 2)[0].severity, 'CPTSD screening pattern');
    assert.equal(report('trauma', 'itq', q => q.id.startsWith('p') ? 2 : 0)[0].severity, 'PTSD screening pattern');
    assert.equal(report('trauma', 'itq', q => ['p7','p8','p9'].includes(q.id) ? 0 : 4)[0].aboveCutoff, false);
    assert.equal(report('wellbeing', 'maas', () => 3)[0].score, '3.00/6');
    const ryff = report('wellbeing', 'ryff', q => q.reverse ? 1 : 6);
    assert.equal(ryff.length, 6);
    assert.ok(ryff.every(r => r.score === '84/84'));
    assert.equal(report('suicide_followup', 'cssrs', q => q.id === 's6' ? 1 : 0)[0].score, '1: No, 2: No, 6: Yes');
    console.log('Scoring parity:', count, 'cases match reviewed scoring fixtures.');
})().catch(error => { console.error(error); process.exitCode = 1; });
