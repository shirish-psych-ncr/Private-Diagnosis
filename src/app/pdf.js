
import { t } from './i18n.js';
import { state, CLINICAL_DATA } from './state.js';

/* ------------------------------------------------------------------ *
 * 10. CLIENT-SIDE PDF GENERATION (jsPDF + AutoTable) — no transmission
 * ------------------------------------------------------------------ */
function generatePDF() {
    if (!window.jspdf || !state.results) return;
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();
    const r = state.results;
    let y = 20;

    doc.setFontSize(16);
    doc.text('Pre-Consultation Clinical Screening Summary', 14, y); y += 8;
    doc.setFontSize(10);
    doc.setTextColor(120);
    doc.text('Prepared on this device for clinician review.', 14, y); y += 4;
    doc.text('Date: ' + new Date().toISOString().slice(0, 10) +
             '  |  Schema: ' + (CLINICAL_DATA.meta ? CLINICAL_DATA.meta.schemaVersion : 'n/a'), 14, y); y += 10;

    doc.setTextColor(0);
    doc.setFontSize(12);
    doc.text('Visit details', 14, y); y += 6;
    doc.setFontSize(10);
    doc.text('Age group: ' + (state.context.ageGroup || '—'), 14, y); y += 5;
    doc.text('Reason for visit: ' + (state.context.reason || '—').substring(0, 180), 14, y); y += 5;
    doc.text('Medications: ' + (state.context.medications || '—').substring(0, 180), 14, y); y += 5;
    doc.text('Prior diagnoses: ' + (state.context.priorDiagnoses || '—').substring(0, 180), 14, y); y += 10;

    doc.autoTable({
        startY: y,
        head: [['Instrument', 'Raw Score', 'Severity']],
        body: r.instrumentResults.map(x => [x.name, x.score, x.severity]),
        theme: 'striped',
        styles: { fontSize: 9 }
    });
    y = doc.lastAutoTable.finalY + 10;

    // Vanderbilt "For Office Use Only" totals (mirrors the NICHQ scoring sheet)
    const vadrsResult = r.instrumentResults.find(x => x.name === 'VADRS');
    if (vadrsResult) {
        const sc = CLINICAL_DATA.scales.vadrs.scoring;
        const cnt = (ids, min) => ids.filter(id => (state.responses['vadrs:' + id] || 0) >= min).length;
        doc.setFontSize(12);
        doc.text('VADRS — For Office Use Only', 14, y); y += 2;
        doc.autoTable({
            startY: y,
            head: [['Scoring Field', 'Value']],
            body: [
                ['Total scored 2 or 3 in questions 1-9 (inattention)', String(cnt(sc.inattention.ids, sc.inattention.minSymptomValue))],
                ['Total scored 2 or 3 in questions 10-18 (hyperactivity/impulsivity)', String(cnt(sc.hyperactivity.ids, sc.hyperactivity.minSymptomValue))],
                ['Total symptom score for questions 1-18', String(sc.inattention.ids.concat(sc.hyperactivity.ids).reduce((t, id) => t + (state.responses['vadrs:' + id] || 0), 0))],
                ['Total scored 2 or 3 in questions 19-26 (oppositional-defiant)', String(cnt(sc.oppositionalDefiant.ids, sc.oppositionalDefiant.minSymptomValue))],
                ['Total scored 2 or 3 in questions 27-40 (conduct)', String(cnt(sc.conduct.ids, sc.conduct.minSymptomValue))],
                ['Total scored 2 or 3 in questions 41-47 (anxiety/depression)', String(cnt(sc.anxietyDepression.ids, sc.anxietyDepression.minSymptomValue))],
                ['Total scored 4 or 5 in performance questions 48-55', String(cnt(sc.performance.ids, sc.performance.minImpairedValue))],
                ['Average performance score', (() => {
                    const vals = sc.performance.ids.map(id => state.responses['vadrs:' + id]).filter(v => v !== undefined);
                    return vals.length ? (vals.reduce((a, b) => a + b, 0) / vals.length).toFixed(2) : '—';
                })()]
            ],
            theme: 'grid',
            styles: { fontSize: 8 }
        });
        y = doc.lastAutoTable.finalY + 10;
        doc.setFontSize(8);
        doc.setTextColor(120);
        doc.text('Scales should not be used alone to make a diagnosis; DSM criteria require 6+ of 9 core symptoms (parent form items 1-9 or 10-18) plus impairment (score 4 or 5 on any performance item).', 14, y);
        doc.setTextColor(0);
        y += 10;
    }

    // MINI optional assessments A & B: reproduce the printed rating tables
    // ("Symptom Name / Score", "Domain Name / Score") row by row.
    const ratingTables = r.instrumentResults.filter(x => x.ratingRegister && x.ratingRegister.length);
    ratingTables.forEach(tbl => {
        if (y > 230) { doc.addPage(); y = 20; }
        doc.setFontSize(12);
        doc.text(tbl.name + ' — For Office Use Only', 14, y); y += 2;
        doc.autoTable({
            startY: y,
            head: [['Name', 'Score (0-10)']],
            body: tbl.ratingRegister.map(row => [row.label, row.value === undefined ? '—' : String(row.value)]),
            theme: 'grid',
            styles: { fontSize: 8 },
            columnStyles: { 1: { cellWidth: 26 } }
        });
        y = doc.lastAutoTable.finalY + 4;
        doc.setFontSize(8);
        doc.setTextColor(120);
        doc.text('Scale: 0 Not present, 1 Mild, 3 Moderate, 6 Severe, 10 Extreme. Each row is rated independently; no composite total is derived and these ratings do not gate any diagnostic box.', 14, y);
        doc.setTextColor(0);
        y += 10;
    });

    // Personality-disorder screens: reproduce the IPDE scoring summary and the
    // PDQ-4+ profile sheet (scale, keyed count, status) as tables.
    const pdRegisters = r.instrumentResults.filter(x => x.pdRegister && x.pdRegister.rows.length);
    pdRegisters.forEach(reg => {
        if (y > 230) { doc.addPage(); y = 20; }
        doc.setFontSize(12);
        doc.text(reg.name + ' — ' + reg.pdRegister.heading, 14, y); y += 2;
        if (reg.pdRegister.validity) {
            doc.setFontSize(8);
            doc.setTextColor(reg.pdRegister.validity.failed ? 170 : 60, reg.pdRegister.validity.failed ? 40 : 110, reg.pdRegister.validity.failed ? 40 : 60);
            doc.text(reg.pdRegister.validity.message, 14, y); y += 4;
            doc.setTextColor(0);
        }
        doc.autoTable({
            startY: y,
            head: [['Module / scale', 'Keyed items', 'Status']],
            body: reg.pdRegister.rows.map(row => [row.label, row.value, (row.flagged ? '* ' : '') + (row.detail || 'Not flagged')]),
            theme: 'grid',
            styles: { fontSize: 8 },
            columnStyles: { 1: { cellWidth: 24 }, 2: { cellWidth: 60 } }
        });
        y = doc.lastAutoTable.finalY + 4;
        doc.setFontSize(8);
        doc.setTextColor(120);
        doc.text(doc.splitTextToSize('Screening only — not diagnostic and no dimensional score. ' + reg.pdRegister.note, 180), 14, y);
        doc.setTextColor(0);
        y += 12;
    });

    doc.setFontSize(12);
    doc.text('Differential Considerations (hypothesis-generating only)', 14, y); y += 2;
    doc.autoTable({
        startY: y,
        head: [['Tier', 'Condition', 'DSM-5-TR', 'ICD-11', 'Triggering Instruments']],
        body: r.differentials.length
            ? r.differentials.map(d => ['T' + d.tier, d.name.en, d.dsm5, d.icd11, d.sources.join(', ')])
            : [['—', 'No significant flags', '—', '—', '—']],
        theme: 'grid',
        styles: { fontSize: 8 }
    });
    y = doc.lastAutoTable.finalY + 6;

    // Classification governance note (see WHITEPAPER.md Appendix A: Comparative Nosological Index)
    doc.setFontSize(8);
    doc.setTextColor(120);
    doc.text('Codes are comparative index entries, not a DSM-to-ICD crosswalk. Tier numbers are navigation aids, not prevalence claims.', 14, y); y += 4;
    doc.text('Record the classification system, version and code independently; do not infer a diagnosis from a code label alone.', 14, y); y += 4;
    doc.text('ICD-11 sleep-wake disorders are in Chapter 07 and gender incongruence / sexual dysfunctions in Chapter 17; verify release and local coding rules.', 14, y); y += 4;
    doc.setTextColor(0);
    y += 6;

    if (r.safetyTriggered) {
        doc.setFontSize(11);
        doc.setTextColor(180, 0, 0);
        doc.text('SAFETY FLAG: Patient endorsed one or more crisis items during screening.', 14, y); y += 6;
        doc.setTextColor(0);
    }
    doc.setFontSize(8);
    doc.setTextColor(120);
    doc.text('This document is a screening aid, not a diagnosis. Clinical judgment is required.', 14, 285);

    doc.save('EPCSS_screening_summary.pdf');
}

export { generatePDF };
