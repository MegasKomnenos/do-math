from work import *
prior=json.loads((RUN/'phases/022/tasks/review-delivery/evidence/history-verification.json').read_text(encoding='utf-8-sig'))
rows=[]
for item in prior:
    argv=['git','show','--format=fuller',item['commit'],'--','.claude/skills/do-math/scripts/tests/support/doc_code.py']
    p=subprocess.run(argv,cwd=REPO,capture_output=True)
    assert p.returncode==0
    (E/(item['id']+'-doc-code.diff')).write_bytes(p.stdout)
    (E/(item['id']+'-doc-code.stderr')).write_bytes(p.stderr)
    lines=p.stdout.decode('utf-8').splitlines()
    excerpts=['\n'.join(lines[max(0,n-3):n+4]) for n,line in enumerate(lines) if any(name in line for name in
        ('import_payload','import_check','governance_view','academic_status',"schemas['governance']","schemas['academic_validation']"))]
    reports=[]
    for row in item['reports']:
        source=REPO/row['path']
        assert source.is_file() and digest(source)['sha256']==row['sha256']
        report=json.loads(source.read_text(encoding='utf-8-sig'))
        reports.append({**row,'actual_complete':report.get('complete'),'actual_successful':report.get('successful')})
    rows.append({'id':item['id'],'commit':item['commit'],'argv':argv,'exit_code':p.returncode,
        'relevant_excerpts':excerpts,'reports':reports})
board=json.loads((REPO/'docs/do-math/시험-재편-2026-09-29/단계-전환표-2026-10-03.json').read_text(encoding='utf-8-sig'))['current_work']
pure=[]
for name,commit in [('record_map_runtime_binding','08d5d217'),('summary_fact_runtime_bindings','369d23bb'),
    ('status_repository_document_binding','61e080b2'),('progress_file_document_binding','a60fb70e')]:
    item=board[name]
    report=item['report']; source=REPO/report['path']
    assert digest(source)['sha256']==report['sha256']
    value=json.loads(source.read_text(encoding='utf-8-sig'))
    p=subprocess.run(['git','show','--format=fuller',commit,'--',
        '.claude/skills/do-math/scripts/tests/support/doc_code.py',
        '.claude/skills/do-math/scripts/tests/structure/test_doc_code.py'],cwd=REPO,capture_output=True)
    assert p.returncode==0
    (E/(item['id']+'-binding.diff')).write_bytes(p.stdout)
    pure.append({'id':item['id'],'commit':commit,'original_board':item,
        'report_sha256':digest(source)['sha256'],'actual_complete':value.get('complete'),
        'actual_successful':value.get('successful'),
        'decision':'Maintain the closed actual-return/repository/file population and its existing negative owner assertions. This phase changes only the four governance/import owners and explicit document-walk delegation. The PURE/CLI helper functions and product producers remain byte-equivalent to the start snapshot; no historical counts are added to the new suite.'})
save('history-verification.json',{'ast_history':rows,'pure_history':pure,
    'scope':'P06/P10 hunk replacement only; PR24 and unrelated producers/hunks remain open.'})
for row in rows:
    print(row['id'],'P06/P10 excerpts',len(row['relevant_excerpts']),'existing reports',len(row['reports']))
    for excerpt in row['relevant_excerpts']: print(excerpt)
print('PURE exact originals',len(pure))
