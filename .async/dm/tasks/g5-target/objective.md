# 미도달 5모듈의 현재 계약 수리와 관련 시험 추가 측정

사용자가 요청한 결과는 결함을 놓치는 시험 기제를 줄이고 현재 제품·시험을 사용할 수 있게 만드는 것이다. g45-final의 수용판에서 일반 검사 G4는 4523선택/4522passed·1정당한 환경skip/exit0다. 같은 판본의 fresh 전체 T3는 측정누락0·재사용0·closing_eligible=true이지만 5모듈39arc/43행이 남아 G5 미충족이다. 이 task는 그 정확한 남김을 실제 생산자·호출자·검사와 대조하고 필요한 구현·시험·설명을 함께 마친다. 단순히 coverage 숫자를 줄이는 작업이 아니다.

## 먼저 읽을 현재 입력

SESSION_JSON, task.json, 고정 inputs/context·plan·seams, 자기 workspace의 do-math AGENTS.md·scripts/tests/시험-지침.md·scripts/이음새-정본.md를 읽는다. RECORDS의 sources/t3-targeted-direction-2026-10-16.md가 과거 전체 fresh 반복 조건보다 우선한다. sources/storage-scope-direction-2026-10-15.md와 archive-resume-2026-10-16.md도 적용한다. managers/0095/review.md·verification-review.json·handoff-delta.json이 이번 수용 근거다.

정확 좌표와 원인 후보는 tasks/g45-final/evidence/fresh-gap-functions.json·gap-disposition.json, 원측정 경로/SHA는 G6-inputs.json·t3-full-a/audit.json이다. 원본 전체 report는 C:/g45f-6d21/t3-full-a/report.json, coverage/store/entered/opened와 보존 index는 G6-inputs.json의 경로를 따른다. 이 자료는 읽기 전용이다. 수용 사본이 정리되면 필요한 과거 파일만 `python C:/math/services/async-development/workspaces.py restore C:/math/.async/dm g45-final result <새 디렉터리> <상대경로...>`로 복원한다. 기존 workspace/base 존속을 전제로 삼지 않는다.

## 한 작업으로 묶는 범위

대상은 scripts/do_math/context_store.py, core_engine.py, file_io.py, integration.py, lifecycle_engine.py다. core의 복구/수신/적용이 같은 helper·설명을 쓰므로 이 5모듈의 관련 수리와 공식 미러를 한 작업자가 소유한다. 현재 제품 코드를 읽고 미도달이 실제 누락, 불필요한 중복 방어, 유효한 외부 조건 중 무엇인지 구분한다. 이전 bounded 수리의 의미 판단은 직접 관련된 것만 재사용한다.

- core_engine의 15함수31arc/32행: _upkeep, _retry_submission_publications, _review_recovery_control, _restore_goal_audit_publication, _recover_disappeared, _validate_bundle_current, _receive_submission, _finish_native_recovery, _obsolete_action_reason, _apply_extensions, _apply, _maintenance_cleanup, _apply_operational_disposition, _complete_operational_disposition, _apply_plan. 정확 좌표는 fresh-gap-functions.json이다. 원 수용·권한·현재성·재시도·게시 후 정산 의미를 유지한다. 허용 입력으로 도달할 수 없는 중복 방어는 실제 앞단 검사와 모든 현재 caller를 근거로 줄일 수 있으며 불가능 상태를 합성해 시험만 통과시키지 않는다.
- integration.bundle_impact_request의 140→141/141행: 같은 보존 assignment의 복수 review candidate를 순회할 때 중복 후보가 실제로 나오는지, 앞선 반환이 언제 일어나는지 판단한다. 정확 영향/assignment 일치와 독립 검토 의미를 유지한다.
- lifecycle_engine._action_lifecycle_gate의 250→268: closed/paused/conversation 검사 뒤 가능한 lifecycle 상태를 실제 enum·생산·호출과 대조한다. 유효한 상태 검사를 약화하지 않는다.
- context_store.collect_outputs와 file_io의 기존6arc/10행은 실제 file symlink 또는 POSIX 조건이다. 이번 호스트에서 이미 확인한 WinError1314와 현재 플랫폼 한계를 재사용한다. 새로운 설치·권한 변경·WSL/환경 반복 probe·os.name 대역·내부 제품 패치로 실제 환경 통과를 꾸미지 않는다. 필요한 실제 입력이 없으면 좌표·요구 조건을 그대로 남기고 독립적인 나머지 수리는 완료한다.

기존 충분한 codec·검증 게시·업무 동작 보장은 재사용한다. 가족별 모든필드/새reader/옛head quota나 새 전수 감사를 만들지 않는다. 쓰기 목록은 허용 범위이며 모든 파일에 새 시험을 쓰라는 의무가 아니다. support와 시험은 위 다섯 모듈의 직접 수리에 필요한 부분만 고친다. runner/계측/선택/변이 프레임워크, 층 목록·분모·임계값은 수정하지 않는다. 새 skip·근거 없는 no-cover·단언 약화·구판 호환은 하지 않는다. 배정 밖 runtime 수정이 실제로 필요하면 원인·최소 필요한 경계를 보고한다.

## 필요한 선택과 검증

시험 슬롯은 jobs1, 한 번에 한 공식 명령이다. 병행 g6-scope는 읽기 전용/시험0이므로 그 결과나 미완성 사본을 기다리지 않는다. 관련 수리를 끝낸 뒤 기존 함수·시험 색인과 실제 직접 소비에서 유한한 시험 ID/모듈을 고르고 왜 그 선택이 이번 불확실성을 확인하는지 짧게 기록한다. 제품 모듈 경로를 시험 ID로 넘기지 않는다. 정적 계약으로 충분한 질문은 정적으로 마친다.

필요한 T3는 `python -u -B .claude/skills/do-math/scripts/run_tests.py <관련 시험 ID 또는 시험 모듈...> --tier T3 --jobs 1 --t3-store <자기 새 외부 경로> --output <자기 새 외부 경로>` 형태로 수행한다. 위치 선택 또는 정확 --match를 반드시 사용한다. 위치 선택 없는 전체 T3, 전체 --full, 전체 일반/T4/T5/변이 재실행을 이 task에 포함하지 않는다. 증분 store를 쓰면 원본을 쓰기 가능한 경로로 넘기지 말고 자기 별도 사본을 사용하며 사용 전 입력/함수 판본을 확인한다. 측정 자료를 실제로 얻어야 하는 선택이 전부 reuse되는 방식으로 새 도달을 주장하지 않는다. 필요하면 새 빈 store로 같은 유한 선택만 측정한다. 작은 수리 뒤에도 그 관련 최소 선택만 확인한다.

현재 run_tests._t3_plan은 선택한 시험 모듈만 plan의 universe로 삼고 _finish_t3는 그 plan.reuse만 합친다. 부분 선택은 closing_eligible=false이고 전체 selection index를 쓰지 않는다. 따라서 부분 report의 전체 module 미측정/미도달과 exit1을 기능 실패로 오인하거나, 원 전체 coverage에 원arc를 임의 합산해 전체 통과로 만들지 않는다. 현재 지원하는 조합·재사용의 범위와 한계를 실제 t3_store.plan/path_mapper/코드 digest 의미에 따라 설명한다. 변경 없는 범위는 원전체 판본·현재 bytes/관련 경계가 같은 근거를 남겨 재사용하고, 변경 함수/이동한 줄의 구도달은 유효하다고 추정하지 않는다. 기술 제약이 남아도 전체 실행으로 대체하지 않는다. raw coverage/store/index·원 source는 수정하지 않는다.

자기 workspace에 독립 실제 Git 기준을 준비하는 것은 허용한다. g45-final/evidence/prepare.py의 빈 hooks/template·local filter/text/ident 비활성화·NUL pathspec·cache 제외·바이트 대조를 필요한 만큼 재사용한다. 공용 Git/index/commit·전역 설정·remote/push·다른 task .git 복사·가짜 HEAD는 하지 않는다. TEMP/TMP/TMPDIR/output은 짧고 고유한 저장소 밖 자기 경로를 사용하고 GIT_CEILING_DIRECTORIES는 기존 값을 보존하여 자기 부모/외부 임시 root를 추가한다. PYTHONDONTWRITEBYTECODE를 자식에도 적용한다. source를 실행 중 바꾸지 않는다. 무관한 설치/다운로드/실모델/예약/기존 연구 변경과 C:/.skill-workspace 생성물 삭제는 하지 않는다.

제품 설명과 대응 미러를 같은 작업에서 마무리한다. 공식 build_skill_mirrors.py를 사용하고 결과 범위를 확인한다. 생성 cache/index는 필요한 증거를 먼저 자기 evidence에 보존한 뒤 baseline.json/objects의 시작 bytes/부재로 복원하여 제품 변경에 섞지 않는다.

## 결과와 완료 판단

evidence/judgment.md에 다섯 모듈의 실제 처분, 변경한 이유, 확인/미확인 범위, 외부 입력이 필요한 정확 남김을 적는다. evidence/gap-disposition.json에는 원39arc/43행→최종 함수/판본·단순화/직접측정/외부조건의 대응만 남기며 새 registry를 만들지 않는다. 추가 측정의 command/cwd/필요환경/원report/실제행/관측exit·전후source SHA와 원전체를 재사용할 유효 범위를 기록한다. 판본이 다른 통과 수를 더하거나 closing_eligible를 변경하지 않는다. G6가 소비할 최종 함수 변경·선택/도달 추가 근거와 기존 index의 한계를 함께 인계한다.

맡은 구현·관련 확인을 끝냈더라도 G5 전체가 충족됐는지는 실제 원전체+추가범위와 남은 조건으로 구분한다. 외부6arc/10행만 남아도 이를 감추지 않는다. report.json을 작성하고 `python C:/math/services/async-development/check.py report C:/math/.async/dm g5-target`을 통과시킨다. 공용 context/plan/seams/queue/state와 graphify는 바꾸지 않는다.
