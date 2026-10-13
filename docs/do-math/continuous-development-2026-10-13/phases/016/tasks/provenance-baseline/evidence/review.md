# 과거 비교 입력 준비 결과

이 task는 입력 준비를 완료했다. 제품 import, 공식 runner, pytest/unittest, ordinary/measured child와 실제 old/new 비교는 실행하지 않았다. 015의 양쪽 두 skipped와 G2/G3/G7 미충족은 그대로 남는다. 후속 연결 작업이 이 입력을 소비하고 두 정확 비교 및 양쪽 전체 T4를 실행한다.

## 판본 선택의 근거

- 도입 commit: `bbe64043f49d46fb7c3b6e768b99a8acbaa125cf`.
- 선택한 pre-fix commit: 도입 commit의 실제 첫 부모 `010b059700115f6d5d3df1bf24e931cf78eaa44a`.
- 조사 시 HEAD: `72684c76ed5d282279de5de956523ea17ffd4e40`. HEAD가 baseline인 것은 아니다. 현재 runner에는 015의 미커밋 변경도 있어 현재 파일을 HEAD와 동일하다고 가정하지 않았다.
- `fix-search.stdout`의 `git log -S input_dependencies`와 `fix-diff.stdout`에서 Measurement의 producers/shared_inputs/dependency_inputs, input_dependencies/opened, shared-use의 producer/paused 처리, transitive 함수 결속, worker별 의존 해소 후 병합, t3_store format2와 필수 인자 도입을 확인했다.
- `fix-memory.stdout`는 도입 commit에 포함된 M-0472 원바이트다. 이 기록은 당시에도 `010b0597` canonical scripts를 git archive로 별도 추출해 P10/P11 비교에 사용했다고 명시한다. 도입 diff, 실제 부모 관계, 원기록의 baseline이 서로 일치한다. 단지 오래된 날짜나 다른 경로를 근거로 선택하지 않았다.
- `b56-original-record.json`는 현 단계 전환표 `/current_work/measurement_integration`의 해당 원기록이다. `pr01-slice.json`의 PR01/B56 review slice가 이 selector, runner/branch_gate/t3_store/shared-input 소비자와 원보고 네 selector를 지정한다. 이 한 slice의 입력 자격을 검토했으며 PR01 전체를 종결하지 않았다.

`requirement-trace.json`에 기록한 것처럼 requirement-state의 103개 row에는 `P10`/`P11` 문자열이나 해당 ID가 없다. 여기서 P10/P11은 현재 정확 비교의 skip 이유와 도입 기록 M-0472의 표기다. 문서 후속 packet P10/P11 또는 2026-09-18 계획 P10/P11로 연결하지 않는다. requirement-state의 관련 원문 진입점 K-05(빈 선택 비통과), K-06(새 출력/시험 결과 캐시 없음)을 추적했고, 직접적인 선택/측정 보존 근거는 설계.md 5.3/5.4/5.5, A29, B56의 contract/limits 및 도입 당시 비교 시험이다. requirement-state에 없는 원문 ID를 만들어 대응시킨 것은 아니다. 새 증거는 현재 G2/G3/G7의 이 한정 남김에 연결해야 한다.

## 존재 원기록과 부재한 원보고

`historical-report-availability.json`은 B56의 다음 네 정확 경로를 직접 확인한 결과다. 네 파일은 모두 현재 없다.

| selector | 원 임시 보고 경로 끝 | 역사 기록의 수치 |
|---|---|---|
| changed_area | do-math-tests-fj9e2u51/report.json | 83 passed, 2 skipped |
| structure | do-math-tests-6bxa__n2/report.json | 6 passed |
| timing_red | do-math-tests-eaivmkw0/report.json | 1 failed |
| exact_baseline_comparison | do-math-tests-hkr9st06/report.json | 2 passed, 15.2초 |

기록된 SHA256과 전체 절대 경로는 JSON에 있다. 위 수치는 원기록의 주장이고 현재 raw 재검산 결과가 아니다. 삭제 이유나 다른 모든 저장소에서의 부재를 추측하지 않았다. 015의 history-original-observation.json에 있는 전체-T3 요약과 그 raw 부재는 별도 역사 자료이며 정확 비교 원보고를 대신하지 않는다. 연구 인스턴스/삭제 자료를 복원하지 않았다.

## 추출과 바이트 검증

소비자가 설정할 절대 경로:

```text
C:\math\docs\do-math\continuous-development-2026-10-13\phases\016\tasks\provenance-baseline\evidence\pre-provenance\scripts
```

`baseline-manifest.json`은 910개 파일, 총 9,901,995바이트, 901개 고유 blob의 repository_path/path/Git mode/blob/SHA256/크기와 scripts tree ID, baseline/도입 commit, 정확 추출 명령 수신을 담는다. `git ls-tree -r -z <commit> -- .claude/skills/do-math/scripts/`로 모집단을 확정하고 그 blob만 `git cat-file --batch`로 읽어 binary exclusive write했다. text 변환/필터를 거치지 않았으며 현재 파일을 섞지 않았다. git checkout/reset/worktree/index 변경은 없다.

모든 상대 경로에 POSIX/Windows 절대경로·drive·..·구분자/예약명·대소문자 충돌 검사를 적용했다. blob 외 mode, symlink/gitlink는 허용하지 않았다. 실제 경로/상위 디렉터리의 reparse point를 검사하고 evidence 밖으로 나가는 대상을 거부했다. 추출 파일 전건을 Git blob 객체의 원바이트, Git object ID, manifest SHA256 및 전체 경로 모집단에 대조했다. `verify_baseline.py`는 새 Git 조회로 독립 재확인했고 baseline-verify.command.json의 실제 exit는 0이다. 검증 stdout·stderr와 baseline-verification.json을 보존했다.

run_tests.py, test_categories.py, tests/support/branch_gate.py, t3_store.py, selection.py 및 do_math/file_io.py/layers.py 등 당시 scripts 트리를 전부 포함한다. 현재 API에 맞추는 수정은 하지 않았다. 추출 root는 현재 canonical/mirror SCRIPTS와 다른 절대 경로다. 추출한 옛 runner의 독립 CLI 전체 실행이나 구판 지원을 추가하는 변경은 이 인계의 목적이 아니다.

## 정적으로 확인한 API와 비교 성질

`api-static-verification.json`은 AST 선언과 현재 시험의 literal child 프로그램만 분석한 결과다. baseline에 `flatten`, `_run_suite(tests, directory, *, checkpoint=False, measurement=None)`와 complete/successful/tests_run/rows 생산, Measurement(root, data_file), start/begin/save/entered/merge, opens/import_opens/coverage, shared_state/used_state/unmeasured가 존재한다. SNAPSHOT/WORKER의 baseline mode는 이 공통 API만 부른다. t3_store는 import되지만 baseline capture가 새 store API를 호출하지 않는다.

구체적인 차이는 사실이다: 옛 Measurement에는 input_dependencies/shared_inputs가 없고 absorb는 entered/opens 두 입력, 옛 build_index/module_records/records에는 새 필수 input_dependencies keyword가 없으며 store format은 1이다. 새 WORKER는 mode=measured에서만 새 의존/색인 API를 호출하고 baseline mode에서는 요청하거나 합성하지 않는다. PROBE의 baseline 반례는 기존 write_index로 뒤 모듈 reader 누락을 확인하도록 작성됐으며 이번 두 exact-baseline 시험의 old capture와 구별한다. 현재 source 세 파일은 015 manager source-inspected SHA와 작업 시작/끝 모두 일치한다. 정확 시험 파일은 도입 Git blob과 개행을 제외한 모든 행이 같다.

`assert_baseline_capture`는 같은 fixture에서 old ordinary, new ordinary, old baseline-measured, new measured 네 실제 child를 실행한다. ordinary의 ids/outcomes/reads/extra_reads 전체를 서로 비교하고 모든 child의 complete/successful/tests_run/고유 row/전건 passed를 확인한다. serial 축은 nested False/True × 순서 ab/ba, 그리고 import/fixture/paused 축이다. serial의 reads는 ['read'] 한 번이며 일반 결과와 계측 결과가 같아야 한다. import 축은 import.txt/import-unused.txt/fixture.txt/fixture-unused.txt/paused.txt의 실제 읽기 목록·값·순서를 보존한다. ordinary count나 결과를 만들어 넣지 않는다.

literal 비교는 모든 entered label과 pair를 보존하고 빈 리스트인 label도 삭제하지 않는다. `split_entries`가 오직 `<shared>` marker를 분리한다. opens의 label/path, import_opens의 path/opener를 정확 비교한다. coverage는 root 상대 파일 모집단, 전체 context, 각 context의 파일별 lines와 arcs를 정확 비교하며 contexts_by_lineno나 총 도달률만으로 대체하지 않는다. shared_state는 함수 recorder의 shared label만 전환하고 literal open/coverage의 원래 fixture/module context를 바꾸지 않는다는 보존 성질이다.

허용한 marker 차이도 정확 기대값이다. serial에서는 양 consumer의 outer 사용은 유지한다. old는 leaf/unused-leaf 사용을 첫 fixture에 귀속하고 paused passive의 outer 사용도 남긴다. new는 leaf를 shared:outer, unused-leaf를 shared:unused-outer에 결속하며 paused 사용자를 만들지 않는다. nested=False에서는 leaf 사용 간선이 없다. import 축의 old는 fixture a/import-leaf, fixture b/fixture-parent, actual/import-leaf와 paused/fixture-parent를 남기고, new는 paused를 없애고 shared:fixture-parent/import-leaf를 남긴다. 이것이 literal 함수 진입이나 실제 coverage에 shared reach를 덧붙이는 허가는 아니다.

두 worker exact 비교는 같은 producer code/key에 실제 input-a/input-b를 각각 읽는 fresh child를 사용한다. 각 worker의 old/new ordinary·literal 자료를 대조한 뒤 각 판본의 실제 Measurement.merge를 호출한다. 각 merge 결과의 entered/opens/import_opens와 파일/context/line/arc가 해당 판본의 두 raw worker set union과 같아야 하고, old/new merged literal 자료도 같아야 한다. 이 exact 시험의 worker 생성은 a/b 차례이며, 같은 파일의 다른 회귀에 있는 두 Popen 동시 실행 검사와 혼동하지 않는다. 소비 의존의 worker 동일 key 격리·정상 store 교체 성질은 별도의 기존 현재 회귀가 다룬다.

정적 API 호환은 실행 성공의 증거가 아니다. 현재/옛 _run_suite의 후속 변화, 실제 coverage/Python 판본과 원문 계측 차이 때문에 정확 비교가 실패할 가능성은 아직 검사하지 않았다. 실패하면 raw old/new 차이를 확인하고 원인과 영향을 보고해야 하며 옛 입력을 현 API에 맞춰 고치거나 literal 동등성 단언을 낮추면 안 된다.

## 후속 연결 작업의 명령과 원자료

cwd는 C:\math, 공식 실행은 두 트리를 순차로 수행한다. 다음 PowerShell에서 `$evidence`만 후속 task가 소유한 **새 evidence 절대 경로**로 지정한다. 출력 디렉터리는 새것이어야 하고 이 task의 baseline을 출력 위치로 쓰지 않는다.

```powershell
$python = 'C:\Users\wogud\AppData\Local\Programs\Python\Python312\python.exe'
$env:SHARED_INPUT_BASELINE_SCRIPTS = 'C:\math\docs\do-math\continuous-development-2026-10-13\phases\016\tasks\provenance-baseline\evidence\pre-provenance\scripts'
$ids = @(
  'boundary.test_shared_input_provenance.SharedInputProvenanceTests.test_exact_baseline_literal_entries_opens_and_coverage_with_explicit_marker_differences'
  'boundary.test_shared_input_provenance.SharedInputProvenanceTests.test_exact_baseline_two_worker_raw_union'
)
& $python -u -B 'C:\math\.claude\skills\do-math\scripts\run_tests.py' @ids --jobs 1 --output (Join-Path $evidence 'canonical-exact')
# 정본의 실제 종료를 기록한 뒤 미러를 실행한다.
& $python -u -B 'C:\math\.agents\skills\do-math\scripts\run_tests.py' @ids --jobs 1 --output (Join-Path $evidence 'mirror-exact')
```

각 실행은 기대 선택2/고유 실제 row2/passed2/skipped0/error0/failed0/not_run0와 실제 exit0를 확인한다. 실행 전에 환경 변수가 parent와 owned worker까지 전달됐는지 argv/환경의 비밀 없는 해당 값으로 기록한다. --list만으로 실행을 대신하지 않는다. 유효하지 않은 baseline을 현재 경로로 대체하거나 skip을 승인하지 않는다. 이 phase는 이 명령을 실행하지 않았다.

015의 전체 T4 연결 미충족을 해소하려면 fixture 수리 검수와 이 입력 준비 검수 후 같은 후속 작업에서 다음 두 전체 실행도 각각 완결한다. 새 유료 호출이나 과거 raw counts 합산은 필요하지 않다.

```powershell
& $python -u -B 'C:\math\.claude\skills\do-math\scripts\run_tests.py' --tier T4 --jobs 1 --output (Join-Path $evidence 'canonical-t4-full')
& $python -u -B 'C:\math\.agents\skills\do-math\scripts\run_tests.py' --tier T4 --jobs 1 --output (Join-Path $evidence 'mirror-t4-full')
```

후속 자료 보존 방법:

1. 시작/종료마다 baseline-manifest 전건 SHA/Git blob 대응과 현재 정본·미러 Python/시험/문서 해시를 저장한다. 이 task의 tool-edition.json은 현재 Python 3.12/coverage 배포 메타데이터와 실행 파일 SHA, Git 판본의 관측이며 후속 실행 시 다시 확인한다. worker의 실제 요청/시작·종료 소스와 부모 소스, baseline commit을 구분한다. HEAD만으로 미커밋 판본을 대표하지 않는다.
2. 공식 report/선택/rows/result.json, 실제 argv/cwd/환경값, PID/시작/종료/exit, stdout/stderr를 보존한다. 전체 T4는 실제 모집단을 다시 얻고 각 worker 게시/adapter DB와 source 판본을 대조한다. 총 worker3 이하·한 검사 묶음씩의 공용 제약을 지킨다.
3. 현재 정확 시험의 TemporaryDirectory는 teardown에서 지워지므로 공식 report만 남으면 raw snapshot을 재검산할 수 없다. 후속 작업의 근거용 companion에서는 **현재 파일의 실제 exact 시험 메서드와 WORKER/SNAPSHOT 프로그램을 그대로 호출**하고, task-owned TEMP/TMP 아래 fixture들을 `doCleanups()` 전에 복사/해시한다. 구체적으로 fresh companion process에서 TEMP/TMP를 자기 scratch로 지정하고 현재 test module을 import해 TestCase를 만든 뒤 두 실제 메서드를 호출한다. 각 호출 뒤(예외 시에도 finally에서 cleanup 전에) 자기 scratch의 fixture 트리를 자기 raw 디렉터리에 보존한 다음 case.doCleanups()로 정리한다. suite/child/기대값을 재작성하거나 비교 입력을 주입하지 않는다. 이 추가 관측은 공식 runner의 결과와 별도로 보고한다. 이는 raw 보존의 필요를 충족하기 위한 후속 실행 방법 제안이며 이 task에서 구현·실행한 관측이 아니다.
4. raw 모집단은 serial의 nested/order별 old/new ordinary와 old/new measured snapshot.json, imports 네 snapshot, worker a/b 네 snapshot씩과 old/new merged snapshot, 각 run/result.json 및 coverage.data/opened.json/entered.json이다. snapshot의 상대 파일/context/lines/arcs와 entered/open/import_open을 직접 재대조한다. baseline-manifest SHA/fixture producer와 모듈의 source SHA/실제 sys.executable·coverage 판본을 함께 남긴다. 보존하지 못한 raw는 미관측으로 보고한다.

이 task의 A 완료는 위 후속 검사의 성공을 뜻하지 않는다. 실제 비교 또는 양쪽 전체 T4가 실패하면 정확 원인에 맞는 다음 work가 필요하며, G4 전체 일반/G5 fresh T3/G6 전체 변이/G8 최종 review와 L01 등 다른 남김도 유지한다.
