"""Complete installation inventories and self-contained environment evidence.

The declared roots are the adopted scope. Files are enumerated by one fixed
rule at collection and at every observation; a role label is not completeness.
"""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import stat

SMOKE = 'import Mathlib\nexample (n : Nat) : n + 0 = n := by rfl\nexample : (2 : ℝ) + 2 = 4 := by norm_num\n'
CORE_SMOKE = 'example (n : Nat) : n + 0 = n := by rfl\nexample : True := True.intro\n'
EXCLUDED_DIRECTORIES = frozenset({'.git', '__pycache__'})
KINDS = frozenset({'toolchain', 'project', 'checker'})


def validation_program(toolchain):
    return ((SMOKE, 'mathlib_import_and_representative_proofs') if toolchain.get('project') is not None
            else (CORE_SMOKE, 'lean_core_representative_proofs'))


def _key(path):
    return os.path.normcase(os.path.normpath(str(path)))


def scope_errors(scope):
    if not isinstance(scope, dict) or set(scope) != {'roots'} or not isinstance(scope['roots'], list) or not scope['roots']:
        return ['inventory scope requires a nonempty roots list']
    paths, kinds, errors = [], [], []
    for root in scope['roots']:
        if (not isinstance(root, dict) or set(root) != {'path', 'kind'} or root.get('kind') not in KINDS
                or not isinstance(root.get('path'), str) or not Path(root['path']).is_absolute()):
            errors.append('inventory root requires an absolute path and a supported kind')
            continue
        path = Path(_key(root['path']))
        if any(path == prior or path.is_relative_to(prior) or prior.is_relative_to(path) for prior in paths):
            errors.append('inventory roots must be distinct and nonoverlapping')
        paths.append(path); kinds.append(root['kind'])
    if kinds.count('toolchain') != 1 or kinds.count('checker') != 1 or kinds.count('project') > 1:
        errors.append('inventory requires one toolchain, one checker and at most one project root')
    return errors


def file_role(root, relative):
    parts = relative.parts
    if root['kind'] == 'checker':
        return 'checker'
    if root['kind'] == 'project':
        return 'mathlib_build' if '.lake' in parts and 'build' in parts else 'mathlib_source'
    if relative.name.lower() in {'lake', 'lake.exe'}:
        return 'lake_binary'
    return 'lean_source' if parts and parts[0] == 'src' else 'lean_binary'


def _ordinary(path):
    for parent in (path, *path.parents):
        stat = parent.lstat()
        if parent.is_symlink() or getattr(stat, 'st_file_attributes', 0) & 0x400:
            raise ValueError('inventory path crosses a reparse point: ' + str(parent))


def inventory(scope, *, should_stop=None):
    errors = scope_errors(scope)
    if errors:
        raise ValueError('; '.join(errors))
    result = {}
    for root in scope['roots']:
        base = Path(root['path'])
        _ordinary(base)
        if not base.is_dir():
            raise ValueError('inventory root is not a directory: ' + str(base))
        def unreadable(error):
            raise error
        for directory, dirs, files in os.walk(base, followlinks=False, onerror=unreadable):
            if should_stop and should_stop():
                raise InterruptedError('inventory observation cancelled')
            dirs[:] = sorted(d for d in dirs if d not in EXCLUDED_DIRECTORIES)
            for name in dirs:
                path = Path(directory) / name
                stat = path.lstat()
                if path.is_symlink() or getattr(stat, 'st_file_attributes', 0) & 0x400:
                    raise ValueError('inventory directory crosses a reparse point: ' + str(path))
            for name in sorted(files):
                if name == '.do-math-ready' or name.endswith('.pyc'):
                    continue
                path = Path(directory) / name
                relative = path.relative_to(base)
                key=_key(path)
                if key in result:
                    raise ValueError('inventory paths have an ambiguous identity: '+str(path))
                result[key] = {'path': str(path), 'role': file_role(root, relative)}
    return result


def binding_errors(environment):
    manifest, chain = environment['manifest'], environment['toolchain']
    errors = scope_errors(manifest.get('scope'))
    if errors:
        return errors
    roots = {row['kind']:Path(_key(row['path'])) for row in manifest['scope']['roots']}
    files = {_key(row['path']):row for row in manifest['files'] if isinstance(row, dict) and isinstance(row.get('path'), str)}
    for entry in manifest['files']:
        if not isinstance(entry, dict) or not isinstance(entry.get('path'), str):
            continue
        path=Path(_key(entry['path']))
        matches=[r for r in manifest['scope']['roots'] if path.is_relative_to(Path(_key(r['path'])))]
        if len(matches)!=1 or entry.get('role')!=file_role(matches[0],path.relative_to(Path(_key(matches[0]['path'])))):
            errors.append('manifest file role or scope differs: ' + entry['path'])
    executables=chain.get('executables', {})
    if not executables or executables.get(chain.get('executable')) != chain.get('sha256'):
        errors.append('toolchain executable must have an exact inventory binding')
    for path,digest in executables.items():
        row=files.get(_key(path))
        if (not Path(path).is_absolute() or not Path(_key(path)).is_relative_to(roots['toolchain'])
                or row is None or row.get('sha256')!=digest):
            errors.append('configured executable is absent or differs from inventory: ' + path)
    checkers=[r for r in manifest['files'] if r.get('role')=='checker'
              and _key(r['path'])==_key(chain.get('verifier_path',''))]
    if len(checkers)!=1 or checkers[0].get('sha256')!=chain.get('verifier_sha256'):
        errors.append('formal checker must have an exact inventory binding')
    project=chain.get('project')
    if project is None:
        if 'project' in roots:errors.append('inventory project has no observed toolchain project')
    elif (not isinstance(project,dict) or not isinstance(project.get('fingerprint'),dict)
          or _key(project['fingerprint'].get('root','')) != str(roots.get('project',''))):
        errors.append('inventory project differs from the observed toolchain project')
    if isinstance(project,dict):
        for path in project.get('search_paths',[]):
            if not any(Path(_key(path)).is_relative_to(root) for kind,root in roots.items() if kind!='checker'):
                errors.append('Lean search path is outside the adopted installation roots: '+path)
    if not any(r.get('role')=='lean_source' for r in manifest['files']):
        errors.append('toolchain inventory lacks Lean sources')
    return errors


def validation_errors(validation, toolchain, inventory_digest):
    from .repository import exact_content_hash
    if not isinstance(validation,dict) or set(validation)!={'record','sha256'}:
        return ['validation requires a sealed self-contained record']
    record=validation['record']
    if not isinstance(record,dict) or validation['sha256']!=exact_content_hash(record):
        return ['validation record hash differs']
    errors=[]
    source_text, scope = validation_program(toolchain)
    if record.get('inventory_sha256') != inventory_digest:
        errors.append('validation does not bind this complete inventory')
    if (record.get('status')!='verified' or type(record.get('exit_code')) is not int or record['exit_code']!=0
            or record.get('scope')!=scope):
        errors.append('validation did not successfully check the required environment examples')
    if record.get('toolchain')!=toolchain or record.get('toolchain_after')!=toolchain:
        errors.append('validation toolchain differs from the adopted environment')
    if (record.get('source_text')!=source_text or record.get('source_sha256')!=hashlib.sha256(source_text.encode()).hexdigest()
            or not isinstance(record.get('source'),str) or not Path(record['source']).is_absolute()
            or record.get('command')!=[*toolchain.get('configured_command',[]),record.get('source')]):
        errors.append('validation source or invocation differs')
    if any(not isinstance(record.get(k),str) for k in ('stdout','stderr','started_at','finished_at')):
        errors.append('validation output and observation times are required')
    else:
        from .governance import timestamp
        try:
            if timestamp(record['finished_at'])<timestamp(record['started_at']):
                raise ValueError('validation time order')
        except (ValueError,TypeError):errors.append('validation observation times are invalid')
    return errors


def collect_inventory(toolchain):
    executable=Path(toolchain['executable'])
    tool_root=executable.parent.parent if executable.parent.name=='bin' else executable.parent
    roots=[{'kind':'toolchain','path':str(tool_root)}, {'kind':'checker','path':str(Path(toolchain['verifier_path']).parent)}]
    if toolchain.get('project') is not None:
        roots.append({'kind':'project','path':toolchain['project']['fingerprint']['root']})
    scope={'roots':roots}
    members=inventory(scope)
    def hashed(entry):
        info=Path(entry['path']).lstat()
        if not stat.S_ISREG(info.st_mode) or getattr(info,'st_file_attributes',0)&0x400:
            raise ValueError('inventory member is not an ordinary file: '+entry['path'])
        with open(entry['path'],'rb') as stream:
            digest=hashlib.file_digest(stream,'sha256').hexdigest()
        return {**entry,'sha256':digest}
    # Executor.map eagerly submits its iterable on Python 3.12. Bound each batch.
    files=[]; entries=list(members.values())
    with ThreadPoolExecutor(max_workers=4) as pool:
        for start in range(0,len(entries),64):files.extend(pool.map(hashed,entries[start:start+64]))
    if inventory(scope)!=members:
        raise ValueError('inventory membership changed during collection')
    return {'scope':scope,'files':files}


def collect_manifest(toolchain, validation_record, *, observed_inventory=None):
    from .repository import exact_content_hash
    observed=collect_inventory(toolchain) if observed_inventory is None else observed_inventory
    scope,files=observed['scope'],observed['files']
    manifest={'command':toolchain['configured_command'],'scope':scope,'files':files,
        'foundation_profile':{'allowed_axioms':['Classical.choice','Quot.sound','propext'],
                              'forbidden':['sorryAx','Lean.trustCompiler','additional_axioms']},
        'validation':{'record':validation_record,'sha256':exact_content_hash(validation_record)}}
    errors=binding_errors({'manifest':manifest,'toolchain':toolchain})+validation_errors(
        manifest['validation'],toolchain,exact_content_hash(observed))
    if errors:raise ValueError('; '.join(errors))
    return manifest
