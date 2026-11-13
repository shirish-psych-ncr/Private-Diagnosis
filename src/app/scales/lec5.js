import { state } from '../state.js';
import { L } from '../i18n.js';

function score(values, questions, form) {
    const options = new Map((form.matrixOptions || []).map(option => [option.v, L(option.label)]));
    const answered = new Map(questions.map((question, index) => [question.id, values[index]]));
    const rows = form.parts.flatMap(part => part.questions).map(question => ({
        label: question.itemNumber + '. ' + L(question.text),
        value: (answered.get(question.id) || state.responses[form.id + ':' + question.id] || [])
            .map(value => options.get(value) || String(value)).join('; ') || 'No response selected'
    }));
    return [{
        name: L(form.name),
        score: 'Exposure history recorded; no total score',
        severity: 'Descriptive event history; not diagnostic',
        notDiagnostic: true,
        eventRegister: rows,
        sourceNote: 'The LEC-5 identifies potentially traumatic event exposures. It does not yield a total or composite score.'
    }];
}

export { score };
