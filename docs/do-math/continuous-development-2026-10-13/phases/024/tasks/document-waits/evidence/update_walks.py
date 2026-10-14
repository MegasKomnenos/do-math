from work import *
phase=json.loads((RUN/'phases/024/phase.json').read_text(encoding='utf-8-sig'))
old="defer_governance=('import_payload', 'import_check', 'governance', 'academic_validation')"
new=old+", defer_waits=('change', 'plan_settle_wait')"
changed=[]
for relative in phase['tasks'][0]['writes']:
    if not relative.startswith('.claude/') or not relative.endswith('.py'):
        continue
    path=REPO/relative
    raw=path.read_bytes(); text=raw.decode('utf-8')
    if old in text:
        updated=text.replace(old,new)
        path.write_bytes(updated.encode('utf-8'))
        changed.append({'path':relative,'calls':text.count(old)})
save('walk-updates.json',changed)
print(changed)
