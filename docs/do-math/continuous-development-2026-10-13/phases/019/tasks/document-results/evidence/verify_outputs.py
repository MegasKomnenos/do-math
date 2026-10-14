from work import *
from collections import Counter

def read(path): return json.loads(path.read_text(encoding='utf-8-sig'))
out={}
for label,tree in [('red','.claude'),('focus','.claude'),('corrected','.claude'),('c','.claude'),('m','.agents')]:
    process=read(E/(label+'-process.json'))
    if process['exit_code'] is None:continue
    path=E/label/'report.json'
    if not path.exists():continue
    report=read(path)
    selected=report['selected']
    rows=[row for group in report['reports'] for row in group['rows'] if not row.get('fixture')]
    assert len(selected)==len(set(selected))==len(rows)==len({r['id'] for r in rows})
    assert set(selected)=={r['id'] for r in rows}
    summary={'selected':len(selected),'rows':len(rows),'counts':dict(Counter(r['outcome'] for r in rows)),
             'exit_code':process['exit_code'],'complete':report['complete'],'successful':report['successful'],
             'nonpassed':[r for r in rows if r['outcome']!='passed'],
             'changed_during_run':report['changed_during_run'],'source_sha256_count':len(report['source_sha256'])}
    assert not report['changed_during_run']
    if label in ('c','m'):
        assert summary['counts']=={'passed':186,'skipped':1}
        assert report['complete'] and report['successful'] and process['exit_code']==0
        skipped=summary['nonpassed'][0]
        assert skipped['id']=='unit.test_context_catalog.ContextStoreTests.test_outside_symlink_is_reported_when_supported'
        scripts=REPO/tree/'skills/do-math/scripts'
        current={p.relative_to(scripts).as_posix():digest(p)['sha256'] for p in scripts.rglob('*.py') if '__pycache__' not in p.parts}
        assert current==report['source_sha256']
        before=read(E/(label+'-before.json'));after=read(E/(label+'-after.json'))
        immutable=[p for p in before if p.startswith(tree+'/skills/do-math/') and Path(p).name not in ('.timings.json','.timings-t3.json')]
        assert all(before[p]==after[p] for p in immutable)
        summary['fixed_tree_files']=len(immutable)
        summary['selected_ids']=selected
    out[label]=summary
if 'm' in out:assert out['c']['selected_ids']==out['m']['selected_ids']
final=snapshot('final')
start=read(E/'start.json')
allowed=read(RUN/'phases/019/phase.json')['tasks'][0]['writes']
changes=[p for p in sorted(set(start)|set(final)) if start.get(p)!=final.get(p)]
assert set(changes)<=set(allowed),set(changes)-set(allowed)
save('verification.json',{'suites':out,'changes':changes,'outside_writes':[],'source_count':len(final)})
print({name:{k:row[k] for k in ('selected','counts','exit_code','source_sha256_count')} for name,row in out.items()})
print('changes',len(changes),'source count',len(final))
