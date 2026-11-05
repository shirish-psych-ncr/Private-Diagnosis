#!/usr/bin/env python3
"""Write individual files under data/interviews/mini/ — MINI 7.0.2 (DSM-5) Modules A-P, bilingual EN/HI.

Module B is loaded verbatim from scripts/modB.json; the other modules are
defined here with the official screening logic:
  - Module A: screen-in (A1a/A2a) -> current followups (A1b/A2b) -> symptom
    gate -> timeframe-explored A3 symptoms -> A4 impairment -> diagnostic box
    (>=5 of A1-A3 Yes + A4 Yes + organic ruled out), A5 recurrence flag, A6a.
  - Module C: family-history vigilance probe, C1/C2 screen-ins (terminate if
    both No), C3a-g criteria (3+ w/ elation incl. C3f, 4+ w/ irritability),
    C4 duration buckets a/b/c, C5 hospitalization, C6 impairment, C7 change of
    function, Manic / Hypomanic / Hypomanic-Symptoms diagnostic boxes with the
    mutual-exclusion rules, C8a-c bipolar follow-ups.
  - Module D: panic attacks screen-in (D1a/D1b/D2), D3 anticipatory anxiety,
    D4a-m 13 somatic/cognitive symptoms (4+ gate), D5 lifetime box, D6 current
    follow-up.
  - Module E: agoraphobia situation list (2+ gate), E2-E6 fear/avoidance/
    persistence/impairment chain -> Current Agoraphobia box.
  - Module F: social anxiety screen-in F1 (past month), F2-F6 chain ->
    Current Social Anxiety box with performance-restricted specifier.
  - Module G: obsessions (G1a/G1b/G2) and compulsions (G3a/G3b) -> OR-gate,
    G4 impact -> Current OCD box with insight specifiers + tic-related.
  - Module H: trauma exposure H1, re-experiencing H2, past-month avoidance
    H3 (1+), negative cognitions/mood H4 (2+), arousal H5 (2+), H6 onset &
    duration, H7 impact -> Current PTSD box with depersonalization/
    derealization/delayed-expression specifiers.
  - Module I: alcohol screen-in I1, criteria I2a-k (k1 withdrawal checklist
    2+/8, k2 relief drinking, k summary counts as one criterion), 2+ gate ->
    Alcohol Use Disorder box with severity/remission specifiers.
  - Module J: drug-class list J1a, criteria J2a-k mirroring Module I with
    class-specific withdrawal checklists (sedatives 2+, opiates 3+,
    stimulants 2+, cannabis 3+), 2+ gate -> Substance Use Disorder box with
    specifiers.
  - Module K: psychotic screen K1-K7a/b (persecutory, mind reading, thought
    insertion/possession, delusions of reference, other odd beliefs, auditory
    and visual hallucinations) plus clinician-judged K8-K10 (disorganized
    speech, disorganized/catatonic behavior, negative symptoms) -> Mood
    Disorder With Psychotic Features lifetime (K11a + K11b) and current (K12)
    boxes with the mood-vs-psychotic duration rules, then Psychotic Disorder
    current (K13) and lifetime (K14) boxes requiring 1+ "b" (or "a") symptom
    of K1-K8, 2+ of K1-K10, two symptoms in the same 1-month period, and
    organic cause ruled out (O2 summary).
  - Module L: anorexia nervosa — height/weight entry with BMI-17 threshold
    table, L2 restriction, L3 fear of gaining weight, L4 body-image items
    (1+ gate -> L5), diagnostic box.
  - Module M: bulimia nervosa — binge screen M1/M2 (gate), weekly frequency
    M3, compensatory behaviours M4 (+M4a flag), self-evaluation M5, episode/
    day counts M6, anorexia-criteria check M7, M8 gate -> Bulimia Nervosa
    Current box; downstream Anorexia Binge-Eating/Purging and Restricting
    Type boxes (shared eating-disorder severity specifiers).
  - Module MB: binge eating disorder — exclusion of anorexia/bulimia (MB1/
    MB2), M2/M3/M4 linkage gates, MB6a-e binging behaviours (3+ gate), MB7
    distress, MB8 binge counts -> Binge-Eating Disorder Current box with
    severity specifiers.
  - Module N: GAD — excessive worry N1a most days N1b, not-better-explained
    gate, uncontrollable worry N2, six associated symptoms N3a-f (3+ gate),
    N4 impact + organic rule-out -> Current GAD box.
  - Module O: rule out medical/organic/drug causes — O1a substances, O1b
    medical illness, O2 clinician judgment, O2 SUMMARY (inverse of O2;
    feeds every organic-exclusion gate above).
  - Module P: antisocial personality disorder — conduct-disorder items P1a-f
    before age 15 (2+ gate), adult criteria P2a-g (3+ gate; politically or
    religiously motivated behaviours excluded) -> ASPD Lifetime box.
  - Mood Disorders Diagnostic Algorithm (after Module P): derived boxes for
    Major Depressive Disorder, Bipolar I, Bipolar II and Other Specified
    Bipolar and Related Disorder from Modules A/C/K plus the O2 summary,
    with psychotic-feature, mixed-features, anxious-distress, severity and
    most-recent-episode specifiers.
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))

def q(qid, en, hi, **kw):
    d = {"id": qid, "text": {"en": en, "hi": hi}}
    d.update(kw)
    return d

YN_NO = {"en": "No", "hi": "नहीं"}
YN_YES = {"en": "Yes", "hi": "हाँ"}


from clinical_data import load_clinical_data, save_clinical_data, save_interview
