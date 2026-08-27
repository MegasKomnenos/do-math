---
유형: 결정
종류: 게이트 2
상태: 결정됨
---

## 브리핑

게이트 2는 아래 승인 대상 스냅샷의 전개 행 7개를 실행할지 결정한다. 승인하면 도구 확보부터 부분 결과 종합까지의 작업 DAG가 열린다. 반려하면 후행 전개는 사용자 발화 축자에 따라 영향받는 미착수 행을 폐기하고 재저작한다.

### 실행 순서와 산출

| 순서 | 행 | 역할 | 다음 행이 소비하는 산출 |
|---|---|---|---|
| 1 | `2.6` | 반례 실험 도구 확보와 스모크 테스트 | 도구 상태, 버전, 대체 수단 |
| 2 | `2.7` | 문헌 22건의 공개 웹 우선 확보와 판독 | 문헌별 PASS 또는 FAIL, 인용 좌표 |
| 3 | `2.8` | 선행연구와 장벽 지도 작성 | 명제, 전제, 적용 범위, 확인 강도 |
| 4 | `2.9` | 공격 방향 포트폴리오 선정 | 채택·기각 후보와 반증 시험 |
| 5 | `2.10` | 명제와 보조정리 시도 | 입증·반증·미결·기각 기록 |
| 6 | `2.11` | 유한 반례 실험 | 재현 가능한 결과와 해석 한계 |
| 7 | `2.12` | 부분 결과 종합과 다음 국면 이월 | 전수 추적표, 잔여, 다음 공격 방향 |

행 `2.7`은 행 `2.6.z` 뒤에 선다. 두 전개가 같은 `파견표.md`와 `이음새.md`를 쓰기 때문이다. 행 `2.11`은 행 `2.10.z` 뒤에 선다. 두 전개도 같은 두 파일을 쓴다. 나머지 순차 간선은 문헌 판독 원장, 지도, 포트폴리오, 시도 기록, 실험 기록의 소비 관계를 따른다.

### 렌즈 처분

| 렌즈 | 지적 | 처분 | 현행 근거 |
|---|---|---|---|
| 운전성 | 행 `2.6`~`2.12`의 착수 경로가 설명문이었다 | 수리 | 일곱 `작업 디렉토리:` 값은 `C:\math`다. 임무 3항은 `worktree-open` 출력 경로를 자식 행에 전사한다 |
| 운전성 | 행 `2.7`의 임무 식별자 `9`가 중복됐다 | 수리 | 두 식별자를 `9a`와 `9b`로 분리했다 |
| 충족성 | 학술DB 조사 수단과 크리덴셜 비인용 검사가 완료 기준에 없었다 | 수리 | 행 `2.7` 완료 기준과 임무 21·22가 공개 웹 실패 목록, Claude `opus low`, Playwright 직접 조작, 값 비출력 검사를 요구한다 |
| 충족성 | 절대 경로, 모델 대체, 격리, 산출 형식의 전수 검사가 없었다 | 수리 | 행 `2.6`~`2.12`의 완료 기준과 보고 대응표가 자식 행 전건을 검사한다 |
| 충족성 | 내용 게이트 반려 환류와 검증런 배치의 전수 검사가 없었다 | 수리 | 행 `2.6`~`2.12`의 후행 전개와 대응표가 환류와 검증런 배치를 검사한다 |
| 충족성 | SAT 솔버 후보 집합을 빈 집합으로 통과할 수 있었다 | 수리 | 행 `2.6`은 `minisat`, `cadical`, `kissat`, `cryptominisat`을 최소 후보로 검사하고 추가 후보도 같은 표에 넣는다 |
| 정합성 | `2.6`·`2.7`과 `2.10`·`2.11`이 공통 운전 파일을 병행 편집했다 | 수리 | 파견표는 각 쌍을 `2.6.z → 2.7`, `2.10.z → 2.11`로 순차화했다 |
| 정합성 | 학술DB 표시 ID는 10개인데 기준선과 게이트 1 브리핑이 9건으로 적었다 | 수리 | 두 문서의 비축자 사실을 10건으로 고쳤다 |
| 승인 대조 | 지적 없음 | 검사 완료 | 사용자 확정 문면의 미이행, 변형, 무단 편입을 발견하지 않았다 |

모든 수리는 사용자 발화 축자, 불가침 자산, 비가역 행위, 코퍼스 밖 사실의 발명을 요구하지 않았다. 따라서 `상신 필요` 처분은 없다. 게이트 1의 미결 U1부터 U6까지는 `결정/1-프레임체급.md`에서 모두 해소됐다.

### 사용자 결정

- A — 승인 (권고): 승인 대상 스냅샷의 전개 행 7개를 현행 문면과 선행 관계로 실행한다.
- B — 반려: 바꿀 행, 요구, 순서를 지정한다. 후행 전개가 영향받는 미착수 행을 재검증하고 폐기·재저작한다.

권고는 A다. 세 FAIL 렌즈의 지적 8건은 현행 파일에서 수리됐고, 승인 대조 렌즈는 지적이 없었다. 파견표 검산은 게이트 결정이 비어 있는 현재 상태에서도 운전 구조를 검사할 수 있다.

## 신규 제약

없음. 위 수리는 게이트 1의 사용자 결정과 기존 do-dag 계약을 집행한다. 수리는 새 연구 방침을 추가하지 않는다.

## 승인 대상 스냅샷

아래 전문은 게이트 2 승인 시점의 미착수 전개 행 `2.6`부터 `2.12`까지를 파일에서 읽어 축자로 실었다.

## 행 2.6 전문

~~~~markdown
---
행: 2.6
유형: 전개
격리: worktree
base:
---

# 반례 실험 도구 확보 spike

- 목표: 승인된 반례 실험 도구를 설치·실측하고, 성공과 실패를 재현 가능한 환경 기준선으로 고정한다.
- 완료 기준: pysat·sympy·z3-solver·ortools과 SMT 솔버 z3 각각에 설치 시도·버전·스모크 테스트·`PASS|FAIL`·대체 수단이 기록된다. SAT 솔버 실행 파일은 `minisat`·`cadical`·`kissat`·`cryptominisat`을 최소 탐색 후보로 삼는다. 후보별 공식 배포 경로와 사용 가능한 로컬 패키지 관리 경로를 조사한다. 탐색 중 발견한 추가 후보도 같은 판정표에 넣고, 확보 가능한 후보를 설치 대상으로 삼는다. FAIL도 완결이다. 형식 증명 도구는 설치하지 않는다. 명령 출력과 환경 기준선 문서의 대응표가 도구 증거다. `6-보고.md`는 자식 행 전건의 절대 경로·모델 대체·Playwright 예외·Codex worktree 격리·산문 형식·내용 게이트 환류·검증런 배치를 닫힌 대응표로 판정한다.
- 작업 디렉토리: C:\math
- 명령: python C:\math\.claude\skills\do-dag\scripts\dag_check.py --table C:\math\.sdd\dag\pvsnp-탐사-1\파견표.md
  python C:\math\.claude\skills\do-dag\scripts\dag_marker.py
- 스킬 루트: C:\math\.claude\skills\do-dag
- 모델_프리셋: mixed
- 검증런_모델_프리셋: mixed
- 계약: C:\math\.claude\skills\do-dag\계약\공통.md, C:\math\.claude\skills\do-dag\references\분해_원리.md, C:\math\.claude\skills\do-dag\references\검증_체제.md, C:\math\.claude\skills\do-dag\references\서식.md, C:\math\.claude\skills\do-dag\references\배정.md
- 불변식: C:\math\.sdd\dag\pvsnp-탐사-1\행\0.d\불변식.md, C:\math\.sdd\dag\pvsnp-탐사-1\행\0.d\불변식-2.md, C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\불변식.md
- 겨냥: 저장소 상대 경로 `research/pvsnp/environment/toolchain-baseline.md`, `experiments/pvsnp/smoke/` 아래 코드·테스트 전건 · 런 디렉토리 절대 경로 `C:\math\.sdd\dag\pvsnp-탐사-1\기준선.md`의 런타임 도구 절 · 런 디렉토리 절대 경로 C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\6.d\ 아래 행 파일·불변식 파일 전건, 파견표 행 추가, 이음새 S행, 6-보고.md
- 정본: C:\math\.sdd\dag\pvsnp-탐사-1\결정\2-작업DAG.md, C:\math\.sdd\dag\pvsnp-탐사-1\결정\1-프레임체급.md P5′
- 읽기 목록: C:\math\.sdd\dag\pvsnp-탐사-1\행\0.d\불변식.md, C:\math\.sdd\dag\pvsnp-탐사-1\행\0.d\불변식-2.md, C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\불변식.md, C:\math\.sdd\dag\pvsnp-탐사-1\결정\2-작업DAG.md, C:\math\.sdd\dag\pvsnp-탐사-1\결정\1-프레임체급.md, C:\math\.sdd\dag\pvsnp-탐사-1\기준선.md, C:\math\research\p-vs-np-statement-and-prior-work.md, C:\math\.claude\skills\do-dag\계약\공통.md, C:\math\.claude\skills\do-dag\references\분해_원리.md, C:\math\.claude\skills\do-dag\references\검증_체제.md, C:\math\.claude\skills\do-dag\references\서식.md, C:\math\.claude\skills\do-dag\references\배정.md
- 모델 배정 근거: 배정표 mixed(전개 fable med)에 불변식 6항 (1)의 fable→gpt-5.6-sol 같은 노력 대체를 적용해 gpt-5.6-sol med. 저장소 파일을 쓰므로 격리 worktree로 불변식 6항 (3)을 충족한다.
- 예산:
  [실측기 budget]
  명령: python dag_measure.py budget --files C:/math/.sdd/dag/pvsnp-탐사-1/행/0.d/불변식.md,C:/math/.sdd/dag/pvsnp-탐사-1/행/0.d/불변식-2.md,C:/math/.sdd/dag/pvsnp-탐사-1/행/2.d/불변식.md,C:/math/.sdd/dag/pvsnp-탐사-1/결정/1-프레임체급.md,C:/math/.sdd/dag/pvsnp-탐사-1/기준선.md,C:/math/.claude/skills/do-dag/계약/공통.md,C:/math/.claude/skills/do-dag/references/분해_원리.md,C:/math/.claude/skills/do-dag/references/검증_체제.md,C:/math/.claude/skills/do-dag/references/서식.md,C:/math/.claude/skills/do-dag/references/배정.md,C:/math/research/p-vs-np-statement-and-prior-work.md --model gpt-5.6-sol --writes 50000 --pending 20000
  시각: 2026-08-24T16:05:05Z
  대상해시: sha1:2cf1b3d842bf
  읽기 합계: ~94,966tok (미존재 정본 20,000바이트 포함) / 하네스 기저: ~28,000tok / 도구 왕복: ~10,000tok / 출력 유보: ~47,500tok
  소요 견적: ~180,466tok
  판정: gpt-5.6-sol 200,000 대비 예산 안
  [/실측기]
- 산출: C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\6-보고.md
- 반환: 공통 최종 반환 계약을 따른다. 완료 첫 줄은 DONE. 둘째 줄 보고: <절대 경로>. 그 외 추가 필드 없음.
- 이음새: S1 도구 환경 명세의 노출 책임. 반례 실험 노드가 버전·호출 표면·FAIL 대체 수단을 소비한다.
- 이월 사슬: 도구별 상태·버전·호출 명령·스모크 테스트·FAIL 대체 수단 — `2.11`과 `2.12`가 소비한다.
- 안전 속성·계약: 불변식 3항(크리덴셜 비인용) · 불변식 5항(학술 기준과 해결 주장 장벽 검증) · 행 2 불변식 P1(유한 실험의 해석 한계).

## 임무

1. C:\math\.sdd\dag\pvsnp-탐사-1\결정\2-작업DAG.md 「결정」 절 축자를 읽는다. 그 축자에 비추어 자기 범위의 기존 행을 재검증하고, 맞지 않는 행을 폐기·재저작한다.
2. 첫 행동으로 불변식 슬롯의 파일 전건을 읽는다.
3. `C:\math`에서 `base:`를 정하고 `worktree-open`을 실행한다. 명령이 출력한 worktree 절대 경로를 자식 파견문의 `작업 디렉토리:` 슬롯에 쓴다. 원자료는 기존 절대 경로로 읽는다.
4. 새 행 파일을 쓰기 전에 C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\6.d\불변식.md를 쓴다.
5. 이 노드는 spike다. 미확인 사실은 각 Python 패키지의 설치 가능성, SAT 솔버 실행 파일의 확보 가능성, z3 실행 파일과 Python 바인딩의 동작 여부다. 각 사실에 최소 스모크 테스트와 갱신 트리거를 둔다.
6. 설치는 사용자 승인 P5′의 닫힌 범위 안에서만 한다. Lean 4·Coq/Rocq·Isabelle/HOL은 설치하지 않는다.
7. 설치 실패는 FAIL 기록과 대체 수단으로 완결한다. 성공으로 바꾸기 위한 무단 환경 우회는 하지 않는다.
9. 자식 작업 단위의 쓰기 집합을 닫고 모든 단위 쌍의 쓰기 교집합·소비 간선·배타 점유를 판정한다. 같은 worktree는 순차 사유가 아니다.
10. 충족성 렌즈를 자기 층의 첫 자식으로 둔다. 렌즈의 선행은 2.6이고, 나머지 자식과 싱크는 렌즈를 선행으로 받는다.
11. 지식자산을 새로 쓰거나 첨삭하는 작업자마다 바로 뒤에 {경량} 검증런을 둔다. 검증런을 뺀 파견 행이 3개 이상이면 싱크 바로 앞에도 {경량} 검증런을 둔다.
12. 자기 싱크 2.6.z를 둔다. 실행 싱크는 계약/싱크.md, 완료 신호 z-결산.md, 모델 opus low를 쓴다.
13. 자식 파견문마다 목표·내용 완료 기준·닫힌 겨냥·정본·이음새·이월 사슬·크리티컬 영역을 쓴다.
14. 자식 파견문마다 받은 명령 두 줄, 스킬 루트, 두 모델 프리셋을 축자로 전사한다. 역할 계약은 서식.md 「계약 자산」 경로로 싣는다.
15. 자식 파견문마다 반환 공통 첫 줄과 역할 계약의 확장 필드를 쓴다. 확장 필드가 없으면 추가 필드 없음을 명시한다.
16. 자식 파견문마다 적용 불변식 전건을 불변식·읽기 목록·예산 --files에 같은 절대 경로로 싣는다.
17. mixed 배정에 불변식 6항의 fable 대체 집행 규칙 넷을 적용한다. playwright 학술DB 행은 subagent_type claude 예외를 지킨다.
18. 행 파일을 먼저 쓰고 파견표에 등재한다. 작성 중에는 --mode partial --writer 2.6으로 검사한다.
19. 이 전사 의무와 충족성 렌즈·검증런·학술DB·크리덴셜·불변식 승계 의무를 자식 전개의 전개 지시에 다시 싣는다.
20. 전체 검산 exit 0 뒤 전개 완료보고를 쓴다. 보고에는 등재 행, 서브트리 싱크, 검산, 병행 자격 판정을 넣는다.
21. SAT 솔버 판정표에 `minisat`·`cadical`·`kissat`·`cryptominisat`과 탐색 중 발견한 추가 후보를 전건 넣는다. 각 후보에 공식 배포 경로, 사용 가능한 로컬 패키지 관리 경로, 확보 가능성, 설치 시도, 버전, 스모크 테스트, `PASS|FAIL`, 대체 수단을 기록한다. 확보 가능 판정을 받은 후보는 설치 대상으로 삼는다.
22. `6-보고.md`에 자식 행 전건의 요구→자식 완료 기준 대응표를 쓴다. 표는 런 디렉토리 입력의 절대 경로, fable의 같은 노력 `gpt-5.6-sol` 대체, Playwright 조사의 Claude 계열 `opus low` 예외, 저장소를 쓰는 Codex 행의 worktree 격리를 검사한다.
23. 대응표는 Markdown 연구 문서와 Markdown 보고의 한국어 산문·LaTeX 수식 형식을 검사한다. 소스 코드·원시 로그·데이터 파일·외부 원문은 산문 형식 검사에서 제외한다.
24. 내용 게이트마다 반려 결정을 소비하는 후행 전개를 둔다. 후행 전개는 같은 산출 계열의 미착수 행 전건을 재검토하고 필요한 행을 폐기·재저작한다. 대응표는 게이트→후행 전개→동일 산출 계열 미착수 행 전건의 결선을 검사한다.
25. 대응표는 지식자산 작업자 전건과 바로 뒤 `{경량}` 검증런을 일대일로 대조한다. 검증런을 뺀 파견 행이 3개 이상이면 싱크 바로 앞 `{경량}` 검증런도 검사한다.
~~~~

## 행 2.7 전문

~~~~markdown
---
행: 2.7
유형: 전개
격리: worktree
base:
---

# 문헌 22건 확보·판독 spike

- 목표: 원자료가 지목한 외부 문헌 22건의 실제 접근성과 내용을 확인하고, 인용 가능한 문헌별 판독 기록을 만든다.
- 완료 기준: 22건 전부가 서지 정보·접근 경로·원문 확보 상태·읽은 범위·핵심 주장·한정·인용 좌표·`PASS|FAIL`을 갖는다. 공개 웹을 먼저 시도하고 공개 웹 실패 목록의 문헌만 학술DB 조사 행이 소비한다. 학술DB 조사 행은 Claude 계열 `opus low`이고 Playwright로 브라우저를 직접 조작한다. `C:\math\.credentials\kudos.md`의 값은 출력하지 않는다. 파견문·보고·저장소 산출·커밋 예정 변경 전수 검사는 값의 출현 건수만 기록하고 0건을 PASS로 판정한다. 구독 문헌 원본은 git에 들이지 않는다. 첫 조사 기록은 내용 게이트를 통과한다. URL·문헌 좌표·접근 로그·판독 기록의 22행 대응표가 조사 증거다. `7-보고.md`는 자식 행 전건의 절대 경로·모델 대체·Playwright 예외·Codex worktree 격리·산문 형식·내용 게이트 환류·검증런 배치를 닫힌 대응표로 판정한다.
- 작업 디렉토리: C:\math
- 명령: python C:\math\.claude\skills\do-dag\scripts\dag_check.py --table C:\math\.sdd\dag\pvsnp-탐사-1\파견표.md
  python C:\math\.claude\skills\do-dag\scripts\dag_marker.py
- 스킬 루트: C:\math\.claude\skills\do-dag
- 모델_프리셋: mixed
- 검증런_모델_프리셋: mixed
- 계약: C:\math\.claude\skills\do-dag\계약\공통.md, C:\math\.claude\skills\do-dag\references\분해_원리.md, C:\math\.claude\skills\do-dag\references\검증_체제.md, C:\math\.claude\skills\do-dag\references\서식.md, C:\math\.claude\skills\do-dag\references\배정.md
- 불변식: C:\math\.sdd\dag\pvsnp-탐사-1\행\0.d\불변식.md, C:\math\.sdd\dag\pvsnp-탐사-1\행\0.d\불변식-2.md, C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\불변식.md
- 겨냥: 저장소 상대 경로 `research/pvsnp/literature/` 아래 문헌별 기록과 출처 원장 전건 · 저장소 밖 문헌 원본 보관 좌표는 산출에 경로만 기록 · 학술DB 계정의 배타 점유 · 런 디렉토리 절대 경로 C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\7.d\ 아래 행 파일·불변식 파일 전건, 파견표 행 추가, 이음새 S행, 7-보고.md
- 정본: C:\math\.sdd\dag\pvsnp-탐사-1\결정\2-작업DAG.md, C:\math\.sdd\dag\pvsnp-탐사-1\기준선.md 2.2·2.3절, C:\math\research\p-vs-np-statement-and-prior-work.md
- 읽기 목록: C:\math\.sdd\dag\pvsnp-탐사-1\행\0.d\불변식.md, C:\math\.sdd\dag\pvsnp-탐사-1\행\0.d\불변식-2.md, C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\불변식.md, C:\math\.sdd\dag\pvsnp-탐사-1\결정\2-작업DAG.md, C:\math\.sdd\dag\pvsnp-탐사-1\결정\1-프레임체급.md, C:\math\.sdd\dag\pvsnp-탐사-1\기준선.md, C:\math\research\p-vs-np-statement-and-prior-work.md, C:\math\.claude\skills\do-dag\계약\공통.md, C:\math\.claude\skills\do-dag\references\분해_원리.md, C:\math\.claude\skills\do-dag\references\검증_체제.md, C:\math\.claude\skills\do-dag\references\서식.md, C:\math\.claude\skills\do-dag\references\배정.md
- 모델 배정 근거: 배정표 mixed(전개 fable med)에 불변식 6항 (1)의 fable→gpt-5.6-sol 같은 노력 대체를 적용해 gpt-5.6-sol med. 저장소 파일을 쓰므로 격리 worktree로 불변식 6항 (3)을 충족한다.
- 예산:
  [실측기 budget]
  명령: python dag_measure.py budget --files C:/math/.sdd/dag/pvsnp-탐사-1/행/0.d/불변식.md,C:/math/.sdd/dag/pvsnp-탐사-1/행/0.d/불변식-2.md,C:/math/.sdd/dag/pvsnp-탐사-1/행/2.d/불변식.md,C:/math/.sdd/dag/pvsnp-탐사-1/결정/1-프레임체급.md,C:/math/.sdd/dag/pvsnp-탐사-1/기준선.md,C:/math/.claude/skills/do-dag/계약/공통.md,C:/math/.claude/skills/do-dag/references/분해_원리.md,C:/math/.claude/skills/do-dag/references/검증_체제.md,C:/math/.claude/skills/do-dag/references/서식.md,C:/math/.claude/skills/do-dag/references/배정.md,C:/math/research/p-vs-np-statement-and-prior-work.md --model gpt-5.6-sol --writes 50000 --pending 20000
  시각: 2026-08-24T16:05:05Z
  대상해시: sha1:2cf1b3d842bf
  읽기 합계: ~94,966tok (미존재 정본 20,000바이트 포함) / 하네스 기저: ~28,000tok / 도구 왕복: ~10,000tok / 출력 유보: ~47,500tok
  소요 견적: ~180,466tok
  판정: gpt-5.6-sol 200,000 대비 예산 안
  [/실측기]
- 산출: C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\7-보고.md
- 반환: 공통 최종 반환 계약을 따른다. 완료 첫 줄은 DONE. 둘째 줄 보고: <절대 경로>. 그 외 추가 필드 없음.
- 이음새: S2 문헌 판독 원장의 노출 책임. 선행연구 지도 노드가 22건의 상태·주장·한정·인용 좌표를 소비한다.
- 이월 사슬: 22건 문헌별 판독 기록과 확보 FAIL 목록 — `2.8`이 전건 소비한다.
- 안전 속성·계약: 불변식 3항(크리덴셜 비인용) · 불변식 5항(학술 기준과 해결 주장 장벽 검증) · 행 2 불변식 P1(유한 실험의 해석 한계).

## 임무

1. C:\math\.sdd\dag\pvsnp-탐사-1\결정\2-작업DAG.md 「결정」 절 축자를 읽는다. 그 축자에 비추어 자기 범위의 기존 행을 재검증하고, 맞지 않는 행을 폐기·재저작한다.
2. 첫 행동으로 불변식 슬롯의 파일 전건을 읽는다.
3. `C:\math`에서 `base:`를 정하고 `worktree-open`을 실행한다. 명령이 출력한 worktree 절대 경로를 자식 파견문의 `작업 디렉토리:` 슬롯에 쓴다. 원자료는 기존 절대 경로로 읽는다.
4. 새 행 파일을 쓰기 전에 C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\7.d\불변식.md를 쓴다.
5. 이 노드는 spike다. 미확인 사실은 22개 URL의 현재 접근성, 학술DB가 실제로 필요한 문헌 범위, 로그인과 원문 연결의 작동 여부다. PASS와 FAIL을 접근 증거로 판정한다.
6. 공개 웹 조사 행을 먼저 둔다. 공개 웹 실패 목록을 소비하는 학술DB 조사 행을 그 뒤에 둔다.
7. playwright 학술DB 행은 subagent_type을 claude로 지정한다. 모델은 opus low로 새로 도출한다. 이 행만 C:\math\.credentials\kudos.md를 싣고 ID·PW 값은 인용하지 않는다.
8. 첫 문헌 판독 기록 1건의 완료를 선행으로 받는 내용 게이트를 둔다. 승인 뒤 남은 문헌 기록을 작성한다.
9a. 원문 확보 실패도 접근 시도·실패 증거·대체 공개본 탐색 결과가 있으면 FAIL로 완결한다.
9b. 자식 작업 단위의 쓰기 집합을 닫고 모든 단위 쌍의 쓰기 교집합·소비 간선·배타 점유를 판정한다. 같은 worktree는 순차 사유가 아니다.
10. 충족성 렌즈를 자기 층의 첫 자식으로 둔다. 렌즈의 선행은 2.7이고, 나머지 자식과 싱크는 렌즈를 선행으로 받는다.
11. 지식자산을 새로 쓰거나 첨삭하는 작업자마다 바로 뒤에 {경량} 검증런을 둔다. 검증런을 뺀 파견 행이 3개 이상이면 싱크 바로 앞에도 {경량} 검증런을 둔다.
12. 자기 싱크 2.7.z를 둔다. 실행 싱크는 계약/싱크.md, 완료 신호 z-결산.md, 모델 opus low를 쓴다.
13. 자식 파견문마다 목표·내용 완료 기준·닫힌 겨냥·정본·이음새·이월 사슬·크리티컬 영역을 쓴다.
14. 자식 파견문마다 받은 명령 두 줄, 스킬 루트, 두 모델 프리셋을 축자로 전사한다. 역할 계약은 서식.md 「계약 자산」 경로로 싣는다.
15. 자식 파견문마다 반환 공통 첫 줄과 역할 계약의 확장 필드를 쓴다. 확장 필드가 없으면 추가 필드 없음을 명시한다.
16. 자식 파견문마다 적용 불변식 전건을 불변식·읽기 목록·예산 --files에 같은 절대 경로로 싣는다.
17. mixed 배정에 불변식 6항의 fable 대체 집행 규칙 넷을 적용한다. playwright 학술DB 행은 subagent_type claude 예외를 지킨다.
18. 행 파일을 먼저 쓰고 파견표에 등재한다. 작성 중에는 --mode partial --writer 2.7으로 검사한다.
19. 이 전사 의무와 충족성 렌즈·검증런·학술DB·크리덴셜·불변식 승계 의무를 자식 전개의 전개 지시에 다시 싣는다.
20. 전체 검산 exit 0 뒤 전개 완료보고를 쓴다. 보고에는 등재 행, 서브트리 싱크, 검산, 병행 자격 판정을 넣는다.
21. 학술DB 조사 행은 공개 웹 실패 목록만 입력으로 받는다. 학술DB 조사 행의 모델은 Claude 계열 `opus low`로 닫고, Playwright 브라우저 직접 조작을 완료 기준과 실행 증거에 둔다.
22. 비밀 검사는 `C:\math\.credentials\kudos.md`의 값을 출력하지 않는다. 비밀 검사는 파견문·보고·저장소 산출·커밋 예정 변경에서 값의 출현 건수만 기록하며, 대상 전건의 0건을 PASS로 판정한다.
23. `7-보고.md`에 자식 행 전건의 요구→자식 완료 기준 대응표를 쓴다. 표는 런 디렉토리 입력의 절대 경로, fable의 같은 노력 `gpt-5.6-sol` 대체, Playwright 조사의 Claude 계열 `opus low` 예외, 저장소를 쓰는 Codex 행의 worktree 격리를 검사한다.
24. 대응표는 Markdown 연구 문서와 Markdown 보고의 한국어 산문·LaTeX 수식 형식을 검사한다. 소스 코드·원시 로그·데이터 파일·외부 원문은 산문 형식 검사에서 제외한다.
25. 내용 게이트마다 반려 결정을 소비하는 후행 전개를 둔다. 후행 전개는 같은 산출 계열의 미착수 행 전건을 재검토하고 필요한 행을 폐기·재저작한다. 대응표는 게이트→후행 전개→동일 산출 계열 미착수 행 전건의 결선을 검사한다.
26. 대응표는 지식자산 작업자 전건과 바로 뒤 `{경량}` 검증런을 일대일로 대조한다. 검증런을 뺀 파견 행이 3개 이상이면 싱크 바로 앞 `{경량}` 검증런도 검사한다.
~~~~

## 행 2.8 전문

~~~~markdown
---
행: 2.8
유형: 전개
격리: worktree
base:
---

# 선행연구 지도와 장벽 지도

- 목표: 판독이 끝난 문헌 22건을 같은 정의 체계로 결합해 공격 방향을 고를 수 있는 선행연구 지도와 장벽 지도를 만든다.
- 완료 기준: 문헌 22건 전부가 확보·판독 PASS여야 한다. 지도는 원자료 6절의 5항목, 알려진 부분·조건부 결과, relativization·natural proofs·algebrization의 가정과 적용 범위, 제한 회로와 일반 회로의 차이를 전건 추적한다. 각 지도 항목은 문헌별 인용 좌표와 확인 강도를 갖는다. 첫 지도 산출은 내용 게이트를 통과한다. 한 문헌이라도 FAIL이면 부분 지도를 보존하되 이 노드는 DONE으로 닫지 않는다. 22건 상태표, 문헌→지도와 요구→지도 추적표, 검증런 종료보고가 지도 증거다. `8-보고.md`는 자식 행 전건의 절대 경로·모델 대체·Playwright 예외·Codex worktree 격리·산문 형식·내용 게이트 환류·검증런 배치를 닫힌 대응표로 판정한다.
- 작업 디렉토리: C:\math
- 명령: python C:\math\.claude\skills\do-dag\scripts\dag_check.py --table C:\math\.sdd\dag\pvsnp-탐사-1\파견표.md
  python C:\math\.claude\skills\do-dag\scripts\dag_marker.py
- 스킬 루트: C:\math\.claude\skills\do-dag
- 모델_프리셋: mixed
- 검증런_모델_프리셋: mixed
- 계약: C:\math\.claude\skills\do-dag\계약\공통.md, C:\math\.claude\skills\do-dag\references\분해_원리.md, C:\math\.claude\skills\do-dag\references\검증_체제.md, C:\math\.claude\skills\do-dag\references\서식.md, C:\math\.claude\skills\do-dag\references\배정.md
- 불변식: C:\math\.sdd\dag\pvsnp-탐사-1\행\0.d\불변식.md, C:\math\.sdd\dag\pvsnp-탐사-1\행\0.d\불변식-2.md, C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\불변식.md
- 겨냥: 저장소 상대 경로 `research/pvsnp/maps/definitions.md`, `research/pvsnp/maps/prior-work.md`, `research/pvsnp/maps/barriers.md`, `research/pvsnp/maps/claim-source-matrix.md` · 런 디렉토리 절대 경로 C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\8.d\ 아래 행 파일·불변식 파일 전건, 파견표 행 추가, 이음새 S행, 8-보고.md
- 정본: C:\math\.sdd\dag\pvsnp-탐사-1\결정\2-작업DAG.md, `research/pvsnp/literature/` 아래 22건 판독 기록, C:\math\research\p-vs-np-statement-and-prior-work.md
- 읽기 목록: C:\math\.sdd\dag\pvsnp-탐사-1\행\0.d\불변식.md, C:\math\.sdd\dag\pvsnp-탐사-1\행\0.d\불변식-2.md, C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\불변식.md, C:\math\.sdd\dag\pvsnp-탐사-1\결정\2-작업DAG.md, C:\math\.sdd\dag\pvsnp-탐사-1\결정\1-프레임체급.md, C:\math\.sdd\dag\pvsnp-탐사-1\기준선.md, C:\math\research\p-vs-np-statement-and-prior-work.md, C:\math\.claude\skills\do-dag\계약\공통.md, C:\math\.claude\skills\do-dag\references\분해_원리.md, C:\math\.claude\skills\do-dag\references\검증_체제.md, C:\math\.claude\skills\do-dag\references\서식.md, C:\math\.claude\skills\do-dag\references\배정.md
- 모델 배정 근거: 배정표 mixed(전개 fable med)에 불변식 6항 (1)의 fable→gpt-5.6-sol 같은 노력 대체를 적용해 gpt-5.6-sol med. 저장소 파일을 쓰므로 격리 worktree로 불변식 6항 (3)을 충족한다.
- 예산:
  [실측기 budget]
  명령: python dag_measure.py budget --files C:/math/.sdd/dag/pvsnp-탐사-1/행/0.d/불변식.md,C:/math/.sdd/dag/pvsnp-탐사-1/행/0.d/불변식-2.md,C:/math/.sdd/dag/pvsnp-탐사-1/행/2.d/불변식.md,C:/math/.sdd/dag/pvsnp-탐사-1/결정/1-프레임체급.md,C:/math/.sdd/dag/pvsnp-탐사-1/기준선.md,C:/math/.claude/skills/do-dag/계약/공통.md,C:/math/.claude/skills/do-dag/references/분해_원리.md,C:/math/.claude/skills/do-dag/references/검증_체제.md,C:/math/.claude/skills/do-dag/references/서식.md,C:/math/.claude/skills/do-dag/references/배정.md,C:/math/research/p-vs-np-statement-and-prior-work.md --model gpt-5.6-sol --writes 50000 --pending 20000
  시각: 2026-08-24T16:05:05Z
  대상해시: sha1:2cf1b3d842bf
  읽기 합계: ~94,966tok (미존재 정본 20,000바이트 포함) / 하네스 기저: ~28,000tok / 도구 왕복: ~10,000tok / 출력 유보: ~47,500tok
  소요 견적: ~180,466tok
  판정: gpt-5.6-sol 200,000 대비 예산 안
  [/실측기]
- 산출: C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\8-보고.md
- 반환: 공통 최종 반환 계약을 따른다. 완료 첫 줄은 DONE. 둘째 줄 보고: <절대 경로>. 그 외 추가 필드 없음.
- 이음새: S3 선행연구·장벽 지도의 노출 책임. 공격 방향 선정 노드가 명제, 장벽 조건, 미확인 표지를 소비한다.
- 이월 사슬: 정의·부분 결과·장벽·출처 대응표 전건 — `2.9`부터 `2.12`까지 소비한다.
- 안전 속성·계약: 불변식 3항(크리덴셜 비인용) · 불변식 5항(학술 기준과 해결 주장 장벽 검증) · 행 2 불변식 P1(유한 실험의 해석 한계).

## 임무

1. C:\math\.sdd\dag\pvsnp-탐사-1\결정\2-작업DAG.md 「결정」 절 축자를 읽는다. 그 축자에 비추어 자기 범위의 기존 행을 재검증하고, 맞지 않는 행을 폐기·재저작한다.
2. 첫 행동으로 불변식 슬롯의 파일 전건을 읽는다.
3. `C:\math`에서 `base:`를 정하고 `worktree-open`을 실행한다. 명령이 출력한 worktree 절대 경로를 자식 파견문의 `작업 디렉토리:` 슬롯에 쓴다. 원자료는 기존 절대 경로로 읽는다.
4. 새 행 파일을 쓰기 전에 C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\8.d\불변식.md를 쓴다.
5. 22건 판독 기록의 FAIL도 입력으로 받는다. FAIL이 하나라도 있으면 미확인 범위와 영향을 기록하고, 프레임 A의 차단 조건으로 판정한다. 후행 공격 방향 노드를 열지 않는다.
6. 원자료 6절의 닫힌 5항목을 각각 별도 완료 기준에 연결한다.
7. 첫 지도 파일 1건의 완료를 선행으로 받는 내용 게이트를 둔다. 반려하면 지도 계열 전건을 재검토한다.
8. 장벽 결과를 P≠NP의 증거로 쓰지 않는다. 조건부 결과의 전제와 결론을 분리한다.
9. 자식 작업 단위의 쓰기 집합을 닫고 모든 단위 쌍의 쓰기 교집합·소비 간선·배타 점유를 판정한다. 같은 worktree는 순차 사유가 아니다.
10. 충족성 렌즈를 자기 층의 첫 자식으로 둔다. 렌즈의 선행은 2.8이고, 나머지 자식과 싱크는 렌즈를 선행으로 받는다.
11. 지식자산을 새로 쓰거나 첨삭하는 작업자마다 바로 뒤에 {경량} 검증런을 둔다. 검증런을 뺀 파견 행이 3개 이상이면 싱크 바로 앞에도 {경량} 검증런을 둔다.
12. 자기 싱크 2.8.z를 둔다. 실행 싱크는 계약/싱크.md, 완료 신호 z-결산.md, 모델 opus low를 쓴다.
13. 자식 파견문마다 목표·내용 완료 기준·닫힌 겨냥·정본·이음새·이월 사슬·크리티컬 영역을 쓴다.
14. 자식 파견문마다 받은 명령 두 줄, 스킬 루트, 두 모델 프리셋을 축자로 전사한다. 역할 계약은 서식.md 「계약 자산」 경로로 싣는다.
15. 자식 파견문마다 반환 공통 첫 줄과 역할 계약의 확장 필드를 쓴다. 확장 필드가 없으면 추가 필드 없음을 명시한다.
16. 자식 파견문마다 적용 불변식 전건을 불변식·읽기 목록·예산 --files에 같은 절대 경로로 싣는다.
17. mixed 배정에 불변식 6항의 fable 대체 집행 규칙 넷을 적용한다. playwright 학술DB 행은 subagent_type claude 예외를 지킨다.
18. 행 파일을 먼저 쓰고 파견표에 등재한다. 작성 중에는 --mode partial --writer 2.8으로 검사한다.
19. 이 전사 의무와 충족성 렌즈·검증런·학술DB·크리덴셜·불변식 승계 의무를 자식 전개의 전개 지시에 다시 싣는다.
20. 전체 검산 exit 0 뒤 전개 완료보고를 쓴다. 보고에는 등재 행, 서브트리 싱크, 검산, 병행 자격 판정을 넣는다.
21. `8-보고.md`에 자식 행 전건의 요구→자식 완료 기준 대응표를 쓴다. 표는 런 디렉토리 입력의 절대 경로, fable의 같은 노력 `gpt-5.6-sol` 대체, Playwright 조사의 Claude 계열 `opus low` 예외, 저장소를 쓰는 Codex 행의 worktree 격리를 검사한다.
22. 대응표는 Markdown 연구 문서와 Markdown 보고의 한국어 산문·LaTeX 수식 형식을 검사한다. 소스 코드·원시 로그·데이터 파일·외부 원문은 산문 형식 검사에서 제외한다.
23. 내용 게이트마다 반려 결정을 소비하는 후행 전개를 둔다. 후행 전개는 같은 산출 계열의 미착수 행 전건을 재검토하고 필요한 행을 폐기·재저작한다. 대응표는 게이트→후행 전개→동일 산출 계열 미착수 행 전건의 결선을 검사한다.
24. 대응표는 지식자산 작업자 전건과 바로 뒤 `{경량}` 검증런을 일대일로 대조한다. 검증런을 뺀 파견 행이 3개 이상이면 싱크 바로 앞 `{경량}` 검증런도 검사한다.
~~~~

## 행 2.9 전문

~~~~markdown
---
행: 2.9
유형: 전개
격리: worktree
base:
---

# 공격 방향 후보 평가와 포트폴리오 확정

- 목표: 완성된 선행연구 지도에서 이 국면이 학술적으로 시험할 수 있는 공격 방향을 도출하고, 시도 포트폴리오를 근거와 함께 닫는다.
- 완료 기준: 후보마다 목표 명제·필요 전제·알려진 결과와의 차분·장벽 접촉·반증 시험·필요 도구·예상 산출을 기록한다. 채택과 기각 후보가 모두 근거를 갖는다. 해결 가능성이나 독창성은 완료 조건이 아니다. 첫 포트폴리오 산출은 내용 게이트를 통과한다. 후보 판정표와 검증런 종료보고가 포트폴리오 증거다. `9-보고.md`는 자식 행 전건의 절대 경로·모델 대체·Playwright 예외·Codex worktree 격리·산문 형식·내용 게이트 환류·검증런 배치를 닫힌 대응표로 판정한다.
- 작업 디렉토리: C:\math
- 명령: python C:\math\.claude\skills\do-dag\scripts\dag_check.py --table C:\math\.sdd\dag\pvsnp-탐사-1\파견표.md
  python C:\math\.claude\skills\do-dag\scripts\dag_marker.py
- 스킬 루트: C:\math\.claude\skills\do-dag
- 모델_프리셋: mixed
- 검증런_모델_프리셋: mixed
- 계약: C:\math\.claude\skills\do-dag\계약\공통.md, C:\math\.claude\skills\do-dag\references\분해_원리.md, C:\math\.claude\skills\do-dag\references\검증_체제.md, C:\math\.claude\skills\do-dag\references\서식.md, C:\math\.claude\skills\do-dag\references\배정.md
- 불변식: C:\math\.sdd\dag\pvsnp-탐사-1\행\0.d\불변식.md, C:\math\.sdd\dag\pvsnp-탐사-1\행\0.d\불변식-2.md, C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\불변식.md
- 겨냥: 저장소 상대 경로 `research/pvsnp/attack-portfolio.md`, `research/pvsnp/rejections/direction-screening.md` · 런 디렉토리 절대 경로 C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\9.d\ 아래 행 파일·불변식 파일 전건, 파견표 행 추가, 이음새 S행, 9-보고.md
- 정본: C:\math\.sdd\dag\pvsnp-탐사-1\결정\2-작업DAG.md, `research/pvsnp/maps/` 아래 지도 전건
- 읽기 목록: C:\math\.sdd\dag\pvsnp-탐사-1\행\0.d\불변식.md, C:\math\.sdd\dag\pvsnp-탐사-1\행\0.d\불변식-2.md, C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\불변식.md, C:\math\.sdd\dag\pvsnp-탐사-1\결정\2-작업DAG.md, C:\math\.sdd\dag\pvsnp-탐사-1\결정\1-프레임체급.md, C:\math\.sdd\dag\pvsnp-탐사-1\기준선.md, C:\math\research\p-vs-np-statement-and-prior-work.md, C:\math\.claude\skills\do-dag\계약\공통.md, C:\math\.claude\skills\do-dag\references\분해_원리.md, C:\math\.claude\skills\do-dag\references\검증_체제.md, C:\math\.claude\skills\do-dag\references\서식.md, C:\math\.claude\skills\do-dag\references\배정.md
- 모델 배정 근거: 배정표 mixed(전개 fable med)에 불변식 6항 (1)의 fable→gpt-5.6-sol 같은 노력 대체를 적용해 gpt-5.6-sol med. 저장소 파일을 쓰므로 격리 worktree로 불변식 6항 (3)을 충족한다.
- 예산:
  [실측기 budget]
  명령: python dag_measure.py budget --files C:/math/.sdd/dag/pvsnp-탐사-1/행/0.d/불변식.md,C:/math/.sdd/dag/pvsnp-탐사-1/행/0.d/불변식-2.md,C:/math/.sdd/dag/pvsnp-탐사-1/행/2.d/불변식.md,C:/math/.sdd/dag/pvsnp-탐사-1/결정/1-프레임체급.md,C:/math/.sdd/dag/pvsnp-탐사-1/기준선.md,C:/math/.claude/skills/do-dag/계약/공통.md,C:/math/.claude/skills/do-dag/references/분해_원리.md,C:/math/.claude/skills/do-dag/references/검증_체제.md,C:/math/.claude/skills/do-dag/references/서식.md,C:/math/.claude/skills/do-dag/references/배정.md,C:/math/research/p-vs-np-statement-and-prior-work.md --model gpt-5.6-sol --writes 50000 --pending 20000
  시각: 2026-08-24T16:05:05Z
  대상해시: sha1:2cf1b3d842bf
  읽기 합계: ~94,966tok (미존재 정본 20,000바이트 포함) / 하네스 기저: ~28,000tok / 도구 왕복: ~10,000tok / 출력 유보: ~47,500tok
  소요 견적: ~180,466tok
  판정: gpt-5.6-sol 200,000 대비 예산 안
  [/실측기]
- 산출: C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\9-보고.md
- 반환: 공통 최종 반환 계약을 따른다. 완료 첫 줄은 DONE. 둘째 줄 보고: <절대 경로>. 그 외 추가 필드 없음.
- 이음새: S4 공격 포트폴리오의 노출 책임. 보조정리 시도와 반례 실험 노드가 후보 ID·명제·반증 시험을 소비한다.
- 이월 사슬: 채택 후보 ID, 목표 명제, 전제, 장벽 접촉, 반증 시험 — `2.10`과 `2.11`이 소비한다.
- 안전 속성·계약: 불변식 3항(크리덴셜 비인용) · 불변식 5항(학술 기준과 해결 주장 장벽 검증) · 행 2 불변식 P1(유한 실험의 해석 한계).

## 임무

1. C:\math\.sdd\dag\pvsnp-탐사-1\결정\2-작업DAG.md 「결정」 절 축자를 읽는다. 그 축자에 비추어 자기 범위의 기존 행을 재검증하고, 맞지 않는 행을 폐기·재저작한다.
2. 첫 행동으로 불변식 슬롯의 파일 전건을 읽는다.
3. `C:\math`에서 `base:`를 정하고 `worktree-open`을 실행한다. 명령이 출력한 worktree 절대 경로를 자식 파견문의 `작업 디렉토리:` 슬롯에 쓴다. 원자료는 기존 절대 경로로 읽는다.
4. 새 행 파일을 쓰기 전에 C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\9.d\불변식.md를 쓴다.
5. 문헌 지도에 없는 수학적 사실을 후보 근거로 발명하지 않는다.
6. 후보마다 relativization·natural proofs·algebrization의 해당 여부를 판정한다. 해당하지 않음을 주장하면 근거를 남긴다.
7. 첫 포트폴리오 문서의 완료를 선행으로 받는 내용 게이트를 둔다.
8. 채택 후보가 0건이어도 근거 있는 기각 원장과 다음 국면 재평가 조건이 있으면 완결이다.
9. 자식 작업 단위의 쓰기 집합을 닫고 모든 단위 쌍의 쓰기 교집합·소비 간선·배타 점유를 판정한다. 같은 worktree는 순차 사유가 아니다.
10. 충족성 렌즈를 자기 층의 첫 자식으로 둔다. 렌즈의 선행은 2.9이고, 나머지 자식과 싱크는 렌즈를 선행으로 받는다.
11. 지식자산을 새로 쓰거나 첨삭하는 작업자마다 바로 뒤에 {경량} 검증런을 둔다. 검증런을 뺀 파견 행이 3개 이상이면 싱크 바로 앞에도 {경량} 검증런을 둔다.
12. 자기 싱크 2.9.z를 둔다. 실행 싱크는 계약/싱크.md, 완료 신호 z-결산.md, 모델 opus low를 쓴다.
13. 자식 파견문마다 목표·내용 완료 기준·닫힌 겨냥·정본·이음새·이월 사슬·크리티컬 영역을 쓴다.
14. 자식 파견문마다 받은 명령 두 줄, 스킬 루트, 두 모델 프리셋을 축자로 전사한다. 역할 계약은 서식.md 「계약 자산」 경로로 싣는다.
15. 자식 파견문마다 반환 공통 첫 줄과 역할 계약의 확장 필드를 쓴다. 확장 필드가 없으면 추가 필드 없음을 명시한다.
16. 자식 파견문마다 적용 불변식 전건을 불변식·읽기 목록·예산 --files에 같은 절대 경로로 싣는다.
17. mixed 배정에 불변식 6항의 fable 대체 집행 규칙 넷을 적용한다. playwright 학술DB 행은 subagent_type claude 예외를 지킨다.
18. 행 파일을 먼저 쓰고 파견표에 등재한다. 작성 중에는 --mode partial --writer 2.9으로 검사한다.
19. 이 전사 의무와 충족성 렌즈·검증런·학술DB·크리덴셜·불변식 승계 의무를 자식 전개의 전개 지시에 다시 싣는다.
20. 전체 검산 exit 0 뒤 전개 완료보고를 쓴다. 보고에는 등재 행, 서브트리 싱크, 검산, 병행 자격 판정을 넣는다.
21. `9-보고.md`에 자식 행 전건의 요구→자식 완료 기준 대응표를 쓴다. 표는 런 디렉토리 입력의 절대 경로, fable의 같은 노력 `gpt-5.6-sol` 대체, Playwright 조사의 Claude 계열 `opus low` 예외, 저장소를 쓰는 Codex 행의 worktree 격리를 검사한다.
22. 대응표는 Markdown 연구 문서와 Markdown 보고의 한국어 산문·LaTeX 수식 형식을 검사한다. 소스 코드·원시 로그·데이터 파일·외부 원문은 산문 형식 검사에서 제외한다.
23. 내용 게이트마다 반려 결정을 소비하는 후행 전개를 둔다. 후행 전개는 같은 산출 계열의 미착수 행 전건을 재검토하고 필요한 행을 폐기·재저작한다. 대응표는 게이트→후행 전개→동일 산출 계열 미착수 행 전건의 결선을 검사한다.
24. 대응표는 지식자산 작업자 전건과 바로 뒤 `{경량}` 검증런을 일대일로 대조한다. 검증런을 뺀 파견 행이 3개 이상이면 싱크 바로 앞 `{경량}` 검증런도 검사한다.
~~~~

## 행 2.10 전문

~~~~markdown
---
행: 2.10
유형: 전개
격리: worktree
base:
---

# 명제·보조정리 시도와 기각 기록

- 목표: 확정된 공격 포트폴리오의 명제를 작은 보조정리로 분해해 증명·반증을 시도하고, 검증된 부분 결과와 기각을 누적한다.
- 완료 기준: 각 시도는 명제 축자, 정의, 전제, 논증 단계, 의존 문헌, 반증 시도, 판정 `입증|반증|미결|기각`, 판정 근거를 갖는다. 기각도 완결이다. 해결 주장은 세 장벽 회피를 포함한 적대 검증을 통과하기 전에는 해결로 쓰지 않는다. 명제·보조정리 계열의 첫 산출과 기각 기록 계열의 첫 산출은 각각 내용 게이트를 통과한다. 문서별 검증런 종료보고와 주장→근거 대응표가 시도 증거다. `10-보고.md`는 자식 행 전건의 절대 경로·모델 대체·Playwright 예외·Codex worktree 격리·산문 형식·내용 게이트 환류·검증런 배치를 닫힌 대응표로 판정한다.
- 작업 디렉토리: C:\math
- 명령: python C:\math\.claude\skills\do-dag\scripts\dag_check.py --table C:\math\.sdd\dag\pvsnp-탐사-1\파견표.md
  python C:\math\.claude\skills\do-dag\scripts\dag_marker.py
- 스킬 루트: C:\math\.claude\skills\do-dag
- 모델_프리셋: mixed
- 검증런_모델_프리셋: mixed
- 계약: C:\math\.claude\skills\do-dag\계약\공통.md, C:\math\.claude\skills\do-dag\references\분해_원리.md, C:\math\.claude\skills\do-dag\references\검증_체제.md, C:\math\.claude\skills\do-dag\references\서식.md, C:\math\.claude\skills\do-dag\references\배정.md
- 불변식: C:\math\.sdd\dag\pvsnp-탐사-1\행\0.d\불변식.md, C:\math\.sdd\dag\pvsnp-탐사-1\행\0.d\불변식-2.md, C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\불변식.md
- 겨냥: 저장소 상대 경로 `research/pvsnp/attempts/` 아래 전건, `research/pvsnp/lemmas/` 아래 전건, `research/pvsnp/rejections/attempt-*.md` · 런 디렉토리 절대 경로 C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\10.d\ 아래 행 파일·불변식 파일 전건, 파견표 행 추가, 이음새 S행, 10-보고.md
- 정본: C:\math\.sdd\dag\pvsnp-탐사-1\결정\2-작업DAG.md, `research/pvsnp/attack-portfolio.md`, `research/pvsnp/maps/` 아래 지도 전건
- 읽기 목록: C:\math\.sdd\dag\pvsnp-탐사-1\행\0.d\불변식.md, C:\math\.sdd\dag\pvsnp-탐사-1\행\0.d\불변식-2.md, C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\불변식.md, C:\math\.sdd\dag\pvsnp-탐사-1\결정\2-작업DAG.md, C:\math\.sdd\dag\pvsnp-탐사-1\결정\1-프레임체급.md, C:\math\.sdd\dag\pvsnp-탐사-1\기준선.md, C:\math\research\p-vs-np-statement-and-prior-work.md, C:\math\.claude\skills\do-dag\계약\공통.md, C:\math\.claude\skills\do-dag\references\분해_원리.md, C:\math\.claude\skills\do-dag\references\검증_체제.md, C:\math\.claude\skills\do-dag\references\서식.md, C:\math\.claude\skills\do-dag\references\배정.md
- 모델 배정 근거: 배정표 mixed(전개 fable med)에 불변식 6항 (1)의 fable→gpt-5.6-sol 같은 노력 대체를 적용해 gpt-5.6-sol med. 저장소 파일을 쓰므로 격리 worktree로 불변식 6항 (3)을 충족한다.
- 예산:
  [실측기 budget]
  명령: python dag_measure.py budget --files C:/math/.sdd/dag/pvsnp-탐사-1/행/0.d/불변식.md,C:/math/.sdd/dag/pvsnp-탐사-1/행/0.d/불변식-2.md,C:/math/.sdd/dag/pvsnp-탐사-1/행/2.d/불변식.md,C:/math/.sdd/dag/pvsnp-탐사-1/결정/1-프레임체급.md,C:/math/.sdd/dag/pvsnp-탐사-1/기준선.md,C:/math/.claude/skills/do-dag/계약/공통.md,C:/math/.claude/skills/do-dag/references/분해_원리.md,C:/math/.claude/skills/do-dag/references/검증_체제.md,C:/math/.claude/skills/do-dag/references/서식.md,C:/math/.claude/skills/do-dag/references/배정.md,C:/math/research/p-vs-np-statement-and-prior-work.md --model gpt-5.6-sol --writes 50000 --pending 20000
  시각: 2026-08-24T16:05:05Z
  대상해시: sha1:2cf1b3d842bf
  읽기 합계: ~94,966tok (미존재 정본 20,000바이트 포함) / 하네스 기저: ~28,000tok / 도구 왕복: ~10,000tok / 출력 유보: ~47,500tok
  소요 견적: ~180,466tok
  판정: gpt-5.6-sol 200,000 대비 예산 안
  [/실측기]
- 산출: C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\10-보고.md
- 반환: 공통 최종 반환 계약을 따른다. 완료 첫 줄은 DONE. 둘째 줄 보고: <절대 경로>. 그 외 추가 필드 없음.
- 이음새: S5 보조정리·기각 기록의 노출 책임. 종합 노드가 명제 ID·판정·근거·잔여를 소비한다.
- 이월 사슬: 명제·보조정리별 판정, 근거, 미결, 기각 사유 — `2.12`가 소비한다.
- 안전 속성·계약: 불변식 3항(크리덴셜 비인용) · 불변식 5항(학술 기준과 해결 주장 장벽 검증) · 행 2 불변식 P1(유한 실험의 해석 한계).

## 임무

1. C:\math\.sdd\dag\pvsnp-탐사-1\결정\2-작업DAG.md 「결정」 절 축자를 읽는다. 그 축자에 비추어 자기 범위의 기존 행을 재검증하고, 맞지 않는 행을 폐기·재저작한다.
2. 첫 행동으로 불변식 슬롯의 파일 전건을 읽는다.
3. `C:\math`에서 `base:`를 정하고 `worktree-open`을 실행한다. 명령이 출력한 worktree 절대 경로를 자식 파견문의 `작업 디렉토리:` 슬롯에 쓴다. 원자료는 기존 절대 경로로 읽는다.
4. 새 행 파일을 쓰기 전에 C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\10.d\불변식.md를 쓴다.
5. 포트폴리오 후보를 독립된 시도 단위로 나눈다. 각 단위는 자기 파일 경계와 반증 시험을 갖는다.
6. 명제·보조정리 문서의 첫 산출 1건 뒤에 내용 게이트를 둔다. 첫 기각 기록이 생기면 그 첫 기록 뒤에 별도 내용 게이트를 둔다.
7. 해결 또는 무조건 분리를 주장하는 산출에는 세 장벽 회피 여부를 별도 적대 검증런으로 검사한다.
8. 논증의 빈칸을 직관이나 계산 표본으로 메우지 않는다. 미결은 미결로 남긴다.
9. 자식 작업 단위의 쓰기 집합을 닫고 모든 단위 쌍의 쓰기 교집합·소비 간선·배타 점유를 판정한다. 같은 worktree는 순차 사유가 아니다.
10. 충족성 렌즈를 자기 층의 첫 자식으로 둔다. 렌즈의 선행은 2.10이고, 나머지 자식과 싱크는 렌즈를 선행으로 받는다.
11. 지식자산을 새로 쓰거나 첨삭하는 작업자마다 바로 뒤에 {경량} 검증런을 둔다. 검증런을 뺀 파견 행이 3개 이상이면 싱크 바로 앞에도 {경량} 검증런을 둔다.
12. 자기 싱크 2.10.z를 둔다. 실행 싱크는 계약/싱크.md, 완료 신호 z-결산.md, 모델 opus low를 쓴다.
13. 자식 파견문마다 목표·내용 완료 기준·닫힌 겨냥·정본·이음새·이월 사슬·크리티컬 영역을 쓴다.
14. 자식 파견문마다 받은 명령 두 줄, 스킬 루트, 두 모델 프리셋을 축자로 전사한다. 역할 계약은 서식.md 「계약 자산」 경로로 싣는다.
15. 자식 파견문마다 반환 공통 첫 줄과 역할 계약의 확장 필드를 쓴다. 확장 필드가 없으면 추가 필드 없음을 명시한다.
16. 자식 파견문마다 적용 불변식 전건을 불변식·읽기 목록·예산 --files에 같은 절대 경로로 싣는다.
17. mixed 배정에 불변식 6항의 fable 대체 집행 규칙 넷을 적용한다. playwright 학술DB 행은 subagent_type claude 예외를 지킨다.
18. 행 파일을 먼저 쓰고 파견표에 등재한다. 작성 중에는 --mode partial --writer 2.10으로 검사한다.
19. 이 전사 의무와 충족성 렌즈·검증런·학술DB·크리덴셜·불변식 승계 의무를 자식 전개의 전개 지시에 다시 싣는다.
20. 전체 검산 exit 0 뒤 전개 완료보고를 쓴다. 보고에는 등재 행, 서브트리 싱크, 검산, 병행 자격 판정을 넣는다.
21. `10-보고.md`에 자식 행 전건의 요구→자식 완료 기준 대응표를 쓴다. 표는 런 디렉토리 입력의 절대 경로, fable의 같은 노력 `gpt-5.6-sol` 대체, Playwright 조사의 Claude 계열 `opus low` 예외, 저장소를 쓰는 Codex 행의 worktree 격리를 검사한다.
22. 대응표는 Markdown 연구 문서와 Markdown 보고의 한국어 산문·LaTeX 수식 형식을 검사한다. 소스 코드·원시 로그·데이터 파일·외부 원문은 산문 형식 검사에서 제외한다.
23. 내용 게이트마다 반려 결정을 소비하는 후행 전개를 둔다. 후행 전개는 같은 산출 계열의 미착수 행 전건을 재검토하고 필요한 행을 폐기·재저작한다. 대응표는 게이트→후행 전개→동일 산출 계열 미착수 행 전건의 결선을 검사한다.
24. 대응표는 지식자산 작업자 전건과 바로 뒤 `{경량}` 검증런을 일대일로 대조한다. 검증런을 뺀 파견 행이 3개 이상이면 싱크 바로 앞 `{경량}` 검증런도 검사한다.
~~~~

## 행 2.11 전문

~~~~markdown
---
행: 2.11
유형: 전개
격리: worktree
base:
---

# 유한 반례 실험과 계산 기록

- 목표: 공격 포트폴리오의 반증 가능한 유한 귀결을 계산 실험으로 시험하고, 재현 가능한 반례·무발견 기록을 누적한다.
- 완료 기준: 각 실험은 가설, 유한 입력 영역, 생성 절차, seed, 도구 버전, 제한 시간, 기대 관찰, 실제 결과, 재현 명령, 판정 범위를 갖는다. 결과는 유한 실험으로만 해석한다. 첫 실험 기록은 내용 게이트를 통과한다. 도구 FAIL이면 승인된 대체 수단을 쓰거나 실험 FAIL로 닫는다. 코드·테스트·원시 결과 해시·실험 보고와 검증런 종료보고가 실험 증거다. `11-보고.md`는 자식 행 전건의 절대 경로·모델 대체·Playwright 예외·Codex worktree 격리·산문 형식·내용 게이트 환류·검증런 배치를 닫힌 대응표로 판정한다.
- 작업 디렉토리: C:\math
- 명령: python C:\math\.claude\skills\do-dag\scripts\dag_check.py --table C:\math\.sdd\dag\pvsnp-탐사-1\파견표.md
  python C:\math\.claude\skills\do-dag\scripts\dag_marker.py
- 스킬 루트: C:\math\.claude\skills\do-dag
- 모델_프리셋: mixed
- 검증런_모델_프리셋: mixed
- 계약: C:\math\.claude\skills\do-dag\계약\공통.md, C:\math\.claude\skills\do-dag\references\분해_원리.md, C:\math\.claude\skills\do-dag\references\검증_체제.md, C:\math\.claude\skills\do-dag\references\서식.md, C:\math\.claude\skills\do-dag\references\배정.md
- 불변식: C:\math\.sdd\dag\pvsnp-탐사-1\행\0.d\불변식.md, C:\math\.sdd\dag\pvsnp-탐사-1\행\0.d\불변식-2.md, C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\불변식.md
- 겨냥: 저장소 상대 경로 `experiments/pvsnp/` 아래 코드·테스트·소형 재현 자료 전건, `research/pvsnp/experiments/` 아래 실험 기록 전건 · 런 디렉토리 절대 경로 C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\11.d\ 아래 행 파일·불변식 파일 전건, 파견표 행 추가, 이음새 S행, 11-보고.md
- 정본: C:\math\.sdd\dag\pvsnp-탐사-1\결정\2-작업DAG.md, `research/pvsnp/attack-portfolio.md`, `research/pvsnp/environment/toolchain-baseline.md`
- 읽기 목록: C:\math\.sdd\dag\pvsnp-탐사-1\행\0.d\불변식.md, C:\math\.sdd\dag\pvsnp-탐사-1\행\0.d\불변식-2.md, C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\불변식.md, C:\math\.sdd\dag\pvsnp-탐사-1\결정\2-작업DAG.md, C:\math\.sdd\dag\pvsnp-탐사-1\결정\1-프레임체급.md, C:\math\.sdd\dag\pvsnp-탐사-1\기준선.md, C:\math\research\p-vs-np-statement-and-prior-work.md, C:\math\.claude\skills\do-dag\계약\공통.md, C:\math\.claude\skills\do-dag\references\분해_원리.md, C:\math\.claude\skills\do-dag\references\검증_체제.md, C:\math\.claude\skills\do-dag\references\서식.md, C:\math\.claude\skills\do-dag\references\배정.md
- 모델 배정 근거: 배정표 mixed(전개 fable med)에 불변식 6항 (1)의 fable→gpt-5.6-sol 같은 노력 대체를 적용해 gpt-5.6-sol med. 저장소 파일을 쓰므로 격리 worktree로 불변식 6항 (3)을 충족한다.
- 예산:
  [실측기 budget]
  명령: python dag_measure.py budget --files C:/math/.sdd/dag/pvsnp-탐사-1/행/0.d/불변식.md,C:/math/.sdd/dag/pvsnp-탐사-1/행/0.d/불변식-2.md,C:/math/.sdd/dag/pvsnp-탐사-1/행/2.d/불변식.md,C:/math/.sdd/dag/pvsnp-탐사-1/결정/1-프레임체급.md,C:/math/.sdd/dag/pvsnp-탐사-1/기준선.md,C:/math/.claude/skills/do-dag/계약/공통.md,C:/math/.claude/skills/do-dag/references/분해_원리.md,C:/math/.claude/skills/do-dag/references/검증_체제.md,C:/math/.claude/skills/do-dag/references/서식.md,C:/math/.claude/skills/do-dag/references/배정.md,C:/math/research/p-vs-np-statement-and-prior-work.md --model gpt-5.6-sol --writes 50000 --pending 20000
  시각: 2026-08-24T16:05:05Z
  대상해시: sha1:2cf1b3d842bf
  읽기 합계: ~94,966tok (미존재 정본 20,000바이트 포함) / 하네스 기저: ~28,000tok / 도구 왕복: ~10,000tok / 출력 유보: ~47,500tok
  소요 견적: ~180,466tok
  판정: gpt-5.6-sol 200,000 대비 예산 안
  [/실측기]
- 산출: C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\11-보고.md
- 반환: 공통 최종 반환 계약을 따른다. 완료 첫 줄은 DONE. 둘째 줄 보고: <절대 경로>. 그 외 추가 필드 없음.
- 이음새: S1 도구 환경의 연결 책임과 S6 실험 기록의 노출 책임. 종합 노드가 실험 ID·범위·결과·해석 한계를 소비한다.
- 이월 사슬: 실험별 입력 범위·재현 명령·결과·한계·반례 또는 무발견 — `2.12`가 소비한다.
- 안전 속성·계약: 불변식 3항(크리덴셜 비인용) · 불변식 5항(학술 기준과 해결 주장 장벽 검증) · 행 2 불변식 P1(유한 실험의 해석 한계).

## 임무

1. C:\math\.sdd\dag\pvsnp-탐사-1\결정\2-작업DAG.md 「결정」 절 축자를 읽는다. 그 축자에 비추어 자기 범위의 기존 행을 재검증하고, 맞지 않는 행을 폐기·재저작한다.
2. 첫 행동으로 불변식 슬롯의 파일 전건을 읽는다.
3. `C:\math`에서 `base:`를 정하고 `worktree-open`을 실행한다. 명령이 출력한 worktree 절대 경로를 자식 파견문의 `작업 디렉토리:` 슬롯에 쓴다. 원자료는 기존 절대 경로로 읽는다.
4. 새 행 파일을 쓰기 전에 C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\11.d\불변식.md를 쓴다.
5. 실험 규모는 기준선 D4에 따라 각 작업자가 정하고 근거를 기록한다.
6. 첫 실험 코드와 기록 1건의 완료를 선행으로 받는 내용 게이트를 둔다. 반려하면 실험 기록 계열 전건을 재검토한다.
7. 방어 제거 시 RED가 되는 테스트, 실패 경로 주입, 결정적 seed 재실행을 크리티컬 영역에 넣는다.
8. 유한 입력 결과를 최악 경우 다항시간 알고리즘의 존재·부재로 확대하지 않는다.
9. 자식 작업 단위의 쓰기 집합을 닫고 모든 단위 쌍의 쓰기 교집합·소비 간선·배타 점유를 판정한다. 같은 worktree는 순차 사유가 아니다.
10. 충족성 렌즈를 자기 층의 첫 자식으로 둔다. 렌즈의 선행은 2.11이고, 나머지 자식과 싱크는 렌즈를 선행으로 받는다.
11. 지식자산을 새로 쓰거나 첨삭하는 작업자마다 바로 뒤에 {경량} 검증런을 둔다. 검증런을 뺀 파견 행이 3개 이상이면 싱크 바로 앞에도 {경량} 검증런을 둔다.
12. 자기 싱크 2.11.z를 둔다. 실행 싱크는 계약/싱크.md, 완료 신호 z-결산.md, 모델 opus low를 쓴다.
13. 자식 파견문마다 목표·내용 완료 기준·닫힌 겨냥·정본·이음새·이월 사슬·크리티컬 영역을 쓴다.
14. 자식 파견문마다 받은 명령 두 줄, 스킬 루트, 두 모델 프리셋을 축자로 전사한다. 역할 계약은 서식.md 「계약 자산」 경로로 싣는다.
15. 자식 파견문마다 반환 공통 첫 줄과 역할 계약의 확장 필드를 쓴다. 확장 필드가 없으면 추가 필드 없음을 명시한다.
16. 자식 파견문마다 적용 불변식 전건을 불변식·읽기 목록·예산 --files에 같은 절대 경로로 싣는다.
17. mixed 배정에 불변식 6항의 fable 대체 집행 규칙 넷을 적용한다. playwright 학술DB 행은 subagent_type claude 예외를 지킨다.
18. 행 파일을 먼저 쓰고 파견표에 등재한다. 작성 중에는 --mode partial --writer 2.11으로 검사한다.
19. 이 전사 의무와 충족성 렌즈·검증런·학술DB·크리덴셜·불변식 승계 의무를 자식 전개의 전개 지시에 다시 싣는다.
20. 전체 검산 exit 0 뒤 전개 완료보고를 쓴다. 보고에는 등재 행, 서브트리 싱크, 검산, 병행 자격 판정을 넣는다.
21. `11-보고.md`에 자식 행 전건의 요구→자식 완료 기준 대응표를 쓴다. 표는 런 디렉토리 입력의 절대 경로, fable의 같은 노력 `gpt-5.6-sol` 대체, Playwright 조사의 Claude 계열 `opus low` 예외, 저장소를 쓰는 Codex 행의 worktree 격리를 검사한다.
22. 대응표는 Markdown 연구 문서와 Markdown 보고의 한국어 산문·LaTeX 수식 형식을 검사한다. 소스 코드·원시 로그·데이터 파일·외부 원문은 산문 형식 검사에서 제외한다.
23. 내용 게이트마다 반려 결정을 소비하는 후행 전개를 둔다. 후행 전개는 같은 산출 계열의 미착수 행 전건을 재검토하고 필요한 행을 폐기·재저작한다. 대응표는 게이트→후행 전개→동일 산출 계열 미착수 행 전건의 결선을 검사한다.
24. 대응표는 지식자산 작업자 전건과 바로 뒤 `{경량}` 검증런을 일대일로 대조한다. 검증런을 뺀 파견 행이 3개 이상이면 싱크 바로 앞 `{경량}` 검증런도 검사한다.
~~~~

## 행 2.12 전문

~~~~markdown
---
행: 2.12
유형: 전개
격리: worktree
base:
---

# 부분 결과 종합과 다음 탐사 이월

- 목표: 보조정리 시도와 반례 실험을 하나의 판정 원장으로 종합해 이 국면의 검증된 진전·기각·미결과 다음 탐사 좌표를 확정한다.
- 완료 기준: 종합은 모든 시도·실험 ID를 누락 없이 추적하고, 각 항목을 `검증된 부분 결과|반증|기각|미결`로 분류한다. 주장 강도는 근거 강도를 넘지 않는다. 해결 여부를 완료 조건으로 쓰지 않는다. 새 공격 방향은 다음 국면으로 이월한다. 첫 종합 산출은 내용 게이트를 통과한다. 전수 추적표, 검증런 종료보고, 노드 결산이 종합 증거다. `12-보고.md`는 자식 행 전건의 절대 경로·모델 대체·Playwright 예외·Codex worktree 격리·산문 형식·내용 게이트 환류·검증런 배치를 닫힌 대응표로 판정한다.
- 작업 디렉토리: C:\math
- 명령: python C:\math\.claude\skills\do-dag\scripts\dag_check.py --table C:\math\.sdd\dag\pvsnp-탐사-1\파견표.md
  python C:\math\.claude\skills\do-dag\scripts\dag_marker.py
- 스킬 루트: C:\math\.claude\skills\do-dag
- 모델_프리셋: mixed
- 검증런_모델_프리셋: mixed
- 계약: C:\math\.claude\skills\do-dag\계약\공통.md, C:\math\.claude\skills\do-dag\references\분해_원리.md, C:\math\.claude\skills\do-dag\references\검증_체제.md, C:\math\.claude\skills\do-dag\references\서식.md, C:\math\.claude\skills\do-dag\references\배정.md
- 불변식: C:\math\.sdd\dag\pvsnp-탐사-1\행\0.d\불변식.md, C:\math\.sdd\dag\pvsnp-탐사-1\행\0.d\불변식-2.md, C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\불변식.md
- 겨냥: 저장소 상대 경로 `research/pvsnp/synthesis/phase-1.md`, `research/pvsnp/rejections/index.md`, `research/pvsnp/next-directions.md` · 런 디렉토리 절대 경로 C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\12.d\ 아래 행 파일·불변식 파일 전건, 파견표 행 추가, 이음새 S행, 12-보고.md
- 정본: C:\math\.sdd\dag\pvsnp-탐사-1\결정\2-작업DAG.md, `research/pvsnp/attempts/`, `research/pvsnp/lemmas/`, `research/pvsnp/rejections/`, `research/pvsnp/experiments/`, `experiments/pvsnp/` 아래 전건
- 읽기 목록: C:\math\.sdd\dag\pvsnp-탐사-1\행\0.d\불변식.md, C:\math\.sdd\dag\pvsnp-탐사-1\행\0.d\불변식-2.md, C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\불변식.md, C:\math\.sdd\dag\pvsnp-탐사-1\결정\2-작업DAG.md, C:\math\.sdd\dag\pvsnp-탐사-1\결정\1-프레임체급.md, C:\math\.sdd\dag\pvsnp-탐사-1\기준선.md, C:\math\research\p-vs-np-statement-and-prior-work.md, C:\math\.claude\skills\do-dag\계약\공통.md, C:\math\.claude\skills\do-dag\references\분해_원리.md, C:\math\.claude\skills\do-dag\references\검증_체제.md, C:\math\.claude\skills\do-dag\references\서식.md, C:\math\.claude\skills\do-dag\references\배정.md
- 모델 배정 근거: 배정표 mixed(전개 fable med)에 불변식 6항 (1)의 fable→gpt-5.6-sol 같은 노력 대체를 적용해 gpt-5.6-sol med. 저장소 파일을 쓰므로 격리 worktree로 불변식 6항 (3)을 충족한다.
- 예산:
  [실측기 budget]
  명령: python dag_measure.py budget --files C:/math/.sdd/dag/pvsnp-탐사-1/행/0.d/불변식.md,C:/math/.sdd/dag/pvsnp-탐사-1/행/0.d/불변식-2.md,C:/math/.sdd/dag/pvsnp-탐사-1/행/2.d/불변식.md,C:/math/.sdd/dag/pvsnp-탐사-1/결정/1-프레임체급.md,C:/math/.sdd/dag/pvsnp-탐사-1/기준선.md,C:/math/.claude/skills/do-dag/계약/공통.md,C:/math/.claude/skills/do-dag/references/분해_원리.md,C:/math/.claude/skills/do-dag/references/검증_체제.md,C:/math/.claude/skills/do-dag/references/서식.md,C:/math/.claude/skills/do-dag/references/배정.md,C:/math/research/p-vs-np-statement-and-prior-work.md --model gpt-5.6-sol --writes 50000 --pending 20000
  시각: 2026-08-24T16:05:05Z
  대상해시: sha1:2cf1b3d842bf
  읽기 합계: ~94,966tok (미존재 정본 20,000바이트 포함) / 하네스 기저: ~28,000tok / 도구 왕복: ~10,000tok / 출력 유보: ~47,500tok
  소요 견적: ~180,466tok
  판정: gpt-5.6-sol 200,000 대비 예산 안
  [/실측기]
- 산출: C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\12-보고.md
- 반환: 공통 최종 반환 계약을 따른다. 완료 첫 줄은 DONE. 둘째 줄 보고: <절대 경로>. 그 외 추가 필드 없음.
- 이음새: S5·S6 연결 책임과 S7 국면 종합 노출 책임. 행 3과 국면 종결 싱크가 종합 판정과 잔여를 소비한다.
- 이월 사슬: 게이트 2 결정 파일 좌표, 노드 싱크 결산 전건, 종합 판정, 다음 공격 방향 — 행 3과 행 z가 소비한다.
- 안전 속성·계약: 불변식 3항(크리덴셜 비인용) · 불변식 5항(학술 기준과 해결 주장 장벽 검증) · 행 2 불변식 P1(유한 실험의 해석 한계).

## 임무

1. C:\math\.sdd\dag\pvsnp-탐사-1\결정\2-작업DAG.md 「결정」 절 축자를 읽는다. 그 축자에 비추어 자기 범위의 기존 행을 재검증하고, 맞지 않는 행을 폐기·재저작한다.
2. 첫 행동으로 불변식 슬롯의 파일 전건을 읽는다.
3. `C:\math`에서 `base:`를 정하고 `worktree-open`을 실행한다. 명령이 출력한 worktree 절대 경로를 자식 파견문의 `작업 디렉토리:` 슬롯에 쓴다. 원자료는 기존 절대 경로로 읽는다.
4. 새 행 파일을 쓰기 전에 C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\12.d\불변식.md를 쓴다.
5. 보조정리 시도와 실험의 ID 전건을 실물에서 다시 세고 종합 추적표에 연결한다.
6. 첫 종합 문서의 완료를 선행으로 받는 내용 게이트를 둔다.
7. 해결·반증 주장이 있으면 세 장벽 회피 적대 검증의 PASS 없이는 검증된 부분 결과로 분류하지 않는다.
8. 새 공격 방향은 이 국면에서 실행하지 않는다. 다음 국면 입력으로 남긴다.
9. 자식 작업 단위의 쓰기 집합을 닫고 모든 단위 쌍의 쓰기 교집합·소비 간선·배타 점유를 판정한다. 같은 worktree는 순차 사유가 아니다.
10. 충족성 렌즈를 자기 층의 첫 자식으로 둔다. 렌즈의 선행은 2.12이고, 나머지 자식과 싱크는 렌즈를 선행으로 받는다.
11. 지식자산을 새로 쓰거나 첨삭하는 작업자마다 바로 뒤에 {경량} 검증런을 둔다. 검증런을 뺀 파견 행이 3개 이상이면 싱크 바로 앞에도 {경량} 검증런을 둔다.
12. 자기 싱크 2.12.z를 둔다. 실행 싱크는 계약/싱크.md, 완료 신호 z-결산.md, 모델 opus low를 쓴다.
13. 자식 파견문마다 목표·내용 완료 기준·닫힌 겨냥·정본·이음새·이월 사슬·크리티컬 영역을 쓴다.
14. 자식 파견문마다 받은 명령 두 줄, 스킬 루트, 두 모델 프리셋을 축자로 전사한다. 역할 계약은 서식.md 「계약 자산」 경로로 싣는다.
15. 자식 파견문마다 반환 공통 첫 줄과 역할 계약의 확장 필드를 쓴다. 확장 필드가 없으면 추가 필드 없음을 명시한다.
16. 자식 파견문마다 적용 불변식 전건을 불변식·읽기 목록·예산 --files에 같은 절대 경로로 싣는다.
17. mixed 배정에 불변식 6항의 fable 대체 집행 규칙 넷을 적용한다. playwright 학술DB 행은 subagent_type claude 예외를 지킨다.
18. 행 파일을 먼저 쓰고 파견표에 등재한다. 작성 중에는 --mode partial --writer 2.12으로 검사한다.
19. 이 전사 의무와 충족성 렌즈·검증런·학술DB·크리덴셜·불변식 승계 의무를 자식 전개의 전개 지시에 다시 싣는다.
20. 전체 검산 exit 0 뒤 전개 완료보고를 쓴다. 보고에는 등재 행, 서브트리 싱크, 검산, 병행 자격 판정을 넣는다.
21. `12-보고.md`에 자식 행 전건의 요구→자식 완료 기준 대응표를 쓴다. 표는 런 디렉토리 입력의 절대 경로, fable의 같은 노력 `gpt-5.6-sol` 대체, Playwright 조사의 Claude 계열 `opus low` 예외, 저장소를 쓰는 Codex 행의 worktree 격리를 검사한다.
22. 대응표는 Markdown 연구 문서와 Markdown 보고의 한국어 산문·LaTeX 수식 형식을 검사한다. 소스 코드·원시 로그·데이터 파일·외부 원문은 산문 형식 검사에서 제외한다.
23. 내용 게이트마다 반려 결정을 소비하는 후행 전개를 둔다. 후행 전개는 같은 산출 계열의 미착수 행 전건을 재검토하고 필요한 행을 폐기·재저작한다. 대응표는 게이트→후행 전개→동일 산출 계열 미착수 행 전건의 결선을 검사한다.
24. 대응표는 지식자산 작업자 전건과 바로 뒤 `{경량}` 검증런을 일대일로 대조한다. 검증런을 뺀 파견 행이 3개 이상이면 싱크 바로 앞 `{경량}` 검증런도 검사한다.
~~~~

## 결정 (메인 기입 — 사용자 발화 축자)

메인이 브리핑을 올린 뒤의 사용자 발화:

> 승인. 다만 오케 재개를 하진 말고, 다음 신규 세션에서 새로 오케를 재개해 진행할 수 있도록 정리 및 마무리를 수행해

## 메인 결정 (사용자 축자 아님)

결정의 해석과 이관 절차다. 「결정」 절과 충돌하면 「결정」 절이 이긴다.

1. **승인 범위**: 브리핑 「사용자 결정」의 선택지 A — 승인 대상 스냅샷의 전개 행 7개(2.6~2.12)를 현행 문면과 선행 관계로 실행한다.
2. **발화 후반부는 세션 이관 지시다.** 이 세션의 메인은 오케를 재개시키지 않는다. 다음 신규 세션의 메인이 새 오케를 파견해 잇는다.
3. **직전 오케의 상태**: 게이트 보고 시점 적재 약 170k 토큰 — 교대 임계 120k를 넘겼다. 재개하지 않는 처분이 교대 규율과도 일치한다. 직전 오케가 남긴 `진행`·`상신중` 행은 없다(파견표 전 행이 `완` 또는 `미착수`).
4. **오케 중계문의 라벨 오기 기록**: 직전 오케의 게이트 보고가 승인 대상을 "게이트 1이 확정한 프레임 B 아래"라고 적었으나, 게이트 1의 사용자 결정은 프레임 A이고 이 파일의 브리핑·행 2.6~2.12 실물도 프레임 A 구조다(행 2.8 임무 5항이 "프레임 A의 차단 조건"을 명시한다). 메인이 브리핑 전문과 행 파일 전건, 승인 대조 렌즈 판정으로 대조해 확인했다. 산출물 결함이 아니라 중계문의 오기다.
5. **다음 세션 메인의 재개 절차** (do-dag SKILL.md 「1. 오케 파견」의 재개 경로):
   - do-dag 문서 전건(`전거/` 제외)을 읽는다. `결정/` 전건의 「전파」 절을 읽고 `영향있음` 줄을 실물로 대조한다.
   - `python C:\math\.claude\skills\do-dag\scripts\dag_marker.py open --phase pvsnp-탐사-1`을 그대로 다시 돌린다 — 이미 활성이면 재개로 지나간다.
   - 아래 프롬프트 축자로 새 오케를 파견한다. `subagent_type: gp-sonnet-medium`, description `do-dag 오케 pvsnp-탐사-1 #2`.
   - 새 오케는 첫 사이클에서 2.g2(미착수·선행 완결)에 닿아 수확 후 정지로 완료 신호 좌표를 보고한다. 이 파일의 frontmatter `상태:`가 이미 `결정됨`이므로, 메인은 그 보고에 재개 신호만 주면 오케가 `완`을 기입하고 2.6부터 잇는다.
6. **새 오케 파견 프롬프트 축자** (직전 오케와 같다):

~~~~text
너는 do-dag 오케스트레이터다. 너는 파견만 한다.
공통 규율: C:\math\.claude\skills\do-dag\계약\공통.md. 첫 행동으로 전문을 읽고 그대로 따른다.
대응표: C:\math\.claude\skills\do-dag\대응표.md. 공통 규율을 읽은 뒤 전문을 읽고 그대로 운전하라.
배정: C:\math\.claude\skills\do-dag\references\배정.md. 배정표와 Codex 일반 파견에 닿으면 이 문서를 읽어라.
국면명: pvsnp-탐사-1
모델_프리셋: mixed
검증런_모델_프리셋: mixed
파견표: C:\math\.sdd\dag\pvsnp-탐사-1\파견표.md
0번 행: C:\math\.claude\skills\do-dag\행_0.md — 경로 전사용이다. 읽지 않는다.
예외 파견문: C:\math\.claude\skills\do-dag\파견문_예외.md
스킬 루트: C:\math\.claude\skills\do-dag
검산 명령: python C:\math\.claude\skills\do-dag\scripts\dag_check.py --table C:\math\.sdd\dag\pvsnp-탐사-1\파견표.md
마커 명령: python C:\math\.claude\skills\do-dag\scripts\dag_marker.py
대상: 사용자 지시 두 건의 축자와 메인 주석 다섯 항이다.

사용자 지시 1 (크리덴셜 문자열 하나만 파일 경로로 치환했다): "P vs NP 문제를 풀어. 자율적으로 직접 선행연구와 연관연구 등을 조사 및 연구해 참고하고 또한 동적으로 직접 DAG의 전개 등을 새로 펼치고 수정하면서 여러 가능성의 시험 및 시행착오의 누적 등을 쌓아나가고 그를 통해 크고 작은 breakthrough와 insight, clue 등을 누적하고 반증하고 기각하고 조합하고 반복해서 쌓아나가면서 증명 혹은 반증 등을 향해 나아가. 조사는 https://kudos.knu.ac.kr/ 에 [로그인 크리덴셜 — C:\math\.credentials\kudos.md 에 있다] 로 로그인해서 학술DB 페이지를 통해 필요한 웹사이트 등에 접속해 수행하고, 이러한 조사는 별도 playwright 에이전트에게 구체적인 지침 및 지시 등을 제공해 playwright로 해당 에이전트가 직접 브라우저와 상호작용해 수행하게 해야 해. 품질, 정합성, 논리적 타당성 등에 대해 가장 엄정하고 엄격한 기준을 유지하고, 스스로를 끊임 없이 반증하며 너 스스로의 판단이 아니라 오직 학계의 학술적인 기준 및 체계에 의해 정합성이 입증 된 것 만을 타당한 사실로 받아들이고 나아가. 한 번에 모든 문제를 풀려고 하지 말고, 문제를 조각내서 조각 조각 부분 부분 도움이 될 수도 있을지 모르는 것들을 쌓아나가면서 꾸준하게 전진해 나아가"

사용자 지시 2: "발동 전제가 충족되지 않았지만, 이번 do-dag은 애시당초 달라. 어떠한 시작점을 정해서 그걸 구현하게 하는 것이 아니야. 어떻게, 어디로, 어느 과정을 거쳐 가야 하는지 몰라. 다만 목적지만을 알고 있는 시점에서 do-dag을 통해 더듬거리며 나아가려는 것이지. 틀리면 틀리는대로 그 시행착오를 누적해가면서"

메인 주석:
1. 두 지시의 축자 정본과 발동 경위는 결정 파일 C:\math\.sdd\dag\pvsnp-탐사-1\결정\사용자확정-탐사형발동.md 에 있다. 이 국면은 확정 정본 없는 탐사형 국면이다.
2. 문제의 정본 명제·선행연구·연구 경계의 원자료는 C:\math\research\p-vs-np-statement-and-prior-work.md 다.
3. 학술DB 로그인 크리덴셜은 C:\math\.credentials\kudos.md 에 있고 git 추적 밖이다. ID·PW 값을 파견문·보고·산출물·커밋 어디에도 인용하지 않는다. 필요한 행의 파견문에는 이 파일의 절대 경로만 싣는다.
4. playwright 브라우저 조사 행은 Agent 도구의 subagent_type을 gp-* 로 지정하면 playwright MCP 도구가 차단된다. 그 행만 subagent_type을 claude 로 지정해 파견하고, 파견문에 사용할 모델·노력을 명시한다.
5. 이 국면의 완료는 P vs NP 의 해결이 아니다. 완료는 학술 기준으로 검증된 부분 산출(조사 기록·명제·보조정리 시도·반례 실험·기각 기록)의 누적과 그 정직한 판정이다. 증명·반증을 주장하는 산출은 알려진 장벽 결과(relativization·natural proofs·algebrization) 회피 여부를 포함한 적대 검증을 통과해야 한다.

추가 주석 (2기 오케에만): 사용자확정 결정 C:\math\.sdd\dag\pvsnp-탐사-1\결정\사용자확정-fable대체.md 에 따라 예외 에이전트의 모델은 배정표 mixed의 fable high가 아니라 gpt-5.6-sol high다. fable 한도 소진 조항은 이 국면에서 서지 않는다.
~~~~

## 전파 (메인 기입 — 실행 중 결정만)

- 불변식 문면: 영향없음 — 승인은 현행 문면의 실행이고 불변식을 정정하지 않는다.
- 미착수 행 파일: 영향없음 — 승인 대상 행 2.6~2.12가 이미 이 파일을 `정본:` 슬롯에 싣고 첫 임무로 결정 절을 소비한다. 문면 변경이 없다.
- 파견표 행 집합·선행: 영향없음 — 행의 추가·제거가 없다. 오케를 이 세션에서 재개시키지 않으므로 2.g2의 `완` 기입은 다음 세션의 새 오케가 한다.
- 파견표 모델 열: 영향없음.
- 이음새 원장: 영향없음 — S1~S7 등재는 행 2가 이미 마쳤고 이 결정이 바꾸지 않는다.
- 기준선 미결 · 재량 위임 조항: 영향없음 — 이 게이트가 해소하는 기준선 미결이 없다(M1·M2는 게이트 1이 닫았다).
