"""Command-line boundary for the do-math CLI workflow."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any

from .codex_adapter import CodexExecAdapter
from .claude_adapter import ClaudePrintAdapter
from .engine import ResearchEngine, control, initialize, json_safe
from .git_store import GitStateStoreConflict, GitStateStoreError, GitStateStoreLockError
from .engine import _repository as ResearchRepository
from . import scheduled_operator
from .repository import canonical_json


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


def _json_document(path: str) -> tuple[dict[str, Any], str]:
    try:
        text = Path(path).read_bytes().decode("utf-8")
        value = json.loads(text, object_pairs_hook=_pairs)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
        raise CliInputError(f"cannot read JSON file {path}: {error}") from error
    if not isinstance(value, dict):
        raise CliInputError("JSON configuration must be an object")
    return value, text


def _json_file(path: str) -> dict[str, Any]:
    return _json_document(path)[0]


def _text_file(path: str) -> str:
    try:
        return Path(path).read_bytes().decode("utf-8")
    except (OSError, UnicodeDecodeError) as error:
        raise CliInputError(f"cannot read text file {path}: {error}") from error


def _require_git(repository: Path, create: bool = False) -> None:
    if create:
        if repository.exists() and (not repository.is_dir() or any(repository.iterdir())):
            raise CliInputError("--create-repository accepts only a missing or empty directory")
        repository.mkdir(parents=True, exist_ok=True)
        result = subprocess.run(["git", "-C", str(repository), "init", "-q"], check=False, capture_output=True, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        if result.returncode:
            raise GitStateStoreError("git init failed")
    result = subprocess.run(["git", "-C", str(repository), "rev-parse", "--git-dir"], check=False, capture_output=True, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    if result.returncode:
        raise CliInputError("--repository must name an existing Git repository; use init --create-repository explicitly")


def _instance_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--repository", required=True, type=Path)
    parser.add_argument("--instance", required=True)


def build_parser() -> _Parser:
    parser = _Parser(prog="do-math")
    parser.add_argument('--describe', action='store_true', help='describe the code-defined JSON command contract')
    parser.add_argument('--request-file', help='execute one schema-version-5 JSON command request')
    commands = parser.add_subparsers(dest="command", required=True)

    init = commands.add_parser("init", help="create a research instance")
    init.add_argument("--repository", required=True, type=Path)
    init.add_argument("--create-repository", action="store_true")
    init.add_argument("--workspace", required=True, type=Path)
    goal = init.add_mutually_exclusive_group(required=True)
    goal.add_argument("--goal")
    goal.add_argument("--goal-file")
    init.add_argument("--title", default="")
    init.add_argument("--goal-kind", choices=("mathematical", "research"), default="mathematical",
                      help="mathematical is supported; research is reserved and currently unsupported")
    init.add_argument("--policies-file")
    init.add_argument("--source", action="append", default=[], type=Path)
    init.add_argument("--config-file")
    init.add_argument("--effort")

    run = commands.add_parser("run", help="advance the workflow")
    _instance_arguments(run)
    timeline = commands.add_parser("timeline", help="export executions from a fixed snapshot")
    _instance_arguments(timeline)
    timeline.add_argument("--snapshot")
    timeline.add_argument("--format", choices=("json", "csv"), default="json")
    timeline.add_argument("--timezone", default="Asia/Seoul")
    timeline.add_argument("--include-operator", action="store_true", help="also read separately observed local operator logs")
    run.add_argument("--max-steps", type=int)
    run.add_argument("--watch", action="store_true")

    status = commands.add_parser("status", help="show current status")
    _instance_arguments(status)
    status.add_argument("--json", action="store_true")
    status.add_argument('--snapshot')

    for name in ("pause", "resume", "close"):
        command = commands.add_parser(name, help=f"queue and apply {name}")
        _instance_arguments(command)
        command.add_argument("--reason", default="")
        command.add_argument("--origin", choices=("user", "operator"), default="user")
        command.add_argument("--request-id", help="stable retry identity; changed payloads are rejected")

    input_command = commands.add_parser("input", help="submit user input")
    _instance_arguments(input_command)
    incoming = input_command.add_mutually_exclusive_group(required=True)
    incoming.add_argument("--text")
    incoming.add_argument("--file")
    input_command.add_argument("--origin", choices=("user", "operator"), default="user")
    input_command.add_argument("--request-id", help="stable retry identity; changed payloads are rejected")
    input_command.add_argument("--responds-to", action="append", default=[], help="ID of an open user question answered by this input; repeat for multiple questions")

    configure = commands.add_parser("configure", help="change explicit instance configuration")
    _instance_arguments(configure)
    configure.add_argument("--config-file", required=True)
    configure.add_argument("--origin", choices=("user", "operator"), default="user")

    request = commands.add_parser("request", help="queue a model-free activity request")
    _instance_arguments(request)
    request_mode = request.add_mutually_exclusive_group(required=True)
    request_mode.add_argument("--role", choices=(
        "research_preparation", "research_plan", "supplemental_research", "operational_review", "maintenance",
    ))
    request_mode.add_argument("--retry-action", help="retry one held input overflow or failed initial interpretation; reuse a verified preserved native final when available")
    request.add_argument("--target")
    request.add_argument("--reason")
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
    query.add_argument("--prefix", help="file-query path prefix; requires --files (default: research/)")
    query.add_argument("--text", default="")
    query.add_argument("--limit", type=int, default=50)
    query.add_argument("--cursor")
    query.add_argument("--files", action="store_true")
    query.add_argument("--kind")
    query.add_argument("--related-to")
    query.add_argument("--direction", choices=("both", "incoming", "outgoing"),
                       help="relation direction; requires --related-to (default: both)")

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
    check.add_argument('--snapshot')
    check.add_argument('--kinds', nargs='+', help='inspection area names; default all registered areas')

    profile = commands.add_parser("profile", help="inspect the installed model CLI surface")
    profile.add_argument("--provider", choices=("codex", "claude"), default="codex")
    profile.add_argument("--codex-path")
    profile.add_argument("--claude-path")

    operator = commands.add_parser("operator", help="manage the independent scheduled operator")
    operator.add_argument("mode", choices=("install", "uninstall", "status", "start", "start-operator", "check", "probe", "engine", "wake", "hold", "release"))
    _instance_arguments(operator)
    operator.add_argument("--workspace", type=Path)
    operator.add_argument("--reason", default="")
    for name in ('configure', 'request', 'decision', 'knowledge', 'trust', 'external', 'conversation', 'source'):
        commands.choices[name].add_argument('--request-id', help='stable retry identity; changed payloads are rejected')
    for name in ('pause','resume','close','input','configure','request','decision','knowledge','trust','external','conversation','source'):
        commands.choices[name].add_argument('--idempotency-key', help='explicit key for an intentional new application of the same content')
    return parser


def _control(args: argparse.Namespace, action: str, *, text: str = "", config: dict[str, Any] | None = None) -> dict[str, Any]:
    explicit, key = getattr(args, 'request_id', None), getattr(args, 'idempotency_key', None)
    if explicit is not None and key is not None:
        raise CliInputError('request_id and idempotency_key are mutually exclusive')
    identity_config = config or {}
    if action == 'source':
        path = Path(identity_config['path'])
        raw = path.read_bytes()
        identity_config = {'name': identity_config.get('name') or path.name,
            'body_base64': base64.b64encode(raw).decode('ascii'), 'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}
    identifier = explicit if explicit is not None else control_request_id(args.instance, action, text=text, config=identity_config,
                                               origin=getattr(args,'origin','user'), idempotency_key=key)
    args._resolved_request_id = identifier
    extra = {'request_id': identifier}
    request = control(args.repository, args.instance, action, text=text, config=identity_config,
                      origin=getattr(args, "origin", "user"), **extra)
    # ENGINE's replay receipt is tied to the original publication. Do not run
    # unrelated pending controls or replace that receipt with current state.
    if request.get('effect') in {'applied', 'rejected'} and request.get('snapshot'):
        return request
    engine = ResearchEngine(args.repository, args.instance)
    try:
        engine.process_controls()
        outcome = engine.control_result(request['request_id'])
    except GitStateStoreLockError:
        return {**request, "effect": "pending engine processing", "lock": "busy"}
    except (ValueError, TypeError, KeyError) as error:
        # Admission already produced a receipt. Failure applying that accepted
        # control belongs to the implementation, not to the user's JSON parser.
        raise RuntimeError(f"accepted request {request['request_id']} could not be processed: {error}") from error
    if outcome is None:
        return {**request, 'effect': 'pending engine processing', 'next_owner': 'engine'}
    return {**request, **outcome}


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
                                       operator_timeout_seconds=configuration["operator_timeout_seconds"])


def _schedule_failure(result: dict[str, Any], error: RuntimeError, instance: str) -> tuple[dict[str, Any], int]:
    result["operator_schedule"] = {"status": "failed", "error": str(error),
                                   "reconcile": f"operator install --instance {instance}"}
    return result, 5


def execute(args: argparse.Namespace) -> tuple[dict[str, Any] | str, int]:
    command = args.command
    if command == "timeline":
        from .reporting import timeline, timeline_csv
        value = timeline(args.repository, args.instance, snapshot=args.snapshot, timezone_name=args.timezone,
                         include_operator=args.include_operator)
        return (timeline_csv(value) if args.format == "csv" else value), 0
    if command == "init":
        if args.goal_kind != "mathematical":
            raise CliInputError("unsupported goal_kind: research; this entrypoint currently supports mathematical only")
        _require_git(args.repository, args.create_repository)
        goal = args.goal if args.goal is not None else _text_file(args.goal_file)
        policies = "" if args.policies_file is None else _text_file(args.policies_file)
        config = {} if args.config_file is None else _json_file(args.config_file)
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
        from .reporting import snapshot_report, render_human_report
        if args.snapshot is None:
            status = ResearchEngine(args.repository, args.instance).status()
            return (status if args.json else _human_status(status)), 0
        status = snapshot_report(args.repository, args.instance, snapshot=args.snapshot)
        if args.json:
            return status, 0
        return render_human_report(status), 0
    if command in {"pause", "resume", "close"}:
        return _control(args, command, text=args.reason), 0
    if command == "input":
        return _control(args, "input", text=args.text if args.text is not None else _text_file(args.file), config={"responds_to": args.responds_to}), 0
    if command == "configure":
        requested = _json_file(args.config_file)
        result = _control(args, "configure", config=requested)
        operator_keys = {"operator_enabled", "operator_interval_seconds", "operator_timeout_seconds", "operator_effort", "checkpoint_grace_seconds"}
        if operator_keys.intersection(requested) and result['effect'] == 'rejected':
            result['operator_schedule'] = {'status': 'not_applied', 'reason': 'configuration was rejected'}
        elif operator_keys.intersection(requested) and result.get('replayed') and result['effect'] == 'applied':
            result['operator_schedule'] = {'status': 'not_reapplied',
                'reason': 'original control receipt replayed; explicit operator install or uninstall reconciles current configuration'}
        elif result["effect"] == "applied" and operator_keys.intersection(requested):
            try:
                result["operator_schedule"] = _reconcile_operator(args.repository, args.instance, result["config"])
            except RuntimeError as error:
                return _schedule_failure(result, error, args.instance)
        elif operator_keys.intersection(requested):
            result["operator_schedule"] = {"status": "pending", "reason": "run operator install or uninstall after the control is applied"}
        return result, 0
    if command == "request":
        if args.retry_action is not None:
            if args.target is not None or args.reason is not None:
                raise CliInputError("--retry-action cannot be combined with target or request text")
            return _control(args, "request", config={"retry_action": args.retry_action}), 0
        return _control(args, "request", text=args.reason or "",
                        config={"role": args.role, "target": args.target}), 0
    if command in {"decision", "knowledge", "trust", "external", "conversation"}:
        payload, original = _json_document(args.file)
        return _control(args, command, text=original,
                        config={"change": payload} if command == "decision" else payload), 0
    if command == "source":
        path = Path(args.file).resolve()
        if not path.is_file():
            raise CliInputError(f"--file is not a file: {args.file}")
        return _control(args, "source", config={"path": str(path), "name": args.name or path.name}), 0
    if command == "query":
        if args.files:
            if args.kind is not None or args.related_to is not None or args.direction is not None:
                raise CliInputError("--files cannot be combined with --kind, --related-to or --direction")
            prefix = args.prefix if args.prefix is not None else "research/"
            value = ResearchRepository(args.repository, args.instance).query(snapshot=args.snapshot, prefix=prefix,
                                                                               text=args.text, limit=args.limit, cursor=args.cursor)
            value["provenance"] = {"snapshot": value["snapshot"],
                                   "filters": {"prefix": prefix, "text": args.text, "limit": args.limit,
                                               "cursor": args.cursor},
                                   "page": {"loaded": len(value["items"]), "total": value["total"],
                                            "next_cursor": value["next_cursor"], "truncated": value["truncated"]}}
            return value, 0
        if args.prefix is not None:
            raise CliInputError("--prefix requires --files")
        if args.direction is not None and args.related_to is None:
            raise CliInputError("--direction requires --related-to")
        from .engine import query_records
        return query_records(args.repository, args.instance, snapshot=args.snapshot, kind=args.kind, text=args.text,
                             limit=args.limit, cursor=args.cursor, related_to=args.related_to,
                             direction=args.direction if args.direction is not None else "both"), 0
    if command == "read":
        if args.output is not None and args.path is None:
            raise CliInputError("--output requires --path")
        if args.path is not None:
            store = ResearchRepository(args.repository, args.instance)
            resolved_snapshot = store._resolve_snapshot(args.snapshot)
            raw = store.read(args.path, resolved_snapshot)
            provenance = {"snapshot": resolved_snapshot, "path": args.path, "sha256": hashlib.sha256(raw).hexdigest(),
                          "range": {"start": 0, "end": len(raw), "total": len(raw)}}
            if args.output is not None:
                args.output.parent.mkdir(parents=True, exist_ok=True)
                args.output.write_bytes(raw)
                return {"path": args.path, "snapshot": resolved_snapshot, "size": len(raw), "output": str(args.output),
                        "sha256": provenance["sha256"], "provenance": provenance}, 0
            try:
                text = raw.decode("utf-8")
                return {"path": args.path, "snapshot": resolved_snapshot, "size": len(raw), "text": text,
                        "sha256": provenance["sha256"], "provenance": provenance}, 0
            except UnicodeDecodeError:
                return {"path": args.path, "snapshot": resolved_snapshot, "size": len(raw),
                        "base64": base64.b64encode(raw).decode("ascii"), "sha256": provenance["sha256"],
                        "provenance": provenance}, 0
        from .engine import read_record
        return read_record(args.repository, args.instance, args.id, snapshot=args.snapshot), 0
    if command == "export":
        prefixes = ("research/", "runtime/") if args.all else ("research/",)
        return ResearchRepository(args.repository, args.instance).export(args.destination, args.snapshot, prefixes), 0
    if command == "check":
        from .state_checks import inspection_exit_code
        result = ResearchEngine(args.repository, args.instance).check(snapshot=args.snapshot, requested_areas=args.kinds)
        code = inspection_exit_code(result['inspection'])
        result.update(exit_code=code, passed=code == 0)
        return result, code
    if command == "profile":
        if args.provider == "claude":
            if args.codex_path:
                raise CliInputError("--codex-path requires --provider codex")
            path = args.claude_path or shutil.which("claude") or "claude"
            adapter = ClaudePrintAdapter(path)
        else:
            if args.claude_path:
                raise CliInputError("--claude-path requires --provider claude")
            path = args.codex_path or shutil.which("codex") or "codex"
            adapter = CodexExecAdapter(path)
        result = json_safe(adapter.describe())
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
                                                   operator_timeout_seconds=configuration.get("operator_timeout_seconds", 5400)), 0
            if mode == "hold":
                marker = scheduled_operator.hold(workspace, reason=args.reason)
                pause = _control(args, "pause", text="User requested scheduled operator HOLD " + marker["id"])
                try:
                    cleanup = scheduled_operator.schedule("cancel-wake", repository=args.repository, instance=args.instance, workspace=workspace)
                    (workspace / "operator/wake-registration.json").unlink(missing_ok=True)
                except (RuntimeError, OSError) as error:
                    cleanup = {"status": "failed", "error": str(error), "hold_still_blocks_wake": True}
                return {"hold": marker, "pause": pause, "wake_cleanup": cleanup}, 0
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
            if mode == "wake":
                return scheduled_operator.wake(args.repository, args.instance, workspace), 0
            if mode == "engine":
                return scheduled_operator.run_engine(args.repository, args.instance, workspace), 0
            return scheduled_operator.check(args.repository, args.instance, workspace, probe=mode == "probe"), 0
    raise CliInputError("unknown command")


def _human_status(status: dict[str, Any]) -> str:
    from .reporting import display_time
    budget = status["budget"]
    budget_text = "sessions: " + "; ".join(pool + " " + ", ".join(
        f"{model} {row['used']}/{row['limit']}" for model, row in values.items()) for pool, values in budget.items())
    tasks = status["tasks"]
    assurance = status["assurance"]
    task_text = ", ".join(f"{task['id']}={task['status']}" for task in tasks) or "none"
    unknown = ", ".join(f"{key}={value}" for key, value in assurance.items())
    lines = [
        f"goal: {status['goal']}",
        f"goal_status: {status['goal_status']}",
        f"status: {status['status']}  snapshot: {status['snapshot']}",
        budget_text,
        f"tasks: {task_text}",
        "observed (Asia/Seoul): " + str(display_time(status.get('research_observed_at')) or 'unknown'),
        f"unknown or bounded scope: {unknown}",
    ]
    for task in tasks:
        waits = ', '.join(row.get('kind', 'unknown') for row in task.get('waits', [])) or 'none'
        lines.append(f"  {task['id']} revision={task.get('revision', 'unknown')} stage={task['status']} "
                     f"assessment_pending={str(task.get('assessment_pending', False)).lower()} "
                     f"active_records={','.join(task.get('active_execution_ids', [])) or 'none'} "
                     f"queued={','.join(str(value) for value in task.get('selected_actions', [])) or 'none'} "
                     f"waits={waits} next={task.get('next_owner') or 'none'}")
    for name, gate in status.get('provider_waits', {}).get('providers', {}).items():
        lines.append(f"provider {name}: {gate['state']} retry={display_time(gate.get('retry_at')) or 'unknown'} generation={gate['generation']}")
    if status.get('inspection'):
        from .reporting import render_human_report
        lines.append(render_human_report(status))
    else:
        lines.append('inspection: not supplied; research effectiveness: not evaluated')
        from .reporting import render_dispatch_waits
        lines.extend(render_dispatch_waits(status))
    return '\n'.join(lines)


def control_request_id(instance_id, action, *, text='', config=None, origin='user', idempotency_key=None):
    """Hash normalized content, not mutable admission state or delivery time.

    Source controls must pass their normalized name/body/hash/size payload.
    ENGINE may call this after resolving source bytes, before inbox admission.
    """
    if idempotency_key is not None and (not isinstance(idempotency_key,str) or not idempotency_key):
        raise CliInputError('idempotency_key must be a nonempty string')
    value = {'schema_version':5,'command':action,'caller':origin,
             'payload':{'instance_id':instance_id,'text':text,'config':config or {}},
             'idempotency_key':idempotency_key}
    return 'UC-' + hashlib.sha256(canonical_json(value)).hexdigest()


def _command_parsers(parser):
    return next(action.choices for action in parser._actions if isinstance(action,argparse._SubParsersAction))


def _request_schema(parser):
    return {'type':'object','required':['schema_version','command','payload'],'additionalProperties':False,
        'properties':{'schema_version':{'type':'integer','const':5},
            'command':{'type':'string','enum':list(_command_parsers(parser))},
            'caller':{'type':'string','enum':['user','operator']},'payload':{'type':'object'},
            'request_id':{'type':'string','minLength':1,'maxLength':128,'pattern':'^[A-Za-z0-9_-]+$'},
            'idempotency_key':{'type':'string','minLength':1}}}


def describe_commands(parser, command=None):
    commands = {}
    for name, subparser in _command_parsers(parser).items():
        if command is not None and name != command:
            continue
        properties, required = {}, []
        for action in subparser._actions:
            if action.dest == 'help':
                continue
            scalar = {'type':'integer' if action.type is int else 'string'}
            if action.choices is not None:
                scalar['enum'] = list(action.choices)
            definition = ({'type':'boolean'} if isinstance(action,argparse._StoreTrueAction) else
                          {'type':'array','items':scalar} if isinstance(action,argparse._AppendAction) or action.nargs in ('+','*') else scalar)
            if action.default is not None and action.default != argparse.SUPPRESS:
                definition['default'] = action.default
            if action.help:
                definition['description'] = action.help
            properties[action.dest] = definition
            if action.required:
                required.append(action.dest)
        schema = {'type':'object','properties':properties,'required':required,'additionalProperties':False}
        if name == 'query':
            schema['allOf'] = [{
                'if': {'properties': {'files': {'const': True}}, 'required': ['files']},
                'then': {'not': {'anyOf': [{'required': [key]} for key in ('kind', 'related_to', 'direction')]}},
                'else': {'not': {'required': ['prefix']}},
            }]
            schema['dependentRequired'] = {'direction': ['related_to']}
        groups = []
        for group in subparser._mutually_exclusive_groups:
            names = [action.dest for action in group._group_actions]
            groups.append({'names':names,'required':group.required})
        commands[name] = {'payload_schema':schema,'exclusive_groups':groups}
    if command is not None and not commands:
        raise CliInputError('unknown command for --describe')
    return {'schema_version':5,'commands':commands,'request_schema':_request_schema(parser),
        'request_fields':['schema_version','command','caller','payload','request_id','idempotency_key'],
        'response_fields':['schema_version','request_id','command','exit_code','result OR error'],
        'inspection_exit_codes':{'healthy':0,'degraded':1,'blocked':1,'incomplete':1},
        'error_exit_codes':{'input_error':2,'tool_error':5,'contract_error':5},
        'caller_authority':'caller is a declared origin, not strong authentication'}


def _json_arguments(parser, request):
    from jsonschema import Draft202012Validator
    errors = list(Draft202012Validator(_request_schema(parser)).iter_errors(request))
    if errors:
        raise CliInputError('invalid command request: ' + errors[0].message)
    command = request.get('command')
    description = describe_commands(parser, command)
    if command not in description['commands']:
        raise CliInputError('command request requires a command')
    payload = request.get('payload')
    errors = list(Draft202012Validator(description['commands'][command]['payload_schema']).iter_errors(payload))
    if errors:
        raise CliInputError('invalid command payload: ' + errors[0].message)
    payload = dict(payload)
    subparser = _command_parsers(parser)[command]
    known = {action.dest:action for action in subparser._actions}
    if 'caller' in request:
        if request['caller'] not in {'user','operator'}:
            raise CliInputError('caller must be user or operator')
        if 'origin' in known:
            if 'origin' in payload and payload['origin'] != request['caller']:
                raise CliInputError('caller differs from payload origin')
            payload['origin'] = request['caller']
    for key in ('request_id','idempotency_key'):
        if key in request:
            if key not in known or key in payload:
                raise CliInputError('unexpected or duplicate ' + key)
            payload[key] = request[key]
    argv = [command]
    for name, value in payload.items():
        action = known[name]
        flag = next((flag for flag in action.option_strings if flag.startswith('--')),None)
        if isinstance(action,argparse._StoreTrueAction):
            if value:
                argv.append(flag)
        elif isinstance(action,argparse._AppendAction):
            for item in value:
                argv.append(f"{flag}={item}")
        elif action.nargs in ('+','*'):
            argv.extend([flag,*map(str,value)])
        else:
            argv.append(f"{flag}={value}" if flag else str(value))
    args = parser.parse_args(argv)
    if command == 'status':
        args.json = True
    return args


def _emit(value, *, command=None, request_id=None, code=0, error=False, force_json=False) -> None:
    if isinstance(value, str) and not force_json:
        print(value)
    else:
        envelope = {'schema_version':5,'response_contract':'do-math-cli/5','request_id':request_id,
                    'command':command,'exit_code':code,'error' if error else 'result':value}
        print(json.dumps(json_safe(envelope), ensure_ascii=False, sort_keys=True))


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    argv = list(sys.argv[1:] if argv is None else argv)
    command, identifier = None, None
    force_json = bool(argv and argv[0] == '--request-file')
    try:
        if argv and argv[0] == '--describe':
            if len(argv) > 2:
                raise CliInputError('--describe accepts at most one command name')
            result = describe_commands(parser,argv[1] if len(argv)==2 else None)
            _emit(result,command='describe',request_id='QR-'+hashlib.sha256(canonical_json(argv)).hexdigest())
            return 0
        if force_json:
            if len(argv) != 2:
                raise CliInputError('--request-file accepts exactly one path')
            request = _json_file(argv[1])
            command = request.get('command')
            args = _json_arguments(parser,request)
        else:
            args = parser.parse_args(argv)
        command = args.command
        normalized = {key:(str(value) if isinstance(value,Path) else value) for key,value in vars(args).items()
                      if key not in {'describe','request_file','json'}}
        identifier = 'QR-' + hashlib.sha256(canonical_json(json_safe(normalized))).hexdigest()
        try:
            result, code = execute(args)
        finally:
            identifier = getattr(args, '_resolved_request_id', identifier)
    except CliInputError as error:
        _emit({"kind": "input_error", "message": str(error), 'next_owner': 'user', 'retryable': False}, command=command,request_id=identifier,code=2,error=True)
        return 2
    except ValueError as error:
        _emit({"kind": "input_error", "message": str(error), 'next_owner': 'user', 'retryable': False}, command=command,request_id=identifier,code=2,error=True)
        return 2
    except (TypeError, KeyError) as error:
        _emit({'kind': 'contract_error', 'message': str(error), 'next_owner': 'maintenance', 'retryable': False}, command=command,request_id=identifier,code=5,error=True)
        return 5
    except (GitStateStoreConflict, GitStateStoreError, OSError, subprocess.SubprocessError) as error:
        _emit({"kind": "tool_error", "message": str(error), 'next_owner': 'operator',
               'retryable': isinstance(error, (GitStateStoreConflict, GitStateStoreLockError))}, command=command,request_id=identifier,code=5,error=True)
        return 5
    except RuntimeError as error:
        _emit({'kind': 'contract_error', 'message': str(error), 'next_owner': 'maintenance', 'retryable': False}, command=command,request_id=identifier,code=5,error=True)
        return 5
    if isinstance(result,dict):
        identifier = result.get('request_id',identifier)
    _emit(result,command=command,request_id=identifier,code=code,force_json=force_json)
    return code
