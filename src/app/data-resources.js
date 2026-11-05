/** Resolve explicit JSON sections without changing question order or clinical values. */
export async function fetchJSON(file) {
    const response = await fetch(file, { cache: 'no-store' });
    if (!response.ok) throw new Error(file + ': HTTP ' + response.status);
    return response.json();
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
