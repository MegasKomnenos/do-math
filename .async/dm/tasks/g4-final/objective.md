# 수용된 수리판의 전체 일반 검사와 남은 실제 결함 처리

g4-contracts와 g4-measurement의 수용 결과가 반영된 새 작업 사본에서 G4를 완결한다. 공식 run_tests.py의 기본 전체 선택을 하나의 고정된 최종 판본에서 실행하고, 발견한 실제 결함의 수리·직접 확인·설명·공식 미러를 같은 task에서 마친다. 두 선행의 accepted는 각 결과의 수용이며 모든 결함 해결을 뜻하지 않을 수 있다. 시작할 때 두 report/수용 manager 기록을 읽고 정확한 남김을 먼저 처리한다. 이미 알려진 미수리 실패를 그대로 둔 채 전체 실행부터 반복하지 않는다.

SESSION_JSON, task.json, inputs/context.md·plan.md·seams.md, 자기 workspace의 do-math AGENTS.md·scripts/tests/시험-지침.md를 읽는다. 추가 입력의 C:/math/.async/dm와 docs는 읽기 전용이다. managers/0065/review.md와 sources/storage-scope-direction-2026-10-15.md를 적용한다. 기존 g4-general/objective.md는 원 G4 의미의 참고이고 이번 실행·Git 권한은 이 objective가 정한다. G1~G8을 유지하되 이번 완료 범위는 G4다.

## 시작판과 Git 준비

기존 full4는 4288선택 중4262passed/14failed/9error/1skipped/2not_run·fixture error1·exit1이다. g4-measurement는 제품 무변경으로 지정 adapter meta7passed·exit0을 확인했지만 두 결과를 더해 전체 성공으로 세지 않는다. g4-contracts의 최종 수리와 검증 범위는 시작 시 수용된 report/현재 코드로 확인한다.

async snapshot에는 .git이 없다. 기존 tests/support/branch_gate.py:repository_root와 write_index는 실제 Git root/HEAD를 소비한다. **자기 workspace 루트에만 독립 .git과 실제 작업 사본의 로컬 기준 commit을 준비할 수 있다.** 이는 공용 Git 관리 금지에 대한 한정 예외다. 이 메타데이터는 workspaces.py의 SKIP 대상이며 통합하지 않는다. 원 base/baseline/inputs를 변경하지 않고 공용 main/index/commit·다른 task의 .git은 쓰거나 복사하지 않는다. 자기 HEAD를 main commit이나 시험 성공 표시로 설명하지 않는다.

tasks/g4-measurement/evidence/prepare.py·git-preparation.json·judgment.md의 성공한 준비를 참고한다. helper를 재사용하면 자기 task/evidence로 복사하고 TASK/SHORT를 자기 경로에 맞춘다. 기존 .git이 있으면 소유/root/HEAD를 먼저 확인하며 지우거나 다시 초기화하지 않는다. Git redirection 환경을 확인하고, 기존 GIT_CEILING_DIRECTORIES를 보존하면서 자기 task 부모와 짧은 외부 임시루트를 추가한다. 외부 임시 cwd는 공용 Git을 찾지 않고 workspace만 자기 root를 반환해야 한다.

초기화 시 빈 template/hooks, 사본 local 설정, .git/info/attributes의 filter/text/ident 비활성화로 바이트 변환을 막는다. NUL pathspec으로 실제 제품·시험·문서·공식미러를 기록하고 timing/selection-index/T3 store 같은 생성 캐시는 제외한다. 준비 전후 파일 바이트와 commit blob 대응, root/HEAD 및 정확한 명령/환경을 기록한다. 수리로 판본이 바뀌면 같은 자기 Git에 최종 소스 기준 commit을 추가할 수 있으며 동일한 바이트 보존 규칙을 따른다. 전역 설정·remote/push·새 비Git fallback·가짜 HEAD는 필요 없다. g4-measurement의 7개 meta만 별도로 다시 실행할 필요 없이 아래 공식 전체 선택에서 확인한다.

## 실행과 관련 수리

1. 두 선행의 결과/남김을 정적으로 대조한다. 해결 가능한 실제 미수리는 관련 정의·호출부·시험·문서를 함께 고친다. 기존 통과가 충분한 부분은 다시 확인하지 않고, 수리 후 실행이 필요한 불확실성만 정확 실패 ID/작은 공식 선택으로 확인한다.
2. 최종 수리판·공식미러를 고정한 뒤 `python -u -B .claude/skills/do-math/scripts/run_tests.py --jobs 3 --output <새 짧은 외부 경로>`를 실행한다. **위치 선택·--tier·--match 없이** structure/unit/contracts/sim/flows 기본 전체를 선택한다. 이는 측정 --tier T3와 다르다. 별도 시험을 동시에 돌리지 않는다. 다른 시험이 있으면 총시험 worker3 이하로 jobs를 낮춘다. 현재 runner는 일반 병렬 묶음을 기다린 뒤 resource/lean 클래스를 순차 격리하므로 기존 adapter meta 내부jobs2와 일반jobs3은 겹치지 않는다. 이 배선을 바꾸면 동시 수를 다시 확인한다.
3. TEMP/TMP/TMPDIR·출력은 저장소 밖 짧고 고유한 경로를 사용한다. 실행 중 제품/시험/문서/미러를 바꾸지 않는다. 시간은 소프트 기준이며 경과 시간만으로 종료·skip·선택 축소·성공을 만들지 않는다. 기본 전체에 포함된 기존 resource/meta의 작은 native 자식 호출은 그대로 실행한다.
4. 새 실패는 원 report/traceback과 실제 정의로 제품 결함·현행 계약과 다른 fixture/기대값·환경 준비를 구별한다. 직접 관련 수리를 이 task에서 끝내고 가장 작은 필요한 확인을 한다. 전체 실행 뒤 소스가 바뀌면 마지막 판본의 기본 전체를 완결한다. 이미 통과한 불변 전체를 다시 돌리지 않는다. 큰 독립 수리나 범위 밖/외부 조건 때문에 끝낼 수 없다면 원실패·유효 수리·정확 남김을 partial/blocked로 보고한다.

writes는 실제 전체 검사에서 발견한 관련 수리를 가능하게 하는 do-math 정본/미러 범위다. 단언 약화·내부 검사 대역·새 skip·구판 필드/호환 계층·무관 정리는 허용하지 않는다. 공통 저장 검증/codec·기존 업무 성질은 재사용하고 가족별 전생산자/전필드/새reader/옛head quota를 추가하지 않는다. 시간 측정만을 위한 반복 실행이나 별도 최적화·검증 프레임워크를 만들지 않는다. 공식 build_skill_mirrors.py로 수정의 대응 미러 생성/check를 마친다. 생성기·다른 스킬·overlay·서비스는 수정 범위 밖이다.

## 완료 근거와 인계

command/cwd/비밀 아닌 필요한 환경·시각·관측 exit·원 report/stdout/stderr를 보존한다. selected와 fixture 아닌 reports[].rows의 ID를 중복/누락/여분 없이 대조하고 counts/fixture_counts·각 row/subTest·complete/successful·changed_during_run을 판정한다. source_sha256과 최종 제출판이 일치해야 한다. Python 범위 밖 제품 문서·미러는 별도 판본과 공식미러 check로 연결한다. 실행 캐시는 evidence에 보존 후 자기 base로 복원해 제품 변경에서 제외한다.

G4는 실패·오류·미실행이 없고 최종 선택이 모두 대응할 때 충족한다. skip/expected_failure는 정확 ID·사유와 원문 계약으로 별도 판정하고 passed로 세지 않는다. 기존 unit.test_context_catalog의 WinError1314 조건부skip는 실제 outside_symlink 반려 확인이 아니며 호스트 권한을 바꾸지 않는다. 관측 시간/소프트초과·원실패/준비오류를 유지한다. G4를 충족하지 못했으면 boolean successful이나 부분 통과 합계로 완료를 대신하지 않는다.

evidence/judgment.md에 G4 충족 여부·실제 수리 이유·최종 결과·판본/exit·남김을 적고 report.json을 작성한다. `python C:/math/services/async-development/check.py report C:/math/.async/dm g4-final`을 통과시킨다. 제품 변경이 없으면 변경 없음으로 보고한다. 공용 source/context/plan/seams/queue/state·다른task·engine은 읽기 전용이다. graphify 갱신·기존 연구 재개/삭제는 하지 않는다.

G5 fresh 전체 T3(--tier T3 --full), G6 전체 변이, G7 전체 T4/T5·유료 모델/외부 HTTP/설치/예약 실험은 별도 후속이며 이번에 덧붙이지 않는다. 작은 기존 meta 자식 실행을 이 관문 완료로 확대하지 않는다. 후속은 실제 수용된 G4 최종판을 사용하며 G1~G3의 최종 연결·L01/Windows1314·G8 최종review도 남는다.
