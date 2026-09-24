"""Regression coverage for autonomous withdrawal of AI-prepared tasks."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from test_redesign_TASKS import task as task_contract
from do_math.planning import contract_hash
from do_math.task_scope import apply_task_dispositions


class EngineIntegrationTest(unittest.TestCase):
    def test_engine_applies_task_disposition_extension(self):
        """A planning extension closes the eligible task through task_scope."""
        from do_math.engine import ResearchEngine as Engine
        from types import SimpleNamespace
        engine=Engine.__new__(Engine)
        task={**task_contract(),'id':'TK-AI','producer_execution':'EX-prep','results':[],'reviews':[]}
        engine.instance={};engine.runtime={'tasks':{},'executions':{},'queue':[],'history':[]}
        engine.runtime["tasks"][task["id"]] = deepcopy(task)
        engine.runtime["executions"]["EX-prep"] = {
            "id": "EX-prep", "role": "research_preparation", "status": "ended",
            "action": {"role": "research_preparation"},
        }
        engine.head='fixed-input'
        engine.store=SimpleNamespace(load=lambda snapshot:('fixed-input',{},deepcopy(engine.runtime)))
        engine.runtime["executions"]["EX-plan"] = {
            "id": "EX-plan", "role": "research_plan", "status": "ended",
            "input_snapshot": engine.head,
            "extensions": {"task_dispositions": [{
                "task_id": task["id"], "disposition": "withdraw", "reason": "A better task subsumes it.",
            }]},
        }

        engine._apply_extensions({"role": "research_plan"}, "EX-plan")

        self.assertEqual(engine.runtime["tasks"][task["id"]]["status"], "closed")


class TaskScopeTests(unittest.TestCase):
    def fixture(self):
        task = {**task_contract(),"id": "TK-AI", "title": "AI proposal", "revision": 3, "status": "planned",
                "producer_execution": "EX-prep",
                "results": [], "reviews": [{"decision": "approved"}], "dependencies": []}
        runtime = {"tasks": {task["id"]: deepcopy(task), "TK-dependent": {
            "id": "TK-dependent", "status": "waiting", "dependencies": [task["id"]]}},
            "executions": {"EX-prep": {"id": "EX-prep", "role": "research_preparation", "status": "ended",
                                           "action": {"role": "research_preparation"}}},
            "queue": [{"id": "AC-review", "role": "task_contract_review", "target": task["id"]},
                      {"id": "AC-other", "role": "research_plan"}],
            "waiting_actions": {"AC-work": {"action": {"id": "AC-work", "role": "research_work", "target": task["id"]}}},
            "history": []}
        return {}, runtime, {task["id"]: deepcopy(task)}

    def withdraw(self, runtime, snapshot):
        return apply_task_dispositions({}, runtime, [{"task_id": "TK-AI", "disposition": "withdraw",
            "reason": "The prepared task is superseded by a narrower current direction."}],
            execution_id="EX-plan", input_tasks=snapshot)

    def test_withdrawal_preserves_contract_and_cancels_only_prestart_actions(self):
        instance, runtime, snapshot = self.fixture()
        _, changed = self.withdraw(runtime, snapshot)
        task = changed["tasks"]["TK-AI"]
        self.assertEqual(task["status"], "closed")
        self.assertEqual(task['completion_obligations'],snapshot['TK-AI']['completion_obligations'])
        self.assertEqual(task["reviews"], [{"decision": "approved"}])
        self.assertNotIn("assessment", task)
        record = task["scope_disposition"]
        self.assertEqual(record["actor_execution"], "EX-plan")
        self.assertEqual(record["previous_revision"], 3)
        self.assertEqual(record["previous_contract_sha256"], contract_hash(snapshot["TK-AI"]))
        self.assertTrue(record["cancelled_queue_actions"])
        self.assertTrue(record["cancelled_waiting_actions"])
        self.assertNotIn('task_readiness',changed)
        self.assertEqual(changed["tasks"]["TK-dependent"]["status"], "waiting")
        self.assertEqual(runtime["tasks"]["TK-AI"]["status"], "planned")

    def test_selected_unstarted_withdrawal_excludes_only_its_authorizing_execution(self):
        _, runtime, snapshot = self.fixture()
        runtime['tasks']['TK-AI']['status'] = 'active'
        runtime['executions']['EX-plan'] = {'id': 'EX-plan', 'role': 'research_preparation',
            'status': 'stopping', 'action': {'target': 'TK-AI'}}
        _, changed = self.withdraw(runtime, snapshot)
        self.assertEqual(changed['tasks']['TK-AI']['status'], 'closed')
        runtime['executions']['EX-other'] = {**runtime['executions']['EX-plan'], 'id': 'EX-other'}
        with self.assertRaisesRegex(ValueError, 'live execution'):
            self.withdraw(runtime, snapshot)
        del runtime['executions']['EX-other']
        runtime['executions']['EX-plan']['role'] = 'research_work'
        with self.assertRaisesRegex(ValueError, 'live execution'):
            self.withdraw(runtime, snapshot)

    def test_terminal_assessment_cannot_withdraw_even_without_results(self):
        from do_math.task_scope import validate_withdrawal_scope
        _, runtime, snapshot = self.fixture()
        for decision in ('completed', 'closed'):
            with self.subTest(decision=decision), self.assertRaisesRegex(ValueError, 'terminal'):
                validate_withdrawal_scope(runtime['tasks']['TK-AI'], snapshot['TK-AI'],
                                          proposed_assessment={'decision': decision})

    def test_rejects_changed_snapshot_user_or_academic_task_and_live_or_terminal_task(self):
        for mutation in (
            lambda runtime, snap: snap["TK-AI"].update(question="new"),
            lambda runtime, snap: runtime["tasks"]["TK-AI"].update(producer_execution="EX-user"),
            lambda runtime, snap: runtime["tasks"]["TK-AI"].update(academic_requirement_id="writeup"),
            lambda runtime, snap: runtime["executions"].update(EX={"id": "EX", "role": "research_work", "status": "running", "action": {"target": "TK-AI"}}),
            lambda runtime, snap: runtime["executions"].update(EX={"id": "EX", "role": "task_contract_review", "status": "running", "action": {"target": "TK-AI"}}),
            lambda runtime, snap: runtime["tasks"]["TK-AI"].update(status="completed"),
            lambda runtime, snap: runtime["tasks"]["TK-AI"].update(status="closed"),
        ):
            with self.subTest(mutation=mutation):
                instance, runtime, snapshot = self.fixture()
                mutation(runtime, snapshot)
                with self.assertRaises(ValueError):
                    self.withdraw(runtime, snapshot)

    def test_rejects_nonwithdraw_and_duplicate_requests_atomically(self):
        _, runtime, snapshot = self.fixture()
        with self.assertRaises(ValueError):
            apply_task_dispositions({}, runtime, [{"task_id": "TK-AI", "disposition": "revise", "reason": "x"}],
                execution_id="EX-plan", input_tasks=snapshot)
        with self.assertRaises(ValueError):
            apply_task_dispositions({}, runtime, [{"task_id": "TK-AI", "disposition": "withdraw", "reason": "x"},
                {"task_id": "TK-AI", "disposition": "withdraw", "reason": "x"}], execution_id="EX-plan", input_tasks=snapshot)
        self.assertEqual(runtime["tasks"]["TK-AI"]["status"], "planned")

    def test_partial_work_requires_item_disposition_and_preserves_results_on_rejection(self):
        _, runtime, snapshot = self.fixture()
        runtime["tasks"]["TK-AI"].update(status="waiting", results=[{"id": "R-partial", "outcome": "partial"}])
        runtime["executions"]["EX-work"] = {"id": "EX-work", "role": "research_work", "status": "ended",
            "action": {"target": "TK-AI"}, "outcome": "output_accepted"}
        snapshot["TK-AI"].update(status="waiting")

        with self.assertRaisesRegex(ValueError,'item dispositions'):
            self.withdraw(runtime, snapshot)

        task = runtime["tasks"]["TK-AI"]
        self.assertEqual(task["status"], "waiting")
        self.assertEqual(task["results"], [{"id": "R-partial", "outcome": "partial"}])
        self.assertEqual(runtime["executions"]["EX-work"]["outcome"], "output_accepted")


class SourceCorrectionRegressionTest(unittest.TestCase):
    def test_same_source_bytes_can_revise_a_misread_claim_and_suspend_dependents(self):
        """A corrected reading changes knowledge, not the immutable source bytes."""
        from types import SimpleNamespace
        from do_math import knowledge,knowledge_io,knowledge_records as kr
        engine=SimpleNamespace(instance={},runtime={'queue':[],'history':[]})
        engine.instance["sources"] = [{"id": "SO-paper", "name": "paper.pdf", "path": "source.pdf",
                                       "sha256": "a" * 64, "status": "active"}]
        candidates = {
            "KN-reading": {"id": "KN-reading", "revision": 1, "status": "verified", "statement": "The paper prints m/n.",
                           "explanation": "Earlier reading.", "summary": "Misread fraction.", "lean_code": "",
                           "declaration_names": [], "dependencies": [], "reviews": [],
                           "source_basis": [{"name": "paper.pdf", "path": "source.pdf", "sha256": "a" * 64}]},
            "KN-dependent": {"id": "KN-dependent", "revision": 1, "status": "verified", "statement": "Derived claim.",
                             "explanation": "Depends on the reading.", "summary": "Dependent.", "lean_code": "",
                             "declaration_names": [], "dependencies": ["KN-reading"], "reviews": []},
        }
        ids={}
        for name,row in candidates.items():
            candidate={key:row[key] for key in ('statement','explanation','summary','lean_code','declaration_names','dependencies')}
            candidate.update(kind='observation',title=name,dependencies=[ids.get(k,k) for k in row['dependencies']])
            engine.instance,engine.runtime,ids[name]=knowledge_io.import_candidate(engine.instance,engine.runtime,candidate,source_ref='SO-paper',actor_ref='user')
        changes={'statement':'The paper prints n/m.','explanation':'The original PDF is unchanged; prior transcription reversed it.'}
        roots=knowledge.revision_roots(engine.instance,ids['KN-reading'])
        impact=knowledge.plan_impact(engine.instance,engine.runtime,roots,[])
        engine.instance,engine.runtime=knowledge.revise_knowledge(engine.instance,engine.runtime,ids['KN-reading'],changes,
            reason='PDF layout audit reads n/m.',actor_ref='EX-correction',declared_impact=impact['computed_impact'])

        self.assertEqual(engine.instance["sources"][0]["sha256"], "a" * 64)
        old=engine.instance['knowledge'][ids['KN-reading']]
        self.assertEqual(old['lifecycle'],'superseded')
        self.assertEqual(kr.proposal_view(engine.instance,old['id'])['statement'],'The paper prints m/n.')
        replacement=next(k for k,v in engine.instance['knowledge'].items() if v.get('supersedes')==old['id'])
        self.assertEqual(kr.proposal_view(engine.instance,replacement)['statement'],'The paper prints n/m.')
        self.assertFalse(knowledge.assess_use(engine.instance['knowledge'][ids['KN-dependent']],engine.instance)['valid'])
        self.assertIn(ids['KN-dependent'],next(row for row in engine.runtime['history'] if row['kind']=='knowledge_reassessment_required')['affected_ids'])


if __name__ == "__main__":
    unittest.main(verbosity=2)
