from work import *
prior=json.loads((RUN/'phases/021/tasks/document-review/evidence/history-verification.json').read_text(encoding='utf-8-sig'))
rows=[]
for item in prior:
    argv=['git','show','--format=fuller',item['commit'],'--','.claude/skills/do-math/scripts/tests/support/doc_code.py']
    p=subprocess.run(argv,cwd=REPO,capture_output=True)
    assert p.returncode==0
    (E/(item['id']+'-doc-code.diff')).write_bytes(p.stdout)
    (E/(item['id']+'-doc-code.stderr')).write_bytes(p.stderr)
    text=p.stdout.decode('utf-8')
    lines=text.splitlines()
    excerpts=[]
    for i,line in enumerate(lines):
        if any(name in line for name in ('submission_check','route_submission_return',"schemas['repair']")):
            excerpts.append('\n'.join(lines[max(0,i-3):i+4]))
    reports=[]
    for row in item['reports']:
        path=REPO/row['path']
        assert path.is_file() and digest(path)['sha256']==row['sha256']
        value=json.loads(path.read_text(encoding='utf-8-sig'))
        reports.append({**row,'sha256':digest(path)['sha256'],
                       'actual_complete':value.get('complete'),'actual_successful':value.get('successful')})
    rows.append({'id':item['id'],'commit':item['commit'],'argv':argv,'exit_code':p.returncode,
                 'p07_excerpts':excerpts,'reports':reports})
save('history-verification.json',rows)
for row in rows:
    print(row['id'],row['commit'],'relevant excerpt count',len(row['p07_excerpts']),'reports',len(row['reports']))
    for excerpt in row['p07_excerpts']: print(excerpt)
