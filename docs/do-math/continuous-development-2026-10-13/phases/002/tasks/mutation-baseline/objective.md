## 목적과 역할

G3와 G6을 위해 변이 포착의 정상 기준을 신뢰할 수 있게 한다. phase 001 gate-readiness F4에서 정상 child 결과가 없는데도 `killed`와 `passed=True`로 이어질 수 있는 소스 경로를 확인했다. manager도 현재 `mutation.py`를 대조했으며 동적 재현은 하지 않았다. 이 task가 작은 실제 parent/child 경계에서 재현·수리·직접 소비 검증을 마친다. 전체 변이 실행, 함수 모집단 확정, T3 전건 측정은 이후 책임이다.

첫 입력은 run:phases/001/tasks/gate-readiness/report.json의 F4와 run:phases/001/manager-evidence/source-excerpts.json의 mutation 구간이다. 관련 과거 변경은 closure-map의 prior-review-state.json에서 PR01/B56의 mutation 결과/정상 기준 부분만 따라간다. 실제 diff·직접 소비자·원보고를 대조해 유지/교정 범위를 보고하고 PR01 전체 완료로 확대하지 않는다.

## 완료 조건

### A1 정상 증거 부재의 거짓 포착 재현과 차단

수리 전 코드에서 `mutant`가 시험 t를 실패시키고 정상 child가 결과 파일을 남기지 않는 입력을 재현한다. 현재 `fails_unmutated`의 `t in failing`이 False가 되어 killed/통과로 이어지는 결과와 기대 동작의 차이를 실제 출력으로 보존한다. 소스 읽기만으로 red라고 쓰지 않는다. 변경 후 동일 입력은 killed가 아니며 `passed`도 False다. 정상 실행 미확정의 구체적 이유와 그 정상 실행 시도를 근거까지 추적할 수 있다.

### A2 parent와 child가 실제 실행 증거를 구별

정상·변이 양쪽에서 선택, 실제 수집/실행 결과, 종료 코드를 구별할 만큼 작은 단일 결과 계약을 정한다. 결과 부재·파손·잘못된 구조, 비정상 child exit, 수집/load 오류, 기대 시험 미실행·skip/expected failure를 정상 통과로 간주하지 않는다. 실제 시험 t가 정상 소스에서 통과했을 때만 그 t의 mutant 실패/error/unexpected success를 포착 근거로 쓴다. fixture skip/error와 0건 실행도 pass로 축약하지 않는다.

loader 오류 문자열 자체를 killer로 쓰지 않는다. 변이 때문에 import가 깨지는 경우를 포착으로 인정하려면 같은 대상 선택이 정상 소스에서는 실제로 수집·실행·통과했다는 근거가 있어야 한다. 이를 확인하지 못하면 실행/수집 증거 오류로 남긴다. 정상 소스도 같은 수집 오류인 경우와 구별하는 시험이 있어야 한다. 계약·결과 구조의 정확한 필드명은 구현자가 정하되 생산자·소비자·fixture·도구 docstring을 같은 변경에서 맞춘다. 구형 tuple/문자열 결과를 계속 받는 호환 계층은 만들지 않는다.

재시도마다 spec/result/출력·exit와 어느 정상 기준을 사용했는지 연결한다. 이전 실패 시도의 근거를 같은 디렉터리에 덮어써 최종 결과만 남기지 않는다. 잘못된 결과 때문에 상위 보고 자체를 잃지 않도록 실패를 기록한다. 경과 시간만으로 failure/kill을 만들지 않는다.

### A3 기존 검출·선택·실행 성질 보존

실제 정상 통과와 mutant 실패의 양성 대조군은 killed이며, 실제 정상 실패는 `baseline_failing` 또는 명시적인 정상 실패 정보로 남아 최종 관문을 막는다. 정상 실패 시험은 기존처럼 제외해 다음 가능한 포착 시험을 검사한다. 근거 오류는 정상 실패와 구별한다.

D9의 지연 정상 기준, 같은 시험의 확인 결과 재사용, 값싼 모듈 우선/failfast, 앞 모듈 생존 뒤 다음 모듈 검사, 유효하지 않은 색인의 layer-folder fallback, 미진입/not_executed, trivial, 생존/사유 없는 pseudo 항목, timeout 없음의 성질을 보존한다. 변이 모집단·rule·선택 폴더나 baseline 보호를 비용 때문에 줄이지 않는다. 관련 PR01/B56의 유지·교정·미검토 범위를 실제 변경과 함께 기록한다.

### A4 실제 child와 공유 최종 판정의 연결

작은 임시 fixture와 실제 Python child를 사용해 선택 시험 통과/실패, 실제 수집 오류, 실제 결과 부재 또는 비정상 종료를 parent가 어떻게 보고하는지 확인한다. 전부 `_child_run` 대역 결과로만 입증하지 않는다. 결정 논리의 유한 입력 행렬에는 process/file 외부 경계의 대역을 사용할 수 있으나 실제 경계 검증과 구별한다. 작업 트리의 제품 소스를 변이하지 않고 임시 mutant만 사용한다.

`mutation.main`의 종료 판단과 `run_tests`의 T3 mutation 소비가 동일한 `passed` 의미를 사용하는지 실제 소비 경로의 작은 시험으로 확인한다. 여기서는 최종 전체 T3를 실행할 필요가 없다. 정상 기준 오류의 비통과와 정상 대조군의 통과를 함께 보이고 수동 보고 dict만 넣은 predicate 시험으로 전체 연결을 대신하지 않는다.

### A5 관련 검증·문서·미러 인도

관련 공식 시험을 완결하고 선택 ID·실제 row·exit·소스 고정을 보존한다. unit.test_mutation, boundary.test_mutation_baseline, 직접 소비에 영향받은 unit.test_runner_tiers 및 해당 구조/시험 냄새 검사를 포함한다. 새 관문 결과 의미를 mutation docstring과 필요한 시험 지침에 반영한다. 정본·생성 미러를 맞추고 생성기 `--check`를 통과한다. 제품 전체 일반/T3/전체 변이/T4/T5의 완료를 주장하지 않는다.

## 판단과 경계

phase.json의 파일만 수정한다. run_tests.py는 mutation 소비 구간을 맞추는 데 필요할 때만 수정하며 T4 측정·빈 T5·문서 필드 수리로 범위를 늘리지 않는다. tests/시험-지침.md도 이번 정상 기준/근거 의미만 수정한다. 새 구현 파일이나 외부 라이브러리·범용 결과 프레임워크는 이 작업의 기본 해법이 아니다. 필요한 좁은 자료형/helper는 mutation.py 내부에 둘 수 있다. 보고 형식과 검증용 fixture를 함께 고치는 것은 이번 재량이다.

최종 모집단의 adapter5/runner2 처분은 context C11에 고정돼 있다. 이 task에서 LAYERS를 바꾸거나 변이 범위를 넓히지 않는다. 원문 설계6.3, 현 시험 지침, 최신 소프트 시간 정책을 따른다. 실제 프로세스 대기에는 시간 제한을 재도입하지 않으며 관찰 도구의 yield와 종료를 구별한다.

모든 검사 묶음은 순차이며 전체 worker 합계 3 이하다. 실제 child 검사가 자식을 띄우므로 공식 관련 검사는 `--jobs 1`로 시작한다. source/시험을 검사 중 편집하지 않는다. 생성된 .timings.json은 허용한 실행 보조 파일이며 의미 변경이 있을 때 보고하고 최종 함수 선택/T3 자료를 새로 생성하거나 조작하지 않는다. 임시 fixture·실제 child 출력·새 raw 보고는 자기 evidence 아래 또는 그 시험의 격리 scratch에 둔다.

`.claude/skills/do-math/`가 정본이고 `.agents/skills/do-math/`는 생성물이다. 생성 전 dirty 상태와 미러 영향 범위를 확인한다. 배정된 대응 파일 이외의 drift를 발견하면 덮어쓰지 말고 정확한 finding으로 남긴다. generator·overlay 규칙·engine·공용 context/plan/seams·과거 task 파일은 수정하지 않는다. Git commit/reset/checkout은 manager 책임이다. 현재 미추적/수정 파일이나 기존 연구 인스턴스도 정리하지 않는다.

## 검증 방법

cwd는 `C:\math`, Python은 `C:\Users\wogud\AppData\Local\Programs\Python\Python312\python.exe`다. source-before/after, 실제 실행 명령·시각·process/session·stdout/stderr·exit를 자기 evidence에 저장한다. raw report는 새 디렉터리로 받고 원본 바이트를 유지한다.

1. 수리 전에 A1 반례와 정상 통과 대조군을 기존 시험을 활용한 작은 선택으로 실행한다. 실제 실패 단언이 무엇인지 확인하고 import/인자 오류를 red로 세지 않는다. 반복 attempt는 별도 경로를 쓴다.
2. 수리 후 A1/A2 입력 행렬을 검사한다. 동일 t의 정상 pass/fail/missing/skip/load/exit, mutant missing/load/failure, 0건 수집과 결과 구조 오류를 실제 의미에 맞게 분류한다. 문자열 membership만 바꾼 수리로 닫지 않는다. A4의 실제 child 경계 원출력을 별도로 남긴다.
3. 최종 관련 실행의 기본 명령은 `& 'C:\Users\wogud\AppData\Local\Programs\Python\Python312\python.exe' -u -B .claude/skills/do-math/scripts/run_tests.py unit.test_mutation boundary.test_mutation_baseline unit.test_runner_tiers structure.test_test_smells --jobs 1 --output docs/do-math/continuous-development-2026-10-13/phases/002/tasks/mutation-baseline/evidence/related-green`이다. 새 관련 시험이 기존 모듈에 포함되게 하고 실패 뒤 재실행은 새 output 경로를 사용한다. 직접 실행 경계 확인도 공식 시험에 포함한다. 실행 중 result.json 관찰은 필요할 때 do_math.file_io.read_bytes_shared를 쓴다.
4. 미러 절차는 repo:.claude/skills/writing-skills/references/멀티런타임_동기화.md다. 영향이 허용 파일 안임을 확인한 뒤 동일 Python으로 `.claude/skills/writing-skills/scripts/build_skill_mirrors.py`와 `--check`를 순서대로 실행한다. 원문/생성물 diff를 확인한다.
5. report A1~A5에 실제 판정과 근거를 대응하고 미검사/후속 전체 관문을 명시한다. 마지막에 동일 Python으로 `services/continuous-development/check.py report C:\math C:\math\docs\do-math\continuous-development-2026-10-13 002 mutation-baseline`을 통과한다. A가 충족되지 않으면 partial/blocked와 정확한 질문·유효한 근거를 반환한다.
