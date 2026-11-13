import { L } from '../i18n.js';

function score(values, questions, form) {
    const total = values.reduce((sum, value, index) => {
        const question = questions[index];
        return sum + (question.reverse ? 1 - value : value);
    }, 0);
    const positive = total >= form.scoringProfile.referenceThreshold;
    return [{
        name: L(form.name),
        score: total + '/14',
        severity: positive
            ? 'At or above the supplied screen reference; discuss with a clinician'
            : 'Below the supplied screen reference',
        aboveCutoff: positive,
        notDiagnostic: true,
        sourceNote: L(form.interpretationNote)
    }];
}

export { score };
