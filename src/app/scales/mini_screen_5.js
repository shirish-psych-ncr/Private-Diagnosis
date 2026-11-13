import { CLINICAL_DATA } from '../state.js';
import { L } from '../i18n.js';

function score(values, questions, form) {
    const answers = new Map(questions.map((question, index) => [question.id, values[index]]));
    const topics = new Map((CLINICAL_DATA.domains || []).map(domain => [domain.id, L(domain.name)]));
    const positive = (form.screenRoutes || []).filter(route => {
        const routeValues = route.questions.map(id => answers.get(id));
        return route.match === 'all'
            ? routeValues.every(value => value === 1)
            : routeValues.some(value => value === 1);
    });
    if (!positive.length) return [{
        name: L(form.name),
        score: 'No follow-up module indicated',
        severity: 'Screening result only; not diagnostic',
        sourceNote: L(form.interpretationNote)
    }];
    return positive.map(route => ({
        name: L(form.name) + ' — Module ' + route.module,
        score: 'Follow-up topic: ' + (route.topicIds || []).map(id => topics.get(id) || id).join(', '),
        severity: 'Screen positive; clinician follow-up suggested',
        aboveCutoff: true,
        notDiagnostic: true,
        sourceNote: 'No topic or additional scale was selected automatically. ' + L(form.interpretationNote)
    }));
}

export { score };
