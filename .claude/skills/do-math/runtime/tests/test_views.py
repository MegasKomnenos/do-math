from pathlib import Path
import sys
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import knowledge
from test_research import InstanceCase, record


class ViewTests(InstanceCase):
    def organized_model(self):
        self.publish('r1', record())
        self.event('o1', 'organization', {
            'batch': ['r1'], 'shared_context': ['r1'],
            'modules': [{'id': name, 'title': name, 'description': 'Full reading guidance.',
                         'records': ['r1']} for name in ('a', 'b')],
        })
        return knowledge.replay(self.instance)

    def test_identical_render_does_not_replace_files(self):
        model = self.organized_model()
        knowledge.render(self.instance, model, [])
        with patch('knowledge.write_text') as text, patch('knowledge.write_json') as data:
            knowledge.render(self.instance, model, [])
        text.assert_not_called()
        data.assert_not_called()

    def test_board_change_only_writes_board(self):
        model = self.organized_model()
        knowledge.render(self.instance, model, [])
        rows = [{'pipeline': 'p1', 'session': 's1', 'role': 'attempt',
                 'stage': 'producing', 'nodes': ['root'], 'sections': [], 'question': None}]
        with patch('knowledge.write_text', wraps=knowledge.write_text) as text, \
                patch('knowledge.write_json') as data:
            knowledge.render(self.instance, model, rows)
        self.assertEqual([call.args[0].name for call in text.call_args_list], ['board.md'])
        data.assert_not_called()
        board = (self.instance / 'knowledge/board.md').read_text(encoding='utf-8')
        self.assertIn('not process liveness', board)
        self.assertIn('producer: s1', board)

    def test_unreadable_existing_view_is_not_treated_as_missing(self):
        model = self.organized_model()
        knowledge.render(self.instance, model, [])
        original = Path.read_bytes

        def unreadable(path):
            if path.name == 'frontier.md':
                raise PermissionError('view locked')
            return original(path)

        with patch.object(Path, 'read_bytes', unreadable), patch('knowledge.write_text') as text:
            with self.assertRaisesRegex(PermissionError, 'view locked'):
                knowledge.render(self.instance, model, [])
        text.assert_not_called()

    def test_merged_notation_keeps_source_scope_and_original_definition(self):
        for rid, symbol in [('r1', 'q'), ('r2', 'c')]:
            self.publish(rid, record(glossary=[{
                'id': 't', 'name': 'Exact count', 'symbol': symbol,
                'definition': 'Historical definition; unresolved at publication.',
                'global_candidate': True,
            }]))
        self.event('o1', 'organization', {
            'batch': ['r1', 'r2'], 'shared_context': ['r1', 'r2'], 'modules': [],
            'merge_terms': [{'keep': 'r1/t', 'others': ['r2/t'], 'reason': 'Same count.'}],
        })
        model = knowledge.replay(self.instance)
        knowledge.render(self.instance, model, [])
        glossary = (self.instance / 'knowledge/glossary.md').read_text(encoding='utf-8')
        self.assertIn('Symbol: q', glossary)
        self.assertIn('Historical name/symbol: Exact count (c)', glossary)
        self.assertIn('[local definition](records/r2/record.json) — r2/t', glossary)
        self.assertIn('Historical definition; unresolved at publication.', glossary)
        self.assertIn('[frontier](frontier.md) for current node status', glossary)
        self.assertNotIn('Aliases:', glossary)

    def test_changed_research_updates_views_and_retains_module_evidence(self):
        model = self.organized_model()
        knowledge.render(self.instance, model, [])
        self.publish('r2', record())
        model = knowledge.replay(self.instance)
        knowledge.render(self.instance, model, [])
        base = self.instance / 'knowledge'
        self.assertEqual(knowledge.read_json(base / 'state.json'), model)
        for name in ('frontier.md', 'glossary.md', 'index.md', 'board.md', 'index/a.md', 'index/b.md'):
            # The frontier heads its revision line differently from the other views.
            label = 'Revision' if name == 'frontier.md' else 'Research revision'
            self.assertIn(f"{label}: {model['sequence']}\n", (base / name).read_text(encoding='utf-8'))
        for name in ('a', 'b'):
            module = (base / 'index' / (name + '.md')).read_text(encoding='utf-8')
            self.assertIn('Full reading guidance.', module)
            self.assertIn('A precise contribution with its limitations.', module)
            self.assertIn('[Review](../records/r1/review/assessment.json)', module)
        index = (base / 'index.md').read_text(encoding='utf-8')
        self.assertIn('records/r2/record.json', index.split('## Unfiled records')[1])

    def test_root_statement_is_read_as_in_the_launch_context(self):
        # init keeps root.md's bytes; a UTF-8 byte order mark is not part of the statement.
        root = self.instance / 'root.md'
        statement = root.read_text(encoding='utf-8')
        root.write_bytes(b'\xef\xbb\xbf' + statement.encode('utf-8'))
        model = knowledge.replay(self.instance)
        self.assertEqual(model['nodes']['root']['statement'], statement)
        knowledge.render(self.instance, model, [])
        self.assertIn('## root\n\n' + statement + '\n',
                      (self.instance / 'knowledge/frontier.md').read_text(encoding='utf-8'))
