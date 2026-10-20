# 게시·지식·검토의 실제 미도달 수리와 직접 확인

사용자 목표는 실제 제품 경로의 결과를 확인하는 시험으로 결함의 누락을 막는 것이다. g5-full의 전체 fresh T3는 4287passed/Windows1314 조건부skip1이지만 미도달 때문에 G5가 미충족이다. 이 task는 gap-scope.json의 9모듈58arc/50행을 현행 계약으로 판정하고 필요한 제품·시험 수리, 최소 확인, 관련 설명과 공식 미러를 함께 마친다. 관측 좌표가 곧 제품 결함이나 도달 가능성의 판정은 아니다.

## 입력과 소유

SESSION_JSON, task.json, inputs/context.md·plan.md·seams.md, 자기 workspace의 do-math AGENTS.md와 scripts/tests/시험-지침.md를 읽는다. managers/0070/review.md·assignment-scope.json, g5-full의 report.json·evidence/judgment.md·full1/report.json·coverage.json·gap-inventory.json을 필요한 범위에서 소비한다. 원 선택 색인은 g5-full/evidence/observed-caches/.claude/skills/do-math/scripts/tests/.selection-index.json에 보존돼 있다. base로 복원된 workspace cache를 원측정 자료로 쓰지 않는다.

제품 소유는 do_math/delegations.py·external_engine.py·integration.py·knowledge.py·knowledge_records.py·retention.py·review_cycle.py·review_engine.py·submission.py다. 이 9파일은 원측정 SHA와 현재 공용판이 같다. 관련 직접시험/helper·scripts/이음새-정본.md와 대응 미러의 정확한 쓰기 상한은 task.json과 gap-scope.json이다. 상한은 전수 수정·실행 quota가 아니다.

실제 선행은 미도달 원측정 g5-full뿐이다. 시작판에는 수용된 g5-core 수리도 반영되지만 이번 독립 9모듈의 선행 요구는 아니다. g5-inputs와 g5-worker의 정의·사본·진행 중 결과를 바꾸거나 소비하지 않는다. 특히 g5-inputs가 맡은 unit/test_review_wait_contract.py와 governance/planning 직접시험·공유helper는 읽기 전용이다. 위임의 정확 반려처럼 적절한 기존 시험 자리가 running 소유이면 허용한 unit/test_publication_branch_contracts.py 및 필요시 support/publication_branches.py에서 현재 제공자를 직접 소비한다. 불필요한 새 framework는 만들지 않는다. core_engine·record_schemas·lifecycle_engine의 남은 165arc/197행은 이 배정에 포함하지 않는다. 배정 밖 제공자 수정이 필수이면 파일·caller·원반례·필요 변경을 보고한다.

## 맡은 결과

- delegations의 보존된 승인/현재 case 결속, external_engine의 정비·정산 중 게시 반환을 실제 caller와 대조한다.
- integration의 impact 대상·member 좌표·기존 mutation root, 검토 범위 합집합·봉인된 지정 입력·단일 응답, bundle 신원·참조·이전 hash 반려를 다룬다.
- knowledge/knowledge_records의 영향 반영과 검토 재평가 정책·저자 제외, 채택된 검토 정책 전제를 확인한다.
- retention의 workspace/runs 경로·참조 집합·정리 순회, review_cycle의 기록된 대체 권한, review_engine의 초기화 재시도·source 물리 경계·activity 소유·고정 source 읽기 실패를 다룬다.
- submission의 봉인 bytes/check_ref·부분후보 검증, import/task 처분·checkpoint 참조·기계검사 보존 실패를 원좌표와 연결한다.

각 좌표의 함수·caller·입력 불변식과 기존 단언을 읽고, 불필요한 중복 방어·죽은 계약을 제거/축소할 수 있는지 먼저 판단한다. 실제 입력의 형식·참조·권한·현재성·원내용 보존·종료 장벽은 유지한다. 필요한 도달 공백은 가장 싼 기존 시험에 정확한 결과/반려/상태/bytes 단언을 보완하며 관련 결함을 같은 task에서 고친다. 호출만 하는 시험, 제품 함수를 패치하는 시험, 다른 반려를 통과로 세는 포괄 예외 포착, 구판 fixture를 살리는 fallback은 해결책이 아니다. 외부 포트/OS 경계 대역과 제품의 실제 판단을 구분한다.

의도적 미도달에는 원설계5.5와 해당 행의 현재 caller·지원계약에 근거한 구체 사유가 필요하다. 불필요한 코드는 제거를 우선 검토한다. blanket no-cover·새skip·층/분모/임계값 완화, 별도 child/T4 결과를 T3 도달로 수동 합치는 방식은 쓰지 않는다. 환경 조건이 필요한 항목은 구체 좌표·조건을 남기고 같은 권한probe를 반복하지 않는다.

sources/storage-scope-direction-2026-10-15.md와 원설계3.3/A22를 적용한다. 저장 검증 상시화·공통 구조 검사·T3 쓰기 도달의 역할을 유지하고 공통codec/기존 업무 단언을 재사용한다. 전가족·전생산자·전필드·새reader·옛head 일괄 재입증이나 별도 장기감사를 추가하지 않는다.

## 최소 확인과 자원

시험슬롯1개, 기본 --jobs 1, 한 공식 명령씩이다. 다른 두 task와 총시험worker3 이하를 유지한다. 자기 scripts/run_tests.py의 가장 작은 관련 선택으로 실제 남은 불확실성만 확인한다. 필요하면 그 선택의 --tier T3 원coverage로 해당 좌표의 도달을 확인한다. 부분선택의 전체분모 gap/exit1을 실제 시험 실패와 구별하고, 같은 동작을 일반/T3로 불필요하게 반복하지 않는다. 정적 판단으로 충분하면 실행하지 않는다. 실행 중 소스는 고정한다. 소프트 시간 초과는 기록하되 시간만으로 중단·skip·실패로 세지 않는다.

전체G4/T3·전체변이·T4/T5·유료호출·실예약·설치/호스트권한 변경·내부 다중worker meta는 이번 배정 밖이다. 모든 동료의 종료를 기다리는 장벽은 없다.

T3 도구가 실제 Git root를 필요로 할 때만 자기 workspace에 독립 .git/실제 소스의 로컬 기준commit을 준비할 수 있다. g5-full/evidence/prepare.py를 자기 경로에 맞춰 쓰며 준비 전후 bytes와 실제 root/HEAD를 남긴다. 공용 Git·다른 .git 복사·가짜HEAD·global설정·remote/push는 사용하지 않는다. 기존 GIT_CEILING_DIRECTORIES를 보존하고 자기 task 부모/저장소 밖 짧은 고유 temp root를 추가한다. 로컬 HEAD는 공용main/성공 인증이 아니다.

command/cwd/관측exit·원report/stdout/stderr·선택/고유실제행/fixture·판본SHA/실행중변경을 보존한다. coverage를 썼으면 원/현재 좌표와 도달/남김을 연결한다. 여러 판본의 결과를 전체 성공으로 합산하지 않는다. 생성 index/timing/store는 원자료 보존 뒤 base의 bytes/부재로 복원한다.

## 제출

evidence/judgment.md와 report.json에 수리·불필요 분기 제거·정당한 제외·미검증 남김, 재사용 근거와 실제 확인 한계를 기록한다. 같은 원인의 좌표는 묶어 판단한다. 배정의 실제 남김이 있으면 partial/blocked로 사실대로 보고하고 이 task 완료를 전체 G5 충족으로 세지 않는다.

허용 정본과 관련 설명을 함께 수정하고 공식 build_skill_mirrors.py로 대응 미러를 생성/check한다. 공용 설명에 필요한 계약을 정확한 파일·심볼로 report에 남긴다. 제품 변경은 자기 workspace에 한정한다. 공용 context/plan/seams/queue/state·engine·다른 task/스킬·기존 연구·graphify는 수정하지 않는다. python C:/math/services/async-development/check.py report C:/math/.async/dm g5-publish를 통과시킨다. 최종 통합판 G4/G5·G6~G8·실경계/환경 조건은 별도다.
