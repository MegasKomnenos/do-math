# manager 0003 판단

inbox의 완료 사건은 protocol-checker이고 cli-adapter는 시작된 배정을 유지한다. 사용자 원문, 공용 context/plan/seams, protocol-checker objective/report, 제품 protocol.md/check.py/tests/test_check.py를 읽었다.

산출 계약은 입력 세 층, 범주별 산출, 결과별 독립 검토와 목표 검토의 구분, 공개 산출만의 전달, 기록 전체 대체와 검토 승계 방지, 계획 게시와 사건 의미를 제공한다. 검사 코드는 구조·참조 실재와 전달에 필요한 대상 일치·항목 완결성을 확인하며 Lean 실행·현재성·연구 가치 판단을 하지 않는다. 공개 후 작성자 폴더가 없어도 검토 가능한 구조가 테스트에 포함돼 있다. 제품 문서를 읽는 실행기/문서 작성자가 필요한 계약을 회수할 수 있으므로 수용한다.

task 보고의 3개 unittest 및 문서 예시 실행은 작성자가 수행한 근거다. manager는 테스트 코드를 읽었으며 같은 실행을 반복하지 않았다. manager가 실행한 check.py report는 PASS였다. workspaces.py integrate는 check.py, protocol.md, tests/test_check.py 세 파일을 충돌 없이 반영했다. 실제 모델·Lean·실행기 흐름·Git 반영은 이번 수용의 확인 범위가 아니다.

독립 후속 session-contexts는 protocol-checker만 선행으로 두고 네 작업맥락 문서를 작성한다. CLI 어댑터의 진행 중 배정을 수정하지 않는다. 실행기는 CLI 어댑터 수용 후 바로 배정할 수 있으며 문서 완성 대기를 구현 착수의 선행으로 추가하지 않는다. SKILL 안내는 실행기 명령 수용 뒤 연결한다. 계획이 이미 게시한 미완료 과제를 읽는 구체 상태 경로는 실행기에서 제공해야 한다는 소비 요구를 seams와 objective에 남겼다. 새 검사나 감시 장치를 추가하는 요구는 아니다.

공용 문서와 objective를 먼저 준비하고 별도 queue.pending.json을 검사한 뒤 queue.json으로 원자 교체한다. 게시 후 공용 파일은 더 수정하지 않는다.
