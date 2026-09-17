"""Non-authoritative, worker-local feedback using the supplied verifier edition."""
from pathlib import Path
import argparse
import json
import tempfile

from .context_store import _safe_path
from .formal import verify_lean
from .submission import load_json


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True)
    parser.add_argument('--declaration', action='append', required=True)
    args = parser.parse_args(argv)
    workspace = Path.cwd().resolve()
    try:
        context = load_json((workspace / 'input/submission/context.json').read_bytes())
        settings = context['formal_verifier']
        source = _safe_path(workspace, args.source).read_bytes().decode('utf-8')
        stopped = lambda: (workspace / 'stop-request.json').exists()
        if stopped():
            result = {'status': 'stopped', 'reason': 'stop requested before compilation'}
        elif not settings.get('command'):
            result = {'status': 'unavailable', 'reason': 'no compiler was supplied in this input'}
        else:
            scratch = workspace / '.scratch'
            scratch.mkdir(exist_ok=True)
            with tempfile.TemporaryDirectory(prefix='lean-preview-', dir=scratch) as directory:
                result = verify_lean(source=source, declarations=args.declaration,
                    workspace=Path(directory), lean_command=settings['command'],
                    allowed_axioms=tuple(settings['allowed_axioms']),
                    timeout_seconds=settings['timeout_seconds'], should_stop=stopped)
        result.update(authoritative=False, input_snapshot=context.get('snapshot'),
            assurance='Same supplied verifier code and configured command; central verification of the submitted source is still required. Shared compiler libraries and Lake caches are not isolated by this preview.')
    except (ValueError, KeyError, OSError) as error:
        result = {'status': 'unavailable', 'reason': str(error), 'authoritative': False}
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result['status'] == 'verified' else 1
