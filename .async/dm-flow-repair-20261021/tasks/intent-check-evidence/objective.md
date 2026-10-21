# 의도 검사의 미해결 입력을 같은 묶음의 후속 판단에 연결

## 결과와 실제 선행

의도 해석의 독립 검사가 필수 근거 부족으로 unresolved를 반환했을 때, 정확한 해석 묶음을 불필요하게 다시 쓰지 않고 실제 자료/답변을 기다린 뒤 같은 묶음의 새 독립 검사로 이어지게 한다. 확인된 원문 왜곡/소유자 오류인 revision_required는 기존 정상 재저작을 유지한다. 이는 context R1~R2의 전체 역할/파이프라인 검토에서 발견된 별도 기능이며 role-question-flow의 QU 해소·대기·증거·저장 정의를 실제 소비한다.

role-question-flow가 수용된 소스 사본에서 시작한다. 자기 inputs context/plan/seams, task.json, 정본 AGENTS·제품 이음새·시험 지침을 읽고 실제 수용된 A 코드와 report의 공개 인터페이스를 따른다. A의 시작 설계 이름을 독자적으로 다시 발명하거나 A가 단순화해 폐기한 장치를 되살리지 않는다.

docs는 snapshot_paths에 없으므로 다음 공용 절대 경로를 읽기 전용으로 읽는다.

- `C:\math\docs\do-math\flow-repair-20261021\role-flow-design.md` 7절의 정적 발견, 8절 B 경계, 9절 최소 검증 설계.
- `C:\math\docs\do-math\flow-repair-20261021\role-question-flow.md`와 `C:\math\.async\dm-flow-repair-20261021\tasks\role-question-flow\report.json`: 수용한 질문·대기·증거·실제 영수증 인터페이스. 필요한 영구 evidence는 같은 task 디렉터리에서 읽는다.
- `C:\math\.async\dm-flow-repair-20261021\user-messages.md`: 최신 요구와 재량의 범위.

## 한 변경의 동작

1. governance_engine._apply_governance_intent와 initialization_engine의 실제 check 소비를 대조한다. approved는 기존 명시 승인/owner 적용으로, revision_required는 정상 rework로, 필수 근거가 없는 unresolved는 동일 import_id/원문/봉인 hash를 가진 `waiting_actions.kind=import_check_evidence`로 연결한다. unresolved의 이유가 미래 결과의 미입증 같은 역할 오독이라면 문서/입력 경계를 함께 명확히 하며 모든 일반 요청의 상시 의심 절차로 바꾸지 않는다.
2. 대기는 A의 실제 QU/근거 대기 정의로 필요한 question_ids와 실제 content basis를 결박한다. 질문의 실제 담당 배정/해소를 재구현하지 않는다. `_resume_import_check_waits`는 관련 해소 영수증이나 판단에 필요한 실제 근거 변화가 생긴 때 같은 정확 묶음의 새 독립 check를 한 번 연다. 같은 기초로 unresolved가 반복됐다는 이유만으로 해석/검사를 계속 재생성하지 않는다. 자료가 없으면 질문과 다음 담당·조건을 보존한다. 사용자 목표/허가 결정은 기존 권한 경계를 따른다.
3. governance.check_import의 기존 ‘check is sealed; reauthor instead’를 해당 대기 해소와 새 독립 실행이 기계적으로 확인된 경우에만 후속 검사로 허용한다. `bundle.check_history[]`에 이전 봉인 check를 보존하고 current check를 갱신한다. import_seal은 검사 이력도 제외해 원 해석 묶음의 불변 hash를 유지한다. 각 check의 exact hash·실제 별도 execution·같은 묶음/원문·독립성·현재성 결박은 유지한다. 임의로 봉인된 판정을 덮어쓰는 공개 API를 추가하지 않는다.
4. 최초 초기화와 일반 입력 양쪽에서 같은 공통 규칙을 소비한다. 실제 원문/묶음 변경은 기존 rework로 새 묶음을 만들고 옛 대기를 이유와 함께 은퇴시킨다. 명시 사용자 승인·원문 전건 피복·소비자 owner 적용·위임의 두 독립 판단은 검사 승인과 별개로 유지한다. 질문 해소로 사용자 pause/HOLD를 해제하거나 연구 실행을 강제하지 않는다.
5. 변경된 저장/대기/schema/참조/보고·해시 투영이 실제 producer와 첫 reader에서 일치하도록 관련 모듈/fixture/역할 문서·references/입력-소비자·이음새 정본을 함께 고친다. 현행 계약 하나를 고치며 구판 기본값·별칭·자동 변환을 추가하지 않는다. A의 이미 작동하는 역할·개정·운영 질문 결과를 보존한다.

seams 10절과 설계 7절의 구조는 구현 선택이다. 기존 구조의 재사용으로 같은 동작을 더 간단히 만들 수 있으면 실제 공유 정의·producer/consumer·검사를 같이 맞추고 이유를 보고한다. 범용 재심사/대기 프레임워크를 별도로 만드는 것이 목표가 아니다.

## 범위와 필요한 확인

queue.writes의 제품 모듈은 위 의도 검사 소비·대기·저장/현재성·공통 검사 입력 경계에만 사용한다. A의 질문/개정 기능이나 병렬 CLI/모델 timeout 진단을 다시 설계하지 않는다. 추가 제품 파일이 필수면 정확한 심볼과 이유·미완료 영향을 report에 남긴다. tests/ 디렉터리 권한은 바뀐 의미의 시험/실제 fixture를 함께 고치기 위한 것이며 별개 진단 시험을 수정할 권한으로 해석하지 않는다.

가장 작은 실제 수신/저장 경계에서 동일 해석 묶음의 check unresolved→입력 대기→실제 QU 해소/근거 변화→새 독립 check approved를 확인한다. 그동안 interpret/rework가 불필요하게 늘지 않고 원문/묶음 hash는 유지되며 history와 현행 check의 실행/봉인이 복원돼야 한다. 같은 영수증/같은 근거 재전달이 중복 검사를 만들지 않는지 확인한다. 실제 revision_required는 rework를 계속하며, 원문 변경과 부정한 재검사/묶음 불일치·독립성 결함을 반려하고 명시 승인/owner 적용·정지는 기존 의미대로 남아야 한다. 초기화와 일반 입력에서 실제로 다른 소비 분기가 있을 때 그 차이를 확인하되 동일 공통 성질을 중복 시험하지 않는다.

정적 확인으로 충분한 문서 연결은 거기서 끝낸다. 기존 run_tests 선택 검사와 구조 probe로 바뀐 영역의 남은 불확실성만 확인한다. 전체 T2+flows 통합은 마지막 제품 변경 수용 뒤 별도 배정하며 이 task에서 반복하지 않는다. 원 연구/감사/HOLD·예약·graphify는 수정·재개·갱신하지 않고 실제 모델/학술 도구도 호출하지 않는다.

정본을 고치고 공식 writing-skills 미러 생성기로 대응 Codex 사본만 맞춘다. 자기 workspace의 `docs/do-math/flow-repair-20261021/intent-check-evidence.md`에 실제 인터페이스·결과·유지/변경 이유·직접 검증/한계와 남은 문제를 기록한다. report/evidence는 자기 task 디렉터리에 보존한다. report.json에 실제 변경·검증·한계를 쓰고 `python ENGINE/check.py report RECORDS intent-check-evidence`를 통과시켜 제출한다.

## manager 0005가 묶은 작은 provider 이음새 보완

`codex-refresh-diagnostics`의 13파일은 이미 공용 소스에 통합·수용됐다. 영구 입력 `C:\math\docs\do-math\flow-repair-20261021\codex-refresh-diagnostics.md` 마지막 절과 inputs/seams 12절을 읽고, 실제 `codex_stream.stderr_diagnostics`·`LocalCLIAdapter.stderr_diagnostics`·`execution.collect.diagnostics`의 제공/보존/소비 의미를 기존 `scripts/이음새-정본.md` provider 연결 표와 공식 미러에 함께 연결한다. 쓰기 권한이 이미 있는 제품 문서의 작은 보완이다. 별도 provider 구현·시험을 수정하거나 같은 선택 시험·CLI 호출·원자료 재생을 반복하지 않는다. 실제 함수/소비를 정적으로 대조하면 충분하다. 색인은 원 stderr 바이트 위치와 CLI 보고값이며 성공/실패·재시도·원격 종료·공급자 원인을 판정하지 않는다는 경계를 보존한다. 원 진단의 외부 원인은 미확정이다.


## manager 0006이 수용한 실제 QU 소비 인터페이스

`role-question-flow`의 제품 구현과 선행 영향 시험/저장 문구 잔여를 수용했다. 실제 코드와 inputs/seams 13절 및 공용 role-question-flow.md의 「근거·저장·오류」를 사용한다. 영구 근거 `C:\math\.async\dm-flow-repair-20261021\tasks\role-question-flow\evidence\verification-summary.json`은 선택 실행별 성공/실패·현행 의미로 바꾼 ID·한계를 제공한다. 정리될 workspace를 직접 읽는 경로에 의존하지 않는다.

대기 소비자는 `questions.question_scope_state(runtime, question_id, target_ids)`의 `{resolved,resolution_refs}`를 사용한다. 각 질문의 **자기 고정 target_ids 범위와 이미 읽은 영수증 basis**를 대기에 보존하고 후속 검사 시 같은 범위를 비교한다. 다른 대상이 남아 있어도 자기 범위가 해소됐으면 그 사실을 사용할 수 있고, superseded 원 질문은 실제 replacement의 같은 범위가 해소돼야 한다. 이미 본 영수증만 있는 unresolved 재보고로 check를 반복하지 않는다. 처음부터 해소돼 있던 질문을 새 대기 원인인 것처럼 처리하지 않는다. 실제 묶음/원문 변화는 기존 rework로 보내며 자료 변화와 무관한 보고 bookkeeping을 재검사 원인으로 쓰지 않는다.

`question_wait`는 엔진이 저장된 target_ids를 결박하고 모델 출력의 wait_for는 question_id만 받는다. 계약 입력 대기의 question_scopes/question_resolution_basis가 실제 소비 예이며 그대로 복제해야 하는 새 형식 요구는 아니다. import check의 자기 대기 schema·첫 reader와 실제 producer/consumer를 함께 맞춘다. 봉인 근거는 기존 `submission.resolve_output_evidence`/`_resolve_execution_evidence`와 실제 수락 영수증을 사용한다. QU 배정/해소 기능을 다시 설계하거나 query helper를 별도로 만들지 않는다.

이 task의 선행판은 R1~R3 선택 수신/저장 흐름과 구조 probe를 확인했지만 전체 T2+flows는 아직 실행하지 않았다. 맡은 의도 검사 동작에 필요한 작은 실제 수신/저장 확인만 하고, 최종 통합 확인은 마지막 변경 수용 후 배정한다. 저장 선읽기 문구와 영향 검토 시험은 이미 끝났으므로 재검증 배정으로 확대하지 않는다.
