"""The engine's side of planning: applying plans and task assessments, readiness refresh and its followups, and the conditions a plan evaluates."""
import hashlib
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import create_autospec, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math import execution_profiles, model_policy, planning
from do_math.initialization import governance_working_view
from do_math.repository import ResearchRepository
from engine_fixtures import context_engine, FakeEngine, reassessment_engine, routing_engine
from research_fixtures import FixtureAdapter


class WorkProfileAdmissionTests(unittest.TestCase):
    def test_policy_change_reprepares_an_unstarted_incompatible_contract(self):
        with tempfile.TemporaryDirectory() as directory, patch('do_math.initialization.adapter_for', return_value=FixtureAdapter()):
            engine=FakeEngine(directory);engine.activate()
            task=engine.task(approved=False)
            task['model_assessment']={'difficulty':'low','importance':'low','reason':'local'}
            low=next(p for p in engine.instance['execution_profiles'].values()
                     if p['role']=='research_work' and p['ai']['tier']=='low')
            task['profile_refs']=[execution_profiles.profile_ref(low)];engine.approve(task)
            engine.instance['config']['role_tiers']['research_work']='high'
            engine._refresh_readiness()
            self.assertEqual(engine._task_readiness[task['id']]['state'],'not_ready')
            self.assertTrue(any(a['role']=='research_preparation' and a.get('target')==task['id']
                                for a in engine.runtime['queue']))
            self.assertFalse(any(a['role']=='task_contract_review' and a.get('target')==task['id']
                                 for a in engine.runtime['queue']))

    def test_reviewed_contract_cannot_be_ready_with_an_inadequate_allowed_profile(self):
        with tempfile.TemporaryDirectory() as directory, patch('do_math.initialization.adapter_for', return_value=FixtureAdapter()):
            engine = FakeEngine(directory)
            engine.activate()
            task = engine.task(approved=False)
            task['model_assessment'] = {'difficulty':'low', 'importance':'high', 'reason':'goal-critical'}
            low = next(p for p in engine.instance['execution_profiles'].values()
                       if p['role']=='research_work' and p['ai']['tier']=='low')
            task['profile_refs'] = [execution_profiles.profile_ref(low)]
            engine.approve(task)
            result = planning.task_ready(task, governance_working_view(engine.instance), engine.runtime)
            self.assertEqual(result['state'], 'not_ready')
            self.assertIn('work profile requirement', result['errors'][0])
            high = next(p for p in engine.instance['execution_profiles'].values()
                        if p['role']=='research_work' and p['ai']['tier']=='high')
            task['profile_refs'] = [execution_profiles.profile_ref(high)]
            engine.approve(task)
            self.assertEqual(planning.task_ready(task, governance_working_view(engine.instance), engine.runtime)['state'], 'ready')
            self.assertEqual(model_policy.work_profile_selection(engine.instance['config'], task,
                engine.instance)['profile_ref'], task['profile_refs'][0])


class PlanningConnections(unittest.TestCase):
    def test_plan_assessment_reaches_assignment_without_changing_contract(self):
        from do_math import execution_profiles, model_policy
        from record_fixtures import approved_task, approve_task, task_disposition
        task, instance, runtime = approved_task()
        engine = context_engine(instance, runtime)
        config = engine.instance['config']
        config['session_limits'] = deepcopy(model_policy.LIMITS)
        config['session_limits']['work'][config['tier_models']['high']] = 0
        config['role_tiers']['research_work'] = 'low'
        engine.instance.update(execution_profiles.build_profiles(config))
        task = engine.runtime['tasks'][task['id']]
        task['profile_refs'] = deepcopy(engine.instance['role_profile_refs']['research_work'])
        task['model_assessment'] = {'difficulty': 'low', 'importance': 'low', 'reason': 'Initial bounded work'}
        approve_task(task, engine.instance, engine.runtime)
        before = deepcopy(task)
        high = {'difficulty': 'high', 'importance': 'high', 'reason': 'New plan needs stronger reasoning'}
        engine.runtime['executions']['EX-plan'] = {'id': 'EX-plan', 'role': 'research_plan', 'status': 'ended',
            'model_decisions': {task['id']: high}}
        engine._apply_task_plan({'dispositions': [task_disposition(task['id'])], 'task_assessments': []},
            'EX-plan', deepcopy(engine.runtime['tasks']), [task['id']])
        action = next(a for a in engine.runtime['queue'] if a['role'] == 'research_work')
        selected = engine._select_model(action)
        self.assertEqual(selected['tier'], 'high')
        self.assertEqual(selected['model'], config['tier_models']['high'])
        self.assertEqual(action['model_assessment'], high)
        self.assertEqual(planning.contract_hash(engine.runtime['tasks'][task['id']]), planning.contract_hash(before))
        self.assertEqual(engine.runtime['tasks'][task['id']]['reviews'], before['reviews'])
        high['reason'] = 'Mutation of the source must not change the request'
        self.assertNotEqual(action['model_assessment'], high)
        from do_math.session_slots import SessionSlots
        from do_math.execution_lifecycle import create_execution, transition_execution
        profile = execution_profiles.resolve_profile(engine.instance['execution_profiles'], selected['profile_ref'])
        execution = create_execution(execution_id='EX-no-slot', owner_activity_id='AY-work', actor_kind='ai',
            input_manifest={}, profile_ref=selected['profile_ref'], created_at='2026-09-23T00:00:00+00:00')
        transition_execution(execution, 'starting', at='2026-09-23T00:00:00+00:00')
        slots = SessionSlots(engine.runtime, engine.instance)
        self.assertFalse(slots.acquire('EX-no-slot', profile=profile, execution=execution))
        self.assertEqual(engine._select_model(action)['tier'], 'high')

    def test_readiness_refresh_requests_reassessment_while_other_work_remains(self):
        from do_math import task_contracts
        with tempfile.TemporaryDirectory() as directory:
            engine = reassessment_engine(directory)
            engine.instance['sources'].append({'id': 'SO-new', 'name': 'new', 'path': 'new.txt', 'sha256': 'b'*64})
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
        with tempfile.TemporaryDirectory() as directory:
            engine = reassessment_engine(directory)
            engine.instance['sources'].append({'id': 'SO-other', 'name': 'other', 'path': 'other.txt', 'sha256': 'c'*64})
            engine._refresh_readiness()
            self.assertTrue(engine.runtime['tasks']['TK-1']['assessment']['current'])
            engine.runtime['executions']['EX-live'] = {'id': 'EX-live', 'status': 'running',
                'role': 'research_work', 'action': {'id': 'AC-live', 'role': 'research_work', 'target': 'TK-1'}}
            engine.instance['sources'].append({'id': 'SO-new', 'name': 'new', 'path': 'new.txt', 'sha256': 'b'*64})
            engine._refresh_readiness()
            self.assertFalse(any(a['role'] == 'research_plan' for a in engine.runtime['queue']))
            engine.runtime['executions']['EX-live']['status'] = 'ended'
            engine._refresh_readiness()
            self.assertFalse(engine.runtime['tasks']['TK-1']['assessment']['current'])
            self.assertEqual(len([a for a in engine.runtime['queue'] if a['role'] == 'research_plan']), 1)

    def test_terminal_history_remains_closed_when_assessment_evidence_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            engine = reassessment_engine(directory)
            task = engine.runtime['tasks']['TK-1']
            task['status'] = 'closed'
            original = deepcopy(task['results'])
            engine.instance['sources'].append({'id': 'SO-new', 'name': 'new', 'path': 'new.txt', 'sha256': 'b'*64})
            engine._refresh_readiness()
            self.assertEqual(engine.runtime['tasks']['TK-1']['status'], 'closed')
            self.assertEqual(engine.runtime['tasks']['TK-1']['results'], original)
            self.assertFalse(engine.runtime['tasks']['TK-1']['assessment']['current'])
            followups = [e for e in engine.runtime['events'] if e['kind'] == 'task_assessment_invalidated']
            self.assertEqual(len(followups), 1)
            self.assertTrue(any(followups[0]['id'] in a.get('event_refs', []) for a in engine.runtime['queue']))


class KindSemanticConnections(unittest.TestCase):
    def test_proposed_kind_is_checked_by_a_separate_execution_before_activation(self):
        engine = routing_engine()
        engine.instance.update(sources=[], kind_definitions={})
        definition = {"family": "knowledge", "token": "method_note", "meaning": "A nonmathematical method observation",
                      "constraints": {"mathematical_claim": False}}
        engine.runtime["executions"]["EX-author"] = {"id": "EX-author", "status": "ended", "role": "research_work",
            "action": {"role": "research_work"}, "extensions": {"kind_definitions": [definition]}}
        engine._apply_queue_plan = create_autospec(engine._apply_queue_plan); engine._apply_academic_resolutions = create_autospec(engine._apply_academic_resolutions)
        engine._apply_extensions({"role": "research_work"}, "EX-author")
        definition = next(row for row in engine.instance["kind_definitions"].values() if row["token"] == "method_note")
        checks = [a for a in engine.runtime["queue"] if a.get("kind_definition_id") == definition["id"]]
        self.assertEqual(len(checks), 1)
        self.assertEqual(definition["status"], "candidate")
        action = checks[0]
        output = {"summary": "Independent semantic comparison", "used_sources": [], "questions": [],
                  "report": "Meaning and constraints agree", "remaining_work": [],
                  "kind_definition_check": {"definition_id": definition["id"], "definition_sha256": action["kind_definition_sha256"],
                                            "decision": "approved", "findings": []}}
        engine.runtime["executions"]["EX-check"] = {"id": "EX-check", "role": "maintenance", "status": "running",
            "input_basis": {"kind_definition": {"id": definition["id"], "sha256": action["kind_definition_sha256"]}}}
        with self.assertRaisesRegex(ValueError, "independent|author"):
            engine._apply(action, output, "EX-author")
        engine._apply(action, output, "EX-check")
        checked = engine.instance["kind_definitions"][definition["id"]]
        self.assertEqual(checked["status"], "active")
        self.assertEqual(checked["checked_by"], "EX-check")
        self.assertEqual(checked["check"]["decision"], "approved")
        self.assertEqual(engine.runtime["pending_kind_checks"], [])


class EvaluationConnections(unittest.TestCase):
    def test_declared_observation_and_repetition_values_can_be_adopted(self):
        from do_math.configuration import validate_config
        validate_config({"tool_review_window_seconds": 20, "self_check_response_window_seconds": 30,
                         "import_rework_limit": 3, "selection_failure_limit": 3,
                         "exhaustion_empty_limit": 3, "proposal_version_limit": 3, "contract_revision_limit": 3})

    def test_artifact_condition_reads_exact_snapshot_and_validates_bytes(self):
        from do_math import planning
        engine = routing_engine(); engine.head = "a" * 40; engine.store = create_autospec(ResearchRepository, instance=True)
        data = b'{"proof": true}'
        engine.store.read.return_value = data
        ref = {"path": "runtime/artifacts/BA-test/evidence.json", "snapshot": "b" * 40,
               "sha256": hashlib.sha256(data).hexdigest()}
        result = planning.evaluate_condition({"op": "artifact_valid", "artifact_ref": ref},
            engine.instance, engine.runtime, evaluation_context=engine._evaluation_context())
        self.assertEqual(result["state"], "ready")
        engine.store.read.assert_called_once_with(ref["path"], ref["snapshot"])
        engine.store.read.return_value = b'{"valid":true'
        ref["sha256"] = hashlib.sha256(engine.store.read.return_value).hexdigest()
        result = planning.evaluate_condition({"op": "artifact_valid", "artifact_ref": ref},
            engine.instance, engine.runtime, evaluation_context=engine._evaluation_context())
        self.assertEqual(result["state"], "evaluation_error")


class DuplicateRevisionConnections(unittest.TestCase):
    def test_same_task_replacements_are_rejected_before_any_receiver_mutation(self):
        from record_fixtures import approved_task
        from research_fixtures import candidate
        from do_math import revisions
        task, instance, runtime = approved_task()
        instance.update(config={"lean_command": ["unused-fixture"], "scholarly_enabled": False},
                        knowledge={})
        runtime.update(cycles=0, waiting_actions={})
        engine = routing_engine()
        engine.instance, engine.runtime = instance, runtime
        engine._evaluation_context = create_autospec(engine._evaluation_context, return_value={})
        action = {"id": "AC-revise", "role": "research_preparation",
                  "revision_targets": revisions.capture_targets(instance, runtime, [task["id"]])}
        runtime["executions"]["EX-revise"] = {"id": "EX-revise", "role": "research_preparation",
            "status": "ended", "extensions": {}, "input_snapshot": "snapshot"}
        proposals = [candidate(title, revises=task["id"]) for title in ("First", "Second")]
        for proposal in proposals:
            proposal["profile_refs"] = deepcopy(task["profile_refs"])
            proposal["authority_refs"] = list(task["authority_refs"])
            proposal["completion_obligations"][0]["claim"] = proposal["title"]
        output = {"summary": "Conflicting replacements", "questions": [],
                  "used_sources": [], "candidates": proposals}
        before = deepcopy((instance, runtime))
        with self.assertRaisesRegex(ValueError, "one replacement candidate"):
            engine._apply(action, output, "EX-revise")
        self.assertEqual((engine.instance, engine.runtime), before)
        engine._record_output_questions.assert_called_once()


if __name__ == "__main__":
    unittest.main()
