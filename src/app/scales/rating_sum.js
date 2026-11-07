export function scoreRating(values, questions, form) {
    const ranges = questions.map(question => {
        const options = question.scale || form.matrixOptions || [];
        return { min: question.scoreMin ?? Math.min(...options.map(option => option.v)),
            max: question.scoreMax ?? Math.max(...options.map(option => option.v)) };
    });
    const keyed = values.map((value, index) => questions[index].reverseScored
        ? ranges[index].min + ranges[index].max - value : value);
    const total = keyed.reduce((sum, value) => sum + value, 0);
    const min = ranges.reduce((sum, range) => sum + range.min, 0);
    const max = ranges.reduce((sum, range) => sum + range.max, 0);
    return [{ name: form.name, score: total + '/' + max,
        severity: form.administeredBy === 'clinician' ? 'Clinician rating; interpret in clinical context' : 'Self-report total; not diagnostic',
        notDiagnostic: true, scoreRange: min + '-' + max }];
}
