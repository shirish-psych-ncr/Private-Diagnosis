/** CIWA-Ar total; only the source-supported medication note is surfaced. */
export function score(values, questions, form) {
    const total = values.reduce((sum, value) => sum + Number(value), 0);
    return [{ name: form.name + ' total', score: total + '/67',
        severity: total < 10 ? 'Below 10; source says additional medication is not usually needed' : '10 or higher; assess and follow clinical protocol', notDiagnostic: true }];
}
