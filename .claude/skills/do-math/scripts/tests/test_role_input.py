"""Role inputs: what the context producer packages for each role, and the checks at that boundary.

Model answers are fixtures. The context producer, input manifests, restored
sources and submission checks are the product's.

Stage 1f moved the other tests of this module to unit.test_role_input_scoped_packaging,
sim.test_role_input_context and boundary.test_role_input_snapshot_reach. These
remain: three compare a plan's input snapshot, which only a store double holds
for their synthetic states, and one needs a review seat deferred for research.
"""
import hashlib
import json
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math import knowledge_records, submission
from do_math.canonical import canonical_json
from do_math.context_store import prepare_role_input
from engine_fixtures import context_engine, package
from record_fixtures import approve_task, approved_task, surface_state, task_disposition
from research_fixtures import governance_start, seal_response
from review_fixtures import defer_review_for_research, ReviewFakeEngine
from runner_fixtures import common


class InputConnections(unittest.TestCase):
    def test_fixed_question_is_packaged_and_answer_returns_to_its_seat(self):
        engine = ReviewFakeEngine(self.enterContext(tempfile.TemporaryDirectory()))
        cid = defer_review_for_research(engine)
        action = next(a for a in engine.runtime['queue'] if a['role'] == 'supplemental_research')
        root = engine.root / 'packaged-investigation'
        context = {'action': deepcopy(action), **engine._review_research_context(action, root)}
        instance, _ = surface_state()
        # The fake engine starts from governance_start's families; the adopted charter
        # comes from surface_state, so each family keeps the records of both.
        instance.update({**engine.instance, **{family: {**instance[family], **engine.instance[family]}
                                                for family in governance_start()}})
        profile = next(p for p in instance['execution_profiles'].values() if p['role'] == 'supplemental_research')
        from do_math.contracts import with_integration_schema
        fitted = prepare_role_input(context, instance=instance, runtime=engine.runtime,
            role='supplemental_research', profile=profile, snapshot='a'*40,
            workspace=root, activity_id=action['owner_activity_id'], install_submission_tools=True,
            output_schema=with_integration_schema(engine._review_research_schema(action)))
        self.assertIsNone(fitted['overflow'])
        self.assertIsNone(fitted['manifest']['private_scope'])
        self.assertIn('review_research', fitted['manifest']['required_direct_keys'])
        self.assertNotIn('task', fitted['manifest']['required_direct_keys'])
        self.assertNotIn('role_review', fitted['context'])
        self.assertEqual(fitted['context']['review_research']['id'], action['research_request_id'])
        self.assertEqual(engine.runtime['review_cycles'][cid]['research'][action['research_request_id']]['status'], 'pending')
        engine.execute({'summary': 'PRIVATE-INITIAL-PEER'})
        research = fitted['context']['review_research']
        execution = {'id': 'INV-answer', 'role': 'supplemental_research', 'status': 'running', 'action': action,
            'execution_profile_ref': deepcopy(engine.research_profile), 'actor_kind': 'ai',
            'owner_activity_id': action['owner_activity_id']}
        self.assertEqual(engine._admit_review_execution(action, execution)['disposition'], 'admitted')
        engine.runtime['executions']['INV-answer'] = execution
        engine._apply_review_research(action, {'summary': 'Fixed source comparison',
            'used_sources': [research['sources'][0]['ref']], 'questions': [], 'research_request_id': research['id'],
            'request_digest': research['request_digest'], 'outcome': 'answered', 'answer': 'The map is complete.',
            'scope_complete': True, 'evidence_refs': [research['sources'][0]['ref']]}, 'INV-answer')
        execution.update(status='ended', outcome='output_accepted')
        resumed, _, _ = engine.execute()
        self.assertTrue(resumed['supplemental_results'])
        self.assertNotIn('PRIVATE-INITIAL-PEER', json.dumps(resumed))
        self.assertEqual(engine.assessment()['review_cycle_id'], cid)


class RoleInputBoundaryTests(unittest.TestCase):
    def artifact_engine(self):
        task, instance, runtime = approved_task()
        raw = b'valid evidence\n'
        instance['sources'][0]['sha256'] = hashlib.sha256(raw).hexdigest()
        task['occurrence_condition'] = {'op': 'artifact_valid', 'artifact_ref': {
            'snapshot': 'a' * 40, 'path': 'runtime/artifacts/BA-evidence/proof.txt',
            'sha256': hashlib.sha256(raw).hexdigest()}}
        approve_task(task, instance, runtime)
        engine = context_engine(instance, runtime)
        engine.store.read.return_value = raw
        return engine, task

    def test_artifact_candidate_survives_packaging_and_population_stays_fixed(self):
        engine, task = self.artifact_engine()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fitted, fixed = package(engine, root)
            self.assertEqual(fixed['ready_task_ids'], [task['id']])
            self.assertEqual(fixed['observed_at'], fixed['submission_contract']['basis_time'])
            self.assertEqual(fitted['manifest']['candidate_order']['ids'], [task['id']])
            output = {**common('research_plan'), 'dispositions': [task_disposition(task['id'])]}
            (root / 'activity-extensions.json').write_bytes(canonical_json({'model_assessments': [{
                'task_id': task['id'], 'difficulty': 'low', 'importance': 'low',
                'reason': 'The selected fixture task has bounded evidence and scope.'}]}))
            seal_response(output, fixed, root)
            draft = root / 'draft.json'; draft.write_bytes(canonical_json(output))
            check = submission.producer_check(root, draft)
            self.assertTrue(check['passed'], check['issues'])
            original = deepcopy(engine.runtime)
            engine.store.load.return_value = (engine.head, deepcopy(engine.instance), original)
            engine.store.view.return_value = engine.store.load.return_value
            frozen = canonical_json(fixed)
            evidence = engine.store.read.return_value
            engine.store.read.side_effect = lambda path, head: (
                frozen if path.endswith('/context.json') else evidence)
            engine.runtime['executions']['EX-plan'] = {'id': 'EX-plan', 'role': 'research_plan', 'status': 'ended',
                'action': fixed['action'], 'input_snapshot': engine.head, 'input_bundle': 'BA-plan'}
            extra = deepcopy(task); extra['id'] = 'TK-later'; engine.runtime['tasks'][extra['id']] = extra
            engine.instance['grants']['GR-later'] = {**deepcopy(engine.instance['grants']['GR-1']),
                                                     'id': 'GR-later', 'task_ids': [extra['id']]}
            extra['authority_refs'] = ['GR-later']
            approve_task(extra, engine.instance, engine.runtime)
            engine._apply_plan(output, 'EX-plan')
            self.assertEqual([a['target'] for a in engine.runtime['queue']], [task['id']])

    def test_selected_candidate_still_requires_current_authority(self):
        engine, task = self.artifact_engine()
        with tempfile.TemporaryDirectory() as directory:
            _, fixed = package(engine, Path(directory))
            output = {**common('research_plan'), 'dispositions': [task_disposition(task['id'])]}
            engine.store.load.return_value = (engine.head, deepcopy(engine.instance), deepcopy(engine.runtime))
            engine.instance['grants']['GR-1']['status'] = 'revoked'
            execution = {'input_snapshot': engine.head, 'extensions': {}, 'goal_revision': 1, 'policy_revision': 1}
            with self.assertRaisesRegex(ValueError, 'changed|current'):
                engine._validate_decision_acceptance(fixed['action'], output, execution, fixed,
                                                     evaluation_context=engine._evaluation_context())

    def test_delivered_identity_receipt_can_complete_only_its_current_task(self):
        from record_fixtures import specialist_assessment
        for mutation in (None, 'foreign', 'withdrawn'):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as directory:
                state, runtime, assessment, kid, aid = specialist_assessment()
                # These source bytes are irrelevant to this specialist obligation.
                state['sources'] = []
                engine = context_engine(state, runtime)
                root = Path(directory)
                _, fixed = package(engine, root)
                output = {**common('research_plan'), 'task_assessments': [assessment]}
                seal_response(output, fixed, root)
                draft = root / 'draft.json'; draft.write_bytes(canonical_json(output))
                check = submission.producer_check(root, draft)
                self.assertTrue(check['passed'], check['issues'])
                engine.store.load.return_value = (engine.head, deepcopy(engine.instance), deepcopy(engine.runtime))
                engine.store.view.return_value = engine.store.load.return_value
                engine.store.read.side_effect = lambda path, head: canonical_json(fixed)
                engine.runtime['executions']['EX-plan'].update(input_snapshot=engine.head, input_bundle='BA-plan')
                if mutation == 'foreign':
                    engine.instance['knowledge'][kid]['task_id'] = 'TK-other'
                elif mutation == 'withdrawn':
                    engine.instance = knowledge_records.set_assessment_use(engine.instance, aid, 'withdrawn', 'recheck', 'reviewer')
                if mutation:
                    with self.assertRaises(ValueError):
                        engine._apply_plan(output, 'EX-plan')
                else:
                    engine._apply_plan(output, 'EX-plan')
                    self.assertEqual(engine.runtime['tasks']['TK-1']['status'], 'completed')


if __name__ == "__main__":
    unittest.main()
