import { loadResource } from './data-resources.js';

export async function loadTree(node) {
    if (node.source) return loadResource(node.source);
    if (node.array) return Promise.all(node.array.map(loadTree));
    if (node.object) return Object.fromEntries(await Promise.all(
        node.object.map(async ([key, value]) => [key, await loadTree(value)])
    ));
    throw new Error('Invalid clinical data manifest');
}
export async function loadDomain(id) {
    const domain = await loadResource('data/domains/' + id + '.json');
    if (!domain.questionSource) return domain;
    const scale = await loadResource(domain.questionSource);
    const questions = new Map([...scale.questions, ...domain.questions].map(q => [q.id, q]));
    const { questionSource, questionOrder, ...metadata } = domain;
    return { ...metadata, questions: questionOrder.map(id => {
        if (!questions.has(id)) throw new Error('Missing question ' + id);
        return questions.get(id);
    }) };
}
export async function loadClinicalData() {
    const index = await loadResource('data/index.json');
    const [core, domains, scales] = await Promise.all([
        loadResource(index.core).then(loadTree),
        Promise.all(index.domains.map(loadDomain)),
        Promise.all(index.scales.map(async id => [id, await loadResource('data/scales/' + id + '.json')]))
    ]);
    return { ...core, domains, scales: Object.fromEntries(scales) };
}
