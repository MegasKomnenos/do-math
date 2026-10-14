import collections
import hashlib
import importlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

from task_driver import BASE, E, REPO, RUN, read, sha, write

def scripts(tree):
    return REPO / ('.claude' if tree == 'canonical' else '.agents') / 'skills/do-math/scripts'

def load_mirror_generator():
    path = REPO / '.claude/skills/writing-skills/scripts/build_skill_mirrors.py'
    spec = importlib.util.spec_from_file_location('official_mirror_generator', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def mirror_plan():
    module = load_mirror_generator()
    diff = REPO / '.agents/diff'
    rules = module.load_rules(diff)
    base = module.iter_files(REPO / module.BASE_REL)
    overlays = {p: f for p, f in module.iter_files(diff).items() if p not in module.RESERVED}
    outputs = {p: module.transform(p, f.read_bytes(), rules) for p, f in base.items()}
    outputs.update({p: f.read_bytes() for p, f in overlays.items()})
    existing = module.iter_files(REPO / '.agents/skills')
    changes = ['.agents/skills/' + p for p in outputs if p not in existing or outputs[p] != existing[p].read_bytes()]
    changes += ['.agents/skills/' + p for p in existing if p not in outputs]
    old_manifest = read(diff / '_manifest.json')
    new_manifest = {'overlays': {p: module.sha1(base[p].read_bytes()) for p in sorted(overlays) if p in base}}
    raw_manifest = (json.dumps(new_manifest, ensure_ascii=False, indent=2, sort_keys=True) + '\n').replace('\n', os.linesep).encode('utf-8')
    if raw_manifest != (diff / '_manifest.json').read_bytes(): changes.append('.agents/diff/_manifest.json')
    allowed = read(RUN / 'phases/017/phase.json')['tasks'][0]['writes']
    outside = [p for p in changes if p not in allowed]
    result = {'outputs': len(outputs), 'changes': changes, 'outside_writes': outside,
              'manifest_value_equal': old_manifest == new_manifest, 'manifest_bytes_equal': raw_manifest == (diff / '_manifest.json').read_bytes()}
    write(E / 'mirror-plan.json', result)
    print(result)
    assert not outside

def raw_verify():
    sys.path[:0] = [str(scripts('canonical')), str(scripts('canonical') / 'tests')]
    m = importlib.import_module('boundary.test_shared_input_provenance')
    import coverage
    results = []
    for fixture in read(E / 'companion-manifest.json'):
        root = Path(fixture['preserved_root'])
        original = Path(fixture['original_root'])
        for row in fixture['files']:
            assert sha(root / row['path']) == row['sha256']
        observed = {}
        db_results = []
        for snapshot in sorted(root.glob('*/snapshot.json')):
            capture = read(snapshot)
            observed[snapshot.parent.name] = capture
            if 'coverage' in capture:
                data = coverage.CoverageData(basename=str(snapshot.parent / 'coverage.data'))
                data.read()
                files = sorted(data.measured_files())
                contexts = {}
                for context in sorted(data.measured_contexts()):
                    data.set_query_context(context)
                    rows = {}
                    for path in files:
                        lines = sorted(data.lines(path) or [])
                        arcs = [list(arc) for arc in sorted(data.arcs(path) or [])]
                        if lines or arcs: rows[Path(path).relative_to(original).as_posix()] = {'lines':lines,'arcs':arcs}
                    contexts[context] = rows
                actual = {'files': sorted(Path(p).relative_to(original).as_posix() for p in files), 'contexts': contexts}
                assert actual == capture['coverage'], snapshot
                if (snapshot.parent / 'entered.json').exists(): assert read(snapshot.parent / 'entered.json') == capture['entered']
                if (snapshot.parent / 'opened.json').exists():
                    opened = read(snapshot.parent / 'opened.json')
                    assert opened['opens'] == capture['opens'] and opened['import_opens'] == capture['import_opens']
                db_results.append({'capture': snapshot.parent.name, 'coverage_sha256': sha(snapshot.parent / 'coverage.data'),
                                   'contexts': len(contexts), 'files': len(files), 'db_snapshot_equal': True})
        prefixes = sorted(name[:-4] for name in observed if name.endswith('-old'))
        pairs = []
        for prefix in prefixes:
            old, new = observed[prefix+'-old'], observed[prefix+'-new']
            oo, no = observed[prefix+'-old-ordinary'], observed[prefix+'-new-ordinary']
            assert oo['ordinary'] == no['ordinary'] == old['ordinary'] == new['ordinary']
            old_literal, old_markers = m.split_entries(old['entered'])
            new_literal, new_markers = m.split_entries(new['entered'])
            assert old_literal == new_literal
            for field in ('opens','import_opens','coverage'): assert old[field] == new[field]
            pairs.append({'prefix': prefix, 'ordinary': old['ordinary'], 'literal_labels': sorted(old_literal),
                          'empty_literal_labels': sorted(k for k,v in old_literal.items() if not v),
                          'literal_pair_count': sum(map(len,old_literal.values())),
                          'old_markers': old_markers, 'new_markers': new_markers, 'literal_open_coverage_equal': True})
        merges = []
        if 'old-merge' in observed:
            for edition in ('old','new'):
                merged = observed[edition+'-merge']
                workers = [observed[letter+'-'+edition] for letter in 'ab']
                assert merged['entered'] == m.union_records([w['entered'] for w in workers])
                for field in ('opens','import_opens'): assert merged[field] == m.union_records([w[field] for w in workers])
                assert merged['coverage'] == m.union_coverage([w['coverage'] for w in workers])
                merges.append({'edition': edition, 'actual_merge_matches_raw_union': True})
            assert m.split_entries(observed['old-merge']['entered'])[0] == m.split_entries(observed['new-merge']['entered'])[0]
            for field in ('opens','import_opens','coverage'): assert observed['old-merge'][field] == observed['new-merge'][field]
        results.append({'test': fixture['test'], 'original_root': str(original), 'preserved_root': str(root),
                        'nested': 'NESTED = True' in (root/'scripts/producer.py').read_text(encoding='utf-8'),
                        'snapshots': len(observed), 'pairs': pairs, 'databases': db_results, 'merges': merges})
    invocations = read(E / 'companion-invocations.json')
    children = [r for r in invocations if Path(r['argv'][0]).resolve() == Path(sys.executable).resolve() and '-c' in r['argv']]
    assert len(children) == 30
    assert all(r['exit_code'] == 0 and r['baseline_environment'] == str(BASE) for r in children)
    g = load_mirror_generator()
    rules = g.load_rules(REPO / '.agents/diff')
    rel = 'do-math/scripts/tests/boundary/test_shared_input_provenance.py'
    canonical = scripts('canonical') / 'tests/boundary/test_shared_input_provenance.py'
    mirror = scripts('mirror') / 'tests/boundary/test_shared_input_provenance.py'
    assert g.transform(rel, canonical.read_bytes(), rules) == mirror.read_bytes()
    assert canonical.read_bytes() == mirror.read_bytes()
    result = {'successful': read(E/'companion-result.json')['successful'], 'fixtures': results,
              'child_invocations': len(children), 'all_child_exit_zero_and_baseline_environment': True,
              'official_transform_matches_mirror': True, 'test_file_byte_equal': True,
              'raw_reuse_limit': 'Canonical companion only; mirror official suites execute separately. No retained mirror fixture raw is claimed.'}
    write(E / 'raw-verification.json', result)
    print('raw fixtures',len(results),'snapshots',sum(r['snapshots'] for r in results),'DBs',sum(len(r['databases']) for r in results),'child',len(children))

def suite_verify(tree, kind, label=None):
    label = label or tree + ('-t4-full' if kind == 'full' else '-exact')
    receipt = read(E / (label + '.command.json'))
    directory = Path(receipt['output'])
    report = read(directory / 'report.json')
    rows = [r for group in report['reports'] for r in group['rows'] if not r.get('fixture')]
    ids = [r['id'] for r in rows]
    assert len(ids) == len(set(ids)) and set(ids) == set(report['selected'])
    current = {p.relative_to(scripts(tree)).as_posix(): sha(p) for p in scripts(tree).rglob('*.py') if '__pycache__' not in p.parts}
    assert current == report['source_sha256']
    assert not report['changed_during_run']
    out = {'label':label, 'selected':len(report['selected']), 'unique_rows':len(set(ids)),
           'counts':dict(collections.Counter(r['outcome'] for r in rows)), 'exit_code':receipt['exit_code'],
           'seconds':receipt['seconds'],'complete':report['complete'],'successful':report['successful'],
           'fixture_counts': report['fixture_counts'], 'python_files':len(current),
           'nonpassed':[r for r in rows if r['outcome'] != 'passed'], 'source_changes':receipt['source_changes']}
    if kind == 'full':
        listed = [line.split('\t')[1] for line in (E/(tree+'-t4-list.stdout')).read_text(encoding='utf-8').splitlines() if '\t' in line]
        assert set(listed) == set(report['selected']) and len(listed) == len(set(listed))
        adapter = read(directory / 'adapter-coverage.json')
        assert adapter == report['t4_adapter']
        sys.path[:0] = [str(scripts(tree)), str(scripts(tree)/'tests')]
        from support.adapter_coverage import validate_publication
        import coverage
        workers = []
        for worker in adapter['workers']:
            wd = Path(worker['directory'])
            request = read(wd/'measure.json')
            assert request['requested'] == read(wd/'requested.json') == worker['requested']
            assert request['source_sha256'] == current and request['run_id'] == adapter['run_id']
            data = validate_publication(wd,request)
            assert worker['status'] == 'merged'
            wr = read(wd/'worker-report.json')
            assert wr['requested'] == request['requested'] and wr['returncode'] == worker['returncode']
            workers.append({'directory':str(wd),'requested':request['requested'],'returncode':worker['returncode'],
                            'run_id':request['run_id'],'branch_db':data.has_arcs(), 'publication_sha256':sha(wd/'adapter-measurement.json')})
        # Saved adapter.data is the actual parent's data after accepted worker union.
        parent = coverage.CoverageData(basename=str(directory/'adapter.data'))
        parent.read()
        for worker in adapter['workers']:
            data = coverage.CoverageData(basename=str(Path(worker['directory'])/'coverage.data'))
            data.read()
            for file in data.measured_files():
                assert set(data.arcs(file) or []) <= set(parent.arcs(file) or [])
                assert data.measured_contexts() <= parent.measured_contexts()
        from do_math.layers import LAYERS
        expected = sorted(p for p,l in LAYERS.items() if l == 'adapter')
        assert sorted(adapter['modules']) == expected
        from support.branch_gate import REASONED_EXCLUSION
        c = coverage.Coverage(data_file=str(directory/'adapter.data'),branch=True,config_file=False)
        c.set_option('report:exclude_lines',[REASONED_EXCLUSION])
        c.set_option('report:partial_branches',[])
        c.load()
        target = E/(label+'-raw-analysis.json')
        c.json_report(morfs=[str(scripts(tree)/p) for p in expected],outfile=str(target))
        analysis = read(target)
        mapped = {(Path.cwd()/p).resolve():v for p,v in analysis['files'].items()}
        assert analysis['totals'] == adapter['totals']
        for path in expected:
            entry = adapter['modules'][path]
            assert entry['source_sha256'] == current[path]
            for k,v in mapped[(scripts(tree)/path).resolve()].items(): assert entry[k] == v
        previous = read(RUN/'phases/015/tasks/t4-adapter-report/evidence'/('canonical-t4-final' if tree=='canonical' else 'mirror-t4-full')/'report.json')
        prev_rows = [r for group in previous['reports'] for r in group['rows'] if not r.get('fixture') and r['outcome']!='passed']
        current_rows = {r['id']:r for r in rows}
        out.update(adapter={'complete':adapter['complete'],'tests_complete':adapter['tests_complete'],
                   'workers':workers,'modules':expected,'totals':adapter['totals'],'raw_analysis_equal':True,
                   'worker_arcs_subset_of_saved_union':True,'problems':adapter['problems']},
                   previous_nonpassed_to_current=[{'id':r['id'],'old':r['outcome'],'new':current_rows[r['id']]['outcome']} for r in prev_rows])
    write(E/(label+'-verification.json'),out)
    print(label, out['counts'],'exit',out['exit_code'])

def preservation():
    start = read(E/'source-start.json')
    final = read(E/'source-final.json')
    changes = [p for p in start if start[p] != final[p]]
    allowed = read(RUN/'phases/017/phase.json')['tasks'][0]['writes']
    assert all(p in allowed for p in changes)
    previous = read(RUN/'phases/016/manager-evidence/verification.json')
    reused = previous['reused_inputs']
    assert len(reused)==139 and all(start[p] == final[p] for p in reused)
    tools = {p:sha(p) for p in previous['tool_sha256_preserved']}
    assert tools == previous['tool_sha256_preserved']
    host = previous['host_recordings_preserved']
    assert len(host)==8
    for r in host: assert sha(RUN/r['path']) == r['sha256']
    product_paths = []
    for phase, task in [('015','t4-adapter-report'),('016','t4-fixture-repair')]:
        rr = read(RUN/f'phases/{phase}/tasks/{task}/report.json')
        for row in rr['changes']:
            if Path(row['path']).name not in ('.timings.json','.timings-t3.json'):
                product_paths.append(row['path'])
                assert start[row['path']] == final[row['path']]
    assert len(set(product_paths))==22
    corpus=[]
    explicit=[]
    for tree in ('canonical','mirror'):
        root = scripts(tree)/'tests/corpus'
        for p in sorted(root.rglob('*')):
            if p.is_file():
                relative=p.relative_to(REPO).as_posix()
                raw = p.read_bytes()
                blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
                proc=subprocess.run(['git','hash-object','--path='+relative,'--stdin'],input=raw,cwd=REPO,capture_output=True)
                assert proc.returncode == 0 and proc.stdout.decode().strip()==blob
                assert start[relative] == final[relative]
                corpus.append({'path':relative,'sha256':sha(p),'raw_git_blob':blob,'clean_git_blob':proc.stdout.decode().strip(),
                               'argv':['git','hash-object','--path='+relative,'--stdin'],'exit_code':proc.returncode})
        for entry in read(root/'manifest.json')['entries']:
            refs=[]
            for digest_key,path_key in [('source_sha256','path'),('schema_sha256','schema_path'),('transport_schema_sha256','transport_schema_path')]:
                if digest_key in entry: refs.append((digest_key,entry[path_key],entry[digest_key]))
            refs += [('recordings/'+str(i),row['path'],row['sha256']) for i,row in enumerate(entry.get('recordings',[]))]
            for selector,path,digest in refs:
                assert sha(root/path)==digest
                explicit.append({'tree':tree,'entry':entry['id'],'selector':selector,'path':path,'sha256':digest})
    assert len(corpus)==144
    assert len(explicit)==150
    write(E/'corpus-raw-clean.json',{'files':corpus,'explicit_sha_records':explicit})
    write(E/'preservation.json',{'source_count':len(final),'changes':changes,'outside_writes':[],
          'runtime_and_live_inputs':reused,'host_recordings':host,'tools':tools,'product22_paths':sorted(set(product_paths)),
          'corpus_paths':len(corpus),'explicit_sha_records':len(explicit),
          'reuse_scope':'Prior approved properties only, same source and tool bytes; no new paid provider/scheduler/scholarly calls.'})
    print('preservation',len(final),'changes',changes,'corpus',len(corpus),'explicit_sha',len(explicit))

def baseline_git():
    manifest=read(RUN/'phases/016/tasks/provenance-baseline/evidence/baseline-manifest.json')
    tree_argv=['git','ls-tree','-r','-z',manifest['baseline_commit'],'--','.claude/skills/do-math/scripts/']
    tree=subprocess.run(tree_argv,cwd=REPO,capture_output=True)
    (E/'baseline-git-tree.bin').write_bytes(tree.stdout)
    assert tree.returncode==0
    entries={}
    for row in tree.stdout.split(b'\0'):
        if not row: continue
        meta,path=row.split(b'\t',1)
        mode,kind,blob=meta.decode().split()
        entries[path.decode()]={'mode':mode,'kind':kind,'blob':blob}
    assert set(entries)=={r['repository_path'] for r in manifest['files']}
    blobs=sorted({r['git_blob'] for r in manifest['files']})
    batch_input=''.join(b+'\n' for b in blobs).encode()
    (E/'baseline-git-objects.stdin').write_bytes(batch_input)
    batch=subprocess.run(['git','cat-file','--batch'],input=batch_input,cwd=REPO,capture_output=True)
    (E/'baseline-git-objects.bin').write_bytes(batch.stdout)
    assert batch.returncode==0
    data={}
    position=0
    for expected in blobs:
        end=batch.stdout.index(b'\n',position)
        oid,kind,size=batch.stdout[position:end].decode().split()
        assert oid==expected and kind=='blob'
        size=int(size)
        position=end+1
        data[oid]=batch.stdout[position:position+size]
        position+=size+1
    assert position==len(batch.stdout)
    for row in manifest['files']:
        assert entries[row['repository_path']]=={'mode':row['mode'],'kind':'blob','blob':row['git_blob']}
        assert (BASE/row['path']).read_bytes()==data[row['git_blob']]
    phase=read(RUN/'phases/017/phase.json')['tasks'][0]
    audit=[]
    for ref in phase['inputs']:
        root,path=ref.split(':',1)
        source=(RUN if root=='run' else REPO)/path
        raw=source.read_bytes()
        # Decode all assigned original text; JSON is parsed without editing it.
        value=json.loads(raw.decode('utf-8-sig')) if source.suffix=='.json' else raw.decode('utf-8-sig')
        audit.append({'reference':ref,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),
                      'type':type(value).__name__})
    write(E/'input-audit.json',audit)
    write(E/'baseline-git-verification.json',{'file_count':len(entries),'unique_blobs':len(blobs),'fresh_git_bytes_equal':True,
          'baseline_commit':manifest['baseline_commit'],'introduction_commit':manifest['introduction_commit'],
          'commands':[{'argv':tree_argv,'cwd':str(REPO),'exit_code':tree.returncode,'stderr':tree.stderr.decode()},
                      {'argv':['git','cat-file','--batch'],'cwd':str(REPO),'exit_code':batch.returncode,'stderr':batch.stderr.decode()}]})
    print('fresh Git baseline',len(entries),len(blobs),'assigned inputs',len(audit))

if __name__ == '__main__':
    mode=sys.argv[1]
    if mode=='raw': raw_verify()
    elif mode=='suite': suite_verify(sys.argv[2],sys.argv[3],sys.argv[4] if len(sys.argv)>4 else None)
    elif mode=='preservation': preservation()
    elif mode=='mirror-plan': mirror_plan()
    elif mode=='baseline-git': baseline_git()
