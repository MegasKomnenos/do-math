# 0074: 호출 결과의 부분 수용과 core·게시 잔여 배정

inbox의 완료 사건은 g5-calls(exit0) 하나다. report의 partial을 유지하고 정본 제품2·시험/helper10·설명1과 공식미러13쌍, 총26파일을 검토했다. check.py report PASS 뒤 workspaces.py integrate로 충돌 없이 통합했다. 제품 코드는 manager가 직접 수정하지 않았다. 다음 큐에서 이 유효한 부분 결과를 accepted에 넣으며 전체 G5 완료를 뜻하지 않는다.

## 코드와 사용자 동작의 판단

core_engine._review_recovery_control의 target 재검사는 review_engine._review_cycle이 같은 cycle/knowledge_id를 검증한 뒤의 중복이다. _validate_initial_retry의 assigned execution 재순회도 현재 활동 전이와 중복된다. activities.wait_for는 모든 배정 실행의 종료를 요구하고, assign_execution은 waiting 활동을 거절하며 ready 활동을 working으로 바꾼다. 대기를 해소하는 resume_activity가 별도로 있다는 점을 구별한다. 추가 주석의 `assigning a new execution resumes that activity`는 이 순서를 압축한 표현이라 후속 core 작업에서 정확히 고치도록 묶었다. 이 설명 보완은 동작 결함 판정이 아니다.

_apply_extensions의 유일한 제품 호출은 _apply_bundle_candidate다. submission.extension_schema의 역할별 task_dispositions 소유권과 _payload_issues의 assigned task/academic effect/지정 grant 검사, _validate_bundle_current→decision_engine._validate_decision_acceptance의 과제 계약 현재성이 앞서 적용된다. planning.CONTRACT_FIELDS에는 required_external_effects가 들어 있다. 이 검사를 유지한 채 내부 반복 방어를 없앴다. 새 시험은 실제 schema 적합 입력에서 효과/지정 grant의 정확 반려와 입력 불변을 단언한다. 반환값만 만든 내부 대역으로 수신 검사를 대신하지 않는다.

call_engine의 prepare_role_input·로컬 context.json 읽기는 Repository/Git를 호출하지 않는다. 해당 구간의 GitStateStoreError 전용 재전파만 제거했고 _context의 저장소 오류 전파는 유지했다. 실제 Git 포트 실패 시험, review admission 거절의 저장, 변경된 impact 대기와 손상 봉인에서 준비 시도만 start_failed/input_preparation으로 끝내는 시험, 공개 pause 뒤 실패 결과와 live 검토의 정산/부모 정지 단언을 확인했다. 원 결과 bytes·원 생산자 wait·예약·저장 결과를 검사한다. 신규 사용자 동작 결함을 수리했다는 주장은 하지 않는다.

나머지 시험은 제어의 정확 반려와 다음 요청 진행, 자기 점검 근거, queue 사실 병합, 취소된 grant/외부 HEAD 변경의 cleanup 반려, kind의 현재 hash/독립 판단, native 보존 출력/영수증 재사용, 운영 처분의 종료 장벽을 보완한다. scheduling_initial.native_failure_sim은 공개 초기화와 실제 call 경로에 기존 외부 Git CAS 실패 대역을 사용한다. 현행 codec·저장 검증·기존 업무 보장을 재사용한다.

## 직접 확인한 범위와 한계

verify.py는 원 part1~8 report·coverage·invocation, 보존 Python source SHA, 실제 선택/고유 행/결과, 원좌표/시작판/제출판을 대조했다. 정본/미러13쌍과 외부 원 report/coverage 사본도 확인했다. 상세는 verification-review.json이다. manager 제품시험은 0회다.

part1~8의 실제 결과는 각각 5(error3/failed2), 7(passed3/error4), 20(passed18/error1/failed1), 6(passed3/error2/failed1), 4(passed2/failed2), 6(passed4/error1/failed1), 1(passed1), 6(passed6)이다. 모두 fixture 오류/실행중변경0·complete=true이며 part7/8만 successful=true다. 부분 branch_gate/closing_eligible=false, 관측 exit1이다. 실패와 비용 초과의 원기록은 보존한다. 시험 구성·기대값 오류를 제품 결함 수리로 세지 않았다.

제출 변경21시험은 각각 통과 행의 보존 본문 AST와 일치한다(시간 docstring 제외). 제품2개의 SHA가 같은 part3~8만 원좌표 처분에 연결했다. part8의 제출판 대비4파일 차이는 전체 모듈 AST로도 docstring뿐이고 native helper는 동일하다. 앞부분 측정에는 뒤 추가/교정된 시험과 helper가 있으므로 서로 다른 부분 실행을 단일 최종판 전체 성공으로 합산하지 않는다. 기존 scheduling_close_parallel.py의 unpinned_rejection은 base/제출 SHA가 같은 범위 밖 실패이며 g5-state가 이미 맡고 있다.

배정 원137arc/173행은 raw 도달38arc/42행, 제거8arc/7행, 남김91arc/124행이다. call의5arc는 raw 도달했고5행은4도달/1제거다. core의33arc/38행 도달·8arc/6행 제거·91arc/124행 남김을 실제 diff와 원 coverage로 대조했다. 이는 과거 좌표의 처분으로, 새 분기까지 포함한 제출판 전체 gap 수가 아니다. 새 skip/제외·층/분모/임계값 변경은 없다. 최종 수용판 전체G4/freshG5는 남는다.

## 후속 범위와 진행 중 작업 보존

새 g5-core-rest는 core91arc/124행과 publish의 작은 남김5arc/2행을 함께 맡는다. 제어 접수/게시 재시도·review/위임·bundle 현재성·수신/관찰·preparation/운영 처분·정비/check의 실제 조건을 현재 caller/계약으로 판정한다. 관련 external_engine/integration/retention/submission의 작은 질문은 같은 수신·게시 작업에 묶어 별도 문서·작은 감사 task를 만들지 않는다. 제품5개와 직접 시험/helper·관련 설명·미러가 허용 범위이며 core_engine/call_engine 전체를 처음부터 다시 검사하라는 배정이 아니다. 정확 좌표/SHA/허용경로는 task gap-scope.json, objective.md와 assignment-scope.json이다.

게시의5arc/2행은 외부 retry의 predecessor 부재, persist의 request/execution 신원 불일치, bundle_impact_request의 exclusion 안정화 실패, retention_inputs의 nameless source alias, submission external의 grant 부재다. 이 조건이 합법적으로 도달하는지부터 판단한다. 특히 외부 grant 부재는 '학술영수증' 전체가 아니라 external_requests 입력 검사의 조건이다. 반복 안정화 실패와 nameless source를 가상 손상 상태로 실행시켜 관문 숫자만 채우지 않는다. 불필요 전제·중복 방어의 제거/축소를 먼저 검토하고 필요한 검증은 유지한다.

실제 선행은 g5-calls·g5-publish다. inbox.running의 g5-state·g5-trust 정의와 objective는 유지하고 새 허용경로와 교집합이 없음을 확인한다. 시험슬롯은 state1/trust1/core-rest1, 총3이며 max_workers10·gpt-6.1-sol/high를 유지한다. 기존90개 정의·취소2건 보존, calls를 추가한 accepted86개, 새task 포함91개 정의·active다. 다른 완료 사건은 다음 manager가 처리한다.

worker의 script/frozen13arc/25행과 I/O환경6arc/10행은 미완료다. 다음 가용 시험슬롯에서 지원계약/실경계와 원설계5.5에 근거한 하나의 후속으로 묶는다. 모든 동료 종료 장벽이나 자원만을 위한 depends_on은 만들지 않는다. G6의 최종 모집단/색인, G7 실제 자원/말뭉치, G1~G3 최종 연결·L01·G8 review도 남는다.

## 저장 범위 지시와 게시

sources/storage-scope-direction-2026-10-15.md 및 원설계3.3/A22·5.5를 적용했다. 공통codec/저장검증과 기존 업무 증거를 재사용한다. 남은 구체 좌표/의미와 관련 수리·필요한 확인만 맡기며 전가족·전필드·새reader·옛head quota나 새 검증 framework/장기감사를 만들지 않는다. 최소검증은 객관적인 G1~G8 완료 기준을 삭제하는 이유가 아니다.

공용 context/plan/seams와 새 objective를 먼저 완성하고 별도 queue.pending.json을 check.py queue로 검사한 뒤 queue.json으로 원자 교체한다. 게시 후 이번 세션의 공용 변경은 끝낸다.
