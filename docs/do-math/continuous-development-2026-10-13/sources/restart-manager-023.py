"""Operator-requested restart of phase 023 manager; never rerun its completed task."""
import datetime
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

RECORDS = Path(__file__).resolve().parents[1]
REPO = RECORDS.parents[2]
PHASE = RECORDS / 'phases/023'
RECEIPT = RECORDS / 'runtime/restart-manager-023.json'
LOG = PHASE / 'logs/manager-restart-001.log'

def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

state = {'state': 'starting', 'phase': '023', 'controller_pid': os.getpid(),
         'started_at': now(), 'log': str(LOG),
         'previous_log': str(PHASE / 'logs/manager.log'),
         'reason': 'User requested restart after manager provider capacity failure; task is retained.'}

def save(**changes):
    state.update(changes)
    temporary = RECEIPT.with_suffix('.tmp')
    temporary.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding='utf-8')
    temporary.replace(RECEIPT)

if (PHASE / 'manager.json').exists() or LOG.exists():
    raise RuntimeError('Manager already submitted or restart log exists; inspect before restarting')
with RECEIPT.open('x', encoding='utf-8') as stream:
    json.dump(state, stream, ensure_ascii=False, indent=2)
try:
    check = [sys.executable, '-B', str(REPO / 'services/continuous-development/check.py')]
    subprocess.run([*check, 'report', str(REPO), str(RECORDS), '023', 'document-governance'],
                   cwd=REPO, check=True)
    selection = json.loads((RECORDS / 'settings.json').read_text(encoding='utf-8-sig'))['manager']
    codex = shutil.which('codex.exe')
    if not codex:
        raise RuntimeError('Native Codex executable is missing')
    command = [codex, 'exec', '--sandbox', 'danger-full-access', '-c', 'approval_policy="never"',
               '--model', selection['model'], '-c', 'model_reasoning_effort=' + json.dumps(selection['effort']),
               '-C', str(REPO), '--add-dir', str(RECORDS), '-']
    prompt = (f'역할: manager\n프로젝트 루트: {REPO}\n실행 기록 루트: {RECORDS}\n'
              f'phase: 023\ntask: -\nPython: {sys.executable}\n'
              f'{REPO / "services/continuous-development/protocol.md"}를 읽고 지정된 역할의 절차를 수행한다.\n'
              '사용자가 재시작을 요청했다. 이전 manager는 503/model capacity 오류로 종료되어 manager.json이 없다. '
              '완료된 document-governance task를 다시 실행하지 말고 원 report/evidence와 현재 파일을 검수한다. '
              '이전 manager.log와 미완성 관리 자료를 보존하고 실제 현황을 확인해 관리 절차를 마감한다. '
              '이번 로그는 logs/manager-restart-001.log다. context의 모델 정책과 문서 묶음 지시를 적용한다.\n')
    with LOG.open('xb') as stream:
        manager = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=stream,
                                   stderr=subprocess.STDOUT, cwd=REPO)
        save(state='manager_running', manager_pid=manager.pid, command=command)
        manager.communicate(prompt.encode('utf-8'))
    save(state='manager_exited', manager_exit_code=manager.returncode)
    if manager.returncode != 0:
        raise RuntimeError(f'Manager exited {manager.returncode}; inspect preserved restart log')
    decision = json.loads((PHASE / 'manager.json').read_text(encoding='utf-8-sig'))
    following = decision['next']
    save(state='continuing' if following is not None else 'exited', next_phase=following)
    if following is not None:
        # Existing launcher checks the next phase and rejects any phase with execution records.
        result = subprocess.run([sys.executable, '-u', '-B', str(RECORDS / 'start.py'),
                                 '--phase', following], cwd=REPO)
        if result.returncode:
            raise RuntimeError(f'Next-phase launcher exited {result.returncode}')
    save(state='exited', exit_code=0, finished_at=now())
except BaseException as error:
    save(state='error', error=repr(error), finished_at=now())
    raise
