"""The paper command, with scripted stand-in sessions and a stand-in TeX command.

No AI session and no TeX is run. The launch is patched as tests/test_pipeline.py patches it: the
command the script starts is this file itself, which then plays the session. Run as
`test_paper.py session <scenario folder>` it reads session.json in its working folder, writes the
files the scenario scripts for that kind of session, and records what the session was given. Run
as `test_paper.py tex paper.tex` it is the TeX command: it fails on `\\undefinedmacro` and otherwise
leaves paper.pdf and paper.log. In the log, a line of the manuscript with `% wide` is reported as set
69pt wider than the text block and one with `% nearly` as 2.5pt wider, in the words of TeX.
"""
import json
from pathlib import Path
import sys

THIS = Path(__file__).resolve()


def stand_in_session(scenario):
    folder = Path.cwd()
    task = json.loads((folder / 'session.json').read_text(encoding='utf-8'))
    prompt = sys.stdin.read()
    script = json.loads((scenario / 'script.json').read_text(encoding='utf-8'))
    record = scenario / 'calls.json'
    calls = json.loads(record.read_text(encoding='utf-8')) if record.exists() else []
    key = next((k for k in (f"{task['kind']}:{task['section']}", task['kind']) if k in script), None)
    given = sorted(p.relative_to(folder).as_posix() for p in folder.rglob('*')
                   if p.is_file() and not p.name.startswith(('cli.', 'worker-')))
    if key is not None:
        entries = script[key]
        for name, content in entries[min(sum(c['key'] == key for c in calls), len(entries) - 1)].items():
            (folder / name).parent.mkdir(parents=True, exist_ok=True)
            (folder / name).write_text(content, encoding='utf-8', newline='\n')
    calls.append({'key': key, 'kind': task['kind'], 'section': task['section'], 'folder': folder.name,
                  'given': given, 'prompt': prompt})
    record.write_text(json.dumps(calls), encoding='utf-8')
    print(json.dumps({'type': 'item.completed', 'item': {'type': 'agent_message', 'text': 'Scripted session.'}}))
    return 0


def stand_in_tex(arguments):
    text = Path(arguments[-1]).read_text(encoding='utf-8')
    for number, line in enumerate(text.splitlines(), 1):
        if '\\undefinedmacro' in line:
            print(f'./paper.tex:{number}: Undefined control sequence.\nl.{number} \\undefinedmacro')
            return 1
    log = ['This is a stand-in for TeX.']
    for number, line in enumerate(text.splitlines(), 1):
        if '% wide' in line:
            log += [f'Overfull \\hbox (69.23543pt too wide) detected at line {number}', '[]']
        if '% nearly' in line:
            log += [f'Overfull \\hbox (2.5pt too wide) in paragraph at lines {number}--{number + 1}', '[]']
    Path('paper.log').write_text('\n'.join(log) + '\n', encoding='utf-8')
    Path('paper.pdf').write_bytes(b'%PDF-1.4 stand-in\n')
    return 0


if __name__ == '__main__' and sys.argv[1:2] == ['session']:
    raise SystemExit(stand_in_session(Path(sys.argv[2])))
if __name__ == '__main__' and sys.argv[1:2] == ['tex']:
    raise SystemExit(stand_in_tex(sys.argv[2:]))

import atexit
import copy
import shutil
import tempfile
import unittest
from unittest.mock import patch

sys.path[:0] = [str(THIS.parents[1]), str(THIS.parent)]
import paper
from cli_adapter import Command, provider_for_model
from knowledge import replay, rests_on
from runtime_support import read_json, write_json
from support import InstanceCase, module_text, record_text, stop_broker

TEX = [sys.executable, '-B', str(THIS), 'tex']

# ----------------------------------------------------------------------------- the settled research

STEP = module_text('''
/-- Adding the next odd number. -/
theorem oddSum_succ (n : Nat) : oddSum (n + 1) = oddSum n + (2 * n + 1) := by
  rfl

/-- The sums increase strictly. -/
theorem oddSum_mono (n : Nat) : oddSum n < oddSum (n + 1) := by
  have step := oddSum_succ n
  omega

/-- The sums do not decrease. -/
theorem oddSum_mono_weak (n : Nat) : oddSum n ≤ oddSum (n + 1) := by
  exact Nat.le_of_lt (oddSum_mono n)
''')
SQUARE = module_text('''
/-- The square of a sum of two terms. -/
theorem expand (a b : Nat) : (a + b) * (a + b) = a * a + 2 * a * b + b * b := by
  ring

/-- Adding 2k + 1 to a square gives the next square. -/
theorem sq_step (k : Nat) : k * k + (2 * k + 1) = (k + 1) * (k + 1) := by
  have h := expand k 1
  omega
''')
ALT = module_text('''
/-- A product written as a sum. -/
theorem alt_helper (k : Nat) : (k + 1) * (k + 1) = k * (k + 1) + (k + 1) := by
  rfl

/-- Adding 2k + 1 to a square gives the next square, by another route. -/
theorem sq_step_alt (k : Nat) : k * k + (2 * k + 1) = (k + 1) * (k + 1) := by
  have h := alt_helper k
  omega
''')
EXTRA = module_text('''
/-- A bound the proof of the root does not use. -/
theorem unused (n : Nat) : oddSum n ≤ oddSum n + 1 := by
  omega
''')
ROOT_PROOF = '''/-- The sum of the first `n` odd numbers is the square of `n`. -/
theorem root (n : Nat) : oddSum n = n * n := by
  induction n with
  | zero => rfl
  | succ k ih =>
    have grows := oddSum_mono_weak k
    rw [oddSum_succ, ih]
    exact {square} k'''
RECORDS = {
    'Small/oddSum_succ.md': record_text('Passing from n to n + 1 adds the odd number 2n + 1.', short='next odd number',
                                        statement='For every natural number $n$, $S_{n+1} = S_n + (2n + 1)$.'),
    'Small/oddSum_mono.md': record_text('The sums increase strictly.', weight='unit', short='the sums increase',
                                        statement='For every natural number $n$, $S_n < S_{n+1}$.',
                                        proof='The sum grows by $2n + 1 > 0$, by `Small.oddSum_succ`.'),
    'Small/oddSum_mono_weak.md': record_text('The sums do not decrease.', weight='unit',
                                             statement='For every natural number $n$, $S_n \\le S_{n+1}$.',
                                             proof='Immediate from `Small.oddSum_mono`.'),
    'Small/expand.md': record_text('The square of a sum.', source='euclid',
                                   statement='For natural numbers $a$ and $b$, $(a+b)^2 = a^2 + 2ab + b^2$.')
    + '## Literature\n\nEuclid, Elements, Book II, Proposition 4. The statement was read; the proof was not.\n',
    'Small/sq_step.md': record_text('Adding 2k + 1 to a square gives the next square.', weight='unit',
                                    short='completing the square',
                                    statement='For every natural number $k$, $k^2 + (2k + 1) = (k + 1)^2$.',
                                    proof='Expand $(k + 1)^2$ by `Small.expand`.'),
    'Small/alt_helper.md': record_text('A product written as a sum.'),
    'Small/sq_step_alt.md': record_text('The next square, by another route.', proves='Small.sq_step',
                                        proof='Write $(k + 1)^2$ as $k(k + 1) + (k + 1)$.'),
    'Small/unused.md': record_text('A bound the proof of the root does not use.', weight='unit',
                                   statement='For every natural number $n$, $S_n \\le S_n + 1$.'),
    'Small/root.md': record_text('The sum of the first n odd numbers equals n times n.', weight='unit',
                                 short='sum of odd numbers',
                                 statement='For every natural number $n$, $1 + 3 + \\dots + (2n - 1) = n^2$.',
                                 proof='By induction on $n$; the step is `Small.sq_step`.'),
}
BIBLIOGRAPHY = '@book{euclid,\n  author = {Euclid},\n  title = {Elements},\n  note = {Book II}\n}\n'
UNDERSTANDING = 'Each step adds one odd number and completes a square; `Small.root` states the result.\n'

# ----------------------------------------------------------------------------- what the scripted sessions write

PLAN = {
    'title': 'The sum of the first odd numbers',
    'outline': 'Induction on the number of terms; the step is the identity that completes a square.',
    'sections': [{'id': 'intro', 'title': 'Introduction', 'content': 'The problem, the main theorem, an outline.'},
                 {'id': 'tools', 'title': 'Preliminaries', 'content': 'The two lemmas the induction uses.'},
                 {'id': 'proof', 'title': 'Proof of the main theorem', 'content': 'The induction.'}],
    'statements': [
        {'element': 'Small.root', 'kind': 'theorem', 'label': 'thm:main', 'section': 'intro', 'proof': 'proof'},
        {'element': 'Small.oddSum_mono', 'kind': 'lemma', 'label': 'lem:increasing', 'section': 'tools'},
        {'element': 'Small.sq_step', 'kind': 'lemma', 'label': 'lem:square', 'section': 'tools'}],
    'others': [
        {'element': 'Small.oddSum', 'treatment': 'absorbed', 'into': ['intro'],
         'reason': 'The object of the problem, defined where the problem is stated.'},
        {'element': 'Small.oddSum_succ', 'treatment': 'absorbed', 'into': ['Small.root', 'Small.oddSum_mono']},
        {'element': 'Small.oddSum_mono_weak', 'treatment': 'not_stated', 'by': 'Small.oddSum_mono',
         'reason': 'The consequence left by a superseded statement; the proof calls the strict form.'},
        {'element': 'Small.expand', 'treatment': 'cited', 'section': 'tools'}],
    'notation': [{'symbol': '$S_n$', 'meaning': 'the sum of the first $n$ odd numbers'}]}
ABSTRACT = 'We show that the sum of the first $n$ odd numbers is the square of $n$.\n'
INTRO = r'''For a natural number $n$ let $S_n$ denote the sum of the first $n$ odd numbers. Which number is $S_n$?

\begin{theorem}\label{thm:main}
For every natural number $n$, we have $S_n = n^2$.
\end{theorem}

\begin{verification}
Theorem~\ref{thm:main} has been formally verified in Lean 4. The formal statement is
\LeanStatement
\end{verification}

The proof, in Section~\ref{sec:proof}, is an induction whose step is Lemma~\ref{lem:square}.
'''
TOOLS = r'''\begin{lemma}\label{lem:increasing}
For every natural number $n$, we have $S_n < S_{n+1}$.
\end{lemma}
\begin{proof}
The sum $S_{n+1}$ exceeds $S_n$ by $2n + 1$.
\end{proof}

The next lemma is the expansion of a square \cite[Book II, Proposition 4]{euclid} for the pair $k$ and $1$.

\begin{lemma}\label{lem:square}
For every natural number $k$, we have $k^2 + (2k + 1) = (k + 1)^2$.
\end{lemma}
\begin{proof}
Expand the right-hand side.
\end{proof}
'''
PROOF = r'''\begin{proof}[Proof of Theorem~\ref{thm:main}]
By induction on $n$. The sums increase by Lemma~\ref{lem:increasing}, and the step is Lemma~\ref{lem:square}.
\end{proof}
'''
PARTS = {'abstract': ABSTRACT, 'intro': INTRO, 'tools': TOOLS, 'proof': PROOF}
CLEAN = {'understanding': {'main_result': 'The sum of the first n odd numbers is n squared.', 'proof': 'Induction.'},
         'findings': []}
FOUND = {**CLEAN, 'findings': [{'where': 'Lemma 2.2', 'quote': 'Expand the right-hand side.',
                                'problem': 'The expansion is not carried out.'}]}
LABELS = ('thm:main', 'lem:increasing', 'lem:square')
SAME = [{'label': label, 'verdict': 'same', 'difference': ''} for label in LABELS]


def good():
    """A scenario in which every session does its work at the first attempt."""
    return {'plan': [{'output/plan.json': json.dumps(PLAN)}],
            'write:intro': [{'output/intro.tex': INTRO, 'output/abstract.tex': ABSTRACT}],
            'write:tools': [{'output/tools.tex': TOOLS}], 'write:proof': [{'output/proof.tex': PROOF}],
            'read': [{'output/reading.json': json.dumps(CLEAN)}],
            'compare': [{'output/comparison.json': json.dumps(SAME)}]}


_SETTLED = None


class PaperCase(InstanceCase):
    """An instance whose root is proved in Lean, made once through the real publication path."""

    def setUp(self):
        global _SETTLED
        super().setUp()
        if _SETTLED is None:
            folder = self.candidate(
                modules={'Small/Step.lean': STEP, 'Small/Square.lean': SQUARE, 'Small/Alt.lean': ALT,
                         'Small/Extra.lean': EXTRA},
                replace={'Small.root': ROOT_PROOF.replace('{square}', 'sq_step')},
                imports={'Small.root': ['Small.Step', 'Small.Square']},
                records=RECORDS, understanding={'q0.md': UNDERSTANDING}, prepare=False)
            (folder / 'bibliography.bib').write_text(BIBLIOGRAPHY, encoding='utf-8')
            self.prepare(folder)
            self.publish(folder)
            stop_broker(self.instance)
            base = Path(tempfile.mkdtemp(prefix='do-math-paper-'))
            atexit.register(shutil.rmtree, base, True)
            shutil.copytree(self.instance, base / 'instance')
            _SETTLED = base / 'instance'
        else:
            self.instance = self.root / 'settled'
            shutil.copytree(_SETTLED, self.instance)
            self.addCleanup(stop_broker, self.instance)
        self.out = self.root / 'paper'
        self.scenario = self.root / 'scenario'
        self.scenario.mkdir()
        self.servers = []

    def command(self, cli, model, effort, cwd, servers=None, **options):
        self.servers.append(servers)
        return Command(provider_for_model(model), [sys.executable, '-B', str(THIS), 'session', str(self.scenario)], Path(cwd))

    def run_paper(self, script, tex=TEX, only=False):
        write_json(self.scenario / 'script.json', script)
        with patch('paper.worker_command', side_effect=self.command), patch('builtins.print'):
            return (paper.typeset_only if only else paper.produce)(self.instance, self.out, tex)

    def calls(self, kind=None):
        calls = read_json(self.scenario / 'calls.json')
        return [c for c in calls if kind in (None, c['kind'])]

    def events(self, kind):
        return [e for e in read_json(self.out / 'log.json') if e['event'] == kind]

    def materials(self):
        return paper.extract(self.instance, replay(self.instance))


class RefusalTests(InstanceCase):
    def test_a_root_without_a_formal_proof_is_refused_before_anything_is_written(self):
        out = self.root / 'paper'
        self.assertEqual(replay(self.instance)['root_state'], 'unresolved')
        with patch('paper.worker_command') as launch, patch('builtins.print') as shown:
            self.assertEqual(paper.main([str(self.instance), '--out', str(out), '--tex', *TEX]), 1)
        self.assertIn('the root is unresolved; the paper is written once the root is settled by a formal proof',
                      shown.call_args.args[0])
        launch.assert_not_called()
        self.assertFalse(out.exists())
        with self.assertRaises(paper.Stop):
            paper.produce(self.instance, out)


class MaterialsTests(PaperCase):
    def test_the_materials_are_what_the_formal_proof_rests_on_in_dependence_order(self):
        model = replay(self.instance)
        self.assertEqual(model['root_state'], 'formal_proved')
        materials = paper.extract(self.instance, model)
        names = [e['name'] for e in materials['elements']]
        self.assertEqual(sorted(names), ['Small.expand', 'Small.oddSum', 'Small.oddSum_mono', 'Small.oddSum_mono_weak',
                                         'Small.oddSum_succ', 'Small.root', 'Small.sq_step'])
        # Every element comes after what its proof names and its statement mentions; the main result is last.
        for position, element in enumerate(materials['elements']):
            for used in element['uses'] + element['mentions']:
                self.assertLess(names.index(used), position, (element['name'], used))
        self.assertEqual((names[-1], materials['main']), ('Small.root', 'Small.root'))
        # The other proof of the lemma, what only it rests on, and a result the root does not use stay out,
        # although the model counts the other proof among what the root's statement rests on.
        self.assertIn('Small.alt_helper', rests_on(model, 'Small.root'))
        self.assertFalse({'Small.sq_step_alt', 'Small.alt_helper', 'Small.unused'} & set(names))
        by_name = {e['name']: e for e in materials['elements']}
        # A superseded statement arrives with the statement its one-line proof names, for the plan to leave it out.
        self.assertEqual(by_name['Small.oddSum_mono_weak']['uses'], ['Small.oddSum_mono'])
        lemma = by_name['Small.sq_step']
        self.assertEqual((lemma['kind'], lemma['weight'], lemma['short'], lemma['states']),
                         ('statement', 'unit', 'completing the square', None))
        self.assertIn('(k + 1)^2', lemma['statement'])
        self.assertIn('Small.expand', lemma['proof'])
        self.assertEqual(lemma['lean'], 'Small.sq_step (k : Nat) : k * k + (2 * k + 1) = (k + 1) * (k + 1)')
        self.assertEqual(lemma['used_by'], ['Small.root'])
        self.assertEqual((by_name['Small.expand']['source'], by_name['Small.expand']['weight']), ('euclid', 'step'))
        self.assertIn('Proposition 4', by_name['Small.expand']['literature'])
        self.assertEqual(by_name['Small.oddSum']['kind'], 'definition')
        self.assertIn('oddSum n + (2 * n + 1)', by_name['Small.oddSum']['definition_text'])
        root = materials['root']
        self.assertEqual((root['name'], root['state']), ('Small.root', 'formal_proved'))
        self.assertEqual(root['words'], 'For every natural number n, the sum of the first n odd numbers is n * n.')
        # The understanding so far of q0 comes without review's note on the work that wrote it.
        self.assertEqual(materials['understanding'], UNDERSTANDING.strip())
        self.assertIn('## Review', (self.instance / 'canon/questions/q0.md').read_text(encoding='utf-8'))
        self.assertEqual(materials['bibliography_keys'], ['euclid'])
        self.assertTrue({'Small.unused', 'Small.Alt'} <= set(materials['identifiers']))
        text = paper.render_materials(materials)
        self.assertLess(text.index('`Small.sq_step`'), text.index('### 7. `Small.root`'))
        self.assertIn('@book{euclid', text)
        self.assertNotIn('Small.unused', text)

    def test_another_proof_is_the_one_given_when_the_proof_of_the_root_names_it(self):
        folder = self.candidate(replace={'Small.root': ROOT_PROOF.replace('{square}', 'sq_step_alt')},
                                imports={'Small.root': ['Small.Alt']})
        self.publish(folder)
        materials = self.materials()
        by_name = {e['name']: e for e in materials['elements']}
        self.assertFalse({'Small.sq_step', 'Small.expand'} & set(by_name))
        other = by_name['Small.sq_step_alt']
        self.assertEqual((other['states'], other['statement_from']), ('Small.sq_step', 'Small.sq_step'))
        self.assertIn('(k + 1)^2', other['statement'])
        self.assertIn('k(k + 1)', other['proof'])
        self.assertIn('Small.alt_helper', by_name)
        self.assertIn('another proof of the statement `Small.sq_step`', paper.render_materials(materials))


class PlanTests(PaperCase):
    def problems(self, change):
        plan = copy.deepcopy(PLAN)
        change(plan)
        return ' | '.join(paper.check_plan(self.materials(), plan))

    def other(self, plan, name):
        return next(item for item in plan['others'] if item['element'] == name)

    def test_the_plan_checks(self):
        self.assertEqual(self.problems(lambda plan: None), '')
        # Every element of the materials is in the plan once, and nothing else is.
        self.assertIn('says nothing about these elements of the materials: Small.expand',
                      self.problems(lambda plan: plan['others'].pop()))
        self.assertIn("'Small.unused' is not an element of the materials",
                      self.problems(lambda plan: plan['statements'].append(
                          {'element': 'Small.unused', 'kind': 'lemma', 'label': 'lem:extra', 'section': 'tools'})))
        self.assertIn('Small.expand appears twice', self.problems(lambda plan: plan['others'].append(plan['others'][-1])))
        # A departure from the weight carries its reason.
        self.assertIn('a unit that is not numbered', self.problems(lambda plan: self.other(plan, 'Small.oddSum').pop('reason')))

        def number_the_step(plan):
            plan['others'] = [item for item in plan['others'] if item['element'] != 'Small.oddSum_succ']
            plan['statements'].insert(1, {'element': 'Small.oddSum_succ', 'kind': 'lemma', 'label': 'lem:next', 'section': 'tools'})
        self.assertIn('Small.oddSum_succ has the weight step and is numbered', self.problems(number_the_step))
        # What is not stated has in its place what its proof names.
        self.assertIn('Small.sq_step does not stand in its place',
                      self.problems(lambda plan: self.other(plan, 'Small.oddSum_mono_weak').update(by='Small.sq_step')))
        self.assertIn('an element that is not stated need a "reason"',
                      self.problems(lambda plan: self.other(plan, 'Small.oddSum_mono_weak').pop('reason')))
        # An absorbed element goes into a statement that rests on it.
        self.assertIn('Small.oddSum_succ is absorbed into Small.sq_step, which does not rest on it',
                      self.problems(lambda plan: self.other(plan, 'Small.oddSum_succ').update(into=['Small.sq_step'])))
        # Only a result with a source is cited, and a result with a source is not proved again.
        self.assertIn('Small.oddSum_succ has no source', self.problems(
            lambda plan: self.other(plan, 'Small.oddSum_succ').update(treatment='cited', section='tools')))

        def prove_the_cited(plan):
            plan['others'].pop()
            plan['statements'].insert(1, {'element': 'Small.expand', 'kind': 'lemma', 'label': 'lem:expand',
                                          'section': 'tools', 'reason': 'Used twice.'})
        self.assertIn('Small.expand is taken from the literature: its "proof" is "cited"', self.problems(prove_the_cited))
        # The main result is first, and it is a theorem of the introduction.
        self.assertIn('the main result Small.root is a theorem stated in the first section',
                      self.problems(lambda plan: plan['statements'][0].update(section='tools')))
        self.assertIn('the main result', self.problems(lambda plan: plan['statements'].reverse()))
        # Dependence: a proof after what it rests on, a statement after the definitions it mentions.
        self.assertIn('the proof of Small.root comes before the statement of Small.oddSum_mono',
                      self.problems(lambda plan: plan['statements'][0].update(proof='intro')))

        def define_late(plan):
            plan['others'] = [item for item in plan['others'] if item['element'] != 'Small.oddSum']
            plan['statements'].insert(1, {'element': 'Small.oddSum', 'kind': 'definition', 'label': 'def:sum', 'section': 'tools'})
        self.assertIn('Small.root is stated before Small.oddSum, which its statement mentions', self.problems(define_late))
        # Form.
        self.assertIn('a definition is numbered as a definition',
                      self.problems(lambda plan: plan['statements'][1].update(kind='definition')))
        self.assertIn('"label"', self.problems(lambda plan: plan['statements'][1].update(label='lem:Small.oddSum_mono')))
        self.assertIn('"section" \'nowhere\' is not the id of a section',
                      self.problems(lambda plan: plan['statements'][2].update(section='nowhere')))
        self.assertEqual(paper.check_plan(self.materials(), ['not', 'an', 'object']), ['plan.json holds one JSON object'])


class ManuscriptTests(PaperCase):
    def problems(self, **changed):
        return ' | '.join(paper.machine_checks(self.materials(), PLAN, {**PARTS, **changed}))

    def test_the_manuscript_of_the_plan_passes_and_is_assembled_in_its_order(self):
        self.assertEqual(self.problems(), '')
        tex, spans = paper.assemble(self.materials(), PLAN, PARTS)
        lines = tex.split('\n')
        self.assertEqual([name for name, _, _ in spans], ['abstract', 'intro', 'tools', 'proof'])
        for name, first, last in spans:
            self.assertEqual('\n'.join(lines[first - 1:last]), PARTS[name].strip('\n'))
        self.assertIn('\\documentclass{amsart}', lines[0])
        self.assertIn('\\section{Preliminaries}\\label{sec:tools}', lines)
        self.assertIn('theorem Small.root (n : Nat) : oddSum n = n * n', tex)
        self.assertLess(tex.index('\\bibliography{references}'), tex.index('\\end{document}'))
        self.assertNotIn('\\bibliography', paper.assemble(self.materials(), PLAN, {**PARTS, 'tools': 'Nothing is cited.'})[0])
        found = paper.found_statements(PLAN, PARTS)
        self.assertEqual([(f['label'], f['kind'], f['number']) for f in found],
                         [('thm:main', 'theorem', '1.1'), ('lem:increasing', 'lemma', '2.1'), ('lem:square', 'lemma', '2.2')])
        self.assertEqual(found[0]['text'], 'For every natural number $n$, we have $S_n = n^2$.')

    def test_lean_names_of_the_canon_are_found_outside_the_verification_remark(self):
        self.assertIn('tools: Lean names of the canon appear outside the verification remark: Small.oddSum_succ',
                      self.problems(tools=TOOLS + 'This is the declaration Small.oddSum_succ.\n'))
        # A last component that no ordinary word resembles is found alone, with TeX's escaped underscore as well,
        # in a comment and in a label; a name of a result the paper does not use is a name of the canon too.
        self.assertIn('oddSum_succ', self.problems(proof=PROOF + 'By \\texttt{oddSum\\_succ}.\n'))
        self.assertIn('sq_step_alt', self.problems(proof=PROOF + '% compare sq_step_alt\n'))
        self.assertIn('oddSum', self.problems(tools=TOOLS.replace('lem:increasing', 'lem:oddSum')))
        self.assertIn('Small.Step', self.problems(abstract=ABSTRACT + 'See the module Small.Step.\n'))
        # An ordinary word that happens to end a Lean name is not one, and neither is ordinary mathematics.
        self.assertEqual(self.problems(proof=PROOF + 'The root of the induction is the case $n = 0$; we expand $x_n$.\n'), '')
        # Inside the remark the formal statement may be explained with its identifiers.
        remark = INTRO.replace('\\LeanStatement', '\\LeanStatement\nHere \\texttt{Small.oddSum} is the sum $S_n$.')
        self.assertEqual(self.problems(intro=remark), '')

    def test_references_citations_statements_and_form_are_checked(self):
        self.assertIn('\\ref{lem:missing} points to a label', self.problems(proof=PROOF + 'See Lemma~\\ref{lem:missing}.\n'))
        self.assertIn('\\cite{gauss} is not a key of the bibliography', self.problems(proof=PROOF + 'See \\cite[p.~1]{gauss}.\n'))
        self.assertIn('\\label{lem:square} is defined more than once', self.problems(proof=PROOF + '\\label{lem:square}\n'))
        # Every numbered statement is one of the plan, and every one of the plan is there.
        extra = '\\begin{proposition}\\label{prop:own}\nA claim of the writer.\n\\end{proposition}\n'
        self.assertIn('the proposition numbered 3.1 with \\label{prop:own} is not a numbered statement of the plan',
                      self.problems(proof=extra + PROOF))
        # A numbered statement without a label is reported beside the labelled statements of the plan.
        self.assertIn('the proposition numbered 3.1 without a \\label is not a numbered statement of the plan',
                      self.problems(proof='\\begin{proposition}\nA claim of the writer.\n\\end{proposition}\n' + PROOF))
        self.assertIn('the plan has a lemma with \\label{lem:square} here', self.problems(tools=TOOLS.split('The next lemma')[0]))
        self.assertIn('not in the order of the plan', self.problems(
            tools=TOOLS.replace('lem:increasing', 'lem:x').replace('lem:square', 'lem:increasing').replace('lem:x', 'lem:square')))
        self.assertIn('the plan cites the result with the bibliography key euclid here',
                      self.problems(tools=TOOLS.replace(' \\cite[Book II, Proposition 4]{euclid}', '')))
        # A statement is followed by its proof, or proved where the plan says, or cited and left without one.
        self.assertIn('the proof of lem:increasing follows its statement directly',
                      self.problems(tools=TOOLS.replace('\\begin{proof}\nThe sum', 'Because the sum').replace(
                          '$2n + 1$.\n\\end{proof}', '$2n + 1$.')))
        self.assertIn('the plan puts the proof of thm:main here',
                      self.problems(proof=PROOF.replace('[Proof of Theorem~\\ref{thm:main}]', '')))
        # The one remark on formal verification, around the statement the script supplies.
        self.assertIn('exactly one verification environment', self.problems(intro=INTRO.replace('\\LeanStatement', '')))
        self.assertIn('exactly one verification environment', self.problems(proof=PROOF + '\\LeanStatement\n'))
        # The form of a part.
        self.assertIn('a part does not use \\newcommand, \\section',
                      self.problems(proof='\\section{More}\n\\newcommand{\\S}{S}\n' + PROOF))
        self.assertIn('a part does not use \\DeclareMathOperator, \\let, \\newenvironment',
                      self.problems(proof='\\newenvironment{claim}{}{}\n\\DeclareMathOperator{\\rk}{rk}\n\\let\\phi\\varphi\n'
                                    + PROOF))
        self.assertIn('written in ASCII', self.problems(proof=PROOF + 'Erdős.\n'))
        self.assertIn('the abstract stands by itself', self.problems(abstract='As in \\cite{euclid}, squares appear.\n'))

    def test_a_numbered_result_from_the_literature_carries_its_citation_and_no_proof(self):
        plan = copy.deepcopy(PLAN)
        plan['others'].pop()
        plan['statements'].insert(1, {'element': 'Small.expand', 'kind': 'lemma', 'label': 'lem:expand', 'section': 'tools',
                                      'proof': 'cited', 'reason': 'It is used in the form stated.'})
        self.assertEqual(paper.check_plan(self.materials(), plan), [])
        source = '[{\\cite[Book II, Proposition 4]{euclid}}]'
        tools = ('\\begin{lemma}' + source + '\\label{lem:expand}\nFor natural numbers $a$ and $b$, we have '
                 '$(a+b)^2 = a^2 + 2ab + b^2$.\n\\end{lemma}\n\n' + TOOLS.replace(' \\cite[Book II, Proposition 4]{euclid}', ''))
        check = lambda text: ' | '.join(paper.machine_checks(self.materials(), plan, {**PARTS, 'tools': text}))
        self.assertEqual(check(tools), '')
        self.assertIn('its statement carries \\cite{euclid}', check(tools.replace(source, '')))
        self.assertIn('lem:expand is a result from the literature; it is cited and has no proof',
                      check(tools.replace('\\end{lemma}\n\n', '\\end{lemma}\n\\begin{proof}\nExpand.\n\\end{proof}\n\n', 1)))

    def test_the_formal_statement_is_typeset_from_ascii(self):
        tex, unknown = paper.lean_tex('theorem T (f : ℕ → ℕ) :\n    ∀ n ≤ 3, f n ≠ x₁ ∧ a_b ∈ {y} ⊛ z')
        self.assertTrue(tex.isascii())
        self.assertEqual(unknown, ['⊛'])
        self.assertIn(r'(f : \ensuremath{\mathbb{N}} \ensuremath{\to} \ensuremath{\mathbb{N}}) :\\', tex)
        self.assertIn(r'~~~~\ensuremath{\forall} n \ensuremath{\le} 3', tex)
        self.assertIn(r'x\ensuremath{_{1}} \ensuremath{\wedge} a\_b \ensuremath{\in} \{y\}', tex)
        self.assertIn(r'\mathrm{U{+}229B}', tex)
        # A circumflex and a tilde are the characters, where \^{} and \~{} would print an accent.
        self.assertEqual(paper.lean_tex('n ^ 2 ~ m')[0], r'n \textasciicircum{} 2 \textasciitilde{} m')

    def test_the_running_head_is_the_title_with_its_formulas_left_as_they_are(self):
        # amsart capitalizes the title for the head, and with no author it does so twice, formulas included.
        tex = paper.assemble(self.materials(), PLAN, PARTS)[0]
        title = PLAN['title'].strip()
        self.assertIn('\\newcommand{\\RunningHead}{' + title + '}\n\\uppercasenonmath\\RunningHead\n\\begin{document}\n'
                      '\\title{' + title + '}\n', tex)
        self.assertIn('\\maketitle\n\\markboth{\\RunningHead}{\\RunningHead}\n', tex)

    def test_the_lines_wider_than_the_text_block_are_read_from_the_log_of_tex(self):
        with tempfile.TemporaryDirectory() as directory:
            log = Path(directory) / 'paper.log'
            self.assertEqual(paper.wide_lines(log), [])  # no log, nothing to report
            log.write_text('Overfull \\hbox (69.23543pt too wide) detected at line 31\n[]\n'
                           'Overfull \\hbox (12.4pt too wide) in paragraph at lines 40--44\n'
                           'Overfull \\hbox (7.0pt too wide) in alignment at lines 50--53\n'
                           'Overfull \\hbox (2.5pt too wide) in paragraph at lines 60--61\n'
                           'Underfull \\vbox (badness 6575) has occurred while \\output is active\n'
                           'Overfull \\hbox (69.23543pt too wide) detected at line 31\n', encoding='utf-8')
            self.assertEqual(paper.wide_lines(log),
                             ['paper.tex, line 31: TeX set a line 69pt wider than the text block',
                              'paper.tex, lines 40 to 44: TeX set a line 12pt wider than the text block',
                              'paper.tex, lines 50 to 53: TeX set a line 7pt wider than the text block'])


class RunTests(PaperCase):
    def test_one_command_leaves_the_paper_and_what_stands_beside_it(self):
        # The test instance sends every role to the common list; review gets its own list, as in the default settings.
        self.configure(roles={'review': [{'model': 'claude/opus', 'effort': 'high'}]})
        script = good()
        wrong = copy.deepcopy(PLAN)
        wrong['others'].pop()
        script['plan'].insert(0, {'output/plan.json': json.dumps(wrong)})
        write_json(self.scenario / 'script.json', script)
        with patch('paper.worker_command', side_effect=self.command), patch('builtins.print') as shown:
            self.assertEqual(paper.main([str(self.instance), '--out', str(self.out), '--tex', *TEX]), 0)
        self.assertIn('paper.pdf', ' '.join(str(call.args[0]) for call in shown.call_args_list))
        for name in ('paper.tex', 'references.bib', 'paper.pdf', 'plan.json', 'correspondence.json', 'log.json',
                     'materials.md'):
            self.assertTrue((self.out / name).is_file(), name)
        self.assertEqual(read_json(self.out / 'plan.json'), PLAN)
        self.assertEqual((self.out / 'references.bib').read_text(encoding='utf-8'), BIBLIOGRAPHY)
        # One session at a time, each in its own folder, in the order of the work; none receives literature tools.
        calls = self.calls()
        self.assertEqual([(c['kind'], c['section']) for c in calls],
                         [('plan', None), ('plan', None), ('write', 'intro'), ('write', 'tools'), ('write', 'proof'),
                          ('read', None), ('compare', None)])
        self.assertEqual([c['folder'] for c in calls], ['01-plan', '02-plan', '03-write-intro', '04-write-tools',
                                                        '05-write-proof', '06-read', '07-compare'])
        self.assertEqual(self.servers, [{}] * 7)
        # The plan the script could not carry out went back with the reason, to a new session.
        self.assertIn('says nothing about these elements of the materials: Small.expand', calls[1]['prompt'])
        self.assertIn('previous-output/plan.json', calls[1]['given'])
        self.assertEqual(self.events('check')[0]['check'], 'output of the plan session')
        # A writing session has the method, the materials, the plan and the parts written before it.
        self.assertEqual(calls[3]['given'], ['materials.md', 'paper-method.md', 'parts/abstract.tex', 'parts/intro.tex',
                                             'plan.json', 'prompt.txt', 'session.json', 'user-writing-preferences.md'])
        self.assertIn('stated here: lemma `lem:square`, which states the element `Small.sq_step`; its proof follows it',
                      calls[3]['prompt'])
        self.assertIn('absorbed into lemma `lem:increasing`: `Small.oddSum_succ`', calls[3]['prompt'])
        self.assertIn('cited in the running text: `Small.expand`', calls[3]['prompt'])
        self.assertIn('proved here: theorem `thm:main` (`Small.root`), stated in section `intro`', calls[4]['prompt'])
        self.assertIn('output/abstract.tex', calls[2]['prompt'])
        # The reader has the manuscript and the method's description of the reader, and nothing else.
        self.assertEqual(calls[5]['given'], ['paper.tex', 'prompt.txt', 'references.bib', 'session.json'])
        self.assertIn(paper.method_part('The reader'), calls[5]['prompt'])
        for word in ('canon', 'materials', 'Small.'):
            self.assertNotIn(word, calls[5]['prompt'])
        # The correspondence is beside the paper and not in it.
        rows = read_json(self.out / 'correspondence.json')
        self.assertEqual([(r['number'], r['label'], r['element'], r['comparison']['verdict']) for r in rows['statements']],
                         [('Theorem 1.1', 'thm:main', 'Small.root', 'same'), ('Lemma 2.1', 'lem:increasing', 'Small.oddSum_mono', 'same'),
                          ('Lemma 2.2', 'lem:square', 'Small.sq_step', 'same')])
        self.assertIn('n^2', rows['statements'][0]['record_statement'])
        self.assertEqual(rows['statements'][0]['paper_statement'], 'For every natural number $n$, we have $S_n = n^2$.')
        self.assertEqual({o['element']: o['treatment'] for o in rows['others']}['Small.oddSum_mono_weak'], 'not_stated')
        tex = (self.out / 'paper.tex').read_text(encoding='utf-8')
        self.assertEqual(tex.count('Small.'), 1)  # the formal statement the script supplies for the remark
        self.assertIn('statements.json', calls[6]['given'])
        self.assertEqual(self.events('end')[0], {**self.events('end')[0], 'status': 'complete', 'open': []})
        self.assertEqual(len(self.events('session')), 7)
        # Planning and writing use the first common model; the reading and the comparison the first model of review.
        chosen = {(c['kind'], tuple(read_json(self.out / 'sessions' / c['folder'] / 'session.json')[key]
                                    for key in ('model', 'effort'))) for c in self.calls()}
        self.assertEqual(chosen, {('plan', ('codex/gpt-6.1-sol', 'xhigh')), ('write', ('codex/gpt-6.1-sol', 'xhigh')),
                                  ('read', ('claude/opus', 'high')), ('compare', ('claude/opus', 'high'))})

    def test_a_compile_error_goes_to_a_repair_session_and_the_manuscript_is_typeset_again(self):
        script = good()
        script['write:proof'] = [{'output/proof.tex': PROOF + '\\undefinedmacro\n'}]
        script['repair:typeset'] = [{'output/proof.tex': PROOF}]
        self.assertEqual(self.run_paper(script), 0)
        repair = self.calls('repair')
        self.assertEqual([c['section'] for c in repair], ['typeset'])
        findings = read_json(self.out / 'sessions' / repair[0]['folder'] / 'findings.json')
        self.assertIn('Undefined control sequence', ' '.join(findings))
        self.assertIn('are `parts/proof.tex`', repair[0]['prompt'])
        self.assertTrue({'paper.tex', 'parts/proof.tex', 'findings.json', 'materials.md', 'plan.json'} <= set(repair[0]['given']))
        checks = [(e['check'], bool(e['problems'])) for e in self.events('check')]
        self.assertEqual(checks[:4], [('machine checks of the manuscript', False), ('typesetting', True),
                                      ('machine checks of the manuscript', False), ('typesetting', False)])
        self.assertEqual((self.out / 'parts/proof.tex').read_text(encoding='utf-8'), PROOF)
        self.assertTrue((self.out / 'paper.pdf').is_file())

    def test_a_line_wider_than_the_text_block_goes_to_a_repair_session(self):
        script = good()
        script['write:proof'] = [{'output/proof.tex': PROOF + '\\[ a = b \\] % wide\nA sentence. % nearly\n'}]
        script['repair:wide'] = [{'output/proof.tex': PROOF + '\\[ a = b \\]\nA sentence. % nearly\n'}]
        self.assertEqual(self.run_paper(script), 0)
        repair = self.calls('repair')
        self.assertEqual([c['section'] for c in repair], ['wide'])
        findings = read_json(self.out / 'sessions' / repair[0]['folder'] / 'findings.json')
        self.assertEqual(len(findings), 1)  # the line that is 2.5pt too wide is left as it is
        self.assertRegex(findings[0], r'^paper\.tex, line \d+: TeX set a line 69pt wider than the text block$')
        self.assertIn('stand out into the margin', repair[0]['prompt'])
        self.assertIn('are `parts/proof.tex`', repair[0]['prompt'])
        checks = [(e['check'], bool(e['problems'])) for e in self.events('check')]
        self.assertEqual(checks[:6], [('machine checks of the manuscript', False), ('typesetting', False), (paper.WIDE, True),
                                      ('machine checks of the manuscript', False), ('typesetting', False), (paper.WIDE, False)])
        self.assertEqual(self.events('end')[0]['open'], [])
        self.assertTrue((self.out / 'paper.pdf').is_file())

    def test_a_wide_line_that_stays_is_reported_and_the_paper_is_typeset_with_it(self):
        script = good()
        script['write:proof'] = [{'output/proof.tex': PROOF + '\\[ a = b \\] % wide\n'}]
        script['repair:wide'] = [{'output/proof.tex': PROOF + f'\\[ a = b \\] % wide, attempt {n}\n'} for n in range(9)]
        write_json(self.scenario / 'script.json', script)
        with patch('paper.worker_command', side_effect=self.command), patch('builtins.print') as shown:
            self.assertEqual(paper.produce(self.instance, self.out, TEX), 2)
        self.assertEqual(len(self.calls('repair')), paper.REPAIR_ROUNDS)
        # The paper is typeset, so the reading and the comparison are made as for any other manuscript.
        self.assertEqual((len(self.calls('read')), len(self.calls('compare'))), (1, 1))
        end = self.events('end')[0]
        self.assertEqual((end['status'], [item['check'] for item in end['open']]), ('open_findings', [paper.WIDE]))
        self.assertIn('69pt wider than the text block', end['open'][0]['problems'][0])
        self.assertTrue((self.out / 'paper.pdf').is_file())
        self.assertIn('paper.pdf', ' '.join(str(call.args[0]) for call in shown.call_args_list if call.args))

    def test_repairs_are_bounded_and_what_stays_open_is_reported(self):
        script = good()
        script['write:proof'] = [{'output/proof.tex': PROOF + '\\undefinedmacro\n'}]
        script['repair:typeset'] = [{'output/proof.tex': PROOF + f'\\undefinedmacro % attempt {n}\n'} for n in range(9)]
        self.assertEqual(self.run_paper(script), 2)
        self.assertEqual(len(self.calls('repair')), paper.REPAIR_ROUNDS)
        self.assertEqual(self.calls('read') + self.calls('compare'), [])
        end = self.events('end')[0]
        self.assertEqual((end['status'], end['open'][0]['check']), ('open_findings', 'typesetting'))
        self.assertTrue((self.out / 'paper.tex').is_file())
        self.assertFalse((self.out / 'paper.pdf').exists())

    def test_a_repair_session_that_changes_nothing_is_followed_by_one_that_is_told_so(self):
        script = good()
        script['write:proof'] = [{'output/proof.tex': PROOF + '\\undefinedmacro\n'}]
        script['repair:typeset'] = [{'output/proof.tex': PROOF + '\\undefinedmacro\n'}, {'output/proof.tex': PROOF}]
        self.assertEqual(self.run_paper(script), 0)
        self.assertIn('no part was changed', self.calls('repair')[1]['prompt'])

    def test_a_lean_name_in_the_text_goes_to_a_repair_session(self):
        script = good()
        script['write:tools'] = [{'output/tools.tex': TOOLS + 'This is \\texttt{Small.oddSum\\_succ}.\n'}]
        script['repair:machine'] = [{'output/tools.tex': TOOLS}]
        self.assertEqual(self.run_paper(script), 0)
        repair = self.calls('repair')[0]
        self.assertIn('Lean names of the canon appear outside the verification remark',
                      ' '.join(read_json(self.out / 'sessions' / repair['folder'] / 'findings.json')))
        self.assertNotIn('oddSum\\_succ', (self.out / 'paper.tex').read_text(encoding='utf-8'))

    def test_the_reading_loop_is_bounded(self):
        script = good()
        script['read'] = [{'output/reading.json': json.dumps(FOUND)}]
        answer = json.dumps([{'finding': 1, 'action': 'revised', 'note': 'The expansion is now written out.'}])
        script['repair:reading'] = [{'output/tools.tex': TOOLS.replace('Expand the right-hand side.', f'Expand, version {n}.'),
                                     'output/response.json': answer} for n in range(9)]
        self.assertEqual(self.run_paper(script), 0)
        kinds = [(c['kind'], c['section']) for c in self.calls()][4:]
        self.assertEqual(kinds, [('read', None), ('repair', 'reading')] * paper.READING_ROUNDS + [('compare', None)])
        repair = self.calls('repair')[0]
        findings = read_json(self.out / 'sessions' / repair['folder'] / 'findings.json')
        self.assertEqual((findings['findings'], findings['understanding']), (FOUND['findings'], FOUND['understanding']))
        self.assertEqual(len(self.events('reading')), paper.READING_ROUNDS)
        self.assertEqual(self.events('repair')[0]['response'][0]['action'], 'revised')
        self.assertIn('has not been read again', self.events('note')[0]['text'])
        # The second reader read what the first repair left.
        second = (self.out / 'sessions' / self.calls('read')[1]['folder'] / 'paper.tex').read_text(encoding='utf-8')
        self.assertIn('Expand, version 0.', second)
        self.assertTrue((self.out / 'paper.pdf').is_file())

    def test_a_statement_that_differs_is_repaired_and_compared_again(self):
        script = good()
        differs = [dict(row) for row in SAME]
        differs[2].update(verdict='differs', difference='The manuscript has k^2 + 2k = (k + 1)^2.')
        script['write:tools'] = [{'output/tools.tex': TOOLS.replace('k^2 + (2k + 1)', 'k^2 + 2k')}]
        script['compare'] = [{'output/comparison.json': json.dumps(differs)}, {'output/comparison.json': json.dumps(SAME)}]
        script['repair:comparison'] = [{'output/tools.tex': TOOLS, 'output/response.json': json.dumps(
            [{'finding': 1, 'action': 'revised', 'note': 'The term 1 is restored.'}])}]
        self.assertEqual(self.run_paper(script), 0)
        self.assertEqual([len(e['differing']) for e in self.events('comparison')], [1, 0])
        rows = read_json(self.out / 'correspondence.json')['statements']
        self.assertEqual([r['comparison']['verdict'] for r in rows], ['same'] * 3)
        self.assertIn('k^2 + (2k + 1)', rows[2]['paper_statement'])

    def test_a_difference_that_the_bounded_repairs_leave_is_reported(self):
        script = good()
        differs = [dict(row) for row in SAME]
        differs[2].update(verdict='differs', difference='The manuscript has k^2 + 2k = (k + 1)^2.')
        script['write:tools'] = [{'output/tools.tex': TOOLS.replace('k^2 + (2k + 1)', 'k^2 + 2k')}]
        script['compare'] = [{'output/comparison.json': json.dumps(differs)}]
        script['repair:comparison'] = [{'output/tools.tex': TOOLS.replace('k^2 + (2k + 1)', 'k^2 + 2k + 0'), 'output/response.json':
                                        json.dumps([{'finding': 1, 'action': 'revised', 'note': 'A term was added.'}])}]
        self.assertEqual(self.run_paper(script), 2)
        self.assertEqual(len(self.calls('compare')), paper.COMPARISON_ROUNDS)
        self.assertEqual(len(self.calls('repair')), paper.COMPARISON_ROUNDS - 1)
        rows = read_json(self.out / 'correspondence.json')['statements']
        self.assertEqual(rows[2]['comparison'], {'verdict': 'differs', 'difference': differs[2]['difference'],
                                                 'record_disagreement': ''})
        self.assertEqual(self.events('end')[0]['open'][0]['problems'][0]['label'], 'lem:square')

    def test_a_disagreement_inside_the_record_of_an_element_is_reported_beside_the_paper(self):
        script = good()
        noted = [dict(row) for row in SAME]
        noted[1]['record_disagreement'] = 'The record states the inequality for n >= 1; the Lean statement holds for every n.'
        script['compare'] = [{'output/comparison.json': json.dumps(noted)}]
        self.assertEqual(self.run_paper(script), 0)
        self.assertIn('"record_disagreement"', self.calls('compare')[0]['prompt'])
        # The manuscript is not repaired for it; the correspondence file and the log carry it.
        self.assertEqual(self.calls('repair'), [])
        rows = read_json(self.out / 'correspondence.json')['statements']
        self.assertEqual([r['comparison']['record_disagreement'] for r in rows], ['', noted[1]['record_disagreement'], ''])
        self.assertEqual(self.events('comparison')[0]['record_disagreements'],
                         [{'label': 'lem:increasing', 'record_disagreement': noted[1]['record_disagreement']}])

    def test_without_a_tex_command_everything_else_is_done_and_the_manuscript_is_typeset_later(self):
        with patch('paper.shutil.which', return_value=None):
            self.assertEqual(self.run_paper(good(), tex=None), 3)
            with self.assertRaises(paper.Stop):
                self.run_paper(good(), tex=None, only=True)
        self.assertFalse((self.out / 'paper.pdf').exists())
        self.assertFalse((self.out / 'typeset').exists())
        for name in ('paper.tex', 'references.bib', 'plan.json', 'correspondence.json', 'log.json'):
            self.assertTrue((self.out / name).is_file(), name)
        self.assertEqual([c['kind'] for c in self.calls()], ['plan', 'write', 'write', 'write', 'read', 'compare'])
        self.assertEqual((self.events('end')[0]['status'], self.events('materials')[0]['tex']), ('no_tex', None))
        self.assertEqual([e['check'] for e in self.events('check')], ['machine checks of the manuscript'])
        # A folder that holds a manuscript is not written over by a new run; it is typeset as it stands.
        with self.assertRaises(paper.Stop):
            self.run_paper(good())
        launched = len(self.calls())
        self.assertEqual(self.run_paper(good(), only=True), 0)
        self.assertEqual(len(self.calls()), launched)
        self.assertTrue((self.out / 'paper.pdf').is_file())
        rows = read_json(self.out / 'correspondence.json')['statements']
        self.assertEqual([r['comparison']['verdict'] for r in rows], ['same'] * 3)
        self.assertEqual([e['status'] for e in self.events('end')], ['no_tex', 'complete'])
        with self.assertRaises(paper.Stop):
            paper.tex_recipe(['no-such-tex-command'])

    def test_typesetting_later_keeps_what_stayed_open_and_needs_a_run_that_finished_its_checks(self):
        script = good()
        differs = [dict(row) for row in SAME]
        differs[2].update(verdict='differs', difference='The manuscript has k^2 + 2k = (k + 1)^2.')
        script['write:tools'] = [{'output/tools.tex': TOOLS.replace('k^2 + (2k + 1)', 'k^2 + 2k')}]
        script['compare'] = [{'output/comparison.json': json.dumps(differs)}]
        script['repair:comparison'] = [{'output/tools.tex': TOOLS.replace('k^2 + (2k + 1)', 'k^2 + 2k + 0'),
                                        'output/response.json': json.dumps(
                                            [{'finding': 1, 'action': 'revised', 'note': 'A term was added.'}])}]
        with patch('paper.shutil.which', return_value=None):
            self.assertEqual(self.run_paper(script, tex=None), 2)
        self.assertFalse((self.out / 'paper.pdf').exists())
        # Typesetting does not compare again, so the difference the comparison left stays open.
        self.assertEqual(self.run_paper(script, only=True), 2)
        self.assertTrue((self.out / 'paper.pdf').is_file())
        end = self.events('end')[-1]
        self.assertEqual((end['status'], end['open'][0]['problems'][0]['label']), ('open_findings', 'lem:square'))
        # A manuscript whose machine checks stayed open was neither read nor compared, and is not typeset alone.
        self.out = self.root / 'paper-unread'
        script = good()
        script['write:tools'] = [{'output/tools.tex': TOOLS + 'This is Small.oddSum_succ.\n'}]
        script['repair:machine'] = [{'output/tools.tex': TOOLS + f'This is Small.oddSum_succ, version {n}.\n'}
                                    for n in range(9)]
        readings = len(self.calls('read'))
        with patch('paper.shutil.which', return_value=None):
            self.assertEqual(self.run_paper(script, tex=None), 2)
        self.assertEqual(len(self.calls('read')), readings)
        with self.assertRaises(paper.Stop):
            self.run_paper(script, only=True)

    def test_the_known_engines_are_run_in_the_way_each_needs(self):
        found = {'latexmk': 'C:/tex/latexmk.exe', 'pdflatex': 'C:/tex/pdflatex.exe', 'C:/tex/pdflatex.exe': 'C:/tex/pdflatex.exe',
                 'tectonic-0.15': 'tectonic-0.15'}
        with patch('paper.shutil.which', side_effect=found.get):
            # Without --tex: the first of tectonic, latexmk and pdflatex that is on PATH.
            self.assertEqual(paper.tex_recipe(None)[0][:2], ['C:/tex/latexmk.exe', '-pdf'])
            recipe = paper.tex_recipe(['C:/tex/pdflatex.exe'])
            self.assertEqual([Path(command[0]).stem for command in recipe], ['pdflatex', 'bibtex', 'pdflatex', 'pdflatex'])
            # Any other command is run once, with the manuscript as its last argument.
            self.assertEqual(paper.tex_recipe(['tectonic-0.15', '-X', 'compile']), [['tectonic-0.15', '-X', 'compile', 'paper.tex']])
            with self.assertRaises(paper.Stop):
                paper.tex_recipe(['tectonic'])
        self.assertEqual(paper.tex_recipe(TEX), [[*TEX, 'paper.tex']])
        # --tex takes the rest of the command line, so an option of this command after it is a mistake.
        with patch('builtins.print') as shown:
            self.assertEqual(paper.main([str(self.instance), '--out', str(self.out), '--tex', 'tectonic', '--model', 'x/y']), 1)
        self.assertIn('put it last', shown.call_args.args[0])
        self.assertFalse(self.out.exists())

if __name__ == '__main__':
    unittest.main()
