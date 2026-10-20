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
    def test_public_revision_stops_the_fixed_input_and_preserves_its_original_source(self):
        from do_math.knowledge import plan_impact, revision_roots
        from support.engine_lifecycle import clear_work
        from support.knowledge_builders import knowledge_candidate
        from support.sim import Sim
        sim = Sim.activated()
        clear_work(sim)
        kid = sim.clock.new_id('KN')
        candidate = knowledge_candidate(id=kid)
        applied(sim, 'knowledge', config={'operation': 'import', 'candidate': candidate})
        sim.lean.allow(candidate['lean_code'], ['truth'], signatures={'truth': 'truth : True'},
            declaration_evidence={'truth': {'type': 'True', 'value': None}}, axioms={'truth': []}, dependencies={'truth': {}})
        sim.engine._enqueue('formal_check', kid)
        sim.engine._save()
        action = next(a for a in sim.runtime['queue'] if a['role'] == 'formal_check' and a['target'] == kid)
        old_source = candidate['lean_code']
        plan = plan_impact(sim.instance, sim.runtime, revision_roots(sim.instance, kid), [])
        stop_with_control(sim, action, 'knowledge', config={'operation': 'revise', 'id': kid,
            'changes': {'statement': 'A revised mathematical statement'}, 'reason': 'reassess the fixed input',
            'declared_impact': plan['computed_impact']})
        execution, = attempts(sim)
        self.assertEqual((execution['outcome'], execution['formal_status']), ('execution_incomplete', 'stopped'))
        self.assertIn('input_changed', execution['result_disposition']['stop_reasons'])
        self.assertNotIn('submission_receipt', execution)
        self.assertEqual(sim.instance['knowledge'][kid]['lifecycle'], 'superseded')
        raw = sim.engine.store.read(execution['result_ref'], sim.engine.head)
        self.assertEqual(json.loads(raw)['status'], 'stopped')
        self.assertEqual(sim.engine.store.read(execution['result_ref'].replace('formal.json', 'proposal.lean'),
                                             sim.engine.head), old_source.encode())
        self.assertEqual(sim.runtime['waiting_actions'][action['id']]['kind'], 'formal_stopped')
        owner = sim.runtime['executions'][execution['id']]['owner_activity_id']
        sim.engine._resume_formal_waits()
        self.assertNotIn(action['id'], sim.runtime['waiting_actions'])
        self.assertFalse(any(a.get('target') == kid and a['role'] == 'formal_check' for a in sim.runtime['queue']))
        self.assertEqual(sim.runtime['activities'][owner]['status'], 'finished')

    def test_withdrawn_authority_wait_finishes_its_owner_without_starting_a_compiler(self):
        from do_math.knowledge import invalidate_knowledge
        sim, action, environment, binding, owner = parked()
        sim.engine.instance, sim.engine.runtime = invalidate_knowledge(sim.instance, sim.runtime, 'K1',
            reason='Withdraw the obsolete proposal', actor_ref=sim.instance['lifecycle']['input_id'],
            declared_impact=[], clock=sim.clock)
        sim.engine._save()
        sim.engine._resume_formal_waits()
        self.assertNotIn(action['id'], sim.runtime['waiting_actions'])
        self.assertEqual(sim.runtime['activities'][owner]['status'], 'finished')
        self.assertEqual(attempts(sim), [])

    def test_actual_identity_rejection_and_publication_gate_both_require_environment_recovery(self):
        """3-C/C-15: a changed owned executable, with actual identity checks and no compiler start."""
        from pathlib import Path
        import tempfile
        from support.sim import Sim
        from support.fakes.host import FakeHost
        from do_math.trust_validation import EnvironmentUnavailable, require_active_environment
        with tempfile.TemporaryDirectory() as directory:
            sim = Sim.activated(directory)
            environment = deepcopy(sim.engine._formal_environment())
            toolchain = environment['toolchain']
            executable = Path(toolchain['executable'])
            self.assertTrue(executable.resolve().is_relative_to(Path(directory).resolve()))
            original = executable.read_bytes()
            self.assertEqual(formal.toolchain_identity_errors(toolchain, jobs=sim.jobs, clock=sim.clock,
                environment=sim.environment, git_backend=sim.ports.git_backend), [])
            from do_math import knowledge_records
            from support.engine_lifecycle import clear_work
            clear_work(sim)
            sim.engine.instance, _ = knowledge_records.create_candidate(sim.instance, {
                'id': 'K-C15', 'kind': 'lemma', 'title': 'Identity classification source',
                'statement': 'True', 'summary': 'Identity classification', 'explanation': 'By introduction.',
                'lean_code': 'theorem rejected_identity : True := True.intro',
                'declaration_names': ['rejected_identity'], 'dependencies': []},
                source_ref=sim.instance['lifecycle']['input_id'], actor_ref=next(iter(sim.runtime['executions'])), clock=sim.clock)
            sim.engine._enqueue('formal_check', 'K-C15')
            sim.engine._save()
            action = next(a for a in sim.runtime['queue'] if a['role'] == 'formal_check')
            executable.write_bytes(original + b'changed owned executable')
            errors = formal.toolchain_identity_errors(toolchain, jobs=sim.jobs, clock=sim.clock,
                environment=sim.environment, git_backend=sim.ports.git_backend)
            self.assertTrue(errors)
            before = len(sim.jobs.launched)
            result = formal.verify_lean(source='theorem rejected_identity : True := True.intro',
                declarations=['rejected_identity'], workspace=sim.root,
                lean_command=toolchain['configured_command'], expected_toolchain=toolchain,
                jobs=sim.jobs, clock=sim.clock, environment=sim.environment, git_backend=sim.ports.git_backend)
            self.assertEqual((result['status'], result['error_kind']), ('rejected', 'trust_environment'))
            self.assertEqual(len(sim.jobs.launched), before)
            host = FakeHost(toolchain_errors=errors)
            with self.assertRaisesRegex(EnvironmentUnavailable, 'current trust identity required') as rejected:
                require_active_environment(sim.instance, sim.runtime, current_identity=True, host=host)
            self.assertEqual(rejected.exception.detail['environment_id'], environment['id'])
            run_formal(sim, action)
            self.assertEqual(sim.runtime['waiting_actions'][action['id']]['kind'], 'formal_environment')
            self.assertFalse(any(a['role'] == 'research_plan' and a.get('formal_target') == 'K-C15'
                                 for a in sim.runtime['queue']))

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
    def test_new_transition_before_publication_keeps_the_verified_return_and_rejects_the_seal(self):
        """T3 4.3 s: a registered second environment, real worker return and owner control pass are the publication boundary."""
        from support.engine_lifecycle import next_environment, only
        sim, action = scene()
        target = next_environment(sim, 'transition-before-seal', configure=False)
        old = sim.instance['active_trust_environment']
        formal_id = sim.instance['knowledge'][action['target']]['formal_result_id']
        original_formal = deepcopy(sim.instance['formal_results'][formal_id])
        spawn, requests = sim.lean.spawn, []
        def request_transition(command, **options):
            if not requests:
                requests.append(sim.control('trust', text='move trust before admitting the compiler result',
                    config={'operation': 'transition', 'env_id': target}))
            return spawn(command, **options)
        sim.lean.spawn = request_transition
        only(sim, 'formal_check')
        sim.engine._save()
        try:
            sim.step()
        finally:
            sim.lean.spawn = spawn
        self.assertEqual(len(requests), 1)
        execution, = attempts(sim)
        raw = json.loads(sim.engine.store.read(execution['raw_result_ref'], sim.engine.head))
        self.assertEqual(raw['status'], 'verified')
        result = json.loads(sim.engine.store.read(execution['result_ref'], sim.engine.head))
        self.assertEqual(result, {**raw, 'status': 'failed',
                                 'reason': 'formal publication waits for the trust transition'})
        self.assertEqual((execution['status'], execution['outcome'], execution['formal_status']),
                         ('ended', 'execution_incomplete', 'failed'))
        self.assertEqual(execution['capacity']['local_termination'], 'confirmed')
        self.assertEqual(execution['result_disposition']['stop_reasons'], [])
        self.assertNotIn('submission_receipt', execution)
        self.assertEqual(sim.instance['formal_results'][formal_id], original_formal)
        self.assertEqual(sim.instance['active_trust_environment'], old)
        self.assertFalse(any(a['role'] == 'identity_review' and a.get('target') == action['target']
                             for a in sim.runtime['queue']))
        self.assertTrue(any(a['role'] == 'research_plan' and a.get('formal_target') == action['target']
                            for a in sim.runtime['queue']))

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
