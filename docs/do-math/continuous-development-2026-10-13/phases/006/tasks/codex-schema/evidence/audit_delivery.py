"""Mirror preflight and task-local source/corpus/command verification."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
from run_command import ROOT, EVIDENCE, snapshot, changed, write_json

RUN = ROOT / 'docs/do-math/continuous-development-2026-10-13'
WRITES = json.loads((RUN / 'phases/006/phase.json').read_bytes())['tasks'][0]['writes']


def read(path):
    return json.loads(path.read_bytes())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def allowed(path):
    return any(path.startswith(w) if w.endswith('/') else path == w for w in WRITES)


def command(argv):
    from datetime import datetime, timezone
    begun = datetime.now(timezone.utc).isoformat()
    p = subprocess.Popen(argv, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    return {'argv': argv, 'cwd': str(ROOT), 'pid': p.pid, 'started_at': begun,
            'ended_at': datetime.now(timezone.utc).isoformat(), 'exit_code': p.returncode,
            'stdout': stdout.decode('utf-8'), 'stderr': stderr.decode('utf-8')}


def plan(label):
    spec = importlib.util.spec_from_file_location('mirror_builder', ROOT / '.claude/skills/writing-skills/scripts/build_skill_mirrors.py')
    builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)
    rules = builder.load_rules(ROOT / '.agents/diff')
    base = builder.iter_files(ROOT / builder.BASE_REL)
    overlays = {r:p for r,p in builder.iter_files(ROOT / '.agents/diff').items() if r not in builder.RESERVED}
    outputs = {r:builder.transform(r,p.read_bytes(),rules) for r,p in base.items()}
    outputs.update({r:p.read_bytes() for r,p in overlays.items()})
    existing = builder.iter_files(ROOT / '.agents/skills')
    differences = ['.agents/skills/' + r for r in sorted(outputs.keys() | existing.keys())
                   if r not in outputs or r not in existing or outputs[r] != existing[r].read_bytes()]
    expected = {'overlays': {r:builder.sha1(base[r].read_bytes()) for r in sorted(overlays) if r in base}}
    expected_bytes = (json.dumps(expected,ensure_ascii=False,indent=2,sort_keys=True)+'\n').replace('\n',os.linesep).encode('utf-8')
    ok, messages = builder.build_target('.agents',check=True,bless=False)
    sources = snapshot()
    result = {'changed': differences, 'outputs': len(outputs), 'check_ok': ok, 'messages': messages,
        'overlay_manifest_bytes_unchanged': (ROOT / '.agents/diff/_manifest.json').read_bytes() == expected_bytes,
        'changes_since_start': changed(read(EVIDENCE / 'source-start.json'), sources),
        'status': command(['git','--no-optional-locks','-c','core.quotepath=false','status','--porcelain=v1','--untracked-files=all'])}
    write_json(EVIDENCE / (label + '.json'),result)
    assert all(allowed(p) for p in differences + result['changes_since_start'])
    assert result['overlay_manifest_bytes_unchanged']
    assert all('드리프트' in m or '추가 문서' in m for m in messages)
    print(json.dumps({k:v for k,v in result.items() if k!='status'},ensure_ascii=False))


def corpus():
    trees, paths = {}, []
    initial = read(EVIDENCE / 'source-start.json')
    before = read(EVIDENCE / 'manifest-before.json')
    for runtime in ('.claude','.agents'):
        base = ROOT / runtime / 'skills/do-math/scripts/tests/corpus'
        files = {p.relative_to(base).as_posix():p for p in sorted(base.rglob('*')) if p.is_file()}
        manifest = read(base / 'manifest.json')
        rows = {r:{'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for r,p in files.items()}
        references, bindings = [], []
        for entry in manifest['entries']:
            for field in ('path','final_path','source_path','compiled_path','schema_path','transport_schema_path','worker_status_path'):
                if field in entry:
                    references.append({'entry':entry['id'],'field':field,'path':entry[field]})
            for field, hashfield in (('path','source_sha256'),('schema_path','schema_sha256'),('transport_schema_path','transport_schema_sha256')):
                if hashfield in entry:
                    bindings.append({'entry':entry['id'],'field':hashfield,'path':entry[field],'expected':entry[hashfield]})
            for recording in entry.get('recordings',[]):
                references.append({'entry':entry['id'],'field':'recordings','path':recording['path']})
                bindings.append({'entry':entry['id'],'field':'recordings.sha256','path':recording['path'],'expected':recording['sha256']})
        for binding in bindings:
            binding['actual'] = rows.get(binding['path'],{}).get('sha256')
            binding['matches'] = binding['actual'] == binding['expected']
        preserved = [r['path'] for rel,r in rows.items() if r['path'] in initial and rel != 'manifest.json']
        assert all(sha(ROOT / p) == initial[p] for p in preserved)
        assert manifest['entries'][:-1] == before['entries']
        tree = {'entry_count':len(manifest['entries']),'files':rows,'file_count':len(rows),
            'bytes':sum(r['bytes'] for r in rows.values()),'bindings':bindings,
            'old_files_unchanged':len(preserved),'old_entries_unchanged':len(before['entries']),
            'undeclared':sorted(set(rows) - {r['path'] for r in references} - {'manifest.json','.gitattributes'})}
        assert all(b['matches'] for b in bindings) and not tree['undeclared']
        assert tree['bytes'] <= 5*1024*1024
        trees[runtime] = tree
        paths.extend(r['path'] for r in rows.values())
    assert {r:v['sha256'] for r,v in trees['.claude']['files'].items()} == {r:v['sha256'] for r,v in trees['.agents']['files'].items()}
    cmds = [command(['git','hash-object','--no-filters',*paths]),command(['git','hash-object',*paths]),
            command(['git','check-attr','--all','--',*paths])]
    assert all(c['exit_code']==0 for c in cmds)
    raw, clean = [c['stdout'].splitlines() for c in cmds[:2]]
    assert len(paths)==len(set(paths))==len(raw)==len(clean)
    git_rows = [{'path':p,'raw':a,'clean':b,'matches':a==b} for p,a,b in zip(paths,raw,clean,strict=True)]
    write_json(EVIDENCE / 'corpus-final.json',{'trees':trees,'commands':cmds,'git_rows':git_rows})
    assert all(r['matches'] for r in git_rows)
    return {k:{'entries':v['entry_count'],'files':v['file_count'],'bytes':v['bytes'],'sha_bindings':len(v['bindings'])} for k,v in trees.items()}


def final():
    sources = snapshot()
    write_json(EVIDENCE / 'source-final.json', sources)
    changes = changed(read(EVIDENCE / 'source-start.json'),sources)
    assert all(allowed(p) for p in changes), changes
    checks = {}
    for label in ('red','semantic','related-01','related-02','consumers','semantic-final','live','corpus','mirror-corpus'):
        report = read(EVIDENCE / label / 'report.json')
        rows = [r for g in report['reports'] for r in g['rows']]
        ids = [r['id'] for r in rows]
        assert len(ids)==len(set(ids))==len(report['selected']) and set(ids)==set(report['selected'])
        assert report['complete'] and not report['changed_during_run']
        checks[label] = {'selected':len(ids),'counts':report['counts'],'successful':report['successful'],
            'complete':True,'changed_during_run':report['changed_during_run'],
            'failed_ids':[r['id'] for r in rows if r['outcome']!='passed']}
        base = ROOT / ('.agents' if label=='mirror-corpus' else '.claude') / 'skills/do-math/scripts'
        current_python = {p.relative_to(base).as_posix():sha(p) for p in base.rglob('*.py')}
        checks[label]['python_changes_since_run'] = changed(report['source_sha256'],current_python)
        if label in ('corpus','mirror-corpus'):
            assert not checks[label]['python_changes_since_run']
    live_sources = read(EVIDENCE / 'live-command/source-before.json')
    runtime = [p for p in sources if p.startswith('.claude/skills/do-math/scripts/do_math/') and p.endswith('.py')]
    assert all(sources[p]==live_sources[p] for p in runtime)
    assert sources['.claude/skills/do-math/scripts/tests/support/provider_live.py']==live_sources['.claude/skills/do-math/scripts/tests/support/provider_live.py']
    result = {'changes':changes,'source_count':len(sources),'checks':checks,'corpus':corpus(),
        'runtime_unchanged_since_live':runtime,'smoke_helper_unchanged_since_live':True,
        'status':command(['git','--no-optional-locks','-c','core.quotepath=false','status','--porcelain=v1','--untracked-files=all'])}
    write_json(EVIDENCE / 'verification-final.json',result)
    print(json.dumps({k:v for k,v in result.items() if k not in ('status','runtime_unchanged_since_live')},ensure_ascii=False))


if __name__=='__main__':
    if sys.argv[1]=='final': final()
    else: plan(sys.argv[1])
