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

``tests/contracts/test_pairs.py`` walks every pair. To add a pair, add a ``Pair``
to ``PAIRS``; a pair with no samples or no named fields fails the walk.
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
    fields: frozenset
    written: Callable[[Any], set] = lambda value: set(value)


def _worker_request_samples(provider):
    """The worker request ``ModelRunner`` writes (``model_call.worker_request_fields``) on each assignment branch."""
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
        options = ADAPTERS[provider](str(root / (provider + '.exe'))).worker_options(evidence)
        profile = next(iter(build_profiles(deepcopy(DEFAULT_CONFIG))['execution_profiles'].values()))
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
            if only and provider != 'claude':
                continue
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


PAIRS = [Pair('worker request (' + provider + ')', _worker_request_samples(provider),
              _receive_worker_request(provider), _worker_request_fields(provider))
         for provider in ('codex', 'claude')]
