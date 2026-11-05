
import { L } from '../i18n.js';
import { state } from '../state.js';

/**
 * PDQ-4+ scoring: validity check first, then True-count per scale against its
 * threshold, Section B gates for Borderline (item 98) and Antisocial (item 99),
 * and finally the mandatory clinical-significance criteria A-E, which must ALL
 * be met before a flagged personality disorder enters the differential list.
 */
function scorePdq4(scale, addFlag) {
    const sc = scale.scoring || {};
    const hi = state.lang === 'hi';
    const ans = id => state.responses[scale.id + ':' + id];

    // 1. Validity / infrequency items (pathological response = True)
    const validityHits = (scale.validity ? scale.validity.items : [])
        .filter(it => ans(it.id) === 1)
        .map(it => it.id.replace('pdq_', ''));
    const profileInvalid = validityHits.length > 0;

    // 2. Section B checklists
    const sectionB = sc.sectionB || {};
    const gateCount = partId => {
        const part = (scale.parts || []).find(p => p.id === partId);
        if (!part) return 0;
        return part.questions.filter(q => ans(q.id) === 1).length;
    };
    const gatesMet = {};
    Object.keys(sectionB).forEach(partId => {
        const g = sectionB[partId];
        gatesMet[g.gateScale] = gateCount(partId) >= g.minimum;
    });

    // 3. Clinical significance criteria A-E (clinician-rated follow-up)
    const csPart = (scale.parts || []).find(p => p.clinicianRated);
    const csAnswers = csPart ? csPart.questions.map(q => ans(q.id)) : [];
    const csComplete = csAnswers.length > 0 && csAnswers.every(v => v !== undefined);
    const csMet = csComplete && csAnswers.every(v => v === 1);

    // 4. Per-scale True counts vs thresholds
    const rows = [];
    let flagged = 0;
    (scale.scales || []).forEach(s => {
        const n = s.items.filter(num => ans('pdq_' + num) === 1).length;
        const reached = n >= s.threshold;
        const needsB = !!s.requiresSectionB;
        const gateOk = !needsB || gatesMet[s.slug] === true;
        const positive = reached && gateOk && !profileInvalid;
        const significant = positive && csMet;
        if (significant) { flagged++; (s.disorders || []).forEach(d => addFlag(d, 'PDQ-4+')); }
        rows.push({
            label: L(s.name) + ' (' + (s.profileColumn || s.slug) + ')',
            value: n + '/' + s.items.length,
            flagged: positive,
            detail: [
                reached ? '' : (hi ? 'threshold ' + s.threshold + ' अपूर्ण' : 'below threshold ' + s.threshold),
                needsB ? (gateOk ? (hi ? 'खंड-B पूर्त' : 'Section B met') : (hi ? 'खंड-B अपूर्ण' : 'Section B not met')) : '',
                positive && !csMet ? (hi ? 'A-E नैदानिक महत्व अपूर्ण' : 'criteria A–E not all met') : '',
                significant ? (hi ? 'नैदानिक दृष्ट्या महत्वपूर्ण' : 'clinically significant') : ''
            ].filter(Boolean).join(' · ')
        });
    });

    return {
        name: L(scale.name),
        score: flagged + '/' + rows.length + ' ' + (hi ? 'पैमाने धनात्मक' : 'scales flagged'),
        severity: profileInvalid
            ? (hi ? 'प्रोफ़ाइल अमान्य — सावधानीपूर्वक व्याख्या' : 'Validity flag — interpret with extreme caution')
            : (flagged
                ? (hi ? 'स्क्रीन धनात्मक — संरचित साक्षात्कार आवश्यक' : 'Positive screen — structured interview indicated')
                : (hi ? 'कोई पैमाना धनात्मक नहीं' : 'No scale at threshold')),
        aboveCutoff: flagged > 0,
        notDiagnostic: true,
        disorders: [],
        pdRegister: {
            kind: 'pdq4',
            heading: hi ? 'PDQ-4+ प्रोफ़ाइल (12 पैमाने)' : 'PDQ-4+ profile (12 scales)',
            note: L(sc.notDiagnosticNote || { en: '', hi: '' }) + ' ' + L(sc.clinicalSignificance || { en: '', hi: '' }),
            validity: {
                message: profileInvalid
                    ? (hi ? 'वैधता आइटम ' + validityHits.join(', ') + ' सत्य — प्रोफ़ाइल अमान्य मानें।'
                          : 'Validity item(s) ' + validityHits.join(', ') + ' answered True — consider the profile invalid.')
                    : (hi ? 'वैधता आइटम (64, 76) मिथ्या — प्रतिविमर्श विश्वसनीय।' : 'Validity items (64, 76) False — responding appears valid.'),
                failed: profileInvalid
            },
            rows: rows
        }
    };
}

export { scorePdq4 };
