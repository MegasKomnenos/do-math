## 목적과 역할

R07 스키마·상수 반환 소유권의 남은 모집단 대응를 자기 workspace의 이관 검수판에서 판정한다. 원래1-E와 tracking-state R07의 남은 질문인 현재 선언 모집단과 원문 전체의 대응만 판정한다. 이미 승인된 B22 및 G4/G5 반환소유권, named/unnamed builder·클래스4메서드·상수6개 성질을 재구현하거나 처음부터 전수 재감사하지 않는다. 현재 test_schema_builders의 _calls/_composition_calls/_constant_object_calls, TRANSFORMERS, DELEGATED_SCHEMA_METHODS와 실제 반환 경로를 기준으로 명시적인 미종결 경계만 닫는다.

이 작업은 유한한 남김의 판단 자료를 만드는 work다. G1/G2/G3의 지정 질문을 닫거나 정확 수리로 바꾸며 최종 review가 아니다. 다른 async task 결과를 기다리거나 소비하지 않는다.

## 입력과 실행 위치

SESSION_JSON의 workspace에서 현재 코드와 시험을 읽는다. inputs/context.md·plan.md·seams.md, objective.md·task.json이 이번 배정의 정본이다. C:/math 공용소스와 다른 task 기록은 읽기 전용이다. inputs의 스킬 상대 경로는 workspace 기준이며 절대 경로는 원자료다. 과거 문서 안 `run:`은 C:/math/docs/do-math/continuous-development-2026-10-13, `repo:docs/`는 C:/math/docs/를 뜻한다. 과거 `repo:.claude/` 코드는 현재 workspace에서 확인한다. 기존030 objective는 질문의 출처이며 그 phase/cwd/report/공용쓰기 절차는 사용하지 않는다.

## 완료 조건

### A1 현재판과 필요한 원문만 고정

baseline.json과 inputs를 사용해 자기 시작판을 고정한다. managers/0001/source-inspected.json의2675 스킬 파일과 자기 baseline의 해당 경로를 대조하고 실제 차이를 기록한다. root 지침6파일과 과거 docs의 snapshot 부재는 제품 결함이 아니다. 해당 requirement-state/tracking-state ID와 원문·설계, 직접 연결 K/P2만 읽는다. 103행 전체 재분류나 기존 충분한 후보의 전수 재감사를 반복하지 않는다. 사용한 정의·단언·원보고 판본과 소스 해시를 evidence에 남긴다.

### A2 남은 모집단과 실제 단언 대응

ownership-map.json에서 기존 선언과 원문이 요구하는 owned builder의 현재 집합을 대응시킨다. 함수명 schema 검색 밖의 반환 builder를 기존 G4/G5 후보·상수소유자 목록에서 따라가고, 그 검토 후 해당 파일의 실제 diff에 새 후보가 생겼는지 확인한다. public builder, caller 입력을 빌리는 transformer, 내부 lookup의 소유 계약을 구별한다. repetition_outcome/recovery_outcome의 읽기 전용 borrowed row를 새 copy 요구로 바꾸지 않는다. 최종 _response_schema 등의 조립 뒤 결과가 전역·다른 반환값과 가변 노드를 공유하는지에 대한 기존 독립 단언과 위임 경로를 연결한다. 유한 인자 변형에서 역할·stage·preparation·review_cycle·filtering에 따라 shape가 바뀌는 축이 현재 선언에 포함되는지 판정한다. 이름 기반 등록이 전체 모집단을 보증한다고 주장하지 않는다.

각 행에는 실제 정의/소비 위치·입력축·정확 시험 ID와 단언·원보고 판본·판정 근거를 둔다. 판정은 기존 근거 유지, 최종 판본 실행 대기, 확인된 수리, 정확 미결을 구별한다. 표의 존재/형식 통과나 test name을 의미 충족으로 세지 않는다. 읽기만으로 충분한 질문과 실제 연결 실행이 남은 질문을 구별한다.

### A3 관련 과거 변경과 최소 후속 처분

PR06 중 B22 schema_isolation_integration와 current_work.builder_population_and_windowless_boundary의 schema_registration 및 그 근거 return_ownership_review(G4/G5)를 JSON 키 선택으로 찾아 읽는다. 그 검토·등록 이후의 실제 관련 diff와 기존 원보고 SHA/testID를 대조한다. PR06의 저장/null/형식 동등성이나 windowless 실호출은 이 task의 재감사 범위가 아니다. 이미 판정된 후보는 같은 코드/소유 계약이면 재사용하고, 새 누락만 정확한 함수/인자/공유노드 반례와 수리 경로로 반환한다.

해당 요구에 직접 연결된 보존 K/P2 ID는 requirements-index와 원문 연결을 따라 판정표에 기록한다. 관련 없는 61/12 전수 감사로 확장하지 않는다. 없는 역사 raw는 실제 부재로 남기며 counts를 성공으로 합산하지 않는다. conclusion.md에 닫힌 질문·확인된 공백·후속 구현/검증의 정확 파일·입력·기대결과를 적는다. 결함이 없어도 읽기판정이 완료되면 complete이며, 제품 전체 합격을 뜻하지 않는다.

### A4 무변경과 인계

writes=[]이므로 제품·시험·미러·공용 문서·다른 task·engine·graphify·Git index를 수정하지 않는다. 자기 task/evidence와 report.json만 쓴다. 끝날 때 baseline 대비 소스 변경이 없음을 확인한다. 새 공식 run_tests/pytest/unittest, 실제 모델/Job/Lean/예약/네트워크 호출은 하지 않는다. 정적 파싱·해시·기존 원자료 대조가 기본이며, 추가 순수 계산은 질문 해결에 꼭 필요하고 제품 부수효과나 공유 캐시가 없을 때만 사용한다. 관찰을 새 통합 실행으로 보고하지 않는다.

런타임·검사 수리가 필요하면 최소 입력, 계약상 기대/현재 결과, 정확 파일·심볼·단언과 다음 담당을 보고한다. manager가 구현·미러·관련 검증을 한 task로 배정한다. 다른 독립 task의 결과를 기다리거나 읽지 않는다. L01 Q1/Q2·UTF-8 byte 미충족, Windows1314 symlink 실반려 미검사, G4~G8과 다른 미결 질문을 유지한다. 이번 complete는 이 종료 질문의 판단 완료이며 전체 제품 합격이 아니다.

## 결과 제출

C:/math/.async/dm/tasks/r07/report.json에 async protocol 형식으로 status, summary, changes=[], verification, findings(문자열 목록)를 작성한다. summary에는 닫힌 질문과 남은 수리/최종 실행을 구별하고 verification에는 실제 읽은 정의·단언·원자료와 새 실행 유무·한계를 적는다. 각 finding 문자열은 근거·영향 G/원문 ID·다음 행동을 포함하며 상세 표와 conclusion.md를 자기 evidence에서 가리킨다. 과거 acceptance/checks 구조를 새 보고 필드로 복사하지 않는다.

마지막에 `python C:/math/services/async-development/check.py report C:/math/.async/dm r07`를 실행해 PASS를 확인한다. Git 과거 조회는 `git -C C:/math`로 읽기만 하며 workspace를 Git repo로 가정하지 않는다. commit은 manager 책임이다.
