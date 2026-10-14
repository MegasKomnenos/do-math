from work import *
base=REPO/'.claude/skills/do-math/references'
edits={
 '지식-저작과-재사용.md': [('원자료는 `sources`의 `local_path`에서 읽는다.', '원자료는 `sources[].local_path`에서 읽는다.'), ('내용의 사본이 아니다.', '내용의 사본이 아니다. <!-- do-math fields: sources=research_sources -->')]
}
for name,replacements in edits.items():
    path=base/name
    raw=path.read_bytes()
    for before,after in replacements:
        assert raw.count(before.encode('utf-8'))==1,(name,before)
        raw=raw.replace(before.encode('utf-8'),after.encode('utf-8'))
    path.write_bytes(raw)
    print(name)
