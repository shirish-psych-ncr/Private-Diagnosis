import { scoreItemSums } from './scoring/item-sums.js';
import { L } from './i18n.js';
import { score as scoreDisability } from './scales/mini_disability.js';
import { score as scoreCrossCutting } from './scales/mini_cross_cutting.js';
import { scoreDomain } from './scoring/domain-registry.js';
import { OPTIONAL_TABLE_ROUTES } from './routing.js';

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
import { selectedDomainForms, selectedFormsForDomain, state, CLINICAL_DATA, setFlagSink, questionIsApplicable } from './state.js';

import { score as scoreUGDS } from './scales/ugds_gs.js';
import { score as scoreITQ } from './scales/itq.js';
import { score as scoreRyff } from './scales/ryff.js';
import { score as scoreMAAS } from './scales/maas.js';
import { score as scoreCSSRS } from './scales/cssrs.js';
import { score as scoreMiniScreen5 } from './scales/mini_screen_5.js';
import { score as scoreLec5 } from './scales/lec5.js';
import { score as scoreSiRModified } from './scales/si_r_modified.js';
import { score as scoreMghHairpulling } from './scales/mgh_hairpulling.js';
import { score as scoreWhodas36 } from './scales/whodas_36.js';
import { score as scoreWhiteley } from './scales/whiteley_index.js';
import { score as scoreAceIIIIndianEnglish } from './scales/ace_iii_indian_english.js';
import { score as scoreCtqEcho } from './scales/ctq_echo.js';

import { score as scoreQids } from './scales/qids_sr16.js';
import { score as scoreMoodMdq } from './scales/mood_mdq.js';
import { score as scoreK10 } from './scales/k10.js';
import { scoreRating } from './scales/rating_sum.js';
import { score as scorePdssSr } from './scales/pdss_sr.js';
import { score as scoreHads } from './scales/hads.js';
import { score as scoreLsas } from './scales/lsas.js';
import { score as scoreMia } from './scales/mia.js';
import { score as scoreIesR } from './scales/ies_r.js';
import { score as scorePanss } from './scales/panss.js';
import { score as scoreOciR } from './scales/oci_r.js';
import { score as scoreEdeq } from './scales/edeq.js';
import { score as scoreCaps5 } from './scales/caps5.js';
import { score as scoreScid5PdSummary } from './scales/scid5pd_summary.js';
import { score as scorePsqi } from './scales/psqi.js';
import { score as scoreBprs24 } from './scales/bprs24.js';
import { score as scoreBars } from './scales/bars.js';
import { score as scoreCows } from './scales/cows.js';
import { score as scorePid5Bf } from './scales/pid5_bf.js';
import { score as scoreYbocs2 } from './scales/ybocs2.js';
import { score as scoreCybocs } from './scales/cybocs.js';
import { score as scoreBddYbocs } from './scales/bdd_ybocs.js';
import { score as scoreCiwaAr } from './scales/ciwa_ar.js';
import { scoreCambridge } from './scales/cambridge_dep.js';
import { scoreMeans } from './scoring/item-means.js';
import { scoreSuppliedProfile } from './scales/supplied-profile.js';
import { scoreHexacoObserver } from './scales/hexaco_observer.js';

const directScorers = { qids_sr16: scoreQids, mood_mdq: scoreMoodMdq, ugds_gs: scoreUGDS, itq: scoreITQ, ryff: scoreRyff, maas: scoreMAAS, cssrs: scoreCSSRS, mini_screen_5: scoreMiniScreen5, lec5: scoreLec5, si_r_modified: scoreSiRModified, mgh_hairpulling: scoreMghHairpulling, whodas_36: scoreWhodas36, whiteley_index: scoreWhiteley, ace_iii_indian_english: scoreAceIIIIndianEnglish, ctq_echo: scoreCtqEcho, k10: scoreK10,
    hexaco_pi_r_observer: (_values, _questions, form) => scoreHexacoObserver(form),
    desii: (_values, _questions, form) => [scoreDesII(form)],
    mid60: (_values, _questions, form) => [scoreMid60(form)],
    hdrs17: (values, questions) => scoreRating(values, questions, CLINICAL_DATA.scales.hdrs17),
    madrs: (values, questions) => scoreRating(values, questions, CLINICAL_DATA.scales.madrs),
    ymrs: (values, questions) => scoreRating(values, questions, CLINICAL_DATA.scales.ymrs),
    bdrs: (values, questions) => scoreRating(values, questions, CLINICAL_DATA.scales.bdrs),
    bdi_ii: (values, questions) => scoreRating(values, questions, CLINICAL_DATA.scales.bdi_ii),
    hama: (values, questions) => scoreRating(values, questions, CLINICAL_DATA.scales.hama),
    pswq: (values, questions) => scoreRating(values, questions, CLINICAL_DATA.scales.pswq),
    bai: (values, questions) => scoreRating(values, questions, CLINICAL_DATA.scales.bai),
    pdss_sr: scorePdssSr,
    bfne: (values, questions) => scoreRating(values, questions, CLINICAL_DATA.scales.bfne),
    hads: scoreHads,
    lsas: scoreLsas,
    mia: scoreMia,
    ies_r: scoreIesR,
    asds: (values, questions) => scoreRating(values, questions, CLINICAL_DATA.scales.asds),
    panss: scorePanss, oci_r: scoreOciR, edeq: scoreEdeq, caps5: scoreCaps5,
    scid5pd_summary: scoreScid5PdSummary, psqi: scorePsqi,
    bprs24: scoreBprs24, bars: scoreBars,
    panss6: (values, questions, form) => scoreRating(values, questions, form), cows: scoreCows,
    pid5_bf: scorePid5Bf, ybocs2: scoreYbocs2, cybocs: scoreCybocs,
    cois_rc: (values, questions, form) => scoreRating(values, questions, form), bdd_ybocs: scoreBddYbocs,
    ciwa_ar: scoreCiwaAr,
    cambridge_dep: (_values, _questions, form) => scoreCambridge(form, state) };

function appendFormResults(id, instrumentResults) {
    const form = CLINICAL_DATA.scales[id];
    if (!form) return;
    const appendContext = () => {
        for (const field of form.contextFields || []) {
            const value = state.formContext[id + ':' + field.id];
            if (Array.isArray(value) ? !value.length : value == null || value === '') continue;
            instrumentResults.push({ name: L(field.label) || L(form.name),
                score: Array.isArray(value) ? value.join(', ') : value,
                severity: 'Context information', sourceNote: form.interpretationNote || form.attribution });
        }
    };
    const questions = form.parts.flatMap(part => part.questions)
        .filter(q => questionIsApplicable(q, id) && !q.nonScored && !q.tickBox);
    const values = questions.map(q => state.responses[id + ':' + q.id]);
    if (!values.length || !values.every(value => Number.isFinite(value) || Array.isArray(value))) {
        appendContext();
        return;
    }
    let rows;
    if (directScorers[id]) rows = directScorers[id](values, questions, form);
    else if (form.sumScores) rows = scoreItemSums(values, form);
    else if (form.meanScores) rows = scoreMeans(values, form);
    else if (form.scoringProfile) rows = scoreSuppliedProfile(form);
    else rows = [];
    if (form.attribution) rows.forEach(row => { row.sourceNote = form.attribution; });
    instrumentResults.push(...rows);
    appendContext();
}

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
        if (domain.selectedForms?.includes('base') && (domain.baseInstrument || domain.originalLabel) && !domain.forms?.length && domain.instrument !== 'auto:bipolartable') {
            const questions = domain.questions.filter(q => !q.scaleId);
            const values = questions.map(q => state.responses[domain.id + ':' + q.id]);
            if (values.every(Number.isFinite)) instrumentResults.push(...scoreDomain({ ...domain, questions }, addFlag));
        }
        if (domain.directForm) {
            appendFormResults(domain.id, instrumentResults);
            return;
        }

        if (domain.forms?.length) {
            const chosen = domain.selectedForms || [];
            if (domain.instrument === 'auto:adhd') {
                const peds = ['pediatric', 'schoolage', 'adolescent'].includes(state.context.ageGroup);
                if (chosen.includes('base')) {
                    if (peds) instrumentResults.push(scoreVadrs(addFlag));
                    else {
                        const baseQuestions = domain.questions.filter(q => !q.scaleId);
                        if (baseQuestions.length && baseQuestions.every(q => Number.isFinite(state.responses[domain.id + ':' + q.id])))
                            instrumentResults.push(...scoreDomain({ ...domain, questions: baseQuestions }, addFlag));
                    }
                }
                chosen.filter(id => domain.forms.includes(id)).forEach(id => appendFormResults(id, instrumentResults));
                return;
            }
            if ((domain.baseInstrument || domain.originalLabel) && chosen.includes('base') && !OPTIONAL_TABLE_ROUTES.includes(domain.instrument)) {
                const baseQuestions = domain.questions.filter(q => !q.scaleId);
                if (baseQuestions.length && baseQuestions.every(q => Number.isFinite(state.responses[domain.id + ':' + q.id])))
                    instrumentResults.push(...scoreDomain({ ...domain, questions: baseQuestions }, addFlag));
            }
            chosen.filter(id => domain.forms.includes(id)).forEach(id => appendFormResults(id, instrumentResults));
            if (!OPTIONAL_TABLE_ROUTES.includes(domain.instrument)) {
                chosen.filter(id => !domain.forms.includes(id) && domain.questions.some(q => q.scaleId === id))
                    .forEach(id => appendFormResults(id, instrumentResults));
            }
            if (!OPTIONAL_TABLE_ROUTES.includes(domain.instrument)) return;
        }

        // Deployed VADRS matrix (pediatric ADHD routing)
        if (domain.instrument === 'auto:adhd' && ['pediatric', 'schoolage', 'adolescent'].includes(state.context.ageGroup)) {
            instrumentResults.push(scoreVadrs(addFlag));
            return;
        }

        // Clinician-rated severity tables (MINI optional assessments A/B): the
        // printed form records one 0-10 rating per row and derives no total, so
        // these are reported as a rating register rather than a cutoff score.
        if (domain.instrument === 'auto:minioptional') {
            domain.questions.forEach(q => {
                if (!q.scaleId) return;
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

        // Bipolar symptom tables are opt-in. Score BISS once when it is among
        // the explicitly selected scales for this topic.
        if (domain.instrument === 'auto:bipolartable') {
            if ((domain.selectedForms || []).includes('biss'))
                deployedScreenInstruments(domain, scale => scale.id === 'biss')
                    .forEach(({ scale }) => instrumentResults.push(scoreBiss(scale, addFlag)));
            return;
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
