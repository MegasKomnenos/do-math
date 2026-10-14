# P04/P05 검토 입력과 고정 원자료의 실제 결속

시작 skills/diff 2,675파일은 020 manager source-inspected.json과 전건 SHA256이 같다. 시작 Git 상태의 기존 canonical/repository/planning 및 작문 도구 변경은 시작 판본에 이미 포함됐으며 이번 task의 변경으로 귀속하지 않는다. start-comparison.json과 git-status/git-diff 원출력, input-audit.json에 좌표를 보존했다. 과거 packet 행 번호는 current-bindings.json의 현재 제목/행/원문과 대조했다. 13-C 중 문서가 명명한 필드의 존재/소유/실제 전달을 맡으며 L01의 출력 단위/운전 프로필 결정을 인증하지 않는다.

| owner | 실제 생산·최종 소비 및 담당 | 확인한 성질 |
|---|---|---|
| role_review | context_for → _prepare_review_context → _context.role_review → prepare_role_input. sim.test_submission_review_inputs.ReviewInputTests.test_review_stage_documents_reach_the_final_seat_input | scope/initial/organize/judge/answer의 실제 반환과 최종 자리 입력, proposal 및 조건에 따른 identity_basis/policy_ref. 최상위 proposal의 중복 지급 여부를 검사한다. 전체 입력 내부 전문 사본의 수는 proposal_probe.py가 별도로 관찰한다. |
| pending_findings | _add_findings가 저장한 발견 → context_for의 현재 열린 키 → 최종 role_review.pending_findings. 같은 sim method와 ReviewCycleTests.test_organizer_omission_forgery_and_owner_checks | 비어 있지 않은 원소, 정확 stage/slot/id/ref와 동일 local ID를 쓰는 다른 자리의 발견 구별. 빈 pending 배열은 양성 ref 증거로 쓰지 않는다. 기존 organizer의 전건 대응/원 담당 반려 단언을 유지한다. |
| review_research | 실제 고정 request → _review_research_context → _context → 최종 prepare_role_input 반환. ResearchOwnerContractTests.test_fixed_question_context_keeps_original_bytes_after_unrelated_publication 및 기존 ResearchFlowTests.test_all_fixed_questions_return_before_resuming_the_deferred_slot | id/request_digest/question/proposal_digest/requesting_slot와 source_records의 정확 대응. 일반 게시 이후 고정 원자료와 질문이 불변이다. 기존 두 질문의 flow를 관찰해 최종 입력까지 확인한다. |
| review_sources | _materialize_research_sources의 실제 반환, review_research.sources와 보충-조사의 line-local sources 별칭. 위 unit/flow method와 test_prepared_source_uses_its_snapshot_after_head_advances, FixedSourceRestorationTests | inline canonical 원문과 artifact의 정확 Git snapshot/원바이트, ref/SHA/bytes/local_path의 전건 대응. 경로는 index와 봉인 SHA/확장자의 input/review-research 경로다. 일반 research_sources의 id/path/name과 다른 경계다. |

assert_review_documents는 실제 반환과 소유한 cycle/request/source_records를 대조한다. review_input_value는 포장 결과가 source_ref/total 형태이면 manifest.catalog의 해당 key와 동일한 참조인지 확인하고 정확 파일의 SHA/bytes/canonical 내용과 total을 읽는다. inline 결과는 그대로 검사한다. 이 참조 처리 코드의 존재를 해당 실행에서 참조 variant가 발생했다는 증거로 쓰지 않는다. 준비 반환 관찰은 기존 ObservedCalls/Returns의 sys.monitoring 사건을 쓰며 제품 함수·반환값을 교체하지 않는다. 실제 flow의 두 조사 준비가 담당 검사에 도달했는지도 개수로 확인한다.

ReviewScene은 실제 ResearchEngine/ResearchRepository를 Git 포트 대역 위에서 실행하는 2층 fixture다. 전체 역할 포장을 위한 채택 거버넌스·id·title이 모두 있는 장면이 아니므로 이를 제품 기본값으로 보충하지 않았다. 초기 focus/corrected/corrected2/corrected3의 title/id/goal_status와 adopted governance 오류는 자신의 연결 시도 실패로 보존했다. 불완전 장면에 넣었던 보충은 제거하고, 최종 자리 입력은 공개 활성화를 거친 기존 opened_sim 경로로 이동했다. 직접 고정 반환과 원자료 검사는 원래 ReviewOwnerCase에 남겼다. corrected4에서 교정한 세 정확 ID가 통과했다. Git/모델/Lean 대역은 외부 포트에 있으며 생산/포장/물질화 함수를 대역으로 가리지 않는다.

수리 전 red의 한 test method는 네 owner subTest 모두 ValueError not raised로 실패했다. 같은 성질의 최종 검사는 실제 입력 없이는 반려하며 정확 owner의 defer만 허용한다. 일반 문서 순회 담당 확인은 해당 method 안의 실제 assert_review_documents 호출을 검사한다. 오기/owner 누락/method 누락/문서 검사 없는 method 및 다른 owner 동시 건너뜀 반례를 유지한다. 이 AST는 담당 확인용이며 반환값 추론이 아니다. 현재 사용이 없어진 네 owner의 AST 반환 추정/소비 키 수집과 identity_basis/policy_ref 수동 조립만 제거했다. 다른 owner가 쓰는 범용 helper를 일괄 제거하거나 새 전역 담당 등록부를 만들지 않았다.

반환 후 사본에서는 proposal/identity_basis/policy_ref, populated finding의 ref와 stage/slot/id, 고정 질문의 question/id/request_digest/proposal_digest/sources, 고정 원자료의 ref/local_path/SHA/bytes를 삭제하거나 바꾸어 반려한다. 다른 ref의 차용, 일반 연구 원자료의 키 차용, 동일 바이트를 복사한 다른 경로, artifact_ref/snapshot 교차 소유를 구별한다. 실제 물질화 파일의 내용 손상과 부재도 읽기 단계에서 반려한다. 이 사본 반례와 제품 자체의 입력 손상 반려는 별개다. 실제 Git 경계는 정상 저장/복원, 없는 artifact의 GitStateStoreError 원인/좌표, 이미 물질화된 원문 손상의 ReviewRestorationError와 slot/ref/snapshot/path/기대·관측 SHA를 확인한다.

기존 initial/answer/judge의 봉인 전 동료 판단 비노출, organizer의 전건 참조와 원 답변 담당, 고정 질문의 잘못된 request/proposal 및 byte 반려, private supplemental 결과의 자기 자리/봉인 이후 공개, replay의 원자료/봉인/예산 반례는 유지한다. Pure cycle의 identity_basis/policy_ref 부재 조건은 엔진의 실제 존재 조건과 구별했다. P01~P03·B130~B134의 실제 반환 검사와 다른 owner의 음성 단언은 지정 회귀에 포함된다.

B110~B114의 실제 도입 diff·현재 소비·존재하는 원보고 7개의 SHA를 대조했다(history-verification.json과 B*-p04-p05.diff). 이 slice의 반환 추정은 B113의 role_review/review_research와 B114의 pending_findings/review_sources에 도입됐으며 실제 검토/물질화 검사로 교체한다. B110의 다른 owner, B111의 callable 명시와 소유 공간 구별, B112의 line-local 별칭 및 다른 producer, B113/B114의 다른 packet은 유지한다. 역사 counts를 현재 성공에 합산하거나 PR24 전체를 종결하지 않는다.

제품 문서를 변경하지 않았으므로 이번 변경으로 향후 문서 prompt 판본이 바뀌지 않는다. 기존 고정 실호출/host/Lean/예약/학술 자료는 보존 검사에서 동일한 입력/도구/바이트가 확인된 승인 성질에 한해 재사용한다. 새 유료 호출·예약/학술 실행·기존 연구 운전은 없다. L01 Q1/Q2, P06~P11/TRUST/N의 다른 절 및 최종 전체 일반/fresh T3/전수 변이/전체 완료 review는 후속 책임이다.

최종 선택/고유 row/실제 exit와 판본은 verification.json 및 c/m report/process/before/after가 정본이다. 조건부 Windows1314 symlink skip은 통과나 실제 탈출 반려의 증거로 세지 않는다. 보존 범위는 preservation.json이며 공식 미러 생성은 사전 계획의 허용 경로만 생성한다.

## A2 미충족: 현재 제안 전문의 재지급

proposal_probe.py는 기존 단계 시험을 공식 run_tests.main으로 실행하면서 실제 prepare_role_input의 반환 사건만 관찰했다. 공식 시험 row는 passed/exit0이지만 이 추가 의미 단언은 exit1이다. 관찰한 15개 반환 중 answer/initial-0의 마지막 반환은 현재 제안 객체와 완전히 같은 map을 두 위치에 포함한다: context.role_review.proposal, context.role_review.self_messages[0].content. 기대값은 문서와 objective의 한 번 제공(1)이고 실제값은 2다. proposal-observation.json과 proposal-return-14.json은 좌표와 실제 context/manifest를 보존한다. 이 행은 수제 반환·AST 추정이 아니다.

_record_review_input은 kind=proposal 메시지에 현재 전문을 저장한다. context_for는 도구 결과·옛 제안·delivered_prompt를 source_ref로 돌려주지만 같은 현재 판본의 proposal 메시지는 전문으로 self_messages에 남긴다. 실제 _context와 최종 포장이 이를 유지한다. 이번 stage 시험의 기존 최상위 proposal 부재 단언만으로는 이 중첩 중복을 잡지 못했다. 이를 만족한 것으로 쓰거나 count=2를 정상 기대값으로 바꾸지 않는다.

review_cycle.context_for 및 review_engine._record_review_input은 배정의 고정 runtime이며 변경하지 않았다. manager가 현재 전문의 단일 지급과 원 메시지 봉인/이전 판본 복원·가시성을 함께 보존하는 좁은 runtime work를 배정해야 한다. 공유 expected seat view와 최종 포장의 일치도 다시 검증해야 한다. probe의 단언을 제품 회귀에 연결한 뒤 정확 단계/관련 양쪽 선택을 재검증한다. 따라서 P04/P05 필드 결속 수리는 유지하지만 A2와 task 전체는 완료로 제출하지 않는다. 일반 검사 green과 요구 충족을 구별한다.

최종 검산은 양쪽 같은270선택·고유row/각269passed·권한1skip/exit0과 각875Python SHA를 확인했다. 정본600.2초/미러530.7초이며 속도 비교 실험으로 해석하지 않는다. 계획14개 미러 경로가 모두 writes 안이고 생성14갱신·마지막캐시1동기화·--check1336파일·skill-only를 통과했다. 실제28변경은 정본13시험/helper·미러13·비용캐시2다. 보존 검사139입력/144corpus/150SHA/8host/5tools/910baseline/258runtime-T4와 최종 비캐시 해시가 같으며 정확변경경로의 git diff --check도 exit0이다. final-inspection.json은 실제 반환에 담긴 두 전문 map과 정규 JSON 바이트가 동일함을 독립적으로 대조한다. A1/A3/A4 pass·A2 fail의 partial로 제출한다.
