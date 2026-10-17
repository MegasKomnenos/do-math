"""4-B: the two review wait kinds preserve a slot until exact input/authority recovers."""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

from do_math import governance
from do_math.review_cycle import record_turn
from do_math.reporting import status_report, render_human_report
from do_math.wait_rules import REVIEW_WAIT_RULES, review_preparation_wait, review_wait_kind
from support.review_inputs import grant_replacement
from support.review_scene import ReviewScene, warm
from support.review_owner_inputs import ReviewOwnerCase
from support.wait_reporting import assert_wait_report
from support.storage_records import INSTANCE_ID

setUpModule = warm


class ReviewWaitContractTests(unittest.TestCase):
    def test_unknown_disposition_and_formal_wait_are_rejected(self):
        from do_math.wait_rules import formal_wait
        for function, args, options, reason in (
            (review_wait_kind, ('invented',), {}, "review disposition has no declared wait: 'invented'"),
            (formal_wait, ({'id': 'AC'}, 'invented'), {'reason': 'invalid wait'},
             "unregistered formal wait: 'invented'"),
        ):
            before = deepcopy((args, options))
            with self.subTest(reason=reason), self.assertRaises(ValueError) as caught:
                function(*args, **options)
            self.assertEqual(str(caught.exception), reason)
            self.assertEqual((args, options), before)

    def test_every_declared_review_wait_is_produced_preserved_and_released(self):
        """T3 0.6 s: real restoration/authority producers retain each wait's distinct resolver."""
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
                if kind == 'review_authority':
                    restored = engine._retry_review_restoration(action, Path(directory) / 'restored')
                    self.assertEqual(restored['disposition'], 'review_resumed')
                else:
                    request = {'id': 'UC-restored-slot', 'action': 'request', 'config': {
                        'role': 'maintenance', 'review_restoration': {'action': action}}}
                    self.assertIs(engine._review_recovery_control(request), True)
                    restored = engine.runtime['history'][-1]
                    self.assertEqual((restored['kind'], restored['request_id'], restored['outcome']['disposition']),
                                     ('review_restoration', request['id'], 'review_resumed'))
                self.assertNotIn(action['id'], engine.runtime['waiting_actions'])
                queue = deepcopy(engine.runtime['queue'])
                repeated = engine._retry_review_restoration(action, Path(directory) / 'same-slot-again')
                self.assertEqual(repeated['disposition'], 'review_resumed')
                self.assertEqual(engine.runtime['queue'], queue)
                exercised.add(kind)
        self.assertEqual(exercised, set(REVIEW_WAIT_RULES))


class ReviewAdmissionWaitContractTests(ReviewOwnerCase):
    def test_recovery_keeps_the_canonical_target_origin_and_permanent_slot_checks(self):
        """T3 0.47 s: the stored review proposal supplies its actual frozen coordinates."""
        _, action = self.opened()
        engine = self.engine
        request = {'id': 'UC-review-guards', 'action': 'request', 'origin': 'user', 'config': {
            'role': 'maintenance', 'review_replacement': {'action': action}}}
        before = deepcopy((engine.head, engine.instance, engine.runtime))
        cases = [({**request, 'config': {**request['config'], 'review_replacement': {
                      'action': {**action, 'target': 'K-other'}}}}, 'review action refers to another or missing proposal'),
                 ({**request, 'origin': 'operator'}, 'review replacement requires an explicit user decision'),
                 ({**request, 'config': {**request['config'], 'review_replacement': {
                      'action': action, 'delegation_id': 'DG-unassigned', 'case': {}}}},
                  'delegated recovery requires a current permanently failed review slot')]
        for value, reason in cases:
            with self.subTest(reason=reason), self.assertRaises(ValueError) as caught:
                engine._review_recovery_control(value)
            self.assertEqual(str(caught.exception), reason)
            self.assertEqual((engine.head, engine.instance, engine.runtime), before)


    def test_revoked_replacement_authority_produces_a_durable_wait_until_exact_reauthorization(self):
        engine = self.engine
        # The layer-2 review fixture omits the instance metadata used by status.
        engine.instance['id'] = INSTANCE_ID
        grant_replacement(engine)
        cid, original, prior = self.registered()
        from do_math.execution_lifecycle import transition_execution
        transition_execution(prior, 'stopping', at=engine.ports.clock.now())
        transition_execution(prior, 'ended', at=engine.ports.clock.now(), outcome='cancelled')
        engine._record_review_recovery(original, ValueError('lost exact slot input'), retryable=False)
        engine._authorize_review_replacement(original, grant_id='GR-review')
        action = deepcopy(next(row for row in engine.runtime['queue'] if row.get('replacement_for') is not None))
        engine.instance, engine.runtime, _ = governance.apply_decision(engine.instance, engine.runtime,
            {'kind': 'revoke', 'decision_id': 'DEC-revoke-review', 'grant_id': 'GR-review'},
            source_ref='SOURCE-review', clock=engine.ports.clock)
        accounting = deepcopy(engine.runtime['review_cycles'][cid]['execution_accounting'])
        denied = engine._register_execution(action, {'id': 'EX-revoked-review',
            'role': 'identity_review', 'status': 'queued'})
        self.assertIsNone(denied)
        self.assertNotIn('EX-revoked-review', engine.runtime['executions'])
        wait = deepcopy(engine.runtime['waiting_actions'][action['id']])
        self.assertEqual((wait['kind'], wait['next_owner']), ('review_authority', 'governance'))
        self.assertEqual(wait['action'], action)
        self.assertEqual(engine.runtime['review_cycles'][cid]['execution_accounting'], accounting)
        engine._save()
        assert_wait_report(self, engine, action['id'])
        before = deepcopy(engine.runtime)
        held = engine._retry_review_restoration(action, self.root / 'revoked')
        self.assertEqual(held['disposition'], 'authorization_denied')
        self.assertEqual(engine.runtime, before)
        # Neither a different seat nor a revoked grant resolves the held action.
        for field, value in (('slot', 'initial-1'), ('stage', 'judge'), ('round', action['round'] + 1)):
            self.assertEqual(engine._release_review_wait({**original, field: value}), [])
            self.assertEqual(engine.runtime['waiting_actions'], before['waiting_actions'])
            self.assertEqual(engine.runtime['activities'], before['activities'])
        rejected = engine._authorize_review_replacement(original, grant_id='GR-review')
        self.assertEqual(rejected['disposition'], 'authorization_denied')
        self.assertEqual(engine.runtime['waiting_actions'], before['waiting_actions'])
        self.assertEqual(engine.runtime['activities'], before['activities'])
        before_control = deepcopy((engine.instance, engine.runtime))
        with self.assertRaisesRegex(ValueError, '^review replacement decision is not authorized: no current grant permits this action$'):
            engine._review_recovery_control({'id': 'UC-revoked-replacement', 'action': 'request',
                'origin': 'user', 'text': 'Replace this exact slot using the revoked grant',
                'config': {'role': 'maintenance', 'review_replacement': {
                    'action': original, 'grant_id': 'GR-review'}}})
        self.assertEqual((engine.instance, engine.runtime), before_control)
        specification = deepcopy(engine.instance['decisions']['DEC-review']['change']['grant'])
        specification['id'] = 'GR-current-review'
        engine.instance, engine.runtime, _ = governance.apply_decision(engine.instance, engine.runtime,
            {'kind': 'grant', 'decision_id': 'DEC-current-review', 'grant': specification},
            source_ref='SOURCE-review', clock=engine.ports.clock)
        authorized = engine._authorize_review_replacement(original, grant_id='GR-current-review')
        self.assertEqual(authorized['disposition'], 'replacement_ready')
        self.assertNotIn(action['id'], engine.runtime['waiting_actions'])
        owner = action['owner_activity_id']
        self.assertEqual(engine.runtime['activities'][owner]['status'], 'ready')
        self.assertNotIn('waiting', engine.runtime['activities'][owner])
        self.assertEqual(engine.runtime['review_cycles'][cid]['execution_accounting'], accounting)
        engine._save()
        engine.head, engine.instance, engine.runtime = engine.store.load()
        report = status_report(engine.store, engine.head, engine.instance, engine.runtime,
            requested_areas=['record_storage'],
            evaluation_context={'now': engine.ports.clock.now(), 'host_id': engine.host_id})
        self.assertNotIn(action['id'], report['waiting_actions'])
        self.assertNotIn(owner, report['waiting_activities'])
        lines = render_human_report(report).splitlines()
        self.assertFalse(any(line.startswith('action ' + action['id'] + ':') or
                             line.startswith('activity ' + owner + ':') for line in lines))
        queued = [row for row in engine.runtime['queue'] if row.get('replacement_for') is not None]
        self.assertEqual(len(queued), 1)
        self.assertEqual(queued[0]['id'], action['id'])
        self.assertEqual(queued[0]['grant_id'], 'GR-current-review')
        after = deepcopy(engine.runtime['queue'])
        engine._authorize_review_replacement(original, grant_id='GR-current-review')
        self.assertEqual(engine.runtime['queue'], after)
        self.assertEqual(engine.runtime['activities'][owner]['status'], 'ready')
        self.assertEqual(engine.runtime['review_cycles'][cid]['execution_accounting'], accounting)
        admitted = engine._register_execution(queued[0], {'id': 'EX-current-review',
            'role': 'identity_review', 'status': 'queued'})
        self.assertIsNotNone(admitted)
        self.assertEqual(admitted['owner_activity_id'], owner)
        self.assertNotIn('waiting', engine.runtime['activities'][owner])
        self.assertEqual(engine.runtime['review_cycles'][cid]['execution_accounting']['executions_used'],
            [*accounting['executions_used'], 'EX-current-review'])
        engine._save()
        self.assertNotIn(action['id'], engine.store.load()[2]['waiting_actions'])

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
        activities.wait_for(self.engine.runtime, owner, kind='review_input_restoration', reason='review_input_restoration',
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
