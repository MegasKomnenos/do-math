from work import *
from collections import Counter
out={}
for label,tree in [('red','.claude'),('focus','.claude'),('corrected','.claude'),('augmented','.claude'),('c','.claude'),('m','.agents')]:
    receipt=E/(label+'-process.json')
    if not receipt.exists():continue
    process=json.loads(receipt.read_text())
    if process['exit_code'] is None:continue
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
    if label in ('c','m'):
        assert report['complete'] and report['successful'] and process['exit_code']==0
        assert summary['counts'].get('skipped')==1 and set(summary['counts'])=={'passed','skipped'}
        assert summary['nonpassed'][0]['id']=='unit.test_context_catalog.ContextStoreTests.test_outside_symlink_is_reported_when_supported'
        scripts=REPO/tree/'skills/do-math/scripts'
        current={p.relative_to(scripts).as_posix():digest(p)['sha256'] for p in scripts.rglob('*.py') if '__pycache__' not in p.parts}
        assert current==report['source_sha256']
        before=json.loads((E/(label+'-before.json')).read_text());after=json.loads((E/(label+'-after.json')).read_text())
        immutable=[p for p in before if p.startswith(tree+'/skills/do-math/') and Path(p).name not in ('.timings.json','.timings-t3.json')]
        assert all(before[p]==after[p] for p in immutable)
        summary.update(fixed_tree_files=len(immutable),selected_ids=selected)
    out[label]=summary
if 'm' in out:assert out['c']['selected_ids']==out['m']['selected_ids']
final=snapshot('final')
start=json.loads((E/'start.json').read_text())
allowed=json.loads((RUN/'phases/020/phase.json').read_text(encoding='utf-8-sig'))['tasks'][0]['writes']
changes=[p for p in sorted(set(start)|set(final)) if start.get(p)!=final.get(p)]
assert set(changes)<=set(allowed),set(changes)-set(allowed)
save('verification.json',{'suites':out,'changes':changes,'outside_writes':[],'source_count':len(final)})
print({k:{key:v[key] for key in ('selected','counts','exit_code','source_sha256_count')} for k,v in out.items()})
print('changes',len(changes))
