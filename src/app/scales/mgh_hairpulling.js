import { L } from '../i18n.js';

function score(values, _questions, form) {
    const total = values.reduce((sum, value) => sum + value, 0);
    return [{
        name: L(form.name),
        score: total + '/28',
        severity: 'Descriptive symptom measure; no diagnostic cutoff supplied',
        notDiagnostic: true
    }];
}

export { score };
