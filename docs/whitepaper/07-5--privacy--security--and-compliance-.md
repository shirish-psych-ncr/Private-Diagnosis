### 5. PRIVACY, SECURITY, AND COMPLIANCE
EPCSS is designed to exceed the baseline requirements of major data protection frameworks (e.g., HIPAA, GDPR, India's DPDP Act) through architectural minimalism.

5.1 The Zero-Transmission Guarantee
Because there is no backend API, no database, and no server-side processing, it is technically impossible for PHI to be intercepted in transit, logged in server access logs, or exposed in a database breach. The only network requests made are the initial, anonymous downloads of static HTML, CSS, JavaScript, and the clinical-logic JSON file.

5.2 The Zero-Persistence Guarantee
By strictly avoiding localStorage and sessionStorage, the system protects against threats inherent to shared devices (e.g., public library computers, shared family tablets). Closing the browser tab invokes the JavaScript garbage collector, permanently erasing all clinical data from the device's memory.

5.3 Safety Overrides and Crisis Routing
The JSON data model includes a `safety: true` flag for specific high-risk items (e.g., PHQ-9 Item 9 regarding self-harm, or psychosis screening items). If a patient endorses these items, the adaptive algorithm immediately halts the standard workflow and triggers a full-screen, non-dismissible safety modal. This modal provides localized emergency contact numbers and crisis hotline information, prioritizing immediate patient safety over data collection.

---

