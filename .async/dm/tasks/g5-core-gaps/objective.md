# core 수신·게시·복구의 남은 계약 질문을 해결한다

g5-core-rest의 유효한 부분 결과를 수용했다. 이 작업은 그 수용판에 남은 core_engine 69arc/93행과 integration.bundle_impact_request 1arc/1행, 총70arc/94행의 현재 의미를 판단하고 필요한 구현·직접 확인·설명·공식미러를 함께 마친다. 과거 측정 좌표는 검토 대상을 찾는 자료이며, 각 좌표를 독립 시험으로 채우라는 quota나 모두 실제 결함이라는 판정이 아니다.

## 입력과 소유

SESSION_JSON, task.json, inputs/context.md·plan.md·seams.md와 자기 workspace의 do-math AGENTS.md·시험-지침.md를 읽는다. 추가 절대경로는 읽기 전용 원자료다. managers/0078/review.md·verification-review.json·assignment-scope.json, 자기 gap-scope.json, g5-core-rest의 report.json·evidence/judgment.md·remaining-functions.md·scope-coordinates.json을 필요한 부분부터 소비한다. gap-scope의 accepted_source_sha256/current는 이번 수용판이며 original은 g5-full의 과거 좌표다. 남김 이유와 제안 시나리오는 이전 구현자의 판단이지 확정 요구가 아니다. 실제 caller와 현재 코드로 다시 판단한다.

제품 쓰기는 core_engine.py·integration.py·필요한 제출 경계 submission.py, task.json에 열거한 직접 시험/helper·관련 설명과 대응미러다. g5-trust-rest의 formal/formal_engine/trust_validation/knowledge_records와 이음새 정본, g5-entry-gate의 worker/control/operator 입구·CLI 설명은 읽기 전용이다. 기존 review/governance/activities/knowledge/lifecycle 제공자도 자기 시작판을 소비한다. 범위 밖 제공자 수리가 실제로 필요하면 원인·영향·필요 변경을 정확히 보고한다. 실행 중 사본의 미완성 결과를 가져오지 않는다. 허용 경로 목록은 수정·실행 의무가 아니다.

사용자 저장범위 지시 C:/math/.async/dm/sources/storage-scope-direction-2026-10-15.md와 원설계3.3/A22·5.5를 적용한다. 공통 codec/저장검증과 기존 업무 보장을 재사용한다. 전가족·전필드·새reader·옛head 재입증, 새 registry/검증 framework, 장기감사를 추가하지 않는다.

## 맡은 결과와 판단 순서

1. 먼저 현재 입력·저장·소유자 전이가 보장하는 전제를 확인해 불필요한 분기와 검사를 줄인다. 특히 preserved request/target/action의 부재, overflow 대기와 live 실행의 겹침, 닫힌 질문의 미해소 target, 고정 planning population, 같은 응답 계보의 상충 receipt, 잠금 아래 link race는 실제 생산 가능성을 먼저 판단한다. 기존 불변식만으로 충분한 부분은 정적 근거로 마치며 숫자를 위해 불가능한 내부 상태를 조립하지 않는다. 외부 파일/Git/종료 관찰의 실제 오류 가능성을 내부 불변식으로 지워서는 안 된다.
2. 실제 가능한 수신·게시·복구 경계는 기존 시험의 최소 사례로 묶는다. core의 공개 request 재접수와 대기 해소, review 자원/재평가 upkeep, 게시 완료 뒤 효과/정산 실패, impact review의 혼합 결과·손상과 원 생산자 routing, 위임 권한 변화, goal-audit의 이미 게시된 결과 복원, native capture/replay·overflow, 준비 결과/조건 이름 결박, 운영 처분·cleanup/check가 정확한 결과를 보존하도록 한다. 정확 대상·반려 사유·원결과/영수증·현재성·종료/정산 중 해당 변경의 불확실성에 필요한 값만 단언한다. 기존 helper와 생산 경로를 읽고 현 계약에 맞춰 fixture를 구성한다.
3. integration.bundle_impact_request의 bounded exclusion loop 실패(현재132→140, 행140)는 core의 impact 게시와 함께 처리한다. 가능한 assignment graph와 고정점 계산의 전제를 먼저 분석한다. 임의 plan 대역으로 진동을 만들거나 증명 없이 제외하지 않는다. 불필요한 반복/제약을 단순화할 수 있으면 현재 권한·정확 입력·영향 집합 의미를 보존하면서 관련 소비자와 직접 확인을 같이 고친다.
4. 앞 task에서 해결한 external retry predecessor/persist·source alias·grant 없는 external request·resume_activity→assign_execution 설명은 재배정하지 않는다. 실제 관련 변경 때문에 다시 불확실해진 경우에만 확인한다. 새 제품 결함 수리와 시험 구성·기대값 오류 교정을 구별한다.
5. 의도적 미도달은 원설계5.5의 같은행 구체 사유와 실제 caller/불변식으로 판단한다. 자동 제외를 전제하지 않으며 blanket no-cover·새skip·층/분모/임계값 완화로 숨기지 않는다. 함수 진입을 단언 성공으로, T4/자식 도달을 T3 원도달로 바꾸지 않는다. 남김은 원/현재 좌표·현재 의미·다음 필요한 입력과 함께 사실대로 보고한다.

## 최소 확인과 자원

시험슬롯1, 공식 scripts/run_tests.py --jobs 1, 한 번에 한 명령만 실행한다. 두 진행 중 동료와 합계3슬롯이다. 정적 판단으로 충분하면 실행하지 않는다. 실행이 필요한 관련 변경만 가장 작은 선택으로 확인한다. 분기 도달이 질문인 경우 그 선택의 --tier T3 원coverage를 함께 확보하고 같은 성질을 일반/T3로 중복 실행하지 않는다. 작은 관련 수리·필요 확인·설명은 이 task에서 함께 마친다.

전체 G4/fresh 전체T3·전체변이·병렬자식을 만드는 meta 검사·T4/T5·유료호출·실예약/도구설치 변경은 범위 밖이다. 시간은 소프트 기준이며 초과만으로 실패/skip/변이포착으로 판정하지 않는다. 외부 포트 실패 대역은 해당 경계에 사용할 수 있지만 제품 함수를 교체하지 않는다.

측정에 Git root가 필요할 때만 자기 workspace에 독립 .git과 실제소스 기준commit을 준비할 수 있다. g5-core-rest/evidence/prepare.py 또는 g5-full/evidence/prepare.py를 읽어 자기 경로에 적용한다. 준비 전후 제품bytes와 실제root/HEAD를 기록한다. 다른 .git 복사·공용Git/index/commit·global 설정·가짜HEAD·remote/push는 하지 않는다. 기존 GIT_CEILING_DIRECTORIES를 유지하며 자기 task 부모와 저장소 밖 짧은 전용 임시root만 추가한다.

command/cwd·관측exit·원report/stdout/stderr/coverage·선택/실제행·fixture·판본SHA·실행중변경을 보존한다. 측정별 T3 store가 필요하면 다음 실행 전 외부 evidence에 보존하고, 생성 index/timing/store는 보존 후 base 바이트/부재로 복원한다. 소스가 다른 부분판의 통과를 한 최종판 전체성공으로 합산하지 않는다. 부분gate=false/exit1과 실제 시험 실패를 구별한다. 전체 제품 불변성 재감사를 새 검증 목표로 만들지 않는다.

## 제출

evidence/judgment.md와 report에 해결한 동작·제거한 전제·재사용 근거·실제 확인/한계·남김을 적는다. 배정된 질문을 모두 해결했을 때 complete이며, 단순 미완료는 partial이다. 외부 입력 부재가 아닌 미완료를 blocked로 바꾸지 않는다. 공개 인터페이스가 달라지면 실제 파일·심볼, 입력·출력·실패·소유자의 의미를 관련 설명과 함께 인계한다.

공식 build_skill_mirrors.py로 정본 대응 미러를 생성/check한다. 공용 context/plan/seams/queue/state, engine, 다른 task, graphify는 수정하지 않는다. `python C:/math/services/async-development/check.py report C:/math/.async/dm g5-core-gaps`를 통과시킨다. 최종수용판 G4/G5·G6~G8·G1~G3 연결과 환경6arc/10행·L01/실경계는 전체 계획의 남은 조건이다.
