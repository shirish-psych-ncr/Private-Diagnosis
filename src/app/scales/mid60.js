
import { L } from '../i18n.js';
import { dissDisorder } from '../scoring/shared.js';
import { state, addFlagGlobal } from '../state.js';

/**
 * MID-60 (Multidimensional Inventory of Dissociation, 60-item short form)
 * scoring: index = mean of all 60 ratings x 10 (0-100), compared against the
 * printed score ranges; each named subscale is scored as its own mean x 10
 * and compared against its published clinical cutoff. Subscales above cutoff
 * flag the dissociative-disorder categories for the structured interview —
 * the inventory itself never makes a diagnosis.
 */
function scoreMid60(scale) {
    const hi = state.lang === 'hi';
    const ans = id => state.responses[scale.id + ':' + id];
    const ids = [];
    (scale.parts || []).forEach(part => part.questions.forEach(q => ids.push(q.id)));
    const got = ids.filter(id => ans(id) !== undefined).map(id => Number(ans(id)));
    const complete = got.length === ids.length;
    const mean = got.length ? got.reduce((a, b) => a + b, 0) / got.length : null;
    const index = mean === null ? null : Math.round(mean * 10 * 10) / 10;   // 0-100, one decimal
    const rangeLabel = r => L(r.label);
    const band = index === null ? null : (scale.scoreRanges || []).find(r => index <= r.max);

    const rows = [];
    const flaggedKeys = [];
    Object.keys(scale.subscales || {}).forEach(slug => {
        const sub = scale.subscales[slug];
        const sids = sub.items.map(n => 'mid_' + n);
        const sgot = sids.filter(id => ans(id) !== undefined).map(id => Number(ans(id)));
        const sMean = sgot.length ? sgot.reduce((a, b) => a + b, 0) / sgot.length : null;
        const sIndex = sMean === null ? null : Math.round(sMean * 10 * 10) / 10;
        const over = sIndex !== null && sgot.length === sids.length && sIndex >= Number(sub.cutoff);
        if (over) flaggedKeys.push(slug);
        rows.push({
            label: L(sub.name),
            value: sIndex === null ? '—' : (sIndex.toFixed(1) + ' / ≥' + sub.cutoff),
            flagged: over,
            detail: sIndex === null
                ? (hi ? 'अपूर्ण (' + sgot.length + '/' + sids.length + ')' : 'Incomplete (' + sgot.length + '/' + sids.length + ')')
                : (over
                    ? (hi ? 'कटऑफ से ऊपर — पूर्ण नैदानिक साक्षात्कार आवश्यक' : 'Above clinical cutoff — needs full diagnostic interview')
                    : (hi ? 'कटऑफ से नीचे' : 'Below clinical cutoff'))
        });
    });

    // Persecutory / self-harm intrusions always raise the risk pathway,
    // regardless of the total index.
    const persec = ['did_persecutory_intrusions', 'did_angry_intrusions']
        .filter(slug => flaggedKeys.includes(slug));

    const DISORDERS_BY_SUBSCALE = {
        did_amnesia_recent: ['dissociative_identity_disorder', 'other_specified_dissociative_disorder', 'dissociative_amnesia'],
        did_alt_awareness: ['dissociative_identity_disorder', 'other_specified_dissociative_disorder'],
        did_angry_intrusions: ['dissociative_identity_disorder', 'other_specified_dissociative_disorder'],
        did_persecutory_intrusions: ['dissociative_identity_disorder', 'other_specified_dissociative_disorder'],
        drdepersonalisation: ['depersonalisation_derealisation_disorder'],
        amnesia_memory_distress: ['dissociative_amnesia'],
        amnesia_autobiographical: ['dissociative_amnesia'],
        ptsd_flashbacks: ['ptsd'],
        conversion_body: ['somatic_symptom_disorder'],
        conversion_seizures: ['somatic_symptom_disorder'],
        general_trance: ['other_specified_dissociative_disorder'],
        general_self_confusion: ['other_specified_dissociative_disorder', 'unspecified_dissociative_disorder']
    };
    const disorders = [];
    flaggedKeys.forEach(slug => (DISORDERS_BY_SUBSCALE[slug] || [])
        .forEach(k => { const d = dissDisorder([k]); if (!disorders.includes(d)) disorders.push(d); }));
    // The overall index also gates the differential when it reaches the
    // "may have dissociative disorder" band (>= 21 on the printed ranges).
    if (index !== null && complete && index >= 21) {
        [dissDisorder(['other_specified_dissociative_disorder']),
         dissDisorder(['unspecified_dissociative_disorder'])].forEach(d => {
            if (!disorders.includes(d)) disorders.push(d);
        });
    }
    disorders.forEach(d => addFlagGlobal(d, 'MID-60'));

    return {
        name: L(scale.name),
        score: index === null ? '—'
            : (index.toFixed(1) + '/100 (' + got.length + '/' + ids.length + ')'),
        severity: band ? L(band.label) : (hi ? 'अपूर्ण' : 'Incomplete'),
        aboveCutoff: index !== null && complete && index >= 21,
        notDiagnostic: true,
        answered: got.length, total: ids.length,
        disorders: disorders,
        pdRegister: {
            kind: 'mid60',
            heading: hi ? 'सूचकांक एवं उप-पैमाना कटऑफ' : 'Index & subscale clinical cutoffs',
            note: (hi
                ? 'सूचकांक = सभी 60 अनुभव-रेटिंग का माध्य × 10 (0-100)। प्रत्येक उप-पैमाना अपना माध्य × 10 है; '
                + 'मुद्रित स्कोर-शीट के नैदानिक कटऑफ से तुलना करें। यह स्क्रीनिंग/तीव्रता माप है — रोग-निर्णायक नहीं: '
                + 'उच्च उप-पैमाना पूर्ण संरचित वियोजीय साक्षात्कार (SCID-5-D / पूर्ण MID) निर्देशित करता है।'
                : 'Index = mean of all 60 experience ratings x 10 (0-100). Each subscale is its own mean x 10, '
                + 'compared with the clinical cutoff printed on the score sheet. Screening/severity measure — '
                + 'not diagnostic: an elevated subscale directs a full structured dissociative interview '
                + '(SCID-5-D / full MID).') +
                (persec.length ? (hi
                    ? ' · चिह्नित उत्पीड़नकारी/क्रोधित आंतरिक आवाज़ें — स्व-क्षति/आत्महत्या जोखिम मूल्यांकन अनिवार्य।'
                    : ' · Endorsed persecutory/angry internal voices — a self-harm and suicide-risk assessment is mandatory.')
                    : ''),
            validity: persec.length ? {
                failed: true,
                message: hi
                    ? 'उत्पीड़नकारी/क्रोधित आंतरिक आवाज़ों का पैमाना-उपर कटऑफ — तत्काल जोखिम-मूल्यांकन एवं निगरानी आवश्यक।'
                    : 'Persecutory/angry intrusion subscale above cutoff — urgent risk assessment and monitoring required.'
            } : null,
            rows: [{
                label: hi ? 'कुल सूचकांक (माध्य × 10)' : 'Total index (mean x 10)',
                value: index === null ? '—' : index.toFixed(1) + '/100',
                flagged: !!(band && (scale.scoreRanges || []).indexOf(band) >= 3),
                detail: band ? rangeLabel(band) : (hi ? 'अपूर्ण' : 'Incomplete')
            }].concat(rows)
        }
    };
}

export { scoreMid60 };
