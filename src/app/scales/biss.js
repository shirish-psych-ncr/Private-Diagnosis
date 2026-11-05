import { allAnswered } from '../completion.js';
import { t, L } from '../i18n.js';
import { state, CLINICAL_DATA } from '../state.js';

/**
 * BISS (Bipolar Inventory of Signs and Symptoms Scale, Bowden v1.5) scoring.
 * 44 clinician-rated items scored 0-4 over the most recent 7 days from
 * self-report plus family and interview observation. Section I Depression is
 * items 1-20 (0-80) and section II Mania is items 21-44 (0-96); an item counts
 * as symptomatic at >= 2 (mild or worse). The printed instrument derives no
 * diagnostic decision rule, so nothing here converts a total into a bipolar
 * diagnosis: the differential categories are flagged only when the domain's
 * own screen-in item is endorsed, exactly as for the other optional tables.
 */
function scoreBiss(scale, addFlag) {
    const hi = state.lang === 'hi';
    const ans = id => state.responses[scale.id + ':' + id];
    const sections = Object.keys((scale.scoring || {}).sections || {});
    const posV = (scale.scoring || {}).positiveItemValue || 2;
    const rows = [];
    let allAnswered = true;
    sections.forEach(slug => {
        const sec = scale.scoring.sections[slug];
        const values = sec.ids.map(ans);
        const answered = values.filter(v => v !== undefined);
        if (answered.length !== sec.ids.length) allAnswered = false;
        const sum = answered.reduce((t, v) => t + Number(v), 0);
        const done = answered.length === sec.ids.length;
        const bandLabelFor = s => {
            if (s === 0) return hi ? 'अनुपस्थित' : 'Absent';
            if (s <= 10) return hi ? 'हल्का-मंद' : 'Slight-mild';
            if (s <= 25) return hi ? 'मध्यम' : 'Moderate';
            return hi ? 'गंभीर' : 'Severe';
        };
        rows.push({
            label: slug === 'depression'
                ? (hi ? 'I. अवसाद (आइटम 1-20)' : 'I. Depression (items 1-20)')
                : (hi ? 'II. उन्माद (आइटम 21-44)' : 'II. Mania (items 21-44)'),
            value: done ? (sum + '/' + sec.maxTotal)
                        : (hi ? 'अपूर्ण (' + answered.length + '/' + sec.count + ')'
                              : 'Incomplete (' + answered.length + '/' + sec.count + ')'),
            flagged: done && sum > 0,
            detail: done ? (bandLabelFor(sum) + ' · ' +
                answered.filter(v => Number(v) >= posV).length + ' ≥ mild' +
                (slug === 'mania' ? '' : ' · ' +
                    answered.filter(v => Number(v) === 1).length + ' slight')) : ''
        });
    });

    // Safety register: suicidality (item 4) at any rating, plus aggression
    // (25), risky behaviour (39) and hallucinations (43) at mild or worse.
    const safetyHits = (scale.safetyItems || []).filter(id => {
        const v = ans(id);
        if (v === undefined) return false;
        return id === 'biss_4' ? Number(v) >= 1 : Number(v) >= posV;
    });
    const itemName = id => {
        const q = (scale.parts || []).flatMap(p => p.questions || [])
            .find(x => x.id === id);
        return q ? L(q.itemName || q.text) : id;
    };

    const depSum = sections.indexOf('depression') >= 0
        ? scale.scoring.sections.depression.ids.map(ans)
            .filter(v => v !== undefined).reduce((t, v) => t + Number(v), 0) : 0;
    const manSum = sections.indexOf('mania') >= 0
        ? scale.scoring.sections.mania.ids.map(ans)
            .filter(v => v !== undefined).reduce((t, v) => t + Number(v), 0) : 0;

    const disorders = [];
    if (allAnswered) {
        // Screen-in endorsement decides which bipolar categories need the
        // structured interview; the BISS itself only grades severity.
        (scale.disorderKeys || []).forEach(k => {
            if (!CLINICAL_DATA.disorders[k]) return;
            const elevated = k === 'bipolar_depressive' ? depSum : manSum;
            if (elevated > 0) disorders.push(k);
        });
        disorders.forEach(d => addFlag(d, 'BISS'));
    }

    return {
        name: L(scale.name),
        score: allAnswered
            ? (hi ? 'अवसाद ' + depSum + '/80 · उन्माद ' + manSum + '/96'
                  : 'Depression ' + depSum + '/80 · Mania ' + manSum + '/96')
            : ((scale.scoring.sections.depression.ids.concat(
                    scale.scoring.sections.mania.ids)
                    .filter(id => ans(id) !== undefined)).length + '/44 ' +
                (hi ? 'रेटित' : 'rated')),
        severity: allAnswered
            ? (hi ? 'विमात्मक तीव्रता — रोग-निर्णायक नहीं'
                  : 'Dimensional severity — not diagnostic')
            : (hi ? 'अपूर्ण' : 'Incomplete'),
        aboveCutoff: false,
        notDiagnostic: true,
        answered: scale.scoring.sections.depression.ids.concat(
                    scale.scoring.sections.mania.ids).filter(id => ans(id) !== undefined).length,
        total: 44,
        disorders: disorders,
        pdRegister: {
            kind: 'biss',
            heading: hi ? 'विभाग-वार तीव्रता (7 दिन)' : 'Section severity (past 7 days)',
            note: L((scale.scoring || {}).interpretationNote || { en: '', hi: '' }) +
                (safetyHits.length ? (hi
                    ? ' · सुरक्षा-चिह्न: ' + safetyHits.map(itemName).join(', ') +
                      ' — तत्काल जोखिम-मूल्यांकन आवश्यक।'
                    : ' · Safety flags: ' + safetyHits.map(itemName).join(', ') +
                      ' — an immediate risk assessment is required.')
                    : ''),
            rows: rows
        },
        bissSafety: safetyHits.map(itemName)
    };
}

export { scoreBiss };
