import { score as phq9 } from '../scales/phq9.js';
import { score as gad7 } from '../scales/gad7.js';
import { score as pcl5 } from '../scales/pcl5.js';
import { score as isi } from '../scales/isi.js';
import { score as auditc } from '../scales/auditc.js';
import { score as asrs } from '../scales/asrs.js';
import { score as caarms } from '../scales/caarms.js';
import { scoreRawSum } from './raw-sum.js';

const scorers = {
    mood: phq9,
    anxiety: gad7,
    trauma: pcl5,
    sleep: isi,
    substance: auditc,
    neurodevelopmental: asrs,
    psychosis: caarms
};
export function scoreDomain(domain, addFlag) {
    return (scorers[domain.id] || scoreRawSum)(domain, addFlag);
}
