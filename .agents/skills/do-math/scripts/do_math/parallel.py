"""Run blocking adapters or machine calls; engine callbacks stay on the owner thread."""
from __future__ import annotations

from concurrent.futures import Future
from contextvars import copy_context
from queue import Empty, Queue
from threading import Lock, Thread


class ModelCalls:
    def __init__(self, *, on_returned=None):
        self.events = Queue()
        self.futures = {}
        self.threads = []
        self.guard = Lock()
        self.pumping = False
        self.collecting = False
        self.stopping = False
        self.on_returned = on_returned

    def _callback(self, function, *, stop=False):
        def call(*args):
            response = Future()
            with self.guard:
                if self.stopping:
                    if stop:
                        return True
                    raise RuntimeError("executor is shutting down")
                self.events.put((function, args, response, stop))
            from .operation_trace import phase
            with phase('callback_wait', callback=getattr(function, '__name__', 'callback')):
                return response.result()
        return call

    def start(self, generator, runner, arguments, *, execution_id=None):
        return self.start_call(generator, runner.run, arguments, execution_id=execution_id)

    def start_call(self, generator, function, arguments, *, execution_id=None):
        arguments = dict(arguments)
        if execution_id is not None:
            if not isinstance(execution_id, str) or not execution_id:
                raise ValueError("execution_id must be a nonempty string")
            if any(getattr(future, "execution_id", None) == execution_id for future in self.futures):
                raise ValueError("an execution already has an active call")
        for key in ("on_started", "on_observation", "should_stop"):
            if key in arguments:
                arguments[key] = self._callback(arguments[key], stop=key == "should_stop")
        future = Future()
        future.execution_id = execution_id
        self.futures[future] = generator
        def run():
            try:
                future.set_result(function(**arguments))
            except BaseException as error:
                future.set_exception(error)
        context = copy_context()
        thread = Thread(target=lambda: context.run(run), name="do-math-call")
        self.threads.append(thread)
        thread.start()
        return future

    def pump(self):
        if self.pumping or self.collecting:
            return
        self.pumping = True
        try:
            for _ in range(self.events.qsize()):
                try:
                    function, args, response, _ = self.events.get_nowait()
                except Empty:
                    break
                try:
                    response.set_result(function(*args))
                except BaseException as error:
                    response.set_exception(error)
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
                try:
                    result = future.result()
                except Exception as error:
                    result = {"status": "failed", "output": None, "usage": {},
                              "error": f"{type(error).__name__}: {error}"}
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
        # error, unblock adapter callbacks so their local termination runs.
        with self.guard:
            self.stopping = True
        while True:
            try:
                _, _, response, stop = self.events.get_nowait()
            except Empty:
                break
            if stop:
                response.set_result(True)
            else:
                response.set_exception(RuntimeError("executor is shutting down"))
        for thread in self.threads:
            thread.join()
