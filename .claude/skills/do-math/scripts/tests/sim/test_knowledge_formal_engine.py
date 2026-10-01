"""Central checks on a Sim: controls, continuation admission and exact verifier binding."""
from copy import deepcopy
import json
import sys
import unittest

from do_math import formal, trust_validation
from support.engine_lifecycle import applied
from support.knowledge_formal_engine import (
    SOURCE, ReturnedValues, attempts, parked, run_formal, scene, stop_with_control, warm_scenes)
from support.knowledge_verifier_jobs import OutputCompiler
from support.provider_probes import ObservedCalls


def setUpModule():
    warm_scenes()


class FormalContinuationTests(unittest.TestCase):
    def test_pause_resume_retains_one_action_and_reaches_identity_review(self):
        sim, action = scene()
        stop_with_control(sim, action, 'pause')
        first, = attempts(sim)
        self.assertEqual(first['status'], 'ended')
        pending = next(a for a in sim.runtime['queue'] if a['id'] == action['id'])
        self.assertEqual(pending['continuation_of'], first['id'])
        self.assertNotEqual(sim.runtime['activities'][first['owner_activity_id']]['status'], 'finished')
        applied(sim, 'resume', config={})
        applied(sim, 'resume', config={})
        self.assertEqual(sum(a['id'] == action['id'] for a in sim.runtime['queue']), 1)
        run_formal(sim, pending)
        rows = attempts(sim)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[-1]['continuation_of'], first['id'])
        self.assertEqual(rows[-1]['formal_status'], 'verified')
        self.assertTrue(any(a['role'] == 'identity_review' for a in sim.runtime['queue']))

    def test_check_stopped_before_start_ends_and_returns_its_capacity(self):
        sim, action = scene()
        applied(sim, 'pause', config={})
        before_jobs = list(sim.jobs.launched)
        with ObservedCalls(verifier=formal.verify_lean) as observed:
            run_formal(sim, action)
        execution, = attempts(sim)
        self.assertEqual(observed.captured('verifier'), [])
        self.assertEqual(sim.jobs.launched, before_jobs)
        self.assertEqual((execution['status'], execution['capacity']['local_termination']), ('ended', 'confirmed'))
        pending = next(a for a in sim.runtime['queue'] if a['id'] == action['id'])
        self.assertEqual(pending['continuation_of'], execution['id'])

    def test_close_preserves_the_ended_check_without_continuation(self):
        sim, action = scene()
        stop_with_control(sim, action, 'close')
        self.assertFalse(any(a['id'] == action['id'] for a in sim.runtime['queue']))
        self.assertEqual(sim.runtime.get('waiting_actions', {}), {})
        execution, = attempts(sim)
        self.assertEqual(execution['status'], 'ended')
class FormalAuthority(unittest.TestCase):
    def test_missing_preapproved_environment_never_runs_or_autoapproves(self):
        with ObservedCalls(verifier=formal.verify_lean) as observed:
            sim, action, _, _, activity = parked()
        self.assertEqual(observed.captured('verifier'), [])
        self.assertEqual(sim.jobs.launched, [])
        self.assertIsNone(sim.instance['active_trust_environment'])
        self.assertEqual(sim.instance['trust_environments'], {})
        self.assertEqual(sim.runtime['activities'][activity]['status'], 'waiting')
        self.assertIn('approved fixed trust environment required', sim.runtime['waiting_actions'][action['id']]['reason'])

    def test_parked_check_returns_to_the_queue_once_an_environment_and_authority_admit_it(self):
        sim, action, environment, binding, _ = parked()
        sim.engine._resume_formal_waits()
        self.assertIn(action['id'], sim.runtime['waiting_actions'])
        sim.instance['trust_environments'][environment['id']] = environment
        sim.runtime['trust_bindings'][environment['id']] = binding
        sim.instance['active_trust_environment'] = environment['id']
        sim.engine._resume_formal_waits()
        self.assertNotIn(action['id'], sim.runtime['waiting_actions'])
        self.assertIn(action['id'], [a['id'] for a in sim.runtime['queue']])
        run_formal(sim, next(a for a in sim.runtime['queue'] if a['id'] == action['id']))
        self.assertEqual(attempts(sim)[0]['formal_status'], 'verified')

    def test_only_a_check_stopped_by_changed_conditions_resumes(self):
        sim, original, environment, binding, _ = parked()
        action = sim.runtime['waiting_actions'].pop(original['id'])['action']
        for identifier, reasons in (('AC-changed', ['authority_changed', 'input_changed']),
                                    ('AC-stopped', ['execution_stop_requested'])):
            sim.runtime['waiting_actions'][identifier] = {
                'action': {**action, 'id': identifier}, 'kind': 'formal_stopped', 'reason': ', '.join(reasons),
                'execution_id': 'EX-' + identifier, 'next_owner': 'trust_governance',
                'detail': {'stop_reasons': reasons}}
        sim.instance['trust_environments'][environment['id']] = environment
        sim.runtime['trust_bindings'][environment['id']] = binding
        sim.instance['active_trust_environment'] = environment['id']
        sim.engine._resume_formal_waits()
        self.assertEqual(list(sim.runtime['waiting_actions']), ['AC-stopped'])
        resumed = next(row for row in sim.runtime['queue'] if row['id'] == 'AC-changed')
        self.assertEqual(resumed['continuation_of'], 'EX-AC-changed')


class FormalBindingConnections(unittest.TestCase):
    def test_verifier_uses_the_fixed_environment_command_and_fingerprint(self):
        sim, action = scene(source=SOURCE, declarations=('t',), python_command=True)
        environment = deepcopy(sim.engine._formal_environment())
        sim.instance['config']['lean_command'] = ['unapproved-config-command']
        with ObservedCalls(verifier=formal.verify_lean) as observed:
            run_formal(sim, action)
        arguments, = observed.captured('verifier')
        self.assertEqual(arguments['lean_command'], [sys.executable])
        self.assertNotIn('timeout_seconds', arguments)
        self.assertEqual(arguments['expected_toolchain'], environment['toolchain'])
        self.assertEqual(set(arguments['allowed_axioms']), set(environment['allowed_axioms']))
        execution, = attempts(sim)
        self.assertEqual(execution['outcome'], 'execution_incomplete')

    def test_failed_compiler_unicode_evidence_crosses_the_real_worker_and_store(self):
        names = ('\N{KELVIN SIGN}', 'K')
        sim, action = scene(source=SOURCE, declarations=names)
        environment = deepcopy(sim.engine._formal_environment())
        sim.instance['config']['lean_command'] = ['unapproved-config-command']
        output = ''.join(f'"__DO_MATH_SIGNATURE_BEGIN_{name}__"\n{name} : True\n'
                         f'"__DO_MATH_SIGNATURE_END_{name}__"\n'
                         f"'{name}' does not depend on any axioms\n" for name in names)
        compiler = OutputCompiler(output)
        sim.lean.spawn = compiler
        with ReturnedValues(trust_validation.verify_formal) as returned, \
                ObservedCalls(verifier=formal.verify_lean) as observed:
            run_formal(sim, action)
        arguments, = observed.captured('verifier')
        self.assertEqual(arguments['lean_command'], environment['toolchain']['configured_command'])
        self.assertEqual(arguments['expected_toolchain'], environment['toolchain'])
        # This is the lower verifier's value before the owner judges/stores it.
        expected, = returned.values
        self.assertEqual(expected['status'], 'failed')
        self.assertEqual(expected['reason'], 'dependency output missing')
        self.assertEqual(expected['axioms'], {'\N{KELVIN SIGN}': [], 'K': []})
        self.assertEqual(len(compiler.commands), 1)
        execution, = attempts(sim)
        self.assertEqual(execution['formal_status'], 'failed')
        self.assertEqual(execution['outcome'], 'execution_incomplete')
        raw = sim.engine.store.read(execution['result_ref'], sim.engine.head)
        self.assertEqual(json.loads(raw), expected)
        source = sim.engine.store.read(execution['result_ref'].replace('formal.json', 'proposal.lean'), sim.engine.head)
        self.assertEqual(source, arguments['source'].encode('utf-8'))
        self.assertIn('e\N{COMBINING ACUTE ACCENT}\r\n'.encode('utf-8'), source)
