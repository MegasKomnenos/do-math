from work import *
paths=[row['path'] for row in json.loads((E/'change-coordinates.json').read_text(encoding='utf-8'))]
argv=['git','diff','--check','--',*paths]
p=subprocess.run(argv,cwd=REPO,capture_output=True)
(E/'git-diff-check.stdout').write_bytes(p.stdout)
(E/'git-diff-check.stderr').write_bytes(p.stderr)
save('git-diff-check.json',{'argv':argv,'cwd':str(REPO),'exit_code':p.returncode,
    'checked_paths':paths})
print('git diff --check',len(paths),'paths exit',p.returncode)
assert p.returncode==0
