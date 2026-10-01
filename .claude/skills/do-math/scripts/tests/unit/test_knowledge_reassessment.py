"""Reassessment of a published identity assessment (``knowledge`` and the engine's review mixin, layer 2).

A qualified defect in the review that produced an assessment suspends its use
and opens an independent review of the same assessment; the sealed outcome
restores, keeps suspended or withdraws that use without ever writing a new
identity assessment.

Two starts:

- The engine's reassessment mixin runs on ``support.review_scene.ReviewScene``:
  the product's ``ResearchEngine`` loaded from a validated stored state with the
  candidate theorem ``K1`` and the fixture review policy; the scene answers each
  review action as a reviewer and applies the answer through the mixin
  (``_admit_review_execution``, ``_apply_identity_review``), and every save
  publishes through the storage contract. ``ReassessmentCase`` first runs
  ``K1``'s original review to a match.
- The domain functions (``knowledge.suspend_assessment_use``,
  ``apply_assessment_reassessment``) run over
  ``support.knowledge_roundtrip.KnowledgeRoundtripHarness``: synthetic sealed
  reviews through the pure review cycle and round trips through the real
  ``ResearchRepository`` on the Git port's fake.

The owner-run path of a public reassessment report is
``flows.test_review_reassessment``; its central control is
``unit.test_review_reassessment``.
"""
import copy
import tempfile
import unittest

from do_math import activities, execution_lifecycle, knowledge, knowledge_records as kr
from do_math.canonical import exact_content_hash
from do_math.configuration import DEFAULT_CONFIG
from do_math.execution_profiles import profile_ref
from do_math.review_cycle import accept_result, next_actions, start_review, validate_sealed_review
from support.review_inputs import grant_replacement, review_stage_output, scoped_start
from support.knowledge_roundtrip import KnowledgeRoundtripHarness
from support.review_scene import ReviewScene, warm


def setUpModule():
    warm()
    warm(rounds=1)


class ReassessmentCase(unittest.TestCase):
    """``K1``'s original review run to a match on a review scene, ready for a reassessment of its assessment.

    ``request(evidence)`` is the reassessment request for that assessment;
    ``defect()`` records that one initial reviewer inherited the author's
    context and returns that evidence; ``use()`` is the assessment's use record;
    ``complete(decision='match')`` answers every queued review action toward
    ``decision``.
    """
    rounds = 2

    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.directory = directory.name
        self.open_scene(self.rounds)
        self.original = self.engine._start_identity_review('K1')
        while any(a['role'] == 'identity_review' for a in self.engine.runtime['queue']):
            self.scene.execute()
        self.assessment = self.scene.assessment()

    def open_scene(self, rounds):
        self.scene = ReviewScene(self.directory, rounds=rounds)
        self.engine = self.scene.engine

    def request(self, evidence):
        return {'assessment_id': self.assessment['id'], 'assessment_sha256': exact_content_hash(self.assessment),
                'evidence': evidence}

    def defect(self):
        cycle = self.engine.runtime['review_cycles'][self.original]
        execution_id = cycle['results']['initial:1:initial-0']['execution_id']
        self.engine.runtime['executions'][execution_id]['context_origin'] = ['author']
        self.engine.runtime['executions']['author'] = {'id': 'author', 'status': 'ended'}
        return {'kind': 'author_context', 'execution_id': execution_id}

    def use(self):
        return next(row for row in self.engine.instance['assessment_uses'].values()
                    if row['assessment_id'] == self.assessment['id'])

    def complete(self, decision='match'):
        while any(a['role'] == 'identity_review' for a in self.engine.runtime['queue']):
            action = self.scene.pending()
            cycle = self.engine.runtime['review_cycles'][action['review_cycle_id']]
            changes = {}
            if action['stage'] == 'initial' and decision == 'unresolved':
                changes = {'decision': 'unresolved', 'scope_complete': False}
            elif action['stage'] == 'initial' and action['slot'] == 'initial-0' and decision == 'mismatch':
                changes = {'decision': 'mismatch', 'findings': [{'id': 'defect', 'statement': 'The stated domain differs', 'evidence': ['proposal']}]}
            elif action['stage'] == 'judge' and decision == 'mismatch':
                changes = {'decision': 'mismatch', 'issue_verdicts': [dict(issue_id=i, decision='approved', reason='Exact mismatch confirmed', evidence=['proposal']) for i in cycle['issues']]}
            self.scene.execute(changes)


class ReassessmentPublicationTests(ReassessmentCase):
    def test_authorized_replacement_replays_through_domain_publication(self):
        """About 0.55 s, over the 0.2 s unit budget: the review scene publishes every review step through the storage contract."""
        self.assert_reassessment_publishes(replacement=True)

    def test_reaffirmed_noncurrent_judgment_is_recorded_without_restoring_use(self):
        """About 0.35 s, over the 0.2 s unit budget: the review scene publishes every review step through the storage contract."""
        self.assert_reassessment_publishes(replacement=False)

    def assert_reassessment_publishes(self, *, replacement):
        """A reaffirming reassessment records its cycle on the use; ``replacement`` replays one lost attempt by grant."""
        engine = self.engine
        original = copy.deepcopy(engine.instance['identity_assessments'])
        if replacement:
            grant_replacement(engine)
        else:
            engine.instance['knowledge']['K1']['kind_use_suspended'] = True
        opened = engine._start_assessment_reassessment(**self.request(self.defect()))
        if replacement:
            self.scene.execute()
            action = self.scene.pending()
            engine._record_review_recovery(action, ValueError('Exact transcript lost'), retryable=False)
            engine._authorize_review_replacement(action, grant_id='GR-review')
        self.complete()
        cycle = engine.runtime['review_cycles'][opened['review_cycle_id']]
        self.assertEqual(cycle['status'], 'completed')
        self.assertEqual(cycle['decision'], 'match')
        self.assertEqual(self.use()['status'], 'active' if replacement else 'suspended')
        self.assertEqual(engine.instance['identity_assessments'], original)
        self.assertEqual(self.use()['history'][-1]['reassessment_ref'], cycle['id'])
        self.assertEqual(len(cycle.get('replacement_receipts', [])), int(replacement))


class AssessmentReassessmentTests(ReassessmentCase):
    def test_confirmed_error_withdraws_without_creating_a_new_identity_assessment(self):
        """About 0.6 s, over the 0.2 s unit budget: the review scene publishes every review step through the storage contract (a dispute runs organize, answer and judge stages)."""
        self.engine.instance['goal_judgments'] = [
            {'id': 'GJ-dependent', 'used_sources': ['K1'], 'current': True},
            {'id': 'GJ-unrelated', 'used_sources': [], 'current': True}]
        formal = copy.deepcopy(self.engine.instance['formal_results'])
        self.engine._start_assessment_reassessment(**self.request(self.defect()))
        self.complete('mismatch')
        self.assertEqual(self.use()['status'], 'withdrawn')
        self.assertEqual(len(self.engine.instance['identity_assessments']), 1)
        self.assertFalse(self.scene.usable())
        self.assertFalse(self.engine.instance['goal_judgments'][0]['current'])
        self.assertTrue(self.engine.instance['goal_judgments'][1]['current'])
        self.assertEqual(self.engine.instance['formal_results'], formal)

    def test_reassessment_organizer_answer_and_judges_replay_the_same_sealed_object(self):
        """About 1.8 s, over the 0.2 s unit budget: the review scene publishes every review step through the storage contract (two dispute rounds, six judge attempts)."""
        from support.entry import entry
        _entry = entry()
        result = self.engine._start_assessment_reassessment(**self.request(self.defect()))
        self.scene.execute()  # scope
        self.scene.execute({'decision': 'mismatch', 'findings': [
            {'id': 'disputed', 'statement': 'An input premise may be missing', 'evidence': ['proposal']}]})
        stages = []
        while any(a['role'] == 'identity_review' for a in self.engine.runtime['queue']):
            stages.append(self.scene.pending()['stage'])
            self.scene.execute()
        self.assertIn('organize', stages)
        self.assertIn('answer', stages)
        self.assertEqual(stages.count('judge'), 6)
        cycle = self.engine.runtime['review_cycles'][result['review_cycle_id']]
        self.assertEqual(validate_sealed_review(cycle, self.engine.runtime, instance=self.engine.instance, at=_entry.ports.clock.now(), clock=_entry.ports.clock)['decision'], 'match')
        self.assertEqual(self.use()['status'], 'active')

    def test_unresolved_remains_suspended_and_finite_activity_retains_next_owner(self):
        """About 0.4 s, over the 0.2 s unit budget: the review scene publishes every review step through the storage contract."""
        result = self.engine._start_assessment_reassessment(**self.request(self.defect()))
        self.complete('unresolved')
        self.assertEqual(self.use()['status'], 'suspended')
        self.assertEqual(self.engine._settle_assessment_reassessments(), [result['review_cycle_id']])
        activity = self.engine.runtime['activities'][result['owner_activity_id']]
        self.assertEqual(activity['status'], 'finished')
        self.assertEqual(activity['unresolved'][0]['next_owner'], 'research_plan')
        self.assertTrue(activity['unresolved'][0]['revisit_conditions'])
        repeated = self.engine._start_assessment_reassessment(**self.request(self.defect()))
        self.assertEqual(repeated['disposition'], 'already_reviewed')

    def test_reaffirmed_negative_original_is_not_positive_knowledge(self):
        """About 0.7 s, over the 0.2 s unit budget: the review scene publishes every review step through the storage contract (two reviews, one with a dispute)."""
        self.open_scene(1)
        self.original = self.engine._start_identity_review('K1')
        self.complete('mismatch')
        self.assessment = self.scene.assessment()
        self.assertEqual(self.assessment['decision'], 'mismatch')
        self.engine._start_assessment_reassessment(**self.request(self.defect()))
        self.complete('match')
        self.assertEqual(self.use()['status'], 'active')
        self.assertFalse(self.scene.usable())
        self.assertEqual(self.scene.assessment()['decision'], 'mismatch')

    def test_changed_current_input_and_forged_result_target_are_rejected(self):
        """About 0.3 s, over the 0.2 s unit budget: the review scene publishes every review step through the storage contract."""
        from support.entry import entry
        _entry = entry()
        result = self.engine._start_assessment_reassessment(**self.request(self.defect()))
        premises = copy.deepcopy(self.engine.instance['review_policy'])
        self.engine.instance['review_policy']['activity_execution_limit'] += 1
        with self.assertRaisesRegex(ValueError, 'premises changed'):
            self.engine._review_cycle(self.scene.pending())
        self.engine.instance['review_policy'] = premises
        self.engine.instance['knowledge']['K1']['kind_use_suspended'] = True
        with self.assertRaisesRegex(ValueError, 'premises changed'):
            self.engine._review_cycle(self.scene.pending())
        self.engine.instance['knowledge']['K1'].pop('kind_use_suspended')
        self.complete()
        cycle = copy.deepcopy(self.engine.runtime['review_cycles'][result['review_cycle_id']])
        entry = next(iter(cycle['results'].values()))
        entry['output']['proposal_digest'] = 'another-target'
        with self.assertRaisesRegex(ValueError, 'actual accepted execution|another proposal'):
            validate_sealed_review(cycle, self.engine.runtime, instance=self.engine.instance, at=_entry.ports.clock.now(), clock=_entry.ports.clock)

    def test_ordinary_report_does_not_suspend(self):
        result = self.engine._start_assessment_reassessment(**self.request({'kind': 'report', 'text': 'It seems wrong'}))
        self.assertEqual(result['disposition'], 'report_only')
        self.assertEqual(self.use()['status'], 'active')

    def test_actual_central_control_and_activity_settlement_call_the_reassessment_mixin(self):
        """About 0.35 s, over the 0.2 s unit budget: the review scene publishes every review step through the storage contract."""
        request = {'id': 'CTRL-reassessment', 'action': 'request',
                   'config': {'role': 'identity_review', 'assessment_reassessment': self.request(self.defect())}}
        self.assertTrue(self.engine._review_recovery_control(request))
        cid = self.scene.pending()['review_cycle_id']
        self.complete('unresolved')
        cycle = self.engine.runtime['review_cycles'][cid]
        eid = list(cycle['results'].values())[-1]['execution_id']
        self.engine._settle_activity(eid)
        activity = self.engine.runtime['activities'][cycle['owner_activity_id']]
        self.assertEqual(activity['status'], 'finished')
        self.assertEqual(activity['unresolved'][0]['next_owner'], 'research_plan')

    def test_independent_objection_must_have_read_the_exact_original_assessment(self):
        for bound in (False, True):
            proposal = {'revision': 1, **({'original_assessment': copy.deepcopy(self.assessment)} if bound else {})}
            seed = scoped_start(proposal, reviewers=2, max_rounds=1)
            cycle = start_review(proposal, reviewers=2, policy=seed['review_policy'])
            cid = 'objection-' + str(bound)
            cycle['id'] = cid
            while next_actions(cycle):
                action = next_actions(cycle)[0]
                output = review_stage_output(cycle, action['stage'])
                if action['stage'] == 'scope':
                    output.update(scope_complete=True, scope_assessment=seed['scope_assessment'])
                elif action['stage'] == 'initial' and action['slot'] == 'initial-0':
                    output.update(decision='mismatch', findings=[{'id': 'specific', 'statement': 'The original domain judgment conflicts with its input',
                        'evidence': ['assessment:' + self.assessment['id']]}])
                eid = cid + '-' + action['stage'] + '-' + action['slot']
                self.engine.runtime['executions'][eid] = {'id': eid, 'role': 'identity_review', 'status': 'ended',
                    'actor_kind': 'ai', 'execution_profile_ref': copy.deepcopy(self.scene.profile),
                    'outcome': 'output_accepted', 'output': copy.deepcopy(output), 'action': {**action, 'review_cycle_id': cid}}
                cycle = accept_result(cycle, action, output, eid)
            self.engine.runtime['review_cycles'][cid] = cycle
            result = self.engine._start_assessment_reassessment(**self.request({'kind': 'independent_objection',
                'review_cycle_id': cid, 'result_key': 'initial:1:initial-0', 'finding_id': 'specific'}))
            self.assertEqual(result['disposition'], 'reassessment_opened' if bound else 'report_only')

    def test_actual_scope_to_sealed_reaffirmation_restores_same_assessment(self):
        """About 0.35 s, over the 0.2 s unit budget: the review scene publishes every review step through the storage contract."""
        from support.entry import entry
        _entry = entry()
        result = self.engine._start_assessment_reassessment(**self.request(self.defect()))
        cid = result['review_cycle_id']
        self.assertEqual(self.use()['status'], 'suspended')
        self.assertEqual(self.scene.pending()['stage'], 'scope')
        self.assertEqual(self.engine.instance['knowledge']['K1']['review_cycle_id'], self.original)
        while any(a['role'] == 'identity_review' for a in self.engine.runtime['queue']):
            self.scene.execute()
        cycle = self.engine.runtime['review_cycles'][cid]
        self.assertEqual(validate_sealed_review(cycle, self.engine.runtime, instance=self.engine.instance, at=_entry.ports.clock.now(), clock=_entry.ports.clock)['decision'], 'match')
        self.assertEqual(self.use()['status'], 'active')
        self.assertEqual(len(self.engine.instance['identity_assessments']), 1)
        self.assertEqual(self.engine.instance['identity_assessments'][self.assessment['id']], self.assessment)
        self.assertEqual(self.use()['history'][-1]['reassessment_ref'], cid)
        execution_id = next(iter(cycle['results'].values()))['execution_id']
        profile_id = self.engine.runtime['executions'][execution_id]['execution_profile_ref']['id']
        del self.engine.instance['execution_profiles'][profile_id]
        with self.assertRaisesRegex(ValueError, 'profile'):
            validate_sealed_review(cycle, self.engine.runtime, instance=self.engine.instance, at=_entry.ports.clock.now(), clock=_entry.ports.clock)

    def test_stale_original_and_unconfirmed_defect_do_not_suspend(self):
        with self.assertRaisesRegex(ValueError, 'exact original'):
            request = self.request(self.defect())
            request['assessment_sha256'] = 'stale'
            self.engine._start_assessment_reassessment(**request)
        eid = self.assessment['execution_ids'][-1]
        result = self.engine._start_assessment_reassessment(**self.request({'kind': 'author_context', 'execution_id': eid}))
        self.assertEqual(result['disposition'], 'report_only')
        self.assertEqual(self.use()['status'], 'active')

    def test_incomplete_and_original_author_continuation_are_rejected(self):
        """About 0.3 s, over the 0.2 s unit budget: the review scene publishes every review step through the storage contract."""
        from support.entry import entry
        _entry = entry()
        result = self.engine._start_assessment_reassessment(**self.request(self.defect()))
        cycle = self.engine.runtime['review_cycles'][result['review_cycle_id']]
        with self.assertRaisesRegex(ValueError, 'complete|sealed'):
            validate_sealed_review(cycle, self.engine.runtime, instance=self.engine.instance, at=_entry.ports.clock.now(), clock=_entry.ports.clock)
        execution = {'id': 'forbidden-continuation', 'actor_kind': 'ai', 'owner_activity_id': result['owner_activity_id'],
                     'status': 'queued', 'continuation_of': self.assessment['execution_ids'][0]}
        with self.assertRaisesRegex(ValueError, 'author|independent'):
            self.engine._admit_review_execution(self.scene.pending(), execution)
        while any(a['role'] == 'identity_review' for a in self.engine.runtime['queue']):
            self.scene.execute()
        cycle = self.engine.runtime['review_cycles'][result['review_cycle_id']]
        eid = next(iter(cycle['results'].values()))['execution_id']
        self.engine.runtime['executions'][eid]['continuation_of'] = self.assessment['execution_ids'][0]
        with self.assertRaisesRegex(ValueError, 'author|independent'):
            validate_sealed_review(cycle, self.engine.runtime, instance=self.engine.instance, at=_entry.ports.clock.now(), clock=_entry.ports.clock)


class DomainReassessmentTests(KnowledgeRoundtripHarness):
    """Domain reassessment over round trips of split knowledge state."""

    def test_qualified_reassessment_restores_negative_and_preserves_sealed_judgment(self):
        """About 0.4 s, over the 0.2 s unit budget: every round trip publishes and reloads the split state through the storage contract."""
        from support.entry import entry
        _entry = entry()
        aid = self.assessment('mismatch')
        original = copy.deepcopy(self.state['identity_assessments'][aid])
        self.state, self.runtime = knowledge.suspend_assessment_use(self.state, self.runtime, aid,
            reason='Independently identified semantic objection', actor_ref='authorized:review', reason_refs=[original['review_cycle_id']], clock=_entry.ports.clock)
        cycle = self.cycle('match', knowledge.assessment_reassessment_proposal(self.state, aid, runtime=self.runtime))
        self.roundtrip()
        self.state, self.runtime = knowledge.apply_assessment_reassessment(self.state, self.runtime, aid,
            cycle['id'], reason='Original negative judgment reaffirmed', actor_ref='authorized:review', at=_entry.ports.clock.now(), clock=_entry.ports.clock)
        self.roundtrip()
        use = next(u for u in self.state['assessment_uses'].values() if u['assessment_id'] == aid)
        self.assertEqual(use['status'], 'active')
        self.assertEqual(use['history'][-1]['reassessment_ref'], cycle['id'])
        self.assertEqual(self.state['identity_assessments'][aid], original)
        self.assertEqual(kr.usable_links(self.state, self.kid), [])
        again = knowledge.apply_assessment_reassessment(self.state, self.runtime, aid, cycle['id'],
            reason='Retry', actor_ref='authorized:review', at=_entry.ports.clock.now(), clock=_entry.ports.clock)
        self.assertEqual(again, (self.state, self.runtime))

    def test_ordinary_review_cannot_restore_or_withdraw_original_assessment(self):
        from support.entry import entry
        _entry = entry()
        aid = self.assessment()
        cycle = self.cycle('mismatch')
        with self.assertRaisesRegex(ValueError, 'reassessment'):
            knowledge.apply_assessment_reassessment(self.state, self.runtime, aid, cycle['id'],
                reason='New ordinary mismatch', actor_ref='authorized:review', at=_entry.ports.clock.now(), clock=_entry.ports.clock)

    def test_reassessment_withdrawal_propagates_locally_and_keeps_formal_result(self):
        from support.entry import entry
        _entry = entry()
        aid = self.assessment()
        fid = self.state['knowledge'][self.kid]['formal_result_id']
        formal = copy.deepcopy(self.state['formal_results'][fid])
        eid = self.state['identity_assessments'][aid]['execution_ids'][0]
        self.state['goal_judgments'] = [{'id': 'GJ-dependent', 'execution_id': eid, 'basis': 'synthetic:goal',
            'decision': 'supported', 'used_sources': [self.kid], 'current': True},
            {'id': 'GJ-other', 'execution_id': eid, 'basis': 'synthetic:goal', 'decision': 'supported',
             'used_sources': [], 'current': True}]
        cycle = self.cycle('mismatch', knowledge.assessment_reassessment_proposal(self.state, aid, runtime=self.runtime))
        self.state, self.runtime = knowledge.apply_assessment_reassessment(self.state, self.runtime, aid,
            cycle['id'], reason='Original positive judgment was erroneous', actor_ref='authorized:review', at=_entry.ports.clock.now(), clock=_entry.ports.clock)
        self.assertEqual(next(u for u in self.state['assessment_uses'].values() if u['assessment_id'] == aid)['status'], 'withdrawn')
        self.assertFalse(self.state['goal_judgments'][0]['current'])
        self.assertTrue(self.state['goal_judgments'][1]['current'])
        self.assertEqual(self.state['formal_results'][fid], formal)
        self.roundtrip()
        current = {g['id']: g['current'] for g in self.state['goal_judgments']}
        self.assertEqual(current, {'GJ-dependent': False, 'GJ-other': True})

    def test_reassessment_rejects_stale_premises_and_original_author(self):
        from support.entry import entry
        _entry = entry()
        aid = self.assessment()
        cycle = self.cycle('match', knowledge.assessment_reassessment_proposal(self.state, aid, runtime=self.runtime))
        eid = next(iter(cycle['results'].values()))['execution_id']
        original = self.state['identity_assessments'][aid]['execution_ids'][0]
        self.runtime['executions'][eid]['continuation_of'] = original
        with self.assertRaisesRegex(ValueError, 'checker resumes an author lineage'):
            knowledge.apply_assessment_reassessment(self.state, self.runtime, aid, cycle['id'], reason='Reaffirm', actor_ref='review', at=_entry.ports.clock.now(), clock=_entry.ports.clock)
        self.runtime['executions'][eid].pop('continuation_of')
        self.runtime['executions'][eid]['context_origin'] = [original]
        with self.assertRaisesRegex(ValueError, 'author context'):
            knowledge.apply_assessment_reassessment(self.state, self.runtime, aid, cycle['id'], reason='Reaffirm', actor_ref='review', at=_entry.ports.clock.now(), clock=_entry.ports.clock)
        self.runtime['executions'][eid]['context_origin'] = []
        self.state['active_trust_environment'] = 'TE-other'
        original_assessment = copy.deepcopy(self.state['identity_assessments'][aid])
        self.state, self.runtime = knowledge.apply_assessment_reassessment(self.state, self.runtime, aid,
            cycle['id'], reason='Reaffirm original judgment with noncurrent premises', actor_ref='review', at=_entry.ports.clock.now(), clock=_entry.ports.clock)
        use = next(u for u in self.state['assessment_uses'].values() if u['assessment_id'] == aid)
        self.assertEqual(use['status'], 'suspended')
        self.assertEqual(use['history'][-1]['reassessment_ref'], cycle['id'])
        self.assertEqual(self.state['identity_assessments'][aid], original_assessment)

    def test_inconclusive_reassessment_keeps_suspension_and_has_no_automatic_repeat(self):
        """About 0.25 s, over the 0.2 s unit budget: every round trip publishes and reloads the split state through the storage contract."""
        from support.entry import entry
        _entry = entry()
        aid = self.assessment('unresolved')
        cycle = self.cycle('unresolved', knowledge.assessment_reassessment_proposal(self.state, aid, runtime=self.runtime))
        self.state, self.runtime = knowledge.apply_assessment_reassessment(self.state, self.runtime, aid,
            cycle['id'], reason='Original uncertainty cannot yet be reassessed', actor_ref='review', at=_entry.ports.clock.now(), clock=_entry.ports.clock)
        use = next(u for u in self.state['assessment_uses'].values() if u['assessment_id'] == aid)
        self.assertEqual(use['status'], 'suspended')
        self.assertFalse(any(a.get('review_cycle_id') == cycle['id'] for a in self.runtime['queue']))
        self.roundtrip()
        # The stored state keeps the suspension (the legacy test stopped at the round trip).
        use = next(u for u in self.state['assessment_uses'].values() if u['assessment_id'] == aid)
        self.assertEqual(use['status'], 'suspended')

    def test_independent_alternative_link_prevents_unrelated_fallout(self):
        from support.entry import entry
        _entry = entry()
        aid = self.assessment()
        alternative = self.assessment()
        self.state['goal_judgments'] = [{'id': 'GJ-dependent', 'used_sources': [self.kid], 'current': True}]
        self.state, self.runtime = knowledge.suspend_assessment_use(self.state, self.runtime, aid,
            reason='Checked objection to first judgment only', actor_ref='review', reason_refs=['checked:objection'], clock=_entry.ports.clock)
        self.assertTrue(self.state['goal_judgments'][0]['current'])
        self.assertEqual([l['assessment_id'] for l in kr.usable_links(self.state, self.kid)], [alternative])

    def test_reassessment_rejects_forged_conclusion_and_accepts_final_running_execution(self):
        from support.entry import entry
        _entry = entry()
        aid = self.assessment()
        cycle = self.cycle('match', knowledge.assessment_reassessment_proposal(self.state, aid, runtime=self.runtime))
        cycle['decision'] = 'mismatch'
        with self.assertRaisesRegex(ValueError, 'sealed evidence'):
            knowledge.apply_assessment_reassessment(self.state, self.runtime, aid, cycle['id'], reason='Forged', actor_ref='review', at=_entry.ports.clock.now(), clock=_entry.ports.clock)
        cycle['decision'] = 'match'
        eid = cycle['results'][cycle['sealed'][-1]]['execution_id']
        execution = self.runtime['executions'][eid]
        execution.update(status='running', outcome=None)
        execution.pop('output')
        self.state, self.runtime = knowledge.apply_assessment_reassessment(self.state, self.runtime, aid,
            cycle['id'], reason='Sealed final response in central transaction', actor_ref='review', at=_entry.ports.clock.now(), clock=_entry.ports.clock)
        self.assertTrue(knowledge.assess_use(self.state['identity_assessments'][aid], self.state)['valid'])


class ReassessmentStorageTests(KnowledgeRoundtripHarness):
    def test_actual_split_state_suspend_review_save_reload_and_next_owner(self):
        """About 0.4 s, over the 0.2 s unit budget: every round trip publishes and reloads the split state through the storage contract, and the engine is loaded three times.

        The engine's reassessment over the stored split state: open, publish, reload, review, settle, reload.

        The legacy test put the harness state into a ``ReviewFakeEngine`` and replaced
        its ``_enqueue``; here the engine is the product's, loaded from the published
        head, and every step publishes through the storage contract.
        """
        aid = self.assessment()
        assessment = self.state['identity_assessments'][aid]
        original = self.runtime['review_cycles'][assessment['review_cycle_id']]
        original['assessment_id'] = aid
        self.state['knowledge'][self.kid]['review_cycle_id'] = original['id']
        producer = original['results']['scope:1:scope']['execution_id']
        flawed = original['results']['initial:1:initial-0']['execution_id']
        original['producer_execution_ids'] = [producer]
        self.runtime['executions'][flawed]['context_origin'] = [producer]
        self.state['review_policy'] = copy.deepcopy(original['review_policy'])
        self.state['config'] = {'review_research_limit': DEFAULT_CONFIG['review_research_limit']}
        self.roundtrip()
        engine = self.engine()
        result = engine._start_assessment_reassessment(aid, exact_content_hash(assessment), {'kind': 'author_context', 'execution_id': flawed})
        engine._save()
        engine = self.engine()  # reload the published state in a new engine
        self.assertEqual(next(u for u in engine.instance['assessment_uses'].values() if u['assessment_id'] == aid)['status'], 'suspended')
        while any(a['role'] == 'identity_review' for a in engine.runtime['queue']):
            action = next(a for a in engine.runtime['queue'] if a['role'] == 'identity_review')
            cid = action['review_cycle_id']
            cycle = engine.runtime['review_cycles'][cid]
            self.assertEqual(engine._prepare_review_context(action, self.root / 'synthetic-review-input')['disposition'], 'ready')
            output = review_stage_output(cycle, action['stage'])
            if action['stage'] == 'scope':
                scope = scoped_start(cycle['proposal'], reviewers=2, max_rounds=1)['scope_assessment']
                scope.update(policy_id=cycle['review_policy']['id'],
                             selected_profile_ref=profile_ref(self.profile), activity_execution_limit=cycle['activity_execution_limit'])
                output.update(scope_complete=True, scope_assessment=scope)
            eid = self.clock.new_id('EX')
            execution = execution_lifecycle.create_execution(execution_id=eid, owner_activity_id=cycle['owner_activity_id'],
                actor_kind='ai', input_manifest={'proposal_digest': cycle['proposal_digest'], 'prompt': {'sha256': 'a' * 64}},
                profile_ref=profile_ref(self.profile), created_at='2026-09-20T00:00:00Z')
            execution.update(role='identity_review', action=copy.deepcopy(action), input_snapshot=engine.head)
            self.assertEqual(engine._admit_review_execution(action, execution)['disposition'], 'admitted')
            activities.assign_execution(engine.runtime, cycle['owner_activity_id'], execution)
            for status in ('starting', 'running'):
                execution_lifecycle.transition_execution(execution, status, at='2026-09-20T00:00:00Z')
            engine.runtime['queue'].remove(action)
            engine._apply_identity_review(action, output, eid)
            execution = engine.runtime['executions'][eid]
            execution.update(output=output, submission_receipt={'state': 'accepted', 'evidence_ref': 'synthetic:review'})
            execution_lifecycle.transition_execution(execution, 'stopping', at='2026-09-20T00:00:00Z')
            execution_lifecycle.transition_execution(execution, 'ended', at='2026-09-20T00:00:00Z', outcome='output_accepted')
        self.assertEqual(engine._settle_assessment_reassessments(), [result['review_cycle_id']])
        engine._save()
        engine = self.engine()
        use = next(u for u in engine.instance['assessment_uses'].values() if u['assessment_id'] == aid)
        self.assertEqual(use['status'], 'active')
        self.assertEqual(use['history'][-1]['reassessment_ref'], result['review_cycle_id'])
        self.assertEqual(engine.runtime['activities'][result['owner_activity_id']]['followups'][0]['next_owner'], 'research_plan')
        self.assertEqual(engine.instance['identity_assessments'][aid], assessment)


if __name__ == '__main__':
    unittest.main()
