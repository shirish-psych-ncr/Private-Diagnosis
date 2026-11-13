import { state } from '../state.js';
import { L } from '../i18n.js';

function score(values, questions, form) {
    const answers = new Map(questions.map((question, index) => [question.id, values[index]]));
    const detailQuestions = new Map(form.parts.flatMap(part => part.questions).map(question => [question.id, question]));
    const events = [];
    for (let number = 1; number <= 6; number++) {
        const id = `ctq_echo_${number}`;
        const response = answers.get(id);
        if (!Number.isFinite(response)) continue;
        const fields = [
            [`${id}_age`, 'Age (years)'],
            [`${id}_trauma`, 'Reported traumatic impact (1–7)'],
            [`${id}_confide`, 'Reported confiding (1–7)']
        ];
        const details = fields.flatMap(([fieldId, label]) => {
            const value = state.responses[form.id + ':' + fieldId];
            if (!Number.isFinite(value)) return [];
            const question = detailQuestions.get(fieldId);
            const option = question?.scale?.find(item => item.v === value);
            return [`${label}: ${option ? L(option.label) : value}`];
        });
        events.push({
            label: L(detailQuestions.get(id)?.text || `Event ${number}`),
            value: [response === 1 ? 'Yes' : 'No', ...details].join('; ')
        });
    }
    return [{
        name: L(form.name),
        score: 'Event history recorded; no total score',
        severity: 'Descriptive history; not a diagnostic score',
        notDiagnostic: true,
        eventRegister: events,
        sourceNote: form.interpretationNote || form.attribution
    }];
}

export { score };
