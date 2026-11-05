import { computeResults } from './results-computation.js';
import { renderDomainScreenIns } from './screen-in.js';
import { state, CLINICAL_DATA } from './state.js';

/* ------------------------------------------------------------------ *
 * 6. STAGE 3 — ADAPTIVE INSTRUMENT DEPLOYMENT (routing engine)
 * ------------------------------------------------------------------ */

/**
 * Given the selected domains and the declared age group, decide which
 * instruments to deploy. `auto:adhd` routes VADRS for pediatric/adolescent
 * and ASRS-v1.1 (the domain's own item set) for adults, per the whitepaper.
 */
/* Routes whose optional instruments are always shown once the domain is picked. */
const OPTIONAL_TABLE_ROUTES = ['auto:minioptional', 'auto:pdscreen', 'auto:angertable', 'auto:dissociationtable', 'auto:somatoptable', 'auto:genderdistress', 'auto:bipolartable'];

function routeInstruments() {
    const deployed = [];
    CLINICAL_DATA.domains.forEach(domain => {
        if (!state.selectedDomains.has(domain.id)) return;
        const instName = domain.instrument || null;
        if (instName === 'auto:adhd') {
            const peds = ['pediatric', 'adolescent'].includes(state.context.ageGroup);
            deployed.push({
                domain,
                scaleId: peds ? 'vadrs' : null,
                instrumentLabel: peds ? 'VADRS' : 'ASRS-v1.1'
            });
        } else if (OPTIONAL_TABLE_ROUTES.includes(instName)) {
            if (instName === 'auto:bipolartable' && domain.baseInstrument) {
                // The mood domain keeps its own PHQ-9 item set as the primary
                // instrument; the BISS rides along underneath as an optional
                // clinician-rated table.
                deployed.push({ domain, scaleId: null, instrumentLabel: domain.baseInstrument });
            }
            // MINI 7.0.2 additional optional interview assessments (pp. 36-37):
            // A - Cross-Cutting Measures (Severity of Symptom) and
            // B - Disability / Functional Impairment. Both are clinician-rated
            // 0-10 tables reached through the domain's own screen-in items.
            //
            // auto:pdscreen is the personality-disorder screening block: endorsing a
            // screen-in item deploys the keyed True/False instrument attached to it
            // (IPDE ICD-10 module screening questionnaire / PDQ-4+). Neither screen
            // is diagnostic — they flag which F60/DSM cluster needs the full interview.
            //
            // auto:angertable deploys the summed anger instruments (STAXI-C/A,
            // Clinical Anger Scale); auto:dissociationtable deploys the dissociative-
            // experience self-report instruments (MID-60 short form, DES-II), each
            // attached to one screen-in item of the `dissociation` domain.
            //
            // auto:genderdistress deploys the Gender Congruence and Life Satisfaction
            // Scale (GCLS) for the `gender` domain - a reverse-keyed, subscale-scored
            // self-report of gender-related distress and life satisfaction.
            //
            // auto:bipolartable deploys the Bipolar Inventory of Signs and Symptoms
            // Scale (BISS, Bowden) on the `mood` domain: 44 clinician-rated items
            // scored 0-4 over the most recent 7 days from self-report plus family
            // and interview observation. The mood domain keeps its own PHQ-9 item
            // scoring, so the BISS rides along as an optional table attached to the
            // domain's two bipolar screen-in items (mood_biss_1/2) rather than
            // replacing the domain instrument.
            // Screen-in questions for these routes are rendered above the
            // instruments they relate to, so they stay answerable (see
            // renderDomainScreenIns).
            domain.questions.forEach(q => {
                if (!q.scaleId) return;
                // Optional rating tables (MINI A/B, IPDE, PDQ-4+, anger,
                // dissociation, somatic instruments) are deployed as soon as their
                // domain is selected. Gating them behind their own screen-in item
                // would be a dead end: the screen-in question and the instrument it
                // unlocks live on the same page, so under an endorse-first rule the
                // table could never appear and the screen-in could never be endorsed.
                // The screen-in answers still drive the domain-level flag in
                // computeResults(); endorsing one records clinical intent and never
                // adds or removes a table.
                deployed.push({ domain, scaleId: q.scaleId, instrumentLabel: null, ratingTable: true });
            });
        } else {
            deployed.push({ domain, scaleId: null, instrumentLabel: instName });
        }
    });
    return deployed;
}

export { OPTIONAL_TABLE_ROUTES, routeInstruments };
