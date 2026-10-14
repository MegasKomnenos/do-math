from work import *
sys.path.insert(0,str(REPO/'.claude/skills/writing-skills/scripts'))
import build_skill_mirrors as build
rules=build.load_rules(REPO/'.agents/diff')
planned=[]
allowed=json.loads((RUN/'phases/021/phase.json').read_text(encoding='utf-8-sig'))['tasks'][0]['writes']
for rel,path in build.iter_files(REPO/'.claude/skills').items():
    target=REPO/'.agents/skills'/rel
    overlay=REPO/'.agents/diff'/rel
    transformed=overlay.read_bytes() if overlay.is_file() else build.transform(rel,path.read_bytes(),rules)
    if not target.exists() or transformed!=target.read_bytes():planned.append(target.relative_to(REPO).as_posix())
assert set(planned)<=set(allowed),set(planned)-set(allowed)
save('mirror-plan.json',{'changes':planned,'all_within_writes':True})
print('mirror plan',len(planned),planned)
