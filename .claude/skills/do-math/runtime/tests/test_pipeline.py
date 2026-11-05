from pathlib import Path
import sys
import time
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cli_adapter import Command, provider_for_model
from knowledge import replay
from runner import Runner
from runtime_support import alive, read_json, terminate_process, write_json
from test_research import InstanceCase


HERE = Path(__file__).resolve().parent


class PipelineTests(InstanceCase):
    def tearDown(self):
        for path in (self.instance / 'runner/lean').glob('process.json'):
            receipt = read_json(path)
            if alive(receipt.get('process')):
                terminate_process(receipt['process'])
        state = read_json(self.instance / 'runner/state.json')
        for sid, s in state['sessions'].items():
            process = self.instance / 'sessions' / sid / 'process.json'
            if process.exists():
                identity = read_json(process)['process']
                if alive(identity): terminate_process(identity)
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline and any(alive(s.get('host')) for s in state['sessions'].values()):
            time.sleep(.05)
        time.sleep(.3)

    @staticmethod
    def command(cli, model, effort, cwd):
        return Command(provider_for_model(model), [sys.executable, '-B', str(HERE / 'pipeline_cli.py')], Path(cwd))

    def test_full_pipeline_formalizes_and_drains_followups(self):
        config = read_json(self.instance / 'settings.json')
        config.update(max_sessions=2, organizer_every_records=1, retry_seconds=1, retry_max_seconds=2)
        config['lean'].update(command=[sys.executable, '-B', str(HERE / 'pipeline_lean.py')],
                              version_command=[sys.executable, '-B', str(HERE / 'pipeline_lean.py'), '--version'],
                              min_free_memory_mb=0, memory_budget_mb=512)
        write_json(self.instance / 'settings.json', config)
        runner = Runner(self.instance, self.skill)
        deadline = time.monotonic() + 60
        with patch('runner.build_command', side_effect=self.command):
            while time.monotonic() < deadline:
                if runner.tick(): break
                time.sleep(.1)
        self.assertTrue(runner.state['finished'], runner.state)
        self.assertEqual(replay(self.instance)['nodes']['root']['state'], 'formal_proved')
        self.assertTrue(all(p['stage'] == 'done' for p in runner.state['pipelines'].values()))
        roles = {s['role'] for s in runner.state['sessions'].values()}
        self.assertTrue({'attempt', 'peer', 'review', 'formalizer', 'explore', 'organizer'} <= roles)
        self.assertEqual(runner.state['attempt_dispatches'], 1)
        records = list((self.instance / 'knowledge/records').iterdir())
        self.assertTrue(any(list(r.glob('review/lean-evidence/*/result.json')) for r in records))
        frozen = sorted((self.instance / 'knowledge/events').glob('*.json'))
        restarted = Runner(self.instance, self.skill)
        with patch('runner.build_command', side_effect=self.command):
            self.assertTrue(restarted.tick())
        self.assertEqual(frozen, sorted((self.instance / 'knowledge/events').glob('*.json')))
        for handle in (runner.broker, runner.archiver, restarted.broker, restarted.archiver):
            if handle is not None:
                handle.wait(timeout=10)


if __name__ == '__main__':
    unittest.main()
