# 권한·온톨로지 8가족의 실제 생산과 저장 계약을 연결한다

사용자 목표는 실제 생산값이 검증 켜진 저장소를 통과하고 수신 계약에만 남은 필드나 검증되지 않는 쓰기 분기가 시험을 빠져나가지 않게 만드는 것이다. R01/1-A·1-B 및 K-78의 남은 저장 가족 중 같은 닫힌 스키마와 사용자 결정·종류 등록 생산자를 쓰는 8가족을 한 task에서 판정하고 필요한 구현·시험 수리까지 마친다. 가족별 작은 task나 별도 registry를 늘리는 것이 목적이 아니다.

SESSION_JSON, task.json, inputs/context.md·plan.md·seams.md, do-math AGENTS.md·현행 시험-지침.md를 읽는다. C:/math/docs/do-math/continuous-development-2026-10-13/sources의 user-decisions.md·model-policy-2026-10-14.md·document-batching-2026-10-14.md·requirements-index.json과 C:/math/docs/do-math/시험-재편-2026-09-29/설계.md 3.3절/A20의 required+optional 역방향 조건이 원요구다. tasks/keep-storage/evidence/families.json의 root/family 키를 사용한다. managers/0047/review.md, 수용된 storage-knowledge의 report·families·judgment와 실제 현재 소스가 새 시작 근거다.

## 대상과 완료 판단

- authority 6: research.decisions, research.delegations, research.governance, research.governance_approval, research.governance_sources, research.grants.
- ontology 2: research.kind_definitions, research.relations.

1. 각 가족의 현재 shape·정본 checker/validator·실제 producer와 Repository 저장 caller를 연결한다. governance_approval은 등록 shape가 singleton이어도 schema는 boolean/object이므로 빈 properties를 빈 pair로 통과시키지 않는다. relations는 list의 실제 item, kind_definitions와 다른 map은 record를 검사한다. 기존 표의 구식 분류나 AST 이름만으로 결함을 세지 않는다.
2. 필수·선택 전 필드의 실제 생산값이 설치된 StateContract/Repository의 검증을 거쳐 저장·load되는지, 수신 필드마다 실제 작성 분기와 정확 단언이 있는지 확인한다. 실제 공개/도메인 생산자가 충분한 기존 시험·수용 원보고가 있으면 해당 성질만 재사용한다. schema fixture·문자열 출현·저장 직전 필드 사후 주입은 생산 근거가 아니다. 권한 원문/승인/범위/현재성·봉인·관계 endpoint·예전 head 보존을 약화하지 않는다.
3. governance.preserve_source/initialize_governance/_install_record/apply_decision/normalized_grant와 현재 호출부를 읽는다. 실제 사용자 원문과 정확 승인 hash, 선언 설치/명시 supersession, grant 발급·교체·취소, 원결정에 대한 delegation 생성/철회가 만드는 필드를 구별한다. 권한이 없는 초기값·승인된 값과 실제 반려를 독립 기대값에 연결한다. r12-r13-fix가 이미 확인한 공개 원결정→위임→두 독립 판단→교체/저장/restart와 r06-finish/r22-snapshots의 현재성·구조 공유는 필요한 부분만 재사용하고 같은 긴 여정을 새로 반복하지 않는다. delegation_applications/intent_imports 자체의 전 필드 질문은 이번 모집단에 다시 넣지 않는다.
4. knowledge_io.ensure_ontology/register_kind_definition/check_kind_definition/activate_kind_definition/withdraw_kind_definition/import_relation과 validate_stored_relation/validate_relation의 현재 생산·수신을 연결한다. builtin과 실제 사용자 등록, 검사/승인/철회 및 재등록 계보, 수학적 관계와 일반 관계·독립 두 endpoint·실제 evidence가 쓰는 필드를 확인한다. 원래 해당 유한 선택지·관계0/1/여럿·선택필드 있음/없음을 필요한 생산 분기에 연결하며 전 입력 Cartesian 곱이나 옛 API를 새 의무로 만들지 않는다.
5. 실제 빠진 표본·단언은 기존 direct producer/저장 시험 또는 새 전용 storage_authority_pairs helper와 계약시험에 묶어 보완한다. 수용된 contracts.pairs.assert_pair(case,pair,samples)의 순방향/역방향 검사를 재사용한다. shape에 맞는 fields/written/receive를 구성하고 최소 하나의 미생산 optional 추가 반례가 같은 역방향에서 드러나도록 한다. 형식상 열린 값에는 닫힌 field 의무를 임의로 만들지 말고 실제 내용·원bytes·관계의 저장 보존을 확인한다.
6. 실제 생산자가 없는 optional field나 생산/수신 불일치를 발견하면 배정된 provider/schema/consumer와 설명을 같은 task에서 고친다. 표본 부족과 현행 미생산을 구별하고, 정상 값을 schema에서 지워 시험을 통과시키지 않는다. 구판 자동변환·기본값 보충·검증 우회는 추가하지 않는다. storage-knowledge가 제거한27필드와 begin/activation의 정본 basis_record 수리, state/10·SOURCE/restart·review 결말·게시 뒤 stop은 보존한다.
7. 8가족의 의미 대응 완료와 모든 실제 쓰기 지점/분기 도달은 별개다. 해당 producer/쓰기 anchor·현재 AST/SHA와 기존 근거를 남겨 최종 fresh T3에서 대조할 수 있게 한다. 이번에는 전체 T3를 실행하지 않는다. 나머지53 미배정가족, 진행 중 실행4가족, 관찰4가족의 최종판 증거를 이 결과로 닫지 않는다.

## 쓰기 소유와 독립 실행

제품 수정은 자기 workspace의 task.json.writes뿐이다. 중앙 record_schemas/schemas.py·__init__.py와 정본 설명은 이 task가 소유하되 위 8가족에 필요한 변경으로 한정한다. 같은 파일을 쓰는 다른 새 저장 task를 동시에 배정하지 않았으므로 알려진 필드 제거를 별도 작은 task로 넘기지 않는다. 실제 정의를 좁혀 확인하고 해당 schema 정의를 보존한 채 관계없는 가족을 수정하지 않는다.

storage-execution은 자기 시작판에서 계속 실행 중일 수 있다. 그 task의 activities/execution_lifecycle/execution_window/session_slots/provider_wait/provider_engine/core_engine/call_engine/scheduler/scheduled_operator/repair_execution과 전용 시험/helper는 읽기 전용이다. 미수용 workspace를 읽거나 그 종료를 기다려 구현하지 않는다. 공유 쓰기는 비용캐시뿐이며 own base 복원 정책을 적용한다. 해당 읽기 전용 제공자 변경이 실제로 필수이면 정확 입력·관측·최소 변경 소유를 report에 남기고 독립적인 나머지 범위를 마친다.

일반 Pair와 storage_records/storage_knowledge_pairs 등 기존 저장 helper는 소비할 수 있다. 새 등록체계를 만들거나 거대 fixture를 복제하지 않는다. 목록에 포함된 직접 시험·helper는 필요한 부분만 바꾼다. C:/math 공용 source·공용 context/plan/seams/queue/state·다른 task·engine·Git index/commit·graphify·기존 연구는 수정하지 않는다. 제품의 정본과 허용된 미러는 같은 작업에서 공식 생성한다.

## 최소 확인과 제출

정적으로 충분한 항목은 읽기로 끝낸다. 실제 수리 검증은 자기 workspace의 공식 scripts/run_tests.py --jobs 1로 가장 작은 관련 ID를 선택한다. 이번 시험 슬롯은 storage-execution과 이 task의 둘이며 둘 다 jobs1이다. 다른 task의 결과 수용을 자원 조건으로 추가하지 않는다. 전체 일반/fresh T3/전체변이/T4/T5·대형 저장 비용·새 native Git/Job/Lean/공급자/설치/OS예약 실행은 하지 않는다. Git·clock·host·모델/컴파일러 대역과 실제 domain/engine/Repository/StateContract 경계를 구별한다.

기존 실패는 보존하고 fixture 준비 오류·제품 실패·교정 성공을 나눈다. 실행 중 소스를 수정하지 않으며 선택/실제 고유 row/counts/fixture_counts/관측 exit/소스 SHA/changed_during_run을 보존한다. 서로 다른 판본의 부분 통과를 최종 단일 실행으로 합산하지 않는다. 필요한 확인 뒤 같은 검사를 반복하지 않는다. 비용캐시 관측은 evidence에 보존한 뒤 own base로 복원하고 공식 mirror check와 변경경로를 확인한다.

evidence는 기존 family 표 중 대상8행과 정확 생산/수신/쓰기/시험 참조만 확장한다. 각 가족의 완료된 성질, 수리 이유, 재사용 원보고/판본, 정확 남김을 기록하고 새 관리체계나 남은 전체61/88행 복제는 만들지 않는다. report.json은 protocol의 status/summary/changes/verification/findings를 갖추고 `python C:/math/services/async-development/check.py report C:/math/.async/dm storage-authority`를 통과시킨다. manager가 통합·수용 및 공용 설명을 갱신한다. G4~G8·다른 원요구/K/P2·L01·Windows1314와 최종 review는 별도 남김이다.
