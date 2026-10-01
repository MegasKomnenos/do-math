"""Observation probes for storage tests, for what ``provider_probes.ObservedCalls`` cannot see; they replace nothing.

``ObservedCalls`` sees calls to Python functions through their code objects.
Two more things are needed here:

- ``BuiltinCalls(function)``: the first argument of every call to a builtin
  (C) callable, such as ``hashlib.sha256``, made by any code while the context
  is open. It listens to ``sys.monitoring`` CALL events of all code, which also
  report the callable and its first argument; other events stay off. Legacy
  tests saw such calls by patching the stdlib name with a ``wraps`` double.
  Blind spot: a call made by C code raises no CALL event, so a builtin handed
  on as a value and called there (``map(hashlib.sha256, ...)``, a ``key=``
  function) is not counted; the product today calls ``hashlib.sha256`` only
  directly from Python code.
- ``Returns(function, snapshot=None)``: the values a Python function returns
  while the context is open, seen through ``sys.monitoring`` PY_RETURN events
  of its code alone, so a test can hold the very object a product call handed
  to its caller. With ``snapshot`` (for example ``copy.deepcopy``),
  ``snapshots`` also holds ``snapshot(value)`` taken at the moment of return: an
  expected value independent of the returning owner, against which a later
  change of the returned object shows.
"""
import inspect
import sys
from support.monitoring_slots import reserve_tool




class BuiltinCalls:
    def __init__(self, function):
        self.function = function
        self.arguments = []

    def __enter__(self):
        monitoring = sys.monitoring
        self.tool = reserve_tool('do-math builtin calls')

        def called(code, offset, callable_, first):
            if callable_ is self.function:
                self.arguments.append(first)
        monitoring.register_callback(self.tool, monitoring.events.CALL, called)
        monitoring.set_events(self.tool, monitoring.events.CALL)
        return self

    def __exit__(self, *exception):
        monitoring = sys.monitoring
        monitoring.set_events(self.tool, monitoring.events.NO_EVENTS)
        monitoring.register_callback(self.tool, monitoring.events.CALL, None)
        monitoring.free_tool_id(self.tool)
        return False


class Returns:
    def __init__(self, function, snapshot=None):
        self.code = inspect.unwrap(getattr(function, '__func__', function)).__code__
        self.snapshot = snapshot
        self.values = []
        self.snapshots = []

    def __enter__(self):
        monitoring = sys.monitoring
        self.tool = reserve_tool('do-math returns')

        def returned(code, offset, value):
            if code is self.code:
                self.values.append(value)
                if self.snapshot is not None:
                    self.snapshots.append(self.snapshot(value))
        monitoring.register_callback(self.tool, monitoring.events.PY_RETURN, returned)
        monitoring.set_local_events(self.tool, self.code, monitoring.events.PY_RETURN)
        return self

    def __exit__(self, *exception):
        monitoring = sys.monitoring
        monitoring.set_local_events(self.tool, self.code, monitoring.events.NO_EVENTS)
        monitoring.register_callback(self.tool, monitoring.events.PY_RETURN, None)
        monitoring.free_tool_id(self.tool)
        return False
