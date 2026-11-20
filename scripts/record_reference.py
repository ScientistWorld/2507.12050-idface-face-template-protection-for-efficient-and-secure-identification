"""Record measured reference rows; preserve all source-paper reported numbers.

Called only by the reproduction script after the isolated reference run.
Future evaluation never writes reference.json.
"""
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
path = root / 'scoring/reference.json'
reference = json.loads(path.read_text())
scores = json.loads((root / 'scoring/scores_test.json').read_text())
for name, experiment in reference['experiments'].items():
    measured = scores['experiments'][name]
    for method, row in experiment['results'].items():
        row.update(measured['results'][method])
    if measured['_diagnostics']['idface']['status'] != 'ok':
        raise RuntimeError('The reference failed; refusing to record it')
path.write_text(json.dumps(reference, indent=2, allow_nan=False) + '\n')
