import { score as scoreDisability } from './scales/mini_disability.js';
import { score as scoreCrossCutting } from './scales/mini_cross_cutting.js';
import { scoreDomain } from './scoring/domain-registry.js';

import { scoreBiss } from './scales/biss.js';
import { scoreCas } from './scales/clinical_anger_scale.js';
import { scoreDesII } from './scales/desii.js';
import { scoreFac22 } from './scales/fac22_sr.js';
import { scoreGcls } from './scales/gcls.js';
import { scoreIpde } from './scales/ipde_screen.js';
import { scoreMid60 } from './scales/mid60.js';
import { scorePdq4 } from './scales/pdq4_screen.js';
import { scorePhq15 } from './scales/phq15.js';
import { scoreStaxi } from './scales/staxi_ca.js';
import { scoreVadrs } from './scales/vadrs.js';
import { deployedScreenInstruments } from './scoring/shared.js';
import { selectedDomainForms, state, CLINICAL_DATA, setFlagSink } from './state.js';

function computeResults() {
    const instrumentResults = [];
    const flaggedDisorders = new Map(); // disorderKey -> {sources:Set, bestScore}

    const addFlag = (dkey, source) => {
        if (!CLINICAL_DATA.disorders[dkey]) return;
        if (!flaggedDisorders.has(dkey)) flaggedDisorders.set(dkey, { sources: new Set() });
        flaggedDisorders.get(dkey).sources.add(source);
    };
    // Standalone scorers (MID-60 / DES-II) raise flags through this sink.
    setFlagSink(addFlag);

    selectedDomainForms().forEach(domain => {

        // Deployed VADRS matrix (pediatric ADHD routing)
        if (domain.instrument === 'auto:adhd' && ['pediatric', 'adolescent'].includes(state.context.ageGroup)) {
            instrumentResults.push(scoreVadrs(addFlag));
            return;
        }

        // Clinician-rated severity tables (MINI optional assessments A/B): the
        // printed form records one 0-10 rating per row and derives no total, so
        // these are reported as a rating register rather than a cutoff score.
        if (domain.instrument === 'auto:minioptional') {
            domain.questions.forEach(q => {
                if (!q.scaleId) return;
                if ((state.responses[domain.id + ':' + q.id] || 0) < 1) return;
                const s = CLINICAL_DATA.scales[q.scaleId];
                if (!s) return;
                instrumentResults.push((s.id === 'mini_disability' ? scoreDisability : scoreCrossCutting)(s));
            });
            return;
        }

        // Keyed True/False personality screens (IPDE ICD-10 module screen, PDQ-4+).
        // Neither instrument yields a dimensional score: they flag which cluster or
        // DSM personality disorder needs the full structured interview.
        if (domain.instrument === 'auto:pdscreen') {
            domain.questions.forEach(q => {
                if (!q.scaleId) return;
                if ((state.responses[domain.id + ':' + q.id] || 0) < 1) return;
                const s = CLINICAL_DATA.scales[q.scaleId];
                if (!s || !s.keyedScoring) return;
                if (s.keying === 'ipde') instrumentResults.push(scoreIpde(s, addFlag));
                else instrumentResults.push(scorePdq4(s, addFlag));
            });
            return;
        }

        // Summed anger instruments (STAXI-CA / Clinical Anger Scale): deployed
        // through the domain's own screen-in items. Both are dimensional - they
        // report severity, never a diagnosis - but a positive screen-in item
        // still flags the impulse-control categories.
        if (domain.instrument === 'auto:angertable') {
            if (domain.questions.some(q => (state.responses[domain.id + ':' + q.id] || 0) >= 1)) {
                (domain.questions[0].disorders || []).forEach(d => addFlag(d, 'Anger screen'));
            }
            deployedScreenInstruments(domain, s => !!s.sumScoring).forEach(({ scale }) => {
                instrumentResults.push(scale.keying === 'staxi' || scale.id === 'staxi_ca'
                    ? scoreStaxi(scale) : scoreCas(scale));
            });
            return;
        }

        // Dissociative-experience inventories (MID-60 short form / DES-II):
        // each is attached to one screen-in item of the `dissociation` domain.
        // Both are dimensional severity measures - they flag the dissociative
        // categories for the structured interview but never diagnose.
        if (domain.instrument === 'auto:dissociationtable') {
            if (domain.questions.some(q => (state.responses[domain.id + ':' + q.id] || 0) >= 1)) {
                (domain.questions[0].disorders || []).forEach(d => addFlag(d, 'Dissociation screen'));
            }
            deployedScreenInstruments(domain, () => true).forEach(({ scale }) => {
                instrumentResults.push(scale.id === 'mid60'
                    ? scoreMid60(scale) : scoreDesII(scale));
            });
            return;
        }

        // Somatic-symptom instruments: keyed Yes/No factitious screen (FAC22-SR)
        // plus the summed PHQ-15 somatic severity index. Neither diagnoses; both
        // flag the somatic-symptom / factitious categories for clinical review.
        if (domain.instrument === 'auto:somatoptable') {
            if (domain.questions.some(q => (state.responses[domain.id + ':' + q.id] || 0) >= 1)) {
                (domain.questions[0].disorders || []).forEach(d => addFlag(d, 'Somatic screen'));
            }
            deployedScreenInstruments(domain, () => true).forEach(({ scale }) => {
                if (scale.keyedScoring) instrumentResults.push(scoreFac22(scale, addFlag));
                else instrumentResults.push(scorePhq15(scale));
            });
            return;
        }

        // Gender-related distress (GCLS): one reverse-keyed, subscale-scored
        // self-report attached to both screen-in items of the `gender` domain.
        // Descriptive only - it never diagnoses gender incongruence/dysphoria,
        // and gender diversity on its own is not a mental disorder.
        if (domain.instrument === 'auto:genderdistress') {
            deployedScreenInstruments(domain, () => true).forEach(({ scale }) => {
                instrumentResults.push(scoreGcls(scale));
            });
            return;
        }

        // Bipolar signs & symptoms (BISS) on the mood domain: the nine PHQ-9
        // items keep their usual raw-sum scoring, and every BISS attached to an
        // endorsed screen-in item is scored as a dimensional severity profile.
        if (domain.instrument === 'auto:bipolartable' && domain.baseInstrument) {
            // Same always-deployed rule as the other optional tables: the BISS
            // appears on screen as soon as the mood domain is selected, so it
            // must be scored regardless of how its screen-in items were answered.
            deployedScreenInstruments(domain, () => true).forEach(({ scale }) => {
                if (scale.id === 'biss') instrumentResults.push(scoreBiss(scale, addFlag));
            });
            // fall through to the generic raw-sum block below for the PHQ-9 items
        }

        instrumentResults.push(scoreDomain(domain, addFlag));
    });

    // Build tiered differential considerations from the harmonized database
    const differentials = [];
    flaggedDisorders.forEach((meta, key) => {
        const d = CLINICAL_DATA.disorders[key];
        differentials.push({ key, ...d, tier: d.tier, sources: [...meta.sources] });
    });
    differentials.sort((a, b) => a.tier - b.tier);

    state.results = { instrumentResults, differentials, safetyTriggered: state.safetyFlags.length > 0 };
    return state.results;
}

export { computeResults };
