"""The contract-pair kind (설계 3.3; 의무 1-A, 1-C): a producer's real output must pass its receiving check.

Each ``Pair`` names a producer and the check that receives what it makes:

- ``samples(root)`` returns ``(branch, value)`` pairs made by the real producer,
  one or more per branch of its input (configuration choices, providers,
  multiplicity 0, 1 and many, optional fields present and absent). ``root`` is
  an empty directory the producer may write under.
- ``receive(value)`` runs the receiving check and raises ``ValueError`` to reject.
- ``fields`` are the fields the receiving check names, required or optional.
  Every one must be written by some producer branch: a field the receiver
  requires or accepts that no producer makes is how a receiver drifts from its
  producers (조사 B-02; 설계 10절 A20).
- ``written(value)`` gives the fields a value writes (default: its top-level keys).
  ``fields=None`` states that the receiving check names no field (a serializer).

``tests/contracts/test_pairs.py`` walks every pair. To add a pair, add a ``Pair``
to ``PAIRS``; a pair with no samples fails the walk. A branch a pair's receiver
rejects today is a known defect: it stays out of the samples, and a test of its
own in ``test_pairs.py`` carries the ledger mark. Storage has whole-product
checks in ``tests/structure/test_storage_fields.py`` (설계 10절 A22) and direct
stored-producer field walks in ``test_storage_knowledge_pairs.py``. The
structural name walk alone does not establish actual optional-field production.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from pathlib import Path
from typing import Any, Callable


@dataclass(frozen=True)
class Pair:
    name: str
    samples: Callable[[Path], list[tuple[str, Any]]]
    receive: Callable[[Any], Any]
    fields: frozenset | None
    written: Callable[[Any], set] = lambda value: set(value)


def assert_pair(case, pair, samples):
    """Receive actual values, then check every required and optional field in reverse."""
    case.assertGreater(len(samples), 0, 'a pair needs producer samples')
    rejected = []
    for branch, value in samples:
        try:
            from copy import deepcopy
            pair.receive(deepcopy(value))
        except ValueError as error:
            rejected.append((branch, str(error)))
    case.assertEqual(rejected, [], 'producer branches the receiving check rejects')
    if pair.fields is not None:
        written = set().union(*(pair.written(value) for _, value in samples))
        case.assertEqual(sorted(pair.fields - written), [],
                         'fields the receiving check names that no producer branch writes')


def worker_request_run(root, provider, *, identity, limits, control, scholarly, only,
                       evidence_name='evidence', scholarly_args=None):
    """One real runner/store/adapter/worker/collector call, observed at the external Job and CLI fakes.

    All files remain under ``root`` until its caller finishes checking them.
    The fixture inputs are returned separately from the requests read from disk.
    """
    from copy import deepcopy
    import json
    import sys
    from do_math.control_transport import ControlTransport
    from do_math.execution_profiles import build_profiles, prepare_prompt, prompt_seal, with_host_resources
    from support.entry import entry
    from support.fakes.clock import FakeClock
    from support.provider_inputs import PROFILE_CONFIG, host_capacity_fixture
    from support.provider_runs import ProviderJobs, dispatched, model_runner
    workspace, evidence = root / 'workspace', root / evidence_name
    workspace.mkdir(parents=True, exist_ok=True)
    clock, publications = FakeClock(), []
    jobs = ProviderJobs(clock=clock)
    model = 'gpt-6-astra' if provider == 'codex' else 'claude:claude-sonnet-5'
    server_path = root / 'server.py'
    server_path.write_text('# CLI fixture; this server is never started.\n', encoding='utf-8')
    server = {'command': sys.executable,
              'args': [str(server_path)] if scholarly_args is None else list(scholarly_args)} if scholarly else None
    profile, ticket, binding, resource_limits = None, None, None, None
    execution_id = 'EX-pair' if identity else None
    prompt, options = 'Return an empty object. 한글', {}
    if identity:
        config = deepcopy(PROFILE_CONFIG)
        config.update(tier_models={tier: model for tier in ('high', 'medium', 'low')},
                      session_limits={'work': {model: 3}}, scholarly_enabled=scholarly,
                      scholarly_server=server, claude_only_assigned_model=only)
        profiles = build_profiles(config, host=entry().ports.host)
        profile = next(p for p in profiles['execution_profiles'].values() if p['role'] == 'research_work')
        if limits:
            _, selected, constraint = host_capacity_fixture()
            demands = selected['research_work']['host_resources']['demands']
            profile = with_host_resources(profile, constraint, demands)
            resource_limits = {k: demands[k] for k in ('memory_bytes', 'cpu_rate_basis_points')}

            def publish(started):
                publications.append({'started': deepcopy(started), 'resumed': jobs.launched[0].resumed,
                                     'cli_calls': len(jobs.cli.calls)})
            options['on_started'] = publish
        prompt = prepare_prompt(prompt, profile)
        ticket = dispatched(execution_id, profile, jobs, clock)
        options.update(execution_id=execution_id, profile=profile, launch_ticket=ticket,
                       input_seal=prompt_seal(prompt))
    else:
        options.update(scholarly_server=server, claude_only_assigned_model=only)
    if control:
        binding = ControlTransport(root / 'control', clock=clock).issue(execution_id, 'GR-pair', workspace=workspace)
        options['control_binding'] = binding
    schema, effort = {'type': 'object'}, profile['ai']['effort'] if identity else 'medium'
    result = model_runner(root, jobs, clock).run(
        prompt=prompt, output_schema=schema, workspace=workspace, evidence_dir=evidence,
        model=model, effort=effort, timeout_seconds=600, **options)
    # Pair.samples must never silently return an accepted request from a failed run.
    assert result['status'] == 'completed', result
    assert len(jobs.launched) == len(jobs.cli.calls) == 1
    assert all(job.done and job.closed for job in jobs.launched)
    request_path, staged_path = evidence / 'request.json', Path(jobs.launched[0].argv[2])
    return {'request': json.loads(request_path.read_bytes()), 'staged': json.loads(staged_path.read_bytes()),
            'request_path': request_path, 'staged_path': staged_path, 'result': result, 'jobs': jobs,
            'publications': publications, 'profile': profile, 'ticket': ticket, 'binding': binding,
            'resource_limits': resource_limits, 'server': server, 'prompt': prompt, 'schema': schema,
            'model': model, 'effort': effort, 'execution_id': execution_id, 'only': only}


def worker_request_runs(root, provider):
    """The original twenty legal settings, each through the real producer and both worker loads."""
    for identity, limits, control, scholarly, only in product((False, True), repeat=5):
        if (limits or control) and not identity:
            continue
        branch = ','.join(name for name, on in (('schema', not control), ('identity', identity), ('limits', limits),
                          ('control', control), ('scholarly', scholarly), ('claude_only', only)) if on) or 'bare'
        yield branch, worker_request_run(root, provider, identity=identity, limits=limits, control=control,
                                        scholarly=scholarly, only=only, evidence_name=branch)


def _worker_request_samples(provider):
    """Requests read from the files ``ModelRunner.run`` actually stored on every legal assignment branch."""
    def samples(root):
        return [(branch, run['request']) for branch, run in worker_request_runs(root, provider)]
    return samples


def _worker_request_fields(provider):
    from do_math import worker_request as rules
    own = {'codex': rules.CODEX_REQUIRED | rules.CODEX_OPTIONAL, 'claude': rules.CLAUDE_REQUIRED | rules.CLAUDE_OPTIONAL}
    return frozenset(rules.COMMON_REQUIRED | rules.COMMON_OPTIONAL | own[provider])


def _receive_worker_request(provider):
    def receive(value):
        from do_math import worker_request as rules
        return (rules.check_codex_request if provider == 'codex' else rules.check_claude_request)(value)
    return receive


def _trust_request_samples(root):
    """Requests read from files setup publishes after real new/reuse/rerecord operations.

    The worker and writer are real; only the external Job/Lean/Lake ports use
    the existing doubles. See setup_request_runs for the independent inputs.
    """
    from support.trust_inputs import setup_request_runs
    return [(branch, run['request']) for branch, run in setup_request_runs(root)]


def _receive_trust_request(value):
    from do_math.trust_validation import register_request_errors
    errors = register_request_errors(value)
    if errors:
        raise ValueError('; '.join(errors))


def _trust_request_fields():
    from do_math.trust_validation import REGISTER_FIELDS
    return frozenset(REGISTER_FIELDS)


# Rule IDs the observation tracker accepts (``observations.validate_rules``) that the stored review rows
# (``runtime.observations``) keep; ones the tracker accepts and storage rejects are KD-0007.
STORABLE_RULE_IDS = ('R-1', 'progress_check', 'rule.2', 'attempts-3')
TEXT_RULE_ID_SAMPLES = ('progress check', '규칙', 'r:1', ' \t')


def accepted_rule_ids(ids):
    """``(id, {'rule_ids': [id]})`` for each rule ID the tracker accepts in a rule."""
    from do_math.observations import OPERATORS, validate_rules
    rows = []
    for rule_id in ids:
        rule = {'id': rule_id, 'operator': 'counter_gte', 'subject': {'kind': 'counter', 'id': 'attempts'},
                'basis': {'source': OPERATORS['counter_gte']['source'], 'unit': OPERATORS['counter_gte']['unit']},
                'threshold': 2, 'required_evidence': ['EV-1']}
        validate_rules([rule])  # the tracker's own acceptance: a rule it rejects is not its output
        rows.append((rule_id, {'rule_ids': [rule_id]}))
    return rows


def stored_rule_id_errors(value):
    """What the stored review row's ``rule_ids`` check (read from the storage contract) says of ``value``."""
    import jsonschema
    from do_math.state_contract import default_state_contract
    row = default_state_contract().family('runtime', 'observations').schema['additionalProperties']
    return [error.message for error in jsonschema.Draft202012Validator(row['properties']['rule_ids'])
            .iter_errors(value['rule_ids'])]


def receive_stored_rule_ids(value):
    errors = stored_rule_id_errors(value)
    if errors:
        raise ValueError('; '.join(errors))


def observation_pairs(contract=None):
    """Four whole-record receivers; metadata is received as a map and measured per row.

    Fields come from the installed schema, including every optional property.
    The rule-ID fragment pair remains an independent input-preservation check.
    """
    from do_math.state_contract import default_state_contract, validate_record
    from support.observation_inputs import owner_observation_samples, tracker_record_samples
    contract = default_state_contract() if contract is None else contract
    pairs = []
    for name in ('observation_facts', 'self_check_obligations', 'self_check_responses', 'observations'):
        family = contract.family('runtime', name)
        metadata = name == 'observations'
        schema = family.schema['additionalProperties'] if metadata else family.schema

        def samples(root, name=name, metadata=metadata):
            rows = [(branch, {record['execution_id']: record} if metadata else record)
                    for branch, own, record in tracker_record_samples(root / 'tracker') if own == name]
            if metadata:
                rows.extend(owner_observation_samples(root / 'owner'))
            return rows

        def receive(value, family=family):
            validate_record(family.checker, value, family.name)
            if family.validator:
                family.validator(value)

        pairs.append(Pair('observation record (' + name + ')', samples, receive,
                          frozenset(schema['properties']),
                          written=(lambda value: set().union(*(set(row) for row in value.values())))
                          if metadata else (lambda value: set(value))))
    return pairs


def accepted_condition(space, family, pointer, value):
    """Whether the condition grammar accepts ``record_field_equals`` on ``family``'s ``pointer`` with ``value``."""
    from do_math.planning import validate_condition
    try:
        validate_condition({'op': 'record_field_equals', 'space': space, 'family': family, 'pointer': pointer,
                            'record_id': 'X-1', 'value': value})
    except ValueError:
        return False
    return True


def enumerated_pointers():
    """``(family, space, pointer, stored enumeration)`` for every exposed pointer whose stored field is enumerated."""
    from do_math import planning
    from do_math.state_contract import default_state_contract
    contract, rows = default_state_contract(), []
    for family, pointers in sorted(planning.EXPOSED_FIELDS.items()):
        space, key = planning.RECORD_FAMILIES.get(family, (None, None))
        if key is None:
            continue
        properties = contract.family(space, key).schema.get('properties', {})
        for pointer in sorted(pointers):
            stored = properties.get(pointer.lstrip('/'), {})
            if 'enum' in stored:
                rows.append((family, space, pointer, tuple(stored['enum'])))
    return rows


def _condition_pairs():
    """One pair per enumerated (condition family, pointer) (조사 C-25): the values the condition grammar accepts
    among the stored enumeration and the family's lifecycle values, against the stored enumeration.
    A value outside the enumeration that the grammar accepts is KD-0008."""
    from do_math.planning import lifecycle_values
    pairs = []
    for family, space, pointer, enumeration in enumerated_pointers():
        lifecycle = set(lifecycle_values().get(family, ())) if pointer in ('/status', '/lifecycle') else set()
        candidates = sorted(set(enumeration) | lifecycle)

        def samples(root, family=family, space=space, pointer=pointer, candidates=candidates):
            return [(str(value), {'value': value}) for value in candidates
                    if accepted_condition(space, family, pointer, value)]

        def receive(value, enumeration=enumeration):
            if value['value'] not in enumeration:
                raise ValueError(repr(value['value']) + ' is outside the stored enumeration')
        pairs.append(Pair(f'condition {family}{pointer}', samples, receive, frozenset(enumeration),
                          written=lambda value: {value['value']}))
    return pairs


def _runner_result_samples(root):
    """Actual runner/worker/collector results; only the external CLI and Job are doubles."""
    from copy import deepcopy
    import json
    from do_math import execution_profiles
    from do_math.control_transport import ControlTransport
    from support.entry import entry
    from support.fakes.clock import FakeClock
    from support.provider_inputs import PROFILE_CONFIG
    from support.provider_runs import (CLAUDE_INIT, ProviderJobs, ScriptedCLI, claude_result,
                                       dispatched, model_runner)
    rows = []
    for provider, model in (('codex', 'gpt-6-astra'), ('claude', 'claude-sonnet-5')):
        for index, outcome in enumerate(('collected', 'collected, bound', 'incomplete', 'stopped')):
            case = root / provider / str(index)
            workspace = case / 'workspace'
            workspace.mkdir(parents=True)
            clock = FakeClock()
            bound, stopped = outcome == 'collected, bound', outcome == 'stopped'
            final = b'Draft submitted.' if bound else b'{}'
            stdout = None
            if provider == 'claude':
                stdout = b''.join(json.dumps(event).encode('utf-8') + b'\n' for event in (
                    CLAUDE_INIT, claude_result(final, structured=not bound, total_cost_usd=0.0123,
                                               modelUsage={model: {'inputTokens': 1}})))
            cli = ScriptedCLI(final=final, stdout=stdout, returncode=1 if outcome == 'incomplete' else 0)
            jobs = ProviderJobs(cli, clock=clock, polls=20 if stopped else 0)
            prompt, options = 'Return an empty object.', {}
            if bound:
                config = deepcopy(PROFILE_CONFIG)
                config.update(tier_models={tier: model for tier in ('high', 'medium', 'low')},
                              session_limits={'work': {model: 3}})
                profiles = execution_profiles.build_profiles(config, host=entry().ports.host)
                profile = next(p for p in profiles['execution_profiles'].values() if p['role'] == 'research_work')
                prompt = execution_profiles.prepare_prompt('Submit the draft centrally.', profile)
                options = {'execution_id': 'EX-pair', 'profile': profile,
                           'input_seal': execution_profiles.prompt_seal(prompt),
                           'control_binding': ControlTransport(case / 'transport', clock=clock).issue(
                               'EX-pair', 'GR-pair', workspace=workspace),
                           'launch_ticket': dispatched('EX-pair', profile, jobs, clock)}
            result = model_runner(case, jobs, clock).run(
                prompt=prompt, output_schema={'type': 'object'}, workspace=workspace, evidence_dir=case / 'evidence',
                model=model, effort=profile['ai']['effort'] if bound else 'low', timeout_seconds=None,
                should_stop=(lambda: jobs.launched[0].resumed) if stopped else None, **options)
            assert len(cli.calls) == 1
            assert all(job.done and job.closed for job in jobs.launched)
            rows.append((provider + ', ' + outcome, result))
    return rows


def _receive_stored_result(value):
    """Decode the engine's stored artifact bytes so assertions can observe their content."""
    import json
    from do_math.canonical import canonical_json
    from do_math.payloads import json_safe
    return json.loads(canonical_json(json_safe(value)))


def _receive_operator_record(value):
    """Decode the file actually published by ``scheduled_operator._json(path, value)``."""
    import json
    import tempfile
    from do_math.file_io import read_bytes_shared
    from do_math.scheduled_operator import _json
    with tempfile.TemporaryDirectory() as directory:
        try:
            _json(Path(directory) / 'runner-result.json', value)
            return json.loads(read_bytes_shared(Path(directory) / 'runner-result.json'))
        except (TypeError, ValueError) as error:
            raise ValueError(str(error)) from None


PAIRS = [Pair('worker request (' + provider + ')', _worker_request_samples(provider),
              _receive_worker_request(provider), _worker_request_fields(provider))
         for provider in ('codex', 'claude')] + [
    Pair('trust registration request', _trust_request_samples, _receive_trust_request, _trust_request_fields()),
    Pair('observation rule id', lambda root: accepted_rule_ids(STORABLE_RULE_IDS), receive_stored_rule_ids,
         frozenset({'rule_ids'})),
    *observation_pairs(),
    *_condition_pairs(),
    Pair('runner result (stored artifact)', _runner_result_samples, _receive_stored_result, None),
    Pair('runner result (operator file)', _runner_result_samples, _receive_operator_record, None),
]

# 3-A의 catalog 참조 문자열 수신자는 객체 필드가 아닌 식별자 집합을 읽는다.
# 일반 쌍 외의 광고 완비·음성 순회는 unit.test_submission_advertised_inputs가 맡는다.
from support.submission_advertised import pair_samples as _submission_catalog_samples
from support.submission_advertised import receive_catalog as _submission_receive_catalog

PAIRS.append(Pair('submission advertised references', _submission_catalog_samples,
                  _submission_receive_catalog, None))
