"""The paper command, with scripted stand-in sessions and a stand-in TeX command.

No AI session and no TeX is run. The launch is patched as tests/test_pipeline.py patches it: the
command the script starts is this file itself, which then plays the session. Run as
`test_paper.py session <scenario folder>` it reads session.json in its working folder, writes the
files the scenario scripts for that kind of session, and records what the session was given. Run
as `test_paper.py tex paper.tex` it is the TeX command: it fails on `\\undefinedmacro` and otherwise
leaves paper.pdf and paper.log. In the log, a line of the manuscript with `% wide` is reported as set
69pt wider than the text block and one with `% nearly` as 2.5pt wider, in the words of TeX. A line with
`% tight` is reported as 12.5pt too wide only when the manuscript carries the lines with which the script
measures the room of the displays.

The script of a scenario gives, for a key, what the sessions with that key write, one entry for each
session in turn and the last entry for every later one. A session looks for `<kind>:<section>`, then,
when its section is `<word>-<rest>`, as that of a repair of one section is, for `<kind>:<word>`, then
for `<kind>`. Sessions may run side by side, so the record of the calls is kept under a lock file.
The last repair of findings is a narrow one, and its sessions have the section `narrow-<kind>` or
`narrow-<kind>-<section>`, so `repair:narrow` scripts all of them; the session that then reads the
changed passages has the kind `changes`. The session that resolves what the readings left open has
the kind `resolve`, and a session that compares the running text of a section with the elements
has the kind `cover` and the section as its section. In a draft, the session that sketches a
section has the kind `sketch`, and the session that repairs the plan of a draft for the paper is a
`plan` session with the section `from-draft`.

`together.json` in the scenario folder lists groups of keys: a session whose own key is in a group
waits, before it writes anything, until a session of every key of the group has started, and its
call records under "met" whether they all did. Sessions that the command runs one after another
never meet.
"""
import json
import os
from pathlib import Path
import sys
import time

THIS = Path(__file__).resolve()


def stand_in_session(scenario):
    folder = Path.cwd()
    task = json.loads((folder / 'session.json').read_text(encoding='utf-8'))
    prompt = sys.stdin.read()
    script = json.loads((scenario / 'script.json').read_text(encoding='utf-8'))
    record = scenario / 'calls.json'
    own = f"{task['kind']}:{task['section']}"
    names = [own] + ([own.split('-')[0]] if '-' in (task['section'] or '') else []) + [task['kind']]
    key = next((k for k in names if k in script), None)
    given = sorted(p.relative_to(folder).as_posix() for p in folder.rglob('*')
                   if p.is_file() and not p.name.startswith(('cli.', 'worker-')))
    # Sessions of one group wait for each other, which they can only do when the command runs them side by side.
    groups = scenario / 'together.json'
    group = next((g for g in (json.loads(groups.read_text(encoding='utf-8')) if groups.exists() else []) if own in g), None)
    met = None
    if group:
        present = lambda k: scenario / ('present-' + k.replace(':', '-'))
        present(own).touch()
        deadline = time.time() + 20
        while not (met := all(present(k).exists() for k in group)) and time.time() < deadline:
            time.sleep(0.05)
    lock = scenario / 'calls.lock'
    while True:
        try:
            os.close(os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY))
            break
        except (FileExistsError, PermissionError):
            time.sleep(0.01)
    try:
        calls = json.loads(record.read_text(encoding='utf-8')) if record.exists() else []
        if key is not None:
            entries = script[key]
            for name, content in entries[min(sum(c['key'] == key for c in calls), len(entries) - 1)].items():
                (folder / name).parent.mkdir(parents=True, exist_ok=True)
                (folder / name).write_text(content, encoding='utf-8', newline='\n')
        calls.append({'key': key, 'kind': task['kind'], 'section': task['section'], 'folder': folder.name,
                      'given': given, 'prompt': prompt, 'met': met})
        record.write_text(json.dumps(calls), encoding='utf-8')
    finally:
        lock.unlink()
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
        # A display that fits its line only with its spaces closed up shows in the typesetting that measures the
        # displays and not in the manuscript's own; the lines the script adds for the measuring name \paper@equation.
        if '% tight' in line and '\\paper@equation' in text:
            log += [f'Overfull \\hbox (12.5pt too wide) detected at line {number}', '[]']
    Path('paper.log').write_text('\n'.join(log) + '\n', encoding='utf-8')
    Path('paper.pdf').write_bytes(b'%PDF-1.4 stand-in\n')
    return 0


if __name__ == '__main__' and sys.argv[1:2] == ['session']:
    raise SystemExit(stand_in_session(Path(sys.argv[2])))
if __name__ == '__main__' and sys.argv[1:2] == ['tex']:
    raise SystemExit(stand_in_tex(sys.argv[2:]))

import atexit
import copy
import hashlib
import shutil
import tempfile
import threading
import types
import unittest
from unittest.mock import patch

sys.path[:0] = [str(THIS.parents[1]), str(THIS.parent)]
import paper
from cli_adapter import Command, provider_for_model
from knowledge import replay, rests_on
from runtime_support import read_json, write_json
from support import InstanceCase, module_text, record_text, stop_broker, theorem
from test_research import RefutedRootCase

TEX = [sys.executable, '-B', str(THIS), 'tex']

# ----------------------------------------------------------------------------- the collection of real papers

# Made for the tests, in the order of its manifest, with the field of each paper. The plan chooses six; of the
# others, those in a field of a chosen paper (number theory, combinatorics) come first for the readings beside papers.
FIELDS = [('eta', 'analysis'), ('alpha', 'number theory'), ('theta', 'number theory'), ('beta', 'combinatorics'),
          ('iota', 'algebra'), ('gamma', 'number theory'), ('kappa', 'combinatorics'), ('delta', 'combinatorics'),
          ('lambda', 'geometry'), ('epsilon', 'number theory'), ('mu', 'number theory'), ('zeta', 'combinatorics'),
          ('nu', 'topology'), ('xi', 'combinatorics')]
KEYS = [key for key, _ in FIELDS]
CHOSEN = ['alpha', 'beta', 'gamma', 'delta', 'epsilon', 'zeta']
FIRST_FOUR = ['theta', 'kappa', 'mu', 'xi']  # the near fields, in the order of the manifest
NEXT_FOUR = ['eta', 'iota', 'lambda', 'nu']  # the rest
# A fetch.py that records each run beside itself and restores what stash/ holds.
FETCH = '\n'.join([
    'import shutil, sys',
    'from pathlib import Path',
    'here = Path(__file__).resolve().parent',
    "with (here / 'runs.txt').open('a', encoding='utf-8') as stream:",
    "    stream.write('run ' + ' '.join(sys.argv[1:]) + chr(10))",
    "for path in sorted((here / 'stash').glob('*.tex')):",
    '    shutil.copyfile(path, here / path.name)',
    "print('stand-in fetch')", ''])


def passage(key):
    """A sentence of the paper `key`, as a quotation gives it: on one line."""
    return f'The paper {key} opens with the question it answers and states its main theorem at once.'


def exemplar(key):
    """The paper `key`, with its sentences broken and indented over lines as LaTeX sources are."""
    return ('\\documentclass{amsart}\n\\begin{document}\n\\title{On the paper ' + key + '}\n\\begin{abstract}\n'
            'The paper ' + key + ' opens with the question it answers\n   and states its main theorem at once.\n'
            '\\end{abstract}\n\\maketitle\n\\section{Introduction}\nIn the paper ' + key + ' a lemma is introduced by '
            'a sentence\nthat says what the lemma is for.\n\\end{document}\n')


def make_collection(folder):
    folder.mkdir(parents=True)
    manifest = []
    for key, field in FIELDS:
        (folder / (key + '.tex')).write_text(exemplar(key), encoding='utf-8', newline='\n')
        manifest.append({'key': key, 'arxiv': '1001.0001v1', 'title': f'On the paper {key}',
                         'authors': ['A. Author', 'B. Author'], 'journal': 'Journal of Examples', 'year': 2001,
                         'category': 'math.NT', 'field': field, 'pages': 12, 'licence': 'arXiv non-exclusive',
                         'abstract': f'The paper {key} opens with the question\n it answers.',
                         'sha256': hashlib.sha256(exemplar(key).encode('utf-8')).hexdigest(),
                         'why': f'The introduction of {key} states its theorem at once.'})
    write_json(folder / 'manifest.json', manifest)
    (folder / 'fetch.py').write_text(FETCH, encoding='utf-8')


STUDY = ('# How the chosen papers are written\n\nEach introduction asks its question before it states the theorem:\n\n'
         '> ' + passage('alpha') + '\n')
LIKE ={'likeness': 'The manuscript opens, states and proves as the papers do.', 'departures': []}
ABSTRACT_QUOTE = 'We show that the sum of the first $n$ odd numbers is the square of $n$.'


def departure(difference, keys=('theta', 'kappa'), quote=ABSTRACT_QUOTE):
    return {'where': 'the abstract', 'quote': quote, 'evidence': [{'exemplar': k, 'quote': passage(k)} for k in keys],
            'difference': difference}


def departed(difference):
    return {**LIKE, 'departures': [departure(difference)]}

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
    'exemplars': CHOSEN,
    'title': 'The sum of the first odd numbers',
    'outline': 'Induction on the number of terms; the step is the identity that completes a square.',
    'sections': [{'id': 'intro', 'title': 'Introduction', 'content': 'The problem, the main theorem, an outline.',
                  'exemplars': ['alpha', 'beta']},
                 {'id': 'tools', 'title': 'Preliminaries', 'content': 'The two lemmas the induction uses.',
                  'exemplars': ['gamma', 'delta']},
                 {'id': 'proof', 'title': 'Proof of the main theorem', 'content': 'The induction.',
                  'exemplars': ['epsilon', 'zeta']}],
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
    'notation': [{'symbol': '$S_n$', 'meaning': 'the sum of the first $n$ odd numbers', 'elements': ['Small.oddSum']}]}
ABSTRACT = 'We show that the sum of the first $n$ odd numbers is the square of $n$.\n'
INTRO = r'''For a natural number $n$ let $S_n$ denote the sum of the first $n$ odd numbers. Which number is $S_n$?

\begin{theorem}\label{thm:main}
For every natural number $n$, we have $S_n = n^2$.
\end{theorem}

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
# The sessions of one comparison, in the order of the sections; the section `proof` states nothing.
COMPARED = [('compare', 'intro'), ('compare', 'tools')]
# The sessions of one comparison of the running text with the elements, in the order of the sections; the section
# `proof` consists of one proof, so it has no running text and no session.
COVERED = [('cover', 'intro'), ('cover', 'tools')]
# The files of the records that a session finds in its folder besides those of its own task.
RECORD_FILES = ['root.md', 'elements.md', 'references.bib'] + [
    f'elements/Small.{name}.md' for name in ('expand', 'oddSum', 'oddSum_mono', 'oddSum_mono_weak', 'oddSum_succ',
                                             'root', 'sq_step')]


def good():
    """A scenario in which every session does its work at the first attempt."""
    return {'plan': [{'output/plan.json': json.dumps(PLAN), 'output/study.md': STUDY}],
            'write:intro': [{'output/intro.tex': INTRO, 'output/abstract.tex': ABSTRACT}],
            'write:tools': [{'output/tools.tex': TOOLS}], 'write:proof': [{'output/proof.tex': PROOF}],
            'read': [{'output/reading.json': json.dumps(CLEAN)}],
            'likeness': [{'output/likeness.json': json.dumps(LIKE)}],
            # The statements are compared section by section; the section `proof` states none.
            'compare:intro': [{'output/comparison.json': json.dumps(SAME[:1])}],
            'compare:tools': [{'output/comparison.json': json.dumps(SAME[1:])}],
            # No sentence of the running text asserts more than an element states.
            'cover': [{'output/coverage.json': '[]'}]}


def answered(note):
    return json.dumps([{'finding': 1, 'action': 'revised', 'note': note}])


def answers(*actions):
    """The answers of a repair session to its findings, in their order: 'revised' or 'kept', with a note that says which."""
    return json.dumps([{'finding': number, 'action': action, 'note': f'{action} {number}'}
                       for number, action in enumerate(actions, 1)])


def keeps(count):
    """What the session that resolves the open findings of the readings writes when it keeps the text at each of
    `count` findings: its answers, with the reasons `kept 1`, `kept 2` and so on, and no part and no plan."""
    return [{'output/response.json': answers(*['kept'] * count)}]


def kept_by_resolve(check, *findings):
    """The list `kept` at the end of a run whose resolving session kept the text at these findings of one check."""
    return [{'check': check, 'finding': finding, 'reason': f'kept {number}'} for number, finding in enumerate(findings, 1)]


def verdicts(changes, findings):
    """What the session that reads the changed passages writes: for each change (sound, the findings it was made for,
    reason), in the order of the manuscript, and for each finding (number, answered, reason)."""
    return json.dumps({'changes': [{'change': number, 'sound': sound, 'findings': made_for, 'reason': reason}
                                   for number, (sound, made_for, reason) in enumerate(changes, 1)],
                       'findings': [{'finding': number, 'answered': fine, 'reason': reason}
                                    for number, fine, reason in findings]})


# Two findings of a reader in the section `tools`, at passages that an empty line separates: in the proof of the
# second lemma and in the proof of the first. In the manuscript the passage of the second finding comes first.
EXPANSION = {'where': 'Lemma 2.2', 'section': 'sec:tools', 'quote': 'Expand the right-hand side.',
             'problem': 'The expansion is not carried out.'}
GAIN = {'where': 'Lemma 2.1', 'section': 'sec:tools', 'quote': 'exceeds', 'problem': 'By how much is not derived.'}
BASE = {'where': 'the proof', 'section': 'sec:proof', 'quote': 'By induction on $n$.', 'problem': 'The base case is not named.'}
EXPANDED = 'We have $(k + 1)^2 = k^2 + 2k + 1$.'
GAINED = 'The sum $S_{n+1}$ is $S_n + (2n + 1)$, which exceeds $S_n$.'
TOOLS_GAINED = TOOLS.replace('The sum $S_{n+1}$ exceeds $S_n$ by $2n + 1$.', GAINED)
TOOLS_BOTH = TOOLS_GAINED.replace('Expand the right-hand side.', EXPANDED)
PROOF_BASED = PROOF.replace('By induction on $n$.', 'By induction on $n$, from $n = 0$.')


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
        # A collection made for the test stands in for the skill's own.
        self.exemplars = self.root / 'exemplars'
        make_collection(self.exemplars)
        collection = patch('paper.EXEMPLARS', self.exemplars)
        collection.start()
        self.addCleanup(collection.stop)

    def command(self, cli, model, effort, cwd, servers=None, **options):
        self.servers.append(servers)
        return Command(provider_for_model(model), [sys.executable, '-B', str(THIS), 'session', str(self.scenario)], Path(cwd))

    def run_paper(self, script, tex=TEX, only=False, parallel=1, resume=False, open_findings=None, **options):
        """One run of the command. Sessions run one at a time unless `parallel` says otherwise, so that the
        order of the calls is the order of the work. `open_findings` is what --open-findings is given, and
        `options` are draft, from_draft and title_page as `produce` takes them."""
        write_json(self.scenario / 'script.json', script)
        with patch('paper.worker_command', side_effect=self.command), patch('builtins.print'):
            if only:
                return paper.typeset_only(self.instance, self.out, tex, **options)
            if open_findings is not None:
                return paper.act_on_open(self.instance, self.out, tex, parallel=parallel, numbers=open_findings)
            return paper.produce(self.instance, self.out, tex, parallel=parallel, resume=resume, **options)

    def said(self, arguments):
        """What the command prints last when it is run with these arguments after the instance, and its exit code."""
        with patch('paper.worker_command', side_effect=self.command), patch('builtins.print') as shown:
            code = paper.main([str(self.instance), '--out', str(self.out), *arguments])
        return code, shown.call_args.args[0]

    def part(self, name):
        return (self.out / 'parts' / (name + '.tex')).read_text(encoding='utf-8')

    def folder(self, call):
        return self.out / 'sessions' / call['folder']

    def calls(self, kind=None):
        calls = read_json(self.scenario / 'calls.json')
        return [c for c in calls if kind in (None, c['kind'])]

    def events(self, kind):
        return [e for e in read_json(self.out / 'log.json') if e['event'] == kind]

    def materials(self):
        return paper.extract(self.instance, replay(self.instance))

    def given(self, call):
        """The papers of the collection a session was given, by key."""
        return [name[len('exemplars/'):-len('.tex')] for name in call['given'] if name.startswith('exemplars/')]


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


class RefutedMaterialsTests(RefutedRootCase):
    def assert_refutation_materials(self, proof):
        materials = paper.extract(self.instance, replay(self.instance))
        self.assertEqual(materials['root']['state'], 'formal_refuted')
        self.assertEqual(materials['main'], proof)
        self.assertEqual(materials['elements'][-1]['name'], proof)
        self.assertIn(f'The declaration whose formal proof settles it is `{proof}`, '
                      'whose statement is the negation of the root.', paper.render_materials(materials))

    def test_direct_formal_refutation_is_the_main_result(self):
        self.formally_refuted()
        self.assert_refutation_materials('Small.notRoot')

    def test_formal_alternative_to_an_informal_refutation_is_the_main_result(self):
        self.refuted()
        with self.assertRaisesRegex(paper.Stop, 'informal_refuted'):
            paper.extract(self.instance, replay(self.instance))
        self.publish(self.candidate(
            modules={'Small/AgainstAlt.lean': module_text(theorem(
                'notRootAlt', self.NEGATION, proof='intro h\n  exact absurd (h 2) (by decide)'),
                imports=('Small.Against',))},
            records={'Small/notRootAlt.md': record_text('Another proof of the negation.', proves='Small.notRoot')}))
        self.assert_refutation_materials('Small.notRootAlt')


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
        # A correction appended by the reviewer reaches the writer under a separate heading.
        self.assertEqual(materials['understanding'], UNDERSTANDING.strip())
        published = (self.instance / 'canon/questions/q0.md').read_text(encoding='utf-8')
        review = published.split('\n## Review\n', 1)[1].strip()
        self.assertTrue(review)
        self.assertEqual(materials['understanding_review'], review)
        self.assertEqual(materials['bibliography_keys'], ['euclid'])
        self.assertTrue({'Small.unused', 'Small.Alt'} <= set(materials['identifiers']))
        text = paper.render_materials(materials)
        self.assertIn('### Review of the change that supplied this account\n\n' + review, text)
        self.assertIn('At this revision this proof is accepted, settled, and formal.', text)
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
        return ' | '.join(paper.check_plan(self.materials(), plan, KEYS))

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
        self.assertEqual(paper.check_plan(self.materials(), ['not', 'an', 'object'], KEYS), ['plan.json holds one JSON object'])

    def test_a_title_of_the_plan_names_no_lean_name_and_does_not_mention_lean(self):
        # A repair keeps the plan, so a title that mentions Lean has to go back to a planning session.
        self.assertIn('the title has Lean; the paper names no declaration of the canon and does not mention Lean',
                      self.problems(lambda plan: plan.update(title='A proof checked in Lean')))
        named = self.problems(lambda plan: plan['sections'][1].update(title='Around Small.sq_step and Mathlib'))
        self.assertIn(f"the title of section {PLAN['sections'][1]['id']!r} has Mathlib, Small.sq_step;", named)
        self.assertEqual(self.problems(lambda plan: plan.update(title='A lean proof of a clean identity')), '')

    def test_the_plan_chooses_six_different_papers_of_the_collection(self):
        self.assertIn('"exemplars" names 5 papers; it names exactly 6 different ones',
                      self.problems(lambda plan: plan.update(exemplars=CHOSEN[:5])))
        repeated = self.problems(lambda plan: plan.update(exemplars=CHOSEN[:5] + ['alpha']))
        self.assertIn('"exemplars" names a paper more than once: alpha', repeated)
        self.assertNotIn('names 6 papers', repeated)
        self.assertIn('"exemplars" names keys that are not keys of exemplars.md: omega',
                      self.problems(lambda plan: plan.update(exemplars=CHOSEN[:5] + ['omega'])))
        self.assertIn('"exemplars" is an array of the keys of the 6 papers', self.problems(lambda plan: plan.pop('exemplars')))
        # The choice is reported beside what else the plan gets wrong.
        both = self.problems(lambda plan: (plan.update(exemplars=CHOSEN[:5]), plan['others'].pop()))
        self.assertIn('names 5 papers', both)
        self.assertIn('says nothing about these elements of the materials: Small.expand', both)

    def test_the_plan_names_two_of_its_papers_for_every_section(self):
        said = "section 'tools': \"exemplars\" names 2 different papers among those of the plan's own \"exemplars\""
        tools = lambda plan: plan['sections'][1]
        # A plan that names no papers for a section fails like any other plan.
        self.assertIn(said, self.problems(lambda plan: tools(plan).pop('exemplars')))
        self.assertIn(said, self.problems(lambda plan: tools(plan).update(exemplars=['gamma'])))
        self.assertIn(said, self.problems(lambda plan: tools(plan).update(exemplars=['gamma', 'gamma'])))
        self.assertIn(said, self.problems(lambda plan: tools(plan).update(exemplars=['gamma', 'delta', 'alpha'])))
        # A paper of the collection that the plan did not choose is not one of its papers.
        self.assertIn(said, self.problems(lambda plan: tools(plan).update(exemplars=['gamma', 'theta'])))
        self.assertNotIn("section 'intro'", self.problems(lambda plan: tools(plan).pop('exemplars')))
        # Two sections may be written beside the same papers.
        self.assertEqual(self.problems(lambda plan: tools(plan).update(exemplars=['alpha', 'beta'])), '')

    def test_the_plan_fixes_the_notation_of_what_the_writers_of_two_sections_meet(self):
        entry = lambda plan: plan['notation'][0]
        # The sum is defined in the introduction, and elements of the two other sections mention it.
        unnamed = self.problems(lambda plan: entry(plan).pop('elements'))
        self.assertIn('the definition Small.oddSum is met by the writers of the sections intro, tools, proof, who do not '
                      'see each other\'s text, and no entry of "notation" names it in its "elements"', unnamed)
        self.assertIn('"notation" is an array of objects, each with a "symbol" and a "meaning"',
                      self.problems(lambda plan: plan.pop('notation')))
        self.assertIn('"notation" is an array of objects', self.problems(lambda plan: entry(plan).pop('meaning')))
        self.assertIn('notation $S_n$: "elements" is an array of the names of the definitions',
                      self.problems(lambda plan: entry(plan).update(elements='Small.oddSum')))
        # An entry names definitions of the materials, and each definition has one entry.
        self.assertIn("notation $S_n$: 'Small.sq_step' is not a definition of the materials",
                      self.problems(lambda plan: entry(plan).update(elements=['Small.oddSum', 'Small.sq_step'])))
        self.assertIn("notation $S_n$: 'Small.unused' is not a definition of the materials",
                      self.problems(lambda plan: entry(plan).update(elements=['Small.oddSum', 'Small.unused'])))
        self.assertIn('Small.oddSum is named in two entries of "notation"', self.problems(lambda plan: plan['notation'].append(
            {'symbol': '$T_n$', 'meaning': 'the same sum', 'elements': ['Small.oddSum']})))
        # An entry for an object that is no element of the materials is the planning session's to make.
        self.assertEqual(self.problems(lambda plan: plan['notation'].append(
            {'symbol': '$n$', 'meaning': 'the number of terms, a natural number'})), '')


class ManuscriptTests(PaperCase):
    def problems(self, **changed):
        return ' | '.join(paper.machine_checks(self.materials(), PLAN, {**PARTS, **changed}))

    def test_the_manuscript_of_the_plan_passes_and_is_assembled_in_its_order(self):
        self.assertEqual(self.problems(), '')
        tex, spans = paper.assemble(PLAN, PARTS)
        lines = tex.split('\n')
        self.assertEqual([name for name, _, _ in spans], ['abstract', 'intro', 'tools', 'proof'])
        for name, first, last in spans:
            self.assertEqual('\n'.join(lines[first - 1:last]), PARTS[name].strip('\n'))
        self.assertIn('\\documentclass{amsart}', lines[0])
        self.assertIn('\\section{Preliminaries}\\label{sec:tools}', lines)
        # What the script adds to the parts carries no formal statement and no remark on formal verification.
        for word in ('Small.', 'Lean', 'verification'):
            self.assertNotIn(word, tex)
        self.assertLess(tex.index('\\bibliography{references}'), tex.index('\\end{document}'))
        self.assertNotIn('\\bibliography', paper.assemble(PLAN, {**PARTS, 'tools': 'Nothing is cited.'})[0])
        found = paper.found_statements(PLAN, PARTS)
        self.assertEqual([(f['label'], f['kind'], f['number']) for f in found],
                         [('thm:main', 'theorem', '1.1'), ('lem:increasing', 'lemma', '2.1'), ('lem:square', 'lemma', '2.2')])
        self.assertEqual(found[0]['text'], 'For every natural number $n$, we have $S_n = n^2$.')

    def test_lean_names_of_the_canon_are_found_anywhere_in_a_part(self):
        self.assertIn('tools: Lean names of the canon appear: Small.oddSum_succ; the paper calls an object by its '
                      'mathematical name (method, section "The implementation does not show")',
                      self.problems(tools=TOOLS + 'This is the declaration Small.oddSum_succ.\n'))
        # A last component that no ordinary word resembles is found alone, with TeX's escaped underscore as well,
        # in a comment and in a label; a name of a result the paper does not use is a name of the canon too.
        self.assertIn('oddSum_succ', self.problems(proof=PROOF + 'By \\texttt{oddSum\\_succ}.\n'))
        self.assertIn('sq_step_alt', self.problems(proof=PROOF + '% compare sq_step_alt\n'))
        self.assertIn('oddSum', self.problems(tools=TOOLS.replace('lem:increasing', 'lem:oddSum')))
        self.assertIn('Small.Step', self.problems(abstract=ABSTRACT + 'See the module Small.Step.\n'))
        # An ordinary word that happens to end a Lean name is not one, and neither is ordinary mathematics.
        self.assertEqual(self.problems(proof=PROOF + 'The root of the induction is the case $n = 0$; we expand $x_n$.\n'), '')
        # No remark is left out of the search, whatever its environment.
        for environment in ('remark', 'verification'):
            remark = f'\\begin{{{environment}}}\nHere \\texttt{{Small.root}} is Theorem~\\ref{{thm:main}}.\n\\end{{{environment}}}\n'
            self.assertIn('intro: Lean names of the canon appear: Small.root', self.problems(intro=INTRO + remark))

    def test_the_words_lean_and_mathlib_are_found_anywhere_in_a_part(self):
        said = 'the paper does not mention Lean, and this part has the words '
        where = ' (method, section "The implementation does not show")'
        self.assertIn('intro: ' + said + 'Lean' + where,
                      self.problems(intro=INTRO + 'Theorem~\\ref{thm:main} has been verified in Lean 4.\n'))
        self.assertIn('proof: ' + said + 'Lean, Mathlib' + where,
                      self.problems(proof=PROOF + 'We use \\texttt{Mathlib} and Lean4.\n'))
        # In a comment, in a label, in the abstract and in the title as well.
        self.assertIn('tools: ' + said + 'Mathlib', self.problems(tools=TOOLS + '% as in Mathlib\n'))
        self.assertIn('tools: ' + said + 'Lean', self.problems(tools=TOOLS + '\\begin{equation}\\label{eq:Lean}a = a\\end{equation}\n'))
        self.assertIn('abstract: ' + said + 'Lean', self.problems(abstract=ABSTRACT + 'The proof is checked in Lean.\n'))
        plan = {**PLAN, 'title': 'The sum of the first odd numbers, in Lean'}
        self.assertIn('the title: ' + said + 'Lean', ' | '.join(paper.machine_checks(self.materials(), plan, PARTS)))
        # Other words that contain the letters are ordinary words; only the two words with these capitals are looked for.
        ordinary = 'The lean case, the clean bound, Leaning on Lemma~\\ref{lem:square}, LEAN and mathlib are not names.\n'
        self.assertEqual(self.problems(proof=PROOF + ordinary), '')

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
        self.assertEqual(paper.check_plan(self.materials(), plan, KEYS), [])
        source = '[{\\cite[Book II, Proposition 4]{euclid}}]'
        tools = ('\\begin{lemma}' + source + '\\label{lem:expand}\nFor natural numbers $a$ and $b$, we have '
                 '$(a+b)^2 = a^2 + 2ab + b^2$.\n\\end{lemma}\n\n' + TOOLS.replace(' \\cite[Book II, Proposition 4]{euclid}', ''))
        check = lambda text: ' | '.join(paper.machine_checks(self.materials(), plan, {**PARTS, 'tools': text}))
        self.assertEqual(check(tools), '')
        self.assertIn('its statement carries \\cite{euclid}', check(tools.replace(source, '')))
        self.assertIn('lem:expand is a result from the literature; it is cited and has no proof',
                      check(tools.replace('\\end{lemma}\n\n', '\\end{lemma}\n\\begin{proof}\nExpand.\n\\end{proof}\n\n', 1)))

    def test_the_running_head_is_the_title_with_its_formulas_left_as_they_are(self):
        # amsart capitalizes the title for the head, and with no author it does so twice, formulas included.
        tex = paper.assemble(PLAN, PARTS)[0]
        title = PLAN['title'].strip()
        self.assertIn('\\newcommand{\\RunningHead}{' + title + '}\n\\uppercasenonmath\\RunningHead\n\\begin{document}\n'
                      '\\title{' + title + '}\n', tex)
        # The head is printed when it has room beside the page number, and left out when it has not.
        self.assertIn('\\maketitle\n\\sbox0{\\normalfont\\scriptsize\\RunningHead}\\ifdim\\wd0>.85\\textwidth\\markboth{}{}'
                      '\\else\\markboth{\\RunningHead}{\\RunningHead}\\fi\n', tex)

    def test_the_running_head_is_the_short_title_when_the_plan_gives_one(self):
        title = PLAN['title'].strip()
        tex = paper.assemble({**PLAN, 'short_title': ' A short title of $x^2$ '}, PARTS)[0]
        self.assertIn('\\newcommand{\\RunningHead}{A short title of $x^2$}\n\\uppercasenonmath\\RunningHead\n'
                      '\\begin{document}\n\\title{' + title + '}\n', tex)
        # A plan without the key is carried out as before; with the key, it is a text, and it names no Lean name.
        materials = self.materials()
        self.assertEqual(paper.check_plan(materials, {**PLAN, 'short_title': 'A short title'}, KEYS), [])
        self.assertIn('"short_title", when the plan has it, is a nonempty text',
                      paper.check_plan(materials, {**PLAN, 'short_title': ''}, KEYS))
        self.assertTrue(any(problem.startswith('the short title has Lean')
                            for problem in paper.check_plan(materials, {**PLAN, 'short_title': 'Squares in Lean'}, KEYS)))

    def test_the_subsection_headings_set_their_formulas_bold(self):
        self.assertIn('{-.5em}{\\normalfont\\bfseries\\boldmath}}', paper.assemble(PLAN, PARTS)[0])

    def test_the_capitals_of_a_title_in_the_bibliography_are_kept_where_a_command_writes_them(self):
        entry = ('@article{a,\n  author = {{\\L}ukasiewicz, Jan},\n'
                 '  title = {Paths of {\\L}ukasiewicz and {\\\'E}tale maps over {$Q$} with {\\ss} and {{\\O}}re {B}ases},\n'
                 '  booktitle = {On {\\L}ukasiewicz},\n}\n')
        kept = paper.capitals_kept(entry)
        # Only the title is put in lower case by a style; a group without a capital and a group that already has
        # its second pair of braces stay as they are.
        self.assertEqual(kept, entry.replace('Paths of {\\L}ukasiewicz and {\\\'E}tale',
                                             'Paths of {{\\L}}ukasiewicz and {{\\\'E}}tale'))
        self.assertEqual(paper.capitals_kept(kept), kept)
        self.assertEqual(paper.capitals_kept(''), '')

    def test_the_displays_without_room_are_found_by_a_second_typesetting(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            text = ('\\documentclass{amsart}\n\\begin{document}\n\\[ a = b \\] % tight\n\\[ c = d \\] % wide\n'
                    'A sentence. % nearly\n\\end{document}\n')
            (folder / 'paper.tex').write_text(text, encoding='utf-8', newline='\n')
            recipe = paper.tex_recipe(TEX)
            self.assertEqual(paper.typeset(folder, recipe), [])
            # The display that the manuscript's own log reports is left to wide_lines; the other one is found here.
            self.assertEqual(paper.wide_lines(folder / 'paper.log'),
                             ['paper.tex, line 4: TeX set a line 69pt wider than the text block'])
            found = paper.tight_displays(folder, recipe)
            self.assertEqual(len(found), 1)
            self.assertRegex(found[0], r'^paper\.tex, line 3: the displayed formula that ends here is 12pt wider than '
                                       r'the room it has on its line')
            # What is measured is the manuscript with lines added in front of \begin{document}, on its own line, so
            # that a line of the one is the same line of the other; the PDF of the manuscript is not touched.
            measured = (folder / 'displays' / 'paper.tex').read_text(encoding='utf-8')
            self.assertEqual(measured, text.replace('\\begin{document}', paper.DISPLAY_ROOM + '\\begin{document}'))
            self.assertEqual(len(measured.splitlines()), len(text.splitlines()))
            self.assertTrue((folder / 'paper.pdf').is_file())
            # A second typesetting that fails reports nothing.
            (folder / 'paper.tex').write_text(text.replace('A sentence.', '\\undefinedmacro'), encoding='utf-8')
            self.assertEqual(paper.tight_displays(folder, recipe), [])

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


class CollectionTests(PaperCase):
    def runs(self):
        runs = self.exemplars / 'runs.txt'
        return runs.read_text(encoding='utf-8').splitlines() if runs.is_file() else []

    def test_a_missing_paper_is_fetched_once_and_the_command_stops_when_it_stays_missing(self):
        (self.exemplars / 'gamma.tex').unlink()
        write_json(self.scenario / 'script.json', good())
        with patch('paper.worker_command', side_effect=self.command), patch('builtins.print'):
            with self.assertRaises(paper.Stop) as stopped:
                paper.produce(self.instance, self.out, TEX)
        self.assertEqual(self.runs(), ['run '])
        message = str(stopped.exception)
        self.assertIn('after fetch.py ran (exit code 0): gamma.', message)
        self.assertIn(f'"{sys.executable}" "{self.exemplars / "fetch.py"}" --only gamma', message)
        self.assertIn('stand-in fetch', message)
        # Nothing was launched and nothing was written.
        self.assertFalse((self.scenario / 'calls.json').exists())
        self.assertFalse(self.out.exists())

    def test_a_paper_that_differs_is_fetched_again_and_then_used(self):
        (self.exemplars / 'stash').mkdir()
        shutil.copyfile(self.exemplars / 'beta.tex', self.exemplars / 'stash' / 'beta.tex')
        (self.exemplars / 'beta.tex').write_text(exemplar('beta') + 'An edit.\n', encoding='utf-8', newline='\n')
        manifest, papers, fetched = paper.load_collection()
        self.assertEqual(self.runs(), ['run '])
        self.assertEqual((fetched['missing_or_different'], fetched['exit_code']), (['beta'], 0))
        self.assertEqual(papers['beta'], exemplar('beta'))
        self.assertEqual([entry['key'] for entry in manifest], KEYS)
        # A collection that agrees with its manifest is used as it is.
        self.assertIsNone(paper.load_collection()[2])
        self.assertEqual(len(self.runs()), 1)

    def test_the_list_for_the_sessions_and_the_order_of_the_papers_for_the_readings(self):
        manifest, _, _ = paper.load_collection()
        text = paper.render_exemplars(manifest)
        entry = text[text.index('## `kappa`'):text.index('## `delta`')]
        for words in ('`kappa`: On the paper kappa', 'A. Author, B. Author. Journal of Examples, 2001.',
                      'Field: combinatorics. Pages: 12.', 'Abstract: The paper kappa opens with the question it answers.',
                      'Why it is in the collection: The introduction of kappa states its theorem at once.'):
            self.assertIn(words, entry)
        self.assertEqual(paper.likeness_papers(manifest, CHOSEN), FIRST_FOUR + NEXT_FOUR)


class LikenessShapeTests(unittest.TestCase):
    """A report of a reading beside papers is checked for its shape, and for nothing that carries meaning."""

    def problems(self, report):
        return ' | '.join(paper.check_likeness(report))

    def test_the_shape_of_a_report_is_checked_and_its_quotations_are_not_looked_up(self):
        self.assertEqual(self.problems(LIKE), '')
        self.assertEqual(self.problems(departed('The abstract says more than theirs.')), '')
        self.assertEqual(self.problems({**LIKE, 'departures': [departure('An outline is missing.', quote='')]}), '')
        # A quotation that stands nowhere, a short one, evidence from one paper or from none: the readings judge these.
        loose = departure('Loose.', keys=('omega',), quote='Nowhere in the manuscript.')
        loose['evidence'][0]['quote'] = 'short'
        self.assertEqual(self.problems({**LIKE, 'departures': [loose, {**departure('No evidence.'), 'evidence': []}]}), '')
        # The shape.
        self.assertIn('"likeness" is a text that is not empty', self.problems({**LIKE, 'likeness': ' '}))
        self.assertIn('"departures" is an array', self.problems({'likeness': 'Alike.'}))
        self.assertIn('departure 1 is not an object', self.problems({**LIKE, 'departures': ['a place']}))
        self.assertIn('departure 2: "where" is a text that is not empty',
                      self.problems({**LIKE, 'departures': [departure('Fine.'), {**departure('No place.'), 'where': ''}]}))
        self.assertIn('departure 1: "difference" is a text that is not empty', self.problems(departed('')))
        self.assertIn('departure 1: "quote" is a text',
                      self.problems({**LIKE, 'departures': [{**departure('No quote.'), 'quote': None}]}))
        self.assertIn('departure 1: "evidence" is an array of objects, each with "exemplar" and "quote" as text',
                      self.problems({**LIKE, 'departures': [{**departure('Bare.'), 'evidence': [{'exemplar': 'theta'}]}]}))
        self.assertIn('"evidence" is an array of objects',
                      self.problems({**LIKE, 'departures': [{**departure('Text.'), 'evidence': 'theta and kappa'}]}))


class RunTests(PaperCase):
    def test_one_command_leaves_the_paper_and_what_stands_beside_it(self):
        # The test instance sends every role to the common list; review gets its own list, as in the default settings.
        self.configure(roles={'review': [{'model': 'claude/opus', 'effort': 'high'}]})
        script = good()
        wrong = copy.deepcopy(PLAN)
        wrong['others'].pop()
        wrong['exemplars'] = CHOSEN[:5] + ['alpha']
        script['plan'].insert(0, {'output/plan.json': json.dumps(wrong), 'output/study.md': STUDY})
        write_json(self.scenario / 'script.json', script)
        with patch('paper.worker_command', side_effect=self.command), patch('builtins.print') as shown:
            self.assertEqual(paper.main([str(self.instance), '--out', str(self.out), '--parallel', '1', '--tex', *TEX]), 0)
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
                          ('read', None), ('likeness', None), ('likeness', None), *COMPARED, *COVERED])
        self.assertEqual([c['folder'] for c in calls], ['01-plan', '02-plan', '03-write-intro', '04-write-tools',
                                                        '05-write-proof', '06-read', '07-likeness', '08-likeness',
                                                        '09-compare-intro', '10-compare-tools', '11-cover-intro',
                                                        '12-cover-tools'])
        self.assertEqual(self.servers, [{}] * 12)
        # The plan the script could not carry out went back with the reasons, to a new session.
        self.assertIn('says nothing about these elements of the materials: Small.expand', calls[1]['prompt'])
        self.assertIn('"exemplars" names a paper more than once: alpha', calls[1]['prompt'])
        self.assertIn('previous-output/plan.json', calls[1]['given'])
        self.assertEqual(self.events('check')[0]['check'], 'output of the plan session')
        # The collection was used as it stands; the planning session had all of it and chose from it.
        self.assertEqual(self.events('collection')[0]['fetched'], None)
        self.assertEqual(sorted(self.given(calls[0])), sorted(KEYS))
        self.assertIn('exemplars.md', calls[0]['given'])
        self.assertNotIn('study.md', calls[0]['given'])
        # It plans from the digest of the materials and has the record of every element as a file of its own;
        # the materials as one text are kept beside the paper and given to no session.
        self.assertTrue({'materials-digest.md', *RECORD_FILES[3:]} <= set(calls[0]['given']))
        for call in calls:
            self.assertNotIn('materials.md', call['given'])
        self.assertEqual(self.events('plan')[0]['papers'], {s['id']: s['exemplars'] for s in PLAN['sections']})
        self.assertIn('"exemplars": the keys of the 6 papers you chose', calls[0]['prompt'])
        self.assertIn('output/study.md', calls[0]['prompt'])
        self.assertEqual(self.events('plan')[0]['exemplars'], CHOSEN)
        # The planning session's account of the papers is kept beside the paper.
        self.assertEqual((self.out / 'study.md').read_text(encoding='utf-8'), STUDY)
        # A writing session has the method, the brief of its section, the records, the plan, the parts that were
        # finished when it started, the planning session's account of the chosen papers and the two papers the
        # plan names for its section; it leaves no account of its own.
        self.assertEqual(calls[3]['given'], sorted(
            ['brief.md', 'paper-method.md', 'parts/abstract.tex', 'parts/intro.tex', 'plan.json', 'prompt.txt',
             'session.json', 'user-writing-preferences.md', 'study.md', 'exemplars/gamma.tex', 'exemplars/delta.tex']
            + RECORD_FILES))
        self.assertEqual([self.given(call) for call in calls[2:5]], [['alpha', 'beta'], ['delta', 'gamma'], ['epsilon', 'zeta']])
        self.assertNotIn('parts/abstract.tex', calls[2]['given'])
        self.assertEqual((self.out / 'sessions' / '04-write-tools' / 'study.md').read_text(encoding='utf-8'), STUDY)
        self.assertIn('The papers come before the writing.', calls[3]['prompt'])
        self.assertNotIn('output/study', calls[3]['prompt'])
        # Two readings beside papers the plan did not choose, each with papers of its own, found nothing.
        likeness = self.calls('likeness')
        for call, keys in zip(likeness, (FIRST_FOUR, NEXT_FOUR)):
            self.assertEqual(call['given'], sorted(['paper.tex', 'prompt.txt', 'references.bib', 'session.json']
                                                   + [f'exemplars/{key}.tex' for key in keys]))
            self.assertIn(', '.join(f'`exemplars/{key}.tex`' for key in keys), call['prompt'])
            self.assertIn(paper.method_part('Reading the manuscript beside real papers'), call['prompt'])
            for word in ('materials', 'Small.', 'plan.json'):
                self.assertNotIn(word, call['prompt'])
        self.assertEqual([(e['round'], e['exemplars'], e['likeness'], e['departures']) for e in self.events('likeness')],
                         [(1, FIRST_FOUR, LIKE['likeness'], []), (2, NEXT_FOUR, LIKE['likeness'], [])])
        # What the plan puts into a section is in the brief of the section.
        tools, proof = ((self.folder(call) / 'brief.md').read_text(encoding='utf-8') for call in calls[3:5])
        self.assertIn('stated here: lemma `lem:square`, which states the element `Small.sq_step`; its proof follows it', tools)
        self.assertIn('absorbed into lemma `lem:increasing`: `Small.oddSum_succ`', tools)
        self.assertIn('cited in the running text: `Small.expand`', tools)
        self.assertIn('proved here: theorem `thm:main` (`Small.root`), stated in section `intro`', proof)
        self.assertEqual(tools, paper.render_brief(self.materials(), PLAN, PLAN['sections'][1]))
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
        # The paper does not speak of Lean: it has no Lean name, no formal statement and no remark on formal verification,
        # and no session is asked to write one.
        tex = (self.out / 'paper.tex').read_text(encoding='utf-8')
        for word in ('Small.', 'Lean', 'verification'):
            self.assertNotIn(word, tex)
        for call in calls:
            self.assertNotIn('formal verification', call['prompt'])
            self.assertNotIn('LeanStatement', call['prompt'])
        self.assertEqual(self.events('materials')[0]['warnings'], [])
        # The correspondence file still gives the Lean statement of every numbered statement.
        self.assertEqual(rows['statements'][2]['lean_statement'],
                         'Small.sq_step (k : Nat) : k * k + (2 * k + 1) = (k + 1) * (k + 1)')
        self.assertIn('statements.json', calls[8]['given'])
        self.assertEqual(self.events('end')[0], {**self.events('end')[0], 'status': 'complete', 'open': []})
        self.assertEqual(len(self.events('session')), 12)
        # Planning and writing use the first common model; the readings and the comparisons the first model of review.
        chosen = {(c['kind'], tuple(read_json(self.out / 'sessions' / c['folder'] / 'session.json')[key]
                                    for key in ('model', 'effort'))) for c in self.calls()}
        self.assertEqual(chosen, {('plan', ('codex/gpt-6.1-sol', 'xhigh')), ('write', ('codex/gpt-6.1-sol', 'xhigh')),
                                  ('read', ('claude/opus', 'high')), ('likeness', ('claude/opus', 'high')),
                                  ('compare', ('claude/opus', 'high')), ('cover', ('claude/opus', 'high'))})

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
        # TeX names the line at which it noticed the error, which need not be where the cause lies: the repair goes
        # to the session that may change every part. It has the manuscript, the parts, the plan and the records.
        self.assertTrue({'paper.tex', 'parts/abstract.tex', 'parts/intro.tex', 'parts/tools.tex', 'parts/proof.tex',
                         'findings.json', 'plan.json', *RECORD_FILES} <= set(repair[0]['given']))
        self.assertFalse({'materials.md', 'brief.md', 'exemplars.md'} & set(repair[0]['given']))
        # It has the planning session's account of the chosen papers and the papers the plan names for the sections.
        self.assertEqual(self.given(repair[0]), sorted(CHOSEN))
        self.assertIn('study.md', repair[0]['given'])
        self.assertIn('section `tools`, `exemplars/gamma.tex` and `exemplars/delta.tex`', repair[0]['prompt'])
        self.assertIn('Whatever you rewrite is written as those papers are written,', repair[0]['prompt'])
        self.assertNotIn('output/study', repair[0]['prompt'])
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
        # The line lies in one section, so the session of that section repairs it, with the brief of the section.
        self.assertEqual([c['section'] for c in repair], ['wide-proof'])
        self.assertTrue({'brief.md', 'paper.tex', 'parts/proof.tex'} <= set(repair[0]['given']))
        self.assertFalse({'parts/tools.tex', 'parts/intro.tex'} & set(repair[0]['given']))
        self.assertEqual(self.given(repair[0]), ['epsilon', 'zeta'])
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

    def test_a_display_without_room_on_its_line_goes_to_a_repair_session(self):
        # TeX reports no line of this manuscript as too wide: the display fits by closing up its spaces. The
        # typesetting that measures the displays finds it, and it is repaired as a wide line is.
        script = good()
        script['write:proof'] = [{'output/proof.tex': PROOF + '\\[ a = b \\] % tight\n'}]
        script['repair:wide'] = [{'output/proof.tex': PROOF + '\\begin{align*} a &= b \\end{align*}\n'}]
        self.assertEqual(self.run_paper(script), 0)
        repair = self.calls('repair')
        self.assertEqual([c['section'] for c in repair], ['wide-proof'])
        findings = read_json(self.out / 'sessions' / repair[0]['folder'] / 'findings.json')
        self.assertEqual(len(findings), 1)
        self.assertRegex(findings[0], r'^paper\.tex, line \d+: the displayed formula that ends here is 12pt wider than the '
                                      r'room it has on its line')
        self.assertIn('closes up the spaces inside the formula', repair[0]['prompt'])
        checks = [(e['check'], bool(e['problems'])) for e in self.events('check')]
        self.assertEqual(checks[:6], [('machine checks of the manuscript', False), ('typesetting', False), (paper.WIDE, True),
                                      ('machine checks of the manuscript', False), ('typesetting', False), (paper.WIDE, False)])
        self.assertEqual(self.events('end')[0]['open'], [])
        # The PDF beside the manuscript is that of the manuscript, not that of the measuring.
        self.assertEqual((self.out / 'paper.pdf').read_bytes(), (self.out / 'typeset' / 'paper.pdf').read_bytes())
        self.assertNotIn('\\paper@equation', paper.read_file(self.out / 'typeset' / 'paper.tex'))

    def test_a_wide_line_that_stays_is_reported_and_the_paper_is_typeset_with_it(self):
        script = good()
        script['write:proof'] = [{'output/proof.tex': PROOF + '\\[ a = b \\] % wide\n'}]
        script['repair:wide'] = [{'output/proof.tex': PROOF + f'\\[ a = b \\] % wide, attempt {n}\n'} for n in range(9)]
        write_json(self.scenario / 'script.json', script)
        with patch('paper.worker_command', side_effect=self.command), patch('builtins.print') as shown:
            self.assertEqual(paper.produce(self.instance, self.out, TEX, parallel=1), 2)
        self.assertEqual(len(self.calls('repair')), paper.REPAIR_ROUNDS)
        # The paper is typeset, so the reading and the comparison are made as for any other manuscript.
        self.assertEqual((len(self.calls('read')), [(c['kind'], c['section']) for c in self.calls('compare')]), (1, COMPARED))
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

    def test_a_lean_name_or_the_word_lean_in_a_part_goes_to_a_repair_session(self):
        script = good()
        # A remark on formal verification as an earlier version of this command asked for, and a Lean name in a comment.
        remark = ('\\begin{remark}\nTheorem~\\ref{thm:main} has been formally verified in Lean, with Mathlib; the formal '
                  'statement is \\texttt{Small.root}.\n\\end{remark}\n')
        script['write:intro'] = [{'output/intro.tex': INTRO + remark, 'output/abstract.tex': ABSTRACT}]
        script['write:tools'] = [{'output/tools.tex': TOOLS + '% This is \\texttt{Small.oddSum\\_succ}.\n'}]
        script['repair:machine'] = [{'output/intro.tex': INTRO, 'output/tools.tex': TOOLS}]
        self.assertEqual(self.run_paper(script), 0)
        repair = self.calls('repair')
        self.assertEqual([c['section'] for c in repair], ['machine-intro', 'machine-tools'])
        found = [read_json(self.folder(call) / 'findings.json') for call in repair]
        self.assertEqual([len(findings) for findings in found], [2, 1])
        findings = found[0] + found[1]
        where = ' (method, section "The implementation does not show")'
        self.assertEqual(sorted(findings), sorted([
            'intro: Lean names of the canon appear: Small.root; the paper calls an object by its mathematical name' + where,
            'intro: the paper does not mention Lean, and this part has the words Lean, Mathlib' + where,
            'tools: Lean names of the canon appear: Small.oddSum_succ; the paper calls an object by its mathematical name'
            + where]))
        tex = (self.out / 'paper.tex').read_text(encoding='utf-8')
        for word in ('Small.', 'oddSum\\_succ', 'Lean', 'Mathlib'):
            self.assertNotIn(word, tex)
        checks = [(e['check'], bool(e['problems'])) for e in self.events('check')]
        self.assertEqual(checks[:2], [('machine checks of the manuscript', True), ('machine checks of the manuscript', False)])

    def test_the_reading_loop_is_bounded(self):
        script = good()
        script['read'] = [{'output/reading.json': json.dumps(FOUND)}]
        answer = json.dumps([{'finding': 1, 'action': 'revised', 'note': 'The expansion is now written out.'}])
        script['repair:reading'] = [{'output/tools.tex': TOOLS.replace('Expand the right-hand side.', f'Expand, version {n}.'),
                                     'output/response.json': answer} for n in range(9)]
        # What the last reading finds goes to a narrow repair, and a session reads the passage that it changed.
        script['repair:narrow'] = [{'output/tools.tex': TOOLS.replace('Expand the right-hand side.', EXPANDED),
                                    'output/response.json': answered('The expansion is written out.')}]
        script['changes'] = [{'output/verdicts.json': verdicts([(True, [1], 'Read with the proof of Lemma 2.2.')],
                                                               [(1, True, '')])}]
        self.assertEqual(self.run_paper(script), 0)
        kinds = [(c['kind'], c['section']) for c in self.calls()][4:]
        # A repair follows every reading. The one after the last reading is narrow and is followed by a reading of
        # what it changed, and by no other reading of the manuscript by itself.
        self.assertEqual(kinds, [('read', None), ('repair', 'reading')] * (paper.READING_ROUNDS - 1)
                         + [('read', None), ('repair', 'narrow-reading'), ('changes', None)]
                         + [('likeness', None)] * paper.LIKENESS_CLEAN + COMPARED + COVERED)
        repair = self.calls('repair')[0]
        findings = read_json(self.out / 'sessions' / repair['folder'] / 'findings.json')
        self.assertEqual((findings['findings'], findings['understanding']), (FOUND['findings'], FOUND['understanding']))
        self.assertEqual(len(self.events('reading')), paper.READING_ROUNDS)
        self.assertEqual(self.events('repair')[0]['response'][0]['action'], 'revised')
        # The second reader read what the first repair left, and the last reader what the last repair left.
        readers = [(self.out / 'sessions' / call['folder'] / 'paper.tex').read_text(encoding='utf-8')
                   for call in self.calls('read')]
        self.assertIn('Expand, version 0.', readers[1])
        self.assertIn(f'Expand, version {paper.READING_ROUNDS - 2}.', readers[-1])
        # The narrow repair had the manuscript that the last reader read, and what that reader found and understood.
        narrow = self.calls('repair')[-1]
        self.assertEqual((self.folder(narrow) / 'paper.tex').read_text(encoding='utf-8'), readers[-1])
        self.assertEqual(read_json(self.folder(narrow) / 'findings.json'), FOUND)
        self.assertIn('So this repair is narrow.', narrow['prompt'])
        self.assertNotIn('First compare the understanding with the research', narrow['prompt'])
        self.assertIn('In the note of a finding that you revise, say which passages you changed for it.', narrow['prompt'])
        self.assertIn('for a finding about the title, keep the text and say so', narrow['prompt'])
        self.assertNotIn('So this repair is narrow.', repair['prompt'])
        # The session that reads the changes has the manuscript as the repair left it and the one passage that differs
        # from what the last reader read, with its text before and after and the place where it stands.
        reader = self.calls('changes')[0]
        self.assertEqual(reader['given'], ['changes.json', 'paper.tex', 'prompt.txt', 'references.bib', 'session.json'])
        self.assertIn(paper.method_part('The reader'), reader['prompt'])
        tex = (self.folder(reader) / 'paper.tex').read_text(encoding='utf-8')
        given = read_json(self.folder(reader) / 'changes.json')
        self.assertEqual(given['changes'], [{'change': 1, 'part': 'tools', 'lines': given['changes'][0]['lines'],
                                             'before': f'Expand, version {paper.READING_ROUNDS - 2}.', 'after': EXPANDED,
                                             'findings': [1]}])
        self.assertEqual(tex.split('\n')[int(given['changes'][0]['lines']) - 1], EXPANDED)
        self.assertEqual(given['findings'], [{'finding': 1, 'check': paper.READING, 'reported': FOUND['findings'][0],
                                              'repair': 'The expansion is written out.'}])
        # The change was found sound and to answer the finding: it stays, and nothing is left open.
        self.assertEqual((self.out / 'paper.tex').read_text(encoding='utf-8'), tex)
        last = self.events('repair')[-1]
        self.assertEqual((last['of'], last['narrow'], last['changed']), ('reading', True, ['tools']))
        self.assertEqual(self.events('changes')[0]['undone'], [])
        end = self.events('end')[0]
        self.assertEqual((end['status'], end['open']), ('complete', []))
        state = read_json(self.out / 'state.json')
        self.assertEqual((state['narrow'], state['rewritten']), (None, False))
        self.assertFalse((self.out / 'narrow').exists())
        self.assertEqual(self.events('note'), [])
        self.assertTrue((self.out / 'paper.pdf').is_file())

    def test_a_statement_that_differs_is_repaired_and_compared_again(self):
        script = good()
        differs = [dict(row) for row in SAME]
        differs[2].update(verdict='differs', difference='The manuscript has k^2 + 2k = (k + 1)^2.')
        script['write:tools'] = [{'output/tools.tex': TOOLS.replace('k^2 + (2k + 1)', 'k^2 + 2k')}]
        script['compare:tools'] = [{'output/comparison.json': json.dumps(differs[1:])},
                                   {'output/comparison.json': json.dumps(SAME[1:])}]
        script['repair:comparison'] = [{'output/tools.tex': TOOLS, 'output/response.json': json.dumps(
            [{'finding': 1, 'action': 'revised', 'note': 'The term 1 is restored.'}])}]
        self.assertEqual(self.run_paper(script), 0)
        self.assertEqual([len(e['differing']) for e in self.events('comparison')], [1, 0])
        # The repair changed a statement and may have adjusted its proof, so the manuscript was read by itself
        # again before its statements were compared once more.
        self.assertEqual([(c['kind'], c['section']) for c in self.calls()][-8:],
                         [*COMPARED, ('repair', 'comparison-tools'), ('read', None), *COMPARED, *COVERED])
        again = self.calls('read')[-1]
        self.assertIn('k^2 + (2k + 1)', (self.out / 'sessions' / again['folder'] / 'paper.tex').read_text(encoding='utf-8'))
        rows = read_json(self.out / 'correspondence.json')['statements']
        self.assertEqual([r['comparison']['verdict'] for r in rows], ['same'] * 3)
        self.assertIn('k^2 + (2k + 1)', rows[2]['paper_statement'])

    def test_a_difference_that_the_bounded_repairs_leave_is_reported(self):
        script = good()
        differs = [dict(row) for row in SAME]
        differs[2].update(verdict='differs', difference='The manuscript has k^2 + 2k = (k + 1)^2.')
        script['write:tools'] = [{'output/tools.tex': TOOLS.replace('k^2 + (2k + 1)', 'k^2 + 2k')}]
        script['compare:tools'] = [{'output/comparison.json': json.dumps(differs[1:])}]
        script['repair:comparison'] = [{'output/tools.tex': TOOLS.replace('k^2 + (2k + 1)', 'k^2 + 2k + 0'), 'output/response.json':
                                        json.dumps([{'finding': 1, 'action': 'revised', 'note': 'A term was added.'}])}]
        self.assertEqual(self.run_paper(script), 2)
        self.assertEqual([(c['kind'], c['section']) for c in self.calls('compare')], COMPARED * paper.COMPARISON_ROUNDS)
        self.assertEqual(len(self.calls('repair')), paper.COMPARISON_ROUNDS - 1)
        rows = read_json(self.out / 'correspondence.json')['statements']
        self.assertEqual(rows[2]['comparison'], {'verdict': 'differs', 'difference': differs[2]['difference'],
                                                 'record_disagreement': ''})
        self.assertEqual(self.events('end')[0]['open'][0]['problems'][0]['label'], 'lem:square')

    def test_a_disagreement_inside_the_record_of_an_element_is_reported_beside_the_paper(self):
        script = good()
        noted = [dict(row) for row in SAME]
        noted[1]['record_disagreement'] = 'The record states the inequality for n >= 1; the Lean statement holds for every n.'
        script['compare:tools'] = [{'output/comparison.json': json.dumps(noted[1:])}]
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
        self.assertEqual([c['kind'] for c in self.calls()],
                         ['plan', 'write', 'write', 'write', 'read', 'likeness', 'likeness', 'compare', 'compare',
                          'cover', 'cover'])
        self.assertEqual((self.events('end')[0]['status'], self.events('materials')[0]['tex']), ('no_tex', None))
        self.assertEqual([e['check'] for e in self.events('check')], ['machine checks of the manuscript'])
        # A folder that holds a manuscript is not written over by a new run; it is typeset as it stands.
        with self.assertRaises(paper.Stop):
            self.run_paper(good())
        launched = len(self.calls())
        # Typesetting later does not use the collection: a paper missing from it is neither fetched nor missed.
        (self.exemplars / 'alpha.tex').unlink()
        self.assertEqual(self.run_paper(good(), only=True), 0)
        self.assertFalse((self.exemplars / 'runs.txt').exists())
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
        script['compare:tools'] = [{'output/comparison.json': json.dumps(differs[1:])}]
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

    def test_a_statement_that_a_repair_changes_while_typesetting_later_is_reported_as_not_compared(self):
        script = good()
        broken = TOOLS.replace('For every natural number $k$, we have', 'For every natural number $k$, \\undefinedmacro we have')
        self.assertNotEqual(broken, TOOLS)
        script['write:tools'] = [{'output/tools.tex': broken}]
        script['repair:typeset'] = [{'output/tools.tex': TOOLS}]
        # Without TeX the macro goes unnoticed: the manuscript is read and compared, and the lemma is judged as written.
        with patch('paper.shutil.which', return_value=None):
            self.assertEqual(self.run_paper(script, tex=None), 3)
        rows = read_json(self.out / 'correspondence.json')['statements']
        self.assertEqual([r['comparison']['verdict'] for r in rows], ['same'] * 3)
        compared = len(self.calls('compare'))
        # Typesetting later repairs the lemma and does not compare again, so its present text has no verdict.
        self.assertEqual(self.run_paper(script, only=True), 2)
        self.assertEqual([c['section'] for c in self.calls('repair')], ['typeset'])
        self.assertEqual(len(self.calls('compare')), compared)
        self.assertTrue((self.out / 'paper.pdf').is_file())
        rows = read_json(self.out / 'correspondence.json')['statements']
        self.assertEqual([r['comparison']['verdict'] for r in rows], ['same', 'same', 'not compared'])
        end = self.events('end')[-1]
        self.assertEqual((end['status'], [item['check'] for item in end['open']]), ('open_findings', [paper.UNCOMPARED]))
        self.assertEqual([problem['label'] for problem in end['open'][0]['problems']], ['lem:square'])
        # Typesetting it once more finds the same statement without a verdict and reports it once.
        self.assertEqual(self.run_paper(script, only=True), 2)
        end = self.events('end')[-1]
        self.assertEqual([(item['check'], [problem['label'] for problem in item['problems']]) for item in end['open']],
                         [(paper.UNCOMPARED, ['lem:square'])])

    def test_a_plan_without_its_account_and_a_report_of_the_wrong_shape_go_back_with_the_reasons(self):
        script = good()
        script['plan'] = [{'output/plan.json': json.dumps(PLAN)}, {'output/plan.json': json.dumps(PLAN), 'output/study.md': ' \n'},
                          *script['plan']]
        shapeless = {'likeness': '', 'departures': [{'where': 'the abstract', 'quote': None,
                                                     'evidence': [{'exemplar': 'theta'}], 'difference': 'Longer.'}]}
        script['likeness'].insert(0, {'output/likeness.json': json.dumps(shapeless)})
        self.assertEqual(self.run_paper(script), 0)
        plans, likeness = self.calls('plan'), self.calls('likeness')
        self.assertEqual((len(plans), len(likeness)), (paper.PLAN_ATTEMPTS, 3))
        for call in plans[1:]:
            self.assertIn('output/study.md, the account of how the chosen papers are written, was not written or is empty',
                          call['prompt'])
        self.assertEqual((self.out / 'study.md').read_text(encoding='utf-8'), STUDY)
        for reason in ('"likeness" is a text that is not empty', 'departure 1: "quote" is a text',
                       'departure 1: "evidence" is an array of objects, each with "exemplar" and "quote" as text'):
            self.assertIn(reason, likeness[1]['prompt'])
        self.assertIn('previous-output/likeness.json', likeness[1]['given'])
        # The reading done again has the papers of the reading it replaces; the next reading has others.
        self.assertEqual([self.given(c) for c in likeness], [sorted(FIRST_FOUR), sorted(FIRST_FOUR), sorted(NEXT_FOUR)])
        self.assertEqual([e['round'] for e in self.events('likeness')], [1, 2])
        self.assertIn('output of the likeness session', [e['check'] for e in self.events('check')])

    def test_a_departure_from_the_papers_is_repaired_and_the_manuscript_read_again_beside_other_papers(self):
        script = good()
        script['likeness'] = [{'output/likeness.json': json.dumps(departed('The abstract says more than theirs.'))},
                              {'output/likeness.json': json.dumps(LIKE)}]
        script['repair:likeness'] = [{'output/intro.tex': INTRO + f'Version {n} of the introduction.\n',
                                      'output/response.json': answered('The opening is rewritten.')} for n in range(9)]
        self.assertEqual(self.run_paper(script), 0)
        kinds = [(c['kind'], c['section']) for c in self.calls()][5:]
        self.assertEqual(kinds, [('likeness', None), ('repair', 'likeness'), ('likeness', None), ('likeness', None),
                                 ('read', None), *COMPARED, *COVERED])
        repair = self.calls('repair')[0]
        self.assertEqual(read_json(self.out / 'sessions' / repair['folder'] / 'findings.json'),
                         [departure('The abstract says more than theirs.')])
        self.assertIn('places where the manuscript is written otherwise than real papers are written', repair['prompt'])
        self.assertIn('The mathematics stays as it is, and so do the plan and the decisions of the method', repair['prompt'])
        self.assertIn('output/response.json', repair['prompt'])
        self.assertEqual(self.given(repair), sorted(CHOSEN))
        self.assertIn('study.md', repair['given'])
        self.assertEqual(self.events('repair')[0]['of'], 'likeness')
        # The repaired manuscript was settled and read again, beside other papers, until two readings found nothing.
        second = (self.out / 'sessions' / self.calls('likeness')[1]['folder'] / 'paper.tex').read_text(encoding='utf-8')
        self.assertIn('Version 0 of the introduction.', second)
        self.assertEqual([(e['round'], e['exemplars'], len(e['departures'])) for e in self.events('likeness')],
                         [(1, FIRST_FOUR, 1), (2, NEXT_FOUR, 0), (3, FIRST_FOUR, 0)])
        self.assertEqual(self.events('end')[0]['open'], [])
        # The repair rewrote the manuscript after it had been read by itself, so it was read in that way again:
        # by a session that has what the first reader had, and that reads what the repair left.
        first, again = self.calls('read')
        self.assertEqual(again['given'], first['given'])
        self.assertIn('Version 0 of the introduction.',
                      (self.out / 'sessions' / again['folder'] / 'paper.tex').read_text(encoding='utf-8'))
        self.assertEqual([e['round'] for e in self.events('reading')], [1, 2])

    def test_readings_without_two_clean_ones_in_succession_leave_the_last_departures_to_the_resolving_session(self):
        # Every odd reading has a departure and every even one has none, so no two clean readings follow each other.
        rounds = paper.LIKENESS_ROUNDS
        self.assertEqual(rounds % 2, 0)
        script = good()
        script['likeness'] = [{'output/likeness.json': json.dumps(departed(f'reading {n}') if n % 2 else LIKE)}
                              for n in range(1, rounds + 1)]
        script['repair:likeness'] = [{'output/intro.tex': INTRO + f'Version {n} of the introduction.\n',
                                      'output/response.json': answered('Rewritten.')} for n in range(rounds)]
        script['resolve'] = keeps(1)
        self.assertEqual(self.run_paper(script), 0)
        kinds = [(c['kind'], c['section']) for c in self.calls()][5:]
        self.assertEqual(kinds, [('likeness', None), ('repair', 'likeness'), ('likeness', None)] * (rounds // 2)
                         + [('read', None), *COMPARED, ('resolve', None), *COVERED])
        self.assertEqual(len(self.calls('likeness')), rounds)
        # The last reading found nothing, and the departures of the one before it stayed open: one clean reading
        # after their repair is not two. The resolving session was given them with that reason. It kept the text,
        # so they are listed with its reason, and they are not open.
        left = {**departure(f'reading {rounds - 1}'), 'open_because': paper.ONCE_CONFIRMED}
        resolver = self.calls('resolve')[0]
        self.assertEqual(read_json(self.folder(resolver) / 'findings.json')['findings'],
                         [{'finding': 1, 'check': paper.LIKENESS, 'reported': left}])
        end = self.events('end')[0]
        self.assertEqual((end['status'], end['open'], end['kept']),
                         ('complete', [], kept_by_resolve(paper.LIKENESS, left)))
        # When the papers the plan did not choose are used up, the readings take them again from the first.
        self.assertEqual([e['exemplars'] for e in self.events('likeness')], [FIRST_FOUR, NEXT_FOUR] * (rounds // 2))
        # The comparison still runs, and its verdicts stand beside the paper.
        rows = read_json(self.out / 'correspondence.json')['statements']
        self.assertEqual([r['comparison']['verdict'] for r in rows], ['same'] * 3)
        self.assertTrue((self.out / 'paper.pdf').is_file())

    def test_what_the_repair_after_the_last_reading_beside_real_papers_keeps_goes_on_with_its_reason(self):
        rounds = paper.LIKENESS_ROUNDS
        script = good()
        script['likeness'] = [{'output/likeness.json': json.dumps(departed(f'reading {n}'))} for n in range(1, rounds + 1)]
        script['repair:likeness'] = [{'output/intro.tex': INTRO + f'Version {n} of the introduction.\n',
                                      'output/response.json': answered('Rewritten.')} for n in range(rounds)]
        # The repair after the last of these readings is narrow, and its session keeps the text.
        script['repair:narrow'] = [{'output/response.json': json.dumps(
            [{'finding': 1, 'action': 'kept', 'note': 'A shorter abstract would drop a hypothesis.'}])}]
        script['resolve'] = keeps(1)
        self.assertEqual(self.run_paper(script), 0)
        kinds = [(c['kind'], c['section']) for c in self.calls()][5:]
        # It changed nothing, so no session reads changes. The repairs before it rewrote the introduction, so the
        # manuscript is read by itself once more, as before.
        self.assertEqual(kinds, [('likeness', None), ('repair', 'likeness')] * (rounds - 1)
                         + [('likeness', None), ('repair', 'narrow-likeness'), ('read', None), *COMPARED,
                            ('resolve', None), *COVERED])
        narrow = self.calls('repair')[-1]
        self.assertEqual(read_json(self.folder(narrow) / 'findings.json'), [departure(f'reading {rounds}')])
        self.assertIn('So this repair is narrow.', narrow['prompt'])
        self.assertNotIn('Rewrite the parts so that at each of these places', narrow['prompt'])
        # What the narrow repair kept went to the resolving session with the reason of that repair, and is listed
        # at the end with the reason of the resolving session.
        end = self.events('end')[0]
        self.assertEqual((end['open'], end['kept']), ([], kept_by_resolve(paper.LIKENESS, {
            **departure(f'reading {rounds}'),
            'open_because': paper.KEPT + 'A shorter abstract would drop a hypothesis.'})))
        self.assertEqual(self.events('changes'), [])
        self.assertTrue((self.out / 'paper.pdf').is_file())

    def test_the_repair_after_the_last_reading_beside_real_papers_is_narrow_and_its_changes_are_read(self):
        named = {**departure('The lemma is announced by no sentence.'), 'where': 'Lemma 2.2', 'section': 'sec:tools',
                 'quote': 'Expand the right-hand side.'}
        kept = {**departure('The proof is one line.'), 'where': 'Lemma 2.1', 'section': 'sec:tools', 'quote': 'exceeds'}
        script = good()
        script['likeness'] = [{'output/likeness.json': json.dumps(
            {**LIKE, 'departures': [departure('The abstract says more than theirs.'), named, kept]})}]
        # The session of the section revises one passage and keeps the other; the session for what concerns no single
        # section shortens the abstract.
        script['repair:narrow-likeness-tools'] = [{'output/tools.tex': TOOLS.replace('Expand the right-hand side.', EXPANDED),
                                                   'output/response.json': answers('revised', 'kept')}]
        script['repair:narrow-likeness'] = [{'output/abstract.tex': 'The sum of the first $n$ odd numbers is $n^2$.\n',
                                             'output/response.json': answers('revised')}]
        # Both changes are sound. The one in the abstract does not answer its finding.
        script['changes'] = [{'output/verdicts.json': verdicts(
            [(True, [1], 'Read with the introduction.'), (True, [2], 'Read with the proof of Lemma 2.2.')],
            [(1, False, 'The abstract still names the method.'), (2, True, '')])}]
        script['resolve'] = keeps(2)
        with patch('paper.LIKENESS_ROUNDS', 1):
            self.assertEqual(self.run_paper(script), 0)
        # The first of these readings is here the last that the bound allows. No repair that may rewrite was made, and
        # the changes of the narrow repair were read where they stand, so the manuscript is not read by itself again.
        self.assertEqual([(c['kind'], c['section']) for c in self.calls()][4:],
                         [('read', None), ('likeness', None), ('repair', 'narrow-likeness-tools'),
                          ('repair', 'narrow-likeness'), ('changes', None), *COMPARED, ('resolve', None), *COVERED])
        tools, whole = self.calls('repair')
        self.assertEqual(read_json(self.folder(tools) / 'findings.json'), [named, kept])
        for call in (tools, whole):
            self.assertIn('So this repair is narrow.', call['prompt'])
            self.assertIn('change the passage that the finding quotes', call['prompt'])
        self.assertNotIn('Rewrite this section so that at each of these places', tools['prompt'])
        # The reader of the changes has both passages in the order of the manuscript, each with the findings whose
        # session changed its part and that the session answered by a change.
        given = read_json(self.folder(self.calls('changes')[0]) / 'changes.json')
        self.assertEqual([(c['change'], c['part'], c['before'], c['after'], c['findings']) for c in given['changes']],
                         [(1, 'abstract', ABSTRACT.strip(), 'The sum of the first $n$ odd numbers is $n^2$.', [1]),
                          (2, 'tools', 'Expand the right-hand side.', EXPANDED, [2])])
        self.assertEqual([(f['finding'], f['check'], f['repair']) for f in given['findings']],
                         [(1, paper.LIKENESS, 'revised 1'), (2, paper.LIKENESS, 'revised 1')])
        # Both changes stay. The finding that its change does not answer and the one that was kept went on to the
        # resolving session, each with its reason.
        self.assertEqual(self.part('abstract'), 'The sum of the first $n$ odd numbers is $n^2$.\n')
        self.assertIn(EXPANDED, self.part('tools'))
        end = self.events('end')[0]
        self.assertEqual((end['open'], end['kept']), ([], kept_by_resolve(
            paper.LIKENESS,
            {**departure('The abstract says more than theirs.'),
             'open_because': paper.UNANSWERED + 'The abstract still names the method.'},
            {**kept, 'open_because': paper.KEPT + 'kept 2'})))
        state = read_json(self.out / 'state.json')
        self.assertEqual((state['narrow'], state['rewritten']), (None, False))
        # The statements were compared afterwards, in the normal course.
        rows = read_json(self.out / 'correspondence.json')['statements']
        self.assertEqual([r['comparison']['verdict'] for r in rows], ['same'] * 3)

    def test_a_change_that_the_reading_of_the_changes_faults_is_undone_and_its_finding_goes_on_with_the_reason(self):
        script = good()
        script['read'] = [{'output/reading.json': json.dumps({**CLEAN, 'findings': [EXPANSION, GAIN]})}]
        script['repair:narrow-reading-tools'] = [{'output/tools.tex': TOOLS_BOTH, 'output/response.json': answers('revised', 'revised')}]
        # In the manuscript the passage of the second finding comes first. Its change is sound; the other loses a term.
        script['changes'] = [{'output/verdicts.json': verdicts(
            [(True, [2], 'Read with the proof of Lemma 2.1.'), (False, [1], 'The expansion drops the factor of $k$.')],
            [(1, True, ''), (2, True, '')])}]
        script['resolve'] = keeps(1)
        with patch('paper.READING_ROUNDS', 1):
            self.assertEqual(self.run_paper(script), 0)
        # Both findings lie in one section, so one session repairs them, and none is launched for the whole.
        self.assertEqual([(c['kind'], c['section']) for c in self.calls()][4:],
                         [('read', None), ('repair', 'narrow-reading-tools'), ('changes', None), ('likeness', None),
                          ('likeness', None), *COMPARED, ('resolve', None), *COVERED])
        repair = self.calls('repair')[0]
        self.assertIn('In every other case revise the passage that the finding names', repair['prompt'])
        self.assertNotIn('which may mean rewriting the passage', repair['prompt'])
        self.assertNotIn('open_because', repair['prompt'])
        given = read_json(self.folder(self.calls('changes')[0]) / 'changes.json')
        self.assertEqual([(c['before'], c['after'], c['findings']) for c in given['changes']],
                         [('The sum $S_{n+1}$ exceeds $S_n$ by $2n + 1$.', GAINED, [1, 2]),
                          ('Expand the right-hand side.', EXPANDED, [1, 2])])
        # The faulted passage reads again as the reader read it, and the sound change beside it stays.
        self.assertEqual(self.part('tools'), TOOLS_GAINED)
        compared = self.calls('compare')[1]
        self.assertEqual((self.folder(compared) / 'paper.tex').read_text(encoding='utf-8'),
                         (self.out / 'paper.tex').read_text(encoding='utf-8'))
        self.assertIn(GAINED, (self.out / 'paper.tex').read_text(encoding='utf-8'))
        self.assertNotIn(EXPANDED, (self.out / 'paper.tex').read_text(encoding='utf-8'))
        changes = self.events('changes')[0]
        self.assertEqual((changes['undone'], [c['sound'] for c in changes['changes']]), ([2], [True, False]))
        # The finding whose change was undone went on to the resolving session, with what the reading of the
        # changes found.
        end = self.events('end')[0]
        self.assertEqual((end['status'], end['open'], end['kept']), ('complete', [], kept_by_resolve(
            paper.READING, {**EXPANSION, 'open_because': paper.UNDONE + 'The expansion drops the factor of $k$.'})))
        self.assertTrue((self.out / 'paper.pdf').is_file())
        self.assertFalse((self.out / 'narrow').exists())

    def test_the_changes_made_for_one_finding_are_undone_together(self):
        script = good()
        script['read'] = [{'output/reading.json': json.dumps({**CLEAN, 'findings': [EXPANSION, BASE]})}]
        script['repair:narrow-reading-tools'] = [{'output/tools.tex': TOOLS_BOTH, 'output/response.json': answers('revised')}]
        script['repair:narrow-reading-proof'] = [{'output/proof.tex': PROOF_BASED, 'output/response.json': answers('revised')}]
        # The session of `tools` changed two passages for its one finding. The reading faults the second of them.
        script['changes'] = [{'output/verdicts.json': verdicts(
            [(True, [1], 'Read with the proof of Lemma 2.1.'), (False, [1], 'The expansion drops the factor of $k$.'),
             (True, [2], 'Read with the proof.')], [(1, False, 'Nothing is expanded.'), (2, True, '')])}]
        script['resolve'] = keeps(1)
        with patch('paper.READING_ROUNDS', 1):
            self.assertEqual(self.run_paper(script), 0)
        self.assertEqual((self.part('tools'), self.part('proof')), (TOOLS, PROOF_BASED))
        self.assertEqual(self.events('changes')[0]['undone'], [1, 2])
        self.assertEqual(self.events('end')[0]['kept'], kept_by_resolve(
            paper.READING, {**EXPANSION, 'open_because': paper.UNDONE + 'The expansion drops the factor of $k$.'}))

    def test_changes_with_which_the_manuscript_cannot_be_typeset_are_all_undone(self):
        script = good()
        script['read'] = [{'output/reading.json': json.dumps(FOUND)}]
        script['repair:narrow'] = [{'output/tools.tex': TOOLS.replace('Expand the right-hand side.', EXPANDED + ' \\undefinedmacro'),
                                    'output/response.json': answered('The expansion is written out.')}]
        script['repair:typeset'] = [{'output/tools.tex': TOOLS.replace('Expand the right-hand side.',
                                                                       EXPANDED + f' \\undefinedmacro % attempt {n}')}
                                    for n in range(9)]
        script['resolve'] = keeps(1)
        with patch('paper.READING_ROUNDS', 1):
            self.assertEqual(self.run_paper(script), 0)
        # The bounded repairs of the typesetting did not help. The text that the reader read is put back, the finding
        # stays open for the resolving session, and the run goes on; no session reads changes, since none is left.
        self.assertEqual([(c['kind'], c['section']) for c in self.calls()][4:],
                         [('read', None), ('repair', 'narrow-reading')] + [('repair', 'typeset')] * paper.REPAIR_ROUNDS
                         + [('likeness', None), ('likeness', None), *COMPARED, ('resolve', None), *COVERED])
        self.assertEqual(self.part('tools'), TOOLS)
        end = self.events('end')[0]
        self.assertEqual(([item['check'] for item in end['kept']], end['open']), ([paper.READING], []))
        self.assertTrue(end['kept'][0]['finding']['open_because'].startswith(paper.FAILING))
        self.assertIn('Undefined control sequence', end['kept'][0]['finding']['open_because'])
        self.assertTrue((self.out / 'paper.pdf').is_file())
        self.assertNotIn('undefinedmacro', (self.out / 'paper.tex').read_text(encoding='utf-8'))

    def test_changes_that_do_not_pass_the_checks_without_an_undone_one_are_all_undone(self):
        script = good()
        script['read'] = [{'output/reading.json': json.dumps({**CLEAN, 'findings': [EXPANSION, GAIN]})}]
        # The change for the second finding displays a formula with a label, and the change for the first refers to it.
        gain = 'The gain is \\begin{equation}\\label{eq:tools-gain} S_{n+1} - S_n = 2n + 1. \\end{equation}'
        expansion = 'Expand the right-hand side as in \\eqref{eq:tools-gain}.'
        script['repair:narrow-reading-tools'] = [{
            'output/tools.tex': TOOLS.replace('The sum $S_{n+1}$ exceeds $S_n$ by $2n + 1$.', gain)
            .replace('Expand the right-hand side.', expansion), 'output/response.json': answers('revised', 'revised')}]
        script['changes'] = [{'output/verdicts.json': verdicts(
            [(False, [2], 'The display states the gain and proves nothing.'), (True, [1], 'Read with the proof.')],
            [(1, True, ''), (2, False, 'Not derived.')])}]
        script['resolve'] = keeps(2)
        with patch('paper.READING_ROUNDS', 1):
            self.assertEqual(self.run_paper(script), 0)
        # With the display undone, the reference of the other change points nowhere, which the machine checks find.
        # No repair is made for it: the other change is undone as well.
        self.assertEqual(self.calls('repair')[1:], [])
        self.assertEqual(self.part('tools'), TOOLS)
        checks = [(e['check'], bool(e['problems'])) for e in self.events('check')]
        self.assertIn((paper.MACHINE, True), checks)
        self.assertEqual(checks[-3:], [(paper.MACHINE, False), (paper.TYPESETTING, False), (paper.WIDE, False)])
        end = self.events('end')[0]
        self.assertEqual(([item['check'] for item in end['kept']], end['open']), ([paper.READING] * 2, []))
        self.assertEqual([item['finding']['where'] for item in end['kept']], ['Lemma 2.2', 'Lemma 2.1'])
        for item in end['kept']:
            self.assertTrue(item['finding']['open_because'].startswith(paper.FAILING))
            self.assertIn('eq:tools-gain', item['finding']['open_because'])
        self.assertTrue((self.out / 'paper.pdf').is_file())

    def test_what_a_reading_after_those_repairs_finds_is_repaired_and_read_again(self):
        script = good()
        script['likeness'] = [{'output/likeness.json': json.dumps(departed('The abstract says more than theirs.'))},
                              {'output/likeness.json': json.dumps(LIKE)}]
        script['repair:likeness'] = [{'output/intro.tex': INTRO + 'Version 0 of the introduction.\n',
                                      'output/response.json': answered('The opening is rewritten.')}]
        # The reader finds nothing before the readings beside real papers, and a gap after the repair that followed one.
        script['read'] = [{'output/reading.json': json.dumps(report)} for report in (CLEAN, FOUND, CLEAN)]
        script['repair:reading'] = [{'output/tools.tex': TOOLS.replace('Expand the right-hand side.', 'Expand, version 0.'),
                                     'output/response.json': answered('The expansion is now written out.')}]
        self.assertEqual(self.run_paper(script), 0)
        kinds = [(c['kind'], c['section']) for c in self.calls()][4:]
        self.assertEqual(kinds, [('read', None), ('likeness', None), ('repair', 'likeness'), ('likeness', None),
                                 ('likeness', None), ('read', None), ('repair', 'reading'), ('read', None),
                                 *COMPARED, *COVERED])
        self.assertEqual([e['of'] for e in self.events('repair')], ['likeness', 'reading'])
        # The readings are counted over the whole run: one before the readings beside real papers and two after.
        self.assertEqual([(e['round'], len(e['findings'])) for e in self.events('reading')], [(1, 0), (2, 1), (3, 0)])
        # The last reader and the comparison had the manuscript as both repairs left it.
        for call in (self.calls('read')[2], self.calls('compare')[0]):
            tex = (self.out / 'sessions' / call['folder'] / 'paper.tex').read_text(encoding='utf-8')
            self.assertIn('Version 0 of the introduction.', tex)
            self.assertIn('Expand, version 0.', tex)
        self.assertEqual(self.events('note'), [])
        self.assertEqual(self.events('end')[0], {**self.events('end')[0], 'status': 'complete', 'open': []})

    def test_the_readings_after_those_repairs_are_bounded_as_the_first_ones_are(self):
        script = good()
        script['likeness'] = [{'output/likeness.json': json.dumps(departed('The abstract says more than theirs.'))},
                              {'output/likeness.json': json.dumps(LIKE)}]
        script['repair:likeness'] = [{'output/intro.tex': INTRO + 'Version 0 of the introduction.\n',
                                      'output/response.json': answered('The opening is rewritten.')}]
        # Every reading after the repair has a finding: the script's last entry serves each of them.
        script['read'] = [{'output/reading.json': json.dumps(report)} for report in (CLEAN, FOUND)]
        script['repair:reading'] = [{'output/tools.tex': TOOLS.replace('Expand the right-hand side.', f'Expand, version {n}.'),
                                     'output/response.json': answered('The expansion is now written out.')} for n in range(9)]
        # The repair after the last of them is narrow, and the reading of its change finds that it loses a term.
        script['repair:narrow'] = [{'output/tools.tex': TOOLS.replace('Expand the right-hand side.', EXPANDED),
                                    'output/response.json': answered('The expansion is written out.')}]
        script['changes'] = [{'output/verdicts.json': verdicts([(False, [1], 'The expansion drops the factor of $k$.')],
                                                               [(1, False, 'Nothing is expanded.')])}]
        script['resolve'] = keeps(1)
        self.assertEqual(self.run_paper(script), 0)
        kinds = [(c['kind'], c['section']) for c in self.calls()][9:]
        self.assertEqual(kinds, [('read', None), ('repair', 'reading')] * (paper.READING_ROUNDS - 1)
                         + [('read', None), ('repair', 'narrow-reading'), ('changes', None), *COMPARED,
                            ('resolve', None), *COVERED])
        self.assertEqual([e['round'] for e in self.events('reading')], list(range(1, paper.READING_ROUNDS + 2)))
        # The change is undone, so the finding goes on to the resolving session, and the comparison has the text
        # that the last reader read.
        end = self.events('end')[0]
        self.assertEqual((end['open'], end['kept']), ([], kept_by_resolve(paper.READING, {
            **FOUND['findings'][0], 'open_because': paper.UNDONE + 'The expansion drops the factor of $k$.'})))
        last, compared = (self.out / 'sessions' / self.calls(kind)[-1]['folder'] / 'paper.tex' for kind in ('read', 'compare'))
        self.assertEqual(last.read_text(encoding='utf-8'), compared.read_text(encoding='utf-8'))
        self.assertEqual(compared.read_text(encoding='utf-8'), (self.out / 'paper.tex').read_text(encoding='utf-8'))

    def test_a_repair_that_keeps_every_passage_is_not_followed_by_another_reading(self):
        script = good()
        script['likeness'] = [{'output/likeness.json': json.dumps(departed('The abstract says more than theirs.'))},
                              {'output/likeness.json': json.dumps(LIKE)}]
        script['repair:likeness'] = [{'output/response.json': json.dumps(
            [{'finding': 1, 'action': 'kept', 'note': 'Shortening the abstract would drop a hypothesis.'}])}]
        self.assertEqual(self.run_paper(script), 0)
        kinds = [(c['kind'], c['section']) for c in self.calls()][4:]
        # Nothing was rewritten, so the manuscript is as its one reader left it.
        self.assertEqual(kinds, [('read', None), ('likeness', None), ('repair', 'likeness'), ('likeness', None),
                                 ('likeness', None), *COMPARED, *COVERED])
        self.assertEqual(self.events('repair')[0]['changed'], [])

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

class BriefTests(PaperCase):
    """What the script makes for the sessions from the plan and the materials: the digest, the records, the briefs."""

    def setUp(self):
        super().setUp()
        self.found = self.materials()
        self.layout = paper.Layout(self.found, PLAN)

    def brief(self, sid):
        """The brief of a section: the whole, the records it gives in full, and the elements it gives by their statements."""
        section = next(section for section in PLAN['sections'] if section['id'] == sid)
        text = paper.render_brief(self.found, PLAN, section)
        head, cited = text.split('\n## Elements of other sections, by their statements\n')
        return text, head.split('\n## The records in full\n')[1], cited

    def headings(self, text):
        """The names under the headings of the elements, in their order."""
        return [line.split('`')[1] for line in text.splitlines() if line.startswith('### ') and '`' in line]

    def test_the_planning_session_has_every_element_by_its_statement_and_each_record_as_a_file(self):
        digest = paper.render_digest(self.found)
        names = [element['name'] for element in self.found['elements']]
        # Every element is there by what it says, in dependence order, with the file of its record and its lengths.
        self.assertEqual(self.headings(digest), ['Small.root'] + names)
        lemma = digest[digest.index('### 6. `Small.sq_step`'):digest.index('### 7. `Small.root`')]
        for words in ('statement · weight: unit · short name: completing the square',
                      'theorem Small.sq_step (k : Nat) : k * k + (2 * k + 1) = (k + 1) * (k + 1)',
                      'Its statement mentions (nothing). Its proof names `Small.expand`. It is named or mentioned by '
                      '`Small.root`.',
                      '**Description.** Adding 2k + 1 to a square gives the next square.',
                      '**Statement.** For every natural number $k$, $k^2 + (2k + 1) = (k + 1)^2$.',
                      'Full record: `elements/Small.sq_step.md` (no explanation in words; proof in words: '
                      + str(len(self.found['elements'][5]['proof'])) + ' characters).'):
            self.assertIn(words, lemma)
        # The proofs in words are left to the files, except that of the declaration that settles the root.
        self.assertNotIn('**Proof.**', lemma)
        self.assertNotIn('Expand $(k + 1)^2$ by `Small.expand`.', digest)
        self.assertEqual(digest.count('**Proof.**'), 1)
        settles = digest[digest.index('## The declaration that settles the root, with its record in full'):
                         digest.index('## The elements the proof rests on')]
        self.assertIn('**Proof.**\n\nBy induction on $n$; the step is `Small.sq_step`.', settles)
        # The root, the account of the problem with its review, and the bibliography are there as in the materials.
        whole = paper.render_materials(self.found)
        head = whole[whole.index('## The root'):whole.index('## The elements the proof rests on')]
        self.assertIn(head, digest)
        self.assertIn(UNDERSTANDING.strip(), head)
        self.assertIn('@book{euclid', digest)
        # The record of every element is a file of its own, and the list of the files names each.
        files = paper.record_files(self.found)
        self.assertEqual(sorted(files), sorted(RECORD_FILES[:2] + RECORD_FILES[3:]))
        self.assertIn('**Proof.**\n\nExpand $(k + 1)^2$ by `Small.expand`.', files['elements/Small.sq_step.md'])
        self.assertIn('- `Small.sq_step` · statement · unit · completing the square · `elements/Small.sq_step.md`', files['elements.md'])
        self.assertEqual(files['root.md'].split('\n## The root\n', 1)[1].strip(), head.split('## The root\n', 1)[1].strip())
        # Names that a file system would not tell apart are given different files.
        twins = {'elements': [{'name': name} for name in ('A.b', 'a.B', 'A/b', 'A.b-2')]}
        self.assertEqual(paper.element_files(twins), {'A.b': 'elements/A.b.md', 'a.B': 'elements/a.B-2.md',
                                                      'A/b': 'elements/A_b.md', 'A.b-2': 'elements/A.b-2-2.md'})

    def test_a_section_has_its_own_elements_in_full_and_the_others_by_their_statements(self):
        layout = self.layout
        # The elements the plan puts into each section. The step absorbed into the main theorem is written where
        # that theorem is proved; the statement the paper does not state goes where a proof names it.
        self.assertEqual(layout.own, {'intro': ['Small.oddSum', 'Small.root'],
                                      'tools': ['Small.oddSum_succ', 'Small.oddSum_mono', 'Small.expand', 'Small.sq_step'],
                                      'proof': ['Small.oddSum_succ', 'Small.oddSum_mono_weak', 'Small.root']})
        text, full, cited = self.brief('tools')
        # Own elements: the whole record, in an order in which each comes after what it names.
        self.assertEqual(self.headings(full), layout.own['tools'])
        by_name = {element['name']: element for element in self.found['elements']}
        for position, name in enumerate(self.headings(full)):
            for used in by_name[name]['uses'] + by_name[name]['mentions']:
                if used in self.headings(full):
                    self.assertLess(self.headings(full).index(used), position, (name, used))
        for words in ('**Proof.**\n\nExpand $(k + 1)^2$ by `Small.expand`.', '**Proof.**\n\nThe sum grows by $2n + 1 > 0$',
                      'Euclid, Elements, Book II, Proposition 4. The statement was read; the proof was not.',
                      'This section states it as lemma `lem:square`; its proof follows it.',
                      'This section writes it into lemma `lem:increasing`; it has no number.',
                      'This section cites it in its running text; it has no number.',
                      'This section states it as lemma `lem:square`; its proof follows it. Other sections use it in theorem '
                      '`thm:main` (section `proof`).'):
            self.assertIn(words, full)
        # An element of another section: what it says, where the paper has it, how the paper writes it, its file.
        self.assertEqual(self.headings(cited), ['Small.oddSum'])
        self.assertIn('In the paper: it has no number; it is defined in the running text of section `intro`. The paper '
                      'writes $S_n$ for it: the sum of the first $n$ odd numbers. Full record: `elements/Small.oddSum.md`.', cited)
        self.assertIn('oddSum n + (2 * n + 1)', cited)
        self.assertIn('**Description.** The sum of the first n odd numbers, defined by recursion on n.', cited)
        # The part of the plan that every section needs, and the part of this section.
        for words in ('Title: The sum of the first odd numbers', PLAN['outline'],
                      '2. `tools`, "Preliminaries" (this section): The two lemmas the induction uses.',
                      '- $S_n$: the sum of the first $n$ odd numbers (the object of `Small.oddSum`)',
                      '- theorem `thm:main` · section `intro` · proved in section `proof` · sum of odd numbers · `Small.root`',
                      '- lemma `lem:square` · section `tools` · completing the square · `Small.sq_step`',
                      '- cited in the running text: `Small.expand`'):
            self.assertIn(words, text)

        text, full, cited = self.brief('proof')
        self.assertEqual(self.headings(full), layout.own['proof'])
        # A lemma of another section is used by its statement: the brief has what it says and not how it is proved.
        self.assertEqual(self.headings(cited), ['Small.oddSum', 'Small.oddSum_mono', 'Small.sq_step'])
        lemma = cited[cited.index('### `Small.sq_step`'):]
        self.assertIn('In the paper: lemma `lem:square`, stated in section `tools`. Full record: `elements/Small.sq_step.md`.', lemma)
        self.assertIn('**Statement.** For every natural number $k$, $k^2 + (2k + 1) = (k + 1)^2$.', lemma)
        self.assertNotIn('Expand $(k + 1)^2$ by `Small.expand`.', text)
        self.assertNotIn('**Proof.**', cited)
        # What the paper does not state is given whole where a proof names it, with what stands in its place.
        self.assertIn('The paper does not state it; `Small.oddSum_mono` stands in its place (lemma `lem:increasing`, stated in '
                      'section `tools`).', full)
        self.assertIn('- stated nowhere in the paper: `Small.oddSum_mono_weak`; `Small.oddSum_mono` stands in its place', text)
        self.assertIn('**Proof.**\n\nImmediate from `Small.oddSum_mono`.', full)

        # The introduction states the main result and leaves its proof to a later section. It has in full what the
        # proof of the main result names directly, for the outline of the proof, and meets nothing else through it.
        text, full, cited = self.brief('intro')
        self.assertEqual(self.headings(full), ['Small.oddSum', 'Small.oddSum_succ', 'Small.oddSum_mono_weak', 'Small.sq_step',
                                               'Small.root'])
        self.assertIn('It belongs to another section: lemma `lem:square`, stated in section `tools`. The proof of the main '
                      'result names it directly, and the introduction draws on its explanation.', full)
        self.assertIn('This section writes it into its running text; it has no number.', full)
        self.assertEqual(self.headings(cited), ['Small.oddSum_mono'])
        self.assertEqual({sid: layout.cited[sid] for sid in layout.ids},
                         {'intro': ['Small.oddSum_mono'], 'tools': ['Small.oddSum'],
                          'proof': ['Small.oddSum', 'Small.oddSum_mono', 'Small.sq_step']})

    def test_a_step_that_another_section_absorbs_is_given_in_full_where_a_proof_names_it(self):
        # The plan writes the step into the lemma alone, although the proof of the main theorem names it as well.
        plan = copy.deepcopy(PLAN)
        next(item for item in plan['others'] if item['element'] == 'Small.oddSum_succ')['into'] = ['Small.oddSum_mono']
        self.assertEqual(paper.check_plan(self.found, plan, KEYS), [])
        layout = paper.Layout(self.found, plan)
        self.assertEqual(layout.own['proof'], ['Small.oddSum_mono_weak', 'Small.root'])
        self.assertEqual(layout.full['proof'], ['Small.oddSum_succ', 'Small.oddSum_mono_weak', 'Small.root'])
        text = paper.render_brief(self.found, plan, plan['sections'][2], layout)
        self.assertIn('It belongs to another section: it has no number; it is written with lemma `lem:increasing` (section '
                      '`tools`). This section cannot refer to it by a number; where a proof of this section uses it, its '
                      'content is written at that place.', text)
        self.assertIn('Passing from n to n + 1 adds the odd number 2n + 1.', text)

    def test_the_section_that_a_reader_names_is_understood_in_the_forms_a_reader_gives_it(self):
        for value, part in (('sec:tools', 'tools'), ('tools', 'tools'), (' Sec:Proof ', 'proof'), ('Section 2', 'tools'),
                            (3, 'proof'), ('1', 'intro'), ('Preliminaries', 'tools'), ('proof of the main theorem', 'proof'),
                            ('abstract', 'abstract'), ('Abstract', 'abstract'), ('', None), (None, None), ('sec:nowhere', None),
                            (0, None), (4, None), (True, None), (['sec:tools'], None), ('the title', None)):
            self.assertEqual(paper.named_part(PLAN, value), part, value)


class PassageTests(unittest.TestCase):
    """The passages in which a part differs from the text that was read, and the numbers --open-findings is given."""

    BEFORE = 'One a.\nOne b.\n\nTwo a.\nTwo b.\nTwo c.\n\nThree.\n'
    AFTER = 'One a.\nOne B.\n\nTwo A.\nTwo b.\nTwo C.\n\nThree.\nFour.\n'

    def test_a_passage_does_not_end_inside_a_paragraph_and_is_put_back_by_itself(self):
        # The two changed lines of the second paragraph are one passage; the lines are counted from 0.
        self.assertEqual(paper.changed_passages(self.BEFORE, self.AFTER), [(1, 2, 1, 2), (3, 6, 3, 6), (8, 8, 8, 9)])
        self.assertEqual(paper.changed_passages(self.BEFORE, self.BEFORE), [])
        # Empty lines at the two ends of a part are not lines of the manuscript.
        self.assertEqual(paper.changed_passages(self.BEFORE, '\n' + self.BEFORE + '\n'), [])
        undone = lambda *positions: paper.with_passages_undone(self.BEFORE, self.AFTER, set(positions))
        self.assertEqual(undone(), self.AFTER)
        self.assertEqual(undone(1), 'One a.\nOne B.\n\nTwo a.\nTwo b.\nTwo c.\n\nThree.\nFour.\n')
        self.assertEqual(undone(0, 2), 'One a.\nOne b.\n\nTwo A.\nTwo b.\nTwo C.\n\nThree.\n')
        self.assertEqual(undone(0, 1, 2), self.BEFORE)

    def test_the_numbers_of_the_chosen_findings(self):
        self.assertEqual(paper.chosen_numbers('all', 3), [1, 2, 3])
        self.assertEqual(paper.chosen_numbers('5-7, 2,6', 9), [2, 5, 6, 7])
        for wrong in ('', 'two', '0', '4-2', '10', '1,,2'):
            with self.assertRaises(paper.Stop, msg=wrong):
                paper.chosen_numbers(wrong, 9)


class WritingTests(unittest.TestCase):
    def test_files_written_from_several_threads_at_once_are_whole(self):
        # The writers of the runtime build a file in one buffer shared by the process; this command serialises them.
        import threading
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            texts = {f'{letter}{number}.txt': (letter * 70 + '\n') * 3000 for letter in 'abcdef' for number in range(8)}

            def write(letter):
                for name, text in texts.items():
                    if name.startswith(letter):
                        paper.write_text(folder / name, text)
                        paper.write_json(folder / (name + '.json'), {'text': text})

            threads = [threading.Thread(target=write, args=(letter,)) for letter in 'abcdef']
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()
            for name, text in texts.items():
                self.assertEqual((folder / name).read_text(encoding='utf-8'), text, name)
                self.assertEqual(read_json(folder / (name + '.json')), {'text': text}, name)
            self.assertEqual(len(list(folder.iterdir())), 2 * len(texts))  # no temporary file is left


class SideBySideTests(PaperCase):
    """Sections, repairs and comparisons that run at the same time, and a run that is stopped and continued."""

    def kinds(self, since=0):
        return [(c['kind'], c['section']) for c in self.calls()][since:]

    def together(self, *groups):
        write_json(self.scenario / 'together.json', [list(group) for group in groups])

    def stop(self, script, parallel=1):
        """A run that the script of the sessions brings to a stop; the message it stops with."""
        with self.assertRaises(paper.Stop) as stopped:
            self.run_paper(script, parallel=parallel)
        self.assertEqual(self.events('end')[-1]['status'], 'failed')
        return str(stopped.exception)

    def test_the_sections_after_the_introduction_and_their_repairs_and_comparisons_run_side_by_side(self):
        script = good()
        # Each of the two later sections has a Lean name in it, so each needs a repair of its own.
        script['write:tools'] = [{'output/tools.tex': TOOLS + '% This is \\texttt{Small.oddSum\\_succ}.\n'}]
        script['write:proof'] = [{'output/proof.tex': PROOF + '% See Small.sq_step.\n'}]
        script['repair:machine-tools'] = [{'output/tools.tex': TOOLS}]
        script['repair:machine-proof'] = [{'output/proof.tex': PROOF}]
        # Every session of a pair waits until the other has started, which only sessions side by side can do.
        self.together(('write:tools', 'write:proof'), ('repair:machine-tools', 'repair:machine-proof'),
                      ('compare:intro', 'compare:tools'))
        self.assertEqual(self.run_paper(script, parallel=2), 0)
        calls = self.calls()
        pairs = [c for c in calls if c['met'] is not None]
        self.assertEqual(sorted((c['kind'], c['section']) for c in pairs),
                         [('compare', 'intro'), ('compare', 'tools'), ('repair', 'machine-proof'), ('repair', 'machine-tools'),
                          ('write', 'proof'), ('write', 'tools')])
        self.assertTrue(all(c['met'] for c in pairs))
        # The introduction is written before them, alone, and both have it and not each other.
        self.assertEqual(self.kinds()[:2], [('plan', None), ('write', 'intro')])
        self.assertEqual(sorted(self.kinds()[2:4]), [('write', 'proof'), ('write', 'tools')])
        for call in self.calls('write')[1:]:
            parts = sorted(name for name in call['given'] if name.startswith('parts/'))
            self.assertEqual(parts, ['parts/abstract.tex', 'parts/intro.tex'])
            self.assertIn('`parts/` holds the parts that were finished when this session started, as the paper carries '
                          'them unless a repair changes them: `parts/intro.tex` with `parts/abstract.tex` (the introduction '
                          'and the abstract). The other sections are written while this session runs or after it, and you '
                          'do not see them', call['prompt'])
            self.assertIn(f"`eq:{call['section']}-`", call['prompt'])
            self.assertIn('Refer to another section as `Section~\\ref{sec:<id>}`', call['prompt'])
        first = self.calls('write')[0]
        self.assertIn('No section was finished when this session started, so this folder has no `parts/`.', first['prompt'])
        self.assertIn('The introduction, which is this section, is written first and alone', first['prompt'])
        self.assertIn('The introduction is written from it: read it in full.', first['prompt'])
        # The sessions share the numbering of their folders and the log: no number is given twice, none is lost.
        folders = sorted(c['folder'] for c in calls)
        self.assertEqual([folder[:2] for folder in folders], [f'{number:02d}' for number in range(1, len(calls) + 1)])
        self.assertEqual(sorted(e['folder'] for e in self.events('session')), [f'sessions/{folder}' for folder in folders])
        # Each repair had its own section to change, and the manuscript came out whole.
        repair = self.events('repair')[0]
        self.assertEqual((repair['of'], repair['changed']), ('machine', ['proof', 'tools']))
        self.assertEqual(repair['sessions'], [{'section': 'tools', 'findings': [1], 'changed': ['tools']},
                                              {'section': 'proof', 'findings': [2], 'changed': ['proof']}])
        for name, text in PARTS.items():
            self.assertEqual((self.out / 'parts' / (name + '.tex')).read_text(encoding='utf-8'), text)
        rows = read_json(self.out / 'correspondence.json')['statements']
        self.assertEqual([r['comparison']['verdict'] for r in rows], ['same'] * 3)
        self.assertEqual(self.events('materials')[0]['parallel'], 2)

    def test_a_run_stopped_between_sections_keeps_what_was_written_and_is_continued(self):
        script = good()
        script['write:tools'] = [{}]  # the session of one section leaves nothing, twice
        self.together(('write:tools', 'write:proof'))
        message = self.stop(script, parallel=2)
        self.assertIn('no write session left output the script can use, in 2 attempts: output/tools.tex was not written', message)
        # The section that was being written beside it came to its end and is kept.
        self.assertEqual(sorted(path.name for path in (self.out / 'parts').iterdir()), ['abstract.tex', 'intro.tex', 'proof.tex'])
        self.assertTrue(next(c for c in self.calls('write') if c['section'] == 'proof')['met'])
        self.assertFalse((self.out / 'paper.tex').exists())
        launched = len(self.calls())
        # A new run does not write over the folder; a dry run of the continuation says what is left to do.
        with self.assertRaises(paper.Stop):
            self.run_paper(good())
        before = sorted((path.relative_to(self.out).as_posix(), path.stat().st_mtime_ns) for path in self.out.rglob('*'))
        with patch('paper.worker_command', side_effect=self.command), patch('builtins.print') as shown:
            self.assertEqual(paper.main([str(self.instance), '--out', str(self.out), '--resume', '--dry-run', '--tex', *TEX]), 0)
        said = shown.call_args.args[0]
        self.assertIn('Dry run: no session is launched and nothing is written.', said)
        self.assertIn('The materials of the canon are those of materials.json: 7 elements.', said)
        self.assertIn('Parts that are written: abstract, intro, proof.', said)
        self.assertIn('Sections that are still to be written, up to 4 at a time: tools.', said)
        self.assertRegex(said, r'\n  tools +\d+ +4 +1 +\d+ +\d+ +\d+')
        self.assertEqual(before, sorted((path.relative_to(self.out).as_posix(), path.stat().st_mtime_ns)
                                        for path in self.out.rglob('*')))
        self.assertEqual(len(self.calls()), launched)
        # The continuation writes the section that is missing, with the parts that are there, and goes on to the end.
        self.assertEqual(self.run_paper(good(), resume=True), 0)
        self.assertEqual(self.kinds(launched), [('write', 'tools'), ('read', None), ('likeness', None), ('likeness', None),
                                                *COMPARED, *COVERED])
        again = self.calls()[launched]
        self.assertEqual(sorted(name for name in again['given'] if name.startswith('parts/')),
                         ['parts/abstract.tex', 'parts/intro.tex', 'parts/proof.tex'])
        self.assertIn('`parts/intro.tex` with `parts/abstract.tex` (the introduction and the abstract), `parts/proof.tex` '
                      '(Section 3, "Proof of the main theorem"). Consult them', again['prompt'])
        self.assertEqual(again['folder'][:2], f'{launched + 1:02d}')
        resumed = self.events('resume')[0]
        self.assertEqual((resumed['plan'], sorted(resumed['parts']), resumed['done']), (True, ['abstract', 'intro', 'proof'], {}))
        self.assertEqual([e['status'] for e in self.events('end')], ['failed', 'complete'])
        self.assertTrue((self.out / 'paper.pdf').is_file())
        for name, text in PARTS.items():
            self.assertEqual((self.out / 'parts' / (name + '.tex')).read_text(encoding='utf-8'), text)
        # A run that came to its end has nothing to continue.
        with self.assertRaisesRegex(paper.Stop, 'came to its end \\(complete\\); there is nothing to continue'):
            self.run_paper(good(), resume=True)
        self.assertEqual(self.run_paper(good(), only=True), 0)

    def test_a_run_is_not_continued_when_the_canon_or_the_plan_is_no_longer_what_it_was(self):
        script = good()
        script['write:tools'] = [{}]
        self.stop(script)
        launched = len(self.calls())
        # The materials are taken from the canon again and compared with those the run began with.
        materials = read_json(self.out / 'materials.json')
        kept = copy.deepcopy(materials)
        materials['elements'][5]['proof'] = 'Another proof.'
        materials['elements'].pop(0)
        write_json(self.out / 'materials.json', materials)
        with self.assertRaises(paper.Stop) as stopped:
            self.run_paper(good(), resume=True)
        for words in ('the canon has changed since the run began', 'new elements: Small.oddSum',
                      'elements whose record or standing changed: Small.sq_step'):
            self.assertIn(words, str(stopped.exception))
        # The revision alone says nothing about what the proof rests on.
        write_json(self.out / 'materials.json', {**kept, 'revision': kept['revision'] - 1})
        self.assertEqual(paper.changed_materials(read_json(self.out / 'materials.json'), self.materials()), [])
        # A plan that does not pass the check, with parts written from it, is not a run that can go on.
        plan = read_json(self.out / 'plan.json')
        plan['sections'][1].pop('exemplars')
        write_json(self.out / 'plan.json', plan)
        with self.assertRaises(paper.Stop) as stopped:
            self.run_paper(good(), resume=True)
        self.assertIn('does not pass the check of the plan, and parts were written from it', str(stopped.exception))
        self.assertIn("section 'tools': \"exemplars\" names 2 different papers", str(stopped.exception))
        self.assertEqual(len(self.calls()), launched)
        # A folder that holds no run is not continued either.
        with self.assertRaisesRegex(paper.Stop, 'holds no run of this command to continue'):
            paper.produce(self.instance, self.root / 'elsewhere', TEX, resume=True)

    def continued(self, script, after, code=0, again=None):
        """Stop a run with `script`, continue it with the sessions that do their work, and compare what was launched then."""
        self.stop(script)
        launched = len(self.calls())
        state = read_json(self.out / 'state.json') if (self.out / 'state.json').is_file() else None
        self.assertEqual(self.run_paper(again or good(), resume=True), code)
        self.assertEqual(self.kinds(launched), after)
        return state

    def test_a_run_stopped_while_the_paper_is_planned_is_continued_with_the_plan(self):
        script = good()
        script['plan'] = [{}]
        self.assertIsNone(self.continued(script, [('plan', None), ('write', 'intro'), ('write', 'tools'), ('write', 'proof'),
                                                  ('read', None), ('likeness', None), ('likeness', None), *COMPARED, *COVERED]))
        self.assertEqual(len(self.calls('plan')), paper.PLAN_ATTEMPTS + 1)
        self.assertEqual(read_json(self.out / 'plan.json'), PLAN)

    def test_a_run_stopped_while_the_manuscript_is_settled_is_continued_with_the_repair(self):
        script = good()
        script['write:proof'] = [{'output/proof.tex': PROOF + '\\undefinedmacro\n'}]
        script['repair:typeset'] = [{}]
        again = good()
        again['repair:typeset'] = [{'output/proof.tex': PROOF}]
        state = self.continued(script, [('repair', 'typeset'), ('read', None), ('likeness', None), ('likeness', None), *COMPARED,
                                        *COVERED], again=again)
        self.assertIsNone(state)  # no stage after the writing had been reached
        self.assertEqual(len(self.calls('write')), 3)

    def test_a_run_stopped_in_the_first_reading_is_continued_with_that_reading(self):
        script = good()
        script['read'] = [{}]
        state = self.continued(script, [('read', None), ('likeness', None), ('likeness', None), *COMPARED, *COVERED])
        self.assertEqual((state['done'], state['open']), ({}, []))
        self.assertEqual((len(self.calls('plan')), len(self.calls('write'))), (1, 3))
        # The readings are counted over the run and its continuation.
        self.assertEqual([e['round'] for e in self.events('reading')], [2])

    def test_a_run_stopped_in_the_readings_beside_real_papers_makes_them_again_and_not_the_reading_before(self):
        script = good()
        # The first of these readings finds a departure, which is repaired; the second leaves nothing.
        script['likeness'] = [{'output/likeness.json': json.dumps(departed('The abstract says more than theirs.'))}, {}]
        script['repair:likeness'] = [{'output/intro.tex': INTRO + 'Version 0 of the introduction.\n',
                                      'output/response.json': answered('The opening is rewritten.')}]
        # The continuation finds no departure. The repair of the stopped run had rewritten the introduction, which
        # the state recorded when it happened, so the manuscript is read by itself again all the same.
        state = self.continued(script, [('likeness', None), ('likeness', None), ('read', None), *COMPARED, *COVERED])
        self.assertEqual((state['done'], state['rewritten']), ({'reading': True}, True))
        self.assertEqual(len(self.calls('read')), 2)
        reread = self.calls('read')[-1]
        self.assertIn('Version 0 of the introduction.', (self.folder(reread) / 'paper.tex').read_text(encoding='utf-8'))
        final = read_json(self.out / 'state.json')
        self.assertEqual((final['done'], final['rewritten']),
                         ({'reading': True, 'likeness': True, 'rereading': True, 'comparison': True, 'resolve': True,
                           'coverage': True}, False))
        self.assertEqual(self.events('end')[-1], {**self.events('end')[-1], 'status': 'complete', 'open': []})

    def test_a_run_stopped_in_the_reading_after_those_readings_is_continued_with_it(self):
        script = good()
        script['likeness'] = [{'output/likeness.json': json.dumps(departed('The abstract says more than theirs.'))},
                              {'output/likeness.json': json.dumps(LIKE)}]
        script['repair:likeness'] = [{'output/intro.tex': INTRO + 'Version 0 of the introduction.\n',
                                      'output/response.json': answered('The opening is rewritten.')}]
        script['read'] = [{'output/reading.json': json.dumps(CLEAN)}, {}]
        state = self.continued(script, [('read', None), *COMPARED, *COVERED])
        self.assertEqual((state['done'], state['rewritten']), ({'reading': True, 'likeness': True}, True))
        self.assertEqual(len(self.calls('likeness')), 3)

    def test_a_run_stopped_in_the_comparison_is_continued_with_the_comparison_of_every_section(self):
        script = good()
        script['compare:tools'] = [{}]
        state = self.continued(script, COMPARED + COVERED)
        self.assertEqual(state['done'], {'reading': True, 'likeness': True, 'rereading': True})
        rows = read_json(self.out / 'correspondence.json')['statements']
        self.assertEqual([r['comparison']['verdict'] for r in rows], ['same'] * 3)

    def test_a_run_stopped_after_a_repair_of_a_statement_reads_the_manuscript_before_it_compares_again(self):
        script = good()
        differs = [dict(row) for row in SAME]
        differs[2].update(verdict='differs', difference='The manuscript has k^2 + 2k = (k + 1)^2.')
        script['write:tools'] = [{'output/tools.tex': TOOLS.replace('k^2 + (2k + 1)', 'k^2 + 2k')}]
        script['compare:tools'] = [{'output/comparison.json': json.dumps(differs[1:])}]
        script['repair:comparison'] = [{'output/tools.tex': TOOLS, 'output/response.json': answered('The term 1 is restored.')}]
        script['read'] = [{'output/reading.json': json.dumps(CLEAN)}, {}]  # the reading after the repair leaves nothing
        state = self.continued(script, [('read', None), *COMPARED, *COVERED])
        self.assertEqual((state['done'], state['rewritten']), ({'reading': True, 'likeness': True, 'rereading': True}, True))
        self.assertEqual((self.out / 'parts/tools.tex').read_text(encoding='utf-8'), TOOLS)
        rows = read_json(self.out / 'correspondence.json')['statements']
        self.assertEqual([r['comparison']['verdict'] for r in rows], ['same'] * 3)
        self.assertEqual(self.events('end')[-1], {**self.events('end')[-1], 'status': 'complete', 'open': []})

    def test_a_run_stopped_in_the_repair_after_the_last_reading_makes_that_repair_again_and_not_the_readings(self):
        script = good()
        script['read'] = [{'output/reading.json': json.dumps({**CLEAN, 'findings': [EXPANSION, BASE]})}]
        script['repair:narrow-reading-tools'] = [{'output/tools.tex': TOOLS_BOTH, 'output/response.json': answers('revised')}]
        script['repair:narrow-reading-proof'] = [{}]  # the session of the other section leaves nothing, twice
        again = good()
        again['repair:narrow-reading-tools'] = script['repair:narrow-reading-tools']
        again['repair:narrow-reading-proof'] = [{'output/proof.tex': PROOF_BASED, 'output/response.json': answers('revised')}]
        again['changes'] = [{'output/verdicts.json': verdicts(
            [(True, [1], 'Read.'), (True, [1], 'Read.'), (True, [2], 'Read.')], [(1, True, ''), (2, True, '')])}]
        with patch('paper.READING_ROUNDS', 1):
            self.stop(script)
            launched = len(self.calls())
            # The state says that the repair is under way, with the findings it takes up, and <out>/narrow keeps the
            # parts as the reader read them; the section whose session came to its end is changed already.
            state = read_json(self.out / 'state.json')
            self.assertEqual((state['done'], state['narrow']['step'], [f['number'] for f in state['narrow']['findings']],
                              [f['finding'] for f in state['narrow']['findings']]), ({}, 'repair', [1, 2], [EXPANSION, BASE]))
            self.assertEqual(state['open'], [{'check': paper.READING, 'after_repairs': 0, 'problems': [EXPANSION, BASE]}])
            self.assertEqual((self.part('tools'), (self.out / 'narrow/before/tools.tex').read_text(encoding='utf-8')),
                             (TOOLS_BOTH, TOOLS))
            code, said = self.said(['--resume', '--dry-run', '--tex', *TEX])
            self.assertEqual(code, 0)
            self.assertIn('The run was stopped in the last repair of 2 findings, at the step "repair"', said)
            self.assertEqual(len(self.calls()), launched)
            self.assertEqual(self.run_paper(again, resume=True), 0)
        # The repair is made again from the text that was read, by the sessions of both sections, and is followed by
        # the reading of the changes. The manuscript is not read by itself again.
        self.assertEqual(self.kinds(launched), [('repair', 'narrow-reading-tools'), ('repair', 'narrow-reading-proof'),
                                                ('changes', None), ('likeness', None), ('likeness', None), *COMPARED, *COVERED])
        tools = self.calls()[launched]
        self.assertEqual((self.folder(tools) / 'parts/tools.tex').read_text(encoding='utf-8'), TOOLS)
        self.assertEqual((self.part('tools'), self.part('proof')), (TOOLS_BOTH, PROOF_BASED))
        self.assertEqual([e['round'] for e in self.events('reading')], [1])
        final = read_json(self.out / 'state.json')
        self.assertEqual((final['done'], final['narrow'], final['open']),
                         ({'reading': True, 'likeness': True, 'rereading': True, 'comparison': True, 'resolve': True,
                           'coverage': True}, None, []))
        self.assertEqual([e['status'] for e in self.events('end')], ['failed', 'complete'])
        self.assertFalse((self.out / 'narrow').exists())

    def test_a_run_stopped_in_the_reading_of_the_changes_is_continued_with_that_reading(self):
        script = good()
        script['likeness'] = [{'output/likeness.json': json.dumps(departed('The abstract says more than theirs.'))}]
        script['repair:narrow'] = [{'output/abstract.tex': 'The sum of the first $n$ odd numbers is $n^2$.\n',
                                    'output/response.json': answered('The abstract is shortened.')}]
        script['changes'] = [{}]
        again = good()
        again['changes'] = [{'output/verdicts.json': verdicts([(False, [1], 'The abstract no longer says what $n$ is.')],
                                                              [(1, True, '')])}]
        again['resolve'] = keeps(1)
        with patch('paper.LIKENESS_ROUNDS', 1):
            message = self.stop(script)
            self.assertIn('no changes session left output the script can use', message)
            launched = len(self.calls())
            state = read_json(self.out / 'state.json')
            self.assertEqual((state['done'], state['narrow']['step'], state['narrow']['response']),
                             ({'reading': True}, 'read', [{'finding': 1, 'action': 'revised', 'note': 'The abstract is shortened.'}]))
            self.assertEqual(self.run_paper(again, resume=True), 0)
        # Neither the readings beside real papers nor the repair are made again.
        self.assertEqual(self.kinds(launched), [('changes', None), *COMPARED, ('resolve', None), *COVERED])
        self.assertEqual(len(self.calls('likeness')), 1)
        self.assertEqual(self.part('abstract'), ABSTRACT)
        self.assertEqual(self.events('end')[-1]['kept'], kept_by_resolve(paper.LIKENESS, {
            **departure('The abstract says more than theirs.'),
            'open_because': paper.UNDONE + 'The abstract no longer says what $n$ is.'}))
        self.assertIn(ABSTRACT.strip(), (self.out / 'paper.tex').read_text(encoding='utf-8'))

    def test_what_a_reader_finds_goes_to_the_sections_it_names_and_the_rest_to_one_session_after_them(self):
        script = good()
        first = {**CLEAN, 'findings': [
            {'where': 'Lemma 2.2', 'section': 'sec:tools', 'quote': 'Expand the right-hand side.', 'problem': 'Not carried out.'},
            {'where': 'the title', 'section': '', 'quote': '', 'problem': 'The title names no result.'},
            {'where': 'the abstract', 'section': 'abstract', 'quote': ABSTRACT_QUOTE, 'problem': 'The range of n is missing.'},
            {'where': 'Lemma 2.1', 'section': 'Section 2', 'quote': 'exceeds', 'problem': 'By how much is not derived.'}]}
        second = {**CLEAN, 'findings': [{'where': 'the proof', 'section': 'sec:proof', 'quote': 'By induction on $n$.',
                                         'problem': 'The base case is not named.'}]}
        script['read'] = [{'output/reading.json': json.dumps(report)} for report in (first, second, CLEAN)]
        answers = lambda *actions: json.dumps([{'finding': number, 'action': action, 'note': f'{action} {number}'}
                                              for number, action in enumerate(actions, 1)])
        script['repair:reading-intro'] = [{'output/abstract.tex': ABSTRACT + 'Here $n$ is a natural number.\n',
                                           'output/response.json': answers('revised')}]
        script['repair:reading-tools'] = [{'output/tools.tex': TOOLS.replace('Expand the right-hand side.', 'Expand, written out.'),
                                           'output/proof.tex': 'A session of one section does not change another.\n',
                                           'output/response.json': answers('revised', 'kept')}]
        script['repair:reading-proof'] = [{'output/proof.tex': PROOF.replace('By induction on $n$.', 'By induction on $n$ from $0$.'),
                                           'output/response.json': answers('revised')}]
        script['repair:reading'] = [{'output/response.json': answers('kept')}, {'output/response.json': '[]'}]
        self.assertEqual(self.run_paper(script), 0)
        self.assertEqual(self.kinds(4), [
            ('read', None), ('repair', 'reading-intro'), ('repair', 'reading-tools'), ('repair', 'reading'),
            ('read', None), ('repair', 'reading-proof'), ('repair', 'reading'),
            ('read', None), ('likeness', None), ('likeness', None), *COMPARED, *COVERED])
        intro, tools, whole, proof, last = self.calls('repair')
        found = lambda call: read_json(self.folder(call) / 'findings.json')
        # Each session of a section has the findings of that section, in the order of the report, and what the reader
        # understood; the abstract goes with the introduction.
        self.assertEqual([f['where'] for f in found(intro)['findings']], ['the abstract'])
        self.assertEqual([f['where'] for f in found(tools)['findings']], ['Lemma 2.2', 'Lemma 2.1'])
        self.assertEqual(found(tools)['understanding'], CLEAN['understanding'])
        # It has the brief and the papers of its section and may change that section only.
        self.assertTrue({'brief.md', 'paper.tex', 'parts/tools.tex', 'study.md', *RECORD_FILES} <= set(tools['given']))
        self.assertEqual(sorted(name for name in tools['given'] if name.startswith('parts/')), ['parts/tools.tex'])
        self.assertEqual(sorted(name for name in intro['given'] if name.startswith('parts/')),
                         ['parts/abstract.tex', 'parts/intro.tex'])
        self.assertEqual((self.given(intro), self.given(tools)), (['alpha', 'beta'], ['delta', 'gamma']))
        self.assertEqual((self.folder(tools) / 'brief.md').read_text(encoding='utf-8'),
                         paper.render_brief(self.materials(), PLAN, PLAN['sections'][1]))
        self.assertIn('this session changes this section and no other', tools['prompt'])
        self.assertIn('are `parts/tools.tex`', tools['prompt'])
        self.assertIn('Write the complete new text of the part as `output/tools.tex`', tools['prompt'])
        self.assertIn('as `output/intro.tex` and `output/abstract.tex`', intro['prompt'])
        self.assertIn('another session compares that understanding with the research', tools['prompt'])
        self.assertEqual((self.out / 'parts/proof.tex').read_text(encoding='utf-8'),
                         PROOF.replace('By induction on $n$.', 'By induction on $n$ from $0$.'))
        # What names no section goes to one session after the others, with the manuscript as they left it. That
        # session also compares what the reader understood with the research, so it follows every such reading.
        self.assertEqual([f['where'] for f in found(whole)['findings']], ['the title'])
        tex = (self.folder(whole) / 'paper.tex').read_text(encoding='utf-8')
        self.assertIn('Here $n$ is a natural number.', tex)
        self.assertIn('Expand, written out.', tex)
        self.assertTrue({'plan.json', 'parts/intro.tex', 'parts/tools.tex', 'parts/proof.tex', *RECORD_FILES} <= set(whole['given']))
        self.assertNotIn('brief.md', whole['given'])
        self.assertIn('First compare the understanding with the research', whole['prompt'])
        self.assertEqual(found(last), {'understanding': CLEAN['understanding'], 'findings': []})
        self.assertIn('an empty array when there is no finding', last['prompt'])
        # The log has one repair for each reading, with the answers in the order of the findings as they were reported.
        one, two = self.events('repair')
        self.assertEqual([(r['finding'], r['action'], r['note']) for r in one['response']],
                         [(1, 'revised', 'revised 1'), (2, 'kept', 'kept 1'), (3, 'revised', 'revised 1'), (4, 'kept', 'kept 2')])
        self.assertEqual(one['sessions'], [{'section': 'intro', 'findings': [3], 'changed': ['abstract']},
                                           {'section': 'tools', 'findings': [1, 4], 'changed': ['tools']},
                                           {'section': None, 'findings': [2], 'changed': []}])
        self.assertEqual((one['changed'], two['changed']), (['abstract', 'tools'], ['proof']))
        self.assertEqual(two['sessions'], [{'section': 'proof', 'findings': [1], 'changed': ['proof']},
                                           {'section': None, 'findings': [], 'changed': []}])
        # The readers are asked for the section of each place.
        for call in self.calls('read') + self.calls('likeness'):
            self.assertIn('"section" says where the place lies', call['prompt'])

    def test_a_departure_that_names_a_section_is_repaired_by_the_session_of_that_section(self):
        script = good()
        named = {**departure('The lemma is announced by no sentence.'), 'where': 'Lemma 2.2', 'section': 'sec:tools',
                 'quote': 'Expand the right-hand side.'}
        script['likeness'] = [{'output/likeness.json': json.dumps({**LIKE, 'departures': [named]})},
                              {'output/likeness.json': json.dumps(LIKE)}]
        script['repair:likeness-tools'] = [{'output/tools.tex': TOOLS.replace('Expand the right-hand side.', 'We expand.'),
                                            'output/response.json': answered('A sentence was added.')}]
        self.assertEqual(self.run_paper(script), 0)
        self.assertEqual(self.kinds(5), [('likeness', None), ('repair', 'likeness-tools'), ('likeness', None), ('likeness', None),
                                         ('read', None), *COMPARED, *COVERED])
        repair = self.calls('repair')[0]
        self.assertEqual(read_json(self.folder(repair) / 'findings.json'), [named])
        self.assertIn('Rewrite this section so that at each of these places the manuscript does what the papers do', repair['prompt'])
        self.assertEqual(self.given(repair), ['delta', 'gamma'])
        self.assertIn('read `study.md` and read the papers in `exemplars/` whole', repair['prompt'])

    def test_the_statements_of_a_section_are_compared_with_the_records_of_their_elements(self):
        script = good()
        differs = [dict(row) for row in SAME]
        differs[2].update(verdict='differs', difference='The manuscript has k^2 + 2k = (k + 1)^2.')
        script['write:tools'] = [{'output/tools.tex': TOOLS.replace('k^2 + (2k + 1)', 'k^2 + 2k')}]
        # The first session for the section answers for the statements of the whole paper, which is not its task.
        script['compare:tools'] = [{'output/comparison.json': json.dumps(differs)},
                                   {'output/comparison.json': json.dumps(differs[1:])},
                                   {'output/comparison.json': json.dumps(SAME[1:])}]
        script['repair:comparison-tools'] = [{'output/tools.tex': TOOLS, 'output/response.json': answered('The term 1 is restored.')}]
        self.assertEqual(self.run_paper(script), 0)
        self.assertEqual(self.kinds(7), [('compare', 'intro'), ('compare', 'tools'), ('compare', 'tools'),
                                         ('repair', 'comparison-tools'), ('read', None), *COMPARED, *COVERED])
        intro, tools, again = self.calls('compare')[:3]
        self.assertIn('one object for each entry of statements.json, in their order', again['prompt'])
        # A session has the statements of its section, the records of their elements in full, and what those mention.
        self.assertEqual(tools['given'], sorted(['paper-method.md', 'paper.tex', 'prompt.txt', 'records.md', 'session.json',
                                                 'statements.json', 'elements.md'] + RECORD_FILES[3:]))
        statements = read_json(self.folder(tools) / 'statements.json')
        self.assertEqual([s['label'] for s in statements], ['lem:increasing', 'lem:square'])
        self.assertEqual([s['label'] for s in read_json(self.folder(intro) / 'statements.json')], ['thm:main'])
        self.assertIn('k^2 + 2k = (k + 1)^2', statements[1]['paper_statement'])
        self.assertIn('k^2 + (2k + 1) = (k + 1)^2', statements[1]['record_statement'])
        records = (self.folder(tools) / 'records.md').read_text(encoding='utf-8')
        stated, mentioned = records.split('\n## What their statements mention\n')
        self.assertEqual([line for line in stated.splitlines() if line.startswith('### ')],
                         ['### `Small.oddSum_mono`', '### `Small.sq_step`'])
        self.assertIn('**Proof.**\n\nExpand $(k + 1)^2$ by `Small.expand`.', stated)
        self.assertIn('### `Small.oddSum`', mentioned)
        self.assertIn('The paper writes $S_n$ for it: the sum of the first $n$ odd numbers.', mentioned)
        self.assertIn('compares the numbered statements of one section of the manuscript, "Preliminaries"', tools['prompt'])
        self.assertRegex(tools['prompt'], r'Its lines \d+ to \d+ are this section\.')
        # The statement that differs is corrected by the session of its section, which has the brief of the section.
        repair = self.calls('repair')[0]
        self.assertEqual(read_json(self.folder(repair) / 'findings.json'), [{'label': 'lem:square', 'difference': differs[2]['difference']}])
        self.assertTrue({'brief.md', 'parts/tools.tex'} <= set(repair['given']))
        self.assertIn('adjust its proof and the places of this section that use it', repair['prompt'])
        self.assertEqual(self.events('repair')[0]['sessions'], [{'section': 'tools', 'findings': [1], 'changed': ['tools']}])
        self.assertEqual([len(e['differing']) for e in self.events('comparison')], [1, 0])

    def test_a_dry_run_of_a_new_paper_launches_nothing_and_writes_nothing(self):
        write_json(self.scenario / 'script.json', good())
        (self.exemplars / 'gamma.tex').unlink()
        with patch('paper.worker_command', side_effect=self.command), patch('builtins.print') as shown:
            self.assertEqual(paper.main([str(self.instance), '--out', str(self.out), '--dry-run', '--tex', *TEX]), 0)
        said = shown.call_args.args[0]
        for words in ('Dry run: no session is launched and nothing is written.',
                      'Papers of the collection that are missing or differ from its manifest, which a run would fetch: gamma.',
                      'The materials: 7 elements that the formal proof of the root rests on.',
                      'The next session plans the paper. It would be given, in bytes:',
                      'materials-digest.md, which it reads in full',
                      'elements/, 7 records, which it opens as a decision needs them'):
            self.assertIn(words, said)
        self.assertFalse(self.out.exists())
        self.assertFalse((self.scenario / 'calls.json').exists())
        self.assertFalse((self.exemplars / 'runs.txt').exists())
        # The options that do not go together are refused.
        with patch('builtins.print') as shown:
            self.assertEqual(paper.main([str(self.instance), '--out', str(self.out), '--typeset-only', '--resume']), 1)
            self.assertEqual(paper.main([str(self.instance), '--out', str(self.out), '--parallel', '0']), 1)
        self.assertIn('--parallel is the number of sessions that run side by side, at least 1', shown.call_args.args[0])


class OpenFindingsTests(PaperCase):
    """A run that came to its end with findings left open, taken up again with --open-findings.

    The run of these tests is one that the command made before it had the stages `resolve` and `coverage`: it
    ends after the comparison of the statements, so the findings of its reading are in its open list. The
    option still acts on such findings, and after a pass it compares the running text of the sections that the
    pass changed."""

    DIFFERENCE = 'The manuscript has k^2 + 2k = (k + 1)^2.'
    OFF = TOOLS.replace('k^2 + (2k + 1)', 'k^2 + 2k')  # the section `tools` with a statement that differs from its element

    def kinds(self, since=0):
        return [(c['kind'], c['section']) for c in self.calls()][since:]

    def leave_open(self, comparison=True):
        """A run that ends with two findings of its one reading kept by the repair, and, with `comparison`, with a
        statement that differs from its element after the bounded comparisons; the number of sessions it launched."""
        script = good()
        script['read'] = [{'output/reading.json': json.dumps({**CLEAN, 'findings': [EXPANSION, BASE]})}]
        script['repair:narrow'] = [{'output/response.json': json.dumps(
            [{'finding': 1, 'action': 'kept', 'note': 'The reader is expected to expand a square.'}])}]
        if comparison:
            differs = [dict(row) for row in SAME]
            differs[2].update(verdict='differs', difference=self.DIFFERENCE)
            script['write:tools'] = [{'output/tools.tex': self.OFF}]
            script['compare:tools'] = [{'output/comparison.json': json.dumps(differs[1:])}]
            script['repair:comparison'] = [{'output/response.json': json.dumps(
                [{'finding': 1, 'action': 'kept', 'note': 'The statement is that of the record.'}])}]
        with patch('paper.READING_ROUNDS', 1), patch('paper.STAGES', paper.STAGES[:4]):
            self.assertEqual(self.run_paper(script), 2)
        self.kept = paper.KEPT + 'The reader is expected to expand a square.'
        self.left = [{'check': paper.READING, 'after_repairs': 1,
                      'problems': [{**EXPANSION, 'open_because': self.kept}, {**BASE, 'open_because': self.kept}]}]
        if comparison:
            self.left.append({'check': paper.COMPARISON, 'after_repairs': paper.COMPARISON_ROUNDS - 1,
                              'problems': [{'label': 'lem:square', 'difference': self.DIFFERENCE}]})
        self.assertEqual(self.events('end')[-1]['open'], self.left)
        return len(self.calls())

    def tree(self):
        return sorted((path.relative_to(self.out).as_posix(), path.stat().st_mtime_ns) for path in self.out.rglob('*'))

    def test_the_open_findings_of_a_finished_run_are_listed_and_the_chosen_ones_are_acted_on(self):
        launched = self.leave_open()
        # The dry run lists the open findings with their numbers, the check each comes from and the place it points
        # to. It launches nothing and writes nothing.
        before = self.tree()
        code, said = self.said(['--open-findings', '--dry-run', '--tex', *TEX])
        self.assertEqual(code, 0)
        for words in ('Dry run: no session is launched and nothing is written.',
                      'came to its end (open_findings) with 3 findings left open',
                      'as in --open-findings 2,5-7',
                      f'{paper.READING}: 2 open after 1 repairs.',
                      '    1. Lemma 2.2 [part tools]', '       quote: Expand the right-hand side.',
                      '       problem: The expansion is not carried out.', '       open because: ' + self.kept,
                      '    2. the proof [part proof]',
                      f'{paper.COMPARISON}: 1 open after 1 repairs.',
                      '    3. the statement with \\label{lem:square}', '       difference: ' + self.DIFFERENCE):
            self.assertIn(words, said)
        self.assertEqual((self.tree(), len(self.calls())), (before, launched))
        # Acting on the first finding alone: the session of its section repairs it narrowly, and a session reads the change.
        script = good()
        script['repair:narrow-reading-tools'] = [{'output/tools.tex': self.OFF.replace('Expand the right-hand side.', EXPANDED),
                                                  'output/response.json': answers('revised')}]
        script['changes'] = [{'output/verdicts.json': verdicts([(True, [1], 'Read with the proof of Lemma 2.2.')], [(1, True, '')])}]
        self.assertEqual(self.run_paper(script, open_findings='1'), 2)
        # The pass changed the section `tools`, so its running text is compared with the elements afterwards.
        self.assertEqual(self.kinds(launched), [('repair', 'narrow-reading-tools'), ('changes', None), ('cover', 'tools')])
        repair = self.calls()[launched]
        self.assertEqual(read_json(self.folder(repair) / 'findings.json'),
                         {'understanding': CLEAN['understanding'], 'findings': [{**EXPANSION, 'open_because': self.kept}]})
        self.assertIn('So this repair is narrow.', repair['prompt'])
        self.assertIn('A finding that carries "open_because" was taken up before and left open', repair['prompt'])
        self.assertIn(EXPANDED, self.part('tools'))
        # The findings that were not chosen are open as they were; the one that was acted on is closed.
        end = self.events('end')[-1]
        self.assertEqual((end['status'], end['open']), ('open_findings', [
            {'check': paper.READING, 'after_repairs': 2, 'problems': [{**BASE, 'open_because': self.kept}]}, self.left[1]]))
        self.assertEqual(self.events('open findings')[0], {**self.events('open findings')[0], 'chosen': [1], 'listed': 3})
        # No statement changed, so none was compared; the one that differs still does.
        self.assertEqual(len(self.events('comparison')), paper.COMPARISON_ROUNDS)
        self.assertEqual(read_json(self.out / 'state.json')['narrow'], None)
        launched = len(self.calls())
        # Acting on all that is left: the finding of the reader in the section `proof`, and the statement that differs,
        # which the session of its section corrects. The changes are read, and the changed statement is compared.
        script = good()
        script['repair:narrow-reading-proof'] = [{'output/proof.tex': PROOF_BASED, 'output/response.json': answers('revised')}]
        script['repair:narrow-comparison-tools'] = [{'output/tools.tex': TOOLS.replace('Expand the right-hand side.', EXPANDED),
                                                     'output/response.json': answers('revised')}]
        script['changes'] = [{'output/verdicts.json': verdicts(
            [(True, [2], 'Read with the proof of Lemma 2.2.'), (True, [1], 'Read with the proof.')], [(1, True, ''), (2, True, '')])}]
        script['compare:tools'] = [{'output/comparison.json': json.dumps(SAME[2:])}]
        self.assertEqual(self.run_paper(script, open_findings='all'), 0)
        self.assertEqual(self.kinds(launched), [('repair', 'narrow-reading-proof'), ('repair', 'narrow-comparison-tools'),
                                                ('changes', None), ('compare', 'tools'), ('cover', 'tools')])
        corrected = self.calls()[launched + 1]
        self.assertEqual(read_json(self.folder(corrected) / 'findings.json'), [{'label': 'lem:square', 'difference': self.DIFFERENCE}])
        self.assertIn('So this repair is narrow.', corrected['prompt'])
        self.assertNotIn('The whole manuscript is read again after this repair.', corrected['prompt'])
        given = read_json(self.folder(self.calls('changes')[-1]) / 'changes.json')
        self.assertEqual([(c['part'], c['findings']) for c in given['changes']], [('tools', [2]), ('proof', [1])])
        self.assertEqual([(f['finding'], f['check']) for f in given['findings']], [(1, paper.READING), (2, paper.COMPARISON)])
        # Only the statement whose text changed is compared, by a session that is told so.
        compared = self.calls('compare')[-1]
        self.assertEqual([s['label'] for s in read_json(self.folder(compared) / 'statements.json')], ['lem:square'])
        self.assertIn('lists those numbered statements of this section whose present text has not been compared', compared['prompt'])
        self.assertEqual(self.events('comparison')[-1], {**self.events('comparison')[-1], 'statements': ['lem:square'], 'differing': []})
        rows = read_json(self.out / 'correspondence.json')['statements']
        self.assertEqual([r['comparison']['verdict'] for r in rows], ['same'] * 3)
        end = self.events('end')[-1]
        self.assertEqual((end['status'], end['open']), ('complete', []))
        self.assertEqual((self.part('tools'), self.part('proof')),
                         (TOOLS.replace('Expand the right-hand side.', EXPANDED), PROOF_BASED))
        self.assertTrue((self.out / 'paper.pdf').is_file())
        # Nothing is open now: the option refuses, and says so. Typesetting later reports the same.
        launched = len(self.calls())
        code, said = self.said(['--open-findings', '--tex', *TEX])
        self.assertEqual(code, 1)
        self.assertIn('came to its end with no finding left open (complete); there is nothing to act on', said)
        with self.assertRaisesRegex(paper.Stop, 'came to its end \\(complete\\); there is nothing to continue'):
            self.run_paper(good(), resume=True)
        self.assertEqual(self.run_paper(good(), only=True), 0)
        self.assertEqual(self.events('end')[-1]['open'], [])
        self.assertEqual(len(self.calls()), launched)

    def test_a_statement_that_still_differs_after_its_repair_stays_open_and_typesetting_later_reports_what_is_open_now(self):
        launched = self.leave_open()
        script = good()
        # The session changes the statement, and the comparison of the changed statement still finds a difference.
        script['repair:narrow-comparison-tools'] = [{'output/tools.tex': self.OFF.replace('k^2 + 2k', 'k^2 + 2k + 0'),
                                                     'output/response.json': answers('revised')}]
        script['changes'] = [{'output/verdicts.json': verdicts([(True, [3], 'Read with its proof.')], [(3, True, '')])}]
        still = 'The manuscript has k^2 + 2k + 0 = (k + 1)^2.'
        script['compare:tools'] = [{'output/comparison.json': json.dumps([{**SAME[2], 'verdict': 'differs', 'difference': still}])}]
        self.assertEqual(self.run_paper(script, open_findings='3'), 2)
        self.assertEqual(self.kinds(launched), [('repair', 'narrow-comparison-tools'), ('changes', None), ('compare', 'tools'),
                                                ('cover', 'tools')])
        # It is not repaired again in the same pass: it is open with the difference that was found now.
        end = self.events('end')[-1]
        self.assertEqual(end['open'], [self.left[0], {
            'check': paper.COMPARISON, 'after_repairs': paper.COMPARISON_ROUNDS,
            'problems': [{'label': 'lem:square', 'difference': still, 'open_because': paper.DIFFERS_NOW}]}])
        # Typesetting later keeps what is open after this pass, and not what the run itself had left.
        self.assertEqual(self.run_paper(good(), only=True), 2)
        self.assertEqual(self.events('end')[-1]['open'], end['open'])

    def test_a_pass_over_open_findings_that_was_stopped_is_continued(self):
        launched = self.leave_open()
        script = good()
        script['repair:narrow-reading-tools'] = [{'output/tools.tex': self.OFF.replace('Expand the right-hand side.', EXPANDED),
                                                  'output/response.json': answers('revised')}]
        script['repair:narrow-reading-proof'] = [{'output/response.json': json.dumps(
            [{'finding': 1, 'action': 'kept', 'note': 'An induction on $n$ starts at $0$.'}])}]
        script['changes'] = [{}]
        write_json(self.scenario / 'script.json', script)
        with patch('paper.worker_command', side_effect=self.command), patch('builtins.print'), self.assertRaises(paper.Stop):
            paper.act_on_open(self.instance, self.out, TEX, parallel=1, numbers='1-2')
        self.assertEqual(self.kinds(launched), [('repair', 'narrow-reading-tools'), ('repair', 'narrow-reading-proof'),
                                                ('changes', None), ('changes', None)])
        self.assertEqual(self.events('end')[-1]['status'], 'failed')
        state = read_json(self.out / 'state.json')
        self.assertEqual((state['narrow']['step'], state['narrow']['pass'], [f['number'] for f in state['narrow']['findings']]),
                         ('read', True, [1, 2]))
        launched = len(self.calls())
        # A pass that was stopped is neither begun again nor typeset; it is continued with --resume.
        with self.assertRaisesRegex(paper.Stop, 'has not come to its end'):
            self.run_paper(script, open_findings='all')
        with self.assertRaisesRegex(paper.Stop, 'was stopped in the last repair of findings'):
            self.run_paper(script, only=True)
        script['changes'] = [{'output/verdicts.json': verdicts([(True, [1], 'Read with the proof of Lemma 2.2.')], [(1, True, '')])}]
        self.assertEqual(self.run_paper(script, resume=True), 2)
        # The repair is not made again: the changes are read, the running text of the section that changed is
        # compared, and the run ends anew. The statement that differs was not chosen and is open as it was; the
        # finding that the repair kept is open with the new reason.
        self.assertEqual(self.kinds(launched), [('changes', None), ('cover', 'tools')])
        end = self.events('end')[-1]
        self.assertEqual((end['status'], end['open']), ('open_findings', [
            {'check': paper.READING, 'after_repairs': 2,
             'problems': [{**BASE, 'open_because': paper.KEPT + 'An induction on $n$ starts at $0$.'}]}, self.left[1]]))
        self.assertIn(EXPANDED, self.part('tools'))
        self.assertEqual(read_json(self.out / 'state.json')['narrow'], None)
        self.assertFalse((self.out / 'narrow').exists())

    def test_a_run_without_open_findings_and_a_run_that_has_not_ended_are_refused(self):
        self.assertEqual(self.run_paper(good()), 0)
        launched = len(self.calls())
        with self.assertRaisesRegex(paper.Stop, 'came to its end with no finding left open \\(complete\\); there is nothing to act on'):
            self.run_paper(good(), open_findings='all')
        code, said = self.said(['--open-findings', '--dry-run', '--tex', *TEX])
        self.assertEqual(code, 1)
        self.assertIn('paper.py: the run in', said)
        self.assertIn('came to its end with no finding left open (complete); there is nothing to act on', said)
        # The option goes with neither --resume nor --typeset-only, and its numbers are those of the list.
        for arguments in (['--open-findings', '--resume'], ['--open-findings', '2', '--typeset-only']):
            code, said = self.said(arguments)
            self.assertEqual(code, 1)
            self.assertIn('it goes with neither --typeset-only nor --resume', said)
        self.assertEqual(len(self.calls()), launched)
        # A run that was stopped has no list of open findings yet, and a folder without a run has none.
        self.out = self.root / 'paper-stopped'
        script = good()
        script['read'] = [{}]
        with self.assertRaises(paper.Stop):
            self.run_paper(script)
        with self.assertRaisesRegex(paper.Stop, 'has not come to its end.*continued with --resume'):
            self.run_paper(good(), open_findings='all')
        with self.assertRaisesRegex(paper.Stop, 'holds no run of this command that came to its end'):
            paper.act_on_open(self.instance, self.root / 'elsewhere', TEX)

    def test_the_numbers_given_are_those_of_the_list(self):
        launched = self.leave_open(comparison=False)
        for wrong in ('3', '0', 'tools'):
            with self.assertRaises(paper.Stop):
                self.run_paper(good(), open_findings=wrong)
        self.assertEqual(len(self.calls()), launched)
        self.assertEqual(self.events('end')[-1]['open'], self.left)


class SessionsTests(PaperCase):
    """The class that launches sessions, used by itself as another command of the skill uses it."""

    def test_sessions_are_launched_without_a_paper_with_servers_and_with_files_of_bytes(self):
        write_json(self.scenario / 'script.json', {'probe': [{'output/found.json': '{"found": 1}'},
                                                             {'output/found.json': '[]'},
                                                             {'output/found.json': '{"found": 2}'}]})
        out = self.root / 'work'
        servers = {'literature': {'command': 'python', 'args': ['server.py']}}
        with patch('paper.worker_command', side_effect=self.command):
            sessions = paper.Sessions(self.instance, out, parallel=3)
            self.assertEqual((sessions.instance, sessions.out, sessions.parallel, sessions.dry, sessions.gate, sessions.log),
                             (self.instance.resolve(), out.resolve(), 3, False, None, []))
            # The writer is the first of the models; the assessor is the first of the review role, or of the models.
            first = sessions.settings['models'][0]
            self.assertEqual((sessions.writer, sessions.assessor),
                             ({'model': first['model'], 'effort': first['effort']}, first))
            # A file of a session is a text or bytes, and bytes are written as they are.
            folder = sessions.launch('probe', 'Find it.', {'data/blob.bin': b'\x00\xff\r\n', 'note.md': 'A note.\n'},
                                     sessions.writer, 'one', servers)
            self.assertEqual(folder, out.resolve() / 'sessions' / '01-probe-one')
            self.assertEqual((folder / 'data' / 'blob.bin').read_bytes(), b'\x00\xff\r\n')
            self.assertEqual(read_json(folder / 'output' / 'found.json'), {'found': 1})

            # A task is given to a second session, with the reasons, when the first leaves output that cannot be used.
            def read(output):
                return paper.Sessions.load(output / 'found.json')['found']

            self.assertEqual(sessions.session('probe', 'Find it.', {}, read, sessions.writer, servers=servers), 2)
            self.assertEqual(sessions.side_by_side([lambda: 1, lambda: 2]), [1, 2])
        calls = self.calls()
        self.assertEqual([c['folder'] for c in calls], ['01-probe-one', '02-probe', '03-probe'])
        self.assertTrue({'data/blob.bin', 'note.md'} <= set(calls[0]['given']))
        self.assertIn('output/found.json holds a JSON object', calls[2]['prompt'])
        self.assertIn('previous-output/found.json', calls[2]['given'])
        # Every session received the servers it was launched with, and the log is beside the sessions.
        self.assertEqual(self.servers, [servers] * 3)
        self.assertEqual([e['event'] for e in read_json(out / 'log.json')], ['session', 'session', 'check', 'session'])
        # With a review role in the settings, the assessor is its first model; a paper takes its sessions from the same class.
        self.configure(roles={'review': [{'model': 'claude/opus', 'effort': 'high'}]})
        self.assertEqual(paper.Sessions(self.instance, out).assessor, {'model': 'claude/opus', 'effort': 'high'})
        self.assertEqual(paper.Sessions(self.instance, out).count, 3)
        self.assertTrue(issubclass(paper.Paper, paper.Sessions))

    def test_the_gate_is_held_while_a_session_runs_and_not_while_it_waits_for_a_usage_limit(self):
        write_json(self.scenario / 'script.json', {'probe': [{'output/done.txt': 'done'}]})
        seen = []

        class Gate:
            """Counts who holds it, as a semaphore would."""
            held, calls = 0, []

            def acquire(self, timeout=None):
                Gate.held += 1
                Gate.calls.append('acquire')
                return True

            def release(self):
                Gate.held -= 1
                Gate.calls.append('release')

        def command(*arguments, **options):
            seen.append(('process', Gate.held))
            return self.command(*arguments, **options)

        # The first run of the session ends at the account's usage limit, which is over a moment later.
        limits = [types.SimpleNamespace(retry_at=time.time() + 0.2), None]

        def limit(*arguments, **options):
            seen.append(('limit', Gate.held))
            return limits.pop(0)

        with patch('paper.worker_command', side_effect=command), patch('paper.detect_usage_limit', side_effect=limit):
            sessions = paper.Sessions(self.instance, self.root / 'work', gate=Gate())
            sessions.launch('probe', 'Wait.', {}, sessions.writer)
        # The gate was taken for each run of the CLI and given back before the wait for the limit.
        self.assertEqual(seen, [('process', 1), ('limit', 0), ('process', 1), ('limit', 0)])
        self.assertEqual(Gate.calls, ['acquire', 'release'] * 2)
        self.assertEqual([e['usage_limit_until'] is None for e in sessions.log], [False, True])
        self.assertEqual(len(self.calls()), 2)
        # A semaphore is free again after a session, and a run of the paper command holds the gate it is given.
        gate = threading.BoundedSemaphore(1)
        with patch('paper.worker_command', side_effect=self.command):
            sessions = paper.Sessions(self.instance, self.root / 'work-2', gate=gate)
            sessions.launch('probe', 'Wait.', {}, sessions.writer)
        self.assertTrue(gate.acquire(blocking=False))
        gate.release()
        self.assertIs(paper.Paper(self.instance, self.out, TEX, {}, gate=gate).gate, gate)


class TitlePageTests(unittest.TestCase):
    def test_the_author_lines_are_the_script_s_and_there_are_none_without_an_author(self):
        authors = [{'name': 'Ada Lovelace', 'address': 'Dept. of Analysis & Engines, London', 'email': 'ada_l@example.org'},
                   {'name': 'C. Babbage'}]
        tex, spans = paper.assemble(PLAN, PARTS, authors)
        lines = tex.split('\n')
        title = lines.index('\\title{The sum of the first odd numbers}')
        # After the title, for each author the name and what the title page gives of address and email; a
        # character that TeX reads as a command is written so that it is printed.
        self.assertEqual(lines[title + 1:title + 6],
                         ['\\author{Ada Lovelace}', '\\address{Dept. of Analysis \\& Engines, London}',
                          '\\email{ada\\_l@example.org}', '\\author{C. Babbage}', '\\begin{abstract}'])
        # The lines of the parts are counted with the author lines in place.
        name, first, last = spans[0]
        self.assertEqual((name, '\n'.join(lines[first - 1:last])), ('abstract', ABSTRACT.strip('\n')))
        # Without an author, and with an empty list, the manuscript is as it was: it has no author line.
        self.assertEqual(paper.assemble(PLAN, PARTS, [])[0], paper.assemble(PLAN, PARTS)[0])
        self.assertNotIn('\\author', paper.assemble(PLAN, PARTS)[0])

    def test_the_title_page_file_names_the_authors(self):
        folder = Path(tempfile.mkdtemp(prefix='do-math-title-'))
        self.addCleanup(shutil.rmtree, folder, True)
        page = folder / 'title-page.json'
        write_json(page, {'authors': [{'name': 'Ada Lovelace', 'email': 'ada@example.org', 'orcid': '0000'}, {'name': 'C. Babbage'}]})
        self.assertEqual(paper.read_title_page(page), [{'name': 'Ada Lovelace', 'email': 'ada@example.org'}, {'name': 'C. Babbage'}])
        write_json(page, {'authors': []})
        self.assertEqual(paper.read_title_page(page), [])
        for wrong in ({'authors': [{'name': ''}]}, {'authors': 'Ada'}, {'authors': [{'name': 'Ada', 'email': 3}]}, ['Ada']):
            write_json(page, wrong)
            with self.assertRaises(paper.Stop):
                paper.read_title_page(page)
        page.write_text('{', encoding='utf-8')
        with self.assertRaises(paper.Stop):
            paper.read_title_page(page)


# ----------------------------------------------------------------------------- the draft, and the paper from it

# What the sketching sessions of the three sections write. The main theorem is declared as a gap that is none; the
# first lemma is sketched weaker than its element without a word; the second is wanted in more generality.
MAIN_TEXT = 'For every natural number $n$, we have $S_n = n^2$.'
WEAK = 'For every natural number $n$, we have $S_n \\le S_{n+1}$.'
STRICT = 'For every natural number $n$, the sum $S_{n+1}$ is strictly larger than $S_n$.'
REAL = 'For every real number $x$, we have $x^2 + (2x + 1) = (x + 1)^2$.'
GAIN_FORMULA = 'S_{n+1} = S_n + (2n + 1)'
WANTED = {'wanted': 'The identity $x^2 + (2x + 1) = (x + 1)^2$ for every real number $x$.',
          'has': 'The identity for natural numbers.', 'reason': 'A paper states an identity in the generality in which it holds.'}
BOUND = {'element': 'Small.oddSum_mono', 'wanted': 'The bound $S_n \\ge n$ for every natural number $n$.',
         'has': 'That the sums increase.', 'reason': 'The proof of the main theorem refers to the bound.'}
SHARPNESS = {'host': None, 'element': 'Small.sq_step', 'wanted': 'The identity holds for no other increment than $2k + 1$.',
             'has': 'The identity for the increment $2k + 1$.', 'reason': 'The section remarks on it after the lemma.'}
SKETCHES = {
    'intro': {'statements': [{'label': 'thm:main', 'text': MAIN_TEXT,
                              'gap': {'wanted': 'The sum is $n^2$.', 'has': 'The sum is $n \\cdot n$.', 'reason': 'Squares are written as squares.'}}],
              'formulas': [], 'assertions': []},
    'tools': {'statements': [{'label': 'lem:increasing', 'text': WEAK, 'gap': None},
                             {'label': 'lem:square', 'text': REAL, 'gap': WANTED}],
              'formulas': [{'label': 'eq:tools-gain', 'host': 'lem:increasing', 'text': GAIN_FORMULA,
                            'element': 'Small.oddSum_succ', 'gap': None},
                           {'label': 'eq:tools-bound', 'host': None, 'text': 'S_n \\ge n', 'element': None, 'gap': BOUND}],
              'assertions': [SHARPNESS]},
    'proof': {'statements': [], 'formulas': [], 'assertions': []}}
CITATIONS = [{'element': 'Small.sq_step', 'result': 'completing the square', 'reason': 'An identity of the textbooks.'}]
DRAFT_VERDICTS = {
    'intro': [{'label': 'thm:main', 'verdict': 'same', 'difference': '', 'text': ''}],
    'tools': [{'label': 'lem:increasing', 'verdict': 'differs', 'difference': 'The sketch has a weak inequality.', 'text': STRICT},
              {'label': 'lem:square', 'verdict': 'differs', 'difference': 'The sketch speaks of real numbers.', 'text': ''},
              {'label': 'eq:tools-gain', 'verdict': 'same', 'difference': '', 'text': ''}]}


def drafting():
    """A scenario in which the paper is drafted: the plan with the results to cite, the sketches and the comparisons."""
    return {'plan': [{'output/plan.json': json.dumps({**PLAN, 'citations': CITATIONS}), 'output/study.md': STUDY}],
            **{f'sketch:{sid}': [{'output/sketch.json': json.dumps(sketch)}] for sid, sketch in SKETCHES.items()},
            **{f'compare:{sid}': [{'output/comparison.json': json.dumps(found)}] for sid, found in DRAFT_VERDICTS.items()}}


class DraftTests(PaperCase):
    """The draft of a paper: the plan, a sketch of every section, and the sketched statements compared with the elements."""

    def test_a_draft_holds_the_statements_the_formulas_the_gaps_and_the_results_to_cite(self):
        script = drafting()
        # The first plan lacks the list of results to cite, and the first sketch of the last section states what the
        # plan gives to another section.
        script['plan'].insert(0, {'output/plan.json': json.dumps(PLAN), 'output/study.md': STUDY})
        script['sketch:proof'].insert(0, {'output/sketch.json': json.dumps({**SKETCHES['proof'], 'statements': SKETCHES['intro']['statements']})})
        write_json(self.scenario / 'script.json', script)
        with patch('paper.worker_command', side_effect=self.command), patch('builtins.print'):
            self.assertEqual(paper.main([str(self.instance), '--out', str(self.out), '--parallel', '1', '--draft', '--tex', *TEX]), 0)
        calls = self.calls()
        self.assertEqual([(c['kind'], c['section']) for c in calls],
                         [('plan', None), ('plan', None), ('sketch', 'intro'), ('sketch', 'tools'), ('sketch', 'proof'),
                          ('sketch', 'proof'), ('compare', 'intro'), ('compare', 'tools')])
        # Only the plan of a draft is asked for the results to cite, and it is not accepted without the list.
        self.assertIn('"citations"', calls[0]['prompt'])
        self.assertNotIn('"citations"', paper.PLAN_PROMPT)
        self.assertIn('"citations" is an array', calls[1]['prompt'])
        self.assertIn('"statements" has one object for each numbered statement that the plan has this section state',
                      calls[5]['prompt'])
        # A sketching session has what the writer of its section will have, and writes no part.
        sketching = calls[3]
        self.assertEqual(sketching['given'], sorted(['brief.md', 'paper-method.md', 'plan.json', 'prompt.txt', 'session.json',
                                                     'study.md', 'exemplars/gamma.tex', 'exemplars/delta.tex'] + RECORD_FILES))
        self.assertEqual((self.folder(sketching) / 'brief.md').read_text(encoding='utf-8'),
                         paper.render_brief(self.materials(), read_json(self.out / 'plan.json'), PLAN['sections'][1]))
        # The comparison has the sketched statements of its section and its formulas that name an element, each with
        # the gap that was declared for it; there is no manuscript yet.
        comparing = calls[7]
        self.assertEqual(comparing['given'], sorted(['paper-method.md', 'plan.json', 'prompt.txt', 'records.md', 'session.json',
                                                     'statements.json', 'elements.md'] + RECORD_FILES[3:]))
        rows = read_json(self.folder(comparing) / 'statements.json')
        self.assertEqual([(r['label'], r['kind'], r['element'], r['draft_statement'], r['declared_gap']) for r in rows],
                         [('lem:increasing', 'numbered statement', 'Small.oddSum_mono', WEAK, None),
                          ('lem:square', 'numbered statement', 'Small.sq_step', REAL, WANTED),
                          ('eq:tools-gain', 'displayed formula', 'Small.oddSum_succ', GAIN_FORMULA, None)])
        self.assertIn('S_n < S_{n+1}', rows[0]['record_statement'])
        self.assertIn('oddSum n < oddSum (n + 1)', rows[0]['lean_statement'])
        # The folder holds the plan, the account of the papers and the draft, and no part of a paper.
        self.assertEqual(read_json(self.out / 'plan.json'), {**PLAN, 'citations': CITATIONS})
        self.assertEqual((self.out / 'study.md').read_text(encoding='utf-8'), STUDY)
        for name in ('parts', 'paper.tex', 'state.json', 'correspondence.json'):
            self.assertFalse((self.out / name).exists(), name)
        draft = read_json(self.out / 'draft.json')
        # A gap that the comparison found to be none is dropped; a statement that differs without a declared gap is
        # replaced by the statement as its element says it; a declared gap stays with the text that was wanted.
        self.assertEqual(draft['statements'], [
            {'label': 'thm:main', 'section': 'intro', 'element': 'Small.root', 'text': MAIN_TEXT, 'gap': None},
            {'label': 'lem:increasing', 'section': 'tools', 'element': 'Small.oddSum_mono', 'text': STRICT, 'gap': None},
            {'label': 'lem:square', 'section': 'tools', 'element': 'Small.sq_step', 'text': REAL, 'gap': 'g1'}])
        self.assertEqual(draft['formulas'], [
            {'label': 'eq:tools-gain', 'section': 'tools', 'host': 'lem:increasing', 'text': GAIN_FORMULA,
             'element': 'Small.oddSum_succ', 'gap': None},
            {'label': 'eq:tools-bound', 'section': 'tools', 'host': None, 'text': 'S_n \\ge n', 'element': None, 'gap': 'g2'}])
        common = {'section': 'tools', 'closed_by': None}
        self.assertEqual(draft['gaps'], [
            {'id': 'g1', 'kind': 'statement', 'label': 'lem:square', 'host': None, 'element': 'Small.sq_step', **WANTED, **common},
            {'id': 'g2', 'kind': 'formula', 'label': 'eq:tools-bound', 'host': None, **BOUND, **common},
            {'id': 'g3', 'kind': 'assertion', 'label': None, **SHARPNESS, **common}])
        self.assertEqual(draft['citations'], CITATIONS)
        self.assertNotIn('main', draft)
        drafted = self.events('draft')[0]
        self.assertEqual((drafted['slips'], drafted['gaps_dropped']),
                         ([{'label': 'lem:increasing', 'difference': 'The sketch has a weak inequality.'}], ['thm:main']))
        end = self.events('end')[-1]
        self.assertEqual((end['status'], end['open'], end['kept']), ('draft', [], []))
        # A draft that came to its end is not continued, and it is no manuscript to typeset.
        with self.assertRaisesRegex(paper.Stop, 'came to its end \\(draft\\)'):
            self.run_paper(drafting(), resume=True)
        with self.assertRaises(paper.Stop):
            self.run_paper(drafting(), only=True)

    def test_a_draft_that_was_stopped_is_continued_with_what_was_sketched_and_compared(self):
        script = drafting()
        script['compare:tools'] = [{}]  # the comparison of one section leaves nothing, twice
        with self.assertRaises(paper.Stop):
            self.run_paper(script, draft=True)
        launched = len(self.calls())
        self.assertEqual(sorted(path.name for path in (self.out / 'sketch').iterdir()),
                         ['intro.compared.json', 'intro.json', 'proof.json', 'tools.json'])
        self.assertFalse((self.out / 'draft.json').exists())
        # The run is continued as the draft it was begun as, with the one session that is missing.
        self.assertEqual(self.run_paper(drafting(), resume=True), 0)
        self.assertEqual([(c['kind'], c['section']) for c in self.calls()][launched:], [('compare', 'tools')])
        self.assertEqual([entry['text'] for entry in read_json(self.out / 'draft.json')['statements']], [MAIN_TEXT, STRICT, REAL])
        self.assertEqual([e['status'] for e in self.events('end')], ['failed', 'draft'])
        # A run that was begun as a paper is not continued as a draft, and a draft is one of the two kinds of run.
        with self.assertRaisesRegex(paper.Stop, 'a run is one of the two'):
            paper.produce(self.instance, self.root / 'other', TEX, draft=True, from_draft=self.out)

    def test_the_results_to_cite_are_statements_whose_record_names_no_source(self):
        materials = self.materials()
        check = lambda citations: paper.check_plan(materials, {**PLAN, 'citations': citations}, KEYS)
        self.assertEqual(check(CITATIONS), [])
        self.assertEqual(check([]), [])
        entry = CITATIONS[0]
        for citations, words in (([{**entry, 'element': 'Small.expand'}], 'has the source euclid in its record'),
                                 ([{**entry, 'element': 'Small.oddSum'}], "'Small.oddSum' is not a statement of the materials"),
                                 ([{**entry, 'result': ''}], 'needs a "result"'),
                                 ([entry, entry], 'is listed twice'),
                                 ('Small.sq_step', '"citations", when the plan has it, is an array of objects')):
            self.assertIn(words, ' '.join(check(citations)))


# The plan as it was when the paper was drafted, before the library had its final form. The first lemma stated the
# weak inequality, which the library then had; the expansion of a square had no source and was a lemma with a proof;
# two elements that are gone were in the plan, and the step that the first lemma absorbs did not exist. Neither did
# `Small.unused`, which the proof of the root does not rest on: it closed the gap of an assertion.
DRAFT_PLAN = {
    **PLAN,
    'statements': [
        PLAN['statements'][0],
        {'element': 'Small.oddSum_mono_weak', 'kind': 'lemma', 'label': 'lem:increasing', 'section': 'tools'},
        {'element': 'Small.gone', 'kind': 'lemma', 'label': 'lem:gone', 'section': 'tools'},
        {'element': 'Small.expand', 'kind': 'lemma', 'label': 'lem:expand', 'section': 'tools',
         'reason': 'The second lemma is this identity at one pair, and the reader has it at hand.'},
        PLAN['statements'][2]],
    'others': [PLAN['others'][0],
               {'element': 'Small.vanished', 'treatment': 'absorbed', 'into': ['Small.gone']}],
    'citations': [{'element': 'Small.expand', 'result': 'the square of a sum', 'reason': 'Euclid has it.'}]}
EXPAND_TEXT = 'For natural numbers $a$ and $b$, we have $(a+b)^2 = a^2 + 2ab + b^2$.'
# The draft as the pipeline hands it over: each statement with the element that states it now, the gaps with the
# declarations that closed them, and a statement that had to go.
DRAFT = {
    'statements': [
        {'label': 'thm:main', 'section': 'intro', 'element': 'Small.root', 'text': MAIN_TEXT, 'gap': None},
        {'label': 'lem:increasing', 'section': 'tools', 'element': 'Small.oddSum_mono', 'text': STRICT, 'gap': 'g1'},
        {'label': 'lem:gone', 'section': 'tools', 'element': 'Small.gone', 'text': 'A statement that had to go.', 'gap': None,
         'cut': True},
        {'label': 'lem:expand', 'section': 'tools', 'element': 'Small.expand', 'text': EXPAND_TEXT, 'gap': None},
        {'label': 'lem:square', 'section': 'tools', 'element': 'Small.sq_step',
         'text': 'For every natural number $k$, we have $k^2 + (2k + 1) = (k + 1)^2$.', 'gap': None}],
    'formulas': [{'label': 'eq:tools-gain', 'section': 'tools', 'host': 'lem:increasing', 'text': GAIN_FORMULA,
                  'element': 'Small.oddSum_succ', 'gap': 'g2'}],
    'gaps': [{'id': 'g1', 'kind': 'statement', 'section': 'tools', 'label': 'lem:increasing', 'host': None,
              'element': 'Small.oddSum_mono_weak', 'wanted': 'The strict inequality.', 'has': 'The weak inequality.',
              'reason': 'The proof of the main theorem uses the strict form.', 'closed_by': 'Small.oddSum_mono'},
             {'id': 'g2', 'kind': 'formula', 'section': 'tools', 'label': 'eq:tools-gain', 'host': 'lem:increasing',
              'element': 'Small.oddSum_mono_weak', 'wanted': 'The gain of one step.', 'has': 'Nothing.',
              'reason': 'A later proof refers to it.', 'closed_by': 'Small.oddSum_succ'},
             {'id': 'g3', 'kind': 'assertion', 'section': 'tools', 'label': None, 'host': 'lem:increasing',
              'element': 'Small.oddSum_mono_weak', 'wanted': 'Each sum is at most itself and one.', 'has': 'Nothing.',
              'reason': 'The section remarks on it after the lemma.', 'closed_by': 'Small.unused'},
             {'id': 'g4', 'kind': 'assertion', 'section': 'tools', 'label': None, 'host': None, 'element': 'Small.sq_step',
              'wanted': 'A remark.', 'has': 'Nothing.', 'reason': 'It was not closed.', 'closed_by': None}],
    'citations': DRAFT_PLAN['citations']}
# The plan that the script makes of it for the library as it now is.
CARRIED = {
    **PLAN,
    'statements': [
        PLAN['statements'][0],
        {'element': 'Small.oddSum_mono', 'kind': 'lemma', 'label': 'lem:increasing', 'section': 'tools'},
        {**DRAFT_PLAN['statements'][3], 'proof': 'cited'},
        PLAN['statements'][2]],
    'others': [PLAN['others'][0],
               {'element': 'Small.oddSum_mono_weak', 'treatment': 'not_stated', 'by': 'Small.oddSum_mono',
                'reason': 'The paper states this result in the form of the element under "by", which the library gained '
                          'after the draft; this element is the form it had before.'},
               {'element': 'Small.oddSum_succ', 'treatment': 'absorbed', 'into': ['Small.oddSum_mono'],
                'reason': 'It states what the draft of the paper needed at this place and the library did not yet contain.'},
               {'element': 'Small.unused', 'treatment': 'absorbed', 'into': ['tools'],
                'reason': 'It states what the draft of the paper needed at this place and the library did not yet contain.'}],
    'citations': []}
TOOLS_CITED = r'''\begin{lemma}\label{lem:increasing}
For every natural number $n$, the sum $S_{n+1}$ is strictly larger than $S_n$.
\end{lemma}
\begin{proof}
The sum $S_{n+1}$ exceeds $S_n$ by $2n + 1$.
\end{proof}

\begin{lemma}[{\cite[Book II, Proposition 4]{euclid}}]\label{lem:expand}
For natural numbers $a$ and $b$, we have $(a+b)^2 = a^2 + 2ab + b^2$.
\end{lemma}

\begin{lemma}\label{lem:square}
For every natural number $k$, we have $k^2 + (2k + 1) = (k + 1)^2$.
\end{lemma}
\begin{proof}
Expand the right-hand side by Lemma~\ref{lem:expand}.
\end{proof}
'''
CITED_LABELS = ('lem:increasing', 'lem:expand', 'lem:square')


def written_from_draft():
    """A scenario in which the paper is written from the carried plan; no session plans it."""
    script = good()
    del script['plan']
    script['write:tools'] = [{'output/tools.tex': TOOLS_CITED}]
    script['compare:tools'] = [{'output/comparison.json': json.dumps(
        [{'label': label, 'verdict': 'same', 'difference': ''} for label in CITED_LABELS])}]
    return script


class FromDraftTests(PaperCase):
    """A paper that is written from a draft, after the library has changed."""

    def draft_folder(self, plan=DRAFT_PLAN, draft=DRAFT):
        folder = self.root / 'draft'
        folder.mkdir()
        write_json(folder / 'plan.json', plan)
        write_json(folder / 'draft.json', draft)
        (folder / 'study.md').write_text(STUDY, encoding='utf-8', newline='\n')
        return folder

    def test_the_plan_of_the_draft_is_brought_to_the_library_by_script_and_the_briefs_carry_the_draft(self):
        folder = self.draft_folder()
        page = self.root / 'title-page.json'
        write_json(page, {'authors': [{'name': 'Ada Lovelace', 'address': 'London', 'email': 'ada_l@example.org'}]})
        self.assertEqual(self.run_paper(written_from_draft(), from_draft=folder, title_page=page), 0)
        calls = self.calls()
        # The check of the plan passed, so no session planned anything and none read the collection.
        self.assertEqual([(c['kind'], c['section']) for c in calls],
                         [('write', 'intro'), ('write', 'tools'), ('write', 'proof'), ('read', None), ('likeness', None),
                          ('likeness', None), *COMPARED, ('cover', 'intro')])
        # A statement that was cut and an element that is gone left the plan; the declaration that closed the gap of
        # the first lemma is stated under its kind and label, and the form the library had before is not stated; the
        # declaration that closed the gap of a formula is absorbed where the gap stood; the lemma whose element now has
        # a source is cited.
        self.assertEqual(read_json(self.out / 'plan.json'), CARRIED)
        # The materials of the run hold the declaration that closed a gap and that the proof of the root does not
        # rest on, marked as such, and the main result is still the last element. The script enters it where the
        # gap stood: the lemma in whose proof the gap stood does not rest on it, so into the running text.
        materials = read_json(self.out / 'materials.json')
        names = [element['name'] for element in materials['elements']]
        self.assertEqual(sorted(names), sorted([element['name'] for element in self.materials()['elements']] + ['Small.unused']))
        self.assertEqual((names[-1], materials['further'], [e['name'] for e in materials['elements'] if e.get('outside')]),
                         ('Small.root', ['Small.oddSum_mono', 'Small.oddSum_succ', 'Small.unused'], ['Small.unused']))
        self.assertEqual(self.events('materials')[0]['further'], materials['further'])
        self.assertEqual(paper.carried_plan(materials, DRAFT_PLAN, DRAFT)[0], CARRIED)
        self.assertEqual(paper.check_plan(materials, CARRIED, KEYS), [])
        planned = self.events('plan')[0]
        self.assertEqual((planned['from_draft'], planned['repaired']), (True, False))
        notes = ' '.join(planned['carried'])
        for words in ('`lem:gone` was cut', '`Small.vanished` left the plan', '`lem:increasing` states `Small.oddSum_mono`',
                      '`lem:expand` is cited', '`Small.oddSum_succ`, which closed the gap g2, is absorbed into `Small.oddSum_mono`',
                      '`Small.unused`, which closed the gap g3, is absorbed into `tools`'):
            self.assertIn(words, notes)
        # The account of the papers and the draft are taken over.
        self.assertEqual((self.out / 'study.md').read_text(encoding='utf-8'), STUDY)
        self.assertEqual(read_json(self.out / 'draft.json'), DRAFT)
        # The brief of a section carries its statements and formulas as they were drafted, and the writer is told so;
        # a section for which nothing was drafted is written as in any run.
        tools, proof = calls[1], calls[2]
        brief = (self.folder(tools) / 'brief.md').read_text(encoding='utf-8')
        drafted = brief.split('## The statements and formulas of this section as they were drafted\n')[1].split('\n## ')[0]
        for words in (STRICT, EXPAND_TEXT, GAIN_FORMULA, 'lemma `lem:increasing`, which states the element `Small.oddSum_mono`',
                      '`eq:tools-gain`, in the proof of `lem:increasing`'):
            self.assertIn(words, drafted)
        self.assertNotIn('A statement that had to go.', brief)
        self.assertEqual(brief, paper.render_brief(materials, CARRIED, CARRIED['sections'][1], draft=DRAFT))
        # The writer of the section has the record of that declaration in full, and is told what it is.
        self.assertIn('written into the running text: `Small.unused`', brief)
        added = brief.split('### `Small.unused`\n')[1].split('\n### ')[0]
        self.assertIn(paper.OUTSIDE, added)
        self.assertIn('The proof of the root does not rest on this element.', added)
        self.assertIn('elements/Small.unused.md', tools['given'])
        self.assertIn(paper.DRAFTED.strip(), tools['prompt'])
        self.assertNotIn(paper.DRAFTED.strip(), proof['prompt'])
        self.assertNotIn('as they were drafted', (self.folder(proof) / 'brief.md').read_text(encoding='utf-8'))
        # The lemma from the literature is cited and has no proof, and the manuscript is checked as in any run.
        rows = read_json(self.out / 'correspondence.json')['statements']
        self.assertEqual([(r['label'], r['comparison']['verdict']) for r in rows],
                         [('thm:main', 'same'), ('lem:increasing', 'same'), ('lem:expand', 'same'), ('lem:square', 'same')])
        # The correspondence file names the source of the statement that the paper cites in place of a proof.
        self.assertEqual([r['cited'] for r in rows], [None, None, 'euclid', None])
        self.assertEqual(self.events('end')[-1], {**self.events('end')[-1], 'status': 'complete', 'open': [], 'kept': []})
        # The author line is written by the script from the title page, of which the folder keeps a copy.
        lines = (self.out / 'paper.tex').read_text(encoding='utf-8').split('\n')
        title = lines.index('\\title{The sum of the first odd numbers}')
        self.assertEqual(lines[title + 1:title + 5],
                         ['\\author{Ada Lovelace}', '\\address{London}', '\\email{ada\\_l@example.org}', '\\begin{abstract}'])
        self.assertEqual(read_json(self.out / 'title-page.json'), read_json(page))
        # Typesetting later keeps the authors, and with another title page it sets the author line anew.
        launched = len(calls)
        self.assertEqual(self.run_paper(good(), only=True), 0)
        self.assertIn('\\author{Ada Lovelace}', (self.out / 'paper.tex').read_text(encoding='utf-8'))
        write_json(page, {'authors': []})
        self.assertEqual(self.run_paper(good(), only=True, title_page=page), 0)
        self.assertNotIn('\\author', (self.out / 'paper.tex').read_text(encoding='utf-8'))
        self.assertEqual(len(self.calls()), launched)

    def test_a_plan_that_fails_the_check_is_repaired_by_a_session_that_does_not_read_the_collection(self):
        # The draft's plan says nothing of the object of the problem, which the script cannot place.
        lacking = {**DRAFT_PLAN, 'others': DRAFT_PLAN['others'][1:]}
        folder = self.draft_folder(plan=lacking)
        script = written_from_draft()
        script['plan:from-draft'] = [{}]  # the session that repairs the plan leaves nothing
        with self.assertRaises(paper.Stop) as stopped:
            self.run_paper(script, from_draft=folder)
        self.assertIn(f'no plan session left output the script can use, in {paper.PLAN_ATTEMPTS} attempts', str(stopped.exception))
        repairing = self.calls()
        self.assertEqual([(c['kind'], c['section']) for c in repairing], [('plan', 'from-draft')] * paper.PLAN_ATTEMPTS)
        # It has the plan as the script carried it over, what the check found, the account of the papers and the
        # draft, with the digest and the records, and no paper of the collection.
        self.assertEqual(repairing[0]['given'], sorted(['carried.md', 'draft.json', 'materials-digest.md', 'paper-method.md',
                                                        'plan.json', 'problems.md', 'prompt.txt', 'session.json', 'study.md',
                                                        'elements/Small.unused.md'] + RECORD_FILES[3:]))
        self.assertEqual(read_json(self.folder(repairing[0]) / 'plan.json'), {**CARRIED, 'others': CARRIED['others'][1:]})
        problem = 'the plan says nothing about these elements of the materials: Small.oddSum'
        self.assertIn(problem, (self.folder(repairing[0]) / 'problems.md').read_text(encoding='utf-8'))
        self.assertIn(problem, repairing[0]['prompt'])
        self.assertFalse((self.out / 'plan.json').exists())
        self.assertEqual(self.events('check')[0]['check'], 'the plan of the draft, brought to the materials')
        # The run is continued without the folder of the draft being named again. A plan with other papers is not
        # accepted, since no session reads the collection for it; the plan that passes is written from.
        again = written_from_draft()
        again['plan:from-draft'] = [{}, {}, {}, {'output/plan.json': json.dumps({**CARRIED, 'exemplars': CHOSEN[::-1]})},
                                    {'output/plan.json': json.dumps(CARRIED)}]
        # The run ends with one finding open, so that it can be taken up afterwards.
        again['cover:intro'] = [{'output/coverage.json': json.dumps([{
            'entry': 2, 'quote': 'Which number is $S_n$?', 'asserts': 'Nothing.', 'nearest': 'Small.root',
            'difference': 'A question is put where a result is expected.'}])}]
        again['repair:narrow'] = [{'output/response.json': json.dumps(
            [{'finding': 1, 'action': 'kept', 'note': 'A question asserts nothing.'}])}]
        # The continued run has the draft it recorded when it began, and takes from it the declarations that its
        # materials hold beside what the proof of the root rests on, whatever the folder of the draft says now.
        self.assertIn('Small.unused', [e['name'] for e in read_json(self.out / 'materials.json')['elements']])
        self.assertEqual(read_json(self.out / 'draft.json'), DRAFT)
        write_json(folder / 'draft.json', {**DRAFT, 'gaps': []})
        self.assertEqual(self.run_paper(again, resume=True), 2)
        calls = self.calls()[paper.PLAN_ATTEMPTS:]
        self.assertEqual([(c['kind'], c['section']) for c in calls][:3],
                         [('plan', 'from-draft'), ('plan', 'from-draft'), ('write', 'intro')])
        self.assertIn('"exemplars" stays as plan.json has it', calls[1]['prompt'])
        self.assertEqual(read_json(self.out / 'plan.json'), CARRIED)
        planned = self.events('plan')[0]
        self.assertEqual((planned['from_draft'], planned['repaired']), (True, True))
        self.assertIn(STRICT, (self.folder(calls[3]) / 'brief.md').read_text(encoding='utf-8'))
        # A pass over the open findings compares the canon with the materials of the run in the same way.
        code, said = self.said(['--open-findings', '--dry-run', '--tex', *TEX])
        self.assertEqual(code, 0)
        self.assertIn('came to its end (open_findings) with 1 findings left open', said)

    def test_the_materials_hold_further_declarations_with_what_they_rest_on_and_are_as_before_without_them(self):
        model = replay(self.instance)
        plain = paper.extract(self.instance, model)
        # One declaration that the proof of the root does not rest on, named twice; one that the instance does not
        # have; and one that the proof of the root rests on already.
        materials = paper.extract(self.instance, model, ['Small.unused', 'Small.unused', 'Small.nothing', 'Small.sq_step'])
        names = [element['name'] for element in materials['elements']]
        self.assertEqual(sorted(names), sorted([element['name'] for element in plain['elements']] + ['Small.unused']))
        self.assertEqual(materials['further'], ['Small.unused', 'Small.sq_step'])
        # The order is one of dependence, and the main result is the last element.
        for position, element in enumerate(materials['elements']):
            for used in element['uses'] + element['mentions']:
                self.assertLess(names.index(used), position, (element['name'], used))
        self.assertEqual((names[-1], materials['elements'][-1]['main']), ('Small.root', True))
        # Only what the proof of the root does not rest on is marked, in the materials and in the texts made of them.
        self.assertEqual([element['name'] for element in materials['elements'] if element.get('outside')], ['Small.unused'])
        self.assertIn(paper.OUTSIDE, paper.render_digest(materials))
        self.assertIn('except those marked as added for the draft of the paper', paper.record_files(materials)['elements.md'])
        # Without further declarations the materials are what they were: no key and no mark is added.
        self.assertEqual(paper.extract(self.instance, model, []), plain)
        self.assertNotIn('further', plain)
        self.assertFalse(any('outside' in element for element in plain['elements']))
        self.assertNotIn(paper.OUTSIDE, paper.render_digest(plain) + paper.render_materials(plain))
        # The further declarations of a paper from a draft are those that closed a gap and that the instance has.
        self.assertEqual(paper.closing(DRAFT, model), ['Small.oddSum_mono', 'Small.oddSum_succ', 'Small.unused'])
        self.assertEqual(paper.closing({**DRAFT, 'gaps': [{**DRAFT['gaps'][0], 'closed_by': 'Small.nothing'}]}, model), [])

    def test_a_folder_without_a_draft_is_refused_before_anything_is_written(self):
        folder = self.draft_folder()
        (folder / 'draft.json').unlink()
        with self.assertRaisesRegex(paper.Stop, 'holds no draft of this command to write the paper from: it has no draft.json'):
            self.run_paper(good(), from_draft=folder)
        self.assertFalse(self.out.exists())
        code, said = self.said(['--draft', '--typeset-only'])
        self.assertEqual(code, 1)
        self.assertIn('they go with neither --typeset-only nor --open-findings', said)


# ----------------------------------------------------------------------------- a main result that is not the root

# A paper that is built around the identity of the step, from which the root follows: the identity is the main
# theorem, stated first and proved in the second section, and the root stands as a corollary in the last section.
MAIN_PLAN = {
    **PLAN,
    'statements': [
        {'element': 'Small.sq_step', 'kind': 'theorem', 'label': 'thm:square', 'section': 'intro', 'proof': 'tools'},
        PLAN['statements'][1],
        {'element': 'Small.root', 'kind': 'corollary', 'label': 'cor:sum', 'section': 'proof'}]}
INTRO_MAIN = r'''For a natural number $n$ let $S_n$ denote the sum of the first $n$ odd numbers. One identity carries what follows.

\begin{theorem}\label{thm:square}
For every natural number $k$, we have $k^2 + (2k + 1) = (k + 1)^2$.
\end{theorem}

It is proved in Section~\ref{sec:tools}, and Corollary~\ref{cor:sum} draws the value of $S_n$ from it.
'''
TOOLS_MAIN = r'''\begin{lemma}\label{lem:increasing}
For every natural number $n$, we have $S_n < S_{n+1}$.
\end{lemma}
\begin{proof}
The sum $S_{n+1}$ exceeds $S_n$ by $2n + 1$.
\end{proof}

The theorem is the expansion of a square \cite[Book II, Proposition 4]{euclid} for the pair $k$ and $1$.

\begin{proof}[Proof of Theorem~\ref{thm:square}]
Expand the right-hand side.
\end{proof}
'''
PROOF_MAIN = r'''\begin{corollary}\label{cor:sum}
For every natural number $n$, we have $S_n = n^2$.
\end{corollary}
\begin{proof}
By induction on $n$. The sums increase by Lemma~\ref{lem:increasing}, and the step is Theorem~\ref{thm:square}.
\end{proof}
'''
MAIN_STATED = {'intro': 'thm:square', 'tools': 'lem:increasing', 'proof': 'cor:sum'}


def around_the_step():
    """A scenario in which the paper is written around `Small.sq_step` at the first attempt of every session."""
    return {'plan': [{'output/plan.json': json.dumps(MAIN_PLAN), 'output/study.md': STUDY}],
            'write:intro': [{'output/intro.tex': INTRO_MAIN, 'output/abstract.tex': ABSTRACT}],
            'write:tools': [{'output/tools.tex': TOOLS_MAIN}], 'write:proof': [{'output/proof.tex': PROOF_MAIN}],
            'read': [{'output/reading.json': json.dumps(CLEAN)}],
            'likeness': [{'output/likeness.json': json.dumps(LIKE)}],
            **{f'compare:{sid}': [{'output/comparison.json': json.dumps([{'label': label, 'verdict': 'same', 'difference': ''}])}]
               for sid, label in MAIN_STATED.items()},
            'cover': [{'output/coverage.json': '[]'}]}


class MainResultTests(PaperCase):
    """A paper whose main result is a theorem that was chosen for it, and not the declaration that settles the root."""

    def kinds(self, since=0):
        return [(c['kind'], c['section']) for c in self.calls()][since:]

    def test_the_materials_and_the_plan_check_follow_a_chosen_main_result_and_are_as_before_without_one(self):
        model = replay(self.instance)
        plain = paper.extract(self.instance, model)
        materials = paper.extract(self.instance, model, main='Small.sq_step')
        # The materials name the chosen theorem as the main result and still say which declaration settles the root.
        # They hold what both rest on, in dependence order, each of the two marked.
        self.assertEqual((materials['main'], materials['settles'], materials['root']['name']),
                         ('Small.sq_step', 'Small.root', 'Small.root'))
        names = [element['name'] for element in materials['elements']]
        self.assertEqual(sorted(names), sorted(element['name'] for element in plain['elements']))
        for position, element in enumerate(materials['elements']):
            for used in element['uses'] + element['mentions']:
                self.assertLess(names.index(used), position, (element['name'], used))
        self.assertEqual(([e['name'] for e in materials['elements'] if e['main']],
                          [e['name'] for e in materials['elements'] if e.get('settles')]), (['Small.sq_step'], ['Small.root']))
        # What the sessions are given says so: the head of the materials, the digest with both records in full, and
        # the list of the elements.
        files = paper.record_files(materials)
        self.assertIn('The declaration whose formal proof settles it is `Small.root`.', files['root.md'])
        self.assertEqual(paper.main_lines(materials)[0], '## The main result of the paper')
        self.assertIn('\n'.join(paper.main_lines(materials)), files['root.md'])
        self.assertIn('so the root follows from the main result', files['root.md'])
        digest = paper.render_digest(materials)
        for heading in ('## The main result of the paper, with its record in full\n\n### `Small.sq_step`',
                        '## The declaration that settles the root, with its record in full\n\n### `Small.root`'):
            self.assertIn(heading, digest)
        listed = files['elements.md'].splitlines()
        self.assertIn(' · the main result', next(line for line in listed if line.startswith('- `Small.sq_step`')))
        self.assertIn(' · settles the root', next(line for line in listed if line.startswith('- `Small.root`')))
        # The plan has the chosen theorem first in the first section, and the settling declaration as a numbered
        # statement, so that the root stands in the paper with its exact statement.
        check = lambda plan: ' '.join(paper.check_plan(materials, plan, KEYS))
        self.assertEqual(check(MAIN_PLAN), '')
        self.assertIn('the main result Small.sq_step is a theorem stated in the first section', check(PLAN))
        absorbed = {**MAIN_PLAN, 'statements': MAIN_PLAN['statements'][:2], 'others': [
            PLAN['others'][0], {**PLAN['others'][1], 'into': ['Small.oddSum_mono']}, *PLAN['others'][2:],
            {'element': 'Small.root', 'treatment': 'absorbed', 'into': ['proof'], 'reason': 'It is the last step.'}]}
        self.assertIn('the declaration that settles the root, Small.root, is a numbered statement', check(absorbed))
        # The brief of a section says which statement is the main theorem and which one states the root.
        brief = paper.render_brief(materials, MAIN_PLAN, MAIN_PLAN['sections'][2])
        self.assertIn('The main theorem of the paper is theorem `thm:square`, which states `Small.sq_step`.', brief)
        self.assertIn('`Small.root`, which the paper states as corollary `cor:sum`.', brief)
        # Without a chosen main result, and when the one named is the settling declaration, nothing is different:
        # the materials, the plan check, and every text made of them.
        self.assertEqual(paper.extract(self.instance, model, main='Small.root'), plain)
        self.assertEqual(paper.extract(self.instance, model, main=None), plain)
        self.assertNotIn('settles', plain)
        self.assertFalse(any('settles' in element for element in plain['elements']))
        self.assertEqual((paper.main_lines(plain), paper.main_note(plain), paper.chosen_said(plain)), ([], '', []))
        self.assertEqual(paper.check_plan(plain, PLAN, KEYS), [])
        self.assertIn('the main result Small.root is a theorem stated in the first section',
                      ' '.join(paper.check_plan(plain, MAIN_PLAN, KEYS)))
        self.assertNotIn('The main theorem of the paper is', paper.render_brief(plain, PLAN, PLAN['sections'][2]))
        self.assertNotIn('settles the root', paper.render_digest(plain).replace('that settles the root', ''))

    def test_a_main_result_that_is_no_settled_formal_theorem_is_refused_before_anything_is_written(self):
        model = replay(self.instance)
        self.assertEqual([paper.chosen_main(model, name) for name in (None, 'Small.root', 'Small.sq_step')],
                         [None, None, 'Small.sq_step'])
        informal = copy.deepcopy(model)
        informal['elements']['Small.sq_step']['formal'] = False
        for given, name, reason in ((model, 'Small.oddSum', 'it is a definition'),
                                    (model, 'Small.nothing', 'the instance has no declaration of that name'),
                                    (informal, 'Small.sq_step', 'its proof is not settled and formal')):
            with self.assertRaises(paper.Stop) as refused:
                paper.chosen_main(given, name)
            self.assertIn(reason, str(refused.exception))
        # The command refuses such a main result before it launches a session or writes a file.
        with self.assertRaisesRegex(paper.Stop, 'it is a definition'):
            self.run_paper(around_the_step(), main='Small.oddSum')
        code, said = self.said(['--main', 'Small.nothing', '--tex', *TEX])
        self.assertEqual(code, 1)
        self.assertIn('--main Small.nothing: the main result of the paper is a theorem of the instance', said)
        self.assertFalse(self.out.exists())
        self.assertFalse((self.scenario / 'calls.json').exists())
        # The option belongs to a run; typesetting later and a pass over open findings keep the main result they find.
        code, said = self.said(['--main', 'Small.sq_step', '--typeset-only'])
        self.assertEqual(code, 1)
        self.assertIn('they go with neither --typeset-only nor --open-findings', said)

    def test_a_paper_around_a_chosen_main_result_states_the_root_beside_it_and_keeps_the_choice_when_it_is_continued(self):
        script = around_the_step()
        script['plan'] = [{}]  # the planning session leaves nothing
        with self.assertRaises(paper.Stop):
            self.run_paper(script, main='Small.sq_step')
        launched = len(self.calls())
        materials = read_json(self.out / 'materials.json')
        self.assertEqual((materials['main'], materials['settles']), ('Small.sq_step', 'Small.root'))
        started = self.events('materials')[0]
        self.assertEqual((started['settled_by'], started['main']), ('Small.root', 'Small.sq_step'))
        # The planning session was told which theorem the paper is built around, and its digest has that record in full.
        planning = self.calls('plan')[0]
        self.assertTrue(paper.main_note(materials))
        self.assertIn(paper.main_note(materials), planning['prompt'])
        self.assertIn('## The main result of the paper, with its record in full',
                      (self.folder(planning) / 'materials-digest.md').read_text(encoding='utf-8'))
        # The run is not continued around another main result, and not around the settling declaration either.
        for other in ('Small.oddSum_mono', 'Small.root'):
            with self.assertRaisesRegex(paper.Stop, f'was made with the main result Small.sq_step, and this run was given --main {other}'):
                self.run_paper(around_the_step(), resume=True, main=other)
        self.assertEqual(len(self.calls()), launched)
        # Continued without the option, it takes the main result from its materials. The first plan it is given has
        # the root as the main theorem and is not accepted. The run ends with one finding open.
        again = around_the_step()
        again['plan'] = [{}, {}, {}, {'output/plan.json': json.dumps(PLAN), 'output/study.md': STUDY}, *again['plan']]
        again['cover:tools'] = [{'output/coverage.json': json.dumps([{
            'entry': 1, 'quote': 'The theorem is the expansion of a square', 'asserts': 'The theorem is a case of a known identity.',
            'nearest': 'Small.expand', 'difference': 'No element says that one is the other.'}])}]
        again['repair:narrow'] = [{'output/response.json': json.dumps(
            [{'finding': 1, 'action': 'kept', 'note': 'The sentence cites the identity and asserts nothing more.'}])}]
        self.assertEqual(self.run_paper(again, resume=True), 2)
        self.assertEqual(self.kinds(launched), [
            ('plan', None), ('plan', None), ('write', 'intro'), ('write', 'tools'), ('write', 'proof'), ('read', None),
            ('likeness', None), ('likeness', None), ('compare', 'intro'), ('compare', 'tools'), ('compare', 'proof'),
            ('cover', 'intro'), ('cover', 'tools'), ('repair', 'narrow-coverage-tools')])
        self.assertIn('the main result Small.sq_step is a theorem stated in the first section', self.calls('plan')[-1]['prompt'])
        self.assertEqual(read_json(self.out / 'plan.json'), MAIN_PLAN)
        # The writers have the head of the materials and a brief that say which statement is which.
        intro, _, proof = self.calls('write')
        self.assertIn('## The main result of the paper', (self.folder(intro) / 'root.md').read_text(encoding='utf-8'))
        brief = (self.folder(proof) / 'brief.md').read_text(encoding='utf-8')
        self.assertIn('`Small.root`, which the paper states as corollary `cor:sum`.', brief)
        self.assertEqual(brief, paper.render_brief(materials, MAIN_PLAN, MAIN_PLAN['sections'][2]))
        # The chosen theorem is Theorem 1.1, and the root stands in the paper as a numbered statement of its own. The
        # correspondence file names the main result and the declaration that settles the root.
        correspondence = read_json(self.out / 'correspondence.json')
        self.assertEqual((correspondence['root'], correspondence['main_result'], correspondence['settled_by']),
                         ('Small.root', 'Small.sq_step', 'Small.root'))
        self.assertEqual([(r['number'], r['label'], r['element'], r['comparison']['verdict']) for r in correspondence['statements']],
                         [('Theorem 1.1', 'thm:square', 'Small.sq_step', 'same'), ('Lemma 2.1', 'lem:increasing', 'Small.oddSum_mono', 'same'),
                          ('Corollary 3.1', 'cor:sum', 'Small.root', 'same')])
        self.assertEqual(correspondence['statements'][2]['paper_statement'], 'For every natural number $n$, we have $S_n = n^2$.')
        # A pass over the open findings and typesetting later read the materials around the same main result.
        launched = len(self.calls())
        code, said = self.said(['--open-findings', '--dry-run', '--tex', *TEX])
        self.assertEqual(code, 0)
        self.assertIn('came to its end (open_findings) with 1 findings left open', said)
        self.assertEqual(self.run_paper(around_the_step(), only=True), 2)
        self.assertEqual(read_json(self.out / 'correspondence.json')['main_result'], 'Small.sq_step')
        self.assertEqual(len(self.calls()), launched)

    def test_a_draft_records_its_main_result_and_the_paper_from_it_is_written_around_the_same_one(self):
        texts = {'thm:square': 'For every natural number $k$, we have $k^2 + (2k + 1) = (k + 1)^2$.',
                 'lem:increasing': 'For every natural number $n$, we have $S_n < S_{n+1}$.', 'cor:sum': MAIN_TEXT}
        script = {'plan': [{'output/plan.json': json.dumps({**MAIN_PLAN, 'citations': []}), 'output/study.md': STUDY}],
                  **{f'sketch:{sid}': [{'output/sketch.json': json.dumps(
                      {'statements': [{'label': label, 'text': texts[label], 'gap': None}], 'formulas': [], 'assertions': []})}]
                     for sid, label in MAIN_STATED.items()},
                  **{f'compare:{sid}': [{'output/comparison.json': json.dumps(
                      [{'label': label, 'verdict': 'same', 'difference': '', 'text': ''}])}] for sid, label in MAIN_STATED.items()}}
        self.assertEqual(self.run_paper(script, draft=True, main='Small.sq_step'), 0)
        draft = read_json(self.out / 'draft.json')
        self.assertEqual((draft['main'], [(s['label'], s['element']) for s in draft['statements']]),
                         ('Small.sq_step', [('thm:square', 'Small.sq_step'), ('lem:increasing', 'Small.oddSum_mono'),
                                            ('cor:sum', 'Small.root')]))
        launched = len(self.calls())
        folder, self.out = self.out, self.root / 'paper-from-draft'
        # A paper from this draft is not written around another main result, whether another theorem is named or
        # the settling declaration.
        for other in ('Small.oddSum_mono', 'Small.root'):
            with self.assertRaisesRegex(paper.Stop, f'was made with the main result Small.sq_step, and this run was given --main {other}'):
                self.run_paper(around_the_step(), from_draft=folder, main=other)
        self.assertFalse(self.out.exists())
        # Without the option, the run takes the main result from the draft, and the same one may be named again.
        for arguments in ([], ['--main', 'Small.sq_step']):
            code, said = self.said(['--from-draft', str(folder), '--dry-run', *arguments, '--tex', *TEX])
            self.assertEqual(code, 0)
            self.assertIn('The main result of the paper is Small.sq_step; the declaration that settles the root is Small.root.', said)
        # A draft that was made around the settling declaration is not turned into a paper around another theorem.
        plain = self.root / 'plain-draft'
        plain.mkdir()
        write_json(plain / 'plan.json', PLAN)
        write_json(plain / 'draft.json', {'statements': [], 'formulas': [], 'gaps': [], 'citations': []})
        (plain / 'study.md').write_text(STUDY, encoding='utf-8', newline='\n')
        with self.assertRaisesRegex(paper.Stop, 'was made with the declaration that settles the root as its main result'):
            self.run_paper(around_the_step(), from_draft=plain, main='Small.sq_step')
        code, said = self.said(['--from-draft', str(plain), '--dry-run', '--main', 'Small.root', '--tex', *TEX])
        self.assertEqual(code, 0)
        self.assertNotIn('The main result of the paper is', said)
        self.assertFalse(self.out.exists())
        self.assertEqual(len(self.calls()), launched)


# ----------------------------------------------------------------------------- what the readings leave open

# The manuscript as the resolving session leaves it: the first lemma has no number any more and is written into the
# proof of the main theorem, and the second lemma stands in the section that uses it, so the section `tools` is gone.
JOINED_PLAN = {
    **PLAN,
    'sections': [PLAN['sections'][0],
                 {'id': 'proof', 'title': 'Proof of the main theorem', 'content': 'The identity of the step, and the induction.',
                  'exemplars': ['epsilon', 'zeta']}],
    'statements': [PLAN['statements'][0],
                   {'element': 'Small.sq_step', 'kind': 'lemma', 'label': 'lem:square', 'section': 'proof'}],
    'others': [PLAN['others'][0],
               {'element': 'Small.oddSum_succ', 'treatment': 'absorbed', 'into': ['Small.root']},
               {'element': 'Small.oddSum_mono', 'treatment': 'absorbed', 'into': ['Small.root'],
                'reason': 'The induction uses it in one clause, and nothing else refers to it.'},
               PLAN['others'][2],
               {'element': 'Small.expand', 'treatment': 'cited', 'section': 'proof'}]}
JOINED_PROOF = r'''The induction rests on one identity, the expansion of a square \cite[Book II, Proposition 4]{euclid} for the pair $k$ and $1$.

\begin{lemma}\label{lem:square}
For every natural number $k$, $k^2 + (2k + 1) = (k + 1)^2$.
\end{lemma}
\begin{proof}
We have $(k + 1)^2 = k^2 + 2k + 1$.
\end{proof}

\begin{proof}[Proof of Theorem~\ref{thm:main}]
By induction on $n$. The sum $S_{n+1}$ exceeds $S_n$ by $2n + 1$, and the step is Lemma~\ref{lem:square}.
\end{proof}
'''
EXPECTED = 'The reader is expected to expand a square.'


def restructuring():
    """A scenario in which the one reading leaves a finding, and the resolving session answers it by another structure.

    The narrow repair after each reading keeps the text. The first resolving session returns a plan that says
    nothing of the lemma that lost its number; the second returns the plan of the manuscript it leaves. The
    reading after it finds something in the section that was rewritten."""
    script = good()
    script['read'] = [{'output/reading.json': json.dumps({**CLEAN, 'findings': [EXPANSION]})},
                      {'output/reading.json': json.dumps({**CLEAN, 'findings': [BASE]})}]
    script['repair:narrow'] = [{'output/response.json': json.dumps([{'finding': 1, 'action': 'kept', 'note': EXPECTED}])}]
    moved = {'output/proof.tex': JOINED_PROOF,
             'output/response.json': answered('The lemma stands where it is used, with its expansion written out.')}
    script['resolve'] = [{**moved, 'output/plan.json': json.dumps({**JOINED_PLAN, 'others': JOINED_PLAN['others'][:2]
                                                                    + JOINED_PLAN['others'][3:]})},
                         {**moved, 'output/plan.json': json.dumps(JOINED_PLAN)}]
    # The lemma was reworded, so its present text has no verdict; it is compared before the running text is.
    script['compare:proof'] = [{'output/comparison.json': json.dumps([SAME[2]])}]
    return script


class ResolveTests(PaperCase):
    """The session that closes what the readings left open, and may change the structure of the paper for it."""

    def kinds(self, since=0):
        return [(c['kind'], c['section']) for c in self.calls()][since:]

    def test_the_resolving_session_may_change_the_structure_and_the_run_follows_the_plan_it_returns(self):
        with patch('paper.READING_ROUNDS', 1):
            self.assertEqual(self.run_paper(restructuring()), 0)
        self.assertEqual(self.kinds(4), [
            ('read', None), ('repair', 'narrow-reading-tools'), ('likeness', None), ('likeness', None), *COMPARED,
            ('resolve', None), ('resolve', None), ('read', None), ('repair', 'narrow-reading-proof'),
            ('compare', 'proof'), ('cover', 'intro'), ('cover', 'proof')])
        # The resolving session has what a repair of the whole manuscript has, and every open finding of the readings
        # with the reason it was left open. It is a session of the model that writes.
        first, second = self.calls('resolve')
        left = {**EXPANSION, 'open_because': paper.KEPT + EXPECTED}
        self.assertEqual(read_json(self.folder(first) / 'findings.json'),
                         {'understanding': CLEAN['understanding'], 'findings': [{'finding': 1, 'check': paper.READING, 'reported': left}]})
        self.assertTrue({'paper-method.md', 'plan.json', 'paper.tex', 'study.md', 'parts/abstract.tex', 'parts/intro.tex',
                         'parts/tools.tex', 'parts/proof.tex', *RECORD_FILES} <= set(first['given']))
        self.assertEqual(self.given(first), sorted(CHOSEN))
        self.assertEqual(read_json(self.folder(first) / 'session.json')['model'],
                         read_json(self.folder(self.calls('write')[0]) / 'session.json')['model'])
        # A plan that does not pass the check of the plan goes back with the reasons, as the first plan does.
        self.assertIn('output/plan.json: the plan says nothing about these elements of the materials: Small.oddSum_mono',
                      second['prompt'])
        # The parts on disk, the plan and the correspondence follow the plan that was returned.
        self.assertEqual(read_json(self.out / 'plan.json'), JOINED_PLAN)
        self.assertEqual(sorted(path.name for path in (self.out / 'parts').iterdir()), ['abstract.tex', 'intro.tex', 'proof.tex'])
        self.assertEqual(self.part('proof'), JOINED_PROOF)
        tex = (self.out / 'paper.tex').read_text(encoding='utf-8')
        self.assertNotIn('\\section{Preliminaries}', tex)
        self.assertNotIn('lem:increasing', tex)
        resolved = self.events('resolve')[0]
        self.assertEqual((resolved['changed'], resolved['removed'], resolved['plan'], resolved['response'][0]['action']),
                         (['proof'], ['tools'], True, 'revised'))
        correspondence = read_json(self.out / 'correspondence.json')
        self.assertEqual([(r['number'], r['label'], r['comparison']['verdict']) for r in correspondence['statements']],
                         [('Theorem 1.1', 'thm:main', 'same'), ('Lemma 2.1', 'lem:square', 'same')])
        self.assertEqual({o['element']: o['treatment'] for o in correspondence['others']}['Small.oddSum_mono'], 'absorbed')
        # The verdict of the statement that stands as it was compared is kept. The lemma that was reworded is compared
        # before the running text, alone; the lemma that lost its number has no verdict any more.
        compared = self.calls('compare')[-1]
        self.assertEqual([s['label'] for s in read_json(self.folder(compared) / 'statements.json')], ['lem:square'])
        self.assertEqual(sorted(read_json(self.out / 'state.json')['compared']), ['lem:square', 'thm:main'])
        # The manuscript was read by itself after the session that may rewrite, and the repair of what that reader
        # found worked from the brief of the new plan.
        reread = self.calls('read')[-1]
        self.assertIn('We have $(k + 1)^2 = k^2 + 2k + 1$.', (self.folder(reread) / 'paper.tex').read_text(encoding='utf-8'))
        repair = self.calls('repair')[-1]
        self.assertEqual((self.folder(repair) / 'brief.md').read_text(encoding='utf-8'),
                         paper.render_brief(self.materials(), JOINED_PLAN, JOINED_PLAN['sections'][1]))
        # The findings of the readings are closed. The one that the resolving session answered by a change is gone;
        # the one that the last narrow repair answered with a reason is listed with that reason, and nothing is open.
        end = self.events('end')[-1]
        self.assertEqual((end['status'], end['open'], end['kept']),
                         ('complete', [], [{'check': paper.READING, 'finding': BASE, 'reason': paper.KEPT + EXPECTED}]))
        state = read_json(self.out / 'state.json')
        self.assertEqual((state['done'], state['resolve'], state['kept']),
                         ({'reading': True, 'likeness': True, 'rereading': True, 'comparison': True, 'resolve': True,
                           'coverage': True}, None, end['kept']))
        self.assertFalse((self.out / 'resolve').exists())
        self.assertTrue((self.out / 'paper.pdf').is_file())

    def test_a_run_stopped_after_the_resolving_session_is_continued_with_the_plan_and_the_parts_it_returned(self):
        script = restructuring()
        script['read'][1] = {}  # the reading after the resolving session leaves nothing
        with patch('paper.READING_ROUNDS', 1):
            with self.assertRaises(paper.Stop):
                self.run_paper(script)
            launched = len(self.calls())
            state = read_json(self.out / 'state.json')
            self.assertEqual((state['resolve']['step'], state['rewritten'], 'resolve' in state['done'], state['open'], state['kept']),
                             ('read', True, False, [], []))
            self.assertEqual(read_json(self.out / 'plan.json'), JOINED_PLAN)
            # As a run would be that was stopped while it put the parts and the plan in place: the state says that
            # this is to be done, and the folder still has the section that is gone and the plan before.
            write_json(self.out / 'state.json', {**state, 'resolve': {**state['resolve'], 'step': 'place'}})
            write_json(self.out / 'plan.json', PLAN)
            (self.out / 'parts' / 'tools.tex').write_text(TOOLS, encoding='utf-8', newline='\n')
            (self.out / 'parts' / 'proof.tex').write_text(PROOF, encoding='utf-8', newline='\n')
            again = restructuring()
            again['read'] = [{'output/reading.json': json.dumps(CLEAN)}]
            self.assertEqual(self.run_paper(again, resume=True), 0)
        # The resolving session is not launched again: what it returned is put in place, and the run goes on with
        # the reading, the comparison of the reworded lemma and the comparison of the running text.
        self.assertEqual(self.kinds(launched), [('read', None), ('compare', 'proof'), ('cover', 'intro'), ('cover', 'proof')])
        self.assertEqual(read_json(self.out / 'plan.json'), JOINED_PLAN)
        self.assertEqual(sorted(path.name for path in (self.out / 'parts').iterdir()), ['abstract.tex', 'intro.tex', 'proof.tex'])
        self.assertEqual(self.part('proof'), JOINED_PROOF)
        end = self.events('end')[-1]
        self.assertEqual((end['status'], end['open'], end['kept']), ('complete', [], []))
        self.assertFalse((self.out / 'resolve').exists())


# ----------------------------------------------------------------------------- the running text

SHARP = 'In particular $S_n \\ge n$ for every $n$, and this bound is sharp.'
TOOLS_SHARP = TOOLS + '\n' + SHARP + '\n'
UNCOVERED = {'entry': 2, 'quote': SHARP, 'asserts': 'The sums are at least $n$, with equality somewhere.',
             'nearest': 'Small.oddSum_mono', 'difference': 'No element bounds $S_n$ from below by $n$ or says where equality holds.'}
REPORTED = {'where': 'the running text of the section "Preliminaries"', 'section': 'sec:tools',
            **{key: UNCOVERED[key] for key in ('quote', 'asserts', 'nearest', 'difference')}}


def asserting(kept=None):
    """A scenario in which the section `tools` ends with a sentence that no element covers.

    The repair cuts the sentence, or with `kept` keeps it and gives that as its reason."""
    script = good()
    script['write:tools'] = [{'output/tools.tex': TOOLS_SHARP}]
    script['cover:tools'] = [{'output/coverage.json': json.dumps([UNCOVERED])}, {'output/coverage.json': '[]'}]
    script['repair:narrow'] = [{'output/response.json': json.dumps([{'finding': 1, 'action': 'kept', 'note': kept}])}] if kept \
        else [{'output/tools.tex': TOOLS, 'output/response.json': answered('The sentence is cut.')}]
    script['changes'] = [{'output/verdicts.json': verdicts([(True, [1], 'Nothing after it rests on the sentence.')], [(1, True, '')])}]
    return script


class CoverageTests(PaperCase):
    """The running text of the manuscript compared with the elements, after everything else."""

    def kinds(self, since=0):
        return [(c['kind'], c['section']) for c in self.calls()][since:]

    def test_the_running_text_is_what_stands_outside_the_statements_and_the_proofs(self):
        tools = TOOLS.replace('The sum $S_{n+1}$ exceeds $S_n$ by $2n + 1$.', '\n'.join([
            'We have', '\\begin{equation}\\label{eq:tools-gain}', 'S_{n+1} - S_n = 2n + 1.', '\\end{equation}',
            'A second display is used here alone:', '\\begin{equation}\\label{eq:tools-local}', '2n + 1 > 0.', '\\end{equation}',
            'By \\eqref{eq:tools-local} the claim follows.'])) + '\n% A comment alone asserts nothing.\n'
        proof = PROOF.replace('The sums increase by', 'The sums increase by \\eqref{eq:tools-gain} and')
        parts = {**PARTS, 'tools': tools, 'proof': proof}
        tex, spans = paper.assemble(PLAN, parts)
        found = paper.running_text(PLAN, parts, spans)
        # The abstract goes with the first section. A numbered statement and a proof are left out, and what stands
        # before and after them is given paragraph by paragraph.
        self.assertEqual([(e['entry'], e['kind'], e['part'], e['text']) for e in found['intro']], [
            (1, 'running text', 'abstract', ABSTRACT.strip()),
            (2, 'running text', 'intro', INTRO.split('\n')[0]),
            (3, 'running text', 'intro', 'The proof, in Section~\\ref{sec:proof}, is an induction whose step is Lemma~\\ref{lem:square}.')])
        # Of a proof, a displayed formula is given when text outside that proof refers to it, and no other.
        self.assertEqual([(e['entry'], e['kind'], e.get('labels')) for e in found['tools']],
                         [(1, 'formula of a proof, referred to from outside that proof', ['eq:tools-gain']),
                          (2, 'running text', None)])
        self.assertIn('S_{n+1} - S_n = 2n + 1.', found['tools'][0]['text'])
        self.assertTrue(found['tools'][1]['text'].startswith('The next lemma is the expansion of a square'))
        # A section that consists of a proof has no running text.
        self.assertEqual(found['proof'], [])
        # Each entry names the lines of the manuscript at which it stands.
        lines = tex.split('\n')
        for entry in found['intro'] + found['tools'][1:]:
            self.assertEqual(lines[int(entry['lines']) - 1], entry['text'])
        first, last = map(int, found['tools'][0]['lines'].split(' to '))
        self.assertEqual((lines[first - 1], lines[last - 1]), ('\\begin{equation}\\label{eq:tools-gain}', '\\end{equation}'))

    def test_a_sentence_that_no_element_covers_is_cut_and_the_section_is_compared_once_more(self):
        script = asserting()
        # The first session for the introduction names an entry and an element that do not exist.
        script['cover:intro'] = [{'output/coverage.json': json.dumps([{**UNCOVERED, 'entry': 9, 'nearest': 'Small.nothing'}])},
                                 {'output/coverage.json': '[]'}]
        self.assertEqual(self.run_paper(script), 0)
        self.assertEqual(self.kinds(7), [*COMPARED, ('cover', 'intro'), ('cover', 'intro'), ('cover', 'tools'),
                                         ('repair', 'narrow-coverage-tools'), ('changes', None), ('cover', 'tools')])
        # The session of a section has the running text of the section as a list, the records in full of the
        # section's elements and every other element by what it says, and the manuscript.
        again, covering = self.calls('cover')[1:3]
        self.assertIn('"nearest", the name of an element as elements.md gives it', again['prompt'])
        self.assertEqual(covering['given'], sorted(['paper-method.md', 'paper.tex', 'prompt.txt', 'records.md', 'session.json',
                                                    'text.json', 'elements.md'] + RECORD_FILES[3:]))
        entries = read_json(self.folder(covering) / 'text.json')
        self.assertEqual([(e['entry'], e['kind'], e['part']) for e in entries],
                         [(1, 'running text', 'tools'), (2, 'running text', 'tools')])
        self.assertEqual(entries[1]['text'], SHARP)
        self.assertEqual([e['part'] for e in read_json(self.folder(again) / 'text.json')], ['abstract', 'intro', 'intro'])
        full, rest = (self.folder(covering) / 'records.md').read_text(encoding='utf-8').split(
            '\n## Every other element that the proof of the root rests on, by what it says\n')
        self.assertEqual([line for line in full.splitlines() if line.startswith('### ')],
                         ['### `Small.oddSum_succ`', '### `Small.oddSum_mono`', '### `Small.expand`', '### `Small.sq_step`'])
        self.assertIn('**Proof.**\n\nExpand $(k + 1)^2$ by `Small.expand`.', full)
        self.assertEqual([line for line in rest.splitlines() if line.startswith('### ')],
                         ['### `Small.oddSum`', '### `Small.oddSum_mono_weak`', '### `Small.root`'])
        self.assertNotIn('**Proof.**', rest)
        self.assertEqual(read_json(self.folder(covering) / 'session.json')['model'],
                         read_json(self.folder(self.calls('compare')[0]) / 'session.json')['model'])
        # What was reported goes to the narrow repair of its section, as a finding of its own kind.
        repair = self.calls('repair')[0]
        self.assertEqual(read_json(self.folder(repair) / 'findings.json'), [REPORTED])
        self.assertIn('So this repair is narrow.', repair['prompt'])
        self.assertTrue({'brief.md', 'parts/tools.tex'} <= set(repair['given']))
        # The change is read as after every narrow repair, by a session that is told what kind of finding it answers.
        given = read_json(self.folder(self.calls('changes')[0]) / 'changes.json')
        self.assertEqual([(f['finding'], f['check'], f['reported']) for f in given['findings']], [(1, paper.COVERAGE, REPORTED)])
        self.assertEqual([(c['part'], c['before'], c['after']) for c in given['changes']], [('tools', '\n' + SHARP, '')])
        # The section that changed is compared once more, alone, on the text as it stands; nothing is open.
        last = self.calls('cover')[-1]
        self.assertEqual([e['text'] for e in read_json(self.folder(last) / 'text.json')], [entries[0]['text']])
        self.assertEqual([(e['round'], e['sections'], len(e['uncovered'])) for e in self.events('coverage')],
                         [(1, ['intro', 'tools'], 1), (2, ['tools'], 0)])
        self.assertEqual(self.part('tools'), TOOLS)
        end = self.events('end')[-1]
        self.assertEqual((end['status'], end['open'], end['kept']), ('complete', [], []))
        state = read_json(self.out / 'state.json')
        self.assertEqual((state['narrow'], state['done']['coverage']), (None, True))
        self.assertFalse((self.out / 'narrow').exists())

    def test_what_stays_uncovered_is_open_and_is_acted_on_as_an_open_finding(self):
        reason = 'The bound is the content of Lemma 2.1.'
        self.assertEqual(self.run_paper(asserting(kept=reason)), 2)
        # The repair kept the sentence, so nothing changed: no session reads changes, and no section is compared again.
        self.assertEqual(self.kinds(7), [*COMPARED, *COVERED, ('repair', 'narrow-coverage-tools')])
        left = [{'check': paper.COVERAGE, 'after_repairs': 1, 'problems': [{**REPORTED, 'open_because': paper.KEPT + reason}]}]
        end = self.events('end')[-1]
        self.assertEqual((end['status'], end['open'], end['kept']), ('open_findings', left, []))
        self.assertEqual(self.part('tools'), TOOLS_SHARP)
        launched = len(self.calls())
        code, said = self.said(['--open-findings', '--dry-run', '--tex', *TEX])
        self.assertEqual(code, 0)
        for words in (f'{paper.COVERAGE}: 1 open after 1 repairs.', '    1. the running text of the section "Preliminaries" [part tools]',
                      '       open because: ' + paper.KEPT + reason):
            self.assertIn(words, said)
        # Acting on it: the sentence is reworded and still says more than an element states, which the comparison
        # of the section that follows the repair reports. It is open with that, and is not repaired in the same pass.
        weaker = 'In particular $S_n \\ge n$ for every $n$.'
        still = {**UNCOVERED, 'quote': weaker, 'asserts': 'The sums are at least $n$.'}
        script = good()
        script['repair:narrow-coverage-tools'] = [{'output/tools.tex': TOOLS + '\n' + weaker + '\n',
                                                   'output/response.json': answered('The remark on sharpness is cut.')}]
        script['changes'] = [{'output/verdicts.json': verdicts([(True, [1], 'Read with the lemma before it.')], [(1, True, '')])}]
        script['cover:tools'] = [{}, {'output/coverage.json': json.dumps([still])}]
        self.assertEqual(self.run_paper(script, open_findings='all'), 2)
        self.assertEqual(self.kinds(launched), [('repair', 'narrow-coverage-tools'), ('changes', None), ('cover', 'tools')])
        repair = self.calls()[launched]
        self.assertEqual(read_json(self.folder(repair) / 'findings.json'), left[0]['problems'])
        self.assertIn('A finding that carries "open_because" was taken up before and left open', repair['prompt'])
        end = self.events('end')[-1]
        self.assertEqual(end['open'], [{'check': paper.COVERAGE, 'after_repairs': 2, 'problems': [
            {**REPORTED, 'quote': weaker, 'asserts': 'The sums are at least $n$.', 'open_because': paper.COVERED_AGAIN}]}])
        self.assertIn(weaker, self.part('tools'))

    def test_a_run_stopped_in_the_repair_of_the_running_text_or_after_it_is_continued_there(self):
        script = asserting()
        script['changes'] = [{}]  # the session that reads the change leaves nothing
        with self.assertRaises(paper.Stop):
            self.run_paper(script)
        launched = len(self.calls())
        state = read_json(self.out / 'state.json')
        self.assertEqual((state['narrow']['step'], [f['check'] for f in state['narrow']['findings']], 'coverage' in state['done'],
                          state['done']['resolve']), ('read', [paper.COVERAGE], False, True))
        # The continuation reads the change; the session that then compares the section again leaves nothing.
        again = asserting()
        again['cover:tools'] = [{}, {}, {}, {'output/coverage.json': '[]'}]
        with self.assertRaises(paper.Stop):
            self.run_paper(again, resume=True)
        self.assertEqual(self.kinds(launched), [('changes', None), ('cover', 'tools'), ('cover', 'tools')])
        launched = len(self.calls())
        state = read_json(self.out / 'state.json')
        self.assertEqual((state['narrow']['step'], self.part('tools')), ('done', TOOLS))
        # The repair and the reading of its change are not made again: the section is compared, and the run ends.
        self.assertEqual(self.run_paper(again, resume=True), 0)
        self.assertEqual(self.kinds(launched), [('cover', 'tools')])
        end = self.events('end')[-1]
        self.assertEqual((end['status'], end['open']), ('complete', []))
        self.assertEqual(read_json(self.out / 'state.json')['narrow'], None)


if __name__ == '__main__':
    unittest.main()
