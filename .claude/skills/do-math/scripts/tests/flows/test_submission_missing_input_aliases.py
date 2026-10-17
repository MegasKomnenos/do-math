"""누락 자료 별칭을 실제 계획이 저장하고 공개 source 도착이 재평가를 연다."""
from copy import deepcopy
import unittest

from do_math import submission
from do_math.canonical import exact_content_hash
from do_math.task_contracts import returned_task_ids
from support.engine_lifecycle import applied
from support.model import Answer, default
from support.scheduling_parallel import ready_work_sim
from support.submission_calls import submission_model


def setUpModule():
    ready_work_sim(1, max_output_repairs=0)


class MissingInputAliasTests(unittest.TestCase):
    def test_source_name_alias_id_and_published_path_reopen_the_actual_plan(self):
        """이름·source 별칭은 첫 도착, ID·게시 경로는 원 생산자의 다음 판본이다."""
        for form in ('name', 'alias', 'id', 'path'):
            with self.subTest(form=form):
                self.assert_source_reopens(form)

    def test_supplied_local_source_path_reopens_the_actual_plan(self):
        self.assert_source_reopens('local_path')

    def assert_source_reopens(self, form):
        sim = ready_work_sim(1, max_output_repairs=0)
        source_path = sim.root / 'submission-missing.txt'
        source_path.write_bytes(b'previous source edition')
        if form in {'id', 'path', 'local_path'}:
            applied(sim, 'source', config={'path': str(source_path)})
            source = next(row for row in sim.instance['sources'] if row['name'] == source_path.name)
            reference = source[form] if form != 'local_path' else None
        else:
            reference = source_path.name if form == 'name' else 'source:' + source_path.name
        sim.engine.runtime['queue'] = [row for row in sim.runtime['queue'] if row['role'] == 'research_work']
        sim.engine._save()
        sim.run_until(lambda s: bool(returned_task_ids(s.runtime['tasks'])), max_steps=8)
        task_id, = returned_task_ids(sim.runtime['tasks'])
        original_results = deepcopy(sim.runtime['tasks'][task_id]['results'])
        model = submission_model(sim)
        seen = []

        def incomplete(output, context):
            nonlocal reference
            if form == 'local_path':
                supplied = next(row for row in context['sources'] if row['id'] == source['id'])
                reference = supplied['local_path']
            tasks = {row['id']: row for row in context['tasks']}
            self.assertIn(task_id, tasks)
            result = deepcopy(output)
            result['goal_audit'] = False
            result['task_assessments'] = [{'task_id': task_id, 'decision': 'incomplete',
                'reason': '정확히 지목한 추가 자료가 필요함', 'item_dispositions': [],
                'unresolved': [{'obligation_id': obligation['id'], 'missing_inputs': [reference],
                    'next_owner': 'research_work'} for obligation in tasks[task_id]['completion_obligations']]}]
            return result

        rule = model.on('research_plan').reply(Answer(incomplete))
        model.before('research_plan', lambda context, workspace: seen.append(context['execution_id']))
        sim.run_until(lambda s: bool(seen) and s.runtime['executions'][seen[0]]['status'] == 'ended', max_steps=8)
        self.assertEqual(sim.runtime['executions'][seen[0]]['outcome'], 'output_accepted')
        assessed = sim.runtime['tasks'][task_id]['assessment']
        self.assertTrue(assessed['current'])
        self.assertEqual([row['missing_inputs'] for row in assessed['unresolved']],
                         [[reference]] * len(assessed['unresolved']))
        self.assertTrue(assessed['unresolved'])
        self.assertEqual(returned_task_ids(sim.runtime['tasks']), [])
        if form == 'local_path':
            self.assertEqual(assessed['basis'][reference],
                             {'source_id': source['id'], 'sha256': exact_content_hash(source)})
            execution = sim.runtime['executions'][seen[0]]
            preserved = deepcopy({key: execution[key] for key in ('submission_intent', 'submission_receipt')})
            sealed_bytes = {execution['submission_intent'][key]: sim.engine.store.read(
                execution['submission_intent'][key], sim.engine.head)
                for key in ('output_ref', 'extensions_ref', 'check_ref')}
            sealed = submission.read_sealed_submission(execution, sim.engine.head, sim.engine.store.read)
            self.assertEqual(sealed['output']['task_assessments'][0]['unresolved'], assessed['unresolved'])
            sim.restart()
            self.assertEqual(sim.runtime['tasks'][task_id]['assessment'], assessed)
        other = sim.root / 'unrelated.txt'
        other.write_bytes(b'unrelated material')
        applied(sim, 'source', config={'path': str(other)})
        sim.engine._refresh_readiness()
        self.assertTrue(sim.runtime['tasks'][task_id]['assessment']['current'])
        source_path.write_bytes(b'the requested next edition arrives')
        applied(sim, 'source', config={'path': str(source_path)})
        if form == 'local_path':
            sim.restart()
        sim.engine._refresh_readiness()
        self.assertFalse(sim.runtime['tasks'][task_id]['assessment']['current'],
                         {'reference': reference, 'basis': sim.runtime['tasks'][task_id]['assessment']['basis']})
        self.assertEqual(returned_task_ids(sim.runtime['tasks']), [task_id])
        self.assertEqual(sim.runtime['tasks'][task_id]['results'], original_results)
        rule.reply(default())
        sim.run_until(lambda s: len(seen) == 2 and s.runtime['executions'][seen[1]]['status'] == 'ended', max_steps=8)
        self.assertEqual(sim.runtime['executions'][seen[1]]['outcome'], 'output_accepted')
        self.assertEqual(sim.runtime['tasks'][task_id]['results'], original_results)
        if form == 'local_path':
            self.assertEqual(sim.runtime['tasks'][task_id]['assessment']['execution_id'], seen[1])
            self.assertTrue(sim.runtime['tasks'][task_id]['assessment']['current'])
            execution = sim.runtime['executions'][seen[0]]
            self.assertEqual({key: execution[key] for key in preserved}, preserved)
            for path, raw in sealed_bytes.items():
                self.assertEqual(sim.engine.store.read(path, sim.engine.head), raw)
            self.assertEqual(submission.read_sealed_submission(execution, sim.engine.head, sim.engine.store.read), sealed)
