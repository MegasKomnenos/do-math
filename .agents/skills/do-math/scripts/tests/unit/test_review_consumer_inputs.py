"""Direct consumer boundaries preserve normal producer state; undecided outcomes are observations."""
from copy import deepcopy

from do_math import revisions, review_cycle as rc
from support.gap_inputs import ExecutedLines, observation
from support.observation_inputs import observation_batch
from support.review_owner_inputs import ReviewOwnerCase
from support.review_scene import warm


def setUpModule():
    warm()


class DirectConsumerInputs(ReviewOwnerCase):
    def test_empty_lineage_probe_preserves_registered_proposal_and_normal_caller(self):
        instance, runtime = self.engine.instance, self.engine.runtime
        action = {'role': 'research_work', 'revision_targets': {'K1': {}}}
        normal = revisions.proposal_lineage(instance, 'K1')
        waits = revisions.action_repetition_waits(instance, runtime, action)
        before = deepcopy((instance, runtime, action))
        # Empty ID rejection/optional return is not yet a decided contract.
        with ExecutedLines(revisions.proposal_lineage) as reached:
            result = revisions.proposal_lineage(instance, '')
        observation('P3-direct', result=result, lines=reached.lines,
                    contract='undecided; result is not the asserted oracle')
        bad = {**action, 'revision_targets': {'': {}}}
        try:
            result = revisions.action_repetition_waits(instance, runtime, bad)
        except (ValueError, TypeError) as error:
            observation('P3-caller', error_type=type(error).__name__, error=str(error))
        else:
            observation('P3-caller', result=result)
        self.assertEqual((instance, runtime, action), before)
        self.assertEqual(revisions.proposal_lineage(instance, 'K1'), normal)
        self.assertEqual(normal, ('K1', 1))
        self.assertEqual(revisions.action_repetition_waits(instance, runtime, action), waits)

    def test_missing_execution_probe_keeps_batch_bytes_and_normal_coordinate(self):
        _, _, execution = self.registered()
        stream = self.root / 'stdout.jsonl'
        batch = observation_batch([{'type': 'assistant', 'text': 'exact row'}],
            received_monotonic=self.engine.ports.clock.monotonic(), stream_path=stream)
        before = deepcopy((self.engine.instance, self.engine.runtime, batch.rows, batch.events, batch.offsets))
        receipt_key = 'a' * 64
        with ExecutedLines(self.engine._review_observation_source) as reached:
            try:
                result = self.engine._review_observation_source('EX-not-registered', batch, 0, receipt_key)
            except (KeyError, ValueError) as error:
                observation('V2-direct', error_type=type(error).__name__, error=str(error),
                            contract='undecided; no public deletion transition asserted')
            else:
                observation('V2-direct', result=result)
        observation('V2-lines', lines=reached.lines)
        self.assertEqual((self.engine.instance, self.engine.runtime, batch.rows, batch.events, batch.offsets), before)
        actual = self.engine._review_observation_source(execution['id'], batch, 0, receipt_key)
        self.assertEqual(actual['raw'], batch.rows[0])
        self.assertEqual(actual['event_index'], batch.first_row)
        self.assertEqual(actual['artifact_ref'], f'runtime/artifacts/BA-provider-{receipt_key}/provider-event.jsonl')
        self.assertEqual(actual['source'], batch.source(batch.offsets[0][1], start_offset=batch.offsets[0][0]))
        self.assertEqual((self.engine.instance, self.engine.runtime), before[:2])
