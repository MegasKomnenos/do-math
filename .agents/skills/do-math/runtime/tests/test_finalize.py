"""The finalize command and its scripts, with stand-in sessions, the stand-in compiler and a stand-in Lake.

No AI session, no Lean and no Lake is run. The launch of a session is patched as tests/test_paper.py
patches it: the command the program starts is this file itself, which then plays the session. Run as
`test_finalize.py session <scenario folder>` it reads session.json in its working folder and writes
what `script.json` of the scenario gives for that kind of session: for the key `<kind>:<section>`,
or else `<kind>`, one entry for each session in turn and the last entry for every later one. An
entry maps a path under the session's folder to its text; the key `@copy` lists pairs of paths, each
a file or folder of the session copied to another place in it. Every call is recorded with the files
the session was given. Run as `test_finalize.py lake ...` it is Lake: `build` succeeds unless
`lake.json` of the scenario names a text that Challenge.lean then holds; `env lean DoMathExtract.lean`
runs the stand-in compiler's extraction; `env lean Check.lean` prints an axioms line for every name
that Check.lean asks about; and every call fails when `lake.json` names under `needs_variable` a variable
that its environment does not have. Run as `test_finalize.py version` it is Lean's version command.

The paper command is not run: `finalize.produce` is replaced by a function that writes the files
section 15.1 of the design names and records what it was called with. Its own tests are test_paper.py.
"""
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time

THIS = Path(__file__).resolve()


def stand_in_session(scenario):
    folder = Path.cwd()
    task = json.loads((folder / 'session.json').read_text(encoding='utf-8'))
    sys.stdin.reconfigure(encoding='utf-8')  # the program hands over the bytes of a UTF-8 file, whatever the locale
    prompt = sys.stdin.read()
    script = json.loads((scenario / 'script.json').read_text(encoding='utf-8'))
    own = f"{task['kind']}:{task['section']}"
    key = next((k for k in (own, task['kind']) if k in script), None)
    given = sorted(p.relative_to(folder).as_posix() for p in folder.rglob('*')
                   if p.is_file() and not p.name.startswith(('cli.', 'worker-')))
    lock = scenario / 'calls.lock'
    while True:
        try:
            os.close(os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY))
            break
        except (FileExistsError, PermissionError):
            time.sleep(0.01)
    try:
        record = scenario / 'calls.json'
        calls = json.loads(record.read_text(encoding='utf-8')) if record.exists() else []
        if key is not None:
            entries = script[key]
            entry = entries[min(sum(c['key'] == key for c in calls), len(entries) - 1)]
            for source, target in entry.get('@copy', []):
                if (folder / source).is_dir():
                    shutil.copytree(folder / source, folder / target, dirs_exist_ok=True)
                else:
                    (folder / target).parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(folder / source, folder / target)
            for name, content in entry.items():
                if name != '@copy':
                    (folder / name).parent.mkdir(parents=True, exist_ok=True)
                    (folder / name).write_text(content, encoding='utf-8', newline='\n')
        calls.append({'key': key, 'kind': task['kind'], 'section': task['section'], 'folder': folder.name,
                      'given': given, 'prompt': prompt, 'model': task.get('model')})
        record.write_text(json.dumps(calls), encoding='utf-8')
    finally:
        lock.unlink()
    print(json.dumps({'type': 'item.completed', 'item': {'type': 'agent_message', 'text': 'Scripted session.'}}))
    return 0


def stand_in_lake(scenario, arguments):
    settings = json.loads((scenario / 'lake.json').read_text(encoding='utf-8')) if (scenario / 'lake.json').exists() else {}
    with (scenario / 'lake-calls.txt').open('a', encoding='utf-8') as stream:
        stream.write(' '.join(arguments) + '\n')
    needed = settings.get('needs_variable')
    if needed and not os.environ.get(needed):
        print(f'error: the stand-in for Lake was started without {needed} in its environment')
        return 1
    if arguments == ['build']:
        failing = settings.get('build_fails_when')
        if failing and failing in Path('Challenge.lean').read_text(encoding='utf-8'):
            print('error: Challenge.lean: the stand-in refuses this text')
            return 1
        manifest = json.loads(Path('lake-manifest.json').read_text(encoding='utf-8'))
        Path('built.json').write_text(json.dumps({'packagesDir': manifest['packagesDir']}), encoding='utf-8')
        return 0
    if arguments[:2] == ['env', 'lean'] and arguments[2] == 'DoMathExtract.lean':
        sys.path.insert(0, str(THIS.parent))
        import canon_lean
        return canon_lean.extract('.', 'DoMathExtract.lean')
    if arguments[:2] == ['env', 'lean'] and arguments[2] == 'Check.lean':
        for name in re.findall(r'^#print axioms (\S+)$', Path('Check.lean').read_text(encoding='utf-8'), re.M):
            axioms = settings.get('axioms', {}).get(name, ['propext', 'Quot.sound'])
            print(f"{name} : a statement\n'{name}' depends on axioms: [{', '.join(axioms)}]" if axioms
                  else f"'{name}' does not depend on any axioms")
        return 0
    return 2


if __name__ == '__main__' and sys.argv[1:2] == ['session']:
    raise SystemExit(stand_in_session(Path(sys.argv[2])))
if __name__ == '__main__' and sys.argv[1:2] == ['lake']:
    raise SystemExit(stand_in_lake(Path(sys.argv[2]), sys.argv[3:]))
if __name__ == '__main__' and sys.argv[1:2] == ['version']:
    print('Lean (version 4.99.0, stand-in)')
    raise SystemExit(0)

import atexit
import hashlib
import tempfile
import threading
import unittest
from unittest.mock import patch

import yaml

sys.path[:0] = [str(THIS.parents[1]), str(THIS.parent)]
import canon
import finalize
import package
import paper
from cli_adapter import Command, provider_for_model
from knowledge import replay
from runtime_support import read_json, remove_tree, write_json
from support import DEFS, ROOT, InstanceCase, module_text, record_text, stop_broker, template, theorem

INSTALLED = THIS.parents[2]
ROOT_STATEMENT = '(n : Nat) : oddSum n = n * n'
STEP = module_text(theorem('sq_step', '(n : Nat) : oddSum (n + 1) = oddSum n + (2 * n + 1)', proof='rfl'))
UNUSED = theorem('unused_two', ': oddSum 2 = 4', proof='rfl')
HELPER_PARTS = [
    'def twice (n : Nat) : Nat := oddSum n + oddSum n',
    theorem('twice_zero', ': twice 0 = 0', proof='rfl'),
    theorem('helper_zero', ': oddSum 0 = 0', proof='rfl'),
    '/-- A rewriting rule. -/\n@[simp]\ntheorem simp_one : oddSum 1 = 1 := by\n  rfl',
    UNUSED,
    theorem('named_four', ': oddSum 4 = 16', proof='rfl'),
    '/-- A helper that is no element. -/\nprivate theorem hidden_three : oddSum 3 = 9 := by\n  have h1 := named_four\n  rfl']
HELPER = module_text('\n\n'.join(HELPER_PARTS))
# The module as a simplifying session returns it: the taken module, which is without `unused_two`, with one lemma added.
HELPER_SIMPLIFIED = module_text('\n\n'.join([part for part in HELPER_PARTS if part != UNUSED]
                                             + [theorem('added_six', ': oddSum 6 = 36', proof='rfl')]))
EXTRA = module_text(theorem('stray', ': oddSum 5 = 25', proof='rfl'))
ROOT_PROOF = theorem('root', ROOT_STATEMENT, uses=['sq_step', 'helper_zero', 'twice_zero'], proof='rfl',
                     doc='The sum of the first `n` odd numbers is the square of `n`.')
BIBLIOGRAPHY = '@book{gauss1801,\n  author = {Gauss, Carl Friedrich},\n  title = {Disquisitiones {A}rithmeticae},\n  year = {1801}\n}\n'
RECORDS = {
    'Small/sq_step.md': record_text('Passing from n to n + 1 adds the odd number 2n + 1.', weight='unit', source='gauss1801',
                                    statement='For every $n$, $s(n+1) = s(n) + 2n + 1$.'),
    'Small/twice.md': record_text('Twice the sum of the first n odd numbers.', weight='unit'),
    'Small/twice_zero.md': record_text('Twice the empty sum is zero.', weight='unit'),
    'Small/helper_zero.md': record_text('The empty sum is zero.'),
    'Small/simp_one.md': record_text('The first odd number is one.'),
    'Small/unused_two.md': record_text('The first two odd numbers sum to four.'),
    'Small/named_four.md': record_text('The first four odd numbers sum to sixteen, as `Small.unused_two` suggests.'),
    'Small/stray.md': record_text('The first five odd numbers sum to twenty-five.'),
    'Small/root.md': record_text('The sum of the first n odd numbers equals n times n.', weight='unit',
                                 proof='By induction, from `Small.sq_step`.',
                                 statement='For every natural number $n$, $1 + 3 + \\dots + (2n - 1) = n^2$.',
                                 short='odd numbers sum to a square'),
}
ACCOUNT = 'The stand-in account of the chosen proof: induction on n through the step.'
INSTRUCTIONS = ('selection', 'selection-read', 'restore', 'review', 'simplify', 'arrange', 'records-write',
                'records-compare', 'sources', 'foldback', 'draft-compare', 'history-write', 'history-read',
                'readme-write', 'package-read')
_SETTLED = None
# What the paper command closed without a person, as the `end` event of its log carries it.
CLOSED = [{'kind': 'removed', 'where': 'the abstract', 'section': 'abstract',
           'quote': 'equivalently, the block sums to a difference of squares',
           'asserts': 'The block sum is a difference of squares.', 'nearest': 'Small.sq_step',
           'difference': 'It states the sum additively.'},
          {'kind': 'restated', 'label': 'lem:step', 'number': 'Lemma 1.1', 'element': 'Small.sq_step',
           'before': 'For $n \\ge 1$ the step holds.', 'difference': 'The element has every n.',
           'after': 'For every $n$ the step holds.', 'verdict': 'differs', 'difference_after': 'The range of n.'}]


def decision(main='Small.sq_step', options=None, choice='a', runner_up=None, **more):
    options = options or [{'id': 'a', 'main': main, 'route': 'present', 'proves': 'The root.', 'rests_on': 'The step.',
                           'size': 'Small.', 'for': 'It shows why.', 'against': 'Nothing.'}]
    return json.dumps({'options': options, 'choice': choice, 'runner_up': runner_up, 'reasons': 'It is the only route.',
                       'sentence': 'The first n odd numbers sum to n squared.', 'account': ACCOUNT,
                       'registry': {'arxiv': ['math.CO'], 'msc2020': ['05A15'], 'origin': 'original',
                                    'sources': [{'key': 'gauss1801', 'relationship': 'background',
                                                 'note': 'It has the step in its first section.'}],
                                    'related_formalizations': [],
                                    'divergences': 'The Lean sum starts at index 0; the empty sum is 0.',
                                    'settles': 'The identity is classical; the records name nobody who posed it.',
                                    'novelty': 'The records name no proof of it and report no search for one.',
                                    'stated_in': 'root.md; the record of Small.sq_step.'}, **more})


def script(**changes):
    """What the stand-in sessions write in a run that comes to its end; `changes` replace entries by key."""
    plain = {
        'selection': [{'output/decision.json': decision()}],
        'selection-read': [{'output/reading.json': json.dumps({'claims': [{'option': 'a', 'claim': 'It rests on the step.',
                                                                           'holds': True}]})}],
        'review': [{'output/review.json': json.dumps({
            'parts': [{'id': 'core', 'title': 'The core', 'modules': ['Small.Root', 'Small.Helper'], 'inside': 'One lemma.'},
                      {'id': 'aux', 'title': 'The step', 'modules': ['Small.Step'], 'inside': 'Nothing.'}],
            'cross': [{'id': 'x1', 'owner': 'core', 'what': 'Add the sum of six terms.', 'touches': ['aux']}]})}],
        'simplify:core': [{'output/lean/Small/Helper.lean': HELPER_SIMPLIFIED,
                           'output/report.json': json.dumps({'deleted': [], 'cross': [{'id': 'x1', 'done': True, 'note': ''}],
                                                             'notes': ''})}],
        # The first session of this part leaves a report that does not parse, the second a module that does not compile.
        'simplify:aux': [{'output/report.json': '{"deleted": [], '},
                         {'output/lean/Small/Step.lean': STEP + '-- fail: this simplification does not compile\n',
                          'output/report.json': json.dumps({'deleted': [], 'cross': [], 'notes': ''})}],
        'arrange': [{'@copy': [['lean', 'output/lean']], 'output/renames.json': '{}', 'output/removed.json': '[]'}],
        'records-write:5-01': [{'output/records/Small/added_six.md': record_text('The first six odd numbers sum to thirty-six.'),
                                'output/records/Small/named_four.md': record_text('The first four odd numbers sum to sixteen.'),
                                'output/findings.json': json.dumps([{'declaration': 'Small.added_six', 'kind': 'conclusion',
                                                                     'detail': 'Nothing uses it.'}])}],
        'records-compare:5-01': [{'output/verdicts.json': json.dumps([
            {'declaration': name, 'verdict': 'agrees', 'difference': ''} for name in ('Small.added_six', 'Small.named_four')])}],
        'sources': [{'@copy': [['bibliography.bib', 'output/bibliography.bib']], 'output/requests.json': '[]',
                     'output/sources.json': json.dumps([{'key': 'gauss1801', 'status': 'verified', 'identifier': 'isbn:1',
                                                         'opened': 'parts', 'note': ''}])}],
        'foldback': [{'output/lean/Small/Step.lean': STEP.replace('\n\nend Small', '\n\n' + theorem(
            'sq_step_strict', '(n : Nat) : oddSum n < oddSum (n + 1)', uses=['sq_step'], proof='rfl') + '\n\nend Small'),
            'output/report.json': json.dumps({'deleted': [], 'items': [
                {'id': 'g1', 'closed': True, 'declarations': ['Small.sq_step_strict'], 'note': ''},
                {'id': 'r1', 'closed': False, 'declarations': [], 'note': 'The lemma is wanted by the cross-part item.'}]})}],
        'records-write:6-01': [{'output/records/Small/sq_step_strict.md': record_text('The sums increase strictly.'),
                                'output/findings.json': json.dumps([{'declaration': 'Small.sq_step_strict', 'kind': 'other',
                                                                     'detail': 'Its doc comment says less than it states.'}])}],
        'records-compare:6-01': [{'output/verdicts.json': json.dumps([{'declaration': 'Small.sq_step_strict',
                                                                       'verdict': 'corrected', 'difference': 'A word.'}]),
                                  'output/records/Small/sq_step_strict.md': record_text('The sums increase strictly with n.')}],
        'draft-compare': [{'output/verdicts.json': json.dumps([{'id': 'g1', 'verdict': 'rewritten',
                                                                'text': 'For every $n$, $s(n) < s(n+1)$.'}])}],
        'history-write': [{'output/entries.json': json.dumps([
            {'event': 1, 'date': '', 'text': 'A change gave the root its proof.'},
            {'event': 2, 'date': '', 'text': 'The root question was understood.'}])}],
        'history-read': [{'output/verdicts.json': json.dumps([{'event': 1, 'verdict': 'stands', 'text': ''},
                                                              {'event': 2, 'verdict': 'corrected',
                                                               'text': 'The account of the root question was written.'}])}],
        'readme-write': [{'output/outline.md': 'The proof is by induction, in {{facts.modules}} modules.\n',
                          'output/obtained.md': 'The research made {{facts.publications}} publication.\n'}],
        'package-read': [{'output/findings.json': '[]'}],
    }
    plain.update({key.replace('_', '-'): value for key, value in changes.items()})
    return plain


DRAFT = {'statements': [{'label': 'thm:main', 'section': 'intro', 'element': 'Small.root', 'text': 'The sum is a square.',
                         'gap': None},
                        {'label': 'lem:step', 'section': 'intro', 'element': 'Small.sq_step', 'text': 'The sums increase.',
                         'gap': 'g1'}],
         'formulas': [],
         'gaps': [{'id': 'g1', 'kind': 'statement', 'section': 'intro', 'label': 'lem:step', 'host': None,
                   'element': 'Small.sq_step', 'wanted': 'The sums increase strictly.', 'has': 'The step as an equation.',
                   'reason': 'A paper states the inequality.', 'closed_by': None}],
         'citations': []}
PLAN = {'title': 'Odd numbers sum to squares', 'sections': [{'id': 'intro', 'title': 'Introduction'}],
        'statements': [{'label': 'thm:main', 'element': 'Small.root'},
                       {'label': 'lem:step', 'element': 'Small.sq_step', 'proof': 'cited'}]}


class FinalizeCase(InstanceCase):
    """An instance whose root is proved in Lean through a step, made once through the real publication path."""

    def starting_instance(self):
        """The published instance once the first test has made it; before that, the one `init` created."""
        return _SETTLED or super().starting_instance()

    def setUp(self):
        global _SETTLED
        super().setUp()
        if _SETTLED is None:
            folder = self.candidate(
                modules={'Small/Step.lean': STEP, 'Small/Helper.lean': HELPER, 'Small/Extra.lean': EXTRA},
                replace={'Small.root': ROOT_PROOF}, imports={'Small.root': ['Small.Step', 'Small.Helper']},
                records=RECORDS, understanding={'q0.md': 'The step from n to n + 1 is the whole proof.\n'}, prepare=False)
            (folder / 'bibliography.bib').write_text(BIBLIOGRAPHY, encoding='utf-8')
            self.prepare(folder)
            self.publish(folder)
            self.configure(lean={'version_command': [sys.executable, '-B', str(THIS), 'version']})
            stop_broker(self.instance)
            base = Path(tempfile.mkdtemp(prefix='do-math-finalize-'))
            atexit.register(remove_tree, base)
            shutil.copytree(self.instance, base / 'instance')
            _SETTLED = base / 'instance'
        self.repository = self.root / 'repository'
        self.repository.mkdir()
        (self.repository / 'README.md').write_text('# The repository\n\n## Solved problems\n\n- An earlier one.\n\n## Other\n',
                                                   encoding='utf-8')
        self.work = self.repository / '.skill-workspace' / 'finalize-odd'
        self.solved = self.repository / 'solved' / 'odd'
        self.scenario = self.root / 'scenario'
        self.scenario.mkdir()
        for name in INSTRUCTIONS:
            path = self.skill / 'finalize' / (name + '.md')
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f'Instruction {name} for {{{{root}}}}, main {{{{main}}}}.\n', encoding='utf-8')
        (self.skill / 'finalize' / 'simplify.md').write_text('Simplify the part {{part}}.\n', encoding='utf-8')
        (self.skill / 'finalize' / 'common.md').write_text(
            'Common: work {{work}}, skill {{skill}}, python {{python}}, library {{library}}, source {{imported_source}}, '
            'memory {{expect_mb}}.\n', encoding='utf-8')
        shutil.copytree(INSTALLED / 'finalize' / 'licences', self.skill / 'finalize' / 'licences')
        self.produced, self.paper_code, self.draft = [], 0, DRAFT
        self.closed = []  # what the stand-in for the paper command says it closed without a person
        self.failing = False  # whether the stand-in leaves a manuscript that fails its typesetting
        self.addCleanup(stop_broker, self.work)

    def command(self, cli, model, effort, cwd, servers=None, **options):
        return Command(provider_for_model(model), [sys.executable, '-B', str(THIS), 'session', str(self.scenario)], Path(cwd))

    def produce(self, instance, out, tex=None, choice=None, parallel=4, resume=False, dry=False, draft=False,
                from_draft=None, title_page=None, gate=None, main=None):
        """Stands in for paper.produce: writes the files that section 15.1 of the design names."""
        out = Path(out)
        self.produced.append({'instance': Path(instance).name, 'out': out.name, 'resume': resume, 'draft': draft,
                              'from_draft': from_draft, 'gate': gate, 'parallel': parallel, 'main': main,
                              'title_page': read_json(title_page) if title_page else None,
                              'root_state': replay(instance)['root_state'],
                              'drafted': read_json(Path(from_draft) / 'draft.json') if from_draft else None,
                              'history': threading.active_count()})
        out.mkdir(parents=True, exist_ok=True)
        write_json(out / 'materials.json', {})
        write_json(out / 'plan.json', PLAN)
        session = {'event': 'session', 'kind': 'write', 'model': 'codex/paper-model'}
        if draft:
            (out / 'study.md').write_text('How the chosen papers are written.\n', encoding='utf-8')
            write_json(out / 'draft.json', self.draft)
            write_json(out / 'log.json', [session])
            return self.paper_code
        if self.failing:
            write_json(out / 'log.json', [session, {'event': 'end', 'status': 'open_findings', 'kept': [], 'open': [
                {'check': paper.TYPESETTING, 'after_repairs': 3, 'problems': ['TeX stopped at line 12.']}]}])
            return 2
        (out / 'parts').mkdir(exist_ok=True)
        (out / 'parts' / 'intro.tex').write_text('We prove that the odd numbers sum to squares.\n', encoding='utf-8')
        # As the paper command writes them: with LF line endings on every platform.
        (out / 'paper.tex').write_text('\\documentclass{amsart}\n', encoding='utf-8', newline='\n')
        (out / 'paper.pdf').write_bytes(b'%PDF-1.4 stand-in\n')
        (out / 'references.bib').write_text(BIBLIOGRAPHY, encoding='utf-8', newline='\n')
        write_json(out / 'correspondence.json', {'root': 'Small.root', 'statements': [
            {'label': 'thm:main', 'element': 'Small.root', 'cited': None},
            {'label': 'lem:step', 'element': 'Small.sq_step', 'cited': 'gauss1801'}]})
        write_json(out / 'log.json', [session, {'event': 'end', 'status': 'complete', 'open': [],
                                                'kept': [{'check': 'reading', 'finding': 'The title is long.',
                                                          'reason': 'It names the result.'}],
                                                **({'closed': self.closed} if self.closed else {})}])
        return self.paper_code

    def run_command(self, plan=None, config=None, name='odd', lake=None, operating=True):
        """One start of the command with the stand-ins in place; returns its exit code.

        The run reduces the Lean settings of the instance to what names the Lean environment, so its broker
        would run the stand-in compiler with the defaults of a real one: at low priority, and reserving
        2 GiB for each compile. With `operating` the reduced settings are given the values the other
        tests of the runtime give the stand-in compiler, so that a test does not wait on the machine's load."""
        real = package.reduced_settings

        def reduced(settings):
            value = real(settings)
            if operating:
                value['lean'].update(priority='normal', min_free_memory_mb=0, memory_budget_mb=512, calibration_expect_mb=64)
            return value

        if plan is not None:
            write_json(self.scenario / 'script.json', plan)
        if lake is not None:
            write_json(self.scenario / 'lake.json', lake)
        arguments = [str(self.instance), '--name', name]
        if config is not None:
            write_json(self.root / 'config.json', config)
            arguments += ['--config', str(self.root / 'config.json')]
        with patch('finalize.REPOSITORY', self.repository), patch('finalize.SKILL', self.skill), \
                patch('paper.worker_command', side_effect=self.command), patch('finalize.produce', side_effect=self.produce), \
                patch('paper.load_collection', return_value=([], {}, None)), \
                patch('package.reduced_settings', side_effect=reduced), \
                patch('package.lake_command', return_value=[sys.executable, '-B', str(THIS), 'lake', str(self.scenario)]), \
                patch('builtins.print') as shown:
            code = finalize.main(arguments)
        self.said = shown.call_args.args[0] if shown.call_args else ''
        return code

    def config(self, **more):
        return {'tex': [sys.executable], 'parallel': 2, **more}

    def calls(self, kind=None):
        calls = read_json(self.scenario / 'calls.json') if (self.scenario / 'calls.json').exists() else []
        return [call for call in calls if kind in (None, call['kind'])]

    def steps(self):
        return [event['step'] for event in read_json(self.work / 'log.json') if event['event'] == 'step']

    def decisions(self):
        return (self.work / 'decisions.md').read_text(encoding='utf-8')


# ----------------------------------------------------------------------------- the scripts, each alone

class TakeTests(FinalizeCase):
    def setUp(self):
        super().setUp()
        self.index = canon.read_index(self.instance / 'canon' / 'index.json')
        self.lean = self.instance / 'canon' / 'lean'
        self.plan = package.take(self.index, self.lean, 'Small', 'Small.root', ['Small.Defs'])

    def test_what_the_root_rests_on_is_kept_with_attributes_definitions_and_what_a_private_declaration_names(self):
        kept, removed = set(self.plan['kept']), set(self.plan['removed'])
        self.assertLessEqual({'Small.root', 'Small.sq_step', 'Small.helper_zero', 'Small.twice_zero', 'Small.twice'}, kept)
        self.assertIn('Small.oddSum', kept)       # an element of a definition module
        self.assertIn('Small.simp_one', kept)     # carries an attribute, and no proof names it
        self.assertIn('Small.named_four', kept)   # named by a private declaration, which is no element and stays
        self.assertEqual(removed, {'Small.unused_two', 'Small.stray'})
        self.assertEqual(self.plan['deleted'], ['Small.Extra'])
        self.assertNotIn('Small/Extra.lean', self.plan['files'])

    def test_a_kept_file_is_the_source_less_whole_removed_elements(self):
        before = (self.lean / 'Small' / 'Helper.lean').read_text(encoding='utf-8')
        after = self.plan['files']['Small/Helper.lean']
        gone = canon.declaration_text(before, self.index['entries']['Small.unused_two']['span'])
        self.assertIn('theorem unused_two', gone)
        self.assertTrue(gone.startswith('/--'))  # the doc comment goes with its declaration
        self.assertNotIn('unused_two', after)
        self.assertEqual(before.count(gone + '\n\n'), 1)
        self.assertEqual(after, before.replace(gone + '\n\n', ''))  # the declaration and the blank line that set it off
        self.assertIn('private theorem hidden_three', after)  # what is no element is never removed
        self.assertEqual(self.plan['files']['Small/Defs.lean'], DEFS)
        self.assertEqual(self.plan['files']['Small/Step.lean'], STEP)

    def test_an_index_that_is_not_of_these_sources_is_refused(self):
        self.index['entries']['Small.unused_two']['span'][0] += 1
        with self.assertRaisesRegex(canon.CanonError, 'the source of Small.unused_two is not the text the index was extracted'):
            package.take(self.index, self.lean, 'Small', 'Small.root', ['Small.Defs'])

    def test_an_attribute_given_by_a_separate_command_keeps_the_element(self):
        target = self.root / 'lean'
        shutil.copytree(self.lean, target)
        path = target / 'Small' / 'Helper.lean'
        path.write_text(path.read_text(encoding='utf-8').replace('\nend Small', '\nattribute [simp] unused_two\n\nend Small'),
                        encoding='utf-8', newline='\n')
        self.assertIn('Small.unused_two', package.take(self.index, target, 'Small', 'Small.root', ['Small.Defs'])['kept'])

    def test_a_theorem_that_is_not_proved_is_not_kept_for_its_attribute(self):
        allowed = ['propext', 'Classical.choice', 'Quot.sound']
        self.assertIn('Small.simp_one', package.take(self.index, self.lean, 'Small', 'Small.root', ['Small.Defs'],
                                                     allowed)['kept'])
        self.index['entries']['Small.simp_one']['axioms'] = ['sorryAx']
        plan = package.take(self.index, self.lean, 'Small', 'Small.root', ['Small.Defs'], allowed)
        self.assertIn('Small.simp_one', plan['removed'])
        self.assertIn('Small.root', plan['kept'])

    def test_a_restore_puts_removed_elements_back_and_nothing_else(self):
        before = {relative: (self.lean / relative).read_text(encoding='utf-8') for relative in self.plan['files']}
        whole = before['Small/Helper.lean']
        back, files, problems = package.restored_files(self.plan['spans'], before, {'Small/Helper.lean': whole})
        self.assertEqual((back, problems), (['Small.unused_two'], []))
        self.assertEqual(files['Small/Helper.lean'], whole)
        for changed, word in ((whole.replace('oddSum 4 = 16', 'oddSum 4 = 17'), 'by more than removed elements'),
                              (whole + '\ntheorem new_one : oddSum 0 = 0 := by\n  rfl\n', 'by more than removed elements')):
            back, files, problems = package.restored_files(self.plan['spans'], before, {'Small/Helper.lean': changed})
            self.assertEqual((back, files), ([], {}))
            self.assertIn(word, problems[0])
        _, _, problems = package.restored_files(self.plan['spans'], before, {'Small/Extra.lean': EXTRA})
        self.assertIn('no file of the taken library', problems[0])


class LibraryCheckTests(FinalizeCase):
    def test_each_fault_of_a_lean_file_and_of_a_definition_module_is_found(self):
        lean = self.root / 'lean'
        shutil.copytree(self.instance / 'canon' / 'lean', lean)
        first = self.instance / 'canon' / 'lean'
        self.assertEqual(package.lean_form_problems(lean) + package.definition_problems(lean, first, ['Small.Defs']), [])
        (lean / 'Small' / 'Plain.lean').write_text('-- a comment\nimport Small.Defs\n', encoding='utf-8')
        (lean / 'Small' / 'Long.lean').write_text('module\n' + '-- line\n' * 10_000, encoding='utf-8')
        (lean / 'Small' / 'Fits.lean').write_text('/- a comment -/\nmodule\n' + '-- line\n' * 9_998, encoding='utf-8')
        problems = package.lean_form_problems(lean)
        self.assertEqual(len(problems), 2, problems)
        self.assertIn('Small/Plain.lean does not begin with `module`', problems)
        self.assertTrue(any('Small/Long.lean has 10001 lines' in problem for problem in problems))
        (lean / 'Small' / 'Defs.lean').write_text(DEFS + '\n-- a comment\n', encoding='utf-8')
        self.assertIn('Small.Defs is not the file of the first commit', package.definition_problems(lean, first, ['Small.Defs'])[0])
        (lean / 'Small' / 'Defs.lean').unlink()
        self.assertIn('is missing', package.definition_problems(lean, first, ['Small.Defs'])[0])

    def test_the_checks_of_an_index_each_find_their_fault(self):
        index = canon.read_index(self.instance / 'canon' / 'index.json')
        hash_ = index['entries']['Small.root']['statement_hash']
        allowed = ['propext', 'Classical.choice', 'Quot.sound']
        records = package.read_records(self.instance / 'canon' / 'records')
        check = lambda changed, given=records, wanted=hash_: package.index_problems(changed, 'Small.root', wanted, allowed, given)
        self.assertEqual(check(index), [])
        self.assertEqual(package.index_problems(index, 'Small.root', hash_, allowed), [])
        self.assertIn('not the statement the instance fixed', check(index, wanted='another')[0])

        def with_entry(name, **changes):
            copy = json.loads(json.dumps(index))
            copy['entries'][name].update(changes)
            return copy

        self.assertIn('Small.helper_zero is not proved from the allowed axioms: sorryAx',
                      check(with_entry('Small.helper_zero', axioms=['sorryAx'], lean_proof='sorry')))
        self.assertTrue(any('not a theorem' in problem for problem in check(with_entry('Small.root', kind='def'))))
        cased = json.loads(json.dumps(index))
        cased['entries']['Small.Helper_zero'] = {**cased['entries']['Small.helper_zero'], 'name': 'Small.Helper_zero'}
        self.assertTrue(any('differ only in the case' in problem for problem in package.index_problems(
            cased, 'Small.root', hash_, allowed)))
        # Records are checked only where they are due.
        lacking = {path: record for path, record in records.items() if path != 'Small/helper_zero'}
        self.assertTrue(any('Small.helper_zero has no record' in problem for problem in check(index, lacking)))
        orphan = {**records, 'Small/gone': records['Small/root']}
        self.assertTrue(any('records/Small/gone.md belongs to no declaration' in problem for problem in check(index, orphan)))
        claim = json.loads(json.dumps(records))
        claim['Small/helper_zero']['meta']['proves'] = 'Small.simp_one'
        self.assertTrue(any('Lean did not confirm' in problem for problem in check(index, claim)))


class RecordTests(FinalizeCase):
    def test_the_list_holds_new_and_changed_elements_and_records_that_name_what_is_gone(self):
        base = canon.read_index(self.instance / 'canon' / 'index.json')
        records = self.root / 'records'
        shutil.copytree(self.instance / 'canon' / 'records', records)
        now = json.loads(json.dumps(base))
        del now['entries']['Small.unused_two'], now['entries']['Small.stray']
        now['entries']['Small.helper_zero']['source_sha'] = 'another'
        now['entries']['Small.fresh'] = {**now['entries']['Small.simp_one'], 'name': 'Small.fresh'}
        todo = {item['declaration']: item for item in package.record_todo(now, base, records)}
        self.assertEqual({name: item['why'] for name, item in todo.items()},
                         {'Small.helper_zero': 'changed', 'Small.fresh': 'new',
                          'Small.named_four': 'names a declaration that is gone'})
        self.assertIsNone(todo['Small.fresh']['record'])
        self.assertEqual(todo['Small.named_four']['record'], 'records/Small/named_four.md')
        self.assertEqual(package.drop_orphans(records, now), ['Small.stray', 'Small.unused_two'])
        self.assertFalse((records / 'Small' / 'stray.md').exists())

    def test_records_follow_renamed_and_removed_declarations(self):
        records = self.root / 'records'
        shutil.copytree(self.instance / 'canon' / 'records', records)
        package.follow_renames(records, {'Small.unused_two': 'Small.Sums.two'}, ['Small.stray'])
        self.assertFalse((records / 'Small' / 'unused_two.md').exists())
        self.assertFalse((records / 'Small' / 'stray.md').exists())
        self.assertIn('first two odd numbers', (records / 'Small' / 'Sums' / 'two.md').read_text(encoding='utf-8'))
        self.assertIn('`Small.Sums.two`', (records / 'Small' / 'named_four.md').read_text(encoding='utf-8'))

    def test_the_cited_sources_are_listed_with_the_records_that_cite_them(self):
        index = canon.read_index(self.instance / 'canon' / 'index.json')
        cited = package.cited(self.instance / 'canon' / 'records', index)
        self.assertEqual([(item['key'], [row['declaration'] for row in item['records']]) for item in cited],
                         [('gauss1801', ['Small.sq_step'])])
        self.assertEqual(package.bibliography_field(BIBLIOGRAPHY, 'gauss1801', 'title'), 'Disquisitiones Arithmeticae')


class RegistryTests(FinalizeCase):
    def first(self):
        folder = self.root / 'first'
        package.export_commit(self.instance, package.first_commit(self.instance, 'HEAD'), ['canon/lean'], folder, 'canon/')
        return folder / 'lean'

    def test_the_challenge_is_the_first_commit_joined_into_one_module_with_the_proof_left_open(self):
        first = self.first()
        self.assertEqual(package.definition_modules(first, 'Small', 'Small.Root'), ['Small.Defs'])
        text = package.challenge_text(first, ['Small.Defs'], 'Small.Root')
        self.assertTrue(text.startswith('module\n'))
        self.assertEqual(text.count('module'), 1)
        self.assertNotIn('import', text)  # the only import was of the definition module, which is now inside
        self.assertLess(text.index('def oddSum'), text.index('theorem root'))
        self.assertIn('theorem root (n : Nat) : oddSum n = n * n := by\n  sorry', text)
        both = package.challenge_text(first, ['Small.Defs'], 'Small.Root', 'Small.sq_step (n : Nat) : oddSum (n + 1) = 7')
        self.assertTrue(both.endswith('\ntheorem Small.sq_step (n : Nat) : oddSum (n + 1) = 7 := by\n  sorry\n'))
        self.assertEqual(package.challenge_measure(text)['fails'], [])
        fails = package.challenge_measure('module\n\nimport Elsewhere.Thing\n' + 'x\n' * 1001)['fails']
        self.assertEqual(len(fails), 2)
        self.assertTrue(any('1004 lines' in fail for fail in fails) and any('Elsewhere.Thing' in fail for fail in fails))

    def frozen(self, compared=('Small.root',), authors=()):
        lean = self.root / 'package' / 'lean'
        shutil.copytree(self.instance / 'canon' / 'lean', lean)
        for name, text in package.build_files('Small', 'odd-squares', None, 'Lean (version 4.99.0, x)', False).items():
            (lean / name).write_text(text, encoding='utf-8')
        config = {**finalize.default_config(), 'authors': list(authors)}
        record = package.read_records(self.instance / 'canon' / 'records')['Small/root']
        data = package.formalization('A title', json.loads(decision()), BIBLIOGRAPHY, config, 'CC-BY-4.0', ['codex/m'],
                                     'Small', list(compared), record, {name: 'Small.Root' for name in compared},
                                     'leanprover/lean4:v4.99.0')
        (lean / 'formalization.yaml').write_text(package.yaml_text(data) + '\n', encoding='utf-8')
        (lean / 'Challenge.lean').write_text(package.challenge_text(self.first(), ['Small.Defs'], 'Small.Root'), encoding='utf-8')
        (lean / 'Solution.lean').write_text(package.solution_text(['Small.Root', 'Small.Step']), encoding='utf-8')
        (lean / 'Check.lean').write_text(package.check_text('Small.Root', ['Small.root', 'Small.sq_step']), encoding='utf-8')
        write_json(lean / 'comparator.json', package.comparator(compared))
        return lean

    def test_the_files_of_the_freeze_have_the_form_the_registry_reads(self):
        lean = self.frozen(compared=('Small.root', 'Small.sq_step'), authors=[{'name': 'A. Author'}])
        self.assertEqual(package.registry_problems(lean, 'CC-BY-4.0'), [])
        self.assertEqual((lean / 'lean-toolchain').read_text(encoding='utf-8'), 'leanprover/lean4:v4.99.0\n')
        lakefile = (lean / 'lakefile.toml').read_text(encoding='utf-8')
        self.assertIn('defaultTargets = ["Small", "Challenge", "Solution"]', lakefile)
        self.assertIn('globs = ["Small.+"]', lakefile)
        self.assertNotIn('[[require]]', lakefile)
        self.assertEqual(read_json(lean / 'lake-manifest.json')['packages'], [])
        self.assertEqual(read_json(lean / 'comparator.json'),
                         {'challenge_module': 'Challenge', 'solution_module': 'Solution',
                          'theorem_names': ['Small.root', 'Small.sq_step'],
                          'permitted_axioms': ['propext', 'Quot.sound', 'Classical.choice']})
        self.assertEqual((lean / 'Solution.lean').read_text(encoding='utf-8'),
                         'module\n\npublic import Small.Root\npublic import Small.Step\n')
        check = (lean / 'Check.lean').read_text(encoding='utf-8')
        self.assertTrue(check.startswith('module\n\nimport Small.Root\n'))
        self.assertIn('#print axioms Small.root\n#check @Small.sq_step\n#print axioms Small.sq_step\n', check)
        data = yaml.safe_load((lean / 'formalization.yaml').read_text(encoding='utf-8'))
        self.assertEqual(data['project'], {'name': 'A title', 'description': 'The first n odd numbers sum to n squared.',
                                           'authors': ['A. Author'], 'license': 'CC-BY-4.0',
                                           'responsible_maintainers': ['A. Author']})
        self.assertEqual(data['classification'], {'arxiv': ['math.CO'], 'msc2020': ['05A15']})
        # The entry that records the result as original carries the selection's grounds for it.
        self.assertEqual(data['sources'][0], {'title': 'The first n odd numbers sum to n squared.', 'type': 'original-proof',
                                              'relationship': 'other',
                                              'note': 'The records name no proof of it and report no search for one.'})
        self.assertEqual(data['sources'][1], {'title': 'Disquisitiones Arithmeticae', 'authors': ['Gauss, Carl Friedrich'],
                                              'id': 'gauss1801', 'relationship': 'background',
                                              'note': 'It has the step in its first section.'})
        self.assertEqual(data['related_formalizations'], [])
        self.assertEqual(package.registry_sources(lean / 'formalization.yaml'), len(data['sources']))
        self.assertEqual(data['review']['status'], 'agent-reviewed')
        # Fidelity is what the selection wrote of the Lean statement, and not the explanation of the root's record.
        self.assertEqual(data['fidelity'], {'divergences': 'The Lean sum starts at index 0; the empty sum is 0.'})
        self.assertIn('No person reviewed', data['review']['notes'])
        self.assertEqual(data['automation']['methods'][0]['method'], 'autonomous')
        self.assertEqual(data['automation']['methods'][0]['framework'], 'do-math')
        # The account of the compared theorem is the root's record, verbatim.
        self.assertEqual(data['status']['scope'], 'For every natural number $n$, $1 + 3 + \\dots + (2n - 1) = n^2$.')
        self.assertEqual([row['lean'] for row in data['alignment']['statements']], ['Small.root', 'Small.sq_step'])

    def test_no_author_means_empty_lists_and_a_configured_review_is_stated_as_it_was(self):
        data = yaml.safe_load((self.frozen() / 'formalization.yaml').read_text(encoding='utf-8'))
        self.assertEqual((data['project']['authors'], data['project']['responsible_maintainers']), ([], []))
        config = {**finalize.default_config(), 'human_review': {'status': 'self-assessed', 'reviewers': ['R.'], 'notes': 'Read.'}}
        data = package.formalization('T', json.loads(decision()), BIBLIOGRAPHY, config, 'CC-BY-4.0', [], 'Small', [], None, {}, 't')
        self.assertEqual(data['review'], {'status': 'self-assessed', 'reviewers': ['R.'], 'notes': 'Read.'})

    def test_a_known_result_lists_the_source_that_the_record_of_the_root_names(self):
        config, known = finalize.default_config(), json.loads(decision())
        known['registry'].update(origin='source-based', sources=[])
        arguments = ('CC-BY-4.0', [], 'Small', [])
        named = {'meta': {'source': 'gauss1801'}, 'sections': {}}
        data = package.formalization('T', known, BIBLIOGRAPHY, config, *arguments, named, {}, 't')
        self.assertEqual([(s['id'], s['title'], s['relationship']) for s in data['sources']],
                         [('gauss1801', 'Disquisitiones Arithmeticae', 'independently-proves')])
        # Without such a record the list stays empty, and a result first proved here does not take the source.
        self.assertEqual(package.formalization('T', known, BIBLIOGRAPHY, config, *arguments, None, {}, 't')['sources'], [])
        first = package.formalization('T', json.loads(decision()), BIBLIOGRAPHY, config, *arguments, named, {}, 't')
        self.assertEqual([s.get('id') for s in first['sources']], [None, 'gauss1801'])
        # The axioms that Lean reports are listed, the standard ones among them, as the format asks.
        self.assertEqual((data['status']['axioms'], package.formalization(
            'T', known, BIBLIOGRAPHY, config, *arguments, named, {}, 't', None, ['Quot.sound', 'propext'])['status']['axioms']),
            ([], ['Quot.sound', 'propext']))
        self.assertIn('It does not say that this work proves it.', data['sources'][0]['note'])
        rooted = package.formalization('T', known, BIBLIOGRAPHY, config, 'CC-BY-4.0', [], 'Small', ['Small.root'], named,
                                       {'Small.root': 'Small.Root'}, 't')
        self.assertIn('The record of `Small.root`, `records/Small/root.md`, names this work', rooted['sources'][0]['note'])
        # A compared theorem is aligned with the statement of its own record.
        both = package.formalization('T', known, BIBLIOGRAPHY, config, 'CC-BY-4.0', [], 'Small', ['Small.root', 'Small.a'],
                                     named, {'Small.root': 'Small.Root', 'Small.a': 'Small.A'}, 't', {'Small.a': 'The step.'})
        self.assertEqual([row['source'] for row in both['alignment']['statements']],
                         ['The first n odd numbers sum to n squared.', 'The step.'])
        self.assertEqual(first['sources'][1]['relationship'], 'background')

    def test_a_source_carries_the_identifier_of_its_entry_and_the_note_of_the_selection(self):
        bibliography = ('@article{a1,\n  title = {One},\n  doi = {10.1000/1},\n  eprint = {2501.00001}\n}\n'
                        '@misc{a2,\n  title = {Two},\n  eprint = {2501.00002},\n  url = {https://example.org/two}\n}\n'
                        '@misc{a3,\n  title = {Three},\n  url = {https://example.org/three}\n}\n')
        earlier = [{'id': 'https://example.org/formal', 'relationship': 'independent', 'note': 'In another prover.'}]
        chosen = json.loads(decision())
        chosen['registry'].update(origin='source-based', related_formalizations=earlier, sources=[
            {'key': 'a1', 'relationship': 'formalizes', 'note': 'Theorem 1.'},
            {'key': 'a2', 'relationship': 'background', 'note': 'It poses the question.'},
            {'key': 'a3', 'relationship': 'other', 'note': 'A table of values.'}])
        data = package.formalization('T', chosen, bibliography, finalize.default_config(), 'CC-BY-4.0', [], 'Small', [],
                                     None, {}, 't')
        self.assertEqual([(s['id'], s['note']) for s in data['sources']],
                         [('doi:10.1000/1', 'Theorem 1.'), ('arXiv:2501.00002', 'It poses the question.'),
                          ('https://example.org/three', 'A table of values.')])
        self.assertEqual(yaml.safe_load(package.yaml_text(data))['related_formalizations'], earlier)
        # The README lists the works and the earlier formal proofs as the registry's file does, under the result.
        path = self.root / 'formalization.yaml'
        package.write_text(path, package.yaml_text(data) + '\n')
        lines = package.provenance_lines(package.provenance(chosen['registry'], path))
        self.assertEqual(lines[:5], ['### Where the result comes from', '',
                                     'The identity is classical; the records name nobody who posed it.', '',
                                     'In `lean/formalization.yaml`, the file that describes the package for a '
                                     'formal-proof registry, the result is recorded as source-based, which there means a '
                                     'result that was presented elsewhere before. The records name no proof of it and '
                                     'report no search for one.'])
        self.assertIn('- One (doi:10.1000/1). The library formalises the result of this work. Theorem 1.', lines)
        self.assertIn('- Three (https://example.org/three). A table of values.', lines)
        self.assertIn('- https://example.org/formal. In another prover.', lines)
        # A decision that was made before these texts were asked for has no such part.
        self.assertIsNone(package.provenance({'origin': 'original'}, path))

    def test_each_rule_of_the_registry_that_the_pipeline_controls_is_checked(self):
        lean = self.frozen()

        def broken(change):
            copy = self.root / ('copy-' + str(len(list(self.root.iterdir()))))
            shutil.copytree(lean, copy)
            change(copy)
            return package.registry_problems(copy, 'CC-BY-4.0')

        def edit_json(name, **changes):
            def change(copy):
                write_json(copy / name, {**read_json(copy / name), **changes})
            return change

        def edit_yaml(path, value):
            def change(copy):
                data = yaml.safe_load((copy / 'formalization.yaml').read_text(encoding='utf-8'))
                target = data
                for key in path[:-1]:
                    target = target[key]
                target[path[-1]] = value
                (copy / 'formalization.yaml').write_text(package.yaml_text(data) + '\n', encoding='utf-8')
            return change

        cases = [(lambda copy: (copy / 'Solution.lean').unlink(), 'lean/Solution.lean is missing'),
                 (lambda copy: (copy / 'lakefile.lean').write_text('module\n', encoding='utf-8'), 'exactly one'),
                 (lambda copy: (copy / 'Small' / 'Step.lean').write_text('import Small.Defs\n', encoding='utf-8'),
                  'Small/Step.lean does not begin with `module`'),
                 (edit_json('comparator.json', extra=1), 'keys the registry does not accept: extra'),
                 (edit_json('comparator.json', theorem_names=[]), 'names no theorem'),
                 (edit_json('comparator.json', permitted_axioms=['propext', 'sorryAx']), 'other axioms than the three'),
                 (edit_yaml(['project', 'name'], 'x' * 301), 'project.name'),
                 (edit_yaml(['project', 'description'], ''), 'project.description'),
                 (edit_yaml(['project', 'license'], 'MIT'), 'project.license'),
                 (edit_yaml(['classification', 'arxiv'], []), 'classification.arxiv'),
                 (edit_yaml(['classification', 'msc2020'], ['5A15']), 'classification.msc2020'),
                 (edit_yaml(['sources'], [{'title': 'T', 'relationship': 'inspired'}]), 'each entry of sources'),
                 (edit_yaml(['automation', 'methods'], []), 'automation.methods'),
                 (edit_yaml(['review', 'status'], ''), 'review.status')]
        for change, wanted in cases:
            problems = broken(change)
            self.assertEqual(len(problems), 1, (wanted, problems))
            self.assertIn(wanted, problems[0])

    def test_the_build_files_come_from_the_lake_project_of_the_lean_environment(self):
        project = self.root / 'project'
        packages = project / '.lake' / 'packages' / 'mathlib'
        packages.mkdir(parents=True)
        (project / 'lean-toolchain').write_text('leanprover/lean4:v4.36.0\n', encoding='utf-8')
        (project / 'lakefile.toml').write_text('name = "env"\n\n[[require]]\nname = "mathlib"\nrev = "v4.36.0"\n\n'
                                               '[[lean_lib]]\nname = "Env"\n', encoding='utf-8')
        git = lambda *arguments: subprocess.run(['git', '-C', str(packages), '-c', 'user.name=t', '-c', 'user.email=t@t',
                                                 *arguments], check=True, capture_output=True, text=True).stdout.strip()
        git('init')
        (packages / 'file').write_text('x', encoding='utf-8')
        git('add', 'file')
        git('commit', '-m', 'one')
        head = git('rev-parse', 'HEAD')
        entry = {'name': 'mathlib', 'type': 'git', 'rev': head, 'inputRev': 'v4.36.0', 'inherited': False}
        write_json(project / 'lake-manifest.json', {'version': '1.3.0', 'packagesDir': '.lake/packages', 'packages': [entry]})
        self.assertEqual(package.lake_project({'lean': {'cwd': str(project)}}), project)
        self.assertIsNone(package.lake_project({'lean': {'cwd': None}}))
        files = package.build_files('Small', 'odd', project, None, True)
        self.assertEqual(files['lean-toolchain'], 'leanprover/lean4:v4.36.0\n')
        self.assertIn('[[require]]\nname = "mathlib"\nrev = "v4.36.0"\n', files['lakefile.toml'])
        self.assertNotIn('"Env"', files['lakefile.toml'])
        self.assertIn('globs = ["Small.*"]', files['lakefile.toml'])  # the library has a top module
        manifest = json.loads(files['lake-manifest.json'])
        self.assertEqual((manifest['packages'], manifest['packagesDir']), ([entry], '.lake/packages'))
        # Before Lake runs: every package stands at the manifest's revision, or Lake would fetch it.
        self.assertEqual(package.packages_problems(manifest, project / '.lake' / 'packages'), [])
        stale = {'packages': [{**entry, 'rev': 'f' * 40}, {**entry, 'name': 'absent'}]}
        problems = package.packages_problems(stale, project / '.lake' / 'packages')
        self.assertEqual(len(problems), 2)
        self.assertIn('mathlib is not at ffffffffffff', problems[0])
        self.assertIn('found: nothing', problems[1])

    def test_the_lake_program_is_the_one_of_the_lean_command(self):
        self.assertEqual(package.lake_command({'lean': {'command': ['C:/t/bin/lake.exe', 'env', 'lean']}}), ['C:/t/bin/lake.exe'])
        beside = package.lake_command({'lean': {'command': [str(Path('C:/t/bin/lean.exe'))]}})
        self.assertEqual(Path(beside[0]), Path('C:/t/bin/lake.exe'))

    def test_the_axioms_are_read_from_what_lean_prints(self):
        printed = ("Small.root (n : Nat) : x\n'Small.root' depends on axioms: [propext,\n Classical.choice,\n Quot.sound]\n"
                   "'Small.clean' does not depend on any axioms\n'Small.open' depends on axioms: [sorryAx]\n")
        self.assertEqual(package.axioms_printed(printed), {'Small.root': ['propext', 'Classical.choice', 'Quot.sound'],
                                                           'Small.clean': [], 'Small.open': ['sorryAx']})


class ArchiveTests(FinalizeCase):
    def test_the_archive_is_the_commit_with_the_account_name_replaced_and_the_ledger_points_into_it(self):
        commit = package.head_commit(self.instance)
        # A word that stands in paths and in files of the research plays the account name.
        info = package.knowledge_archive(self.instance, commit, self.root / 'knowledge', 'odd', 'Small')
        archive = self.root / 'knowledge' / 'odd-knowledge.tar.xz'
        members = package.archive_members(archive)
        tree = {}
        for line in package.git_run(self.instance, 'ls-tree', '-r', '-z', commit, '--', 'canon', 'knowledge').split(b'\0'):
            if line:
                head, path = line.split(b'\t', 1)
                tree[path.decode('utf-8')] = head.decode().split()[2]
        blob = lambda data: hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        self.assertEqual({path.replace('<account>', 'Small'): blob(data.replace(b'<account>', b'Small'))
                          for path, data in members.items()}, tree)
        self.assertFalse(any(b'Small' in data or 'Small' in path for path, data in members.items()))
        self.assertIn('canon/lean/<account>/Defs.lean', members)
        touched = sum(b'<account>' in data or '<account>' in path for path, data in members.items())
        self.assertEqual((info['files'], info['touched']), (len(tree), touched))
        self.assertGreater(touched, 0)
        manifest = (self.root / 'knowledge' / 'MANIFEST.md').read_text(encoding='utf-8')
        self.assertEqual(package.manifest_sha(self.root / 'knowledge' / 'MANIFEST.md'), package.sha256_file(archive))
        self.assertIn(f'{touched} files were touched', manifest)
        self.assertIn(commit, manifest)
        # The same commit gives the same archive.
        again = package.knowledge_archive(self.instance, commit, self.root / 'again', 'odd', 'Small')
        self.assertEqual(again['sha256'], info['sha256'])
        rows = package.ledger({path: data for path, data in members.items()
                               if path.startswith(('knowledge/', 'canon/approaches/', 'canon/questions/'))})
        self.assertEqual([(row['event'], row['kind']) for row in rows], [(1, 'change'), (2, 'question')])
        self.assertEqual(rows[0]['title'], 'A contribution')
        self.assertEqual(rows[0]['review'], 'Useful work.')
        self.assertEqual(rows[0]['contribution'], 'Closed what it took on.')
        self.assertIn('<account>.sq_step', rows[0]['elements'])
        self.assertTrue(all(row['record'] in members for row in rows))
        self.assertEqual(rows[1]['record'], 'canon/questions/q0.md')
        beside = package.event_members(rows[0], list(members))
        self.assertIn(rows[0]['record'], beside)
        self.assertTrue(all(name.startswith(rows[0]['record'].rsplit('/', 1)[0] + '/') for name in beside))
        self.assertIn('by', rows[0])
        self.assertEqual(rows[1]['by'], '')
        # What was tried on a statement that was proved later stands in the canon's history, and is a line too.
        tried = package.ledger({'canon/history/Small/root/000001-approaches/by-induction.md':
                                b'---\ntitle: Induction on n\n---\n## Idea\n\nInduct.\n',
                                'canon/history/Small/root/000001-record.md': b'An earlier record.\n'})
        self.assertEqual([(row['kind'], row['title'], row['elements'], row['record']) for row in tried],
                         [('approach', 'Induction on n', ['Small.root'],
                           'canon/history/Small/root/000001-approaches/by-induction.md')])
        listed = [{'group': 'Steps', 'items': ['`Small.sq_step`:  the step of the square']},
                  {'group': '', 'items': ['`Small.twice`: doubling']}]
        text = package.timeline([{**rows[0], 'text': 'A change   gave the root its proof.', 'list': listed},
                                 {**rows[1], 'text': 'The question was understood.'}], 'Small.root')
        # One heading for each entry: a publication by its number, date and kind; then the text, the list, the record.
        head = ' \u00b7 '.join(part for part in (str(rows[0]['event']), rows[0]['date'], 'change') if part)
        self.assertIn('### ' + head + '\n\nA change gave the root its proof.\n\n'
                      '- **Steps**\n  - `Small.sq_step`: the step of the square\n- `Small.twice`: doubling\n\n'
                      f"Record: `{rows[0]['record']}`\n", text)
        self.assertIn('### Question `q0`\n\nThe question was understood.\n\nRecord: `canon/questions/q0.md`\n', text)
        # An entry beyond the form is refused: too long a text, too long an item, a list that is no list of groups.
        self.assertEqual(package.entry_problems(1, 'Short.', listed), [])
        self.assertIn('121 words', package.entry_problems(1, 'word ' * 121, [])[0])
        self.assertIn('more than 30 words', package.entry_problems(1, 'Short.', [{'group': '', 'items': ['w ' * 31]}])[0])
        self.assertIn('array of groups', package.entry_problems(1, 'Short.', ['an item'])[0])
        self.assertLess(text.index('Publications'), text.index('What was understood of each question'))

    def test_a_working_tree_that_differs_from_the_commit_does_not_reach_the_archive(self):
        commit = package.head_commit(self.instance)
        path = self.instance / 'canon' / 'questions' / 'q0.md'
        committed = path.read_bytes()
        path.write_bytes(b'Changed after the commit.\r\n')
        package.knowledge_archive(self.instance, commit, self.root / 'knowledge', 'odd', 'nobody-of-this-name')
        members = package.archive_members(self.root / 'knowledge' / 'odd-knowledge.tar.xz')
        self.assertEqual(members['canon/questions/q0.md'], committed)


class DocumentTests(FinalizeCase):
    def packed(self):
        """A small package with every kind of file the final check reads."""
        folder = self.root / 'package'
        for relative, text in (('lean/Small/Defs.lean', DEFS), ('lean/lakefile.toml', 'name = "x"\n'),
                               ('records/Small/root.md', 'A record.\n'), ('history/timeline.md', '# History\n'),
                               ('README.md', '# Title\n\n[the timeline](history/timeline.md) and [a site](https://example.org/a)\n'),
                               ('dependency-map/dependency_map.html', '<a href="dependency_map.svg">map</a>\n'),
                               ('dependency-map/dependency_map.svg', '<svg/>\n')):
            (folder / relative).parent.mkdir(parents=True, exist_ok=True)
            (folder / relative).write_text(text, encoding='utf-8', newline='\n')
        package.knowledge_archive(self.instance, package.head_commit(self.instance), folder / 'knowledge', 'odd', 'no-such-account')
        freeze = package.freeze_hashes(folder)
        (folder / 'MANIFEST.sha256').write_text(package.manifest_text(folder), encoding='utf-8', newline='\n')
        return folder, freeze

    def test_a_package_that_stands_alone_passes_and_each_fault_is_found(self):
        folder, freeze = self.packed()
        work = self.root / 'work-folder'
        check = lambda account='no-such-account': package.standalone_problems(folder, work, account, freeze)
        self.assertEqual(check(), [])

        def faulty(relative, text, wanted, account='no-such-account', manifest=True):
            path = folder / relative
            before = path.read_bytes() if path.exists() else None
            path.write_text(text, encoding='utf-8', newline='\n')
            listing = (folder / 'MANIFEST.sha256').read_bytes()
            if manifest:
                (folder / 'MANIFEST.sha256').write_text(package.manifest_text(folder), encoding='utf-8', newline='\n')
            problems = check(account)
            self.assertTrue(any(wanted in problem for problem in problems), (wanted, problems))
            path.write_bytes(before) if before is not None else path.unlink()
            (folder / 'MANIFEST.sha256').write_bytes(listing)
            self.assertEqual(check(), [])
            return problems

        faulty('README.md', '[gone](history/absent.md)\n', 'README.md: the link history/absent.md does not resolve')
        faulty('README.md', '[out](../outside.md)\n', 'the link ../outside.md does not resolve inside the package')
        faulty('dependency-map/dependency_map.html', '<img src="missing.svg">\n', 'the link missing.svg')
        faulty('history/timeline.md', 'Run by pat on the machine.\n', 'history/timeline.md holds the account name', account='pat')
        # In a document a colon before a backslash is a formula, so a drive path is found there by its form with a slash.
        faulty('README.md', 'Built in C:/Users/someone/lean.\n', 'README.md holds a drive path')
        faulty('lean/lakefile.toml', "path = 'C:\\Users\\someone\\lean'\n", 'lean/lakefile.toml holds a drive path')
        faulty('lean/lakefile.toml', f'path = "{work.as_posix()}/stage"\n', "holds the work folder's path")
        faulty('lean/Small/Defs.lean', DEFS + '-- changed after the freeze\n', 'lean/ is not what the freeze hashed: lean/Small/Defs.lean')
        faulty('records/Small/new.md', 'A record added after the freeze.\n', 'records/ is not what the freeze hashed')
        faulty('history/timeline.md', '# Another history\n', 'MANIFEST.sha256 does not hold for history/timeline.md', manifest=False)
        faulty('history/unlisted.md', 'x\n', 'MANIFEST.sha256 has no line for history/unlisted.md', manifest=False)
        faulty('history/timeline.md', '# The history\r\n\r\nOne entry.\r\n', 'history/timeline.md has line endings other than LF')
        # A file that is no text, as the typeset paper is, is not read for its line endings.
        (folder / 'paper').mkdir(exist_ok=True)
        (folder / 'paper' / 'paper.pdf').write_bytes(b'%PDF-1.5\r\n%\xd0\xd4\xc5\xd8\r\n')
        (folder / 'MANIFEST.sha256').write_text(package.manifest_text(folder), encoding='utf-8', newline='\n')
        self.assertEqual(check(), [])
        # A formula with a colon before a command is no drive path, in a document and in the source of the paper.
        formula = 'A map $f:\\mathbb{N}\\to\\mathbb{N}$ and the set $X:\\ M$.\n'
        (folder / 'README.md').write_text('# Title\n\n' + formula, encoding='utf-8', newline='\n')
        (folder / 'paper' / 'paper.tex').write_text(formula, encoding='utf-8', newline='\n')
        (folder / 'MANIFEST.sha256').write_text(package.manifest_text(folder), encoding='utf-8', newline='\n')
        self.assertEqual(check(), [])
        # A member of the archive that holds the account name is found inside the archive.
        problems = check('oddSum')
        self.assertTrue(any('the member canon/lean/Small/Defs.lean holds the account name' in problem for problem in problems))
        # A drive path in a file the pipeline did not write, such as a record of the research, is not its concern.
        (folder / 'records' / 'Small' / 'root.md').write_text('Computed in D:\\data.\n', encoding='utf-8', newline='\n')
        freeze = package.freeze_hashes(folder)
        (folder / 'MANIFEST.sha256').write_text(package.manifest_text(folder), encoding='utf-8', newline='\n')
        self.assertEqual(package.standalone_problems(folder, work, 'no-such-account', freeze), [])

    def test_a_file_the_pipeline_writes_ends_its_lines_with_a_line_feed(self):
        path = self.root / 'written.md'
        package.write_text(path, 'One line.\r\nAnother.\r\n')
        self.assertEqual(path.read_bytes(), b'One line.\nAnother.\n')

    def test_placeholders_are_filled_from_the_facts_and_an_unknown_key_is_named(self):
        self.assertEqual(package.fill('In {{facts.modules}} modules and {{facts.lines}} lines.', {'modules': 4, 'lines': 90}),
                         ('In 4 modules and 90 lines.', []))
        self.assertEqual(package.fill('In {{facts.pages}} pages.', {'modules': 4}), ('In {{facts.pages}} pages.', ['pages']))

    def test_the_entry_goes_under_solved_problems_once(self):
        readme = self.root / 'README.md'
        readme.write_text('# R\n\n## Solved problems\n\n- An earlier one.\n\n## Other\n\nText.\n', encoding='utf-8')
        entry = '- [T](solved/odd/README.md): S.'
        self.assertTrue(package.add_solved_entry(readme, 'odd', entry))
        self.assertEqual(readme.read_text(encoding='utf-8'),
                         '# R\n\n## Solved problems\n\n- An earlier one.\n' + entry + '\n\n## Other\n\nText.\n')
        self.assertFalse(package.add_solved_entry(readme, 'odd', entry))
        bare = self.root / 'bare.md'
        bare.write_text('# R\n', encoding='utf-8')
        package.add_solved_entry(bare, 'odd', entry)
        self.assertEqual(bare.read_text(encoding='utf-8'), '# R\n\n## Solved problems\n\n' + entry + '\n')


class PaperRunTests(FinalizeCase):
    def test_a_folder_that_holds_a_run_of_the_paper_command_is_continued_as_that_command_continues_it(self):
        run = finalize.Run(self.instance, 'odd', {**finalize.default_config(), 'parallel': 3, 'tex': ['tex']})
        out = self.root / 'paper'
        session = {'event': 'session', 'kind': 'write'}

        def called(log=None, materials=True):
            if out.exists():
                shutil.rmtree(out)
            if log is not None:
                out.mkdir()
                write_json(out / 'log.json', log)
                if materials:
                    write_json(out / 'materials.json', {})
            with patch('finalize.produce', return_value=7) as made, patch('paper.close_open', return_value=9) as acted:
                code = run.paper_run(self.root / 'view', out, from_draft=self.root / 'draft')
            return code, made.call_args, acted.call_args

        code, made, acted = called()
        self.assertEqual((code, acted), (7, None))
        self.assertEqual(made.kwargs, {'tex': ['tex'], 'parallel': 3, 'resume': False, 'gate': run.gate,
                                       'from_draft': self.root / 'draft'})
        # Stopped in the middle, or ended as a failure: resumed.
        for log in ([session], [session, {'event': 'end', 'status': 'failed', 'error': 'x'}]):
            code, made, acted = called(log)
            self.assertEqual((code, acted, made.kwargs['resume']), (7, None, True))
        # Ended with findings left open: the paper command closes them without a person, and stage 4 is judged by
        # that exit code.
        code, made, acted = called([session, {'event': 'end', 'status': 'open_findings', 'open': [{'check': 'c'}]}])
        self.assertEqual((code, made), (9, None))
        self.assertEqual(acted.args, (self.root / 'view', out, ['tex'], None, 3))
        # Ended with its manuscript failing the typesetting: nothing takes that run up, and the paper is written anew.
        code, made, acted = called([session, {'event': 'end', 'status': 'open_findings',
                                              'open': [{'check': paper.TYPESETTING, 'problems': ['x']}]}])
        self.assertEqual((code, acted, made.kwargs['resume'], out.exists()), (7, None, False, False))
        # A run that comes to its end with open findings while this command runs is closed in the same way.
        ending = [session, {'event': 'end', 'status': 'open_findings', 'open': [{'check': 'c'}]}]

        def produced(view, folder, **options):
            folder.mkdir()
            write_json(folder / 'log.json', ending)
            return 2

        shutil.rmtree(out, ignore_errors=True)
        with patch('finalize.produce', side_effect=produced), patch('paper.close_open', return_value=0) as acted:
            self.assertEqual(run.paper_run(self.root / 'view', out), 0)
        self.assertEqual(acted.call_args.args, (self.root / 'view', out, ['tex'], None, 3))
        # Ended without them: done, and nothing is launched.
        for status in ('complete', 'draft'):
            self.assertEqual(called([session, {'event': 'end', 'status': status, 'open': []}]), (0, None, None))
        # A folder that holds something else is cleared and the run begins anew.
        code, made, acted = called([], materials=False)
        self.assertEqual((code, made.kwargs['resume'], out.exists()), (7, False, False))


class PromptTests(FinalizeCase):
    def prepared(self):
        run = finalize.Run(self.instance, 'odd', finalize.default_config())
        run.settings, run.library, run.root, run.expect_mb = {'lean': {'cwd': None}}, 'Small', 'Small.root', 64
        run.state = {'main': 'Small.sq_step'}
        return run

    def test_every_instruction_file_of_the_skill_is_filled_with_the_names_the_command_gives(self):
        run = self.prepared()
        common = package.read_text(INSTALLED / 'finalize' / 'common.md')
        for name in INSTRUCTIONS:
            text = run.prompt(name, {'part': 'core'} if name in ('simplify', 'foldback') else None)
            self.assertEqual(finalize.PLACEHOLDER.findall(text), [], name)
            self.assertTrue(text.startswith(common.split('{{')[0]), name)
            self.assertIn(Path(sys.executable).as_posix(), text)
            self.assertIn(INSTALLED.as_posix() + '/runtime/lean_broker.py', text)
            self.assertIn('--expect-mb 64', text)
        self.assertIn('There is none', run.prompt('review'))
        run.settings = {'lean': {'cwd': 'C:/toolchains/mathlib'}}
        self.assertIn('C:/toolchains/mathlib', run.prompt('review'))

    def test_a_name_the_command_does_not_give_stops_the_run_and_is_named(self):
        (self.skill / 'finalize' / 'review.md').write_text('Review {{library}} in {{folder}}.\n', encoding='utf-8')
        with patch('finalize.SKILL', self.skill), self.assertRaises(paper.Stop) as raised:
            self.prepared().prompt('review')
        self.assertIn('review.md uses {{folder}}', str(raised.exception))


# ----------------------------------------------------------------------------- the command

class RefusalTests(FinalizeCase):
    def refused(self, wanted, **options):
        self.assertEqual(self.run_command(script(), **options), 1)
        self.assertIn(wanted, self.said)
        self.assertFalse((self.work / 'state.json').exists())
        self.assertEqual(self.calls(), [])

    def test_what_cannot_be_packaged_is_refused_before_any_work(self):
        self.refused('does not name a package', config=self.config(), name='Odd_Squares')
        self.refused('unknown configuration key: author', config=self.config(author='A'))
        self.refused('"parallel" is the number of sessions', config={'parallel': 0})
        self.refused('no licence text for MIT', config=self.config(licence='MIT'))
        with patch.dict(sys.modules, {'yaml': None}):
            self.refused('has no PyYAML', config=self.config())
        self.refused('was not found', config={'tex': ['no-such-tex-command']})
        self.solved.mkdir(parents=True)
        self.refused('exists', config=self.config())
        self.solved.rmdir()
        write_json(self.instance / 'settings.json', {**read_json(self.instance / 'settings.json'), 'no_such_setting': 1})
        self.refused('the settings of the instance are not valid: unknown setting: no_such_setting', config=self.config())
        self.assertFalse(self.work.exists())
        remove_tree(self.instance / '.git')
        self.refused('is not an instance of this runtime with a Git repository', config=self.config())

    def test_a_root_that_is_not_proved_formally_is_refused(self):
        self.instance = self.root / 'pristine'  # the instance as it was created: its root has no proof
        shutil.copytree(template(), self.instance)
        self.refused('the root is unresolved', config=self.config())

    def test_a_lean_environment_that_does_not_answer_is_refused(self):
        self.configure(lean={'version_command': [sys.executable, '-c', 'raise SystemExit(3)']})
        self.refused('does not answer its version command', config=self.config())

    def test_the_settings_are_the_working_file_and_the_research_is_the_commit(self):
        # The committed settings hold a key the runtime refuses; the working file is valid. The working tree of the
        # canon was changed after the commit; the run reads the commit.
        valid = (self.instance / 'settings.json').read_bytes()
        write_json(self.instance / 'settings.json', {**json.loads(valid), 'no_such_setting': 1})
        subprocess.run(['git', '-C', str(self.instance), '-c', 'user.name=t', '-c', 'user.email=t@t', 'commit', '-am', 'stale'],
                       check=True, capture_output=True)
        (self.instance / 'settings.json').write_bytes(valid)
        self.configure(lean={'min_free_memory_mb': 1_000_000})
        (self.instance / 'canon' / 'lean' / 'Small' / 'Step.lean').write_text(STEP + '-- fail: changed after the commit\n',
                                                                            encoding='utf-8')
        self.assertEqual(self.run_command(script(review=[{}]), config=self.config(), operating=False), 2)
        settings = read_json(self.work / 'settings.json')
        self.assertEqual(set(settings['lean']), {'command', 'version_command', 'cwd', 'env', 'cache_epoch', 'allowed_axioms'})
        self.assertNotIn('no_such_setting', settings)
        self.assertEqual((self.work / 'source' / 'canon' / 'lean' / 'Small' / 'Step.lean').read_text(encoding='utf-8'), STEP)
        self.assertEqual(read_json(self.work / 'state.json')['run']['commit'], package.head_commit(self.instance))
        # The first commit holds the definition module and the root as it was posed.
        self.assertEqual((self.work / 'first' / 'lean' / 'Small' / 'Root.lean').read_text(encoding='utf-8'), ROOT)
        self.assertEqual(read_json(self.work / 'state.json')['definitions'], ['Small.Defs'])
        self.assertIn('2.1-take', read_json(self.work / 'state.json')['steps'])  # the build ran with the reduced settings
        # The run's compile service is its own, and began with what the instance's had compiled.
        cached = {path.name for path in (self.instance / 'runner' / 'lean' / 'cache').iterdir()}
        self.assertTrue(cached)
        self.assertLessEqual(cached, {path.name for path in (self.work / 'runner' / 'lean' / 'cache').iterdir()})
        self.assertTrue((self.work / 'runner' / 'lean' / 'broker.log').is_file())


class RunTests(FinalizeCase):
    def test_a_run_comes_to_its_end_with_the_package_in_place(self):
        config = self.config(authors=[{'name': 'A. Author', 'email': 'a@example.org', 'orcid': '0000'}])
        self.assertEqual(self.run_command(script(), config=config), 0, self.said)
        # The order of the stages is the program's: each step of the library stage after the one before it.
        steps = self.steps()
        main = [step for step in steps if not step.startswith('3-')]
        self.assertEqual(main, ['1-selection', '2.1-take', '2.2-review', '2.3-simplify', '2.4-merge', '2.4-arrange',
                                '2.5-records', '2.6-draft', '2.6-foldback', '2.6-records', '2.6-compare', '2.7-freeze',
                                '4-map', '4-paper', '5-documents', '6-check'])
        self.assertLess(steps.index('3-archive'), steps.index('3-history'))
        self.assertLess(steps.index('3-history'), steps.index('5-documents'))
        kinds = [call['kind'] for call in self.calls() if call['kind'] not in ('history-write', 'history-read', 'simplify')]
        self.assertEqual(kinds, ['selection', 'selection-read', 'review', 'arrange', 'records-write', 'records-compare',
                                 'sources', 'foldback', 'records-write', 'records-compare', 'draft-compare', 'readme-write',
                                 'package-read'])
        # One part was accepted at once. The other was tried twice and discarded: its first session left a report that
        # does not parse, and the second, which was told so, left a module that does not compile.
        self.assertEqual(sorted(call['section'] for call in self.calls('simplify')), ['aux', 'aux', 'core'])
        self.assertIn('output/report.json is not JSON', [call for call in self.calls('simplify')
                                                       if call['section'] == 'aux'][1]['prompt'])
        self.assertIn('this simplification does not compile', self.decisions())
        self.assertEqual([call['kind'] for call in self.calls() if call['kind'].startswith('history')],
                         ['history-write', 'history-read'])

        # What each session was given, by the table of the design.
        given = {call['kind'] + ':' + str(call['section']): set(call['given']) for call in self.calls()}
        library = {'lean/Small/Defs.lean', 'lean/Small/Root.lean', 'lean/Small/Step.lean', 'lean/Small/Helper.lean'}
        self.assertLessEqual({'digest.md', 'root.md', 'index.json', 'canon/lean/Small/Extra.lean', 'canon/records/Small/root.md',
                              'canon/questions/q0.md', 'canon/bibliography.bib'}, given['selection:None'])
        self.assertLessEqual({'decision.json', 'digest.md', 'canon/lean/Small/Root.lean'}, given['selection-read:None'])
        self.assertLessEqual(library | {'records/Small/root.md', 'rests-on.md'}, given['review:None'])
        self.assertNotIn('lean/Small/Extra.lean', given['review:None'])  # the take deleted the module
        self.assertLessEqual(library | {'part.json'}, given['simplify:core'])
        self.assertLessEqual(library | {'review.json', 'reports/core.json', 'declarations.md'}, given['arrange:None'])
        self.assertNotIn('reports/aux.json', given['arrange:None'])
        self.assertLessEqual(library | {'todo.json', 'records/Small/root.md', 'bibliography.bib', 'records-format.md',
                                        'user-writing-preferences.md'}, given['records-write:5-01'])
        self.assertLessEqual(library | {'todo.json', 'records/Small/added_six.md', 'records-format.md'},
                             given['records-compare:5-01'])
        self.assertLessEqual({'bibliography.bib', 'cited.json', 'requests.json', 'records/Small/sq_step.md'}, given['sources:5'])
        self.assertLessEqual(library | {'part.json', 'items.json', 'records/Small/added_six.md'}, given['foldback:Small'])
        self.assertLessEqual({'rows.json', 'lean/Small/Step.lean', 'records/Small/sq_step_strict.md'}, given['draft-compare:None'])
        self.assertLessEqual({'ledger.json'}, given['history-write:01'])
        self.assertTrue(any(name.startswith('archive/knowledge/changes/') for name in given['history-write:01']))
        self.assertIn('archive/canon/questions/q0.md', given['history-write:01'])
        self.assertLessEqual({'entries.json', 'archive/canon/questions/q0.md'}, given['history-read:01'])
        self.assertNotIn('ledger.json', given['history-read:01'])
        self.assertLessEqual({'facts.json', 'introduction.tex', 'account.md', 'timeline.md'}, given['readme-write:None'])
        reader = given['package-read:None']
        self.assertLessEqual({'package/README.md', 'package/LICENSE', 'package/lean/Challenge.lean', 'package/paper/paper.pdf',
                              'package/knowledge/MANIFEST.md', 'package/history/timeline.md'}, reader)
        self.assertNotIn('package/knowledge/odd-knowledge.tar.xz', reader)
        self.assertFalse(any(not name.startswith(('package/', 'prompt.txt', 'session.json')) for name in reader), reader)
        prompts = {call['kind'] + ':' + str(call['section']): call['prompt'] for call in self.calls()}
        self.assertIn(f'work {self.work.as_posix()}, skill {self.skill.as_posix()}', prompts['selection:None'])
        self.assertIn('Instruction selection for Small.root, main .', prompts['selection:None'])
        self.assertIn('Instruction review for Small.root, main Small.sq_step.', prompts['review:None'])
        self.assertIn('Simplify the part core.', prompts['simplify:core'])

        # The paper command was called twice, in this process, on views, with the run's one semaphore.
        draft, written = self.produced
        self.assertEqual((draft['instance'], draft['out'], draft['draft'], draft['root_state']), ('4', 'draft', True, 'formal_proved'))
        self.assertEqual((written['instance'], written['out'], written['draft'], written['root_state']),
                         ('frozen', 'paper', False, 'formal_proved'))
        self.assertIsInstance(draft['gate'], type(threading.BoundedSemaphore()))
        self.assertIs(draft['gate'], written['gate'])
        self.assertEqual((draft['parallel'], written['parallel']), (2, 2))
        # Both are given the main theorem that the selection chose, which is not the root here.
        self.assertEqual((draft['main'], written['main']), ('Small.sq_step', 'Small.sq_step'))
        self.assertEqual(written['title_page'], {'authors': [{'name': 'A. Author', 'email': 'a@example.org'}]})
        # Before --from-draft reads the draft, it was brought to the library.
        drafted = written['drafted']
        step = next(item for item in drafted['statements'] if item['label'] == 'lem:step')
        self.assertEqual((step['text'], step['element']), ('For every $n$, $s(n) < s(n+1)$.', 'Small.sq_step_strict'))
        self.assertEqual(drafted['gaps'][0]['closed_by'], 'Small.sq_step_strict')
        self.assertEqual(drafted['statements'][0], DRAFT['statements'][0])

        # The package.
        package_files = set(package.files_under(self.solved))
        self.assertLessEqual({'README.md', 'LICENSE', 'MANIFEST.sha256', 'lean/lean-toolchain', 'lean/lakefile.toml',
                              'lean/lake-manifest.json', 'lean/Check.lean', 'lean/Challenge.lean', 'lean/Solution.lean',
                              'lean/comparator.json', 'lean/formalization.yaml', 'lean/Small/Root.lean',
                              'records/Small/root.md', 'records/bibliography.bib', 'dependency-map/dependency_map.html',
                              'paper/paper.pdf', 'paper/paper.tex', 'paper/references.bib', 'paper/correspondence.json',
                              'history/timeline.md', 'knowledge/odd-knowledge.tar.xz', 'knowledge/MANIFEST.md'}, package_files)
        self.assertFalse(any('DoMathExtract' in name or name.startswith('lean/.lake') for name in package_files))
        self.assertNotIn('lean/Small/Extra.lean', package_files)
        # The licence's text as the skill has it, with LF line endings whatever a checkout gave the skill's file.
        self.assertEqual((self.solved / 'LICENSE').read_bytes(),
                         (INSTALLED / 'finalize' / 'licences' / 'CC-BY-4.0.txt').read_bytes().replace(b'\r\n', b'\n'))
        helper = (self.solved / 'lean' / 'Small' / 'Helper.lean').read_text(encoding='utf-8')
        self.assertIn('theorem added_six', helper)       # the accepted simplification
        self.assertNotIn('unused_two', helper)           # removed by the take
        step_module = (self.solved / 'lean' / 'Small' / 'Step.lean').read_text(encoding='utf-8')
        self.assertNotIn('-- fail', step_module)         # the discarded simplification left the part as it was
        self.assertIn('theorem sq_step_strict', step_module)  # the fold-back closed the gap
        self.assertEqual((self.solved / 'lean' / 'Small' / 'Defs.lean').read_text(encoding='utf-8'), DEFS)
        records = set(package.files_under(self.solved / 'records'))
        self.assertEqual(records, {'bibliography.bib'} | {f'Small/{name}.md' for name in (
            'oddSum', 'root', 'sq_step', 'sq_step_strict', 'twice', 'twice_zero', 'helper_zero', 'simp_one', 'named_four',
            'added_six')})
        self.assertIn('increase strictly with n', (self.solved / 'records' / 'Small' / 'sq_step_strict.md').read_text(encoding='utf-8'))
        # The main theorem names only the definition module's elements, so it is compared beside the root.
        self.assertEqual(read_json(self.solved / 'lean' / 'comparator.json')['theorem_names'], ['Small.root', 'Small.sq_step'])
        challenge = (self.solved / 'lean' / 'Challenge.lean').read_text(encoding='utf-8')
        self.assertIn('theorem root (n : Nat) : oddSum n = n * n := by\n  sorry', challenge)
        self.assertTrue(challenge.endswith('theorem Small.sq_step (n : Nat) : oddSum (n + 1) = oddSum n + (2 * n + 1) := by\n  sorry\n'))
        self.assertEqual((self.solved / 'lean' / 'Solution.lean').read_text(encoding='utf-8'),
                         'module\n\npublic import Small.Root\npublic import Small.Step\n')
        meta = yaml.safe_load((self.solved / 'lean' / 'formalization.yaml').read_text(encoding='utf-8'))
        self.assertEqual((meta['project']['name'], meta['project']['authors']), ('Odd numbers sum to squares', ['A. Author']))
        lake = (self.scenario / 'lake-calls.txt').read_text(encoding='utf-8').split('\n')
        self.assertEqual(lake[:4], ['build', 'env lean DoMathExtract.lean', 'env lean Check.lean', ''])  # one Lake build
        readme = (self.solved / 'README.md').read_text(encoding='utf-8')
        self.assertIn('# Odd numbers sum to squares\n\nA. Author\n', readme)
        self.assertIn('The proof is by induction, in 4 modules.', readme)
        self.assertIn('The research made 1 publication.', readme)
        self.assertIn("'Small.root' depends on axioms: [propext, Quot.sound]", readme)
        # The result is the selection's sentence and the statement of the root's record. root.md is not printed.
        self.assertIn('## The result\n\nThe first n odd numbers sum to n squared.\n\nThe proposition that was posed, as the '
                      'record of `Small.root` states it:\n\n', readme)
        self.assertNotIn('For every natural number n, the sum of the first n odd numbers is n * n.', readme)
        self.assertIn('Lean is installed through elan', readme)
        self.assertIn('The warnings concern that one file; no declaration of the library uses `sorry`.', readme)
        self.assertIn('do-math is a program that conducts mathematical research in Lean', readme)
        self.assertIn('It compares: Small.root, Small.sq_step.', readme)
        self.assertIn('### Where the result comes from\n\nThe identity is classical; the records name nobody who posed it.\n\n'
                      'In `lean/formalization.yaml`, the file that describes the package for a formal-proof registry, the '
                      'result is recorded as original, which there means a result that the formalisation presents first. '
                      'The records name no proof of it and report no search for one.\n', readme)
        self.assertIn('- Disquisitiones Arithmeticae, Gauss, Carl Friedrich (gauss1801). This work gives context and not '
                      'the result. It has the step in its first section.\n', readme)
        self.assertIn('The records of the research name no earlier formal proof of this result.\n\n## Outline of the proof',
                      readme)
        self.assertIn('and the library proves each of them formally: `Small.sq_step`.', readme)
        self.assertNotIn('names no author', readme)
        timeline = (self.solved / 'history' / 'timeline.md').read_text(encoding='utf-8')
        self.assertIn('The account of the root question was written.\n\nRecord: `canon/questions/q0.md`', timeline)  # the reader's text
        self.assertIn('A change gave the root its proof.\n\nRecord: `knowledge/changes/', timeline)
        self.assertEqual(package.standalone_problems(
            self.solved, self.work, package.account_name(),
            {'folders': {name: canon.tree_hash(self.solved / name) for name in ('lean', 'records')}, 'files': {}}), [])

        # What the run leaves: the entry in the repository's README, and three files in the work folder.
        listing = (self.repository / 'README.md').read_text(encoding='utf-8')
        self.assertIn('- An earlier one.\n- [Odd numbers sum to squares](solved/odd/README.md): The first n odd numbers sum '
                      'to n squared. Lean 4.99.0; root `Small.root`.\n\n## Other\n', listing)
        self.assertEqual(sorted(path.name for path in self.work.iterdir()), ['decisions.md', 'log.json', 'report.md'])
        decisions = self.decisions()
        self.assertIn('The main theorem is `Small.sq_step` (option a)', decisions)
        self.assertIn('## Step 3: the simplification of the part aux\n\nDiscarded; that part of the library keeps the form it had.',
                      decisions)
        self.assertIn('g1 (draft, `Small.sq_step`): closed by `Small.sq_step_strict`', decisions)
        self.assertIn('r1 (records, `Small.added_six`): not closed. The lemma is wanted by the cross-part item.', decisions)
        self.assertIn('Restated as the declaration says it: g1', decisions)
        self.assertIn('The title is long. Kept because: It names the result.', decisions)
        # What the writers of the records found after the fold-back is kept in the decisions, since the work folder goes.
        self.assertIn('- `Small.sq_step_strict` (other): Its doc comment says less than it states.', decisions)
        report = (self.work / 'report.md').read_text(encoding='utf-8')
        self.assertIn('The package is in place: `solved/odd/`', report)
        self.assertNotIn('`project.authors`', report)
        # What only the user can add before a submission, and the release the registry's tools depend on.
        self.assertIn("- The Lean release. The library is on leanprover/lean4:v4.99.0. The registry takes the tools", report)
        self.assertIn("read the registry's open issues for this release", report)
        self.assertIn('- What the result is in the literature.', report)
        self.assertIn('`related_formalizations` in `lean/formalization.yaml` is empty', report)
        self.assertIn('`author_endorsement` of each source', report)
        self.assertIn('For the registry the result is recorded as original. The records name no proof of it', decisions)
        # Started again, the command refuses: the package exists.
        self.assertEqual(self.run_command(config=config), 1)
        self.assertIn('exists', self.said)

    def test_a_stopped_run_keeps_its_work_folder_and_continues_at_the_step_that_stopped(self):
        # The review leaves no partition, twice: the step stops the run.
        broken = json.dumps({'parts': [{'id': 'core', 'modules': ['Small.Root']}], 'cross': []})
        plan = script(review=[{'output/review.json': broken}])
        plan['selection'] = [{'output/decision.json': decision(), 'output/marker.txt': 'kept'}]
        self.assertEqual(self.run_command(plan, config=self.config(), lake={'build_fails_when': 'theorem Small.sq_step'}), 2)
        report = (self.work / 'report.md').read_text(encoding='utf-8')
        self.assertIn('The run stopped at the step `2.2-review`', report)
        self.assertIn('modules in no part: Small.Helper, Small.Step', report)
        # The report says what the user does. What sessions left is not the user's to repair.
        self.assertIn('## What to do\n\nNothing is to be repaired by hand', report)
        self.assertIn('The same command with the same arguments continues at the step `2.2-review`', report)
        state = read_json(self.work / 'state.json')
        self.assertEqual([step for step in state['steps'] if not step.startswith('3-')], ['0-start', '1-selection', '2.1-take'])
        self.assertLessEqual({'state.json', 'log.json', 'decisions.md', 'report.md', 'settings.json', 'source', 'first',
                              'lib', 'sessions', 'runner'}, {path.name for path in self.work.iterdir()})
        self.assertFalse(self.solved.exists())
        self.assertEqual(len(self.calls('review')), 2)        # at most two sessions for a task
        self.assertIn('modules in no part', self.calls('review')[1]['prompt'])  # the second is told the reasons
        self.assertEqual((len(self.calls('selection')), len(self.calls('simplify'))), (1, 0))
        # Each product has its hash in the state, with the hashes of what its step read.
        taken = state['steps']['2.1-take']
        self.assertEqual(taken['products'], {'lib/1-taken': canon.tree_hash(self.work / 'lib' / '1-taken')})
        self.assertEqual(taken['read']['lib/0-selected'], state['steps']['1-selection']['products']['lib/0-selected'])
        self.assertEqual(read_json(self.work / 'lib' / '1-taken' / 'taken.json')['removed'], ['Small.stray', 'Small.unused_two'])

        # A product that was changed between two starts stops the run, and is named.
        helper = self.work / 'lib' / '1-taken' / 'lean' / 'Small' / 'Helper.lean'
        original = helper.read_bytes()
        helper.write_bytes(original + b'-- repaired by hand\n')
        self.assertEqual(self.run_command(script(), config=self.config()), 2)
        report = (self.work / 'report.md').read_text(encoding='utf-8')
        self.assertIn('The run stopped at the step `2.2-review`', report)
        self.assertIn('the product lib/1-taken is not what the step that wrote it left', report)
        self.assertEqual(len(self.calls('review')), 2)
        helper.write_bytes(original)

        # A run of other arguments is not continued.
        self.assertEqual(self.run_command(script(), config=self.config(parallel=3)), 1)
        self.assertIn('differs from this one in: configuration', self.said)

        # Started again with the same arguments, the run continues at the review and comes to its end.
        again = script()
        again['selection'] = [{'output/decision.json': decision(main='Small.root')}]  # would be another choice, were it asked
        self.closed = CLOSED  # the paper command of this start closes two findings without a person
        self.assertEqual(self.run_command(again, config=self.config()), 0, self.said)
        self.assertEqual(len(self.calls('selection')), 1)      # an accepted output is not made again
        self.assertEqual(len(self.calls('selection-read')), 1)
        self.assertEqual(len(self.calls('review')), 3)
        self.assertEqual(self.steps().count('2.1-take'), 1)    # a step that passed is not made again
        self.assertEqual(self.steps().count('2.2-review'), 2)  # the start that found the changed product did not enter it
        self.assertEqual(self.steps().count('3-archive'), 1)
        self.assertEqual(self.produced[0]['resume'], False)
        # With the main theorem, Challenge.lean did not build: the root alone is compared, and the reason is recorded.
        self.assertEqual(read_json(self.solved / 'lean' / 'comparator.json')['theorem_names'], ['Small.root'])
        self.assertNotIn('Small.sq_step', (self.solved / 'lean' / 'Challenge.lean').read_text(encoding='utf-8'))
        self.assertEqual((self.solved / 'lean' / 'Solution.lean').read_text(encoding='utf-8'), 'module\n\npublic import Small.Root\n')
        self.assertIn('The root alone is compared. With the main theorem `Small.sq_step` added to Challenge.lean: lake build '
                      'ended with exit code 1', self.decisions())
        self.assertEqual((self.scenario / 'lake-calls.txt').read_text(encoding='utf-8').split('\n')[:5],
                         ['build', 'build', 'env lean DoMathExtract.lean', 'env lean Check.lean', ''])
        self.assertIn('#print axioms Small.sq_step', (self.solved / 'lean' / 'Check.lean').read_text(encoding='utf-8'))
        # No author was configured: none is named, and the report says what the user fills in.
        self.assertNotIn('A. Author', (self.solved / 'README.md').read_text(encoding='utf-8'))
        self.assertIn('names no author and no responsible maintainer', (self.solved / 'README.md').read_text(encoding='utf-8'))
        self.assertIn('`project.authors` and `project.responsible_maintainers`', (self.work / 'report.md').read_text(encoding='utf-8'))
        self.assertEqual(self.produced[-1]['title_page'], {'authors': []})
        # What the paper command closed without a person is in the decisions and in the report.
        decisions, report = self.decisions(), (self.work / 'report.md').read_text(encoding='utf-8')
        self.assertIn('## Stage 4: what the paper lost so that it says no more than the library', decisions)
        self.assertIn('- Removed from the abstract: "equivalently, the block sums to a difference of squares" It asserted: '
                      'The block sum is a difference of squares. The declaration that came nearest is `Small.sq_step`. It '
                      'states the sum additively.', decisions)
        self.assertIn('- Lemma 1.1 (`lem:step`) was restated as its declaration `Small.sq_step` says it.', decisions)
        self.assertIn('The comparison after the restatement still found a difference: The range of n.', decisions)
        self.assertIn('it took 1 passages that no declaration covers out of the paper and restated 1 statements', report)
        self.assertIn('- In the paper, Lemma 1.1 still differs from the declaration `Small.sq_step` that it states: The '
                      'range of n.', report)
        self.assertIn("The library is built with Lean 4.99.0. Lean is installed through elan, its toolchain manager, as "
                      "Lean's own installation instructions describe.",
                      (self.solved / 'README.md').read_text(encoding='utf-8'))
        self.assertEqual(sorted(path.name for path in self.work.iterdir()), ['decisions.md', 'log.json', 'report.md'])

    def test_an_output_that_fails_its_exit_check_is_sent_back_with_what_the_check_found(self):
        """Every session's first output has the fault its check is there for; the second session is told, and repairs it."""
        good = script()
        taken_helper = module_text('\n\n'.join(part for part in HELPER_PARTS if part != UNUSED))
        strict = record_text('The sums increase strictly.')
        faulty = {
            'selection-read': {'output/reading.json': json.dumps({'claims': [{'option': 'a', 'claim': 'It rests on the step.'}]})},
            'review': {'output/review.json': json.dumps({'parts': [{'id': 'core', 'modules': ['Small.Root', 'Small.Helper']}],
                                                         'cross': [{'id': 'x1', 'owner': 'nobody', 'what': 'w'}]})},
            'simplify:core': {'output/lean/Small/Step.lean': STEP, 'output/report.json': json.dumps(
                {'deleted': [], 'cross': [{'id': 'x1', 'done': True}]})},
            'arrange': {'@copy': [['lean', 'output/lean']], 'output/lean/Small/Helper.lean': taken_helper,
                        'output/renames.json': '{}', 'output/removed.json': '[]'},
            'records-write:5-01': {'output/records/Small/added_six.md': record_text('Six terms.'), 'output/findings.json': '[]'},
            'records-compare:5-01': {'output/verdicts.json': json.dumps([{'declaration': 'Small.added_six', 'verdict': 'agrees'}])},
            'sources': {'@copy': [['bibliography.bib', 'output/bibliography.bib']], 'output/sources.json': '[]',
                        'output/requests.json': '[]'},
            'foldback': {'output/report.json': json.dumps({'deleted': [], 'items': [
                {'id': 'g1', 'closed': True, 'declarations': ['Small.sq_step_strict'], 'note': ''}]})},
            'records-write:6-01': {'output/records/Small/sq_step_strict.md': strict.replace('---\n', '---\nproves: Small.sq_step\n', 1),
                                   'output/findings.json': '[]'},
            'records-compare:6-01': {'output/verdicts.json': json.dumps([{'declaration': 'Small.sq_step_strict',
                                                                          'verdict': 'corrected', 'difference': 'A word.'}])},
            'draft-compare': {'output/verdicts.json': json.dumps([{'id': 'g1', 'verdict': 'rewritten', 'text': ''}])},
            'history-write': {'output/entries.json': json.dumps([{'event': 1, 'date': '', 'text': 'A change.'}])},
            'history-read': {'output/verdicts.json': json.dumps([{'event': 1, 'verdict': 'stands', 'text': ''},
                                                                 {'event': 2, 'verdict': 'corrected', 'text': ''}])},
            'readme-write': {'output/outline.md': 'The paper has {{facts.pages}} pages.\n', 'output/obtained.md': 'x\n'},
            'package-read': {'output/findings.json': json.dumps([{'file': 'README.md', 'quote': 'by induction'}])},
        }
        plan = {key: ([faulty[key]] if key in faulty else []) + entries for key, entries in good.items()}
        plan['package-read'][1] = {'output/findings.json': json.dumps([
            {'file': 'README.md', 'quote': 'The proof is by induction', 'problem': 'The outline does not say on what.'}])}
        plan['readme-write:correction'] = [{'output/outline.md': 'The proof is by induction on n.\n',
                                            'output/obtained.md': 'The research made {{facts.publications}} publication.\n'}]
        self.assertEqual(self.run_command(plan, config=self.config()), 0, self.said)
        told = {}
        for call in self.calls():
            told.setdefault(call['kind'] + ':' + str(call['section']), []).append(call['prompt'])
        for key, wanted in (
                ('selection-read:None', 'claim 1 has no verdict'),
                ('review:None', 'modules in no part: Small.Step'),
                ('review:None', 'the cross-part item x1 has no owner that is a part'),
                ('simplify:core', 'Small.Step is not a module of this part'),
                ('arrange:None', 'nor among those removed: Small.added_six'),
                ('records-write:5-01', 'records/Small/named_four.md was not written'),
                ('records-compare:5-01', 'Small.named_four has no verdict'),
                ('sources:5', 'sources.json has no status of "verified" or "removed" for gauss1801'),
                ('foldback:Small', 'report.json does not say whether the item r1 is closed'),
                ('records-write:6-01', '"proves: Small.sq_step" is a claim that Lean did not confirm'),
                ('records-compare:6-01', 'records/Small/sq_step_strict.md was not written'),
                ('draft-compare:None', 'g1 is rewritten and verdicts.json does not give the text'),
                ('history-write:01', 'entries.json has no entry with a text for the event 2'),
                ('history-read:01', 'the entry of the event 2 is corrected and no text is given'),
                ('readme-write:None', 'outline.md uses {{facts.pages}}, and facts.json has no such key'),
                ('package-read:None', 'every finding has "file", "quote" and "problem"')):
            self.assertEqual(len(told[key]), 2, key)
            self.assertNotIn(wanted, told[key][0])
            self.assertIn(wanted, told[key][1], key)
            self.assertTrue(any(name.startswith('previous-output/') for call in self.calls()
                                if call['kind'] + ':' + str(call['section']) == key for name in call['given']), key)
        # What the reader of the package found in the prose went to a correcting session, with the prose as it was.
        correction = next(call for call in self.calls('readme-write') if call['section'] == 'correction')
        self.assertLessEqual({'findings.json', 'previous/outline.md', 'previous/obtained.md', 'facts.json'}, set(correction['given']))
        readme = (self.solved / 'README.md').read_text(encoding='utf-8')
        self.assertIn('The proof is by induction on n.', readme)
        self.assertNotIn('in 4 modules', readme)
        self.assertIn('found 1 faults in the two prose sections of the README; a session corrected them', self.decisions())
        self.assertIn('added_six', (self.solved / 'lean' / 'Small' / 'Helper.lean').read_text(encoding='utf-8'))

    def test_a_manuscript_that_fails_its_typesetting_stops_the_run_and_the_next_start_writes_the_paper_anew(self):
        self.failing = True
        self.assertEqual(self.run_command(script(), config=self.config()), 2)
        report = (self.work / 'report.md').read_text(encoding='utf-8')
        self.assertIn('The run stopped at the step `4-paper`', report)
        self.assertIn('- typesetting, after 3 repairs: TeX stopped at line 12.\n', report)
        # The report says what the user does, and prints no JSON.
        self.assertIn('## What to do\n\nRead the problems.', report)
        self.assertIn('Started again, the command writes the paper anew from the draft', report)
        self.assertNotIn('{"', report)
        # Nothing takes up a run whose manuscript failed: started again, the command deletes it and writes the paper anew.
        self.failing = False
        self.assertEqual(self.run_command(script(), config=self.config()), 0, self.said)
        self.assertEqual([call['resume'] for call in self.produced if call['out'] == 'paper'], [False, False])

    def test_a_fault_the_reader_finds_in_a_sentence_of_the_script_is_reported_and_the_run_ends(self):
        self.draft = {'statements': [DRAFT['statements'][0]], 'formulas': [], 'gaps': [], 'citations': []}
        plan = script(package_read=[{'output/findings.json': json.dumps([
            {'file': 'README.md', 'quote': 'Everything in this folder is under', 'problem': 'The licence is not named.'},
            {'file': 'README.md', 'quote': '', 'problem': 'It was not read to its end: the last section is missing here.'}])}])
        self.assertEqual(self.run_command(plan, config=self.config()), 0, self.said)
        # No session may rewrite a sentence of the program: the finding is reported with the package, and the run ends.
        report = (self.work / 'report.md').read_text(encoding='utf-8')
        self.assertIn('## What the reader of the package found and the run did not correct', report)
        self.assertIn('- README.md, at "Everything in this folder is under": The licence is not named.', report)
        # A document that the reader could not read is reported without a quote, and is no finding in the prose.
        self.assertIn('- README.md: It was not read to its end: the last section is missing here.', report)
        self.assertIn('## Stage 5: what the reader of the package found and the run did not correct', self.decisions())
        self.assertEqual(len(self.calls('readme-write')), 1)  # nothing was found in the prose, so no session corrects
        self.assertTrue((self.solved / 'README.md').is_file())

    def halted_after_the_freeze(self, plan, **options):
        """A run that is stopped at the map, so that the freeze can be looked at in the work folder."""
        with patch('finalize.Run.depmap', side_effect=paper.Stop('halted for the test')):
            self.assertEqual(self.run_command(plan, config=self.config(), **options), 2, self.said)
        self.assertIn('The run stopped at the step `4-map`', (self.work / 'report.md').read_text(encoding='utf-8'))
        return self.work / 'package' / 'lean'

    def test_a_main_theorem_whose_statement_needs_more_than_the_definitions_is_not_compared(self):
        self.draft = {'statements': [DRAFT['statements'][0]], 'formulas': [], 'gaps': [], 'citations': []}
        plan = script(selection=[{'output/decision.json': decision(main='Small.twice_zero')}])
        plan['records-write:5-01'][0]['output/findings.json'] = '[]'  # the writers found nothing, and the draft has no gap
        # Lake is run in the Lean environment of the settings: the stand-in fails without the variable `lean.env` gives.
        self.configure(lean={'env': {'DO_MATH_TEST_LAKE': 'given'}})
        lean = self.halted_after_the_freeze(plan, lake={'needs_variable': 'DO_MATH_TEST_LAKE'})
        self.assertEqual(read_json(lean / 'comparator.json')['theorem_names'], ['Small.root'])
        self.assertNotIn('twice_zero', (lean / 'Challenge.lean').read_text(encoding='utf-8'))
        self.assertIn('the statement of the main theorem `Small.twice_zero` names declarations outside the definition '
                      'modules (`Small.twice`)', self.decisions())
        self.assertIn('#print axioms Small.twice_zero', (lean / 'Check.lean').read_text(encoding='utf-8'))
        freeze = read_json(self.work / 'freeze.json')
        self.assertEqual(freeze['compared'], ['Small.root'])
        self.assertEqual(freeze['folders']['lean'], canon.tree_hash(lean))
        self.assertEqual(replay(self.work / 'view' / 'frozen')['root_state'], 'formal_proved')
        self.assertEqual((self.work / 'view' / 'frozen' / 'canon' / 'questions' / 'q0.md').read_text(encoding='utf-8'), ACCOUNT + '\n')
        self.assertFalse((self.work / 'stage' / 'lake').exists())
        # Nothing was to be folded back, so no fold-back session ran and nothing was built for it.
        self.assertEqual((self.calls('foldback'), self.calls('draft-compare')), ([], []))
        log = read_json(self.work / 'log.json')
        self.assertFalse([event for event in log if event['event'] == 'check' and event['check'].startswith('library fold')])
        self.assertEqual(canon.tree_hash(self.work / 'lib' / '6-folded' / 'lean'), canon.tree_hash(self.work / 'lib' / '4-arranged' / 'lean'))
        self.assertEqual([call['section'] for call in self.calls('records-write')], ['5-01'])
        # The sources step 5 verified were not verified again in step 6.
        self.assertEqual([call['section'] for call in self.calls('sources')], ['5'])

    def test_axioms_beyond_the_three_at_the_freeze_stop_the_run(self):
        self.draft = {'statements': [DRAFT['statements'][0]], 'formulas': [], 'gaps': [], 'citations': []}
        self.assertEqual(self.run_command(script(), config=self.config(), lake={'axioms': {'Small.root': ['propext', 'sorryAx']}}), 2)
        report = (self.work / 'report.md').read_text(encoding='utf-8')
        self.assertIn('The run stopped at the step `2.7-freeze`', report)
        self.assertIn('Small.root depends on axioms beyond the three: sorryAx', report)
        self.assertNotIn('2.7-freeze', read_json(self.work / 'state.json')['steps'])
        self.assertFalse(self.solved.exists())


class SelectionTests(FinalizeCase):
    def stopped_at_the_take(self, plan):
        with patch('finalize.Run.take', side_effect=paper.Stop('halted for the test')):
            code = self.run_command(plan, config=self.config())
        return code

    def test_a_derivation_is_compiled_and_becomes_the_module_of_the_root(self):
        derived = module_text(theorem('root', ROOT_STATEMENT, uses=['named_four'], proof='rfl',
                                      doc='The sum of the first `n` odd numbers is the square of `n`.'),
                              imports=('Small.Defs', 'Small.Helper'))
        options = [{'id': 'a', 'main': 'Small.sq_step', 'route': 'present', 'proves': 'p', 'rests_on': 'r', 'size': 's',
                    'for': 'f', 'against': 'a'},
                   {'id': 'b', 'main': 'Small.named_four', 'route': 'derivation', 'proves': 'p', 'rests_on': 'r', 'size': 's',
                    'for': 'f', 'against': 'a'}]
        reading = {'claims': [{'option': 'b', 'claim': 'It is shorter.', 'holds': False, 'correction': 'It is not shorter.',
                               'changes_comparison': True, 'printed': False}]}
        plan = script(selection=[{'output/decision.json': decision(options=options, choice='b', runner_up='a'),
                                  'output/derivations/b.lean': derived}],
                      selection_read=[{'output/reading.json': json.dumps(reading)}])
        self.assertEqual(self.stopped_at_the_take(plan), 2)
        selected = self.work / 'lib' / '0-selected'
        self.assertEqual((selected / 'lean' / 'Small' / 'Root.lean').read_text(encoding='utf-8'), derived)
        index = read_json(selected / 'index.json')
        self.assertEqual(index['entries']['Small.root']['uses'], ['Small.named_four'])
        self.assertEqual(read_json(self.work / 'state.json')['main'], 'Small.named_four')
        # The reading corrected a ground of the comparison, so the selection decided once more, and that was the end.
        calls = [call for call in self.calls() if not call['kind'].startswith('history')]  # stage 3 runs beside
        self.assertEqual([(call['kind'], call['section']) for call in calls],
                         [('selection', None), ('selection-read', None), ('selection', 'again')])
        self.assertLessEqual({'reading.json', 'previous/decision.json', 'previous/derivations/b.lean'}, set(calls[2]['given']))
        self.assertIn('derivations/b.lean', calls[1]['given'])
        self.assertIn('The independent reading corrected a claim about option b: It is not shorter. This changed a ground',
                      self.decisions())

    def test_a_corrected_claim_in_a_text_the_package_prints_sends_the_decision_back(self):
        reading = {'claims': [{'option': 'a', 'claim': 'It settles a conjecture.', 'holds': False,
                               'correction': 'root.md names no conjecture.', 'changes_comparison': False, 'printed': True}]}
        self.assertEqual(self.stopped_at_the_take(script(selection_read=[{'output/reading.json': json.dumps(reading)}])), 2)
        calls = [call for call in self.calls() if not call['kind'].startswith('history')]  # stage 3 runs beside
        self.assertEqual([(call['kind'], call['section']) for call in calls],
                         [('selection', None), ('selection-read', None), ('selection', 'again')])
        self.assertIn('root.md names no conjecture. The claim stood in a text that the package prints, and the selection '
                      'decided once more.', self.decisions())

    def test_a_corrected_claim_that_is_not_printed_and_changes_no_ground_is_recorded_and_no_more(self):
        reading = {'claims': [{'option': 'a', 'claim': 'It has four modules.', 'holds': False, 'correction': 'It has three.',
                               'changes_comparison': False, 'printed': False}]}
        self.assertEqual(self.stopped_at_the_take(script(selection_read=[{'output/reading.json': json.dumps(reading)}])), 2)
        self.assertEqual(len(self.calls('selection')), 1)
        self.assertIn('The independent reading corrected a claim about option a: It has three.\n', self.decisions())

    def test_a_reading_that_does_not_say_whether_a_wrong_claim_is_printed_is_not_accepted(self):
        unsaid = {'output/reading.json': json.dumps({'claims': [
            {'option': 'a', 'claim': 'It has four modules.', 'holds': False, 'correction': 'It has three.',
             'changes_comparison': False}]})}
        self.assertEqual(self.run_command(script(selection_read=[unsaid]), config=self.config()), 2)
        report = (self.work / 'report.md').read_text(encoding='utf-8')
        self.assertIn('The run stopped at the step `1-selection`', report)
        self.assertIn('whether the claim stands in a text that the package prints ("printed")', report)

    def test_an_accepted_output_inside_a_step_that_stopped_is_not_made_again_and_may_not_change(self):
        unread = {'output/reading.json': json.dumps({'claims': 'none'})}
        self.assertEqual(self.run_command(script(selection_read=[unread]), config=self.config()), 2)
        self.assertIn('The run stopped at the step `1-selection`', (self.work / 'report.md').read_text(encoding='utf-8'))
        self.assertEqual((len(self.calls('selection')), len(self.calls('selection-read'))), (1, 2))
        state = read_json(self.work / 'state.json')
        self.assertNotIn('1-selection', state['steps'])
        accepted = state['accepted']['selection']
        output = self.work / accepted['folder'] / 'output'
        self.assertEqual(accepted['hash'], canon.tree_hash(output))  # hashed when it was accepted
        # The accepted output was changed between two starts: the run stops and names it.
        original = (output / 'decision.json').read_bytes()
        (output / 'decision.json').write_bytes(original + b'\n')
        self.assertEqual(self.run_command(script(), config=self.config()), 2)
        self.assertIn(f"the accepted output of the session {accepted['folder']} is not what was accepted",
                      (self.work / 'report.md').read_text(encoding='utf-8'))
        self.assertEqual((len(self.calls('selection')), len(self.calls('selection-read'))), (1, 2))
        (output / 'decision.json').write_bytes(original)
        # The step is made again from its start, except for the session whose output was accepted.
        self.assertEqual(self.stopped_at_the_take(script()), 2)
        self.assertIn('The run stopped at the step `2.1-take`', (self.work / 'report.md').read_text(encoding='utf-8'))
        self.assertEqual((len(self.calls('selection')), len(self.calls('selection-read'))), (1, 3))
        self.assertEqual(len(self.calls('history-write')), 1)  # stage 3 had come to its end beside the stopped step
        self.assertIn('1-selection', read_json(self.work / 'state.json')['steps'])

    def test_a_choice_that_is_not_eligible_is_sent_back_with_the_eligible_options(self):
        wrong_statement = module_text(theorem('root', '(n : Nat) : oddSum n = n', uses=['named_four'], proof='rfl'),
                                      imports=('Small.Defs', 'Small.Helper'))
        options = [{'id': 'a', 'main': 'Small.sq_step', 'route': 'present', 'proves': 'p', 'rests_on': 'r', 'size': 's',
                    'for': 'f', 'against': 'a'},
                   {'id': 'b', 'main': 'Small.named_four', 'route': 'derivation', 'proves': 'p', 'rests_on': 'r', 'size': 's',
                    'for': 'f', 'against': 'a'},
                   {'id': 'c', 'main': 'Small.unused_two', 'route': 'present', 'proves': 'p', 'rests_on': 'r', 'size': 's',
                    'for': 'f', 'against': 'a'}]
        plan = script(selection=[{'output/decision.json': decision(options=options, choice='b', runner_up='a'),
                                  'output/derivations/b.lean': wrong_statement},
                                 {'output/decision.json': decision(options=options[:1])}])
        self.assertEqual(self.stopped_at_the_take(plan), 2)
        second = self.calls('selection')[1]['prompt']
        self.assertIn('the root does not have the statement the instance fixed', second)
        self.assertIn("option c: without a derivation an option is eligible when the root's own declaration is proved", second)
        self.assertIn('the choice is not eligible; the eligible options are: a', second)
        self.assertEqual(read_json(self.work / 'state.json')['main'], 'Small.sq_step')

    def test_a_decision_without_its_parts_is_not_accepted(self):
        faults = [({'runner_up': 'a'}, '"runner_up" is null when there is one option'),
                  ({'reasons': ' '}, '"reasons" is empty'),
                  ({'registry': {'arxiv': ['Math CO'], 'msc2020': ['05A15', '5A'], 'origin': 'new',
                                 'sources': [{'key': 'absent', 'relationship': 'background'}]}}, 'registry.msc2020')]
        entries = [{'output/decision.json': decision(**fault)} for fault, _ in faults[:2]]
        plan = script(selection=entries)
        with patch('finalize.Run.take', side_effect=paper.Stop('halted')):
            self.assertEqual(self.run_command(plan, config=self.config()), 2)
        report = (self.work / 'report.md').read_text(encoding='utf-8')
        self.assertIn('The run stopped at the step `1-selection`', report)
        self.assertIn(faults[1][1], report)
        self.assertIn(faults[0][1], self.calls('selection')[1]['prompt'])
        run = finalize.Run(self.instance, 'odd', finalize.default_config())
        run.definitions, run.allowed, run.root = ['Small.Defs'], ['propext'], 'Small.root'
        output = self.root / 'output'
        output.mkdir()
        (output / 'decision.json').write_text(decision(**faults[2][0]), encoding='utf-8')
        with self.assertRaises(paper.Unusable) as raised:
            run.read_decision(output, canon.read_index(self.instance / 'canon' / 'index.json'), replay(self.instance), BIBLIOGRAPHY)
        # Four faults of the values given, and what this registry block lacks: the account of fidelity, the three
        # texts on where the result comes from, and the list of earlier formalisations.
        self.assertEqual(len(raised.exception.problems), 9, raised.exception.problems)
        self.assertTrue(any('"registry.divergences"' in problem for problem in raised.exception.problems))


class TakeStepTests(FinalizeCase):
    def test_a_take_that_does_not_build_is_repaired_by_putting_elements_back_and_by_nothing_else(self):
        # Lean uses a lemma that the index does not show under the root, as `simp` uses a lemma without a trace in the
        # term: here the index is made blind to one use, so the take removes a lemma the root's proof needs.
        real = package.take

        def blind(index, *rest):
            index = json.loads(json.dumps(index))
            index['entries']['Small.root']['uses'].remove('Small.helper_zero')
            return real(index, *rest)

        helper = (self.instance / 'canon' / 'lean' / 'Small' / 'Helper.lean').read_text(encoding='utf-8')
        plan = script(restore=[{'output/lean/Small/Helper.lean': helper.replace('oddSum 4 = 16', 'oddSum 4 = 61')},
                               {'output/lean/Small/Helper.lean': helper}])
        with patch('finalize.Run.review', side_effect=paper.Stop('halted for the test')), patch('package.take', side_effect=blind):
            self.assertEqual(self.run_command(plan, config=self.config()), 2)
        self.assertIn('The run stopped at the step `2.2-review`', (self.work / 'report.md').read_text(encoding='utf-8'))
        first, second = self.calls('restore')
        self.assertLessEqual({'lean/Small/Helper.lean', 'before/Small/Helper.lean', 'removed.json', 'errors.txt'}, set(first['given']))
        folder = self.work / 'sessions' / first['folder']
        self.assertIn("unknown identifier 'helper_zero'", (folder / 'errors.txt').read_text(encoding='utf-8'))
        self.assertNotIn('helper_zero', (folder / 'lean' / 'Small' / 'Helper.lean').read_text(encoding='utf-8'))
        self.assertIn('theorem helper_zero', (folder / 'before' / 'Small' / 'Helper.lean').read_text(encoding='utf-8'))
        self.assertEqual(read_json(folder / 'removed.json'), [{'declaration': 'Small.helper_zero', 'file': 'Small/Helper.lean'},
                                                               {'declaration': 'Small.unused_two', 'file': 'Small/Helper.lean'}])
        self.assertIn('by more than removed elements put back whole', second['prompt'])
        taken = read_json(self.work / 'lib' / '1-taken' / 'taken.json')
        self.assertEqual((taken['restored'], taken['removed']), (['Small.helper_zero', 'Small.unused_two'], ['Small.stray']))
        self.assertEqual((self.work / 'lib' / '1-taken' / 'lean' / 'Small' / 'Helper.lean').read_text(encoding='utf-8'), helper)
        self.assertTrue((self.work / 'lib' / '1-taken' / 'records' / 'Small' / 'helper_zero.md').is_file())
        self.assertIn('these removed elements were put back: `Small.helper_zero`, `Small.unused_two`', self.decisions())


if __name__ == '__main__':
    unittest.main()
