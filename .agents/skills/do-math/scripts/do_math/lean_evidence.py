"""Lean evidence rules (layer 1): the compiled check file, the parse of its output,
and the shape rules shared by registration, inspection and the knowledge records.

``formal`` runs the compiler and passes its output to ``parse_evidence``; recorded
compiler output (the corpus) goes through the same function.
"""
import hashlib
import json
from pathlib import Path
import re

from .canonical import exact_content_hash
from .values import is_sha256

# The approved axioms of a formal result; sorryAx is never approved (forbidden_axioms).
AXIOMS = ('propext', 'Classical.choice', 'Quot.sound')
LEAN_VERSION='4.32.0'; READY_MARKER='.do-math-ready'


class VerificationStopped(RuntimeError):
    pass


def _check_stop(should_stop):
    if should_stop and should_stop():
        raise VerificationStopped('verification stopped')


DEPENDENCY_EXTRACTOR = r'''
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


def is_lean_identifier(x: str) -> bool:
    """The declaration-name grammar that formal checks accept."""
    if not isinstance(x, str) or not x:
        return False
    parts = [part.rstrip("'") for part in x.split('.')]
    return all(part and part.replace('_', 'a').isalnum() and part[0].isalpha() for part in parts)


def portable_bin(root: Path) -> Path: return root/f'lean-{LEAN_VERSION}/lean-{LEAN_VERSION}-windows/bin'


def mathlib_project(root: Path) -> Path: return root/f'mathlib-{LEAN_VERSION}'


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



# The Lake project's input files; a project's identity covers them and its .lean sources.
LAKE_PROJECT_FILES = ('lean-toolchain', 'lake-manifest.json', 'lakefile.lean', 'lakefile.toml')


def check_completion_status(data) -> None:
    """The formal worker's status: exited with an integer exit code, or worker_error."""
    if (not isinstance(data, dict) or data.get('state') not in {'exited', 'worker_error'}
            or (data['state'] == 'exited' and type(data.get('exit')) is not int)):
        raise ValueError('invalid completion status')
    if 'os_error' in data:
        error = data['os_error']
        fields = {'errno', 'strerror', 'filename', 'winerror', 'filename2', 'message'}
        if (data['state'] != 'worker_error' or not isinstance(error, dict) or set(error) != fields
                or any(error[name] is not None and type(error[name]) is not int for name in ('errno', 'winerror'))
                or not isinstance(error['message'], str)
                or any(error[name] is not None and not isinstance(error[name], str)
                       for name in ('strerror', 'filename', 'filename2'))):
            raise ValueError('invalid completion OS error')


def is_lake_project_command(command) -> bool:
    """A Lake command that names its project with ``--dir``."""
    return Path(command[0]).name.lower().startswith('lake') and '--dir' in command


def lake_project_dir(command) -> str:
    """The project path after ``--dir`` in a Lake project command."""
    index = command.index('--dir') + 1
    if index >= len(command):
        raise ValueError('Lake --dir requires a project path')
    return command[index]


def project_inputs_changed(identity: dict, expected: dict | None) -> bool:
    """Changed project inputs; changed project code is never executed merely to discover its environment."""
    return expected is not None and any(identity[k] != expected.get(k) for k in identity)


def lake_env_prefix(command, workspace) -> list:
    """The ``lake ... env`` prefix that runs a program in the project's environment."""
    if workspace is None or 'env' not in command:
        raise ValueError('Lake environment observation requires env and an observation workspace')
    return command[:command.index('env') + 1]


def check_search_path_observation(observed) -> None:
    """The environment observation reports its cwd and a list of search paths."""
    if (not isinstance(observed, dict) or not isinstance(observed.get('cwd'), str)
            or not isinstance(observed.get('paths'), list) or any(not isinstance(p, str) for p in observed['paths'])):
        raise ValueError('invalid project environment observation')


def check_lean_command(command) -> None:
    """A Lean command is a nonempty list of nonempty, NUL-free strings."""
    if not command or any(not isinstance(p, str) or not p or '\x00' in p for p in command):
        raise ValueError('a nonempty Lean command is required')


def declaration_rejection(declarations) -> str | None:
    """Why the declarations to audit cannot be verified, or None."""
    if not all(is_lean_identifier(x) for x in declarations):
        return 'invalid declaration'
    if not declarations:
        return 'no declaration to audit'
    return None


def command_verdict(command) -> tuple[str, str] | None:
    """``(status, reason)`` when the Lean command cannot run, or None."""
    if not command or not command[0]:
        return 'unavailable', 'lean not found'
    if any(not isinstance(x, str) or '\x00' in x for x in command):
        return 'rejected', 'unsafe command'
    return None


def approved_toolchain_differs(expected: dict, command, executable: str) -> bool:
    """The approved toolchain names another command or executable than the one about to run."""
    return expected.get('configured_command') != command or expected.get('executable') != executable


def identity_rejection_reason(identity_errors) -> str:
    """The rejection reason for an approved toolchain whose local facts changed."""
    return ('approved project inputs changed before execution' if identity_errors == ['approved project inputs changed']
            else 'approved toolchain changed before execution')


def compiler_failure_reason(code: int, os_name: str) -> str:
    """A nonzero compiler exit: a crash (an NTSTATUS error on Windows, a signal elsewhere) or Lean's rejection."""
    crashed = (code & 0x80000000 != 0) if os_name == 'nt' else code < 0
    return 'compiler crashed' if crashed else 'lean rejected'


def check_file(raw: bytes, declarations: list[str], *, extract_evidence: bool) -> bytes:
    """The compiled file: ``import Lean``, the source, the signature and axiom
    audits and, when extracting evidence, the dependency extractor and its command."""
    checks='\n'.join('#eval "__DO_MATH_SIGNATURE_BEGIN_'+x+'__"\n#check '+x+'\n#eval "__DO_MATH_SIGNATURE_END_'+x+'__"\n#print axioms '+x for x in declarations)
    parts=[b'import Lean',raw,checks.encode()]
    if extract_evidence:
        parts+=[DEPENDENCY_EXTRACTOR.encode(),('#do_math_dependencies '+' '.join(declarations)).encode()]
    return b'\n'.join(parts)


def parse_evidence(base, declarations, allowed_axioms, should_stop=None, *, extract_evidence=True):
    """Consume one evidence row at a time; retain hashes, not every dependency body."""
    # Imported here: Job workers import this module only to start the compiler.
    from .canonical import exact_content_hash
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
    return {**base,'stdout':''.join(kept),'status':'verified','reason':None}
