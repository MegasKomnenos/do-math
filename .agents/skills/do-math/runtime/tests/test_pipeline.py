from pathlib import Path
import sys
import time
import unittest
from unittest.mock import patch
sys.path[:0] = [str(Path(__file__).resolve().parents[1]), str(Path(__file__).resolve().parent)]
from canon import Canon
from cli_adapter import Command, provider_for_model
from knowledge import replay
from lean_broker import terminate_tree
from runner import Runner
from runtime_support import alive, git, process_identity, read_json, write_json
from support import InstanceCase


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
    def command(cli, model, effort, cwd, servers=None):
        return Command(provider_for_model(model), [sys.executable, '-B', str(HERE / 'pipeline_cli.py')], Path(cwd))

    def test_full_pipeline_formalizes_and_drains_followups(self):
        config = read_json(self.instance / 'settings.json')
        config.update(max_sessions=2, organizer_every_records=1,
                      # A reconsideration turn is launched by the session host with the configured CLI, which
                      # the stand-in below does not replace; test_ending covers end reconsideration.
                      max_end_resumptions=0)
        write_json(self.instance / 'settings.json', config)
        runner = Runner(self.instance, self.skill)
        self.addCleanup(self.cleanup_runner, runner)
        deadline = time.monotonic() + 300  # a guard against a hung runner; an idle machine finishes in a fraction
        with patch('runner.build_command', side_effect=self.command):
            while time.monotonic() < deadline:
                if runner.tick(): break
                time.sleep(.1)
        self.assertTrue(runner.state['finished'], runner.state)
        model = replay(self.instance)
        self.assertEqual(model['root_state'], 'formal_proved')
        root = model['elements']['Small.root']
        self.assertEqual((root['standing'], root['settled'], root['formal'], root['lean_proof']),
                         ('accepted', True, True, 'complete'))
        self.assertEqual(model['remaining'], [])
        self.assertTrue(all(p['stage'] == 'done' for p in runner.state['pipelines'].values()))
        roles = {s['role'] for s in runner.state['sessions'].values()}
        self.assertTrue({'attempt', 'peer', 'review', 'formalizer', 'explore', 'organizer'} <= roles)
        self.assertEqual(sum(s['role'] == 'attempt' for s in runner.state['sessions'].values()), 1)
        # Each producer and peer handed over at the configured limit, not through a failed resumption.
        self.assertEqual({s['end_check']['authorization']['basis'] for s in runner.state['sessions'].values()
                          if s['role'] in ('attempt', 'explore', 'formalizer', 'peer')}, {'resumption_limit'})
        # The real dispatch assigns q0 to an explorer; its peer's account becomes the understanding so far of
        # q0, and the question it proposes reaches the frontier through the actual checks and review.
        held = [read_json(self.instance / 'sessions' / sid / 'declaration.json')['question']
                for sid, s in runner.state['sessions'].items()
                if s['role'] == 'explore' and (self.instance / 'sessions' / sid / 'declaration.json').is_file()]
        self.assertIn(('q0', 'runner'), [(q['id'], q['by']) for q in held])
        self.assertTrue(any(q['origin'] == 'change' for q in model['questions'].values()))
        canon = Canon(self.instance)
        self.assertIn('## Review', (canon.questions / 'q0.md').read_text(encoding='utf-8'))
        # The first proof was informal and named what it rests on; the formal one replaced it in place, and
        # what it replaced is in the history. The approach recorded before acceptance went there as well.
        source = (canon.lean / 'Small/Root.lean').read_text(encoding='utf-8')
        self.assertIn('public import Small.Step', source)
        self.assertNotIn('sorry', source)
        self.assertTrue(list((canon.history / 'Small/root').glob('*-approaches/induction.md')))
        self.assertFalse((canon.approaches / 'Small/root').exists())
        self.assertFalse((canon.lean / 'DoMathExtract.lean').exists())
        # The review that confirmed a Lean proof compiled it itself.
        changes = list((self.instance / 'knowledge/changes').iterdir())
        self.assertTrue(any((c / 'verify.json').is_file() for c in changes))

        def published_bytes():
            return {p.relative_to(self.instance).as_posix(): p.read_bytes()
                    for name in ('knowledge/events', 'knowledge/changes', 'knowledge/reviews',
                                 'knowledge/organizations', 'canon')
                    for p in (self.instance / name).rglob('*') if p.is_file()}

        frozen = published_bytes()
        history = git(self.instance, 'log', '--format=%H', '--', 'knowledge', 'canon')
        restarted = Runner(self.instance, self.skill)
        self.addCleanup(self.cleanup_runner, restarted)
        with patch('runner.build_command', side_effect=self.command):
            self.assertTrue(restarted.tick())
        self.assertEqual(frozen, published_bytes())
        self.assertEqual(history, git(self.instance, 'log', '--format=%H', '--', 'knowledge', 'canon'))
        # Registered cleanups also run if a tick or assertion above fails.


if __name__ == '__main__':
    unittest.main()
