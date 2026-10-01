"""An instance the CLI's ``init --create-repository`` made, for the engine region's advanced CLI tests.

``cli.main`` takes no Ports (1f seam ledger 6), so these tests read and write
through the real Git process and live with the boundary tests
(``support.engine_cli`` is the same arrangement for a ``git_init`` repository).

- ``created_instance(root, shared)``: a ``research_fixtures.restore_template``
  build: ``init --create-repository`` with repository ``root / 'repo'``,
  workspace ``root / 'workspace'``, goal ``Original goal`` and a configuration
  file without the scheduled operator. It returns the instance ID.
- ``CreatedCliTest``: a test case on a fresh copy with ``root``, ``repo``,
  ``instance_id``; ``cli(*arguments)`` returns ``(exit code, envelope body,
  stderr)`` after the envelope's invariants (``support.engine_cli.body``);
  ``control(command, payload)`` writes the payload to a new file, sends it with
  ``--file`` and requires exit code 0; ``load()`` reads the published state.
- ``ReturnedValues(name=function, ...)``: records the object each named
  function returns while the block is open, seen through ``sys.monitoring``
  return events of those functions' code objects (nothing is replaced).
- ``control_at_first_sleep(send, seconds)``: calls ``send()`` (a control) when
  this thread first starts the real clock port's ``sleep(seconds)`` inside the
  block, as a watching owner does between passes.
"""
from contextlib import contextmanager
import inspect
import json
import sys
from support.monitoring_slots import reserve_tool
import threading
import unittest

from do_math.repository import ResearchRepository
from support.cli_images import initialized_cli
from support.cli_inputs import run_cli
from support.engine_cli import body


def created_instance(root):
    """``restore_template`` build: ``init --create-repository`` through the CLI; returns the instance ID."""
    configuration = root / 'config.json'
    configuration.write_text(json.dumps({'operator_enabled': False}), encoding='utf-8')
    init = run_cli('init', '--create-repository', '--repository', str(root / 'repo'),
                   '--workspace', str(root / 'workspace'), '--goal', 'Original goal',
                   '--config-file', str(configuration), cwd=root)
    if init.returncode != 0:
        raise AssertionError(init.stdout + init.stderr)
    return json.loads(init.stdout)['result']['instance_id']


class CreatedCliTest(unittest.TestCase):
    def setUp(self):
        self.root, self.instance_id = initialized_cli('created')
        self.repo = self.root / 'repo'

    def cli(self, *arguments):
        completed = run_cli(*arguments, cwd=self.root)
        text = completed.stdout.strip()
        return completed.returncode, (body(completed) if text else None), completed.stderr

    def control(self, command, payload):
        path = self.root / f"{command}-{len(list(self.root.glob(command + '-*.json')))}.json"
        path.write_text(json.dumps(payload), encoding='utf-8')
        result = self.cli(command, '--repository', str(self.repo), '--instance', self.instance_id, '--file', str(path))
        self.assertEqual(result[0], 0, result)
        return result

    def load(self):
        from support.entry import entry
        _entry = entry()
        from do_math.wiring import real_ports
        _entry.ports = real_ports(environment=_entry.environment)
        return ResearchRepository(self.repo, self.instance_id, backend=_entry.ports.git_backend, clock=_entry.ports.clock).load()




@contextmanager
def control_at_first_sleep(send, seconds):
    """Call ``send()`` once, when this thread first starts ``SystemClock.sleep(seconds)`` inside the block.

    An owner on the real clock port waits between passes with the port's
    ``sleep``; a control sent then is read by its next pass. The start is seen
    through a ``sys.monitoring`` start event of that one code object, so nothing
    is replaced. Yields ``{'sent': send's result, or None before the sleep}``.
    """
    from do_math.system_clock import SystemClock
    code, thread, state = SystemClock.sleep.__code__, threading.get_ident(), {'sent': None}
    monitoring = sys.monitoring
    tool = reserve_tool('do-math control at sleep')

    def started(started_code, offset):
        if threading.get_ident() != thread or state['sent'] is not None \
                or sys._getframe(1).f_locals.get('seconds') != seconds:
            return
        state['sent'] = 'sending'
        state['sent'] = send()
    monitoring.register_callback(tool, monitoring.events.PY_START, started)
    monitoring.set_local_events(tool, code, monitoring.events.PY_START)
    try:
        yield state
    finally:
        monitoring.set_local_events(tool, code, monitoring.events.NO_EVENTS)
        monitoring.register_callback(tool, monitoring.events.PY_START, None)
        monitoring.free_tool_id(tool)


class ReturnedValues:
    def __init__(self, **functions):
        self.names = {inspect.unwrap(getattr(f, '__func__', f)).__code__: name for name, f in functions.items()}
        self.values = {name: [] for name in functions}

    def __enter__(self):
        monitoring = sys.monitoring
        self.tool = reserve_tool('do-math returned values')

        def returned(code, offset, value):
            self.values[self.names[code]].append(value)
        monitoring.register_callback(self.tool, monitoring.events.PY_RETURN, returned)
        for code in self.names:
            monitoring.set_local_events(self.tool, code, monitoring.events.PY_RETURN)
        return self

    def __exit__(self, *exception):
        monitoring = sys.monitoring
        for code in self.names:
            monitoring.set_local_events(self.tool, code, monitoring.events.NO_EVENTS)
        monitoring.register_callback(self.tool, monitoring.events.PY_RETURN, None)
        monitoring.free_tool_id(self.tool)
        return False
