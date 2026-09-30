"""The calls manager (``parallel.ModelCalls``, layer 3) on real threads: collection, stop flags, owner waits and observations.

A calculation runs on its own thread and reads only its stop flag; the owner
thread judges stops, answers start callbacks, applies queued observations and
collects returned calls, resuming each call's continuation (a generator that
yields once). Calculations here poll their flag with a bound (``reached``).
"""
import threading
import time
import unittest

from do_math.parallel import ModelCalls
from test_categories import test_group


def reached(predicate, timeout):
    """Poll ``predicate`` until it holds or ``timeout`` seconds pass; whether it held."""
    deadline = time.monotonic() + timeout
    pause = threading.Event()
    while time.monotonic() < deadline:
        if predicate():
            return True
        pause.wait(0.01)
    return bool(predicate())


def flag_waiter(result):
    """A calculation that reads its stop flag until it is set (at most 30 s), then returns ``result``."""
    def wait(should_stop):
        reached(should_stop, 30)
        return dict(result)
    return wait


def drain(calls, timeout=5):
    """The owner collects until no call is pending or ``timeout`` seconds pass."""
    reached(lambda: not calls.collect() and not calls.futures, timeout)


def continuation(into):
    """A call's continuation, ready for ``start_call``: it records the result it is resumed with."""
    def body():
        into.append((yield))
    generator = body()
    next(generator)
    return generator


class CallManagerTests(unittest.TestCase):
    def test_collection_releases_finished_threads_but_retains_a_live_call(self):
        calls = ModelCalls()
        release = threading.Event()
        returned = []

        def wait_for_release():
            release.wait()
            return "released"

        calls.start_call(continuation(returned), wait_for_release, {}, execution_id="EX-live")
        live_thread = calls.threads[-1]
        try:
            for index in range(16):
                future = calls.start_call(continuation(returned), lambda value: value,
                                          {"value": index}, execution_id="EX-finished-" + str(index))
                thread = calls.threads[-1]
                self.assertEqual(future.result(timeout=5), index)
                thread.join(timeout=5)
                self.assertFalse(thread.is_alive())
                self.assertEqual(calls.collect(), 1)
                self.assertEqual(calls.threads, [live_thread])
                self.assertEqual(len(calls.futures), 1)
            self.assertEqual(returned, list(range(16)))
        finally:
            release.set()
            calls.close()
        self.assertEqual(calls.collect(), 1)
        self.assertEqual(calls.collect(), 0)
        self.assertEqual(returned, [*range(16), "released"])
        self.assertEqual(calls.threads, [])
        self.assertEqual(calls.futures, {})

    @test_group('resource')
    def test_close_sets_every_stop_flag_and_fails_pending_start_callbacks(self):
        calls = ModelCalls()
        seen = []
        calls.start_call(continuation(seen), flag_waiter({'stopped': True}), {'should_stop': lambda: False},
                         execution_id='EX-one')
        calls.start_call(continuation(seen), lambda on_started: on_started({}),
                         {'on_started': lambda identity: self.fail('must not run')}, execution_id='EX-two')
        reached(lambda: calls.events.qsize() >= 1, 3)
        self.assertEqual(calls.events.qsize(), 1, 'only the start callback waits for the owner')
        calls.close()
        self.assertEqual(calls.collect(), 2)
        self.assertEqual(calls.collect(), 0)
        self.assertIn({'stopped': True}, seen)
        self.assertTrue(any(r.get('status') == 'failed' for r in seen))
        self.assertFalse(any(t.is_alive() for t in calls.threads))

    def test_owner_wait_wakes_on_a_returned_call_not_its_bound(self):
        calls = ModelCalls()
        release = threading.Event()
        calls.start_call(continuation([]), lambda: release.wait(5), {}, execution_id='EX-wake')
        calls.wait(0)
        release.set()
        started = time.monotonic()
        calls.wait(30)
        self.assertLess(time.monotonic() - started, 5, 'a returned call wakes the owner')
        calls.collect()
        started = time.monotonic()
        calls.wait(.2)
        self.assertGreaterEqual(time.monotonic() - started, .15, 'nothing pending: the bound paces the owner')
        calls.close()

    def test_stop_flag_reads_never_wait_for_the_owner(self):
        calls = ModelCalls()
        judged = []

        def poll(should_stop):
            started = time.monotonic()
            for _ in range(1000):
                should_stop()
            return {'stopped': should_stop(), 'seconds': time.monotonic() - started}
        # The owner never pumps while the calculation polls its flag.
        future = calls.start_call(continuation(judged), poll, {'should_stop': lambda: judged.append('judged') or False},
                                  execution_id='EX-poll')
        result = future.result(timeout=5)
        self.assertFalse(result['stopped'])
        self.assertLess(result['seconds'], 1)
        self.assertEqual(judged, ['judged'], 'the judgment runs on the owner, once at start')
        calls.close()

    def test_owner_judgment_sets_the_flag_once_and_stops_the_calculation(self):
        calls = ModelCalls()
        owner = threading.get_ident()
        reasons, returned, judgments = [], [], []

        def judge():
            self.assertEqual(threading.get_ident(), owner)
            judgments.append(bool(reasons))
            return bool(reasons)
        future = calls.start_call(continuation(returned), flag_waiter({'status': 'stopped'}), {'should_stop': judge},
                                  execution_id='EX-judged')
        calls.judge()
        self.assertFalse(future.stop.is_set())
        reasons.append('paused')  # A published stop reason.
        calls.judge()
        calls.judge()  # A set flag is not judged again.
        drain(calls)
        self.assertEqual(returned, [{'status': 'stopped'}])
        self.assertEqual(judgments, [False, False, True])
        calls.close()

    def test_failed_judgment_fails_only_its_own_call(self):
        calls = ModelCalls()
        returned = []
        state = {'fail': False}

        def judge():
            if state['fail']:
                raise KeyError('missing record')
            return False
        calls.start_call(continuation(returned), flag_waiter({'status': 'stopped', 'evidence': 'kept'}),
                         {'should_stop': judge}, execution_id='EX-broken')
        state['fail'] = True
        calls.judge()  # The owner does not raise.
        drain(calls)
        self.assertEqual(returned[0]['status'], 'failed')
        self.assertEqual(returned[0]['evidence'], 'kept')
        self.assertIn('stop judgment failed: KeyError', returned[0]['error'])
        calls.close()

    def test_observations_queue_without_waiting_and_apply_before_collection(self):
        failures, applied, order = [], [], []
        calls = ModelCalls(on_observation_error=lambda eid, error: failures.append((eid, str(error))))

        def collected():
            def body():
                order.append(('collected', (yield)))
            generator = body()
            next(generator)
            return generator

        def observe(item):
            if item == 'bad':
                raise ValueError('unapplied observation')
            applied.append(item)
            order.append(('applied', item))

        def produce(on_observation, should_stop):
            for item in ('one', 'two'):
                on_observation(item)  # Returns without an owner round trip.
            return {'status': 'completed'}
        future = calls.start_call(collected(), produce, {'on_observation': observe, 'should_stop': lambda: False},
                                  execution_id='EX-observed')
        future.result(timeout=5)
        self.assertEqual(applied, [], 'nothing is applied until the owner pumps')
        self.assertEqual(calls.collect(), 1)
        self.assertEqual(order, [('applied', 'one'), ('applied', 'two'), ('collected', {'status': 'completed'})])

        def fail_then_wait(on_observation, should_stop):
            on_observation('bad')
            reached(should_stop, 30)
            return {'status': 'stopped'}
        calls.start_call(collected(), fail_then_wait, {'on_observation': observe, 'should_stop': lambda: False},
                         execution_id='EX-failed-observation')
        drain(calls)
        self.assertEqual(failures, [('EX-failed-observation', 'unapplied observation')])
        self.assertEqual(order[-1], ('collected', {'status': 'stopped'}))
        calls.close()

    def test_one_pump_applies_only_the_rows_queued_before_it(self):
        # A call producing faster than the owner applies must not hold the owner
        # inside one pump (dispatch, live reviews, controls); the rest waits a pass.
        calls = ModelCalls()
        release, applied, emit = threading.Event(), [], []

        def collected():
            def body():
                applied.append(('collected', (yield)))
            generator = body()
            next(generator)
            return generator

        def observe(item):
            applied.append(item)
            if not release.is_set() and item < 50:
                emit[0](item + 2)  # The call keeps producing while the owner applies.

        def produce(on_observation, should_stop):
            emit.append(on_observation)
            on_observation(0)
            on_observation(1)
            release.wait(5)
            return {'status': 'completed'}
        future = calls.start_call(collected(), produce, {'on_observation': observe, 'should_stop': lambda: False},
                                  execution_id='EX-streaming')
        reached(lambda: len(future.observations) >= 2, 5)
        calls.pump()
        self.assertEqual(applied, [0, 1])
        self.assertEqual([args for _, args in future.observations], [(2,), (3,)])
        release.set()
        future.result(timeout=5)
        self.assertEqual(calls.collect(), 1)
        self.assertEqual(applied, [0, 1, 2, 3, ('collected', {'status': 'completed'})])
        calls.close()


if __name__ == '__main__':
    unittest.main()
