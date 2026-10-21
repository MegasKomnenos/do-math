"""The engine's receivers of preparation, contract review and plan extensions on a restored Sim
(``core_engine._apply``, ``_apply_extensions``; layer 2), moved from ``test_task_scope`` and ``test_task_contracts``.

The legacy tests built an engine without its constructor (``bare_engine``) and
replaced what the receivers read: the store (an autospec whose ``view``
returned the current runtime as the plan's input snapshot) or the engine's
issued-input, question, evaluation-context and governance methods. Here the
engine is a restored Sim's: the store is the real ``ResearchRepository`` over
the Git port, an input snapshot is a published head, and an execution's issued
input is archived below its input bundle (``support.engine_context.issue``), so
every method the receivers call runs as it is. Tasks and returned executions
come from ``support.engine_lifecycle``.
"""
import unittest
from copy import deepcopy

from do_math import planning
from support.engine_context import issue
from support.engine_lifecycle import _ended_execution, clear_work, task
from support.sim import Sim, warm_template

setUpModule = warm_template

WITHDRAW = {'task_id': 'TK-AI', 'disposition': 'withdraw', 'reason': 'A better task subsumes it.'}


class EngineIntegrationTest(unittest.TestCase):
    """A plan's withdrawal extension, applied against the tasks of the plan's published input snapshot."""

    def setUp(self):
        self.sim = Sim.activated()
        clear_work(self.sim)
        self.engine = self.sim.engine
        # An unreviewed task a returned preparation (EX-preparation) produced.
        task(self.engine, 'TK-AI', approved=False)
        self.engine._save()
        self.snapshot = self.engine.head

    def plan(self):
        """The returned plan EX-plan that read ``self.snapshot`` and asked to withdraw TK-AI."""
        _ended_execution(self.engine, 'EX-plan', 'research_plan')
        self.engine.runtime['executions']['EX-plan'].update(input_snapshot=self.snapshot,
                                                            extensions={'task_dispositions': [dict(WITHDRAW)]})

    def test_engine_applies_task_disposition_extension(self):
        """A planning extension closes the eligible task through task_scope."""
        before = planning.contract_hash(self.engine.runtime['tasks']['TK-AI'])
        self.plan()
        self.engine._apply_extensions({'role': 'research_plan'}, 'EX-plan')
        withdrawn = self.engine.runtime['tasks']['TK-AI']
        self.assertEqual(withdrawn['status'], 'closed')
        self.assertEqual((withdrawn['scope_disposition']['actor_execution'],
                          withdrawn['scope_disposition']['previous_contract_sha256']), ('EX-plan', before))
        self.engine._save()
        self.sim.restart()
        self.assertEqual(self.sim.runtime['tasks']['TK-AI']['status'], 'closed')

    def test_withdrawal_reads_the_plans_input_snapshot(self):
        """The contract the plan saw is read from its snapshot: a later contract change refuses the withdrawal."""
        self.engine.runtime['tasks']['TK-AI']['question'] = 'A narrower question published after the plan read its input'
        self.engine._save()
        self.plan()
        with self.assertRaisesRegex(ValueError, '^task contract changed since the execution input snapshot: TK-AI$'):
            self.engine._apply_extensions({'role': 'research_plan'}, 'EX-plan')
        self.assertEqual(self.engine.runtime['tasks']['TK-AI']['status'], 'planned')


class PreparationReceiverTests(unittest.TestCase):
    """A returned preparation's candidates become tasks through the engine's receiver."""

    def setUp(self):
        self.sim = Sim.activated()
        clear_work(self.sim)
        self.engine = self.sim.engine

    def preparation(self, identifier, issued, extensions=None):
        """The ended preparation ``identifier`` that read the current head and was issued ``issued``."""
        _ended_execution(self.engine, identifier, 'research_preparation')
        execution = self.engine.runtime['executions'][identifier]
        execution.update(input_snapshot=self.engine.head, extensions=extensions or {})
        issue(self.engine, execution, issued, 'BA-' + identifier)
        return execution

    def test_preparation_rechecks_revision_status_and_the_current_dependency_graph(self):
        """T3 2.1 s: two stored tasks and an issued revision exercise the candidate receiver."""
        from support.role_answers import candidate
        from support.engine_lifecycle import research_grant
        engine = self.engine
        first = task(engine, 'TK-first')
        second = task(engine, 'TK-second')
        second['dependencies'] = [first['id']]
        engine._save()
        self.preparation('EX-revision-author', {'available_input_refs': [first['id'], second['id']],
            'supplied_record_ids': [first['id'], second['id']]})
        wire = candidate('Revised first', revises=first['id'])
        wire['profile_refs'] = deepcopy(first['profile_refs'])
        wire['authority_refs'] = [research_grant(engine)]
        wire['dependencies'] = [second['id']]
        def apply(candidate_runtime):
            # This is the preparation receiver's own seam. The integration
            # caller owns these copies; impact-review behavior has its tests.
            original = engine.runtime
            try:
                engine.runtime = candidate_runtime
                engine._apply({'role': 'research_preparation'}, {'candidates': [wire]},
                    'EX-revision-author', owns_response=False)
            finally:
                engine.runtime = original
        before = deepcopy((engine.head, engine.instance, engine.runtime))
        with self.assertRaisesRegex(ValueError, '^explicit task dependency cycle: '):
            apply(deepcopy(engine.runtime))
        self.assertEqual((engine.head, engine.instance, engine.runtime), before)
        current = deepcopy(engine.runtime)
        current['tasks'][first['id']]['status'] = 'active'
        with self.assertRaisesRegex(ValueError, '^revision must identify an existing unfinished task$'):
            apply(current)
        self.assertEqual((engine.head, engine.instance, engine.runtime), before)

    def test_replacement_preserves_the_actual_delegated_revision_owner(self):
        """T3 52.6 s cold: the real theorem/relation, delegation and replacement preserve the original owner."""
        from support.planning_contract_inputs import relation_sim, delegated_revision, produce_task
        sim = relation_sim()
        parent, tid, kid = delegated_revision(sim)
        engine = sim.engine
        self.assertEqual(engine.runtime['tasks'][tid]['revision_request_action_id'], parent)
        old_revision = engine.runtime['tasks'][tid]['revision']
        replacement = produce_task(sim, 'Revised delegated task', revises=tid, revision_targets=[kid])
        self.assertEqual(replacement, tid)
        self.assertEqual(engine.runtime['tasks'][tid]['revision'], old_revision + 1)
        self.assertEqual(engine.runtime['tasks'][tid]['revision_request_action_id'], parent)
        self.assertEqual(engine.store.load()[2]['tasks'][tid]['revision_request_action_id'], parent)

    def test_preparation_rejects_an_unfinished_execution_outcome_condition(self):
        from support.role_answers import candidate
        from support.engine_lifecycle import research_grant
        engine = self.engine
        prior = task(engine, 'TK-current-revision')
        self.preparation('EX-current-author', {'available_input_refs': [], 'supplied_record_ids': []})
        live = engine._register_execution({'id': 'AC-condition-live', 'role': 'maintenance'},
            {'id': 'EX-condition-live', 'role': 'maintenance', 'status': 'running'})
        proposal = candidate('Conditional work')
        proposal['profile_refs'] = deepcopy(prior['profile_refs'])
        proposal['authority_refs'] = [research_grant(engine)]
        extension = {'task_conditions': [{'task_title': proposal['title'], 'occurrence_condition': {
            'op': 'record_field_equals', 'space': 'runtime', 'family': 'execution',
            'record_id': live['id'], 'pointer': '/outcome', 'value': 'output_accepted'}}]}
        # The grammar is valid. A still-running execution has no scalar outcome
        # yet, which must remain an evaluation error rather than a ready task.
        planning.validate_condition(extension['task_conditions'][0]['occurrence_condition'])
        before = deepcopy((engine.head, engine.instance, engine.runtime))
        bundle = {'integration_id': 'IN-current-candidate', 'output': {'candidates': [proposal]},
                  'extensions': extension, 'owns_response': False}
        with self.assertRaisesRegex(ValueError, "^invalid task occurrence condition: '/outcome'$"):
            engine._apply_bundle_candidate(deepcopy(engine.instance), deepcopy(engine.runtime), bundle,
                action={'role': 'research_preparation'}, execution_id='EX-current-author', extensions=extension)
        self.assertEqual((engine.head, engine.instance, engine.runtime), before)

    def test_actual_input_seal_excludes_a_later_task_and_binds_same_response_siblings(self):
        from support.planning_contract_inputs import issue_preparation, produce_task
        from support.role_answers import candidate
        from support.engine_lifecycle import research_grant
        engine = self.engine
        earlier = produce_task(self.sim, 'Earlier input task')
        _ended_execution(engine, 'EX-fixed-input-author', 'research_preparation')
        execution = engine.runtime['executions']['EX-fixed-input-author']
        execution.update(input_snapshot=engine.head, extensions={})
        issue_preparation(self.sim, execution)
        fixed, _ = engine._issued_input(execution, with_schema=False)
        self.assertIn(earlier, fixed['available_input_refs'])
        later = produce_task(self.sim, 'Later unpublished-to-author task')
        reread, _ = engine._issued_input(engine.runtime['executions'][execution['id']], with_schema=False)
        self.assertEqual(reread, fixed)
        self.assertNotIn(later, fixed['available_input_refs'])
        self.assertNotIn(later, fixed['supplied_record_ids'])

        def wire(title, refs):
            row = candidate(title, refs=refs)
            row['reuse'] = []
            row['profile_refs'] = deepcopy(engine.instance['role_profile_refs']['research_work'])
            row['authority_refs'] = [research_grant(engine)]
            return row

        def apply(rows):
            instance, runtime = deepcopy(engine.instance), deepcopy(engine.runtime)
            bundle = {'integration_id': 'IN-fixed-input-tasks', 'output': {'candidates': rows},
                      'extensions': {}, 'owns_response': False}
            engine._apply_bundle_candidate(instance, runtime, bundle,
                action={'role': 'research_preparation'}, execution_id=execution['id'], extensions={})
            return instance, runtime

        before = deepcopy((engine.instance, engine.runtime))
        head = engine.head
        with self.assertRaisesRegex(ValueError, 'unknown: ' + later + '$'):
            apply([wire('Cannot cite a later task', [later])])
        self.assertEqual((engine.instance, engine.runtime), before)
        self.assertEqual(engine.head, head)
        instance, runtime = apply([wire('Same response first', [earlier, 'context:goal', 'source:future.txt']),
                                   wire('Same response second', ['Same response first'])])
        first = next(t for t in runtime['tasks'].values() if t['title'] == 'Same response first')
        second = next(t for t in runtime['tasks'].values() if t['title'] == 'Same response second')
        self.assertEqual(first['inputs'], [earlier, 'context:goal', 'source:future.txt'])
        self.assertEqual(second['inputs'], [first['id']])
        engine.store.validate_candidate(instance, runtime, head)
        self.assertEqual((engine.instance, engine.runtime), before)
        self.assertEqual(engine.head, head)

    def test_actual_engine_candidate_and_review_receiver_round_trip(self):
        from do_math.contracts import TASK_CANDIDATE
        from do_math.execution_profiles import profile_ref
        from jsonschema import Draft202012Validator
        from support.role_answers import candidate, review_items
        from support.engine_lifecycle import research_grant
        engine = self.engine
        wire = candidate()
        profile = next(p for p in engine.instance['execution_profiles'].values()
                       if p['role'] == 'research_work' and p['ai']['tier'] == 'high')
        wire['profile_refs'] = [profile_ref(profile)]
        wire['authority_refs'] = [research_grant(engine)]
        Draft202012Validator(TASK_CANDIDATE).validate(wire)
        # No ID/revision or approval basis is patched into this actual receiver input.
        # The author's archived issued input fixes which task inputs it could name.
        self.preparation('EX-author', {'available_input_refs': [], 'supplied_record_ids': []})
        _ended_execution(engine, 'EX-review', 'task_contract_review')
        engine._apply({'role': 'research_preparation'}, {'candidates': [wire]}, 'EX-author', owns_response=False)
        task, = engine.runtime['tasks'].values()
        self.assertEqual(task['revision'], 1)
        self.assertEqual(task['profile_refs'], wire['profile_refs'])
        engine._apply({'role': 'task_contract_review', 'target': task['id']}, review_items(['S']), 'EX-review',
                      owns_response=False)
        engine._save()
        self.sim.restart()
        task = self.sim.runtime['tasks'][task['id']]
        self.assertTrue(planning.contract_review_current(task['reviews'][-1], task, self.sim.instance, self.sim.runtime)['valid'])
        self.assertEqual(planning.task_ready(task, self.sim.instance, self.sim.runtime, evaluation_context=self.sim.engine._evaluation_context())['state'], 'ready')

    def test_engine_preserves_primary_dependency_when_extension_only_sets_condition(self):
        from copy import deepcopy
        from support.role_answers import candidate
        from support.default_responder import common
        engine = self.engine
        prior = task(engine, 'TK-prior')
        engine._save()
        proposal = candidate('Followup')
        # The author binds a permitted work profile it was given (research_fixtures.bind_candidates).
        proposal['profile_refs'] = deepcopy(prior['profile_refs'])
        proposal['dependencies'] = [prior['id']]
        self.preparation('EX-prepare', {'available_input_refs': [], 'supplied_record_ids': []},
                         {'task_conditions': [{'task_title': 'Followup', 'occurrence_condition': {'op': 'always'}}]})
        engine._apply({'role': 'research_preparation'}, {**common('research_preparation'), 'candidates': [proposal]},
                      'EX-prepare')
        applied = next(t for t in engine.runtime['tasks'].values() if t.get('title') == 'Followup')
        self.assertEqual(applied['dependencies'], [prior['id']])
        self.assertEqual(applied['occurrence_condition']['args'][1]['task_id'], prior['id'])


class ContractVerdictReceivers(unittest.TestCase):
    def test_each_contract_verdict_is_stored_and_replayed_without_a_second_effect(self):
        from do_math import contracts, integration
        from support.default_responder import common
        from support.planning_contract_inputs import prepared_sim, only_task, produce_task
        from support.role_answers import review_items
        from support.wait_reporting import assert_task_wait_report
        decisions = contracts.REVIEW_ITEM['properties']['decision']['enum']
        self.assertEqual(set(decisions), {'approved', 'revision_required', 'unresolved'})
        for decision in decisions:
            with self.subTest(decision=decision):
                sim = prepared_sim()
                engine = sim.engine
                task_id = only_task(sim)['id']
                clear_work(sim)
                eid = 'EX-verdict-' + decision
                _ended_execution(engine, eid, 'task_contract_review')
                action = {**engine.runtime['executions'][eid]['action'], 'target': task_id}
                engine.runtime['executions'][eid]['action'] = deepcopy(action)
                engine.runtime['executions'][eid].update(input_snapshot=engine.head,
                    contract_sha256=planning.contract_hash(engine.runtime['tasks'][task_id]),
                    **engine._governance_revisions())
                output = {**common('task_contract_review'), **review_items([task_id], decision=decision,
                    next_owner='research_preparation', findings=[] if decision == 'approved' else ['계약 근거 보완'])}
                extensions = {}
                source_ref = 'runtime/artifacts/BA-' + eid + '/output.json'
                if decision == 'unresolved':
                    output['questions'] = ['Retrieve the missing contract judgment evidence']
                    extensions = {'question_routes': [{'question_index': 0, 'owner': 'operations',
                        'target_ids': [task_id], 'blocks': True, 'reason': 'The supplied judgment evidence is unavailable',
                        'review_item_ids': list(contracts.CONTRACT_REVIEW_ITEMS),
                        'obligation': {'kind': 'input_retrieval', 'subject_ref': task_id, 'requirement_ref': 'contract-evidence'}}]}
                from do_math.canonical import canonical_json
                artifacts = {source_ref: canonical_json(output)}
                context = {'action': action, 'execution_id': eid, 'snapshot': engine.head,
                    'tasks': list(engine.runtime['tasks'].values())}
                def apply(instance, runtime, bundle):
                    engine._apply_bundle_candidate(instance, runtime, bundle,
                        action=action, execution_id=eid, extensions=extensions, question_source_ref=source_ref)
                def publish(instance, runtime, bundle, validated):
                    engine.instance, engine.runtime = instance, runtime
                    engine._save(artifacts)
                callbacks = {'apply_bundle': apply,
                    'validate_current': lambda i, r, b: engine._validate_bundle_current(i, r, b,
                        action=action, execution_id=eid, context=context),
                    'validate_candidate': lambda i, r, b: engine._validate_bundle_candidate(i, r, b, artifacts=artifacts),
                    'publish': publish}
                first = integration.apply_bundles(engine.instance, engine.runtime, output, extensions, context,
                    execution_id=eid, **callbacks)
                self.assertEqual(first['status'], 'accepted', first['issues'])
                current = engine.runtime['tasks'][task_id]
                self.assertEqual(current['reviews'][-1]['decision'], decision)
                self.assertEqual(current['reviews'][-1]['execution_id'], eid)
                preparations = [a for a in engine.runtime['queue'] if a['role'] == 'research_preparation']
                self.assertEqual(len(preparations), int(decision == 'revision_required'))
                if decision == 'approved':
                    self.assertEqual(current['status'], 'planned')
                    self.assertNotIn('waiting', current)
                elif decision == 'revision_required':
                    self.assertEqual(current['waiting']['basis_ref'], eid)
                    self.assertEqual(preparations[0]['contract_review_execution'], eid)
                    assert_task_wait_report(self, engine, task_id)
                else:
                    self.assertNotIn('revision_requested', current)
                    self.assertEqual(current['waiting']['kind'], 'contract_review_input')
                    self.assertEqual(len([a for a in engine.runtime['queue'] if a.get('question_ids')]), 1)
                    self.assertEqual(planning.task_ready(current, engine.instance, engine.runtime,
                        evaluation_context=engine._evaluation_context())['state'], 'not_ready')
                before = deepcopy(engine.store.load())
                second = integration.apply_bundles(engine.instance, engine.runtime, output, extensions, context,
                    execution_id=eid, **callbacks)
                self.assertEqual(second['bundles'][0]['status'], 'already_accepted', second['issues'])
                self.assertEqual(engine.store.load(), before)
                self.assertEqual((second['instance'], second['runtime']), before[1:])
                sim.restart()
                self.assertEqual(sim.runtime['tasks'][task_id], before[2]['tasks'][task_id])
                if decision == 'revision_required':
                    produce_task(sim, '수정 계약', revises=task_id)
                    self.assertNotIn('waiting', sim.runtime['tasks'][task_id])
                    self.assertEqual(sim.runtime['tasks'][task_id]['reviews'][-1]['decision'], 'approved')


if __name__ == '__main__':
    unittest.main(verbosity=2)
