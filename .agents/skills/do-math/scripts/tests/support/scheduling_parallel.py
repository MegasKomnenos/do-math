"""Scheduling scenes with several model calls on a Sim: ready work, fair turns and overlapping calls.

- ``ready_work_sim(count, **config)``: moved from ``test_session_scheduler.ready_work``.
  A template built once per ``(count, config)`` through the public activation
  with ``config``: the default responder's preparation proposes tasks ``'0'`` ..
  ``count-1`` rated high difficulty and medium importance, real contract reviews
  approve them, and the plan selects every ready task, until the queue holds
  exactly one research work per task and no pending event.
- ``round_robin()``: a ``choose`` for the calls port fake that gives the turn to
  the ready call that waited longest. The fake's default resumes the earliest
  ready call, so a call that hands the turn back while it waits for the others
  would be resumed again before they start.
- ``Overlap(sim, expected)``: a model double hook (``ScenarioModel.during``) for
  research work: each call records its target in ``same-name.txt`` of its
  workspace and hands the turn back to the owner until ``expected`` calls have
  entered, so no call answers before all of them are in flight. ``waited_out``
  records, per call, whether it saw all ``expected`` calls entered before it went
  on (bounded at 200 turns); ``peak`` is the most calls one of them saw entered;
  ``workspaces`` lists the calls' workspaces.
"""
from __future__ import annotations

from pathlib import Path

from support.sim import Sim, built

RATING = {'difficulty': 'high', 'importance': 'medium', 'reason': 'Independent novel fixture approaches'}


def _ready(root, shared, *, count, config):
    from support.role_answers import candidate
    from support.default_responder import DefaultResponder
    from support.model import ModelDouble
    sim = Sim.activated(root, shared=shared, config=config)
    sim.model = ModelDouble(sim.clock, DefaultResponder(preparation_candidates=[candidate(str(i)) for i in range(count)],
                                                      model_rating=RATING))

    def ready(s):
        tasks = s.runtime['tasks']
        queued = sorted((a['role'], a.get('target')) for a in s.runtime['queue'])
        return (len(tasks) == count and queued == sorted(('research_work', tid) for tid in tasks)
                and s.runtime['pending_events'] == [])
    sim.run_until(ready, max_steps=4 * count + 8)
    return sim


def ready_work_sim(count, **config):
    return built('scheduling-ready-work', _ready, count=count, config=config)


def round_robin():
    given, tick = {}, [0]

    def choose(ready):
        index = min(range(len(ready)), key=lambda i: given.get(id(ready[i]), -1))
        tick[0] += 1
        given[id(ready[index])] = tick[0]
        return index
    return choose


class Overlap:
    def __init__(self, sim, expected):
        self.sim, self.expected = sim, expected
        self.entered, self.peak, self.workspaces, self.waited_out = 0, 0, [], []

    def __call__(self, context, workspace):
        from support.fakes.calls import owner_turn
        self.entered += 1
        self.workspaces.append(Path(workspace))
        (Path(workspace) / 'same-name.txt').write_text(context['action']['target'], encoding='utf-8')
        for _ in range(200):
            if self.entered >= self.expected:
                break
            owner_turn()
        self.peak = max(self.peak, self.entered)
        self.waited_out.append(self.entered >= self.expected)
