"""The do-math CLI's wire contract (layer 2).

The argument parser, the JSON request schemas derived from it, the published
``--describe`` contract, the validation of a JSON request, and what a
``configure`` means for the installed operator tasks. The command-line entry
point that runs commands under this contract is ``cli`` (layer 3).
"""
from __future__ import annotations

import argparse
from pathlib import Path
from .control_contracts import OPERATOR_ACTIONS, REQUEST_ID_PATTERN, REQUESTABLE_ROLES
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
    run.add_argument('--installation-manifest', type=Path,
                     help='verified frozen bootstrap manifest to compare with the live installation before dispatch')

    status = commands.add_parser("status", help="show current status")
    _instance_arguments(status)
    status.add_argument("--json", action="store_true")
    status.add_argument('--snapshot')

    for name in ("pause", "resume", "close", "quiesce", "release-quiesce"):
        command = commands.add_parser(name, help=f"queue and apply {name}")
        _instance_arguments(command)
        command.add_argument("--reason", default="")
        command.add_argument("--request-id", help="stable retry identity; changed payloads are rejected")
        if name == 'release-quiesce':
            command.add_argument('--fence', required=True)

    input_command = commands.add_parser("input", help="submit user input")
    _instance_arguments(input_command)
    incoming = input_command.add_mutually_exclusive_group(required=True)
    incoming.add_argument("--text")
    incoming.add_argument("--file")
    input_command.add_argument("--request-id", help="stable retry identity; changed payloads are rejected")
    input_command.add_argument("--responds-to", action="append", default=[], help="ID of an open user question answered by this input; repeat for multiple questions")

    configure = commands.add_parser("configure", help="change explicit instance configuration")
    _instance_arguments(configure)
    configure.add_argument("--config-file", required=True)

    request = commands.add_parser("request", help="queue a model-free activity request")
    _instance_arguments(request)
    request_mode = request.add_mutually_exclusive_group(required=True)
    request_mode.add_argument("--role", choices=REQUESTABLE_ROLES)
    request_mode.add_argument("--retry-action", help="retry one held input overflow or failed initial interpretation; reuse a verified preserved native final when available")
    request_mode.add_argument("--assessment-reassessment-file", help="report exact original assessment and defect evidence for bounded independent reassessment")
    request.add_argument("--target")
    request.add_argument("--reason")

    for name in ("decision", "knowledge", "trust", "external", "conversation"):
        command = commands.add_parser(name, help=f"apply a structured {name} control")
        _instance_arguments(command)
        command.add_argument("--file", required=True)

    source = commands.add_parser("source", help="import an exact local source file")
    _instance_arguments(source)
    source.add_argument("--file", required=True)
    source.add_argument("--name")

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
        # Control admission refuses the operator origin outside OPERATOR_ACTIONS; only those commands offer it.
        origins = ('user', 'operator') if name.replace('-', '_') in OPERATOR_ACTIONS else ('user',)
        commands.choices[name].add_argument('--origin', choices=origins, default='user')
    return parser


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


# The settings the scheduled tasks are installed with. operator_effort reaches the recovery AI
# through the recovery profile that a configure rebuilds, so it needs no schedule change.
OPERATOR_SCHEDULE_KEYS = frozenset({"operator_enabled", "operator_interval_seconds", "operator_timeout_seconds"})


def operator_schedule_after_configure(requested: dict, result: dict):
    """What a ``configure`` means for the installed operator tasks.

    None when it changed no schedule setting; ``'reconcile'`` when its applied
    control must reconcile the tasks now; otherwise the schedule status to report.
    """
    if not OPERATOR_SCHEDULE_KEYS.intersection(requested):
        return None
    if result['effect'] == 'rejected':
        return {'status': 'not_applied', 'reason': 'configuration was rejected'}
    if result.get('replayed') and result['effect'] == 'applied':
        return {'status': 'not_reapplied',
                'reason': 'original control receipt replayed; explicit operator install or uninstall reconciles current configuration'}
    if result['effect'] == 'applied':
        return 'reconcile'
    return {"status": "pending", "reason": "run operator install or uninstall after the control is applied"}
