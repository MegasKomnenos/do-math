# core의 남은 입력·권한·게시·복구 계약을 마친다

g5-core-gaps의 부분 결과를 manager0082에서 통합·수용했다. 영향 검토 assignment 계산과 수용 후 cleanup의 Git CAS 실패 수리는 완료됐고, overflow 중복 검사는 실제 활동·질문 전이로 줄였다. 이 작업은 남은 core_engine 58arc/63행의 현재 계약 판단·필요한 구현·최소 확인·설명·공식 미러를 함께 맡는다. 좌표는 과거 전체 T3에서 시작한 유한 조사 범위이며 각각을 별도 시험으로 채우라는 quota가 아니다. 이전 작업자의 제안 시나리오는 확정 요구가 아니다.

## 입력과 소유

SESSION_JSON, task.json, inputs/context.md·plan.md·seams.md, 자기 workspace의 do-math AGENTS.md와 시험-지침.md를 읽는다. 추가 절대경로는 읽기 전용 원자료다. managers/0082/review.md·verification-review.json·handoff-delta.json, g5-core-gaps/report.json·evidence/judgment.md·remaining-functions.md·scope-coordinates.json, 자기 gap-scope.json을 소비한다. gap-scope의 accepted_source_sha256/current는 수용판이고 original은 과거 g5-full 좌표다. 재현 준비가 필요하면 g5-core-gaps/evidence/prepare.py와 run.py의 절차를 자기 경로에 적용한다.

실제 선행은 g5-core-gaps뿐이다. g7-scheduler의 helper·smoke·시험지침과 g23-handoff의 기록은 독립 소유이며 미완성 결과를 소비하지 않는다. 제품 쓰기는 task.json에 열거한 core_engine·직접 integration/submission 경계·관련 시험/helper·두 설명과 대응 미러다. integration의 이전 안정화 오류는 이번 남김이 아니다. 새로 확인한 core 소비 계약을 수리하는 데 직접 필요한 경우에만 건드린다. 제공자 activities/questions/review/governance/retention 등은 시작판을 읽는다. 범위 밖 제공자 수리가 필요하면 정확한 원인·영향·최소 수정 범위를 보고한다. 허용 경로 목록은 변경·시험 의무가 아니다.

## 해결할 결과와 순서

1. 현재 입장·저장·불변 영수증·소유자 전이로 이미 보장되는 전제부터 확인한다. preserved user request/operational target/action 부재, response lineage 상충, fixed planning population, 정확 lock 아래 link race, 닫힌 role dispatch 등은 실제 생산/소비를 짧게 따라가 불필요한 방어를 줄일 수 있는지 판단한다. 충분한 기존 보장은 정적 근거로 재사용한다. 도달 수를 위해 불가능한 내부 상태를 조립하거나 외부 파일/Git/종료 관찰 오류를 불변식으로 지우지 않는다.
2. 위임·복구에서는 두 독립 판단 뒤 현재 권한 변화, 고정 요청의 출처/정확 대상, 재평가 upkeep, 이미 게시된 goal judgment의 다른 wait 복원, native capture/재접수의 원결과와 owner, 운영 처분의 superseded·checkpoint·과제/assessment·user decision과 로컬 종료를 관련 기존 소비 경로에서 판단한다. 같은 원인과 helper를 쓰는 수리·확인은 묶는다.
3. 제출·영향·준비에서는 source/academic/추가 authority의 실제 현재성, mixed impact 결과·관계없는 pending action 보존, 영향 계획 없는 mutation, private insight의 원입력/출처, preparation revision·formal environment·condition 이름/평가/순환과 종류 후속을 판단한다. role 입력/봉인/검증저장 뒤의 내부 조건과 실제 공개 입력 거절을 구별한다. 서로 다른 assignment의 순수 domain 회귀를 공개 owner 전체 흐름 인증으로 확대하지 않는다.
4. 외부 오류에서는 receipt 게시 후 head 전진·reload 실패, native CAS/전제 복원, 수용 후 operational repair/정산 실패, 파일 listing/inbox 삭제 경쟁, 관찰 게시와 self-check 전달 사이 종료를 현재 외부 포트에서 판단한다. 반려·원결과/영수증·owner·무중복·실제 로컬 효과 중 해당 불확실성에 필요한 값만 확인한다. 이미 수리한 cleanup archive/final CAS 두 위치·실제 삭제 보존, closed source 보존, overflow 공개 retry, nested condition 이름 결박은 새 관련 변경 없으면 다시 실행하지 않는다.
5. 새 결함이 있으면 관련 구현·직접 확인·설명/미러를 이 task에서 마친다. 배정 전부를 해소하지 못하면 원/현재 좌표·현재 의미·왜 필요한지·최소 다음 조건을 남긴다. 의도적 제외는 원설계5.5의 같은 행 사유와 실제 caller/불변식으로 판단하며 자동제외·blanket no-cover·새 skip·층/분모/임계값 완화는 하지 않는다. 표의 숫자만 줄이는 것이 완료가 아니다.

## 최소 확인과 자원

사용자 storage-scope-direction-2026-10-15.md와 원설계3.3/A22를 적용한다. 공통 codec·검증저장·기존 업무 보장을 재사용하며 전가족/전필드/새 reader/옛 head quota·새 검증 framework·장기감사를 추가하지 않는다. 확인마다 이번 변경으로 남은 불확실성을 기준으로 가장 작은 선택을 사용한다. 충분하면 끝내며 성공한 성질을 되풀이하지 않는다.

시험슬롯1, 공식 scripts/run_tests.py --jobs 1, 한 번에 한 명령이다. 진행 중 예약1과 합계2슬롯이며 다른 읽기 작업은0이다. 도달이 실제 질문이면 그 최소 선택의 --tier T3 원coverage를 확보하고 일반/T3를 중복하지 않는다. 전체 G4/fresh 전체T3·전체변이·병렬자식 meta검사·T4/T5·유료호출·실예약/도구설치 변경은 범위 밖이다. 제품 함수 대역은 쓰지 않고 필요한 외부 오류는 실제 외부 포트에서 제어한다. 시간 초과 자체를 실패/skip/변이포착으로 세지 않는다.

측정에 Git root가 필요할 때만 자기 workspace의 독립 .git과 실제 시작 bytes 기준commit을 준비할 수 있다. 전후 bytes·root/HEAD를 기록하고 공용 Git/index/commit·다른 .git 복사·가짜HEAD·global 설정·remote/push는 하지 않는다. 기존 GIT_CEILING_DIRECTORIES를 유지하고 자기 task 부모와 저장소 밖 짧은 전용 임시root만 더한다. command/cwd·관측exit·원report/stdout/stderr/coverage·선택/실제행·fixture·소스판본/실행중변경을 보존한다. T3 store/index/timing은 필요한 원자료를 보존한 뒤 시작 bytes/부재로 복원한다. 부분 gate=false/exit1과 실제 시험 실패를 구별하고 서로 다른 부분판을 전체성공으로 합산하지 않는다.

## 제출

evidence/judgment.md와 report.json에 수리·줄인 전제·재사용 근거·직접 확인과 한계·남김을 적는다. complete는 배정된 유한 질문의 해결이며 단순 미완료는 partial이다. 외부 입력이 필요하지 않은 미완료를 blocked로 부르지 않는다. 공식 build_skill_mirrors.py로 해당 정본의 미러를 생성/check하고, python C:/math/services/async-development/check.py report C:/math/.async/dm g5-core-tail을 통과시킨다. 공용 문서/queue/state·다른 task·engine·graphify는 수정하지 않는다. 최종 G4/G5·G6~G8·G1~G3, 환경6arc/10행·L01/실경계는 전체 계획에 남는다.
