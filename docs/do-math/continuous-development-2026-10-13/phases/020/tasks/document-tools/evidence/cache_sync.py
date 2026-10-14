from work import *
changed=[]
for name in ('.timings.json','.timings-t3.json'):
    source=REPO/'.claude/skills/do-math/scripts/tests'/name
    target=REPO/'.agents/skills/do-math/scripts/tests'/name
    if source.read_bytes()!=target.read_bytes():
        target.write_bytes(source.read_bytes());changed.append(target.relative_to(REPO).as_posix())
save('cache-sync.json',{'changes':changed,'canonical_cache_preserved':True})
print('Synchronized caches',changed)
