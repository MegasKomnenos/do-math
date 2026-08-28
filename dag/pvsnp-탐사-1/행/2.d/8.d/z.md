---
행: 2.8.z
유형: 싱크
---

# 선행연구·장벽 지도 노드 싱크

- 목표: 검증된 지도 네 파일과 S3 노출 증거를 메인 `main`에 한 번 병합한다.
- 완료 기준: (1) `research/pvsnp/maps/definitions.md`·`prior-work.md`·`barriers.md`·`claim-source-matrix.md`가 전건 실재한다. (2) 최종 정리의 `재판독 상태` 22개, 직후 종료보고의 `재판독 상태 판정` 22개, 누적 종료보고의 `누적 재판독 상태 판정` 2개를 소비한다. L04·L05·L15는 원 FAIL 대신 재작업·수리된 최종 정리와 그 직후 `{경량}` 검증런 판정을 소비한다. 누적 FAIL은 그 원인 문헌이 전건 대체 소비되면 대체된 것으로 읽는다. `누적 봉쇄 접근 판정`은 소비하지 않는다. 값 하나라도 없거나 FAIL이면 병합하지 않고 `완료미충족`으로 닫는다. (3) 원자료 6절의 5항목이 각각 지도 완료 기준과 `claim-source-matrix.md` 요구→지도 표에 연결된다. (4) 문헌→지도 표가 L01~L22 전건을 가진다. (5) 알려진 부분 결과와 조건부 결과가 분리되고, 조건부 결과는 전제와 결론이 분리된다. (6) relativization·natural proofs·algebrization의 가정·적용 범위·비적용 범위가 실재한다. 세 장벽을 `P\ne NP` 증거로 쓴 항목은 0건이다. (7) 제한 회로와 일반 회로의 차이가 실재한다. 제한 결과를 일반 회로 결과로 확대한 항목은 0건이다. (8) 지도 항목마다 재판독 정리 좌표, 원문 인용 좌표, 확인 강도가 있다. (9) 내용 게이트와 반려 소비 전개의 완료 신호가 실재한다. (10) 지식자산 작업자와 직후 `{경량}` 검증런의 일대일 대응, 누적 검증런, 기각 보관 검토가 전건 완결했다. (11) 귀속 대조와 파견표 검산이 통과한다. (12) S3를 `노출됨`으로 전기하고 증거 좌표를 쓴다. (13) 노드 병합·커밋·worktree 회수·grant 해제·lease 반납 뒤 `z-결산.md`의 단계가 `종결`이다.
- 작업 디렉토리: C:\math
- 명령: python C:\math\.claude\skills\do-dag\scripts\dag_check.py --table C:\math\.sdd\dag\pvsnp-탐사-1\파견표.md
  python C:\math\.claude\skills\do-dag\scripts\dag_marker.py
- 스킬 루트: C:\math\.claude\skills\do-dag
- 모델_프리셋: codex-full
- 검증런_모델_프리셋: codex-full
- 계약: C:\math\.claude\skills\do-dag\계약\공통.md, C:\math\.claude\skills\do-dag\계약\싱크.md
- 불변식: C:\math\.sdd\dag\pvsnp-탐사-1\행\0.d\불변식.md, C:\math\.sdd\dag\pvsnp-탐사-1\행\0.d\불변식-2.md, C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\불변식.md, C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\불변식-2.md, C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\8.d\불변식.md
- 겨냥: 브랜치 `dag/pvsnp-탐사-1/2.8`, worktree `C:\Users\wogud\AppData\Local\dag-wt\pvsnp-탐사-1+2.8`, 메인 체크아웃 병합 인덱스와 lease, `research/pvsnp/maps/definitions.md`, `research/pvsnp/maps/prior-work.md`, `research/pvsnp/maps/barriers.md`, `research/pvsnp/maps/claim-source-matrix.md`, C:\math\.sdd\dag\pvsnp-탐사-1\이음새.md의 S3, C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\8.d\z-결산.md
- 정본: C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\8-보고.md, C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\8.d\2-보고.md, C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\8.d\3-보고.md, C:\math\.sdd\dag\pvsnp-탐사-1\파견표.md, C:\math\.sdd\dag\pvsnp-탐사-1\이음새.md
- 읽기 목록: C:\math\.sdd\dag\pvsnp-탐사-1\행\0.d\불변식.md, C:\math\.sdd\dag\pvsnp-탐사-1\행\0.d\불변식-2.md, C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\불변식.md, C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\불변식-2.md, C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\8.d\불변식.md, C:\math\.claude\skills\do-dag\계약\공통.md, C:\math\.claude\skills\do-dag\계약\싱크.md, C:\math\.claude\skills\commit-harness\SKILL.md, C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\8-보고.md, C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\8.d\2-보고.md, C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\8.d\3-보고.md, C:\math\.sdd\dag\pvsnp-탐사-1\파견표.md, C:\math\.sdd\dag\pvsnp-탐사-1\이음새.md, worktree의 지도 네 파일과 자식 보고·검증런 종료보고 전건
- 모델 배정 근거: 저장소에 닿는 격리 없는 실행 싱크이므로 `사용자확정-codexfull전환.md` 「메인 결정」 2항과 불변식 6항 (3)을 적용해 codex-full 싱크 `gpt-5.6-terra low` 대신 Claude `opus low`로 도출한다.
- 예산:
  [실측기 budget]
  명령: python dag_measure.py budget --files C:/math/.sdd/dag/pvsnp-탐사-1/행/0.d/불변식.md,C:/math/.sdd/dag/pvsnp-탐사-1/행/0.d/불변식-2.md,C:/math/.sdd/dag/pvsnp-탐사-1/행/2.d/불변식.md,C:/math/.sdd/dag/pvsnp-탐사-1/행/2.d/불변식-2.md,C:/math/.sdd/dag/pvsnp-탐사-1/행/2.d/8.d/불변식.md,C:/math/.claude/skills/do-dag/계약/공통.md,C:/math/.claude/skills/do-dag/계약/싱크.md,C:/math/.claude/skills/commit-harness/SKILL.md,C:/math/.sdd/dag/pvsnp-탐사-1/파견표.md,C:/math/.sdd/dag/pvsnp-탐사-1/이음새.md --model opus --writes 15000 --pending 180000
  시각: 2026-08-28T02:46:02Z
  대상해시: sha1:49df1a56daae
  미존재 정본: ~94,737tok (180,000바이트)
  읽기 합계: ~136,333tok / 하네스 기저: ~28,000tok / 도구 왕복: ~10,000tok / 출력 유보: ~35,000tok
  소요 견적: ~209,333tok
  판정: opus 250,000 대비 예산 안
  [/실측기]
- 산출: C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\8.d\z-결산.md
- 반환: 공통 최종 반환 계약을 따른다. 완료 첫 줄은 `DONE`이다. 공통 필드 뒤에 `결산: <절대 경로>`를 쓴다.
- 이음새: S3 노출 책임. 상태는 `미착수`에서 `노출됨`으로만 올린다. `결합됨`은 행 2.9의 책임이다.
- 이월 사슬: 지도 네 파일과 S3 증거 좌표를 행 `2.9`부터 `2.12`까지 넘긴다.
- 안전 속성·계약: 싱크는 수리하지 않는다. 문헌 상태가 하나라도 유효 PASS가 아니면 병합하지 않는다. 메인 병합은 lease와 grant 아래서만 한다. 크리덴셜 값과 외부 원문을 커밋하지 않는다.
- 크리티컬 영역: 지도 네 파일, 유효 문헌 상태 22건, 원자료 6절 5항목, 장벽 세 결과, 제한 회로·일반 회로 구별, 문헌→지도·요구→지도 추적표, 검증런 종료보고 전건, 기각 보관 검토 결과, 귀속 대조, S3 전기, 병합·커밋·회수 단계 원장.

## 임무

1. 첫 행동으로 결산 파일이 있는지 확인한다. 결산 파일이 있으면 단계 원장에 따라 다음 행위부터 잇는다.
2. 계약과 불변식 전건을 읽는다.
3. `2.8.3.z`와 그 선행 전건의 완료를 확인한다.
4. 기각 보관 파일의 항목 ID 전건이 검토전개 보고에 있는지 대조한다.
5. 귀속 대조와 완료 기준 (1)~(12)를 병합 전에 판정한다.
6. 판정이 모두 통과할 때만 싱크 계약의 노드 병합 절차를 실행한다.
7. S3를 `노출됨`으로 전기하고 지도 네 파일과 검증 증거 좌표를 적는다.
8. 마지막 편집으로 결산 단계 `종결`을 쓴다.

