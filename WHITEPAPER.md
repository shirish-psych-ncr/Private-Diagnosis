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
The system maps symptom clusters to a harmonized DSM-5-TR and ICD-11 reference database, stratified by global prevalence and clinical complexity:
- Tier 1: Highly Prevalent Disorders (e.g., Major Depressive Disorder, Generalized Anxiety Disorder, Alcohol Use Disorder).
- Tier 2: Moderately Prevalent, Demographic-Specific (e.g., ADHD, PTSD, Insomnia Disorder, Somatic Symptom Disorder).
- Tier 3: Less Prevalent, High Chronicity (e.g., Obsessive-Compulsive Disorder, Personality Disorders, Eating Disorders).
- Tier 4: Low Prevalence, High Severity (e.g., Schizophrenia Spectrum, Neurocognitive Disorders, Gender Incongruence).
- Tier 5: Rare or Specialized Conditions (e.g., Dissociative Disorders, Paraphilic Disorders, Factitious Disorders).

3.2 Adaptive Instrument Routing
The system does not administer a monolithic battery of tests. Instead, it uses a two-stage triage:
- Stage A: Symptom Clustering. The patient selects broad domains of concern (e.g., "Low mood," "Difficulty focusing").
- Stage B: Instrument Deployment. Based on Stage A selections and the patient's declared age group, the system dynamically renders the appropriate validated scales. For example, selecting the neurodevelopmental domain for a pediatric patient triggers the Vanderbilt ADHD Diagnostic Rating Scale (VADRS), while the same selection for an adult triggers the Adult ADHD Self-Report Scale (ASRS-v1.1).

3.3 Validated Instrument Library
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

4.1 Stage 1: Informed Consent
The landing page presents a prominent, unambiguous disclaimer stating that the tool is an intake aid, not a diagnostic instrument. The patient must actively check a consent box acknowledging that data is ephemeral and will be lost if the tab is closed. The continue control remains disabled until consent is granted.

4.2 Stage 2: Patient Context
The patient provides minimal, non-identifying demographic context essential for clinical routing: age group, primary reason for visit, optional current medications, and optional prior diagnoses. No names, contact information, or government IDs are collected.

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
