"""The engine's side of planning: applying plans and task assessments, readiness refresh and its followups,
and the conditions a plan evaluates (``lifecycle_engine._refresh_readiness``, ``decision_engine._apply_task_plan``,
``dispatch_engine._select_model``, ``core_engine._apply``/``_apply_extensions``/``_evaluation_context``; layer 2),
moved from ``test_planning_engine``.

The legacy tests ran the engine as the in-memory ``FakeEngine``, as an engine
built without its constructor with an autospec store (``context_engine``) or
with its store refused and methods replaced (``routing_engine``: output
questions, revision binding, queue plan, academic resolutions, evaluation
context); one patched the host's provider adapter. Here every test runs the real
``ResearchEngine`` of a restored Sim on the port fakes and its real
``ResearchRepository``, so the methods the legacy doubles replaced run as they
are. Start states come from the public activation and the product's own
producers (``support.planning_owner``); where a legacy test read a method's
call, the call is observed (``sys.monitoring``) instead of replaced.
"""
from copy import deepcopy
import hashlib
import unittest

from do_math import execution_profiles, model_policy, planning
from do_math.initialization import governance_working_view
from do_math.repository import ResearchRepository
from support.model import amend
from support.engine_lifecycle import ObservedCalls, _ended_execution, applied, approve, artifact_reader_code, \
    clear_work, code_of, task
from support.planning_owner import MISSING_SOURCE, arrive, owner_sim, reassessment_sim, warm_owner, warm_reassessment, \
    work_profile
from support.sim import Sim, warm_template


def setUpModule():
    warm_template()
    warm_owner()
    warm_reassessment()


def unapproved(engine, task_id, assessment, tier):
    """A task a returned preparation produced, assessed ``assessment``, allowing only the adopted ``tier`` work profile."""
    row = task(engine, task_id, approved=False)
    row['model_assessment'] = dict(assessment)
    row['profile_refs'] = [execution_profiles.profile_ref(work_profile(engine.instance, tier))]
    return row


class WorkProfileAdmissionTests(unittest.TestCase):
    def setUp(self):
        self.sim = Sim.activated()
        clear_work(self.sim)
        self.engine = self.sim.engine

    def test_policy_change_reprepares_an_unstarted_incompatible_contract(self):
        engine = self.engine
        t = unapproved(engine, 'T1', {'difficulty': 'low', 'importance': 'low', 'reason': 'local'}, 'low')
        approve(engine, t)
        engine.instance['config']['role_tiers']['research_work'] = 'high'
        engine._refresh_readiness()
        self.assertEqual(engine._task_readiness[t['id']]['state'], 'not_ready')
        self.assertTrue(any(a['role'] == 'research_preparation' and a.get('target') == t['id']
                            for a in engine.runtime['queue']))
        self.assertFalse(any(a['role'] == 'task_contract_review' and a.get('target') == t['id']
                             for a in engine.runtime['queue']))

    def test_reviewed_contract_cannot_be_ready_with_an_inadequate_allowed_profile(self):
        engine = self.engine
        t = unapproved(engine, 'T1', {'difficulty': 'low', 'importance': 'high', 'reason': 'goal-critical'}, 'low')
        approve(engine, t)
        result = planning.task_ready(t, governance_working_view(engine.instance), engine.runtime, evaluation_context=engine._evaluation_context())
        self.assertEqual(result['state'], 'not_ready')
        self.assertIn('work profile requirement', result['errors'][0])
        t['profile_refs'] = [execution_profiles.profile_ref(work_profile(engine.instance, 'high'))]
        approve(engine, t)
        self.assertEqual(planning.task_ready(t, governance_working_view(engine.instance), engine.runtime, evaluation_context=engine._evaluation_context())['state'], 'ready')
        self.assertEqual(model_policy.work_profile_selection(engine.instance['config'], t,
            engine.instance)['profile_ref'], t['profile_refs'][0])


class PlanningConnections(unittest.TestCase):
    def test_snapshot_report_supplies_clock_to_task_authority(self):
        from do_math.reporting import snapshot_report
        sim = owner_sim()
        engine = sim.engine
        before = deepcopy((engine.instance, engine.runtime))
        report = snapshot_report(sim.repository, sim.instance_id, snapshot=engine.head,
                                 backend=engine.ports.git_backend, clock=engine.ports.clock)
        row = next(row for row in report['tasks'] if row['id'] == 'TK-1')
        self.assertEqual(row['readiness']['state'], 'ready')
        self.assertIsNone(report['research_observed_at'])
        self.assertEqual((engine.instance, engine.runtime), before)

    def test_plan_assessment_reaches_assignment_without_changing_contract(self):
        from do_math.execution_lifecycle import create_execution, transition_execution
        from do_math.session_slots import SessionSlots
        from support.record_builders import task_disposition
        sim = owner_sim()
        engine = sim.engine
        config = engine.instance['config']
        config['session_limits'] = deepcopy(model_policy.LIMITS)
        config['session_limits']['work'][config['tier_models']['high']] = 0
        config['role_tiers']['research_work'] = 'low'
        engine.instance.update(execution_profiles.build_profiles(config, host=sim.ports.host))
        t = engine.runtime['tasks']['TK-1']
        t['profile_refs'] = deepcopy(engine.instance['role_profile_refs']['research_work'])
        t['model_assessment'] = {'difficulty': 'low', 'importance': 'low', 'reason': 'Initial bounded work'}
        approve(engine, t)
        before = deepcopy(t)
        high = {'difficulty': 'high', 'importance': 'high', 'reason': 'New plan needs stronger reasoning'}
        _ended_execution(engine, 'EX-plan', 'research_plan')
        engine.runtime['executions']['EX-plan']['model_decisions'] = {t['id']: high}
        engine._apply_task_plan({'dispositions': [task_disposition(t['id'])], 'task_assessments': []},
            'EX-plan', deepcopy(engine.runtime['tasks']), [t['id']], evaluation_context=engine._evaluation_context())
        action = next(a for a in engine.runtime['queue'] if a['role'] == 'research_work')
        selected = engine._select_model(action)
        self.assertEqual(selected['tier'], 'high')
        self.assertEqual(selected['model'], config['tier_models']['high'])
        self.assertEqual(action['model_assessment'], high)
        self.assertEqual(planning.contract_hash(engine.runtime['tasks'][t['id']]), planning.contract_hash(before))
        self.assertEqual(engine.runtime['tasks'][t['id']]['reviews'], before['reviews'])
        high['reason'] = 'Mutation of the source must not change the request'
        self.assertNotEqual(action['model_assessment'], high)
        profile = execution_profiles.resolve_profile(engine.instance['execution_profiles'], selected['profile_ref'])
        execution = create_execution(execution_id='EX-no-slot', owner_activity_id='AY-work', actor_kind='ai',
            input_manifest={}, profile_ref=selected['profile_ref'], created_at='2026-09-23T00:00:00+00:00')
        transition_execution(execution, 'starting', at='2026-09-23T00:00:00+00:00')
        slots = SessionSlots(engine.runtime, engine.instance, clock=sim.ports.clock, host_id=sim.host_id, jobs=sim.ports.jobs)
        self.assertFalse(slots.acquire('EX-no-slot', profile=profile, execution=execution))
        self.assertEqual(engine._select_model(action)['tier'], 'high')

    def test_readiness_refresh_requests_reassessment_while_other_work_remains(self):
        from do_math import task_contracts
        sim = reassessment_sim()
        engine = sim.engine
        arrive(sim, MISSING_SOURCE)
        self.assertTrue(engine.runtime['tasks']['TK-1']['assessment']['current'])
        original_results = deepcopy(engine.runtime['tasks']['TK-1']['results'])
        engine._refresh_readiness()
        self.assertFalse(engine.runtime['tasks']['TK-1']['assessment']['current'])
        plans = [a for a in engine.runtime['queue'] if a['role'] == 'research_plan']
        self.assertEqual(len(plans), 1)
        self.assertIn('TK-1', plans[0]['reason'])
        self.assertEqual(task_contracts.returned_task_ids(engine.runtime['tasks']), ['TK-1'])
        engine._refresh_readiness()
        self.assertEqual(len([a for a in engine.runtime['queue'] if a['role'] == 'research_plan']), 1)
        self.assertEqual(engine.runtime['tasks']['TK-1']['results'], original_results)

    def test_live_work_defers_reassessment_until_end_and_unrelated_changes_do_not_reopen(self):
        from do_math.execution_lifecycle import transition_execution
        sim = reassessment_sim()
        engine = sim.engine
        arrive(sim, 'other.txt')
        engine._refresh_readiness()
        self.assertTrue(engine.runtime['tasks']['TK-1']['assessment']['current'])
        # Research work on TK-1 starts: the engine registers its execution, published before the next control.
        engine._register_execution({'id': 'AC-live', 'role': 'research_work', 'target': 'TK-1'},
                                   {'id': 'EX-live', 'role': 'research_work', 'status': 'running'})
        engine._save()
        source = arrive(sim, MISSING_SOURCE)
        # The public source controls leave source events, which the first refresh already queued as one plan to
        # reconsider them. While the work runs, the refresh only joins the new source's event to that plan: no
        # reassessment plan, no reassessment reason (the whole queue is compared).
        imported = [e['id'] for e in engine.runtime['events']
                    if e['kind'] == 'source_imported' and e['target'] == source['id']]
        expected = deepcopy(engine.runtime['queue'])
        plan, = [row for row in expected if row['role'] == 'research_plan']
        plan['event_refs'] = [*plan['event_refs'], *imported]
        engine._refresh_readiness()
        self.assertEqual(engine.runtime['queue'], expected)
        self.assertTrue(engine.runtime['tasks']['TK-1']['assessment']['current'])
        live = engine.runtime['executions']['EX-live']
        at = engine._lifecycle_now().isoformat()
        transition_execution(live, 'stopping', at=at)
        transition_execution(live, 'ended', at=at, outcome='execution_incomplete')
        engine._refresh_readiness()
        self.assertFalse(engine.runtime['tasks']['TK-1']['assessment']['current'])
        plans = [a for a in engine.runtime['queue'] if a['role'] == 'research_plan']
        self.assertEqual(len(plans), 1)
        self.assertIn('TK-1', plans[0]['reason'])

    def test_terminal_history_remains_closed_when_assessment_evidence_changes(self):
        sim = reassessment_sim()
        engine = sim.engine
        arrive(sim, MISSING_SOURCE)
        t = engine.runtime['tasks']['TK-1']
        # Synthetic, as in the legacy test: a closed task still holding a current incomplete assessment.
        t['status'] = 'closed'
        original = deepcopy(t['results'])
        engine._refresh_readiness()
        self.assertEqual(engine.runtime['tasks']['TK-1']['status'], 'closed')
        self.assertEqual(engine.runtime['tasks']['TK-1']['results'], original)
        self.assertFalse(engine.runtime['tasks']['TK-1']['assessment']['current'])
        followups = [e for e in engine.runtime['events'] if e['kind'] == 'task_assessment_invalidated']
        self.assertEqual(len(followups), 1)
        self.assertTrue(any(followups[0]['id'] in a.get('event_refs', []) for a in engine.runtime['queue']))


class KindSemanticConnections(unittest.TestCase):
    def test_proposed_kind_is_checked_by_a_separate_execution_before_activation(self):
        """About 2.4 s, over the 2 s Sim budget: the owner runs the check as one maintenance call through the worker."""
        sim = Sim.activated()
        clear_work(sim)
        engine = sim.engine
        definition = {'family': 'knowledge', 'token': 'method_note', 'meaning': 'A nonmathematical method observation',
                      'constraints': {'mathematical_claim': False}}
        _ended_execution(engine, 'EX-author', 'research_work')
        engine.runtime['executions']['EX-author']['extensions'] = {'kind_definitions': [definition]}
        engine._apply_extensions({'role': 'research_work'}, 'EX-author')
        definition = next(row for row in engine.instance['kind_definitions'].values() if row['token'] == 'method_note')
        checks = [a for a in engine.runtime['queue'] if a.get('kind_definition_id') == definition['id']]
        self.assertEqual(len(checks), 1)
        self.assertEqual(definition['status'], 'candidate')
        action = checks[0]
        check = {'definition_id': definition['id'], 'definition_sha256': action['kind_definition_sha256'],
                 'decision': 'approved', 'findings': []}
        output = {'summary': 'Independent semantic comparison', 'used_sources': [], 'questions': [],
                  'report': 'Meaning and constraints agree', 'remaining_work': [], 'kind_definition_check': check}
        with self.assertRaisesRegex(ValueError, 'independent|author'):
            engine._apply(action, output, 'EX-author')
        engine._save()
        # The owner runs the queued check as a separate maintenance execution; the model double approves.
        sim.model.on('maintenance', kind_definition_id=definition['id']).reply(
            amend(report='Meaning and constraints agree', kind_definition_check=dict(check)))
        sim.run_until(lambda s: s.instance['kind_definitions'][definition['id']]['status'] == 'active', max_steps=6)
        engine = sim.engine
        checker, = [row for row in engine.runtime['executions'].values()
                    if row.get('action', {}).get('kind_definition_id') == definition['id']]
        self.assertEqual((checker['role'], checker['input_basis']['kind_definition']),
                         ('maintenance', {'id': definition['id'], 'sha256': action['kind_definition_sha256']}))
        checked = engine.instance['kind_definitions'][definition['id']]
        self.assertEqual(checked['status'], 'active')
        self.assertEqual(checked['checked_by'], checker['id'])
        self.assertNotEqual(checked['checked_by'], 'EX-author')
        self.assertEqual(checked['check']['decision'], 'approved')
        self.assertEqual(engine.runtime['pending_kind_checks'], [])


class EvaluationConnections(unittest.TestCase):
    VALUES = {'tool_review_window_seconds': 20, 'self_check_response_window_seconds': 30,
              'import_rework_limit': 3, 'selection_failure_limit': 3,
              'exhaustion_empty_limit': 3, 'proposal_version_limit': 3, 'contract_revision_limit': 3}

    def test_declared_observation_and_repetition_values_can_be_adopted(self):
        from support.entry import entry
        _entry = entry()
        from do_math.configuration import validate_config
        validate_config(dict(self.VALUES), host_id=_entry.host_id)
        # The legacy test only validated the values; the adoption its name states is the public configure control.
        sim = Sim.activated()
        applied(sim, 'configure', config=dict(self.VALUES))
        self.assertEqual({key: sim.instance['config'][key] for key in self.VALUES}, self.VALUES)

    def test_artifact_condition_reads_exact_snapshot_and_validates_bytes(self):
        sim = Sim.activated()
        engine = sim.engine
        cases = (('ready', b'{"proof": true, "reader": "planning engine exact snapshot"}', 'ready'),
                 ('broken', b'{"valid":true, "reader": "planning engine exact snapshot"', 'evaluation_error'))
        for bundle, data, state in cases:
            with self.subTest(state=state):
                # Sealed bundles are immutable; bytes no other test seals, so the verdict caches cannot answer.
                path = f'runtime/artifacts/BA-planning-engine-{bundle}/evidence.json'
                engine._save({path: data})
                snapshot = engine.head
                # A later publication moves the head: the reference names the earlier snapshot.
                engine._save({f'runtime/artifacts/BA-planning-engine-later-{bundle}/other.json': b'{"later": true}'})
                self.assertNotEqual(engine.head, snapshot)
                ref = {'path': path, 'snapshot': snapshot, 'sha256': hashlib.sha256(data).hexdigest()}
                # The store boundary the legacy autospec stood at: its read must name the referenced snapshot.
                with ObservedCalls(read=artifact_reader_code(), store=code_of(ResearchRepository.read)) as observed:
                    result = planning.evaluate_condition({'op': 'artifact_valid', 'artifact_ref': ref},
                        engine.instance, engine.runtime, evaluation_context=engine._evaluation_context())
                self.assertEqual(result['state'], state)
                self.assertEqual([(call['path'], call['commit']) for call in observed.calls['read']], [(path, snapshot)])
                self.assertEqual([(call['path'], call['snapshot']) for call in observed.calls['store']], [(path, snapshot)])


class DuplicateRevisionConnections(unittest.TestCase):
    def test_same_task_replacements_are_rejected_before_any_receiver_mutation(self):
        from do_math import revisions
        from support.role_answers import candidate
        sim = owner_sim()
        engine = sim.engine
        t = engine.runtime['tasks']['TK-1']
        action = {'id': 'AC-revise', 'role': 'research_preparation',
                  'revision_targets': revisions.capture_targets(engine.instance, engine.runtime, [t['id']])}
        _ended_execution(engine, 'EX-revise', 'research_preparation')
        engine.runtime['executions']['EX-revise'].update(extensions={}, input_snapshot=engine.head)
        proposals = [candidate(title, revises=t['id']) for title in ('First', 'Second')]
        for proposal in proposals:
            proposal['profile_refs'] = deepcopy(t['profile_refs'])
            proposal['authority_refs'] = list(t['authority_refs'])
            proposal['completion_obligations'][0]['claim'] = proposal['title']
        output = {'summary': 'Conflicting replacements', 'questions': [],
                  'used_sources': [], 'candidates': proposals}
        before = deepcopy((engine.instance, engine.runtime))
        with ObservedCalls(questions=code_of(engine._record_output_questions)) as observed:
            with self.assertRaisesRegex(ValueError, 'one replacement candidate'):
                engine._apply(action, output, 'EX-revise')
        self.assertEqual((engine.instance, engine.runtime), before)
        self.assertEqual(len(observed.calls['questions']), 1)


if __name__ == '__main__':
    unittest.main()
