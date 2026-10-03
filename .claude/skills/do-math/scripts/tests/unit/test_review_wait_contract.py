"""4-B: the two review wait kinds preserve a slot until exact input/authority recovers."""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

from do_math import governance
from do_math.review_cycle import record_turn
from do_math.wait_rules import REVIEW_WAIT_RULES, review_preparation_wait, review_wait_kind
from support.review_inputs import grant_replacement
from support.review_scene import ReviewScene, warm
from support.review_owner_inputs import ReviewOwnerCase

setUpModule = warm


class ReviewWaitContractTests(unittest.TestCase):
    def test_every_declared_review_wait_is_produced_preserved_and_released(self):
        exercised = set()
        for kind in REVIEW_WAIT_RULES:
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as directory:
                scene = ReviewScene(directory)
                engine = scene.engine
                if kind == 'review_authority':
                    grant_replacement(engine)
                cid = scene.start('K1')
                action = deepcopy(scene.pending())
                good = record_turn(engine.runtime['review_cycles'][cid], action['slot'],
                    [{'role': 'assistant', 'content': 'exact original slot input'}])
                engine.runtime['review_cycles'][cid] = deepcopy(good)
                engine.runtime['review_cycles'][cid]['turns'][action['slot']][0]['content'] = 'unverified changed input'
                prepared = engine._prepare_review_context(action, Path(directory) / 'broken')
                if kind == 'review_authority':
                    self.assertEqual(prepared['disposition'], 'recovery_recorded')
                    authorized = engine._authorize_review_replacement(action, grant_id='GR-review')
                    self.assertEqual(authorized['disposition'], 'replacement_ready')
                    action = deepcopy(next(row for row in engine.runtime['queue'] if row.get('replacement_for') is not None))
                    source = engine.instance['governance_sources']['SOURCE-review']['text']
                    engine.instance['governance_sources']['SOURCE-review']['text'] += ' unverified source change'
                    prepared = engine._prepare_review_context(action, Path(directory) / 'unauthorized')
                self.assertEqual(prepared['disposition'], REVIEW_WAIT_RULES[kind]['prepared_disposition'])
                self.assertEqual(review_wait_kind(prepared['disposition']), kind)
                entry = review_preparation_wait(action, prepared)
                self.assertEqual(entry['kind'], kind)
                self.assertEqual(entry['action'], action)
                self.assertEqual(entry['detail'], prepared['recovery'])
                engine.runtime.setdefault('waiting_actions', {})[action['id']] = entry
                before = deepcopy(entry)
                still_held = engine._retry_review_restoration(action, Path(directory) / 'not-yet-restored')
                self.assertNotEqual(still_held['disposition'], 'review_resumed')
                self.assertEqual(engine.runtime['waiting_actions'][action['id']], before)
                if kind == 'review_authority':
                    engine.instance['governance_sources']['SOURCE-review']['text'] = source
                else:
                    engine.runtime['review_cycles'][cid]['turns'] = deepcopy(good['turns'])
                restored = engine._retry_review_restoration(action, Path(directory) / 'restored')
                self.assertEqual(restored['disposition'], 'review_resumed')
                self.assertNotIn(action['id'], engine.runtime['waiting_actions'])
                queue = deepcopy(engine.runtime['queue'])
                repeated = engine._retry_review_restoration(action, Path(directory) / 'same-slot-again')
                self.assertEqual(repeated['disposition'], 'review_resumed')
                self.assertEqual(engine.runtime['queue'], queue)
                exercised.add(kind)
        self.assertEqual(exercised, set(REVIEW_WAIT_RULES))


class ReviewAdmissionWaitContractTests(ReviewOwnerCase):

    def test_an_admitted_replacement_cannot_rebind_its_sealed_authority(self):
        grant_replacement(self.engine)
        cid, action = self.opened()
        self.engine._record_review_recovery(action, ValueError('lost exact slot input'), retryable=False)
        self.assertEqual(self.engine._authorize_review_replacement(action, grant_id='GR-review')['disposition'], 'replacement_ready')
        replacement = deepcopy(next(row for row in self.engine.runtime['queue'] if row.get('replacement_for') is not None))
        execution = self.engine._register_execution(replacement, {'id': 'EX-admitted-authority',
            'role': 'identity_review', 'status': 'queued'})
        self.assertIsNotNone(execution)
        specification = deepcopy(self.engine.instance['decisions']['DEC-review']['change']['grant'])
        specification['id'] = 'GR-different-authority'
        self.engine.instance, self.engine.runtime, _ = governance.apply_decision(self.engine.instance, self.engine.runtime,
            {'kind': 'grant', 'decision_id': 'DC-different-authority', 'grant': specification},
            source_ref='SOURCE-review', clock=self.engine.ports.clock)
        cycle = deepcopy(self.engine.runtime['review_cycles'][cid])
        admitted = deepcopy(self.engine.runtime['executions']['EX-admitted-authority'])
        denied = self.engine._authorize_review_replacement(action, grant_id='GR-different-authority')
        self.assertEqual(denied['disposition'], 'authorization_denied')
        self.assertEqual(denied['reason'], 'replacement authority is already sealed into an admitted attempt')
        self.assertEqual(self.engine.runtime['review_cycles'][cid], cycle)
        self.assertEqual(self.engine.runtime['executions']['EX-admitted-authority'], admitted)

    def test_a_held_activity_blocks_registration_without_losing_its_real_next_owner(self):
        from do_math import activities, execution_lifecycle
        cid, action, execution = self.registered()
        execution_lifecycle.transition_execution(execution, 'stopping', at=self.engine.ports.clock.now())
        execution_lifecycle.transition_execution(execution, 'ended', at=self.engine.ports.clock.now(), outcome='cancelled')
        owner = execution['owner_activity_id']
        activities.wait_for(self.engine.runtime, owner, reason='review_input_restoration',
            condition={'review_cycle_id': cid, 'slot': action['slot']}, next_owner='review_recovery',
            at=self.engine.ports.clock.now())
        before = deepcopy(self.engine.runtime['review_cycles'][cid]['execution_accounting'])
        result = self.engine._register_execution(action, {'id': 'EX-blocked-restoration',
            'role': 'identity_review', 'status': 'queued'})
        self.assertIsNone(result)
        self.assertNotIn('EX-blocked-restoration', self.engine.runtime['executions'])
        entry = self.engine.runtime['waiting_actions'][action['id']]
        self.assertEqual((entry['kind'], entry['next_owner']), ('review_input_restoration', 'review_recovery'))
        self.assertEqual(self.engine.runtime['activities'][owner]['waiting']['next_owner'], 'review_recovery')
        self.assertEqual(self.engine.runtime['review_cycles'][cid]['execution_accounting'], before)
