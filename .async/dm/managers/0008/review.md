# manager 0008 판단

inbox 완료 사건 r11만 처리했다. inbox의 r05·r03 시작 배정은 유지한다. 판단 중 도착하는 다른 완료 결과는 다음 manager가 처리한다.

## 수용한 결과

r11의 report.json·objective.md, evidence/review.md·verification.json·세 공식 원보고와 하위 row, 실제 base/workspace의 정본4개 diff를 대조했다. check.py report는 PASS다. source-review.json은 변경8파일·미러4쌍, 제출판과 공용판의 관련 불변 runtime/helper14파일, 실행별875 Python SHA와 원보고 해시·선택/실제 row를 직접 계산한 기록이다. workspaces.py integrate가8파일을 충돌 없이 통합했고 tasks/r11/integration.json에 기록됐다. 비용 캐시는 base로 복원됐고 runtime 변경은 없다.

assert_no_dispatch는 이전 중복 단언을 모으면서 예약/durable/owner 정리를 보강한다. recovery의 정확 보존 처분 추가를 runtime _recover_disappeared와 대조했으며 그 외 execution 전체·예약·종료 미확인 소유권을 보존한다. 기존 test_pairs나 다른 진행 task 코드는 변경하지 않았다.

until_active/live-future의 실제 전제는 공개 pause 중 승인된 maintenance 제한 복구와 공개 resume이다. lifecycle_engine._resume_lifecycle은 저장 active를 복원하고 미종결 execution 자체를 veto하지 않는다. scheduler는 stop/fence 검사 뒤 until_active를 보고 live future를 기다린다. 새 시험은 기존 검증된 fixture에서 실제 engine/runner/worker/collector를 거쳐 active·미완료 future의 wait를 관찰한다. 단계 상한 없이 run을 반환시키며 실행1개·accepted 영수증·artifact·confirmed 종료·예약/durable·Calls/owner 정리를 단언한다. 실제 CLI/Job/Lean 호출 성공의 증거는 아니다.

## 확인과 한계

- live-first: 1passed, task 기록exit0. 제출판과2파일 차이이며 최종판 증거로 사용하지 않는다.
- related-final: 9선택·9고유 row, 7passed/1failed/1error, task 기록exit1. recovery 처분 누락과 load 반환 순서 오류는 새 시험의 문제였다.
- corrected: 해당2ID만2passed, task 기록exit0. 원보고/하위 row 일치,875 Python SHA 전건 제출판 일치, 모든 실행 changed_during_run=[]. 다른7행은 수정과 무관한 성질만 유지하고 동일 최종판9passed로 합산하지 않는다.
- 미러4쌍 바이트 일치와 캐시2개의 base 복원을 직접 확인했다. task의 공식 미러 --check는1336파일 drift0·exit0 기록이다. manager가 새 제품 시험을 실행하거나 전체 미러 검사를 반복하지 않았다.
- 과거 B50 원보고7개와 B34 관련5개는 현재12개 모두 없다. counts를 새 성공으로 쓰지 않는다. r11의 기존 중도 stop/draining 성질은 실제 소스/단언 범위로 재사용한다.

R11/2-C의 현행 종료 전제·until_active 의미 질문은 해결돼 최종 판본 대기다. PR11 B50 조기 반환·B34 보존 처분 slice만 유지/보완한다. 전체 PR11, R15/R16, K/P2 전체, G4~G8, L01과 Windows1314 symlink 미검사는 남긴다.

## 후속 선택

r14는 8-A의 진행성 성질을 현재 원천에 대응하고 빠진 실제 입력/단언을 수리한다. requirement-state의 알려진 공백은 경쟁 관찰 부하 속 기계 완료 회수다. 기존 AI/관찰의 세 progress 시험과 기계 pause 시험·동일 owner observer를 함께 다루는 유한 묶음으로 배정한다. 기계/AI의 모든 반환 조합 R15/R16까지 확대하지 않는다. 실제 발견된 해당 runtime 결함은 parallel/scheduler의 한정 범위에서 같은 task가 수리한다.

r14는 r03/r05와 의미 있는 writes가 겹치지 않으며 두 결과도 필요하지 않아 depends_on=[]다. r11 종료 증거를 읽을 수 있지만 진행성 구현의 선행 API는 아니므로 인위적인 dependency를 넣지 않는다. worker gpt-6.1-sol/high·jobs1·최대3을 유지한다. 공용 context/plan/seams와 objective를 먼저 준비하고 별도 queue.pending.json을 check.py queue로 검사한 뒤 queue.json으로 원자 교체한다. 게시 이후 이번 manager는 공용 파일을 수정하지 않는다.

제출 검사: `python C:/math/services/async-development/check.py queue C:/math/.async/dm C:/math/.async/dm/managers/0008/queue.pending.json`은 PASS queue·exit0이다. 검사한 임시파일의 내용은 더 수정하지 않는다. 게시할 queue와 공용 문서/objective의 해시는 publication.json에 보존한다.
