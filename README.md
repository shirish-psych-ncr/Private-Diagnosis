# EPCSS — Ephemeral Pre-Consultation Clinical Screening System

A fully static, zero-backend, zero-persistence mental health intake screening tool.
All clinical data lives only in volatile browser memory and is destroyed on tab close.
See `WHITEPAPER.md` for the complete technical and clinical specification.

## Files
- `index.html` — single-page app shell with strict Content Security Policy (no inline scripts, no third-party trackers)
- `app.js` — vanilla JS engine: ephemeral state model, adaptive two-stage routing, scoring, safety/crisis override, EN/HI live language switching, client-side PDF generation
- `data.json` — decoupled clinical logic: 7 symptom domains, 22 validated instruments (PHQ-9, GAD-7, PCL-5, VADRS, ASRS-v1.1, CAARMS...), 31-disorder Tier 1-5 DSM-5-TR / ICD-11 harmonized database, crisis resources, bilingual dictionary
- `styles.css` — responsive, WCAG 2.1 AA-oriented styling with high-contrast mode
- `tests/epcss_test.js` — headless jsdom integration test covering the full five-stage journey

## Privacy guarantees
1. Zero-transmission: no backend, no analytics; only static asset downloads occur over the network.
2. Zero-persistence: localStorage, sessionStorage, and cookies are strictly prohibited for clinical data.
3. Safety-first: items flagged `safety:true` (e.g., PHQ-9 item 9) immediately open a non-dismissible localized crisis modal.

## Run locally
Any static file server works, e.g.:

    python3 -m http.server 8000

Then open http://localhost:8000 (fetch of `data.json` requires HTTP, not `file://`).

## Test
Requires Node.js and `jsdom` (`npm i jsdom`):

    node tests/epcss_test.js

## Deploy
Push to GitHub and enable Pages — the repository's static assets are the entire application.
Clinical updates require editing only `data.json`; every change is Git-audited.
