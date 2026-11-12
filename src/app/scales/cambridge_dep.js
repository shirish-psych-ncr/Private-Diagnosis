function scoreCambridge(form, state) {
    const questions = form.parts.flatMap(part => part.questions);
    const frequencyItems = questions.filter(question => question.id.endsWith('_frequency'));
    if (!frequencyItems.length) return [];

    let frequencyTotal = 0;
    let durationTotal = 0;
    let endorsed = 0;
    for (const item of frequencyItems) {
        const frequency = state.responses[form.id + ':' + item.id];
        if (!Number.isFinite(frequency)) return [];
        frequencyTotal += frequency;
        if (frequency <= 0) continue;

        endorsed++;
        const durationId = item.id.replace('_frequency', '_duration');
        const duration = state.responses[form.id + ':' + durationId];
        if (!Number.isFinite(duration)) return [];
        durationTotal += duration;
    }

    const count = frequencyItems.length;
    const meanFrequency = frequencyTotal / count;
    const meanDuration = endorsed ? durationTotal / endorsed : 0;
    const sourceNote = form.interpretationNote;
    return [
        { name: 'CDS total', score: `${frequencyTotal + durationTotal}/290`,
            severity: 'Descriptive profile; not diagnostic', notDiagnostic: true, sourceNote },
        { name: 'Experiences endorsed', score: `${endorsed}/${count}`,
            severity: 'Frequency above zero', notDiagnostic: true, sourceNote },
        { name: 'Mean frequency (all items)', score: `${meanFrequency.toFixed(2)}/4`,
            severity: 'Descriptive mean', notDiagnostic: true, sourceNote },
        { name: 'Mean duration (endorsed items)', score: `${meanDuration.toFixed(2)}/6`,
            severity: 'Descriptive mean', notDiagnostic: true, sourceNote }
    ];
}

export { scoreCambridge };
