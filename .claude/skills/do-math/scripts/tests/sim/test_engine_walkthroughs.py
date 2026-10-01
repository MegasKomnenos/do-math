"""Design walkthroughs (통합-설계.md 17.3) and priority vectors on the Sim's real engine: cross-owner domain paths.

Each walkthrough replays public domain functions and the engine's own response
receiver (``_apply``) on the restored public activation
(``support.engine_walkthroughs``). Model, reviewer and compiler verdicts are
declared fixtures; the unexercised ends are the same as the legacy trace's:
live provider and host, semantic truth of responses, and research efficacy.
The legacy walkthroughs ran on ``engine_fixtures.evidence_engine``, an engine
built without ``__init__`` over an input-snapshot store double; there a
receiver's issued input was an autospec (``_issued_input``), here it is archived
below the execution's input bundle and read back by the engine.
"""
from copy import deepcopy
import json
import unittest

from jsonschema import Draft202012Validator

from do_math import activities, contracts, execution_lifecycle, knowledge, knowledge_io, knowledge_records as kr, planning, questions
from do_math.context_store import fit_context, read_source
from do_math.governance import governance_view
from do_math.task_contracts import validate_task_contract
from do_math.task_scope import apply_task_dispositions
from support.record_builders import evidence_task
from support.engine_context import issue
from support.engine_lifecycle import _ended_execution, research_grant, task
from support.engine_walkthroughs import (accept_knowledge, apply_plan, audit_goal, evidence_sim, plan_output,
                                         truth_candidate)
from support.sim import warm_template

setUpModule = warm_template


def disposition(tid, kind='selected'):
    row = {'task_id': tid, 'kind': kind, 'reason': 'Compare scope and current evidence',
           'next_owner': 'research_work' if kind == 'selected' else 'research_plan'}
    if kind == 'selected':
        row['expected_research_change'] = 'resolve the bounded case'
    else:
        row['revisit'] = {'event_refs': ['EV-new-evidence']}
    return row


def reviewed_task(engine, identifier='TK-1'):
    """A planned task with an approving contract review, under the adopted research grant (``engine_lifecycle.task``)."""
    return task(engine, identifier)


class DesignWalkthroughs(unittest.TestCase):
    def test_w01_existing_knowledge_solves_without_new_research_task(self):
        requirement = {'id': 'AR-reproduce', 'scope': 'Reproduce the accepted result', 'assessor': 'research_plan',
                       'criteria': ['Reproduction evidence is preserved'], 'required_inputs': [], 'external_effects': []}
        e = evidence_sim(academic_requirements=[requirement]).engine
        kid, _ = accept_knowledge(e)
        self.assertTrue(knowledge.assess_use(e.instance['knowledge'][kid], e.instance)['valid'])
        audit_goal(e, kid)
        self.assertEqual(e.instance['goal_status'], 'mathematically_solved')
        self.assertEqual(len(e.runtime['tasks']), 1)
        followup = next(iter(e.runtime['tasks'].values()))
        self.assertEqual(followup['academic_requirement_id'], requirement['id'])
        self.assertEqual(followup['solution_basis'], e._solution_basis())
        self.assertEqual(followup['status'], 'planned')
        self.assertTrue(any(followup['id'] in a.get('observation_rule_targets', {}) for a in e.runtime['queue']))
        self.assertFalse(any(a['role'] == 'task_contract_review' and a.get('target') == followup['id']
                             for a in e.runtime['queue']))
        self.assertFalse(any(a['role'] == 'research_work' for a in e.runtime['queue']))
        self.assertIsNotNone(e._solution_basis())
        # The generated followup must be consumable by the installed task contract.
        validate_task_contract(followup)

    def test_w02_periodic_reconsideration_prepares_while_work_is_live(self):
        sim = evidence_sim()
        e = sim.engine
        old = reviewed_task(e, 'TK-running')
        now = e.ports.clock.now()
        e.runtime.update(status='active', cycles=0, next_research_reconsider_at=now)
        running = e._register_execution({'id': 'AC-running', 'role': 'research_work', 'target': old['id']},
                                        {'id': 'EX-running', 'role': 'research_work', 'status': 'running',
                                         'input_snapshot': e.head, 'input_manifest': []})
        planning.record_due_events(e.instance, e.runtime, now)
        state = planning.schedule_reconsideration(e.instance, e.runtime, now=now, clock=sim.ports.clock)
        self.assertFalse(state['exhausted'])
        preparation = next(a for a in e.runtime['queue'] if a['role'] == 'research_preparation')
        self.assertTrue(preparation['event_refs'])
        template = evidence_task('TK-different')
        # A model emits the wire candidate, never receiver-owned task fields.
        proposal = {name: deepcopy(template[name]) for name in (
            'question', 'scope', 'expected', 'progress_criteria', 'completion_obligations',
            'inputs', 'reuse', 'dependencies', 'profile_refs', 'authority_refs', 'basis_refs')}
        # This case tests periodic scheduling, with no formal checker premise.
        proposal.update(title='Different approach', revises_task_id=None, work_class='nonformal',
                        authority_refs=[research_grant(e)])
        proposal['profile_refs'] = deepcopy(e.instance['role_profile_refs']['research_work'])  # the adopted editions
        self.assertEqual(list(Draft202012Validator(contracts.TASK_CANDIDATE).iter_errors(proposal)), [])
        _ended_execution(e, 'EX-prep', 'research_preparation')
        prep = e.runtime['executions']['EX-prep']
        prep.update(input_snapshot=e.head, extensions={})
        # The preparation's issued input names what its task inputs may cite; this proposal cites none.
        issue(e, prep, {'available_input_refs': [], 'supplied_record_ids': []}, 'BA-EX-prep')
        e._apply(preparation, {'candidates': [proposal], 'summary': 'Different lens', 'questions': []}, 'EX-prep')
        created = next(t for t in e.runtime['tasks'].values() if t['id'] != old['id'])
        self.assertEqual(created['status'], 'planned')
        self.assertEqual(running['status'], 'running')
        self.assertTrue(any(a['role'] == 'task_contract_review' and a['target'] == created['id'] for a in e.runtime['queue']))
        self.assertFalse(any(a['role'] == 'research_work' and a['target'] == created['id'] for a in e.runtime['queue']))

    def test_w03_conditional_theorem_does_not_discharge_missing_hypothesis(self):
        e = evidence_sim().engine
        hypothesis = task(e, 'TK-hypothesis', approved=False)
        hypothesis['question'] = 'Establish H'
        e._save()
        snapshot = e.head  # what the next plan reads; the knowledge below is accepted in memory only
        kid, _ = accept_knowledge(e, truth_candidate('H implies P', 'theorem truth (H P : Prop) (h : H → P) : H → P := h'))
        basis_before = deepcopy(e.instance.get('goal_assessment_basis', 'absent'))
        audit_goal(e, kid, 'not_satisfied')
        self.assertEqual(e.instance['goal_status'], 'unsolved')
        # The unsatisfied audit records no goal assessment: its basis is the one before the audit.
        self.assertEqual(e.instance.get('goal_assessment_basis', 'absent'), basis_before)
        self.assertEqual(e.runtime['tasks'][hypothesis['id']]['status'], 'planned')
        self.assertTrue(knowledge.assess_use(e.instance['knowledge'][kid], e.instance)['valid'])
        apply_plan(e, plan_output(preparation_requests=['Find evidence for H']), snapshot=snapshot)
        self.assertTrue(any(a['role'] == 'research_preparation' for a in e.runtime['queue']))

    def test_w04_counterexample_audit_depends_on_charter_and_keeps_certificate(self):
        """About 2.3 s, over the 2 s Sim budget: each of the two charters is a template restore and a public decision."""
        from support.entry import entry
        _entry = entry()
        # Auditor responses distinguish proof-only from prove-or-refute. Their
        # mathematical correctness is a fixture, not inferred by the engine.
        for goal, decision, solved in [('Prove C or exhibit a counterexample', 'satisfied', True),
                                       ('Prove C', 'not_satisfied', False)]:
            with self.subTest(goal=goal):
                e = evidence_sim(goal=goal).engine
                self.assertEqual(e._governance()['charter']['content']['goal'], goal)
                n = 1
                certificate = {'domain': 'Nat', 'n': n, 'in_domain': n >= 0, 'claim_n_equals_zero': n == 0}
                self.assertTrue(certificate['in_domain'])
                self.assertFalse(certificate['claim_n_equals_zero'])
                for kind, statement in [('observation', json.dumps(certificate, sort_keys=True)),
                                        ('conjecture', 'Every natural number equals zero')]:
                    proposed = truth_candidate(statement, '')
                    proposed.update(kind=kind, declaration_names=[])
                    e.instance, e.runtime, endpoint = knowledge_io.import_candidate(e.instance, e.runtime,
                        proposed, source_ref='fixture:finite-calculation', actor_ref='EX-calculation', clock=_entry.ports.clock)
                    if kind == 'observation':
                        calculation_id = endpoint
                    else:
                        conjecture_id = endpoint
                claim = {'kind': 'refutes', 'source': calculation_id, 'target': conjecture_id,
                         'confirmed_scope': 'n=1 refutes forall n : Nat, n=0; it proves no universal affirmative'}
                kid, aid = accept_knowledge(e, truth_candidate('¬ (∀ n : Nat, n = 0)',
                    'theorem truth : ¬ (∀ n : Nat, n = 0) := by intro h; exact Nat.noConfusion (h 1)',
                    relation_claim=claim))
                relation = {**claim, 'formal_result_refs': [e.instance['knowledge'][kid]['formal_result_id']],
                            'assessment_refs': [aid], 'evidence_refs': [calculation_id, kid]}
                e.instance, rid = knowledge_io.import_relation(e.instance, relation,
                    source_ref='fixture:counterexample', actor_ref='EX-relation', clock=_entry.ports.clock)
                self.assertEqual(next(r for r in e.instance['relations'] if r['id'] == rid)['kind'], 'refutes')
                formal_before = deepcopy(e.instance['formal_results'])
                self.assertEqual(e.instance['goal_judgments'], [])
                audit_goal(e, kid, decision)
                self.assertEqual(e.instance['goal_status'] == 'mathematically_solved', solved)
                self.assertEqual(e.instance['formal_results'], formal_before)
                self.assertTrue(e.instance['goal_judgments'][0]['dependencies'])

    def test_w05_waiting_task_keeps_obligations_and_other_work_can_proceed(self):
        from support.entry import entry
        _entry = entry()
        e = evidence_sim().engine
        waiting = reviewed_task(e, 'TK-waiting')
        peer = reviewed_task(e, 'TK-independent')
        waiting['status'] = 'waiting'
        question = questions.link(e.runtime, execution_id='EX-old', field='questions/0', owner='user',
                                  targets=[waiting['id']], reason='Approve external scope?', blocks=True, clock=_entry.ports.clock)
        before = deepcopy(waiting['completion_obligations'])
        _ended_execution(e, 'EX-old', 'research_work')
        e.runtime['executions']['EX-old'].update(outcome='waiting', action={'target': waiting['id']})
        self.assertNotEqual(planning.task_ready(waiting, e.instance, e.runtime, evaluation_context=e._evaluation_context())['state'], 'ready')
        self.assertEqual(planning.task_ready(peer, e.instance, e.runtime, evaluation_context=e._evaluation_context())['state'], 'ready')
        with self.assertRaisesRegex(ValueError, '^the applied decision does not affect the question target: '
                                                + question['id'] + '$'):
            questions.resolve_user(e.runtime, [question['id']], resolution_ref='DC-unrelated', affected_ids=[peer['id']])
        questions.resolve_user(e.runtime, [question['id']], resolution_ref='DC-answer', affected_ids=[waiting['id']])
        self.assertEqual(question['resolution_ref'], 'DC-answer')
        next_action = {'id': 'AC-resume', 'role': 'research_work', 'target': waiting['id'],
                       'continuation_of': 'EX-old', 'resolution_ref': 'DC-answer'}
        readiness = planning.task_ready(waiting, e.instance, e.runtime, action=next_action, evaluation_context=e._evaluation_context())
        self.assertEqual(readiness['state'], 'ready', repr(readiness))
        e.instance['grants'][research_grant(e)]['status'] = 'revoked'
        self.assertNotEqual(planning.task_ready(waiting, e.instance, e.runtime, action=next_action, evaluation_context=e._evaluation_context())['state'], 'ready')
        self.assertEqual(waiting['completion_obligations'], before)
        self.assertEqual(e.runtime['executions']['EX-old']['status'], 'ended')

    def test_w06_exposition_revision_invalidates_consumers_not_formal_result(self):
        from support.entry import entry
        _entry = entry()
        e = evidence_sim().engine
        kid, aid = accept_knowledge(e)
        audit_goal(e, kid)
        old_solution = e._solution_basis()
        formal_before = deepcopy(e.instance['formal_results'])
        use_ids = [key for key, row in e.instance['assessment_uses'].items() if row['assessment_id'] == aid]
        changes = {'summary': 'Correct the explanation after an objection'}
        roots = knowledge.revision_roots(e.instance, kid)
        impact = knowledge.plan_impact(e.instance, e.runtime, roots, [])
        e.instance, e.runtime = knowledge.revise_knowledge(e.instance, e.runtime, kid, changes,
            reason='Confirmed explanation defect', actor_ref='EX-internal-review', declared_impact=impact['computed_impact'], clock=_entry.ports.clock)
        self.assertEqual(e.instance['formal_results'], formal_before)
        self.assertEqual(e.instance['knowledge'][kid]['lifecycle'], 'superseded')
        self.assertFalse(knowledge.assess_use(e.instance['knowledge'][kid], e.instance)['valid'])
        self.assertNotEqual(e._solution_basis(), old_solution)
        replacement = next(k for k in e.instance['knowledge'].values() if k.get('supersedes') == kid)
        self.assertFalse(knowledge.assess_use(replacement, e.instance)['valid'])
        e.instance, new_assessment = kr.record_identity_assessment(e.instance, replacement['id'],
            {'decision': 'match', 'basis': kr.identity_basis(e.instance, replacement['id'])}, 'policy:fixture',
            runtime=e.runtime, clock=_entry.ports.clock)
        self.assertNotEqual(new_assessment, aid)
        self.assertTrue(knowledge.assess_use(e.instance['knowledge'][replacement['id']], e.instance)['valid'])
        audit_goal(e, replacement['id'])
        self.assertEqual(e.instance['goal_status'], 'mathematically_solved')
        self.assertNotEqual(e._solution_basis(), old_solution)
        self.assertEqual(e.instance['formal_results'], formal_before)
        self.assertTrue(use_ids)

    def test_w07_every_ready_candidate_disposed_and_changed_premise_blocks_reuse(self):
        e = evidence_sim().engine
        first = reviewed_task(e, 'TK-a')
        second = reviewed_task(e, 'TK-b')
        self.assertEqual(planning.ready_task_ids(e.runtime, e.instance, evaluation_context=e._evaluation_context()), ['TK-a', 'TK-b'])
        with self.assertRaisesRegex(ValueError, EVERY_READY):
            apply_plan(e, plan_output(dispositions=[disposition(first['id'])]))
        apply_plan(e, plan_output(dispositions=[disposition(first['id']), disposition(second['id'], 'not_selected')]),
                   'EX-plan-both')
        first, second = e.runtime['tasks'][first['id']], e.runtime['tasks'][second['id']]
        self.assertTrue(any(a['role'] == 'research_work' and a['target'] == first['id'] for a in e.runtime['queue']))
        self.assertEqual(second['selection_disposition']['kind'], 'not_selected')
        self.assertTrue(planning.contract_review_current(second['reviews'][0], second, e.instance, e.runtime)['valid'])
        second['completion_obligations'][0]['claim'] = 'A different requirement'
        self.assertFalse(planning.contract_review_current(second['reviews'][0], second, e.instance, e.runtime)['valid'])

    def test_w11_history_compaction_keeps_catalog_and_compound_occurrence(self):
        import tempfile
        from pathlib import Path
        e = evidence_sim().engine
        work = reviewed_task(e)
        history = [{'execution_id': 'EX-old', 'report': 'historical ' * 4000}]
        context = {'goal': governance_view(e.instance)['goal'], 'action': {'role': 'research_plan'},
                   'tasks': [{'id': work['id'], 'question': work['question'], 'scope': work['scope']}],
                   'recent_history': history}
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            fit = fit_context(context, max_bytes=6000, workspace=workspace, mandatory_keys=['goal', 'tasks'],
                              role='research_plan')
            self.assertTrue(any(r['key'] == 'recent_history' for r in fit['reductions']))
            self.assertIsNone(fit['overflow'])
            self.assertEqual(fit['context']['tasks'][0]['id'], work['id'])
            ref = fit['context']['recent_history']['source_ref']
            self.assertEqual(json.loads(read_source(workspace, ref)['bytes']), history)
            overflow = fit_context(context, max_bytes=100, workspace=workspace, mandatory_keys=['goal', 'tasks'],
                                   role='research_plan')
            self.assertEqual(overflow['overflow']['kind'], 'input_overflow')
        condition = {'op': 'all', 'args': [{'op': 'always'}, {'op': 'any', 'args': [
            {'op': 'task_disposition_is', 'task_id': work['id'], 'value': 'completed'}, {'op': 'always'}]}]}
        self.assertEqual(planning.evaluate_condition(condition, e.instance, e.runtime)['state'], 'ready')
        # Occurrence truth is not a replacement for independent review.
        work['occurrence_condition'] = condition
        work['reviews'] = []
        self.assertNotEqual(planning.task_ready(work, e.instance, e.runtime, evaluation_context=e._evaluation_context())['state'], 'ready')


class PriorityVectorTests(unittest.TestCase):
    def test_v45_scheduler_blocks_other_activity_and_allows_ended_retry(self):
        e = evidence_sim().engine
        work = reviewed_task(e)
        # The public activation's probe observed every adopted profile's CLI on the fake host.
        # No difficulty/importance judgment is authored here; the admission rule then requires the high profile.
        model = e.instance['config']['tier_models']['high']
        first = {'id': 'AC-first', 'role': 'research_work', 'target': work['id'], 'grant_id': research_grant(e),
                 'owner_activity_id': 'AY-first', 'model_selection': {'model': model}}
        other = {**first, 'id': 'AC-other', 'owner_activity_id': 'AY-other', 'role': 'supplemental_research'}
        same_role = {**first, 'id': 'AC-other-work', 'owner_activity_id': 'AY-other'}
        self.assertTrue(e._dispatchable(deepcopy(other)), repr(other))
        self.assertTrue(e._dispatchable(deepcopy(same_role)), 'different work request is valid before occupancy')
        self.assertTrue(e._dispatchable(deepcopy(first)), 'reviewed unoccupied task must be dispatchable')
        activities.open_activity(e.runtime, activity_id='AY-first', activity_kind='research_work', owner_ref='AC-first',
                                 input_refs=[work['id']], opened_at=e._lifecycle_now().isoformat())
        running = e._register_execution(deepcopy(first), {'id': 'EX-first', 'role': first['role'], 'status': 'running',
                                                          'input_snapshot': e.head, 'input_manifest': []})
        self.assertFalse(e._dispatchable(deepcopy(other)))
        self.assertFalse(e._dispatchable(deepcopy(same_role)))
        at = e._lifecycle_now().isoformat()
        execution_lifecycle.transition_execution(running, 'stopping', at=at)
        execution_lifecycle.transition_execution(running, 'ended', at=at, outcome='execution_incomplete')
        self.assertTrue(e._dispatchable({**deepcopy(first), 'id': 'AC-retry', 'continuation_of': 'EX-first'}),
                        'ended attempt must not consume a lifetime task slot')
        self.assertTrue(e._dispatchable(deepcopy(other)), 'ended work releases the task for the other role')

    def test_v112_engine_completion_rejects_open_then_applies_fulfilled_obligations(self):
        e = evidence_sim().engine
        work = task(e, 'TK-1')
        work.update(status='waiting', results=[{'id': 'EV-proof', 'execution_id': 'EX-work', 'report': 'bounded result'},
                                               {'id': 'EV-scope', 'execution_id': 'EX-work', 'report': 'scope disposition'}])
        assessment = {'task_id': work['id'], 'decision': 'completed', 'item_dispositions': [
            {'obligation_id': 'OB-proof', 'kind': 'fulfilled', 'evidence_refs': ['EV-proof']},
            {'obligation_id': 'OB-scope', 'kind': 'open', 'evidence_refs': []}]}
        before = deepcopy(work)
        for decision in ('completed', 'closed'):
            assessment['decision'] = decision
            with self.subTest(decision=decision), self.assertRaisesRegex(ValueError, OPEN_OBLIGATION[decision]):
                apply_plan(e, plan_output(task_assessments=[assessment]), 'EX-plan-' + decision)
        self.assertEqual(e.runtime['tasks'][work['id']], before)
        assessment['item_dispositions'][1].update(kind='fulfilled', evidence_refs=['EV-scope'])
        assessment['decision'] = 'completed'
        apply_plan(e, plan_output(task_assessments=[assessment]), 'EX-plan-retry')
        work = e.runtime['tasks'][work['id']]
        self.assertEqual(work['status'], 'completed')
        self.assertEqual(work['assessment']['execution_id'], 'EX-plan-retry')
        self.assertEqual(work['assessment']['item_dispositions'], assessment['item_dispositions'])

    def test_v82_withdrawal_preserves_separate_formal_assessment_and_use(self):
        from support.entry import entry
        _entry = entry()
        e = evidence_sim().engine
        kid, aid = accept_knowledge(e)
        work = task(e, 'TK-1', approved=False)
        e.runtime['queue'] = [{'id': 'AC-cancel', 'role': 'research_work', 'target': work['id']}]
        families = {name: deepcopy(e.instance[name]) for name in
                    ('knowledge', 'formal_results', 'expositions', 'identity_assessments', 'assessment_uses')}
        request = [{'task_id': work['id'], 'disposition': 'withdraw', 'reason': 'Different direction'}]
        changed, runtime = apply_task_dispositions(e.instance, e.runtime, request,
            execution_id='EX-planner', input_tasks=deepcopy(e.runtime['tasks']), clock=_entry.ports.clock)
        self.assertEqual(runtime['tasks'][work['id']]['status'], 'closed')
        self.assertEqual(runtime['queue'], [])
        self.assertEqual({name: changed[name] for name in families}, families)
        self.assertTrue(knowledge.assess_use(changed['knowledge'][kid], changed)['valid'])
        e.instance = kr.set_assessment_use(e.instance, aid, 'suspended', 'check objection', 'reviewer')
        changed, _ = apply_task_dispositions(e.instance, e.runtime, request,
            execution_id='EX-planner', input_tasks=deepcopy(e.runtime['tasks']), clock=_entry.ports.clock)
        self.assertFalse(knowledge.assess_use(changed['knowledge'][kid], changed)['valid'])
        self.assertEqual(changed['formal_results'], families['formal_results'])


EVERY_READY = 'every.*ready'
OPEN_OBLIGATION = {'completed': '^terminal assessment retains open obligations$',
                   'closed': '^terminal assessment retains open obligations$'}


if __name__ == '__main__':
    unittest.main()
