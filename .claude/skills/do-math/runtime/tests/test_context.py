"""Actual launch snapshots, instruction isolation and current research updates."""
from pathlib import Path
import sys
import tomllib
import os
import json
import shutil
import subprocess
import unittest
from unittest.mock import patch
sys.path[:0] = [str(Path(__file__).resolve().parents[1]), str(Path(__file__).resolve().parent)]
from canon_tool import view
from context import assemble, rebase_links
from coordination import updates
from knowledge import render, replay
from launch import worker_command, worker_environment
from runner import Runner, main
from runtime_support import read_json, write_json
from support import InstanceCase, module_text, record_text, take

INSTALLED = Path(__file__).resolve().parents[2]
ROLES = ('attempt', 'explore', 'formalizer', 'peer', 'review', 'organizer')
# A pack opens with the root and the assignment, so that the guides are read with both in mind. The other
# research views, the user conditions and the commands follow the guides, in this order.
OPENING = ['# Root statement', '# The root in Lean', '# Your assignment']
VIEWS = ['# Frontier at launch',
         '# Understanding so far of the root problem as a whole (question q0)', '# Board at launch',
         '# User conditions supplied at launch', '# Executable commands']
ROOT_RECORD = record_text('The sum of the first n odd numbers equals n times n.', weight='unit',
                          short='odd numbers sum to a square',
                          statement='For every natural number $n$, $1 + 3 + \\dots + (2n - 1) = n^2$.',
                          proof='By induction on $n$: adding the next odd number $2k + 1$ to $k^2$ gives $(k + 1)^2$.')
INFORMAL = '''/-- The sum of the first `n` odd numbers is the square of `n`. -/
theorem root (n : Nat) : oddSum n = n * n := by
  -- induction on n; the step adds 2 * n + 1
  sorry'''
FORMAL = '''/-- The sum of the first `n` odd numbers is the square of `n`. -/
theorem root (n : Nat) : oddSum n = n * n := by
  induction n with
  | zero => rfl
  | succ k ih => simp only [oddSum, ih]; omega'''
LEAD = module_text('''/-- A lead that no proof of the root uses. -/
theorem lead (n : Nat) : oddSum (n + n) = 4 * oddSum n := by
  sorry''')
UNDERSTANDING = ('The sum grows by one odd number at a time, and each step completes a square. '
                 'The elements `Small.oddSum` and `Small.root` carry the exact statements.\n')


class ContextTests(InstanceCase):
    def session(self, name):
        """A session folder as the runner's dispatch leaves it before the pack is assembled."""
        folder = self.instance / 'sessions' / name
        folder.mkdir()
        for part in ('output', 'work', 'inbox'):
            (folder / part).mkdir()
        return folder

    def pack(self, folder, role='attempt', task=None):
        engine = Runner(self.instance, self.skill)
        return assemble(self.skill, self.instance, folder, role, task or {}, None,
                        engine.model['sequence'], engine.settings)

    def running(self, engine, sid, role='attempt'):
        """A launched producer as the runner records it, so that its coordination commands are served."""
        key = engine.producer(role)
        job = engine.state['jobs'][key]
        folder = self.session(sid)
        assemble(self.skill, self.instance, folder, role, {}, job['pipeline'], engine.model['sequence'],
                 engine.settings)
        engine.state['pipelines'][job['pipeline']]['producer'] = sid
        engine.state['sessions'][sid] = {'id': sid, 'role': role, 'status': 'running', 'job': key}
        job.update(status='running', session=sid)
        engine.save()
        return folder

    def prove_root(self, text, engine=None, modules=None, records=None):
        folder = self.candidate(modules=modules, replace={'Small.root': text},
                                records={'Small/root.md': ROOT_RECORD, **(records or {})})
        return self.publish(folder, engine=engine)

    @staticmethod
    def lead(folder):
        """The part of a pack before its guides: the root in words and in Lean, and the assignment."""
        text = (folder / 'pack.md').read_text(encoding='utf-8')
        return text[:text.index('<!-- begin ')]

    @staticmethod
    def views(folder):
        """The part of a pack after its guides: the research views, the user conditions and the commands."""
        text = (folder / 'pack.md').read_text(encoding='utf-8')
        return text[text.rindex('<!-- end '):]

    def parts(self, text, headings):
        """The text under each heading, after checking that the headings stand in the given order."""
        positions = [text.index('\n' + heading + '\n') for heading in headings]
        self.assertEqual(positions, sorted(positions))
        return dict(zip(headings, (text[a:b] for a, b in zip(positions, positions[1:] + [len(text)]))))

    def test_cli_json_preserves_unicode_under_ascii_output_environment(self):
        instance = self.root / '연구'
        shutil.copytree(self.instance, instance)
        session = instance / 'sessions/s1'; session.mkdir()
        write_json(session / 'input.json', {'instance': str(instance), 'session': 's1', 'role': 'attempt',
                                           'user_inputs': [{'id': 'initial', 'text': 'Use ℕ, including zero.'}]})
        runtime = Path(__file__).resolve().parents[1]

        def run(script, *args):
            return subprocess.run([sys.executable, '-B', str(runtime / script), *args],
                                  capture_output=True, env={**os.environ, 'PYTHONIOENCODING': 'ascii'})

        for script, args in [('runner.py', ['status', str(instance)]),
                             ('coordination.py', ['updates', str(session)]),
                             ('lean_broker.py', ['status', str(instance)])]:
            with self.subTest(script=script):
                result = run(script, *args)
                self.assertEqual(result.returncode, 0, result.stderr)
                data = json.loads(result.stdout.decode('utf-8'))
                if script == 'coordination.py':
                    self.assertEqual(data['user_inputs'][0]['text'], 'Use ℕ, including zero.')
                else:
                    self.assertEqual(data['instance'], str(instance))
        # The reading command prints text, not JSON; its answers, a refusal included, survive the same
        # environment. A Lean name may hold any letter, so a refusal can have to repeat one.
        with self.subTest(script='canon_tool.py', command='frontier'):
            result = run('canon_tool.py', 'frontier', str(session))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('`Small.root`', result.stdout.decode('utf-8'))
        with self.subTest(script='canon_tool.py', command='view'):
            result = run('canon_tool.py', 'view', str(session), 'Small.ℕ')
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertEqual(json.loads(result.stdout.decode('utf-8')), {'error': 'no such element: Small.ℕ'})

    def test_instruction_links_lead_to_snapshot_and_research_text_stays_verbatim(self):
        session = self.instance / 'sessions/s1'
        context = session / 'context'
        text = rebase_links('[The canon](../reference/canon.md)', context / 'roles/attempt.md', session, context)
        self.assertEqual(text, '[The canon](context/reference/canon.md)')
        # A fragment stays on the rebased target; links that are not local files are left as they are.
        self.assertEqual(rebase_links('[Lean](lean.md#builds) and [site](https://example.org/a)',
                                      context / 'reference/tools.md', session, context),
                         '[Lean](context/reference/lean.md#builds) and [site](https://example.org/a)')
        self.assertEqual(rebase_links('[Below](#commands)', context / 'reference/tools.md', session, context),
                         '[Below](#commands)')
        # A link that leaves the snapshot would not lead to a retained copy, so assembly refuses it.
        with self.assertRaisesRegex(ValueError, 'escapes its source area'):
            rebase_links('[Skill](../../SKILL.md)', context / 'roles/attempt.md', session, context)
        folder = self.session('s1')
        root = 'Consider the expression \\([n](x)\\) with its original notation.'
        (self.instance / 'root.md').write_text(root, encoding='utf-8')
        assemble(self.skill, self.instance, folder, 'attempt', {}, None, 0,
                 read_json(self.instance / 'settings.json'))
        self.assertIn(root, (folder / 'pack.md').read_text(encoding='utf-8'))

    def test_new_user_conditions_only_reach_future_launches(self):
        first = self.session('first')
        self.pack(first)
        original = (first / 'pack.md').read_bytes()
        (self.instance / 'control/inputs/001.txt').write_text('Use convention K in new work.', encoding='utf-8')
        engine = Runner(self.instance, self.skill)
        engine.ingest_inputs()
        second = self.session('second')
        self.pack(second)
        self.assertEqual(updates(first)['user_inputs'], [])
        self.assertEqual(list((first / 'inbox').iterdir()), [])
        self.assertEqual((first / 'pack.md').read_bytes(), original)
        self.assertEqual(updates(second)['user_inputs'][0]['text'], 'Use convention K in new work.')
        self.assertEqual(updates(first)['root_state'], 'unresolved')
        # What research publishes afterwards does reach a session that is already running, through updates.
        self.prove_root(INFORMAL)
        self.assertEqual(updates(first)['root_state'], 'informal_proved')
        self.assertEqual((first / 'pack.md').read_bytes(), original)

    def test_input_command_preserves_standing_conditions_for_later_launches(self):
        condition = self.root / 'conditions.md'
        # A condition file can begin with a byte order mark, as Windows PowerShell writes UTF-8; it is no part of the condition.
        condition.write_text('Write every record in English.', encoding='utf-8-sig')
        blank = self.root / 'blank.md'
        blank.write_text(' \n', encoding='utf-8')
        with patch('builtins.print') as shown:
            self.assertEqual(main(['input', str(self.instance), '--file', str(condition)]), 0)
            self.assertEqual(main(['input', str(self.instance), '--file', str(blank)]), 1)
        stored = Path(json.loads(shown.call_args_list[0].args[0])['input'])
        inputs = self.instance / 'control/inputs'
        self.assertEqual(stored.parent.resolve(), inputs.resolve())
        self.assertEqual(stored.read_text(encoding='utf-8'), 'Write every record in English.')
        self.assertEqual([p.name for p in inputs.iterdir()], [stored.name])
        later = self.session('later')
        self.assertEqual([item['text'] for item in self.pack(later)['user_inputs']],
                         ['Write every record in English.'])

    def test_every_role_receives_the_root_the_frontier_the_understanding_and_the_board_but_no_index(self):
        (self.instance / 'control/inputs/001.txt').write_text('Use convention K in new work.', encoding='utf-8')
        knowledge = self.instance / 'knowledge'
        frontier = (knowledge / 'frontier.md').read_text(encoding='utf-8')
        board = (knowledge / 'board.md').read_text(encoding='utf-8')
        # At the start the frontier is the root alone, without a proof.
        self.assertIn('- `Small.root` — odd numbers sum to a square — no proof', frontier)
        saved = {}
        for role in ROLES:
            with self.subTest(role=role, launch='initial'):
                folder = self.session('initial-' + role)
                self.pack(folder, role, {'batch': []} if role == 'organizer' else None)
                saved[role] = (folder / 'pack.md').read_bytes()
                lead, views = self.lead(folder), self.views(folder)
                opening, section = self.parts(lead, OPENING), self.parts(views, VIEWS)
                self.assertIn((self.instance / 'root.md').read_text(encoding='utf-8'), opening[OPENING[0]])
                # The root in Lean: where it stands, its declaration as written and as Lean prints it. The file is
                # named from the instance folder, which is the base the view gives for its relative references.
                self.assertIn('the declaration `Small.root` of the library `Small`, in `canon/lean/Small/Root.lean`',
                              opening[OPENING[1]])
                self.assertIn(f'Relative references in this research view use {self.instance} as their base.',
                              opening[OPENING[1]])
                self.assertIn('```lean\n/-- The sum of the first `n` odd numbers is the square of `n`. -/\n'
                              'theorem root (n : Nat) : oddSum n = n * n := by\n  sorry\n```', opening[OPENING[1]])
                self.assertIn('As Lean prints it: `Small.root (n : Nat) : oddSum n = n * n`', opening[OPENING[1]])
                self.assertIn(frontier, section[VIEWS[0]])
                self.assertIn('No exploration has written it yet.', section[VIEWS[1]])
                self.assertIn(board, section[VIEWS[2]])
                self.assertIn('## 001.txt\n\nUse convention K in new work.', section[VIEWS[3]])
                # The index is a derived view a session asks for; it is not delivered at launch.
                for delivered in (lead, views):
                    self.assertNotIn('index.md', delivered)
                    self.assertNotIn('# Index of the canon', delivered)

        # An exploration's change writes the understanding so far of q0. Later launches receive it with the
        # frontier as it then is; the packs of sessions already launched stay as they were.
        folder = self.candidate(understanding={'q0.md': UNDERSTANDING}, title='What the sum of odd numbers shows')
        self.publish(folder, role='explore', question='q0')
        current = (knowledge / 'frontier.md').read_text(encoding='utf-8')
        self.assertNotEqual(current, frontier)
        written = (self.instance / 'canon/questions/q0.md').read_text(encoding='utf-8')
        self.assertIn('## Review', written)
        for role in ROLES:
            with self.subTest(role=role, launch='later'):
                old = self.instance / 'sessions' / ('initial-' + role)
                self.assertEqual((old / 'pack.md').read_bytes(), saved[role])
                folder = self.session('later-' + role)
                self.pack(folder, role, {'batch': []} if role == 'organizer' else None)
                views = self.views(folder)
                self.assertIn(current, views)
                self.assertIn(written, self.parts(views, VIEWS)[VIEWS[1]])
                self.assertNotIn('No exploration has written it yet.', views)

    def test_launch_snapshot_keeps_references_research_views_and_assignment(self):
        # Role selection and reading order are checked for every role in
        # test_every_role_receives_its_ordered_guides_and_output_contract.
        self.changes_guides = True  # this test rewrites a guide, so it works on its own copy of the guides
        first = self.session('first')
        self.pack(first, 'peer', {'source': '/retained/source'})
        source = self.skill / 'reference/change-format.md'
        saved = (first / 'context/reference/change-format.md').read_bytes()
        source.write_text('Revised format for later launches.', encoding='utf-8')
        self.assertEqual((first / 'context/reference/change-format.md').read_bytes(), saved)
        text = (first / 'pack.md').read_text(encoding='utf-8')
        for heading in OPENING + VIEWS:
            self.assertIn('\n' + heading + '\n', text)
        self.assertIn('/retained/source', text)
        self.assertNotIn('Revised format for later launches.', text)
        later = self.session('later')
        self.pack(later, 'peer')
        self.assertIn('Revised format for later launches.', (later / 'pack.md').read_text(encoding='utf-8'))

    def test_input_json_holds_the_assignment_and_every_command_with_its_placeholders(self):
        folder = self.session('s1')
        task = {'source': '/retained/source', 'source_role': 'attempt'}
        inp = self.pack(folder, 'peer', task)
        self.assertEqual(read_json(folder / 'input.json'), inp)
        self.assertEqual((inp['instance'], inp['session'], inp['role'], inp['task'], inp['pipeline'], inp['revision']),
                         (str(self.instance), 's1', 'peer', task, None, 0))
        self.assertEqual(inp['references'], str(folder / 'context/reference'))
        self.assertEqual(inp['settings'], read_json(self.instance / 'settings.json'))
        runtime = INSTALLED / 'runtime'
        python, session = sys.executable, str(folder)
        coordination, tool = str(runtime / 'coordination.py'), str(runtime / 'canon_tool.py')
        self.assertEqual(inp['commands'], {
            'updates': [python, coordination, 'updates', session],
            'canon': [python, tool, '<command>', session],
            'prepare': [python, tool, 'prepare', session],
            'verify': [python, tool, 'verify', session],
            'lease': [python, coordination, 'lease', session, '<element>'],
            'wait': [python, coordination, 'wait', session, '<element>', '--timeout', '50'],
            'section': [python, coordination, 'section', session, '<element>', '--file', '<file>'],
            'release': [python, coordination, 'release', session, '<element>'],
            'question_lease': [python, coordination, 'question-lease', session, '<question>'],
            'question_wait': [python, coordination, 'question-wait', session, '<question>', '--timeout', '50'],
            'question_take': [python, coordination, 'question-take', session, '<question>'],
            'question_release': [python, coordination, 'question-release', session, '<question>'],
            'message': [python, coordination, 'message', session, '<recipient>', '--file', '<file>'],
            'check': [python, str(runtime / 'check.py'), session],
            'lean': [python, str(runtime / 'lean_broker.py'), '<command>', str(self.instance)],
        })
        for name, argv in inp['commands'].items():
            with self.subTest(command=name):
                self.assertTrue(Path(argv[1]).is_file())
        # The pack shows the same task, before the guides, and the same commands, after them, so a session
        # can act from either.
        pack = (folder / 'pack.md').read_text(encoding='utf-8')

        def shown(heading):
            return json.loads(pack.split('\n' + heading + '\n', 1)[1].split('```json\n', 1)[1].split('\n```', 1)[0])

        self.assertEqual(shown('# Your assignment'), {'task': task})
        self.assertEqual(shown('# Executable commands'), {'commands': inp['commands']})
        self.assertLess(pack.index('\n# Your assignment\n'), pack.index('<!-- begin '))
        self.assertLess(pack.rindex('<!-- end '), pack.index('\n# Executable commands\n'))
        prompt = (folder / 'prompt.txt').read_text(encoding='utf-8')
        self.assertIn(str(folder / 'pack.md'), prompt)
        self.assertIn(str(folder / 'input.json'), prompt)
        # The prompt gives the size of the pack as the file on disk has it, for reading the pack in ranges.
        written = (folder / 'pack.md').read_bytes()
        lines, size = written.count(b'\n'), len(written)
        self.assertIn(f'The file has {lines} lines in {size} bytes', prompt)

    def test_the_commands_of_input_json_run_once_their_placeholders_are_replaced(self):
        # A session has nothing but these argument arrays, so each kind is run as a session runs it.
        engine = Runner(self.instance, self.skill)
        attempt = self.running(engine, 'sattempt')
        commands = read_json(attempt / 'input.json')['commands']

        def run(argv, **replace):
            argv = [replace.get(part.strip('<>'), part) if part.startswith('<') else part for part in argv]
            self.assertFalse([part for part in argv if part.startswith('<')], 'a placeholder was left in place')
            result = subprocess.run(argv, capture_output=True, cwd=attempt)
            return result.returncode, result.stdout.decode('utf-8')

        code, text = run(commands['canon'], command='frontier')
        self.assertEqual(code, 0, text)
        self.assertIn('Root: Small.root · state: unresolved · revision 0', text)
        self.assertIn('- `Small.root` — odd numbers sum to a square — no proof', text)
        code, text = run(commands['updates'])
        self.assertEqual((code, json.loads(text)['root_state']), (0, 'unresolved'))
        code, text = run(commands['lease'], element='Small.root')
        self.assertEqual((code, json.loads(text)['leased']), (0, True), text)
        request = attempt / 'section.json'
        write_json(request, {'whole': True})
        code, text = run(commands['section'], element='Small.root', file=str(request))
        answer = json.loads(text)
        self.assertEqual((code, answer['registered'], answer['section']['element']), (0, True, 'Small.root'), text)
        code, text = run(commands['release'], element='Small.root')
        self.assertEqual((code, json.loads(text)['released']), (0, True), text)
        code, text = run(commands['wait'], element='Small.oddSum')
        self.assertEqual(code, 1, text)
        self.assertIn('definition', json.loads(text)['reason'])
        note = attempt / 'note.md'
        note.write_text('Our sections meet at n = 7.', encoding='utf-8')
        code, text = run(commands['message'], recipient='sattempt', file=str(note))
        self.assertEqual(code, 0, text)
        delivered = read_json(Path(json.loads(text)['delivered']))
        self.assertEqual((delivered['from'], delivered['text']), ('sattempt', 'Our sections meet at n = 7.'))
        code, text = run(commands['check'])
        self.assertEqual((code, json.loads(text)), (0, {'ok': True, 'errors': []}))
        code, text = run(commands['lean'], command='status')
        self.assertEqual((code, json.loads(text)['instance']), (0, str(self.instance)), text)

        # prepare is the peer's and verify the review's; a change without Lean is prepared without a build.
        peer = self.session('speer')
        candidate = self.candidate(approaches={'Small/root/induction.md': (
            '---\ntitle: Induction on the number of terms\nsessions: sattempt\n---\n## Idea\n\n'
            'Compare the sum for n + 1 with the sum for n.\n\n## Where it stops\n\nThe arithmetic is unchecked.\n')},
            prepare=False)
        (peer / 'output').rmdir()
        candidate.rename(peer / 'output')
        commands = self.pack(peer, 'peer')['commands']
        code, text = run(commands['prepare'])
        self.assertEqual((code, json.loads(text).get('ok')), (0, True), text)
        self.assertTrue(read_json(peer / 'output/prepared.json')['ok'])
        review = self.session('sreview')
        commands = self.pack(review, 'review', {'kind': 'candidate', 'candidate': str(peer / 'output')})['commands']
        with self.subTest(command='verify'):
            code, text = run(commands['verify'])
            self.assertEqual((code, json.loads(text).get('ok')), (0, True), text)
            self.assertTrue(read_json(review / 'work/verify/outcome.json')['ok'])
        # Each is refused to the other role, with the reason.
        code, text = run(commands['prepare'])
        self.assertEqual(code, 1, text)
        self.assertIn('a peer or an organizer', json.loads(text)['error'])

    def test_worker_commands_keep_auth_separate_from_customizations(self):
        folder = self.session('isolated')
        server = {'explicit': {'command': sys.executable, 'args': ['server.py']}}
        codex = worker_command('codex', 'codex/gpt-6.1-sol', 'xhigh', folder, server)
        # Retention copies the CLI's native transcript, so the worker session must persist.
        self.assertNotIn('--ephemeral', codex.argv)
        self.assertIn('--ignore-user-config', codex.argv)
        self.assertIn('--ignore-rules', codex.argv)
        self.assertIn('project_doc_max_bytes=0', codex.argv)
        self.assertIn('skip_host_skill_discovery', codex.argv)
        overrides = [codex.argv[i+1] for i, value in enumerate(codex.argv[:-1]) if value == '-c']
        # Codex splits a dotted override key literally, so a quoted component such as
        # mcp_servers."explicit".command becomes part of the server's name. TOML parsing
        # strips those quotes and would accept that form, so also require one whole-table override.
        self.assertEqual([value.partition('=')[0] for value in overrides if value.startswith('mcp_servers')],
                         ['mcp_servers'])
        self.assertEqual(tomllib.loads('\n'.join(overrides))['mcp_servers'], server)
        self.assertEqual(tomllib.loads('\n'.join(overrides))['developer_instructions'], '')
        for name in ('hooks', 'memories', 'plugins', 'apps', 'multi_agent'):
            self.assertTrue(any(codex.argv[i:i+2] == ['--disable', name] for i in range(len(codex.argv))))
        claude = worker_command('claude', 'claude/opus', 'xhigh', folder, server)
        self.assertNotIn('--no-session-persistence', claude.argv)
        self.assertNotIn('--bare', claude.argv)
        self.assertEqual(claude.argv[claude.argv.index('--setting-sources') + 1], '')
        # The two files asserted below reach the CLI only through these arguments.
        self.assertEqual(claude.argv[claude.argv.index('--settings') + 1], str(folder / 'worker-settings.json'))
        self.assertEqual(claude.argv[claude.argv.index('--mcp-config') + 1], str(folder / 'worker-mcp.json'))
        self.assertIn('--disable-slash-commands', claude.argv)
        self.assertIn('--strict-mcp-config', claude.argv)
        config = read_json(folder / 'worker-settings.json')
        self.assertTrue(config['disableAllHooks'])
        self.assertFalse(config['autoMemoryEnabled'])
        self.assertEqual(config['claudeMdExcludes'], ['**'])
        self.assertEqual(read_json(folder / 'worker-mcp.json')['mcpServers'], server)
        # A worker launched from an operator's Codex or Claude session starts a session of its own, not a nested one.
        parent = dict.fromkeys(('CODEX_THREAD_ID', 'CODEX_SESSION_ID', 'CLAUDE_CODE_SESSION_ID', 'CLAUDECODE'), 'parent')
        with patch.dict('os.environ', {**parent, 'TASK_PROBE': 'kept'}):
            env = worker_environment()
            self.assertEqual(set(parent) & set(env), set())
            self.assertEqual(env['TASK_PROBE'], 'kept')

    def test_a_worker_is_launched_without_the_tools_it_is_asked_to_withhold_and_with_all_of_them_otherwise(self):
        folder = self.session('withheld')
        plain = worker_command('claude', 'claude/opus', 'xhigh', folder, {})
        without = worker_command('claude', 'claude/opus', 'xhigh', folder, {}, withheld=('ScheduleWakeup', 'Monitor'))
        codex = worker_command('codex', 'codex/gpt-6.1-sol', 'xhigh', folder, {}, withheld=('ScheduleWakeup',))
        self.assertNotIn('--disallowedTools', plain.argv)
        self.assertEqual(without.argv[without.argv.index('--disallowedTools') + 1], 'ScheduleWakeup,Monitor')
        self.assertEqual(without.argv[:-2], plain.argv)
        self.assertNotIn('--disallowedTools', codex.argv)

    def test_runner_dispatch_launches_the_isolated_worker_command(self):
        # The session host executes launch.json, so the runner must record the isolated
        # worker command with the instance's explicit tools, not the bare base command.
        engine = Runner(self.instance, self.skill)
        engine.settings['mcp_servers'] = {'explicit': {'command': sys.executable, 'args': ['server.py']}}
        key = engine.producer('attempt')
        with patch('runner.subprocess.Popen') as host:
            host.return_value.pid = engine.identity['pid']
            self.assertTrue(engine.dispatch(key))
        sid = engine.state['jobs'][key]['session']
        session = engine.state['sessions'][sid]
        launched = read_json(engine.session_dir(sid) / 'launch.json')['command']['argv']
        expected = worker_command(engine.settings['cli'][session['provider']], session['model'],
                                  session['effort'], engine.session_dir(sid), engine.settings['mcp_servers'])
        self.assertEqual(launched, expected.argv)

    def test_context_request_applies_to_every_worker_model(self):
        folder = self.session('long-context')
        for model in ('codex/gpt-6.1-sol', 'codex/gpt-6-astra', 'codex/custom-model'):
            with self.subTest(model=model):
                command = worker_command('codex', model, 'xhigh', folder)
                overrides = [command.argv[i + 1] for i, arg in enumerate(command.argv[:-1]) if arg == '-c']
                config = tomllib.loads('\n'.join(overrides))
                self.assertEqual(config['model_context_window'], 1_000_000)
                self.assertEqual(config['model_auto_compact_token_limit'], 900_000)
                self.assertEqual(command.argv[command.argv.index('--model') + 1], model.split('/', 1)[1])
                self.assertEqual(command.argv[-1], '-')
        for model, expected in (
            ('claude/opus', 'opus[1m]'), ('claude/sonnet', 'sonnet[1m]'),
            ('claude/haiku', 'haiku[1m]'), ('claude/custom-model', 'custom-model[1m]'),
            ('claude/claude-opus-4-6', 'claude-opus-4-6[1m]'),
            ('claude/opus[1m]', 'opus[1m]'), ('claude/opus[1M]', 'opus[1m]'),
            ('claude/sonnet[200k]', 'sonnet[1m]'),
        ):
            with self.subTest(model=model):
                command = worker_command('claude', model, 'xhigh', folder)
                self.assertEqual(command.argv[command.argv.index('--model') + 1], expected)
                self.assertIn('--strict-mcp-config', command.argv)
        with patch.dict(os.environ, {'CLAUDE_CODE_DISABLE_1M_CONTEXT': '1',
                                     'CLAUDE_AUTOCOMPACT_PCT_OVERRIDE': '20',
                                     'CLAUDE_CODE_AUTO_COMPACT_WINDOW': '200000'}):
            environment = worker_environment()
            self.assertNotIn('CLAUDE_CODE_DISABLE_1M_CONTEXT', environment)
            self.assertNotIn('CLAUDE_AUTOCOMPACT_PCT_OVERRIDE', environment)
            self.assertEqual(environment['CLAUDE_CODE_AUTO_COMPACT_WINDOW'], '900000')
            self.assertEqual(os.environ['CLAUDE_CODE_AUTO_COMPACT_WINDOW'], '200000')
        with patch.dict(os.environ, {'CLAUDE_CODE_MAX_OUTPUT_TOKENS': '32000'}):
            # The worker's output cap is explicit, not the operator's or the CLI default.
            self.assertEqual(worker_environment()['CLAUDE_CODE_MAX_OUTPUT_TOKENS'], '128000')
        # A configured MCP server that starts slowly under load must still be attached (reference/operations.md).
        with patch.dict(os.environ, {'MCP_TIMEOUT': '5000'}):
            self.assertEqual(worker_environment()['MCP_TIMEOUT'], '180000')
        # Sub-agents a worker left running when its turn ended get two hours, not the CLI's default ten
        # minutes (reference/operations.md).
        with patch.dict(os.environ, {'CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS': '600000'}):
            self.assertEqual(worker_environment()['CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS'], '7200000')

    def test_withdrawn_proof_keeps_its_explanation_visible(self):
        self.prove_root(INFORMAL)
        self.assertEqual(replay(self.instance)['root_state'], 'informal_proved')
        self.event('v1', 'review', {'feedback': 'feedback.md', 'findings': [{
            'concerns': [], 'status': 'confirmed', 'reason': 'The quantified domain was narrower than the statement.',
            'invalidates': ['Small.root']}]})
        model = replay(self.instance)
        render(self.instance, model, [])
        self.assertEqual(model['root_state'], 'unresolved')
        self.assertEqual(model['elements']['Small.root']['standing'], 'not_confirmed')
        self.assertEqual(model['remaining'], ['Small.root'])
        # The root is work that remains again, and the line that says so carries the reason.
        frontier = (self.instance / 'knowledge/frontier.md').read_text(encoding='utf-8')
        self.assertIn('- `Small.root` — odd numbers sum to a square — proof not confirmed: '
                      'The quantified domain was narrower than the statement.', frontier)
        # The element's own view names the review that withdrew the confirmation.
        shown = view(self.instance, model, 'Small.root')
        self.assertIn('later review  v1 (confirmed): The quantified domain was narrower than the statement.', shown)
        # Only a proof confirmed as correct is accepted, so the verdict shown for a withdrawn proof is not "accepted".
        verdict = next(line for line in shown.splitlines() if line.startswith('verdict'))
        self.assertIn('not_confirmed', verdict)
        self.assertNotIn(', accepted', verdict)

    def test_root_completion_only_gates_new_producers_and_reopens_on_loss(self):
        engine = Runner(self.instance, self.skill)
        folder = self.running(engine, 'running')
        # The root is proved in Lean; the same change leaves a lead that no proof of the root uses.
        self.prove_root(FORMAL, engine=engine, modules={'Small/Lead.lean': LEAD},
                        records={'Small/lead.md': record_text('Doubling the number of terms multiplies the sum by four.')})
        self.assertEqual(engine.model['root_state'], 'formal_proved')
        self.assertTrue(engine.state['complete'])
        self.assertTrue(take(folder, 'Small.lead')['registered'])
        queued = [engine.producer(role) for role in ('attempt', 'explore')]
        review = engine.enqueue('review', {'kind': 'comprehensive', 'concerns': [], 'conflicts': []})
        with patch.object(engine, 'populate'), patch.object(engine, 'dispatch') as dispatch, \
             patch.object(engine, 'producer') as producer:
            engine.schedule()
            producer.assert_not_called()
        self.assertEqual([call.args[0] for call in dispatch.call_args_list], [review])
        for key in queued:
            self.assertEqual(engine.state['jobs'][key]['status'], 'cancelled')
            pipeline = engine.state['jobs'][key]['pipeline']
            self.assertEqual(engine.state['pipelines'][pipeline]['stage'], 'done')
        self.assertEqual(engine.state['sessions']['running']['status'], 'running')
        self.assertEqual(engine.state['jobs'][engine.state['sessions']['running']['job']]['status'], 'running')
        self.event('v1', 'review', {'feedback': 'feedback.md', 'findings': [{
            'concerns': [], 'status': 'confirmed', 'reason': 'Support withdrawn.', 'invalidates': ['Small.root']}]})
        engine.model = replay(self.instance)
        with patch.object(engine, 'collect'), patch.object(engine, 'ensure_broker'), patch.object(engine, 'archive'), \
             patch.object(engine, 'schedule') as schedule:
            engine.tick()
        self.assertFalse(engine.state['complete'])
        schedule.assert_called_once()

    def test_every_role_receives_its_ordered_guides_and_output_contract(self):
        research = ['what-research-is-for.md', 'user-writing-preferences.md']
        # sections.md goes to the roles that register sections, and records.md to the roles that write or
        # judge the written texts of the canon.
        references = {
            'attempt': research + ['literature.md', 'sections.md', 'retained-work.md'],
            'explore': research + ['literature.md', 'retained-work.md'],
            'formalizer': ['retained-work.md'],
            'peer': research + ['literature.md', 'sections.md', 'retained-work.md', 'records.md', 'change-format.md'],
            'review': research + ['literature.md', 'records.md', 'change-format.md', 'review-output.md'],
            'organizer': research + ['records.md', 'change-format.md', 'organizer-output.md'],
        }
        for role, specialized in references.items():
            with self.subTest(role=role):
                folder = self.session('reading-' + role)
                inp = self.pack(folder, role, {'batch': []} if role == 'organizer' else None)
                # Every role states mathematics in Lean and reads the canon, so the canon and Lean guides
                # are common to all of them, between the writing guide and the tools.
                expected = ['reference/common.md', 'roles/' + role + '.md', 'reference/writing.md',
                            'reference/canon.md', 'reference/lean.md', 'reference/tools.md']
                expected += ['reference/' + name for name in specialized]
                self.assertEqual(inp['documents'], expected)
                body = (folder / 'pack.md').read_text(encoding='utf-8')
                previous_end = -1
                for name in expected:
                    marker = '<!-- begin ' + name + ' -->'
                    begin = body.index(marker)
                    self.assertGreater(begin, previous_end)
                    previous_end = body.index('<!-- end ' + name + ' -->', begin)
                    snapshot = folder / 'context' / name
                    self.assertEqual(snapshot.read_bytes(), (self.skill / name).read_bytes())
                    expected_body = rebase_links(snapshot.read_text(encoding='utf-8-sig'),
                                                 snapshot, folder, folder / 'context')
                    self.assertEqual(body[begin + len(marker):previous_end].strip(),
                                     expected_body.strip(), name)
                # The root and the assignment come before the first guide, and every other research view
                # comes after the last one.
                first = body.index('<!-- begin ' + expected[0] + ' -->')
                for heading in OPENING:
                    self.assertLess(body.index('\n' + heading + '\n'), first)
                self.assertLess(previous_end, body.index('\n# Frontier at launch\n', previous_end))
                self.assertEqual([p.name for p in (folder / 'context/roles').iterdir()],
                                 [role + '.md'])
                # The snapshot holds every reference, so a link from a guide to another one leads to a copy.
                self.assertEqual(sorted(p.name for p in (folder / 'context/reference').iterdir()),
                                 sorted(p.name for p in (self.skill / 'reference').glob('*.md')))
                # It holds the operator's entry point as well, which reference/operations.md links to.
                self.assertEqual((folder / 'context/SKILL.md').read_bytes(), (self.skill / 'SKILL.md').read_bytes())

    def test_the_account_guide_goes_only_to_the_peer_and_the_review_of_the_text_of_q0(self):
        account = 'reference/q0-account.md'
        carrying = self.candidate(understanding={'q0.md': UNDERSTANDING}, prepare=False)
        other = self.candidate(understanding={'narrower.md': UNDERSTANDING}, prepare=False)
        # A peer's assignment names the question its producer held. A review's names the candidate folder,
        # and a comprehensive review's names none.
        cases = [('peer', {'source_role': 'explore', 'question': 'q0'}, True),
                 ('peer', {'source_role': 'explore', 'question': 'narrower'}, False),
                 ('review', {'kind': 'candidate', 'candidate': str(carrying)}, True),
                 ('review', {'kind': 'candidate', 'candidate': str(other)}, False),
                 ('review', {'kind': 'comprehensive', 'concerns': [], 'conflicts': []}, False),
                 ('explore', {'question': 'q0'}, False)]
        for number, (role, task, expected) in enumerate(cases):
            with self.subTest(role=role, task=task):
                folder = self.session(f'account-{number}')
                inp = self.pack(folder, role, task)
                self.assertEqual(account in inp['documents'], expected)
                if expected:
                    # The guide is the last of the role's guides, embedded in the pack like the others.
                    self.assertEqual(inp['documents'][-1], account)
                body = (folder / 'pack.md').read_text(encoding='utf-8')
                self.assertEqual('<!-- begin ' + account + ' -->' in body, expected)


if __name__ == '__main__':
    unittest.main()
