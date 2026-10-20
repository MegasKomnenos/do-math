# 질문·원자료 연결·이력·입력 초과의 저장 네 가족을 마친다

사용자가 질문의 원문과 해소 대상을 보존한 채 입력 초과를 처리할 수 있도록, runtime.question_links/questions/history/input_overflows 네 가족의 실제 생산·검증 게시·새 reader decode·내용/필드 대응을 완성한다. 같은 질문/제어/입력 준비 경계의 필요한 구현·직접시험·설명·미러 수리를 한 task에서 마친다. 목록 조사만 하고 수리를 다음 task로 넘기지 않는다.

SESSION_JSON, task.json, inputs/context.md·plan.md·seams.md, `.claude/skills/do-math/AGENTS.md`·scripts/tests/시험-지침.md를 읽는다. 사용자 결정과 모델/묶음 지시는 C:/math/docs/do-math/continuous-development-2026-10-13/sources의 user-decisions.md·requirements-index.json·model-policy-2026-10-14.md·document-batching-2026-10-14.md다. 원요구 R01/1-A·1-B/K-78, phases/001/tasks/closure-map/evidence/requirement-state.json, C:/math/docs/do-math/시험-재편-2026-09-29/설계.md 3.3/A20을 따른다. 읽기 전용 근거는 C:/math/.async/dm/tasks/keep-storage/evidence/families.json의 같은 root/family, managers/0059/review.md와 queue.inputs에 지정한 수용 보고다. 과거 표의 설명을 현재 writer 대신 쓰지 않는다.

## 지정 질문과 완료 판단

1. question_links는 list item이다. questions.link/close/resolve_user와 QuestionEngineMixin._record_output_questions/_record_review_questions/_apply_question_resolutions의 실제 생산을 사용한다. origin_execution_id·origin_field·source_ref 또는 source_kind/source_id, owner/blocks/checked_by, 중복 없는 target_ids와 미해소 target 순서, status/resolution_ref/해소이력을 원 output·제어 결정·실행·정확 affected_ids에 대조한다. 처음 생성, 같은 원자료 재전달, 일부/마지막 대상 해소, 허용된 AI/사용자 해소의 충분한 기존 장면을 재사용한다. 사용자 질문을 AI가 해소하거나 잘못된 owner/대상으로 조용히 바꾸지 않는 기존 반려를 유지한다.
2. 질문 원문은 원 result artifact·intent import·review cycle·history에 있고 question_view가 pointer로 읽는다. 저장 링크와 원문/UTF-8 내용·순서·null/부재의 관계를 새 reader의 검증된 head에서 확인한다. 원자료를 읽을 수 없을 때 반환하는 text=None/source_status=unavailable는 view 의미이며 저장 root 필드로 추가하지 않는다. source_kind/source_id/question_kind 등의 선택필드가 실제 어느 writer에서 나오는지 확인한다. 한 helper 표본에 없다는 이유로 전체 미생산으로 제거하지 않는다. 닫힌 schema를 실제 생산자의 필수·선택 필드와 공통 Pair/assert_pair 역방향에 연결한다.
3. questions는 array(TEXT) singleton, history는 열린 HISTORY singleton이다. _check_installation의 중복 없는 안내문, 실제 실패/제어/입력 처리의 원문과 이력 중 필요한 독립 표본을 검증 저장·새 decode·옛head 불변에 연결한다. 원배열 순서·원문·원사유/실행/요청 좌표를 독립 기대값으로 확인한다. 빈 properties를 검사한 것만으로 내용 검사를 대신하지 않고, 열린 이력의 임의 키를 닫힌 필드 의무로 만들지 않는다. 실제 설치를 변경하거나 외부 모델을 호출할 필요 없이 기존 fixture 경계에서 생산한다. 같은 이름의 output.questions·review-cycle 내부 질문과 이 runtime singleton을 혼동하지 않는다.
4. input_overflows는 action/detail/source_catalog를 가진 닫힌 item 배열 singleton이다. CallEngineMixin._prepare_call의 실제 입력 포장 초과를 사용한다. 일반 질문/보류 분기와 identity_review의 현재 제안/필수원자료 초과 분기는 서로 다른 처분이다. 원 action/owner, detail 원인·한도/프로필 후보·해소 질문, 원 source manifest를 저장된 내용 및 보존 artifact와 연결한다. 기존 support.engine_overflow와 flows.test_engine_input_recovery/test_review_overflow_evidence 등의 충분한 장면을 재사용해 재시도/교체 질문과 원이력 보존을 확인한다. _ACTION은 queue/executions 등과 공유하므로 특정 가족 표본의 부재로 공통 필드를 제거하지 않는다. storage-actions/recovery의 최신 수용 계약과 가까운 소비자를 함께 보존한다.
5. 실제 저장을 막는 불일치와 충분한 근거가 없는 수신 필드를 구별한다. 필요한 provider/consumer/schema/직접시험·공유 정본 설명·미러 수리를 함께 마친다. current producer 전체를 읽고 미생산이 확인된 슬롯만 제거하며, 실제 writer를 삭제하거나 필드 수동 보충·구판 호환·범용 fallback으로 시험을 통과시키지 않는다. 제거한 슬롯은 정확 반려 사유와 head 불변을 확인한다. 기존 helper의 실제 준비를 공통화해야 한다면 기존 소비자도 같은 정본으로 옮기며 별도 registry/역방향 알고리즘을 만들지 않는다.

## 범위와 선행

직접 선행은 storage-recovery 하나다. 그 task와 storage-actions가 core/call/중앙schema/저장 직접시험/공유 설명을 수정하므로 통합된 시작판을 받아 동일 파일 충돌과 낡은 계약 소비를 피한다. storage-ontology-fix는 제품 동작의 새 선행이 아니며 이미 통합된 공통 Pair/helper를 읽기 전용으로 소비한다. 기존 두 배정은 바꾸지 않는다. writes의 자기 workspace에서만 수정한다. 의존 producer를 읽는 권한과 수정하는 범위를 구별하고, 범위 밖 결함이면 정확 파일·심볼·영향·작은 반례를 보고한다.

이번 네 가족과 직접 연결된 기존 R39 질문 원문/부분해소 근거는 재사용한다. r08에서 남긴 특정 review-cycle 종료/task_ready·공개 record 삭제 의미는 이번 실제 경로가 직접 답하는 범위만 기록한다. 가상 del이나 옛 API 복원으로 채우거나 별도 전수 조사로 확장하지 않는다. tasks/task_observation_rules/checkpoints/external_operations 및 research.capability_evidence/review_policy 여섯 가족은 이번 대상이 아니다. 공용 원84 가족 중 이 네 가족 질문 완료와 모든 쓰기분기 fresh T3/최종판 관문은 별개다.

## 필요한 확인과 보고

기존 코드/원보고로 충분하면 해당 성질을 재사용하고 실제 남은 저장/내용 연결만 자기 workspace 공식 run_tests.py --jobs 1의 최소 관련 ID로 확인한다. public producer → schema 검증 게시 → 별도 ResearchRepository/설치 contract의 첫 decode를 거쳐 저장 전 값을 보충하지 않는다. 새 독립 기대값을 생산 함수와 같은 계산으로 만들지 않는다. 공식시험 총worker3 이하, source 고정, 소프트 시간 기준을 유지한다. 전체 일반/freshT3/변이/T4/T5·실provider/Lean/HTTP/native Job/설치/OS예약은 이 배정이 아니다.

원실패·교정판·selected/고유실제row/counts/fixture·실제 exit·source SHA/changed_during_run·소프트 초과를 보존한다. 공식 build_skill_mirrors.py 생성/check 후 비용캐시는 관측을 evidence에 보존하고 own base로 복원한다. report.json에는 네 가족 각각의 실제 producer/receiver/내용 단언·수용 범위와 남은 질문을 설명한다. 변경과 관련 확인을 마치고 `python C:/math/services/async-development/check.py report C:/math/.async/dm storage-questions`를 통과시킨다. 공용 source/context/plan/seams/queue/state·다른 task·engine·Git index/commit·graphify·기존 연구는 수정하지 않는다.
