from work import *
board=json.loads((REPO/'docs/do-math/시험-재편-2026-09-29/단계-전환표-2026-10-03.json').read_text(encoding='utf-8-sig'))
rows=[]
def walk(node):
    if isinstance(node,dict):
        if node.get('id') in ('B110','B111','B112','B113','B114'):
            rows.append(node)
        for value in node.values(): walk(value)
    elif isinstance(node,list):
        for value in node: walk(value)
walk(board)
save('history-b110-b114.json', rows)
for row in rows:
    print(row['id'],json.dumps({k:v for k,v in row.items() if k in ('commit','summary','title','result','status','purpose','date')},ensure_ascii=False), 'keys',list(row))

sys.path.insert(0,str(REPO/'.claude/skills/writing-skills/scripts'))
import build_skill_mirrors as build
rules=build.load_rules(REPO/'.agents/diff')
planned=[]
allowed=json.loads((RUN/'phases/019/phase.json').read_text(encoding='utf-8-sig'))['tasks'][0]['writes']
for rel,path in build.iter_files(REPO/'.claude/skills').items():
    raw=path.read_bytes()
    target=REPO/'.agents/skills'/rel
    overlay=REPO/'.agents/diff'/rel
    transformed=overlay.read_bytes() if overlay.is_file() else build.transform(rel,raw,rules)
    if not target.exists() or transformed!=target.read_bytes():
        planned.append(target.relative_to(REPO).as_posix())
assert set(planned)<=set(allowed),set(planned)-set(allowed)
save('mirror-plan.json', {'changes':planned,'all_within_writes':True})
print('mirror plan',len(planned))
