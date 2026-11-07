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
    const newAnxietyForms = [
        ['hama', 14, 56, 'clinician'], ['pswq', 16, 80, 'self-report'], ['bai', 21, 63, 'self-report'],
        ['pdss_sr', 7, null, 'self-report'], ['mia', 55, null, 'self-report'],
        ['lsas', 48, null, 'self-report'], ['bfne', 12, 60, 'self-report'], ['hads', 14, null, 'self-report']
    ];
    for (const [id, n, max, role] of newAnxietyForms) {
        const form = data.scales[id];
        assert.ok(form, id + ' is loaded');
        assert.equal(form.administeredBy, role, id + ' administration role');
        assert.equal(form.parts.flatMap(part => part.questions).length, n, id + ' item count');
        const rows = report('anxiety', id, () => id === 'mia' ? 0 : 1);
        assert.ok(rows.length > 0, id + ' returns score rows');
        if (max) assert.equal(rows[0].score, (id === 'hama' ? 14 : id === 'pswq' ? 36 : id === 'bfne' ? 28 : 21) + '/' + max, id + ' score range/scoring');
        if (id === 'pdss_sr') assert.equal(rows[0].score, '1.00/4');
        if (id === 'hads') assert.deepEqual(Array.from(rows, row => row.score), ['7/21', '7/21']);
        if (id === 'lsas') assert.deepEqual(Array.from(rows, row => row.score), ['24/72', '24/72', '48/144']);
        if (id === 'mia') assert.ok(rows.every(row => row.severity === 'No applicable situations rated'));
    }
    assert.equal(data.scales.ies_r.parts.flatMap(part => part.questions).length, 22);
    const iesRows = report('trauma', 'ies_r', () => 2);
    assert.deepEqual(Array.from(iesRows, row => row.score), ['44/88', '2.00/4', '2.00/4', '2.00/4']);
    assert.equal(data.scales.asds.parts.flatMap(part => part.questions).length, 20);
    assert.equal(report('trauma', 'asds', () => 1)[0].score, '20/100');
    assert.equal(data.scales.panss.administeredBy, 'clinician');
    assert.equal(data.scales.panss.parts.flatMap(part => part.questions).length, 30);
    assert.deepEqual(Array.from(report('psychosis', 'panss', () => 1), row => row.score),
        ['7/49', '7/49', '16/112', '30/210']);
    assert.deepEqual(Array.from(report('psychosis', 'panss', () => 7), row => row.score),
        ['49/49', '49/49', '112/112', '210/210']);
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
