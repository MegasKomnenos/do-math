"""Calls port contract (설계 2.2): the thread executor and the deterministic fake run calls alike.

``make()`` returns the port; ``port.new(...)`` returns an executor with the
ModelCalls surface the scheduler uses (start_call, wait, judge, pump, collect,
close, futures). The fake side runs here; the thread side is boundary/test_port_calls.py.
"""

import threading


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
    def track_threads(self, calls):
        """Return a reader retaining this executor's thread handles across close."""
        raise NotImplementedError

    def park_callback(self, calls):
        """Reach a pending start callback without applying its owner function."""
        raise NotImplementedError

    def assert_close_completion(self, calls, future, threads, results, returned):
        self.assertTrue(calls.stopping)
        self.assertTrue(future.stop.is_set())
        self.assertTrue(future.done(), 'close discarded the calculation that completes the Future')
        self.assertFalse(any(thread.is_alive() for thread in threads()))
        self.assertIn(future, calls.futures, 'abort still needs the original Future and generator')
        self.assertEqual(results, [])
        self.assertEqual(returned, [])

    def test_close_before_owner_progress_preserves_actual_result_and_exception(self):
        for raises in (False, True):
            with self.subTest(raises=raises):
                entered, stopped, finalized, applied, results, returned = [], [], [], [], [], []
                result, failure = {'status': 'stopped', 'evidence': object()}, ValueError('local cleanup failed')
                calls = self.executor(on_returned=lambda *args: returned.append(args))

                def run(should_stop, on_started):
                    entered.append('run')
                    try:
                        try:
                            on_started('identity')
                        except RuntimeError as error:
                            self.assertEqual(str(error), 'executor is shutting down')
                            stopped.append(should_stop())
                        if raises:
                            raise failure
                        return result
                    finally:
                        finalized.append('finally')

                future = self.start(calls, run, {'should_stop': lambda: False,
                    'on_started': applied.append}, results)
                threads = self.track_threads(calls)
                # No wait/pump: the real thread may have started; the fake has not.
                for _ in range(2):
                    calls.close()
                    self.assert_close_completion(calls, future, threads, results, returned)
                    self.assertEqual((entered, stopped, finalized, applied), (['run'], [True], ['finally'], []))
                    if raises:
                        self.assertIs(future.exception(timeout=0), failure)
                    else:
                        self.assertIs(future.result(timeout=0), result)

    def test_close_rejects_pending_start_callback_and_preserves_its_exception(self):
        calls = self.executor()
        entered, stopped, errors, finalized, applied, results = [], [], [], [], [], []

        def run(should_stop, on_started):
            entered.append('run')
            try:
                on_started('identity')
            except RuntimeError as error:
                stopped.append(should_stop())
                errors.append(error)
                raise
            finally:
                finalized.append('finally')

        future = self.start(calls, run, {'should_stop': lambda: False, 'on_started': applied.append}, results)
        threads = self.track_threads(calls)
        self.park_callback(calls)
        self.assertFalse(future.done())
        for _ in range(2):
            calls.close()
            self.assert_close_completion(calls, future, threads, results, [])
            self.assertEqual((entered, stopped, finalized, applied), (['run'], [True], ['finally'], []))
            self.assertEqual(len(errors), 1)
            self.assertIs(future.exception(timeout=0), errors[0])
            self.assertEqual(str(errors[0]), 'executor is shutting down')

    def test_close_preserves_already_returned_uncollected_calculation(self):
        calls = self.executor()
        entered, results = [], []
        result = {'status': 'completed', 'evidence': object()}
        future = self.start(calls, lambda: entered.append('run') or result, {}, results)
        threads = self.track_threads(calls)
        for _ in range(500):
            if future.done():
                break
            calls.wait(0.01)
        self.assertTrue(future.done(), 'calculation did not return within owner wait bound')
        for _ in range(2):
            calls.close()
            self.assert_close_completion(calls, future, threads, results, [])
            self.assertIs(future.result(timeout=0), result)
            self.assertEqual(entered, ['run'])

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
