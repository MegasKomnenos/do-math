from work import *
import re
commits={'B110':'0c5ebdb7','B111':'2b78e597','B112':'8af6e011','B113':'7823c9a0','B114':'136dc3d5'}
rows=json.loads((E/'history-b110-b114.json').read_text(encoding='utf-8'))
observations=[]
for row in rows:
    bid=row['id']
    argv=['git','show','--format=fuller',commits[bid],'--','.claude/skills/do-math/scripts/tests/support/doc_code.py','.claude/skills/do-math/scripts/tests/structure/test_doc_code.py','.claude/skills/do-math/references']
    proc=subprocess.run(argv,cwd=REPO,capture_output=True)
    assert proc.returncode==0
    (E/(bid+'.diff')).write_bytes(proc.stdout)
    text=proc.stdout.decode('utf-8')
    hunks=[h for h in re.split(r'(?=^@@)',text,flags=re.M) if any(word in h for word in ('execution_window','scholarly','formal_verifier','preview','read_tool','submission_contract'))]
    (E/(bid+'-p03.diff')).write_text('\n'.join(hunks),encoding='utf-8')
    reports=[]
    def visit(node):
        if isinstance(node,dict):
            path=node.get('path')
            if isinstance(path,str) and '/검증/' in path and path.endswith('.json'):
                file=REPO/path
                entry={'path':path,'exists':file.is_file(),'expected_sha256':node.get('sha256')}
                if file.is_file():
                    entry.update(digest(file))
                    obj=json.loads(file.read_text(encoding='utf-8-sig'))
                    entry['actual_complete']=obj.get('complete')
                    entry['actual_successful']=obj.get('successful')
                    if node.get('sha256'): assert entry['sha256']==node['sha256']
                reports.append(entry)
            for value in node.values(): visit(value)
        elif isinstance(node,list):
            for value in node:visit(value)
    visit(row)
    observations.append({'id':bid,'commit':commits[bid],'p03_hunks':len(hunks),'reports':reports})
    print(bid, 'hunks',len(hunks),'reports',len(reports),'present',sum(r['exists'] for r in reports))
save('history-verification.json',observations)
print('P03 DIFF selected lines:')
for bid in commits:
    print(bid)
    for line in (E/(bid+'-p03.diff')).read_text(encoding='utf-8').splitlines():
        if line.startswith(('+','-')) and any(word in line for word in ('execution_window','scholarly','formal_verifier','preview','read_tool','submission_contract')):
            print(line)
