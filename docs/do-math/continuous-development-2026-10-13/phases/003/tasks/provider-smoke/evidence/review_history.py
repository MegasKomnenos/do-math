import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
from collections import Counter

from run_command import REPO, EVIDENCE, write
sys.path.insert(0, str(REPO / '.claude/skills/do-math/scripts'))
from do_math.claude_stream import parse_stream
from do_math.payloads import json_safe
from probe_cli import background_completed_before_result

slices = json.loads((EVIDENCE / 'historical-slices.json').read_text(encoding='utf-8'))
reports = list(slices['provider_corpus_integration']['reports'].values()) + [slices['background_probe_contract']['related']]
observations = []
for entry in reports:
    path = REPO / entry['path']
    observation = {'path': entry['path'], 'exists': path.exists()}
    if path.exists():
        raw = path.read_bytes()
        obj = json.loads(raw)
        rows = [row for group in obj.get('reports', []) for row in group.get('rows', [])]
        observation.update(sha256=hashlib.sha256(raw).hexdigest(), recorded_sha256=entry['sha256'],
                           complete=obj.get('complete'), successful=obj.get('successful'),
                           selected=obj.get('selected'), rows=rows, counts=dict(Counter(row['outcome'] for row in rows)),
                           changed_during_run=obj.get('changed_during_run'))
    observations.append(observation)
write(EVIDENCE / 'historical-reports.json', observations)

historical = json.loads((EVIDENCE / 'historical-background.json').read_text(encoding='utf-8'))
source = REPO / historical['entry']['source']
case = source.parent.parent
destination = EVIDENCE / 'historical-background-source'
destination.mkdir()
files = {}
for name in ('report.json', 'workspace/completed.txt', 'workspace/phase-pending.json',
             'evidence/stdout.jsonl', 'evidence/stderr.txt', 'evidence/worker-status.json',
             'evidence/input.txt', 'evidence/output.schema.json', 'evidence/request.json'):
    path = case / name
    files[name] = {'exists': path.exists()}
    if path.exists():
        raw = path.read_bytes()
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
        files[name]['sha256'] = hashlib.sha256(raw).hexdigest()
report = json.loads((case / 'report.json').read_bytes())
parsed = parse_stream(source.read_bytes())
collected = report['result']['execution']['collect']
final = parsed['structured_output']
changes = {}
for name in ('probe_cli.py', 'do_math/claude_stream.py', 'do_math/model_runner.py',
             'do_math/claude_worker.py', 'do_math/codex_adapter.py', 'do_math/cli_execution.py'):
    path = '.claude/skills/do-math/scripts/' + name
    before = subprocess.check_output(['git', 'show', '87fd1c1b:' + path], cwd=REPO)
    after = (REPO / path).read_bytes()
    changes[name] = {'b87_sha256': hashlib.sha256(before).hexdigest(), 'current_sha256': hashlib.sha256(after).hexdigest(),
                     'same_bytes': before == after}
review = {'files': files, 'source': str(case), 'historical_passed': report['passed'],
          'historical_checks': report['checks'], 'current_background_predicate': background_completed_before_result(parsed),
          'raw_matches_corpus': files['evidence/stdout.jsonl']['sha256'] == historical['entry']['source_sha256'],
          'file_matches_selected_nonce': (case / 'workspace/completed.txt').read_text(encoding='utf-8').strip() == final['nonce'],
          'worker_status': collected['worker_status'], 'termination_barrier': collected['termination_barrier'],
          'selected_result': parsed['selected_result'], 'background_events': parsed['background_events'],
          'current_sources': changes}
write(EVIDENCE / 'background-reuse-review.json', json_safe(review))
print(json.dumps({key: review[key] for key in ('historical_passed', 'historical_checks', 'current_background_predicate',
                                              'raw_matches_corpus', 'file_matches_selected_nonce', 'termination_barrier',
                                              'current_sources')}, ensure_ascii=False))
