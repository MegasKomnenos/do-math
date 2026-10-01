"""Non-authoritative, worker-local feedback using the supplied verifier edition."""
from pathlib import Path
import argparse
import json
import tempfile

from .context_store import safe_path
from .values import strict_json_loads
from .formal import verify_lean

# What a worker reads from a preview (references/공통-실행.md): the verdict and its
# reason, the checked source and toolchain, signatures, axioms, the compiler's output
# and the preview's own standing. Central dependency evidence is neither made nor printed.
PREVIEW_FIELDS = ('status', 'reason', 'source_sha256', 'declarations', 'declaration_signatures', 'axioms',
                  'toolchain', 'identity_errors', 'stdout', 'stderr', 'authoritative', 'input_snapshot', 'assurance')


def main(argv=None, *, ports=None, environment=None):
    import os
    from .wiring import real_ports
    environment = dict(os.environ) if environment is None else environment
    ports = real_ports(environment=environment) if ports is None else ports
    clock, jobs, backend = ports.clock, ports.jobs, ports.git_backend
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True)
    parser.add_argument('--declaration', action='append', required=True)
    args = parser.parse_args(argv)
    workspace = Path.cwd().resolve()
    try:
        context = strict_json_loads((workspace / 'input/submission/context.json').read_bytes())
        settings = context['formal_verifier']
        source = safe_path(workspace, args.source).read_bytes().decode('utf-8')
        stopped = lambda: (workspace / '.control' / 'stop-request.json').exists()
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
                    should_stop=stopped,
                    expected_toolchain=settings.get('expected_toolchain'),
                    extract_evidence=False, clock=clock, jobs=jobs, environment=environment)
        result.update(authoritative=False, input_snapshot=context.get('snapshot'),
            assurance='Same supplied verifier code and configured command for the kernel check, signatures and axioms; '
                      'dependency evidence is not extracted. Central verification of the submitted source is still required. '
                      'Shared compiler libraries and Lake caches are not isolated by this preview.')
    except (ValueError, KeyError, OSError) as error:
        result = {'status': 'unavailable', 'reason': str(error), 'authoritative': False}
    print(json.dumps({key: result[key] for key in PREVIEW_FIELDS if key in result}, ensure_ascii=False))
    return 0 if result['status'] == 'verified' else 1
