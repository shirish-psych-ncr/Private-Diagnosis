"""Verify source-section builders and modular-data round trips in a temporary tree."""
import inspect
import json
from pathlib import Path
import runpy
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))
import clinical_data

with tempfile.TemporaryDirectory(prefix='epcss-builder-test-') as temporary:
    temporary = Path(temporary)
    shutil.copytree(ROOT / 'data', temporary / 'data')
    clinical_data.ROOT = temporary
    before = clinical_data.load_clinical_data()
    clinical_data.save_clinical_data(before)
    assert clinical_data.load_clinical_data() == before
    # Saving a builder result must retain small sections, never inflate the scale file.
    assert all(len(p.read_text(encoding='utf-8').encode('utf-8')) <= 12000
               for p in (temporary / 'data').rglob('*.json'))
    assert not (temporary / 'data.json').exists()
    manifest = json.loads((ROOT / 'scripts/builder-sources.json').read_text(encoding='utf-8'))
    constructed = 0
    for name in manifest:
        namespace = runpy.run_path(str(ROOT / ('scripts/build_' + name + '.py')), run_name='builder_test')
        for key, value in namespace.items():
            if key.startswith('build_') and inspect.isfunction(value) and not inspect.signature(value).parameters:
                result = value()
                assert isinstance(result, dict) and result.get('id'), key
                constructed += 1
    mini = clinical_data.read_json('data/interviews/mini/index.json')
    assert len(mini['modules']) == 20
    assert all((temporary / 'data/interviews/mini' / module).exists() for module in mini['modules'])
    assert not (temporary / 'data/core.json').exists()
    print('Builder checks passed:', len(manifest), 'entry points,', constructed,
          'scale/domain constructors, modular round trip and 20 MINI module files.')
