"""Fixed-question review investigations: the pure cycle (``review_cycle``, layer 1) and the engine's review mixin (layer 2).

A reviewer's fixed questions defer its slot; each investigation answers from
fixed sources only, and the answers return to the same slot. The pure tests
run ``review_cycle`` on ``review_fixtures.deferred_research_cycle``; the
engine tests run the product's ``ResearchEngine`` over the stored review state
of ``support.review_scene`` and call the mixin as the owner does, from a
review deferred by ``support.review_research.defer_review_for_research``.
Moved from ``test_review_research`` (``PureResearchTests``,
``SplitReviewResearchTests``), whose engine tests ran on
``review_fixtures.ReviewFakeEngine`` (no repository, ``_save`` an autospec
double, a store that read no artifact). The owner's path through the same
mixin (investigation input, answer, resumption, stop) runs on a Sim in
``flows.test_review_research_flows``.
"""
from copy import deepcopy
import hashlib
import json
import tempfile
import unittest

from do_math import knowledge_records as kr, submission
from do_math.review_cycle import accept_research_result, accept_result, context_for, next_actions, validate_sealed_review
from review_fixtures import deferred_research_cycle, research_answer
from support.review_research import defer_review_for_research, research_profile
from support.review_scene import ReviewScene, warm


def setUpModule():
    warm()


class PureResearchTests(unittest.TestCase):
    def test_completed_investigation_is_private_until_its_requester_seals(self):
        cycle, action = deferred_research_cycle()
        self.assertNotIn(action, next_actions(cycle))
        request_id = next(iter(cycle['research']))
        cycle = accept_research_result(cycle, request_id, research_answer(cycle), 'investigator')
        peer = next(a for a in next_actions(cycle) if a['slot'] != action['slot'])
        self.assertEqual(context_for(cycle, peer)['supplemental_results'], [])
        self.assertEqual(len(context_for(cycle, action)['supplemental_results']), 1)
        self.assertEqual(cycle['results'], {})

    def test_wrong_question_and_partial_answer_are_not_accepted(self):
        cycle, _ = deferred_research_cycle()
        request_id = next(iter(cycle['research']))
        other_question = '^investigation result belongs to a different fixed question$'
        partial = '^answered investigation requires complete scope, exact evidence and no unresolved question$'
        for field, value, reason in [('request_digest', 'wrong', other_question), ('research_request_id', 'wrong', other_question),
                                     ('scope_complete', False, partial), ('evidence_refs', [], partial)]:
            output = research_answer(cycle); output[field] = value
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, reason):
                accept_research_result(cycle, request_id, output, 'investigator')
        self.assertIn('initial:1:initial-0', cycle['deferred_actions'])

    def test_deferred_initial_slot_does_not_allow_peer_to_finish_the_cycle(self):
        cycle, deferred = deferred_research_cycle()
        peer = next_actions(cycle)[0]
        output = {'proposal_digest': cycle['proposal_digest'], 'summary': 'All current material matched',
                  'used_sources': [], 'questions': [], 'decision': 'match', 'scope_complete': True, 'findings': []}
        cycle = accept_result(cycle, peer, output, 'peer')
        self.assertEqual(cycle['status'], 'working')
        self.assertEqual(cycle['sealed'], [])
        self.assertEqual(next_actions(cycle), [])


class SceneResearchTests(unittest.TestCase):
    """The engine's review mixin over the stored review state (``support.review_scene``)."""

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.scene = ReviewScene(temporary.name)
        self.engine = self.scene.engine

    def test_producer_and_receiver_reject_an_unassigned_used_source(self):
        engine = self.engine
        defer_review_for_research(self.scene)
        action = next(a for a in engine.runtime['queue'] if a['role'] == 'supplemental_research')
        workspace = self.scene.root / 'source-check'
        context = engine._review_research_context(action, workspace)
        context.update(action=action, knowledge_catalog=[{'id': 'KN-unassigned'}])
        research = context['review_research']
        output = {'summary': 'Compare fixed evidence', 'used_sources': ['KN-unassigned'], 'questions': [],
            'research_request_id': research['id'], 'request_digest': research['request_digest'],
            'outcome': 'answered', 'answer': 'The declared evidence is complete', 'scope_complete': True,
            'evidence_refs': [research['sources'][0]['ref']]}
        schema = engine._review_research_schema(action)
        # The same answer citing only its fixed source passes: the receiver's
        # schema binds the request identity without constraining other fields.
        assigned = {**output, 'used_sources': [research['sources'][0]['ref']]}
        self.assertEqual(submission._payload_issues(assigned, schema, context, {}, workspace), [])
        issues = submission._payload_issues(output, schema, context, {}, workspace)
        self.assertTrue(any(row['path'] == 'output/used_sources/0' and 'fixed source set' in row['message']
                            for row in issues), issues)
        execution = {'id': 'INV-unassigned', 'role': 'supplemental_research', 'action': action,
            'actor_kind': 'ai', 'owner_activity_id': action['owner_activity_id'],
            'execution_profile_ref': research_profile(engine)}
        self.assertEqual(engine._admit_review_execution(action, execution)['disposition'], 'admitted')
        engine.runtime['executions'][execution['id']] = execution
        with self.assertRaisesRegex(ValueError, 'fixed source set'):
            engine._apply_review_research(action, output, execution['id'])

    def test_session_mode_does_not_let_optional_research_spend_reserved_followup(self):
        self.engine.instance['review_policy']['activity_execution_limit'] = 13
        cid = defer_review_for_research(self.scene)
        self.assertFalse(any(a['role'] == 'supplemental_research' for a in self.engine.runtime['queue']))
        self.assertEqual(self.engine.runtime['review_cycles'][cid]['decision'], 'unresolved')

    def test_split_scope_fixed_research_and_resumed_review_publish_exact_assessment(self):
        engine, scene = self.engine, self.scene
        cid = defer_review_for_research(scene)
        scene.execute({'summary': 'PRIVATE-INITIAL-PEER'})
        action = next(a for a in engine.runtime['queue'] if a['role'] == 'supplemental_research')
        context = engine._review_research_context(action, scene.root / 'investigation')
        self.assertNotIn('PRIVATE-INITIAL-PEER', json.dumps(context))
        self.assertEqual(context['proposal']['lean_code'], kr.proposal_view(engine.instance, 'K1')['lean_code'])
        research = context['review_research']
        for source in research['sources']:
            self.assertEqual(hashlib.sha256((scene.root / 'investigation' / source['local_path']).read_bytes()).hexdigest(), source['sha256'])
        execution = {'id': 'INV-answer', 'role': 'supplemental_research', 'status': 'running', 'action': action,
                     'execution_profile_ref': research_profile(engine),
                     'actor_kind': 'ai', 'owner_activity_id': action['owner_activity_id']}
        self.assertEqual(engine._admit_review_execution(action, execution)['disposition'], 'admitted')
        engine.runtime['executions']['INV-answer'] = execution
        engine._apply_review_research(action, {'summary': 'Exact dependency map checked',
            'used_sources': [research['sources'][0]['ref']], 'questions': [], 'research_request_id': research['id'],
            'request_digest': research['request_digest'], 'outcome': 'answered', 'answer': 'The sealed map is complete.',
            'scope_complete': True, 'evidence_refs': [research['sources'][0]['ref']]}, 'INV-answer')
        engine.runtime['executions']['INV-answer'].update(status='ended', outcome='output_accepted')
        context, _, _ = scene.execute()
        self.assertTrue(context['supplemental_results'])
        self.assertNotIn('PRIVATE-INITIAL-PEER', json.dumps(context))
        self.assertEqual(scene.assessment()['review_cycle_id'], cid)
        self.assertEqual(scene.assessment()['basis'], kr.identity_basis(engine.instance, 'K1'))
        self.assertTrue(scene.usable())
        self.assertIn('INV-answer', engine.runtime['review_cycles'][cid]['execution_accounting']['executions_used'])
        self.assertEqual(validate_sealed_review(engine.runtime['review_cycles'][cid], engine.runtime,
            instance=engine.instance)['decision'], 'match')

    def test_unadmitted_supplemental_execution_is_not_counted_late_at_acceptance(self):
        engine = self.engine
        defer_review_for_research(self.scene)
        action = next(a for a in engine.runtime['queue'] if a['role'] == 'supplemental_research')
        engine.runtime['executions']['UNADMITTED'] = {'id': 'UNADMITTED', 'role': 'supplemental_research', 'action': action}
        with self.assertRaisesRegex(ValueError, 'admitted before execution'):
            engine._apply_review_research(action, {}, 'UNADMITTED')

    def test_corrupt_fixed_research_source_is_a_local_diagnostic_on_slot_resume(self):
        engine, scene = self.engine, self.scene
        cid = defer_review_for_research(scene)
        investigation = next(a for a in engine.runtime['queue'] if a['role'] == 'supplemental_research')
        engine._abandon_review_research(investigation, 'INV-failed', 'failed before producing an answer')
        cycle = engine.runtime['review_cycles'][cid]
        request = cycle['research'][investigation['research_request_id']]
        source = request['source_records'][0]
        expected = source['sha256']
        source['inline'] = 'Changed after sealing'
        action = next(a for a in engine.runtime['queue'] if a['role'] == 'identity_review' and a['slot'] == request['action']['slot'])
        outcome = engine._prepare_review_context(action, scene.root / 'corrupt-fixed-source')
        event = outcome['recovery']['recovery_event']
        self.assertEqual(event['cause_kind'], 'fixed_source_content_mismatch')
        self.assertEqual(event['coordinate']['source_ref'], source['ref'])
        self.assertEqual(event['coordinate']['slot'], action['slot'])
        self.assertEqual(event['expected_sha256'], expected)
        self.assertNotEqual(event['observed_sha256'], expected)
        self.assertFalse(event['retryable'])

    def test_split_stopped_investigation_returns_to_its_original_slot(self):
        engine = self.engine
        cid = defer_review_for_research(self.scene)
        action = next(a for a in engine.runtime['queue'] if a['role'] == 'supplemental_research')
        execution = {'id': 'INV-stopped', 'role': 'supplemental_research', 'status': 'running', 'action': action,
                     'actor_kind': 'ai', 'owner_activity_id': action['owner_activity_id']}
        self.assertEqual(engine._admit_review_execution(action, execution)['disposition'], 'admitted')
        engine.runtime['executions']['INV-stopped'] = execution
        self.assertTrue(engine._abandon_review_research(action, 'INV-stopped', 'operator stopped this run'))
        cycle = engine.runtime['review_cycles'][cid]
        self.assertEqual(cycle['status'], 'working')
        request = cycle['research'][action['research_request_id']]
        self.assertEqual(request['result']['execution_status'], 'incomplete')
        self.assertIn(request['action'], next_actions(cycle))
        self.assertEqual(engine.instance['identity_assessments'], {})
        self.assertIn('INV-stopped', cycle['execution_accounting']['executions_used'])


if __name__ == '__main__':
    unittest.main()
