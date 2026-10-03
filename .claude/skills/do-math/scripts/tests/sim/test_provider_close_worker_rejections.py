"""실제 Claude load/run의 반려가 spawn과 파일 효과보다 앞서는지 검사한다."""
import json
from pathlib import Path
import re
import tempfile
import unittest

from do_math import claude_worker
from support.fakes.clock import FakeClock
from support.provider_runs import ProviderJobs, ScriptedCLI
from support.provider_close_inputs import request_seed, claude_rejections


class WorkerRejectionTests(unittest.TestCase):
    def test_claude_guards_reject_before_spawn_or_output_creation(self):
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        cli = ScriptedCLI()
        seed = request_seed('claude', root, jobs=ProviderJobs(cli), clock=FakeClock())
        path = root / 'request.json'
        for label, request, reason in claude_rejections(seed):
            with self.subTest(label=label):
                path.write_text(json.dumps(request), encoding='utf-8')
                before = {str(p.relative_to(root)): p.read_bytes() for p in root.rglob('*') if p.is_file()}
                with self.assertRaisesRegex(ValueError, '^' + re.escape(reason) + '$'):
                    claude_worker.run(path, spawn=cli.spawn)
                self.assertEqual(cli.calls, [])
                self.assertEqual({str(p.relative_to(root)): p.read_bytes() for p in root.rglob('*') if p.is_file()}, before)


class WorkerResourceBoundaryTests(unittest.TestCase):
    def test_produced_bound_requests_reject_invalid_limits_before_spawn(self):
        from copy import deepcopy
        import struct
        from do_math import codex_worker
        from do_math.configuration import DEFAULT_CONFIG
        from do_math.execution_profiles import build_profiles, prompt_seal
        from support.entry import entry
        from support.provider_runs import model_runner, dispatched
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        values = entry()
        for provider, worker, model in (
            ('codex', codex_worker, DEFAULT_CONFIG['tier_models']['high']),
            ('claude', claude_worker, 'claude-sonnet-5'),
        ):
            with self.subTest(provider=provider):
                directory = root / provider
                directory.mkdir()
                workspace = directory / 'workspace'
                workspace.mkdir()
                clock = FakeClock()
                cli = ScriptedCLI()
                jobs = ProviderJobs(cli, clock=clock)
                config = {**DEFAULT_CONFIG, 'scholarly_enabled': False,
                          'tier_models': {tier: model for tier in DEFAULT_CONFIG['tier_models']},
                          'session_limits': {'work': {model: DEFAULT_CONFIG['session_limits']['work'][
                              DEFAULT_CONFIG['tier_models']['high']]}}}
                profile = next(p for p in build_profiles(config, host=values.ports.host)['execution_profiles'].values()
                               if p['role'] == 'maintenance')
                prompt, execution_id = 'Validate this worker request.', 'EX-resource-' + provider
                evidence = directory / 'evidence'
                result = model_runner(directory, jobs, clock).run(
                    prompt=prompt, output_schema={}, workspace=workspace, evidence_dir=evidence,
                    model=profile['ai']['model'], effort=profile['ai']['effort'], timeout_seconds=1,
                    execution_id=execution_id, profile=profile, input_seal=prompt_seal(prompt),
                    launch_ticket=dispatched(execution_id, profile, jobs, clock))
                self.assertEqual(result['status'], 'completed')
                self.assertEqual(len(cli.calls), 1)
                seed = worker.load_request(evidence / 'request.json')
                path = directory / 'invalid-request.json'
                invalid = [
                    (None, 'explicit resource limits cannot be null'),
                    ([], 'Job limits need positive commit bytes and CPU hard-cap basis points in 1..10000'),
                    ({'memory_bytes': 1}, 'Job limits need positive commit bytes and CPU hard-cap basis points in 1..10000'),
                    ({'memory_bytes': True, 'cpu_rate_basis_points': 1},
                     'Job limits need positive commit bytes and CPU hard-cap basis points in 1..10000'),
                    ({'memory_bytes': 0, 'cpu_rate_basis_points': 1},
                     'Job limits need positive commit bytes and CPU hard-cap basis points in 1..10000'),
                    ({'memory_bytes': 1 << (8 * struct.calcsize('N')), 'cpu_rate_basis_points': 1},
                     'Job limits need positive commit bytes and CPU hard-cap basis points in 1..10000'),
                    ({'memory_bytes': 1, 'cpu_rate_basis_points': 10001},
                     'Job limits need positive commit bytes and CPU hard-cap basis points in 1..10000'),
                ]
                for limits, reason in invalid:
                    with self.subTest(limits=limits):
                        request = {**deepcopy(seed), 'resource_limits': limits}
                        path.write_text(json.dumps(request), encoding='utf-8')
                        before = {p.relative_to(directory).as_posix(): p.read_bytes()
                                  for p in directory.rglob('*') if p.is_file()}
                        with self.assertRaisesRegex(ValueError, '^' + re.escape(reason) + '$'):
                            worker.run(path, spawn=cli.spawn)
                        self.assertEqual(len(cli.calls), 1)
                        self.assertEqual({p.relative_to(directory).as_posix(): p.read_bytes()
                                          for p in directory.rglob('*') if p.is_file()}, before)
                if provider == 'codex':
                    # main has no spawn parameter; this deliberately invalid request
                    # must stop in load_request, before the bound default spawn.
                    with self.assertRaisesRegex(ValueError, '^' + re.escape(invalid[-1][1]) + '$'):
                        codex_worker.main([str(path)])
                    self.assertEqual(len(cli.calls), 1)

    def test_codex_main_rejects_argument_cardinality(self):
        from do_math import codex_worker
        for arguments in ([], ['one.json', 'two.json']):
            with self.subTest(arguments=arguments):
                with self.assertRaises(SystemExit) as stopped:
                    codex_worker.main(arguments)
                self.assertEqual(stopped.exception.code, 'usage: codex_worker.py REQUEST.json')
