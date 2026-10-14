"""Knowledge records stored and reloaded through the real ``ResearchRepository`` on the Git port's fake.

``KnowledgeRoundtripHarness`` replaces ``review_fixtures.KnowledgeRoundtripHarness``,
which published through a real ``git`` repository (``research_fixtures.git_init``).
Here the repository is the same ``ResearchRepository`` with its storage contract
over the in-process Git fake and the fake clock (설계 4.3); the real Git backend's
publication and reads are the boundary's (``boundary.test_git_process_storage``).
Reviews stay synthetic, as in the legacy harness: their executions are recorded
directly and their cycle runs through the pure review cycle.

- ``KnowledgeRoundtripHarness`` (a ``unittest.TestCase`` base without tests): a
  verified, not yet reviewed theorem "Truth" ``kid`` in the active trust
  environment ``TE-test`` (a synthetic toolchain under ``root``), with ``root``,
  ``repo``, ``clock``, ``state`` (its workspace ``root/'work'``), ``runtime`` and
  ``profile`` (the identity review profile).
  ``cycle(decision='match', proposal=None)`` runs one complete synthetic review
  of ``kid`` through the pure review cycle and records its executions;
  ``assessment(decision='match')`` records the identity assessment of such a
  cycle and returns its ID; ``roundtrip()`` publishes and reloads the state;
  ``engine()`` is the product's ``ResearchEngine`` loaded from the last
  published head on the port fakes that share the repository's clock and Git fake.
- ``installed_request(workspace, toolchain)``: the registration request that
  adopts the installed ``toolchain`` through a toolchain record written under
  ``workspace`` (its fingerprint and content hashes are real; validation is a double).
- ``installed_trust_state(workspace, toolchain)``: ``(instance, runtime, kid)``, an
  unverified candidate "Truth" in the active environment ``TE-old`` registered
  from ``installed_request``. This is the state half of
  ``knowledge_fixtures.formal_boundary_engine`` without its engine doubles; it
  fails at once when the synthetic environment does not validate, as that fixture did.
"""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

from do_math import activities, execution_lifecycle, knowledge_records as kr
from do_math.configuration import DEFAULT_CONFIG
from do_math.execution_profiles import build_profiles, profile_ref
from do_math.review_cycle import accept_result, identity_assessment, next_actions, start_review
from support.knowledge_builders import add_knowledge, verified_knowledge
from support.state_builders import current_state
from support.trust_inputs import trust_environment, trust_fixture, validation_fixture
from support.review_inputs import review_stage_output, scoped_start
from support.fakes.clock import FakeClock
from support.fakes.git_backend import InProcessGit
from support.storage_records import INSTANCE_ID, fake_ports, record_store


class KnowledgeRoundtripHarness(unittest.TestCase):
    def setUp(self):
        from support.entry import entry
        _entry = entry()
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name).resolve()
        self.clock, self.backend = FakeClock(), InProcessGit()
        self.repo = record_store(self.root, backend=self.backend, clock=self.clock)
        environment, binding = trust_environment(trust_fixture(self.root, ['synthetic-lean']),
                                                 environment_id='TE-test', source_ref='synthetic:approval')
        self.state, self.runtime, self.kid, _ = verified_knowledge(environment, binding=binding, identity=False)
        # Every stored state passes the current lifecycle gate.
        self.state, self.runtime = current_state(self.state, self.runtime)
        profiles = build_profiles({**DEFAULT_CONFIG, 'lean_command': ['synthetic-lean']}, host=_entry.ports.host)
        self.profile = next(p for p in profiles['execution_profiles'].values() if p['role'] == 'identity_review')
        self.state.update(execution_profiles={self.profile['id']: self.profile},
                          capacity_constraints=profiles['capacity_constraints'])
        # A loaded engine opens its control transport under the instance workspace.
        self.state['workspace'] = str(self.root / 'work')

    def cycle(self, decision='match', proposal=None):
        cid = self.clock.new_id('RC')
        proposal = proposal or {**kr.proposal_view(self.state, self.kid), 'revision': 1}
        scoped = scoped_start(proposal, reviewers=2, max_rounds=1)
        cycle = start_review(proposal, reviewers=2, max_rounds=1, policy=scoped['review_policy'])
        activity = activities.open_activity(self.runtime, activity_id=self.clock.new_id('AT'), activity_kind='identity_review',
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
            eid = self.clock.new_id('EX')
            cycle = accept_result(cycle, action, output, eid)
            execution = execution_lifecycle.create_execution(execution_id=eid, owner_activity_id=activity['id'],
                actor_kind='ai', input_manifest={'proposal_digest': cycle['proposal_digest']},
                profile_ref=profile_ref(self.profile), created_at='2026-09-20T00:00:00Z')
            action_id = self.clock.new_id('AC')
            execution.update(role='identity_review', action={'id': action_id, 'lineage_id': action_id,
                'role': 'identity_review', 'target': self.kid, 'review_cycle_id': cid, **action}, output=output)
            activities.assign_execution(self.runtime, activity['id'], execution)
            for status in ('starting', 'running'):
                execution_lifecycle.transition_execution(execution, status, at='2026-09-20T00:00:00Z')
            execution['submission_receipt'] = {'state': 'accepted', 'evidence_ref': 'synthetic:review'}
            execution_lifecycle.transition_execution(execution, 'stopping', at='2026-09-20T00:00:00Z')
            execution_lifecycle.transition_execution(execution, 'ended', at='2026-09-20T00:00:00Z', outcome='output_accepted')
        self.assertEqual(cycle['decision'], decision)
        cycle.update(id=cid, knowledge_id=self.kid, identity_basis=kr.identity_basis(self.state, self.kid), policy_ref='policy:fixture')
        self.runtime.setdefault('review_cycles', {})[cid] = cycle
        return cycle

    def assessment(self, decision='match'):
        from support.entry import entry
        _entry = entry()
        cycle = self.cycle(decision)
        assessment = identity_assessment(cycle, reason='Synthetic sealed review')
        self.state, aid = kr.record_identity_assessment(self.state, self.kid,
            {**assessment, 'basis': cycle['identity_basis']}, cycle['policy_ref'], runtime=self.runtime, clock=_entry.ports.clock)
        return aid

    def roundtrip(self):
        if not hasattr(self, 'head'):
            self.head = self.repo.initialize(self.state, self.runtime)
        else:
            self.head = self.repo.save_with_state(self.head, self.state, self.runtime)[0]
        self.head, self.state, self.runtime = self.repo.load()

    def engine(self):
        """The product engine loaded from the published head; call ``roundtrip`` first (the state names its workspace)."""
        from support.entry import entry
        _entry = entry()
        from do_math.engine import ResearchEngine
        return ResearchEngine(self.repo.repository, INSTANCE_ID, ports=fake_ports(self.clock, self.backend), codex_home=_entry.codex_home, environment=_entry.environment, host_id=_entry.host_id)


def installed_request(workspace, toolchain):
    """The registration request (``operation: register``) that adopts the installed ``toolchain``.

    Its toolchain record is written under ``workspace/'records'``; the record's
    fingerprint and content baseline use the installed judgment files' actual
    metadata and bytes. Clean-build validation alone is synthetic: this fixture
    does not approve or rewrite the installation's shared trust record.
    """
    from support.entry import entry
    _entry = entry()
    from do_math import trust_inventory as records
    identity = deepcopy(toolchain)
    fingerprint = records.observe_fingerprint(identity)
    content = records.content_hashes(identity, fingerprint['files'])
    record = records.new_record(identity, records.new_baseline(fingerprint,
        content, validation_fixture(identity, Path(workspace) / 'smoke.lean'), clock=_entry.ports.clock))
    path = Path(workspace) / 'records' / (record['id'] + '.json')
    records.write_record(path, record)
    return records.registration_request(record, path, records.binding(record))


def installed_trust_state(workspace, toolchain):
    request = installed_request(workspace, toolchain)
    trust, binding = trust_environment(request, environment_id='TE-old', source_ref='synthetic:test-adoption')
    from do_math.trust_validation import environment_errors
    errors = environment_errors(trust, binding)
    if errors:
        raise AssertionError('The synthetic trust environment does not validate: ' + repr(errors))
    instance = {'active_trust_environment': 'TE-old', 'trust_environments': {'TE-old': trust}}
    runtime = {'queue': [], 'history': [], 'trust_bindings': {'TE-old': binding}}
    instance, runtime, kid, _ = add_knowledge(instance, runtime, verified=False)
    return instance, runtime, kid
