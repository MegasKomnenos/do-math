# do-math 역할과 작업 인계 수리 설계

작성일: 2026-10-21. 이 문서는 `role-flow-design` 시작판의 조사 결과와 후속 구현 계약 제안이다. **아래 새 필드·함수·전이는 아직 제품에 구현되지 않았다.** R1~R3 제품 완료의 근거로 사용하지 않는다. 경로의 `D/`는 `.claude/skills/do-math/`, `M/`는 `D/scripts/do_math/`를 뜻한다. 정본만 가리키며 공식 미러는 구현 task에서 생성한다.

## 1. 목적, 확인 사실과 선택

목적은 승인된 연구를 실제 수행하고, 그 결과·실패·미확정을 다음 판단에 연결하는 것이다. 사용자의 최신 정정은 일반 요청의 정상 처리를 유지하면서 예외에서 적절한 종결·이관을 허용한다. 모든 요청을 새로 의심하거나 재심사하는 절차를 만들 이유는 없다. 사용자 목표·필수조건·권한과 AI가 만든 개별 개정 요청은 다른 권위다.

권고안은 기존 역할 10개와 질문·action·execution·개정 대기 구조를 유지하면서 다음 연결을 고치는 것이다.

1. 계약 검토는 수행 가능한 의무를 판단한다. 지적을 전달하기 전에 원문·근거·반대 근거와 자신의 해석을 대조한다. 착수 후 수행자가 확인할 도구 동작이나 연구 결과를 사전 승인 증명으로 요구하지 않는다.
2. `unresolved`는 증거·판단 대기로, `revision_required`는 확인된 계약 결함의 개정 요청으로 소비한다. AI 개정 요청의 전제가 틀렸거나 수정할 내용이 없으면 `dismissed`로 그 요청을 종결한다. 독립 승인이 필요한 계약은 별도 검토가 판단한다.
3. 운영 질문의 안정된 의무를 기존 QU 기록에 보존하고 실제 담당 action·execution·처분·후속과 연결한다. 재시작 때 같은 원장을 읽어 복원하며 소유자 이름을 배정으로 세지 않는다.

### 근거의 범위

- 실제 원문: RECORDS의 `user-messages.md` 전체, 이 task의 `inputs/{context,plan,seams}.md`, `objective.md`, `task.json`, 개발 서비스 `protocol.md`의 task/보고 절차.
- 역할 모집단: `D/SKILL.md` 읽기 대응표, `M/contracts.py:ROLES/reading_map/prompt_documents/action_schema`, 계약 11개와 공통 실행의 개정·질문·제출·독립성 규칙. 설치 복구의 실제 지시는 별도로 `M/repair_execution.py:repair_prompt`에 있다.
- 사건 원문: `C:/math/.skill-workspace/parking-unimodality-20261021/work/runs/`의 E05=`EX-01M5CZSKE82FXDZJHKDYYB393R`, E10=`EX-01M5D0ZPXND4CN3VV67DA6HGB2`, E12=`EX-01M5D19Y02PMCZQPKPS32G4FF0`의 `evidence/final.txt`, E05/E10의 `workspace/activity-extensions.json`. 감사 `executions.csv`, `reproduction-results.json`과 `research/parking-unimodality-audit-2026-10-21/원인-분석.md`의 관련 절을 대조했다.
- workspace의 작은 실제 호출은 task `evidence/inspect_current.py`와 `evidence/current-observations.json`에 있다. 10개 역할의 실제 지급 문서 순서·내용 해시, 동일 origin 재전달, 다른 origin의 같은 질문, 필수 개정의 unchanged 거부, 운영 질문의 역할 제한을 확인했다. 전체 시험·모델 호출·새 연구 운전은 하지 않았다.
- scholarly 호출 성공은 그 호출의 범위다. E05의 보고는 실제 미노출의 공급자 원본 증거가 아니다. 프로필별 전체 도구 성공, 최초 인식과 후속 자기모순의 모델 내부 원인은 미확정이다. 이 설계가 그것을 확정할 필요도 없다.

## 2. 역할 모집단 평가

표의 입력은 `_context` → `context_store.prepare_role_input`의 inline/지도/차단 규칙을 거쳐 지급된다. 출력은 역할별 스키마와 `submission` 공통 검사 뒤 `_apply_bundle_candidate`의 원자적 후보 적용·검증·CAS로 소비된다. 세부 판단을 산문으로만 약속하고 수신 경로가 없는 경우는 변경 대상으로 표시했다.

| 실제 역할·단계 / 계약 | 목적·책임·판단과 재량 | 실제 입력 → 출력 소비 | 유지·수정 판단과 이유 |
|---|---|---|---|
| `research_preparation` 일반 / 후보-준비 | K/F·실패·목표에서 질문과 수행 계약을 저작한다. 방법을 미리 증명하거나 자기 계약을 승인·선택하지 않는다. AI 미완료 과제는 근거 있게 개정·철회할 수 있다. | `_refresh_readiness`, 계획의 `preparation_requests`, 개정 요청 → `_context`의 tasks/catalog/history/pending_revisions → candidates와 확장 → `_apply`의 완전 계약 교체·조건 결박·독립 검토 배정, `_apply_revision_followup` | 저작/선택 분리, 무산출·위임·근거 재사용 유지. 개정 예외 종결과 실제 후속을 추가한다. 문헌·정의·계산을 단순 순서 편의로 전체 완료에 묶지 않고 필요한 산출만 의존시킨다. |
| 같은 역할의 `assessment_targets`/`observation_rule_targets` 보충 | 사용자 계약을 유지하며 AI 모델 평가·관찰 규칙을 보충한다. 후보 생성 권한은 없다. | `planning_engine._ensure_model_assessments` → 고정 판본·과거 반려 → 보충 확장 → `_finish_assessment_preparation`/관찰 준비 검사 | 좁은 보충 계약 유지. 도구 불확실성까지 평가·규칙 삭제로 처리하지 않게 수정한다. 사용자 원 계약의 결함은 사용자 결정으로, AI 부속 평가 결함만 보충으로 보낸다. |
| `research_plan` / 연구-계획 | ready 전건 비교·선택, returned 전건 완료 집계, 다음 준비·감사 요청. 후보 저작·수학 인증·사용자 의무 면제는 하지 않는다. | `_refresh_readiness`의 사건과 ready/returned, 결과 원문 → dispositions/task_assessments/preparation_requests → `decision_engine._apply_task_plan`, `task_scope.apply_task_assessments` | 고정 모집단 전건 처분, not_assessable, 지정 판정·권위 있는 면제/이전 유지. 운영 사실을 발견하면 기존 QU에 새 근거를 연결하도록 수정한다. 자연어 next_owner만 적는 것을 인계 완료로 쓰지 않는다. |
| `research_work` / 연구-수행 | 선택된 계약 안에서 실제 조사·증명·계산·반례와 가능한 형식화를 수행한다. 방법 선택과 실패·부분 결과 반환의 자유가 있다. | 계획 선택 → task/readiness/도구/허가 → submitted/partial/waiting/no_result와 지식·관계 → `_apply`의 results·지식 편입·다음 계획, 형식/동일성 경로 | 수행과 완료·인증 분리 유지. 실제 도구 확인·접근 실패와 운영 인계를 이 역할의 착수/수행 책임으로 명확히 한다. 없는 결과를 사전 검토의 전제로 요구하지 않는다. |
| `task_contract_review` / 작업-계약-검토 | 질문·범위·입력·산출·완료 기준의 수행 가능성과 인계 적합성을 독립 판단한다. 구체적인 결함을 반환하며 직접 계약을 쓰거나 미래 성공을 보증하지 않는다. | 후보/현행 기초 → task·참조 원문·profile/authority → 다섯 item_reviews → `contract_review_decision`, `seal_contract_review`, `_apply` | 목적·독립성·다섯 관점 유지. §4의 지적 자기 검토, 도구 책임 경계, 미해결/개정 분기와 예외 재검토 입력을 수정한다. 이미 타당한 계약을 고치게 하지 않는다. |
| `identity_review` scope/initial/organize/answer/judge, 판정 재심사 / 동일성-검토 | Lean·해설·요약의 의미 전건 대조. scope는 배정 계획, organize는 쟁점 연결, answer는 유지/수정/분화/철회, judge는 이의와 제안 각각의 판단이다. | 형식 검사 뒤 `_queue_identity_actions`, `review_cycle`의 고정 제안·자리·공개 결과 → 동적 stage schema → `_apply_identity_review`, 봉인 IA·다음 계획 | 현행 예외 재량이 이미 있다. 이의 철회·기각과 전체 판정, 한도/미응답과 의미 판단을 분리하는 구조를 유지한다. 다른 단계에 이 절차 전체를 복제하지 않는다. 공개 가능한 운영 질문에만 §6 배정을 연결하고 비공개 자리의 차단을 유지한다. |
| `goal_audit` 추가 감사 포함 / 목표-감사 | 현재 목표와 사용 가능한 형식 결과·해설·판정의 충족 대응을 독립 판단한다. 정확한 부분 결과와 목표 충족을 구별한다. | 계획/목표 감사 배정 → eligible_knowledge·목표/정책·추가 감사 → satisfied/not_satisfied/unresolved → `governance_engine._apply_governance_goal_audit`, 독립 자리 집계·학술 후속 | 수학적 해결과 학술 후속·과제 완료 분리 유지. 운영 질문의 처리 결과를 감사 결론으로 바꾸지 않는다. 근거 부족을 목표 거짓으로 해석하지 않는 계약도 유지한다. |
| `supplemental_research` 과제/검토 고정 질문 / 보충-조사 | 상위가 정한 질문을 조사하고 근거·한계를 반환한다. 과제 배정에서는 일반 지식 저작, 고정 조사에서는 답만 반환한다. | 일반 task 또는 `_defer_review_for_research` → 봉인 request_digest·sources → 연구 스키마 또는 answered/unresolved → `_apply_review_research`/`accept_research_result` → 같은 자리 재개 | 고정 질문의 확장·중첩 요청 금지 유지. 질문 범위·독립성·상위 한도 보존에 실익이 있다. answered를 상위 승인으로 쓰지 않는 경계 유지. 취소/실패도 `_abandon_review_research`가 범위·미완료를 반환하므로 새 보편 종결 장치 불필요. |
| `operational_review` live/종료 후 / 운영-점검 | 실행·활동의 진전 근거, 실패·재생 안전성·복구 필요를 판단한다. 실제 설치 결함은 repair, 수행 복구는 retry/resume, 사용자 결정은 별도 질문으로 보낸다. | 관찰/주기/실패 배정 → execution_to_review·checkpoint·recovery_materials·admissible_basis_refs → 여섯 disposition → `_apply_operational_disposition`/종료 장벽/설치 복구 | 여섯 처분과 현재 근거 제한 유지. 첫머리의 “과제 완료를 대신 판정하지 않는다”와 뒤 task_disposition을 맞춰 ‘지정 판정과 근거를 집계할 수 있으나 대신 발명하지 않는다’로 고친다. 모든 질문을 실행 진단으로 억지 배정하지 않는다. §6에서 execution 대상이 있는 운영 처분에 사용한다. |
| `intent_interpretation` interpret/check/위임 판단 / 의도-해석 | 원문을 등록 소비자의 단위로 해석·독립 검사한다. 사용자 승인과 소비자 적용을 대신하지 않는다. | 초기/후속 원문 → import_consumers·고정 source·원문 좌표 → import/check/delegation 동적 응답 → `_apply_governance_intent`/owner handlers | 전건 원문 피복·독립 검사·명시 승인·위임 범위 유지. 현재 check의 모든 비승인이 재저작으로 가는 연결은 §7에서 구분한다. 자료 부재만으로 정확한 묶음을 다시 쓰게 하는 것은 개정 사건과 같은 종류의 낭비다. |
| `maintenance` 일반/초기 진단/종류 정의/impact / 유지보수 | 호출 절차의 대상·권한·성공 조건 안에서 기술 근거와 의미 보존·인계 충분성을 판단한다. 일반 report만으로 중앙 상태를 고치지 않는다. | 제어/초기 실패/종류 제안/편입 영향 요청 → 단계별 고정 자료 → report와 동적 판정 → `_apply`의 진단·종류/영향 소비 | 좁은 권한과 impact 전건·독립성 유지. 일반 지원·자료 확인 질문에는 §6의 구체적 `stage=question` 입력·출구를 추가한다. “대상 없는 유지보수”를 생성하지 않는다. |

내부 역할 밖의 실제 모집단도 확인했다.

| 경로 | 실제 책임과 소비 | 판단 |
|---|---|---|
| `formal_check`, `trust_check`, `trust_activate`, `external_action` | 기계 action이다. `execution_profiles`와 `formal_engine`/외부 행동 원장이 실제 입장·형식 결과·신뢰/외부 영수증을 처리한다. | `contracts.ROLES`에 AI 역할로 추가하지 않는다. 형식 검사 성공과 동일성/목표·외부 허가의 경계 유지. |
| 예약 감독 | `scheduled_operator.check/engine_start_guard`, `supervision`의 HOLD·pause·lock·wake 점검 후 기존 실행기 예약 시작 | 모델 없는 감독 유지. 열린 질문 해소를 이 경로의 의미 판단으로 맡기지 않는다. 새로운 도래 질문 의무는 엔진의 wake 사실로 전달한다. |
| 설치 복구 AI `recovery` | `scheduled_operator.recovery` → `repair_execution.repair_prompt`와 JSON → `supervision.repair_report_schema`/실제 로그·설치 검사·잠금 반환 후 launcher | 읽기 표의 11번째 내부 역할로 오인하지 않는다. 고정 프롬프트가 실제 지급 지시다. 실패 재현·최소 수리·연구 원장/권한/예약 변경 금지·HOLD 보존 유지. 질문 triage가 설치 수리 권한을 새로 만들지 않는다. |
| 사용자 대화/운영자 | 목표·정책·허가·정지·답변을 공개 제어/의도 수입으로 전달 | 기술 사실 확인을 사용자 재승인으로 바꾸지 않는다. 기존 승인과 정지의 적용 범위는 그대로 유지한다. |

## 3. 현재 끊기는 연결과 유지할 연결

### 실제 추적에서 확인한 공백

`core_engine._apply(task_contract_review)`는 `seal_contract_review` 뒤 승인 외 두 값을 모두 `revision_requested`·`contract_revision` 대기·후보 준비로 바꾼다. `revisions.submission_errors`는 required 또는 현행 반려가 있으면 unchanged를 거부한다. `_apply_revision_followup`도 required인 부모의 unchanged를 남긴다. `planning.revision_required`는 같은 revision의 역사적 비승인 하나만 있어도 참이다. 단지 새 처분 enum을 추가하면 이 네 소비자와 `_refresh_readiness`의 `reviewed` 억제가 여전히 막는다.

`questions.link`의 재전달 키는 origin_execution_id+origin_field다. `_record_output_questions`는 link만 호출한다. 서로 다른 보고의 같은 의무는 다른 QU가 되고, 등록만으로 queue가 생기지 않는다. `questions.user_waits`는 user 질문만 차단하며, operations의 blocks 표시는 현재 일반 착수 검사와 연결되지 않는다. `_apply_question_resolutions`는 질문을 닫지만 관련 revision_dependency 해소나 독립 검토 재개를 하지 않는다. R3은 등록·배정뿐 아니라 이 후속까지 포함한다.

E05 원문은 네 항목을 승인했고 도구 지원만 미확정으로 남겼다. E10은 실제 계약 수정 사유가 없다고 썼지만 deferred만 가능했다. E12는 실제 성공 호출을 보고했지만 operations 질문을 해소할 권한도 배정할 구조화 경로도 없었다. 이 사실은 도구 자체의 전면 장애를 입증하지 않는다.

### 형식과 재량의 실익 판단

| 경계·형식 | 유지/변경과 이유 |
|---|---|
| 다섯 계약 검토 항목의 정확한 피복 | 유지. 질문·입력·산출·단계·도구 중 미검토 범위를 숨기지 않고 완료 기준을 공유한다. 승인에는 해당 계약/제공 근거가 충분하며 새로운 호출 성공 증명서를 요구하는 형식으로 쓰지 않는다. |
| 후보 contract_checks, 기호·결과 갈래·형제 경계 자기 점검 | 유지. `submission.contract_check_errors`는 실재 ID·판본·선언 경계를 검사하고 의미는 저자와 독립 검토가 판단한다. 빈 sibling 목록은 저비용 전건 대응 표지다. 다만 ‘상대 계약 개정 대기’와 ‘상대 연구 전체 완료’는 다르므로, 실제 결과가 필요 없는 경우 전체 dependencies를 편의로 추가하지 않고 독립 경계를 정련한다. 이 task는 새로운 조건 문법을 요구하지 않는다. |
| ready/returned 전건 처분·의무별 완료 판정 | 유지. 누락 방지와 다음 소유자의 판단에 실익이 있다. not_assessable/open/unresolved 및 권위 있는 철회가 이미 있으며 모든 미선택에 수리를 강제하지 않는다. |
| 개정 대상 전건 대응 | 유지. 대상별로 개정·유지·예외 종결·대기·위임을 식별해야 의무를 잃지 않는다. 전건 대응은 전건 실제 수정과 다르다. |
| integration_bundles·previous_hashes | 유지. 개정 처분도 기존 객체와 의무 상태를 바꾸므로 고정 입력과 원자적 적용을 결박한다. R4~R5 공통 검사 수리의 정본을 소비한다. 단순 request 생성에는 기존과 같이 개정 묶음을 강제하지 않는다. |
| 출력 수리 issue 대응 | 유지. 원 issue와 수리·유지·철회를 추적한다. schema 통과만으로 maintained가 수용되는 것은 아니며 동일한 실제 검사를 통과해야 한다. 출력 결함과 실제 전제 변화·게시 실패는 각각의 경로를 유지한다. |
| 동일성 이의·고정 조사 전건 대응 | 유지. 현행 answer의 withdraw와 judge의 rejected가 예외 처분을 제공한다. 한도 소진은 이의 성립이 아니다. 다른 역할에 세 판정자/쟁점 정리 전체를 복제하지 않는다. |
| 외부 행동 unknown·신뢰 전환·목표 종료 정산 | 유지. 알 수 없는 외부 효과의 재전송, 부분 인증의 목표 해결, 종료된 실행 부활을 막는 실익이 있다. 개정 요청 반려 재량으로 이를 해제하지 않는다. |
| 일반 maintenance report/remaining_work | 유지하되 질문을 맡긴 실행에는 기계가 소비할 question_resolutions를 요구한다. 다음 담당의 이름만으로 수행 의무가 넘어갔다고 해석하지 않는다. |

## 4. 계약 검토 책임과 지급 문구

`D/계약/작업-계약-검토.md`의 목적·시작 입력·도구 절·판정 절에 다음 의미를 함께 반영한다.

- 질문을 수행하고 산출을 판정할 수 있는지 확인한다. 지적할 때에는 정확한 계약 위치, 읽은 근거, 예상되는 잘못된 수행/완료 판정과 필요한 조치를 설명한다. 지적 전에 자신의 오독, 단계 혼동, 누락한 지급 원문·공개 기록, 반대 근거로 설명되는지 확인한다. 별도 고정 수량의 자기 검토 보고 필드는 만들지 않고 기존 findings/evidence_refs에 판단 근거를 담는다.
- 새로운 문헌 확보·증명·정확 계산, 향후 수행 세션의 실제 도구 확인은 그것을 맡은 수행의 책임이다. 검토자는 현재 계약이 그 책임과 실패 반환을 적절히 정하는지 본다. 검토 자신의 성공 호출 부재는 수행 계약의 결함이 아니다. 계약을 이해하는 데 필요한 원문을 읽지 못한 것과 미래 산출이 아직 없는 것을 구별한다.
- 실제 허가 부재·필수 능력의 명백한 미지원·모순된 프로필이나 수행 불가능한 완료 의무는 영향받는 범위의 근거 있는 지적이다. 설정을 성공으로 쓰지도, 실패 근거 없는 불확실성을 전면 사전 차단으로 키우지도 않는다. 같은 설치의 과거 호출은 해당 호출의 근거로만 읽는다.
- `revision_required`는 무엇을 고쳐야 하는지 확인한 경우다. `unresolved`는 지금 끝낼 계약 의미 판단에 꼭 필요한 자료/효력이 없는 경우다. 단순히 연구의 답이나 미래 도구 성공을 아직 모르는 것은 unresolved 사유가 아니다.
- 승인에는 계약·제공된 설정/권한·입력 등 기존 참조가 충분할 수 있다. 승인도 향후 도구 성공·수학 결과를 보증하지 않는다. 수행 중 실제 실패는 §6의 운영 의무로 연결한다.

`SKILL.md`의 준비→검토→선택 설명과 `references/학술자료-활용.md`의 ‘먼저 확인’은 **해당 역할이 자기 판단에 실제 조회를 필요로 할 때** 적용한다고 범위를 맞춘다. 모든 역할이 문서 지급을 받았다는 이유로 미래 수행 프로필의 search/fetch/extract 성공까지 입증하게 하지 않는다. `core_engine._context`의 scholarly.availability 안내도 “현재 역할의 도구 사용 시 확인, 수행 역할은 착수/수행에서 실제 확인”으로 맞춘다. 이 문구는 `prompt_documents`가 실제 지급하므로 별도 읽히지 않는 가이드만 만들지 않는다.

## 5. 계약 개정과 예외 종결의 정확한 계약 제안

### 5.1 정본과 wire/저장 필드

정본은 `M/revisions.py`에 둔다. 기존 파일에는 `validate_extensions`라는 함수가 **없고 `submission_errors(output, extensions, context)`가 있다.** objective의 해당 이름은 이 실제 함수로 구현한다. 새 공통 정의를 엔진에 두지 않는다.

| 정의 | 제안할 정확한 의미 |
|---|---|
| `revisions.REVISION_DISPOSITIONS` | `revised`, `unchanged`, `dismissed`, `deferred`, `delegated`. submission의 확장 schema도 이 상수를 소비한다. |
| `revision_resolutions[]` | 기존 record_id/disposition/reason, delegated 전용 task_title 유지. dismissed에 `request_refs: REFS(minItems=1)`, `evidence_refs: REFS(minItems=1)`를 필수로 추가한다. 해당 대상에 선언된 AI source_refs 전건을 request_refs로 지정하고 실제 원문을 읽은 근거와 잘못된 전제/무수정 이유를 설명한다. 다른 처분에 이 두 필드를 무의미하게 요구하지 않는다. |
| `capture_targets(instance,runtime,identifiers,*,required=False,source_ref=None,user_decision_refs=())` | 기존 revision/contract 또는 content hash/required/source_refs에 기계가 확인한 `user_decision_refs` 목록을 더한다. source가 사용자 task_scope revise 결정이면 현재 승인된 결정 ID를 반드시 포함한다. 모델이 이 목록을 만들거나 줄이지 못한다. |
| `task.revision_requested` | 현행 저장 형태를 `{revision, contract_sha256, source_refs, user_decision_refs, reason}`로 교체한다. 단일 source는 source_refs로 통일한다. 미해소 요청 전건의 출처를 보존하고 종결한 출처만 제거한다. 원 요청은 history에 남긴다. |
| `revisions.resolution_schema()` | 확장의 한 대상 처분 모양을 반환하는 새 schema builder. submission.extension_schema가 이 정의를 넣고 submission_errors가 같은 schema 및 의미 검사를 쓴다. 엔진은 검사를 통과한 처분만 적용한다. |
| `revisions.resolved_targets(action, extensions)` | 새 순수 함수 → 종결할 `{record_id: source_refs}`. revised/선택적 unchanged/허용된 dismissed/철회를 공통 계산한다. deferred·delegated는 실제 남은 의무를 종결로 반환하지 않는다. 부모 대기 정산과 실패 action 해소가 이 함수를 공유한다. |
| `planning.revision_required(task)` | 현재 판본의 미해소 revision_requested 의무만 참이다. 역사적 비승인 reviews를 OR하지 않는다. 독립 승인의 부재/미해결은 아래 effective_contract_review로 별도 판단한다. |
| `planning.effective_contract_review(task,instance,runtime,*,task_basis=None)` | 새 순수 함수 → 현재 계약·전제의 **마지막 수락된** 검토 또는 None. 기존 contract_review_current를 호출한다. 과거 approved 하나와 나중 부정 판정을 동시에 유효 승인으로 쓰지 않는다. pending/conflict 재검토 동안에는 None이다. readiness와 lifecycle의 승인/검토 여부 집계 모두 이 함수를 쓴다. |
| `task.contract_review_reconsiderations[]` | 기계 기록 `{key, basis_key, requested_by, source_refs, evidence_refs, status, review_execution_id}`. key는 계약 해시+원래 review_basis_key로 만든 exact_content_hash, status=`pending|reviewed|conflict`, review_execution_id는 처음 null. 계약 내용이 아니므로 CONTRACT_FIELDS에 넣지 않는다. 요청 종결 뒤 같은 계약의 독립 판단을 한 번 열고 그 결과를 연결하는 기록이다. |
| `action.contract_review_reconsideration` | 재검토에만 `{key, requested_by, source_refs, evidence_refs}`를 지급한다. 원 검토와 dismissal 근거를 함께 읽되 계약 전건을 독립적으로 판단한다. action schema/저장/현재성/중복 비교 필드에 추가한다. |

명시적인 사용자 revise 의무나 사용자 학술 필수조건을 dismissed/unchanged로 끝내지 않는다. `user_decision_refs`가 남은 대상은 dismissed를 반려한다. mixed AI+user 대상도 사용자 요구를 지우지 않는다. revised로 이행하거나 필요한 새 사용자 결정을 기다린다. 사용자 목표가 보존되는 AI 개별 과제의 재설계/철회는 기존 task_dispositions·task_scope 규칙을 따른다.

### 5.2 정상·예외 전이

| 입력/처분 | 요청·과제·다음 판단의 실제 효과 |
|---|---|
| 계약 검토 approved | 검토를 봉인한다. 해당 current AI 검토 요청의 review 대기만 해소한다. 별개 사용자 개정·운영 차단·의무는 유지한다. 정상 readiness→계획 선택으로 간다. |
| revision_required | 확인된 결함과 원 검토 실행을 source_refs에 넣고 required=True로 후보 준비에 배정한다. 기존 정상 revised 경로는 그대로다. |
| unresolved | revision_requested를 만들지 않는다. task.status=waiting, waiting.kind=`contract_review_input`, review execution·missing_inputs·question_ids를 저장한다. §5.3으로 필요한 입력 담당을 배정한다. |
| revised | 실제 저작 변경을 요구한다. 새 완전 계약은 revision+1, 이전 문면·검토·의무/대기를 revision_history에 보존한다. 대응 요청과 부모 대기만 종결하고 새 판본을 독립 검토한다. 원 지식 개정은 실제 수락된 knowledge_changes가 있어야 한다. |
| unchanged | 선택적 검토 요청에만 기존과 같이 허용한다. 이미 유효 승인과 실제 전제가 그대로면 새 승인 실행을 만들지 않는다. 필수 AI 반려의 예외는 dismissed로 이유/근거를 명시한다. |
| dismissed | 그 AI 요청을 근거 있게 종결한다. 해당 revision_targets와 source_refs, 부모 revision_dependency·deferrals·delegated_targets의 해당 의무를 제거하고 history에 요청/근거/처분 실행을 보존한다. 계약 내용·revision·완료 의무는 바꾸지 않는다. 독립 승인 필요가 없으면 정상 후속 계획, 필요하면 아래 재검토를 한 번 연다. |
| deferred | 해결하지 못한 대상/출처를 보존한다. revision_dependency는 남는다. 원인 QU 또는 실제 입력 변화에 연결해 기다리며 같은 입력의 준비를 즉시 재생성하지 않는다. 자연어 reason만으로 해소됐다고 쓰지 않는다. |
| delegated | 기존 지식 개정 과제 생성·대상 결박을 유지한다. 과제 배정/종료는 개정 이행이 아니다. 실제 개정 또는 허용된 예외 처분이 부모에게 돌아와야 종결한다. 위임 과제 실패/철회면 `_reconcile_revision_delegations`가 계획에 남은 의무를 돌린다. |

`_bind_revision_action`과 `_enqueue`의 병합은 source_refs/user_decision_refs를 합집합으로 보존한다. `_cancel_selected_revision_targets`가 단순 writer 예약을 새 필수 변경 사유로 위조하지 않게 한다. 실제 개정 요청을 결박할 때만 revision_requested에 출처를 넣고, 요청의 출처가 없는 writer 잠금은 기존 revision_waits로 표현한다. target 재결박에서는 최신 해시만 갱신하고 요청 출처·사용자 결정은 잃지 않는다.

`_apply_revision_followup`은 resolved_targets를 사용해 자기/부모 waiting_actions를 함께 정산한다. 다른 target/source와 live 실행은 건드리지 않는다. `_settle_revision_owner`·`_settle_request_owner`의 실제 종료/예약 반환 경계를 유지한다. `decision_engine._apply_action_resolutions`의 “실제 revised만 해소” 검사도 같은 resolved_targets를 소비하도록 바꾼다. 그렇지 않으면 실패한 개정 요청은 dismissed 뒤에도 execution_failure/output_validation 대기로 남는다. `_resolve_failed_actions`도 범위가 다른 대기를 역할/target만 같다는 이유로 없애지 않는다.

### 5.3 미해결 입력과 무수정 재검토

`REVIEW_ITEM`의 세 판정과 다섯 ID는 유지한다. `question_routes`에 선택 `review_item_ids`(CONTRACT_REVIEW_ITEMS 부분집합)를 추가한다. unresolved 항목 전건은 관련 질문 하나 이상에 연결돼야 하며, 그 질문은 부족한 입력·영향·실제 다음 담당을 지정한다. 공통 검사에서 피복을 확인한다. engine은 생성된 QU ID를 contract_review_input 대기에 결박한다. 사용자 목적/허가 판단이면 user, 기술 확인·자료 회수면 operations, 새 수학 연구가 필요한 의미 질문이면 research로 보내 준비/계획이 조사 계약을 정한다. 미래 수행의 성공 미입증만으로 이 질문을 만들지 않는다.

dismissed를 수락한 계약에 유효한 독립 승인이 없으면, `_apply_revision_followup`은 `contract_review_reconsiderations`에 pending을 기록하고 같은 계약 판본에 새 `task_contract_review`를 배정한다. **준비 실행의 처분은 승인으로 변환하지 않는다.** 새 검토자는 계약 저자·dismissal 생산자·문제된 원 검토의 실행 문맥을 이어받지 않는 새 실행이어야 한다. 공개된 계약·이전 판단·반박 근거는 입력으로 읽는다. 이를 `seal_contract_review`/입장 독립성 검사에도 적용한다.

동일 계약+원 review_basis_key에는 자동 예외 재검토를 한 번만 연다. 재검토가 승인하면 reviewed와 실행 ID를 기록하고 다음 readiness/계획을 연다. 새로 근거 있는 결함을 반환하면 그 **새 판단**이 source인 개정 요청이 된다. 준비는 정상적으로 고칠 수 있다. 이를 다시 dismissed할 수도 있지만 동일 key의 자동 재검토는 반복하지 않고 conflict로 두며, 안정된 `decision_conflict` 운영 질문 하나로 판단 불일치의 근거·다음 행동을 조사한다. 요청 자체는 종결됐고 필수 수정 의무를 다시 만든 것은 아니다. 승인 미확정은 별도 대기다.

운영 결과나 원자료가 실제 바뀌면 `_resume_contract_review_waits`(새 엔진 함수)는 해당 QU의 새 resolution_ref 또는 실제 입력 fingerprint를 소비해 현재 계약의 독립 검토를 한 번 연다. 같은 질문 해소 영수증을 재소비하지 않도록 history의 `(task_id, contract_hash, question_id, resolution_ref)`로 식별한다. 판단에 필요한 새 근거가 없는 ‘다시 보라’ 보고는 재개 사건이 아니다. 일반 계약 검토에 이 재검토를 필수 단계로 넣지 않는다.

`lifecycle_engine._refresh_readiness`는 reviewed=True인 옛 비승인이 있다는 이유로 이 명시 재검토를 억제하지 않고, 동일 계약의 live 검토가 있으면 종료까지 기다린다. task_ready는 미해소 요청·pending/conflict·현재 독립 승인·질문·입력·권한을 각각 확인한다. 승인 하나로 다른 gate를 무효화하지 않는다. readiness가 변하면 기존 사건→계획 경로를 사용한다.

학술 계약에도 같은 비승인 분리를 적용한다. `_ensure_model_assessments`는 unresolved나 도구 지원 질문을 이유로 모델 평가/최초 관찰 규칙을 지우지 않는다. revision_required의 실제 지적이 AI 부속 평가/규칙이면 그 필드만 보충 대상으로 삼고, 사용자 원 계약 수정은 현행 governance 경로로 보낸다. 새 전이가 일반 계약만 수리하고 학술 경로를 같은 무한 준비에 남기지 않게 한다.

## 6. 운영 질문의 안정된 의무와 실제 처리

### 6.1 정체성: 원 보고와 처리 의무를 함께 보존한다

별도의 운영 티켓 원장을 만들지 않는다. `questions.py`가 QU의 식별·중복·처분·대상 대기 규칙을 소유하고, `question_engine.py`가 배정·실행·후속 연결을 소유한다. 기존 QU ID는 원 보고 위치와 분리되는 안정된 처리 요청 ID도 겸한다.

`question_routes[]`의 기존 question_index/owner/target_ids/reason/blocks에 다음 선택 필드를 더한다. **operations 라우팅에는 obligation을 필수로 한다.**

```text
obligation = {
  kind: execution_support | input_retrieval | installation_defect | decision_conflict | other,
  subject_ref: 실제 제공된 대상 ID/입력 참조,
  requirement_ref: 실제 의무 ID/도구 토큰/필드 좌표
}
existing_question_id: 같은 의무가 이미 입력에 있으면 그 QU ID
handler_role: maintenance | operational_review  (생략 시 아래 기계 규칙)
reopen_basis_refs: 실제 재발 관찰의 참조 목록  (해소된 같은 대상을 다시 열 때만)
reopen_reason: 재개할 의무와 새 관찰의 관계
```

`questions.obligation_key(obligation) -> str`를 새로 두고, 닫힌 세 필드의 canonical exact_content_hash로 식별한다. 질문 문장의 문자열 해시, origin 실행, 보고 시각, title은 key가 아니다. 예를 들어 특정 과제의 `tool:scholarly` 지원 의무는 `{kind:execution_support, subject_ref:TK-L, requirement_ref:tool:scholarly}`다. 프로필의 어떤 판본을 조사했는지는 증거 기초에 보존하고, 같은 과제의 같은 지원 질문을 매 실행마다 새 의무로 만들지 않는다. 과제 자체와 무관한 설치 결함은 subject_ref에 지급된 installation 참조를 쓴다.

같은 의미를 다른 descriptor로 썼을 가능성은 기계 문자열 대조만으로 완전히 판단할 수 없다. 생산자는 지급된 open/최근 resolved 질문 목록을 읽고 같은 의무이면 existing_question_id를 사용한다. checker는 참조·owner·대상·키의 양립성을 검사한다. 단지 wording이 다르다는 이유로 새 요청을 만들지 않는 책임은 역할 계약에 둔다. triage에서 이미 있던 중복을 발견하면 근거 있는 superseded→replacement_question_id로 합친다. 두 descriptor가 같다는 것만으로 내용상 다른 장애를 조용히 폐기하지 않는다. 임의 자연어의 의미 동일성을 완벽히 자동 인식했다고 주장하지 않는다.

명시 existing_question_id가 있으면 다른 descriptor도 생산자의 동일 의무 판단과 nonblank reason을 근거로 연결할 수 있다. QU가 입력에 실제 지급됐고 양쪽 owner가 operations이며 대상 참조가 유효해야 한다. canonical obligation/key를 고치지 않고 origins에 이번 `obligation`을 보존한다. 다른 사용자 권위를 합치거나 권한을 넓히는 연결은 거부한다. 동일 key 자동 연결과 AI의 명시 동일성 판단을 구별해 이력에 남긴다.

`questions.link`에 `obligation=None, existing_question_id=None, handler_role=None`을 추가한다. 같은 origin 재전달은 기존과 같이 같은 결과를 반환한다. 다른 origin이라도 명시 QU 또는 같은 obligation_key가 있으면 **같은 QU**에 아래 origins를 추가한다. 같은 origin을 다른 소유자·의무·효과로 재전달하면 ValueError다. 새 origin은 독립 보고이므로 영향 대상은 추가할 수 있다.

`question_links` 저장 필드의 변경은 다음과 같다.

| 필드 | 의미 |
|---|---|
| 기존 origin_execution_id/origin_field/source_ref/source_kind/source_id | 최초 원문 위치를 유지한다. 기존 질문 원문을 덮어쓰지 않는다. |
| `origins[]` | 각 보고의 `{execution_id, field, source_ref, source_kind, source_id, target_ids, blocks, reason}`와 operations의 보고 descriptor `obligation`. 없는 source_kind/source_id는 생략, execution_id/source_ref는 기존 비실행 원천 규칙을 따른다. 최초 보고도 한 항목으로 저장한다. 원문 자체는 기존 보존 위치에 있다. |
| `obligation`, `obligation_key` | operations 처리 의무의 설명과 기계 계산 key. key는 모델이 제출하지 않는다. |
| target_ids/unresolved_target_ids/blocks | target_ids는 보고별 대상의 순서 보존 합집합으로 **추가만** 할 수 있다. 원래 라우팅 대상 이력은 origins에 보존한다. 새 미해소 대상만 unresolved에 더한다. 대상별 차단은 origins의 blocks와 해당 origin 대상의 미해소 교집합으로 계산하며, root blocks는 그 요약이다. |
| `handling` | operations 전용 `{generation, role, state, action_id, owner_activity_id, execution_ids, waiting, last_resolution_ref, observation_basis}`. generation≥1, role은 두 운영 역할, state=`pending|assigned|waiting|resolved|superseded`, action_id/activity는 최초 null, execution_ids는 실제 등록 실행 목록, waiting은 아래 조건 또는 null이다. observation_basis는 실제 관찰 참조의 기계 포착 기초(처음 null)다. 이 값은 엔진이 생산하며 모델이 쓰지 않는다. queue/live/활동과 의미가 일치하는지 저장 관문에서 검사한다. |
| `resolution_history` | 기존 close 이력 모양을 유지한다. waiting/transferred도 같은 kind/resolution_ref/affected_ids/evidence 계열 이력에 기록하되 terminal close와 구별한다. evidence에 reason·실제 evidence_refs·후속 ID를 보존한다. |

`question_view`는 최초 text와 함께 origins마다 원문을 회수한 `reports`를 지급한다. 새 출처를 기존 해소 근거처럼 쓰지 않는다. 동일 key·동일 실패 기초·이미 해소된 대상의 재보고는 origins만 보존하고 해소를 취소하지 않는다. 명시적으로 다시 관찰한 실패나 새 미해소 대상이 있으면 같은 QU에서 새 generation을 시작한다. 재개 이유와 실제 관찰 기초를 남긴다. 새 실행 ID나 새 표현만으로 재개하지 않는다. 검사기는 관찰된 원문/프로필/입력의 기존 content-basis를 소비하며 보고 문장만의 해시는 새 관찰 근거가 아니다.

해소된 기존 대상의 재발에는 reopen_basis_refs/reopen_reason 두 필드를 함께 요구한다. 실제 기존 입력/관찰 기록 또는 이번 수집 파일만 허용하고 §6.3의 증거 해소기로 기초를 포착한다. observation_basis와 같은 관찰이면 해소 상태를 유지한다. 새로운 근거에 재발을 결박할 때만 unresolved 대상과 generation을 다시 연다. 실행 중 추가된 보고는 그 실행의 generation/고정 action을 바꾸지 않고, 종료 뒤 남은 대상을 다음 generation에 넣는다.

### 6.2 등록→배정→실행: 하나의 저장 의무

새 `QuestionEngineMixin._reconcile_question_actions() -> bool`은 question_links와 queue·waiting_actions·미종료 executions를 읽고 pending 의무에 담당 요청을 연결한다. 모델 호출은 하지 않는다. 최초 질문 등록이 포함된 candidate 안에서 호출하여 **QU와 action을 같은 CAS에** 보존한다. `_upkeep`/기동 후 준비 갱신에서도 같은 함수를 호출해 미배정 의무를 복원한다. 반복 실행이 같은 queue를 생산해야 한다.

- 기본은 `maintenance`, `stage=question`, `target=obligation.subject_ref`다. 질문·정확한 자료·범위·허가·완료 조건을 입력으로 주어 기술 사실·자료 회수·인계 충분성을 확인한다.
- 실제 execution의 continue/repair/retry/resume/task_disposition 판단이 필요한 경우 `operational_review`, `stage=question`, `target=<그 EX ID>`를 사용한다. 실행 대상은 subject_ref 또는 명시적으로 지급된 관련 실행이어야 한다. 기존 execution_to_review/admissible_basis_refs와 여섯 disposition을 그대로 사용한다. target이 과제/프로필/자료뿐이면 operational_review를 억지로 만들지 않는다.
- action에 `question_ids:[QU]`, `question_generation:<정수>`, `question_target_ids:<그때 미해소 대상의 복사>`를 추가한다. 첫 구현은 action 하나에 QU 하나만 맡긴다. 여러 질문의 일괄 병합은 필요하지 않다. `_enqueue`의 compare_keys와 `_resolve_failed_actions`의 판단 범위 비교에 세 필드를 넣는다. 같은 target의 주기 점검과 질문 처리는 별개의 판단이다.
- queue에서 같은 QU+generation이 있으면 그 요청을 재사용한다. 그 action이 미종료 execution을 소유하면 새로운 요청·실행을 만들지 않는다. 질문 처리의 최신 결과가 수락됐어도 물리 실행이 끝나지 않았으면 다음 처리 generation은 착수하지 않는다. live 실행의 고정 입력에 나중 보고를 병합하지 않는다.
- `_register_execution`은 실제 action의 QU+generation을 확인해 handling.execution_ids/owner_activity_id를 연결한다. 등록 거부는 기존 permission/provider/capacity 대기다. 질문은 해소되지 않는다. 시작·로컬 종료·수락 영수증은 기존 execution 계약을 쓴다.
- 담당 action 실패는 기존 출력 수리/실행 실패 진단에 맡기고 QU는 열린 채 보존한다. 동일 입력의 무제한 자동 triage를 추가하지 않는다. 기존 한정 수리 뒤에는 handling.waiting과 실제 blocked_action을 연결해 운영 또는 기술 입력을 기다린다. 진단 action을 다시 같은 미해소 질문의 신규 보고로 만들지 않는다.

`core_engine._context`는 `operations_questions`에 이번 QU와 reports·assigned_target_ids·handling generation·subject의 정확한 기초·관련 대기(action/review/task)를 지급한다. `context_store`의 `maintenance:question` 범위와 `_ROLE_DIRECT`/INLINE_SCOPES에 이 키를 추가한다. 다른 역할에는 허용된 공개 question_links 목록을 제공한다. 원 의무가 검토 자리의 비공개 자료이면 기존 자리 범위를 적용하고 그 자료가 지급되지 않는 일반 담당에게 넘기지 않는다. 공개 전의 질문은 해당 검토 내부 경로에서만 처리하며, 공개 후 등록 시 배정한다.

`planning.record_index(..., question_links=True)`라는 기존 선택 기능을 QU 참조 조회에 사용한다. 질문을 새 조건 family나 일반 수학 지식으로 등록하지 않는다. 현재성의 `_decision_references`는 질문 보고 전체의 bookkeeping 대신 obligation·assigned_target_ids와 실제 subject/증거 참조를 결박한다. handler가 QU만 읽은 것으로 기록되어 실제 대상 변경을 놓치지 않아야 한다.

현재 `_obsolete_action_reason`의 “원 실패 해소됨”/“live 대상 종료”가 **별개의 열린 QU**까지 버리지 않도록 질문 action의 유효성을 별도로 확인한다. 원 실행이 종료됐어도 지원 질문은 남을 수 있다. 반대로 QU가 해소/대체되면 아직 시작하지 않은 그 generation의 요청을 근거와 함께 은퇴시킨다.

### 6.3 담당 결과의 처분과 기계 소비

일반 maintenance의 report/remaining_work, 운영 점검의 여섯 disposition은 유지한다. `action.question_ids`가 있는 실행은 확장 `question_resolutions`에 **배정받은 QU 전건**의 처분을 반환해야 한다. 기존 연구 질문의 resolved/superseded도 같은 정본을 쓰되 waiting/transferred는 operations의 담당 실행에서만 쓴다.

`questions.resolution_schema()`(새 schema builder)를 submission과 수신 검사가 함께 사용한다. 기존 question_id/disposition/evidence_refs(min1)/reason에 다음 의미를 추가한다.

| disposition | 추가 필드와 효과 |
|---|---|
| `resolved` | operations 담당 응답에는 `affected_ids`와 `generation` 필수. affected_ids는 이번 action.question_target_ids와 같은 집합이어야 하고 그 전건을 실제 확인해 닫는다. 입력 뒤 추가된 대상은 열린 채 다음 generation으로 간다. 일부 배정 대상만 확정됐으면 waiting으로 실제 확인 범위를 근거에 남기고 나머지를 기다린다. “문제 없음”도 읽은 근거와 범위를 요구한다. research 질문의 기존 전체 대상 close는 유지한다. |
| `superseded` | `replacement_question_id` 필수. 이미 존재하는 같은 책임의 수신 QU로 대상·원 보고/대기·근거를 옮긴 뒤 원 QU를 superseded로 닫는다. 자기 참조·순환·서로 다른 사용자 권위의 합병은 반려한다. 다른 의무가 있다는 문장만으로 종결하지 않는다. |
| `waiting` | generation/affected_ids, `wait_for` 필수. 질문 status는 open, handling.state=waiting. 조사 결과가 부족하다는 사실과 다음 확인 조건을 보존한다. 시간 도래만으로 해소하지 않는다. |
| `transferred` | generation/affected_ids, `next_owner`와 아래 실제 수신 참조 필수. 원 질문을 해결됨으로 쓰지 않는다. 운영 역할 간 이관은 같은 QU를 새 담당에게 배정하고, 사용자/연구 의무는 연결된 새 QU를 만들고 그 결과를 기다린다. |

wait_for의 닫힌 합집합은 다음 네 종류다. 일반 새 대기 DSL을 만들지 않는다.

- `{kind:question, question_id}`: 연결된 사용자/연구 질문의 근거 있는 해소·대체를 기다린다.
- `{kind:record_change, ref, basis}`: 지급된 기록/원자료의 실제 기초가 달라질 때 다시 확인한다. basis는 `input_basis`의 해당 참조 투영이며 임의 시각/보고 문장이 아니다. 아직 없는 자료도 제공된 입력 참조의 missing 기초로 결박한다.
- `{kind:time, at}`: 실제 Retry-After 등 근거가 있는 다음 관찰 시각이다. 현재 clock guard와 parse_utc를 사용한다. 다시 실패하면 새 사실/대기 처분을 반환한다.
- `{kind:operational_disposition, disposition_id}`: 설치 수리 등 실제 처분의 종료 영수증을 기다린다. pending/실행 중은 wake가 아니다.

transferred.next_owner=`maintenance|operational_review`는 실제 같은 QU의 새 action으로 연결한다. 실행기 수리 요청이면 기존 operational_review의 `repair` 수락을 통해 installation_recovery로 전달한다. 같은 응답의 `current:operational_disposition` 토큰은 질문 처분의 수신 참조 자리에서만 허용하며 `_apply_operational_disposition`이 **실제로 생성한 OD**로 치환한다. checker는 원 disposition이 repair인지 검사한다. maintenance 보고만으로 이 토큰이나 수리 권한을 만들 수 없다.

next_owner=`user|research`이면 같은 주 응답의 `output:questions/N` 토큰을 수신 참조로 쓴다. 반드시 그 index의 질문과 question_routes가 같은 bundle에 있고 소유자·영향 대상이 맞아야 한다. `_record_output_questions`가 실제 QU를 만든 뒤 이 토큰을 해소한다. 부모 operations 질문은 그 child QU의 결과를 기다린다. 사용자 목적·허가·위험 결정만 user에 보내고, 단순 기술 사실은 maintenance/operations에서 처리한다. 연구 조사가 필요하면 연구 질문→계획/준비→실제 조사 계약을 연결한다. `question_ids`를 받은 담당의 빈 questions/자기 재질문으로 이관을 흉내 내지 않는다.

research로 이관한 경우 `_advance_question_dependents`는 child QU를 target으로 하는 기존 lifecycle 사건 경로에 새 kind=`question_research_followup`을 한 번 기록해 research_plan에 배정한다. 계획은 그 사건을 읽고 기존 preparation_requests 또는 근거 있는 연구 질문 해소로 대응한다. 요청받은 준비는 그 QU를 실제 후보의 basis_refs에 결박하고, 그 과제 결과의 다음 계획이 답의 충분성을 판단해 child를 해소한다. 계획/준비가 기존 질문을 처리 중이면 같은 사건을 새로 만들지 않는다. 새로운 수학 조사를 maintenance 안에서 수행하거나, 배정 없이 ‘research로 넘김’만 기록하지 않는다.

`questions.validate_extensions`는 모양·배정 피복·역할·기초·현재 입력 참조·이관 대상·generation을 검사한다. `_apply_question_resolutions`는 같은 규칙을 현행 상태에 다시 적용한다. handler가 해소하려는 대상만 `questions.close`로 닫는다. history의 resolution_ref는 **수락된 담당 execution**이며 action의 요청이나 파일 이름만으로 해소하지 않는다. 기본 whole-response bundle 안에서 질문 처분·child 생성·실제 후속을 원자적으로 적용한다. accepted receipt 재전달은 이미 적용한 결과를 반환한다.

증거의 실제 소비 경계도 함께 고친다. 현재 submission의 question evidence는 `_validate_reference`로 workspace 파일을 허용할 수 있지만 적용의 `academic.evidence_record(..., self._academic_evidence)`는 저장소에 아직 없는 `workspace:` 문자열을 그대로 회수할 수 없다. 새 `submission.resolve_output_evidence(ref, *, output_files, read_artifact, resolve_record) -> dict`는 제공 기록이면 기존 academic 증거 resolver를 호출하고, `workspace:<상대 경로>`이면 **이번 실행의 수집된 output_files**에서만 artifact_ref/sha256/bytes를 찾는다. `repository.sealed_bytes`의 기존 대조로 실제 바이트를 확인하고 `{artifact_ref,sha256,bytes}`를 반환한다. 빠진 파일·수집 제외·다른 실행의 임의 경로는 반려한다. `_apply_question_resolutions(execution_id, *, read_artifact)`의 reader는 이번 제출의 봉인 staged artifact와 기존 snapshot을 읽는 실제 후보 reader를 받는다. CAS 전 새 파일을 현재 head에서 찾으려 하지 않는다. 이력에는 확인한 고정 artifact 참조를 보존한다. dismissed의 새 출력 근거와 질문 재개 근거도 이 함수를 공유한다. 스냅숏/파일 읽기 검증 정본을 새로 만들지 않는다.

늦은 결과는 원 generation·고정 대상에 대해서만 수용한다. 같은 실행이 읽지 않은 신규 대상까지 닫지 않는다. 배정 뒤 중복 보고만 추가된 것은 무관한 bookkeeping 변화이므로 실제 판단을 무효화하지 않는다. 실제 대상 내용·권한·효력 변화는 CurrentnessChanged, 처음부터 없는 참조·잘못된 처분은 출력 오류다. R4~R5 실패 분류 정본을 재사용한다.

### 6.4 대기 해소와 다음 업무

`QuestionEngineMixin._advance_question_dependents(question_id, resolution_ref) -> bool`을 새로 두고, 수락된 해소/이관 영수증을 실제 대기 소유자에 전달한다. 수행 성공이나 승인으로 변환하는 함수가 아니다.

1. contract_review_input → §5.3의 `_resume_contract_review_waits`가 같은 계약의 독립 검토를 연다. 운영의 문제 없음은 계약 승인과 다르다.
2. revision_dependency의 deferred 사유가 그 QU인 경우 → 해당 원 action의 남은 대상을 같은 출처로 다시 준비한다. 질문 close만으로 required를 지우지 않는다. 준비의 revised/dismissed 등이 의무를 종결한다. `revision_resolutions`의 deferred에 선택 `question_ids`를 추가하고 배정/입력에 있는 실제 QU만 허용해 이 연결을 기계가 식별하게 한다.
3. 수행의 waiting/assessment_input → 실제 입력 변화와 결과를 계획 사건으로 전달한다. 필요한 완료 판정·선택은 원 계약과 현재 근거로 다시 판단한다. 종료 실행을 되살리거나 질문 해소만으로 과제를 completed로 만들지 않는다.
4. user/research child 또는 installation 처분 종료 → 부모 QU를 pending으로 전환해 그 답/수리 결과가 운영 질문에 충분한지 확인한다. 같은 영수증은 한 번만 소비한다. 답변이 user pause 해제를 포함하지 않았다면 pause는 그대로다.
5. 질문이 닫히며 착수 기초가 바뀌면 기존 `_refresh_readiness`·readiness 사건·`schedule_reconsideration`이 다음 계획을 만든다. 독립 과제를 전부 재개하거나 원 문헌 과제의 종속 과제를 자동 완료로 만들지 않는다.

`questions.action_waits(action,instance,runtime,*,records=None)`를 새 공통 gate로 정하고 기존 `user_waits` 호출부를 이 이름으로 바꾼다. 기존 user 차단 의미를 보존하며 operations의 blocks를 실제 읽기 대상/과제에 적용한다. diagnostic 운영·maintenance·intent와 계획은 해소 판단을 할 수 있게 통과한다. preparation은 operations 질문 때문에 예외 종결/정련을 할 수 없게 막지 않되 기존 user 결정 gate는 유지한다. 연구 수행과 그 대상의 승인/입력 대기는 영향받은 operations 의무가 남으면 기다린다. origins별 대상·차단 교집합만 계산해 새 보고의 비차단 대상까지 전면 차단하지 않는다.

activity의 실제 미완료 의무에는 `wait_rules`의 새 `question_dependency`(condition=`{question_id,generation}`, next_owner=담당 role)를 사용한다. handling.waiting을 해소할 때만 원 owner_activity를 resume하고, 모든 미종료 execution과 예약 반환을 확인한 뒤 후속 execution을 연다. 처리 보고의 종료와 지속 QU 의무를 구별한다. 처리 완료 시 같은 활동을 finish하고 result_refs에 담당 execution과 해소 근거를 남긴다.

사용자 pause/HOLD, 정비 fence, provider/권한/용량 관문을 우회하지 않는다. 질문은 정지 중에도 이미 수락된 보고와 원장에 보존될 수 있지만 자동 연구/triage 호출은 새로 시작하지 않는다. 기존 정확한 제한 복구 권한이 별도로 허용하는 범위만 그 기존 gate를 통과한다. `_advance_question_dependents`가 runtime.status=ready 또는 user_pause 삭제를 직접 하지 않는다. 정상 재개 권한 뒤에 남은 의무를 다시 배정한다. 예약 감독은 `research_wake_reasons`의 pending/due 운영 질문 사실만 보고 실행기를 깨울 수 있으며 HOLD·pause 차단이 항상 먼저다.

### 6.5 사례의 전후와 필요한 분기

| 상황 | 수정 후의 구체적 결과 |
|---|---|
| 계약은 적합하고 도구의 미래 성공만 미입증 | 검토자는 수행 책임·실패 반환을 확인해 승인 가능하다. 수행자가 실제 노출/필요 호출을 확인한다. 문헌조사 자체를 미리 수행하게 하지 않는다. |
| 검토가 정말 필요한 프로필/원자료를 못 읽음 | unresolved → contract_review_input+QU → maintenance/해당 담당 execution → 근거 확보 → 독립 계약 검토 → readiness/계획. 새 계약 판본은 필요하지 않다. |
| AI가 잘못된 전제로 필수 개정을 요청함 | 준비의 dismissed → 해당 요청/부모 writer 대기 종결 → 같은 계약에 새 독립 검토 1회 → 승인되면 선택 가능. 과거 부정 판정 OR로 필수 개정이 부활하지 않는다. |
| 실제 계약 결함 | revision_required → revised revision+1 → 독립 검토 → 계획. 정상 경로에 별도 재심사를 더하지 않는다. |
| 실제 scholarly 실행 지원 실패 | 수행의 사실·현재 프로필·제한 범위 → 같은 지원 의무 QU → maintenance의 조사. 설치 결함이면 operational_review repair→실제 복구와 검증을 기다린다. 자료원 429·부분 응답은 서버/모델 전체 실패로 바꾸지 않는다. |
| 자료 부족/사용자 결정/문제 없음 | 자료는 record_change 대기 또는 회수 담당, 사용자 선택은 연결된 user QU, 문제 없음은 근거 있는 resolved. 기술 수리 미완료를 resolved로 닫지 않는다. |
| 같은 의무가 E05/E10/E12에서 반복 보고 | 같은 descriptor/명시 QU에 origins와 근거를 합친다. 아직 실행 중인 담당은 하나다. 새 근거는 다음 고정 입력/후속으로 전달한다. |
| 등록 CAS 직후 재시작, 실행 중 재시작, 결과 재전달 | 같은 QU+generation의 기존 action/execution/receipt를 재사용한다. owner 문자열만 남은 열린 질문은 재조정이 action에 연결한다. 실제 종료 확인 전 두 번째 담당을 시작하지 않는다. |
| 사용자가 연구를 정지함 | 미해소 QU·개정·후속을 보존하고 자동 호출을 멈춘다. 질문을 닫거나 설치 수리를 마쳐도 user_pause/HOLD를 해제하지 않는다. |

## 7. 계약 개정 밖의 주요 인계

의도 해석의 `governance_engine._apply_governance_intent`는 현재 check의 approved 이외 값을 모두 `_queue_intent_rework`로 보낸다. `revision_required`의 실제 원문 왜곡/소유자 오류는 이 경로가 맞다. 반면 읽지 못한 필수 근거만 있는 unresolved에 같은 원문을 새로 해석하게 할 이유는 없다.

후속 구현에는 다음 작은 분리를 포함한다. `governance.check_import`는 동일 bundle의 후속 독립 검사 이력을 보존한다(`bundle.check_history[]`에 기존 check를 이동하고 현행 check를 저장). unresolved이면 새 `waiting_actions.kind=import_check_evidence`, action은 같은 stage=check/import_id/원문·봉인 해시를 유지한다. `question_ids`와 실제 미확정 근거의 basis를 대기에 결박한다. `GovernanceEngineMixin._resume_import_check_waits()`는 관련 질문 해소나 실제 근거 변화에서 같은 묶음의 새 독립 check를 한 번 연다. 실행/출력 수리는 기존 한도와 계보를 사용한다. 재검사도 unresolved인데 근거가 같으면 다시 배정하지 않는다. 원문/묶음이 실제로 바뀌면 기존 rework가 새 묶음을 만들고 옛 대기를 은퇴시킨다. 재검사 승인도 사용자 명시 승인·owner 적용을 대신하지 않는다. `wait_rules`·저장 의미 검사·governance 봉인 및 current_import에서 check_history와 현행 check의 관계를 함께 맞춘다. 최초 입력 해석의 정상 승인 경로와 위임의 두 독립 판단은 유지한다.

현재 `check_import`는 기존 check가 있으면 `check is sealed; reauthor instead`로 거부한다. 이 조건을 해당 import_check_evidence의 해소와 새 독립 실행이 확인된 경우에만 후속 검사 허용으로 바꾼다. `import_seal`의 해시 제외 집합에 check_history도 넣어 검사 이력 추가가 원 해석 묶음의 불변 SHA를 바꾸지 않게 한다. 개별 check의 exact hash와 실행·묶음 결박 검사는 유지한다. 저장 검사에서 check_history의 각 봉인과 현행 check가 같은 원문/묶음에 대한 실제 별도 실행인지 확인한다. 최초 초기화의 같은 비승인 분기가 있는지도 `initialization_engine`에서 함께 대조·수정한다.

나머지 확인한 주요 연결은 현재 의미를 유지한다.

- 연구 보고→results 보존→계획의 의무별 완료 집계: submitted/no_result는 완료 값이 아니며 partial/waiting의 근거도 재사용한다. 새로운 blanket 수리 의무를 넣지 않는다.
- 새 형식 결과→중앙 형식 검사→동일성 scope/자리/이의/판정→K 사용 효력→목표 감사: 각 판단은 서로의 성공을 대신하지 않는다. `_defer_review_for_research`의 고정 조사 요청은 `_apply_review_research`에서 같은 자리에 돌아오며 실패/취소도 실제 범위로 남긴다.
- 지식 개정→영향 계획/독립 확인→현재성·CAS: 출처 인용과 실제 효력 의존을 구별하는 기존 정본을 유지한다. R2의 dismissed는 기존 사용 정지나 영향 전파를 근거 없이 복원하지 않는다.
- 운영 retry/resume→대상 종료/예약 반환→같은 의무의 후속, 설치 repair→복구 AI/검증/launcher: 이미 후속이 있는 경우 reconcile_recovery가 중복을 피하는 현행 구조를 재사용한다. QU도 이 실제 결과를 기다린다.
- 사용자 질문→원문 독립 해석/적용된 결정→해소, 외부 행동→허가/전송/unknown/영수증: 질문을 닫는 AI 재량으로 사용자 권위나 미확정 외부 효과를 대체하지 않는다.
- 목표 완료→새 일반 연구 중단·미해석 입력/실행 중 의무 정산→학술 요구 후속: 종료 정산은 과제 이행이나 보류 산출 편입이 아니다. 새 질문 연결에서도 이 제한을 유지한다.

## 8. 구현 변경 경계와 실제 선행관계

공통 해시/검사 task가 이미 소유한 `core_engine.py`, `context_store.py`, `submission.py`, `submission_tool.py`, `integration.py`, `input_basis.py`, `scripts/이음새-정본.md`는 이번 설계 task가 고치지 않았다. R2~R3 구현자는 그 task의 **수용판**을 사용한다. 함수 내용이 멀리 떨어졌다는 이유로 병렬 같은 파일 수정을 독립 writes로 배정하지 않는다.

권고하는 구현 묶음은 다음과 같다. task를 지나치게 쪼개 새 인터페이스 소비를 미루지 않는다.

| 구현 묶음 | 실제 수정 파일·생산자/소비자 | 선행·완료 범위 |
|---|---|---|
| A. 역할·개정·운영 질문 end-to-end | contracts, revisions/revision_engine, planning/planning_engine/lifecycle_engine, questions/question_engine, decision_engine, core_engine/context_store/submission, operational_dispositions, record_schemas/{schemas,__init__}, wait_rules, governance의 task_scope revise 생산, reporting/state_checks/activities의 관련 투영·실제 소유자, supervision/wake. SKILL·공통 실행·학술자료 활용·관련 역할 계약·이음새 정본·시험과 공식 미러를 같은 배정에 포함 | 본 설계 수용 + shared-validation-hashes 수용판. §4~6의 전이·schema·지급 입력·실제 handler/해소/독립 승인/계획을 함께 구현한다. 공유 core/context/submission을 별개 병렬 소비자가 발명하지 않게 A 한 task를 권고한다. |
| B. 의도 검사 미해결의 입력 대기 | governance_engine/governance 및 필요한 저장/대기 계약, 의도-해석·입력-소비자 문서·해당 시험·미러 | A가 제공하는 QU 해소·wait/저장 정의가 필요하다. 따라서 A 수용판에서 시작한다. 같은 schema/core 파일이 필요하면 이 선행관계로 충돌을 피한다. |
| C. 통합 검토·남은 최소 확인 | manager의 seams/context/plan 갱신, 통합된 역할 계약 10개+독립 운영의 최종 대조, 공식 미러 일치 | A/B 및 독립 수리 수용 뒤 실제 남은 불확실성만 확인한다. 설계 문서의 작성이나 enum 존재로 R1~R3을 수용하지 않는다. |

독립적으로 병렬 가능한 writes는 기존 저장 payload 개선, worker 진단, Windows/패치 안내다. A의 역할 문서가 공통 실행을 바꾸므로 windows-patch-guidance의 공통 문서 변경 수용판을 소비하거나 manager가 충돌 없는 후속 순서로 배정한다. 제품 변경에 맞춰 공식 생성기 `D/../writing-skills/scripts/build_skill_mirrors.py`로 미러를 만든다. 생성기의 전체 비교 대상과 이번 task의 통합 경로를 구별한다.

공유 seams에 추가할 항목은 §5.1의 revision 정본·effective_contract_review·reconsideration, §6의 question descriptor/key/origins/handling·action 좌표·resolution_schema/action_waits·배정/해소/후속 함수, §7의 import_check_evidence와 check 이력이다. 기존 계약 승인·질문 해소·과제 완료의 다른 의미와 오류/현재성 경계를 함께 적는다. 저장은 현행 계약 하나를 고치고 구판 자동 변환·alias를 만들지 않는다. 모든 새 필드는 실제 생산값·참조와 저장 왕복이 있어야 하며, 산문만 있는 미생산 optional을 허용하지 않는다.

현재 개발 snapshot_paths에는 docs가 없다. manager가 이 설계를 수용한 뒤 후속 inputs/objective에는 `C:/math/docs/do-math/flow-repair-20261021/role-flow-design.md`를 읽기 전용 원자료로 명시한다. 정리될 이 task workspace의 경로를 영구 의존으로 쓰지 않는다.

## 9. 후속 최소 검증과 수용 기준

이 task의 검증은 정적 추적과 §1의 작은 호출뿐이다. 아래는 **구현 task가 수행할 검증 설계**이며 수행 완료를 주장하지 않는다. 기존 `scripts/run_tests.py`와 `scripts/tests/시험-지침.md`의 선택 실행 원칙을 따른다. 공통 성공을 반복해 전체 연구 효능으로 확대하지 않는다.

| 필요한 불확실성 | 가장 작은 실제 경계와 단언 |
|---|---|
| 검토 책임이 실제 문맥에 도달하는가 | reading_map/prompt_documents와 실제 준비 입력에서 공통+역할 문서 순서·내용 해시, scholarly 안내와 exception 입력을 확인한다. structure/doc-code 및 unit.test_planning_reading_map, sim.test_planning_document_context의 해당 모듈을 수정한다. 실제 모델의 심리 개선까지 자동 인증하지 않는다. |
| 정상·미해결·예외 개정이 모두 진행되는가 | sim.test_planning_engine_receivers/ revision_transitions/ revision_obligations에서 실제 후보·독립 검토 응답을 수신한다. approved, 결함→revised→새 승인, unresolved→QU→자료→같은 판본 승인, required AI→dismissed→독립 승인, 사용자 required dismissed 반려를 각각 확인한다. 내용/판본·요청 source_refs·부모 writer 대기·활동·후속 계획을 단언한다. |
| 역사적 반려와 재검토가 다시 막는가 | 같은 판본의 과거 부정·후속 승인을 보존하고 effective_contract_review/task_ready가 후속 승인만 소비하는지 확인한다. 재검토 negative→재dismissed는 동일 key 자동 실행이 늘지 않고 conflict 의무가 하나 남는지 본다. 다른 대상/실제 새 계약·전제는 독립적으로 진행돼야 한다. |
| 운영 질문이 실제 실행되는가 | flows.test_governance_question_flow 또는 새 제한 flow에서 질문 응답 생산→중앙 접수→실제 queue action→실행 등록→근거 처분→QU 해소/대기→영향받은 검토/계획까지 한 번 이어간다. owner 필드·enqueue 호출 횟수만 확인하는 시험으로 대체하지 않는다. |
| 중복·재시작·늦은 결과 | 서로 다른 보고가 같은 descriptor/명시 QU를 제출한 뒤 새 Repository에서 첫 load한다. 등록 전/등록 뒤/담당 실행 중 경계에서 재조정해 QU+generation당 action과 미종료 handler가 하나인지 확인한다. 결과 재전달의 같은 receipt, 뒤에 추가한 대상의 미해소 보존, 원문 reports의 전건 보존을 단언한다. 자연어 모든 동의어의 자동 중복 제거를 시험했다고 쓰지 않는다. |
| 네 가지 운영 결과와 실제 후속 | 문제 없음 resolved, 자료 부족 record_change 대기/실제 자료 도착 wake, 사용자 결정 child→답변→부모 재판단, 기술 결함→OD repair→기존 복구 결과를 연결한다. 설치 수리의 실제 adapter는 기존 수리 flow 중 바뀐 경계만 확인하고 새로운 원격 연구 호출은 하지 않는다. |
| 정지·권한·독립 범위 | pending/실행 중 질문에 pause/HOLD를 적용하고 새 모델 호출·연구 실행이 생기지 않는지, 결과 접수 후에도 정지가 유지되는지 확인한다. 동일 target의 주기 점검과 질문 판단이 실패 해소에서 섞이지 않고, 검토 비공개 질문이 일반 운영 입력에 노출되지 않아야 한다. |
| 스키마·오류·저장·공통 정의 일치 | 단위 검사는 새 필드 모양뿐 아니라 실제 생산값을 게시하고 첫 reader 복원 및 schema의 역방향 불허를 확인한다. 빠진 request/evidence/이관 참조·잘못된 generation·user 의무 종결은 출력 오류, 읽은 전제의 실제 변경은 CurrentnessChanged, CAS/환경 실패는 원 실패로 분류한다. shared-validation-hashes의 같은 검사 함수를 소비한다. |
| 의도 검사 분리 | 같은 정확 묶음의 check unresolved→관련 자료 변화→새 check approved를 확인한다. import_seal·원문 피복·check_history·명시 승인/owner 적용은 보존되고, 그 사이 interpret 실행과 재저작 계수가 불필요하게 늘지 않아야 한다. 실제 revision_required는 원 rework 경로를 유지한다. |

구현 후 수용 판단은 다음 결과로 한다. 타당한 계약은 고칠 필요 없이 독립 승인·선택으로 이어지고, 실제 결함은 수정되며, 잘못된 AI 요청은 근거 있게 끝나고, 열린 운영 의무는 담당 실행 또는 명시된 대기/이관을 가진다. 해소 뒤에는 영향을 받은 판단이 다시 열리며 사용자 정지는 유지된다. 유지한 역할의 전문 판단·원문·권한·형식/현재성 경계도 보존돼야 한다.

단순 구현 세부로 남길 수 있는 것은 함수 내부 순회·자료구조의 지역 변수·시험 fixture 이름이다. 정확 field/enum·권위·전이·실제 consumer 경계는 이 문서의 권고안을 소비한다. 외부 사실이 없어 남는 것은 당시 공급자의 전체 도구 노출과 모델 내부 원인, 모든 프로필에서의 향후 실제 도구 동작이다. 이 불확실성을 해결할 때까지 역할/인계 수리를 기다릴 이유는 없다. 과거 연구 원장·work·HOLD/예약 작업은 이 개발의 검증 대상 쓰기로 사용하지 않는다.
