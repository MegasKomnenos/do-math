"""Regression paths for the 2026-09-23 static walkthrough.

Model answers and compiler evidence are fixtures. Git, receipt application,
registration, activity transitions and queued followups use their real owners.
"""
from copy import deepcopy
from datetime import datetime, timedelta
import errno
import hashlib
import json
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import Mock, patch

from do_math import activities, contracts, governance, integration, knowledge_io, planning, revisions, submission, task_contracts
from do_math.engine import ResearchEngine, control, now
from do_math.repository import new_id
from test_categories import test_group
from test_knowledge import candidate
from test_purpose_engine import ActiveStateHarness, theorem
import test_redesign_ENGINE
from test_redesign_ENGINE import routing_engine


@test_group('unit')
class RepetitionReceiptTests(unittest.TestCase):
    def test_dependency_impact_keeps_execution_and_activity_receipts_unchanged(self):
        from do_math import knowledge
        instance = {'knowledge': {'KN': {'id': 'KN', 'family': 'knowledge'}}}
        runtime = {'executions': {'EX': {'id': 'EX', 'status': 'ended', 'outcome': 'output_accepted'}},
                   'activities': {'AY': {'id': 'AY', 'status': 'finished'}}, 'queue': []}
        _, changed = knowledge._apply_impact_effects(instance, runtime, {'EX', 'AY'}, {'KN'},
                                                    reason='Source changed', impact_digest='a' * 64)
        self.assertEqual(changed['executions'], runtime['executions'])
        self.assertEqual(changed['activities'], runtime['activities'])
        self.assertEqual(changed['history'][-1]['affected_ids'], ['AY', 'EX'])

    def test_released_incidental_insights_plan_only_preserved_items(self):
        for valid in (True, False):
            engine = routing_engine()
            engine.instance = knowledge_io.ensure_ontology(engine.instance)
            engine._apply_queue_plan = Mock()
            engine._apply_academic_resolutions = Mock()
            engine.runtime['executions'] = {'EX-old': {'id': 'EX-old', 'status': 'ended'},
                'EX-current': {'id': 'EX-current', 'status': 'ended', 'extensions': {}}}
            engine.runtime['review_cycles'] = {'RC': {'status': 'completed'}}
            engine.runtime['private_insights'] = {'RC': [{'source_execution': 'EX-old',
                'kind': 'question' if valid else 'unregistered', 'title': 'Question ' + str(i),
                'statement': 'What remains?', 'summary': 'A retained question', 'evidence_ids': []} for i in range(3)]}
            engine._apply_extensions({'role': 'identity_review', 'review_cycle_id': 'RC'}, 'EX-current')
            plans = [a for a in engine.runtime['queue'] if a['role'] == 'research_plan']
            self.assertEqual(len(plans), int(valid))
            if valid:
                self.assertEqual(set(plans[0]['evidence_refs']), set(engine.instance['knowledge']))
                self.assertEqual(len(plans[0]['evidence_refs']), 3)
            else:
                self.assertEqual(engine.instance['knowledge'], {})

    def test_collected_checkpoint_keeps_exact_resume_reference(self):
        from do_math.observations import recovered_checkpoint, bind_checkpoint_artifact
        value = {'current_claim': 'Partial claim', 'evidence_paths': [], 'attempts': ['Compared the definitions'],
                 'remaining_work': ['Finish the argument'], 'next_step': 'Check the remaining case',
                 'progress_state': 'working', 'counters': {}}
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            raw = json.dumps(value).encode()
            (workspace / 'checkpoint.json').write_bytes(raw)
            checkpoint = recovered_checkpoint(workspace)
        self.assertEqual(checkpoint['kind'], 'worker_checkpoint')
        entry = {'path': 'checkpoint.json', 'artifact_ref': 'runtime/artifacts/BA/files/checkpoint.json',
                 'sha256': hashlib.sha256(raw).hexdigest()}
        bound = bind_checkpoint_artifact(checkpoint, [entry])
        self.assertEqual(bound['artifact_ref'], entry['artifact_ref'])
        self.assertNotIn('artifact_ref', bind_checkpoint_artifact(checkpoint, [{**entry, 'sha256': 'wrong'}]))
        self.assertEqual(bind_checkpoint_artifact(checkpoint, [], bound)['artifact_ref'], entry['artifact_ref'])

    def test_retry_waits_for_unknown_effect_from_an_ancestor(self):
        engine = routing_engine()
        engine.runtime['executions'] = {
            'EX-original': {'id': 'EX-original', 'status': 'ended', 'action': {}},
            'EX-later': {'id': 'EX-later', 'status': 'ended', 'continuation_of': 'EX-original', 'action': {}}}
        engine.runtime['external_operations'] = {'EO-one': {
            'status': 'unknown', 'producer_executions': ['EX-original']}}
        record = {'id': 'OD', 'execution_id': 'EX-review', 'target_execution_id': 'EX-later',
                  'disposition': {'kind': 'retry'}}
        with self.assertRaisesRegex(ValueError, 'reconciliation'):
            engine._complete_operational_disposition(record)
        self.assertEqual(engine.runtime['queue'], [])

    def test_legacy_threshold_keeps_user_authority_without_rewriting_history(self):
        historical = {'kind': 'repetition_hold', 'lineage': 'selection_failure', 'lineage_id': 'basis',
                      'event_ref': 'EX-failed', 'owner': 'ai', 'next_owner': 'operational_review', 'count': 2, 'limit': 2}
        runtime = {'history': [deepcopy(historical)]}
        current = revisions.repetition_hold({}, runtime, 'selection_failure', 'basis')
        self.assertEqual((current['owner'], current['next_owner']), ('user', 'user'))
        self.assertEqual(runtime['history'], [historical])

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
        helper = test_redesign_ENGINE.IntentConnections()
        bundle, check_action = helper.make_import(engine)
        engine._apply(check_action, helper.verdict(bundle, 'revision_required', False), 'EX-check')
        rework = next(a for a in engine.runtime['queue'] if a.get('stage') == 'interpret')
        revisions.bind_repetition_bases(engine.instance, engine.runtime, rework)
        engine.runtime['executions']['EX-rework'] = {'role': rework['role'], 'action': deepcopy(rework)}
        revisions.record_import_rework(engine.instance, engine.runtime, rework, 'EX-rework')
        revisions.record_import_rework(engine.instance, engine.runtime, rework, 'EX-rework')
        counts = task_contracts.repetition_lineages(engine.instance, engine.runtime)
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
        self.assertEqual(task_contracts.repetition_lineages(instance, runtime)['selection_failure']['count'], 3)
        for kind in ('currentness_changed', 'capacity_wait', 'input_overflow', 'provider_failure', 'publication_failure'):
            runtime['executions'][kind] = {'role': action['role'], 'error_kind': kind}
            revisions.record_execution_outcome(instance, runtime, action, {}, kind, accepted=False)
        self.assertEqual(task_contracts.repetition_lineages(instance, runtime)['selection_failure']['count'], 3)
        runtime['executions']['EX-good'] = {'role': action['role']}
        revisions.record_execution_outcome(instance, runtime, action, {}, 'EX-good', accepted=True)
        self.assertEqual(task_contracts.repetition_lineages(instance, runtime)['selection_failure']['count'], 0)

    def test_generation_time_uses_fixed_machine_observation_and_excludes_supplement(self):
        action = {'role': 'research_preparation'}
        schema = contracts.action_schema(action, {})
        self.assertIn('regenerate_after', schema['required'])
        supplemental = contracts.action_schema({**action, 'assessment_targets': {}}, {})
        self.assertNotIn('regenerate_after', supplemental['properties'])
        context = {'action': action, 'observed_at': '2026-09-23T00:00:00Z',
                   'tasks': [], 'kind_definitions': {}, 'knowledge_catalog': [], 'available_input_refs': []}
        output = {'summary': 'No candidates', 'used_sources': [], 'questions': [], 'candidates': []}
        with tempfile.TemporaryDirectory() as directory:
            for time, invalid in (('2026-09-23T01:00:00Z', False), ('2026-09-22T23:00:00Z', True),
                                  ('2026-09-23T01:00:00', True)):
                issues = submission._payload_issues({**output, 'regenerate_after': time}, schema, context, {}, Path(directory))
                self.assertEqual(any(i.get('rule_id') == 'submission.regeneration_time' for i in issues), invalid, issues)

    def test_accepted_batch_opens_one_plan_and_preserves_all_evidence(self):
        for count in (3, 1, 0):
            engine = routing_engine()
            engine.instance = knowledge_io.ensure_ontology(engine.instance)
            engine.runtime['tasks']['TK'] = {'id': 'TK', 'results': [], 'status': 'active'}
            engine.runtime['executions']['EX'] = {'id': 'EX', 'role': 'research_work', 'status': 'running', 'extensions': {}}
            output = {'summary': 'Report', 'questions': [], 'used_sources': [], 'outcome': 'partial', 'report': 'Actual report',
                'remaining_work': ['Open obligation'], 'checkpoint': '', 'relations': [],
                'knowledge': [candidate(title='K' + str(i), lean_code='', declaration_names=[]) for i in range(count)]}
            engine._apply({'id': 'AC', 'role': 'research_work', 'target': 'TK'}, output, 'EX')
            plans = [a for a in engine.runtime['queue'] if a['role'] == 'research_plan']
            self.assertEqual(len(plans), 1, plans)
            self.assertEqual(set(plans[0]['evidence_refs']), set(engine.instance['knowledge']))
            self.assertEqual(plans[0]['receipt_refs'], ['EX'])
        _, runtime, _ = knowledge_io.import_candidate({}, {}, candidate(lean_code='', declaration_names=[]),
            source_ref='source', actor_ref='user')
        self.assertEqual([a['role'] for a in runtime['queue']], ['research_plan'])
        _, runtime, _ = knowledge_io.import_candidate({}, {}, candidate(), source_ref='source', actor_ref='user', plan_nonformal=False)
        self.assertEqual([a['role'] for a in runtime['queue']], ['formal_check'])


class WalkthroughEngineTests(ActiveStateHarness):
    def test_failed_review_slot_keeps_its_live_sibling_running(self):
        engine, runner = self.make()
        engine.runtime['queue'] = []
        engine._knowledge_io_control({'action': 'knowledge', 'id': new_id('UC'),
            'config': {'operation': 'import', 'candidate': theorem()}})
        formal = next(a for a in engine.runtime['queue'] if a['role'] == 'formal_check')
        engine._save()
        engine._formal(formal)
        engine._start_identity_review(formal['target'])
        scope = next(a for a in engine.runtime['queue'] if a['role'] == 'identity_review')
        engine._call(scope)
        engine.runtime['queue'] = [a for a in engine.runtime['queue'] if a['role'] == 'identity_review']
        self.assertEqual({a['slot'] for a in engine.runtime['queue']}, {'initial-0', 'initial-1'})
        release = threading.Event()
        answer = runner.answer
        def wait_for_sibling(role, context, workspace):
            if role == 'identity_review' and context['action']['slot'] == 'initial-0':
                self.assertTrue(release.wait(60), 'Sibling preparation never reached its restoration failure')
            return answer(role, context, workspace)
        runner.answer = wait_for_sibling
        prepare = engine._prepare_review_context
        mkdir = Path.mkdir
        observed = []
        def busy(path, *args, **kwargs):
            if 'review-sources' in path.parts:
                raise OSError(errno.EBUSY, 'Only this review slot cannot materialize its input')
            return mkdir(path, *args, **kwargs)
        def prepare_slot(action, workspace, **kwargs):
            if action.get('slot') != 'initial-1':
                return prepare(action, workspace, **kwargs)
            observed.append(any(e.get('action', {}).get('slot') == 'initial-0' and e['status'] != 'ended'
                                for e in engine.runtime['executions'].values()))
            try:
                with patch.object(Path, 'mkdir', busy):
                    return prepare(action, workspace, **kwargs)
            finally:
                release.set()
        with patch.object(engine, '_prepare_review_context', side_effect=prepare_slot):
            engine._save()
            engine.run(max_steps=2)
        self.assertEqual(observed, [True])
        first = next(e for e in engine.runtime['executions'].values() if e.get('action', {}).get('slot') == 'initial-0')
        self.assertEqual(first['outcome'], 'output_accepted', first.get('error'))
        held = next(w for w in engine.runtime['waiting_actions'].values() if w['action'].get('slot') == 'initial-1')
        self.assertEqual(held['kind'], 'review_input_restoration')

    def test_empty_preparation_preserves_machine_time_and_opens_one_due_regeneration(self):
        from test_engine import ScriptedRunner
        engine, _ = self.make()
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
        from test_native_final_submission import native_result
        from do_math.repository import canonical_json
        from do_math.execution_lifecycle import transition_execution
        engine, _ = self.make(selection_failure_limit=3)
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
            execution.update(grant_id=action['grant_id'], input_snapshot=engine.head, input_bundle=bundle)
            execution.update(planning.governance_revisions(engine.instance))
            from do_math.input_basis import capture_decision_basis
            execution['decision_basis'] = capture_decision_basis(engine.instance, engine.runtime, engine._decision_references(action))
            workspace = Path(engine.instance['workspace']) / 'runs' / eid / 'workspace'
            workspace.mkdir(parents=True)
            context = engine._context(action, workspace, execution_id=eid)
            schema = engine._response_schema(action)
            submission.install_tools(workspace, context, schema, engine.instance['config']['max_artifact_bytes'])
            prefix = 'runtime/artifacts/' + bundle
            engine._save({prefix + '/input/submission/context.json': canonical_json(context),
                          prefix + '/schema.json': canonical_json(schema), prefix + '/input.txt': b'exact sealed prompt'})
            execution = engine.runtime['executions'][eid]
            result = native_result(execution, context, raw, workspace)
            result = engine._collect_submitted_result(execution, result, context, schema, workspace)
            self.assertIn('rejected_submission', result, result.get('error'))
            transition_execution(engine.runtime['executions'][eid], 'stopping', at=now(), stop_phase='terminating')
            engine._receive_submission(action, result, eid, context, schema, workspace)
            failure = engine.runtime['executions'][eid]
            self.assertEqual(failure['error_kind'], expected, failure.get('integration_result'))
            receipts = [r for r in engine.runtime['history'] if r.get('kind') == 'task_repetition'
                        and r.get('lineage') == 'selection_failure']
            self.assertEqual(len(receipts), index + 1)
            self.assertEqual(receipts[-1]['outcome'], 'rejected')
            self.assertEqual(task_contracts.repetition_lineages(engine.instance, engine.runtime)['selection_failure']['count'], index + 1)
        hold = revisions.repetition_hold(engine.instance, engine.runtime, 'selection_failure', receipts[-1]['lineage_id'])
        self.assertEqual(hold['owner'], 'user')
        engine._save()

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

    def test_public_continue_releases_exact_hold_and_replay_is_idempotent(self):
        engine, _ = self.make(selection_failure_limit=1)
        target = self.seed_plan(engine)
        action = activities.continue_activity(engine.runtime, target['id'], at=now(), reason='Retry held plan')
        lineage = action['repetition_bases']['selection_failure']
        revisions.record_repetition(engine.instance, engine.runtime, lineage='selection_failure', lineage_id=lineage,
            event_ref=target['id'], outcome='rejected', owner='ai', reason='Missing population')
        hold = revisions.repetition_hold(engine.instance, engine.runtime, 'selection_failure', lineage)
        self.assertEqual(hold['owner'], 'user')
        self.assertTrue(revisions.action_repetition_waits(engine.instance, engine.runtime, action))
        engine._save()
        change = {'kind': 'repetition_continue', 'decision_id': new_id('DC'), 'lineage': 'selection_failure',
            'lineage_id': lineage, 'hold_event_ref': hold['event_ref'], 'allowed_action': revisions.action_scope(action)}
        control(self.repo, engine.instance['id'], 'decision', config={'change': change}, text='Continue this held plan.')
        engine.process_controls()
        self.assertFalse(revisions.action_repetition_waits(engine.instance, engine.runtime, action))
        self.assertEqual(task_contracts.repetition_lineages(engine.instance, engine.runtime)['selection_failure']['count'], 0)
        stored = engine.instance['decisions'][change['decision_id']]
        _, replay, _ = governance.apply_decision(engine.instance, engine.runtime, change, source_ref=stored['source_ref'])
        self.assertEqual(replay['history'], engine.runtime['history'])
        stale = {**change, 'decision_id': new_id('DC')}
        with self.assertRaisesRegex(ValueError, 'current repetition hold'):
            governance.apply_decision(engine.instance, engine.runtime, stale, source_ref=stored['source_ref'])

    def test_operational_retry_is_idempotent_and_waits_for_user_at_the_limit(self):
        engine, _ = self.make(selection_failure_limit=1)
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
        from test_native_final_submission import native_result
        from do_math.repository import canonical_json
        bundle = new_id('BA')
        assessor.update(grant_id=review_action['grant_id'], input_snapshot=engine.head, input_bundle=bundle,
                        **planning.governance_revisions(engine.instance))
        from do_math.input_basis import capture_decision_basis
        assessor['decision_basis'] = capture_decision_basis(engine.instance, engine.runtime, engine._decision_references(review_action))
        workspace = Path(engine.instance['workspace']) / 'runs' / assessor['id'] / 'workspace'
        workspace.mkdir(parents=True)
        context = engine._context(review_action, workspace, execution_id=assessor['id'])
        schema = engine._response_schema(review_action)
        submission.install_tools(workspace, context, schema, engine.instance['config']['max_artifact_bytes'])
        prefix = 'runtime/artifacts/' + bundle
        engine._save({prefix + '/input/submission/context.json': canonical_json(context),
                      prefix + '/schema.json': canonical_json(schema), prefix + '/input.txt': b'exact sealed prompt'})
        assessor = engine.runtime['executions'][assessor['id']]
        result = native_result(assessor, context, json.dumps(output).encode(), workspace)
        result = engine._collect_submitted_result(assessor, result, context, schema, workspace)
        self.assertEqual(result['status'], 'completed', result.get('error'))
        from do_math.execution_lifecycle import transition_execution
        transition_execution(engine.runtime['executions'][assessor['id']], 'stopping', at=now(), stop_phase='terminating')
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

    def test_review_materialization_failure_ends_preparation_and_saves_recovery(self):
        engine, _ = self.make()
        engine.runtime['queue'] = []
        engine._knowledge_io_control({'action': 'knowledge', 'id': new_id('UC'),
            'config': {'operation': 'import', 'candidate': theorem()}})
        formal = next(a for a in engine.runtime['queue'] if a['role'] == 'formal_check')
        engine._save()
        engine._formal(formal)
        kid = formal['target']
        engine._start_identity_review(kid)
        action = next(a for a in engine.runtime['queue'] if a['role'] == 'identity_review')
        original = Path.mkdir
        def unavailable(path, *args, **kwargs):
            if 'review-sources' in path.parts:
                raise OSError(errno.EBUSY, 'Regression source materialization busy')
            return original(path, *args, **kwargs)
        with patch.object(Path, 'mkdir', unavailable):
            engine._call(action)
        attempts = [e for e in engine.runtime['executions'].values() if e.get('action', {}).get('id') == action['id']]
        self.assertEqual(len(attempts), 1)
        self.assertEqual(attempts[0]['status'], 'ended')
        wait = engine.runtime['waiting_actions'][action['id']]
        self.assertEqual(wait['kind'], 'review_input_restoration')
        self.assertEqual(wait['next_owner'], 'review_recovery')
        _, _, saved = engine.store.load()
        self.assertEqual(saved['waiting_actions'][action['id']], wait)
        outcome = engine._retry_review_restoration(wait['action'], self.root / 'restored', at=now())
        self.assertEqual(outcome['disposition'], 'review_resumed')
        self.assertNotIn(action['id'], engine.runtime['waiting_actions'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
