"""Repetition lineages: how repeated generations, reworks and receiver failures are counted, held and released (``do_math.revisions``).

Model answers are fixtures. Receipt application, activity transitions and
queued followups are the product's.
"""
import hashlib
import json
import sys
import tempfile
import unittest
from copy import deepcopy
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math import (activities, contracts, governance, integration, planning, revisions, submission,
                     task_contracts)
from do_math.engine import control, ResearchEngine
from do_math.file_io import now
from do_math.repository import new_id
from engine_fixtures import intent_import, intent_verdict, routing_engine
from purpose_fixtures import ActivatedPurposeHarness


class RepetitionLineageTests(unittest.TestCase):
    def test_continue_after_successful_empty_preparation_creates_its_missing_request(self):
        engine = routing_engine()
        engine.instance['config']['exhaustion_empty_limit'] = 1
        engine.instance['governance_sources'] = {'UI-source': governance.preserve_source(
            'UI-source', 'Continue the held empty preparation.', origin='user')}
        original = {'id': 'AC-original', 'role': 'research_preparation'}
        revisions.bind_repetition_bases(engine.instance, engine.runtime, original)
        engine.runtime['executions']['EX-empty'] = {'id': 'EX-empty', 'role': 'research_preparation',
            'status': 'ended', 'outcome': 'output_accepted', 'action': original}
        revisions.record_execution_outcome(engine.instance, engine.runtime, original,
            {'summary': 'No candidate'}, 'EX-empty', accepted=True)
        key = original['repetition_bases']['exhaustion_empty']
        allowed = {'id': 'AC-next', 'role': 'research_preparation', 'revision_targets': {},
                   'repetition_bases': {'exhaustion_empty': key}}
        change = {'kind': 'repetition_continue', 'decision_id': 'DC-continue', 'lineage': 'exhaustion_empty',
                  'lineage_id': key, 'hold_event_ref': 'EX-empty', 'allowed_action': allowed}
        instance, runtime, _ = governance.apply_decision(engine.instance, engine.runtime, change, source_ref='UI-source')
        self.assertEqual([a['id'] for a in runtime['queue']], ['AC-next'])
        self.assertFalse(revisions.action_repetition_waits(instance, runtime, runtime['queue'][0]))
        self.assertEqual(revisions.action_scope(runtime['queue'][0]), allowed)

    def test_supplement_does_not_increment_or_reset_empty_generation(self):
        instance = {'id': 'RI', 'config': {}}
        runtime = {'tasks': {}, 'queue': [], 'history': [], 'executions': {}}
        revisions.record_repetition(instance, runtime, lineage='exhaustion_empty', lineage_id='basis',
            event_ref='EX-empty', outcome='empty', owner='ai', reason='No candidates')
        before = deepcopy(runtime['history'])
        for field in ('assessment_targets', 'observation_rule_targets'):
            action = {'role': 'research_preparation', field: {'TK': {}}}
            runtime['executions']['EX-supplement'] = {'role': action['role']}
            revisions.record_execution_outcome(instance, runtime, action, {'summary': 'Supplement applied'},
                                               'EX-supplement', accepted=True)
        self.assertEqual(runtime['history'], before)
        runtime['history'].append({'kind': 'repetition_hold', 'lineage': 'exhaustion_empty',
            'lineage_id': 'basis', 'event_ref': 'EX-empty', 'owner': 'user'})
        action.update(repetition_bases={'exhaustion_empty': 'basis'}, observation_rule_targets={})
        self.assertFalse(revisions.action_repetition_waits(instance, runtime, action))
        runtime['tasks']['TK'] = {'id': 'TK'}
        runtime['history'].append({'kind': 'repetition_hold', 'lineage': 'contract_revision',
            'lineage_id': 'TK', 'event_ref': 'EX-revision', 'owner': 'user'})
        action['observation_rule_targets'] = {'TK': {}}
        self.assertEqual([row['lineage'] for row in revisions.action_repetition_waits(instance, runtime, action)], ['contract_revision'])

    def test_real_intent_rework_producer_keeps_original_lineage(self):
        engine = routing_engine()
        bundle, check_action = intent_import(engine)
        engine._apply(check_action, intent_verdict(bundle, 'revision_required', False), 'EX-check')
        rework = next(a for a in engine.runtime['queue'] if a.get('stage') == 'interpret')
        revisions.bind_repetition_bases(engine.instance, engine.runtime, rework)
        engine.runtime['executions']['EX-rework'] = {'role': rework['role'], 'action': deepcopy(rework)}
        revisions.record_import_rework(engine.instance, engine.runtime, rework, 'EX-rework')
        revisions.record_import_rework(engine.instance, engine.runtime, rework, 'EX-rework')
        counts = task_contracts.repetition_lineages(engine.runtime)
        self.assertEqual(counts['import_rework']['count'], 1)
        retry = {**deepcopy(rework), 'id': 'AC-next', 'previous_import_id': 'IM-next'}
        retry.pop('repetition_bases')
        revisions.bind_repetition_bases(engine.instance, engine.runtime, retry)
        self.assertEqual(retry['repetition_bases'], rework['repetition_bases'])
        check = {**rework, 'stage': 'check', 'continuation_of': 'EX-check'}
        self.assertFalse(revisions.import_rework(engine.runtime, check))
        engine.instance['config']['import_rework_limit'] = 1
        later = deepcopy(rework)
        revisions.record_repetition(engine.instance, engine.runtime, lineage='import_rework',
            lineage_id=rework['repetition_bases']['import_rework'], event_ref='EX-rework-2',
            outcome='reauthored', owner='ai', reason='Second registered reauthor')
        self.assertTrue(revisions.action_repetition_waits(engine.instance, engine.runtime, later))
        self.assertFalse(revisions.action_repetition_waits(engine.instance, engine.runtime, check))
        other = {**later, 'target': 'UC-unrelated'}
        other.pop('repetition_bases')
        revisions.bind_repetition_bases(engine.instance, engine.runtime, other)
        self.assertFalse(revisions.action_repetition_waits(engine.instance, engine.runtime, other))

    def test_receiver_failure_categories_count_once_and_success_ends_streak(self):
        instance = {'id': 'RI', 'config': {}}
        runtime = {'queue': [], 'executions': {}, 'history': []}
        action = {'role': 'research_plan', 'repetition_bases': {'selection_failure': 'basis'}}
        for index, rule in enumerate(('schema.required', 'submission.parse', 'integration.application')):
            eid = 'EX-' + str(index)
            runtime['executions'][eid] = {'role': action['role'], 'error_kind': integration.failure_kind([
                integration.issue(rule, 'output', 'message deliberately contains no classification hints')])}
            for _ in range(2):
                revisions.record_execution_outcome(instance, runtime, action, {}, eid, accepted=False)
        self.assertEqual(task_contracts.repetition_lineages(runtime)['selection_failure']['count'], 3)
        for kind in ('currentness_changed', 'publication_failure', 'input_failure'):
            runtime['executions'][kind] = {'role': action['role'], 'error_kind': kind}
            revisions.record_execution_outcome(instance, runtime, action, {}, kind, accepted=False)
        self.assertEqual(task_contracts.repetition_lineages(runtime)['selection_failure']['count'], 3)
        runtime['executions']['EX-good'] = {'role': action['role']}
        revisions.record_execution_outcome(instance, runtime, action, {}, 'EX-good', accepted=True)
        self.assertEqual(task_contracts.repetition_lineages(runtime)['selection_failure']['count'], 0)

    def test_generation_time_uses_fixed_machine_observation_and_excludes_supplement(self):
        action = {'role': 'research_preparation'}
        schema = contracts.action_schema(action)
        self.assertIn('regenerate_after', schema['required'])
        supplemental = contracts.action_schema({**action, 'assessment_targets': {}})
        self.assertNotIn('regenerate_after', supplemental['properties'])
        context = {'action': action, 'observed_at': '2026-09-23T00:00:00Z',
                   'tasks': [], 'kind_definitions': {}, 'knowledge_catalog': [], 'available_input_refs': []}
        output = {'summary': 'No candidates', 'used_sources': [], 'questions': [], 'candidates': []}
        with tempfile.TemporaryDirectory() as directory:
            for time, invalid in (('2026-09-23T01:00:00Z', False), ('2026-09-22T23:00:00Z', True),
                                  ('2026-09-23T01:00:00', True)):
                issues = submission._payload_issues({**output, 'regenerate_after': time}, schema, context, {}, Path(directory))
                self.assertEqual(any(i.get('rule_id') == 'submission.regeneration_time' for i in issues), invalid, issues)


class RepetitionEngineTests(ActivatedPurposeHarness):
    def seed_plan(self, engine):
        engine.runtime['queue'] = []
        engine._enqueue('research_plan', reason='Regression selection')
        action = engine.runtime['queue'][0]
        execution = engine._register_execution(action, {'id': new_id('EX'), 'role': action['role'], 'status': 'queued'})
        from do_math.execution_lifecycle import end_preparation
        end_preparation(execution, at=now(), stage='context', reason='Fixture original failure', cancelled=False)
        engine._remove_action(action)
        activities.wait_for(engine.runtime, execution['owner_activity_id'], reason='receipt failed',
            condition={'execution_id': execution['id']}, next_owner='operational_review', at=now())
        return execution

    def test_empty_preparation_preserves_machine_time_and_opens_one_due_regeneration(self):
        from runner_fixtures import ScriptedRunner
        engine, _ = self.make_active()
        engine.runtime['queue'] = []
        engine._enqueue('research_preparation', reason='No usable candidate in this fixture')
        engine.runner = ScriptedRunner(preparation_candidates=[])
        engine._save()
        engine.run(max_steps=1)
        receipt = next(r for r in engine.runtime['history'] if r.get('kind') == 'task_repetition'
                       and r.get('lineage') == 'exhaustion_empty')
        execution = engine.runtime['executions'][receipt['event_ref']]
        self.assertEqual(execution['outcome'], 'output_accepted', execution.get('error'))
        self.assertEqual(receipt['observed_at'], execution['observed_at'])
        due = datetime.fromisoformat(receipt['regenerate_after'])
        state = deepcopy(engine.runtime)
        state.update(queue=[], status='active')
        early = planning.exhaustion_state(engine.instance, state, now=(due - timedelta(seconds=1)).isoformat())
        self.assertEqual(early['reasons'], ['regeneration_guard'])
        for _ in range(2):
            planning.schedule_reconsideration(engine.instance, state, now=due.isoformat())
        preparations = [a for a in state['queue'] if a['role'] == 'research_preparation']
        self.assertEqual(len(preparations), 1)

    def test_native_plan_failures_reach_receiver_counter_through_preserved_bytes(self):
        from engine_fixtures import native_result
        from do_math.repository import canonical_json
        from do_math.execution_lifecycle import transition_execution
        engine, _ = self.make_active(selection_failure_limit=3)
        engine.runtime['queue'] = []
        for index, (raw, expected) in enumerate(((b'{broken', 'output_parse'),
                (b'{"summary":"Missing plan fields"}', 'output_schema'),
                (json.dumps({'summary': 'Invalid population', 'used_sources': [], 'questions': [],
                    'dispositions': [{'task_id': 'TK-missing', 'kind': 'not_selected', 'reason': 'Unknown task',
                        'uncertainty': '', 'parallel_task_ids': [], 'expected_research_change': '',
                        'revisit': {'event_refs': [], 'at': '2100-01-01T00:00:00Z'}, 'missing_inputs': [], 'next_owner': 'research_plan'}],
                    'preparation_requests': [], 'goal_audit': False, 'task_assessments': []}).encode(), 'output_contract'))):
            action = {'id': new_id('AC'), 'role': 'research_plan'}
            engine._action_lifecycle_gate(action)
            execution = engine._register_execution(action, {'id': new_id('EX'), 'role': 'research_plan', 'status': 'running'})
            eid = execution['id']
            bundle = new_id('BA')
            prefix = 'runtime/artifacts/' + bundle
            prompt = b'exact sealed prompt'
            # The role input manifest names the archived prompt saved below.
            execution.update(grant_id=action['grant_id'], input_snapshot=engine.head, input_bundle=bundle,
                input_manifest={'prompt': {'artifact_ref': prefix + '/input.txt',
                    'sha256': hashlib.sha256(prompt).hexdigest(), 'bytes': len(prompt)}})
            execution.update(planning.governance_revisions(engine.instance))
            from do_math.input_basis import capture_decision_basis
            execution['decision_basis'] = capture_decision_basis(engine.instance, engine.runtime, engine._decision_references(action))
            workspace = Path(engine.instance['workspace']) / 'runs' / eid / 'workspace'
            workspace.mkdir(parents=True)
            context = engine._context(action, workspace, execution_id=eid)
            schema = engine._response_schema(action)
            submission.install_tools(workspace, context, schema, engine.instance['config']['max_artifact_bytes'])
            engine._save({prefix + '/input/submission/context.json': canonical_json(context),
                          prefix + '/schema.json': canonical_json(schema), prefix + '/input.txt': prompt})
            execution = engine.runtime['executions'][eid]
            result = native_result(execution, context, raw, workspace)
            result = engine._collect_submitted_result(execution, result, context, schema, workspace)
            self.assertIn('rejected_submission', result, result.get('error'))
            transition_execution(engine.runtime['executions'][eid], 'stopping', at=now())
            engine._receive_submission(action, result, eid, context, schema, workspace)
            failure = engine.runtime['executions'][eid]
            self.assertEqual(failure['error_kind'], expected, failure.get('integration_result'))
            receipts = [r for r in engine.runtime['history'] if r.get('kind') == 'task_repetition'
                        and r.get('lineage') == 'selection_failure']
            self.assertEqual(len(receipts), index + 1)
            self.assertEqual(receipts[-1]['outcome'], 'rejected')
            self.assertEqual(task_contracts.repetition_lineages(engine.runtime)['selection_failure']['count'], index + 1)
        hold = revisions.repetition_hold(engine.runtime, 'selection_failure', receipts[-1]['lineage_id'])
        self.assertEqual(hold['owner'], 'user')
        engine._save()

    def test_public_continue_releases_exact_hold_and_replay_is_idempotent(self):
        engine, _ = self.make_active(selection_failure_limit=1)
        target = self.seed_plan(engine)
        action = activities.continue_activity(engine.runtime, target['id'], at=now(), reason='Retry held plan')
        lineage = action['repetition_bases']['selection_failure']
        revisions.record_repetition(engine.instance, engine.runtime, lineage='selection_failure', lineage_id=lineage,
            event_ref=target['id'], outcome='rejected', owner='ai', reason='Missing population')
        hold = revisions.repetition_hold(engine.runtime, 'selection_failure', lineage)
        self.assertEqual(hold['owner'], 'user')
        self.assertTrue(revisions.action_repetition_waits(engine.instance, engine.runtime, action))
        engine._save()
        change = {'kind': 'repetition_continue', 'decision_id': new_id('DC'), 'lineage': 'selection_failure',
            'lineage_id': lineage, 'hold_event_ref': hold['event_ref'], 'allowed_action': revisions.action_scope(action)}
        control(self.repo, engine.instance['id'], 'decision', config={'change': change}, text='Continue this held plan.')
        engine.process_controls()
        self.assertFalse(revisions.action_repetition_waits(engine.instance, engine.runtime, action))
        self.assertEqual(task_contracts.repetition_lineages(engine.runtime)['selection_failure']['count'], 0)
        stored = engine.instance['decisions'][change['decision_id']]
        _, replay, _ = governance.apply_decision(engine.instance, engine.runtime, change, source_ref=stored['source_ref'])
        self.assertEqual(replay['history'], engine.runtime['history'])
        stale = {**change, 'decision_id': new_id('DC')}
        with self.assertRaisesRegex(ValueError, 'current repetition hold'):
            governance.apply_decision(engine.instance, engine.runtime, stale, source_ref=stored['source_ref'])

    def test_operational_retry_is_idempotent_and_waits_for_user_at_the_limit(self):
        engine, _ = self.make_active(selection_failure_limit=1)
        target = self.seed_plan(engine)
        lineage = target['action']['repetition_bases']['selection_failure']
        revisions.record_repetition(engine.instance, engine.runtime, lineage='selection_failure',
            lineage_id=lineage, event_ref=target['id'], outcome='rejected', owner='ai', reason='Held plan failure')
        review_action = {'id': new_id('AC'), 'role': 'operational_review', 'target': target['id']}
        engine._action_lifecycle_gate(review_action)
        assessor = engine._register_execution(review_action, {'id': new_id('EX'), 'role': 'operational_review', 'status': 'running'})
        disposition = {'kind': 'retry', 'basis_refs': [target['id']], 'next_owner': 'research_plan', 'reason': 'Repair selection',
            'scope': 'Same held plan', 'replay_safety': 'No external effects or accepted bundles'}
        output = {'summary': 'Retry', 'questions': [], 'used_sources': [], 'disposition': disposition, 'task_assessments': []}
        from engine_fixtures import native_result
        from do_math.repository import canonical_json
        bundle = new_id('BA')
        prefix = 'runtime/artifacts/' + bundle
        prompt = b'exact sealed prompt'
        # The role input manifest names the archived prompt saved below; the
        # owner's pre-write inspection requires it to exist.
        assessor.update(grant_id=review_action['grant_id'], input_snapshot=engine.head, input_bundle=bundle,
                        input_manifest={'prompt': {'artifact_ref': prefix + '/input.txt',
                            'sha256': hashlib.sha256(prompt).hexdigest(), 'bytes': len(prompt)}},
                        **planning.governance_revisions(engine.instance))
        from do_math.input_basis import capture_decision_basis
        assessor['decision_basis'] = capture_decision_basis(engine.instance, engine.runtime, engine._decision_references(review_action))
        workspace = Path(engine.instance['workspace']) / 'runs' / assessor['id'] / 'workspace'
        workspace.mkdir(parents=True)
        context = engine._context(review_action, workspace, execution_id=assessor['id'])
        schema = engine._response_schema(review_action)
        submission.install_tools(workspace, context, schema, engine.instance['config']['max_artifact_bytes'])
        engine._save({prefix + '/input/submission/context.json': canonical_json(context),
                      prefix + '/schema.json': canonical_json(schema), prefix + '/input.txt': prompt})
        assessor = engine.runtime['executions'][assessor['id']]
        result = native_result(assessor, context, json.dumps(output).encode(), workspace)
        result = engine._collect_submitted_result(assessor, result, context, schema, workspace)
        self.assertEqual(result['status'], 'completed', result.get('error'))
        from do_math.execution_lifecycle import transition_execution
        transition_execution(engine.runtime['executions'][assessor['id']], 'stopping', at=now())
        received = engine._receive_submission(review_action, result, assessor['id'], context, schema, workspace)
        self.assertEqual(received['status'], 'accepted', received.get('issues'))
        record = next(iter(engine.runtime['operational_dispositions'].values()))
        self.assertEqual(record['status'], 'applied')
        retry = next(a for a in engine.runtime['queue'] if a.get('continuation_of') == target['id'])
        self.assertEqual(retry['id'], target['action']['id'])
        self.assertTrue(revisions.action_repetition_waits(engine.instance, engine.runtime, retry))
        restored = ResearchEngine(self.repo, engine.instance['id'])
        restored_retry = next(a for a in restored.runtime['queue'] if a.get('id') == retry['id'])
        self.assertTrue(revisions.action_repetition_waits(restored.instance, restored.runtime, restored_retry))
        engine._complete_operational_disposition(record)
        self.assertEqual(sum(a.get('id') == retry['id'] for a in engine.runtime['queue']), 1)
        change = {'kind': 'repetition_continue', 'decision_id': new_id('DC'), 'lineage': 'selection_failure',
            'lineage_id': lineage, 'hold_event_ref': target['id'], 'allowed_action': revisions.action_scope(retry)}
        control(self.repo, engine.instance['id'], 'decision', config={'change': change}, text='Continue this held plan after diagnosis.')
        engine.process_controls()
        retry = next(a for a in engine.runtime['queue'] if a.get('id') == retry['id'])
        self.assertFalse(revisions.action_repetition_waits(engine.instance, engine.runtime, retry))
        successor = engine._register_execution(retry, {'id': new_id('EX'), 'role': 'research_plan', 'status': 'queued'})
        self.assertEqual(successor['continuation_of'], target['id'])
        self.assertEqual(successor['action']['id'], target['action']['id'])
        self.assertFalse(any(r.get('kind') == 'repetition_repair_authorized' for r in engine.runtime['history']))


if __name__ == "__main__":
    unittest.main()
