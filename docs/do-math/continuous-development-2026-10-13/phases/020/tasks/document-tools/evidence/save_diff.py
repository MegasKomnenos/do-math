from work import *
paths=json.loads((E/'verification.json').read_text())['changes']
argv=['git','diff','--no-ext-diff','--',*paths]
proc=subprocess.run(argv,cwd=REPO,capture_output=True)
(E/'changes.diff').write_bytes(proc.stdout)
(E/'changes-diff.stderr').write_bytes(proc.stderr)
save('changes-diff-command.json',{'argv':argv,'cwd':str(REPO),'exit_code':proc.returncode})
assert proc.returncode==0
print('Saved actual diff for',len(paths),'changed paths')
