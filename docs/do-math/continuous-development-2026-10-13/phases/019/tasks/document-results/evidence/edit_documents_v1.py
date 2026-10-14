from work import *
base=REPO/'.claude/skills/do-math/references'
edits={
 '공통-실행.md': [('판단에 그 목록의 항목이나 상세가 필요하면 `source_ref.path`를 열고, 기록된 해시와 크기에 대응하는 원문을 읽는다.', '판단에 그 목록의 항목이나 상세가 필요하면 `source_ref.path`를 열고, `source_ref.sha256`과 `source_ref.bytes`에 대응하는 원문을 읽는다.')],
 '지식-저작과-재사용.md': [('원자료는 `sources`의 `local_path`에서 읽는다.', '원자료는 `sources[].local_path`에서 읽는다.'), ('내용의 사본이 아니다.\r\n', '내용의 사본이 아니다. <!-- do-math fields: sources=research_sources -->\r\n')]
}
for name,replacements in edits.items():
    path=base/name
    raw=path.read_bytes()
    for before,after in replacements:
        assert raw.count(before.encode('utf-8'))==1,(name,before)
        raw=raw.replace(before.encode('utf-8'),after.encode('utf-8'))
    path.write_bytes(raw)
    print(name)
