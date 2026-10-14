from work import *
scripts=REPO/'.claude/skills/do-math/scripts'
sys.path[:0]=[str(scripts),str(scripts/'tests')]
from do_math import formal
from do_math.wiring import real_ports
from support.entry import entry
values=entry()
ports=real_ports(environment=values.environment)
project=scripts/'tests'
observed=formal.project_source_identity(project,git_backend=ports.git_backend)
queries=[]
def git(*arguments):
    argv=['git','-C',str(REPO),*arguments]
    p=subprocess.run(argv,cwd=REPO,capture_output=True,env=values.environment)
    assert p.returncode==0,(argv,p.stderr)
    index=len(queries)
    (E/f'git-identity-{index}.stdout').write_bytes(p.stdout)
    (E/f'git-identity-{index}.stderr').write_bytes(p.stderr)
    queries.append({'argv':argv,'exit_code':p.returncode,'stdout_file':f'git-identity-{index}.stdout',
                    'stderr_file':f'git-identity-{index}.stderr'})
    return p.stdout
relative=project.relative_to(REPO).as_posix()
tree=git('rev-parse','--verify','HEAD:'+relative).decode().strip()
diff=git('diff','--no-ext-diff','HEAD','--',relative)
tracked=set(git('ls-files','-z','--',relative).decode().split('\0'))
# Explicit untracked input expectation from native Git's current tracked set
# and the real files. This reads files only; no Git state is changed.
untracked={}
for path in project.rglob('*'):
    if not path.is_file() or '.lake' in path.relative_to(project).parts:
        continue
    if path.suffix=='.lean' or path.name in ('lean-toolchain','lake-manifest.json','lakefile.lean','lakefile.toml'):
        if path.relative_to(REPO).as_posix() not in tracked:
            untracked[path.relative_to(project).as_posix()]=digest(path)['sha256']
expected={'root':str(project.resolve()),'git_tree':tree,'working_diff_hash':hashlib.sha256(diff).hexdigest(),
          'untracked_file_count':len(untracked),'untracked_sha256':hashlib.sha256(
              json.dumps(untracked,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()}
assert observed==expected,(observed,expected)
assert diff, 'The real current tests include working-tree changes'
save('actual-git-project.json',{'producer':'formal.project_source_identity','ports':'real_ports.git_backend',
    'actual':observed,'expected_from_native_Git_and_files':expected,'untracked_inputs':untracked,'queries':queries,
    'scope':'Read-only observation of the actual tracked current test subtree and its working diff; dedicated positive/untracked and .lake-exclusion axes use the retained project scene tests. No Git init/add/commit/reset/checkout/push.'})
lake_root=REPO/'.skill-workspace/do-math-toolchains/lean-4.32.0/lean-4.32.0-windows/src/lean/lake/Lake'
files=[]
for rel in ('Config/Workspace.lean','Util/LakePath.lean'):
    path=lake_root/rel
    if path.is_file():
        lines=path.read_text(encoding='utf-8').splitlines()
        excerpts=[{'line':i+1,'text':'\n'.join(lines[max(0,i-2):i+4])} for i,line in enumerate(lines)
                  if any(key in line for key in ('augmentedLeanPath','augmentedLeanSrcPath','leanSrcPath :=','libDir'))]
        files.append({'path':str(path),**digest(path),'excerpts':excerpts})
save('lake-search-path-contract.json',{'installed_source':files,
    'expectation':'The package build/lib/lean path plus the installed Lean lib/lean and src/lean/lake paths follow installed Lake workspace augmentation. The original single-project-path expectation omitted the two system directories; c keeps that failure.'})
print('Actual tracked Git tree/diff/untracked producer matches native read-only Git and files',observed)
