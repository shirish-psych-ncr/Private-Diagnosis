IDENTIFICATION DATA
Document Type: Technical and Clinical Whitepaper
Project Name: Ephemeral Pre-Consultation Clinical Screening System (EPCSS)
Target Audience: Clinical Directors, Privacy Officers, IT Administrators, and Development Teams
Formatting Rule: Clean, narrative-style structure with section headers. Bullet icons strictly omitted. Numbered lists and hyphens used for structural clarity.

---

# WHITEPAPER: Zero-Trust Pre-Consultation Clinical Screening
## A Static, Client-Side Architecture for Secure, Multilingual Mental Health Triage

### EXECUTIVE SUMMARY
Modern mental health care faces a critical paradox: clinicians require comprehensive, structured pre-consultation data to optimize diagnostic accuracy and session efficiency, yet traditional web-based intake forms introduce significant Protected Health Information (PHI) security risks, backend maintenance burdens, and cross-border data compliance challenges.

This whitepaper outlines the architecture and clinical logic of the Ephemeral Pre-Consultation Clinical Screening System (EPCSS). EPCSS is a fully static, client-side web application that guides patients through a structured, adaptive screening process. By leveraging a zero-backend, zero-persistence architecture, the system ensures that no PHI is ever transmitted over a network or stored on a server. All data processing, scoring, and PDF report generation occur exclusively within the patient's device memory, permanently self-destructing upon tab closure. The system natively supports real-time English and Hindi language switching, maps symptoms to a harmonized DSM-5-TR and ICD-11 tiered disorder framework, and recommends validated psychometric instruments (e.g., PHQ-9, GAD-7, VADRS) based on adaptive clinical routing.

---

### 1. INTRODUCTION AND CLINICAL RATIONALE
The pre-consultation phase is a high-value window for clinical data gathering. Unstructured intake often leads to missed comorbidities, inefficient use of session time, and delayed differential diagnosis.

EPCSS addresses this by replacing open-ended text fields with a deterministic, rubric-equivalent screening engine. The system is built upon a harmonized nosological framework that bridges the categorical approach of the DSM-5-TR with the dimensional and coding structure of the ICD-11 Chapter 06. By stratifying disorders into five prevalence-based tiers, the system prioritizes high-yield screening for common conditions while retaining the capacity to flag rare or highly specialized presentations, ensuring comprehensive clinical coverage without overwhelming the patient.

---

### 2. SYSTEM ARCHITECTURE AND TECHNICAL STACK
The architectural philosophy of EPCSS is "compute at the edge, store nowhere." The application is designed for deployment on static hosting platforms (e.g., GitHub Pages, Cloudflare Pages) without any server-side runtime environment.

2.1 Core Technologies
- Framework: Vanilla JavaScript with zero build-step complexity and maximum source transparency. The shipped implementation (`app.js`) is a single dependency-free module readable directly by auditors.
- Form Engine: A declarative, JSON-driven rendering engine producing accessible question blocks and sticky-column matrix tables with conditional branching and built-in localization support. (SurveyJS Community Edition remains an optional drop-in renderer for clinics preferring a third-party form library; the current implementation omits it deliberately to preserve the strict Content Security Policy described in Section 2.3.)
- PDF Generation: jsPDF and jspdf-autotable, loaded from a vetted CDN and executed entirely in the browser to compile the clinician-facing summary.
- Styling: A hand-authored, WCAG-oriented stylesheet (`styles.css`) providing a responsive, medical-grade interface with a dedicated high-contrast mode.

2.2 The Ephemeral State Model
Unlike conventional web applications, EPCSS strictly prohibits the use of localStorage, sessionStorage, or cookies for any clinical data. The application state resides exclusively in volatile RAM (JavaScript objects). If the patient refreshes the page, closes the tab, or experiences a browser crash, all entered data is permanently and irrecoverably destroyed. This is a deliberate security feature, not a limitation.

2.3 Content Security Policy (CSP)
A strict CSP meta tag is enforced at the document level, permitting script execution only from the same origin and vetted CDNs, blocking inline scripts, restricting styles and fonts to local assets, and limiting `connect-src` to `'self'` so that no cross-origin fetch or beacon can exfiltrate form data. This prevents cross-site scripting (XSS) attacks and ensures no unauthorized third-party scripts can intercept or transmit patient responses.

---

### 3. CLINICAL LOGIC AND DIAGNOSTIC MAPPING
The clinical intelligence of EPCSS is decoupled from the application code and housed entirely within a static, version-controlled JSON file (`data.json`). This allows clinical directors to update screening logic, cutoffs, or instrument libraries without requiring software engineering intervention.

3.1 The Five-Tier Disorder Framework
The system maps symptom clusters to a comparative DSM-5-TR and ICD-11 reference database, organised by clinical complexity and screening yield. Tier numbers are navigation aids for the clinician; they are not validated prevalence claims, and any statement about combined global prevalence requires clearly defined categories and supporting data (see the appended Comparative Nosological Index and its Operational Decision Rules). Immediate safety concerns, acute medical instability, delirium, intoxication or withdrawal, and severe psychiatric symptoms always take assessment priority over tier order.
- Tier 1: Core Screening Presentations (e.g., Major Depressive Disorder, Generalized Anxiety Disorder, Alcohol Use Disorder).
- Tier 2: Common Associated and Demographic-Specific Presentations (e.g., ADHD, PTSD, Insomnia Disorder, Somatic Symptom Disorder).
- Tier 3: Less Prevalent, High Chronicity (e.g., Obsessive-Compulsive Disorder, Personality Disorders, Eating Disorders).
- Tier 4: Low Prevalence, High Severity (e.g., Schizophrenia Spectrum, Neurocognitive Disorders, Gender Incongruence).
- Tier 5: Rare or Specialized Conditions (e.g., Dissociative Disorders, Paraphilic Disorders, Factitious Disorders).

3.2 Comparative Code Harmonisation with Appendix A
The disorder database in `data.json` is harmonised against the Comparative DSM-5-TR / ICD-11 Nosological Index in Appendix A, following its rule that similar labels do not establish identical diagnostic requirements and that parent categories may require a more specific final code:
- Major Depressive Disorder carries "6A70 / 6A71" with a mapping note distinguishing single-episode (6A70) from recurrent (6A71) depressive disorder (§3.2.2).
- Stimulant Use Disorder carries "6C45 / 6C46" with a note that ICD-11 separates cocaine (6C45) from amphetamine-type stimulants (6C46); the substance-specific family must be selected rather than a generic parent (§14.2.2).
- Gender Incongruence notes the life-stage codes HA60 (adolescence/adulthood), HA61 (childhood) and HA6Z (unspecified), and that ICD gender incongruence does not require the DSM distress/impairment criterion (§12.2).
- Neurocognitive entries note that ICD dementia categories 6D80–6D85 are the principal comparison for DSM major neurocognitive disorder, with 6D71 for mild neurocognitive disorder (§15.1.2).
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

### 4. USER JOURNEY AND OPERATIONAL WORKFLOW
The patient experience is designed to be linear, low-friction, and transparent, consisting of five distinct stages.

4.0 Sequential Gating and Scroll Behaviour
Stage navigation follows a strict "Continue gate" rule: the next state loads only after the current stage's Continue control is activated and its validation passes. No later stage section is revealed beforehand — a single controlled reveal function is the only code path that can display a stage, and it is invoked exclusively from the consent, context, domains, and scales Continue handlers (and at boot, which reveals only Stage 1). Every newly revealed state scrolls the viewport to the top of the page before focus moves to the new stage heading, so users never resume mid-scroll in stale content. If validation fails (missing consent, no age group selected, no domains chosen, or unanswered items), an inline alert with `role="alert"` is shown and focused, and the next state is not loaded.

4.1 Stage 1: Informed Consent
The landing page presents a prominent, unambiguous disclaimer stating that the tool is an intake aid, not a diagnostic instrument. The patient must actively check a consent box acknowledging that data is ephemeral and will be lost if the tab is closed. The continue control remains disabled until consent is granted. As a defence-in-depth measure, all four Continue gates — including this one — share the same standard validation treatment: if the gate is activated without valid input (e.g., a forced or assistive-technology click on the button), an inline alert ("Please confirm the consent checkbox to continue.") is shown and focused, and the next state is not loaded.

4.2 Stage 2: Patient Context
The patient provides minimal, non-identifying demographic context essential for clinical routing: age group, primary reason for visit, optional current medications, and optional prior diagnoses. Age group is required because it drives adaptive instrument routing; activating Continue without it displays the inline validation message ("Please select an age group to continue.") and keeps the patient on this stage. No names, contact information, or government IDs are collected.

4.3 Stage 3: Symptom Clustering
The patient is presented with a grid of plain-language symptom domains. They select all domains that resonate with their current experience. This step acts as the routing mechanism for the subsequent assessment phase.

4.4 Stage 4: Clinical Assessments
The rendering engine deploys the specific, validated instruments mapped to the selected domains. The UI utilizes sticky-column matrix tables (mirroring clinical standards like the VADRS) to ensure readability on mobile devices. Real-time language toggling is available without disrupting progress.

4.5 Stage 5: Results and PDF Generation
- Patient View: A plain-language, non-stigmatizing summary. (e.g., "Your responses indicate areas of concern that merit discussion. Please review these findings with your clinician.") Diagnostic labels are intentionally withheld from the patient view.
- Clinician View: A structured, professional PDF report generated client-side. This document includes the patient's age group, reason for visit, raw instrument scores, and a "Differential Considerations" table mapped to the Tier 1-5 disorder database with corresponding DSM-5-TR and ICD-11 codes.
- Action: The patient clicks "Download PDF Report," saves the file to their local device, and physically brings it or securely uploads it to the clinic's portal prior to their appointment.

---

### 5. PRIVACY, SECURITY, AND COMPLIANCE
EPCSS is designed to exceed the baseline requirements of major data protection frameworks (e.g., HIPAA, GDPR, India's DPDP Act) through architectural minimalism.

5.1 The Zero-Transmission Guarantee
Because there is no backend API, no database, and no server-side processing, it is technically impossible for PHI to be intercepted in transit, logged in server access logs, or exposed in a database breach. The only network requests made are the initial, anonymous downloads of static HTML, CSS, JavaScript, and the clinical-logic JSON file.

5.2 The Zero-Persistence Guarantee
By strictly avoiding localStorage and sessionStorage, the system protects against threats inherent to shared devices (e.g., public library computers, shared family tablets). Closing the browser tab invokes the JavaScript garbage collector, permanently erasing all clinical data from the device's memory.

5.3 Safety Overrides and Crisis Routing
The JSON data model includes a `safety: true` flag for specific high-risk items (e.g., PHQ-9 Item 9 regarding self-harm, or psychosis screening items). If a patient endorses these items, the adaptive algorithm immediately halts the standard workflow and triggers a full-screen, non-dismissible safety modal. This modal provides localized emergency contact numbers and crisis hotline information, prioritizing immediate patient safety over data collection.

---

### 6. MULTILINGUAL AND ACCESSIBILITY IMPLEMENTATION
To serve diverse populations effectively, the system is built with internationalization (i18n) and accessibility as foundational requirements, not afterthoughts.

6.1 Real-Time Bilingual Switching
The application includes a persistent language toggle (English / Hindi). When activated, the system dynamically swaps the text content of the UI, form questions, and response options by referencing the `data.json` dictionary. Crucially, this re-rendering occurs without a page reload, preserving the patient's existing responses and current position in the assessment. Clinical Hindi translations utilize standardized, respectful psychiatric terminology to avoid colloquial or stigmatizing phrasing.

6.2 WCAG 2.1 AA Compliance
- Keyboard Navigation: All form elements, including complex matrix radio buttons, are fully operable via keyboard (Tab, Space, Enter).
- Screen Reader Compatibility: ARIA labels and roles (radiogroup, alertdialog, aria-live regions) are applied to all form inputs, ensuring screen readers accurately announce question text and response options.
- Visual Contrast: The UI adheres to strict color contrast ratios, and a high-contrast mode is available for visually impaired users.

---

### 7. DEPLOYMENT AND MAINTENANCE OPERATIONS
The operational overhead of EPCSS is minimal, designed for clinics without dedicated DevOps teams.

7.1 Static Hosting Deployment
The application is deployed via GitHub Pages. The repository contains only static assets (`index.html`, `styles.css`, `app.js`, `data.json`). Enabling GitHub Pages in the repository settings instantly provisions a secure, HTTPS-enabled URL.

7.2 Updating Clinical Logic
To add a new validated instrument or adjust a diagnostic cutoff, a clinician or administrator only needs to edit the `data.json` file. The application logic automatically ingests the new schema on the next page load. No code compilation, server restarts, or database migrations are required.

7.3 Version Control and Auditability
Because the clinical logic is stored in a JSON file within a Git repository, every change to the screening criteria is permanently logged, timestamped, and attributable to a specific user. This provides a robust audit trail for clinical governance and regulatory compliance.

---

### 8. LIMITATIONS AND ETHICAL GUARDRAILS
Transparency regarding the system's boundaries is critical for ethical deployment.

8.1 Not a Diagnostic Device
The system is explicitly framed as a "Pre-Consultation Screening Aid." It does not replace clinical judgment, structured clinical interviews, or comprehensive psychological testing. The output is a hypothesis-generating tool for the clinician, not a definitive diagnosis for the patient.

8.2 The Burden of Patient Action
Because the system cannot email or securely transmit the PDF report, it relies entirely on the patient to successfully download, save, and deliver the report to the clinic. Clinics must establish clear intake protocols instructing patients to bring this document to their appointment.

8.3 Scope of Validation
While the system utilizes internationally validated instruments (e.g., WHO, APA endorsed), the adaptive routing algorithm itself is a novel implementation. Clinics should pilot the system and correlate its output with traditional intake methods to ensure it aligns with their specific diagnostic workflows.

---

### 9. CONCLUSION AND FUTURE ROADMAP
The Ephemeral Pre-Consultation Clinical Screening System represents a paradigm shift in digital mental health intake. By rejecting the traditional backend database model in favor of ephemeral, client-side computation, it achieves an unprecedented level of data privacy and security without sacrificing clinical rigor.

Future development phases may include:
- Expansion of the language dictionary to include regional Indian languages (e.g., Marathi, Tamil, Bengali) to further reduce barriers to care.
- Integration of a client-side, password-protected PDF encryption feature for patients who wish to store the document digitally before their appointment.
- Expansion of the `data.json` library to include specialized geriatric and pediatric behavioral inventories.

By aligning cutting-edge static web architecture with harmonized, evidence-based clinical nosology, EPCSS provides a scalable, secure, and deeply respectful foundation for modern psychiatric and psychological practice.

---

## APPENDIX A: COMPARATIVE DSM-5-TR / ICD-11 NOSOLOGICAL INDEX

IDENTIFICATION DATA
---
Source Framework 1: Diagnostic and Statistical Manual of Mental Disorders, Fifth Edition, Text Revision (DSM-5-TR).
Source Framework 2: International Classification of Diseases, 11th Revision (ICD-11), Chapter 06 (Mental, Behavioural or Neurodevelopmental Disorders).
Output Structure: Segmented, tiered, numbered hierarchical list.
Formatting Rule: Bullet icons omitted per user documentation preferences.
Operational Note: This is a selective comparative index, not an official DSM-to-ICD crosswalk, a complete diagnostic classification, or a diagnostic algorithm. Similar labels do not establish identical diagnostic requirements. Preserve each system’s diagnosis and assess its criteria independently.
Verification: 2 November 2026. ICD code labels checked against the WHO ICD-11 MMS 2026-01 English Simple Tabulation. DSM context checked against APA classification resources and published updates; complete proprietary diagnostic criteria are not reproduced. DSM-5-TR printed codes are ICD-10-CM codes, not ICD-11 codes.
Scope: The 18 headings below preserve the source document’s editorial organization; they are not the official chapter sequence of either manual. Parent categories may require a more specific code for final coding. Other-specified and unspecified categories exist in many families and are not exhaustively listed.

---

1. NEURODEVELOPMENTAL DISORDERS
1.1. Intellectual and Cognitive Development
1.1.1. DSM-5-TR: Intellectual Developmental Disorder (Intellectual Disability), Global Developmental Delay, Unspecified Intellectual Developmental Disorder.
1.1.2. ICD-11 (6A00): Disorders of intellectual development (Mild 6A00.0, Moderate 6A00.1, Severe 6A00.2, Profound 6A00.3, Provisional 6A00.4, Unspecified 6A00.Z).
1.2. Communication Disorders
1.2.1. DSM-5-TR: Language Disorder, Speech Sound Disorder, Childhood-Onset Fluency Disorder (Stuttering), Social (Pragmatic) Communication Disorder.
1.2.2. ICD-11 (6A01): Developmental speech or language disorders (Speech sound 6A01.0, Speech fluency 6A01.1, Language disorder 6A01.2). Developmental language disorder with impairment of mainly pragmatic language (6A01.22) is the relevant comparison for DSM social (pragmatic) communication disorder, with independent criteria assessment.
1.3. Autism Spectrum Conditions
1.3.1. DSM-5-TR: Autism Spectrum Disorder (with specifiers for intellectual and language impairment).
1.3.2. ICD-11: Autism spectrum disorder (6A02): 6A02.0 without disorder of intellectual development, with mild/no functional-language impairment; 6A02.1 with disorder of intellectual development, with mild/no functional-language impairment; 6A02.2 without disorder of intellectual development, with impaired functional language; 6A02.3 with disorder of intellectual development, with impaired functional language; 6A02.5 with disorder of intellectual development and absence of functional language; 6A02.Y other specified; 6A02.Z unspecified. Do not infer a continuous .0–.5 sequence: 6A02.4 is absent from this MMS release.
1.4. Attention and Hyperactivity
1.4.1. DSM-5-TR: Attention-Deficit/Hyperactivity Disorder (Predominantly Inattentive, Predominantly Hyperactive-Impulsive, Combined).
1.4.2. ICD-11 (6A05): Attention deficit hyperactivity disorder (Predominantly inattentive 6A05.0, Predominantly hyperactive-impulsive 6A05.1, Combined 6A05.2).
1.5. Specific Learning Disorders
1.5.1. DSM-5-TR: Specific Learning Disorder (with impairment in reading, written expression, mathematics).
1.5.2. ICD-11 (6A03): Developmental learning disorder (Impairment in reading 6A03.0, written expression 6A03.1, mathematics 6A03.2).
1.6. Motor Disorders
1.6.1. DSM-5-TR: Developmental Coordination Disorder, Stereotypic Movement Disorder, Tic Disorders (Tourette's, Persistent Motor/Vocal, Provisional).
1.6.2. ICD-11 (6A04, 6A06): Developmental motor coordination disorder (6A04), Stereotyped movement disorder (6A06). Note: Tic disorders have their primary ICD-11 location in Chapter 08, Diseases of the nervous system (8A05), and are cross-listed under neurodevelopmental disorders. Examples: Tourette syndrome 8A05.00, Chronic motor tic disorder 8A05.01, Chronic phonic tic disorder 8A05.02, Transient motor tics 8A05.03. The last is not an automatic equivalent of all DSM provisional tic presentations.

---

2. SCHIZOPHRENIA SPECTRUM AND OTHER PRIMARY PSYCHOTIC DISORDERS
2.1. Core Schizophrenia and Related Psychoses
2.1.1. DSM-5-TR: Schizophrenia, Schizophreniform Disorder, Brief Psychotic Disorder, Delusional Disorder, Schizoaffective Disorder.
2.1.2. ICD-11 (6A20-6A24): Schizophrenia (6A20), Schizoaffective disorder (6A21), Schizotypal disorder (6A22), Acute and transient psychotic disorder (6A23), Delusional disorder (6A24).
2.1.3. Mapping note: ICD schizotypal disorder belongs to the primary psychotic-disorders grouping; DSM schizotypal personality disorder is a personality disorder, also referenced in the schizophrenia-spectrum chapter. DSM schizophreniform and brief psychotic disorders do not map automatically to ICD acute and transient psychotic disorder. Duration and symptom requirements differ; assess each system independently.
2.2. Substance and Medical Condition Psychoses
2.2.1. DSM-5-TR: Substance/Medication-Induced Psychotic Disorder, Psychotic Disorder Due to Another Medical Condition.
2.2.2. ICD-11: Coded under secondary psychotic syndrome (6E61) or specific substance-induced psychotic disorders (e.g., 6C40.6 for alcohol).
2.3. Catatonia
2.3.1. DSM-5-TR: Catatonia Associated With Another Mental Disorder, Catatonic Disorder Due to Another Medical Condition, Unspecified Catatonia.
2.3.2. ICD-11: Catatonia associated with another mental disorder (6A40); Catatonia induced by substances or medications (6A41); Catatonia, unspecified (6A4Z). Catatonia due to a medical disease is classified as Secondary catatonia syndrome (6E69). These are not subdivisions 6A40.0–6A40.2.

---

3. MOOD DISORDERS (BIPOLAR AND DEPRESSIVE)
3.1. Bipolar and Related Disorders
3.1.1. DSM-5-TR: Bipolar I Disorder, Bipolar II Disorder, Cyclothymic Disorder, Substance/Medication-Induced Bipolar Disorder, Bipolar Disorder Due to Another Medical Condition.
3.1.2. ICD-11: Bipolar type I disorder (6A60), Bipolar type II disorder (6A61), Cyclothymic disorder (6A62). Episode, psychosis and remission subdivisions must be selected separately. Examples: 6A60.0 = current manic episode without psychotic symptoms; 6A60.1 = current manic episode with psychotic symptoms; 6A60.2 = current hypomanic episode; 6A60.3 = current depressive episode, mild. They do not mean generic manic/depressive/mixed/remission states.
3.2. Depressive Disorders
3.2.1. DSM-5-TR: Major Depressive Disorder, Persistent Depressive Disorder (Dysthymia), Disruptive Mood Dysregulation Disorder, Premenstrual Dysphoric Disorder, Substance/Medication-Induced Depressive Disorder.
3.2.2. ICD-11: Single episode depressive disorder (6A70), Recurrent depressive disorder (6A71), Dysthymic disorder (6A72), Mixed depressive and anxiety disorder (6A73). Premenstrual dysphoric disorder is GA34.41, in Chapter 16, Diseases of the genitourinary system. DSM disruptive mood dysregulation disorder has no identically named ICD-11 category; Oppositional defiant disorder with chronic irritability-anger (6C90.0) is a related construct, not an automatic equivalent.
3.3. Persistent Mood Disorders
3.3.1. DSM-5-TR: Cyclothymic Disorder, Persistent Depressive Disorder.
3.3.2. ICD-11: Cyclothymic disorder (6A62) and Dysthymic disorder (6A72), already listed above. 6A80 concerns symptomatic/course presentations for mood episodes, not a persistent mood-disorders family. DSM persistent depressive disorder and ICD dysthymic disorder overlap but are not definitionally identical.

---

4. ANXIETY AND FEAR-RELATED DISORDERS
4.1. Phobic and Panic Disorders
4.1.1. DSM-5-TR: Specific Phobia, Social Anxiety Disorder, Panic Disorder, Agoraphobia.
4.1.2. ICD-11: Specific phobia (6B03), Social anxiety disorder (6B04), Panic disorder (6B01), Agoraphobia (6B02). 6B00 is Generalised anxiety disorder, not a phobic-anxiety parent category.
4.2. Generalized and Separation Anxiety
4.2.1. DSM-5-TR: Generalized Anxiety Disorder, Separation Anxiety Disorder, Selective Mutism.
4.2.2. ICD-11: Generalised anxiety disorder (6B00), Separation anxiety disorder (6B05), Selective mutism (6B06).

---

5. OBSESSIVE-COMPULSIVE AND RELATED DISORDERS
5.1. Core OCD and Body-Focused Disorders
5.1.1. DSM-5-TR: Obsessive-Compulsive Disorder, Body Dysmorphic Disorder, Hoarding Disorder, Trichotillomania (Hair-Pulling), Excoriation (Skin-Picking).
5.1.2. ICD-11: Obsessive-compulsive disorder (6B20), Body dysmorphic disorder (6B21), Olfactory reference disorder (6B22), Hypochondriasis (6B23), Hoarding disorder (6B24), Body-focused repetitive behaviour disorders (6B25), including Trichotillomania (6B25.0) and Excoriation disorder (6B25.1). DSM illness anxiety disorder is compared with ICD hypochondriasis, despite their different chapter placement. Olfactory reference disorder is not a separately named DSM Section II diagnosis; an olfactory reference presentation is described within other specified obsessive-compulsive and related disorder.

---

6. TRAUMA- AND STRESSOR-RELATED DISORDERS
6.1. Trauma-Specific Disorders
6.1.1. DSM-5-TR: Posttraumatic Stress Disorder, Acute Stress Disorder.
6.1.2. ICD-11 (6B40): Post-traumatic stress disorder (6B40), Complex post-traumatic stress disorder (6B41).
6.1.3. Mapping note: DSM acute stress disorder is not equivalent to ICD acute stress reaction (QE84), which is outside Chapter 06. ICD complex PTSD has no separately named DSM-5-TR diagnosis. Prolonged grief disorder also differs between systems, including the required time since bereavement.
6.2. Attachment and Adjustment Disorders
6.2.1. DSM-5-TR: Reactive Attachment Disorder, Disinhibited Social Engagement Disorder, Adjustment Disorders, Prolonged Grief Disorder.
6.2.2. ICD-11 (6B42-6B45): Prolonged grief disorder (6B42), Adjustment disorder (6B43), Reactive attachment disorder (6B44), Disinhibited social engagement disorder (6B45).

---

7. DISSOCIATIVE DISORDERS
7.1. Identity and Memory Dissociation
7.1.1. DSM-5-TR: Dissociative Identity Disorder, Dissociative Amnesia, Depersonalization/Derealization Disorder.
7.1.2. ICD-11: Dissociative neurological symptom disorder (6B60), Dissociative amnesia (6B61), Trance disorder (6B62), Possession trance disorder (6B63), Dissociative identity disorder (6B64), Partial dissociative identity disorder (6B65), Depersonalization-derealization disorder (6B66). “Identity disturbance due to brain injury or disease” is not the title of 6B64.

---

8. SOMATIC SYMPTOM AND DISORDERS OF BODILY DISTRESS
8.1. Somatic and Illness-Related Conditions
8.1.1. DSM-5-TR: Somatic Symptom Disorder, Illness Anxiety Disorder, Functional Neurological Symptom Disorder (Conversion Disorder), Psychological Factors Affecting Other Medical Conditions.
8.1.2. ICD-11: Bodily distress disorder (6C20); Hypochondriasis (6B23) is the relevant comparison for DSM illness anxiety disorder; Dissociative neurological symptom disorder (6B60) is the comparison for DSM functional neurological symptom disorder; Psychological or behavioural factors affecting disorders or diseases classified elsewhere (6E40). 6C21 is Body integrity dysphoria, a distinct condition, not illness anxiety disorder. Bodily distress disorder and somatic symptom disorder are related constructs, not identical criteria sets.
8.2. Factitious Conditions
8.2.1. DSM-5-TR: Factitious Disorder (Imposed on Self, Imposed on Another).
8.2.2. ICD-11: Factitious disorder imposed on self (6D50), Factitious disorder imposed on another (6D51), Factitious disorders, unspecified (6D5Z). The diagnosis imposed on another describes the perpetrator’s disorder; the affected person’s harm is documented separately.

---

9. FEEDING AND EATING DISORDERS
9.1. Core Eating Disorders
9.1.1. DSM-5-TR: Anorexia Nervosa, Bulimia Nervosa, Binge-Eating Disorder, Avoidant/Restrictive Food Intake Disorder (ARFID).
9.1.2. ICD-11 (6B80-6B83): Anorexia nervosa (6B80), Bulimia nervosa (6B81), Binge eating disorder (6B82), Avoidant restrictive food intake disorder (6B83).
9.2. Other Feeding Conditions
9.2.1. DSM-5-TR: Pica, Rumination Disorder.
9.2.2. ICD-11 (6B84-6B85): Pica (6B84), Rumination-regurgitation disorder (6B85).

---

10. ELIMINATION DISORDERS
10.1. Bladder and Bowel Control
10.1.1. DSM-5-TR: Enuresis, Encopresis.
10.1.2. ICD-11: Enuresis (6C00), Encopresis (6C01). “Non-organic” is not part of these official category titles.

---

11. SLEEP-WAKE DISORDERS
Note: ICD-11 classifies these under Chapter 07 (Sleep-wake disorders); Diseases of the nervous system is Chapter 08, while DSM-5-TR includes them as a primary mental health chapter.
11.1. Insomnia and Hypersomnolence
11.1.1. DSM-5-TR: Insomnia Disorder, Hypersomnolence Disorder.
11.1.2. ICD-11: Chronic insomnia (7A00), Short-term insomnia (7A01); hypersomnolence disorders include Narcolepsy (7A20) and Idiopathic hypersomnia (7A21). DSM hypersomnolence disorder must not be automatically equated with every ICD hypersomnolence category.
11.2. Sleep-Related Breathing, Narcolepsy and Circadian Disorders
11.2.1. DSM-5-TR: Obstructive Sleep Apnea Hypopnea, Central Sleep Apnea, Sleep-Related Hypoventilation, Narcolepsy, Circadian Rhythm Sleep-Wake Disorders.
11.2.2. ICD-11: Obstructive sleep apnoea (7A41), Central sleep apnoeas (7A40), Sleep-related hypoventilation or hypoxemia disorders (7A42). Circadian disorders include Delayed sleep-wake phase disorder (7A60), Advanced sleep-wake phase disorder (7A61), Irregular sleep-wake rhythm disorder (7A62), Non-24 hour sleep-wake rhythm disorder (7A63), shift work type (7A64), jet lag type (7A65).
11.3. Parasomnias and Movement Disorders
11.3.1. DSM-5-TR: Non-Rapid Eye Movement Sleep Arousal Disorders, Nightmare Disorder, REM Sleep Behavior Disorder, Restless Legs Syndrome.
11.3.2. ICD-11: Disorders of arousal from non-REM sleep (7B00), REM sleep behaviour disorder (7B01.0), Nightmare disorder (7B01.2), Restless legs syndrome (7A80). 7A24 is Hypersomnia due to a medication or substance, not nightmare disorder.

---

12. SEXUAL DYSFUNCTIONS AND GENDER INCONGRUENCE
Note: ICD-11 moved Gender Incongruence to Chapter 17 (Conditions related to sexual health) to de-stigmatize it, whereas DSM-5-TR retains Gender Dysphoria.
12.1. Sexual Dysfunctions
12.1.1. DSM-5-TR: Delayed Ejaculation, Erectile Disorder, Female Orgasmic Disorder, Female Sexual Interest/Arousal Disorder, Genito-Pelvic Pain/Penetration Disorder, Male Hypoactive Sexual Desire Disorder, Premature Ejaculation.
12.1.2. ICD-11: Hypoactive sexual desire dysfunction (HA00); Sexual arousal dysfunctions (HA01), including Female sexual arousal dysfunction (HA01.0) and Male erectile dysfunction (HA01.1); Orgasmic dysfunctions (HA02); Ejaculatory dysfunctions (HA03), including Male early ejaculation (HA03.0) and Male delayed ejaculation (HA03.1); Sexual pain-penetration disorder (HA20). DSM female sexual interest/arousal disorder spans constructs separated in ICD-11; no single automatic equivalent is appropriate.
12.2. Gender Identity Conditions
12.2.1. DSM-5-TR: Gender Dysphoria (in Children, Adolescents/Adults).
12.2.2. ICD-11: Gender incongruence of adolescence or adulthood (HA60), Gender incongruence of childhood (HA61), Gender incongruence, unspecified (HA6Z). These are in Chapter 17, Conditions related to sexual health. DSM gender dysphoria requires clinically significant distress or impairment; ICD gender incongruence is a different construct and does not require that same distress/impairment criterion. Gender diversity alone is not a mental disorder.
12.2.3. Editorial note on the supplied list: the source text contained a duplicated block here — a stray "12.1.3. Mapping note" reproducing Section 2.1.3 verbatim, plus a mis-numbered "2.2.2. ICD-11" carrying the gender-incongruence content. Both belong to no item in this section; they have been removed and the gender-incongruence content retained as 12.2.2 above. No clinical content was lost.

---

13. DISRUPTIVE, IMPULSE-CONTROL, AND CONDUCT DISORDERS
13.1. Behavioral and Conduct Disorders
13.1.1. DSM-5-TR: Oppositional Defiant Disorder, Conduct Disorder, Antisocial Personality Disorder (also listed in Personality Disorders).
13.1.2. ICD-11 (6C90-6C91): Oppositional defiant disorder (6C90), Conduct-dissocial disorder (6C91).
13.2. Impulse Control Disorders
13.2.1. DSM-5-TR: Intermittent Explosive Disorder, Kleptomania, Pyromania.
13.2.2. ICD-11: Pyromania (6C70), Kleptomania (6C71), Compulsive sexual behaviour disorder (6C72), Intermittent explosive disorder (6C73). Compulsive sexual behaviour disorder has no separately named DSM-5-TR Section II counterpart; distress based entirely on moral disapproval is insufficient for the ICD diagnosis.

---

14. SUBSTANCE-RELATED AND ADDICTIVE DISORDERS
14.1. Alcohol and Depressants
14.1.1. DSM-5-TR: Alcohol Use Disorder, Alcohol Intoxication, Alcohol Withdrawal, Sedative/Hypnotic/Anxiolytic Use Disorder.
14.1.2. ICD-11 (6C40, 6C44): Disorders due to use of alcohol (6C40), Disorders due to use of sedatives or hypnotics (6C44).
14.2. Stimulants, Cannabis, and Nicotine
14.2.1. DSM-5-TR: Cannabis Use Disorder, Stimulant Use Disorder, Tobacco Use Disorder, Caffeine-Related Disorders.
14.2.2. ICD-11: Cannabis (6C41), Cocaine (6C45), Stimulants including amphetamines, methamphetamine or methcathinone (6C46), Caffeine (6C48), Nicotine (6C4A). Each is a “Disorders due to use of…” family. DSM stimulant-related diagnoses distinguish amphetamine-type substances and cocaine; ICD separates these families.
14.3. Other Substances and Behavioral Addictions
14.3.1. DSM-5-TR: Opioid Use Disorder, Hallucinogen Use Disorder, Inhalant Use Disorder, Gambling Disorder.
14.3.2. ICD-11: Opioids (6C43), Hallucinogens (6C49), Volatile inhalants (6C4B), Gambling disorder (6C50), Gaming disorder (6C51). Additional substance families include Synthetic cannabinoids (6C42), Synthetic cathinones (6C47), MDMA or related drugs (6C4C), Dissociative drugs including ketamine or PCP (6C4D), Other specified psychoactive substances (6C4E), Multiple specified psychoactive substances (6C4F), Unknown/unspecified psychoactive substances (6C4G), Non-psychoactive substances (6C4H). DSM Internet Gaming Disorder is a Section III condition for further study, not a Section II diagnosis equivalent in status to ICD Gaming disorder. DSM use disorder is not automatically equivalent to ICD dependence: assess harmful use, dependence, intoxication, withdrawal and induced syndromes independently.

---

15. NEUROCOGNITIVE DISORDERS
15.1. Delirium and Major/Mild Neurocognitive Disorders
15.1.1. DSM-5-TR: Delirium, Major/Mild Neurocognitive Disorder due to Alzheimer's Disease, Frontotemporal Lobar Degeneration, Lewy Body Disease, Vascular Disease, Traumatic Brain Injury, HIV, Prion Disease, Parkinson's Disease, Huntington's Disease.
15.1.2. ICD-11: Delirium (6D70), Mild neurocognitive disorder (6D71), Amnestic disorder (6D72); Dementia due to Alzheimer disease (6D80), cerebrovascular disease (6D81), Lewy body disease (6D82), Frontotemporal dementia (6D83), Dementia due to psychoactive substances including medications (6D84), Dementia due to diseases classified elsewhere (6D85). Examples under 6D85: Parkinson disease (6D85.0), Huntington disease (6D85.1), HIV (6D85.3), prion disease (6D85.5), injury to the head (6D85.7). ICD dementia categories are the principal comparison for DSM major neurocognitive disorder, not exact interchangeable labels. Code associated causes and disturbances according to the relevant coding instructions.

---

16. PERSONALITY DISORDERS AND RELATED TRAITS
16.1. Personality Disorder Classification
16.1.1. DSM-5-TR: Cluster A (Paranoid, Schizoid, Schizotypal), Cluster B (Antisocial, Borderline, Histrionic, Narcissistic), Cluster C (Avoidant, Dependent, Obsessive-Compulsive).
16.1.2. ICD-11: Personality disorder (6D10), with Mild (6D10.0), Moderate (6D10.1), Severe (6D10.2), severity unspecified (6D10.Z). Additional prominent traits/patterns: Negative affectivity (6D11.0), Detachment (6D11.1), Dissociality (6D11.2), Disinhibition (6D11.3), Anankastia (6D11.4), Borderline pattern (6D11.5). These qualifiers do not replace assessment of personality disorder and its severity. DSM Section II uses categorical diagnoses; Section III also contains an Alternative Model for Personality Disorders.

---

17. PARAPHILIC DISORDERS
17.1. Atypical Sexual Interest Disorders
17.1.1. DSM-5-TR: Voyeuristic Disorder, Exhibitionistic Disorder, Frotteuristic Disorder, Sexual Masochism Disorder, Sexual Sadism Disorder, Pedophilic Disorder, Fetishistic Disorder, Transvestic Disorder.
17.1.2. ICD-11: Exhibitionistic disorder (6D30), Voyeuristic disorder (6D31), Pedophilic disorder (6D32), Coercive sexual sadism disorder (6D33), Frotteuristic disorder (6D34), Other paraphilic disorder involving non-consenting individuals (6D35), Paraphilic disorder involving solitary behaviour or consenting individuals (6D36), Paraphilic disorders, unspecified (6D3Z). There are no separately named ICD-11 MMS categories for fetishistic disorder, transvestic disorder or sexual masochism disorder. Consider 6D36 only when its requirements are met; an atypical consensual interest alone does not establish a disorder. DSM sexual sadism disorder is not automatically equivalent to ICD coercive sexual sadism disorder.

---

18. OTHER MENTAL DISORDERS, MEDICATION EFFECTS, AND SECONDARY SYNDROMES
18.1. Medication-Induced and Secondary Conditions
18.1.1. DSM-5-TR: Medication-Induced Movement Disorders (Parkinsonism, Neuroleptic Malignant Syndrome, Tardive Dyskinesia, Akathisia), Antidepressant Discontinuation Syndrome.
18.1.2. ICD-11: Secondary syndromes include neurodevelopmental (6E60), psychotic (6E61), mood (6E62), anxiety (6E63), obsessive-compulsive or related (6E64), dissociative (6E65), impulse control (6E66), neurocognitive (6E67), personality change (6E68), and catatonia (6E69). This family concerns syndromes arising as a direct pathophysiological consequence of another disease; it is not a general code family for medication adverse effects or movement disorders. Medication-induced movement disorders and adverse effects require their own condition-specific and causal coding, often outside Chapter 06.
18.2. Psychosocial and Environmental Factors
18.2.1. DSM-5-TR: Other Conditions That May Be a Focus of Clinical Attention (Relational problems, Abuse and neglect, Housing/Economic problems, Suicidal behavior).
18.2.2. ICD-11: Psychosocial circumstances and reasons for contact are selected from Chapter 24, Factors influencing health status or contact with health services, rather than assuming QE00–QE8Z covers all possibilities. Examples: Acute stress reaction (QE84), Uncomplicated bereavement (QE62). These are not automatically mental disorder diagnoses. Suicidal behaviour/self-harm requires separate assessment and appropriate event, injury or history coding; it has no single universal cross-system code.

---

### COMPARATIVE NOSOLOGICAL INDEX: OPERATIONAL DECISION RULES FOR CLASSIFICATION

1. Independent diagnosis: Record the classification system, version, diagnostic label and applicable code. Treat mappings as comparative unless equivalence has been established for the particular use case. Do not infer diagnosis from a code label or symptom checklist alone.
2. Causation: A coexisting medical condition or substance exposure does not itself establish a secondary/induced disorder. Assess timing, plausible causal evidence, exclusions and whether an independent disorder better explains the presentation. Substance-induced conditions generally use their substance-specific families; do not send all of them to 6E6x.
3. Comorbidity and encounter priority: Neurodevelopmental onset does not force a condition to become the primary diagnosis. Record all independently established comorbidities; choose the main diagnosis/reason for encounter according to the setting’s coding rules. The numbered tiers are navigation aids only.
4. Chapter placement: ICD sleep-wake disorders are in Chapter 07; nervous-system diseases in Chapter 08; sexual health conditions in Chapter 17. PMDD is in Chapter 16. Chapter placement does not establish DSM diagnostic equivalence.
5. Personality: Establish ICD personality disorder and its severity before adding applicable traits/patterns. A DSM borderline personality disorder label must not be replaced by 6D11.5 alone. Other DSM personality categories cannot be deterministically assigned to one ICD trait.
6. Coding specificity: Distinguish a parent family from a final assignable diagnosis. Select valid child codes, qualifiers and required additional codes using the chosen release and local coding rules. Do not assume sequential code ranges exist.
7. Completeness: This document is a corrected overview of the supplied list. It does not enumerate every diagnosis, residual category, presentation, severity, course qualifier, exclusion or diagnostic requirement in either manual.

---

### ADDENDUM: OPERATIONAL DECISION RULES FOR SCREENING AND PRIORITIZATION

Rule 1: Clinical Priority Before Prevalence. Begin assessment with immediate safety concerns, acute medical instability, delirium, intoxication or withdrawal, and severe psychiatric symptoms. Subsequently assess common conditions alongside presentation-specific differentials. Prevalence may inform screening priorities but must not override urgency or clinical evidence. Tier numbers are organizational labels; claims about their combined global prevalence require clearly defined categories and supporting data.

Rule 2: Primary versus Secondary Etiology. Diagnose a secondary or substance/medication-induced syndrome only when evidence supports the required causal relationship; coexistence alone is insufficient. For syndromes directly attributable to another medical disease, select the applicable ICD-11 secondary syndrome category, including 6E60–6E69 where appropriate, and code the underlying condition as instructed. For substance/medication-induced presentations, use the relevant substance-specific or condition-specific category. Do not route all induced disorders to 6E6x or automatically discard independently established primary psychiatric diagnoses.

Rule 3: Developmental Classification and Comorbidity. Classify a condition as neurodevelopmental when its developmental history and clinical features satisfy the relevant diagnostic requirements. Within this document, use Tier 2.1 only if that tier explicitly denotes neurodevelopmental disorders. Record co-occurring mood, anxiety, psychotic, and other disorders when their independent requirements are met. Developmental onset does not automatically determine the principal diagnosis or reason for the current encounter.

Rule 4: Personality Disorder Assessment Across Systems. Assess ICD-11 personality disorder and its severity independently, then add applicable trait-domain or pattern qualifiers. DSM-5-TR categorical personality diagnoses do not have automatic one-to-one equivalents in ICD-11. Where requirements are met, the ICD-11 Borderline pattern qualifier is 6D11.5; 6D11.0 denotes Negative affectivity. A borderline pattern qualifier alone does not replace documentation of personality disorder and its severity.

Rule 5: Cross-Chapter Referencing and Coding. In ICD-11, sleep-wake disorders are classified in Chapter 07, while sexual dysfunctions and gender incongruence are classified in Chapter 17: Conditions related to sexual health. DSM-5-TR includes separate chapters for sleep-wake disorders, sexual dysfunctions, and gender dysphoria. Gender dysphoria and gender incongruence are related but distinct diagnostic constructs. Record each diagnosis using the requirements and codes of the chosen classification system. Verify the applicable release, national implementation, and payer requirements separately; cross-referencing does not itself establish diagnostic equivalence or billing compatibility.
