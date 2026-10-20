# 현재 판정 근거와 다섯 교란 축의 남은 질문

R44·R45·R46의 5-A 판정 근거를 고정된 현행 사본에서 조사한다. 사용자는 관리 정보 변화 때문에 불필요한 재검토가 열리거나, 실제 내용·모집단·봉인 뒤 전제 변화가 누락되지 않는 결과를 원한다. 이미 수용된 근거와 실제 공백을 구분해 필요한 후속 구현을 바로 맡길 수 있는 결론을 만든다. 제품을 수정하지 않는 kind=work 조사이며 writes=[]다.

SESSION_JSON/task.json과 inputs/context.md·plan.md·seams.md, do-math AGENTS.md·시험-지침.md를 읽는다. 원문은 C:/math/docs/do-math/continuous-development-2026-10-13/sources/user-decisions.md·requirements-index.json, phases/001/tasks/closure-map/evidence/tracking-state.json의 R44/R45/R46와 requirement-state 5-A, 시험-재편-2026-09-29/조사/결함-범주.md의 5-A다. 과거 run:은 continuous-development-2026-10-13 기준, repo:는 자기 workspace 기준이다. 원자료·공용 소스·다른 task는 읽기 전용이다.

## 조사할 유한 모집단

- R44: input_basis.capture_decision_basis/decision_basis_changes 및 planning.task_reference_basis, task_scope.assessment_basis/assessment_current와 실제 호출자. 선언 필드와 관리/내용/모집단/봉인 뒤 시점/동시 검토의 다섯 축이 실제 판정·후속에 연결되는지 판단한다. 제출 내용 인용과 형식 판단 인용, append된 결과와 원 결과 교체·삭제를 구별한다. r31-fix의 input_sources source ID/SHA 전달·저장/restart와 현재 null 의미를 재사용한다.
- R45: lifecycle/core의 _refresh_readiness 개설 기준·진행 중 같은 검토 억제, trust_validation/trust_inventory의 현재 record·baseline 목록·환경 검사를 같은 다섯 축에 연결한다. 역사 manifest/inventory 명칭은 실제 현행 객체로 대응한다. 현재 신뢰 모델을 전 파일 재해시로 확대하거나 대규모 설치를 다시 만들지 않는다.
- R46: task_contracts의 봉인 준비 입력/허용 참조 계산과 submission·core의 실제 편입 수신/전제 변경 처분을 연결한다. 봉인 뒤 새 과제 배제·같은 응답 형제 ID·관리/중복/순서 안정성과 내용/누락 반려, premise change가 producer repair 계수를 쓰지 않는지 확인한다. 이 원문이 요구하는 판정 함수 전건의 잔여 목록도 현재 정의/호출로 닫되, 모든 bool 함수나 제품 전체 감사로 확장하지 않는다. 제외한 함수는 실제 역할상 이유를 남긴다.

단계-전환표의 review_basis_field_integration(B74), completion_review_basis_integration(B75), trust_record_basis_integration(B76), preparation_input_basis_integration(B77)과 현행 소스·직접 시험·원보고를 먼저 읽는다. B74~B77의 이미 충분한 성질과 남긴 시점/동시상태 등 질문을 구별한다. R06/R09/r31-fix/r37 및 r39 수용 결과의 관련 부분을 재사용한다. 원 Temp 보고가 없으면 부재를 기록하고 요약 count를 실제 성공으로 세지 않는다.

## 반환할 결과와 경계

각 판정 함수에 실제 producer/consumer, 선언 근거 필드, 다섯 축의 적용 여부, 정확 시험ID·단언·원보고 판본, 충분한 근거/실제 결함/검사 공백/정당한 비적용을 연결한다. 단순 문자열 검색이나 함수 목록을 의미 충족으로 바꾸지 않는다. API 없는 행위나 옛 호환성 요구를 새 조건으로 만들지 않는다. 충분한 기존 근거는 완료로 판단하고 재검증 일을 만들지 않는다.

실제 결함 또는 필요한 시험 수리가 있으면 가장 작은 입력·기대 계약·현재 관측/정적 근거·수정할 파일/심볼과 직접 소비시험을 함께 제시한다. 공유 owner별로 구현과 필요한 확인을 묶어 다음 task 하나가 끝낼 수 있게 한다. 관리 표 형식 자체를 새 제품 체계로 만들지 않는다. 별도 제품 실행은 기본적으로 필요 없으며 읽기만으로 판단 가능한 곳은 정적 분석으로 끝낸다. 판단에 꼭 필요한 순수 호출은 자기 evidence 임시자료에서 수행하고 범위·판본을 남긴다. 공식 제품 시험·대규모 fixture·외부 호출·도구설치/예약은 이 읽기 배정에서 실행하지 않는다.

R41은 core/planning/task_scope를 수정할 수 있지만 그 종료는 이번 고정 사본 조사의 선행이 아니다. 미완성 R41 또는 r47-r48 사본을 읽거나 배정을 바꾸지 않는다. 읽은 실제 소스 해시와 함수 경계를 남겨 manager가 이후 수용판에서 관련 변경만 재대조할 수 있게 한다. 이 조사로 아직 수행하지 않은 수리나 최종 통합판 실행을 완료로 선언하지 않는다.

report.json과 evidence는 자기 task 디렉터리에만 쓴다. 변경 목록은 []이며 check.py report C:/math/.async/dm r44-r46으로 검사한다. 공용 문서/queue/state·제품/미러·Git index·graphify·기존 연구 운전은 수정하지 않는다. G4~G8·다른 원요구/보존/P2·L01/Windows1314는 별도다.
