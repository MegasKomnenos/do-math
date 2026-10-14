from work import *
root=Path(os.environ['TEMP'])
argv=['git','rev-parse','--show-toplevel']
p=subprocess.run(argv,cwd=root,capture_output=True)
(E/'temp-git.stdout').write_bytes(p.stdout)
(E/'temp-git.stderr').write_bytes(p.stderr)
save('temp-check.json',{'argv':argv,'cwd':str(root),'exit_code':p.returncode,
    'outside_repo':not root.resolve().is_relative_to(REPO),
    'stdout':p.stdout.decode('utf-8',errors='replace'),'stderr':p.stderr.decode('utf-8',errors='replace')})
assert not root.resolve().is_relative_to(REPO)
assert p.returncode==128 and not p.stdout.strip()
print('Parent TEMP outside repository',root,'git exit',p.returncode)
