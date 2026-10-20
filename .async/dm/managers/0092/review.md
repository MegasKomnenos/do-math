# Manager 0092: 기반 1a·1d review 수용

## 판단

inbox.completed의 pr-base-tests(exited/0)를 검토했다. scope.json의 기반1a 실행기/구조검사와1d Sim/ModelDouble/Calls·템플릿/A19/A25/corpus seed의 BT01~BT09 의미 판단을 완료한 결과로 수용한다. 새 제품 결함이나 제품 수정은 없다. `workspaces.py integrate C:/math C:/math/.async/dm pr-base-tests`가 exit0·files=[]·changes={}를 반환했고 task/integration.json에 기록됐다. queue에는 이 task만 accepted로 추가한다.

최초 구현의 묵시 binding fallback·terminal이면 무조건 성공·정상 close의 미시작 계산 누락은 이미 교정된 약점이다. 현행의 정확 receipt 후 provider 종료, 원계산/collect와 정상 close·owner-loss 분리, 공개 활성화의 해당 receipt와 active 검사, 준비판 복원/미정산 자원 반려를 유지한다. core의 수신→저장→정산→저장도0089 수용판과 일치한다. 옛 구현을 보존한다는 이유로 이 교정을 되돌리지 않는다.

## 직접 확인한 범위

protocol의 manager 절차, 공용 context/plan/seams, inbox, archive-resume·storage-scope 사용자 지시, objective/scope/report와 evidence/judgment.md·decisions.json을 읽었다. 현재 run_tests의 선택/보고/격리, known_defects의 expectedFailure/closed mark 반려, os_lock의 잠금 후 초기화/해제, ModelDouble 송신/receipt/종료, DeterministicCalls의 종료/owner-loss, Sim 활성화/준비판 복원, core publication 재시도 정의를 정적으로 대조했다. B36/B48의 실제 교정 hunk와 현재 소비를 연결했다.

`verification-review.json`은 이번에 실행한 `verify_review.py`의 읽기 전용 비교다. 제품 import·시험은 없다. 실제 확인은 다음과 같다.

- task의 현재67정의 참조가 가리키는28파일 모두 기록 SHA·작업판·공용판이 같다. 정의의 위치/판본 연결이며67개 동작 실행을 뜻하지 않는다.
- 보존된8commit diff의 bytes/SHA가 읽기 전용 Git show와 같다.
- 원보고8개 SHA·선택/고유실제행·집계·complete/successful을 대조했다. 1a b1의1error와 b2의1skip, c-red의1failed/3error는 그대로다. c-green5passed·d-template4passed·d-t2/d-t2b 각113passed는 각각 별도 실행이다.
- 재사용 비교의 실제 목록은19연결이며 파일일치18·기록된 AST일치6이다. 과거 판단 원본의 해당 정의/파일SHA와 재사용 목록을 대조했다. 보고 본문17연결/16파일일치/4AST일치는 ScenarioModel.render와 record_submissions 두 연결을 빠뜨린 집계다. 원보고를 덮지 않고 이 manager 기록과 공용 설명에서19/18/6으로 정정한다. 별도 task를 요구할 제품 결함은 아니다.
- B56 Temp4개와 B36 Temp5개의 현재 부재를 확인했다. file_io의 재사용 파일SHA 불일치는 숨기지 않고 현재 정의와 직접 잠금 시험을 읽어 판단했다.

원실행 outer exit를 이번에 관측하지 않았다. 원보고의 LF/CRLF·중간판 연결과 전체 의존판본 미인증 한계는 worker의 한정 판단대로 유지하며 과거 실행을 재인증하지 않는다. 제품시험·실공급자·환경probe·Git쓰기·graphify는0회다. 모든 과거 수용결과를 다시 검사하거나 진행 중 worker의 미완성 산출물을 소비하지 않았다.

## 계획과 사용자 범위 지시의 적용

기반1a/1d의 지정9개 질문은 닫는다. 이는 G2/G3/G8 전체 인증이 아니다. g23의 기존72개 한정재사용과0086/0087의 추가37건 처분, PR05 차이 해명, K61/P2의 충분한 성질은 재사용한다. 원인계는 유지하고 handoff-delta.json으로 이번 처분과 집계 정정만 보충한다.

저장범위 지시/A22에 따라 구조검사의 알려진 한계를 새 구체 결함으로 취급하지 않는다. 공통codec·검증게시·기존업무 보장은 재사용하며 전가족/전필드 quota·자료 없는 과거 실행의 반복·새1932전수강도감사·별도 장기감사는 배정하지 않는다. 기존 실제 남김과 G1~G8은 축소하지 않는다.

inbox.running의 g7-t4r·pr-base-ports-r와 미시작 g45-final의 정의/objective/고정입력은 그대로다. 기존115정의와 취소4건은 보존한다. 전체T4(g7-t4r jobs1) → 수용판 전체일반/freshT3(g45-final jobs3)의 순서와 독립 기반1b/1c review(슬롯0)를 유지한다. 이번 review를 전체관문의 포괄 선행으로 만들지 않는다. 새 독립 결함/기능이 없고 기존 결과물은 배정돼 있으므로 새 task는0개다.

G6는 최종 stable T3/함수진입색인 뒤 실제 모집단을 준비한다. G1~G3 최종연결·나머지G7/G8과 환경6arc/10행, L01 Q1/Q2/원UTF-8 byte, 현지원 quota/복수result/역할동적schema 원자료 조건은 남는다. Q3 해결도 유지한다. accepted108·cancelled4·미해결3으로 active를 유지한다. 이후 도착한 사건은 다음 manager가 처리한다.

## 게시

공용 context/plan/seams와 이 수용 기록을 먼저 완성한다. queue.pending-0092.json은 기존115개 task 정의와 취소 목록을 그대로 두고 pr-base-tests만 accepted에 더한다. pending 파일에 `check.py queue`를 실행하고, 통과한 파일의 SHA와 진행 중/대기 배정 입력 불변을 확인한 뒤 그 파일을 queue.json으로 원자 교체한다. 검사 결과·문서SHA·변경 배정 수는 queue-check.json에 남긴다. 게시가 마지막 공용 변경이다. state.json과 다른 task 기록은 편집하지 않으며 수용·통합·종료 사본 정리는 실행기에 맡긴다.
