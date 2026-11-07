/** BPRS-24 total includes only items actually assessed. */
export function score(values, questions, form) {
    const rated = values.map(Number).filter(value => value >= 1 && value <= 7);
    const total = rated.reduce((sum, value) => sum + value, 0);
    return [{ name: form.name + ' total', score: total + '/' + (rated.length * 7),
        severity: `${rated.length} of 24 items rated; no diagnostic cutoff applied`, notDiagnostic: true }];
}
