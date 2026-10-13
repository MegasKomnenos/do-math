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
own in ``test_pairs.py`` carries the ledger mark. The storage families' pair is
two whole-product checks in ``tests/structure/test_storage_fields.py``
(설계 10절 A22).
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


def _worker_request_samples(provider):
    """The worker request ``ModelRunner`` writes (``model_call.worker_request_fields``) on each assignment branch."""
    from support.entry import entry
    _entry = entry()
    def samples(root):
        from copy import deepcopy
        from do_math.claude_adapter import ADAPTERS
        from do_math.configuration import DEFAULT_CONFIG
        from do_math.control_transport import ControlTransport
        from do_math.execution_profiles import build_profiles, profile_ref
        from do_math.model_call import worker_request_fields
        from support.fakes.clock import FakeClock
        workspace, evidence = root / 'workspace', root / 'evidence'
        workspace.mkdir()
        options = ADAPTERS[provider](str(root / (provider + '.exe')), jobs=_entry.ports.jobs, clock=_entry.ports.clock).worker_options(evidence)
        profile = next(iter(build_profiles(deepcopy(DEFAULT_CONFIG), host=_entry.ports.host)['execution_profiles'].values()))
        reference, execution_id = profile_ref(profile), 'EX-01M3HM0X0000000000000000AB'
        binding = ControlTransport(root / 'control', clock=FakeClock()).issue(execution_id, 'GR-pair',
                                                                                workspace=workspace)
        # ModelRunner gives the CLI a schema file exactly when the call is unbound, and passes a configured
        # "claude:<name>" model to the CLI as <name>.
        cli_model = DEFAULT_CONFIG['tier_models']['high'] if provider == 'codex' else 'claude:claude-sonnet-5'.removeprefix('claude:')
        rows = []
        for bound, limits, control, scholarly, only in product((False, True), repeat=5):
            schema = not control
            if (limits or control) and not bound:
                continue  # the runner pins limits and a control binding only to an identified execution
            branch = ','.join(name for name, on in (('schema', schema), ('identity', bound), ('limits', limits),
                              ('control', control), ('scholarly', scholarly), ('claude_only', only)) if on) or 'bare'
            rows.append((branch, worker_request_fields(
                options, prompt_path=evidence / 'input.txt', workspace=workspace, evidence_dir=evidence,
                cli_model=cli_model, effort='high', timeout_seconds=600.0,
                schema_path=evidence / 'output.schema.json' if schema else None,
                execution_id=execution_id if bound else None, reference=reference if bound else None,
                resource_limits={'memory_bytes': 1 << 30, 'cpu_rate_basis_points': 5000} if limits else None,
                control_binding=binding if control else None,
                scholarly_server={'command': str(root / 'python.exe'), 'args': [str(root / 'server.py')]}
                if scholarly else None,
                claude_only_assigned_model=only)))
        return rows
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
    """Registration requests ``trust_inventory.registration_request`` makes for a Lean core and a Lake project
    toolchain, from the record's first baseline and from a rerecorded (second) baseline."""
    import hashlib
    from do_math import formal, trust_inventory as records
    from do_math.file_io import sha256_file
    from support.trust_inputs import validation_fixture
    from support.fakes.clock import FakeClock
    rows = []
    for kind in ('core', 'project'):
        directory = root / kind
        for relative in ('toolchain/bin/lean.exe', 'toolchain/bin/lake.exe', 'toolchain/lib/lean/Init/Prelude.olean'):
            path = directory / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b'synthetic ' + relative.encode())
        lean, lake = (directory / 'toolchain/bin/lean.exe').resolve(), (directory / 'toolchain/bin/lake.exe').resolve()
        checker = Path(formal.__file__).resolve()
        project = None
        if kind == 'project':
            (directory / 'project' / '.lake').mkdir(parents=True)
            (directory / 'project' / 'lakefile.lean').write_text('-- synthetic', encoding='utf-8')
            project = {'manifest_hashes': {'lakefile.lean': hashlib.sha256(b'-- synthetic').hexdigest()},
                       'source_identity': {'root': str((directory / 'project').resolve())},
                       'search_paths': [str((directory / 'project' / '.lake').resolve())]}
        identity = {'executable': str(lean), 'sha256': sha256_file(lean), 'version': 'Lean 4.32.0',
                    'version_exit': 0, 'configured_command': [str(lean)],
                    'verifier_sha256': sha256_file(checker), 'verifier_path': str(checker),
                    'executables': {str(lean): sha256_file(lean), str(lake): sha256_file(lake)}, 'project': project}
        fingerprint = records.observe_fingerprint(identity)
        content = records.content_hashes(identity, fingerprint['files'])
        validation = validation_fixture(identity, directory / 'smoke.lean')
        record = records.new_record(identity, records.new_baseline(fingerprint, content, validation, clock=FakeClock()))
        path = records.record_path(directory / 'records', record['id'])
        records.write_record(path, record)
        rows.append((kind + ', first baseline', records.registration_request(record, path, records.binding(record))))
        record['baselines'].append(records.new_baseline(fingerprint, content, validation, clock=FakeClock()))
        records.write_record(path, record)
        rows.append((kind + ', rerecorded', records.registration_request(record, path, records.binding(record))))
    return rows


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
    """The engine keeps a runner result as a stored artifact: ``canonical_json(json_safe(result))``."""
    from do_math.canonical import canonical_json
    from do_math.payloads import json_safe
    canonical_json(json_safe(value))


def _receive_operator_record(value):
    """The scheduled operator writes a runner result file with ``scheduled_operator._json(path, value)``."""
    import tempfile
    from do_math.scheduled_operator import _json
    with tempfile.TemporaryDirectory() as directory:
        try:
            _json(Path(directory) / 'runner-result.json', value)
        except (TypeError, ValueError) as error:
            raise ValueError(str(error)) from None


PAIRS = [Pair('worker request (' + provider + ')', _worker_request_samples(provider),
              _receive_worker_request(provider), _worker_request_fields(provider))
         for provider in ('codex', 'claude')] + [
    Pair('trust registration request', _trust_request_samples, _receive_trust_request, _trust_request_fields()),
    Pair('observation rule id', lambda root: accepted_rule_ids(STORABLE_RULE_IDS), receive_stored_rule_ids,
         frozenset({'rule_ids'})),
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
