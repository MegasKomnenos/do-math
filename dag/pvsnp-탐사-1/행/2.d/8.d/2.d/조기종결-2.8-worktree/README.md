# 2.8 worktree 조기 종결 채록

이 디렉토리는 국면 `pvsnp-탐사-1`의 조기 종결 전에 2.8 worktree에서 채록한 미커밋 산출을 보존한다. worktree의 HEAD는 `7f27db70019f5a48ddafc130931672e89b4c5123`이다. 원래 파일과 이 디렉터리의 복사본을 대조해 채록을 검증한다.

main에 병합되지 않은 2.8 브랜치의 커밋은 태그 `archive/pvsnp-탐사-1-2.8`로 보존한다. 태그는 이 문서의 HEAD를 가리킨다.

| 원래 상대 경로 | 상태 | SHA-256 |
|---|---|---|
| `research/pvsnp/maps/definitions.md` | 수정 | `15B7B3EAB98ADE850D24D2E23D3EF620CD6F2506AC6C5574B49DC07189057909` |
| `research/pvsnp/maps/corpus/L18-L22.md` | 수정 | `12EB831EF39D75E2819E448C4110C1DAEC35769F202BF6396A5F6FF6BA9FE23B` |
| `research/pvsnp/maps/corpus/L07-L11.md` | 미추적 | `B69F25E01E033BEF7F5435613638A911616EF099A5ADB6161398A17414622D7B` |
| `research/pvsnp/maps/corpus/L12-L17.md` | 미추적 | `6484184E2FBD5FD1E6BF88E4F56521532A9C72324C9AD2E3120344025A52E134` |

복사본은 원래 상대 경로를 보존한다. 원래 worktree는 복사본 검증 뒤 제거한다.
