"""Knowledge imports by public control and the owner's central formal check of a proposal, on the Sim (설계 4.1).

Imports, kind registrations and revisions enter through the public
``knowledge`` control and the owner applies them; every publication passes the
storage contract. The formal check is the owner's dispatch in one owner pass
(``sim.step()``): ``verify_formal`` and ``verify_lean`` run on
the Jobs port fake, whose program runs ``formal._worker`` with the Lean double
at its spawn seam, and the owner's continuation records the result, ends the
execution and opens the identity review. The legacy tests called ``_formal`` on
``knowledge_fixtures.formal_boundary_engine``: a bare engine whose admission,
storage, registration, activity and review start were autospec doubles and
whose ``governance.authorize`` was patched to allow. Here nothing is replaced;
calls are observed as they start (``ObservedCalls``) and a verifier that
records its arguments and runs ``verify_lean`` (``recorded_verifier``) replaces
the patched verifier ``Mock``. The installed Lean runs the same consumer in
``boundary.test_knowledge_formal_consumer``.
"""
from copy import deepcopy
from pathlib import Path
import unittest

from do_math import activities, execution_lifecycle, formal, knowledge_records as kr
from do_math.execution_profiles import profile_ref
from do_math.knowledge import assess_use, plan_impact, revision_roots
from do_math.state_contract import default_state_contract
from support.knowledge_builders import knowledge_candidate
from support.engine_lifecycle import (applied, clear_work, next_environment, only, recorded_verifier, run_machine,
                                      task, transition)
from support.provider_probes import ObservedCalls
from support.review_sim import THEOREM, cycle_of, opened_sim, reviewed_sim, theorem_id, warm_opened, warm_reviewed
from support.sim import Sim, warm_template


def setUpModule():
    warm_template()
    warm_opened()
    warm_reviewed()


def imported(sim, candidate):
    """Import ``candidate`` by public control on a Sim with no other work; returns its knowledge ID."""
    clear_work(sim)
    applied(sim, 'knowledge', config={'operation': 'import', 'candidate': candidate})
    return next(kid for kid, row in sim.instance['knowledge'].items() if row['title'] == candidate['title'])


def audit_goal_once(engine, kid):
    """One configured goal auditor returns ``satisfied`` on ``kid`` and the engine's receiver records its judgment.

    As ``engine_lifecycle.solve_goal`` does for every auditor; with one of the two the goal stays unsolved.
    """
    from support.engine_lifecycle import _ended_execution
    basis, required = engine._goal_basis_key(), engine.instance['config']['goal_auditors']
    _ended_execution(engine, 'EX-goal-audit-0', 'goal_audit')
    engine._bind_governance_input({'role': 'goal_audit'}, engine.runtime['executions']['EX-goal-audit-0'],
                                  engine._governance_context({'role': 'goal_audit'}, {}))
    engine._apply({'role': 'goal_audit', 'slot': 0, 'basis': basis, 'required': required},
                  {'decision': 'satisfied', 'scope_complete': True, 'used_sources': [kid],
                   'summary': 'Fixture auditor response for the stated charter', 'questions': []}, 'EX-goal-audit-0')


class KnowledgeImportTests(unittest.TestCase):
    def test_import_is_persisted_as_families_with_exact_source(self):
        sim = Sim.activated()
        data = knowledge_candidate()
        data.update(lean_code='theorem \u212a : True := True.intro\r\ntheorem K : True := True.intro\n-- e\u0301\n',
                    declaration_names=['\u212a', 'K'])
        kid = imported(sim, data)
        record = sim.instance['knowledge'][kid]
        self.assertFalse(assess_use(record, sim.instance)['valid'])
        self.assertNotIn('formal', record)
        self.assertNotIn('reviews', record)
        self.assertTrue(any(a['role'] == 'formal_check' and a['target'] == kid for a in sim.runtime['queue']))
        head, loaded, runtime = sim.engine.store.load()
        self.assertEqual(head, sim.engine.head)
        self.assertEqual(loaded['formal_results'], sim.instance['formal_results'])
        self.assertEqual(loaded['expositions'], sim.instance['expositions'])
        restored = kr.proposal_view(loaded, kid)
        self.assertEqual(restored['lean_code'].encode(), data['lean_code'].encode())
        self.assertEqual(restored['declaration_names'], data['declaration_names'])

    def test_duplicate_import_does_not_replace_saved_record(self):
        sim = Sim.activated()
        kid = sim.ports.clock.new_id('KN')
        clear_work(sim)
        applied(sim, 'knowledge', config={'operation': 'import', 'candidate': knowledge_candidate(id=kid)})
        saved = deepcopy(sim.instance['knowledge'][kid])
        count = len(sim.instance['knowledge'])
        request = sim.control('knowledge', text='duplicate import', config={
            'operation': 'import', 'candidate': knowledge_candidate(id=kid, summary='Changed')})
        sim.engine.process_controls()
        self.assertEqual(sim.instance['knowledge'][kid], saved)
        self.assertEqual(len(sim.instance['knowledge']), count)
        rejected = [row for row in sim.runtime['history'] if row.get('kind') == 'rejected_user_control'
                    and row['request']['id'] == request['request_id']]
        self.assertEqual(len(rejected), 1, sim.runtime['history'])
        self.assertEqual(rejected[0]['reason'], 'record ID already exists; revisions require a new ID')

    def test_ended_instance_refuses_knowledge_imports(self):
        sim = Sim.activated()
        engine = sim.engine
        knowledge = deepcopy(engine.instance['knowledge'])
        for status in ('completed', 'closed'):
            with self.subTest(status=status):
                engine.runtime['status'] = status
                with self.assertRaisesRegex(ValueError, '^closed/completed instance cannot apply knowledge controls$'):
                    engine._knowledge_io_control({'action': 'knowledge', 'id': sim.ports.clock.new_id('UC'),
                                                  'config': {'operation': 'import', 'candidate': knowledge_candidate()}})
                self.assertEqual(engine.runtime['status'], status)
                self.assertEqual(engine.instance['knowledge'], knowledge)

    def test_custom_kind_reaches_worker_catalog_only_after_check_and_activation(self):
        """The kind check's verdict is applied by the central consumer (``_apply_kind_definition_check``) for a
        synthetic AI verdict on its own execution, as in the legacy test; the check's model call is not run."""
        sim = Sim.activated()
        engine = sim.engine
        definition = dict(family='knowledge', token='computational_lemma',
                          meaning='An explicitly bounded computational proposition.', constraints={})
        clear_work(sim)
        applied(sim, 'knowledge', config={'operation': 'register-kind', 'definition': definition})

        def kinds():
            # Each actual invocation receives a new immutable input workspace.
            context = sim.engine._context({'role': 'research_preparation'}, sim.root / sim.ports.clock.new_id('EX'))
            return [row['token'] for row in context['kind_definitions']['knowledge']]
        self.assertNotIn(definition['token'], kinds())
        # Only the central consumer of an independent check activates a kind.
        engine = sim.engine
        action = next(a for a in engine.runtime['queue'] if a.get('kind_definition_id'))
        identifier = action['kind_definition_id']
        profile = next(p for p in engine.instance['execution_profiles'].values() if p['role'] == 'maintenance')
        activity = activities.open_activity(engine.runtime, activity_id=sim.ports.clock.new_id('AT'), activity_kind='maintenance',
            owner_ref=identifier, input_refs=[identifier], opened_at=sim.ports.clock.now())
        eid = sim.ports.clock.new_id('EX')
        basis = {'kind_definition': {'id': identifier, 'sha256': action['kind_definition_sha256']}}
        execution = execution_lifecycle.create_execution(execution_id=eid, owner_activity_id=activity['id'],
            actor_kind='ai', input_manifest=basis, profile_ref=profile_ref(profile), created_at=sim.ports.clock.now())
        execution.update(role='maintenance', action=deepcopy(action), input_basis=basis)
        activities.assign_execution(engine.runtime, activity['id'], execution)
        for status in ('starting', 'running'):
            execution_lifecycle.transition_execution(execution, status, at=sim.ports.clock.now())
        verdict = {'definition_id': identifier, 'definition_sha256': action['kind_definition_sha256'],
                   'decision': 'approved', 'findings': []}
        engine._apply_kind_definition_check(action, verdict, eid)
        execution['submission_receipt'] = {'state': 'accepted', 'evidence_ref': 'synthetic:kind-check'}
        execution_lifecycle.transition_execution(execution, 'stopping', at=sim.ports.clock.now())
        execution_lifecycle.transition_execution(execution, 'ended', at=sim.ports.clock.now(), outcome='output_accepted')
        with engine.store.writer_lock():
            engine._save()
        engine.head, engine.instance, engine.runtime = engine.store.load()
        self.assertIn(definition['token'], kinds())


class FormalConsumerTests(unittest.TestCase):
    def test_formal_consumer_passes_runtime_and_preapproved_toolchain(self):
        sim = Sim.activated()
        sim.lean.allow('theorem truth : True := True.intro', ['truth'],
                       signatures={'truth': 'truth : True'})
        calls = self.enterContext(recorded_verifier())
        kid = imported(sim, knowledge_candidate())
        only(sim, 'formal_check')
        sim.engine._save()
        with ObservedCalls(capture={'review': lambda arguments: arguments['knowledge_id']},
                           review=sim.engine._start_identity_review) as observed:
            sim.step()  # the owner dispatches the formal check and runs its continuation
        environment = sim.instance['trust_environments'][sim.instance['active_trust_environment']]
        self.assertEqual([arguments['expected_toolchain'] for arguments in calls], [environment['toolchain']])
        record = sim.instance['formal_results'][sim.instance['knowledge'][kid]['formal_result_id']]
        self.assertEqual(record['publication_state'], 'accepted')
        self.assertFalse(assess_use(sim.instance['knowledge'][kid], sim.instance)['valid'])
        self.assertEqual([knowledge_id for _, knowledge_id in observed.calls['review']], [kid])
        [execution] = [row for row in sim.runtime['executions'].values() if row.get('role') == 'formal_check']
        self.assertEqual(execution['status'], 'ended')
        self.assertEqual(execution['outcome'], 'output_accepted')
        self.assertEqual(execution['submission_receipt']['state'], 'accepted')

    def test_review_start_failure_produces_a_storable_wait_after_formal_acceptance(self):
        """The review start fails for real: the instance has no adopted review policy when the formal result is accepted."""
        sim = Sim.activated()
        sim.lean.allow('theorem truth : True := True.intro', ['truth'],
                       signatures={'truth': 'truth : True'})
        kid = imported(sim, knowledge_candidate())
        only(sim, 'formal_check')
        sim.engine.instance.pop('review_policy')
        sim.engine._save()
        action = next(row for row in sim.runtime['queue'] if row['role'] == 'formal_check')
        sim.step()
        [(identifier, waiting)] = [(key, row) for key, row in sim.runtime.get('waiting_actions', {}).items()
                                   if row.get('kind') == 'review_initialization']
        self.assertNotEqual(identifier, action['id'])
        self.assertEqual(waiting['action']['role'], 'identity_review')
        self.assertEqual(waiting['action']['target'], kid)
        self.assertEqual(waiting['next_owner'], 'review_policy')
        self.assertIn('adopted review policy', waiting['reason'])
        execution = sim.runtime['executions'][waiting['execution_id']]
        self.assertEqual((execution['status'], execution['outcome']), ('ended', 'output_accepted'))
        self.assertEqual(sim.instance['formal_results'][sim.instance['knowledge'][kid]['formal_result_id']]['publication_state'], 'accepted')
        # The waiting record the producer wrote was published through the storage contract and reloads unchanged.
        _, instance, runtime = sim.engine.store.load()
        default_state_contract().validate(instance, runtime)
        self.assertEqual(runtime['waiting_actions'][identifier], waiting)

    def test_review_starts_from_split_proposal_without_nested_authorities(self):
        sim = opened_sim()
        kid = theorem_id(sim)
        proposal = cycle_of(sim)['proposal']
        self.assertEqual(proposal['lean_code'], THEOREM['lean_code'])
        self.assertEqual(proposal['statement'], THEOREM['statement'])
        kr.validate_knowledge_records(sim.instance)
        self.assertEqual(sim.instance['knowledge'][kid]['review_cycle_id'], cycle_of(sim)['id'])

    def test_revision_consumer_passes_declared_scope_and_queues_replacement(self):
        """The revised theorem has a dependent record, a relation, goal judgments and a task that use it, as the
        legacy ``knowledge_graph`` did: the dependent and the relation enter by public control, a current goal
        judgment through the receiver of one satisfied goal audit (the goal needs two, so the instance stays
        open) and the task as a preparation produces it."""
        sim = reviewed_sim()
        kid = theorem_id(sim)
        clear_work(sim)
        applied(sim, 'knowledge', config={'operation': 'import', 'candidate': {
            'kind': 'observation', 'title': 'uses k1', 'statement': 'A consequence of k1', 'explanation': 'Uses k1',
            'summary': 'Uses k1', 'lean_code': '', 'declaration_names': [], 'dependencies': [kid]}})
        dependent = theorem_id(sim, 'uses k1')
        applied(sim, 'knowledge', config={'operation': 'import-relation', 'relation': {
            'kind': 'supports', 'source': kid, 'target': dependent, 'evidence': 'k1 supports the consequence'}})
        [relation] = [row['id'] for row in sim.instance['relations'] if row['source'] == kid]
        audit_goal_once(sim.engine, kid)
        goals = [row['id'] for row in sim.instance['goal_judgments'] if kid in row.get('used_sources', [])]
        self.assertEqual(len(goals), 1)
        self.assertNotEqual(sim.instance['goal_status'], 'mathematically_solved')
        task(sim.engine, 'TK-uses-k1', inputs=[kid])
        sim.engine._save()
        changes = {'summary': 'Clarified summary'}
        impact = plan_impact(sim.instance, sim.runtime, revision_roots(sim.instance, kid), [])['computed_impact']
        # The declared scope is not trivial: it reaches every consumer of the revised theorem.
        self.assertTrue({dependent, relation, 'TK-uses-k1', *goals} <= set(impact), impact)
        applied(sim, 'knowledge', config={'operation': 'revise', 'id': kid, 'changes': changes,
                                          'reason': 'clarify', 'declared_impact': impact})
        replacement = next(r for r in sim.instance['knowledge'].values() if r.get('supersedes') == kid)
        self.assertFalse(kr.usable_links(sim.instance, replacement['id']))
        self.assertTrue(any(a.get('target') == replacement['id'] and a['role'] == 'identity_review' for a in sim.runtime['queue']))
        kr.validate_knowledge_records(sim.instance)


class FormalTrustFileTests(unittest.TestCase):
    def test_changed_olean_blocks_even_fake_verifier(self):
        """The active environment is a toolchain of this test's own (registered, configured and moved to by control),
        since the test changes one of its files; the template's shared toolchain is never changed."""
        sim = Sim.activated()
        environment = next_environment(sim, 'changed-olean')
        transition(sim, environment)
        run_machine(sim, 'trust_activate')
        self.assertEqual(sim.instance['active_trust_environment'], environment)
        kid = imported(sim, knowledge_candidate())
        only(sim, 'formal_check')
        sim.engine._save()
        executable = sim.instance['trust_environments'][environment]['toolchain']['executable']
        (Path(executable).parents[1] / 'lib/lean/Init/Prelude.olean').write_text('changed', encoding='utf-8')
        with ObservedCalls(verify=formal.verify_lean, enqueue=sim.engine._enqueue) as observed:
            sim.step()
        self.assertEqual((observed.calls['verify'], sim.lean.checks), ([], []))
        [execution] = [row for row in sim.runtime['executions'].values()
                       if row.get('role') == 'formal_check' and row['action'].get('target') == kid]
        self.assertEqual((execution['status'], execution['outcome']), ('ended', 'execution_incomplete'))
        [waiting] = [row for row in sim.runtime['waiting_actions'].values() if row.get('execution_id') == execution['id']]
        self.assertEqual(waiting['next_owner'], 'trust_governance')
        self.assertIn('olean fingerprint differs', waiting['reason'])
        self.assertEqual(waiting['detail']['environment_id'], environment)
        self.assertEqual(observed.calls['enqueue'], [])

    def test_configured_command_other_than_the_approved_one_holds_the_formal_check(self):
        """The active environment moves to another toolchain while the configured command stays the old Lean
        (조사 K-42): the owner does not start Lean with the configured command, it holds the check."""
        sim = Sim.activated()
        configured = list(sim.instance['config']['lean_command'])
        environment = next_environment(sim, 'unconfigured', configure=False)
        transition(sim, environment)
        run_machine(sim, 'trust_activate')
        approved = sim.instance['trust_environments'][environment]['toolchain']['configured_command']
        self.assertEqual(sim.instance['active_trust_environment'], environment)
        self.assertNotEqual(configured, approved)
        kid = imported(sim, knowledge_candidate())
        only(sim, 'formal_check')
        sim.engine._save()
        action = next(row for row in sim.runtime['queue'] if row['role'] == 'formal_check')
        with ObservedCalls(verify=formal.verify_lean) as observed:
            sim.step()
        self.assertEqual((observed.calls['verify'], sim.lean.checks), ([], []))
        waiting = sim.runtime['waiting_actions'][action['id']]
        self.assertEqual((waiting['kind'], waiting['next_owner']), ('formal_authority', 'trust_governance'))
        self.assertEqual(waiting['reason'], 'profile command differs from the approved trust environment')
        self.assertFalse([row for row in sim.runtime['executions'].values()
                          if row.get('role') == 'formal_check' and row['action'].get('target') == kid])


if __name__ == '__main__':
    unittest.main()
