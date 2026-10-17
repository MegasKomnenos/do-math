"""Run blocking adapters or machine calls; the owner thread judges stops and applies callbacks.

A calculation reads only its stop flag. The owner thread runs each call's stop
judgment after every head movement (and when a time-bound reason falls due)
and sets the flag once the judgment is true. ``on_started`` remains a
synchronous owner round trip because the identity must be published before
resume. Observations are queued per call without waiting; the owner applies a
call's observations in order, and all of them before it collects that call.
"""
from __future__ import annotations

from collections import deque
from concurrent.futures import Future
from contextvars import copy_context
from dataclasses import replace
from queue import Empty, Queue
from threading import Event, Lock, Thread

from .model_call import failed_result, judged_result
from .observation_transport import ObservationBatch


class ModelCalls:
    def __init__(self, *, on_returned=None, on_observation_error=None):
        self.events = Queue()
        self.futures = {}
        self.threads = []
        self.guard = Lock()
        self.pumping = False
        self.collecting = False
        self.judging = False
        self.stopping = False
        # The scheduler pins a shared allowance at owner-pass entry. Standalone
        # callers leave it unset and each pump takes its own entry snapshot.
        self._observation_limits = None
        self.on_returned = on_returned
        self.on_observation_error = on_observation_error
        # Set by anything the owner must handle: a callback request, an
        # observation or a returned call. The owner waits on it, not a spin.
        self.wake = Event()

    def _owner_call(self, function, args):
        """Run ``function(*args)`` on the owner thread and return its result to the calling thread."""
        response = Future()
        with self.guard:
            if self.stopping:
                raise RuntimeError("executor is shutting down")
            self.events.put((function, args, response))
            self.wake.set()
        from .operation_trace import phase
        with phase('callback_wait', callback=getattr(function, '__name__', 'callback')):
            return response.result()

    def _started(self, function):
        def call(*args):
            return self._owner_call(function, args)
        return call

    def _spawn(self, run):
        """Start one call's calculation off the owner thread."""
        context = copy_context()
        thread = Thread(target=lambda: context.run(run), name="do-math-call")
        self.threads.append(thread)
        thread.start()

    def _observed(self, function, future):
        def call(*args):
            with self.guard:
                if self.stopping:
                    raise RuntimeError("executor is shutting down")
                future.observations.append((function, args))
                self.wake.set()
        return call

    def start_call(self, generator, function, arguments, *, execution_id=None):
        arguments = dict(arguments)
        if execution_id is not None:
            if not isinstance(execution_id, str) or not execution_id:
                raise ValueError("execution_id must be a nonempty string")
            if any(future.execution_id == execution_id for future in self.futures):
                raise ValueError("an execution already has an active call")
        future = Future()
        future.execution_id = execution_id
        future.stop = Event()
        future.judge = arguments.get("should_stop")
        future.observations = deque()
        future.observation_failed = False
        future.judge_error = None
        if "should_stop" in arguments:
            arguments["should_stop"] = future.stop.is_set
        if "on_started" in arguments:
            arguments["on_started"] = self._started(arguments["on_started"])
        if "on_observation" in arguments:
            arguments["on_observation"] = self._observed(arguments["on_observation"], future)
        if self.stopping:
            future.stop.set()
        elif future.judge is not None:
            self._judge(future)  # The state at start may already require a stop.
        self.futures[future] = generator
        def run():
            try:
                future.set_result(function(**arguments))
            except BaseException as error:
                future.set_exception(error)
            finally:
                self.wake.set()
        self._spawn(run)
        return future

    def wait(self, timeout):
        """Owner thread: sleep until a call needs the owner, at most ``timeout`` seconds.

        A wake set after this returns stays set for the next wait; the pass that
        follows handles everything set before the clear.
        """
        self.wake.wait(timeout)
        self.wake.clear()

    def _judge(self, future):
        try:
            stop = future.judge()
        except Exception as error:
            # A failing judgment fails its own call, not the owner.
            future.judge_error, stop = error, True
        if stop:
            future.stop.set()

    def judge(self):
        """Owner thread: run the stop judgment of each live call whose flag is still clear."""
        if self.judging:
            return
        self.judging = True
        try:
            for future in list(self.futures):
                # A returned calculation no longer reads its flag; its continuation judges the result.
                if future.judge is not None and not future.stop.is_set() and not future.done():
                    self._judge(future)
        finally:
            self.judging = False

    def _apply_observations(self, future, *, limit=None, yield_to_returns=False, returned_at_entry=None):
        # A running call keeps appending: share the owner's entry allowance
        # across pumps, or use this standalone invocation's snapshot. A result
        # is collected only after all of its own rows have been applied.
        count = len(future.observations) if limit is None else limit
        if self._observation_limits is not None:
            count = min(count, self._observation_limits.get(future, 0))
        consumed = 0
        while consumed < count:
            # A completion arriving during a slow callback gets the next owner
            # opportunity, before any more unrelated backlog is applied. Only
            # collect resumes continuations, after the owner receives controls.
            if yield_to_returns and any(call.done() for call in self.futures):
                break
            if returned_at_entry is not None and any(
                    call.done() and call not in returned_at_entry for call in self.futures):
                # A return arrived while collect was paying another result's
                # observation debt. Finish the active publication, then return
                # to the owner for controls and a fresh completion ordering.
                break
            function, args = future.observations.popleft()
            taken = 1
            if (not future.observation_failed and future.done() and len(self.futures) == 1
                    and len(args) == 1 and isinstance(args[0], ObservationBatch)):
                # With only this returned call left, no competing calculation
                # can complete during its publication. Join its entry parts of
                # one read; preserve received coordinates and the read's tick.
                batch = last = args[0]
                events, offsets, rows = list(batch.events), list(batch.offsets), list(batch.rows)
                while consumed + taken < count and not last.ends_read:
                    _, next_args = future.observations[0]
                    # start_call installs one callback for this future; every
                    # queued observation uses that same function (_observed).
                    if len(next_args) != 1:
                        break
                    part = next_args[0]
                    if (not isinstance(part, ObservationBatch) or part.stream_path != batch.stream_path
                            or part.is_terminated is not batch.is_terminated
                            or (part.received_at, part.received_monotonic) !=
                               (batch.received_at, batch.received_monotonic)
                            or part.first_row != batch.first_row + len(rows)):
                        break
                    future.observations.popleft()
                    events.extend(part.events)
                    offsets.extend(part.offsets)
                    rows.extend(part.rows)
                    last, taken = part, taken + 1
                if taken > 1:
                    args = (replace(batch, events=events, offsets=offsets, rows=rows,
                                    end_offset=last.end_offset, ends_read=last.ends_read),)
            consumed += taken
            if self._observation_limits is not None:
                self._observation_limits[future] -= taken
            if future.observation_failed:
                continue  # Later rows depend on the one that could not be applied.
            try:
                function(*args)
            except Exception as error:
                # The call has not been collected yet: stop it and record why.
                future.observation_failed = True
                future.stop.set()
                if self.on_observation_error is not None:
                    self.on_observation_error(future.execution_id, error)

    def pump(self):
        if self.pumping or self.collecting:
            return
        self.pumping = True
        try:
            with self.guard:
                observations = [(future, len(future.observations)) for future in self.futures]
                events = self.events.qsize()
            for _ in range(events):
                try:
                    function, args, response = self.events.get_nowait()
                except Empty:
                    break
                try:
                    response.set_result(function(*args))
                except BaseException as error:
                    response.set_exception(error)
            for future, count in observations:
                if self._observation_limits is not None:
                    # Live observations precede transport/inbox controls in
                    # the owner. Return after one bounded callback per call,
                    # even when calculations are still waiting for receipts.
                    # collect can pay a returned call's own entry debt later.
                    count = min(count, 1)
                self._apply_observations(future, limit=count, yield_to_returns=True)
        finally:
            self.pumping = False

    def collect(self):
        if self.collecting:
            return 0
        self.collecting = True
        finished = 0
        try:
            # Results without observation debt (including machine calls) must
            # not wait behind another returned call's observation backlog.
            returned = tuple(future for future in self.futures if future.done())
            for future in sorted(returned, key=lambda call: len(call.observations)):
                generator = self.futures[future]
                # The calculation queued its observations before it returned.
                self._apply_observations(future, returned_at_entry=returned)
                if future.observations:
                    # Rows arriving after owner-pass entry belong to the next
                    # pass. Keep their result until its own rows are applied.
                    continue
                try:
                    result = future.result()
                except Exception as error:
                    result = failed_result(error)
                result = judged_result(result, future.judge_error)
                if self.on_returned is not None:
                    self.on_returned(future.execution_id, result)
                try:
                    generator.send(result)
                except StopIteration:
                    pass
                else:
                    raise RuntimeError("an execution yielded more than one call")
                self.futures.pop(future)
                if self._observation_limits is not None:
                    self._observation_limits.pop(future, None)
                finished += 1
        finally:
            self.collecting = False
        self.pump()
        self.threads[:] = [thread for thread in self.threads if thread.is_alive()]
        return finished

    def close(self):
        # The engine normally drains all calls first. On an unexpected owner
        # error, stop every calculation and unblock start callbacks so their
        # local termination runs.
        with self.guard:
            self.stopping = True
        for future in self.futures:
            future.stop.set()
            future.observations.clear()
        while True:
            try:
                _, _, response = self.events.get_nowait()
            except Empty:
                break
            response.set_exception(RuntimeError("executor is shutting down"))
        for thread in self.threads:
            thread.join()


class ThreadCalls:
    """Real calls port: each call's calculation runs on its own thread."""

    def new(self, *, on_returned=None, on_observation_error=None):
        return ModelCalls(on_returned=on_returned, on_observation_error=on_observation_error)
