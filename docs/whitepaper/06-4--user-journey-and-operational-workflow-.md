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

