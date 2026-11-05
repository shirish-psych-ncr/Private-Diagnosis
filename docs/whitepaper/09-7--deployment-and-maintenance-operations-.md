### 7. DEPLOYMENT AND MAINTENANCE OPERATIONS
The operational overhead of EPCSS is minimal, designed for clinics without dedicated DevOps teams.

7.1 Static Hosting Deployment
The application is deployed via GitHub Pages. The repository contains only static assets (`index.html`, `styles.css`, the `app.js` entry point, and the `src/` and `data/` trees). Enabling GitHub Pages in the repository settings instantly provisions a secure, HTTPS-enabled URL.

7.2 Updating Clinical Logic
To add a new validated instrument or adjust a diagnostic cutoff, a clinician or administrator only needs to edit the relevant instrument file in `data/scales/` and its domain settings in `data/domains/`. The application logic automatically ingests the new schema on the next page load. No code compilation, server restarts, or database migrations are required.

7.3 Version Control and Auditability
Because the clinical logic is stored in a JSON file within a Git repository, every change to the screening criteria is permanently logged, timestamped, and attributable to a specific user. This provides a robust audit trail for clinical governance and regulatory compliance.

---

