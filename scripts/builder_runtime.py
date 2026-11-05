"""Execute ordered builder sources in memory, without writing a large script."""
import json
from pathlib import Path


def run_builder(name, namespace):
    root = Path(__file__).resolve().parent.parent
    manifest = json.loads((root / 'scripts/builder-sources.json').read_text(encoding='utf-8'))
    source = ''.join((root / part).read_text(encoding='utf-8') for part in manifest[name])
    # Keep the original entry point's __file__ and __name__ semantics.
    exec(compile(source, namespace['__file__'], 'exec'), namespace)
