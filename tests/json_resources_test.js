const assert = require('node:assert/strict');
const vm = require('node:vm');
const { loadModule } = require('./module_loader');

(async () => {
    const files = {
        'scale.json': { id: 'example', parts: { $concat: ['first.json', 'second.json'] }, source: 'publication' },
        'first.json': [{ text: { $file: 'text.json' }, score: 0 }],
        'second.json': [{ text: 'second', optional: false, note: null }],
        'text.json': { en: 'First', hi: 'पहला' },
        'cycle.json': { $file: 'cycle.json' },
        'invalid.json': { $concat: ['text.json'] }
    };
    const context = vm.createContext({ fetch: async file => {
        // Reverse completion order to ensure network timing cannot reorder questions.
        if (file === 'first.json') await new Promise(resolve => setTimeout(resolve, 10));
        return { ok: Object.hasOwn(files, file), status: 404, json: async () => files[file] };
    } });
    const { main } = await loadModule(context, 'src/app/data-resources.js');
    const load = main.namespace.loadResource;
    assert.deepEqual(JSON.parse(JSON.stringify(await load('scale.json'))), {
        id: 'example', parts: [{ text: { en: 'First', hi: 'पहला' }, score: 0 },
            { text: 'second', optional: false, note: null }], source: 'publication'
    });
    await assert.rejects(load('cycle.json'), /Circular JSON reference/);
    await assert.rejects(load('missing.json'), /HTTP 404/);
    await assert.rejects(load('invalid.json'), /must contain arrays/);
    console.log('JSON resource checks passed: ordered chunks, nested bilingual values, missing files and cycles.');
})().catch(error => { console.error(error); process.exitCode = 1; });
