# manager 0016: 제출 반려 수용과 크기 경계 후속

이번 inbox의 완료 사건은 r09 하나다. 시작 당시 r14-fix·r06·r23-r24는 실행 중이고 기존 r12-r13-fix는 실제 core 선행 대기다. 모든 기존 배정 정의를 유지한다. 세션 중 도착한 다른 완료 사건은 다음 manager에게 남긴다.

## 수용한 결과

r09의 정본7·미러7을 workspaces.py integrate로 충돌 없이 통합했다. check.py report는 PASS다. 실제 base/workspace14변경·허용 쓰기·공용 시작 바이트, 제출 diff와 실제 diff, 미러7쌍, AST 및 관련 불변17파일을 직접 대조했다. inspect_result.py·source-review.json과 tasks/r09/integration.json이 근거다. runtime의 변경 함수는 integration.inspect_bundles 하나이며 비용 캐시는 base와 같다.

mutation target의 list/dict가 schema 반려 전에 dict key로 해시되어 TypeError를 내던 F1을 해결했다. 문자열 대상만 구조 색인에 넣어 기존 schema.type 반려로 이어지게 한다. 지식 개정 id·과제 처분 task_id·revision resolution record_id의 NOT_TEXTS 및 비빈list/dict가 unit과 실제 role owner 입력에 연결됐다. schema/참조/권한/현재성 검사는 유지된다. 중앙 seal이 예외를 포획하던 사실을 정확한 schema 반려와 혼동하지 않는다.

OwnerIngressAssertions.reject_and_replay는 모든(rule_id,path,message)의 순서 있는 목록을 비교한다. 기존 특정 issue 선택이 놓치던 계획 차집합과 model assessment coverage, 명시 참조와 completion evidence의 추가 진단을 생산자/중앙 수신에서 정확히 고정했다. 원 input hash·artifact bytes/SHA·도메인 불변·receipt/event1개와, output/sidecar 변이 뒤 같은 ID/같은 payload의 기존 receipt 재사용·다른 payload의 정확 ValueError를 확인한다. sidecar를 원바이트로 복원해 다음 입력이 앞 replay의 영향을 받지 않게 했다. 역할별 뒤 정상 적용·저장/restart 단언과 연결되며 제품 API는 늘리지 않았다.

## 검수한 실행과 한계

원보고와 하위result row·선택ID·원보고SHA·판본을 대조했다. owner-exact-1은10passed/1error, mutation-red는1error/1failed, mutation-green은6passed/1failed, related-final은18passed/5failed이며 task 관측exit는 모두1이다. red unit의22개 subtest 오류는 inspect_bundles의 실제 unhashable target이다. 나머지 새 기대/fixture 오류(빈 문자열 경로, 봉인 시 integration_bundles, empty-family 정규화, replay sidecar 잔류, 숨겨졌던 추가 진단)는 현재 계약에 맞춰 교정됐다.

corrected-final은5선택/5고유passed·task 관측exit0이며 Python876 SHA가 제출판과 모두 같다. 모든 원보고 changed_during_run은 비어 있고 fixture_counts도 비어 있다. unit13과 owner mutation의 앞 판본 성공은 직접 불변 runtime/입력·유지된 단언 범위만 재사용한다.18+5를 최종판23전건 통과로 합산하지 않는다.156.812초 owner 흐름 등 소프트기준 초과도 보존한다. manager의 새 제품 시험은0이다. task의 미러build/check1337파일 drift0/exit0 기록과 실제 변경7쌍 바이트 일치를 사용한다.

r09 시작 뒤 공용판의 core 차이는 r08의 submit_control, control_transport 차이는 worker_submit/_reject_delivery_file이다. 직접 AST 대조로 나머지 중앙 제출 수신·receive·영수증 경로 불변을 확인했다. 이번 실제 수리는 submission/integration 고유 의미이며 r08의 제어 세 수리와 충돌하지 않는다. 서로 다른 사본의 결과를 현재 전체 통합판 실행으로 주장하지 않는다.

PR07 B29/B47의 실제 hunk와 현행 소비/단언 연결을 읽었다. B29 원보고5개/B47 2개는 현재 부재이며 수치를 재사용하지 않는다. r05의 extension null/부재/빈/nested/hash slice만 유지한다. 역사 snapshot 인용 허용과 최신 대상 권한/현재성은 별개다. 공개 개정/종결 코드와 기존 단언은 정적으로 확인했고 공개 execution/review 삭제 생산자는 지정 경로에서 미확인이다. 내부dict 삭제를 공개 도달 근거로 만들지 않는다. 전체2-A/PR07/K/P2와 최종G4~G8·L01·Windows1314는 그대로 남긴다.

## 후속 판단

R17은 원자료 tracking-state에서 구현 검토 완료·최종 동일 판본 연결만 남았으므로 새 반례 없이 재배정하지 않는다. 남은10-A의 R21/R22는 같은 세 크기 시험·engine_size_cases/engine_tool_output을 공유하므로 한 task로 묶는다. 역할×대표 상태·37프로필·100×10이력, 녹화5선언/603폐포/약5MB와 대형manifest의 실제 포장·저장·원문 읽기·상한을 함께 판단한다. 충분한 기존 성질은 재사용하고 확인된 가까운 수리만 수행한다. 등록표/합성 포장과 실제 producer/저장 증거, 녹화 재생과 실Lean을 구별한다.

r21-r22의 직접 시험/helper·한정 context_store/input_tool/formal_preview/formal/knowledge_records 쓰기는 현재 배정과 독립이다. 공유 core·스키마·위임·저장/신뢰 비용 runtime·공통fixture는 읽기 전용이며 직접 읽기 심볼의 시작 SHA를 남긴다. 실제 선행 결과가 없어 depends_on=[]이다. 기존 r06·r23-r24의 제품 쓰기와 겹치지 않고 비용 캐시는 모두 evidence 보존 후 base복원이므로 통합 대상이 아니다. 세 worker 한도 안에서 실행기가 준비된 순서로 시작한다.

## 게시

공용 context/plan/seams와 r21-r22 objective를 먼저 완성한다. r09를 accepted에 추가하고 새 배정만 덧붙인 managers/0016/queue.pending.json을 check.py queue로 검사한다. 검사 성공 판본과 문서/목표 해시를 queue-check.json에 기록한 뒤 검사한 파일을 queue.json으로 원자 교체한다. status는 active다. 게시 뒤 이번 세션의 공용 변경을 마친다.
