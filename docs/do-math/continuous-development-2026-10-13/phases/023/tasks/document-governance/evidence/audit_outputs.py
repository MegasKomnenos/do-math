from work import *
from collections import Counter
import ast
out={}
observer_errors={
 'unit.test_role_input_packaging.RoleInputTests.test_role_overflow_keeps_original_sizes_and_waits_on_activity',
 'unit.test_role_input_packaging.RoleInputTests.test_role_overflow_records_the_context_budget_it_compared',
 'unit.test_role_input_scoped_packaging.RoleInputClassTests.test_scope_follows_the_role_the_input_is_prepared_for'}
for label,tree in [('red','.claude'),('focus','.claude'),('corrected','.claude'),('c','.claude'),('c2','.claude'),('m','.agents')]:
    process=json.loads((E/(label+'-process.json')).read_text(encoding='utf-8'))
    report=json.loads((E/label/'report.json').read_text(encoding='utf-8-sig'))
    selected=report['selected']
    rows=[r for g in report['reports'] for r in g['rows'] if not r.get('fixture')]
    assert len(selected)==len(set(selected))==len(rows)==len({r['id'] for r in rows})
    assert set(selected)=={r['id'] for r in rows}
    summary={'selected':len(selected),'rows':len(rows),'counts':dict(Counter(r['outcome'] for r in rows)),
        'exit_code':process['exit_code'],'complete':report['complete'],'successful':report['successful'],
        'nonpassed':[r for r in rows if r['outcome']!='passed'],
        'source_sha256_count':len(report['source_sha256']),'changed_during_run':report['changed_during_run'],
        'selected_ids':selected,'total_seconds':report['total_seconds']}
    assert process['exit_code'] is not None and not report['changed_during_run']
    if label=='red':
        assert process['exit_code']==1 and summary['counts']=={'failed':1}
        assert (E/'red.stderr').read_text(encoding='utf-8').count('AssertionError: ValueError not raised')==4
    elif label=='focus':
        assert process['exit_code']==1 and summary['counts'].get('failed')==3
    elif label=='corrected':
        assert process['exit_code']==0 and set(summary['counts'])=={'passed'}
    elif label=='c':
        assert process['exit_code']==1 and summary['counts']=={'passed':456,'skipped':1,'error':3}
        assert {r['id'] for r in rows if r['outcome']=='error'}==observer_errors
        assert all('run_suite.py' in '\n'.join(r['details']) and "KeyError: 'role'" in '\n'.join(r['details'])
                   for r in rows if r['outcome']=='error')
    else:
        assert report['complete'] and report['successful'] and process['exit_code']==0
        assert summary['counts'].get('skipped')==1 and set(summary['counts'])=={'passed','skipped'}
        assert summary['nonpassed'][0]['id']=='unit.test_context_catalog.ContextStoreTests.test_outside_symlink_is_reported_when_supported'
        scripts=REPO/tree/'skills/do-math/scripts'
        current={p.relative_to(scripts).as_posix():digest(p)['sha256'] for p in scripts.rglob('*.py') if '__pycache__' not in p.parts}
        assert current==report['source_sha256']
        before=json.loads((E/(label+'-before.json')).read_text(encoding='utf-8-sig'))
        after=json.loads((E/(label+'-after.json')).read_text(encoding='utf-8-sig'))
        immutable=[p for p in before if p.startswith(tree+'/skills/do-math/') and Path(p).name not in ('.timings.json','.timings-t3.json')]
        assert all(before[p]==after[p] for p in immutable)
        observation=json.loads((E/(label+'-observations.json')).read_text(encoding='utf-8-sig'))
        assert observation['official_exit_code']==0 and observation['single_proposal']
        query_states={r['status'] for r in observation['academic_queries']}
        assert query_states=={'not_applicable','incomplete','pending','active','completed','externally_rejected'},query_states
        check_states={r['status'] for r in observation['checks']}
        assert check_states=={'approved','revision_required','unresolved'},check_states
        for row in observation['checks']:
            value=json.loads((E/row['file']).read_text(encoding='utf-8'))
            check=value['check']
            assert check['bundle_sha256']==value['sha256']
            from hashlib import sha256
            # The product's exact JSON representation is used, while the
            # original values and expected verdicts remain in direct tests.
            sys.path[:0]=[str(scripts)]
            from do_math.canonical import exact_content_hash
            assert check['sha256']==exact_content_hash({k:v for k,v in check.items() if k!='sha256'})
        proposal_count=0
        for row in observation['final_returns']:
            value=json.loads((E/row['file']).read_text(encoding='utf-8'))['context']
            if row['proposal_count'] is None: continue
            proposal=value['role_review']['proposal']
            def count(node):
                if isinstance(node,dict): return int(node==proposal)+sum(count(v) for v in node.values())
                if isinstance(node,list): return sum(count(v) for v in node)
                return 0
            assert count(value)==1
            proposal_count+=1
        summary.update(fixed_tree_files=len(immutable),final_returns=len(observation['final_returns']),
            checked_returns=len(observation['checks']),academic_queries=len(observation['academic_queries']),
            academic_states=sorted(query_states),check_states=sorted(check_states),single_proposal_returns=proposal_count)
    out[label]=summary
assert out['c']['selected_ids']==out['c2']['selected_ids']==out['m']['selected_ids']
for row in out['c2']['nonpassed']: assert row['outcome']=='skipped'
assert observer_errors <= set(out['c2']['selected_ids'])
assert json.loads((E/'c/report.json').read_text(encoding='utf-8'))['source_sha256']==json.loads((E/'c2/report.json').read_text(encoding='utf-8'))['source_sha256']
final=snapshot('final'); start=json.loads((E/'start.json').read_text(encoding='utf-8'))
preserved=json.loads((E/'preservation.json').read_text(encoding='utf-8-sig'))
assert all(final[p]['sha256']==sha for p,sha in preserved['runtime_sha256'].items())
assert all(final[p]['sha256']==sha for p,sha in preserved['fixed_runtime_and_t4_sha256'].items())
assert all(digest(Path(p))['sha256']==sha for p,sha in preserved['tools'].items())
assert all(digest(RUN/r['path'])['sha256']==r['sha256'] for r in preserved['host_recordings'])
baseline=json.loads((RUN/'phases/018/tasks/job-cleanup/evidence/final-baseline.json').read_text(encoding='utf-8-sig'))
assert all(digest(Path(baseline['baseline'])/r['path'])['sha256']==r['sha256'] for r in baseline['files'])
assert all(start[r['path']]==final[r['path']] for r in preserved['corpus'])
save('final-preservation-check.json',{'runtime139':True,'fixed_boundary258':True,'corpus144':True,
    'tools5':True,'host8':True,'baseline910':True,'comparison':'Fresh post-suite bytes against the verified preservation metadata and current 022 baseline.'})
allowed=json.loads((RUN/'phases/023/phase.json').read_text(encoding='utf-8-sig'))['tasks'][0]['writes']
changes=[p for p in sorted(set(start)|set(final)) if start.get(p)!=final.get(p)]
assert set(changes)<=set(allowed)
prior=json.loads((RUN/'phases/022/manager-evidence/task-files.json').read_text(encoding='utf-8-sig'))
for path,sha in prior.items():
    assert digest(RUN/'phases/022/tasks/review-delivery'/path)['sha256']==sha,path
save('verification.json',{'suites':out,'changes':changes,'outside_writes':[],
    'source_count':len(final),'previous_task_files_unchanged':len(prior),
    'product_documents_unchanged':all(start[p]==final[p] for p in start if '/do-math/' in p and Path(p).suffix=='.md'),
    'observer_initial_failure':{'ids':sorted(observer_errors),'script':'run_suite_initial.py',
        'fix':'Read the actual prepared execution_profile.role; action.role is intentionally absent in these valid test inputs. Only the observer changed. Initial errors and output remain intact.'}})
print({k:{key:v[key] for key in ('selected','counts','exit_code','source_sha256_count')} for k,v in out.items()})
print('Authorized changes',len(changes),'original 022 task files preserved',len(prior))
