"""Calls port: an executor that runs blocking calls off the owner thread and hands results back to it.

The executor's surface is the one ``parallel.ModelCalls`` has: ``start_call``,
``wait``, ``judge``, ``pump``, ``collect``, ``close`` and the ``futures`` map.
Callbacks passed to a call (``on_started``, ``on_observation``) and the result
are applied on the owner thread.
"""
from typing import Protocol


class Calls(Protocol):
    def new(self, *, on_returned=None, on_observation_error=None):
        """A fresh executor whose returned calls report through ``on_returned(execution_id, result)``."""
