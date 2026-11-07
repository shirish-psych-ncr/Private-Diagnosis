/** CAPS-5 clinician worksheet; outputs criterion tallies, never an autonomous diagnosis. */
export function score(values, questions, form) {
    const a = Object.fromEntries(questions.map((question, i) => [question.id, Number(values[i])]));
    const symptom = (n) => a['caps5_' + n] || 0;
    const traumaRelated = n => ![9, ...Array.from({ length: 10 }, (_, i) => i + 11)].includes(n) || a['caps5_tr_' + n] <= 1;
    const present = n => symptom(n) >= 2 && traumaRelated(n);
    const clusters = [
        { name: 'Criterion B - intrusion', items: [1, 2, 3, 4, 5], needed: 1 },
        { name: 'Criterion C - avoidance', items: [6, 7], needed: 1 },
        { name: 'Criterion D - cognition and mood', items: [8, 9, 10, 11, 12, 13, 14], needed: 2 },
        { name: 'Criterion E - arousal and reactivity', items: [15, 16, 17, 18, 19, 20], needed: 2 }
    ];
    const severity = n => traumaRelated(n) ? symptom(n) : 0;
    const rows = [];
    let total = 0;
    for (const cluster of clusters) {
        const subtotal = cluster.items.reduce((sum, n) => sum + severity(n), 0);
        const count = cluster.items.filter(present).length;
        total += subtotal;
        rows.push({ name: cluster.name, score: subtotal + '/' + (cluster.items.length * 4),
            severity: count + ' threshold symptom(s); ' + (count >= cluster.needed ? 'cluster count met' : 'cluster count not met'), notDiagnostic: true });
    }
    const criterionA = a.caps5_a === 1;
    const criterionF = a.caps5_22 === 1;
    const criterionG = [23, 24, 25].some(n => symptom(n) >= 2);
    const clusterCriteria = clusters.every(cluster => cluster.items.filter(present).length >= cluster.needed);
    const criteriaTally = criterionA && clusterCriteria && criterionF && criterionG;
    rows.unshift({ name: form.name + ' symptom severity total', score: total + '/80',
        severity: 'Sum of trauma-related items 1–20; descriptive clinician rating', notDiagnostic: true });
    rows.push({ name: 'Criterion A - qualifying exposure', score: criterionA ? 'Met' : 'Not met', severity: 'Clinician-recorded criterion' });
    rows.push({ name: 'Criterion F - duration over one month', score: criterionF ? 'Met' : 'Not met', severity: 'Clinician-recorded criterion' });
    rows.push({ name: 'Criterion G - distress or impairment', score: criterionG ? 'Met' : 'Not met', severity: 'Any of items 23–25 rated at least 2' });
    rows.push({ name: 'CAPS-5 criteria tally', score: criteriaTally ? 'All entered criteria met' : 'Entered criteria not all met',
        severity: 'Clinician must independently review all criteria and differential diagnoses; this is not a diagnosis' });
    const diss = [29, 30].filter(n => symptom(n) >= 2 && a['caps5_tr_' + n] <= 1).length;
    rows.push({ name: 'Dissociative symptom count', score: diss + '/2', severity: diss ? 'Review dissociative subtype' : 'No threshold dissociative symptoms entered' });
    rows.push({ name: 'Dissociation cluster severity', score: [29, 30].reduce((sum, n) => sum + (a['caps5_tr_' + n] <= 1 ? symptom(n) : 0), 0) + '/8', severity: 'Separate from the PTSD total' });
    rows.push({ name: 'Delayed onset', score: a.caps5_21 ? 'Yes' : 'No', severity: 'More than six months after event' });
    for (const [n, label] of [[26, 'Global validity'], [27, 'Global severity'], [28, 'Global improvement']])
        rows.push({ name: label, score: String(symptom(n)), severity: 'Clinician-rated global item' });
    return rows;
}
