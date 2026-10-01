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
            engine.instance['decisions']['ORIGINAL'] = {'id': 'ORIGINAL', 'actor': 'user',
                'kind': 'review_replacement', 'source_ref': 'SOURCE-review'}
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
