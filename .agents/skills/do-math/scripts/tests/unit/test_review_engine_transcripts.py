"""The engine's identity review mixin (``review_engine``, layer 2): slot transcripts, restoration and recovery records.

Every test runs the product's ``ResearchEngine`` over the stored review state
of ``support.review_scene`` and calls the mixin as the owner does.
"""
from copy import deepcopy
import errno
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from do_math.canonical import canonical_json
from do_math.review_cycle import record_turn, validate_transcript
from support.review_scene import ReviewScene, warm


def setUpModule():
    warm()


class ReviewSceneCase(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.scene = ReviewScene(temporary.name)
        self.engine = self.scene.engine


class ObservedTranscriptTests(ReviewSceneCase):
    def test_current_proposal_message_restores_by_exact_ref_without_repeating_the_body(self):
        from do_math.values import compact_json_bytes
        engine, scene = self.engine, self.scene
        cid = scene.start('K1')
        action = scene.pending()
        cycle = engine.runtime['review_cycles'][cid]
        original = {'role': 'user', 'kind': 'proposal', 'content': deepcopy(cycle['proposal']),
                    'message_id': 'current-proposal'}
        cycle = record_turn(cycle, action['slot'], [original])
        engine.runtime['review_cycles'][cid] = cycle
        sealed = deepcopy((cycle['turns'], cycle['transcript_manifest']))
        workspace = scene.root / 'current-proposal'
        context = engine._prepare_review_context(action, workspace)['context']
        reference = context['source_refs'][0]
        self.assertEqual(context['proposal'], original['content'])
        self.assertEqual(context['self_messages'], [{'role': 'user', 'content': {'source_ref': reference}}])
        self.assertEqual(reference['proposal_digest'], cycle['proposal_digest'])
        raw = (workspace / reference['local_path']).read_bytes()
        self.assertEqual(raw, compact_json_bytes(original))
        self.assertEqual(len(raw), reference['bytes'])
        self.assertEqual(hashlib.sha256(raw).hexdigest(), reference['sha256'])
        self.assertEqual(sealed, (cycle['turns'], cycle['transcript_manifest']))
        # Missing materialized copies can be rebuilt from the verified original.
        (workspace / reference['local_path']).unlink()
        rebuilt = engine._prepare_review_context(action, workspace)
        self.assertEqual(rebuilt['disposition'], 'ready')
        self.assertEqual((workspace / reference['local_path']).read_bytes(), raw)
        (workspace / reference['local_path']).write_bytes(b'changed proposal source')
        event = engine._prepare_review_context(action, workspace)['recovery']['recovery_event']
        self.assertEqual(event['cause_kind'], 'materialized_content_mismatch')
        self.assertEqual(event['coordinate'], {'slot': action['slot'], 'index': 0,
                                              'path': str(workspace / reference['local_path'])})
        self.assertEqual(event['expected_sha256'], reference['sha256'])
        self.assertEqual(event['observed_sha256'], hashlib.sha256(b'changed proposal source').hexdigest())

    def test_actual_prompt_and_public_provider_events_restore_only_to_their_slot(self):
        engine, scene = self.engine, self.scene
        cid = scene.start('K1')
        action = deepcopy(scene.pending())
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
        own = engine._prepare_review_context(action, scene.root / 'own')['context']
        self.assertIn('PUBLIC EXPLANATION', json.dumps(own))
        contents = [(scene.root / 'own' / row['local_path']).read_text(encoding='utf-8') for row in own['source_refs']]
        self.assertTrue(any(prompt in text for text in contents))
        self.assertTrue(any('EXACT TOOL OUTPUT' in text for text in contents))
        peer = next(a for a in engine.runtime['queue'] if a['slot'] != action['slot'])
        peer_context = engine._prepare_review_context(peer, scene.root / 'peer')['context']
        self.assertNotIn('PUBLIC EXPLANATION', json.dumps(peer_context))
        self.assertEqual(peer_context['source_refs'], [])

    def test_observed_public_events_reject_out_of_order_append_but_allow_exact_replay(self):
        engine, scene = self.engine, self.scene
        scene.start('K1')
        engine.runtime['executions']['ORDER'] = {'id': 'ORDER', 'action': deepcopy(scene.pending())}
        event = {'type': 'public_message', 'message': {'role': 'assistant', 'content': 'later message'}}
        engine._record_review_observation('ORDER', event, artifact_ref='events.jsonl', event_index=3)
        engine._record_review_observation('ORDER', event, artifact_ref='events.jsonl', event_index=3)
        with self.assertRaisesRegex(ValueError, 'observed public review event arrived out of order'):
            engine._record_review_observation('ORDER', event, artifact_ref='events.jsonl', event_index=1)

    def test_public_provider_numbers_survive_storage_and_slot_restoration(self):
        engine, scene = self.engine, self.scene
        cid = scene.start('K1')
        action = deepcopy(scene.pending())
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
        restored = engine._prepare_review_context(action, scene.root / 'numeric-restoration')['context']
        self.assertEqual(len(restored['self_messages']), len(events))
        for reference in restored['source_refs']:
            raw = (scene.root / 'numeric-restoration' / reference['local_path']).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), reference['sha256'])
            self.assertEqual(json.loads(raw), turns[reference['index']])

    def test_source_recovery_has_exact_bytes_hash_and_relative_path(self):
        engine, scene = self.engine, self.scene
        cycle_id = scene.start('K1')
        cycle = engine.runtime['review_cycles'][cycle_id]
        source = dict(role='tool', content='Original source at line 12: quantifier', call='read',
                      arguments={'path': 'original.txt'}, message_id='source-1')
        engine.runtime['review_cycles'][cycle_id] = record_turn(cycle, 'initial-0', [source])
        action = scene.pending()
        workspace = scene.root / 'source-test'
        context = engine._prepare_review_context(action, workspace)['context']
        reference = context['source_refs'][0]
        path = workspace / reference['local_path']
        self.assertTrue(path.is_file())
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), reference['sha256'])
        self.assertEqual(json.loads(path.read_bytes()), source)
        self.assertFalse(Path(reference['local_path']).is_absolute())
        self.assertNotIn(source['content'], json.dumps(context))
        self.assertEqual(context['self_messages'][0]['content']['source_ref']['local_path'], reference['local_path'])
        engine._prepare_review_context(action, workspace)
        self.assertEqual(len(engine.runtime['review_cycles'][cycle_id]['turns']['initial-0']), 1)

    def test_input_delta_is_not_a_recursive_transcript_copy(self):
        """About 0.4 s, over the 0.2 s unit budget: eleven slots answer through two dispute rounds, each recording its input twice."""
        engine, scene = self.engine, self.scene
        cycle_id = scene.start('K1')
        scene.execute(dict(decision='mismatch', findings=[dict(id='f', statement='The domain is wrong', evidence=['proposal:1'])]))
        scene.execute()
        self.assertEqual(scene.pending()['stage'], 'organize')
        scene.execute()
        for _ in range(3): scene.execute(record_first=True)
        scene.execute(record_first=True)
        for _ in range(3): scene.execute(record_first=True)
        cycle = engine.runtime['review_cycles'][cycle_id]
        total_messages = sum(len(messages) for messages in cycle['turns'].values())
        self.assertEqual(total_messages, 3 * len(cycle['results']))
        for messages in cycle['turns'].values():
            for message in messages:
                if message.get('kind') == 'review_request':
                    self.assertNotIn('self_messages', message['content'])
                    self.assertNotIn('proposal', message['content'])
        self.assertEqual(len({m['message_id'] for messages in cycle['turns'].values() for m in messages}), total_messages)


class RestorationFailureTests(ReviewSceneCase):
    def test_restore_diagnostics_keep_exact_coordinate_hashes_and_verified_prefix(self):
        engine, scene = self.engine, self.scene
        cid = scene.start('K1')
        action = scene.pending()
        cycle = record_turn(engine.runtime['review_cycles'][cid], action['slot'], [
            {'role': 'assistant', 'content': 'verified first'}, {'role': 'assistant', 'content': 'original second'}])
        expected = cycle['transcript_manifest'][action['slot']][1]['sha256']
        cycle['turns'][action['slot']][1]['content'] = 'changed second'
        engine.runtime['review_cycles'][cid] = cycle
        outcome = engine._prepare_review_context(action, scene.root / 'broken')
        event = outcome['recovery']['recovery_event']
        self.assertEqual(event['cause_kind'], 'content_mismatch')
        self.assertEqual(event['coordinate'], {'slot': action['slot'], 'index': 1})
        self.assertEqual(event['expected_sha256'], expected)
        self.assertNotEqual(event['expected_sha256'], event['observed_sha256'])
        self.assertEqual(event['preserved_range']['verified_indices'], [0])
        self.assertFalse(event['retryable'])
        self.assertFalse(event['continuity_broken'])  # mismatch is not proof that every original copy is lost
        again = engine._prepare_review_context(action, scene.root / 'broken')
        self.assertEqual(again['recovery']['recovery_event'], event)
        self.assertEqual(len(engine.runtime['review_cycles'][cid]['recovery_events']), 1)

    def test_tampered_materialized_source_records_the_exact_file_hashes(self):
        engine, scene = self.engine, self.scene
        cid = scene.start('K1')
        action = scene.pending()
        engine.runtime['review_cycles'][cid] = record_turn(engine.runtime['review_cycles'][cid], action['slot'],
            [{'role': 'tool', 'content': 'exact original'}])
        workspace = scene.root / 'source'
        context = engine._prepare_review_context(action, workspace)['context']
        ref = context['source_refs'][0]
        (workspace / ref['local_path']).write_bytes(b'changed file')
        event = engine._prepare_review_context(action, workspace)['recovery']['recovery_event']
        self.assertEqual(event['expected_sha256'], ref['sha256'])
        self.assertEqual(event['observed_sha256'], hashlib.sha256(b'changed file').hexdigest())
        self.assertEqual(event['coordinate']['path'], str(workspace / ref['local_path']))

    def test_temporary_io_failure_preserves_reason_and_can_be_retried(self):
        """The file system refuses the review source folder with EAGAIN while the real context is built.

        The file system is not a port (설계 2.2); the operating system's
        temporary refusal is ``Path.mkdir`` raising for the one
        ``review-sources`` folder the context builder creates.
        """
        engine, scene = self.engine, self.scene
        scene.start('K1')
        original = Path.mkdir

        def unavailable(path, *args, **kwargs):
            if 'review-sources' in path.parts:
                raise OSError(errno.EAGAIN, 'sharing temporarily unavailable', 'source.json')
            return original(path, *args, **kwargs)
        with patch.object(Path, 'mkdir', unavailable):
            outcome = engine._prepare_review_context(scene.pending(), scene.root / 'temporary')
        self.assertEqual(outcome['disposition'], 'recovery_recorded')
        self.assertEqual((outcome['recovery']['disposition'], outcome['recovery']['next_owner']),
                         ('slot_restore_retry', 'review_recovery'))
        event = outcome['recovery']['recovery_event']
        self.assertTrue(event['retryable'])
        self.assertIn('sharing temporarily unavailable', event['reason'])
        self.assertEqual(event['coordinate']['path'], 'source.json')

    def test_restored_exact_bytes_release_the_held_slot_without_a_replacement(self):
        engine, scene = self.engine, self.scene
        cid = scene.start('K1')
        action = deepcopy(scene.pending())
        action['id'] = 'AC-held'
        good = record_turn(engine.runtime['review_cycles'][cid], action['slot'], [{'role': 'assistant', 'content': 'original'}])
        engine.runtime['review_cycles'][cid] = deepcopy(good)
        engine.runtime['review_cycles'][cid]['turns'][action['slot']][0]['content'] = 'corrupt'
        outcome = engine._prepare_review_context(action, scene.root / 'broken')
        engine.runtime['waiting_actions'] = {'AC-held': {'kind': 'review_input_restoration', 'action': action, 'recovery': outcome['recovery']}}
        engine.runtime['queue'] = []
        engine.runtime['review_cycles'][cid]['turns'] = deepcopy(good['turns'])
        resumed = engine._retry_review_restoration(action, scene.root / 'restored', at='now')
        self.assertEqual(resumed['disposition'], 'review_resumed')
        self.assertEqual(engine.runtime['waiting_actions'], {})
        self.assertTrue(engine.runtime['queue'])
        self.assertEqual(engine.runtime['review_cycles'][cid]['continuity_events'], [])


if __name__ == '__main__':
    unittest.main()
