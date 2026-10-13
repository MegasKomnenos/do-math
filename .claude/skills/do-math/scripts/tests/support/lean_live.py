"""T5 installed Mathlib checks with real ports and passive file/Job observation.

ObservedCalls watches the real WindowsJob.close before the verifier removes its
temporary spool. It neither wraps nor replaces the Job, compiler or parser.
Only this invocation's files are copied to the official persistent scratch.
"""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

import setup_lean
from do_math import formal, trust_inventory
from do_math.canonical import exact_content_hash
from do_math.file_io import sha256_file
from do_math.lean_evidence import check_file, mathlib_project, READY_MARKER
from do_math.windows_job import WindowsJob, process_identity
from do_math.wiring import real_ports
from support.entry import entry
from support.provider_probes import ObservedCalls

SOURCE = ('import Mathlib\n'
          'theorem lean_smoke_add_zero (n : ℕ) : n + 0 = n := by rfl\n'
          'theorem lean_smoke_true : True := True.intro\n')
DECLARATIONS = ['lean_smoke_add_zero', 'lean_smoke_true']
SIGNATURES = {'lean_smoke_add_zero': 'lean_smoke_add_zero (n : ℕ) : n + 0 = n',
              'lean_smoke_true': 'lean_smoke_true : True'}
INVALID_SOURCE = SOURCE.replace('by rfl', 'True.intro')


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def installation_inputs(command):
    """Read configured inputs/records and installed dependency revisions; never repair them."""
    root = formal.toolchain_root()
    project = mathlib_project(root) if root else None
    files = {}
    for path in ([project / name for name in
                  ('lean-toolchain', 'lake-manifest.json', 'lakefile.toml', 'lakefile.lean', READY_MARKER)]
                 if project else []):
        if path.is_file(): files[str(path)] = sha256_file(path)
    if root:
        for path in (root / 'records').rglob('*'):
            if path.is_file(): files[str(path)] = sha256_file(path)
    manifest = json.loads((project / 'lake-manifest.json').read_bytes()) if project and (project / 'lake-manifest.json').is_file() else None
    dependencies = []
    for package in manifest.get('packages', []) if manifest else []:
        directory = project / manifest['packagesDir'] / package['name']
        observed = subprocess.run(['git', '-C', str(directory), 'rev-parse', 'HEAD'],
            capture_output=True, text=True, encoding='utf-8',
            creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        dependencies.append({'name':package['name'], 'url':package.get('url'),
            'manifest_rev':package.get('rev'), 'input_rev':package.get('inputRev'),
            'directory':str(directory), 'observed_rev':observed.stdout.strip(),
            'exit_code':observed.returncode, 'stderr':observed.stderr})
    return {'root':str(root) if root else None, 'command':command, 'files':files,
            'lean_toolchain':(project / 'lean-toolchain').read_text(encoding='utf-8') if project and (project / 'lean-toolchain').is_file() else None,
            'manifest':manifest, 'dependencies':dependencies,
            'executables':{str(Path(value)):sha256_file(Path(value)) for value in command or []
                           if Path(value).is_file() and Path(value).suffix.lower() == '.exe'}}


def run_lean_smoke():
    context = entry()
    context.ports = real_ports(environment=context.environment)
    ports = context.ports
    root = Path(tempfile.mkdtemp(prefix='lean-smoke-')).resolve()
    workspace = root / 'workspace'
    workspace.mkdir()
    report = {'evidence_directory':str(root), 'started_at':ports.clock.now(),
              'source':SOURCE, 'declarations':DECLARATIONS, 'extract_evidence':True,
              'checks':{}, 'jobs':[], 'commands':[], 'observation_errors':[]}
    jobs = []

    def observe_command(arguments):
        row = {'command':list(arguments['command']), 'cwd':str(arguments['cwd']),
               'started_at':ports.clock.now()}
        report['commands'].append(row)
        return row

    def preserve_close(arguments):
        try:
            return capture_close(arguments)
        except Exception as error:
            # An observation failure must fail the smoke without blocking real close.
            report['observation_errors'].append(f'{type(error).__name__}: {error}')
            return None

    def capture_close(arguments):
        job = arguments['self']
        # Find the unchanged transport frame; unrelated Job closures are ignored.
        frame = sys._getframe()
        while frame is not None and frame.f_code is not formal._job_run.__code__:
            frame = frame.f_back
        if frame is None: return None
        spool = frame.f_locals['root']
        destination = root / 'jobs' / str(len(report['jobs']) + 1)
        destination.mkdir(parents=True)
        for filename in ('request.json', 'out', 'err', 'status'):
            path = spool / filename
            if path.is_file(): shutil.copyfile(path, destination / filename)
        request = json.loads((destination / 'request.json').read_bytes())
        proposal = Path(request['command'][-1])
        if proposal.is_file() and proposal.suffix == '.lean':
            shutil.copyfile(proposal, destination / 'compiled.lean')
        inspection = job.inspect()
        row = {'directory':str(destination), 'spool':str(spool),
               'identity':process_identity(job), 'job_name':job.name,
               'finished_at':ports.clock.now(), 'root_ended':job.wait(0),
               'active_processes':inspection.active_processes,
               'process_ids':list(inspection.process_ids),
               'usage':job.resource_usage(), 'request':request}
        report['jobs'].append(row)
        jobs.append(job)
        write_json(destination / 'observed.json', row)
        return row

    try:
        command = formal.discover_lean()
        report['installation_before'] = installation_inputs(command)
        write_json(root / 'installation-before.json', report['installation_before'])
        with ObservedCalls(job_run=formal._job_run, close=WindowsJob.close,
                           new_calls=ports.calls.new,
                           capture={'job_run':observe_command, 'close':preserve_close,
                                    'new_calls':lambda arguments:{}}) as observed:
            # Observe before the first Lake command, including its own cached olean.
            seed_identity = {'executable':command[0], 'project':
                {'source_identity':{'root':str(mathlib_project(formal.toolchain_root()))}}}
            before = trust_inventory.observe_fingerprint(seed_identity)
            write_json(root / 'judgment-before.json', before)
            identity = formal.inspect_toolchain(command or [], workspace,
                jobs=ports.jobs, clock=ports.clock, environment=context.environment,
                git_backend=ports.git_backend)
            report['identity'] = identity
            write_json(root / 'identity.json', identity)
            validation = setup_lean.verify_environment(command, root / 'environment', identity,
                jobs=ports.jobs, clock=ports.clock, environment=context.environment)
            report['validation'] = validation
            for label, source in (('normal', SOURCE), ('invalid', INVALID_SOURCE)):
                (root / (label + '.lean')).write_bytes(source.encode('utf-8'))
                result = formal.verify_lean(source=source, declarations=DECLARATIONS,
                    workspace=workspace, lean_command=command, expected_toolchain=identity,
                    extract_evidence=True, jobs=ports.jobs, clock=ports.clock,
                    environment=context.environment, git_backend=ports.git_backend)
                report[label] = result
                write_json(root / (label + '.json'), result)
            after = trust_inventory.observe_fingerprint(identity)
            write_json(root / 'judgment-after.json', after)
            report['call_executors_created'] = observed.count('new_calls')
        report['installation_after'] = installation_inputs(command)
        write_json(root / 'installation-after.json', report['installation_after'])
        normal, invalid = report['normal'], report['invalid']
        normal_jobs = [row for row in report['jobs'] if row['request']['command'] == normal['command']]
        invalid_jobs = [row for row in report['jobs'] if row['request']['command'] == invalid['command']]
        report['normal_job'] = normal_jobs[0] if len(normal_jobs) == 1 else None
        report['invalid_job'] = invalid_jobs[0] if len(invalid_jobs) == 1 else None
        expected_source, scope = trust_inventory.validation_program(identity)
        report['checks'] = {
            'mathlib_identity':identity['project'] is not None and any(p['name'] == 'mathlib' for p in report['installation_before']['dependencies']),
            'dependencies_pinned':all(row['exit_code'] == 0 and row['observed_rev'] == row['manifest_rev'] for row in report['installation_before']['dependencies']),
            'representative_mathlib':scope == 'mathlib_import_and_representative_proofs' and validation['scope'] == scope and validation['source_text'] == expected_source and 'import Mathlib' in expected_source and validation['status'] == 'verified' and validation['exit_code'] == 0,
            'representative_source':validation['source_sha256'] == sha256_file(Path(validation['source'])),
            'kernel_success':normal['status'] == 'verified' and normal.get('exit_code') == 0 and normal['toolchain'] == identity,
            'exact_declarations':normal['declarations'] == DECLARATIONS and normal['declaration_signatures'] == SIGNATURES and set(normal['axioms']) == set(DECLARATIONS),
            'signature_hash':normal['signature_hash'] == exact_content_hash(SIGNATURES),
            'axioms':normal['axioms'] == {name:[] for name in DECLARATIONS},
            'full_evidence':set(normal['declaration_evidence']) == set(DECLARATIONS) and set(normal['dependency_closure']) == set(DECLARATIONS) and bool(normal.get('dependency_evidence')) and set(normal.get('dependency_evidence', {})) == {name for closure in normal['dependency_closure'].values() for name in closure},
            'proof_dependencies':{'Nat', 'Eq.refl'} <= set(normal['dependency_closure'].get(DECLARATIONS[0], [])) and {'True', 'True.intro'} <= set(normal['dependency_closure'].get(DECLARATIONS[1], [])),
            'type_error':invalid['status'] == 'failed' and invalid.get('exit_code') == 1 and invalid['reason'] == 'lean rejected' and 'type mismatch' in (invalid['stdout'] + invalid['stderr']).lower(),
            'raw_compiled_input':len(normal_jobs) == 1 and (Path(normal_jobs[0]['directory']) / 'compiled.lean').read_bytes() == check_file(SOURCE.encode(), DECLARATIONS, extract_evidence=True),
            'installation_unchanged':report['installation_before'] == report['installation_after'] and before == after,
        }
    except Exception as error:
        report['error'] = f'{type(error).__name__}: {error}'
        report['checks']['execution_completed'] = False
    finally:
        # Check the actual real objects after close, and the named kernel Job state.
        report['checks']['jobs_ended'] = bool(jobs) and all(row['root_ended'] and not row['active_processes'] for row in report['jobs'])
        report['checks']['jobs_closed'] = bool(jobs) and all(job._closed for job in jobs)
        report['checks']['named_jobs_empty'] = bool(jobs) and all(ports.jobs.named_job_empty(job.name) is True for job in jobs)
        report['checks']['temporary_proposals_removed'] = not list(workspace.rglob('proposal.lean'))
        report['checks']['observation_complete'] = not report['observation_errors']
        report['checks']['no_extra_calls'] = report.get('call_executors_created') == 0
        # The remaining identity-observation spools are ours and copied above.
        shutil.rmtree(workspace)
        report['checks']['workspace_removed'] = not workspace.exists()
        report['finished_at'] = ports.clock.now()
        report['passed'] = bool(report['checks']) and all(report['checks'].values())
        write_json(root / 'smoke.json', report)
    return report
