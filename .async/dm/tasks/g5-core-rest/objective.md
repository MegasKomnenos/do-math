# core의 남은 수신·게시 조건과 작은 게시 보완을 마무리한다

g5-calls에서 호출 준비/수신의 원5arc를 정리했고 core의 유효한 부분 수리를 수용했다. 이 작업은 core_engine의 남은91arc/124행과 g5-publish의 external_engine/integration/retention/submission5arc/2행, 총96arc/126행을 현재 계약으로 판정하고 필요한 구현·직접시험·설명·공식미러를 함께 끝낸다. 이는 원 측정에서 남은 좌표이며 제품 결함/도달가능성을 미리 확정한 목록이나 새로운 전수 저장시험 의무가 아니다.

## 입력과 범위

SESSION_JSON, task.json, inputs/context.md·plan.md·seams.md, workspace의 do-math AGENTS.md·scripts/tests/시험-지침.md를 읽는다. 추가 절대경로는 공용 원자료를 읽기 전용으로 소비하는 참조다. managers/0074/review.md·verification-review.json·assignment-scope.json, 자기 gap-scope.json, g5-calls의 report·evidence/judgment.md·remaining-functions.md·scope-coordinates.json, g5-publish의 report·evidence/remaining-scope.json을 필요한 범위에서 읽는다. gap-scope는 수용판 SHA와 원/현재 좌표의 연결이며 새 계약이 아니다.

제품 쓰기는 core_engine.py·external_engine.py·integration.py·retention.py·submission.py와 task.json의 직접 시험/helper·관련 설명·미러에 한정한다. call_engine의 정리된5arc는 재배정하지 않는다. 진행 중 g5-state의 dispatch/engine/lifecycle/repository/repair/state_checks/record_schemas/__init__, g5-trust의 formal/knowledge/review/schema 및 공용 제품 이음새 정본은 읽기 전용이다. 제공자 수정이 실제로 필요하면 정확한 원인/필요 변경을 보고한다. 다른 작업 사본을 소비하거나 수정하지 않는다. 쓰기상한은 전수수정/전수실행 quota가 아니다.

사용자 저장범위 지시 sources/storage-scope-direction-2026-10-15.md와 원설계3.3/A22·5.5 및 시간 정정을 적용한다. 기존 공통codec/저장검증/업무 단언을 재사용한다. 전가족·전필드·새reader·옛head 재입증, 새 registry/검증 framework/장기감사를 만들지 않는다. 과거 전체T3는 g5-full/evidence/full1이고 보존 index는 evidence/observed-caches/.claude/skills/do-math/scripts/tests/.selection-index.json이다. 복원된 workspace 캐시를 측정 근거로 쓰지 않는다.

## 맡은 결과

1. core의 잔여 조건은 gap-scope와 remaining-functions의 실제 함수별 목록을 따른다. 제어 재접수/이미 게시된 오류 acknowledgment·source 변경/live 정지, 게시 retry의 정산과 실패, review 복원/위임 권한, bundle currentness/authority, 관찰/checkpoint/feedback, native 복구/입력 overflow, preparation/과제 조건/운영 처분/정비/check가 남아 있다. 현재 caller/입력·저장 경계가 보장하는 중복 방어/죽은 계약은 제거·축소부터 검토한다. 공개 형식·권한·근거·현재성·종료/정산 검증을 약하게 하지 않는다.
2. 작은 게시 보완은 같은 작업에서 마친다. external_engine._external_control의 retry predecessor 부재와 persist의 request_sha256/execution_id 불일치, integration.bundle_impact_request의 exclusion 안정화 실패, retention.retention_inputs의 nameless source alias, submission._payload_issues 안 external_requests의 grant 부재다. 유효한 생산자와 계약상 필요한 경계를 먼저 확인한다. 가능한 입력이면 가장 싼 기존 시험에서 정확 결과/반려·저장/정산을 확인한다. 불가능한 내부상태를 조립해 실행 숫자를 만드는 방법은 쓰지 않는다.
3. g5-calls의 _validate_initial_retry 주석에서 'assigning ... resumes'는 실제 순서를 정확히 써 준다. activities.assign_execution은 waiting을 거절하고, resume_activity가 ready로 되돌린 뒤 assign_execution이 working으로 바꾼다. 관련 references/과제-착수조건.md도 필요한 경우 함께 명확히 한다. 설명만을 위한 별도 task/시험을 만들지 않는다. g5-state가 이미 맡은 test_scheduling_close_parallel의 반려 단언 누락은 중복 수정하지 않는다.
4. 실제 미검증 경계는 입력과 예상 결과를 현재 계약에서 얻어 직접 단언하고 발견한 관련 결함을 같은 작업에서 수리한다. 내부 제품 패치/호출만 하는 시험/빈 단언/이유 없는 예외포착은 쓰지 않는다. 해당 경계가 필요로 하면 외부 포트 실패 대역은 허용한다. 충분한 codec/저장 성질은 반복하지 않는다.
5. 의도적 미도달은 설계5.5와 실제 caller/불변식의 구체 이유로 판정한다. blanket no-cover·새skip·층/분모/임계값 완화로 숨기지 않는다. 자식/T4 도달을 T3에 수동 합치지 않고 함수 진입을 결과 단언으로 대신하지 않는다. 미완료 항목은 정확 좌표/현재 의미/다음 필요한 입력과 함께 남긴다.

## 최소 확인과 자원

시험슬롯1, 공식 scripts/run_tests.py --jobs 1, 한 번에 한 명령만 실행한다. 두 동료와 동시 시험 합계3 이하다. 정적 판단으로 충분하면 실행하지 않는다. 도달 여부가 실제로 불확실한 변경만 가장 작은 선택의 --tier T3로 확인하고 원coverage를 보존한다. 같은 성질을 일반/T3로 중복 실행하거나 이미 충분한 부분을 다시 실행하지 않는다. 한정 수리와 필요한 검증은 이 task에서 함께 마친다.

전체G4/fresh전체T3·전체변이·병렬자식을 만드는 meta 검사·T4/T5·유료호출·실예약/도구설치 변경은 이번 범위가 아니다. 시간은 소프트 기준이며 초과만으로 중단/skip/실패/변이포착으로 판정하지 않는다.

측정에 Git root가 필요할 때만 자기 workspace에 독립 .git/실제소스 기준commit을 준비할 수 있다. g5-full/evidence/prepare.py의 절차를 자기 경로로 적용하고 준비 전후 제품bytes와 자기 root/HEAD를 기록한다. 공용 main/통과 인증이 아니다. 다른 .git 복사·공용Git/index/commit·global 설정·가짜HEAD·remote/push는 금지한다. 기존 GIT_CEILING_DIRECTORIES를 유지하며 자기 task 부모/저장소 밖 짧은 임시root를 추가한다. 외부 권한은 변경하지 않는다.

실행한 확인의 command/cwd·관측exit·원report/stdout/stderr·선택/실제행·fixture·판본SHA·실행중변경을 보존한다. coverage는 해당 bytes와 원/현재 좌표/처분을 연결한다. 서로 다른 부분 판본의 통과를 단일 최종판 전체성공으로 합산하지 않는다. 부분gate=false/exit1과 실제시험 실패를 구별한다. 생성 index/timing/store는 원자료를 보존한 뒤 base 바이트/부재로 복원한다.

## 제출

evidence/judgment.md와 report에 해결한 동작/불확실성, 재사용한 근거, 실제 수리·제거·사유 있는 제외·남김을 설명한다. 남김이 있으면 partial로 사실대로 보고하고 외부 입력 부재가 아닌 단순 미완료를 blocked로 바꾸지 않는다. 제품 설명은 허용 문서에서 구현과 함께 고치며 공용 seams에 필요한 의미는 실제 파일·심볼/입출력·오류와 함께 인계한다.

공식 build_skill_mirrors.py로 정본 대응 미러를 생성/check하고 범위 밖 파일은 제출하지 않는다. 공용 context/plan/seams/queue/state와 engine·다른 task·graphify는 수정하지 않는다. `python C:/math/services/async-development/check.py report C:/math/.async/dm g5-core-rest`를 통과시킨다. 최종수용판 G4/G5·G6~G8·G1~G3 연결과 실제 경계는 남는다.
