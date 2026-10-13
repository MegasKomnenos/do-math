"""Task-local observations; no product writes or paid calls."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from run_command import ROOT, EVIDENCE, snapshot, write_json, changed

RUN = ROOT / 'docs/do-math/continuous-development-2026-10-13'
sys.path.insert(0, str(ROOT / '.claude/skills/do-math/scripts'))


def main():
    sources = snapshot()
    write_json(EVIDENCE / 'source-start.json', sources)
    previous = json.loads((RUN / 'phases/005/tasks/corpus-git-bytes/evidence/source-final.json').read_bytes())
    state = {'against_phase005': changed(previous, sources), 'sources': len(sources)}
    for key, argv in [('head', ['git', 'rev-parse', 'HEAD']),
                      ('status', ['git', 'status', '--porcelain=v1', '--untracked-files=all'])]:
        result = subprocess.run(argv, cwd=ROOT, capture_output=True)
        state[key] = {'argv': argv, 'exit_code': result.returncode,
                      'stdout': result.stdout.decode('utf-8'), 'stderr': result.stderr.decode('utf-8')}
    write_json(EVIDENCE / 'start-state.json', state)
    print(json.dumps({'sources': len(sources), 'against_phase005': state['against_phase005'],
                      'head': state['head']['stdout'].strip()}, ensure_ascii=False))
    phase = json.loads((RUN / 'phases/006/phase.json').read_bytes())
    observations = {}
    for ref in phase['tasks'][0]['inputs']:
        base, rel = ref.split(':', 1)
        path = (RUN if base == 'run' else ROOT) / rel
        raw = path.read_bytes()
        row = {'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}
        if path.suffix == '.json':
            data = json.loads(raw)
            if 'report.json' == path.name and 'narrative' in data:
                row['report'] = data
                print(ref, json.dumps({k: data[k] for k in ('status', 'narrative', 'findings')}, ensure_ascii=False))
            elif 'selected' in data:
                row['run'] = {k: v for k, v in data.items() if k != 'source_sha256'}
                print(ref, json.dumps({k: data.get(k) for k in ('selected','counts','complete','successful','changed_during_run')}, ensure_ascii=False))
            elif path.name == 'prior-review-state.json':
                row['keys'] = list(data)
                print(ref, 'keys:', list(data))
            else:
                row['keys'] = list(data) if isinstance(data, dict) else None
        observations[ref] = row
    write_json(EVIDENCE / 'input-observations.json', observations)
    from do_math.contracts import action_schema
    from do_math.supervision import repair_report_schema
    schemas = {'maintenance': action_schema({'role': 'maintenance'}),
               'repair_undiagnosed': repair_report_schema(diagnosed=False),
               'repair_diagnosed': repair_report_schema(diagnosed=True)}
    write_json(EVIDENCE / 'caller-schemas.json', schemas)
    for name, schema in schemas.items():
        print(name, json.dumps(schema, ensure_ascii=False))


if __name__ == '__main__':
    main()
