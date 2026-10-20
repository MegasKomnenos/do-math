# test_formal

| 항목 | 값 |
|---|---|
| 조각 | `host` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_formal.py` (341행) |
| 클래스 / 테스트 | 2 / 32 |
| 시험 대상 제품 코드 | `do_math/formal.py`의 `verify_lean`(행 474–545), `_parse_evidence`(행 548–631), `_job_run`(행 277–326), `_worker`, `inspect_toolchain`(행 404–424), `toolchain_identity_errors`(행 427–461), `toolchain_errors`, `_project_identity`(행 367–401), `project_source_identity`(행 221–257), `compare_formal_results`(행 181–187), `is_lean_identifier`(행 209–214), `portable_bin`, `toolchain_root`; `do_math/trust_validation.py`의 `environment_errors`, `register_request_errors` |
| 사용하는 픽스처 모듈 | `provider_fixtures.actual_command`; `research_fixtures.trust_fixture`, `research_fixtures.trust_environment`(함수 안에서 import); `test_categories.test_group`(이름 `category`로 import) |
| 격리 표지 | 메서드 표지 `category('lean')` 6개: `T`의 `test_actual_shared_closure_traversal_matches_each_declaration_checked_alone`, `test_actual_exact_unicode_names_and_expressions_are_not_normalized`, `test_actual_prime_declarations_have_signatures_and_axioms`, `test_actual_signatures_preserve_binders_and_unicode`, `test_actual_changed_transitive_body_requires_identity_reassessment`와 `ToolchainContractTests.test_inspection_matches_actual_formal_verifier`. 클래스 표지는 없다. `resource` 표지는 없다 |
| 시작 상태 | 네 단 밖이거나 1단. 저장소·엔진을 쓰지 않는다. 합성 컴파일러(Python 스크립트)를 실제 Windows Job 안에서 돌리는 시험, 실제 Lean을 부르는 시험, 실제 Git 저장소를 만드는 시험, `_job_run`·`WindowsJob`을 대역으로 바꾼 시험, 순수 함수를 직접 부르는 시험이 섞여 있다 |

## 목적

원문에는 모듈 docstring이 없다. 시험 대상 `formal.verify_lean`의 docstring은 "Lean을 끝까지 검증한다. 검증된 결과가 해시로 남기는 의존 본문 행만 빼고 출력을 보존한다. 취소는 `should_stop`으로만 가능하다"고 밝힌다. `verify_lean`은 선언 이름 문법을 확인하고, 승인된 도구 모음 신원(`expected_toolchain`)이 있으면 실행 전에 실행 파일·검사기·Lake 프로젝트 입력을 다시 해시해 비교한 뒤, 원천 뒤에 서명(`#check`)·공리(`#print axioms`)·의존 추출기(`#do_math_dependencies`)를 붙인 파일을 `_job_run`으로 컴파일한다. `_job_run`은 Windows Job 안의 작업자 프로세스가 컴파일러를 띄우게 하고, 명시적 정지 때만 Job을 끝내며 끝냄 확인에는 2초 기한을 둔다(docstring 행 279–282). 이 모듈은 의존 증거의 모양, 실제 Lean에서의 서명·공리·유니코드 보존, Job 수명과 정지·충돌·시작 실패의 보고, 승인 신원의 실행 전 확인, 프로젝트 원천 신원, Lake 탐색 경로의 기억, 신뢰 환경 등록의 도구 모음 계약을 검사한다.

## 모듈 수준 요소

- 행 10: `scripts/` 폴더를 `sys.path` 앞에 넣는 공통 머리.
- 행 11–15: `formal` 모듈과 `compare_formal_results`, `is_lean_identifier`, `project_source_identity`, `verify_lean`, `provider_fixtures.actual_command`, `exact_content_hash`를 import한다. 행 14는 `test_categories.test_group`을 `category`라는 이름으로 들여온다. `test_`로 시작하는 이름을 모듈에 두지 않으므로 unittest가 이 함수를 시험으로 모으지 않는다.
- `_evidence_compiler(root)` (행 18–33): 합성 컴파일러를 만든다. `root/'fake.py'`를 쓰고 `[sys.executable, str(fake)]`를 돌려준다. 이 스크립트는 `--version`이면 `Lean fake`를, 아니면 미리 만든 줄들을 출력한다. 줄은 `first`와 `second` 각각의 서명 구간(`"__DO_MATH_SIGNATURE_BEGIN_<이름>__"`, `<이름> : True`, 끝 표지)과 `'<이름>' does not depend on any axioms`, 사용자 출력 `user output`, 의존 본문 행 둘(`__DO_MATH_DEPENDENCY__` 뒤 `True`는 `{'type':'Prop','value':None}`, `True.intro`는 `{'type':'True','value':None}`), 선언별 의존 행 둘(`__DO_MATH_DEPENDENCIES__` 뒤 `dependencies=['True','True.intro']`, `axioms=[]`, 증거 `{'type':'True','value':'True.intro'}`)이다. docstring은 "`first`와 `second`가 공유 폐포 `True`, `True.intro` 위에서 검증된다"고 밝힌다. 사용처는 행 37과 행 47의 두 시험이다.
- 행 341: 직접 실행하면 `unittest.main()`.

## T (행 36–308)

`unittest.TestCase`를 그대로 상속한다. 클래스 표지·설정 훅·도우미·속성이 없다. 각 시험이 자기 임시 폴더를 만든다. 실제 Lean을 부르는 다섯 시험에만 메서드 표지 `category('lean')`이 있다. 합성 컴파일러를 `_job_run`으로 돌리는 시험들은 실제 `WindowsJob`과 자식 프로세스를 쓰지만 `resource` 표지나 skip이 없다.

### `test_dependency_bodies_are_one_table_shared_by_the_declared_closures` (행 37–45)
- 성질: 여러 선언이 같은 의존 폐포를 공유하면 의존 본문은 이름마다 해시 하나인 표 하나로 저장되고, 따로 된 요약 해시나 형식 표지는 남지 않는다.
- 준비: 임시 폴더와 `_evidence_compiler`의 합성 컴파일러. 원천은 빈 문자열, 선언은 `first`, `second`.
- 실행: `verify_lean(source='', declarations=['first','second'], workspace=..., lean_command=합성 컴파일러)`. `inspect_toolchain`의 `--version` 관찰과 컴파일이 모두 실제 `_job_run`(Windows Job) 안에서 돈다.
- 단언: `status`가 `verified`다. `dependency_closure`가 두 선언 모두 `['True', 'True.intro']`다. `dependency_evidence`가 `True → exact_content_hash({'type':'Prop','value':None})`, `True.intro → exact_content_hash({'type':'True','value':None})` 두 항목과 같다. 결과 키에 `dependency_hash`와 `expression_encoding`이 없다(주석 행 44: 폐포와 본문 표가 저장되는 증거이며 둘째 요약이나 형식 표지는 두지 않는다).
- 대역: 합성 컴파일러 스크립트(실제 Lean 대신).
- 비고: 실제 외부 자원은 Windows Job과 Python 자식 프로세스다. 표지 없음.

### `test_verified_output_omits_dependency_body_rows_reduced_to_hashes` (행 47–54)
- 성질: 검증된 결과의 출력에서는 해시로 줄어든 의존 본문 행만 빠지고, 사용자 출력·선언별 의존 행·서명 표지는 남는다.
- 준비: 앞 시험과 같은 합성 컴파일러와 입력.
- 실행: 같은 `verify_lean` 호출.
- 단언: `status`가 `verified`다. `stdout`에 `__DO_MATH_DEPENDENCY__`가 없다. `user output`이 있다. `__DO_MATH_DEPENDENCIES__`가 정확히 2번 나온다. `"__DO_MATH_SIGNATURE_BEGIN_first__"`가 있다.
- 대역: 합성 컴파일러.
- 비고: `__DO_MATH_DEPENDENCIES__`가 `__DO_MATH_DEPENDENCY__`로 시작하지 않는다는 점(단수형 뒤에 `__`가 바로 옴)을 이용해 두 행을 구분한다. 실제 Windows Job과 자식 프로세스를 쓴다.

### `test_results_without_dependencies_compare_as_equivalent` (행 56–59)
- 성질: 의존이 하나도 없는(빈 의존 표) 두 결과는 같다고 비교된다.
- 준비: 1단. `axioms={'x':[]}`, `dependency_closure={'x':[]}`, `dependency_evidence={}`, `declaration_evidence`가 있는 결과 사전.
- 실행: `compare_formal_results(result, dict(result))`.
- 단언: `equivalent`가 참이다.
- 대역: 없음.
- 비고: 제품 주석(행 183)은 "빈 의존 표도 증거다"라고 밝힌다. 빈 사전이 `None`과 같이 "없음"으로 취급되지 않음을 고정한다.

### `test_actual_shared_closure_traversal_matches_each_declaration_checked_alone` (행 62–76)
- 성질: 실제 Lean에서 여러 선언을 한 번에 검사해 공유 폐포를 순회한 결과는, 각 선언을 따로 검사한 결과와 선언별로 같다.
- 준비: 원천에 `base`, `mid`(=`base`), `leaf : mid = mid`, 고전 공리를 쓰는 `em'`, `t : True`를 둔다. 선언 `leaf`, `em'`, `t`.
- 실행: 세 선언을 함께 한 번, 각각 따로 세 번 `verify_lean`(명령은 `actual_command()`).
- 단언: 함께 검사한 결과가 `verified`이고 `em'`의 공리 집합이 `{'Classical.choice', 'Quot.sound', 'propext'}`다. 따로 검사한 각 결과가 `verified`이고, `axioms`, `dependency_closure`, `declaration_evidence`, `declaration_signatures`의 그 선언 항목이 함께 검사한 결과와 같다. 함께 검사한 `dependency_evidence`를 그 선언의 폐포로 제한한 사전이 따로 검사한 `dependency_evidence` 전체와 같다.
- 대역: 없음.
- 비고: 메서드 표지 `category('lean')`. `verify_lean`을 네 번(함께 한 번, 따로 세 번) 부르고, 기대 신원이 없으므로 호출마다 `inspect_toolchain`의 `--version` 관찰과 컴파일로 실제 Lean을 두 번씩, 모두 여덟 번 띄운다. `actual_command()`는 `DO_MATH_KNOWLEDGE_TEST_LEAN`이 있으면 그 경로를, 없으면 `portable_bin(toolchain_root())/'lean.exe'`(저장소 루트 `.skill-workspace/do-math-toolchains` 아래)를 쓴다. Lean이 없을 때 건너뛰는 장치는 없으므로 `status`가 `unavailable`이 되어 실패한다(시험-지침 2절은 이 실패를 환경 원인으로 본다).

### `test_project_preparation_honors_stop_before_starting_git` (행 78–81)
- 성질: 프로젝트 원천 신원 계산은 정지 요청이 있으면 Git을 띄우기 전에 멈춘다.
- 준비: 빈 임시 폴더.
- 실행: `project_source_identity(Path(d), should_stop=lambda: True)`.
- 단언: `RuntimeError`가 나고 메시지가 정규식 `stopped`에 맞는다(제품은 `RuntimeError`의 하위 클래스 `VerificationStopped('verification stopped')`를 던진다).
- 대역: `do_math.formal.subprocess.Popen`을 `AssertionError('must stop before Git')`를 던지게 패치한다. `formal.subprocess`는 표준 `subprocess` 모듈 자체이므로, 패치 중에는 어느 곳의 `subprocess.run`·`Popen`도 자식을 띄우면 실패한다.

### `test_nested_stop_preserves_flushed_child_output` (행 84–91)
- 성질: 정지로 Job을 끝내도, 손자 프로세스가 끝내기 전에 비워(flush) 쓴 출력은 결과에 보존된다.
- 준비: 부모 명령은 Python으로 손자 Python을 `Popen`하고 10초 잔다. 손자는 `child started`를 flush 출력하고 `ready` 파일을 만든 뒤 10초 잔다.
- 실행: `formal._job_run([sys.executable, '-c', parent], root, should_stop=ready.exists)`. `ready`가 생기면 정지가 요청된다.
- 단언: 반환 튜플의 넷째 값(`stopped`)이 참이다. 둘째 값(stdout)에 `child started`가 있다.
- 대역: 없음. 정지 조건은 실제 파일의 존재다.
- 비고: 실제 Windows Job, 작업자 프로세스, 부모·손자 Python 프로세스를 쓴다. 표지·skip이 없다. 정지 뒤 Job 비움 확인에는 제품의 2초 기한이 걸린다.

### `test_compiler_crash_preserves_native_exit_code` (행 93–101)
- 성질: 컴파일러가 네이티브 예외 코드로 충돌하면 그 종료 코드가 보존되고 이유는 Lean의 거부가 아니라 컴파일러 충돌로 보고된다.
- 준비: `--version`에는 `synthetic compiler`를 출력하고, 그 밖에는 `ctypes.windll.kernel32.ExitProcess(0xC0000005)`로 끝나는 합성 컴파일러.
- 실행: `verify_lean(source='theorem good : True := True.intro', declarations=['good'], lean_command=[sys.executable, 합성])`.
- 단언: `status`가 `failed`, `exit_code`가 `0xC0000005`, `reason`이 `compiler crashed`다.
- 대역: 합성 컴파일러.
- 비고: 제품은 Windows에서 종료 코드의 최상위 비트(`0x80000000`)로 충돌을 가린다(행 540). `ctypes.windll`을 쓰므로 Windows 전용이지만 skip이 없다. 실제 Windows Job을 두 번(버전 관찰, 컴파일) 쓴다.

### `test_job_start_failure_is_not_reported_as_timeout` (행 103–106)
- 성질: Job 안에서 컴파일러를 시작하지 못하면 시간 초과가 아니라 시작 실패로 보고된다.
- 준비: 존재하지 않는 `missing-compiler.exe` 경로.
- 실행: `formal._job_run([missing], Path(d))`.
- 단언: `RuntimeError`가 나고 메시지에 `FileNotFoundError`가 있다. 작업자가 `Popen` 실패의 traceback을 stderr에 쓰고 상태를 `worker_error`로 남기면, `_job_run`이 `formal worker failed: <stderr>`로 올린다.
- 대역: 없음.
- 비고: 실제 Windows Job과 작업자 프로세스를 쓴다.

### `test_job_missing_completion_is_not_reported_as_timeout` (행 108–115)
- 성질: Job이 비었는데 작업자의 완료 상태 파일이 없으면 시간 초과가 아니라 완료 상태 누락으로 보고되고, Job은 닫힌다.
- 준비: `Mock` Job(`name='worker'`, `pid=17`, `creation_filetime=1`). `wait`는 참, `inspect`는 루트 신호됨·활성 프로세스 0·프로세스 ID 없음을 돌려준다.
- 실행: `patch('do_math.formal.WindowsJob', return_value=job)` 아래 `formal._job_run(['fixture'], Path(d))`.
- 단언: `RuntimeError`가 나고 메시지가 `completion status`에 맞는다(제품 문구 `formal worker completion status missing`). `job.close`가 정확히 한 번 불렸다.
- 대역: `WindowsJob` 패치와 `Mock` Job. 실제 프로세스는 없다.

### `test_job_termination_confirmation_has_a_fixed_deadline` (행 117–129)
- 성질: 정지 뒤 Job이 비었음을 확인하는 대기에는 고정 기한이 있어, 기한 안에 비지 않으면 끝냄 확인 실패로 보고된다.
- 준비: `Mock` Job. `inspect`는 활성 프로세스 1개(`process_ids=(18,)`)인 상태를 20번, 그다음 빈 상태를 돌려준다. 주석(행 122)은 "마지막에 비게 해 두어, 기한이 없던 옛 반복문이면 시험이 멈추지 않고 단언에서 실패하게 한다"고 밝힌다.
- 실행: `WindowsJob` 패치, `do_math.formal.time.monotonic`을 `range(100)`의 차례값으로, `do_math.formal.time.sleep`을 아무것도 안 하게 패치하고 `_job_run(['fixture'], Path(d), should_stop=lambda: True)`.
- 단언: `RuntimeError`가 나고 메시지가 `termination`에 맞는다(제품 문구 `formal Job termination could not be confirmed`). `job.terminate`와 `job.close`가 각각 한 번 불렸다.
- 대역: `WindowsJob`, `time.monotonic`(시계 주입), `time.sleep`.
- 비고: 기한은 `monotonic()+2`이므로 가짜 시계로는 둘째 확인 뒤 기한에 이른다. 실제 시간은 거의 들지 않는다.

### `test_actual_job_stop_without_completion_is_still_stopped` (행 132–135)
- 성질: 실제 Job을 정지로 끝내면, 작업자가 완료 상태를 남기지 못했어도 결과는 정지로 보고된다.
- 준비: 10초 자는 Python 명령.
- 실행: `formal._job_run([...], Path(d), should_stop=lambda: True)`.
- 단언: 반환 튜플의 넷째 값(`stopped`)이 참이다.
- 대역: 없음.
- 비고: 실제 Windows Job을 쓴다. 제품은 `stopped`이면 상태 파일을 보기 전에 `(None, stdout, stderr, True)`를 돌려준다. 앞 시험(행 108)과 대조된다.

### `test_verifier_reports_worker_failure_without_raising_or_claiming_timeout` (행 137–144)
- 성질: 컴파일 중 작업자 실패는 `verify_lean`에서 예외가 아닌 `failed` 결과로 보고되고, 이유에 원래 오류가 남으며 시간 초과라고 하지 않는다.
- 준비: `inspect_toolchain`을 `{}`로, `_job_run`을 `RuntimeError('worker completion status missing')`를 던지게 패치한다.
- 실행: `verify_lean(..., declarations=['good'], lean_command=[sys.executable])`.
- 단언: `status`가 `failed`, `reason`에 `worker completion status missing`이 들어 있고(제품은 `verification process failed: ` 뒤에 붙인다), `reason`이 `timeout`이 아니다.
- 대역: `do_math.formal.inspect_toolchain`, `do_math.formal._job_run` 패치.

### `test_pinned_project_change_is_rejected_before_process_start` (행 146–165)
- 성질: 승인 뒤 Lake 프로젝트의 매니페스트가 바뀌면 컴파일러나 Lake 환경을 띄우기 전에 "승인된 프로젝트 입력이 바뀜"으로 거부된다.
- 준비: 임시 폴더에 실제 `git init`(자식 프로세스)을 하고 그 아래 `project/lakefile.toml`(`name = "approved"`)과 실행되지 않는 `lake.exe`(바이트 `not executed`)를 둔다. 명령은 `[lake.exe, '--dir', project, 'env', 'lean']`. 기대 신원 `expected`를 손으로 짓는다: 명령, 실행 파일 경로와 해시, 검사기(`formal.__file__`)의 해시와 절대 경로, `executables`, 버전 `fixture`, 버전 종료 0, 프로젝트(`lakefile.toml` 해시, 그 시점의 `project_source_identity(project)`, 빈 탐색 경로). 그 뒤 매니페스트를 `name = "changed"`로 바꾼다.
- 실행: `_job_run`을 `AssertionError('changed project must not start the compiler')`로 패치하고 `verify_lean(..., lean_command=command, expected_toolchain=expected)`.
- 단언: `status`가 `rejected`, `reason`이 정확히 `approved project inputs changed before execution`이다.
- 대역: `_job_run` 패치(불리면 실패).
- 비고: 주석(행 160)은 "Git은 직접 돈다. Job이 있다면 컴파일러나 Lake 환경뿐이다"라고 밝힌다. 곧 `project_source_identity`의 Git 호출은 실제로 돌고, Job을 띄우는 경로만 막힌다. 제품은 신원 오류가 `['approved project inputs changed']` 하나일 때만 이 이유 문구를 쓰므로(행 509–510), 실행 파일·검사기 해시가 모두 맞았다는 것도 함께 고정된다.

### `test_actual_exact_unicode_names_and_expressions_are_not_normalized` (행 168–178)
- 성질: 실제 Lean 검증은 유니코드 선언 이름과 식을 정규화하지 않고, 원천 해시는 원천 바이트 그대로의 해시다.
- 준비: 선언 이름 `'K'`(켈빈 기호 K)와 라틴 `K`. 원천은 `Ω`(옴 기호)을 결속 변수로 쓰는 정리, CRLF 줄끝, 결합 문자가 든 주석 `é`을 담는다.
- 실행: `verify_lean(source, names, lean_command=actual_command())`.
- 단언: `status`가 `verified`다(실패 시 `status`, `reason`, `stderr`만 보여 줌). `source_sha256`이 `hashlib.sha256(source.encode())`와 같다. `declarations`가 입력 목록과 같다. `declaration_evidence`와 `declaration_signatures`의 키 집합이 두 이름과 같다(NFKC 정규화였다면 두 이름이 하나로 합쳐진다). 켈빈 선언의 서명에 `Ω`이 남아 있다.
- 대역: 없음.
- 비고: 메서드 표지 `category('lean')`. 실제 Lean. Lean이 없으면 skip 없이 실패한다.

### `test_changed_approved_executable_is_rejected_before_version_execution` (행 180–191)
- 성질: 승인된 실행 파일의 바이트가 바뀌면 버전 관찰을 포함한 어떤 실행도 하기 전에 거부된다.
- 준비: `_job_run`을 `(0, 'fixture version', '', False)`를 돌려주게 패치한다. 합성 `synthetic-lean.exe`를 쓰고 `formal.inspect_toolchain([exe], d)`로 승인 신원을 관찰한 뒤 `run.reset_mock()`으로 호출 기록을 지우고 실행 파일 바이트를 바꾼다.
- 실행: `verify_lean(..., lean_command=[exe], expected_toolchain=approved)`.
- 단언: `status`가 `rejected`이고, `_job_run`이 한 번도 불리지 않았다.
- 대역: `_job_run` 패치.
- 비고: 이유 문구는 단언하지 않는다(제품은 `approved toolchain changed before execution`을 쓴다).

### `test_executable_change_during_run_is_left_to_the_next_identity_check` (행 192–208)
- 성질: 검증기는 승인 신원을 컴파일 전에 한 번만 확인하며, 컴파일 도중의 실행 파일 변경은 이 검증에서 다시 관찰하지 않고 다음 신원 확인이 찾는다.
- 준비: 합성 실행 파일과, `_job_run` 패치 아래 관찰한 기대 신원. 이어서 `_job_run`을 함수 `run`으로 바꾼다. `run`은 `--version`이면 버전을, 아니면 실행 파일 바이트를 바꾸고 빈 출력 `(0, '', '', False)`를 돌려준다.
- 실행: `verify_lean(..., expected_toolchain=expected)`, 이어서 `formal.toolchain_identity_errors(expected)`.
- 단언: 검증 결과 `(status, reason)`이 `('failed', 'signature output missing')`이다(신원 거부가 아니라 빈 출력의 파싱 실패). 신원 확인 결과가 정확히 `['approved toolchain file changed: <실행 파일의 resolve 경로>']` 한 줄이다.
- 대역: `_job_run` 패치 두 번.
- 비고: 주석(행 193–194)은 "컴파일 중의 변경은 게시 관문이나 다음 형식 검사가 찾는다"고 밝힌다. 실행 파일은 `executable`과 `executables` 두 곳에 기록되지만 제품이 같은 문구를 한 번만 넣으므로 오류가 한 줄이다.

### `test_path_lookup_spelling_matches_the_inspected_executable` (행 209–218)
- 성질: 대소문자가 다른 철자로 준 실행 파일은 실제 파일의 철자로 관찰되고, 같은 명령으로 한 검증은 신원 불일치로 거부되지 않는다.
- 준비: `os.name != 'nt'`이면 `skipTest('Windows PATHEXT lookup keeps the spelling of its argument')`. `_job_run`을 버전 반환으로 패치하고, `synthetic-lean.exe`를 만든 뒤 명령은 `SYNTHETIC-LEAN.EXE`로 준다.
- 실행: `formal.inspect_toolchain(command, root)`, 이어서 `verify_lean(..., expected_toolchain=observed)`.
- 단언: 관찰한 `executable`이 소문자 실제 경로다. 검증 결과가 `('failed', 'signature output missing')`이다. 곧 `approved toolchain changed before execution`으로 거부되지 않고 컴파일 단계(패치된 `_job_run`이 버전 문자열을 돌려줌)까지 갔다.
- 대역: `_job_run` 패치.
- 비고: skip은 메서드 안의 `self.skipTest`다.

### `test_prime_names_keep_the_existing_identifier_boundary` (행 219–223)
- 성질: 선언 이름 문법은 이름 조각 끝의 프라임(`'`)을 받아들이되, 식별자 경계를 넘는 문자열은 거부한다.
- 준비: 1단.
- 실행: `is_lean_identifier`를 여러 값에.
- 단언: `sumTo_succ'`, `N.foo''`, `α'`, `N'.foo'`는 참이다. `'`, `N.'`, `x'; #eval 1`, `x' y`, 줄바꿈이 든 `x\ny`, 가운데 프라임 `x'y`, `x"`, `x()`, `.x`, `x.`는 거짓이다. 실패 메시지는 값 자체다.
- 대역: 없음.
- 비고: `subTest` 없는 반복이므로 첫 실패에서 멈춘다.

### `test_actual_prime_declarations_have_signatures_and_axioms` (행 225–234)
- 성질: 실제 Lean에서 프라임이 든 선언 이름(이름공간 안의 것 포함)도 서명·공리·선언 증거·의존 증거가 빠짐없이 나온다.
- 준비: `sumTo_succ'`, 이름공간 `N` 안의 `foo''`, `α'`를 정의한 원천.
- 실행: `verify_lean(..., lean_command=actual_command())`.
- 단언: `status`가 `verified`다. `declaration_signatures`, `axioms`, `declaration_evidence`의 키 집합이 세 이름과 같다. `dependency_evidence`의 키 집합이 세 선언 폐포의 합집합과 같다.
- 대역: 없음.
- 비고: 메서드 표지 `category('lean')`. 실제 Lean. Lean이 없으면 skip 없이 실패한다.

### `test_invalid_declaration_rejected` (행 235–236)
- 성질: 문법에 맞지 않는 선언 이름은 거부된다.
- 준비: 1단에 준함. 빈 원천과 선언 `bad;`.
- 실행: `verify_lean(source='', declarations=['bad;'], workspace=...)`.
- 단언: `status`가 `rejected`다(제품 이유 `invalid declaration`, 미단언).
- 대역: 없음. 명령 해석 전에 끝나므로 프로세스를 띄우지 않는다.

### `test_empty_declaration_list_is_rejected` (행 237–238)
- 성질: 감사할 선언이 없으면 원천에 `sorry`가 있든 없든 거부된다.
- 준비: `theorem foo : False := sorry` 원천과 빈 선언 목록.
- 실행: `verify_lean(...)`.
- 단언: `status`가 `rejected`다(제품 이유 `no declaration to audit`, 미단언).
- 대역: 없음. 프로세스를 띄우지 않는다.

### `test_missing_lean_unavailable` (행 239–240)
- 성질: 지정한 Lean 명령이 없으면 결과는 `unavailable`이다.
- 준비: 명령 `['no-such-lean']`.
- 실행: `verify_lean(source='', declarations=['X'], lean_command=['no-such-lean'])`.
- 단언: `status`가 `unavailable`이다.
- 대역: 없음.
- 비고: `inspect_toolchain`의 `resolve(strict=True)`가 `OSError`를 내고, 제품은 이를 준비 단계의 `unavailable`로 돌려준다. 프로세스는 띄우지 않는다.

### `test_fake_lean_rejects_real_sorry_even_when_source_prints_allowed_text` (행 241–245)
- 성질: 공리 출력에 `sorryAx`가 있으면, 같은 선언에 대해 허용된 공리 줄이 함께 있어도 거부된다.
- 준비: 합성 컴파일러는 `X`의 서명 구간과 `'X' depends on axioms: [Classical.choice]`, `'X' depends on axioms: [sorryAx]` 두 줄을 출력한다. 원천은 허용 공리 문구를 `#eval`로 찍는 한 줄이다.
- 실행: `verify_lean(..., declarations=['X'], lean_command=[sys.executable, fake])`.
- 단언: `status`가 `rejected`이고 `axioms['X']`에 `sorryAx`가 있다.
- 대역: 합성 컴파일러.
- 비고: 합성 컴파일러는 원천을 읽지 않으므로, 원천이 찍는 문구는 실제로 출력에 나타나지 않는다. 이 시험이 실제로 확인하는 것은 한 선언의 공리 줄 여러 개가 합쳐지고 `sorryAx`가 `forbidden_axioms`에 걸린다는 것이다. 공리 거부가 의존 행 확인보다 앞서므로 의존 행이 없어도 `rejected`가 된다. 실제 Windows Job을 쓴다.

### `test_missing_axiom_output_fails` (행 246–249)
- 성질: 컴파일러가 감사 출력을 내지 않으면 검증은 `failed`다.
- 준비: `--version`에만 `v`를 출력하고 그 밖에는 아무것도 출력하지 않는 합성 컴파일러.
- 실행: `verify_lean(source='', declarations=['X'], lean_command=[sys.executable, fake])`.
- 단언: `status`가 `failed`다.
- 대역: 합성 컴파일러.
- 비고: 이름은 공리 출력 누락을 말하지만, 제품은 서명 확인을 먼저 하므로 실제 이유는 `signature output missing`이다. 시험은 이유를 단언하지 않으므로 `axiom output missing` 경로는 따로 고정되지 않는다. 실제 Windows Job을 쓴다.

### `test_actual_signatures_preserve_binders_and_unicode` (행 251–254)
- 성질: 실제 Lean에서 얻은 서명은 결속자 표기와 유니코드 문자를 보존한다.
- 준비: `good (n : Nat) : n = n`과 `unicodeGood : ∀ α : Type, α → α`.
- 실행: `verify_lean(..., lean_command=actual_command())`.
- 단언: `status`가 `verified`이고, `good`의 서명에 `(n : Nat)`이, `unicodeGood`의 서명에 `α`가 있다.
- 대역: 없음.
- 비고: 메서드 표지 `category('lean')`. 실제 Lean. Lean이 없으면 skip 없이 실패한다.

### `test_actual_changed_transitive_body_requires_identity_reassessment` (행 256–268)
- 성질: 선언 자체는 같아도 전이 의존의 본문이 바뀌면 두 결과의 비교가 신원 재평가를 요구하고, 같은 결과끼리는 요구하지 않는다.
- 준비: `base`의 값만 1과 2로 다른 두 원천(`mid := base`, `leaf : mid = mid`).
- 실행: 두 원천을 실제 Lean으로 `verify_lean`하고 `compare_formal_results(*results)`, 그리고 첫 결과끼리 비교.
- 단언: 두 결과가 `verified`이고 `leaf`의 폐포에 `base`가 있다. 비교의 `requires_identity_review`가 참이고 `changed`에 `dependency_evidence`가 있다. 첫 결과끼리 비교하면 `requires_identity_review`가 거짓이다.
- 대역: 없음.
- 비고: 메서드 표지 `category('lean')`. `verify_lean`을 두 번 부르고, 호출마다 버전 관찰과 컴파일로 실제 Lean을 두 번씩, 모두 네 번 띄운다. Lean이 없으면 skip 없이 실패한다.

### `test_project_source_identity_excludes_unrelated_and_tracks_project_changes` (행 269–275)
- 성질: 프로젝트 원천 신원은 `.lake` 안의 의존 원천과 프로젝트 밖의 변경에 흔들리지 않고, 프로젝트 파일의 변경은 반영한다.
- 준비: 임시 폴더에 `project/Main.lean`(`def x := 1`)과 `unrelated/x`를 두고 실제 Git으로 `init`, `add .`, `commit`한다.
- 실행: 아래 번호 단계에 적은 호출을 차례로 한다.
- 단언: 각 단계의 단언은 아래 번호 단계에 함께 적는다. 단계 목록:
  1. 처음 신원 `before`를 잰다.
  2. `project/.lake/packages/dep/Dep.lean`을 만든 뒤 신원이 `before`와 같다.
  3. `unrelated/x`를 바꿔 커밋한 뒤에도 신원이 `before`와 같다(`HEAD:project` 트리가 같음).
  4. `Main.lean`을 `def x := 2`로 바꾸면 신원이 `before`와 다르다(작업 트리 diff 해시가 바뀜).
- 대역: 없음.
- 비고: 시험과 제품 모두 실제 Git 자식 프로세스를 여러 번 띄운다. 제품의 `_GIT_ROOTS`는 프로세스 안 기억이지만 임시 경로가 매번 새로우므로 영향이 없다.

### `test_stop_is_not_a_math_failure` (행 276–279)
- 성질: 정지 요청은 수학적 실패가 아니라 `stopped` 결과로 보고된다.
- 준비: `--version`에 `v`를 출력하고 그 밖에는 10초 자는 합성 컴파일러.
- 실행: `verify_lean(..., should_stop=lambda: True)`.
- 단언: `status`가 `stopped`다.
- 대역: 합성 컴파일러와 항상 참인 `should_stop`.
- 비고: `should_stop`이 처음부터 참이므로 제품은 준비 단계의 첫 `_check_stop`에서 멈추고 `phase='preparation'`인 `stopped`를 돌려준다. 합성 컴파일러는 실제로 실행되지 않는다. 컴파일 중 정지 경로는 이 시험이 아니라 `_job_run` 시험들(행 84, 행 132)이 본다.

### `test_untracked_project_does_not_report_unresolved_git_expression_as_hash` (행 280–291)
- 성질: Git 저장소 안에 있지만 추적되지 않는 프로젝트는 트리 해시 자리에 풀리지 않은 Git 식을 넣지 않고 `None`을 두며, 추적되지 않은 입력 파일을 따로 센다.
- 준비: 실제 Git으로 `tracked.txt`만 커밋한 저장소와, 그 안의 추적되지 않은 `untracked/lakefile.toml`.
- 실행: `project_source_identity(project)`.
- 단언: `git_tree`가 `None`이다. `untracked_file_count`가 1이다. `untracked_sha256`이 16진 64자다.
- 대역: 없음.
- 비고: 제품은 `git rev-parse --verify HEAD:untracked`가 실패하면 `None`을 둔다(행 231–233). 실제 Git 자식 프로세스를 쓴다.

### `test_lake_search_paths_are_observed_once_per_unchanged_project_input` (행 292–308)
- 성질: Lake 환경의 탐색 경로 관찰은 프로젝트 입력이 바뀌지 않는 한 프로세스당 한 번이고, 입력이 바뀌면 다시 관찰한다.
- 준비: `project/lake-manifest.json`(`{}`)과 합성 `lake.exe`. 명령 `[lake.exe, '--dir', project, 'env', 'lean']`.
- 실행: `formal.project_source_identity`를 `{'root': project}`로, `formal._job_run`을 `(0, 관찰 JSON, '', False)`로 패치하고 `formal._project_identity(command, workspace=root)`를 두 번 부른다. 매니페스트를 `{"packages":[]}`로 바꾼 뒤 한 번 더 부른다.
- 단언: 두 번째 결과가 첫 결과와 같다. 그때까지 `_job_run` 호출이 1회다(메시지 `unchanged inputs reuse the observed search paths`). 매니페스트를 바꾼 뒤 호출이 2회다(메시지 `a changed project input is observed again`).
- 대역: `project_source_identity`, `_job_run` 패치.
- 비고: 제품 기억 `_SEARCH_PATHS`의 키는 Lake 명령 앞부분, 프로젝트 신원, Lake 실행 파일의 해시다(행 385–389). 함수 안에서 `patch`, `json`, `formal`을 다시 import한다.

## ToolchainContractTests (행 311–338)

`unittest.TestCase`를 그대로 상속한다. 클래스 표지·훅·도우미가 없다. 한 메서드에만 `category('lean')`이 있다.

### `test_inspection_matches_actual_formal_verifier` (행 313–325)
- 성질: 실제 이식형 Lean에 대한 도구 모음 관찰은 구조 계약을 만족하고, 그 관찰을 승인 신원으로 넘긴 실제 검증은 통과하며 결과의 도구 모음이 관찰과 같다.
- 준비: 명령 `[portable_bin(toolchain_root())/'lean.exe']`. 파일이 없으면 `skipTest('portable Lean is not installed')`.
- 실행: `inspect_toolchain(command, root)`, `toolchain_errors(observed)`, `verify_lean(source='theorem repair_probe : True := True.intro', declarations=['repair_probe'], lean_command=command, expected_toolchain=observed)`.
- 단언: `toolchain_errors`가 빈 목록이다. 검증 `status`가 `verified`이고 `toolchain`이 관찰과 같다.
- 대역: 없음.
- 비고: 메서드 표지 `category('lean')`. 실제 Lean. 이 시험은 `actual_command()`가 아니라 `toolchain_root()`를 직접 쓰므로 `DO_MATH_KNOWLEDGE_TEST_LEAN`의 영향을 받지 않는다. 대신 Lean이 없으면 건너뛴다. worktree에는 `.skill-workspace`가 없으므로 이 시험은 worktree에서 늘 건너뛰어진다.

### `test_registration_rejects_the_incomplete_document_toolchain` (행 327–338)
- 성질: 도구 모음 기록에 검사기 해시(`verifier_sha256`)가 빠진 신뢰 환경은 등록 요청 검사와 환경 검사에서 모두 거부된다.
- 준비: `research_fixtures.trust_fixture(Path(directory), ['test-lean'])`로 합성 설치·도구 모음 기록·등록 요청을 만들고, `trust_environment(request, source_ref='UC-adopt')`로 환경과 결속을 얻는다.
- 실행: 먼저 `environment_errors(environment, binding)`, 이어 환경과 요청의 `toolchain`에서 `verifier_sha256`을 지우고 `environment_errors`와 `register_request_errors(request)`.
- 단언: 지우기 전 환경 오류가 빈 목록이다. 요청 오류에 정확한 문구 `toolchain.verifier_sha256 is missing`이 있다. 지운 뒤 환경 오류 가운데 `verifier_sha256`을 포함한 것이 있다.
- 대역: 없음. 합성 설치 파일은 픽스처가 만든다.
- 비고: 이름의 "document toolchain"은 문서에 적힌(기록된) 도구 모음을 가리킨다. 등록 요청 쪽 문구는 `formal.toolchain_errors`의 `'toolchain.' + key + ' is missing'`이다.

## 관계

- 같은 제품 기능을 다른 층에서 보는 모듈: `test_formal_runtime`은 `_job_run`·`WindowsJob`의 실제 수명(프로세스 트리, 자원 사용)을 `resource` 표지 아래에서 본다. `test_lean_preview`는 작업자 미리보기(`extract_evidence=False`) 경로를, `test_formal_engine`(`lifecycle` 조각)은 엔진이 형식 검사를 부르고 결과를 기록하는 경로를, `test_formal_input_manifest`와 `test_trust_continuation`(`foundation` 조각)은 입력 매니페스트와 신뢰 환경의 도메인 규칙을 본다. `test_windows_job`은 `WindowsJob` 자체의 커널 동작을 본다.
- 픽스처 의존: `provider_fixtures.actual_command`(실제 Lean 경로), `research_fixtures.trust_fixture`와 `trust_environment`(마지막 시험).
- 이 모듈에만 있는 도우미: `_evidence_compiler`.
- 반복되는 기법: 합성 컴파일러를 Python 스크립트로 써서 `[sys.executable, fake.py]`를 Lean 명령으로 넘기는 방식(행 18, 93, 241, 246, 276). 이 경우 버전 관찰과 컴파일이 모두 실제 `_job_run`과 `WindowsJob`을 거친다. 반면 `_job_run` 자체를 패치해 프로세스를 없애는 방식(행 137, 146, 180, 192, 209, 292)과 `WindowsJob`만 `Mock`으로 바꾸는 방식(행 108, 117)이 있다.
- 격리 표지의 적용 범위: 실제 Lean을 부르는 여섯 시험에만 `lean` 표지가 있다. 합성 컴파일러나 Python 명령으로 실제 Windows Job을 띄우는 시험(행 37, 47, 84, 93, 103, 132, 241, 246)에는 `resource` 표지가 없어, `run_tests.py`의 Job 격리와 시간 상한 없이 돈다.
- 겹침과 보완: 정지는 준비 단계(행 78, 276), 손자 출력 보존(행 84), 완료 상태 없는 실제 정지(행 132), 끝냄 확인 기한(행 117)으로 나뉜다. 승인 신원 확인은 매니페스트 변경(행 146), 실행 파일 변경(행 180), 실행 중 변경(행 192), 철자 차이(행 209)로 나뉜다.
