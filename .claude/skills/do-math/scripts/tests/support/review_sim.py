"""Identity review scenes on the Sim: the owner runs the review through the worker, the model double and submission.

A theorem imported by public control is verified by the Lean double through
the owner's formal check, which opens its identity review at the scope stage.
From there every review attempt is registered by the owner (and so admitted by
the review), runs as a model call in a Job, is submitted through the workspace
submission tool and is applied by the central receiver. The model double's
default responder answers every stage as a match.

Templates, each built once per process (``support.sim.built``); a test
module's ``setUpModule`` calls the matching ``warm_*``:

- ``opened_sim()``: an active instance whose theorem ``k1`` (imported by
  control, ``import_theorem``) has just been verified and whose identity review
  was opened: only the scope action is queued. ``reviewed_sim()``: the same
  review run to a match; the queue and pending events are empty.
- ``produced_sim()``: a formal theorem that research work produced, verified
  and reviewed to a match; its proposal names that work as its producer.
  ``reviewed_theorem(sim)`` is its knowledge ID and current assessment.
- ``impact_sim()``: research work revised observations ``A`` and ``C`` with ``B``
  declared in their impact, and its bundle waits for an independent impact
  review (``impact_work_responder``). ``observations(sim)``, ``held_impact(sim)``
  and ``impact_review_answer(decisions)`` read and answer that scene.

Other helpers:

- ``theorem_id(sim, title)`` is a knowledge ID; ``cycle_of(sim)`` ``k1``'s current review cycle.
- ``dispute(sim, finding)``: model rules for one rejected objection: the first
  initial slot reports ``finding`` as a mismatch, the organizer turns each
  pending finding into an issue for its original slot, judges reject every
  issue and the answer withdraws every objection.
- ``review_executions(sim, cycle_id)``: the identity review executions of a
  cycle in registration order.
- ``export_objects(sim)`` writes the Git fake's objects as loose objects, so a
  real ``git`` (the CLI's default ports) reads the Sim's repository.
"""
from __future__ import annotations

from do_math import knowledge_records as kr
from support.engine_lifecycle import applied, clear_work
from support.model import Answer, amend
from support.sim import Sim, built

THEOREM = {'kind': 'theorem', 'title': 'k1', 'statement': 'One equals one', 'summary': 'Reflexivity',
           'explanation': 'By reflexivity.', 'lean_code': 'theorem k1 : 1 = 1 := rfl',
           'declaration_names': ['k1'], 'dependencies': []}


def theorem_id(sim, title='k1'):
    return next(k for k, row in sim.instance['knowledge'].items() if row['title'] == title)


def cycle_of(sim, title='k1'):
    return sim.runtime['review_cycles'][sim.instance['knowledge'][theorem_id(sim, title)]['review_cycle_id']]


def import_theorem(sim, candidate=None):
    """Import ``candidate`` (default ``THEOREM``) by public control and run the owner until its identity review opens.

    Work the import queued besides the review is dropped and the state published.
    Returns the knowledge ID.
    """
    sim.lean.allow(THEOREM['lean_code'], ['k1'], signatures={'k1': 'k1 : 1 = 1'})
    candidate = candidate or THEOREM
    clear_work(sim)
    applied(sim, 'knowledge', config={'operation': 'import', 'candidate': candidate})
    kid = theorem_id(sim, candidate['title'])
    sim.run_until(lambda s: s.instance['knowledge'][kid].get('review_cycle_id'), max_steps=4)
    sim.engine.runtime['queue'][:] = [a for a in sim.engine.runtime['queue'] if a['role'] == 'identity_review']
    sim.engine.runtime['pending_events'].clear()
    sim.engine._save()
    return kid


def _build_opened(root, shared):
    sim = Sim(root, shared=shared)
    sim.activate()
    import_theorem(sim)
    return sim


def _build_reviewed(root, shared):
    sim = _build_opened(root, shared)
    sim.run_until(lambda s: cycle_of(s)['status'] != 'working', max_steps=8)
    if cycle_of(sim).get('decision') != 'match':
        raise AssertionError('the template review ended ' + repr(cycle_of(sim).get('decision')))
    clear_work(sim)
    return sim


def _build_produced(root, shared):
    from support.default_responder import DefaultResponder
    sim = Sim(root, shared=shared)
    sim.activate()
    sim.model.responder = DefaultResponder(formal=True)

    def reviewed(s):
        return any(kr.usable_links(s.instance, kid) for kid in s.instance['knowledge'])
    sim.run_until(reviewed, max_steps=40)
    clear_work(sim)
    return sim


def opened_sim():
    sim = built('review-opened', _build_opened)
    sim.lean.allow(THEOREM['lean_code'], ['k1'], signatures={'k1': 'k1 : 1 = 1'})
    return sim


def produced_sim():
    """An active instance whose research work produced a formal theorem the owner verified and reviewed to a match.

    The owner ran preparation, contract review, planning and the research work
    with the formal default responder (``support.default_responder.DefaultResponder(formal=True)``),
    then the formal check and the identity review; the reviewed theorem's
    proposal names that research work execution as its producer. The queue and
    pending events are empty.
    """
    return built('review-produced', _build_produced)


def warm_produced():
    produced_sim()


def reviewed_theorem(sim):
    """``(knowledge ID, its current assessment)`` of the one theorem with a usable identity link."""
    kid = next(kid for kid in sim.instance['knowledge'] if kr.usable_links(sim.instance, kid))
    return kid, sim.instance['identity_assessments'][kr.usable_links(sim.instance, kid)[0]['assessment_id']]


def observations(sim):
    """``{'A': ID, 'B': ID, 'C': ID}`` of the observations the impact template imported."""
    return {row['title']: kid for kid, row in sim.instance['knowledge'].items()
            if row['kind'] == 'observation' and row['title'] in 'ABC' and not row.get('supersedes')}


def impact_work_responder(ids):
    """The default responder, except that research work revises ``A`` and ``C`` and declares ``B`` in each change's impact.

    The work resolves both declared revision targets as revised; the model
    double's seal declares the output and the extension rows as one bundle.
    """
    import json
    from support.default_responder import DefaultResponder

    class ImpactWork(DefaultResponder):
        def respond(self, role, ctx, workspace):
            out = super().respond(role, ctx, workspace)
            if role == 'research_work':
                out.update(knowledge=[], report='Corrects the explanations of A and C')
                extensions = {'knowledge_changes': [
                    {'id': ids[title], 'changes': {'summary': 'Revised ' + title}, 'reason': 'Correct explanation',
                     'impact_set': [ids['B']]} for title in ('A', 'C')],
                    'revision_resolutions': [{'record_id': ids[title], 'disposition': 'revised', 'reason': 'Corrected ' + title}
                                             for title in ('A', 'C')]}
                (workspace / 'activity-extensions.json').write_text(json.dumps(extensions), encoding='utf-8')
            return out
    return ImpactWork()


def _build_impact(root, shared):
    from support.record_builders import observation_knowledge
    from support.engine_lifecycle import approve, only, queue_work, task
    sim = Sim(root, shared=shared)
    sim.activate()
    clear_work(sim)
    for title in ('A', 'B', 'C'):
        applied(sim, 'knowledge', config={'operation': 'import', 'candidate': observation_knowledge(title)})
    ids = observations(sim)
    clear_work(sim)
    row = task(sim.engine, 'TK-impact', approved=False)
    row['knowledge_revision_targets'] = [ids['A'], ids['C']]
    approve(sim.engine, row)
    queue_work(sim.engine, 'TK-impact')
    only(sim, 'research_work')
    sim.engine._save()
    sim.model.responder = impact_work_responder(ids)
    sim.run_until(lambda s: any(w.get('kind') == 'impact_review' for w in s.runtime.get('waiting_actions', {}).values()),
                  max_steps=2)
    only(sim, 'maintenance')
    sim.engine.runtime['pending_events'].clear()
    sim.engine._save()
    return sim


def impact_sim():
    """Research work on task ``TK-impact`` revised observations ``A`` and ``C`` and declared ``B`` in their impact.

    The receiver returned the bundle for an independent impact review: the work
    action waits (kind ``impact_review``) and the one queued action is the
    ``maintenance`` impact review of the exact held request. A template built once per process.
    """
    return built('review-impact', _build_impact)


def warm_impact():
    impact_sim()


def held_impact(sim):
    """``(waiting entry, producer execution, integration ID, impact review request)`` of the held work."""
    waiting = next(row for row in sim.runtime['waiting_actions'].values() if row.get('kind') in {'impact_review', 'impact_review_blocked'})
    [(identifier, request)] = waiting['review_requests'].items()
    return waiting, sim.runtime['executions'][waiting['execution_id']], identifier, request


def impact_review_answer(decisions=None):
    """A model answer for the ``maintenance`` impact review of its assigned request: ``decisions`` per scope, else approve."""
    def make(out, ctx):
        request = ctx['action']['input_basis']['impact_review']
        rows = [{'scope': scope, 'plan_digest': plan['digest'], 'decision': (decisions or {}).get(scope, 'approve'),
                 'affected_ids': sorted(set(plan['computed_impact']) | set(plan['declared_impact'])),
                 'reason': 'The declared additional scope must also be reassessed.'} for scope, plan in request['plans'].items()]
        return {**out, 'report': 'Compared each declared scope with its computed dependencies and supplied premises.',
                'remaining_work': [], 'impact_review': {**{key: request[key] for key in
                    ('integration_id', 'payload_sha256', 'producer_execution_id', 'input_snapshot')}, 'plan_decisions': rows}}
    return Answer(make)


def export_objects(sim):
    """Write the Git fake's objects of ``sim``'s repository as loose objects, so a real ``git`` reads its history."""
    import zlib
    git_dir = sim.repository / '.git'
    for oid, (kind, body) in sim.ports.git_backend.objects.get(str(git_dir.absolute()), {}).items():
        path = git_dir / 'objects' / oid[:2] / oid[2:]
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(zlib.compress(kind.encode('ascii') + b' %d\0' % len(body) + body))


def reviewed_sim():
    sim = built('review-reviewed', _build_reviewed)
    sim.lean.allow(THEOREM['lean_code'], ['k1'], signatures={'k1': 'k1 : 1 = 1'})
    return sim


def warm_opened():
    opened_sim()


def warm_reviewed():
    reviewed_sim()


def review_executions(sim, cycle_id):
    return [row for row in sim.runtime['executions'].values()
            if row.get('role') == 'identity_review' and row.get('action', {}).get('review_cycle_id') == cycle_id]


def _organized(out, ctx):
    review = ctx['role_review']
    issues = [{'id': 'issue-' + str(len(review['issues']) + index), 'finding_refs': [row['ref']],
               'answer_role_slot_id': row['ref']['slot'] if row['ref']['stage'] == 'initial' else 'initial-0'}
              for index, row in enumerate(review['pending_findings'])]
    return {**out, 'issues': issues}


def _rejected(out, ctx):
    verdicts = [{'issue_id': issue, 'decision': 'rejected', 'reason': 'Original source refutes the objection',
                 'evidence': ['proposal']} for issue in ctx['role_review']['issues']]
    return {**out, 'decision': 'match', 'scope_complete': True, 'new_findings': [], 'issue_verdicts': verdicts}


def _withdrawn(out, ctx):
    answers = [{'issue_id': issue, 'disposition': 'withdraw', 'statement': 'I misread the domain', 'evidence': ['proposal']}
               for issue in ctx['role_review']['answer_requests']]
    return {**out, 'new_findings': [], 'answers': answers}


def dispute(sim, finding):
    """Model rules for one objection the judges reject and its reviewer withdraws; see the module docstring."""
    sim.model.on('identity_review', stage='initial', slot='initial-0').reply(
        amend(decision='mismatch', scope_complete=True, findings=[finding])).reply(amend())
    sim.model.on('identity_review', stage='organize').reply(Answer(_organized))
    sim.model.on('identity_review', stage='judge').reply(Answer(_rejected))
    sim.model.on('identity_review', stage='answer').reply(Answer(_withdrawn))
