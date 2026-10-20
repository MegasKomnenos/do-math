# manager 0040 결과 판정

r49-startup을 수용한다. check.py report PASS/exit0과 실제 변경을 대조한 뒤 workspaces.py integrate로 정본13·미러13을 충돌 없이 통합했다. manager는 제품 코드를 직접 수정하거나 제품 시험을 재실행하지 않았다. source-review.json과 integration-check.json은 제출 26파일의 base/작업판/통합판 SHA, 13미러쌍, 비용캐시 own base 복원, 선행11심볼 AST 불변과 역사 원보고2개를 확인한다.

새 owner의 run이 옛 running 실행을 복구하기 전에 예정 검토를 열던 결함을 수리했다. run은 inbox 적용→이전 실행 복구→upkeep 순서이며 제어 전용 process_controls는 due 예약 생산만 실행 owner에게 남긴다. 수락된 continue가 실제 생산한 예약의 tracker 유무·기한·stopping/ended·재시작11국면과 빈 caught-up tick, 살아 있는 대상1회/끝난 대상0회 및 원 예약 보존을 단언한다. 대화 임대의 처리 UTC·expiry>now·generation/두 policy는 불변이고 공개 run의 입력 없는 경과·상실1회·재시작 불변을 추가했다. 관찰 received_at 규칙으로 임대 시각을 바꾸지 않았다.

ResearchEngine.run의 선택 installation_manifest와 CLI --installation-manifest는 기존 bootstrap.verify_snapshot/startup_evidence로 독립 동결본을 검증·대조한다. manifest 부재는 no_recorded_manifest이고 독립 검증 성공이 아니다. 다른 root/동결본 손상은 오류, live 차이/관측 불가는 배정 전 pause이며 종결은 유지한다. startup.json과 결과에 설치/Git 관측·runtime_root·polling_edition·observed_at을 남긴다. 직접 operator check/probe/wake/engine과 예약 main은 execute의 동작 전 기동 기록을 공유하고 예약 child는 동결 manifest 경로를 전달한다. 전체 설치 대조와 기존 진행 중 polling 모집단을 구별하며 수리 보고/원 provider 결과·lock·복구 owner는 보존했다.

verification-review.json은 원보고5개의 SHA·선택/고유row/counts·하위 result와 판본을 대조한다. focused의3passed/2failed/2error·exit1은 실제 예약 결함과 준비/봉투 오류를 구별해 보존한다. corrected4passed, related-final32passed, submission-final6passed, owner-final3passed는 별도 판본이다. 마지막3ID의889 Python SHA는 제출판과 전건 일치한다. 앞6통과 이후 변경은 core/engine의 제어 전용 scheduling과 예약 시험에 한정된다. 모든 fixture_counts/changed_during_run은 비었고 task 관측 exit와 소프트 초과를 보존한다. 마지막82초 중 예약63.235초/기준60초, 임대12.890초/기준2초다. B83/B91의 역사100/7passed와 B52 Temp 부재는 현재 전체 인증으로 승격하지 않는다.

R49 및 R50 엔진/직접 CLI의 지정 질문과 발견 수리는 해결·최종 통합판 증거 대기로 옮긴다. 전체6-A/12-A·PR15/PR19·다른 K/P2·G4~G8·L01/Windows1314와 최종 review는 남는다.

inbox.running의 keep-inputs/keep-storage 정의를 유지한다. 새 keep-evidence는 KEEP-FAKE-EVIDENCE의 K-38/39/41/42/72/75를 한 task에 묶어 합성 Lean·host 증거, checker/승인 명령, fake 기본 상태와 준비 경로 보존의 필요한 수정·최소 확인을 맡는다. 실제 소비하는 keep-templates/r03만 선행이며 바로 시작할 수 있다. 진행 중 역할 입력/저장 파일은 읽기 전용이고 의미 있는 writes는 독립이다. 공통 비용캐시는 각자 own base로 복원한다. 세 task는 각 jobs1·동시시험worker 상한3을 유지한다.

context/plan/seams와 objective를 먼저 완성하고 별도 queue.pending.json을 검사한다. 기존 task 정의와 inbox 시작spec 일치를 assignment-review.json에 남기며, 검사한 pending bytes를 queue.json으로 원자 교체하는 것으로 이번 공용 변경을 마친다. 이 manager 도중의 추가 완료 사건은 다음 inbox에서 처리한다.
