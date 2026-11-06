// Limit concurrent downloads on mobile connections and static hosts.
const waiting = [];
let active = 0;
const maxDownloads = 8;

async function download(file) {
    if (active >= maxDownloads) await new Promise(resolve => waiting.push(resolve));
    else active++;
    try {
        const response = await fetch(file, { cache: 'no-cache' });
        if (!response.ok) {
            const error = new Error(file + ': HTTP ' + response.status);
            error.status = response.status;
            throw error;
        }
        return await response.json();
    } finally {
        if (waiting.length) waiting.shift()();
        else active--;
    }
}

export async function fetchJSON(file) {
    try {
        return await download(file);
    } catch (error) {
        if (!(error instanceof TypeError || error.name === 'TypeError' ||
              error.status === 408 || error.status === 429 || error.status >= 500)) throw error;
        await new Promise(resolve => setTimeout(resolve, 500));
        return download(file);
    }
}

export async function loadResource(file, ancestors = []) {
    if (ancestors.includes(file)) throw new Error('Circular JSON reference: ' + file);
    return resolveReferences(await fetchJSON(file), [...ancestors, file]);
}

async function resolveReferences(value, ancestors) {
    if (Array.isArray(value)) return Promise.all(value.map(item => resolveReferences(item, ancestors)));
    if (value === null || typeof value !== 'object') return value;
    const keys = Object.keys(value);
    if (keys.length === 1 && keys[0] === '$file') return loadResource(value.$file, ancestors);
    if (keys.length === 1 && keys[0] === '$concat') {
        const chunks = await Promise.all(value.$concat.map(file => loadResource(file, ancestors)));
        if (chunks.some(chunk => !Array.isArray(chunk))) throw new Error('JSON list chunks must contain arrays');
        return chunks.flat();
    }
    return Object.fromEntries(await Promise.all(Object.entries(value).map(
        async ([key, item]) => [key, await resolveReferences(item, ancestors)]
    )));
}
