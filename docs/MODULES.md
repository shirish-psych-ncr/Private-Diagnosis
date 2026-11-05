# Per-scale source map

The browser imports native JavaScript modules and fetches individual JSON files. There is no compiled application or clinical-data bundle. `app.js` only imports and starts the application.

| Task | Edit |
| --- | --- |
| Custom scoring | `src/app/scales/<id>.js` |
| Questions, options and scale-specific scoring metadata | `data/scales/<id>.json` |
| Domain routing and screen-ins | `data/domains/<id>.json` |
| Common raw-sum and rating rubrics | `src/app/scoring/` |
| Data fetching and domain question hydration | `src/app/data.js` |
| Shared translations, metadata, instruments and disorders | `data/core/` |
| Results dispatch | `src/app/results-computation.js` |
| Safety, PDF, events and UI | Named modules in `src/app/` |
| Python instrument builders | `src/builders/<instrument>/` |
| Specification chapters | `docs/whitepaper/` |

## Scale files

Dedicated scoring modules cover BISS, CAS, DES-II, FAC22-SR, GCLS, IPDE, MID-60, PDQ-4+, PHQ-15, STAXI-CA and VADRS. PHQ-9, GAD-7, PCL-5, ISI, AUDIT-C, ASRS and CAARMS have their own entry modules and questionnaire files, using the shared raw-sum implementation. MINI cross-cutting and disability tables have separate entry modules using the shared descriptive rating register. HEXACO's existing item bank remains under its own JSON entry file; this refactor does not add a new scoring implementation.

The data loader reconstructs the previous in-memory shape. Domain files retain routing and order; `questionSource` points to simple questionnaires. The 14 table-scale files are listed in `data/index.json`; the seven simple questionnaires are reached through domain references. Shared core files are listed in `data/core/index.json`.

## Validation and deployment

- `npm run build`: validate module imports and data references; write nothing.
- `npm test`: run the build gate, 260 pre-refactor scoring parity cases, screening journeys and page checks.
- `python scripts/build_data.py`: validate the modular data tree; write nothing.
- `python tests/builders_test.py`: verify Python entry points, constructors, data round trips and MINI module output in a temporary directory.

Node's VM-module flag is used only by local tests. Browsers use standard ES modules, with no runtime package dependency or bundler. Serve over HTTP(S); deploy the complete `src/` and `data/` directories with the root static assets. All definitions currently load at startup; this change reduces individual file size rather than total downloaded clinical content.

The Python entry points execute small source sections in their original scope and write individual data files. Shared core keys need explicit manifest entries. `WHITEPAPER.md` and the legacy clinic script are small indexes/entry points. The previous monoliths are removed, not retained as generated duplicates.

## Smaller sections within a scale

Large scale entry files now reference smaller parts, questions, anchors and scoring data under their own directories. For example, BISS question chunks live under `data/scales/biss/parts/`. `$file` replaces one JSON value with the referenced file; `$concat` joins referenced arrays in listed order. All reference paths are relative to the repository root. Ordinary clinical fields such as `source` retain their original meaning.

The browser and Python tools resolve the same structure into the original in-memory clinical data. `scripts/json_resources.py` writes sections around 12 KB and list chunks around 8 KB. This preserves small files when a builder saves an updated instrument. Missing files, invalid list chunks and cycles fail validation. The additional files are static definitions; responses remain in browser memory.

Styles now live in `src/styles/screening/` (8 modules) and `src/styles/clinic/` (12 modules), loaded in their original order through CSS imports. The matrix UI is separated into `matrix-rendering.js`, `anchor-legend.js` and `answers.js`. The classification appendix links to 18 topics in `docs/whitepaper/classification/`.

Large Python sections are split further without changing their concatenated source. Some are fragments of a literal or function body, so edit only the relevant fragment and preserve manifest order. They are not standalone Python modules.
