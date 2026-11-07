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
    assert.equal(report('mood', 'qids_sr16', () => 3)[0].score, '27/27');
    assert.equal(report('mood', 'qids_sr16', q => Number(q.id.split('_').at(-1)) <= 4 ? 3 : 0)[0].score, '3/27');
    for (const symptoms of [6, 7]) {
        const rows = report('mood', 'mood_mdq', q => {
            const item = Number(q.id.split('_').at(-1));
            return item === 15 ? 2 : Number(item <= symptoms || item >= 14);
        });
        assert.equal(rows[0].aboveCutoff, symptoms === 7);
    }
    for (const id of ['aase_confidence', 'aase_temptation']) {
        assert.ok(report('substance', id, () => 3).every(row => row.score === '3.00/4'));
    }
    assert.equal(report('wellbeing', 'dts', () => 3)[0].score, '3.00/5');
    const ryff = report('wellbeing', 'ryff', q => q.reverse ? 1 : 6);
    assert.equal(ryff.length, 6);
    assert.ok(ryff.every(r => r.score === '84/84'));
    assert.equal(report('suicide_followup', 'cssrs', q => q.id === 's6' ? 1 : 0)[0].score, '1: No, 2: No, 6: Yes');
    for (const topic of data.domains) {
        for (const id of topic.forms || []) {
            const form = data.scales[id];
            if (!form.sumScores) continue;
            const n = form.parts.flatMap(part => part.questions).length;
            for (const indexes of Object.values(form.sumScores.groups)) {
                assert.equal(new Set(indexes).size, indexes.length, id);
                assert.ok(indexes.every(i => Number.isInteger(i) && i >= 1 && i <= n), id);
            }
            const low = form.matrixOptions[0].v;
            const high = form.matrixOptions.at(-1).v;
            const lengths = Object.values(form.sumScores.groups).map(items => items.length);
            if (form.sumScores.total) lengths.unshift(n);
            for (const value of [low, high]) {
                const rows = report(topic.id, id, q => q.reverse ? low + high - value : value);
                assert.deepEqual(Array.from(rows, row => row.score), lengths.map(length =>
                    (value * length * form.sumScores.multiplier) + '/' + (high * length * form.sumScores.multiplier)), id);
            }
        }
    }
    assert.equal(report('wellbeing', 'ders', () => 1)[0].score, '80/180');
    console.log('Scoring parity:', count, 'cases match reviewed scoring fixtures.');
})().catch(error => { console.error(error); process.exitCode = 1; });
