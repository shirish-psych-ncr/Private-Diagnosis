import { t } from '../i18n.js';
import { state, CLINICAL_DATA } from '../state.js';

function scoreVadrs(addFlag) {
            const vadrs = CLINICAL_DATA.scales.vadrs;
            const sc = vadrs.scoring;
            const count = (ids, min) => ids.filter(id => (state.responses['vadrs:' + id] || 0) >= min).length;
            const sum = (ids) => ids.reduce((t, id) => t + (state.responses['vadrs:' + id] || 0), 0);
            const inat = count(sc.inattention.ids, sc.inattention.minSymptomValue);
            const hyp = count(sc.hyperactivity.ids, sc.hyperactivity.minSymptomValue);
            const odd = count(sc.oppositionalDefiant.ids, sc.oppositionalDefiant.minSymptomValue);
            const cond = count(sc.conduct.ids, sc.conduct.minSymptomValue);
            const anxdep = count(sc.anxietyDepression.ids, sc.anxietyDepression.minSymptomValue);
            const perfImpaired = count(sc.performance.ids, sc.performance.minImpairedValue);
            const totalSymptomScore = sum(sc.inattention.ids.concat(sc.hyperactivity.ids));
            const perfValues = sc.performance.ids.map(id => state.responses['vadrs:' + id]).filter(v => v !== undefined);
            const avgPerf = perfValues.length ? (perfValues.reduce((a, b) => a + b, 0) / perfValues.length) : null;
            const impairedGate = perfImpaired >= sc.performance.requiresImpairedCount;

            const positive = (inat >= sc.inattention.thresholdCount || hyp >= sc.hyperactivity.thresholdCount) && impairedGate;
            if (positive) sc.disordersOnPositive.forEach(d => addFlag(d, 'VADRS'));
            if (odd >= sc.oppositionalDefiant.thresholdCount && impairedGate)
                (sc.oppositionalDefiant.disordersOnPositive || []).forEach(d => addFlag(d, 'VADRS'));
            if (cond >= sc.conduct.thresholdCount && impairedGate)
                (sc.conduct.disordersOnPositive || []).forEach(d => addFlag(d, 'VADRS'));

            return {
                name: 'VADRS',
                score: 'IA ' + inat + '/' + sc.inattention.ids.length +
                       ' · HI ' + hyp + '/' + sc.hyperactivity.ids.length +
                       ' · ODD ' + odd + '/' + sc.oppositionalDefiant.ids.length +
                       ' · CD ' + cond + '/' + sc.conduct.ids.length +
                       ' · Anx/Dep ' + anxdep + '/' + sc.anxietyDepression.ids.length +
                       ' · Perf ' + perfImpaired + '/' + sc.performance.ids.length +
                       ' | Total symptom score 1–18: ' + totalSymptomScore +
                       (avgPerf !== null ? ' | Avg performance: ' + avgPerf.toFixed(2) : ''),
                severity: positive ? (state.lang === 'hi' ? 'सकारात्मक स्क्रीन' : 'Positive screen') : (state.lang === 'hi' ? 'ऋणात्मक' : 'Negative'),
                disorders: positive ? sc.disordersOnPositive : []
            };
}

export { scoreVadrs };
