"""The index of the canon: descriptions of modules and folders, the descent, and what keeps the index current.

The tests of the text form and of the tree work on values. Every other test works on an instance and goes
through the commands a session or the operator gives and through the runner's publication.
"""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import types
import unittest
from unittest.mock import patch

sys.path[:0] = [str(Path(__file__).resolve().parents[1]), str(Path(__file__).resolve().parent)]
import canon_index
import canon_tool
import knowledge
import settings
from canon import Canon, CanonError, load_change
from check import check_session, tree_hashes
from context import assemble
from runner import Runner, main, search_usage, status, uid
from runtime_support import InstanceLock, git, read_json, write_json
from support import POPEN, InstanceCase, module_text, record_text, session_record, theorem

# The kinds of event that the replay knew before the index had descriptions. A session host keeps the code it
# loaded at its start and replays the instance in its own process when it checks the output of a review or an
# organizer, so no publication may leave an event of another kind while such a host can still be alive.
KINDS_BEFORE = ('change', 'review', 'organization', 'questions')

ZERO_LINE = 'The value of the sum of odd numbers at zero terms, as a statement with its proof in Lean.\n'
TWO_LINE = 'The sum of the first two odd numbers, stated for use where a small case is checked by hand.\n'
SUMS_TEXT = ('Small cases of the sum of odd numbers: the value of the sum at particular numbers of terms.\n\n'
             'A session that wants a base case or a numerical check of the closed form finds it here.\n')
# When each module came, as the summary of the descriptions says it once the canon of `filed` has a description.
SINCE_FILED = {'Small.Defs': 0, 'Small.Root': 0, 'Small.Sums.Two': 1, 'Small.Sums.Zero': 1}


def installed_runtime():
    """The runtime folder of the skill where it is installed, or None when that is the folder under test.

    The skill is installed in the main working tree of the repository: the sessions of a running research
    read it there. A change to it is built in a linked working tree beside that one, and until the change
    is brought in, the main working tree holds the programs from before the change. Git says where the
    main working tree is. A test reads those programs from there and copies nothing out of them."""
    here = Path(__file__).resolve().parents[1]
    try:
        top, common = (subprocess.run(['git', 'rev-parse', *options], cwd=here, capture_output=True, text=True,
                                      timeout=120).stdout.strip()
                       for options in (['--show-toplevel'], ['--path-format=absolute', '--git-common-dir']))
        folder = (Path(common).parent / here.relative_to(Path(top).resolve())).resolve()
    except (OSError, ValueError, subprocess.SubprocessError):
        return None
    return folder if top and common and folder != here and (folder / 'canon.py').is_file() else None


def tree_identity(folder):
    """One identity for the files under a folder, by path and content."""
    digest = hashlib.sha256()
    for path in sorted(p for p in Path(folder).rglob('*') if p.is_file()):
        digest.update(path.relative_to(folder).as_posix().encode('utf-8') + b'\0' + path.read_bytes())
    return digest.hexdigest()


class TextFormTests(unittest.TestCase):
    def test_a_description_is_stored_in_one_form_and_its_identity_is_that_of_the_form(self):
        written = '\ufeff  A module of small cases.  \r\nIt holds two of them.\r\n\r\n\r\n'
        self.assertEqual(canon_index.parse_description(written, 'module', 'the line'),
                         'A module of small cases.\nIt holds two of them.\n')
        self.assertEqual(canon_index.text_sha(written),
                         canon_index.text_sha('A module of small cases.\nIt holds two of them.\n'))
        self.assertNotEqual(canon_index.text_sha(written), canon_index.text_sha('A module of small cases.'))
        folder = canon_index.parse_description('What it holds.\n\n\n\nWhat it is needed for.', 'folder', 'the text')
        self.assertEqual(folder, 'What it holds.\n\nWhat it is needed for.\n')

    def test_a_text_that_is_empty_or_would_break_a_view_is_refused_with_what_to_correct(self):
        for text, kind, said in (
                ('  \n\n', 'module', 'is empty'),
                ('What it holds.\n# A heading', 'folder', 'begins with "#"'),
                ('What it holds.\n```lean\ndef x := 1\n```', 'folder', 'three backticks'),
                ('First paragraph.\n\nSecond paragraph.', 'module', 'a module line is one paragraph'),
                ('Boundary: mixed content.', 'folder', 'begins the last paragraph'),
                ('Boundary: mixed.\n\nWhat it holds.', 'folder', 'begins the last paragraph'),
                ('What it holds.\n\nBoundary:', 'folder', 'begins the last paragraph')):
            with self.subTest(text=text):
                with self.assertRaises(CanonError) as raised:
                    canon_index.parse_description(text, kind, 'descriptions/x.md')
                self.assertIn(said, str(raised.exception))
                self.assertIn('descriptions/x.md', str(raised.exception))

    def test_the_boundary_paragraph_is_the_last_one_and_is_read_without_its_label(self):
        text = canon_index.parse_description(
            'Two unrelated topics.\n\nBoundary: the counting lemmas belong\nwith the bounds.', 'folder', 'the text')
        self.assertEqual(canon_index.boundary_of(text), 'the counting lemmas belong with the bounds.')
        self.assertIsNone(canon_index.boundary_of('Two unrelated topics.\n'))
        # In a module line the word has no such meaning, and the line stays one paragraph.
        self.assertEqual(canon_index.parse_description('Boundary: cases at the edge.', 'module', 'the line'),
                         'Boundary: cases at the edge.\n')

    def test_folders_parents_children_and_counts_are_read_off_the_names_of_the_modules(self):
        modules = {'Lib': [], 'Lib.Defs': ['Lib.a'], 'Lib.Ext': ['Lib.b'], 'Lib.Ext.Basic': ['Lib.c', 'Lib.d'],
                   'Lib.Ext.Moment.One': ['Lib.e'], 'Lib.Bar.Two': []}
        self.assertEqual(canon_index.folders_of(modules), ['Lib.Bar', 'Lib.Ext', 'Lib.Ext.Moment'])
        self.assertEqual([canon_index.parent(name, 'Lib') for name in ('Lib', 'Lib.Defs', 'Lib.Ext.Basic', 'Lib.Ext.Moment')],
                         ['Lib', 'Lib', 'Lib.Ext', 'Lib.Ext'])
        # The library's own module and the modules directly under the library stand at the top. `Lib.Ext` is a
        # module there and also a folder, and the module is no part of the folder.
        self.assertEqual(canon_index.children(modules, 'Lib', 'Lib'), (['Lib.Bar', 'Lib.Ext'], ['Lib', 'Lib.Defs', 'Lib.Ext']))
        self.assertEqual(canon_index.children(modules, 'Lib', 'Lib.Ext'), (['Lib.Ext.Moment'], ['Lib.Ext.Basic']))
        self.assertEqual(canon_index.counts(modules), {'Lib.Ext': (2, 3), 'Lib.Ext.Moment': (1, 1), 'Lib.Bar': (1, 0)})
        summary = {'modules': {'Lib.Ext.Basic': {'text': 'The line of the canon.'}}, 'folders': {}}
        overlay = {'modules': {'Lib.Ext.Basic': 'The line of the candidate.\n'}, 'folders': {}}
        self.assertEqual(canon_index.level_items(modules, 'Lib', summary, 'Lib.Ext', overlay), [
            {'name': 'Lib.Ext.Moment', 'kind': 'folder', 'text': None},
            {'name': 'Lib.Ext.Basic', 'kind': 'module', 'text': 'The line of the candidate.'}])
        self.assertEqual(canon_index.level_items(modules, 'Lib', summary, 'Lib.Ext')[1]['text'], 'The line of the canon.')


class IndexCase(InstanceCase):
    """An instance, the folders of sessions that write descriptions, and the publications that carry them."""

    def filed(self):
        """A canon with a folder: `Small.Sums` holds the modules `Small.Sums.Zero` and `Small.Sums.Two`.

        Published once per test process, by a change that carries no description, as the change of a
        session does that was launched before the index had descriptions."""
        def build():
            folder = self.candidate(
                modules={'Small/Sums/Zero.lean': module_text(theorem('sumZero', ': oddSum 0 = 0')),
                         'Small/Sums/Two.lean': module_text(theorem('sumTwo', ': oddSum 2 = 4'))},
                records={'Small/sumZero.md': record_text('The empty sum is zero.', weight='unit'),
                         'Small/sumTwo.md': record_text('The first two odd numbers sum to four.')})
            self.publish(folder)
        self.scenario('filed', build)

    def session_folder(self, sid, role, marker=True, task=None):
        """The folder of a session with its input.json; with `marker`, as a session has it that was launched
        with the guides that ask for descriptions (context.assemble)."""
        folder = self.instance / 'sessions' / sid
        (folder / 'output').mkdir(parents=True)
        inp = {'instance': str(self.instance), 'session': sid, 'role': role, 'pipeline': None, 'task': task or {},
               'user_inputs': []}
        if marker:
            inp['descriptions'] = True
        write_json(folder / 'input.json', inp)
        return folder

    def fill(self, folder, files, **manifest):
        """Write files into a candidate folder or a folder for the describe command; with `manifest`, a change.json."""
        for name, text in files.items():
            path = Path(folder) / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding='utf-8', newline='\n')
        if manifest:
            write_json(Path(folder) / 'change.json', {'title': 'A contribution', 'description': 'What it adds.',
                                                      'replace': [], 'questions': [], 'resolutions': [], **manifest})
        return Path(folder)

    def receipt(self, output, *results, work=None):
        """descriptions/tests.json as the command descent-test writes it, with the folder of the test it names
        as that command's work leaves it (search.submit, search.descent_work). A result is (kind, name,
        purpose, outcome): True for a test that passed, False for one that failed, 'unavailable' for a reader
        that was refused. The tests of the command itself, with a stand-in for the reader, are in test_search.py."""
        output = Path(output)
        rows = []
        for kind, name, purpose, outcome in results:
            text = canon_index.description_file(output, kind, name).read_text(encoding='utf-8')
            row = {'target': name, 'kind': kind, 'text_sha': canon_index.text_sha(text),
                   'level': canon_index.parent(name, 'Small'), 'purpose': purpose}
            row.update({'unavailable': 'usage_limit'} if outcome == 'unavailable' else
                       {'opened': [name] if outcome else ['Small.Root'], 'passed': bool(outcome)})
            rows.append(row)
        tests = {'reader': {'model': 'claude/sonnet', 'effort': 'low'}, 'revision': 0, 'results': rows}
        work = work or 't-' + uid('w')
        folder = self.instance / 'runner/search' / work
        folder.mkdir(parents=True, exist_ok=True)
        write_json(folder / 'request.json', {'kind': 'descent-test', 'key': work, 'caller': output.parent.name})
        write_json(folder / 'result.json', {'complete': True, 'text': '', 'failed': 0, 'tests': tests})
        write_json(output / 'descriptions/tests.json', {**tests, 'work': work})
        return work

    def prepare_command(self, session):
        """The exit code and the printed summary of `prepare`, by the command a session gives."""
        code, text = self.command_line('prepare', session, '--timeout', self.patience)
        return code, json.loads(text)

    def organizer(self, sid, files, marker=True, **manifest):
        """The session folder of an organizer whose output holds a change with the given files."""
        engine = Runner(self.instance, self.skill)
        batch = [cid for cid in engine.model['changes'] if cid not in engine.model['organized']]
        session = self.session_folder(sid, 'organizer', marker, {'batch': batch, 'batch_frozen': True})
        self.fill(session / 'output', files, title='Descriptions', description='What the folders hold.', **manifest)
        write_json(session / 'output/organization.json', {'batch': batch})
        return session

    def publish_organizer(self, session, engine=None):
        """Publish the output of an organizer as the runner does: the transport check, the queue, the publication.
        A change that has not been prepared is prepared first, by the command."""
        if not (session / 'output/prepared.json').exists():
            code, printed = self.prepare_command(session)
            self.assertEqual(code, 0, printed)
        engine = engine or Runner(self.instance, self.skill)
        sid, key = session.name, uid('j')
        self.assertEqual(check_session(session), [])
        engine.state['jobs'][key] = {'id': key, 'role': 'organizer', 'pipeline': None, 'status': 'running',
                                     'session': sid, 'retries': 0, 'not_before': 0,
                                     'task': read_json(session / 'input.json')['task']}
        engine.state['sessions'][sid] = session_record(sid, 'organizer', key, 'publishing', model='codex/test', effort='low')
        engine.state['publish_queue'].append({'session': sid, 'job': key, 'kind': 'organization'})
        engine.save()
        self.drain(engine)
        self.assertEqual(engine.state['jobs'][key]['status'], 'done', engine.state['jobs'][key].get('last_error'))
        return engine.state['jobs'][key]['record'], engine

    def exclude(self, output, sid, **assessed):
        """Have a review exclude the candidate that a peer's output folder holds, as the runner does it when
        the session of the review ends (Runner.finish): the runner and the job of the review. The candidate is
        frozen from the output, the review's assessment says `publish: false` with the keys given in `assessed`
        beside it, and it passes the transport check first."""
        engine = Runner(self.instance, self.skill)
        pid = engine.state['jobs'][engine.producer('explore')]['pipeline']
        producer = uid('s')
        engine.state['pipelines'][pid].update(producer=producer, peer=output.parent.name, review=sid, stage='review')
        engine.state['jobs'][pid + ':producer']['status'] = 'done'
        candidate = output.parent / 'candidate'
        shutil.copytree(output, candidate)
        task = {'kind': 'candidate', 'candidate': str(candidate), 'candidate_hashes': tree_hashes(candidate),
                'peer': str(output.parent), 'source': str(engine.session_dir(producer))}
        key = engine.enqueue('review', task, pid, pid + ':review')
        folder = engine.session_dir(sid)
        for name in ('output', 'work', 'inbox'):
            (folder / name).mkdir(parents=True)
        write_json(folder / 'input.json', {'instance': str(self.instance), 'session': sid, 'role': 'review',
                                           'pipeline': pid, 'task': task, 'user_inputs': []})
        for name in ('cli.stdout.jsonl', 'cli.stderr.log'):
            (folder / name).write_text('', encoding='utf-8')
        write_json(folder / 'output/assessment.json', {
            **self.verdicts(candidate), 'publish': False, 'reason': 'The canon holds this already.', **assessed})
        (folder / 'output/feedback.md').write_text('Checked.', encoding='utf-8')
        engine.state['sessions'][sid] = session_record(sid, 'review', key, started_at=1, exit_code=0)
        engine.state['jobs'][key].update(status='running', session=sid)
        engine.save()
        self.assertEqual(check_session(folder), [])
        engine.finish(sid, engine.state['sessions'][sid])
        self.assertEqual((engine.state['sessions'][sid]['status'], engine.state['sessions'][sid].get('rejected'),
                          engine.state['jobs'][key]['status'], engine.state['pipelines'][pid]['stage']),
                         ('integrated', True, 'done', 'done'), engine.state['jobs'][key].get('last_error'))
        return engine, engine.state['jobs'][key]

    def describe(self, files, reason='The descriptions of the canon as it stands.', *more):
        """The describe command of the operator on a folder with the given files, with further options in
        `more`: its exit code and what it printed."""
        source = self.fill(self.root / ('describe-' + uid('f')), files)
        return self.operator('describe', str(self.instance), '--folder', str(source), '--reason', reason, *more)

    def operator(self, *argv):
        """One command of the operator (runner.main): its exit code and what it printed."""
        with patch('builtins.print') as shown:
            code = main(list(argv))
        return code, json.loads(shown.call_args.args[0])

    def collect(self, engine=None):
        """A runner that has collected the requests of the operator and carried their publications to the end."""
        engine = engine or Runner(self.instance, self.skill)
        with patch.object(subprocess, 'Popen', POPEN):
            engine.ingest_inputs()
        self.drain(engine)
        return engine

    def summary(self):
        return canon_index.read_summary(self.instance)

    def events(self):
        return sorted((read_json(path) for path in (self.instance / 'knowledge/events').glob('*.json')),
                      key=lambda event: event['sequence'])


class ReadingTests(IndexCase):
    def test_every_reading_command_works_on_an_instance_that_has_no_description(self):
        canon = self.instance / 'canon'
        self.assertFalse((canon / 'descriptions.json').exists())
        self.assertFalse((canon / 'descriptions').exists())
        model = knowledge.replay(self.instance)
        self.assertEqual((model['modules'], model['module_since'], model['index_reports']),
                         (['Small.Defs', 'Small.Root'], {'Small.Defs': 0, 'Small.Root': 0}, []))
        reader = self.reader()
        for argv in (['frontier'], ['list'], ['view', 'Small.root'], ['log'], ['questions', '--resolved'],
                     ['question', 'q0'], ['index'], ['index', 'Small.Root'], ['index', '--due']):
            with self.subTest(command=argv):
                code, text = self.command_line(argv[0], reader, *argv[1:])
                self.assertEqual(code, 0, text)
        level = ('Index of the canon · revision 0 · library Small: 0 folders, 2 modules, 2 elements.\n\n'
                 'Folders (0)\n\n'
                 'Modules directly under Small (2)\n\n'
                 '- Small.Defs · 1 element — (no line yet)\n'
                 '- Small.Root · 1 element — (no line yet)\n\n'
                 '0 folders and 2 modules at this level.\n')
        self.assertEqual(self.command_line('index', reader), (0, level))
        # The operator gives the instance folder, and the name of the library is the top of the index.
        self.assertEqual(self.command_line('index', self.instance, 'Small'), (0, level))
        # The same text is the view knowledge/folders.md, which `init` rendered.
        self.assertEqual((self.instance / 'knowledge/folders.md').read_text(encoding='utf-8'), level)
        self.assertEqual(self.command_line('index', reader, 'Small.Root'), (0, (
            'Small.Root · module · 1 element\n'
            '(no line yet)\n\n'
            'Small.root · theorem · unit · no proof — The sum of the first n odd numbers equals n times n.\n'
            '1 element.\n')))
        self.assertEqual(self.command_line('index', reader, '--due'), (0, (
            'What the index of the canon lacks, and what has been reported about it · revision 0\n\n'
            'Modules without a line (2)\n\n'
            '- Small.Defs · 1 element\n'
            '- Small.Root · 1 element\n\n'
            'Folders without a description (0)\n\n'
            'Folders that received modules after their description was last written or confirmed (0)\n\n'
            'Descriptions published without a blind descent test (0)\n\n'
            'Reports that a description did not lead a session to an element, each listed until its description '
            'is written or confirmed against a revision of the canon that showed the report (0)\n\n'
            'Folders whose description ends in a Boundary paragraph (0)\n')))
        # Reading and rendering make no file of descriptions.
        Runner(self.instance, self.skill).refresh()
        self.assertFalse((canon / 'descriptions.json').exists())
        self.assertFalse((canon / 'descriptions').exists())

    def test_a_name_that_is_no_folder_and_no_module_is_an_error(self):
        reader = self.reader()
        code, text = self.command_line('index', reader, 'Small.Nowhere')
        self.assertEqual((code, json.loads(text)),
                         (1, {'error': 'no folder or module of the canon has the name Small.Nowhere'}))
        # An element is no module: the descent reaches it with `view`.
        self.assertEqual(self.command_line('index', reader, 'Small.root')[0], 1)
        code, text = self.command_line('index', reader, 'Small.Root', '--due')
        self.assertEqual((code, json.loads(text)['error']),
                         (1, 'index takes the name of a folder or a module, or --due, and not both'))

    def test_a_publication_without_descriptions_makes_no_file_of_them_and_its_modules_are_listed_as_due(self):
        self.filed()
        canon = self.instance / 'canon'
        self.assertFalse((canon / 'descriptions.json').exists())
        self.assertFalse((canon / 'descriptions').exists())
        model = knowledge.replay(self.instance)
        self.assertEqual(model['module_since'],
                         {'Small.Defs': 0, 'Small.Root': 0, 'Small.Sums.Two': 1, 'Small.Sums.Zero': 1})
        code, text = self.command_line('index', self.reader())
        self.assertEqual((code, text), (0, (
            'Index of the canon · revision 1 · library Small: 1 folder, 4 modules, 4 elements.\n\n'
            'Folders (1)\n\n'
            '- Small.Sums · 2 modules · 2 elements\n'
            '  (no description yet; open the folder to see what it holds)\n\n'
            'Modules directly under Small (2)\n\n'
            '- Small.Defs · 1 element — (no line yet)\n'
            '- Small.Root · 1 element — (no line yet)\n\n'
            '1 folder and 2 modules at this level.\n')))
        code, text = self.command_line('index', self.reader(), '--due')
        self.assertIn('Modules without a line (4)\n\n- Small.Defs · 1 element\n- Small.Root · 1 element\n'
                      '- Small.Sums.Two · 1 element\n- Small.Sums.Zero · 1 element\n', text)
        self.assertIn('Folders without a description (1)\n\n- Small.Sums · 2 modules · 2 elements\n', text)
        # The record of the publication has the keys it always had.
        applied = read_json(self.instance / 'knowledge' / self.events()[-1]['folder'] / 'applied.json')
        self.assertEqual(sorted(applied), ['added', 'records', 'replaced', 'retired'])


STEP = {'lean/Small/Step.lean': module_text(theorem('sumSucc', '(n : Nat) : oddSum (n + 1) = oddSum n + (2 * n + 1)')),
        'records/Small/sumSucc.md': record_text('Passing from n to n + 1 adds the odd number 2n + 1.', weight='unit')}
STEP_LINE = 'The passage from n terms to n + 1 terms of the sum of odd numbers, the step of every induction on it.\n'
PURPOSE = 'how the sum changes when one more odd number is added'


class PeerDescriptionTests(IndexCase):
    """What `prepare` asks of a peer for the modules it adds, and only of a session launched with the guides
    that ask for it."""

    def test_a_candidate_without_a_line_passes_for_a_session_without_the_marker_and_is_refused_with_it(self):
        # A session launched before the index had descriptions: its input.json has no `descriptions`, and its
        # candidate is prepared, checked and published as it always was.
        earlier = self.session_folder('searlier', 'peer', marker=False)
        self.fill(earlier / 'output', STEP, replace=[])
        code, printed = self.prepare_command(earlier)
        self.assertEqual((code, printed['ok'], printed['added'], printed['errors']), (0, True, ['Small.sumSucc'], []))
        self.assertEqual(sorted(printed), ['added', 'axioms', 'build', 'errors', 'ok', 'records', 'replaced'])
        receipt = read_json(earlier / 'output/prepared.json')
        self.assertNotIn('descriptions', receipt)
        self.assertEqual(check_session(earlier), [])
        # Its review compiles it and its publication applies it without asking for a line, also where the
        # review itself was launched with the guides that ask for descriptions.
        review = self.session_folder('sreview', 'review', task={'kind': 'candidate', 'candidate': str(earlier / 'output')})
        code, text = self.command_line('verify', review, '--timeout', self.patience)
        self.assertEqual((code, json.loads(text)['ok'], json.loads(text)['errors']), (0, True, []))
        self.publish(earlier / 'output')
        self.assertIn('Small.sumSucc', knowledge.replay(self.instance)['elements'])
        self.assertFalse((self.instance / 'canon/descriptions.json').exists())

        # The same candidate from a session launched with those guides.
        later = self.session_folder('slater', 'peer')
        self.fill(later / 'output', {name.replace('Step', 'Next'): text.replace('sumSucc', 'sumNext')
                                     for name, text in STEP.items()}, replace=[])
        (later / 'output/records/Small/sumSucc.md').rename(later / 'output/records/Small/sumNext.md')
        code, printed = self.prepare_command(later)
        self.assertEqual((code, printed['ok'], printed['build']), (1, False, None))
        self.assertEqual(printed['errors'], [
            'the module Small.Next has no line; write descriptions/modules/Small/Next.md, one paragraph that says '
            'what the module holds, and take the blind descent test on it'])
        refused = check_session(later)
        self.assertEqual(len(refused), 1)
        self.assertIn('prepare reported errors: the module Small.Next has no line', refused[0])

    def test_a_line_needs_a_blind_descent_test_on_its_present_text_that_did_not_fail(self):
        peer = self.session_folder('speer', 'peer')
        output = self.fill(peer / 'output', {**STEP, 'descriptions/modules/Small/Step.md': STEP_LINE}, replace=[])
        code, printed = self.prepare_command(peer)
        self.assertEqual(code, 1)
        self.assertEqual(printed['errors'], [
            'the line of the module Small.Step has taken the blind descent test on 0 different purposes with the '
            'text it has now and needs at least 1; give it a purpose in descriptions/purposes.json, each as '
            '{"target": "Small.Step", "purpose": "..."}, and run the canon command descent-test'])
        # A receipt that no test produced: written by hand, it names no test, or a test that is not there, or the
        # test of another session, or it holds other results than the test it names.
        passed = {'target': 'Small.Step', 'kind': 'module', 'text_sha': canon_index.text_sha(STEP_LINE),
                  'level': 'Small', 'purpose': PURPOSE, 'opened': ['Small.Step'], 'passed': True}
        refusal = ('descriptions/tests.json is not the receipt of a blind descent test of this session: {}. The canon '
                   'command descent-test takes the test and writes the file; run it, and then prepare again')
        write_json(output / 'descriptions/tests.json', {'reader': {}, 'revision': 0, 'results': [passed]})
        self.assertEqual(self.prepare_command(peer)[1]['errors'], [refusal.format('it names no test that was taken')])
        write_json(output / 'descriptions/tests.json', {'results': [passed], 'work': 't-none'})
        self.assertEqual(self.prepare_command(peer)[1]['errors'],
                         [refusal.format('the test it names, t-none, has no result in this instance')])
        write_json(output / 'descriptions/tests.json', {'results': [passed], 'work': '../search/t-none'})
        self.assertEqual(self.prepare_command(peer)[1]['errors'], [refusal.format('it names no test that was taken')])
        other = self.session_folder('sother', 'peer')
        self.fill(other / 'output', {'descriptions/modules/Small/Step.md': STEP_LINE})
        work = self.receipt(other / 'output', ('module', 'Small.Step', PURPOSE, True))
        write_json(output / 'descriptions/tests.json', read_json(other / 'output/descriptions/tests.json'))
        self.assertEqual(self.prepare_command(peer)[1]['errors'],
                         [refusal.format(f'the test it names, {work}, was not taken for this session')])
        work = self.receipt(output, ('module', 'Small.Step', PURPOSE, False))
        write_json(output / 'descriptions/tests.json', {'results': [passed], 'work': work})
        self.assertEqual(self.prepare_command(peer)[1]['errors'],
                         [refusal.format(f'its results are not those of the test it names, {work}')])
        # A test that failed: the reader opened something else.
        self.receipt(output, ('module', 'Small.Step', PURPOSE, False))
        code, printed = self.prepare_command(peer)
        self.assertEqual(code, 1)
        self.assertEqual(printed['errors'], [
            'the line of the module Small.Step did not pass the blind descent test for the purpose '
            f'"{PURPOSE}": the reader opened Small.Root. Rewrite the description so that it leads a reader with '
            'that purpose there, or the purpose if the module does not hold what it asks for, and run descent-test '
            'again'])
        # A test that passed, and the line rewritten after it: the receipt is for another text.
        self.receipt(output, ('module', 'Small.Step', PURPOSE, True))
        (output / 'descriptions/modules/Small/Step.md').write_text('Another line.\n', encoding='utf-8')
        self.assertIn('has taken the blind descent test on 0 different purposes with the text it has now',
                      self.prepare_command(peer)[1]['errors'][0])
        (output / 'descriptions/modules/Small/Step.md').write_text(STEP_LINE, encoding='utf-8', newline='\n')
        code, printed = self.prepare_command(peer)
        self.assertEqual((code, printed['ok'], printed['added']), (0, True, ['Small.sumSucc']), printed)
        # The receipt names the descriptions and the revision of the canon they were prepared against. The change
        # carries no description of a module the canon already has, so nothing is said of reports.
        self.assertEqual(read_json(output / 'prepared.json')['descriptions'],
                         {'modules': ['Small.Step'], 'folders': [], 'revision': 0})
        self.assertNotIn('open_reports', read_json(output / 'prepared.json'))
        self.assertEqual(sorted(printed), ['added', 'axioms', 'build', 'errors', 'ok', 'records', 'replaced'])
        self.assertEqual(check_session(peer), [])

        # Published, the line is in the canon and in its summary. Its revision is that of the canon it was
        # prepared against, 0, and not the sequence of its publication. The summary now says when each module
        # came: the module of this publication at 1, the modules the instance began with at 0.
        self.publish(output)
        self.assertEqual((self.instance / 'canon/descriptions/modules/Small/Step.md').read_text(encoding='utf-8'),
                         STEP_LINE)
        self.assertEqual(self.summary(), {'folders': {}, 'modules': {'Small.Step': {
            'text': STEP_LINE.rstrip('\n'), 'revision': 0, 'published': 1, 'tested': True}},
            'since': {'Small.Defs': 0, 'Small.Root': 0, 'Small.Step': 1}})
        code, text = self.command_line('index', self.reader(), 'Small.Step')
        self.assertEqual((code, text), (0, (
            'Small.Step · module · 1 element\n' + STEP_LINE + '\n'
            'Small.sumSucc · theorem · unit · no proof — Passing from n to n + 1 adds the odd number 2n + 1.\n'
            '1 element.\n')))
        self.assertIn('- Small.Step · 1 element — ' + STEP_LINE, self.command_line('index', self.reader())[1])
        self.assertIn('## Small.Step\n\n' + STEP_LINE + '\n- `Small.sumSucc`',
                      (self.instance / 'knowledge/index.md').read_text(encoding='utf-8'))
        self.assertIn('- Small.Step · 1 element — ' + STEP_LINE,
                      (self.instance / 'knowledge/folders.md').read_text(encoding='utf-8'))
        self.assertNotIn('Small.Step', self.command_line('index', self.reader(), '--due')[1])

    def test_a_line_whose_reader_was_unavailable_is_published_as_untested_and_listed_as_due(self):
        peer = self.session_folder('speer', 'peer')
        output = self.fill(peer / 'output', {**STEP, 'descriptions/modules/Small/Step.md': STEP_LINE}, replace=[])
        self.receipt(output, ('module', 'Small.Step', PURPOSE, 'unavailable'))
        self.assertEqual(self.prepare_command(peer)[0], 0)
        self.publish(output)
        self.assertEqual(self.summary()['modules']['Small.Step']['tested'], False)
        self.assertIn('Descriptions published without a blind descent test (1)\n\n- module Small.Step · revision 0\n',
                      self.command_line('index', self.reader(), '--due')[1])

    def interrupted(self, step):
        """The publication of a peer's change that carries a module line, ended inside the runner's method `step`
        and completed by a runner that starts afterwards: (the canon folder, the session's output)."""
        peer = self.session_folder('speer', 'peer')
        output = self.fill(peer / 'output', {**STEP, 'descriptions/modules/Small/Step.md': STEP_LINE}, replace=[])
        self.receipt(output, ('module', 'Small.Step', PURPOSE, True))
        self.assertEqual(self.prepare_command(peer)[0], 0)
        with patch.object(Runner, step, side_effect=RuntimeError('simulated end of the runner')), \
                self.assertRaisesRegex(RuntimeError, 'simulated end of the runner'):
            self.publish(output)
        canon = self.instance / 'canon'
        # The line is in the canon, and the index is still the one from before the publication.
        self.assertEqual((canon / 'descriptions/modules/Small/Step.md').read_text(encoding='utf-8'), STEP_LINE)
        self.assertNotIn('Small.Step', Canon(self.instance).load_index()['modules'])
        self.assertIsNotNone(read_json(self.instance / 'runner/state.json')['publication'])
        return canon, output

    def completed(self):
        """A runner that starts after the interruption carries the publication to its end, with the summary
        that an uninterrupted publication leaves."""
        recovered = Runner(self.instance, self.skill)
        self.drain(recovered)
        self.assertIsNone(recovered.state['publication'])
        self.assertEqual(self.summary(), {'folders': {}, 'modules': {'Small.Step': {
            'text': STEP_LINE.rstrip('\n'), 'revision': 0, 'published': 1, 'tested': True}},
            'since': {'Small.Defs': 0, 'Small.Root': 0, 'Small.Step': 1}})
        self.assertIn('Small.Step', Canon(self.instance).load_index()['modules'])
        event, = self.events()
        self.assertEqual(git(self.instance, 'log', '--format=%s').count('Publish ' + event['id']), 1)
        self.assertEqual(git(self.instance, 'status', '--porcelain', '--', 'knowledge', 'canon'), '')
        self.assertIn('- Small.Step · 1 element — ' + STEP_LINE, self.command_line('index', self.reader())[1])

    def test_a_publication_ended_between_the_description_files_and_the_summary_is_completed_by_the_next_runner(self):
        canon, _ = self.interrupted('write_descriptions')
        self.assertFalse((canon / 'descriptions.json').exists())
        self.completed()

    def test_a_publication_ended_between_the_summary_and_the_index_is_completed_with_the_same_summary(self):
        # The summary is written before the index. It says that the module came with this publication, and a
        # runner that starts now, whose model is the research before the publication, leaves that as it is.
        canon, _ = self.interrupted('install_canon')
        self.assertEqual(self.summary()['since'], {'Small.Defs': 0, 'Small.Root': 0, 'Small.Step': 1})
        self.completed()

    def test_a_peer_carries_the_lines_of_the_modules_it_adds_and_nothing_else(self):
        self.filed()
        peer = self.session_folder('speer', 'peer')
        output = self.fill(peer / 'output', {
            **STEP, 'descriptions/modules/Small/Step.md': STEP_LINE,
            'descriptions/modules/Small/Sums/Zero.md': ZERO_LINE,
            'descriptions/folders/Small/Sums.md': SUMS_TEXT,
            'descriptions/reports.json': json.dumps([
                {'description': 'Small.Nowhere', 'element': 'Small.nothing', 'purpose': 'a base case'}])}, replace=[])
        self.receipt(output, ('module', 'Small.Step', PURPOSE, True), ('module', 'Small.Sums.Zero', 'a base case', True),
                     *(('folder', 'Small.Sums', 'purpose %d' % number, True) for number in range(3)))
        code, printed = self.prepare_command(peer)
        self.assertEqual(code, 1)
        self.assertEqual(printed['errors'], [
            'descriptions/modules/Small/Sums/Zero.md is the line of a module this candidate does not add; a peer '
            "writes the line of each module it adds, and the lines of the other modules are the organizer's to write",
            "descriptions/folders/Small/Sums.md: the description of a folder is the organizer's to write; remove the file",
            'descriptions/reports.json names no folder or module of the canon: Small.Nowhere',
            'descriptions/reports.json names no element of the canon: Small.nothing'])

    def test_a_malformed_description_or_report_is_refused_when_the_candidate_is_read(self):
        peer = self.session_folder('speer', 'peer', marker=False)
        output = self.fill(peer / 'output', {**STEP, 'descriptions/modules/Small/Step.md': 'One.\n\nTwo.\n'}, replace=[])
        self.assertIn('descriptions/modules/Small/Step.md: a module line is one paragraph',
                      self.prepare_command(peer)[1]['errors'][0])
        (output / 'descriptions/modules/Small/Step.md').write_text(STEP_LINE, encoding='utf-8')
        report = {'description': 'Small.Defs', 'element': 'Small.root', 'purpose': 'the definition of the sum'}
        for written, said in (
                ('{not json', r'^descriptions/reports\.json is not JSON \('),
                (json.dumps({'description': 'Small.Defs'}), r'^descriptions/reports\.json is an array$'),
                (json.dumps([{'description': 'Small.Defs', 'element': 'Small.root'}]),
                 r'^an entry of descriptions/reports\.json has exactly "description", the name of a folder or module, '
                 r'"element", the name of an element, and "purpose", each as nonempty text$'),
                (json.dumps([{**report, 'purpose': ' '}]), r'^an entry of descriptions/reports\.json has exactly'),
                (json.dumps([{**report, 'session': 'speer'}]), r'^an entry of descriptions/reports\.json has exactly')):
            with self.subTest(written=written):
                self.fill(output, {'descriptions/reports.json': written})
                with self.assertRaisesRegex(CanonError, said):
                    load_change(output)
        # The file in its form is read, and its reports are given with the change.
        self.fill(output, {'descriptions/reports.json': json.dumps([report])})
        self.assertEqual(load_change(output)['index_reports'], [report])
        # change.json has the keys it had before the index had descriptions. A report written there is refused
        # as every key is that the manifest does not have, and the refusal names the file.
        self.fill(output, {}, replace=[], index_reports=[report])
        with self.assertRaises(CanonError) as refused:
            load_change(output)
        self.assertEqual(str(refused.exception), (
            'unknown key in change.json: index_reports. A report that a description did not lead to an element is '
            'written in the file descriptions/reports.json of the candidate, as an array of {"description", '
            '"element", "purpose"}, and in no key of change.json'))
        self.assertEqual(self.prepare_command(peer)[1]['errors'], [str(refused.exception)])
        self.fill(output, {}, replace=[], notes='x')
        with self.assertRaisesRegex(CanonError, r'^unknown key in change\.json: notes$'):
            load_change(output)
        # A candidate without the folder reads as it always did.
        change = load_change(self.candidate(understanding={'q0.md': 'What is understood.\n'}, prepare=False))
        self.assertEqual((change['module_lines'], change['folder_descriptions'], change['index_reports']), ([], [], []))


FOLDER_PURPOSES = ('a base case of the sum', 'the value of the sum at two terms', 'a numerical check of the closed form')


class OrganizerDescriptionTests(IndexCase):
    """An organizer writes the descriptions of folders and the lines that are missing, in a change of its own."""

    def described(self, sid='sorganizer', text=SUMS_TEXT, lines=None, outcome=True):
        """The session of an organizer whose change holds the description of Small.Sums and some lines, each tested."""
        lines = {'Small.Sums.Zero': ZERO_LINE} if lines is None else lines
        files = {'descriptions/folders/Small/Sums.md': text,
                 **{'descriptions/modules/' + name.replace('.', '/') + '.md': line for name, line in lines.items()}}
        session = self.organizer(sid, files)
        self.receipt(session / 'output', *(('folder', 'Small.Sums', purpose, outcome) for purpose in FOLDER_PURPOSES),
                     *(('module', name, 'what this module holds', outcome) for name in lines))
        return session

    def test_a_change_that_holds_descriptions_alone_is_published_without_a_build(self):
        self.filed()
        canon = self.instance / 'canon'
        lean, index = tree_identity(canon / 'lean'), (canon / 'index.json').read_bytes()
        session = self.described()
        code, printed = self.prepare_command(session)
        self.assertEqual((code, printed['ok'], printed['build'], printed['added']), (0, True, None, []), printed)
        self.assertEqual(read_json(session / 'output/prepared.json')['descriptions'],
                         {'modules': ['Small.Sums.Zero'], 'folders': ['Small.Sums'], 'revision': 1})
        # The change carries descriptions of a module and a folder that the canon has, so the result says which
        # reports are listed against them: none.
        self.assertEqual((printed['open_reports'], read_json(session / 'output/prepared.json')['open_reports']), ([], []))
        oid, engine = self.publish_organizer(session)
        event = self.events()[-1]
        self.assertEqual((event['id'], event['kind'], event['sequence']), (oid, 'organization', 2))
        # No Lean source changed, no index was made and nothing was staged for a build.
        self.assertEqual((tree_identity(canon / 'lean'), (canon / 'index.json').read_bytes()), (lean, index))
        # The descriptions were prepared against revision 1, and that is their revision. The map of when the
        # modules came is made with this publication, the first that leaves a description, from the research.
        self.assertEqual(self.summary(), {
            'modules': {'Small.Sums.Zero': {'text': ZERO_LINE.rstrip('\n'), 'revision': 1, 'published': 2, 'tested': True}},
            'folders': {'Small.Sums': {'text': SUMS_TEXT.rstrip('\n'), 'revision': 1, 'published': 2, 'tested': True,
                                       'boundary': None}},
            'since': SINCE_FILED})
        self.assertEqual(self.command_line('index', self.reader(), 'Small.Sums'), (0, (
            'Small.Sums · folder · 2 modules · 2 elements\n\n' + SUMS_TEXT + '\n'
            'Folders (0)\n\n'
            'Modules (2)\n\n'
            '- Small.Sums.Two · 1 element — (no line yet)\n'
            '- Small.Sums.Zero · 1 element — ' + ZERO_LINE + '\n'
            '0 folders and 2 modules at this level.\n')))
        level = self.command_line('index', self.reader())[1]
        self.assertIn('- Small.Sums · 2 modules · 2 elements\n'
                      '  Small cases of the sum of odd numbers: the value of the sum at particular numbers of terms.\n'
                      '  A session that wants a base case or a numerical check of the closed form finds it here.\n', level)
        self.assertEqual((self.instance / 'knowledge/folders.md').read_text(encoding='utf-8'), level)
        due = self.command_line('index', self.reader(), '--due')[1]
        self.assertIn('Modules without a line (3)', due)
        self.assertIn('Folders without a description (0)', due)
        # The research is as it was: the publication changed the sequence and nothing else that a session reads of it.
        self.assertEqual(engine.model['sequence'], 2)
        self.assertEqual(git(self.instance, 'log', '--format=%s').count('Publish ' + oid), 1)

    def test_descriptions_without_a_change_and_reports_in_an_organizers_change_are_refused_by_the_check(self):
        self.filed()
        session = self.described()
        (session / 'output/change.json').unlink()
        self.assertEqual(check_session(session), [
            'descriptions take effect only as part of a change; write change.json with "title" and "description" '
            'beside them and prepare the change'])
        session = self.organizer('sreporting', {
            'descriptions/modules/Small/Sums/Zero.md': ZERO_LINE,
            'descriptions/reports.json': json.dumps([
                {'description': 'Small.Sums', 'element': 'Small.sumZero', 'purpose': 'a base case'}])})
        self.receipt(session / 'output', ('module', 'Small.Sums.Zero', 'a base case', True))
        self.assertEqual(self.prepare_command(session)[0], 0)
        self.assertEqual(check_session(session), [
            'descriptions/reports.json belongs to the candidate of a peer, and a review reports under "index_reports" '
            'in its assessment. An organizer that finds a description which does not lead to an element rewrites that '
            'description in its own change; remove the file and prepare the change again'])

    def test_prepare_asks_an_organizer_for_three_tests_of_a_folder_and_for_the_line_of_each_module_it_creates(self):
        self.filed()
        session = self.organizer('sorganizer', {
            'descriptions/folders/Small/Sums.md': SUMS_TEXT, 'descriptions/folders/Small/Gone.md': SUMS_TEXT,
            'descriptions/modules/Small/Sums/Missing.md': ZERO_LINE,
            # A rearrangement that creates a module, and a module that the change adds as a peer's does: the
            # check of the descriptions reads the paths alone.
            'rewrite/lean/Small/Moved.lean': module_text(theorem('moved', ': oddSum 0 = 0')),
            'lean/Small/Fresh.lean': module_text(theorem('fresh', ': oddSum 1 = 1'))})
        self.receipt(session / 'output', ('folder', 'Small.Sums', FOLDER_PURPOSES[0], True),
                     ('folder', 'Small.Sums', FOLDER_PURPOSES[1], 'unavailable'))
        code, printed = self.prepare_command(session)
        self.assertEqual(code, 1)
        self.assertEqual(printed['errors'][:4], [
            'the module Small.Fresh has no line; write descriptions/modules/Small/Fresh.md, one paragraph that says '
            'what the module holds, and take the blind descent test on it',
            'the module Small.Moved has no line; write descriptions/modules/Small/Moved.md, one paragraph that says '
            'what the module holds, and take the blind descent test on it',
            'descriptions/modules/Small/Sums/Missing.md names no module of the canon as it is after this change',
            'descriptions/folders/Small/Gone.md names no folder of the canon as it is after this change'])
        needs = ('the description of the folder Small.Sums has taken the blind descent test on {} with the text it '
                 'has now and needs at least 3; give it 3 different purposes in descriptions/purposes.json, each as '
                 '{{"target": "Small.Sums", "purpose": "..."}}, and run the canon command descent-test')
        self.assertEqual(printed['errors'][-1], needs.format('2 different purposes'))
        # One purpose given three times asks the reader one thing, and counts as one.
        self.receipt(session / 'output', *[('folder', 'Small.Sums', FOLDER_PURPOSES[0], True)] * 3)
        self.assertEqual(self.prepare_command(session)[1]['errors'][-1], needs.format('1 different purpose'))

    def test_a_folder_falls_behind_when_a_module_comes_beneath_it_and_a_confirmed_description_is_current_again(self):
        self.filed()
        boundary = SUMS_TEXT + '\nBoundary: the case of two terms belongs with the worked examples.\n'
        self.publish_organizer(self.described(text=boundary))
        self.assertIn('Folders whose description ends in a Boundary paragraph (1)\n\n'
                      '- Small.Sums · 2 modules · 2 elements\n'
                      '  Boundary: the case of two terms belongs with the worked examples.\n',
                      self.command_line('index', self.reader(), '--due')[1])
        self.assertIn('  Boundary: the case of two terms belongs with the worked examples.\n',
                      self.command_line('index', self.reader())[1])
        # A peer adds a module beneath the folder, with its line.
        peer = self.session_folder('speer', 'peer')
        output = self.fill(peer / 'output', {
            'lean/Small/Sums/Four.lean': module_text(theorem('sumFour', ': oddSum 4 = 16')),
            'records/Small/sumFour.md': record_text('The first four odd numbers sum to sixteen.'),
            'descriptions/modules/Small/Sums/Four.md': 'The sum of the first four odd numbers.\n'}, replace=[])
        self.receipt(output, ('module', 'Small.Sums.Four', 'the sum at four terms', True))
        self.assertEqual(self.prepare_command(peer)[0], 0)
        self.publish(output)
        self.assertEqual(knowledge.replay(self.instance)['module_since']['Small.Sums.Four'], 3)
        self.assertIn('Folders that received modules after their description was last written or confirmed (1)\n\n'
                      '- Small.Sums · described at revision 1 · 1 module since\n'
                      '  - Small.Sums.Four · revision 3 · 1 element — The sum of the first four odd numbers.\n',
                      self.command_line('index', self.reader(), '--due')[1])
        # An organizer that has seen the new module confirms the description: its change carries the text as
        # the canon has it, and the line of a module as it stands. It prepared the change against the canon of
        # revision 3, which held the new module, so the folder is current again, with the same text.
        self.publish_organizer(self.described('ssecond', text=boundary))
        summary = self.summary()
        folder = summary['folders']['Small.Sums']
        self.assertEqual((folder['text'] + '\n', folder['revision'], folder['published']), (boundary, 3, 4))
        self.assertEqual((summary['modules']['Small.Sums.Zero']['revision'], summary['modules']['Small.Sums.Zero']['published']),
                         (3, 4))                                                 # confirmed with the same text
        # Not carried, so as it was: the peer prepared it at revision 2, after the first organizer's descriptions.
        self.assertEqual((summary['modules']['Small.Sums.Four']['revision'], summary['modules']['Small.Sums.Four']['published']),
                         (2, 3))
        self.assertEqual(summary['since'], {**SINCE_FILED, 'Small.Sums.Four': 3})
        due = self.command_line('index', self.reader(), '--due')[1]
        self.assertIn('Folders that received modules after their description was last written or confirmed (0)', due)
        self.assertIn('Folders whose description ends in a Boundary paragraph (1)', due)
        # A confirmed text left nothing in the history.
        history = self.instance / 'canon/history/descriptions'
        self.assertEqual(list(history.rglob('*.md')) if history.exists() else [], [])
        # A third organizer rewrites the description without the Boundary paragraph. The replaced text left
        # its difference in the history.
        self.publish_organizer(self.described('sthird', text=SUMS_TEXT))
        summary = self.summary()
        # Its revision is the one the canon had when it was prepared, after the publication of descriptions
        # alone at 4, which left the revision of the Lean library at 3.
        self.assertEqual((summary['folders']['Small.Sums']['revision'], summary['folders']['Small.Sums']['published'],
                          summary['folders']['Small.Sums']['boundary']), (4, 5, None))
        self.assertEqual(Canon(self.instance).load_index()['revision'], 3)
        due = self.command_line('index', self.reader(), '--due')[1]
        self.assertIn('Folders that received modules after their description was last written or confirmed (0)', due)
        self.assertIn('Folders whose description ends in a Boundary paragraph (0)', due)
        self.assertEqual(sorted(path.relative_to(history).as_posix() for path in history.rglob('*.md')),
                         ['folders/Small/Sums/000005.md'])
        self.assertIn('+Boundary: the case of two terms belongs with the worked examples.',
                      (history / 'folders/Small/Sums/000005.md').read_text(encoding='utf-8'))

    def test_the_description_of_a_module_that_is_gone_goes_to_the_history_when_the_summary_is_gathered(self):
        self.filed()
        self.publish_organizer(self.described(lines={'Small.Sums.Zero': ZERO_LINE, 'Small.Sums.Two': TWO_LINE}))
        canon = Canon(self.instance)
        index = canon.load_index()
        # The index of a publication that removed the module Small.Sums.Two, and with it nothing else.
        after = {**index, 'modules': {name: value for name, value in index['modules'].items() if name != 'Small.Sums.Two'}}
        known = knowledge.replay(self.instance)['module_since']
        gathered = canon_index.gather(self.instance, after, 9, {'modules': {}, 'folders': {}}, known)
        self.assertEqual(sorted(gathered['modules']), ['Small.Sums.Zero'])
        self.assertEqual(gathered['modules']['Small.Sums.Zero']['revision'], 1)
        # The module that left the index left the map of when the modules came.
        self.assertEqual(gathered['since'], {'Small.Defs': 0, 'Small.Root': 0, 'Small.Sums.Zero': 1})
        self.assertFalse((canon.root / 'descriptions/modules/Small/Sums/Two.md').exists())
        self.assertEqual((canon.history / 'descriptions/modules/Small/Sums/Two/000009-removed.md').read_text(encoding='utf-8'),
                         TWO_LINE)
        # Gathered again, as after an interruption, the summary is the same.
        self.assertEqual(canon_index.gather(self.instance, after, 9, {'modules': {}, 'folders': {}}, known), gathered)


    def test_a_module_moved_by_an_organizers_change_takes_its_line_to_the_history_and_is_new_to_its_folder(self):
        self.filed()
        self.publish_organizer(self.described(lines={'Small.Sums.Zero': ZERO_LINE, 'Small.Sums.Two': TWO_LINE}))
        # A peer adds the module Small.Low, directly under the library, with its line.
        low = module_text(theorem('low', ': oddSum 1 = 1', doc='The first odd number is one.'))
        low_line = 'The sum of the first odd number alone.\n'
        peer = self.session_folder('speer', 'peer')
        output = self.fill(peer / 'output', {
            'lean/Small/Low.lean': low, 'records/Small/low.md': record_text('The first odd number is one.'),
            'descriptions/modules/Small/Low.md': low_line}, replace=[])
        self.receipt(output, ('module', 'Small.Low', 'the sum at one term', True))
        self.assertEqual(self.prepare_command(peer)[0], 0)
        self.publish(output)
        self.assertEqual(self.summary()['since'], {**SINCE_FILED, 'Small.Low': 3})
        # An organizer moves it into the folder Small.Sums: the module Small.Low is deleted, and its text
        # stands in the new module Small.Sums.Low, whose line the change carries.
        moved_line = 'The sum of the first odd number alone, among the small cases.\n'
        session = self.organizer('smover', {'rewrite/lean/Small/Sums/Low.lean': low,
                                            'descriptions/modules/Small/Sums/Low.md': moved_line})
        organization = read_json(session / 'output/organization.json')
        write_json(session / 'output/organization.json', {**organization, 'merge_questions': [], 'delete': ['Small.Low']})
        self.receipt(session / 'output', ('module', 'Small.Sums.Low', 'the sum at one term', True))
        oid, engine = self.publish_organizer(session)
        self.assertEqual(self.events()[-1]['sequence'], 4)
        index = Canon(self.instance).load_index()
        self.assertEqual((index['entries']['Small.low']['module'], 'Small.Low' in index['modules']),
                         ('Small.Sums.Low', False))
        # The line of the module that is gone went to the history, as the text it was.
        canon = self.instance / 'canon'
        self.assertFalse((canon / 'descriptions/modules/Small/Low.md').exists())
        self.assertEqual((canon / 'history/descriptions/modules/Small/Low/000004-removed.md').read_text(encoding='utf-8'),
                         low_line)
        summary = self.summary()
        self.assertNotIn('Small.Low', summary['modules'])
        self.assertEqual(summary['modules']['Small.Sums.Low'],
                         {'text': moved_line.rstrip('\n'), 'revision': 3, 'published': 4, 'tested': True})
        # The module came to the index with this publication, although its element was added at revision 3.
        self.assertEqual(summary['since'], {**SINCE_FILED, 'Small.Sums.Low': 4})
        self.assertEqual(knowledge.replay(self.instance)['module_since']['Small.Sums.Low'], 3)
        # So the folder that received it, described at revision 1, is listed as behind.
        self.assertIn('Folders that received modules after their description was last written or confirmed (1)\n\n'
                      '- Small.Sums · described at revision 1 · 1 module since\n'
                      '  - Small.Sums.Low · revision 4 · 1 element — ' + moved_line,
                      self.command_line('index', self.reader(), '--due')[1])
        self.assertEqual(git(self.instance, 'status', '--porcelain', '--', 'knowledge', 'canon'), '')

    def mover(self):
        """A canon in which a peer has added the module Small.Low, directly under the library, at revision 2,
        and the session of an organizer whose change moves that module into the folder Small.Sums and carries
        the description of the folder: the organizer wrote the description with the module before it."""
        self.filed()
        low = module_text(theorem('low', ': oddSum 1 = 1', doc='The first odd number is one.'))
        peer = self.session_folder('speer', 'peer')
        output = self.fill(peer / 'output', {
            'lean/Small/Low.lean': low, 'records/Small/low.md': record_text('The first odd number is one.'),
            'descriptions/modules/Small/Low.md': 'The sum of the first odd number alone.\n'}, replace=[])
        self.receipt(output, ('module', 'Small.Low', 'the sum at one term', True))
        self.assertEqual(self.prepare_command(peer)[0], 0)
        self.publish(output)
        session = self.organizer('smover', {
            'rewrite/lean/Small/Sums/Low.lean': low,
            'descriptions/modules/Small/Sums/Low.md': 'The sum of the first odd number alone, among the small cases.\n',
            'descriptions/folders/Small/Sums.md': SUMS_TEXT})
        organization = read_json(session / 'output/organization.json')
        write_json(session / 'output/organization.json', {**organization, 'merge_questions': [], 'delete': ['Small.Low']})
        self.receipt(session / 'output', ('module', 'Small.Sums.Low', 'the sum at one term', True),
                     *(('folder', 'Small.Sums', purpose, True) for purpose in FOLDER_PURPOSES))
        code, printed = self.prepare_command(session)
        self.assertEqual((code, read_json(session / 'output/prepared.json')['revision']), (0, 2), printed)
        return session

    BEHIND = 'Folders that received modules after their description was last written or confirmed'

    def test_a_folder_is_not_behind_for_the_module_that_came_with_its_description(self):
        session = self.mover()
        self.publish_organizer(session)
        # The description was prepared against revision 2 and published at revision 3, and the module came
        # to the folder with that publication: later than the revision, and with the description.
        summary = self.summary()
        folder = summary['folders']['Small.Sums']
        self.assertEqual((folder['revision'], folder['published'], summary['since']['Small.Sums.Low']), (2, 3, 3))
        self.assertIn(f'{self.BEHIND} (0)\n', self.command_line('index', self.reader(), '--due')[1])

    def test_a_module_that_another_change_brought_between_the_writing_and_the_publication_still_counts(self):
        session = self.mover()
        # After the organizer prepared its change and before it is published, a peer's change brings another
        # module to the folder, at revision 3.
        peer = self.session_folder('sfour', 'peer')
        output = self.fill(peer / 'output', {
            'lean/Small/Sums/Four.lean': module_text(theorem('sumFour', ': oddSum 4 = 16')),
            'records/Small/sumFour.md': record_text('The first four odd numbers sum to sixteen.'),
            'descriptions/modules/Small/Sums/Four.md': 'The sum of the first four odd numbers.\n'}, replace=[])
        self.receipt(output, ('module', 'Small.Sums.Four', 'the sum at four terms', True))
        self.assertEqual(self.prepare_command(peer)[0], 0)
        self.publish(output)
        self.publish_organizer(session)
        summary = self.summary()
        folder = summary['folders']['Small.Sums']
        self.assertEqual((folder['revision'], folder['published']), (2, 4))
        self.assertEqual((summary['since']['Small.Sums.Four'], summary['since']['Small.Sums.Low']), (3, 4))
        # The module the organizer did not see is listed, and the one its own change brought is not.
        self.assertIn(f'{self.BEHIND} (1)\n\n'
                      '- Small.Sums · described at revision 2 · 1 module since\n'
                      '  - Small.Sums.Four · revision 3 · 1 element — The sum of the first four odd numbers.\n\n'
                      'Descriptions published without',
                      self.command_line('index', self.reader(), '--due')[1])

    def test_a_summary_that_does_not_say_which_publication_carried_a_description_lists_no_less(self):
        # A summary gathered before it kept `published`: the description counts as carried at its revision,
        # so a module that came after that revision is listed, as it was.
        self.filed()
        self.publish_organizer(self.described())
        path = self.instance / 'canon/descriptions.json'
        summary = read_json(path)
        for key in ('modules', 'folders'):
            for entry in summary[key].values():
                del entry['published']
        summary['folders']['Small.Sums']['revision'] = 0
        write_json(path, summary)
        self.assertIn(f'{self.BEHIND} (1)\n\n- Small.Sums · described at revision 0 · 2 modules since\n',
                      self.command_line('index', self.reader(), '--due')[1])
        # The next publication keeps such an entry with its revision as the publication that carried it.
        gathered = canon_index.gather(self.instance, Canon(self.instance).load_index(), 9,
                                      {'modules': {}, 'folders': {}}, {})
        self.assertEqual((gathered['folders']['Small.Sums']['revision'], gathered['folders']['Small.Sums']['published']),
                         (0, 0))

    def test_a_description_written_before_a_module_came_and_published_after_it_shows_its_folder_as_behind(self):
        self.filed()
        # An organizer prepares the description of Small.Sums against the canon of revision 1.
        session = self.described()
        self.assertEqual(self.prepare_command(session)[0], 0)
        self.assertEqual(read_json(session / 'output/prepared.json')['revision'], 1)
        # Before its output is published, a peer's change brings a module to that folder, at revision 2.
        peer = self.session_folder('speer', 'peer')
        output = self.fill(peer / 'output', {
            'lean/Small/Sums/Four.lean': module_text(theorem('sumFour', ': oddSum 4 = 16')),
            'records/Small/sumFour.md': record_text('The first four odd numbers sum to sixteen.'),
            'descriptions/modules/Small/Sums/Four.md': 'The sum of the first four odd numbers.\n'}, replace=[])
        self.receipt(output, ('module', 'Small.Sums.Four', 'the sum at four terms', True))
        self.assertEqual(self.prepare_command(peer)[0], 0)
        self.publish(output)
        # The organizer's output is published at revision 3, and its description is one of revision 1.
        self.publish_organizer(session)
        self.assertEqual(self.events()[-1]['sequence'], 3)
        self.assertEqual(self.summary()['folders']['Small.Sums']['revision'], 1)
        self.assertIn('Folders that received modules after their description was last written or confirmed (1)\n\n'
                      '- Small.Sums · described at revision 1 · 1 module since\n'
                      '  - Small.Sums.Four · revision 2 · 1 element — The sum of the first four odd numbers.\n',
                      self.command_line('index', self.reader(), '--due')[1])


DEFS_LINE = 'The definition of the sum of the first n odd numbers, by recursion on n.\n'
DESCRIBED = {'descriptions/folders/Small/Sums.md': SUMS_TEXT, 'descriptions/modules/Small/Sums/Zero.md': ZERO_LINE,
             'descriptions/modules/Small/Defs.md': DEFS_LINE}


class OperatorDescriptionTests(IndexCase):
    """The describe command: the route by which the descriptions of an existing canon are published at once."""

    def test_the_command_refuses_a_folder_it_cannot_publish_and_leaves_no_request(self):
        self.filed()
        for files, reason, said in (
                ({}, 'R.', 'holds no descriptions/ folder'),
                ({'descriptions/notes.md': 'A note.\n'}, 'R.', 'holds no description'),
                ({'descriptions/modules/Small/Nowhere.md': 'A line.\n'}, 'R.',
                 'no module or folder of the canon has the name: Small.Nowhere'),
                # The line of a module filed where the descriptions of folders are.
                ({'descriptions/folders/Small/Defs.md': DEFS_LINE}, 'R.',
                 'no module or folder of the canon has the name: Small.Defs'),
                ({'descriptions/modules/Small/Defs.md': 'One.\n\nTwo.\n'}, 'R.', 'a module line is one paragraph'),
                (DESCRIBED, '  ', 'describe needs a nonempty --reason')):
            with self.subTest(said=said):
                code, answer = self.describe(files, reason)
                self.assertEqual(code, 1)
                self.assertIn(said, answer['error'])
        self.assertEqual(list((self.instance / 'control/requests').iterdir()), [])

    def test_the_runner_publishes_the_descriptions_without_a_build_and_without_a_notice_to_sessions(self):
        self.filed()
        canon = self.instance / 'canon'
        engine = Runner(self.instance, self.skill)
        active = self.session(engine, 'sactive')
        lean, index = tree_identity(canon / 'lean'), (canon / 'index.json').read_bytes()
        configured = (self.instance / 'settings.json').read_bytes()
        code, answer = self.describe(DESCRIBED, 'The canon as it stands at the switch.')
        self.assertEqual((code, answer['modules'], answer['folders']), (0, 2, 1))
        request = read_json(Path(answer['request']))
        copy = Path(request['folder'])
        self.assertEqual((request['kind'], request['reason'], copy.parent, copy.name),
                         ('descriptions', 'The canon as it stands at the switch.', self.instance / 'control/requests',
                          Path(answer['request']).stem + '-descriptions'))
        self.assertEqual(sorted(path.relative_to(copy).as_posix() for path in copy.rglob('*.md')), sorted(DESCRIBED))
        # A description of a module that is gone when the turn of the request comes is left out and named.
        self.fill(copy, {'descriptions/modules/Small/Gone.md': 'A module removed since the command.\n'})
        engine = self.collect(Runner(self.instance, self.skill))
        self.assertIsNone(engine.state['last_error'])
        event = self.events()[-1]
        eid = event['id']
        self.assertEqual({key: value for key, value in event.items() if key != 'at'},
                         {'id': eid, 'kind': 'organization', 'sequence': 2, 'folder': 'descriptions/' + eid,
                          'source': 'operator'})
        published = self.instance / 'knowledge/descriptions' / eid
        # Without --revision the texts count as written against the canon as it was when the command was given.
        self.assertEqual((answer['revision'], request['revision']), (1, 1))
        self.assertEqual({key: value for key, value in read_json(published / 'descriptions.json').items() if key != 'at'},
                         {'source': 'operator', 'reason': 'The canon as it stands at the switch.', 'revision': 1,
                          'modules': ['Small.Defs', 'Small.Sums.Zero'], 'folders': ['Small.Sums'],
                          'skipped': ['Small.Gone']})
        # What a replay reads of the event, with the code of today and with the code a host loaded earlier.
        self.assertEqual(read_json(published / 'organization.json'), {'batch': [], 'merge_questions': []})
        self.assertEqual(read_json(published / 'applied.json'), {'added': [], 'replaced': [], 'records': [], 'retired': []})
        self.assertTrue(all(item['kind'] in KINDS_BEFORE for item in self.events()))
        self.assertEqual(self.summary(), {
            'modules': {'Small.Defs': {'text': DEFS_LINE.rstrip('\n'), 'revision': 1, 'published': 2, 'tested': True},
                        'Small.Sums.Zero': {'text': ZERO_LINE.rstrip('\n'), 'revision': 1, 'published': 2, 'tested': True}},
            'folders': {'Small.Sums': {'text': SUMS_TEXT.rstrip('\n'), 'revision': 1, 'published': 2, 'tested': True,
                                       'boundary': None}},
            'since': SINCE_FILED})
        self.assertFalse((canon / 'descriptions/modules/Small/Gone.md').exists())
        # No Lean source and no index changed, nothing was staged for a build, and no key came into the settings.
        self.assertEqual((tree_identity(canon / 'lean'), (canon / 'index.json').read_bytes()), (lean, index))
        self.assertEqual([path.name for path in (self.instance / 'runner').iterdir()
                          if path.name.startswith(('stage-', 'event-'))], [])
        self.assertEqual((self.instance / 'settings.json').read_bytes(), configured)
        # The research is the same but for the sequence, and the session at work was told of no change.
        model = knowledge.replay(self.instance)
        self.assertEqual((model['sequence'], model['organized'], sorted(model['changes'])),
                         (2, [], sorted(engine.model['changes'])))
        self.assertEqual(list((active / 'inbox').iterdir()), [])
        self.assertEqual(git(self.instance, 'log', '--format=%s').count('Publish ' + eid), 1)
        self.assertEqual(git(self.instance, 'status', '--porcelain', '--', 'knowledge', 'canon'), '')
        self.assertIsNone(engine.state['publication'])
        self.assertIn('- Small.Defs · 1 element — ' + DEFS_LINE, (self.instance / 'knowledge/folders.md').read_text(encoding='utf-8'))
        # A publication that changes the canon tells the session, as before.
        self.note('The sum grows by one odd number at a time.', engine=engine)
        self.assertEqual(len(list((active / 'inbox').iterdir())), 1)

    def test_a_restart_completes_the_same_publication_wherever_the_runner_ended(self):
        self.filed()
        self.describe({'descriptions/folders/Small/Sums.md': 'Text 0 of the folder.\n',
                       'descriptions/modules/Small/Sums/Zero.md': 'Text 0 of the module.\n'})
        self.collect()

        def failing(real, when):
            """A stand-in that raises where `when` says so and does what the real function does otherwise."""
            def call(*args, **kwargs):
                if when(*args, **kwargs):
                    raise RuntimeError('simulated end of the runner')
                return real(*args, **kwargs)
            return call

        import runner as runner_module
        puts = []
        steps = {
            # while the files of the event are staged
            'stage': patch('runner.rename_directory', side_effect=RuntimeError('simulated end of the runner')),
            # with the folder of the event in place and its event not written
            'event': patch('runner.write_json', side_effect=failing(
                runner_module.write_json, lambda path, value: Path(path).parent.name == 'events')),
            # between the first description and the second
            'put': patch('canon_index.put', side_effect=failing(
                canon_index.put, lambda *args: puts.append(args) or len(puts) % 2 == 0)),
            # with every description in the canon and the summary not written
            'summary': patch.object(Runner, 'write_descriptions', side_effect=RuntimeError('simulated end of the runner')),
            # with the canon in place and the commit not made
            'commit': patch('runner.git', side_effect=failing(runner_module.git, lambda instance, *args: args[0] == 'commit')),
        }
        history = self.instance / 'canon/history/descriptions'
        for number, (step, interruption) in enumerate(steps.items(), 1):
            with self.subTest(step=step):
                sequence = number + 2
                texts = {'folder': f'Text {number} of the folder.\n', 'module': f'Text {number} of the module.\n'}
                self.describe({'descriptions/folders/Small/Sums.md': texts['folder'],
                               'descriptions/modules/Small/Sums/Zero.md': texts['module']})
                first = Runner(self.instance, self.skill)
                with interruption, self.assertRaisesRegex(RuntimeError, 'simulated end of the runner'):
                    first.ingest_inputs()
                prepared = read_json(self.instance / 'runner/state.json')['publication']
                self.assertEqual(prepared['event']['sequence'], sequence)
                recovered = Runner(self.instance, self.skill)
                recovered.collect()
                self.assertIsNone(recovered.state['publication'])
                eid = prepared['event']['id']
                self.assertEqual([event['id'] for event in self.events()][-1], eid)
                self.assertEqual(len(self.events()), sequence)
                self.assertEqual(git(self.instance, 'log', '--format=%s').count('Publish ' + eid), 1)
                # The revision of a description is that of the canon when the command was given, one before
                # the sequence of its publication; the history names the publication.
                summary = self.summary()
                self.assertEqual(summary['folders']['Small.Sums'], {
                    'text': texts['folder'].rstrip('\n'), 'revision': sequence - 1, 'published': sequence, 'tested': True,
                    'boundary': None})
                self.assertEqual(summary['modules']['Small.Sums.Zero'],
                                 {'text': texts['module'].rstrip('\n'), 'revision': sequence - 1, 'published': sequence,
                                  'tested': True})
                self.assertEqual(summary['since'], SINCE_FILED)
                # Each replaced text left its difference once, against the text that took its place.
                for kind, place in (('folder', 'folders/Small/Sums'), ('module', 'modules/Small/Sums/Zero')):
                    left = (history / place / f'{sequence:06d}.md').read_text(encoding='utf-8')
                    self.assertIn(f'-Text {number} of the {kind}.\n+Text {number - 1} of the {kind}.', left)
                self.assertEqual([path.name for path in (self.instance / 'runner').iterdir()
                                  if path.name.startswith(('stage-', 'event-'))], [])
        self.assertEqual(len(list(history.rglob('*.md'))), 2 * len(steps))

    def test_the_operator_names_the_revision_the_descriptions_were_written_against(self):
        self.filed()
        text = {'descriptions/folders/Small/Sums.md': SUMS_TEXT}
        for given, said in (('5', 'from 0 to 1, the revision the canon has now; got 5'),
                            ('-1', 'from 0 to 1, the revision the canon has now; got -1')):
            code, answer = self.describe(text, 'R.', '--revision', given)
            self.assertEqual(code, 1)
            self.assertEqual(answer['error'], '--revision takes the revision of the canon the descriptions were '
                                              'written against, ' + said)
        self.assertEqual(list((self.instance / 'control/requests').iterdir()), [])
        # Written against the canon of revision 0, which did not have the two modules of the folder.
        code, answer = self.describe(text, 'Written from the canon as it began.', '--revision', '0')
        self.assertEqual((code, answer['revision']), (0, 0))
        self.collect()
        self.assertEqual(self.summary()['folders']['Small.Sums']['revision'], 0)
        self.assertEqual(read_json(self.instance / 'knowledge' / self.events()[-1]['folder'] / 'descriptions.json')['revision'], 0)
        self.assertIn('Folders that received modules after their description was last written or confirmed (1)\n\n'
                      '- Small.Sums · described at revision 0 · 2 modules since\n'
                      '  - Small.Sums.Two · revision 1 · 1 element — (no line yet)\n'
                      '  - Small.Sums.Zero · revision 1 · 1 element — (no line yet)\n',
                      self.command_line('index', self.reader(), '--due')[1])
        # The history of a text it replaces names the publication, whatever revision the text was written against.
        self.describe({'descriptions/folders/Small/Sums.md': 'Another text.\n'}, 'R.', '--revision', '1')
        self.collect()
        self.assertEqual(self.summary()['folders']['Small.Sums']['revision'], 1)
        self.assertTrue((self.instance / 'canon/history/descriptions/folders/Small/Sums/000003.md').is_file())
        # A request that does not say the revision, as the command wrote it before it recorded one, is refused.
        code, answer = self.describe(text)
        request = Path(answer['request'])
        write_json(request, {key: value for key, value in read_json(request).items() if key != 'revision'})
        engine = self.collect()
        self.assertIn(f'descriptions request {request.name} refused: the request does not say against which revision',
                      engine.state['last_error']['error'])
        self.assertEqual(len(self.events()), 3)

    def withdraw(self):
        code, answer = self.operator('describe', str(self.instance), '--withdraw')
        self.assertEqual((code, answer.pop('instance')), (0, str(self.instance)), answer)
        return answer

    def assert_nothing_left(self):
        """The state holds nothing of a publication of descriptions that is not done, and a second call does nothing."""
        state = read_json(self.instance / 'runner/state.json')
        self.assertTrue(state['publication'] is None or not state['publication'].get('descriptions'))
        self.assertEqual([item for item in state['publish_queue'] if item['kind'] == 'descriptions'], [])
        requests = [path.name for path in (self.instance / 'control/requests').glob('*.json')]
        self.assertEqual(sorted(set(requests) - set(state['seen_requests'])), [])
        self.assertEqual(self.withdraw(), {'completed': None, 'removed_from_queue': [], 'marked_collected': []})

    def test_withdraw_marks_a_request_that_was_not_collected_and_it_is_not_published(self):
        self.filed()
        request = Path(self.describe(DESCRIBED)[1]['request'])
        self.assertEqual(self.withdraw(), {'completed': None, 'removed_from_queue': [], 'marked_collected': [request.name]})
        self.assert_nothing_left()
        self.collect()
        self.assertEqual(len(self.events()), 1)
        self.assertFalse((self.instance / 'canon/descriptions.json').exists())

    def test_withdraw_takes_a_request_out_of_the_publication_queue(self):
        self.filed()
        request = Path(self.describe(DESCRIBED)[1]['request'])
        # Collected, and its turn has not come: another publication is under way.
        with patch.object(Runner, 'publish'):
            Runner(self.instance, self.skill).ingest_inputs()
        queued = read_json(self.instance / 'runner/state.json')['publish_queue']
        self.assertEqual([(item['kind'], item['request']) for item in queued], [('descriptions', request.name)])
        self.assertEqual(self.withdraw(), {'completed': None, 'removed_from_queue': [request.name], 'marked_collected': []})
        self.assert_nothing_left()
        self.collect()
        self.assertEqual(len(self.events()), 1)

    def test_withdraw_completes_a_publication_of_descriptions_that_is_under_way_and_starts_no_other(self):
        self.filed()
        self.describe(DESCRIBED)
        first = Runner(self.instance, self.skill)
        with patch('canon_index.put', side_effect=RuntimeError('simulated end of the runner')), \
                self.assertRaisesRegex(RuntimeError, 'simulated end of the runner'):
            first.ingest_inputs()
        before = read_json(self.instance / 'runner/state.json')
        under_way = before['publication']
        self.assertEqual((under_way['event']['sequence'], bool(under_way.get('installed'))), (2, False))
        # A second request, which no runner has collected.
        waiting = Path(self.describe({'descriptions/modules/Small/Sums/Two.md': TWO_LINE})[1]['request'])
        # While a runner is alive the command refuses, and it is given alone.
        with InstanceLock(self.instance / 'runner/lock'):
            code, answer = self.operator('describe', str(self.instance), '--withdraw')
        self.assertEqual((code, answer['error']), (1, 'the runner of this instance is alive; describe --withdraw is for '
                                                      'an instance whose runner has ended'))
        code, answer = self.operator('describe', str(self.instance), '--withdraw', '--reason', 'R.')
        self.assertEqual((code, answer['error']),
                         (1, 'describe --withdraw is given alone, without --folder, --reason and --revision'))
        code, answer = self.operator('describe', str(self.instance), '--reason', 'R.')
        self.assertEqual((code, answer['error']),
                         (1, 'describe needs --folder and --reason; describe --withdraw is given alone'))
        done = self.withdraw()
        # The publication under way was completed, and nothing else was begun: no session and no job came into
        # the state. The request that had not been collected was not published.
        after = read_json(self.instance / 'runner/state.json')
        self.assertEqual((sorted(after['sessions']), sorted(after['jobs'])), (sorted(before['sessions']), sorted(before['jobs'])))
        self.assertEqual(done, {'completed': under_way['event']['id'], 'removed_from_queue': [],
                                'marked_collected': [waiting.name]})
        self.assertEqual([event['id'] for event in self.events()][1:], [under_way['event']['id']])
        self.assertEqual(sorted(self.summary()['modules']), ['Small.Defs', 'Small.Sums.Zero'])
        self.assertEqual(git(self.instance, 'log', '--format=%s').count('Publish ' + under_way['event']['id']), 1)
        self.assertEqual(git(self.instance, 'status', '--porcelain', '--', 'knowledge', 'canon'), '')
        self.assert_nothing_left()
        # The runner that starts afterwards finds nothing to publish.
        self.collect()
        self.assertEqual(len(self.events()), 2)

    def test_a_request_whose_copy_is_damaged_is_refused_and_the_runner_goes_on(self):
        self.filed()
        code, answer = self.describe(DESCRIBED)
        copy = Path(read_json(Path(answer['request']))['folder'])
        (copy / 'descriptions/modules/Small/Defs.md').write_text('# A heading\n', encoding='utf-8')
        engine = self.collect()
        self.assertIn(f"descriptions request {Path(answer['request']).name} refused: descriptions/modules/Small/Defs.md: "
                      'a line begins with "#"', engine.state['last_error']['error'])
        self.assertEqual((len(self.events()), engine.state['publish_queue'], engine.state['publication']), (1, [], None))
        self.assertFalse((self.instance / 'canon/descriptions').exists())
        # The next request is published.
        self.describe(DESCRIBED)
        self.collect(engine)
        self.assertEqual(sorted(self.summary()['modules']), ['Small.Defs', 'Small.Sums.Zero'])


MINE = {'description': 'Small.Sums', 'element': 'Small.sumZero', 'purpose': 'a base case of the sum'}
THEIRS = {'description': 'Small.Root', 'element': 'Small.root', 'purpose': 'the closed form of the sum'}
ROOT_LINE = 'The statement the research is about: the closed form of the sum of the first n odd numbers.\n'


class ReportTests(IndexCase):
    TITLE = ('Reports that a description did not lead a session to an element, each listed until its description is '
             'written or confirmed against a revision of the canon that showed the report')

    # The session of an organizer whose change carries the description of Small.Sums and the line of a module.
    described = OrganizerDescriptionTests.described

    @staticmethod
    def listed(origin, by, report, needs, has=None):
        """One report as list 5 of `index --due` prints it: where it came from, with the revision of the canon
        then, its purpose, and from which revision a description answers it, with the revision the description
        has now (None where there is none)."""
        return (f"- {origin} · from the {by} · description {report['description']} · element {report['element']}\n"
                f"  purpose: {report['purpose']}\n"
                f"  listed until the description is written or confirmed against revision {needs} or later; "
                + ('there is none yet' if has is None else f'it is of revision {has}') + '\n')

    def reporting(self, sid='speer', reports=(MINE,)):
        """The output of a peer that touches no Lean, prepared and checked: an understanding of q0 and, with
        `reports`, the file descriptions/reports.json that holds them."""
        peer = self.session_folder(sid, 'peer')
        files = {'questions/q0.md': f'The sum grows by one odd number at a time, as {sid} found.\n'}
        if reports:
            files['descriptions/reports.json'] = json.dumps(list(reports))
        output = self.fill(peer / 'output', files, replace=[])
        self.assertEqual(self.prepare_command(peer)[0], 0)
        self.assertEqual(check_session(peer), [])
        return output

    def due(self):
        return self.command_line('index', self.reader(), '--due')[1]

    def test_what_the_peer_and_review_report_of_the_index_is_listed_until_the_description_is_written_again(self):
        from check import Invalid, assessment_check
        self.filed()
        mine, theirs = MINE, THEIRS
        output = self.reporting()
        # The manifest has the keys it had before the index had descriptions.
        self.assertEqual(sorted(read_json(output / 'change.json')), ['description', 'questions', 'replace', 'resolutions', 'title'])
        assessment = {**self.verdicts(output), 'index_reports': [theirs]}
        # The check of the assessment reads the form of the reports and whether what they name exists.
        review = self.root / 'review-output'
        review.mkdir()
        (review / 'feedback.md').write_text('Checked.', encoding='utf-8')
        model = knowledge.replay(self.instance)
        for reports, said in (('Small.Root', 'is an array'), ([{'description': 'Small.Root'}], 'has exactly'),
                              ([{**theirs, 'description': 'Small.Nowhere'}], 'names no folder or module of the canon'),
                              ([{**theirs, 'element': 'Small.nothing'}], 'names an unknown element')):
            with self.subTest(reports=reports), self.assertRaisesRegex(Invalid, said):
                assessment_check({**assessment, 'index_reports': reports}, review, output, model, self.instance, 'sreview')
        cid, engine = self.publish(output, assessment, role='explore', question='q0')
        # The peer's reports stand in the folder of the published change, in a file of their own, and the
        # manifest published there has no key for them.
        published = self.instance / 'knowledge/changes' / cid
        self.assertEqual(read_json(published / 'index_reports.json'), [mine])
        self.assertNotIn('index_reports', read_json(published / 'change.json'))
        self.assertEqual(knowledge.replay(self.instance)['index_reports'],
                         [{'change': cid, 'by': 'peer', 'sequence': 2, **mine},
                          {'change': cid, 'by': 'review', 'sequence': 2, **theirs}])
        origin = f'published change {cid} · revision 2'
        both = (f'{self.TITLE} (2)\n\n' + self.listed(origin, 'peer', mine, 2) + self.listed(origin, 'review', theirs, 2)
                + '\nFolders whose description')
        self.assertIn(both, self.due())
        # An organizer whose batch holds the change and that leaves the descriptions as they are answers for
        # the change and not for the reports: they stay.
        self.organize(engine=engine)
        self.assertIn(cid, knowledge.replay(self.instance)['organized'])
        self.assertIn(both, self.due())
        # A description written for another folder or module leaves them as well.
        self.describe({'descriptions/modules/Small/Defs.md': DEFS_LINE})
        self.collect()
        self.assertIn(both, self.due())
        # The operator publishes a description of the folder that was written against the canon of revision 1,
        # before the report existed. It is published after the report, and the report stays.
        self.describe({'descriptions/folders/Small/Sums.md': SUMS_TEXT}, 'Written from the canon of revision 1.',
                      '--revision', '1')
        self.collect()
        folder = self.summary()['folders']['Small.Sums']
        self.assertEqual((folder['revision'], folder['published']), (1, 5))
        self.assertIn(f'{self.TITLE} (2)\n\n' + self.listed(origin, 'peer', mine, 2, 1)
                      + self.listed(origin, 'review', theirs, 2), self.due())
        # The description is confirmed against the canon as it is now, which showed the report: that report
        # leaves the list, and the other stays.
        self.describe({'descriptions/folders/Small/Sums.md': SUMS_TEXT})
        self.collect()
        folder = self.summary()['folders']['Small.Sums']
        self.assertEqual((folder['revision'], folder['published']), (5, 6))
        self.assertIn(f'{self.TITLE} (1)\n\n' + self.listed(origin, 'review', theirs, 2) + '\nFolders whose description',
                      self.due())
        self.describe({'descriptions/modules/Small/Root.md': ROOT_LINE})
        self.collect()
        self.assertIn(f'{self.TITLE} (0)\n', self.due())

    def test_a_report_published_after_a_description_was_prepared_stays_until_one_is_prepared_that_could_read_it(self):
        self.filed()
        # An organizer prepares the description of Small.Sums against the canon of revision 1. No report is
        # listed against what its change carries, and `prepare` says so.
        first = self.described('sfirst')
        code, printed = self.prepare_command(first)
        self.assertEqual((code, printed['open_reports']), (0, []), printed)
        # Before its output is published, a change is published with a report against that description.
        cid, _ = self.publish(self.reporting(), role='explore', question='q0')
        self.publish_organizer(first)
        folder = self.summary()['folders']['Small.Sums']
        self.assertEqual((folder['revision'], folder['published']), (1, 3))
        # The description was published after the report and written before it: the report stays.
        origin = f'published change {cid} · revision 2'
        self.assertIn(f'{self.TITLE} (1)\n\n' + self.listed(origin, 'peer', MINE, 2, 1), self.due())
        # A second organizer prepares the description now. The canon shows the report, and `prepare` names
        # it with the descriptions the change carries, in the result it prints and in the receipt.
        second = self.described('ssecond')
        code, printed = self.prepare_command(second)
        named = [{**MINE, 'from': origin + ' · from the peer', 'answered_at_this_revision': True}]
        self.assertEqual((code, printed['open_reports']), (0, named), printed)
        receipt = read_json(second / 'output/prepared.json')
        self.assertEqual((receipt['open_reports'], receipt['descriptions']['revision']), (named, 3))
        # Published, the description is one of a revision that held the report, and the report leaves.
        self.publish_organizer(second)
        self.assertEqual(self.summary()['folders']['Small.Sums']['revision'], 3)
        self.assertIn(f'{self.TITLE} (0)\n', self.due())

    def test_a_report_against_a_name_that_is_a_module_and_a_folder_is_answered_by_both_descriptions_only(self):
        self.filed()
        # An organizer whose change carries the description of the folder Small.Sums and nothing for a module
        # of that name. Its session is there before the publications below, so its batch is the change of `filed`.
        folder_only = self.described('sfolder')
        # The canon receives a module whose name is that of the folder, and then a change is published with a
        # report against the name.
        self.publish(self.candidate(modules={'Small/Sums.lean': module_text(theorem('sumOne', ': oddSum 1 = 1'))},
                                    records={'Small/sumOne.md': record_text('The first odd number is one.')}))
        model = knowledge.replay(self.instance)
        self.assertIn('Small.Sums', model['modules'])
        self.assertIn('Small.Sums', canon_index.folders_of(model['modules']))
        cid, _ = self.publish(self.reporting(), role='explore', question='q0')
        origin = f'published change {cid} · revision 3'
        listed = f'{self.TITLE} (1)\n\n' + self.listed(origin, 'peer', MINE, 3) + '\nFolders whose description'
        self.assertIn(listed, self.due())
        # The change that carries the folder's description alone is prepared at a revision that holds the
        # report. `prepare` names the report and says that this preparation does not answer it: the line
        # of the module of that name is neither carried nor in the canon.
        named = {**MINE, 'from': origin + ' · from the peer'}
        code, printed = self.prepare_command(folder_only)
        self.assertEqual((code, printed['open_reports']), (0, [{**named, 'answered_at_this_revision': False}]), printed)
        self.publish_organizer(folder_only)
        self.assertEqual(self.summary()['folders']['Small.Sums']['revision'], 3)
        self.assertNotIn('Small.Sums', self.summary()['modules'])
        self.assertIn(listed, self.due())
        # A change that carries both descriptions answers the report, and published, it takes the report off.
        line = 'The value of the sum of odd numbers at one term, in the module that has the name of the folder.\n'
        both = self.described('sboth', lines={'Small.Sums': line})
        code, printed = self.prepare_command(both)
        self.assertEqual((code, printed['open_reports']), (0, [{**named, 'answered_at_this_revision': True}]), printed)
        self.publish_organizer(both)
        summary = self.summary()
        self.assertEqual((summary['folders']['Small.Sums']['revision'], summary['modules']['Small.Sums']['revision']), (4, 4))
        self.assertIn(f'{self.TITLE} (0)\n', self.due())

    # The module that the tests below publish under the name of the folder Small.Sums.
    ONE = module_text(theorem('sumOne', ': oddSum 1 = 1'))

    def named_twice(self):
        """Make Small.Sums a module as well as a folder, and publish a change with a report against that name,
        at revision 3: where the report came from, as the list says it."""
        self.publish(self.candidate(modules={'Small/Sums.lean': self.ONE},
                                    records={'Small/sumOne.md': record_text('The first odd number is one.')}))
        cid, _ = self.publish(self.reporting(), role='explore', question='q0')
        return f'published change {cid} · revision 3'

    def test_one_description_answers_a_report_when_the_other_of_the_name_already_stands_at_a_revision_that_held_it(self):
        self.filed()
        folder_only = self.described('sfolder')
        origin = self.named_twice()
        # The folder's description is published at a revision that held the report, and the module of that
        # name has no line: the report stays.
        self.publish_organizer(folder_only)
        self.assertEqual(self.summary()['folders']['Small.Sums']['revision'], 3)
        self.assertIn(f'{self.TITLE} (1)\n\n' + self.listed(origin, 'peer', MINE, 3) + '\nFolders whose description',
                      self.due())
        # A change that carries the line of the module alone answers the report: the description of the
        # folder stands in the canon at a revision that reaches it.
        session = self.organizer('sline', {'descriptions/modules/Small/Sums.md':
                                           'The value of the sum of odd numbers at one term.\n'})
        self.receipt(session / 'output', ('module', 'Small.Sums', 'the sum at one term', True))
        code, printed = self.prepare_command(session)
        self.assertEqual((code, printed['open_reports']), (0, [
            {**MINE, 'from': origin + ' · from the peer', 'answered_at_this_revision': True}]), printed)
        self.publish_organizer(session)
        summary = self.summary()
        self.assertEqual((summary['folders']['Small.Sums']['revision'], summary['modules']['Small.Sums']['revision']), (3, 4))
        self.assertIn(f'{self.TITLE} (0)\n', self.due())

    def test_a_change_that_makes_a_module_a_folder_as_well_does_not_answer_a_report_with_the_line_alone(self):
        self.filed()
        cid, _ = self.publish(self.reporting(reports=(THEIRS,)), role='explore', question='q0')
        origin = f'published change {cid} · revision 2'
        named = {**THEIRS, 'from': origin + ' · from the peer'}
        listed = f'{self.TITLE} (1)\n\n' + self.listed(origin, 'peer', THEIRS, 2) + '\nFolders whose description'
        self.assertIn(listed, self.due())
        # Small.Root is a module with nothing beneath it. A change that carries its line and leaves the
        # modules as they are answers the report.
        session = self.organizer('sline', {'descriptions/modules/Small/Root.md': ROOT_LINE})
        self.receipt(session / 'output', ('module', 'Small.Root', 'the closed form of the sum', True))
        code, printed = self.prepare_command(session)
        self.assertEqual((code, printed['open_reports']), (0, [{**named, 'answered_at_this_revision': True}]), printed)
        # A change that carries the same line and moves the module Small.Sums.Two beneath Small.Root makes
        # Small.Root a folder as well, and carries no description of that folder: it does not answer the report.
        session = self.organizer('smover', {
            'rewrite/lean/Small/Root/Two.lean': module_text(theorem('sumTwo', ': oddSum 2 = 4')),
            'descriptions/modules/Small/Root/Two.md': TWO_LINE, 'descriptions/modules/Small/Root.md': ROOT_LINE})
        organization = read_json(session / 'output/organization.json')
        write_json(session / 'output/organization.json', {**organization, 'merge_questions': [], 'delete': ['Small.Sums.Two']})
        self.receipt(session / 'output', ('module', 'Small.Root.Two', 'the sum at two terms', True),
                     ('module', 'Small.Root', 'the closed form of the sum', True))
        code, printed = self.prepare_command(session)
        self.assertEqual(printed['open_reports'], [{**named, 'answered_at_this_revision': False}], printed)
        self.assertEqual(code, 0, printed)
        # Published, the line is of a revision that held the report, and the report stays: the folder
        # Small.Root has no description.
        self.publish_organizer(session)
        modules = knowledge.replay(self.instance)['modules']
        self.assertTrue('Small.Root' in modules and 'Small.Root' in canon_index.folders_of(modules), modules)
        summary = self.summary()
        self.assertEqual((summary['modules']['Small.Root']['revision'], 'Small.Root' in summary['folders']), (2, False))
        self.assertIn(listed, self.due())

    def test_a_change_that_deletes_the_module_of_a_name_answers_a_report_with_the_description_of_the_folder(self):
        self.filed()
        origin = self.named_twice()
        self.assertIn(f'{self.TITLE} (1)\n\n' + self.listed(origin, 'peer', MINE, 3) + '\nFolders whose description',
                      self.due())
        # The change moves the module Small.Sums into the folder of that name, as Small.Sums.One, and carries
        # the description of the folder. After it the name is a folder alone, so that description answers
        # the report, though the module has no line.
        session = self.organizer('smover', {
            'rewrite/lean/Small/Sums/One.lean': self.ONE,
            'descriptions/modules/Small/Sums/One.md': 'The value of the sum of odd numbers at one term.\n',
            'descriptions/folders/Small/Sums.md': SUMS_TEXT})
        organization = read_json(session / 'output/organization.json')
        write_json(session / 'output/organization.json', {**organization, 'merge_questions': [], 'delete': ['Small.Sums']})
        self.receipt(session / 'output', ('module', 'Small.Sums.One', 'the sum at one term', True),
                     *(('folder', 'Small.Sums', purpose, True) for purpose in FOLDER_PURPOSES))
        code, printed = self.prepare_command(session)
        self.assertEqual(printed['open_reports'], [
            {**MINE, 'from': origin + ' · from the peer', 'answered_at_this_revision': True}], printed)
        self.assertEqual(code, 0, printed)
        # Published, the name is a folder alone, its description is of a revision that held the report, and
        # the report has left the list.
        self.publish_organizer(session)
        modules = knowledge.replay(self.instance)['modules']
        self.assertTrue('Small.Sums' not in modules and 'Small.Sums' in canon_index.folders_of(modules), modules)
        self.assertEqual(self.summary()['folders']['Small.Sums']['revision'], 3)
        self.assertIn(f'{self.TITLE} (0)\n', self.due())

    def test_a_change_without_reports_has_no_file_of_them_and_a_file_of_the_review_under_that_name_is_not_read(self):
        self.filed()
        output = self.reporting('squiet', reports=())
        cid, _ = self.publish(output, role='explore', question='q0')
        self.assertFalse((self.instance / 'knowledge/changes' / cid / 'index_reports.json').exists())
        # The output of a review is published whole. A file of it under the name that the peer's reports
        # have in a published change is not taken for them.
        engine = Runner(self.instance, self.skill)
        real = shutil.copytree

        def with_a_file(source, target, *more, **options):
            made = real(source, target, *more, **options)
            if Path(target).name.startswith('event-'):
                (Path(target) / 'index_reports.json').write_text('not the reports of a peer', encoding='utf-8')
            return made

        with patch('runner.shutil.copytree', side_effect=with_a_file):
            cid, _ = self.publish(self.reporting('squieter', reports=()), role='explore', question='q0', engine=engine)
        self.assertFalse((self.instance / 'knowledge/changes' / cid / 'index_reports.json').exists())
        self.assertEqual(knowledge.replay(self.instance)['index_reports'], [])

    def test_a_folder_named_like_the_file_of_reports_in_a_reviews_output_does_not_stop_the_publication(self):
        self.filed()
        real = shutil.copytree

        def with_a_folder(source, target, *more, **options):
            """The output of a review is published whole. It holds a folder under the name that the peer's
            reports have in a published change."""
            made = real(source, target, *more, **options)
            if Path(target).name.startswith('event-'):
                (Path(target) / 'index_reports.json').mkdir()
                (Path(target) / 'index_reports.json' / 'notes.md').write_text('Not the reports of a peer.', encoding='utf-8')
            return made

        # The candidate carries reports: the publication goes through, and the published folder holds the
        # candidate's file under that name.
        with patch('runner.shutil.copytree', side_effect=with_a_folder):
            cid, _ = self.publish(self.reporting(), role='explore', question='q0')
        published = self.instance / 'knowledge/changes' / cid / 'index_reports.json'
        self.assertTrue(published.is_file())
        self.assertEqual(read_json(published), [MINE])
        self.assertEqual(knowledge.replay(self.instance)['index_reports'], [{'change': cid, 'by': 'peer', 'sequence': 2, **MINE}])
        # The candidate carries none: the folder is taken out, and nothing stands under the name.
        with patch('runner.shutil.copytree', side_effect=with_a_folder):
            cid, _ = self.publish(self.reporting('squiet', reports=()), role='explore', question='q0')
        self.assertFalse((self.instance / 'knowledge/changes' / cid / 'index_reports.json').exists())
        self.assertEqual(len(knowledge.replay(self.instance)['index_reports']), 1)

    def test_the_programs_installed_before_this_change_read_a_candidate_that_carries_reports(self):
        installed = installed_runtime()
        if installed is None:
            self.skipTest('the skill is installed nowhere but in the tree under test, so no earlier programs are at hand')
        self.filed()
        output = self.reporting()
        self.assertTrue((output / 'descriptions/reports.json').is_file())
        # The installed canon.py is loaded in a process of its own, from where it is installed, with the modules
        # beside it; nothing is written there (-B).
        script = ('import json, sys\n'
                  'sys.path.insert(0, sys.argv[1])\n'
                  'import canon\n'
                  'try:\n'
                  '    change = canon.load_change(sys.argv[2])\n'
                  'except canon.CanonError as exc:\n'
                  '    print(json.dumps({"file": canon.__file__, "error": str(exc)}))\n'
                  'else:\n'
                  '    print(json.dumps({"file": canon.__file__, "keys": sorted(change)}))\n')
        environment = {key: value for key, value in os.environ.items() if key != 'PYTHONPATH'}

        def installed_load_change(candidate):
            done = subprocess.run([sys.executable, '-B', '-c', script, str(installed), str(candidate)], cwd=self.root,
                                  capture_output=True, text=True, timeout=600, env=environment)
            self.assertEqual(done.returncode, 0, done.stderr)
            said = json.loads(done.stdout)
            self.assertEqual(Path(said.pop('file')).resolve(), installed / 'canon.py')
            return said

        loaded = installed_load_change(output)
        self.assertNotIn('error', loaded)
        self.assertTrue({'title', 'description', 'replace', 'understanding'} <= set(loaded['keys']), loaded)
        # The same report in a key of change.json is what those programs refuse wherever they load a
        # candidate, the runner at each of its starts among them; this code refuses it as well.
        manifest = read_json(output / 'change.json')
        write_json(output / 'change.json', {**manifest, 'index_reports': [MINE]})
        self.assertIn('unknown key in change.json: index_reports', installed_load_change(output)['error'])
        with self.assertRaisesRegex(CanonError, r'^unknown key in change\.json: index_reports\. '):
            load_change(output)

    def test_the_reports_of_a_candidate_that_review_excluded_are_listed_until_a_later_revision_confirms_the_description(self):
        self.filed()
        self.describe({'descriptions/folders/Small/Sums.md': SUMS_TEXT})
        self.collect()
        kept = self.instance / 'runner/index-reports.jsonl'
        canon_before = tree_identity(self.instance / 'canon')
        # A candidate without a report, excluded: nothing is kept, and no file is made.
        self.exclude(self.reporting('squiet', reports=()), 'sfirstreview')
        self.assertFalse(kept.exists())
        self.assertIn(f'{self.TITLE} (0)\n', self.due())
        # A candidate with a report, excluded by a review that reports of the index itself.
        engine, job = self.exclude(self.reporting(), 'sexcluding', index_reports=[THEIRS])
        self.assertIsNone(engine.state['last_error'])
        lines = [json.loads(line) for line in kept.read_text(encoding='utf-8').splitlines()]
        self.assertEqual([{key: value for key, value in line.items() if key != 'at'} for line in lines],
                         [{'sequence': 2, 'by': 'peer', 'review': 'sexcluding', 'origin': 'excluded', **MINE},
                          {'sequence': 2, 'by': 'review', 'review': 'sexcluding', 'origin': 'excluded', **THEIRS}])
        # Nothing was published, and no state names the file: the canon and the events are as they were.
        self.assertEqual((len(self.events()), tree_identity(self.instance / 'canon')), (2, canon_before))
        self.assertEqual(knowledge.replay(self.instance)['index_reports'], [])
        self.assertNotIn('index-reports', (self.instance / 'runner/state.json').read_text(encoding='utf-8'))
        # The reports were kept when the canon had revision 2. A description of that revision may have been
        # prepared before they were kept, so they are answered from revision 3 on.
        origin = 'candidate that the review sexcluding excluded · revision 2'
        both = (f'{self.TITLE} (2)\n\n' + self.listed(origin, 'peer', MINE, 3, 1) + self.listed(origin, 'review', THEIRS, 3)
                + '\nFolders whose description')
        self.assertIn(both, self.due())
        # A runner that ended after it wrote the lines and before it saved the state writes them once more
        # when it collects the review again. The reports are listed once.
        engine.keep_reports('excluded', 'sexcluding', job)
        self.assertEqual(len(kept.read_text(encoding='utf-8').splitlines()), 4)
        self.assertIn(both, self.due())
        # A line that its process did not finish writing is passed over, and a line without `origin` is one of
        # an excluded candidate: the same report of the same review, listed once.
        with kept.open('ab') as stream:
            stream.write(json.dumps({'at': 2.0, 'sequence': 2, 'by': 'peer', 'review': 'sexcluding', **MINE}).encode('utf-8')
                         + b'\n{"at": 3.0, "sequence": 2, "by": "pe')
        self.assertIn(both, self.due())
        # An organizer prepares the description of Small.Sums at the revision at which the report was kept.
        # `prepare` names the report and says that this preparation does not answer it.
        session = self.described()
        code, printed = self.prepare_command(session)
        self.assertEqual((code, printed['open_reports']), (0, [
            {**MINE, 'from': origin + ' · from the peer', 'answered_at_this_revision': False}]), printed)
        self.publish_organizer(session)
        folder = self.summary()['folders']['Small.Sums']
        self.assertEqual((folder['revision'], folder['published']), (2, 3))
        self.assertIn(both.replace('it is of revision 1', 'it is of revision 2'), self.due())
        # The description is confirmed against the canon of revision 3: published again with the text it
        # has. The report against it leaves the list, and the report against the module without a line stays.
        self.describe({'descriptions/folders/Small/Sums.md': SUMS_TEXT})
        self.collect()
        folder = self.summary()['folders']['Small.Sums']
        self.assertEqual((folder['text'] + '\n', folder['revision'], folder['published']), (SUMS_TEXT, 3, 4))
        history = self.instance / 'canon/history/descriptions'
        self.assertEqual(list(history.rglob('*.md')) if history.exists() else [], [])
        self.assertIn(f'{self.TITLE} (1)\n\n' + self.listed(origin, 'review', THEIRS, 3) + '\nFolders whose description',
                      self.due())
        self.describe({'descriptions/modules/Small/Root.md': ROOT_LINE})
        self.collect()
        self.assertIn(f'{self.TITLE} (0)\n', self.due())

    def test_an_excluded_candidate_is_closed_also_where_its_reports_cannot_be_kept(self):
        self.filed()
        output = self.reporting()
        kept = self.instance / 'runner/index-reports.jsonl'
        # The file of the reports cannot be written: a folder stands where it belongs.
        kept.mkdir()
        engine, job = self.exclude(output, 'sexcluding')
        self.assertIn('the reports about the index of the candidate that the review sexcluding judged were not kept: ',
                      engine.state['last_error']['error'])
        kept.rmdir()
        # A candidate whose file of reports cannot be read as its form, and a candidate that is gone.
        candidate = Path(job['task']['candidate'])
        (candidate / 'descriptions/reports.json').write_text('{not json', encoding='utf-8')
        engine.state['last_error'] = None
        engine.keep_reports('excluded', 'sexcluding', job, {'publish': False})
        self.assertIn('were not kept: descriptions/reports.json is not JSON', engine.state['last_error']['error'])
        engine.state['last_error'] = None
        engine.keep_reports('excluded', 'sexcluding', {'task': {'candidate': str(self.root / 'gone')}}, {'publish': False})
        self.assertIsNone(engine.state['last_error'])
        self.assertFalse(kept.exists())
        self.assertIn(f'{self.TITLE} (0)\n', self.due())

    def test_a_kept_line_cut_inside_a_character_is_passed_over_and_the_lines_appended_after_it_are_listed(self):
        self.filed()
        kept = self.instance / 'runner/index-reports.jsonl'
        engine, job = self.exclude(self.reporting(), 'sexcluding', index_reports=[THEIRS])
        self.assertIsNone(engine.state['last_error'])
        whole = kept.read_bytes()
        origin = 'candidate that the review sexcluding excluded · revision 1'
        both = (f'{self.TITLE} (2)\n\n' + self.listed(origin, 'peer', MINE, 2) + self.listed(origin, 'review', THEIRS, 2)
                + '\nFolders whose description')
        self.assertIn(both, self.due())
        # The machine goes down inside the write of a line: the line ends inside a character of two bytes and
        # has no line end. Read as text, the file is no UTF-8.
        cut = '{"at": 3.0, "sequence": 1, "by": "peer", "review": "sexcluding", "purpose": "the thé'.encode('utf-8')[:-1]
        kept.write_bytes(whole + cut)
        with self.assertRaises(UnicodeDecodeError):
            kept.read_text(encoding='utf-8')
        # The cut line is passed over: `index --due` answers and lists the two reports, and the `prepare` of
        # an organizer whose change carries the description named is given the report against it.
        code, text = self.command_line('index', self.reader(), '--due')
        self.assertEqual(code, 0, text)
        self.assertIn(both, text)
        code, printed = self.prepare_command(self.described())
        self.assertEqual((code, printed['open_reports']), (0, [
            {**MINE, 'from': origin + ' · from the peer', 'answered_at_this_revision': False}]), printed)
        # The runner keeps further reports. Its lines begin on a line of their own after the cut one, so the
        # first of them is read like the second.
        engine.keep_reports('publication_failed', 'sexcluding', job)
        self.assertIsNone(engine.state['last_error'])
        self.assertTrue(kept.read_bytes().startswith(whole + cut + b'\n{"at": '))
        self.assertEqual([(entry['origin'], entry['by'], entry['description']) for entry in canon_index.kept_reports(self.instance)],
                         [('excluded', 'peer', 'Small.Sums'), ('excluded', 'review', 'Small.Root'),
                          ('publication_failed', 'peer', 'Small.Sums'), ('publication_failed', 'review', 'Small.Root')])
        self.assertIn(f'{self.TITLE} (4)\n', self.due())

    def test_the_reports_of_an_accepted_candidate_whose_publication_fails_are_kept_for_the_organizers(self):
        self.filed()
        kept = self.instance / 'runner/index-reports.jsonl'

        def failing(output):
            """A review accepts the candidate with a report of its own, and the candidate cannot be applied to
            the canon as it now is: (the runner, the session of the review)."""
            assessment = {**self.verdicts(output), 'index_reports': [THEIRS]}
            with patch('runner.apply_lean', side_effect=CanonError('the canon has changed under the candidate')):
                _, engine = self.publish(output, assessment, role='explore', question='q0', expect=False)
            review = next(sid for sid, session in reversed(engine.state['sessions'].items()) if session['role'] == 'review')
            pipeline = next(reversed(engine.state['pipelines'].values()))
            # The work went to a new peer, as it did before the reports were kept.
            self.assertEqual((pipeline['stage'], pipeline['record'], engine.state['publication']), ('peer', None, None))
            self.assertEqual([job['task']['previous_error'] for job in engine.state['jobs'].values()
                              if job['role'] == 'peer' and job['pipeline'] == pipeline['id'] and job['status'] == 'pending'],
                             ['the candidate could not be published on the current canon: the canon has changed under '
                              'the candidate'])
            return engine, review

        # The file of the reports cannot be written: the runner goes on, and says so in its state.
        kept.mkdir()
        engine, review = failing(self.reporting('sunkept'))
        self.assertIn(f'the reports about the index of the candidate that the review {review} judged were not kept: ',
                      engine.state['last_error']['error'])
        kept.rmdir()
        # A review whose assessment cannot be read leaves nothing either, and stops nothing.
        engine.state['last_error'] = None
        engine.keep_reports('publication_failed', 'snowhere', {'task': {'candidate': str(self.root / 'gone')}})
        self.assertIn('the review snowhere judged were not kept: ', engine.state['last_error']['error'])
        self.assertFalse(kept.exists())
        # The reports of the candidate and of the review are kept, with where they came from.
        engine, review = failing(self.reporting())
        lines = [json.loads(line) for line in kept.read_text(encoding='utf-8').splitlines()]
        self.assertEqual([{key: value for key, value in line.items() if key != 'at'} for line in lines],
                         [{'sequence': 1, 'by': 'peer', 'review': review, 'origin': 'publication_failed', **MINE},
                          {'sequence': 1, 'by': 'review', 'review': review, 'origin': 'publication_failed', **THEIRS}])
        self.assertEqual(len(self.events()), 1)
        origin = f'candidate that the review {review} accepted and whose publication failed · revision 1'
        self.assertIn(f'{self.TITLE} (2)\n\n' + self.listed(origin, 'peer', MINE, 2) + self.listed(origin, 'review', THEIRS, 2)
                      + '\nFolders whose description', self.due())
        # A description written against the revision at which they were kept leaves them, and a later one
        # answers the report against it.
        self.describe({'descriptions/folders/Small/Sums.md': SUMS_TEXT})
        self.collect()
        self.assertIn(f'{self.TITLE} (2)\n\n' + self.listed(origin, 'peer', MINE, 2, 1), self.due())
        self.describe({'descriptions/folders/Small/Sums.md': SUMS_TEXT})
        self.collect()
        self.assertIn(f'{self.TITLE} (1)\n\n' + self.listed(origin, 'review', THEIRS, 2) + '\nFolders whose description',
                      self.due())

    def test_reports_kept_of_a_failed_publication_are_not_listed_beside_the_published_change_of_the_same_review(self):
        self.filed()
        kept = self.instance / 'runner/index-reports.jsonl'
        output = self.reporting()
        assessment = {**self.verdicts(output), 'index_reports': [THEIRS]}
        real = Runner.keep_reports

        def ended(engine, *arguments, **options):
            """The runner keeps the reports of the failed publication and ends before it saves that the work
            goes to a new peer."""
            real(engine, *arguments, **options)
            raise RuntimeError('simulated end of the runner')

        with patch('runner.apply_lean', side_effect=CanonError('the canon has changed under the candidate')), \
                patch.object(Runner, 'keep_reports', autospec=True, side_effect=ended), \
                self.assertRaisesRegex(RuntimeError, 'simulated end of the runner'):
            self.publish(output, assessment, role='explore', question='q0', expect=False)
        lines = [json.loads(line) for line in kept.read_text(encoding='utf-8').splitlines()]
        self.assertEqual([(line['origin'], line['by']) for line in lines],
                         [('publication_failed', 'peer'), ('publication_failed', 'review')])
        # The state that was saved last still holds the publication. The next runner carries it on, and this
        # time the candidate can be applied: the change is published.
        self.assertIsNotNone(read_json(self.instance / 'runner/state.json')['publication'])
        engine = Runner(self.instance, self.skill)
        self.drain(engine)
        pipeline = next(reversed(engine.state['pipelines'].values()))
        cid, review = pipeline['record'], pipeline['review']
        self.assertEqual((pipeline['stage'], {line['review'] for line in lines}), ('done', {review}))
        self.assertEqual(read_json(self.instance / 'knowledge/changes' / cid / 'provenance.json')['review_session'], review)
        # The kept lines are still in the file, and each report is listed once, as one of the published change.
        self.assertEqual(len(kept.read_text(encoding='utf-8').splitlines()), 2)
        self.assertEqual(canon_index.kept_reports(self.instance), [])
        origin = f'published change {cid} · revision 2'
        due = self.due()
        self.assertIn(f'{self.TITLE} (2)\n\n' + self.listed(origin, 'peer', MINE, 2) + self.listed(origin, 'review', THEIRS, 2)
                      + '\nFolders whose description', due)
        self.assertNotIn('whose publication failed', due)

    def test_the_reports_of_a_review_whose_candidate_is_found_changed_are_kept_for_the_organizers(self):
        self.filed()
        kept = self.instance / 'runner/index-reports.jsonl'
        output = self.reporting()
        assessment = {**self.verdicts(output), 'index_reports': [THEIRS]}
        real = Runner.prepare_publication

        def changed(engine, sid, job, kind):
            """The review accepted the candidate. Before the runner applies it, a file of it is changed."""
            real(engine, sid, job, kind)
            (output / 'questions/q0.md').write_text('Another text, written after the review was assigned.\n',
                                                    encoding='utf-8')

        with patch.object(Runner, 'prepare_publication', autospec=True, side_effect=changed):
            _, engine = self.publish(output, assessment, role='explore', question='q0', expect=False)
        # The runner found the candidate changed and could not restore it: the work went to a new peer, and
        # nothing was published.
        pipeline = next(reversed(engine.state['pipelines'].values()))
        review = pipeline['review']
        self.assertEqual((pipeline['stage'], pipeline['record'], engine.state['publication'], len(self.events())),
                         ('peer', None, None, 1))
        # What the review reported in its assessment is kept, under the origin of an accepted candidate that
        # was not published. What the candidate reports is not: its files are not the ones that were frozen.
        lines = [json.loads(line) for line in kept.read_text(encoding='utf-8').splitlines()]
        self.assertEqual([{key: value for key, value in line.items() if key != 'at'} for line in lines],
                         [{'sequence': 1, 'by': 'review', 'review': review, 'origin': 'publication_failed', **THEIRS}])
        origin = f'candidate that the review {review} accepted and whose publication failed · revision 1'
        self.assertIn(f'{self.TITLE} (1)\n\n' + self.listed(origin, 'review', THEIRS, 2) + '\nFolders whose description',
                      self.due())
        # A review that excluded its candidate has its reports kept as those of an excluded candidate.
        engine.keep_reports(None, review, {'task': {}}, {'publish': False, 'index_reports': [MINE]}, candidate=False)
        last = json.loads(kept.read_text(encoding='utf-8').splitlines()[-1])
        self.assertEqual((last['origin'], last['by'], last['description']), ('excluded', 'review', 'Small.Sums'))
        # An assessment that cannot be read leaves no line and stops nothing.
        engine.state['last_error'] = None
        engine.keep_reports(None, 'snowhere', {'task': {}}, candidate=False)
        self.assertIn('the review snowhere judged were not kept: ', engine.state['last_error']['error'])
        self.assertEqual(len(kept.read_text(encoding='utf-8').splitlines()), 2)

    def test_review_reports_the_line_of_a_module_that_its_candidate_adds(self):
        from check import Invalid, assessment_check
        self.filed()
        peer = self.session_folder('speer', 'peer')
        output = self.fill(peer / 'output', {
            'lean/Small/Fresh/One.lean': module_text(theorem('sumOne', ': oddSum 1 = 1')),
            'records/Small/sumOne.md': record_text('The first odd number is one.'),
            'descriptions/modules/Small/Fresh/One.md': 'A statement about odd numbers.\n'}, replace=[])
        self.receipt(output, ('module', 'Small.Fresh.One', 'the sum at one term', True))
        self.assertEqual(self.prepare_command(peer)[0], 0)
        # The line the review was asked to judge, and the folder that the new module opens.
        line = {'description': 'Small.Fresh.One', 'element': 'Small.sumOne', 'purpose': 'the sum of one odd number'}
        folder = {'description': 'Small.Fresh', 'element': 'Small.sumZero', 'purpose': 'a base case of the sum'}
        assessment = {**self.verdicts(output), 'index_reports': [line, folder]}
        review = self.root / 'review-output'
        review.mkdir()
        (review / 'feedback.md').write_text('Checked.', encoding='utf-8')
        with self.assertRaisesRegex(Invalid, 'index_reports names no folder or module of the canon or of this '
                                             'candidate: Small.Fresh.Two'):
            assessment_check({**assessment, 'index_reports': [{**line, 'description': 'Small.Fresh.Two'}]}, review,
                             output, knowledge.replay(self.instance), self.instance, 'sreview')
        # The transport check of the review's output passes (publish makes it), and the change is published.
        cid, engine = self.publish(output, assessment)
        self.assertEqual(knowledge.replay(self.instance)['index_reports'],
                         [{'change': cid, 'by': 'review', 'sequence': 2, **line},
                          {'change': cid, 'by': 'review', 'sequence': 2, **folder}])
        # The line came with the change that the review reports of. It was prepared against the canon of
        # revision 1, before the report existed, so the report against it is listed like the one against the
        # folder that has no description yet.
        entry = self.summary()['modules']['Small.Fresh.One']
        self.assertEqual((entry['revision'], entry['published']), (1, 2))
        origin = f'published change {cid} · revision 2'
        self.assertIn(f'{self.TITLE} (2)\n\n' + self.listed(origin, 'review', line, 2, 1)
                      + self.listed(origin, 'review', folder, 2) + '\nFolders whose description', self.due())


class SettingsUsageAndContextTests(IndexCase):
    def test_the_search_settings_are_a_default_in_code_and_no_key_is_written_into_an_instance(self):
        self.assertEqual(settings.defaults()['search'], {'model': 'claude/sonnet', 'effort': 'medium', 'parallel': 2})
        # An instance from before the search: its settings.json has no such key.
        raw = read_json(self.instance / 'settings.json')
        del raw['search']
        write_json(self.instance / 'settings.json', raw)
        held = (self.instance / 'settings.json').read_bytes()
        self.assertEqual(settings.load_settings(self.instance)['search'], settings.defaults()['search'])
        engine = Runner(self.instance, self.skill)
        engine.refresh()
        self.assertEqual(engine.settings['search']['parallel'], 2)
        self.assertEqual((self.instance / 'settings.json').read_bytes(), held)
        # A key given is merged over the default, and what cannot be run is refused.
        self.assertEqual(settings.validate({**raw, 'search': {'parallel': 4}})['search'],
                         {'model': 'claude/sonnet', 'effort': 'medium', 'parallel': 4})
        for given, said in (({'model': 'codex/gpt-6.1-sol'}, 'search.model must be a Claude model'),
                            ({'effort': 'extreme'}, 'Unsupported Claude effort'),
                            ({'parallel': 0}, 'search.parallel must be a positive integer'),
                            ({'depth': 3}, 'unknown setting: search.depth')):
            with self.subTest(given=given), self.assertRaisesRegex(ValueError, said):
                settings.validate({**raw, 'search': given})

    def test_status_adds_up_what_the_searches_and_the_blind_tests_used(self):
        self.assertEqual(search_usage(self.instance)['searches'], 0)
        ledger = self.instance / 'runner/search/ledger.jsonl'
        ledger.parent.mkdir(parents=True)
        said = {'model': 'claude/sonnet', 'effort': 'low'}
        # The search s-a has the lines of two light sessions, the line that closes its first run, and the lines of
        # a second run, in which the part that was not read was read. It is one search. s-b is another, and the
        # test t-a has one light session, which reported no cost. A key names a search or a test apart, also
        # where a search and a test had the same.
        lines = [{'at': 1.0, 'kind': 'search', 'key': 's-a', 'session': 's1', **said, 'light_sessions': 1,
                  'tokens': {'inputTokens': 10, 'cacheReadInputTokens': 900}, 'cost_usd': 0.25, 'seconds': 40.5},
                 {'at': 1.1, 'kind': 'search', 'key': 's-a', 'session': 's1', **said, 'light_sessions': 1,
                  'tokens': {'inputTokens': 2}, 'cost_usd': 0.5, 'seconds': 3},
                 {'at': 1.2, 'kind': 'search', 'key': 's-a', 'session': 's1', **said, 'light_sessions': 0, 'tokens': {},
                  'cost_usd': 0, 'seconds': 0, 'read': {'parts': 2, 'parts_not_read': 1}},
                 {'at': 1.3, 'kind': 'search', 'key': 's-a', 'session': 's3', **said, 'light_sessions': 1,
                  'tokens': {'inputTokens': 1}, 'cost_usd': 0.25, 'seconds': 1},
                 {'at': 1.4, 'kind': 'search', 'key': 's-a', 'session': 's3', **said, 'light_sessions': 0, 'tokens': {},
                  'cost_usd': 0, 'seconds': 0, 'read': {'parts': 2, 'parts_not_read': 0}},
                 {'at': 1.5, 'kind': 'search', 'key': 's-b', 'session': 's1', **said, 'light_sessions': 1,
                  'tokens': {'inputTokens': 1}, 'cost_usd': 1, 'seconds': 2},
                 {'at': 2.0, 'kind': 'descent-test', 'key': 't-a', 'session': 's2', **said, 'light_sessions': 1,
                  'tokens': {'inputTokens': 4, 'outputTokens': 7}, 'cost_usd': None, 'seconds': 6},
                 {'at': 2.1, 'kind': 'descent-test', 'key': 's-a', 'session': 's2', **said, 'light_sessions': 1,
                  'tokens': {}, 'cost_usd': 0.5, 'seconds': 0},
                 # A line without a key is a search of its own.
                 {'at': 2.2, 'kind': 'search', 'session': 's4', **said, 'light_sessions': 2, 'tokens': {}, 'cost_usd': 0.5,
                  'seconds': 0}]
        # A line that its process did not finish writing is left out.
        ledger.write_text('\n'.join(json.dumps(line) for line in lines) + '\n{"at": 3.0, "kind": "sea', encoding='utf-8')
        self.assertEqual(status(self.instance)['usage']['search'], {
            'searches': 3, 'descent_tests': 2, 'light_sessions': 8, 'cost_usd': 3.0, 'without_cost': 1,
            'seconds': 52.5, 'tokens': {'inputTokens': 18, 'cacheReadInputTokens': 900, 'outputTokens': 7}})

    def test_a_session_launched_before_the_view_was_rendered_is_told_how_to_print_the_folder_level(self):
        (self.instance / 'knowledge/folders.md').unlink()
        folder = self.instance / 'sessions' / 'sfirst'
        folder.mkdir(parents=True)
        engine = Runner(self.instance, self.skill)
        inp = assemble(self.skill, self.instance, folder, 'attempt', {}, None, 0, engine.settings)
        self.assertIs(inp['descriptions'], True)
        pack = (folder / 'pack.md').read_text(encoding='utf-8')
        view = pack.split('\n# Index of the canon at launch: the folder level\n', 1)[1].split('\n# Board at launch\n', 1)[0]
        self.assertIn('The runner has not rendered this view yet. The command `index` of `commands.canon` prints the '
                      'folder level as it is now.', view)

    def test_descent_test_is_handed_to_the_search_program_and_no_reading_command_depends_on_that_program(self):
        peer = self.session_folder('speer', 'peer')
        calls = []
        program = types.ModuleType('search')

        def stand_in(session, timeout):
            calls.append((session, timeout))
            if len(calls) > 1:
                raise CanonError('the test is for the session that writes descriptions')
            return 7

        program.descent_test_command = stand_in
        with patch.dict(sys.modules, {'search': program}):
            # The command gives the folder and the timeout on, and its exit code is what the program returns.
            code, text = self.command_line('descent-test', peer, '--timeout', '9')
            self.assertEqual((code, calls), (7, [(peer, 9.0)]))
            # What the program refuses is reported as every error of the canon tool is.
            code, text = self.command_line('descent-test', peer)
            self.assertEqual((code, json.loads(text), calls[1]),
                             (1, {'error': 'the test is for the session that writes descriptions'}, (peer, 50.0)))
        # Without the program the command says so, and the reading commands do not depend on it.
        with patch.dict(sys.modules, {'search': None}):
            code, text = self.command_line('descent-test', peer)
            self.assertEqual(code, 1)
            self.assertIn('the blind descent test cannot be run', json.loads(text)['error'])
            self.assertEqual(self.command_line('index', peer)[0], 0)


if __name__ == '__main__':
    unittest.main()
