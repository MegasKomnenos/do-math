# manager 0015: 교차 전이 부분 수용과 후속 배정

이번 inbox는 r12-r13의 정상 종료를 알린다. 시작 당시 r09와 r14-fix는 실행 중이다. 두 작업과 이전에 게시한 r06의 정의를 유지하며, 검토 중 새 완료 사건은 다음 manager가 처리한다.

## 수용한 변경

r12-r13의 정본 시험/helper4·미러4를 workspaces.py integrate로 충돌 없이 반영했다. check.py report는 PASS다. 실제 base/workspace 차이8경로·배정 범위·공용 시작판 일치, 제출 diff와 실제 diff, 미러4쌍 바이트, 기존 함수 AST와 관련 불변17파일을 직접 대조했다. inspect_result.py·source-review.json과 tasks/r12-r13/integration.json이 근거다. 제품 runtime과 비용 캐시는 이 task에서 바뀌지 않았다.

RoleInputSelection.ready는 실제 lifecycle gate가 직접 낸 다섯 권한 반려만 비선택(False)으로 처리한다. 문구와 최종 traceback의 코드 객체를 함께 검사하므로 하위 함수의 같은 문구 오류도 무조건 흡수하지 않는다. 실제 만료 대조는 정상 선택→권한 만료→False와 queued action 불변을 확인한다. 잘못된 profile SHA 입력은 실제 resolver에서 정확 ValueError가 나고 instance/runtime을 바꾸지 않으며 정상 입력 복귀 후 선택된다. 용량·모델 oracle는 제품 gate 반환을 기대값으로 재사용하지 않는다.

cross_states.assert_event는 없어진 cross_diagnostics를 호출하던 진단 분기를 없앴다. drive의 원 AssertionError 객체가 그대로 전파되고, 수신 반려는 실제 ended execution rows를 담은 event-not-accepted 오류로 남는다. 기존 성공의 arm/drive/선택ID/accepted/event/value/oracle 순서는 유지됐다. 두 새 unit은 test-side drive만 대체하고 제품 함수를 바꾸지 않는다. 삭제된 진단 저장 체계를 복원하지 않은 선택은 필요한 실패 전달을 더 직접적으로 만든다.

## 확인한 근거와 한계

공식 final-consumers는 unit13·sim5·Planning LONG1의19선택/19고유passed, task 관측exit0·77.7초다. 원보고와 각 하위 result row를 직접 대조했고 Python876 SHA가 제출판과 모두 같다. 실행 중 소스 변경은 없다. SHORT2×4·LONG6×20와 기존 시험 메서드 AST는 유지됐다. LONG65.922초, 용량 사건2.766초, SHORT2.031초의 소프트기준 초과를 지우지 않는다. 성능 개선이나 다른 LONG 전건 실행을 주장하지 않는다.

실제 stale profile을 원 helper에 넣은 red-profile은1failed/exit1이다. 원 진단 import 경로의 red-diagnostics는2error/exit1이다. 초기 예외 주입 시험의 결과는 보존하고 최종 실제 입력/gate 시험으로 교체한 판본과 구별했다. 이전6passed/2passed를 최종19와 합산하지 않는다. manager의 제품 재실행은0이다. task의 공식 미러 build/check exit0·1337파일 drift0 기록과 실제4쌍 바이트 일치를 사용하며 두 비용 캐시는 base와 같다.

B129 원보고SHA와 정확94cross passed row를 확인했다. 전체 보고는 successful=false이며 현행 전체 runtime 판본과 같다는 뜻이 아니다. 지정 Temp30원보고의 현재 부재도 확인했다. PR16 B39/B55/B61의 직접 교차 slice만 유지하고 B54/B60의 CLI/기동·R25/R26과 전체 PR/K/P2는 남긴다. task 시작 뒤 공용 core 차이는 r08의 submit_control뿐이며 _review_recovery_control/_apply_delegation_judgment는 같은 AST다. 현재 통합판 전체 실행·모든 알파벳 발생·전체G4~G8의 증거로 확대하지 않는다.

## 미결 F3와 후속 판단

공개 review_replacement 원결정은 governance.apply_decision에서 unsupported로 반려되고, 같은 종류의 없는 원결정을 참조한 delegation도 반려된다. tests/flows/test_cross_required_events.py의 해당 seed는 두 실제 반려·decisions 불변·application 부재·restart를 확인한다. 실제 governance/delegations/core 정의를 대조했다. support/governance_delegation.py의 replacement_case는 ORIGINAL을 직접 넣으므로 공개 생산의 근거가 아니다.

현재 사례별 위임 설명, CLI의 delegation_judgment 세 값, core의 실제 두 판단 소비가 존재한다. manager는 이 선언된 사용 경로를 삭제해 공백을 닫지 않고 실제 사용자 원결정/승인 생산에 연결하기로 했다. 구체적 공개 문법과 저장 연결 방식은 아직 구현 선택이다. 새 승인 체계를 전제하지 않으며 기존 공개 요청·원문·결정 경로를 우선 사용한다. 원결정/승인 진위·현재성·동일 봉인 사례와 판단 독립성·기계 grant는 보존한다.

r12-r13-fix는 원결정 생산부터 두 판단의 within_scope/outside_scope/unresolved, 실제 교체 또는 사용자 질문, 저장/restart와 cross 도달까지 관련 구현·시험·설명·미러를 한 task에 묶는다. r12-r13 및 core 파일의 현재 소유자인 r14-fix만 선행이다. 관찰/진행성·무관한 제어 수리는 보존하고 r09/r06 종료는 기다리지 않는다. 따라서 r12-r13의 원 report.partial은 그대로이며 F1/F2만 해결, F3와 최종 통합판 증거는 남는다.

독립 r23-r24는 원래10-B의 export/query/신뢰 파일/readiness/idle 다섯 사례를 같은 세 시험·비용 helper 경계로 묶는다. 계수와 실제 반환/파일/JSON/원 입력 보존을 함께 판단한다. 충분한 근거는 정적으로 유지하며 56230파일 등 원문 축을 줄이거나 관례적으로 다시 실행하지 않는다. 해당 직접 결함의 저장/신뢰/readiness runtime 수리만 허용하고 core/scheduler·진행 중 제출/관찰은 읽기 전용이다. 기존 작업의 의미 있는 쓰기와 겹치지 않아 depends_on=[]이다. 기존 r06은 그대로 파견 가능하다.

## 게시

context/plan/seams와 두 objective를 먼저 작성한다. 기존 task 정의를 보존하고 r12-r13을 accepted에 추가한 queue.pending.json을 check.py queue로 검사한다. 검사 성공 판본과 문서/목표 해시를 queue-check.json에 기록한 뒤 바로 그 pending 파일을 queue.json으로 원자 교체한다. 상태는 active다. 게시 뒤 이번 manager의 공용 변경을 마친다. 외부 입력 없이는 못 하는 최종 범위·L01·Windows1314와 기타 미결은 기존 계획에 남아 있다.
