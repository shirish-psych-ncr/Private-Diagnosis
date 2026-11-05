# Editing this repository

The browser now uses real ES modules and per-scale JSON files directly. Do not recreate the old app or data bundles.

- `app.js` is a tiny ES-module entry point. `src/app/scales/<id>.js` contains individual scale scoring entry points; common rubrics live in `src/app/scoring/`.
- `data/scales/<id>.json` is each instrument's entry file. Large instruments use smaller files under `data/scales/<id>/`. Follow `$file` references and ordered `$concat` chunks; do not read the entire instrument tree. Seven simple questionnaires use their entry files through the domain's `questionSource`.
- `data/domains/<id>.json` holds routing, screen-in items and domain settings. `questionOrder` preserves the original questionnaire sequence.
- `data/core/` holds small shared files. `data/core/index.json` maps their structure; `data/index.json` lists runtime domains and table scales.
- `src/app/` contains shared state, data loading, navigation, rendering, safety, events and PDF modules. Search only the relevant file or scale directory.
- `src/builders/<instrument>/` contains small Python source sections. `scripts/build_<instrument>.py` runs them in memory using `scripts/builder_runtime.py` and `scripts/builder-sources.json`; it never generates a giant Python file. Sections are not standalone Python modules.
- Builders read and save the modular data tree through `scripts/clinical_data.py`. The MINI builder writes one JSON file per interview module under `data/interviews/mini/`.
- `src/site/` contains native modules for the separate legacy clinic effects.
- `WHITEPAPER.md` is an index; read individual chapters under `docs/whitepaper/`. See `docs/MODULES.md` for the editing map.

- JSON resource loading/writing lives in `src/app/data-resources.js` and `scripts/json_resources.py`. References are repository-root-relative. Sections stay near 12 KB and question chunks near 8 KB; do not flatten them.
- `styles.css` and `src/styles/main.css` are ordered import lists. Edit `src/styles/screening/` or `src/styles/clinic/` and preserve import order.
- Classification topics live in `docs/whitepaper/classification/`. Some Python sections split long literals or function bodies; join them only in `scripts/builder-sources.json` order.

Run `npm test` for module linking, data validation, scoring parity and journey/page tests. Run `python tests/builders_test.py` after builder/data-helper edits. `npm run build` and `python scripts/build_data.py` are read-only validation commands; no generated bundles are needed. Serve over HTTP(S) and deploy all HTML, CSS, JS, `src/` and `data/` assets together.

Do not recreate `data.json`, `data/core.json`, or a concatenated `app.js`. Preserve wording, scoring, routing, safety, language support and volatile-memory privacy during structural changes. Scoring fixtures were captured from the pre-refactor engine; update them only for intentional, reviewed behavior changes. Software tests are not clinical validation.
