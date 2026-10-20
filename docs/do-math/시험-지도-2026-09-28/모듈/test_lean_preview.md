# test_lean_preview

| 항목 | 값 |
|---|---|
| 조각 | `host` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_lean_preview.py` (165행) |
| 클래스 / 테스트 | 1 / 6 |
| 시험 대상 제품 코드 | `do_math/submission.py`의 `install_tools`(행 1438 이하, 작업자 도구 `input/tools/check_lean.py`와 `submission-support.zip` 설치, `formal_verifier.preview` 명령 작성); `do_math/formal_preview.py`의 `main`(행 18–50), `PREVIEW_FIELDS`(행 14–15); `do_math/formal.py`의 `verify_lean`(`extract_evidence=False`), `toolchain_identity_errors`; `do_math/contracts.schema_for` |
| 사용하는 픽스처 모듈 | `provider_fixtures.actual_command`; `test_categories.test_group`(이름 `category`) |
| 격리 표지 | 메서드 표지 `category('lean')` 1개: `test_actual_standalone_preview_checks_code_axioms_and_stop`. 클래스 표지 없음 |
| 시작 상태 | 네 단 밖. 임시 작업 공간에 `install_tools`로 작업자 도구를 설치하고, 작업자가 하듯 미리보기 명령을 실제 자식 프로세스로 실행한다. 저장소·엔진은 쓰지 않는다 |

## 목적

모듈 docstring은 "생산자의 독립 컴파일러 명령은 피드백을 줄 뿐 권위를 주지 않는다"고 밝힌다. 제품 `formal_preview.py`의 docstring은 "공급된 검증기 판본을 쓰는, 권위 없는 작업자 로컬 피드백"이다. `install_tools`는 작업자 작업 공간에 중앙 상태가 아닌 코드 판본(엔진 모듈을 뺀 `do_math` 묶음 `submission-support.zip`)과 도구 스크립트를 복사하고, 입력 문맥에 `formal_verifier` 절이 있으면 미리보기 명령(`[console_python(), '-B', 'input/tools/check_lean.py']`)을 적는다. 미리보기는 정지 요청을 컴파일 전에 확인하고, `verify_lean`을 의존 증거 추출 없이(`extract_evidence=False`) 돌린 뒤 `PREVIEW_FIELDS`에 든 필드만 `authoritative=False`와 함께 출력한다. 이 모듈은 그 정지 우선, pythonw 아래의 콘솔 해석기 선택, 의존 추출 미부착과 출력 필드 제한, 도구·작업자의 모듈 적재 범위, 압축 파일에서 적재한 검사기의 신원, 실제 Lean 미리보기의 판정을 검사한다.

## 모듈 수준 요소

- 행 10: `scripts/` 폴더를 `sys.path` 앞에 넣는 공통 머리.
- 행 11–14: `actual_command`, `test_group`(이름 `category`), `install_tools`, `schema_for`를 import한다.
- 행 164–165: 직접 실행하면 `unittest.main()`.

## LeanPreviewTests (행 17–161)

`unittest.TestCase`를 그대로 상속한다. 클래스 표지·설정 훅·도우미·속성이 없다. 각 시험이 임시 작업 공간에 문맥 사전(`action.role='research_work'`, `snapshot='fixed'`, `formal_verifier`)을 만들고 `install_tools(workspace, context, schema_for('research_work'), 1000000)`을 부른다. `install_tools`는 문맥 사전에 `preview`를 직접 써 넣는다.

### `test_control_stop_is_consumed_before_any_compiler_start` (행 18–30)
- 성질: 작업 공간에 정지 요청이 있으면 미리보기는 컴파일러를 시작하기 전에 `stopped`로 끝난다.
- 준비: 존재하지 않는 명령 `definitely-missing-lean`을 컴파일러로 둔 문맥, 도구 설치, `draft.lean`, `.control/stop-request.json`.
- 실행: 미리보기 명령에 `--source draft.lean --declaration good`을 붙여 작업 공간에서 `subprocess.run`(`timeout=30`).
- 단언: 출력 JSON의 `status`가 `stopped`다.
- 대역: 없는 컴파일러 명령. 컴파일러가 시작되었다면 `unavailable`이 되었을 것이므로, `stopped`는 정지 확인이 명령 해석보다 앞섬을 보인다.
- 비고: 실제 자식 Python(미리보기 도구)을 띄운다.

### `test_worker_commands_use_the_console_interpreter_when_the_engine_runs_windowless` (행 32–48)
- 성질: 엔진이 창 없는 `pythonw.exe`로 돌아도 작업자에게 주는 도구 명령은 같은 폴더의 콘솔 해석기 `python.exe`를 쓴다.
- 준비: 임시 `Python` 폴더에 빈 `python.exe`, `pythonw.exe` 파일을 만든다. 없는 컴파일러를 둔 문맥.
- 실행: `patch.object(sys, 'executable', pythonw 경로)` 아래 `install_tools`.
- 단언: 반환된 제출 계약의 `command[0]`과 문맥의 `formal_verifier.preview.command[0]`이 모두 가짜 `python.exe` 경로다.
- 대역: `sys.executable` 패치와 빈 해석기 파일.
- 비고: docstring은 "예약된 엔진은 pythonw.exe 아래에서 돌고, 작업자 셸은 그 출력을 읽을 수 없다"고 밝힌다. 프로세스를 띄우지 않는다.

### `test_preview_attaches_no_dependency_extraction_and_prints_only_worker_fields` (행 50–75)
- 성질: 미리보기는 검사 파일에 의존 추출기를 붙이지 않고, 작업자용 필드만 출력한다.
- 준비: 합성 컴파일러 `compiler.py`. `--version`이면 `Lean fake`를 출력하고, 검사 파일에 `#do_math_dependencies`가 있으면 `dependency extraction attached`를 출력하며, 이어 `good`의 서명 구간과 `'good' does not depend on any axioms`를 출력한다. 문맥의 컴파일러는 `[sys.executable, compiler.py]`다.
- 실행: 도구 설치, `draft.lean` 작성, 미리보기 명령을 `subprocess.run`(`timeout=60`).
- 단언: 출력의 `status`가 `verified`다. `stdout` 필드에 `dependency extraction attached`가 없다. 출력 키 집합이 `formal_preview.PREVIEW_FIELDS`의 부분집합이다. `declaration_signatures`가 `{'good': 'good : True'}`, `axioms`가 `{'good': []}`다.
- 대역: 합성 컴파일러.
- 비고: 미리보기 도구 자식 프로세스 안에서 `verify_lean`이 실제 `_job_run`(Windows Job)으로 합성 컴파일러를 두 번(버전, 검사) 돌린다. 표지가 없다.

### `test_preview_tool_and_compiler_worker_skip_unneeded_modules` (행 77–94)
- 성질: 미리보기 도구는 제출 검사기를 적재하지 않고, 컴파일러만 띄우는 Job 작업자(`do_math.formal`)는 상태 저장소나 스키마 라이브러리를 적재하지 않는다.
- 준비: 도구 설치(없는 컴파일러 문맥).
- 실행: `do_math.formal_preview`와 `do_math.formal` 각각을 `submission-support.zip`을 `sys.path` 앞에 둔 새 Python(`-B`)에서 import하고 `sys.modules`의 이름을 출력한다(`timeout=60`).
- 단언: 두 실행의 종료 코드가 0이다. `formal_preview` 쪽 적재 목록에 `do_math.submission`이 없다. `formal` 쪽 적재 목록에 `do_math.repository`와 `jsonschema`가 없다.
- 대역: 없음.
- 비고: docstring은 "도구는 제출 검사기 없이 입력을 읽고, 컴파일러만 띄우는 Job 작업자는 상태 저장소나 스키마 라이브러리를 적재하지 않는다"고 밝힌다. 제품 `_parse_evidence`가 `exact_content_hash`를 함수 안에서 import하는 이유(주석 "Job workers import this module only to start the compiler")와 맞닿아 있다. 실제 자식 Python 두 개.

### `test_preview_checker_loaded_from_the_support_archive_is_the_approved_checker` (행 96–120)
- 성질: 작업자가 압축 파일에서 적재한 `formal.py`는 경로가 승인 경로와 달라도 같은 바이트이므로 같은 검사기이며 신원 확인을 통과한다.
- 준비: 승인 신원을 손으로 짓는다. 실행 파일은 현재 Python(해시 포함), 명령은 `[python]`, 검사기 해시와 경로는 설치된 `formal.py`의 것, `executables`는 빈 사전, `project`는 `None`. 이 신원을 `expected_toolchain`으로 둔 문맥으로 도구를 설치한다.
- 실행: 압축 파일을 `sys.path` 앞에 둔 새 Python에서 `formal`을 import하고 `formal.__file__`과 `toolchain_identity_errors(승인 신원)`을 JSON으로 출력한다(`timeout=60`).
- 단언: 출력이 있다(없으면 stderr 표시). `file`에 `submission-support.zip`이 들어 있다(압축 파일에서 적재됨). `errors`가 빈 목록이다.
- 대역: 없음.
- 비고: docstring이 의도를 밝힌다. 제품의 `_RUNNING_CHECKER_SHA256`은 모듈 로더에서 읽은 바이트의 해시이므로(`formal.py` 행 18–21 주석) 압축 파일 안에서도 같다. 실제 자식 Python.

### `test_actual_standalone_preview_checks_code_axioms_and_stop` (행 123–161)
- 성질: 실제 Lean으로 도는 독립 미리보기는 증명을 판정하고 공리를 보고하되 권위가 없음을 밝히고, 의존 증거를 만들지 않으며, 중앙 기록 파일을 만들지 않고, 정지 요청에 `stopped`로 답한다.
- 준비: `actual_command()`를 컴파일러로, 허용 공리 `propext`, `Classical.choice`, `Quot.sound`를 둔 문맥으로 도구를 설치한다.
- 실행: 여섯 원천을 차례로 `draft.lean`에 바이트로 쓰고 미리보기 명령을 실행한다(`CREATE_NO_WINDOW`, `timeout=None`). 끝으로 `.control/stop-request.json`을 쓰고 한 번 더 실행한다(`timeout=30`).
- 단언:
  - `preview`가 `None`이 아니다(메시지 `worker must receive the compiler preview command`).
  - 원천별 기대 `status`: `by trivial`은 `verified`, CRLF와 들여쓰기가 든 같은 증명은 `verified`, `False := by sorry`는 `rejected`(금지 공리 `sorryAx`), `False := by trivial`은 `failed`(Lean 거부), 프라임 이름 `good'`은 `verified`, 켈빈 기호 이름과 옴 기호 결속자·결합 문자 주석이 든 원천은 `verified`.
  - 모든 경우: `source_sha256`이 원천 UTF-8 바이트의 SHA-256이다. `authoritative`가 거짓이다. `toolchain.configured_command`가 명령과 같다. `input_snapshot`이 `fixed`다. `dependency_closure`, `dependency_evidence`, `declaration_evidence` 키가 없다. `stdout`에 `__DO_MATH_DEPENDENC`가 없다.
  - `verified`인 경우: `declaration_signatures`에 그 이름이 있고 `axioms[name]`이 빈 목록이다.
  - 작업 공간에 `formal_results`, `expositions`, `identity_assessments`, `assessment_uses` 폴더가 없다.
  - 정지 요청 뒤 `status`가 `stopped`다.
- 대역: 없음.
- 비고: 메서드 표지 `category('lean')`. 여섯 원천마다 미리보기 도구 자식 프로세스 안의 `verify_lean`이 기대 신원 없이 돌므로, 버전 관찰과 검사로 실제 Lean을 두 번씩, 모두 열두 번 Windows Job 안에서 띄운다. 마지막 정지 요청 실행은 컴파일 전에 끝나 Lean을 띄우지 않는다. `assertIsNotNone(command, 'this integration test requires the real compiler')`는 `actual_command()`가 늘 목록을 돌려주므로 항상 통과한다. Lean이 없으면 건너뛰지 않고, 미리보기가 `unavailable`을 돌려 첫 기대 `verified`에서 실패한다(시험-지침 2절의 환경 원인 실패).

## 관계

- 같은 제품 기능을 다른 층에서 보는 모듈: `test_formal`은 `verify_lean`의 중앙 판정(의존 추출 포함)을, `test_formal_runtime`은 추출기 출력 모양을, `test_submission_tools`(`review` 조각)는 `install_tools`가 설치하는 제출 도구를, `test_role_input`(`lifecycle` 조각)은 역할 입력의 포장을 본다. `test_background_processes`와 `test_schedule_pythonw`는 pythonw 아래 자식 실행의 다른 측면을 본다.
- 픽스처 의존: `provider_fixtures.actual_command` 하나(마지막 시험).
- 이 모듈에만 있는 도우미: 없음. 문맥 사전과 `install_tools` 호출이 시험마다 반복된다.
- 반복 기법: 작업자처럼 설치된 명령을 작업 공간을 `cwd`로 실제 자식 프로세스로 돌리고 표준 출력의 JSON을 읽는다. 정지 요청은 파일(`.control/stop-request.json`)로 준다. 없는 컴파일러 명령(`definitely-missing-lean`)으로 "컴파일러가 불리지 않음"을 결과 상태로 가린다.
