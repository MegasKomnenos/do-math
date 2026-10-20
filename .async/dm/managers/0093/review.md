# Manager 0093: 기반 1b·1c review 수용

inbox.completed의 pr-base-ports-r(exited/0)를 기반 1b 포트 도입·기본값 제거와 1c 첫~다섯 이동 단위의 지정 의미 판단을 완료한 결과로 수용한다. 17개 처분은 현재 구현 유지, 불필요한 이행 기본값의 정당한 제거, 이미 수용된 교정 유지다. 새 제품 결함이나 수정 필요는 확인하지 않았다. `workspaces.py integrate C:/math C:/math/.async/dm pr-base-ports-r`는 exit0·files=[]·changes={}였으며 task/integration.json에 기록됐다. queue에는 이 task만 accepted로 추가한다.

판단의 핵심은 효과를 포트로 옮겨도 현재 입력·권한·소유 검사를 유지한다는 점이다. `ResearchEngine.__init__`는 Repository/ModelRunner/Lean verifier/ControlTransport에 같은 ports를 전달하고 `wiring.real_ports`가 실제 구현을 조립한다. `runner_assignment`는 profile·host 자원·launch owner·UTF-8 input seal을 검사한다. `GitStateStore._call/_compare_and_swap`의 경계 재확인과 충돌, `external.execute_operation`의 전송 전 현재 grant 재검사·저장 및 불확실한 결과의 unknown 처리, `termination_confirmed`의 root/프로세스 종료 장벽이 유지된다. 옛 fallback과 계산 대체를 복구할 이유가 없다.

`ResearchEngine._call_steps`는 준비 결과의 값으로 callback/deadline을 등록하고 yield 뒤 등록을 해제해 수신한다. 분리 전후 문장 비교만으로 전체 동작을 인증하지 않으며, 작업자의 현재 생산/소비 연결과 이 순서의 직접 읽기를 함께 사용한다. core의 수신→저장→정산→저장은0089 수용판 그대로다. B38/B07·r07/r18와 기존 충분한 성질은 원래 한정 범위에서 재사용하며 과거 결함 동작을 보존하지 않는다.

## 확인 범위와 한계

protocol의 manager 절차, 공용 context/plan/seams, inbox, archive-resume·storage-scope 사용자 지시, objective/scope/report와 evidence/judgment.md·decisions.json을 읽었다. 위 현재 정의들과 f0ddec0f의 engine/model_runner/migration_defaults 실제 Git diff를 읽었다. 작업자가 보존한 current_connections.py와 cut_comparison.py의 분석 범위도 확인했다. 새 결과는 무변경 review라 제품 시험을 다시 실행할 필요가 없었다.

`verification-review.json`은 이번 `verify_review.py`의 읽기 전용 대조다. 제품 import·시험은0회다.

- 17개 처분의90정의 참조가 가리키는50파일 모두 기록 SHA·작업판·공용판이 같고 심볼 위치가 맞다. 이는 검토 판본의 연결이며90개 동작 실행이 아니다.
- 직접 연결21파일의 공용 SHA가 같다. 38직접호출의 필수 keyword 누락0과 넷째 단위 네 문장 AST 일치는 작업자의 보존 근거로 수용했다. manager가 그 분석을 다시 실행한 결과로 표시하지 않는다. partial/callback/동적 호출은 이름 검사와 구별한다.
- 작업자의32원보고 목록은 완결 메타데이터28·미완결4다. manager는 최초 clock 실패, close의 미완결, 1c/c5/b1 세 원보고를 직접 읽어 SHA·complete·집계를 대조했다. 각각292passed/2error와 실행중변경1, 최종집계 부재,336passed/1error/expected_failure1을 보존한다. c5의 engine source 지문은 작업자가 기록한 f2583f07 연결과 같다. 디렉터리명을 다섯째 단위 인증으로 쓰지 않는다.
- 작업자의 나머지 역사 hunk 처분과 원보고 비교는 명시된 범위의 근거를 수용했다. manager가15diff/32보고 전부나 과거 수용 작업을 재감사한 것은 아니다. 검토 보조 스크립트의 첫 실행은 c5의 중첩 경로를 잘못 선택해 StopIteration으로 끝났고 경로 선택을 고친 뒤 완료했다. 제품이나 작업자 결과의 실패가 아니다.

넷째·다섯째 단위와 연결되는 원 실행 및 과거 parent exit는 이 유한 원자료에서 인증되지 않는다. 현재 hunk의 정적 판단 완료와 과거 실행 인증의 한계는 별개다. 실패·skip·다른 판본을 합쳐 현행 전체 성공을 만들지 않는다. 실공급자·환경probe·Git쓰기·graphify 실행도 없다. 진행 중 worker의 사본이나 미완성 결과는 소비하지 않았다.

## 계획

기반1b/1c의 지정 질문은 닫고,0092의1a/1d와 함께 g1/g23 원인계에 이번 handoff-delta.json으로 보충한다. 이는 PR02/PR03/PR04 전체나 G2/G3/G8 인증이 아니다. 최종판 연결·기존 한정검토 밖의 실제 남김과 G1~G8은 유지한다. 별도1932행/전시험강도 감사나 원보고 부재만을 이유로 한 재시험을 추가하지 않는다.

저장범위 지시/A22에 따라 공통codec·검증게시·충분한 기존 업무 보장을 재사용한다. 가족별quota·반복 실호출·별도 장기감사를 만들지 않는다. 새 독립 결함/기능이 없고 현재 실행 가능한 전체관문은 이미 배정돼 있으므로 새 task는0개다. G6는 최종 stable T3/함수진입색인을 실제 소비하므로 그 결과 뒤 준비한다.

기존115개 task 정의·취소4건과 inbox.running의 g7-t4r 및 미시작 g45-final의 objective/고정입력은 불변이다. 전체T4(g7-t4r jobs1) → 수용판 전체일반/freshT3(g45-final jobs3) 순서를 유지한다. 이번 review를 관문의 새 선행으로 만들지 않는다. accepted109·미해결2·active로 게시한다. G1~G3 최종연결·나머지G7/G8과 환경6arc/10행, L01 Q1/Q2/원UTF-8 byte, 현지원 공급자 quota/복수result/역할동적schema 원자료 조건은 남는다. Q3 해결도 유지한다. 이후 완료 사건은 다음 manager가 처리한다.

## 게시 절차

공용 context/plan/seams와 이 수용 기록을 먼저 완성한다. 기존 배정은 유지한 queue.pending-0093.json에 수용 ID만 추가하고 `check.py queue RECORDS QUEUE_PENDING_FILE`을 실행한다. 검사 결과·문서 SHA·배정/고정입력 불변 확인은 queue-check.json에 남기고 검사한 임시파일을 queue.json으로 원자 교체한다. 게시가 이번 세션의 마지막 공용 변경이다. state.json과 기존 task 보고를 편집하지 않으며 수용·통합·종료 사본 정리는 실행기에 맡긴다.
