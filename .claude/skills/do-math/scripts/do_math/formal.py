"""Lean proposal verification; source is executable and must be treated as untrusted."""
from __future__ import annotations
import hashlib, json, os, re, shutil, subprocess, sys, tempfile, time, traceback, uuid
from pathlib import Path
from .lean_evidence import (AXIOMS, FORMAL_EVIDENCE_FIELDS, LAKE_PROJECT_FILES, LEAN_VERSION, READY_MARKER,
                            VerificationStopped, _check_stop, approved_toolchain_differs, check_completion_status,
                            check_lean_command, check_search_path_observation, command_verdict,
                            compare_formal_results, compiler_failure_reason, declaration_rejection, forbidden_axioms,
                            identity_rejection_reason, is_lake_project_command,
                            lake_env_prefix, lake_project_dir, lean_source_sha256, mathlib_project, portable_bin,
                            project_inputs_changed, toolchain_errors)
from .cli_execution import termination_confirmed
from .lean_evidence import check_file as _check_file, parse_evidence as _parse_evidence
from .file_io import cached_sha256
from .values import is_sha256, json_digest
from do_math.windows_job import WindowsJob, process_identity


# The checker's identity is the SHA-256 of the bytes this process runs, read once
# from the module's own loader: a file path or a zip member of the same bytes is
# the same checker. Inspection records it; approved identities are compared with it.
_RUNNING_CHECKER_SHA256 = hashlib.sha256(__loader__.get_data(__file__)).hexdigest()


def _git(command, should_stop=None):
    # A short local read of the trusted project, not untrusted code: no Job or worker.
    # A stop request is honoured before and after it.
    _check_stop(should_stop)
    result = subprocess.run(command, stdin=subprocess.DEVNULL, capture_output=True,
                            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    _check_stop(should_stop)
    return result


def toolchain_root() -> Path | None:
    """Machine-wide toolchain location shared by instances; None for a shallow installation."""
    parents=Path(__file__).resolve().parents
    return parents[5]/'.skill-workspace/do-math-toolchains' if len(parents) > 5 else None
def discover_lean() -> list[str] | None:
    """Discover an already-installed Lean; never downloads or changes PATH.

    A Mathlib project that setup_lean.py finished (marker written after its smoke test) wins,
    so instances without an explicit lean_command can import Mathlib."""
    root=toolchain_root()
    if root and (mathlib_project(root)/READY_MARKER).is_file() and (portable_bin(root)/'lake.exe').is_file():
        return [str(portable_bin(root)/'lake.exe'),'--dir',str(mathlib_project(root)),'env',str(portable_bin(root)/'lean.exe')]
    found=shutil.which('lean')
    if found: return [found]
    if not root: return None
    portable=portable_bin(root)/'lean.exe'
    return [str(portable)] if portable.is_file() else None

# Per-process memos of facts derived from unchanged inputs (accidental-change model).
_GIT_ROOTS = {}     # resolved project path -> git top level
_SEARCH_PATHS = {}  # digest of (Lake command, project identity, Lake executable) -> search paths


def project_source_identity(project_root: Path, *, should_stop=None) -> dict:
    """Identify the configured Lake project's tracked subtree and local inputs (not its .lake)."""
    _check_stop(should_stop)
    root=project_root.resolve()
    if root not in _GIT_ROOTS:  # Where the repository starts changes only if it is moved.
        _GIT_ROOTS[root]=_git(['git','-C',str(root),'rev-parse','--show-toplevel'],should_stop).stdout.decode().strip()
    gitroot=_GIT_ROOTS[root]
    tree,diff,tracked_paths=None,b'',set()
    if gitroot:
        gitroot=Path(gitroot); relative='.' if root==gitroot else root.relative_to(gitroot).as_posix()
        target='HEAD^{tree}' if relative=='.' else f'HEAD:{relative}'
        tree_result=_git(['git','-C',str(gitroot),'rev-parse','--verify',target],should_stop)
        tree=tree_result.stdout.decode().strip() if tree_result.returncode == 0 else None
        diff=_git(['git','-C',str(gitroot),'diff','--no-ext-diff','HEAD','--',relative],should_stop).stdout
        tracked_result=_git(['git','-C',str(gitroot),'ls-files','-z','--',relative],should_stop)
        if tracked_result.returncode:
            raise RuntimeError('cannot read tracked paths for the configured project')
        tracked_paths={name.decode('utf-8') for name in tracked_result.stdout.split(b'\0') if name}
    else:
        gitroot=root  # Outside Git every project input is an untracked file.
    untracked={}
    # .lake holds dependency sources and build output; lake-manifest.json already pins them.
    for directory,dirs,names in os.walk(root):
        _check_stop(should_stop)
        dirs[:]=[x for x in dirs if x!='.lake']
        for path in (Path(directory)/name for name in names):
            _check_stop(should_stop)
            if path.suffix=='.lean' or path.name in LAKE_PROJECT_FILES:
                tracked=path.relative_to(gitroot).as_posix() in tracked_paths
                if not tracked: untracked[path.relative_to(root).as_posix()]=cached_sha256(path)
    # Consumers compare project identity; no runtime consumer reads individual
    # entries. Keep the full filename/content sensitivity without copying a
    # large inventory into every role prompt and formal result.
    untracked_digest = json_digest(untracked)
    _check_stop(should_stop)
    return {'root':str(root),'git_tree':tree,'working_diff_hash':hashlib.sha256(diff).hexdigest(),
            'untracked_file_count':len(untracked),'untracked_sha256':untracked_digest}

def _worker(request_path: Path) -> int:
    q=json.loads(request_path.read_text())
    code=None
    try:
        # Files receive all bytes directly: no PIPE buffers, reader threads or output truncation.
        with open(q['stdout'],'wb',buffering=0) as out, open(q['stderr'],'wb',buffering=0) as err:
            with subprocess.Popen(q['command'],cwd=q['cwd'],stdout=out,stderr=err,
                    shell=False,creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)) as process:
                code=process.wait()
        state='exited'
    except Exception:
        state='worker_error'
        with open(q['stderr'],'ab') as err:
            err.write(traceback.format_exc().encode('utf-8'))
    Path(q['status']).write_text(json.dumps({'state':state,'exit':code}))
    return 0


def _job_run(command: list[str], cwd: Path, *, should_stop=None, on_started=None,
             on_finished=None, job_name=None, jobs=None):
    """Wait for the whole Job; only explicit stop terminates it.

    The two-second termination check applies only after cancellation, never to computation.
    """
    root=Path(tempfile.mkdtemp(dir=cwd)); out=root/'out'; err=root/'err'; status=root/'status'; request=root/'request.json'
    request.write_text(json.dumps({'command':command,'cwd':str(cwd),'stdout':str(out),'stderr':str(err),'status':str(status)}))
    worker = "import sys; from pathlib import Path; sys.path.insert(0,sys.argv[1]); from do_math.formal import _worker; raise SystemExit(_worker(Path(sys.argv[2])))"
    environment={key:value for key,value in os.environ.items()
                 if not key.upper().startswith(('LEAN_', 'LAKE_', 'ELAN_'))}
    # The Jobs port; None starts the module's WindowsJob (stage 1b migration).
    job=(jobs.launch if jobs is not None else WindowsJob)(
        [sys.executable,'-B','-c',worker,str(Path(__file__).resolve().parents[1]),str(request)],cwd=root,env=environment,
                   name=job_name or 'do-math-formal-'+uuid.uuid4().hex)
    try:
        started={**process_identity(job),'job_name':job.name}
        if on_started: on_started(started)
        job.resume(); stopped=False
        while True:
            if should_stop and should_stop():
                job.terminate(); stopped=True; break
            if job.wait(0) and termination_confirmed(job.inspect()):
                break
            time.sleep(.02)
        if stopped:
            termination_deadline=time.monotonic()+2
            while True:
                if termination_confirmed(job.inspect()): break
                if time.monotonic()>=termination_deadline:
                    raise RuntimeError('formal Job termination could not be confirmed')
                time.sleep(.02)
        if on_finished: on_finished(job.resource_usage())
        def read_output(path):
            return path.read_text(encoding='utf-8',errors='replace') if path.exists() else ''
        stdout,stderr=read_output(out),read_output(err)
        if stopped: return None,stdout,stderr,True
        if not status.exists():
            raise RuntimeError('formal worker completion status missing' + (': '+stderr if stderr else ''))
        try:
            data=json.loads(status.read_text())
            check_completion_status(data)
        except ValueError as error:
            raise RuntimeError('formal worker completion status invalid: '+str(error)) from error
        if data['state']=='worker_error': raise RuntimeError('formal worker failed: '+stderr)
        return data['exit'],stdout,stderr,False
    finally: job.close()


def _project_identity(command, should_stop=None, *, workspace=None, expected=None):
    if not is_lake_project_command(command):
        return None
    _check_stop(should_stop)
    root = Path(lake_project_dir(command)).resolve(strict=True)
    identity={'manifest_hashes': {name: cached_sha256(root/name) for name in LAKE_PROJECT_FILES if (root/name).is_file()},
              'source_identity': project_source_identity(root,should_stop=should_stop)}
    if project_inputs_changed(identity, expected):
        return {**identity,'search_paths':[]}
    prefix=lake_env_prefix(command, workspace)
    # Lake derives the search paths from its executable and the inputs identified
    # above; unchanged inputs give the same paths, so one observation per process.
    lake=Path(shutil.which(prefix[0]) or prefix[0])
    key=json_digest([prefix,identity,cached_sha256(lake) if lake.is_file() else None])
    if key in _SEARCH_PATHS:
        return {**identity,'search_paths':list(_SEARCH_PATHS[key])}
    script=('import os,json; print(json.dumps({"cwd":os.getcwd(),"paths":'
            '[p for k in ("LEAN_PATH","LEAN_SRC_PATH") for p in os.environ.get(k,"").split(os.pathsep) if p]}))')
    code,out,err,stopped=_job_run([*prefix,sys.executable,'-c',script],Path(workspace),should_stop=should_stop)
    if stopped:raise VerificationStopped('project environment observation stopped')
    if code!=0:raise RuntimeError('project environment observation failed: '+err)
    observed=json.loads(out)
    check_search_path_observation(observed)
    identity['search_paths']=sorted({str((Path(observed['cwd'])/p).resolve()) for p in observed['paths']})
    _SEARCH_PATHS[key]=tuple(identity['search_paths'])
    return identity


def inspect_toolchain(command, workspace, *, should_stop=None):
    """Observe exact tool identity; this does not run environment validation."""
    command = list(command)
    check_lean_command(command)
    _check_stop(should_stop)
    resolved = Path(shutil.which(command[0]) or command[0]).resolve(strict=True)
    code, stdout, stderr, stopped = _job_run([*command, '--version'], Path(workspace), should_stop=should_stop)
    if stopped: raise VerificationStopped('toolchain observation stopped')
    if code != 0:
        raise RuntimeError('toolchain version observation failed: ' + stderr)
    result = {'executable': str(resolved), 'sha256': cached_sha256(resolved),
        'configured_command': command, 'version': stdout.strip(), 'version_exit': code,
        'project': _project_identity(command,should_stop,workspace=workspace),
        'verifier_sha256': _RUNNING_CHECKER_SHA256, 'verifier_path':str(Path(__file__).resolve()),
        'executables': {str(Path(p).resolve()): cached_sha256(Path(p)) for p in command
                        if Path(p).is_file() and Path(p).suffix.lower() in {'.exe', '.dll'}}}
    errors = toolchain_errors(result)
    if errors:
        raise ValueError('; '.join(errors))
    return result


def toolchain_identity_errors(toolchain, *, should_stop=None):
    """Recompute the local facts of an approved identity: the recorded executable
    and checker bytes, the running checker and the Lake project inputs.

    Formal checks, activation and publication gates share this one check. It does
    not isolate processes from concurrent writers under the same OS identity.
    """
    errors = toolchain_errors(toolchain)
    if errors:
        return errors
    if toolchain['verifier_sha256'] != _RUNNING_CHECKER_SHA256:
        errors.append('approved checker is not the running checker')
    # Pairs, not a mapping: the executable may also appear among the command's
    # files, and each recorded hash must hold on its own.
    files = [(toolchain['executable'], toolchain['sha256']), *toolchain['executables'].items(),
             (toolchain['verifier_path'], toolchain['verifier_sha256'])]
    for path, expected in files:
        try:
            current = cached_sha256(Path(path))
        except OSError:
            current = None
        message = 'approved toolchain file changed: ' + path
        if current != expected and message not in errors:
            errors.append(message)
    try:
        with tempfile.TemporaryDirectory(prefix='do-math-identity-') as workspace:
            project = _project_identity(toolchain['configured_command'], should_stop,
                                        workspace=Path(workspace), expected=toolchain['project'])
    except VerificationStopped:
        raise
    except (OSError, RuntimeError, ValueError) as error:
        return errors + ['approved project inputs could not be observed: ' + str(error)]
    if project != toolchain['project']:
        errors.append('approved project inputs changed')
    return errors


def verify_lean(*, source: str, declarations: list[str], workspace: Path,
                lean_command: list[str] | None = None,
                allowed_axioms: tuple[str,...] = AXIOMS, should_stop=None,
                expected_toolchain: dict | None = None, on_started=None, launch_ticket=None,
                extract_evidence: bool = True, jobs=None) -> dict:
    """Verify Lean to completion.

    The output is preserved except the dependency body rows that a verified result
    keeps as hashes. Without ``extract_evidence`` (the worker preview) the kernel
    check, signatures and ``#print axioms`` run and no dependency evidence is made.
    Cancellation remains available through should_stop.
    """
    if launch_ticket is not None:
        from .launch import require_dispatched_native, validate_start
        validate_start(launch_ticket, jobs=jobs)
        require_dispatched_native(launch_ticket)
    workspace=workspace.resolve(); raw=source.encode(); base={"source_sha256":lean_source_sha256(source),"declarations":declarations,"axioms":{},"declaration_signatures":{},"dependency_closure":{},"declaration_evidence":{},"signature_hash":None,"stdout":"","stderr":"","command":None,"toolchain":None,"reason":None}
    base['launch_not_created'] = True
    rejection=declaration_rejection(declarations)
    if rejection: return {**base,"status":"rejected","reason":rejection}
    command=list(lean_command) if lean_command else (discover_lean() or [])
    verdict=command_verdict(command)
    if verdict: return {**base,"status":verdict[0],"reason":verdict[1]}
    try:
        _check_stop(should_stop)
        # Compare the same canonical executable identity that inspect_toolchain records.
        resolved=Path(shutil.which(command[0]) or command[0]).resolve()
        if expected_toolchain is not None:
            if approved_toolchain_differs(expected_toolchain, command, str(resolved)):
                return {**base,'status':'rejected','reason':'approved toolchain changed before execution',
                        'error_kind':'trust_environment'}
            identity_errors=toolchain_identity_errors(expected_toolchain,should_stop=should_stop)
            if identity_errors:
                return {**base,'status':'rejected','reason':identity_rejection_reason(identity_errors),'identity_errors':identity_errors,
                        'error_kind':'trust_environment'}
        toolchain=inspect_toolchain(command,workspace,should_stop=should_stop) if expected_toolchain is None else dict(expected_toolchain)
    except VerificationStopped as error:
        return {**base,'status':'stopped','reason':str(error),'phase':'preparation'}
    except (OSError,RuntimeError,ValueError) as error:
        return {**base,'status':'unavailable','reason':str(error),'phase':'preparation'}
    with tempfile.TemporaryDirectory(dir=workspace) as directory:
        check=Path(directory)/'proposal.lean'
        check.write_bytes(_check_file(raw,declarations,extract_evidence=extract_evidence))
        local_job_usage={}
        def started(identity):
            base['launch_not_created'] = False
            if on_started is not None:
                on_started(identity)
        try:
            _check_stop(should_stop)
            code,stdout,stderr,stopped=_job_run([*command,str(check)],Path(directory),should_stop=should_stop,
                on_started=started,on_finished=lambda observed:local_job_usage.update(observed),
                job_name=launch_ticket['job_name'] if launch_ticket is not None else None, jobs=jobs)
        except VerificationStopped as error:
            return {**base,'status':'stopped','reason':str(error),'toolchain':toolchain}
        except (OSError,RuntimeError) as error:
            return {**base,'status':'failed','reason':'verification process failed: '+str(error),
                'command':[*command,str(check)],'toolchain':toolchain}
    base.update(stdout=stdout,stderr=stderr,command=[*command,str(check)],toolchain=toolchain,exit_code=code,
                local_job_usage=local_job_usage)
    if stopped: return {**base,'status':'stopped','reason':'stopped'}
    if code:
        return {**base,'status':'failed','reason':compiler_failure_reason(code, os.name)}
    try:
        return _parse_evidence(base,declarations,allowed_axioms,should_stop,extract_evidence=extract_evidence)
    except VerificationStopped as error:
        return {**base,'status':'stopped','reason':str(error)}


