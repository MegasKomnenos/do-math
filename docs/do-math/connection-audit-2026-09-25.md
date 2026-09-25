# do-math 정적 연결 감사

기준 소스: `c4d78382a6922cd1a65ebe5e859ffb110d1cfab2`에서 시작한 `.claude/skills/do-math/` 249개 파일. 감사 중 변경한 파일은 현재 작업 트리의 원문으로 다시 확인했다. graphify는 시작할 때 `current`였고, 수정 중에는 `stale`인 기존 지도를 위치 탐색에 사용했다. 마지막 조회에서는 2026-09-25T07:23:18Z 구축본이 현재 소스와 일치하는 `current` 상태였다. 이 감사에서는 그래프 갱신 명령을 실행하지 않았다.

## 경로와 판정 범위

지원 입력에서 코드 조건을 따라 도달 가능한 계약 전달을 경로로 삼는다. 진입점에서 입력·권한·스키마·상태 전이·저장·후속 소비·사용자 반환까지 추적하며, 오류·중단·재시도·복구는 효과가 달라지는 별도 분기로 본다. 반복은 무한 경로로 펼치지 않고 진입·유지·종료 조건을 검사한다. 파일 포함과 단순 import는 계약의 위치를 찾는 근거이며 동작 적합 판정이 아니다.

| 정적 전수 목록 | 결과 | 해석 |
|---|---:|---|
| graphify 파일·노드·관계 | 249 · 6,520 · 23,028 | 마지막 `current` 상태의 수치. 관계 자체는 적합 판정이 아님 |
| Python 구문 | 220개 파일, 파싱 오류 0 | 함수의 의미는 별도 검사 |
| 생산 코드 모듈의 진입점 관계 도달성 | 77/77 | CLI·예약 감독·작업자·제출·형식 검사 진입점에서 `calls`·`uses`·`imports`·`inherits`를 따라 확인 |
| 교차 모듈 `calls` 관계 | 1,159 | 1,094건의 직접 호출 인자·서명 대조, 생성자 53건 중 명시된 `__init__` 41건 대조, `**kwargs` 5건의 전달 원문 확인, 지역 이름·별칭 연결 7건 확인. 직접 대조에서 나온 5개 경고는 지역 `read`·`stop`과 외부 `wait`의 동명 연결이었다 |
| 역할 문서 배정과 스키마 역할 | 10/10 일치 | `SKILL.md`의 역할 표, `contracts.ROLES`, 실재 문서 및 엔진 적용 분기 대조 |
| 내부 Markdown 링크 | 24개 문서의 68개, 누락 대상 0 | 링크 대상 존재만 확인 |
| graphify 미해결 구조 참조 | 24개 | 테스트의 `runner` 지역 참조 23개와 `scheduled_operator.Runner` 형식 별칭 1개. 결함 판정 근거로 사용하지 않음 |

## 계약 경계 대조

| 경로 | 생산자 → 전달 → 소비자 | 정적 대조 항목 |
|---|---|---|
| 공개 제어 | `cli.execute` → `engine.control` → `ResearchEngine._inbox/_controls` → Git 영수증 | 입력 형식, 접수 순서, 적용·반려·재전송, pause/resume/HOLD. 접수 순서 결함 F1 확인 |
| 초기화·운영 | `init` → `initialize`/통치·프로필 → `scheduled_operator`/bootstrap → 엔진 | 사용자 원문, 권한·능력·신뢰 관문, 예약 작업과 상태 저장의 별도 효과 |
| 역할 실행 | 역할 읽기 표·출력 스키마 → `prepare_role_input` → scheduler/model runner → `seal_submission` → `_apply` | 10개 내부 역할, review/intent/maintenance의 동적 단계, 입력 봉인과 출력 수신 분기 |
| 과제와 지식 | 후보 준비 → 계약 검토 → 계획 → 수행 → 지식 편입 → 후속 계획 | 과제 ID·의무·의존, 선행 입력과 개정, 형식 결과·동일성·목표 감사의 별도 효력 |
| 산출 보존 | 작업 공간 → `collect_outputs` → 중앙 제출 → repository/state contract/Git | 빠진 파일·바이트 한도·불변 artifact·저장 후 재읽기. 입력 형식 결함 F2 확인 |
| 독립 검토 | 고정 제안·입력 manifest → `review_cycle.accept_result` → 검토 집계·후속 | 자리·원저자·동료 비노출·복원 좌표. manifest 형식 결함 F3 확인 |
| 공급자 대기 | 모델 결과 → provider wait → 재관찰·재배정 | 실패 자료 형식, 공급자 분리, backoff 경계. 형식 결함 F4 확인 |
| 형식·외부·학술 | Lean 검사/독립 판정, HTTP grant/송신 기록, 추가 학술 요구 | 권한·현재성·확인된 효과의 분리. 실제 도구·원격 서비스는 실행하지 않음 |
| 조회·보고 | CLI query/read/export/status/timeline → repository/reporting | 24개 공개 명령의 구현 분기와 문서 반환 형식. README 불일치 F5 확인 |

## 확인한 불일치와 수정

| ID | 기존 불일치 | 수정 및 영향 |
|---|---|---|
| F1 | 제어 요청에 저장된 `accepted_order`보다 벽시계 `created_at`을 먼저 정렬해 시각 역행 때 수신 순서가 뒤집힐 수 있었다. 단순히 단조 시계를 우선하면 재부팅 뒤 기존 요청과 새 요청의 순서가 다시 뒤집힌다. | 인스턴스 inbox의 별도 로컬 잠금 아래 지속 증가하는 접수 번호를 먼저 기록하고, 그 번호로 처리 순서를 정한다. 재전송은 원 요청 번호를 유지한다. |
| F2 | `collect_outputs(captured_files=[])`가 빈 dict로 치환돼 명시된 형식 검사를 우회했다. | `None`만 빈 dict로 해석하고 다른 형식은 반려한다. |
| F3 | 독립 검토의 `input_manifest=[]`가 빈 dict로 치환돼 manifest 객체 검사를 우회했다. | 부재(`None`)와 잘못된 값(빈 목록)을 구별한다. |
| F4 | provider wait의 `failure=[]`가 빈 dict로 치환돼 실패 자료 형식 검사를 우회했다. | 부재(`None`)만 기본값으로 처리한다. |
| F5 | README는 텍스트 응답이 `status`뿐이라고 설명했지만, 구현과 같은 README의 예시는 `timeline --format csv`도 텍스트로 반환한다. | 반환 형식 설명을 현행 CLI와 일치시킨다. |
| F6 | 한 레코드의 큰 값이 둘 이상이면 payload 참조를 삽입 순서로 기록하면서 JSON 키는 정렬해 저장했다. 재읽기의 정본 인코딩 검사가 같은 기록을 거부했다. | payload 방문 순서를 키 정렬 순서로 고정했다. 두 큰 값의 저장·재읽기 회귀 사례를 추가했다. |
| F7 | `run(max_steps=1)`이 이미 시작한 환경 관측의 완료를 회수하고도, 보존된 제출을 다시 적용하기 전에 루프를 종료했다. 다음 실행에서는 관측을 새로 시작해 진행이 대기 상태에서 끊길 수 있었다. | 완료된 호출이 있으면 제어·게시 정산 단계를 한 번 더 거친 뒤 bounded run을 종료한다. |

F1–F4와 F6의 회귀 사례는 관련 테스트에 추가했다. F7은 실제 저장·검토 흐름의 기존 통합 사례로 재검증한다. 테스트는 합의대로 정적 검토와 수정이 끝난 마지막 검증 단계에만 실행한다.

## 검증 범위의 한계

이 감사는 정적 계약·코드 대조다. 실제 연구 인스턴스, 모델 서비스, Lean 증명, 예약 작업, HTTP 전송의 동작을 보증하지 않는다. 그래프의 방향·누락·추론 관계는 원문 검토가 필요한 탐색 단서이며, 모든 가능한 입력값과 실행 순서의 무결함 증명으로 해석하지 않는다. 최종 테스트 결과는 아래에 별도 기록한다.

## 최종 검사

- `python .claude/skills/do-math/scripts/probe_cli.py --skill-only`: `verified`. 문서·역할 스키마 구조 검사이며 의미·실행 성능 검사는 아니다.
- `python .claude/skills/do-math/scripts/run_tests.py --group unit`: 358개 통과, 실행 중 소스 변경 0.
- 변경 경계의 통합 사례 9개: 9개 통과. payload 저장·재사용, 제어 순서, provider wait, 산출물·검토 입력 형식, 보존 제출의 환경 관측 정산을 포함한다.
- 동시 제어 접수 사례: 1개 통과.
- `test_explicit_requirement_blocks_runtime_completion_until_independent_assessment`: 저장 코덱과 제한 단계 실행 루프의 결함을 각각 드러낸 뒤 수정 후 통과. 실제 모델과 Lean은 테스트 대역이며, 실제 Git 상태를 사용한 흐름 검사다.
- `lean` 19개, `resource` 9개, `archive` 1개: 모두 통과. 격리된 로컬 형식 검사·프로세스 자원·과거 검증 기록 구조를 확인한다.
- 전체 기본 그룹 실행은 초기 통합 사례의 실패를 조사하려고 중단했다. 수정 후 전체 1,750개 발견 테스트의 완주 결과는 없다. 통합 그룹 전체가 통과했다고 주장하지 않는다.
- Python 220개 파일 정적 파싱 오류 0, `git diff --check` 통과.

테스트 증거는 `.skill-workspace/do-math-audit-unit-current-2026-09-25/`, `.skill-workspace/do-math-audit-integration-final-2026-09-25/`, `.skill-workspace/do-math-audit-concurrent-2026-09-25/`, `.skill-workspace/do-math-audit-target-settled-2026-09-25/`, `.skill-workspace/do-math-audit-special-final-2026-09-25/`의 `report.json`에 보존했다.
