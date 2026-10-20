# manager 0011: r10 수용과 공개 제어·수송 후속

이번 inbox의 완료 사건은 r10이다. r14·r03-fix의 시작 정의와 입력은 유지한다. manager 실행 중 도착한 다른 완료 사건은 다음 inbox의 판단 대상이다.

## 수용 결과와 근거

r10의 실제 변경8파일은 정본 시험3/helper1·미러4이며 보고와 같다. 변경 전 공용판은 각 base와 같았다. 변경4쌍 byte 일치, 관련 불변 runtime/helper/시험19파일, r05 값 영역 정의3개와 r03이 확장한 observation_inputs의 기존 소비 함수3개 AST를 직접 대조했다. 검사 스크립트의 최초 경로 확인 오류는 observation_inputs에서 batch를 찾은 것이며 실제 import는 provider_live.batch다. 이를 고쳐 실제 소비 세 함수를 확인했다. 제품 시험 실패가 아니다. report 검사 PASS 뒤 workspaces.py integrate로 8파일을 충돌 없이 통합했다. queue.accepted에 r10을 넣는다. source-review.json·inspect_result.py와 tasks/r10/integration.json이 근거다.

F1은 malformed(root string)가 생성하지 않던 public role 비문자열5입력을 공통 NOT_TEXTS로 복원한 수리다. native 입력은29에서34가 됐다. 기존 EXTERNAL_JSON_VALUES/NATIVE_ROWS/nested_native_rows와 r05 저장/해시/JSON 성질은 유지됐다. F2는 raw42조합과 native의 정확 반려·mode별 followup·원 bytes/artifact·offset·receipt·fresh tracker 재전달의 runtime/head 불변 단언이다. F3은 append fixture의 first_row를 실제 runner와 같은 누적 nonblank 행 번호로 바꾼 것이다. 기존 관련4ID를 확인했다. runtime 변경·실환경 호출은 없으며 실행 결함 수리로 확대하지 않는다.

ingress-final은7선택/7고유passed, 이후 helper5입력 수리의 native-role-final은1선택/1passed다. 원보고 SHA·실제 row·선택·source_sha256을 대조했다. 마지막 Python876해시가 제출판과 같고 첫 실행과의 차이는 provider_native_inputs helper 하나다. 나머지6row는 그 generator를 소비하지 않아 재사용하며 7+1을 단일 최종판 전체 통과로 합산하지 않는다. task 관측 exit는 둘 다0, fixture 오류·실행 중 변경 없음이다. r05 원보고의 native_storage4passed와 해당 소스15파일은 그 slice만 재사용하고 r05 전체 successful=false는 유지한다. 캐시는 증거 보존 뒤 base로 복원됐다. manager 제품 재실행은0이다.

현재성의 revise/review 종결 반려는 실제 _obsolete_review_reason/_record_review_observation와 기존 native_targets 단언을 정적으로 대조했다. 그 ID와 pending slot 소실을 새로 실행한 것은 아니다. 공개 execution/review 삭제 생산자는 확인되지 않았고 모든 삭제 부재를 인증하지 않는다. ended 연구 실행의 늦은 사실 보존은 현행 정상 계약이다. R10의 한정 질문과 F1/F2/F3 수리는 수용·최종 통합판 증거 대기로 옮기며 전체2-A/R06/PR15/K/P2, G4~G8·L01·Windows1314 미검사는 유지한다.

## 다음 배정

r08은 원문 R08/2-A의 공개 action·제어 수송 pump/영수증 반려와 실제 한 번 소비·뒤 정상 제어 진행을 담당한다. 현재 PAYLOADS/configure, submit_control/_inbox/_apply_inbox와 ControlTransport.receive/_pump_paths, 기존 ingress·nested control·transport·receipt 시험에서 가까운 수리를 한 task로 묶는다. 형식·적용 전제 소실·동일 ID/두 transport/양순서를 기존 근거로 먼저 판단하고 부족한 입력/단언만 수리한다. PR07 B15/B23/B59의 관련 slice를 함께 연결하며 R09 제출 확장/참조는 별도 남김이다. 이미 충분한 성질을 재감사하거나 같은 부류를 action마다 재배정하지 않는다.

r08은 다른 실행 중 결과를 필요로 하지 않아 depends_on=[]이다. r14와 r03-fix의 의미 있는 쓰기와 겹치지 않으며 비용 캐시만 공통이다. 캐시는 보존 뒤 base 복원을 요구한다. runtime 쓰기는 실제 재현된 해당 제어 결함에 한해 지정4파일이고 일반 정책/관찰/제출/진행성 변경은 대상이 아니다. 원문과 실제 현재 정의를 연결하는 seams와 objective를 먼저 준비하고 공용 맥락/계획을 갱신한다. queue.pending.json을 check.py queue로 검사한 뒤 검사한 파일 자체를 원자 교체해 마지막 게시한다. status는 active다.
