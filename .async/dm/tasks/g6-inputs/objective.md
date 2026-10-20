# 현재 수용판에서 G6의 명시 시험 선택과 실행 입력을 완성한다

G6는 현재 1~3층의 모든 대상 함수에 극단 변이를 적용하고 실제 정상 기준과 대응시키는 요구다. 이 task는 이를 실행할 수 있도록 기존 mutation 도구의 한정 선택 공백과 직접 시험을 고치고, g5-target 수용 diff를 기존 모집단·선택에 반영한다. 전체 G6 실행은 이 결과를 수용한 뒤 별도 실행자가 맡는다. 준비만 반복하는 조사 task가 아니라 필요한 코드·시험·설명·미러와 작은 직접 검증을 함께 마치는 work다.

## 입력과 실제 선행

SESSION_JSON, task.json, 고정 inputs/context·plan·seams, 자기 workspace의 do-math AGENTS.md·시험-지침.md·이음새-정본.md와 managers/0096/review.md·verification-review.json을 읽는다. sources/t3-targeted-direction-2026-10-16.md·storage-scope-direction-2026-10-15.md·archive-resume-2026-10-16.md가 적용된다. 공용 source와 다른 task 기록은 읽기 전용이다.

g6-scope/evidence/population.json·execution-plan.md·static-check.json은 고정 g45-final판의 준비 결과다. 123모듈/1677함수, 비trivial1645 중 indexed1641·무진입4, trivial32, 20묶음이다. 이 수를 새 판본의 고정 quota로 삼지 않는다. 원규칙은 scripts/do_math/layers.py:LAYERS, tests/support/mutation.py:functions/body/rule_of/mutate/tests_for/run/main, selection.py:read_index/usable/is_ancestor_of_head다. 기존 규칙과 정상 기준/오류 의미는 그대로 사용한다.

g5-target의 **수용된** report/integration/evidence와 자기 시작판이 다른 실제 선행이다. 해당 다섯 모듈과 변경 시험/helper/입력의 영향만 기존 population에 반영한다. report의 최종 근거 경로를 따라가고 미완성 사본을 소비하지 않는다. 과거 source가 필요하면 `python C:/math/services/async-development/workspaces.py restore C:/math/.async/dm TASK baseline|result NEW_DIRECTORY PATH...`로 필요한 경로만 복원한다. 과거 workspace/base 존속을 전제로 삼지 않는다.

## 한 작업에서 마칠 결과

1. 원색인에서 진입키가 없는 operation_trace.measured와 그 decorate, engine_operation과 그 decorate의 실제 계약을 기존 sim/test_engine_operation_trace.py·test_engine_trace_failure_paths.py에서 확인한다. import 때 꾸미기를 만들었다는 사실과 시험이 직접 factory/decorate를 호출한 사실을 구별한다. 기존 시험으로 충분한 성질을 반복하지 말고 필요한 직접 호출·원 반환/예외 보존·실제 trace 의미만 가장 싼 입력으로 보완한다. 제품 runtime은 이 배정에서 변경하지 않는다. 구체적인 runtime 결함을 발견하면 정확 심볼·영향을 보고한다.

2. 기존 mutation CLI/API에 유한한 **명시 시험 ID 선택**을 연결한다. 현 --only 모듈 범위에서 쓰며, 원색인 자동 선택과 보충/대체의 의미를 한 가지 명확한 계약으로 정하고 docstring·시험 지침·보고에 함께 기록한다. 기본 색인 선택의 동작은 유지한다. 명시 ID는 관측된 진입 ordinals와 구별해 실제 출처·선택을 보고한다. 무진입 네 함수 및 수용 diff 뒤 새/영향 함수에 사용할 수 있어야 한다. 기존 색인이 가리키는 유효 시험을 이유 없이 빠뜨리지 않고, 바뀌거나 제거된 시험 ID는 수용 diff와 직접 소비를 근거로 처리한다. 함수별 새 registry나 별도 실행/색인 병합 프레임워크를 만들지 않는다. 새 옵션·의미의 구체 구현은 작업자가 가장 작은 방법으로 정한다.

   원index/coverage/entered/store를 수동 편집하거나, 일부 실행을 측정된 전체 index로 위장하거나, runtime 소스를 바꿔 fallback을 유도하지 않는다. 전체 T3를 반복할 필요가 없는 입력 방식이어야 한다. 명시 선택에서 실제 수집·실행이 누락되면 기존 evidence 오류로 남고 정상 child 없이 killed가 되지 않아야 한다. skip·환경오류·시간경과·0건을 성공으로 바꾸지 않는다. 기존 run_tests.py의 mutation.run 소비와 기본 호출은 유지하며 새 run_tests 옵션이나 측정 구조 변경은 필요 없다.

3. g5-target의 최종 수용 diff와 이번 직접시험 변경을 기존 population에 연결한다. 다섯 모듈은 필수 갱신하고 다른 모듈도 선택 시험/helper/입력 또는 호출 경계가 바뀐 만큼만 갱신한다. 원 source/AST/body SHA와 index 참조, indexed 입력 readers 및 import closure를 재사용한다. 함수의 줄 이동과 본문 변경을 구별하고 '다른 모듈'만으로 기존 선택을 최종 인증하지 않는다. 원전체 T3의 유효 범위와 추가 측정의 한계는 유지한다. 전체 모집단 재감사나 과거 raw 전수 복사는 하지 않는다.

4. 후속 실행자가 바로 쓸 evidence/population.json·execution-plan.md에 현재 함수/선택/변경 이유·정확한 유한 CLI argv·사용 index/입력/실제 source 판본을 남긴다. 기존 20묶음을 필요한 만큼만 수정한다. 실제 원commit ancestry와 단일 pseudo_tested.json 소유자, 명령/child 하나씩 순차 실행하는 원안을 유지한다. 모든 outcome은 아직 not_run이며 이 task의 작은 도구 확인과 전체 G6를 구별한다. 전체 변이 과정에서 발견할 survivor/오류의 수리와 최종 판정은 후속이다.

## 검증·실행 입력과 쓰기 경계

시험은 jobs1·한 번에 한 명령이다. 수정한 mutation 선택 계약과 decorator 직접 성질을 확인하는 최소 ID를 자기 공식 run_tests.py로 실행한다. 실제 선택이 child에 전달되고 실패 후보가 실제 정상 통과로만 killed가 되는지 기존 boundary/test_mutation_baseline.py의 작은 fixture를 재사용하여 한정 확인한다. 기존 모든 오류 조합의 전수 반복은 하지 않는다. --every 전체123모듈, 전체 일반/T3/T4/T5, 실공급자/설치/예약은 이번 배정이 아니다. 추가 T3도 배정하지 않는다. 필요한 선택 입력은 직접 시험과 수용된 g5-target 근거로 공급하고 측정으로 주장하지 않는다.

자기 workspace의 독립 Git 준비는 허용한다. 보존 색인은 g45-final/evidence/G6-inputs.json의 `preserved_selection_index` 경로/SHA이며 기본 tests/.selection-index.json의 오래된 자료와 다르다. 실제 원commit 4dae85911f26f891fc3d79be9916bf4363e2d46f는 managers/0095/g45-index-baseline.bundle에 있다. g6-scope/execution-plan.md의 실제 bundle fetch·작업파일을 건드리지 않는 mixed reset·실제 현재 snapshot 자식 commit 안과 g45-final/evidence/prepare.py의 raw-byte filter 설정을 필요한 만큼 재사용한다. 직접 준비했다면 실제 root/HEAD/ancestor·bytes 불변을 기록한다. 원bundle/공용 Git/전역 설정은 쓰지 않는다. 이 준비를 하지 않았다면 미실행으로 명시하고 전체 Git 실험만을 추가하지 않는다.

TEMP/TMP/TMPDIR/output은 짧고 고유한 저장소 밖 경로를 사용한다. GIT_CEILING_DIRECTORIES의 기존 값을 보존해 자기 부모/외부 경로를 추가한다. source는 시험 동안 고정한다. 생성 index/비용cache/listing은 필요한 증거를 먼저 자기 evidence에 보존한 뒤 시작 bytes/부재로 복원한다. 전체 G6 listing은 이 task에서 게시하지 않는다.

쓰기 범위는 mutation.py, 직접 unit/sim/boundary 시험, 시험 지침과 그 공식 미러다. 필요한 최소 파일만 바꾸고 selection.py/branch_gate/run_tests/runtime/층 목록/분모를 바꾸지 않는다. 공식 build_skill_mirrors.py를 사용하고 허용 범위 밖 결과는 제출에 섞지 않는다. 제품 변경과 검증을 한 task에서 마치며 공용 context/plan/seams/queue/state·graphify는 수정하지 않는다.

## 제출

evidence/judgment.md에 현재 선택 계약, 네 공백 처리, g5-target 수용 diff의 영향/재사용, 실행·미실행과 남은 조건을 적는다. 관련 원report·실제 argv/exit/source SHA·정상/변이 child 원자료는 자기 evidence에서 찾을 수 있게 남긴다. 원G4/전체T3·환경6arc/10행·기존 조건부skip·소프트 시간 기준을 보존하며 G5/G6 전체 완료를 주장하지 않는다. report.json의 실제 changes와 근거를 쓰고 `python C:/math/services/async-development/check.py report C:/math/.async/dm g6-inputs`를 통과시킨다.
