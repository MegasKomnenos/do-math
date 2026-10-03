"""Changes to approved academic requirements after the mathematical solution, on the real engine
(``academic_engine`` and the charter decision; layer 2), moved from ``test_academic_engine``.

The legacy tests started from a synthetic active state: ``goal_status`` set
directly with no goal judgments and a solution basis from
``patch.object(engine, '_solution_basis', ...)``. Here the goal is solved for
real: each test restores ``support.academic_scenes.theorem_sim`` (a reviewed
theorem), approves its requirements by the user's charter decision through the
public control, and lets the configured goal auditors solve the goal on the
theorem, whose receiver generates the academic tasks.

Each requirement-change scenario runs through both the public control and the
governance rule. Both refresh owner readiness before checking academic follow-up.
The mathematical premise hash preserves the solved judgments across an academic-only
charter change; the requirements still carry their own edition binding.

Other controls go through the public control path (``support.engine_lifecycle.applied``,
which fails on a rejection, preserved rule K-35).
"""
from copy import deepcopy
import unittest

from do_math.governance import governance_view, mathematical_goal_basis
from support.purpose_answers import requirement
from support.state_builders import charter_change
from support.academic_inputs import complete_academic_task
from support.academic_scenes import decide_requirements, solve_with, theorem_sim
from support.engine_lifecycle import applied

REVISED = ['draft account', 'archival supplement']


def setUpModule():
    theorem_sim()


def academic_tasks(engine):
    return [task for task in engine.runtime['tasks'].values() if task.get('academic_requirement_id') == 'writeup']


def publish_followup(engine):
    """Run the academic follow-up, publish it and load the published state, as the next owner pass reads it."""
    engine._ensure_academic_followup()
    engine._save()
    engine.head, engine.instance, engine.runtime = engine.store.load()


def by_public_control(sim, requirements):
    """The user's charter decision replacing the academic requirements, sent and applied as a public control."""
    applied(sim, 'decision', config={'change': charter_change(sim.engine, academic_requirements=requirements)})


def by_governance_rule(sim, requirements):
    """The same decision applied by the governance rule alone, without the engine's control step."""
    decide_requirements(sim.engine, requirements)


def solved(test, *, completed=False):
    """A solved instance whose approved requirement is ``writeup`` (and, completed, ``remaining``).

    ``completed`` completes the ``writeup`` task through the real assessment
    rules (``state_fixtures.complete_academic_task``); ``remaining`` keeps the
    instance open for requirement changes.
    """
    sim = theorem_sim()
    requirements = [requirement(['draft account'])]
    if completed:
        requirements.append({**requirement(['Independent remaining account']), 'id': 'remaining'})
    solve_with(sim, requirements)
    engine = sim.engine
    if completed:
        complete_academic_task(engine, academic_tasks(engine)[0], engine._solution_basis())
        test.assertEqual(engine.runtime['status'], 'ready')
        test.assertTrue(academic_tasks(engine)[0]['assessment']['current'])
    return sim


def change(test, sim, requirements, how):
    """Change the approved requirements ``how``; the goal stays solved (the governance rule's academic-only case)."""
    how(sim, requirements)
    sim.engine._refresh_readiness()
    test.assertEqual(sim.engine.instance['goal_status'], 'mathematically_solved')
    publish_followup(sim.engine)


def assert_same_requirement_id_supersedes_old_contract(test, how):
    sim = solved(test)
    engine = sim.engine
    old = academic_tasks(engine)[0]
    old_basis = deepcopy(old['solution_basis'])
    old_hash = old['requirements_sha256']
    change(test, sim, [requirement(REVISED)], how)
    tasks = academic_tasks(engine)
    test.assertEqual(len(tasks), 2)
    superseded = next(task for task in tasks if task['id'] == old['id'])
    current = next(task for task in tasks if task['id'] != old['id'])
    test.assertEqual(superseded['status'], 'closed')
    test.assertEqual(superseded['scope_disposition']['kind'], 'superseded_requirements')
    test.assertEqual(current['academic_requirement_id'], 'writeup')
    test.assertEqual([row['claim'] for row in current['completion_obligations']], REVISED)
    test.assertEqual(current['solution_basis'], old_basis)
    test.assertNotEqual(current['requirements_sha256'], old_hash)
    test.assertNotEqual(engine.runtime['status'], 'completed')


def assert_completed_task_is_preserved(test, how):
    sim = solved(test, completed=True)
    engine = sim.engine
    old = academic_tasks(engine)[0]
    test.assertEqual(old['status'], 'completed')
    change(test, sim, [requirement(REVISED)], how)
    tasks = academic_tasks(engine)
    preserved = next(task for task in tasks if task['id'] == old['id'])
    current = next(task for task in tasks if task['id'] != old['id'])
    test.assertEqual(preserved['status'], 'completed')
    test.assertNotIn('scope_disposition', preserved)
    test.assertFalse(preserved['assessment']['current'])
    test.assertTrue(preserved['assessment']['invalidated_reason'].strip())
    test.assertEqual([row['claim'] for row in current['completion_obligations']], REVISED)
    test.assertNotEqual(engine.runtime['status'], 'completed')


def assert_removal_retires_old_tasks_and_completes(test, how):
    sim = solved(test, completed=True)
    engine = sim.engine
    before = deepcopy(engine.runtime['tasks'])
    test.assertTrue(any(task['status'] == 'completed' for task in before.values()))
    test.assertTrue(any(task['status'] != 'completed' for task in before.values()))
    change(test, sim, [], how)
    test.assertEqual(set(engine.runtime['tasks']), set(before))
    for tid, previous in before.items():
        current = engine.runtime['tasks'][tid]
        test.assertEqual(current['results'], previous['results'])
        if previous['status'] == 'completed':
            test.assertEqual(current['status'], 'completed')
            test.assertFalse(current['assessment']['current'])
        else:
            test.assertEqual(current['status'], 'closed')
            test.assertEqual(current['scope_disposition']['kind'], 'superseded_requirements')
    test.assertEqual(engine.instance['goal_status'], 'mathematically_solved')
    test.assertEqual(engine._academic_status()['status'], 'not_applicable')
    test.assertEqual(engine.runtime['status'], 'completed')
    test.assertEqual(engine.runtime['queue'], [])


def assert_removal_preserves_unresolved_external_rejection(test, how):
    sim = solved(test)
    engine = sim.engine
    applied(sim, 'decision', config={'change': {'kind': 'academic_rejection', 'actor': 'referee',
                                                'text': 'The preserved solution still needs a response.'}})
    rejection = deepcopy(engine.runtime['external_rejections'][-1])
    change(test, sim, [], how)
    test.assertEqual(engine._academic_status()['status'], 'externally_rejected')
    test.assertNotEqual(engine.runtime['status'], 'completed')
    test.assertEqual(engine.runtime['external_rejections'][-1], rejection)
    test.assertTrue(all(task['status'] == 'closed' for task in engine.runtime['tasks'].values()))
    test.assertFalse(any(action.get('target') in engine.runtime['tasks'] for action in engine.runtime['queue']))


class AcademicRequirementChangeTests(unittest.TestCase):
    """The requirement change through the public control, as the legacy tests sent it."""

    def test_changed_same_requirement_id_supersedes_old_contract_and_creates_new_criteria(self):
        assert_same_requirement_id_supersedes_old_contract(self, by_public_control)

    def test_changed_requirements_preserve_completed_academic_task(self):
        assert_completed_task_is_preserved(self, by_public_control)

    def test_removing_all_requirements_retires_old_tasks_and_completes_followup(self):
        assert_removal_retires_old_tasks_and_completes(self, by_public_control)

    def test_removing_all_requirements_preserves_unresolved_external_rejection(self):
        assert_removal_preserves_unresolved_external_rejection(self, by_public_control)

    def test_completed_instance_rejects_requirement_changes(self):
        from do_math.task_scope import apply_task_assessments
        from support.provider_probes import ObservedCalls
        sim = solved(self)
        engine = sim.engine
        with ObservedCalls(assessment=apply_task_assessments) as observed:
            complete_academic_task(engine, academic_tasks(engine)[0], engine._solution_basis())
        self.assertIs(observed.captured('assessment')[0]['clock'], engine.ports.clock)
        self.assertEqual(engine.runtime['status'], 'completed')
        before = deepcopy(engine.runtime['tasks'])
        request = sim.control('decision', text='Change the approved academic requirements', config={
            'change': charter_change(engine, academic_requirements=[requirement(['New requirement'])])})
        engine.process_controls()
        rejected = [row for row in engine.runtime['history'] if row.get('kind') == 'rejected_user_control'
                    and row.get('request', {}).get('id') == request['request_id']]
        self.assertEqual(len(rejected), 1)
        self.assertEqual(rejected[0]['reason'], 'closed/completed instance cannot apply lifecycle controls')
        self.assertEqual(engine.runtime['status'], 'completed')
        self.assertEqual(engine.store.load()[2]['tasks'], before)


class RequirementChangeByGovernanceRuleTests(unittest.TestCase):
    """The same scenarios with the change applied by the governance rule alone (added tests, see the module docstring).

    The direct-rule cases also refresh readiness, checking the same currentness rule as the owner.
    """

    def test_changed_same_requirement_id_by_the_governance_rule_supersedes_old_contract(self):
        assert_same_requirement_id_supersedes_old_contract(self, by_governance_rule)

    def test_changed_requirements_by_the_governance_rule_preserve_completed_academic_task(self):
        assert_completed_task_is_preserved(self, by_governance_rule)

    def test_removing_all_requirements_by_the_governance_rule_retires_old_tasks_and_completes_followup(self):
        assert_removal_retires_old_tasks_and_completes(self, by_governance_rule)

    def test_removing_all_requirements_by_the_governance_rule_preserves_unresolved_external_rejection(self):
        assert_removal_preserves_unresolved_external_rejection(self, by_governance_rule)


class AcademicOnlyCharterControlTests(unittest.TestCase):
    def test_a_mathematical_goal_change_invalidates_the_solved_judgments(self):
        sim = theorem_sim()
        solve_with(sim, [requirement(['draft account'])])
        engine = sim.engine
        previous_basis = engine._solution_basis()
        old_judgments = deepcopy(engine.instance['goal_judgments'])
        applied(sim, 'decision', config={'change': charter_change(engine,
            goal=governance_view(engine.instance)['goal'] + ' with a changed mathematical target')})
        engine._refresh_readiness()
        self.assertEqual(engine.instance['goal_status'], 'unsolved')
        self.assertNotEqual(engine._solution_basis(), previous_basis)
        self.assertEqual(len(engine.instance['goal_judgments']), len(old_judgments))
        self.assertTrue(all(row['current'] is False for row in engine.instance['goal_judgments']))
        sim.restart()
        sim.engine._refresh_readiness()
        self.assertEqual(sim.engine.instance['goal_status'], 'unsolved')
        self.assertTrue(all(row['current'] is False for row in sim.engine.instance['goal_judgments']))

    def test_an_academic_only_charter_control_keeps_the_solved_goal_and_its_basis(self):
        """The user's charter decision changing only the academic requirements, through the public control, after the
        solution: the governance rule keeps the goal solved and the solution basis excludes the requirements, so the
        follow-up replaces the requirement's task on the same mathematical basis."""
        sim = theorem_sim()
        solve_with(sim, [requirement(['draft account'])])
        engine = sim.engine
        basis = engine._solution_basis()
        judgments = deepcopy(engine.instance['goal_judgments'])
        charter = governance_view(engine.instance)['charter']
        self.assertTrue(all(row['goal_basis_sha256'] == mathematical_goal_basis(charter) for row in judgments))
        old, = academic_tasks(engine)
        by_public_control(sim, [requirement(REVISED)])
        self.assertEqual(engine.instance['goal_status'], 'mathematically_solved')
        self.assertGreater(governance_view(engine.instance)['charter']['revision'], charter['revision'])
        self.assertEqual(engine.instance['goal_judgments'], judgments)
        self.assertEqual(engine._solution_basis(), basis)
        publish_followup(engine)
        current, = [task for task in academic_tasks(engine) if task['id'] != old['id']]
        self.assertEqual(current['solution_basis'], basis)
        sim.restart()
        sim.engine._refresh_readiness()
        self.assertEqual(sim.engine.instance['goal_status'], 'mathematically_solved')
        self.assertEqual(sim.engine.instance['goal_judgments'], judgments)
        self.assertEqual(sim.engine._solution_basis(), basis)


class AcademicTaskPersistenceTests(unittest.TestCase):
    def test_user_requirement_task_keeps_charter_provenance_without_invented_execution(self):
        sim = theorem_sim()
        solve_with(sim, [{**requirement(['Explain the supplied result']), 'id': '원고 검토'}])
        engine = sim.engine
        task = next(t for t in engine.runtime['tasks'].values() if t.get('academic_requirement_id'))
        charter = governance_view(engine.instance)['charter']
        self.assertNotIn('producer_execution', task)
        self.assertEqual(task['basis_refs'], [charter['id'], charter['approval_ref']])
        self.assertEqual(task['academic_requirement_id'], '원고 검토')
        self.assertEqual(task['requirements_sha256'], governance_view(engine.instance)['academic_requirements']['sha256'])
        preparation = next(a for a in engine.runtime['queue'] if task['id'] in a.get('observation_rule_targets', {}))
        self.assertEqual(preparation['role'], 'research_preparation')
        self.assertFalse(any(a['role'] == 'task_contract_review' and a.get('target') == task['id']
                             for a in engine.runtime['queue']))
        _, _, saved = engine.store.load()
        self.assertEqual(saved['tasks'][task['id']], task)

    def test_absent_academic_evidence_resolves_to_none(self):
        engine = theorem_sim().engine
        self.assertIsNone(engine._academic_evidence('runtime/artifacts/BA-absent/evidence.json'))


if __name__ == '__main__':
    unittest.main()
