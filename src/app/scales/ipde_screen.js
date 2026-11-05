import { L } from '../i18n.js';
import { ipdeKeyedHits } from '../scoring/shared.js';
import { state } from '../state.js';

/**
 * IPDE ICD-10 module screening questionnaire scoring.
 * Official standard: >=3 keyed items per disorder fails the screen. The
 * authors explicitly permit a lower standard, which this app applies
 * (>=1 keyed item) so that no cluster needing the full interview is missed.
 * No dimensional score is produced and nothing here is diagnostic.
 */
function scoreIpde(scale, addFlag) {
    const sc = scale.scoring || {};
    const official = sc.failThreshold != null ? sc.failThreshold : 3;
    const applied = sc.positiveThreshold != null ? sc.positiveThreshold : 1;
    const modules = [];
    let flaggedTotal = 0, anyKeyed = 0;
    scale.parts.forEach(part => {
        const hits = ipdeKeyedHits(part, scale.id);
        anyKeyed += hits.length;
        const failed = hits.length >= official;
        const flag = hits.length >= applied;
        if (flag) {
            flaggedTotal++;
            (part.disorders || []).forEach(d => addFlag(d, 'IPDE screen'));
        }
        modules.push({
            id: part.id,
            code: part.icd10Module,
            name: L(part.name),
            disorderName: L(part.disorderName),
            keyed: hits.length,
            totalItems: part.questions.length,
            failedOfficial: failed,
            flagged: flag,
            disorders: part.disorders || []
        });
    });
    const hi = state.lang === 'hi';
    return {
        name: L(scale.name),
        score: anyKeyed + ' keyed item(s) · ' + flaggedTotal + '/' + scale.parts.length +
            ' ' + (hi ? 'मॉड्यूल चिह्नित' : 'modules flagged'),
        severity: flaggedTotal
            ? (hi ? 'स्क्रीन असफल — पूर्ण IPDE साक्षात्कार आवश्यक' : 'Screen failed — full IPDE interview indicated')
            : (hi ? 'चिह्नित नहीं' : 'No module flagged'),
        aboveCutoff: flaggedTotal > 0,
        notDiagnostic: true,
        disorders: [],
        pdRegister: {
            kind: 'ipde',
            heading: hi ? 'IPDE स्क्रीनिंग — मॉड्यूल अनुसार कुंजी-उत्तर' : 'IPDE screen — keyed items by ICD-10 module',
            note: L(sc.appStandard || sc.note || { en: '', hi: '' }),
            rows: modules.map(m => ({
                label: m.name + ' — ' + m.disorderName,
                value: m.keyed + '/' + m.totalItems,
                flagged: m.flagged,
                detail: m.failedOfficial
                    ? (hi ? 'औपचारिक मानदंड (≥3) असफल' : 'Meets official ≥3 fail criterion')
                    : (m.flagged ? (hi ? 'निम्नतर मानदंड से चिह्नित' : 'Flagged under the app\u2019s lower standard') : '')
            }))
        }
    };
}

export { scoreIpde };
