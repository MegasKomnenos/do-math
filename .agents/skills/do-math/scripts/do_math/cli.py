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
from .engine import ResearchEngine, control, initialize, query_records, read_record
from .git_store import GitStateStoreConflict, GitStateStoreError, GitStateStoreLockError
from .payloads import json_safe
from . import scheduled_operator
from .file_io import console_python
from .values import strict_json_loads
from .repository import ResearchRepository
from .canonical import canonical_json, exact_content_hash
from .state_checks import inspection_exit_code
from .cli_contract import (CliInputError, ERROR_EXIT_CODES, RESPONSE_FIELDS, WIRE_VERSION, _command_parsers, _json_arguments, build_parser, describe_commands,
                           operator_schedule_after_configure)

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


def _control(args: argparse.Namespace, action: str, *, ports, text: str = "", config: dict[str, Any] | None = None, codex_home, environment, host_id) -> dict[str, Any]:
    # ENGINE normalizes a source and derives the request ID; the CLI reports the ID it returns.
    request = control(args.repository, args.instance, action, text=text, config=config or {},
                      origin=getattr(args, "origin", "user"), request_id=getattr(args, 'request_id', None),
                      idempotency_key=getattr(args, 'idempotency_key', None), ports=ports, host_id=host_id)
    args._resolved_request_id = request['request_id']
    # ENGINE's replay receipt is tied to the original publication. Do not run
    # unrelated pending controls or replace that receipt with current state.
    if request.get('effect') in {'applied', 'rejected'} and request.get('snapshot'):
        return request
    engine = ResearchEngine(args.repository, args.instance, ports=ports, codex_home=codex_home, environment=environment, host_id=host_id)
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


def _operator_workspace(repository: Path, instance: str, supplied: Path | None = None, *, ports) -> Path:
    actual = scheduled_operator.resolve_workspace(repository, instance, ports=ports)
    if supplied is not None:
        if supplied.resolve() != actual:
            raise CliInputError("--workspace must equal the instance workspace")
    return actual


def _reconcile_operator(repository: Path, instance: str, configuration: dict[str, Any], *, ports) -> dict[str, Any]:
    workspace = scheduled_operator.resolve_workspace(repository, instance, ports=ports)
    action = "install" if configuration["operator_enabled"] else "uninstall"
    return scheduled_operator.schedule(action, repository=repository, instance=instance, workspace=workspace,
                                       interval_seconds=configuration["operator_interval_seconds"],
                                       operator_timeout_seconds=configuration["operator_timeout_seconds"], scheduler=ports.scheduler)


def _schedule_failure(result: dict[str, Any], error: Exception, repository: Path,
                      instance: str) -> tuple[dict[str, Any], int]:
    mode = "install" if result.get("config", {}).get("operator_enabled", True) else "uninstall"
    def quote(value):
        return "'" + str(value).replace("'", "''") + "'"
    entrypoint = Path(__file__).resolve().parents[1] / "do_math.py"
    reconcile = ("& " + quote(console_python()) + " " + quote(entrypoint)
                 + " operator " + mode + " --repository " + quote(repository.resolve())
                 + " --instance " + quote(instance))
    result["operator_schedule"] = {"status": "failed", "error": str(error), "reconcile": reconcile}
    return result, ERROR_EXIT_CODES['tool_error']


def execute(args: argparse.Namespace, *, ports, codex_home, environment, host_id) -> tuple[dict[str, Any] | str, int]:
    command = args.command
    if command == "timeline":
        from .reporting import timeline, timeline_csv
        value = timeline(args.repository, args.instance, snapshot=args.snapshot, timezone_name=args.timezone,
                         include_operations=args.include_operations, backend=ports.git_backend, clock=ports.clock)
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
                            sources=args.source, ports=ports,
                            source_input=args.request_text if args.request_text is not None else
                                _text_file(args.request_text_file) if args.request_text_file else goal, codex_home=codex_home, host_id=host_id)
        _, initialized, _ = ResearchRepository(args.repository, result["instance_id"], backend=ports.git_backend, clock=ports.clock).load()
        if initialized["config"]["operator_enabled"]:
            try:
                result["operator_schedule"] = _reconcile_operator(args.repository, result["instance_id"], initialized["config"], ports=ports)
            except (RuntimeError, OSError, subprocess.SubprocessError) as error:
                return _schedule_failure(result, error, args.repository, result["instance_id"])
        return result, 0
    if command == "run":
        return ResearchEngine(args.repository, args.instance, ports=ports, codex_home=codex_home, environment=environment, host_id=host_id).run(max_steps=args.max_steps, watch=args.watch,
                                                                 until_active=args.until_active), 0
    if command == 'select-profile':
        from .model_policy import selection
        from .execution_profiles import match_profile_ref
        head, instance, runtime = ResearchRepository(args.repository, args.instance, backend=ports.git_backend, clock=ports.clock).load(args.snapshot)
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
        engine = ResearchEngine(args.repository, args.instance, ports=ports, codex_home=codex_home, environment=environment, host_id=host_id)
        engine.head, engine.instance, engine.runtime = engine.store.load(args.snapshot)
        value = import_approval_draft(engine.instance, engine.runtime, args.import_id,
                                     owner_handlers=engine.governance_owner_handlers(), clock=ports.clock)
        with args.output.open('xb') as stream:
            stream.write(canonical_json(value))
        return {'snapshot':engine.head, 'output':str(args.output.resolve()),
                'decision':value, 'effect':'draft_only'}, 0
    if command == "status":
        from .reporting import snapshot_report, render_human_report
        # The current head with this host's observations, or one stored snapshot without them.
        status = (ResearchEngine(args.repository, args.instance, ports=ports, codex_home=codex_home, environment=environment, host_id=host_id).status() if args.snapshot is None
                  else snapshot_report(args.repository, args.instance, snapshot=args.snapshot, backend=ports.git_backend, clock=ports.clock))
        return (status if args.json else render_human_report(status)), 0
    if command == 'quiesce':
        return _control(args, 'quiesce', ports=ports, text=args.reason, codex_home=codex_home, environment=environment, host_id=host_id), 0
    if command == 'release-quiesce':
        return _control(args, 'release_quiesce', ports=ports, text=args.reason, config={'fence_id':args.fence}, codex_home=codex_home, environment=environment, host_id=host_id), 0
    if command in {"pause", "resume", "close"}:
        return _control(args, command, ports=ports, text=args.reason, codex_home=codex_home, environment=environment, host_id=host_id), 0
    if command == "input":
        return _control(args, "input", ports=ports, text=args.text if args.text is not None else _text_file(args.file), config={"responds_to": args.responds_to}, codex_home=codex_home, environment=environment, host_id=host_id), 0
    if command == "configure":
        requested = _json_file(args.config_file)
        result = _control(args, "configure", ports=ports, config=requested, codex_home=codex_home, environment=environment, host_id=host_id)
        schedule = operator_schedule_after_configure(requested, result)
        if schedule == 'reconcile':
            try:
                result["operator_schedule"] = _reconcile_operator(args.repository, args.instance, result["config"], ports=ports)
            except (RuntimeError, OSError, subprocess.SubprocessError) as error:
                return _schedule_failure(result, error, args.repository, args.instance)
        elif schedule is not None:
            result["operator_schedule"] = schedule
        return result, 0
    if command == "request":
        if args.assessment_reassessment_file is not None:
            if args.target is not None or args.reason is not None:
                raise CliInputError("--assessment-reassessment-file cannot be combined with target or request text")
            payload, original = _json_document(args.assessment_reassessment_file)
            return _control(args, "request", ports=ports, text=original,
                            config={"role": "identity_review", "assessment_reassessment": payload}, codex_home=codex_home, environment=environment, host_id=host_id), 0
        if args.retry_action is not None:
            if args.target is not None or args.reason is not None:
                raise CliInputError("--retry-action cannot be combined with target or request text")
            return _control(args, "request", ports=ports, config={"retry_action": args.retry_action}, codex_home=codex_home, environment=environment, host_id=host_id), 0
        return _control(args, "request", ports=ports, text=args.reason or "",
                        config={"role": args.role, "target": args.target}, codex_home=codex_home, environment=environment, host_id=host_id), 0
    if command in {"decision", "knowledge", "trust", "external", "conversation"}:
        payload, original = _json_document(args.file)
        return _control(args, command, ports=ports, text=original,
                        config={"change": payload} if command == "decision" else payload, codex_home=codex_home, environment=environment, host_id=host_id), 0
    if command == "source":
        path = Path(args.file).resolve()
        if not path.is_file():
            raise CliInputError(f"--file is not a file: {args.file}")
        return _control(args, "source", ports=ports, config={"path": str(path), "name": args.name or path.name}, codex_home=codex_home, environment=environment, host_id=host_id), 0
    if command == "query":
        if args.files:
            if args.kind is not None or args.related_to is not None or args.direction is not None:
                raise CliInputError("--files cannot be combined with --kind, --related-to or --direction")
            prefix = args.prefix if args.prefix is not None else "research/"
            value = ResearchRepository(args.repository, args.instance, backend=ports.git_backend, clock=ports.clock).query(snapshot=args.snapshot, prefix=prefix,
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
                             direction=args.direction if args.direction is not None else "both", backend=ports.git_backend, clock=ports.clock), 0
    if command == "read":
        if args.output is not None and args.path is None:
            raise CliInputError("--output requires --path")
        if args.path is not None:
            store = ResearchRepository(args.repository, args.instance, backend=ports.git_backend, clock=ports.clock)
            resolved_snapshot = store.resolve_snapshot(args.snapshot)
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
        return read_record(args.repository, args.instance, args.id, snapshot=args.snapshot, backend=ports.git_backend, clock=ports.clock), 0
    if command == "export":
        prefixes = ("research/", "runtime/") if args.all else ("research/",)
        return ResearchRepository(args.repository, args.instance, backend=ports.git_backend, clock=ports.clock).export(args.destination, args.snapshot, prefixes), 0
    if command == "check":
        result = ResearchEngine(args.repository, args.instance, ports=ports, codex_home=codex_home, environment=environment, host_id=host_id).check(snapshot=args.snapshot, requested_areas=args.kinds)
        code = inspection_exit_code(result['inspection'])
        result.update(exit_code=code, passed=code == 0)
        return result, code
    if command == "profile":
        paths = {"codex": args.codex_path, "claude": args.claude_path}
        other = next(name for name in paths if name != args.provider)
        if paths[other]:
            raise CliInputError(f"--{other}-path requires --provider {other}")
        result = json_safe(provider_adapter(args.provider, paths[args.provider], clock=ports.clock, jobs=ports.jobs).describe())
        return result, 0 if result.get("verified") else 1
    if command == "operator":
        workspace = _operator_workspace(args.repository, args.instance, args.workspace, ports=ports)
        mode = args.mode
        if mode in {"install", "uninstall", "status", "start", "start-operator"}:
            action = {"start": "start-engine", "start-operator": "start-operator"}.get(mode, mode)
            if action == "start-engine":
                guard = scheduled_operator.engine_start_guard(args.repository, args.instance, workspace, ports=ports, codex_home=codex_home, environment=environment, host_id=host_id)
                if guard["outcome"] != "startable":
                    return guard, 0
            settings = {}
            if action == "install":
                configuration = ResearchRepository(args.repository, args.instance, backend=ports.git_backend, clock=ports.clock).load()[1]["config"]
                settings = {"interval_seconds": configuration["operator_interval_seconds"],
                            "operator_timeout_seconds": configuration["operator_timeout_seconds"]}
            return scheduled_operator.schedule(action, repository=args.repository, instance=args.instance,
                                               workspace=workspace, scheduler=ports.scheduler, **settings), 0
        if mode == "hold":
            marker = scheduled_operator.hold(workspace, reason=args.reason, clock=ports.clock)
            pause = _control(args, "pause", ports=ports, text=scheduled_operator.hold_pause_reason(marker["id"]), codex_home=codex_home, environment=environment, host_id=host_id)
            try:
                cleanup = scheduled_operator.cancel_wake(args.repository, args.instance, workspace, scheduler=ports.scheduler)
            except (RuntimeError, OSError) as error:
                cleanup = {"status": "failed", "error": str(error), "hold_still_blocks_wake": True}
            return {"hold": marker, "pause": pause, "wake_cleanup": cleanup}, 0
        if mode == "release":
            released = scheduled_operator.release(workspace, clock=ports.clock)
            marker = released.get("released")
            expected = scheduled_operator.hold_pause_reason(marker["id"]) if marker else None
            if expected:
                released["resume"] = _control(args, "resume", ports=ports, text="User released scheduled operator HOLD " + marker["id"],
                                              config={"expected_user_pause_reason": expected}, codex_home=codex_home, environment=environment, host_id=host_id)
            else:
                released["resume"] = {"effect": "not_requested", "reason": "no HOLD was released"}
            return released, 0
        if mode == "wake":
            return scheduled_operator.wake(args.repository, args.instance, workspace, ports=ports, codex_home=codex_home, environment=environment, host_id=host_id), 0
        if mode == "engine":
            return scheduled_operator.run_engine(args.repository, args.instance, workspace, ports=ports, environment=environment, codex_home=codex_home, host_id=host_id), 0
        return scheduled_operator.check(args.repository, args.instance, workspace, ports=ports, probe=mode == "probe", codex_home=codex_home, environment=environment, host_id=host_id), 0
    raise CliInputError("unknown command")


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


def main(argv=None, *, ports=None, environment=None, host_id=None, codex_home=None):
    import os
    import platform
    from .wiring import real_ports
    environment = dict(os.environ) if environment is None else environment
    host_id = platform.node() if host_id is None else host_id
    codex_home = (Path(environment["CODEX_HOME"]) if environment.get("CODEX_HOME") else Path.home() / ".codex") if codex_home is None else codex_home
    ports = real_ports(environment=environment) if ports is None else ports
    clock, jobs, backend = ports.clock, ports.jobs, ports.git_backend
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
            result, code = execute(args, ports=ports, codex_home=codex_home, environment=environment, host_id=host_id)
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
