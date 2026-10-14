from work import *
rows=[]
for name in ('.timings.json','.timings-t3.json'):
    source=REPO/'.claude/skills/do-math/scripts/tests'/name
    target=REPO/'.agents/skills/do-math/scripts/tests'/name
    if target.read_bytes()!=source.read_bytes(): target.write_bytes(source.read_bytes())
    assert digest(source)==digest(target)
    rows.append({'name':name,**digest(source)})
save('cache-sync.json',rows)
print('Canonical/mirror cost caches equal')
