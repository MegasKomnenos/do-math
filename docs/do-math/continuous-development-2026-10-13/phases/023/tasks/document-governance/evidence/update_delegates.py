from work import *
phase=json.loads((RUN/'phases/023/phase.json').read_text(encoding='utf-8-sig'))
changed=[]
for path in phase['tasks'][0]['writes']:
    if not path.startswith('.claude/') or not path.endswith('.py'):
        continue
    source=REPO/path
    text=source.read_text(encoding='utf-8')
    updated=text.replace("defer_delivery_inputs=('submission_check', 'repair')",
        "defer_delivery_inputs=('submission_check', 'repair'), defer_governance=('import_payload', 'import_check', 'governance', 'academic_validation')")
    if updated!=text:
        source.write_text(updated,encoding='utf-8')
        changed.append(path)
save('delegated-consumers.json',changed)
print('Updated',len(changed),'existing owner document consumers')
