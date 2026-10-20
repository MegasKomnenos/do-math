# 목적과 완료할 결과

R14/8-A의 남은 F3, 즉 경쟁 관찰을 적용하는 도중 도착한 완료 결과가 관찰량에 비례해 지연되는 문제를 실제 현재 경계에서 해결한다. 원래 세 성질인 owner 바퀴 진입 적재분 한정·관찰량과 독립된 완료 회수 상한·대기 제어 한 owner 바퀴 내 처리를 유지하고, runtime 수리·직접 소비 시험·미러·최소 확인을 한 task에서 마친다. 수용된 F1/F2를 되돌리거나 단순히 정산 성공을 진행성으로 세지 않는다.

## 입력과 선행

SESSION_JSON workspace, 고정 inputs/context.md·plan.md·seams.md, task.json을 읽는다. C:/math/.async/dm/managers/0012/review.md·source-review.json과 tasks/r14/report.json·evidence/review.md·verification.json·changes.diff, atomic-counterexample/report.json·log·exit, progress-atomic-diagnostic.py가 출발 근거다. final-snapshots의4passed는 r14 제출판 증거이고 atomic 실패는 마지막 snapshot lock 전 판본이다. 원문은 C:/math/docs/do-math/continuous-development-2026-10-13의 sources/user-decisions.md·requirements-index.json 및 phases/001/tasks/closure-map/evidence의 requirement-state.json 8-A, tracking-state.json R14, prior-review-state.json PR11 B50/B34 해당 slice다. 큰 JSON의 필요한 항목만 읽는다.

r14와 r08 수용 뒤 시작한다. r14는 출발 수리이며 r08은 같은 core_engine.py의 앞선 제어 수정과 충돌하지 않기 위한 선행이다. 시작판에 반영된 r08의 보고/통합 결과에서 core가 바뀌었으면 그 제어 의미를 보존한다. 실행 중 r03-fix 및 독립 r09의 미완성 사본은 소비하지 않는다. 관찰 저장 schema는 자기 시작판의 실제 정의를 사용하고 버전 호환 경로를 만들지 않는다.

## 종료할 질문과 구현 판단

1. 보존한 진단의 실제 native1/64/1024입력·held formal worker·완료→실제 수신 사건을 읽어 F3를 좁힌다. 지금 관측기는 _observe_running 함수 진입에서 묶음 전체 가상 비용을 먼저 부과한다. 이는 실벽시계 측정이 아니며 함수 내부 수리만으로 이 선부과 비용이 사라지지 않는다. 실제 runner→ObservationBatch→queued callback→tracker/게시→collect 경계와 비용 관측 단위가 무엇인지 구별한다. 원문 요구와 구현자가 선택한 처리 단위/검사 방법을 혼동하지 않는다.
2. 새로운 큐/스레드/프레임워크를 추가하기 전에 큰 묶음 전체를 한 owner 호출로 처리해야 한다는 전제가 필요한지 검토한다. 생산·수송·owner 적용의 적절한 경계에서 유한한 처리 단위와 양보를 제공하는 가장 작은 수리를 선택한다. 특정 함수 내부의 재진입을 필수 방법으로 강제하지 않는다. 미게시 runtime을 가진 채 임의 continuation을 실행해 상태 원자성/롤백/제어 우선순위를 깨지 않는다.
3. 시험의 총입력1/64/1024, 사건당0.25초, 기존 고정1초·owner≤1 단언은 유지한다. 시험 입력을 줄이거나 N비례 상한/시간 경과만으로 성공을 만들지 않는다. 제품 처리 단위 자체를 바꾸는 것은 허용한다. 그때 비용 관측이 옛 큰 callback의 전액 선부과로 새 구현을 가리면 실제 사건 처리 단위에 대응시키고 동일 총입력·사건 비용·경쟁 도착점·상한을 유지했다는 근거를 남긴다. 시험만 바꿔 실패를 없애지 않는다. 필요한 가장 작은 실패/수리 비교로 새 runtime의 효과를 확인하고 지속 회귀를 제품 시험에 둔다.
4. 관찰 원 bytes/offset/first_row·receipt_key, 사건 순서·1회 적용, 자기 관찰 뒤 자기 결과 수신, caught_up/tick·종결/idle 의미, tracker candidate의 저장 성공 뒤 commit/실패 rollback, 제어→완료 순서를 보존한다. worker마다 관찰 세 mode의 의미를 바꾸지 않는다. r10의 실제 재전달/반려·뒤 정상 입력과 r03의 현재 저장 계약을 관련 영향 범위에서 대조한다. 처리 단위 변경으로 tick/review/중복 receipt 의미가 바뀌면 같은 작업에서 바로 수리한다.
5. 실제 ModelCalls·runner·worker·collector·owner·store를 유지하고 외부 CLI/Lean/Calls/시계는 기존 계약 fixture만 사용한다. OwnerProbe/ObservedCalls로 실제 함수의 사건을 관찰한다. 모델/기계의 동일 future 경계 대표를 재사용하되 동기 external HTTP 전체를 같은 경계로 합치지 않는다. R15/R16 전체 정산 재감사와 다른 의미 질문은 이 배정이 아니다.

## 수정 범위

task.json writes가 권한 정본이다. runtime은 parallel.py·scheduler.py·core_engine.py의 관찰 적용/게시 연결, model_runner.py·observation_transport.py의 직접 생산/수송 처리 단위, 필요하면 observations.py까지 이 F3 수리에 한정한다. core의 제어/제출 정책, record schema, review 도메인 계약을 별도로 재설계하지 않는다. progress·직접 settlement/관찰 적용/관찰 ingress·Calls 계약 시험과 좁은 scheduling helper, 대응 미러를 같은 task가 소유한다. r08의 제어 시험·r03-fix의 schema/pairs/helper·r09의 제출 시험과 helper는 읽기 전용이다. 공유 관측 helper는 기본적으로 읽기 전용이며 새 구조가 꼭 필요한 경우에만 배정된 scheduling_progress를 사용한다. 필요 없는 helper/정책/등록부를 추가하지 않는다.

## 최소 확인과 보고

현재 코드/원보고로 충분한 성질은 유지하고 새 불확실성만 자기 workspace의 scripts/run_tests.py jobs1로 확인한다. 실패를 읽고 고친 ID만 다시 실행한다. 최종 관련 ID는 변경 영향에 맞게 최소 선택하며 전체 일반/T3/변이/T4/T5·실외부 모델/Lean/Job/설치/예약은 이 배정이 아니다. r14에서 이미 알려진 구조44건은 별도 묶음 남김이며 이번 진행성 완료의 증거와 구별한다.

소스가 고정된 실행의 선택/실제 row/exit/해시·최초 실패·fixture 오류·남김을 evidence에 보존한다. 판본이 다른 결과를 전체 통과로 합산하지 않는다. 공식 build_skill_mirrors.py --target .agents와 --check --target .agents로 미러를 만들고 대응 바이트를 확인한다. 비용 캐시2개는 evidence에 보존한 뒤 자기 base로 복원한다. report에는 실제 동작과 수리 이유, 직접 확인 범위, F3 및 8-A의 처분과 남김을 적고 check.py report C:/math/.async/dm r14-fix의 PASS를 확인한다. 공용소스·공용문서/queue/state·engine·다른 task·원자료·Git index를 수정하지 않고 graphify를 갱신하지 않는다.
