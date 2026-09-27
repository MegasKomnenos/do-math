"""Design walkthroughs (design 17.3) and priority vectors: cross-owner domain paths, not activity labels.

The twelve walkthroughs are twelve different domain paths. They replay public domain APIs and ENGINE's actual response consumer. Model
and compiler verdicts are declared fixtures. The trace lists the unexercised
ends (live provider/host, semantic truth of responses, and research efficacy).
"""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from engine_fixtures import evidence_engine, reviewed_task, evidence_task, truth_candidate, accept_knowledge, audit_goal, apply_plan, plan_output, EVIDENCE_TIME
from do_math import execution_profiles, knowledge, knowledge_io, knowledge_records as kr, planning, review_cycle as review
from do_math import contracts
from do_math import questions
from do_math.context_store import fit_context, read_source
from do_math.observations import ObservationTracker
from research_fixtures import write_checkpoint
from do_math.repository import exact_content_hash, new_id
from do_math.engine import query_records, read_record
from do_math.repository import ResearchRepository
from research_fixtures import git_init, observation_rule, observe
from do_math.task_scope import apply_task_dispositions


def start_review(proposal=None, *, previous=None, rounds=2):
    policy = {'id': 'RP-fixture', 'required_perspectives': [], 'minimum_initial_slots': 2,
        'judge_slots': ['judge-0', 'judge-1', 'judge-2'], 'round_limit': rounds,
        'activity_execution_limit': 2 + rounds * 6, 'overflow_disposition': 'unresolved'}
    scope = {'assessment_id': 'SA-fixture', 'policy_id': policy['id'],
        'required_perspectives': [], 'initial_slots': [{'id': f'initial-{i}', 'perspective': str(i),
        'required_source_refs': ['proposal']} for i in range(2)], 'selected_profile_ref': None,
        'activity_execution_limit': policy['activity_execution_limit'], 'overflow_disposition': 'unresolved'}
    return review.start_review(proposal or {'revision': 1, 'proof': 'P'}, 2, max_rounds=rounds,
                               previous=previous, policy=policy, scope_assessment=scope)


def respond(cycle, **changes):
    action = review.next_actions(cycle)[0]
    stage = action['stage']
    output = {'proposal_digest': cycle['proposal_digest'], 'summary': 'Fixture full-source response',
              'used_sources': ['proposal:1'], 'questions': []}
    if stage == 'initial': output.update(decision='match', scope_complete=True, findings=[])
    elif stage == 'organize':
        output['issues'] = [{'id': f'i{index}', 'finding_refs': [f['ref']],
            'answer_role_slot_id': f['ref']['slot'] if f['ref']['stage'] in {'initial', 'answer'} else 'initial-0'}
            for index, f in enumerate(review.context_for(cycle, action)['pending_findings'], start=len(cycle['issues']))]
    elif stage == 'answer':
        output.update(answers=[{'issue_id': i, 'disposition': 'maintain', 'statement': 'Still applies',
            'evidence': ['proposal:1']} for i in review.context_for(cycle, action)['answer_requests']], new_findings=[])
    elif stage == 'judge':
        output.update(decision='mismatch', scope_complete=True, issue_verdicts=[{'issue_id': i,
            'decision': 'approved', 'reason': 'Source comparison', 'evidence': ['proposal:1']}
            for i in cycle['issues']], new_findings=[])
    output.update(changes)
    return review.accept_result(cycle, action, output, new_id('EX'))


def disposition(tid, kind='selected'):
    row = {'task_id': tid, 'kind': kind, 'reason': 'Compare scope and current evidence',
           'next_owner': 'research_work' if kind == 'selected' else 'research_plan'}
    if kind == 'selected': row['expected_research_change'] = 'resolve the bounded case'
    else: row['revisit'] = {'event_refs': ['EV-new-evidence']}
    return row


def activate_relation(e, token):
    template = next(t for t in knowledge_io.relation_templates() if t['token'] == token)
    e.instance, token = knowledge_io.register_kind_definition(e.instance, template,
        source_ref='fixture:relation-definition', actor_ref='EX-definition-author')
    e.instance = knowledge_io.check_kind_definition(e.instance, 'relation', token,
        check_ref='fixture:independent-kind-check', actor_ref='EX-kind-checker')
    e.instance = knowledge_io.activate_kind_definition(e.instance, 'relation', token,
        approval_ref='fixture:kind-approval', actor_ref='EX-kind-approver')
    return token


def rule(threshold=2):
    return observation_rule(threshold=threshold, id='R-attempts', required_evidence=['EV-attempts'], repeat_interval=2)


class Clock:
    value = 0
    def __call__(self): return self.value


def self_check(tracker, obligation, status='normal', **changes):
    return tracker.record_self_check_response({'execution_id': tracker.execution_id,
        'obligation_id': obligation['id'], 'rule_revision': obligation['rule_revision'],
        'progress': 'progress', 'attempts': ['Inspected bounded cases'], 'next_method': 'Check the next case', 'rule_results': [
            {'rule_id': 'R-attempts', 'status': status, 'evidence_refs': ['EV-attempts'],
             'missing_evidence_refs': [], 'reason': 'Observed the preserved event log'}], **changes},
        available_evidence_refs={'EV-attempts'})


class DesignWalkthroughs(unittest.TestCase):
    def test_w01_existing_knowledge_solves_without_new_research_task(self):
        requirement = {'id': 'AR-reproduce', 'scope': 'Reproduce the accepted result', 'assessor': 'research_plan',
                       'criteria': ['Reproduction evidence is preserved'], 'required_inputs': [], 'external_effects': []}
        e = evidence_engine(academic_requirements=[requirement]); kid, _ = accept_knowledge(e)
        self.assertTrue(knowledge.assess_use(e.instance['knowledge'][kid], e.instance)['valid'])
        audit_goal(e, kid)
        self.assertEqual(e.instance['goal_status'], 'mathematically_solved')
        self.assertEqual(len(e.runtime['tasks']), 1)
        task = next(iter(e.runtime['tasks'].values()))
        self.assertEqual(task['academic_requirement_id'], requirement['id'])
        self.assertEqual(task['solution_basis'], e._solution_basis())
        self.assertEqual(task['status'], 'planned')
        self.assertTrue(any(task['id'] in a.get('observation_rule_targets', {}) for a in e.runtime['queue']))
        self.assertFalse(any(a['role'] == 'task_contract_review' and a.get('target') == task['id'] for a in e.runtime['queue']))
        self.assertFalse(any(a['role'] == 'research_work' for a in e.runtime['queue']))
        self.assertIsNotNone(e._solution_basis())
        # The generated followup must be consumable by the installed v5 task
        # contract, not merely an old-format object labelled planned.
        from do_math.task_contracts import validate_task_contract
        validate_task_contract(task)

    def test_w02_periodic_reconsideration_prepares_while_work_is_live(self):
        e = evidence_engine(); old = reviewed_task(e, 'TK-running')
        e.runtime.update(status='active', cycles=0, next_research_reconsider_at=EVIDENCE_TIME)
        e.runtime['executions']['EX-running'] = {'id': 'EX-running', 'role': 'research_work', 'status': 'running',
                                                'action': {'id': 'AC-running', 'target': old['id'], 'role': 'research_work'}}
        planning.record_due_events(e.instance, e.runtime, EVIDENCE_TIME)
        state = planning.schedule_reconsideration(e.instance, e.runtime, now=EVIDENCE_TIME)
        self.assertFalse(state['exhausted'])
        preparation = next(a for a in e.runtime['queue'] if a['role'] == 'research_preparation')
        self.assertTrue(preparation['event_refs'])
        template = evidence_task('TK-different')
        # A model emits the wire candidate, never receiver-owned task fields.
        proposal = {name: deepcopy(template[name]) for name in (
            'question', 'scope', 'expected', 'progress_criteria', 'completion_obligations',
            'inputs', 'reuse', 'dependencies', 'profile_refs', 'authority_refs', 'basis_refs')}
        # This case tests periodic scheduling, with no formal checker premise.
        proposal.update(title='Different approach', revises_task_id=None, work_class='nonformal')
        from do_math.execution_profiles import profile_ref
        proposal['profile_refs'] = [profile_ref(p) for p in e.instance['execution_profiles'].values()
                                    if p['role'] == 'research_work']
        from jsonschema import Draft202012Validator
        self.assertEqual(list(Draft202012Validator(contracts.TASK_CANDIDATE).iter_errors(proposal)), [])
        e.runtime['executions']['EX-prep'] = {'id': 'EX-prep', 'role': 'research_preparation', 'status': 'ended', 'input_snapshot': e.head, 'extensions': {}}
        # The preparation's issued input names what its task inputs may cite; this proposal cites none.
        from unittest.mock import create_autospec
        e._issued_input = create_autospec(e._issued_input, return_value=(
            {'available_input_refs': [], 'supplied_record_ids': []}, None))
        e._apply(preparation, {'candidates': [proposal], 'summary': 'Different lens', 'questions': []}, 'EX-prep')
        created = next(t for t in e.runtime['tasks'].values() if t['id'] != old['id'])
        self.assertEqual(created['status'], 'planned')
        self.assertEqual(e.runtime['executions']['EX-running']['status'], 'running')
        self.assertTrue(any(a['role'] == 'task_contract_review' and a['target'] == created['id'] for a in e.runtime['queue']))
        self.assertFalse(any(a['role'] == 'research_work' and a['target'] == created['id'] for a in e.runtime['queue']))

    def test_w03_conditional_theorem_does_not_discharge_missing_hypothesis(self):
        e = evidence_engine(); task = evidence_task('TK-hypothesis')
        task['question'] = 'Establish H'; e.runtime['tasks'][task['id']] = task
        kid, _ = accept_knowledge(e, truth_candidate('H implies P', 'theorem truth (H P : Prop) (h : H → P) : H → P := h'))
        audit_goal(e, kid, 'not_satisfied')
        self.assertEqual(e.instance['goal_status'], 'unresolved')
        self.assertEqual(e.runtime['tasks'][task['id']]['status'], 'planned')
        self.assertTrue(knowledge.assess_use(e.instance['knowledge'][kid], e.instance)['valid'])
        apply_plan(e, plan_output(preparation_requests=['Find evidence for H']))
        self.assertTrue(any(a['role'] == 'research_preparation' for a in e.runtime['queue']))

    def test_w04_counterexample_audit_depends_on_charter_and_keeps_certificate(self):
        # Auditor responses distinguish proof-only from prove-or-refute. Their
        # mathematical correctness is a fixture, not inferred by the engine.
        for goal, decision, solved in [('Prove C or exhibit a counterexample', 'satisfied', True),
                                       ('Prove C', 'not_satisfied', False)]:
            with self.subTest(goal=goal):
                e = evidence_engine(goal)
                n = 1
                certificate = {'domain': 'Nat', 'n': n, 'in_domain': n >= 0, 'claim_n_equals_zero': n == 0}
                self.assertTrue(certificate['in_domain']); self.assertFalse(certificate['claim_n_equals_zero'])
                for kind, statement in [('observation', json.dumps(certificate, sort_keys=True)),
                                         ('conjecture', 'Every natural number equals zero')]:
                    proposed = truth_candidate(statement, ''); proposed.update(kind=kind, declaration_names=[])
                    e.instance, e.runtime, endpoint = knowledge_io.import_candidate(e.instance, e.runtime,
                        proposed, source_ref='fixture:finite-calculation', actor_ref='EX-calculation')
                    if kind == 'observation': calculation_id = endpoint
                    else: conjecture_id = endpoint
                token = activate_relation(e, 'refutes')
                claim = {'kind': token, 'source': calculation_id, 'target': conjecture_id,
                         'confirmed_scope': 'n=1 refutes forall n : Nat, n=0; it proves no universal affirmative'}
                kid, aid = accept_knowledge(e, truth_candidate('¬ (∀ n : Nat, n = 0)',
                    'theorem truth : ¬ (∀ n : Nat, n = 0) := by intro h; exact Nat.noConfusion (h 1)',
                    relation_claim=claim))
                relation = {**claim, 'formal_result_refs': [e.instance['knowledge'][kid]['formal_result_id']],
                            'assessment_refs': [aid], 'evidence_refs': [calculation_id, kid]}
                e.instance, rid = knowledge_io.import_relation(e.instance, relation,
                    source_ref='fixture:counterexample', actor_ref='EX-relation')
                self.assertEqual(next(r for r in e.instance['relations'] if r['id'] == rid)['kind'], 'refutes')
                formal_before = deepcopy(e.instance['formal_results'])
                audit_goal(e, kid, decision)
                self.assertEqual(e.instance['goal_status'] == 'mathematically_solved', solved)
                self.assertEqual(e.instance['formal_results'], formal_before)
                self.assertTrue(e.instance['goal_judgments'][0]['dependencies'])

    def test_w05_waiting_task_keeps_obligations_and_other_work_can_proceed(self):
        e = evidence_engine(); waiting = reviewed_task(e, 'TK-waiting'); peer = reviewed_task(e, 'TK-independent')
        waiting['status'] = 'waiting'
        question = questions.link(e.runtime, execution_id='EX-old', field='questions/0', owner='user',
            targets=[waiting['id']], reason='Approve external scope?', blocks=True)
        before = deepcopy(waiting['completion_obligations'])
        e.runtime['executions']['EX-old'] = {'id': 'EX-old', 'role': 'research_work', 'status': 'ended',
                                           'outcome': 'waiting', 'action': {'target': waiting['id']}}
        self.assertNotEqual(planning.task_ready(waiting, e.instance, e.runtime)['state'], 'ready')
        self.assertEqual(planning.task_ready(peer, e.instance, e.runtime)['state'], 'ready')
        with self.assertRaises(ValueError):
            questions.resolve_user(e.runtime, [question['id']], resolution_ref='DC-unrelated', affected_ids=[peer['id']])
        questions.resolve_user(e.runtime, [question['id']], resolution_ref='DC-answer', affected_ids=[waiting['id']])
        self.assertEqual(question['resolution_ref'], 'DC-answer')
        next_action = {'id': 'AC-resume', 'role': 'research_work', 'target': waiting['id'],
                       'continuation_of': 'EX-old', 'resolution_ref': 'DC-answer'}
        readiness = planning.task_ready(waiting, e.instance, e.runtime, action=next_action)
        self.assertEqual(readiness['state'], 'ready', repr(readiness))
        e.instance['grants']['GR-evidence']['status'] = 'revoked'
        self.assertNotEqual(planning.task_ready(waiting, e.instance, e.runtime, action=next_action)['state'], 'ready')
        self.assertEqual(waiting['completion_obligations'], before)
        self.assertEqual(e.runtime['executions']['EX-old']['status'], 'ended')

    def test_w06_exposition_revision_invalidates_consumers_not_formal_result(self):
        e = evidence_engine(); kid, aid = accept_knowledge(e); audit_goal(e, kid)
        old_solution = e._solution_basis(); formal_before = deepcopy(e.instance['formal_results'])
        use_ids = [key for key, row in e.instance['assessment_uses'].items() if row['assessment_id'] == aid]
        changes = {'summary': 'Correct the explanation after an objection'}
        roots = knowledge.revision_roots(e.instance, kid)
        impact = knowledge.plan_impact(e.instance, e.runtime, roots, [])
        e.instance, e.runtime = knowledge.revise_knowledge(e.instance, e.runtime, kid,
            changes, reason='Confirmed explanation defect',
            actor_ref='EX-internal-review', declared_impact=impact['computed_impact'])
        self.assertEqual(e.instance['formal_results'], formal_before)
        self.assertEqual(e.instance['knowledge'][kid]['lifecycle'], 'superseded')
        self.assertFalse(knowledge.assess_use(e.instance['knowledge'][kid], e.instance)['valid'])
        self.assertNotEqual(e._solution_basis(), old_solution)
        replacement = next(k for k in e.instance['knowledge'].values() if k.get('supersedes') == kid)
        self.assertFalse(knowledge.assess_use(replacement, e.instance)['valid'])
        e.instance, new_assessment = kr.record_identity_assessment(e.instance, replacement['id'],
            {'decision': 'match', 'basis': kr.identity_basis(e.instance, replacement['id']),
             }, 'policy:fixture', runtime=e.runtime)
        self.assertNotEqual(new_assessment, aid)
        self.assertTrue(knowledge.assess_use(e.instance['knowledge'][replacement['id']], e.instance)['valid'])
        audit_goal(e, replacement['id'])
        self.assertEqual(e.instance['goal_status'], 'mathematically_solved')
        self.assertNotEqual(e._solution_basis(), old_solution)
        self.assertEqual(e.instance['formal_results'], formal_before)
        self.assertTrue(use_ids)

    def test_w07_every_ready_candidate_disposed_and_changed_premise_blocks_reuse(self):
        e = evidence_engine(); first = reviewed_task(e, 'TK-a'); second = reviewed_task(e, 'TK-b')
        ready = planning.ready_task_ids(e.runtime, e.instance)
        self.assertEqual(ready, ['TK-a', 'TK-b'])
        with self.assertRaisesRegex(ValueError, 'every.*ready'):
            apply_plan(e, plan_output(dispositions=[disposition(first['id'])]))
        apply_plan(e, plan_output(dispositions=[disposition(first['id']), disposition(second['id'], 'not_selected')]))
        first, second = e.runtime['tasks'][first['id']], e.runtime['tasks'][second['id']]
        self.assertTrue(any(a['role'] == 'research_work' and a['target'] == first['id'] for a in e.runtime['queue']))
        self.assertEqual(second['selection_disposition']['kind'], 'not_selected')
        self.assertTrue(planning.contract_review_current(second['reviews'][0], second, e.instance, e.runtime)['valid'])
        second['completion_obligations'][0]['claim'] = 'A different requirement'
        self.assertFalse(planning.contract_review_current(second['reviews'][0], second, e.instance, e.runtime)['valid'])

    def test_w08_self_check_defect_and_late_objection_reach_fresh_judges(self):
        clock = Clock()
        with tempfile.TemporaryDirectory() as directory:
            tracker = ObservationTracker('EX-repeat', Path(directory), {
                'self_check_revision': 1, 'observation_rules': [rule()], 'self_check_response_window_seconds': 5}, clock=clock)
            write_checkpoint(directory, counters={'attempts': 2})
            due = next(r for r in observe(tracker, {'type': 'tick'}) if r['kind'] == 'self_check_due')
            receipt = self_check(tracker, due, 'defect')
            self.assertEqual(receipt['followup']['kind'], 'operational_review_due')
            self.assertIn(due['id'], receipt['followup']['basis_refs'])
        cycle = respond(start_review(), decision='mismatch', findings=[{'id': 'f1', 'statement': 'Original defect', 'evidence': ['proposal:1']}])
        cycle = respond(respond(cycle))  # independent peer, then organization
        cycle = respond(cycle, new_findings=[{'id': 'late', 'statement': 'Late independent defect', 'evidence': ['proposal:2']}])
        cycle = respond(respond(cycle))
        self.assertEqual((cycle['phase'], cycle['round']), ('organize', 2))
        cycle = respond(cycle)
        self.assertEqual(review.next_actions(cycle)[0]['stage'], 'answer')
        cycle = respond(cycle)
        self.assertEqual([a['slot'] for a in review.next_actions(cycle)], ['judge-0', 'judge-1', 'judge-2'])
        cycle = respond(cycle, new_findings=[{'id': 'at-cap', 'statement': 'Unanswered at cap', 'evidence': ['proposal:3']}])
        cycle = respond(respond(cycle))
        self.assertEqual(cycle['decision'], 'unresolved')
        self.assertTrue(cycle['pending_findings'])

    def test_w09_new_edition_reopens_all_slots_and_restoration_is_local(self):
        old = respond(respond(start_review()))
        self.assertEqual(old['decision'], 'match')
        fresh = start_review({'revision': 2, 'proof': 'P with local edit', 'unchanged_part': 'old defect'}, previous=old)
        self.assertEqual(len(review.next_actions(fresh)), 2)
        fresh = respond(fresh, decision='mismatch', findings=[{'id': 'old-defect',
            'statement': 'Error in unchanged part', 'evidence': ['proposal:unchanged_part']}])
        fresh = respond(respond(fresh))
        self.assertEqual(fresh['phase'], 'judge')
        action = review.next_actions(fresh)[0]
        recovered = review.record_recovery_event(fresh, action, {'reason': 'source_read_error',
            'retryable': True, 'preserved_range': {'slot': action['slot'], 'through_index': 0}})
        self.assertIn(action, review.next_actions(recovered))
        lost = review.record_recovery_event(recovered, action, {'reason': 'permanent_loss',
            'retryable': False, 'preserved_range': {'slot': action['slot'], 'through_index': 0}})
        self.assertNotIn(action, review.next_actions(lost))
        self.assertEqual(len(review.next_actions(lost)), 2)
        self.assertNotEqual(lost.get('decision'), 'match')

    def test_w10_rule_revision_preserves_old_obligation_deadline_and_rejects_replay(self):
        clock = Clock()
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            tracker = ObservationTracker('EX-adapt', workspace, {
                'self_check_revision': 1, 'observation_rules': [rule()], 'self_check_response_window_seconds': 5}, clock=clock)
            write_checkpoint(workspace, counters={'attempts': 2})
            due = next(r for r in observe(tracker, {'type': 'tick'}) if r['kind'] == 'self_check_due')
            deadline = due['deadline_offset_ms']
            # A valid response may adapt rules. A free-standing file must not
            # erase obligations. Leave the first obligation open while a second
            # real boundary supplies the response that changes the rules.
            write_checkpoint(workspace, counters={'attempts': 4})
            second = next(r for r in observe(tracker, {'type': 'tick'}) if r['kind'] == 'self_check_due')
            receipt = self_check(tracker, second, rule_proposal={'current_revision': 1,
                'reason': 'Next search stage uses a larger batch', 'rules': [rule(6)]})
            self.assertEqual(receipt['rule_update']['kind'], 'observation_rules_accepted')
            self.assertEqual(tracker.obligations[due['id']]['deadline_offset_ms'], deadline)
            bad = tracker.record_self_check_response({'obligation_id': due['id'], 'rule_revision': 2})
            self.assertEqual(bad['kind'], 'self_check_rejected')
            self.assertEqual(tracker.obligations[due['id']]['status'], 'open')
            self.assertEqual(self_check(tracker, due)['followup']['kind'], 'continue')
            self.assertEqual(self_check(tracker, due)['kind'], 'self_check_rejected')

    def test_w11_history_compaction_keeps_catalog_and_compound_occurrence(self):
        e = evidence_engine(); task = reviewed_task(e)
        history = [{'execution_id': 'EX-old', 'report': 'historical ' * 4000}]
        context = {'goal': e.instance['goal'], 'action': {'role': 'research_plan'},
                   'tasks': [{'id': task['id'], 'question': task['question'], 'scope': task['scope']}],
                   'recent_history': history}
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            fit = fit_context(context, max_bytes=6000, workspace=workspace,
                              mandatory_keys=['goal', 'tasks'], role='research_plan')
            self.assertTrue(any(r['key'] == 'recent_history' for r in fit['reductions']))
            self.assertIsNone(fit['overflow'])
            self.assertEqual(fit['context']['tasks'][0]['id'], task['id'])
            ref = fit['context']['recent_history']['source_ref']
            self.assertEqual(json.loads(read_source(workspace, ref)['bytes']), history)
            overflow = fit_context(context, max_bytes=100, workspace=workspace,
                                   mandatory_keys=['goal', 'tasks'], role='research_plan')
            self.assertEqual(overflow['overflow']['kind'], 'input_overflow')
        condition = {'op': 'all', 'args': [{'op': 'always'}, {'op': 'any', 'args': [
            {'op': 'task_disposition_is', 'task_id': task['id'], 'value': 'completed'}, {'op': 'always'}]}]}
        self.assertEqual(planning.evaluate_condition(condition, e.instance, e.runtime)['state'], 'ready')
        # Occurrence truth is not a replacement for independent review.
        task['occurrence_condition'] = condition; task['reviews'] = []
        self.assertNotEqual(planning.task_ready(task, e.instance, e.runtime)['state'], 'ready')

    def test_w12_query_import_metadata_and_next_snapshot_preserve_epistemic_distinctions(self):
        # Reuse the owner's real review-cycle producer, not an invented cycle
        # reference or an unsealed match. Only the compiler/reviewer answers
        # are fixtures; the cycle, executions and registered storage are real.
        from review_fixtures import reviewed_candidate
        state, archived_runtime, kid, aid = reviewed_candidate(
            Path(self.enterContext(tempfile.TemporaryDirectory())), verified=True)
        e = evidence_engine()
        e.instance.update(deepcopy(state))
        e.runtime.update(deepcopy(archived_runtime))
        e.runtime['tasks']['TK-work'] = evidence_task('TK-work')
        e.runtime['executions']['EX-work'] = {'id': 'EX-work', 'role': 'research_work', 'status': 'ended',
            'extensions': {'knowledge_metadata': [{'title': 'Useful failed search', 'epistemic_status': 'exploratory',
                'selection_relevance': 'Avoid the exhausted finite search',
                'uncertainty_assessment': {'claim': 'Not a proof', 'scope': 'finite search only'}}]}}
        useful = truth_candidate('Useful failed search', '')
        useful.update(title='Useful failed search', declaration_names=[], kind='observation')
        e._apply({'id': 'AC-work', 'role': 'research_work', 'target': 'TK-work'}, {'report': 'No proof found',
            'outcome': 'partial', 'remaining_work': ['general case'], 'knowledge': [useful], 'relations': [], 'questions': []}, 'EX-work')
        imported = next(k for k in e.instance['knowledge'].values() if k['id'] != kid)
        self.assertEqual(imported['selection_relevance'], 'Avoid the exhausted finite search')
        self.assertFalse(knowledge.assess_use(imported, e.instance)['valid'])
        e.instance = kr.set_assessment_use(e.instance, aid, 'suspended', 'new objection', 'review')
        self.assertFalse(knowledge.assess_use(e.instance['knowledge'][kid], e.instance)['valid'])
        token = activate_relation(e, 'supports')
        e.instance, relation_id = knowledge_io.import_relation(e.instance, {
            'kind': token, 'source': imported['id'], 'target': kid,
            'confirmed_scope': 'Search history informs reuse; no formal implication',
            'evidence_refs': [imported['id']]}, source_ref='fixture:search-history', actor_ref='EX-relation')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            git_init(root)
            identifier = new_id('RI'); e.instance['id'] = identifier
            store = ResearchRepository(root, identifier)
            # Persist the actual knowledge families, not the intentionally
            # partial in-memory ENGINE/host fixture.
            state = {k: deepcopy(e.instance[k]) for k in ('knowledge', 'formal_results', 'expositions',
                'identity_assessments', 'assessment_uses', 'kind_definitions', 'relations',
                'trust_environments', 'active_trust_environment', 'execution_profiles', 'capacity_constraints')}
            state.update(id=identifier, sources=[])
            runtime = deepcopy(archived_runtime)
            runtime['trust_bindings'] = deepcopy(e.runtime['trust_bindings'])
            # Every stored state passes the current lifecycle gate.
            from research_fixtures import current_state
            state, runtime = current_state(state, runtime)
            head = store.initialize(state, runtime)
            found = query_records(root, identifier, kind='knowledge', snapshot=head)
            self.assertEqual(found['snapshot'], head)
            self.assertEqual({r['record']['id'] for r in found['items']}, {kid, imported['id']})
            record = read_record(root, identifier, imported['id'], snapshot=head)
            self.assertEqual(record['record']['uncertainty_assessment'],
                             {'claim': 'Not a proof', 'scope': 'finite search only'})
            outward = query_records(root, identifier, related_to=imported['id'], direction='outgoing', snapshot=head)
            inward = query_records(root, identifier, related_to=imported['id'], direction='incoming', snapshot=head)
            self.assertEqual({r['record']['id'] for r in outward['items']}, {kid, relation_id})
            self.assertEqual(inward['items'], [])
            self.assertTrue(outward['query_basis']['complete'])


class PriorityVectorTests(unittest.TestCase):
    def test_v45_scheduler_blocks_other_activity_and_allows_ended_retry(self):
        e = evidence_engine(); task = reviewed_task(e)
        from do_math.initialization import adapter_for
        # Fixture behavioral capability observations are bound to actual local
        # adapter/worker identity. Reading hashes does not execute the CLI.
        e.instance['capability_evidence'] = {}
        for profile in e.instance['execution_profiles'].values():
            if profile['role'] not in {'research_work', 'supplemental_research'}: continue
            observation = {'execution_profile_ref': execution_profiles.profile_ref(profile),
                'identity': adapter_for(profile).capability_identity(), 'observed_at': EVIDENCE_TIME,
                'capabilities': {key: {'status': 'supported', 'evidence': 'fixture only'}
                                 for key in profile['required_capabilities']}}
            observation['id'] = 'CE-' + exact_content_hash(observation)
            e.instance['capability_evidence'][observation['id']] = observation
        # No difficulty/importance judgment is authored in this fixture;
        # the current admission rule therefore requires the high profile.
        model = e.instance['config']['tier_models']['high']
        first = {'id': 'AC-first', 'role': 'research_work', 'target': task['id'], 'grant_id': 'GR-evidence',
                 'owner_activity_id': 'AY-first', 'model_selection': {'model': model}}
        other = {**first, 'id': 'AC-other', 'owner_activity_id': 'AY-other', 'role': 'supplemental_research'}
        same_role = {**first, 'id': 'AC-other-work', 'owner_activity_id': 'AY-other'}
        self.assertTrue(e._dispatchable(other), repr(other))
        self.assertTrue(e._dispatchable(same_role), 'different work request is valid before occupancy')
        self.assertTrue(e._dispatchable(first), 'reviewed unoccupied task must be dispatchable')
        e.runtime['executions']['EX-first'] = {'id': 'EX-first', 'status': 'running',
            'role': first['role'], 'action': deepcopy(first), 'owner_activity_id': 'AY-first'}
        self.assertFalse(e._dispatchable(other))
        self.assertFalse(e._dispatchable(same_role))
        e.runtime['executions']['EX-first'].update(status='ended', outcome='execution_incomplete')
        self.assertTrue(e._dispatchable({**first, 'id': 'AC-retry', 'continuation_of': 'EX-first'}),
                        'ended attempt must not consume a lifetime task slot')
        self.assertTrue(e._dispatchable(other), 'ended work releases the task for the other role')

    def test_v112_engine_completion_rejects_open_then_applies_fulfilled_obligations(self):
        e = evidence_engine(); task = evidence_task()
        task.update(status='waiting', results=[{'id': 'EV-proof', 'execution_id': 'EX-work', 'report': 'bounded result'},
                                              {'id': 'EV-scope', 'execution_id': 'EX-work', 'report': 'scope disposition'}])
        e.runtime['tasks'][task['id']] = task
        assessment = {'task_id': task['id'], 'decision': 'completed', 'item_dispositions': [
            {'obligation_id': 'OB-proof', 'kind': 'fulfilled', 'evidence_refs': ['EV-proof']},
            {'obligation_id': 'OB-scope', 'kind': 'open', 'evidence_refs': []}]}
        before = deepcopy(task)
        for decision in ('completed', 'closed'):
            assessment['decision'] = decision
            with self.assertRaises(ValueError): apply_plan(e, plan_output(task_assessments=[assessment]))
        self.assertEqual(e.runtime['tasks'][task['id']], before)
        assessment['item_dispositions'][1].update(kind='fulfilled', evidence_refs=['EV-scope'])
        assessment['decision'] = 'completed'
        apply_plan(e, plan_output(task_assessments=[assessment]), 'EX-plan-retry')
        task = e.runtime['tasks'][task['id']]
        self.assertEqual(task['status'], 'completed')
        self.assertEqual(task['assessment']['execution_id'], 'EX-plan-retry')
        self.assertEqual(task['assessment']['item_dispositions'], assessment['item_dispositions'])

    def test_v82_withdrawal_preserves_separate_formal_assessment_and_use(self):
        e = evidence_engine(); kid, aid = accept_knowledge(e); task = evidence_task()
        e.runtime['tasks'][task['id']] = task
        e.runtime['executions']['EX-preparation'] = {'id': 'EX-preparation', 'role': 'research_preparation', 'status': 'ended'}
        e.runtime['queue'] = [{'id': 'AC-cancel', 'role': 'research_work', 'target': task['id']}]
        families = {name: deepcopy(e.instance[name]) for name in
                    ('knowledge', 'formal_results', 'expositions', 'identity_assessments', 'assessment_uses')}
        request = [{'task_id': task['id'], 'disposition': 'withdraw', 'reason': 'Different direction'}]
        changed, runtime = apply_task_dispositions(e.instance, e.runtime, request,
            execution_id='EX-planner', input_tasks=deepcopy(e.runtime['tasks']))
        self.assertEqual(runtime['tasks'][task['id']]['status'], 'closed')
        self.assertEqual(runtime['queue'], [])
        self.assertEqual({name: changed[name] for name in families}, families)
        self.assertTrue(knowledge.assess_use(changed['knowledge'][kid], changed)['valid'])
        e.instance = kr.set_assessment_use(e.instance, aid, 'suspended', 'check objection', 'reviewer')
        changed, _ = apply_task_dispositions(e.instance, e.runtime, request,
            execution_id='EX-planner', input_tasks=deepcopy(e.runtime['tasks']))
        self.assertFalse(knowledge.assess_use(changed['knowledge'][kid], changed)['valid'])
        self.assertEqual(changed['formal_results'], families['formal_results'])


if __name__ == '__main__': unittest.main(verbosity=2)
