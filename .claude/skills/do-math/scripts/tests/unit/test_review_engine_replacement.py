"""The engine's identity review mixin (``review_engine``, layer 2) and central recovery: replacing a lost slot.

A slot whose exact transcript cannot be restored is replaced only under a
current user grant (``review_fixtures.grant_replacement``) or an applied
delegation. Every test runs the product's ``ResearchEngine`` over the stored
review state of ``support.review_scene`` and calls the mixin and the central
recovery control (``core_engine``, layer 2) as the owner does.
"""
from copy import deepcopy
import hashlib
import json
import tempfile
import unittest

from do_math import activities, delegations, governance
from do_math.review_cycle import record_turn, validate_sealed_review
from support.review_inputs import grant_replacement
from support.review_scene import ReviewScene, warm


def setUpModule():
    warm()


class ReviewSceneCase(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.scene = ReviewScene(temporary.name)
        self.engine = self.scene.engine

    def replacement(self):
        return next(a for a in self.engine.runtime['queue'] if a.get('replacement_for') is not None)

    def delegate(self, cid, action):
        """The user's review replacement decision ``ORIGINAL`` delegated as ``DG``, and a case for ``action``'s slot."""
        from support.entry import entry
        _entry = entry()
        engine = self.engine
        engine.instance['decisions']['ORIGINAL'] = {'id': 'ORIGINAL', 'actor': 'user',
            'kind': 'review_replacement', 'source_ref': 'SOURCE-review'}
        engine.instance, engine.runtime, _ = governance.apply_decision(engine.instance, engine.runtime,
            {'kind': 'delegation', 'decision_id': 'DD', 'delegation': {'id': 'DG', 'status': 'active',
             'decision_kind': 'review_replacement', 'original_decision_id': 'ORIGINAL',
             'included_targets': ['K1'], 'excluded_targets': [], 'external_effects': [],
             'resource_limits': {}, 'expires_at': None}}, source_ref='SOURCE-review', clock=_entry.ports.clock)
        effect = {'review_cycle_id': cid, 'stage': action['stage'], 'slot': action['slot'],
                  'round': action['round'], 'replacement_for': 0, 'continuity_break_cause': 'permanent_loss'}
        return {'id': 'CASE', 'decision_kind': 'review_replacement', 'target_id': 'K1',
                'external_effects': [], 'resources': {}, 'effect': effect}


class UserGrantReplacementTests(ReviewSceneCase):
    def test_central_replacement_control_releases_wait_and_queues_next_execution(self):
        engine, scene = self.engine, self.scene
        grant_replacement(engine)
        cid = scene.start('K1')
        action = deepcopy(scene.pending())
        action.update(id='AC-held', owner_activity_id='AY-held')
        engine._prepare_review_context(action, scene.root / 'initial')
        recovery = engine._record_review_recovery(action, ValueError('permanent_loss'), retryable=False)
        activities.open_activity(engine.runtime, activity_id='AY-held', activity_kind='identity_review',
                                 owner_ref=cid, input_refs=['K1'], opened_at='now')
        activities.wait_for(engine.runtime, 'AY-held', reason='review_input_restoration',
                            condition={'kind': 'review_recovery', 'recovery': recovery}, next_owner='governance', at='now')
        engine.runtime['waiting_actions'] = {'AC-held': {'kind': 'review_input_restoration', 'action': action, 'recovery': recovery}}
        engine.runtime['queue'] = []
        request = {'action': 'request', 'config': {'role': 'maintenance', 'review_replacement': {'action': action, 'grant_id': 'GR-review'}}}
        self.assertTrue(engine._review_recovery_control(request))
        self.assertNotIn('AC-held', engine.runtime['waiting_actions'])
        self.assertEqual(engine.runtime['activities']['AY-held']['status'], 'ready')
        replacement = self.replacement()
        self.assertEqual(replacement['owner_activity_id'], 'AY-held')
        self.assertEqual(engine._prepare_review_context(replacement, scene.root / 'next')['disposition'], 'ready')

    def test_corrupt_slot_can_be_replaced_from_verified_records_under_real_user_grant(self):
        engine, scene = self.engine, self.scene
        grant_replacement(engine)
        cid = scene.start('K1')
        action = deepcopy(scene.pending())
        cycle = record_turn(engine.runtime['review_cycles'][cid], action['slot'], [
            {'role': 'user', 'content': 'preserved visible conversation', 'message_id': 'good'},
            {'role': 'tool', 'content': 'lost exact body', 'message_id': 'bad'}])
        cycle['turns'][action['slot']][1]['content'] = 'CORRUPTED'
        engine.runtime['review_cycles'][cid] = cycle
        engine._record_review_recovery(action, ValueError('permanent_loss'), retryable=False)
        outcome = engine._authorize_review_replacement(action, grant_id='GR-review')
        self.assertEqual(outcome['disposition'], 'replacement_ready')
        replacement = self.replacement()
        scene.execute({'summary': 'PRIVATE-PEER-REVIEW'})
        context = engine._prepare_review_context(replacement, scene.root / 'replacement')
        self.assertEqual(context['disposition'], 'ready')
        self.assertIn('preserved visible conversation', json.dumps(context))
        self.assertNotIn('CORRUPTED', json.dumps(context))
        self.assertNotIn('PRIVATE-PEER-REVIEW', json.dumps(context))
        scene.execute()
        self.assertTrue(scene.usable())
        self.assertTrue(engine.runtime['review_cycles'][cid]['replacement_receipts'])

    def test_replacement_rejects_forged_grant_source_and_revocation_before_input(self):
        engine, scene = self.engine, self.scene
        grant_replacement(engine)
        scene.start('K1')
        action = deepcopy(scene.pending())
        engine._record_review_recovery(action, ValueError('permanent_loss'), retryable=False)
        source = engine.instance['governance_sources']['SOURCE-review']['text']
        engine.instance['governance_sources']['SOURCE-review']['text'] += ' forged'
        self.assertEqual(engine._authorize_review_replacement(action, grant_id='GR-review')['disposition'], 'authorization_denied')
        engine.instance['governance_sources']['SOURCE-review']['text'] = source
        outcome = engine._authorize_review_replacement(action, grant_id='GR-review')
        self.assertEqual(outcome['disposition'], 'replacement_ready')
        engine.instance['grants']['GR-review']['status'] = 'revoked'
        result = engine._prepare_review_context(self.replacement(), scene.root / 'revoked')
        self.assertEqual(result['disposition'], 'authorization_denied')

    def test_approved_replacement_omits_malformed_manifest_without_rethrowing(self):
        engine, scene = self.engine, self.scene
        grant_replacement(engine)
        cid = scene.start('K1')
        action = deepcopy(scene.pending())
        cycle = record_turn(engine.runtime['review_cycles'][cid], action['slot'], [
            {'role': 'user', 'content': 'UNVERIFIABLE', 'message_id': 'lost'}])
        cycle['transcript_manifest'][action['slot']][0] = None
        engine.runtime['review_cycles'][cid] = cycle
        result = engine._prepare_review_context(action, scene.root / 'broken')
        self.assertEqual(result['disposition'], 'recovery_recorded')
        outcome = engine._authorize_review_replacement(action, grant_id='GR-review')
        self.assertEqual(outcome['disposition'], 'replacement_ready')
        ready = engine._prepare_review_context(self.replacement(), scene.root / 'replacement')
        self.assertEqual(ready['disposition'], 'ready')
        self.assertNotIn('UNVERIFIABLE', json.dumps(ready))
        scene.execute()
        scene.execute()
        self.assertTrue(scene.usable())

    def test_replacement_unresolved_question_keeps_organizer_finding_coordinates(self):
        engine, scene = self.engine, self.scene
        grant_replacement(engine)
        scene.start('K1')
        action = deepcopy(scene.pending())
        engine._record_review_recovery(action, ValueError('permanent_loss'), retryable=False)
        engine._authorize_review_replacement(action, grant_id='GR-review')
        scene.execute()
        scene.execute({'decision': 'unresolved', 'questions': ['Exact domain still disputed']})
        self.assertEqual(scene.pending()['stage'], 'organize')
        scene.execute()
        self.assertEqual(scene.pending()['stage'], 'judge')


class DelegatedReplacementTests(ReviewSceneCase):
    def test_checked_delegation_replacement_survives_its_own_recorded_input(self):
        from support.entry import entry
        _entry = entry()
        engine, scene = self.engine, self.scene
        grant_replacement(engine)
        cid = scene.start('K1')
        action = deepcopy(scene.pending())
        engine._record_review_recovery(action, ValueError('permanent_loss'), retryable=False)
        case = self.delegate(cid, action)
        case['basis_refs'] = [cid]
        application = delegations.prepare_application(engine.instance, engine.runtime, 'DG', case, now_iso=engine.ports.clock.now())
        for eid, stage in [('INTERPRET', 'interpret'), ('CHECK', 'check')]:
            engine.runtime['executions'][eid] = {'id': eid, 'role': 'intent_interpretation', 'status': 'ended',
                                                'delegation_input_sha256': application['input_sha256']}
            delegations.record_judgment(engine.runtime, application['id'],
                {'input_sha256': application['input_sha256'], 'decision': 'within_scope', 'reason': 'Same authorized recovery'},
                execution_id=eid, stage=stage)
        case['application_id'] = application['id']
        outcome = engine._authorize_review_replacement(action, grant_id='GR-review', delegation_id='DG', case=case)
        self.assertEqual(outcome['disposition'], 'replacement_ready')
        replacement = self.replacement()
        engine.runtime['queue'].remove(replacement)
        engine.runtime['queue'].insert(0, replacement)
        scene.execute(record_first=True)
        scene.execute()
        self.assertTrue(scene.usable())
        self.assertEqual(validate_sealed_review(engine.runtime['review_cycles'][cid], engine.runtime,
            instance=engine.instance, at=engine.ports.clock.now(), clock=engine.ports.clock)['decision'], 'match')

    def test_actual_blind_judgments_apply_the_approved_review_recovery(self):
        engine, scene = self.engine, self.scene
        grant_replacement(engine)
        cid = scene.start('K1')
        action = deepcopy(scene.pending())
        engine._record_review_recovery(action, ValueError('permanent_loss'), retryable=False)
        case = self.delegate(cid, action)
        case['basis_refs'] = [{'id': cid}]
        request = {'id': 'UC-case', 'action': 'request', 'config': {'role': 'maintenance', 'review_replacement': {
            'action': action, 'grant_id': 'GR-review', 'delegation_id': 'DG', 'case': case}}}
        self.assertTrue(engine._review_recovery_control(request))
        engine.runtime.setdefault('history', []).append({'kind': 'user_control', 'request': request})
        judgments = [a for a in engine.runtime['queue'] if a.get('delegation_application_id')]
        self.assertEqual(len(judgments), 2)
        application_id = judgments[0]['delegation_application_id']
        application = engine.runtime['delegation_applications'][application_id]
        for index, judgment in enumerate(judgments):
            eid = 'EX-delegation-' + str(index)
            engine.runtime['executions'][eid] = {'id': eid, 'role': 'intent_interpretation', 'status': 'running',
                'input_manifest': {'prompt': {'sha256': hashlib.sha256(('exact rendered prompt ' + str(index)).encode()).hexdigest()}},
                'delegation_input_sha256': application['input_sha256']}
            engine._apply_delegation_judgment(judgment, {'delegation_judgment': {'input_sha256': application['input_sha256'],
                'decision': 'within_scope', 'reason': 'This exact case stays within the original approved replacement'}}, eid)
        self.assertEqual(engine.runtime['delegation_applications'][application_id]['application']['status'], 'applied')
        self.assertTrue(any(a.get('replacement_for') == 0 for a in engine.runtime['queue']))


if __name__ == '__main__':
    unittest.main()
