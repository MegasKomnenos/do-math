"""Isolated Codex CLI task queue. Terminal claims await human/root evidence review."""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SERVICE = ROOT / 'services/scholarly-mcp'
PYTHON = SERVICE / '.venv/Scripts/python.exe'
CODEX = Path(shutil.which('codex') or 'codex')


def now():
    return datetime.now(timezone.utc).isoformat()


def write_json(path, data):
    temporary = path.with_name(path.name + '.new')
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    temporary.replace(path)


def read_json(path):
    return json.loads(path.read_text('utf-8'))


def result_schema():
    string = {'type': 'string'}
    strings = {'type': 'array', 'items': string}
    properties = {
        'task_id': string, 'disposition': {'type': 'string', 'enum': ['completed', 'exhausted', 'incomplete']},
        'summary': string, 'report_path': string, 'experiments_path': string, 'visual_review_path': string,
        'changed_files': strings, 'evidence_paths': strings, 'remaining_executable_methods': strings,
        'exhaustion_reason': string,
        'tests': {'type': 'array', 'items': {'type': 'object', 'additionalProperties': False,
            'properties': {'command': string, 'result': string, 'kind': {'type': 'string', 'enum': ['live', 'offline', 'mock']}},
            'required': ['command', 'result', 'kind']}}
    }
    return {'type': 'object', 'additionalProperties': False, 'properties': properties, 'required': list(properties)}


def prepare():
    tasks = read_json(HERE / 'tasks.json')
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    public = SERVICE / 'data/dispatch' / stamp
    private = ROOT / '.credentials/scholarly-mcp/probes/cli-dispatch' / stamp
    public.mkdir(parents=True)
    private.mkdir(parents=True)
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    archive = subprocess.check_output(['git', 'archive', '--format=zip', commit, 'services/scholarly-mcp'], cwd=ROOT)
    contract = (HERE / 'contract.md').read_text('utf-8')
    write_json(public / 'result-schema.json', result_schema())
    rows = []
    for task in tasks:
        output = public / task['id']
        home = private / task['id']
        workspace = home / 'workspace'
        credentials = home / 'credentials'
        for path in (output, workspace, credentials / 'scholarly-mcp', home / 'artifacts'):
            path.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(io.BytesIO(archive)) as bundle:
            for item in bundle.infolist():
                target = (workspace / item.filename).resolve()
                if not target.is_relative_to(workspace.resolve()):
                    raise ValueError('Archive path outside workspace')
            bundle.extractall(workspace)
        # Credential bytes stay in protected per-task copies, never in prompts or output.
        for relative in ('kudos.md', 'scholarly-mcp/kudos.json', 'scholarly-mcp/kudos-firefox.json', 'scholarly-mcp/kudos-chromium.json'):
            source = ROOT / '.credentials' / relative
            if source.exists():
                shutil.copyfile(source, credentials / relative)
        base = workspace / 'services/scholarly-mcp'
        baseline = {str(p.relative_to(base)): hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in base.rglob('*') if p.is_file()}
        write_json(home / 'baseline.json', baseline)
        paths = {'workspace': str(workspace), 'service_copy': str(base), 'private_dir': str(home),
                 'credential_root': str(credentials), 'data_dir': str(home / 'artifacts'),
                 'output_dir': str(output), 'python': str(PYTHON), 'base_commit': commit}
        prompt = (contract + '\n\n## 이 세션의 개별 임무\n\n' + json.dumps(task, ensure_ascii=False, indent=2)
                  + '\n\n## 이 세션의 실제 경로\n\n' + json.dumps(paths, ensure_ascii=False, indent=2)
                  + '\n\n지금 위 임무의 작업을 시작하고 종료 조건이 충족될 때까지 수행하라. 다른 과제나 원본 저장소를 수정하지 마라.\n')
        (output / 'prompt.md').write_text(prompt, encoding='utf-8')
        write_json(output / 'progress.json', {'task_id': task['id'], 'state': 'queued', 'updated_at': now()})
        rows.append({**task, **paths, 'state': 'queued', 'attempts': 0, 'thread_id': None,
                     'thread_ids': [], 'pid': None, 'retry_at': 0, 'last_exit': None})
    state = {'created_at': now(), 'updated_at': now(), 'base_commit': commit, 'model': 'gpt-5.6-sol',
             'reasoning': 'high', 'max_parallel': 8, 'private_dir': str(private),
             'runner_pid': None, 'tasks': rows}
    write_json(public / 'state.json', state)
    write_json(HERE / 'latest.json', {'campaign': str(public), 'created_at': now()})
    lines = ['# 개별 Codex CLI 파견 목록', '',
             '각 행은 별도 세션이다. 동시 실행은 최대8개이며 같은 자료원은 순서대로 실행한다. 실행 상태는 state.json을 따른다.', '',
             '| 작업 ID | 분리한 기능 | 상태 유형 | 파견문 |', '|---|---|---|---|']
    lines += [f"| {t['id']} | {t['title']} | {t['kind']} | [{t['id']}/prompt.md]({t['id']}/prompt.md) |" for t in rows]
    (public / 'INDEX.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(json.dumps({'campaign': str(public), 'tasks': len(rows), 'base_commit': commit}, ensure_ascii=False))
    return public


def invocation(task, state, campaign):
    output = Path(task['output_dir'])
    home = Path(task['private_dir'])
    attempt = task['attempts'] + 1
    last = home / f'attempt-{attempt:03d}-last.json'
    options = ['--ignore-user-config', '-m', state['model'], '-c', 'model_reasoning_effort="high"',
               '-c', 'approval_policy="never"', '-c', 'mcp_servers={}',
               '--json', '--output-schema', str(campaign / 'result-schema.json'), '-o', str(last)]
    if task['thread_id']:
        command = [str(CODEX), 'exec', 'resume', *options, task['thread_id'], '-']
        prompt = (f"미완료 작업 {task['id']}을 같은 세션에서 계속한다. 원 파견문 {output / 'prompt.md'}와 "
                  f"{output / 'progress.json'}를 먼저 확인하라. 이전 반환은 완료로 수용되지 않았다. "
                  f"반환 문제: {task.get('return_problem', '실행이 정상 완료되지 않음')}. "
                  "이미 받은 자료와 사본 변경을 보존해 이어가라. 해결하거나 실행 가능한 방법을 근거로 모두 소진하기 전에는 최종 반환하지 마라. "
                  "실제 새 화면을 직접 열어 판독하고 원 요청·응답·파일과 대조하라. 보고의 누락만 고치는 것으로 남은 구현·검증을 대신하지 마라.")
    else:
        command = [str(CODEX), 'exec', *options, '--sandbox', 'danger-full-access', '-C', str(ROOT), '-']
        prompt = (output / 'prompt.md').read_text('utf-8')
    return command, prompt, last


def thread_from_log(path):
    if not path.exists():
        return None
    with path.open('r', encoding='utf-8', errors='replace') as stream:
        for _ in range(30):
            line = stream.readline()
            if not line:
                break
            try:
                item = json.loads(line)
            except ValueError:
                continue
            if item.get('type') == 'thread.started':
                return item.get('thread_id')
    return None


def check_claim(task, result):
    if result.get('task_id') != task['id']:
        return 'task_id 불일치'
    if result.get('disposition') not in ('completed', 'exhausted'):
        return '최종 처분이 incomplete 또는 누락'
    if result.get('remaining_executable_methods'):
        return '실행 가능한 미시도 방법이 남음'
    output = Path(task['output_dir']).resolve()
    for key in ('report_path', 'experiments_path', 'visual_review_path'):
        value = result.get(key)
        if not isinstance(value, str):
            return key + ' 누락'
        path = Path(value).resolve()
        if not path.is_relative_to(output) or not path.is_file() or not path.stat().st_size:
            return key + ' 실제 파일 부재 또는 경로 범위 위반'
    try:
        experiments = read_json(Path(result['experiments_path']))
    except (OSError, ValueError):
        return '실험 원장이 유효한 JSON 아님'
    if not isinstance(experiments, list) or not experiments or not any(x.get('executed') is True for x in experiments if isinstance(x, dict)):
        return '실행된 실험 근거 없음'
    evidence = result.get('evidence_paths')
    if not evidence or any(not Path(p).is_file() for p in evidence):
        return '실제 근거 파일 누락'
    if not any(Path(p).suffix.lower() in ('.png', '.jpg', '.jpeg', '.webp') for p in evidence):
        return '직접 화면 판독에 대응하는 이미지 근거 파일 누락'
    if result['disposition'] == 'exhausted' and not result.get('exhaustion_reason', '').strip():
        return '소진 이유 없음'
    if result['disposition'] == 'completed' and not any(t.get('kind') == 'live' for t in result.get('tests', [])):
        return '실서비스 검증 기록 없음'
    return None


class AdoptedProcess:
    """Monitor an existing owned CLI without interrupting or duplicating it."""
    def __init__(self, task):
        import psutil
        self.process = psutil.Process(task['pid'])
        arguments = self.process.cmdline()
        expected = str(Path(task['last_output_path'])).casefold()
        if self.process.name().casefold() != 'codex.exe' or expected not in [argument.casefold() for argument in arguments]:
            raise ValueError('Existing process identity mismatch')
        self.returncode = None

    def poll(self):
        import psutil
        try:
            result = self.process.wait(timeout=0)
        except psutil.TimeoutExpired:
            return None
        self.returncode = result if result is not None else 0
        return self.returncode


def run(campaign):
    state_path = campaign / 'state.json'
    state = read_json(state_path)
    lock = Path(state['private_dir']) / 'runner.lock'
    # Hold an OS file lock so two controllers cannot duplicate a live job.
    lock_stream = lock.open('a+b')
    if os.name == 'nt':
        import msvcrt
        lock_stream.seek(0)
        if not lock.read_bytes():
            lock_stream.write(b'0'); lock_stream.flush(); lock_stream.seek(0)
        msvcrt.locking(lock_stream.fileno(), msvcrt.LK_NBLCK, 1)
    state['runner_pid'] = os.getpid()
    active = {}
    # Transfer supervision only after checking the exact existing CLI invocation.
    for task in state['tasks']:
        if task['state'] == 'running':
            try:
                process = AdoptedProcess(task)
                home = Path(task['private_dir'])
                log_path = home / f"attempt-{task['attempts']:03d}-events.jsonl"
                active[task['id']] = (process, io.BytesIO(), io.BytesIO(), log_path, Path(task['last_output_path']))
                task['supervision_adopted_at'] = now()
            except Exception as error:
                task.update(state='controller_recovery_required', return_problem='실행 신원 확인 실패: '+type(error).__name__)
    while True:
        limits = campaign / 'limits.json'
        if limits.exists():
            maximum = read_json(limits).get('max_parallel')
            if type(maximum) is int and maximum > 0:
                state['max_parallel'] = maximum
        for task_id, running in list(active.items()):
            process, log_stream, err_stream, log_path, last_path = running
            task = next(t for t in state['tasks'] if t['id'] == task_id)
            thread = thread_from_log(log_path)
            if thread:
                task['thread_id'] = thread
                if thread not in task['thread_ids']:
                    task['thread_ids'].append(thread)
            if process.poll() is None:
                continue
            log_stream.close(); err_stream.close()
            task.update(pid=None, last_exit=process.returncode, attempt_finished_at=now())
            try:
                result = read_json(last_path)
                problem = check_claim(task, result)
            except (OSError, ValueError, TypeError, AttributeError, KeyError) as error:
                result = None
                problem = '최종 구조화 결과 읽기 실패: ' + type(error).__name__
            if process.returncode == 0 and problem is None:
                write_json(Path(task['output_dir']) / 'result.json', result)
                task.update(state='awaiting_review', claimed_disposition=result['disposition'], return_problem=None)
            else:
                task.update(state='resume_queued', return_problem=problem or 'CLI 비정상 종료',
                            retry_at=time.time() + min(300, 30 * task['attempts']))
            del active[task_id]
        busy_sources = {next(t['source'] for t in state['tasks'] if t['id'] == key) for key in active}
        for task in state['tasks']:
            if len(active) >= state['max_parallel']:
                break
            if task['state'] not in ('queued', 'resume_queued') or task['source'] in busy_sources or task['retry_at'] > time.time():
                continue
            command, prompt, last = invocation(task, state, campaign)
            number = task['attempts'] + 1
            home = Path(task['private_dir'])
            log_path = home / f'attempt-{number:03d}-events.jsonl'
            log_stream = log_path.open('wb')
            err_stream = (home / f'attempt-{number:03d}-stderr.log').open('wb')
            try:
                process = subprocess.Popen(command, cwd=ROOT, stdin=subprocess.PIPE, stdout=log_stream,
                    stderr=err_stream, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
                process.stdin.write(prompt.encode('utf-8'))
                process.stdin.close()
            except OSError as error:
                log_stream.close(); err_stream.close()
                task.update(state='resume_queued', attempts=number, retry_at=time.time()+60,
                            return_problem='CLI 시작 실패: '+type(error).__name__)
                # A configuration/startup failure is likely shared; do not cascade
                # the same broken invocation through every queued task in this tick.
                break
            task.update(state='running', attempts=number, pid=process.pid, attempt_started_at=now(), last_output_path=str(last), return_problem=None)
            active[task['id']] = (process, log_stream, err_stream, log_path, last)
            busy_sources.add(task['source'])
        state['updated_at'] = now()
        write_json(state_path, state)
        if not active and all(t['state'] in ('awaiting_review', 'controller_recovery_required') for t in state['tasks']):
            state['runner_finished_at'] = now()
            write_json(state_path, state)
            break
        time.sleep(5)


def launch(campaign):
    state = read_json(campaign / 'state.json')
    private = Path(state['private_dir'])
    with (private/'controller.stdout.log').open('ab') as stdout, (private/'controller.stderr.log').open('ab') as stderr:
        process = subprocess.Popen([str(PYTHON), str(__file__), 'run', '--campaign', str(campaign)],
            cwd=ROOT, stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr,
            creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0) | getattr(subprocess,'CREATE_NEW_PROCESS_GROUP',0))
    print(json.dumps({'controller_pid':process.pid,'campaign':str(campaign)},ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['prepare', 'launch', 'run', 'status', 'limit'])
    parser.add_argument('--campaign', type=Path)
    parser.add_argument('--max-parallel', type=int)
    args = parser.parse_args()
    if args.command == 'prepare':
        prepare(); return
    campaign = args.campaign or Path(read_json(HERE/'latest.json')['campaign'])
    if args.command == 'limit':
        if args.max_parallel is None or args.max_parallel < 1:
            parser.error('--max-parallel must be positive')
        write_json(campaign/'limits.json', {'max_parallel':args.max_parallel,'updated_at':now()})
        print(json.dumps({'max_parallel':args.max_parallel,'campaign':str(campaign)},ensure_ascii=False))
    elif args.command == 'launch':
        launch(campaign)
    elif args.command == 'run':
        run(campaign)
    else:
        state = read_json(campaign/'state.json')
        print(json.dumps({'campaign':str(campaign),'runner_pid':state['runner_pid'],'updated_at':state['updated_at'],
            'tasks':[{key:t.get(key) for key in ('id','state','pid','thread_id','attempts','claimed_disposition','return_problem')} for t in state['tasks']]},ensure_ascii=False,indent=2))


if __name__ == '__main__':
    main()
