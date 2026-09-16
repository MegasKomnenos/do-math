"""Command-line boundary for the do-math CLI workflow."""

from __future__ import annotations

import argparse
import base64
import json
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any

from .codex_adapter import CodexExecAdapter
from .engine import ResearchEngine, control, initialize, json_safe
from .git_store import GitStateStoreConflict, GitStateStoreError, GitStateStoreLockError
from .repository import ResearchRepository
from . import scheduled_operator


class CliInputError(ValueError):
    """A command-line argument or supplied local input is invalid."""


class _Parser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise CliInputError(message)


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise CliInputError(f"duplicate JSON key: {key}")
        value[key] = item
    return value


def _json_file(path: str) -> dict[str, Any]:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"), object_pairs_hook=_pairs)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
        raise CliInputError(f"cannot read JSON file {path}: {error}") from error
    if not isinstance(value, dict):
        raise CliInputError("JSON configuration must be an object")
    return value


def _text_file(path: str) -> str:
    try:
        return Path(path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as error:
        raise CliInputError(f"cannot read text file {path}: {error}") from error


def _require_git(repository: Path, create: bool = False) -> None:
    if create:
        if repository.exists() and (not repository.is_dir() or any(repository.iterdir())):
            raise CliInputError("--create-repository accepts only a missing or empty directory")
        repository.mkdir(parents=True, exist_ok=True)
        result = subprocess.run(["git", "-C", str(repository), "init", "-q"], check=False, capture_output=True)
        if result.returncode:
            raise GitStateStoreError("git init failed")
    result = subprocess.run(["git", "-C", str(repository), "rev-parse", "--git-dir"], check=False, capture_output=True)
    if result.returncode:
        raise CliInputError("--repository must name an existing Git repository; use init --create-repository explicitly")


def _instance_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--repository", required=True, type=Path)
    parser.add_argument("--instance", required=True)


def build_parser() -> _Parser:
    parser = _Parser(prog="do-math")
    commands = parser.add_subparsers(dest="command", required=True)

    init = commands.add_parser("init", help="create a research instance")
    init.add_argument("--repository", required=True, type=Path)
    init.add_argument("--create-repository", action="store_true")
    init.add_argument("--workspace", required=True, type=Path)
    goal = init.add_mutually_exclusive_group(required=True)
    goal.add_argument("--goal")
    goal.add_argument("--goal-file")
    init.add_argument("--title", default="")
    init.add_argument("--goal-kind", choices=("mathematical", "research"), default="mathematical")
    init.add_argument("--policies-file")
    init.add_argument("--source", action="append", default=[], type=Path)
    init.add_argument("--config-file")
    init.add_argument("--model")
    init.add_argument("--effort")

    run = commands.add_parser("run", help="advance the workflow")
    _instance_arguments(run)
    run.add_argument("--max-steps", type=int)
    run.add_argument("--watch", action="store_true")

    status = commands.add_parser("status", help="show current status")
    _instance_arguments(status)
    status.add_argument("--json", action="store_true")

    for name in ("pause", "resume", "close"):
        command = commands.add_parser(name, help=f"queue and apply {name}")
        _instance_arguments(command)
        command.add_argument("--reason", default="")
        command.add_argument("--origin", choices=("user", "operator"), default="user")

    input_command = commands.add_parser("input", help="submit user input")
    _instance_arguments(input_command)
    incoming = input_command.add_mutually_exclusive_group(required=True)
    incoming.add_argument("--text")
    incoming.add_argument("--file")
    input_command.add_argument("--origin", choices=("user", "operator"), default="user")

    configure = commands.add_parser("configure", help="change explicit instance configuration")
    _instance_arguments(configure)
    configure.add_argument("--config-file", required=True)
    configure.add_argument("--origin", choices=("user", "operator"), default="user")

    request = commands.add_parser("request", help="queue a model-free activity request")
    _instance_arguments(request)
    request.add_argument("--role", required=True, choices=(
        "research_preparation", "research_plan", "supplemental_research", "operational_review", "maintenance",
    ))
    request.add_argument("--target")
    reason = request.add_mutually_exclusive_group()
    reason.add_argument("--reason")
    reason.add_argument("--text")
    request.add_argument("--origin", choices=("user", "operator"), default="user")

    for name in ("decision", "knowledge", "trust", "external", "conversation"):
        command = commands.add_parser(name, help=f"apply a structured {name} control")
        _instance_arguments(command)
        command.add_argument("--file", required=True)
        command.add_argument("--origin", choices=("user", "operator"), default="user")

    source = commands.add_parser("source", help="import an exact local source file")
    _instance_arguments(source)
    source.add_argument("--file", required=True)
    source.add_argument("--name")
    source.add_argument("--origin", choices=("user", "operator"), default="user")

    query = commands.add_parser("query", help="query records or raw snapshot files")
    _instance_arguments(query)
    query.add_argument("--snapshot")
    query.add_argument("--prefix", default="research/")
    query.add_argument("--text", default="")
    query.add_argument("--limit", type=int, default=50)
    query.add_argument("--cursor")
    query.add_argument("--files", action="store_true")
    query.add_argument("--kind")
    query.add_argument("--related-to")
    query.add_argument("--direction", choices=("both", "incoming", "outgoing"), default="both")

    read = commands.add_parser("read", help="read a record or raw snapshot file")
    _instance_arguments(read)
    read.add_argument("--snapshot")
    choice = read.add_mutually_exclusive_group(required=True)
    choice.add_argument("--id")
    choice.add_argument("--path")
    read.add_argument("--output", type=Path)

    export = commands.add_parser("export", help="export a snapshot")
    _instance_arguments(export)
    export.add_argument("--destination", required=True, type=Path)
    export.add_argument("--snapshot")
    export.add_argument("--all", action="store_true")

    check = commands.add_parser("check", help="check persisted workflow relations")
    _instance_arguments(check)

    profile = commands.add_parser("profile", help="inspect the installed Codex CLI surface")
    profile.add_argument("--codex-path")

    operator = commands.add_parser("operator", help="manage the independent scheduled operator")
    operator.add_argument("mode", choices=("install", "uninstall", "status", "start", "start-operator", "check", "probe", "engine", "hold", "release"))
    _instance_arguments(operator)
    operator.add_argument("--workspace", type=Path)
    operator.add_argument("--reason", default="")
    return parser


def _control(args: argparse.Namespace, action: str, *, text: str = "", config: dict[str, Any] | None = None) -> dict[str, Any]:
    request = control(args.repository, args.instance, action, text=text, config=config,
                      origin=getattr(args, "origin", "user"))
    engine = ResearchEngine(args.repository, args.instance)
    try:
        status = engine.process_controls()
    except GitStateStoreLockError:
        return {**request, "effect": "pending engine processing", "lock": "busy"}
    outcome = next(h for h in reversed(engine.runtime["history"]) if
                   request["request_id"] in {h.get("request", {}).get("id"), h.get("request_id")})
    return {**request, "effect": "rejected" if outcome["kind"] == "rejected_user_control" else "applied",
            "reason": outcome.get("reason"), "status": status["status"], "snapshot": status["snapshot"],
            "config": engine.instance["config"] if action == "configure" else None}


def _operator_workspace(repository: Path, instance: str, supplied: Path | None = None) -> Path:
    actual = scheduled_operator.resolve_workspace(repository, instance)
    if supplied is not None:
        if supplied.resolve() != actual:
            raise CliInputError("--workspace must equal the instance workspace")
    return actual


def _reconcile_operator(repository: Path, instance: str, configuration: dict[str, Any]) -> dict[str, Any]:
    workspace = scheduled_operator.resolve_workspace(repository, instance)
    action = "install" if configuration["operator_enabled"] else "uninstall"
    return scheduled_operator.schedule(action, repository=repository, instance=instance, workspace=workspace,
                                       interval_seconds=configuration["operator_interval_seconds"],
                                       operator_timeout_seconds=configuration["operator_timeout_seconds"],
                                       engine_timeout_seconds=configuration["run_timeout_seconds"] + configuration["checkpoint_grace_seconds"])


def _schedule_failure(result: dict[str, Any], error: RuntimeError, instance: str) -> tuple[dict[str, Any], int]:
    result["operator_schedule"] = {"status": "failed", "error": str(error),
                                   "reconcile": f"operator install --instance {instance}"}
    return result, 5


def execute(args: argparse.Namespace) -> tuple[dict[str, Any] | str, int]:
    command = args.command
    if command == "init":
        _require_git(args.repository, args.create_repository)
        goal = args.goal if args.goal is not None else _text_file(args.goal_file)
        policies = "" if args.policies_file is None else _text_file(args.policies_file)
        config = {} if args.config_file is None else _json_file(args.config_file)
        if args.model is not None:
            config["model"] = args.model
        if args.effort is not None:
            config["effort"] = args.effort
        for source in args.source:
            if not source.is_file():
                raise CliInputError(f"--source is not a file: {source}")
        result = initialize(args.repository, goal=goal, workspace=args.workspace, config=config, title=args.title,
                            goal_kind=args.goal_kind, policies=policies, sources=args.source)
        _, initialized, _ = ResearchRepository(args.repository, result["instance_id"]).load()
        if initialized["config"]["operator_enabled"]:
            try:
                result["operator_schedule"] = _reconcile_operator(args.repository, result["instance_id"], initialized["config"])
            except RuntimeError as error:
                return _schedule_failure(result, error, result["instance_id"])
        return result, 0
    if command == "run":
        return ResearchEngine(args.repository, args.instance).run(max_steps=args.max_steps, watch=args.watch), 0
    if command == "status":
        status = ResearchEngine(args.repository, args.instance).status()
        if args.json:
            return status, 0
        return _human_status(status), 0
    if command in {"pause", "resume", "close"}:
        return _control(args, command, text=args.reason), 0
    if command == "input":
        return _control(args, "input", text=args.text if args.text is not None else _text_file(args.file)), 0
    if command == "configure":
        requested = _json_file(args.config_file)
        result = _control(args, "configure", config=requested)
        operator_keys = {"operator_enabled", "operator_interval_seconds", "operator_timeout_seconds", "operator_model", "operator_effort", "run_timeout_seconds", "checkpoint_grace_seconds"}
        if result["effect"] == "applied" and operator_keys.intersection(requested):
            try:
                result["operator_schedule"] = _reconcile_operator(args.repository, args.instance, result["config"])
            except RuntimeError as error:
                return _schedule_failure(result, error, args.instance)
        elif operator_keys.intersection(requested):
            result["operator_schedule"] = {"status": "pending", "reason": "run operator install or uninstall after the control is applied"}
        return result, 0
    if command == "request":
        return _control(args, "request", text=args.reason if args.reason is not None else args.text or "",
                        config={"role": args.role, "target": args.target}), 0
    if command in {"decision", "knowledge", "trust", "external", "conversation"}:
        payload = _json_file(args.file)
        return _control(args, command,
                        config={"change": payload} if command == "decision" else payload), 0
    if command == "source":
        path = Path(args.file).resolve()
        if not path.is_file():
            raise CliInputError(f"--file is not a file: {args.file}")
        return _control(args, "source", config={"path": str(path), "name": args.name or path.name}), 0
    if command == "query":
        if args.files:
            return ResearchRepository(args.repository, args.instance).query(snapshot=args.snapshot, prefix=args.prefix,
                                                                              text=args.text, limit=args.limit, cursor=args.cursor), 0
        from .engine import query_records
        return query_records(args.repository, args.instance, snapshot=args.snapshot, kind=args.kind, text=args.text,
                             limit=args.limit, cursor=args.cursor, related_to=args.related_to, direction=args.direction), 0
    if command == "read":
        if args.path is not None:
            raw = ResearchRepository(args.repository, args.instance).read(args.path, args.snapshot)
            if args.output is not None:
                args.output.parent.mkdir(parents=True, exist_ok=True)
                args.output.write_bytes(raw)
                return {"path": args.path, "snapshot": args.snapshot, "size": len(raw), "output": str(args.output)}, 0
            try:
                text = raw.decode("utf-8")
                return {"path": args.path, "snapshot": args.snapshot, "size": len(raw), "text": text}, 0
            except UnicodeDecodeError:
                return {"path": args.path, "snapshot": args.snapshot, "size": len(raw),
                        "base64": base64.b64encode(raw).decode("ascii")}, 0
        from .engine import read_record
        return read_record(args.repository, args.instance, args.id, snapshot=args.snapshot), 0
    if command == "export":
        prefixes = ("research/", "runtime/") if args.all else ("research/",)
        return ResearchRepository(args.repository, args.instance).export(args.destination, args.snapshot, prefixes), 0
    if command == "check":
        result = ResearchEngine(args.repository, args.instance).check()
        return result, 0 if result["passed"] else 1
    if command == "profile":
        path = args.codex_path or shutil.which("codex") or "codex"
        result = json_safe(CodexExecAdapter(path).describe())
        return result, 0 if result.get("verified") else 1
    if command == "operator":
        workspace = _operator_workspace(args.repository, args.instance, args.workspace)
        if command == "operator":
            mode = args.mode
            if mode in {"install", "uninstall", "status", "start", "start-operator"}:
                _, initialized, _ = ResearchRepository(args.repository, args.instance).load()
                configuration = initialized["config"]
                action = {"start": "start-engine", "start-operator": "start-operator"}.get(mode, mode)
                if action == "start-engine":
                    guard = scheduled_operator.engine_start_guard(args.repository, args.instance, workspace)
                    if guard["outcome"] != "startable":
                        return guard, 0
                return scheduled_operator.schedule(action, repository=args.repository, instance=args.instance, workspace=workspace,
                                                   interval_seconds=configuration.get("operator_interval_seconds", 7200),
                                                   operator_timeout_seconds=configuration.get("operator_timeout_seconds", 5400),
                                                   engine_timeout_seconds=configuration.get("run_timeout_seconds", 7200) + configuration.get("checkpoint_grace_seconds", 10)), 0
            if mode == "hold":
                marker = scheduled_operator.hold(workspace, reason=args.reason)
                pause = _control(args, "pause", text="User requested scheduled operator HOLD " + marker["id"])
                return {"hold": marker, "pause": pause}, 0
            if mode == "release":
                released = scheduled_operator.release(workspace)
                marker = released.get("released")
                expected = "User requested scheduled operator HOLD " + marker["id"] if marker else None
                if expected:
                    released["resume"] = _control(args, "resume", text="User released scheduled operator HOLD " + marker["id"],
                                                  config={"expected_user_pause_reason": expected})
                else:
                    released["resume"] = {"effect": "not_requested", "reason": "no HOLD was released"}
                return released, 0
            if mode == "engine":
                return scheduled_operator.run_engine(args.repository, args.instance, workspace), 0
            return scheduled_operator.check(args.repository, args.instance, workspace, probe=mode == "probe"), 0
    raise CliInputError("unknown command")


def _human_status(status: dict[str, Any]) -> str:
    budget = status["budget"]
    limits = {pool: "unlimited" if row["limit"] is None else row["limit"] for pool, row in budget.items()}
    tasks = status["tasks"]
    assurance = status["assurance"]
    task_text = ", ".join(f"{task['id']}={task['status']}" for task in tasks) or "none"
    unknown = ", ".join(f"{key}={value}" for key, value in assurance.items())
    return "\n".join((
        f"goal: {status['goal']}",
        f"goal_status: {status['goal_status']}",
        f"status: {status['status']}  snapshot: {status['snapshot']}",
        f"budget: work {budget['work']['used']}/{limits['work']}; operations {budget['operations']['used']}/{limits['operations']}",
        f"tasks: {task_text}",
        f"unknown or bounded scope: {unknown}",
    ))


def _emit(value: dict[str, Any] | str) -> None:
    if isinstance(value, str):
        print(value)
    else:
        print(json.dumps(json_safe(value), ensure_ascii=False, sort_keys=True))


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
        result, code = execute(args)
    except CliInputError as error:
        _emit({"kind": "input_error", "error": str(error)})
        return 2
    except (ValueError, TypeError, KeyError) as error:
        _emit({"kind": "input_error", "error": str(error)})
        return 2
    except (GitStateStoreConflict, GitStateStoreError, OSError, subprocess.SubprocessError) as error:
        _emit({"kind": "tool_error", "error": str(error)})
        return 5
    _emit(result)
    return code
