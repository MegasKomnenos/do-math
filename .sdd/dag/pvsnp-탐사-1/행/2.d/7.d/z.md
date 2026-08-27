---
행: 2.7.z
유형: 싱크
---

# 문헌 22건 확보·판독 노드 결산

- 목표: 검증된 문헌 기록과 S2 원장을 저장소에 병합하고 하류 선행연구 지도에 노출한다.
- 완료 기준: (1) 자식 완료 신호 전건과 22개 문헌 기록이 실재한다. (2) 원장은 URL·문헌 좌표·공개 접근 로그·학술DB 접근 로그 또는 해당 없음·기록 좌표의 22행 대응을 갖는다. (3) 각 기록의 서지·확보 상태·읽은 범위·핵심 주장·한정·인용 좌표·`PASS|FAIL`을 증거 실물과 대조한다. (4) 학술DB 입력이 공개 실패 목록으로 한정됐고 Playwright 직접 조작 증거가 있다. (5) 행 `2.7.5.8`의 비밀 검사 결과가 0건이고 대상 전수성이 성립한다. 행 `2.7.8`은 그 증거와 후행 크리덴셜 직접 입력 0건을 `PASS`로 판정한다. 행 `2.7.z`는 크리덴셜 파일과 값을 읽지 않는다. (6) 행 `2.7.8`의 감사 목록 형식과 정렬을 검사한다. 병합 직전에 같은 커밋 후보에서 상대 경로·바이트 길이·SHA-256 목록을 다시 만든다. 두 목록이 바이트 단위로 같아야 한다. 목록이 다르거나 행 `2.7.8`의 두 검사 중 하나가 `FAIL`이면 병합하지 않고 `단계: 차단`으로 끝낸다. (7) 공개 PDF·공개 데이터셋·구독 원본을 포함한 외부 원문이 커밋 후보에 0건이다. 커밋 후보가 행 `2.7.8`의 닫힌 허용 경로 안에 있어야 한다. (8) Markdown 연구 문서·보고·결산은 한국어 산문이고 수식은 LaTeX다. 원시 로그·데이터·외부 원문은 산문 형식 검사에서 제외한다. (9) 기준 (1)~(8)이 모두 통과한 뒤 한 커밋으로 병합한다. (10) S2를 `노출됨`으로 전기하고 `단계: 종결`로 끝낸다.
- 작업 디렉토리: C:\Users\wogud\AppData\Local\dag-wt\pvsnp-탐사-1+2.7
- 명령: python C:\math\.claude\skills\do-dag\scripts\dag_check.py --table C:\math\.sdd\dag\pvsnp-탐사-1\파견표.md
  python C:\math\.claude\skills\do-dag\scripts\dag_marker.py
- 스킬 루트: C:\math\.claude\skills\do-dag
- 모델_프리셋: codex-full
- 검증런_모델_프리셋: codex-full
- 계약: C:\math\.claude\skills\do-dag\계약\공통.md, C:\math\.claude\skills\do-dag\계약\싱크.md
- 불변식: C:\math\.sdd\dag\pvsnp-탐사-1\행\0.d\불변식.md, C:\math\.sdd\dag\pvsnp-탐사-1\행\0.d\불변식-2.md, C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\불변식.md, C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\7.d\불변식.md
- 겨냥: 2.7 worktree 변경 전건 · 메인 병합 인덱스 배타 점유 · C:\math\.sdd\dag\pvsnp-탐사-1\이음새.md S2 · C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\7.d\z-결산.md · worktree와 브랜치 회수
- 정본: C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\7.md, C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\7.d\5.d\8-보고.md, C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\7.d\8-보고.md, C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\7.d\8-감사목록.tsv, C:\math\.sdd\dag\pvsnp-탐사-1\이음새.md S2, C:\math\.claude\skills\do-dag\계약\싱크.md
- 읽기 목록: C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\7.md, C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\7-보고.md, C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\7.d\2-보고.md, C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\7.d\3.d\종료보고.md, C:\math\.sdd\dag\pvsnp-탐사-1\결정\2.7-첫문헌판독.md, C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\7.d\4-보고.md, C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\7.d\5-보고.md, C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\7.d\5.d\8-보고.md, C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\7.d\6.d\종료보고.md, C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\7.d\8-보고.md, C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\7.d\8-감사목록.tsv, C:\math\.sdd\dag\pvsnp-탐사-1\이음새.md, C:\math\.sdd\dag\pvsnp-탐사-1\행\0.d\불변식.md, C:\math\.sdd\dag\pvsnp-탐사-1\행\0.d\불변식-2.md, C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\불변식.md, C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\7.d\불변식.md, C:\math\.claude\skills\do-dag\계약\공통.md, C:\math\.claude\skills\do-dag\계약\싱크.md
- 모델 배정 근거: Claude opus low — 배정표 codex-full(싱크 gpt-5.6-terra low)에서 이탈한다. 이 행은 격리 없이 메인 체크아웃 저장소에 병합·커밋하고, 불변식 6항 (3)이 저장소에 닿는 격리 없는 행의 Codex 배정을 막는다(사용자확정 결정 C:\math\.sdd\dag\pvsnp-탐사-1\결정\사용자확정-codexfull전환.md). 단계 원장과 병합 절차가 잣대를 고정한다.
- 예산:
  [실측기 budget]
  명령: python dag_measure.py budget --files C:/math/.sdd/dag/pvsnp-탐사-1/행/2.d/7.md,C:/math/.sdd/dag/pvsnp-탐사-1/행/2.d/7-보고.md,C:/math/.sdd/dag/pvsnp-탐사-1/행/2.d/7.d/2-보고.md,C:/math/.sdd/dag/pvsnp-탐사-1/행/2.d/7.d/3.d/종료보고.md,C:/math/.sdd/dag/pvsnp-탐사-1/결정/2.7-첫문헌판독.md,C:/math/.sdd/dag/pvsnp-탐사-1/행/2.d/7.d/4-보고.md,C:/math/.sdd/dag/pvsnp-탐사-1/행/2.d/7.d/5-보고.md,C:/math/.sdd/dag/pvsnp-탐사-1/행/2.d/7.d/5.d/8-보고.md,C:/math/.sdd/dag/pvsnp-탐사-1/행/2.d/7.d/6.d/종료보고.md,C:/math/.sdd/dag/pvsnp-탐사-1/행/2.d/7.d/8-보고.md,C:/math/.sdd/dag/pvsnp-탐사-1/행/2.d/7.d/8-감사목록.tsv,C:/math/.sdd/dag/pvsnp-탐사-1/이음새.md,C:/math/.sdd/dag/pvsnp-탐사-1/행/0.d/불변식.md,C:/math/.sdd/dag/pvsnp-탐사-1/행/0.d/불변식-2.md,C:/math/.sdd/dag/pvsnp-탐사-1/행/2.d/불변식.md,C:/math/.sdd/dag/pvsnp-탐사-1/행/2.d/7.d/불변식.md,C:/math/.claude/skills/do-dag/계약/공통.md,C:/math/.claude/skills/do-dag/계약/싱크.md --model opus --writes 18000 --pending 120000
  시각: 2026-08-25T15:11:48Z
  대상해시: sha1:18af922b3f9c
  미해석: C:/math/.sdd/dag/pvsnp-탐사-1/행/2.d/7.d/5.d/8-보고.md · C:/math/.sdd/dag/pvsnp-탐사-1/행/2.d/7.d/6.d/종료보고.md · C:/math/.sdd/dag/pvsnp-탐사-1/행/2.d/7.d/8-보고.md · C:/math/.sdd/dag/pvsnp-탐사-1/행/2.d/7.d/8-감사목록.tsv
  .claude\skills\do-dag\계약\공통.md: ~4,077tok
  .claude\skills\do-dag\계약\싱크.md: ~10,040tok
  .sdd\dag\pvsnp-탐사-1\결정\2.7-첫문헌판독.md: ~7,086tok
  .sdd\dag\pvsnp-탐사-1\이음새.md: ~1,225tok
  .sdd\dag\pvsnp-탐사-1\행\0.d\불변식-2.md: ~916tok
  .sdd\dag\pvsnp-탐사-1\행\0.d\불변식.md: ~1,395tok
  .sdd\dag\pvsnp-탐사-1\행\2.d\7-보고.md: ~3,602tok
  .sdd\dag\pvsnp-탐사-1\행\2.d\7.d\2-보고.md: ~2,389tok
  .sdd\dag\pvsnp-탐사-1\행\2.d\7.d\3.d\종료보고.md: ~1,380tok
  .sdd\dag\pvsnp-탐사-1\행\2.d\7.d\4-보고.md: ~2,017tok
  .sdd\dag\pvsnp-탐사-1\행\2.d\7.d\5-보고.md: ~4,427tok
  .sdd\dag\pvsnp-탐사-1\행\2.d\7.d\불변식.md: ~2,479tok
  .sdd\dag\pvsnp-탐사-1\행\2.d\7.md: ~4,664tok
  .sdd\dag\pvsnp-탐사-1\행\2.d\불변식.md: ~2,875tok
  미존재 정본: ~63,158tok (120,000바이트 — 측정 시점 미존재)
  읽기 합계: ~111,730tok (문자계열 단가 견적)
  하네스 기저: ~28,000tok (시스템 프롬프트·툴 스키마·스킬 목록 — 실측 상수)
  도구 왕복: ~10,000tok (셸·검색 결과, 편집 회신 — 실측 상수)
  출력 유보: ~35,000tok (하한 — 저작 예상 18,000바이트는 하한 미달)
  소요 견적: ~184,730tok
  판정: opus 250,000 대비 예산 안
  [/실측기]
- 산출: C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\7.d\z-결산.md
- 반환: 공통 최종 반환 계약을 따른다. 완료 첫 줄은 `DONE`. 공통 필드 뒤에 `결산: <절대 경로>`를 추가한다.
- 이음새: S2를 `노출됨`으로 전기한다. 행 `2.8`이 22건 상태·주장·한정·인용 좌표·FAIL 목록을 소비한다.
- 이월 사슬: S2 최종 원장과 검증 잔여를 `2.8`·`2.12`에 넘긴다.
- 안전 속성·계약: 판정 전에 병합하지 않는다. 크리덴셜 값을 결산에 적지 않는다. 외부 원본을 커밋하지 않는다.

## 임무

1. `계약/싱크.md`의 노드 싱크 절차와 단계 원장을 따른다.
2. 보고의 편집 귀속과 worktree diff를 대조한다.
3. 2.7 완료 기준과 자식 완료 기준의 증거 실물을 전부 연다.
4. 행 `2.7.5.8` 보고의 비밀 검사 0건·대상 전수성과 행 `2.7.8` 보고의 후행 입력·외부 원문 검사를 대조한다.
5. 행 `2.7.8` 감사 목록의 형식과 정렬을 검사한다.
6. 병합 직전 같은 커밋 후보의 감사 목록을 다시 만든다.
7. 두 감사 목록을 바이트 단위로 대조한다.
8. 두 검사 중 하나가 `FAIL`이면 병합하지 않는다.
9. 두 감사 목록이 다르면 병합하지 않는다.
10. S2를 `노출됨`으로 전기하고 잔여 소유자를 적는다.
