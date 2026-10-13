# P01과 설치 경로 문장 검토

시작 HEAD는 12a751550dc06ac75cdc56058b622d8b621b21cd이다. source-start.json의2640파일과007 source-final의 차이는 모델 정책에 적힌 작문 도구 정본/미러4개뿐이다. do-math 및 서비스 엔진은 시작에 불변이다. start-state.json의 기존 dirty/untracked는 보존했고 Git 상태 변경 명령은 실행하지 않았다. 관리자의007 제품·기억·공용문서 마감은 HEAD 변화이며 제품 소스의 추가 변경으로 세지 않는다.

| 이전 field_schemas 입력 이름 | 실제 문서 소비와 생산자 | 이번 처분 |
|---|---|---|
| checkpoint_source | 운영-점검의 실행 중 증거는 _context.evidence.update; 종료 뒤 복구는 _context.recover의 별도 값 | 단독 이름을 제거하고 두 중첩 소유자를 명시 |
| recovery_source | recover의 정상/오류 dict를 추출해 recovery_materials와 recovered_output_files에 합성한 내부 의존 | 실제 복구 반환을 직접 검사하여 마지막 의존 제거 |
| checkpoint_files | _context.evidence의 근거 파일; 운영-점검에서 local_path 소비 | operational_evidence.checkpoint_files로 결속 |
| recovered_output_files | 운영-점검의 output_files 별칭이 복구 파일을 가리킴 | 별칭을 제거하고 recovery_materials.output_files로 결속 |
| recovery_materials | 종료 뒤 진단; 정상 결과·복구 체크포인트·활동 결과·출력의 복원 성공/오류/null | 실제 _context와 prepare_role_input 반환, 실제 저장 바이트로 검사 |
| operational_evidence | 실행 중/종료 후 checkpoint·근거·activity_continuations | 실제 _context와 포장 반환을 검사하고 명시 후속의 frontier/실행 ID를 확인 |

기존 여섯 AST 호출 지점은 이 입력의 실제 반환 경계로 교체했다. field_schemas의 입력 이름은 operational_evidence/recovery_materials 두 개이며 문서 필드 경로의 첫 이름과 같다. checkpoint_source/recovery_source/checkpoint_files/recovered_output_files는 현 문서·helper·시험에서 독립 입력으로 더 이상 소비하지 않는다. materialized_output_files/results 등 P02의 AST 소비는 유지하며 일반 재개의 result_source/rejected_response/previous_output_files도 그대로다. 삭제 개수는 완료율이 아니다.

## 실제 시험 책임

operational_evidence는 sim.test_role_input_context.OperationalInputTests.test_live_review_receives_exact_checkpoint_evidence_files가 실제 checkpoint·근거 파일과 포장 반환으로 문서 전건의 해당 경로를 확인한다. 정상 바이트·SHA256·크기·snapshot·artifact 읽기를 검사하고, local_path 삭제/해시·크기 교란 사본을 거부한다. live에 recovery_materials가 없고 not_preserved의 checkpoint_source가 null인 분기를 별도로 확인한다. 실제 제품 경계의 hash/size 반려는 반환 후 사본 교란과 다른 검사다.

recovery_materials는 sim.test_knowledge_currentness.RecoveryMaterialTests.test_failed_execution_materials_are_restored_for_its_operational_review가 실제 중단된 공급자 호출의 저장·반환·파일을 확인한다. checkpoint_recovery와 activity_result 기존 경로를 유지하고 정상 formal/인라인 자식의 null, 결과/출력/체크포인트 부재와 출력 해시/크기 오류를 실제 Repository와 _context에서 검사한다. 오류 자료의 local_path 부재와 미검증 바이트 미물질화를 확인한다. 일반 재개의 실제 restore_continuation 반환을 복구 결과에 교환하거나 운영 checkpoint를 복구 결과에 교환하면 거부된다. 운영/복구 입력 전체 교환도 거부된다.

flows.test_knowledge_impact_retry.UnreadableBeforeReviewTests의 실제 운영 모델 입력에서도 복구 문서 필드·파일을 검사한다. 당시 실행의 input_snapshot을 기준으로 하며 이후 engine.head와 혼동하지 않는다. 기존 손상 제출의 정확 오류·단일 소비·후속 진척·지식 불변·재시작 단언을 유지했다.

일반 문서 순회는 두 입력을 defer하고 위 실제 시험이 검사한다. structure.test_doc_code의 책임 대응 검사는 dict 키 두 개와 담당 메서드의 존재 및 해당 owner로 실제 문서 검사 호출을 확인한다. 이름 오기·담당 누락·메서드 부재·문서 검사가 없는 메서드로의 교환은 거부되고, 두 입력 defer가 일반 재개 입력까지 건너뛰지 않음을 확인한다. AST는 여기서 검사 호출 위치를 확인할 뿐 제품 반환 객체를 추정하지 않는다.

doc-code-consumers.json은 기존6시험 모듈과 새 공유 helper(engine_context)를 기록한다. 기존6모듈은 구조·입력 포장·trace report·저장 query·저장 report·CLI이고 모두 공식 최종 선택에 포함한다. manifest/prompt/documents/profile_selection과 일반 재개의 실제 반환·기존 단언은 재구현하거나 삭제하지 않았다. shared-consumers-final에서 끝 인자 및 CLI owner 차집합 형태의 호출에 새 defer가 빠진 오류를 발견했고 해당4모듈의 모든 문서 순회 호출을 고쳤다. canonical-joined-final은 두 지정 묶음 전체를 같은 최종 판본에서 합쳐 검사한 새 근거다. 이전 오류 출력은 보존한다.

## fixture와 기존 실패

첫 focused-01에서 같은 workspace에 _context를 두 번 호출해 입력 파일 중복 오류가 났다. 포장 검사는 새 하위 workspace에서 진행하도록 고쳤다. 추가 정상 시험이 같은 template 저장소의 고정 artifact 경로를 먼저 검증하자 기존 손상 checkpoint 시험이 per-process sealed memo에 의해 실패했다. template은 동일 저장소 경로를 재사용하므로, fixture의 checkpoint artifact 묶음을 호출마다 새 UUID로 만들어 불변 artifact 정체성을 유지했다. 제품 cache를 지우거나 우회하지 않았고 기존 정확한 hash 반려 단언을 유지했다. focused-02의 기존/새 손상 및 정상 포장·실제 운영 입력5개는 통과했다. 이후 null/오류 분기를 추가한 최종 판본에서 다시 검사했다.

지정 구조·문서 입력 검사에서 provider_final.output_contract가 unowned field로 분류되는 기존 공백이 드러났다. 시작 소스 해시는007 종료와 같고, HEAD의 정규화 원문과 당시 helper로 동일한 분류를 재현했다(preexisting-field-failure.json). working 파일은 혼합 개행이므로 HEAD raw와 시작 raw 해시를 동일하다고 주장하지 않는다. callable은 실제 존재한다. 이 표기는 phase006 공급자 설명 절(현재 CLI-실행-계약718행)에 있고, P01 문장만 교정하라는 이번 경계 밖이다. 구조 검사를 완화하거나 제외하지 않았다. 이 실패가 남아 A5는 fail이고 task는 partial이다. manager가 해당 함수 표기/분류의 한정 수리와 실패한 문서 검사들의 새 판본 실행을 배정해야 한다.

## 문서와 설치 설명

운영-점검은 정상 local_path의 존재 조건, available의 경로 선택 의미, restoration_error의 진단 좌표, checkpoint_source=null 및 live 복구 입력 부재를 명시했다. 동일 원 artifact/snapshot 중복 계수 금지, 다른 live 공간으로 보충 금지, 검증되지 않은 바이트의 수학적 수락 금지를 유지했다. CLI-실행-계약은 P01 오류 설명 문장만 맞췄다.

독립-운영의 오래된 LIVE_INSTALLATION_ROOT 한 문장은 operator_bootstrap.main의 manifest.installation_root 또는 snapshot_root 선택과 scheduled_operator.main(..., installation_root=...) 전달로 교정했다. runtime을 바꾸지 않았다. 기존 bootstrap-info의 실제 자식 실행 두 검사가 설치 원경로·고정 manifest와 manifest 부재 실패를 확인한다. 인증·의미·격리의 한계와 고정 사본/live 수리 대상 구별을 유지한다. N03의 나머지 이름 검토는 계속 남는다.

최종 일반/T3/변이/G7 실호출·graphify 갱신·연구 재개/삭제·예약 변경·Git 마감은 수행하지 않았다. 미러·전건 corpus·runtime 보존의 실제 결과는 verification-final.json과 공식 원출력을 따른다.
