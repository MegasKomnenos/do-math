import collections
import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import time

REPO = Path('C:/math')
RUN = REPO / 'docs/do-math/continuous-development-2026-10-13'
E = Path(__file__).resolve().parent
PY = Path(sys.executable)
BASE = RUN / 'phases/016/tasks/provenance-baseline/evidence/pre-provenance/scripts'
IDS = ['boundary.test_shared_input_provenance.SharedInputProvenanceTests.' + name for name in (
    'test_exact_baseline_literal_entries_opens_and_coverage_with_explicit_marker_differences',
    'test_exact_baseline_two_worker_raw_union')]

def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def write(path, data):
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def snapshot():
    return {p.relative_to(REPO).as_posix(): sha(p)
            for base in ('.claude/skills', '.agents/skills', '.agents/diff')
            for p in (REPO/base).rglob('*') if p.is_file() and '__pycache__' not in p.parts}

def baseline_check(label):
    m = read(RUN / 'phases/016/tasks/provenance-baseline/evidence/baseline-manifest.json')
    rows = []
    for row in m['files']:
        raw = (BASE / row['path']).read_bytes()
        blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        rows.append({'path': row['path'], 'sha256': hashlib.sha256(raw).hexdigest(), 'git_blob': blob,
                     'equal': blob == row['git_blob'] and hashlib.sha256(raw).hexdigest() == row['sha256']})
    files = sorted(p.relative_to(BASE).as_posix() for p in BASE.rglob('*') if p.is_file())
    data = {'baseline': str(BASE), 'commit': m['baseline_commit'], 'introduction': m['introduction_commit'],
            'files': rows, 'population_equal': files == sorted(r['path'] for r in m['files']),
            'all_equal': all(r['equal'] for r in rows)}
    write(E / (label + '-baseline.json'), data)
    assert data['all_equal'] and data['population_equal']

def execute(label, argv, *, output=None, external_temp=False):
    env = os.environ.copy()
    env['SHARED_INPUT_BASELINE_SCRIPTS'] = str(BASE)
    if external_temp:
        scratch = Path(tempfile.mkdtemp(prefix='dm018-', dir=tempfile.gettempdir())).resolve()
        assert not scratch.is_relative_to(REPO)
    else:
        scratch = E / 'scratch' / label
        scratch.mkdir(parents=True, exist_ok=False)
    env['TEMP'] = env['TMP'] = env['TMPDIR'] = str(scratch)
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    receipt = {'argv': list(map(str, argv)), 'cwd': str(REPO), 'started': now(),
               'environment': {k: env[k] for k in ('SHARED_INPUT_BASELINE_SCRIPTS','TEMP','TMP','TMPDIR','PYTHONDONTWRITEBYTECODE')},
               'external_temp': external_temp,
               'parent_pid': os.getpid(), 'output': str(output) if output else None}
    if external_temp:
        probe_argv = ['git','-C',str(scratch),'rev-parse','--show-toplevel']
        probe = subprocess.run(probe_argv, capture_output=True, text=True, env=env)
        receipt['temp_git_probe'] = {'argv':probe_argv,'cwd':str(REPO),'exit_code':probe.returncode,
                                     'stdout':probe.stdout,'stderr':probe.stderr}
        assert probe.returncode == 128 and not probe.stdout, receipt['temp_git_probe']
    before = snapshot()
    write(E / (label + '-source-before.json'), before)
    with (E / (label + '.stdout')).open('wb') as stdout, (E / (label + '.stderr')).open('wb') as stderr:
        start = time.monotonic()
        p = subprocess.Popen(list(map(str, argv)), cwd=REPO, env=env, stdout=stdout, stderr=stderr)
        receipt['pid'] = p.pid
        write(E / (label + '.command.json'), receipt)
        code = p.wait()
    receipt.update(ended=now(), exit_code=code, seconds=time.monotonic()-start)
    after = snapshot()
    write(E / (label + '-source-after.json'), after)
    receipt['source_changes'] = [path for path in before if before[path] != after[path]]
    write(E / (label + '.command.json'), receipt)
    print(label, 'exit', code, 'seconds', round(receipt['seconds'], 1), flush=True)
    if output and (Path(output) / 'report.json').exists():
        d = read(Path(output) / 'report.json')
        print('report', {k: d.get(k) for k in ('complete','successful','tests_run')},
              dict(collections.Counter(r['outcome'] for r in d.get('rows', []))), flush=True)
    return code

def main():
    mode = sys.argv[1]
    if mode == 'start':
        old = read(RUN / 'phases/017/manager-evidence/source-inspected.json')
        current = snapshot()
        write(E / 'source-start.json', current)
        diff = [p for p in old if old[p] != current[p]]
        import coverage
        write(E / 'environment.json', {'python': sys.version, 'executable': str(PY), 'python_sha256': sha(PY),
              'coverage': coverage.__version__, 'coverage_file': coverage.__file__, 'coverage_sha256': sha(coverage.__file__),
              'platform': platform.platform(), 'cwd': str(REPO), 'baseline': str(BASE),
              'start_source_count': len(current), 'different_from_017': diff,
              'head': subprocess.check_output(['git','rev-parse','HEAD'], cwd=REPO, text=True).strip()})
        baseline_check('start')
        print('start', len(current), 'changes', diff, flush=True)
        assert not diff
    elif mode in ('exact','full','full-short','list'):
        tree = sys.argv[2]
        scripts = REPO / ('.claude' if tree == 'canonical' else '.agents') / 'skills/do-math/scripts'
        suffix = '-' + sys.argv[3] if len(sys.argv)>3 else ''
        full_mode = mode in ('full','full-short')
        output = E / (('c4' if tree=='canonical' else 'm4') if mode=='full-short' else tree + ('-t4-full' if full_mode else '-exact') + suffix)
        args = ['--tier','T4'] if full_mode or mode=='list' else IDS
        label = tree + ('-t4-short' if mode=='full-short' else '-t4-list' if mode=='list' else '-t4-full' if full_mode else '-exact') + suffix
        argv = [PY,'-u','-B',scripts/'run_tests.py', *args, '--jobs','1']
        if mode == 'list': argv += ['--list']
        else: argv += ['--output',output]
        sys.exit(execute(label, argv, output=output if mode != 'list' else None, external_temp=full_mode))
    elif mode == 'companion':
        sys.exit(execute('canonical-companion',[PY,'-u','-B',E/'raw_companion.py']))
    elif mode == 'probe-path':
        sys.exit(execute('probe-path-'+sys.argv[2],[PY,'-u','-B',E/'probe_path_observer.py',sys.argv[2]]))
    elif mode == 'verify':
        label = 'verify-' + '-'.join(sys.argv[2:])
        sys.exit(execute(label,[PY,'-u','-B',E/'verify_task.py',*sys.argv[2:]]))
    elif mode == 'mirror-build':
        sys.exit(execute('mirror-build',[PY,'-u','-B',REPO/'.claude/skills/writing-skills/scripts/build_skill_mirrors.py']))
    elif mode == 'mirror-check':
        sys.exit(execute('mirror-check',[PY,'-u','-B',REPO/'.claude/skills/writing-skills/scripts/build_skill_mirrors.py','--check']))
    elif mode == 'skill':
        sys.exit(execute('skill',[PY,'-u','-B',REPO/'.claude/skills/do-math/scripts/probe_cli.py','--skill-only']))
    elif mode == 'observe':
        sys.exit(execute('observe-'+sys.argv[2], [PY,'-u','-B',E/'observe_job.py',sys.argv[2]], external_temp=True))
    elif mode == 'related':
        tree = sys.argv[2]
        scripts = REPO / ('.claude' if tree == 'canonical' else '.agents') / 'skills/do-math/scripts'
        label = tree + '-related'
        output = E / ('cr' if tree == 'canonical' else 'mr')
        sys.exit(execute(label, [PY,'-u','-B',scripts/'run_tests.py','boundary.test_port_jobs','contracts.test_port_jobs','--jobs','1','--output',output], output=output, external_temp=True))
    elif mode == 'exact-job':
        output = E/'cj'
        scripts = REPO/'.claude/skills/do-math/scripts'
        sys.exit(execute('canonical-exact-job',[PY,'-u','-B',scripts/'run_tests.py','boundary.test_port_jobs.WindowsJobsContract.test_a_job_resumes_only_once','--jobs','1','--output',output],output=output,external_temp=True))
    elif mode == 'finish':
        write(E / 'source-final.json', snapshot())
        baseline_check('final')

if __name__ == '__main__':
    main()
