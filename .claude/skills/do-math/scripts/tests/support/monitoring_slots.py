"""Allocate a monitoring ID without displacing coverage, profiling or another observer."""
import sys


def reserve_tool(name):
    monitoring = sys.monitoring
    for tool in (3, 4, 0, 2, 5, 1):
        if monitoring.get_tool(tool) is None:
            monitoring.use_tool_id(tool, name)
            return tool
    raise RuntimeError('all six Python monitoring tool IDs are occupied')
