from work import *
from collections import Counter
out={}
for label,tree in [('red','.claude'),('focus','.claude'),('corrected','.claude'),('c','.claude'),('c2','.claude'),('m','.agents')]:
    process=json.loads((E/(label+'-process.json')).read_text(encoding='utf-8'))
    report=json.loads((E/label/'report.json').read_text(encoding='utf-8-sig'))
    rows=[r for g in report['reports'] for r in g['rows'] if not r.get('fixture')]
    selected=report['selected']; counts=dict(Counter(r['outcome'] for r in rows))
    assert len(selected)==len(set(selected))==len(rows)==len({r['id'] for r in rows})
    assert set(selected)=={r['id'] for r in rows}
    assert not report['changed_during_run']
    summary={'selected':len(selected),'rows':len(rows),'counts':counts,'selected_ids':selected,
        'exit_code':process['exit_code'],'complete':report['complete'],'successful':report['successful'],
        'source_sha256_count':len(report['source_sha256']),'nonpassed':[r for r in rows if r['outcome']!='passed'],
        'fixture_rows':[r for g in report['reports'] for r in g['rows'] if r.get('fixture')],
        'total_seconds':report['total_seconds']}
    if label in ('c2','m'):
        assert report['complete'] and report['successful'] and process['exit_code']==0
        assert set(counts)<= {'passed','skipped'}
        scripts=REPO/tree/'skills/do-math/scripts'
        current={p.relative_to(scripts).as_posix():digest(p)['sha256'] for p in scripts.rglob('*.py') if '__pycache__' not in p.parts}
        assert current==report['source_sha256']
        before=json.loads((E/(label+'-before.json')).read_text(encoding='utf-8'))
        after=json.loads((E/(label+'-after.json')).read_text(encoding='utf-8'))
        fixed=[p for p in before if Path(p).name not in ('.timings.json','.timings-t3.json')]
        assert all(before[p]==after[p] for p in fixed)
        observed=json.loads((E/(label+'-observations.json')).read_text(encoding='utf-8'))
        assert observed['exit_code']==0
        for row in observed['final_proposals']:
            value=json.loads((E/row['file']).read_text(encoding='utf-8'))['context']
            proposal=value['role_review']['proposal']
            def count(node):
                if isinstance(node,dict):return int(node==proposal)+sum(count(v) for v in node.values())
                if isinstance(node,list):return sum(count(v) for v in node)
                return 0
            assert count(value)==1
        assert observed['final_proposals']
        summary.update(observed_returns=len(observed['actual_returns']),
            observed_kinds=dict(Counter(r['kind'] for r in observed['actual_returns'])),
            single_proposal_returns=len(observed['final_proposals']))
    out[label]=summary
assert out['c']['selected_ids']==out['c2']['selected_ids']==out['m']['selected_ids']
assert json.loads((E/'c/report.json').read_text())['source_sha256']==json.loads((E/'c2/report.json').read_text())['source_sha256']
assert set(r['id'] for r in out['c']['nonpassed'] if r['outcome']!='skipped') <= {
    r['id'] for g in json.loads((E/'c2/report.json').read_text())['reports'] for r in g['rows'] if r['outcome']=='passed'}
final=snapshot('final'); start=json.loads((E/'start.json').read_text(encoding='utf-8'))
allowed=json.loads((RUN/'phases/024/phase.json').read_text(encoding='utf-8-sig'))['tasks'][0]['writes']
changes=sorted(p for p in set(start)|set(final) if start.get(p)!=final.get(p))
assert set(changes)<=set(allowed)
preserved=json.loads((E/'preservation.json').read_text(encoding='utf-8'))
assert all(final[p]['sha256']==sha for p,sha in preserved['runtime_sha256'].items())
assert all(final[p]['sha256']==sha for p,sha in preserved['fixed_runtime_and_t4_sha256'].items())
assert all(start[r['path']]==final[r['path']] for r in preserved['corpus'])
original=json.loads((E/'prior-task-preservation.json').read_text())
assert all(digest(REPO/p)['sha256']==sha for p,sha in original['files'].items())
resources=[]
for label in ('c2','m'):
    for path in (E/label).rglob('*.json'):
        if '-isolated-' not in str(path):continue
        try:value=json.loads(path.read_bytes().decode('utf-8-sig'))
        except (ValueError,UnicodeError):continue
        def visit(node):
            if isinstance(node,dict):
                for k,v in node.items():
                    if k in ('cwd','workspace') and isinstance(v,str) and v.startswith(('C:', 'C/')):
                        resources.append({'suite':label,'source':path.relative_to(E).as_posix(),
                                          'field':k,'value':v,'characters':len(v)})
                    visit(v)
            elif isinstance(node,list):
                for item in node:visit(item)
        visit(value)
save('resource-cwd.json',resources)
save('verification.json',{'suites':out,'source_count':len(final),'changes':changes,'outside_writes':[],
    'runtime139':True,'fixed_boundary258':True,'corpus144':True,'prior_task891':True,
    'initial_observer':'run_suite_initial.py targeted the shared operation_trace decorator instead of the unwrapped prepare_role_input. Exact same product Python revision and selected IDs pass in c2 after inspect.unwrap correction. Original c and all fixture errors/failures/not_run rows are retained.'})
print({k:{n:v[n] for n in ('selected','counts','exit_code')} for k,v in out.items()})
print('Authorized changes',len(changes),'final source count',len(final),'resource cwd records',len(resources))
