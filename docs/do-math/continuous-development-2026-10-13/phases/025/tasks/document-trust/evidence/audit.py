from work import *
from collections import Counter
labels=sys.argv[1:] or ['red','focus','c','c2','m']
out={}
for name in labels:
    process=json.loads((E/(name+'-process.json')).read_text(encoding='utf-8'))
    report=json.loads((E/name/'report.json').read_text(encoding='utf-8-sig'))
    rows=[row for group in report['reports'] for row in group['rows'] if not row.get('fixture')]
    selected=report['selected']
    assert len(selected)==len(set(selected))==len(rows)==len({r['id'] for r in rows})
    assert set(selected)=={r['id'] for r in rows}
    assert not report['changed_during_run']
    entry={'selected':len(selected),'rows':len(rows),'selected_ids':selected,
        'counts':dict(Counter(r['outcome'] for r in rows)),'exit_code':process['exit_code'],
        'complete':report['complete'],'successful':report['successful'],
        'source_sha256_count':len(report['source_sha256']),
        'nonpassed':[r for r in rows if r['outcome']!='passed'],'total_seconds':report['total_seconds']}
    if name in ('c2','m'):
        assert process['exit_code']==0 and report['complete'] and report['successful']
        assert entry['counts']=={'passed':len(selected)}
        tree='.claude' if name=='c2' else '.agents'
        scripts=REPO/tree/'skills/do-math/scripts'
        source={p.relative_to(scripts).as_posix():digest(p)['sha256'] for p in scripts.rglob('*.py')
                if '__pycache__' not in p.parts}
        assert source==report['source_sha256']
        before=json.loads((E/(name+'-before.json')).read_text())
        after=json.loads((E/(name+'-after.json')).read_text())
        assert all(before[p]==after[p] for p in before if Path(p).name not in ('.timings.json','.timings-t3.json'))
        observations=[]
        for path in sorted((E/('observations-'+name)).glob('*.jsonl')):
            observations.extend(json.loads(line) for line in path.read_text(encoding='utf-8').splitlines())
        errors=[r for r in observations if r['kind']=='observer_error']
        # The optional complete packaging return includes raw installation
        # bytes. Its failed JSON capture is retained; it does not affect any
        # P08 trust/Job observation. Current proposal cardinality is directly
        # asserted by the unchanged selected review-stage test.
        assert all(r['target']=='prepared' and 'bytes is not JSON serializable' in r['error'] for r in errors),errors
        trust=[r for r in observations if r['kind'] in ('project','toolchain','environment_check')]
        kinds=Counter(r['kind'] for r in trust)
        assert all(kinds[k] for k in ('project','toolchain','environment_check'))
        environment=[r for r in trust if r['kind']=='environment_check']
        positive=[r for r in environment if r['value']['status']=='verified']
        invalid=[r for r in environment if r['value']['status']=='invalid']
        rebind=[r for r in positive if 'rebind' in r['value']]
        changes=[r for r in invalid if 'changed_files' in r['value']]
        early=[r for r in invalid if 'changed_files' not in r['value']]
        assert positive and invalid and rebind and early and changes
        assert any(r['value']['changed_file_count']==55 and len(r['value']['changed_files'])==50 for r in changes)
        assert all('changed_files' not in r['value'] and 'changed_file_count' not in r['value'] for r in positive)
        assert all(r['value']['rebind']['previous']==r['input_binding'] and
            r['value']['binding']==r['value']['rebind']['current'] for r in rebind)
        toolchain=[r for r in trust if r['kind']=='toolchain']
        assert any(r['value']['project'] is None for r in toolchain)
        assert any(isinstance(r['value']['project'],dict) and r['value']['project']['search_paths'] for r in toolchain)
        finals=[r for r in observations if r['kind']=='prepared']
        assert all(r['proposal_count']==1 for r in finals)
        proposal_rows=[r for r in rows if r['id'].endswith('.test_review_stage_documents_reach_the_final_seat_input')]
        assert len(proposal_rows)==1 and proposal_rows[0]['outcome']=='passed'
        jobs=[r for r in observations if r['kind']=='job']
        actual_cwd=[{'command':r['command'],'cwd':r['workspace'],'characters':len(r['workspace']),
                    'exit_code':r['value'][0],'stopped':r['value'][3]} for r in jobs]
        installed_jobs=[r for r in actual_cwd if r['command'][0].startswith(str(REPO/'.skill-workspace'))]
        assert installed_jobs and all(r['exit_code']==0 and not r['stopped'] for r in installed_jobs)
        save(name+'-actual-returns.json',{'trust_returns':trust,'final_proposals':finals,
            'job_calls':jobs,'resource_cwd':actual_cwd,'installed_jobs':installed_jobs,
            'optional_packaging_capture_errors':errors,
            'packaging_limit':'Complete prepare_role_input returns contain raw archive bytes and were not captured as JSON; P08 trust/installed Job returns are all captured. The current exact selected review-stage test still independently asserts one proposal per final input, and 024 unchanged-producer raw samples remain retained.'})
        entry.update(observed=dict(kinds),verified=len(positive),invalid=len(invalid),
            rebind=len(rebind),changed_files=len(changes),early_invalid=len(early),
            captured_single_proposal=len(finals),actual_job_count=len(jobs),installed_job_count=len(installed_jobs),
            optional_packaging_observer_errors=len(errors),current_single_proposal_property_row=proposal_rows[0])
        save(name+'-resource-cwd.json',actual_cwd)
    out[name]=entry
save('verification-'+('-'.join(labels))+'.json',out)
print({k:{key:r[key] for key in ('selected','counts','exit_code')} for k,r in out.items()})
if 'c2' in out and 'm' in out:
    assert out['c2']['selected_ids']==out['m']['selected_ids']
    for name in ('red','focus','c'):
        assert set(r['id'] for r in out[name]['nonpassed'])<=set(out['c2']['selected_ids'])
    final=snapshot('final'); start=json.loads((E/'start.json').read_text())
    changes=sorted(p for p in set(start)|set(final) if start.get(p)!=final.get(p))
    allowed=json.loads((RUN/'phases/025/phase.json').read_text())['tasks'][0]['writes']
    assert set(changes)<=set(allowed),set(changes)-set(allowed)
    save('verification.json',{'suites':out,'changes':changes,'source_count':len(final),
        'outside_writes':[],'same_final_selection':True,
        'limitations':'Narrow task only; no full ordinary/fresh T3/all-function mutation/final G7 revision or final review. Historical 1314 symlink absence, policy meanings and L01 decisions remain.'})
    print('Authorized changes',len(changes),'final source count',len(final))
