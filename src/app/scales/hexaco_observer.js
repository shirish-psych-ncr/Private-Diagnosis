import { L } from '../i18n.js';
import { state, CLINICAL_DATA } from '../state.js';

function scoreHexacoObserver(form) {
    const answers = new Map(form.parts.flatMap(part => part.questions)
        .map(question => [question.itemNumber, state.responses[form.id + ':' + question.id]]));
    const reverse = new Set(form.scoring.reverseItems);
    const facetScores = {};
    const rows = [];
    for (const [key, facet] of Object.entries(form.facets)) {
        const values = facet.items.map(item => {
            const value = answers.get(item);
            return reverse.has(item) ? 6 - value : value;
        });
        if (!values.every(Number.isFinite)) return [];
        const mean = values.reduce((sum, value) => sum + value, 0) / values.length;
        facetScores[key] = mean;
        rows.push({ name: L(facet.name), score: mean.toFixed(2) + '/5',
            severity: 'Observer-rated facet mean; descriptive profile', notDiagnostic: true });
    }
    for (const domain of Object.values(form.domains)) {
        const values = domain.facets.map(key => facetScores[key]);
        const mean = values.reduce((sum, value) => sum + value, 0) / values.length;
        rows.push({ name: L(domain.name), score: mean.toFixed(2) + '/5',
            severity: 'Observer-rated domain mean; descriptive profile', notDiagnostic: true,
            sourceNote: L(form.scoring.interpretationNote) });
    }
    return rows;
}

export { scoreHexacoObserver };
