"""Identity reviews in the engine: cycles, scope budgets, preparation failures, input overflow, impact reviews, reassessment and delegation."""
import errno
import hashlib
import json
import sys
import tempfile
import threading
import unittest
import uuid
from copy import deepcopy
from pathlib import Path
from unittest.mock import create_autospec, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math import (execution_profiles, governance, knowledge, knowledge_io, knowledge_records as kr,
                     review_cycle, review_policy)
from do_math.configuration import DEFAULT_CONFIG
from do_math.engine import control, ResearchEngine
from do_math.system_clock import now
from do_math.canonical import canonical_json, exact_content_hash
from do_math.repository import ResearchRepository
from do_math.system_clock import new_id
from do_math.review_cycle import record_turn
from engine_fixtures import formal_check_engine, formal_verification, routing_engine
from purpose_fixtures import ActivatedPurposeHarness, theorem
from research_fixtures import bare_engine, current_state, git_init, scope_assessment, start_scoped_review
from review_fixtures import grant_replacement, ReviewFakeEngine
from state_fixtures import owner_calls, start_active_copy, start_model_call


class ReviewEngineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.engine = ReviewFakeEngine(self.temp.name)

    def test_adopted_instance_policy_is_the_only_opening_and_publication_policy(self):
        engine = self.engine
        approved = deepcopy(engine.instance['review_policy'])
        approved.update(id='ADOPTED', minimum_initial_slots=3,
                        required_perspectives=['formal', 'semantic', 'scope'], activity_execution_limit=18)
        engine.instance['review_policy'] = approved
        cid = engine._start_identity_review('K1')
        self.assertEqual(engine.runtime['review_cycles'][cid]['review_policy'], approved)
        context = engine._prepare_review_context(engine.pending(), engine.root / 'scope')['context']
        self.assertEqual(context['review_policy'], approved)
        engine.instance['review_policy']['activity_execution_limit'] = 19
        with self.assertRaisesRegex(ValueError, 'publication premises'):
            engine._review_cycle(engine.pending())
        with self.assertRaisesRegex(ValueError, 'publication premises'):
            engine._start_identity_review('K1')

    def test_kernel_evidence_outside_the_reviewed_projection_still_binds_publication(self):
        engine = self.engine
        cid = engine._start_identity_review('K1')
        sealed = deepcopy(engine.runtime['review_cycles'][cid]['proposal'])
        formal = engine.instance['formal_results'][engine.instance['knowledge']['K1']['formal_result_id']]
        formal['verification']['declaration_evidence']['sample']['value'] = 'another proof term'
        self.assertEqual(review_cycle.review_proposal(engine.instance, 'K1'), sealed)
        with self.assertRaisesRegex(ValueError, 'publication premises'):
            engine._review_cycle(engine.pending())

    def test_v5_missing_adopted_policy_does_not_use_config_default(self):
        engine = self.engine
        engine.instance.pop('review_policy', None)
        with self.assertRaisesRegex(ValueError, 'adopted review policy'):
            engine._start_identity_review('K1')

    def test_admission_counts_failed_and_retried_executions_before_results(self):
        engine = self.engine
        from do_math.review_policy import minimum_scope_executions
        limit = minimum_scope_executions(2, 2)
        engine.instance['review_policy']['activity_execution_limit'] = limit
        cid = engine.start('K1', scope={**engine.scope, 'activity_execution_limit': limit})
        action = engine.pending()
        attempts = [f'attempt-{number}' for number in range(1, limit + 1)]
        for eid in attempts:
            execution = {'id': eid, 'actor_kind': 'ai', 'owner_activity_id': 'AY', 'status': 'queued'}
            self.assertEqual(engine._admit_review_execution(action, execution)['disposition'], 'admitted')
            self.assertEqual(engine._admit_review_execution(action, execution)['disposition'], 'already_admitted')
            execution['status'] = 'ended'
            engine.runtime['executions'][eid] = execution
        denied = engine._admit_review_execution(action, {'id': 'attempt-extra', 'actor_kind': 'ai', 'owner_activity_id': 'AY'})
        self.assertEqual(denied['disposition'], 'review_budget_exhausted')
        self.assertEqual(engine.runtime['review_cycles'][cid]['execution_accounting']['executions_used'], attempts)
        self.assertEqual(engine.runtime['review_cycles'][cid]['results'], {})

    def test_optional_research_cannot_consume_mandatory_followup_reservations(self):
        engine = self.engine
        engine.instance['review_policy']['activity_execution_limit'] = 12
        cid = engine.start('K1', scope={**engine.scope, 'activity_execution_limit': 12})
        action = {**engine.pending(), 'role': 'supplemental_research', 'stage': 'investigating', 'research_request_id': 'R'}
        denied = engine._admit_review_execution(action, {'id': 'optional', 'actor_kind': 'ai', 'owner_activity_id': 'AY'})
        self.assertEqual(denied['disposition'], 'review_followup_reserved')
        stages = {row['stage'] for row in denied['reserved_execution_slots']}
        self.assertTrue({'initial', 'organize', 'answer', 'judge'} <= stages)
        self.assertEqual(engine.runtime['review_cycles'][cid]['execution_accounting']['executions_used'], [])

    def test_admission_cannot_reseal_changed_policy_or_scope(self):
        engine = self.engine
        cid = engine.start('K1')
        cycle = engine.runtime['review_cycles'][cid]
        cycle['activity_execution_limit'] += 1
        with self.assertRaisesRegex(ValueError, 'review inputs changed'):
            engine._admit_review_execution(engine.pending(), {'id': 'stale', 'actor_kind': 'ai', 'owner_activity_id': 'AY'})
        self.assertEqual(cycle['execution_accounting']['executions_used'], [])

    def test_actual_prompt_and_public_provider_events_restore_only_to_their_slot(self):
        engine = self.engine
        cid = engine.start('K1')
        action = deepcopy(engine.pending())
        engine.runtime['executions']['PUBLIC'] = {'id': 'PUBLIC', 'role': 'identity_review', 'action': action}
        prompt = 'Exact rendered input including the provider boundary.'
        engine._record_review_prompt('PUBLIC', prompt, artifact_ref='runtime/artifacts/PUBLIC/input.txt')
        events = [
            {'type': 'item.completed', 'item': {'type': 'reasoning', 'text': 'HIDDEN'}},
            {'type': 'item.completed', 'item': {'type': 'agent_message', 'text': 'PUBLIC EXPLANATION'}},
            {'type': 'item.completed', 'item': {'type': 'command_execution', 'command': 'read source',
                                               'aggregated_output': 'EXACT TOOL OUTPUT', 'exit_code': 0}},
        ]
        for index, event in enumerate(events):
            engine._record_review_observation('PUBLIC', event, artifact_ref='runtime/artifacts/PUBLIC/stdout.jsonl', event_index=index)
            engine._record_review_observation('PUBLIC', event, artifact_ref='runtime/artifacts/PUBLIC/stdout.jsonl', event_index=index)
        cycle = engine.runtime['review_cycles'][cid]
        self.assertEqual(len(cycle['turns'][action['slot']]), 3)
        self.assertNotIn('HIDDEN', json.dumps(cycle['turns']))
        own = engine._prepare_review_context(action, engine.root / 'own')['context']
        self.assertIn('PUBLIC EXPLANATION', json.dumps(own))
        contents = [(engine.root / 'own' / row['local_path']).read_text(encoding='utf-8') for row in own['source_refs']]
        self.assertTrue(any(prompt in text for text in contents))
        self.assertTrue(any('EXACT TOOL OUTPUT' in text for text in contents))
        peer = next(a for a in engine.runtime['queue'] if a['slot'] != action['slot'])
        peer_context = engine._prepare_review_context(peer, engine.root / 'peer')['context']
        self.assertNotIn('PUBLIC EXPLANATION', json.dumps(peer_context))
        self.assertEqual(peer_context['source_refs'], [])

    def test_observed_public_events_reject_out_of_order_append_but_allow_exact_replay(self):
        engine = self.engine
        engine.start('K1')
        engine.runtime['executions']['ORDER'] = {'id': 'ORDER', 'action': deepcopy(engine.pending())}
        event = {'type': 'public_message', 'message': {'role': 'assistant', 'content': 'later message'}}
        engine._record_review_observation('ORDER', event, artifact_ref='events.jsonl', event_index=3)
        engine._record_review_observation('ORDER', event, artifact_ref='events.jsonl', event_index=3)
        with self.assertRaisesRegex(ValueError, 'out of order'):
            engine._record_review_observation('ORDER', event, artifact_ref='events.jsonl', event_index=1)

    def test_public_provider_numbers_survive_storage_and_slot_restoration(self):
        from do_math.canonical import canonical_json
        from do_math.review_cycle import validate_transcript
        engine = self.engine
        cid = engine.start('K1')
        action = deepcopy(engine.pending())
        engine.runtime['executions']['NUMBERS'] = {'id': 'NUMBERS', 'action': action}
        events = []
        for value in (0.25, 2 ** 53):
            events.extend([
                {'type': 'assistant', 'message': {'content': [{'type': 'text', 'text': 'Observed value'}],
                                                'usage': {'reported': value}}},
                {'type': 'item.completed', 'item': {'type': 'mcp_tool_call', 'id': str(len(events)),
                    'arguments': {'threshold': value}, 'result': {'estimate': value}}},
                {'type': 'assistant', 'message': {'content': [{'type': 'tool_use', 'id': 'tool',
                    'name': 'calculate', 'input': {'threshold': value}}]}},
                {'type': 'public_message', 'message': {'role': 'tool', 'content': 'Returned value',
                    'arguments': {'threshold': value}}},
            ])
        original = deepcopy(events)
        for index, event in enumerate(events):
            for _ in range(2):
                engine._record_review_observation('NUMBERS', event,
                    artifact_ref='runtime/artifacts/NUMBERS/events.jsonl', event_index=index)
        self.assertEqual(events, original)
        cycle = json.loads(canonical_json(engine.runtime['review_cycles'][cid]))
        engine.runtime['review_cycles'][cid] = cycle
        turns, _ = validate_transcript(cycle, action['slot'])
        self.assertEqual(len(turns), len(events))
        for offset, value in ((0, 0.25), (4, 2 ** 53)):
            self.assertEqual(turns[offset]['content'], 'Observed value')
            self.assertEqual(json.loads(turns[offset + 1]['content'])['result']['estimate'], value)
            self.assertEqual(json.loads(turns[offset + 2]['content'])['input']['threshold'], value)
            self.assertEqual(json.loads(turns[offset + 3]['arguments'])['threshold'], value)
        restored = engine._prepare_review_context(action, engine.root / 'numeric-restoration')['context']
        self.assertEqual(len(restored['self_messages']), len(events))
        for reference in restored['source_refs']:
            raw = (engine.root / 'numeric-restoration' / reference['local_path']).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), reference['sha256'])
            self.assertEqual(json.loads(raw), turns[reference['index']])

    def test_restore_diagnostics_keep_exact_coordinate_hashes_and_verified_prefix(self):
        engine = self.engine
        cid = engine.start('K1')
        action = engine.pending()
        cycle = record_turn(engine.runtime['review_cycles'][cid], action['slot'], [
            {'role': 'assistant', 'content': 'verified first'}, {'role': 'assistant', 'content': 'original second'}])
        expected = cycle['transcript_manifest'][action['slot']][1]['sha256']
        cycle['turns'][action['slot']][1]['content'] = 'changed second'
        engine.runtime['review_cycles'][cid] = cycle
        outcome = engine._prepare_review_context(action, engine.root / 'broken')
        event = outcome['recovery']['recovery_event']
        self.assertEqual(event['cause_kind'], 'content_mismatch')
        self.assertEqual(event['coordinate'], {'slot': action['slot'], 'index': 1})
        self.assertEqual(event['expected_sha256'], expected)
        self.assertNotEqual(event['expected_sha256'], event['observed_sha256'])
        self.assertEqual(event['preserved_range']['verified_indices'], [0])
        self.assertFalse(event['retryable'])
        self.assertFalse(event['continuity_broken'])  # mismatch is not proof that every original copy is lost
        again = engine._prepare_review_context(action, engine.root / 'broken')
        self.assertEqual(again['recovery']['recovery_event'], event)
        self.assertEqual(len(engine.runtime['review_cycles'][cid]['recovery_events']), 1)

    def test_tampered_materialized_source_records_the_exact_file_hashes(self):
        engine = self.engine
        cid = engine.start('K1'); action = engine.pending()
        engine.runtime['review_cycles'][cid] = record_turn(engine.runtime['review_cycles'][cid], action['slot'],
            [{'role': 'tool', 'content': 'exact original'}])
        workspace = engine.root / 'source'
        context = engine._prepare_review_context(action, workspace)['context']
        ref = context['source_refs'][0]
        (workspace / ref['local_path']).write_bytes(b'changed file')
        event = engine._prepare_review_context(action, workspace)['recovery']['recovery_event']
        self.assertEqual(event['expected_sha256'], ref['sha256'])
        self.assertEqual(event['observed_sha256'], hashlib.sha256(b'changed file').hexdigest())
        self.assertEqual(event['coordinate']['path'], str(workspace / ref['local_path']))

    def test_temporary_io_failure_preserves_reason_and_can_be_retried(self):
        import errno
        from unittest.mock import patch
        engine = self.engine
        engine.start('K1')
        with patch.object(engine, '_build_review_context', side_effect=OSError(errno.EAGAIN, 'sharing temporarily unavailable', 'source.json')):
            outcome = engine._prepare_review_context(engine.pending(), engine.root / 'temporary')
        event = outcome['recovery']['recovery_event']
        self.assertTrue(event['retryable'])
        self.assertIn('sharing temporarily unavailable', event['reason'])
        self.assertEqual(event['coordinate']['path'], 'source.json')

    def test_central_replacement_control_releases_wait_and_queues_next_execution(self):
        from do_math.engine import ResearchEngine
        from do_math import activities
        engine = self.engine
        grant_replacement(engine)
        cid = engine.start('K1')
        action = deepcopy(engine.pending())
        action.update(id='AC-held', owner_activity_id='AY-held')
        engine._prepare_review_context(action, engine.root / 'initial')
        recovery = engine._record_review_recovery(action, ValueError('permanent_loss'), retryable=False)
        activities.open_activity(engine.runtime, activity_id='AY-held', activity_kind='identity_review',
                                 owner_ref=cid, input_refs=['K1'], opened_at='now')
        activities.wait_for(engine.runtime, 'AY-held', reason='review_input_restoration',
                            condition={'kind': 'review_recovery', 'recovery': recovery}, next_owner='governance', at='now')
        engine.runtime['waiting_actions'] = {'AC-held': {'kind': 'review_input_restoration', 'action': action, 'recovery': recovery}}
        engine.runtime['queue'] = []
        request = {'action': 'request', 'config': {'role': 'maintenance', 'review_replacement': {'action': action, 'grant_id': 'GR-review'}}}
        self.assertTrue(ResearchEngine._review_recovery_control(engine, request))
        self.assertNotIn('AC-held', engine.runtime['waiting_actions'])
        self.assertEqual(engine.runtime['activities']['AY-held']['status'], 'ready')
        replacement = next(a for a in engine.runtime['queue'] if a.get('replacement_for') is not None)
        self.assertEqual(replacement['owner_activity_id'], 'AY-held')
        self.assertEqual(engine._prepare_review_context(replacement, engine.root / 'next')['disposition'], 'ready')

    def test_restored_exact_bytes_release_the_held_slot_without_a_replacement(self):
        engine = self.engine
        cid = engine.start('K1')
        action = deepcopy(engine.pending()); action['id'] = 'AC-held'
        good = record_turn(engine.runtime['review_cycles'][cid], action['slot'], [{'role': 'assistant', 'content': 'original'}])
        engine.runtime['review_cycles'][cid] = deepcopy(good)
        engine.runtime['review_cycles'][cid]['turns'][action['slot']][0]['content'] = 'corrupt'
        outcome = engine._prepare_review_context(action, engine.root / 'broken')
        engine.runtime['waiting_actions'] = {'AC-held': {'kind': 'review_input_restoration', 'action': action, 'recovery': outcome['recovery']}}
        engine.runtime['queue'] = []
        engine.runtime['review_cycles'][cid]['turns'] = deepcopy(good['turns'])
        resumed = engine._retry_review_restoration(action, engine.root / 'restored', at='now')
        self.assertEqual(resumed['disposition'], 'review_resumed')
        self.assertEqual(engine.runtime['waiting_actions'], {})
        self.assertTrue(engine.runtime['queue'])
        self.assertEqual(engine.runtime['review_cycles'][cid]['continuity_events'], [])

    def staged_transition(self):
        engine = self.engine
        engine.instance['trust_environments']['TE-next'] = {'id': 'TE-next', 'status': 'registered',
            'toolchain': {'sha256': 'new-toolchain', 'version': 'next'}, 'allowed_axioms': []}
        transition = knowledge.begin_transition(engine.instance, 'TE-next')
        fid = engine.instance['knowledge']['K1']['formal_result_id']
        result = deepcopy(engine.instance['formal_results'][fid]['verification'])
        result.update(id='K1', toolchain=engine.instance['trust_environments']['TE-next']['toolchain'])
        result['declaration_evidence']['sample']['value'] = 'staged verified proof'
        transition = knowledge.record_transition_result(engine.instance, transition, result)
        engine.runtime['trust_transitions'] = {transition['id']: transition}
        return transition['id']

    def test_staged_candidate_uses_the_same_scope_cycle_without_publication(self):
        engine = self.engine
        transition_id = self.staged_transition()
        before = deepcopy(engine.instance)
        cid = engine._start_staged_identity_review(transition_id, 'K1')
        self.assertEqual(engine.pending()['stage'], 'scope')
        cycle = engine.runtime['review_cycles'][cid]
        self.assertEqual(cycle['proposal']['formal']['toolchain'], engine.instance['trust_environments']['TE-next']['toolchain'])
        engine.execute(); engine.execute(); engine.execute()
        self.assertEqual(engine.instance, before)
        receipt = engine._completed_staged_identity_review(transition_id, 'K1', cid)
        self.assertEqual(receipt['decision'], 'match')
        self.assertEqual(receipt['review_cycle_id'], cid)
        self.assertEqual(receipt['transition_basis'], cycle['staged_candidate']['transition_basis'])
        engine.runtime['trust_transitions'][transition_id]['results']['K1']['declaration_evidence']['sample']['value'] = 'changed'
        with self.assertRaisesRegex(ValueError, 'staged'):
            engine._completed_staged_identity_review(transition_id, 'K1', cid)

    def test_completed_staged_review_is_consumed_by_transition_activation(self):
        engine = self.engine
        transition_id = self.staged_transition()
        before = deepcopy(engine.instance)
        cid = engine._start_staged_identity_review(transition_id, 'K1')
        engine.execute(); engine.execute(); engine.execute()
        receipt = engine._completed_staged_identity_review(transition_id, 'K1', cid)
        candidate = deepcopy(engine.runtime['trust_transitions'][transition_id])
        candidate['results']['K1']['identity_review'] = receipt

        activated = knowledge.activate_transition(engine.instance, candidate, runtime=engine.runtime)

        self.assertEqual(activated['active_trust_environment'], candidate['to_environment'])
        current = activated['knowledge']['K1']
        self.assertNotEqual(current['formal_result_id'], before['knowledge']['K1']['formal_result_id'])
        self.assertNotEqual(current['exposition_id'], before['knowledge']['K1']['exposition_id'])
        self.assertEqual(activated['formal_results'][current['formal_result_id']]['supersedes'],
                         before['knowledge']['K1']['formal_result_id'])
        self.assertEqual(activated['expositions'][current['exposition_id']]['supersedes'],
                         before['knowledge']['K1']['exposition_id'])
        assessment = next(row for row in activated['identity_assessments'].values()
                          if row.get('review_cycle_id') == cid)
        self.assertEqual(assessment['execution_ids'], receipt['execution_ids'])
        self.assertEqual(assessment['formal_result_id'], current['formal_result_id'])
        self.assertEqual(assessment['exposition_id'], current['exposition_id'])
        self.assertTrue(any(use['assessment_id'] == assessment['id'] and use['status'] == 'active'
                            for use in activated['assessment_uses'].values()))
        self.assertEqual(engine.instance, before)

    def test_staged_activation_rejects_tampered_receipt_and_stale_policy(self):
        engine = self.engine
        transition_id = self.staged_transition()
        cid = engine._start_staged_identity_review(transition_id, 'K1')
        engine.execute(); engine.execute(); engine.execute()
        receipt = engine._completed_staged_identity_review(transition_id, 'K1', cid)

        forged = deepcopy(engine.runtime['trust_transitions'][transition_id])
        forged['results']['K1']['identity_review'] = {**receipt, 'proposal_digest': '0' * 64}
        before = deepcopy(engine.instance)
        with self.assertRaisesRegex(ValueError, 'receipt'):
            knowledge.activate_transition(engine.instance, forged, runtime=engine.runtime)
        self.assertEqual(engine.instance, before)

        for field, value in (('transition_id', 'TR-another'), ('knowledge_id', 'K-another')):
            wrong_owner = deepcopy(engine.runtime['trust_transitions'][transition_id])
            wrong_owner['results']['K1']['identity_review'] = {**receipt, field: value}
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, 'receipt|another transition target'):
                knowledge.activate_transition(engine.instance, wrong_owner, runtime=engine.runtime)
            self.assertEqual(engine.instance, before)

        stale_instance = deepcopy(engine.instance)
        stale_instance['review_policy']['round_limit'] += 1
        stale_before = deepcopy(stale_instance)
        candidate = deepcopy(engine.runtime['trust_transitions'][transition_id])
        candidate['results']['K1']['identity_review'] = receipt
        with self.assertRaisesRegex(ValueError, 'publication premises'):
            knowledge.activate_transition(stale_instance, candidate, runtime=engine.runtime)
        self.assertEqual(stale_instance, stale_before)

    def _staged_activation_git_round_trip(self, *, followup_transition):
        engine = self.engine
        from research_fixtures import trust_environment, trust_fixture
        old_fixture = trust_fixture(Path(self.temp.name), ['old-lean'])
        old_environment, old_binding = trust_environment(old_fixture, environment_id='TE-review',
                                                         source_ref='fixture:old-trust-environment')
        engine.instance['trust_environments']['TE-review'] = old_environment
        formal = engine.instance['formal_results'][engine.instance['knowledge']['K1']['formal_result_id']]
        formal['verification'].update(toolchain=deepcopy(old_environment['toolchain']),
                                      allowed_axioms=deepcopy(old_environment['allowed_axioms']))
        next_fixture = trust_fixture(Path(self.temp.name), ['next-lean'])
        next_environment, next_binding = trust_environment(next_fixture, environment_id='TE-next', status='registered',
                                                           source_ref='fixture:next-trust-environment')
        engine.instance['trust_environments']['TE-next'] = next_environment
        engine.runtime['trust_bindings'] = {'TE-review': old_binding, 'TE-next': next_binding}
        transition = knowledge.begin_transition(engine.instance, 'TE-next')
        result = deepcopy(formal['verification'])
        result.update(id='K1', toolchain=deepcopy(next_fixture['toolchain']),
                      allowed_axioms=deepcopy(next_fixture['allowed_axioms']))
        result['declaration_evidence']['sample']['value'] = 'staged verified proof'
        transition = knowledge.record_transition_result(engine.instance, transition, result)
        transition_id = transition['id']
        engine.runtime['trust_transitions'] = {transition_id: transition}
        before = deepcopy(engine.instance)
        cid = engine._start_staged_identity_review(transition_id, 'K1')
        engine.execute(); engine.execute(); engine.execute()
        receipt = engine._completed_staged_identity_review(transition_id, 'K1', cid)
        candidate = deepcopy(engine.runtime['trust_transitions'][transition_id])
        candidate['results']['K1']['identity_review'] = receipt
        activated = knowledge.activate_transition(engine.instance, candidate, runtime=engine.runtime)

        repository_path = Path(self.temp.name) / 'round-trip-repository'
        repository_path.mkdir()
        git_init(repository_path)
        instance_id = 'RI-00000000000000000000000000'
        repository = ResearchRepository(repository_path, instance_id)
        # Every stored state passes the current lifecycle gate.
        lifecycle_instance, lifecycle_runtime = current_state()
        persisted_runtime_before = {**lifecycle_runtime, 'trust_bindings': {'TE-review': old_binding}}
        persisted_runtime_after = {**deepcopy(engine.runtime), **lifecycle_runtime}
        persisted_runtime_after['trust_transitions'][transition_id]['status'] = 'active'
        # This domain-level fixture has explicitly applied the queued activation.
        persisted_runtime_after['queue'] = [a for a in persisted_runtime_after['queue']
            if not (a['role'] == 'trust_activate' and a.get('transition_id') == transition_id)]
        execution_ids = list(persisted_runtime_after['executions'])
        persisted_runtime_after['activities'] = {'AY-fixture': {
            'id': 'AY-fixture', 'activity_kind': 'identity_review', 'owner_ref': cid,
            'opened_at': '2026-09-22T00:00:00+00:00', 'input_refs': ['K1'],
            'status': 'finished', 'stage': 'identity_review', 'execution_limit': 24,
            'assigned_execution_ids': execution_ids, 'result_refs': [cid],
            'unresolved': [], 'followups': [], 'finished_at': '2026-09-22T00:00:01+00:00'}}
        for execution_id, execution in persisted_runtime_after['executions'].items():
            execution['action'].setdefault('id', 'AC-' + execution_id)
            execution['input_manifest'] = {'review_cycle_id': cid, 'prompt': {'sha256': 'a' * 64}}
            execution['created_at'] = '2026-09-22T00:00:00+00:00'
            execution['context_origin'] = []
            execution['ended_at'] = '2026-09-22T00:00:01+00:00'
            execution['submission_receipt'] = {'accepted': True}
        for cycle in persisted_runtime_after['review_cycles'].values():
            cycle['producer_execution_ids'] = []
            for binding in cycle.get('input_bindings', {}).values():
                binding['input_sha256'] = 'a' * 64
        persisted_before, persisted_after = deepcopy(before), deepcopy(activated)
        from do_math.configuration import DEFAULT_CONFIG
        from do_math.execution_profiles import build_profiles
        capacity_constraints = build_profiles(DEFAULT_CONFIG)['capacity_constraints']
        for state in (persisted_before, persisted_after):
            state['capacity_constraints'] = deepcopy(capacity_constraints)
            state.pop('role_profile_refs', None)
            state['lifecycle'] = deepcopy(lifecycle_instance['lifecycle'])
        first = repository.initialize(persisted_before, persisted_runtime_before)
        from do_math import canonical as canonical_module
        def transition_hashes(save):
            with patch.object(canonical_module, 'exact_content_hash', wraps=canonical_module.exact_content_hash) as hashes:
                head = save()
            return head, [call for call in hashes.call_args_list if isinstance(call.args[0], dict)
                          and {'transition_id', 'from_environment'} <= set(call.args[0])]
        # A staged review new to the parent binds its transition by hash.
        second, rehashed = transition_hashes(
            lambda: repository.save_with_state(first, persisted_after, persisted_runtime_after)[0])
        self.assertTrue(rehashed)
        old_loaded = ResearchRepository(repository_path, instance_id).load(first)[1]
        new_loaded = ResearchRepository(repository_path, instance_id).load(second)[1]

        for family in ('formal_results', 'identity_assessments'):
            for identifier, record in before[family].items():
                self.assertEqual(old_loaded[family][identifier], record)
                self.assertEqual(new_loaded[family][identifier], record)
        current = new_loaded['knowledge']['K1']
        assessment = next(row for row in new_loaded['identity_assessments'].values()
                          if row.get('review_cycle_id') == cid)
        self.assertEqual(new_loaded['formal_results'][current['formal_result_id']]['transition_id'], transition_id)
        self.assertEqual(new_loaded['expositions'][current['exposition_id']]['formal_result_id'], current['formal_result_id'])
        self.assertEqual(assessment['formal_result_id'], current['formal_result_id'])
        self.assertEqual(assessment['exposition_id'], current['exposition_id'])
        self.assertTrue(any(use['assessment_id'] == assessment['id'] for use in new_loaded['assessment_uses'].values()))
        if not followup_transition:
            return

        first_transition_records = {
            'formal': deepcopy(persisted_after['formal_results'][current['formal_result_id']]),
            'exposition': deepcopy(persisted_after['expositions'][current['exposition_id']]),
            'assessment': deepcopy(assessment),
        }
        final_fixture = trust_fixture(Path(self.temp.name), ['final-lean'])
        final_environment, final_binding = trust_environment(final_fixture, environment_id='TE-final', status='registered',
                                                             source_ref='fixture:final-trust-environment')
        persisted_after['trust_environments']['TE-final'] = final_environment
        persisted_runtime_after['trust_bindings']['TE-final'] = final_binding
        continuity = knowledge.begin_transition(persisted_after, 'TE-final')
        continuity_result = deepcopy(first_transition_records['formal']['verification'])
        continuity_result.update(id='K1', toolchain=deepcopy(final_fixture['toolchain']),
                                 allowed_axioms=deepcopy(final_fixture['allowed_axioms']))
        continuity = knowledge.record_transition_result(persisted_after, continuity, continuity_result)
        persisted_runtime_after['trust_transitions'][continuity['id']] = continuity
        twice_activated = knowledge.activate_transition(
            persisted_after, continuity, runtime=persisted_runtime_after)
        persisted_runtime_after['trust_transitions'][continuity['id']]['status'] = 'active'

        self.assertEqual(twice_activated['formal_results'][current['formal_result_id']],
                         first_transition_records['formal'])
        self.assertEqual(twice_activated['expositions'][current['exposition_id']],
                         first_transition_records['exposition'])
        self.assertEqual(twice_activated['identity_assessments'][assessment['id']],
                         first_transition_records['assessment'])
        reviewed_environment = persisted_runtime_after['review_cycles'][cid]['staged_candidate']['target_environment']
        self.assertEqual(reviewed_environment['status'], 'registered')
        self.assertEqual(twice_activated['trust_environments']['TE-next']['status'], 'superseded')
        # The sealed result binds the identity (toolchain), not a hash of the mutable environment record.
        sealed = twice_activated['formal_results'][current['formal_result_id']]
        self.assertNotIn('trust_environment_digest', sealed['verification'])
        self.assertEqual(sealed['verification']['toolchain'], reviewed_environment['toolchain'])
        self.assertFalse(kr.formal_usable(twice_activated, sealed))
        self.assertFalse(kr.assessment_current(twice_activated, assessment['id']))
        self.assertTrue(kr.usable_links(twice_activated, 'K1'))

        # The finished staged review and its transition equal the parent's: the hash is not recomputed.
        third, rehashed = transition_hashes(
            lambda: repository.save_with_state(second, twice_activated, persisted_runtime_after)[0])
        self.assertEqual(rehashed, [])
        twice_loaded = ResearchRepository(repository_path, instance_id).load(third)[1]
        self.assertEqual(twice_loaded['formal_results'][current['formal_result_id']],
                         first_transition_records['formal'])
        self.assertEqual(twice_loaded['expositions'][current['exposition_id']],
                         first_transition_records['exposition'])
        self.assertEqual(twice_loaded['identity_assessments'][assessment['id']],
                         first_transition_records['assessment'])
        self.assertFalse(kr.assessment_current(twice_loaded, assessment['id']))
        self.assertTrue(kr.usable_links(twice_loaded, 'K1'))

    def test_staged_activation_git_round_trip_preserves_old_and_loads_new_records(self):
        self._staged_activation_git_round_trip(followup_transition=False)

    def test_staged_assessment_survives_a_second_transition_and_git_round_trip(self):
        self._staged_activation_git_round_trip(followup_transition=True)

    def test_split_proposal_binds_real_formal_exposition_and_current_basis(self):
        engine = self.engine
        before = deepcopy(engine.instance['knowledge']['K1'])
        cid = engine.start('K1')
        cycle = engine.runtime['review_cycles'][cid]
        self.assertEqual(cycle['proposal']['lean_code'], kr.proposal_view(engine.instance, 'K1')['lean_code'])
        self.assertEqual(cycle['identity_basis'], kr.identity_basis(engine.instance, 'K1'))
        self.assertEqual(cycle['proposal']['formal_result_id'], before['formal_result_id'])
        self.assertEqual(cycle['proposal']['exposition_id'], before['exposition_id'])
        for field in ('formal', 'lean_code', 'reviews', 'status', 'identity_assessment'):
            self.assertNotIn(field, engine.instance['knowledge']['K1'])

    def test_corrupt_slot_can_be_replaced_from_verified_records_under_real_user_grant(self):
        engine = self.engine
        grant_replacement(engine)
        cid = engine.start('K1')
        action = deepcopy(engine.pending())
        cycle = record_turn(engine.runtime['review_cycles'][cid], action['slot'], [
            {'role': 'user', 'content': 'preserved visible conversation', 'message_id': 'good'},
            {'role': 'tool', 'content': 'lost exact body', 'message_id': 'bad'}])
        cycle['turns'][action['slot']][1]['content'] = 'CORRUPTED'
        engine.runtime['review_cycles'][cid] = cycle
        engine._record_review_recovery(action, ValueError('permanent_loss'), retryable=False)
        outcome = engine._authorize_review_replacement(action, grant_id='GR-review')
        self.assertEqual(outcome['disposition'], 'replacement_ready')
        replacement = next(a for a in engine.runtime['queue'] if a.get('replacement_for') is not None)
        engine.execute({'summary': 'PRIVATE-PEER-REVIEW'})
        context = engine._prepare_review_context(replacement, engine.root / 'replacement')
        self.assertEqual(context['disposition'], 'ready')
        self.assertIn('preserved visible conversation', json.dumps(context))
        self.assertNotIn('CORRUPTED', json.dumps(context))
        self.assertNotIn('PRIVATE-PEER-REVIEW', json.dumps(context))
        engine.execute()
        self.assertTrue(engine.usable())
        self.assertTrue(engine.runtime['review_cycles'][cid]['replacement_receipts'])

    def test_replacement_rejects_forged_grant_source_and_revocation_before_input(self):
        engine = self.engine
        grant_replacement(engine)
        engine.start('K1')
        action = deepcopy(engine.pending())
        engine._record_review_recovery(action, ValueError('permanent_loss'), retryable=False)
        source = engine.instance['governance_sources']['SOURCE-review']['text']
        engine.instance['governance_sources']['SOURCE-review']['text'] += ' forged'
        self.assertEqual(engine._authorize_review_replacement(action, grant_id='GR-review')['disposition'], 'authorization_denied')
        engine.instance['governance_sources']['SOURCE-review']['text'] = source
        outcome = engine._authorize_review_replacement(action, grant_id='GR-review')
        self.assertEqual(outcome['disposition'], 'replacement_ready')
        engine.instance['grants']['GR-review']['status'] = 'revoked'
        action = next(a for a in engine.runtime['queue'] if a.get('replacement_for') is not None)
        result = engine._prepare_review_context(action, engine.root / 'revoked')
        self.assertEqual(result['disposition'], 'authorization_denied')

    def test_approved_replacement_omits_malformed_manifest_without_rethrowing(self):
        engine = self.engine
        grant_replacement(engine)
        cid = engine.start('K1')
        action = deepcopy(engine.pending())
        cycle = record_turn(engine.runtime['review_cycles'][cid], action['slot'], [
            {'role': 'user', 'content': 'UNVERIFIABLE', 'message_id': 'lost'}])
        cycle['transcript_manifest'][action['slot']][0] = None
        engine.runtime['review_cycles'][cid] = cycle
        result = engine._prepare_review_context(action, engine.root / 'broken')
        self.assertEqual(result['disposition'], 'recovery_recorded')
        outcome = engine._authorize_review_replacement(action, grant_id='GR-review')
        self.assertEqual(outcome['disposition'], 'replacement_ready')
        replacement = next(a for a in engine.runtime['queue'] if a.get('replacement_for') is not None)
        ready = engine._prepare_review_context(replacement, engine.root / 'replacement')
        self.assertEqual(ready['disposition'], 'ready')
        self.assertNotIn('UNVERIFIABLE', json.dumps(ready))
        engine.execute()
        engine.execute()
        self.assertTrue(engine.usable())

    def test_checked_delegation_replacement_survives_its_own_recorded_input(self):
        from do_math import delegations
        engine = self.engine
        grant_replacement(engine)
        cid = engine.start('K1')
        action = deepcopy(engine.pending())
        engine._record_review_recovery(action, ValueError('permanent_loss'), retryable=False)
        engine.instance['decisions']['ORIGINAL'] = {'id': 'ORIGINAL', 'actor': 'user',
            'kind': 'review_replacement', 'source_ref': 'SOURCE-review'}
        engine.instance, engine.runtime, _ = governance.apply_decision(engine.instance, engine.runtime,
            {'kind': 'delegation', 'decision_id': 'DD', 'delegation': {'id': 'DG', 'status': 'active',
             'decision_kind': 'review_replacement', 'original_decision_id': 'ORIGINAL',
             'included_targets': ['K1'], 'excluded_targets': [], 'external_effects': [],
             'resource_limits': {}, 'expires_at': None}}, source_ref='SOURCE-review')
        effect = {'review_cycle_id': cid, 'stage': action['stage'], 'slot': action['slot'],
                  'round': action['round'], 'replacement_for': 0, 'continuity_break_cause': 'permanent_loss'}
        case = {'id': 'CASE', 'decision_kind': 'review_replacement', 'target_id': 'K1',
                'external_effects': [], 'resources': {}, 'effect': effect, 'basis_refs': [cid]}
        application = delegations.prepare_application(engine.instance, engine.runtime, 'DG', case)
        for eid, stage in [('INTERPRET', 'interpret'), ('CHECK', 'check')]:
            engine.runtime['executions'][eid] = {'id': eid, 'role': 'intent_interpretation', 'status': 'ended',
                                                'delegation_input_sha256': application['input_sha256']}
            delegations.record_judgment(engine.runtime, application['id'],
                {'input_sha256': application['input_sha256'], 'decision': 'within_scope', 'reason': 'Same authorized recovery'},
                execution_id=eid, stage=stage)
        case['application_id'] = application['id']
        outcome = engine._authorize_review_replacement(action, grant_id='GR-review', delegation_id='DG', case=case)
        self.assertEqual(outcome['disposition'], 'replacement_ready')
        replacement = next(a for a in engine.runtime['queue'] if a.get('replacement_for') is not None)
        engine.runtime['queue'].remove(replacement)
        engine.runtime['queue'].insert(0, replacement)
        engine.execute(record_first=True)
        engine.execute()
        self.assertTrue(engine.usable())
        from do_math.review_cycle import validate_sealed_review
        self.assertEqual(validate_sealed_review(engine.runtime['review_cycles'][cid], engine.runtime,
            instance=engine.instance)['decision'], 'match')

    def test_replacement_unresolved_question_keeps_organizer_finding_coordinates(self):
        engine = self.engine
        grant_replacement(engine)
        engine.start('K1')
        action = deepcopy(engine.pending())
        engine._record_review_recovery(action, ValueError('permanent_loss'), retryable=False)
        engine._authorize_review_replacement(action, grant_id='GR-review')
        engine.execute()
        engine.execute({'decision': 'unresolved', 'questions': ['Exact domain still disputed']})
        self.assertEqual(engine.pending()['stage'], 'organize')
        engine.execute()
        self.assertEqual(engine.pending()['stage'], 'judge')

    def test_actual_profile_and_restored_input_remain_bound_to_the_logical_slot(self):
        engine = self.engine
        engine.start('K1')
        engine.profile = {'id': 'EP-review', 'revision': 1, 'sha256': 'a' * 64}
        engine.execute()
        engine.execute()
        cid = engine.instance['knowledge']['K1']['review_cycle_id']
        cycle = engine.runtime['review_cycles'][cid]
        self.assertEqual(cycle['slot_profiles']['initial-0'], engine.profile)
        self.assertEqual(cycle['input_bindings']['ex-1']['profile_ref'], engine.profile)
        kid = engine.revise()
        next_id = engine.start(kid, previous_cycle_id=cid)
        context, _, eid = engine.execute()
        bound = engine.runtime['review_cycles'][next_id]['input_bindings'][eid]
        self.assertEqual(bound['restored_messages'], context['self_messages'])
        self.assertTrue(bound['restored_messages'])
        engine.profile = {'id': 'EP-other', 'revision': 1, 'sha256': 'b' * 64}
        with self.assertRaisesRegex(ValueError, 'profile'):
            engine.execute()

    def test_runtime_trust_barrier_leaves_final_slot_pending_for_retry(self):
        engine = self.engine
        cid = engine.start('K1')
        engine.execute()
        before = deepcopy(engine.runtime['review_cycles'][cid])
        engine.runtime['trust_transitions'] = {'TR': {'status': 'ready'}}
        with self.assertRaisesRegex(ValueError, 'trust transition'):
            engine.execute()
        after = engine.runtime['review_cycles'][cid]
        self.assertEqual({k: v for k, v in after.items() if k != 'execution_accounting'},
                         {k: v for k, v in before.items() if k != 'execution_accounting'})
        self.assertEqual(after['execution_accounting']['executions_used'], ['ex-1', 'ex-2'])

    def test_initial_match_activates_only_after_all_slots(self):
        engine = self.engine
        cycle_id = engine.start('K1')
        self.assertFalse(engine.usable())
        self.assertEqual(len(engine.runtime['queue']), 2)
        self.assertEqual(engine._start_identity_review('K1'), cycle_id)
        self.assertEqual(len(engine.runtime['queue']), 2)
        schema = engine._review_schema(engine.pending())
        self.assertEqual(schema['properties']['proposal_digest']['enum'], [engine.runtime['review_cycles'][cycle_id]['proposal_digest']])
        engine.execute()
        self.assertEqual(engine.instance['identity_assessments'], {})
        context, _, _ = engine.execute()
        self.assertEqual(context['completed_results'], {})
        item = engine.instance['knowledge']['K1']
        self.assertTrue(engine.usable())
        self.assertEqual(engine.assessment()['decision'], 'match')
        self.assertEqual(len(engine.assessment()['execution_ids']), 2)
        self.assertNotIn('identity_assessment', item)
        self.assertEqual(engine.runtime['queue'][0]['role'], 'research_plan')
        self.assertEqual(json.loads(json.dumps(engine.runtime)), engine.runtime)

    def test_v5_scope_execution_selects_initial_slots_before_the_initial_phase(self):
        engine = self.engine
        cycle_id = engine._start_identity_review('K1')
        self.assertEqual(engine.pending()['stage'], 'scope')
        engine.execute()
        cycle = engine.runtime['review_cycles'][cycle_id]
        self.assertEqual(cycle['phase'], 'initial')
        self.assertEqual(cycle['review_input_basis']['values']['scope_assessment']['assessment_id'], 'generated-scope')
        self.assertEqual({action['slot'] for action in engine.runtime['queue'] if action['role'] == 'identity_review'},
                         {'initial-0', 'initial-1'})

    def test_scope_admission_propagates_actual_activity_and_selected_profile_to_initial_actions(self):
        engine = self.engine
        cid = engine._start_identity_review('K1')
        engine.pending()['owner_activity_id'] = 'AY-actual'
        selected = {'id': 'EP-fixed', 'revision': 2, 'sha256': 'b' * 64}
        policy = engine.runtime['review_cycles'][cid]['review_policy']
        scope = {'assessment_id': 'scope-picked', 'policy_id': policy['id'],
            'required_perspectives': [], 'initial_slots': [
                {'id': 'initial-0', 'perspective': 'formal', 'required_source_refs': ['proposal']},
                {'id': 'initial-1', 'perspective': 'semantic', 'required_source_refs': ['proposal']}],
            'selected_profile_ref': selected, 'activity_execution_limit': 24, 'overflow_disposition': 'unresolved'}
        engine.execute({'scope_assessment': scope})
        self.assertEqual(engine.runtime['review_cycles'][cid]['owner_activity_id'], 'AY-actual')
        for action in engine.runtime['queue']:
            if action['role'] == 'identity_review':
                self.assertEqual(action['owner_activity_id'], 'AY-actual')
                self.assertEqual(action['profile_ref'], selected)

    def test_scope_to_answer_and_judgment_publishes_the_same_links_consumed_by_goal_audit(self):
        engine = self.engine
        cid = engine._start_identity_review('K1')
        engine.execute()  # actual scope consumer, followed by a disputed initial batch
        engine.execute({'decision': 'mismatch', 'findings': [
            {'id': 'f', 'statement': 'Check the domain', 'evidence': ['proposal']}]})
        engine.execute()
        engine.execute()  # organization
        for _ in range(3): engine.execute()
        engine.execute()  # original slot withdraws its objection
        for _ in range(3): engine.execute()
        assessment = engine.assessment()
        link = kr.usable_links(engine.instance, 'K1')[0]
        self.assertEqual(link['assessment_id'], assessment['id'])
        self.assertEqual(kr.knowledge_view(engine.instance)[0]['links'], [link])
        self.assertTrue(knowledge.assess_use(engine.instance['knowledge']['K1'], engine.instance)['valid'])
        self.assertEqual(assessment['policy_ref'], engine.runtime['review_cycles'][cid]['policy_ref'])
        audit = bare_engine(engine.instance, engine.runtime)
        audit.instance['goal_judgments'] = []
        audit.runtime['tasks'] = {}
        from do_math import governance as gov
        from research_fixtures import charter
        record = charter('CH-goal-fixture', 'Prove the fixture')
        source = gov.preserve_source('US-goal-fixture', 'User approves the fixture goal', origin='user')
        audit.instance = gov.initialize_governance(audit.instance, source,
            {'id': 'DC-goal-fixture', 'actor': 'user', 'source_ref': source['id'],
             'source_sha256': source['sha256'], 'record_hashes': {record['id']: exact_content_hash(record)}}, [record])
        assessment = audit.instance['identity_assessments'][link['assessment_id']]
        audit._render_prompt = create_autospec(audit._render_prompt, return_value='fixed goal-audit instructions')
        audit.runtime['inputs'] = []
        audit.instance['config']['goal_auditors'] = 2
        goal_basis = audit._goal_basis_key()
        audit._record_output_questions = create_autospec(audit._record_output_questions)
        audit.runtime['executions']['AUDIT'] = {'id': 'AUDIT', 'role': 'goal_audit', 'source_basis': []}
        audit._bind_governance_input({'role': 'goal_audit'}, audit.runtime['executions']['AUDIT'],
                                    audit._governance_context({'role': 'goal_audit'}, {}))
        audit._apply({'role': 'goal_audit', 'basis': goal_basis, 'slot': 0, 'required': 2},
            {'decision': 'satisfied', 'scope_complete': True, 'used_sources': ['K1'], 'questions': [],
             'summary': 'The reviewed links support the charter goal', 'findings': [], 'additional_audits': []}, 'AUDIT')
        judgment = audit.instance['goal_judgments'][0]
        self.assertEqual(judgment['formal_result_refs'], [link['formal_result_id']])
        self.assertEqual(judgment['record_basis'], knowledge.capture_basis(audit.instance, audit.runtime, ['K1']))
        self.assertIs(audit.instance['identity_assessments'][link['assessment_id']], assessment)
        audit.instance = kr.set_assessment_use(audit.instance, assessment['id'], 'suspended', 'New source dispute', 'operator')
        self.assertNotEqual(audit._goal_basis_key(), goal_basis)
        self.assertFalse(knowledge.assess_use(audit.instance['knowledge']['K1'], audit.instance)['valid'])

    def open_dispute(self):
        engine = self.engine
        cycle_id = engine.start('K1')
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
        self.assertTrue(engine.usable())
        self.assertEqual(engine.assessment()['review_cycle_id'], cycle_id)
        self.assertEqual(len(engine.assessment()['execution_ids']), 3)
        self.assertEqual(engine.assessment()['basis'], kr.identity_basis(engine.instance, 'K1'))

    def test_mismatch_and_round_limit_return_precise_followup(self):
        cycle_id = self.open_dispute()
        engine = self.engine
        for _ in range(3):
            engine.execute(dict(decision='mismatch', issue_verdicts=[dict(issue_id='issue-0', decision='approved', reason='Actual mismatch in the domain', evidence=['proposal:1'])]))
        self.assertEqual(engine.assessment()['decision'], 'mismatch')
        self.assertFalse(engine.usable())
        plan = next(a for a in engine.runtime['queue'] if a['role'] == 'research_plan')
        self.assertEqual(plan['identity_review']['cycle_id'], cycle_id)
        self.assertIn('issue-0', plan['identity_review']['issues'])
        self.assertTrue(plan['identity_review']['actual_scope'])
        self.assertFalse(plan['identity_review']['effective'])
        self.engine = ReviewFakeEngine(self.temp.name, rounds=1)
        self.open_dispute()
        for _ in range(3):
            self.engine.execute(dict(decision='unresolved', issue_verdicts=[dict(issue_id='issue-0', decision='unresolved', reason='Source is ambiguous', evidence=[])]))
        self.assertEqual(self.engine.assessment()['decision'], 'unresolved')
        plan = next(a for a in self.engine.runtime['queue'] if a['role'] == 'research_plan')
        self.assertTrue(plan['identity_review']['remaining_questions'])

    def test_new_revision_restarts_all_slots_and_retains_own_conversation(self):
        engine = self.engine
        first_id = engine.start('K1')
        engine.execute()
        engine.execute()
        first = deepcopy(engine.runtime['review_cycles'][first_id])
        previous_assessment = deepcopy(engine.assessment())
        kid = engine.revise()
        second_id = engine.start(kid, previous_cycle_id=first_id)
        second = engine.runtime['review_cycles'][second_id]
        self.assertNotEqual(second['revision'], first['revision'])
        self.assertEqual(second['reviewer_slots'], first['reviewer_slots'])
        self.assertEqual(second['turns'], first['turns'])
        self.assertFalse(engine.usable(kid))
        context, _, _ = engine.execute()
        self.assertTrue(context['self_messages'])
        self.assertTrue(context['source_refs'])
        engine.execute()
        self.assertEqual(engine.assessment(kid)['review_cycle_id'], second_id)
        self.assertTrue(engine.usable(kid))
        self.assertEqual(engine.assessment('K1'), previous_assessment)

    def test_source_recovery_has_exact_bytes_hash_and_relative_path(self):
        engine = self.engine
        cycle_id = engine.start('K1')
        cycle = engine.runtime['review_cycles'][cycle_id]
        source = dict(role='tool', content='Original source at line 12: quantifier', call='read',
                      arguments={'path': 'original.txt'}, message_id='source-1')
        engine.runtime['review_cycles'][cycle_id] = record_turn(cycle, 'initial-0', [source])
        action = engine.pending()
        workspace = engine.root / 'source-test'
        context = engine._prepare_review_context(action, workspace)['context']
        reference = context['source_refs'][0]
        path = workspace / reference['local_path']
        self.assertTrue(path.is_file())
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), reference['sha256'])
        self.assertEqual(json.loads(path.read_bytes()), source)
        self.assertFalse(Path(reference['local_path']).is_absolute())
        self.assertNotIn(source['content'], json.dumps(context))
        self.assertEqual(context['self_messages'][0]['content']['source_ref']['local_path'], reference['local_path'])
        engine._prepare_review_context(action, workspace)['context']
        self.assertEqual(len(engine.runtime['review_cycles'][cycle_id]['turns']['initial-0']), 1)

    def test_final_match_does_not_override_suspension_or_formal_change(self):
        for failure in ('suspended', 'source_hash', 'environment', 'trust_transition', 'policy'):
            with self.subTest(failure=failure):
                engine = ReviewFakeEngine(self.temp.name)
                engine.start('K1')
                engine.execute()
                formal = engine.instance['formal_results'][engine.instance['knowledge']['K1']['formal_result_id']]
                if failure == 'suspended': formal['formal_use'] = 'suspended'
                elif failure == 'source_hash': formal['verification']['source_sha256'] = 'changed'
                elif failure == 'environment': engine.instance['trust_environments']['TE-review']['status'] = 'invalid'
                elif failure == 'policy': engine.instance['review_policy']['activity_execution_limit'] += 1
                else: engine.runtime['trust_transitions'] = {'TR-pending': {'status': 'checking'}}
                with self.assertRaises(ValueError):
                    engine.execute()
                self.assertEqual(engine.instance['identity_assessments'], {})
                self.assertFalse(engine.usable())

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
        engine.start('K1')
        engine.execute()
        formal = engine.instance['formal_results'][engine.instance['knowledge']['K1']['formal_result_id']]
        verification = deepcopy(formal['verification'])
        engine.instance = kr.record_formal_result(engine.instance, 'K1', verification, 'TE-review', runtime=engine.runtime)
        engine.execute()
        self.assertTrue(engine.usable())
        self.assertEqual(engine.assessment()['basis'], kr.identity_basis(engine.instance, 'K1'))

    def test_environment_transition_during_review_invalidates_old_environment_use(self):
        engine = self.engine
        engine.start('K1')
        engine.execute()
        engine.instance['active_trust_environment'] = 'TE-new'
        engine.instance['trust_environments']['TE-review']['status'] = 'superseded'
        with self.assertRaisesRegex(ValueError, 'premises changed'):
            engine.execute()
        self.assertFalse(engine.usable())

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
        self.assertTrue(engine.usable())

    def test_mutated_proposal_and_old_action_are_rejected(self):
        engine = self.engine
        cycle_id = engine.start('K1')
        old_action = deepcopy(engine.pending())
        formal = engine.instance['formal_results'][engine.instance['knowledge']['K1']['formal_result_id']]
        original = formal['lean_code']
        formal['lean_code'] += '\n-- changed during review'
        with self.assertRaisesRegex(ValueError, 'sealed mathematical proposal'):
            engine._review_schema(old_action)
        formal['lean_code'] = original
        engine.execute()
        engine.execute()
        kid = engine.revise()
        engine.start(kid, previous_cycle_id=cycle_id)
        with self.assertRaisesRegex(ValueError, 'not pending'):
            engine._review_schema(old_action)


class ReleasedInsightTests(unittest.TestCase):
    def test_released_incidental_insights_plan_only_preserved_items(self):
        for valid in (True, False):
            engine = routing_engine()
            engine.instance = knowledge_io.ensure_ontology(engine.instance)
            engine._apply_queue_plan = create_autospec(engine._apply_queue_plan)
            engine._apply_academic_resolutions = create_autospec(engine._apply_academic_resolutions)
            engine.runtime['executions'] = {'EX-old': {'id': 'EX-old', 'status': 'ended'},
                'EX-current': {'id': 'EX-current', 'status': 'ended', 'extensions': {}}}
            engine.runtime['review_cycles'] = {'RC': {'status': 'completed'}}
            engine.runtime['private_insights'] = {'RC': [{'source_execution': 'EX-old',
                'kind': 'question' if valid else 'unregistered', 'title': 'Question ' + str(i),
                'statement': 'What remains?', 'summary': 'A retained question', 'evidence_ids': []} for i in range(3)]}
            engine._apply_extensions({'role': 'identity_review', 'review_cycle_id': 'RC'}, 'EX-current')
            plans = [a for a in engine.runtime['queue'] if a['role'] == 'research_plan']
            self.assertEqual(len(plans), int(valid))
            if valid:
                self.assertEqual(set(plans[0]['evidence_refs']), set(engine.instance['knowledge']))
                self.assertEqual(len(plans[0]['evidence_refs']), 3)
            else:
                self.assertEqual(engine.instance['knowledge'], {})


class ReviewPreparationFailureTests(ActivatedPurposeHarness):
    def test_failed_review_slot_keeps_its_live_sibling_running(self):
        engine, runner = self.make_active()
        engine.runtime['queue'] = []
        engine._knowledge_io_control({'action': 'knowledge', 'id': new_id('UC'),
            'config': {'operation': 'import', 'candidate': theorem()}})
        formal = next(a for a in engine.runtime['queue'] if a['role'] == 'formal_check')
        engine._save()
        with owner_calls(engine):
            engine._formal(formal)
        engine._start_identity_review(formal['target'])
        scope = next(a for a in engine.runtime['queue'] if a['role'] == 'identity_review')
        with owner_calls(engine):
            start_model_call(engine, scope)
        engine.runtime['queue'] = [a for a in engine.runtime['queue'] if a['role'] == 'identity_review']
        self.assertEqual({a['slot'] for a in engine.runtime['queue']}, {'initial-0', 'initial-1'})
        release = threading.Event()
        answer = runner.answer
        def wait_for_sibling(role, context, workspace):
            if role == 'identity_review' and context['action']['slot'] == 'initial-0':
                self.assertTrue(release.wait(60), 'Sibling preparation never reached its restoration failure')
            return answer(role, context, workspace)
        runner.answer = wait_for_sibling
        prepare = engine._prepare_review_context
        mkdir = Path.mkdir
        observed = []
        def busy(path, *args, **kwargs):
            if 'review-sources' in path.parts:
                raise OSError(errno.EBUSY, 'Only this review slot cannot materialize its input')
            return mkdir(path, *args, **kwargs)
        def prepare_slot(action, workspace, **kwargs):
            if action.get('slot') != 'initial-1':
                return prepare(action, workspace, **kwargs)
            observed.append(any(e.get('action', {}).get('slot') == 'initial-0' and e['status'] != 'ended'
                                for e in engine.runtime['executions'].values()))
            try:
                with patch.object(Path, 'mkdir', busy):
                    return prepare(action, workspace, **kwargs)
            finally:
                release.set()
        with patch.object(engine, '_prepare_review_context', side_effect=prepare_slot):
            engine._save()
            engine.run(max_steps=2)
        self.assertEqual(observed, [True])
        first = next(e for e in engine.runtime['executions'].values() if e.get('action', {}).get('slot') == 'initial-0')
        self.assertEqual(first['outcome'], 'output_accepted', first.get('error'))
        held = next(w for w in engine.runtime['waiting_actions'].values() if w['action'].get('slot') == 'initial-1')
        self.assertEqual(held['kind'], 'review_input_restoration')

    def test_review_materialization_failure_ends_preparation_and_saves_recovery(self):
        engine, _ = self.make_active()
        engine.runtime['queue'] = []
        engine._knowledge_io_control({'action': 'knowledge', 'id': new_id('UC'),
            'config': {'operation': 'import', 'candidate': theorem()}})
        formal = next(a for a in engine.runtime['queue'] if a['role'] == 'formal_check')
        engine._save()
        with owner_calls(engine):
            engine._formal(formal)
        kid = formal['target']
        engine._start_identity_review(kid)
        action = next(a for a in engine.runtime['queue'] if a['role'] == 'identity_review')
        original = Path.mkdir
        def unavailable(path, *args, **kwargs):
            if 'review-sources' in path.parts:
                raise OSError(errno.EBUSY, 'Regression source materialization busy')
            return original(path, *args, **kwargs)
        with patch.object(Path, 'mkdir', unavailable), owner_calls(engine):
            start_model_call(engine, action)
        attempts = [e for e in engine.runtime['executions'].values() if e.get('action', {}).get('id') == action['id']]
        self.assertEqual(len(attempts), 1)
        self.assertEqual(attempts[0]['status'], 'ended')
        wait = engine.runtime['waiting_actions'][action['id']]
        self.assertEqual(wait['kind'], 'review_input_restoration')
        self.assertEqual(wait['next_owner'], 'review_recovery')
        _, _, saved = engine.store.load()
        self.assertEqual(saved['waiting_actions'][action['id']], wait)
        outcome = engine._retry_review_restoration(wait['action'], self.root / 'restored', at=now())
        self.assertEqual(outcome['disposition'], 'review_resumed')
        self.assertNotIn(action['id'], engine.runtime['waiting_actions'])


class ReviewScopeBudgetTests(unittest.TestCase):
    def test_exhaustion_drains_only_owned_attempts_before_publishing_followup(self):
        from do_math import execution_lifecycle
        engine, _ = formal_check_engine(self)
        engine.knowledge('K2')
        policy = engine._adopted_review_policy()
        limit = review_policy.minimum_scope_executions(2, policy['round_limit'])
        policy['activity_execution_limit'] = limit
        engine._adopted_review_policy = create_autospec(engine._adopted_review_policy, side_effect=lambda: deepcopy(policy))
        cid = start_scoped_review(engine, 'K2', scope_assessment(policy, ['one', 'two']))
        action = next(a for a in engine.runtime['queue'] if a.get('review_cycle_id') == cid)
        stamp = engine.current_time.isoformat()
        for number in range(limit):
            execution = engine._register_execution(action,
                {'id': f'EX-attempt-{number}', 'role': 'identity_review', 'status': 'queued'})
            if number < limit-1:
                execution_lifecycle.end_preparation(execution, at=stamp, stage='context', reason='fixture interrupted attempt', cancelled=True)
        last = execution['id']
        execution_lifecycle.transition_execution(execution, 'starting', at=stamp)
        execution_lifecycle.transition_execution(execution, 'running', at=stamp)
        unrelated = engine._register_execution({'id': 'AC-unrelated', 'role': 'maintenance'},
            {'id':'EX-unrelated','role':'maintenance','status':'running'})
        self.assertIsNone(engine._register_execution(action, {'id':'EX-denied','role':'identity_review','status':'queued'}))
        cycle = engine.runtime['review_cycles'][cid]
        self.assertEqual(review_cycle.resource_disposition(cycle)['state'], 'draining')
        self.assertEqual(engine.runtime['executions'][last]['stop_requested'], 'review_resource_disposition')
        self.assertNotIn('stop_requested', unrelated)
        self.assertFalse(any(a['role']=='research_plan' for a in engine.runtime['queue']))
        execution_lifecycle.transition_execution(execution, 'stopping', at=stamp)
        execution_lifecycle.transition_execution(execution, 'ended', at=stamp, outcome='execution_incomplete', disposition='fixture return')
        engine._settle_activity(last)
        self.assertEqual(cycle['status'], 'unresolved')
        self.assertEqual(engine.runtime['activities'][cycle['owner_activity_id']]['status'], 'finished')
        self.assertEqual(unrelated['status'], 'running')
        self.assertEqual(sum(a['role']=='research_plan' for a in engine.runtime['queue']), 1)
        self.assertEqual(review_cycle.validate_sealed_review(cycle, engine.runtime)['decision'], 'unresolved')


    def test_floor_counts_scope_and_mandatory_followup(self):
        for rounds, required in [(1, 8), (2, 14), (4, 14)]:
            with self.subTest(rounds=rounds):
                policy = review_policy.build_review_policy(None, reviewer_count=3, max_rounds=rounds)
                scope = scope_assessment(policy, ['one', 'two', 'three'])
                scope['activity_execution_limit'] = required - 1
                with self.assertRaisesRegex(ValueError, 'at least'):
                    review_policy.validate_scope_assessment(scope, policy, executions_used=1)
                scope['activity_execution_limit'] = required
                self.assertEqual(review_policy.validate_scope_assessment(scope, policy,
                    executions_used=1)['activity_execution_limit'], required)

    def test_scope_context_exposes_actual_attempt_usage(self):
        cycle = review_cycle.start_review({'revision': 1}, 2)
        cycle['execution_accounting']['executions_used'] = ['EX-first', 'EX-retry']
        visible = review_cycle.context_for(cycle, review_cycle.next_actions(cycle)[0])
        self.assertEqual(visible['scope_executions_used'], 2)
        self.assertEqual(visible['minimum_scope_execution_limit'], 13)

    def test_unaffordable_scope_returns_to_plan_without_fabricating_a_judgment(self):
        for disposition in ('unresolved', 'defer'):
            with self.subTest(disposition=disposition):
                engine, _ = formal_check_engine(self)
                engine.knowledge('K2')
                policy = engine._adopted_review_policy()
                policy.update(activity_execution_limit=1, overflow_disposition=disposition)
                engine._adopted_review_policy = create_autospec(engine._adopted_review_policy,
                                                                side_effect=lambda: deepcopy(policy))
                cid = engine._start_identity_review('K2')
                action = next(a for a in engine.runtime['queue'] if a.get('review_cycle_id') == cid)
                before = deepcopy(engine.instance['identity_assessments'])
                result = engine._register_execution(action, {'id': 'EX-unstarted', 'role': 'identity_review', 'status': 'queued'})
                self.assertIsNone(result)
                self.assertNotIn('EX-unstarted', engine.runtime['executions'])
                cycle = engine.runtime['review_cycles'][cid]
                record = review_cycle.validate_resource_disposition(cycle, engine.runtime)
                self.assertEqual(record['state'], 'ended' if disposition == 'unresolved' else 'deferred')
                self.assertEqual(engine.instance['identity_assessments'], before)
                plans = [a for a in engine.runtime['queue'] if a['role'] == 'research_plan']
                self.assertEqual(len(plans), 1)
                self.assertIn(cid, plans[0]['evidence_refs'])
                self.assertEqual(review_cycle.next_actions(cycle), [])
                engine._settle_review_resource_dispositions()
                self.assertEqual(len([a for a in engine.runtime['queue'] if a['role'] == 'research_plan']), 1)
                if disposition == 'unresolved':
                    self.assertEqual(review_cycle.validate_sealed_review(cycle, engine.runtime)['decision'], 'unresolved')


class ReviewInputOverflowTests(unittest.TestCase):
    def setUp(self):
        start_active_copy(self)

    def test_actual_proposal_overflow_ends_preparation_and_reaches_plan_input(self):
        import json
        from do_math import knowledge_records, context_store
        engine = ResearchEngine(self.repo, self.identifier)
        source = 'theorem overflow : 1 = 1 := rfl'
        fragment = 'This is preserved explanation evidence. '
        engine.instance, _ = knowledge_records.create_candidate(engine.instance, {
            'id': 'KN-overflow', 'kind': 'lemma', 'title': 'Overflow fixture', 'statement': 'One equals one', 'summary': 'Large explanation',
            'explanation': fragment * (engine.instance['config']['max_input_bytes'] // len(fragment) + 1),
            'lean_code': source, 'declaration_names': ['overflow'], 'dependencies': []},
            source_ref=engine.instance['lifecycle']['input_id'], actor_ref=next(iter(engine.runtime['executions'])))
        environment = engine._formal_environment()
        result = formal_verification(source, ['overflow'], environment['toolchain'])
        engine.instance = knowledge_records.record_formal_result(engine.instance, 'KN-overflow', result,
            environment['id'], runtime=engine.runtime)
        engine._save()
        cid = engine._start_identity_review('KN-overflow')
        action = next(a for a in engine.runtime['queue'] if a.get('review_cycle_id') == cid)
        with self.assertRaises(StopIteration):
            next(engine._call_steps(action))
        cycle = engine.runtime['review_cycles'][cid]
        event = review_cycle.resource_disposition(cycle)
        self.assertIsNotNone(event)
        self.assertEqual(event['reason'], 'review_input_overflow')
        execution = engine.runtime['executions'][event['detail']['execution_id']]
        self.assertEqual((execution['status'], execution['input_preparation']['stage']), ('ended', 'packing'))
        self.assertIsNone(execution.get('capacity', {}).get('process'))
        for entry in execution['input_manifest']['direct']:
            self.assertTrue(engine.store.read(entry['artifact_ref'], engine.head))
        self.assertFalse(any(q.get('blocks') for q in engine.runtime.get('question_links', [])))
        plan = next(a for a in engine.runtime['queue'] if a['role'] == 'research_plan')
        workspace = Path(engine.instance['workspace'])/'plan-input'
        workspace.mkdir()
        context = engine._context(plan, workspace, execution_id='EX-plan-input')
        profile = engine._execution_profile(plan)
        fitted = context_store.prepare_role_input(context, instance=engine.instance, runtime=engine.runtime,
            role='research_plan', profile=profile, snapshot=engine.head, workspace=workspace,
            activity_id='AY-plan-input', artifact_prefix='runtime/artifacts/BA-plan-input')
        followup = fitted['validation_context']['review_followups'][0]
        self.assertEqual(followup['id'], cid)
        restored = json.loads((workspace/followup['source_ref']['path']).read_bytes())
        self.assertEqual(restored['proposal_digest'], cycle['proposal_digest'])
        self.assertEqual(restored['history'], cycle['history'])
        self.assertIn(cid, fitted['validation_context']['supplied_record_ids'])
        restarted = ResearchEngine(self.repo, self.identifier)
        self.assertEqual(restarted.runtime['review_cycles'][cid]['status'], 'unresolved')


class ImpactReviewRouting(unittest.TestCase):
    def fixture(self):
        # Reuse the owner's concrete domain fixture, not a substitute apply engine.
        from review_fixtures import ImpactReviewHarness
        source = ImpactReviewHarness(); source.setUp()
        engine = routing_engine(); engine.instance = source.instance
        engine.runtime.update(source.runtime); engine.head = "current"
        engine.instance["workspace"] = "unused"
        action = {"id": "AC-held", "role": "research_work", "owner_activity_id": "AY-work"}
        producer = engine.runtime["executions"]["EX-producer"]
        producer.update(action=action, output=source.output, input_bundle="BA-input", status="ended", outcome="execution_incomplete")
        request = source.request()
        received = {"bundles": [{"integration_id": "IN-held", "next_owner": "impact_review", "impact_review_request": request}]}
        engine._hold_impact_reviews(action, "EX-producer", received)
        return engine, source, action, request, received

    def test_exact_request_waits_for_accepted_review_without_new_producer(self):
        engine, source, action, request, received = self.fixture()
        before = deepcopy(source.output)
        engine._hold_impact_reviews(action, "EX-producer", received)
        reviews = [row for row in engine.runtime["queue"] if row.get("stage") == "impact_review"]
        self.assertEqual(len(reviews), 1)
        review_action = reviews[0]
        self.assertEqual(review_action["input_basis"]["impact_review"], request)
        self.assertNotIn("continuation_of", review_action)
        engine._receive_submission = create_autospec(engine._receive_submission); engine._save = create_autospec(engine._save); engine._settle_activity = create_autospec(engine._settle_activity)
        with patch("do_math.submission.read_sealed_submission",
                   side_effect=lambda execution, *_, **__: {"output": execution["output"]}):
            engine._retry_impact_reviews()
        engine._receive_submission.assert_not_called()
        engine.runtime["executions"]["EX-review"] = {"id": "EX-review", "status": "ended", "outcome": "output_accepted",
            "action": review_action, "output": source.review_output(request)}
        engine.store = create_autospec(ResearchRepository, instance=True); engine.store.read.return_value = b"{}"
        with patch("do_math.submission.read_sealed_submission",
                   side_effect=lambda execution, *_, **__: {"output": execution["output"]}):
            engine._retry_impact_reviews()
        self.assertEqual(engine._receive_submission.call_args.args[2], "EX-producer")
        self.assertTrue(engine._receive_submission.call_args.kwargs["preserved"])
        self.assertEqual(engine.runtime["waiting_actions"][action["id"]]["review_execution_ids"], {"IN-held": "EX-review"})
        self.assertEqual(source.output, before)

    def test_shared_candidate_applies_actual_domain_revision_without_mutating_preview_source(self):
        from do_math import knowledge
        engine, source, action, request, received = self.fixture()
        bundle = deepcopy(source.bundle)
        bundle["owns_response"] = False
        for change in bundle["extensions"]["knowledge_changes"]:
            roots = knowledge.revision_roots(engine.instance, change["id"])
            change["impact_set"] = knowledge.plan_impact(engine.instance, engine.runtime, roots, [])["computed_impact"]
        roots = set().union(*(knowledge.revision_roots(engine.instance, change["id"])
            for change in bundle["extensions"]["knowledge_changes"]))
        bundle["impact_set"] = knowledge.plan_impact(engine.instance, engine.runtime, roots, [])["computed_impact"]
        # Preview and receiver both call this exact domain callback; storage/CAS is
        # tested separately. Keep independent copies of the actual original state.
        original = canonical_json(engine.instance)
        candidate, running = deepcopy(engine.instance), deepcopy(engine.runtime)
        engine._apply_bundle_candidate(candidate, running, bundle, action=action,
            execution_id="EX-producer", extensions=bundle["extensions"])
        self.assertEqual(canonical_json(engine.instance), original)
        self.assertEqual({source.ids[0], source.ids[2]}, {row["supersedes"] for row in candidate["knowledge"].values() if row.get("supersedes")})
        self.assertEqual(len([row for row in running["queue"] if row.get("reason") == "knowledge currentness changed"]), 0)

    def test_unresolved_review_remains_held_and_has_one_final_rejected_receipt(self):
        engine, source, action, request, received = self.fixture()
        output = source.review_output(request); output["impact_review"]["plan_decisions"][0]["decision"] = "unresolved"
        engine.runtime["executions"]["EX-review"] = {"id": "EX-review", "status": "ended", "outcome": "output_accepted",
            "action": deepcopy(next(row for row in engine.runtime["queue"] if row.get("stage") == "impact_review")), "output": output}
        engine._record_task_receipt = create_autospec(engine._record_task_receipt); engine._save = create_autospec(engine._save); engine._receive_submission = create_autospec(engine._receive_submission)
        engine.store = create_autospec(ResearchRepository, instance=True); engine.store.git_dir = 'git-' + uuid.uuid4().hex
        with patch("do_math.submission.read_sealed_submission",
                   side_effect=lambda execution, *_, **__: {"output": execution["output"]}):
            engine._retry_impact_reviews(); engine._retry_impact_reviews()
        engine._receive_submission.assert_not_called()
        engine._record_task_receipt.assert_called_once()
        self.assertFalse(engine._record_task_receipt.call_args.kwargs["accepted"])
        self.assertEqual(engine.runtime["waiting_actions"][action["id"]]["kind"], "impact_review_blocked")
        self.assertEqual(len([row for row in engine.runtime["queue"] if row.get("stage") == "impact_review"]), 1)


class AssessmentReassessmentConnections(unittest.TestCase):
    def fixture(self):
        from review_fixtures import ReassessmentHarness
        owner = ReassessmentHarness(); owner.setUp(); self.addCleanup(owner.doCleanups)
        owner.engine.runtime["status"] = "ready"
        return owner

    def test_central_control_consumes_qualified_evidence_and_retains_bounded_followup(self):
        owner = self.fixture(); engine = owner.engine
        request = {"id": "UC-reassessment", "action": "request", "config": {"role": "identity_review",
            "assessment_reassessment": owner.request(owner.defect())}}
        self.assertTrue(ResearchEngine._review_recovery_control(engine, request))
        opened = engine.runtime["history"][-1]["result"]
        self.assertEqual(opened["disposition"], "reassessment_opened")
        self.assertEqual(owner.use()["status"], "suspended")
        owner.complete("unresolved")
        activity = engine.runtime["activities"][opened["owner_activity_id"]]
        # The review-domain harness creates executions; attach them through the
        # production activity API before exercising the central terminal hook.
        from do_math.activities import assign_execution
        for execution in list(engine.runtime["executions"].values()):
            if execution.get("owner_activity_id") == activity["id"]:
                assign_execution(engine.runtime, activity["id"], execution)
        ResearchEngine._settle_activity(engine, activity["assigned_execution_ids"][-1])
        self.assertEqual(activity["status"], "finished")
        self.assertEqual(activity["unresolved"][0]["next_owner"], "research_plan")
        self.assertTrue(activity["followups"][0]["revisit_conditions"])
        self.assertEqual(len(engine.instance["identity_assessments"]), 1)

    def test_cli_report_reaches_qualified_reassessment_and_replay_is_idempotent(self):
        from do_math import cli
        owner = self.fixture()
        path = Path(owner.directory.name) / "assessment-report.json"
        path.write_text(json.dumps(owner.request(owner.defect())), encoding="utf-8")
        args = cli.build_parser().parse_args(["request", "--repository", owner.directory.name,
            "--instance", "RI-test", "--assessment-reassessment-file", str(path)])
        def consume(args, action, *, text, config):
            self.assertEqual(json.loads(text), config["assessment_reassessment"])
            ResearchEngine._review_recovery_control(owner.engine,
                {"id": "UC-cli-report", "action": action, "config": config})
            return owner.engine.runtime["history"][-1]["result"]
        with patch("do_math.cli._control", side_effect=consume):
            first, code = cli.execute(args)
            second, _ = cli.execute(args)
        self.assertEqual(code, 0)
        self.assertEqual(first["disposition"], "reassessment_opened")
        self.assertEqual(second["disposition"], "already_open")
        self.assertEqual(first["review_cycle_id"], second["review_cycle_id"])
        self.assertEqual(owner.use()["status"], "suspended")

    def test_ordinary_report_cannot_suspend_and_closed_control_cannot_open_review(self):
        owner = self.fixture(); engine = owner.engine
        request = {"id": "UC-report", "action": "request", "config": {"role": "identity_review",
            "assessment_reassessment": owner.request({"kind": "report", "text": "Maybe wrong"})}}
        self.assertTrue(ResearchEngine._review_recovery_control(engine, request))
        self.assertEqual(engine.runtime["history"][-1]["result"]["disposition"], "report_only")
        self.assertEqual(owner.use()["status"], "active")
        engine.runtime["status"] = "closed"
        with self.assertRaisesRegex(ValueError, "closed/completed"):
            ResearchEngine._review_recovery_control(engine, request)

    def test_public_admission_binds_original_assessment_hash(self):
        owner = self.fixture(); engine = owner.engine
        engine.instance["workspace"] = owner.directory.name
        store = create_autospec(ResearchRepository, instance=True); store.load.return_value = (engine.head, engine.instance, engine.runtime)
        config = {"role": "identity_review", "assessment_reassessment": owner.request({"kind": "report", "text": "Read this original judgment"})}
        with patch("do_math.core_engine.ResearchRepository", return_value=store):
            result = control(Path(owner.directory.name), "RI-test", "request", config=config)
            self.assertTrue(result["accepted"])
            wrong = deepcopy(config); wrong["assessment_reassessment"]["assessment_sha256"] = "0" * 64
            with self.assertRaisesRegex(ValueError, "original judgment"):
                control(Path(owner.directory.name), "RI-test", "request", config=wrong)


class DelegationConnections(unittest.TestCase):
    def test_actual_blind_judgments_apply_the_approved_review_recovery(self):
        from review_fixtures import ReviewFakeEngine, grant_replacement
        from do_math import governance
        from types import MethodType
        with tempfile.TemporaryDirectory() as temporary:
            engine = ReviewFakeEngine(temporary)
            grant_replacement(engine)
            cid = engine.start("K1")
            action = deepcopy(engine.pending())
            engine._record_review_recovery(action, ValueError("permanent_loss"), retryable=False)
            engine.instance["decisions"]["ORIGINAL"] = {"id": "ORIGINAL", "actor": "user", "kind": "review_replacement", "source_ref": "SOURCE-review"}
            engine.instance, engine.runtime, _ = governance.apply_decision(engine.instance, engine.runtime,
                {"kind": "delegation", "decision_id": "DD", "delegation": {"id": "DG", "status": "active", "decision_kind": "review_replacement",
                    "original_decision_id": "ORIGINAL", "included_targets": ["K1"], "excluded_targets": [], "external_effects": [], "resource_limits": {}, "expires_at": None}}, source_ref="SOURCE-review")
            effect = {"review_cycle_id": cid, "stage": action["stage"], "slot": action["slot"],
                      "round": action["round"], "replacement_for": 0,
                      "continuity_break_cause": "permanent_loss"}
            case = {"id": "CASE", "decision_kind": "review_replacement", "target_id": "K1", "external_effects": [], "resources": {}, "effect": effect,
                    "basis_refs": [{"id": cid}]}
            request = {"id": "UC-case", "action": "request", "config": {"role": "maintenance", "review_replacement": {"action": action, "grant_id": "GR-review", "delegation_id": "DG", "case": case}}}
            engine._review_recovery_control = MethodType(ResearchEngine._review_recovery_control, engine)
            engine._apply_delegation_judgment = MethodType(ResearchEngine._apply_delegation_judgment, engine)
            self.assertTrue(engine._review_recovery_control(request))
            engine.runtime.setdefault("history", []).append({"kind": "user_control", "request": request})
            judgments = [a for a in engine.runtime["queue"] if a.get("delegation_application_id")]
            self.assertEqual(len(judgments), 2)
            application_id = judgments[0]["delegation_application_id"]
            application = engine.runtime["delegation_applications"][application_id]
            for index, judgment in enumerate(judgments):
                eid = "EX-delegation-" + str(index)
                engine.runtime["executions"][eid] = {"id": eid, "role": "intent_interpretation", "status": "running",
                    "input_manifest": {"prompt": {"sha256": hashlib.sha256(("exact rendered prompt " + str(index)).encode()).hexdigest()}},
                    "delegation_input_sha256": application["input_sha256"]}
                engine._apply_delegation_judgment(judgment, {"delegation_judgment": {"input_sha256": application["input_sha256"], "decision": "within_scope", "reason": "This exact case stays within the original approved replacement"}}, eid)
            self.assertEqual(engine.runtime["delegation_applications"][application_id]["application"]["status"], "applied")
            self.assertTrue(any(a.get("replacement_for") == 0 for a in engine.runtime["queue"]))


class ReviewAttemptAdmissionTests(unittest.TestCase):
    def test_every_review_owned_attempt_uses_owner_admission_before_registration(self):
        engine = routing_engine()
        profile = next(p for p in execution_profiles.build_profiles(DEFAULT_CONFIG)["execution_profiles"].values()
                       if p["role"] == "supplemental_research")
        engine._execution_profile = create_autospec(engine._execution_profile, return_value=profile)
        engine._admit_review_execution = create_autospec(engine._admit_review_execution, return_value={"disposition": "review_followup_reserved"})
        engine._request_review_resource_disposition = create_autospec(engine._request_review_resource_disposition)
        action = {"id": "AC-review", "role": "supplemental_research", "owner_review_cycle_id": "RC-one"}
        engine.runtime["queue"] = [action]
        result = engine._register_execution(action, {"id": "EX-attempt", "role": action["role"], "status": "queued"})
        self.assertIsNone(result)
        execution = engine._admit_review_execution.call_args.args[1]
        self.assertEqual(execution["actor_kind"], "ai")
        self.assertEqual(execution["execution_profile_ref"], execution_profiles.profile_ref(profile))
        self.assertNotIn("EX-attempt", engine.runtime["executions"])
        engine._request_review_resource_disposition.assert_called_once_with(
            action, "review_followup_reserved", {"disposition": "review_followup_reserved"})


if __name__ == '__main__':
    unittest.main()
