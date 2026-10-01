"""Canonical synthetic inputs and real producers; no engine or storage replacement."""
from __future__ import annotations

from support.role_answers import assessment
from do_math import knowledge_io, knowledge_records as kr
from pathlib import Path
from do_math import governance
from do_math.review_cycle import start_review


def scope_assessment(policy, slots):
    """Explicit synthetic full-proposal scope authored by the fixture reviewer."""
    return {"assessment_id": "fixture-full-proposal-scope", "policy_id": policy["id"],
        "required_perspectives": policy["required_perspectives"],
        "initial_slots": [{"id": slot, "perspective": slot, "required_source_refs": ["proposal"]} for slot in slots],
        "selected_profile_ref": None, "activity_execution_limit": policy["activity_execution_limit"],
        "overflow_disposition": policy["overflow_disposition"]}


def start_scoped_review(engine, knowledge_id, assessment, previous_cycle_id=None):
    """Open a review whose scope stage the fixture has already settled with ``assessment``.

    The engine opens every review at its scope stage. A test about the later
    stages takes the cycle it opened and gives it the scope that the pure
    ``start_review(..., scope_assessment=...)`` path gives, as sealed replay does,
    instead of running a scope execution; it returns the cycle ID.
    """
    from do_math.input_basis import capture_review_input_basis
    from do_math.review_cycle import start_review
    cycle_id = engine._start_identity_review(knowledge_id, previous_cycle_id)
    cycle = engine.runtime['review_cycles'][cycle_id]
    previous = engine.runtime['review_cycles'][previous_cycle_id] if previous_cycle_id else None
    scoped = start_review(cycle['proposal'], cycle['requested_reviewer_slots'], cycle['judge_slots'],
                          cycle['max_rounds'], previous, policy=cycle['review_policy'], scope_assessment=assessment)
    cycle.update({key: scoped[key] for key in ('scope_assessment', 'reviewer_slots', 'activity_execution_limit',
                                               'required_source_refs', 'phase')})
    cycle['review_input_basis'] = capture_review_input_basis(cycle)
    engine.runtime['queue'][:] = [action for action in engine.runtime['queue']
                                  if action.get('review_cycle_id') != cycle_id]
    engine._queue_identity_actions(knowledge_id, cycle_id)
    return cycle_id


def grant_replacement(engine, *, reuse='reusable'):
    engine.instance.setdefault('governance_sources', {})['SOURCE-review'] = governance.preserve_source(
        'SOURCE-review', 'Authorize record-based replacement of K1 review.', origin='user')
    engine.instance, engine.runtime, _ = governance.apply_decision(engine.instance, engine.runtime,
        {'kind': 'grant', 'decision_id': 'DEC-review', 'grant': {'id': 'GR-review', 'kind': 'local',
         'roles': ['identity_review'], 'reuse': reuse, 'included_targets': ['K1'],
         'purposes': ['record_replacement']}}, source_ref='SOURCE-review', clock=engine.ports.clock)


def scoped_start(proposal, reviewers, judges=3, max_rounds=3, previous=None):
    slots = [f"initial-{index}" for index in range(reviewers)] if isinstance(reviewers, int) else list(reviewers)
    judge_slots = [f"judge-{index}" for index in range(judges)] if isinstance(judges, int) else list(judges)
    policy = {"id": "test-policy-v5", "required_perspectives": [],
              "minimum_initial_slots": len(slots), "judge_slots": judge_slots, "round_limit": max_rounds,
              "activity_execution_limit": len(slots) + max_rounds * (len(slots) + 4), "overflow_disposition": "unresolved"}
    assessment = {"assessment_id": "test-scope", "policy_id": policy["id"],
                  "required_perspectives": [], "initial_slots": [
                      {"id": slot, "perspective": slot, "required_source_refs": ["proposal"]} for slot in slots],
                  "selected_profile_ref": None, "activity_execution_limit": policy["activity_execution_limit"],
                  "overflow_disposition": "unresolved"}
    return start_review(proposal, reviewers, judges, max_rounds, previous, policy=policy, scope_assessment=assessment)


def review_stage_output(cycle, stage, **changes):
    """A reviewer's output for the next ``stage`` of ``cycle``; ``changes`` replace fields.

    Initial reviewers match, organizers turn each pending finding into an issue,
    answers maintain every objection and judges approve every issue as a
    mismatch.
    """
    from do_math.review_cycle import context_for, next_actions
    result = dict(proposal_digest=cycle['proposal_digest'], summary='Complete review evidence', used_sources=['proposal:1'], questions=[])
    if stage == 'initial':
        result.update(decision='match', scope_complete=True, findings=[])
    elif stage == 'organize':
        result['issues'] = [dict(id=f'i{j}', finding_refs=[x['ref']], answer_role_slot_id=x['ref']['slot'] if x['ref']['stage'] in ('initial', 'answer') else 'initial-0') for j, x in enumerate(context_for(cycle, next_actions(cycle)[0])['pending_findings'], start=len(cycle['issues']))]
    elif stage == 'answer':
        action = next_actions(cycle)[0]
        result.update(answers=[dict(issue_id=i, disposition='maintain', statement='The objection still applies', evidence=['proposal:1']) for i in context_for(cycle, action)['answer_requests']], new_findings=[])
    elif stage == 'judge':
        result.update(decision='mismatch', scope_complete=True, issue_verdicts=[dict(issue_id=i, decision='approved', reason='Proof at precise source coordinate', evidence=['proposal:1']) for i in cycle['issues']], new_findings=[])
    result.update(changes)
    return result


def deferred_research_cycle():
    """``(cycle, action)``: a two-reviewer cycle whose first initial review is deferred for one research request."""
    from do_math.review_cycle import defer_for_research, inline_source_row, next_actions, start_review
    scope = {'assessment_id': 'research-test-scope', 'policy_id': 'review-policy-v5-default',
             'required_perspectives': [],
             'initial_slots': [{'id': 'initial-0', 'perspective': 'first', 'required_source_refs': ['proposal']},
                               {'id': 'initial-1', 'perspective': 'second', 'required_source_refs': ['proposal']}],
             'selected_profile_ref': None, 'activity_execution_limit': 20,
             'overflow_disposition': 'unresolved'}
    cycle = start_review({'revision': 1}, reviewers=2, scope_assessment=scope)
    action = next_actions(cycle)[0]
    output = {'proposal_digest': cycle['proposal_digest'], 'summary': 'Need exact domain evidence',
              'used_sources': [], 'questions': [], 'decision': 'unresolved', 'scope_complete': False, 'findings': []}
    requests = [{'id': 'r', 'question': 'What is the exact domain?', 'source_refs': ['proposal']}]
    sources = [[inline_source_row('proposal', cycle['proposal'])]]
    return defer_for_research(cycle, action, output, requests, 'requester', sources, limit=3), action


def research_answer(cycle):
    """The investigator's answer to ``cycle``'s single research request."""
    request = next(iter(cycle['research'].values()))
    return {'summary': 'Domain recovered', 'used_sources': ['proposal'], 'questions': [],
            'research_request_id': request['id'], 'request_digest': request['request_digest'],
            'outcome': 'answered', 'answer': 'The domain is Nat.', 'scope_complete': True, 'evidence_refs': ['proposal']}


def reviewed_candidate(root, *, verified=False):
    """``(instance, runtime, kid, assessment ID)``: a stored-shape theorem candidate after one sealed identity review.

    ``record_fixtures.execution_state('identity_review')`` holds the review.
    ``verified`` first adopts a synthetic trust environment under ``root`` and
    records a verified formal result, so the review matches; otherwise the
    single reviewer leaves the scope unresolved.
    """
    from support.entry import entry
    _entry = entry()
    from do_math import review_cycle as rc
    from do_math.execution_lifecycle import create_execution
    from do_math.activities import assign_execution
    from support.knowledge_builders import formal_evidence, knowledge_candidate
    from support.record_builders import execution_state
    instance, runtime = execution_state("identity_review")
    if verified:
        from support.trust_inputs import trust_fixture, trust_environment
        eid = 'TE-reviewed'
        environment, binding = trust_environment(trust_fixture(root, ['synthetic-reviewed-lean']),
                                                  environment_id=eid, status='registered', source_ref='synthetic:review')
        instance['trust_environments'] = {eid: environment}
        runtime['trust_bindings'] = {eid: binding}
        from do_math.knowledge import begin_transition, activate_transition
        transition = begin_transition(instance, eid, clock=_entry.ports.clock)
        instance = activate_transition(instance, transition, runtime=runtime, at=_entry.ports.clock.now(), clock=_entry.ports.clock)
        transition['status'] = 'active'
        runtime['trust_transitions'] = {transition['id']: transition}
    instance = knowledge_io.ensure_ontology(instance)
    instance, runtime, kid = knowledge_io.import_candidate(instance, runtime, knowledge_candidate(
        explanation="Truth", lean_code="theorem t : True := True.intro", declaration_names=["t"]),
        source_ref="input", actor_ref="EX-1", clock=_entry.ports.clock)
    if verified:
        instance = kr.record_formal_result(instance, kid, formal_evidence(instance, kid, eid), eid, runtime=runtime)
    cycle = rc.start_review({**kr.proposal_view(instance, kid), "revision": 1}, reviewers=1, max_rounds=1)
    cycle.update(id="RC-1", owner_activity_id="AT-1", knowledge_id=kid, identity_basis=kr.identity_basis(instance, kid),
        input_snapshot="a" * 40, producer_execution_ids=[], policy_ref="policy-test",
        slot_profiles={}, input_bindings={}, publication_premises={}, review_input_basis={})
    profile = runtime["executions"]["EX-1"]["execution_profile_ref"]
    for index in range(2):
        action = rc.next_actions(cycle)[0]
        eid = "EX-review-" + str(index)
        execution = create_execution(execution_id=eid, owner_activity_id="AT-1", actor_kind="ai",
            input_manifest={}, profile_ref=profile, created_at="2026-09-20T00:00:00Z")
        execution["role"] = "identity_review"
        assign_execution(runtime, "AT-1", execution)
        output = {"proposal_digest": cycle["proposal_digest"], "summary": "Synthetic reviewer output",
            "used_sources": ["proposal"], "questions": [], "scope_complete": verified or index == 0}
        if action["stage"] == "scope":
            scope = scope_assessment(cycle["review_policy"], ["initial-0"])
            scope["selected_profile_ref"] = profile
            output["scope_assessment"] = scope
        else:
            output.update(decision="match" if verified else "unresolved", findings=[])
        cycle = rc.accept_result(cycle, action, output, eid,
            input_manifest={"proposal_digest": cycle["proposal_digest"], "role_slot_id": action["slot"]})
    if cycle["status"] != ("completed" if verified else "unresolved"):
        raise AssertionError("The synthetic review ended as " + repr(cycle["status"]))
    runtime["review_cycles"] = {cycle["id"]: cycle}
    assessment = rc.identity_assessment(cycle, reason="Scope remains incomplete")
    assessment["basis"] = kr.identity_basis(instance, kid)
    instance, aid = kr.record_identity_assessment(instance, kid, assessment, cycle["policy_ref"], runtime=runtime, clock=_entry.ports.clock)
    from support.storage_records import record_store
    from support.fakes.git_backend import InProcessGit
    from support.fakes.clock import FakeClock
    store = record_store(Path(root) / 'review-state', backend=InProcessGit(), clock=FakeClock())
    head = store.initialize(instance, runtime)
    loaded_head, instance, runtime = store.load(head)
    if (loaded_head != head or runtime['review_cycles'][cycle['id']] != cycle
            or instance['identity_assessments'][aid]['review_cycle_id'] != cycle['id']):
        raise AssertionError('the actual review producer did not survive storage')
    return instance, runtime, kid, aid
