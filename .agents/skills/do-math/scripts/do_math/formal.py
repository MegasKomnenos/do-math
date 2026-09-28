"""Lean proposal verification; source is executable and must be treated as untrusted."""
from __future__ import annotations
import hashlib, json, os, re, shutil, subprocess, sys, tempfile, time, traceback, uuid
from pathlib import Path
from .trust_validation import AXIOMS
from .file_io import cached_sha256, is_sha256, json_digest
from do_math.windows_job import WindowsJob, process_identity

class VerificationStopped(RuntimeError):
    pass


def _check_stop(should_stop):
    if should_stop and should_stop():
        raise VerificationStopped('verification stopped')


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

_DEPENDENCY_EXTRACTOR = r'''
namespace DoMathDependencyAudit
open Lean
def flatFormat (format : Std.Format) : String := Id.run do
  let mut pending := #[format]
  let mut output := ""
  while !pending.isEmpty do
    let current := pending.back!
    pending := pending.pop
    match current with
    | .nil => pure ()
    | .text text => output := output ++ text
    | .line | .align _ => output := output ++ " "
    | .append left right => pending := pending.push right |>.push left
    | .nest _ inner | .group inner _ | .tag _ inner => pending := pending.push inner
  return output
def scalar [Repr α] (value : α) : Json :=
  Json.mkObj [("atom", toJson (flatFormat (reprArg value)))]
def children : Expr → Array Expr
  | .app fn arg => #[fn, arg]
  | .lam _ type body _ | .forallE _ type body _ => #[type, body]
  | .letE _ type value body _ => #[type, value, body]
  | .mdata _ body | .proj _ _ body => #[body]
  | _ => #[]
def exprEvidence (value : Expr) : CoreM String := do
  let mut ids : ExprStructMap Nat := {}
  let mut nodes : Array Json := #[]
  let mut pending := #[(value, false)]
  while !pending.isEmpty do
    let (current, ready) := pending.back!
    pending := pending.pop
    if (ids.get? ⟨current⟩).isNone then
      if !ready then
        pending := pending.push (current, true)
        for child in (children current).reverse do
          if (ids.get? ⟨child⟩).isNone then pending := pending.push (child, false)
      else
        let refs ← (children current).mapM fun child => do
          let some index := ids.get? ⟨child⟩ | throwError "missing expression child"
          pure (Json.mkObj [("ref", toJson index)])
        let args := match current with
          | .bvar index => #[scalar index]
          | .fvar id => #[scalar id]
          | .mvar id => #[scalar id]
          | .sort level => #[scalar level]
          | .const name levels => #[scalar name, scalar levels]
          | .app _ _ => refs
          | .lam name _ _ info | .forallE name _ _ info => #[scalar name, refs[0]!, refs[1]!, scalar info]
          | .letE name _ _ _ nonDep => #[scalar name, refs[0]!, refs[1]!, refs[2]!, scalar nonDep]
          | .lit literal => #[scalar literal]
          | .mdata data _ => #[scalar data, refs[0]!]
          | .proj name index _ => #[scalar name, scalar index, refs[0]!]
        let index := nodes.size
        nodes := nodes.push (Json.mkObj [("constructor", toJson ("Lean.Expr." ++ current.ctorName)),
          ("args", Json.arr args)])
        ids := ids.insert ⟨current⟩ index
  let some root := ids.get? ⟨value⟩ | throwError "missing expression root"
  return (Json.mkObj [("format", toJson "lean-expr-dag/1"), ("root", toJson root),
    ("nodes", Json.arr nodes)]).compress
def constantEvidence (info : ConstantInfo) : CoreM Json := do
  let type ← exprEvidence info.type
  let value ← match info.value? true with
    | some value => toJson <$> exprEvidence value
    | none => pure Json.null
  return Json.mkObj [("type", toJson type), ("value", value)]
def directRefs (env : Environment) (name : Name) : Except String (Array Name) := do
  let some info := env.checked.get.find? name | throw s!"missing constant {name}"
  let mut refs := info.type.getUsedConstants
  if let some value := info.value? true then
    refs := refs ++ value.getUsedConstants
  if let .inductInfo value := info then
    refs := refs ++ value.ctors.toArray
  return refs
-- The closure of `name`. `known` holds each constant's direct references and is
-- shared by the audited declarations, so every expression is traversed once.
def visit (env : Environment) (name : Name) (known : NameMap (Array Name)) :
    Except String (NameSet × NameMap (Array Name)) := do
  let mut result : NameSet := {}
  let mut known := known
  let mut pending := #[name]
  while !pending.isEmpty do
    let current := pending.back!
    pending := pending.pop
    if !result.contains current then
      result := result.insert current
      let refs ← match known.find? current with
        | some refs => pure refs
        | none => directRefs env current
      known := known.insert current refs
      for ref in refs do
        if !result.contains ref then pending := pending.push ref
  return (result, known)
def audit (name : Name) (emitted : NameSet) (known : NameMap (Array Name)) :
    CoreM (Json × NameSet × NameMap (Array Name)) := do
  let env ← getEnv
  let some info := env.checked.get.find? name | throwError "missing audited declaration"
  let (closure, known) ← match visit env name known with
    | .ok value => pure value
    | .error error => throwError "{error}"
  let names := (closure.toArray.filter (· != name)).qsort Name.lt
  -- The axiom constants of the closure; the verifier compares them with `#print axioms`.
  let axioms := closure.toArray.filter fun constant =>
    match env.checked.get.find? constant with
    | some (.axiomInfo _) => true
    | _ => false
  let mut emitted := emitted
  for dependency in names do
    if !emitted.contains dependency then
      let some constant := env.checked.get.find? dependency | throwError "missing dependency"
      let evidence ← constantEvidence constant
      let row := Json.mkObj [("name", toJson dependency.toString), ("evidence", evidence)]
      IO.println ("__DO_MATH_DEPENDENCY__" ++ row.compress)
      emitted := emitted.insert dependency
  let evidence ← constantEvidence info
  return (Json.mkObj [("declaration", toJson name.toString),
    ("dependencies", toJson (names.map Name.toString)),
    ("axioms", toJson ((axioms.qsort Name.lt).map Name.toString)),
    ("evidence", evidence)], emitted, known)
end DoMathDependencyAudit
elab "#do_math_dependencies " names:ident+ : command => do
  Lean.Elab.Command.liftCoreM do
    let mut emitted : Lean.NameSet := {}
    let mut known : Lean.NameMap (Array Lean.Name) := {}
    for name in names do
      let (evidence, nextEmitted, nextKnown) ← DoMathDependencyAudit.audit name.getId emitted known
      emitted := nextEmitted
      known := nextKnown
      IO.println ("__DO_MATH_DEPENDENCIES__" ++ evidence.compress)
'''


# The kernel evidence of one verification. declaration_evidence, dependency_closure
# and axioms are keyed by declaration name; dependency_evidence holds one body hash
# per constant of the union of the closures (knowledge_records.validate_formal_evidence).
FORMAL_EVIDENCE_FIELDS = ("declaration_evidence", "dependency_closure", "dependency_evidence", "axioms")


def lean_source_sha256(code: str) -> str:
    """The identity of a Lean source that a verification names as source_sha256."""
    return hashlib.sha256(code.encode()).hexdigest()


def forbidden_axioms(axiom_rows: dict, allowed) -> set[str]:
    """Axioms outside the approved set; sorryAx is never approved."""
    return {axiom for axioms in axiom_rows.values() for axiom in axioms
            if axiom == 'sorryAx' or axiom not in allowed}


def compare_formal_results(previous: dict, current: dict) -> dict:
    fields = FORMAL_EVIDENCE_FIELDS
    # An empty dependency table is evidence: the closures may contain no constant.
    missing = [field for field in fields if previous.get(field) is None or current.get(field) is None]
    changed = [field for field in fields if field not in missing and previous[field] != current[field]]
    return {"equivalent": not missing and not changed, "missing": missing, "changed": changed,
            "requires_identity_review": bool(missing or changed)}

LEAN_VERSION='4.32.0'; READY_MARKER='.do-math-ready'
def toolchain_root() -> Path | None:
    """Machine-wide toolchain location shared by instances; None for a shallow installation."""
    parents=Path(__file__).resolve().parents
    return parents[5]/'.skill-workspace/do-math-toolchains' if len(parents) > 5 else None
def portable_bin(root: Path) -> Path: return root/f'lean-{LEAN_VERSION}/lean-{LEAN_VERSION}-windows/bin'
def mathlib_project(root: Path) -> Path: return root/f'mathlib-{LEAN_VERSION}'
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
def is_lean_identifier(x: str) -> bool:
    """The declaration-name grammar that formal checks accept."""
    if not isinstance(x, str) or not x:
        return False
    parts = [part.rstrip("'") for part in x.split('.')]
    return all(part and part.replace('_', 'a').isalnum() and part[0].isalpha() for part in parts)

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
            if path.suffix=='.lean' or path.name in {'lean-toolchain','lake-manifest.json','lakefile.lean','lakefile.toml'}:
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
             on_finished=None, raw_output=False, job_name=None):
    """Wait for the whole Job; only explicit stop terminates it.

    The two-second termination check applies only after cancellation, never to computation.
    """
    root=Path(tempfile.mkdtemp(dir=cwd)); out=root/'out'; err=root/'err'; status=root/'status'; request=root/'request.json'
    request.write_text(json.dumps({'command':command,'cwd':str(cwd),'stdout':str(out),'stderr':str(err),'status':str(status)}))
    worker = "import sys; from pathlib import Path; sys.path.insert(0,sys.argv[1]); from do_math.formal import _worker; raise SystemExit(_worker(Path(sys.argv[2])))"
    environment={key:value for key,value in os.environ.items()
                 if not key.upper().startswith(('LEAN_', 'LAKE_', 'ELAN_'))}
    job=WindowsJob([sys.executable,'-B','-c',worker,str(Path(__file__).resolve().parents[1]),str(request)],cwd=root,env=environment,
                   name=job_name or 'do-math-formal-'+uuid.uuid4().hex)
    try:
        started={**process_identity(job),'job_name':job.name}
        if on_started: on_started(started)
        job.resume(); stopped=False
        while True:
            if should_stop and should_stop():
                job.terminate(); stopped=True; break
            if job.wait(0):
                observed=job.inspect()
                if observed.root_signaled and not observed.active_processes and not observed.process_ids:
                    break
            time.sleep(.02)
        if stopped:
            termination_deadline=time.monotonic()+2
            while True:
                observed=job.inspect()
                if observed.root_signaled and not observed.active_processes and not observed.process_ids: break
                if time.monotonic()>=termination_deadline:
                    raise RuntimeError('formal Job termination could not be confirmed')
                time.sleep(.02)
        if on_finished: on_finished(job.resource_usage())
        def read_output(path):
            if not path.exists(): return b'' if raw_output else ''
            return path.read_bytes() if raw_output else path.read_text(encoding='utf-8',errors='replace')
        stdout,stderr=read_output(out),read_output(err)
        error_stderr=stderr.decode(errors='replace') if isinstance(stderr,bytes) else stderr
        if stopped: return None,stdout,stderr,True
        if not status.exists():
            raise RuntimeError('formal worker completion status missing' + (': '+error_stderr if error_stderr else ''))
        try:
            data=json.loads(status.read_text())
            if (not isinstance(data,dict) or data.get('state') not in {'exited','worker_error'}
                    or (data['state']=='exited' and type(data.get('exit')) is not int)):
                raise ValueError('invalid completion status')
        except ValueError as error:
            raise RuntimeError('formal worker completion status invalid: '+str(error)) from error
        if data['state']=='worker_error': raise RuntimeError('formal worker failed: '+error_stderr)
        return data['exit'],stdout,stderr,False
    finally: job.close()

def toolchain_errors(toolchain):
    """The structural contract shared by registration, inspection and execution."""
    required = {'executable', 'sha256', 'configured_command', 'version', 'version_exit',
                'verifier_sha256', 'verifier_path', 'executables', 'project'}
    if not isinstance(toolchain, dict):
        return ['toolchain must be an object']
    errors = ['toolchain.' + key + ' is missing' for key in sorted(required - toolchain.keys())]
    for key in ('sha256', 'verifier_sha256'):
        value = toolchain.get(key)
        if key in toolchain and not is_sha256(value):
            errors.append('toolchain.' + key + ' must be a SHA-256')
    for key in ('executable', 'version'):
        if key in toolchain and (not isinstance(toolchain[key], str) or not toolchain[key].strip()):
            errors.append('toolchain.' + key + ' must be nonempty')
    if not isinstance(toolchain.get('verifier_path'),str) or not Path(toolchain['verifier_path']).is_absolute():
        errors.append('toolchain.verifier_path must identify the absolute checker source')
    command = toolchain.get('configured_command')
    if not isinstance(command, list) or not command or any(not isinstance(p, str) or not p or '\x00' in p for p in command):
        errors.append('toolchain.configured_command must be a nonempty argv')
    if type(toolchain.get('version_exit')) is not int or toolchain['version_exit'] != 0:
        errors.append('toolchain.version_exit must record a successful version observation')
    executables = toolchain.get('executables')
    if not isinstance(executables, dict) or any(not isinstance(p, str) or not p or
            not is_sha256(h) for p, h in executables.items()):
        errors.append('toolchain.executables must map paths to SHA-256 values')
    project = toolchain.get('project')
    if project is not None and (not isinstance(project, dict) or
            set(project) != {'manifest_hashes', 'source_identity', 'search_paths'}
            or not isinstance(project['source_identity'], dict)
            or not isinstance(project['source_identity'].get('root'), str)
            or not Path(project['source_identity']['root']).is_absolute()):
        errors.append('toolchain.project must be null or the observed Lake project identity')
    elif project is not None:
        paths=project['search_paths']
        if not isinstance(paths,list) or any(not isinstance(p,str) or not Path(p).is_absolute() for p in paths):
            errors.append('toolchain project search paths must be observed absolute paths')
    return errors


def _project_identity(command, should_stop=None, *, workspace=None, expected=None):
    if not Path(command[0]).name.lower().startswith('lake') or '--dir' not in command:
        return None
    _check_stop(should_stop)
    index = command.index('--dir') + 1
    if index >= len(command):
        raise ValueError('Lake --dir requires a project path')
    root = Path(command[index]).resolve(strict=True)
    names = ('lean-toolchain', 'lake-manifest.json', 'lakefile.lean', 'lakefile.toml')
    identity={'manifest_hashes': {name: cached_sha256(root/name) for name in names if (root/name).is_file()},
              'source_identity': project_source_identity(root,should_stop=should_stop)}
    # Never execute changed project code merely to discover its environment.
    if expected is not None and any(identity[k]!=expected.get(k) for k in identity):
        return {**identity,'search_paths':[]}
    if workspace is None or 'env' not in command:
        raise ValueError('Lake environment observation requires env and an observation workspace')
    prefix=command[:command.index('env')+1]
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
    if (not isinstance(observed,dict) or not isinstance(observed.get('cwd'),str)
            or not isinstance(observed.get('paths'),list) or any(not isinstance(p,str) for p in observed['paths'])):
        raise ValueError('invalid project environment observation')
    identity['search_paths']=sorted({str((Path(observed['cwd'])/p).resolve()) for p in observed['paths']})
    _SEARCH_PATHS[key]=tuple(identity['search_paths'])
    return identity


def inspect_toolchain(command, workspace, *, should_stop=None):
    """Observe exact tool identity; this does not run environment validation."""
    command = list(command)
    if not command or any(not isinstance(p, str) or not p or '\x00' in p for p in command):
        raise ValueError('a nonempty Lean command is required')
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


def _check_file(raw: bytes, declarations: list[str], *, extract_evidence: bool) -> bytes:
    """The compiled file: ``import Lean``, the source, the signature and axiom
    audits and, when extracting evidence, the dependency extractor and its command."""
    checks='\n'.join('#eval "__DO_MATH_SIGNATURE_BEGIN_'+x+'__"\n#check '+x+'\n#eval "__DO_MATH_SIGNATURE_END_'+x+'__"\n#print axioms '+x for x in declarations)
    parts=[b'import Lean',raw,checks.encode()]
    if extract_evidence:
        parts+=[_DEPENDENCY_EXTRACTOR.encode(),('#do_math_dependencies '+' '.join(declarations)).encode()]
    return b'\n'.join(parts)


def verify_lean(*, source: str, declarations: list[str], workspace: Path,
                lean_command: list[str] | None = None,
                allowed_axioms: tuple[str,...] = AXIOMS, should_stop=None,
                expected_toolchain: dict | None = None, on_started=None, launch_ticket=None,
                extract_evidence: bool = True) -> dict:
    """Verify Lean to completion.

    The output is preserved except the dependency body rows that a verified result
    keeps as hashes. Without ``extract_evidence`` (the worker preview) the kernel
    check, signatures and ``#print axioms`` run and no dependency evidence is made.
    Cancellation remains available through should_stop.
    """
    if launch_ticket is not None:
        from .launch import validate_start
        validate_start(launch_ticket)
        if launch_ticket['kind'] != 'native_job' or launch_ticket['phase'] != 'dispatched':
            raise ValueError('formal runner needs the dispatched native launch ticket')
    workspace=workspace.resolve(); raw=source.encode(); base={"source_sha256":lean_source_sha256(source),"declarations":declarations,"axioms":{},"declaration_signatures":{},"dependency_closure":{},"declaration_evidence":{},"signature_hash":None,"stdout":"","stderr":"","command":None,"toolchain":None,"reason":None}
    base['launch_not_created'] = True
    if not all(is_lean_identifier(x) for x in declarations): return {**base,"status":"rejected","reason":"invalid declaration"}
    if not declarations: return {**base,"status":"rejected","reason":"no declaration to audit"}
    command=list(lean_command) if lean_command else (discover_lean() or [])
    if not command or not command[0]: return {**base,"status":"unavailable","reason":"lean not found"}
    if any(not isinstance(x,str) or '\x00' in x for x in command):
        return {**base,"status":"rejected","reason":"unsafe command"}
    try:
        _check_stop(should_stop)
        # Compare the same canonical executable identity that inspect_toolchain records.
        resolved=Path(shutil.which(command[0]) or command[0]).resolve()
        if expected_toolchain is not None:
            if expected_toolchain.get('configured_command') != command or expected_toolchain.get('executable') != str(resolved):
                return {**base,'status':'rejected','reason':'approved toolchain changed before execution',
                        'error_kind':'trust_environment'}
            identity_errors=toolchain_identity_errors(expected_toolchain,should_stop=should_stop)
            if identity_errors:
                reason=('approved project inputs changed before execution' if identity_errors == ['approved project inputs changed']
                        else 'approved toolchain changed before execution')
                return {**base,'status':'rejected','reason':reason,'identity_errors':identity_errors,
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
                job_name=launch_ticket['job_name'] if launch_ticket is not None else None)
        except VerificationStopped as error:
            return {**base,'status':'stopped','reason':str(error),'toolchain':toolchain}
        except (OSError,RuntimeError) as error:
            return {**base,'status':'failed','reason':'verification process failed: '+str(error),
                'command':[*command,str(check)],'toolchain':toolchain}
    base.update(stdout=stdout,stderr=stderr,command=[*command,str(check)],toolchain=toolchain,exit_code=code,
                local_job_usage=local_job_usage)
    if stopped: return {**base,'status':'stopped','reason':'stopped'}
    if code:
        crashed=(code & 0x80000000 != 0) if os.name=='nt' else code<0
        return {**base,'status':'failed','reason':'compiler crashed' if crashed else 'lean rejected'}
    try:
        return _parse_evidence(base,declarations,allowed_axioms,should_stop,extract_evidence=extract_evidence)
    except VerificationStopped as error:
        return {**base,'status':'stopped','reason':str(error)}


def _parse_evidence(base, declarations, allowed_axioms, should_stop=None, *, extract_evidence=True):
    """Consume one evidence row at a time; retain hashes, not every dependency body."""
    # Imported here: Job workers import this module only to start the compiler.
    from .repository import exact_content_hash
    begin={f'"__DO_MATH_SIGNATURE_BEGIN_{name}__"':name for name in declarations}
    end={f'"__DO_MATH_SIGNATURE_END_{name}__"':name for name in declarations}
    selected=set(declarations); signatures={}; capture=None; fragments=[]
    axiom_rows={}; extracted={}; dependency_hashes={}
    kept=[]  # The output without the dependency body rows reduced to hashes.
    # Unlike splitlines(), this does not duplicate the complete output as a list of strings.
    for match in re.finditer(r'[^\n]*(?:\n|$)',base['stdout']):
        _check_stop(should_stop)
        line=match.group(0).rstrip('\r\n')
        if line in begin and begin[line] not in signatures:
            capture=begin[line]; fragments=[]
        elif capture is not None and end.get(line)==capture:
            signatures[capture]='\n'.join(fragments).strip(); capture=None; fragments=[]
        elif capture is not None:
            fragments.append(line)
        if extract_evidence and line.startswith('__DO_MATH_DEPENDENCY__'):
            try:
                row=json.loads(line[len('__DO_MATH_DEPENDENCY__'):])
                name=row['name']
                evidence=row['evidence']
                if (not isinstance(name,str) or name in dependency_hashes
                        or not isinstance(evidence,dict) or not isinstance(evidence.get('type'),str)
                        or evidence.get('value') is not None and not isinstance(evidence['value'],str)):
                    raise ValueError('invalid dependency evidence')
                dependency_hashes[name]=exact_content_hash({'type':evidence['type'],'value':evidence.get('value')})
                del row
            except (KeyError,TypeError,ValueError,RecursionError):
                return {**base,'status':'failed','reason':'malformed dependency evidence'}
            continue
        kept.append(match.group(0))
        if extract_evidence and line.startswith('__DO_MATH_DEPENDENCIES__'):
            try:
                row=json.loads(line[len('__DO_MATH_DEPENDENCIES__'):])
                name=row['declaration']
                if (name not in selected or name in extracted
                        or not isinstance(row['dependencies'],list)
                        or any(not isinstance(value,str) for value in row['dependencies'])
                        or not isinstance(row['evidence'],dict)
                        or not isinstance(row['evidence'].get('type'),str)
                        or not isinstance(row['axioms'],list)
                        or any(not isinstance(value,str) for value in row['axioms'])):
                    raise ValueError('invalid declaration evidence')
                extracted[name]=row
            except (KeyError,TypeError,ValueError,RecursionError):
                return {**base,'status':'failed','reason':'malformed dependency evidence'}
        else:
            stripped=line.strip()
            if stripped.endswith("' does not depend on any axioms"):
                name=stripped[1:-len("' does not depend on any axioms")]
                if name in selected: axiom_rows.setdefault(name,[])
            elif ' depends on' in stripped:
                prefix,body=stripped.split(' depends on',1)
                name=prefix[1:-1]
                if name in selected:
                    parsed=re.fullmatch(r' axioms: \[(.*)\]',body)
                    if not parsed: return {**base,'status':'failed','reason':'malformed axiom output'}
                    axiom_rows.setdefault(name,[]).extend(value.strip() for value in parsed[1].split(',') if value.strip())
    for declaration in declarations:
        if not signatures.get(declaration): return {**base,'status':'failed','reason':'signature output missing'}
        if declaration not in axiom_rows: return {**base,'status':'failed','reason':'axiom output missing'}
    base['declaration_signatures']=signatures
    base['axioms']=axiom_rows
    base['signature_hash']=exact_content_hash(signatures)
    if forbidden_axioms(axiom_rows, allowed_axioms):
        return {**base,'status':'rejected','reason':'forbidden axiom'}
    if not extract_evidence:
        return {**base,'status':'verified','reason':None}
    if set(extracted)!=selected: return {**base,'status':'failed','reason':'dependency output missing'}
    for declaration,row in extracted.items():
        _check_stop(should_stop)
        if set(row['axioms']) != set(axiom_rows[declaration]):
            return {**base,'status':'failed','reason':'axiom extraction mismatch'}
        dependencies=sorted(set(row['dependencies']))
        if any(name not in dependency_hashes for name in dependencies):
            return {**base,'status':'failed','reason':'dependency output missing'}
        base['dependency_closure'][declaration]=dependencies
        base['declaration_evidence'][declaration]=row['evidence']
    # One body hash per constant of the closures; the rows it came from leave the output.
    base['dependency_evidence']={name:dependency_hashes[name] for names in base['dependency_closure'].values() for name in names}
    base['dependency_hash']=exact_content_hash(base['dependency_closure'])
    return {**base,'stdout':''.join(kept),'status':'verified','reason':None,'expression_encoding':'lean-expr-dag/1'}
