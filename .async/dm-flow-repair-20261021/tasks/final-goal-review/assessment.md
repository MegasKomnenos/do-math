# 최종 목표 대조

리뷰 배정은 완료했다. 전체 역할과 주요 인계의 구현, 공통 검사·해시·복구, Windows/패치 안내, Codex 진단, 정확 snapshot 조회 개선은 아래 범위에서 확인했다. **프로젝트 전체 완료는 작은 문서 수리 뒤에 판단할 것을 권고한다.** 실제 후보 준비 프롬프트에 지급되는 학술 과제 설명이 현행 코드와 다른 F1 한 건이 남아 있다. 실행기가 옛 삭제·재준비 동작을 계속한다는 결함은 확인하지 않았다.

이 리뷰는 제품을 수정하지 않았다. `report.json.status=complete`는 리뷰 수행 완료를 뜻한다. 최종 수용·프로젝트 상태 게시·후속 배정은 manager의 책임이다.

## 판단 기준과 판본

- `inputs/context.md`, `plan.md`, `seams.md`, `task.json`, `objective.md`, 서비스 `protocol.md`, `RECORDS/user-messages.md`의 최신 정정을 읽었다. R4는 같은 판단과 같은 의미의 입력을 한 구현에서 공유하라는 요구로 평가했다. 이전의 클래스 계층 제안이나 설계 필드 수를 완료 조건으로 삼지 않았다.
- 아래 `D/`는 이 리뷰 workspace의 `.claude/skills/do-math/`, `M/`은 그 `scripts/do_math/`다. `R/`는 `C:/math/.async/dm-flow-repair-20261021/`다. 공식 사본은 workspace의 `.agents/skills/do-math/`다. 제품 AGENTS, 이음새 정본의 원칙·관련 공유 정의·마지막 수리 절, 시험 지침의 실행/판정/변경/최소 검증 규칙을 읽었다.
- 공용 `C:/math/docs/do-math/flow-repair-20261021/`의 배정된 결과 문서 8개를 안내로 사용했다. 역할 설계는 전체 모집단 표·형식/재량 판단·주요 인계 절을 읽고 현재 코드로 대조했다. 설계 당시의 미구현 제안이나 당시 잔여를 현재 결함으로 옮기지 않았다.
- `integration-repair-check`의 원 공식 보고 4개와 manager 0008의 판단·검증 자료를 대조했다. 직접 작성·실행한 읽기 전용 `evidence/audit_evidence.py`와 결과 3개 JSON에 판본·행/선택·원자료 대조·F1 발췌를 남겼다. 새 제품 시험·모델·Lean 호출은 하지 않았다. 구체적인 발견은 정적으로 충분히 확인된다.
- 정리 후 현재 소스가 필요하면 `python C:/math/services/async-development/workspaces.py restore RECORDS final-goal-review baseline NEW_DIRECTORY .claude/skills/do-math .agents/skills/do-math`로 복원할 수 있다. 이 리뷰는 제품 순변경이 없으며 시작판이 판단한 판본이다.

## F1 — P2: 학술 과제의 근거 대기를 평가·관찰 규칙 재준비라고 지급한다

**위치:** `D/계약/후보-준비.md:214`. 같은 문장이 공식 미러에도 있다. 관련 과도한 일반화는 `D/references/모델과-실행예산.md:68`, `D/references/CLI-실행-계약.md:144`에도 있다.

후보 준비 계약의 「기존 과제의 평가와 관찰 규칙을 보충하는 실행」은 이 절을 유일한 정본이라고 지정한다. 그런데 214행은 학술 과제가 `revision_required` **또는 `unresolved`**를 받으면 평가와 관찰 규칙을 다시 준비시키고, 이전 두 값을 history에 보존해 현행에서 분리한다고 설명한다. 이것은 수리 전 동작이다. 단순 표현 취향이나 옛 개발 기록의 문장이 아니다.

**대조한 현재 동작:**

1. `M/core_engine.py:3434` 이하의 unresolved 분기는 `contract_review_input`, 질문 범위, 읽은 영수증 basis, 같은 계약 SHA를 보존한다. `revision_requested`를 만들거나 평가·규칙을 삭제하지 않는다.
2. `M/planning_engine.py:106`의 `_ensure_model_assessments`는 현재 개정 요청이 있고 최신 검토가 `revision_required`인 경우만 반려 필드를 처리한다. `revision_fields`의 `contract`면 사용자 원 계약을 보존하는 일반 개정 요청 처리로 넘긴다. `model_assessment`와 `initial_observation_rules`는 각각 지적된 경우에만 분리한다. 모든 비승인에서 두 값을 일괄 지우는 규칙이 아니다.
3. 현행 `D/scripts/tests/flows/test_academic_preparation_calls.py:264`의 `test_rejected_rating_is_preserved_and_replaced_by_assessment_only_request`는 뒤의 unresolved 대조군에서 기존 평가·규칙 유지와 두 history 미생성을 직접 단언한다. 이 ID의 마지막 저장 결과는 `integration-repair-check/evidence/boundaries-and-recheck/report.json`의 passed다. 이 리뷰가 재실행한 결과는 아니다.
4. `D/SKILL.md:153`은 후보 준비에 해당 계약과 「모델과 실행예산」을 지급한다. `M/contracts.py:332`의 `_document`/`prompt_documents`, `render_prompt`는 해당 파일 전문을 읽어 프롬프트에 넣는다. 따라서 읽히지 않는 참고 문서의 문제가 아니다. 계약 검토도 예산 문서를 받는다. 계약 뒤의 새 일반 예외 설명은 앞의 구체적 학술 보충 설명을 명시적으로 대체하지 않으므로 둘을 동시에 읽게 된다.

**발생 조건과 영향:** 학술 과제의 검토가 자료 부족으로 unresolved이거나 평가·규칙 일부만 실제 수정 대상으로 돌아왔을 때, 역할과 운영자는 지급 설명에서 불필요한 재준비·기존 값 삭제가 정상 후속이라고 이해할 수 있다. 이는 R1의 역할 책임·인계와 '같은 현행 계약' 완료 조건에 직접 관련된다. 현재 엔진의 올바른 gate가 임의 삭제를 막는다는 반대 근거는 인정한다. 새 live 모델이 실제로 이 문장을 따라 연구를 다시 막았다는 관측은 없다. 그런 재발을 주장하거나 코드 수정·대규모 회귀의 이유로 확대하지 않는다.

**최소 후속:** 후보 준비 214행을 현재 세 분기(실제 수정 필드의 보충, 원 사용자 계약 요청의 별도 처리, unresolved의 질문 근거 대기)에 맞게 교체한다. 이를 가리키는 「모델과 실행예산」 68행과 CLI 144행의 일반화도 같은 의미로 좁힌다. 「작업 계약 검토」 143행은 뒤의 151~153행과 충돌하지 않도록 이 구분에 맞춰 함께 읽어 정리할 수 있다. 정본 문서와 대응 공식 미러를 한 작은 work에서 마무리하면 된다. 기존 학술 흐름 코드나 schema를 옛 설명에 맞춰 되돌릴 이유가 없다. 확인은 실제 수정 문구의 프롬프트 지급과 공식 미러 검사에 한정할 수 있다. 런타임을 바꾸지 않으면 전체 T2/T5를 다시 실행할 이유가 없다.

## R1 — 역할 전체의 적합성: 구현은 확인, 지급 계약에는 F1 잔여

모집단은 `M/contracts.py:ROLES`, `action_schema`, SKILL 읽기 대응표, `M/core_engine.py:_context/_apply`, 동적 review/governance 경로에서 확인했다. 내부 AI 열 역할을 모두 대조했으며 동일성 scope나 의도 check를 새 독립 역할로 세지 않았다. 역할마다 목적·입력·판단·출력 소비·재량을 확인한 범위는 다음과 같다. 계약 문서의 목적/입력/판정/실패·후속 관련 절을 읽은 것이며 모든 산문 예시나 모든 수학 판정의 정확성을 인증한 것은 아니다.

| 역할·변형 | 현재 책임과 실제 소비 | 유지·변경 판단 |
|---|---|---|
| 후보 준비, 평가/관찰 보충 | 계약 저작은 `_apply(research_preparation)`의 완전 계약 교체·새 검토로, 좁은 보충은 `planning_engine._finish_assessment_preparation`으로 간다. 선택·승인을 대신하지 않는다. | 저작/선택 분리와 조사 과제 제안 재량은 적합하다. 실제 필요한 산출만 의존하게 한 지침도 목적에 맞는다. 학술 보충 설명 F1은 수리 필요. |
| 연구 계획 | ready 전건 선택·미선택·판정 불가, returned 전건 완료 집계는 `planning.validate_plan_submission`, `decision_engine._apply_task_plan`, `task_scope.apply_task_assessments`가 소비한다. | 후보 저작이나 전문 판정의 대행을 막고 open/unresolved·권위 있는 면제/이전을 보존한다. QU 연구 child의 준비·결과 판단도 실제 사건으로 연결된다. |
| 연구 수행 | 선택된 계약에서 방법을 선택하고 실제 범위·부분 결과·실패를 반환한다. `_apply`가 results와 지식을 보존하고 다음 계획을 연다. | 도구 노출/호출의 실제 확인과 지원 실패 보고를 수행 책임으로 명확히 했다. 과제 완료·형식/동일성·목표 판정과 분리는 필요하다. |
| 작업 계약 검토 | 질문·범위·입력·산출/판정 가능성을 독립 판단한다. 다섯 항목의 정확 피복은 `contracts.contract_review_decision`, 현재성/독립성은 seal·decision 경계가 확인한다. | 지적 전에 실제 원문·반대 근거·자기 오독을 확인하며 위치/영향을 설명한다. 미래 도구 성공이나 연구 결과의 사전 입증을 요구하지 않는다. 실제 허가 부재·확인된 필수 능력 미지원은 계속 지적할 수 있다. |
| 동일성 scope/initial/organize/answer/judge, 재심사 | `review_engine`, `review_cycle.stage_schema/accept_result`가 고정 제안·자리·쟁점·응답·판정·효력을 소비한다. | 이의 maintain/revise/split/withdraw, 이의 기각과 전체 판정의 구별, 한도/미응답과 의미 판단의 분리는 이미 유효한 재량이다. 다른 역할에 이 전체 절차를 복제할 이유가 없다. |
| 목표 감사·추가 감사 | `governance_engine._apply_governance_goal_audit`가 목표 기초·독립 slot·현재 유효 결과·추가 감사를 집계한다. | 부분 결과와 목표 해결, 수학 해결과 학술 후속을 구별한다. 질문 해소나 한 실행의 satisfied를 전체 해결로 쓰지 않는다. |
| 과제/고정 질문 보충 조사 | 일반 과제는 연구 결과 편입 경로, 고정 조사는 `review_engine._apply_review_research/accept_research_result`를 통해 같은 검토 자리로 돌아간다. 실패도 `_abandon_review_research`가 원 질문·미완료 범위를 보존한다. | 고정 질문·원자료·독립성·상위 한도와 중첩 확장 금지는 실제 실익이 있다. answered는 상위 승인과 다르다. |
| 운영 점검 live/종료 후/question | 실제 EX와 admissible 근거를 읽고 여섯 disposition을 `_apply_operational_disposition`이 소비한다. 대상 종료·예약·복구/설치 관문은 별도다. | 지정 판정 집계와 새 수학 판정 발명을 구별했다. 주기 점검과 질문 handler의 목적을 분리하고 EX 없는 질문은 maintenance에 맡긴다. |
| 의도 interpret/check/위임 | 원문·단위·소비자·고정 묶음을 `governance`와 `_apply_governance_intent`가 소비한다. 위임 판단은 별도 소비자다. | 의미 피복·독립 검사·명시 승인·owner 적용은 필요하다. unresolved의 재저작 대신 근거 대기를 연결한 변경도 적합하다. |
| maintenance 일반/초기 진단/종류/impact/question | 동적 `action_schema`, 초기 진단·종류 판정·독립 영향 검사, QU 처분이 각각의 소비자에 연결된다. | 대상·권한·성공 조건이 없는 범용 수리 권한을 만들지 않았다. 실제 subject·보고·고정 scope의 질문 판단을 추가한 범위가 적절하다. |

내부 역할 밖도 확인했다. formal_check/trust_check/trust_activate/external_action은 기계 action이며 모델 역할 열 개와 구별한다. `D/계약/독립-운영.md`의 감독은 모델 없는 HOLD/pause/lock/wake 관문이다. 실제 별도 recovery 지시는 `M/repair_execution.py:repair_prompt`에 있으며 재현·최소 설치 수리·검증과 연구 기록/권한/예약 변경 금지를 명시한다. `recovery_held`도 사용자 정지/HOLD를 해제하지 않는다. 이 모집단을 '열 역할 프롬프트 확인'에 포함했다고 주장하지 않는다. 실제 외부 복구 AI의 수리 성공은 새로 실행하지 않았다.

common은 SKILL·GLOSSARY·공통 실행·지식 저작·학술자료 활용이고, 역할별 추가 문서는 `reading_map/prompt_documents`가 한 표에서 선택한다. `_context.scholarly.availability`, 학술자료 활용의 첫 확인 절, 계약 검토의 타당성 절, 연구 수행의 지원 실패 절은 같은 책임 경계를 설명한다. 형식적 다섯 항목 피복은 누락을 막는 장치이며 미래 연구 성공을 입증하는 새 보편 승인 관문으로 바뀌지 않았다.

## R2 — 정상 처리와 예외 재량: 확인한 범위 충족

`M/revisions.py:resolution_schema/submission_errors/resolved_targets/remaining_targets`가 처분 의미를 소유한다. 실제 revised는 저작을, 필수 요청의 예외 dismissed는 AI 출처·근거·이유를 요구한다. optional unchanged와 달리 사용자 revise를 기각할 수 없으며 `capture_targets/user_revision_sources`, 바인딩/병합/저장 검사에서 실제 사용자 결정 참조를 보존한다. deferred/delegated는 의무가 남아 있는 처분이다.

`revision_engine._apply_revision_followup`은 해당 출처만 정산하고, 유효 승인이 필요하면 `_request_contract_reconsideration`이 같은 계약·기초의 새 독립 검토를 한 번 연다. 반복 충돌은 decision_conflict QU와 자료 대기다. `planning.revision_required`는 과거 비승인의 OR가 아니라 현재 요청이며, `effective_contract_review`는 마지막 유효 검토를 판단한다. lifecycle/task_ready가 같은 정의를 소비한다. 기각이 승인·수학 해결로 변환되지 않는다.

통합 추가 수리인 `resolved_targets(...,consumer_targets=...)`를 부모 후속, 자동 실패 정산, 명시 action 해소가 사용한다. 선택적 자식 unchanged가 필수 부모를 지우지 않고 실제 revised는 해당 의무를 정산한다. 원장·사용자 권위·다른 출처를 지우는 지름길은 없다. 저장 보고의 실제 필수 부모 보존·재적재와 순수 반례 ID는 `evidence/edition-and-reports.json.reviewed_flow_observations`에 있다.

개정 외에도 연구 보고→계획 완료 집계, 형식 결과→동일성→K 사용→목표 감사, 고정 조사→원 자리, 사용자 질문→원문 해석/적용 결정, 운영 retry/resume→실제 종료/예약 반환, 설치 repair→검증/launcher, 외부 unknown→권한/영수증, 목표 종료→남은 의무 정산을 대조했다. 정상 결과에 새 일괄 의심·반려 절차를 추가한 것으로 보이지 않는다. 모든 분기를 독립 실행한 것은 아니며, 현재 관련 생산/소비 코드와 기존 통합 근거에 의한 판단이다.

## R3 — 운영 질문의 실제 처리와 후속: 확인한 범위 충족

`questions.link`는 descriptor의 `obligation_key`/명시 QU와 origins를 보존한다. 문장 해시를 모든 의미 중복의 판별자로 쓰지 않는다. 같은 관찰의 재보고와 새 대상·근거 있는 재발을 구별하고, 원문의 보고 수 증가는 live 입력을 바꾸지 않는다.

`core_engine._apply_bundle_candidate`의 같은 후보에서 질문 등록·처분 뒤 `_reconcile_question_actions`가 호출되고, owner upkeep/첫 갱신도 같은 함수를 사용한다. 기본 maintenance:question 또는 실제 EX의 operational_review:question에 고정 generation·target_ids를 결박한다. `_register_execution`이 실제 EX/activity를 handling에 연결한다. 단순 담당 이름이 배정으로 취급되지 않는다.

`question_engine._apply_question_resolution_candidate`는 배정 scope와 실제 근거를 확인한다. 뒤에 도착한 대상·읽지 않은 같은 대상의 새 관찰은 늦은 해소가 닫지 않는다. resolved는 해당 범위만, superseded는 같은 owner의 실제 열린 수신자와 replacement 사슬, waiting/transferred는 실제 child/record/time/OD·다른 운영 action에 연결한다. 물리 종료·held 예약 반환 뒤에 후속을 연다. `_resolve_execution_evidence`와 `submission.resolve_output_evidence`는 이번 봉인 output_files의 artifact_ref/SHA/bytes를 실제 reader로 대조하며 임의 타 실행 workspace를 인용할 수 없다.

`_advance_question_dependents`, `_resume_contract_review_waits`는 고정 소비 범위의 해소와 읽지 않은 영수증/실제 basis 변화로 계약 검토·deferred 준비·연구 계획·부모 handler를 잇는다. QU 전체 status나 기존 영수증 존재만으로 무한 재검토하지 않는다. 질문 close는 승인·개정 이행·완료가 아니다. pause/HOLD·기존 lifecycle/권한 관문도 남아 있다. pause 중 새 triage 미시작·재시작/다른 보고·고정 scope·실제 운영 OD·사용자 child·봉인 근거·후속 선택은 저장된 `flows.test_governance_question_flow`, 관련 sim/저장 소비 근거에 있다.

의도 check도 실제 소비한다. `governance_engine._wait_import_check_evidence`는 같은 import_id·원문/묶음/검사 SHA와 검사자가 읽은 snapshot의 scope/receipt/content basis를 보존한다. `_resume_import_check_waits`는 이전 검사 수락·종료·예약 반환 및 새 근거를 확인하고 한 action을 만든다. `governance.import_check_release/validate_import_checks/check_import`는 해소 기록·실행 continuation 계보·저자/이전 검사와 독립성·현재 근거를 확인한다. `import_seal`은 check/history를 제외해 원 묶음 SHA를 보존한다. 초기화·일반 입력은 같은 경로를 쓰며 명시 승인·owner 적용·위임 독립 판단·정지 해제는 별개다. 네 의도 flow의 실제 저장 결과와 봉인 변조/계보 반례 단언을 읽었다.

닫힌 저장 schema와 첫 reader는 `M/record_schemas/schemas.py`, `record_schemas.__init__.validate_semantics`, `questions.validate_state`에서 실제 action/EX/receipt·출처·고정 scope를 검증한다. retention도 이 참조를 보존한다. 필드 보충/구판 자동 변환을 새로 요구하거나 사용하는 경로는 이번 수리에서 확인하지 않았다.

## R4~R5 — 공통 판단·입력·해시·실패 복구: 확인한 범위 충족

`context_store.prepare_role_input`은 비교 과제의 content_sha256을 보존하고 전체 검사 tasks에는 원장 `knowledge.content_hash`를 넣는다. 결과 복원의 local_path/source_ref를 다시 해시하지 않는다. `planning.validate_plan_submission`의 저장 과제 투영은 content_sha256만 새 객체에서 제외하고 원 catalog를 바꾸지 않는다. 따라서 정상 평가와 필수 이전 해시 검사를 모두 유지한다.

생산자 설치 검사/중앙 접수의 `submission.payload_issues`와 preview/적용은 `integration.inspect_bundles`를 사용한다. 기존 mutation 대상 부재, 검사 입력의 해시 부재/손상, 제출 previous_hashes 누락/불일치(추가 선언 포함)를 구별한다. `_missing_previous_hashes`를 고정/live 경계가 함께 사용한다. live `bundle_impact_request`는 올바른 고정 선언 뒤 현재 원장과 비교해 실제 변경만 CurrentnessChanged로 낸다. 권한·정지·효력·출처·영향 독립 검사·후보/저장 CAS는 각 위치의 추가 검사로 남는다.

`integration.apply_bundles/failure_kind/submission_outcome`, `core_engine._receive_submission/_hold_submission_input_failure`는 출력 결함→bounded 수리, 실제 변경→refresh, 깨진 검사 입력→운영 진단, 환경/게시 실패→엔진 대기를 소비한다. stage 이름만으로 일반 ValueError를 currentness_changed로 바꾸지 않는다.

원 해시 누락 응답의 보존 원자료 네 파일은 이 리뷰에서 길이·SHA를 다시 비교해 모두 일치했다. 선행 audit-replay의 baseline premises_changed, 깨진 문맥 input_failure, 올바른 catalog에서 원 제출 output_rejected, 정확 reader hash의 공통 검사 통과, 실제 live 변경의 별도 premises_changed를 읽었다. 이것은 원바이트의 공통 검사 재현이며 과거 응답 전체를 현재 schema로 실제 적용한 성공과 구별한다. 현재 생성 입력/실제 수신 선택과 영향 fixture의 후속 통과도 기존 기록으로 확인했다.

## R6 및 R7.1 — Windows/패치 예시의 실제 지급: 확인한 범위 충족

`D/references/공통-실행.md:51`은 PowerShell LiteralPath/호출 연산자/분리 인수, cmd 자체 문자열과 바깥 프로세스 호출, JSON wire와 해석 후 문자열을 구별한다. 한 파일 한 Update에 여러 hunk를 모으고 거부 뒤 재독·수정 재제출·성공 뒤 재독하도록 한다. 내부 열 역할은 기존 common 지급으로 이 전문을 받는다.

`windows-patch-guidance/evidence/tool-probes.json`, `cmd-raw-probes.json`, `prompt-delivery.json`의 실제 무해 명령·거부/성공/재독·정본/미러 20 프롬프트 결과를 읽었다. 직접 cmd wrapper 시도 중 실패한 것과 raw cmd/PowerShell 경유의 성공을 구별해 남긴 근거다. 현재 셸 명령 실험은 반복하지 않았다. 미래 모델 준수, 확보하지 못한 과거 패치 본문·wrapper argv, recovery 고정 프롬프트 전건까지 인증하지 않는다.

## R7.2 — 목록 갱신 진단과 한계: 확인한 범위 충족

`codex_stream.stderr_diagnostics`는 인식한 CLI 목록 timeout의 종류·CLI 보고 시각/수준·원 stderr 바이트 좌표만 색인한다. `codex_adapter.LocalCLIAdapter.collect`는 종료 장벽 확인 뒤 원바이트·SHA/크기와 함께 보존한다. 이유/완료 판정과 진단 목록은 별개이며 장벽 미확인 때는 읽지 않는다. `call_engine._receive_call`의 기존 json_safe(result)와 result_ref가 artifact 보존자다. 새 실행 원장 필드를 만들지 않았다.

현재 `call_result` 문서 소유자와 `sim.test_provider_collection`의 실제 runner 반환 직렬화·원바이트 복원·비어 있지 않은 offset 소비·없는 필드 반려를 대조했다. 진단이 있어도 정상은 정상이고 exit 1/turn.failed/제품 timeout은 실패라는 단언을 읽었으며 저장된 마지막 결과는 passed다.

원 EX-01M5D097XN0TR7G5S582K1MKX4의 원장/결과/CLI 자료/capability 7개 파일의 실제 길이·SHA를 선행 재생 provenance와 대조해 일치했다. 원 stderr는 119 bytes이고 final 수락과 목록 timeout이 공존했다. 과거 장벽을 Job 대역으로 재생한 것과 새 OS 종료 관측은 다르다. URL/HTTP·요청 기한·요청 소요·네트워크/공급자 내부 원인은 미확정이다. 전체 실행 467.066195초를 목록 요청 시간으로 해석하지 않는다. 외부 원인 미확정은 이 개발의 추가 blocker로 만들지 않는다.

## R7.3 — exact snapshot 복원과 Git 호출: 확인한 범위 충족

`repository._read_documents/_decode_families`는 같은 명시 head에서 최대 64경로씩 기존 read_many를 사용하고 복원 안에서 bytes를 재사용한다. `payloads.prefetch`는 검증된 부모의 도달 가능한 참조를 차례로 읽는다. `_references/_snapshot_node/_snapshot_cell`의 공통 구조 검사, `_read_json_blob`의 hash/길이/정규 JSON, decode의 좌표·중복·관계·재인코딩과 뒤 저장 계약/사건 검사를 유지한다. 새 전역 캐시나 외부 Git 포트는 없다.

원 snapshot 811c4576af7fc8a5054181ad0208db42ddd329c6의 before/after 원 계측 JSON을 직접 비교했다. 765개 파일 맵(4,399,529 bytes)과 논리 SHA가 같고 cold 실제 명령은 260→23개, 모두 returncode 0이며 기록 경과는 31.261→3.677초다. warm은 양쪽 0개다. 개선 후 네 모듈 SHA는 현재 코드와 같다. 현재 실제 Git 경계 두 ID도 저장된 통합 보고에서 passed다. 이 리뷰는 벤치마크를 재실행하지 않았다. OS 캐시/호스트 부하 미통제의 한 쌍이며 일반 성능 보장이나 깊은 단일 사슬 비용 해소로 확대하지 않는다.

## 같은 계약·미러·검증의 실제 범위

직접 집계 결과는 `evidence/edition-and-reports.json`에 있다.

| 저장 실행 | 선택/실제 시험 행 | 결과 | 현재 Python과 다른 파일 |
|---|---:|---|---:|
| t2-flows | 4610/4610 | 4482 passed, 115 failed, 11 error, 1 not_run, 1 skipped; fixture error 1 별도 | 34 |
| recheck-1 | 179/179 | 170 passed, 8 failed, 1 error | 12 |
| boundaries-and-recheck | 32/32 | 30 passed, 2 failed | 2(시험 fixture만) |
| final-fixtures | 2/2 | 2 passed | 0(930개 SHA 일치) |

선택 누락/임의 추가 시험 행과 중복 ID는 없고 complete/worker returncode/changed_during_run을 함께 확인했다. 최초 비통과 127 ID와 후속 관측 비통과의 마지막 기록은 모두 passed다. 여러 판본의 마지막 관측은 4618 passed/1 skipped이며 최종 판본의 전체 회귀 성공이 아니다. Windows symlink 권한 skip은 해당 OS 동작 미확인이다. 실제 Git/CLI 결정/설치 검사기/고정 snapshot·문서 소비의 여덟 boundary도 보고의 실제 행을 확인했다. 통합 task의 probe verified는 그 task의 실행 근거이며 이번에 반복하지 않았다.

미러는 파일 경로/내용을 직접 대조한 뒤 공식 생성기의 읽기 전용 `python -B .claude/skills/writing-skills/scripts/build_skill_mirrors.py --check --target .agents`도 실행했다. 출력은 `[.agents] 드리프트 없음 (1394파일)`이다. do-math 파일 각 1224개 중 원바이트 차이 5개는 공식 .claude→.agents/CLAUDE.md→AGENTS.md 변환 대상이며 drift가 아니다. F1 문장은 양쪽에 동일하므로 미러 일치 자체가 의미 정확성의 근거는 아니다.

전체 역할·주요 단계 연결을 위 범위에서 평가했다. 모든 자연어 의미 중복의 자동 판별, 모든 실행/저장 분기, 최종 전체 회귀·T3 full/T5, 새 live 모델/scholarly/실제 Lean/설치 복구 AI, 미래 역할 준수와 수학 연구 효능은 확인하지 않았다. 원 연구·감사·HOLD·예약·graphify·공용 source_repo·다른 task·서비스 상태는 수정하거나 재개하지 않았다. 추가로 입증된 런타임 차단 결함이나 별도 기능 개선 필요는 찾지 못했다. F1의 지급 계약 불일치를 정리한 뒤, 이 범위와 한계를 유지해 최종 완료를 판단할 수 있다.
