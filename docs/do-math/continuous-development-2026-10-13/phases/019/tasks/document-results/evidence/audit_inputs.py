from work import *
phase=json.loads((RUN/'phases/019/phase.json').read_text(encoding='utf-8-sig'))
start=json.loads((E/'start.json').read_text(encoding='utf-8'))
rows=[]
for ref in phase['tasks'][0]['inputs']:
    root,rel=ref.split(':',1)
    path=(REPO if root=='repo' else RUN)/rel
    raw=path.read_bytes()
    obj=json.loads(raw.decode('utf-8-sig')) if path.suffix=='.json' else raw.decode('utf-8-sig')
    rows.append({'reference':ref,**digest(path),'start_source':start.get(rel) if root=='repo' else None,
                 'parsed_type':type(obj).__name__})
save('input-audit.json',{'inputs':rows,'meaning_scope':'The objective-authorized P02 owners, original 13-C/D-06 clauses, preserved P01/B130-B134, source roles, current producer/consumer definitions. Large inventory JSONs were selected by P02/four owners; byte parsing is not whole-project semantic review.'})
print('Required inputs parsed and hashed',len(rows))
argv=['git','diff','--no-ext-diff','--',*json.loads((E/'verification.json').read_text(encoding='utf-8'))['changes']]
proc=subprocess.run(argv,cwd=REPO,capture_output=True)
assert proc.returncode==0
(E/'changes.diff').write_bytes(proc.stdout)
(E/'changes-diff.stderr').write_bytes(proc.stderr)
save('changes-diff-command.json',{'argv':argv,'cwd':str(REPO),'exit_code':proc.returncode})
