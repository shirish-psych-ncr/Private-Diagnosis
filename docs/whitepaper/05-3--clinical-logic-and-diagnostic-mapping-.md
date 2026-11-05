### 3. CLINICAL LOGIC AND DIAGNOSTIC MAPPING
The clinical intelligence of EPCSS is decoupled from the application code and housed in static, version-controlled JSON files under `data/scales/`, `data/domains/` and `data/core/`. This allows clinical directors to update screening logic, cutoffs, or instrument libraries without requiring software engineering intervention.

3.1 The Five-Tier Disorder Framework
The system maps symptom clusters to a comparative DSM-5-TR and ICD-11 reference database, organised by clinical complexity and screening yield. Tier numbers are navigation aids for the clinician; they are not validated prevalence claims, and any statement about combined global prevalence requires clearly defined categories and supporting data (see the appended Comparative Nosological Index and its Operational Decision Rules). Immediate safety concerns, acute medical instability, delirium, intoxication or withdrawal, and severe psychiatric symptoms always take assessment priority over tier order.
- Tier 1: Core Screening Presentations (e.g., Major Depressive Disorder, Generalized Anxiety Disorder, Alcohol Use Disorder).
- Tier 2: Common Associated and Demographic-Specific Presentations (e.g., ADHD, PTSD, Insomnia Disorder, Somatic Symptom Disorder).
- Tier 3: Less Prevalent, High Chronicity (e.g., Obsessive-Compulsive Disorder, Personality Disorders, Eating Disorders).
- Tier 4: Low Prevalence, High Severity (e.g., Schizophrenia Spectrum, Neurocognitive Disorders, Gender Incongruence).
- Tier 5: Rare or Specialized Conditions (e.g., Dissociative Disorders, Paraphilic Disorders, Factitious Disorders).

3.2 Comparative Code Harmonisation with Appendix A
The disorder database in `data/core/disorders/` is harmonised against the Comparative DSM-5-TR / ICD-11 Nosological Index in Appendix A, following its rule that similar labels do not establish identical diagnostic requirements and that parent categories may require a more specific final code:
- Major Depressive Disorder carries "6A70 / 6A71" with a mapping note distinguishing single-episode (6A70) from recurrent (6A71) depressive disorder (§3.2.2).
- Stimulant Use Disorder carries "6C45 / 6C46" with a note that ICD-11 separates cocaine (6C45) from amphetamine-type stimulants (6C46); the substance-specific family must be selected rather than a generic parent (§14.2.2).
- Gender Incongruence notes the life-stage codes HA60 (adolescence/adulthood), HA61 (childhood) and HA6Z (unspecified), and that ICD gender incongruence does not require the DSM distress/impairment criterion (§12.2).
- Neurocognitive entries note that ICD dementia categories 6D80–6D85 are the principal comparison for DSM major neurocognitive disorder, with 6D71 for mild neurocognitive disorder (§15.1.2).
- Full coverage: every one of the 33 disorders in the database now carries an Appendix-A-referenced mapping note, including family/parent-category guidance (e.g., OCD 6B20 as parent of the 6B20–6B25 block §5.1.2; anorexia 6B80 within the 6B80–6B85 feeding family §9.1.2; alcohol 6C40 subdivisions §14.1.2), non-equivalence warnings (DSM acute stress disorder vs ICD QE84 §6.1.3; schizophreniform/brief psychotic vs 6A23 §2.1.3; absent 6A02.4 §1.3.2; no ICD counterparts for fetishistic/transvestic/masochism diagnoses §17.1.2), and cross-chapter placement (sleep codes in Chapter 07 §11.x). Mapping notes are clinician-facing only.
These mapping notes appear only in the clinician view; the patient view continues to withhold diagnostic labels.

3.3 Adaptive Instrument Routing
The system does not administer a monolithic battery of tests. Instead, it uses a two-stage triage:
- Stage A: Symptom Clustering. The patient selects broad domains of concern (e.g., "Low mood," "Difficulty focusing").
- Stage B: Instrument Deployment. Based on Stage A selections and the patient's declared age group, the system dynamically renders the appropriate validated scales. For example, selecting the neurodevelopmental domain for a pediatric patient triggers the Vanderbilt ADHD Diagnostic Rating Scale (VADRS), while the same selection for an adult triggers the Adult ADHD Self-Report Scale (ASRS-v1.1).

3.4 Validated Instrument Library
The system supports multiple instruments per condition to allow for differential diagnosis. The shipped library includes:
- Mood: PHQ-9, Beck Depression Inventory-II (BDI-II), Mood Disorder Questionnaire (MDQ).
- Anxiety: GAD-7, Beck Anxiety Inventory (BAI), State-Trait Anxiety Inventory (STAI).
- Trauma: PTSD Checklist for DSM-5 (PCL-5), Impact of Event Scale-Revised (IES-R), CAPS-5.
- Sleep: Insomnia Severity Index (ISI), Pittsburgh Sleep Quality Index (PSQI), Epworth Sleepiness Scale (ESS).
- Substance: AUDIT-C, DAST-10, CAGE-AID.
- Neurodevelopmental: VADRS (Pediatric), ASRS-v1.1 (Adult), Conners-3, Autism Spectrum Quotient-10 (AQ-10).
- Psychosis: CAARMS, PANSS, BPRS.

---

