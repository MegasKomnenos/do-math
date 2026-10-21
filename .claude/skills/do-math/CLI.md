# Codex·Claude 세션 연결

실행기는 [cli_adapter.py](cli_adapter.py)의 함수로 새 세션의 명령을 만들고, 프로세스가 끝나면 로그에서 공급자 사용 한도를 읽는다. 어댑터는 표준 라이브러리만 사용하며, 실행에 필요한 Python 판본은 [RUNTIME.md](RUNTIME.md)가 정한다. 범주별 기본 모델·노력과 계획의 개별 지정을 합치는 일은 호출자가 맡는다. 어댑터에는 그렇게 선택한 최종 값을 전달한다.

## 모델 선택과 명령 생성

```python
provider_for_model(model: str) -> Literal["codex", "claude"]
build_command(cli_path: str | os.PathLike[str], model: str,
              effort: str, cwd: str | os.PathLike[str]) -> Command
```

`provider_for_model`은 [protocol.md](protocol.md)의 `codex/<CLI 모델>` 또는 `claude/<CLI 모델>`을 받는다. 대소문자를 구분하는 첫 `/` 앞의 공급자를 반환하며, `build_command`는 첫 `/` 뒤 **전체 문자열**을 CLI 모델 인자로 넘긴다. 예를 들어 `codex/gpt-6.1-sol`, `claude/sonnet`, `codex/vendor/model`은 각각 `gpt-6.1-sol`, `sonnet`, `vendor/model`을 전달한다. 공급자가 다르거나 `/`가 없거나 뒤가 빈 문자열·공백뿐이면 `ValueError`다. bare 이름으로 공급자를 추정하지 않는다. 모델의 존재와 계정 접근 권한은 CLI가 판단한다.

호출자는 반환된 공급자의 설정 경로를 `cli_path`에 넣는다. `build_command`는 다음 필드를 가진 `Command`를 반환한다.

| 필드 | 의미 |
|---|---|
| `provider` | `"codex"` 또는 `"claude"` |
| `argv` | `subprocess.Popen`에 그대로 전달할 문자열 목록. 셸 인용을 더하지 않는다. |
| `cwd` | 입력 작업 디렉터리를 `Path.resolve()`로 절대화한 `Path`. **두 CLI 모두 Popen의 cwd로 전달한다.** |

`cli_path`는 네이티브 실행 파일의 절대 경로를 권장하며 PATH에서 찾을 실행 파일명도 받는다. 상대 파일 경로 대신 절대 경로를 쓰면 자식의 cwd에 따른 해석 차이를 피할 수 있다. 함수는 실행 파일과 작업 디렉터리의 존재를 검사하거나 디렉터리를 만들지 않는다. 빈 실행 경로·빈 노력 문자열과 지원하지 않는 Claude 노력은 `ValueError`다. 잘못된 Python 인자 형식은 `TypeError`, 경로 해석 실패는 파일 시스템 예외가 날 수 있다. 실제 파일 부재·권한·인증·모델 거절은 기동 또는 CLI 실행 시 드러난다.

Codex의 노력 값은 비어 있지 않은 문자열을 TOML 문자열로 인코딩해 전달한다. 모델마다 유효한 노력은 CLI와 모델이 판단한다. Claude는 설치 help의 `low`, `medium`, `high`, `xhigh`, `max`를 받는다. 모델별 지원을 보장하는 것은 아니다.

| 목적 | Codex argv | Claude argv |
|---|---|---|
| 새 비대화 세션 | `exec`, stdin 위치 인자 `-` | `--print --input-format text`, stdin |
| 모델·노력 | `--model MODEL -c model_reasoning_effort="EFFORT"` | `--model MODEL --effort EFFORT` |
| 무인 실행 | `-c approval_policy="never" --sandbox danger-full-access` | `--dangerously-skip-permissions --permission-prompts none` |
| 작업 위치 | `--cd DIR --skip-git-repo-check` 및 Popen cwd | Popen cwd |
| 대화 보존 생략 | `--ephemeral` | `--no-session-persistence` |
| 한도 출처 구분용 출력 | `--color never --json` | `--output-format stream-json --verbose` |

이 명령은 resume/continue 없이 새 대화를 시작한다. 기존 로그인과 사용자 환경을 사용한다. Claude의 `--bare`는 OAuth/keychain을 읽지 않으므로 구독 로그인을 쓰는 이 명령에 포함하지 않는다. 새 대화도 사용자 설정, hooks, `AGENTS.md`·`CLAUDE.md` 등의 영향을 받을 수 있다. 대화 보존 생략은 CLI의 인증·캐시·진단 쓰기까지 막는다는 뜻은 아니다.

권한 옵션은 무인 작업 중 승인 대기를 피하기 위한 선택이다. cwd나 권한 우회가 OS 수준의 세션 폴더 쓰기 격리를 제공하지는 않는다. 프롬프트의 작업맥락에 자기 세션 폴더에만 쓴다는 지시와 읽을 공통 문서·범주 문서·이번 작업 문서·축적 지식 위치, 산출 검사 방법을 담는다.

## 실행기의 사용

[runner.py](runner.py)의 세션 호스트가 `Command.argv`를 `Command.cwd`에서 shell 없이 실행한다. 긴 한국어 프롬프트는 세션 폴더의 UTF-8 `prompt.txt`를 stdin 파일로 연결해 전달하므로 명령행 재인용·길이 문제가 생기지 않는다. stdout과 stderr도 같은 폴더의 `cli.stdout.jsonl`·`cli.stderr.log`에 직접 연결한다. PIPE로 받고 아무도 읽지 않으면 버퍼가 차서 자식이 멈출 수 있기 때문이다. CLI가 끝나면 실행기가 이 두 로그로 아래 한도 함수를 호출한다. 호스트가 CLI 종료를 기다리는 방식, 기동 실패의 기록, 종료 코드와 무관한 산출 재검사는 [RUNTIME.md](RUNTIME.md)의 '세션 전달, 반영, 복구'가 정하고, 세션 시간 상한이 없다는 점은 같은 문서의 '멈춰 버린 세션 하나 종료'가 정한다.

## 끝난 로그에서 한도 읽기

```python
detect_usage_limit(
    provider: Literal["codex", "claude"],
    stdout_path: str | os.PathLike[str], stderr_path: str | os.PathLike[str], *,
    now: float, fallback_seconds: float,
    session_started_at: float | None = None,
    local_timezone: datetime.tzinfo | None = None,
) -> UsageLimit | None
```

두 경로는 해당 세션의 닫힌 로그 파일이다. 함수는 UTF-8로 줄별로 읽고 잘못된 바이트는 대체한다. `now`는 로그를 처리하는 현재 시각, `fallback_seconds`는 해제 시각을 알 수 없을 때 기다릴 양의 초 수다. `session_started_at`은 그 CLI 프로세스를 띄우기 직전에 기록한 시각이다. 모든 숫자 시각은 **UTC Unix epoch 초**이며 밀리초가 아니다. 호출자는 `time.time()` 값을 쓸 수 있다. `local_timezone`은 Codex가 메시지를 작성한 호스트의 로컬 시간대다. `None`이면 현재 호스트 시간대, 명시하면 `datetime.timezone` 또는 `zoneinfo.ZoneInfo` 같은 tzinfo를 쓴다. 고정 오프셋은 해당 날짜에 그 오프셋임을 알 때 사용한다.

| 반환 | 호출자가 읽을 의미 |
|---|---|
| `None` | 지원하는 계정 한도 거절 신호를 발견하지 못했다. 세션 성공이나 계정 여유를 보증하는 값은 아니다. |
| `UsageLimit(provider, retry_at, "provider")` | 해당 공급자 거절에서 읽은 유효한 미래 해제 시각. `retry_at`은 UTC Unix 초. |
| `UsageLimit(provider, retry_at, "fallback")` | 거절은 확인했지만 해제 시각은 미확인. `retry_at = now + fallback_seconds`. |

함수는 대기하거나 세션을 재시작하지 않는다. 여러 실제 거절이 발견되면 각 거절에 대해 계산한 대기 만료 중 가장 늦은 것을 반환한다. 이때 `source`는 선택된 만료의 근거다. 같은 레코드의 예방적 사용량 통계를 여러 거절로 합치지는 않는다.

알 수 없는 공급자, 유효하지 않은 현재/시작 시각, 시작이 현재보다 미래인 경우, 양수가 아닌 대기 간격, 잘못된 시간대 인자는 `ValueError`다. 숫자 시각은 유한하며 Python datetime으로 표현 가능해야 한다. 파일 부재·읽기 권한 등 I/O 실패는 `OSError` 계열을 그대로 전달한다. 실행기는 이를 로그 읽기 실패로 기록하고 **산출의 공식 재검사는 계속 수행한다**. 파일 오류를 한도 없음이나 산출 실패로 바꾸지 않는다.

JSON 아닌 줄, 잘린 JSON, 객체 아닌 값, 알 수 없는 필드, 의미 없는 필드 값은 탐지 대상으로 쓰지 않고 넘어간다. 중복 키는 Python `json.loads`의 기본 규칙대로 마지막 값을 읽는다. 이런 출력 차이는 산출 승인 조건이 아니다. 한도 거절 표식은 유효하고 시각 부분만 잘못됐다면 `fallback`을 반환한다.

## 공급자별 신호와 시간 의미

Codex는 `type="error"`의 `message`, `type="turn.failed"`의 `error.message`만 읽는다. 양끝 공백을 제외한 메시지가 다음 문구로 시작하면 계정 한도다. 곡선·ASCII 아포스트로피를 동일하게 처리한다.

- `You’ve hit your usage limit`
- `Your workspace is out of credits`
- `You hit your spend cap`

같은 메시지의 `Try again at 7:11 PM` 또는 `or try again at Oct 22nd, 2026 7:11 PM`을 읽는다. 월은 영문 약자이며 호스트 로컬 시각이다. 날짜까지 있으면 해당 날짜를 사용한다. 시간만 있으면 `session_started_at`부터 `now`까지 같은 로컬 날짜인 경우에만 그 날짜를 사용한다. 시작을 모르는 경우, 자정을 넘긴 세션, 시계/시간대가 바뀌어 날짜를 신뢰할 수 없는 경우에는 날짜를 추측하지 않는다. 호출자는 시계/시간대 변경을 아는 경우 시작 시각을 생략한다. DST 때문에 존재하지 않거나 둘로 해석되는 로컬 시각도 미확인으로 처리한다.

표시된 분의 시작을 해제 시각으로 사용한다. 원래 reset의 초가 출력에서 생략되므로 최대 59초 일찍 재개될 수 있다. 이미 지난 시각·잘못된 날짜·`later`·시각 누락이면 설정 간격을 쓴다. Codex exec 오류에는 숫자 reset 필드가 없으므로 그런 필드를 찾지 않는다. 일반 답변·도구 출력의 한도 문구, 일반 429, 원시 stderr의 문구만으로는 판정하지 않는다. `--json`의 명시적인 오류 이벤트만 사용하는 선택이다.

Claude는 아래 **최상위 필드 세 개가 함께 있는** 레코드를 계정 사용 한도 거절로 읽는다.

```json
{"type":"assistant","is_api_error_message":true,"api_error":"usage_limit_reached","api_error_params":{"rate_limit_info":{"status":"rejected","rateLimitType":"five_hour","resetsAt":1792598400,"isUsingOverage":false}}}
```

위 예는 필드 위치 설명용 합성 레코드다. `api_error_params.rate_limit_info`에서 시간 의미가 분명한 다음 경우만 해제 시각을 채택한다.

- `status="rejected"`이고 일반 제한 창(`five_hour`, `seven_day`, `seven_day_opus`, `seven_day_sonnet`, `seven_day_overage_included`)이며 `overageStatus`와 `overageResetsAt`이 모두 생략되거나 `null`이면 `resetsAt`을 쓴다.
- `overageStatus="rejected"`이고 창이 위 목록 또는 `overage`인 일반 overage 거절에서는 `resetsAt`·`overageResetsAt` 중 제공된 값의 최솟값을 쓴다. 제공된 모든 값이 유효한 미래 시각이어야 한다. 앞선 값이 만료됐다고 뒤의 값을 임의로 선택하지 않는다.
- 위 두 분기 모두 `isUsingOverage`가 생략·`null`·false 중 하나이고, `overageDisabledReason`·`limitScope`·`overageScope`는 각각 생략되거나 `null`이어야 한다. 조직·그룹·채널의 특수 지출 한도, 모르는 창이나 모순된 상태, 불명확한 다중 reset은 설정 간격으로 처리한다. 그 경우에도 명시적인 계정 거절 자체는 유지된다.

`resetsAt`·`overageResetsAt`은 Unix 초다. `unifiedWindows`는 다른 창의 예방적 통계를 포함하므로 사용하지 않는다. `rate_limit_event` 보조 신호는 채택하지 않는다. 이 이벤트는 정상·경고도 포함하고 기본 사용량이 rejected여도 paid overage로 계속 사용할 수 있기 때문이다. 실제 거절 표식이 없는 allowed/allowed_warning/rejected 상태 이벤트, 일반 `error="rate_limit"`·429와 문구 인용은 한도로 읽지 않는다.

이 함수가 한도를 반환하면 실행기는 새 세션 파견을 `retry_at`까지 멈춘다. 이미 실행 중인 세션은 계속 두고 끝난 세션은 평소처럼 산출을 재검사한다. 끝난 세션을 한도 때문에 그대로 다시 띄우지 않으며 이후 배정은 원래 흐름에서 계획이 결정한다. 한도 대기와 다른 대기 조건의 관계는 [RUNTIME.md](RUNTIME.md)의 '세션 전달, 반영, 복구'에 있다.

## 근거와 확인 범위

기동 옵션과 신호는 2026-10-21에 확인한 Codex CLI 0.163.0의 help·동일 버전 공식 소스 및 Claude Code 2.1.306의 help·설치 구현에 근거한다. Codex의 실제 메시지와 로컬 시각 형식은 [UsageLimitReachedError 및 format_retry_timestamp](https://github.com/openai/codex/blob/rust-v0.163.0/codex-rs/protocol/src/error.rs), JSON 오류 위치는 [exec_events.rs](https://github.com/openai/codex/blob/rust-v0.163.0/codex-rs/exec/src/exec_events.rs)에 정의돼 있다. Claude 설치 구현의 assistant schema·직렬화는 위 typed 필드를 최상위에 두고, 일반 overage 표시 분기는 두 reset 중 더 이른 것을 표시한다. 특수 조직 한도는 별도 분기를 사용한다.

Claude typed 필드는 `@internal`이므로 이후 CLI에서 바뀔 수 있다. 이 어댑터는 현재 구독 인증 경로를 대상으로 하며 API key·다른 cloud 공급자의 모든 한도, 모든 오류 문구를 포괄하지 않는다. 버전 고정이나 설치 비교는 하지 않는다. 실제 모델 접근과, 프롬프트를 읽고 자기 폴더에 산출을 쓰는 동작은 2026-10-21에 Codex 세 세션과 Claude 두 세션이 작은 목표를 무인 완주한 실제 인스턴스에서 확인했다. 사용자 설정·hooks는 호스트마다 다르므로, 그 완주의 설정 밖에서 그것들이 세션에 주는 영향은 확인되지 않았다.

`tests/test_cli_adapter.py`는 실제 한도를 유도하지 않고 근거에서 만든 합성 로그로 미래 시각, 날짜 미확인, 일반 overage와 특수 분기, 정상 인용·경고·불완전 로그를 구분한다. 테스트 실행에는 TOML 인자 확인용 표준 라이브러리 `tomllib`이 있는 Python 3.11 이상을 사용한다.

```powershell
python -B -m unittest discover -s .claude/skills/do-math/tests -p test_cli_adapter.py
```
