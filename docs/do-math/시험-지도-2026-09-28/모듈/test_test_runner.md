# test_test_runner

| 항목 | 값 |
|---|---|
| 조각 | `foundation` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_test_runner.py` (193행) |
| 클래스 / 테스트 | 1 / 11 |
| 시험 대상 제품 코드 | 시험 실행기 `scripts/run_tests.py`(`TimedResult`, `_run_suite`, `wait_for_worker`, `_isolated`, `main`의 선택·`--list` 경로, `_write_json`, `TESTS`)와 `scripts/test_categories.py`(`test_group`, `isolation_for`, `unregistered_modules`, `shard_for`, `SHARDS`). `do_math` 제품 코드는 검사 대상이 아니다 |
| 사용하는 픽스처 모듈 | 없음 |
| 격리 표지 | 없음 |
| 시작 상태 | 네 단에 들지 않는다. 시험 안에서 정의한 합성 `TestCase`, 합성 시계, 합성 Job 대역을 실행기 함수에 직접 넘긴다. 두 시험은 실제 `scripts/tests` 폴더를 발견·목록화한다 |

## 목적

모듈 docstring은 "Runner regressions use synthetic tests/clocks, never a compiler or provider."다. 시험 대상은 do-math 제품이 아니라 시험을 돌리는 도구 자체다. `run_tests.py`의 docstring은 실행기를 이렇게 정의한다. 조각(shard) 단위로 차례로 도는 unittest 실행기다. `lean`·`resource` 시험은 소유한 Windows Job 안에서 단계별 제한 시간을 두고 클래스 단위로 돈다. 결과 캐시는 없다. `SHARDS`에 없는 시험 모듈이 있으면 실행을 멈춘다. `test_categories.py`의 docstring은 `SHARDS`가 어느 모듈이 어느 조각에서 도는지의 유일한 목록이라고 밝힌다. 또한 격리 표지가 클래스에 붙거나 메서드에 붙고, 메서드 표지가 클래스 표지를 이긴다고 밝힌다.

이 모듈은 실행기가 결과를 거짓으로 통과시키거나 잃지 않는다는 성질들을 검사한다. 실패는 다음 시험이 도는 동안에도 읽을 수 있다. 실패한 부분 시험(subTest)은 기계 보고에서도 실패로 남는다. 모르는 시험 ID는 선택 전체를 거부한다. 격리 작업자의 비정상 종료 코드는 성공 JSON에 가려지지 않는다. 시간 초과는 소유한 프로세스 트리를 끝내고 돌던 시험을 식별한다.

## 모듈 수준 요소

- 행 12: 스킬의 `scripts/` 폴더를 `sys.path` 앞에 넣는다. 그래야 `run_tests`와 `test_categories`를 모듈로 import할 수 있다.
- 행 13–14: `import run_tests`, `from test_categories import isolation_for, test_group as category, unregistered_modules`. `test_group`은 `category`라는 이름으로 들여온다.
- 행 192–193: 직접 실행하면 `unittest.main()`을 부른다.

## RunnerTests (행 17–189)

`unittest.TestCase`를 그대로 상속한다. 표지, 클래스 속성, 설정 훅, 도우미가 없다. 대부분의 시험이 시험 안에 합성 `TestCase` 클래스를 정의하고, `unittest.TextTestRunner(stream=io.StringIO(), resultclass=lambda *a, **k: run_tests.TimedResult(*a, directory=..., **k))`로 돌린다.

### `test_failure_is_readable_while_the_next_test_runs_before_group_completion` (행 18–41)
- 성질: 한 시험이 실패하면 그 실패 기록이 즉시 `failures/` 아래 파일로 게시된다. 그래서 같은 묶음의 다음 시험이 도는 동안에도 실패를 읽을 수 있다. 묶음 결과(`result.json`)는 아직 없다.
- 준비: 합성 `Failed.test_first`는 `'preserve this exact failure'`로 실패한다. 합성 `Following.test_next`는 실행 중에 `failures/*.json`을 읽어 스스로 단언하고, 읽은 행을 바깥 목록 `observations`에 넣는다. 두 시험을 한 스위트로 묶는다.
- 실행: `TimedResult`를 결과 클래스로 한 `TextTestRunner.run(...)`.
- 단언: 안쪽 `test_next`는 다음을 단언한다. 실패 파일이 정확히 하나다. 그 행의 `complete`가 거짓이다. `test.id`가 첫 시험의 ID다. `test.outcome == 'failed'`다. `test.details[0]`에 실패 메시지가 들어 있다. `result.json`이 아직 없다. 바깥 단언으로는 `observations`의 길이가 1(안쪽 시험이 실제로 돌았음), `result.failures`의 길이가 1, `wasSuccessful()`이 거짓이다.
- 대역: 없음(합성 시험).
- 비고: 실패 파일 이름은 시험 ID의 SHA-256이다(`TimedResult._outcome`, run_tests.py 행 83–89). 제품 주석은 "Publish this failure before the next possibly long test begins. It is diagnostic evidence, not a completed group result."다. `checkpoint`가 기본값 거짓이므로 진행 중 `result.json`을 쓰지 않는다. 그래서 `result.json` 부재 단언이 성립한다.

### `test_isolation_label_is_inherited_and_a_method_label_overrides_its_class` (행 43–59)
- 성질: 격리 표지는 하위 클래스로 상속되고, 메서드 표지가 클래스 표지를 이긴다. 알 수 없는 표지 이름은 거부된다.
- 준비: `@category('lean')`을 붙인 `Base`(메서드 `test_compiler`, 그리고 `@category('resource')`를 붙인 `test_job`). 표지 없는 하위 클래스 `Child(Base)`. 표지 없는 `Plain`(메서드 `test_rule`, 그리고 `@category('resource')`를 붙인 `test_process`).
- 실행: 네 시험 인스턴스에 `isolation_for`를 부른다. 이어서 `category('unit')`을 부른다.
- 단언: `Child('test_compiler')`는 `'lean'`, `Child('test_job')`은 `'resource'`, `Plain('test_rule')`은 `None`, `Plain('test_process')`는 `'resource'`다. `category('unit')`은 `ValueError`다(메시지는 보지 않는다).
- 대역: 없음.

### `test_every_test_module_is_in_exactly_one_shard_and_absent_modules_are_reported` (행 61–67)
- 성질: 실제 `scripts/tests`의 모든 `test_*.py`가 `SHARDS`에 등록되어 있고, `SHARDS`에는 없는 모듈의 이름이 없다. 등록 검사는 디스크에만 있는 모듈과 목록에만 있는 모듈을 모두 보고한다.
- 준비: 실제 시험 폴더 `run_tests.TESTS`. 그리고 빈 `test_new_module.py` 하나만 둔 임시 폴더.
- 실행: 두 폴더에 `unregistered_modules`를 부른다.
- 단언: 실제 폴더의 결과가 `([], [])`다. 임시 폴더에서 빠진 모듈이 `['test_new_module']`이고, 목록에만 있는 모듈에 `'test_test_runner'`가 있다.
- 대역: 없음.
- 비고: 이름은 "정확히 한 조각에"라고 말하지만, 단언은 등록 여부만 본다. `test_categories._SHARD_OF`는 모듈 이름을 키로 한 사전이다(행 58). 한 모듈이 두 조각에 적혀 있으면 뒤 조각의 값이 앞 조각을 덮어쓴다. 그 경우 `unregistered_modules`는 아무것도 보고하지 않고, 이 시험도 실패하지 않는다. 중복 등록은 검사되지 않는다. 이 시험은 실제 저장소 상태를 읽는 회귀 검사이기도 하다. 새 시험 모듈을 `SHARDS`에 등록하지 않으면 이 시험이 실패한다(`시험-지침.md` 4절 규칙 9).

### `test_positional_ids_select_a_module_class_or_method_without_prefix_collisions` (행 69–81)
- 성질: 위치 인자로 준 시험 ID는 모듈, 클래스, 메서드를 고른다. 이름이 다른 모듈의 접두사여도 그 모듈을 함께 고르지 않는다.
- 준비: 실제 시험 폴더. 표준 출력과 오류를 문자열로 돌린다.
- 실행: `run_tests.main(['--list', 'test_test_runner.RunnerTests'])`, 이어서 `run_tests.main(['--list', 'test_knowledge'])`.
- 단언: 첫 호출의 반환이 0이다. 출력 행이 하나 이상이다. 모든 행의 둘째 칸(탭 구분)이 `'test_test_runner.RunnerTests.'`로 시작하고, 첫째 칸이 `'foundation'`이다. 둘째 호출의 출력 행이 하나 이상이고, 모든 행의 시험 ID의 모듈 부분이 정확히 `'test_knowledge'`다. 원문 주석(행 78)은 `test_knowledge_io`와 `test_knowledge_storage`가 그 이름을 접두사로 공유한다고 밝힌다.
- 대역: 없음. 실제 발견을 한다.
- 비고: `main`은 목록화 전에 세 가지를 실제로 한다. `unregistered_modules(TESTS)`로 등록을 검사하고, `_edition()`으로 `scripts` 아래 모든 `.py`를 해시하며, `loader.discover`로 모든 시험 모듈을 import한다. 따라서 첫 호출의 반환 0은 모든 시험 모듈이 import 오류 없이 적재된다는 사실도 함께 요구한다. 둘째 호출의 반환값은 단언하지 않는다. 선택 규칙은 `test.id() == name or test.id().startswith(name + '.')`다(run_tests.py 행 291).

### `test_an_id_that_matches_no_test_refuses_the_whole_selection` (행 83–88)
- 성질: 여러 시험 ID 가운데 하나라도 어떤 시험에도 맞지 않으면, 나머지 유효한 선택도 목록화하지 않고 전체를 거부한다.
- 준비: 표준 출력과 오류를 문자열로 받는다.
- 실행: `run_tests.main(['--list', 'test_test_runner', 'test_no_such_module'])`.
- 단언: 반환이 2다. 표준 출력이 빈 문자열이다. 표준 오류에 `'test_no_such_module'`이 있다.
- 대역: 없음.
- 비고: 원문 주석(행 84)은 "A mistyped ID beside valid ones must not drop out and leave the rest to read as a pass."라고 밝힌다. 제품 메시지는 `'No test matches: ...'`다(행 293–298). 이 시험도 실제 발견을 거친다.

### `test_failing_subtest_remains_a_failure_in_the_machine_report` (행 90–104)
- 성질: 부분 시험 하나가 실패하고 다른 부분 시험이 통과해도, 기계 보고의 부모 행은 실패로 남고 보고 전체가 실패다.
- 준비: 합성 `Specimen.test_cases`. 부분 시험 `value='failure'`는 `assertEqual(1, 2)`로 실패하고, `value='success'`는 통과한다.
- 실행: `TimedResult`로 돌린 뒤 `result.preserve(complete=True)`.
- 단언: 보고의 `successful`이 거짓이다. 첫 행의 `outcome == 'failed'`다. 그 행의 `details[0]`에 `'failure'`가 있다.
- 대역: 없음.
- 비고: `details[0]`은 `str(subtest)`와 추적 문자열을 이은 것이다(`addSubTest`, 행 122–126). 그래서 `'failure'`는 부분 시험의 매개변수 표기에서 나온다.

### `test_timeout_terminates_the_owned_tree_and_identifies_the_running_test` (행 106–122)
- 성질: 작업자가 제한 시간을 넘기면 대기 함수는 소유한 Job을 종료하고, 종료가 확인되었는지와 그때 돌던 시험을 보고한다.
- 준비: 진행 파일 `progress.json`에 `{'sequence': 1, 'test_id': 'slow.compiler', 'phase': 'test'}`를 쓴다. 합성 시계 `clock.value`와, 시계를 앞당기는 `pause`를 둔다. 합성 `Job`의 `wait`는 `ended`를 돌려주고, `terminate`는 `ended`를 참으로 만든다. `inspect`는 끝나기 전에는 활성 프로세스 1과 PID `(123,)`을, 끝난 뒤에는 빈 상태를 보인다.
- 실행: `run_tests.wait_for_worker(job, path, .2, clock=..., pause=...)`.
- 단언: 반환의 `test_id == 'slow.compiler'`이고 `termination_confirmed`가 참이다. `job.ended`가 참이다.
- 대역: 합성 `Job`, 합성 시계와 대기 함수.
- 비고: 대기 함수는 먼저 `progress-*.json` 게시 파일을 찾고, 없으면 `progress.json`을 읽는다(행 184–185). 이 시험은 두 번째 경로를 쓴다. 실제 작업자가 쓰는 이름(`progress-000001.json` 등, `TimedResult._progress`)은 이 시험에서 쓰이지 않는다. 반환의 `timeout_seconds`와 `observed_seconds`는 단언하지 않는다.

### `test_skipped_subtest_is_not_reported_as_a_running_or_passed_parent` (행 124–138)
- 성질: 부분 시험이 건너뛰어지면 부모 행은 `running`이나 `passed`가 아니라 `skipped`로 보고되고, 건너뛴 부분 시험과 그 사유가 기록된다. 보고는 성공이다.
- 준비: 합성 `Specimen.test_cases`. 부분 시험 `value='unavailable'`은 `skipTest('fixture unavailable')`을 부르고, `value='checked'`는 통과한다.
- 실행: `TimedResult`로 돌린 뒤 `result.preserve(complete=True)`.
- 단언: 보고의 `successful`이 참이다. 첫 행의 `outcome == 'skipped'`다. `skipped_subtests[0].reason == 'fixture unavailable'`이다.
- 대역: 없음.
- 비고: `TimedResult.addSkip`은 부분 시험의 건너뜀을 부모 행에 붙이고, 부모가 `running`이면 `skipped`로 바꾼다(행 103–112). unittest는 부분 시험이 건너뛰어진 시험에 `addSuccess`를 부르지 않으므로 부모 행은 `skipped`로 남는다.

### `test_class_setup_skip_accounts_for_each_selected_test` (행 140–151)
- 성질: 클래스 준비(`setUpClass`)가 건너뜀을 일으키면, 선택된 각 시험이 `skipped` 행으로 보고되고 보고는 성공이다.
- 준비: 합성 `Specimen`. `setUpClass`는 `unittest.SkipTest('compiler unavailable')`을 던지고, 두 시험은 돌면 실패한다.
- 실행: 표준 오류를 버리면서 `run_tests._run_suite([Specimen('test_one'), Specimen('test_two')], <임시>)`.
- 단언: `fixture` 표지가 없는 행만 모아, 결과가 `['skipped', 'skipped']`다. 보고의 `successful`이 참이다.
- 대역: 없음.
- 비고: unittest는 클래스 준비의 건너뜀을 `setUpClass (<모듈>.<클래스 qualname>)` ID의 행 하나로 알린다. `_run_suite`는 보고되지 않은 시험마다 그 준비 행을 찾아, 건너뜀이면 `skipped` 행을 더하고 아니면 `not_run` 행을 더한다(행 145–154). 원문의 지역 `from contextlib import redirect_stderr`(행 141)는 모듈 머리의 import와 겹친다.

### `test_next_test_gets_its_own_deadline_without_restarting_class_fixtures` (행 153–169)
- 성질: 격리 작업자 안에서 다음 시험이 시작되면(진행 순번이 바뀌면) 그 시험은 새 제한 시간을 받는다. 그래서 각각 제한 시간 안에 끝나는 두 시험이 합쳐서 제한 시간을 넘겨도 종료되지 않는다.
- 준비: 진행 파일에 순번 1(`'first'`)을 쓴다. 합성 시계와 대기 함수를 둔다. 합성 `Job.wait`는 시계가 .4 이상이 되면 진행 파일을 순번 2(`'second'`)로 한 번 바꾸고, 시계가 .8 이상이면 끝났다고 알린다. `terminate`는 부르면 `AssertionError('a progressing test group must not time out')`을 던진다. `inspect`는 빈 상태를 보인다.
- 실행: 제한 시간 .6으로 `run_tests.wait_for_worker(Job(), path, .6, clock=..., pause=...)`.
- 단언: 반환이 `None`이다(정상 종료).
- 대역: 합성 `Job`, 합성 시계와 대기 함수.
- 비고: 새 순번을 관찰한 시각부터 제한 시간을 다시 잰다(행 186–189). 순번 1의 제한 .6은 .8보다 앞이지만, 합성 `Job.wait`가 약 .45에 쓴 새 순번을 다음 회차(약 .5)에 관찰하면서 제한이 약 1.1로 옮겨진다. 이름의 "without restarting class fixtures"는 한 작업자 프로세스 안에서 제한만 새로 잡는다는 설계를 말한다. 이 시험은 클래스 준비의 재실행 여부를 관찰하지 않는다.

### `test_native_worker_failure_cannot_be_hidden_by_a_successful_json_report` (행 171–189)
- 성질: 격리 작업자 프로세스가 0이 아닌 종료 코드로 끝나면, 작업자가 남긴 `result.json`이 성공을 말해도 보고는 실패이고 종료 코드가 기록된다.
- 준비: 합성 `Case.test_one`. 합성 `Job` 클래스는 생성자 인자를 무시하는 문맥 관리자다. `resume()`이 작업 폴더에 `complete=True`, `successful=True`인 `result.json`과 그 시험의 `passed` 행을 쓴다.
- 실행: `do_math.windows_job.WindowsJob`을 합성 `Job`으로, `run_tests.wait_for_worker`를 `None`으로, `run_tests._exit_code`를 7로 패치한다. 그 뒤 `run_tests._isolated([test], <임시>/worker, 1)`을 부른다.
- 단언: 보고의 `successful`이 거짓이다. `returncode == 7`이다.
- 대역: `patch('do_math.windows_job.WindowsJob', Job)`, `patch.object(run_tests, 'wait_for_worker', return_value=None)`, `patch.object(run_tests, '_exit_code', return_value=7)`.
- 비고: 제품은 `report['successful'] = report['successful'] and returncode == 0`로 합친다(행 220). `_isolated`는 함수 안에서 `from do_math.windows_job import WindowsJob`을 하므로, 모듈 속성 패치가 효력을 가진다. 실제 자식 프로세스는 만들지 않는다.

## 실행기에서 검사되는 것과 검사되지 않는 것

이 절은 `scripts/run_tests.py`(356행)와 `scripts/test_categories.py`(83행)의 전문을 이 모듈의 시험과 대조한 결과다.

### `test_categories.py`

- 검사되는 것은 다음과 같다. `test_group`의 표지 부착과 알 수 없는 표지의 거부(`ValueError`, 메시지는 보지 않음). `isolation_for`의 클래스 상속과 메서드 우선. `unregistered_modules`의 두 방향 보고와 실제 저장소의 등록 완결성. `shard_for`는 `--list` 출력의 첫 칸 `'foundation'`을 통해 간접적으로 확인된다.
- 검사되지 않는 것은 다음과 같다.
  - 한 모듈이 두 조각에 중복 등록된 경우(위 시험의 비고).
  - `SHARDS`의 구체적 배정(어느 모듈이 어느 조각인지). `test_test_runner`가 `foundation`이라는 사실만 본다.
  - `LABELS`가 정확히 `('lean', 'resource')`인지. 시험은 `'lean'`과 `'resource'`가 받아들여지고 `'unit'`이 거부되는 것만 본다.
  - 조각 시간 목표(단독 120초, 전체 300초).

### `run_tests.py`

- 검사되는 것은 다음과 같다.
  - `TimedResult`: 실패의 즉시 게시(`_outcome`의 `failures/` 파일), `addSubTest`의 실패 기록, `addSkip`의 부분 시험 처리, `preserve`의 `successful` 계산.
  - `_run_suite`: 클래스 준비 건너뜀의 시험별 전개.
  - `wait_for_worker`: 제한 초과 시 종료와 보고, 새 순번에서의 제한 재설정, 정상 종료 시 `None`.
  - `_isolated`: 작업자 종료 코드와 JSON 보고의 결합.
  - `main`: 위치 ID 선택과 접두사 충돌 방지, `--list` 출력 형식, 모르는 ID의 전체 거부(반환 2).
  - `_write_json`: 시험 준비 도구로만 쓰인다.
- 검사되지 않는 것은 다음과 같다.
  - `main`의 실제 실행 경로 전체. 출력 폴더 생성과 `--output`이 비어 있지 않을 때의 거부, 조각별 루프와 `shard_seconds`, 중간과 최종 `report.json`, `counts`·`fixture_counts`·`slowest`의 계산, `Report:` 줄, 종료 코드 0과 1이 여기에 든다.
  - 실행 중 코드 변경 감지. `_edition()`의 전후 비교, `changed_during_run`, 변경 시 실패 처리가 여기에 든다.
  - `--shard`와 `--match` 필터, `--timeout`의 유한·양수 검사(`parser.error`).
  - `main`의 `SHARDS` 불일치 거부 메시지와 반환 2. `unregistered_modules` 함수만 검사된다.
  - import 오류(`loader.errors`) 시의 반환 2와 `'No tests selected; no pass was established.'` 분기.
  - `_worker`(작업자 쪽). `requested.json` 적재, `stdout.txt`·`stderr.txt` 기록, `checkpoint=True`의 진행 파일 게시(`TimedResult._progress`와 `progress-NNNNNN.json`)가 여기에 든다.
  - `_isolated`의 나머지 분기. 예외 시 `worker_error`, 시간 초과 기록에 따른 `timeout` 행, 작업자 안의 클래스 준비 건너뜀(`skipped_fixture`)의 전개, `running` 행의 제거, `TMP`·`TEMP`·`TMPDIR`을 `scratch/`로 돌리는 환경, `worker-report.json` 기록이 여기에 든다.
  - `wait_for_worker`가 `progress-*.json` 게시 파일을 읽는 경로와, 종료 뒤 10초 안에 비지 않을 때의 `termination_confirmed=False`.
  - `_exit_code`의 실제 `GetExitCodeProcess` 호출과 `_empty`의 실제 Job 상태.
  - `TimedResult`의 `addError`, `addExpectedFailure`, `addUnexpectedSuccess` 경로. 오류 행의 `failures/` 게시는 실패 경로만 검사된다.
  - `_run_suite`의 `not_run` 전개(클래스 준비나 모듈 준비의 오류)와 `setUpModule` 범위.
  - `flatten`의 중첩 스위트 전개. 실제 발견을 거치는 두 시험에서 간접적으로 쓰일 뿐이다.
- 실제 Windows Job과 실제 격리 작업자 프로세스를 만드는 시험은 없다. 모듈 docstring대로 모든 시험이 합성 시험과 합성 시계, 합성 Job을 쓴다.

## 관계

- 이 모듈은 `시험-지침.md` 1절이 설명하는 실행기 계약의 회귀 시험이다. 선택된 시험이 없으면 실패하는 규칙, 격리 실행의 시간 상한, 끝내지 못한 시험의 미실행 기록 등이 그 계약이다. 지침의 명령 표는 이 모듈이 검사하지 않는 `--shard`, `--match`, `--output`도 다룬다.
- 실제 Windows Job의 동작(프로세스 트리 소유, 종료, 자식 추적)은 `host` 조각의 `test_windows_job`과 `foundation`의 `test_owned_job_children`이 검사한다.
- 세 시험(`test_every_test_module_is_in_exactly_one_shard_and_absent_modules_are_reported`, `test_positional_ids_select_a_module_class_or_method_without_prefix_collisions`, `test_an_id_that_matches_no_test_refuses_the_whole_selection`)은 실제 시험 폴더 전체의 상태에 기댄다. 뒤의 둘은 `main`을 거치므로, 등록 불일치나 import 오류가 있으면 `main`이 다른 사유로 먼저 2를 돌려주거나 다른 메시지를 낸다. 다른 모듈의 추가, 삭제, import 오류가 이 모듈의 실패로 나타날 수 있다.
- 픽스처 모듈을 쓰지 않는다. 합성 `TestCase`와 합성 `Job`은 모두 시험 안의 지역 클래스다.
