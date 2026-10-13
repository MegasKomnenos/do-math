"""One authorized Codex smoke with explicit inputs; no automatic retry."""
import json
import os
import sys
from run_command import EVIDENCE, run, write_json

inputs = json.loads((EVIDENCE / 'environment.json').read_bytes())['smoke_inputs']
write_json(EVIDENCE / 'live-inputs.json', inputs)
os.environ.update(inputs)
raise SystemExit(run('live-command', [sys.executable, '-u', '-B', '.claude/skills/do-math/scripts/run_tests.py',
    'smoke.test_provider_live.ProviderLiveTests.test_codex_maintenance_files_and_termination',
    '--jobs', '1', '--output', str(EVIDENCE / 'live')]))
