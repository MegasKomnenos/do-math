import json
import subprocess
from pathlib import Path
from task_driver import E, REPO, RUN, read, sha, write

commands = [
    ('history-job-origin', ['git','show','116cff28','--','.claude/skills/do-math/scripts/do_math/windows_job.py']),
    ('history-job-port', ['git','show','0b05e8ab','--','.claude/skills/do-math/scripts/tests/contracts/test_port_jobs.py',
                         '.claude/skills/do-math/scripts/tests/boundary/test_port_jobs.py',
                         '.claude/skills/do-math/scripts/do_math/windows_job.py']),
    ('history-job-migration', ['git','show','23cc4df3','--','.claude/skills/do-math/scripts/tests/boundary/test_scheduling_windows_job.py']),
]
for label, argv in commands:
    p = subprocess.run(argv, cwd=REPO, capture_output=True)
    (E/(label+'.stdout')).write_bytes(p.stdout)
    (E/(label+'.stderr')).write_bytes(p.stderr)
    write(E/(label+'.command.json'), {'argv':argv,'cwd':str(REPO),'exit_code':p.returncode})
    assert p.returncode == 0 and p.stdout
old = RUN/'phases/017/tasks/t4-baseline-integration/evidence'
refs = ['.claude/skills/do-math/scripts/tests/boundary/test_shared_input_provenance.py',
        '.agents/skills/do-math/scripts/tests/boundary/test_shared_input_provenance.py',
        '.claude/skills/do-math/scripts/tests/support/adapter_coverage.py',
        '.agents/skills/do-math/scripts/tests/support/adapter_coverage.py',
        '.claude/skills/do-math/scripts/tests/support/branch_gate.py',
        '.agents/skills/do-math/scripts/tests/support/branch_gate.py',
        '.claude/skills/do-math/scripts/run_tests.py',
        '.agents/skills/do-math/scripts/run_tests.py']
start = read(E/'source-start.json')
old_start = read(RUN/'phases/017/manager-evidence/source-inspected.json')
for p in refs: assert sha(REPO/p) == start[p] == old_start[p]
raw_files = {p.relative_to(old).as_posix():sha(p) for p in old.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
write(E/'previous-evidence-start.json',raw_files)
write(E/'raw-reuse-basis.json', {'unchanged_current_definitions':{p:start[p] for p in refs},
    'previous_evidence_files':len(raw_files),'companion_manifest_sha256':sha(old/'companion-manifest.json'),
    'baseline_manifest_sha256':sha(RUN/'phases/016/tasks/provenance-baseline/evidence/baseline-manifest.json'),
    'scope':'017 canonical actual TestCase/WORKER/SNAPSHOT companion and measurement evidence only; mirror execution is new and separate; no mirror companion raw claim.'})
print('History slices saved; raw-reuse inputs unchanged;',len(raw_files),'previous evidence files hashed.')
