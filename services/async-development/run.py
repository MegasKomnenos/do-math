"""Dispatch ready tasks; run one manager without pausing unrelated workers."""
import argparse
import contextlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

from workspaces import prepare, read_json, write_json

ENGINE=Path(__file__).resolve().parent


@contextlib.contextmanager
def runner_lock(path):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('a+b') as lock:
        lock.seek(0);lock.write(b'0');lock.flush();lock.seek(0)
        if os.name=='nt':
            import msvcrt
            msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
        else:
            import fcntl
            fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        try:yield
        finally:
            lock.seek(0)
            if os.name=='nt':msvcrt.locking(lock.fileno(),msvcrt.LK_UNLCK,1)
            else:fcntl.flock(lock,fcntl.LOCK_UN)


def alive(pid):
    if not pid:return False
    if os.name=='nt':
        import ctypes
        from ctypes import wintypes
        k=ctypes.WinDLL('kernel32',use_last_error=True)
        k.OpenProcess.argtypes=[wintypes.DWORD,wintypes.BOOL,wintypes.DWORD];k.OpenProcess.restype=wintypes.HANDLE
        k.GetExitCodeProcess.argtypes=[wintypes.HANDLE,ctypes.POINTER(wintypes.DWORD)]
        k.CloseHandle.argtypes=[wintypes.HANDLE]
        h=k.OpenProcess(0x1000,False,pid)
        if not h:return ctypes.get_last_error()==5
        try:
            code=wintypes.DWORD()
            return bool(k.GetExitCodeProcess(h,ctypes.byref(code))) and code.value==259
        finally:k.CloseHandle(h)
    try:os.kill(pid,0);return True
    except ProcessLookupError:return False
    except PermissionError:return True


class WindowsWorker:
    """An existing worker retained during an explicit dispatcher handover."""
    def __init__(self,pid):
        if os.name!='nt':raise ValueError('--adopt-workers currently supports Windows only')
        import ctypes
        from ctypes import wintypes
        self.api=ctypes.WinDLL('kernel32',use_last_error=True);self.ctypes=ctypes;self.wintypes=wintypes
        self.api.OpenProcess.argtypes=[wintypes.DWORD,wintypes.BOOL,wintypes.DWORD]
        self.api.OpenProcess.restype=wintypes.HANDLE
        self.api.GetExitCodeProcess.argtypes=[wintypes.HANDLE,ctypes.POINTER(wintypes.DWORD)]
        self.api.CloseHandle.argtypes=[wintypes.HANDLE]
        self.handle=self.api.OpenProcess(0x1000,False,pid)
        if not self.handle:raise ctypes.WinError(ctypes.get_last_error())
        self.pid=pid;self.returncode=None

    def poll(self):
        if self.returncode is not None:return self.returncode
        code=self.wintypes.DWORD()
        if not self.api.GetExitCodeProcess(self.handle,self.ctypes.byref(code)):
            raise self.ctypes.WinError(self.ctypes.get_last_error())
        if code.value!=259:
            self.returncode=code.value;self.api.CloseHandle(self.handle)
        return self.returncode


def selected(command, selection):
    result=list(command)
    if 'model' in selection:result+=['--model',selection['model']]
    if 'effort' in selection:result+=['-c','model_reasoning_effort='+json.dumps(selection['effort'])]
    return result


def bootstrap(session):
    principles=(ENGINE/'principles.md').read_text(encoding='utf-8-sig')
    role=session['role']
    instructions=(
        '프로젝트 목적은 현재 context와 사용자 요구로 판단한다. '
        '목적에 불필요한 구조와 제약은 제거하거나 축소한다.\n'
        f'{ENGINE / "protocol.md"}의 {role} 절차를 읽는다.\n'
    )
    if role=='manager':
        instructions+=(f'공용 context.md, plan.md, seams.md와 {session["inbox"]}를 읽는다. '
            '다른 task는 계속 실행 중일 수 있다. 진행 중 task의 배정을 바꾸지 않는다. '
            '새 결과의 변경 파일을 검토하고 workspaces.py integrate로 반영한 뒤 accepted에 넣는다. '
            '자잘한 보완은 묶고 독립 후속 기능은 바로 준비한다. 새 task는 objective.md와 queue entry를 작성한다. '
            '공용 문서를 먼저 갱신하고 check.py queue RECORDS QUEUE_PENDING_FILE로 제출할 배정을 확인한다. '
            'queue.json은 검사한 임시파일에서 원자 교체해 마지막으로 게시한다. '
            '제품 코드 수정은 task에 맡기고 공용 맥락/계획/배정을 갱신한다.\n')
    else:
        home=Path(session['records'])/'tasks'/session['task']
        instructions+=(f'{home / "inputs"}의 context.md, plan.md, seams.md와 '
            f'{home / "task.json"}, {home / "objective.md"}를 읽는다. '
            '소스 수정/시험은 workspace에서 수행하고 canonical source_repo 및 다른 task의 파일은 수정하지 않는다. '
            'inputs에 명시한 원자료는 필요한 부분을 읽는다. 공용 정의를 재발명하지 않는다. '
            '작업의 실제 완료/부분완료/차단을 report.json에 기록하고 check.py report를 직접 실행한다. '
            'review task는 사용자 요구와 실제 결과를 대조하고 제품을 수정하지 않는다.\n')
    return 'SESSION_JSON='+json.dumps(session,ensure_ascii=False)+'\n'+principles+'\n'+instructions


def start(command, session, cwd, log_path):
    log_path.parent.mkdir(parents=True,exist_ok=True)
    prompt=bootstrap(session)
    log_path.with_suffix('.prompt.md').write_text(prompt,encoding='utf-8')
    log=log_path.open('xb')
    try:
        proc=subprocess.Popen([*command,'-C',str(cwd),'--add-dir',session['records'],'-'],
            stdin=subprocess.PIPE,stdout=log,stderr=subprocess.STDOUT,cwd=cwd)
        proc.stdin.write(prompt.encode('utf-8'));proc.stdin.close()
    except BaseException:
        log.close();raise
    return proc,log


def run(repo, records, *, adopt_workers=False):
    repo=Path(repo).resolve();records=Path(records).resolve();records.mkdir(parents=True,exist_ok=True)
    settings=read_json(records/'settings.json');limit=settings.get('max_workers',3)
    if not isinstance(limit,int) or limit<1:raise ValueError('max_workers must be positive')
    command=settings.get('command',['codex','exec','--json'])
    state_path=records/'state.json'
    with runner_lock(records/'runner.lock'):
        state=read_json(state_path) if state_path.exists() else dict(tasks={},manager=None,pending=[],manager_number=0)
        state.update(repo=str(repo),runner_pid=os.getpid(),status='running')
        previous=state.get('manager')
        if previous and previous.get('status')=='running':
            if alive(previous['pid']):raise RuntimeError('Previous manager is alive; do not duplicate it')
            state['pending']=previous['completed']+state['pending'];previous['status']='interrupted'
        workers={}
        for task_id,entry in state['tasks'].items():
            if entry['status']=='running':
                if alive(entry['pid']):
                    if not adopt_workers:raise RuntimeError(f'Previous task {task_id} is alive; stop or finish it before resuming')
                    workers[task_id]=(WindowsWorker(entry['pid']),open(os.devnull,'wb'))
                    print(json.dumps(dict(event='task_adopted',task=task_id,pid=entry['pid'])),flush=True)
                    continue
                entry.update(status='interrupted',returncode=None)
                state['pending'].append(dict(id=task_id,status='interrupted',returncode=None))
        write_json(state_path,state)
        manager=None;startup=not bool(workers);failed_manager=False
        settings_stamp=None
        while True:
            stamp=(records/'settings.json').stat().st_mtime_ns
            if stamp!=settings_stamp:
                updated=read_json(records/'settings.json').get('max_workers',3)
                if type(updated) is not int or updated<1:raise ValueError('max_workers must be positive')
                limit=updated;settings_stamp=stamp
                state['max_workers']=limit;write_json(state_path,state)
            changed=False
            for task_id,(proc,log) in list(workers.items()):
                code=proc.poll()
                if code is None:continue
                log.close();del workers[task_id]
                state['tasks'][task_id].update(status='exited',returncode=code)
                state['pending'].append(dict(id=task_id,status='exited',returncode=code))
                print(json.dumps(dict(event='task_exited',task=task_id,returncode=code)),flush=True)
                changed=True
            if manager and manager[0].poll() is not None:
                proc,log=manager;log.close();manager=None
                state['manager'].update(status='exited',returncode=proc.returncode)
                if proc.returncode:
                    state['pending']=state['manager']['completed']+state['pending'];failed_manager=True
                print(json.dumps(dict(event='manager_exited',returncode=proc.returncode)),flush=True)
                changed=True
            if changed:write_json(state_path,state)
            queue=read_json(records/'queue.json')
            if failed_manager:
                if not workers:
                    state['status']='manager_failed';write_json(state_path,state);return 1
                time.sleep(.1);continue
            if not manager and (startup or state['pending']):
                # An explicitly final/blocked queue is stable until an explicit restart.
                if startup and queue['status'] in ('complete','blocked') and not state['pending']:
                    state['status']=queue['status'];write_json(state_path,state);return 0
                startup=False;state['manager_number']+=1
                home=records/'managers'/f'{state["manager_number"]:04d}';home.mkdir(parents=True)
                completed=state['pending'];state['pending']=[]
                inbox=dict(completed=completed,running=list(workers),tasks=state['tasks'])
                write_json(home/'inbox.json',inbox)
                session=dict(role='manager',source_repo=str(repo),records=str(records),engine=str(ENGINE),inbox=str(home/'inbox.json'))
                manager=start(selected(command,settings.get('manager',{})),session,repo,home/'session.log')
                state['manager']=dict(status='running',pid=manager[0].pid,completed=completed,number=state['manager_number'])
                write_json(state_path,state)
                print(json.dumps(dict(event='manager_started',number=state['manager_number'],pid=manager[0].pid)),flush=True)
            if queue['status']=='active':
                accepted=set(queue['accepted']);cancelled=set(queue.get('cancelled',[]))
                for task in queue['tasks']:
                    task_id=task['id']
                    if len(workers)>=limit:break
                    if task_id in state['tasks'] or task_id in accepted|cancelled:continue
                    if not set(task['depends_on'])<=accepted:continue
                    try:
                        workspace=prepare(repo,records,task,settings)
                        session=dict(role='review' if task['kind']=='review' else 'task',source_repo=str(repo),
                            records=str(records),engine=str(ENGINE),task=task_id,workspace=str(workspace))
                        proc,log=start(selected(command,task),session,workspace,records/'tasks'/task_id/'session.log')
                        workers[task_id]=(proc,log)
                        state['tasks'][task_id]=dict(status='running',pid=proc.pid,workspace=str(workspace),spec=task)
                        print(json.dumps(dict(event='task_started',task=task_id,pid=proc.pid)),flush=True)
                    except Exception as exc:
                        state['tasks'][task_id]=dict(status='launch_failed',returncode=None,spec=task,error=str(exc))
                        state['pending'].append(dict(id=task_id,status='launch_failed',returncode=None,error=str(exc)))
                    write_json(state_path,state)
            if not manager and not workers and not state['pending']:
                state['status']=queue['status'] if queue['status']!='active' else 'idle'
                write_json(state_path,state)
                return 0
            time.sleep(.1)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('repo');parser.add_argument('records')
    parser.add_argument('--adopt-workers',action='store_true',help='Explicit Windows handover after stopping only the prior dispatcher')
    args=parser.parse_args();raise SystemExit(run(args.repo,args.records,adopt_workers=args.adopt_workers))
