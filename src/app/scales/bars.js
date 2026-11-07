/** BARS objective/subjective sum and global assessment are reported separately. */
export function score(values, questions, form) {
    const objective = Number(values[0]);
    const awareness = Number(values[1]);
    const distress = Number(values[2]);
    const global = Number(values[3]);
    return [
        { name: form.name + ' objective + subjective total', score: objective + awareness + distress + '/9', severity: 'Three-item subtotal' },
        { name: 'Global Clinical Assessment of Akathisia', score: global + '/5', severity: 'Separate global clinician rating' }
    ];
}
