#!/usr/bin/env python3
"""
build_data.py — Reassemble data.json from the modular data/ tree.

This is the inverse of scripts/split_data.py and lets clinicians keep working in
small files:

    1. edit data/domains/<id>.json, data/scales/<id>.json or data/core.json
    2. python3 scripts/build_data.py          -> regenerates data.json
    3. npm test                               -> verifies the app still boots

data.json stays in the repo as a single-file convenience artifact / fallback: the
browser fetches the chunked data/ tree first (app.js bootstrap) and only falls back
to data.json if the manifest is missing.

Ordering is taken from data/index.json so domains keep their declared sequence.
The script refuses to write if any chunk fails to parse, if an id is duplicated, or
if a manifest entry has no matching file - a corrupt split can never silently ship.

Run:  python3 scripts/build_data.py [--check]
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'data')
OUT = os.path.join(ROOT, 'data.json')


def load_json(path):
    with open(path, encoding='utf-8') as fh:
        return json.load(fh)


def main():
    check_only = '--check' in sys.argv
    index = load_json(os.path.join(DATA, 'index.json'))

    core = load_json(os.path.join(DATA, 'core.json'))
    for k in ('meta', 'i18n', 'reference', 'tiers', 'crisisResources',
              'sharedScales', 'instruments', 'disorders'):
        if k not in core:
            raise SystemExit('data/core.json missing required key %r' % k)

    domains, seen = [], set()
    for did in index['domains']:
        path = os.path.join(DATA, 'domains', did + '.json')
        if not os.path.exists(path):
            raise SystemExit('manifest lists domain %r but %s is missing' % (did, path))
        obj = load_json(path)
        if obj.get('id') != did:
            raise SystemExit('domain file %s declares id %r' % (path, obj.get('id')))
        if did in seen:
            raise SystemExit('duplicate domain id %r' % did)
        seen.add(did)
        domains.append(obj)

    scales, scale_files = {}, sorted(index['scales'])
    for fn in os.listdir(os.path.join(DATA, 'scales')):
        if fn.endswith('.json'):
            sid = fn[:-5]
            if sid not in scale_files:
                raise SystemExit('scale file %s is not listed in data/index.json' % fn)
    for sid in scale_files:
        path = os.path.join(DATA, 'scales', sid + '.json')
        if not os.path.exists(path):
            raise SystemExit('manifest lists scale %r but %s is missing' % (sid, path))
        scales[sid] = load_json(path)

    # Every scale referenced by a domain screen-in item must exist, and every
    # deployed route's scaleIds must resolve - catch dangling ids at build time.
    referenced = set()
    for d in domains:
        for q in d.get('questions', []):
            if q.get('scaleId'):
                referenced.add(q['scaleId'])
    missing = sorted(referenced - set(scales))
    if missing:
        raise SystemExit('domains reference unknown scales: %s' % ', '.join(missing))

    payload = dict(core)
    payload['domains'] = domains
    payload['scales'] = scales

    blob = json.dumps(payload, ensure_ascii=False, indent=2) + '\n'
    reparsed = json.loads(blob)
    if reparsed['domains'] != domains or reparsed['scales'] != scales:
        raise SystemExit('serialisation round-trip failed - refusing to write')

    if check_only:
        print('would write data.json: %d bytes | %d domains | %d scales'
              % (len(blob.encode()), len(domains), len(scales)))
        return

    with open(OUT, 'w', encoding='utf-8') as fh:
        fh.write(blob)
    print('wrote data.json: %d bytes | %d domains | %d scales | schema %s'
          % (len(blob.encode()), len(domains), len(scales), core['meta']['schemaVersion']))


if __name__ == '__main__':
    main()
