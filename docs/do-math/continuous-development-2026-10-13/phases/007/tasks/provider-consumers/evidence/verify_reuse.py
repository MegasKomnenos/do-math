"""Read-only comparison of prior live inputs and current CLI surfaces; no model calls."""
from datetime import datetime, timezone
import hashlib
from pathlib import Path
import subprocess
import sys

from audit_delivery import PREVIOUS, RUN, read, sha
from run_command import ROOT, EVIDENCE, snapshot, write_json

sys.path.insert(0, str(ROOT / '.claude/skills/do-math/scripts'))
from do_math.file_io import executable_identity

old = read(PREVIOUS / 'environment.json')
surfaces = {}
for provider, previous in old['surfaces'].items():
    cli = executable_identity(provider, strict=True)
    rows = []
    for index, before in enumerate(previous['observations']):
        argv = [str(cli), *before['argv'][1:]]
        started = datetime.now(timezone.utc).isoformat()
        process = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        stdout, stderr = process.communicate()
        stem = f'reuse-{provider}-{index}'
        (EVIDENCE / (stem + '.stdout.txt')).write_bytes(stdout)
        (EVIDENCE / (stem + '.stderr.txt')).write_bytes(stderr)
        row = {'argv': argv, 'cwd': str(ROOT), 'pid': process.pid, 'started_at': started,
               'ended_at': datetime.now(timezone.utc).isoformat(), 'exit_code': process.returncode,
               'stdout': stem + '.stdout.txt', 'stderr': stem + '.stderr.txt',
               'sha256': hashlib.sha256(stdout).hexdigest(), 'previous_sha256': before['sha256']}
        rows.append(row)
    surfaces[provider] = {'path': str(cli), 'previous_path': previous['cli'], 'sha256': sha(cli),
                          'previous_sha256': previous['cli_sha256'], 'observations': rows}

current, live = snapshot(), read(PREVIOUS / 'live-command/source-before.json')
runtime = read(RUN / 'phases/006/manager-evidence/verification.json')['runtime_unchanged_since_live']
inputs = ['.claude/skills/do-math/scripts/' + p for p in
          ('tests/support/provider_live.py', 'tests/smoke/test_provider_live.py', 'probe_cli.py')]
record = {'surfaces': surfaces, 'runtime': {p: {'current': current[p], 'live': live[p]} for p in runtime},
          'smoke_inputs': {p: {'current': current[p], 'live': live[p]} for p in inputs},
          'new_model_calls': 0,
          'claude_reuse_limit': 'Phase 003 binary SHA was not recorded. Preserve phase 006 current-receipt/input/path/version/help basis; only phase 006-to-007 binary equality is checked here.',
          'background_limit': 'No new call; retain historical passed=false and only the previously approved native completion/file/local-termination properties.'}
write_json(EVIDENCE / 'live-reuse.json', record)
for name, row in surfaces.items():
    assert Path(row['path']) == Path(row['previous_path']), name
    assert row['sha256'] == row['previous_sha256'], name
    assert all(r['exit_code'] == 0 and r['sha256'] == r['previous_sha256'] for r in row['observations']), name
assert len(runtime) == 124
assert all(row['current'] == row['live'] for rows in (record['runtime'], record['smoke_inputs']) for row in rows.values())
print('Runtime 124, smoke inputs 3, and both CLI paths/binaries/version/help unchanged since phase 006; no model calls.')
