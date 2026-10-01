"""Owner scenes of the planning region on a Sim: an approved task over a registered source, and a verified theorem.

The legacy planning tests built the engine without its constructor over the
record fixtures' approved task (``research_fixtures.bare_engine`` with
``record_fixtures.approved_task``) or used the in-memory ``FakeEngine``; they then
called the engine's own mixin methods. Here the engine is a restored Sim's: the
real ``ResearchEngine`` on the port fakes and the real ``ResearchRepository``,
with its instance built by events, and the tests call the same methods on it.

- ``owner_sim()``: a restored copy of one template this process builds: the
  public activation, the theorem ``source_theorem`` imported by control and
  verified by the Lean double with its identity review matched
  (``engine_lifecycle.theorems``), the source ``source.txt`` registered by the
  public ``source`` control, and the approved task ``TK-1`` a returned
  preparation produced that reads that source (``engine_lifecycle.task``).
  Queue and pending events are empty. ``SOURCE_THEOREM``, ``source_id(sim)`` and
  ``theorem_id(sim)`` name the records.
- ``enqueue(engine, role, target=None, **fields)``: queue through the product
  (``_enqueue``) and return the row it added or merged into.
- ``reassessment_sim()``: the legacy ``engine_fixtures.reassessment_engine`` on a
  restored template: task ``TK-1`` returned result ``EV-1`` (work ``EX-work``) and
  the plan ``EX-plan`` assessed it ``incomplete``: ``OB-scope`` transferred to the
  planned task ``TK-2`` under the user's ``task_scope`` decision (public control),
  and ``OB-proof`` waiting for the missing input ``new.txt``, a source the instance
  does not hold. One other preparation is queued; no pending events.
  ``arrive(sim, name)`` registers the source ``name`` by the public ``source`` control;
  an assessment finds a missing input by its name (``input_basis.aliases``).
- ``work_profile(instance, tier)``: the adopted ``research_work`` profile edition of ``tier``.
"""
from __future__ import annotations

from copy import deepcopy

from support.engine_lifecycle import _ended_execution, applied, approve, clear_work, task, theorems
from support.sim import Sim, built

SOURCE_THEOREM = 'source_theorem'
SOURCE_NAME = 'source.txt'


def _build(root, shared):
    sim = Sim.activated(root, shared=shared)
    theorems(sim, SOURCE_THEOREM)
    path = sim.root / SOURCE_NAME
    path.write_bytes(b'The fixture source the planned task reads.\n')
    applied(sim, 'source', config={'path': str(path)})
    clear_work(sim)
    task(sim.engine, 'TK-1', inputs=[source_id(sim)])
    sim.engine._save()
    return sim


def owner_sim():
    return built('planning-owner', _build)


def warm_owner():
    """``setUpModule``: build the owner template before the first test, so no test pays for it."""
    owner_sim()


def source_id(sim):
    return next(row['id'] for row in sim.instance['sources'] if row['name'] == SOURCE_NAME)


def theorem_id(sim):
    return next(k for k, row in sim.instance['knowledge'].items() if row['title'] == SOURCE_THEOREM)


def enqueue(engine, role, target=None, **fields):
    """Queue through the product and return the row it added or merged into."""
    engine._enqueue(role, target, **fields)
    return next(a for a in reversed(engine.runtime['queue']) if a['role'] == role and a.get('target') == target)


def work_profile(instance, tier):
    """The adopted ``research_work`` profile edition of ``tier`` (the instance also keeps replaced editions)."""
    adopted = {row['id'] for row in instance['role_profile_refs']['research_work']}
    return next(p for key, p in instance['execution_profiles'].items() if key in adopted and p['ai']['tier'] == tier)


def _build_reassessment(root, shared):
    from do_math import planning
    from do_math.task_scope import apply_task_assessments
    sim = Sim.activated(root, shared=shared)
    engine = sim.engine
    clear_work(sim)
    approve(engine, task(engine, 'TK-1', approved=False))
    task(engine, 'TK-2', approved=False)
    engine._save()
    first = sim.runtime['tasks']['TK-1']
    applied(sim, 'decision', config={'change': {'kind': 'task_scope', 'task_id': 'TK-1', 'disposition': 'transfer',
        'revision': first['revision'], 'contract_sha256': planning.contract_hash(first), 'obligation_ids': ['OB-scope'],
        'target_task_id': 'TK-2', 'reason': 'The scope obligation belongs to the second task'}})
    decision = next(k for k, v in sim.instance['decisions'].items() if v.get('change', {}).get('kind') == 'task_scope')
    clear_work(sim)
    engine = sim.engine
    _ended_execution(engine, 'EX-work', 'research_work')
    _ended_execution(engine, 'EX-plan', 'research_plan')
    engine.runtime['tasks']['TK-1'].update(status='waiting', results=[{'id': 'EV-1', 'execution_id': 'EX-work'}])
    assessment = {'task_id': 'TK-1', 'decision': 'incomplete', 'reason': 'The proof waits for a missing input',
        'item_dispositions': [{'obligation_id': 'OB-scope', 'kind': 'transferred', 'evidence_refs': [],
                               'authority_ref': decision, 'target_task_id': 'TK-2', 'target_obligation_id': 'OB-inherited'}],
        'unresolved': [{'obligation_id': 'OB-proof', 'missing_inputs': [MISSING_SOURCE], 'next_owner': 'research_work'}]}
    engine.instance, engine.runtime = apply_task_assessments(engine.instance, engine.runtime, [assessment],
        execution_id='EX-plan', input_tasks=deepcopy(engine.runtime['tasks']), clock=sim.ports.clock)
    engine._enqueue('research_preparation', reason='Other preparation work remains')
    engine._save()
    return sim


MISSING_SOURCE = 'new.txt'


def reassessment_sim():
    return built('planning-reassessment', _build_reassessment)


def arrive(sim, name, body=None):
    """The user's public ``source`` control registering ``name`` (the owner applies it); returns its source row."""
    path = sim.root / name
    path.write_bytes(body or ('The source ' + name + ' arrives.\n').encode('utf-8'))
    applied(sim, 'source', config={'path': str(path)})
    return next(row for row in sim.instance['sources'] if row['name'] == name)


def warm_reassessment():
    reassessment_sim()
