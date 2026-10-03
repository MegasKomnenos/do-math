"""Calls port contract (설계 2.2): the thread executor and the deterministic fake run calls alike.

``make()`` returns the port; ``port.new(...)`` returns an executor with the
ModelCalls surface the scheduler uses (start_call, wait, judge, pump, collect,
close, futures). The fake side runs here; the thread side is boundary/test_port_calls.py.
"""
import unittest

from support.fakes.calls import make_fake


from support.port_contracts.calls import _generator, _drain, CallsContract

class DeterministicCallsContract(CallsContract, unittest.TestCase):
    def track_threads(self, calls):
        turns = list(calls.turns)
        return lambda: [turn.thread for turn in turns if turn.thread is not None]

    def park_callback(self, calls):
        self.assertEqual(calls.turns[0].give(None)[0], 'owner_call')

    def make(self):
        return make_fake()


class DeterministicCallsTests(unittest.TestCase):
    """Fake-only semantics: one of the owner and the calls runs at a time, switching only at stated points."""

    def executor(self):
        calls = make_fake().new()
        self.addCleanup(calls.close)
        return calls

    def test_owner_loss_keeps_started_cleanup_outcomes_without_applying_old_work(self):
        from support.fakes.calls import owner_turn

        for boundary in ('yield', 'owner_call'):
            for raises in (False, True):
                with self.subTest(boundary=boundary, raises=raises):
                    applied, results, returned, finalized, unstarted = [], [], [], [], []
                    result, failure = object(), ValueError('started cleanup failed')
                    calls = make_fake().new(on_returned=lambda *args: returned.append(args))
                    self.addCleanup(calls.close)

                    def run(should_stop, on_started, on_observation):
                        on_observation('queued before owner loss')
                        try:
                            if boundary == 'yield':
                                owner_turn()
                            else:
                                on_started('identity')
                        except RuntimeError as error:
                            self.assertEqual(str(error), 'executor is shutting down')
                            self.assertTrue(should_stop())
                            if raises:
                                raise failure
                            return result
                        finally:
                            finalized.append('finally')

                    generator = _generator(results)
                    next(generator)
                    started = calls.start_call(generator, run, {
                        'should_stop': lambda: False, 'on_started': applied.append,
                        'on_observation': applied.append})
                    turn, = calls.turns
                    self.assertEqual(turn.give(None)[0], boundary)
                    pending = calls.start_call(None, lambda: unstarted.append('ran'), {})
                    pending_turn = calls.turns[-1]
                    self.assertFalse(started.done())
                    for _ in range(2):
                        calls.abandon_owner()
                        self.assertFalse(turn.thread.is_alive())
                        self.assertIsNone(pending_turn.thread)
                        self.assertTrue(pending.cancelled())
                        self.assertTrue(started.stop.is_set() and pending.stop.is_set())
                        self.assertFalse(started.cancelled())
                        if raises:
                            self.assertIs(started.exception(timeout=0), failure)
                        else:
                            self.assertIs(started.result(timeout=0), result)
                        self.assertEqual(finalized, ['finally'])
                        self.assertFalse(started.observations)
                        self.assertEqual((calls.turns, calls.futures), ([], {}))
                        calls.wait(0)
                        calls.pump()
                        self.assertEqual(calls.collect(), 0)
                        self.assertEqual((applied, results, returned, unstarted), ([], [], [], []))

    def test_a_call_waiting_for_the_owner_continues_after_an_owner_pass_and_sees_its_work(self):
        from support.fakes.calls import owner_turn
        inbox, receipts, results = [], [], []
        calls = self.executor()

        def worker(**_):
            inbox.append('request')          # as a worker writes a control request
            while not receipts:
                owner_turn()                 # as it waits for the owner's receipt
            return {'status': 'completed', 'receipt': receipts[0]}

        generator = _generator(results)
        next(generator)
        calls.start_call(generator, worker, {})
        for _ in range(10):
            calls.pump()
            calls.collect()
            if not calls.futures:
                break
            if inbox and not receipts:
                receipts.append('accepted ' + inbox[0])  # the owner pass handles the request
            calls.wait(0.01)
        self.assertEqual(results, [{'status': 'completed', 'receipt': 'accepted request'}])

    def test_calls_run_one_at_a_time_in_the_chosen_order(self):
        order, results = [], []
        calls = self.executor()
        for name in ('first', 'second'):
            generator = _generator(results)
            next(generator)
            calls.start_call(generator, lambda name=name, **_: order.append(name) or {'status': name}, {})
        self.assertEqual(order, [], 'a call runs only when the owner waits')
        _drain(calls)
        self.assertEqual(order, ['first', 'second'])

    def test_closing_releases_a_call_still_waiting_for_the_owner(self):
        from support.fakes.calls import owner_turn
        released = []
        calls = make_fake().new()

        def worker(**_):
            try:
                while True:
                    owner_turn()
            except RuntimeError as error:
                released.append(str(error))
                raise

        generator = _generator([])
        next(generator)
        calls.start_call(generator, worker, {})
        calls.wait(0.01)
        calls.close()
        self.assertEqual(released, ['executor is shutting down'])


if __name__ == '__main__':
    unittest.main()
