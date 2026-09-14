"""Lean proposal verification; source is executable and must be treated as untrusted."""
from __future__ import annotations
import hashlib, json, os, re, shutil, subprocess, sys, tempfile, time
from pathlib import Path
from typing import Sequence
if __package__ in (None, ''): sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math.windows_job import WindowsJob

def _hash(b: bytes) -> str: return hashlib.sha256(b).hexdigest()
def discover_lean() -> list[str] | None:
    """Discover an already-installed Lean; never downloads or changes PATH."""
    found=shutil.which('lean')
    if found: return [found]
    portable=Path(__file__).resolve().parents[5]/'.skill-workspace/do-math-toolchains/lean-4.32.0/lean-4.32.0-windows/bin/lean.exe'
    return [str(portable)] if portable.is_file() else None
def _ident(x: str) -> bool:
    return isinstance(x,str) and x and all(part and part.replace('_','a').isalnum() and part[0].isalpha() for part in x.split('.'))

def _worker(request_path: Path) -> int:
    q=json.loads(request_path.read_text()); p=subprocess.Popen(q['command'],cwd=q['cwd'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=False)
    try: out,err=p.communicate(timeout=q['timeout']); state='exited'
    except subprocess.TimeoutExpired:
        p.kill(); out,err=p.communicate(); state='timeout'
    Path(q['stdout']).write_bytes(out); Path(q['stderr']).write_bytes(err); Path(q['status']).write_text(json.dumps({'state':state,'exit':p.returncode}))
    return 0

def _job_run(command: list[str], cwd: Path, timeout: float) -> tuple[int | None,str,str,bool]:
    root=Path(tempfile.mkdtemp(dir=cwd)); out=root/'out'; err=root/'err'; status=root/'status'; request=root/'request.json'
    request.write_text(json.dumps({'command':command,'cwd':str(cwd),'timeout':timeout,'stdout':str(out),'stderr':str(err),'status':str(status)}))
    job=WindowsJob([sys.executable,str(Path(__file__).resolve()),'--worker',str(request)],cwd=root,env=os.environ)
    try:
        job.resume(); deadline=time.monotonic()+timeout+2
        while not job.wait(0):
            if time.monotonic()>=deadline: job.terminate(); break
            time.sleep(.02)
        while True:
            s=job.inspect()
            if s.root_signaled and not s.active_processes and not s.process_ids: break
            if time.monotonic()>=deadline+2: job.terminate(); break
            time.sleep(.02)
        data=json.loads(status.read_text()) if status.exists() else {'state':'timeout','exit':None}
        return data.get('exit'),out.read_bytes().decode(errors='replace') if out.exists() else '',err.read_bytes().decode(errors='replace') if err.exists() else '',data.get('state')=='timeout'
    finally: job.close()

def verify_lean(*, source: str, declarations: list[str], workspace: Path,
                lean_command: list[str] | None = None, timeout_seconds: float = 60,
                allowed_axioms: tuple[str,...] = ('propext','Classical.choice','Quot.sound')) -> dict:
    workspace=workspace.resolve(); raw=source.encode(); base={"source_sha256":_hash(raw),"declarations":declarations,"axioms":{},"stdout":"","stderr":"","command":None,"toolchain":None,"reason":None}
    if not all(_ident(x) for x in declarations): return {**base,"status":"rejected","reason":"invalid declaration"}
    command=list(lean_command) if lean_command else (discover_lean() or [])
    if not command or not command[0]: return {**base,"status":"unavailable","reason":"lean not found"}
    if any(not isinstance(x,str) or '\x00' in x for x in command) or timeout_seconds<=0: return {**base,"status":"rejected","reason":"unsafe command or timeout"}
    try:
        exe=Path(command[0]); code,vout,verr,vtimeout=_job_run([*command,'--version'],workspace,timeout_seconds)
        toolchain={"executable":str(exe),"sha256":_hash(exe.read_bytes()) if exe.is_file() else None,"version":vout.strip(),"version_exit":code}
        if vtimeout or code != 0: return {**base,"status":"unavailable","toolchain":toolchain,"reason":"version failed"}
    except (OSError,RuntimeError) as e: return {**base,"status":"unavailable","reason":type(e).__name__}
    with tempfile.TemporaryDirectory(dir=workspace) as d:
        proposal=Path(d)/'proposal.lean'
        checks='\n'.join('#print axioms '+x for x in declarations)
        check=proposal; check.write_bytes(raw+b'\n'+checks.encode())
        code,stdout,stderr,timedout=_job_run([*command,str(check)],Path(d),timeout_seconds)
    base.update(stdout=stdout,stderr=stderr,command=[*command,str(check)],toolchain=toolchain)
    if timedout: return {**base,"status":"failed","reason":"timeout"}
    if code: return {**base,"status":"failed","reason":"lean rejected"}
    lines=stdout.splitlines(); forbidden=[]
    for decl in declarations:
        prefix="'"+decl+"'"
        found=[line.strip() for line in lines if line.strip().startswith(prefix+' depends on') or line.strip() == prefix+' does not depend on any axioms']
        if not found: return {**base,"status":"failed","reason":"axiom output missing"}
        axioms=[]
        for line in found:
            if line == prefix+' does not depend on any axioms': continue
            match=re.search(r'axioms: \[(.*)\]$',line)
            if not match: return {**base,"status":"failed","reason":"malformed axiom output"}
            axioms.extend(x.strip() for x in match.group(1).split(',') if x.strip())
        base['axioms'][decl]=axioms
        forbidden += [a for a in axioms if a=='sorryAx' or a not in allowed_axioms]
    return {**base,"status":"rejected" if forbidden else "verified","reason":None if not forbidden else 'forbidden axiom'}

if __name__ == '__main__' and len(sys.argv)==3 and sys.argv[1]=='--worker': raise SystemExit(_worker(Path(sys.argv[2])))
