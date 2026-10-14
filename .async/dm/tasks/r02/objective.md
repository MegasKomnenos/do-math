## 목적과 역할

R02 작업자 요청의 실제 생산·수신과 역방향 필드 대응를 자기 workspace의 이관 검수판에서 판정한다. 원래 1-A의 여섯 가족 중 작업자 요청 가족만 맡는다. tracking-state R02와 requirement-state 1-A의 해당 질문, 설계3.3/A20의 필수+선택 필드 역방향이 기준이다. 현재 ModelRunner 및 실제 남아 있는 runner/adapters가 만든 요청과 check_codex_request/check_claude_request·worker load 경계를 연결한다. 역사 CodexModelRunner 이름이 현재 다른 정의로 이동했으면 현재 호출부로 설명하고 구판 경로를 복원하지 않는다. 006/007에서 이미 검수한 전송/collector/pair 결과는 재사용하며 공급자 전체나 저장·trust·조건/영수증 가족을 다시 조사하지 않는다.

이 작업은 유한한 남김의 판단 자료를 만드는 work다. G1/G2/G3의 지정 질문을 닫거나 정확 수리로 바꾸며 최종 review가 아니다. 다른 async task 결과를 기다리거나 소비하지 않는다.

## 입력과 실행 위치

SESSION_JSON의 workspace에서 현재 코드와 시험을 읽는다. inputs/context.md·plan.md·seams.md, objective.md·task.json이 이번 배정의 정본이다. C:/math 공용소스와 다른 task 기록은 읽기 전용이다. inputs의 스킬 상대 경로는 workspace 기준이며 절대 경로는 원자료다. 과거 문서 안 `run:`은 C:/math/docs/do-math/continuous-development-2026-10-13, `repo:docs/`는 C:/math/docs/를 뜻한다. 과거 `repo:.claude/` 코드는 현재 workspace에서 확인한다. 기존030 objective는 질문의 출처이며 그 phase/cwd/report/공용쓰기 절차는 사용하지 않는다.

## 완료 조건

### A1 현재판과 필요한 원문만 고정

baseline.json과 inputs를 사용해 자기 시작판을 고정한다. managers/0001/source-inspected.json의2675 스킬 파일과 자기 baseline의 해당 경로를 대조하고 실제 차이를 기록한다. root 지침6파일과 과거 docs의 snapshot 부재는 제품 결함이 아니다. 해당 requirement-state/tracking-state ID와 원문·설계, 직접 연결 K/P2만 읽는다. 103행 전체 재분류나 기존 충분한 후보의 전수 재감사를 반복하지 않는다. 사용한 정의·단언·원보고 판본과 소스 해시를 evidence에 남긴다.

### A2 남은 모집단과 실제 단언 대응

현재 공급자 전건, execution identity/profile_ref의 유무, resource_limits, control_binding, scholarly_server, claude_only_assigned_model의 허용 조합, schema 경로, adapter 고유 필드의 생산/소비를 branch-field-map.json에 연결한다. 원문에 적힌 0/1/여럿·선택 필드 축이 이 요청 가족의 어느 값에 적용되는지 실제 코드로 판정하고 적용 불가이면 이유를 적는다. _worker_request_samples의 5불리언 곱과 제외 조합이 실제 runner 전제와 같은지, 각 수신자의 required/optional 전부에 실제 생산 분기와 단언이 있는지 비교한다. 필드명 합집합의 성공을 중첩 값·의미나 실제 ModelRunner 저장 연결 성공으로 바꾸지 않는다. helper 직접 호출, runner가 저장한 request, 실제 worker 수신 검증을 구별한다. 007의 성공/결박/불완전/정지8표본은 실행 결과 가족의 근거로 유지하며 요청의 모든 분기를 대신하지 않는다.

각 행에는 실제 정의/소비 위치·입력축·정확 시험 ID와 단언·원보고 판본·판정 근거를 둔다. 판정은 기존 근거 유지, 최종 판본 실행 대기, 확인된 수리, 정확 미결을 구별한다. 표의 존재/형식 통과나 test name을 의미 충족으로 세지 않는다. 읽기만으로 충분한 질문과 실제 연결 실행이 남은 질문을 구별한다.

### A3 관련 과거 변경과 최소 후속 처분

PR18의 계약 쌍 slice와 current_work.provider_population_integration(B49/065a323a), 006/007 검수 처분을 읽는다. 현재 요청 조립/수신/직접 시험에 실제로 닿는 도입 hunk와 존재 원보고만 대조한다. B70~B73의 별도 평가자 전수나 PR15/PR18 전체는 확장하지 않는다. 예전 Codex only=True 누락 주장은 현 pair에서 해소됐으므로 되살리지 않는다. 요청 분기별 기존 검사와 원보고가 충분하면 최종 판본 실행 대기로 판정하고, 누락이면 최소 입력·기대/현재·정확 후속 시험/수리 파일을 지정한다.

해당 요구에 직접 연결된 보존 K/P2 ID는 requirements-index와 원문 연결을 따라 판정표에 기록한다. 관련 없는 61/12 전수 감사로 확장하지 않는다. 없는 역사 raw는 실제 부재로 남기며 counts를 성공으로 합산하지 않는다. conclusion.md에 닫힌 질문·확인된 공백·후속 구현/검증의 정확 파일·입력·기대결과를 적는다. 결함이 없어도 읽기판정이 완료되면 complete이며, 제품 전체 합격을 뜻하지 않는다.

### A4 무변경과 인계

writes=[]이므로 제품·시험·미러·공용 문서·다른 task·engine·graphify·Git index를 수정하지 않는다. 자기 task/evidence와 report.json만 쓴다. 끝날 때 baseline 대비 소스 변경이 없음을 확인한다. 새 공식 run_tests/pytest/unittest, 실제 모델/Job/Lean/예약/네트워크 호출은 하지 않는다. 정적 파싱·해시·기존 원자료 대조가 기본이며, 추가 순수 계산은 질문 해결에 꼭 필요하고 제품 부수효과나 공유 캐시가 없을 때만 사용한다. 관찰을 새 통합 실행으로 보고하지 않는다.

런타임·검사 수리가 필요하면 최소 입력, 계약상 기대/현재 결과, 정확 파일·심볼·단언과 다음 담당을 보고한다. manager가 구현·미러·관련 검증을 한 task로 배정한다. 다른 독립 task의 결과를 기다리거나 읽지 않는다. L01 Q1/Q2·UTF-8 byte 미충족, Windows1314 symlink 실반려 미검사, G4~G8과 다른 미결 질문을 유지한다. 이번 complete는 이 종료 질문의 판단 완료이며 전체 제품 합격이 아니다.

## 결과 제출

C:/math/.async/dm/tasks/r02/report.json에 async protocol 형식으로 status, summary, changes=[], verification, findings(문자열 목록)를 작성한다. summary에는 닫힌 질문과 남은 수리/최종 실행을 구별하고 verification에는 실제 읽은 정의·단언·원자료와 새 실행 유무·한계를 적는다. 각 finding 문자열은 근거·영향 G/원문 ID·다음 행동을 포함하며 상세 표와 conclusion.md를 자기 evidence에서 가리킨다. 과거 acceptance/checks 구조를 새 보고 필드로 복사하지 않는다.

마지막에 `python C:/math/services/async-development/check.py report C:/math/.async/dm r02`를 실행해 PASS를 확인한다. Git 과거 조회는 `git -C C:/math`로 읽기만 하며 workspace를 Git repo로 가정하지 않는다. commit은 manager 책임이다.
