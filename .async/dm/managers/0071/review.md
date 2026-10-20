# manager 0071 — 입력·권한 부분 수용과 호출 처리 후속

## 판단과 통합

inbox.completed는 g5-inputs(exit0), running은 g5-worker·g5-publish다. protocol.md의 manager 절차와 공용 context/plan/seams, 저장 범위 추가 지시, 원설계3.3/A22·5.5를 읽었다. g5-inputs의 objective/report, 정본25파일 diff와 현재 caller, 시험 단언, 원보고/coverage를 검토했다. 정본8제품·16시험·1설명과 공식미러25개를 workspaces.py integrate로 충돌 없이 통합하고 부분 수용한다. 원보고 partial과 call_engine의 원5arc/5행 미완료를 유지한다. manager는 제품 코드를 직접 수정하거나 제품시험을 재실행하지 않았다.

## 변경을 받아들인 이유

CallEngineMixin._prepare_call은 _selected_action_current의 task_ready와 같은 상태에서 반복하던 두 번째 준비성 확인을 제거했다. 처음의 개정 대기·현재성, 입력 후 stop/설치/head 검사는 유지한다. goal audit의 처음 basis 검사와 input_head 비교 뒤 중복 판정, 성공한 SessionSlots.acquire가 이미 starting으로 바꾼 실행의 재전이도 제거했다. _receive_call의 마지막 fallback은 classify_run/collector의 completed·failed·stopped 및 앞 처분으로 모두 다뤄진다. handler 뒤 pause/close 보존 guard는 별도 미완료로 남아 있다.

governance.apply_decision의 두 형식 중복은 validate_decision_shape의 닫힌 GRANT 스키마가 먼저 검사한다. _configure_candidate는 host 변경 때 live 실행/예약을 반려하고 non-live action의 model_selection을 먼저 지우므로 뒤 갱신은 불필요하다. planning.evaluate_condition은 validate_condition 뒤 닫힌 문법을 소비한다. task_contracts는 returned-task 집합 일치 뒤 ID를 읽으며, BudgetConflict 생산자는 host/concurrency 두 종류만 낸다. repetition_hold는 history/dispatch 조건이고 등록된 waiting_actions 종류가 아니므로 해당 해제 분기를 없애고 다른 소유자의 대기를 보존했다. 공개 형식·권한·원문/봉인·현재성 검증을 줄이지 않았다.

payloads._decode_snapshot의 size는 최초 root에만 공급되고 _read_json_blob이 실제 bytes 길이·SHA256·canonical JSON 또는 이미 검증된 불변 artifact 경계를 확인한다. 중복 길이 검사 제거는 이 호출 계약에 한정한다. 두 순환 방어는 유지하며 같은 행의 사유 있는 제외를 수용한다. 검증된 내용 주소 그래프의 back edge를 실제 입력으로 만들려면 SHA256 fixed point/cycle 구성이 필요하기 때문이다. 이는 수학적 불가능의 증명이 아니며 현재 검증된 불변 artifact 위협모델의 실용적 도달 한계다. 해시 검사를 우회한 내부 대역을 만들지 않았고 실제 hash-matched DAG 중복은 정확히 반려하는 시험이 있다. 원설계5.5가 허용한 구체 제외이며 새skip·층/임계값 완화는 없다.

시험은 실제 decode, 승인 원문/봉인/권한, 상태·queue·저장 결과와 정확 반려를 단언한다. 호출 수신 표본은 실제 입력을 준비한 뒤 launch_not_created 영수증으로 정산하는 인프로세스 시험이다. 실제 OS Job/유료 공급자 성공으로 해석하지 않는다. 공급자 대기 시험의 새 pause 단언은 주어진 paused 상태 보존이며 공개 pause 전체 여정 인증은 아니다.

## 확인한 범위와 남김

verify.py와 verification-review.json은 원보고/보존자료 SHA, 선택과 고유 실제행, counts/fixture, 실행중변경, 원coverage와 소유모듈 SHA, 원좌표 처분, 제출시험 최종 변경 AST, 미러25쌍을 대조한다. check.py report는 PASS다. integration-check.json은 통합50경로와 보고 changes 및 공용/제출 bytes의 일치를 남긴다.

| 실행 | 실제 결과 | 관측 종료 |
|---|---|---|
| part1 부분T3 | 56행: 55passed/1error | 1 |
| part2 부분T3 | 12행: 10passed/1error/1failed | 1 |
| part3 부분T3 | 4행: 3passed/1failed | 1 |
| part4 부분T3 | 6행: 2passed/4failed | 1 |
| part5 부분T3 | 6행: 5passed/1failed | 1 |
| part6 부분T3 | 2행: 1passed/1error | 1 |
| part7 일반 | 1행: 1failed | 1 |

모두 complete=true지만 successful=false이며 fixture 오류/실행중변경은0이다. 부분T3의 gate도 false다. 실패한 구성/단언은 해당 후속 passing 행으로 연결되며, 실제 _register_execution 진입0회였던 review admission 표본은 철회됐다. 그 분기는 해결로 세지 않는다. 최종 세 시험 파일의 변경은 보존한 source와 비교해 철회1개 및 docstring 차이임을 AST로 확인했다. 서로 다른 판본/선택을 단일 최종 통과로 합산하지 않는다. 공식 미러 생성/check exit0 기록과 실제 제출25쌍도 확인했다. 소프트 초과와 앞 실패 비용은 원자료대로 남긴다.

원66arc의 처분은 raw arc 도달43, 예외 대상행 도달1, 제거15, 사유 있는 제외2, 남김5다. 원66행은 도달38/제거21/제외2/남김5다. 대상행 도달1을 raw branch 도달로 바꾸지 않는다. 이는 원측정 좌표의 부분 처분이며 최종 전체 gap 수나 전체G5 통과가 아니다. 현재 통합판의 최종G4/G5, G6~G8와 G1~G3 연결은 남는다.

## 후속 배정과 범위 교정

새 g5-calls는 수용된 g5-core·g5-inputs를 실제 선행으로 core_engine 잔여132arc/168행과 call_engine 잔여5arc/5행을 함께 맡는다. core 제어·게시/복구·결과 적용과 call 준비/수신의 연결된 구현·시험·설명을 한 task에서 처리한다. gap-scope.json은 두 원자료의 정확한 원/현재 좌표와 수용판 SHA를 연결한다. calls의5arc는 현재149→150,177→180,558→589,568→589,584→589이고 행150/151/180/183/205가 남는다. 마지막 두행의 GitStateStoreError 전파도 실제 port fault 또는 caller 불변식으로 판정해야 한다. 잘못된 review_scene 표본을 다시 살리는 대신 현재 실제 생산 전제를 확인한다.

g5-worker·g5-publish 배정/objective는 유지한다. 새 쓰기상한은 이 두task와 겹치지 않으며 각시험슬롯1로 합계3이다. 공용 이음새-정본.md는 publish 소유로 calls에서는 읽기전용이다. calls가 필요한 설명은 허용한 README/착수조건/초기화·정비 설명과 report에서 함께 끝낸다. 쓰기상한을 전수수정/시험 quota로 사용하지 않는다. 기존87정의·취소2건을 보존하며 g5-inputs를 accepted에 추가해83개 수용, 새task 포함88정의가 된다. max_workers10·gpt-6.1-sol/high·queue active를 유지한다.

다음 가용 슬롯에서 core 나머지7모듈33arc/29행, 독립 Lean·신뢰3모듈43arc/68행을 실제 파일 충돌에 맞춰 이어간다. g5-io 환경6arc/10행도 미완료다. 자원만을 위한 depends_on이나 모든 동료 종료 장벽은 만들지 않는다. 사용자 저장범위/A22에 따라 공통codec·저장검증·기존업무 보장을 재사용하고 전가족/전필드/새reader/옛head quota·새framework·장기감사를 추가하지 않는다. 현재 산출물과 원증거, 취소2건은 보존한다.

공용 문서와 objective를 먼저 완성하고 queue.pending.json을 검사한 뒤 같은 파일로 queue.json을 원자 교체한다. 그 게시가 이번 manager의 마지막 공용 변경이다.
