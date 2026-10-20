# 큐 검사 반복 읽기 수정

사용자가 발견된 문제를 즉시 고치고 테스트 파일을 추가하지 말라고 지시했다. 추가했던 test_checks.py는 제거했다. services/async-development/check.py에서 report_metadata와 실제 workspace 대조를 분리했다. queue는 기존 수용 report의 형식과 integration.json의 task ID·변경 경로·writes 일치를 확인하며 과거 workspace 전체를 다시 해시하지 않는다. report 명령과 integrate의 실제 변경/범위·충돌 검사는 유지했다. 최종 review·의존관계·미완료 task 종료 조건도 유지한다.

운영자 확인: 기존0036 pending 큐는 확인 중 이미 게시되어 해당 경로 조회는 실패했다. 게시된 실제 queue를 수정된 검사로 확인하여 PASS를 받았으며 keep-templates의 기동과 accepted46을 관측했다. 전체 실행기 재시작이나 과거 로그 변경은 하지 않았다. 서비스는 다음 check.py 호출부터 수정된 코드를 사용한다.
