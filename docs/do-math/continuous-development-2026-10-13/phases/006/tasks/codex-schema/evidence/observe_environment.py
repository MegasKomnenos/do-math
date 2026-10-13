"""Observe only non-secret configuration and installed command surfaces."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tomllib

from run_command import ROOT, EVIDENCE, write_json

settings = []
for p in (Path.home() / '.codex/config.toml', ROOT / '.codex/config.toml'):
    d = tomllib.loads(p.read_text(encoding='utf-8-sig'))
    settings.append({'path': str(p), 'selected_fields': {k: d[k] for k in ('model','model_reasoning_effort') if k in d}})
cache = json.loads((Path.home() / '.codex/models_cache.json').read_bytes())
models = [{k: row[k] for k in ('slug','supported_reasoning_levels','default_reasoning_level') if k in row}
          for row in cache['models'] if row['slug'] == settings[-1]['selected_fields']['model']]
sys.path.insert(0, str(ROOT / '.claude/skills/do-math/scripts'))
from do_math.claude_adapter import ADAPTERS
from do_math.file_io import executable_identity
from do_math.cli_execution import surface_report
from do_math.payloads import json_safe
from subprocess import CompletedProcess

surfaces = {}
for provider, adapter in ADAPTERS.items():
    cli = executable_identity(provider, strict=True)
    observations = []
    for index, args in enumerate([('--version',), *(args for args, _ in adapter.help_commands)]):
        argv = [str(cli), *args]
        p = subprocess.run(argv, capture_output=True, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        filename = f'environment02-{provider}-{index}'
        (EVIDENCE / (filename + '.stdout.txt')).write_bytes(p.stdout)
        (EVIDENCE / (filename + '.stderr.txt')).write_bytes(p.stderr)
        observations.append({'argv': argv, 'exit_code': p.returncode,
                             'stdout': filename + '.stdout.txt', 'stderr': filename + '.stderr.txt',
                             'sha256': hashlib.sha256(p.stdout).hexdigest()})
    results = [CompletedProcess(r['argv'], r['exit_code'], (EVIDENCE / r['stdout']).read_bytes()) for r in observations]
    verdict = surface_report(results[0], [(r, flags) for r, (_, flags) in zip(results[1:], adapter.help_commands)],
        identity={}, provider=provider, cli_path=str(cli), surface=adapter.surface_capabilities,
        unknown=adapter.unknown_capabilities)
    surfaces[provider] = {'cli': str(cli), 'cli_sha256': hashlib.sha256(cli.read_bytes()).hexdigest(),
                          'version': results[0].stdout.decode('utf-8').strip(),
                          'observations': observations, 'verdict': verdict}
    assert verdict['verified'], verdict
inputs = {'DO_MATH_SMOKE_CODEX_CLI': surfaces['codex']['cli'],
          'DO_MATH_SMOKE_CODEX_MODEL': settings[-1]['selected_fields']['model'],
          'DO_MATH_SMOKE_CODEX_EFFORT': 'low', 'DO_MATH_SMOKE_HOST': 'desktop'}
result = {'settings': settings, 'codex_model_observations': models, 'surfaces': surfaces, 'smoke_inputs': inputs,
          'input_reason': 'Current configured Codex model and supported low effort for the short file smoke; no global settings changed.'}
write_json(EVIDENCE / 'environment.json', json_safe(result))
print(json.dumps(json_safe(result), ensure_ascii=False, indent=2))
