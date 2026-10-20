# 수명·상태·저장 의미의 잔여 분기와 종료 시험의 정확 반려

사용자 목표는 실제 제품 경로의 결과를 확인해 결함이 시험을 빠져나가는 기제를 막는 것이다. g5-full의 fresh T3에서 드러난 공백 중 g5-core 수용 후 남은 7모듈33arc/29행과 g5-worker가 발견한 기존 종료 시험의 정확 반려 누락1건을 한 task에서 처리한다. 관련 제품/시험 수리·최소 직접 확인·설명·공식 미러를 함께 마친다. 좌표는 관측된 공백이며 도달 가능성이나 제품 결함의 사전 판정이 아니다.

## 입력과 소유

SESSION_JSON, task.json, inputs/context.md·plan.md·seams.md, 자기 workspace의 do-math AGENTS.md·scripts/tests/시험-지침.md를 먼저 읽는다. gap-scope.json은 g5-core/evidence/remaining-scope.json의 정확한 원/현재 좌표·수용판 SHA와 실패 시험을 연결한다. managers/0072/review.md·assignment-scope.json, 원 task 보고·judgment·필요한 원coverage를 읽는다. 공용 소스와 다른 task 기록은 읽기 전용이다. 추가 docs 경로는 C:/math의 외부 원문이며 상대 제품 경로는 자기 workspace다.

실제 선행은 g5-core의 수리·잔여 좌표와 g5-worker의 수용판·smell 발견이다. 시작 시 진행 중일 수 있는 g5-publish·g5-calls의 사본/결과를 소비하거나 정의를 바꾸지 않는다. core_engine.py/call_engine.py, support/engine_lifecycle.py·engine_control.py·scheduling_initial.py·repair_host.py, README·착수조건·초기화정비·이음새-정본.md 등 다른 task 소유는 읽기 전용이다. 필요하면 허용된 unit/test_core_state_gaps.py와 support/core_state_gaps.py에 이 작은 범위의 사례를 둔다. 새 helper는 기존 적합한 생산자/fixture 재사용만으로 부족할 때만 만든다. task.json의 정확 writes가 허용 상한이며 전수 수정/실행 quota가 아니다.

## 맡은 결과

1. dispatch_engine._dispatchable의 같은 과제 연구 중복, engine._run_executor의 닫힌 인스턴스와 기동 불일치, lifecycle_engine의 제한 복구 승인/범위·원입력 ID·준비성/재고 시각·기계 실행 정산, repair_execution.continue_initial_retries의 실패 후 대기 유무를 현행 생산/호출 계약으로 판정한다.
2. record_schemas.validate_semantics의 staged 전이/검토·입력 binding·위임 참조/판정·impact 대기 결속과 state_checks.inspect_state/_inspect_area의 신뢰 유일성·종료 과제의 live worker·이관 의무·학술 evidence/완료 상태·영역 순회를 다룬다. 공개 입력의 구조·참조·권한·원내용·현재성·실제 종료 장벽을 유지한다. 저장 경계가 이미 보장하는 조건과 inspector가 따로 보고해야 하는 조건을 구분한다.
3. repository._descends의 계보 한도, _learn_artifact의 cache 축소, _validate_artifact_evidence의 불변 namespace를 실제 caller/검증 경계로 판정한다. 공통 codec/검증과 기존 업무 단언을 재사용한다. 가족별 모든 생산자/필드/새reader/옛head 시나리오를 새로 만들지 않는다.
4. tests/sim/test_scheduling_close_parallel.py의 InterruptedCallEvidenceTests.test_aborted_owner_preserves_the_actual_exception_result_and_clears_live_ids는 future.result에서 KeyboardInterrupt 종류만 확인해 unpinned_rejection을 낸다. 실제 calculate가 던지는 사유를 정확히 고정하고 기존 원결과 bytes·저장 결과·live ID/transport/continuation 정산 단언을 보존한다. smell 규칙을 약화하거나 시험을 제거/skip하지 않는다. 별도 작은 문서/정리 task로 나누지 않는다.

먼저 불필요한 중복 방어·죽은 계약의 제거/축소로 해결되는지 검토한다. 유효 입력으로 도달하는 공백은 가장 싼 기존 시험에 정확 결과/반려/상태/bytes 단언을 보완하고 실제 결함은 같은 task에서 고친다. 제품 내부 함수 패치·원문 없는 예외 포착·구판 fixture fallback으로 공백을 숨기지 않는다. 외부 OS/포트 대역과 실제 제품 판단을 구분한다. 현재 source에서 특정 분기가 앞 검증으로 닫히는지는 그 생산자·caller·validator로 설명한다.

원설계3.3/A22·5.5와 sources/storage-scope-direction-2026-10-15.md를 적용한다. 이 7모듈의 구체 잔여만 다루며 저장 전가족 재입증·새framework·장기감사를 추가하지 않는다. 의도적 미도달 제외에는 같은 행의 구체 사유·현재 계약 근거가 필요하다. blanket no-cover, 새skip, 층/분모/임계값 완화는 허용하지 않는다. 범위 밖 제공자 수정이 꼭 필요하면 파일·심볼·실제 반례·영향을 보고하고 해당 좌표를 남긴다.

## 최소 확인과 자원

시험슬롯1개, 기본 --jobs 1, 한 공식명령씩이다. 다른 두 task와 전체 시험worker3 이하를 유지한다. 자기 scripts/run_tests.py의 가장 작은 관련 선택으로 이번 불확실성만 확인한다. 정적 판단으로 충분하면 실행하지 않는다. 필요 시 해당 선택의 --tier T3 원coverage로 좌표 도달을 확인하고 다른 모듈 gap의 exit1과 실제 시험 실패를 구별한다. 같은 동작을 일반/T3로 불필요하게 반복하지 않는다. 소프트 시간 초과는 기록하고 경과 시간만으로 중단/skip/실패/변이포착으로 세지 않는다. 실행 중 소스를 고정한다.

전체G4/T3·전체변이·T4/T5·유료호출·실예약·설치/호스트권한 변경·내부 다중worker meta는 배정 밖이다. 모든 동료 종료를 기다리는 barrier는 없다. T3가 실제 Git root를 필요로 할 때만 자기 workspace에 독립 .git/실제 소스의 로컬 기준commit을 준비할 수 있다. g5-full/evidence/prepare.py를 자기 경로에 맞추고 준비 전후 bytes·실제 root/HEAD를 남긴다. 공용 Git·다른.git 복사·가짜HEAD·global설정·remote/push는 쓰지 않는다. 기존 GIT_CEILING_DIRECTORIES를 보존하고 자기 task 부모와 저장소 밖 짧은 고유 temp root를 추가한다. 자기 HEAD는 공용main/성공 인증이 아니다.

command/cwd/관측exit·원report/stdout/stderr·선택/고유실제행/fixture·판본SHA/실행중변경을 보존한다. 원/현재 좌표를 도달·제거·정당한 제외·남김으로 연결하고 여러 선택/판본을 전체 성공으로 합산하지 않는다. 생성 index/timing/store는 원자료 보존 뒤 base의 bytes/부재로 복원한다.

## 제출

evidence/judgment.md와 report.json에 무엇을 고쳤는지, 제거/유지의 이유, 실제 확인·재사용 근거·한계와 남은 좌표를 적는다. 미완료는 partial/blocked로 남기며 이 결과를 전체 G5 통과로 쓰지 않는다. 허용된 계약/운영-점검.md의 상태 검사 설명과 관련 docstring을 필요한 만큼 갱신하고, 다른 task 소유 문서의 변경 필요는 정확한 파일/심볼/계약으로 report에 인계한다.

공식 build_skill_mirrors.py로 대응 미러를 생성/check한다. 자기 workspace의 writes만 수정하며 공용 문서/queue/state·engine·다른 task·기존 연구·graphify는 수정하지 않는다. python C:/math/services/async-development/check.py report C:/math/.async/dm g5-state를 통과시킨다. 최종 통합판 G4/G5·G6~G8 및 script/frozen·I/O 환경·Lean/신뢰 잔여는 이 배정의 완료 주장과 구별한다.

