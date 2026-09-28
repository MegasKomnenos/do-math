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
from queue import Empty, Queue
from threading import Event, Lock, Thread


def failed_result(error):
    """The one result a call records when its calculation raised instead of returning."""
    return {"status": "failed", "output": None, "usage": {}, "error": f"{type(error).__name__}: {error}"}


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

    def _apply_observations(self, future):
        # Apply only the rows queued on entry: a running call keeps appending, and
        # an unbounded drain would starve the owner loop (dispatch, live reviews,
        # controls). A returned call appends nothing more, so collect applies all.
        for _ in range(len(future.observations)):
            function, args = future.observations.popleft()
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
            for _ in range(self.events.qsize()):
                try:
                    function, args, response = self.events.get_nowait()
                except Empty:
                    break
                try:
                    response.set_result(function(*args))
                except BaseException as error:
                    response.set_exception(error)
            for future in list(self.futures):
                self._apply_observations(future)
        finally:
            self.pumping = False

    def collect(self):
        if self.collecting:
            return 0
        self.collecting = True
        finished = 0
        try:
            for future in list(self.futures):
                if not future.done():
                    continue
                generator = self.futures[future]
                # The calculation queued its observations before it returned.
                self._apply_observations(future)
                try:
                    result = future.result()
                except Exception as error:
                    result = failed_result(error)
                error = future.judge_error
                if error is not None and isinstance(result, dict):
                    result = {**result, "status": "failed",
                              "error": f"stop judgment failed: {type(error).__name__}: {error}"}
                if self.on_returned is not None:
                    self.on_returned(future.execution_id, result)
                try:
                    generator.send(result)
                except StopIteration:
                    pass
                else:
                    raise RuntimeError("an execution yielded more than one call")
                self.futures.pop(future)
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
