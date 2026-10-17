"""The engine's delegated review recovery (``core_engine._review_recovery_control``, ``_apply_delegation_judgment``; layer 2), moved from ``test_delegations``.

The legacy test ran on ``review_fixtures.ReviewFakeEngine``, an engine subclass
that skipped its ``__init__``, replaced ``_save`` with an autospec double and
read no artifact. Here the engine is the product's ``ResearchEngine`` over the
stored review state of ``support.review_scene`` (validated by the storage
contract, on the port fakes); the scene answers the reviewer as the legacy
double did. The central recovery control and the delegation judgment
receiver are called as the owner calls them; the two judgment executions are
recorded as the legacy test recorded them.
"""
from copy import deepcopy
import tempfile
import unittest

from do_math import delegations as d
from do_math import governance as gov
from support.review_inputs import grant_replacement
from support.review_scene import ReviewScene, warm


def setUpModule():
    warm()


class DelegatedRecoveryEngineTests(unittest.TestCase):
    def test_current_replacement_authority_denial_preserves_the_failed_slot_and_wait(self):
        """Publicly produced failed seat/request; two registered independent receiver judgments, without model calls."""
        from support.governance_delegation import public_replacement_case
        from support.cross_states import applied
        from do_math.execution_lifecycle import transition_execution
        sim, config = public_replacement_case()
        engine = sim.engine
        applied(sim, 'request', text='Independently compare this held seat.', config=config)
        stages = [a for a in engine.runtime['queue'] if a.get('delegation_application_id')]
        self.assertEqual(len(stages), 2)
        app_id = stages[0]['delegation_application_id']
        shared = d.judgment_input(engine.runtime, app_id)
        executions = []
        for index, action in enumerate(stages):
            execution = engine._register_execution(action, {'id': 'EX-current-' + str(index),
                'role': 'intent_interpretation'})
            execution['delegation_input_sha256'] = shared['input_sha256']
            transition_execution(execution, 'ended', at=sim.clock.now(), outcome='cancelled')
            executions.append(execution['id'])
        output = {'delegation_judgment': {'input_sha256': shared['input_sha256'],
            'decision': 'within_scope', 'reason': 'The exact original decision covers this seat.'}}
        engine._apply_delegation_judgment(stages[0], output, executions[0])
        engine._save()  # Public controls reload; publish these receiver records first.
        applied(sim, 'decision', config={'change': {'kind': 'revoke',
            'grant_id': config['review_replacement']['grant_id']}})
        original = deepcopy((engine.runtime['review_cycles'], engine.runtime['waiting_actions']))
        with self.assertRaisesRegex(ValueError, '^independently checked case no longer authorizes recovery: '):
            engine._apply_delegation_judgment(stages[1], output, executions[1])
        self.assertEqual((engine.runtime['review_cycles'], engine.runtime['waiting_actions']), original)
        app = engine.runtime['delegation_applications'][app_id]
        self.assertEqual(set(app['judgments']), {'interpret', 'check'})
        self.assertEqual({j['output']['decision'] for j in app['judgments'].values()}, {'within_scope'})
        self.assertNotIn('application', app)
        self.assertEqual(len({j['execution_id'] for j in app['judgments'].values()}), 2)
        engine._reload()  # Discard the denied candidate, as the bundle receiver does.
        spec = config['review_replacement']
        request = sim.control('request', text='Replace this seat explicitly.', config={
            'role': 'maintenance', 'review_replacement': {key: deepcopy(spec[key]) for key in ('action', 'grant_id')}})
        engine.process_controls()
        result = engine.control_result(request['request_id'])
        self.assertEqual(result['effect'], 'rejected')
        self.assertEqual(result['reason'],
            'review replacement decision is not authorized: no current grant permits this action')
        self.assertEqual((engine.runtime['review_cycles'], engine.runtime['waiting_actions']), original)
        control_ids = {row.get('request', {}).get('id') for row in engine.runtime['history']}
        source_id = next(identifier for identifier in engine.instance['governance_sources']
                         if identifier not in control_ids)
        sources = deepcopy(engine.instance['governance_sources'])
        collision = sim.control('request', request_id=source_id, text='Different replacement source text.', config={
            'role': 'maintenance', 'review_replacement': {key: deepcopy(spec[key]) for key in ('action', 'grant_id')}})
        engine.process_controls()
        result = engine.control_result(collision['request_id'])
        self.assertEqual((result['effect'], result['reason']), ('rejected', 'preserved control source ID reused'))
        self.assertEqual(engine.instance['governance_sources'], sources)
        self.assertEqual((engine.runtime['review_cycles'], engine.runtime['waiting_actions']), original)

    def test_public_original_reaches_delegated_replacement(self):
        from support.governance_delegation import public_replacement_case
        from support.cross_states import applied, assert_event, queued
        sim, config = public_replacement_case()
        applied(sim, 'request', text='Compare this exact later replacement with my delegation.', config=config)
        stages = deepcopy([a for a in sim.runtime['queue'] if a.get('delegation_application_id')])
        self.assertEqual(len(stages), 2)
        applied(sim, 'pause', text='Do not execute the delegated comparison until I resume.')
        pause = deepcopy(sim.runtime['user_pause'])
        applied(sim, 'request', text='Compare this same case again.', config=config)
        before = deepcopy(sim.runtime['executions'])
        sim.step()
        self.assertEqual(sim.runtime['executions'], before)
        self.assertEqual(sim.runtime['user_pause'], pause)
        self.assertEqual([a for a in sim.runtime['queue'] if a.get('delegation_application_id')], stages)
        applied(sim, 'resume', text='Resume my paused research.')
        for stage in ('delegation_interpret', 'delegation_check'):
            assert_event(sim, deepcopy(queued(sim, 'intent_interpretation', stage)), 'delegation', 'within_scope')
            if stage == 'delegation_interpret':
                pending = deepcopy(sim.runtime['queue'])
                applied(sim, 'request', text='Reuse the comparison already in progress.', config=config)
                self.assertEqual(sim.runtime['queue'], pending)
        app, = sim.runtime['delegation_applications'].values()
        from do_math.canonical import exact_content_hash
        original = app['basis']['original_decision']
        self.assertEqual(app['basis']['approval']['original_decision_sha256'], exact_content_hash(original))
        self.assertEqual(original['effect']['stage'], 'scope')
        self.assertEqual(original['affected'], [config['review_replacement']['action']['target']])
        self.assertEqual(app['basis']['original_source']['text'], 'Replace this scope seat from its verified records.')
        self.assertEqual(app['application']['effect'], config['review_replacement']['case']['effect'])
        self.assertEqual(len({j['execution_id'] for j in app['judgments'].values()}), 2)
        observations = [row for row in sim.model.responder.observed if row['event'] == 'delegation']
        self.assertEqual(len(observations), 2)
        self.assertEqual(observations[0]['input']['delegation_case'], observations[1]['input']['delegation_case'])
        for row in observations:
            self.assertIsNone(row['input']['interpretation_to_check'])
            self.assertNotIn('judgments', row['input']['delegation_case'])
            for field in ('recent_history', 'user_inputs', 'open_questions', 'question_links'):
                self.assertNotIn(field, row['input'])
        pending = deepcopy(sim.runtime['queue'])
        applied(sim, 'request', text='Reuse the applied case receipt.', config=config)
        self.assertEqual(sim.runtime['queue'], pending)
        self.assertEqual(len(sim.runtime['delegation_applications']), 1)
        replacement = deepcopy(queued(sim, 'identity_review', 'initial'))
        self.assertIsNotNone(replacement.get('replacement_for'))
        sim.restart()
        assert_event(sim, replacement, 'identity', 'match')
        self.assertTrue(sim.runtime['review_cycles'][replacement['review_cycle_id']]['replacement_receipts'])
        saved = deepcopy((sim.instance['decisions'], sim.runtime['delegation_applications']))
        sim.restart()
        self.assertEqual((sim.instance['decisions'], sim.runtime['delegation_applications']), saved)

    def test_public_case_rejects_changed_slot_cause_and_cycle_before_judgments(self):
        from support.governance_delegation import public_replacement_case
        sim, config = public_replacement_case()
        before = deepcopy((sim.instance['decisions'], sim.instance['delegations'], sim.runtime['queue']))
        for field, value in (('slot', 'other-seat'), ('round', 99), ('review_cycle_id', 'RC-other'),
                             ('replacement_for', 99), ('continuity_break_cause', 'another failure')):
            with self.subTest(field=field):
                damaged = deepcopy(config)
                damaged['review_replacement']['case']['effect'][field] = value
                receipt = sim.control('request', text='Compare this replacement.', config=damaged)
                sim.engine.process_controls()
                result = sim.engine.control_result(receipt['request_id'])
                self.assertEqual((result['effect'], result['reason']), ('rejected',
                    'delegated recovery case differs from the actual review slot'))
                self.assertFalse(sim.runtime.get('delegation_applications'))
                self.assertEqual((sim.instance['decisions'], sim.instance['delegations'], sim.runtime['queue']), before)

    def test_actual_engine_delegation_control_to_independent_judgments_effect_and_receipt(self):
        from support.entry import entry
        _entry = entry()
        with tempfile.TemporaryDirectory() as root:
            scene = ReviewScene(root)
            engine = scene.engine
            grant_replacement(engine)
            cid = scene.start('K1')
            action = deepcopy(scene.pending())
            engine._record_review_recovery(action, ValueError('permanent_loss'), retryable=False)
            from support.governance_delegation import original_replacement
            original_replacement(engine, action)
            engine.instance, engine.runtime, _ = gov.apply_decision(engine.instance, engine.runtime,
                {'kind': 'delegation', 'decision_id': 'DD', 'delegation': {'id': 'DG', 'status': 'active',
                 'decision_kind': 'review_replacement', 'original_decision_id': 'ORIGINAL',
                 'included_targets': ['K1'], 'excluded_targets': [], 'external_effects': [],
                 'resource_limits': {}, 'expires_at': None}}, source_ref='SOURCE-review', clock=_entry.ports.clock)
            effect = {**{key: action[key] for key in ('review_cycle_id', 'stage', 'slot', 'round')},
                      'replacement_for': 0, 'continuity_break_cause': 'permanent_loss'}
            case = {'id': 'CASE', 'decision_kind': 'review_replacement', 'target_id': 'K1',
                    'external_effects': [], 'resources': {}, 'effect': effect, 'basis_refs': [cid]}
            request = {'id': 'REQUEST', 'action': 'request', 'config': {'role': 'maintenance', 'review_replacement': {
                'action': action, 'grant_id': 'GR-review', 'delegation_id': 'DG', 'case': case}}}
            engine.runtime.setdefault('history', []).append({'kind': 'user_control', 'request': request})
            self.assertTrue(engine._review_recovery_control(request))
            stages = [a for a in engine.runtime['queue'] if a.get('delegation_application_id')]
            self.assertEqual(len(stages), 2)
            app_id = stages[0]['delegation_application_id']
            shared = d.judgment_input(engine.runtime, app_id)
            before_authority = deepcopy({key: engine.instance.get(key) for key in ('decisions', 'grants', 'delegations')})
            for index, stage in enumerate(stages):
                self.assertEqual(d.judgment_input(engine.runtime, app_id), shared)
                eid = 'DG-' + str(index)
                engine.runtime['executions'][eid] = {'id': eid, 'role': 'intent_interpretation', 'status': 'ended',
                    'input_sha256': 'full-context-' + eid, 'delegation_input_sha256': shared['input_sha256']}
                engine._apply_delegation_judgment(stage, {'delegation_judgment': {
                    'input_sha256': shared['input_sha256'], 'decision': 'within_scope',
                    'reason': 'Exact case is covered by original authority'}}, eid)
            app = engine.runtime['delegation_applications'][app_id]
            self.assertEqual(set(app['judgments']), {'interpret', 'check'})
            self.assertEqual(app['application']['effect'], effect)
            self.assertEqual({key: engine.instance.get(key) for key in before_authority}, before_authority)
            replacement = next(a for a in engine.runtime['queue'] if a.get('replacement_for') is not None)
            engine.runtime['queue'].remove(replacement)
            engine.runtime['queue'].insert(0, replacement)
            scene.execute(record_first=True)
            scene.execute()
            self.assertTrue(scene.usable())
            self.assertTrue(engine.runtime['review_cycles'][cid]['replacement_receipts'])


if __name__ == '__main__':
    unittest.main()
