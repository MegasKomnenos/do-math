"""Command-line boundary for the do-math CLI workflow."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

from .claude_adapter import provider_adapter
from .contracts import RESPONSE_CONTRACT_ID
from .control_contracts import REQUEST_ID_PATTERN
from .engine import ResearchEngine, control, initialize, query_records, read_record
from .git_store import GitStateStoreConflict, GitStateStoreError, GitStateStoreLockError
from .payloads import json_safe
from . import scheduled_operator
from .file_io import strict_json_loads
from .repository import ResearchRepository, canonical_json, exact_content_hash
from .state_checks import inspection_exit_code

# Envelope fields every response carries, before its ``result`` or ``error``.
RESPONSE_FIELDS = ('schema_version', 'response_contract', 'request_id', 'command', 'exit_code')
# The JSON wire version of requests, responses and ``--describe``.
WIRE_VERSION = 5
# The exit code of each error kind ``main`` reports; ``--describe`` publishes this table.
ERROR_EXIT_CODES = {'input_error': 2, 'tool_error': 5, 'contract_error': 5}


class CliInputError(ValueError):
    """A command-line argument or supplied local input is invalid."""


class _Parser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise CliInputError(message)


def _json_document(path: str) -> tuple[dict[str, Any], str]:
    try:
        text = Path(path).read_bytes().decode("utf-8")
        value = strict_json_loads(text)
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
    original = init.add_mutually_exclusive_group()
    original.add_argument('--request-text', help='complete original request, including constraints')
    original.add_argument('--request-text-file', help='UTF-8 complete original request')
    init.add_argument("--title", default="")
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
    timeline.add_argument('--include-operations', action='store_true', help='include separately observed operational phase timings')
    run.add_argument("--max-steps", type=int)
    run.add_argument("--watch", action="store_true")
    run.add_argument('--until-active', action='store_true', help='return after activation before dispatching research')

    status = commands.add_parser("status", help="show current status")
    _instance_arguments(status)
    status.add_argument("--json", action="store_true")
    status.add_argument('--snapshot')

    for name in ("pause", "resume", "close", "quiesce", "release-quiesce"):
        command = commands.add_parser(name, help=f"queue and apply {name}")
        _instance_arguments(command)
        command.add_argument("--reason", default="")
        command.add_argument("--origin", choices=("user", "operator"), default="user")
        command.add_argument("--request-id", help="stable retry identity; changed payloads are rejected")
        if name == 'release-quiesce':
            command.add_argument('--fence', required=True)

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
    request_mode.add_argument("--assessment-reassessment-file", help="report exact original assessment and defect evidence for bounded independent reassessment")
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
    choose = commands.add_parser('select-profile', help='resolve the current role/task model requirement without execution')
    _instance_arguments(choose)
    choose.add_argument('--role', required=True)
    choose.add_argument('--task')
    choose.add_argument('--snapshot')
    draft = commands.add_parser('prepare-import-approval', help='write exact checked-import approval coordinates without applying them')
    _instance_arguments(draft)
    draft.add_argument('--import-id', required=True)
    draft.add_argument('--snapshot')
    draft.add_argument('--output', required=True, type=Path)

    operator = commands.add_parser("operator", help="manage the independent scheduled operator")
    operator.add_argument("mode", choices=("install", "uninstall", "status", "start", "start-operator", "check", "probe", "engine", "wake", "hold", "release"))
    _instance_arguments(operator)
    operator.add_argument("--workspace", type=Path)
    operator.add_argument("--reason", default="")
    for name in ('configure', 'request', 'decision', 'knowledge', 'trust', 'external', 'conversation', 'source'):
        commands.choices[name].add_argument('--request-id', help='stable retry identity; changed payloads are rejected')
    for name in ('pause','resume','close','quiesce','release-quiesce','input','configure','request','decision','knowledge','trust','external','conversation','source'):
        commands.choices[name].add_argument('--idempotency-key', help='explicit key for an intentional new application of the same content')
    return parser


def _control(args: argparse.Namespace, action: str, *, text: str = "", config: dict[str, Any] | None = None) -> dict[str, Any]:
    # ENGINE normalizes a source and derives the request ID; the CLI reports the ID it returns.
    request = control(args.repository, args.instance, action, text=text, config=config or {},
                      origin=getattr(args, "origin", "user"), request_id=getattr(args, 'request_id', None),
                      idempotency_key=getattr(args, 'idempotency_key', None))
    args._resolved_request_id = request['request_id']
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


def _schedule_failure(result: dict[str, Any], error: Exception, repository: Path,
                      instance: str) -> tuple[dict[str, Any], int]:
    mode = "install" if result.get("config", {}).get("operator_enabled", True) else "uninstall"
    def quote(value):
        return "'" + str(value).replace("'", "''") + "'"
    entrypoint = Path(__file__).resolve().parents[1] / "do_math.py"
    reconcile = ("& " + quote(sys.executable) + " " + quote(entrypoint)
                 + " operator " + mode + " --repository " + quote(repository.resolve())
                 + " --instance " + quote(instance))
    result["operator_schedule"] = {"status": "failed", "error": str(error), "reconcile": reconcile}
    return result, ERROR_EXIT_CODES['tool_error']


def execute(args: argparse.Namespace) -> tuple[dict[str, Any] | str, int]:
    command = args.command
    if command == "timeline":
        from .reporting import timeline, timeline_csv
        value = timeline(args.repository, args.instance, snapshot=args.snapshot, timezone_name=args.timezone,
                         include_operations=args.include_operations)
        return (timeline_csv(value) if args.format == "csv" else value), 0
    if command == "init":
        _require_git(args.repository, args.create_repository)
        goal = args.goal if args.goal is not None else _text_file(args.goal_file)
        config = {} if args.config_file is None else _json_file(args.config_file)
        if args.effort is not None:
            config["effort"] = args.effort
        for source in args.source:
            if not source.is_file():
                raise CliInputError(f"--source is not a file: {source}")
        result = initialize(args.repository, goal=goal, workspace=args.workspace, config=config, title=args.title,
                            sources=args.source,
                            source_input=args.request_text if args.request_text is not None else
                                _text_file(args.request_text_file) if args.request_text_file else goal)
        _, initialized, _ = ResearchRepository(args.repository, result["instance_id"]).load()
        if initialized["config"]["operator_enabled"]:
            try:
                result["operator_schedule"] = _reconcile_operator(args.repository, result["instance_id"], initialized["config"])
            except (RuntimeError, OSError, subprocess.SubprocessError) as error:
                return _schedule_failure(result, error, args.repository, result["instance_id"])
        return result, 0
    if command == "run":
        return ResearchEngine(args.repository, args.instance).run(max_steps=args.max_steps, watch=args.watch,
                                                                 until_active=args.until_active), 0
    if command == 'select-profile':
        from .model_policy import selection
        from .execution_profiles import match_profile_ref
        head, instance, runtime = ResearchRepository(args.repository, args.instance).load(args.snapshot)
        if args.role not in instance['role_profile_refs']:
            raise CliInputError('unknown execution role')
        if args.task and args.task not in runtime['tasks']:
            raise CliInputError('unknown task')
        selected = selection(instance['config'], {'role':args.role, 'target':args.task},
                             runtime['tasks'], instance['knowledge'], instance=instance)
        return {'snapshot':head, 'selection':selected,
                'profile':match_profile_ref(instance['execution_profiles'], selected['profile_ref'])}, 0
    if command == 'prepare-import-approval':
        from .governance import import_approval_draft
        engine = ResearchEngine(args.repository, args.instance)
        engine.head, engine.instance, engine.runtime = engine.store.load(args.snapshot)
        value = import_approval_draft(engine.instance, engine.runtime, args.import_id,
                                     owner_handlers=engine._governance_owner_handlers())
        with args.output.open('xb') as stream:
            stream.write(canonical_json(value))
        return {'snapshot':engine.head, 'output':str(args.output.resolve()),
                'decision':value, 'effect':'draft_only'}, 0
    if command == "status":
        from .reporting import snapshot_report, render_human_report
        # The current head with this host's observations, or one stored snapshot without them.
        status = (ResearchEngine(args.repository, args.instance).status() if args.snapshot is None
                  else snapshot_report(args.repository, args.instance, snapshot=args.snapshot))
        return (status if args.json else render_human_report(status)), 0
    if command == 'quiesce':
        return _control(args, 'quiesce', text=args.reason), 0
    if command == 'release-quiesce':
        return _control(args, 'release_quiesce', text=args.reason, config={'fence_id':args.fence}), 0
    if command in {"pause", "resume", "close"}:
        return _control(args, command, text=args.reason), 0
    if command == "input":
        return _control(args, "input", text=args.text if args.text is not None else _text_file(args.file), config={"responds_to": args.responds_to}), 0
    if command == "configure":
        requested = _json_file(args.config_file)
        result = _control(args, "configure", config=requested)
        operator_keys = {"operator_enabled", "operator_interval_seconds", "operator_timeout_seconds", "operator_effort"}
        if operator_keys.intersection(requested) and result['effect'] == 'rejected':
            result['operator_schedule'] = {'status': 'not_applied', 'reason': 'configuration was rejected'}
        elif operator_keys.intersection(requested) and result.get('replayed') and result['effect'] == 'applied':
            result['operator_schedule'] = {'status': 'not_reapplied',
                'reason': 'original control receipt replayed; explicit operator install or uninstall reconciles current configuration'}
        elif result["effect"] == "applied" and operator_keys.intersection(requested):
            try:
                result["operator_schedule"] = _reconcile_operator(args.repository, args.instance, result["config"])
            except (RuntimeError, OSError, subprocess.SubprocessError) as error:
                return _schedule_failure(result, error, args.repository, args.instance)
        elif operator_keys.intersection(requested):
            result["operator_schedule"] = {"status": "pending", "reason": "run operator install or uninstall after the control is applied"}
        return result, 0
    if command == "request":
        if args.assessment_reassessment_file is not None:
            if args.target is not None or args.reason is not None:
                raise CliInputError("--assessment-reassessment-file cannot be combined with target or request text")
            payload, original = _json_document(args.assessment_reassessment_file)
            return _control(args, "request", text=original,
                            config={"role": "identity_review", "assessment_reassessment": payload}), 0
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
        return read_record(args.repository, args.instance, args.id, snapshot=args.snapshot), 0
    if command == "export":
        prefixes = ("research/", "runtime/") if args.all else ("research/",)
        return ResearchRepository(args.repository, args.instance).export(args.destination, args.snapshot, prefixes), 0
    if command == "check":
        result = ResearchEngine(args.repository, args.instance).check(snapshot=args.snapshot, requested_areas=args.kinds)
        code = inspection_exit_code(result['inspection'])
        result.update(exit_code=code, passed=code == 0)
        return result, code
    if command == "profile":
        paths = {"codex": args.codex_path, "claude": args.claude_path}
        other = next(name for name in paths if name != args.provider)
        if paths[other]:
            raise CliInputError(f"--{other}-path requires --provider {other}")
        result = json_safe(provider_adapter(args.provider, paths[args.provider]).describe())
        return result, 0 if result.get("verified") else 1
    if command == "operator":
        workspace = _operator_workspace(args.repository, args.instance, args.workspace)
        mode = args.mode
        if mode in {"install", "uninstall", "status", "start", "start-operator"}:
            action = {"start": "start-engine", "start-operator": "start-operator"}.get(mode, mode)
            if action == "start-engine":
                guard = scheduled_operator.engine_start_guard(args.repository, args.instance, workspace)
                if guard["outcome"] != "startable":
                    return guard, 0
            settings = {}
            if action == "install":
                configuration = ResearchRepository(args.repository, args.instance).load()[1]["config"]
                settings = {"interval_seconds": configuration["operator_interval_seconds"],
                            "operator_timeout_seconds": configuration["operator_timeout_seconds"]}
            return scheduled_operator.schedule(action, repository=args.repository, instance=args.instance,
                                               workspace=workspace, **settings), 0
        if mode == "hold":
            marker = scheduled_operator.hold(workspace, reason=args.reason)
            pause = _control(args, "pause", text=scheduled_operator.hold_pause_reason(marker["id"]))
            try:
                cleanup = scheduled_operator.cancel_wake(args.repository, args.instance, workspace)
            except (RuntimeError, OSError) as error:
                cleanup = {"status": "failed", "error": str(error), "hold_still_blocks_wake": True}
            return {"hold": marker, "pause": pause, "wake_cleanup": cleanup}, 0
        if mode == "release":
            released = scheduled_operator.release(workspace)
            marker = released.get("released")
            expected = scheduled_operator.hold_pause_reason(marker["id"]) if marker else None
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


def _command_parsers(parser):
    return next(action.choices for action in parser._actions if isinstance(action,argparse._SubParsersAction))


def _request_schema(parser):
    return {'type':'object','required':['schema_version','command','payload'],'additionalProperties':False,
        'properties':{'schema_version':{'type':'integer','const':WIRE_VERSION},
            'command':{'type':'string','enum':list(_command_parsers(parser))},
            'caller':{'type':'string','enum':['user','operator']},'payload':{'type':'object'},
            'request_id':{'type':'string','pattern':REQUEST_ID_PATTERN},
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
    request_schema = _request_schema(parser)
    return {'schema_version':WIRE_VERSION,'commands':commands,'request_schema':request_schema,
        'request_fields':list(request_schema['properties']),
        'response_fields':[*RESPONSE_FIELDS,'result OR error'],
        'inspection_exit_codes':{status:inspection_exit_code({'status':status})
                                 for status in ('healthy','degraded','blocked','incomplete')},
        'error_exit_codes':dict(ERROR_EXIT_CODES),
        'caller_authority':'caller is a declared origin, not strong authentication'}


def _json_arguments(parser, request):
    from jsonschema import Draft202012Validator
    errors = list(Draft202012Validator(_request_schema(parser)).iter_errors(request))
    if errors:
        raise CliInputError('invalid command request: ' + errors[0].message)
    # The request schema has already fixed the command and caller to their enums.
    command = request['command']
    description = describe_commands(parser, command)
    payload = request['payload']
    errors = list(Draft202012Validator(description['commands'][command]['payload_schema']).iter_errors(payload))
    if errors:
        raise CliInputError('invalid command payload: ' + errors[0].message)
    payload = dict(payload)
    subparser = _command_parsers(parser)[command]
    known = {action.dest:action for action in subparser._actions}
    if 'caller' in request:
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
        fields = dict(zip(RESPONSE_FIELDS, (WIRE_VERSION, RESPONSE_CONTRACT_ID, request_id, command, code)))
        envelope = {**fields, 'error' if error else 'result': value}
        print(json.dumps(json_safe(envelope), ensure_ascii=False, sort_keys=True))


def _fail(kind, error, next_owner, retryable, command, request_id) -> int:
    code = ERROR_EXIT_CODES[kind]
    _emit({'kind': kind, 'message': str(error), 'next_owner': next_owner, 'retryable': retryable},
          command=command, request_id=request_id, code=code, error=True)
    return code


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
            _emit(result,command='describe',request_id='QR-'+exact_content_hash(argv))
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
        identifier = 'QR-' + exact_content_hash(json_safe(normalized))
        try:
            result, code = execute(args)
        finally:
            identifier = getattr(args, '_resolved_request_id', identifier)
    except ValueError as error:  # includes CliInputError
        return _fail('input_error', error, 'user', False, command, identifier)
    except (TypeError, KeyError) as error:
        return _fail('contract_error', error, 'maintenance', False, command, identifier)
    except (GitStateStoreConflict, GitStateStoreError, OSError, subprocess.SubprocessError) as error:
        return _fail('tool_error', error, 'operator', isinstance(error, (GitStateStoreConflict, GitStateStoreLockError)),
                     command, identifier)
    except RuntimeError as error:  # after the store errors, which are RuntimeErrors
        return _fail('contract_error', error, 'maintenance', False, command, identifier)
    if isinstance(result,dict):
        identifier = result.get('request_id',identifier)
    _emit(result,command=command,request_id=identifier,code=code,force_json=force_json)
    return code
