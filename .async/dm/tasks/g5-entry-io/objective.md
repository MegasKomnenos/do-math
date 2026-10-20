# 직접 실행 입구·frozen manifest·I/O 환경의 남은 계약

사용자 목표는 실제 제품 경로의 결과를 확인해 결함이 시험을 빠져나가는 기제를 막는 것이다. g5-worker의 script/import/frozen 남김13arc/25행과 g5-io의 환경 남김6arc/10행을 하나의 한정 작업으로 처리한다. 원좌표19arc/35행은 과거 관측의 출발점이며 제품 결함이나 도달 가능성을 미리 판정한 목록이 아니다. 관련 구현·최소 확인·설명·공식 미러를 함께 마친다.

## 입력과 소유

SESSION_JSON, task.json, inputs/context.md·plan.md·seams.md, 자기 workspace의 do-math AGENTS.md와 scripts/tests/시험-지침.md를 읽는다. gap-scope.json에 원좌표/현재좌표/수용판 SHA와 원결과를 연결했다. g5-worker와 g5-io의 report.json·evidence/judgment.md·gap-disposition.json, managers/0075/review.md와 assignment-scope.json, 원설계3.3/A22·5.5 및 사용자 저장범위 지시를 필요한 부분만 읽는다. C:/math/docs와 records의 추가 자료는 공용 원자료이므로 읽기 전용이며 상대 제품 경로는 자기 workspace다.

실제 선행은 g5-worker·g5-io다. 시작 시 다른 작업이 진행 중이어도 자기 base의 수용판만 사용한다. g5-trust의 formal/setup_lean/knowledge·공용 이음새 문서, g5-core-rest의 core/external/integration/retention/submission과 관련 시험/helper는 읽기 전용이다. task.json의 writes는 허용 상한이며 전수 수정·실행 quota가 아니다. 제공자 수정이 필요하면 정확한 반례와 파일·심볼을 보고한다.

## 맡은 결과와 판단 순서

1. claude_worker/codex_worker의 direct Python Job root, control_server의 직접 import/main/submit_draft와 control_transport의 bare import를 실제 생산 명령(codex_adapter worker argv, mcp_server_config)과 대조한다. 이미 package import로 확인된 함수와 실제 새 Python 인터프리터에서만 성립하는 입구를 구분한다. 기존 boundary/test_provider_worker_roots·test_provider_control_server·test_engine_control_transport·test_submission_mcp_server의 필요한 사례를 재사용한다. 인자 없는 usage 성공만으로 REQUEST.json 처리나 submit_draft 결과를 확인했다고 하지 않는다. 입력을 처리하는 새 사례가 필요하면 유료 공급자를 호출하지 않는 기존 외부 CLI 경계와 실제 제품 판단을 연결한다.
2. operator_bootstrap의 독립 script dispatch/main, probe_cli의 직접 main 및 scheduled_operator.run_engine의 SKILL_ROOT 옆 manifest 자동 선택을 다룬다. 기존 freeze/실제 설치 복사와 짧은 child를 재사용해 frozen manifest 경로가 실제 선택되고 올바른 설치·manifest가 다음 실행 요청에 결속되는지 확인한다. 다른 manifest 반려·live 설치 손상·--help는 이 성공 조건을 대신하지 않는다. 새 인프로세스 frozen 장면으로 충분한 부분과 child가 필요한 startup 부분을 나누고 같은 동작을 두 층에서 반복하지 않는다.
3. context_store.collect_outputs의 파일 reparse/symlink omission, file_io._replace_once·shared_reader·os_lock·PhysicalBoundary.check의 비Windows 경로는 현재 지원 계약·호출자·실환경을 먼저 확인한다. 이 호스트에서는 이전 파일 symlink 생성이 WinError1314였으며 junction 시험은 파일 symlink와 다르다. 같은 권한 probe를 반복해서 성공을 기대하지 않는다. 이미 사용할 수 있는 적합한 로컬 환경이 있다면 그 실제 조건에서 작은 호출로 확인할 수 있다. 플랫폼 이름이나 제품 내부 판단을 패치해 실제 OS 도달이라고 쓰지 않는다. 지원계약의 명시 근거 없이 다른 플랫폼 동작을 삭제하거나 Windows만 지원한다고 새로 정하지 않는다. 제거할 불필요 전제가 확인되면 그 이유와 현재 소비자를 함께 수정한다. 필요한 환경이 없으면 정확한 남김·영향·필요 조건을 보고한다.
4. 제품·시험·CLI 설명은 실제 판단에 맞춘다. 불필요한 중복 방어/입구를 줄일 수 있는지 먼저 검토하되 공개 입력·참조·권한·원내용·현재성·정산/물리경계 검사는 유지한다. 원설계5.5가 인정하는 의도적 미도달은 구체적인 현재 호출 계약과 같은 행의 사유를 근거로만 제외할 수 있다. 단순히 이번 호스트에서 실행되지 않았다는 이유로 제외하지 않는다. 원래 1~3층의 해석 로직을 boundary로 옮겨 분모를 줄이거나 모듈 전체를 제외하지 않는다. 새 skip·무근거 no-cover·층/분모/임계값 완화는 허용하지 않는다.

T4 child의 결과와 분기 측정은 경계의 독립 증거다. T3 parent coverage에 수동 합치거나 최종 G5 gate/index를 보정하지 않는다. 현재 공식 T4가 제공하는 보고 방식을 사용하고 측정하지 못한 범위를 표시한다. 이 작은 경계 작업을 새 자식coverage 수집 프레임워크나 모든 G7의 선행조건으로 확대하지 않는다.

## 최소 확인·자원·외부 경계

시험슬롯1개, --jobs 1, 공식명령 한 번씩이며 다른 두 task와 총시험worker3 이하를 유지한다. 실제 남은 불확실성에 맞는 가장 작은 공식 선택을 실행한다. 정적 근거로 충분하면 실행하지 않는다. 필요한 T3 선택과 지정된 로컬 T4 subprocess/파일/잠금/loopback 경계 실행을 허용한다. 부모/자식의 실제 정체성·종료·출력/반려와 원bytes를 필요한 만큼만 단언하며 기존 준비물과 업무 성질을 재사용한다.

이 배정은 유료 모델 호출·전체T4/T5·실예약 등록/발화·도구 설치/갱신·호스트 정책/권한 변경·새 WSL/VM/원격 환경 준비를 포함하지 않는다. 실 child는 자기 임시 자료와 자기 소유 프로세스만 사용하며 창을 띄우지 않고 정상 정산한다. 전체G4/fresh전체T3·전체변이·내부 다중worker meta도 배정 밖이다. 모든 동료의 종료 장벽은 없다. 필요한 실환경을 사용할 수 없으면 그 부분을 남기되 독립적으로 가능한 판단·수리·확인은 완료한다.

T3의 실제 Git root가 필요할 때 자기 workspace의 독립 .git/실제 소스 기준 로컬commit만 허용한다. g5-full/evidence/prepare.py의 준비를 자기 경로에 맞추고 시작/준비 뒤 bytes와 실제 root/HEAD를 남긴다. 공용 Git·다른 .git 복사·가짜HEAD·global설정·remote/push는 사용하지 않는다. 기존 GIT_CEILING_DIRECTORIES를 보존하고 자기 부모와 저장소 밖 짧은 고유 temp root를 추가한다. 자기 HEAD는 공용 main/성공 인증이 아니다.

원 command/cwd/관측exit·stdout/stderr/report/coverage·선택/고유실제행/fixture·판본SHA/실행중변경을 보존한다. 소프트 비용은 기록하되 경과 시간만으로 실패·중단·skip·변이포착으로 세지 않는다. 실행 중 소스를 고정하고 생성cache/index/store는 원bytes를 보존한 뒤 자기 base의 bytes/부재로 복원한다. 서로 다른 부분 선택/판본은 단일 전체 성공이 아니다.

## 제출

evidence/judgment.md와 report.json에 실제 동작의 변화, 제거/유지/제외의 근거, 원/현재좌표 도달·제거·정당한 제외·남김, 실제 환경·확인 범위·한계를 적는다. 3.3/A22와 저장범위 지시에 따라 공통codec/저장검증·기존 업무 보장을 재사용하며 전가족/전필드/새reader/옛head quota·장기감사는 추가하지 않는다. 미완료는 partial/blocked로 정확히 보고한다. 이 배정의 결과는 최종수용판 G4/G5·G6~G8과 G7의 공급자/Lean/예약/학술 전체 성공을 뜻하지 않는다.

필요한 설명은 허용된 README.md·references/CLI-실행-계약.md와 해당 docstring에 묶는다. 공식 build_skill_mirrors.py를 자기 workspace에서 실행하고 대응 미러/check를 확인한다. 다른 task의 문서는 수정하지 않는다. 공용 source/records 문서/queue/state·engine·기존 연구·graphify는 수정하지 않는다. python C:/math/services/async-development/check.py report C:/math/.async/dm g5-entry-io를 통과시킨다.
