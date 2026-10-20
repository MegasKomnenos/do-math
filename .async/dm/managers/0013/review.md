# manager 0013: 관찰 저장 계약 수용과 교차 전이 묶음

이번 inbox는 r03-fix의 정상 종료를 알리며 r08·r09는 실행 중이다. 시작한 배정과 준비된 r14-fix의 정의는 유지한다. 이번 검토 중 들어오는 다른 완료 사건은 다음 manager가 처리한다.

## 수용 판단

r03-fix의 실제 변경은 정본7·미러7이고 report 검사 PASS다. base/workspace의 실제 파일 집합 차이, 공용판이 각 변경의 base와 같은 점, 미러7쌍과 관련 불변16파일을 직접 대조했다. workspaces.py integrate는 충돌 없이14파일을 반영했다. 근거는 source-review.json·inspect_result.py 및 tasks/r03-fix/integration.json이다.

스키마에서 현재 생산자가 없는16선택 필드와 의무closed만 제거했다. observation_facts의 event_json/event_sha256/monotonic_offset_ms는 한 형태의 필수 필드이며 _observation_fact_rules의 엄격 JSON/SHA 검사는 무조건 수행한다. 선택 source의 좌표/시각, 의무의 offset·delivery/ack·hold·response_ref, 응답 내부 _RULE_UPDATE는 유지한다. 현재 fact 생산과 core의 실제 저장 분기를 대조했고 과거 자료를 위한 변환이나 구형 producer를 추가하지 않았다.

observation_pairs는 네 가족의 실제 전체 record를 현재 StateContract checker/validator에 보낸다. 세 가족은 개별 record, observations는 metadata map이며 역방향은 각 row의 전체 properties다. tracker_record_samples의 실행 불일치 입력과 owner_observation_samples의 실제 running_work/on_observation/store.load가 next_owner/followup·observation_refs를 생산한다. owner fact의 JSON과 metadata 연결도 단언한다. field 면제·사후 스키마 보충은 없다. 기존 rule ID 텍스트 보존 pair는 별도 역할로 유지한다.

일반 assert_pair의 순방향/역방향과 trust 파일 단언, 기존 worker40입력/args/lock·runner8/두 JSON·trust12·enum·Unicode 규칙 단언의 AST 보존을 대조했다. 정상 실제 생산값과 삭제16필드/closed 반려, fact 필수3필드 누락·JSON/SHA 변조, 별도 StateContract의 새 미생산 optional 키가 동일 일반 walk의 역방향에서 실패하는 반례가 있다. C-03의 공개 boundary→rule response→answered→execution stopping→저장/restart 시험과 생산자 저장 시험은 수정 없이 포함된다.

공식 related-1의13선택·13고유passed와 unit/sim/contracts 하위 result.json row를 직접 대조했다. task 관측exit0·19.5초이며 fixture 오류·실행 중 변경은 없다. 원보고의 Python876 SHA는 제출판과 전건 같다. 소프트 예산 초과6ID를 유지하며 전체 관문이나 통합판 전건 성공으로 확대하지 않는다. 잘못된 TrackerTests 선택은 실행 전exit1 뒤 교정됐고 최초 미러 완료 전 일시 드리프트는 후속 완료 빌드/검사로 교정된 기록이다. 비용 캐시2개는 base로 복원됐다. manager의 제품 시험 재실행은0이다.

r10은 시험/helper만 변경했고 실제 관찰/저장 생산·소비 코드는 이번 task 판본과 공용판이 같다. r14가 바꾼 parallel/scheduler는 처리량/큐 순서이며 record 모양/내용은 바꾸지 않았다. 통합판에서 모든 r10/r14 시험을 새로 실행했다는 주장은 하지 않는다. r14-fix와 향후 r08/r09 통합은 각 실제 변경에 따라 관련 저장 영향만 판단한다.

r03 F2를 해결로 수용한다. R03/1-A의 이 관찰 가족·PR18/C-03 해당 성질은 최종 판본 증거 대기다. 다른1-A·R06 전체·PR/K/P2 전체·G4~G8·L01·Windows1314는 남는다.

## 후속 배정

r12-r13은 원래7-A/2-D의 짧은/긴 사건 열과 같은 cross_machine/cross_contracts 전용 helper·직접 시험을 한 담당자가 판단하고 필요한 수리·미러·최소 확인까지 끝낸다. R12/R13을 별도 실행으로 나누면 같은 helper 수정·검증이 반복된다. 실제 알파벳 도달, 원문a/b/c, 예외 전파와 원래 회귀 순서에 한정하고 PR16의 직접 slice를 함께 판단한다. 기존 충분한 단언/원보고는 재사용하며 전수 장기 조사를 만들지 않는다.

depends_on=[]이며 전용 시험/helper만 쓰므로 r08/r09 및 r14-fix와 비용 캐시 외 중첩이 없다. runtime·공용 Sim/engine_control/provider/scheduling helper는 읽기 전용이다. 발견된 runtime 문제는 정확한 재현/필요 파일을 보고해 소유 task 뒤 수리에 연결한다. 44개 구조 발견 전체는 별도 묶음으로 유지하며 cross_*의 직접 수정 건만 같은 작업에서 처리할 수 있다. R06 전체 null 및 다른 의미 질문도 후속으로 남긴다.

context·plan·seams와 objective를 먼저 갱신한다. r03-fix를 accepted에 추가하고 새 task를 넣은 queue.pending.json을 검사한 뒤 그 파일을 queue.json으로 원자 교체한다. 상태는 active다. 게시 뒤 공용 변경은 끝낸다.
