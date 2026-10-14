from work import *
from collections import Counter
out={}
for label,tree in [('red','.claude'),('red-doc','.claude'),('focus','.claude'),('corrected','.claude'),('c','.claude'),('m','.agents')]:
    process=json.loads((E/(label+'-process.json')).read_text(encoding='utf-8'))
    assert process['exit_code'] is not None
    report=json.loads((E/label/'report.json').read_text(encoding='utf-8-sig'))
    selected=report['selected']
    rows=[r for g in report['reports'] for r in g['rows'] if not r.get('fixture')]
    assert len(selected)==len(set(selected))==len(rows)==len({r['id'] for r in rows})
    assert set(selected)=={r['id'] for r in rows}
    summary={'selected':len(selected),'rows':len(rows),'counts':dict(Counter(r['outcome'] for r in rows)),
        'exit_code':process['exit_code'],'complete':report['complete'],'successful':report['successful'],
        'nonpassed':[r for r in rows if r['outcome']!='passed'],'source_sha256_count':len(report['source_sha256']),
        'changed_during_run':report['changed_during_run']}
    assert not report['changed_during_run']
    if label in ('red','red-doc'):
        assert process['exit_code']==1 and summary['counts']=={'failed':1}
    elif label in ('focus','corrected'):
        assert process['exit_code']==0 and set(summary['counts'])=={'passed'}
    else:
        assert report['complete'] and report['successful'] and process['exit_code']==0
        assert summary['counts'].get('skipped')==1 and set(summary['counts'])=={'passed','skipped'}
        assert summary['nonpassed'][0]['id']=='unit.test_context_catalog.ContextStoreTests.test_outside_symlink_is_reported_when_supported'
        scripts=REPO/tree/'skills/do-math/scripts'
        current={p.relative_to(scripts).as_posix():digest(p)['sha256'] for p in scripts.rglob('*.py') if '__pycache__' not in p.parts}
        assert current==report['source_sha256']
        before=json.loads((E/(label+'-before.json')).read_text(encoding='utf-8'))
        after=json.loads((E/(label+'-after.json')).read_text(encoding='utf-8'))
        immutable=[p for p in before if p.startswith(tree+'/skills/do-math/') and Path(p).name not in ('.timings.json','.timings-t3.json')]
        assert all(before[p]==after[p] for p in immutable)
        observation=json.loads((E/(label+'-proposal-observation.json')).read_text(encoding='utf-8'))
        assert observation['official_exit_code']==0 and observation['satisfied']
        summary.update(fixed_tree_files=len(immutable),selected_ids=selected,
                       final_proposal_returns=len(observation['returns']),single_proposal=True)
    out[label]=summary
assert out['c']['selected_ids']==out['m']['selected_ids']
final=snapshot('final')
start=json.loads((E/'start.json').read_text(encoding='utf-8'))
allowed=json.loads((RUN/'phases/022/phase.json').read_text(encoding='utf-8-sig'))['tasks'][0]['writes']
changes=[p for p in sorted(set(start)|set(final)) if start.get(p)!=final.get(p)]
assert set(changes)<=set(allowed),set(changes)-set(allowed)
prior=json.loads((RUN/'phases/021/manager-evidence/task-files.json').read_text(encoding='utf-8-sig'))
for path,sha in prior.items():
    assert digest(RUN/'phases/021/tasks/document-review'/path)['sha256']==sha, path
save('verification.json',{'suites':out,'changes':changes,'outside_writes':[],
    'source_count':len(final),'previous_task_files_unchanged':len(prior),
    'product_documents_unchanged':all(start[p]==final[p] for p in start if '/do-math/' in p and Path(p).suffix=='.md')})
print({k:{key:v[key] for key in ('selected','counts','exit_code','source_sha256_count')} for k,v in out.items()})
print('Changes',len(changes),'previous task files unchanged',len(prior))
