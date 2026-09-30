"""Postsolution academic requirements driven by the owner through model calls on the real engine, moved from
``test_academic_engine``.

The model double answers as the legacy ``purpose_fixtures.AcademicRunner``
(``support.academic_scenes.academic_responder``): the purpose scenario's
answers, a planner's resolution of an external rejection, and academic research
work that may ask for a required external effect. The worker submits every
answer with the workspace tool; ``support.engine_purpose.drive`` fails at once
when the responder refused its input or the flow stops (preserved rules K-32,
K-33). The legacy external-effect tests sent real HTTP to a loopback server;
here the engine sends through the HTTP port, whose fake answers from a table by
URL path and records each request (the bytes urllib sends are
``boundary.test_academic_http_bytes``). A test drives several owner passes of
model calls, from about 10 s to about a minute, so these tests live in the flow folder.
"""
from copy import deepcopy
import unittest
from urllib.parse import urlsplit

from do_math import academic
from do_math.task_scope import apply_task_assessments
from purpose_fixtures import SOLVED_REQUIREMENT_CRITERIA, requirement
from research_fixtures import assessment, charter_change
from support.academic_scenes import academic_responder, ended, explicit_sim, solve_with, solved_sim, theorem_sim
from support.engine_lifecycle import applied, http_fails
from support.engine_purpose import drive

ORIGIN = 'http://127.0.0.1:8123'


def academic_tasks(engine):
    return [task for task in engine.runtime['tasks'].values() if task.get('academic_requirement_id') == 'writeup']


def http_grant(sim):
    applied(sim, 'decision', text='Explicit test-only permission for this endpoint', config={'change': {
        'kind': 'grant', 'grant': {'id': 'HTTP', 'kind': 'http', 'allowed_origins': [ORIGIN], 'allowed_methods': ['POST'],
                                   'allowed_path_prefixes': ['/'], 'reuse': 'reusable'}}})


def effect_request(path):
    return {'grant_id': 'HTTP', 'request': {'method': 'POST', 'url': ORIGIN + path, 'body': 'proof'}}


def sent(sim):
    """(path, body, body bytes) of every request the HTTP port received."""
    return [(urlsplit(request['request']['url']).path, request['request']['body'], len(request['request']['body'].encode()))
            for request, _, _ in sim.ports.http.requests]


class AcademicRequirementFlowTests(unittest.TestCase):
    def test_explicit_requirement_blocks_runtime_completion_until_independent_assessment(self):
        # The template approves the requirement, then drives the real solution to mathematically_solved.
        sim = solved_sim(SOLVED_REQUIREMENT_CRITERIA)
        responder = sim.model.responder = academic_responder()
        engine = sim.engine
        tasks = academic_tasks(engine)
        self.assertEqual(len(tasks), 1)
        task = tasks[0]
        self.assertEqual([row['claim'] for row in task['completion_obligations']], ['draft account', 'cite reviewed equality'])
        self.assertNotEqual(engine.runtime['status'], 'completed')
        self.assertNotEqual(task['status'], 'completed')

        drive(self, sim, predicate=lambda s: s.runtime['status'] == 'completed', limit=30)
        task = academic_tasks(engine)[0]
        self.assertEqual(task['status'], 'completed')
        self.assertTrue(any(review['decision'] == 'approved' for review in task['reviews']))
        self.assertNotEqual(task['assessment']['execution_id'], task['results'][0]['execution_id'])
        self.assertEqual([item['obligation_id'] for item in task['assessment']['item_dispositions']],
                         [row['id'] for row in task['completion_obligations']])
        recorded = [entry for entry in engine.runtime['academic_assessments'] if entry['task_id'] == task['id']]
        self.assertEqual(len(recorded), 1)
        self.assertEqual(recorded[0]['decision'], 'satisfied')
        self.assertEqual(engine.status()['academic_validation']['status'], 'completed')
        self.assertIn(task['title'], responder.work_order)

    def test_external_rejection_keeps_formal_solution_and_requires_planner_evidence_to_clear(self):
        sim = solved_sim(None)  # The real solution; the runtime completed.
        sim.model.responder = academic_responder()
        engine = sim.engine
        knowledge = next(iter(engine.instance['knowledge'].values()))
        formal_before = deepcopy(engine.instance['formal_results'][knowledge['formal_result_id']])
        self.assertEqual(engine.runtime['status'], 'completed')

        applied(sim, 'decision', config={'change': {
            'kind': 'academic_rejection', 'actor': 'external referee',
            'text': 'The reader-facing explanation needs a specific response.'}})
        rejection = engine.runtime['external_rejections'][-1]
        rejection_before = deepcopy(rejection)
        # The stored rejection never changes; the planner's input derives whether it blocks the solution.
        before_plan = engine._context({'role': 'research_plan'}, sim.root / 'plan-before-resolution')
        self.assertIs(next(row for row in before_plan['external_rejections']
                           if row['id'] == rejection['id'])['blocks_current_solution'], True)
        self.assertEqual(engine.instance['goal_status'], 'mathematically_solved')
        self.assertEqual(engine.instance['formal_results'][knowledge['formal_result_id']], formal_before)
        self.assertNotEqual(engine.runtime['status'], 'completed')

        drive(self, sim, predicate=lambda s: s.runtime['status'] == 'completed', limit=12)
        rejection = next(item for item in engine.runtime['external_rejections'] if item['id'] == rejection['id'])
        self.assertEqual(rejection, rejection_before)
        after_plan = engine._context({'role': 'research_plan'}, sim.root / 'plan-after-resolution')
        self.assertIs(next(row for row in after_plan['external_rejections']
                           if row['id'] == rejection['id'])['blocks_current_solution'], False)
        resolution = next(row for row in engine.runtime['academic_resolution_records']
                          if row['rejection_id'] == rejection['id'])
        self.assertEqual(resolution['decision'], 'resolved')
        self.assertTrue(resolution['evidence'].strip())
        self.assertEqual(academic.unresolved_rejections(engine.instance, engine.runtime, engine._solution_basis(),
                                                       resolve_evidence=engine._academic_evidence), [])
        resolution_execution = engine.runtime['executions'][resolution['execution_id']]
        self.assertEqual(resolution_execution['action']['role'], 'research_plan')
        self.assertEqual(engine.instance['goal_status'], 'mathematically_solved')
        self.assertEqual(engine.instance['formal_results'][knowledge['formal_result_id']], formal_before)

    def test_required_external_effect_uses_confirmed_loopback_receipt_before_completion(self):
        """From the public activation through the real solution to the academic task and its external effect."""
        sim = explicit_sim()
        sim.model.responder = academic_responder(effect_request=effect_request('/submit'))
        sim.ports.http.table['/submit'] = (200, b'accepted', None)
        engine = sim.engine
        http_grant(sim)
        applied(sim, 'decision', config={'change': charter_change(engine, academic_requirements=[requirement(
            ['send manuscript'], required_inputs=['context:goal'],
            external_effects=[{'id': 'submit', 'scope': 'send manuscript', 'grant_id': 'HTTP'}])])})
        drive(self, sim, predicate=lambda s: s.runtime['status'] == 'completed', limit=35)
        task = academic_tasks(engine)[0]
        self.assertEqual(task['inputs'][-1], 'context:goal')
        self.assertEqual(task['required_external_effects'][0]['id'], 'submit')
        operation = next(item for item in engine.runtime['external_operations'].values()
                         if item.get('academic_binding', {}).get('task_id') == task['id'])
        self.assertEqual((operation['status'], operation['succeeded'], operation['grant_id']), ('confirmed', True, 'HTTP'))
        self.assertEqual(operation['academic_binding']['effect_id'], 'submit')
        self.assertEqual(sent(sim), [('/submit', 'proof', 5)])

    def test_non2xx_or_unknown_external_effect_cannot_complete_academic_requirement(self):
        """A 409 answer and a connection closed without an answer both leave the effect unknown; the receipt gate
        refuses the planner's completed assessment. The premise is a goal the auditors solved on a reviewed theorem
        (the successful effect test covers the full mathematical path)."""
        for suffix in ('/reject', '/unknown'):
            with self.subTest(suffix=suffix):
                sim = theorem_sim()
                sim.model.responder = academic_responder(effect_request=effect_request(suffix))
                if suffix == '/reject':
                    sim.ports.http.table[suffix] = (409, b'rejected', None)
                else:
                    sim.ports.http.table[suffix] = (500, b'', None)  # the request is recorded before it fails
                    http_fails(sim, ConnectionResetError('Remote end closed connection without response'))
                engine = sim.engine
                http_grant(sim)
                solve_with(sim, [requirement(['send manuscript'], external_effects=[
                    {'id': 'submit', 'scope': 'send manuscript', 'grant_id': 'HTTP'}])])
                operation = None
                for _ in range(30):
                    sim.step()
                    operation = next(iter(engine.runtime['external_operations'].values()), None)
                    if operation and operation.get('status') in {'confirmed', 'unknown'}:
                        break
                self.assertIsNotNone(operation)
                self.assertEqual((operation['status'], operation.get('succeeded')), ('unknown', None))
                task = academic_tasks(engine)[0]
                # The loop stops before any planner assessment exists, so the status checks below hold even without
                # the receipt gate. Submit the planner's completed assessment to that gate against the actual ledger.
                completed = assessment(task)
                original_instance, original_runtime = engine.instance, engine.runtime
                try:
                    engine.instance, engine.runtime = deepcopy(original_instance), deepcopy(original_runtime)
                    ended(engine, 'EX-planner-fixture', 'research_plan',
                          input_solution_basis=deepcopy(task['solution_basis']))
                    engine.instance, engine.runtime = apply_task_assessments(engine.instance, engine.runtime, [completed],
                        execution_id='EX-planner-fixture', input_tasks=deepcopy(engine.runtime['tasks']))
                    with self.assertRaisesRegex(ValueError,
                                                '^satisfied academic assessment lacks confirmed successful required external effects$'):
                        engine._record_academic_assessment(engine.runtime['tasks'][task['id']], completed, 'EX-planner-fixture')
                finally:
                    engine.instance, engine.runtime = original_instance, original_runtime
                self.assertFalse([entry for entry in engine.runtime.get('academic_assessments', [])
                                  if entry.get('task_id') == task['id']])
                self.assertNotEqual(engine.status()['academic_validation']['status'], 'completed')
                self.assertNotEqual(engine.runtime['status'], 'completed')
                self.assertEqual([path for path, _, _ in sent(sim)], [suffix])


if __name__ == '__main__':
    unittest.main()
