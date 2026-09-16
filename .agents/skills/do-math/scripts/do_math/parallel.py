"""Run blocking model adapters concurrently; all engine callbacks stay on owner thread."""
from __future__ import annotations

from concurrent.futures import Future
from queue import Empty, Queue
from threading import Lock, Thread


class ModelCalls:
    def __init__(self):
        self.events = Queue()
        self.futures = {}
        self.threads = []
        self.guard = Lock()
        self.pumping = False
        self.stopping = False

    def _callback(self, function, *, stop=False):
        def call(*args):
            response = Future()
            with self.guard:
                if self.stopping:
                    if stop:
                        return True
                    raise RuntimeError("executor is shutting down")
                self.events.put((function, args, response))
            return response.result()
        return call

    def start(self, generator, runner, arguments):
        arguments = dict(arguments)
        for key in ("on_started", "on_observation", "should_stop"):
            if key in arguments:
                arguments[key] = self._callback(arguments[key], stop=key == "should_stop")
        future = Future()
        self.futures[future] = generator
        def run():
            try:
                future.set_result(runner.run(**arguments))
            except BaseException as error:
                future.set_exception(error)
        thread = Thread(target=run, name="do-math-model")
        self.threads.append(thread)
        thread.start()

    def pump(self):
        if self.pumping:
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
        finally:
            self.pumping = False

    def collect(self):
        self.pump()
        finished = 0
        for future in list(self.futures):
            if not future.done():
                continue
            generator = self.futures.pop(future)
            try:
                result = future.result()
            except Exception as error:
                result = {"status": "failed", "output": None, "usage": {},
                          "error": f"{type(error).__name__}: {error}"}
            try:
                generator.send(result)
            except StopIteration:
                pass
            else:
                raise RuntimeError("a model execution yielded more than one call")
            finished += 1
        return finished

    def close(self):
        # The engine normally drains all calls first. On an unexpected owner
        # error, unblock adapter callbacks so their local termination runs.
        with self.guard:
            self.stopping = True
        while True:
            try:
                _, _, response = self.events.get_nowait()
            except Empty:
                break
            response.set_exception(RuntimeError("executor is shutting down"))
        for thread in self.threads:
            thread.join()
