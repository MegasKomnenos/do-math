# 정상 기준이 없는 변이 성공을 막는 수리의 효과를 한 번 무력화해 확인한다

KEEP-REGRESSION-PROOF의 K-73은 수정 내용을 무력화하면 시험이 실패하는지 확인하라는 요구다. 수용된 keep-proof는 일반 극단 변이·수리 전 red와 수정 후 green을 확인했지만, 현재 정상 기준 수리를 직접 무력화한 별도 실행은 지정 원자료에서 찾지 못했다. 이 task는 그 한 건을 끝낸다. 새로운 제품 기능이나 모든 역사 수리의 재감사가 아니다.

SESSION_JSON, task.json, inputs/context.md·plan.md·seams.md, do-math AGENTS.md와 현행 시험-지침.md를 읽는다. C:/math/.async/dm/managers/0045/review.md 및 tasks/keep-proof/evidence/judgment.md의 K-73 절과 historical-source-comparison.json·report-rows.json을 시작 근거로 삼는다. requirements-index.json의 K-73 원문은 유지하되 과거 단계표의 exact reversal proved 문장을 실행 근거로 대신하지 않는다.

## 수행할 한정 확인

현재 `scripts/tests/support/mutation.py:run` 안 `baseline(chosen)`은 실제 정상 child 결과가 없거나 child가 오류로 끝나면 status=evidence_error로 보존한다. mutant의 failing ID는 이 정상 기준이 passed일 때만 killer가 된다. 현재 `passed(report)`는 execution_error 등을 실패로 소비한다. 다음 두 기존 시험을 그대로 사용한다.

- `boundary.test_mutation_baseline.ActualBaselineTests.test_missing_normal_child_result_never_certifies_a_kill`
- `boundary.test_mutation_baseline.ActualBaselineTests.test_actual_normal_pass_certifies_the_mutant_failure`

자기 시작 workspace에서 분리한 고정 정상 사본과 probe 사본을 만든다. 두 사본 사이의 의도한 코드 차이는 `baseline`의 정상 결과 부재/child 오류 분류 한 곳이다. 그 경우만 종전의 정상 통과 취급으로 바꿔, 실제 mutant 실패가 잘못 killed가 되도록 수리를 무력화한다. 정상 result·실제 child 실행·선택·다른 결과 검증·오류 원자료·시험 단언은 유지한다. `validate_result` 전체를 끄거나 `passed`/시험 기대값을 바꿔 목적과 다른 실패를 만들지 않는다. 정확 변경은 실제 코드를 읽고 가장 작은 형태로 정하고 diff와 이유를 남긴다.

정상 사본에서는 두 ID가 통과하고, probe 사본에서는 missing-normal ID가 실제 `killed == killed` 반례로 실패하며 정상 대조 ID는 통과하는지 확인한다. 프로브가 실패했다는 사실만으로 수용하지 않는다. 정확 failing 단언·실제 정상 child exit17/result 부재와 mutant 실패, 잘못된 baseline/status와 killed의 연결이 필요하다. import/Git 준비 오류·0건·미실행·일반 fixture 실패는 이 결론의 근거가 아니다. 예상과 다르면 실제 원인을 읽고 probe 준비에 필요한 최소 수정만 하며, 처음 실패도 보존한다.

기존 legacy의 세 핵심 파일은 keep-proof가 현재와 같음을 검수했다. 기존58passed의 하위 성질은 재사용한다. 다만 이 task는 Git 없는 workspace에서 독립 실행 사본을 새로 구성하므로, 정상 두 ID의 한 번 실행은 그 실제 준비와 현재 runner 경로의 유효성을 확인한다. 정상/프로브의 두 최소 호출 외 전체 boundary·일반·T3·전체 변이는 실행하지 않는다. 각 사본의 공식 `scripts/run_tests.py`로 위 두 ID만 jobs1·서로 다른 출력에서 실행한다. 실행 중인 사본은 수정하지 않는다.

## 사본·자원·쓰기 경계

task writes=[]이며 제출 제품은 무변경이다. probe 변경은 자기 task/evidence의 별도 실험 사본 또는 보존 경로가 명확한 자기 전용 짧은 임시 디렉터리에서만 한다. workspace/base, C:/math 공용소스, 다른 task, legacy 원보고, queue/state, 서비스, 제품 Git index/commit과 graphify를 수정하지 않는다. 제품 미러 생성은 필요 없다. 이 확인에서 실제 제품 수리가 필요하다고 판명되면 정확 원인/소유파일/미완료를 보고하고 범위 밖 제품을 바꾸지 않는다.

`ActualBaselineTests._run_fixture`는 `branch_gate.repository_root()`와 실제 Git blob/HEAD를 사용하고, 격리 scratch 경로가 그 저장소 아래여야 한다. 공용 C:/math를 우연히 fixture 저장소로 쓰지 않는다. 필요하면 자기 전용 짧은 실험 사본에 최소 Git 저장소와 HEAD를 시험 입력으로 구성한다. 그 폐기용 fixture의 로컬 Git 초기화/기준 commit은 허용되며 제품 commit이 아니다. 출력·scratch는 그 fixture root 아래, scripts 바깥에 둔다. 원본 snapshot의 bytes와 사본·의도한 probe 차이를 기록하고 별도 사본을 scripts 아래에 중첩해 discovery/SHA 모집단을 오염시키지 않는다. 현재 GIT_CEILING_DIRECTORIES와 Windows 긴 경로 조건을 확인한다. Git/프로세스 자체가 이번 실제 경계이고 모델·Lean·외부 서비스 호출은 필요 없다.

이 task의 자료 읽기·AST 대조·사본 준비는 즉시 진행할 수 있다. 동시 시험worker3 제한을 지키기 위해 **새 공식 시험 또는 시험 모듈 import 전** C:/math/.async/dm/state.json에서 기존 `storage-knowledge`, `storage-profiles`, `keep-rejections` 중 하나 이상이 `exited`임을 읽기 전용으로 확인한다. 이 세 작업 중 첫 종료로 생긴 시험 슬롯 하나는 proof-baseline에 예약돼 있다. 그 전에는 시험을 시작하지 않고 조건이 바뀌기를 기다린다. 60초 이하의 조건 확인 간격을 쓰고 시간 경과를 종료/성공 조건으로 삼지 않는다. 처음 슬롯을 인계받은 상태·시각을 evidence에 남긴다. 이 대기는 실행 자원에 관한 것이며 이 세 task의 제품 결과·수용에 대한 의존성이 아니다. `depends_on`은 keep-proof만이다. 이후 manager도 proof-baseline 종료 전 이 예약을 다른 새 시험 task에 중복 배정하지 않는다. 기존 진행 중 배정은 변경하지 않는다.

## 제출

evidence에 정상/프로브 소스 판본과 의도한 diff, 정확 명령·관측 parent exit·선택/고유 실제 row/counts/fixture_counts/complete/successful/changed_during_run, 실제 child spec/result 또는 부재·attempt/exit·stdout/stderr와 결론을 보존한다. 짧은 임시 경로를 사용하면 원파일 경로를 유지한 manifest와 필요한 원자료를 task/evidence에 연결한다. 원실패를 덮어쓰거나 서로 다른 판본의 통과를 합산하지 않는다. 프로브의 예상 failed는 제품 정상판 실패와 구별한다.

K-73의 이 수리 무력화 질문이 충족됐는지, 정상 대조가 보존됐는지, 확인한 실제 프로세스/파일 경계와 한계를 report.json에 남긴다. G2/G3 전체·PR01 전체·G4~G8/최종 통합판·Windows1314·L01을 종결하지 않는다. status/summary/changes=[]/verification/findings를 갖춘 뒤 `python C:/math/services/async-development/check.py report C:/math/.async/dm proof-baseline`을 확인한다. manager가 무변경 integrate와 수용 여부를 판단한다.
