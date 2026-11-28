"""Tests of the search by meaning and of the blind descent test (search.py, light.py).

tests/light_cli.py stands in for the Claude CLI: the settings of the test instance name a small command
file that starts it, so the command line that light.py builds, the environment, the slots and the reading
of the stream are the real ones. The process that does the work of a search is run inside the test
process (`inline`), except where a test is about that process itself.
"""
import copy
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import time
import unittest
from unittest.mock import patch

sys.path[:0] = [str(Path(__file__).resolve().parents[1]), str(Path(__file__).resolve().parent)]
import canon_index
import light
import search
from canon_tool import head, main as canon_tool_main
from knowledge import replay
from runner import Runner, search_usage
from runtime_support import read_json, write_json
from support import InstanceCase, module_text, record_text, theorem

HERE = Path(__file__).resolve().parent
NOTHING = '{"hits": [], "unpublished": []}'
RELATED = search.GROUPS[1][1]  # the line above the related hits of a section
LINES = {'Small.Defs': 'The definition of the sum of the first odd numbers.',
         'Small.Sums.Low': 'Values of the sum for zero and two terms.',
         'Small.Sums.High': 'Values of the sum for three terms.',
         'Small.Steps.Next': 'How the sum changes when one more odd number is added.'}
FOLDERS = {'Small.Sums': 'Particular values of the sum of the first odd numbers, each computed outright.\n\n'
                         'It serves as a stock of base cases.',
           'Small.Steps': 'Statements that pass from one number of terms to the next.'}


class Ended:
    """What `search.start` returns in a test that does the work inside the test process: a process that has ended."""

    def poll(self):
        return 0


def inline(folder):
    search.work(folder)
    return Ended()


def answer(**lists):
    return json.dumps(lists)


class SearchCase(InstanceCase):
    """A canon of two folders, two modules directly under the library and six elements, with descriptions."""

    def setUp(self):
        super().setUp()
        # The name of a scenario is its key for the whole test process; test_index keeps another canon as 'filed'.
        self.scenario('filed for the search', self.filed)
        # The descriptions as a canon holds them: the files, and the summary that a publication gathers from them.
        for kind, texts in (('module', LINES), ('folder', FOLDERS)):
            for name, text in texts.items():
                path = canon_index.description_file(self.instance / 'canon', kind, name)
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text + '\n', encoding='utf-8', newline='\n')
        write_json(self.instance / 'canon' / 'descriptions.json', {
            'modules': {name: {'text': text + '\n', 'revision': 1, 'tested': True} for name, text in LINES.items()},
            'folders': {name: {'text': text + '\n', 'revision': 1, 'tested': True, 'boundary': None}
                        for name, text in FOLDERS.items()}})
        self.scenario_folder = self.root / 'cli'
        self.scenario_folder.mkdir()
        self.script([])
        # The command file that the settings name as the Claude CLI. It hands every argument on to the stand-in.
        if os.name == 'nt':
            cli = self.root / 'claude.cmd'
            cli.write_text(f'@"{sys.executable}" -B "{HERE / "light_cli.py"}" "{self.scenario_folder}" %*\r\n',
                           encoding='utf-8')
        else:
            cli = self.root / 'claude'
            cli.write_text(f'#!/bin/sh\nexec "{sys.executable}" -B "{HERE / "light_cli.py"}" '
                           f'"{self.scenario_folder}" "$@"\n', encoding='utf-8')
            cli.chmod(0o755)
        self.configure(cli={'codex': 'codex', 'claude': str(cli)},
                       search={'model': 'claude/sonnet', 'effort': 'low', 'parallel': 2})
        started = patch.object(search, 'start', side_effect=inline)
        started.start()
        self.addCleanup(started.stop)
        self.inline = started
        self.home = self.instance / 'runner' / 'search'

    def filed(self):
        folder = self.candidate(
            modules={'Small/Sums/Low.lean': module_text('\n\n'.join([theorem('sumZero', ': oddSum 0 = 0'),
                                                                     theorem('sumTwo', ': oddSum 2 = 4')])),
                     'Small/Sums/High.lean': module_text(theorem('sumThree', ': oddSum 3 = 9')),
                     'Small/Steps/Next.lean': module_text(theorem(
                         'sumSucc', '(n : Nat) : oddSum (n + 1) = oddSum n + (2 * n + 1)'))},
            records={'Small/sumZero.md': record_text('The empty sum is zero.', weight='unit'),
                     'Small/sumTwo.md': record_text('The first two odd numbers sum to four.', weight='unit'),
                     'Small/sumThree.md': record_text('The first three odd numbers sum to nine.'),
                     'Small/sumSucc.md': record_text('Passing from n to n + 1 adds the odd number 2n + 1.')})
        self.publish(folder)

    def script(self, rules):
        write_json(self.scenario_folder / 'script.json', rules)

    def calls(self):
        folder = self.scenario_folder / 'calls'
        return [read_json(path) for path in sorted(folder.glob('*.json'))] if folder.is_dir() else []

    def command(self, *argv, main=search.main):
        """The exit code and the output of one command line of search.py, or of the canon tool."""
        stream = io.TextIOWrapper(io.BytesIO(), encoding='utf-8', newline='\n')
        with patch('sys.stdout', stream):
            code = main([str(argument) for argument in argv])
        stream.flush()
        return code, stream.buffer.getvalue().decode('utf-8')

    def request(self, text='Where is the sum of the first two odd numbers worked out?', name='request.md'):
        path = self.root / name
        path.write_text(text, encoding='utf-8')
        return path

    def searcher(self):
        return self.reader('ssearcher')

    def small_parts(self, limit=420):
        """Parts of at most so many characters. At 420 the test canon is four of them: the two modules directly
        under the library together, the folder Small.Steps, and the two modules of Small.Sums, a folder
        longer than a part, each alone."""
        limited = patch.object(search, 'PART_CHARS', limit)
        limited.start()
        self.addCleanup(limited.stop)

    def unpublished(self):
        """Two pipelines whose work is not in the canon: one with its peer, one with a review of its candidate."""
        engine = Runner(self.instance, self.skill)
        for sid in ('swithpeer', 'swithreview'):
            folder = self.session(engine, sid)
            (folder / 'output' / 'report.md').write_text(
                f'# Report of {sid}\n\n## Part 2\n\nAn inequality cut by distances, worked out by {sid}.\n', encoding='utf-8')
        pipelines = {sid: engine.state['jobs'][engine.state['sessions'][sid]['job']]['pipeline']
                     for sid in ('swithpeer', 'swithreview')}
        engine.state['pipelines'][pipelines['swithpeer']]['stage'] = 'peer'
        candidate = self.root / 'frozen-candidate'
        (candidate / 'records' / 'Small').mkdir(parents=True)
        (candidate / 'records' / 'Small' / 'cutByDistances.md').write_text(
            record_text('The sum is bounded by a count of pairs at each distance.'), encoding='utf-8')
        pid = pipelines['swithreview']
        engine.state['pipelines'][pid]['stage'] = 'review'
        engine.state['jobs'][pid + ':review:speer'] = {
            'id': pid + ':review:speer', 'role': 'review', 'pipeline': pid, 'status': 'running', 'session': None,
            'retries': 0, 'not_before': 0, 'task': {'kind': 'candidate', 'candidate': str(candidate)}}
        engine.save()
        return candidate


def top(module):
    """The top-level folder of a module, as the tests name it; '' for a module directly under the library."""
    return '.'.join(module.split('.')[:2]) if module.count('.') > 1 else ''


class CorpusTests(SearchCase):
    # Further modules, each with so many elements, for a canon of six top-level folders. In the order of their
    # names these are Small.Alpha, Small.Big, Small.Mid, Small.Steps, Small.Sums and Small.Wide.
    WIDER = {'Small.Alpha.One': 1, 'Small.Big.One': 4, 'Small.Big.Three': 4, 'Small.Big.Two': 4,
             'Small.Mid.One': 2, 'Small.Wide.One': 10}
    # A part of so many characters. Of the folders of the wider canon Small.Big is then longer than a part,
    # and Small.Wide is longer than the four fifths to which a part is filled and not longer than a part.
    PART = 1100

    def parts(self, model=None, **request):
        model = model or replay(self.instance)
        corpus, texts = search.build_parts(self.instance, {'folders': [], 'history': False, **request}, model)
        return model, corpus, texts

    def grown(self, model, modules):
        """A copy of the model with further modules in it, as their publication would leave it for the corpus:
        {module: number of elements}. An element is a copy of one of the canon under a name and a description
        of its own."""
        model = copy.deepcopy(model)
        model['modules'] = sorted({*model['modules'], *modules})
        for module, count in modules.items():
            for number in range(1, count + 1):
                name = 'Small.in' + ''.join(module.split('.')[1:]) + str(number)
                model['elements'][name] = {**model['elements']['Small.sumThree'], 'name': name, 'module': module,
                                           'statement_of': name,
                                           'description': f'Statement {number} of the module {module}.'}
        return model

    def assert_whole(self, model, texts, limit):
        """Every element and every module of the model stands once in the texts, and no text exceeds the limit."""
        for name, element in model['elements'].items():
            line = '- ' + canon_index.one_line(head(element)) + '\n'
            self.assertEqual(sum(text.count(line) for text in texts), 1, name)
        self.assertEqual(sum(text.count('\n- ') for text in texts), len(model['elements']))
        for module in model['modules']:
            self.assertEqual(sum(text.count(f'### Module {module}\n') for text in texts), 1, module)
        self.assertTrue(all(len(text) <= limit for text in texts), [len(text) for text in texts])

    def test_the_corpus_holds_every_element_once_and_is_cut_where_a_module_ends(self):
        self.small_parts()
        model, corpus, texts = self.parts()
        self.assertEqual(len(texts), 4)
        self.assert_whole(model, texts, 420)
        self.assertFalse(any('(continued)' in text for text in texts))
        # What parts.json says of the parts is what the texts hold.
        self.assertEqual(corpus['modules'], {module: len(names) for module, names in canon_index.modules_of(model).items()})
        self.assertEqual([list(part['modules']) for part in corpus['parts']],
                         [['Small.Defs', 'Small.Root'], ['Small.Steps.Next'], ['Small.Sums.High'], ['Small.Sums.Low']])
        self.assertEqual([part['kind'] for part in corpus['parts']], ['canon'] * len(texts))
        for part, text in zip(corpus['parts'], texts):
            for module, count in part['modules'].items():
                self.assertIn(f'### Module {module}\n', text)
            self.assertEqual(sum(part['modules'].values()), text.count('\n- '))

    def test_a_part_shows_the_descriptions_above_its_elements(self):
        _, corpus, texts = self.parts()
        self.assertEqual(len(texts), 1)
        text = texts[0]
        self.assertIn('## Folder Small.Sums\n' + FOLDERS['Small.Sums'] + '\n', text)
        self.assertEqual(text.count('## Folder Small.Sums\n'), 1)
        self.assertIn('### Module Small.Sums.Low\n' + LINES['Small.Sums.Low'] + '\n- Small.sumTwo · ', text)
        self.assertIn('### Module Small.Root\n(no line yet)\n- Small.root · ', text)
        # The order of the tree: the modules of one folder stand together.
        places = [text.index(f'### Module {module}\n') for module in
                  ('Small.Defs', 'Small.Root', 'Small.Steps.Next', 'Small.Sums.High', 'Small.Sums.Low')]
        self.assertEqual(places, sorted(places))
        # In small parts the description of a folder stands in each part that holds one of its modules.
        self.small_parts()
        _, _, texts = self.parts()
        holding = [text for text in texts if '### Module Small.Sums.' in text]
        self.assertEqual(len(holding), 2)
        self.assertTrue(all('## Folder Small.Sums\n' in text for text in holding))

    def test_a_part_holds_whole_top_level_folders_and_a_folder_longer_than_a_part_is_cut_alone(self):
        self.small_parts(self.PART)
        model = self.grown(replay(self.instance), self.WIDER)
        _, corpus, texts = self.parts(model)
        self.assertEqual([list(part['modules']) for part in corpus['parts']], [
            # The modules directly under the library stand first, and the next folder fits beside them.
            ['Small.Defs', 'Small.Root', 'Small.Alpha.One'],
            # A folder longer than a part is cut where a module ends, into parts that hold nothing else.
            ['Small.Big.One', 'Small.Big.Three'],
            ['Small.Big.Two'],
            ['Small.Mid.One', 'Small.Steps.Next'],
            ['Small.Sums.High', 'Small.Sums.Low'],
            ['Small.Wide.One']])
        self.assert_whole(model, texts, self.PART)
        # A top-level folder has the same text alone and beside others, so the text of a part is the texts of its
        # folders one after another; and a search narrowed to a folder that stands alone in its part, or that
        # is cut inside, has the very parts that the search of the whole canon has for it.
        direct, = self.parts(model, folders=['Small.Defs', 'Small.Root'])[2]
        alone = {folder: self.parts(model, folders=['Small.' + folder])[2]
                 for folder in ('Alpha', 'Big', 'Mid', 'Steps', 'Sums', 'Wide')}
        self.assertEqual([len(alone[folder]) for folder in ('Alpha', 'Big', 'Mid', 'Steps', 'Sums', 'Wide')], [1, 2, 1, 1, 1, 1])
        self.assertEqual(texts, [direct + alone['Alpha'][0], *alone['Big'], alone['Mid'][0] + alone['Steps'][0],
                                 alone['Sums'][0], alone['Wide'][0]])
        self.assertEqual(self.parts(model, folders=['Small.Mid', 'Small.Steps'])[2], [texts[3]])
        # Whole folders fill a part to four fifths. Small.Sums would fit beside Small.Mid and Small.Steps in a
        # part and stands in the next one; Small.Wide, longer than four fifths by itself, is one part and whole.
        full = search.PART_FILL * self.PART
        self.assertEqual(search.PART_FILL, 0.8)
        self.assertLessEqual(len(texts[3]) + len(texts[4]), self.PART)
        self.assertGreater(len(texts[3]) + len(texts[4]), full)
        self.assertGreater(len(texts[5]), full)
        self.assertGreater(sum(len(text) for text in alone['Big']), self.PART)
        self.assertNotIn('(continued)', ''.join(texts))

    def test_a_new_module_leaves_every_part_that_does_not_hold_its_top_level_folder_the_same(self):
        self.small_parts(self.PART)
        model = self.grown(replay(self.instance), self.WIDER)
        _, corpus, texts = self.parts(model)
        holding = [{top(module) for module in part['modules']} for part in corpus['parts']]
        for new in ('Small.Extra', 'Small.Alpha.Two', 'Small.Big.Above', 'Small.Big.Zed', 'Small.Mid.Two',
                    'Small.Steps.Back', 'Small.Sums.Mid', 'Small.Wide.Two'):
            with self.subTest(new=new):
                after, corpus_after, texts_after = self.parts(self.grown(model, {new: 1}))
                self.assert_whole(after, texts_after, self.PART)
                holding_after = [{top(module) for module in part['modules']} for part in corpus_after['parts']]
                # Byte for byte, and in the same order, the parts without the folder are those there were before.
                self.assertEqual([text for folders, text in zip(holding_after, texts_after) if top(new) not in folders],
                                 [text for folders, text in zip(holding, texts) if top(new) not in folders])
                self.assertEqual(sum(top(new) not in folders for folders in holding), 5 if top(new) != 'Small.Big' else 4)
        # A module early in a folder that is cut inside moves the cut within that folder; a late one does not.
        self.assertEqual(self.parts(self.grown(model, {'Small.Big.Zed': 1}))[2][1], texts[1])
        self.assertNotEqual(self.parts(self.grown(model, {'Small.Big.Above': 1}))[2][1], texts[1])
        # A new top-level folder changes the part it comes to stand in, and no other.
        _, corpus_after, texts_after = self.parts(self.grown(model, {'Small.New.One': 1}))
        self.assertEqual(list(corpus_after['parts'][3]['modules']), ['Small.Mid.One', 'Small.New.One', 'Small.Steps.Next'])
        self.assertEqual(texts_after[:3] + texts_after[4:], texts[:3] + texts[4:])

    def test_a_folder_that_no_longer_fits_beside_its_neighbour_moves_on_and_the_cut_meets_the_earlier_one(self):
        # The cut is made from the canon as it stands. A folder that grows past what its part takes sends the
        # folder after it to the next part: here the text of two parts changes though only one folder did.
        self.small_parts(self.PART)
        model = self.grown(replay(self.instance), self.WIDER)
        _, corpus, texts = self.parts(model)
        after, corpus_after, texts_after = self.parts(self.grown(model, {'Small.Mid.Two': 5}))
        self.assert_whole(after, texts_after, self.PART)
        self.assertEqual([list(part['modules']) for part in corpus_after['parts']], [
            ['Small.Defs', 'Small.Root', 'Small.Alpha.One'], ['Small.Big.One', 'Small.Big.Three'], ['Small.Big.Two'],
            ['Small.Mid.One', 'Small.Mid.Two'],
            ['Small.Steps.Next', 'Small.Sums.High', 'Small.Sums.Low'],
            ['Small.Wide.One']])
        self.assertEqual(texts_after[:3] + texts_after[5:], texts[:3] + texts[5:])
        self.assertNotIn(texts_after[4], texts)
        steps, = self.parts(model, folders=['Small.Steps'])[2]
        self.assertEqual(texts_after[4], steps + texts[4])

    def test_a_unit_longer_than_a_part_is_continued_and_no_line_is_lost(self):
        def unit(tag, count):
            return {'tag': tag, 'intro': lambda shown, continued: (f"[{tag}{' again' if continued else ''}]\n", shown),
                    'outro': f'[/{tag}]\n', 'lines': [f'{tag} line {number:03d}' for number in range(count)]}

        parts = search.pack([unit('a', 3), unit('b', 40), unit('c', 2)], 200)
        text = ''.join(part['text'] for part in parts)
        for tag, count in (('a', 3), ('b', 40), ('c', 2)):
            self.assertEqual([line for line in text.split('\n') if line.startswith(tag + ' line')],
                             [f'{tag} line {number:03d}' for number in range(count)])
        self.assertTrue(all(len(part['text']) <= 200 for part in parts))
        # `b` does not fit beside `a`, so it begins a part of its own, and it alone is cut inside.
        self.assertEqual(parts[0]['held'], [('a', 3)])
        self.assertEqual({tag for part in parts[1:-1] for tag, _ in part['held']}, {'b'})
        self.assertEqual(sum(count for part in parts for tag, count in part['held'] if tag == 'b'), 40)
        self.assertIn('[b again]', parts[2]['text'])
        self.assertEqual(text.count('[b]') + text.count('[b again]'), text.count('[/b]'))

    def test_narrowing_selects_folders_and_modules_and_refuses_an_unknown_name(self):
        _, corpus, texts = self.parts(folders=['Small.Sums', 'Small.Defs'])
        self.assertEqual(sorted(corpus['modules']), ['Small.Defs', 'Small.Sums.High', 'Small.Sums.Low'])
        self.assertNotIn('Small.sumSucc', texts[0])
        self.assertNotIn('Small.root', texts[0])
        with self.assertRaisesRegex(search.CanonError, 'no folder or module of the canon has the name Small.Sum$'):
            self.parts(folders=['Small.Sum'])

    def test_unpublished_work_and_history_are_parts_of_their_own(self):
        candidate = self.unpublished()
        history = self.instance / 'canon' / 'history' / 'Small' / 'sumTwo'
        history.mkdir(parents=True)
        (history / '000002-record.md').write_text('# Small.sumTwo: record replaced\n\n+An earlier wording.\n',
                                                  encoding='utf-8')
        _, corpus, texts = self.parts(history=True)
        # The work of each session is a part of its own, however little it is.
        self.assertEqual([part['kind'] for part in corpus['parts']], ['canon', 'unpublished', 'unpublished', 'history'])
        self.assertEqual([part['sessions'] for part in corpus['parts'][1:3]], [['swithpeer'], ['swithreview']])
        self.assertTrue(texts[1].startswith('\n<unpublished session="swithpeer" role="attempt" stage="peer" source="report">\n'
                                            '# Report of swithpeer\n'))
        self.assertTrue(texts[1].endswith('worked out by swithpeer.\n</unpublished>\n'))
        self.assertTrue(texts[2].startswith('\n<unpublished session="swithreview" role="attempt" stage="review" source="report">\n'))
        self.assertTrue(texts[2].endswith(
            '<unpublished session="swithreview" role="attempt" stage="review" source="candidate records">\n'
            '- Small.cutByDistances — The sum is bounded by a count of pairs at each distance.\n'
            '</unpublished>\n'))
        self.assertNotIn('swithreview', texts[1])
        self.assertNotIn('swithpeer', texts[2])
        self.assertEqual(corpus['unpublished']['swithreview'],
                         {'role': 'attempt', 'stage': 'review', 'candidate': str(candidate),
                          'report': str(self.instance / 'sessions' / 'swithreview' / 'output' / 'report.md')})
        self.assertIsNone(corpus['unpublished']['swithpeer']['candidate'])
        self.assertIn('<history element="Small.sumTwo" file="000002-record.md">\n# Small.sumTwo: record replaced', texts[3])
        self.assertEqual(corpus['parts'][3]['elements'], ['Small.sumTwo'])
        # A session whose work is published or given up leaves; the part of another session stays the same text.
        state = read_json(self.instance / 'runner' / 'state.json')
        pid, = (pid for pid, pipeline in state['pipelines'].items() if pipeline.get('producer') == 'swithpeer')
        state['pipelines'][pid]['stage'] = 'done'
        write_json(self.instance / 'runner' / 'state.json', state)
        _, corpus, left = self.parts()
        self.assertEqual([part.get('sessions') for part in corpus['parts']], [None, ['swithreview']])
        self.assertEqual(left, [texts[0], texts[2]])
        # A search narrowed to folders reads the canon of those folders, and of the history what belongs to them.
        _, corpus, _ = self.parts(folders=['Small.Steps'], history=True)
        self.assertEqual([part['kind'] for part in corpus['parts']], ['canon'])


class LightTests(SearchCase):
    def test_the_command_of_a_light_session_has_no_tools_and_none_of_the_operators_settings(self):
        folder = self.root / 'light'
        folder.mkdir()
        line = light.command('claude', 'claude/sonnet', 'low', folder, folder / 'system.txt')
        argv = line.argv
        self.assertEqual(argv[argv.index('--model') + 1], 'sonnet')  # without the [1m] of a worker
        for option, value in (('--tools', ''), ('--setting-sources', ''), ('--system-prompt-file', str(folder / 'system.txt')),
                              ('--mcp-config', str(folder / 'worker-mcp.json')), ('--effort', 'low')):
            self.assertEqual(argv[argv.index(option) + 1], value, option)
        for option in ('--print', '--strict-mcp-config', '--disable-slash-commands', '--no-session-persistence'):
            self.assertIn(option, argv)
        self.assertEqual(read_json(folder / 'worker-mcp.json'), {'mcpServers': {}})
        self.assertTrue(read_json(folder / 'worker-settings.json')['disableAllHooks'])
        self.assertEqual(line.cwd, folder.resolve())
        with self.assertRaisesRegex(ValueError, 'Claude CLI'):
            light.command('codex', 'codex/gpt', 'low', folder, folder / 'system.txt')

    def run_light(self, name='one'):
        folder = self.root / name
        (self.root / 'system.txt').write_text('Instructions and a text.', encoding='utf-8')
        return folder, light.run(folder, self.root / 'system.txt', 'The request.', executable=read_json(
            self.instance / 'settings.json')['cli']['claude'], model='claude/sonnet', effort='low',
            slots=self.root / 'slots', parallel=2, retry_seconds=5)

    def test_a_light_session_returns_the_answer_and_the_use_the_cli_reported(self):
        self.script([{'answer': '{"ok": true}'}])
        folder, outcome = self.run_light()
        self.assertEqual(outcome, {'text': '{"ok": true}', 'refused': None, 'error': None, 'exit_code': 0,
                                   'usage': {'tokens': {'inputTokens': 3, 'outputTokens': 40, 'cacheReadInputTokens': 1000,
                                                        'cacheCreationInputTokens': 200},
                                             'cost_usd': 0.0125, 'seconds': 1.2}})
        call, = self.calls()
        # What the CLI was given: the options through the command file, the system prompt, the request on its
        # standard input, the session's own folder as its working folder, and the smaller cap on what it writes.
        self.assertEqual(call['argv'][call['argv'].index('--tools') + 1], '')
        self.assertEqual((call['system'], call['request']), ('Instructions and a text.', 'The request.'))
        self.assertEqual(Path(call['cwd']), folder.resolve())
        self.assertEqual(call['output_tokens'], str(light.OUTPUT_TOKENS))
        self.assertTrue((folder / 'cli.stdout.jsonl').is_file() and (folder / 'request.txt').is_file())

    def test_a_refusal_an_error_and_a_cli_that_died_are_told_apart(self):
        for name, rule, expected in (
                ('limit', {'refuse': 'usage_limit'}, ('refused', 'usage_limit')),
                ('credits', {'refuse': 'model_requires_usage_credits'}, ('refused', 'model_requires_usage_credits')),
                ('safeguard', {'refuse': 'model_refusal'}, ('refused', 'model_refusal')),
                ('died', {'exit': 3}, ('error', 'exit code 3')),
                ('failed', {'error': 'Prompt is too long'}, ('error', 'Prompt is too long'))):
            self.script([rule])
            folder, outcome = self.run_light(name)
            kind, said = expected
            self.assertIsNone(outcome['text'], name)
            if kind == 'refused':
                self.assertEqual(outcome['refused']['reason'], said, name)
                self.assertGreater(outcome['refused']['until'], time.time(), name)
                self.assertIsNone(outcome['error'], name)
            else:
                self.assertIsNone(outcome['refused'], name)
                self.assertIn(said, outcome['error'], name)
        # A CLI that cannot be started is an error as well, and it held no slot when it failed.
        (self.root / 'system.txt').write_text('x', encoding='utf-8')
        outcome = light.run(self.root / 'missing', self.root / 'system.txt', 'r', executable=str(self.root / 'no-such-cli'),
                            model='claude/sonnet', effort='low', slots=self.root / 'slots', parallel=1)
        self.assertIn('could not be started', outcome['error'])
        with light.slot(self.root / 'slots', 1):
            pass

    def test_a_slot_is_held_by_one_holder_at_a_time(self):
        slots, order = self.root / 'slots', []

        def second():
            with light.slot(slots, 1):
                order.append('second')

        with light.slot(slots, 1) as first:
            thread = threading.Thread(target=second)
            thread.start()
            time.sleep(3 * light.SLOT_POLL_SECONDS)
            order.append('first releases')
        thread.join(timeout=30)
        self.assertEqual((first, order), (0, ['first releases', 'second']))
        with light.slot(slots, 2) as one, light.slot(slots, 2) as two:
            self.assertEqual({one, two}, {0, 1})


class SearchTests(SearchCase):
    def test_a_search_returns_hits_filled_in_from_the_canon_and_drops_a_name_the_canon_does_not_have(self):
        self.script([{'answer': answer(hits=[
            {'name': '`Small.oddSum`', 'match': 'related', 'why': 'The definition of the sum.'},
            {'name': 'Small.invented', 'match': 'direct', 'why': 'It would be exactly what is asked.'},
            {'name': 'Small.sumTwo', 'match': 'direct', 'why': 'It states the value of the sum for two terms.'},
            {'name': 'Small.sumTwo', 'match': 'related', 'why': 'Named twice.'}])}])
        code, text = self.command(self.searcher(), '--file', self.request())
        self.assertEqual(code, 0, text)
        model = replay(self.instance)
        self.assertEqual(text, f'''Search of the canon · revision {model['sequence']} · read by claude/sonnet at low effort · {text.splitlines()[0][-16:]}

Hits in the canon (2): 1 direct, 1 related

Direct: these state or decide what the request asks for, in this or another formulation, more generally, as a special case, or by showing that it fails.

- {head(model['elements']['Small.sumTwo'])}
  filed in Small.Sums.Low
  why: It states the value of the sum for two terms.

Related: definitions, lemmas, steps and neighbouring statements that the request would use or that do part of its work.

- {head(model['elements']['Small.oddSum'])}
  filed in Small.Defs
  why: The definition of the sum.

Hits in unpublished work (0), not reviewed

Read:
- 6 of 6 elements in 5 of 5 modules: the whole canon
- the unpublished work of 0 sessions
Not read:
- the replaced texts in the canon's history: not asked for; --history adds them

A search can miss: that it found nothing is no evidence that the canon holds nothing on the matter. The descent returns the whole of a scope: `index`, then `index <folder>` and `index <module>`.
''')
        self.assertIn('The first two odd numbers sum to four.', text)  # the self-description, from the record
        self.assertNotIn('Small.invented', text)
        self.assertNotIn('Named twice', text)  # the first time an element is named is the one that counts
        call, = self.calls()
        self.assertIn('BEGIN REQUEST\nWhere is the sum of the first two odd numbers worked out?\nEND REQUEST', call['request'])
        self.assertTrue(call['system'].startswith(search.READER))
        self.assertIn('\nBEGIN PART\n', call['system'])
        # The files of the search, under the instance's runner folder.
        folder, = (path for path in self.home.iterdir() if path.is_dir())
        self.assertTrue(folder.name.startswith('s-'))
        self.assertEqual((folder / 'answer.txt').read_text(encoding='utf-8'), text)
        self.assertEqual(read_json(folder / 'request.json')['caller'], 'ssearcher')
        self.assertEqual(read_json(folder / 'parts.json')['parts'], [{'kind': 'canon', 'modules': {
            'Small.Defs': 1, 'Small.Root': 1, 'Small.Steps.Next': 1, 'Small.Sums.High': 1, 'Small.Sums.Low': 2}}])
        # The part was read, so its text is kept no longer; what the light session wrote is.
        self.assertFalse((folder / 'parts' / '01' / 'system.txt').exists())
        self.assertTrue(read_json(folder / 'parts' / '01' / 'outcome.json')['ok'])
        self.assertTrue((folder / 'parts' / '01' / 'run-1' / 'cli.stdout.jsonl').is_file())
        result = read_json(folder / 'result.json')
        self.assertTrue(result['complete'])
        self.assertEqual([(hit['name'], hit['match']) for hit in result['hits']['canon']],
                         [('Small.sumTwo', 'direct'), ('Small.oddSum', 'related')])

    def test_a_direct_hit_of_a_later_part_stands_before_a_related_hit_of_an_earlier_one(self):
        self.small_parts()
        # Four parts: the modules directly under the library, Small.Steps, Small.Sums.High and Small.Sums.Low.
        # A hit without the key, or with a value that is neither of the two, counts as related.
        self.script([{'system': '### Module Small.Defs', 'answer': answer(hits=[
                         {'name': 'Small.oddSum', 'why': 'The definition of the sum.'},
                         {'name': 'Small.root', 'match': 'related', 'why': 'The root.'}])},
                     {'system': '### Module Small.Steps.Next', 'answer': answer(hits=[
                         {'name': 'Small.sumSucc', 'match': 'Direct', 'why': 'The step gives every value.'}])},
                     {'system': '### Module Small.Sums.High', 'answer': answer(hits=[
                         {'name': 'Small.sumThree', 'match': 'nearly', 'why': 'Nine.'}])},
                     {'system': '### Module Small.Sums.Low', 'answer': answer(hits=[
                         {'name': 'Small.sumZero', 'match': 7, 'why': 'Zero.'},
                         {'name': 'Small.sumTwo', 'match': 'direct', 'why': 'Four.'}])}])
        code, text = self.command(self.searcher(), '--file', self.request())
        self.assertEqual(code, 0, text)
        direct, related = (line for _, line in search.GROUPS)
        canon = text.split('Hits in the canon ')[1].split('Hits in unpublished work')[0]
        self.assertEqual(canon.split('\n\n')[0], '(6): 2 direct, 4 related')
        self.assertEqual([line for line in canon.splitlines() if line.startswith(('Direct', 'Related', '- '))],
                         [direct, '- ' + head(replay(self.instance)['elements']['Small.sumSucc']),
                          '- ' + head(replay(self.instance)['elements']['Small.sumTwo']), related]
                         + ['- ' + head(replay(self.instance)['elements'][name])
                            for name in ('Small.oddSum', 'Small.root', 'Small.sumThree', 'Small.sumZero')])
        # With related hits only, the heading says so and the group of direct hits is not printed.
        self.script([{'system': '### Module Small.Sums.Low', 'answer': answer(hits=[{'name': 'Small.sumTwo', 'why': 'Four.'}])}])
        code, text = self.command(self.searcher(), '--file', self.request('Another request.', 'other.md'))
        self.assertEqual(code, 0, text)
        self.assertIn(f'Hits in the canon (1): 0 direct, 1 related\n\n{related}\n\n- Small.sumTwo · ', text)
        self.assertNotIn(direct, text)
        self.assertIn('Hits in unpublished work (0), not reviewed\n\nRead:', text)

    def test_a_hit_counts_only_where_the_element_stood_in_the_part_that_named_it(self):
        self.small_parts()
        # The part of the modules directly under the library names an element of another part, as a light
        # session can that knows the name from the request. The element's own part calls it direct.
        elsewhere = {'name': 'Small.sumTwo', 'match': 'related', 'why': 'Named from the request, not from this part.'}
        self.script([{'system': '### Module Small.Defs', 'answer': answer(hits=[
                         elsewhere, {'name': 'Small.oddSum', 'match': 'related', 'why': 'The definition of the sum.'}])},
                     {'system': '### Module Small.Sums.Low', 'answer': answer(hits=[
                         {'name': 'Small.sumTwo', 'match': 'direct', 'why': 'Four.'}])}])
        code, text = self.command(self.searcher(), '--file', self.request())
        self.assertEqual(code, 0, text)
        self.assertIn('Hits in the canon (2): 1 direct, 1 related', text)
        self.assertIn('  why: Four.\n', text)
        self.assertNotIn('Named from the request', text)
        # Where the element's own part was not read, the name is no hit at all.
        self.script([{'system': '### Module Small.Defs', 'answer': answer(hits=[elsewhere])},
                     {'system': '### Module Small.Sums.Low', 'exit': 3}])
        code, text = self.command(self.searcher(), '--file', self.request('Another request.', 'other.md'))
        self.assertEqual(code, 0, text)
        self.assertIn('Hits in the canon (0)', text)
        self.assertIn('Not read:\n- Small.Sums (1 of its 2 modules: Small.Sums.Low)', text)
        self.assertNotIn('Small.sumTwo', text)
        # A search narrowed to a folder prints no element that is filed outside it.
        self.script([{'answer': answer(hits=[elsewhere, {'name': 'Small.sumSucc', 'why': 'The step.'}])}])
        code, text = self.command(self.searcher(), '--file', self.request(), '--folder', 'Small.Steps')
        self.assertEqual(code, 0, text)
        self.assertIn('Hits in the canon (1): 0 direct, 1 related', text)
        self.assertNotIn('Small.sumTwo', text)

    def test_the_last_object_of_an_answer_that_corrects_itself_is_the_answer(self):
        self.script([{'answer': answer(hits=[{'name': 'Small.sumZero', 'match': 'direct', 'why': 'Zero.'}])
                      + '\n\nOn reflection that element is about no terms. Corrected:\n\n```json\n'
                      + answer(hits=[{'name': 'Small.sumTwo', 'match': 'direct', 'why': 'Four.'}]) + '\n```\nThat is all.'}])
        code, text = self.command(self.searcher(), '--file', self.request())
        self.assertEqual((code, len(self.calls())), (0, 1), text)
        self.assertIn('Hits in the canon (1): 1 direct, 0 related', text)
        self.assertIn('- Small.sumTwo · ', text)
        self.assertNotIn('Small.sumZero', text)
        # An object of another form after the answer does not hide it, and a text without the form is no answer.
        parse = search.hits_of('canon')
        self.assertEqual([hit['name'] for hit in parse('{"hits": [{"name": "A"}]} and a note: {"checked": true}')], ['A'])
        self.assertIsNone(parse('{"note": "nothing in the form"} {broken'))
        self.assertEqual(search.opened_of(2)('{"answers": [{"purpose": 1, "open": ["A"]}]} I left one out. '
                                            '{"answers": [{"purpose": 1, "open": ["A"]}, {"purpose": 2, "open": []}]}'),
                         {'1': ['A'], '2': []})

    def test_work_that_its_review_accepted_and_that_waits_to_be_published_is_printed_as_such(self):
        candidate = self.unpublished()
        # The review of swithreview has ended with the decision to publish: its session waits for the publication.
        engine = Runner(self.instance, self.skill)
        job = next(job for job in engine.state['jobs'].values() if job['role'] == 'review' and job['status'] == 'running')
        job['session'] = 'sreviewer'
        engine.state['sessions']['sreviewer'] = {'id': 'sreviewer', 'role': 'review', 'job': job['id'], 'status': 'publishing'}
        engine.save()
        self.script([{'system': '<unpublished session="swithreview"', 'answer': answer(unpublished=[
                         {'session': 'swithreview', 'match': 'direct', 'where': 'Part 2 of the report', 'why': 'It bounds the sum.'}])},
                     {'system': '<unpublished session="swithpeer"', 'answer': answer(unpublished=[
                         {'session': 'swithpeer', 'where': 'Part 2', 'why': 'The same inequality, earlier.'}])}])
        code, text = self.command(self.searcher(), '--file', self.request('An inequality cut by distances.'))
        self.assertEqual(code, 0, text)
        sessions = self.instance / 'sessions'
        self.assertIn(f'''Hits in unpublished work (1), not reviewed: 0 direct, 1 related

This work is not in the canon and no review has judged it. A hit says that the work exists; check it yourself before you rest anything on it.

{RELATED}

- session swithpeer · attempt · with a peer · not reviewed
  report {sessions / 'swithpeer' / 'output' / 'report.md'}
  where: Part 2
  why: The same inequality, earlier.

Hits in work accepted by its review and waiting to be published (1): 1 direct, 0 related

This work is not in the canon yet. Its review has accepted it, and it waits for its turn to be published; it enters the canon when its publication has built it on the canon as the canon stands then.

{search.GROUPS[0][1]}

- session swithreview · attempt · accepted by its review · waiting to be published
  report {sessions / 'swithreview' / 'output' / 'report.md'} · candidate {candidate}
  where: Part 2 of the report
  why: It bounds the sum.

Read:
- 6 of 6 elements in 5 of 5 modules: the whole canon
- the unpublished work of 2 sessions: swithpeer and swithreview
''', text)
        # The light session is told the stage, and what it is told of the work says what that stage means.
        given = next(call['system'] for call in self.calls() if '<unpublished session="swithreview"' in call['system'])
        self.assertIn('<unpublished session="swithreview" role="attempt" stage="accepted" source="report">', given)
        self.assertIn('No review has judged it, except a piece whose `stage` is "accepted": its review has accepted '
                      'that work, and it waits to be published.', given)
        # Without a hit in such work its section is not printed, and with no other hit the sentence that no
        # review has judged the work is not printed either.
        self.script([{'system': '<unpublished session="swithreview"', 'answer': answer(unpublished=[
            {'session': 'swithreview', 'where': 'Part 2', 'why': 'It bounds the sum.'}])}])
        code, text = self.command(self.searcher(), '--file', self.request('Another request.', 'other.md'))
        self.assertIn('Hits in unpublished work (0), not reviewed\n\nHits in work accepted by its review and waiting '
                      'to be published (1): 0 direct, 1 related\n', text)
        self.assertNotIn(search.NOT_JUDGED, text)
        self.script([])
        code, text = self.command(self.searcher(), '--file', self.request('A third request.', 'third.md'))
        self.assertIn('Hits in unpublished work (0), not reviewed\n\nRead:', text)
        self.assertNotIn('accepted by its review', text)

    def test_a_search_given_while_a_publication_is_put_in_place_reads_the_canon_as_that_publication_leaves_it(self):
        arguments = (self.searcher(), '--file', self.request())
        real, asked = search.replay, []

        def behind(instance, index=None):
            """The research as a replay gives it while the index of the latest publication is not in place."""
            asked.append(instance)
            model = real(instance, index)
            return {**model, 'sequence': model['sequence'] - 1} if len(asked) <= self.calls_behind else model

        waits = patch.multiple(search, INDEX_WAIT_SECONDS=0.3, INDEX_POLL_SECONDS=0.05)
        # The index does not come within the time the search waits: nothing is read, nothing is kept as the
        # answer, and the command says to give it again.
        self.calls_behind = 10 ** 6
        with waits, patch.object(search, 'replay', side_effect=behind):
            code, text = self.command(*arguments)
        self.assertEqual(code, 1, text)
        self.assertRegex(json.loads(text)['error'], r'^the search ended with an error: CanonError: the canon is being '
                                                     r'published to: publication 1 is recorded and its index was not in '
                                                     r'place after 0\.3 seconds, so the canon read as revision 0\. .* Run '
                                                     r'the same command again$')
        self.assertEqual(self.calls(), [])
        folder, = (path for path in self.home.iterdir() if path.is_dir())
        self.assertFalse((folder / 'parts.json').exists())
        # The index comes while the search waits: the search reads the canon of the publication its key counts.
        asked.clear()
        self.calls_behind = 2
        with waits, patch.object(search, 'replay', side_effect=behind):
            code, text = self.command(*arguments)
        self.assertEqual((code, len(asked), len(self.calls())), (0, 3, 1), text)
        self.assertTrue(text.startswith('Search of the canon · revision 1 · '), text)
        self.assertEqual(read_json(folder / 'parts.json')['revision'], 1)

    def test_a_search_given_after_a_change_is_in_the_canon_and_before_its_publication_ends_reads_it_with_the_canon(self):
        import runner as runner_module
        folder = self.candidate(modules={'Small/Sums/Five.lean': module_text(theorem('sumFive', ': oddSum 5 = 25'))},
                                records={'Small/sumFive.md': record_text('The first five odd numbers sum to twenty-five.')})
        self.script([{'system': '### Module Small.Sums.Five', 'answer': answer(hits=[
            {'name': 'Small.sumFive', 'match': 'direct', 'why': 'It is the sum asked for.'}])}])
        arguments = (self.searcher(), '--file', self.request('What do the first five odd numbers add up to?'))
        real, given = runner_module.render, []

        def rendering(*args, **kwargs):
            """The runner renders the views after it has put the change into the canon and marked the publication
            as installed, and before the save that ends the publication. A session gives its command then."""
            state = read_json(self.instance / 'runner' / 'state.json')
            review = state['sessions'][state['publication']['session']]
            given.append((state['publication'].get('installed'), review['status'],
                          [pipeline['stage'] for pipeline in state['pipelines'].values()], self.command(*arguments)))
            return real(*args, **kwargs)

        with patch('runner.render', side_effect=rendering):
            self.publish(folder)
        (installed, status, stages, (code, text)), = given
        # The pipeline is still at its review and the review session still waits for the publication.
        self.assertEqual((installed, status, stages[-1], code), (True, 'publishing', 'review', 0), text)
        # The elements of the change are hits in the canon, and its work is no unpublished work: no light
        # session was given it, and no section says that it waits to be published.
        self.assertIn('Hits in the canon (1): 1 direct, 0 related\n', text)
        self.assertIn('- Small.sumFive · theorem · ', text)
        self.assertIn('Hits in unpublished work (0), not reviewed\n\nRead:\n'
                      '- 7 of 7 elements in 6 of 6 modules: the whole canon\n'
                      '- the unpublished work of 0 sessions\n', text)
        self.assertNotIn('waiting to be published', text)
        self.assertFalse(any('<unpublished session=' in call['system'] for call in self.calls()))
        # The answer is final: the same command after the publication has ended is given the same text.
        self.assertEqual(self.command(*arguments), (0, text))

    def test_a_search_of_the_history_given_while_a_publication_sets_approaches_aside_waits_for_its_end(self):
        import runner as runner_module
        # The proof of Small.sumTwo is accepted, and a later change brings an approach that was tried on it. The
        # publication of that change moves the approach into the history after it is marked as installed.
        proved = self.candidate(
            replace={'Small.sumTwo': theorem('sumTwo', ': oddSum 2 = 4', proof='-- one and three\n  sorry')},
            records={'Small/sumTwo.md': record_text('The first two odd numbers sum to four.', weight='unit',
                                                    proof='The first two odd numbers are $1$ and $3$, and $1 + 3 = 4$.')})
        self.publish(proved)
        self.assertEqual(replay(self.instance)['elements']['Small.sumTwo']['standing'], 'accepted')
        tried = self.candidate(approaches={'Small/sumTwo/pairing.md': (
            '---\ntitle: Pairing the odd numbers\nsessions: searly\n---\n## Idea\n\n'
            'Pair the first odd number with the last.\n\n## Where it stops\n\nThe pairing is not carried out.\n')})
        self.script([{'system': '<history element="Small.sumTwo"', 'answer': answer(hits=[
            {'name': 'Small.sumTwo', 'match': 'direct', 'why': 'A pairing of the odd numbers was tried on it.'}])}])
        plain = (self.searcher(), '--file', self.request('Was a pairing of the odd numbers tried?'))
        history = (*plain, '--history')
        real, given = runner_module.retire_approaches, []

        def setting_aside(canon, name, revision):
            """The runner has marked the publication as installed and is about to move the approach from
            canon/approaches into the history. A session gives its commands then: the search of the history,
            which waits a short time here, and the same search without the history."""
            if name == 'Small.sumTwo' and not given:
                state = read_json(self.instance / 'runner' / 'state.json')
                still = (canon.approaches / 'Small' / 'sumTwo' / 'pairing.md').is_file()
                # The process that does the work prints what ended it; here that process is the test's own.
                with patch.multiple(search, INDEX_WAIT_SECONDS=0.3, INDEX_POLL_SECONDS=0.05), patch('traceback.print_exc'):
                    waited = self.command(*history)
                given.append((state['publication'].get('installed'), still, waited, len(self.calls()),
                              self.command(*plain)))
            return real(canon, name, revision)

        with patch('runner.retire_approaches', side_effect=setting_aside):
            self.publish(tried)
        (installed, still, (code, text), calls, (plain_code, plain_text)), = given
        # The search of the history read nothing and kept nothing: the history was not yet the one this
        # publication leaves.
        self.assertEqual((installed, still, code, calls), (True, True, 1, 0), text)
        self.assertEqual(json.loads(text)['error'], (
            'the search ended with an error: CanonError: the canon is being published to: after 0.3 seconds a '
            'publication was still being put in place. A search reads the canon as its latest publication leaves it. '
            'Run the same command again'))
        folder, = (path for path in self.home.iterdir() if path.is_dir() and not (path / 'parts.json').exists())
        # The search that does not read the history was answered at that moment, as it was before.
        self.assertEqual(plain_code, 0, plain_text)
        self.assertTrue(plain_text.startswith('Search of the canon · revision 3 · '), plain_text)
        self.assertIn("- the replaced texts in the canon's history: not asked for; --history adds them\n", plain_text)
        # The same command after the publication has ended reads the history with the approach in it.
        self.assertIsNone(read_json(self.instance / 'runner' / 'state.json')['publication'])
        code, text = self.command(*history)
        self.assertEqual(code, 0, text)
        self.assertTrue((folder / 'parts.json').is_file())
        self.assertTrue(text.startswith('Search of the canon · revision 3 · '), text)
        self.assertIn(f'Hits in replaced texts of the history (1): 1 direct, 0 related\n\n{search.GROUPS[0][1]}\n\n'
                      '- Small.sumTwo · ', text)
        self.assertIn('  the replaced texts: view Small.sumTwo --part history\n'
                      '  why: A pairing of the odd numbers was tried on it.\n', text)
        read = next(call['system'] for call in self.calls() if '<history element="Small.sumTwo"' in call['system'])
        self.assertIn('<history element="Small.sumTwo" file="000003-approaches/pairing.md">\n', read)
        self.assertIn('Pair the first odd number with the last.', read)

    def test_a_search_given_while_a_publication_without_lean_is_put_in_place_waits_for_it(self):
        from runner import main as runner_main
        source = self.root / 'described'
        path = canon_index.description_file(source, 'folder', 'Small.Sums')
        path.parent.mkdir(parents=True)
        path.write_text('The small cases, described anew at this publication.\n', encoding='utf-8')
        with patch('builtins.print'):
            self.assertEqual(runner_main(['describe', str(self.instance), '--folder', str(source), '--reason', 'R.']), 0)
        arguments = (self.searcher(), '--file', self.request())
        real, during = Runner.write_descriptions, []

        def writing(engine, summary):
            """The event of the publication is written and the texts are in the canon; their summary, from which
            every reader takes them, is not. A session gives its command then, and waits a short time."""
            self.assertEqual(len(list((self.instance / 'knowledge' / 'events').glob('*.json'))), 2)
            # The process that does the work prints what ended it; here that process is the test's own.
            with patch.multiple(search, INDEX_WAIT_SECONDS=0.3, INDEX_POLL_SECONDS=0.05), patch('traceback.print_exc'):
                during.append(self.command(*arguments))
            return real(engine, summary)

        with patch.object(Runner, 'write_descriptions', autospec=True, side_effect=writing):
            Runner(self.instance, self.skill).ingest_inputs()
        (code, text), = during
        # Nothing was read and nothing kept: the canon was neither the one before the publication nor the one after.
        self.assertEqual((code, json.loads(text)['error']), (1, (
            'the search ended with an error: CanonError: the canon is being published to: after 0.3 seconds a '
            'publication was still being put in place. A search reads the canon as its latest publication leaves it. '
            'Run the same command again')))
        self.assertEqual(self.calls(), [])
        folder, = (path for path in self.home.iterdir() if path.is_dir())
        self.assertFalse((folder / 'parts.json').exists())
        # The same command after the publication reads the canon as the publication left it.
        self.assertIsNone(read_json(self.instance / 'runner' / 'state.json')['publication'])
        code, text = self.command(*arguments)
        self.assertEqual(code, 0, text)
        self.assertTrue(text.startswith('Search of the canon · revision 2 · '), text)
        self.assertIn('## Folder Small.Sums\nThe small cases, described anew at this publication.\n', self.calls()[-1]['system'])

    def test_a_candidate_that_is_still_being_built_keeps_no_search_waiting(self):
        # A publication whose event is not written yet has changed nothing of the canon.
        engine = Runner(self.instance, self.skill)
        engine.state['publication'] = {'event': {'id': 'cbuilding', 'kind': 'change', 'sequence': 2}, 'job': None,
                                       'session': None, 'stage': 'build'}
        engine.save()
        with patch.multiple(search, INDEX_WAIT_SECONDS=0.3, INDEX_POLL_SECONDS=0.05):
            code, text = self.command(self.searcher(), '--file', self.request())
        self.assertEqual(code, 0, text)
        self.assertTrue(text.startswith('Search of the canon · revision 1 · '), text)

    def test_each_kind_of_part_asks_for_the_kind_of_every_hit(self):
        for kind in ('canon', 'unpublished', 'history'):
            with self.subTest(kind=kind):
                asked = search.ASKED[kind]
                self.assertIn(search.MATCHES, asked)
                form, = (line for line in asked.splitlines() if line.startswith('{"'))
                self.assertIn('"match": "<direct or related>"', form)
                # The form is JSON once its placeholders are filled in.
                json.loads(form.replace('<direct or related>', 'direct'))
        for said in ('Say of every match which of two kinds it is:', '\n- "direct": it states or decides what the request asks for.',
                     '\n- "related": it does part of the work the request describes, or the request would use it',
                     'The kind is a judgment of the mathematics', 'When you are unsure whether something matches, include it',
                     'Something you include because you are unsure whether it matches is related unless you judge it direct.'):
            self.assertIn(said, search.MATCHES)
        # What a light session is given holds it.
        self.command(self.searcher(), '--file', self.request())
        call, = self.calls()
        self.assertIn(search.ASKED['canon'], call['system'])

    def ledger(self):
        return [json.loads(row) for row in (self.home / 'ledger.jsonl').read_text(encoding='utf-8').splitlines()]

    def test_the_ledger_has_a_line_for_each_light_session_and_one_for_the_run_and_none_for_an_answer_given_again(self):
        self.small_parts()
        arguments = (self.searcher(), '--file', self.request())
        self.assertEqual(self.command(*arguments)[0], 0)
        lines = self.ledger()
        folder, = (path for path in self.home.iterdir() if path.is_dir())
        said = {'kind': 'search', 'key': folder.name, 'session': 'ssearcher', 'model': 'claude/sonnet', 'effort': 'low'}
        for line in lines:
            self.assertLess(abs(line.pop('at') - time.time()), 60)
        # Each of the four light sessions has its line, with what it used.
        self.assertEqual(lines[:4], [{**said, 'light_sessions': 1, 'cost_usd': 0.0125, 'seconds': 1.2, 'tokens': {
            'inputTokens': 3, 'outputTokens': 40, 'cacheReadInputTokens': 1000, 'cacheCreationInputTokens': 200}}] * 4)
        # The run that ended the search has one more, which says what was read and adds no use.
        self.assertEqual(lines[4:], [{
            **said, 'light_sessions': 0, 'tokens': {}, 'cost_usd': 0, 'seconds': 0,
            'read': {'revision': replay(self.instance)['sequence'], 'folders': None, 'elements': 6, 'modules': 5,
                     'unpublished_sessions': 0, 'history_elements': 0, 'parts': 4, 'parts_not_read': 0}}])
        # The same command again is given the same answer; nothing is read, so nothing is added.
        first = self.command(*arguments)
        self.assertEqual((first[0], len(self.calls())), (0, 4))
        self.assertEqual(len(self.ledger()), 5)
        # Added up, the lines are one search of four light sessions.
        usage = search_usage(self.instance)
        self.assertEqual((round(usage.pop('cost_usd'), 6), round(usage.pop('seconds'), 6)), (0.05, 4.8))
        self.assertEqual(usage, {
            'searches': 1, 'descent_tests': 0, 'light_sessions': 4, 'without_cost': 0,
            'tokens': {'inputTokens': 12, 'outputTokens': 160, 'cacheReadInputTokens': 4000, 'cacheCreationInputTokens': 800}})

    def test_the_light_sessions_of_a_process_that_was_ended_are_in_the_ledger_and_the_next_run_adds_only_its_own(self):
        self.small_parts()
        self.configure(search={'model': 'claude/sonnet', 'effort': 'low', 'parallel': 1})
        arguments = (self.searcher(), '--file', self.request())
        real, runs = light.run, []

        def ended(*args, **kwargs):
            """The first two light sessions run; the process is ended while it starts the third."""
            runs.append(args)
            if len(runs) > 2:
                raise KeyboardInterrupt('the process that does the work is ended')
            return real(*args, **kwargs)

        with patch.object(light, 'run', side_effect=ended), self.assertRaises(KeyboardInterrupt):
            self.command(*arguments)
        folder, = (path for path in self.home.iterdir() if path.is_dir())
        self.assertFalse((folder / 'result.json').exists())
        self.assertEqual(len(list(folder.glob('parts/*/outcome.json'))), 2)
        # The two light sessions that ended are counted, though the work has no result and no closing line.
        self.assertEqual([(line['light_sessions'], 'read' in line) for line in self.ledger()], [(1, False)] * 2)
        # The same command again: the two parts that were not read are read, and only they are added.
        code, text = self.command(*arguments)
        self.assertEqual((code, len(self.calls())), (0, 4), text)
        self.assertIn('Read:\n- 6 of 6 elements in 5 of 5 modules: the whole canon\n', text)
        lines = self.ledger()
        self.assertEqual([(line['light_sessions'], 'read' in line) for line in lines], [(1, False)] * 4 + [(0, True)])
        self.assertEqual({line['key'] for line in lines}, {folder.name})
        usage = search_usage(self.instance)
        self.assertEqual((usage['searches'], usage['light_sessions'], round(usage['cost_usd'], 6)), (1, 4, 0.05))

    def test_a_ledger_line_cut_inside_a_character_is_left_out_and_the_lines_appended_after_it_are_counted(self):
        self.assertEqual(self.command(self.searcher(), '--file', self.request())[0], 0)
        ledger = self.home / 'ledger.jsonl'
        whole = ledger.read_bytes()
        self.assertEqual(len(whole.splitlines()), 2)  # one light session, and the run that ended the search
        # The machine goes down inside the write of a line: the line ends inside a character of two bytes and
        # has no line end. Read as text, the file is no UTF-8.
        cut = '{"at": 3.0, "kind": "search", "key": "s-é'.encode('utf-8')[:-1]
        ledger.write_bytes(whole + cut)
        with self.assertRaises(UnicodeDecodeError):
            ledger.read_text(encoding='utf-8')
        usage = search_usage(self.instance)
        self.assertEqual((usage['searches'], usage['light_sessions']), (1, 1))
        # The next search appends its lines. The first of them begins a line of its own and is counted: it
        # is the line of the light session, and the line that closes the run carries no use.
        self.assertEqual(self.command(self.searcher(), '--file', self.request('Another request.', 'other.md'))[0], 0)
        self.assertTrue(ledger.read_bytes().startswith(whole + cut + b'\n{"at": '))
        usage = search_usage(self.instance)
        self.assertEqual((usage['searches'], usage['light_sessions'], round(usage['cost_usd'], 6)), (2, 2, 0.025))

    def test_a_search_narrowed_to_a_folder_reads_that_folder_and_says_what_it_left_out(self):
        self.unpublished()
        code, text = self.command(self.searcher(), '--file', self.request(), '--folder', 'Small.Sums')
        self.assertEqual(code, 0, text)
        call, = self.calls()
        self.assertIn('- Small.sumZero · ', call['system'])
        self.assertNotIn('Small.sumSucc', call['system'])
        self.assertNotIn('unpublished', text.split('Read:')[0])
        self.assertIn('Read:\n- 3 of 3 elements in 2 of 2 modules: the scope named with --folder, Small.Sums\nNot read:\n'
                      '- the canon outside that scope, and the unpublished work: the search was narrowed with --folder\n'
                      "- the replaced texts in the canon's history: not asked for; --history adds them\n", text)
        code, text = self.command(self.searcher(), '--file', self.request(), '--folder', 'Small.Nowhere')
        self.assertEqual((code, json.loads(text)), (1, {'error': 'no folder or module of the canon has the name Small.Nowhere'}))

    def test_an_unpublished_hit_names_its_session_and_says_that_no_review_judged_it(self):
        candidate = self.unpublished()
        # The work of each session is a part of its own. The reader of one names a session that was not given
        # and the session of the other part; only the session whose work it read counts.
        self.script([{'system': '<unpublished session="swithreview"', 'answer': answer(unpublished=[
            {'session': 'swithreview', 'match': 'direct', 'where': 'Part 2 of the report', 'why': 'It bounds the sum by distances.'},
            {'session': 'sinvented', 'match': 'direct', 'where': 'somewhere', 'why': 'No such session was given.'},
            {'session': 'swithpeer', 'where': 'Part 9', 'why': 'Its work stood in another part.'}])},
                     {'system': '<unpublished session="swithpeer"', 'answer': answer(unpublished=[
                         {'session': 'swithpeer', 'where': 'Part 2', 'why': 'The same inequality, earlier.'}])}])
        code, text = self.command(self.searcher(), '--file', self.request('An inequality cut by distances.'))
        self.assertEqual(code, 0, text)
        sessions = self.instance / 'sessions'
        # The work of swithpeer is the earlier part; its hit has no kind, so it is related and stands second.
        self.assertIn(f'''Hits in unpublished work (2), not reviewed: 1 direct, 1 related

This work is not in the canon and no review has judged it. A hit says that the work exists; check it yourself before you rest anything on it.

Direct: these state or decide what the request asks for, in this or another formulation, more generally, as a special case, or by showing that it fails.

- session swithreview · attempt · with a review · not reviewed
  report {sessions / 'swithreview' / 'output' / 'report.md'} · candidate {candidate}
  where: Part 2 of the report
  why: It bounds the sum by distances.

Related: definitions, lemmas, steps and neighbouring statements that the request would use or that do part of its work.

- session swithpeer · attempt · with a peer · not reviewed
  report {sessions / 'swithpeer' / 'output' / 'report.md'}
  where: Part 2
  why: The same inequality, earlier.

Read:
- 6 of 6 elements in 5 of 5 modules: the whole canon
- the unpublished work of 2 sessions: swithpeer and swithreview
''', text)
        self.assertNotIn('sinvented', text)
        self.assertNotIn('Part 9', text)
        self.assertEqual(len(self.calls()), 3)

    def test_the_history_is_read_when_asked_for_and_a_hit_is_an_element_whose_texts_were_read(self):
        history = self.instance / 'canon' / 'history' / 'Small' / 'sumTwo'
        history.mkdir(parents=True)
        (history / '000002-record.md').write_text('# Small.sumTwo: record replaced\n\n+An earlier wording.\n',
                                                  encoding='utf-8')
        self.script([{'system': '<history', 'answer': answer(hits=[
            {'name': 'Small.sumTwo', 'match': 'direct', 'why': 'Its earlier record worded the value differently.'},
            {'name': 'Small.sumZero', 'match': 'direct', 'why': 'An element of the canon, but none of its texts was given.'}])}])
        code, text = self.command(self.searcher(), '--file', self.request(), '--history')
        self.assertEqual(code, 0, text)
        self.assertIn(f'Hits in replaced texts of the history (1): 1 direct, 0 related\n\n{search.GROUPS[0][1]}\n\n'
                      '- Small.sumTwo · ', text)
        self.assertNotIn(search.GROUPS[1][1], text)
        self.assertIn('  the replaced texts: view Small.sumTwo --part history\n'
                      '  why: Its earlier record worded the value differently.\n', text)
        self.assertIn('- the replaced texts of 1 element\nNot read:\n\nA search can miss', text)
        self.assertNotIn('--history adds them', text)

    def test_an_element_whose_replaced_texts_stand_in_two_parts_is_counted_once_and_not_when_one_part_was_not_read(self):
        self.small_parts()
        # Two texts of one element, each shorter than a part and the two together longer: two parts of the
        # history, and both hold texts of Small.sumTwo.
        history = self.instance / 'canon' / 'history' / 'Small' / 'sumTwo'
        history.mkdir(parents=True)
        for number in (2, 3):
            (history / f'00000{number}-record.md').write_text(
                ''.join(f'+Line {line} of the wording that publication {number} replaced.\n' for line in range(1, 6)),
                encoding='utf-8')
        code, text = self.command(self.searcher(), '--file', self.request(), '--history')
        self.assertEqual(code, 0, text)
        folder, = (path for path in self.home.iterdir() if path.is_dir())
        self.assertEqual([part['elements'] for part in read_json(folder / 'parts.json')['parts'] if part['kind'] == 'history'],
                         [['Small.sumTwo'], ['Small.sumTwo']])
        # Both parts were read: the element is counted once, in the answer and in the ledger.
        self.assertIn('- the unpublished work of 0 sessions\n- the replaced texts of 1 element\nNot read:\n\nA search can miss',
                      text)
        self.assertEqual(self.ledger()[-1]['read']['history_elements'], 1)
        # One of the two parts is not read: the element is named under "Not read" and is not counted as read.
        self.script([{'system': 'file="000003-record.md"', 'exit': 3}])
        code, text = self.command(self.searcher(), '--file', self.request('Another request.', 'other.md'), '--history')
        self.assertEqual(code, 0, text)
        self.assertIn('Incomplete: 1 of the 6 parts of this search was not read', text)
        self.assertIn('- the replaced texts of 0 elements\nNot read:\n- the replaced texts of 1 element, Small.sumTwo: '
                      'the Claude CLI ended with exit code 3 and reported no result; ', text)
        closing = self.ledger()[-1]['read']
        self.assertEqual((closing['history_elements'], closing['parts_not_read']), (0, 1))

    def test_a_part_whose_light_session_failed_is_named_under_not_read_and_read_by_the_next_command(self):
        self.small_parts()
        self.script([{'system': '### Module Small.Sums.Low', 'exit': 3},
                     {'system': '### Module Small.Sums.High', 'answer': 'I found nothing of use.', 'times': 1},
                     {'system': '### Module Small.Sums.High', 'answer': answer(hits=[{'name': 'Small.sumThree', 'why': 'Nine.'}])}])
        arguments = (self.searcher(), '--file', self.request())
        code, text = self.command(*arguments)
        self.assertEqual(code, 0, text)
        # The answer that was not in the form asked for was asked for once more, in the same run, and then read.
        self.assertIn(f'Hits in the canon (1): 0 direct, 1 related\n\n{RELATED}\n\n- Small.sumThree · ', text)
        self.assertIn('Incomplete: 1 of the 4 parts of this search was not read; "Not read" below says which. '
                      'Run the same command again to have them read.', text)
        self.assertIn('Read:\n- 4 of 6 elements in 4 of 5 modules: the whole canon\n', text)
        folder, = (path for path in self.home.iterdir() if path.is_dir())
        failed = folder / 'parts' / '04'
        self.assertEqual(list(read_json(folder / 'parts.json')['parts'][3]['modules']), ['Small.Sums.Low'])
        self.assertIn(f'Not read:\n- Small.Sums (1 of its 2 modules: Small.Sums.Low) (2 elements of 1 module): '
                      f"the Claude CLI ended with exit code 3 and reported no result; what it wrote is in {failed / 'run-2'}\n", text)
        self.assertEqual(len(self.calls()), 4 + 1 + 1)  # the dead part and the malformed answer were each tried once more
        self.assertFalse(read_json(failed.parents[1] / 'result.json')['complete'])
        # The same command again: the part that was not read is read, and no other.
        self.script([{'answer': answer(hits=[{'name': 'Small.sumTwo', 'why': 'Four.'}])}])
        code, text = self.command(*arguments)
        self.assertEqual((code, len(self.calls())), (0, 7), text)
        self.assertNotIn('Incomplete', text)
        self.assertIn('Hits in the canon (2)', text)
        self.assertIn('Read:\n- 6 of 6 elements in 5 of 5 modules: the whole canon\n', text)
        # Complete now: a third command is given the same answer and reads nothing.
        self.assertEqual((self.command(*arguments)[1], len(self.calls())), (text, 7))
        # Seven light sessions, each with its line, and the two runs of the one search, each with the line that
        # says what had been read by then.
        lines = self.ledger()
        self.assertEqual([line['light_sessions'] for line in lines], [1] * 6 + [0] + [1] + [0])
        self.assertEqual([line['read']['parts_not_read'] for line in lines if 'read' in line], [1, 0])
        self.assertEqual((search_usage(self.instance)['searches'], search_usage(self.instance)['light_sessions']), (1, 7))

    def test_a_part_that_was_read_keeps_no_copy_of_its_text_and_one_that_was_not_keeps_it_for_the_next_command(self):
        self.small_parts()
        self.script([{'system': '### Module Small.Steps.Next', 'exit': 3}])
        arguments = (self.searcher(), '--file', self.request())
        code, text = self.command(*arguments)
        self.assertEqual(code, 0, text)
        self.assertIn('Incomplete: 1 of the 4 parts', text)
        folder, = (path for path in self.home.iterdir() if path.is_dir())
        # Of the four parts only the one that was not read still has the file with its text.
        self.assertEqual([path.is_file() for path in sorted(folder.glob('parts/*/outcome.json'))], [True] * 4)
        kept, = folder.glob('parts/*/system.txt')
        self.assertEqual(kept, folder / 'parts' / '02' / 'system.txt')
        system = kept.read_text(encoding='utf-8')
        self.assertIn('\nBEGIN PART\n\n## Folder Small.Steps\n', system)
        self.assertEqual([call['system'] for call in self.calls()].count(system), search.LIGHT_TRIES)
        # What each part held is still told by parts.json, and what its light session wrote stays.
        self.assertEqual([list(part['modules']) for part in read_json(folder / 'parts.json')['parts']],
                         [['Small.Defs', 'Small.Root'], ['Small.Steps.Next'], ['Small.Sums.High'], ['Small.Sums.Low']])
        self.assertTrue(all((folder / 'parts' / f'{number:02d}' / 'run-1' / 'cli.stdout.jsonl').is_file() for number in range(1, 5)))
        # The same command again has that part read from the file that was kept, the same text, and no other
        # part; then that file goes as well, and no file of the search holds the text of a part.
        self.script([{'answer': answer(hits=[{'name': 'Small.sumSucc', 'why': 'The step.'}])}])
        code, text = self.command(*arguments)
        self.assertEqual((code, len(self.calls())), (0, 3 + search.LIGHT_TRIES + 1), text)
        self.assertEqual(self.calls()[-1]['system'], system)
        self.assertNotIn('Incomplete', text)
        self.assertIn(f'Hits in the canon (1): 0 direct, 1 related\n\n{RELATED}\n\n- Small.sumSucc · ', text)
        self.assertEqual(list(folder.glob('parts/*/system.txt')), [])
        for path in folder.rglob('*'):
            if path.is_file():
                self.assertNotIn(b'BEGIN PART', path.read_bytes(), path)

    def test_after_a_publication_in_one_folder_the_light_sessions_are_given_the_other_parts_unchanged(self):
        self.small_parts()
        arguments = (self.searcher(), '--file', self.request())
        code, first = self.command(*arguments)
        self.assertEqual(code, 0, first)
        before = [call['system'] for call in self.calls()]
        self.assertEqual(len(before), 4)
        self.publish(self.candidate(
            modules={'Small/Steps/Back.lean': module_text(theorem('sumOne', ': oddSum 1 = 1'))},
            records={'Small/sumOne.md': record_text('The first odd number is one.')}))
        code, second = self.command(*arguments)
        self.assertEqual(code, 0, second)
        # The canon has another revision and one element more, and the answer says so.
        self.assertNotEqual(first.splitlines()[0].split(' · ')[1], second.splitlines()[0].split(' · ')[1])
        self.assertIn('Read:\n- 7 of 7 elements in 6 of 6 modules: the whole canon\n', second)
        after = [call['system'] for call in self.calls()[4:]]
        # The system prompt is what the provider keeps in its cache. For every part without the folder that was
        # published to, it is, character for character, the one of the search before; so nothing in it tells
        # of the revision, of the day or of the size of the canon.
        elsewhere = [system for system in after if '## Folder Small.Steps\n' not in system]
        self.assertEqual(sorted(elsewhere), sorted(system for system in before if '## Folder Small.Steps\n' not in system))
        self.assertEqual(len(elsewhere), 3)
        changed = [system for system in after if '## Folder Small.Steps\n' in system]
        self.assertTrue(changed and all(system not in before for system in changed))
        self.assertEqual(sum(system.count('### Module Small.Steps.Back\n') for system in changed), 1)

    def test_a_refusal_of_the_provider_leaves_the_parts_not_read_and_starts_no_further_session(self):
        self.small_parts()
        self.configure(search={'model': 'claude/sonnet', 'effort': 'low', 'parallel': 1})
        self.script([{'refuse': 'usage_limit'}])
        code, text = self.command(self.searcher(), '--file', self.request())
        self.assertEqual(code, 0, text)
        self.assertEqual(len(self.calls()), 1)
        self.assertIn('Incomplete: 4 of the 4 parts of this search were not read', text)
        self.assertIn('Hits in the canon (0)', text)
        self.assertIn('Read:\n- 0 of 6 elements in 0 of 5 modules: the whole canon\n', text)
        self.assertRegex(text, r'Not read:\n- module Small\.Defs; module Small\.Root \(2 elements of 2 modules\): the provider '
                               r'refused the light session \(usage_limit\); it may take sessions again from about '
                               r'\d{4}-\d\d-\d\d \d\d:\d\d\n'
                               r'- Small\.Steps \(1 element of 1 module\): not started: the provider had refused '
                               r'another light session of the same work \(usage_limit\)\n')
        # A safeguard of the model that stops a session is tried once more, and then the part is not read either.
        self.script([{'refuse': 'model_refusal'}])
        code, text = self.command(self.searcher(), '--file', self.request('Another request.', 'other.md'))
        self.assertEqual((code, len(self.calls())), (0, 1 + 8), text)
        self.assertIn('a safeguard of the model stopped the light session', text)

    def test_the_operator_chooses_a_configuration_and_a_folder_and_a_session_does_not(self):
        out = self.root / 'kept'
        code, text = self.command(self.instance, '--file', self.request(), '--model', 'claude/opus', '--effort', 'medium',
                                  '--out', out)
        self.assertEqual(code, 0, text)
        self.assertIn('read by claude/opus at medium effort', text)
        argv = self.calls()[0]['argv']
        self.assertEqual((argv[argv.index('--model') + 1], argv[argv.index('--effort') + 1]), ('opus', 'medium'))
        self.assertFalse(self.home.exists())  # nothing was written in the instance
        # The folder of the search, the ledger, the slot of its light session and the turn of its process.
        self.assertEqual(sorted(path.name[:2] for path in out.iterdir()), ['le', 's-', 'sl', 'tu'])
        self.assertEqual({json.loads(row)['session'] for row in (out / 'ledger.jsonl').read_text(encoding='utf-8').splitlines()},
                         {'operator'})
        for option in (('--model', 'claude/opus'), ('--effort', 'high'), ('--out', out)):
            code, text = self.command(self.searcher(), '--file', self.request(), *option)
            self.assertEqual(code, 1)
            self.assertIn('options of the operator', json.loads(text)['error'])
        for arguments, said in (((self.instance, '--file', self.request(), '--model', 'codex/gpt'), 'claude/<model>'),
                                ((self.instance, '--file', self.request(), '--effort', 'huge'), 'effort'),
                                ((self.searcher(),), '--file'),
                                ((self.searcher(), '--file', self.request('  \n', 'empty.md')), 'is empty'),
                                ((self.root, '--file', self.request()), 'not a session directory')):
            code, text = self.command(*arguments)
            self.assertEqual(code, 1, text)
            self.assertIn(said, json.loads(text)['error'])


class WaitingTests(SearchCase):
    """The process that does the work is a real one here, started as a command of a session starts it."""

    def setUp(self):
        super().setUp()
        self.inline.stop()
        real, self.started = search.start, []

        def kept(folder):
            self.started.append(real(folder))
            return self.started[-1]

        started = patch.object(search, 'start', side_effect=kept)
        started.start()
        self.addCleanup(started.stop)
        # No process of a test outlives it: the folder of the test is removed when the test ends.
        self.addCleanup(lambda: [process.wait(timeout=60) for process in self.started])

    def until_done(self, *arguments):
        deadline = time.monotonic() + 120
        while True:
            code, text = self.command(*arguments, '--timeout', '5')
            if code != 124 or time.monotonic() > deadline:
                return code, text

    def test_a_search_that_is_not_done_says_so_and_the_same_command_finds_it_again(self):
        self.script([{'hold': 'go', 'answer': answer(hits=[{'name': 'Small.sumTwo', 'why': 'Four.'}])}])
        arguments = (self.searcher(), '--file', self.request())
        for _ in range(2):
            code, text = self.command(*arguments, '--timeout', '0.5')
            self.assertEqual((code, json.loads(text)),
                             (124, {'waiting': True, 'hint': 'the search continues; run the same command again'}))
        # Another session with the same request, scope and options waits for the same search.
        code, _ = self.command(self.reader('sother'), '--file', self.request(), '--timeout', '0')
        self.assertEqual(code, 124)
        folder, = (path for path in self.home.iterdir() if path.is_dir())
        (self.scenario_folder / 'go').touch()
        code, text = self.until_done(*arguments)
        self.assertEqual(code, 0, text)
        self.assertIn(f'Hits in the canon (1): 0 direct, 1 related\n\n{RELATED}\n\n- Small.sumTwo · ', text)
        self.assertEqual(len(self.calls()), 1)  # one process did the work, once
        self.assertEqual(self.command(self.reader('sother'), '--file', self.request())[1], text)
        self.assertEqual(len(self.calls()), 1)
        # Another request, another scope and another option are each another search.
        for more in (('--file', self.request('Something else.', 'else.md')), ('--file', self.request(), '--folder', 'Small.Sums'),
                     ('--file', self.request(), '--history')):
            self.assertEqual(self.until_done(self.searcher(), *more)[0], 0)
        self.assertEqual(len([path for path in self.home.iterdir() if path.is_dir()]), 4)
        self.assertEqual((folder / 'worker.log').read_bytes(), b'')

    def test_two_searches_at_once_share_the_slots_of_the_instance(self):
        # With `parallel` 2 there are two turns, so two of the three searches are at work at one time, each in
        # a process of its own. Each search has three parts, the canon and the work of two sessions, and its
        # process reads them two at a time (search.read_parts). The only thing that keeps the two processes
        # from running four light sessions beside each other is the slot a light session holds while its CLI
        # runs (light.run), which the processes take from one folder. That four would run without the slot
        # was confirmed by reading light.run, search.read_parts and search.work, and by no run of the
        # programs without the slot. With `parallel` 1 the single turn would let one process work at a time,
        # and the number below would be 1 with the slot and without it.
        self.configure(search={'model': 'claude/sonnet', 'effort': 'low', 'parallel': 2})
        self.unpublished()
        # Every light session waits for the file `go`, so that the test sees how many run beside each other
        # without depending on how fast a process starts on the machine. (A first form of this test let each
        # stand-in run for half a second; on a loaded machine no two of them overlapped and it failed.)
        self.script([{'hold': 'go', 'answer': NOTHING}])
        commands = [(self.searcher(), '--file', self.request(f'Request {number}.', f'request-{number}.md')) for number in range(3)]
        for arguments in commands:
            self.assertEqual(self.command(*arguments, '--timeout', '0')[0], 124)
        running = self.scenario_folder / 'running'

        def beside():
            return len(list(running.iterdir())) if running.is_dir() else 0

        deadline = time.monotonic() + 50
        while beside() < 2 and time.monotonic() < deadline:
            time.sleep(0.05)
        # Two light sessions run beside each other. Two processes are at work with two threads each, so two
        # more calls stand ready; they find no slot, and the number stays at two.
        self.assertEqual(beside(), 2)
        time.sleep(3)
        self.assertEqual(beside(), 2)
        (self.scenario_folder / 'go').touch()
        for arguments in commands:
            self.assertEqual(self.until_done(*arguments)[0], 0)
        calls = self.calls()
        self.assertEqual(len(calls), 9)
        # Two light sessions did run beside each other, and never more than two.
        self.assertEqual(max(call['beside'] for call in calls), 2)
        # Both turns were taken: a process takes the second only while another holds the first.
        self.assertEqual(sorted(path.name for path in self.home.glob('turn-*.lock')), ['turn-0.lock', 'turn-1.lock'])
        self.assertEqual(sorted(path.name for path in self.home.glob('slot-*.lock')), ['slot-0.lock', 'slot-1.lock'])

    def test_with_one_turn_a_second_search_reads_nothing_of_the_research_while_the_first_is_at_work(self):
        self.configure(search={'model': 'claude/sonnet', 'effort': 'low', 'parallel': 1})
        self.script([{'hold': 'go', 'answer': NOTHING}])
        first = (self.searcher(), '--file', self.request('Request 1.', 'request-1.md'))
        second = (self.searcher(), '--file', self.request('Request 2.', 'request-2.md'))

        def wait_for(condition):
            deadline = time.monotonic() + 120
            while not condition() and time.monotonic() < deadline:
                time.sleep(0.1)
            self.assertTrue(condition())

        began = time.monotonic()
        self.assertEqual(self.command(*first, '--timeout', '0')[0], 124)
        # The first search is at work: it has read the research and cut its parts, and its light session is held.
        wait_for(lambda: len(self.calls()) == 1)
        took = time.monotonic() - began
        one, = (path for path in self.home.iterdir() if path.is_dir())
        self.assertTrue((one / 'parts.json').is_file())
        self.assertEqual(self.command(*second, '--timeout', '0')[0], 124)
        two, = (path for path in self.home.iterdir() if path.is_dir() and path != one)
        # The process of the second search runs and holds the lock of its folder, so the same command finds it
        # at work. It is given as long again as the first took from its command to its light session, and
        # more: it has read nothing of the research, cut no part and started no light session.
        wait_for(lambda: search.working(two))
        time.sleep(min(max(2.0, 1.5 * took), 20.0))  # the stand-in holds the first light session for a minute
        self.assertFalse((self.scenario_folder / 'go').exists())
        self.assertTrue(search.working(two))
        self.assertFalse((two / 'parts.json').exists())
        self.assertFalse((two / 'parts').exists())
        self.assertEqual(len(self.calls()), 1)
        self.assertEqual(self.command(*second, '--timeout', '0')[0], 124)
        # The turns are locks beside the slots, one for each search that may be at work.
        self.assertEqual(sorted(path.name for path in self.home.glob('turn-*.lock')), ['turn-0.lock'])
        (self.scenario_folder / 'go').touch()
        for arguments in (first, second):
            self.assertEqual(self.until_done(*arguments)[0], 0)
        self.assertTrue((two / 'parts.json').is_file())
        self.assertEqual(len(self.calls()), 2)

    def test_a_process_that_ended_without_a_result_is_reported_and_the_next_command_starts_again(self):
        arguments = (self.searcher(), '--file', self.request())
        def gone(folder):
            self.started.append(subprocess.Popen([sys.executable, '-c', 'pass']))
            return self.started[-1]

        with patch.object(search, 'start', side_effect=gone):
            code, text = self.command(*arguments)
        self.assertEqual(code, 1)
        self.assertIn('ended before it had finished', json.loads(text)['error'])
        self.assertIn('Run the same command again', json.loads(text)['error'])
        code, text = self.until_done(*arguments)
        self.assertEqual(code, 0, text)
        self.assertIn('Hits in the canon (0)', text)

    def test_work_that_fails_is_reported_once_and_started_again_by_the_next_command(self):
        arguments = (self.searcher(), '--file', self.request())
        state = self.instance / 'runner' / 'state.json'
        kept = state.read_bytes()
        state.write_text('{}', encoding='utf-8')  # the process cannot read the pipelines
        code, text = self.until_done(*arguments)
        self.assertEqual(code, 1, text)
        self.assertIn("the search ended with an error: KeyError: 'pipelines'. Run the same command again", json.loads(text)['error'])
        folder, = (path for path in self.home.iterdir() if path.is_dir())
        self.assertIn(b'KeyError', (folder / 'worker.log').read_bytes())
        state.write_bytes(kept)
        code, text = self.until_done(*arguments)
        self.assertEqual(code, 0, text)


class DescentTests(SearchCase):
    def writer(self, role='peer', sid='swriter'):
        """The session folder of a peer or an organizer, and its output folder, which is its candidate."""
        folder = self.reader(sid, role=role)
        (folder / 'output' / 'descriptions').mkdir(parents=True)
        return folder, folder / 'output'

    def describe(self, candidate, kind, name, text):
        path = canon_index.description_file(candidate, kind, name)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding='utf-8')

    def purposes(self, candidate, *items):
        write_json(candidate / 'descriptions' / 'purposes.json',
                   [{'target': target, 'purpose': purpose} for target, purpose in items])

    def peer(self):
        """A peer whose change adds the module Small.Sums.Four with its line."""
        session, output = self.writer()
        (output / 'lean' / 'Small' / 'Sums').mkdir(parents=True)
        (output / 'lean' / 'Small' / 'Sums' / 'Four.lean').write_text(
            module_text(theorem('sumFour', ': oddSum 4 = 16')), encoding='utf-8')
        self.describe(output, 'module', 'Small.Sums.Four', 'The value of the sum for four terms.\n')
        self.purposes(output, ('Small.Sums.Four', 'what the first four odd numbers  add up to'))
        return session, output

    def opens(self, *names_by_purpose):
        return answer(answers=[{'purpose': number, 'open': list(names)} for number, names in enumerate(names_by_purpose, 1)])

    def test_the_test_of_a_peers_module_line_passes_and_leaves_its_receipt(self):
        session, output = self.peer()
        self.script([{'system': 'BEGIN LEVEL', 'answer': self.opens(
            ['Small.Sums.Four', 'Small.Sums.Low', 'Small.Elsewhere', 'Small.Sums.Four'])}])
        code, text = self.command('descent-test', session, main=canon_tool_main)
        self.assertEqual(code, 0, text)
        revision = replay(self.instance)['sequence']
        receipt = output / 'descriptions' / 'tests.json'
        self.assertEqual(text, f'''Blind descent test · revision {revision} · reader claude/sonnet at low effort

Passed (1)
- Small.Sums.Four at the level Small.Sums — purpose: what the first four odd numbers add up to — the reader opened: Small.Sums.Four and Small.Sums.Low

1 purpose: 1 passed, 0 failed, 0 not tested.
The receipt is {receipt}.
''')
        line = 'The value of the sum for four terms.\n'
        # The receipt names the folder in which the test was taken, and the result there holds the same results.
        work, = self.home.glob('t-*')
        self.assertEqual(read_json(receipt), {
            'reader': {'model': 'claude/sonnet', 'effort': 'low'}, 'revision': revision, 'work': work.name,
            'results': [{'target': 'Small.Sums.Four', 'kind': 'module', 'text_sha': canon_index.text_sha(line),
                         'level': 'Small.Sums', 'purpose': 'what the first four odd numbers add up to',
                         'opened': ['Small.Sums.Four', 'Small.Sums.Low'], 'passed': True}]})
        self.assertEqual(read_json(work / 'result.json')['tests']['results'], read_json(receipt)['results'])
        self.assertEqual(read_json(work / 'request.json')['caller'], 'swriter')
        # The receipt is one that the check of a change accepts for this line as it stands.
        taken = canon_index.results_for(canon_index.test_results(output), 'module', 'Small.Sums.Four', line)
        self.assertEqual([result['passed'] for result in taken], [True])
        # What the reader was given: the level that holds the target, with the candidate's module beside the
        # canon's, names and descriptions only.
        call, = self.calls()
        self.assertTrue(call['system'].startswith(search.BLIND))
        self.assertTrue(call['system'].endswith('''
BEGIN LEVEL
The items directly inside the folder Small.Sums.

Modules

- Small.Sums.Four
  The value of the sum for four terms.
- Small.Sums.High
  Values of the sum for three terms.
- Small.Sums.Low
  Values of the sum for zero and two terms.
END LEVEL
'''))
        self.assertIn('BEGIN PURPOSES\n1. what the first four odd numbers add up to\nEND PURPOSES', call['request'])
        for below in ('sumFour', 'sumTwo', 'elements'):
            self.assertNotIn(below, call['system'])
        # Nothing else in the session's output changed, and the ledger has the line of the test.
        self.assertEqual(sorted(path.name for path in (output / 'descriptions').iterdir()),
                         ['modules', 'purposes.json', 'tests.json'])
        used, closing = (json.loads(row) for row in (self.home / 'ledger.jsonl').read_text(encoding='utf-8').splitlines())
        self.assertEqual((used['kind'], used['key'], used['session'], used['light_sessions'], used['cost_usd'], 'read' in used),
                         ('descent-test', work.name, 'swriter', 1, 0.0125, False))
        self.assertEqual((closing['kind'], closing['key'], closing['light_sessions'], closing['read']),
                         ('descent-test', work.name, 0, {'revision': revision, 'levels': 1, 'purposes': 1, 'levels_not_read': 0}))
        # The level was read, so the file with its listing is kept no longer.
        self.assertTrue(read_json(next(self.home.glob('t-*/parts/01/outcome.json')))['ok'])
        self.assertEqual(list(self.home.glob('t-*/parts/*/system.txt')), [])
        # The same test again is not taken again: the same texts and purposes have the same result.
        self.assertEqual(self.command('descent-test', session, main=canon_tool_main), (code, text))
        self.assertEqual(len(self.calls()), 1)

    def test_a_purpose_fails_when_the_reader_does_not_open_the_target_and_a_new_text_is_tested_anew(self):
        session, output = self.peer()
        self.script([{'system': 'BEGIN LEVEL', 'answer': self.opens(['Small.Sums.High', 'Small.Sums.Low'])}])
        code, text = self.command('descent-test', session, main=canon_tool_main)
        self.assertEqual(code, 1, text)
        self.assertIn('Failed (1)\n- Small.Sums.Four at the level Small.Sums — purpose: what the first four odd numbers add up to '
                      '— the reader opened instead: Small.Sums.High and Small.Sums.Low\n\n'
                      '1 purpose: 0 passed, 1 failed, 0 not tested.\n', text)
        result, = read_json(output / 'descriptions' / 'tests.json')['results']
        self.assertEqual((result['opened'], result['passed']), (['Small.Sums.High', 'Small.Sums.Low'], False))
        # The line is written anew, so the test is taken anew, on the new text. The reader names the target
        # second, and only as many names count as a reader is asked for.
        self.describe(output, 'module', 'Small.Sums.Four', 'The sum of the first four odd numbers, which is sixteen.\n')
        self.script([{'system': 'which is sixteen', 'answer': self.opens(['Small.Sums.Low', 'Small.Sums.Four'])}])
        with patch.object(search, 'OPEN_AT_MOST', 1):
            code, text = self.command('descent-test', session, main=canon_tool_main)
        self.assertEqual(code, 1, text)
        self.assertIn('the reader opened instead: Small.Sums.Low\n', text)
        result, = read_json(output / 'descriptions' / 'tests.json')['results']
        self.assertEqual((result['text_sha'], result['opened'], result['passed']),
                         (canon_index.text_sha('The sum of the first four odd numbers, which is sixteen.\n'),
                          ['Small.Sums.Low'], False))
        self.assertEqual(len(self.calls()), 2)
        # A reader that opens nothing fails the purpose as well.
        self.describe(output, 'module', 'Small.Sums.Four', 'Sixteen.\n')
        self.script([{'answer': self.opens([])}])
        code, text = self.command('descent-test', session, main=canon_tool_main)
        self.assertEqual(code, 1, text)
        self.assertIn('the reader opened instead: nothing\n', text)

    def test_an_organizers_texts_are_laid_over_the_canons_and_each_level_has_its_own_reader(self):
        session, output = self.writer('organizer', 'sorganizer')
        self.describe(output, 'folder', 'Small.Sums', 'Base cases: the sum for small numbers of terms.\n\nBoundary: none of note.\n')
        self.describe(output, 'module', 'Small.Sums.Low', 'The sum for no terms and for two.\n')
        self.purposes(output, ('Small.Sums', 'a base case for an induction'), ('Small.Sums', 'the sum of three odd numbers'),
                      ('Small.Sums.Low', 'the empty sum'), ('Small.Sums', 'a value to test a conjecture against'))
        self.script([{'system': 'The top of the library Small.', 'answer': self.opens(
            ['Small.Sums'], ['Small.Steps', 'Small.Defs'], ['Small.Sums', 'Small.Steps', 'Small.Defs', 'Small.Root', 'Small.Sums'])},
                     {'system': 'directly inside the folder Small.Sums', 'answer': self.opens(['Small.Sums.Low'])}])
        code, text = self.command('descent-test', session, main=canon_tool_main)
        self.assertEqual(code, 1, text)
        self.assertIn('4 purposes: 3 passed, 1 failed, 0 not tested.', text)
        results = read_json(output / 'descriptions' / 'tests.json')['results']
        self.assertEqual([(result['target'], result['kind'], result['level'], result['passed']) for result in results],
                         [('Small.Sums', 'folder', 'Small', True), ('Small.Sums', 'folder', 'Small', False),
                          ('Small.Sums', 'folder', 'Small', True), ('Small.Sums.Low', 'module', 'Small.Sums', True)])
        self.assertEqual(results[2]['opened'], ['Small.Sums', 'Small.Steps', 'Small.Defs', 'Small.Root'])
        top, inside = sorted(self.calls(), key=lambda call: 'directly inside' in call['system'])
        self.assertTrue(top['system'].endswith('''
BEGIN LEVEL
The top of the library Small.

Folders

- Small.Steps
  Statements that pass from one number of terms to the next.
- Small.Sums
  Base cases: the sum for small numbers of terms.
  Boundary: none of note.

Modules

- Small.Defs
  The definition of the sum of the first odd numbers.
- Small.Root
  (no line yet)
END LEVEL
'''))
        self.assertIn('BEGIN PURPOSES\n1. a base case for an induction\n2. the sum of three odd numbers\n'
                      '3. a value to test a conjecture against\nEND PURPOSES', top['request'])
        self.assertIn('- Small.Sums.Low\n  The sum for no terms and for two.\n', inside['system'])
        self.assertNotIn(LINES['Small.Sums.Low'], inside['system'])

    def test_a_refusal_of_the_provider_is_recorded_as_unavailable_and_the_next_command_tests_again(self):
        session, output = self.peer()
        self.script([{'refuse': 'usage_limit'}])
        code, text = self.command('descent-test', session, main=canon_tool_main)
        self.assertEqual(code, 0, text)
        self.assertRegex(text, r'Not tested, recorded as unavailable \(1\)\n- Small\.Sums\.Four at the level Small\.Sums — purpose: '
                               r'what the first four odd numbers add up to — the provider refused the light session \(usage_limit\)')
        self.assertIn('1 purpose: 0 passed, 0 failed, 1 not tested. Run the same command again to test those not tested.\n'
                      'The reader of the level Small.Sums could not be had. `prepare` takes these results as they stand: '
                      'a description on which no test could be taken is published as not tested, and `index --due` '
                      'lists it for the organizers.\n', text)
        result, = read_json(output / 'descriptions' / 'tests.json')['results']
        self.assertEqual(result, {'target': 'Small.Sums.Four', 'kind': 'module', 'level': 'Small.Sums',
                                  'text_sha': canon_index.text_sha('The value of the sum for four terms.\n'),
                                  'purpose': 'what the first four odd numbers add up to', 'unavailable': 'usage_limit'})
        # The level was not read, so the file with its listing is kept; once it has been read, the file goes.
        kept, = self.home.glob('t-*/parts/*/system.txt')
        system = kept.read_text(encoding='utf-8')
        self.assertIn('\nBEGIN LEVEL\nThe items directly inside the folder Small.Sums.\n', system)
        self.script([{'answer': self.opens(['Small.Sums.Four'])}])
        code, text = self.command('descent-test', session, main=canon_tool_main)
        self.assertEqual(code, 0, text)
        result, = read_json(output / 'descriptions' / 'tests.json')['results']
        self.assertEqual((result['opened'], result['passed']), (['Small.Sums.Four'], True))
        self.assertEqual(self.calls()[-1]['system'], system)
        self.assertFalse(kept.exists())
        self.assertTrue(read_json(kept.parent / 'outcome.json')['ok'])

    def test_a_reader_that_could_not_be_had_for_any_reason_leaves_a_record_and_the_command_does_not_fail(self):
        session, output = self.peer()
        row = {'target': 'Small.Sums.Four', 'kind': 'module', 'level': 'Small.Sums',
               'text_sha': canon_index.text_sha('The value of the sum for four terms.\n'),
               'purpose': 'what the first four odd numbers add up to'}
        # It speaks of no purpose, both times.
        self.script([{'answer': answer(answers=[])}])
        code, text = self.command('descent-test', session, main=canon_tool_main)
        self.assertEqual((code, len(self.calls())), (0, 2), text)
        said = 'the light session did not answer in the form it was asked for'
        self.assertIn('Not tested, recorded as unavailable (1)\n- Small.Sums.Four at the level Small.Sums — purpose: what '
                      f'the first four odd numbers add up to — {said}\n\n'
                      '1 purpose: 0 passed, 0 failed, 1 not tested. Run the same command again to test those not tested.\n'
                      'The reader of the level Small.Sums could not be had. `prepare` takes these results as they stand: '
                      'a description on which no test could be taken is published as not tested, and `index --due` '
                      'lists it for the organizers.\n', text)
        self.assertNotIn('no record', text)
        self.assertEqual(read_json(output / 'descriptions' / 'tests.json')['results'], [{**row, 'unavailable': said}])
        # The CLI dies in both tries of the next command: the same, with what happened as the reason.
        self.script([{'exit': 3}])
        code, text = self.command('descent-test', session, main=canon_tool_main)
        self.assertEqual((code, len(self.calls())), (0, 4), text)
        result, = read_json(output / 'descriptions' / 'tests.json')['results']
        self.assertIn('the Claude CLI ended with exit code 3 and reported no result', result['unavailable'])
        # The command given again when the reader can be had tests the level.
        self.script([{'answer': self.opens(['Small.Sums.Four'])}])
        code, text = self.command('descent-test', session, main=canon_tool_main)
        self.assertEqual((code, len(self.calls())), (0, 5), text)
        self.assertEqual(read_json(output / 'descriptions' / 'tests.json')['results'],
                         [{**row, 'opened': ['Small.Sums.Four'], 'passed': True}])

    def candidate_peer(self, sid='swriter'):
        """A peer that was launched with the guides that ask for descriptions, whose change adds the module
        Small.Sums.Four with its record and its line: (its session folder, its output folder)."""
        session, output = self.writer(sid=sid)
        write_json(session / 'input.json', {**read_json(session / 'input.json'), 'descriptions': True})
        for name, content in (('lean/Small/Sums/Four.lean', module_text(theorem('sumFour', ': oddSum 4 = 16'))),
                              ('records/Small/sumFour.md', record_text('The first four odd numbers sum to sixteen.'))):
            (output / name).parent.mkdir(parents=True, exist_ok=True)
            (output / name).write_text(content, encoding='utf-8', newline='\n')
        write_json(output / 'change.json', {'title': 'Four terms', 'description': 'The sum at four terms.',
                                            'replace': [], 'questions': [], 'resolutions': []})
        self.describe(output, 'module', 'Small.Sums.Four', 'The value of the sum for four terms.\n')
        self.purposes(output, ('Small.Sums.Four', 'what the first four odd numbers add up to'))
        return session, output

    def prepared(self, session):
        """The exit code and the printed summary of `prepare`, by the command a session gives."""
        code, text = self.command('prepare', session, '--timeout', self.patience, main=canon_tool_main)
        return code, json.loads(text)

    def test_prepare_takes_the_receipt_of_a_test_that_ran_for_the_session_and_no_other(self):
        session, output = self.candidate_peer()
        receipt = output / 'descriptions' / 'tests.json'
        refusal = ('descriptions/tests.json is not the receipt of a blind descent test of this session: {}. The canon '
                   'command descent-test takes the test and writes the file; run it, and then prepare again')
        code, printed = self.prepared(session)
        self.assertEqual((code, printed['build']), (1, None))
        self.assertIn('has taken the blind descent test on 0 different purposes', printed['errors'][0])
        # A receipt that no test produced: the form the command writes, with a passed result, written by hand.
        row = {'target': 'Small.Sums.Four', 'kind': 'module', 'level': 'Small.Sums',
               'text_sha': canon_index.text_sha('The value of the sum for four terms.\n'),
               'purpose': 'what the first four odd numbers add up to', 'opened': ['Small.Sums.Four'], 'passed': True}
        write_json(receipt, {'reader': {'model': 'claude/sonnet', 'effort': 'low'}, 'revision': 1, 'results': [row]})
        self.assertEqual(self.prepared(session), (1, {**printed, 'errors': [refusal.format('it names no test that was taken')]}))
        self.assertEqual(self.calls(), [])
        # The test that ran: its receipt is taken, and the candidate is built.
        self.script([{'answer': self.opens(['Small.Sums.Four'])}])
        self.assertEqual(self.command('descent-test', session, main=canon_tool_main)[0], 0)
        taken = read_json(receipt)
        self.assertEqual((taken['work'], taken['results']), (next(self.home.glob('t-*')).name, [row]))
        code, printed = self.prepared(session)
        self.assertEqual((code, printed['ok'], printed['added']), (0, True, ['Small.sumFour']), printed)
        # Its results changed by hand are not those of the test.
        write_json(receipt, {**taken, 'results': [{**row, 'purpose': 'another purpose'}]})
        self.assertEqual(self.prepared(session)[1]['errors'],
                         [refusal.format(f"its results are not those of the test it names, {taken['work']}")])
        # The receipt of the same test, taken for another session, is another test and is not this session's.
        other, other_output = self.candidate_peer('sother')
        self.assertEqual(self.command('descent-test', other, main=canon_tool_main)[0], 0)
        theirs = read_json(other_output / 'descriptions' / 'tests.json')
        self.assertEqual((theirs['results'], theirs['work'] != taken['work'], len(self.calls())), ([row], True, 2))
        write_json(receipt, theirs)
        self.assertEqual(self.prepared(session)[1]['errors'],
                         [refusal.format(f"the test it names, {theirs['work']}, was not taken for this session")])
        # The command, given again, writes the session's own receipt from the test that was taken; nothing is read.
        self.assertEqual(self.command('descent-test', session, main=canon_tool_main)[0], 0)
        self.assertEqual((read_json(receipt), len(self.calls())), (taken, 2))
        code, printed = self.prepared(session)
        self.assertEqual((code, printed['ok']), (0, True), printed)
        # Published, the line stands as tested, with the revision of the canon it was prepared against, and the
        # summary, which had no map of when the modules came, has one.
        self.publish(output)
        summary = canon_index.read_summary(self.instance)
        self.assertEqual(summary['modules']['Small.Sums.Four'],
                         {'text': 'The value of the sum for four terms.', 'revision': 1, 'published': 2, 'tested': True})
        self.assertEqual(summary['since'], {'Small.Defs': 0, 'Small.Root': 0, 'Small.Steps.Next': 1,
                                            'Small.Sums.Four': 2, 'Small.Sums.High': 1, 'Small.Sums.Low': 1})

    def test_one_purpose_given_three_times_is_one_test_of_a_folder_description(self):
        session, output = self.writer('organizer', 'sorganizer')
        write_json(session / 'input.json', {**read_json(session / 'input.json'), 'descriptions': True,
                                            'task': {'batch': [], 'batch_frozen': True}})
        write_json(output / 'organization.json', {'batch': []})
        write_json(output / 'change.json', {'title': 'The small cases described', 'description': 'What the folder holds.'})
        self.describe(output, 'folder', 'Small.Sums', 'Base cases: the sum for small numbers of terms.\n')
        self.purposes(output, *[('Small.Sums', 'a base case for an induction')] * 3)
        self.script([{'answer': self.opens(*[['Small.Sums']] * 3)}])
        code, text = self.command('descent-test', session, main=canon_tool_main)
        self.assertEqual(code, 0, text)
        self.assertIn('3 purposes: 3 passed, 0 failed, 0 not tested.', text)
        code, printed = self.prepared(session)
        self.assertEqual((code, printed['errors']), (1, [
            'the description of the folder Small.Sums has taken the blind descent test on 1 different purpose with the '
            'text it has now and needs at least 3; give it 3 different purposes in descriptions/purposes.json, each as '
            '{"target": "Small.Sums", "purpose": "..."}, and run the canon command descent-test']))
        self.purposes(output, ('Small.Sums', 'a base case for an induction'), ('Small.Sums', 'the sum of three odd numbers'),
                      ('Small.Sums', 'a value to test a conjecture against'))
        self.assertEqual(self.command('descent-test', session, main=canon_tool_main)[0], 0)
        code, printed = self.prepared(session)
        self.assertEqual((code, printed['ok'], printed['errors']), (0, True, []))

    def test_a_folder_and_a_module_of_one_name_are_two_items_and_each_is_judged_by_its_own(self):
        session, output = self.writer()
        # The canon has the folder Small.Sums, and the peer's change brings a module of that name.
        (output / 'lean' / 'Small').mkdir(parents=True)
        (output / 'lean' / 'Small' / 'Sums.lean').write_text(
            module_text(theorem('sumAll', '(n : Nat) : oddSum n = n * n')), encoding='utf-8')
        self.describe(output, 'module', 'Small.Sums', 'The closed form of the sum, for every number of terms.\n')
        # A bare name that is both means the one the candidate describes, the module; a target can also say which.
        self.purposes(output, ('Small.Sums', 'the closed form'), ('Small.Sums (folder)', 'a base case'),
                      ('Small.Sums (module)', 'the general statement'))
        # The reader names the bare name, which is no item, and the folder; then the folder; then both.
        self.script([{'answer': self.opens(['Small.Sums', 'Small.Sums (folder)'], ['Small.Sums (folder)'],
                                           ['Small.Sums (module)', 'Small.Sums (folder)'])}])
        code, text = self.command('descent-test', session, main=canon_tool_main)
        self.assertEqual(code, 1, text)
        results = read_json(output / 'descriptions' / 'tests.json')['results']
        self.assertEqual([(result['target'], result['kind'], result['opened'], result['passed']) for result in results], [
            ('Small.Sums', 'module', ['Small.Sums (folder)'], False),
            ('Small.Sums', 'folder', ['Small.Sums (folder)'], True),
            ('Small.Sums', 'module', ['Small.Sums (module)', 'Small.Sums (folder)'], True)])
        self.assertIn('Passed (2)\n'
                      '- Small.Sums (folder) at the level Small — purpose: a base case — the reader opened: Small.Sums (folder)\n'
                      '- Small.Sums (module) at the level Small — purpose: the general statement — the reader opened: '
                      'Small.Sums (module) and Small.Sums (folder)\n\n'
                      'Failed (1)\n'
                      '- Small.Sums (module) at the level Small — purpose: the closed form — the reader opened instead: '
                      'Small.Sums (folder)\n\n'
                      '3 purposes: 2 passed, 1 failed, 0 not tested.\n', text)
        call, = self.calls()
        self.assertTrue(call['system'].endswith('''
BEGIN LEVEL
The top of the library Small.
A folder and a module can have the same name. They are two items, and they stand below with (folder) or (module) after the name. Name such an item with that word in brackets, as it stands.

Folders

- Small.Steps
  Statements that pass from one number of terms to the next.
- Small.Sums (folder)
  Particular values of the sum of the first odd numbers, each computed outright.
  It serves as a stock of base cases.

Modules

- Small.Defs
  The definition of the sum of the first odd numbers.
- Small.Root
  (no line yet)
- Small.Sums (module)
  The closed form of the sum, for every number of terms.
END LEVEL
'''), call['system'])
        # A level without such a pair has no such sentence and shows every item under its bare name (the other tests).
        self.purposes(output, ('Small.Steps (module)', 'the passage to the next number of terms'))
        code, text = self.command('descent-test', session, main=canon_tool_main)
        self.assertEqual((code, json.loads(text)['error']), (1, 'descriptions/purposes.json, entry 1: Small.Steps is no '
                                                               'module of the canon or of this change'))

    def test_a_folder_description_whose_paragraphs_were_joined_is_another_text_and_is_tested_anew(self):
        session, output = self.writer('organizer', 'sorganizer')
        apart, joined = 'Base cases of the sum.\n\nA stock for inductions.\n', 'Base cases of the sum.\nA stock for inductions.\n'
        self.describe(output, 'folder', 'Small.Sums', apart)
        self.purposes(output, ('Small.Sums', 'a base case for an induction'))
        self.script([{'answer': self.opens(['Small.Sums'])}])
        self.assertEqual(self.command('descent-test', session, main=canon_tool_main)[0], 0)
        first = read_json(output / 'descriptions' / 'tests.json')
        # The two paragraphs joined into one: the reader is given the same listing, and the text is another.
        self.describe(output, 'folder', 'Small.Sums', joined)
        self.assertEqual(self.command('descent-test', session, main=canon_tool_main)[0], 0)
        second = read_json(output / 'descriptions' / 'tests.json')
        one, two = self.calls()
        self.assertEqual(one['system'], two['system'])
        self.assertNotEqual(first['work'], second['work'])
        self.assertEqual((first['results'][0]['text_sha'], second['results'][0]['text_sha']),
                         (canon_index.text_sha(apart), canon_index.text_sha(joined)))
        self.assertEqual(len(canon_index.results_for(canon_index.test_results(output), 'folder', 'Small.Sums', joined)), 1)

    def test_the_modules_that_an_organizers_change_deletes_do_not_stand_in_the_level(self):
        session, output = self.writer('organizer', 'sorganizer')
        write_json(output / 'organization.json', {'batch': [], 'delete': ['Small.Sums.High', 'Small.Steps.Next']})
        self.describe(output, 'module', 'Small.Sums.Low', 'The sum for no terms and for two.\n')
        self.describe(output, 'folder', 'Small.Sums', 'Base cases of the sum.\n')
        self.purposes(output, ('Small.Sums.Low', 'the empty sum'), ('Small.Sums', 'a base case'))
        self.script([{'system': 'The top of the library Small.', 'answer': self.opens(['Small.Sums'])},
                     {'system': 'directly inside the folder Small.Sums', 'answer': self.opens(['Small.Sums.Low'])}])
        code, text = self.command('descent-test', session, main=canon_tool_main)
        self.assertEqual(code, 0, text)
        top, inside = sorted(self.calls(), key=lambda call: 'directly inside' in call['system'])
        # The deleted module is no item of its level, and the folder whose only module is deleted is no item of the top.
        self.assertTrue(inside['system'].endswith('\nBEGIN LEVEL\nThe items directly inside the folder Small.Sums.\n\n'
                                                  'Modules\n\n- Small.Sums.Low\n  The sum for no terms and for two.\nEND LEVEL\n'))
        self.assertNotIn('Small.Steps', top['system'])
        self.assertIn('- Small.Sums\n  Base cases of the sum.\n', top['system'])
        self.purposes(output, ('Small.Sums.High', 'the sum of three odd numbers'))
        code, text = self.command('descent-test', session, main=canon_tool_main)
        self.assertEqual((code, json.loads(text)['error']), (
            1, 'descriptions/purposes.json, entry 1: Small.Sums.High is a module of the canon that this change deletes, '
               'so the canon has no such module after the change and no level shows it'))
        # A folder of the canon whose every module the change deletes is refused in the same words, under
        # its bare name and where the target says that the folder is meant.
        for target in ('Small.Steps', 'Small.Steps (folder)'):
            self.purposes(output, (target, 'a step from one number of terms to the next'))
            code, text = self.command('descent-test', session, main=canon_tool_main)
            self.assertEqual((code, json.loads(text)['error']), (
                1, 'descriptions/purposes.json, entry 1: Small.Steps is a folder of the canon, and this change deletes '
                   'every module beneath it, so the canon has no such folder after the change and no level shows it'),
                target)
        # As a module the name was never in the canon, and it is refused as every unknown name is.
        self.purposes(output, ('Small.Steps (module)', 'a step from one number of terms to the next'))
        code, text = self.command('descent-test', session, main=canon_tool_main)
        self.assertEqual((code, json.loads(text)['error']), (1, 'descriptions/purposes.json, entry 1: Small.Steps is '
                                                               'no module of the canon or of this change'))
        # A name in `delete` that the canon does not have is refused as every unknown name is.
        write_json(output / 'organization.json', {'batch': [], 'delete': ['Small.Sums.High', 'Small.Sums.Never']})
        self.purposes(output, ('Small.Sums.Never', 'what never was'))
        code, text = self.command('descent-test', session, main=canon_tool_main)
        self.assertEqual((code, json.loads(text)['error']), (1, 'descriptions/purposes.json, entry 1: Small.Sums.Never is '
                                                               'no module and no folder of the canon or of this change'))

    def test_what_cannot_be_tested_is_refused_in_plain_words(self):
        session, output = self.peer()
        def refused(said, main=canon_tool_main, arguments=None):
            code, text = self.command(*(arguments or ('descent-test', session)), main=main)
            self.assertEqual(code, 1, text)
            self.assertIn(said, json.loads(text)['error'])

        self.purposes(output, ('Small.Sums.Five', 'the sum of five terms'))
        refused('entry 1: Small.Sums.Five is no module and no folder of the canon or of this change')
        self.purposes(output, ('Small.Root', 'the statement the research is about'))
        refused('entry 1: Small.Root has no description to test; write it as descriptions/modules/Small/Root.md first')
        write_json(output / 'descriptions' / 'purposes.json', [{'target': 'Small.Sums.Four'}])
        refused('entry 1: an entry has exactly "target" and "purpose"')
        write_json(output / 'descriptions' / 'purposes.json', [])
        refused('descriptions/purposes.json holds an array of')
        (output / 'descriptions' / 'purposes.json').unlink()
        refused('purposes.json is not there')
        refused('a peer or an organizer', arguments=('descent-test', self.searcher()))
        refused('works in the session folder of a peer or an organizer', arguments=('descent-test', self.instance))
        self.assertEqual(self.calls(), [])

    def test_the_operator_tests_the_descriptions_of_a_folder_outside_the_instance(self):
        candidate, out = self.root / 'described', self.root / 'kept'
        self.describe(candidate, 'module', 'Small.Root', 'The statement the research is to settle.\n')
        self.purposes(candidate, ('Small.Root', 'the root statement'))
        self.script([{'answer': self.opens(['Small.Root'])}])
        code, text = self.command(self.instance, '--descent-test', candidate, '--out', out, '--effort', 'medium')
        self.assertEqual(code, 0, text)
        self.assertIn('reader claude/sonnet at medium effort', text)
        self.assertEqual(read_json(candidate / 'descriptions' / 'tests.json')['results'][0]['passed'], True)
        self.assertFalse(self.home.exists())
        self.assertTrue(any(path.name.startswith('t-') for path in out.iterdir()))

    def test_the_operator_is_told_that_describe_reads_no_receipt_when_the_reader_could_not_be_had(self):
        candidate = self.root / 'described'
        self.describe(candidate, 'module', 'Small.Root', 'The statement the research is to settle.\n')
        self.purposes(candidate, ('Small.Root', 'the root statement'))
        self.script([{'answer': answer(answers=[])}])
        code, text = self.command(self.instance, '--descent-test', candidate)
        self.assertEqual((code, len(self.calls())), (0, 2), text)
        # The operator has no `prepare`, and `describe` records what it publishes as tested: the command says
        # that, and not what it says to a session.
        self.assertIn('1 purpose: 0 passed, 0 failed, 1 not tested. Run the same command again to test those not tested.\n'
                      'The reader of the level Small could not be had. The command `describe` reads no receipt and '
                      'records every description it publishes as tested, so a description of such a level that is '
                      'published now is recorded as tested without a test. Have the level tested, by this command '
                      'given again, before you publish its descriptions.\n'
                      f"The receipt is {candidate.resolve() / 'descriptions' / 'tests.json'}.\n", text)
        self.assertNotIn('`prepare`', text)
        self.assertNotIn('index --due', text)
        result, = read_json(candidate / 'descriptions' / 'tests.json')['results']
        self.assertEqual(result['unavailable'], 'the light session did not answer in the form it was asked for')


if __name__ == '__main__':
    unittest.main()
