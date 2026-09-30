"""Owner-thread machine continuations, scheduler progress, and real Job barriers."""
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
import os
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import create_autospec, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math.engine import ResearchEngine
from do_math.parallel import ModelCalls
from do_math.execution_lifecycle import transition_execution
from do_math.repository import ResearchRepository
from do_math.system_clock import new_id
from do_math import knowledge_records
from engine_fixtures import FakeEngine
from research_fixtures import FixtureAdapter, await_stop, clock_ports, git_init
from state_fixtures import owner_calls
from test_categories import test_group


class Host(FakeEngine):
    _execution_profile = ResearchEngine._execution_profile

    def __init__(self, root):
        self.owner_thread = threading.get_ident()
        super().__init__(root)
        self.activate()
        from do_math.execution_profiles import build_profiles
        self.instance['config']['lean_command'] = self.instance['trust_environments'][self.instance['active_trust_environment']]['toolchain']['configured_command']
        configured = build_profiles(self.instance['config'])
        self.instance['execution_profiles'].update(configured['execution_profiles'])
        self.instance['role_profile_refs'].update(configured['role_profile_refs'])
        self.ai_finished = threading.Event()
        self.tick = 0.
        self.control_action = lambda: None
        self.identity_reviews = []
        self.runner = SimpleNamespace(run=lambda **args: {'status': 'completed'})

    def storage_double(self):
        self.store = create_autospec(ResearchRepository, instance=True)
        self.store.load.side_effect = lambda snapshot=None: (
            self.head, deepcopy(self.saves[-1]['instance']), deepcopy(self.saves[-1]['runtime']))

    def _save(self, artifacts=None):
        if threading.get_ident() != self.owner_thread:
            raise AssertionError('engine mutation escaped the owner thread')
        super()._save(artifacts)
        self.head = 'fixture-head-' + str(len(self.saves))  # A publication moves the head.
        self._evaluate_stops()  # The real publication point judges stops after every save.

    def _controls(self):
        if self._calls is not None:
            self._calls.pump()
        self.control_action()

    def _check_installation(self, **kwargs): return True
    def _refresh_readiness(self): pass
    def _settle_activity(self, execution_id): pass
    def _start_identity_review(self, kid): self.identity_reviews.append(kid)

    def _call_steps(self, action):
        # Only the model response is synthetic. Admission, collection and release
        # still use the scheduler's real Git-backed reservation implementation.
        profile = self._execution_profile(action)
        eid = new_id('EX')
        execution = self._register_execution(action, {'id': eid, 'role': action['role'], 'status': 'queued'})
        assert self._session_slots().acquire(eid, profile=profile, execution=execution)
        transition_execution(execution, 'running', at=self._lifecycle_now().isoformat())
        result = yield {'execution_id': eid}
        assert result['status'] == 'completed', result
        self._end_machine_execution(execution, outcome='execution_incomplete', disposition={'kind': 'synthetic_AI_return'})
        self._remove_action(action)
        self.ai_finished.set()

    def candidate(self, kid):
        self.instance, _ = knowledge_records.create_candidate(self.instance, {
            'id': kid, 'kind': 'lemma', 'statement': 'One equals one', 'summary': 'Reflexivity',
            'lean_code': 'theorem fixture : 1 = 1 := rfl', 'declaration_names': ['fixture'], 'dependencies': []},
            source_ref='UI-source', actor_ref='EX-author')
        return {'id': new_id('AC'), 'role': 'formal_check', 'target': kid}


class MachineSchedulerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.enterContext(patch('do_math.local_host.adapter_for', return_value=FixtureAdapter()))
        self.enterContext(patch('do_math.windows_job.named_job_empty', return_value=True))
        self.host = Host(self.temp.name)
        self.host.ports = clock_ports(monotonic=lambda: self.host.tick)

    def test_environment_failure_waits_for_rerecord_before_compiler_retry(self):
        import os
        import setup_lean
        from research_fixtures import fixture_setup_lean
        host = self.host
        action = host.candidate('K-env')
        host.runtime['queue'] = [action]
        environment = host.instance['trust_environments'][host.instance['active_trust_environment']]
        bound = deepcopy(host.runtime['trust_bindings'][environment['id']])
        olean = Path(environment['toolchain']['executable']).parents[1] / 'lib/lean/Init/Prelude.olean'
        info = os.stat(olean)
        os.utime(olean, ns=(info.st_atime_ns, info.st_mtime_ns + 10**9))  # e.g. a cache re-download
        from unittest.mock import Mock
        host.formal_verifier = Mock()
        with owner_calls(host):
            host._formal(action)
        host.formal_verifier.assert_not_called()
        waiting = host.runtime['waiting_actions'][action['id']]
        self.assertEqual(waiting['kind'], 'formal_environment')
        self.assertEqual(waiting['next_owner'], 'trust_governance')
        previous = waiting['execution_id']
        host._resume_formal_waits()
        self.assertIn(action['id'], host.runtime['waiting_actions'])
        record_path = Path(environment['toolchain_record']['path'])
        with fixture_setup_lean(environment['toolchain'], record_path.parent / 'smoke.lean'):
            recorded =setup_lean.rerecord(['unused'], record_path.parent, record_path.parent / 'evidence', None)
        host._resume_formal_waits()
        successor = next(a for a in host.runtime['queue'] if a['id']==action['id'])
        self.assertEqual(successor['continuation_of'], previous)
        self.assertNotIn(action['id'], host.runtime['waiting_actions'])
        def verify(**args):
            args['on_started']({'job_name':args['launch_ticket']['job_name']})
            return host.verification(args['source'], args['declarations'], args['expected_toolchain'])
        host.formal_verifier = verify
        with owner_calls(host):
            host._formal(successor)
        latest = next(e for e in host.runtime['executions'].values() if e.get('continuation_of')==previous)
        self.assertEqual(latest['outcome'], 'output_accepted')
        self.assertEqual(host.runtime['trust_bindings'][environment['id']], recorded['binding'])
        rebound = [row for row in host.runtime['events'] if row['kind'] == 'trust_environment_rebound']
        self.assertEqual([(row['previous'], row['current']) for row in rebound], [(bound, recorded['binding'])])


if __name__ == '__main__':
    unittest.main()
