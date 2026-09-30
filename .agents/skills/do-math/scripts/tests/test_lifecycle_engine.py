"""Feature-five lifecycle integration; CLI/Lean probes are explicit test doubles.

1f moved the other tests of this module to the new system (dispositions/engine.1.json).
These two stay until the product offers what their migration needs (the engine batch's report).
"""
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import create_autospec, patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from engine_fixtures import FakeEngine
from research_fixtures import FixtureAdapter


class LifecycleBoundaryTests(unittest.TestCase):
    """Clock, trust, limited-recovery and close boundaries of the lifecycle, on in-memory engines."""

    def test_limited_recovery_refuses_unbound_requests_and_surfaces_check_defects(self):
        with tempfile.TemporaryDirectory() as root:
            e = FakeEngine(root)
            with patch.object(e, '_check_limited_recovery', side_effect=AssertionError('unbound request checked')):
                self.assertFalse(e._limited_recovery_allowed({'id': 'AC-plain', 'role': 'maintenance'}))
            bound = {'id': 'AC-bound', 'role': 'maintenance', 'repair': {'limited_recovery': {'source_ref': 'UC-one'}}}
            with patch.object(e, '_check_limited_recovery', side_effect=KeyError('defect')):
                with self.assertRaises(KeyError):
                    e._limited_recovery_allowed(bound)


class GrantAndExternalEffectTests(unittest.TestCase):
    """Grant adoption and selection, initial queue, and external HTTP effects and their controls."""

    def setUp(self):
        temp=tempfile.TemporaryDirectory(); self.addCleanup(temp.cleanup)
        mock=patch('do_math.local_host.adapter_for',return_value=FixtureAdapter())
        mock.start(); self.addCleanup(mock.stop)
        self.engine=FakeEngine(temp.name); self.engine.activate()

    def prepare_http(self, *, once=False, credentials=False, scope=None, origin='http://127.0.0.1:1'):
        e=self.engine
        grant={'id':'GR-http-audit','kind':'http','reuse':'once' if once else 'reusable',
            'allowed_origins':[origin],'allowed_methods':['POST'],'allowed_path_prefixes':['/effect']}
        if credentials: grant['credential_env']={'X-Test':'LIFECYCLE_AUDIT_TEST_TOKEN'}
        if scope: grant.update(scope)
        e.control('decision',{'change':{'kind':'grant','grant':grant}})
        config={'operation':'prepare','id':'OP-audit','grant_id':grant['id'],
                'request':{'method':'POST','url':origin+'/effect','body':'test'}}
        return config

    def test_academic_control_binds_current_real_prerequisite(self):
        from do_math.academic import current_requirements, solution_basis
        e=self.engine; config=self.prepare_http(scope={'requires_academic':True})
        e._solution_basis=create_autospec(e._solution_basis,side_effect=lambda: solution_basis('synthetic-goal-evidence',
            list(e.instance['formal_results'].values())) if e.instance['goal_status']=='mathematically_solved' else None)
        with self.assertRaises(ValueError): e.control('external',config)
        # Synthetic upstream proof result; actual binding and academic prerequisite consumers.
        e.knowledge('K-academic')
        e.instance['goal_status']='mathematically_solved'
        basis=e._solution_basis(); self.assertIsNotNone(basis)
        e.control('external',config)
        op=e.runtime['external_operations'][config['id']]
        self.assertEqual(op['academic_basis'],{'solution_basis':basis,
            'requirements_sha256':current_requirements(e.instance)['sha256']})
        e.instance['goal_status']='unsolved'
        with patch('do_math.http_transport._http') as send:
            e.machine('external_action'); send.assert_not_called()
        self.assertEqual(e.runtime['external_operations'][config['id']]['status'],'cancelled')


if __name__=='__main__': unittest.main()
