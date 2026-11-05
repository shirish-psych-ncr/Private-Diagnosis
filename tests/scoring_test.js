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
    console.log('Scoring parity:', count, 'cases match the original engine.');
})().catch(error => { console.error(error); process.exitCode = 1; });
