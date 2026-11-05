"""Lossless JSON resources with small referenced sections and ordered list chunks."""
import json
import re
from pathlib import Path

MAX_BYTES = 12000
CHUNK_BYTES = 8000


def encode(value):
    return json.dumps(value, ensure_ascii=False, indent=2) + '\n'


def size(value):
    return len(encode(value).encode('utf-8'))


def read_resource(root, relative, ancestors=()):
    if relative in ancestors:
        raise ValueError('Circular JSON reference: ' + relative)
    value = json.loads((root / relative).read_text(encoding='utf-8'))
    return resolve(root, value, ancestors + (relative,))


def resolve(root, value, ancestors):
    if isinstance(value, list):
        return [resolve(root, item, ancestors) for item in value]
    if not isinstance(value, dict):
        return value
    if set(value) == {'$file'}:
        return read_resource(root, value['$file'], ancestors)
    if set(value) == {'$concat'}:
        items = []
        for relative in value['$concat']:
            chunk = read_resource(root, relative, ancestors)
            if not isinstance(chunk, list):
                raise ValueError('JSON list chunk must contain an array: ' + relative)
            items.extend(chunk)
        return items
    return {key: resolve(root, item, ancestors) for key, item in value.items()}


def write_resource(root, relative, value):
    """Plan all sections before writing; retain small resources as ordinary JSON."""
    planned = {}

    def section(filename, item):
        planned[filename] = encode(split(item, str(Path(filename).with_suffix('')).replace('\\', '/')))
        return {'$file': filename}

    def split(item, folder):
        if size(item) <= MAX_BYTES:
            return item
        if isinstance(item, dict):
            output = dict(item)
            for key in sorted(item, key=lambda key: size(item[key]), reverse=True):
                if size(output) <= MAX_BYTES:
                    break
                slug = re.sub(r'[^a-zA-Z0-9_-]', '_', key)
                filename = folder + '/' + slug + '.json'
                if filename in planned:
                    raise ValueError('Conflicting JSON section name: ' + filename)
                output[key] = section(filename, item[key])
            return output
        if isinstance(item, list):
            items = []
            for index, child in enumerate(item):
                if size(child) > CHUNK_BYTES:
                    label = child.get('id', str(index + 1)) if isinstance(child, dict) else str(index + 1)
                    slug = re.sub(r'[^a-zA-Z0-9_-]', '_', str(label))
                    child = section(folder + '/%03d-%s.json' % (index + 1, slug), child)
                items.append(child)
            if size(items) <= MAX_BYTES:
                return items
            chunks, chunk = [], []
            for child in items:
                if chunk and size(chunk + [child]) > CHUNK_BYTES:
                    chunks.append(chunk)
                    chunk = []
                chunk.append(child)
            if chunk:
                chunks.append(chunk)
            paths = []
            for index, chunk in enumerate(chunks):
                filename = folder + '/questions-%03d.json' % (index + 1)
                section(filename, chunk)
                paths.append(filename)
            return {'$concat': paths}
        raise ValueError('Single JSON value exceeds section limit: ' + folder)

    section(relative, value)
    for filename, text in planned.items():
        destination = root / filename
        destination.parent.mkdir(parents=True, exist_ok=True)
        if not destination.exists() or destination.read_text(encoding='utf-8') != text:
            destination.write_text(text, encoding='utf-8')
