"""Narrow owner failure injection; normal producers, repository and calls stay in use."""
import inspect
import sys
from copy import deepcopy

from support.monitoring_slots import reserve_tool


def publication_wait(sim):
    """A real first work result sealed centrally, with only its integration CAS refused."""
    from support.scheduling_return_matrix import AfterReturn
    from support.submission_scenes import withhold_publication, release_publication
    action_id = sim.runtime['queue'][0]['id']

    def withhold():
        execution, = [row for row in sim.runtime['executions'].values()
                      if row['action'].get('id') == action_id]
        withhold_publication(sim, execution['id'])

    try:
        with AfterReturn(sim.engine._prepare_call, withhold, predicate=lambda value: isinstance(value, dict)):
            sim.engine.run(max_steps=1)
    finally:
        release_publication(sim)
    wait = deepcopy(sim.runtime['waiting_actions'][action_id])
    if wait['kind'] != 'submission_publication':
        raise AssertionError('the actual sealed result did not wait for publication: ' + repr(wait))
    return wait, deepcopy(sim.runtime['executions'][wait['execution_id']])


def reading_sealed_output(execution):
    """Whether the real Git read belongs to this submission's output read."""
    from do_math.submission import read_sealed_submission
    frame = sys._getframe(1)
    while frame is not None:
        if (frame.f_code is read_sealed_submission.__code__
                and frame.f_locals.get('identifier') == execution['id']
                and frame.f_locals.get('field') == 'output_ref'):
            return True
        frame = frame.f_back
    return False


class FailOnce:
    """Raise at one matching function entry, then let later calls run unchanged."""
    def __init__(self, function, predicate, error):
        self.code = inspect.unwrap(function).__code__
        self.predicate, self.error = predicate, error
        self.hits = []

    def __enter__(self):
        self.tool = reserve_tool('owner unit failure')

        def started(code, offset):
            arguments = dict(sys._getframe(1).f_locals)
            if self.predicate(arguments):
                sys.monitoring.set_local_events(self.tool, self.code, sys.monitoring.events.NO_EVENTS)
                self.hits.append(arguments)
                raise self.error

        sys.monitoring.register_callback(self.tool, sys.monitoring.events.PY_START, started)
        sys.monitoring.set_local_events(self.tool, self.code, sys.monitoring.events.PY_START)
        return self

    def __exit__(self, *error):
        sys.monitoring.set_local_events(self.tool, self.code, sys.monitoring.events.NO_EVENTS)
        sys.monitoring.register_callback(self.tool, sys.monitoring.events.PY_START, None)
        sys.monitoring.free_tool_id(self.tool)
        return False
