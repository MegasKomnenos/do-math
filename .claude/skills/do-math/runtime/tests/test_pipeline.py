from pathlib import Path
import sys
import time
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cli_adapter import Command, provider_for_model
from knowledge import replay
from lean_broker import terminate_tree
from runner import Runner
from runtime_support import alive, process_identity, read_json, write_json
from test_research import InstanceCase


HERE = Path(__file__).resolve().parent


class PipelineTests(InstanceCase):
    @staticmethod
    def cleanup_runner(engine):
        handles = [*engine.hosts.values(), engine.archiver, engine.broker]
        for handle in handles:
            if handle is None:
                continue
            identity = process_identity(handle.pid)
            if alive(identity):
                terminate_tree(identity['pid'])
            handle.wait(timeout=10)

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
        self.addCleanup(self.cleanup_runner, runner)
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
        self.addCleanup(self.cleanup_runner, restarted)
        with patch('runner.build_command', side_effect=self.command):
            self.assertTrue(restarted.tick())
        self.assertEqual(frozen, sorted((self.instance / 'knowledge/events').glob('*.json')))
        # Registered cleanups also run if a tick or assertion above fails.


if __name__ == '__main__':
    unittest.main()
