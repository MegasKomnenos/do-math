"""Follow receiver observations through real scheduling and temporary Git.

Model responses remain explicit doubles; no live research or scheduler task is
modified. Passing assertions confirm observations, not overall product quality.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
import threading
import time
import unittest

ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / '.claude/skills/do-math'
sys.path[:0] = [str(SKILL / 'scripts'), str(SKILL / 'scripts/tests')]
from test_session_scheduler import ParallelEngineTests
from test_engine import common
from test_purpose_engine import candidate, parse_context
from do_math.engine import control
import jsonschema

OBSERVED = []


class Reaudit(unittest.TestCase):
    def setUp(self):
        self.harness = ParallelEngineTests()
        self.harness.setUp()
        self.addCleanup(self.harness.tearDown)

    def record(self, case, **values):
        OBSERVED.append({'case': case, **values})

    def test_retry_failure_stops_live_peer_and_resume_keeps_failed_action(self):
        peer_started = threading.Event()
        observations = {'peer_stopped': False}
        class Runner:
            def run(inner, **kw):
                ctx = parse_context(kw['prompt'], kw['workspace'])
                kw['on_started']({'pid': 1})
                if ctx['task']['title'] == '0':
                    if not peer_started.wait(10):
                        raise AssertionError('The independent task did not start')
                    return {'status': 'failed', 'output': None, 'usage': {}, 'error': 'second local attempt failed'}
                (kw['workspace'] / 'partial.txt').write_text('A preserved independent partial result.')
                peer_started.set()
                until = time.monotonic() + 12
                while time.monotonic() < until:
                    if kw['should_stop']():
                        observations['peer_stopped'] = True
                        return {'status': 'stopped', 'output': None, 'usage': {}, 'error': 'obeyed unrelated global pause'}
                    time.sleep(.02)
                raise AssertionError('The expected stop never reached the live peer')
        engine = self.harness.engine(Runner(), count=2, checkpoint_grace_seconds=1, run_timeout_seconds=30)
        failed_id = engine.runtime['queue'][0]['id']
        engine.runtime['queue'][0]['recovery_attempt'] = 1
        engine._save()
        result = engine.run(max_steps=2)
        self.assertEqual(result['status'], 'paused')
        self.assertTrue(observations['peer_stopped'])
        self.assertEqual(len(engine.runtime['executions']), 2)
        peer = next(e for e in engine.runtime['executions'].values() if e['action']['id'] != failed_id)
        self.assertEqual(peer['outcome'], 'execution_incomplete')
        self.assertTrue(any(f['path'] == 'partial.txt' for f in peer['output_files']))
        control(self.harness.repo, engine.instance['id'], 'resume', origin='operator')
        engine.process_controls()
        same_failed_action = next(a for a in engine.runtime['queue'] if a['id'] == failed_id)
        self.assertEqual(same_failed_action['recovery_attempt'], 1)
        self.record('retry_failure_live_peer', peer_stopped=True, peer_partial_preserved=True,
                    runtime_before_resume=result['status'], runtime_after_resume=engine.runtime['status'],
                    resume_keeps_same_failed_action=True, execution_count=2)

    def test_atomic_rejection_repairs_without_recomputing_main(self):
        main = {**common('research_preparation'), 'candidates': [candidate('A', formal=False)]}
        calls = []
        class Runner:
            def run(inner, **kw):
                ctx = parse_context(kw['prompt'], kw['workspace'])
                kw['on_started']({'pid': 1})
                repair = ctx['action'].get('repair')
                calls.append(bool(repair))
                insight = {'kind': 'question', 'title': 'Independent idea', 'summary': 'An optional idea'}
                if repair:
                    if repair['previous_output'] != main:
                        raise AssertionError('The original main output was not delivered exactly')
                    if not any(f['path'] == 'activity-extensions.json' for f in ctx['previous_output_files']):
                        raise AssertionError('The original sidecar was not delivered')
                    insight['statement'] = 'Which separate lemma would help later?'
                    out = deepcopy(repair['previous_output'])
                else:
                    out = deepcopy(main)
                (kw['workspace'] / 'activity-extensions.json').write_text(json.dumps({'research_insights': [insight]}))
                jsonschema.validate(out, kw['output_schema'])
                return {'status': 'completed', 'output': out, 'usage': {}}
        engine = self.harness.engine(Runner(), count=0)
        engine._enqueue('research_preparation', reason='One explicit preparation and one optional insight')
        engine._save()
        engine.run(max_steps=2)
        self.assertEqual(calls, [False, True])
        self.assertEqual(len(engine.runtime['tasks']), 1)
        accepted = [e for e in engine.runtime['executions'].values() if e['outcome'] == 'output_accepted']
        self.assertEqual(len(accepted), 1)
        self.record('atomic_repair', calls=2, main_reused_without_recomputation=True,
                    accepted_tasks=1, accepted_insights=len(engine.instance['knowledge']))

    def test_accepted_large_report_blocks_and_repeats_contract_review(self):
        seen = []
        class Runner:
            def run(inner, **kw):
                ctx = parse_context(kw['prompt'], kw['workspace'])
                role = ctx['action']['role']
                seen.append(role)
                kw['on_started']({'pid': 1})
                out = common(role)
                if role == 'research_work':
                    out.update(outcome='partial', report='p' * 600000, remaining_work=['Resolve the remaining case.'], checkpoint='Partial work preserved')
                elif role == 'research_plan':
                    out.update(selections=ctx['ready_task_ids'], deferred=[], goal_audit=False,
                               preparation_requests=['Revise the unfinished task'], task_assessments=[{
                        'task_id': t['id'], 'decision': 'incomplete', 'reason': 'The report is partial',
                        'criteria_results': [{'criterion': c, 'satisfied': False, 'evidence': 'Remaining work is explicit'} for c in t['completion_criteria']]
                    } for t in ctx['tasks'] if t['status'] == 'assessing'])
                elif role == 'research_preparation':
                    task = ctx['tasks'][0]
                    out['candidates'] = [candidate(task['title'], formal=False, revises=task['id'])]
                elif role == 'task_contract_review':
                    raise AssertionError('Oversized contract input unexpectedly reached the model')
                else:
                    raise AssertionError(role)
                jsonschema.validate(out, kw['output_schema'])
                return {'status': 'completed', 'output': out, 'usage': {}}
        engine = self.harness.engine(Runner(), count=1, max_input_bytes=500000)
        engine.run(max_steps=1)
        self.assertEqual(next(iter(engine.runtime['executions'].values()))['outcome'], 'output_accepted')
        engine.run(max_steps=6)
        overflows = engine.runtime.get('input_overflows', [])
        reviews = [x for x in overflows if x['action']['role'] == 'task_contract_review']
        self.assertGreaterEqual(len(reviews), 2)
        self.assertEqual({x['detail']['reason'] for x in reviews}, {'mandatory_context_exceeds_limit'})
        self.assertEqual(len({x['action']['target'] for x in reviews}), 1)
        task = next(iter(engine.runtime['tasks'].values()))
        self.assertGreaterEqual(task['revision'], 2)
        self.assertEqual(len(task['results'][0]['report']), 600000)
        self.record('large_report_repeated_review', executed_model_roles=seen,
                    report_accepted=True, revision=task['revision'],
                    identical_target_overflows=len(reviews), status=engine.runtime['status'],
                    overflow_details=[x['detail'] for x in reviews],
                    future_review_queued=any(a['role']=='task_contract_review' for a in engine.runtime['queue']))

    def test_invalid_insight_reaches_next_plan_but_is_not_k(self):
        seen = []
        class Runner:
            def run(inner, **kw):
                ctx = parse_context(kw['prompt'], kw['workspace'])
                role = ctx['action']['role']
                kw['on_started']({'pid': 1})
                out = common(role)
                if role == 'research_preparation':
                    (kw['workspace']/'activity-extensions.json').write_text(json.dumps({'research_insights':[{
                        'kind':'not_a_registered_kind','title':'Invalid candidate','statement':'A tentative note',
                        'summary':'A tentative note','evidence_ids':['KN-MISSING']
                    }]}))
                elif role == 'research_plan':
                    seen.extend(ctx['knowledge_catalog'])
                jsonschema.validate(out, kw['output_schema'])
                return {'status':'completed','output':out,'usage':{}}
        engine = self.harness.engine(Runner(), count=0)
        engine._enqueue('research_preparation', reason='Test the downstream consumer')
        engine._save()
        engine.run(max_steps=2)
        self.assertEqual(len(seen), 1)
        self.assertEqual(seen[0]['kind'], 'not_a_registered_kind')
        self.assertFalse(seen[0]['usable_as_k'])
        checked = engine.check()
        self.assertTrue(checked['passed'], checked)
        self.record('invalid_insight_next_consumer', kind=seen[0]['kind'],
                    status=seen[0]['status'], usable_as_k=seen[0]['usable_as_k'],
                    state_check_passed=checked['passed'], next_role='research_plan')


if __name__ == '__main__':
    program = unittest.main(verbosity=2, exit=False)
    report = {'tests_run':program.result.testsRun,'successful':program.result.wasSuccessful(),
              'scope':'Actual ResearchEngine.run, thread scheduler, SQLite slots, temporary Git; scripted models. No scheduled OS tasks or live research changed.',
              'observations':OBSERVED,'failures':[(str(t),x) for t,x in program.result.failures],
              'errors':[(str(t),x) for t,x in program.result.errors],
              'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                               for p in sorted(SKILL.rglob('*.py'))}}
    destination=Path(__file__).with_name('reaudit-results.json')
    if destination.exists():
        previous=destination.with_name('reaudit-results-previous-'+str(time.time_ns())+'.json')
        previous.write_bytes(destination.read_bytes())
    destination.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    sys.exit(not program.result.wasSuccessful())
