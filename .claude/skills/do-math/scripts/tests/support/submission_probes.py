"""Observation probes of the submission region: they watch the product and replace nothing.

- ``CallSites(target)``: a context that records, for every call of ``target``
  made while it is open on this thread's interpreter, the source file of the
  calling code. It works for builtins such as ``hashlib.sha256``, which have no
  Python code object for ``ObservedCalls`` to watch: ``sys.monitoring`` CALL
  events fire before any call, with the callable. ``files()`` gives the
  calling files; ``count(module)`` counts the calls made by that module's code.
  The legacy tests replaced a module's ``hashlib`` name with a double that
  raised; this counts the calls of the unchanged product.
"""
from pathlib import Path
import sys


class CallSites:
    def __init__(self, target):
        self.target, self.sites = target, []

    def __enter__(self):
        monitoring = sys.monitoring
        # A tool slot no debugger, coverage tool, profiler or ObservedCalls holds.
        self.tool = next(tool for tool in (4, 3, 0, 2) if monitoring.get_tool(tool) is None)
        monitoring.use_tool_id(self.tool, 'do-math submission call sites')

        def called(code, offset, callable_, argument):
            if callable_ is self.target:
                self.sites.append(code.co_filename)
        monitoring.register_callback(self.tool, monitoring.events.CALL, called)
        monitoring.set_events(self.tool, monitoring.events.CALL)
        return self

    def __exit__(self, *exception):
        monitoring = sys.monitoring
        monitoring.set_events(self.tool, monitoring.events.NO_EVENTS)
        monitoring.register_callback(self.tool, monitoring.events.CALL, None)
        monitoring.free_tool_id(self.tool)
        return False

    def files(self):
        return list(self.sites)

    def count(self, module):
        """Calls made by code defined in ``module``'s source file."""
        source = Path(module.__file__).resolve()
        return sum(1 for site in self.sites if Path(site).resolve() == source)
