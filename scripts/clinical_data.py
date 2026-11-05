"""Read and update individual clinical files without creating a data.json bundle."""
import json
from pathlib import Path
from json_resources import read_resource, write_resource

ROOT = Path(__file__).resolve().parent.parent


def read_json(relative):
    return read_resource(ROOT, relative)


def write_json(relative, value):
    write_resource(ROOT, relative, value)


def read_tree(node):
    if 'source' in node:
        return read_json(node['source'])
    if 'array' in node:
        return [read_tree(value) for value in node['array']]
    return {key: read_tree(value) for key, value in node['object']}


def load_domain(identifier):
    domain = read_json('data/domains/' + identifier + '.json')
    if 'questionSource' in domain:
        scale = read_json(domain.pop('questionSource'))
        questions = {q['id']: q for q in scale['questions'] + domain['questions']}
        domain['questions'] = [questions[key] for key in domain.pop('questionOrder')]
    return domain


def load_clinical_data():
    index = read_json('data/index.json')
    data = read_tree(read_json(index['core']))
    data['domains'] = [load_domain(identifier) for identifier in index['domains']]
    data['scales'] = {identifier: read_json('data/scales/' + identifier + '.json')
                      for identifier in index['scales']}
    return data


def write_tree(node, value):
    """Preserve existing source locations; add only newly introduced object keys."""
    if 'source' in node:
        write_json(node['source'], value)
        return
    if 'array' in node:
        if len(node['array']) != len(value):
            raise ValueError('Array source count changed; update the core manifest explicitly')
        for child, item in zip(node['array'], value):
            write_tree(child, item)
        return
    children = dict(node['object'])
    for key, item in value.items():
        if key not in children:
            raise ValueError('New core key requires an explicit source path: ' + key)
        write_tree(children[key], item)
    node['object'] = [(key, child) for key, child in node['object'] if key in value]


def validate_data(data):
    domain_ids = [domain['id'] for domain in data['domains']]
    if len(domain_ids) != len(set(domain_ids)):
        raise ValueError('Duplicate domain identifiers')
    for identifier, scale in data['scales'].items():
        if scale['id'] != identifier:
            raise ValueError('Scale identifier mismatch: ' + identifier)
    for domain in data['domains']:
        for question in domain['questions']:
            if question.get('scaleId') and question['scaleId'] not in data['scales']:
                raise ValueError('Missing scale: ' + question['scaleId'])


def save_clinical_data(data):
    validate_data(data)
    index = read_json('data/index.json')
    tree = read_json(index['core'])
    # Fail before writing anything if a builder introduces an unmapped core key.
    def check(node, value):
        if 'object' in node:
            children = dict(node['object'])
            if set(value) - set(children):
                raise ValueError('Add new core keys to ' + index['core'] + ' before running this builder')
            for key, item in value.items():
                check(children[key], item)
        elif 'array' in node:
            if len(node['array']) != len(value):
                raise ValueError('Update the core array manifest before running this builder')
            for child, item in zip(node['array'], value):
                check(child, item)
    core = {key: value for key, value in data.items() if key not in ('domains', 'scales')}
    check(tree, core)
    write_tree(tree, core)
    write_json(index['core'], tree)
    for domain in data['domains']:
        relative = 'data/domains/' + domain['id'] + '.json'
        previous = read_json(relative) if (ROOT / relative).exists() else {}
        output = dict(domain)
        if previous.get('questionSource'):
            source = previous['questionSource']
            scale = read_json(source)
            scale['questions'] = [q for q in domain['questions'] if not q.get('scaleId')]
            write_json(source, scale)
            output['questionSource'] = source
            output['questionOrder'] = [q['id'] for q in domain['questions']]
            output['questions'] = [q for q in domain['questions'] if q.get('scaleId')]
        write_json(relative, output)
    for identifier, scale in data['scales'].items():
        write_json('data/scales/' + identifier + '.json', scale)
    index['domains'] = [domain['id'] for domain in data['domains']]
    index['scales'] = list(data['scales'])
    index['schemaVersion'] = data.get('schemaVersion', data['meta']['schemaVersion'])
    write_json('data/index.json', index)


def save_interview(interview):
    """MINI export: each interview module is a separate JSON file."""
    folder = 'data/interviews/' + interview['id']
    metadata = {key: value for key, value in interview.items() if key != 'modules'}
    metadata['modules'] = [module['id'] + '.json' for module in interview['modules']]
    for module in interview['modules']:
        write_json(folder + '/' + module['id'] + '.json', module)
    write_json(folder + '/index.json', metadata)
    return folder + '/index.json'
