"""Close the fake's explicit handoffs using the real ModelCalls run closure."""
import unittest

from support.fakes.calls import make_fake, owner_turn
from support.port_contracts.calls import _generator


class CallsCloseTurnsTests(unittest.TestCase):
    def start(self, calls, run, **arguments):
        generator = _generator([])
        next(generator)
        return calls.start_call(generator, run, arguments)

    def test_close_runs_every_unstarted_turn_once_after_all_stop_flags_are_set(self):
        calls = make_fake().new()
        self.addCleanup(calls.close)
        entered, finalized, futures = [], [], []
        results = [object(), object()]

        def run(index, should_stop):
            entered.append((index, calls.stopping, should_stop(), all(f.stop.is_set() for f in futures)))
            try:
                return results[index]
            finally:
                finalized.append(index)

        for index in range(2):
            futures.append(self.start(calls, run, index=index, should_stop=lambda: False))
        turns = list(calls.turns)
        self.assertEqual(entered, [])
        self.assertTrue(all(turn.thread is None for turn in turns))
        for _ in range(2):
            calls.close()
            self.assertEqual(entered, [(0, True, True, True), (1, True, True, True)])
            self.assertEqual(finalized, [0, 1])
            self.assertEqual(calls.turns, [])
            for index, future in enumerate(futures):
                self.assertTrue(future.done())
                self.assertIs(future.result(timeout=0), results[index])
            self.assertTrue(all(turn.thread is not None and not turn.thread.is_alive() for turn in turns))

    def test_close_unwinds_owner_turn_and_preserves_actual_return_or_exception(self):
        for raises in (False, True):
            with self.subTest(raises=raises):
                calls = make_fake().new()
                self.addCleanup(calls.close)
                entered, stopped, finalized = [], [], []
                result, failure = object(), ValueError('receipt cleanup failed')

                def run(should_stop):
                    entered.append('run')
                    try:
                        try:
                            owner_turn()
                        except RuntimeError as error:
                            self.assertEqual(str(error), 'executor is shutting down')
                            stopped.append(should_stop())
                        if raises:
                            raise failure
                        return result
                    finally:
                        finalized.append('finally')

                future = self.start(calls, run, should_stop=lambda: False)
                turn = calls.turns[0]
                calls.wait(0)
                self.assertEqual(turn.message, ('yield',))
                self.assertFalse(future.done())
                for _ in range(2):
                    calls.close()
                    self.assertEqual((entered, stopped, finalized), (['run'], [True], ['finally']))
                    self.assertTrue(future.done())
                    self.assertFalse(turn.thread.is_alive())
                    if raises:
                        self.assertIs(future.exception(timeout=0), failure)
                    else:
                        self.assertIs(future.result(timeout=0), result)

    def test_close_joins_a_done_turn_without_giving_it_another_turn(self):
        calls = make_fake().new()
        self.addCleanup(calls.close)
        entered, result = [], object()
        future = self.start(calls, lambda: entered.append('run') or result)
        turn = calls.turns[0]
        self.assertEqual(turn.give(None), ('done',))
        for _ in range(2):
            calls.close()
            self.assertIs(future.result(timeout=0), result)
            self.assertEqual(entered, ['run'])
            self.assertFalse(turn.thread.is_alive())
            self.assertEqual(calls.turns, [])
