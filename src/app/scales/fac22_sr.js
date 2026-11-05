import { L } from '../i18n.js';
import { keyedHitsOfParts } from '../scoring/shared.js';
import { state, CLINICAL_DATA } from '../state.js';

/**
 * FAC22-SR (Senthil & Prabhakar, 2019) — factitious disorder self-report
 * screen. Keying as printed: Yes to items 5, 8, 10-22 and No to items 1-4,
 * 6, 7, 9, 12, 13. Bands: 9-14 possible factitious disorder, 15+ probable.
 * A screen only — it must never be used to diagnose factitious disorder,
 * which requires excluding deception for external gain and medical
 * malingering, so a positive result flags the category for clinical review.
 */
function scoreFac22(scale, addFlag) {
    const hi = state.lang === 'hi';
    const ids = [];
    (scale.parts || []).forEach(part => (part.questions || []).forEach(q => ids.push(q.id)));
    const got = ids.filter(id => state.responses[scale.id + ':' + id] !== undefined);
    const complete = got.length === ids.length;
    const keyed = keyedHitsOfParts(scale);
    const sc = scale.scoring || {};
    const probableAt = sc.probableThreshold != null ? sc.probableThreshold : 15;
    const possibleAt = sc.possibleThreshold != null ? sc.possibleThreshold : 9;
    const level = keyed.length >= probableAt ? 2 : (keyed.length >= possibleAt ? 1 : 0);
    if (complete && level > 0) {
        (sc.disorders || scale.disorders ||
            ['factitious_disorder', 'somatic_symptom_disorder']).forEach(d => {
                const key = CLINICAL_DATA.disorders[d] ? d : null;
                if (key) addFlag(key, 'FAC22-SR');
            });
    }
    return {
        name: L(scale.name),
        score: keyed.length + ' (' + got.length + '/' + ids.length + ')',
        severity: level === 2
            ? (hi ? 'संभावित भत्रुण रोग — पूर्ण मूल्यांकन आवश्यक' : 'Probable factitious disorder — full evaluation indicated')
            : level === 1
                ? (hi ? 'संभव भत्रुण रोग — पूर्ण मूल्यांकन आवश्यक' : 'Possible factitious disorder — full evaluation indicated')
                : (hi ? 'स्क्रीन नेगेटिव' : 'Screen negative'),
        aboveCutoff: complete && level > 0,
        notDiagnostic: true,
        answered: got.length, total: ids.length,
        disorders: [],
        pdRegister: {
            kind: 'fac22',
            heading: hi ? 'FAC22-SR कुंजी-अंक' : 'FAC22-SR keyed score',
            note: L(sc.rule || { en: '', hi: '' }),
            rows: [{
                label: hi ? 'कुंजीकृत उत्तर (Yes 5,8,10-22 · No 1-4,6,7,9,12,13)' : 'Keyed responses (Yes 5,8,10-22 · No 1-4,6,7,9,12,13)',
                value: keyed.length + '/22',
                flagged: level > 0,
                detail: hi
                    ? possibleAt + '-' + (probableAt - 1) + ' संभव · ' + probableAt + '+ संभावित'
                    : possibleAt + '-' + (probableAt - 1) + ' possible · ' + probableAt + '+ probable'
            }]
        }
    };
}

export { scoreFac22 };
