"""Identity review scenes of the review region: the review state on the real engine and repository.

The legacy ``review_fixtures.ReviewFakeEngine`` subclassed the product engine,
skipped its ``__init__``, replaced ``_save`` with an autospec double and gave it
a store that read no artifact. ``ReviewScene`` keeps the same synthetic state
(``support.storage_role_inputs.review_candidate_state``: one candidate theorem
``K1`` with verified formal evidence and the fixture review policy) and the
same reviewer answers, but the engine is the product's ``ResearchEngine``
loaded from a ``ResearchRepository`` on the Git port's fake that validated the
state through the storage contract, on the port fakes. Nothing is replaced.

- ``ReviewScene(root, rounds=2)``: ``engine`` (the real engine), ``root`` (a
  scratch folder for review workspaces), ``scope`` (the settled fixture scope
  ``start`` gives), ``profile`` (the execution profile reference ``execute``
  records; a test may set another). The stored state is built and validated
  once per process and round limit and restored for each scene at the same
  absolute path (as ``Sim.activated()`` restores its template), so a test
  finishes with one scene of a round limit before creating the next.
- ``start(kid='K1', previous_cycle_id=None, scope=None)`` opens a review of
  ``kid`` at its initial slots with the fixture scope
  (``research_fixtures.start_scoped_review``); the engine itself opens every
  review at its scope stage (``engine._start_identity_review``).
- ``pending()`` is the next queued identity review action; ``assessment(kid)``
  and ``usable(kid)`` read the published result; ``revise()`` creates the
  successor candidate ``K2``.
- ``execute(changes=None, *, record_first=False)`` answers the pending action
  as the legacy double did (scope: the fixture scope; initial: match;
  organize: one issue per pending finding; judge: reject every issue; answer:
  withdraw every objection), admits the attempt through the owner admission
  and applies the answer (``_apply_identity_review``). An admission other than
  ``admitted`` fails at once (preserved rule K-52). Returns ``(context, output,
  execution ID)``; attempts are ``ex-1``, ``ex-2``, ... in order.

The answers bypass the model call and the submission path, as the legacy
double did: the tests that use a scene examine the review mixin (layer 2).
The wiring from the owner's registration and a sealed submission to the same
mixin runs on a ``Sim``: ``sim/test_review_owner_path.py`` (``OwnerReviewTests``)
and ``flows/test_review_owner_flows.py`` (``DisputeFlowTests``).
"""
from __future__ import annotations

import atexit
from copy import deepcopy
from pathlib import Path
import shutil
import tempfile

from do_math import knowledge_records as kr
from do_math.configuration import DEFAULT_CONFIG
from do_math.engine import ResearchEngine
from do_math.execution_profiles import build_profiles, profile_ref
from research_fixtures import current_state, start_scoped_review
from support.fakes.clock import FakeClock
from support.fakes.git_backend import InProcessGit
from support.sim import _remove
from support.storage_records import INSTANCE_ID, engine_on, fake_ports, record_store
from support.storage_role_inputs import review_candidate_state


def initialized_families():
    """``(instance, runtime)`` families the product's initialization gives every instance empty (``initialize_state``)."""
    from do_math.initialization import initialize_state
    instance, runtime = initialize_state(instance_id='RI-fixture', goal='fixture', workspace='work',
                                         config=deepcopy(DEFAULT_CONFIG), source_input='fixture input', clock=FakeClock())
    return tuple({key: value for key, value in state.items() if isinstance(value, (dict, list)) and not value}
                 for state in (instance, runtime))


class _Template:
    """One stored review state per process and round limit, restored for each scene.

    The build stores the state once (the storage contract validates it); a
    restore copies the untouched repository and workspace back to the same
    absolute path the state names, gives a fresh Git fake a copy of the stored
    objects and a clock at the build's time, and loads a new engine. A restore
    replaces the previous copy, so a test finishes with one scene of a round
    limit before asking for the next. The trust toolchain stays in ``shared``,
    which is never copied: the trust record fingerprints its files by creation time.
    """

    def __init__(self, rounds):
        self.base = Path(tempfile.mkdtemp(prefix='do-math-review-')).resolve()
        atexit.register(_remove, self.base)
        self.live, self.pristine, shared = (self.base / name for name in ('live', 'pristine', 'shared'))
        instance, runtime, self.scope = review_candidate_state(shared / 'trust', rounds=rounds)
        # The whole configuration the profiles were built from, as every initialized instance has;
        # the owner's registration reads it (model selection).
        instance['config'] = {**deepcopy(DEFAULT_CONFIG), **instance['config']}
        empty_instance, empty_runtime = initialized_families()
        instance = {**empty_instance, **instance, 'object_format': 'sha1'}
        instance['capacity_constraints'] = build_profiles(DEFAULT_CONFIG)['capacity_constraints']
        instance, runtime = current_state(instance, {**empty_runtime, **runtime})
        clock, backend = FakeClock(), InProcessGit()
        store = record_store(self.live / 'repository', backend=backend, clock=clock)
        engine_on(store, instance, runtime, workspace=self.live / 'work', ports=fake_ports(clock, backend))
        self.objects, self.clock = backend.objects, clock.state()
        shutil.copytree(self.live, self.pristine)
        self.used = False

    def restore(self):
        if self.used:
            _remove(self.live)
            shutil.copytree(self.pristine, self.live)
        self.used = True
        clock, backend = FakeClock(*self.clock), InProcessGit({key: dict(value) for key, value in self.objects.items()})
        return ResearchEngine(self.live / 'repository', INSTANCE_ID, ports=fake_ports(clock, backend))


_TEMPLATES = {}


def warm(rounds=2):
    """Build this process's template for ``rounds`` now; a test module's ``setUpModule`` so no test pays the build."""
    _template(rounds)


def _template(rounds):
    """The template for ``rounds``; a failed build is not retried, since every later scene would repeat its cost."""
    if rounds not in _TEMPLATES:
        _TEMPLATES[rounds] = 'failed'
        _TEMPLATES[rounds] = _Template(rounds)
    elif _TEMPLATES[rounds] == 'failed':
        raise AssertionError(f'the review scene template for {rounds} rounds failed to build earlier in this process')
    return _TEMPLATES[rounds]


class ReviewScene:
    def __init__(self, root, rounds=2):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        template = _template(rounds)
        self.scope = deepcopy(template.scope)
        self.engine = template.restore()
        self.profile = profile_ref(next(p for p in self.engine.instance['execution_profiles'].values()
                                        if p['role'] == 'identity_review'))
        self.sequence = 0

    def start(self, kid='K1', previous_cycle_id=None, scope=None):
        """Open a review of ``kid`` that begins at its initial slots with the fixture scope."""
        return start_scoped_review(self.engine, kid, scope or self.scope, previous_cycle_id)

    def pending(self):
        return next(a for a in self.engine.runtime['queue'] if a['role'] == 'identity_review')

    def cycle(self, cycle_id):
        return self.engine.runtime['review_cycles'][cycle_id]

    def assessment(self, kid='K1'):
        engine = self.engine
        cid = engine.instance['knowledge'][kid]['review_cycle_id']
        return engine.instance['identity_assessments'][engine.runtime['review_cycles'][cid]['assessment_id']]

    def usable(self, kid='K1'):
        return bool(kr.usable_links(self.engine.instance, kid))

    def revise(self, previous_id='K1', new_id='K2'):
        """Create the successor candidate ``new_id`` of ``previous_id`` (one revision later, a longer explanation)."""
        engine = self.engine
        proposal = kr.proposal_view(engine.instance, previous_id)
        candidate = {key: deepcopy(value) for key, value in proposal.items()
                     if key not in {'formal', 'status', 'review_cycle_id', 'review_history', 'formal_result_id', 'exposition_id'}}
        candidate.update(id=new_id, supersedes=previous_id, revision=proposal['revision'] + 1,
                         explanation='Expanded proof by reflexivity', formal_result_ref=proposal['formal_result_id'])
        engine.instance, _ = kr.create_candidate(engine.instance, candidate, source_ref='test-revision', actor_ref='author')
        return new_id

    def execute(self, changes=None, *, record_first=False):
        """Answer the pending identity review action as a reviewer and apply the answer; see the module docstring."""
        engine = self.engine
        action = self.pending()
        self.sequence += 1
        execution_id = f'ex-{self.sequence}'
        workspace = self.root / execution_id / 'workspace'
        context = engine._prepare_review_context(action, workspace)['context']
        cycle = engine.runtime['review_cycles'][action['review_cycle_id']]
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
            output['issues'] = [dict(id=f'issue-{len(cycle["issues"]) + i}', finding_refs=[source['ref']],
                                     answer_role_slot_id=source['ref']['slot'] if source['ref']['stage'] == 'initial' else 'initial-0')
                                for i, source in enumerate(context['pending_findings'])]
        elif stage == 'judge':
            output.update(decision='match', scope_complete=True, new_findings=[],
                          issue_verdicts=[dict(issue_id=i, decision='rejected', reason='Original source refutes the objection',
                                               evidence=['proposal:1']) for i in cycle['issues']])
        elif stage == 'answer':
            output.update(new_findings=[], answers=[dict(issue_id=i, disposition='withdraw', statement='I misread the domain',
                                                         evidence=['proposal:1']) for i in context['answer_requests']])
        output.update(changes or {})
        engine.runtime['executions'][execution_id] = dict(
            id=execution_id, role='identity_review', action=deepcopy(action), status='running', input_snapshot=engine.head,
            input_manifest={'prompt': {'sha256': 'actual-prompt-hash'}}, actor_kind='ai',
            owner_activity_id=action.get('owner_activity_id') or 'AY-fixture', execution_profile_ref=deepcopy(self.profile))
        admitted = engine._admit_review_execution(action, engine.runtime['executions'][execution_id])
        if admitted['disposition'] != 'admitted':
            raise ValueError(admitted['disposition'])
        if record_first:
            engine._record_review_input(action, execution_id)
            engine._record_review_input(action, execution_id)
        engine.runtime['queue'].remove(action)
        engine._apply_identity_review(action, output, execution_id)
        execution = engine.runtime['executions'][execution_id]
        execution.update(status='ended', outcome='output_accepted', output=deepcopy(output))
        return context, output, execution_id
