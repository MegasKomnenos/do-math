from pathlib import Path
import json
import subprocess
import sys
import threading
import time
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cli_adapter import Command
from coordination import board, session_live
from ending import conversation_id, end_decision, request_prompt, run_turn, supervise
from launch import worker_command
from retention import capture
from runner import Runner, main
from runtime_support import process_identity, read_json, session_host, write_json
from settings import defaults, validate
from test_research import InstanceCase, take

SCRIPT = Path(__file__).with_name('ending_cli.py')


class EndingTests(InstanceCase):
    def prepare(self, maximum=3, role='attempt', config=None):
        engine = Runner(self.instance, self.skill)
        engine.settings['max_end_resumptions'] = maximum
        engine.settings['roles'] = {}  # the scripted CLI speaks the Codex stream for every role
        key = engine.producer('attempt' if role == 'peer' else role,
                              {'node': 'root', 'proofs': []} if role == 'formalizer' else None)
        if role == 'peer':
            pipeline = engine.state['jobs'][key]['pipeline']
            engine.state['jobs'][key]['status'] = 'done'
            engine.state['pipelines'][pipeline].update(role='attempt', stage='peer', producer='source')
            key = engine.enqueue('peer', {'source': str(self.instance / 'sessions/source'),
                                         'source_role': 'attempt'}, pipeline)
        with patch('runner.subprocess.Popen') as host, patch('runner.build_command') as build:
            host.return_value.pid = engine.identity['pid']
            build.return_value = self.command(None, None, None, self.instance)
            self.assertTrue(engine.dispatch(key))
        sid = engine.state['jobs'][key]['session']
        directory = engine.session_dir(sid)
        launch = read_json(directory / 'launch.json')
        launch['command']['cwd'] = str(directory)
        write_json(directory / 'launch.json', launch)
        write_json(directory / 'work/ending-test.json', config or {})
        if role == 'attempt' and not (config or {}).get('no_research'):
            self.assertTrue(take(directory, 'root')['registered'])
        return engine, sid, directory

    @staticmethod
    def command(executable, model, effort, session, *args, **kwargs):
        return Command('codex', [sys.executable, '-B', str(SCRIPT)], Path(session))

    def run_host(self, directory):
        with patch('ending.worker_command', side_effect=self.command):
            self.assertEqual(session_host(directory), 0)
        return read_json(directory / 'end-check.json')

    def test_worker_end_resumes_exact_conversation_and_preserves_context(self):
        for role in ('attempt', 'formalizer', 'explore', 'peer'):
            with self.subTest(role=role):
                engine, sid, directory = self.prepare(role=role, config={'end_after': 1})
                pack = (directory / 'pack.md').read_bytes()
                declaration_path = directory / 'declaration.json'
                declaration = declaration_path.read_bytes() if declaration_path.exists() else None
                with patch('ending.worker_command', side_effect=self.command) as resume:
                    session_host(directory)
                self.assertEqual(resume.call_count, 1)
                self.assertEqual(resume.call_args.kwargs['resume_id'], '01234567-89ab-cdef-0123-456789abcdef')
                state = read_json(directory / 'end-check.json')
                self.assertEqual(state['authorization']['source'], 'worker')
                self.assertEqual(state['authorization']['basis'], 'no_way_forward')
                self.assertEqual(state['resumptions'], 1)
                self.assertEqual(pack, (directory / 'pack.md').read_bytes())
                self.assertEqual(declaration, declaration_path.read_bytes() if declaration_path.exists() else None)
                self.assertIn('directives supplied for this session', (directory / 'turns/0001/prompt.txt').read_text())
                self.assertTrue((directory / 'turns/0001/turn-result.json').is_file())
                # Runner restart sees the same logical session, then collects it once.
                engine = Runner(self.instance, self.skill)
                s = engine.state['sessions'][sid]
                s.update(read_json(directory / 'exit.json'))
                s.update(host=None, cli=None)
                engine.finish(sid, s)
                engine.finish(sid, s)
                pipeline = engine.state['jobs'][s['job']]['pipeline']
                self.assertEqual(engine.state['pipelines'][pipeline]['stage'], 'review' if role == 'peer' else 'peer')
                if role == 'peer':
                    self.assertEqual((directory / 'candidate/report.md').read_text(), 'Research through turn 1.')
                    self.assertEqual(len([j for j in engine.state['jobs'].values()
                                          if j['role'] == 'review' and j['pipeline'] == pipeline]), 1)
                self.assertEqual(len([j for j in engine.state['jobs'].values()
                                      if j['role'] == 'peer' and j['pipeline'] == pipeline]), 1)
                body = (directory / 'conversation.md').read_text()
                self.assertIn('work from turn 0', body)
                self.assertIn('work from turn 1', body)
                self.assertEqual(len(s['retention']['streams']), 4)
                # Finish the first test pipeline so the next role can take root.
                engine.state['pipelines'][pipeline]['stage'] = 'done'
                engine.save()

    def test_guidance_edits_reach_next_turn_without_restarting_host(self):
        _, _, directory = self.prepare(maximum=2, role='explore')
        guidance = self.skill / 'resume'
        original_common = (guidance / 'common.md').read_bytes()
        original_role = (guidance / 'explore.md').read_bytes()
        def update_after_turn(session, folder, command):
            result = run_turn(session, folder, command)
            if Path(folder) == directory:
                (guidance / 'common.md').write_bytes(original_common + b'\nCommon update between turns.\n')
            else:
                (guidance / 'explore.md').write_bytes(original_role + b'\nRole update between turns.\n')
            return result
        with patch('ending.run_turn', side_effect=update_after_turn):
            state = self.run_host(directory)
        self.assertEqual(state['resumptions'], 2)
        first = directory / 'turns/0001'
        second = directory / 'turns/0002'
        self.assertIn('Common update between turns.', (first / 'prompt.txt').read_text())
        self.assertNotIn('Role update between turns.', (first / 'prompt.txt').read_text())
        self.assertIn('Role update between turns.', (second / 'prompt.txt').read_text())
        self.assertEqual((first / 'guidance/explore.md').read_bytes(), original_role)
        self.assertIn(b'Role update between turns.', (second / 'guidance/explore.md').read_bytes())
        self.assertEqual((directory / 'candidate').exists(), False)

    def test_limit_authorizes_end_instead_of_waiting_or_resuming_indefinitely(self):
        _, _, directory = self.prepare(maximum=2)
        state = self.run_host(directory)
        self.assertEqual(state['resumptions'], 2)
        self.assertEqual(state['authorization']['source'], 'runner')
        self.assertEqual(state['authorization']['basis'], 'resumption_limit')
        self.assertTrue(state['authorization']['authorized'])
        self.assertEqual(len((directory / 'work/turns.jsonl').read_text().splitlines()), 3)

    def test_zero_limit_authorizes_initial_exit_without_native_id(self):
        _, _, directory = self.prepare(maximum=0, config={'omit_identity': True})
        state = self.run_host(directory)
        self.assertEqual(state['resumptions'], 0)
        self.assertEqual(state['authorization']['basis'], 'resumption_limit')

    def test_stale_decision_is_not_reused_and_can_be_corrected(self):
        _, _, directory = self.prepare(config={'end_after': 1, 'stale_at': 1})
        state = self.run_host(directory)
        self.assertEqual(state['resumptions'], 2)
        self.assertEqual(state['authorization']['source'], 'worker')
        first = read_json(directory / 'turns/0001/request.json')
        second = read_json(directory / 'turns/0002/request.json')
        self.assertNotEqual(first['id'], second['id'])
        self.assertIn('another reconsideration', second['previous_error'])
        self.assertEqual(read_json(directory / 'turns/0001/submitted-end-decision.json')['request_id'], 'old-request')

    def test_malformed_decision_still_ends_at_configured_limit(self):
        _, _, directory = self.prepare(maximum=1, config={'malformed_at': 1})
        state = self.run_host(directory)
        self.assertEqual(state['authorization']['basis'], 'resumption_limit')
        self.assertIn('not valid JSON', read_json(directory / 'turns/0001/decision-check.json')['error'])

    def test_availability_only_exit_skips_reconsideration(self):
        _, _, directory = self.prepare(config={'no_research': True})
        state = self.run_host(directory)
        self.assertEqual(state['authorization']['basis'], 'no_research')
        self.assertEqual(state['resumptions'], 0)

    def test_refusal_is_interruption_not_worker_authorization(self):
        _, _, directory = self.prepare(config={'refuse_at': 1})
        state = self.run_host(directory)
        self.assertEqual(state['authorization']['basis'], 'interrupted')
        receipt = read_json(directory / 'turns/0001/turn-termination.json')
        self.assertEqual(receipt['refusal']['reason'], 'usage_limit')
        self.assertEqual(read_json(directory / 'exit.json')['exit_code'], 1)

    def test_missing_or_changed_identity_does_not_start_a_fresh_conversation(self):
        for config in ({'omit_identity': True}, {'change_identity_at': 1, 'end_after': 1}):
            engine, sid, directory = self.prepare(config=config)
            state = self.run_host(directory)
            self.assertEqual(state['authorization']['basis'], 'resume_unavailable')
            pipeline = engine.state['jobs'][engine.state['sessions'][sid]['job']]['pipeline']
            engine.state['pipelines'][pipeline]['stage'] = 'done'
            engine.save()

    def test_stop_holds_same_host_and_scope_until_resumed(self):
        engine, sid, directory = self.prepare(maximum=1)
        stop = self.instance / 'control/STOP'
        stop.touch()
        result = []
        with patch('ending.worker_command', side_effect=self.command):
            thread = threading.Thread(target=lambda: result.append(session_host(directory)), daemon=True)
            thread.start()
            try:
                deadline = time.monotonic() + 10
                while time.monotonic() < deadline:
                    path = directory / 'end-check.json'
                    if path.exists() and read_json(path)['status'] == 'waiting_dispatch':
                        break
                    time.sleep(.05)
                self.assertEqual(read_json(path)['status'], 'waiting_dispatch')
                self.assertEqual(read_json(path)['resumptions'], 0)
                self.assertTrue(thread.is_alive())
                self.assertTrue(session_live(engine.state, sid))
                self.assertEqual(board(self.instance)[0]['stage'], 'producing')
                restarted = Runner(self.instance, self.skill)
                restarted.collect()
                self.assertEqual(len(restarted.active()), 1)
                self.assertFalse(any(j['role'] == 'peer' for j in restarted.state['jobs'].values()))
                stop.unlink()
                thread.join(10)
                self.assertFalse(thread.is_alive())
                self.assertEqual(result, [0])
            finally:
                (directory / 'CANCEL').touch()
                thread.join(10)

    def test_cancel_while_dispatch_stopped_never_launches_another_turn(self):
        _, sid, directory = self.prepare()
        (self.instance / 'control/STOP').touch()
        errors = []
        def run():
            try:
                session_host(directory)
            except Exception as exc:
                errors.append(exc)
        with patch('ending.worker_command', side_effect=self.command):
            thread = threading.Thread(target=run, daemon=True)
            thread.start()
            try:
                deadline = time.monotonic() + 10
                while time.monotonic() < deadline:
                    path = directory / 'end-check.json'
                    if path.exists() and read_json(path)['status'] == 'waiting_dispatch':
                        break
                    time.sleep(.05)
                self.assertEqual(read_json(path)['status'], 'waiting_dispatch')
                import io
                with patch('sys.stdout', new=io.StringIO()):
                    self.assertEqual(main(['kill-session', str(self.instance), sid]), 0)
                thread.join(10)
                self.assertFalse(thread.is_alive())
                self.assertEqual(errors, [])
            finally:
                (directory / 'CANCEL').touch()
                thread.join(10)
        state = read_json(directory / 'end-check.json')
        self.assertEqual(state['authorization']['basis'], 'interrupted')
        self.assertEqual(state['resumptions'], 0)

    def test_another_sessions_provider_block_holds_resumption(self):
        engine, _, directory = self.prepare(maximum=1)
        engine.state['blocks']['provider:codex'] = {'until': time.time() + 60, 'reason': 'usage_limit'}
        engine.save()
        with patch('ending.worker_command', side_effect=self.command):
            thread = threading.Thread(target=session_host, args=(directory,), daemon=True)
            thread.start()
            try:
                deadline = time.monotonic() + 10
                while time.monotonic() < deadline:
                    path = directory / 'end-check.json'
                    if path.exists() and read_json(path)['status'] == 'waiting_provider':
                        break
                    time.sleep(.05)
                self.assertEqual(read_json(path)['status'], 'waiting_provider')
                self.assertEqual(read_json(path)['resumptions'], 0)
                engine.state['blocks'].clear()
                engine.save()
                thread.join(10)
                self.assertFalse(thread.is_alive())
                self.assertEqual(read_json(path)['authorization']['basis'], 'resumption_limit')
            finally:
                (directory / 'CANCEL').touch()
                thread.join(10)

    def test_host_loss_is_recorded_as_interruption_without_duplicate_publication(self):
        engine, sid, directory = self.prepare()
        write_json(directory / 'end-check.json', {'maximum': 3, 'resumptions': 0,
                   'status': 'running', 'request': None, 'authorization': None})
        (directory / 'output/report.md').write_text('Retained interrupted mathematics.')
        s = engine.state['sessions'][sid]
        s.update(host=None, cli=None, exit_code=None)
        engine.finish(sid, s)
        self.assertEqual(s['end_check']['authorization']['basis'], 'interrupted')
        self.assertEqual(engine.state['pipelines'][engine.state['jobs'][s['job']]['pipeline']]['stage'], 'peer')


class EndingConfigurationTests(unittest.TestCase):
    def test_role_guidance_is_selected_and_invalid_templates_fail_before_delivery(self):
        import shutil
        import tempfile
        from ending import RESUME_DIRECTORY, ROLES
        self.assertEqual(set(ROLES), {'attempt', 'formalizer', 'explore', 'peer'})
        with tempfile.TemporaryDirectory() as tmp:
            guidance = Path(tmp) / 'resume'
            shutil.copytree(RESUME_DIRECTORY, guidance)
            request = {'id': 'current-request', 'previous_error': 'Stale decision'}
            for role in ROLES:
                prompt = request_prompt(None, request, role=role, guidance_dir=guidance)
                self.assertIn((guidance / (role + '.md')).read_text().strip(), prompt)
                self.assertIn('current-request', prompt)
                self.assertIn('Stale decision', prompt)
                self.assertNotIn('{{', prompt)
            with self.assertRaises(ValueError):
                request_prompt(None, request, role='review', guidance_dir=guidance)
            (guidance / 'peer.md').unlink()
            with self.assertRaises(FileNotFoundError):
                request_prompt(None, request, role='peer', guidance_dir=guidance)
            (guidance / 'common.md').write_text('Incomplete message.')
            with self.assertRaises(ValueError):
                request_prompt(None, request, role='explore', guidance_dir=guidance)

    def test_limit_validation(self):
        self.assertEqual(defaults()['max_end_resumptions'], 3)
        for value in (0, 1, 8):
            self.assertEqual(validate({'max_end_resumptions': value})['max_end_resumptions'], value)
        for value in (-1, True, 1.5, '3', None):
            with self.assertRaises(ValueError):
                validate({'max_end_resumptions': value})

    def test_resume_cli_keeps_isolation_and_context_options(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            identity = '01234567-89ab-cdef-0123-456789abcdef'
            for model in ('codex/gpt-6.1-sol', 'claude/opus'):
                command = worker_command('cli', model, 'xhigh', tmp, resume_id=identity)
                if command.provider == 'codex':
                    self.assertEqual(command.argv[-3:], ['resume', identity, '-'])
                    self.assertIn('--ignore-user-config', command.argv)
                    self.assertIn('model_context_window=1000000', command.argv)
                else:
                    self.assertEqual(command.argv[-2:], ['--resume', identity])
                    self.assertIn('--strict-mcp-config', command.argv)
                    self.assertIn('opus[1m]', command.argv)


if __name__ == '__main__':
    unittest.main()
