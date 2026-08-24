---
name: ponytail-debt
description: 코드베이스의 `ponytail:` 주석 전수를 부채 원장으로 수확한다(ponytail-debt). 의도적 지름길과 유예가 "나중"이라는 이름으로 썩지 않게 추적한다. "ponytail 부채 보여줘", "뭘 미뤄뒀지", "list the shortcuts", "ponytail ledger", /ponytail-debt에서 호출한다. 1회성 보고이고 아무것도 바꾸지 않는다.
---

# ponytail-debt

의도적인 ponytail 지름길은 전부 한계와 승급 경로를 담은 `ponytail:` 주석으로 표시되어 있다. 이 스킬은 그것을 원장 하나로 모아, 유예가 조용히 영구화되는 것을 막는다.

## 원본 추적

- 원본: ponytail / ponytail / 4.9.0 / ponytail-debt
- 원본 경로: `~/.claude/plugins/cache/ponytail/ponytail/4.9.0/skills/ponytail-debt/`
- 원본 SKILL.md 해시: `ecbc0ca8161b25ced3b4f728398c2ec33988a777`
- 원본 라이선스: MIT (Dietrich Gebert)
- 대조표: `.agents/skills/ponytail/references/원본_대조.md` (4종 통합)
- 재검토 트리거: 원본 플러그인 갱신(해시 불일치) 또는 로컬 규범 개정. adapt-skill 재호출로 수행한다

## 스캔

저장소에서 주석 마커를 전수 검색한다. 패턴: `(#|//) ?ponytail:` (스택에 다른 주석 접두가 있으면 추가한다). 제외한다: `.agents/`(생성 미러의 이중 계수 방지), `node_modules`, `.git`, 빌드 산출물. 히트 하나가 원장 한 행이다. 주석 접두 조건이, 규약을 언급만 하는 산문을 원장 밖에 둔다.

## 출력

마커당 1행, 파일별로 묶는다:

`<파일>:<행>, <무엇을 단순화했나>. 한계: <지목된 한계>. 승급: <재방문 트리거>.`

규약이 `ponytail: <한계>, <승급 경로>`이므로 한계와 트리거는 주석에서 그대로 뽑는다. 행별 작성자가 필요하면 `git blame -L<행>,<행>`을 더한다.

승급 경로·트리거를 지목하지 않은 `ponytail:` 주석에는 `no-trigger` 태그를 단다. 조용히 썩는 것이 그것들이다.

끝맺음: `<N>개 마커, 그중 <M>개 no-trigger.` 발견이 없으면: `No ponytail: debt. Clean ledger.`

## 경계

- 읽고 보고만 하며 아무것도 바꾸지 않는다. 보존은 사용자가 요청할 때 파일(예: `PONYTAIL-DEBT.md`)로 쓴다. 1회성이다.
- "stop ponytail-debt" / "normal mode"로 이 스킬의 서식 제약을 해제한다.
