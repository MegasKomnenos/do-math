"""The engine's identity review mixin (``review_engine``, layer 2): stages the engine drives to a published assessment.

Every test runs the product's ``ResearchEngine`` over the stored review state
of ``support.review_scene`` and answers the pending review actions with the
scene's reviewer (``ReviewScene.execute``), which admits each attempt and
applies its answer as the owner does.
"""
from copy import deepcopy
import json
import tempfile
import unittest

from do_math import governance, knowledge, knowledge_records as kr
from do_math.canonical import exact_content_hash
from support.state_builders import charter
from support.review_scene import ReviewScene, warm


def setUpModule():
    warm()
    warm(rounds=1)


class ReviewSceneCase(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.scene = ReviewScene(temporary.name)
        self.engine = self.scene.engine

    def open_dispute(self, scene=None):
        """A review of ``K1`` whose first initial slot found ``f``; the organizer made ``issue-0``, three judges remain."""
        scene = scene or self.scene
        cycle_id = scene.start('K1')
        scene.execute(dict(decision='mismatch', findings=[dict(id='f', statement='The domain is wrong', evidence=['proposal:1'])]))
        scene.execute()
        self.assertEqual(scene.pending()['stage'], 'organize')
        scene.execute()
        return cycle_id


class ScopeStageTests(ReviewSceneCase):
    def test_v5_scope_execution_selects_initial_slots_before_the_initial_phase(self):
        engine, scene = self.engine, self.scene
        cycle_id = engine._start_identity_review('K1')
        self.assertEqual(scene.pending()['stage'], 'scope')
        scene.execute()
        cycle = engine.runtime['review_cycles'][cycle_id]
        self.assertEqual(cycle['phase'], 'initial')
        self.assertEqual(cycle['review_input_basis']['values']['scope_assessment']['assessment_id'], 'generated-scope')
        self.assertEqual({action['slot'] for action in engine.runtime['queue'] if action['role'] == 'identity_review'},
                         {'initial-0', 'initial-1'})

    def test_scope_admission_propagates_actual_activity_and_selected_profile_to_initial_actions(self):
        engine, scene = self.engine, self.scene
        cid = engine._start_identity_review('K1')
        scene.pending()['owner_activity_id'] = 'AY-actual'
        selected = {'id': 'EP-fixed', 'revision': 2, 'sha256': 'b' * 64}
        policy = engine.runtime['review_cycles'][cid]['review_policy']
        scope = {'assessment_id': 'scope-picked', 'policy_id': policy['id'],
            'required_perspectives': [], 'initial_slots': [
                {'id': 'initial-0', 'perspective': 'formal', 'required_source_refs': ['proposal']},
                {'id': 'initial-1', 'perspective': 'semantic', 'required_source_refs': ['proposal']}],
            'selected_profile_ref': selected, 'activity_execution_limit': 24, 'overflow_disposition': 'unresolved'}
        scene.execute({'scope_assessment': scope})
        self.assertEqual(engine.runtime['review_cycles'][cid]['owner_activity_id'], 'AY-actual')
        reviews = [action for action in engine.runtime['queue'] if action['role'] == 'identity_review']
        self.assertEqual({action['slot'] for action in reviews}, {'initial-0', 'initial-1'})
        for action in reviews:
            self.assertEqual(action['owner_activity_id'], 'AY-actual')
            self.assertEqual(action['profile_ref'], selected)


class InitialStageTests(ReviewSceneCase):
    def test_initial_match_activates_only_after_all_slots(self):
        engine, scene = self.engine, self.scene
        cycle_id = scene.start('K1')
        self.assertFalse(scene.usable())
        self.assertEqual(len(engine.runtime['queue']), 2)
        self.assertEqual(engine._start_identity_review('K1'), cycle_id)
        self.assertEqual(len(engine.runtime['queue']), 2)
        schema = engine._review_schema(scene.pending())
        self.assertEqual(schema['properties']['proposal_digest']['enum'], [engine.runtime['review_cycles'][cycle_id]['proposal_digest']])
        scene.execute()
        self.assertEqual(engine.instance['identity_assessments'], {})
        context, _, _ = scene.execute()
        self.assertEqual(context['completed_results'], {})
        item = engine.instance['knowledge']['K1']
        self.assertTrue(scene.usable())
        self.assertEqual(scene.assessment()['decision'], 'match')
        self.assertEqual(len(scene.assessment()['execution_ids']), 2)
        self.assertNotIn('identity_assessment', item)
        self.assertEqual(engine.runtime['queue'][0]['role'], 'research_plan')
        self.assertEqual(json.loads(json.dumps(engine.runtime)), engine.runtime)

    def test_actual_profile_and_restored_input_remain_bound_to_the_logical_slot(self):
        engine, scene = self.engine, self.scene
        scene.start('K1')
        scene.profile = {'id': 'EP-review', 'revision': 1, 'sha256': 'a' * 64}
        scene.execute()
        scene.execute()
        cid = engine.instance['knowledge']['K1']['review_cycle_id']
        cycle = engine.runtime['review_cycles'][cid]
        self.assertEqual(cycle['slot_profiles']['initial-0'], scene.profile)
        self.assertEqual(cycle['input_bindings']['ex-1']['profile_ref'], scene.profile)
        kid = scene.revise()
        next_id = scene.start(kid, previous_cycle_id=cid)
        context, _, eid = scene.execute()
        bound = engine.runtime['review_cycles'][next_id]['input_bindings'][eid]
        self.assertEqual(bound['restored_messages'], context['self_messages'])
        self.assertTrue(bound['restored_messages'])
        scene.profile = {'id': 'EP-other', 'revision': 1, 'sha256': 'b' * 64}
        with self.assertRaisesRegex(ValueError, 'logical review slot profile changed'):
            scene.execute()

    def test_new_revision_restarts_all_slots_and_retains_own_conversation(self):
        engine, scene = self.engine, self.scene
        first_id = scene.start('K1')
        scene.execute()
        scene.execute()
        first = deepcopy(engine.runtime['review_cycles'][first_id])
        previous_assessment = deepcopy(scene.assessment())
        kid = scene.revise()
        second_id = scene.start(kid, previous_cycle_id=first_id)
        second = engine.runtime['review_cycles'][second_id]
        self.assertEqual(second['input_bindings'], {})
        self.assertEqual(engine.runtime['review_cycles'][first_id]['input_bindings'], first['input_bindings'])
        self.assertNotEqual(second['revision'], first['revision'])
        self.assertEqual(second['reviewer_slots'], first['reviewer_slots'])
        self.assertEqual(second['turns'], first['turns'])
        self.assertFalse(scene.usable(kid))
        context, _, _ = scene.execute()
        self.assertTrue(context['self_messages'])
        self.assertTrue(context['source_refs'])
        import hashlib
        from pathlib import Path
        from do_math.values import compact_json_bytes
        restored_proposals = []
        for reference in context['source_refs']:
            original = first['turns'][reference['slot']][reference['index']]
            raw = (scene.root / 'ex-3' / 'workspace' / reference['local_path']).read_bytes()
            self.assertEqual(raw, compact_json_bytes(original))
            self.assertEqual(hashlib.sha256(raw).hexdigest(), reference['sha256'])
            self.assertEqual(len(raw), reference['bytes'])
            self.assertEqual(reference['proposal_digest'], first['proposal_digest'])
            if reference['kind'] == 'proposal':
                restored_proposals.append(json.loads(raw)['content'])
        self.assertEqual(restored_proposals, [first['proposal']])
        self.assertEqual(context['proposal'], second['proposal'])
        self.assertNotEqual(context['proposal'], first['proposal'])
        scene.execute()
        self.assertEqual(scene.assessment(kid)['review_cycle_id'], second_id)
        self.assertTrue(scene.usable(kid))
        self.assertEqual(scene.assessment('K1'), previous_assessment)


class DisputeTests(ReviewSceneCase):
    def test_complete_rejected_objection_round_trip(self):
        """About 0.35 s, over the 0.2 s unit budget: eleven slots answer through two dispute rounds."""
        engine, scene = self.engine, self.scene
        cycle_id = self.open_dispute()
        for _ in range(3): scene.execute()
        self.assertEqual((scene.pending()['stage'], scene.pending()['slot']), ('answer', 'initial-0'))
        context, _, _ = scene.execute(record_first=True)
        self.assertEqual(len([r for r in context['completed_results'].values() if r['stage'] == 'judge']), 3)
        self.assertEqual(scene.pending()['round'], 2)
        for _ in range(3): scene.execute()
        self.assertTrue(scene.usable())
        self.assertEqual(scene.assessment()['review_cycle_id'], cycle_id)
        self.assertEqual(len(scene.assessment()['execution_ids']), 3)
        self.assertEqual(scene.assessment()['basis'], kr.identity_basis(engine.instance, 'K1'))

    def test_mismatch_and_round_limit_return_precise_followup(self):
        """About 0.55 s, over the 0.2 s unit budget: two disputes of six slots each run on two scenes."""
        scene = self.scene
        cycle_id = self.open_dispute()
        for _ in range(3):
            scene.execute(dict(decision='mismatch', issue_verdicts=[dict(issue_id='issue-0', decision='approved', reason='Actual mismatch in the domain', evidence=['proposal:1'])]))
        self.assertEqual(scene.assessment()['decision'], 'mismatch')
        self.assertFalse(scene.usable())
        plan = next(a for a in scene.engine.runtime['queue'] if a['role'] == 'research_plan')
        self.assertEqual(plan['identity_review']['cycle_id'], cycle_id)
        self.assertIn('issue-0', plan['identity_review']['issues'])
        self.assertTrue(plan['identity_review']['actual_scope'])
        self.assertFalse(plan['identity_review']['effective'])
        limited = ReviewScene(scene.root / 'one-round', rounds=1)
        self.open_dispute(limited)
        for _ in range(3):
            limited.execute(dict(decision='unresolved', issue_verdicts=[dict(issue_id='issue-0', decision='unresolved', reason='Source is ambiguous', evidence=[])]))
        self.assertEqual(limited.assessment()['decision'], 'unresolved')
        plan = next(a for a in limited.engine.runtime['queue'] if a['role'] == 'research_plan')
        self.assertTrue(plan['identity_review']['remaining_questions'])

    def test_new_judge_finding_is_assigned_answered_and_fully_judged(self):
        """About 0.5 s, over the 0.2 s unit budget: twelve slots answer through two dispute rounds."""
        scene = self.scene
        self.open_dispute()
        scene.execute(dict(decision='mismatch', new_findings=[dict(id='new-source', statement='New source inconsistency', evidence=['proposal:3'])]))
        scene.execute()
        scene.execute()
        self.assertEqual(scene.pending()['stage'], 'organize')
        context, _, _ = scene.execute()
        self.assertEqual(context['pending_findings'][0]['ref']['slot'], 'judge-0')
        self.assertEqual(scene.pending()['stage'], 'answer')
        context, _, _ = scene.execute()
        self.assertEqual(set(context['answer_requests']), {'issue-0', 'issue-1'})
        for _ in range(3): scene.execute()
        self.assertTrue(scene.usable())

    def test_scope_to_answer_and_judgment_publishes_the_same_links_consumed_by_goal_audit(self):
        """A review from its scope stage to a second-round judgment publishes the link the goal audit consumes.

        The goal audit is the same real engine's receiver: its governance input is
        bound (``_bind_governance_input``) and its satisfied judgment applied
        (``_apply``) as the owner does after a goal audit call; nothing is replaced.
        About 0.7 s, over the 0.2 s unit budget: twelve slots answer and the goal audit's governance input is rendered.
        """
        engine, scene = self.engine, self.scene
        cid = engine._start_identity_review('K1')
        scene.execute()  # actual scope consumer, followed by a disputed initial batch
        scene.execute({'decision': 'mismatch', 'findings': [
            {'id': 'f', 'statement': 'Check the domain', 'evidence': ['proposal']}]})
        scene.execute()
        scene.execute()  # organization
        for _ in range(3): scene.execute()
        scene.execute()  # original slot withdraws its objection
        for _ in range(3): scene.execute()
        assessment = scene.assessment()
        link = kr.usable_links(engine.instance, 'K1')[0]
        self.assertEqual(link['assessment_id'], assessment['id'])
        self.assertEqual(kr.knowledge_view(engine.instance)[0]['links'], [link])
        self.assertTrue(knowledge.assess_use(engine.instance['knowledge']['K1'], engine.instance)['valid'])
        self.assertEqual(assessment['policy_ref'], engine.runtime['review_cycles'][cid]['policy_ref'])
        engine.instance['goal_judgments'] = []
        engine.runtime['tasks'] = {}
        record = charter('CH-goal-fixture', 'Prove the fixture')
        # The stored state has a lifecycle, so the first charter's source is its immutable input.
        source = governance.preserve_source('US-goal-fixture', engine.instance['lifecycle']['immutable_input']['text'], origin='user')
        engine.instance = governance.initialize_governance(engine.instance, source,
            {'id': 'DC-goal-fixture', 'actor': 'user', 'source_ref': source['id'],
             'source_sha256': source['sha256'], 'record_hashes': {record['id']: exact_content_hash(record)}}, [record])
        assessment = engine.instance['identity_assessments'][link['assessment_id']]
        engine.runtime['inputs'] = []
        engine.instance['config']['goal_auditors'] = 2
        goal_basis = engine._goal_basis_key()
        engine.runtime['executions']['AUDIT'] = {'id': 'AUDIT', 'role': 'goal_audit', 'source_basis': []}
        engine._bind_governance_input({'role': 'goal_audit'}, engine.runtime['executions']['AUDIT'],
                                      engine._governance_context({'role': 'goal_audit'}, {}))
        engine._apply({'role': 'goal_audit', 'basis': goal_basis, 'slot': 0, 'required': 2},
            {'decision': 'satisfied', 'scope_complete': True, 'used_sources': ['K1'], 'questions': [],
             'summary': 'The reviewed links support the charter goal', 'findings': [], 'additional_audits': []}, 'AUDIT')
        judgment = engine.instance['goal_judgments'][0]
        self.assertEqual(judgment['formal_result_refs'], [link['formal_result_id']])
        self.assertEqual(judgment['record_basis'], knowledge.capture_basis(engine.instance, engine.runtime, ['K1']))
        self.assertIs(engine.instance['identity_assessments'][link['assessment_id']], assessment)
        engine.instance = kr.set_assessment_use(engine.instance, assessment['id'], 'suspended', 'New source dispute', 'operator')
        self.assertNotEqual(engine._goal_basis_key(), goal_basis)
        self.assertFalse(knowledge.assess_use(engine.instance['knowledge']['K1'], engine.instance)['valid'])


if __name__ == '__main__':
    unittest.main()
