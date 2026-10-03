"""실제 작업자·수신·저장을 마친 검토 증거의 한 필드 변조를 거부한다."""
from copy import deepcopy
import unittest

from do_math import review_cycle as rc
from support.review_sim import reviewed_sim, cycle_of, warm_reviewed
from support.review_transition_inputs import replace_path


def setUpModule():
    warm_reviewed()


class StoredEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.sim = reviewed_sim()
        self.cycle = deepcopy(cycle_of(self.sim))
        self.runtime = deepcopy(self.sim.runtime)
        self.instance = deepcopy(self.sim.instance)
        self.entry = next(e for e in self.cycle['results'].values() if e['action']['stage'] == 'initial')
        self.eid = self.entry['execution_id']
        self.action = self.entry['action']

    def replay(self, cycle=None, runtime=None):
        return rc.validate_sealed_review(self.cycle if cycle is None else cycle,
            self.runtime if runtime is None else runtime, instance=self.instance,
            read_artifact=self.sim.engine.store.read, git_dir=self.sim.engine.store.git_dir,
            clock=self.sim.clock, at=self.sim.clock.now())

    def assert_replay_rejected(self, cycle, reason, runtime=None):
        runtime = self.runtime if runtime is None else runtime
        before = deepcopy((cycle, runtime, self.instance))
        head = self.sim.engine.head
        with self.assertRaisesRegex(ValueError, reason):
            self.replay(cycle, runtime)
        self.assertEqual((cycle, runtime, self.instance), before)
        self.assertEqual(self.sim.engine.head, head)

    def test_real_sealed_review_replays_exact_result_fields_without_writes(self):
        before = deepcopy((self.cycle, self.runtime, self.instance))
        head = self.sim.engine.head
        replayed = self.replay()
        for field in ('status', 'decision', 'phase', 'results', 'sealed', 'issues', 'findings', 'scope_assessment'):
            self.assertEqual(replayed[field], self.cycle[field], field)
        self.assertEqual(replayed['decision'], 'match')
        self.assertEqual((self.cycle, self.runtime, self.instance), before)
        self.assertEqual(self.sim.engine.head, head)

    def test_replay_rejects_unfinished_or_unnamed_cycle(self):
        for field, value in [('id', ''), ('status', 'working'), ('decision', None)]:
            with self.subTest(field=field):
                self.assert_replay_rejected({**self.cycle, field: value}, 'not a completely sealed finite cycle')

    def test_replay_rejects_recursion_and_changed_proposal(self):
        with self.assertRaisesRegex(ValueError, 'not a completely sealed finite cycle'):
            rc.validate_sealed_review(self.cycle, self.runtime, _seen=(self.cycle['id'],), clock=self.sim.clock, at=self.sim.clock.now())
        changed = replace_path(self.cycle, ['proposal', 'statement'], '변조')
        self.assert_replay_rejected(changed, 'sealed proposal changed')

    def test_replay_rejects_removed_seal(self):
        key = next(k for k, e in self.cycle['results'].items() if e['action']['stage'] == 'initial')
        self.assert_replay_rejected({**self.cycle, 'sealed': [k for k in self.cycle['sealed'] if k != key]}, 'review is not completely sealed')

    def test_replay_rejects_changed_conclusion(self):
        self.assert_replay_rejected({**self.cycle, 'decision': 'mismatch'}, 'review conclusion differs from sealed evidence')

    def test_binding_rejects_each_changed_execution_coordinate(self):
        for path, value in [(['role'], 'maintenance'), (['action', 'review_cycle_id'], 'other'),
                (['action', 'slot'], 'other'), (['status'], 'queued'), (['outcome'], 'cancelled'),
                (['output'], {**self.entry['output'], 'summary': '변조'})]:
            changed = replace_path(self.runtime, ['executions', self.eid, *path], value)
            before = deepcopy(changed)
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, 'not bound to its actual accepted execution'):
                rc.validate_review_binding(self.cycle, changed, self.eid, self.action, self.entry['output'])
            self.assertEqual(changed, before)

    def test_binding_rejects_profile_for_another_ai_role(self):
        from do_math.execution_profiles import profile_ref
        profile = next(p for p in self.instance['execution_profiles'].values() if p['role'] == 'research_plan')
        changed = replace_path(self.runtime, ['executions', self.eid, 'execution_profile_ref'], profile_ref(profile))
        with self.assertRaisesRegex(ValueError, 'profile does not belong to its actual AI role'):
            rc.validate_review_binding(self.cycle, changed, self.eid, self.action, self.entry['output'], instance=self.instance)
        self.assertEqual(changed['executions'][self.eid]['execution_profile_ref'], profile_ref(profile))

    def test_binding_requires_ai_actor(self):
        changed = replace_path(self.runtime, ['executions', self.eid, 'actor_kind'], 'machine')
        with self.assertRaisesRegex(ValueError, 'profile does not belong to its actual AI role'):
            rc.validate_review_binding(self.cycle, changed, self.eid, self.action, self.entry['output'], instance=self.instance)

    def test_binding_rejects_snapshot_and_prompt_hash_changes(self):
        for field, value in [('input_snapshot', '0' * 40), ('input_sha256', '0' * 64)]:
            changed = replace_path(self.cycle, ['input_bindings', self.eid, field], value)
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, 'input binding does not match the actual execution'):
                rc.validate_review_binding(changed, self.runtime, self.eid, self.action, self.entry['output'])

    def test_binding_rejects_proposal_slot_and_profile_changes(self):
        for field, value in [('proposal_digest', '0' * 64), ('role_slot_id', 'other'), ('profile_ref', None)]:
            changed = replace_path(self.cycle, ['input_bindings', self.eid, field], value)
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, 'profile or proposal binding changed'):
                rc.validate_review_binding(changed, self.runtime, self.eid, self.action, self.entry['output'])
        changed = replace_path(self.cycle, ['slot_profiles', self.action['slot']], None)
        with self.assertRaisesRegex(ValueError, 'profile or proposal binding changed'):
            rc.validate_review_binding(changed, self.runtime, self.eid, self.action, self.entry['output'])

    def test_incomplete_binding_is_explicit_and_returns_actual_record(self):
        for outcome in ('execution_incomplete', 'cancelled', 'start_failed'):
            changed = replace_path(self.runtime, ['executions', self.eid, 'outcome'], outcome)
            with self.subTest(outcome=outcome):
                result = rc.validate_review_binding(self.cycle, changed, self.eid, self.action,
                    self.entry['output'], allow_incomplete=True)
                self.assertIs(result, changed['executions'][self.eid])
                self.assertEqual(result['outcome'], outcome)

    def test_missing_context_origin_is_rejected(self):
        changed = replace_path(self.runtime, ['executions', self.eid, 'context_origin'], ['missing-execution'])
        with self.assertRaisesRegex(ValueError, 'review context lineage does not resolve'):
            rc.validate_review_independence(self.cycle, changed, self.eid, self.action)

    def test_peer_context_origin_is_rejected(self):
        peer = next(e['execution_id'] for e in self.cycle['results'].values()
                    if e['action']['stage'] == 'initial' and e['execution_id'] != self.eid)
        changed = replace_path(self.runtime, ['executions', self.eid, 'context_origin'], [peer])
        with self.assertRaisesRegex(ValueError, 'logical review slot inherited private peer context'):
            rc.validate_review_independence(self.cycle, changed, self.eid, self.action)

    def test_ancestor_author_is_rejected_even_through_context_origin(self):
        author = next(eid for eid, row in self.runtime['executions'].items() if row.get('actor_kind') == 'machine')
        changed = replace_path(self.runtime, ['executions', self.eid, 'context_origin'], [author])
        with self.assertRaisesRegex(ValueError, 'review inherited original author context'):
            rc.validate_review_independence(self.cycle, changed, self.eid, self.action, excluded_execution_ids=[author])

    def test_identity_receipt_names_only_final_review_executions(self):
        receipt = rc.identity_assessment(self.cycle, reason='완전한 검토')
        expected = [entry['execution_id'] for entry in self.cycle['results'].values() if entry['action']['stage'] == 'initial']
        self.assertEqual(receipt, {'review_cycle_id': self.cycle['id'], 'proposal_digest': self.cycle['proposal_digest'],
            'decision': 'match', 'execution_ids': expected, 'scope_complete': True, 'summary': '완전한 검토'})

    def test_engine_result_rejection_rolls_back_memory_and_preserves_head(self):
        engine = self.sim.engine
        action = deepcopy(engine.runtime['executions'][self.eid]['action'])
        action['slot'] = 'other'
        before = deepcopy((engine.instance, engine.runtime))
        head = engine.head
        with self.assertRaisesRegex(ValueError, 'execution was assigned to a different review action'):
            engine._apply_identity_review(action, self.entry['output'], self.eid)
        self.assertEqual((engine.instance, engine.runtime), before)
        self.assertEqual(engine.head, head)

    def test_completed_review_is_obsolete_without_enqueuing_a_second_review(self):
        engine = self.sim.engine
        action = deepcopy(engine.runtime['executions'][self.eid]['action'])
        before = deepcopy(engine.runtime)
        self.assertEqual(engine._obsolete_review_reason(action), 'The assigned review ended or its proposal revision was superseded')
        self.assertEqual(engine.runtime, before)
