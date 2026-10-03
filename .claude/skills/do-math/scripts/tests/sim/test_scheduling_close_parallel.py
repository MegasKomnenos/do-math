"""parallel의 미실행 오류·재진입 분기. 이 직접 시험을 엔진 의무 증거로 세지 않는다."""
from concurrent.futures import Future
import unittest

from do_math.parallel import ModelCalls, ThreadCalls
from support.fakes.calls import DeterministicCalls


def continuation(results):
    def receive():
        results.append((yield))
    value = receive()
    next(value)
    return value


class ParallelBranchTests(unittest.TestCase):
    def test_callback_shutdown_drains_snapshot_queue_without_losing_responses(self):
        calls = ModelCalls()
        first, second = Future(), Future()
        calls.events.put((calls.close, (), first))
        calls.events.put((lambda: '호출되면 안 됨', (), second))
        calls.pump()
        self.assertIsNone(first.result(timeout=0))
        with self.assertRaisesRegex(RuntimeError, '^executor is shutting down$'):
            second.result(timeout=0)
        self.assertEqual(calls.events.qsize(), 0)
        self.assertFalse(calls.pumping)
        self.assertTrue(calls.stopping)

    def test_stopped_manager_rejects_owner_callback_and_observation(self):
        calls = ModelCalls()
        calls.close()
        with self.assertRaisesRegex(RuntimeError, '^executor is shutting down$'):
            calls._owner_call(lambda: '사용되지 않음', ())
        with self.assertRaisesRegex(RuntimeError, '^executor is shutting down$'):
            calls._observed(lambda value: None, Future())('관찰')
        self.assertEqual(calls.events.qsize(), 0)
        self.assertEqual(calls.futures, {})

    def test_invalid_execution_identity_does_not_start_a_calculation(self):
        calls = DeterministicCalls()
        seen = []
        for eid in ('', 0, [], False):
            with self.subTest(eid=eid):
                generator = continuation(seen)
                try:
                    with self.assertRaisesRegex(ValueError, '^execution_id must be a nonempty string$'):
                        calls.start_call(generator, lambda: 1, {}, execution_id=eid)
                finally:
                    generator.close()
        self.assertEqual(calls.futures, {})
        self.assertEqual(calls.turns, [])
        self.assertEqual(seen, [])

    def test_start_after_close_observes_a_set_stop_flag(self):
        calls = DeterministicCalls()
        seen = []
        calls.close()
        calls.start_call(continuation(seen), lambda should_stop: {'stopped': should_stop()},
                         {'should_stop': lambda: False}, execution_id='EX-stop')
        calls.wait(0)
        self.assertEqual(calls.collect(), 1)
        self.assertEqual(seen, [{'stopped': True}])
        self.assertEqual(calls.futures, {})
        calls.close()

    def test_callback_exception_is_delivered_to_its_own_response(self):
        calls = ModelCalls()
        response = Future()

        def reject():
            raise ValueError('개별 시작 callback 거부')

        calls.events.put((reject, (), response))
        calls.pump()
        with self.assertRaisesRegex(ValueError, '^개별 시작 callback 거부$'):
            response.result(timeout=0)
        self.assertFalse(calls.pumping)
        self.assertEqual(calls.events.qsize(), 0)
        calls.close()

    def test_collect_reentry_does_not_resume_a_continuation_twice(self):
        calls = DeterministicCalls()
        received = []

        def body():
            result = yield
            received.append((result, calls.collect()))

        generator = body()
        next(generator)
        calls.start_call(generator, lambda: {'value': 7}, {}, execution_id='EX-once')
        calls.wait(0)
        self.assertEqual(calls.collect(), 1)
        self.assertEqual(received, [({'value': 7}, 0)])
        self.assertEqual(calls.collect(), 0)
        self.assertEqual(calls.futures, {})
        calls.close()

    def test_second_yield_is_a_precise_contract_error(self):
        calls = DeterministicCalls()

        def twice():
            yield
            yield

        generator = twice()
        next(generator)
        calls.start_call(generator, lambda: {'value': 7}, {}, execution_id='EX-twice')
        calls.wait(0)
        try:
            with self.assertRaisesRegex(RuntimeError, '^an execution yielded more than one call$'):
                calls.collect()
            self.assertFalse(calls.collecting)
            self.assertEqual(len(calls.futures), 1)
        finally:
            generator.close()
            calls.close()

    def test_real_calls_factory_keeps_callbacks(self):
        returned, failed = [], []
        calls = ThreadCalls().new(on_returned=returned.append, on_observation_error=failed.append)
        self.assertIsInstance(calls, ModelCalls)
        self.assertEqual(calls.on_returned, returned.append)
        self.assertEqual(calls.on_observation_error, failed.append)
        calls.close()
        self.assertTrue(calls.stopping)
