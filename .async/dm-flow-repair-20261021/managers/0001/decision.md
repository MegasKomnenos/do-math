# manager 0001의 배정 판단

이번 inbox에는 completed/running/task 항목이 없다. 최초 queue와 state에도 task 배정이 없어 결과 통합·수용할 대상은 없다. accepted는 빈 목록으로 유지한다. 원 연구와 제품 코드는 변경하지 않았다.

protocol manager 절차, 공용 context/plan/seams, user-messages의 최신 정정, 정본 개발 원칙과 검사/질문/개정/저장/역할 문서 지급의 관련 실제 코드를 읽었다. 직접 정적 확인한 범위와 미조사 범위는 context 7절에 구별했다.

역할 모집단과 R2~R3의 공유되는 업무 상태는 전체 흐름 설계가 먼저 있어야 한다. 이를 한 설계 task에 맡겨 서로 다른 구현자가 처분/질문 상태를 각자 정의하지 않게 했다. 이 결과가 R1~R3의 제품 수정·검증을 대신하지 않는다. 공통 검사/해시와 payload 조회는 이미 인터페이스 경계를 확인했으므로 독립 구현으로 함께 배정한다. Windows/패치 문맥 안내와 Codex timeout 진단은 해당 결과에 의존하지 않아 지금 배정을 준비했다.

다섯 task 모두 선행 의존성이 없으며 max_workers=3에 따라 처음 세 작업이 우선 실행 가능하다. 준비 스크립트는 정본/미러/시험/산출 경로의 task 간 중복이 없음을 확인했다. 각 제품 task는 관련 구현·문서·시험·공식 미러를 맡은 범위 안에서 함께 마무리한다. 추가 파일 수정이 실제 필요한 경우 후속 manager에게 근거와 정확 경계를 보고하도록 했다.

공용 context/plan/seams 및 모든 objective를 먼저 작성한 뒤 `managers/0001/queue.pending.json`을 생성했다. 게시 전 서비스 `check.py queue`로 이 파일을 확인하며, 통과한 바이트를 `os.replace`로 마지막에 queue.json에 게시한다. 게시 후 공용 변경을 이어가지 않는다. 다음 manager는 완료 사건의 산출물을 대조해 integrate로 통합·수용하고, 설계가 도착하면 runtime 구현을 신속히 준비한다.
