
import { t, L } from '../i18n.js';
import { genderDisorder } from '../scoring/shared.js';
import { state, addFlagGlobal } from '../state.js';

/* ------------------------------------------------------------------ *
 * 7f. Gender-related distress (GCLS)                                   *
 * ------------------------------------------------------------------ */

/**
 * GCLS scoring. Items are rated Never=0 ... Always=4 over the past six
 * months. The positively worded congruence items (16, 20, 22, 25, 30) and
 * the negatively worded satisfaction items (35, 37) are reverse-scored as
 * (scaleMax - response) before summing, exactly as printed in the scale's
 * scoring rule. Three distress subscales (functional impact, body
 * preoccupation, social preoccupation) rise with distress; life
 * satisfaction is reported separately and rises with satisfaction. There
 * are no published cutoffs, so nothing here diagnoses gender incongruence
 * or dysphoria — it describes distress, functioning and satisfaction and
 * supports follow-up measurement. The non-scored surgery tick-box is
 * reported as a clinical note only.
 */
function scoreGcls(scale) {
    const hi = state.lang === 'hi';
    const maxV = ((scale.ratingScale || {}).max != null ? scale.ratingScale.max : 4);
    const ans = id => state.responses[scale.id + ':' + id];
    const ids = [];
    (scale.parts || []).forEach(part => (part.questions || []).forEach(q => {
        if (!q.nonScored) ids.push({ id: q.id, num: q.itemNumber, rev: !!q.reverseScored });
    }));
    const got = ids.filter(i => ans(i.id) !== undefined);
    const complete = got.length === ids.length;
    const valueOf = i => {
        const v = Number(ans(i.id));
        return i.rev ? maxV - v : v;
    };

    // item number -> scored entry, for subscale lookup
    const byNum = {};
    ids.forEach(i => { byNum[i.num] = i; });

    const rows = [];
    Object.keys(scale.subscales || {}).forEach(slug => {
        const sub = scale.subscales[slug];
        const entries = (sub.items || []).map(n => byNum[n]).filter(Boolean);
        const answered = entries.filter(i => ans(i.id) !== undefined);
        const sum = answered.reduce((t, i) => t + valueOf(i), 0);
        const done = answered.length === entries.length;
        rows.push({
            label: L(sub),
            value: done ? (sum + '/' + (sub.maxTotal != null ? sub.maxTotal : entries.length * maxV))
                        : (hi ? 'अपूर्ण (' + answered.length + '/' + entries.length + ')'
                              : 'Incomplete (' + answered.length + '/' + entries.length + ')'),
            flagged: false,
            detail: slug === 'life_satisfaction'
                ? (hi ? 'उच्च = अधिक जीवन-संतुष्टि (पृथक् रिपोर्ट)' : 'Higher = MORE life satisfaction (reported separately)')
                : (hi ? 'उच्च = अधिक लिंग-संबंधी कष्ट' : 'Higher = more gender-related distress')
        });
    });

    const distressSlugs = ['functional_impact', 'body_preoccupation', 'social_preoccupation'];
    const distressSum = distressSlugs.reduce((t, slug) => {
        const sub = (scale.subscales || {})[slug] || {};
        return t + (sub.items || []).map(n => byNum[n]).filter(Boolean)
            .filter(i => ans(i.id) !== undefined).reduce((a, i) => a + valueOf(i), 0);
    }, 0);
    const satEntry = (scale.subscales.life_satisfaction || {}).items || [];
    const satSum = satEntry.map(n => byNum[n]).filter(Boolean)
        .filter(i => ans(i.id) !== undefined).reduce((a, i) => a + valueOf(i), 0);

    // Safety: items 8 (chest/genital self-harm) and 13 (suicidal thoughts).
    const safetyItems = ids.filter(i => {
        const q = (scale.parts || []).flatMap(pt => pt.questions || [])
            .find(x => x.itemNumber === i.num);
        return q && q.safety;
    });
    const riskEndorsed = safetyItems.filter(i => ans(i.id) !== undefined && Number(ans(i.id)) > 0);

    const disorders = [];
    if (complete && distressSum > 0) {
        const d = genderDisorder();
        if (d) { disorders.push(d); addFlagGlobal(d, 'GCLS'); }
    }

    const tick = (scale.parts || []).flatMap(pt => pt.questions || [])
        .find(q => q.nonScored && q.tickBox);
    const ticked = tick ? !!ans(tick.id) : false;

    return {
        name: L(scale.name),
        score: complete
            ? (hi ? 'कष्ट उप-पैमाने योग ' + distressSum + ' · संतुष्टि ' + satSum
                  : 'Distress subscale sum ' + distressSum + ' · Satisfaction ' + satSum)
            : (got.length + '/' + ids.length + ' ' + (hi ? 'उत्तर' : 'answered')),
        severity: complete
            ? (hi ? 'वर्णनात्मक — रोग-निर्णायक नहीं' : 'Descriptive — not diagnostic')
            : (hi ? 'अपूर्ण' : 'Incomplete'),
        aboveCutoff: false,
        notDiagnostic: true,
        answered: got.length, total: ids.length,
        disorders: disorders,
        pdRegister: {
            kind: 'gcls',
            heading: hi ? 'उप-पैमाना अंक (व्युक्रम-अंकित)' : 'Subscale scores (reverse-keyed)',
            note: (hi
                ? 'आइटम 16, 20, 22, 25, 30 (संगति) तथा 35, 37 (नकारात्मक संतुष्टि) को व्युक्रम कर (4 − उत्तर) उप-पैमाना योग निकाले जाते हैं। '
                + 'कष्ट उप-पैमाने उच्च होने पर अधिक कष्ट; जीवन-संतुष्टि पृथक् रिपोर्ट (उच्च = अधिक संतुष्टि)। '
                + 'GCLS का कोई नैदानिक कटअफ नहीं — यह कष्ट एवं कार्य-क्षमता वर्णित करता है।'
                : 'Congruence items 16/20/22/25/30 and negative satisfaction items 35/37 are reverse-scored (4 minus response) before summing. '
                + 'Higher distress subscales mean more gender-related distress; life satisfaction is reported separately (higher = more satisfied). '
                + 'The GCLS has no diagnostic cutoffs: it describes distress and functioning and supports outcome monitoring.')
                + (riskEndorsed.length ? (hi
                    ? ' · आइटम 8/13 पर स्व-क्षति/आत्महत्या विचार — जोखिम-मूल्यांकन अनिवार्य।'
                    : ' · Item 8/13 endorsed chest/genital self-harm or suicidal thoughts — a risk assessment is mandatory.')
                    : '')
                + (ticked ? (hi ? ' · रोगी ने जननांग-शस्त्रक्रिया पहले होना चिह्नित किया (आइटम 26 सावधानी से व्याख्या करें)।'
                                : ' · Respondent ticked prior genital surgery — interpret item 26 accordingly.')
                           : ''),
            rows: rows
        }
    };
}

export { scoreGcls };
