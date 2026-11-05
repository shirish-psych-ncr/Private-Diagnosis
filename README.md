# EPCSS — Ephemeral Pre-Consultation Clinical Screening System

A static mental-health intake screening application. Clinical responses remain in browser memory; static definitions are loaded from the same site. The application has no clinical-data backend or persistent response storage.

## Edit one scale at a time

- `data/scales/<id>.json` — one instrument's entry file, with large sections under `data/scales/<id>/`.
- `src/app/scales/<id>.js` — one instrument's scoring entry point.
- `data/domains/<id>.json` — domain routing, screen-ins and questionnaire order.
- `data/core/` — shared translations, instrument metadata and disorders.
- `src/app/` — small shared UI, safety, state, loading and PDF modules.
- `src/builders/<instrument>/` — Python builder source sections.

Read [the module map](docs/MODULES.md) and [editor guidance](AGENTS.md) before editing. [The whitepaper](WHITEPAPER.md) links to individual specification chapters.

There is no `data.json` bundle. `app.js` is a tiny native-module entry point. Edits to the per-scale files are used directly without rebuilding large files.

## Run locally

Run `python -m http.server 8000`, then open http://localhost:8000. HTTP(S) is required for module imports and JSON fetches.

## Validate

Install test dependencies with `npm ci`, then run:

```text
npm test
python tests/builders_test.py
```

`npm run build` checks module linking and clinical-data references without creating bundles. `python scripts/build_data.py` is also a read-only validator. Scoring parity tests compare synthetic cases with results captured from the previous engine; they do not constitute clinical validation.

## Deploy

Deploy the root static assets together with the complete `src/` and `data/` directories. GitHub Pages or another static HTTP(S) host can serve them directly. Do not deploy only `app.js`: its imported modules and data files are required.

The informational pages use `site.css` and `site.js`. The screening app uses `styles.css`, an ordered import list for `src/styles/screening/`. The separate legacy clinic effects have their own module entry point at `src/scripts/main.js`.
