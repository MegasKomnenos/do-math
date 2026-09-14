from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math.review_cycle import record_turn
from do_math.review_engine import ReviewEngineMixin


class FakeEngine(ReviewEngineMixin):
    def __init__(self, root, rounds=2):
        source = 'theorem sample : 1 = 1 := rfl'
        self.instance = {'config': {'reviewers': 2, 'objection_round_limit': rounds},
            'knowledge': {'K1': {'id': 'K1', 'statement': 'One equals one', 'explanation': 'Reflexivity',
                'summary': 'A sample theorem', 'lean_code': source, 'declaration_names': ['sample'],
                'dependencies': [], 'producer_execution': 'author', 'required_reviews': 2,
                'status': 'candidate', 'reviews': [],
                'formal': {'status': 'verified', 'source_sha256': hashlib.sha256(source.encode()).hexdigest(),
                           'declarations': ['sample'], 'axioms': {'sample': []},
                           'toolchain': {'sha256': 'exact-toolchain-hash', 'version': 'test'},
                           'execution_id': 'formal-1', 'artifact_ref': 'artifacts/formal-1.json'}}}}
        self.runtime = {'queue': [], 'executions': {}, 'questions': []}
        self.head = 'snapshot-one'
        self.store = object()
        self.root = Path(root)
        self.saved = 0
        self.sequence = 0

    def _save(self, artifacts=None):
        self.saved += 1

    def _enqueue(self, role, target=None, **extra):
        action = {'role': role, **extra}
        if target is not None: action['target'] = target
        if action not in self.runtime['queue']: self.runtime['queue'].append(action)

    def pending(self):
        return next(a for a in self.runtime['queue'] if a['role'] == 'identity_review')

    def execute(self, changes=None, *, record_first=False):
        action = self.pending()
        self.sequence += 1
        execution_id = f'ex-{self.sequence}'
        workspace = self.root / execution_id / 'workspace'
        context = self._review_context(action, workspace)
        cycle = self.runtime['review_cycles'][action['review_cycle_id']]
        output = dict(proposal_digest=context['proposal_digest'], summary='Evidence-backed result',
                      used_sources=['proposal:1'], questions=[])
        stage = action['stage']
        if stage == 'initial':
            output.update(decision='match', scope_complete=True, findings=[])
        elif stage == 'organize':
            output['issues'] = [dict(id=f'issue-{len(cycle["issues"])+i}', finding_refs=[source['ref']],
                answer_role_slot_id=source['ref']['slot'] if source['ref']['stage'] == 'initial' else 'initial-0')
                for i, source in enumerate(context['pending_findings'])]
        elif stage == 'judge':
            output.update(decision='match', scope_complete=True, new_findings=[],
                issue_verdicts=[dict(issue_id=i, decision='rejected', reason='Original source refutes the objection', evidence=['proposal:1']) for i in cycle['issues']])
        elif stage == 'answer':
            output.update(new_findings=[], answers=[dict(issue_id=i, disposition='withdraw',
                statement='I misread the domain', evidence=['proposal:1']) for i in context['answer_requests']])
        output.update(changes or {})
        self.runtime['executions'][execution_id] = dict(id=execution_id, role='identity_review', action=deepcopy(action),
                                                      input_snapshot=self.head, input_sha256='actual-prompt-hash')
        if record_first:
            self._record_review_input(action, execution_id)
            self._record_review_input(action, execution_id)
        self.runtime['queue'].remove(action)
        self._apply_identity_review(action, output, execution_id)
        return context, output, execution_id


class ReviewEngineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.engine = FakeEngine(self.temp.name)

    def test_initial_match_activates_only_after_all_slots(self):
        engine = self.engine
        cycle_id = engine._start_identity_review('K1')
        self.assertEqual(engine.instance['knowledge']['K1']['status'], 'reviewing')
        self.assertEqual(len(engine.runtime['queue']), 2)
        self.assertEqual(engine._start_identity_review('K1'), cycle_id)
        self.assertEqual(len(engine.runtime['queue']), 2)
        schema = engine._review_schema(engine.pending())
        self.assertEqual(schema['properties']['proposal_digest']['enum'], [engine.runtime['review_cycles'][cycle_id]['proposal_digest']])
        engine.execute()
        self.assertFalse(engine.instance['knowledge']['K1']['identity_assessment']['effective'])
        context, _, _ = engine.execute()
        self.assertEqual(context['completed_results'], {})
        item = engine.instance['knowledge']['K1']
        self.assertEqual(item['status'], 'verified')
        self.assertEqual(item['identity_assessment']['decision'], 'match')
        self.assertTrue(item['identity_assessment']['effective'])
        self.assertEqual(len(item['reviews']), 2)
        self.assertEqual(len(item['identity_assessment']['execution_ids']), 2)
        self.assertEqual(engine.runtime['queue'][0]['role'], 'research_plan')
        self.assertEqual(json.loads(json.dumps(engine.runtime)), engine.runtime)

    def open_dispute(self):
        engine = self.engine
        cycle_id = engine._start_identity_review('K1')
        engine.execute(dict(decision='mismatch', findings=[dict(id='f', statement='The domain is wrong', evidence=['proposal:1'])]))
        engine.execute()
        self.assertEqual(engine.pending()['stage'], 'organize')
        engine.execute()
        return cycle_id

    def test_complete_rejected_objection_round_trip(self):
        cycle_id = self.open_dispute()
        engine = self.engine
        for _ in range(3): engine.execute()
        self.assertEqual((engine.pending()['stage'], engine.pending()['slot']), ('answer', 'initial-0'))
        context, _, _ = engine.execute(record_first=True)
        self.assertEqual(len([r for r in context['completed_results'].values() if r['stage'] == 'judge']), 3)
        self.assertEqual(engine.pending()['round'], 2)
        for _ in range(3): engine.execute()
        item = engine.instance['knowledge']['K1']
        self.assertEqual(item['status'], 'verified')
        self.assertEqual(item['identity_assessment']['cycle_id'], cycle_id)
        self.assertEqual(len(item['identity_assessment']['execution_ids']), 3)
        self.assertEqual(len(item['reviews']), 2)

    def test_mismatch_and_round_limit_return_precise_followup(self):
        cycle_id = self.open_dispute()
        engine = self.engine
        for _ in range(3):
            engine.execute(dict(decision='mismatch', issue_verdicts=[dict(issue_id='issue-0', decision='approved', reason='Actual mismatch in the domain', evidence=['proposal:1'])]))
        self.assertEqual(engine.instance['knowledge']['K1']['status'], 'needs_revision')
        plan = next(a for a in engine.runtime['queue'] if a['role'] == 'research_plan')
        self.assertEqual(plan['identity_review']['cycle_id'], cycle_id)
        self.assertIn('issue-0', plan['identity_review']['issues'])
        self.assertTrue(plan['identity_review']['actual_scope'])
        self.assertFalse(plan['identity_review']['effective'])
        self.engine = FakeEngine(self.temp.name, rounds=1)
        self.open_dispute()
        for _ in range(3):
            self.engine.execute(dict(decision='unresolved', issue_verdicts=[dict(issue_id='issue-0', decision='unresolved', reason='Source is ambiguous', evidence=[])]))
        self.assertEqual(self.engine.instance['knowledge']['K1']['status'], 'unresolved')
        plan = next(a for a in self.engine.runtime['queue'] if a['role'] == 'research_plan')
        self.assertTrue(plan['identity_review']['remaining_questions'])

    def test_new_revision_restarts_all_slots_and_retains_own_conversation(self):
        engine = self.engine
        first_id = engine._start_identity_review('K1')
        engine.execute()
        engine.execute()
        first = deepcopy(engine.runtime['review_cycles'][first_id])
        item = engine.instance['knowledge']['K1']
        item['explanation'] = 'Expanded proof by reflexivity'
        second_id = engine._start_identity_review('K1', previous_cycle_id=first_id)
        second = engine.runtime['review_cycles'][second_id]
        self.assertNotEqual(second['revision'], first['revision'])
        self.assertEqual(second['reviewer_slots'], first['reviewer_slots'])
        self.assertEqual(second['turns'], first['turns'])
        self.assertEqual(item['reviews'], [])
        self.assertEqual(item['status'], 'reviewing')
        self.assertFalse(item['identity_assessment']['effective'])
        context, _, _ = engine.execute()
        self.assertTrue(context['self_messages'])
        self.assertTrue(context['source_refs'])
        self.assertEqual(engine.instance['knowledge']['K1']['status'], 'reviewing')
        engine.execute()
        self.assertEqual(item['identity_assessment']['cycle_id'], second_id)
        self.assertEqual(item['status'], 'verified')
        self.assertIn(first_id, item['review_history'])
        self.assertIn(second_id, item['review_history'])

    def test_source_recovery_has_exact_bytes_hash_and_relative_path(self):
        engine = self.engine
        cycle_id = engine._start_identity_review('K1')
        cycle = engine.runtime['review_cycles'][cycle_id]
        source = dict(role='tool', content='Original source at line 12: quantifier', call='read',
                      arguments={'path': 'original.txt'}, message_id='source-1')
        engine.runtime['review_cycles'][cycle_id] = record_turn(cycle, 'initial-0', [source])
        action = engine.pending()
        workspace = engine.root / 'source-test'
        context = engine._review_context(action, workspace)
        reference = context['source_refs'][0]
        path = workspace / reference['local_path']
        self.assertTrue(path.is_file())
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), reference['sha256'])
        self.assertEqual(json.loads(path.read_bytes()), source)
        self.assertFalse(Path(reference['local_path']).is_absolute())
        self.assertNotIn(source['content'], json.dumps(context))
        self.assertEqual(context['self_messages'][0]['content']['source_ref']['local_path'], reference['local_path'])
        engine._review_context(action, workspace)
        self.assertEqual(len(engine.runtime['review_cycles'][cycle_id]['turns']['initial-0']), 1)

    def test_final_match_does_not_override_suspension_or_formal_change(self):
        for failure in ('suspended', 'source_hash', 'environment'):
            with self.subTest(failure=failure):
                engine = FakeEngine(self.temp.name)
                engine._start_identity_review('K1')
                engine.execute()
                item = engine.instance['knowledge']['K1']
                if failure == 'suspended': item['use_suspended'] = True
                elif failure == 'source_hash': item['formal']['source_sha256'] = 'changed'
                else: item['formal']['toolchain']['sha256'] = 'new-environment'
                engine.execute()
                self.assertNotEqual(item['status'], 'verified')
                self.assertFalse(item['identity_assessment']['effective'])
                self.assertEqual(item['identity_assessment']['decision'], 'match')

    def test_input_delta_is_not_a_recursive_transcript_copy(self):
        cycle_id = self.open_dispute()
        engine = self.engine
        for _ in range(3): engine.execute(record_first=True)
        engine.execute(record_first=True)
        for _ in range(3): engine.execute(record_first=True)
        cycle = engine.runtime['review_cycles'][cycle_id]
        total_messages = sum(len(messages) for messages in cycle['turns'].values())
        self.assertEqual(total_messages, 3 * len(cycle['results']))
        for messages in cycle['turns'].values():
            for message in messages:
                if message.get('kind') == 'review_request':
                    self.assertNotIn('self_messages', message['content'])
                    self.assertNotIn('proposal', message['content'])
        self.assertEqual(len({m['message_id'] for messages in cycle['turns'].values() for m in messages}), total_messages)

    def test_fresh_exact_formal_check_preserves_eligibility(self):
        engine = self.engine
        engine._start_identity_review('K1')
        engine.execute()
        item = engine.instance['knowledge']['K1']
        item['formal']['execution_id'] = 'formal-final-check'
        item['formal']['artifact_ref'] = 'artifacts/formal-final-check.json'
        engine.execute()
        self.assertEqual(item['status'], 'verified')
        self.assertEqual(item['identity_assessment']['formal_verification']['execution_id'], 'formal-final-check')

    def test_environment_transition_during_review_invalidates_old_environment_use(self):
        engine = self.engine
        item = engine.instance['knowledge']['K1']
        engine.instance['trust_environments'] = {'old': {'id': 'old', 'status': 'active'},
                                                'new': {'id': 'new', 'status': 'registered'}}
        engine.instance['active_trust_environment'] = 'old'
        item['formal'].update(trust_environment_id='old', trust_environment_status='active')
        engine._start_identity_review('K1')
        engine.execute()
        engine.instance['active_trust_environment'] = 'new'
        engine.instance['trust_environments']['old']['status'] = 'superseded'
        engine.instance['trust_environments']['new']['status'] = 'active'
        engine.execute()
        self.assertNotEqual(item['status'], 'verified')
        self.assertFalse(item['identity_assessment']['effective'])

    def test_new_judge_finding_is_assigned_answered_and_fully_judged(self):
        self.open_dispute()
        engine = self.engine
        engine.execute(dict(decision='mismatch', new_findings=[dict(id='new-source', statement='New source inconsistency', evidence=['proposal:3'])]))
        engine.execute()
        engine.execute()
        self.assertEqual(engine.pending()['stage'], 'organize')
        context, _, _ = engine.execute()
        self.assertEqual(context['pending_findings'][0]['ref']['slot'], 'judge-0')
        self.assertEqual(engine.pending()['stage'], 'answer')
        context, _, _ = engine.execute()
        self.assertEqual(set(context['answer_requests']), {'issue-0', 'issue-1'})
        for _ in range(3): engine.execute()
        self.assertEqual(engine.instance['knowledge']['K1']['status'], 'verified')

    def test_mutated_proposal_and_old_action_are_rejected(self):
        engine = self.engine
        cycle_id = engine._start_identity_review('K1')
        old_action = deepcopy(engine.pending())
        engine.instance['knowledge']['K1']['lean_code'] += '\n-- changed during review'
        with self.assertRaisesRegex(ValueError, 'sealed mathematical proposal'):
            engine._review_schema(old_action)
        engine.instance['knowledge']['K1']['lean_code'] = engine.runtime['review_cycles'][cycle_id]['proposal']['lean_code']
        engine.execute()
        engine.execute()
        engine._start_identity_review('K1', previous_cycle_id=cycle_id)
        with self.assertRaisesRegex(ValueError, 'superseded'):
            engine._review_schema(old_action)


if __name__ == '__main__':
    unittest.main()
