"""Read current non-secret configuration and record adapter-declared CLI surfaces."""
import hashlib
import json
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tomllib

from run_command import REPO, EVIDENCE, write

sys.path.insert(0, str(REPO / '.claude/skills/do-math/scripts'))
from do_math.claude_adapter import ADAPTERS
from do_math.claude_stream import parse_stream
from do_math.cli_execution import surface_report
from do_math.contracts import action_schema
from do_math.payloads import json_safe
from probe_cli import background_completed_before_result

schema = action_schema({'role': 'maintenance'})
write(EVIDENCE / 'maintenance.schema.json', schema)
config = {'host': platform.node(), 'python': sys.executable, 'settings': []}
for path in (Path.home() / '.codex/config.toml', REPO / '.codex/config.toml'):
    if path.exists():
        value = tomllib.loads(path.read_text(encoding='utf-8'))
        config['settings'].append({'path': str(path), 'selected_fields': {
            key: value[key] for key in ('model', 'model_reasoning_effort', 'model_provider') if key in value}})
for path in (Path.home() / '.claude/settings.json', REPO / '.claude/settings.json', REPO / '.claude/settings.local.json'):
    if path.exists():
        value = json.loads(path.read_text(encoding='utf-8-sig'))
        config['settings'].append({'path': str(path), 'selected_fields': {
            key: value[key] for key in ('model', 'effortLevel') if key in value}})
cache = Path.home() / '.codex/models_cache.json'
if cache.exists():
    value = json.loads(cache.read_text(encoding='utf-8'))
    config['codex_model_observations'] = [{key: row[key] for key in (
        'slug', 'default_reasoning_level', 'supported_reasoning_levels') if key in row}
        for row in value.get('models', []) if row.get('slug') == 'gpt-6-astra']
config['selected'] = {}
surfaces = EVIDENCE / 'surfaces'
surfaces.mkdir()
for provider, adapter in ADAPTERS.items():
    cli = shutil.which(provider)
    config['selected'][provider] = {'cli': cli, 'model': 'gpt-6-astra' if provider == 'codex' else 'opus',
                                    'effort': 'low', 'only_assigned_model': False}
    results, recordings = [], []
    for index, args in enumerate([('--version',)] + [args for args, _ in adapter.help_commands]):
        command = [cli, *args]
        result = subprocess.run(command, capture_output=True)
        target = surfaces / f'{provider}-{index}.txt'
        target.write_bytes(result.stdout)
        (surfaces / f'{provider}-{index}.stderr.txt').write_bytes(result.stderr)
        results.append(result)
        recordings.append({'command': command, 'exit_code': result.returncode, 'path': str(target),
                           'sha256': hashlib.sha256(result.stdout).hexdigest()})
    parsed = surface_report(results[0], [(result, flags) for result, (_, flags) in zip(results[1:], adapter.help_commands)],
                            identity={}, provider=provider, cli_path=cli, surface=adapter.surface_capabilities,
                            unknown=adapter.unknown_capabilities)
    write(surfaces / f'{provider}.json', {'recordings': recordings, 'report': json_safe(parsed)})
    config['selected'][provider]['version'] = results[0].stdout.decode('utf-8').strip()
config['effort_reason'] = 'Explicit low effort for a short file/checkpoint smoke; Codex cache and installed Claude --help record accepted effort values. Configured model names are unchanged; global effort settings are not edited.'
write(EVIDENCE / 'environment.json', config)

corpus = REPO / '.claude/skills/do-math/scripts/tests/corpus'
manifest = json.loads((corpus / 'manifest.json').read_text(encoding='utf-8'))
entry = next(row for row in manifest['entries'] if row['id'] == 'claude-background-completed-21289')
parsed = parse_stream((corpus / entry['path']).read_bytes())
background = {'entry': entry, 'source_exists': (REPO / entry['source']).exists(),
              'current_predicate': background_completed_before_result(parsed),
              'background_events': parsed['background_events'], 'selected_result': parsed['selected_result']}
write(EVIDENCE / 'historical-background.json', json_safe(background))

run = REPO / 'docs/do-math/continuous-development-2026-10-13'
assignment = json.loads((run / 'phases/003/phase.json').read_text(encoding='utf-8'))['tasks'][0]
input_hashes = {}
for ref in assignment['inputs']:
    prefix, name = ref.split(':', 1)
    path = (REPO if prefix == 'repo' else run) / name
    input_hashes[ref] = hashlib.sha256(path.read_bytes()).hexdigest()
write(EVIDENCE / 'input-hashes.json', input_hashes)
board = json.loads((REPO / 'docs/do-math/시험-재편-2026-09-29/단계-전환표-2026-10-03.json').read_text(encoding='utf-8-sig'))
write(EVIDENCE / 'historical-slices.json', {key: board['current_work'][key]
      for key in ('provider_corpus_integration', 'background_probe_contract')})
print(json.dumps({'environment': config, 'schema_required': schema['required'],
                  'schema_properties': list(schema['properties']),
                  'historical_background': {key: background[key] for key in ('source_exists', 'current_predicate')}}, ensure_ascii=False))
