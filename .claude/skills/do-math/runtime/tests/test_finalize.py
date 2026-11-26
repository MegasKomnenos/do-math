"""The finalize command and its scripts, with stand-in sessions, the stand-in compiler and a stand-in Lake.

No AI session, no Lean and no Lake is run. The launch of a session is patched as tests/test_paper.py
patches it: the command the program starts is tests/finalize_cli.py, which then plays the session. The
same file is Lake and Lean's version command, and its description says what `script.json` and
`lake.json` of a scenario make the stand-ins do.

The paper command is not run: `finalize.produce` is replaced by a function that writes the files the
pipeline reads of a run of that command and records what it was called with. Its own tests are test_paper.py.
"""
import functools
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import threading
import unittest
from unittest.mock import patch

import yaml

THIS = Path(__file__).resolve()
CLI = THIS.with_name('finalize_cli.py')  # the stand-in for the CLI of a session, for Lake and for Lean's version command

sys.path[:0] = [str(THIS.parents[1]), str(THIS.parent)]
import canon
import finalize
import lean_broker
import package
import paper
from cli_adapter import Command, provider_for_model
from knowledge import replay
from runtime_support import first_commit, git, read_json, remove_tree, write_json
from support import (DEFS, ROOT, InstanceCase, fixture_settings, kept_copy, module_text, record_text, stop_broker,
                     template, theorem)

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
# What the session that checks the sources keeps of the one work the records cite: the sentence of the record whose
# header names the work, the place in the work, and the words of the work there.
QUOTED = {'declaration': 'Small.sq_step', 'sentence': 'Passing from n to n + 1 adds the odd number 2n + 1.',
          'place': 'Section 1', 'quote': 'The stand-in words of the work at that place.'}
INSTRUCTIONS = ('selection', 'selection-read', 'restore', 'review', 'simplify', 'arrange', 'records-write',
                'records-compare', 'sources', 'foldback', 'draft-compare', 'history-write', 'history-read',
                'readme-write', 'package-read')
_SETTLED = None
_RECORDED = None  # the repository and the scenario of a run that stopped before the draft (FinalizeCase.from_the_records)
# What the paper command closed without a person, as the `end` event of its log carries it.
CLOSED = [{'kind': 'removed', 'where': 'the abstract', 'section': 'abstract',
           'quote': 'equivalently, the block sums to a difference of squares',
           'asserts': 'The block sum is a difference of squares.', 'nearest': 'Small.sq_step',
           'difference': 'It states the sum additively.'},
          {'kind': 'removed', 'where': 'the proof of Lemma 1.1', 'section': 'sec:step',
           'quote': 'as Gauss shows for every block', 'asserts': '', 'nearest': '',
           'difference': 'The words kept of the work speak of the single step.', 'source': 'gauss1801'},
          {'kind': 'restated', 'label': 'lem:step', 'number': 'Lemma 1.1', 'element': 'Small.sq_step',
           'before': 'For $n \\ge 1$ the step holds.', 'difference': 'The element has every n.',
           'after': 'For every $n$ the step holds.', 'verdict': 'differs', 'difference_after': 'The range of n.'},
          {'kind': 'uncovered', 'where': 'the running text of the section "The step"', 'section': 'sec:step',
           'quote': 'Hence every block sum is positive.', 'asserts': 'The block sums are positive.',
           'nearest': 'Small.sq_step', 'difference': 'No declaration bounds a block sum.'},
          {'kind': 'differs', 'label': 'thm:main', 'number': 'Theorem 1.2', 'element': 'Small.root',
           'difference': 'The sum starts at 1.'},
          {'kind': 'wide', 'problem': 'paper.tex, line 40: TeX set a line 12pt wider than the text block'}]


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
                                                         'opened': 'parts', 'note': '', 'attributions': [QUOTED]}])}],
        'foldback': [{'output/lean/Small/Step.lean': STEP.replace('\n\nend Small', '\n\n' + theorem(
            'sq_step_strict', '(n : Nat) : oddSum n < oddSum (n + 1)', uses=['sq_step'], proof='rfl') + '\n\nend Small'),
            # Where the session has nothing to say it writes null: no note for the item it closed, no declaration for the other.
            'output/report.json': json.dumps({'deleted': [], 'items': [
                {'id': 'g1', 'closed': True, 'declarations': ['Small.sq_step_strict'], 'note': None},
                {'id': 'r1', 'closed': False, 'declarations': None, 'note': 'The lemma is wanted by the cross-part item.'}]})}],
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

    changes_guides = True  # `skill` below writes the stand-in instruction files into the copy
    reads_the_instance = False  # set by a class whose tests read the published instance and write nothing into it

    def starting_instance(self):
        """The published instance once the first test has made it; before that, the one `init` created."""
        return _SETTLED or super().starting_instance()

    @functools.cached_property
    def skill(self):
        """The copy of the guides that InstanceCase makes, with what the command reads from the `finalize` folder.

        Every instruction file is one line of text with the names the program fills, and the licence texts are
        the installed ones. The folder is made when it is first asked for: by the runner that publishes the
        instance once per test process, by the command, or by a test that changes an instruction file. A test
        of a script alone reads nothing of the skill, so nothing is copied or written for it."""
        folder = super().skill
        for name in INSTRUCTIONS:
            path = folder / 'finalize' / (name + '.md')
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f'Instruction {name} for {{{{root}}}}, main {{{{main}}}}.\n', encoding='utf-8')
        (folder / 'finalize' / 'simplify.md').write_text('Simplify the part {{part}}.\n', encoding='utf-8')
        (folder / 'finalize' / 'common.md').write_text(
            'Common: work {{work}}, skill {{skill}}, python {{python}}, library {{library}}, source {{imported_source}}, '
            'memory {{expect_mb}}.\n', encoding='utf-8')
        shutil.copytree(INSTALLED / 'finalize' / 'licences', folder / 'finalize' / 'licences')
        return folder

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
            self.configure(lean={'version_command': [sys.executable, '-B', str(CLI), 'version']})
            _SETTLED = kept_copy(self.instance, 'do-math-finalize-')
        if self.reads_the_instance:
            # The kept instance itself and no copy of it: the tests of such a class write nothing into it.
            self.instance = _SETTLED
        self.repository = self.root / 'repository'
        self.repository.mkdir()
        (self.repository / 'README.md').write_text('# The repository\n\n## Solved problems\n\n- An earlier one.\n\n## Other\n',
                                                   encoding='utf-8')
        self.work = self.repository / '.skill-workspace' / 'finalize-odd'
        self.solved = self.repository / 'solved' / 'odd'
        self.scenario = self.root / 'scenario'
        self.scenario.mkdir()
        self.produced, self.paper_code, self.draft = [], 0, DRAFT
        self.closed = []  # what the stand-in for the paper command says it closed without a person
        self.failing = False  # whether the stand-in leaves a manuscript that fails its typesetting
        self.disagreements = []  # what the stand-in's comparison of the draft reports of the records
        self.addCleanup(stop_broker, self.work)

    def command(self, cli, model, effort, cwd, servers=None, **options):
        return Command(provider_for_model(model), [sys.executable, '-B', str(CLI), 'session', str(self.scenario)], Path(cwd))

    def produce(self, instance, out, tex=None, choice=None, parallel=4, resume=False, dry=False, draft=False,
                from_draft=None, title_page=None, gate=None, main=None):
        """Stands in for paper.produce: writes the files that the pipeline reads of a run of the paper command."""
        out = Path(out)
        self.produced.append({'instance': Path(instance).name, 'out': out.name, 'resume': resume, 'draft': draft,
                              'gate': gate, 'parallel': parallel, 'main': main,
                              'title_page': read_json(title_page) if title_page else None,
                              'root_state': replay(instance)['root_state'],
                              'drafted': read_json(Path(from_draft) / 'draft.json') if from_draft else None})
        out.mkdir(parents=True, exist_ok=True)
        write_json(out / 'materials.json', {})
        write_json(out / 'plan.json', PLAN)
        session = {'event': 'session', 'kind': 'write', 'model': 'codex/paper-model'}
        if draft:
            (out / 'study.md').write_text('How the chosen papers are written.\n', encoding='utf-8')
            write_json(out / 'draft.json', self.draft)
            write_json(out / 'log.json', [session] + ([{'event': 'draft', 'record_disagreements': self.disagreements}]
                                                      if self.disagreements else []))
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
        instances = (read_json(Path(from_draft) / 'draft.json').get('instances') or []) if from_draft else []
        write_json(out / 'correspondence.json', {'root': 'Small.root', 'statements': [
            {'label': 'thm:main', 'element': 'Small.root', 'cited': None},
            {'label': 'lem:step', 'element': 'Small.sq_step', 'cited': 'gauss1801'}],
            'instances': [{key: entry[key] for key in ('element', 'key', 'where')} for entry in instances]})
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
                given = fixture_settings()['lean']
                value['lean'].update({key: given[key] for key in ('priority', 'min_free_memory_mb', 'memory_budget_mb',
                                                                  'calibration_expect_mb')})
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
                patch('command_sessions.worker_command', side_effect=self.command), patch('finalize.produce', side_effect=self.produce), \
                patch('paper.load_collection', return_value=([], {}, None)), \
                patch('package.reduced_settings', side_effect=reduced), \
                patch('package.lake_command', return_value=[sys.executable, '-B', str(CLI), 'lake', str(self.scenario)]), \
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

    def noted(self, text):
        """Add a text to what the research understood of its root question and commit it; returns the commit."""
        note = self.instance / 'canon' / 'questions' / 'q0.md'
        note.write_text(note.read_text(encoding='utf-8') + text, encoding='utf-8', newline='\n')
        git(self.instance, 'commit', '-m', 'a note', '--', 'canon/questions/q0.md')
        return package.head_commit(self.instance)

    def lake_project(self, release, lakefile=''):
        """A Lake project as the Lean environment of a research that imports a library; returns it and its one package.

        The project requires `mathlib` at `release`, and `lakefile` is what its lakefile holds after that. The
        package stands in the packages folder as a Git repository at the revision that the manifest names."""
        project = self.root / 'project'
        mathlib = project / '.lake' / 'packages' / 'mathlib'
        mathlib.mkdir(parents=True)
        (project / 'lean-toolchain').write_text(f'leanprover/lean4:{release}\n', encoding='utf-8')
        (project / 'lakefile.toml').write_text(
            f'name = "env"\n\n[[require]]\nname = "mathlib"\nrev = "{release}"\n' + lakefile, encoding='utf-8')
        git(mathlib, 'init')
        (mathlib / 'file').write_text('x', encoding='utf-8')
        git(mathlib, 'add', 'file')
        git(mathlib, 'commit', '-m', 'one')
        entry = {'name': 'mathlib', 'type': 'git', 'rev': git(mathlib, 'rev-parse', 'HEAD'), 'inputRev': release,
                 'inherited': False}
        write_json(project / 'lake-manifest.json', {'version': '1.3.0', 'packagesDir': '.lake/packages', 'packages': [entry]})
        return project, entry

    def from_the_records(self):
        """Begin this test at a run that has passed every step before the draft, with the plain script.

        The first test that asks makes that run with the command itself, stopped at the draft, and a copy
        of its repository and of its scenario is kept for the test process. Every test that asks then
        has that run in its own folders, and its next start of the command continues at the draft, as
        the command continues any run that stopped. A run names its instance by the path, so these
        tests give the command the kept instance itself; the command reads an instance and writes
        nothing into it. This is for a test whose subject lies after the records: its script entries for
        the earlier steps, its configuration and its instance are the plain ones."""
        global _RECORDED
        self.instance = _SETTLED
        if _RECORDED is None:
            with patch('finalize.Run.draft', side_effect=paper.Stop('halted for the test')):
                self.assertEqual(self.run_command(script(), config=self.config()), 2, self.said)
            self.assertIn('The run stopped at the step `2.6-draft`', (self.work / 'report.md').read_text(encoding='utf-8'))
            # The run has ended its broker, so nothing writes into the folders while they are copied.
            _RECORDED = (kept_copy(self.repository, 'do-math-finalize-run-'), kept_copy(self.scenario, 'do-math-finalize-run-'))
        else:
            for kept, folder in zip(_RECORDED, (self.repository, self.scenario)):
                shutil.copytree(kept, folder, dirs_exist_ok=True)


# ----------------------------------------------------------------------------- the scripts, each alone

class TakeTests(FinalizeCase):
    reads_the_instance = True

    def setUp(self):
        super().setUp()
        self.index = canon.read_index(self.instance / 'canon' / 'index.json')
        self.lean = self.instance / 'canon' / 'lean'
        self.allowed = ['propext', 'Classical.choice', 'Quot.sound']  # the axioms the instance allows, as the command gives them
        self.plan = package.take(self.index, self.lean, 'Small', 'Small.root', ['Small.Defs'], self.allowed)

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
            package.take(self.index, self.lean, 'Small', 'Small.root', ['Small.Defs'], self.allowed)

    def test_an_attribute_given_by_a_separate_command_keeps_the_element(self):
        target = self.root / 'lean'
        shutil.copytree(self.lean, target)
        path = target / 'Small' / 'Helper.lean'
        path.write_text(path.read_text(encoding='utf-8').replace('\nend Small', '\nattribute [simp] unused_two\n\nend Small'),
                        encoding='utf-8', newline='\n')
        self.assertIn('Small.unused_two',
                      package.take(self.index, target, 'Small', 'Small.root', ['Small.Defs'], self.allowed)['kept'])

    def test_an_instance_is_kept_though_no_proof_names_it(self):
        # Lean finds an instance by its type, so no proof names it. Here the declaration that the root does not rest
        # on is an instance behind a modifier, and the index has the hash of that source, as an extraction gives it.
        target = self.root / 'lean'
        shutil.copytree(self.lean, target)
        path = target / 'Small' / 'Helper.lean'
        text = path.read_text(encoding='utf-8').replace('theorem unused_two', 'noncomputable instance unused_two')
        path.write_text(text, encoding='utf-8', newline='\n')
        entry = self.index['entries']['Small.unused_two']
        entry['source_sha'] = canon.sha256_text(canon.declaration_text(text, entry['span']))
        self.assertIn('Small.unused_two',
                      package.take(self.index, target, 'Small', 'Small.root', ['Small.Defs'], self.allowed)['kept'])

    def test_a_command_that_ends_with_in_is_removed_with_the_element_it_stands_above(self):
        # `open Classical in` applies to the one declaration that follows it, and Lean gives that declaration a
        # span that begins below the line. Left behind, the line would apply to whatever follows the removed element.
        target = self.root / 'lean'
        shutil.copytree(self.lean, target)
        path = target / 'Small' / 'Helper.lean'
        before = path.read_text(encoding='utf-8')
        entries = self.index['entries']
        gone = canon.declaration_text(before, entries['Small.unused_two']['span'])
        path.write_text(before.replace(gone, 'set_option maxHeartbeats 400000 in\nopen Classical in\n' + gone),
                        encoding='utf-8', newline='\n')
        # The spans as Lean gives them for that file: from the two lines on, every declaration stands two lines lower.
        first = entries['Small.unused_two']['span'][0]
        for entry in entries.values():
            if entry['file'] == 'Small/Helper.lean' and entry['span'][0] >= first:
                entry['span'][0] += 2
                entry['span'][2] += 2
        plan = package.take(self.index, target, 'Small', 'Small.root', ['Small.Defs'], self.allowed)
        self.assertEqual(plan['removed'], self.plan['removed'])
        self.assertEqual(plan['files']['Small/Helper.lean'], self.plan['files']['Small/Helper.lean'])

    def test_a_theorem_that_is_not_proved_is_not_kept_for_its_attribute(self):
        self.assertIn('Small.simp_one', self.plan['kept'])
        self.index['entries']['Small.simp_one']['axioms'] = ['sorryAx']
        plan = package.take(self.index, self.lean, 'Small', 'Small.root', ['Small.Defs'], self.allowed)
        self.assertIn('Small.simp_one', plan['removed'])
        self.assertIn('Small.root', plan['kept'])

    def test_a_definition_that_uses_a_theorem_without_a_proof_is_not_kept_for_its_attribute(self):
        # A definition can name a theorem that the research left without a proof: its own text is complete, and Lean
        # reports `sorryAx` for it through that theorem. Kept for its attribute, it would keep the theorem in the
        # library, and no check of the library passes a theorem without a proof. The index is made to say of
        # `simp_one`, which carries an attribute, what it says of such a definition.
        entries = self.index['entries']
        entries['Small.unused_two']['axioms'] = ['sorryAx']
        entries['Small.simp_one'].update(kind='def', uses=['Small.unused_two'], axioms=['sorryAx'])
        plan = package.take(self.index, self.lean, 'Small', 'Small.root', ['Small.Defs'], self.allowed)
        self.assertLessEqual({'Small.simp_one', 'Small.unused_two'}, set(plan['removed']))
        self.assertEqual([item['declaration'] for item in plan['spans'] if not item['proved']],
                         ['Small.simp_one', 'Small.unused_two'])

    def test_a_restore_puts_removed_elements_back_and_deletes_lines_and_does_nothing_else(self):
        before = {relative: (self.lean / relative).read_text(encoding='utf-8') for relative in self.plan['files']}
        whole = before['Small/Helper.lean']

        def restored(plan, text, relative='Small/Helper.lean'):
            return package.restored_files(plan['spans'], plan['held'], before, {relative: text})

        back, files, deleted, problems = restored(self.plan, whole)
        self.assertEqual((back, deleted, problems), (['Small.unused_two'], {}, []))
        self.assertEqual(files['Small/Helper.lean'], whole)
        for changed, word in ((whole.replace('oddSum 4 = 16', 'oddSum 4 = 17'), 'by more than removed elements'),
                              (whole + '\ntheorem new_one : oddSum 0 = 0 := by\n  rfl\n', 'by more than removed elements')):
            back, files, deleted, problems = restored(self.plan, changed)
            self.assertEqual((back, files, deleted), ([], {}, {}))
            self.assertIn(word, problems[0])
        self.assertIn('no file of the taken library', restored(self.plan, EXTRA, 'Small/Extra.lean')[3][0])
        # A theorem that the research left without a proof is removed although a private declaration names it, and it
        # may not come back. The session deletes the private declaration, and no line of an element that stays.
        self.index['entries']['Small.named_four']['axioms'] = ['sorryAx']
        plan = package.take(self.index, self.lean, 'Small', 'Small.root', ['Small.Defs'], self.allowed)
        self.assertEqual([item['declaration'] for item in plan['spans'] if not item['proved']], ['Small.named_four'])
        hidden = HELPER_PARTS[-1]
        without = plan['files']['Small/Helper.lean'].replace('\n\n' + hidden, '')
        back, files, deleted, problems = restored(plan, without)
        self.assertEqual((back, files, problems), ([], {'Small/Helper.lean': without}, []))
        self.assertEqual(deleted, {'Small/Helper.lean': hidden.split('\n')})
        for changed, word in ((whole.replace(UNUSED + '\n\n', ''), 'puts back Small.named_four'),
                              (without.replace('@[simp]\n', ''), 'Small.simp_one')):
            back, files, deleted, problems = restored(plan, changed)
            self.assertEqual((back, files, deleted), ([], {}, {}))
            self.assertIn(word, problems[0])

    def test_the_texts_by_which_sessions_read_the_library_say_what_the_index_and_the_records_hold(self):
        # The digest of the selection: the declaration whose proof settles the root, the units under it with the
        # descriptions of their records, and the settled units that proof does not rest on, of which this research
        # has none. An element of weight step that the proof rests on is not listed.
        digest = package.selection_digest(replay(self.instance), self.index)
        self.assertIn('## Declarations whose proof formally settles the root\n\n### `Small.root`\n\nIt rests on ', digest)
        self.assertIn('\n- `Small.sq_step`: Passing from n to n + 1 adds the odd number 2n + 1.\n', digest)
        self.assertNotIn('Small.helper_zero', digest)
        self.assertTrue(digest.endswith('that these proofs do not rest on\n\nNone.\n'), digest)
        # What rests on what, for the elements the take keeps: the line of the root names what its proof names.
        rests = package.rests_on_text(self.index, set(self.plan['kept']))
        self.assertIn('; proof names `Small.helper_zero`, `Small.sq_step`, `Small.twice_zero`\n', rests)
        self.assertNotIn('Small.stray', rests)
        # The declarations by module, each with its statement; the module of the step is the last by name.
        self.assertTrue(package.declarations_text(self.index).endswith(
            '\n## `Small.Step`\n\n- theorem `Small.sq_step (n : Nat) : oddSum (n + 1) = oddSum n + (2 * n + 1)`\n'))


class LibraryCheckTests(FinalizeCase):
    reads_the_instance = True

    def test_each_fault_of_a_lean_file_and_of_a_definition_module_is_found(self):
        lean = self.root / 'lean'
        shutil.copytree(self.instance / 'canon' / 'lean', lean)
        first = self.instance / 'canon' / 'lean'
        self.assertEqual(package.lean_form_problems(lean) + package.definition_problems(lean, first, ['Small.Defs']), [])
        (lean / 'Small' / 'Plain.lean').write_text('-- a comment\nimport Small.Defs\n', encoding='utf-8')
        (lean / 'Small' / 'Long.lean').write_text('module\n' + '-- line\n' * 10_000, encoding='utf-8')
        (lean / 'Small' / 'Fits.lean').write_text('/- a comment -/\nmodule\n' + '-- line\n' * 9_998, encoding='utf-8')
        (lean / 'Small' / 'notes.txt').write_text('What a session left beside its modules.\n', encoding='utf-8')
        problems = package.lean_form_problems(lean)
        self.assertEqual(len(problems), 3, problems)
        self.assertIn('Small/Plain.lean does not begin with `module`', problems)
        self.assertTrue(any('Small/Long.lean has 10001 lines' in problem for problem in problems))
        self.assertTrue(any('Small/notes.txt is no Lean file' in problem for problem in problems))
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
        # A private lemma is no element, so no entry shows a proof that it leaves open. The index holds it apart.
        opened = json.loads(json.dumps(index))
        self.assertTrue(opened['hidden'])
        for item in opened['hidden'].values():
            item['sorry'] = True
        self.assertIn('Small.hidden_three, a declaration that is no element, has an open proof (`sorry`)', check(opened))
        # Records are checked only where they are due.
        lacking = {path: record for path, record in records.items() if path != 'Small/helper_zero'}
        self.assertTrue(any('Small.helper_zero has no record' in problem for problem in check(index, lacking)))
        orphan = {**records, 'Small/gone': records['Small/root']}
        self.assertTrue(any('records/Small/gone.md belongs to no declaration' in problem for problem in check(index, orphan)))
        claim = json.loads(json.dumps(records))
        claim['Small/helper_zero']['meta']['proves'] = 'Small.simp_one'
        self.assertTrue(any('Lean did not confirm' in problem for problem in check(index, claim)))

    def test_what_a_part_returns_is_held_to_the_modules_it_may_change(self):
        # A part returns files under lean/ and names in its report the files it deleted. Each is a module that the
        # part owns or, for a new file, one that it may add. A definition module is neither.
        base, output = self.instance / 'canon' / 'lean', self.root / 'output'
        for relative in ('Small/Step.lean', 'Small/Sums/New.lean'):
            package.write_text(output / 'lean' / relative, STEP)
        owns = lambda module: module in ('Small.Step', 'Small.Helper', 'Small.Absent')
        write_json(output / 'report.json', {'deleted': ['lean/Small/Helper.lean']})
        files, deleted, problems = package.part_output(output, base, owns, ['Small.Defs'])
        self.assertEqual((sorted(files), deleted, problems),
                         (['Small/Step.lean', 'Small/Sums/New.lean'], ['Small/Helper.lean'], []))
        write_json(output / 'report.json', {'deleted': ['Small/Absent.lean', 'Small/Defs.lean', 'Small/Root.lean',
                                                        'Small/notes.txt']})
        _, _, problems = package.part_output(output, base, owns, ['Small.Defs'], lambda module: False)
        wanted = ('the new module Small.Sums.New does not lie in this part',
                  'lean/Small/Absent.lean is listed as deleted and the library has no such file',
                  'Small.Defs is a definition module', 'Small.Root is not a module of this part',
                  'lean/Small/notes.txt is no Lean file')
        self.assertEqual(len(problems), len(wanted), problems)
        for problem, reason in zip(problems, wanted):
            self.assertIn(reason, problem)
        write_json(output / 'report.json', {'deleted': 'Small/Helper.lean'})
        _, deleted, problems = package.part_output(output, base, owns, ['Small.Defs'])
        self.assertEqual(deleted, [])
        self.assertIn('"deleted" in report.json is an array of paths', problems[0])


class RecordTests(FinalizeCase):
    reads_the_instance = True

    def test_the_list_holds_new_and_changed_elements_and_records_that_name_what_is_gone(self):
        base = canon.read_index(self.instance / 'canon' / 'index.json')
        records = self.root / 'records'
        shutil.copytree(self.instance / 'canon' / 'records', records)
        now = json.loads(json.dumps(base))
        del now['entries']['Small.unused_two'], now['entries']['Small.stray']
        now['entries']['Small.helper_zero']['source_sha'] = 'another'
        now['entries']['Small.fresh'] = {**now['entries']['Small.simp_one'], 'name': 'Small.fresh'}
        # A record can name what is gone in its header alone, as the statement it proves, and nowhere between backticks.
        (records / 'Small' / 'twice_zero.md').write_text(
            record_text('Twice the empty sum is zero.', weight='unit', proves='Small.stray'), encoding='utf-8')
        # And it can name what is gone without the library's first component, as a text inside the namespace does.
        (records / 'Small' / 'simp_one.md').write_text(
            record_text('The first odd number is one, the case that `stray` goes on from.'), encoding='utf-8')
        todo = {item['declaration']: item for item in package.record_todo(now, base, records)}
        self.assertEqual({name: item['why'] for name, item in todo.items()},
                         {'Small.helper_zero': 'changed', 'Small.fresh': 'new',
                          'Small.named_four': 'names a declaration that is gone',
                          'Small.simp_one': 'names a declaration that is gone',
                          'Small.twice_zero': 'names a declaration that is gone'})
        self.assertIsNone(todo['Small.fresh']['record'])
        self.assertEqual(todo['Small.named_four']['record'], 'records/Small/named_four.md')
        self.assertEqual(package.drop_orphans(records, now), ['Small.stray', 'Small.unused_two'])
        self.assertFalse((records / 'Small' / 'stray.md').exists())
        # A record that claims, under `proves`, what Lean did not confirm for this index is written again: the check
        # of the records requires every such claim to be confirmed, and only a writer can leave the claim out.
        (records / 'Small' / 'twice_zero.md').write_text(
            record_text('Twice the empty sum is zero.', weight='unit', proves='Small.simp_one'),
            encoding='utf-8', newline='\n')
        listed = lambda: {item['declaration']: item['why'] for item in package.record_todo(now, base, records)}
        self.assertEqual(listed().get('Small.twice_zero'), 'claims what Lean did not confirm')
        now['pairs'] = {'same|Small.twice_zero|Small.simp_one': True}
        self.assertNotIn('Small.twice_zero', listed())

    def test_what_is_due_goes_to_the_sessions_in_groups_of_one_folder_and_of_a_bounded_size(self):
        # The groups are numbered in the order of their folders, and inside a folder in the order of the list.
        due = ['Small/Sums/a', 'Small/p', 'Small/q', 'Small/r']
        self.assertEqual(package.batches(due, 2, key=lambda item: item.rsplit('/', 1)[0]),
                         [('01', ['Small/p', 'Small/q']), ('02', ['Small/r']), ('03', ['Small/Sums/a'])])
        # Without a key, as the events of the history are divided, the list is cut in its own order.
        self.assertEqual(package.batches(due, 3), [('01', due[:3]), ('02', due[3:])])

    def test_records_follow_renamed_and_removed_declarations(self):
        records = self.root / 'records'
        shutil.copytree(self.instance / 'canon' / 'records', records)
        # A record names the renamed declaration in its header too, as the statement it proves.
        (records / 'Small' / 'twice_zero.md').write_text(
            record_text('Twice the empty sum is zero.', weight='unit', proves='Small.unused_two'), encoding='utf-8')
        package.follow_renames(records, {'Small.unused_two': 'Small.Sums.two'}, ['Small.stray'])
        self.assertFalse((records / 'Small' / 'unused_two.md').exists())
        self.assertFalse((records / 'Small' / 'stray.md').exists())
        self.assertIn('first two odd numbers', (records / 'Small' / 'Sums' / 'two.md').read_text(encoding='utf-8'))
        self.assertIn('`Small.Sums.two`', (records / 'Small' / 'named_four.md').read_text(encoding='utf-8'))
        self.assertIn('\nproves: Small.Sums.two\n', (records / 'Small' / 'twice_zero.md').read_text(encoding='utf-8'))

    def test_the_cited_sources_are_listed_with_the_records_that_cite_them_in_the_header_or_in_the_text(self):
        index = canon.read_index(self.instance / 'canon' / 'index.json')
        # As the research left its records, one of them cites a work, in its header.
        cited = package.cited(self.instance / 'canon' / 'records', index, package.bibliography_keys(BIBLIOGRAPHY))
        self.assertEqual([(item['key'], [row['declaration'] for row in item['records']]) for item in cited],
                         [('gauss1801', ['Small.sq_step'])])
        self.assertEqual(package.bibliography_field(BIBLIOGRAPHY, 'gauss1801', 'title'), 'Disquisitiones Arithmeticae')
        records = self.root / 'records'
        shutil.copytree(self.instance / 'canon' / 'records', records)
        # A record cites a work by its key in brackets, with or without the place. A bracket that holds no key of the
        # bibliography is other text: an interval, a set of indices, a key that the bibliography does not have.
        said = ('The empty sum is zero. The step is in the first section [gauss1801, Section 1], and the sums over the '
                'interval [0, n] are tabulated there as well [gauss1801]. See also [nobody1900, p. 2] and the set [n].')
        (records / 'Small' / 'helper_zero.md').write_text(record_text(said), encoding='utf-8', newline='\n')
        keys = package.bibliography_keys(BIBLIOGRAPHY)
        cited = package.cited(records, index, keys)
        self.assertEqual([(item['key'], [(row['declaration'], row['header'], row['citations']) for row in item['records']])
                          for item in cited],
                         [('gauss1801', [('Small.helper_zero', False, ['[gauss1801, Section 1]', '[gauss1801]']),
                                         ('Small.sq_step', True, [])])])


class RegistryTests(FinalizeCase):
    reads_the_instance = True

    def first(self):
        folder = self.root / 'first'
        package.export_commit(self.instance, first_commit(self.instance), ['canon/lean'], folder, 'canon/')
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

    def test_the_challenge_keeps_outside_imports_once_and_joins_the_definition_modules_in_import_order(self):
        # A research on an imported library, as one on Mathlib is: its definition modules import from outside the
        # library, and one definition module imports another, which here comes later by name.
        first = self.root / 'outside'
        outside = 'public import Mathlib.Data.Finset.Card'
        package.write_text(first / 'Lib' / 'Kernel.lean',
                           f'module\n\n{outside}\n\nnamespace Lib\n\ndef kernel : Nat := 0\n\nend Lib\n')
        package.write_text(first / 'Lib' / 'Defs.lean',
                           f'module\n\n{outside}\npublic import Lib.Kernel\nimport Mathlib.Tactic\n\n'
                           'namespace Lib\n\ndef twice : Nat := kernel + kernel\n\nend Lib\n')
        package.write_text(first / 'Lib' / 'Root.lean',
                           'module\n\npublic import Lib.Defs\n\nnamespace Lib\n\n'
                           'theorem root : twice = 0 := by\n  sorry\n\nend Lib\n')
        definitions = package.definition_modules(first, 'Lib', 'Lib.Root')
        self.assertEqual(definitions, ['Lib.Kernel', 'Lib.Defs'])
        # One header: each import from outside once, as it was written, and no import of a module that is now inside.
        text = package.challenge_text(first, definitions, 'Lib.Root')
        self.assertEqual(text, f'module\n\n{outside}\nimport Mathlib.Tactic\n\n'
                               'namespace Lib\n\ndef kernel : Nat := 0\n\nend Lib\n\n'
                               'namespace Lib\n\ndef twice : Nat := kernel + kernel\n\nend Lib\n\n'
                               'namespace Lib\n\ntheorem root : twice = 0 := by\n  sorry\n\nend Lib\n')
        measure = package.challenge_measure(text)
        self.assertEqual((measure['imports'], measure['fails']), (['Mathlib.Data.Finset.Card', 'Mathlib.Tactic'], []))

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
        (lean / 'Check.lean').write_text(package.check_text(['Small.Root', 'Small.Step'], ['Small.root', 'Small.sq_step']),
                                         encoding='utf-8')
        write_json(lean / 'comparator.json', package.comparator(compared))
        return lean

    def test_the_files_of_the_freeze_have_the_form_the_registry_reads(self):
        lean = self.frozen(compared=('Small.root', 'Small.sq_step'), authors=[
            {'name': 'A. Author', 'address': 'A town', 'email': 'a@example.org'},
            {'name': 'B. Author', 'email': 'b@example.org', 'github': 'b-author', 'orcid': '0000-0002-1825-0097'}])
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
        self.assertTrue(check.startswith('module\n\nimport Small.Root\nimport Small.Step\n\n'))
        self.assertIn('#print axioms Small.root\n#check @Small.sq_step\n#print axioms Small.sq_step\n', check)
        data = yaml.safe_load((lean / 'formalization.yaml').read_text(encoding='utf-8'))
        # An author with a GitHub login or an ORCID iD is a mapping of the name and those, as the registry reads an
        # author; one without them is the name alone, and so is every responsible maintainer. The address and the
        # e-mail of an author are for the paper and do not stand here.
        self.assertEqual(data['project'], {'name': 'A title', 'description': 'The first n odd numbers sum to n squared.',
                                           'authors': ['A. Author', {'name': 'B. Author', 'github': 'b-author',
                                                                     'orcid': '0000-0002-1825-0097'}],
                                           'license': 'CC-BY-4.0',
                                           'responsible_maintainers': ['A. Author', 'B. Author']})
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
                 (edit_yaml(['classification', 'arxiv'], ['math.CO', 'math.NT', 'math.PR']), 'classification.arxiv'),
                 (edit_yaml(['classification', 'msc2020'], ['5A15']), 'classification.msc2020'),
                 (edit_yaml(['sources'], [{'title': 'T', 'relationship': 'inspired'}]), 'each entry of sources'),
                 (edit_yaml(['automation', 'methods'], []), 'automation.methods'),
                 (edit_yaml(['review', 'status'], ''), 'review.status')]
        for change, wanted in cases:
            problems = broken(change)
            self.assertEqual(len(problems), 1, (wanted, problems))
            self.assertIn(wanted, problems[0])

    def test_the_build_files_come_from_the_lake_project_of_the_lean_environment(self):
        project, entry = self.lake_project('v4.36.0', '\n[[lean_lib]]\nname = "Env"\n')
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
        # A name can hold an apostrophe, and so can the statement that `#check` prints on the line before it.
        printed = ("Small.root (n : Nat) : x\n'Small.root' depends on axioms: [propext,\n Classical.choice,\n Quot.sound]\n"
                   "'Small.clean' does not depend on any axioms\n'Small.open' depends on axioms: [sorryAx]\n"
                   "Small.step' (h' : x) : y\n'Small.step'' depends on axioms: [propext]\n"
                   "'Small.end'' does not depend on any axioms\n")
        self.assertEqual(package.axioms_printed(printed), {'Small.root': ['propext', 'Classical.choice', 'Quot.sound'],
                                                           'Small.clean': [], 'Small.open': ['sorryAx'],
                                                           "Small.step'": ['propext'], "Small.end'": []})


class ArchiveTests(FinalizeCase):
    def test_the_archive_is_the_commit_with_the_account_name_replaced_and_the_ledger_points_into_it(self):
        # The research wrote paths of its machine into a text of the canon: the home folder of the account `pat` with
        # either separator, with the doubled backslash of a JSON string, and as another system writes it; the home
        # folder of another account, whose name begins with that name; and a folder that is no home folder. The
        # name stands there as a word by itself too, and as a part of the word "path".
        paths = ('Computed in C:\\Users\\{0}\\work and C:/Users/{0}/work, logged under "C:\\\\Users\\\\{0}\\\\log.json", '
                 'and on the server in /home/{0}/work. Checked in /home/patricia/work. The data is in D:\\srv\\pat\\data. '
                 'Run by pat along the path above.\n')
        commit = self.noted(paths.format('pat'))
        info = package.knowledge_archive(self.instance, commit, self.root / 'knowledge', 'odd', 'pat')
        archive = self.root / 'knowledge' / 'odd-knowledge.tar.xz'
        members = package.archive_members(archive)
        tree = {}
        for line in git(self.instance, 'ls-tree', '-r', '-z', commit, '--', 'canon', 'knowledge').split('\0'):
            if line:
                head, path = line.split('\t', 1)
                tree[path] = head.split()[2]
        blob = lambda data: hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        # Every member has its path, and the bytes of the commit but for the name inside the paths of the home folder.
        self.assertEqual({path: blob(data.replace(b'<account>', b'pat')) for path, data in members.items()}, tree)
        self.assertTrue(members['canon/questions/q0.md'].decode('utf-8').endswith(paths.format('<account>')))
        self.assertEqual((info['files'], info['touched']), (len(tree), 1))
        manifest = (self.root / 'knowledge' / 'MANIFEST.md').read_text(encoding='utf-8')
        self.assertEqual(package.manifest_sha(self.root / 'knowledge' / 'MANIFEST.md'), package.sha256_file(archive))
        self.assertIn('1 files were touched', manifest)
        self.assertIn(commit, manifest)
        # The same commit gives the same archive.
        again = package.knowledge_archive(self.instance, commit, self.root / 'again', 'odd', 'pat')
        self.assertEqual(again['sha256'], info['sha256'])
        # A name that stands in the research only as a word by itself is replaced nowhere: `Small` is the library.
        self.assertEqual(package.knowledge_archive(self.instance, commit, self.root / 'word', 'odd', 'Small')['touched'], 0)
        # A home folder that lies neither under `Users` nor under `home` is known by its own path.
        with patch.object(Path, 'home', return_value=Path('D:/srv/pat')):
            package.knowledge_archive(self.instance, commit, self.root / 'elsewhere', 'odd', 'pat')
        elsewhere = package.archive_members(self.root / 'elsewhere' / 'odd-knowledge.tar.xz')['canon/questions/q0.md']
        self.assertIn(b'The data is in D:\\srv\\<account>\\data.', elsewhere)
        rows = package.ledger({path: data for path, data in members.items()
                               if path.startswith(('knowledge/', 'canon/approaches/', 'canon/questions/'))})
        self.assertEqual([(row['event'], row['kind']) for row in rows], [(1, 'change'), (2, 'question')])
        self.assertEqual(rows[0]['title'], 'A contribution')
        self.assertEqual(rows[0]['review'], 'Useful work.')
        self.assertEqual(rows[0]['contribution'], 'Closed what it took on.')
        self.assertIn('Small.sq_step', rows[0]['elements'])
        self.assertTrue(all(row['record'] in members for row in rows))
        self.assertEqual(rows[1]['record'], 'canon/questions/q0.md')
        beside = package.event_members(rows[0], list(members))
        self.assertIn(rows[0]['record'], beside)
        self.assertTrue(all(name.startswith(rows[0]['record'].rsplit('/', 1)[0] + '/') for name in beside))
        self.assertEqual(rows[0]['by'], 'attempt')  # the kind of session whose work the publication carries
        self.assertEqual(rows[1]['by'], '')
        # What was tried on a statement that was proved later stands in the canon's history, and is a line too.
        tried = package.ledger({'canon/history/Small/root/000001-approaches/by-induction.md':
                                b'---\ntitle: Induction on n\n---\n## Idea\n\nInduct.\n',
                                'canon/history/Small/root/000001-record.md': b'An earlier record.\n'})
        self.assertEqual([(row['kind'], row['title'], row['elements'], row['record']) for row in tried],
                         [('approach', 'Induction on n', ['Small.root'],
                           'canon/history/Small/root/000001-approaches/by-induction.md')])
        # A change says which questions it resolves, and review judges each resolution. One that review did not
        # accept resolved nothing, so the line of the change does not name its question.
        judged = package.ledger({name: json.dumps(value).encode('utf-8') for name, value in {
            'knowledge/events/1.json': {'sequence': 1, 'kind': 'change', 'folder': 'changes/c1'},
            'knowledge/changes/c1/change.json': {'resolutions': [{'id': 'r1', 'question': 'q1'},
                                                                 {'id': 'r2', 'question': 'q2'}]},
            'knowledge/changes/c1/assessment.json': {'resolutions': [{'proposal': 'r1', 'resolved': True},
                                                                     {'proposal': 'r2', 'resolved': False}]},
            # The other three kinds of publication: a comprehensive review, an organization, questions of the operator.
            'knowledge/events/2.json': {'sequence': 2, 'kind': 'review', 'folder': 'reviews/v1'},
            'knowledge/reviews/v1/assessment.json': {'findings': [
                {'reason': 'The induction skips a case.', 'invalidates': ['Small.b'], 'validates': ['Small.a'],
                 'reopens': ['q1']}]},
            'knowledge/events/3.json': {'sequence': 3, 'kind': 'organization', 'folder': 'organizations/o1'},
            'knowledge/organizations/o1/organization.json': {'merge_questions': [{'from': 'q2', 'into': 'q1'}]},
            'knowledge/organizations/o1/applied.json': {'added': ['Small.joined']},
            'knowledge/events/4.json': {'sequence': 4, 'kind': 'questions', 'folder': 'questions/e1'},
            'knowledge/questions/e1/questions.json': {'reason': 'The user asked.',
                                                      'questions': [{'id': 'q3', 'statement': 'Is it sharp?'}]},
        }.items()})
        self.assertEqual(judged[0]['questions'], ['resolves q1'])
        # Each is a line with the kind of session it comes from, its elements, its questions and its record.
        self.assertEqual([(row['kind'], row['by'], row['title'], row['elements'], row['questions'], row['record'])
                          for row in judged[1:]],
                         [('review', 'review', 'A comprehensive review', ['Small.a', 'Small.b'], ['reopens q1'],
                           'knowledge/reviews/v1/assessment.json'),
                          ('organization', 'organizer', 'An organization of the canon', ['Small.joined'],
                           ['merges q2 into q1'], 'knowledge/organizations/o1/organization.json'),
                          ('questions', 'operator', 'Questions placed by the operator', [], ['q3: Is it sharp?'],
                           'knowledge/questions/e1/questions.json')])
        self.assertEqual((judged[1]['review'], judged[3]['description']),
                         ('The induction skips a case.', 'The user asked.'))
        listed = [{'group': 'Steps', 'items': ['`Small.sq_step`:  the step of the square']},
                  {'group': '', 'items': ['`Small.twice`: doubling']}]
        text = package.timeline([{**rows[0], 'text': 'A change   gave the root its proof.', 'list': listed},
                                 {**rows[1], 'text': 'The question was understood.'},
                                 {**tried[0], 'text': 'Induction was tried first.'}], 'Small.root')
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
        # What was tried on a statement stands under the statement and the title of the approach, between the
        # publications and the questions.
        self.assertIn('### `Small.root`: Induction on n\n\nInduction was tried first.\n\n'
                      'Record: `canon/history/Small/root/000001-approaches/by-induction.md`\n', text)
        self.assertLess(text.index('## Publications'), text.index('## What was tried on each statement'))
        self.assertLess(text.index('## What was tried on each statement'),
                        text.index('## What was understood of each question'))

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
                               # A record has formulas between dollar signs and names of elements between backticks.
                               # A bracket before a parenthesis there is mathematics or code, and no link.
                               ('records/Small/root.md', 'The coefficient $[X^n](fg)$, displayed\n$$[X^n](gf),$$\n'
                                                         'and `coeff[n](fg)`.\n'),
                               ('history/timeline.md', '# History\n'),
                               ('README.md', '# Title\n\n[the timeline](history/timeline.md) and [a site](https://example.org/a)\n'),
                               ('dependency-map/dependency_map.html', '<a href="dependency_map.svg">map</a>\n'),
                               ('dependency-map/dependency_map.svg', '<svg/>\n')):
            (folder / relative).parent.mkdir(parents=True, exist_ok=True)
            (folder / relative).write_text(text, encoding='utf-8', newline='\n')
        # The research wrote a path of a home folder into a text of its canon, and the archive is made under another account.
        package.knowledge_archive(self.instance, self.noted('Computed in /home/pat/work.\n'), folder / 'knowledge', 'odd',
                                  'no-such-account')
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

        # A link that stands between two formulas is a link.
        faulty('README.md', 'For $n$, see [the notes](history/absent.md) on $s(n)$.\n',
               'README.md: the link history/absent.md does not resolve')
        faulty('README.md', '[out](../outside.md)\n', 'the link ../outside.md does not resolve inside the package')
        faulty('dependency-map/dependency_map.html', '<img src="missing.svg">\n', 'the link missing.svg')
        faulty('history/timeline.md', 'Computed in C:\\Users\\pat\\work.\n',
               'history/timeline.md holds the account name inside a path of a home folder', account='pat')
        # The name as a word by itself is no fault: `oddSum` is a definition of the library. The files that hold it so
        # are found for the report of the run, a member of the archive after the archive.
        self.assertEqual(check('oddSum'), [])
        words = package.account_words(folder, 'oddSum')
        self.assertLessEqual({'lean/Small/Defs.lean', 'knowledge/odd-knowledge.tar.xz, member canon/lean/Small/Defs.lean'},
                             set(words))
        self.assertNotIn('README.md', words)
        # A word of which the name is only a part is not the name: the manifest of the archive says "machine".
        self.assertEqual(package.account_words(folder, 'achin'), [])
        # The archive is read by its members and not by its packed bytes, in which a name can stand only by chance.
        # Those bytes begin with the signature of the format, which holds `7zXZ`, and no member has that word.
        self.assertEqual(package.account_words(folder, '7zXZ'), [])
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
        # A JSON file writes the end of a line inside a text as a backslash and a letter, so a statement with a line
        # that ends in "case A:" stands there as `A:\n`, which is no drive path. The same holds for the YAML that the
        # program writes with JSON's strings. A path in its form with a slash is found in such a file as well.
        (folder / 'paper' / 'correspondence.json').write_text(
            json.dumps({'paper_statement': 'In case A:\nthe sum is even.'}), encoding='utf-8', newline='\n')
        (folder / 'lean' / 'formalization.yaml').write_text(
            'scope: ' + json.dumps('In case A:\nthe sum is even.') + '\n', encoding='utf-8', newline='\n')
        freeze = package.freeze_hashes(folder)
        (folder / 'MANIFEST.sha256').write_text(package.manifest_text(folder), encoding='utf-8', newline='\n')
        self.assertEqual(check(), [])
        faulty('paper/correspondence.json', json.dumps({'paper_statement': 'Built in D:/lean-work.'}),
               'paper/correspondence.json holds a drive path')
        # A member of the archive that holds the account name inside a path of a home folder is found inside the archive.
        self.assertEqual(check('pat'), ['knowledge/odd-knowledge.tar.xz: the member canon/questions/q0.md holds the account '
                                        'name inside a path of a home folder'])
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
        # The file is the repository's and keeps the line endings it has: a checkout on Windows gives it CRLF.
        windows = self.root / 'windows.md'
        windows.write_bytes(b'# R\r\n\r\n## Solved problems\r\n\r\n- An earlier one.\r\n')
        package.add_solved_entry(windows, 'odd', entry)
        self.assertEqual(windows.read_bytes(), b'# R\r\n\r\n## Solved problems\r\n\r\n- An earlier one.\r\n'
                         + entry.encode('utf-8') + b'\r\n')
        unix = self.root / 'unix.md'
        unix.write_bytes(b'# R\n')
        package.add_solved_entry(unix, 'odd', entry)
        self.assertEqual(unix.read_bytes(), b'# R\n\n## Solved problems\n\n' + entry.encode('utf-8') + b'\n')


class PaperRunTests(FinalizeCase):
    reads_the_instance = True

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


class BuildTests(FinalizeCase):
    reads_the_instance = True

    def test_a_broker_that_does_not_come_up_stops_the_step_and_is_no_fault_of_the_library(self):
        # What `build` returns as faults goes to a session as the faults of its output, and a part is discarded for
        # them. A broker that does not come up is raised instead, as the error with which a step stops the run.
        run = finalize.Run(self.instance, 'odd', finalize.default_config())
        run.library, run.expect_mb = 'Small', 64
        absent = RuntimeError('No Lean broker became ready')
        with patch('finalize.Run.ensure_broker'), patch('finalize.BROKER_SECONDS', 0), \
                patch('canon.start_build', side_effect=absent) as asked, self.assertRaises(RuntimeError) as raised:
            run.build(self.instance / 'canon' / 'lean', False, None, None, None)
        self.assertEqual(str(raised.exception),
                         'the Lean broker of the run does not stay alive: No Lean broker became ready')
        self.assertEqual(asked.call_count, 6)  # asked once, and once more after each of five waits

    def test_a_broker_that_was_started_and_has_not_written_its_receipt_ends_with_the_run(self):
        # A broker writes its receipt some seconds after it was started. A run that stops within those seconds finds
        # no receipt; a broker left behind then would go on holding broker.log in the work folder. The stand-in is a
        # broker that never gets as far as its receipt, started as the watcher starts one and as the client inside a
        # build does.
        slow = self.root / 'slow_broker.py'
        slow.write_text('import time\ntime.sleep(120)\n', encoding='utf-8')
        with patch('finalize.REPOSITORY', self.repository):
            run = finalize.Run(self.instance, 'odd', finalize.default_config())
        paths = lean_broker.Paths(run.work)

        def ended():
            for process in lean_broker.started_brokers(paths):
                process.kill()
                process.wait()

        self.addCleanup(ended)
        with patch('lean_broker.SCRIPT', slow):
            run.ensure_broker()
            lean_broker.launch_broker(paths)
            started = lean_broker.started_brokers(paths)
            self.assertEqual(len(started), 2)
            self.assertIsNone(lean_broker.broker_alive(paths))  # they run, and there is no receipt of either
            run.stop_broker()
            self.assertEqual([process.poll() is None for process in started], [False, False])
            run.broker_attempt = float('-inf')
            run.ensure_broker()  # the watcher's next look, were it to come after the stop
            self.assertEqual(lean_broker.started_brokers(paths), [])

    def test_the_command_holds_the_broker_module_from_its_start(self):
        # A run lasts hours, and the files of the skill can change under it. A module that the command first loaded in
        # the middle of a run would come from the files as they then are, beside the modules loaded at the start, and
        # fails where it names something those do not have. So a fresh process that has imported finalize.py already
        # holds the broker module, which a run first uses some seconds or minutes after it began.
        probe = 'import sys; sys.path.insert(0, sys.argv[1]); import finalize; print("lean_broker" in sys.modules)'
        result = subprocess.run([sys.executable, '-B', '-c', probe, str(THIS.parents[1])], capture_output=True, text=True,
                                timeout=120)
        self.assertEqual((result.returncode, result.stdout.strip()), (0, 'True'), result.stderr)


class EndTests(FinalizeCase):
    reads_the_instance = True

    def test_a_package_that_cannot_be_moved_stays_whole_in_the_work_folder(self):
        # The package goes into solved/ by one rename, which moves all of it or nothing. Here a folder stands where
        # the package is to go: the end fails, the package is not put inside that folder, and both stay as they were.
        with patch('finalize.REPOSITORY', self.repository):
            run = finalize.Run(self.instance, 'odd', finalize.default_config())
        for relative in ('freeze.json', 'facts.json', 'lib/0-selected/decision.json'):
            package.write_json(run.work / relative, {})
        package.write_text(run.package / 'README.md', '# The package\n')
        package.write_text(run.solved / 'kept.md', 'It stood here before the run came to its end.\n')
        with self.assertRaises(FileExistsError):
            run.finish()
        self.assertEqual(set(package.files_under(run.package)), {'README.md'})
        self.assertEqual(set(package.files_under(run.solved)), {'kept.md'})


class StepTests(FinalizeCase):
    reads_the_instance = True

    def test_a_step_that_is_entered_again_decides_anew_and_stage_3_leaves_the_decisions_as_they_are(self):
        # A step that stopped is made again from its start, and what its first start decided may no longer be so.
        # Here the part that the first start discarded is accepted by the second, and decisions.md says that alone.
        with patch('finalize.REPOSITORY', self.repository):
            run = finalize.Run(self.instance, 'odd', finalize.default_config())
        run.state = {'steps': {}}
        run.decide('Stage 0: start', 'The research is read.')
        run.sessions = finalize.Sessions(self.instance, run.work)

        def halts():
            raise paper.Stop('halted for the test')

        def discards():
            run.decide('Step 3: the simplification of the part aux', 'Discarded; that part keeps the form it had.')
            halts()

        # Stage 3 is entered first, before a step of the library has decided anything, and stops.
        with self.assertRaises(finalize.Halt):
            run.step('3-history', [], [], halts, decides=False)
        with self.assertRaises(finalize.Halt):
            run.step('2.3-simplify', [], [], discards)
        self.assertIn('Discarded', self.decisions())
        run.step('2.3-simplify', [], [], lambda: run.decide('Step 3: the parts', 'Every part was accepted.'))
        # Entered again after that, stage 3 takes nothing away from what the step of the library decided.
        run.step('3-history', [], [], lambda: None, decides=False)
        self.assertEqual(self.decisions(), '# Decisions of the run\n\n## Stage 0: start\n\nThe research is read.\n'
                                           '\n## Step 3: the parts\n\nEvery part was accepted.\n')
        self.assertEqual(list(read_json(run.work / 'state.json')['steps']), ['2.3-simplify', '3-history'])
        # A value that the work of a step returns is entered with the step and not before. A state that is saved
        # while the step is under way, as a step of stage 3 saves it, holds neither the value nor the step.
        saved = []

        def renames():
            run.save()
            saved.append(read_json(run.work / 'state.json'))
            return {'main': 'Small.renamed'}

        run.state['main'] = 'Small.chosen'
        run.step('2.4-arrange', [], [], renames, decides=False)
        self.assertEqual((saved[0]['main'], '2.4-arrange' in saved[0]['steps']), ('Small.chosen', False))
        state = read_json(run.work / 'state.json')
        self.assertEqual((state['main'], '2.4-arrange' in state['steps']), ('Small.renamed', True))


class PromptTests(FinalizeCase):
    reads_the_instance = True

    def prepared(self):
        run = finalize.Run(self.instance, 'odd', finalize.default_config())
        run.settings, run.library, run.root, run.expect_mb = {'lean': {'cwd': None}}, 'Small', 'Small.root', 64
        run.state = {'main': 'Small.sq_step'}
        return run

    def test_every_instruction_file_of_the_skill_is_filled_with_the_names_the_command_gives(self):
        run = self.prepared()
        common = package.read_text(INSTALLED / 'finalize' / 'common.md')
        # The two sections on Lean that every session has except those that work on the history, on the README or on
        # the finished package, and what only the section on compiling holds, which only a session whose step writes
        # Lean has.
        lean = ('## Reading the imported library\n', '## What every Lean file of the library keeps\n')
        compiling = ('## Compiling\n', INSTALLED.as_posix() + '/runtime/lean_broker.py', '--expect-mb 64')
        for name in INSTRUCTIONS:
            text = run.prompt(name, {'part': 'core'} if name in ('simplify', 'foldback') else None)
            self.assertTrue(text.startswith(common.split('{{')[0]), name)
            self.assertIn('\n## One proof, presented by itself\n', text, name)
            given = name not in ('history-write', 'history-read', 'readme-write', 'package-read')
            self.assertEqual([part in text for part in lean], [given] * len(lean), name)
            compiles = name in ('selection', 'restore', 'simplify', 'arrange', 'foldback')
            self.assertEqual([part in text for part in compiling], [compiles] * len(compiling), name)
            if compiles:
                self.assertIn(Path(sys.executable).as_posix(), text, name)
        self.assertIn('There is none', run.prompt('review'))
        run.settings = {'lean': {'cwd': 'C:/toolchains/mathlib'}}
        self.assertIn('C:/toolchains/mathlib', run.prompt('review'))

    def test_a_name_the_command_does_not_give_stops_the_run_and_is_named(self):
        (self.skill / 'finalize' / 'review.md').write_text('Review {{library}} in {{folder}}.\n', encoding='utf-8')
        (self.skill / 'finalize' / 'simplify.md').write_text('Simplify the part {{part}} in {{folder}}.\n', encoding='utf-8')
        run = self.prepared()
        with patch('finalize.SKILL', self.skill), self.assertRaises(paper.Stop) as raised:
            run.prompt('review')
        self.assertIn('review.md uses {{folder}}', str(raised.exception))
        # A part is discarded for what its sessions left. This fault of its instruction stops the run like any other.
        with patch('finalize.SKILL', self.skill), self.assertRaises(paper.Stop) as raised:
            run.discardable('Step 3: the simplification of the part core', lambda: run.task(
                'simplify', 'simplify', {}, None, None, names={'part': 'core'}))
        self.assertIn('simplify.md uses {{folder}}', str(raised.exception))


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
        # A later stage cannot use an empty field of an author or a reviewer that is no name, and the configuration
        # of a run that has begun cannot be changed, so both are refused here.
        self.refused('each a text that is not empty', config=self.config(authors=[{'name': 'A. Author', 'email': ''}]))
        self.refused('"reviewers" (a list of names)',
                     config=self.config(human_review={'status': 'self-assessed', 'reviewers': [{'name': 'R. Reader'}]}))
        self.refused('"parallel" is the number of sessions', config={'parallel': 0})
        self.refused('no licence text for MIT', config=self.config(licence='MIT'))
        with patch.dict(sys.modules, {'yaml': None}):
            self.refused('has no PyYAML', config=self.config())
        self.refused('was not found', config={'tex': ['no-such-tex-command']})
        self.solved.mkdir(parents=True)
        self.refused(f'{self.solved} exists', config=self.config())
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

    def test_a_lean_environment_from_which_the_build_files_cannot_be_taken_is_refused(self):
        # The freeze takes the toolchain and the `[[require]]` blocks of the package from the Lake project that the
        # settings name as `lean.cwd`. A project without a lakefile.toml, as a checkout of Mathlib itself is, would
        # stop the run at the freeze, after every session of the library, and no new start would get past it.
        project = self.root / 'project'
        project.mkdir()
        write_json(project / 'lake-manifest.json', {'version': '1.3.0', 'packagesDir': '.lake/packages', 'packages': []})
        (project / 'lean-toolchain').write_text('leanprover/lean4:v4.99.0\n', encoding='utf-8')
        (project / 'lakefile.lean').write_text('import Lake\n', encoding='utf-8')
        self.configure(lean={'cwd': str(project)})
        self.refused('declares its dependencies in lakefile.lean', config=self.config())

    def test_a_research_that_changed_a_definition_module_is_refused(self):
        # Every step that writes Lean requires the definition modules as the first commit has them. A run on a
        # research that changed one would stop at the take, after the sessions of the selection, and no new start
        # would get past it.
        with (self.instance / 'canon' / 'lean' / 'Small' / 'Defs.lean').open('ab') as module:
            module.write(b'-- a line that a publication added\n')
        git(self.instance, 'commit', '-m', 'a changed definition module', '--', 'canon/lean/Small/Defs.lean')
        self.refused('the definition module Small.Defs is not the file of the first commit', config=self.config())

    def test_a_run_whose_paper_is_still_to_be_written_is_not_continued_without_a_tex_command(self):
        # Where the configuration names no TeX command, the command is the first engine on PATH. When a run is
        # continued and none is found, the paper command would write the whole paper and end it untypeset, and no
        # later start of this command takes such a paper up. So the start refuses, as the start of a new run does.
        self.from_the_records()
        events = lambda: [event['event'] for event in read_json(self.work / 'log.json')]
        with patch('paper.tex_recipe', return_value=None):
            self.assertEqual(self.run_command(config=self.config()), 1, self.said)
        self.assertIn('no TeX command is available', self.said)
        self.assertEqual((self.produced, events().count('resume')), ([], 0))  # nothing was launched or entered
        # With a TeX command the same command continues the run where it had stopped.
        with patch('finalize.Run.draft', side_effect=paper.Stop('halted for the test')):
            self.assertEqual(self.run_command(config=self.config()), 2, self.said)
        self.assertEqual(events().count('resume'), 1)

    def test_a_command_given_while_another_is_at_work_for_the_name_is_refused(self):
        # A command that is at work holds the lock beside its work folder. It is held here as that command holds it.
        lock = self.work.with_name('finalize-odd.lock')
        with finalize.alone(self.work):
            self.refused('another command is at work in', config=self.config())
            self.assertFalse(self.work.exists())
            self.assertTrue(lock.is_file())  # the refused command left the lock of the other alone
        self.assertFalse(lock.exists())  # and the command that held the folder took its lock away with it

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
        # The instance's compile service is still at work: two files of its store stand under the names it writes
        # them to first, not yet moved into place. Such a file is not seeded.
        store = self.instance / 'runner' / 'lean' / 'cache'
        unfinished = {'.' + 'b' * 32 + '.olean.' + 'a' * 32, 'b' * 32 + '.artifacts.json.' + 'a' * 32 + '.tmp'}
        for name in unfinished:
            (store / name).write_bytes(b'half a file')
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
        # The run's compile service is its own, and began with what the instance's had compiled: the files of its
        # store that were in place, and not the two that were not yet moved there.
        cached = {path.name for path in store.iterdir()} - unfinished
        seeded = {path.name for path in (self.work / 'runner' / 'lean' / 'cache').iterdir()}
        self.assertTrue(cached)
        self.assertLessEqual(cached, seeded)
        self.assertFalse(unfinished & seeded)
        self.assertTrue((self.work / 'runner' / 'lean' / 'broker.log').is_file())

    def test_the_definition_modules_are_those_of_the_module_the_root_was_posed_in(self):
        # The root's own module is not locked, and an organizer moves declarations between modules until a proof
        # stands under its statement (roles/organizer.md), so the root can stand in another module than the one it
        # was posed in. The definition modules and the challenge go by the module that held the root in the first
        # commit, as the runner's lock on those modules does (canon.definition_modules). The head commit is made by
        # hand here, as in the test of a changed definition module above: its index names for the root a module
        # that the first commit does not have. The run is stopped at its first two steps.
        index = self.instance / 'canon' / 'index.json'
        moved = read_json(index)
        moved['entries']['Small.root']['module'] = 'Small.Step'
        write_json(index, moved)
        git(self.instance, 'commit', '-m', 'the root in another module', '--', 'canon/index.json')
        halted = paper.Stop('halted for the test')
        with patch('finalize.Run.selection', side_effect=halted), patch('finalize.Run.archive', side_effect=halted):
            self.assertEqual(self.run_command(script(), config=self.config()), 2, self.said)
        state = read_json(self.work / 'state.json')
        self.assertEqual((state['definitions'], state['posed_module'], state['root_module']),
                         (['Small.Defs'], 'Small.Root', 'Small.Step'))

    def test_the_script_refuses_a_command_line_it_cannot_read(self):
        # Run as the file the operator runs, so that what the script does before it reads its arguments runs too.
        # Without --name the command line cannot be read, and the run does not begin.
        result = subprocess.run([sys.executable, '-B', str(THIS.parents[1] / 'finalize.py'), str(self.instance)],
                                capture_output=True)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertTrue(result.stderr.startswith(b'usage:'), result.stderr)


class RunTests(FinalizeCase):
    def test_a_run_comes_to_its_end_with_the_package_in_place(self):
        config = self.config(authors=[{'name': 'A. Author', 'email': 'a@example.org', 'orcid': '0000'}])
        # The repository is under Git, as the one that holds the skill is, with its README committed.
        git = lambda *arguments: subprocess.run(['git', '-C', str(self.repository), '-c', 'user.name=t', '-c', 'user.email=t@t',
                                                 *arguments], check=True, capture_output=True, text=True).stdout.strip()
        git('init')
        git('add', 'README.md')
        git('commit', '-m', 'before the run')
        head = git('rev-parse', 'HEAD')
        self.assertEqual(self.run_command(script(), config=config), 0, self.said)
        # The run commits nothing: the head is the commit it found, nothing is staged, and the package and the entry in
        # the README stand in the working tree alone.
        self.assertEqual((git('rev-parse', 'HEAD'), git('diff', '--cached', '--name-only')), (head, ''))
        self.assertEqual(git('ls-files'), 'README.md')
        # The order of the stages is the program's: each step of the library stage after the one before it.
        steps = self.steps()
        main = [step for step in steps if not step.startswith('3-')]
        self.assertEqual(main, ['1-selection', '2.1-take', '2.2-review', '2.3-simplify', '2.4-merge', '2.4-arrange',
                                '2.5-records', '2.6-draft', '2.6-sources', '2.6-foldback', '2.6-records', '2.6-compare',
                                '2.7-freeze',
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

        # What each session was given, as the part "What you are given" of its instruction file lists it.
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
        # The title page names the authors, and the subject classification that the selection chose for the registry.
        self.assertEqual(written['title_page'], {'authors': [{'name': 'A. Author', 'email': 'a@example.org'}],
                                                 'msc2020': ['05A15']})
        # What the works say at the places where the records cite them goes to the paper with the draft.
        self.assertEqual(written['drafted']['attributions'], [{'key': 'gauss1801', **QUOTED}])
        self.assertEqual(written['drafted']['instances'], [])
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
        # Check.lean imports the module of each theorem it asks about. Lean loads for it what the root's module
        # imports only where that import is `public`, so the module of the main theorem is named there itself.
        self.assertTrue((self.solved / 'lean' / 'Check.lean').read_text(encoding='utf-8').startswith(
            'module\n\nimport Small.Root\nimport Small.Step\n\n'))
        meta = yaml.safe_load((self.solved / 'lean' / 'formalization.yaml').read_text(encoding='utf-8'))
        # The ORCID iD of the author goes with the name into the registry's file; the maintainer is named alone.
        self.assertEqual((meta['project']['name'], meta['project']['authors'], meta['project']['responsible_maintainers']),
                         ('Odd numbers sum to squares', [{'name': 'A. Author', 'orcid': '0000'}], ['A. Author']))
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
        # A record names a file of the research by its path under `evidence/`. The package has that file inside the
        # archive alone, so the README says where the path leads.
        self.assertIn('Where a record names a file under `evidence/`, that file is in the knowledge archive, under '
                      '`canon/evidence/`.', readme)
        # The models are those of the sessions that made the package; nothing is said of the models of the research.
        self.assertIn('The sessions that made this package from the research ran on ', readme)
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
        # So is what the comparer of a record says of its correction, where it also says what it could not compare.
        self.assertIn('## Step 6: what the comparison of the records corrected\n\n- `Small.sq_step_strict`: A word.\n',
                      decisions)
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
        self.assertIn(f'{self.solved} exists', self.said)

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
        self.assertIn('put it back as it was', report)  # the remedy that the operator's guide gives
        self.assertEqual(len(self.calls('review')), 2)
        helper.write_bytes(original)

        # A run of other arguments is not continued.
        self.assertEqual(self.run_command(script(), config=self.config(parallel=3)), 1)
        self.assertIn('differs from this one in: configuration', self.said)

        # Started again with the same arguments, the run continues at the review and comes to its end.
        again = script()
        again['selection'] = [{'output/decision.json': decision(main='Small.root')}]  # would be another choice, were it asked
        self.closed = CLOSED  # what the paper command of this start closes without a person
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
        self.assertEqual(self.produced[-1]['title_page'], {'authors': [], 'msc2020': ['05A15']})
        # What the paper command closed without a person is in the decisions and in the report.
        decisions, report = self.decisions(), (self.work / 'report.md').read_text(encoding='utf-8')
        self.assertIn('## Stage 4: what the paper lost so that it says no more than the library', decisions)
        self.assertIn('- Removed from the abstract: "equivalently, the block sums to a difference of squares" It asserted: '
                      'The block sum is a difference of squares. The declaration that came nearest is `Small.sq_step`. It '
                      'states the sum additively.', decisions)
        # A passage that went for what it said of a cited work is recorded with that work, and the report counts it.
        self.assertIn('- Removed from the proof of Lemma 1.1: "as Gauss shows for every block" It said of the cited work '
                      '`gauss1801` something that the words copied from that work do not show. The words kept of the '
                      'work speak of the single step.', decisions)
        self.assertIn('- Lemma 1.1 (`lem:step`) was restated as its declaration `Small.sq_step` says it.', decisions)
        self.assertIn('The comparison after the restatement still found a difference: The range of n.', decisions)
        self.assertIn('it took 2 passages out of the paper (each asserted what no declaration states, or said of a '
                      'cited work what the words copied from it do not show) and restated 1 statements', report)
        self.assertIn('- In the paper, Lemma 1.1 still differs from the declaration `Small.sq_step` that it states: The '
                      'range of n.', report)
        # A passage that a repair wrote during the closing pass and that no declaration covers stays, and both say so.
        self.assertIn('- Stays in the running text of the section "The step": "Hence every block sum is positive."', decisions)
        self.assertIn('The passage asserts: The block sums are positive. The declaration that came nearest is '
                      '`Small.sq_step`. No declaration bounds a block sum.', decisions)
        self.assertIn('the running text compared with the declarations, which cover it except for the passages listed '
                      'under what was not verified.', report)
        self.assertIn('- In the paper, 1 passages of the running text assert what no declaration states', report)
        # A statement that a repair of the typesetting changed and that then differs stays as it is, and so does a
        # line that is still too wide. The decisions have each, and the report lists both as not verified.
        self.assertIn('- Theorem 1.2 (`thm:main`) differs from its declaration `Small.root` after a repair of the '
                      'typesetting changed its text, and stays as it is: The sum starts at 1.', decisions)
        self.assertIn('- A line of the typeset paper is wider than the text block: paper.tex, line 40: TeX set a line '
                      '12pt wider than the text block', decisions)
        self.assertIn('- In the paper, Theorem 1.2 still differs from the declaration `Small.root` that it states: The '
                      'sum starts at 1.', report)
        self.assertIn('- 1 lines of the typeset paper are wider than the text block; `decisions.md` names them.', report)
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
            # The first claim has no verdict. The second does not hold and does not say whether it is printed.
            'selection-read': {'output/reading.json': json.dumps({'claims': [
                {'option': 'a', 'claim': 'It rests on the step.'},
                {'option': 'a', 'claim': 'It has four modules.', 'holds': False, 'correction': 'It has three.',
                 'changes_comparison': False}]})},
            'review': {'output/review.json': json.dumps({'parts': [{'id': 'core', 'modules': ['Small.Root', 'Small.Helper']}],
                                                         'cross': [{'id': 'x1', 'owner': 'nobody', 'what': 'w'}]})},
            'simplify:core': {'output/lean/Small/Step.lean': STEP, 'output/report.json': json.dumps(
                {'deleted': [], 'cross': [{'id': 'x1', 'done': True}]})},
            'arrange': {'@copy': [['lean', 'output/lean']], 'output/lean/Small/Helper.lean': taken_helper,
                        'output/renames.json': '{}', 'output/removed.json': '[]'},
            'records-write:5-01': {'output/records/Small/added_six.md': record_text('Six terms.'), 'output/findings.json': '[]'},
            'records-compare:5-01': {'output/verdicts.json': json.dumps([{'declaration': 'Small.added_six', 'verdict': 'agrees'}])},
            # The second entry is of a work that no record cites: it keeps words of the work and names no sentence.
            'sources': {'@copy': [['bibliography.bib', 'output/bibliography.bib']], 'output/requests.json': '[]',
                        'output/sources.json': json.dumps([
                            {'status': 'verified', 'identifier': 'isbn:1'},
                            {'key': 'euler1748', 'status': 'verified', 'identifier': 'isbn:2', 'opened': 'parts',
                             'attributions': [{'declaration': 'Small.sq_step', 'place': 'Chapter 1',
                                               'quote': 'Words of the work.'}]}])},
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
            # The first file uses a figure that facts.json does not have, and the second links to a file that the
            # package does not have.
            'readme-write': {'output/outline.md': 'The paper has {{facts.pages}} pages.\n',
                             'output/obtained.md': 'See [the notes](notes/absent.md).\n'},
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
                ('selection-read:None', 'whether the claim stands in a text that the package prints ("printed")'),
                ('review:None', 'modules in no part: Small.Step'),
                ('review:None', 'the cross-part item x1 has no owner that is a part'),
                ('simplify:core', 'Small.Step is not a module of this part'),
                ('arrange:None', 'nor among those removed: Small.added_six'),
                ('records-write:5-01', 'records/Small/named_four.md was not written'),
                ('records-compare:5-01', 'Small.named_four has no verdict'),
                ('sources:5', 'sources.json has no status of "verified" or "removed" for gauss1801'),
                ('sources:5', 'sources.json has an entry without "key"'),
                ('sources:5', 'sources.json: "attributions" of euler1748 is an array of objects'),
                ('foldback:Small', 'report.json does not say whether the item r1 is closed'),
                ('records-write:6-01', '"proves: Small.sq_step" is a claim that Lean did not confirm'),
                ('records-compare:6-01', 'records/Small/sq_step_strict.md was not written'),
                ('draft-compare:None', 'g1 is rewritten and verdicts.json does not give the text'),
                ('history-write:01', 'entries.json has no entry with a text for the event 2'),
                ('history-read:01', 'the entry of the event 2 is corrected and no text is given'),
                ('readme-write:None', 'outline.md uses {{facts.pages}}, and facts.json has no such key'),
                ('readme-write:None', 'obtained.md links to notes/absent.md, which the package does not have'),
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

    def test_a_part_that_builds_and_leaves_a_proof_open_is_discarded_at_the_merge(self):
        # A part is accepted on its build, which a proof left open passes. The merge reads the index and finds it.
        plan = script()
        plan['simplify:aux'] = [{
            'output/lean/Small/Step.lean': STEP.replace('\n\nend Small', '\n\n' + theorem('open_seven', ': oddSum 7 = 49')
                                                        + '\n\nend Small'),
            'output/report.json': json.dumps({'deleted': [], 'cross': [], 'notes': ''})}]
        # The other part moves what one of its two modules holds into the other and deletes the emptied module.
        joined = module_text('\n\n'.join([part for part in HELPER_PARTS if part != UNUSED]
                                         + [theorem('added_six', ': oddSum 6 = 36', proof='rfl'), ROOT_PROOF]),
                             imports=('Small.Defs', 'Small.Step'))
        plan['simplify:core'] = [{
            'output/lean/Small/Root.lean': joined,
            'output/report.json': json.dumps({'deleted': ['lean/Small/Helper.lean'],
                                              'cross': [{'id': 'x1', 'done': True, 'note': ''}], 'notes': ''})}]
        with patch('finalize.Run.arrange', side_effect=paper.Stop('halted for the test')):
            self.assertEqual(self.run_command(plan, config=self.config()), 2, self.said)
        self.assertIn('The run stopped at the step `2.4-arrange`', (self.work / 'report.md').read_text(encoding='utf-8'))
        self.assertEqual(read_json(self.work / 'lib' / '3-parts' / 'parts.json'), {'accepted': ['core', 'aux'], 'discarded': []})
        # The library with both parts does not pass the check of the merge, so the parts are added one at a time under
        # that check: the part that brought the open proof is discarded, and the run goes on with the other.
        self.assertEqual(read_json(self.work / 'lib' / '4-merged' / 'merge.json'), {'merged': ['core'], 'discarded': ['aux']})
        self.assertIn('The part aux was discarded: the library does not pass its check with it added. Small.open_seven is '
                      'not proved from the allowed axioms: sorryAx', self.decisions())
        merged = self.work / 'lib' / '4-merged' / 'lean' / 'Small'
        self.assertEqual((merged / 'Step.lean').read_text(encoding='utf-8'), STEP)
        # The module that the accepted part deleted is gone from the merged library, and what it held is in the other.
        self.assertFalse((merged / 'Helper.lean').exists())
        self.assertEqual((merged / 'Root.lean').read_text(encoding='utf-8'), joined)

    def test_a_manuscript_that_fails_its_typesetting_stops_the_run_and_the_next_start_writes_the_paper_anew(self):
        self.from_the_records()
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
        # At the end of this start another program holds the folder of the sessions, which Windows then refuses to delete.
        real = finalize.remove_tree

        def held(path):
            if Path(path) == self.work / 'sessions':
                raise PermissionError(13, 'The folder is in use by another program', str(path))
            real(path)

        with patch('finalize.remove_tree', side_effect=held):
            self.assertEqual(self.run_command(script(), config=self.config()), 0, self.said)
        self.assertEqual([call['resume'] for call in self.produced if call['out'] == 'paper'], [False, False])
        # The run has come to its end all the same: the package is in place, and the report names what is left.
        report = (self.work / 'report.md').read_text(encoding='utf-8')
        self.assertIn('The package is in place: `solved/odd/`', report)
        self.assertIn('## What could not be deleted', report)
        self.assertIn('- `sessions`: ', report)
        self.assertEqual(sorted(path.name for path in self.work.iterdir()), ['decisions.md', 'log.json', 'report.md', 'sessions'])

    def test_an_end_that_is_held_up_or_interrupted_is_entered_again_or_refused_by_the_next_start(self):
        self.from_the_records()
        held = PermissionError(13, 'It is in use by another program')

        def stopped_at_the_end():
            report = (self.work / 'report.md').read_text(encoding='utf-8')
            self.assertIn('The run stopped at the step `the end of the run`', report)
            self.assertIn('It is in use by another program', report)

        # The first start cannot move the package, because another program holds its folder. The run stops there as
        # a step stops it, and the package stays whole in the work folder.
        with patch('finalize.rename_directory', side_effect=held):
            self.assertEqual(self.run_command(script(), config=self.config()), 2)
        stopped_at_the_end()
        self.assertTrue((self.work / 'package' / 'README.md').is_file())
        self.assertFalse(self.solved.exists())
        # The second start moves the package, and is interrupted when the repository's README has no entry yet.
        with patch('package.add_solved_entry', side_effect=KeyboardInterrupt), self.assertRaises(KeyboardInterrupt):
            self.run_command(config=self.config())
        self.assertTrue((self.solved / 'README.md').is_file())
        self.assertFalse((self.work / 'package').exists())
        self.assertNotIn('(solved/odd/README.md)', (self.repository / 'README.md').read_text(encoding='utf-8'))
        # The third start enters the end again and cannot write the repository's README. It stops in the same way,
        # with a report of its own and not with an error of the program.
        (self.work / 'report.md').unlink()
        with patch('package.add_solved_entry', side_effect=held):
            self.assertEqual(self.run_command(config=self.config()), 2)
        stopped_at_the_end()
        # The fourth start enters the end again, and is interrupted while it deletes the files of the run.
        real = finalize.remove_tree

        def interrupted(path):
            if Path(path) == self.work / 'sessions':
                raise KeyboardInterrupt
            real(path)

        with patch('finalize.remove_tree', side_effect=interrupted), self.assertRaises(KeyboardInterrupt):
            self.run_command(config=self.config())
        self.assertEqual((self.repository / 'README.md').read_text(encoding='utf-8').count('(solved/odd/README.md)'), 1)
        self.assertIn('The package is in place: `solved/odd/`', (self.work / 'report.md').read_text(encoding='utf-8'))
        self.assertTrue((self.work / 'sessions').is_dir())
        # The run has ended. The next start refuses as after any run that ended, although files of the run are left.
        self.assertEqual(self.run_command(config=self.config()), 1)
        self.assertIn(f'{self.solved} exists', self.said)

    def test_an_interrupt_of_the_command_ends_the_session_of_the_history_that_runs_beside_the_library(self):
        # The stand-in of a session waits for the lock of the scenario, which this test holds, so the first session
        # of the history is running when the interrupt comes. It comes where Ctrl-C does, in the thread of the
        # command, which is at its first step and waits for no session of its own.
        lock = self.scenario / 'calls.lock'
        lock.write_bytes(b'')
        # Were the session not ended, the command would wait for it without end. The lock is given up after a
        # while, so that the session then records its call and the test fails.
        release = threading.Timer(30, lock.unlink)
        release.start()
        self.addCleanup(lock.unlink, missing_ok=True)
        self.addCleanup(release.cancel)
        pause = threading.Event()

        def interrupted():
            while not list((self.work / 'sessions').glob('*-history-write-01/cli.stdout.jsonl')):
                pause.wait(0.05)
            raise KeyboardInterrupt

        with patch('finalize.Run.selection', side_effect=interrupted), self.assertRaises(KeyboardInterrupt):
            self.run_command(script(), config=self.config())
        # The session was ended before it recorded its call, and the step of the history stopped for the interrupt
        # before the command came back.
        self.assertEqual(self.calls(), [])
        checks = [(event['check'], event['problems']) for event in read_json(self.work / 'log.json')
                  if event['event'] == 'check']
        self.assertIn(('exit check of 3-history', ['the command was interrupted']), checks)

    def test_a_fault_the_reader_finds_in_a_sentence_of_the_script_is_reported_and_the_run_ends(self):
        self.draft = {'statements': [DRAFT['statements'][0]], 'formulas': [], 'gaps': [], 'citations': []}
        # The selection of this run chooses the root itself as the main theorem of the package. It records the result
        # as known, and the one work it lists gives context.
        known = json.loads(decision(main='Small.root'))
        known['registry']['origin'] = 'source-based'
        # The reader of the package leaves nothing at its first two sessions, and its findings at the third.
        plan = script(selection=[{'output/decision.json': json.dumps(known)}], package_read=[{}, {}, {
            'output/findings.json': json.dumps([
                {'file': 'README.md', 'quote': 'Everything in this folder is under', 'problem': 'The licence is not named.'},
                {'file': 'README.md', 'quote': '', 'problem': 'It was not read to its end: the last section is missing here.'}])}])
        # So the first start stops in the documents stage, after the prose of the README was accepted.
        self.assertEqual(self.run_command(plan, config=self.config()), 2)
        self.assertIn('The run stopped at the step `5-documents`', (self.work / 'report.md').read_text(encoding='utf-8'))
        self.assertEqual((len(self.calls('readme-write')), len(self.calls('package-read'))), (1, 2))
        self.assertEqual(self.run_command(config=self.config()), 0, self.said)
        # No session may rewrite a sentence of the program: the finding is reported with the package, and the run ends.
        report = (self.work / 'report.md').read_text(encoding='utf-8')
        self.assertIn('## What the reader of the package found and the run did not correct', report)
        self.assertIn('- README.md, at "Everything in this folder is under": The licence is not named.', report)
        # A document that the reader could not read is reported without a quote, and is no finding in the prose.
        self.assertIn('- README.md: It was not read to its end: the last section is missing here.', report)
        # The registry asks a result that was known for a work that has it. The work that is listed gives context, so
        # the report leaves the field to the user although the list is not empty.
        self.assertIn('neither the selection nor the record of the root names a work that has it', report)
        self.assertIn('## Stage 5: what the reader of the package found and the run did not correct', self.decisions())
        # Nothing was found in the prose, so no session corrects. And the stage that was entered again gave the writer
        # of the prose the figures it had given before, so the accepted prose was not written a second time.
        self.assertEqual(len(self.calls('readme-write')), 1)
        self.assertTrue((self.solved / 'README.md').is_file())
        # With the root as the main theorem, Challenge.lean states the root once, as it was posed, and the root alone
        # is compared. The paper command is given no other main result, and the README names no second theorem.
        lean = self.solved / 'lean'
        self.assertEqual((lean / 'Challenge.lean').read_text(encoding='utf-8').count('root (n : Nat) : oddSum n = n * n'), 1)
        self.assertEqual(read_json(lean / 'comparator.json')['theorem_names'], ['Small.root'])
        self.assertEqual((lean / 'Solution.lean').read_text(encoding='utf-8'), 'module\n\npublic import Small.Root\n')
        self.assertEqual([call['main'] for call in self.produced], [None, None])
        self.assertNotIn('The library proves it from its main theorem', (self.solved / 'README.md').read_text(encoding='utf-8'))

    def halted_after_the_freeze(self, plan, **options):
        """A run that is stopped at the map, so that the freeze can be looked at in the work folder."""
        with patch('finalize.Run.depmap', side_effect=paper.Stop('halted for the test')):
            self.assertEqual(self.run_command(plan, config=self.config(), **options), 2, self.said)
        self.assertIn('The run stopped at the step `4-map`', (self.work / 'report.md').read_text(encoding='utf-8'))
        return self.work / 'package' / 'lean'

    def test_a_main_theorem_whose_statement_needs_more_than_the_definitions_is_not_compared(self):
        self.draft = {'statements': [DRAFT['statements'][0]], 'formulas': [], 'gaps': [], 'citations': []}
        # The account of this selection names three declarations. The arrangement renames one of them, and the take
        # removes another, as a later step can remove a declaration or rename it without a table.
        account = 'The proof goes through `Small.simp_one` and `Small.twice_zero`, and it leaves `Small.unused_two` aside.'
        plan = script(selection=[{'output/decision.json': decision(main='Small.twice_zero', account=account)}],
                      arrange=[{'@copy': [['lean', 'output/lean']],
                                'output/lean/Small/Helper.lean': HELPER_SIMPLIFIED.replace('simp_one', 'first_odd'),
                                'output/renames.json': json.dumps({'Small.simp_one': 'Small.first_odd'}),
                                'output/removed.json': '[]'}])
        plan['records-write:5-01'][0]['output/findings.json'] = '[]'  # the writers found nothing, and the draft has no gap
        # The record of the renamed declaration is due: the research's index has no declaration of that name.
        plan['records-write:5-01'][0]['output/records/Small/first_odd.md'] = record_text('The first odd number is one.')
        plan['records-compare:5-01'] = [{'output/verdicts.json': json.dumps([
            {'declaration': name, 'verdict': 'agrees', 'difference': ''}
            for name in ('Small.added_six', 'Small.first_odd', 'Small.named_four')])}]
        # Lake is run in the Lean environment of the settings: the stand-in fails without the variable `lean.env` gives.
        # The instance allows one axiom beyond the three of the registry, and Lean reports it for the root.
        self.configure(lean={'env': {'DO_MATH_TEST_LAKE': 'given'},
                             'allowed_axioms': ['propext', 'Classical.choice', 'Quot.sound', 'Lean.ofReduceBool']})
        lean = self.halted_after_the_freeze(plan, lake={'needs_variable': 'DO_MATH_TEST_LAKE',
                                                        'axioms': {'Small.root': ['propext', 'Lean.ofReduceBool']}})
        self.assertEqual(read_json(lean / 'comparator.json')['theorem_names'], ['Small.root'])
        self.assertNotIn('twice_zero', (lean / 'Challenge.lean').read_text(encoding='utf-8'))
        self.assertIn('the statement of the main theorem `Small.twice_zero` names declarations outside the definition '
                      'modules (`Small.twice`)', self.decisions())
        self.assertIn('#print axioms Small.twice_zero', (lean / 'Check.lean').read_text(encoding='utf-8'))
        # The root and the main theorem keep their names and statements, and the part that holds them is told so,
        # although no module of another part uses either. So does the definition that the statement of the main
        # theorem names: with another body the theorem would say something else under the same text.
        core = next(call for call in self.calls('simplify') if call['section'] == 'core')
        self.assertEqual([item['declaration'] for item in self.session_file(core, 'part.json')['interface']],
                         ['Small.root', 'Small.twice', 'Small.twice_zero'])
        freeze = read_json(self.work / 'freeze.json')
        self.assertEqual(freeze['compared'], ['Small.root'])
        # The freeze passes, since the instance allows the axiom, and the package says that the registry will not.
        self.assertEqual(freeze['fails'], ["The compared theorems depend on Lean.ofReduceBool, which the settings of the "
                                           "research allow; the registry's comparator permits propext, Quot.sound, "
                                           'Classical.choice only'])
        self.assertEqual(freeze['folders']['lean'], canon.tree_hash(lean))
        self.assertEqual(replay(self.work / 'view' / 'frozen')['root_state'], 'formal_proved')
        # The renamed declaration has its record under the new name, and the account of the selection goes to both
        # runs of the paper command with that name.
        self.assertIn('Renamed: `Small.simp_one` to `Small.first_odd`', self.decisions())
        arranged = set(package.files_under(self.work / 'lib' / '4-arranged' / 'records'))
        self.assertTrue('Small/first_odd.md' in arranged and 'Small/simp_one.md' not in arranged, arranged)
        todo = self.session_file(self.calls('records-write')[0], 'todo.json')
        self.assertEqual({item['declaration']: item['why'] for item in todo},
                         {'Small.added_six': 'new', 'Small.first_odd': 'changed',
                          'Small.named_four': 'names a declaration that is gone'})
        # The name that the library no longer has is listed after the account, for the sessions that read it.
        for view in ('4', 'frozen'):
            self.assertEqual((self.work / 'view' / view / 'canon' / 'questions' / 'q0.md').read_text(encoding='utf-8'),
                             'The proof goes through `Small.first_odd` and `Small.twice_zero`, and it leaves '
                             '`Small.unused_two` aside.\n\nThe library no longer has these declarations under the names '
                             'that the account above gives them: `Small.unused_two`.\n')
        self.assertFalse((self.work / 'stage' / 'lake').exists())
        # Nothing was to be folded back, so no fold-back session ran and nothing was built for it.
        self.assertEqual((self.calls('foldback'), self.calls('draft-compare')), ([], []))
        log = read_json(self.work / 'log.json')
        self.assertFalse([event for event in log if event['event'] == 'check' and event['check'].startswith('library fold')])
        self.assertEqual(canon.tree_hash(self.work / 'lib' / '6-folded' / 'lean'), canon.tree_hash(self.work / 'lib' / '4-arranged' / 'lean'))
        self.assertEqual([call['section'] for call in self.calls('records-write')], ['5-01'])
        # The sources step 5 verified were not verified again in step 6.
        self.assertEqual([call['section'] for call in self.calls('sources')], ['5'])

    def test_the_freeze_builds_against_the_packages_of_the_lake_project_of_the_lean_environment(self):
        # A research that imports a library has a Lake project as its Lean environment (`lean.cwd`). The package takes
        # its toolchain, its `[[require]]` blocks and its packages from that project, and the one Lake build of the
        # freeze is made on a copy whose manifest names the folder in which the environment already holds the
        # packages, so that Lake fetches nothing.
        project, entry = self.lake_project('v4.99.0')
        self.configure(lean={'cwd': str(project)})
        lean = self.halted_after_the_freeze(script())
        self.assertEqual((lean / 'lean-toolchain').read_text(encoding='utf-8'), 'leanprover/lean4:v4.99.0\n')
        self.assertIn('[[require]]\nname = "mathlib"\nrev = "v4.99.0"\n', (lean / 'lakefile.toml').read_text(encoding='utf-8'))
        # The manifest of the package names the packages folder of the published layout, and the build was made
        # against the folder of the project.
        manifest = read_json(lean / 'lake-manifest.json')
        self.assertEqual((manifest['packages'], manifest['packagesDir']), ([entry], '.lake/packages'))
        self.assertEqual(read_json(self.scenario / 'built.json'),
                         {'packagesDir': (project / '.lake' / 'packages').as_posix()})
        self.assertEqual(read_json(self.work / 'freeze.json')['requires'], 'mathlib v4.99.0')

    STRONGER = {'key': 'euler1748', 'states': 'For all $m$ and $n$, $s(m+n) = s(m) + n(2m+n)$.',
                'where': 'Chapter 1, section 2'}
    EULER = BIBLIOGRAPHY + '@book{euler1748,\n  author = {Euler, Leonhard},\n  title = {Introductio},\n  year = {1748}\n}\n'
    VERIFIED = json.dumps([{'key': 'euler1748', 'status': 'verified', 'identifier': 'isbn:2', 'opened': 'parts', 'note': ''}])
    # The same entry once a record cites the work: with the sentence of that record and the words of the work.
    ENTERED = json.dumps([{'key': 'euler1748', 'status': 'verified', 'identifier': 'isbn:2', 'opened': 'parts', 'note': '',
                           'attributions': [{'declaration': 'Small.block_sum', 'place': 'Chapter 1, section 2',
                                             'sentence': 'Every block of consecutive odd numbers has a closed sum.',
                                             'quote': 'The stand-in words of the work at that place.'}]}])

    def asking_to_cite(self):
        """A scenario whose draft asks to cite `Small.helper_zero`, of which the search finds a stronger form in a source."""
        self.draft = {**DRAFT, 'citations': [{'element': 'Small.helper_zero', 'result': 'the empty sum',
                                              'reason': 'It is classical.'}]}
        plan = script()
        plan['sources:6-search'] = [{
            'output/bibliography.bib': self.EULER, 'output/sources.json': self.VERIFIED,
            'output/requests.json': json.dumps([{'declaration': 'Small.helper_zero', 'found': False, 'key': None,
                                                 'note': 'It has every block.', 'stronger': self.STRONGER}])}]
        return plan

    def session_file(self, call, name):
        return read_json(self.work / 'sessions' / call['folder'] / name)

    def test_a_source_that_states_more_than_the_library_becomes_a_gap_and_is_cited_once_the_library_has_its_form(self):
        self.from_the_records()
        plan = self.asking_to_cite()
        block = theorem('block_sum', '(m n : Nat) : oddSum (m + n) = oddSum m + n * (2 * m + n)', proof='rfl')
        strict = theorem('sq_step_strict', '(n : Nat) : oddSum n < oddSum (n + 1)', uses=['sq_step'], proof='rfl')
        plan['foldback'] = [{
            'output/lean/Small/Step.lean': STEP.replace('\n\nend Small', '\n\n' + strict + '\n\n' + block + '\n\nend Small'),
            'output/report.json': json.dumps({'deleted': [], 'items': [
                {'id': 'g1', 'closed': True, 'declarations': ['Small.sq_step_strict'], 'note': ''},
                {'id': 'r1', 'closed': False, 'declarations': [], 'note': 'The lemma is wanted by the cross-part item.'},
                {'id': 'c1', 'closed': True, 'declarations': ['Small.block_sum'], 'note': ''}]})}]
        closed = record_text('Every block of consecutive odd numbers has a closed sum.', weight='unit')
        plan['records-write:6-01'][0]['output/records/Small/block_sum.md'] = closed
        plan['records-compare:6-01'] = [{
            'output/verdicts.json': json.dumps([{'declaration': name, 'verdict': 'agrees', 'difference': ''}
                                                for name in ('Small.block_sum', 'Small.sq_step_strict')])}]
        plan['sources:6'] = [{
            '@copy': [['bibliography.bib', 'output/bibliography.bib']], 'output/sources.json': self.ENTERED,
            'output/requests.json': json.dumps([{'declaration': 'Small.block_sum', 'found': True, 'key': 'euler1748',
                                                 'note': 'It is Theorem 2.', 'stronger': None}]),
            'output/records/Small/block_sum.md': record_text('Every block of consecutive odd numbers has a closed sum.',
                                                             weight='unit', source='euler1748')}]
        plan['draft-compare'] = [{'output/verdicts.json': json.dumps([
            {'id': 'g1', 'verdict': 'rewritten', 'text': 'For every $n$, $s(n) < s(n+1)$.'}, {'id': 'c1', 'verdict': 'same'}])}]
        self.halted_after_the_freeze(plan)
        # The search comes before the fold-back, and the source is checked against the new declaration after it.
        kinds = [(call['kind'], call['section']) for call in self.calls()
                 if call['kind'] in ('sources', 'foldback') and call['section'] != '5']
        self.assertEqual(kinds, [('sources', '6-search'), ('foldback', 'Small'), ('sources', '6')])
        search, _, check = [call for call in self.calls() if (call['kind'], call['section']) in kinds]
        self.assertEqual(self.session_file(search, 'requests.json'), [
            {'declaration': 'Small.helper_zero', 'result': 'the empty sum', 'reason': 'It is classical.'}])
        self.assertEqual(self.session_file(search, 'cited.json'), [])  # what step 5 verified is not verified again
        # What the source states is a gap of the draft, and the fold-back has it as an item of its own kind.
        gap = read_json(self.work / 'lib' / '6-sources' / 'draft.json')['gaps'][-1]
        self.assertEqual({key: gap[key] for key in ('id', 'kind', 'element', 'source', 'where', 'wanted', 'closed_by')},
                         {'id': 'c1', 'kind': 'assertion', 'element': 'Small.helper_zero', 'source': 'euler1748',
                          'where': 'Chapter 1, section 2', 'wanted': self.STRONGER['states'], 'closed_by': None})
        item = next(item for item in self.session_file(self.calls('foldback')[0], 'items.json') if item['id'] == 'c1')
        self.assertEqual((item['from'], item['declaration'], item['wanted']),
                         ('source', 'Small.helper_zero', self.STRONGER['states']))
        self.assertIn('The work euler1748 states this form (Chapter 1, section 2)', item['detail'])
        # The fold-back session of the part that holds the root and the main theorem is told that both stay as they are,
        # and with them the definition that their statements name, which lies in a module of the part's folder.
        part = self.session_file(self.calls('foldback')[0], 'part.json')
        self.assertEqual([entry['declaration'] for entry in part['interface']],
                         ['Small.oddSum', 'Small.root', 'Small.sq_step'])
        # The source is entered for the declaration that has its form, by the session that opened it again.
        self.assertEqual([(r['declaration'], r['source'], r['result']) for r in self.session_file(check, 'requests.json')],
                         [('Small.block_sum', 'euler1748', 'the empty sum')])
        folded = self.work / 'lib' / '6-folded'
        self.assertIn('source: euler1748', (folded / 'records' / 'Small' / 'block_sum.md').read_text(encoding='utf-8'))
        self.assertIn('euler1748', (folded / 'bibliography.bib').read_text(encoding='utf-8'))
        self.assertEqual(read_json(self.work / 'lib' / '6-draft' / 'draft.json')['gaps'][-1]['closed_by'], 'Small.block_sum')
        self.assertIn('- `Small.helper_zero`: euler1748 states a stronger or more general form (Chapter 1, section 2): For '
                      'all $m$ and $n$, $s(m+n) = s(m) + n(2m+n)$. The fold-back gave the library that form as '
                      '`Small.block_sum`. The paper cites it from euler1748 and does not prove it.', self.decisions())

    def test_a_source_whose_form_the_library_cannot_be_given_is_recorded_and_the_paper_proves_the_result(self):
        self.from_the_records()
        plan = self.not_closed(self.asking_to_cite(), 'The general form needs a lemma on products that does not compile.')
        self.halted_after_the_freeze(plan)
        # Nothing has the source's form, so nothing is entered and no source is checked a second time.
        self.assertEqual([call['section'] for call in self.calls('sources')], ['5', '6-search'])
        self.assertIsNone(read_json(self.work / 'lib' / '6-draft' / 'draft.json')['gaps'][-1]['closed_by'])
        self.assertNotIn('source:', (self.work / 'lib' / '6-folded' / 'records' / 'Small' / 'helper_zero.md')
                         .read_text(encoding='utf-8'))
        self.assertIn('The library could not be brought to that form, so it keeps its own, and the paper proves '
                      '`Small.helper_zero`. The general form needs a lemma on products that does not compile. A reader who '
                      'knows the source will ask why the paper does not cite it; this is the answer.', self.decisions())

    def test_a_finding_of_the_records_that_is_closed_by_taking_its_declaration_out_is_recorded_as_closed(self):
        # The writer of a record found a lemma that nothing uses. The fold-back takes the lemma out, so its report has
        # no declaration to name for that item, and the item is closed all the same.
        self.from_the_records()
        plan = script()
        added = theorem('added_six', ': oddSum 6 = 36', proof='rfl')
        plan['foldback'][0]['output/lean/Small/Helper.lean'] = HELPER_SIMPLIFIED.replace('\n\n' + added, '')
        plan['foldback'][0]['output/report.json'] = json.dumps({'deleted': [], 'items': [
            {'id': 'g1', 'closed': True, 'declarations': ['Small.sq_step_strict'], 'note': None},
            {'id': 'r1', 'closed': True, 'declarations': [], 'note': 'Nothing used the lemma, so it is removed.'}]})
        with patch('finalize.Run.records_again', side_effect=paper.Stop('halted for the test')):
            self.assertEqual(self.run_command(plan, config=self.config()), 2, self.said)
        self.assertEqual(len(self.calls('foldback')), 1)  # the report is accepted as the first session left it
        self.assertNotIn('Small.added_six', read_json(self.work / 'lib' / '6-folded' / 'index.json')['entries'])
        decisions = self.decisions()
        self.assertIn('g1 (draft, `Small.sq_step`): closed by `Small.sq_step_strict`', decisions)
        self.assertIn('r1 (records, `Small.added_six`): closed. Nothing used the lemma, so it is removed.', decisions)

    def test_a_report_of_a_stronger_form_names_a_verified_entry_and_what_the_source_states(self):
        self.from_the_records()
        plan = self.asking_to_cite()
        loose = json.loads(plan['sources:6-search'][0]['output/requests.json'])
        loose[0]['stronger'] = {'key': 'absent1900', 'states': 'More.', 'where': 'Somewhere.'}
        plan['sources:6-search'] = [{**plan['sources:6-search'][0], 'output/requests.json': json.dumps(loose)}]
        self.assertEqual(self.run_command(plan, config=self.config()), 2)
        report = (self.work / 'report.md').read_text(encoding='utf-8')
        self.assertIn('The run stopped at the step `2.6-sources`', report)
        self.assertIn('"stronger" of Small.helper_zero goes with "found": false', report)
        self.assertEqual(self.calls('foldback'), [])

    def not_closed(self, plan, note='It does not compile.'):
        """The scenario `plan` with a fold-back that does not close the gap of the source, and a comparison that cuts it."""
        report = json.loads(plan['foldback'][0]['output/report.json'])
        report['items'].append({'id': 'c1', 'closed': False, 'declarations': [], 'note': note})
        plan['foldback'][0]['output/report.json'] = json.dumps(report)
        plan['draft-compare'] = [{'output/verdicts.json': json.dumps([
            {'id': 'g1', 'verdict': 'rewritten', 'text': 'For every $n$, $s(n) < s(n+1)$.'}, {'id': 'c1', 'verdict': 'cut'}])}]
        return plan

    def test_a_sentence_that_cites_a_work_is_kept_with_the_words_of_the_work_and_an_unopened_work_is_not_cited(self):
        plan = self.not_closed(self.asking_to_cite())
        # Step 5: the first session verifies the work and keeps words for a sentence that the record does not have.
        loose = json.dumps([{'key': 'gauss1801', 'status': 'verified', 'identifier': 'isbn:1', 'opened': 'parts', 'note': '',
                             'attributions': [{**QUOTED, 'sentence': 'It adds an odd number.'}]}])
        plan['sources:5'] = [{**plan['sources'][0], 'output/sources.json': loose}, plan['sources'][0]]
        # The search: the first session enters a work that it could not open into a record, in brackets.
        unopened = json.dumps([{'key': 'euler1748', 'status': 'verified', 'identifier': 'isbn:2', 'opened': 'none',
                                'note': '', 'attributions': []}])
        plan['sources:6-search'] = [{
            'output/bibliography.bib': self.EULER, 'output/sources.json': unopened,
            'output/requests.json': json.dumps([{'declaration': 'Small.helper_zero', 'found': False, 'key': None, 'note': ''}]),
            'output/records/Small/helper_zero.md': record_text('The empty sum is zero, as in [euler1748, Chapter 1].')},
            plan['sources:6-search'][0]]
        self.halted_after_the_freeze(plan)
        first, second = [call for call in self.calls('sources') if call['section'] == '5']
        # The session is given every work that a record cites, with how each record cites it.
        self.assertEqual([(item['key'], [(r['declaration'], r['header'], r['citations']) for r in item['records']])
                          for item in self.session_file(first, 'cited.json')], [('gauss1801', [('Small.sq_step', True, [])])])
        self.assertIn('sources.json: "attributions" of gauss1801 has no entry for the result that the header attributes to '
                      'the work in the record of Small.sq_step', second['prompt'])
        search = [call for call in self.calls('sources') if call['section'] == '6-search']
        self.assertEqual(len(search), 2)
        self.assertIn('euler1748 could not be opened, and the records of Small.helper_zero still cite it', search[1]['prompt'])
        # The record that cited the unopened work was not taken, and what was kept of the works goes to the paper.
        folded = self.work / 'lib' / '6-folded'
        self.assertNotIn('euler1748', (folded / 'records' / 'Small' / 'helper_zero.md').read_text(encoding='utf-8'))
        self.assertEqual(read_json(self.work / 'lib' / '6-draft' / 'draft.json')['attributions'],
                         [{'key': 'gauss1801', **QUOTED}])
        self.assertEqual([row.get('attributions') for row in read_json(folded / 'sources.json')], [[QUOTED]])

    def test_a_result_that_a_cited_theorem_contains_is_proved_in_the_paper_from_that_theorem(self):
        self.from_the_records()
        self.draft = {**DRAFT, 'citations': [{'element': 'Small.helper_zero', 'result': 'the empty sum',
                                              'reason': 'It is classical.'}]}
        instance = {**self.STRONGER, 'specialisation': 'Take $m = 0$ and $n = 0$; both sides are then $s(0)$ and $0$.'}
        sentence = 'The statement is the case of no terms of a theorem on blocks [euler1748, Chapter 1, section 2].'
        literature = record_text('The empty sum is zero.') + '## Literature\n\n' + sentence + '\n'
        entered = json.dumps([{'key': 'euler1748', 'status': 'verified', 'identifier': 'isbn:2', 'opened': 'parts', 'note': '',
                               'attributions': [{'declaration': 'Small.helper_zero', 'sentence': sentence,
                                                 'place': 'Chapter 1, section 2',
                                                 'quote': 'The stand-in words of the work at that place.'}]}])
        plan = script()
        answer = {'declaration': 'Small.helper_zero', 'found': False, 'key': None, 'note': 'No work has the empty sum alone.'}
        # The first session reports the theorem without saying how the statement follows from it.
        plan['sources:6-search'] = [
            {'output/bibliography.bib': self.EULER, 'output/sources.json': entered,
             'output/records/Small/helper_zero.md': literature,
             'output/requests.json': json.dumps([{**answer, 'instance': self.STRONGER}])},
            {'output/bibliography.bib': self.EULER, 'output/sources.json': entered,
             'output/records/Small/helper_zero.md': literature,
             'output/requests.json': json.dumps([{**answer, 'instance': instance}])}]
        self.assertEqual(self.run_command(plan, config=self.config()), 0, self.said)
        search = [call for call in self.calls('sources') if call['section'] == '6-search']
        self.assertIn('"instance" of Small.helper_zero goes with "found": false', search[1]['prompt'])
        # Nothing is asked of the library for it, and the paper is given the theorem with the specialisation.
        self.assertEqual([call['section'] for call in self.calls('sources')], ['5', '6-search', '6-search'])
        drafted = self.produced[-1]['drafted']
        self.assertEqual(drafted['instances'], [{'element': 'Small.helper_zero', 'result': 'the empty sum', **instance}])
        self.assertEqual([gap['id'] for gap in drafted['gaps']], ['g1'])
        self.assertIn({'key': 'euler1748', 'declaration': 'Small.helper_zero', 'sentence': sentence,
                       'place': 'Chapter 1, section 2', 'quote': 'The stand-in words of the work at that place.'},
                      drafted['attributions'])
        # The record says where the result comes from and names no source in its header.
        record = (self.solved / 'records' / 'Small' / 'helper_zero.md').read_text(encoding='utf-8')
        self.assertIn(sentence, record)
        self.assertNotIn('source:', record)
        self.assertIn('- `Small.helper_zero`: no source found that states it in the form the library has. euler1748 states a '
                      'general theorem of which the result is an instance (Chapter 1, section 2). The paper states the '
                      "result in the library's form, cites that theorem and gives the specialisation as its proof; the "
                      'library proves the result by an argument of its own. No work has the empty sum alone.', self.decisions())
        self.assertIn('These statements it proves from a general theorem of the literature, which it cites, by specialising '
                      'that theorem: `Small.helper_zero`.', (self.solved / 'README.md').read_text(encoding='utf-8'))

    def test_a_check_that_a_safeguard_stops_every_time_is_recorded_as_not_done_and_the_run_goes_on(self):
        # The sign of such a stop is known for the Claude CLI, so the sessions that check are given a Claude model.
        self.configure(roles={'review': [{'model': 'claude/opus', 'effort': 'high'}]})
        plan = script()
        plan['records-compare:5-01'] = [{'@stopped': ''}]
        plan['package-read'] = [{'@stopped': ''}]
        # A session that was stopped once is started again as it was, and what it then leaves is taken.
        plan['selection-read'] = [{'@stopped': ''}, plan['selection-read'][0]]
        # The account under which this run is made has the name of the library: a word that stands in most files of the
        # package, and in no path of a home folder.
        with patch('package.account_name', return_value='Small'):
            self.assertEqual(self.run_command(plan, config=self.config()), 0, self.said)
        for kind, section in (('records-compare', '5-01'), ('package-read', None), ('selection-read', None)):
            first, second = [call for call in self.calls(kind) if call['section'] == section]
            # The same prompt and the same files, with no word of the stop and nothing of the stopped session.
            self.assertEqual((first['prompt'], first['given']), (second['prompt'], second['given']), kind)
        log = read_json(self.work / 'log.json')
        self.assertEqual([(event['kind'], event['section']) for event in log if event['event'] == 'safeguard'].count(
            ('selection-read', None)), 1)
        self.assertEqual(sorted((event['kind'], event['section'], event['attempts']) for event in log
                                if event['event'] == 'not done'), [('package-read', None, 2), ('records-compare', '5-01', 2)])
        # The sessions that check ran on the first model of the role `review`, and every other session on the first
        # entry of `models`, so that a different model checks than wrote.
        writer = read_json(self.instance / 'settings.json')['models'][0]['model']
        checking = {'selection-read', 'records-compare', 'sources', 'draft-compare', 'history-read', 'package-read'}
        self.assertEqual({call['kind'] for call in self.calls() if call['model'] == 'claude/opus'}, checking)
        self.assertEqual({call['model'] for call in self.calls() if call['kind'] not in checking}, {writer})
        readme = (self.solved / 'README.md').read_text(encoding='utf-8')
        self.assertIn('- Not made: some of the checks that the items above describe. A safeguard of the AI system stopped '
                      'the session that had the task, each time the session was started', readme)
        self.assertIn('the comparison, by a session that did not write them, of these records with the Lean text: '
                      '`Small.added_six`, `Small.named_four`', readme)
        self.assertIn("the reading of the package's documents by a session that has the package and nothing else", readme)
        self.assertNotIn('independent reading of what the selection claims', readme)  # that reading was made
        report = (self.work / 'report.md').read_text(encoding='utf-8')
        self.assertIn('- Some of the checks that the list above describes were not made.', report)
        self.assertIn("  - the reading of the package's documents by a session that has the package and nothing else.", report)
        # The final check did not stop for the account name as a word by itself, and the report lists the files that
        # hold it so, a member of the archive after the archive.
        self.assertIn('## Where the account name stands as a word by itself\n\nThe account of this run is named `Small`.',
                      report)
        self.assertIn('\n- lean/Small/Root.lean\n', report)
        self.assertIn('\n- knowledge/odd-knowledge.tar.xz, member canon/lean/Small/Root.lean\n', report)
        self.assertNotIn('\n- paper/paper.pdf\n', report)
        # The README is in the manifest as it stands, with that item.
        self.assertEqual(package.standalone_problems(
            self.solved, self.work, package.account_name(),
            {'folders': {name: canon.tree_hash(self.solved / name) for name in ('lean', 'records')}, 'files': {}}), [])

    def test_a_session_that_makes_what_the_run_needs_and_is_stopped_every_time_stops_the_run(self):
        self.configure(roles={'review': [{'model': 'claude/opus', 'effort': 'high'}]})
        plan = script(sources=[{'@stopped': ''}])
        self.assertEqual(self.run_command(plan, config=self.config()), 2)
        report = (self.work / 'report.md').read_text(encoding='utf-8')
        self.assertIn('The run stopped at the step `2.5-records`', report)
        self.assertIn('a safeguard of the AI system stopped every sources session of 5, in 2 attempts', report)
        self.assertIn('## What to do\n\nNothing is to be repaired by hand. Start the same command again: it starts the '
                      'session again, with the same prompt and the same files.', report)
        first, second = self.calls('sources')
        self.assertEqual((first['prompt'], first['given']), (second['prompt'], second['given']))
        # Started again, the command tries the same session again, and the step that had stopped passes.
        with patch('finalize.Run.draft', side_effect=paper.Stop('halted for the test')):
            self.assertEqual(self.run_command(script(), config=self.config()), 2, self.said)
        self.assertIn('The run stopped at the step `2.6-draft`', (self.work / 'report.md').read_text(encoding='utf-8'))
        self.assertEqual(len(self.calls('sources')), 3)

    def test_a_part_whose_session_the_provider_refuses_is_not_discarded_and_the_run_stops_until_it_is_taken(self):
        self.configure(retry_max_seconds=1)  # the wait for a refusal that names no time
        plan = script()
        # The provider has no capacity for the model at the first two runs of the session. At the next two the CLI
        # ends with an error before the session writes anything, as when the network fails. The fifth run is sound.
        plan['simplify:core'] = [{'@refused': ''}, {'@refused': ''}, {'@failed': ''}, {'@failed': ''}] + plan['simplify:core']
        with patch('command_sessions.LIMIT_WAITS', 1):
            self.assertEqual(self.run_command(plan, config=self.config()), 2)
        # The session was waited for and started again once, in its folder. Then the run stopped and named the reason.
        refused = [call for call in self.calls('simplify') if call['section'] == 'core']
        self.assertEqual((len(refused), refused[0]['folder']), (2, refused[1]['folder']))
        report = (self.work / 'report.md').read_text(encoding='utf-8')
        self.assertIn('The run stopped at the step `2.3-simplify`', report)
        self.assertIn('the provider refused the simplify session of core', report)
        self.assertIn('for this reason: model_capacity', report)
        self.assertIn('## What to do\n\nNothing is to be repaired by hand, and no output of a session is in question', report)
        # The part was not discarded for it. Started again, the command launches the session, and the CLI of both
        # attempts ends with an error before the session writes anything. That is nothing a session wrote, so the part
        # is not discarded for it either: the run stops again, and the report says where the words of the CLI are.
        self.assertEqual(self.run_command(config=self.config()), 2)
        self.assertEqual(len([call for call in self.calls('simplify') if call['section'] == 'core']), 4)
        report = (self.work / 'report.md').read_text(encoding='utf-8')
        self.assertIn('The run stopped at the step `2.3-simplify`', report)
        self.assertIn('no simplify session left output the script can use, in 2 attempts: output/report.json was not '
                      'written. The CLI of every session that was read had ended with an error before the session '
                      'wrote anything', report)
        self.assertIn('## What to do\n\nNothing that a session wrote is in question', report)
        self.assertNotIn('the simplification of the part core', self.decisions())
        # Started once more, the command launches the session and accepts the part.
        with patch('finalize.Run.merge', side_effect=paper.Stop('halted for the test')):
            self.assertEqual(self.run_command(config=self.config()), 2, self.said)
        self.assertIn('The run stopped at the step `2.4-merge`', (self.work / 'report.md').read_text(encoding='utf-8'))
        self.assertEqual(len([call for call in self.calls('simplify') if call['section'] == 'core']), 5)
        self.assertEqual(read_json(self.work / 'lib' / '3-parts' / 'parts.json'), {'accepted': ['core'], 'discarded': ['aux']})
        self.assertNotIn('the simplification of the part core', self.decisions())

    def test_a_record_whose_statement_says_more_than_lean_is_written_again_before_the_freeze(self):
        self.from_the_records()
        said = 'The record adds that both sides are 0 for n = 0, which the Lean statement does not say.'
        self.disagreements = [{'label': 'thm:main', 'record_disagreement': said}]
        plan = script()
        plan['records-write:6-01'][0]['output/records/Small/root.md'] = RECORDS['Small/root.md']
        plan['records-compare:6-01'] = [{
            'output/verdicts.json': json.dumps([{'declaration': name, 'verdict': 'agrees', 'difference': ''}
                                                for name in ('Small.root', 'Small.sq_step_strict')])}]
        plan['draft-compare'] = [{'output/verdicts.json': json.dumps([
            {'id': 'g1', 'verdict': 'rewritten', 'text': 'For every $n$, $s(n) < s(n+1)$.'},
            {'id': 's:thm:main', 'verdict': 'same'}])}]
        self.halted_after_the_freeze(plan)
        # The record is due like one whose declaration changed, and its writer and its comparer are told why.
        entry = {'declaration': 'Small.root', 'file': 'Small/Root.lean', 'why': finalize.DISAGREES,
                 'record': 'records/Small/root.md', 'disagreement': said}
        write = next(call for call in self.calls('records-write') if call['section'] == '6-01')
        compare = next(call for call in self.calls('records-compare') if call['section'] == '6-01')
        self.assertIn(entry, self.session_file(write, 'todo.json'))
        self.assertIn(entry, self.session_file(compare, 'todo.json'))
        # The drafted statement that was made from that record is compared with the declaration again.
        rows = self.session_file(self.calls('draft-compare')[0], 'rows.json')
        self.assertEqual([row['id'] for row in rows], ['s:thm:main', 'g1'])
        self.assertIn('## Step 6: records whose statement said more than the Lean statement', self.decisions())
        self.assertIn('- `Small.root`: ' + said, self.decisions())

    def test_the_record_of_a_root_that_a_derivation_proves_is_listed_as_changed(self):
        derived = module_text(theorem('root', ROOT_STATEMENT, uses=['named_four'], proof='rfl',
                                      doc='The sum of the first `n` odd numbers is the square of `n`.'),
                              imports=('Small.Defs', 'Small.Helper'))
        option = {'id': 'a', 'main': 'Small.named_four', 'route': 'derivation', 'proves': 'p', 'rests_on': 'r', 'size': 's',
                  'for': 'f', 'against': 'a'}
        plan = script(selection=[{'output/decision.json': decision(options=[option]), 'output/derivations/a.lean': derived}],
                      review=[{'output/review.json': json.dumps({
                          'parts': [{'id': 'core', 'modules': ['Small.Root', 'Small.Helper']}], 'cross': []})}])
        plan['simplify:core'] = [{'output/report.json': json.dumps({'deleted': [], 'cross': [], 'notes': ''})}]
        plan['records-write:5-01'] = [{
            'output/records/Small/root.md': record_text('The sum of the first n odd numbers equals n times n.', weight='unit',
                                                        proof='From `Small.named_four`.'),
            'output/records/Small/named_four.md': record_text('The first four odd numbers sum to sixteen.'),
            'output/findings.json': '[]'}]
        plan['records-compare:5-01'] = [{'output/verdicts.json': json.dumps([
            {'declaration': name, 'verdict': 'agrees', 'difference': ''} for name in ('Small.root', 'Small.named_four')])}]
        with patch('finalize.Run.draft', side_effect=paper.Stop('halted for the test')):
            self.assertEqual(self.run_command(plan, config=self.config()), 2, self.said)
        self.assertIn('The run stopped at the step `2.6-draft`', (self.work / 'report.md').read_text(encoding='utf-8'))
        # The research wrote the root's record for the proof it gave. The root now has the proof of the derivation,
        # so its record is listed as written for another Lean text, whatever the old record names.
        todo = self.session_file(self.calls('records-write')[0], 'todo.json')
        self.assertEqual({item['declaration']: item['why'] for item in todo},
                         {'Small.named_four': 'names a declaration that is gone', 'Small.root': 'changed'})

    def test_each_fault_of_what_lean_reports_and_of_the_registry_files_stops_the_run_at_the_freeze(self):
        self.from_the_records()
        self.draft = {'statements': [DRAFT['statements'][0]], 'formulas': [], 'gaps': [], 'citations': []}
        # Lean reports for the root an axiom that the instance does not allow, what it prints for the main theorem has
        # no axioms line, and the title that the plan of the paper gives is longer than the registry takes for a name.
        # Before that, Lean elaborates the statement that Challenge.lean prints for the main theorem to another term
        # than the library's. That alone stops nothing: the root alone is compared, and the reason is recorded.
        lake = {'axioms': {'Small.root': ['propext', 'sorryAx'], 'Small.sq_step': None},
                'elaborates_otherwise': 'theorem Small.sq_step'}
        with patch.dict(PLAN, title='T' * 301):
            self.assertEqual(self.run_command(script(), config=self.config(), lake=lake), 2)
        report = (self.work / 'report.md').read_text(encoding='utf-8')
        self.assertIn('The run stopped at the step `2.7-freeze`', report)
        self.assertIn('Small.root depends on axioms that the instance does not allow: sorryAx', report)
        self.assertIn('Check.lean prints no axioms line for Small.sq_step', report)
        self.assertIn('formalization.yaml: project.name is a nonempty text of at most 300 characters', report)
        self.assertNotIn('2.7-freeze', read_json(self.work / 'state.json')['steps'])
        self.assertFalse(self.solved.exists())
        self.assertIn('The root alone is compared. With the main theorem `Small.sq_step` added to Challenge.lean: '
                      'Challenge.lean does not state as the library does: Small.sq_step', self.decisions())
        registry = self.work / 'package' / 'lean'
        self.assertEqual(read_json(registry / 'comparator.json')['theorem_names'], ['Small.root'])
        self.assertNotIn('Small.sq_step', (registry / 'Challenge.lean').read_text(encoding='utf-8'))

    def test_a_draft_that_the_paper_command_does_not_make_stops_the_run(self):
        self.from_the_records()
        self.paper_code = 1  # the paper command ends without having made the draft
        self.assertEqual(self.run_command(script(), config=self.config()), 2)
        self.assertIn('the paper command did not make the draft: exit code 1', (self.work / 'report.md').read_text(encoding='utf-8'))
        self.assertNotIn('2.6-draft', read_json(self.work / 'state.json')['steps'])
        self.assertEqual(self.steps()[-1], '2.6-draft')  # no later step was entered

    def test_a_defect_of_the_program_in_a_step_stops_the_run_at_that_step_with_the_traceback(self):
        # An exception that no exit check raises is a defect of the program. The run stops at the step all the same:
        # the report names the step and holds the traceback, and the step is not recorded as passed.
        self.from_the_records()
        with patch('finalize.Run.draft', side_effect=TypeError('a defect of the program')):
            self.assertEqual(self.run_command(script(), config=self.config()), 2, self.said)
        report = (self.work / 'report.md').read_text(encoding='utf-8')
        self.assertIn('The run stopped at the step `2.6-draft`', report)
        self.assertIn('the program failed in this step:\nTraceback (most recent call last):', report)
        self.assertIn('TypeError: a defect of the program', report)
        self.assertNotIn('2.6-draft', read_json(self.work / 'state.json')['steps'])

    def test_a_package_that_fails_the_final_check_stops_the_run_and_is_not_moved(self):
        self.from_the_records()
        # The session that writes the prose of the README gives a path of a machine, which its instruction forbids.
        # The check of the prose does not read for that, so the final check is the first to find it.
        plan = script(readme_write=[{'output/outline.md': 'The proof is by induction; it was checked in D:/lean-work.\n',
                                     'output/obtained.md': 'The research made {{facts.publications}} publication.\n'}])
        self.assertEqual(self.run_command(plan, config=self.config()), 2)
        report = (self.work / 'report.md').read_text(encoding='utf-8')
        self.assertIn('The run stopped at the step `6-check`', report)
        self.assertIn('the package does not pass its final check: README.md holds a drive path', report)
        self.assertNotIn('6-check', read_json(self.work / 'state.json')['steps'])
        self.assertTrue((self.work / 'package' / 'README.md').is_file())
        self.assertFalse(self.solved.exists())
        # No step before the final check is made again, and the report says so where it says what the user does.
        self.assertIn('## What to do\n\nThe final check reads the finished package.', report)


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
        self.assertEqual(read_json(folder / 'removed.json'), [
            {'declaration': 'Small.helper_zero', 'file': 'Small/Helper.lean', 'proved': True},
            {'declaration': 'Small.unused_two', 'file': 'Small/Helper.lean', 'proved': True}])
        self.assertIn('by more than removed elements put back whole', second['prompt'])
        taken = read_json(self.work / 'lib' / '1-taken' / 'taken.json')
        self.assertEqual((taken['restored'], taken['removed']), (['Small.helper_zero', 'Small.unused_two'], ['Small.stray']))
        self.assertEqual((self.work / 'lib' / '1-taken' / 'lean' / 'Small' / 'Helper.lean').read_text(encoding='utf-8'), helper)
        self.assertTrue((self.work / 'lib' / '1-taken' / 'records' / 'Small' / 'helper_zero.md').is_file())
        self.assertIn('these removed elements were put back: `Small.helper_zero`, `Small.unused_two`', self.decisions())

    def test_a_theorem_without_a_proof_is_not_put_back_and_the_private_declaration_that_names_it_is_deleted(self):
        # The research left `named_four` without a proof, which its index says, and a private declaration of a module
        # that stays names it. The take removes the theorem, the module no longer builds, and the theorem may not come
        # back: the first session puts it back and is refused, the second deletes the private declaration.
        real = package.take

        def unproved(index, *rest):
            index = json.loads(json.dumps(index))
            index['entries']['Small.named_four']['axioms'] = ['sorryAx']
            return real(index, *rest)

        helper = (self.instance / 'canon' / 'lean' / 'Small' / 'Helper.lean').read_text(encoding='utf-8')
        with_theorem = helper.replace(UNUSED + '\n\n', '')
        without = with_theorem.replace(HELPER_PARTS[5] + '\n\n' + HELPER_PARTS[6] + '\n\n', '')
        plan = script(restore=[{'output/lean/Small/Helper.lean': with_theorem}, {'output/lean/Small/Helper.lean': without}])
        with patch('finalize.Run.review', side_effect=paper.Stop('halted for the test')), \
                patch('package.take', side_effect=unproved):
            self.assertEqual(self.run_command(plan, config=self.config()), 2)
        self.assertIn('The run stopped at the step `2.2-review`', (self.work / 'report.md').read_text(encoding='utf-8'))
        first, second = self.calls('restore')
        folder = self.work / 'sessions' / first['folder']
        self.assertIn("unknown identifier 'named_four'", (folder / 'errors.txt').read_text(encoding='utf-8'))
        self.assertIn({'declaration': 'Small.named_four', 'file': 'Small/Helper.lean', 'proved': False},
                      read_json(folder / 'removed.json'))
        self.assertIn('puts back Small.named_four', second['prompt'])
        taken = read_json(self.work / 'lib' / '1-taken' / 'taken.json')
        self.assertEqual((taken['restored'], taken['removed']), ([], ['Small.named_four', 'Small.stray', 'Small.unused_two']))
        self.assertEqual((self.work / 'lib' / '1-taken' / 'lean' / 'Small' / 'Helper.lean').read_text(encoding='utf-8'), without)
        self.assertFalse((self.work / 'lib' / '1-taken' / 'records' / 'Small' / 'named_four.md').exists())
        decisions = self.decisions()
        self.assertIn('these removed elements were put back: none.', decisions)
        self.assertIn('  have h1 := named_four', decisions)  # the deleted lines are kept for the user

    def test_a_private_declaration_whose_own_proof_is_open_is_deleted_at_the_take(self):
        # The research left the proof of a private declaration open. What is no element stays through the take, and the
        # module builds with the open proof, so only the index shows it. The session of the take is told of it: the
        # first returns the module as the take left it and is refused, the second deletes the declaration.
        private = HELPER_PARTS[6]
        left_open = private[:-len('rfl')] + 'sorry'
        lean = self.instance / 'canon' / 'lean' / 'Small' / 'Helper.lean'
        lean.write_text(lean.read_text(encoding='utf-8').replace(private, left_open), encoding='utf-8', newline='\n')
        index = read_json(self.instance / 'canon' / 'index.json')
        for item in index['hidden'].values():
            item['sorry'] = item.get('user') == 'Small.hidden_three'
        write_json(self.instance / 'canon' / 'index.json', index)
        git(self.instance, 'commit', '-m', 'an open private proof', '--', 'canon/lean/Small/Helper.lean', 'canon/index.json')
        taken = lean.read_text(encoding='utf-8').replace(UNUSED + '\n\n', '')
        without = taken.replace(left_open + '\n\n', '')
        plan = script(restore=[{'output/lean/Small/Helper.lean': taken}, {'output/lean/Small/Helper.lean': without}])
        with patch('finalize.Run.review', side_effect=paper.Stop('halted for the test')):
            self.assertEqual(self.run_command(plan, config=self.config()), 2, self.said)
        self.assertIn('The run stopped at the step `2.2-review`', (self.work / 'report.md').read_text(encoding='utf-8'))
        first, second = self.calls('restore')
        told = 'Small.hidden_three, a declaration of the module Small.Helper that is no element, has an open proof'
        errors = (self.work / 'sessions' / first['folder'] / 'errors.txt').read_text(encoding='utf-8')
        self.assertEqual(errors.count(told), 1)
        self.assertIn(told, second['prompt'])
        self.assertEqual((self.work / 'lib' / '1-taken' / 'lean' / 'Small' / 'Helper.lean').read_text(encoding='utf-8'), without)
        decisions = self.decisions()
        self.assertIn('The library built after the take and held declarations that are no element with an open proof',
                      decisions)
        self.assertIn('    private theorem hidden_three : oddSum 3 = 9 := by', decisions)


if __name__ == '__main__':
    unittest.main()
