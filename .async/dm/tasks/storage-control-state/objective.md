# 수명·시계·제어 처리의 저장 계약 네 가족을 마친다

사용자 목표는 실제 제품 생산값과 저장 수신 계약의 불일치가 시험을 빠져나가지 않게 만드는 것이다. research.lifecycle, runtime.clock_guard, runtime.processed_controls, runtime.extended_controls 네 가족의 실제 생산·저장·필드/내용 대응과 확인한 수리를 한 작업에서 마친다. 단순 가족표 작성이나 저장 성공만으로 완료하지 않는다.

SESSION_JSON, task.json, inputs/context.md·plan.md·seams.md, do-math AGENTS.md와 시험-지침.md를 읽는다. 원자료는 C:/math/docs/do-math/continuous-development-2026-10-13/sources의 user-decisions.md·requirements-index.json·model-policy-2026-10-14.md·document-batching-2026-10-14.md, phases/001/tasks/closure-map/evidence/requirement-state.json의 R01/1-A·1-B/K-78, C:/math/docs/do-math/시험-재편-2026-09-29/설계.md 3.3/A20이다. C:/math/.async/dm/tasks/keep-storage/evidence/families.json의 원 root/family를 유지한다. managers/0053/review.md와 storage-conversation의 수용 보고·families/write-sites/judgment·검증 원보고를 읽는다. 외부 원자료와 다른 task 기록은 읽기 전용이다.

## 실제 선행과 소유

storage-conversation의 실제 생산→검증 게시→새 contract reader decode 방법과 직접시험을 소비한다. storage-academic은 같은 record_schemas/schemas.py 및 __init__.py·정본 설명을 수정 중이므로 그 수용판도 선행이다. 현재 확인한 미생산 후보의 정리·직접소비 수정·검증을 쪼개지 않고 처리하기 위한 파일 소유 순서다. 시작 시 실제 수용된 중앙 스키마를 읽고 manager0053 시점의 행 번호/필드 수를 맹목적으로 복원하지 않는다. execution-storage의 종료는 필요하지 않다.

수명/초기화 생산자·저장 기반·중앙 스키마와 직접시험·관련 정본 설명/미러만 자기 writes에서 수정한다. 실행 중 execution-storage가 소유한 core_engine/call_engine/dispatch_engine/provider_engine/model_runner/scheduled_operator/repair_execution 및 실행 직접시험은 읽기 전용이다. core의 실제 공개 제어 처리 경로를 호출하여 확인할 수 있지만 구현을 수정하지 않는다. 정확한 결함이 자기 writes 밖에서 확인되면 원 입력/실패/필요 심볼을 남기고 자기 범위의 독립 결과를 마친다. 미완성 task 사본을 소비하지 않는다.

## 현재 사실과 판단할 질문

1. research.lifecycle은 singleton이다. 현재 required는 state/immutable_input/input_id이고 optional은 activated_at/activation/adoption/history/intent_check/permanently_closed/required_capabilities다. initialize_state의 원 UTF-8 text/bytes/SHA와 input_id, InitializationEngineMixin._initialization_control의 명시 채택, LifecycleEngineMixin._activate_initialization/_pause_lifecycle/_resume_lifecycle/_apply_extended_control의 실제 전이를 대응한다. immutable_input의 text/bytes/hash는 원문에서 독립 계산하며 JSON 포장 bytes와 혼동하지 않는다. activation의 completed/missing/observation_errors, adoption의 config/governance/review 해시·프로필/권한/source refs, intent_check의 실제 해석/검사 execution과 input SHA를 현재 생산자에 연결한다. 중첩 닫힌 객체 필드를 top-level 검사만으로 완료 처리하지 않는다. 영구 close는 lifecycle.state에 임의 closed enum을 더하는 문제가 아니라 permanently_closed와 runtime.status='closed'의 현재 계약이다. 초기화·활성화/정지/재개·close·옛head·원input 불변의 충분한 기존 근거를 재사용한다.
2. runtime.clock_guard는 metadata이지만 닫힌 객체다. _clock_guard가 계산한 메모리 반환과 _refresh_readiness가 실제 root에 게시한 값을 구별한다. usable/observed_utc, persisted/live UTC·monotonic regression의 reason/last_observed_utc/expected_at_least와 저장 state를 주입 시계·high-water·독립 계산에 연결한다. 정상 시간이 돌아와도 보존된 failure가 검증된 재관측 전 권한을 열지 않는 기존 성질을 유지한다. manager0053의 현재 검색에서는 optional observed_at의 root writer를 찾지 못했다. 이는 제거 검토 후보이며 해당 문자열의 다른 가족 사용은 생산 근거가 아니다. 현재 전 생산·소비를 읽어 처분하고 실제 쓰이지 않는 슬롯만 정리한다. 모든 해상도/시계 분기를 새로 반복할 필요는 없으며 불변 기존 근거와 새 실행의 범위를 구별한다.
3. runtime.processed_controls는 ID 배열 singleton이다. initialize_state의 빈 값과 core_engine의 공개 process_controls/_apply_inbox 실제 처리 결과를 연결한다. 정상·반려·중복/재전달에서 어떤 요청 ID를 언제 한 번 보존하는지 원 요청·receipt와 대조하고 reload 뒤 비재생, 독립 요청의 진행, 옛head/입력 불변을 유지한다. 배열의 빈 properties를 역방향 성공으로 세지 않는다. 기존 R08/R09/R29-R30의 충분한 실제 처리 근거를 재사용하고 손으로 processed ID를 넣은 fixture를 실제 writer라고 보고하지 않는다. control_receipts/events/integrations 전체 가족은 이 배정 범위가 아니다.
4. runtime.extended_controls는 요청 ID→닫힌 행의 singleton이다. _apply_extended_control은 현재 성공 뒤 request의 deepcopy/action/processed_at를 작성한다. 재사용 ID는 exact_content_hash(old['request'])로 중복과 내용 충돌을 구별하며 _limited_recovery_control 등은 보존 request를 소비한다. manager0053의 현재 검색에서는 schema의 source_ref/status/result 필드 writer가 없고 request/action/processed_at만 저장된다. 실제 코드/소비자를 확인해 미생산 슬롯은 제거하고 유효 필드·원 request의 text/origin/config/created_at·키의 요청 ID·정확 처리시각을 유지한다. request/result의 열린 evidence와 map 내부 행의 닫힌 필드 모집단을 구별한다. pause/resume의 early return을 실제 extended 기록으로 잘못 세거나 새 ledger를 추가하지 않는다. 원 요청 변경/다른 반환 격리, 동일 재전달과 바뀐 내용 반려 및 정상 후속의 저장 결과를 기존 직접시험에 연결한다.

## 구현과 최소 확인

현재 실제 제공/수신의 정확 심볼·source SHA·시험 ID와 판본을 가족별로 연결한다. closed schema 필드에는 기존 contracts.pairs.assert_pair를 쓰고 nested object/map row도 실제 표본으로 대응한다. scalar/REFS/open evidence에는 독립 값·순서·부재 단언을 쓴다. 새 registry·범용 wrapper·병렬 프레임워크는 만들지 않는다. 기존 test_lifecycle_engine_public/controls/initialization_controls 및 record_family_storage의 직접시험을 우선 보완하고, 새 helper는 실제 공유가 필요한 경우에만 만든다. 긴 활성화·승인 시나리오를 가족/필드별로 반복하지 않는다.

정상 표본은 실제 producer→ResearchRepository.initialize/save_with_state 검증 게시→새 installed_contract 객체를 받은 reader의 첫 load로 읽는다. Repository._read_key는 contract 객체를 포함한다. publication cache가 돌려준 값을 별도 bytes decode 근거로 쓰지 않는다. family별 checker/validator, 명시 저장 경로, metadata/manifest 또는 singleton bytes, 정확 반려/head불변/write0와 필요한 손상 read 하나를 확인한다. 비검증 publish는 손상 read 반례에만 사용한다. 동일 상태의 전체검증을 불필요하게 반복하지 않는다.

실제 미생산 슬롯을 제거할 때 현재 소비·직접시험·정본 설명·공식 미러를 함께 고친다. 이전 fixture를 살리기 위한 alias/자동보충·구판 호환 분기는 금지한다. 현재 권한/참조/immutable input/high-water/close·처리 정확1회 검사를 약화하지 않는다. 앞선 metadata5·수명8·대화제어5가족의 단언은 보존한다. 학술 task가 수리한 중앙 스키마의 다른 가족은 그대로 유지한다. 공통 pairs와 다른 task helper는 읽기 전용이며 복제한 역방향 알고리즘을 만들지 않는다.

자기 workspace의 공식 scripts/run_tests.py --jobs 1로 변경에 남은 불확실성을 해소하는 최소 ID만 실행한다. 정적으로 충분한 질문은 실행하지 않는다. 현재 배정의 공식시험은 execution-storage와 본 task 최대2개·각jobs1이며 전체 상한3을 유지한다. source를 실행 중 고정하고 selected/실제 고유row/counts/fixture_counts/관측exit/source SHA/changed_during_run/소프트초과를 보존한다. 최초 실패와 교정 판본은 구별하고 서로 다른 판본 성공을 합산하지 않는다. 비용캐시는 관측을 evidence에 보존한 뒤 own base로 복원한다. 공식 build_skill_mirrors.py 생성/check와 실제 writes를 확인한다.

전체 일반/fresh T3/변이/T4/T5·유료 공급자/HTTP/native Git/Lean/Job·설치/OS예약은 실행하지 않는다. 원84가족의 나머지25미배정 가족, events/pending_events/event_cursor·tasks/queue, 다른원요구/K/P2·G4~G8·L01·Windows1314·최종review는 별도다. 모든쓰기분기 전건도달을 측정하지 않았다면 완료라고 쓰지 않는다.

report.json에 네 가족의 지정 질문별 충족/제거/정확 남김, 실제 수리와 확인 범위·한계를 남긴다. `python C:/math/services/async-development/check.py report C:/math/.async/dm storage-control-state`를 통과시킨다. 공용 context/plan/seams/queue/state·다른task·engine·Git index/commit·graphify·기존 연구는 수정하지 않는다. manager가 통합·수용과 공용 설명을 맡는다.
