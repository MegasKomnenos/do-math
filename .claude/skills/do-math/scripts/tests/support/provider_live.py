"""A running execution on a Sim's real engine, and the runner's observation batches for it.

``running_execution(sim, execution_id, role)`` opens an activity and registers
one execution of ``role`` through the product's own lifecycle functions
(``activities``, ``execution_lifecycle``), moves it to ``running`` and
publishes it with the engine's ``_save`` under the storage contract. It
returns the execution's workspace (``<instance workspace>/runs/<id>/workspace``).
Legacy tests put a bare ``{'status': 'running'}`` record into a memory engine
whose ``_save`` was a double; this record passes the real store. ``bind`` also
issues the execution's control transport binding, as input preparation does.

``batch(sim, events, stream_path, ...)`` is the ``ObservationBatch`` a
``ModelRunner`` hands the owner: consecutive JSON rows from ``start``, received
at the Sim clock's time (so no real time reaches the published state).
"""
import json
from pathlib import Path

from do_math import activities, execution_lifecycle
from do_math.execution_profiles import profile_ref
from do_math.observation_transport import ObservationBatch


def running_execution(sim, execution_id, role, *, action=None, bind=False):
    engine = sim.engine
    runtime = engine.runtime
    at = sim.clock.now()
    profile = next(p for p in engine.instance['execution_profiles'].values() if p['role'] == role)
    activity = 'AY-' + execution_id
    activities.open_activity(runtime, activity_id=activity, activity_kind=role, owner_ref='engine', input_refs=[],
                             opened_at=at)
    execution = execution_lifecycle.create_execution(execution_id=execution_id, owner_activity_id=activity,
                                                     actor_kind='ai', input_manifest={},
                                                     profile_ref=profile_ref(profile), created_at=at)
    execution.update(role=role, action={'id': 'AC-' + execution_id, 'role': role, 'owner_activity_id': activity,
                                        **(action or {})})
    activities.assign_execution(runtime, activity, execution)
    for status in ('starting', 'running'):
        execution_lifecycle.transition_execution(runtime['executions'][execution_id], status, at=at)
    engine._save()
    workspace = Path(engine.instance['workspace']) / 'runs' / execution_id / 'workspace'
    workspace.mkdir(parents=True, exist_ok=True)
    if bind:
        engine._transport_bindings[execution_id] = engine._transport.issue(
            execution_id, 'GR-research-sim', workspace=workspace, self_check=True)
    return workspace


def batch(sim, events, stream_path, *, start=0, rows=None, first_row=0, terminated=False, received_monotonic=None):
    """The runner's batch of ``events``; ``rows`` gives their exact bytes (default: one JSON row each).

    ``received_monotonic`` is when the runner read the rows (default: the Sim clock now).
    """
    rows = rows if rows is not None else [json.dumps(event).encode('utf-8') + b'\n' for event in events]
    offsets, position = [], start
    for row in rows:
        offsets.append((position, position + len(row)))
        position += len(row)
    received = sim.clock.monotonic() if received_monotonic is None else received_monotonic
    return ObservationBatch(list(events), offsets, list(rows), first_row, sim.clock.now(), received,
                            position, Path(stream_path), lambda: terminated)


def smoke_inputs(provider, environment):
    """Explicit, non-secret T5 inputs. Missing configuration is a failure, never a skip."""
    from do_math.claude_adapter import ADAPTERS
    from do_math.provider_wait import provider_for
    if provider not in ADAPTERS:
        raise ValueError('unknown smoke provider: ' + provider)
    names = {key: 'DO_MATH_SMOKE_' + provider.upper() + '_' + key.upper()
             for key in ('cli', 'model', 'effort')}
    names['host'] = 'DO_MATH_SMOKE_HOST'
    missing = [name for name in names.values() if not environment.get(name, '').strip()]
    if missing:
        raise ValueError('provider smoke requires explicit inputs: ' + ', '.join(missing))
    inputs = {key: environment[name] for key, name in names.items()}
    if not Path(inputs['cli']).is_absolute() or not Path(inputs['cli']).is_file():
        raise ValueError('provider smoke CLI must be an existing absolute file')
    if provider == 'codex' and provider_for(inputs['model']) != 'codex':
        raise ValueError('Codex smoke model belongs to another provider')
    if inputs['model'].startswith('claude:'):
        raise ValueError('smoke model must be the bare CLI model name')
    return inputs


def smoke_request(workspace, nonce):
    """Use the complete current maintenance schema and a file read with an observable result."""
    from do_math.contracts import action_schema
    from do_math.observations import checkpoint_value
    from jsonschema import Draft202012Validator
    schema = action_schema({'role': 'maintenance'})
    checkpoint = {'current_claim': 'The smoke file was written and read back.',
                  'evidence_paths': ['probe-evidence.txt'], 'attempts': ['Write and read the nonce file.'],
                  'remaining_work': [], 'next_step': 'Return the maintenance response.',
                  'progress_state': 'ready_to_submit'}
    checkpoint_value(json.dumps(checkpoint).encode('utf-8'))
    expected = {'summary': 'Provider smoke complete.', 'used_sources': ['probe-evidence.txt', 'checkpoint.json'],
                'questions': [], 'report': nonce, 'remaining_work': []}
    Draft202012Validator(schema).validate(expected)
    prompt = (f'This is an isolated maintenance integration smoke. Work only in {workspace}. '
              f'Write probe-evidence.txt as UTF-8 containing exactly {nonce}, with no newline. '
              'Then use a separate shell tool call to read that file from disk and print only a JSON object '
              'with key read_nonce and the value read from the file. Do not print a hardcoded nonce. '
              'Write checkpoint.json with this exact JSON content: ' + json.dumps(checkpoint) + '. '
              'Read checkpoint.json back and verify its JSON value silently, without printing its content. '
              'The dedicated nonce read tool result must contain only the one read_nonce JSON object; '
              'do not append checkpoint contents or diagnostic text to that output. '
              'Finally return this maintenance response exactly: '
              + json.dumps(expected) + '. Keep the complete supplied response schema. '
              'Do not start agents, another model, background tasks, research, or network tools.')
    return prompt, schema, expected, checkpoint


def smoke_read_events(provider, events, nonce):
    """Locate successful native tool results containing the requested structured disk read."""
    matches, uses = [], set()
    for index, event in enumerate(events):
        candidates = []
        item = event.get('item', {})
        if (provider == 'codex' and event.get('type') == 'item.completed'
                and item.get('type') == 'command_execution' and item.get('exit_code') == 0
                and item.get('status') == 'completed'):
            candidates.append((item.get('id'), item.get('aggregated_output')))
        if provider == 'claude':
            message = event.get('message', {})
            content = message.get('content', []) if isinstance(message, dict) else []
            for block in content if isinstance(content, list) else []:
                if not isinstance(block, dict):
                    continue
                if block.get('type') == 'tool_use' and block.get('name') == 'Bash':
                    uses.add(block.get('id'))
                if (block.get('type') == 'tool_result' and block.get('tool_use_id') in uses
                        and block.get('is_error') is not True):
                    candidates.append((block['tool_use_id'], block.get('content')))
        for identifier, output in candidates:
            if not isinstance(output, str):
                continue
            try:
                value = json.loads(output)
            except (ValueError, TypeError):
                continue
            if value == {'read_nonce': nonce}:
                matches.append({'event_index': index, 'tool_id': identifier, 'value': value})
    return matches


def run_provider_smoke(provider, *, environment):
    """One paid real call, owned by ModelRunner/WindowsJobs, with persistent runner scratch evidence.

    No retries, test doubles, schema weakening, skips, or time limits.
    The official resource worker supplies the temporary directory and owns its lifetime.
    """
    import hashlib
    import subprocess
    import tempfile
    from do_math.model_runner import ModelRunner
    from do_math.observations import read_checkpoint
    from do_math.payloads import json_safe
    from do_math.provider_final import final_bytes, output_contract, semantic_output
    from do_math.wiring import real_ports
    root = Path(tempfile.mkdtemp(prefix='provider-smoke-' + provider + '-'))
    ports = real_ports(environment=environment)
    report = {'provider': provider, 'started_at': ports.clock.now(), 'runner_calls': 0,
              'evidence_directory': str(root), 'checks': {}}
    print('Provider smoke evidence: ' + str(root), flush=True)
    try:
        inputs = smoke_inputs(provider, environment)
        report['inputs'] = inputs
        version = subprocess.run([inputs['cli'], '--version'], capture_output=True, env=environment)
        (root / 'version.stdout.txt').write_bytes(version.stdout)
        (root / 'version.stderr.txt').write_bytes(version.stderr)
        report['version'] = {'command': version.args, 'exit_code': version.returncode,
                             'text': version.stdout.decode('utf-8').strip()}
        if version.returncode != 0:
            raise ValueError('provider smoke version observation failed')
        workspace = root / 'workspace'
        workspace.mkdir()
        nonce = ports.clock.random_hex(16)
        prompt, schema, expected, checkpoint = smoke_request(workspace, nonce)
        report.update(nonce=nonce, expected_output=expected, expected_checkpoint=checkpoint)
        events = []

        def started(value):
            (root / 'started.json').write_text(json.dumps(json_safe(value), indent=2), encoding='utf-8')

        runner = ModelRunner(**{provider + '_path': inputs['cli']}, jobs=ports.jobs, clock=ports.clock,
                             environment=environment, host_id=inputs['host'])
        report['runner_calls'] = 1
        result = runner.run(prompt=prompt, output_schema=schema, workspace=workspace, evidence_dir=root / 'call',
                            model=('claude:' if provider == 'claude' else '') + inputs['model'],
                            effort=inputs['effort'], timeout_seconds=None, claude_only_assigned_model=False,
                            on_started=started, on_observation=lambda batch: events.extend(batch.events))
        report['result'] = json_safe(result)
        report['prompt_sha256'] = hashlib.sha256((root / 'call/input.txt').read_bytes()).hexdigest()
        report['schema_sha256'] = hashlib.sha256((root / 'call/output.schema.json').read_bytes()).hexdigest()
        request = json.loads((root / 'call/request.json').read_bytes())
        transport = Path(request['output_schema_path']).read_bytes()
        report['transport_schema_sha256'] = hashlib.sha256(transport).hexdigest()
        collected = result.get('execution', {}).get('collect', {})
        parsed = collected.get('jsonl', {})
        selected = final_bytes(parsed)
        if selected is not None:
            (root / 'selected-final.txt').write_bytes(selected)
        observed_checkpoint = read_checkpoint(workspace, clock=ports.clock)
        report['checkpoint'] = json_safe(observed_checkpoint)
        report['native_read_events'] = smoke_read_events(provider, events, nonce)
        report['observed_event_count'] = len(events)
        file = workspace / 'probe-evidence.txt'
        report['checks'] = {
            'completed': result.get('status') == 'completed',
            'structured_output': result.get('output') == expected,
            'schema_unchanged': json.loads((root / 'call/output.schema.json').read_bytes()) == schema,
            'transport_schema': json.loads(transport) == output_contract(provider, schema),
            'worker_schema_hash': collected.get('worker_status', {}).get('schema_sha256')
                                  == report['transport_schema_sha256'],
            'nonce_file': file.is_file() and file.read_bytes() == nonce.encode('utf-8'),
            'checkpoint': observed_checkpoint.get('status') == 'valid'
                          and observed_checkpoint.get('value') == checkpoint,
            'native_read': bool(report['native_read_events']),
            'native_completion': parsed.get('turn_completed') is True and parsed.get('turn_failed') is False
                                 and parsed.get('parse_complete') is True,
            'selected_final': selected is not None and not runner.adapters[provider].validate_final(parsed, selected)
                              and selected == collected.get('final', {}).get('raw')
                              and semantic_output(provider, selected) == expected,
            'local_termination': collected.get('termination_barrier', {}).get('confirmed') is True,
        }
    except Exception as error:
        report['error'] = type(error).__name__ + ': ' + str(error)
        raise
    finally:
        report['ended_at'] = ports.clock.now()
        report['passed'] = bool(report['checks']) and all(report['checks'].values()) and 'error' not in report
        (root / 'smoke.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    return report
