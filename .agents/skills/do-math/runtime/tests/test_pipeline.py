import json
import os
from pathlib import Path
import sys
import time
import unittest
from unittest.mock import patch
sys.path[:0] = [str(Path(__file__).resolve().parents[1]), str(Path(__file__).resolve().parent)]
import canon_index
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

    def light_reader(self):
        """The stand-in for the Claude CLI of a light session (tests/light_cli.py), as a command file that the
        settings can name: (the command file, the folder in which the stand-in records its calls).

        The scripted peer adds the module Small.Step and takes the blind descent test on its line by the
        command a session has. The reader of that test is a light session, and this one opens Small.Step for
        every purpose it is given."""
        scenario = self.root / 'reader'
        scenario.mkdir()
        write_json(scenario / 'script.json', [{'system': 'BEGIN LEVEL', 'answer': json.dumps(
            {'answers': [{'purpose': 1, 'open': ['Small.Step']}]})}])
        if os.name == 'nt':
            cli = self.root / 'claude.cmd'
            cli.write_text(f'@"{sys.executable}" -B "{HERE / "light_cli.py"}" "{scenario}" %*\r\n', encoding='utf-8')
        else:
            cli = self.root / 'claude'
            cli.write_text(f'#!/bin/sh\nexec "{sys.executable}" -B "{HERE / "light_cli.py"}" "{scenario}" "$@"\n',
                           encoding='utf-8')
            cli.chmod(0o755)
        return cli, scenario

    def test_full_pipeline_formalizes_and_drains_followups(self):
        cli, scenario = self.light_reader()
        config = read_json(self.instance / 'settings.json')
        config.update(max_sessions=2, organizer_every_records=1,
                      # A reconsideration turn is launched by the session host with the configured CLI, which
                      # the stand-in below does not replace; test_ending covers end reconsideration. The Claude
                      # CLI that the settings name is the reader of the blind descent test and nothing else here.
                      max_end_resumptions=0, cli={**config['cli'], 'claude': str(cli)})
        write_json(self.instance / 'settings.json', config)
        runner = Runner(self.instance, self.skill)
        self.addCleanup(self.cleanup_runner, runner)
        deadline = time.monotonic() + 300  # a guard against a hung runner; an idle machine finishes in a fraction
        with patch('runner.worker_command', side_effect=self.command):
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
        # Each producer and peer ended at the configured limit of resumptions, not through a failed resumption.
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
        # The peer that added the module Small.Step wrote its line and took the blind descent test on it, by
        # the command a session has, before `prepare` accepted the change: one light session read the level.
        # The canon carries the line as tested, and the index shows it.
        line = (canon.root / 'descriptions/modules/Small/Step.md').read_text(encoding='utf-8')
        self.assertEqual(line, 'The passage from n terms of the sum of odd numbers to n + 1 terms, the step of an '
                               'induction on it.\n')
        described = canon_index.read_summary(self.instance)['modules']
        self.assertEqual((sorted(described), described['Small.Step']['tested'], described['Small.Step']['text'] + '\n'),
                         (['Small.Step'], True, line))
        calls = [read_json(path) for path in (scenario / 'calls').glob('*.json')]
        self.assertEqual(len(calls), 1)
        self.assertIn('BEGIN LEVEL\nThe top of the library Small.\n', calls[0]['system'])
        self.assertIn('- Small.Step\n  ' + line, calls[0]['system'])
        code, text = self.command_line('index', self.instance)
        self.assertEqual(code, 0, text)
        self.assertIn('- Small.Step · 1 element — ' + line, text)
        self.assertIn('- Small.Step · 1 element — ' + line, (self.instance / 'knowledge/folders.md').read_text(encoding='utf-8'))

        def published_bytes():
            return {p.relative_to(self.instance).as_posix(): p.read_bytes()
                    for name in ('knowledge/events', 'knowledge/changes', 'knowledge/reviews',
                                 'knowledge/organizations', 'canon')
                    for p in (self.instance / name).rglob('*') if p.is_file()}

        frozen = published_bytes()
        history = git(self.instance, 'log', '--format=%H', '--', 'knowledge', 'canon')
        restarted = Runner(self.instance, self.skill)
        self.addCleanup(self.cleanup_runner, restarted)
        with patch('runner.worker_command', side_effect=self.command):
            self.assertTrue(restarted.tick())
        self.assertEqual(frozen, published_bytes())
        self.assertEqual(history, git(self.instance, 'log', '--format=%H', '--', 'knowledge', 'canon'))
        # Registered cleanups also run if a tick or assertion above fails.


if __name__ == '__main__':
    unittest.main()
