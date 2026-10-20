# test_probe_cli

| 항목 | 값 |
|---|---|
| 조각 | `host` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_probe_cli.py` (56행) |
| 클래스 / 테스트 | 1 / 3 |
| 시험 대상 제품 코드 | 스크립트 `scripts/probe_cli.py`의 `main`(행 95 이하: 인자 검사와 `parser.error`, 출력 폴더 생성, `report.json`의 `sources`), `run_case`(행 17 이하: 모델 이름의 제공자 접두 부여, 행 67) |
| 사용하는 픽스처 모듈 | 없음 |
| 격리 표지 | 없음 |
| 시작 상태 | 1단에 준하는 직접 호출. `probe_cli`를 프로세스 안에서 import하고 `run_case`나 `ModelRunner`를 대역으로 바꿔 모델을 부르지 않는다 |

## 목적

모듈 docstring은 "모델을 결코 부르지 않는 probe_cli 인자 검사"라고 밝힌다. 제품 `probe_cli.py`의 docstring은 "설치된 스키마 검사와, 제공자를 명시한 대표적인 로컬 CLI 탐침"이다. 탐침은 실제 제공자 CLI를 불러 구조화 출력·파일·백그라운드·정지 같은 경우를 확인하고, 결과 보고에 구현 모듈의 해시를 남긴다. 이 모듈은 Claude 전용 경우·옵션이 Codex 제공자에서 준비 작업 전에 거부되는지, Claude 모델 이름이 제공자 접두를 한 번만 달고 러너에 닿는지, 보고서가 모든 구현 모듈을 해시하는지를 검사한다.

## 모듈 수준 요소

- 행 1–4: 표준 라이브러리만 import한다. 모듈 수준에서 `sys.path`를 고치지 않는다. 세 시험이 각각 함수 안에서 `scripts/`를 `sys.path` 앞에 넣고 `import probe_cli`한다(`probe_cli`가 `from do_math...`로 시작하므로).
- 행 55–56: 직접 실행하면 `unittest.main()`.

## ProbeTests (행 7–52)

`unittest.TestCase`를 그대로 상속한다. 표지·설정 훅·도우미·속성이 없다.

### `test_claude_only_cases_and_options_are_rejected_before_live_setup` (행 8–22)
- 성질: Codex 제공자로 Claude 전용 경우(`background`)나 옵션(`--only-assigned-model`)을 요청하면, 출력 폴더를 만들거나 탐침을 돌리기 전에 인자 오류로 끝난다.
- 준비: 두 `subTest(options=...)`: `['--cases', 'background']`, `['--only-assigned-model']`. `Path.mkdir`과 `probe_cli.run_case`를 패치하고 표준 오류를 버린다.
- 실행: `probe_cli.main(['--provider', 'codex', '--model', 'must-not-run', '--output-dir', 'unused-evidence', *options])`.
- 단언: `SystemExit`의 코드가 2(argparse 오류)다. `mkdir`과 `run_case`가 불리지 않았다.
- 대역: `Path.mkdir`, `run_case` 패치, `redirect_stderr`.
- 비고: 오류 메시지(`background and --only-assigned-model require --provider claude`)는 단언하지 않는다.

### `test_claude_model_names_reach_the_runner_with_one_provider_prefix` (행 24–36)
- 성질: Claude 제공자의 모델 이름은 제공자 접두 `claude:`를 정확히 한 번 달고 러너에 전달되며, 완전한 Claude 모델 ID는 그대로 전달된다.
- 준비: 세 `subTest(model=...)`: `opus` → `claude:opus`, `claude:opus` → `claude:opus`, `claude-opus-5` → `claude-opus-5`. `probe_cli.ModelRunner`를 패치하고 `run`이 `{'status': 'failed', 'output': None}`을 돌려주게 한다.
- 실행: `probe_cli.run_case(임시 폴더, 'structured', provider='claude', model=model, effort='low', timeout=1, only_assigned=False)`.
- 단언: 러너 `run` 호출의 `model` 키워드가 기대값과 같다.
- 대역: `ModelRunner` 패치.
- 비고: 제품은 `provider_for(model) == provider`이면 이름을 그대로, 아니면 `"claude:" + model`로 보낸다(행 67).

### `test_live_report_hashes_every_implementation_module` (행 38–52)
- 성질: 탐침 보고서는 `do_math` 패키지의 모든 파이썬 모듈을 해시해 `sources`에 싣는다.
- 준비: `run_case`를 `{'case': 'structured', 'passed': True}`로, `builtins.print`를 패치한다.
- 실행: `probe_cli.main(['--provider', 'codex', '--model', 'fixture-model', '--cases', 'structured', '--output-dir', 임시/evidence])`.
- 단언: `evidence/report.json`의 `sources` 키 집합이 `do_math` 아래 모든 `*.py`의 `scripts/` 기준 상대 경로 문자열 집합과 같다.
- 대역: `run_case`, `print` 패치.
- 비고: 해시 값 자체는 단언하지 않고 키 집합만 본다. 경로 문자열은 `str(Path)`이므로 운영체제의 구분 기호를 따른다.

## 관계

- 같은 제품 기능을 다른 층에서 보는 모듈: `test_preflight`는 `probe_cli`가 부르는 `inspect_bundle`을, `test_claude_adapter`·`test_codex_adapter`·`test_model_runner`(`foundation` 조각)는 제공자 어댑터와 러너를, `test_diagnosed_installation_recovery`는 수리 뒤 `probe_cli.py --skill-only`를 검증 자식으로 부르는 경로를(대역으로) 본다.
- 픽스처를 쓰지 않는다.
- 이 모듈에만 있는 도우미: 없음.
- 실제 외부 자원: 없음. 조각 `host`에 있지만 모든 시험이 프로세스 안에서 대역으로 끝난다.
