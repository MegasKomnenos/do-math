"""Calls port contract (설계 2.2): the thread executor and the deterministic fake run calls alike.

``make()`` returns the port; ``port.new(...)`` returns an executor with the
ModelCalls surface the scheduler uses (start_call, wait, judge, pump, collect,
close, futures). The fake side runs here; the thread side is boundary/test_port_calls.py.
"""
import threading
import unittest

from support.fakes.calls import make_fake


def _generator(results):
    result = yield
    results.append(result)


def _drain(calls, limit=400):
    """Owner loop: wait and collect until every call is collected."""
    for _ in range(limit):
        calls.pump()
        calls.collect()
        if not calls.futures:
            return
        calls.wait(0.01)
    raise AssertionError('calls did not finish')


class CallsContract:
    def make(self):
        raise NotImplementedError

    def executor(self, **callbacks):
        calls = self.make().new(**callbacks)
        self.addCleanup(calls.close)
        return calls

    def start(self, calls, function, arguments, results, execution_id=None):
        generator = _generator(results)
        next(generator)
        return calls.start_call(generator, function, arguments, execution_id=execution_id)

    def test_a_returned_result_reaches_the_generator_and_on_returned(self):
        returned, results = [], []
        calls = self.executor(on_returned=lambda eid, result: returned.append((eid, result)))
        self.start(calls, lambda **_: {'status': 'completed'}, {}, results, execution_id='EX-1')
        _drain(calls)
        self.assertEqual(results, [{'status': 'completed'}])
        self.assertEqual(returned, [('EX-1', {'status': 'completed'})])

    def test_on_started_runs_on_the_owner_thread_and_answers_the_call(self):
        owner, seen, results = threading.get_ident(), [], []
        calls = self.executor()

        def started(value):
            seen.append(threading.get_ident())
            return value * 2

        self.start(calls, lambda on_started, **_: {'status': 'completed', 'started': on_started(21)},
                   {'on_started': started}, results)
        _drain(calls)
        self.assertEqual(seen, [owner])
        self.assertEqual(results[0]['started'], 42)

    def test_observations_apply_in_order_on_the_owner_before_collection(self):
        applied, results = [], []
        calls = self.executor()

        def run(on_observation, **_):
            for index in range(3):
                on_observation(index)
            return {'status': 'completed'}

        self.start(calls, run, {'on_observation': lambda index: applied.append((index, threading.get_ident()))}, results)
        _drain(calls)
        self.assertEqual([index for index, _ in applied], [0, 1, 2])
        self.assertEqual({thread for _, thread in applied}, {threading.get_ident()})
        self.assertEqual(len(results), 1)

    def test_a_raising_calculation_returns_the_failed_result(self):
        results = []
        calls = self.executor()

        def fail(**_):
            raise ValueError('boom')

        self.start(calls, fail, {}, results)
        _drain(calls)
        self.assertEqual(results, [{'status': 'failed', 'output': None, 'usage': {}, 'error': 'ValueError: boom'}])

    def test_a_stop_judged_true_at_start_is_visible_to_the_calculation(self):
        results = []
        calls = self.executor()
        self.start(calls, lambda should_stop, **_: {'status': 'stopped' if should_stop() else 'completed'},
                   {'should_stop': lambda: True}, results)
        _drain(calls)
        self.assertEqual(results, [{'status': 'stopped'}])

    def test_one_execution_has_at_most_one_live_call(self):
        calls = self.executor()
        self.start(calls, lambda **_: {'status': 'completed'}, {}, [], execution_id='EX-1')
        with self.assertRaisesRegex(ValueError, 'already has an active call'):
            self.start(calls, lambda **_: {'status': 'completed'}, {}, [], execution_id='EX-1')
        _drain(calls)


class DeterministicCallsContract(CallsContract, unittest.TestCase):
    def make(self):
        return make_fake()


if __name__ == '__main__':
    unittest.main()
