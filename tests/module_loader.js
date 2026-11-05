const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const ROOT = path.resolve(__dirname, '..');

// Execute real ES modules inside each fresh jsdom window, including cyclic imports.
async function loadModule(context, entry) {
    const modules = new Map();
    function get(file) {
        file = path.resolve(file);
        if (!modules.has(file)) {
            modules.set(file, new vm.SourceTextModule(fs.readFileSync(file, 'utf8'), {
                context, identifier: file
            }));
        }
        return modules.get(file);
    }
    const main = get(path.join(ROOT, entry));
    await main.link((specifier, parent) => get(path.resolve(path.dirname(parent.identifier), specifier)));
    await main.evaluate();
    return { main, modules };
}

function localFetch(url) {
    const parsed = new URL(String(url), 'http://localhost/');
    if (parsed.origin !== 'http://localhost') throw new Error('Unexpected external fetch ' + url);
    const file = path.resolve(ROOT, '.' + decodeURIComponent(parsed.pathname));
    if (!file.startsWith(ROOT + path.sep)) throw new Error('Path outside fixture root');
    try {
        const text = fs.readFileSync(file, 'utf8');
        return Promise.resolve({ ok: true, json: async () => JSON.parse(text) });
    } catch (error) {
        return Promise.resolve({ ok: false, status: 404, json: async () => { throw error; } });
    }
}

module.exports = { loadModule, localFetch };
