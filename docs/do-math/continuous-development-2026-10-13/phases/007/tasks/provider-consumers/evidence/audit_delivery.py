"""Task-local evidence: source ownership, official mirror plan, and corpus bytes."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone

from run_command import ROOT, EVIDENCE, snapshot, changed, write_json

RUN = ROOT / 'docs/do-math/continuous-development-2026-10-13'
PREVIOUS = RUN / 'phases/006/tasks/codex-schema/evidence'


def read(path):
    return json.loads(path.read_bytes())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def command(argv):
    begun = datetime.now(timezone.utc).isoformat()
    process = subprocess.Popen(argv, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    return {'argv': argv, 'cwd': str(ROOT), 'pid': process.pid, 'started_at': begun,
            'ended_at': datetime.now(timezone.utc).isoformat(), 'exit_code': process.returncode,
            'stdout': stdout.decode('utf-8'), 'stderr': stderr.decode('utf-8')}


def allowed(paths):
    writes = read(RUN / 'phases/007/phase.json')['tasks'][0]['writes']
    return all(p in writes for p in paths)


def plan(label):
    spec = importlib.util.spec_from_file_location('mirror_builder', ROOT / '.claude/skills/writing-skills/scripts/build_skill_mirrors.py')
    builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)
    rules = builder.load_rules(ROOT / '.agents/diff')
    base = builder.iter_files(ROOT / builder.BASE_REL)
    overlays = {r: p for r, p in builder.iter_files(ROOT / '.agents/diff').items() if r not in builder.RESERVED}
    outputs = {r: builder.transform(r, p.read_bytes(), rules) for r, p in base.items()}
    outputs.update({r: p.read_bytes() for r, p in overlays.items()})
    existing = builder.iter_files(ROOT / '.agents/skills')
    differences = ['.agents/skills/' + r for r in sorted(outputs.keys() | existing.keys())
                   if r not in outputs or r not in existing or outputs[r] != existing[r].read_bytes()]
    manifest = {'overlays': {r: builder.sha1(base[r].read_bytes()) for r in sorted(overlays) if r in base}}
    manifest_bytes = (json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + '\n').replace('\n', os.linesep).encode('utf-8')
    ok, messages = builder.build_target('.agents', check=True, bless=False)
    result = {'changed': differences, 'outputs': len(outputs), 'check_ok': ok, 'messages': messages,
              'overlay_manifest_unchanged': (ROOT / '.agents/diff/_manifest.json').read_bytes() == manifest_bytes,
              'changes_since_start': changed(read(EVIDENCE / 'source-start.json'), snapshot()),
              'status': command(['git', '--no-optional-locks', '-c', 'core.quotepath=false', 'status', '--porcelain=v1'])}
    write_json(EVIDENCE / (label + '.json'), result)
    assert allowed(differences + result['changes_since_start']), result
    assert result['overlay_manifest_unchanged']
    print(json.dumps({k: v for k, v in result.items() if k != 'status'}, ensure_ascii=False))


def corpus():
    trees, paths = {}, []
    initial = read(EVIDENCE / 'source-start.json')
    for runtime in ('.claude', '.agents'):
        base = ROOT / runtime / 'skills/do-math/scripts/tests/corpus'
        files = {p.relative_to(base).as_posix(): p for p in sorted(base.rglob('*')) if p.is_file()}
        manifest = read(base / 'manifest.json')
        rows = {r: {'path': p.relative_to(ROOT).as_posix(), 'bytes': p.stat().st_size, 'sha256': sha(p)} for r, p in files.items()}
        bindings = []
        for entry in manifest['entries']:
            for field, key in (('path', 'source_sha256'), ('schema_path', 'schema_sha256'),
                               ('transport_schema_path', 'transport_schema_sha256')):
                if key in entry:
                    bindings.append({'entry': entry['id'], 'key': key, 'path': entry[field], 'expected': entry[key]})
            for recording in entry.get('recordings', []):
                bindings.append({'entry': entry['id'], 'key': 'recordings.sha256', 'path': recording['path'],
                                 'expected': recording['sha256']})
        for binding in bindings:
            binding['actual'] = rows[binding['path']]['sha256']
            assert binding['actual'] == binding['expected'], binding
        assert all(initial[row['path']] == row['sha256'] for row in rows.values())
        prefix = (base.relative_to(ROOT).as_posix() + '/')
        assert {row['path'] for row in rows.values()} == {p for p in initial if p.startswith(prefix)}
        trees[runtime] = {'entry_count': len(manifest['entries']), 'file_count': len(files), 'files': rows,
                          'bytes': sum(row['bytes'] for row in rows.values()), 'bindings': bindings, 'unchanged': True}
        assert (len(manifest['entries']), len(files), trees[runtime]['bytes'], len(bindings)) == (18, 51, 223685, 50)
        paths.extend(row['path'] for row in rows.values())
    assert {p: r['sha256'] for p, r in trees['.claude']['files'].items()} == {p: r['sha256'] for p, r in trees['.agents']['files'].items()}
    commands = [command(['git', 'hash-object', '--no-filters', *paths]), command(['git', 'hash-object', *paths]),
                command(['git', 'check-attr', '--all', '--', *paths])]
    assert all(c['exit_code'] == 0 for c in commands)
    raw, clean = [c['stdout'].splitlines() for c in commands[:2]]
    assert len(paths) == len(set(paths)) == len(raw) == len(clean) == 102
    git_rows = [{'path': p, 'raw': a, 'clean': b, 'matches': a == b} for p, a, b in zip(paths, raw, clean, strict=True)]
    write_json(EVIDENCE / 'corpus-final.json', {'trees': trees, 'commands': commands, 'git_rows': git_rows})
    assert all(row['matches'] for row in git_rows)
    return {k: {field: v[field] for field in ('entry_count', 'file_count', 'bytes', 'unchanged')} for k, v in trees.items()}


def final():
    sources = snapshot()
    write_json(EVIDENCE / 'source-final.json', sources)
    changes = changed(read(EVIDENCE / 'source-start.json'), sources)
    assert allowed(changes), changes
    checks = {}
    for label in ('pair-red', 'pair-green', 'consumers', 'raw-green', 'consumers-final', 'boundaries', 'corpus', 'mirror'):
        report = read(EVIDENCE / label / 'report.json')
        rows = [row for group in report['reports'] for row in group['rows']]
        ids = [row['id'] for row in rows]
        process = read(EVIDENCE / (label + '-command') / 'command.json')
        base = ROOT / ('.agents' if label == 'mirror' else '.claude') / 'skills/do-math/scripts'
        current = {p.relative_to(base).as_posix(): sha(p) for p in base.rglob('*.py')}
        checks[label] = {'selected': len(report['selected']), 'rows': len(ids), 'unique_rows': len(set(ids)),
                         'counts': report['counts'], 'complete': report['complete'], 'successful': report['successful'],
                         'exit_code': process['exit_code'], 'changed_during_run': report['changed_during_run'],
                         'python_changes_since_run': changed(report['source_sha256'], current),
                         'changed_sources': process['changed_sources']}
        assert set(ids) == set(report['selected']) and len(ids) == len(set(ids))
        assert report['complete'] and not report['changed_during_run']
        assert all(p.endswith('/.timings.json') for p in process['changed_sources'])
        if label == 'pair-red':
            assert process['exit_code'] == 1 and report['counts'] == {'failed': 1}
        elif label == 'consumers':
            assert process['exit_code'] == 1 and report['counts'] == {'passed': 97, 'failed': 1}
        else:
            assert report['successful'] and process['exit_code'] == 0
            assert report['counts'] == {'passed': len(ids)}, report['counts']
            if label != 'pair-green':
                assert not checks[label]['python_changes_since_run']
    old_rows = read(EVIDENCE / 'previous-failures.json')
    now_rows = {row['id']: row for group in read(EVIDENCE / 'consumers-final/report.json')['reports'] for row in group['rows']}
    recovered = {row['id']: now_rows[row['id']]['outcome'] for row in old_rows}
    assert len(recovered) == 11 and set(recovered.values()) == {'passed'}
    manager = read(RUN / 'phases/006/manager-evidence/verification.json')
    runtime = manager['runtime_unchanged_since_live']
    live = read(PREVIOUS / 'live-command/source-before.json')
    assert len(runtime) == 124
    assert all(sources[p] == live[p] for p in runtime)
    smoke_inputs = ['.claude/skills/do-math/scripts/' + p for p in
                    ('tests/support/provider_live.py', 'tests/smoke/test_provider_live.py', 'probe_cli.py')]
    assert all(sources[p] == live[p] for p in smoke_inputs)
    result = {'source_count': len(sources), 'changes': changes, 'checks': checks, 'recovered_failures': recovered,
              'runtime_unchanged_since_live': runtime, 'smoke_inputs_unchanged': smoke_inputs,
              'corpus': corpus(), 'head': command(['git', 'rev-parse', 'HEAD']),
              'status': command(['git', '--no-optional-locks', 'status', '--porcelain=v1'])}
    assert result['head']['stdout'].strip() == read(EVIDENCE / 'start-state.json')['head']
    assert read(EVIDENCE / 'mirror-build-command/command.json')['changed_sources'] == read(EVIDENCE / 'mirror-plan.json')['changed']
    assert read(EVIDENCE / 'cache-plan.json')['changed'] == ['.agents/skills/do-math/scripts/tests/.timings.json']
    assert read(EVIDENCE / 'cache-sync-command/command.json')['changed_sources'] == read(EVIDENCE / 'cache-plan.json')['changed']
    write_json(EVIDENCE / 'verification-final.json', result)
    print(json.dumps({k: v for k, v in result.items() if k not in ('status', 'runtime_unchanged_since_live')}, ensure_ascii=False))


if __name__ == '__main__':
    if sys.argv[1] == 'final':
        final()
    else:
        plan(sys.argv[1])
