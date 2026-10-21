# manager 0006 판단

inbox의 완료 사건은 runner 하나이고 실행 중 task는 없었다. 사용자 원문, 공용 context/plan/seams, runner 배정·보고, 변경 파일 6개의 신규 본문 또는 변경 diff를 읽었다. RUNTIME 진입→설정/init/start→status·정지·입력·개별 종료→계획 요청 상태→공개 반영·복구 경로를 실제 runner 심볼과 대조했다.

Runner.dispatch는 common/protocol/goal·범주 문서·task를 연결하고 계획에만 요청 상태를 안내한다. tick/collect/finish/apply_output은 단일 계획·전체 상한, 종료 코드와 독립된 공식 재검사, 전체 output 공개·Git, 자동 검토·사건, 완료 후 파견 차단과 기존 산출 처리를 구현한다. 세션 호스트·PID 생성 식별값·상태 원자 저장은 재기동 시 기존 프로세스를 기다리고 중복 파견/반영을 피하려는 구현이다. 환경 고정·수학 판정·추가 AI 역할을 만들지 않는다. provider_for_model/build_command 변경은 공급자 접두 계약과 일치하고 시험은 `/`를 포함한 모델 나머지도 확인한다.

task는 runner 시험 6개와 어댑터 시험 8개 통과를 보고했다. manager는 가짜 CLI와 실제 검사기·Git을 사용하는 시험 코드의 assertion을 대조했으며 같은 실행을 반복하지 않았다. 실제 두 모델·Lean·실제 한도·Linux·호스트 재부팅은 확인되지 않았다. 수용을 막는 결함을 이 검토에서 발견하지 않았다. `check.py report` PASS 후 `workspaces.py integrate`가 변경 6개 파일을 충돌 없이 통합했다. integration.json에 기록됐다.

runner를 accepted에 추가한다. 기존 skill-entry 배정은 그대로 두며 그 두 선행이 모두 수용되어 파견 가능하다. 독립적으로 먼저 처리할 새 기능은 없고, 실제 사용자 진입 안내가 필요한 mixed-completion의 objective와 queue entry를 미리 준비한다. 그 task는 skill-entry에 의존하며 실제 완주와 필요한 사용 결함 수정을 함께 맡는다. 최종 review는 실제 완주와 그 수정까지 수용된 뒤 준비한다. 개발은 active이며 완료로 판정하지 않는다.

공용 context/plan/seams와 objective를 먼저 갱신하고 managers/0006/queue.pending.json을 검사한 뒤 queue.json으로 원자 교체한다. 게시 뒤 이번 manager는 공용 변경을 끝낸다.
