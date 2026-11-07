/** Y-BOCS-II scores items 1-10 and keeps insight item 11 separate. */
export function score(values, questions, form) {
    const nums = values.map(Number);
    const obsessions = nums.slice(0, 5).reduce((sum, value) => sum + value, 0);
    const compulsions = nums.slice(5, 10).reduce((sum, value) => sum + value, 0);
    return [
        { name: form.name + ' severity total', score: (obsessions + compulsions) + '/50', severity: 'Sum of items 1–10; clinician-rated', notDiagnostic: true },
        { name: 'Y-BOCS-II obsessions subtotal', score: obsessions + '/25', severity: 'Items 1–5', notDiagnostic: true },
        { name: 'Y-BOCS-II compulsions subtotal', score: compulsions + '/25', severity: 'Items 6–10', notDiagnostic: true },
        { name: 'Y-BOCS-II insight', score: nums[10] + '/4', severity: 'Item 11 reported separately', notDiagnostic: true }
    ];
}
