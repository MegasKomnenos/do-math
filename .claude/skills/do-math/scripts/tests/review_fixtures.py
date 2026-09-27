"""Identity review fixtures: a review engine double, scoped cycles, reviewer outputs and review harnesses.

Reviewer, researcher and compiler answers here are synthetic; the review
cycle, admission and application code they pass through is the product's.

- ``ReviewFakeEngine(root, rounds=2)``: an in-memory engine over one verified
  candidate theorem ``K1`` (see its docstring). ``grant_replacement(engine)``
  grants the record-based replacement of ``K1``'s review.
- ``scoped_start(proposal, reviewers, ...)``: a pure review cycle whose scope
  stage is already settled with one initial slot per reviewer.
- ``review_stage_output(cycle, stage, **changes)``: a reviewer's output for the
  next stage of a pure cycle.
- ``defer_review_for_research(engine)``, ``deferred_research_cycle()`` and
  ``research_answer(cycle)``: a review deferred for fixed-source research, on a
  ``ReviewFakeEngine`` or a pure cycle, and the investigator's answer.
- ``reviewed_candidate(root, *, verified=False)``: a stored-shape candidate
  after one sealed identity review.
- Harnesses (``unittest.TestCase`` bases without tests):
  ``ReassessmentHarness`` (a completed review ready for reassessment),
  ``KnowledgeRoundtripHarness`` (sealed synthetic reviews over real Git
  storage) and ``ImpactReviewHarness`` (a producer bundle held for impact
  review).
"""
from copy import deepcopy
import hashlib
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import create_autospec

from do_math import governance, knowledge_io, knowledge_records as kr
from do_math.engine import ResearchEngine
from do_math.repository import exact_content_hash
from do_math.review_cycle import start_review
from research_fixtures import governance_start, start_scoped_review


def grant_replacement(engine, *, reuse='reusable'):
    engine.instance.setdefault('governance_sources', {})['SOURCE-review'] = governance.preserve_source(
        'SOURCE-review', 'Authorize record-based replacement of K1 review.', origin='user')
    engine.instance, engine.runtime, _ = governance.apply_decision(engine.instance, engine.runtime,
        {'kind': 'grant', 'decision_id': 'DEC-review', 'grant': {'id': 'GR-review', 'kind': 'local',
         'roles': ['identity_review'], 'reuse': reuse, 'included_targets': ['K1'],
         'purposes': ['record_replacement']}}, source_ref='SOURCE-review')


def _no_artifacts(path, snapshot):
    raise FileNotFoundError(path)


class ReviewFakeEngine(ResearchEngine):
    """The product engine over one candidate theorem ``K1`` with verified formal evidence and a review policy.

    ``start`` opens a review at its initial slots with the fixture scope, ``pending``
    is the next identity review action, ``execute(changes=None)`` answers it as a
    reviewer (match; organizers pair findings with answers; judges reject every
    issue) and applies the answer, ``revise`` creates a successor candidate and
    ``assessment``/``usable`` read the result. It has no repository: ``_save`` is
    an autospec double and its store reads no artifact.
    """
    def __init__(self, root, rounds=2):
        self._init_process_state()
        source = 'theorem sample : 1 = 1 := rfl'
        policy = {'id': 'fixture-review-policy-v5', 'required_perspectives': [],
                  'minimum_initial_slots': 2, 'judge_slots': ['judge-0', 'judge-1', 'judge-2'],
                  'round_limit': rounds, 'activity_execution_limit': 24, 'overflow_disposition': 'unresolved'}
        scope = {'assessment_id': 'fixture-scope', 'policy_id': policy['id'],
                 'required_perspectives': [], 'initial_slots': [
                     {'id': 'initial-0', 'perspective': 'formal', 'required_source_refs': ['proposal']},
                     {'id': 'initial-1', 'perspective': 'semantic', 'required_source_refs': ['proposal']}],
                 'selected_profile_ref': None, 'activity_execution_limit': 24, 'overflow_disposition': 'unresolved'}
        from do_math.configuration import DEFAULT_CONFIG
        # The scope a start() review begins with; engine-opened reviews begin at the scope stage.
        self.scope = scope
        self.instance = governance_start({'config': {'reviewers': 2, 'review_research_limit': DEFAULT_CONFIG['review_research_limit']},
            'knowledge': {'K1': {'id': 'K1', 'statement': 'One equals one', 'explanation': 'Reflexivity',
                'summary': 'A sample theorem', 'lean_code': source, 'declaration_names': ['sample'],
                'dependencies': [], 'producer_execution': 'author',
                'status': 'candidate', 'reviews': [],
                'formal': {'status': 'verified', 'source_sha256': hashlib.sha256(source.encode()).hexdigest(),
                           'declarations': ['sample'], 'axioms': {'sample': []},
                           'toolchain': {'sha256': 'exact-toolchain-hash', 'version': 'test'},
                           'execution_id': 'formal-1', 'artifact_ref': 'artifacts/formal-1.json'}}}})
        self.runtime = {'queue': [], 'executions': {}, 'questions': []}
        legacy = self.instance.pop('knowledge')['K1']
        self.instance = knowledge_io.ensure_ontology(self.instance)
        from do_math.execution_profiles import build_profiles, profile_ref
        profiles = build_profiles(DEFAULT_CONFIG)
        self.instance.update(execution_profiles=profiles['execution_profiles'],
                             role_profile_refs=profiles['role_profile_refs'])
        self.profile = profile_ref(next(p for p in profiles['execution_profiles'].values() if p['role'] == 'identity_review'))
        self.research_profile = profile_ref(next(p for p in profiles['execution_profiles'].values() if p['role'] == 'supplemental_research'))
        self.instance['review_policy'] = deepcopy(policy)
        from research_fixtures import trust_environment, trust_fixture
        trusted = trust_fixture(Path(root), ['fixture-review-lean'])
        environment, binding = trust_environment(trusted, environment_id='TE-review', source_ref='fixture-review-trust')
        legacy['formal']['toolchain'] = deepcopy(trusted['toolchain'])
        self.instance.update(active_trust_environment='TE-review',
            trust_environments={'TE-review': environment})
        self.runtime['trust_bindings'] = {'TE-review': binding}
        definition = next(row for row in self.instance['kind_definitions'].values() if row['token'] == 'theorem')
        candidate = {key: value for key, value in legacy.items() if key not in {'formal', 'status', 'reviews'}}
        candidate.update(revision=1, kind='theorem', kind_definition_id=definition['id'])
        self.instance, _ = kr.create_candidate(self.instance, candidate, source_ref='test-fixture', actor_ref='author')
        proof = deepcopy(legacy['formal'])
        proof.update(dependency_closure={'sample': []}, dependency_evidence={'sample': {}},
                     declaration_evidence={'sample': {'type': 'fixture-type', 'value': 'fixture-proof'}})
        self.instance = kr.record_formal_result(self.instance, 'K1', proof, 'TE-review', runtime=self.runtime)
        self.head = 'snapshot-one'
        # No repository: the reviews here read no sealed artifact and key no process memo.
        self.store = SimpleNamespace(git_dir=None, read=_no_artifacts)
        self.root = Path(root)
        self.sequence = 0
        self._save = create_autospec(self._save)

    def start(self, kid='K1', previous_cycle_id=None, scope=None):
        """Open a review of kid that begins at its initial slots with the fixture scope."""
        return start_scoped_review(self, kid, scope or self.scope, previous_cycle_id)

    def pending(self):
        return next(a for a in self.runtime['queue'] if a['role'] == 'identity_review')

    def assessment(self, kid='K1'):
        cid = self.instance['knowledge'][kid]['review_cycle_id']
        return self.instance['identity_assessments'][self.runtime['review_cycles'][cid]['assessment_id']]

    def usable(self, kid='K1'):
        return bool(kr.usable_links(self.instance, kid))

    def revise(self, previous_id='K1', new_id='K2'):
        proposal = kr.proposal_view(self.instance, previous_id)
        candidate = {key: deepcopy(value) for key, value in proposal.items()
                     if key not in {'formal', 'status', 'review_cycle_id', 'review_history', 'formal_result_id', 'exposition_id'}}
        candidate.update(id=new_id, supersedes=previous_id, revision=proposal['revision'] + 1,
                         explanation='Expanded proof by reflexivity', formal_result_ref=proposal['formal_result_id'])
        self.instance, _ = kr.create_candidate(self.instance, candidate, source_ref='test-revision', actor_ref='author')
        return new_id

    def execute(self, changes=None, *, record_first=False):
        action = self.pending()
        self.sequence += 1
        execution_id = f'ex-{self.sequence}'
        workspace = self.root / execution_id / 'workspace'
        context = self._prepare_review_context(action, workspace)['context']
        cycle = self.runtime['review_cycles'][action['review_cycle_id']]
        output = dict(proposal_digest=context['proposal_digest'], summary='Evidence-backed result',
                      used_sources=['proposal:1'], questions=[])
        stage = action['stage']
        if stage == 'scope':
            policy = cycle['review_policy']
            output.update(scope_complete=True, scope_assessment={
                'assessment_id': 'generated-scope', 'policy_id': policy['id'],
                'required_perspectives': list(policy['required_perspectives']),
                'initial_slots': [{'id': 'initial-0', 'perspective': 'formal', 'required_source_refs': ['proposal']},
                                  {'id': 'initial-1', 'perspective': 'semantic', 'required_source_refs': ['proposal']}],
                'selected_profile_ref': None, 'activity_execution_limit': policy['activity_execution_limit'],
                'overflow_disposition': policy['overflow_disposition']})
        elif stage == 'initial':
            output.update(decision='match', scope_complete=True, findings=[])
        elif stage == 'organize':
            output['issues'] = [dict(id=f'issue-{len(cycle["issues"])+i}', finding_refs=[source['ref']],
                answer_role_slot_id=source['ref']['slot'] if source['ref']['stage'] == 'initial' else 'initial-0')
                for i, source in enumerate(context['pending_findings'])]
        elif stage == 'judge':
            output.update(decision='match', scope_complete=True, new_findings=[],
                issue_verdicts=[dict(issue_id=i, decision='rejected', reason='Original source refutes the objection', evidence=['proposal:1']) for i in cycle['issues']])
        elif stage == 'answer':
            output.update(new_findings=[], answers=[dict(issue_id=i, disposition='withdraw',
                statement='I misread the domain', evidence=['proposal:1']) for i in context['answer_requests']])
        output.update(changes or {})
        self.runtime['executions'][execution_id] = dict(id=execution_id, role='identity_review', action=deepcopy(action),
                                                      status='running',
                                                      input_snapshot=self.head,
                                                      input_manifest={'prompt': {'sha256': 'actual-prompt-hash'}},
                                                      actor_kind='ai', owner_activity_id=action.get('owner_activity_id') or 'AY-fixture',
                                                      execution_profile_ref=deepcopy(getattr(self, 'profile', None)))
        admitted = self._admit_review_execution(action, self.runtime['executions'][execution_id])
        if admitted['disposition'] != 'admitted': raise ValueError(admitted['disposition'])
        if record_first:
            self._record_review_input(action, execution_id)
            self._record_review_input(action, execution_id)
        self.runtime['queue'].remove(action)
        self._apply_identity_review(action, output, execution_id)
        self.runtime['executions'][execution_id]['status'] = 'ended'
        self.runtime['executions'][execution_id]['outcome'] = 'output_accepted'
        self.runtime['executions'][execution_id]['output'] = deepcopy(output)
        return context, output, execution_id

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


def defer_review_for_research(engine):
    """Open a review of ``K1`` on a ``ReviewFakeEngine`` and defer its first initial review for fixed research.

    The deferred reviewer asks one question over the proposal's dependency
    closure and Lean code; returns the review cycle ID.
    """
    cid = engine._start_identity_review('K1')
    engine.execute()
    action = deepcopy(engine.pending())
    context = engine._prepare_review_context(action, engine.root / 'deferred')['context']
    requests = [{'id': 'domain', 'question': 'Which kernel constants does this exact declaration depend on?',
                 'source_refs': ['proposal:formal.dependency_closure', 'proposal:lean_code']}]
    # A started review execution carries the manifest of the prompt it was given.
    engine.runtime['executions']['INV-request'] = {'id': 'INV-request', 'role': 'identity_review',
        'status': 'running', 'action': action, 'actor_kind': 'ai', 'owner_activity_id': action['owner_activity_id'],
        'execution_profile_ref': deepcopy(engine.profile),
        'input_manifest': {'prompt': {'sha256': 'deferred-prompt-hash'}},
        'extensions': {'research_requests': requests}}
    output = {'proposal_digest': context['proposal_digest'], 'summary': 'Need a fixed-source comparison',
        'used_sources': [], 'questions': [], 'decision': 'unresolved', 'scope_complete': False, 'findings': []}
    if not engine._defer_review_for_research(action, output, 'INV-request'):
        raise AssertionError('The review was not deferred for research')
    engine.runtime['executions']['INV-request'].update(status='ended', outcome='output_accepted',
        output=deepcopy(output), input_snapshot=engine.head)
    return cid


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
    from do_math import review_cycle as rc
    from do_math.review_engine import ReviewEngineMixin
    from do_math.execution_lifecycle import create_execution
    from do_math.activities import assign_execution
    from engine_fixtures import FakeEngine
    from knowledge_fixtures import formal_evidence, knowledge_candidate
    from record_fixtures import execution_state
    from research_fixtures import scope_assessment
    instance, runtime = execution_state("identity_review")
    if verified:
        owner = FakeEngine(root)
        eid = owner.environment("synthetic-base", active=True)
        instance["trust_environments"] = deepcopy(owner.instance["trust_environments"])
        instance["active_trust_environment"] = eid
        runtime["trust_transitions"] = deepcopy(owner.runtime["trust_transitions"])
        runtime["trust_bindings"] = deepcopy(owner.runtime["trust_bindings"])
    instance = knowledge_io.ensure_ontology(instance)
    instance, runtime, kid = knowledge_io.import_candidate(instance, runtime, knowledge_candidate(
        explanation="Truth", lean_code="theorem t : True := True.intro", declaration_names=["t"]),
        source_ref="input", actor_ref="EX-1")
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
    assessment = ReviewEngineMixin._identity_assessment(cycle, reason="Scope remains incomplete")
    assessment["basis"] = kr.identity_basis(instance, kid)
    instance, aid = kr.record_identity_assessment(instance, kid, assessment, cycle["policy_ref"], runtime=runtime)
    return instance, runtime, kid, aid


class ReassessmentHarness(unittest.TestCase):
    """A ``ReviewFakeEngine`` whose ``K1`` review completed, ready for a reassessment of that assessment.

    Sets ``directory``, ``engine``, ``original`` (the first review cycle ID) and
    ``assessment``. ``request(evidence)`` is the public reassessment request for
    ``assessment``; ``defect()`` makes one initial reviewer's context include
    the author's and returns that evidence; ``use()`` is the assessment's use
    record; ``complete(decision='match')`` answers every queued review action
    toward ``decision``. Subclass it, or call ``setUp`` on an instance and
    ``doCleanups`` when done.
    """
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.engine = ReviewFakeEngine(self.directory.name)
        self.original = self.engine._start_identity_review('K1')
        while any(a['role'] == 'identity_review' for a in self.engine.runtime['queue']):
            self.engine.execute()
        self.assessment = self.engine.assessment()

    def request(self, evidence):
        return {'assessment_id': self.assessment['id'], 'assessment_sha256': exact_content_hash(self.assessment),
                'evidence': evidence}

    def defect(self):
        cycle = self.engine.runtime['review_cycles'][self.original]
        execution_id = cycle['results']['initial:1:initial-0']['execution_id']
        self.engine.runtime['executions'][execution_id]['context_origin'] = ['author']
        self.engine.runtime['executions']['author'] = {'id': 'author', 'status': 'ended'}
        return {'kind': 'author_context', 'execution_id': execution_id}

    def use(self):
        return next(row for row in self.engine.instance['assessment_uses'].values()
                    if row['assessment_id'] == self.assessment['id'])

    def complete(self, decision='match'):
        while any(a['role'] == 'identity_review' for a in self.engine.runtime['queue']):
            action = self.engine.pending()
            cycle = self.engine.runtime['review_cycles'][action['review_cycle_id']]
            changes = {}
            if action['stage'] == 'initial' and decision == 'unresolved':
                changes = {'decision': 'unresolved', 'scope_complete': False}
            elif action['stage'] == 'initial' and action['slot'] == 'initial-0' and decision == 'mismatch':
                changes = {'decision': 'mismatch', 'findings': [{'id': 'defect', 'statement': 'The stated domain differs', 'evidence': ['proposal']}]}
            elif action['stage'] == 'judge' and decision == 'mismatch':
                changes = {'decision': 'mismatch', 'issue_verdicts': [dict(issue_id=i, decision='approved', reason='Exact mismatch confirmed', evidence=['proposal']) for i in cycle['issues']]}
            self.engine.execute(changes)


class KnowledgeRoundtripHarness(unittest.TestCase):
    """A verified, not yet reviewed theorem in a real Git repository, with domain-produced sealed reviews.

    Sets ``root``, ``repo`` (a ``ResearchRepository``), ``state``, ``runtime``,
    ``kid`` and ``profile`` (the identity review profile).
    ``cycle(decision='match', proposal=None)`` runs one complete synthetic
    review of ``kid`` through the pure review cycle and records its executions;
    ``assessment(decision='match')`` records the identity assessment of such a
    cycle and returns its ID; ``roundtrip()`` publishes and reloads the state.
    """

    def setUp(self):
        from do_math.repository import ResearchRepository, new_id
        from do_math.configuration import DEFAULT_CONFIG
        from do_math.execution_profiles import build_profiles
        from knowledge_fixtures import verified_knowledge
        from research_fixtures import current_state, git_init, trust_environment, trust_fixture
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = git_init(self.directory.name)
        self.repo = ResearchRepository(self.root, new_id('RI'))
        environment, binding = trust_environment(trust_fixture(self.root, ['synthetic-lean']),
                                                 environment_id='TE-test', source_ref='synthetic:approval')
        self.state, self.runtime, self.kid, _ = verified_knowledge(environment, binding=binding, identity=False)
        # Every stored state passes the current lifecycle gate.
        self.state, self.runtime = current_state(self.state, self.runtime)
        profiles = build_profiles({**DEFAULT_CONFIG, 'lean_command': ['synthetic-lean']})
        self.profile = next(p for p in profiles['execution_profiles'].values() if p['role'] == 'identity_review')
        self.state.update(execution_profiles={self.profile['id']: self.profile}, capacity_constraints=profiles['capacity_constraints'])

    def cycle(self, decision='match', proposal=None):
        from do_math.repository import new_id
        from do_math import activities, execution_lifecycle
        from do_math.execution_profiles import profile_ref
        from do_math.review_cycle import accept_result, next_actions, start_review
        cid = new_id('RC')
        proposal = proposal or {**kr.proposal_view(self.state, self.kid), 'revision': 1}
        scoped = scoped_start(proposal, reviewers=2, max_rounds=1)
        cycle = start_review(proposal, reviewers=2, max_rounds=1, policy=scoped['review_policy'])
        activity = activities.open_activity(self.runtime, activity_id=new_id('AT'), activity_kind='identity_review',
            owner_ref=cid, input_refs=[self.kid], opened_at='2026-09-20T00:00:00Z')
        while next_actions(cycle):
            action = next_actions(cycle)[0]
            output = review_stage_output(cycle, action['stage'])
            if action['stage'] == 'scope':
                output.update(scope_complete=True, scope_assessment=scoped['scope_assessment'])
            elif action['stage'] == 'initial' and decision == 'mismatch' and action['slot'] == 'initial-0':
                output.update(decision='mismatch', findings=[{'id': 'objection', 'statement': 'Scope mismatch', 'evidence': ['proposal']}])
            elif action['stage'] == 'initial' and decision == 'unresolved':
                output.update(decision='unresolved', scope_complete=False)
            eid = new_id('EX')
            cycle = accept_result(cycle, action, output, eid)
            execution = execution_lifecycle.create_execution(execution_id=eid, owner_activity_id=activity['id'],
                actor_kind='ai', input_manifest={'proposal_digest': cycle['proposal_digest']},
                profile_ref=profile_ref(self.profile), created_at='2026-09-20T00:00:00Z')
            action_id = new_id('AC')
            execution.update(role='identity_review', action={'id': action_id, 'lineage_id': action_id,
                'role': 'identity_review', 'target': self.kid, 'review_cycle_id': cid, **action}, output=output)
            activities.assign_execution(self.runtime, activity['id'], execution)
            for status in ('starting', 'running'):
                execution_lifecycle.transition_execution(execution, status, at='2026-09-20T00:00:00Z')
            execution['submission_receipt'] = {'state': 'accepted', 'evidence_ref': 'synthetic:review'}
            execution_lifecycle.transition_execution(execution, 'stopping', at='2026-09-20T00:00:00Z', stop_phase='terminating')
            execution_lifecycle.transition_execution(execution, 'ended', at='2026-09-20T00:00:00Z', outcome='output_accepted')
        self.assertEqual(cycle['decision'], decision)
        cycle.update(id=cid, knowledge_id=self.kid, identity_basis=kr.identity_basis(self.state, self.kid), policy_ref='policy:fixture')
        self.runtime.setdefault('review_cycles', {})[cid] = cycle
        return cycle

    def assessment(self, decision='match'):
        from do_math.review_engine import ReviewEngineMixin
        cycle = self.cycle(decision)
        assessment = ReviewEngineMixin._identity_assessment(cycle, reason='Synthetic sealed review')
        self.state, aid = kr.record_identity_assessment(self.state, self.kid,
            {**assessment, 'basis': cycle['identity_basis']}, cycle['policy_ref'], runtime=self.runtime)
        return aid

    def roundtrip(self):
        if not hasattr(self, 'head'):
            self.head = self.repo.initialize(self.state, self.runtime)
        else:
            self.head = self.repo.save_with_state(self.head, self.state, self.runtime)[0]
        self.head, self.state, self.runtime = self.repo.load()


class ImpactReviewHarness(unittest.TestCase):
    """A research_work bundle held for impact review: it revises ``A`` and ``C`` and declares ``B`` in its impact.

    Sets ``api`` (``do_math.integration``), ``instance`` and ``runtime`` with the
    three imported observations ``ids`` (A, B, C) and the running producer
    ``EX-producer``, the producer ``output`` and ``extensions``, and the split
    ``bundle`` ``IN-held``. ``request()`` is its impact review request;
    ``review_output(request)`` is an independent review approving every plan;
    ``seal_review_fixture(execution, output, fixed, workspace)`` seals that
    review through the product's central capture and returns the artifacts to
    publish.
    """
    def seal_review_fixture(self, execution, output, fixed, workspace):
        """Use the actual central capture format before testing its consumer."""
        from unittest.mock import create_autospec
        from do_math import contracts, submission
        from do_math.execution_lifecycle import transition_execution
        from do_math.repository import canonical_json, new_id
        from research_fixtures import bare_engine
        schema = contracts.action_schema(fixed['action'])
        submission.install_tools(workspace, fixed, schema, None)
        (workspace / 'draft.json').write_bytes(canonical_json(output))
        sealed = submission.seal_submission(workspace, 'draft.json', execution_id=execution['id'],
            context=fixed, schema=schema, max_artifact_bytes=1024 * 1024)
        self.assertTrue(sealed['passed'], sealed['check']['issues'])
        host = bare_engine()
        host._lifecycle_event = create_autospec(host._lifecycle_event)
        artifacts = host._stage_submission_capture(execution, sealed,
            {'id': new_id('CT'), 'kind': 'submit_intent', 'state': 'accepted', 'execution_id': execution['id'],
             'received_at': '2026-09-20T00:00:01Z'}, origin='explicit_tool')
        transition_execution(execution, 'ended', at='2026-09-20T00:00:02Z', outcome='output_accepted')
        execution['submitted_output_ref'] = execution['submission_intent']['output_ref']
        return artifacts

    def setUp(self):
        from do_math import integration
        from do_math.knowledge import content_hash
        from record_fixtures import observation_knowledge, research_work_context, two_observation_output
        self.api = integration
        self.instance = knowledge_io.ensure_ontology({"knowledge": {}, "expositions": {}})
        self.runtime = {"executions": {
            "EX-producer": {"id": "EX-producer", "role": "research_work", "status": "running", "input_snapshot": "fixed-input"}}, "queue": []}
        self.ids = []
        for title in ("A", "B", "C"):
            self.instance, self.runtime, kid = knowledge_io.import_candidate(self.instance, self.runtime,
                observation_knowledge(title), source_ref="EX-producer", actor_ref="EX-producer")
            self.ids.append(kid)
        self.output = two_observation_output()
        self.output["knowledge"] = []
        self.output["integration_bundles"] = [{"integration_id": "IN-held", "members": ["output",
            "activity-extensions.json/knowledge_changes/0", "activity-extensions.json/knowledge_changes/1"],
            "impact_set": [self.ids[1]], "authority_refs": [],
            "previous_hashes": {kid: content_hash(self.instance["knowledge"][kid]) for kid in (self.ids[0], self.ids[2])}}]
        self.extensions = {"knowledge_changes": [{"id": kid, "changes": {"summary": "Revised " + str(n)},
            "reason": "Correct explanation", "impact_set": [self.ids[1]]} for n, kid in enumerate((self.ids[0], self.ids[2]))]}
        self.bundle = next(self.api.split_bundles(self.output, self.extensions, research_work_context()))

    def request(self):
        return self.api.bundle_impact_request(self.instance, self.runtime, self.bundle,
            producer_execution_id="EX-producer", input_snapshot=self.runtime["executions"]["EX-producer"]["input_snapshot"])

    def review_output(self, request):
        return {"summary": "Independent impact assessment", "questions": [], "used_sources": [],
            "report": "Compared each declared scope with its computed dependencies and supplied premises.", "remaining_work": [],
            "impact_review": {key: deepcopy(request[key]) for key in
                ("integration_id", "payload_sha256", "producer_execution_id", "input_snapshot")} | {
                "plan_decisions": [{"scope": scope, "plan_digest": plan["digest"], "decision": "approve",
                    "affected_ids": sorted(set(plan["computed_impact"]) | set(plan["declared_impact"])),
                    "reason": "The declared additional scope must also be reassessed."} for scope, plan in request["plans"].items()]},
            "integration_bundles": [{"integration_id": "IN-review", "members": ["output"],
                                     "impact_set": [], "authority_refs": []}]}
