# 입구와 보존자료의 남은 계약

manager0084는 g5-core-tail의 명시적/native 캡처 재조회 실패 수리를 통합·부분 수용했다. 남은 원56arc/60행을 같은 core 파일의 세 유한 묶음으로 나눴다. 이 작업은 10함수의 원10arc/12행에 해당하는 아래 계약 판단을 맡는다. 좌표는 이전 전체T3에서 나온 질문의 범위이며 시험quota가 아니다. 수리와 필요한 확인을 함께 끝낼 크기로 줄인 배정이다.

실제 선행은 g5-core-tail 하나다. 같은 core_engine.py·직접 helper·설명/미러의 통합판을 소비하기 위한 순서이며 다른 독립 작업의 완료를 기다리는 장벽이 아니다. 앞 결과가 partial이면 그 보고의 남김을 완료로 간주하지 않는다.

## 이번에 해결할 결과

1. _control_result의 publication_parent/후손, _context의 operational target·위임 원요청, _submission_repair_context의 response lineage는 실제 생산자·수신자·참조 정본을 짧게 따라가 먼저 판단한다. schema에 optional이라고 쓰였다는 이유만으로 지원되는 결손 상태라고 간주하지 않는다. 반대로 외부 Git/artifact 읽기 실패를 내부 불변식으로 지우지 않는다.
2. 방금 수리한 explicit/native capture의 재조회 실패와 원 영수증 재사용은 재실행하지 않는다. 남은 head 전진 뒤 재조회 실패·native 현재성 분기는 _save/_reload의 head 채택 뒤 _evaluate_stops/ModelCalls.judge 예외 소유를 먼저 읽는다. 실제 가능한 입력/오류일 때만 최소 확인과 필요한 수리를 한다. 앞 수리의 원 메모리 보존/무중복 계약은 유지한다.
3. 과제 개정 뒤 overflow의 selected_contract_sha256 보존, check의 기존 blocked와 불완전 제출의 우선순위, 공개 handler Git 오류의 전파/원 요청 보존을 기존 helper에서 필요한 만큼 판단한다. 무관한 overflow/cleanup 전이는 다시 실행하지 않는다.
4. submit_control의 acceptance lock 뒤 FileExistsError는 실제 지원 writer/물리 경계를 판단하고, _installation_manifest 캐시 재열거의 OSError는 최종 manifest/실패 의미를 판단한다. lock 해제나 내부 함수 대역으로 가상 도달을 만들지 않는다. 외부 파일 오류는 외부 포트 또는 자기 임시 파일에서 제어한다.

## 실제 범위와 판단 방식

SESSION_JSON, task.json, inputs/context.md·plan.md·seams.md, 자기 workspace의 do-math AGENTS.md와 시험-지침.md를 읽는다. 절대경로 원자료는 읽기 전용이다. 자기 gap-scope.json은 manager0084 수용판의 좌표/심볼과 원 g5-full 좌표를 함께 보존한다. 앞 task 통합으로 줄번호가 바뀌면 자기 base의 실제 함수로 다시 연결한다. 앞 작업의 완료되지 않은 범위까지 자동으로 인수하지 않는다. 이전 worker의 제안 시나리오는 확정 요구가 아니다.

이 묶음의 현재 계약 판단·필요 구현·최소 확인·설명/미러를 한 task에서 마친다. 공통 입력/저장 검증과 실제 생산/호출 불변식부터 읽고, 충분하면 정적 근거로 종료한다. 행마다 새 시험을 만들지 않는다. 불필요한 방어는 실제 전제에 따라 줄일 수 있다. 현재 구조·권한·참조·증거·현재성 검사는 유지하고, 외부 오류를 불가능한 내부 상태로 바꾸지 않는다. 제외가 필요하면 원설계5.5의 같은 행 사유와 실제 caller/불변식으로 판단한다. 자동제외·blanket no-cover·새 skip·층/분모/임계값 완화는 하지 않는다. 수치 감소 자체가 완료가 아니다.

제품 쓰기는 task.json의 경로에 한정한다. 목록은 수정·시험 의무가 아니다. core와 해당 직접 소비 시험/helper·설명을 같은 소유자가 맡는다. integration/submission은 허용된 경우에도 맡은 core 계약의 직접 결함 수리에만 수정한다. 다른 제공자 수리가 필요하면 원인/영향/최소 범위를 보고한다. 실행 중 g23-handoff의 고정 배정이나 기록을 바꾸지 않는다. g23 인계·전체 관문을 이 작업의 선행으로 삼지 않는다.

## 최소 확인과 제출

storage-scope-direction-2026-10-15.md와 설계3.3/A22를 적용한다. 공통codec·검증게시·기존 업무 증거는 재사용하고 가족별 전필드/새reader/옛head quota·별도 장기감사·새 검증 framework를 만들지 않는다. 새 검사는 남은 구체적 불확실성을 설명할 수 있을 때만 수행하고 충분해지면 끝낸다. 원자료가 없다는 이유만으로 같은 환경probe·공급자호출을 반복하지 않는다.

시험슬롯1, 공식 scripts/run_tests.py --jobs 1로 한 번에 한 명령이다. 도달이 실제 남은 질문이면 그 최소 선택의 --tier T3를 사용하고 일반/T3를 중복하지 않는다. 전체 G4/fresh전체T3·변이·T4/T5·병렬자식 meta검사·유료/실예약·설치변경은 이 배정 밖이다. 제품 함수 대역은 쓰지 않고 실제 외부 포트에서 필요한 오류를 제어한다. 시간초과를 시험실패/skip/변이포착으로 세지 않는다.

측정에 필요할 때만 자기 workspace의 독립 .git과 실제 시작bytes 기준commit을 준비할 수 있다. root/HEAD·전후bytes를 남기고 공용 Git/index/commit, 다른 .git 복사, 가짜HEAD/global 설정/remote/push는 하지 않는다. 기존 GIT_CEILING_DIRECTORIES를 유지하고 자기 부모와 저장소밖 짧은 전용 임시root만 더한다. 이전 evidence/prepare.py·run.py는 절차를 참고하되 자기 경로를 사용한다.

command/cwd·관측exit·원report/stdout/stderr/coverage·선택/실제행·fixture·소스판본/실행중변경을 보존한다. T3 store/index/timing은 필요한 자료 보존 뒤 시작bytes/부재로 복원한다. 부분 gate=false/exit1과 실제 시험실패를 구분하며 다른 부분판을 전체성공으로 합산하지 않는다. 공식 build_skill_mirrors.py로 변경 정본의 미러를 생성/check한다.

evidence/judgment.md와 report.json에 수리/줄인 전제/재사용 근거/직접 확인과 한계·남김을 적는다. 자기 유한 질문별 판정과 근거를 남기되 새 전수 원장을 만들지 않는다. complete는 이 묶음의 질문 해결이며 미완료는 partial이다. 외부 입력 없이 수행 가능한 미완료를 blocked로 부르지 않는다. check.py report RECORDS TASK를 통과시킨다. 공용 문서/queue/state·다른task·engine·graphify는 수정하지 않는다. 최종G1~G8·환경6arc/10행·L01/실원자료 조건은 전체계획에 남는다.
