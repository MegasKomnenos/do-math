"""Purpose-level flows of the real engine with explicitly scripted semantics, on a Sim.

The model double answers every role as the legacy ``support.purpose_answers.PurposeAnswers``
did (``support.engine_purpose.PurposeResponder``); the worker submits each answer
with the workspace tool, the Lean double answers the formal checks the product's
``verify_lean`` runs, and every other external resource is a port fake. Each
test starts from a restored public activation with the purpose configuration
and drives the owner until its fixture outcome, failing at once when the flow
stops first (``support.engine_purpose.drive``). Neither category establishes
actual-model or actual-Lean accuracy. A flow runs every role of one or more
research rounds, from about 10 s to about a minute, so these tests live in the
flow folder.

This module: a task dependency, a large task history, and the solution the public activation reaches.
"""
import hashlib
import json
import unittest

from support.engine_purpose import PurposeResponder, drive, purpose_sim


class PurposeFlowTests(unittest.TestCase):
    def start(self, scenario='direct', **config):
        sim = purpose_sim(**config)
        responder = sim.model.responder = PurposeResponder(scenario)
        return sim, responder

    def test_task_dependency_extension_blocks_A_until_B_completed_then_solves_goal(self):
        sim, responder = self.start('dependency')
        drive(self, sim)
        # The responder also refuses work on A while B is not completed (PurposeAnswers.answer).
        self.assertEqual(responder.work_order, ['B', 'A'])
        tasks = {task['title']: task for task in sim.runtime['tasks'].values()}
        self.assertEqual(tasks['A']['dependencies'], [tasks['B']['id']])
        self.assertNotIn('"task_id": "B"', json.dumps(tasks['A']['occurrence_condition']))
        self.assertTrue(all(task['status'] == 'completed' for task in tasks.values()))
        self.assertEqual(sim.engine.status()['knowledge']['K'], 1)
        self.assertTrue(any(row['role'] == 'formal_check' for row in sim.runtime['executions'].values()))

    def test_large_history_uses_exact_context_source_files_without_losing_work(self):
        sim, responder = self.start('catalog')
        engine = sim.engine

        def large(context):
            return any(task.get('results') and len(task['results'][0]['report']) > 180000 for task in context['tasks'])
        drive(self, sim, predicate=lambda s: any(call['role'] == 'research_plan' and large(call['context'])
                                                 for call in responder.calls))
        # Comparison population stays direct. Large record details are exact
        # sources independently of optional whole-field input reductions.
        task_sources = [entry for execution in engine.runtime['executions'].values()
                        if execution.get('role') == 'research_plan' and execution.get('outcome') == 'output_accepted'
                        and isinstance(execution.get('input_manifest'), dict)
                        for entry in execution['input_manifest'].get('detail_sources', [])
                        if entry['path'].startswith('input/details/tasks/') and entry['bytes'] > 180000]
        self.assertTrue(task_sources)
        for entry in task_sources:
            raw = engine.store.read(entry['artifact_ref'], engine.head)
            self.assertEqual(hashlib.sha256(raw).hexdigest(), entry['sha256'])
            self.assertEqual(len(raw), entry['bytes'])
        self.assertEqual(responder.work_order, ['A'])
        self.assertTrue(any(large(call['context']) for call in responder.calls if call['role'] == 'research_plan'))


class SolvedPurposeTests(unittest.TestCase):
    def test_public_activation_reaches_the_solution_with_archived_role_inputs(self):
        """The public initialization and activation (the purpose template) driven to the goal."""
        sim = purpose_sim()
        responder = sim.model.responder = PurposeResponder()
        drive(self, sim)
        store = sim.engine.store
        snapshot, instance, runtime = store.load()
        self.assertEqual(instance['goal_status'], 'mathematically_solved')
        self.assertEqual(snapshot, sim.engine.head)
        self.assertTrue(all(row.get('outcome') in {'output_accepted', 'verified'} for row in runtime['executions'].values()),
                        [(row['role'], row.get('outcome')) for row in runtime['executions'].values()])
        for execution in runtime['executions'].values():
            if execution.get('input_bundle'):
                # The role input manifest names the archived prompt and its digest.
                prompt = execution['input_manifest']['prompt']
                self.assertEqual(prompt['artifact_ref'], f"runtime/artifacts/{execution['input_bundle']}/input.txt")
                raw = store.read(prompt['artifact_ref'], snapshot)
                self.assertEqual(hashlib.sha256(raw).hexdigest(), prompt['sha256'])
        self.assertEqual(responder.work_order, ['A'])


if __name__ == '__main__':
    unittest.main()
