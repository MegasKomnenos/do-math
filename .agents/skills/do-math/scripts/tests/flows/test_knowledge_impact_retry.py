"""The owner reads a held bundle's sealed bytes only once its requested impact review ended (``core_engine._retry_impact_reviews``).

``support.review_sim.impact_sim()`` holds research work whose bundle waits for
an independent impact review; the review is queued, not run. The legacy test
built that wait on a ``bare_engine`` with an autospec store, replaced
``submission.read_sealed_submission`` with a reader that always failed and
``_hold_unreadable_impact_submission`` with an autospec double. Here the
owner's retry and the review run for real on a Sim. While the review's model
call runs (its input, which holds the producer's sealed output, is already
fixed), the producer's accepted receipt stops matching its sealed output, so
the owner's next read of those bytes fails. Calls are observed as they start
(``ObservedCalls``). The review is a model call, so the scene is longer than
one Sim test's budget (설계 5.4 흐름 폴더).

``UnreadableBeforeReviewTests`` reproduces KD-0600: the producer's stored
output changed in the repository (same length, so the owner's pre-write
presence and length inspection passes) before the review is prepared, and a
new owner process (no process-level artifact knowledge) runs the owner pass.
"""
import hashlib
import unittest

from do_math import repository, submission
from support.known_defects import known_defect
from support.model import Answer
from support.provider_probes import ObservedCalls
from support.review_sim import held_impact, impact_review_answer, impact_sim, warm_impact

UNMATCHED = '0' * 64


def setUpModule():
    warm_impact()


def output_row(execution):
    """The producer's receipt row for its sealed output."""
    output_ref = execution['submission_intent']['output_ref']
    return next(row for row in execution['submission_receipt']['payload']['submission_check']['artifacts']
                if row['path'] == output_ref)


def read_by(arguments):
    """Whose sealed submission a read opens, and whether that receipt still matched its output as the read began."""
    execution = arguments['execution']
    return execution['id'], output_row(execution)['sha256'] != UNMATCHED if execution.get('submission_receipt') else None


class ImpactReviewRetryTests(unittest.TestCase):
    def test_sealed_bytes_are_read_only_after_every_requested_review_ended(self):
        """About 2 s: the impact review runs as a model call in one owner pass (on the impact template it shares with ``flows.test_review_impact_routing``)."""
        sim = impact_sim()
        waiting, producer, _, _ = held_impact(sim)
        engine = sim.engine
        # Control processing retries every waiting item; a pending review reads nothing.
        with ObservedCalls(read=submission.read_sealed_submission, hold=engine._hold_unreadable_impact_submission) as observed:
            engine._retry_impact_reviews()
        self.assertEqual((observed.calls['read'], observed.calls['hold']), ([], []))
        approve = impact_review_answer()

        def unmatched_then_approve(output, context):
            execution = sim.engine.runtime['executions'][producer['id']]
            output_row(execution)['sha256'] = UNMATCHED
            execution['submission_intent'].pop('output_sha256', None)
            return approve.make(output, context)
        sim.model.on('maintenance', stage='impact_review').reply(Answer(unmatched_then_approve))
        with ObservedCalls(capture={'read': read_by, 'hold': lambda arguments: arguments['waiting']['action']['id']},
                           read=submission.read_sealed_submission,
                           hold=engine._hold_unreadable_impact_submission) as observed:
            sim.step()  # the review runs and is received; the owner's retry then reads the held bundle
        [review] = [row for row in sim.runtime['executions'].values()
                    if row.get('role') == 'maintenance' and row.get('action', {}).get('stage') == 'impact_review']
        self.assertEqual((review['status'], review['outcome']), ('ended', 'output_accepted'))
        # Every sealed read of the pass, in order: the review's input read the producer's bytes before its call,
        # the receiver read the review's own sealed output, and after the review ended the retry read the
        # producer's bytes once (now unmatched) and held it without reading the review again.
        self.assertEqual(observed.calls['read'], [('do_math.core_engine', (producer['id'], True)),
                                                  ('do_math.core_engine', (review['id'], True)),
                                                  ('do_math.core_engine', (producer['id'], False))])
        self.assertEqual([action for _, action in observed.calls['hold']], [waiting['action']['id']])
        held = sim.runtime['waiting_actions'][waiting['action']['id']]
        # The hold routes the unreadable submission to a diagnosis of the producer (active lifecycle).
        self.assertEqual((held['kind'], held['next_owner']), ('submission_failure', 'operational_review'))
        self.assertIn('sealed output_ref hash differs', held['reason'])
        self.assertEqual([row.get('target') for row in sim.runtime['queue'] if row['role'] == 'operational_review'],
                         [producer['id']])


def damage_stored_output(sim, execution):
    """Change one byte of ``execution``'s stored sealed output in the Git fake, keeping its length."""
    engine = sim.engine
    raw = engine.store.read(execution['submission_intent']['output_ref'], engine.head)
    oid = hashlib.sha1(b'blob %d\0' % len(raw) + raw).hexdigest()
    [stored] = [objects for objects in sim.ports.git_backend.objects.values() if oid in objects]
    kind, body = stored[oid]
    changed = body.replace(b'a', b'b', 1)
    if changed == body or len(changed) != len(body):
        raise AssertionError('the fixture could not change the stored output in place')
    stored[oid] = (kind, changed)


def new_owner_process(sim):
    """A new owner process on the same repository: a restart, without this process's knowledge of artifact bytes."""
    sim.restart()


class UnreadableBeforeReviewTests(unittest.TestCase):
    @known_defect('KD-0600')
    def test_an_unreadable_held_submission_is_consumed_once_before_its_review_is_prepared(self):
        """About 2 s on the impact template: two owner passes, no model call."""
        sim = impact_sim()
        waiting, producer, _, _ = held_impact(sim)
        damage_stored_output(sim, producer)
        new_owner_process(sim)

        def owner_pass():
            try:
                sim.step()
            except submission.SealedSubmissionError as error:
                self.fail('the unreadable sealed submission raised out of the owner pass: ' + str(error))

        def review_attempts():
            return [row['id'] for row in sim.runtime['executions'].values()
                    if row.get('action', {}).get('stage') == 'impact_review']
        owner_pass()
        # The held item is consumed once: it waits as a submission failure, as the retry path holds it.
        held = sim.runtime['waiting_actions'][waiting['action']['id']]
        self.assertEqual(held['kind'], 'submission_failure')
        attempts = review_attempts()
        self.assertLessEqual(len(attempts), 1)
        owner_pass()  # the next pass proceeds and does not prepare the same review again
        self.assertEqual(review_attempts(), attempts)


if __name__ == '__main__':
    unittest.main()
