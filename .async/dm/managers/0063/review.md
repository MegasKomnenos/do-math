# manager 0063 판단

control-currentness의 두 의미 질문을 수용했다. check.py report는 PASS, workspaces.py integrate 결과는 files=[]다. 제품·시험·미러 변경은 없고 manager의 제품 시험 실행도 0회다. verification-review.json에서 지정17파일의 공용/작업사본/보고 SHA 및 r08 대비 심볼 AST 판정을 직접 대조했고, 재사용한 r08 원보고3개의 SHA·원선택·실제 관련 row·관측 exit·fixture/실행중변경·소프트예산이 task 기록과 일치함을 확인했다.

원 결함-범주 2-A:358~361/A-02:384의 목적은 전제가 없어진 요청을 정확히 한 번 반려·소비하고 뒤 정상 입력을 진행하는 것이다. 현재 submit_control/_apply_inbox는 supplemental_research의 runtime.tasks 대상과 planning.task_ready를 접수/적용 때 각각 검사한다. 적용 때 준비 소실이면 원request/정확 사유를 history에 저장하고 processed_controls에 넣어 뒤 요청으로 continue한다. cycle 상태를 조건으로 참조하는 과제는 evaluate_condition에서 현재 상태를 읽지만 무관한 cycle의 종결 자체가 모든 과제를 무효화하지는 않는다.

cycle 결속 내부 조사는 _defer_review_for_research가 knowledge target/review_cycle_id/research_request_id를 생산하는 별개 경로다. _knowledge_control의 공개 revise/invalidate는 cycle을 unresolved/ended, pending research를 cancelled로 기록하고 관련 행동을 은퇴시킨다. _obsolete_review_reason와 준비/회수 경계는 낡은 행동과 원결과 보존을 구별한다. 이를 근거로 역사 cycle 직접대상과 현행 task_ready의 대응 질문은 해명 완료·최종 통합판 증거 대기로 옮긴다.

삭제 질문은 접수 대상 task/execution/review-cycle의 실제 현재 생산자·변경자 범위에서 비적용·공개 생산자 없음으로 판정했다. task_scope 철회는 원 task와 처분/이력을 남기고, 개정은 같은 ID의 계약/결과 이력을 보존하며, cycle 종결/지식 교체도 과거 기록을 남긴다. retention.cleanup의 물리 삭제는 승인/종료/참조보호/보관을 거친 local runs 디렉터리이며 execution map 삭제가 아니다. 임의 del fixture/옛 API/새 삭제 기능을 만들지 않는다. 이 판정은 R09/R10의 다른 입구나 모든 파일·외부 손상·미래 API에 대한 삭제 부재 보장이 아니다.

기존 r08 stale-final은 관련1passed·exit0, related는 종결 요청 row passed이지만 전체26passed/1error·exit1, focused는 두 수송 양순서 row passed·전체8passed·exit0다. related의 deepcopy NameError와 후속 교정판을 보존한다. 공개 task_scope revise가 실제 준비 소실을 생산하고 반려 원내용/소비1회/뒤pause/재시작을 검사하는 현재 시험 본문을 확인했다. 최초 ready task는 support fixture라는 한계를 유지한다. 내부 조사 취소 flow는 이번에 정적으로만 읽었으며 실행 성공을 새로 주장하지 않는다. 서로 다른 판본의 통과를 현재 전체 성공으로 합산하지 않는다.

다음 결과물은 G4다. g4-general 한 task에 현재 통합판 기본 전체 선택과 실제 발견 결함의 관련 구현·시험·미러·직접 확인을 묶었다. 현재 run_tests.DEFAULT_FOLDERS=TIERS['T3']는 structure/unit/contracts/sim/flows이며 기본 일반 실행은 측정 T3 및 boundary/smoke와 다르다. 하나의 최종판에서 선택/실제행/exit/판본을 완결한다. 수리 뒤 필요한 작은 확인과 최종 전체 확인은 같은 task가 맡고, 충분한 전체 성공은 이유 없이 반복하지 않는다. 전체 성공이 없는 partial 결과는 G4 완료로 수용하지 않는다.

inbox.running=[]이고 state의 task 목록에도 실행 중 worker가 없다. 기존77개 task 정의와 두 취소 상태는 유지한다. g4-general의 선행은 수용된75work 전부를 포괄하는 DAG 끝점13개다. 이는 전체 통합 후보를 검사하는 실제 입력 관계다. worker gpt-6.1-sol/high, max_workers10은 유지하며 이번 단독 전체 일반 실행에 시험 슬롯3개를 배정했다. 다른 시험 작업은 병행하지 않는다. 지금 확인된 독립 신규 구현은 없고 fresh T3는 G4의 실제 수리/수용판이 필요하므로 이번 큐에 선실행 배정하지 않는다.

사용자 저장 범위 교정은 유지한다. 기존 유효 저장 수리/시험을 보존하고 84가족 quota·전필드/새reader/옛head 재입증을 되살리지 않는다. 별도 장기 감사를 만들지 않는다. G5 freshT3, G6 변이/정상 기준, G7 실제 경계/녹화, G1~G3의 최종 근거 연결, L01/Windows1314와 G8 최종 review는 남는다. 전체 프로젝트 상태는 active다.

공용 context/plan/seams와 objective를 먼저 갱신하고 queue.pending.json을 검사한다. 검사한 같은 bytes를 queue.json으로 원자 교체하는 것이 마지막 공용 변경이다. 제품 수정은 task의 workspace에만 맡긴다.
