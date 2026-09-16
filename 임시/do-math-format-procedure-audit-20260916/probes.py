"""Read-only product audit: real receiver/context code, scripted model and storage.

Run from C:\\math. PASS means the stated observation was reproduced; it is not
a claim that the product satisfies the guidance. No live research is opened.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
import time
import unittest

ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / '.claude/skills/do-math'
sys.path[:0] = [str(SKILL / 'scripts'), str(SKILL / 'scripts/tests')]
from test_purpose_engine import PurposeHarness, common, candidate, parse_context
from do_math.engine import DEFAULT_CONFIG, control
from do_math.context_store import fit_context
from do_math.contracts import prompt_documents, ROLES
from do_math.repository import new_id
import jsonschema

OBSERVATIONS = []


class Audit(PurposeHarness):
    def make_current(self, **config):
        return self.make(session_limits=deepcopy(DEFAULT_CONFIG['session_limits']),
                         scholarly_enabled=False, **config)

    def step(self, engine):
        engine.runtime['queue'][0].setdefault('id', new_id('AC'))
        action = deepcopy(engine.runtime['queue'][0])
        if action['role'] == 'formal_check':
            engine._formal(action)
        else:
            engine._call(action, time.monotonic() + 60)

    def record(self, name, **evidence):
        OBSERVATIONS.append({'name': name, **evidence})

    def fixed_runner(self, output, files=None):
        class Runner:
            def run(inner, **kwargs):
                kwargs['on_started']({'fixture': True})
                jsonschema.validate(output, kwargs['output_schema'])
                for name, value in (files or {}).items():
                    (kwargs['workspace'] / name).write_bytes(value)
                return {'status': 'completed', 'output': deepcopy(output), 'usage': {}}
        return Runner()

    def last(self, engine):
        return list(engine.runtime['executions'].values())[-1]

    def test_01_main_schema_is_delivered_but_code_is_not_materialized(self):
        engine, _ = self.make_current()
        for role in ROLES:
            schema = engine._response_schema({'role': role})
            prompt = engine._render_prompt(role, {}, output_schema=schema)
            self.assertIn('--- OUTPUT JSON SCHEMA ---', prompt)
            docs = prompt_documents(role)
            self.assertTrue(all(row['path'].endswith('.md') for row in docs))
        workspace = self.root / 'delivery-preparation'
        engine._context({'role': 'research_preparation'}, workspace)
        self.assertFalse(list((workspace / 'input/implementation').rglob('*.py')))
        self.record('main_schema_delivery', roles=len(ROLES),
                    main_schema=True, materialized_validator_code=False)

    def test_02_optional_file_overflow_rejects_valid_main(self):
        output = {**common('A valid independent preparation'),
                  'candidates': [candidate('A', formal=False)]}
        baseline, _ = self.make_current(max_artifact_bytes=128)
        baseline.runner = self.fixed_runner(output)
        self.step(baseline)
        self.assertEqual(self.last(baseline)['outcome'], 'output_accepted')
        engine, _ = self.make_current(max_artifact_bytes=128)
        engine.runner = self.fixed_runner(output, {'unreferenced-scratch.txt': b'x' * 129})
        self.step(engine)
        execution = self.last(engine)
        self.assertEqual(execution['outcome'], 'execution_incomplete')
        self.assertEqual(len(engine.runtime['tasks']), 0)
        omitted = json.loads(engine.store.read(f"runtime/artifacts/{execution['artifact_bundle']}/omitted.json"))
        self.assertFalse(omitted[0]['required'])
        self.record('optional_file_rejection', error=execution['error'], omitted=omitted,
                    baseline_tasks=len(baseline.runtime['tasks']), resulting_tasks=len(engine.runtime['tasks']))

    def test_03_independent_extension_error_rolls_back_main(self):
        engine, _ = self.make_current()
        output = {**common('A valid independent preparation'),
                  'candidates': [candidate('A', formal=False)]}
        extension = {'research_insights': [{'kind': 'question', 'title': 'Unrelated question',
                                            'summary': 'A separate candidate'}]}
        engine.runner = self.fixed_runner(output, {'activity-extensions.json': json.dumps(extension).encode()})
        self.step(engine)
        execution = self.last(engine)
        self.assertEqual(execution['outcome'], 'execution_incomplete')
        self.assertEqual(len(engine.runtime['tasks']), 0)
        repair = next(a for a in engine.runtime['queue'] if a.get('repair'))
        self.assertEqual(repair['repair']['previous_output'], output)
        recovered = engine._context(repair, self.root / 'repair-context')
        self.assertTrue(any(f['path'] == 'activity-extensions.json' for f in recovered['previous_output_files']))
        self.record('extension_rolls_back_independent_main', error=execution['error'],
                    tasks=len(engine.runtime['tasks']), previous_output_preserved=True,
                    extension_delivered_to_repair=True)

    def test_04_unrelated_source_rejects_identity_review(self):
        engine, runner = self.make_current(max_output_repairs=0)
        source = self.root / 'unrelated.txt'
        source.write_text('An unrelated imported note.', encoding='utf-8')
        control(self.repo, engine.instance['id'], 'source', config={'path': str(source)})
        engine.process_controls()
        for _ in range(15):
            if engine.runtime['queue'][0]['role'] == 'identity_review':
                break
            self.step(engine)
        self.assertEqual(engine.runtime['queue'][0]['role'], 'identity_review')
        proposal = engine.instance['knowledge'][engine.runtime['queue'][0]['target']]
        self.assertEqual(proposal['source_basis'], [])
        self.assertEqual(proposal['dependencies'], [])
        original = runner.run
        def changing(**kwargs):
            result = original(**kwargs)
            source.write_text('A revised unrelated imported note.', encoding='utf-8')
            control(self.repo, engine.instance['id'], 'source', config={'path': str(source)})
            kwargs['should_stop']()
            return result
        runner.run = changing
        self.step(engine)
        execution = self.last(engine)
        self.assertEqual(execution['outcome'], 'execution_incomplete')
        self.assertIn('source content changed', execution['error'])
        self.record('unrelated_source_invalidates_review', proposal_source_basis=proposal['source_basis'],
                    output_used_sources=runner.returned[-1]['output']['used_sources'],
                    captured_source_basis=execution['source_basis'], error=execution['error'])

    def test_05_accumulated_task_results_cannot_be_cataloged(self):
        engine, _ = self.make_current(max_input_bytes=500000)
        self.step(engine)
        task = next(iter(engine.runtime['tasks'].values()))
        action = {'role': 'research_work', 'target': task['id']}
        workspace = self.root / 'small-task'
        context = engine._context(action, workspace)
        mandatory = [k for k in ('goal', 'goal_kind', 'policies', 'action', 'task', 'proposal', 'role_review', 'user_request', 'interpretation_to_check') if k in context]
        overhead = len(engine._render_prompt(action['role'], {}, output_schema=engine._response_schema(action)).encode()) + 2048
        small = fit_context(context, max_bytes=500000-overhead, workspace=workspace, mandatory_keys=mandatory)
        self.assertIsNone(small['overflow'])
        task['results'] = [{'execution_id': 'EX-old', 'report': 'p' * 600000, 'output_files': []}]
        workspace = self.root / 'large-task'
        context = engine._context(action, workspace)
        large = fit_context(context, max_bytes=500000-overhead, workspace=workspace, mandatory_keys=mandatory)
        self.assertEqual(large['overflow']['reason'], 'mandatory_context_exceeds_limit')
        self.assertTrue((workspace / 'input/catalog/tasks.json').is_file())
        self.record('growing_task_is_mandatory', overflow=large['overflow'],
                    catalog_tasks_exists=True, inline_task_result_bytes=600000,
                    small_input_fits=True, common_overhead_bytes=overhead)

    def test_06_invalid_insight_kind_and_evidence_are_accepted(self):
        engine, _ = self.make_current()
        bad_kind, bad_ref = 'not_a_registered_kind', 'KN-NOT-PROVIDED'
        extension = {'research_insights': [{'kind': bad_kind, 'title': 'An invalidly typed insight',
                     'statement': 'A bounded observation.', 'summary': 'A separate candidate',
                     'evidence_ids': [bad_ref]}]}
        self.assertNotIn(bad_kind, engine.instance['kind_definitions'])
        output = {**common('Preserve one insight'), 'candidates': []}
        engine.runner = self.fixed_runner(output, {'activity-extensions.json': json.dumps(extension).encode()})
        self.step(engine)
        execution = self.last(engine)
        self.assertEqual(execution['outcome'], 'output_accepted')
        item = next(iter(engine.instance['knowledge'].values()))
        self.assertEqual(item['kind'], bad_kind)
        self.assertEqual(item['dependencies'], [bad_ref])
        self.record('invalid_insight_kind_and_reference_accepted', outcome=execution['outcome'],
                    kind=item['kind'], dependencies=item['dependencies'])

    def test_07_failed_diagnosed_retry_pauses_unrelated_queue(self):
        engine, _ = self.make_current()
        action = engine.runtime['queue'][0]
        action['recovery_attempt'] = 1
        engine._enqueue('maintenance', reason='An independent maintenance observation')
        class Failure:
            def run(inner, **kwargs):
                kwargs['on_started']({'fixture': True})
                return {'status': 'failed', 'output': None, 'usage': {}, 'error': 'Local transient model failure'}
        engine.runner = Failure()
        self.step(engine)
        self.assertEqual(engine.runtime['status'], 'paused')
        self.assertTrue(any(a['role'] == 'maintenance' for a in engine.runtime['queue']))
        self.record('diagnosed_retry_failure_pauses_instance', status=engine.runtime['status'],
                    remaining_roles=[a['role'] for a in engine.runtime['queue']],
                    error=self.last(engine)['error'], feature_version=engine.instance['feature_version'])


if __name__ == '__main__':
    manifest = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in sorted(SKILL.rglob('*')) if p.is_file() and p.suffix in {'.md', '.py'}}
    program = unittest.main(verbosity=2, exit=False)
    result = {'scope': 'Real input/receiver core; scripted model, compiler and memory repository. No live Codex/Lean or scheduler execution.',
              'tests_run': program.result.testsRun, 'successful': program.result.wasSuccessful(),
              'failures': [(str(t), trace) for t, trace in program.result.failures],
              'errors': [(str(t), trace) for t, trace in program.result.errors],
              'observations': OBSERVATIONS, 'source_sha256': manifest}
    Path(__file__).with_name('probe-results.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    sys.exit(not program.result.wasSuccessful())
