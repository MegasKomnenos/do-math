"""Prepare manager-owned phase010 assignment metadata."""
import json
from pathlib import Path
ROOT = Path(r'C:\math')
RUN = ROOT/'docs/do-math/continuous-development-2026-10-13'
OUT = Path(__file__).resolve().parent
files = ['scripts/tests/smoke/test_host_live.py', 'scripts/tests/support/host_live.py',
         'scripts/tests/boundary/test_scheduling_windows_job.py',
         'scripts/tests/boundary/test_scheduling_owned_job_children.py',
         'scripts/tests/boundary/test_role_input_snapshot_reach.py',
         'scripts/tests/시험-지침.md', 'scripts/tests/.timings.json']
common = ['run:sources/user-decisions.md','run:sources/model-policy-2026-10-14.md',
          'repo:.claude/skills/do-math/AGENTS.md',
          'repo:docs/do-math/시험-재편-2026-09-29/설계.md',
          'repo:docs/do-math/시험-재편-2026-09-29/조사/결함-범주.md']
host = ['run:phases/009/manager-evidence/verification.json','run:phases/009/manager-evidence/review.md',
        'run:phases/001/tasks/closure-map/evidence/prior-review-state.json',
        'run:phases/001/tasks/gate-readiness/evidence/gate-readiness.json',
        'repo:.claude/skills/writing-skills/references/멀티런타임_동기화.md']
host += ['repo:.claude/skills/do-math/'+p for p in [
    'scripts/tests/시험-지침.md','scripts/이음새-정본.md','scripts/do_math/windows_job.py',
    'scripts/do_math/wiring.py','scripts/do_math/cli_worker.py','scripts/do_math/powershell_scheduler.py',
    'scripts/tests/support/port_contracts/jobs.py','scripts/tests/support/provider_live.py',
    'scripts/tests/boundary/test_scheduling_windows_job.py',
    'scripts/tests/boundary/test_scheduling_owned_job_children.py',
    'scripts/tests/boundary/test_scheduling_call_jobs.py',
    'scripts/tests/boundary/test_role_input_snapshot_reach.py',
    'scripts/tests/boundary/test_operator_schedule_adapter.py']]
reading = ['run:phases/001/tasks/document-closeout/evidence/followup-packets.json',
           'run:phases/001/tasks/document-closeout/evidence/binding-inventory.json',
           'run:phases/001/tasks/document-closeout/evidence/review-notes.md']
reading += ['repo:.claude/skills/do-math/'+p for p in [
    'SKILL.md','references/초기화-운전.md','계약/독립-운영.md','scripts/do_math/contracts.py',
    'scripts/do_math/context_store.py','scripts/do_math/cli_worker.py']]
phase = {'kind':'work','purpose':'실제 Windows Job·pythonw T5 연결과 운전 문서 읽기 한도 L01 조사를 독립 수행한다. 시험·공유 캐시는 host-smoke만 소유한다.',
         'tasks':[
             {'id':'host-smoke','model':'gpt-6.1-sol','effort':'high','inputs':common+host,
              'writes':[tree+'/skills/do-math/'+p for tree in ('.claude','.agents') for p in files],
              'provides':[],'uses':[]},
             {'id':'reading-limits','model':'gpt-6.1-sol','effort':'high','inputs':common+reading,
              'writes':[],'provides':[],'uses':[]}]}
(RUN/'phases/010/phase.json').write_text(json.dumps(phase,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='')
for rel in ['logs','tasks/host-smoke/evidence','tasks/reading-limits/evidence']:
    (RUN/'phases/010'/rel).mkdir(parents=True,exist_ok=True)
print('Prepared phase010 assignments.')

