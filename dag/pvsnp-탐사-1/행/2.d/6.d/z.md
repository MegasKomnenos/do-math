---
행: 2.6.z
유형: 싱크
---

# 반례 실험 도구 확보 노드 결산

- 목표: 검증된 도구 환경 명세를 저장소와 런 기준선에 병합하고 S1 노출 상태를 종결한다.
- 완료 기준: 자식 완료 신호 전건이 실재한다. 각 자식 완료 신호에서 P5′ 승인 목록 밖 설치 0건, WSL·컨테이너·새 패키지 관리자·소스 빌드 사용 0건, 크리덴셜 값·개인 식별 정보(PII) 출현 0건, 유한 스모크 결과의 복잡도 계급 주장 0건, Markdown 연구 문서·보고의 한국어 산문·LaTeX 수식 형식 통과를 확인한다. 귀속 대조와 노드 완료 기준 전건이 통과한다. 행 `2.6.10`의 수리 보고와 실물을 대조해 SAT-MINI 광고·라이브 로그·두 기준선의 상태·버전·호출 명령·스모크 결과·`candidate_status`가 일치하는지 확인한다. worktree 변경을 한 커밋으로 병합한다. S1은 도구 이름·상태 `PASS|FAIL`·버전·호출 명령·스모크 테스트·대체 수단·증거 좌표를 갖고 `노출됨`으로 전기된다. `z-결산.md`는 한국어 산문으로 작성하고 수식은 LaTeX로 표기한다. 결산은 잔여를 이월 또는 기각하고 `단계: 종결`로 끝난다.
- 작업 디렉토리: C:\Users\wogud\AppData\Local\dag-wt\pvsnp-탐사-1+2.6
- 명령: python C:\math\.claude\skills\do-dag\scripts\dag_check.py --table C:\math\.sdd\dag\pvsnp-탐사-1\파견표.md
  python C:\math\.claude\skills\do-dag\scripts\dag_marker.py
- 스킬 루트: C:\math\.claude\skills\do-dag
- 모델_프리셋: mixed
- 검증런_모델_프리셋: mixed
- 계약: C:\math\.claude\skills\do-dag\계약\공통.md, C:\math\.claude\skills\do-dag\계약\싱크.md
- 불변식: C:\math\.sdd\dag\pvsnp-탐사-1\행\0.d\불변식.md, C:\math\.sdd\dag\pvsnp-탐사-1\행\0.d\불변식-2.md, C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\불변식.md, C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\6.d\불변식.md
- 겨냥: 노드 worktree 변경 전건 · 메인 체크아웃 병합 인덱스의 배타 점유 · C:\math\.sdd\dag\pvsnp-탐사-1\이음새.md S1 · C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\6.d\z-결산.md · 노드 worktree와 브랜치의 회수
- 정본: C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\6.md, C:\math\.sdd\dag\pvsnp-탐사-1\이음새.md S1, C:\math\.claude\skills\do-dag\계약\싱크.md
- 읽기 목록: C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\6.md, C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\6-보고.md, C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\6.d\1-판정.md, C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\6.d\2-보고.md, C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\6.d\3.d\종료보고.md, C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\6.d\4-보고.md, C:\math\.sdd\dag\pvsnp-탐사-1\결정\2.6-도구기준선.md, C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\6.d\5-보고.md, C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\6.d\6-보고.md, C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\6.d\7.d\종료보고.md, C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\6.d\10-보고.md, C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\6.d\z-결산.md, C:\math\.sdd\dag\pvsnp-탐사-1\기준선.md, C:\math\.sdd\dag\pvsnp-탐사-1\이음새.md, C:\math\.sdd\dag\pvsnp-탐사-1\행\0.d\불변식.md, C:\math\.sdd\dag\pvsnp-탐사-1\행\0.d\불변식-2.md, C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\불변식.md, C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\6.d\불변식.md, C:\math\.claude\skills\do-dag\계약\공통.md, C:\math\.claude\skills\do-dag\계약\싱크.md
- 모델 배정 근거: 배정표 mixed(싱크 opus low). 단계 원장과 병합 절차가 잣대를 고정한다.
- 예산:
  [실측기 budget]
  명령: python dag_measure.py budget --files C:/math/.sdd/dag/pvsnp-탐사-1/행/0.d/불변식.md,C:/math/.sdd/dag/pvsnp-탐사-1/행/0.d/불변식-2.md,C:/math/.sdd/dag/pvsnp-탐사-1/행/2.d/불변식.md,C:/math/.sdd/dag/pvsnp-탐사-1/행/2.d/6.d/불변식.md,C:/math/.claude/skills/do-dag/계약/공통.md,C:/math/.claude/skills/do-dag/계약/싱크.md,C:/math/.sdd/dag/pvsnp-탐사-1/행/2.d/6.md,C:/math/.sdd/dag/pvsnp-탐사-1/기준선.md,C:/math/.sdd/dag/pvsnp-탐사-1/이음새.md,C:/math/.sdd/dag/pvsnp-탐사-1/행/2.d/6.d/10-보고.md --model opus --writes 15000 --pending 20000
  시각: 2026-08-25T04:48:14Z
  대상해시: sha1:285d1644f3da
  .claude\skills\do-dag\계약\공통.md: ~4,077tok
  .claude\skills\do-dag\계약\싱크.md: ~9,721tok
  .sdd\dag\pvsnp-탐사-1\기준선.md: ~13,270tok
  .sdd\dag\pvsnp-탐사-1\이음새.md: ~1,046tok
  .sdd\dag\pvsnp-탐사-1\행\0.d\불변식-2.md: ~916tok
  .sdd\dag\pvsnp-탐사-1\행\0.d\불변식.md: ~1,395tok
  .sdd\dag\pvsnp-탐사-1\행\2.d\6.d\불변식.md: ~2,881tok
  .sdd\dag\pvsnp-탐사-1\행\2.d\6.md: ~4,382tok
  .sdd\dag\pvsnp-탐사-1\행\2.d\불변식.md: ~2,875tok
  미해석: C:/math/.sdd/dag/pvsnp-탐사-1/행/2.d/6.d/10-보고.md
  미존재 정본: ~10,526tok (20,000바이트 — 측정 시점 미존재)
  읽기 합계: ~51,089tok (문자계열 단가 견적)
  하네스 기저: ~28,000tok (시스템 프롬프트·툴 스키마·스킬 목록 — 실측 상수)
  도구 왕복: ~10,000tok (셸·검색 결과, 편집 회신 — 실측 상수)
  출력 유보: ~35,000tok (하한 — 저작 예상 15,000바이트는 하한 미달)
  소요 견적: ~124,089tok
  판정: opus 200,000 대비 예산 안
  [/실측기]
- 산출: C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\6.d\z-결산.md
- 반환: 공통 최종 반환 계약을 따른다. 완료 첫 줄은 `DONE`. 공통 필드 뒤에 `결산: <절대 경로>`를 추가한다.
- 이음새: S1을 `노출됨`으로 전기한다. 행 `2.11`이 환경 기준선과 증거 좌표를 소비한다.
- 이월 사슬: S1 최종 명세, 도구별 FAIL 대체 수단, 검증런 잔여를 `2.11`과 `2.12`에 넘긴다.
- 안전 속성·계약: 귀속·완료 기준 판정 전에 병합하지 않는다. 병합 임계구역은 lease 획득부터 커밋까지다. 미귀속 편집, 미충족 기준, 충돌, 계약 이동을 숨기지 않는다.

## 임무

1. `계약/싱크.md`의 노드 싱크 절차와 단계 원장을 그대로 따른다.
2. 보고의 편집 귀속 표와 worktree diff를 대조한다.
3. 행 `2.6` 완료 기준과 자식 완료 기준 전건의 증거 실물을 연다.
4. 최종 기준선과 S1 광고의 도구별 필드가 일치하는지 검사한다.
5. S1을 `노출됨`으로 전기하고 증거 좌표를 적는다.
6. 잔여를 이월 또는 기각하고 해소 소유자를 적는다.

## 재개 상태 — 예외 처분 2026-08-25

기존 결산 `C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\6.d\z-결산.md`의 `단계: 판정완료`는 수리 전 판정이다. 행 `2.6.10`이 같은 worktree를 고친 뒤에는 기존 판정을 병합 허가로 쓰지 않는다.

1. 행 `2.6.10`의 보고와 편집 귀속을 실제 diff와 대조한다.
2. `sat-solvers.txt`를 직접 열어 SAT-MINI 상태와 SAT·UNSAT exit code를 확인한다.
3. 저장소 기준선과 런 기준선이 같은 로그 값과 `candidate_status` 정의를 쓰는지 확인한다.
4. 세 조건이 통과하면 결산의 판정표와 `상태:`를 갱신한 뒤 worktree 커밋부터 잇는다.
5. 한 조건이라도 실패하면 병합하지 않고 결산을 `상태: 완료미충족`, `단계: 판정완료`로 유지한다.
