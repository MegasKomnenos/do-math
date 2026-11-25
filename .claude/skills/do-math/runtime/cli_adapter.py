"""Base CLI commands and account usage-limit detection. Worker isolation is in launch.py."""

from dataclasses import dataclass
from datetime import datetime, timezone, tzinfo
import json
import math
import os
from pathlib import Path
import re
from typing import Literal

Provider = Literal["codex", "claude"]
PathLike = str | os.PathLike[str]


@dataclass(frozen=True)
class Command:
    provider: Provider
    argv: list[str]
    cwd: Path


@dataclass(frozen=True)
class UsageLimit:
    provider: Provider
    retry_at: float  # UTC Unix seconds
    source: Literal["provider", "fallback"]


def provider_for_model(model: str) -> Provider:
    """Use the explicit protocol provider; leave model availability to the CLI."""
    if isinstance(model, str):
        provider, separator, name = model.partition("/")
        if provider in ("codex", "claude") and separator and name.strip():
            return provider
    raise ValueError(f"Expected codex/<model> or claude/<model>: {model!r}")


def build_command(
    cli_path: PathLike, model: str, effort: str, cwd: PathLike
) -> Command:
    """Build an unattended command for a new conversation; caller supplies stdin and log files.

    The native conversation persists: retention copies its transcript and the session
    host resumes it (launch.py), so no ephemeral or no-persistence flag is set here."""
    provider = provider_for_model(model)
    model = model.partition("/")[2]
    executable = os.fspath(cli_path)
    if not isinstance(executable, str) or not executable.strip():
        raise ValueError("cli_path must be a nonempty executable path or name")
    if not isinstance(effort, str) or not effort.strip():
        raise ValueError("effort must be a nonempty string")
    workdir = Path(cwd).resolve()
    if provider == "codex":
        argv = [
            executable, "exec", "--model", model,
            "-c", "model_reasoning_effort=" + json.dumps(effort),
            "-c", 'approval_policy="never"',
            "--sandbox", "danger-full-access", "--cd", str(workdir),
            "--skip-git-repo-check", "--color", "never",
            "--json", "-",
        ]
    else:
        if effort not in ("low", "medium", "high", "xhigh", "max"):
            raise ValueError(f"Unsupported Claude effort: {effort!r}")
        argv = [
            executable, "--print", "--model", model, "--effort", effort,
            "--dangerously-skip-permissions", "--permission-prompts", "none",
            "--input-format", "text",
            "--output-format", "stream-json", "--verbose",
        ]
    return Command(provider, argv, workdir)


_CODEX_LIMIT = re.compile(
    r"^(?:You've hit your usage limit\b|Your workspace is out of credits\b|"
    r"You hit your spend cap\b)", re.IGNORECASE
)
_RETRY = re.compile(
    r"\btry again at (?:(?P<month>[A-Za-z]{3}) (?P<day>\d{1,2})"
    r"(?:st|nd|rd|th), (?P<year>\d{4}) )?"
    r"(?P<hour>\d{1,2}):(?P<minute>\d{2}) (?P<ampm>AM|PM)(?=\.|\s|$)",
    re.IGNORECASE,
)
_MONTHS = {name: i for i, name in enumerate(
    "jan feb mar apr may jun jul aug sep oct nov dec".split(), 1
)}
_WINDOWS = ("five_hour", "seven_day", "seven_day_opus", "seven_day_sonnet",
            "seven_day_overage_included")


def _epoch(value: object) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    try:
        result = float(value)
        if not math.isfinite(result):
            return None
        datetime.fromtimestamp(result, timezone.utc)
        return result
    except (ValueError, OverflowError, OSError):
        return None


def _codex_reset(
    message: str, now: float, started: float | None, zone: tzinfo | None
) -> float | None:
    match = _RETRY.search(message)
    if match is None:
        return None
    try:
        if match["year"]:
            year, month, day = (int(match["year"]), _MONTHS[match["month"].lower()],
                                int(match["day"]))
        else:
            # No per-event timestamp is provided by Codex exec. The entire
            # session must fit in one local date to infer the missing date.
            today = datetime.fromtimestamp(now, zone).date()
            if started is None or datetime.fromtimestamp(started, zone).date() != today:
                return None
            year, month, day = today.year, today.month, today.day
        hour = int(match["hour"])
        if not 1 <= hour <= 12:
            return None
        hour = hour % 12 + (12 if match["ampm"].upper() == "PM" else 0)
        wall = datetime(year, month, day, hour, int(match["minute"]))
        # Round-trip both folds: nonexistent or ambiguous DST times are unknown.
        candidates = set()
        for fold in (0, 1):
            stamp = wall.replace(tzinfo=zone, fold=fold).timestamp()
            if datetime.fromtimestamp(stamp, zone).replace(tzinfo=None) == wall:
                candidates.add(stamp)
        if len(candidates) == 1:
            return candidates.pop()
    except (KeyError, ValueError, OverflowError, OSError):
        pass
    return None


def _claude_reset(info: object, now: float) -> float | None:
    if not isinstance(info, dict) or info.get("status") != "rejected":
        return None
    # Scope/disabled-reason branches have different recovery semantics.
    if any(info.get(key) is not None for key in (
        "overageDisabledReason", "limitScope", "overageScope"
    )) or (info.get("isUsingOverage") is not None and info.get("isUsingOverage") is not False):
        return None
    kind = info.get("rateLimitType")
    if info.get("overageStatus") == "rejected" and kind in (*_WINDOWS, "overage"):
        values = [info[key] for key in ("resetsAt", "overageResetsAt")
                  if info.get(key) is not None]
        stamps = [_epoch(value) for value in values]
        # This is the ordinary overage rejection's earliest recovery branch.
        # Do not discard an expired/bad earlier value and pick a later window.
        if stamps and all(stamp is not None and stamp > now for stamp in stamps):
            return min(stamps)
    elif (kind in _WINDOWS and info.get("overageStatus") is None
          and info.get("overageResetsAt") is None):
        return _epoch(info.get("resetsAt"))
    return None


def codex_error_message(event: dict) -> object:
    """The message of a failure that a Codex stream event reports, or None for any other event.

    An `error` event carries the message itself, and a `turn.failed` event carries it under `error`.
    The usage-limit detection below and retention.refusal both read this rule here, so a change of
    the stream's form is one edit."""
    if event.get("type") == "error":
        return event.get("message")
    error = event.get("error")
    if event.get("type") == "turn.failed" and isinstance(error, dict):
        return error.get("message")
    return None


def detect_usage_limit(
    provider: Provider,
    stdout_path: PathLike,
    stderr_path: PathLike,
    *,
    now: float,
    fallback_seconds: float,
    session_started_at: float | None = None,
    local_timezone: tzinfo | None = None,
) -> UsageLimit | None:
    """Read finished logs; return no signal or a UTC deadline. Never sleep.

    Times are Unix seconds. local_timezone=None uses the CLI host's current
    local timezone. session_started_at permits same-date Codex time inference.
    File errors propagate as OSError. Malformed log records are ignored.
    See the operating guide for provider waits and model fallback.
    """
    if session_started_at is not None and session_started_at > now:
        # The clock moved back during the session, so no date is inferred.
        session_started_at = None

    result = None
    for path in (stdout_path, stderr_path):
        with open(path, encoding="utf-8", errors="replace") as stream:
            for line in stream:
                try:
                    event = json.loads(line)
                except (ValueError, RecursionError):
                    continue
                if not isinstance(event, dict):
                    continue
                reset = None
                if provider == "codex":
                    message = codex_error_message(event)
                    if not isinstance(message, str) or not _CODEX_LIMIT.match(
                        message.strip().replace("\u2019", "'")
                    ):
                        continue
                    reset = _codex_reset(message, now, session_started_at, local_timezone)
                else:
                    if not (event.get("type") == "assistant"
                            and event.get("is_api_error_message") is True
                            and event.get("api_error") == "usage_limit_reached"):
                        continue
                    params = event.get("api_error_params")
                    info = params.get("rate_limit_info") if isinstance(params, dict) else None
                    reset = _claude_reset(info, now)
                known = reset is not None and reset > now
                candidate = UsageLimit(provider, reset if known else now + fallback_seconds,
                                       "provider" if known else "fallback")
                # Multiple genuine refusals can describe separate windows.
                if result is None or candidate.retry_at > result.retry_at:
                    result = candidate
    return result
