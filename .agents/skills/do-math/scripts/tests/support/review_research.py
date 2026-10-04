"""Fixed-question review investigations of the review region: the owner-run scene on a Sim and the stored review scene.

A reviewer may answer an initial or judge slot with fixed questions (the
``research_requests`` activity extension) instead of a sealed judgment; the
slot is deferred, a ``supplemental_research`` investigation answers each
question from fixed sources only, and the answers return to the same slot.

On a Sim (3층):

- ``research_policy(review_rounds=2, review_research_limit=3)``: the review
  policy the legacy tests adopted: the configured default for two reviewers
  and ``review_rounds`` rounds, whose activity limit also authorizes the
  investigations and the deferred slot's replay (``2 * review_research_limit``).
- ``research_sim(**config)``: a restored copy of the purpose scenario
  (``support.engine_purpose``, the legacy ``purpose_fixtures.purpose_state(until='review')``
  on a Sim): the public activation with the purpose configuration updated by
  ``config`` adopted ``research_policy`` for it; ``PurposeResponder('direct')``
  answered preparation, contract review, planning and task A's research work,
  whose theorem ``add_zero_fixture`` the owner verified through the Lean double
  and whose identity review it opened; the scope review is queued with whatever
  else the flow queued, and no execution is unfinished (preserved rule K-21).
  One template per configuration, built once per process.
- ``InvestigationResponder(repeat=False, batch=False)``: the Sim model double's
  responder (``ModelDouble.responder``); the purpose responder
  (``support.engine_purpose.PurposeResponder``, with its input checks, preserved
  rule K-32) answering with ``InvestigationRunner``, moved from the legacy
  ``test_review_research``. The first initial slot ``initial-0`` asks the
  fixed question ``domain`` (``batch``: also ``export``; ``repeat``: an
  unanswerable one, every time), investigators answer from the fixed sources,
  every other call answers as ``PurposeAnswers``. Its input checks stay (preserved
  rule K-46): each returned or supplied source must still have its fixed hash,
  and an investigation must not inherit a task execution contract; a failed
  check is kept in ``failures``, so ``support.engine_purpose.drive`` fails the
  test at once. ``research_answers`` and ``resumed_contexts`` are the runner's.
- ``record_prompts(sim)``: the list of prompts the model double receives, in
  call order (the worker hands the provider CLI its prompt on standard input);
  the double answers as before. ``research_fixtures.role_reach`` reads a role's
  actual prompt.

On the stored review scene (``support.review_scene.ReviewScene``, 2층):

- ``defer_review_for_research(scene)``: opens a review of ``K1``, runs its scope
  and defers the first initial slot for one fixed question over the proposal's
  checked axioms and Lean code, as an execution ``INV-request`` that asked it;
  a review that is not deferred fails at once (preserved rule K-52). Returns
  the review cycle ID. The same steps as ``review_fixtures.defer_review_for_research``,
  which runs on ``ReviewFakeEngine`` and stays for the legacy tests that still use it.
- ``research_profile(engine)``: the profile reference of the investigation role.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
from pathlib import Path

from do_math.canonical import canonical_json
from do_math.execution_profiles import profile_ref
from do_math.review_policy import build_review_policy
from support.purpose_answers import EXPLANATION, PurposeAnswers, common
from support.engine_purpose import PURPOSE_CONFIG, PurposeResponder
from support.sim import Sim, built


def research_policy(review_rounds=2, review_research_limit=3):
    policy = build_review_policy(reviewer_count=2, max_rounds=review_rounds)
    # The investigations and the deferred slot's replay, besides the final review calls the base policy reserves.
    policy['activity_execution_limit'] += 2 * review_research_limit
    return policy


def build_research_sim(root, shared, *, settings, policy):
    sim = Sim(root, shared=shared, config=settings)
    sim.activate(review_policy=policy)
    sim.model.responder = PurposeResponder()
    for _ in range(45):
        sim.step()
        if sim.model.responder.failures:
            raise AssertionError('The purpose responder refused its input: ' + '; '.join(sim.model.responder.failures))
        if sim.runtime['review_cycles']:
            break
        if sim.runtime['status'] in {'paused', 'closed', 'waiting'}:
            raise AssertionError('The purpose flow stopped before its review: ' + repr(sim.waiting()))
    else:
        raise AssertionError('The purpose flow did not open its review: ' + repr(sim.waiting()))
    unfinished = [row['id'] for row in sim.runtime['executions'].values() if row['status'] != 'ended']
    if unfinished:
        raise AssertionError('A template must not end with unfinished executions: ' + repr(unfinished))
    return sim


def research_sim(**config):
    """A restored purpose scenario whose identity review just opened; see the module docstring."""
    settings = {**PURPOSE_CONFIG, **config}
    policy = research_policy(settings.get('review_rounds', 2), settings.get('review_research_limit', 3))

    return built('review-research', build_research_sim, settings=settings, policy=policy)


class InvestigationRunner(PurposeAnswers):
    """``PurposeAnswers`` whose first initial reviewer asks fixed questions and whose investigators answer them."""

    def __init__(self, *, repeat=False, batch=False):
        super().__init__('direct')
        self.repeat, self.batch = repeat, batch
        self.research_answers = []
        self.resumed_contexts = []

    def answer(self, role, context, workspace):
        action = context['action']
        if role == 'identity_review' and action['stage'] == 'initial' and action['slot'] == 'initial-0':
            review = context['role_review']
            if not review['supplemental_results'] or self.repeat:
                requests = [{'id': 'domain', 'question': 'Which binder domain does the exact exported declaration signature use?',
                             'source_refs': ['proposal:formal.declaration_signatures', 'proposal:lean_code']}]
                if self.repeat:
                    requests[0]['question'] = 'Does this signature match the external textbook definition that has not been supplied?'
                if self.batch:
                    requests.append({'id': 'export', 'question': 'Which declaration exports the supplied proof?',
                                     'source_refs': ['proposal:declaration_names', 'proposal:lean_code']})
                (workspace / 'activity-extensions.json').write_bytes(canonical_json({'research_requests': requests}))
                return {**common('A fixed source comparison is needed before my complete review'),
                    'proposal_digest': review['proposal_digest'], 'decision': 'unresolved', 'scope_complete': False, 'findings': []}
            self.resumed_contexts.append(deepcopy(review))
            for research in review['supplemental_results']:
                for source in research['result']['source_records']:
                    raw = (workspace / source['local_path']).read_bytes()
                    if hashlib.sha256(raw).hexdigest() != source['sha256']:
                        raise AssertionError('Returned supplemental source differs from its fixed hash')
            return super().answer(role, context, workspace)
        if role == 'supplemental_research':
            research = context['review_research']
            if context.get('task') is not None:
                raise AssertionError('Review investigation incorrectly inherited a task execution contract')
            for source in research['sources']:
                raw = (workspace / source['local_path']).read_bytes()
                if hashlib.sha256(raw).hexdigest() != source['sha256']:
                    raise AssertionError('Investigator source differs from its fixed hash')
            if self.repeat:
                output = {**common('The external textbook definition is not among the fixed inputs'),
                    'questions': ['The exact external definition remains unavailable'],
                    'research_request_id': research['id'], 'request_digest': research['request_digest'],
                    'outcome': 'unresolved', 'answer': 'The supplied signature cannot establish equivalence to an unavailable textbook definition.',
                    'scope_complete': False, 'evidence_refs': []}
            else:
                answer = 'The binder domain is Nat.' if 'binder domain' in research['question'] else 'The exported declaration is add_zero_fixture.'
                (workspace / 'comparison.txt').write_text(answer + '\n' + EXPLANATION, encoding='utf-8')
                output = {**common('The requested exact source comparison is complete'),
                    'used_sources': [research['sources'][0]['ref']], 'research_request_id': research['id'],
                    'request_digest': research['request_digest'], 'outcome': 'answered', 'answer': answer,
                    'scope_complete': True, 'evidence_refs': [research['sources'][0]['ref'], 'workspace:comparison.txt']}
            self.research_answers.append(deepcopy(output))
            return output
        return super().answer(role, context, workspace)


class InvestigationResponder(PurposeResponder):
    """The purpose responder answering with ``InvestigationRunner``; see the module docstring."""

    def __init__(self, *, repeat=False, batch=False):
        super().__init__()
        self.runner = InvestigationRunner(repeat=repeat, batch=batch)

    @property
    def research_answers(self):
        return self.runner.research_answers

    @property
    def resumed_contexts(self):
        return self.runner.resumed_contexts


def record_prompts(sim):
    """The prompts ``sim``'s model double receives, appended in call order; see the module docstring."""
    from support.model import FakeCLI
    prompts, model = [], sim.model

    class PromptCLI(FakeCLI):
        def communicate(self, input=None, timeout=None):
            prompts.append(input.decode('utf-8'))
            return super().communicate(input, timeout)

    def spawn(command, *, stdin=None, stdout=None, stderr=None, cwd=None, env=None, shell=False, creationflags=0):
        return PromptCLI(model, list(command), stdout, stderr, Path(cwd))
    # The Sim's worker programs look up ``sim.model.spawn`` each time a Job runs.
    model.spawn = spawn
    return prompts


def research_profile(engine):
    return profile_ref(next(p for p in engine.instance['execution_profiles'].values() if p['role'] == 'supplemental_research'))


def defer_review_for_research(scene):
    """Open a review of ``K1`` and defer its first initial review for one fixed question; see the module docstring."""
    engine = scene.engine
    cid = engine._start_identity_review('K1')
    scene.execute()
    action = deepcopy(scene.pending())
    context = engine._prepare_review_context(action, scene.root / 'deferred')['context']
    requests = [{'id': 'domain', 'question': 'Which axioms does this exact declaration use?',
                 'source_refs': ['proposal:formal.axioms', 'proposal:lean_code']}]
    # A started review execution carries the manifest of the prompt it was given.
    engine.runtime['executions']['INV-request'] = {'id': 'INV-request', 'role': 'identity_review',
        'status': 'running', 'action': action, 'actor_kind': 'ai', 'owner_activity_id': action['owner_activity_id'],
        'execution_profile_ref': deepcopy(scene.profile),
        'input_manifest': {'prompt': {'sha256': 'deferred-prompt-hash'}},
        'extensions': {'research_requests': requests}}
    output = {'proposal_digest': context['proposal_digest'], 'summary': 'Need a fixed-source comparison',
        'used_sources': [], 'questions': [], 'decision': 'unresolved', 'scope_complete': False, 'findings': []}
    if not engine._defer_review_for_research(action, output, 'INV-request'):
        raise AssertionError('The review was not deferred for research')
    engine.runtime['executions']['INV-request'].update(status='ended', outcome='output_accepted',
        output=deepcopy(output), input_snapshot=engine.head)
    return cid
