### 2. SYSTEM ARCHITECTURE AND TECHNICAL STACK
The architectural philosophy of EPCSS is "compute at the edge, store nowhere." The application is designed for deployment on static hosting platforms (e.g., GitHub Pages, Cloudflare Pages) without any server-side runtime environment.

2.1 Core Technologies
- Framework: Vanilla JavaScript with zero build-step complexity and maximum source transparency. The small `app.js` entry point imports native modules under `src/app/`, including a separate scoring entry point per instrument. No application bundle is generated.
- Form Engine: A declarative, JSON-driven rendering engine producing accessible question blocks and sticky-column matrix tables with conditional branching and built-in localization support. (SurveyJS Community Edition remains an optional drop-in renderer for clinics preferring a third-party form library; the current implementation omits it deliberately to preserve the strict Content Security Policy described in Section 2.3.)
- PDF Generation: jsPDF and jspdf-autotable, loaded from a vetted CDN and executed entirely in the browser to compile the clinician-facing summary.
- Styling: A hand-authored, WCAG-oriented stylesheet (`styles.css`) providing a responsive, medical-grade interface with a dedicated high-contrast mode.

2.2 The Ephemeral State Model
Unlike conventional web applications, EPCSS strictly prohibits the use of localStorage, sessionStorage, or cookies for any clinical data. The application state resides exclusively in volatile RAM (JavaScript objects). If the patient refreshes the page, closes the tab, or experiences a browser crash, all entered data is permanently and irrecoverably destroyed. This is a deliberate security feature, not a limitation.

2.3 Content Security Policy (CSP)
A strict CSP meta tag is enforced at the document level, permitting script execution only from the same origin and vetted CDNs, blocking inline scripts, restricting styles and fonts to local assets, and limiting `connect-src` to `'self'` so that no cross-origin fetch or beacon can exfiltrate form data. This prevents cross-site scripting (XSS) attacks and ensures no unauthorized third-party scripts can intercept or transmit patient responses.

---

