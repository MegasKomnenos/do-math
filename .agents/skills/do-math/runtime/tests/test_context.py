"""Actual launch snapshots, instruction isolation and current research updates."""
from pathlib import Path
import sys
import tomllib
import os
import json
import subprocess
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from context import assemble, rebase_links
from coordination import updates, claim
from knowledge import render, replay
from launch import worker_command, worker_environment
from runner import Runner, initialize
from runtime_support import read_json, write_json
from test_research import InstanceCase, record, claim_row, solution, assessment


class ContextTests(InstanceCase):
    def test_cli_json_preserves_unicode_under_ascii_output_environment(self):
        instance = self.root / '연구'
        initialize(instance, self.root / 'goal.md')
        session = instance / 'sessions/s1'; session.mkdir()
        write_json(session / 'input.json', {'instance': str(instance), 'session': 's1', 'role': 'attempt',
                                           'user_inputs': [{'id': 'initial', 'text': 'Use ℕ, including zero.'}]})
        runtime = Path(__file__).resolve().parents[1]
        for script, args in [('runner.py', ['status', str(instance)]),
                             ('coordination.py', ['updates', str(session)]),
                             ('lean_broker.py', ['status', str(instance)])]:
            with self.subTest(script=script):
                result = subprocess.run([sys.executable, '-B', str(runtime / script), *args],
                                        capture_output=True, env={**os.environ, 'PYTHONIOENCODING': 'ascii'})
                self.assertEqual(result.returncode, 0, result.stderr)
                data = json.loads(result.stdout.decode('utf-8'))
                if script == 'coordination.py':
                    self.assertEqual(data['user_inputs'][0]['text'], 'Use ℕ, including zero.')
                else:
                    self.assertEqual(data['instance'], str(instance))

    def test_instruction_links_lead_to_snapshot_and_research_text_stays_verbatim(self):
        session = self.instance / 'sessions/s1'
        context = session / 'context'
        text = rebase_links('[Evidence](../reference/evidence.md)', context / 'roles/attempt.md', session, context)
        self.assertEqual(text, '[Evidence](context/reference/evidence.md)')
        folder = self.session('s1')
        root = 'Consider the expression \\([n](x)\\) with its original notation.'
        (self.instance / 'root.md').write_text(root, encoding='utf-8')
        assemble(self.skill, self.instance, folder, 'attempt', {}, None, 0,
                 read_json(self.instance / 'settings.json'))
        self.assertIn(root, (folder / 'pack.md').read_text(encoding='utf-8'))

    def session(self, name, role='attempt'):
        folder = self.instance / 'sessions' / name
        folder.mkdir()
        (folder / 'inbox').mkdir()
        return folder

    def pack(self, folder, role='attempt', task=None):
        engine = Runner(self.instance, self.skill)
        return assemble(self.skill, self.instance, folder, role, task or {}, None, 0, engine.settings)

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
        data = record([claim_row('p')], solutions=[solution('s', 'root', 'p')])
        self.publish('r1', data)
        self.assertEqual(updates(first)['root_state'], 'informal_proved')

    def test_every_role_receives_the_complete_current_glossary_at_launch(self):
        terms = [
            {'id': 'pending', 'name': 'Pending object', 'symbol': 'Ω',
             'definition': 'For every n in ℕ, Ω(n) is n + 1, including n = 0.',
             'global_candidate': True},
            {'id': 'permanent', 'name': 'Permanent object', 'symbol': 'Λ',
             'definition': 'Λ is the set of natural numbers greater than zero.',
             'global_candidate': True},
        ]
        self.publish('rterms', record(glossary=terms))
        self.event('oterms', 'organization', {
            'batch': ['rterms'], 'modules': [], 'shared_context': ['rterms'],
            'promote': ['rterms/permanent']})
        render(self.instance, replay(self.instance), [])
        glossary = (self.instance / 'knowledge/glossary.md').read_text(encoding='utf-8')
        self.assertIn('Membership: candidate', glossary)
        self.assertIn('Membership: permanent', glossary)
        for term in terms:
            self.assertIn(term['definition'], glossary)
        roles = ('attempt', 'explore', 'formalizer', 'peer', 'review', 'organizer')
        saved = {}
        for role in roles:
            with self.subTest(role=role, launch='initial'):
                folder = self.session('initial-' + role)
                self.pack(folder, role)
                self.assertIn(glossary, (folder / 'pack.md').read_text(encoding='utf-8'))
                saved[role] = (folder / 'pack.md').read_bytes()

        self.publish('rnew', record(glossary=[{
            'id': 'later', 'name': 'Later object', 'symbol': 'Ξ',
            'definition': 'Ξ is the singleton set containing zero.',
            'global_candidate': True}]))
        render(self.instance, replay(self.instance), [])
        current = (self.instance / 'knowledge/glossary.md').read_text(encoding='utf-8')
        self.assertIn('Ξ is the singleton set containing zero.', current)
        self.assertNotEqual(current, glossary)
        for role in roles:
            with self.subTest(role=role, launch='later'):
                old = self.instance / 'sessions' / ('initial-' + role)
                self.assertEqual((old / 'pack.md').read_bytes(), saved[role])
                folder = self.session('later-' + role)
                self.pack(folder, role)
                self.assertIn(current, (folder / 'pack.md').read_text(encoding='utf-8'))

    def test_references_are_snapshots_and_pack_contains_only_assigned_role(self):
        first = self.session('first')
        self.pack(first, 'peer', {'source': '/retained/source'})
        source = self.skill / 'reference/record-format.md'
        saved = (first / 'context/reference/record-format.md').read_bytes()
        source.write_text('Revised format for later launches.', encoding='utf-8')
        self.assertEqual((first / 'context/reference/record-format.md').read_bytes(), saved)
        self.assertEqual([p.name for p in (first / 'context/roles').iterdir()], ['peer.md'])
        text = (first / 'pack.md').read_text(encoding='utf-8')
        self.assertIn('Full current global glossary', text)
        self.assertIn('General index at launch', text)
        self.assertIn('/retained/source', text)
        self.assertNotIn('Revised format', text)
        self.assertLess(text.index('<!-- begin reference/common.md -->'), text.index('<!-- begin roles/peer.md -->'))
        self.assertLess(text.index('<!-- begin roles/peer.md -->'), text.index('<!-- begin reference/writing.md -->'))
        self.assertLess(text.index('<!-- begin reference/tools.md -->'), text.index('<!-- begin reference/record-format.md -->'))

    def test_worker_commands_keep_auth_separate_from_customizations(self):
        folder = self.session('isolated')
        server = {'explicit': {'command': sys.executable, 'args': ['server.py']}}
        codex = worker_command('codex', 'codex/gpt-6.1-sol', 'xhigh', folder, server)
        self.assertIn('--ignore-user-config', codex.argv)
        self.assertIn('project_doc_max_bytes=0', codex.argv)
        self.assertIn('skip_host_skill_discovery', codex.argv)
        overrides = [codex.argv[i+1] for i, value in enumerate(codex.argv[:-1]) if value == '-c']
        self.assertEqual(tomllib.loads('\n'.join(overrides))['mcp_servers'], server)
        for name in ('hooks', 'memories', 'plugins', 'apps', 'multi_agent'):
            self.assertTrue(any(codex.argv[i:i+2] == ['--disable', name] for i in range(len(codex.argv))))
        claude = worker_command('claude', 'claude/opus', 'xhigh', folder, server)
        self.assertNotIn('--bare', claude.argv)
        self.assertEqual(claude.argv[claude.argv.index('--setting-sources') + 1], '')
        self.assertIn('--strict-mcp-config', claude.argv)
        config = read_json(folder / 'worker-settings.json')
        self.assertTrue(config['disableAllHooks'])
        self.assertFalse(config['autoMemoryEnabled'])
        self.assertEqual(config['claudeMdExcludes'], ['**'])
        self.assertEqual(read_json(folder / 'worker-mcp.json')['mcpServers'], server)
        with patch.dict('os.environ', {'CODEX_THREAD_ID': 'parent', 'CODEX_SESSION_ID': 'parent', 'TASK_PROBE': 'kept'}):
            env = worker_environment()
            self.assertNotIn('CODEX_THREAD_ID', env)
            self.assertEqual(env['TASK_PROBE'], 'kept')

    def test_withdrawn_solution_keeps_its_explanation_visible(self):
        data = record([claim_row('p')], solutions=[solution('p', 'root', 'p')])
        self.publish('r1', data, assessment(data, ['p']))
        self.event('v1', 'review', {'findings': [{'concerns': [], 'status': 'confirmed',
            'reason': 'The quantified domain was narrower than the node.', 'invalidates': [{'record': 'r1', 'claim': 'p'}]}]})
        model = replay(self.instance)
        render(self.instance, model, [])
        self.assertEqual(model['nodes']['root']['state'], 'unresolved')
        for file in ('frontier.md', 'index.md'):
            text = (self.instance / 'knowledge' / file).read_text(encoding='utf-8')
            self.assertIn('quantified domain', text)
            self.assertIn('reviews/v1/assessment.json', text)

    def test_root_completion_only_gates_new_producers_and_reopens_on_loss(self):
        engine = Runner(self.instance, self.skill)
        key = engine.producer('attempt')
        sid = 'running'
        folder = self.session(sid)
        self.pack(folder)
        engine.state['pipelines'][engine.state['jobs'][key]['pipeline']]['producer'] = sid
        engine.state['jobs'][key].update(status='running', session=sid)
        engine.state['sessions'][sid] = {'id': sid, 'role': 'attempt', 'status': 'running', 'job': key}
        engine.save()
        self.publish('r0', self.reduction())
        data = record([claim_row('p')], solutions=[solution('p', 'root', 'p')])
        self.publish('r1', data, assessment(data, ['p']))
        engine.model = replay(self.instance); engine.state['complete'] = True
        self.assertEqual(claim(folder, 'Q')['nodes'], ['Q'])
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
        self.assertEqual(engine.state['sessions'][sid]['status'], 'running')
        self.assertEqual(engine.state['jobs'][engine.state['sessions'][sid]['job']]['status'], 'running')
        self.event('v1', 'review', {'findings': [{'concerns': [], 'status': 'confirmed', 'reason': 'Support withdrawn.',
            'invalidates': [{'record': 'r1', 'claim': 'p'}]}]})
        engine.model = replay(self.instance)
        with patch.object(engine, 'collect'), patch.object(engine, 'ensure_broker'), patch.object(engine, 'archive'), \
             patch.object(engine, 'schedule') as schedule:
            engine.tick()
        self.assertFalse(engine.state['complete'])
        schedule.assert_called_once()

    def test_every_role_receives_its_ordered_guides_and_output_contract(self):
        references = {
            'attempt': ['retained-work.md'],
            'explore': ['retained-work.md'],
            'formalizer': ['retained-work.md', 'lean.md'],
            'peer': ['record-format.md'],
            'review': ['record-format.md', 'review-output.md'],
            'organizer': ['organizer-output.md'],
        }
        for role, specialized in references.items():
            with self.subTest(role=role):
                folder = self.session('reading-' + role)
                inp = self.pack(folder, role)
                expected = ['reference/common.md', 'roles/' + role + '.md',
                            'reference/writing.md', 'reference/tools.md']
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
                self.assertEqual([p.name for p in (folder / 'context/roles').iterdir()],
                                 [role + '.md'])


if __name__ == '__main__':
    unittest.main()
