"""T5 and corpus share a narrow native list_sources observer.

The product Codex parser checks the stream lifecycle; it does not judge MCP
payloads. This test-only observer links one start/completion and compares every
summary with the installed registry (live) or its dated source snapshot (replay).
It is not a general MCP parser or a scholarly search/access certification.
"""
import hashlib
import json
from pathlib import Path
import subprocess

from do_math.codex_stream import parse_jsonl
from do_math.values import strict_json_loads


def list_sources_observation(raw, expected_sources):
    parsed = parse_jsonl(raw)
    if not parsed['parse_complete'] or not parsed['turn_completed'] or parsed['turn_failed']:
        raise ValueError('scholarly stream did not complete successfully')
    events = [strict_json_loads(line) for line in raw.splitlines() if line.strip()]
    calls = [(index, event) for index, event in enumerate(events)
             if isinstance(event.get('item'), dict) and event['item'].get('type') == 'mcp_tool_call']
    if any((event['item'].get('server'), event['item'].get('tool')) != ('scholarly', 'list_sources')
           for _, event in calls):
        raise ValueError('scholarly probe called an unassigned MCP tool')
    starts = [(index, event['item']) for index, event in calls if event['type'] == 'item.started']
    ends = [(index, event['item']) for index, event in calls if event['type'] == 'item.completed']
    if len(starts) != 1 or len(ends) != 1:
        raise ValueError('scholarly requires exactly one start and one completion')
    start_index, start = starts[0]
    end_index, end = ends[0]
    if not isinstance(start.get('id'), str) or not start['id'] or start['id'] != end.get('id') or start_index >= end_index:
        raise ValueError('scholarly completion is not bound to its start')
    if end.get('status') != 'completed' or end.get('error') is not None:
        raise ValueError('scholarly native completion failed')
    result = end.get('result')
    if not isinstance(result, dict) or result.get('isError', False) is not False:
        raise ValueError('scholarly MCP result is absent or an error')
    content = result.get('content')
    if (not isinstance(content, list) or len(content) != 1 or not isinstance(content[0], dict)
            or content[0].get('type') != 'text' or not isinstance(content[0].get('text'), str)):
        raise ValueError('scholarly response must preserve its complete text content')
    payload = strict_json_loads(content[0]['text'])
    # Codex JSONL exposes MCP structuredContent as structured_content.
    # Use this observed native spelling; do not silently discard that body.
    structured = result.get('structured_content')
    if structured is not None and structured != payload:
        raise ValueError('scholarly content and structuredContent disagree')
    if not isinstance(payload, dict) or payload.get('status') != 'ok' or not isinstance(payload.get('sources'), list):
        raise ValueError('scholarly response is not an ok source list')
    sources = payload['sources']
    ids = [source.get('id') for source in sources if isinstance(source, dict)]
    if (len(ids) != len(sources) or any(not isinstance(key, str) or not key for key in ids)
            or len(set(ids)) != len(ids)):
        raise ValueError('scholarly source IDs are missing or duplicated')
    expected = {source['id']: source for source in expected_sources}
    if len(expected) != len(expected_sources) or not expected:
        raise ValueError('scholarly registry snapshot is empty or duplicated')
    if {source['id']: source for source in sources} != expected:
        raise ValueError('scholarly source summaries differ from the server registry')
    return {'tool_id': start['id'], 'server': start['server'], 'tool': start['tool'],
            'start_event': start_index, 'completion_event': end_index,
            'status': payload['status'], 'sources': sources,
            'content': content, 'structuredContent': structured,
            'structured_content_present': structured is not None}


def installed_registry(server, destination, *, environment):
    """Read actual Source.summary with its Python; do not import/start server.py.

    registry has no authentication or browser initialization. The isolated
    subprocess imports it directly and records only public summaries/versions.
    """
    if not server or not server['args'] or not Path(server['args'][0]).is_file():
        raise ValueError('scholarly smoke requires an installed Python server file')
    directory = Path(server['args'][0]).parent
    code = ('import hashlib, importlib.metadata as m, json, pathlib, platform, sys; '
            'sys.path.insert(0, sys.argv[1]); from registry import SOURCES; '
            'print(json.dumps({"sources":[s.summary() for s in SOURCES.values()], '
            '"python":platform.python_version(), "executable":sys.executable, '
            '"packages":{n:m.version(n) for n in ("mcp","pydantic","openpyxl")}, '
            '"source_sha256":{n:hashlib.sha256((pathlib.Path(sys.argv[1])/n).read_bytes()).hexdigest() '
            'for n in ("server.py","registry.py","scholarly.py")}}, ensure_ascii=False))')
    command = [server['command'], '-B', '-c', code, str(directory)]
    result = subprocess.run(command, capture_output=True, env=environment, cwd=directory,
                            creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    (destination / 'registry.stdout.json').write_bytes(result.stdout)
    (destination / 'registry.stderr.txt').write_bytes(result.stderr)
    (destination / 'registry.command.json').write_text(json.dumps(
        {'command': command, 'cwd': str(directory), 'exit_code': result.returncode}, indent=2), encoding='utf-8')
    if result.returncode != 0:
        raise ValueError('installed scholarly registry observation failed')
    return strict_json_loads(result.stdout)


def run_scholarly_smoke(*, environment):
    """One existing protocol_probe files call through real worker/Job/collector.

    There are no retries, time limits, service/configuration changes or direct
    MCP calls. Scratch remains evidence; the ModelRunner closes its own Job.
    """
    import tempfile
    from do_math.codex_worker import build_argv
    from do_math.file_io import executable_identity
    from do_math.observations import read_checkpoint
    from do_math.payloads import json_safe
    from do_math.provider_final import final_bytes, semantic_output
    from do_math.scholarly_config import _from_config, resolve_scholarly_server
    from do_math.wiring import real_ports
    from support.provider_live import smoke_inputs
    from probe_cli import run_case
    root = Path(tempfile.mkdtemp(prefix='scholarly-smoke-'))
    ports = real_ports(environment=environment)
    report = {'started_at': ports.clock.now(), 'evidence_directory': str(root), 'runner_calls': 0, 'checks': {}}
    print('Scholarly smoke evidence: ' + str(root), flush=True)
    try:
        inputs = smoke_inputs('codex', environment)
        # run_case uses the existing PATH-resolved ModelRunner, unchanged.
        import shutil
        if executable_identity(shutil.which('codex') or 'codex') != executable_identity(inputs['cli']):
            raise ValueError('explicit scholarly smoke CLI differs from the existing probe PATH selection')
        report['inputs'] = inputs
        executable = executable_identity(inputs['cli'])
        report['cli_identity'] = {'path': str(executable), 'sha256': hashlib.sha256(executable.read_bytes()).hexdigest()}
        version = subprocess.run([inputs['cli'], '--version'], capture_output=True, env=environment,
                                 creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        (root / 'version.stdout.txt').write_bytes(version.stdout)
        (root / 'version.stderr.txt').write_bytes(version.stderr)
        report['version'] = {'command': version.args, 'exit_code': version.returncode,
                             'text': version.stdout.decode('utf-8').strip()}
        if version.returncode:
            raise ValueError('scholarly smoke CLI version failed')
        home = Path(environment.get('CODEX_HOME', str(Path.home() / '.codex')))
        server = resolve_scholarly_server(None, start=Path.cwd(), codex_home=home)
        report['server'] = server
        candidates = [directory / '.codex/config.toml' for directory in (Path.cwd(), *Path.cwd().parents)]
        candidates.append(home / 'config.toml')
        report['configuration_source'] = next((str(path) for path in candidates
            if path.is_file() and _from_config(path) is not None), None)
        registry = installed_registry(server, root, environment=environment)
        report['registry'] = registry
        server_python = executable_identity(server['command'])
        report['server_python'] = {'path': str(server_python), 'sha256': hashlib.sha256(server_python.read_bytes()).hexdigest()}
        report['runner_calls'] = 1
        probe = run_case(root, 'files', ports=ports, provider='codex', model=inputs['model'], effort=inputs['effort'],
                         only_assigned=False, scholarly=True, codex_home=home, environment=environment, host_id=inputs['host'])
        report['probe'] = probe
        saved = strict_json_loads(Path(probe['report']).read_bytes())
        result = saved['result']
        collected = result.get('execution', {}).get('collect', {})
        call = root / 'files/evidence'
        workspace = root / 'files/workspace'
        # source_request is the actual private worker snapshot, not the unsnapshotted input request.
        worker_argv = collected['worker_argv']
        request_path = Path(worker_argv[-1])
        request_raw = request_path.read_bytes()
        request = strict_json_loads(request_raw)
        argv = build_argv(request)
        report['worker_snapshot'] = {'path': str(request_path), 'request': request, 'argv': argv,
                                     'sha256': hashlib.sha256(request_raw).hexdigest()}
        raw = (call / 'stdout.jsonl').read_bytes()
        observation = list_sources_observation(raw, registry['sources'])
        report['native_list_sources'] = observation
        parsed = parse_jsonl(raw)
        final = final_bytes(parsed)
        schema = strict_json_loads((call / 'output.schema.json').read_bytes())
        nonce = schema['properties']['nonce']['const']
        checkpoint = read_checkpoint(workspace, clock=ports.clock)
        expected_checkpoint = {'current_claim': 'The local probe file exists.', 'evidence_paths': ['probe-evidence.txt'],
                               'attempts': ['Write and read the probe file.'], 'remaining_work': [],
                               'next_step': 'Return the structured probe result.', 'progress_state': 'ready_to_submit'}
        data_dir = str(workspace.resolve() / 'scholarly-data')
        args_setting = 'mcp_servers.scholarly.args=' + json.dumps([*server['args'], '--data-dir', data_dir], ensure_ascii=False)
        status = collected['worker_status']
        report['data_directory'] = {'path': data_dir, 'exists_after_list_sources': Path(data_dir).exists(),
                                    'scope': 'ArtifactStore creates directories only when storing artifacts; list_sources does not store any.'}
        report['checks'] = {**saved['checks'],
            'exact_nonce_file': (workspace / 'probe-evidence.txt').read_bytes() == nonce.encode('utf-8'),
            'exact_checkpoint': checkpoint.get('status') == 'valid' and checkpoint.get('value') == expected_checkpoint,
            'native_success_response': observation['status'] == 'ok',
            'worker_server': request.get('scholarly_server') == server,
            'worker_cwd': Path(request['cwd']).resolve() == workspace.resolve(),
            'isolated_server_argv': args_setting in argv and Path(data_dir).parent == workspace.resolve(),
            'worker_request_hash': status['request_sha256'] == hashlib.sha256(request_raw).hexdigest(),
            'worker_argv_hash': status['argv_sha256'] == hashlib.sha256('\0'.join(argv).encode('utf-8')).hexdigest(),
            'worker_exit': status['state'] == 'exited' and status['cli_exit_code'] == 0,
            'native_final': final == (call / 'final.txt').read_bytes() and semantic_output('codex', final) == result['output'],
            'empty_job': collected['termination_barrier']['active_processes'] == 0
                         and collected['termination_barrier']['process_ids'] == [],
        }
        report['nonce'] = nonce
        report['checkpoint'] = checkpoint
        report['scope'] = 'list_sources only; local Job termination; no search/fetch or remote cancellation guarantee'
        report['initialization'] = 'Actual native completion demonstrates an initialized tool session; CLI does not emit the MCP handshake/version negotiation.'
    except Exception as error:
        report['error'] = type(error).__name__ + ': ' + str(error)
        raise
    finally:
        report['ended_at'] = ports.clock.now()
        report['passed'] = bool(report['checks']) and all(report['checks'].values()) and 'error' not in report
        (root / 'smoke.json').write_text(json.dumps(json_safe(report), ensure_ascii=False, indent=2), encoding='utf-8')
    return report
