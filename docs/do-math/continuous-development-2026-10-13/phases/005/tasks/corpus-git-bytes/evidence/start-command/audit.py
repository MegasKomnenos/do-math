"""Task-local read-only byte comparisons and mirror generation preflight."""
import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(r'C:\math')
OUT = Path(__file__).resolve().parent
RUN = ROOT / 'docs/do-math/continuous-development-2026-10-13'
OLD = RUN / 'phases/004/tasks/mirror-corpus/evidence'
WRITES = json.loads((RUN / 'phases/005/phase.json').read_bytes())['tasks'][0]['writes']


def read(path):
    return json.loads(path.read_bytes())


def save(name, data):
    (OUT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def changed(a, b):
    return [p for p in sorted(a.keys() | b.keys()) if a.get(p) != b.get(p)]


def snapshot():
    paths = {ROOT / '.gitattributes'}
    for rel in ('.claude/skills', '.agents/skills', '.agents/diff', 'services/continuous-development'):
        paths.update(p for p in (ROOT / rel).rglob('*')
                     if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc')
    return {p.relative_to(ROOT).as_posix(): sha(p) for p in sorted(paths)}


def command(argv):
    record = {'argv': argv, 'cwd': str(ROOT), 'wrapper_pid': os.getpid(),
              'started_at': datetime.datetime.now(datetime.timezone.utc).isoformat()}
    process = subprocess.Popen(argv, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    record.update(pid=process.pid, ended_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  exit_code=process.returncode, stdout=stdout.decode('utf-8'), stderr=stderr.decode('utf-8'))
    return record


def corpus():
    trees, paths = {}, []
    for runtime in ('.claude', '.agents'):
        base = ROOT / runtime / 'skills/do-math/scripts/tests/corpus'
        files = {p.relative_to(base).as_posix(): p for p in sorted(base.rglob('*')) if p.is_file()}
        manifest = read(files['manifest.json'])
        rows = {rel: {'path': p.relative_to(ROOT).as_posix(), 'bytes': p.stat().st_size, 'sha256': sha(p)}
                for rel, p in files.items()}
        bindings, references = [], []
        for entry in manifest['entries']:
            for field in ('path', 'final_path', 'source_path', 'compiled_path', 'schema_path'):
                if field in entry:
                    references.append({'entry': entry['id'], 'field': field, 'path': entry[field]})
            for field, hashfield in (('path', 'source_sha256'), ('schema_path', 'schema_sha256')):
                if hashfield in entry:
                    bindings.append({'entry': entry['id'], 'field': hashfield,
                                     'path': entry[field], 'expected': entry[hashfield]})
            for recording in entry.get('recordings', []):
                references.append({'entry': entry['id'], 'field': 'recordings', 'path': recording['path']})
                bindings.append({'entry': entry['id'], 'field': 'recordings.sha256',
                                 'path': recording['path'], 'expected': recording['sha256']})
        for binding in bindings:
            binding['actual'] = rows.get(binding['path'], {}).get('sha256')
            binding['matches'] = binding['expected'] == binding['actual']
        trees[runtime] = {'entry_count': len(manifest['entries']), 'file_count': len(files),
                          'bytes': sum(r['bytes'] for r in rows.values()), 'files': rows,
                          'manifest': manifest, 'references': references, 'sha_bindings': bindings,
                          'missing_references': [r for r in references if r['path'] not in files],
                          'bad_bindings': [r for r in bindings if not r['matches']],
                          'undeclared': sorted(set(files) - {r['path'] for r in references}
                                               - {'manifest.json', '.gitattributes'})}
        paths.extend(r['path'] for r in rows.values())
    assert len(paths) == len(set(paths)) == 88
    commands = [command(['git', 'hash-object', '--no-filters', *paths]),
                command(['git', 'hash-object', *paths]),
                command(['git', 'check-attr', '--all', '--', *paths])]
    assert all(c['exit_code'] == 0 for c in commands), commands
    raw, clean = [c['stdout'].splitlines() for c in commands[:2]]
    assert len(raw) == len(clean) == len(paths)
    git_rows = [{'path': p, 'raw_object_id': a, 'clean_object_id': b, 'matches': a == b}
                for p, a, b in zip(paths, raw, clean, strict=True)]
    return {'trees': trees, 'git_commands': commands, 'git_rows': git_rows,
            'git_differences': [r for r in git_rows if not r['matches']],
            'path_count': len(paths), 'raw_line_count': len(raw), 'clean_line_count': len(clean),
            'unique_path_count': len(set(paths))}


def reuse(sources):
    result = {}
    for runtime, label in (('.claude', 'canonical-replay'), ('.agents', 'mirror-replay')):
        report = read(OLD / label / 'report.json')
        cmd = read(OLD / (label + '-command') / 'command.json')
        base = ROOT / runtime / 'skills/do-math/scripts'
        current = {p.relative_to(base).as_posix(): sha(p) for p in sorted(base.rglob('*.py'))}
        rows = [r for g in report['reports'] for r in g['rows']]
        selected, ids = report['selected'], [r['id'] for r in rows]
        result[label] = {'report_sha256': sha(OLD / label / 'report.json'),
                         'selected': len(selected), 'rows': len(rows), 'counts': report['counts'],
                         'python_files': len(current), 'python_mismatches': changed(current, report['source_sha256']),
                         'exit_code': cmd['exit_code'], 'rerun': False}
        assert report['complete'] and report['successful'] and not report['changed_during_run']
        assert report['counts'] == {'passed': 14} and not report['fixture_counts']
        assert len(selected) == len(set(selected)) == len(ids) == len(set(ids)) == 14
        assert set(selected) == set(ids) and all(r['outcome'] == 'passed' for r in rows)
        assert all(g['complete'] and g['successful'] and g['tests_run'] == len(g['rows']) for g in report['reports'])
        assert cmd['exit_code'] == 0 and len(current) == 864 and not result[label]['python_mismatches']
    generator = read(OLD / 'generator-tests/command.json')
    before = read(OLD / 'generator-tests/source-before.json')
    after = read(OLD / 'generator-tests/source-after.json')
    relevant = ['.agents/diff/_rules.json', '.claude/skills/writing-skills/scripts/build_skill_mirrors.py',
                '.claude/skills/writing-skills/scripts/test_build_skill_mirrors.py']
    stderr = (OLD / 'generator-tests/stderr.txt').read_text(encoding='utf-8')
    assert generator['exit_code'] == 0 and 'Ran 22 tests' in stderr and stderr.rstrip().endswith('OK')
    assert all(before[p] == after[p] == sources[p] for p in relevant)
    result['generator-tests'] = {'exit_code': generator['exit_code'], 'tests': 22, 'rerun': False,
                                 'input_sha256': {p: sources[p] for p in relevant},
                                 'stderr_sha256': sha(OLD / 'generator-tests/stderr.txt')}
    return result


def observe(stage):
    sources = snapshot()
    save('source-' + stage + '.json', sources)
    current = corpus()
    save('corpus-' + stage + '.json', current)
    old = read(OLD / 'corpus-final.json')
    old_sources = read(OLD / 'source-final.json')
    compared = {'source_count': len(sources), 'phase004_source_count': len(old_sources),
                'phase004_source_changes': changed(old_sources, sources), 'corpus': {},
                'reused': reuse(sources), 'git_differences': current['git_differences']}
    for runtime, tree in current['trees'].items():
        previous = old['trees'][runtime]
        differences = changed(previous['files'], tree['files'])
        compared['corpus'][runtime] = {'entries': tree['entry_count'], 'files': tree['file_count'],
                                     'bytes': tree['bytes'], 'sha_bindings': len(tree['sha_bindings']),
                                     'phase004_file_changes': differences}
        assert tree['entry_count'] == 17 and tree['file_count'] == 44
        assert len(tree['sha_bindings']) == 41 and not tree['bad_bindings']
        assert not tree['undeclared'] and not tree['missing_references']
        assert tree['references'] == previous['references'] and tree['sha_bindings'] == previous['sha_bindings']
        assert differences == ([] if stage == 'start' else ['.gitattributes'])
    canonical = {k: v['sha256'] for k, v in current['trees']['.claude']['files'].items()}
    mirror = {k: v['sha256'] for k, v in current['trees']['.agents']['files'].items()}
    assert canonical == mirror
    if stage == 'start':
        expected = read(RUN / 'phases/004/manager-evidence/git-clean-observation.json')['differences']
        assert current['git_differences'] == expected and not compared['phase004_source_changes']
        env = {'head': command(['git', 'rev-parse', 'HEAD']), 'git_version': command(['git', '--version']),
               'status': command(['git', '--no-optional-locks', '-c', 'core.quotepath=false', 'status', '--porcelain=v1', '--untracked-files=all'])}
        save('environment-start.json', env)
        assert all(c['exit_code'] == 0 for c in env.values())
        compared['head'] = env['head']['stdout'].strip()
        compared['git_version'] = env['git_version']['stdout'].strip()
        assert compared['git_version'] == read(OLD / 'attribute-probe.json')['git_version']['stdout'].strip()
        assert all(t['bytes'] == 200872 for t in current['trees'].values())
    else:
        start_sources = read(OUT / 'source-start.json')
        compared['task_changes'] = [{'path': p, 'before': start_sources.get(p), 'after': sources.get(p)}
                                    for p in changed(start_sources, sources)]
        assert sorted(changed(start_sources, sources)) == sorted(WRITES)
        assert sorted(compared['phase004_source_changes']) == sorted(WRITES)
        assert not current['git_differences']
        start = read(OUT / 'corpus-start.json')
        assert all(tree['manifest'] == start['trees'][runtime]['manifest'] for runtime, tree in current['trees'].items())
        save('environment-final.json', {'head': command(['git', 'rev-parse', 'HEAD']),
                                        'status': command(['git', '--no-optional-locks', '-c', 'core.quotepath=false', 'status', '--porcelain=v1', '--untracked-files=all'])})
    save('verification-' + stage + '.json', compared)
    print(json.dumps(compared, ensure_ascii=False))


def plan():
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
    expected = {'overlays': {r: builder.sha1(base[r].read_bytes()) for r in sorted(overlays) if r in base}}
    expected_bytes = (json.dumps(expected, ensure_ascii=False, indent=2, sort_keys=True) + '\n').replace('\n', os.linesep).encode('utf-8')
    ok, messages = builder.build_target('.agents', check=True, bless=False)
    result = {'changed': differences, 'outputs': len(outputs), 'check_ok': ok, 'messages': messages,
              'overlay_manifest_bytes_unchanged': (ROOT / '.agents/diff/_manifest.json').read_bytes() == expected_bytes,
              'changes_since_start': changed(read(OUT / 'source-start.json'), snapshot()),
              'status': command(['git', '--no-optional-locks', '-c', 'core.quotepath=false', 'status', '--porcelain=v1', '--untracked-files=all'])}
    save('build-plan.json', result)
    assert differences == ['.agents/skills/do-math/scripts/tests/corpus/.gitattributes']
    assert result['changes_since_start'] == ['.claude/skills/do-math/scripts/tests/corpus/.gitattributes']
    assert result['overlay_manifest_bytes_unchanged'] and result['status']['exit_code'] == 0
    assert all('드리프트' in m or '추가 문서' in m for m in messages), messages
    print(json.dumps({k: v for k, v in result.items() if k != 'status'}, ensure_ascii=False))


if __name__ == '__main__':
    if sys.argv[1] == 'plan':
        plan()
    else:
        observe(sys.argv[1])
