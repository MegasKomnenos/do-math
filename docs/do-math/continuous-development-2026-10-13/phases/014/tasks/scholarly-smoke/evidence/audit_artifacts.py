import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

REPO = Path('C:/math')
RUN = REPO / 'docs/do-math/continuous-development-2026-10-13'
OUT = Path(__file__).parent

def save(name, value):
    (OUT / (name + '.json')).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def allowed(path, writes):
    return any(path == w or w.endswith('/') and path.startswith(w) for w in writes)

def mirror_plan(name):
    spec = importlib.util.spec_from_file_location('builder', REPO / '.claude/skills/writing-skills/scripts/build_skill_mirrors.py')
    builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)
    rules = builder.load_rules(REPO / '.agents/diff')
    outputs = {r: builder.transform(r, p.read_bytes(), rules) for r, p in builder.iter_files(REPO / '.claude/skills').items()}
    overlays = builder.iter_files(REPO / '.agents/diff')
    outputs.update({r:p.read_bytes() for r,p in overlays.items() if r not in builder.RESERVED})
    existing = builder.iter_files(REPO / '.agents/skills')
    changed = ['.agents/skills/' + r for r,b in outputs.items() if r not in existing or existing[r].read_bytes() != b]
    removed = ['.agents/skills/' + r for r in existing if r not in outputs]
    writes = json.loads((RUN / 'phases/014/phase.json').read_bytes())['tasks'][0]['writes']
    result = {'changed': changed, 'removed': removed, 'outside_writes': [p for p in changed + removed if not allowed(p,writes)],
              'output_count': len(outputs)}
    save(name,result)
    assert not result['outside_writes'] and not removed
    print(json.dumps(result, ensure_ascii=False))

def corpus_audit():
    trees = {}
    for prefix in ('.claude/skills/do-math/scripts/tests/corpus', '.agents/skills/do-math/scripts/tests/corpus'):
        root = REPO / prefix
        manifest = json.loads((root / 'manifest.json').read_bytes())
        rows = []
        for path in sorted(p for p in root.rglob('*') if p.is_file()):
            relative = path.relative_to(REPO).as_posix()
            commands = [['git','hash-object','--no-filters','--',relative], ['git','hash-object','--path=' + relative,relative]]
            results = [subprocess.run(a,cwd=REPO,capture_output=True,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0)) for a in commands]
            rows.append({'path': relative,'bytes':path.stat().st_size,'sha256':digest(path),'argv':commands,
                         'exit_codes':[r.returncode for r in results], 'raw_oid':results[0].stdout.decode().strip(),
                         'clean_oid':results[1].stdout.decode().strip(), 'stderr':[r.stderr.decode(errors='replace') for r in results]})
        refs = []
        for e in manifest['entries']:
            for r in e.get('recordings',[]):
                refs.append({'id':e['id'],'path':r['path'],'expected':r['sha256'],'actual':digest(root/r['path'])})
            for h,p in [('source_sha256','path'),('schema_sha256','schema_path'),('transport_schema_sha256','transport_schema_path')]:
                if h in e:
                    refs.append({'id':e['id'],'path':e[p],'expected':e[h],'actual':digest(root/e[p])})
        trees[prefix] = {'entries':len(manifest['entries']),'file_count':len(rows),'bytes':sum(r['bytes'] for r in rows),'rows':rows,'sha_refs':refs}
    ordered = list(trees.values())
    result = {'trees':trees,
              'raw_clean_equal':all(r['exit_codes']==[0,0] and r['raw_oid']==r['clean_oid'] for t in ordered for r in t['rows']),
              'sha_refs_match':all(r['expected']==r['actual'] for t in ordered for r in t['sha_refs']),
              'mirror_bytes_equal':[(r['path'].split('/corpus/')[1],r['sha256']) for r in ordered[0]['rows']] ==
                                   [(r['path'].split('/corpus/')[1],r['sha256']) for r in ordered[1]['rows']]}
    save('corpus-final',result)
    assert all(result[k] for k in ('raw_clean_equal','sha_refs_match','mirror_bytes_equal'))
    print(json.dumps({k:v for k,v in result.items() if k != 'trees'}))

if __name__ == '__main__':
    if sys.argv[1] == 'plan': mirror_plan(sys.argv[2])
    elif sys.argv[1] == 'corpus': corpus_audit()
