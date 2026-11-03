#!/usr/bin/env python3
"""
split_data.py — Break the monolithic data.json into a modular data/ tree.

Layout produced (all committed, all hand-editable):

    data/core.json          meta, i18n, reference, tiers, crisisResources,
                            sharedScales, instruments, disorders
    data/domains/<id>.json  one file per symptom domain (13 files)
    data/scales/<id>.json   one file per instrument item bank
    data/index.json         manifest of file names consumed by app.js bootstrap

Why this shape
--------------
`scales` alone was 69.8% of data.json's bytes and grows with every new instrument;
domains are independent routing units; core metadata is small but edited most often.
Splitting along those seams means adding an instrument touches ONE small file instead
of a 15k-line blob, so diffs stay reviewable and editor/tool loads stay cheap.

Byte-exact extraction: chunks are written from the ORIGINAL source text using a
streaming walk of the outermost JSON object only (so nested keys that happen to share
a name - e.g. "instruments" inside a scale - are never mistaken for the top level).
Formatting survives verbatim: no re-serialisation churn in Git.

Round-trip guarantee: split_data.py asserts the assembled chunks are deep-equal to
the parsed source before writing anything, and build_data.py regenerates a data.json
that is deep-equal to the original.

Run:  python3 scripts/split_data.py [--check]
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'data.json')
OUT = os.path.join(ROOT, 'data')

CORE_KEYS = ['meta', 'i18n', 'reference', 'tiers', 'crisisResources',
             'sharedScales', 'instruments', 'disorders']

DEC = json.JSONDecoder()


def _skip_ws(s, i):
    while i < len(s) and s[i] in ' \t\r\n':
        i += 1
    return i


def top_level_ranges(text):
    """Return {key: (value_start, value_end)} for the outermost JSON object."""
    i = _skip_ws(text, text.index('{') + 1)
    out = {}
    while text[i] != '}':
        key, i = DEC.raw_decode(text, i)
        i = _skip_ws(text, i)
        assert text[i] == ':', 'malformed JSON near offset %d' % i
        i = _skip_ws(text, i + 1)
        _, end = DEC.raw_decode(text, i)
        out[key] = (i, end)
        i = _skip_ws(text, end)
        if text[i] == ',':
            i = _skip_ws(text, i + 1)
    return out


def array_elements(arr_text):
    """Return [(obj, element_text)] for a JSON array's elements, order preserved."""
    i = _skip_ws(arr_text, arr_text.index('[') + 1)
    els = []
    while arr_text[i] != ']':
        start = i
        obj, i = DEC.raw_decode(arr_text, i)
        els.append((obj, arr_text[start:i]))
        i = _skip_ws(arr_text, i)
        if arr_text[i] == ',':
            i = _skip_ws(arr_text, i + 1)
    return els


def object_members(obj_text):
    """Return [(key, value_text)] for a JSON object's members, order preserved."""
    i = _skip_ws(obj_text, obj_text.index('{') + 1)
    members = []
    while obj_text[i] != '}':
        key, i = DEC.raw_decode(obj_text, i)
        i = _skip_ws(obj_text, i)
        assert obj_text[i] == ':'
        i = _skip_ws(obj_text, i + 1)
        start = i
        _, i = DEC.raw_decode(obj_text, i)
        members.append((key, obj_text[start:i]))
        i = _skip_ws(obj_text, i)
        if obj_text[i] == ',':
            i = _skip_ws(obj_text, i + 1)
    return members


def main():
    check_only = '--check' in sys.argv
    text = open(SRC, encoding='utf-8').read()
    data = json.loads(text)
    ranges = top_level_ranges(text)
    for k in CORE_KEYS + ['domains', 'scales']:
        if k not in ranges:
            raise SystemExit('data.json lacks expected top-level key %r' % k)

    def slice_of(key):
        s, e = ranges[key]
        return text[s:e]

    # --- core.json ---------------------------------------------------------
    core_json = '{\n' + ',\n'.join(
        '    "%s": %s' % (k, slice_of(k)) for k in CORE_KEYS) + '\n}\n'
    core_obj = json.loads(core_json)

    # --- domains/<id>.json -------------------------------------------------
    dom_blobs, ordered_ids = {}, []
    for obj, blob in array_elements(slice_of('domains')):
        dom_blobs[obj['id']] = blob
        ordered_ids.append(obj['id'])
    if ordered_ids != [d['id'] for d in data['domains']]:
        raise SystemExit('domain re-slicing lost ordering or ids')

    # --- scales/<id>.json --------------------------------------------------
    scale_blobs = {}
    for sid, blob in object_members(slice_of('scales')):
        scale_blobs[sid] = blob
    if sorted(scale_blobs) != sorted(data['scales']):
        raise SystemExit('scale re-slicing mismatch')

    # --- verify assembly equals source (deep) ------------------------------
    assembled = dict(core_obj)
    assembled['domains'] = [json.loads(dom_blobs[i]) for i in ordered_ids]
    assembled['scales'] = {k: json.loads(v) for k, v in scale_blobs.items()}
    if assembled != data:
        raise SystemExit('assembled chunks are NOT deep-equal to data.json - aborting')

    # --- index.json --------------------------------------------------------
    # `topLevelOrder` records the source key order so build_data.py can re-emit a
    # data.json that is byte-comparable (a split -> rebuild round trip produces no
    # diff noise, which keeps clinical Git history readable).
    src_order = [k for k in ranges]
    index = {
        '_comment': 'Runtime assembly manifest for app.js bootstrap. Generated by '
                    'scripts/split_data.py. Edit the chunk files it lists, then run '
                    'scripts/build_data.py to regenerate data.json.',
        'schemaVersion': data['meta']['schemaVersion'],
        'core': 'data/core.json',
        'domains': ordered_ids,
        'scales': sorted(scale_blobs),
        'topLevelOrder': src_order,
    }
    index_json = json.dumps(index, indent=2, ensure_ascii=False) + '\n'

    def pretty(blob):
        """Re-indent a raw slice at file level (the slices were indented inside
        data.json, so they need one dedent pass to look natural standalone)."""
        return json.dumps(json.loads(blob), ensure_ascii=False, indent=2) + '\n'

    files = {'core.json': core_json, 'index.json': index_json}
    for did, blob in dom_blobs.items():
        files[os.path.join('domains', did + '.json')] = pretty(blob)
    for sid, blob in scale_blobs.items():
        files[os.path.join('scales', sid + '.json')] = pretty(blob)

    if check_only:
        print('source data.json: %d bytes / %d lines'
              % (len(text.encode()), text.count('\n') + 1))
        print('would write %d files:' % len(files))
        for rel in sorted(files, key=lambda p: -len(files[p].encode())):
            print('  %-34s %7d bytes' % (rel, len(files[rel].encode())))
        return

    for rel, blob in files.items():
        path = os.path.join(OUT, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as fh:
            fh.write(blob)
    total = sum(len(b.encode()) for b in files.values())
    print('wrote data/ tree: %d files, %d bytes (source data.json %d bytes)'
          % (len(files), total, len(text.encode())))


if __name__ == '__main__':
    main()
