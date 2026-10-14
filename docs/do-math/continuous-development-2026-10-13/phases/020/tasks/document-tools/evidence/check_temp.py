from work import *
argv=['git','rev-parse','--show-toplevel']
root=Path(os.environ['TEMP'])
proc=subprocess.run(argv,cwd=root,capture_output=True)
(E/'temp-git.stdout').write_bytes(proc.stdout)
(E/'temp-git.stderr').write_bytes(proc.stderr)
save('temp-check.json',{'argv':argv,'cwd':str(root),'exit_code':proc.returncode,
                      'outside_repo':not root.resolve().is_relative_to(REPO),
                      'stdout':proc.stdout.decode('utf-8',errors='replace'),
                      'stderr':proc.stderr.decode('utf-8',errors='replace')})
assert not root.resolve().is_relative_to(REPO)
assert proc.returncode==128 and not proc.stdout.strip()
print('Parent TEMP is outside Git repository:',root,'git exit',proc.returncode)
