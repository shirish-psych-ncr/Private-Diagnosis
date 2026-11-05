// Read-only build gate: deployment uses native modules, so no bundles are emitted.
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const { loadModule, localFetch } = require('../tests/module_loader');
const root = path.resolve(__dirname, '..');

async function checkGraph(entry) {
    const cache = new Map();
    const context = vm.createContext({});
    function get(file) {
        if (!cache.has(file)) cache.set(file, new vm.SourceTextModule(fs.readFileSync(file, 'utf8'), {
            identifier: file, context
        }));
        return cache.get(file);
    }
    await get(path.join(root, entry)).link((specifier, parent) => {
        assert(specifier.startsWith('.'), 'Only local module imports are allowed');
        return get(path.resolve(path.dirname(parent.identifier), specifier));
    });
    return cache.size;
}

function checkStyles(file, ancestors = []) {
    assert(!ancestors.includes(file), 'Circular stylesheet import: ' + file);
    const text = fs.readFileSync(file, 'utf8');
    for (const match of text.matchAll(/@import\s+url\("([^"]+)"\);/g)) {
        checkStyles(path.resolve(path.dirname(file), match[1]), [...ancestors, file]);
    }
}

(async () => {
    const count = await checkGraph('app.js');
    await checkGraph('src/scripts/main.js');
    checkStyles(path.join(root, 'styles.css'));
    checkStyles(path.join(root, 'src/styles/main.css'));
    const { main } = await loadModule(vm.createContext({ fetch: localFetch }), 'src/app/data.js');
    const data = await main.namespace.loadClinicalData();
    assert.equal(new Set(data.domains.map(d => d.id)).size, data.domains.length);
    for (const [id, scale] of Object.entries(data.scales)) assert.equal(id, scale.id);
    for (const domain of data.domains) {
        assert.equal(new Set(domain.questions.map(q => q.id)).size, domain.questions.length);
        for (const question of domain.questions) {
            if (question.scaleId) assert(data.scales[question.scaleId], 'Missing ' + question.scaleId);
        }
    }
    assert(!fs.existsSync(path.join(root, 'data.json')), 'Do not recreate the data bundle');
    assert(!fs.existsSync(path.join(root, 'data/core.json')), 'Do not recreate the core bundle');
    assert(fs.statSync(path.join(root, 'app.js')).size < 1024, 'Keep app.js a small entry point');
    console.log('Valid module graph:', count, 'modules;', data.domains.length, 'domains;', Object.keys(data.scales).length, 'table scales. No bundles generated.');
})().catch(error => { console.error(error); process.exitCode = 1; });
