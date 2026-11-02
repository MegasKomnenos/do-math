# Connecting Codex and Claude sessions

The runner builds the command of a new session with the functions of [cli_adapter.py](cli_adapter.py), and when the process ends it reads the provider usage limit from the logs. The adapter uses only the standard library, and the Python version needed to run it is defined by [RUNTIME.md](RUNTIME.md). Merging the per-category default model and effort with a plan's per-request specification is the caller's job. The adapter is passed the final values chosen that way.

## Model selection and command construction

```python
provider_for_model(model: str) -> Literal["codex", "claude"]
build_command(cli_path: str | os.PathLike[str], model: str,
              effort: str, cwd: str | os.PathLike[str]) -> Command
```

`provider_for_model` takes the `codex/<CLI model>` or `claude/<CLI model>` of [protocol.md](protocol.md). It returns the case-sensitive provider before the first `/`, and `build_command` passes the **whole string** after the first `/` as the CLI model argument. For example `codex/gpt-6.1-sol`, `claude/sonnet` and `codex/vendor/model` pass `gpt-6.1-sol`, `sonnet` and `vendor/model` respectively. A different provider, no `/`, or an empty or whitespace-only remainder is a `ValueError`. The provider is not guessed from a bare name. The existence of the model and the account's access right are judged by the CLI.

The caller puts the configured path of the returned provider in `cli_path`. `build_command` returns a `Command` with the following fields.

| Field | Meaning |
|---|---|
| `provider` | `"codex"` or `"claude"` |
| `argv` | The list of strings to pass to `subprocess.Popen` as it is. No shell quoting is added. |
| `cwd` | The input working directory made absolute with `Path.resolve()`, as a `Path`. **Passed as Popen's cwd for both CLIs.** |

For `cli_path`, the absolute path of the native executable is recommended, and an executable name to be found on PATH is also accepted. Using an absolute path instead of a relative file path avoids differences of interpretation depending on the child's cwd. The function does not check the existence of the executable or the working directory and does not create directories. An empty executable path, an empty effort string and an unsupported Claude effort are a `ValueError`. A wrong Python argument type may raise a `TypeError`, and a path resolution failure a filesystem exception. Actual file absence, permissions, authentication and model refusal show up at launch or when the CLI runs.

The Codex effort value is passed as a nonempty string encoded as a TOML string. Which efforts are valid for each model is judged by the CLI and the model. Claude accepts the `low`, `medium`, `high`, `xhigh` and `max` of the installed help. Support per model is not guaranteed.

| Purpose | Codex argv | Claude argv |
|---|---|---|
| New non-interactive session | `exec`, stdin positional argument `-` | `--print --input-format text`, stdin |
| Model and effort | `--model MODEL -c model_reasoning_effort="EFFORT"` | `--model MODEL --effort EFFORT` |
| Unattended execution | `-c approval_policy="never" --sandbox danger-full-access` | `--dangerously-skip-permissions --permission-prompts none` |
| Working location | `--cd DIR --skip-git-repo-check` and Popen cwd | Popen cwd |
| Skip conversation persistence | `--ephemeral` | `--no-session-persistence` |
| Output for distinguishing the limit source | `--color never --json` | `--output-format stream-json --verbose` |

This command starts a new conversation without resume/continue. It uses the existing login and the user's environment. Claude's `--bare` does not read OAuth/keychain, so it is not included in this command, which uses the subscription login. A new conversation may also be affected by user settings, hooks, `AGENTS.md`, `CLAUDE.md` and the like. Skipping conversation persistence does not mean that the CLI's writes of authentication, cache and diagnostics are blocked as well.

The permission options are a choice for avoiding approval waits during unattended work. Neither cwd nor the permission bypass provides OS-level write isolation of the session folder. The working context in the prompt includes the instruction to write only in one's own session folder, the locations of the common documents, the category document, this task's document and the accumulated knowledge to read, and the way to check the output.

## Use by the runner

The session host of [runner.py](runner.py) runs `Command.argv` in `Command.cwd` without a shell. The long prompt is delivered by connecting the session folder's UTF-8 `prompt.txt` as the stdin file, so no command-line re-quoting or length problems arise. stdout and stderr are also connected directly to `cli.stdout.jsonl` and `cli.stderr.log` in the same folder, because if they were received through a PIPE and nobody read them, the buffer would fill and the child could stall. The job host of the Lean broker runs Lean the same way, with `stdout.log` and `stderr.log` in the job's folder ([LEAN.md](LEAN.md)). When the CLI ends, the runner calls the limit function below on these two logs. How the host waits for the CLI's exit, the recording of launch failures and the re-check of output regardless of the exit code are defined by 'Session delivery, integration and recovery' of [RUNTIME.md](RUNTIME.md), and the fact that there is no session time cap by 'Terminating one stuck session' of the same document.

## Reading usage limits from finished logs

```python
detect_usage_limit(
    provider: Literal["codex", "claude"],
    stdout_path: str | os.PathLike[str], stderr_path: str | os.PathLike[str], *,
    now: float, fallback_seconds: float,
    session_started_at: float | None = None,
    local_timezone: datetime.tzinfo | None = None,
) -> UsageLimit | None
```

The two paths are the closed log files of the session concerned. The function reads line by line as UTF-8 and replaces invalid bytes. `now` is the current time at which the logs are processed, and `fallback_seconds` is the positive number of seconds to wait when the reset time cannot be known. `session_started_at` is the time recorded just before launching that CLI process. All numeric times are **UTC Unix epoch seconds**, not milliseconds. The caller may use `time.time()` values. `local_timezone` is the local time zone of the host on which Codex composed the message. `None` uses the current host time zone; if specified, use a tzinfo such as `datetime.timezone` or `zoneinfo.ZoneInfo`. Use a fixed offset when you know that the offset applies on that date.

| Return | Meaning for the caller |
|---|---|
| `None` | No supported account-limit refusal signal was found. Not a value that guarantees session success or account headroom. |
| `UsageLimit(provider, retry_at, "provider")` | A valid future reset time read from the provider's refusal. `retry_at` is UTC Unix seconds. |
| `UsageLimit(provider, retry_at, "fallback")` | The refusal was confirmed but the reset time is unconfirmed. `retry_at = now + fallback_seconds`. |

The function does not wait or restart the session. If several actual refusals are found, it returns the latest of the wait expiries computed for each refusal. `source` is then the basis of the chosen expiry. The preventive usage statistics of the same record are not merged into several refusals.

An unknown provider, an invalid current or start time, a non-positive wait interval and a wrong time-zone argument are a `ValueError`. Numeric times must be finite and representable as a Python datetime. I/O failures such as file absence or read permission are passed through as `OSError` and its kind. The runner records these as log read failures and **still performs the official re-check of the output**. A file error is not turned into "no limit" or an output failure.

Non-JSON lines, truncated JSON, non-object values, unknown fields and meaningless field values are not used for detection and are skipped. Duplicate keys are read as the last value, by the default rule of Python's `json.loads`. Such output differences are not conditions for approving the output. If the limit-refusal marker is valid and only the time part is wrong, `fallback` is returned.

## Per-provider signals and time semantics

For Codex, only the `message` of `type="error"` and the `error.message` of `type="turn.failed"` are read. A message that, with surrounding whitespace removed, begins with one of the following phrases is an account limit. Curly and ASCII apostrophes are treated alike.

- `You’ve hit your usage limit`
- `Your workspace is out of credits`
- `You hit your spend cap`

The `Try again at 7:11 PM` or `or try again at Oct 22nd, 2026 7:11 PM` of the same message is read. The month is an English abbreviation and the time is host local time. If the date is present, that date is used. If only the time is present, that date is used only when `session_started_at` through `now` fall on the same local date. When the start is unknown or later than the present, when the session crossed midnight, or when the date cannot be trusted because the clock or time zone changed, the date is not guessed. The caller omits the start time when it knows of a clock or time-zone change. A local time that does not exist or is ambiguous because of DST is also treated as unknown.

The start of the displayed minute is used as the reset time. Since the seconds of the original reset are omitted in the output, resumption may be up to 59 seconds early. A time already past, an invalid date, `later` or a missing time uses the configured interval. Codex exec errors have no numeric reset field, so no such field is looked for. Limit phrases in ordinary answers or tool output, ordinary 429s and phrases in raw stderr alone are not used for the verdict. This is the choice to use only the explicit error events of `--json`.

For Claude, a record in which the following **three top-level fields are present together** is read as an account usage-limit refusal.

```json
{"type":"assistant","is_api_error_message":true,"api_error":"usage_limit_reached","api_error_params":{"rate_limit_info":{"status":"rejected","rateLimitType":"five_hour","resetsAt":1792598400,"isUsingOverage":false}}}
```

The example above is a synthetic record for explaining field positions. From `api_error_params.rate_limit_info`, the reset time is adopted only in the following cases where the time semantics are clear.

- If `status="rejected"` and the window is an ordinary limit window (`five_hour`, `seven_day`, `seven_day_opus`, `seven_day_sonnet`, `seven_day_overage_included`) and `overageStatus` and `overageResetsAt` are both omitted or `null`, `resetsAt` is used.
- In an ordinary overage refusal where `status="rejected"` and `overageStatus="rejected"` are present together and the window is in the list above or `overage`, the minimum of the values provided among `resetsAt` and `overageResetsAt` is used. All the values provided must be valid future times. A later value is not chosen arbitrarily because an earlier one has expired.
- In both branches above, `isUsingOverage` must be omitted, `null` or false, and `overageDisabledReason`, `limitScope` and `overageScope` must each be omitted or `null`. Special spend limits of organizations, groups or channels, unknown windows or contradictory states, and unclear multiple resets are handled with the configured interval. Even then the explicit account refusal itself is kept.

`resetsAt` and `overageResetsAt` are Unix seconds. `unifiedWindows` contains the preventive statistics of other windows and is not used. The `rate_limit_event` auxiliary signal is not adopted. That event also includes normal and warning states, and even when the base usage is rejected, use can continue with paid overage. Allowed/allowed_warning/rejected state events without an actual refusal marker, ordinary `error="rate_limit"` and 429s, and quoted phrases are not read as a limit.

When this function returns a limit, the runner stops dispatching new sessions until `retry_at`. Sessions already running are left alone, and finished sessions have their output re-checked as usual. A finished session is not relaunched as it is because of a limit, and later assignment is decided by the plan in the original flow. The relation between the limit wait and the other wait conditions is in 'Session delivery, integration and recovery' of [RUNTIME.md](RUNTIME.md).

## Evidence and confirmed scope

The launch options and signals are based on the help of Codex CLI 0.163.0 and the official source of the same version, and on the help and installed implementation of Claude Code 2.1.306, confirmed on 2026-10-21. Codex's actual messages and local time format are defined in [UsageLimitReachedError and format_retry_timestamp](https://github.com/openai/codex/blob/rust-v0.163.0/codex-rs/protocol/src/error.rs), and the JSON error location in [exec_events.rs](https://github.com/openai/codex/blob/rust-v0.163.0/codex-rs/exec/src/exec_events.rs). The assistant schema and serialization of the Claude installed implementation put the typed fields above at the top level, and the ordinary overage display branch shows the earlier of the two resets. Special organization limits use a separate branch.

The Claude typed fields are `@internal`, so they may change in later CLIs. This adapter targets the current subscription authentication path and does not cover every limit of API keys or other cloud providers, or every error phrase. No version pinning or installation comparison is done. Actual model access, and the behavior of reading the prompt and writing output in one's own folder, were confirmed on 2026-10-21 in an actual instance in which three Codex sessions and two Claude sessions completed a small goal unattended. User settings and hooks differ per host, so their effect on sessions outside the settings of that flow has not been confirmed.

`tests/test_cli_adapter.py` distinguishes, with synthetic logs built from the evidence rather than inducing an actual limit, future times, unconfirmed dates, ordinary overage and special branches, and normal quotes, warnings and incomplete logs.

```powershell
python -B -m unittest discover -s .claude/skills/do-math/tests -p test_cli_adapter.py
```
