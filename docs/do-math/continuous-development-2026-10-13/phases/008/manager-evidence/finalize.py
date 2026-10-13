"""Validate the handoff, publish atomically, then let the manager stage exact files."""
import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(r'C:\math')
RUN = ROOT / 'docs/do-math/continuous-development-2026-10-13'
OUT = Path(__file__).resolve().parent

def execute(argv):
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    result = subprocess.run(argv, cwd=ROOT, capture_output=True)
    return {'argv': argv, 'cwd': str(ROOT), 'started_at': started,
            'ended_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'exit_code': result.returncode, 'stdout': result.stdout.decode('utf-8'),
            'stderr': result.stderr.decode('utf-8')}

def main():
    pending, published = RUN / 'phases/008/manager.pending.json', RUN / 'phases/008/manager.json'
    assert pending.is_file() and not published.exists()
    command = [sys.executable, '-B', str(ROOT / 'services/continuous-development/check.py'),
               'handoff', str(ROOT), str(RUN), '008']
    gates = [execute([sys.executable, '-B', str(ROOT / '기억/scripts/validate_memory_index.py')]), execute(command)]
    (OUT / 'gates.json').write_text(json.dumps(gates, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    assert all(row['exit_code'] == 0 for row in gates), gates
    preserve = execute([sys.executable, '-B', str(OUT / 'preserve.py')])
    assert preserve['exit_code'] == 0, preserve
    files = [RUN / p for p in ('context.md', 'plan.md', 'seams.md', 'phases/008/phase.json',
             'phases/008/tasks/document-recovery/objective.md', 'phases/008/tasks/document-recovery/report.json',
             'phases/009/phase.json', 'phases/009/tasks/document-callable/objective.md')]
    files.append(pending)
    before = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    checked = execute(command)
    assert checked['exit_code'] == 0, checked
    assert before == {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    pending.rename(published)
    (OUT / 'finalize.json').write_text(json.dumps({'preserve': preserve, 'handoff': checked,
        'input_sha256': before, 'published': str(published)}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(checked['stdout'].strip())
    print('Published:', published)
    print(preserve['stdout'].strip())

if __name__ == '__main__':
    main()
