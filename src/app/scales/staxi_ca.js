
import { t, L } from '../i18n.js';
import { state } from '../state.js';

/**
 * STAXI-CA scoring: raw sums for State Anger (items 1-15), Trait Anger
 * (16-24) and each Part-3 subscale, plus the composite Expression score
 * (Anger-In + Anger-Out + Control-Out reversed). The instrument is purely
 * dimensional - there is no caseness cutoff - so nothing here raises a
 * differential flag; the flagged-disorder list for the anger domain comes
 * from the screen-in items themselves.
 */
function scoreStaxi(scale) {
    const hi = state.lang === 'hi';
    const ans = id => state.responses[scale.id + ':' + id];
    const slugs = Object.keys(scale.subscales);
    // Item-level totals come from the printed parts, not from the subscale
    // lists: item 25 is scored on Part 3 but belongs to no expression
    // subscale, so counting subscale items would over-report completion.
    const allIds = [];
    (scale.parts || []).forEach(part => part.questions.forEach(q => allIds.push(q.id)));
    const answeredOf = ids => ids.filter(id => ans(id) !== undefined);
    const sumOf = ids => answeredOf(ids).reduce((t, id) => t + Number(ans(id)), 0);
    const rows = [];
    slugs.forEach(slug => {
        const sub = scale.subscales[slug];
        const ids = sub.items.map(n => 'staxi_' + n);
        const got = answeredOf(ids);
        const raw = sumOf(ids);
        const lo = ids.length * (scale.scoring.scaleMin || 1);
        const up = ids.length * (scale.scoring.scaleMax || 4);
        rows.push({
            label: L(sub.name),
            value: got.length === ids.length ? (raw + '/' + up) : (raw + ' (' + got.length + '/' + ids.length + ')'),
            flagged: false,
            detail: (hi ? 'सीमा ' : 'range ') + lo + '-' + up +
                (slug === 'control' ? (hi ? ' · उच्च = बेहतर नियंत्रण' : ' · higher = better control') : '') +
                (slug === 'denial' ? (hi ? ' · व्याख्या सावधानी से करें' : ' · interpret with caution') : '')
        });
    });
    // Composite Expression = Anger-In + Anger-Out + reversed Anger Control,
    // where each control item is reversed as (scaleMax + scaleMin - response).
    const mn = scale.scoring.scaleMin || 1, mx = scale.scoring.scaleMax || 4;
    const completePart = slug => scale.subscales[slug].items
        .every(n => ans('staxi_' + n) !== undefined);
    const controlReversed = scale.subscales.control.items
        .map(n => ans('staxi_' + n))
        .filter(v => v !== undefined)
        .reduce((t, v) => t + (mx + mn - Number(v)), 0);
    const exprComplete = ['in', 'out', 'control'].every(completePart);
    const expr = exprComplete
        ? (sumOf(scale.subscales.in.items.map(n => 'staxi_' + n)) +
           sumOf(scale.subscales.out.items.map(n => 'staxi_' + n)) + controlReversed)
        : null;
    const answered = answeredOf(allIds).length;
    const complete = answered === allIds.length;
    if (exprComplete) {
        rows.push({
            label: hi ? 'क्रोध-अभिव्यक्ति संयुक्त स्कोर (AES)' : 'Anger Expression Summary (AES)',
            value: String(expr),
            flagged: false,
            detail: hi
                ? 'Anger-In + Anger-Out + (5 − प्रत्येक Control आइटम)'
                : 'Anger-In + Anger-Out + reversed Anger Control (per item: max+min − response)'
        });
    }
    return {
        name: L(scale.name),
        score: answered + '/' + allIds.length + ' ' + (hi ? 'आइटम उत्तरित' : 'items answered'),
        severity: complete
            ? (hi ? 'पूर्ण — आयामगत स्कोर (रोग-निर्णायक नहीं)' : 'Complete — dimensional scores (not diagnostic)')
            : (hi ? 'अपूर्ण' : 'Incomplete'),
        aboveCutoff: false,
        notDiagnostic: true,
        answered, total: allIds.length,
        disorders: [],
        pdRegister: {
            kind: 'staxi',
            heading: hi ? 'STAXi-CA उप-पैमाना प्रोफ़ाइल' : 'STAXI-CA subscale profile',
            note: L((scale.scoring.rule || {}).en ? scale.scoring.rule : { en: '', hi: '' }),
            rows: rows
        }
    };
}

export { scoreStaxi };
