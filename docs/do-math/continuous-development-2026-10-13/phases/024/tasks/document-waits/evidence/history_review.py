from work import *
prior=json.loads((RUN/'phases/023/tasks/document-governance/evidence/history-verification.json').read_text(encoding='utf-8-sig'))
rows=[]
for item in prior['ast_history']:
    argv=['git','show','--format=fuller',item['commit'],'--','.claude/skills/do-math/scripts/tests/support/doc_code.py']
    p=subprocess.run(argv,cwd=REPO,capture_output=True); assert p.returncode==0
    (E/(item['id']+'-doc-code.diff')).write_bytes(p.stdout)
    lines=p.stdout.decode('utf-8').splitlines()
    excerpts=['\n'.join(lines[max(0,n-3):n+4]) for n,line in enumerate(lines)
              if 'plan_settle_wait' in line or "schemas['change']" in line or 'decision_value_is' in line]
    for row in item['reports']:
        assert digest(REPO/row['path'])['sha256']==row['sha256']
        json.loads((REPO/row['path']).read_text(encoding='utf-8-sig'))
    rows.append({**item,'argv':argv,'exit_code':p.returncode,'relevant_excerpts':excerpts,
        'decision':'Replace only the P09/P11 consumed/produced AST approximations with real input/wait document boundaries. Retain owner aliasing, shared-schema fields, callable checks, other packet helpers and their direct tests. Missing history counts are not new evidence.'})
argv=['git','show','--format=fuller','8694693','--','.claude/skills/do-math/SKILL.md',
      '.claude/skills/do-math/references/CLI-실행-계약.md', '.claude/skills/do-math/scripts']
p=subprocess.run(argv,cwd=REPO,capture_output=True); assert p.returncode==0
(E/'D-06.diff').write_bytes(p.stdout)
save('history-verification.json',{'ast_history':rows,'D-06':{'argv':argv,'exit_code':p.returncode,
    'decision':'Keep removal of the obsolete initial-preparation barrier. Plan settling concerns queued contract reviews, not all candidates or unreturned preparation output. Initial events remain assigned until an accepted response consumes them. No legacy fields or timeout restored.'},
    'scope':'P09/P11 and D-06 hunks only; PR24/TRUST and unrelated N/L01 remain open.',
    'pure_history_retained':prior['pure_history']})
print([(r['id'],len(r['relevant_excerpts']),len(r['reports'])) for r in rows])
