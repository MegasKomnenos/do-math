# 역할 책임·개정 예외·운영 질문의 실제 연구 흐름 수리

## 얻어야 할 결과와 선행판

context R1~R3의 사용 결과를 구현한다. 수행 가능한 계약은 실제 연구 선택/수행으로 이어지고, 실제 결함은 고치며, 잘못된 AI 개정 요청은 근거 있게 끝낼 수 있어야 한다. 운영 질문은 실제 담당 실행 또는 명시된 대기/이관과 근거를 가지며 해소 뒤 영향을 받은 판단으로 이어져야 한다. 역할 문서·enum·배정 함수만 만든 것을 완료로 보고하지 않는다.

이 task는 role-flow-design, shared-validation-hashes, windows-patch-guidance가 모두 수용된 공용 소스 사본에서 시작한다. 자기 inputs의 context/plan/seams, task.json, 정본 AGENTS.md·scripts/이음새-정본.md·scripts/tests/시험-지침.md를 먼저 읽는다. 시작판 코드와 세 선행 report/integration을 확인해 이미 해결된 부분을 중복 구현하지 않는다. 원 연구와 감사 자료는 읽기 전용이다.

현재 snapshot_paths에는 docs가 없다. 반드시 공용 소스의 다음 절대 경로를 읽기 전용으로 읽는다. 정리될 선행 workspace 경로에 의존하지 않는다.

- `C:\math\docs\do-math\flow-repair-20261021\role-flow-design.md`: 역할 모집단·유지/수정 근거는 2~4절, 개정/독립 승인 5절, 질문·증거·해소 6절, 실제 생산자/소비자와 최소 확인 8~9절. 7절 의도 검사 구현은 후속 task의 범위다.
- `C:\math\docs\do-math\flow-repair-20261021\batch-payload-reads.md`: 마지막 절의 제품 이음새에 옮길 문구만 이 배정에서 보완한다.
- `C:\math\.async\dm-flow-repair-20261021\tasks\role-flow-design\report.json` 및 `evidence/current-observations.json`: 과거 제한 호출의 근거/한계. 실행 스크립트도 같은 evidence 안에 있다.
- `C:\math\.async\dm-flow-repair-20261021\tasks\shared-validation-hashes\report.json` 및 `tasks\windows-patch-guidance\report.json`: 실제 수용한 검사/공통 안내의 정의를 소비한다.
- 원 요구의 최신 의미는 `C:\math\.async\dm-flow-repair-20261021\user-messages.md`다. 원 사건이 필요하면 context에 연결된 audit와 work/runs의 정확 파일만 읽는다.

## 한 변경에서 구현할 의미

1. **역할 책임을 실제 지급 경로에서 맞춘다.** 설계의 전체 역할/단계 모집단을 사용해 유지한 전문 판단의 이유를 보존하고 바뀐 책임을 관련 계약·SKILL·공통 실행·학술자료 활용·_context 안내에 반영한다. 검토자는 문제를 전달하기 전에 지적의 타당성/자기 오독/지급 자료·반대 근거를 확인하고 작업 영향을 설명한다. 수행자가 착수 후 확인할 도구 성공·연구 결과를 사전 승인 증명으로 요구하지 않는다. 확인된 실제 허가/지원 결함의 구체적 지적은 허용한다. 공통 실행의 수용된 Windows/패치 안내를 보존하고 prompt_documents가 실제 지급함을 확인한다. 운영 점검은 지정 완료 판정의 집계와 새 수학 판정 발명을 구분한다.
2. **정상 개정과 예외 종결을 끝까지 연결한다.** revisions.py의 단일 처분/schema/의미 검사 정의를 생산자·수신자·적용이 소비한다. 실제 revised, 선택적 unchanged, AI 요청의 근거 있는 dismissed, deferred, delegated를 그 의미대로 처리한다. dismissed의 요청 출처/사유/근거와 사용자 revise 권위의 기계 포착을 보존한다. 대응 source만 해소하고 부모/자기 revision_dependency·위임·실패 action·writer 대기를 함께 정산한다. 다른 의무·live 실행은 유지한다. 실제 수정 없이 요청을 끝낼 수 있어야 하며 이를 과제 완료나 사용자 요구 면제로 바꾸지 않는다. 사용자 권위로 지정한 개정은 AI dismissal이 지우지 못한다.
3. **검토 결과를 다르게 소비한다.** approved는 현재 독립 승인, revision_required는 실제 개정, unresolved는 판단에 꼭 필요한 입력/효력 대기다. 현재 판본의 미해소 요청과 최신 유효 검토의 정본을 planning에 두고 task_ready/lifecycle/학술 보충이 함께 사용한다. 과거 비승인 때문에 해소한 요청을 부활시키거나 과거 승인으로 후속 반려를 무시하지 않는다. 무수정 종결 뒤 독립 승인이 필요하면 같은 계약에 새 독립 검토를 연결한다. 동일 기초의 자동 반복은 한정하고 실제 판단 충돌은 원 의무/근거와 다음 처리자를 보존한다. 질문 해소/자료 변화가 생기면 수락된 영수증으로 영향받은 검토를 한 번 재개한다. 일반 요청에 새 필수 재심사 절차를 넣지 않는다.
4. **QU를 실제 처리 의무로 잇는다.** questions.py가 정체성/중복/처분/대상 차단의 정본, question_engine.py가 등록·배정·실행·후속의 정본이다. 설계와 seams 9절의 descriptor/key·명시 existing_question_id·origin 원 보고를 사용해 같은 의무의 보고를 재사용한다. 단지 문장이나 실행 ID가 다르다는 이유로 새 의무를 만들지 않는다. 같은 key의 서로 다른 실제 실패나 새 관찰을 조용히 버리지 않는다. 이전 근거로 해결된 동일 관찰을 다시 보고한 것과 실제 재발/새 대상은 구분한다. 임의 자연어의 모든 의미 중복을 완전히 판별한다고 주장하지 않는다.
5. **담당 action/execution을 같은 저장 결과에 연결한다.** 등록 candidate의 CAS 안에서 QU와 pending action을 함께 보존하고 restart/upkeep에서 조정한다. 기본 maintenance:question은 과제/프로필/자료 등 실제 subject를 받고, 실제 EX의 운영 처분이 필요할 때 operational_review:question으로 배정한다. 고정된 QU+generation/배정 대상과 실제 action/activity/execution/receipt가 연결돼야 한다. queue/live handler는 같은 의무에 중복 생성하지 않는다. 새 보고가 live의 고정 입력을 바꾸거나 물리 종료 전에 후속 실행을 열지 않는다. 현재성은 실제 대상/내용/권한을 결박하며 단순 보고 bookkeeping 변화와 구별한다. action 병합/폐기/실패 정산도 같은 범위를 사용한다. 다른 목적의 주기 운영 점검과 같은 target이라는 이유로 합치지 않는다.
6. **처분·증거를 적용하고 다음 업무로 잇는다.** 배정받은 질문 전건에 resolved/superseded/waiting/transferred를 대응한다. 문제 없음도 실제 확인 범위·근거가 있어야 한다. 자료 부족은 실제 자료 변화/다른 질문/근거 있는 시각/수리 처분 영수증 대기로, 사용자 결정이나 연구 조사는 실제 child QU와 그 소비자로, 설치 결함은 기존 operational repair와 실제 복구로 잇는다. 역할 이름만 적은 인계를 처리 완료로 쓰지 않는다. 늦은 응답은 읽은 generation/대상 범위에만 적용하고 나중 추가된 대상을 닫지 않는다. 질문 해소는 해당 계약 검토, QU로 deferred된 개정 준비, 연구의 다음 계획, 부모 운영 질문 재판단에 실제 영수증으로 연결한다. 질문 close 자체는 계약 승인·개정 이행·연구 완료가 아니다.
7. **실제 증거 reader를 확인해 수리한다.** 설계의 workspace 근거 문제는 아직 정적 발견이다. 수용된 시작판에서 이번 수집 output_files와 기존 snapshot을 읽는 실제 후보 reader를 확인한다. 필요하면 설계의 resolve_output_evidence 공통 정의를 구현해 질문/dismissal/재개 근거가 봉인 artifact bytes와 해시/길이를 확인하도록 한다. 다른 실행의 임의 workspace나 현재 head에 아직 없는 파일을 근거로 허용하지 않는다. 기존 정의로 해결됐으면 새 중복 장치를 추가하지 말고 근거를 보고한다.
8. **권위와 저장 경계를 보존한다.** 사용자 pause/HOLD·권한·provider/capacity·설치 복구 fence·비공개 검토 범위·실제 종료/예약 반환을 유지한다. 정지 중 등록/보고를 보존할 수 있지만 자동 triage나 연구 호출은 새로 시작하지 않는다. 질문 해소로 user pause를 지우지 않는다. operations.blocks는 실제 영향 대상에 적용하고 필요한 진단/계획/예외 종결 준비를 막지 않는다. 모든 새 필드/대기/참조는 실제 생산·저장 schema·첫 reader 복원·왕복·보관/보고에서 일치시킨다. 프리알파 현행 계약을 고치며 구판 보완·별칭·변환을 만들지 않는다.

공유 의미는 seams 8~9절과 설계 4~6절이 제공한다. 설계는 구현 수단이며 같은 결과를 기존 구조로 더 단순하게 달성할 수 있으면 생산자·소비자·schema·검사를 함께 맞추고 이유와 정확 인터페이스를 보고한다. 설계 마지막 문단의 ‘지역 변수만 재량’은 이 배정의 제약이 아니다. 별도 운영 티켓 원장·범용 대기 언어·상시 재심사 절차의 구현 자체가 목표가 아니다. 관련 코드를 고치고 필요한 확인까지 이 task에서 마친다.

## 범위와 다음 소비자

queue.writes는 관련 제품 모듈, 역할·참조 문서, 시험, 제품 이음새와 공식 미러, 이 task 결과 문서를 허용한다. tests/는 새 파일과 현행 fixture/지원 생산자 수정이 필요할 수 있어 디렉터리로 열었다. 이 권한은 제품의 역할/개정/질문 경계에 한정한다. 병렬 codex-refresh-diagnostics의 worker/CLI 모듈·CLI 실행 계약·진단 시험을 수정하지 않는다. 추가 제품 모듈이 반드시 필요하면 범위 밖 공용/타 작업 파일을 수정하지 말고 정확한 심볼·이유와 미완료 영향을 report에 남긴다.

의도 check의 비승인 분기/check_history/import_seal 수리는 후속 intent-check-evidence가 맡는다. 이 task는 의도 check를 독자 설계하지 않으며 QU/대기/증거 인터페이스를 후속 소비자가 사용할 수 있게 완결한다. governance 쪽 변경 권한은 사용자 revise 출처 포착과 질문 답변/해소 연결에 필요한 경계다. A만 수용돼도 계약 개정·운영 질문 흐름은 사용 가능해야 한다.

정본에 구현하고 공식 writing-skills 미러 생성기를 사용해 대응 `.agents/skills/do-math` 파일만 맞춘다. `scripts/이음새-정본.md`에는 실제 공개 정의와 제공/소비/오류 의미를 갱신하고 저장 batch 문서의 마지막 절도 함께 옮긴다. 외부 docs에 있던 보고가 제품 이음새 정의의 유일한 근거로 남지 않게 한다. 결과 설명은 자기 workspace의 `docs/do-math/flow-repair-20261021/role-question-flow.md`에 실제 인터페이스·왜 유지/변경했는지·직접 확인·한계·후속 의도 검사 소비 경계를 남긴다. 보고/근거는 task 디렉터리 evidence에도 보존한다.

## 필요한 최소 확인과 완료 판단

정적 판단으로 충분한 역할 유지/범위는 원문·실제 지급 문서 대조로 끝낸다. 상태 전이는 기존 run_tests 선택 실행과 작은 실제 엔진/저장 경계로 확인한다. 설계 9절은 확인할 불확실성의 안내이며 같은 성질을 여러 층에서 반복할 시험 할당량이 아니다.

- 실제 ready/선택까지 정상 승인, 실제 결함→revised→새 검토, 입력 부족→QU/담당 근거→같은 판본 검토를 확인한다. 무수정 AI dismissed→대응 의무/대기 정산→독립 승인/다음 계획 및 사용자 revise dismissed 반려, 과거 부정+후속 승인의 readiness를 확인한다. 동일 기초의 반복 dismissal이 무한 자동 검토를 만들지 않아야 한다.
- 질문 응답의 제출/수신→QU→실제 queue/실행 등록→수집 근거 처분→저장→영향받은 검토/계획까지 연결한다. owner 필드나 enqueue 호출 횟수만으로 대체하지 않는다. 문제 없음·실제 자료 대기/변화·사용자 child 답변·설치 repair의 실제 영수증 연결은 바뀐 가장 작은 경계에서 확인한다.
- 서로 다른 보고/명시 QU 재전달, 새 Repository 첫 load/restart 조정, handler live 동안 추가 보고/대상, 같은 receipt 재전달을 확인해 의무 손실·중복 실행·읽지 않은 대상 해소를 막는다. pause/HOLD·권한·비공개 범위와 실제 종료 관문의 기존 의미를 필요한 변경 경계에서 확인한다.
- actual producer 값을 schema/첫 reader/왕복에 넣고 누락 근거·잘못된 참조/generation·사용자 의무 면제는 출력 오류, 실제 대상 전제 변화는 수용한 CurrentnessChanged 경로로 소비되는지 확인한다. 실제 이번 수집 파일의 근거 해소가 같은 적용 경로로 동작해야 한다.

편집 중 영향 시험만, 인계 전 바뀐 영역의 필요한 선택 검사와 구조 probe만 수행한다. 전체 T2+flows/경계의 통합 실행은 마지막 구현 수용 뒤 별도 배정한다. 같은 성공을 다시 돌리거나 실제 연구/유료 모델/학술 도구를 호출하지 않는다. 기존 원 연구 repo/work/HOLD·예약·감사 자료·graphify는 수정/재개/갱신하지 않는다.

report.json은 변경 파일, 실제 확인/결과/한계, 남은 결함, 다음 소비자의 정확 정의를 담는다. 최종적으로 `python ENGINE/check.py report RECORDS role-question-flow`로 제출 형식/실제 변경 범위를 확인한다. 결과가 미완료면 완료라고 포장하지 말고 사용 가능한 부분과 남은 실제 차단을 분명히 남긴다.

## manager 0004가 함께 배정한 작은 소비 시험 보완

이 추가는 task.json이 아직 없는 미착수 배정에만 반영했다. `shared-validation-hashes`는 제품 수리 21개 파일을 통합·부분 수용했으며 writes 밖 기존 영향 검토 시험의 입력·신호 갱신이 남았다. 이 task의 기존 tests/ 권한과 연관된 편입 소비 경계 안에서 다음 보완을 함께 마친다. 별도 기능·새 선행관계나 공통 검사의 재설계를 추가하지 않는다.

정확 근거는 공용 `C:\math\docs\do-math\flow-repair-20261021\shared-validation-hashes.md` 마지막 절, 선행 report의 findings, 영구 `C:\math\.async\dm-flow-repair-20261021\tasks\shared-validation-hashes\evidence\outside-scope-consumers\report.json`이다.

- `scripts/tests/unit/test_knowledge_impact_review.py:ImpactBundleTests.test_previous_hashes_cover_the_exact_current_mutation_targets`의 실제 변경 사례는 올바른 고정 선언 뒤 live 기록을 바꾸고 `CurrentnessChanged.changes`의 대상·field·before·after를 단언한다. 처음부터 틀린 선언은 출력 오류로 유지한다.
- 같은 파일 `ImpactReviewTests.test_review_required_is_a_waiting_disposition_not_a_producer_retry`와 `test_sealed_review_allows_real_domain_git_retry_and_rejects_wrong_evidence`의 적용 입력에 mutation 원판 대상과 `content_sha256`이 있는 고정 catalog를 공급한다. 적용 뒤 재전달도 같은 고정 문맥을 쓰고 live 상태에서 해시를 재계산하지 않는다. 필요하면 기존 `tests/support/knowledge_impact.py:ImpactCase`를 함께 고친다.
- 제품 검사를 약화하거나 시험을 삭제해 통과시키지 않는다. 이 보완 뒤 `unit.test_knowledge_impact_review` 모듈 한 번으로 영향 검토 대기·독립 봉인 근거·실제 Git 게시·재전달의 현행 계약을 확인하고 공식 미러를 맞춘다. 다른 역할/질문 수정 때문에 같은 모듈을 이미 실행했다면 그 결과를 사용한다. 첫 두 시험은 선행에서 실패를 관측했고 세 번째는 정적 결손만 확인했으므로 미실행 결과를 이미 실패했다고 기록하지 않는다.
