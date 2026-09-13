import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('dispatch_run', Path(__file__).with_name('run.py'))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ReturnContract(unittest.TestCase):
    def test_incomplete_and_untried_methods_cannot_finish(self):
        task = {'id': 'test'}
        self.assertIsNotNone(module.check_claim(task, {'task_id': 'test', 'disposition': 'incomplete'}))
        self.assertIsNotNone(module.check_claim(task, {'task_id': 'test', 'disposition': 'exhausted',
                                                       'remaining_executable_methods': ['try actual control']}))

    def test_existing_reports_without_visual_evidence_are_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for name in ('report.md', 'visual.md'):
                (root/name).write_text('Observed state and evidence.', encoding='utf-8')
            (root/'experiments.json').write_text(json.dumps([{'executed': True}]), encoding='utf-8')
            result = {'task_id':'test','disposition':'exhausted','remaining_executable_methods':[],
                      'report_path':str(root/'report.md'),'visual_review_path':str(root/'visual.md'),
                      'experiments_path':str(root/'experiments.json'),'evidence_paths':[str(root/'report.md')],
                      'exhaustion_reason':'External state prevents all recorded alternatives.'}
            self.assertIn('이미지', module.check_claim({'id':'test','output_dir':str(root)},result))

    def test_resume_binds_exact_thread_and_does_not_choose_last(self):
        with tempfile.TemporaryDirectory() as temporary:
            task = {'id':'test','output_dir':temporary,'private_dir':temporary,'attempts':1,
                    'thread_id':'11111111-1111-1111-1111-111111111111'}
            command, prompt, last = module.invocation(task, {'model':'gpt-5.6-sol'}, Path(temporary))
            self.assertIn('resume', command)
            self.assertIn('--dangerously-bypass-approvals-and-sandbox', command)
            self.assertIn(task['thread_id'], command)
            self.assertNotIn('--last', command)
            self.assertIn('mcp_servers={}', command)
            self.assertIn('미완료', prompt)
            self.assertEqual(last.name,'attempt-002-last.json')

    def test_sources_and_seed_files_are_present_and_exclusions_are_absent(self):
        tasks = module.read_json(module.HERE/'tasks.json')
        self.assertEqual(len(tasks),len({t['id'] for t in tasks}))
        self.assertFalse({'unpaywall','scopus','github'} & {t['source'] for t in tasks})
        for task in tasks:
            for name in task['entry_files']:
                self.assertTrue((module.SERVICE/name).is_file(),(task['id'],name))


if __name__ == '__main__':
    unittest.main()
