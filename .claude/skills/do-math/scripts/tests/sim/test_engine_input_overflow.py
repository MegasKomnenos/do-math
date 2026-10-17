"""The planner's choice for a held input overflow on the Sim's real engine (``core_engine``, ``integration``, ``submission``).

Research work held by an input overflow waits for the planner, whose role
input offers the held action with its allowed larger profile; the planner's
extension may choose that profile, and the engine requeues the same action.
The held state is built on the restored public activation
(``support.engine_overflow.held_work``) with the product's task, activity and
profile functions; the legacy tests held it in ``context_engine``, an engine
without ``__init__`` whose store, session slots and clock were autospec doubles.
The planner's role input is the product's own packaging
(``support.engine_context.package``: ``_context`` and ``prepare_role_input``).
"""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

import jsonschema

from do_math import contracts, integration, submission
from do_math.canonical import canonical_json
from support.engine_context import package
from support.role_answers import seal_response
from support.default_responder import common
from support.engine_overflow import held_work
from support.sim import Sim, warm_template

setUpModule = warm_template


def directory(test):
    folder = tempfile.TemporaryDirectory()
    test.addCleanup(folder.cleanup)
    return Path(folder.name)


class OverflowConnections(unittest.TestCase):
    def setUp(self):
        self.sim = Sim.activated()
        self.engine = self.sim.engine
        self.reference = held_work(self.sim)

    def test_overflow_choices_are_supplied_without_changing_ready_population(self):
        from do_math.context_store import prepare_role_input
        from support.provider_probes import ObservedCalls
        with ObservedCalls(package=prepare_role_input) as observed:
            fitted, fixed = package(self.engine, directory(self))
        self.assertIs(observed.captured('package')[0]['clock'], self.engine.ports.clock)
        self.assertEqual(fixed['ready_task_ids'], [])
        item = fitted['context']['input_overflow_requests'][0]
        self.assertEqual(item['action_id'], 'AC-held')
        self.assertEqual(item['owner_activity_id'], 'AY-held')
        self.assertEqual(item['allowed_profile_refs'], [self.reference])

    def test_planner_extension_accepts_exact_choice_and_requeues_same_obligation(self):
        engine = self.engine
        choice = {'action_id': 'AC-held', 'profile_ref': self.reference, 'reason': 'Required evidence fits'}
        extension = {'input_overflow_resolutions': [choice]}
        jsonschema.validate(extension, submission.extension_schema({'role': 'research_plan'}))
        _, fixed = package(engine, directory(self))
        engine._apply_input_overflow_resolutions([choice], fixed, 'EX-plan')
        action = next(a for a in engine.runtime['queue'] if a['id'] == 'AC-held')
        self.assertEqual(action['owner_activity_id'], 'AY-held')
        self.assertEqual(action['profile_ref'], self.reference)
        self.assertEqual(action['model_assessment']['difficulty'], 'low')
        self.assertEqual(action['input_overflow_retry']['request_id'], 'EX-plan')
        self.assertEqual(action['input_overflow_retry']['state'], 'pending')
        self.assertNotIn('AC-held', engine.runtime['waiting_actions'])

    def test_stale_contract_or_unoffered_profile_cannot_release_wait(self):
        """About 2.6 s, over the 2 s Sim budget: each of the four cases packages the planner's full role input."""
        engine = self.engine
        start = deepcopy((engine.instance, engine.runtime))
        for mutation, reason in STALE:
            with self.subTest(mutation=mutation):
                engine.instance, engine.runtime = deepcopy(start)
                _, fixed = package(engine, directory(self))
                choice = {'action_id': 'AC-held', 'profile_ref': self.reference, 'reason': 'Fits'}
                if mutation == 'contract':
                    engine.runtime['tasks']['TK-1']['revision'] += 1
                elif mutation == 'profile':
                    choice['profile_ref'] = engine.instance['role_profile_refs']['research_plan'][0]
                elif mutation == 'question':
                    engine.runtime['waiting_actions']['AC-held']['question_id'] = 'QU-new-failure'
                else:
                    engine.runtime['waiting_actions']['AC-held']['action']['role'] = 'identity_review'
                with self.assertRaisesRegex(ValueError, reason):
                    engine._apply_input_overflow_resolutions([choice], fixed, 'EX-plan')
                self.assertIn('AC-held', engine.runtime['waiting_actions'])

    def test_revised_task_keeps_the_original_overflow_contract_pin_and_cannot_resume_it(self):
        """T3 18.5 s cold: actual review, replacement and sealed planner input establish the old contract pin."""
        from do_math import planning
        from do_math.execution_lifecycle import transition_execution
        from support.role_answers import review_items
        from support.planning_contract_inputs import produce_task
        engine = self.engine
        original = deepcopy(engine.runtime['tasks']['TK-1'])
        pin = engine.runtime['waiting_actions']['AC-held']['action']['selected_contract_sha256']
        self.assertEqual(pin, planning.contract_hash(original))
        action = {'id': 'AC-revision-review', 'role': 'task_contract_review', 'target': 'TK-1'}
        review = engine._register_execution(action,
            {'id': 'EX-revision-review', 'role': 'task_contract_review', 'status': 'running'})
        transition_execution(review, 'stopping', at=self.sim.clock.now())
        transition_execution(review, 'ended', at=self.sim.clock.now(), outcome='execution_incomplete')
        engine._apply(action, review_items(['TK-1'], decision='revision_required',
            next_owner='research_preparation', findings=['Clarify the held task contract']),
            review['id'], owns_response=False)
        self.assertEqual(engine.runtime['tasks']['TK-1']['status'], 'waiting')
        identifier = produce_task(self.sim, 'Revised held task', revises='TK-1',
                                  profiles=[self.reference])
        self.assertEqual(identifier, 'TK-1')
        self.assertGreater(engine.runtime['tasks'][identifier]['revision'], original['revision'])
        self.assertNotEqual(planning.contract_hash(engine.runtime['tasks'][identifier]), pin)
        _, fixed = package(engine, directory(self))
        request, = fixed['input_overflow_requests']
        self.assertEqual(request['contract_revision'], engine.runtime['tasks'][identifier]['revision'])
        self.assertEqual(request['contract_sha256'], pin)
        before = deepcopy((engine.head, engine.instance, engine.runtime))
        choice = {'action_id': 'AC-held', 'profile_ref': self.reference, 'reason': 'Larger input fits'}
        with self.assertRaisesRegex(ValueError, '^input overflow task contract changed: AC-held$'):
            engine._apply_input_overflow_resolutions([choice], fixed, 'EX-plan')
        self.assertEqual((engine.head, engine.instance, engine.runtime), before)

    def test_shared_submission_check_rejects_duplicate_and_unoffered_choices(self):
        from support.entry import entry
        _entry = entry()
        engine = self.engine
        root = directory(self)
        _, fixed = package(engine, root)
        choice = {'action_id': 'AC-held', 'profile_ref': self.reference, 'reason': 'Fits required evidence'}
        for mode, expected in (('valid', []), *SUBMISSION_ISSUES):
            with self.subTest(mode=mode):
                row = deepcopy(choice)
                if mode == 'profile':
                    row['profile_ref'] = engine.instance['role_profile_refs']['research_plan'][0]
                if mode == 'unknown':
                    row['action_id'] = 'AC-unknown'
                extensions = {'input_overflow_resolutions': [row, row] if mode == 'duplicate' else [row]}
                (root / 'activity-extensions.json').write_bytes(canonical_json(extensions))
                output = common('research_plan')
                seal_response(output, fixed, root)
                issues = submission.payload_issues(output, contracts.schema_for('research_plan'), fixed, extensions, root, clock=_entry.ports.clock)
                self.assertEqual([issue['message'] for issue in issues], expected, (mode, issues))

    def test_same_integration_receipt_prevents_duplicate_retry(self):
        engine = self.engine
        _, fixed = package(engine, directory(self))
        extension = {'input_overflow_resolutions': [{'action_id': 'AC-held', 'profile_ref': self.reference, 'reason': 'Fits'}]}
        calls = []

        def apply(instance, runtime, bundle):
            calls.append(bundle['integration_id'])
            engine.instance, engine.runtime = instance, runtime
            engine._apply_input_overflow_resolutions(bundle['extensions']['input_overflow_resolutions'], fixed, 'EX-plan')
        callbacks = {'apply_bundle': apply, 'validate_candidate': lambda *args: None,
                     'validate_current': lambda *args: None, 'publish': lambda *args: None}
        first = integration.apply_bundles(engine.instance, engine.runtime, common('research_plan'), extension, fixed,
                                          execution_id='EX-plan', **callbacks)
        self.assertEqual(first['status'], 'accepted', first['issues'])
        second = integration.apply_bundles(first['instance'], first['runtime'], common('research_plan'), extension, fixed,
                                           execution_id='EX-plan', **callbacks)
        self.assertEqual(second['bundles'][0]['status'], 'already_accepted', second['issues'])
        self.assertEqual(len(calls), 1)
        self.assertEqual(len([a for a in second['runtime']['queue'] if a['id'] == 'AC-held']), 1)


class InputRecoveryMarkerTests(unittest.TestCase):
    def test_preexisting_user_resolution_is_preserved_when_retry_input_fits(self):
        engine = Sim.activated().engine
        prior_history = [{'resolution_ref': 'DE-user', 'affected_ids': ['AC-held']}]
        engine.runtime['question_links'] = [{'id': 'QU-overflow', 'status': 'resolved', 'resolution_ref': 'DE-user',
                                             'unresolved_target_ids': [], 'resolution_history': deepcopy(prior_history)}]
        disposition = engine._resolve_input_overflow_question('QU-overflow', execution_id='EX-retry',
            kind='input_overflow_retry_resolved', evidence={'action_id': 'AC-held'})
        question = engine.runtime['question_links'][0]
        self.assertEqual(disposition, 'already_resolved')
        self.assertEqual(question['resolution_ref'], 'DE-user')
        self.assertEqual(question['resolution_history'], prior_history)


STALE = [('contract', '^input overflow request changed before profile selection: AC-held$'),
         ('profile', '^input overflow profile was not offered for this action: AC-held$'),
         ('question', '^input overflow request changed before profile selection: AC-held$'),
         ('review', '^input overflow action was not available for planning: AC-held$')]
SUBMISSION_ISSUES = [('duplicate', ['input overflow resolutions must name distinct actions']),
                     ('profile', ['input overflow profile was not offered for this action: AC-held']),
                     ('unknown', ['input overflow action was not available for planning: AC-unknown'])]


if __name__ == '__main__':
    unittest.main()
