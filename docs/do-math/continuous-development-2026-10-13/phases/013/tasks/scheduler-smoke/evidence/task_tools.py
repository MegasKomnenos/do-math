import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from datetime import datetime, timezone

REPO = Path('C:/math')
RUN = REPO / 'docs/do-math/continuous-development-2026-10-13'
E = RUN / 'phases/013/tasks/scheduler-smoke/evidence'
PYTHON = sys.executable

def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def snapshot(name):
    previous = json.loads((RUN / 'phases/012/manager-evidence/source-inspected.json').read_bytes())
    paths = set(previous)
    for prefix in ('.claude/skills', '.agents/skills', '.agents/diff', 'services/continuous-development'):
        for path in (REPO / prefix).rglob('*'):
            if path.is_file() and '__pycache__' not in path.parts and path.suffix != '.pyc':
                paths.add(path.relative_to(REPO).as_posix())
    result = {p: digest(REPO / p) for p in sorted(paths) if (REPO / p).is_file()}
    save(E / (name + '.json'), result)
    if name == 'source-start':
        differences = {p: [previous.get(p), result.get(p)] for p in previous if previous.get(p) != result.get(p)}
        save(E / 'start-comparison.json', {'previous_count':len(previous), 'current_count':len(result), 'differences':differences})
    print(name, len(result))

def command(name, argv):
    record = {'argv':argv, 'cwd':str(REPO), 'started_at':datetime.now(timezone.utc).isoformat()}
    with (E / (name + '.stdout')).open('wb') as out, (E / (name + '.stderr')).open('wb') as err:
        process = subprocess.Popen(argv, cwd=REPO, stdout=out, stderr=err,
                                   creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        record['pid'] = process.pid
        save(E / (name + '.started.json'), record)
        record['exit_code'] = process.wait()
    record['finished_at'] = datetime.now(timezone.utc).isoformat()
    save(E / (name + '.command.json'), record)
    print(name, 'exit', record['exit_code'])
    print((E / (name + '.stdout')).read_text(encoding='utf-8', errors='replace')[-2200:])
    print((E / (name + '.stderr')).read_text(encoding='utf-8', errors='replace')[-1800:])
    return record['exit_code']

def summary(folder):
    sys.path.insert(0, str(REPO / '.claude/skills/do-math/scripts'))
    from do_math.file_io import read_bytes_shared
    value = json.loads(read_bytes_shared(E / folder / 'report.json'))
    print('report keys', list(value))
    print(json.dumps({k:v for k,v in value.items() if k not in ('reports','source_before','source_after','selected','selection','code_version')}, ensure_ascii=False)[:2500])
    for report in value.get('reports', []):
        print('inner keys', list(report))
        print(json.dumps(report, ensure_ascii=False)[:1800])
    for path in (E / folder).rglob('smoke.json'):
        smoke = json.loads(path.read_bytes())
        print(str(path), smoke.get('checks'), smoke.get('error'))
        print('identity', smoke.get('identity'))

def corpus_audit(name):
    trees = {}
    for prefix in ('.claude/skills/do-math/scripts/tests/corpus', '.agents/skills/do-math/scripts/tests/corpus'):
        root = REPO / prefix
        manifest = json.loads((root / 'manifest.json').read_bytes())
        paths = sorted(p for p in root.rglob('*') if p.is_file())
        rows = []
        for path in paths:
            relative = path.relative_to(REPO).as_posix()
            commands = [['git','hash-object','--no-filters','--',relative],
                        ['git','hash-object','--path=' + relative,relative]]
            completed = [subprocess.run(argv, cwd=REPO, capture_output=True, creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0)) for argv in commands]
            rows.append({'path':relative, 'bytes':path.stat().st_size,'sha256':digest(path),
                'argv':commands,'exit_codes':[r.returncode for r in completed],
                'raw_oid':completed[0].stdout.decode().strip(), 'clean_oid':completed[1].stdout.decode().strip(),
                'stderr':[r.stderr.decode(errors='replace') for r in completed]})
        sha_refs = []
        for entry in manifest['entries']:
            for recording in entry.get('recordings', []):
                sha_refs.append({'id':entry['id'], 'path':recording['path'], 'expected':recording['sha256'], 'actual':digest(root / recording['path'])})
            for hash_key, path_key in [('source_sha256','path'),('schema_sha256','schema_path'),('transport_schema_sha256','transport_schema_path')]:
                if hash_key in entry:
                    sha_refs.append({'id':entry['id'],'path':entry[path_key], 'expected':entry[hash_key], 'actual':digest(root / entry[path_key])})
        trees[prefix] = {'entries':len(manifest['entries']), 'file_count':len(paths), 'bytes':sum(row['bytes'] for row in rows),
            'rows':rows, 'sha_refs':sha_refs}
    ordered = list(trees.values())
    result = {'trees':trees,
        'raw_clean_equal':all(row['exit_codes'] == [0,0] and row['raw_oid'] == row['clean_oid'] for tree in ordered for row in tree['rows']),
        'sha_refs_match':all(row['expected'] == row['actual'] for tree in ordered for row in tree['sha_refs']),
        'mirrored_bytes_equal':{r['path'].split('/corpus/')[1]:r['sha256'] for r in ordered[0]['rows']} == {r['path'].split('/corpus/')[1]:r['sha256'] for r in ordered[1]['rows']}}
    save(E / (name + '.json'), result)
    print(name, [(v['entries'],v['file_count'],v['bytes'],len(v['sha_refs'])) for v in ordered], {k:v for k,v in result.items() if k != 'trees'})
    assert all(result[k] for k in ('raw_clean_equal','sha_refs_match','mirrored_bytes_equal'))

def mirror_plan(name):
    spec = importlib.util.spec_from_file_location('build_skill_mirrors',REPO / '.claude/skills/writing-skills/scripts/build_skill_mirrors.py')
    builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)
    rules = json.loads((REPO / '.agents/diff/_rules.json').read_bytes())
    outputs = {relative:builder.transform(relative,path.read_bytes(),rules) for relative,path in builder.iter_files(REPO / '.claude/skills').items()}
    overlays = builder.iter_files(REPO / '.agents/diff')
    outputs.update({relative:path.read_bytes() for relative,path in overlays.items() if relative not in builder.RESERVED})
    existing = builder.iter_files(REPO / '.agents/skills')
    changed = ['.agents/skills/' + relative for relative,raw in outputs.items() if relative not in existing or existing[relative].read_bytes() != raw]
    removed = ['.agents/skills/' + relative for relative in existing if relative not in outputs]
    writes = json.loads((RUN / 'phases/013/phase.json').read_bytes())['tasks'][0]['writes']
    outside = [path for path in changed + removed if not any(path == w or w.endswith('/') and path.startswith(w) for w in writes)]
    save(E / (name + '.json'), {'changed':changed,'removed':removed,'outside_writes':outside,'output_count':len(outputs)})
    print(name, json.dumps({'changed':changed,'removed':removed,'outside':outside},ensure_ascii=False))
    assert not outside


if __name__ == '__main__':
    action = sys.argv[1]
    if action == 'snapshot': snapshot(sys.argv[2])
    elif action == 'command': sys.exit(command(sys.argv[2], sys.argv[3:]))
    elif action == 'corpus': corpus_audit(sys.argv[2])
    elif action == 'plan': mirror_plan(sys.argv[2])
    elif action == 'summary': summary(sys.argv[2])
