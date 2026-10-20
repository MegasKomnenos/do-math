# test_scholarly

| 항목 | 값 |
|---|---|
| 조각 | `foundation` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_scholarly.py` (92행) |
| 클래스 / 테스트 | 1 / 5 |
| 시험 대상 제품 코드 | `do_math/scholarly.py`의 `resolve_scholarly_server`, `validate_scholarly_server`(내부의 `_validate`, `_from_config`, `_absolute_from_config`, `_pathlike`) |
| 사용하는 픽스처 모듈 | 없음 |
| 격리 표지 | 없음 |
| 시작 상태 | 1단(순수 함수 직접 호출). 셋은 임시 폴더에 `config.toml`을 쓰고 환경변수 `CODEX_HOME`을 바꾼다 |

## 목적

모듈 docstring은 없다. 시험 대상 `do_math/scholarly.py`의 모듈 docstring은 "Closed scholarly-MCP configuration for isolated Codex executions."이다. 격리된 Codex 실행에 넘길 scholarly MCP 서버 설정을 `command`와 `args` 두 키만 가진 닫힌 쌍으로 만든다. `resolve_scholarly_server(explicit, *, start)`는 명시값이 있으면 그것만 검증한다. 명시값이 없으면 `start`에서 위로 올라가며 가장 가까운 `.codex/config.toml`의 `mcp_servers.scholarly` 항목을 찾고, 없으면 `CODEX_HOME`(미설정이면 `Path.home() / ".codex"`)의 `config.toml`을 읽는다. 설정 파일에서 읽은 상대 경로 실행 파일과 첫 인자(서버 파일)는 그 설정 파일 옆의 실제 파일로 절대화한다. 나머지 인자는 문자 그대로 둔다(제품 docstring 행 70–75). 이 모듈은 명시값의 닫힘, 거부 규칙, 세 설정 출처의 우선순위를 검사한다.

## 모듈 수준 요소

- 행 1: `from __future__ import annotations`.
- 행 9–10: 스킬의 `scripts/` 폴더를 `sys.path` 앞에 넣는 공통 머리.
- 행 91–92: 직접 실행하면 `unittest.main()`을 부른다.

## ScholarlyServerTests (행 15–88)

`unittest.TestCase`를 그대로 상속한다. 표지, 클래스 속성, 설정 훅, 도우미가 없다. 설정 파일 출처를 다루는 세 시험은 저마다 `TemporaryDirectory` 둘(프로젝트 루트와 홈)을 만들고, `CODEX_HOME`을 바꾼 뒤 `finally`에서 원래 값으로 되돌린다.

### `test_explicit_server_is_closed_when_paths_are_already_absolute` (행 16–20)
- 성질: 절대 경로만 가진 명시 설정은 그대로 통과하되, 호출자의 객체가 아닌 사본으로 돌아온다.
- 준비: `command="C:/tools/python.exe"`, `args=["C:/service/server.py", "--credential-root", "credentials"]`인 사전.
- 실행: `resolve_scholarly_server(value, start=Path.cwd())`.
- 단언: 결과가 입력과 같고(`assertEqual`), 같은 객체는 아니다(`assertIsNot`). 둘째 이후 인자의 상대 경로 `credentials`가 거부되지 않는다는 것도 같은 등식으로 확인된다. 제품은 첫 인자만 경로 규칙으로 본다(`_validate` 행 27).
- 대역: 없음.

### `test_rejects_non_scholarly_fields_and_data_directory_override` (행 22–31)
- 성질: 설정 파일이라는 기준점이 없는 명시 설정은 여분 키, 상대 경로 실행 파일과 서버 파일, 데이터 폴더 덮어쓰기 인자를 모두 거부한다.
- 준비: `subTest`로 다섯 입력. (1) `env` 키가 더 있는 사전. (2) `command="tools/python.exe"`(상대 경로). (3) `args=["server.py"]`(상대 서버 파일). (4) `args`에 `"--data-dir", "outside"`. (5) `args`에 `"--data-dir=outside"`.
- 실행: 각 입력에 `validate_scholarly_server(value)`.
- 단언: 다섯 경우 모두 `ValueError`가 난다. 예외 유형만 보고 메시지는 보지 않는다. 제품의 메시지는 차례로 `"scholarly server must contain exactly command and args"`, `"relative scholarly command needs a configuration-file base"`, `"relative scholarly server file needs a configuration-file base"`, `"scholarly args must not override the execution data directory"`(4와 5)다.
- 대역: 없음.
- 비고: 이름은 "비scholarly 필드와 데이터 폴더 덮어쓰기"만 말하지만, 경우 (2)와 (3)은 기준점 없는 상대 경로의 거부를 검사한다. 거부 사유를 메시지로 고정하지 않으므로, 다섯 경우가 서로 다른 규칙에서 거부되는지는 이 시험으로 구별되지 않는다.

### `test_project_config_beats_code_home_and_extracts_only_scholarly` (행 33–55)
- 성질: 프로젝트의 `.codex/config.toml`이 `CODEX_HOME`보다 우선한다. 그 파일에서는 `mcp_servers.scholarly`의 `command`와 `args`만 가져오고, 상대 경로 두 개는 설정 파일 옆의 실제 파일로 절대화한다.
- 준비: 프로젝트 루트의 `.codex/`에 빈 `python.exe`와 내용이 `# fixture`인 `server.py`를 만든다. `config.toml`에는 두 표를 둔다. 다른 서버 `[mcp_servers.other]`(`command="ignored"`, `args=["secret"]`)와 `[mcp_servers.scholarly]`(`command="python.exe"`, `args=["server.py"]`, `startup_timeout_sec=30`, `tool_timeout_sec=1800`)다. 홈 폴더의 `config.toml`에는 다른 scholarly 항목(`home-python`, `home-server.py`)을 둔다. `CODEX_HOME`을 홈 폴더로 설정한다.
- 실행: `resolve_scholarly_server(None, start=root)`.
- 단언: 결과가 정확히 `{"command": <.codex/python.exe의 resolve 경로>, "args": [<.codex/server.py의 resolve 경로>]}`다. 사전 등식이므로 다른 서버의 값과 두 시간 제한 키가 결과에 없다는 것도 함께 확인된다. 제품 주석(행 59–60)은 시간 제한 설정이 상위 설정의 소유로 남고 상속되지 않는다고 밝힌다.
- 대역: 없음. 환경변수 `CODEX_HOME`만 직접 바꾸고 복원한다.

### `test_code_home_is_used_when_project_has_no_scholarly_entry` (행 57–72)
- 성질: 프로젝트 쪽에 scholarly 항목이 없으면 `CODEX_HOME`의 `config.toml`을 쓴다.
- 준비: 프로젝트 루트에는 `.codex`가 없다. 홈 폴더의 `config.toml`에 `command="python"`, `args=["C:/home-server.py"]`를 둔다. `CODEX_HOME`을 홈 폴더로 설정한다.
- 실행: `resolve_scholarly_server(None, start=root)`.
- 단언: 결과가 `{"command": "python", "args": ["C:/home-server.py"]}`다. `python`은 경로 모양이 아니므로(`_pathlike`는 구분자나 확장자를 본다) 절대화하지 않는다.
- 대역: 없음.
- 비고: 제품은 `start`의 모든 조상 폴더에서 `.codex/config.toml`을 찾는다(행 80–86). 따라서 이 시험과 다음 시험은 임시 폴더의 조상 어디에도 scholarly 항목을 가진 `.codex/config.toml`이 없다는 환경을 전제한다. 작성 시점의 기계에서는 임시 폴더 `C:\Users\wogud\AppData\Local\Temp`의 조상인 `C:\Users\wogud\.codex\config.toml`이 실제로 있지만, `mcp_servers` 표가 없어 `None`을 돌려주므로 전제가 성립한다.

### `test_default_home_config_is_used_when_code_home_is_unset` (행 74–88)
- 성질: `CODEX_HOME`이 설정되지 않았으면 `Path.home() / ".codex" / "config.toml"`을 쓴다.
- 준비: 홈 폴더 아래 `.codex/config.toml`에 이전 시험과 같은 항목을 둔다. `CODEX_HOME`을 환경에서 뺀다(`os.environ.pop`).
- 실행: `do_math.scholarly.Path.home`을 홈 폴더로 패치한 채 `resolve_scholarly_server(None, start=root)`.
- 단언: 결과가 `{"command": "python", "args": ["C:/home-server.py"]}`다.
- 대역: `mock.patch("do_math.scholarly.Path.home", return_value=Path(home))`.
- 비고: 이전 시험과 같은 조상 폴더 전제를 둔다. 원래 `CODEX_HOME`이 있었으면 `finally`에서 되돌린다.

## 관계

- scholarly 설정이 실제 Codex 실행 인자로 들어가는 경로는 제공자 어댑터 쪽 모듈(`test_codex_adapter` 등)과 실시간 탐침 `probe_cli.py --scholarly`의 몫이다. 이 모듈은 해석 함수만 본다.
- 제품의 다른 거부 사유(비어 있거나 NUL을 가진 `command`, 문자열이 아닌 인자, TOML 파싱 오류 `"invalid Codex configuration at ..."`, 표가 아닌 scholarly 항목, 설정 파일 옆에 없는 상대 파일 `"... does not name a file beside its configuration"`)는 이 모듈에서 단언하지 않는다. 같은 설정 파일을 두 번 검사하지 않는 `checked` 집합(행 79–89)도 따로 검사하지 않는다.
- 픽스처 모듈을 쓰지 않는다.
