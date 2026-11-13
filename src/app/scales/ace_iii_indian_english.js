const domainScores = [
    ['Attention', 'ace_attention', 18],
    ['Memory', 'ace_memory', 26],
    ['Verbal fluency', 'ace_fluency', 14],
    ['Language', 'ace_language', 26],
    ['Visuospatial abilities', 'ace_visuospatial', 16]
];

function score(values, questions, form) {
    const answers = new Map(questions.map((question, index) => [question.id, values[index]]));
    const entries = domainScores.map(([name, id, maximum]) => ({ name, id, maximum, value: answers.get(id) }));
    const invalid = entries.find(entry => !Number.isInteger(entry.value) || entry.value < 0 || entry.value > entry.maximum);
    if (invalid) {
        return [{
            name: form.name,
            score: 'Check domain score entry',
            severity: `Enter a whole-number ${invalid.name} subtotal from 0 to ${invalid.maximum}.`,
            notDiagnostic: true
        }];
    }

    const rows = entries.map(entry => ({
        name: entry.name,
        score: `${entry.value}/${entry.maximum}`,
        severity: 'Domain subtotal; interpret clinically',
        notDiagnostic: true
    }));
    rows.push({
        name: 'ACE-III total',
        score: `${entries.reduce((sum, entry) => sum + entry.value, 0)}/100`,
        severity: 'Cognitive screening score; not diagnostic',
        notDiagnostic: true,
        sourceNote: form.interpretationNote
    });
    return rows;
}

export { score };
