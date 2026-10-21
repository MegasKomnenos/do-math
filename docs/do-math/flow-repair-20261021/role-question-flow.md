# 역할 책임·개정 예외·운영 질문 수리

정본은 `.claude/skills/do-math/`다. 이 문서는 `role-question-flow`의 실제 구현과 확인 범위를 설명한다. 코드 안의 공용 이음새는 `scripts/이음새-정본.md`로도 옮겼다. 선행 설계의 필드 수를 목표로 삼지 않고 기존 QU·action·execution·원자적 bundle 적용과 저장 검사를 사용했다.

## 사용 결과

계약 검토의 정상 승인은 기존 ready·선택 경로로 진행한다. 실제 결함은 후보 계약 교체와 새 독립 검토로 이어진다. `unresolved`는 계약을 다시 쓰게 하지 않고 부족한 판단 자료의 QU와 실제 처리 실행으로 연결한다. 자료·답변의 실제 영수증 뒤 같은 계약 판본을 새로 검토한다.

AI 개정 요청의 잘못된 전제는 `dismissed`로 해당 요청 출처만 종결할 수 있다. 계약 판본·완료 의무를 바꾸거나 준비자가 승인한 것으로 처리하지 않는다. 필요한 새 독립 검토는 같은 계약·기초에 한 번 열며 반복 충돌은 실제 `decision_conflict` QU에 남긴다. 사용자 `task_scope/revise` 권위는 기계가 `user_decision_refs`로 포착하고 기각을 반려한다.

운영 질문은 같은 의무의 원 보고를 QU에 축적하고 실제 maintenance 또는 EX 대상 operational_review action에 연결한다. 배정 세대·대상, 실행·활동, 근거 있는 처분·대기·이관과 후속을 저장한다. 기존 사용자 정지·HOLD·허가·공급자·용량·설치 복구와 실제 종료 관문은 유지한다.

## 역할 모집단과 유지·변경 이유

실제 모집단은 `contracts.ROLES`, `reading_map`, `prompt_documents`와 `core_engine._apply`의 소비 경로를 기준으로 대조했다. 선행 `role-flow-design.md`의 평가와 현재 계약·코드를 함께 사용했다.

| 역할·동적 단계 | 유지한 전문 판단과 이유 | 이번 변경 |
|---|---|---|
| 후보 준비, 평가·관찰 규칙 보충 | 질문·범위·완료 의무의 저작과 선택·독립 승인 분리. 보충은 사용자 원 계약을 대체하지 않음 | 기각·질문에 연결한 보류, 실제 필요한 산출만 의존, 원 학술 계약의 AI 검토 요청에도 실제 준비 수신자를 둠 |
| 연구 계획 | ready/returned 전건 처분, 지정 판정의 완료 집계, not_assessable와 권위 있는 면제·이전 | QU 연구 child의 실제 사건·준비·결과 판단, 질문 close와 과제 완료 구분 |
| 연구 수행 | 계약 안의 조사·증명·계산 방법 선택, 실패·부분 결과 보존. 형식·완료·목표 판정은 후속 소유자 | 실제 도구 확인과 지원 실패 보고를 수행 책임으로 명시하고 같은 QU에 새 근거 연결 |
| 작업 계약 검토 | 다섯 관점·전건 대조·독립성 유지. 수행 가능한 질문과 판정 가능한 완료 기준을 확인 | 원문·반대 근거·자기 오독과 영향을 지적 전에 확인. 미래 수행 성공을 사전 증명 의무로 만들지 않음. unresolved/실제 개정/예외 재검토 분리 |
| 동일성 scope/initial/organize/answer/judge·판정 재심사 | 전건 의미 대조, 이의 철회·기각·고정 조사·유한 한도와 판정 효력 구별 | 기존 전문 절차 유지. 비공개 질문은 원 검토 안에서 처리하고 공개 뒤에만 공용 질문 담당으로 연결 |
| 목표 감사·추가 감사 | 현재 목표와 실제 유효 결과의 대응, 부분 결과와 목표 해결 구분 | 운영 해소를 수학적 긍정 판정으로 쓰지 않음. 전문 계약 유지 |
| 보충 조사: 과제/검토 고정 질문 | 고정 질문·원자료·독립 범위와 실패의 원 자리 반환 | 고정 조사 안의 확장 금지 유지. 일반 역할이 받는 공통 질문 계약만 수정 |
| 운영 점검: live/종료 후/질문 | 실제 EX의 여섯 처분, 현재 근거 제한, replay 안전성과 종료·설치 복구 관문 | 지정 판정의 집계와 새 수학 판정 발명을 구별. 실제 EX를 받는 `stage=question`과 QU 처분 연결 |
| 의도 해석: interpret/check/위임 | 원문 전건 피복·독립 검사·명시 승인·owner 적용 | 공통 QU·근거 인터페이스 제공. import check 비승인 분기의 수리는 다음 task가 소유 |
| 유지보수: 일반/초기 진단/종류/impact/질문 | 절차별 대상·권한·완료 조건, 종류·영향의 독립 판단, 중앙 상태와 수학 의미의 무단 변경 금지 | 실제 subject·보고·배정 기초를 받는 `maintenance:question`과 기계가 소비하는 질문 처분 |
| 기계 formal/trust/external | 형식 결과·신뢰 전환·외부 unknown/영수증과 사용자 허가 구별 | 기존 기계 action 유지 |
| 모델 없는 예약 감독·별도 설치 복구 AI | HOLD·pause·lock·설치 판본·실제 수리 검증. 내부 열 역할과 별도 계약 | 감독은 pending/due QU의 wake 사실만 사용. 새 의미 판단·허가·정지 해제는 만들지 않음 |

문서 변경은 기존 common 지급 경로 안에 뒀다. Windows 명령·단일 파일 패치 안내를 보존했다. `core_engine._context`의 scholarly 안내도 같은 수행/검토 책임을 전달한다. 실제 프롬프트 지급은 기존 읽기 시험으로 확인했다. 이 확인은 미래 모델의 준수나 과거 모델의 내부 원인을 인증하지 않는다.

## 개정과 승인 정본

- `revisions.resolution_schema/submission_errors`: revised/unchanged/dismissed/deferred/delegated의 한 정의를 생산자·중앙이 사용한다. 기각은 요청 출처·이유·근거를 요구하고 실제 user revise를 지우지 못한다.
- `capture_targets/user_revision_sources`, `_bind_revision_action`, `_enqueue`, 재결박: 요청 출처·사용자 권위·부모를 합집합으로 보존한다. writer 예약만으로 필수 변경 이유를 만들지 않는다.
- `resolved_targets/remaining_targets`: 종결한 대상별 출처와 나머지를 부모·자기 revision_dependency·위임·실패 action 정산이 함께 소비한다. 다른 출처·대상·live 실행은 유지한다.
- `planning.revision_required/effective_contract_review`: 현재 미해소 요청과 현재 전제의 마지막 유효 검토를 따로 판단한다. task_ready와 lifecycle이 같은 승인을 사용한다.
- `task.waiting.kind=contract_review_input`: 계약 SHA, review basis, missing item, question_ids와 원 검토를 보존한다. `_resume_contract_review_waits`는 자료 기초 변화 또는 관련 실제 해소 뒤 같은 판본의 새 독립 검토를 연다.
- `task.contract_review_reconsiderations`, `action.contract_review_reconsideration`: 기각과 원 판단을 결박한다. 같은 계약·basis의 자동 재검토는 한 번이며 재차 기각하면 안정된 conflict 의무가 남는다. 저자·원 검토·기각 생산자의 문맥을 잇는 재검토는 수락하지 않는다.
- 학술 `revision_required`의 `revision_fields`는 원 계약과 AI 평가·관찰 규칙을 구별한다. unresolved로 평가·규칙을 삭제하지 않는다. 원 계약은 일반 준비 수신자가 AI 요청을 기각하거나 실제 사용자 결정으로 보류할 수 있으나 후보 저작으로 원 학술 계약을 바꿀 수 없다.

deferred의 question_ids는 지급 QU 또는 같은 응답의 `output:questions/N`이다. 후자는 정확한 route·대상을 검사한 뒤 실제 QU ID로 저장한다. 질문 해소는 보류한 준비를 다시 열 뿐 원 개정을 이행한 것으로 처리하지 않는다.

## QU 등록·배정·실행·처분

`questions.py`가 descriptor/key·원 보고·중복·처분·대상 차단·저장 결박의 정본이다. `question_engine.py`가 등록·실제 배정·실행 연결·수신·후속의 정본이다. 별도 티켓 원장은 추가하지 않았다.

operations의 `{kind,subject_ref,requirement_ref}`는 문장·실행 ID와 독립된 의무 키다. 같은 키 또는 지급된 explicit existing_question_id의 보고는 origins와 원문 reports에 보존한다. 다른 descriptor의 명시 동일성 판단도 원 보고에 남긴다. 이미 해소한 동일 관찰의 재보고는 다시 열지 않고, 새 대상·명시한 실제 관찰 기초가 있으면 후속 세대를 보존한다. 임의 자연어의 모든 의미 중복을 자동 판별하지 않는다.

`handling={generation,role,state,action_id,owner_activity_id,execution_ids,waiting,last_resolution_ref,observation_basis}`는 엔진 생산값이다. `_reconcile_question_actions`는 등록 candidate의 같은 CAS와 upkeep/첫 owner 갱신에서 QU를 실제 action에 연결한다. `question_ids/question_generation/question_target_ids`는 고정 배정 좌표다. queue/live/실패 대기의 같은 의무를 재사용하고 다른 목적의 주기 점검과 합치지 않는다.

기본 handler는 실제 subject의 maintenance:question이다. 실제 EX 처분이 필요할 때 operational_review:question을 사용한다. `_register_execution`이 실제 실행·활동을 연결한다. operations_questions는 reports, assigned_generation/assigned_target_ids, subject, record_bases, related_waits를 지급한다. record_bases는 실제 대상·자료·프로필 기초이며 보고 수 증가 자체는 현재성 변경이 아니다.

resolved/superseded/waiting/transferred는 배정 전건에 대응한다. 운영 응답의 generation·affected_ids는 고정 action과 맞아야 한다. 일부 배정 범위만 확정됐으면 대기를 반환한다. 뒤에 추가된 대상과 읽지 않은 새 관찰은 늦은 응답이 닫지 않는다. 같은 대상의 새 관찰도 원 입력과 현재 origins를 비교해 다음 세대에 남긴다. 다음 담당은 실제 종료·예약 반환 뒤 열린다.

superseded는 실제 같은 책임의 열린 replacement로 보고·대상·근거를 옮긴다. `current_question(runtime, QU)`로 replacement 사슬을 따라가며 자기 참조·순환·책임 혼합을 거부한다. 대체 원 질문의 close만으로 아직 열린 수신 의무를 해결했다고 쓰지 않는다.

waiting은 실제 question/record_change/time/operational_disposition 조건을 보존한다. transferred는 다른 운영 handler action, 같은 응답의 user/research child, 또는 실제 repair OD로 연결한다. child의 user 답변·연구 결과와 실제 OD 복구 영수증은 부모를 재판단하게 한다. 연구 child는 question_research_followup 사건으로 계획·준비 경로에 전달한다. 운영 처분의 user 질문과 명시 child가 같으면 같은 QU를 사용한다.

`_advance_question_dependents(QU,resolution_ref)`는 실제 수락된 해소 영수증을 한 번 소비하고 영향받은 계약 검토·보류한 개정 준비·연구의 다음 계획·부모 질문에 연결한다. 활동은 question_dependency에 원 의무를 보존한다. `action_waits`는 기존 user gate와 origins별 operations.blocks의 미해소 대상 교집합을 적용하며 진단·계획·예외 종결 준비를 막지 않는다.

## 근거·저장·오류

대상별 후속의 정본은 `questions.question_scope_state(runtime, QU, target_ids)`다. 반환은 `{resolved, resolution_refs}`이며 부분 해소·replacement의 해당 범위를 따라간다. 계약 입력 대기는 `question_scopes`와 원 검토 입력의 `question_resolution_basis`, 개정 deferral은 `question_scopes`, 운영의 child 대기는 엔진이 결박한 고정 `target_ids`를 저장한다. 다른 대상이 남았다고 이미 해소한 대상의 검토를 막지 않고, 읽지 않은 새 관찰도 이전 해소로 덮지 않는다. 이미 본 영수증만 있는 같은 입력의 unresolved 재보고는 새 검토를 자동 반복하지 않는다. 후속 의도 검사도 자신의 고정 범위와 영수증 기초를 이 함수로 비교할 수 있다.

기존 적용 reader가 workspace 문자열을 기존 head에서 읽으려는 정적 결손을 확인했다. `submission.resolve_output_evidence`는 이번 봉인 output_files의 정확한 artifact_ref/SHA-256/bytes와 실제 바이트를 `repository.sealed_bytes`로 대조한다. `_resolve_execution_evidence`를 질문·기각·재발이 함께 사용한다. 실제 적용은 봉인 file_refs와 snapshot reader를, preview는 staged artifact와 manifest를 전달한다. 다른 실행의 임의 workspace·수집 제외 파일·변조된 바이트는 허용하지 않는다.

처음부터 잘못된 참조·generation·사용자 의무 면제는 출력 오류다. 실제 대상·권한·내용 변화는 기존 CurrentnessChanged 경로다. 공유 고정 해시 검사·영향 독립 검토·저장 CAS와 환경/게시 실패 분류는 선행 수용판을 유지했다.

새 action·QU·출처·재검토·대기 필드는 닫힌 저장 schema와 의미 검사, 첫 reader·왕복·보고·retention 참조에 연결했다. 질문 AI 처분은 실제 response integration 영수증에 결박한다. 구판 기본값 보충·별칭·변환은 추가하지 않았다.

선행 영향 검토 시험은 실제 변경의 CurrentnessChanged와 고정 mutation catalog를 사용하도록 갱신했다. 적용 뒤 replay도 같은 원판 catalog를 쓴다. 실행 중 추가로 드러난 replacement-ID 생산자 fixture의 누락 hash/catalog도 고쳤으며 제품 검사를 약화하지 않았다. 저장 batch 선읽기의 공개 정의도 제품 이음새로 옮겼다.

## 직접 확인과 한계

task evidence의 공식 run_tests 보고가 실행별 실제 근거다. 실패 후에는 오류·코드를 읽고 해당 fixture/문구 또는 실제 결함을 고친 뒤 필요한 ID만 다시 확인했다. 주요 직접 확인은 다음과 같다.

- 작은 반례로 옛 기각 출처 무검사·역사적 반려 OR·운영 의무 연결 부재를 먼저 확인했다.
- 실제 worker/중앙 제출/봉인 파일/QU/action/EX/저장/재시작을 지나 unresolved → maintenance 근거 → 같은 판본 승인·ready, dismissed → 독립 승인·선택, 반복 기각 → 하나의 conflict 의무를 확인했다.
- 실제 source 등록과 user question_answer 결정으로 대기 → 다음 부모 handler → 해소를 확인했다. EX subject의 실제 operational_review와 OD continue도 연결했다.
- 별도 Repository 첫 load, 같은 의무의 다른 보고·명시 QU·재시작, live 추가 대상과 읽지 않은 같은 대상의 새 관찰, generation 반려, pause 보존과 새 triage 미시작, 변조/누락 근거를 확인했다.
- 사용자 revise 출처·저장·AI 기각 반려와 권위 제거 반례, 대상별 writer 의무·부모/위임·실패 정산, 실제 개정·새 승인과 기존 원장 유지, 실제 기계 생산값의 저장 대응을 확인했다.
- 설치 복구의 기존 실제 handoff·종료 관문과 pending OD가 해소 영수증이 아니라는 경계를 확인했다. 새 설치 복구 AI나 실제 모델·학술·Lean 도구·원 연구는 호출하지 않았다.

전체 T2+flows·실제 외부 경계·최종 review는 objective가 정한 후속 통합 확인의 범위다. 이 선택 확인을 모든 저장 분기·모든 프로필의 도구 성공·모델 행동 준수로 확대하지 않는다. 의도 check의 unresolved/봉인 이력 수리는 변경하지 않았고 다음 task가 이 QU·근거·대기 인터페이스를 소비한다. 원 연구·감사·HOLD·예약·canonical source_repo와 다른 task 파일은 수정하지 않았다.
